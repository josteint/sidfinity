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


def _observe_play_phases(sid_path: str, subtune: int, play_addr: int,
                         base: int, n_calls: int = 18):
    """Ledger C18 per-call phase schedule for a V5 wrapper member.

    A CIA-multispeed V5 member's PSID play vector is NOT the jump table: it is a
    small wrapper that runs the FULL play (jump-table entry `base+3`) once every
    N calls and an EFFECTS-ONLY pass (a THIRD jump-table entry at `base+6`,
    which canon family-3/5 does not have) on the others. The tune's real tempo
    is the divided rate; running the full play every call makes the rebuild N×
    too fast and one tick out of phase from the first frame.

    ⚠ CLASSIFY BY ENTRY-POINT REACHABILITY, NOT BY THE WRITE FOOTPRINT — the
    C18 card's rule, and it is load-bearing here. The footprints are actively
    misleading on this family: the effects pass emits 21 writes (3 voices × the
    per-voice tail) while the full play emits 18, and early full plays emit
    NOTHING at all while the lead-in runs. A footprint-based reading of
    Cyber_Brain gives `S F F F F S F F F F P ...` — no clean period; watching
    the two jump-table entries gives `P_F123_F123_F123_F123` from call 0.

    ⚠ AND DO NOT PARSE THE WRAPPER. Measured shapes in this corpus: an SMC
    counter living in an `LDX #imm` OPERAND, an `INC/AND #$03/BNE` modulo gate,
    an `INC/CMP #$04/BNE` with an SMC store, and a per-call CIA-latch SWING that
    rewrites $DC05 from a table. Observation covers all of them for free.

    py65 cannot run these members (they are CIA/IRQ-armed — ledger C9), so the
    observer is the libsidplayfp pc-trace, which is also straddle-free.

    Returns a `play_phases` token string ('P_F123_...') or None — None both for
    "no wrapper" (the degenerate all-P schedule, so canon members are
    unaffected) and for any shape that does not settle into a clean period from
    call 0, which the build+verify gate then judges as before.
    """
    if play_addr == base + 3:
        return None                      # canon vector: no wrapper to observe
    try:
        from pipelines.hubbard.verify_cycle import pctrace_per_play_capture
        plays, hits = pctrace_per_play_capture(
            sid_path, subtune, play_addr, n_frames=max(10, n_calls),
            watch_pcs={'full': {base + 3}, 'fx': {base + 6}})
    except Exception:
        return None
    if len(plays) < 8:
        return None
    seq = []
    for i, w in enumerate(plays[:n_calls]):
        h = hits[i] if i < len(hits) else set()
        if 'full' in h:
            seq.append('P')
        elif 'fx' in h:
            voices = sorted({r // 7 for r, _v in w if r < 21})
            if not voices:
                return None              # effects call touching no voice: unmodelled
            seq.append('F' + ''.join(str(v + 1) for v in voices))
        elif not w:
            seq.append('S')
        else:
            return None                  # neither entry reached: unmodelled shape
    n = len(seq)
    for p in range(1, n // 2 + 1):
        if all(seq[i] == seq[i % p] for i in range(n)):
            sched = '_'.join(seq[:p])
            return None if set(seq) == {'P'} else sched
    return None


_REF = None         # full (init+play) reachable-instruction reference
_PLAY_REF = None    # play-ONLY reachable reference (init excluded)


_REF_BIN = os.path.join(os.path.dirname(__file__), '..', 'docs',
                        'dmc5_player_embedded_1000.bin')


def _build_ref(init_pc):
    """Reachable-instruction reference, traced from the COMMITTED player image.

    ⚠ This used to read `hvsc85/DEMOS/G-L/Katusha.sid` at runtime, which made
    every v5 member's player-code validation depend on a file in the music
    collection: an HVSC update that touched that one SID would silently move
    the reference every member is dispatched against, and a missing hvsc85
    tree would break detection outright. That is ledger C20's seventh layer
    (the input changed under the stored artifact) sitting in the DISPATCH
    layer, where no gate can see it. The reference is now a committed binary,
    the way v4 carries `dmc4_player_embedded_1000.bin`, and it is inside the
    fingerprint (the `*.py`-only glob used to skip it).
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from seed_disassembly import trace, _INST_LEN
    mem = bytearray(0x10000)
    with open(_REF_BIN, 'rb') as f:
        blob = f.read()
    mem[0x1000:0x1000 + len(blob)] = blob
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


def _load(sid_path: str, post_init_sub: 'int | None' = None):
    """Load the member's file image into a 64K map.

    `post_init_sub` (0-based) returns the RAM left by running THAT subtune's
    init under py65 instead of the raw file image — for a RELOCATING
    compilation sub-player (ledger C31 + C26; Black_It's family-4 V5 player
    is COPIED to $1000 by the wrapper and absent from the image). Snapshot
    AT THE LANDING (`stop_at_player`), mirroring the V4 factory's _load.
    Falls back to the file image when py65 can't complete the init."""
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
    if post_init_sub is not None:
        from pipelines.dmc.v4.extract.engine_model import _postinit_window
        post = _postinit_window(s, 0, 0x10000, sub=post_init_sub,
                                stop_at_player=True)
        if post is not None:
            mem = bytearray(post)
    return mem, s


# ---------------------------------------------------------------------------
# ledger C26 — the song data is NOT in the file image (the init generates it)
# ---------------------------------------------------------------------------
_TABLE_OPS = ('op_orderlist', 'op_secp_lo', 'op_secp_hi', 'op_instr',
              'op_freq_lo', 'op_freq_hi', 'op_wave_ctrl', 'op_wave_freq',
              'op_pulse_lo', 'op_pulse_hi', 'op_filter_lo', 'op_filter_hi')


def data_tables_off_image(mem, s, d):
    """The data-table addresses `d`'s operand sites resolve to that lie
    OUTSIDE the loaded image — returned only when that pattern is strong
    enough to mean the song cannot be read from the image at all: MOST
    operands outside AND the orderlist among them. `[(field, addr), ...]`
    or None.

    ONE definition, shared by the C26 probe below and the extract's
    `data_tables_off_image` refusal, so the two cannot drift apart: the
    probe must consider exactly the members the refusal would otherwise
    kill, or it either misses carriers or pays py65 for the whole family."""
    lo, hi = s['load'], s['load'] + len(s['payload'])
    addrs = [(f, mem[getattr(d, f)] | (mem[getattr(d, f) + 1] << 8))
             for f in _TABLE_OPS]
    off = [(f, a) for f, a in addrs if not lo <= a < hi]
    order = dict(addrs)['op_orderlist']
    return off if len(off) >= 6 and not lo <= order < hi else None


def _preinit_image(s):
    """The RAM the CPU sees BEFORE init — libsidplayfp's power-on pattern,
    psiddrv's $0000-$03FF wipe, then the loaded image. The baseline that
    makes "the init WROTE this address" decidable from two snapshots."""
    from pipelines.dmc.v4.extract.engine_model import _poweron_fill
    mem = bytearray(0x10000)
    _poweron_fill(mem)
    for a in range(0x400):
        mem[a] = 0
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    return mem


def postinit_view(s):
    """The RAM the engine reads when the init GENERATES the song data.

    Snapshotted AT THE PLAYER LANDING when the init reaches one — that is
    the exact analogue of the file image an ordinary in-image member is
    extracted from (post-unpack, but before the player's own init overwrites
    the leftover state the extract reads as priming; see `_postinit_window`).
    Falls back to running the init to completion for an unpacker that never
    lands on a player head, and to None when py65 cannot run the init at all
    (C9 territory — the caller refuses rather than reading the empty image).
    """
    from pipelines.dmc.v4.extract.engine_model import _postinit_window
    for stop in (True, False):
        post = _postinit_window(s, 0, 0x10000, stop_at_player=stop)
        if post is not None:
            return bytearray(post)
    return None


def _data_post_init(s, mem, d) -> bool:
    """Does this member's init GENERATE its song data (ledger C26)?

    V4's gate for this class counts operands and is all-or-nothing — EVERY
    data-table operand must point outside the loaded image. That refuses a
    genuine unpacker whose freq tables live INSIDE the player body (they
    relocate with it, so they are in-image by construction) or whose
    sector-LO table is a zero block in the player tail (every sector
    page-aligned => every low byte $00).
    `MUSICIANS/P/Piirainen_Antti/Left_Ear_Bleedin_Ear_Left` is exactly that
    shape: 9 of 12 operands point at RAM the file never loads, the other 3
    are those in-player tables, and the wrapper's init pastes the song out
    to $4000-$4700 / $6000+.

    So decide by MEASUREMENT rather than by counting: run the init and
    require that every off-image table address was WRITTEN by it. That is
    the C26 claim stated literally, and it is exactly what separates an
    unpacker from a MISIDENTIFIED player — whose "table addresses" are not
    addresses at all (Ed/We_Were_All_Kids reads a `STA` opcode byte plus its
    operand low byte as "$D89D") and which writes none of them.

    NB the snapshot runs the START song's init; a multi-song member that
    unpacks DIFFERENT data per subtune would need one view per subtune (no
    such carrier exists — the one carrier has a single song)."""
    off = data_tables_off_image(mem, s, d)
    if not off:
        return False
    post = postinit_view(s)
    if post is None:
        return False
    pre = _preinit_image(s)
    return all(any(post[(a + k) & 0xFFFF] != pre[(a + k) & 0xFFFF]
                   for k in range(16))
               for _f, a in off)


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


def v5_diagnose(sid_path: str, hvsc_root: str = 'hvsc85') -> dict:
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


def _family4_config(sid_path, mem, s, jt_addr,
                    hvsc_root: str = 'hvsc85') -> DMCV5Config:
    """Build the config for the family-4 (Jupiter41) V5 variant. Same data
    format as family-3, relocated, with a different player — so the extract
    reuses the V5 decode at the family-4 operand sites (FAMILY4_SITES + delta).

    ⚠ THIS IS A SECOND BUILD PATH, AND IT WAS DEFAULTING PROBED PARAMS —
    ledger C9's recurring shape ("a SECOND build path that defaults probed
    params: fix the CONSTRUCTOR, not the knob"). It measured neither the CIA
    latch nor the C18 phase schedule, so every family-4 member with the PSID
    speed bit was built as VBLANK: 37 members, of which ZERO were FULL. A
    defaulted rate is silently wrong MUSIC, not a refusal."""
    from pipelines.dmc.v5.config import FAMILY4_SITES
    base = jt_addr                              # family-4 base = the jump table
    delta = base - 0x1000
    full = os.path.join(hvsc_root, sid_path)
    cia_period = 0
    if s['play'] != jt_addr + 3 and (s.get('speed', 0) & 1):
        cia_period = _cia_period_from_writelog(full, s['start'] - 1)
        if not (0x0100 <= cia_period <= 0xFFFF):
            raise DMCV5Unsupported('cia_multispeed', f"play=${s['play']:04X}")
    d = DMCV5Config(sid_path=sid_path,
                    name=os.path.splitext(os.path.basename(sid_path))[0],
                    base=base, family4=True, cia_period=cia_period,
                    play_phases=_observe_play_phases(
                        full, s['start'] - 1, s['play'], base) or '')
    for f, pc in FAMILY4_SITES.items():
        setattr(d, f, pc + delta)
    return d


def dmc_v5_config(sid_path: str, hvsc_root: str = 'hvsc85',
                  base_override: 'int | None' = None,
                  n_songs: 'int | None' = None,
                  post_init_sub: 'int | None' = None) -> DMCV5Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path), post_init_sub)
    if base_override is not None:
        # COMPILATION sub-player (ledger C31): the caller forces the base —
        # auto-detection can't pick it (the file also packs other players,
        # and the scan stops at the first jump table it sees). The masked
        # compare below still validates the player; a partially-relocated
        # re-linked copy is admitted (see _diff_play_body). A family-4 head
        # (init +$40 / play +$95 — Black_It's relocated $1000 player)
        # dispatches to the family-4 config like auto-detection would.
        base, jt_addr, layout = base_override, base_override, 'v5'
        if not (mem[base] == 0x4C and mem[base + 3] == 0x4C):
            raise DMCV5Unsupported('no_jumptable',
                                   f'base_override=${base:04X}')
        init_target = mem[base + 1] | (mem[base + 2] << 8)
        play_target = mem[base + 4] | (mem[base + 5] << 8)
        if init_target == base + 0x40 and play_target == base + 0x95:
            layout = 'family4'
    else:
        base, init_target, jt_addr, layout = _detect_v5(mem, s)
    if base is None and layout != 'family4':
        raise DMCV5Unsupported(
            'no_jumptable',
            f"load=${s['load']:04X} init=${s['init']:04X} play=${s['play']:04X}")
    if layout == 'family4':
        d = _family4_config(sid_path, mem, s, jt_addr, hvsc_root)
        d.n_songs, d.post_init_sub = n_songs, post_init_sub
        if post_init_sub is None:
            d.data_post_init = _data_post_init(s, mem, d)
        return d
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

    # C18 phase schedule — observed, never parsed (see _observe_play_phases).
    # Only a non-canon play vector can carry one, so canon members pay nothing.
    play_phases = _observe_play_phases(
        os.path.join(hvsc_root, sid_path), s['start'] - 1, s['play'], base) or ''

    d = DMCV5Config(sid_path=sid_path,
                    name=os.path.splitext(os.path.basename(sid_path))[0],
                    base=base, cia_period=cia_period, n_songs=n_songs,
                    play_phases=play_phases,
                    post_init_sub=post_init_sub)
    # play-body operand sites relocate with the base; the orderlist site is
    # read from the (possibly relocated/wrapped) init's actual load operand.
    for f in ('op_secp_lo', 'op_secp_hi', 'op_instr', 'op_freq_lo',
              'op_freq_hi', 'op_wave_ctrl', 'op_wave_freq', 'op_pulse_lo',
              'op_pulse_hi', 'op_filter_lo', 'op_filter_hi'):
        setattr(d, f, getattr(d, f) + delta)
    d.op_orderlist = it + 7
    if post_init_sub is None:
        d.data_post_init = _data_post_init(s, mem, d)
    return d
