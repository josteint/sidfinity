"""DMC V5 config factory — `dmc_v5_config(sid_path)`.

Validates that a SID carries the dominant family-3/5 V5 player and
derives its DMCV5Config (relocation-aware). Raises `DMCV5Unsupported`
with a typed reason otherwise (FC/V4 factory-hygiene lesson: typed
flags, never silent misbuilds).

Identity probe = masked byte-compare of the reachable player code
against the representative carved from Katusha (the family-3 rep). The
code region ($1040-$170E) is byte-identical across the family except:
  - PATCHED per-song data-table operands (freq / orderlist / sector ptr /
    instrument / wave / pulse / filter) — the editor's packer rewrites
    these per song; the extract reads them by dataflow, so they are
    masked here.
  - SELF-REF operands (code + work-RAM/state addresses) — relocate with
    the player base.
  - ABSOLUTE operands (SID $D4xx, CIA $DCxx) — base-invariant, compared
    as-is.

Base detection = the 2-entry jump table `JMP base+$40 (init) /
JMP base+$A1 (play)`. Family-4 (Jupiter41, play +$95) is a DISTINCT
branch and is rejected with `family4_branch`.
"""
from __future__ import annotations

import os
import struct

from pipelines.dmc.v5.config import DMCV5Config

# operand value ranges (Katusha layout) for the per-instruction operand
# classification (validated against the traced player — see RE_NOTES /
# the factory build session): everything is either code+state (relocates),
# a patched data-table read (masked), or absolute hardware (compared raw).
_FREQ = (0x170F, 0x17CF)          # freq lo+hi tables (patched per tune)
_DATA = (0x1878, 0x19D0)          # orderlist rec + sector/instr/wave/pulse/filter
_CODE_STATE = ((0x1006, 0x170F), (0x17CF, 0x1878))  # code + work RAM/state


def _opclass(v: int) -> str:
    if _FREQ[0] <= v < _FREQ[1] or _DATA[0] <= v < _DATA[1]:
        return 'patched'
    for lo, hi in _CODE_STATE:
        if lo <= v < hi:
            return 'reloc'
    return 'abs'


class DMCV5Unsupported(Exception):
    def __init__(self, reason: str, detail: str = ''):
        self.reason = reason
        self.detail = detail
        super().__init__(f'{reason}: {detail}' if detail else reason)


_REF = None      # list[(pc, len, ref_bytes, operand_class)]


def _v5_ref():
    """Trace the Katusha player once; return the reachable-instruction
    reference (pc, length, bytes, operand class). Cached."""
    global _REF
    if _REF is not None:
        return _REF
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from seed_disassembly import parse_psid, trace, _INST_LEN
    rep = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                       'hvsc84', 'DEMOS', 'G-L', 'Katusha.sid')
    s = parse_psid(rep)
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        mem[s['load'] + i] = b
    _c, starts, _l, _j = trace(bytes(mem), 0, 0x1040, 0x10A1, ())
    ref = []
    for pc in sorted(p for p in starts if 0x1000 <= p < 0x1A00):
        L = _INST_LEN[mem[pc]]
        if pc + L > 0x1A00:
            continue
        cls = (_opclass(mem[pc + 1] | (mem[pc + 2] << 8)) if L == 3 else None)
        ref.append((pc, L, bytes(mem[pc:pc + L]), cls))
    _REF = ref
    return ref


def _load(sid_path: str):
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    raw = open(sid_path, 'rb').read()
    s['speed'] = struct.unpack('>I', raw[18:22])[0]
    mem = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    return mem, s


def _detect_base(mem, s):
    """Find the V5 player base via the 2-entry jump table. Returns
    (base, layout) where layout in {'v5','family4'}, or (None, reason)."""
    def jt(b):
        if not (0 < b and s['load'] <= b and b + 0xA1 < 0x10000
                and mem[b] == 0x4C and mem[b + 3] == 0x4C):
            return None
        e0 = mem[b + 1] | (mem[b + 2] << 8)
        e1 = mem[b + 4] | (mem[b + 5] << 8)
        if e0 == b + 0x40 and e1 == b + 0xA1:
            return 'v5'
        if e0 == b + 0x40 and e1 == b + 0x95:
            return 'family4'           # Jupiter41 branch — distinct engine
        return None
    for b in (s['play'] - 3, s['load']):
        lay = jt(b)
        if lay:
            return b, lay
    # relocated-within-file (CIA/multispeed wrapper, player elsewhere):
    # scan for the first valid jump-table signature; the masked compare
    # then validates it.
    lo, hi = s['load'], min(0x10000, s['load'] + len(s['payload']))
    for b in range(lo, hi - 0xA2):
        if mem[b] == 0x4C and mem[b + 3] == 0x4C:
            lay = jt(b)
            if lay:
                return b, lay
    return None, None


def dmc_v5_config(sid_path: str, hvsc_root: str = 'hvsc84') -> DMCV5Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path))
    base, layout = _detect_base(mem, s)
    if base is None:
        raise DMCV5Unsupported(
            'no_jumptable',
            f"load=${s['load']:04X} init=${s['init']:04X} play=${s['play']:04X}")
    if layout == 'family4':
        raise DMCV5Unsupported('family4_branch', f'base=${base:04X}')
    delta = base - 0x1000

    # ---- masked identity compare vs the relocated Katusha reference ----
    ref = _v5_ref()
    for pc, L, rbytes, cls in ref:
        a = pc + delta
        if a + L > 0x10000:
            raise DMCV5Unsupported('oob', f'${pc:04X}')
        if mem[a] != rbytes[0]:
            raise DMCV5Unsupported('player_code_mismatch',
                                   f'opcode at ${pc:04X}')
        if L == 3:
            mv = mem[a + 1] | (mem[a + 2] << 8)
            rv = rbytes[1] | (rbytes[2] << 8)
            if cls == 'patched':
                continue
            if cls == 'reloc':
                if mv != (rv + delta) & 0xFFFF:
                    raise DMCV5Unsupported('player_code_mismatch',
                                           f'reloc operand at ${pc:04X}')
            elif mv != rv:
                raise DMCV5Unsupported('player_code_mismatch',
                                       f'abs operand at ${pc:04X}')
        elif mem[a + 1:a + L] != rbytes[1:]:
            raise DMCV5Unsupported('player_code_mismatch',
                                   f'immediate at ${pc:04X}')

    # ---- CIA multispeed: a wrapper member (play != base+3) whose PSID
    #      speed bit is set runs the player from a CIA-timer dispatcher.
    #      Not yet supported by the V5 verify (VBI-only); flag it. ----
    if s['play'] != base + 3 and (s.get('speed', 0) & 1):
        raise DMCV5Unsupported('cia_multispeed', f"play=${s['play']:04X}")

    def at(off):
        return off + delta

    d = DMCV5Config(sid_path=sid_path,
                    name=os.path.splitext(os.path.basename(sid_path))[0],
                    base=base)
    # relocate every operand site to the member's base
    for f in ('op_orderlist', 'op_secp_lo', 'op_secp_hi', 'op_instr',
              'op_freq_lo', 'op_freq_hi', 'op_wave_ctrl', 'op_wave_freq',
              'op_pulse_lo', 'op_pulse_hi', 'op_filter_lo', 'op_filter_hi'):
        setattr(d, f, at(getattr(d, f)))
    return d
