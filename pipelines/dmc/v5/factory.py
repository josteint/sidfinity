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
# Work-RAM scratch gap ($1006-$103F, 58 bytes: voice-active flags + scratch).
# Some relink variants move this block independently of the code (e.g. up near
# a wrapper), so a `LDA $1006,x` read points elsewhere though the player is
# otherwise byte-identical. It's RUNTIME STATE, not musical content, and the
# composer rebuilds its own engine — so its address is a don't-care for both
# detection and extraction. Classed 'state' (operand not compared), distinct
# from CODE operands in the same `_CODE_STATE` span which must still relocate
# by delta exactly.
_STATE = ((0x1006, 0x1040),)


def _opclass(v: int) -> str:
    if _FREQ[0] <= v < _FREQ[1] or _DATA[0] <= v < _DATA[1]:
        return 'patched'
    for lo, hi in _STATE:
        if lo <= v < hi:
            return 'state'
    for lo, hi in _CODE_STATE:
        if lo <= v < hi:
            return 'reloc'
    return 'abs'


class DMCV5Unsupported(Exception):
    def __init__(self, reason: str, detail: str = ''):
        self.reason = reason
        self.detail = detail
        super().__init__(f'{reason}: {detail}' if detail else reason)


def _cia_period_from_writelog(sid_path: str, subtune: int,
                              dur: float = 3.0) -> int:
    """Measure the multispeed CIA period from the GROUND-TRUTH writelog
    (libsidplayfp) — V5's CIA wrapper members can't be run by py65. Same
    method as the v4 factory (ledger C9): the player's IRQ fires every L+1
    cycles, running N = 19656/(L+1) play()s per PAL frame; count play()s /
    PAL-frames from `--writelog-per-irq --per-irq-debug`, round N to the
    integer multispeed factor, return latch 19656/N - 1 (N=2 -> $2663,
    N=4 -> $1331). Returns 0 if not measurable / single-speed."""
    import subprocess
    import re
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                      'tools', 'siddump')
    try:
        out = subprocess.run(
            [sd, sid_path, '--writelog-per-irq', '--per-irq-debug',
             '--duration', str(dur), '--subtune', str(subtune)],
            capture_output=True, text=True, timeout=90).stderr
    except Exception:
        return 0
    frames = []
    for line in out.splitlines():
        m = re.search(r'frame=\d+ base=(\d+) nentries=(\d+)', line)
        if m:
            frames.append((int(m.group(1)), int(m.group(2))))
    if len(frames) < 20:
        return 0
    total = sum(f[1] for f in frames)
    span = frames[-1][0] - frames[0][0]
    if span <= 0:
        return 0
    n = round(total / (span / 19656.0))
    if n < 2:
        return 0
    return 19656 // n - 1


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
        # only code+state relocate with base (the data tables are patched
        # to arbitrary addresses); the reachable code/state span is
        # $1006-$1845 -> base+$845. Data-table fit is the masked compare's job.
        if base >= s['load'] and base + 0x848 <= 0x10000:
            # relink-stub trampoline: a wrapper puts `JMP real_base+$A1` at
            # base+$A1 (the DMC play body starts A5 F8 = LDA $F8, never a $4C
            # JMP). Follow one hop to the real player. The init stub is
            # resolved separately (it may bounce too, or the real init sits at
            # +$40 when a custom wrapper-init falls through to it).
            if mem[base + 0xA1] == 0x4C:
                rpt = mem[base + 0xA1 + 1] | (mem[base + 0xA1 + 2] << 8)
                rbase = (rpt - 0xA1) & 0xFFFF
                if rbase >= s['load'] and rbase + 0x848 <= 0x10000:
                    base = rbase
            return base, it, jt_addr, 'v5'
    return None, None, None, None


# ---- masked compare, factored so both the raising config builder and the
#      non-raising residue-triage diagnosis share ONE implementation. -------
_DIFF_MSG = {'opcode': 'opcode', 'reloc': 'reloc operand',
             'abs': 'abs operand', 'imm': 'immediate'}


def _diff_play_body(mem, delta, ref, allow_unrelocated: bool = False):
    """First divergence of the PLAY-reachable body vs the relocated reference,
    or None if it matches. Returns (pc, kind, member_val, ref_val) with kind in
    {'oob','opcode','reloc','abs','imm'}. Pure: no raise, no side effects.

    `allow_unrelocated` admits a PARTIALLY-RELOCATED copy (a compilation's
    re-linked sub-player, ledger C31): every reloc operand must be either the
    relocated value OR the canon $1xxx value verbatim — the re-linker only
    patched the paths this song reaches, leaving dead paths at canon
    (Super_Tau-Zeta's $B400 player: 101 such sites, none executed at runtime).
    Build+verify stays the judge of whether a left-canon site is truly dead."""
    for pc, L, rbytes, cls in ref:
        a = pc + delta
        if a + L > 0x10000:
            return (pc, 'oob', 0, 0)
        if mem[a] != rbytes[0]:
            return (pc, 'opcode', mem[a], rbytes[0])
        if L == 3:
            mv = mem[a + 1] | (mem[a + 2] << 8)
            rv = rbytes[1] | (rbytes[2] << 8)
            if cls in ('patched', 'state'):
                continue
            if cls == 'reloc':
                if mv != (rv + delta) & 0xFFFF and not (
                        allow_unrelocated and mv == rv):
                    return (pc, 'reloc', mv, (rv + delta) & 0xFFFF)
            elif mv != rv:
                return (pc, 'abs', mv, rv)
        elif mem[a + 1:a + L] != rbytes[1:]:
            return (pc, 'imm', mem[a + 1], rbytes[1])
    return None


def _diff_init_skel(mem, it, delta):
    """('init_skeleton', it) if the init copy skeleton at `it` is wrong, else
    None. The 4-byte prefix varies (single vs song-indexed); only the
    `A8 A2 00 B9 lo hi 9D <17CF+delta>` copy skeleton is checked."""
    tcf = (0x17CF + delta) & 0xFFFF
    ok = (it + 12 < 0x10000 and mem[it + 3] == 0xA8 and mem[it + 4] == 0xA2
          and mem[it + 6] == 0xB9 and mem[it + 9] == 0x9D
          and (mem[it + 10] | (mem[it + 11] << 8)) == tcf)
    return None if ok else ('init_skeleton', it)


def _resolve_init(mem, it, base, delta):
    """Locate the init copy skeleton. Candidates, in order: the jumptable's
    init target; one JMP hop from it (a relink stub trampolines init too); the
    standard base+$40 (a wrapper's custom init falls through to the real one
    there). Returns the skeleton address, or None if none validate. Standard
    members hit the first candidate, so existing behaviour is unchanged."""
    cands = [it]
    if mem[it] == 0x4C:
        cands.append(mem[it + 1] | (mem[it + 2] << 8))
    cands.append((base + 0x40) & 0xFFFF)
    for c in cands:
        if _diff_init_skel(mem, c, delta) is None:
            return c
    return None


def v5_diagnose(sid_path: str, hvsc_root: str = 'hvsc84') -> dict:
    """Non-raising detection diagnosis for residue triage (the engine behind
    `tools/divergence_census.py`). Walks the SAME stages as `dmc_v5_config`
    but RECORDS the first failure instead of raising, so a whole family's
    detect-reject residue can be clustered by first-divergence site.

    Returns a dict with `status` in
    {'ok','load_error','no_base','family4','oob','player_code_mismatch',
     'init_skeleton','cia_multispeed'} plus, when meaningful, base/delta/init
     and (site, kind) for a player_code_mismatch."""
    try:
        mem, s = _load(os.path.join(hvsc_root, sid_path))
    except Exception as e:                       # noqa: BLE001 - triage report
        return {'status': 'load_error', 'detail': type(e).__name__}
    base, it, jt, layout = _detect_v5(mem, s)
    if layout == 'family4':
        return {'status': 'family4', 'jt': jt}
    if base is None:
        return {'status': 'no_base', 'load': s['load'],
                'play': s['play'], 'init': s['init']}
    delta = base - 0x1000
    out = {'base': base, 'delta': delta & 0xFFFF, 'init': it,
           'play': s['play'], 'load': s['load']}
    d = _diff_play_body(mem, delta, _v5_play_ref())
    if d is not None:
        pc, kind, mv, rv = d
        if kind == 'oob':
            return {**out, 'status': 'oob', 'site': pc}
        return {**out, 'status': 'player_code_mismatch', 'site': pc,
                'kind': kind, 'member': mv, 'ref': rv}
    rit = _resolve_init(mem, it, base, delta)
    if rit is None:
        return {**out, 'status': 'init_skeleton', 'site': it}
    out['init'] = rit
    if s['play'] != jt + 3 and (s.get('speed', 0) & 1):
        return {**out, 'status': 'cia_multispeed'}
    return {**out, 'status': 'ok'}


def _family4_config(sid_path, mem, s, jt_addr) -> DMCV5Config:
    """Build the config for the family-4 (Jupiter41) V5 variant. Same data
    format as family-3, relocated, with a different player — so the extract
    reuses the V5 decode at the family-4 operand sites (FAMILY4_SITES + delta).
    The composer player knobs (2-phase timing, $D416-only filter) are Phase C."""
    from pipelines.dmc.v5.config import FAMILY4_SITES
    base = jt_addr                              # family-4 base = the jump table
    delta = base - 0x1000
    d = DMCV5Config(sid_path=sid_path,
                    name=os.path.splitext(os.path.basename(sid_path))[0],
                    base=base, family4=True)
    for f, pc in FAMILY4_SITES.items():
        setattr(d, f, pc + delta)
    return d


def dmc_v5_config(sid_path: str, hvsc_root: str = 'hvsc84',
                  base_override: 'int | None' = None,
                  n_songs: 'int | None' = None) -> DMCV5Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path))
    if base_override is not None:
        # COMPILATION sub-player (ledger C31): the caller forces the base —
        # auto-detection can't pick it (the file also packs other players,
        # and the scan stops at the first jump table it sees). The masked
        # compare below still validates the player; a partially-relocated
        # re-linked copy is admitted (see _diff_play_body).
        base, jt_addr, layout = base_override, base_override, 'v5'
        if not (mem[base] == 0x4C and mem[base + 3] == 0x4C):
            raise DMCV5Unsupported('no_jumptable',
                                   f'base_override=${base:04X}')
        init_target = mem[base + 1] | (mem[base + 2] << 8)
    else:
        base, init_target, jt_addr, layout = _detect_v5(mem, s)
    if base is None and layout != 'family4':
        raise DMCV5Unsupported(
            'no_jumptable',
            f"load=${s['load']:04X} init=${s['init']:04X} play=${s['play']:04X}")
    if layout == 'family4':
        return _family4_config(sid_path, mem, s, jt_addr)
    delta = base - 0x1000

    # ---- masked identity compare of the PLAY-reachable body vs the
    #      relocated Katusha reference, then the init copy skeleton. Both use
    #      the shared diff helpers (see `v5_diagnose`); the init is validated
    #      separately (it may be relocated/wrapped). ----
    d = _diff_play_body(mem, delta, _v5_play_ref(),
                        allow_unrelocated=base_override is not None)
    if d is not None:
        pc, kind, _mv, _rv = d
        if kind == 'oob':
            raise DMCV5Unsupported('oob', f'${pc:04X}')
        raise DMCV5Unsupported('player_code_mismatch',
                               f'{_DIFF_MSG[kind]} at ${pc:04X}')
    it = _resolve_init(mem, init_target, base, delta)
    if it is None:
        raise DMCV5Unsupported('player_code_mismatch',
                               f'init skeleton at ${init_target:04X}')

    # ---- multi-subtune (song-indexed orderlist record) is emitted as a
    #      multi-song PSID: the composer's init reads song# from A and indexes
    #      ordrec by song#*8; the extract reads one record per subtune. ----

    # ---- CIA multispeed: a wrapper member (play vector not the jump table)
    #      whose PSID speed bit is set runs from a CIA-timer dispatcher; the
    #      V5 verify is VBI-only, so flag it. ----
    cia_period = 0
    if s['play'] != jt_addr + 3 and (s.get('speed', 0) & 1):
        # Wrapper member driven by the CIA1 timer (py65 can't run its init).
        # Measure the rate from the ground-truth writelog (libsidplayfp); the
        # composer programs the same timer + the V5 batch verifies per-IRQ.
        cia_period = _cia_period_from_writelog(
            os.path.join(hvsc_root, sid_path), s['start'] - 1)
        if not (0x0100 <= cia_period <= 0xFFFF):
            raise DMCV5Unsupported('cia_multispeed', f"play=${s['play']:04X}")

    d = DMCV5Config(sid_path=sid_path,
                    name=os.path.splitext(os.path.basename(sid_path))[0],
                    base=base, cia_period=cia_period, n_songs=n_songs)
    # play-body operand sites relocate with the base; the orderlist site is
    # read from the (possibly relocated/wrapped) init's actual load operand.
    for f in ('op_secp_lo', 'op_secp_hi', 'op_instr', 'op_freq_lo',
              'op_freq_hi', 'op_wave_ctrl', 'op_wave_freq', 'op_pulse_lo',
              'op_pulse_hi', 'op_filter_lo', 'op_filter_hi'):
        setattr(d, f, getattr(d, f) + delta)
    d.op_orderlist = it + 7
    return d
