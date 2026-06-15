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


_REF = None         # full (init+play) reachable-instruction reference
_PLAY_REF = None    # play-ONLY reachable reference (init excluded)


def _build_ref(init_pc):
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
    _c, starts, _l, _j = trace(bytes(mem), 0, init_pc, 0x10A1, ())
    ref = []
    for pc in sorted(p for p in starts if 0x1000 <= p < 0x1A00):
        L = _INST_LEN[mem[pc]]
        if pc + L > 0x1A00:
            continue
        cls = (_opclass(mem[pc + 1] | (mem[pc + 2] << 8)) if L == 3 else None)
        ref.append((pc, L, bytes(mem[pc:pc + L]), cls))
    return ref


def _v5_ref():
    """Full reachable-instruction reference (init+play). Cached."""
    global _REF
    if _REF is None:
        _REF = _build_ref(0x1040)
    return _REF


def _v5_play_ref():
    """PLAY-only reachable reference ($10A1..$170E) — excludes init, so it
    validates members whose init is relocated/wrapped (the player body is
    still the family-3/5 player at base+$A1 even when the init moved). Cached."""
    global _PLAY_REF
    if _PLAY_REF is None:
        _PLAY_REF = _build_ref(0x10A1)
    return _PLAY_REF


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


def _detect_v5(mem, s):
    """Locate the V5 player from its 2-entry jump table. entry0 = init
    target, entry1 = play target. The PLAY routine is the reliable anchor:
    base = play_target - $A1 (Katusha play is at base+$A1). The INIT target
    is read separately and may be RELOCATED/WRAPPED away from base+$40 (a
    re-linked build moves the init elsewhere; the play body stays at
    base+$A1) — so base is derived from play, not init. Returns
    (base, init_target, jt_addr, layout) with layout in {'v5','family4'},
    or (None, None, None, None)."""
    def jt_at(b):
        if not (s['load'] <= b and b + 5 < 0x10000
                and mem[b] == 0x4C and mem[b + 3] == 0x4C):
            return None
        return (mem[b + 1] | (mem[b + 2] << 8),
                mem[b + 4] | (mem[b + 5] << 8))
    cands = []
    for b in (s['load'], s['play'] - 3):
        r = jt_at(b)
        if r:
            cands.append((b, r[0], r[1]))
    if not cands:
        lo, hi = s['load'], min(0x10000, s['load'] + len(s['payload']))
        for b in range(lo, hi - 6):
            if mem[b] == 0x4C and mem[b + 3] == 0x4C:
                r = jt_at(b)
                if r:
                    cands.append((b, r[0], r[1]))
                    break
    for jt_addr, it, pt in cands:
        # family-4 (Jupiter41) = standard jump table at load with play+$95
        if jt_addr == s['load'] and it == jt_addr + 0x40 and pt == jt_addr + 0x95:
            return None, None, jt_addr, 'family4'
        base = (pt - 0xA1) & 0xFFFF
        if base >= s['load'] and base + 0x1900 <= 0x10000:
            return base, it, jt_addr, 'v5'
    return None, None, None, None


def dmc_v5_config(sid_path: str, hvsc_root: str = 'hvsc84') -> DMCV5Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path))
    base, init_target, jt_addr, layout = _detect_v5(mem, s)
    if base is None and layout != 'family4':
        raise DMCV5Unsupported(
            'no_jumptable',
            f"load=${s['load']:04X} init=${s['init']:04X} play=${s['play']:04X}")
    if layout == 'family4':
        raise DMCV5Unsupported('family4_branch', f'jt=${jt_addr:04X}')
    delta = base - 0x1000

    # ---- masked identity compare of the PLAY-reachable body vs the
    #      relocated Katusha reference. The init is validated separately
    #      (it may be relocated/wrapped) so we don't compare it here. ----
    for pc, L, rbytes, cls in _v5_play_ref():
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

    # ---- init skeleton: the V5 init copies the orderlist record into the
    #      track pointers — `<4-byte A-prefix> A2 00 B9 lo hi 9D <17CF+delta>`.
    #      Validate that shape at init_target (wherever the init lives) and
    #      read the orderlist-record operand site from it (init_target+7).
    #      The 4-byte prefix varies (LDA #0 single-subtune vs ASL*3 song-
    #      indexed multi-subtune) so only the copy skeleton is checked. ----
    it = init_target
    tcf = (0x17CF + delta) & 0xFFFF
    if not (it + 12 < 0x10000 and mem[it + 3] == 0xA8 and mem[it + 4] == 0xA2
            and mem[it + 6] == 0xB9 and mem[it + 9] == 0x9D
            and (mem[it + 10] | (mem[it + 11] << 8)) == tcf):
        raise DMCV5Unsupported('player_code_mismatch',
                               f'init skeleton at ${it:04X}')

    # ---- multi-subtune (song-indexed orderlist record) needs a multi-song
    #      build the V5 composer doesn't emit yet (single-song PSID); flag. ----
    if s.get('songs', 1) > 1:
        raise DMCV5Unsupported('multi_subtune', f"songs={s['songs']}")

    # ---- CIA multispeed: a wrapper member (play vector not the jump table)
    #      whose PSID speed bit is set runs from a CIA-timer dispatcher; the
    #      V5 verify is VBI-only, so flag it. ----
    if s['play'] != jt_addr + 3 and (s.get('speed', 0) & 1):
        raise DMCV5Unsupported('cia_multispeed', f"play=${s['play']:04X}")

    d = DMCV5Config(sid_path=sid_path,
                    name=os.path.splitext(os.path.basename(sid_path))[0],
                    base=base)
    # play-body operand sites relocate with the base; the orderlist site is
    # read from the (possibly relocated/wrapped) init's actual load operand.
    for f in ('op_secp_lo', 'op_secp_hi', 'op_instr', 'op_freq_lo',
              'op_freq_hi', 'op_wave_ctrl', 'op_wave_freq', 'op_pulse_lo',
              'op_pulse_hi', 'op_filter_lo', 'op_filter_hi'):
        setattr(d, f, getattr(d, f) + delta)
    d.op_orderlist = it + 7
    return d
