"""DMC V4 config factory — `dmc_v4_config(sid_path)`.

Validates that a SID carries the canonical V4 player and derives its
DMCV4Config. Raises `DMCV4Unsupported(reason)` with a typed reason
bucket otherwise (FC factory-hygiene lesson: typed flags, never
silent misbuilds).

Identity probe = masked byte-compare of the player region against the
canonical carved binary (pipelines/dmc/docs/dmc4_player_embedded_1000.bin):
code + fixed tables must match EXACTLY except the packer-patched
operand positions, the per-song variables block, the copyright string
and the state leftovers. Multi-site operands (the packer patches the
same table address at several LDA abs,y sites) must agree with each
other — inconsistency = shifted/custom code (e.g. On_My_Way_to_X).

Leftover-state probes: the work-file image ships bytes the original
init never clears. The ones the play stream can read are either
captured ($1012-$1014 idle notes, $1018 routing shadow — both already
modeled) or flagged when non-default ($100F-$1011 gate masks, $1019
dual parity, record-0 wave_start with an idling voice).
"""
from __future__ import annotations

import os
import re

from pipelines.dmc.v4.config import DMCV4Config
from pipelines.dmc.engine_constants import VIBDEPTH

_CANON_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs',
                           'dmc4_player_embedded_1000.bin')
# Family-2 reference (carved from DEMOS/G-L/Kajun_Klog.sid, $1000-$17B0):
# the V4-derived build with the relocated instrument table ($17B0) and the
# $FF-terminator sector encoding. The play body + effect chain are
# canon-compatible, but the init / note-init tail / gate-off / hard-restart
# / rest dispatch / sector decoder differ — so family-2 members compare
# against THIS reference, not canon. See pipelines/dmc/family2/RE_NOTES.md.
_FAMILY2_PATH = os.path.join(os.path.dirname(__file__), '..', 'docs',
                             'dmc4_family2_player_1000.bin')
_F2_INSTR_BASE = 0x17B0      # code/data boundary (instr table base @ $1000)
# family-2 data regions masked out of the identity compare (per-tune /
# leftovers): vars + copyright, then the all-off/sfx PSID sub-entries
# ($162F-$1646, NEVER executed during play() — sub-builds re-author them
# freely, same rationale as canon's _MASKED_RANGES), then freq tables +
# state up to the instr table. The reachable PLAY code is $1037-$162E.
_F2_DATA_MASK = [(0x100C, 0x1037), (0x162F, _F2_INSTR_BASE)]

# packer-patched operand sites: name -> list of operand addresses
# (each site = 2 bytes lo/hi); per name all sites must agree
# (filter sites are filtdef + a fixed per-site offset).
_SITES = {
    'tunetab':  [0x1051, 0x180E],
    'secp_lo':  [0x1103],
    'secp_hi':  [0x1108],
    'instr':    [0x1227],
    'wavectrl': [0x159C, 0x15D9],
    'wavefreq': [0x15B9, 0x15FB],
    'filtdef':  [0x1296],
}
# filtdef satellite sites: operand = filtdef + offset
_FILT_SAT = [(0x12AC, 1), (0x12B2, 2), (0x12B8, 3), (0x13E7, 4), (0x13ED, 10)]
# tunetab satellite sites: operand = tunetab + 1 (the hi-byte reads)
_TUNE_SAT = [(0x1057, 1), (0x1814, 1)]

# 2ENTRY layout: the restructured-init regions that differ from canon
# (the play body matches, so masking these lets the canon identity
# compare pass). The 2-entry reads the tune table at $180E (tune setup,
# also a canon site) rather than canon's $1051 init-tail site.
_V2ENTRY_MASK = [(0x1000, 0x100C), (0x1050, 0x10B0), (0x162F, 0x1647),
                 (0x17EC, 0x17FB), (0x184B, 0x187E)]
_V2ENTRY_TUNETAB_SITE = 0x180E
_V2ENTRY_TUNE_SAT = [(0x1814, 1)]
# instrument satellite sites: operand = $18F0 + offset
_INST_SAT = [(0x122B, 1), (0x1242, 2), (0x1358, 3), (0x1258, 6),
             (0x1289, 6), (0x12CD, 7), (0x12DD, 8), (0x12E3, 9),
             (0x123B, 10), (0x126A, 10), (0x127A, 10), (0x12E9, 10)]

# track-loop hook site: canonical = STA $1726,x (loop to 0); the JSR
# hook variant reads the next track byte as the loop target. Both
# operands relocate with base. (hook signature: iny / lda ($f8),y /
# sta $1726,x / rts — validated inline, relocation-aware.)
_LOOP_SITE = 0x10DF

# regions masked out of the identity compare (per-song / leftovers /
# dead-code gaps). The gap fragments are unreachable padding between
# routines that nonetheless carry relocated operands (e.g. a dead
# JMP $110C / STA $1975) the trace never reaches — never executed, so
# they don't affect the writelog; masking keeps the compare reloc-clean.
_MASKED_RANGES = [
    (0x100C, 0x1050),    # player vars + copyright string
    (0x110F, 0x1113),    # dead-code gap
    (0x119A, 0x11A2),    # dead-code gap (holds a dead JMP $110C)
    (0x131B, 0x1322),    # dead-code gap
    (0x162F, 0x1647),    # all-off (+$06) + sfx (+$09) routines — these are
                         # the PSID sub-entries, NEVER executed during play()
                         # (the verify only drives the play vector), so their
                         # per-build variation is irrelevant to the write
                         # stream. Sub-builds re-author them freely.
    (0x1647, 0x1707),    # freq tables (per-tune tuning, carried in USF)
    (0x1707, 0x170D),    # track ptr leftovers
    (0x1716, 0x17C0),    # state leftovers
    (0x17C3, 0x17C5),    # dead-code gap
    (0x187E, 0x1885),    # dead-code gap (holds a dead STA $1975)
    (0x18E8, 0x18F0),    # gap before instruments
]


class DMCV4Unsupported(Exception):
    def __init__(self, reason: str, detail: str = ''):
        self.reason = reason
        self.detail = detail
        super().__init__(f'{reason}: {detail}' if detail else reason)


# Canon's self-referencing operands: every 3-byte instruction whose
# 16-bit operand points into the fixed player region [$1000,$1900)
# (code, RAM state, freq/vibdepth tables) relocates with base. Computed
# once by tracing the canonical player; used to relocate the reference
# image so the identity compare is base-invariant.
_RELOC_INSTRS = None      # list[(pc, operand_value)]


def _canon_reloc_instrs():
    global _RELOC_INSTRS
    if _RELOC_INSTRS is not None:
        return _RELOC_INSTRS
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from seed_disassembly import trace, _INST_LEN
    canon = open(_CANON_PATH, 'rb').read()
    mem = bytearray(0x10000)
    mem[0x1000:0x1000 + len(canon)] = canon
    # trace both the loop-to-0 player AND the +$006 / +$009 entries
    # (all-off, sfx) so every reachable instruction is covered.
    _c, starts, _l, _j = trace(bytes(mem), 0, 0x1000, 0x1003, (0x1006, 0x1009))
    out = []
    for pc in sorted(starts):
        if pc < 0x1000 or pc + 2 >= 0x1000 + len(canon):
            continue
        if _INST_LEN[mem[pc]] == 3:
            val = mem[pc + 1] | (mem[pc + 2] << 8)
            if 0x1000 <= val < 0x1900:
                out.append((pc, val))
    _RELOC_INSTRS = out
    return out


_F2_REF = None      # (ref_bytes, masked[], reloc_instrs)


def _family2_ref():
    """Trace the carved family-2 reference once: return its byte image,
    the compare mask (1 = ignore: data regions + per-song operand bytes +
    non-reachable bytes), and the self-ref operand list (relocates with
    base). Mirrors _canon_reloc_instrs but reachable-instruction-precise."""
    global _F2_REF
    if _F2_REF is not None:
        return _F2_REF
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from seed_disassembly import trace, _INST_LEN
    ref = bytearray(open(_FAMILY2_PATH, 'rb').read())   # $1000-$17B0
    mem = bytearray(0x10000)
    mem[0x1000:0x1000 + len(ref)] = ref
    # entries: init $1037 / play $1085 / all-off $162F / sfx $163E
    _c, starts, _l, _j = trace(bytes(mem), 0, 0x1037, 0x1085, (0x162F, 0x163E))
    masked = bytearray([1]) * _F2_INSTR_BASE        # default: ignore
    reloc = []
    for pc in sorted(starts):
        if pc < 0x1000 or pc >= _F2_INSTR_BASE:
            continue
        L = _INST_LEN[mem[pc]]
        if pc + L > _F2_INSTR_BASE:
            continue
        for i in range(pc, pc + L):
            masked[i] = 0                           # compare this code byte
        if L == 3:
            op = mem[pc + 1] | (mem[pc + 2] << 8)
            if _F2_INSTR_BASE <= op < 0x1C00:
                masked[pc + 1] = masked[pc + 2] = 1  # per-song table operand
            elif 0x1000 <= op < _F2_INSTR_BASE:
                reloc.append((pc, op))               # self-ref (relocates)
    # data regions + the jump table (validated separately) are never code
    for a, b in _F2_DATA_MASK + [(0x1000, 0x100C)]:
        for i in range(a, b):
            masked[i] = 1
    _F2_REF = (ref, masked, reloc)
    return _F2_REF


def _load(sid_path: str, post_init_sub: 'int | None' = None):
    """Load the member's file image into a 64K map.

    `post_init_sub` (0-based) returns the RAM left by running THAT subtune's
    init under py65 instead of the raw file image — for a RELOCATING
    compilation player (ledger C31 + C26), which the wrapper copies into place
    at init and which therefore is not in the file image at all. Falls back to
    the file image when py65 can't complete the init (C9 territory); the
    caller's locate then fails cleanly rather than reading a half-built map."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools'))
    import struct
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    raw = open(sid_path, 'rb').read()
    s['speed'] = struct.unpack('>I', raw[18:22])[0]   # PSID speed bitmask
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


def _rd16(mem, a):
    return mem[a] | (mem[a + 1] << 8)


def _cia_period_from_writelog(sid_path: str, subtune: int,
                              dur: float = 3.0) -> int:
    """Measure the multispeed CIA period from the GROUND-TRUTH writelog
    (libsidplayfp) when py65 can't read the latch (init hangs / unsupported
    opcode / timer set in an IRQ handler). The player's IRQ fires every L+1
    cycles; over a PAL frame (19656 cyc) it runs N = 19656/(L+1) play()s.
    Measure N = total play()s / PAL-frames from `--writelog-per-irq
    --per-irq-debug` (nentries per siddump frame; base = absolute PHI1 clock),
    round to the integer multispeed factor, and return the canonical latch
    19656/N - 1 (e.g. N=2 -> $2663, N=4 -> $1331 — the exact DMC inits).
    Single-speed CIA (N rounds to <2): a speed-bit tune whose init programs
    NO timer runs at the PSID environment's DEFAULT latch $4025 (16422
    cycles, ~60 Hz) — measure the exact play-entry period and return $4025
    when it matches (Phobos/Crazy_Mix). Returns 0 if not measurable /
    any other single-speed rate."""
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
    span = frames[-1][0] - frames[0][0]        # base = absolute PHI1 clock
    if span <= 0:
        return 0
    n = round(total / (span / 19656.0))
    if n >= 2:
        canon = 19656 // n - 1
        # Cross-check the canonical latch against the MEASURED long-run mean
        # entry period (r132, Falu_Mix — C9 8th occ): a player that REPROGRAMS
        # the latch every IRQ (tempo-swing cycle [4033,4033,4033,7610]) has a
        # non-canonical effective rate; returning the canonical builds a
        # 0.3%-fast rebuild = a guaranteed length partial. The mean is
        # entry0-anchored (exact period count between first and last entry0
        # — the base-span estimator's ±1-frame edge error is bigger than the
        # signal). Canonical members measure within a couple of cycles of
        # canon+1 and are returned unchanged.
        def _med(txt):
            # median of per-frame per-period estimates — for a cyclic
            # latch schedule, frames holding whole cycles dominate, so the
            # median IS the steady whole-cycle average; and unlike an
            # entry0-anchored raw mean it is IMMUNE to the init->first-play
            # gap outlier (which inflated a 3s mean by ~+7 cycles and made
            # this branch fire for dozens of truly-canonical members).
            # frame0's delta (the init gap) is skipped outright.
            ent = [(int(m.group(1)), int(m.group(2))) for m in
                   re.finditer(r'nentries=(\d+) entry0=(\d+)', txt)]
            per = [(e1 - e0) / n0
                   for (n0, e0), (_, e1) in zip(ent[1:], ent[2:])
                   if n0 >= 1 and e1 > e0]
            if len(per) < 20:
                return None
            per.sort()
            return per[len(per) // 2]
        med = _med(out)
        if med is not None and abs((canon + 1) - med) > 4:
            # rare path (Falu_Mix-class swing drivers): re-measure over 10 s
            try:
                out10 = subprocess.run(
                    [sd, sid_path, '--writelog-per-irq', '--per-irq-debug',
                     '--duration', '10', '--subtune', str(subtune)],
                    capture_output=True, text=True, timeout=120).stderr
                m10 = _med(out10)
                if m10 is not None:
                    med = m10
            except Exception:
                pass
            return round(med) - 1
        return canon
    # Single-speed: measure the exact entry-to-entry period (entry0 = the
    # play-entry PHI1 clock per siddump frame; a frame holding 2 entries
    # yields a doubled delta — the median discards those). The DEFAULT CIA
    # latch is the only single-speed value admitted; a 50 Hz-ish period is
    # indistinguishable from a correct vblank build, leave it 0.
    entries = [int(m.group(1)) for m in
               re.finditer(r'entry0=(\d+)', out)]
    deltas = sorted(b - a for a, b in zip(entries, entries[1:]) if b > a)
    if not deltas:
        return 0
    period = deltas[len(deltas) // 2]
    if abs(period - 0x4026) <= 2:      # default latch $4025 -> 16422 cycles
        return 0x4025
    return 0


def _cia_entry_period(sid_path: str, subtune: int, dur: float = 3.0):
    """Measure the ACTUAL steady play-entry period from the ground-truth
    writelog debug stream. Returns (median_period, stable) or None when
    unmeasurable. `stable` = >=80% of per-period estimates within +/-3
    cycles of the median (a C18 phase wrapper / alternating-latch driver
    fails stability and must not be judged by the median)."""
    import subprocess
    import re
    import statistics
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                      'tools', 'siddump')
    try:
        out = subprocess.run(
            [sd, sid_path, '--writelog-per-irq', '--per-irq-debug',
             '--duration', str(dur), '--subtune', str(subtune)],
            capture_output=True, text=True, timeout=90).stderr
    except Exception:
        return None
    frames = []
    for line in out.splitlines():
        m = re.search(r'nentries=(\d+) entry0=(\d+)', line)
        if m:
            frames.append((int(m.group(1)), int(m.group(2))))
    per = []
    for (n0, e0), (_, e1) in zip(frames, frames[1:]):
        if n0 >= 1 and e1 > e0:
            per.append((e1 - e0) / n0)
    if len(per) < 20:
        return None
    med = statistics.median(per)
    stable = sum(1 for p in per if abs(p - med) <= 3) / len(per) >= 0.8
    return round(med), stable


def _cia_period_crosschecked(sid_path: str, subtune: int) -> int:
    """`_cia_period_from_init`, CROSS-CHECKED against the ground-truth
    entry-period measurement (ledger C9, 6th occ — Big_GLORZ): the py65
    post-init $DC04/$DC05 snapshot can be a plausible WRONG latch when the
    fine byte is programmed where the init run never reaches (Big_GLORZ:
    init leaves $2600, the $63 lo byte lands from a second site — measured
    steady period 9828 = the canonical $2663). Keep the init latch when the
    measured period agrees (+/-3 cyc jitter) or the measurement is
    unstable/unavailable (byte-identical for every truthful-init member);
    on a STABLE disagreement return `measured_period - 1`."""
    cp = _cia_period_from_init(sid_path, subtune)
    if not (0x0100 <= cp <= 0xFFFF):
        return cp
    m = _cia_entry_period(sid_path, subtune)
    if m is None:
        return cp
    period, stable = m
    if not stable or abs((cp + 1) - period) <= 3:
        return cp
    return period - 1


def _cia_period_from_init(sid_path: str, subtune: int,
                          max_cycles: int = 3_000_000) -> int:
    """Run the PSID init in py65 and read the CIA1 timer A latch
    ($DC04/$DC05) the wrapper programs — the multispeed play rate.
    Returns 0 if init never returns or programs no timer."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mpu = MPU()
    mem = ObservableMemory()
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    mpu.memory = mem
    mpu.stPush(0x00)
    mpu.stPush(0x00)               # RTS sentinel -> PC = $0001
    mpu.pc = s['init']
    mpu.a = subtune
    mpu.x = mpu.y = 0
    for _ in range(max_cycles):
        if mpu.pc == 0x0001:
            break
        try:
            mpu.step()
        except Exception:
            return 0
    else:
        return 0
    return mem[0xDC04] | (mem[0xDC05] << 8)


def _post_init_ram(sid_path: str, subtune: int,
                   max_cycles: int = 3_000_000):
    """Run the PSID init in py65 and return the post-init RAM (an
    ObservableMemory), or None if init never returns / crashes. Used by the
    dataflow path to capture leftover-priming bytes a re-assembled init may
    clear (canon init provably never touches them, so canon keeps reading
    the file image)."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mpu = MPU()
    mem = ObservableMemory()
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    mpu.memory = mem
    mpu.stPush(0x00)
    mpu.stPush(0x00)               # RTS sentinel -> PC = $0001
    mpu.pc = s['init']
    mpu.a = subtune
    mpu.x = mpu.y = 0
    for _ in range(max_cycles):
        if mpu.pc == 0x0001:
            return mem
        try:
            mpu.step()
        except Exception:
            return None
    return None


def _observe_play_phases(sid_path: str, subtune: int, base: int,
                         n_calls: int = 12):
    """OBSERVE a play-vector wrapper's phase behaviour under libsidplayfp
    (`siddump --pc-watch`, the GROUND-TRUTH engine — Phase 2 of
    docs/siddump_native_capture_plan.md; the py65 twin was deleted after an
    A/B gate over the C18 carriers). Semantics unchanged: watch the three
    canon entry points and classify each play() invocation by which it
    reached —
        P = the full play body (base+$85)
        F<voices> = the per-voice frame entry (base+$1F9) without the play
            body (voices = the X&3 values seen there)
        R<voices> = the per-voice glide/write tail (base+$41C) only
        S = none of them (silent no-op)
    then return the minimal repeating period as a 'P_F123'-style string, or
    None when observation fails / the sequence doesn't settle. All three
    watch PCs hold 3-byte instructions (DEC abs / LDA abs,X), so the C36
    execution signature fires within the instruction and X samples
    pre-instruction — identical to the py65 twin's pc==entry check. Events
    with play-index 0 (during init) are dropped, as the twin discarded its
    init run's hits; a play() with no watched hit classifies S via the
    play-index GAP, which is sound for every call below the highest index
    seen. Classification anchors at the FIRST index carrying events, not
    index 1: the play counter is a bus-read proxy, so an init-time DATA read
    of the play vector address bumps it once and every real call shifts +1
    (27/204 A/B carriers) — the phantom leading index would read as S and
    break the fit. That anchor equals the py65 twin's call 1 (its first
    play() after init); a phantom bump LATER in the window still inserts a
    false S and fails the fit -> None -> the pctrace fallback (safe), and a
    genuine leading-S schedule is S-containing, which the call site replaces
    with the pctrace answer anyway."""
    import subprocess
    p_play, p_fe, p_et = base + 0x85, base + 0x1F9, base + 0x41C
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', '..', '..'))
    siddump = os.path.join(repo, 'tools', 'siddump')
    try:
        out = subprocess.run(
            [siddump, sid_path, '--pc-watch',
             '%X,%X,%X' % (p_play, p_fe, p_et), '0-0',
             '--subtune', str(subtune + 1), '--duration', '2'],
            capture_output=True, text=True, timeout=120)
    except Exception:
        return None
    per = {}
    max_idx = 0
    for line in out.stdout.splitlines():
        pos = 0
        while True:
            pos = line.find('|PW:', pos)
            if pos < 0:
                break
            f = line[pos + 4:].split(':', 6)
            if len(f) < 7:
                break
            pc, x, idx = int(f[0], 16), int(f[2], 16), int(f[4], 10)
            if idx > 0:
                max_idx = max(max_idx, idx)
                rec = per.setdefault(idx, [False, set(), set()])
                if pc == p_play:
                    rec[0] = True
                elif pc == p_fe:
                    rec[1].add(x & 0x03)
                elif pc == p_et:
                    rec[2].add(x & 0x03)
            pos += 4
    if not per:
        return None
    i0 = min(per)                     # first play with events = py65's call 1
    if max_idx < i0 + n_calls:        # too few observed plays to classify 12
        return None
    seq = []
    for i in range(i0, i0 + n_calls):
        hp, fv, rv = per.get(i, (False, set(), set()))
        if hp:
            seq.append('P')
        elif fv:
            seq.append('F' + ''.join(str(v + 1) for v in sorted(fv)))
        elif rv:
            seq.append('R' + ''.join(str(v + 1) for v in sorted(rv)))
        else:
            seq.append('S')
    for p in range(1, n_calls // 2 + 1):
        if all(seq[i] == seq[i % p] for i in range(n_calls)):
            return '_'.join(seq[:p])
    return None


def _frame_entry_candidates(payload, load: int) -> set:
    """Locate the per-voice FRAME-ENTRY by shape for re-assembled members:
    `LDA pending,X / BNE +3 / JMP effects` = bytes `bd ?? ?? d0 03 4c` (canon
    $11F9; re-assembled variants shift it, e.g. My_Rusty_Love $11FA). Used by
    the offset-blind phase observers to classify F POSITIVELY by entry
    reachability — the value-advance heuristic alone false-reads a HELD note's
    frame entry as R (all its writes are idempotent), dropping the holding
    AD/SR=$00 re-assert (sub_17EC) from the rebuild's schedule."""
    b = bytes(payload)
    return {load + i for i in range(len(b) - 6)
            if b[i] == 0xbd and b[i + 3] == 0xd0
            and b[i + 4] == 0x03 and b[i + 5] == 0x4c}


def _effects_tail_candidates(payload, load: int) -> set:
    """Locate the per-voice glide/write EFFECTS-TAIL head (canon $141C — the R
    body's entry) by shape: `LDA glsp,X / BEQ +$7E` = bytes `bd ?? ?? f0 7e`.
    Used by the offset-blind phase observers to classify R POSITIVELY by entry
    reachability: a wrapper that JSRs the effects tail directly (Real_Hardcore
    `LDX/JSR $141C x3`) legitimately ADVANCES the chip while a vibrato/glide
    runs, so the chip-state rule alone false-reads it as F — and the F arm
    entry (wavestep, past the vib update) then loses the per-call vib step.
    A frame-entry (F) call FALLS THROUGH into $141C, so this signal is only
    meaningful when frame-entry candidates are also locatable and NOT hit."""
    b = bytes(payload)
    return {load + i for i in range(len(b) - 5)
            if b[i] == 0xbd and b[i + 3] == 0xf0 and b[i + 4] == 0x7e}


def _observe_play_phases_pctrace(sid_path: str, subtune: int, play_addr: int,
                                 n_calls: int = 16):
    """Ground-truth play-phase observation from the STRADDLE-FREE libsidplayfp
    pc-trace — the reliable replacement for py65 observation when py65 can't run
    the member (CIA/IRQ-armed tunes that idle silent under the interpreter).

    The earlier `_observe_play_phases_writelog` (parked 2026-07-03) bucketed the
    per-IRQ writelog by play-entry CYCLE, so a play() spanning a siddump-frame
    boundary straddled into the next chunk (Domination's aperiodic 'F12,P,P'
    hiccup, the guessy phase rotation). `pctrace_per_play_capture` buckets by CPU
    INVOCATION (writes between consecutive PC==play_addr entries), which never
    straddles — verified on F.A.K.E-Intro: the writelog view showed a spurious
    'F P P' warm-up, the pc-trace view is a clean 'P F123 P F123' from call 0.

    Same 'P_F123'-style output + minimal-period fit as the canon observer
    (P = the $D416 filter tail; F<voices>/R<voices>/S). The verify gate is the
    net for any misclassification (C18: observe, don't parse). Returns None when
    the sequence doesn't settle into a clean period from call 0."""
    try:
        from pipelines.hubbard.verify_cycle import pctrace_per_play_capture
        from seed_disassembly import parse_psid
        s = parse_psid(sid_path)
        fe_cands = _frame_entry_candidates(s['payload'], s['load'])
        et_cands = _effects_tail_candidates(s['payload'], s['load'])
        # ~2 invocations per 50 Hz frame under 2x CIA; capture enough for a
        # period<=n_calls//2 fit plus headroom.
        plays, wp_hits = pctrace_per_play_capture(
            sid_path, subtune, play_addr, n_frames=max(10, n_calls),
            watch_pcs={'fe': fe_cands, 'et': et_cands})
    except Exception:
        return None
    if len(plays) < 8:
        return None
    # R vs F by CHIP STATE (the former py65 write-footprint observer's rule): a pure
    # refresh can only re-emit values already on the chip; an effects call
    # eventually writes a value that DIFFERS from the current register content.
    # The capture drops the init prefix, so the chip starts unknown — a reg's
    # FIRST sighting is recorded, never counted as advancing (a refresh
    # re-emitting an init-written reg must not false-F); a genuine effects
    # phase changes a known reg within the window. Comparing against the
    # previous call's write set (the old rule) misread a wave-step whose early
    # steps repeat values (chord [0,0,0,3,...]) as R — Bladeswede played its
    # arpeggio's first tone forever.
    chip = {}
    seq = []
    for i, w in enumerate(plays[:n_calls]):
        regs = {r for r, _ in w}
        # F POSITIVELY when the invocation reached the (signature-located)
        # frame entry — the advance heuristic alone false-reads a HELD note's
        # idempotent frame entry as R (My_Rusty_Love; see
        # the deleted py65 write-footprint observer).
        h = wp_hits[i] if i < len(wp_hits) else set()
        advancing = 'fe' in h
        adv_chip = False
        for r, v in w:
            if r in chip and chip[r] != v:
                adv_chip = True
            chip[r] = v
        # Same rule the deleted write-footprint observer used: chip-state advance is the
        # fallback, EXCEPT for a call that positively entered the effects tail
        # ($141C = the R body) without passing a locatable frame entry — that
        # entry advances the chip whenever a vibrato/glide runs
        # (Real_Hardcore's wrapper JSRs $141C x3; advance-as-F lost the
        # per-call vib step behind the wavestep arm entry). Arm F entries
        # ($1591/$1567) sit past $141C and keep classifying F via advance.
        if adv_chip and not ('et' in h and fe_cands):
            advancing = True
        if not w:
            seq.append('S')
        elif 0x16 in regs:
            seq.append('P')
        else:
            voices = sorted({r // 7 for r in regs if r < 21})
            vs = ''.join(str(v + 1) for v in voices)
            seq.append(('F' if advancing else 'R') + vs)
    n = len(seq)
    # Period fit is done on a COLLAPSED key (F<v> and R<v> both -> 'x<v>'): an
    # effects phase reads R on occurrences where its program repeats values,
    # which would spuriously break an otherwise clean period. Voice set + P/S
    # must still match. Once a period is found, each phase position's OUTPUT
    # token is resolved from all its occurrences: ANY advancing occurrence =>
    # F<v> (a refresh can never advance, so this has no false positive); all
    # non-advancing => R<v> (a pure register refresh, e.g. Compotune_1's
    # P_R123_R123_R123).
    def _key(t):
        return t if t in ('P', 'S') else 'x' + t[1:]
    keys = [_key(t) for t in seq]
    for p in range(1, n // 2 + 1):
        if not all(keys[i] == keys[i % p] for i in range(n)):
            continue
        out = []
        for k in range(p):
            toks = [seq[i] for i in range(k, n, p)]
            base = toks[0]
            if base in ('P', 'S'):
                out.append(base)
            else:
                anyF = any(t[0] == 'F' for t in toks)
                out.append(('F' if anyF else 'R') + base[1:])
        return '_'.join(out)
    return None


def _detect_notestart_arm(sid_path: str, subtune: int, play_addr: int) -> bool:
    """Does this member DEFER note-init by one play() call — the 2-frame
    note-start ARM? Some CIA play-routine variants enter the F phase PAST the
    $11F9 note-init check, so a note fetched on a P call only ARMS (wave-step
    only, envelope held at the $0F0F hard-restart leftover) on the intervening
    F call, then loads the real AD/SR on the NEXT P call. Others do note-init
    on the F call directly (no arm). This is a per-member play-routine property
    NOT derivable from the schedule string (Words and F.A.K.E-Intro are both
    P_F123 but Words is immediate, F.A.K.E defers) or the multispeed factor
    (both 1.82 calls/frame) — so observe it, C18-style.

    Detected from the WRITE FOOTPRINT (reloc-invariant, no PCs): after a voice's
    hard-restart call (ctrl=$08, AD=SR=$0F), the FIRST call that re-emits that
    voice's freq/ctrl is the note-init iff it ALSO writes AD/SR; if it writes
    freq/ctrl with NO AD/SR it is the ARM => deferred. note-init ALWAYS carries
    AD/SR ($D405/$D406 at $1234/$1230), so a 'deferred' verdict is never a false
    positive — the change is regression-safe by construction. Conservative
    (returns False = immediate = current behaviour) when no HR is observed
    (soft-start openings) or no emit follows.

    ALL voices are checked and ANY arm footprint => deferred: with a partial
    F phase (e.g. P_F3) only the F-phase voice defers — the others note-init
    directly on P calls and read "immediate", so the first-HR-voice verdict
    alone misses the deferring voice (Dresden_Party: V2 immediate, V3 arms).

    The window ESCALATES (12 -> 96 frames) when the short pass is
    inconclusive — some voice showed no HR (soft-start opening) or no emit
    followed within it. Wavefrontline's first HR is at play ~41 (~21 frames
    at 2x), past the original fixed 12-frame window, yet the member defers
    from its very first soft note — the HR footprint is the only observable
    discriminator, so look far enough to find one. A definitive "immediate"
    on all three voices stops the escalation."""
    try:
        from pipelines.hubbard.verify_cycle import pctrace_per_play_capture
    except Exception:
        return False
    for n_frames in (12, 96):
        try:
            plays = pctrace_per_play_capture(sid_path, subtune, play_addr,
                                             n_frames=n_frames)
        except Exception:
            return False
        inconclusive = False
        for v in range(3):
            b = v * 7
            flo, fhi, ctl, ad, sr = b, b + 1, b + 4, b + 5, b + 6
            hr = next((i for i, fr in enumerate(plays)
                       if dict(fr).get(ctl) == 0x08 and dict(fr).get(ad) == 0x0F
                       and dict(fr).get(sr) == 0x0F), None)
            if hr is None:
                inconclusive = True                    # no HR seen (yet)
                continue
            for j in range(hr + 1, min(hr + 6, len(plays))):
                regs = {r for r, _ in plays[j]}
                if regs & {flo, fhi, ctl}:             # first note-emit call
                    if not regs & {ad, sr}:            # arm iff no envelope
                        return True
                    break
            else:
                inconclusive = True                    # no emit in the window
        if not inconclusive:
            return False                               # all voices immediate
    return False


def _vibhalf_candidates(payload, load: int) -> set:
    """Locate the vibrato half-cycle entry ($1567) by shape, reloc/re-assembly
    invariant: `LDA #$00 / STA ctr,x / LDA dir,x / EOR #$01 / STA dir,x` =
    bytes `a9 00 9d ?? ?? bd ?? ?? 49 01 9d` (the same shape the rest-tail
    vibflip target check keys on)."""
    b = bytes(payload)
    return {load + i for i in range(len(b) - 11)
            if b[i] == 0xa9 and b[i + 1] == 0x00 and b[i + 2] == 0x9d
            and b[i + 5] == 0xbd and b[i + 8] == 0x49
            and b[i + 9] == 0x01 and b[i + 10] == 0x9d}


def _detect_fx_entry_vibhalf(sid_path: str, subtune: int,
                             play_addr: int) -> bool:
    """Does the wrapper's F phase enter the player at the VIBRATO HALF-CYCLE
    boundary ($1567: vibctr=0, flip vibdir, swell, fall through wavestep)
    instead of the plain wave step ($1591)? The two entries emit IDENTICAL
    writes on the F call itself (wavestep + sidwrite) — the difference is
    vibrato STATE only, observable later as the vibrato's shape (Acid_Dance:
    3 flips between full plays -> a +/-vstep square, where the wavestep entry
    free-runs the triangle). Not derivable from the write footprint, so watch
    ENTRY REACHABILITY (C18 canonical form): classify each observed play()
    invocation P (writes $D416) or F (voice writes, no $D416) off the same
    pc-trace, and answer vib_half iff EVERY F invocation executed a
    shape-located $1567 candidate. A wavestep-entry F call can never reach
    $1567 (it lies upstream of $1591, nothing jumps back), so a True verdict
    has no false positive on the arm members this probe is gated to
    (notestart_arm=1: entry is past note-init by observation) —
    regression-safe by construction."""
    try:
        from pipelines.hubbard.verify_cycle import pctrace_per_play_capture
        from seed_disassembly import parse_psid
    except Exception:
        return False
    try:
        s = parse_psid(sid_path)
        cands = _vibhalf_candidates(s['payload'], s['load'])
        if not cands:
            return False
        plays, hits = pctrace_per_play_capture(sid_path, subtune, play_addr,
                                               n_frames=12, watch_pcs=cands)
    except Exception:
        return False
    f_hits = []
    for fr, hit in zip(plays, hits):
        if not fr:
            continue
        regs = {r for r, _ in fr}
        if 0x16 in regs:
            continue                       # P (full play body)
        if regs & set(range(0x15)):
            f_hits.append(hit)             # F (per-voice, no $D416 tail)
    return len(f_hits) >= 4 and all(f_hits)


def _rphase_pulse_tail_probe(sid_path: str, subtune: int, base: int) -> bool:
    """Does the play-vector wrapper's R (non-tick) phase re-run the pulse
    program TAIL — a SECOND pulse advance per music tick (C18 entry variant,
    R-phase twin of _detect_fx_entry_vibhalf)?

    Toccata_v2's init generates a parity wrapper (`$2702`: full-play every
    other call, `$1006 -> $162F: JSR $135D x3` on the rest). `$135D` is the
    pulse routine PAST its `LDA $18f3,y / STA $171F` speed-nibble reload, so
    the tail computes its step from the STALE $171F left by the prior
    full-play frame — a real second sweep the write-footprint observer misses
    (it read the phase as a plain register-refresh `R` because the pulse holds
    its value for the first ~6 frames, before the sweep moves). Detect it by
    EXECUTION (C18 'observe, don't parse'): run a few play() calls and watch
    for a `JSR base+$35D`. The full-play path reaches $135D by FALL-THROUGH
    from $134E (never a JSR), so a JSR to it is uniquely the wrapper's R entry.

    Regression-safe by construction: only members that actually execute this
    JSR get rphase_variant='pulse_tail'; every other build is byte-identical
    (census over all 743 non-canonical-play family-1 members: sole carrier is
    Bakewell_Dwayne/Toccata_v2). Returns False if py65 can't run the member."""
    try:
        from py65.devices.mpu6502 import MPU
        from py65.memory import ObservableMemory
        from seed_disassembly import parse_psid
    except Exception:
        return False
    try:
        s = parse_psid(sid_path)
    except Exception:
        return False
    mpu = MPU()
    mem = ObservableMemory()
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    mpu.memory = mem
    target = (base + 0x35D) & 0xFFFF

    def run(pc: int, acc: int, watch: bool) -> bool:
        mpu.stPush(0x00)
        mpu.stPush(0x00)                        # RTS sentinel -> PC = $0001
        mpu.pc = pc
        mpu.a = acc
        hit = False
        for _ in range(200_000):
            pcv = mpu.pc
            if pcv == 0x0001:
                return hit
            if watch and mem[pcv] == 0x20 and \
                    (mem[pcv + 1] | (mem[pcv + 2] << 8)) == target:
                hit = True
            try:
                mpu.step()
            except Exception:
                return hit
        return hit

    try:
        run(s['init'], subtune, False)          # generate the wrapper in RAM
        # A parity wrapper alternates full-play / R every other call; 8 calls
        # covers several R phases regardless of the seeded parity.
        for _ in range(8):
            if run(s['play'], 0, True):
                return True
    except Exception:
        return False
    return False


def _detect_play_repeat(mem, play: int, base: int, load: int) -> int:
    """INTERNAL multispeed: a play vector that is N consecutive `JSR T` (same
    target T) terminated by RTS runs the engine N times per VBI (e.g. High_Speed
    play=$1E80 = `JSR $1003` x4 : RTS). Returns N (>=2) or 1. A leading JMP at
    the play vector is followed once. Verify-gated: a misread N yields a partial.
    """
    # base+3 is the canonical play entry. In canon it is `JMP <play-body>`
    # (the body starts with a DEC speed-counter — the loop follows the JMP and
    # returns 1). But a few members redirect base+3 into a JSR-chain/JMP-tail
    # double-play WRAPPER (Scan_Collection_end: $1003 = JMP $2000, and $2000 =
    # `JSR $1050 : JMP $1050` = the engine twice per frame) — and the wrapper
    # can also sit AT base+3 itself, JSR-first (Insinuanity/Long_Way_tune_7:
    # $1003 = `JSR $1085 : JMP $1085`, r114). So only short-circuit when
    # base+3 starts with neither JMP nor JSR; otherwise fall through and let
    # the wrapper analysis decide (returns 1 for a plain body, N for a
    # genuine repeat). Regression-safe: a plain canon body's first opcode is
    # DEC, and the r114 census over all 5401 f1 members found exactly 3 with
    # JSR-first at base+3 — the two wrapper carriers above plus one whose
    # loop-analysis still returns 1.
    if play == base + 3 and mem[play] not in (0x4C, 0x20):
        return 1
    pc = play
    target = None
    n = 0
    # Orchestral (C24 + sole carrier censused 2026-08-14): the double-play
    # wrapper opens with a per-play TEMPO-RELOAD clamp `LDA #imm /
    # STA base+$716` before the `JSR T / JMP T` pair. Step over exactly that
    # prefix — the clamp re-asserts the reload the tune record already
    # carries, so it is write-stream inert when they agree (and a member
    # where they disagree reads honestly partial; verify judges, C13).
    if (mem[pc] == 0xA9 and mem[pc + 2] == 0x8D
            and (mem[pc + 3] | (mem[pc + 4] << 8)) == base + 0x716):
        pc += 5
    for _ in range(20):
        if not (load <= pc < 0x10000 - 2):
            return 1
        op = mem[pc]
        if op == 0x20:                       # JSR abs
            t = mem[pc + 1] | (mem[pc + 2] << 8)
            if target is None:
                target = t
            elif t != target:
                return 1
            n += 1
            pc += 3
        elif op == 0x60:                     # RTS terminates the wrapper
            return n if (n >= 2 and target is not None and target >= load) else 1
        elif op == 0x4C:                     # JMP abs
            t = mem[pc + 1] | (mem[pc + 2] << 8)
            if n == 0 and target is None:    # leading indirection: follow once
                pc = t
            elif n >= 1 and t == target:     # tail-call final play (X-Static:
                return n + 1                 # JSR x3 + JMP = 4 plays)
            else:
                return 1
        else:
            return 1
    return 1


# canon-path failures that signal a re-assembled / moved layout the
# dataflow extractor can recover (the player IS a DMC v4, just relocated
# internally). Verify-gated downstream — a mislocation yields a partial.
_DATAFLOW_RETRY = {'player_code_mismatch', 'loop_site_unknown',
                   'loop_hook_unknown', 'operand_inconsistent',
                   'layout_disorder', 'nonstandard_instr_base',
                   'no_jumptable'}


def frames_clear_adsr(frames) -> bool:
    """Write-stream signature of the holding gate-off MODE. The canon player's
    sub_17EC clears AD+SR to $00 (both, same voice, same frame) at a holding
    instrument's gate-off; a mask-only variant never does. Scans a PRE-CAPTURED
    original write-log (post-init) and returns True if it EVER clears AD+SR (=>
    adsr_clear), False if never (=> mask_only candidate). CORE-TENET detection:
    don't model the (tangled) mechanism — observe what the write stream DOES.
    MUST be given a FULL-songlength capture: a holding instrument can first gate
    off late (e.g. 34-42s in Szybka_1/Ann), so a short window false-negatives
    into a regression. The caller (the verify batch) reuses its full-songlength
    orig capture, so the scan is free + reliable. Conservative: a zero-envelope
    note-init also trips True -> keeps adsr_clear, never a false mask_only."""
    pairs = ((0x05, 0x06), (0x0C, 0x0D), (0x13, 0x14))   # V1/V2/V3 (AD, SR)
    for fi, fr in enumerate(frames):
        if fi == 0:
            continue                                     # skip init clear
        wr = {}
        for _, reg, val in fr:
            wr[reg & 0xFF] = val
        for ad, sr in pairs:
            if wr.get(ad) == 0 and wr.get(sr) == 0:
                return True
    return False


def _cymbal_burst_byte(path: str):
    """The immediate operand of the cymbal noise-burst write (LDA #imm; STA
    $D400,y; STA $D401,y; LDA #imm2; STA $D404,y). Canon is ($FF, $81); a few
    demos patch either immediate — the freq for a different noise timbre
    (Presentation's $DF), the CTRL for a different attack waveform
    (Grapevine_18_intro's $02 = sync-only, r133 — the immediate-wedge class
    dmc_canon_diff documents as its blind spot). Read from the file image so
    it is layout-independent. Returns (burst, ctrl) or None if the pattern is
    absent."""
    import re
    data = open(path, 'rb').read()
    doff = int.from_bytes(data[6:8], 'big')
    m = re.search(rb'\xa9(.)\x99\x00\xd4\x99\x01\xd4\xa9(.)\x99\x04\xd4',
                  data[doff:])
    return (m.group(1)[0], m.group(2)[0]) if m else None


def _hr_patch_probe(path: str, base: int, post_init_sub: 'int | None' = None):
    """Hard-restart-patch variant probe (The_Syndrom / Tragic_Error /
    Gaston, 24 members): note-init has `JMP base+$262` at base+$257 (skips
    the PW step-base load + phase/direction reset) and the base+$25A wedge
    parks SR at base+$40 then feeds #$99 to sub_184B, whose first STA is
    retargeted at the hard-restart primer's ctrl-write OPCODE (base+$7FB,
    SMC: $99 = STA -> TEST written, $B9 = LDA -> TEST skipped; toggled per
    note-init by the instrument's $04 flag). Returns the initial toggle
    (1 iff the file-image opcode is $99) or None when not this variant."""
    mem, _ = _load(path, post_init_sub)
    b = base
    wedge = bytes((0x8D, (b + 0x40) & 0xFF, (b + 0x40) >> 8, 0xA9, 0x99))
    if (mem[b + 0x257] == 0x4C
            and mem[b + 0x258] | (mem[b + 0x259] << 8) == b + 0x262
            and bytes(mem[b + 0x25A:b + 0x25F]) == wedge
            and mem[b + 0x84B] == 0x8D
            and mem[b + 0x84C] | (mem[b + 0x84D] << 8) == b + 0x7FB):
        return 1 if mem[b + 0x7FB] == 0x99 else 0
    return None


_HOLD_BRANCH = re.compile(rb'\x29\x10\xF0\x0E\xBD..\xC9\x01\xD0\x13\xA9\xFE\x20(..)')


def _hold_gateoff_probe(path: str, base: 'int | None' = None,
                        post_init_sub: 'int | None' = None):
    """Holding gate-off variant probe (STATIC, opcode-shape — layout-blind).
    A widespread editor build (Surgeon / Imaic / Rio / Taxim / Phobos /
    Behdad_Arman, 660+ carriers) patches ONE byte in sub_17EC: $17EF BC->60,
    turning `gate mask + AD/SR=$00` into `gate mask / RTS` — i.e. the
    composer's hold_gateoff='mask_only' semantics as a 1-byte wedge (C19).
    Locate the holding branch (`AND #$10 / BEQ / LDA dur,x / CMP #$01 /
    BNE / LDA #$FE / JSR T`), follow the JSR, require the gate-mask STA
    abs,x at T, and classify the next opcode: $BC (LDY -> clear) = canon,
    $60 (RTS) = mask_only. Returns 'mask_only' or None (canon / not found).
    NB: unlike a write-stream scan this cannot false-negative on
    late-gate-off members — it reads the patched instruction itself. The
    batch's frames_clear_adsr retry stays as the fallback for members this
    shape probe misses.

    `base` scopes the search to that player's OWN code window. A multi-SID or
    compilation image holds several players, each of which can carry the wedge
    independently (C27's per-chip param class), and a whole-image first match
    silently answers for player 1 on behalf of every chip. Falls back to the
    first image-wide match when the window holds none, so a member whose
    player sits outside the assumed span keeps its previous answer."""
    mem, _ = _load(path, post_init_sub)
    cands = list(_HOLD_BRANCH.finditer(bytes(mem)))
    if base is not None:
        own = [c for c in cands if base <= c.start() < base + 0x900]
        cands = own or cands
    if not cands:
        return None
    m = cands[0]
    t = m.group(1)[0] | (m.group(1)[1] << 8)
    if mem[t] == 0x9D and mem[t + 3] == 0x60:
        return 'mask_only'
    return None


# sub_17FB hard-restart prime: `STA $D404,y / LDA #$0F / STA $D405,y /
# STA $D406,y / RTS`. First opcode admits $B9 too — the _hr_patch_probe
# variant SMC-toggles it STA<->LDA. Group(1) = the AD/SR immediate.
_HR_PRIME = re.compile(rb'[\x99\xB9]\x04\xD4\xA9(.)\x99\x05\xD4\x99\x06\xD4\x60',
                       re.DOTALL)


def _hr_preset_probe(path: str, post_init_sub: 'int | None' = None):
    """Hard-restart AD/SR immediate probe (STATIC opcode probe, C19 5th
    occurrence — Stryyker/Proportional_Text_Writer): the member patches ONE
    byte, sub_17FB's `LDA #$0F` immediate ($17FF), so the hard-restart prime
    writes AD=SR=that value on every note-fetch frame. Anchor on the
    routine's opcode shape (layout-blind); return the immediate when it
    differs from the canon $0F, else None (build unchanged)."""
    mem, _ = _load(path, post_init_sub)
    m = _HR_PRIME.search(bytes(mem))
    if m is None or m.group(1)[0] == 0x0F:
        return None
    return m.group(1)[0]


def _hr_prep_skip_probe(path: str, base: int,
                        post_init_sub: 'int | None' = None):
    """Hard-restart prep-CALL skip probe (STATIC opcode probe, C19 —
    SilverFox/Seaside_99). The note-load primes the hard restart with
    `LDA #$08 / JSR sub_17FB / LDA #$FF` at base+$1D9..base+$1DF (sub_17FB =
    base+$7FB writes TEST $08 + AD/SR $0F0F on the fetch frame). A wedge
    patches the JSR opcode $20->$2C (BIT $17FB), neutering the ENTIRE call:
    the fetch frame writes NOTHING (no TEST, no AD/SR), while pending
    (base+$74A via $11E3) is still set so the note inits normally next frame.
    Anchor on the surrounding shape both sides (LDA #$08, the sub_17FB
    operand = base+$7FB, LDA #$FF) so a non-canon layout fails open; return
    'skip' iff the opcode byte is $2C, else None (canon $20 / not this
    shape -> build unchanged)."""
    mem, _ = _load(path, post_init_sub)
    b = base
    if (mem[b + 0x1D9] == 0xA9 and mem[b + 0x1DA] == 0x08
            and mem[b + 0x1DC] | (mem[b + 0x1DD] << 8) == b + 0x7FB
            and mem[b + 0x1DE] == 0xA9 and mem[b + 0x1DF] == 0xFF
            and mem[b + 0x1DB] == 0x2C):
        return 'skip'
    return None


def _note_guard_probe(path: str, base: int,
                      post_init_sub: 'int | None' = None):
    """Post-note guard immediate probe (STATIC opcode probe, C19 —
    Rayden/NOFX_tune_2). The note-init sets the post-note guard with
    `LDA #$02 / STA $1786,x` at base+$2F8..base+$2FC; while the guard is >0 it
    is DEC'd each frame and the end-of-note gate-off logic (L_132D at
    base+$32D) is skipped, so a fresh note stays gated for 3 frames minimum.
    A wedge patches the immediate ($02 -> $00 here), so the gate drops on the
    first frame after note-init (min gate-on = imm+1 frames). Anchor on the
    surrounding canon shape (LDA# opcode + the STA-abs,x opcode + its operand =
    the guard address base+$786, reloc-aware) so a non-canon layout fails open;
    return the immediate iff it differs from the canon $02, else None (build
    unchanged)."""
    mem, _ = _load(path, post_init_sub)
    b = base
    if (mem[b + 0x2F8] == 0xA9                          # LDA #imm
            and mem[b + 0x2FA] == 0x9D                  # STA abs,x
            and (mem[b + 0x2FB] | (mem[b + 0x2FC] << 8)) == b + 0x786
            and mem[b + 0x2F9] != 0x02):
        return mem[b + 0x2F9]
    return None


def _pw_up_reverse_probe(path: str, base: int,
                         post_init_sub: 'int | None' = None):
    """Pulse UP-sweep reversal-bound repoint probe (STATIC opcode probe, C19 —
    Rygar/Complications). The canon pulse up-sweep at base+$381.. adds the step
    to the PW accumulator then reverses when pwh == bound B: `LDA $1753,x /
    ADC #$00 / STA $1753,x / CMP $1759,x` (base+$38B..base+$395). A wedge
    re-points the CMP operand from $1759,x (bound B) to $1710,x = the per-voice
    filter route-bit const ($01/$02/$04), so the up-sweep reverses when pwh ==
    the route bit instead of at bound B (a voice starting above its route bit
    ramps the full 16-bit PW range). Anchor on the surrounding canon shape (the
    pwh LDA/STA operands == base+$753, the CMP opcode) so a non-canon layout
    fails open; return 'routebit' iff the CMP operand is base+$710, else None
    (canon base+$759 or any other target -> build unchanged / honest residue)."""
    mem, _ = _load(path, post_init_sub)
    b = base
    if (mem[b + 0x38B] == 0xBD                          # LDA $1753,x (pwh)
            and (mem[b + 0x38C] | (mem[b + 0x38D] << 8)) == b + 0x753
            and mem[b + 0x390] == 0x9D                  # STA $1753,x (pwh)
            and (mem[b + 0x391] | (mem[b + 0x392] << 8)) == b + 0x753
            and mem[b + 0x393] == 0xDD                  # CMP abs,x
            and (mem[b + 0x394] | (mem[b + 0x395] << 8)) == b + 0x710):
        return 'routebit'
    return None


def _master_vol_static_probe(path: str, base: int,
                             post_init_sub: 'int | None' = None):
    """Static-$D418 probe (STATIC opcode probe, C19 — Signor/Logic_Intro). The
    canon engine writes $D418 twice: at init (master vol, `STA $D418` at
    base+$5C) and at every filter note-init (mode|vol, `STA $D418` at
    base+$2A8). This member NOPs BOTH (`EA EA EA`) and instead an appended init
    WRAPPER writes $D418 = a fixed mode|vol immediate ONCE (`LDA #imm /
    STA $D418`), so $D418 is set once at init and NEVER touched during play (a
    static filter mode + master vol for the whole tune). Anchor on both NOPs
    (specific), then read the immediate from the sole remaining `LDA #imm /
    STA $D418` in the image (both canon writes gone ⇒ the wrapper's is the only
    STA $D418). Returns the immediate, else None (build unchanged)."""
    mem, s = _load(path, post_init_sub)
    b = base
    if not (mem[b + 0x5C] == 0xEA and mem[b + 0x5D] == 0xEA and mem[b + 0x5E] == 0xEA
            and mem[b + 0x2A8] == 0xEA and mem[b + 0x2A9] == 0xEA
            and mem[b + 0x2AA] == 0xEA):
        return None
    lo, hi = s['load'], s['load'] + len(s['payload'])
    hits = [mem[i + 1] for i in range(lo, hi - 4)
            if mem[i] == 0xA9 and mem[i + 2] == 0x8D
            and mem[i + 3] == 0x18 and mem[i + 4] == 0xD4]
    return hits[0] if len(hits) == 1 else None


def _filter_static_probe(path: str, base: int,
                         post_init_sub: 'int | None' = None):
    """Static-filter probe (STATIC opcode probe, C19 — SilverFox/Blood_2_game).
    A re-assembled play routine keeps the canon filter tail's LOADS but NOPs the
    two stores: canon `LDA $171C / STA $D416 / LDA $1018 / ORA $1723 /
    STA $D417` becomes `LDA $171C / EA EA EA / LDA $1018 / ORA $1723 / EA EA EA`,
    so the filter cutoff/res are set once at init and never written during play
    (a static filter). Anchor on the whole reloc-invariant shape (cutoff
    base+$71C, shadow base+$18, res base+$723, both store slots = EA EA EA) so a
    canon member with real stores fails open; return '1' iff the NOPed pattern
    is present, else None (build unchanged)."""
    mem, _ = _load(path, post_init_sub)
    b = base
    cut, sh, res = b + 0x71C, b + 0x18, b + 0x723
    for i in range(len(mem) - 15):
        if (mem[i] == 0xAD and (mem[i + 1] | (mem[i + 2] << 8)) == cut
                and mem[i + 3] == 0xEA and mem[i + 4] == 0xEA and mem[i + 5] == 0xEA
                and mem[i + 6] == 0xAD and (mem[i + 7] | (mem[i + 8] << 8)) == sh
                and mem[i + 9] == 0x0D and (mem[i + 10] | (mem[i + 11] << 8)) == res
                and mem[i + 12] == 0xEA and mem[i + 13] == 0xEA and mem[i + 14] == 0xEA):
            return '1'
    return None


def _song_restart_gap_probe(path: str, base: int,
                            post_init_sub: 'int | None' = None):
    """Song-end REST before the repeat (ledger C38 sibling — SLC/Sidewinder's
    Crazy_Labyrinth). An appended play wrapper SMC-patches its own play JMP
    between two phases: phase 1 calls the real player and then, on one
    subtune, watches the engine's per-voice current-note bytes for a sentinel
    the composer planted in each voice's final pattern; when all three match
    it re-inits (restarting the song) and flips to phase 2, which calls the
    player NOT AT ALL for a fixed count — a silent gap — before flipping back.

    We reproduce the AUDIBLE result, not the mechanism (core tenet): the
    composer triggers off the ORDERLIST structure it already has (every voice
    has entered its final entry) and needs only the REST LENGTH, which is
    musical. So this probe returns just that length, MEASURED from
    libsidplayfp — never derived from the counter seeds, which are one
    decrement away from the truth and feed the write stream
    (feedback_ground_truth).

    STATIC GATE (cheap, runs on every member): the play vector is `JMP abs`
    into a phase target, and the wrapper's phase-2 body is the rigid
    `DEC c / BEQ / RTS ... LDA #imm / STA c / DEC c2` countdown that ends by
    re-pointing the play JMP's operand. Only when that shape is present do we
    pay for the measurement. Returns the rest length in play() calls, else
    None (no field emitted -> byte-identical build)."""
    mem, s = _load(path, post_init_sub)
    pv = s['play']
    if mem[pv] != 0x4C:
        return None
    ptr = pv + 1                       # the SMC'd JMP operand
    # phase 2 = a countdown that stores back into the play JMP's operand byte
    tgt = None
    lo, hi = s['load'], s['load'] + len(s['payload'])
    for a in range(lo, hi - 3):
        if mem[a] == 0x8D and (mem[a + 1] | (mem[a + 2] << 8)) == ptr:
            tgt = a
            break
    if tgt is None:
        return None
    try:
        import subprocess
        from src.songlengths import load_database, get_durations
        sub = post_init_sub if post_init_sub is not None else 0
        try:
            db = load_database(os.path.join('hvsc85', 'DOCUMENTS',
                                            'Songlengths.md5'))
            dur = get_durations(path, db)[sub] * 1.15 + 10.0
        except Exception:
            dur = 400.0
        from pipelines.hubbard.verify_cycle import writelog_per_irq_capture
        chunks = writelog_per_irq_capture(path, subtune=sub, duration=dur,
                                          keep_init=True)[1:]
        # The rest = a run of play() calls that emit NOTHING (the wrapper
        # skips the player entirely, so the chip is untouched) IMMEDIATELY
        # PRECEDED BY THE RESTART — i.e. the previous call carries the init's
        # ascending silence-clear sweep. Without that second condition an
        # ordinary musical silence (a subtune that simply rests for a while,
        # emitting nothing) reads as a song-end rest and the build inserts a
        # gap that is not there (measured: it regressed this member's OTHER
        # subtune from FULL). The sweep is unmistakable: >=20 writes of $00
        # walking $D400 upward in one call.
        def _is_restart(ch):
            # the sweep is an ascending RUN inside the call, not the whole
            # call: the restart play emits its normal tail first (which also
            # contains zeros) and only then the init's clear.
            zeros = [r for r, v in ((t[1], t[2]) for t in ch) if v == 0]
            run = best_run = 1 if zeros else 0
            for a, b in zip(zeros, zeros[1:]):
                run = run + 1 if b > a else 1
                best_run = max(best_run, run)
            return best_run >= 20
        best = 0
        for i, ch in enumerate(chunks):
            if ch or i == 0 or not _is_restart(chunks[i - 1]):
                continue
            n = 0
            while i + n < len(chunks) and not chunks[i + n]:
                n += 1
            best = max(best, n)
        return best if best >= 8 else None
    except Exception:
        return None


def _master_vol_fade_probe(path: str, base: int,
                           post_init_sub: 'int | None' = None):
    """Song-end master-volume fade+restart wrapper (ledger C10/C19, Slayer). An
    appended play wrapper counts play() invocations; at play N it fades the
    master vol ($1717) by 1 every STEP plays (the note-init `ora mvol` writes
    then emit the faded $D418), then writes $D418=$00 (silence) for SIL plays,
    then re-inits (JMP <init>) to restart the whole song. STATIC GATE: the fade
    decrement `DEC $101E / LDA $101E / STA $1717` + an `LDA #$00 / STA $D418`
    silence write. MEASUREMENT IS SIDDUMP-NATIVE (libsidplayfp = ground truth,
    NOT py65 — the schedule feeds the write stream, so it must come from the
    real machine per feedback_ground_truth): `--pc-watch` the fade STA $1717 PC
    gives each decrement's exact play-invocation index (N = first, STEP = the
    delta), and the writelog's longest contiguous $D418=$00 run is SIL. Returns
    "N:STEP:SIL", else None (build unchanged)."""
    mem, s = _load(path, post_init_sub)
    b = base
    load, plen = s['load'], len(s['payload'])
    lo1e, hi1e = (b + 0x1E) & 0xFF, (b + 0x1E) >> 8
    lo17, hi17 = (b + 0x717) & 0xFF, (b + 0x717) >> 8
    # static: the fade decrement `DEC $101E / LDA $101E / STA $1717` -> STA PC
    dec_pc = None
    for a in range(load, load + plen - 8):
        if (mem[a] == 0xCE and mem[a + 1] == lo1e and mem[a + 2] == hi1e
                and mem[a + 3] == 0xAD and mem[a + 4] == lo1e and mem[a + 5] == hi1e
                and mem[a + 6] == 0x8D and mem[a + 7] == lo17 and mem[a + 8] == hi17):
            dec_pc = a + 6
            break
    if dec_pc is None:
        return None
    if not any(mem[a] == 0xA9 and mem[a + 1] == 0x00 and mem[a + 2] == 0x8D
               and mem[a + 3] == 0x18 and mem[a + 4] == 0xD4
               for a in range(load, load + plen - 4)):
        return None
    try:
        import subprocess
        from src.songlengths import load_database, get_durations
        from pipelines.hubbard.verify_cycle import writelog_capture
        sub = post_init_sub if post_init_sub is not None else 0
        try:
            db = load_database(os.path.join('hvsc85', 'DOCUMENTS', 'Songlengths.md5'))
            dur = get_durations(path, db)[sub] * 1.15 + 5.0
        except Exception:
            dur = 400.0
        out = subprocess.run(
            ['siddump', path, '--subtune', str(sub + 1), '--duration', f'{dur:.0f}',
             '--pc-watch', f'{dec_pc:04X}', '0-0'],
            capture_output=True, text=True).stdout
        idxs = []
        for line in out.splitlines():
            for tok in line.split('|'):
                if tok.startswith('PW:'):
                    p = tok.split(':')
                    if len(p) > 5:
                        idxs.append(int(p[5]))
        if len(idxs) < 2:
            return None
        n_fade, step = idxs[0], idxs[1] - idxs[0]
        # SIL = the longest contiguous run of $D418=$00 writes (the silence
        # phase writes it once per play, and it is the only $00 run: init/normal
        # $D418 is $0F/$1F, the fade values are $1E..$11).
        best = cur = 0
        for fr in writelog_capture(path, subtune=sub, duration=dur):
            for (_c, reg, val) in fr:
                if reg == 24:
                    cur = cur + 1 if val == 0 else 0
                    best = max(best, cur)
        if best < 1 or n_fade < 1 or step < 1:
            return None
        # Restart note-state: the canon init leaves $100F-$1018 (gatemask,
        # curnote, instr, shadow17) UNCLEARED, so the replay resumes them from
        # the last-song values. Measure them from libsidplayfp during the
        # silence (frozen there, no play body): memwatch $100F-$1018 on every
        # $D418 write, take the mode over the $D418=$00 (silence) snapshots.
        addrs = [b + off for off in range(0x0F, 0x19)]
        mw = subprocess.run(
            ['siddump', path, '--subtune', str(sub + 1), '--duration', f'{dur:.0f}',
             '--memwatch-on-write', 'd418',
             ','.join(f'{a:04X}' for a in addrs)],
            capture_output=True, text=True).stdout
        from collections import Counter
        tag = f'{b + 0x18:04X}'
        counts: 'Counter[str]' = Counter()
        for line in mw.splitlines():
            for ev in line.split('|')[1:]:
                kv = dict(p.split('=') for p in ev.split(':') if '=' in p)
                if kv.get('d418'.upper()) == '00' or kv.get('D418') == '00':
                    ns = ','.join(str(int(kv[f'{a:04X}'], 16)) for a in addrs
                                  if f'{a:04X}' in kv)
                    if ns.count(',') == 9:
                        counts[ns] += 1
        if not counts:
            return None
        note_state = counts.most_common(1)[0][0]
        return f"{n_fade}:{step}:{best}:{note_state}"
    except Exception:
        return None


_PW_HI_WRITE = re.compile(rb'\xBD(..)\x99\x02\xD4\xBD(..)\x99\x03\xD4',
                          re.DOTALL)


def _pw_hi_const_probe(path: str, base: int,
                       post_init_sub: 'int | None' = None):
    """PW-hi source patch probe (STATIC opcode probe, C19 — Olsen/Lame, the
    only family-1 carrier): the sidwrite tail is canonically
    `LDA $1750,x / STA $D402,y / LDA $1753,x / STA $D403,y`; the wedge
    re-points the second LDA's operand at another per-voice byte (Lame:
    base+$707 = the track-ptr lo triple, set once at init — so each voice's
    audible PW hi is pinned at a per-voice constant while the internal PWM
    state machine still runs on $1753). Anchor on the $D402/$D403 stores +
    the canon PW-accum-lo operand (base+$750, layout-blind wrt relocation);
    if the hi operand differs from canon, capture the POST-INIT runtime
    bytes at operand..+2 (init rewrites them; file image is the fallback)
    and return them as 'a,b,c'. Canon operand -> None (build unchanged)."""
    mem, s = _load(path, post_init_sub)
    m = _PW_HI_WRITE.search(bytes(mem))
    if not m:
        return None
    oplo = m.group(1)[0] | (m.group(1)[1] << 8)
    ophi = m.group(2)[0] | (m.group(2)[1] << 8)
    if oplo != base + 0x750 or ophi == base + 0x753:
        return None
    ram = _post_init_ram(path, s['start'] - 1)
    src = ram if ram is not None else mem
    return ','.join(str(src[ophi + i]) for i in range(3))


def _pw_dir_persist_probe(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """PW-direction reset redirect (STATIC opcode probe, C19). The note-init
    pulse reset canonically ends `LDA #$00 / STA $1762,x (phase) / STA $1765,x
    (direction=up)`; the wedge re-points the second STA at an unused state
    byte (Artlace: $17AB, in the $179E-$17AF gap), so the sweep DIRECTION
    persists across note-inits while value/bounds/step/phase still reset.
    Anchor on `A9 00 9D <base+$762> 9D <op>` (relocation-aware: the state page
    rides on base). Positive minority signature: return 1 iff exactly one
    site matches and its second operand != base+$765; canon or ambiguous ->
    None (build unchanged). Carrier: Artlace/End_of_1992_intro."""
    mem, _ = _load(path, post_init_sub)
    a = base + 0x762
    # re.escape the operand bytes: a relocated address low byte can be a regex
    # metacharacter (e.g. '[' = $5B) that breaks compile / matches loosely.
    pat = re.compile(
        rb'\xA9\x00\x9D' + re.escape(bytes([a & 0xFF, (a >> 8) & 0xFF]))
        + rb'\x9D(..)',
        re.DOTALL)
    ms = pat.findall(bytes(mem))
    if len(ms) != 1:
        return None
    op = ms[0][0] | (ms[0][1] << 8)
    return 1 if op != base + 0x765 else None


def _switch_toggle_mask_probe(path: str, base: int, gatemask_addr: int,
                              post_init_sub: 'int | None' = None):
    """SWITCH ($7D tie/legato) gate-mask toggle immediate (STATIC opcode probe,
    C19). The switch handler at base+$183 canonically toggles ONLY the gate bit:
    `LDA gatemask,x / EOR #$01 / STA gatemask,x` (base+$189..$18E), so a SWITCH
    flips the mask $FF<->$FE (gate as the wave table says <-> force gate off).
    A wedge patches the EOR immediate (Bax/Feed_a_Bird: $01->$1F), so the switch
    instead toggles gate+test+ring+sync+triangle ($FF<->$E0) — cutting a
    triangle/ring/sync note to silence ($17 & $E0 = $00) where the canon merely
    releases the gate ($17 & $FE = $16). Anchor on the handler shape both sides
    (the LDA/STA operands = gatemask_addr, reloc-aware) and return the immediate
    iff it differs from the canon $01, else None (build unchanged).

    Regression-safe by construction: the composer applies the probed mask
    verbatim, so its $D404 write can only match the orig MORE often (never less)
    than the hardcoded $01 — and $E0 vs $FE coincide for noise/pulse/saw notes
    (only bits 5-7 survive either), so the value only matters on notes that
    carry sync/ring/test/triangle. Census over 5833 f1: 1 carrier (Feed_a_Bird),
    5502 canon $01 -> 0 FULL exposure."""
    if gatemask_addr is None:
        return None
    mem, _ = _load(path, post_init_sub)
    gm = bytes([gatemask_addr & 0xFF, (gatemask_addr >> 8) & 0xFF])
    b = base
    if (mem[b + 0x189] == 0xBD and bytes(mem[b + 0x18A:b + 0x18C]) == gm
            and mem[b + 0x18C] == 0x49
            and mem[b + 0x18E] == 0x9D
            and bytes(mem[b + 0x18F:b + 0x191]) == gm
            and mem[b + 0x18D] != 0x01):
        return mem[b + 0x18D]
    return None


def _forced_subtune_probe(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """Hand-crafted init WRAPPER `LDA #imm` that HARD-FORCES the played tune
    record, overriding the PSID subtune arg (STATIC opcode probe, C19).

    Sans_intro: init $0FFE = `A9 01` (LDA #$01) falling through to base $1000
    (`4C 1D 10` = JMP $101D = the tune-select dispatch, which does `A*8 -> Y`),
    so EVERY play forces record 1 no matter the PSID song number — but the
    extract walks record 0, a dummy record whose V1/V2 tracks are `$FE` (stop),
    dropping the whole tune. Return the forced record index so the extract
    walks the PLAYED record. None = no such prefix (canon init == base).

    Regression-safe by construction: imm==0 reproduces the default record-0
    walk (byte-identical) so a false match on it is a no-op; the guard that
    `base` itself is the standard `JMP base+$1D` dispatch AND the `LDA #imm`
    reaches it (fall-through, or a `JMP base`) rejects banking / other
    LDA#-leading wrappers whose immediate is not a subtune index. Census over
    5833 f1 members: exactly 2 carriers, both imm=1 and both previously partial
    — Sans_intro (fall-through form) + Devilock/Sub_Effect (JMP-to-base form).
    3rd form (2026-07-30, Odysseus/Hear_Circa_2_Minutes, imm=3): the forcing
    LDA sits deeper in a longer wrapper and reaches init via `JSR base`
    (wrapper continues with CIA latch programming after); family census of the
    JSR shape: 1 behavior-changing carrier + 8 imm=0 no-ops."""
    mem, s = _load(path, post_init_sub)
    init = s['init']
    if init == base or not (0 <= init and init + 4 <= 0xFFFF):
        return None
    if mem[base] != 0x4C:                          # base must be a JMP dispatch
        return None
    canon = (mem[base + 1] | (mem[base + 2] << 8)) == (base + 0x1D) & 0xFFFF
    if not canon:
        # RE-ASSEMBLED base -> JMP elsewhere (Fatamorcana_intro: $1000 -> JMP
        # $1807, and the wrapper interposes reg-transfers a fixed shape can't
        # parse: init $1E52 = `LDA #$03 / TAX / TAY / JMP $1000`). The static
        # forms below trust the canon base+$1D dispatch is record-indexed; here
        # OBSERVE instead (C18): run the real init(A=sub) under py65 and read A
        # at base. Gate on an `LDA #imm` at the vector (a forcing candidate) so
        # py65 stays off non-forcing wrappers. Fire iff the observed A is UNIFORM
        # AND NON-IDENTITY (a forced record). REGRESSION-SAFE by construction: a
        # member FULL walking record 0 has A==sub (identity) at base -> the
        # observation returns list(range(songs)) -> no fire; verify-gated
        # besides. Census the newly-firing set before landing (see project_dmc).
        if mem[init] != 0xA9:
            return None
        seen = _init_song_observe(path, base, s.get('songs', 1))
        if seen and len(set(seen)) == 1 and seen != list(range(len(seen))):
            forced = seen[0]
            # CONFIRM the init body actually USES A (else it's a wrapper whose
            # LDA#imm is not a record index / an init that ignores A -> forcing
            # would regress a member that plays record 0 regardless).
            if _init_forced_changes_state(path, base, forced):
                return forced
        return None
    if mem[init] == 0xA9:                          # LDA #imm at the vector
        nxt = init + 2                             # LDA #imm must REACH base
        if (nxt == base or
                (mem[nxt] == 0x4C and
                 (mem[nxt + 1] | (mem[nxt + 2] << 8)) == base)):
            return mem[init + 1]
    # 3rd form (Hear_Circa_2_Minutes): the forcing LDA sits DEEPER in the
    # wrapper and reaches init via `JSR base` (`A9 imm 20 <base>`), with the
    # wrapper continuing after (CIA latch programming). The exact 16-bit JSR
    # target adjacent to an LDA# is the static anchor; scan only the wrapper
    # window before/around the vector's page so a data byte can't pattern-match.
    # ⚠ The static match alone is NOT sufficient: the LDA can sit under a
    # CONDITION (Bomberman_preview: `CMP #$00 / BNE / LDA #$05 / JSR base`
    # remaps ONLY subtune 0 to song 5) — a byte scan cannot see the branch.
    # Cross-check by OBSERVATION (C18): run init(A=sub) under py65 per header
    # subtune and require the A entering `base` to equal the immediate for
    # EVERY subtune; a conditional wrapper fails the check and stays refused.
    end = min(init + 0x30, base if base > init else init + 0x30, 0xFFFC)
    for a in range(init, end):
        if (mem[a] == 0xA9 and mem[a + 2] == 0x20 and
                (mem[a + 3] | (mem[a + 4] << 8)) == base):
            imm = mem[a + 1]
            seen = _init_song_observe(path, base, s.get('songs', 1))
            if seen is not None and all(v == imm for v in seen):
                return imm
            return None
    return None


def _subtune_song_map_probe(path: str, base: int,
                            post_init_sub: 'int | None' = None):
    """PER-SUBTUNE song remap by an init wrapper (the CONDITIONAL sibling of
    _forced_subtune_probe, ledger C31/C19). A uniform forced_subtune sends
    EVERY play onto one record; a wrapper can instead remap only SOME subtunes
    to a different tune record — Bomberman_preview's `STA c / LDA c / CMP #$00 /
    BNE / LDA #$05 / JSR base` sends ONLY subtune 0 to song 5 (subtunes 1-3
    pass straight through), a map [5, 1, 2, 3] the uniform probe can't express.
    The extract otherwise walks record 0 (subtune 0's REAL data is at record 5),
    so its V2/V3 tracks read as `$FE` stops -> the whole tune 0 mis-decodes.

    OBSERVE (C18): the map is under a branch a byte scan can't see, so run the
    FILE's init(A=sub) per header subtune and read the A entering `base` (pure
    init, py65-trustworthy). Return the map iff it is NON-IDENTITY (else the
    default walk) and NON-UNIFORM (else forced_subtune owns it). A static anchor
    gate (an `LDA #imm / JSR base` or fall-through/JMP form in the wrapper, as
    forced_subtune's) keeps the py65 observation off the canonical-init hot path.
    Regression-safe: identity/uniform/no-wrapper -> None -> byte-identical."""
    mem, s = _load(path, post_init_sub)
    init = s['init']
    songs = s.get('songs', 1)
    if init == base or songs < 2 or not (0 <= init and init + 4 <= 0xFFFF):
        return None
    # base must be a tune-select dispatch — canon `JMP base+$1D` or the
    # family-2 form `JMP base+$37` (both inits are record-indexed via the
    # tunetab; the f2 body just sits at a different offset). The canon-only
    # guard blinded EVERY per-subtune wrapper probe to family-2
    # (Fuckin_Birds/NemTP's conditional song-0 remap, found 2026-08-13).
    if not (mem[base] == 0x4C and
            (mem[base + 1] | (mem[base + 2] << 8)) in
            ((base + 0x1D) & 0xFFFF, (base + 0x37) & 0xFFFF)):
        return None
    # STATIC anchor gate (perf): an `LDA #imm` reaching base (fall-through /
    # JMP base) OR an `LDA #imm / JSR base` in the wrapper window, OR an
    # `LDA #imm` followed within 10 bytes by `JMP base` (the Arthur wrapper
    # interposes two STx stores between the force and the jump). Only then
    # pay for the per-subtune py65 observation.
    anchor = mem[init] == 0xA9 and (
        init + 2 == base or
        (mem[init + 2] == 0x4C and
         (mem[init + 3] | (mem[init + 4] << 8)) == base))
    if not anchor:
        end = min(init + 0x30, base if base > init else init + 0x30, 0xFFFC)
        for a in range(init, end):
            if (mem[a] == 0xA9 and mem[a + 2] == 0x20 and
                    (mem[a + 3] | (mem[a + 4] << 8)) == base):
                anchor = True
                break
            if mem[a] == 0xA9:
                for j in range(a + 2, min(a + 12, end)):
                    if (mem[j] == 0x4C and
                            (mem[j + 1] | (mem[j + 2] << 8)) == base):
                        anchor = True
                        break
            if anchor:
                break
                break
    if not anchor:
        return None
    seen = _init_song_observe(path, base, songs)
    if seen is None or seen == list(range(songs)) or len(set(seen)) == 1:
        return None
    return seen


def _smc_jsr_table_refine(path: str, base: int, observed: str,
                          post_init_sub: 'int | None' = None):
    """Refine an OBSERVED play-phase schedule against the statically-decoded
    SMC-JSR-TABLE wrapper (C18's first listed idiom; Hexzakk r141).

    The wrapper shape: `INC c / LDA c / CMP #N / BNE +5 / LDA #0 / STA c /
    LDX c / LDA tab,X / STA <jsr-operand-lo> / JSR base+t / RTS` — the
    N-entry table holds jump-table LO bytes, so the true per-call TARGET
    sequence is static ground truth. The pc-trace observer classifies each
    call's ROLE (P/F/R) from chip-state heuristics and can misclassify a
    single call (Hexzakk: one of four F123 calls read as R123 — an R never
    advances the wave program, so a multi-step wave drifted a step behind,
    invisible until the program's next value change). The refiner keeps the
    observer's ROLE vocabulary but forces every call that JSRs the SAME
    table target to the SAME token (majority vote within the group) — the
    engine runs one routine per target, so per-call divergence within a
    group is observation noise by construction.

    Returns the refined schedule string, or None when the wrapper doesn't
    match / lengths disagree (keep the observation)."""
    mem, s = _load(path, post_init_sub)
    play = s['play']
    if play == base + 3 or play + 26 > 0xFFFF:
        return None
    def op16(a):
        return mem[a] | (mem[a + 1] << 8)
    if not (mem[play] == 0xEE and mem[play + 3] == 0xAD and
            op16(play + 1) == op16(play + 4) and
            mem[play + 6] == 0xC9 and mem[play + 8] == 0xD0 and
            mem[play + 10] == 0xA9 and mem[play + 11] == 0x00 and
            mem[play + 12] == 0x8D and op16(play + 13) == op16(play + 1) and
            mem[play + 15] == 0xAE and op16(play + 16) == op16(play + 1) and
            mem[play + 18] == 0xBD and
            mem[play + 21] == 0x8D and mem[play + 24] == 0x20):
        return None
    n = mem[play + 7]
    if not 2 <= n <= 16:
        return None
    if op16(play + 22) != play + 25:      # STA must patch the JSR operand lo
        return None
    if mem[play + 26] != (base >> 8):     # JSR hi byte = the player page
        return None
    tab = op16(play + 19)
    ctr = op16(play + 1)
    targets = [mem[tab + i] for i in range(n)]
    # counter seed: init wrapper `LDA #ss / STA ctr`, else the file byte
    seed = mem[ctr]
    init = s['init']
    for a in range(init, min(init + 0x30, 0xFFFB)):
        if mem[a] == 0xA9 and mem[a + 2] == 0x8D and op16(a + 3) == ctr:
            seed = mem[a + 1]
            break
    obs = [t for t in observed.split('_') if t]
    if len(obs) != n:
        return None
    # per-call table index: INC first, reset at N
    call_idx = [(seed + 1 + k) % n for k in range(n)]
    groups = {}
    for k, ti in enumerate(call_idx):
        groups.setdefault(targets[ti], []).append(k)
    out = list(obs)
    for tgt, calls in groups.items():
        toks = [obs[k] for k in calls]
        best = max(set(toks), key=toks.count)
        if tgt == 0x03 and best != 'P' and best != 'P2':
            return None                   # base+3 must be the full play
        for k in calls:
            out[k] = best
    refined = '_'.join(out)
    return refined if refined != observed else None


def _wavestep_arm_refine(path: str, base: int, observed: str,
                         post_init_sub: 'int | None' = None):
    """Refine an OBSERVED schedule whose wrapper calls the canon WAVESTEP
    entry directly (r143, Mathematika_II): the play wrapper dispatches
    `LDX #v / JMP base+$591` — the $1591 arm entry, an ADVANCING wave step.
    A voice that IDLES during the observation window makes that call look
    like a register refresh, so the pc-trace observer emits an R token —
    but an R never advances the wave program, and a multi-step (drum)
    program then lags one step per cycle behind the orig, invisible until
    the program's next value change. STATIC truth: scan the wrapper window
    for `A2 vv 4C <base+$591>`; when found and the observed schedule
    carries an R token for exactly those voices, flip it to F and return
    (schedule, noteinit_deferred='1') — the F-as-wavestep-arm mode
    (voice_fx = wavestep) is the literal orig call. None = no match."""
    mem, s = _load(path, post_init_sub)
    play = s['play']
    # the wrapper can BE the play vector, or the jump table's play entry can
    # be re-pointed at it (Mathematika_II: $1003 `JMP $2528`) — follow one JMP
    if mem[play] == 0x4C:
        play = mem[play + 1] | (mem[play + 2] << 8)
    tgt = (base + 0x591) & 0xFFFF
    voices = set()
    for a in range(play, min(play + 0x40, 0xFFFA)):
        if (mem[a] == 0xA2 and mem[a + 2] == 0x4C and
                (mem[a + 3] | (mem[a + 4] << 8)) == tgt and mem[a + 1] < 3):
            voices.add(mem[a + 1] + 1)
    if not voices:
        return None
    want = ''.join(str(v) for v in sorted(voices))
    toks = [t for t in observed.split('_') if t]
    hit = False
    for i, t in enumerate(toks):
        if t == 'R' + want:
            toks[i] = 'F' + want
            hit = True
    if not hit:
        return None
    return '_'.join(toks)


def _fphase_effect_repeat(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """Decode a C18 F-phase that runs the per-voice wave-step with REPEATS
    (PVCF 'massive multispeed' — Sound_Test, STIL: 'an 11-speeder, sounds like
    samples'). The play-vector wrapper's effects branch is `JSR SUB xk`
    (SUB != base+3, so it is not a whole-play repeat), and SUB is
    `(LDX #v / JSR FX xm)...` with FX a SINGLE wave-step routine — so voice v's
    wave program advances m*k steps per effects-call (the massive multispeed).
    Returns the repeat spec 'k:VxC,VxC' (1-based voice; e.g. Sound_Test's
    `JSR $1006 x5`, `$1006 = LDX#0/JSR $15A2 / LDX#2/JSR $15A2 x5` -> '5:1x1,3x5'),
    or None when the wrapper is not this nested-repeat shape (the default:
    each F voice once, byte-identical). Static (C24/C18 JSR-count method)."""
    mem, s = _load(path, post_init_sub)
    play = s['play']
    if mem[play] == 0x4C:                       # play vector may JMP to wrapper
        play = mem[play + 1] | (mem[play + 2] << 8)
    # outer: the first run of >=2 consecutive identical `JSR SUB` (SUB != base+3)
    sub = outer = None
    for a in range(play, min(play + 0x40, 0xFFFA)):
        if mem[a] != 0x20:
            continue
        t = mem[a + 1] | (mem[a + 2] << 8)
        run, q = 1, a + 3
        while q + 2 < 0x10000 and mem[q] == 0x20 and \
                (mem[q + 1] | (mem[q + 2] << 8)) == t:
            run += 1
            q += 3
        if run >= 2 and t != (base + 3) & 0xFFFF:
            sub, outer = t, run
            break
    if sub is None:
        return None
    # inner: SUB = (LDX #v / JSR FX xm)...  FX must be a single routine
    inner, fx, v, a = [], None, None, sub
    for _ in range(24):
        op = mem[a]
        if op == 0xA2:                          # LDX #v (voice select)
            v = mem[a + 1]
            a += 2
        elif op == 0x20:                        # JSR FX (count the run)
            t = mem[a + 1] | (mem[a + 2] << 8)
            if fx is None:
                fx = t
            if t != fx or v is None or v > 2:
                return None
            run, q = 1, a + 3
            while mem[q] == 0x20 and (mem[q + 1] | (mem[q + 2] << 8)) == t:
                run += 1
                q += 3
            inner.append((v + 1, run))
            v, a = None, q
        elif op == 0x60:                        # RTS = end of SUB
            break
        else:
            return None
    if not inner or fx is None or fx == (base + 3) & 0xFFFF:
        return None
    return f'{outer}:' + ','.join(f'{vv}x{cc}' for vv, cc in inner)


def _playclk_probe(path: str, base: int,
                   post_init_sub: 'int | None' = None):
    """PLAY-CLOCK-IN-SONG-DATA wrapper (C19 'Ed'-animator family, Dresden):
    the appended play vector is `INC addr / LDA addr / AND #$01 / CMP #$01 /
    BEQ fx / JMP base+3`, where `addr` is a byte INSIDE A PLAYED SECTOR —
    the wrapper's phase parity counter doubles as pattern content (a glide
    row reads the live counter as its start note = a pitch that rises one
    step per play tick). STATIC anchored probe: the exact INC/LDA operand
    pair at the play vector + the init wrapper seeding the SAME address
    (`LDX #$FF / STX addr` or LDA/STA form). Returns the addr (int) or
    None; non-carriers are untouched (the probe fires on nothing else —
    an ordinary phase wrapper keeps its counter OUTSIDE the data, and the
    walk flags only rows whose source byte sits AT the addr anyway)."""
    mem, s = _load(path, post_init_sub)
    play, init = s['play'], s['init']
    if play == base + 3 or play + 8 > 0xFFFF:
        return None
    if not (mem[play] == 0xEE and mem[play + 3] == 0xAD):
        return None
    addr = mem[play + 1] | (mem[play + 2] << 8)
    if (mem[play + 4] | (mem[play + 5] << 8)) != addr:
        return None
    if not (mem[play + 6] == 0x29 and mem[play + 7] == 0x01):
        return None
    # init wrapper must seed the same byte to $FF (LDX #$FF/STX or LDA/STA)
    end = min(init + 0x30, 0xFFFB)
    for a in range(init, end):
        if (mem[a] in (0xA2, 0xA9) and mem[a + 1] == 0xFF and
                mem[a + 2] in (0x8E, 0x8D) and
                (mem[a + 3] | (mem[a + 4] << 8)) == addr):
            return addr
    return None


def _init_song_observe(path: str, base: int, songs: int):
    """Run the FILE's init(A=sub) under py65 for each header subtune and
    return the list of A values at the FIRST entry into `base` (the song
    the real init actually receives), or None if any run fails to reach
    base / return. py65 is trustworthy here — pure init, no playback."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                     '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from seed_disassembly import parse_psid
    spec = parse_psid(path)
    out = []
    for sub in range(max(songs, 1)):
        mpu = MPU()
        m = bytearray(0x10000)
        for i, b in enumerate(spec['payload']):
            if spec['load'] + i < 0x10000:
                m[spec['load'] + i] = b
        mpu.memory = m
        mpu.stPush(0x00)
        mpu.stPush(0x00)                    # RTS sentinel -> PC = $0001
        mpu.pc = spec['init']
        mpu.a = sub
        mpu.x = mpu.y = 0
        a_at_base = None
        for _ in range(3_000_000):
            if mpu.pc == base and a_at_base is None:
                a_at_base = mpu.a
            if mpu.pc == 0x0001:
                break
            try:
                mpu.step()
            except Exception:
                return None
        else:
            return None
        if a_at_base is None:
            return None
        out.append(a_at_base)
    return out


def _init_forced_changes_state(path: str, base: int, forced: int) -> bool:
    """Run the init BODY (entering at `base`, BYPASSING the forcing wrapper) to
    COMPLETION twice — A=0 and A=forced — and report whether the two post-init
    RAM images DIFFER. The forced-subtune observation (`A == forced` reaches
    base) is only meaningful if the init actually USES A to pick the tune
    record: a member whose init IGNORES A plays record 0 no matter what, so
    forcing `forced` would be a false positive that regresses it. Entering at
    `base` (not the wrapper, which overrides A) with A=0 vs A=forced makes the
    track pointers (and downstream state) differ iff A selects the record.
    py65 is trustworthy here (pure init, no divergent-memory playback)."""
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                     '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from seed_disassembly import parse_psid
    spec = parse_psid(path)

    def _run(sub):
        mpu = MPU()
        m = bytearray(0x10000)
        for i, b in enumerate(spec['payload']):
            if spec['load'] + i < 0x10000:
                m[spec['load'] + i] = b
        mpu.memory = m
        mpu.stPush(0x00)
        mpu.stPush(0x00)                    # RTS sentinel -> PC = $0001
        mpu.pc = base                       # enter the init BODY, not the wrapper
        mpu.a = sub
        mpu.x = mpu.y = 0
        for _ in range(3_000_000):
            if mpu.pc == 0x0001:
                break
            try:
                mpu.step()
            except Exception:
                return None
        else:
            return None
        return bytes(mpu.memory)

    a0 = _run(0)
    af = _run(forced)
    if a0 is None or af is None:
        return False
    # compare the player + data image (skip zero page / stack / IO)
    return a0[0x0400:0x8000] != af[0x0400:0x8000]


def _medley_switch_probe(path: str, base: int,
                         post_init_sub: 'int | None' = None):
    """PER-SUBTUNE TIME-MEDLEY SWITCH (C31 medley variant, per-subtune form —
    Arthur/Fuckin_Birds + NemTP): the play vector is a countdown wrapper
    `LDA v0 / ORA v1 / BEQ play / DEC v1 / BNE play / DEC v0 / BNE play /
    LDA #target / JMP base(init)`, and the INIT wrapper arms (v0,v1) only
    for specific subtunes (Arthur: sub 2 = song 0 for $03FF plays, then
    re-init into song 1 forever; unarmed subtunes play plain). The armed
    values are OBSERVED per subtune from post-init RAM (py65-trustworthy:
    written by the init wrapper itself), never parsed from the branch chain
    (C18/C31). Returns 'sub:target:lo:hi[;...]' or None."""
    mem, s = _load(path, post_init_sub)
    p = s['play']
    if not (0 < p < 0xFFE0):
        return None
    # the exact countdown shape (offsets fixed; operands = the two counters)
    if not (mem[p] == 0xAD and mem[p + 3] == 0x0D and mem[p + 6] == 0xF0
            and mem[p + 8] == 0xCE and mem[p + 11] == 0xD0
            and mem[p + 13] == 0xCE and mem[p + 16] == 0xD0
            and mem[p + 18] == 0xA9 and mem[p + 20] == 0x4C
            and _rd16(mem, p + 21) == base):
        return None
    v0 = _rd16(mem, p + 1)
    v1 = _rd16(mem, p + 4)
    if {v0, v1} != {_rd16(mem, p + 14), _rd16(mem, p + 9)}:
        return None                       # DECs must hit the same two counters
    target = mem[p + 19]
    segs = []
    for sub in range(s.get('songs', 1)):
        ram = _post_init_ram(path, sub)
        if ram is None:
            return None
        hi, lo = ram[v0], ram[v1]
        if hi or lo:
            segs.append(f'{sub}:{target}:{lo:X}:{hi:X}')
    return ';'.join(segs) or None


def _state_resume_probe(path: str, base: int,
                        post_init_sub: 'int | None' = None):
    """Subtune SAVE-STATE RESUME wrapper (ledger C37, STATIC anchored probe).

    The init vector is an appended wrapper: `JSR copy / JMP real-init`,
    where `copy` is an SMC loop (`TAX / LDA srclo_tab,X / STA <src-operand>`
    then per pair: dest lo/hi from a pair table -> the STA operand, one
    data byte from the per-subtune source block -> that dest, INC src-lo)
    ending `LDA #imm / RTS` — so the real init always receives song `imm`
    and every header "subtune" is the same song resumed from a pasted
    state snapshot. Decode statically, anchored on the exact opcode
    skeleton (a shape mismatch returns None — never guess).

    Returns (forced_song, {subtune: {addr: byte}}) with the copy filtered
    to its init-wipe SURVIVORS (the copy runs BEFORE init, so anything in
    the base+$718..base+$79D wipe is dead cargo), or None. The source
    address INCs only its LO byte, so the per-byte address wraps within
    the page (ledger C11 — mirror the register width).

    Regression-safe: the probe fires only on the full skeleton match
    (census 2026-07-28: exactly 2 carriers in HVSC, Rio's two Calf_Love
    members); a non-carrier's cfg is untouched."""
    mem, s = _load(path, post_init_sub)
    init = s['init']
    tgt = init
    if mem[init] == 0x4C:
        tgt = mem[init + 1] | mem[init + 2] << 8
    if mem[tgt] != 0x20 or mem[(tgt + 3) & 0xFFFF] != 0x4C:
        return None
    sub = mem[tgt + 1] | mem[tgt + 2] << 8

    def op16(a):
        return mem[a] | mem[a + 1] << 8
    ops = [(0, 0xAA), (1, 0xBD), (4, 0x8D), (7, 0xA0), (9, 0xB9),
           (12, 0x8D), (15, 0xC8), (16, 0xB9), (19, 0x8D), (22, 0xC8),
           (23, 0xAD), (26, 0x8D), (29, 0xEE), (32, 0xC0), (34, 0xD0),
           (36, 0xA9), (38, 0x60)]
    if any(mem[(sub + o) & 0xFFFF] != op for o, op in ops):
        return None
    # SMC wiring: the STA at +4 and INC at +29 must target the LDA-src lo
    # operand (+24); the two dest-operand stores must target the STA-dst
    # operand lo/hi (+27/+28); both pair-table reads share one table.
    if op16(sub + 5) != sub + 24 or op16(sub + 30) != sub + 24:
        return None
    if op16(sub + 13) != sub + 27 or op16(sub + 20) != sub + 28:
        return None
    dtab = op16(sub + 10)
    if op16(sub + 17) != dtab:
        return None
    cnt = mem[sub + 33]
    if cnt == 0 or cnt & 1:
        return None
    n = cnt // 2
    src_hi = mem[sub + 25]
    stab = op16(sub + 2)
    dests = [op16(dtab + 2 * k) for k in range(n)]
    forced = mem[sub + 37]
    wipe_lo, wipe_hi = base + 0x718, base + 0x79D
    out = {}
    for song_i in range(s.get('songs', 1)):
        lo = mem[stab + song_i]
        out[song_i] = {
            d: mem[(src_hi << 8) | ((lo + k) & 0xFF)]
            for k, d in enumerate(dests) if not wipe_lo <= d <= wipe_hi}
    return forced, out


def _state_resume_observe(path: str, base: int,
                          post_init_sub: 'int | None' = None,
                          max_diff: int = 256):
    """C37 save-state resume wrapper, detected by OBSERVATION (the ledger's
    own canonical rule — C18/C31: don't keep teaching a static wrapper
    parser new shapes). Fallback when `_state_resume_probe`'s skeleton
    doesn't match (2nd shape, Cafe_Odd: `JMP copy` form, single src-lo
    table + dest lo/hi tables, `LDA #$00` before `JMP base`).

    Run the FILE's init(A=sub) under py65 per header subtune, recording A
    at the FIRST entry into `base` (py65's PC is exact — no C36 bus-tap
    ambiguity). If EVERY subtune enters the player with the SAME song A
    (a forced song) and ≥1 non-start subtune's post-init RAM differs from
    the start subtune's, it is a resume wrapper: the diffs ARE the
    init-wipe survivors (the wipe zeroes identically across subs, so
    wiped copy bytes cancel out of the diff automatically). py65 is
    trustworthy here — every surviving byte is file-loaded or
    init-written (no deep playback).

    Returns (forced_song, {subtune: {addr: byte}}) or None. Survivors
    exclude I/O ($D000-$DFFF); a sub with > max_diff differing bytes
    refuses (that scale suggests a per-subtune unpacker, C26 — not a
    state paste; the member stays partial rather than mis-modeled).
    LIMIT: survivors are measured relative to the START subtune, so a
    start-subtune poke that differs from the file image is invisible —
    such a carrier would present as sub-0 partial and needs the static
    probe (or a baseline-vs-image extension)."""
    mem0, s = _load(path, post_init_sub)
    init = s['init']
    songs = s.get('songs', 1)
    if songs < 2 or init == base:
        return None
    import sys as _sys
    _sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                     '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from seed_disassembly import parse_psid
    spec = parse_psid(path)

    def run(sub):
        mpu = MPU()
        m = bytearray(0x10000)
        for i, b in enumerate(spec['payload']):
            if spec['load'] + i < 0x10000:
                m[spec['load'] + i] = b
        mpu.memory = m
        mpu.stPush(0x00)
        mpu.stPush(0x00)                    # RTS sentinel -> PC = $0001
        mpu.pc = spec['init']
        mpu.a = sub
        mpu.x = mpu.y = 0
        a_at_base = None
        for _ in range(3_000_000):
            if mpu.pc == base and a_at_base is None:
                a_at_base = mpu.a
            if mpu.pc == 0x0001:
                return a_at_base, m
            try:
                mpu.step()
            except Exception:
                return None, None
        return None, None

    a0, post0 = run(0)
    if a0 is None:
        return None
    out = {0: {}}
    any_diff = False
    for k in range(1, songs):
        ak, postk = run(k)
        if ak != a0 or postk is None:
            return None                     # not a forced-song wrapper
        d = {a: postk[a] for a in range(0x10000)
             if postk[a] != post0[a] and not 0xD000 <= a <= 0xDFFF}
        if len(d) > max_diff:
            return None
        if d:
            any_diff = True
        out[k] = d
    if not any_diff:
        return None                         # pure forced song = C19's probe
    return a0, out


def _glide_neutered_probe(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """Glide-speed store re-pointed away from glsp (STATIC opcode probe, C19).
    The canon $Cx/$Dx dispatch stores the command's speed nibble with
    `AND #$1F / PHA / AND #$0F / STA glsp,x` ($1136: `9D 41 17`); a wedge
    variant re-points that STA into dead data (Ice_on_Fire: `9D 41 1F`), so
    glsp is NEVER written and no glide/slide ever moves — every $Cx plays its
    note A verbatim and every $Dx is a soft hold. Musically that IS the
    engine's speed-0 glide-cancel, so the extractor forces the decoded speed
    nibble to 0 (byte consumption + note/target unchanged) and the composer
    needs no knob.

    Anchor: the truth for where glsp LIVES is the fx_glide READ site (the
    runtime consumer), and store/read must be paired WITHIN ONE PLAYER
    COPY — so both sites are anchored at fixed canon offsets from the
    member's base (store `29 1F 48 29 0F 9D <op>` at base+$131, read
    `BD <op> F0` at base+$41C). The wedge fires iff store != read. Two
    rejected cuts: comparing against the gla store minus 3 flagged
    Rocket_n_Roll (FULL; player relocated to $5000, glsp store/read
    correctly at $5741, gla operand a STALE dead-path canon $1744 — the
    r93 partial-relocation pattern); a whole-image regex pair mis-paired
    compilation members (first dispatch from one packed player, reads from
    another). Fail-open: either anchor absent -> None (extract unchanged).

    The value is the re-pointed store's OPERAND (hex) — the wedge's second
    effect needs it: `STA operand,X` can land INSIDE THE SONG DATA, so each
    voice's executed glide-speed nibble is POKED over the byte at operand+X
    (Ice_on_Fire: V1's $C4 rows write $04 over sector 20's pos-37 note
    byte, audibly a played note 4). The extract simulates that poke
    (`_glide_poke_overlay`) so the walk reads the engine's effective data."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    st = base + 0x131
    if st + 8 > 0x10000 or \
            bytes(mem[st:st + 6]) != b'\x29\x1F\x48\x29\x0F\x9D':
        return None
    store = mem[st + 6] | (mem[st + 7] << 8)
    rd = base + 0x41C
    if rd + 4 > 0x10000 or mem[rd] != 0xBD or mem[rd + 3] != 0xF0:
        return None
    read = mem[rd + 1] | (mem[rd + 2] << 8)
    if read != base + 0x741:
        # the READ site itself deviates from canon geometry relative to the
        # detected base: no trustworthy live-glsp anchor — fail open.
        return None
    if store == read:
        return None                         # store hits the live glsp
    return f'{store:04X}'


def _v3_instr_tempo_probe(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """Tempo-mailbox play tail (STATIC opcode probe, custom Doxx build —
    Two_Channels). The rewritten play body ends `JMP <handler>` where the
    handler reads the THIRD voice's current-instrument slot and treats a
    value >= $10 as a tempo command:

        AD lo hi   LDA curinst+2
        C9 10      CMP #$10
        90 05      BCC +5
        29 0F      AND #$0F
        8D 16 17   STA speed          (base+$716)
        60         RTS

    Layout-independent shape scan (the build relocates its globals); the
    STA operand must be the member's speed reload (base+$716) — the one
    address the canon layout pins. Fail-open: no match -> None (extract
    unchanged; an instr command >= $10 stays a plain phantom-instrument
    statement)."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    spd = base + 0x716
    tail = bytes([0xC9, 0x10, 0x90, 0x05, 0x29, 0x0F,
                  0x8D, spd & 0xFF, spd >> 8, 0x60])
    hi = min(0x10000, base + 0x2000) - 13
    for a in range(base, hi):
        if mem[a] == 0xAD and bytes(mem[a + 3:a + 13]) == tail:
            return '1'
    return None


def _route_clear_dead_probe(path: str, base: int,
                            post_init_sub: 'int | None' = None):
    """Non-filter route-bit CLEAR re-pointed off the $D417 shadow (STATIC
    opcode probe, C19 16th occ, Daf/Classic_Mix). At note-init a filter
    instrument ORs its route bit into the shadow (base+$18, canon
    $1270-$1278) and a NON-filter instrument ANDs it clear ($12C0-$12C8).
    The wedge re-points ONLY the clear's STA (canon `8D 18 10` ->
    `8D 1C 10`, a void byte), so routing bits accumulate and never clear —
    the work-file leftover ($07) persists through the whole song although
    voices keep playing non-filter instruments. Anchor BOTH sites' full
    canon shape relative to the member's base (LDA shadow / AND
    base+$713,x / STA ... and LDA shadow / ORA base+$710,x / STA shadow);
    fire iff the SET store hits the shadow and the CLEAR store does not.
    Fail-open on any shape deviation. Value = the re-pointed operand."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    sh = base + 0x18
    cl = base + 0x2C0
    st = base + 0x270
    if cl + 9 > 0x10000 or st + 9 > 0x10000:
        return None

    def _abs(op, a):
        return (mem[a + 1] | (mem[a + 2] << 8)) if mem[a] == op else None

    if _abs(0xAD, cl) != sh or _abs(0x3D, cl + 3) != base + 0x713 \
            or mem[cl + 6] != 0x8D:
        return None
    if _abs(0xAD, st) != sh or _abs(0x1D, st + 3) != base + 0x710 \
            or _abs(0x8D, st + 6) != sh:
        return None
    tgt = mem[cl + 7] | (mem[cl + 8] << 8)
    if tgt == sh:
        return None                         # clear hits the live shadow
    return f'{tgt:04X}'


def _track_ff_reinit_probe(path: str, base: int,
                           post_init_sub: 'int | None' = None):
    """$FF track-loop handler re-pointed at the INIT routine (STATIC opcode
    probe, C19, Greenhorn/Second r117). Canon handler (base+$DD):
    `A9 00 / 9D 26 17 (otrk,x = 0) / 4C D2 10 (re-fetch)` — loop the track.
    The wedge: `A9 00 / 20 <rts> (neutered) / 4C <init-body>` — the FIRST
    track end RESTARTS the whole song via init (A=0): the init's $D418 +
    ascending SID clear land mid-stream, then the song plays from the top
    with init-cleared state. Anchor the full patched shape: LDA #$00, a JSR
    whose target is an RTS byte, and a JMP whose target is the member's real
    init body (the jump-table init JMP's operand) — fail-open on anything
    else. Value = the JMP target."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    site = base + 0xDD
    if site + 8 > 0x10000:
        return None
    if mem[site] != 0xA9 or mem[site + 1] != 0x00:
        return None
    if mem[site + 2] != 0x20:                       # JSR (canon: STA $9D)
        return None
    jsr_tgt = mem[site + 3] | (mem[site + 4] << 8)
    if jsr_tgt >= 0x10000 or mem[jsr_tgt] != 0x60:  # must be a neutered call
        return None
    if mem[site + 5] != 0x4C:
        return None
    jmp_tgt = mem[site + 6] | (mem[site + 7] << 8)
    if jmp_tgt == base + 0xD2:                      # canonical re-fetch loop
        return None
    # The full anchor (LDA #$00 + a byte-preserving neutered JSR-to-RTS where
    # canon has the otrk store + a JMP away from the re-fetch) is the
    # hand-patch signature; the JMP target is the member's init body — which
    # need NOT equal the jump-table operand (Second: JT init -> a $101D stub,
    # the wedge jumps the $1807 body directly). Verify-gated: a false fire
    # yields a partial, never a silent wrong FULL.
    return f'{jmp_tgt:04X}'


def _track_loop_dead_probe(path: str, base: int,
                           post_init_sub: 'int | None' = None):
    """$FF track-LOOP hook re-pointed OFF the track-position address = a DEAD
    loop that HALTS the tune (STATIC opcode probe, C19 — Zyron/Solar_Energy).

    The JSR-hook loop variant reads the byte AFTER `$FF` as the loop position
    and stores it to otrk: the dispatch `C9 FF D0 08 A9 00 20 <hook>` (CMP #$FF
    / BNE / LDA #0 / JSR hook) calls `INY / LDA (zp),y / STA base+$726,x / RTS`.
    The wedge re-points that STA operand AWAY from otrk (base+$726) to a dead
    address (Solar_Energy: STA $6726,x, hi-byte $17->$67), so the loop target
    goes nowhere, otrk never advances, and the `JMP` back to the dispatch
    re-reads the same `$FF` — play() spins uselessly the moment a voice reaches
    its track end, so the WHOLE tune HALTS and HOLDS (no further SID writes,
    $D418 frozen). The musician's "play once, end — don't loop" trick.

    Write-stream effect (CORE TENET — reproduce the stream, not the spin): play
    normally, and at the frame the first voice reaches its track end produce no
    more writes ever. The extract walks the track as a STOP (not a loop); the
    composer keys on this param to swap the per-voice $FE stop for a
    halt-the-song handler (like track_fe_reset, minus its $D418=$00 write).

    Regression-safe by construction: canon loop-to-0 has `STA otrk,x` inline at
    base+$DF (not a JSR) -> the sig's JSR byte fails; a GENUINE read-next hook
    stores to otrk (op == base+$726) -> returns None. Only a JSR-hook whose
    store is re-pointed off otrk fires."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    disp = base + 0xD2                   # loop dispatch entry: LDY otrk,x (BC)
    site = base + 0xD9                   # ...then CMP #$FF at +$D9
    if site + 9 > 0x10000 or disp < 0:
        return None
    # dispatch reads otrk from `LDY <otrk>,x`; the loop hook must store the loop
    # target BACK to that same otrk. Read the actual otrk from the fetch operand
    # (relocation-safe; NOT the assumed base+$726 — a variant can place otrk
    # elsewhere and comparing to base+$726 would false-fire, e.g. the $0350
    # read-next family).
    if mem[disp] != 0xBC:
        return None
    otrk = mem[disp + 1] | (mem[disp + 2] << 8)
    # loop dispatch: CMP #$FF / BNE +8 / LDA #0 / JSR hook  (JSR-hook variant)
    if not (mem[site] == 0xC9 and mem[site + 1] == 0xFF
            and mem[site + 2] == 0xD0 and mem[site + 3] == 0x08
            and mem[site + 4] == 0xA9 and mem[site + 5] == 0x00
            and mem[site + 6] == 0x20):
        return None
    hook = mem[site + 7] | (mem[site + 8] << 8)
    if hook + 7 > 0x10000:
        return None
    # hook: INY / LDA (zp),y / STA <op>,x / RTS
    if not (mem[hook] == 0xC8 and mem[hook + 1] == 0xB1
            and mem[hook + 3] == 0x9D and mem[hook + 6] == 0x60):
        return None
    op = mem[hook + 4] | (mem[hook + 5] << 8)
    if op == otrk:
        return None                     # genuine read-next loop (stores to otrk)
    # OBSERVE-CONFIRM (ground truth — a static store-mismatch is NOT enough).
    # The mismatched dispatch can be DEAD CODE never reached at runtime: KB/
    # 1_67_Years ($4000) and PVCF/Kata_Sandom ($0800) are relocated players whose
    # $FF dispatch reads a relocated otrk (base+$726) but whose hook stores to the
    # UN-relocated canon $1726 — a leftover; the loop dispatch is never executed
    # and the tune plays on (verified: 0 hits on the hook, writes grow with
    # duration). The wedge only HALTS the tune when the dead loop is actually
    # reached, so confirm from the orig write stream: the writes must CEASE well
    # before the capture end (a long trailing silence). A looping/continuous tune
    # writes to the end and is rejected here.
    try:
        import subprocess
        from src.songlengths import load_database, get_durations
        sub = post_init_sub if post_init_sub is not None else 0
        try:
            db = load_database(os.path.join('hvsc85', 'DOCUMENTS',
                                            'Songlengths.md5'))
            # the recorded songlength can END at the fade-out, SHORT of the
            # engine's actual halt frame (Solar_Energy: recorded 345 s, halts
            # at 376 s) — use the standard verify margin so the halt (if any)
            # lands well inside the window.
            dur = get_durations(path, db)[sub] * 1.15 + 30.0
        except Exception:
            dur = 450.0
        out = subprocess.run(
            ['siddump', path, '--subtune', str(sub + 1),
             '--duration', f'{dur:.0f}', '--writelog'],
            capture_output=True, text=True).stdout
        lines = out.splitlines()[2:]                    # drop json + col header
        last = max((i for i, ln in enumerate(lines)
                    if '|W:' in ln
                    and len(ln.split('|W:', 1)[1].split(':')) >= 3),
                   default=-1)
        if last < 0 or (len(lines) - last) < 1000:      # <20s trailing silence
            return None                                 # plays on -> not a halt
    except Exception:
        return None
    return '1'                          # dead loop reached -> tune HALTS + HOLDS


def _track_fe_reset_probe(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """$FE track-STOP handler re-pointed at the KERNAL RESET vector (STATIC
    opcode probe, C19 — Wayne/Dark_Side). Canon handler (base+$E9):
    `A9 00 / 9D 0C 10 (STA $100C,x = clear the voice-active flag) / 60 (RTS)`
    — the per-voice STOP: the voice freewheels its last note, the OTHER voices
    keep playing. The wedge overwrites the first 3 bytes with `4C E2 FC`
    (JMP $FCE2 = KERNAL RESET): the FIRST voice to reach its `$FE` stop resets
    the machine, whose IOINIT does `STX $D418` with X=0 (KERNAL $FDC4) — a lone
    `$D418=$00` (silence) — then the CPU idles in the BASIC loop, so the whole
    song HALTS with no further SID writes. Anchor the walker's `$FE` test
    (`C9 FE D0 06` at base+$E5) AND the JMP-to-$FCE2 handler; fail-open on
    anything else. Value = the JMP target (song-end silence marker).

    Write-stream effect (CORE TENET — reproduce the stream, not the reset): at
    the frame the first voice hits `$FE`, emit a single `$D418=$00` and produce
    no more writes ever. The composer keys on this param to swap the per-voice
    stop for a halt-the-song handler."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    site = base + 0xE9
    if site + 3 > 0x10000:
        return None
    # walker's $FE test immediately before the handler (canon layout)
    if (mem[base + 0xE5] != 0xC9 or mem[base + 0xE6] != 0xFE or
            mem[base + 0xE7] != 0xD0 or mem[base + 0xE8] != 0x06):
        return None
    if mem[site] != 0x4C:                       # JMP (canon: LDA #$00)
        return None
    jmp_tgt = mem[site + 1] | (mem[site + 2] << 8)
    if jmp_tgt != 0xFCE2:                        # only the KERNAL RESET vector
        return None
    return f'{jmp_tgt:04X}'


def _reinit_ghost_state_map(base: int) -> dict:
    """canon_addr -> (composer_label, voice_index) for every per-voice state
    slot a ghost unit can poke, relocated for `base`. The $1718-$179D block is
    the composer's DMC_OFFTABLE_STATE (+ the gated wavepos row, always a real
    label); the three arrays BELOW $1718 that init does NOT clear — gate masks
    ($100F), current notes ($1012), current instruments ($1015) — are added
    explicitly (they carry the surviving voice's note/wave state and are the
    below-$1718 slots the first shape-B investigation skipped)."""
    from pipelines.dmc.composer_asm import DMC_OFFTABLE_STATE, DMC_WAVEPOS_ROW
    shift = base - 0x1000
    m = {}
    rows = list(DMC_OFFTABLE_STATE) + [DMC_WAVEPOS_ROW]
    rows += [(0x100F, 'gatemask', 3), (0x1012, 'curnote', 3),
             (0x1015, 'curinst', 3), (0x1018, 'shadow17', 1)]
    for a, lbl, nb in rows:
        for i in range(nb):
            m[a + shift + i] = (lbl, i)
    return m


def _extract_reinit_burst(frames) -> 'list | None':
    """Given the orig's per-frame writelog, find a MID-STREAM init burst (the
    $FF re-init firing in-window) and return the ghost SID burst it carries, or
    None if no such burst exists in the window (the wrap is past-window, so the
    re-init never fires and the member must stay byte-identical).

    An init burst = `$D418=x` then the ascending `$D400..$D417 = 0` clear. The
    ghost burst is the writes AFTER that clear and BEFORE the filter tail
    ($D415+), i.e. the voice-register writes the aliased ghost units emit."""
    for f in frames[5:]:                          # skip the frame-0 cold init
        w = [(r, v) for (_c, r, v) in f]
        n = len(w)
        for i in range(n):
            if w[i][0] != 0x18:
                continue
            j, exp = i + 1, 0
            while j < n and w[j][0] == exp and w[j][1] == 0 and exp < 0x18:
                j += 1
                exp += 1
            if exp < 0x18:
                continue                          # not the full ascending clear
            ghost = []
            for r, v in w[j:]:
                if r >= 0x15:                     # filter tail begins
                    break
                ghost.append((r, v))
            if ghost:
                return ghost
    return None


def _reinit_windows_via_siddump(path: str, wedge: int, window_s: float):
    """GROUND-TRUTH capture of the C19 shape-B reinit COLD/WARM RAM windows
    ($1000-$17FF) from libsidplayfp, via `siddump --reinit-snapshot`:
      COLD = the window at the first play-vector entry (post-init, pre-play);
      WARM = the window at the first play-vector entry AFTER the wedge PC has
             executed (= the end of the reinit play(), after the ghost units).
    Both windows are play-vector-entry-aligned, so robust to siddump frame
    bucketing (Trap C). Returns (cold, warm) as 2048-byte objects, or
    (None, None) if both windows were not captured (no PSID play vector, or the
    wedge never fired within the window).

    Ground-truth replacement for the deleted py65 capture (Phase 1 of
    docs/siddump_native_capture_plan.md): the reinit fires ~9800 frames deep,
    where a py65 journey can diverge on power-on/environment reads
    (feedback_ground_truth.md). Validated byte-identical (2x2048 bytes) to the
    py65 capture on For_Party before the py65 path was deleted. The trigger's
    execution-signature discriminator cannot be split by an IRQ here: the
    wedge runs inside the play() IRQ handler with the I flag set."""
    import subprocess
    repo = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', '..', '..'))
    siddump = os.path.join(repo, 'tools', 'siddump')
    try:
        out = subprocess.run(
            [siddump, path, '--reinit-snapshot', '%X' % wedge, '1000-17FF',
             '--duration', str(window_s + 10)],
            capture_output=True, text=True, timeout=300)
    except Exception:
        return None, None
    line = next((l for l in out.stdout.splitlines()
                 if l.startswith('SNAP:')), None)
    if not line:
        return None, None
    parts = dict(p.split('=', 1) for p in line[len('SNAP:'):].split('|')
                 if '=' in p)
    cold_h, warm_h = parts.get('COLD', ''), parts.get('WARM', '')
    if len(cold_h) != 0x800 * 2 or len(warm_h) != 0x800 * 2:
        return None, None                     # WARM absent => wedge never hit
    return bytes.fromhex(cold_h), bytes.fromhex(warm_h)


def _simulate_reinit_ghosts(path: str, base: int,
                            post_init_sub: 'int | None' = None):
    """GHOST reproduction data for the shape-B $FF-reinit wedge (C19, For_Party).

    When the wrap voice is NOT the last unit, init's RTS pops the wrap voice's
    call and the play body runs the REMAINING voices as ghost units (X past the
    3-voice range). On the ORIG memory map those aliased reads/writes emit a
    member-constant SID burst on V1's registers AND poke the surviving (idle)
    voice's state so it plays a real part in the restart instead of idling.

    We reproduce the WRITE STREAM, not the aliasing (CORE TENET). Two ground
    truths, cheap gate first:

      * ghost burst — from the orig's siddump writelog over the verify window
        (`_extract_reinit_burst`); this ALSO gates in-window (None past-window,
        so every non-For_Party shape-B carrier stays byte-identical without ever
        touching py65);
      * pokes — the surviving voice's state slots. Capture the RAM window at
        the wrap (WARM) and diff against the clean post-init baseline (COLD),
        mapping each differing per-voice slot to its composer label. (The
        below-$1718 slots curnote/gatemask are the freq-determining state the
        first shape-B pass skipped.) The windows come from libsidplayfp
        (`_reinit_windows_via_siddump`, GROUND TRUTH by construction —
        feedback_ground_truth.md / docs/siddump_native_capture_decision.md).
        Migration gate (2026-07-25): windows byte-identical to the py65
        capture (2x2048) + For_Party FULL, then the py65 path was deleted.
        NB the first flag version captured a WRONG WARM (79/2048 off): its PC
        trigger fired on a DATA read of the wedge address at frame 200 — the
        C20-style fresh-py65-baseline control caught it; c64cpu.h now
        discriminates execution by the consecutive-read bus signature.

    Returns 'burst|pokes' (the track_ff_reinit_ghost param) or None."""
    try:
        from pipelines.hubbard.verify_cycle import writelog_capture
        from pipelines.dmc.v4.extract.engine_model import _verify_window
    except Exception:
        return None

    window_s = _verify_window(path)
    # (1) cheap siddump gate + ghost burst (in-window ground truth)
    try:
        frames = writelog_capture(path, subtune=0, duration=window_s)
    except Exception:
        return None
    ghost = _extract_reinit_burst(frames)
    if not ghost:
        return None                               # wrap past-window / no ghost

    # (2) surviving voice's state pokes: WARM-vs-COLD RAM diff. GROUND TRUTH
    #     first (siddump), py65 only as a fallback (see the helpers' docstrings
    #     + feedback_ground_truth.md).
    wedge = base + 0xDD
    cold, warm = _reinit_windows_via_siddump(path, wedge, window_s)
    if cold is None or warm is None:
        return None

    smap = _reinit_ghost_state_map(base)
    pokes = []
    for off in range(0x1000, 0x1800):
        if cold[off - 0x1000] == warm[off - 0x1000]:
            continue
        ent = smap.get(off)
        if ent is None:
            continue                              # scratch / copyright, not state
        lbl, vi = ent
        pokes.append((lbl, vi, warm[off - 0x1000]))

    burst_s = ';'.join(f'{r:02X}={v:02X}' for r, v in ghost)
    poke_s = ';'.join(f'{lbl},{vi},{val:02X}' for lbl, vi, val in pokes)
    return f'{burst_s}|{poke_s}'


def _track_ff_reinit_ghost_probe(path: str, base: int,
                                 post_init_sub: 'int | None' = None):
    """Shape-B $FF-track-reinit WITH a ghost-unit tail (C19, 22nd occ shape B —
    Hallen/For_Party_V_95). The canon $FF handler `A9 00 / 9D 26 17 / 4C D2 10`
    is patched to one of two forms, both of which restart the whole song via
    init AND run one or more voices as GHOST units (see `_simulate_reinit_ghosts`):

      * JMP-init (Hallen/For_Party): `A9 00 / 4C <init>` — JMP straight to init;
        init's RTS pops the wrap voice's call, so the play body's remaining
        `inx : jsr voice` iterations run as ghost units with X past the 3-voice
        range ($19/$1A). (The canon re-fetch tail is left as dead code.)

      * JSR-init RESUME (Verdict/Verdict_01, C19 new occ): `A9 00 / 20 <init> /
        4C <base+D2>` — JSR init (its clear loop leaves X=$18) then JMP the
        CANONICAL re-fetch in the SAME frame. So the re-fetch runs as a ghost
        unit at X=$18 *and* the play body's two remaining iterations run at
        X=$19/$1A — one more ghost unit than the JMP-init form. Distinct from
        shape A's `track_ff_reinit` (JSR to a NEUTERED RTS byte + JMP AWAY from
        the re-fetch): here the JSR target is the REAL init and the JMP target
        is exactly the re-fetch (base+$D2).

    Both forms share the same capture + the same composer `reinit_ghost` branch:
    we reproduce the captured V1-reg burst (the aliased ghost writes), NOT the
    out-of-bounds aliasing (CORE TENET — different memory map ⇒ different
    garbage). STATIC anchor identifies the shape and confirms it leads to init,
    then the ghost sim GATES on the wrap being in the verify window (its burst
    capture returns None past-window) and captures the burst + pokes. Returns
    the `track_ff_reinit_ghost` spec, or None (not shape B / past window / no
    ghost tail — every non-carrier member stays byte-identical)."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    site = base + 0xDD
    if site + 8 > 0x10000:
        return None
    if mem[site] != 0xA9 or mem[site + 1] != 0x00:
        return None
    # a target leads to init iff it is the init vector (base = `JMP body`) or
    # the body that vector jumps to. A false lead yields a partial, never a
    # wrong FULL (build+verify gated).
    init_body = mem[base + 1] | (mem[base + 2] << 8) if mem[base] == 0x4C else None
    leads_to_init = (lambda tgt: tgt == base
                     or (init_body is not None and tgt == init_body))
    op = mem[site + 2]
    if op == 0x4C:                                # JMP-init form
        jmp_tgt = mem[site + 3] | (mem[site + 4] << 8)
        if jmp_tgt == base + 0xD2:               # canonical re-fetch loop
            return None
        if not leads_to_init(jmp_tgt):
            return None
    elif op == 0x20:                             # JSR-init RESUME form
        if not leads_to_init(mem[site + 3] | (mem[site + 4] << 8)):
            return None
        if mem[site + 5] != 0x4C:
            return None
        if (mem[site + 6] | (mem[site + 7] << 8)) != base + 0xD2:
            return None                          # must JMP the re-fetch in-frame
    else:
        return None
    return _simulate_reinit_ghosts(path, base, post_init_sub)


def _hank_ff_loop_targets(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """Per-voice $FF loop targets for the HANK $FF-loop variant (Hank/Roots).

    The canon $FF handler `A9 00 / 9D 26 17 (otrk=0) / 4C D2 10` is patched to
    `A9 00 / 4C <handler>` where <handler> = `LDY otrk,X / INY / LDA ($zp),Y /
    STA otrk,X / JMP <re-fetch>` — the loop target is the byte read through a
    zero-page pointer `$zp`. In the buggy majority `$zp` holds a pointer whose
    `[otrk+1]` byte is $00, so every voice loops to start (== the canon-path
    default, handled). But on Roots `$zp` = $0000 (never set on this path), so
    the handler reads ZERO PAGE at `$0000+otrk+1`: voice 1's `otrk+1=$31` reads a
    player scratch byte ($87) and voice 2's `otrk+1=$58` collides with the
    $0057/$0058 track-pointer slot (the live track-pointer-hi byte, $1A). Those
    are sonified emulator-environment bytes (C29 class).

    ⚠ GROUND TRUTH IS LIBSIDPLAYFP, NOT py65 (feedback_ground_truth). The read
    sources are uninitialized/player-written zero page whose value DIFFERS
    between emulators — py65 read $00 (wrong) where libsidplayfp reads $87. So
    measure the post-loop track offset each voice actually reaches from siddump
    (the verdict engine): run `--memwatch-on-write D417` (a per-frame filter-tail
    write) snapshotting the three otrk bytes, find the frame where a voice's
    otrk JUMPS (loop), and take the value it lands on. The walk's `loop_reset_pos`
    is the pre-fetch target = landed-otrk − 1 (the loop lands one row before its
    first note-init, past a leading transpose); a voice whose landing is ≤ 1 is
    an ordinary loop-to-start and is left on the canon path (None).

    Returns a 3-tuple for `loop_reset_pos`, or None when no voice loops to a
    non-start target (the whole Hank family except Roots) so nothing changes."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    site = base + 0xDD
    if site + 5 > 0x10000 or mem[site] != 0xA9 or mem[site + 1] != 0x00 \
            or mem[site + 2] != 0x4C:
        return None
    h = mem[site + 3] | (mem[site + 4] << 8)
    # handler shape: LDY otrk,X (BC) / INY (C8) / LDA (zp),Y (B1) / STA otrk,X
    # (9D), the LDY and STA targeting the SAME address (= otrk); anything else
    # is a different $FF variant (For_Party's JMP-init, canon, reset-all-to-N).
    if h + 9 > 0x10000 or mem[h] != 0xBC or mem[h + 3] != 0xC8 \
            or mem[h + 4] != 0xB1 or mem[h + 6] != 0x9D:
        return None
    otrk = mem[h + 1] | (mem[h + 2] << 8)
    if (mem[h + 7] | (mem[h + 8] << 8)) != otrk:
        return None

    import subprocess
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                      'tools', 'siddump')
    try:
        from pipelines.dmc.v4.extract.engine_model import _verify_window
        window = _verify_window(path)
    except Exception:
        window = 200.0
    # watch the 3 otrk bytes + each voice's track base (trkpl $1707,x / trkph
    # $170A,x), so the loop TARGET can be compared to the canon-path default
    # `track[otrk+1]` — override ONLY where the buggy zero-page read yields a
    # target the track-read would NOT (valid-pointer members read the track and
    # are already correct, must stay byte-identical).
    trkpl, trkph = base + 0x707, base + 0x70A
    snap = [otrk, otrk + 1, otrk + 2, trkpl, trkpl + 1, trkpl + 2,
            trkph, trkph + 1, trkph + 2]
    addrs = ','.join(f'{a:04X}' for a in snap)
    try:
        out = subprocess.run(
            [sd, path, '--memwatch-on-write', 'D417', addrs,
             '--duration', str(window), '--subtune', '1'],
            capture_output=True, text=True, timeout=180).stdout
    except Exception:
        return None
    keys = [f'{a:04X}'.lstrip('0').upper() for a in snap]
    seq = []
    for ln in out.splitlines():
        if 'D417' not in ln:
            continue
        d = {}
        for kv in ln.split('|')[-1].split(':'):
            if '=' in kv:
                k, v = kv.split('=')
                try:
                    d[k.upper()] = int(v, 16)
                except ValueError:
                    pass
        row = tuple(d.get(k) for k in keys)
        if None not in row:
            seq.append(row)
    # per voice: the FIRST otrk JUMP (decrease, or +>2) is its loop. Compare the
    # landed offset to the CANON-PATH default `track[otrk_before+1]`: a valid
    # pointer lands within a few transposes of it (the walk only INCs), so the
    # default is already right — leave it (None). Only a zero-page read lands
    # UNRELATED to the track byte (Roots): override with landed−1 (the loop lands
    # one row past its target). Ordinary advance is +0/+1 per frame.
    out_t = []
    for v in range(3):
        found = None
        for i in range(1, len(seq)):
            if seq[i][v] < seq[i - 1][v] or seq[i][v] > seq[i - 1][v] + 2:
                pos_b = seq[i - 1][v]                    # otrk before the loop
                tbase = seq[i][3 + v] | (seq[i][6 + v] << 8)   # trkpl/trkph
                deflt = mem[(tbase + ((pos_b + 1) & 0xFF)) & 0xFFFF]
                lv = seq[i][v]
                # landed reachable from the track default (a few transposes)?
                if lv >= 2 and (lv - deflt) & 0xFF > 8:
                    found = (lv - 1) & 0xFF             # zero-page read override
                break
        out_t.append(found)
    return tuple(out_t) if any(t is not None for t in out_t) else None


def _fclaim_clear_dead_probe(path: str, base: int,
                             post_init_sub: 'int | None' = None):
    """Per-play fclaim CLEAR re-pointed off the state block (STATIC opcode
    probe, C19, Gomez/Jezuseczek r115). The canon play body opens
    `LDX #$00 / STX $1720` (base+$90/$92) — clearing the filter claim so
    the FIRST filter voice each play() steps the filter program once. The
    wedge re-points the STX at a VOID address ($3F20, past the image), so
    the claim persists forever after the first filter voice sets it: the
    filter program NEVER steps again and every later cutoff change comes
    solely from $F1 filterset commands (the orig freezes at each command's
    init cutoff). Anchor the full canon shape (LDX #$00 imm + STX abs);
    fire iff the store misses base+$720 AND lands outside the loaded image
    (an in-image repoint would poke data — a different wedge, refuse).
    Fail-open on any shape deviation. Value = the re-pointed operand."""
    if base is None:
        return None
    mem, s = _load(path, post_init_sub)
    site = base + 0x90
    if site + 5 > 0x10000:
        return None
    if mem[site] != 0xA2 or mem[site + 1] != 0x00 or mem[site + 2] != 0x8E:
        return None
    tgt = mem[site + 3] | (mem[site + 4] << 8)
    if tgt == base + 0x720:
        return None                         # canonical clear
    lo, hi = s['load'], s['load'] + len(s['payload'])
    if lo <= tgt < hi:
        return None                         # in-image repoint = data poke,
                                            # not this wedge
    return f'{tgt:04X}'


def _filterdef_anim_probe(path: str, base: int, op_filtdef: int,
                          post_init_sub: 'int | None' = None):
    """Appended filter-def ANIMATOR driver (Ed/Wrath Designs, Cliche_Beat;
    C19 18th occ). Both PSID vectors are re-pointed at a driver appended
    after the canon body. Its init pokes defs 0-2 (r0 = a start byte, init
    cell = a seed), builds a 256-byte triangle table, aims an SMC JSR at the
    ramp routine, then continues the canon init (base+$1D). Every play() the
    wrapper JSRs the SMC target then JMPs the canon play body (base+$85):

      phase 1 (ramp):  every p1 plays, defs 0-2 r0 += step until def0's r0
                       equals the cap byte — then the stub retargets the SMC
                       JSR to phase 2;
      phase 2 (LFO):   every p2 plays, def0.init = tri[i0--] and def1.init =
                       tri[i3], i3 += 2. (The third store hits def1 AGAIN —
                       an author bug that leaves def2's init static and makes
                       the middle index walk dead; reproduced as-is.)

    fres/fcut sample these table bytes at filter note-inits, so the audible
    effect is a resonance sweep then a cutoff-init triangle LFO. Full-shape
    template match anchored from the two vectors; any deviation fail-opens.
    Returns 'step,capF0,c1seed,p1reset,c2seed,p2reset,tristart,tridesc'."""
    if base is None or op_filtdef is None:
        return None
    mem, _ = _load(path, post_init_sub)

    def rd16(a):
        return mem[a] | (mem[a + 1] << 8)

    if mem[base] != 0x4C or mem[base + 3] != 0x4C:
        return None
    I = rd16(base + 1)
    W = rd16(base + 4)
    fd = rd16(op_filtdef)
    if mem[W] != 0x20 or mem[W + 3] != 0x4C or rd16(W + 4) != base + 0x85:
        return None
    # (W+1 is the SMC slot — its FILE byte is stale; init re-aims it below.)
    # --- init block ---
    if mem[I] != 0xA9 or mem[I + 2] != 0xA2 or mem[I + 4] != 0xA0:
        return None
    r0i, c_seed = mem[I + 1], mem[I + 5]
    a = I + 6
    for op, tgt in ((0x8D, fd), (0x8D, fd + 16), (0x8D, fd + 32),
                    (0x8E, fd + 1), (0x8E, fd + 17), (0x8E, fd + 33)):
        if mem[a] != op or rd16(a + 1) != tgt:
            return None
        a += 3
    if mem[a] != 0x8C or mem[a + 3] != 0x8C:
        return None
    ctr1, ctr2 = rd16(a + 1), rd16(a + 4)
    a += 6
    if mem[a] != 0xA9 or mem[a + 2] != 0xA2 or mem[a + 4] != 0x20:
        return None
    R = mem[a + 1] | (mem[a + 3] << 8)   # init aims the SMC JSR at phase 1
    setsmc = rd16(a + 5)
    a += 7
    if bytes(mem[a:a + 3]) != b'\xa2\x00\xa0' or mem[a + 4] != 0x98 \
            or mem[a + 5] != 0x9D:
        return None
    tstart = mem[a + 3]
    tri = rd16(a + 6)
    if bytes(mem[a + 8:a + 13]) != bytes((0xC8, 0xE8, 0xE0, 0x80, 0xD0)):
        return None
    a += 14
    if bytes(mem[a:a + 3]) != b'\xa2\x00\xa0' or mem[a + 4] != 0x98 \
            or mem[a + 5] != 0x9D or rd16(a + 6) != tri + 0x80:
        return None
    tdesc = mem[a + 3]
    if bytes(mem[a + 8:a + 13]) != bytes((0x88, 0xE8, 0xE0, 0x80, 0xD0)):
        return None
    a += 14
    if bytes(mem[a:a + 2]) != b'\xa9\x00' or mem[a + 2] != 0x8D \
            or mem[a + 5] != 0x8D or mem[a + 8] != 0x8D:
        return None
    i_slots = {rd16(a + 3), rd16(a + 6), rd16(a + 9)}
    if bytes(mem[a + 11:a + 13]) != b'\xaa\xa8' or mem[a + 13] != 0x4C \
            or rd16(a + 14) != base + 0x1D:
        return None
    # --- phase 1 (ramp) at R ---
    if mem[R] != 0xA2 or R + 1 != ctr1 or bytes(mem[R + 2:R + 4]) != b'\xca\x8e' \
            or rd16(R + 4) != ctr1 or bytes(mem[R + 6:R + 9]) != b'\xf0\x01\x60':
        return None
    if mem[R + 9] != 0xA2 or mem[R + 11] != 0x8E or rd16(R + 12) != ctr1:
        return None
    p1_reset = mem[R + 10]
    if mem[R + 14] != 0xAD or rd16(R + 15) != fd or mem[R + 17] != 0xC9 \
            or mem[R + 19] != 0xF0:
        return None
    cap = mem[R + 18]
    retgt = R + 21 + mem[R + 20]
    step = mem[R + 26]
    a2 = R + 21
    for tgt in (fd, fd + 16, fd + 32):
        if mem[a2] != 0xAD or rd16(a2 + 1) != tgt or mem[a2 + 3] != 0x18 \
                or mem[a2 + 4] != 0x69 or mem[a2 + 5] != step \
                or mem[a2 + 6] != 0x8D or rd16(a2 + 7) != tgt:
            return None
        a2 += 9
    if mem[a2] != 0x60:
        return None
    # --- retarget stub + SMC setter ---
    if mem[retgt] != 0xA9 or mem[retgt + 2] != 0xA2 or retgt + 4 != setsmc:
        return None
    P2 = mem[retgt + 1] | (mem[retgt + 3] << 8)
    if mem[setsmc] != 0x8D or rd16(setsmc + 1) != W + 1 \
            or mem[setsmc + 3] != 0x8E or rd16(setsmc + 4) != W + 2 \
            or mem[setsmc + 6] != 0x60:
        return None
    # --- phase 2 (init-cell LFO) at P2 ---
    if mem[P2] != 0xA2 or P2 + 1 != ctr2 or bytes(mem[P2 + 2:P2 + 4]) != b'\xca\x8e' \
            or rd16(P2 + 4) != ctr2 or mem[P2 + 6] != 0xD0:
        return None
    if mem[P2 + 8] != 0xA2 or mem[P2 + 10] != 0x8E or rd16(P2 + 11) != ctr2:
        return None
    p2_reset = mem[P2 + 9]
    a3 = P2 + 13
    pokes = []
    for _ in range(3):
        if mem[a3] != 0xA2 or mem[a3 + 2] != 0xBD or rd16(a3 + 3) != tri \
                or mem[a3 + 5] != 0x8D:
            return None
        pokes.append((a3 + 1, rd16(a3 + 6)))
        a3 += 8
    if [t for _, t in pokes] != [fd + 1, fd + 17, fd + 17]:
        return None                       # incl. the dup-store author bug
    if mem[a3] != 0xEE or rd16(a3 + 1) != pokes[1][0] \
            or mem[a3 + 3] != 0xEE or rd16(a3 + 4) != pokes[2][0] \
            or mem[a3 + 6] != 0xEE or rd16(a3 + 7) != pokes[2][0] \
            or mem[a3 + 9] != 0xCE or rd16(a3 + 10) != pokes[0][0] \
            or mem[a3 + 12] != 0x60:
        return None
    if i_slots != {s for s, _ in pokes}:
        return None                       # init must zero exactly these
    if (cap ^ r0i) & 0x0F:
        return None                       # masked fdres compare equivalence
    return (f'{step:02X},{cap & 0xF0:02X},{c_seed:02X},{p1_reset:02X},'
            f'{c_seed:02X},{p2_reset:02X},{tstart:02X},{tdesc:02X}')


def _pw_bound_shift_probe(path: str, base: int,
                          post_init_sub: 'int | None' = None):
    """PWM bound-A extraction shift (STATIC opcode probe, C19). The note-init
    derives the pulse-width sweep bounds from instrument byte+2: canonically
    `PLA / LSR LSR LSR LSR / STA $1756,x` => bound A = byte+2 >> 4 (its hi
    nibble), bound B = A EOR $0F. A wedge variant swaps one LSR for a 2-byte
    no-op opcode ($17 = SLO $4A,X — it ASLs an unused zp scratch byte and ORs 0
    into A), so only >>2 applies: bound A = byte+2 >> 2, and the pulse hi-byte
    sweeps over a much wider band before flipping direction. The bound VALUES
    are musical content (they ride in USF min_hi/max_hi); this probe only tells
    the extractor which shift produced them, so it stays extract-only.

    Anchor on the STA $1756,x / EOR #$0F / STA $1759,x tail (relocation-aware:
    the two store operands sit at base+$756 and base+$759). Decode the 4-byte
    window between PLA and the first STA, counting LSR-A ($4A); $17 is the known
    2-byte filler, any other opcode bails to canon. Return the shift when != 4,
    else None (extract unchanged). Sole family-1 carrier: Aomeba/20_Years_of_NOP."""
    mem, _ = _load(path, post_init_sub)
    a1 = base + 0x756
    # re.escape the operand bytes: a relocated address low byte can be a regex
    # metacharacter (e.g. '[' = $5B) that breaks compile / matches loosely.
    pat = re.compile(
        rb'\x68(....)\x9D' + re.escape(bytes([a1 & 0xFF, (a1 >> 8) & 0xFF]))
        + rb'\x49\x0F\x9D'
        + re.escape(bytes([(a1 + 3) & 0xFF, ((a1 + 3) >> 8) & 0xFF])),
        re.DOTALL)
    m = pat.search(bytes(mem))
    if not m:
        return None
    window = m.group(1)                     # exactly 4 bytes (PLA's shift run)
    oplen = {0x4A: 1, 0x17: 2}              # LSR-A / SLO zp,X (known no-op)
    shift = 0
    i = 0
    while i < 4:
        n = oplen.get(window[i])
        if n is None:
            return None                     # unknown opcode -> canon >>4 (safe)
        if window[i] == 0x4A:
            shift += 1
        i += n
    if i != 4 or shift == 4:
        return None
    return shift


# Filter-def modulation play wrapper (Ed/Core_of_Acid, the only DMC carrier):
# the play vector runs `JSR reader` — `LDA ptr1 / STA def+1 / LDA ptr2 /
# STA def+3 / RTS` — then a double 16-bit SMC automaton that increments both
# LDA operands each call, wrapping them from $<hi>00 back to the reset
# pointer, then JMPs to the real play body. The pointers sweep an init-time
# GENERATED table (a triangle ramp past the file end), so the filter
# definition's init/stop cutoff bytes carry a free-running looped LFO that
# the engine samples at every filter note-init. Groups: (1) reader addr,
# (2) reset lo (LDY #), (3) reset hi (LDX #), then per pointer block the
# INC lo site, INC hi site, LDA hi site, CMP #wrap_hi, STY lo site,
# STX hi site.
_FMOD_WRAPPER = re.compile(
    rb'\x20(..)\xA0(.)\xA2(.)'
    rb'\xEE(..)\xD0\x10\xEE(..)\xAD(..)\xC9(.)\xD0\x06\x8C(..)\x8E(..)'
    rb'\xEE(..)\xD0\x10\xEE(..)\xAD(..)\xC9(.)\xD0\x06\x8C(..)\x8E(..)'
    rb'\x4C(..)', re.DOTALL)


def _filter_mod_probe(path: str, op_filtdef: int,
                      post_init_sub: 'int | None' = None):
    """Detect the filter-def modulation wrapper and lift its LFO as musical
    content: return 'prog|start|init_phase|stop_phase|d:f,d:f,...' (the
    contour value at position 0, the two taps' start phases, and the
    piecewise-constant-rate delta runs over one period), or None (build
    unchanged). The contour bytes come from the post-init RAM (the table is
    generated by the member's init wrapper); the probe validates that the
    SMC automaton targets exactly the reader's two LDA operands and that the
    stores hit filterdef + 16n + 1 / + 3 (the init/stop cutoff bytes of one
    definition)."""
    mem, s = _load(path, post_init_sub)
    m = _FMOD_WRAPPER.search(bytes(mem))
    if m is None:
        return None
    g = [gr[0] | (gr[1] << 8) if len(gr) == 2 else gr[0]
         for gr in m.groups()]
    (rd, reset_lo, reset_hi,
     inc1lo, inc1hi, lda1, wrap1, sty1, stx1,
     inc2lo, inc2hi, lda2, wrap2, sty2, stx2, _jmp) = g
    # reader shape: LDA p1 / STA t1 / LDA p2 / STA t2 / RTS
    if not (mem[rd] == 0xAD and mem[rd + 3] == 0x8D and mem[rd + 6] == 0xAD
            and mem[rd + 9] == 0x8D and mem[rd + 12] == 0x60):
        return None
    # the automaton must maintain exactly the reader's two LDA operands
    if not (inc1lo == sty1 == rd + 1 and inc1hi == lda1 == stx1 == rd + 2
            and inc2lo == sty2 == rd + 7 and inc2hi == lda2 == stx2 == rd + 8
            and wrap1 == wrap2):
        return None
    p1 = mem[rd + 1] | (mem[rd + 2] << 8)
    t1 = mem[rd + 4] | (mem[rd + 5] << 8)
    p2 = mem[rd + 7] | (mem[rd + 8] << 8)
    t2 = mem[rd + 10] | (mem[rd + 11] << 8)
    fd = mem[op_filtdef] | (mem[op_filtdef + 1] << 8)
    if t2 != t1 + 2 or (t1 - fd - 1) % 16 or not 0 <= (t1 - fd - 1) // 16 < 16:
        return None
    prog = (t1 - fd - 1) // 16 + 1
    reset = reset_lo | (reset_hi << 8)
    period = (wrap1 << 8) - reset
    if not 2 <= period <= 4096:
        return None
    if not (0 <= p1 - reset < period and 0 <= p2 - reset < period):
        return None
    ram = _post_init_ram(path, s['start'] - 1)
    if ram is None:
        return None
    tab = [ram[reset + i] for i in range(period)]
    runs = []
    for i in range(period):
        d = (tab[(i + 1) % period] - tab[i]) & 0xFF
        if runs and runs[-1][0] == d:
            runs[-1][1] += 1
        else:
            runs.append([d, 1])
    if len(runs) > 16 or any(c > 255 for _, c in runs):
        return None
    steps = ','.join(f'{d if d < 128 else d - 256}:{c}' for d, c in runs)
    return f'{prog}|{tab[0]}|{p1 - reset}|{p2 - reset}|{steps}'


def _filter_mod_multi_probe(path: str, base: int, op_filtdef: int,
                            post_init_sub: 'int | None' = None):
    """Multi-tap variant of the filter-def cutoff LFO (Ed/Elechromania; the
    Core_of_Acid single-prog probe above fail-opens on it). The play vector
    JMPs an appendix: `JSR APPLY / LDY #<reset_lo> / LDX #<reset_hi> / N x
    automaton / JMP base+$85`. APPLY is N x `LDA ptr / STA fd+16p+1 /
    STA fd+16p+3` + RTS — ONE roving pointer per def feeds BOTH its init and
    stop cutoff cells. Each automaton block wraps its pointer's hi byte at a
    cap back to (reset_hi:reset_lo) then ALWAYS increments — so the visited
    cycle is reset+1 .. reset+period inclusive (the byte at reset+period is
    read once per cycle before the wrap check fires), period = (cap<<8) -
    reset. The contour bytes are init-GENERATED (read from post-init RAM);
    the init tail also runs APPLY once, so the file bytes of the pointers
    are exactly play 1's apply positions. Returns the same per-prog format
    as the single probe, ';'-joined: 'prog|start|ip|sp|d:f,...;...' with
    ip == sp (one tap serves both cells)."""
    if base is None or op_filtdef is None:
        return None
    mem, s = _load(path, post_init_sub)

    def rd16(a):
        return mem[a] | (mem[a + 1] << 8)

    if mem[base + 3] != 0x4C:
        return None
    W = rd16(base + 4)
    if mem[W] != 0x20 or mem[W + 3] != 0xA0 or mem[W + 5] != 0xA2:
        return None
    A = rd16(W + 1)
    reset = (mem[W + 6] << 8) | mem[W + 4]
    fd = rd16(op_filtdef)
    taps = []                            # (ptr operand addr, ptr, target)
    a = A
    while mem[a] == 0xAD and len(taps) < 16:
        t = rd16(a + 4)
        if mem[a + 3] != 0x8D or mem[a + 6] != 0x8D or rd16(a + 7) != t + 2:
            return None
        taps.append((a + 1, rd16(a + 1), t))
        a += 9
    if mem[a] != 0x60 or not taps:
        return None
    wrap = None
    b = W + 7
    for opa, _p, _t in taps:
        if mem[b] != 0xAD or rd16(b + 1) != opa + 1 or mem[b + 3] != 0xC9 \
                or bytes(mem[b + 5:b + 7]) != b'\xd0\x06' \
                or mem[b + 7] != 0x8C or rd16(b + 8) != opa \
                or mem[b + 10] != 0x8E or rd16(b + 11) != opa + 1 \
                or mem[b + 13] != 0xEE or rd16(b + 14) != opa \
                or bytes(mem[b + 16:b + 18]) != b'\xd0\x03' \
                or mem[b + 18] != 0xEE or rd16(b + 19) != opa + 1:
            return None
        if wrap is None:
            wrap = mem[b + 4]
        elif mem[b + 4] != wrap:
            return None
        b += 21
    if mem[b] != 0x4C or rd16(b + 1) != base + 0x85:
        return None
    period = (wrap << 8) - reset
    if not 2 <= period <= 4096:
        return None
    progs = []
    for _opa, p, t in taps:
        if (t - fd - 1) % 16 or not 0 <= (t - fd - 1) // 16 < 16:
            return None
        if not reset + 1 <= p <= reset + period:
            return None
        progs.append((t - fd - 1) // 16 + 1)
    if len(set(progs)) != len(progs):
        return None
    ram = _post_init_ram(path, s['start'] - 1)
    if ram is None:
        return None
    tab = [ram[reset + 1 + i] for i in range(period)]
    runs = []
    for i in range(period):
        d = (tab[(i + 1) % period] - tab[i]) & 0xFF
        if runs and runs[-1][0] == d:
            runs[-1][1] += 1
        else:
            runs.append([d, 1])
    if len(runs) > 32 or any(c > 255 for _, c in runs):
        return None
    steps = ','.join(f'{d if d < 128 else d - 256}:{c}' for d, c in runs)
    out = []
    for prog, (_opa, p, _t) in zip(progs, taps):
        ph = p - reset - 1
        out.append(f'{prog}|{tab[0]}|{ph}|{ph}|{steps}')
    return ';'.join(out)


def _d417_tail_anim_probe(path: str, base: int, op_filtdef: int,
                          op_wavefreq: int,
                          post_init_sub: 'int | None' = None):
    """Filter-tail STA $D417 re-pointed at a POWER-ON-PATTERN cutoff
    animator (Ed/Go_Funk; C19 19th occ). The canon filter tail's final
    `STA $D417` (base+$AC) is patched to `JMP stub`; the stub does the
    store, then every `reset` plays (first firing after `seed` plays)
    pokes def N's INIT-cutoff cell from `tab_hi<<8 + (++X1)` — an address
    PAST THE IMAGE END, i.e. libsidplayfp's power-on RAM pattern (C29
    environment class; NB `--peek-post-init` reports RELOCATED-psiddrv
    bytes there and disagrees with the play-run RAM — the memwatch is the
    ground truth, `_poweron_fill` models it exactly). The stub also pokes
    two WAVEFREQ-TABLE bytes (note offsets — pattern $FF = offset -1
    audibly shifts every note the affected wave step plays) from a second
    pattern page, one X2 walk (+2/firing) feeding BOTH cells. Those are
    reproducible only when the composer's wave pool is layout-preserving,
    so the EXTRACT forces wave_table_pos layout for carriers and drops the
    param if it cannot be proven. Fail-open on any shape deviation.
    Returns 'seed,reset,x1init,tabhi1,defslot,x2init,tabhi2,wf1,wf2'
    (hex)."""
    if base is None or op_filtdef is None or op_wavefreq is None:
        return None
    mem, _ = _load(path, post_init_sub)

    def rd16(a):
        return mem[a] | (mem[a + 1] << 8)

    site = base + 0xA6
    # canon: LDA shadow / ORA fres / STA $D417 — the STA replaced by JMP
    if mem[site] != 0xAD or mem[site + 3] != 0x0D or mem[site + 6] != 0x4C:
        return None
    S = rd16(site + 7)
    if bytes(mem[S:S + 3]) != b'\x8d\x17\xd4':
        return None
    if mem[S + 3] != 0xA2:
        return None
    seed = mem[S + 4]
    if mem[S + 5] != 0xCA or mem[S + 6] != 0x8E or rd16(S + 7) != S + 4 \
            or bytes(mem[S + 9:S + 12]) != b'\xf0\x01\x60':
        return None
    if mem[S + 12] != 0xA2:
        return None
    reset = mem[S + 13]
    if mem[S + 14] != 0x8E or rd16(S + 15) != S + 4:
        return None
    if mem[S + 17] != 0xEE or rd16(S + 18) != S + 21 or mem[S + 20] != 0xA2:
        return None
    x1 = mem[S + 21]
    if mem[S + 22] != 0xBD or mem[S + 23] != 0x00:
        return None
    tabhi = mem[S + 24]
    fd = rd16(op_filtdef)
    if mem[S + 25] != 0x8D:
        return None
    tgt = rd16(S + 26)
    if (tgt - fd - 1) % 16 or not 0 <= (tgt - fd - 1) // 16 < 16:
        return None
    slot = (tgt - fd - 1) // 16
    # secondary block: X2 walk (+2/firing) poking two WAVEFREQ-table bytes
    if mem[S + 28] != 0xA2 or bytes(mem[S + 30:S + 32]) != b'\xe8\xe8' \
            or mem[S + 32] != 0x8E or rd16(S + 33) != S + 29 \
            or mem[S + 35] != 0xBD or mem[S + 36] != 0x00 \
            or mem[S + 38] != 0x8D or mem[S + 41] != 0x8D \
            or mem[S + 44] != 0x60:
        return None
    x2 = mem[S + 29]
    tabhi2 = mem[S + 37]
    wfb = rd16(op_wavefreq)
    wf1 = rd16(S + 39) - wfb
    wf2 = rd16(S + 42) - wfb
    if not (0 <= wf1 < 0x100 and 0 <= wf2 < 0x100):
        return None
    return (f'{seed:02X},{reset:02X},{x1:02X},{tabhi:02X},{slot:02X},'
            f'{x2:02X},{tabhi2:02X},{wf1:02X},{wf2:02X}')


def _filterdef_anim3_probe(path: str, base: int, op_filtdef: int,
                           post_init_sub: 'int | None' = None):
    """Third Ed appended filter-def driver (Only_Ones; C19 20th occ). Both
    vectors re-pointed. Init generates a 256-byte triangle (asc i+step /
    desc d0-i), pokes def s2 (r0/init/stop) + def s1 (init/stop), seeds the
    SMC slots, then continues canon init. Play: `JSR <smc> / JMP base+$85`.
    PHASE A (every p1 plays): ramp def s2 init/stop up to cap2; res nibble
    of def s2's r0 = a counter<<4 (counter seeded x2seed+1, capped rescap);
    at the cap, ramp def s1 init/stop DOWN to dncap; then retarget the SMC
    to PHASE B (every play): def s2 init/stop = tri[X1]/2 + add2 and def s1
    = tri[X2]/2 + add1, X1 += 1 per p8 plays, X2 += 1 per p8*p2 plays.
    Full-shape template match, fail-open. Returns
    'p1,cap2,rescap,dncap,x1,x2,p8,p2,add2,add1,step,d0,s2,s1' (hex)."""
    if base is None or op_filtdef is None:
        return None
    mem, _ = _load(path, post_init_sub)

    def rd16(a):
        return mem[a] | (mem[a + 1] << 8)

    def match(addr, spec):
        out = {}
        a = addr
        for it in spec:
            if isinstance(it, int):
                if mem[a] != it:
                    return None
                a += 1
            elif it[0] == 'b':
                out[it[1]] = mem[a]
                a += 1
            else:                        # ('w', name)
                out[it[1]] = rd16(a)
                a += 2
        out['_end'] = a
        return out

    if mem[base] != 0x4C or mem[base + 3] != 0x4C:
        return None
    I = rd16(base + 1)
    W = rd16(base + 4)
    w = match(W, [0x20, ('w', 'A'), 0x4C, ('w', 'play')])
    if w is None or w['play'] != base + 0x85:
        return None
    A = w['A']
    ini = match(I, [
        0xA2, 0x00, 0x8A, 0x18, 0x69, ('b', 'step'), 0x9D, ('w', 'tab'),
        0xE8, 0xE0, 0x80, 0xD0, 0xF4,
        0xA2, 0x00, 0xA0, ('b', 'd0'), 0x98, 0x9D, ('w', 'tab80'),
        0x88, 0xE8, 0xE0, 0x80, 0xD0, 0xF6,
        0xA9, ('b', 'r0v'), 0xA2, ('b', 'i2v'), 0xA0, ('b', 'i1v'),
        0x8D, ('w', 't_r0'), 0x8E, ('w', 't_i2'), 0x8E, ('w', 't_s2'),
        0x8C, ('w', 't_i1'), 0x8C, ('w', 't_s1'),
        0xA9, ('b', 'x1'), 0xA2, ('b', 'x2'),
        0x8D, ('w', 'x1op'), 0x8E, ('w', 'x2op'), 0xE8, 0x8E, ('w', 'cnt'),
        0xA9, 0x00, 0xAA, 0xA8, 0x4C, ('w', 'caninit')])
    if ini is None or ini['tab80'] != ini['tab'] + 0x80 \
            or ini['caninit'] != base + 0x1D:
        return None
    fd = rd16(op_filtdef)
    if (ini['t_r0'] - fd) % 16 or (ini['t_i1'] - fd - 1) % 16:
        return None
    s2 = (ini['t_r0'] - fd) // 16
    s1 = (ini['t_i1'] - fd - 1) // 16
    if not (0 <= s2 < 16 and 0 <= s1 < 16) \
            or ini['t_i2'] != fd + 16 * s2 + 1 or ini['t_s2'] != fd + 16 * s2 + 3 \
            or ini['t_s1'] != fd + 16 * s1 + 3:
        return None
    pa = match(A, [
        0xA2, ('b', 'p1'), 0xCA, 0x8E, ('w', 'actr'), 0xF0, 0x01, 0x60,
        0xA2, ('b', 'p1b'), 0x8E, ('w', 'actr2'),
        0xAD, ('w', 'ti2'), 0xC9, ('b', 'cap2'), 0xF0, 0x06,
        0xEE, ('w', 'ti2b'), 0xEE, ('w', 'ts2b'),
        0xA9, ('b', 'cntfile'), 0x0A, 0x0A, 0x0A, 0x0A, 0x8D, ('w', 'oraop'),
        0xAD, ('w', 'r0a'), 0x29, 0x0F, 0x09, ('b', 'orafile'),
        0x8D, ('w', 'r0b'),
        0xAD, ('w', 'cnta'), 0xC9, ('b', 'rescap'), 0xF0, 0x04,
        0xEE, ('w', 'cntb'), 0x60,
        0xAD, ('w', 'i1a'), 0xC9, ('b', 'dncap'), 0xF0, 0x07,
        0xCE, ('w', 'i1b'), 0xCE, ('w', 's1b'), 0x60,
        0xA9, ('b', 'Blo'), 0xA2, ('b', 'Bhi'),
        0x8D, ('w', 'smc1'), 0x8E, ('w', 'smc2'), 0x60])
    if pa is None:
        return None
    if pa['p1'] != pa['p1b'] or pa['actr'] != A + 1 or pa['actr2'] != A + 1 \
            or pa['ti2'] != ini['t_i2'] or pa['ti2b'] != ini['t_i2'] \
            or pa['ts2b'] != ini['t_s2'] or pa['oraop'] != A + 0x2A \
            or pa['r0a'] != ini['t_r0'] or pa['r0b'] != ini['t_r0'] \
            or pa['cnta'] != ini['cnt'] or pa['cntb'] != ini['cnt'] \
            or ini['cnt'] != A + 0x1C \
            or pa['i1a'] != ini['t_i1'] or pa['i1b'] != ini['t_i1'] \
            or pa['s1b'] != ini['t_s1'] \
            or pa['smc1'] != W + 1 or pa['smc2'] != W + 2:
        return None
    B = pa['Blo'] | (pa['Bhi'] << 8)
    pb = match(B, [
        0xA2, ('b', 'x1f'), 0xBD, ('w', 'tabB1'), 0x4A, 0x18, 0x69,
        ('b', 'add2'), 0x8D, ('w', 'i2p'), 0x8D, ('w', 's2p'),
        0xA2, ('b', 'x2f'), 0xBD, ('w', 'tabB2'), 0x4A, 0x18, 0x69,
        ('b', 'add1'), 0x8D, ('w', 'i1p'), 0x8D, ('w', 's1p'),
        0xA2, ('b', 'p8'), 0xCA, 0x8E, ('w', 'c8op'), 0xD0, ('b', 'r1'),
        0xA2, ('b', 'p8b'), 0x8E, ('w', 'c8op2'), 0xEE, ('w', 'x1opB'),
        0xA2, ('b', 'p2'), 0xCA, 0x8E, ('w', 'c2op'), 0xD0, ('b', 'r2'),
        0xA2, ('b', 'p2b'), 0x8E, ('w', 'c2op2'), 0xEE, ('w', 'x2opB'),
        0x60])
    if pb is None:
        return None
    if pb['tabB1'] != ini['tab'] or pb['tabB2'] != ini['tab'] \
            or pb['i2p'] != ini['t_i2'] or pb['s2p'] != ini['t_s2'] \
            or pb['i1p'] != ini['t_i1'] or pb['s1p'] != ini['t_s1'] \
            or B + 1 != ini['x1op'] or pb['x1opB'] != ini['x1op'] \
            or pb['x2opB'] != ini['x2op'] \
            or pb['p8'] != pb['p8b'] or pb['p2'] != pb['p2b'] \
            or pb['c8op'] != pb['c8op2'] or pb['c2op'] != pb['c2op2']:
        return None
    # the X2 immediate slot phase B reads must be the init-seeded one
    if B + 16 != ini['x2op']:
        return None
    return (f"{pa['p1']:02X},{pa['cap2']:02X},{pa['rescap']:02X},"
            f"{pa['dncap']:02X},{ini['x1']:02X},{ini['x2']:02X},"
            f"{pb['p8']:02X},{pb['p2']:02X},{pb['add2']:02X},"
            f"{pb['add1']:02X},{ini['step']:02X},{ini['d0']:02X},"
            f"{s2:02X},{s1:02X}")


# The dual-effect wedge: canon `LDY $170D,x / LDA $172F,x / ... / STA $1724`
# byte-edited into `LDY $170D,x / LDX $2F / ADC #$18 / ADC $1735,x / STA <tgt>`
# (opcode BD->A6 turns the base-freq load into `LDX $2F`, re-indexing every
# subsequent per-voice read +$A9 past the state arrays — onto fixed CODE
# bytes). Anchor on the wedge itself; group(1) = the repointed STA operand.
_DUAL_HACK_SITE = re.compile(rb'\xBC\x0D.\xA6\x2F\x69\x18\x7D\x35.\x8D(..)',
                             re.DOTALL)


def _dual_freq_gen_probe(path: str, base: int, freq_lo: int,
                         post_init_sub: 'int | None' = None):
    """Dual-effect ($40) freq-generator wedge (STATIC opcode probe, C19 4th
    occurrence — Taurus/Taurus_02, the only family-1 carrier): the odd-parity
    dual path's `LDA $172F,x` opcode is patched BD->A6 (`LDX $2F`). Under the
    PSID environment zp $2F holds $A9 (constant; pc-trace-verified), so every
    per-voice `,x` read lands +$A9 past the state arrays, i.e. on fixed code
    bytes: slide speed = the JMP opcode at state+$1820, freq base hi = the
    $80 operand of `CMP #$80` ($17DB), PW lo/hi + ctrl = sub_17EC/17FB code
    bytes, and the "slide accumulator" self-modifies two tune-setup code
    bytes at state+$1841/$1844 whose FILE-IMAGE values seed the ramp (the
    orig init wipe stops at $179D). The repointed STA lands in the pwphase
    triple (Taurus_02: slot 2). The `ORA $BD68,y` in the update reads BASIC
    ROM (environment constants, hardcoded composer-side). Returns
    'step,ph_add,base_hi,pw_lo,pw_hi,ctrl,seed_lo,seed_hi,slot' or None
    (no wedge -> build unchanged)."""
    mem, s = _load(path, post_init_sub)
    m = _DUAL_HACK_SITE.search(bytes(mem))
    if not m:
        return None
    d = freq_lo - 0x1647
    xofs = 0xA9                      # zp $2F under the PSID environment

    def st(canon):                   # state-array byte at canon addr, +$A9
        return mem[canon + d + xofs]

    tgt = m.group(1)[0] | (m.group(1)[1] << 8)
    slot = tgt - (0x1762 + d)        # canon pwphase triple
    if not 0 <= slot <= 2:
        return None                  # unrecognised store target
    ph_add = st(0x1735)
    if 1 + 0x18 + 1 + ph_add > 0xFF:
        return None                  # composer folds the carry chain; keep safe
    ctrl = st(0x1780) & mem[base + 0x00F + xofs]   # canon $100F gate masks
    vals = [st(0x1777), ph_add, st(0x1732), st(0x1750), st(0x1753),
            ctrl, st(0x1798), st(0x179B), slot]
    return ','.join(str(v) for v in vals)


def _d418_play_wrapper(path: str, base: int,
                       post_init_sub: 'int | None' = None):
    """$D418 play-vector wrapper probe: the play entry runs
    `LDA #imm / STA $D418 / JMP <play body>` (PVCF / Zyron / Signor) — a
    constant master-vol|filter-mode write on every play() call before the canon
    play body. Two topologies, both anchored on the reloc-invariant
    `STA $D418`:
      (a) inline   — the PSID play address IS the wrapper, exiting `JMP base+3`
                     (into the canon play jump-table slot);
      (b) indirect — the PSID play address is `JMP <appended wrapper>` (the
                     canon play jump-table slot re-pointed), the wrapper doing
                     the $D418 write then `JMP <real play body>` inside the
                     image (Scratch_It: play $7003 = JMP $82F0, wrapper $82F0 =
                     `LDA #$1F / STA $D418 / JMP $7085`).
    Returns imm, or None when the play entry isn't this shape."""
    mem, s = _load(path, post_init_sub)
    p = s['play']
    # (a) inline: PSID play IS the wrapper, exit `JMP base+3`.
    if (mem[p] == 0xA9 and bytes(mem[p + 2:p + 5]) == b'\x8d\x18\xd4'
            and mem[p + 5] == 0x4C
            and mem[p + 6] | (mem[p + 7] << 8) == base + 3):
        return mem[p + 1]
    # (b) indirect: PSID play is `JMP <wrapper>`; the wrapper does the $D418
    # write then `JMP <real play body>` (a valid in-image target, no self-loop).
    if mem[p] == 0x4C:
        w = mem[p + 1] | (mem[p + 2] << 8)
        lo, hi = s['load'], min(s['load'] + len(s['payload']), 0x10000)
        if (lo <= w and w + 8 <= hi and mem[w] == 0xA9
                and bytes(mem[w + 2:w + 5]) == b'\x8d\x18\xd4'
                and mem[w + 5] == 0x4C):
            tgt = mem[w + 6] | (mem[w + 7] << 8)
            if tgt != w and lo <= tgt < hi:
                return mem[w + 1]
    return None


def _d418_filter_tail_probe(path: str, base: int,
                            post_init_sub: 'int | None' = None):
    """Per-frame $D418 re-assert wedge (Groove class, ledger C19 -> C10
    master-vol-every-frame form): the PLAY-BODY global filter routine
    (`STA $D416 / LDA route / ORA res / STA $D417`, run every frame) has its
    `STA $D417` REPLACED by `JSR <wrapper>`, and the wrapper does
    `STA $D417 / LDA #mode / ORA mvol / STA $D418 / RTS` — so $D418 =
    filter-mode | master-vol is re-written EVERY frame; the canon filter
    note-init $D418 write is neutered (STA $D418 -> BIT $D418). Net
    write-stream: $D418 emitted once per frame at the END of the filter tail
    (after $D417), never at note-init. Returns the initial mode immediate (the
    wrapper's `LDA #imm` operand), or None (canonical: the play-body routine
    ends `STA $D417`).

    Anchored on the play-body filter routine specifically — `STA $D416`
    (fixed hardware addr, reloc-invariant) then the canonical
    `LDA abs / ORA abs` route+res computation, then a JSR at +9. This EXCLUDES
    stray `STA $D417 .. STA $D418` pairs in unrelated / init routines (which
    do not start with `STA $D416 / LDA abs / ORA abs`, e.g. Qbhead_01's $1CA8
    `STA $D416 / LDA #imm`)."""
    mem, s = _load(path, post_init_sub)
    lo, hi = s['load'], min(s['load'] + len(s['payload']), 0x10000)
    for a in range(lo, hi - 12):
        # play-body filter routine: STA $D416 / LDA abs / ORA abs / <op at +9>
        if not (mem[a] == 0x8D and mem[a + 1] == 0x16 and mem[a + 2] == 0xD4
                and mem[a + 3] == 0xAD and mem[a + 6] == 0x0D):
            continue
        if mem[a + 9] != 0x20:        # canonical ends STA $D417 ($8D) -> no wedge
            continue
        w = mem[a + 10] | (mem[a + 11] << 8)    # JSR <wrapper> target
        # wrapper: STA $D417 / LDA #imm / [ORA mvol] / STA $D418
        if not (w + 4 < 0x10000 and mem[w] == 0x8D and mem[w + 1] == 0x17
                and mem[w + 2] == 0xD4 and mem[w + 3] == 0xA9):
            continue
        imm = mem[w + 4]
        for b in range(w + 5, w + 9):
            if (mem[b] == 0x8D and mem[b + 1] == 0x18 and mem[b + 2] == 0xD4):
                return imm
    return None


def _play_unit_repeat_probe(path: str, base: int,
                            post_init_sub: 'int | None' = None):
    """Detect the DMC play-body 'double-speed unit' hack. The play body runs
    four units per frame — voice 0, voice 1, voice 2, then the global filter
    tail — and a hand-patch can redirect a per-voice JSR to a stub that calls
    the voice routine N times (a double-speed voice: its wave/pulse program
    advances N steps/frame, its full block emitted N times), optionally ending
    in a JMP back into the filter tail (which, via the leftover play-body JSR
    return address, re-runs the tail — $D416/$D417 written twice). Returns a
    '1,1,2,2'-style 4-int string [v0,v1,v2,filter] when any unit repeats > 1,
    else None (canonical single-pass — no param, byte-identical build).

    Static byte-probe (C19): follow the play vector, locate `STX fclaim`
    (base+$720), read the three per-voice JSR sites, and for a redirected site
    count the `JSR <voice>` inside the stub. Terminators: RTS (clean) or, on
    the LAST voice only, JMP <filter-tail> (sets the filter unit to 2). Any
    other stub shape returns None (unrecognised -> build unchanged)."""
    mem, s = _load(path, post_init_sub)
    p = s['play']
    if mem[p] != 0x4C:
        return None
    body = mem[p + 1] | (mem[p + 2] << 8)
    fclaim = base + 0x720
    stx = None
    a = body
    for _ in range(80):
        if a + 2 > 0xFFFF:        # scan ran off the 64K image: not a
            return None           # recognisable body — fail-open (no param)
        if mem[a] == 0x8E and (mem[a + 1] | (mem[a + 2] << 8)) == fclaim:
            stx = a
            break
        a += 1
    if stx is None:
        return None
    q = stx + 3
    x = 0                         # track X so a SKIPPED voice is visible:
    sites = []                    # (site_addr, target, voice) per JSR — the
    for _ in range(24):           # two-voice build (Two_Channels) inserts
        op = mem[q]               # INX before the first JSR, so voice 0 has
        if op == 0x20:            # NO site at all (unit count 0)
            sites.append((q, mem[q + 1] | (mem[q + 2] << 8), x)); q += 3
        elif op == 0xE8:          # INX = step to the next voice
            x += 1; q += 1
            if x > 2:
                break
        else:
            break
    if not sites or len(sites) > 3:
        return None
    vaddr = sites[0][1]
    filter_tail_addr = sites[-1][0] + 3  # the play body continues here
    filt = [1]                    # boxed so _count can bump the filter unit

    def _count(i, tgt):
        if tgt == vaddr:
            return 1
        a = tgt
        if mem[a] == 0xA2:               # optional `LDX #imm` re-assert
            if mem[a + 1] != i:          # must re-select THIS voice
                return None
            a += 2
        c = 0
        for _ in range(12):
            op = mem[a]
            if op == 0x20:               # JSR <unit>
                if (mem[a + 1] | (mem[a + 2] << 8)) != vaddr:
                    return None          # calls something else -> not this hack
                c += 1; a += 3
            elif op == 0x60:             # RTS = clean stub
                return c or None
            elif op == 0x4C:             # JMP = only the filter-tail re-entry
                if i == 2 and (mem[a + 1] | (mem[a + 2] << 8)) == filter_tail_addr:
                    filt[0] = 2
                    return c or None
                return None
            else:
                return None              # unrecognised stub shape
        return None

    reps = [0, 0, 0]                     # 0 = the voice has NO call site
    for _, t, vx in sites:
        c = _count(vx, t)
        if c is None:
            return None
        reps[vx] += c
    units = reps + filt
    if all(u == 1 for u in units):
        return None
    return ','.join(str(u) for u in units)


def _loop_target_probe(mem, base: int, strict: bool = False):
    """C19 STATIC opcode probe — does this player read the byte AFTER a track
    `$FF` as the loop POSITION (True) or always loop to 0 (False)?

    The canonical player stores the loop position inline (`STA base+$726,x`);
    the JSR-hook variant calls a 7-byte stub `INY / LDA (zp),y / STA
    base+$726,x / RTS` that fetches the next track byte first. The stub's
    ZEROPAGE track pointer is NOT a constant: a multi-SID chip-2 player is
    chip 1's copy with its own zp pair (Rayden's Disco_Zak uses `$F6` where
    chip 1 uses `$F8`), and the pointer is engine-internal — the composer
    picks its own — so accept any zp operand and key on the SHAPE.

    `strict` raises DMCV4Unsupported on an unrecognised site/hook (the
    canonical build's behaviour, where the masked identity compare is the
    real gate); otherwise an unknown site returns the canonical False.
    (The reset-all-to-0 JSR hook is classified on the dataflow path — see
    dataflow.locate.)
    """
    d = base - 0x1000
    site = _LOOP_SITE + d
    op = mem[site]
    if op == 0x9D and _rd16(mem, site + 1) == 0x1726 + d:
        return False                                 # canonical loop-to-0
    if op == 0x20:                                   # JSR hook
        hook = _rd16(mem, site + 1)
        if (mem[hook] == 0xC8 and mem[hook + 1] == 0xB1     # INY / LDA (zp),y
                and mem[hook + 3] == 0x9D                   # STA base+$726,x
                and _rd16(mem, hook + 4) == 0x1726 + d
                and mem[hook + 6] == 0x60):                 # RTS
            return True
        if strict:
            raise DMCV4Unsupported(
                'loop_hook_unknown', bytes(mem[hook:hook + 14]).hex())
        return False
    if strict:
        raise DMCV4Unsupported('loop_site_unknown',
                               bytes(mem[site:site + 3]).hex())
    return False


def _noteinit_defer_probe(path: str, subtune: int = 0) -> 'str | None':
    """OBSERVED note-init variant (C23 write-footprint rule — layout-blind,
    for RE-ASSEMBLED builds the static probes can't address). Classify each
    play() chunk per voice from the ORIGINAL's per-IRQ writelog
    (libsidplayfp ground truth): an INIT chunk writes both AD+SR with a
    value pair that is neither the $0F/$0F hard-restart prep nor the
    $00/$00 hold-clear. Canon note-init falls through the wave step, so an
    init chunk ALWAYS carries the voice's same-chunk CTRL write; the
    deferred-wave build (re-assembled Heinmueck player, Redable_Rain) RTSes
    first — AD/SR only, the note's freq/PW/ctrl land on the NEXT play().
    Cymbal (noise-burst) inits write freq+ctrl=$81 in BOTH variants (the
    composer's cym_ni path already bursts + RTSes), so cymbal chunks are
    excluded from the classification — BOTH the same-frame form (ctrl $81 +
    both freq bytes) AND the DEFERRED/SPLIT form where the $81 burst lands in a
    LATER frame while its AD/SR sat alone (an AD/SR-only chunk whose SAME
    voice's next ctrl write is $81 is a cymbal note, not a deferred melodic
    init — Wodnik/R1: all 8 of its AD/SR-only chunks land as $81 cymbals, so
    excluding them drops inits to 0 = the canon default it needs).
    `noteinit_defer_wave='1'` needs >= 2 MELODIC (non-cymbal) init chunks with
    FEWER THAN 20% carrying a ctrl write. A canon member's melodic inits always
    carry ctrl (ratio ~100%) AND its deferred cymbals are excluded, so it has
    ZERO qualifying chunks — the >= 2 is a SPARSITY floor (very-long-note defer
    members show only a couple of note-starts all song), not a confidence gate. The small ratio
    tolerance (not a strict ==0) absorbs the occasional per-IRQ BUCKETING
    COLLISION: two consecutive play()s in one capture bucket merge a deferred
    init's AD/SR with the NEXT play()'s wave-landing ctrl (Akademia: 46/47
    pure-defer, 1 merged bucket). The window ESCALATES to 30s when the 10s pass
    is inconclusive (inits < 8 AND with_ctrl == 0): a genuine defer member with
    LONG notes shows too few melodic inits in 10s (King_Leter: 2 in 10s, 13 in
    30s) so `inits >= 8` never trips; a canon member's inits carry ctrl
    (with_ctrl > 0) within 10s so it never escalates, and a cymbal-heavy member
    (R1) escalates to inits=0 (all excluded) so it still can't fire. The cymbal
    exclusion is what makes escalation regression-safe — WITHOUT it the escalation
    fired defer on R1/R2/R4/R5 (canon cymbal members, FULL without defer) and
    dropped them to 8.8% (the r170 regression this cymbal-following rule fixes).

    The SAME capture also classifies the hard-restart PREP chunks (AD=SR=
    $0F): the build writes ctrl $08 THEN $09 (TEST, then TEST|GATE) where
    canon writes $08 alone — `hr_prep_gate='1'` when > 80% of the (>= 8) prep
    chunks show the [$08, $09] ctrl SUBSEQUENCE. Two collision-tolerances vs
    the original strict all-or-nothing, both for the same per-IRQ BUCKETING
    COLLISION as `noteinit_defer_wave` (two play()s in one capture bucket):
    (1) the per-chunk test is a subsequence, not equality, so a merged chunk
    that PREPENDS the prior play()'s note ctrl ([$41,$08,$09]) still counts;
    (2) the aggregate is > 80%, not ==, absorbing the rare bucket that SPLITS
    the $08 and $09. Canon preps write $08 ALONE (0% show [$08,$09]), so a
    canon member is cleanly rejected and CANNOT flip — the two populations
    separate at 0% vs ~95-100% with a wide empty gap (measured across the
    whole Wodnik family + canon controls).

    Returns a (possibly empty) dict of composer params."""
    from pipelines.hubbard.verify_cycle import writelog_per_irq_capture

    def _count(frames):
        # per-frame per-voice register dicts (for the cymbal-following lookahead)
        fv = []
        for fr in frames:
            per = {}
            for _cyc, reg, val in fr:      # reg = $D4xx offset (0-$18)
                if 0 <= reg <= 0x14:
                    v, r = divmod(reg, 7)
                    per.setdefault(v, {})[r] = val
            fv.append(per)
        inits = with_ctrl = preps = preps_gate9 = 0
        for fi, fr in enumerate(frames):
            ctrls = {}
            for _cyc, reg, val in fr:
                if 0 <= reg <= 0x14 and reg % 7 == 4:
                    ctrls.setdefault(reg // 7, []).append(val)
            for v, regs in fv[fi].items():
                if 5 not in regs or 6 not in regs:
                    continue
                if (regs[5], regs[6]) == (0x0F, 0x0F):
                    preps += 1
                    # HR prep writes ctrl $08 THEN $09; test the [$08,$09]
                    # SUBSEQUENCE (a merged bucket prepends the prior play()'s
                    # note ctrl [$41,$08,$09], which a strict == misreads).
                    c = ctrls.get(v, [])
                    if any(c[i:i + 2] == [0x08, 0x09]
                           for i in range(len(c) - 1)):
                        preps_gate9 += 1
                    continue
                if (regs[5], regs[6]) == (0x00, 0x00):
                    continue
                if regs.get(4) == 0x81 and 0 in regs and 1 in regs:
                    continue               # cymbal burst — same-frame form
                if 4 not in regs:
                    # AD/SR-only: a DEFERRED/SPLIT cymbal note if this voice's
                    # NEXT ctrl write is a $81 burst (not a melodic wave-land).
                    cym = False
                    for fj in range(fi + 1, min(fi + 3, len(fv))):
                        nc = fv[fj].get(v, {})
                        if 4 in nc:
                            cym = (nc[4] == 0x81)
                            break
                    if cym:
                        continue
                inits += 1
                if 4 in regs:
                    with_ctrl += 1
        return inits, with_ctrl, preps, preps_gate9

    try:
        frames = writelog_per_irq_capture(path, subtune=subtune, duration=10.0)
    except Exception:
        return {}
    inits, with_ctrl, preps, preps_gate9 = _count(frames)
    # ESCALATE the window progressively while the pass is INCONCLUSIVE for defer
    # (< 2 melodic inits AND no ctrl-carrying = canon signal): a genuine defer
    # member with long held notes / a LATE melodic section shows too few (or
    # zero) melodic inits early — King_Leter has 2 in 10s, Lalamido reaches 2 by
    # 30s, Logarytm's melodic section starts ~43s (0 in 30s, 29 by 90s). Stop as
    # soon as decisive: inits >= 2 (fire) OR with_ctrl > 0 (a late CANON melodic
    # section — its inits carry ctrl, so it correctly never fires).
    for _dur in (30.0, 90.0):
        if not (inits < 2 and with_ctrl == 0):
            break
        try:
            inits, with_ctrl, preps, preps_gate9 = _count(
                writelog_per_irq_capture(path, subtune=subtune, duration=_dur))
        except Exception:
            break
    out = {}
    # >= 2 (not 8): after the cymbal exclusion a CANON member has ZERO non-cymbal
    # AD/SR-only inits (its melodic inits carry ctrl; its deferred cymbals are
    # excluded), so ANY such chunk is a genuine defer signal — the count is a
    # sparsity floor, not a confidence gate. Very-sparse defer members (long
    # held notes) exist: Lalamido has just 2 melodic inits in the whole song
    # (canon build 0.02%, defer 100%). `with_ctrl*5 < inits` still requires
    # with_ctrl==0 at inits 2-4 (one ctrl exceeds 20%), so a stray split cannot
    # fire. Census: 0 non-Wodnik/Heinmueck members fire at >=2 but not >=8.
    if inits >= 2 and with_ctrl * 5 < inits:   # < 20% carry ctrl (see docstring)
        out['noteinit_defer_wave'] = '1'
    if preps >= 8 and preps_gate9 * 5 > preps * 4:   # > 80% show [$08,$09]
        out['hr_prep_gate'] = '1'
    return out


def _drum_fhi_probe(path: str, base: int,
                    post_init_sub: 'int | None' = None):
    """Drum freq-hi REPOINT probe (C19 STATIC opcode probe). The absolute-freq
    wave step's hi store (canon $15FD `STA $1732,x` = fbh) is re-pointed at
    base+$754,x = pwh+1, the NEXT voice's pulse-width-hi running state: a
    drum step then zeroes fbl but leaves the voice's SID freq hi at the
    note's base value, while the wave table's freq byte pokes the next
    voice's PW hi. Anchored on the surrounding canon shape (`LDA #$00 / STA
    fbl,x / LDA abs,y / STA ...`) so a re-assembled layout can't false-fire.
    Returns '1' (the composer's `drum_fhi_to_pw` param) or None (canon /
    unknown repoint — canon behaviour, the verify verdict judges). Sole
    HVSC carrier: MUSICIANS/H/Heinmueck/Enforcer_2_Level_1_preview.sid."""
    mem, _ = _load(path, post_init_sub)
    if (mem[base + 0x5F5] != 0xA9 or mem[base + 0x5F6] != 0x00
            or mem[base + 0x5F7] != 0x9D
            or _rd16(mem, base + 0x5F8) != base + 0x72F
            or mem[base + 0x5FA] != 0xB9):
        return None
    site = base + 0x5FD
    if mem[site] != 0x9D:
        return None
    if _rd16(mem, site + 1) == base + 0x754:
        return '1'
    return None


def _switch_retrig_probe(mem, base: int) -> bool:
    """C19 STATIC opcode probe — the $7D (SWITCH) dispatch branch operand.

    Canon: `CMP #$7D / BEQ base+$183` (toggle the per-voice switch flag).
    The Dreck_Ist_Weg wedge re-points the BEQ to base+$158 — canon's own
    mode-0 glide tail `LDA base+$744,x / JMP base+$1A6` — so $7D becomes a
    FULL NOTE-INIT of the stored glide start note (the transpose add at
    base+$1A2 is skipped and the switch flag never toggles). Accept ONLY
    that exact target+tail; anything else keeps canon semantics (the
    masked identity compare / verify judge). Sole HVSC carrier:
    MUSICIANS/H/Heinmueck/Dreck_Ist_Weg.sid (family census 2026-07-27)."""
    d = base - 0x1000
    if bytes(mem[0x1129 + d:0x112C + d]) != b'\xC9\x7D\xF0':
        return False
    op = mem[0x112C + d]
    tgt = (0x112D + d + (op - 256 if op >= 128 else op)) & 0xFFFF
    h = 0x1158 + d
    return (tgt == h and mem[h] == 0xBD and _rd16(mem, h + 1) == 0x1744 + d
            and mem[h + 3] == 0x4C and _rd16(mem, h + 4) == 0x11A6 + d)


def _sid_header_multi(sid_path: str):
    """Read the PSID v3/v4 multi-SID header fields. Returns
    (n_chips, sid2_addr, sid3_addr, sid2_model, sid3_model). Addresses are
    full $Dxx0 chip bases (0 = chip absent); models are 6581/8580/'both' or
    None (Unknown = same as first SID, per the SID_file_format spec)."""
    with open(sid_path, 'rb') as f:
        h = f.read(0x7C)
    if len(h) < 0x7C or h[:4] not in (b'PSID', b'RSID'):
        return (1, 0, 0, None, None)
    flags = int.from_bytes(h[0x76:0x78], 'big')
    models = {0: None, 1: 6581, 2: 8580, 3: 'both'}

    def _addr(b):
        return (0xD000 + b * 0x10) if (b and b % 2 == 0
                                       and (0x42 <= b <= 0x7E
                                            or 0xE0 <= b <= 0xFE)) else 0
    a2, a3 = _addr(h[0x7A]), _addr(h[0x7B])
    n = 1 + (1 if a2 else 0) + (1 if a3 else 0)
    return (n, a2, a3, models[(flags >> 6) & 3], models[(flags >> 8) & 3])


def _config_at_base(sid_path: str, hvsc_root: str, base: int,
                    name: str, chip_addr: int = 0,
                    post_init_sub: 'int | None' = None) -> DMCV4Config:
    """Construct a DMCV4Config for a canonical/2entry DMC v4 player at a
    KNOWN base (used for multi-SID sub-players, where the dispatch wrapper
    overwrote one player's jump table so base-detection can't find it).

    A sub-player is an ORDINARY DMC player that happens not to own the PSID
    vectors — exactly what `_build_via_canon(base_override=)` was built for
    (C31's compilation members), so run the FULL canonical build first: it
    runs every knob probe (track_loop_target, hold_gateoff, hard_restart,
    the C19 wedge probes, rest_effects, cymbal ...) and the masked identity
    compare. Hand-rolling the config here instead silently defaulted all of
    them — the structural form of C9's "a second build path never measured
    the parameter" (Mc_Dieter's V2 track loops to a stated position, and the
    defaulted `track_loop_target=False` looped it to 0 instead).

    The bare fallback below keeps every member that the canonical build
    refuses (a wrapper-clobbered jump table, an unhandled sub-build variant)
    exactly as it built before — no member can regress to unsupported. All
    operand + fixed-table sites are canon-relative; the write-log verify is
    the gate on a mislocation."""
    try:
        cfg = _build_via_canon(sid_path, hvsc_root, base_override=base,
                               chip_addr=chip_addr,
                               post_init_sub=post_init_sub)
        cfg.name = name
        # `_build_via_canon` sits BELOW the caller that runs the C19 wedge
        # probes, so a sub-player built straight off it had every wedge knob
        # defaulted (see _apply_wedge_probes). Record the memory view (set by
        # dmc_v4_config, not by _build_via_canon) so every probe reads it, then
        # probe against THIS chip's base.
        cfg.post_init_sub = post_init_sub
        _apply_wedge_probes(os.path.join(hvsc_root, sid_path), cfg)
        return cfg
    except DMCV4Unsupported:
        pass
    d = base - 0x1000
    at = lambda a: a + d                                       # noqa: E731
    # The bare fallback still runs the STANDALONE static probes — a knob left
    # at its default here is silently wrong music, not a refusal (the track
    # loop target decides whether the song repeats its whole orderlist or the
    # tail from a stated position). A chip the init COPIES out of the file
    # image reads from that subtune's post-init RAM (ledger C26 + C31).
    mem = _load(os.path.join(hvsc_root, sid_path), post_init_sub)[0]
    cfg = DMCV4Config(
        sid_path=sid_path, name=name, base=base,
        op_instr=at(0x1227), op_wavectrl=at(0x159C), op_wavefreq=at(0x15B9),
        op_filtdef=at(0x1296), op_tunetab=at(0x180E),
        op_secp_lo=at(0x1103), op_secp_hi=at(0x1108),
        freq_lo_addr=at(0x1647), freq_hi_addr=at(0x16A7),
        vibdepth_addr=at(0x1888), d417_shadow_addr=at(0x1018),
        track_loop_target=_loop_target_probe(mem, base),
        switch_retrig=_switch_retrig_probe(mem, base))
    cfg.post_init_sub = post_init_sub
    _apply_wedge_probes(os.path.join(hvsc_root, sid_path), cfg)
    return cfg


def dmc_v4_config_2sid(sid_path: str, hvsc_root: str = 'hvsc85'):
    """Multi-SID (2SID/3SID) DMC member: a dispatch wrapper calls two/three
    independent DMC player instances, one per chip. Returns a list of
    per-chip DMCV4Config (chip order = wrapper JSR order = header chip
    order), or None if this isn't a multi-SID DMC member. The play vector
    at load is `JMP play_wrapper`; the play wrapper is a run of
    `JSR <player_play>` — each target names a player (base = target-3 when a
    jump table sits there, else the 2entry play handler at target-$50)."""
    path = os.path.join(hvsc_root, sid_path)
    n_chips = _sid_header_multi(path)[0]
    if n_chips < 2:
        return None
    mem, s = _load(path)
    # The static scan wants the wrapper's first call. `JMP wrapper` is the
    # common play vector; a wrapper that IS the play vector (a C18 phase
    # cycler inlined there) is scanned from the vector itself. Neither shape
    # is required — an unrecognised one just finds no calls and falls through
    # to the observation path below, which is the C18 answer to wrapper
    # variety. (play == 0 means the tune installs its own IRQ: nothing to
    # scan at all.)
    if not (s['load'] <= s['play'] < 0x10000):
        bases, a = [], None
    else:
        a = _rd16(mem, s['play'] + 1) if mem[s['play']] == 0x4C else s['play']
        bases = []
    # JSR <player play> ($20), or BIT ($2C) — the wrapper neuters a chip's
    # call by patching the opcode $20<->$2C per subtune (see
    # multisid_active_chips), so a member SAVED while a chip-only subtune was
    # selected ships that call as BIT. It still names its player (C19: never
    # assume the file-image state of a toggled byte).
    while a is not None and mem[a] in (0x20, 0x2C):
        t = _rd16(mem, a + 1)
        if t - 3 >= 0 and mem[t - 3] == 0x4C and mem[t] == 0x4C:
            bases.append(t - 3)                 # play = JT entry (base+3)
        else:
            bases.append(t - 0x50)              # direct 2entry play handler
        a += 3
    if len(bases) != n_chips:
        # The wrapper is not a plain run of calls — a C18 PHASE CYCLER can sit
        # in front of them (Rayden: an SMC counter at the play vector runs the
        # full play for both chips on one call and only each chip's per-voice
        # effects entry on the next). Shapes vary, so discover the players by
        # RUNNING the wrapper instead of parsing it (C18).
        bases = _observe_player_bases(path, n_chips)
        if bases is None:
            return None
    # A relocating init wrapper (ledger C26 + C31) copies players AND song
    # data into RAM. Surgeon/Mothafucka relocates chip 2's player to $E800
    # (zero-fill in the image) AND copies BOTH chips' sectors to $8000+ (also
    # zero-fill) — so chip 1's player is in the image but its DATA is not.
    # Extract EVERY chip from POST-INIT RAM whenever ANY chip's player is out
    # of the image (the tell that init relocates); reading the raw image would
    # decode the out-of-image data as zeros (garbage rows). The file's start
    # song materialises every chip's copy at init (the copy runs before any
    # per-subtune call gating), so it names the snapshot. When every player is
    # in the image (the common 2SID build), the raw image is used
    # (post_init_sub=None), byte-identical to before.
    matr_sub = max(0, s.get('start', 1) - 1)
    relocating = not all(mem[b] == 0x4C and mem[b + 3] == 0x4C for b in bases)
    psubs = [matr_sub if relocating else None for b in bases]
    # Every layer that reads memory for a relocated chip must use its post-init
    # view (locate + wedge probes via _config_at_base, keep-regs below). A chip
    # that is neither a valid in-image player NOR materialised in post-init RAM
    # is a shape this constructor can't extract — refuse and let the
    # single-chip fallback stand, rather than raising mid-extract.
    chip_mem = {b: (mem if ps is None else _load(path, ps)[0])
                for b, ps in zip(bases, psubs)}
    if not all(chip_mem[b][b] == 0x4C and chip_mem[b][b + 3] == 0x4C
               for b in bases):
        return None
    base0 = os.path.splitext(os.path.basename(sid_path))[0]
    addrs = [0xD400, _sid_header_multi(path)[1], _sid_header_multi(path)[2]]
    cfgs = [_config_at_base(sid_path, hvsc_root, b, f'{base0}_chip{i + 1}',
                            chip_addr=addrs[i], post_init_sub=psubs[i])
            for i, b in enumerate(bases)]
    # CIA multispeed (C9: measure, don't assume). The dispatch wrapper is
    # driven by the timer it programs at init, and a C18 phase schedule
    # DIVIDES that rate (Rayden: latch $2663 = 100Hz with a period-2 P_F123
    # schedule, or $1331 = 200Hz with period 4 — both a 50Hz music tick).
    # Built as vblank, such a member plays at 1/N speed: a per-chip EXACT
    # PREFIX of ~1/N the original's length, with no content divergence.
    cia = 0
    if s.get('speed', 0) & 1:
        cp = _cia_period_crosschecked(path, 0)
        if not (0x0100 <= cp <= 0xFFFF):
            cp = _cia_period_from_writelog(path, 0)
        if 0x0100 <= cp <= 0xFFFF:
            cia = cp
    for ci, cfg in enumerate(cfgs):
        cfg.cia_period = cia
        keep = _multisid_keep_regs(chip_mem[cfg.base], cfg.base, addrs[ci])
        if keep:
            cfg.extra_params['multisid_keep_regs'] = ','.join(keep)
    # C18: the wrapper may run the full play only every Nth call and dispatch
    # the others to each chip's effects entry. Observed per chip; the
    # composer's phase dispatcher then lives inside each player, so the chips
    # cycle in lockstep as the original does.
    obs = [_observe_play_phases_chip(path, cfg.base) for cfg in cfgs]
    # An 'S' (this chip's player is not entered at all this call) is normally
    # REFUSED: in the single-chip observer an S usually means py65 failed to
    # run an IRQ-armed effects call that the ground truth does run (C18's
    # "a silent phase may hide a register refresh"). Here it can be the real
    # shape — Surgeon's Cow_Anus_Fucked dispatches ONE chip per call
    # (`INC ctr / AND #$01 / BEQ ; JMP chip2play ; JMP chip1play`), so each
    # chip ticks at half the timer rate. Accept an S only on the structural
    # evidence that this is what the wrapper does: the chips' schedules are
    # COMPLEMENTARY — same period, and at every phase index exactly one chip
    # runs. A py65 shortfall cannot fake that (the same shortfall hits every
    # chip at the same index, leaving all of them S).
    scheds = [ph for ph, _ in obs]
    toks = [ph.split('_') if ph else [] for ph in scheds]
    complementary = (
        len(toks) > 1 and all(t for t in toks)
        and len({len(t) for t in toks}) == 1
        and all(sum(1 for t in toks if t[i] != 'S') == 1
                for i in range(len(toks[0]))))
    for cfg, (ph, deferred) in zip(cfgs, obs):
        if (ph and '_' in ph and 'P' in ph.split('_')
                and ('S' not in ph.split('_') or complementary)):
            cfg.extra_params['play_phases'] = ph
            if deferred:
                cfg.extra_params['noteinit_deferred'] = '1'
    return cfgs


def _observe_play_phases_chip(sid_path: str, base: int, subtune: int = 0,
                              n_calls: int = 12, max_steps: int = 200_000):
    """C18 phase schedule for ONE chip of a multi-SID member.

    The shared `_observe_play_phases` classifies by the canon frame entry
    (base+$1F9) and glide tail (base+$41C); Rayden's 2SID wrapper dispatches
    its effects calls to the WAVE-STEP entry (base+$591) instead, which that
    observer reads as 'S' (silent) and which its pc-trace fallback cannot
    disentangle for a multi-SID member (two players in one trace). Watching
    base+$591 here keeps the shared single-chip path byte-identical.

    A wave-step F entry sits PAST the note-init check, so a note fetched on a
    P call only ARMS on the F call and note-inits on the NEXT P — the C23
    2-frame note-start. Returns (schedule, noteinit_deferred).
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mpu = MPU()
    mem = ObservableMemory()
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    mpu.memory = mem
    deferred = [False]
    wavestep = [False]                     # per-call: base+$591 entered?

    def run(pc, acc):
        mpu.stPush(0x00)
        mpu.stPush(0x00)                   # RTS sentinel -> PC = $0001
        mpu.pc = pc
        mpu.a = acc
        hit_play = False
        fx = set()
        for _ in range(max_steps):
            if mpu.pc == 0x0001:
                return hit_play, fx
            if mpu.pc == base + 0x85:
                hit_play = True
            elif mpu.pc == base + 0x1F9:
                fx.add(mpu.x & 0x03)
            elif mpu.pc == base + 0x591:   # wave-step entry (C18 variant)
                fx.add(mpu.x & 0x03)
                wavestep[0] = True
            try:
                mpu.step()
            except Exception:
                return None
        return None

    if run(s['init'], subtune) is None:
        return (None, False)
    seq = []
    for _ in range(n_calls):
        wavestep[0] = False
        r = run(s['play'], 0)
        if r is None:
            return (None, False)
        hp, fx = r
        seq.append('P' if hp else
                   ('F' + ''.join(str(v + 1) for v in sorted(fx)) if fx
                    else 'S'))
        # The 2-frame arm is a property of the F CALL's entry point, so only
        # a wave-step entry on a call that did NOT run the play body means
        # it. A full play passes through base+$591 for every voice anyway —
        # keying on that alone set `deferred` for any member with a P call.
        if wavestep[0] and not hp:
            deferred[0] = True
    for p in range(1, n_calls // 2 + 1):
        if all(seq[i] == seq[i % p] for i in range(n_calls)):
            return ('_'.join(seq[:p]), deferred[0])
    return (None, False)


def _observe_player_bases(sid_path: str, n_chips: int,
                          max_steps: int = 400000):
    """Discover the per-chip player bases by RUNNING the dispatch wrapper.

    The static scan in `dmc_v4_config_2sid` reads a wrapper that is a plain
    run of `JSR <player play>`; when a C18 phase cycler sits in front of the
    per-chip calls the scan sees an `LDA #imm` and gives up. Rather than
    teach it each wrapper shape (C18: observe, never parse), run the member's
    init under py65 and collect the CALL targets that look like a DMC
    player's 2-entry JUMP TABLE: page-aligned (players are relocated to a
    page boundary — true of all known carriers) with `JMP` at both +0 and
    +3. First-seen order is the wrapper's call order = chip order.

    Two things widen what "call" and "when" mean, each as a LATER pass so a
    member the strict pass already resolves can never be pushed over the
    chip count by a looser one (zero-regression by construction):

    * JMP as well as JSR — an init that sets up chip 1 and TAIL-JUMPS into
      chip 2's init (Surgeon's Cow_Anus_Fucked: `JSR $1000 / LDA #$00 /
      JMP $3000`) reaches its second player by `JMP`.
    * a few PLAY calls as well as init — a wrapper can pick the player by
      SMC-patching its own call operand per call (Surgeon's Mothafucka:
      `INC imm / AND #$01 / TAX / LDA basehi,x / STA $0F16 / JSR $xx03`,
      alternating $1000 and $E800), so chip 2 is never named during init.
      Reading the operand at EXECUTION time sees whatever the patch left,
      which is the point — parsing the wrapper could not.

    Returns the base list, or None if it doesn't find exactly `n_chips`.
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    img = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            img[s['load'] + i] = b

    def _scan(call_ops, n_play=0):
        mpu = MPU()
        mem = ObservableMemory()
        for i, b in enumerate(s['payload']):
            if s['load'] + i < 0x10000:
                mem[s['load'] + i] = b
        mpu.memory = mem
        found = []

        def _run(pc, acc):
            mpu.stPush(0x00)
            mpu.stPush(0x00)               # RTS sentinel -> PC = $0001
            mpu.pc = pc
            mpu.a = acc
            for _ in range(max_steps):
                if mpu.pc == 0x0001:
                    return True
                if mem[mpu.pc] in call_ops:   # JSR abs (+ JMP abs on a retry)
                    t = mem[mpu.pc + 1] | (mem[mpu.pc + 2] << 8)
                    # Test the jump-table signature against LIVE memory, not
                    # the file image: an init can COPY a player to its run
                    # address (Surgeon/Mothafucka relocates chip 2 to $E800,
                    # which is zero-fill in the file — C26's "the data is not
                    # in the image" applied to the player itself). We are
                    # observing the machine, so read what the CPU would.
                    if not (t & 0xFF) and mem[t] == 0x4C \
                            and mem[t + 3] == 0x4C and t not in found:
                        found.append(t)
                try:
                    mpu.step()
                except Exception:
                    return False
            return False

        if not _run(s['init'], 0):
            return None
        for _ in range(n_play):
            if not (s['load'] <= s['play'] < 0x10000) or not _run(s['play'], 0):
                break
        return found if len(found) == n_chips else None

    return (_scan((0x20,)) or _scan((0x20, 0x4C))
            or _scan((0x20,), n_play=4) or _scan((0x20, 0x4C), n_play=4))


def multisid_active_chips(sid_path: str, bases, n_subtunes: int,
                          max_steps: int = 400000):
    """Which chips' players actually RUN, per subtune.

    A multi-SID dispatch wrapper may gate its per-chip calls on the subtune
    number — Rayden's 2SID builds ship subtune 0 = both chips, 1 = chip 1
    only, 2 = chip 2 only, by SMC-patching the four call opcodes $20 (JSR)
    <-> $2C (BIT). It also chooses the SONG each player is initialised with,
    independently of the PSID subtune (Rayden hardcodes `LDA #$00` before
    both calls, so each chip always plays its own song 0) — the multi-SID
    form of C31's per-subtune (player, song) map. Wrapper shapes vary, so
    per C18 this OBSERVES under py65 rather than parsing the wrapper: run
    init(sub) and play() twice, recording which player regions the PC enters
    and the A each player's init is entered with. The image is reloaded per
    subtune because the wrapper's patching is SMC.

    Returns a list (one per subtune) of {chip index: song number}, or None
    if observation fails (caller falls back to "every chip plays subtune s").
    """
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    # Watch each player's own ENTRY VECTORS, not an address RANGE: players
    # can sit less than a page apart and the dispatch wrapper itself can lie
    # inside a player's nominal page (Dark_Knight: players $E000/$EE00,
    # wrapper $FC00), so ranges both overlap each other and swallow the
    # wrapper — which reports every chip active in every subtune. Entry =
    # the jump-table slots (base, base+3), or the direct 2entry play handler
    # at base+$50 when there is no table (mirrors the wrapper scan above).
    img = bytearray(0x10000)
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            img[s['load'] + i] = b
    entries = []
    for b in bases:
        jt = img[b] == 0x4C and img[b + 3] == 0x4C
        entries.append((b, b + 3 if jt else b + 0x50))
    out = []
    for sub in range(n_subtunes):
        mpu = MPU()
        mem = ObservableMemory()
        for i, b in enumerate(s['payload']):
            if s['load'] + i < 0x10000:
                mem[s['load'] + i] = b
        mpu.memory = mem
        seen = {}

        def run(pc, acc, watch_song):
            mpu.stPush(0x00)
            mpu.stPush(0x00)               # RTS sentinel -> PC = $0001
            mpu.pc = pc
            mpu.a = acc
            for _ in range(max_steps):
                if mpu.pc == 0x0001:
                    return True
                for ci, (ini, ply) in enumerate(entries):
                    if mpu.pc == ini or mpu.pc == ply:
                        # A at the player's init vector = its song number
                        if watch_song and mpu.pc == ini and ci not in seen:
                            seen[ci] = mpu.a
                        seen.setdefault(ci, 0)
                try:
                    mpu.step()
                except Exception:
                    return False
            return False

        if not run(s['init'], sub, True):
            return None
        for _ in range(2):
            if not run(s['play'], 0, False):
                return None
        out.append(dict(seen))
    return out


# Canon SID-store sites -> the composer routine (label) that plays the same
# role. Used only to name a store when a register's stores are MIXED (some
# relocated to this chip, some not — C19's per-store granularity trap): the
# composer re-architects the player, so a store is identified by what its
# block DOES, never by an address. Extend a row at a time, and only when the
# composer's label is unambiguously the same role — an unmapped site falls
# back to relocating the whole register (today's behaviour).
_SIDSTORE_ROLE = {
    0x130C: 'cymburst',    # STA $D400,y — noise-attack burst freq lo ($FFFF)
    0x130F: 'cymburst',    # STA $D401,y — noise-attack burst freq hi
    0x1314: 'cymburst',    # STA $D404,y — noise-attack burst ctrl ($81)
    0x160D: 'sidwrite',    # STA $D400,y — voice freq lo (base + accum)
    0x1616: 'sidwrite',    # STA $D401,y — voice freq hi
    0x161C: 'pwwrite',     # STA $D402,y — pulse width lo
    0x1622: 'pwwrite',     # STA $D403,y — pulse width hi
    0x162B: 'pwwrite',     # STA $D404,y — waveform ctrl (gate-masked)
}


def _multisid_keep_regs(mem, base: int, chip_addr: int) -> tuple:
    """C19 STATIC opcode probe — which SID registers this chip's player still
    stores to CHIP 1 because the 2SID relocation missed their operand.

    The editor builds chip 2/3's player by copying chip 1's and adding the
    chip offset to every `$D4xx` store operand. Some builds miss one
    (Surgeon/Nice_Dream: the res/route `STA $D417`), so that write lands on
    chip 1 for BOTH players — a real write-stream difference we must
    reproduce. Read the operands rather than assuming either way: the
    default is a FULLY relocated player (what most builds produce).

    Returns the registers ALL of whose stores are un-relocated. A register
    with a MIX (some stores relocated, some not — Nice_Dream's `$D401`, 1 of
    3) is not representable at register granularity and is skipped: the
    composer relocates it, matching the pre-probe behaviour. Note the chip's
    real address is only used to classify the operands; the composer still
    standardises chip k to $D400+k*$20 (C27) and the verdict is chip-tagged.
    """
    if not chip_addr or chip_addr == 0xD400:
        return ()
    body = bytes(mem[base:base + 0x1000])
    own = [0] * 0x19
    foreign = [0] * 0x19
    foreign_at = {}                    # reg -> [canon offset, ...]
    # STA abs ($8D) / STA abs,y ($99) / STA abs,x ($9D)
    for i in range(len(body) - 2):
        if body[i] not in (0x8D, 0x99, 0x9D):
            continue
        tgt = body[i + 1] | (body[i + 2] << 8)
        if 0xD400 <= tgt <= 0xD418:
            foreign[tgt - 0xD400] += 1
            foreign_at.setdefault(tgt - 0xD400, []).append(0x1000 + i)
        elif chip_addr <= tgt <= chip_addr + 0x18:
            own[tgt - chip_addr] += 1
    keep = [f'%02X' % r for r in range(0x19) if foreign[r] and not own[r]]
    # MIXED register (some stores relocated, some not) — name the specific
    # canon SITE by the composer ROUTINE that plays its role, so the composer
    # can keep just that store on chip 1. Only sites in _SIDSTORE_ROLE are
    # nameable; anything else keeps the old behaviour (relocate the register
    # wholesale, member stays partial) rather than guessing at a role.
    for r in range(0x19):
        if not (foreign[r] and own[r]):
            continue
        roles = {_SIDSTORE_ROLE.get(a) for a in foreign_at[r]}
        if None not in roles:
            keep += ['%02X@%s' % (r, role) for role in sorted(roles)]
    return tuple(keep)


# C19 static-opcode wedge probes with a UNIFORM shape: probe(path, cfg) returns
# the param value or None; a non-None result is written verbatim to
# cfg.extra_params[key]. This is the C19 canonical form (static-opcode-probe ->
# extra_params key) factored out of the per-probe copy-paste in dmc_v4_config —
# a new uniform wedge is ONE row here, not a new dispatch stanza. The NON-uniform
# stanzas stay explicit in dmc_v4_config: cymbal_burst (!= $FF guard), hr_patch
# (two keys), the hard_restart precedence block, and forced_subtune (a cfg
# attribute, not a param). Insertion order is irrelevant — the USF writer sorts
# param keys and the composer reads them by name.
# Every probe is handed `c.post_init_sub` so it reads the SAME memory view the
# rest of the build used. A RELOCATED compilation player (ledger C31) is absent
# from the file image at `c.base` — probing the image there reads zeros, so
# every wedge would come back defaulted: C9's "a second build path never
# measured the parameter", one layer further out than round 83b closed it.
def _play_repeat_parity_probe(path: str, base: int,
                              post_init_sub: 'int | None' = None):
    """Alternating whole-play repeat via a PARITY wrapper (C24 sibling). Two
    shapes, both a parity counter dispatching a SINGLE vs a MULTI play per IRQ:
      A (r135, Bajerek): `INC zp / LDA zp / LSR / BCS +3 / JSR T / JMP T` —
        odd = 2 body-runs (1 JSR + JMP), so 3 runs per 2 IRQs (1/2 alternation).
      B (r161, Vegeta/Heniek): `LDA #imm / INC abs(==play+1) / AND #$01 /
        BEQ +N / (JSR T)* / JMP T` — the SMC immediate at play+1 IS the parity
        counter; even = single play (BEQ -> JMP T), odd = k JSR T + JMP T =
        (k+1) body-runs (Heniek k=2 -> 1/3 alternation, an avg-2x tune).
    The factory forces play_repeat=1 for CIA members and the C18 reachability
    observer sees only 'P' phases, so the doubling was invisible. Static shape
    gate → the MULTI count from the JSR count; then OBSERVE which parity is
    multi from the orig's per-IRQ write counts (the phase counter seeds so
    call #1 executes tokens[0], so tokens[0] = play #0's class). Returns a
    play_phases schedule ('P2_P'/'P_P2'/'P_P3'/...) or None. Follows a JMP at
    the play vector to the wrapper body."""
    mem, s = _load(path, post_init_sub)
    play = s['play']
    if mem[play] == 0x4C:                  # JMP wrapper (Heniek: $0FD3 -> $0FE8)
        play = mem[play + 1] | (mem[play + 2] << 8)
    if not (0 <= play and play + 24 < 0x10000):
        return None
    multi = None
    # SHAPE A (Bajerek): INC zp / LDA zp / LSR / BCS +3 / JSR T / JMP T.
    w = bytes(mem[play:play + 13])
    if (w[0] == 0xE6 and w[2] == 0xA5 and w[1] == w[3] and w[4] == 0x4A
            and w[5] == 0xB0 and w[6] == 0x03 and w[7] == 0x20 and w[10] == 0x4C
            and (w[8] | (w[9] << 8)) == (mem[play + 11] | (mem[play + 12] << 8))
            and base <= (w[8] | (w[9] << 8)) < base + 0x1000):
        multi = 2
    # SHAPE B (Heniek): LDA #imm / INC abs(==play+1) / AND #$01 / BEQ +N /
    # (JSR T)* / JMP T. The BEQ (even) path is a bare JMP T = 1 body.
    if multi is None and (mem[play] == 0xA9 and mem[play + 2] == 0xEE
            and (mem[play + 3] | (mem[play + 4] << 8)) == play + 1
            and mem[play + 5] == 0x29 and mem[play + 6] == 0x01
            and mem[play + 7] == 0xF0):
        beq = play + 9 + mem[play + 8]           # BEQ (relative) target
        i, njsr, T = play + 9, 0, None
        while mem[i] == 0x20:                     # count consecutive JSR T
            tgt = mem[i + 1] | (mem[i + 2] << 8)
            if T is None:
                T = tgt
            if tgt != T:
                break
            njsr += 1
            i += 3
        if (njsr >= 1 and mem[i] == 0x4C and (mem[i + 1] | (mem[i + 2] << 8)) == T
                and 0 <= beq and mem[beq] == 0x4C
                and (mem[beq + 1] | (mem[beq + 2] << 8)) == T
                and base <= T < base + 0x1000):
            multi = njsr + 1                      # k JSR + the JMP
    if multi is None:
        return None
    # observe the doubling parity from the ground-truth per-IRQ capture
    # (one chunk per play() — the per-frame debug nwrites can't split a
    # multi-entry frame)
    import statistics
    try:
        from pipelines.hubbard.verify_cycle import writelog_per_irq_capture
        cap = writelog_per_irq_capture(path, subtune=0, duration=8,
                                       keep_init=False)
    except Exception:
        return None
    counts = [len(fr) for fr in cap]
    if len(counts) < 60:
        return None
    # parity classes relative to play index 0 (skip the init-transient head)
    even_med = statistics.median([c for i, c in enumerate(counts[20:], 20)
                                  if i % 2 == 0])
    odd_med = statistics.median([c for i, c in enumerate(counts[20:], 20)
                                 if i % 2 == 1])
    hi, lo = max(even_med, odd_med), min(even_med, odd_med)
    # require a clear parity split roughly consistent with the static MULTI
    # count (single ~= 1 body, multi ~= `multi` bodies), so a mis-parsed shape
    # can't mint a schedule (build+verify is the final gate regardless).
    if lo <= 0 or hi / lo < max(1.6, multi - 0.9):
        return None
    hi_tok = 'P%d' % multi
    return hi_tok + '_P' if even_med > odd_med else 'P_' + hi_tok


def _play_repeat_counter_probe(path: str, base: int,
                               post_init_sub: 'int | None' = None):
    """Whole-play N-repeat via a periodic-COUNTER wrapper (C24 sibling of the
    parity probe). The play vector runs the full play body BASE times per IRQ,
    plus ONE (or more) extra body call every (M+1)th IRQ — a mod-(M+1) resync
    counter (Vegeta/Trzewiki: 4 bodies normally, 5 every 41st frame -> avg
    4.024x, the length-tail cause):

        LDA cz / CMP #M / BNE skip
        LDA #$FF / STA cz / (JSR T)+        ; special: +extra bodies, cz -> $FF
    skip: INC cz                            ; the counter increments each IRQ
        (JSR T)* / JMP T                    ; BASE = njsr + 1 body calls

    cz cycles 0..M (M+1 values); the special fires at cz==M (the LAST frame of
    the period) and forces cz=$FF so INC lands on 0 -> a UNIFORM period M+1. So
    the schedule is M x P{BASE} + 1 x P{BASE+extra} (period M+1), aligned with
    the composer's phasectr seed (init sets cz=0, play #0 reads cz=0 = phase 0).
    Fully STATIC (unlike the parity shape, WHICH frame is multi is deterministic
    from the CMP, so no per-IRQ observation is needed); build+verify is the
    final gate. Returns the schedule ('P4_...P4_P5') or None. Follows one JMP at
    the play vector."""
    mem, s = _load(path, post_init_sub)
    play = s['play']
    if mem[play] == 0x4C:                        # follow a JMP wrapper
        play = mem[play + 1] | (mem[play + 2] << 8)
    if not (0 <= play and play + 24 < 0x10000):
        return None
    # head: LDA cz / CMP #M / BNE rel
    if not (mem[play] == 0xA5 and mem[play + 2] == 0xC9 and mem[play + 4] == 0xD0):
        return None
    cz = mem[play + 1]
    M = mem[play + 3]
    if not (2 <= M + 1 <= 255):                  # phasetab byte count / cpy #imm
        return None
    skip = play + 6 + mem[play + 5]              # BNE target (past the special)
    # special block: LDA #$FF / STA cz / (JSR T)+ ... falling through to `skip`
    if not (mem[play + 6] == 0xA9 and mem[play + 7] == 0xFF
            and mem[play + 8] == 0x85 and mem[play + 9] == cz):
        return None
    T = None
    i, extra = play + 10, 0
    while i + 2 < skip and mem[i] == 0x20:       # count the special's extra JSRs
        t = mem[i + 1] | (mem[i + 2] << 8)
        if T is None:
            T = t
        elif t != T:
            return None
        extra += 1
        i += 3
    if extra < 1 or i != skip:                   # special must end exactly at skip
        return None
    # skip = INC cz, then the BASE body: (JSR T)* / JMP T
    if not (mem[skip] == 0xE6 and mem[skip + 1] == cz):
        return None
    i, njsr = skip + 2, 0
    while mem[i] == 0x20:                         # BASE-1 consecutive JSR T
        if (mem[i + 1] | (mem[i + 2] << 8)) != T:
            return None
        njsr += 1
        i += 3
    if not (mem[i] == 0x4C and (mem[i + 1] | (mem[i + 2] << 8)) == T):
        return None                              # ... terminated by JMP T
    base_rep = njsr + 1
    if base_rep < 2 or not (base <= T < base + 0x1000):
        return None
    lo_tok = 'P' if base_rep == 1 else 'P%d' % base_rep
    hi_tok = 'P%d' % (base_rep + extra)
    return '_'.join([lo_tok] * M + [hi_tok])


def _pw_base_read_probe(path: str, base: int,
                        post_init_sub: 'int | None' = None):
    """Pulse-step BASE read re-pointed into SID-MIRROR space (C19,
    Mathematica_tune_3): canon $1376 `ADC $175F,X` patched to `ADC $D75F,X`
    — X=0 reads ENV3, X=1/2 read write-only SID mirrors (the decayed bus).
    Probe the canon site's operand; fire ONLY when it points into the SID
    address space ($D400-$D7FF): hardware-stable and layout-independent, so
    the composer reproduces the exact absolute read. Any other repoint
    target (a RAM var in the ORIG's layout) is NOT reproducible verbatim
    and keeps the default (member stays partial, honest residue)."""
    mem, s = _load(path, post_init_sub)
    site = base + 0x376
    if mem[site] != 0x7D:                 # ADC abs,X intact
        return None
    op = mem[site + 1] | (mem[site + 2] << 8)
    if op == (base + 0x75F) & 0xFFFF:     # canon
        return None
    if not 0xD400 <= op <= 0xD7FC:        # SID space only (see docstring)
        return None
    return f'{op:04X}'


def _cia_rearm_probe(path: str, base: int,
                     post_init_sub: 'int | None' = None):
    """Reproduce the play VECTOR's per-play CIA1 timer-A latch RE-ARM (C25
    mirrored class — PVCF octa-multispeed Strange_Acidshit + the re-arming DMC
    family). The orig play vector writes BOTH $DC04 and $DC05 (the SAME latch
    it set at init, ~12 cyc) before the body EVERY call; our composer sets the
    latch once at init, so our body runs ~12 cyc/play FASTER -> a small length
    OVERSHOOT (out of the CIA tolerance under an extreme latch like Strange's
    8x, comfortably inside it elsewhere). Reproducing the re-arm carries the
    same per-play cost, matching orig's effective rate. Returns 1 iff the play
    vector (following one JMP) writes both $DC04 and $DC05 before its body JMP,
    on a CIA-timed member; else None.

    GATED ON MEASURED OVERRUN — the re-arm is beneficial ONLY when orig's play
    body OVERRUNS its latch (effective period > latch+1). Then orig runs slower
    than the latch rate and our clean, lighter body is FASTER (overshoot), so
    the re-arm closes the gap. When orig FITS its latch and OUR body is the
    heavier one (undershoot — e.g. Moog/Compozak, overrun 0.9986, our body
    slower), the re-arm would WORSEN the match, so we DON'T fire. This is the
    C9 'measure, don't guess' reflex: the static shape says the orig re-arms,
    the measurement says whether reproducing it helps. Verified: firing on the
    overrunning members closed 22/22 tested re-arming builds toward orig (0
    regressed); Compozak (non-overrunning) is correctly left alone."""
    mem, s = _load(path, post_init_sub)
    if not (s.get('speed', 0) & 1):        # CIA-driven subtune 0 only
        return None
    p = s['play']
    if p and mem[p] == 0x4C:               # follow one JMP into the wrapper
        p = mem[p + 1] | (mem[p + 2] << 8)
    lo = hi = imm = None
    a = p
    for _ in range(24):                    # play vector must re-arm the latch,
        if not (0 <= a <= 0xFFFC):         # capturing its immediate lo/hi
            break
        op = mem[a]
        if op == 0xA9:                     # LDA #imm
            imm = mem[a + 1]
            a += 2
        elif op == 0x8D:                   # STA abs
            addr = mem[a + 1] | (mem[a + 2] << 8)
            if addr == 0xDC04:
                lo = imm
            elif addr == 0xDC05:
                hi = imm
            a += 3
        elif op == 0x4C:                   # JMP -> body: stop before the body
            break
        else:
            a += 1
    if lo is None or hi is None:           # not a both-bytes latch re-arm
        return None
    latch = lo | (hi << 8)
    if latch == 0:
        return None
    period = _measure_play_period(path, 0)                 # failing sub 0
    if period is None or period <= (latch + 1) * 1.0015:   # orig must OVERRUN
        return None
    return 1


def _measure_play_period(sid_path: str, subtune: int, dur: float = 4.0):
    """Orig's effective play-entry period in CPU cycles (ground truth): sum the
    per-play write-log buckets' entry counts over the absolute PHI1 cycle span
    (`--writelog-per-irq --per-irq-debug`). Returns cycles/play, or None."""
    import subprocess
    import re
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                      'tools', 'siddump')
    try:
        out = subprocess.run(
            [sd, sid_path, '--writelog-per-irq', '--per-irq-debug',
             '--duration', str(dur), '--subtune', str(subtune + 1)],
            capture_output=True, text=True, timeout=90).stderr
    except Exception:
        return None
    fr = [(int(m.group(1)), int(m.group(2))) for m in
          re.finditer(r'frame=\d+ base=(\d+) nentries=(\d+)', out)]
    if len(fr) < 20:
        return None
    total = sum(f[1] for f in fr)
    span = fr[-1][0] - fr[0][0]
    return span / total if total and span > 0 else None


def _filter_cut_from_fbase_probe(path: str, base: int,
                                 post_init_sub: 'int | None' = None):
    """Filter-tail cutoff LOAD operand repointed fcut->fbase (STATIC opcode
    probe, C19 — Zyron/One_Man_and_Boris). The canon filter tail at base+$A0 is
    `AD 1C 17` = `LDA $171C` (fcut, the swept cutoff) `/ STA $D416`; the wedge
    repoints the operand one byte down to `AD 1B 17` = `LDA $171B` (fbase = the
    filter-def base index def#<<4), so $D416 sources the def index, not the
    cutoff. Anchor the exact canon site (LDA abs at base+$A0 immediately
    followed by `STA $D416`) and require the operand == base+$71B. Return '1'.
    Regression-safe: the canon fcut operand returns None -> byte-identical."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    site = base + 0xA0
    if site + 5 > 0x10000:
        return None
    if mem[site] != 0xAD:                          # LDA abs
        return None
    # must be the filter-cutoff tail: LDA abs / STA $D416
    if not (mem[site + 3] == 0x8D and
            (mem[site + 4] | (mem[site + 5] << 8)) == 0xD416):
        return None
    operand = mem[site + 1] | (mem[site + 2] << 8)
    if operand == (base + 0x71B) & 0xFFFF:         # fbase (canon fcut = +$71C)
        return '1'
    return None


_WEDGE_PROBES = [
    ('play_phases',                     lambda p, c: (_play_repeat_parity_probe(p, c.base, c.post_init_sub)
                                                      or _play_repeat_counter_probe(p, c.base, c.post_init_sub))),
    ('cia_rearm_per_play',              lambda p, c: _cia_rearm_probe(p, c.base, c.post_init_sub)),
    ('pw_base_sid_read',                lambda p, c: _pw_base_read_probe(p, c.base, c.post_init_sub)),
    ('master_vol_every_play',           lambda p, c: _d418_play_wrapper(p, c.base, c.post_init_sub)),
    ('master_vol_reassert_filter_tail', lambda p, c: _d418_filter_tail_probe(p, c.base, c.post_init_sub)),
    ('hold_gateoff',                    lambda p, c: _hold_gateoff_probe(p, c.base, c.post_init_sub)),
    ('note_guard_init',                 lambda p, c: _note_guard_probe(p, c.base, c.post_init_sub)),
    ('pw_up_reverse',                   lambda p, c: _pw_up_reverse_probe(p, c.base, c.post_init_sub)),
    ('master_vol_static',               lambda p, c: _master_vol_static_probe(p, c.base, c.post_init_sub)),
    ('filter_static',                   lambda p, c: _filter_static_probe(p, c.base, c.post_init_sub)),
    ('master_vol_fade',                 lambda p, c: _master_vol_fade_probe(p, c.base, c.post_init_sub)),
    ('play_unit_repeat',                lambda p, c: _play_unit_repeat_probe(p, c.base, c.post_init_sub)),
    ('pulsewidth_hi_const',             lambda p, c: _pw_hi_const_probe(p, c.base, c.post_init_sub)),
    ('dual_freq_generator',             lambda p, c: _dual_freq_gen_probe(p, c.base, c.freq_lo_addr, c.post_init_sub)),
    ('filter_mod',                      lambda p, c: _filter_mod_probe(p, c.op_filtdef, c.post_init_sub)
                                            or _filter_mod_multi_probe(p, c.base, c.op_filtdef, c.post_init_sub)),
    ('pw_bound_shift',                  lambda p, c: _pw_bound_shift_probe(p, c.base, c.post_init_sub)),
    ('pulsewidth_dir_persist',          lambda p, c: _pw_dir_persist_probe(p, c.base, c.post_init_sub)),
    ('switch_toggle_mask',              lambda p, c: _switch_toggle_mask_probe(p, c.base, c.gatemask_addr, c.post_init_sub)),
    ('glide_neutered',                  lambda p, c: _glide_neutered_probe(p, c.base, c.post_init_sub)),
    ('drum_fhi_to_pw',                  lambda p, c: _drum_fhi_probe(p, c.base, c.post_init_sub)),
    ('route_clear_dead',                lambda p, c: _route_clear_dead_probe(p, c.base, c.post_init_sub)),
    ('fclaim_clear_dead',               lambda p, c: _fclaim_clear_dead_probe(p, c.base, c.post_init_sub)),
    ('track_ff_reinit',                 lambda p, c: _track_ff_reinit_probe(p, c.base, c.post_init_sub)),
    ('track_ff_reinit_ghost',           lambda p, c: _track_ff_reinit_ghost_probe(p, c.base, c.post_init_sub)),
    ('track_fe_reset',                  lambda p, c: _track_fe_reset_probe(p, c.base, c.post_init_sub)),
    ('track_loop_dead',                 lambda p, c: _track_loop_dead_probe(p, c.base, c.post_init_sub)),
    ('v3_instr_tempo',                  lambda p, c: _v3_instr_tempo_probe(p, c.base, c.post_init_sub)),
    ('filterdef_anim',                  lambda p, c: _filterdef_anim_probe(p, c.base, c.op_filtdef, c.post_init_sub)),
    ('d417_tail_anim',                  lambda p, c: _d417_tail_anim_probe(p, c.base, c.op_filtdef, c.op_wavefreq, c.post_init_sub)),
    ('filterdef_anim3',                 lambda p, c: _filterdef_anim3_probe(p, c.base, c.op_filtdef, c.post_init_sub)),
    ('filter_cut_from_fbase',           lambda p, c: _filter_cut_from_fbase_probe(p, c.base, c.post_init_sub)),
]


def _apply_wedge_probes(path: str, cfg) -> None:
    """Run the uniform C19 wedge probes and record what they find on `cfg`.

    Called by BOTH constructors. `dmc_v4_config` is the obvious one; the other
    is `_config_at_base`, the multi-SID sub-player constructor, which reaches
    the canonical build through `_build_via_canon` — one layer BELOW this loop,
    so it used to return a config with every wedge knob defaulted. That is
    C9's "a second build path never measured the parameter" recurring at a
    finer grain than round 81 caught: r81 made sub-players run the canonical
    build, which fixed the table/layout probes, but the wedge probes live out
    here in the caller. Nice_Dream_2SID carries the hold_gateoff wedge on BOTH
    chips ($17EC and $37EC) and got neither, so its stored .usf specified a
    build that verifies partial while the batch's write-stream retry quietly
    supplied the missing param at verify time (ledger C20 / the Principle §8:
    a rebuild must not need information absent from the USF)."""
    for key, probe in _WEDGE_PROBES:
        v = probe(path, cfg)
        if v is not None:
            cfg.extra_params[key] = v
    # SONG-END REST before the repeat (ledger C38 sibling) — a CONFIG field
    # rather than an extra_param, because it becomes typed USF content
    # (MusicSubtune.song_restart_gap), not a composer knob. Cheap static gate
    # inside the probe; only a real carrier pays for the measurement.
    try:
        import tools.seed_disassembly as _sd
        _n = _sd.parse_psid(path).get('songs', 1)
    except Exception:
        _n = 1
    _m = {}
    for _sub in range(_n):
        _g = _song_restart_gap_probe(path, cfg.base, post_init_sub=_sub)
        if _g:
            _m[_sub] = _g
    if _m:
        cfg.song_restart_gap = _m


def _durrel_ramp_probe(path: str, base: int,
                       post_sub: 'int | None' = None) -> 'list | None':
    """Rayden's custom global duration-ramp driver (ledger C19). A non-canon
    routine cycles a 4-entry table and writes the value to ALL three voices'
    durrel ($173E/$173F/$1740, base-relocated) on each V1 note-advance, so the
    per-note duration becomes a GLOBAL period-4 beat instead of the canon
    per-voice $80-$BF command. Static-opcode probe: the three consecutive
    `STA durrel_v,abs` stores are the signature (canon writes durrel via
    `STA $173E,X`, never three absolute stores); the table is the operand of the
    `LDA table,X` that loads the value just before them. Returns the 4-entry
    duration table, or None. The extract deconstructs it to per-row durations
    (see engine_model.extract); nothing here reaches the composer."""
    mem, _ = _load(path, post_sub)
    d = base - 0x1000
    a0, a1, a2 = 0x173E + d, 0x173F + d, 0x1740 + d
    sig = bytes([0x8D, a0 & 0xFF, a0 >> 8,
                 0x8D, a1 & 0xFF, a1 >> 8,
                 0x8D, a2 & 0xFF, a2 >> 8])
    i = bytes(mem).find(sig)
    if i < 0:
        return None
    tbl = None
    for p in range(max(0, i - 16), i):
        if mem[p] == 0xBD:                       # LDA abs,X (reads the table)
            tbl = mem[p + 1] | (mem[p + 2] << 8)
    if tbl is None:
        return None
    return [mem[(tbl + k) & 0xFFFF] for k in range(4)]


def dmc_v4_config(sid_path: str, hvsc_root: str = 'hvsc85',
                  base_override: 'int | None' = None,
                  post_init_sub: 'int | None' = None) -> DMCV4Config:
    """Primary canonical-layout build; on a moved-layout rejection, fall back
    to the layout-independent dataflow extractor (pipelines.dmc.v4.dataflow).

    `base_override` FORCES the player base (bypasses auto-detection + the
    dataflow fallback) — used to extract one player of a COMPILATION member
    (ledger C31), where several independent players share the file behind a
    per-subtune dispatch wrapper and auto-detection can't pick the right one.

    `post_init_sub` names the 0-based subtune whose init MATERIALISES that
    player: a relocating compilation wrapper COPIES its players into RAM, so
    the one at `base_override` is not in the file image at all. Every memory
    read of this build — locate, every probe, and the extract — then uses that
    subtune's post-init RAM instead of the image (ledger C31 + C26).

    hold_gateoff: the STATIC opcode probe (_hold_gateoff_probe) detects the
    1-byte sub_17EC patch ($17EF BC->60 = mask_only) directly — it reads the
    patched instruction, so it cannot false-negative on late-gate-off members
    (unlike a bounded write-stream scan). The verify batch's frames_clear_adsr
    mask_only retry remains as the fallback for shapes the probe misses."""
    if base_override is not None:
        # forced player of a compilation. Try the canon path first (uniform
        # relocation — e.g. Abyssal_Karma); on a code-identity mismatch fall
        # back to the signature-based dataflow locate, which handles the
        # NON-uniformly-relocated players (the packer moves the state scratch
        # independently of the code — most compilations, ledger C31).
        try:
            cfg = _build_via_canon(sid_path, hvsc_root,
                                   base_override=base_override,
                                   post_init_sub=post_init_sub)
        except DMCV4Unsupported:
            cfg = _build_via_dataflow(sid_path, hvsc_root,
                                      base_override=base_override,
                                      post_init_sub=post_init_sub)
            if cfg is None:
                raise
    else:
        try:
            cfg = _build_via_canon(sid_path, hvsc_root)
        except DMCV4Unsupported as e:
            if e.reason not in _DATAFLOW_RETRY:
                raise
            cfg = _build_via_dataflow(sid_path, hvsc_root)
            if cfg is None:
                raise
    # Recorded BEFORE the probes run: they read the memory view it names.
    cfg.post_init_sub = post_init_sub
    path = os.path.join(hvsc_root, sid_path)
    # --- non-uniform wedge stanzas (special guard / two keys / attribute) ---
    # negative-transpose ADC immediate (C19 wedge, r136 — the $80-$9F
    # transpose branch `EOR #$1F / ADC #imm / STA base+$72C,x`; canon #$01).
    # Anchored on the EOR/ADC/STA shape with the relocation-aware operand.
    _mem0, _ = _load(path, post_init_sub)
    _tb = cfg.base + 0x72C
    _pat = re.compile(rb'\x49\x1f\x69(.)\x9d'
                      + re.escape(bytes([_tb & 0xFF, _tb >> 8])), re.DOTALL)
    _m = _pat.search(bytes(_mem0))
    if _m and _m.group(1)[0] != 0x01:
        cfg.transpose_neg_bias = _m.group(1)[0]
    # cymbal noise-burst timbre / attack ctrl: only when patched off the
    # canon ($FF, $81).
    cb = _cymbal_burst_byte(path)
    if cb is not None and cb[0] != 0xFF:
        cfg.extra_params['cymbal_burst'] = cb[0]
    if cb is not None and cb[1] != 0x81:
        cfg.extra_params['cymbal_ctrl'] = cb[1]
    # durrel-ramp driver (Rayden's custom global note-duration beat).
    dr = _durrel_ramp_probe(path, cfg.base, post_init_sub)
    if dr is not None:
        cfg.extra_params['durrel_ramp'] = ','.join(str(x) for x in dr)
    # hard-restart SMC-toggle wedge sets TWO keys.
    hr = _hr_patch_probe(path, cfg.base, post_init_sub)
    if hr is not None:
        cfg.extra_params['hardrestart_smc_variant'] = 1
        cfg.extra_params['hardrestart_test_init'] = hr
    # hard_restart: family-2 sets 'none' (no sub_17FB) — never override; else the
    # prep-CALL skip wedge (JSR $17FB -> BIT) takes precedence over the
    # preset-immediate wedge (different sites, don't co-occur).
    if 'hard_restart' not in cfg.extra_params:
        hrs = _hr_prep_skip_probe(path, cfg.base, post_init_sub)
        if hrs is not None:
            cfg.extra_params['hard_restart'] = hrs
        else:
            hrv = _hr_preset_probe(path, post_init_sub)
            if hrv is not None:
                cfg.extra_params['hard_restart'] = str(hrv)
    _apply_wedge_probes(path, cfg)
    # Deferred-wave note-init + prep-gate9 (re-assembled builds only — the
    # DATAFLOW path, marked by a located curnote_addr; canon members are
    # proven canon by the masked identity compare, so the extra siddump
    # observation is skipped).
    # (skipped under a C18 phase wrapper: init writes legitimately split
    # across F/P calls there and could mimic the defer footprint.)
    if getattr(cfg, 'curnote_addr', None) is not None and \
            'play_phases' not in cfg.extra_params and \
            'noteinit_defer_wave' not in cfg.extra_params:
        for k, v in _noteinit_defer_probe(path).items():
            cfg.extra_params.setdefault(k, v)
    # play-clock counter byte embedded in the song data (Dresden, C19).
    pca = _playclk_probe(path, cfg.base, post_init_sub)
    if pca is not None:
        cfg.extra_params.setdefault('playclk_addr', f'{pca:04X}')
    # forced_subtune is a cfg ATTRIBUTE, not a param; 0 == the default walk.
    fs = _forced_subtune_probe(path, cfg.base, post_init_sub)
    if fs:
        cfg.forced_subtune = fs
    # PER-SUBTUNE song remap (the conditional sibling of forced_subtune):
    # Bomberman_preview's wrapper sends ONLY subtune 0 to song 5.
    ssm = _subtune_song_map_probe(path, cfg.base, post_init_sub)
    if ssm is not None:
        cfg.subtune_songs = ssm
    # C37 save-state resume wrapper: every subtune plays the forced song,
    # differentiated only by the wrapper's surviving state copy.
    sr = _state_resume_probe(path, cfg.base, post_init_sub)
    if sr is None:
        # 2nd wrapper shape onwards: detect by observation (C37 canonical).
        sr = _state_resume_observe(path, cfg.base, post_init_sub)
    if sr is not None:
        cfg.forced_subtune, cfg.subtune_state_copy = sr
    # per-subtune time-medley switch (C31 medley variant — Arthur pair).
    msw = _medley_switch_probe(path, cfg.base, post_init_sub)
    if msw is not None:
        cfg.extra_params['medley_switch'] = msw
    return cfg


def _build_via_dataflow(sid_path: str, hvsc_root: str,
                        base_override: 'int | None' = None,
                        post_init_sub: 'int | None' = None):
    """Build a config by locating every table via opcode-skeleton signatures
    (handles re-assembled players whose routines + operand sites moved). Returns
    None if the base or any table can't be located; the verify gate is the net.

    `base_override` FORCES the player base (a compilation player, ledger C31):
    such players are canonical DMC but NON-UNIFORMLY relocated (the packer moves
    the state scratch — e.g. the $100C active-flag array — independently of the
    code), which fails the canon path's uniform-delta identity compare. The
    signature-based dataflow locate reads each table's ACTUAL operand regardless
    of relocation, so it handles them."""
    from pipelines.dmc.v4 import dataflow
    mem, s = _load(os.path.join(hvsc_root, sid_path), post_init_sub)
    load = s['load']

    def _state_addr_sanity(loc):
        # The signature locator can FALSE-MATCH a state site and deref an
        # address OUTSIDE the loaded image (Chwat player 2: curnote $EA12,
        # image ends $35BE). There is no file byte there, so the leftover
        # priming it feeds is fiction (idle notes read as zeros). None =
        # the documented canon base-offset fallback, which reads the real
        # file leftover. Data/table addrs are verify-gated; only the three
        # priming addrs feed the stream unverified.
        img_end = load + len(s['payload'])
        for _k in ('curnote_addr', 'gatemask_addr', 'dual_parity_addr'):
            _v = loc.get(_k)
            if _v is not None and not load <= _v < img_end:
                loc[_k] = None
        return loc
    if base_override is not None:
        # A co-packed compilation player can carry dead-code JMPs into a sibling
        # player's canonical code (ledger C31); bound the locate to this
        # player's own $Xxxx code window so the sibling's block doesn't create
        # ambiguous double-matches (0x900 covers the canonical player extent
        # $1000-$18E8; data-table addresses are the READ RESULT, not the site).
        loc = dataflow.locate(mem, base_override,
                              region=(base_override, base_override + 0x900))
        if loc is None:
            return None
        loc = _state_addr_sanity(loc)
        # A compilation player is a plain canonical DMC dispatched by the
        # wrapper: its own play is base+3, so skip the CIA/play-phase/post-init
        # probes (all keyed on the PSID play vector = the shared wrapper). The
        # file-image leftover priming is used as-is (verified sufficient for the
        # compilation cluster; a non-start player's post-init state can't be
        # captured through the wrapper anyway). cia_period stays 0 (the cluster
        # is vblank; a CIA compilation would fall to the single-player path).
        cfg = DMCV4Config(
            sid_path=sid_path,
            name=os.path.splitext(os.path.basename(sid_path))[0],
            base=base_override, cia_period=0,
            play_repeat=_detect_play_repeat(mem, base_override + 3,
                                            base_override, load),
            extra_params=_dataflow_knob_probes(mem, load), **loc)
        return cfg

    def _jt(b):
        return (0 < b and load <= b and b + 6 < 0x10000 and mem[b] == 0x4C
                and mem[b + 3] == 0x4C and (mem[b + 1] | (mem[b + 2] << 8)) == b + 0x1D)
    base = next((b for b in (s['play'] - 3, load) if _jt(b)), None)
    if base is None:
        hi = min(0x10000, load + len(s['payload']))
        base = next((b for b in range(load, hi - 6) if _jt(b)), None)
    if base is None:
        # JT-less (`no_jumptable`): a jump table with NON-canonical targets
        # (e.g. init->+$7D / +$807, play->+$E5 / +$85). The dataflow trace
        # follows the JMPs to the handlers regardless of the target offsets, so
        # ANY `4C .. 4C` table at play-3 or load is a base candidate. play-3 is
        # the common $0FF4-prefix case: a CIA-timer init wrapper at load=$0FF4
        # with the real JT at $1000 = play-3 (JMP $1751 / $1075, non-canonical).
        for cb in (s['play'] - 3, load):
            if 0 < cb and load <= cb and mem[cb] == 0x4C and mem[cb + 3] == 0x4C:
                base = cb
                break
    loc = None
    if base is None:
        # WRAPPER-PREFIX / MIXED-TABLE members (the residual no_jumptable
        # bucket): a CIA-setup wrapper at load ends in `JMP $1000` with the
        # real jump table at the target, or the table itself mixes JSR/JMP
        # entries (`4C init / 20 85 10 / 4C 85 10`) so the strict 4C@+3 check
        # misses it. Tiered candidates, each judged by dataflow.locate
        # succeeding (and the verify gate downstream): (1) wrapper JMP
        # targets that carry a strict 4C..4C table — the wrapper names the
        # player entry explicitly, the strongest base signal; (2) play-3 /
        # load with only the leading 4C (mixed table). No full-image loose
        # scan — an interior `4C..4C` pair (e.g. entries 3+4 of a mixed
        # table) can locate from the wrong base.
        hi = min(0x10000, load + len(s['payload']))
        cands = []
        for a in range(load, min(load + 64, hi - 2)):
            if mem[a] == 0x4C:
                t = mem[a + 1] | (mem[a + 2] << 8)
                if (load <= t < hi - 6 and mem[t] == 0x4C
                        and mem[t + 3] == 0x4C and t not in cands):
                    cands.append(t)
        for cb in (s['play'] - 3, load):
            if (0 < cb and load <= cb < hi - 6 and mem[cb] == 0x4C
                    and cb not in cands):
                cands.append(cb)
        for cb in cands:
            try:
                loc = dataflow.locate(mem, cb)
            except Exception:
                loc = None
            if loc is not None:
                base = cb
                break
    if base is None:
        return None
    if loc is None:
        loc = dataflow.locate(mem, base)
    if loc is None and s['play'] != base + 3:
        # jump-table play entry rotted (ripper artifact: JMP into zeroed RAM)
        # while the PSID header names the real play body — trace from there.
        loc = dataflow.locate(mem, base, play=s['play'])
    if loc is None:
        return None
    # CIA multispeed (same as the canon path): if the speed bit is set, run the
    # init and recover the timer latch so the rebuild runs at the same rate.
    # When py65 can't read it (init hangs / latch programmed in an IRQ /
    # wrapper the sentinel never returns from), measure the rate from the
    # ground-truth writelog — the same fallback the canon path uses. Still
    # lenient on a fully unmeasurable latch (fall back to single-speed; the
    # verify gate catches a mis-rated build as a partial) — the dataflow path
    # is itself a best-effort fallback.
    cia_period = 0
    if s.get('speed', 0) & 1:
        cp = _cia_period_crosschecked(os.path.join(hvsc_root, sid_path),
                                       s['start'] - 1)
        if not (0x0100 <= cp <= 0xFFFF):
            cp = _cia_period_from_writelog(os.path.join(hvsc_root, sid_path),
                                           s['start'] - 1)
        if 0x0100 <= cp <= 0xFFFF:
            cia_period = cp
    play_repeat = (1 if (s.get('speed', 0) & 1)
                   else _detect_play_repeat(mem, s['play'], base, load))
    cfg = DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        base=base, cia_period=cia_period, play_repeat=play_repeat,
        extra_params=_dataflow_knob_probes(mem, load),
        **_state_addr_sanity(loc))
    # PLAY-PHASE wrapper on the RE-ASSEMBLED route (C18): canon entry-point
    # offsets don't hold here, so observe by SID-write footprint instead of
    # PCs (P = the $D416 global-filter tail; F/R = per-voice writes without
    # it). E.g. Arrive: CIA 6x with full play every 6th call, effects-only
    # between — without the knob the rebuild ticks 6x too fast.
    if cfg.play_repeat == 1:
        # PLAY-PHASE wrapper on the RE-ASSEMBLED route (C18): observe under
        # libsidplayfp — the straddle-free per-play pc-trace (GROUND TRUTH,
        # native-capture Phase 2e; feedback_ground_truth.md). Classifies each
        # play() P/F/R/S by the $D416 filter tail + signature-located frame-
        # entry / effects-tail reachability. This REPLACES the py65 write-
        # footprint observer `_observe_play_phases_writes` (deleted), for which
        # the pc-trace was already the designed ground-truth fallback. An A/B
        # over all 129 writes-with-P f1 carriers found pctrace gives the
        # IDENTICAL schedule on every S-phase slow-tempo carrier (P_S, ...) —
        # so the gate keeps allowing S (an 'S' from the ground-truth engine is
        # a genuine play-body SKIP; the body always writes $D416 -> P, so a
        # plain member is never spuriously S) — and the only three effective
        # changes are F/R re-classifications on members already PARTIAL, where
        # ground truth is the correct call.
        ph = _observe_play_phases_pctrace(
            os.path.join(hvsc_root, sid_path), s['start'] - 1, s['play'])
        if (ph and '_' in ph and 'P' in ph.split('_')):
            # static SMC-JSR-table wrapper: force same-target calls to one
            # token (majority) — kills single-call F/R misreads (Hexzakk).
            ph2 = _smc_jsr_table_refine(os.path.join(hvsc_root, sid_path),
                                        cfg.base, ph, post_init_sub)
            if ph2 is not None:
                ph = ph2
            # direct-JMP wavestep-arm wrapper: an idle voice made the call
            # look like R; the static wrapper target is the truth (r143).
            ph3 = _wavestep_arm_refine(os.path.join(hvsc_root, sid_path),
                                       cfg.base, ph, post_init_sub)
            if ph3 is not None:
                ph = ph3
                cfg.extra_params.setdefault('noteinit_deferred', '1')
            cfg.extra_params['play_phases'] = ph
            # F-phase per-voice REPEAT (C18/C24, PVCF 'massive multispeed' —
            # Sound_Test): the effects branch runs `JSR SUB xk`, SUB advancing
            # each voice's wave-step m times, so the wave program steps m*k per
            # E-call. Static decode -> 'k:VxC,..'; the F phase is pure wave-step
            # (effects only), so it enters the arm (noteinit_deferred).
            if any(t and t[0] == 'F' for t in ph.split('_')):
                fr = _fphase_effect_repeat(os.path.join(hvsc_root, sid_path),
                                           cfg.base, post_init_sub)
                if fr is not None:
                    cfg.extra_params['fphase_repeat'] = fr
                    cfg.extra_params.setdefault('noteinit_deferred', '1')
            # Per-member: does the F phase DEFER note-init (the 2-frame arm)?
            # Only F-token schedules have the ambiguity (the arm lives on an F
            # call). Observe it — not derivable from the schedule/multispeed.
            if any(t and t[0] == 'F' for t in ph.split('_')) and \
                    _detect_notestart_arm(os.path.join(hvsc_root, sid_path),
                                          s['start'] - 1, s['play']):
                cfg.extra_params['noteinit_deferred'] = '1'
                # Arm entry-point variant: F phase enters the vibrato
                # half-cycle boundary ($1567) instead of the wave step.
                if _detect_fx_entry_vibhalf(
                        os.path.join(hvsc_root, sid_path),
                        s['start'] - 1, s['play']):
                    cfg.extra_params['effect_entry_variant'] = 'vibflip'
            # R-phase entry variant: does the non-tick phase re-run the pulse
            # TAIL ($135D, a 2nd pulse advance/tick) instead of a plain
            # register refresh? (C18, twin of vibflip for the R phase.)
            if any(t and t[0] == 'R' for t in ph.split('_')) and \
                    _rphase_pulse_tail_probe(os.path.join(hvsc_root, sid_path),
                                             s['start'] - 1, base):
                cfg.extra_params['rphase_variant'] = 'pulse_tail'
    # POST-INIT leftover capture: canon's leftover priming (d417 shadow,
    # idle notes/masks, dual phase) reads the file image because canon init
    # never touches those bytes. A re-assembled init MAY clear/rewrite them
    # (Scalework clears its route shadow), so run THIS member's init and
    # capture the values the play loop actually starts from. Falls back to
    # the file image when init can't be run (None).
    ram = _post_init_ram(os.path.join(hvsc_root, sid_path), s['start'] - 1)
    if ram is not None:
        cn = cfg.curnote_addr if cfg.curnote_addr is not None else base + 0x12
        gm = cfg.gatemask_addr if cfg.gatemask_addr is not None else base + 0x0F
        dp = (cfg.dual_parity_addr if cfg.dual_parity_addr is not None
              else base + 0x19)
        cfg.post_init_state = {
            'd417_shadow': ram[cfg.d417_shadow_addr],
            'idle_notes': (ram[cn], ram[cn + 1], ram[cn + 2]),
            'idle_masks': (ram[gm], ram[gm + 1], ram[gm + 2]),
            'dual_phase': ram[dp] & 1,
            'durrel_init': (ram[base + 0x73E], ram[base + 0x73F],
                            ram[base + 0x740]),
        }
    # HANK $FF-loop variant (Hank/Roots): the patched $FF handler reads its
    # loop target through a zero-page pointer; when that pointer is null the
    # target is a sonified zero-page byte (the live track-pointer hi) that a
    # static walk cannot see. Measure the per-voice targets under py65 and
    # override loop_reset_pos (only for a voice whose target is a non-zero
    # constant; $00/unobserved voices stay on the canon path, byte-identical),
    # only when the dataflow found no explicit loop hook.
    if cfg.loop_reset_pos is None:
        _hlt = _hank_ff_loop_targets(os.path.join(hvsc_root, sid_path), base,
                                     post_init_sub)
        if _hlt is not None:
            cfg.loop_reset_pos = _hlt
    return cfg


def _dataflow_knob_probes(mem, load: int) -> dict:
    """Variant-knob probes for re-assembled players (the dataflow path).

    The canon path probes its sub-build knobs at canon-relative sites
    ($1180 rest dispatch, ...); a re-assembled layout moves those sites, so
    the probes silently missed and every dataflow member got default knobs
    (Hyper's rest-skip player diverged at flat pos 2 because rest_effects
    stayed 'run'). Probe by OPCODE SHAPE instead (layout-independent, the
    same idiom dataflow.locate uses):

    rest/switch/slide-tail dispatch — the rest handler is
        LDA dur_reload,x / STA dur,x / INC secpos,x / [JSR end-check] /
        JMP target
    and `target` classifies the variant by its own signature:
        wave-step = LDA flags,x / AND #$01 / BNE   (BD .. .. 29 01 D0)
                    -> rest_effects='skip'
        effects   = LDA guard,x / BEQ .. / DEC     (BD .. .. F0 .. DE)
                    -> canon 'run' (no knob)
    """
    extra = {}
    hi = min(0x10000, load + 0x2000) - 16
    for a in range(load, hi):
        if not (mem[a] == 0xBD and mem[a + 3] == 0x9D and mem[a + 6] == 0xFE):
            continue
        p = a + 9
        if mem[p] == 0x20:                      # optional JSR end-check
            p += 3
        if mem[p] == 0x60:                      # RTS wedge: NO effects on
            extra['rest_effects'] = 'none'      # the fetch frame (C19)
            break
        if mem[p] != 0x4C:
            continue
        tgt = mem[p + 1] | (mem[p + 2] << 8)
        if tgt + 6 >= 0x10000:
            continue
        if (mem[tgt] == 0xBD and mem[tgt + 3] == 0x29
                and mem[tgt + 4] == 0x01 and mem[tgt + 5] == 0xD0):
            extra['rest_effects'] = 'skip'      # wave-step target
            break
        if (mem[tgt] == 0xA9 and mem[tgt + 1] == 0x00 and mem[tgt + 2] == 0x9D
                and mem[tgt + 5] == 0xBD and mem[tgt + 8] == 0x49
                and mem[tgt + 9] == 0x01):
            extra['rest_effects'] = 'vibflip'   # vibrato half-cycle entry
            break
        if (mem[tgt] == 0xBD and mem[tgt + 3] == 0xF0
                and mem[tgt + 5] == 0xDE):
            break                               # effects target = canon 'run'
    return extra


def _build_via_canon(sid_path: str, hvsc_root: str = 'hvsc85',
                     base_override: 'int | None' = None,
                     chip_addr: int = 0,
                     post_init_sub: 'int | None' = None) -> DMCV4Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path), post_init_sub)

    # ---- base detection. The canonical jump table is `JMP base+$1D /
    # JMP base+$85` (init / play handlers). Normally play = base+3, but a
    # multispeed / CIA wrapper member's play vector points to its own
    # dispatcher while the real player sits at the LOAD address. So try
    # play-3 first (clean relocations), then load. Relocation is
    # extract-only (the composer always emits at $1000; the writelog is
    # base-independent — the original's wrapper init/play are captured
    # as-is by the verify, handled by Check A + per-IRQ for CIA). ----
    # Two jump-table layouts share the same play body but wire init
    # differently. CANONICAL: `JMP base+$1D / JMP base+$85` (4-entry).
    # 2ENTRY: `JMP base+$807 / JMP base+$50` (2-entry table, restructured
    # init — ~621 members; the play body is byte-identical to canon, only
    # the init/dispatch/all-off regions differ, and we emit our own init).
    # A player the wrapper RELOCATED into RAM can sit BELOW the load address
    # (Pour_le_merite loads at $8000 and copies its second player down to
    # $1000), so the load floor — a sanity guard for players read out of the
    # file image — must not apply to one read out of post-init RAM.
    _floor = 0 if post_init_sub is not None else s['load']

    def _jt_layout(b):
        if not (0 < b and _floor <= b and b + 0x8E7 < 0x10000
                and mem[b] == 0x4C and mem[b + 3] == 0x4C):
            return None
        e0 = mem[b + 1] | (mem[b + 2] << 8)
        e1 = mem[b + 4] | (mem[b + 5] << 8)
        if e0 == b + 0x1D and e1 == b + 0x85:
            return 'canonical'
        if e0 == b + 0x807 and e1 == b + 0x50:
            return '2entry'
        # family 2: init $37 / play $85 (the distinctive signature). Some
        # builds wire all 4 entries (all-off $62F / sfx $63E), others only
        # init+play (the rest of $1006-$100B zeroed). The masked identity
        # compare validates the actual player either way, so init+play is
        # enough to dispatch.
        if e0 == b + 0x37 and e1 == b + 0x85:
            return 'family2'
        # The play body is at the canonical family-2 offset +$85, but the init
        # handler is shifted a few bytes (+$38..$3A instead of +$37) — a
        # restructured init header. We emit our own init and every operand site
        # lives in the UNSHIFTED play body, so these build+verify as family2.
        # (canonical/2entry are matched above — init+$1D / play+$50 — so this
        # never catches them.) Validated: 12 FULL / 2 correctly-partial /
        # 0 false-accept on the no_jumptable residue; the build+verify gate in
        # _family2_build is the real judge.
        if e1 == b + 0x85 and b + 0x30 <= e0 <= b + 0x40:
            return 'family2'
        return None

    base = layout = None
    # COMPILATION member: the file packs N independent players behind a
    # per-subtune SMC dispatch wrapper (ledger C31). The caller extracts each
    # player by FORCING its base — skip auto-detection (both players carry a
    # valid canonical jump table, so detection can't pick the right one), and
    # treat the forced player as standalone-canonical (its own play is
    # base+3; the PSID play vector is the wrapper, not this player).
    if base_override is not None:
        layout = _jt_layout(base_override)
        if layout is None:
            raise DMCV4Unsupported(
                'base_override_not_player', f'${base_override:04X}')
        base = base_override
    for b in ([] if base_override is not None else (s['play'] - 3, s['load'])):
        layout = _jt_layout(b)
        if layout:
            base = b
            break
    if base is None and base_override is None:
        # relocated-WITHIN-file: the player sits at neither play-3 nor
        # load — typically a CIA/multispeed wrapper whose dispatcher is at
        # play/load while the real player is elsewhere in the image. Scan
        # for the first valid jump-table signature; the masked identity
        # compare then validates it (a spurious 4C..4C match fails the
        # compare cleanly as player_code_mismatch).
        lo = s['load']
        hi = min(0x10000, lo + len(s['payload']))
        for b in range(lo, hi - 0x12):
            if mem[b] == 0x4C and mem[b + 3] == 0x4C:
                lay = _jt_layout(b)
                if lay:
                    base, layout = b, lay
                    break
    if base is None:
        # BANKING-WRAPPER JT-less (Itinerant): the PSID play vector is a
        # ROM-banking wrapper `LDA #$35/STA $01/JSR t/LDA #$37/STA $01/RTS`
        # and the jump table at the handler's base was OVERWRITTEN by the
        # wrapper/init code itself (the member's init tail `JMP base+$807`
        # is the 2entry init handler). Trust the wrapper's JSR target:
        # t-$50 = the 2entry play-handler offset, t-$85 = canonical. The
        # masked identity compare downstream validates the base (a wrong
        # base fails cleanly as player_code_mismatch).
        p = s['play']
        if (bytes(mem[p:p + 4]) == bytes.fromhex('a9358501')
                and mem[p + 4] == 0x20
                and bytes(mem[p + 7:p + 11]) == bytes.fromhex('a9378501')
                and mem[p + 11] == 0x60):
            t = _rd16(mem, p + 5)
            for off, lay in ((0x50, '2entry'), (0x85, 'canonical')):
                b = t - off
                if s['load'] <= b and b + 0x8E7 < 0x10000:
                    base, layout = b, lay
                    break
    if base is None:
        # FAMILY-2 NEAR-MISS fallbacks (2026-08-12, the "easy-8" unsupported
        # census — see pipelines/dmc/family2/RE_NOTES.md). These run ONLY
        # after every detection above failed, so no previously-detected
        # member's dispatch can change. The family-2 body offsets are the
        # anchor: init sits at base+$37 and play at base+$85, so any pair of
        # candidate targets (ti, tp) with ti-$37 == tp-$85 names ONE
        # consistent base — a wrapper that re-points a single vector fails
        # the equation structurally (verified on the wrapper-class members).
        # build+verify is the real judge downstream (the identity compare is
        # advisory for family 2).
        _NEUTRAL_1 = {0xAA, 0xA8, 0x8A, 0x98, 0xC8, 0xE8, 0xEA}  # trans/inc
        _NEUTRAL_2 = {0xA9, 0xA2, 0xA0,               # LDA/LDX/LDY #imm
                      0xA5, 0xA6, 0xA4,               # LDA/LDX/LDY zp
                      0x85, 0x86, 0x84, 0xE6, 0xC6,   # STA/STX/STY/INC/DEC zp
                      0xC9, 0xE0, 0xC0,               # CMP/CPX/CPY #imm
                      0xD0, 0xF0}                     # BNE/BEQ (fallthrough)

        def _neutral_walk(pc, depth=24):
            """Follow a write-stream-NEUTRAL wrapper (zp counters, register
            transfers, forward branches) to its terminal JMP target. The
            CORE TENET makes such a wrapper irrelevant to the rebuild: it
            touches no SID register, so the write stream is the wrapped
            body's alone (Soul_tune_1/2's zp frame counter). Any absolute
            store, JSR, or unknown opcode refuses (returns None)."""
            acc = None                # last LDA #imm value, if known
            for _ in range(depth):
                op = mem[pc]
                if op == 0x4C:
                    tgt = _rd16(mem, pc + 1)
                    if not (0 < tgt < 0xFFF0) or tgt == pc:
                        return None
                    # terminal: the consistency equation at the caller decides
                    # (the wrappers seen end in exactly one JMP into the body).
                    return tgt
                if op in (0xF0, 0xD0) and acc is not None:
                    # after `LDA #imm` the branch direction is STATIC — follow
                    # the taken path (Soul_partselector's `LDA #0 / BEQ ->
                    # JMP $1085` obfuscated jump); an unknown-flag branch
                    # still falls through as before.
                    taken = (acc == 0) == (op == 0xF0)
                    off = mem[pc + 1]
                    pc += 2
                    if taken:
                        pc = (pc + (off - 0x100 if off >= 0x80 else off)) \
                            & 0xFFFF
                    continue
                if op in _NEUTRAL_1:
                    if op in (0x8A, 0x98):   # TXA/TYA load A: unknown
                        acc = None
                    pc += 1
                elif op in _NEUTRAL_2:
                    if op == 0xA9:
                        acc = mem[pc + 1]
                    elif op == 0xA5:
                        acc = None           # LDA zp: unknown
                    pc += 2
                else:
                    return None
            return None

        def _mvol_prime_walk(pc):
            """The Note_from_Tonka init-wrapper shape: `JSR real_init /
            LDA #imm / STA $D418 / RTS` — pure trichotomy §4.2 master-vol
            priming around the canonical init. Returns (real_init, imm)."""
            if (mem[pc] == 0x20 and mem[pc + 3] == 0xA9
                    and mem[pc + 5] == 0x8D and _rd16(mem, pc + 6) == 0xD418
                    and mem[pc + 8] == 0x60):
                return _rd16(mem, pc + 1), mem[pc + 4]
            return None

        def _poke_wrapper_walk(pc):
            """The X-mas_Cooperation init-wrapper shape: `TAY / LDA tab,Y /
            STA tgt / TYA / JMP real_init` — a C37-degenerate per-subtune
            KNOB poke (classified downstream in _family2_build). Returns the
            real_init target for the consistency equation."""
            if (mem[pc] == 0xA8 and mem[pc + 1] == 0xB9 and mem[pc + 4] == 0x8D
                    and mem[pc + 7] == 0x98 and mem[pc + 8] == 0x4C):
                return _rd16(mem, pc + 9)
            return None

        def _jsr_body_walk(pc):
            """A C24 whole-play wrapper (`JSR T ... JMP T|RTS`) names the
            real play body T; _detect_play_repeat later derives the repeat
            count from the same shape (Twin_Russian: `JSR $87BE/JMP $87BE`
            on a re-assembled 2-vector player)."""
            if mem[pc] == 0x20:
                return _rd16(mem, pc + 1)
            return None

        def _f2_base(ti, tp):
            if ti is None or tp is None:
                return None
            b2 = tp - 0x85
            if ti - 0x37 != b2 or not (0 < b2 and b2 + 0x8E7 < 0x10000):
                return None
            return b2

        # candidate (init, play) target pairs, most-direct first: JT slots
        # with the opcode relaxed to JSR (Merilyn's `JSR $1085/RTS` play
        # slot, Yoko's JSR init slot), then the raw header vectors (the
        # KERNAL-reset trap JT whose header points straight at the bodies),
        # each combined with a neutral-walked resolution of either side.
        cands = []
        for b in dict.fromkeys((s['play'] - 3, s['load'])):
            if (0 < b and _floor <= b and b + 9 < 0x10000
                    and mem[b] in (0x4C, 0x20) and mem[b + 3] in (0x4C, 0x20)):
                cands.append((_rd16(mem, b + 1), _rd16(mem, b + 4)))
        cands.append((s['init'], s['play']))
        _mvol_prime = None
        for ti0, tp0 in cands:
            mp = _mvol_prime_walk(ti0) if s['load'] <= ti0 else None
            ti_opts = [ti0] + ([mp[0]] if mp else []) + \
                ([_neutral_walk(ti0), _poke_wrapper_walk(ti0),
                  _jsr_body_walk(ti0)]
                 if s['load'] <= ti0 else [])
            tp_opts = [tp0] + \
                ([_neutral_walk(tp0), _jsr_body_walk(tp0)]
                 if s['load'] <= tp0 else [])
            for ti in ti_opts:
                for tp in tp_opts:
                    b2 = _f2_base(ti, tp)
                    if b2 is not None:
                        base, layout = b2, 'family2'
                        if mp and ti == mp[0]:
                            _mvol_prime = mp[1]
                        break
                if base is not None:
                    break
            if base is not None:
                break
    if base is None:
        b = s['play'] - 3
        reason = ('no_jumptable' if 0 < b and s['load'] <= b
                  else 'nonstandard_vectors')
        raise DMCV4Unsupported(
            reason,
            f"load=${s['load']:04X} init=${s['init']:04X} play=${s['play']:04X}")
    # CIA multispeed. When the PSID speed bit is set the player runs off the
    # CIA1 timer A, not the 50 Hz VBI — at ~2-6x speed, so the rebuild must
    # run at the same CIA rate or it logs proportionally fewer writes (the
    # dominant CIA-partial signature: full overlap match, len_post_a = k *
    # len_post_b). The timer comes from the init in TWO ways and BOTH must be
    # recovered: (a) a separate wrapper dispatcher (play != base+3), or
    # (b) the CANONICAL player's own init programming $DC04/$DC05 with
    # play == base+3 (the common case: e.g. latch $1331 => 4x, $2663 => 2x).
    # So gate on the speed bit alone and read the latch the init leaves.
    # The composer emits the same latch + speed bit (see config.cia_period).
    # A forced-base compilation player is standalone-canonical: its own play
    # is base+3 (the PSID play vector is the shared dispatch wrapper). Use that
    # for every play-vector-shape test so the wrapper isn't mistaken for a
    # multispeed/play-phase wrapper of THIS player.
    eff_play = base + 3 if base_override is not None else s['play']
    cia_period = 0
    if s.get('speed', 0) & 1:
        cia_period = _cia_period_crosschecked(
            os.path.join(hvsc_root, sid_path), s['start'] - 1)
        if not (0x0100 <= cia_period <= 0xFFFF):
            # py65 couldn't read the latch (init hangs / unsupported opcode /
            # timer programmed in an IRQ) OR the init programs none. Measure
            # the rate from the ground-truth writelog (libsidplayfp runs the
            # init correctly) — this also recovers the speed-bit-with-NO-latch
            # class, which runs at the PSID default $4025 (60 Hz; a vblank
            # 50 Hz build under-runs it ~20% = a guaranteed length partial).
            cia_period = _cia_period_from_writelog(
                os.path.join(hvsc_root, sid_path), s['start'] - 1)
            if not (0x0100 <= cia_period <= 0xFFFF):
                # A wrapper member IS multispeed but we can't read its rate ->
                # can't rebuild it faithfully. A canonical-play member falls
                # back to single-speed (a 50 Hz-ish CIA rate is equivalent).
                if eff_play != base + 3:
                    raise DMCV4Unsupported(
                        'cia_multispeed',
                        f"play=${s['play']:04X} CIA latch unreadable "
                        "(py65 + writelog)")
                cia_period = 0
    # INTERNAL multispeed (vblank wrapper, no speed bit) — independent of CIA.
    play_repeat = (1 if (s.get('speed', 0) & 1)
                   else _detect_play_repeat(mem, eff_play, base, s['load']))
    # PLAY-PHASE wrapper (not an N-JSR repeat): the play vector cycles
    # full-play / effects-only calls — with the CIA speed bit this is TRUE
    # multispeed EFFECTS (e.g. $1331 4x + 'PFFF' = engine ticks at 50Hz,
    # effect chain runs at 200Hz); without it, a slow-tempo cycler. A pure
    # CIA rate wrapper (every call a full play) observes as 'P' = no knob,
    # so the existing cia_multispeed members are untouched. Observed under
    # py65 (C9: measure, don't parse — wrapper shapes vary: SMC operand
    # table, DEC+dual-JMP, INC+AND, stubs hidden in compare-masked regions).
    play_phases = None
    if play_repeat == 1 and eff_play != base + 3:
        play_phases = _observe_play_phases(
            os.path.join(hvsc_root, sid_path), s['start'] - 1, base)
        if play_phases in ('P', 'S', None):
            play_phases = None
        # py65 gave nothing usable, OR observed an 'S' (silent) frame — under
        # py65 a CIA/IRQ-armed member's effect frames don't run and read as S,
        # while the ground-truth pc-trace shows they run effects. Fall back to
        # the straddle-free pc-trace observer and adopt its clean, S-free
        # P-cycle. Verify-gated; a clean non-S py65 answer is left untouched.
        if play_phases is None or 'S' in (play_phases or ''):
            pf = _observe_play_phases_pctrace(
                os.path.join(hvsc_root, sid_path), s['start'] - 1, s['play'])
            if pf and '_' in pf and 'P' in pf.split('_') and 'S' not in pf:
                play_phases = pf
        # direct-JMP wavestep-arm wrapper: an idle voice made the call look
        # like R; the static wrapper target is the truth (r143). Sets the
        # arm mode via _WAVESTEP_ARM_HINT (consumed by the caller below).
        if play_phases:
            ph3 = _wavestep_arm_refine(os.path.join(hvsc_root, sid_path),
                                       base, play_phases)
            if ph3 is not None:
                play_phases = ph3 + '!arm'
    delta = base - 0x1000

    def at(canon_addr):                 # canonical $1xxx addr -> mem index
        return canon_addr + delta

    def reloc(operand_val):             # canonical abs value -> relocated
        return operand_val + delta

    if layout == 'family2':
        return _family2_build(mem, s, sid_path, base, delta, at, cia_period,
                              play_repeat)

    # ---- masked identity compare against the RELOCATED canonical
    # player. Build the reference image: canon with every self-ref
    # operand (code/RAM/table addresses) shifted by delta. ----
    canon = bytearray(open(_CANON_PATH, 'rb').read())
    if delta:
        for pc, val in _canon_reloc_instrs():
            nv = (val + delta) & 0xFFFF
            canon[pc - 0x1000 + 1] = nv & 0xFF
            canon[pc - 0x1000 + 2] = nv >> 8
    # layout-local site/satellite maps (the 2-entry play body uses the
    # canon sites; only the init-region tunetab access + the masked
    # init regions differ).
    sites_map = dict(_SITES)
    tune_sat = _TUNE_SAT
    mask_ranges = _MASKED_RANGES
    if layout == '2entry':
        sites_map = dict(_SITES, tunetab=[_V2ENTRY_TUNETAB_SITE])
        tune_sat = _V2ENTRY_TUNE_SAT
        mask_ranges = _MASKED_RANGES + _V2ENTRY_MASK
    masked = bytearray(0x1000)           # 1 = ignore, indexed by canon offset
    for a, b in mask_ranges:
        for i in range(a, b):
            masked[i - 0x1000] = 1
    for sites in sites_map.values():
        for a in sites:
            masked[a - 0x1000] = masked[a - 0x1000 + 1] = 1
    for a, _off in _FILT_SAT + _INST_SAT + tune_sat:
        masked[a - 0x1000] = masked[a - 0x1000 + 1] = 1
    # track-loop hook probe: the site holds STA (base+$726),x in the
    # canonical player; a JSR-hook variant reads the next track byte as
    # the loop target. Both operands relocate with base. (The reset-all-to-0
    # JSR hook — LDA #0/STA $1726/$1727/$1728, a synchronized loop-to-start —
    # is a wedge that fails the masked compare below with player_code_mismatch
    # and is classified on the dataflow path; see dataflow.locate.)
    loop_target = _loop_target_probe(mem, base, strict=True)
    for i in range(_LOOP_SITE, _LOOP_SITE + 3):
        masked[i - 0x1000] = 1
    # $7D-retrig wedge (C19): the SWITCH dispatch BEQ operand at base+$12C is
    # re-pointed at canon's own glide replay tail — a validated probe masks
    # that one operand byte so the carrier flows through this canonical path.
    switch_retrig = _switch_retrig_probe(mem, base)
    if switch_retrig:
        masked[0x112C - 0x1000] = 1
    # ---- canon sub-build knob probes: variants that either map to an
    # existing composer knob or emit the same writes. Each masks its site
    # so the variant passes the compare; the verify is the safety net. ----
    extra = {}
    if play_phases:
        if play_phases.endswith('!arm'):
            # wavestep-arm refinement (r143): the flipped F token IS the
            # $1591 arm entry — force the 2-frame-arm mode directly (the
            # footprint observer below can't see it: the voice idled).
            play_phases = play_phases[:-4]
            extra['noteinit_deferred'] = '1'
        extra['play_phases'] = play_phases
        # Per-member: does the F phase DEFER note-init (the 2-frame arm)?
        # Only F-token schedules carry the ambiguity; observe it (not derivable
        # from the schedule string — Words/F.A.K.E are both P_F123 but differ).
        if any(t and t[0] == 'F' for t in play_phases.split('_')) and \
                _detect_notestart_arm(os.path.join(hvsc_root, sid_path),
                                      s['start'] - 1, s['play']):
            extra['noteinit_deferred'] = '1'
            # Arm entry-point variant: F phase enters the vibrato half-cycle
            # boundary ($1567: flip+swell, falls through wavestep) instead of
            # the wave step ($1591) — Acid_Dance's wrapper JSRs $1567 x3.
            if _detect_fx_entry_vibhalf(os.path.join(hvsc_root, sid_path),
                                        s['start'] - 1, s['play']):
                extra['effect_entry_variant'] = 'vibflip'
        # R-phase entry variant: does the non-tick phase re-run the pulse TAIL
        # ($135D, a 2nd pulse advance/tick from the stale $171F) instead of a
        # plain register refresh? (C18, twin of vibflip for the R phase.)
        if any(t and t[0] == 'R' for t in play_phases.split('_')) and \
                _rphase_pulse_tail_probe(os.path.join(hvsc_root, sid_path),
                                         s['start'] - 1, base):
            extra['rphase_variant'] = 'pulse_tail'
    # rest/switch/slide-tail dispatch ($1180): canon JMP $1322 (run
    # effects); a sub-build JMP $1591 (wavestep) — the modulators hold one
    # frame at each tie (the family-2 rest_effects='skip' behavior).
    if mem[at(0x1180)] == 0x60:
        # RTS wedge (C19, Bassy_Introtune): the rest/switch/slide tail
        # RETURNS instead of jumping anywhere — the fetch frame runs NO
        # effects for the voice, not even the wave-step refresh ('skip'
        # still refreshes). The two bytes after the RTS are dead.
        extra['rest_effects'] = 'none'
        for i in range(0x1180, 0x1183):
            masked[i - 0x1000] = 1
    elif mem[at(0x1180)] == 0x4C:
        tgt = _rd16(mem, at(0x1180) + 1)
        if tgt == reloc(0x1591):
            extra['rest_effects'] = 'skip'
        elif tgt == reloc(0x1567):
            # mid-routine vibrato half-cycle entry (L_1567): rest frames
            # flip the vibrato direction, then wave-step (Acid_Dance).
            extra['rest_effects'] = 'vibflip'
        elif tgt != reloc(0x1322):
            raise DMCV4Unsupported('rest_dispatch_unknown', hex(tgt))
        for i in range(0x1180, 0x1183):
            masked[i - 0x1000] = 1
    # filter $D418 write ($12A8): canon inline STA $D418; a sub-build JSRs
    # a helper that does STA $D418 (+ a dead store) — identical write.
    if mem[at(0x12A8)] == 0x20:
        h = _rd16(mem, at(0x12A8) + 1)
        if not any(mem[h + k] == 0x8D
                   and (mem[h + k + 1] | (mem[h + k + 2] << 8)) == 0xD418
                   for k in range(9)):
            raise DMCV4Unsupported('filter_write_helper_unknown', hex(h))
        for i in range(0x12A8, 0x12AB):
            masked[i - 0x1000] = 1
    # COMPILATION player (base_override): the packer wires the all-off + sfx
    # jump-table entries ($1006-$100B) to a SHARED routine (one all-off for all
    # packed players, e.g. JMP $C62F) instead of each player's own base+$62F.
    # Those two vectors are never called during play, and the composer emits its
    # own canonical all-off/sfx — so the difference is write-stream-irrelevant.
    # Mask them (only for a forced compilation player; single-player members
    # keep the strict check).
    if base_override is not None:
        for i in range(0x1006, 0x100C):
            masked[i - 0x1000] = 1
    # MULTI-SID sub-player (C27): the editor builds chip 2/3's player by
    # copying chip 1's and adding the chip offset to every `$D4xx` store
    # operand, so those two operand bytes differ from canon exactly like a
    # relocated address does. Mask them — but ONLY where the member's
    # operand is the canon register or its chip-relocated twin, so a real
    # wedge (any other value) still fails the compare. Which stores the
    # relocation MISSED is probed separately (`_multisid_keep_regs`, C19).
    if chip_addr and chip_addr != 0xD400:
        for i in range(0x1000, 0x18E8 - 2):
            if canon[i - 0x1000] not in (0x8D, 0x99, 0x9D):     # STA abs/,y/,x
                continue
            tgt = canon[i - 0x1000 + 1] | (canon[i - 0x1000 + 2] << 8)
            if not (0xD400 <= tgt <= 0xD418):
                continue
            got = mem[at(i) + 1] | (mem[at(i) + 2] << 8)
            if got in (tgt, tgt - 0xD400 + chip_addr):
                masked[i - 0x1000 + 1] = masked[i - 0x1000 + 2] = 1
    # compare the player region (code + fixed tables + vibdepth);
    # operand BYTES are masked (they relocate); the surrounding opcodes
    # are base-invariant and must match canonical exactly.
    for i in range(0x1000, 0x18E8):
        if masked[i - 0x1000]:
            continue
        if mem[at(i)] != canon[i - 0x1000]:
            raise DMCV4Unsupported(
                'player_code_mismatch', f'first diff at ${i:04X}')

    # ---- operand consistency (relocated absolute values) ----
    vals = {}
    for name, sites in sites_map.items():
        vs = {_rd16(mem, at(a)) for a in sites}
        if len(vs) != 1:
            raise DMCV4Unsupported('operand_inconsistent',
                                   f'{name}: {sorted(hex(v) for v in vs)}')
        vals[name] = vs.pop()
    # INIT-UNPACKER members (the Flash trio): EVERY data-table operand
    # points OUTSIDE the loaded image — the init GENERATES the song data
    # in high RAM (the file bytes there don't exist), and the editor
    # placed the unpacked tables in its own order. Accept the
    # operand-named instr base and skip the canonical packing-order
    # check for this class only; the extract reads the tables from
    # post-init RAM (cfg.data_post_init) and the verify gates a
    # mislocation. A member with a mixed in/out-of-image layout stays
    # rejected — the signature is all-or-nothing.
    img_hi = min(0x10000, s['load'] + len(s['payload']))
    unpacked = all(not (s['load'] <= v < img_hi) for v in vals.values())
    if vals['instr'] != reloc(0x18F0) and not unpacked:
        raise DMCV4Unsupported('nonstandard_instr_base', hex(vals['instr']))
    for a, off in _FILT_SAT:
        if _rd16(mem, at(a)) != vals['filtdef'] + off:
            raise DMCV4Unsupported('operand_inconsistent', f'filtdef+{off}')
    for a, off in tune_sat:
        if _rd16(mem, at(a)) != vals['tunetab'] + off:
            raise DMCV4Unsupported('operand_inconsistent', f'tunetab+{off}')
    for a, off in _INST_SAT:
        if _rd16(mem, at(a)) != vals['instr'] + off:
            raise DMCV4Unsupported('operand_inconsistent', f'instr+{off}')
    if not unpacked and not (
            reloc(0x18F0) < vals['wavectrl'] < vals['wavefreq']
            < vals['filtdef'] <= vals['tunetab'] < vals['secp_lo']
            < vals['secp_hi']):
        raise DMCV4Unsupported(
            'layout_disorder',
            ' '.join(f'{k}=${v:04X}' for k, v in sorted(vals.items())))

    # ---- vibdepth stays a family constant (freq tables are per-tune
    # tuning content, carried in USF). Bytes 0-5 OVERLAP the player code
    # ($1888-$188D) so they relocate; only 6-95 are real vibrato data.
    # (the composer emits the canonical curve incl. 0-5; an octave-0
    # vibrato note on a relocated member is the rare exception the
    # verify gate would flag — not worth carrying.) ----
    if bytes(mem[at(0x1888) + 6:at(0x1888) + 96]) != VIBDEPTH[6:]:
        raise DMCV4Unsupported('custom_vibdepth')

    # ---- leftover-state probes ----
    # ($100F-$1011 gate masks and the $1019 dual-clock phase are
    # CAPTURED by the extract as priming — no flags needed.)
    # (the idle wave walk from table index 0 is carried explicitly as
    # wave_programs[0] — record 0's wave_start no longer matters)

    return DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        base=base,
        op_instr=at(0x1227), op_wavectrl=at(0x159C), op_wavefreq=at(0x15B9),
        op_filtdef=at(0x1296), op_tunetab=at(sites_map['tunetab'][0]),
        op_secp_lo=at(0x1103), op_secp_hi=at(0x1108),
        freq_lo_addr=at(0x1647), freq_hi_addr=at(0x16A7),
        vibdepth_addr=at(0x1888), d417_shadow_addr=at(0x1018),
        track_loop_target=loop_target, switch_retrig=switch_retrig,
        cia_period=cia_period,
        play_repeat=play_repeat,
        data_post_init=unpacked,
        extra_params=extra,
    )


def _fdinit_contour_probe(mem, s, base):
    """SilverFox 4k_Byter appended sequencer, DECONSTRUCTED to musical
    content (ledger C1 + C19 33rd occurrence — a driver that changes a
    MUSICAL VALUE is deconstructed, never reproduced as a composer
    mechanism). The appended play wrapper steps/ramps ONE filter def's
    INIT-CUTOFF byte over the song via an SMC counter-retarget sequencer.
    The sequencer is fully deterministic, so this probe:

      1. template-matches the driver (anchored opcodes + operand
         cross-references, the C19 idiom) and captures its constants;
      2. classifies the animated byte — it must be a filter-def record's
         byte 1 (the def's init cutoff);
      3. SIMULATES the sequencer play-by-play (the literal disasm
         semantics) to get the cutoff value each play body observes;
      4. run-length-compresses that series into a C1 piecewise contour:
         start + (delta, count) phases, terminal hold implicit.

    Returns (filter_mod_param, init_plays) where filter_mod_param feeds the
    TYPED `filter_mod` block ('prog|start|0||delta:count,...|once' — a
    single-tap ONE-SHOT contour on the def's init cutoff, the same musical
    space as the FC/Ed looped LFO drivers) — the MUSICAL fact; the engine
    mechanism (counters, phases, SMC) never leaves this function.
    init_plays = the number of raw play-body calls the orig's init wrapper
    makes before returning (a C24-family temporal/dispatch fact). None if
    no match."""
    t = _rd16(mem, base + 4)                     # JT play slot -> the driver
    ii = _rd16(mem, base + 1)                    # JT init slot -> init wrapper
    if not (s['load'] <= t < 0xFFE0 and s['load'] <= ii < 0xFFE0):
        return None
    if not (mem[t] == 0x20 and _rd16(mem, t + 1) == base + 0x85
            and mem[t + 3] == 0xAD and mem[t + 6] == 0xD0
            and mem[t + 8] == 0xAD and mem[t + 11] == 0xC9
            and mem[t + 13] == 0xF0 and mem[t + 15] == 0xEE
            and mem[t + 18] == 0xAD
            and _rd16(mem, t + 16) == _rd16(mem, t + 19)   # INC/LDA same cell
            and mem[t + 21] == 0xD0 and mem[t + 23] == 0xAE
            and mem[t + 26] == 0xBD and mem[t + 29] == 0xD0
            and mem[t + 31] == 0x8D
            and mem[t + 34] == 0xA9 and mem[t + 36] == 0xA0):
        return None
    tgt = _rd16(mem, t + 9)                      # the animated byte
    if _rd16(mem, t + 32) != tgt:
        return None
    if (mem[t + 35], mem[t + 37]) != (tgt >> 8, tgt & 0xFF):
        return None                              # SMC retarget aims elsewhere
    cap = mem[t + 12]
    tab = _rd16(mem, t + 27)
    phcap = idxcap = None                        # the two step-cap compares
    for off in range(0x38, 0x58):
        if mem[t + off] == 0xAD and mem[t + off + 3] == 0xC9:
            v = mem[t + off + 4]
            if phcap is None:
                phcap = v
            else:
                idxcap = v
                break
    if phcap is None or idxcap is None:
        return None
    # init wrapper: JSR base+$37 / LDA #prime / STA tgt / (JSR base+$85) x N
    if not (mem[ii] == 0x20 and _rd16(mem, ii + 1) == base + 0x37
            and mem[ii + 3] == 0xA9 and mem[ii + 5] == 0x8D
            and _rd16(mem, ii + 6) == tgt):
        return None
    prime = mem[ii + 4]
    plays = 0
    pc = ii + 8
    while mem[pc] == 0x20 and _rd16(mem, pc + 1) == base + 0x85:
        plays += 1
        pc += 3
    # the animated byte must be a filter-def record's INIT byte (offset 1 of
    # a 4-byte def record). Anything else refuses — the member stays
    # honestly partial rather than carrying a wrong deconstruction.
    filtdef = _rd16(mem, base + 0x296)
    if not (filtdef <= tgt and (tgt - filtdef) % 4 == 1
            and (tgt - filtdef) // 4 < 16):
        return None
    dnum = (tgt - filtdef) // 4
    tabbytes = [mem[tab + k] for k in range(idxcap + 1)]
    # ---- simulate the literal driver semantics; v[k] = the byte value the
    # play body of PSID play k observes (the driver runs AFTER each body).
    val, cnt, idx, ph, cell_mode = prime, 0, 0, 0, False
    series = []
    for _ in range(65536):
        series.append(val)                       # body sees current value
        if ph == 0 and val == cap:
            continue                             # halted
        if cell_mode:
            val = (val + 1) & 0xFF
            c = val
        else:
            cnt = (cnt + 1) & 0xFF
            c = cnt
        if c:
            continue
        step = tabbytes[idx] if idx < len(tabbytes) else 0
        val = step
        if step == 0:
            cell_mode = True
            ph += 1
        idx += 1
        cnt = 0
        if ph == phcap and idx == idxcap:
            cell_mode = False
            ph = 0
    # RLE-compress the deltas into C1 (delta, count) phases; stop at the
    # terminal hold (the tail where the value never changes again).
    last_change = max((k for k in range(1, len(series))
                       if series[k] != series[k - 1]), default=0)
    deltas = [(series[k] - series[k - 1]) & 0xFF
              for k in range(1, last_change + 1)]
    phases = []
    for d in deltas:
        if phases and phases[-1][0] == d and phases[-1][1] < 255:
            phases[-1][1] += 1
        else:
            phases.append([d, 1])
    if len(phases) > 100:
        return None                              # not contour-shaped: refuse
    steps = ','.join(f'{d if d < 0x80 else d - 0x100}:{n}'
                     for d, n in phases)
    return f'{dnum + 1}|{prime}|0||{steps}|once', plays


def _family2_build(mem, s, sid_path, base, delta, at, cia_period,
                   play_repeat=1):
    """Family-2 config: masked identity compare vs the carved family-2
    reference (relocation-aware), then derive the packer-patched table
    addresses from the canon-compatible operand sites. The 5 family-2
    write-stream params (cymbal_onset / vib_ramp / hold_gateoff /
    hard_restart / rest_effects) are emitted by the extract whenever
    sector_format=='family2' — see pipelines/dmc/v4/extract/to_usf.py."""
    ref, masked, reloc = _family2_ref()
    canon = bytearray(ref)
    if delta:
        for pc, val in reloc:
            nv = (val + delta) & 0xFFFF
            canon[pc - 0x1000 + 1] = nv & 0xFF
            canon[pc - 0x1000 + 2] = nv >> 8
    # the holding gate-off ($133D) varies across family-2 sub-builds: some
    # builds inline STA $100f,x (mask only), others JSR a helper that also
    # clears AD/SR=$00 (the relocated sub_17EC). Probe it; mask its 3 bytes
    # out of the code compare. (Other knobs stay validated by the compare;
    # a sub-build that varies them is rejected with a typed reason.)
    probe = set(range(0x133D, 0x1340))    # hold_gateoff variant
    probe |= set(range(0x129F, 0x12A1))   # filter-mode-extract variant
    for i in range(0x1000, _F2_INSTR_BASE):
        if masked[i] or i in probe:
            continue
        if mem[at(i)] != canon[i - 0x1000]:
            # The play-body code differs from the reference, but most diffs are
            # write-stream-BENIGN: zero-page slot ($F8->$78), SID-mirror address
            # ($D401->$D441 = same register), $D418-via-JSR-helper, relocated
            # table/state operand, or a loop-target immediate. Per the CORE TENET
            # the WRITE STREAM is the judge, not code identity — so don't
            # hard-reject: the operands extract from the canonical sites below
            # regardless, and build+verify gates the result (verify rejects the
            # real variants whose diff DOES change the writelog). Measured on the
            # 49 family-2 rejects: 21 verify FULL, 26 correctly partial, 0 false
            # accepts (a FULL = thousands of exact (reg,val) writes match). The
            # $1037-init dispatch already scopes this to family-2-signature
            # members. (Previously raised player_code_mismatch_f2 here.)
            break
    # $129F filter-mode extraction: Kajun masks `AND #$0F`; a re-assembly
    # variant uses `STA $9E` (a dead store — the following ASL x4 discards
    # the hi nibble either way, so $D418 is identical). Both equivalent, and
    # an UNKNOWN opcode here no longer refuses: the f2 philosophy is
    # verify-gated (C13 — a loosened dispatch can't false-FULL; of the 49
    # historical code-mismatch refusals, 21 verified FULL), so a third form
    # builds with the canon semantic and reads honestly partial if it
    # actually differs. (Review 2026-08-13: aligned with the $12F4 probe's
    # default-to-canon convention; previously raised filter_mode_variant.)
    gop = mem[at(0x133D)]
    if gop == 0x20:                       # JSR helper — clears AD/SR=$00
        hold_gateoff = 'adsr_clear'
    else:                                 # STA $100f,x ($9D) = the carved
        hold_gateoff = 'mask_only'        # reference's behavior; unknown
                                          # opcodes default to it (verify
                                          # judges — see $129F note above;
                                          # previously raised
                                          # hold_gateoff_unknown)
    # packer-patched table addresses (canon-compatible sites; tunetab via
    # $1051 since family 2 leaves the $180E site empty; instr base $17B0).
    instr = _rd16(mem, at(0x1227))
    wavectrl = _rd16(mem, at(0x159C))
    wavefreq = _rd16(mem, at(0x15B9))
    filtdef = _rd16(mem, at(0x1296))
    tunetab = _rd16(mem, at(0x1051))
    secp_lo = _rd16(mem, at(0x1103))
    secp_hi = _rd16(mem, at(0x1108))
    if not (base + 0x600 <= instr < base + 0x1000):
        raise DMCV4Unsupported('nonstandard_instr_base_f2', hex(instr))
    # A PACKED SUB-PLAYER can carry an out-of-image filter-def operand: the
    # packer relocated every REACHED path but left UNREACHED ones at their
    # pre-relocation addresses (Moog/Techno-Rap's second player — its filter
    # note-init never runs, so the table is never read; a --pc-trace of the
    # original shows NO execution outside the file image, and the $5xxx
    # state candidates stay $00 all song while the relocated $2xxx ones are
    # live). Drop such a pointer from the ordering chain instead of refusing
    # the whole player — the defs then read as zeros and build+verify judges
    # (C13: a loosened dispatch cannot false-FULL). An IN-IMAGE filtdef keeps
    # the strict chain, so no currently-detected member changes.
    _img_lo, _img_hi = s['load'], s['load'] + len(s['payload'])
    _chain = [instr, wavectrl, wavefreq]
    if _img_lo <= filtdef < _img_hi:
        _chain.append(filtdef)
    _chain += [tunetab, secp_lo, secp_hi]
    if not all(a < b for a, b in zip(_chain, _chain[1:])):
        raise DMCV4Unsupported(
            'layout_disorder_f2',
            f'instr=${instr:04X} wc=${wavectrl:04X} wf=${wavefreq:04X} '
            f'fd=${filtdef:04X} tt=${tunetab:04X} '
            f'sl=${secp_lo:04X} sh=${secp_hi:04X}')
    # C37-degenerate per-subtune KNOB-POKE wrapper (X-mas_Cooperation_tune_2):
    # the JT init slot (or header init) points at `TAY / LDA tab,Y / STA tgt /
    # TYA / JMP base+$37`. When tgt is the $FF track-loop handler's `LDA #imm`
    # operand (canon $10DE — the loop-to-N track position this build family
    # ships with imm=0), the poke IS a per-subtune loop target: record
    # {subtune: table[subtune]} for the non-zero entries (zero = the canon
    # default, identity — such subtunes build byte-identically).
    subtune_loop_reset = None
    for _iv in {_rd16(mem, base + 1), s['init']}:
        if not (s['load'] <= _iv < 0xFFF0):
            continue
        if (mem[_iv] == 0xA8 and mem[_iv + 1] == 0xB9 and mem[_iv + 4] == 0x8D
                and mem[_iv + 7] == 0x98 and mem[_iv + 8] == 0x4C
                and _rd16(mem, _iv + 9) == base + 0x37
                and _rd16(mem, _iv + 5) == at(0x10DE)):
            _tab = _rd16(mem, _iv + 2)
            _n = s.get('songs', 1)
            _m = {k: mem[_tab + k] for k in range(_n) if mem[_tab + k]}
            subtune_loop_reset = _m or None
            break
    return DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        base=base,
        subtune_loop_reset=subtune_loop_reset,
        op_instr=at(0x1227), op_wavectrl=at(0x159C), op_wavefreq=at(0x15B9),
        op_filtdef=at(0x1296), op_tunetab=at(0x1051),
        op_secp_lo=at(0x1103), op_secp_hi=at(0x1108),
        freq_lo_addr=at(0x1647), freq_hi_addr=at(0x16A7),
        vibdepth_addr=at(0x1888), d417_shadow_addr=at(0x1034),
        # family-2's $40 half-rate slide/vib parity lives beside its $1034
        # routing shadow (canon pairs $1018/$1019 the same way). Unset, the
        # post-init capture fell back to canon base+$19 = init-code bytes in
        # an f2 image (RE_NOTES known bug; 13 carriers censused 2026-08-12).
        dual_parity_addr=at(0x1035),
        track_loop_target=False, cia_period=cia_period,
        play_repeat=play_repeat,
        sector_format='family2',
        # $12F4 vib-swell increment: canon f2 `LSR` = freq_hi(note)>>1; the
        # Brian build variant replaces it with `TAY` (A untouched) = the FULL
        # freq_hi — a double-rate vibrato swell (4 carriers, all partial
        # before this probe). Any other opcode keeps canon (advisory compare
        # + build+verify judge, as for every f2 sub-build knob).
        extra_params={'cymbal_onset': 1,
                      'vib_ramp': ('step_full' if mem[at(0x12F4)] == 0xA8
                                   else 'step'),
                      # $11C4: the note-init `STA rampctr,x` clear re-pointed
                      # off its state var (Dreaming -> unused RAM, X-mas_end
                      # -> out of image) = the clear is DEAD, the vibrato
                      # swell counter persists across notes (legato swell,
                      # C19 clear-repointed family).
                      **({'vib_ramp_persist': 1}
                         if (mem[at(0x11C4)] == 0x9D
                             and _rd16(mem, at(0x11C5)) != base + 0x76E)
                         else {}),
                      'hold_gateoff': hold_gateoff, 'hard_restart': 'none',
                      'rest_effects': 'skip',
                      # $11BE note-init `STA $1768,x` (vib direction clear)
                      # patched to the 2-byte `EOR $68,x` (C19 — Shock/
                      # Mea_Culpa_end `55`): the stream MISALIGNS so the
                      # following `STA $176B,x` (vib half-cycle counter
                      # clear) decodes as filler too — the vibrato PHASE
                      # persists across notes; the re-aligned `STA $176E,x`
                      # (rampctr) survives. Anchor: the preceding canon
                      # `STA $1738,x` + the surviving rampctr store.
                      **({'vib_phase_persist': '1'}
                         if (mem[at(0x11BB)] == 0x9D
                             and _rd16(mem, at(0x11BC)) == base + 0x738
                             and mem[at(0x11BE)] == 0x55
                             and mem[at(0x11BF)] == 0x68
                             and mem[at(0x11C4)] == 0x9D
                             and _rd16(mem, at(0x11C5)) == base + 0x76E)
                         else {}),
                      # $12F5 vib-increment store `STA $178C,x` re-pointed
                      # to a CMP (C19 — Shade/For_Moonlight `D9`): vdep is
                      # never written per note, so the vibrato swell ramps
                      # by 0. Anchor: the $12F4 LSR/TAY + the operand still
                      # naming base+$78C (fail-open otherwise).
                      **({'vib_step_dead': '1'}
                         if (mem[at(0x12F4)] in (0x4A, 0xA8)
                             and mem[at(0x12F5)] != 0x9D
                             and _rd16(mem, at(0x12F6)) == base + 0x78C)
                         else {}),
                      # Per-voice INIT-call skip = a voice REMOVED (C24
                      # zero-count form via the INIT, not the play body —
                      # Riot/Koshimo_preview_1: the first of the three
                      # `JSR base+$B0` per-voice init calls at base+$95/
                      # $99/$9D is re-pointed at base+$AF = the filter
                      # tail's RTS, so that voice's vactive is never set
                      # and it emits ZERO writes all song; the composer's
                      # canonical build would run a phantom voice). A call
                      # is intact iff its JSR/JMP targets base+$B0; any
                      # other target = voice removed. Fires only when some
                      # voice is skipped (else byte-identical).
                      **({'play_unit_repeat': _pur}
                         if (_pur := _f2_init_skip_units(mem, at, base))
                         else {}),
                      # $12A8 filter note-init `STA $D418` KILLED (C19 —
                      # Third_Zak's `85 xx` zp-redirect / Chance_for_Win's
                      # `EA EA EA` NOP; the INIT master-vol store at base+$5C
                      # survives, so $D418 = mvol from init on, never
                      # mode|vol). Anchor on the preceding canon
                      # `ORA $1717` (reloc-aware) so a re-assembled layout
                      # fails open; the killed forms are the two observed.
                      **({'d418_noteinit_dead': 1}
                         if (mem[at(0x12A5)] == 0x0D
                             and _rd16(mem, at(0x12A6)) == base + 0x717
                             and mem[at(0x12A8)] in (0xEA, 0x85))
                         else {}),
                      # $10A3 play filter tail `STA $D416` NOPed (C19 —
                      # SilverFox/No_End; the $D417 store at base+$AC
                      # survives): cutoff set once at init, never during
                      # play. Anchor on the canon cutoff LOAD before it.
                      **({'filter_cut_static': 1}
                         if (mem[at(0x10A0)] == 0xAD
                             and _rd16(mem, at(0x10A1)) == base + 0x71C
                             and mem[at(0x10A3)] == 0xEA
                             and mem[at(0x10A4)] == 0xEA
                             and mem[at(0x10A5)] == 0xEA)
                         else {}),
                      # $11D9 fetch-frame prep ctrl `LDA #imm / STA $D404,Y`
                      # (canon imm $08 = TEST). Rowdy's $F000 sub-player
                      # patches the immediate to $40 (C19 patched-immediate
                      # wedge). Anchor on the LDA# + STA $D404,Y shape so a
                      # re-assembled layout fails open; emit only non-canon.
                      **({'prep_ctrl': mem[at(0x11DA)]}
                         if (mem[at(0x11D9)] == 0xA9
                             and mem[at(0x11DB)] == 0x99
                             and _rd16(mem, at(0x11DC)) == 0xD404
                             and mem[at(0x11DA)] != 0x08)
                         else {}),
                      **(dict(zip(('filter_mod', 'init_plays'),
                                  _fdc))
                         if (_fdc := _fdinit_contour_probe(mem, s, base))
                         else {}),
                      **({'filter_mod': _cta}
                         if (_cta := _cutoff_table_anim_probe(mem, s, base))
                         else {})},
    )


def _f2_init_skip_units(mem, at, base):
    """C24 zero-count units at the f2 play body's voice-call chain
    (Riot/Koshimo_preview_1): the three per-voice calls `JSR base+$B0` at
    base+$95/$99/$9D, falling through into the filter tail (base+$A0) and
    its RTS (base+$AF). Two wedge forms, both observed on Koshimo:
    - a voice call re-pointed at base+$AF (the RTS) = that voice runs
      NOTHING, zero writes all song (the canonical build runs a phantom
      voice);
    - the LAST call's JSR patched to JMP (a tail-call) = the fall-through
      into the filter tail never happens, so $D416/$D417 are never
      written = the FILTER unit removed.
    A call is intact iff it targets base+$B0; removed iff it JSRs
    base+$AF; ANY other shape aborts (fail-open — re-assembled bodies must
    not read as removals). Returns 'v0,v1,v2,f' when any unit is removed,
    else None (canon → no param, byte-identical)."""
    counts = []
    for v in range(3):
        op = mem[at(0x1095 + 4 * v)]
        tgt = _rd16(mem, at(0x1096 + 4 * v))
        if op in (0x20, 0x4C) and tgt == base + 0xB0:
            counts.append('1')
        elif op == 0x20 and tgt == base + 0xAF:
            counts.append('0')
        else:
            return None
    filt = '0' if mem[at(0x109D)] == 0x4C else '1'
    counts.append(filt)
    return ','.join(counts) if '0' in counts else None


def _cutoff_table_anim_probe(mem, s, base):
    """SilverFox/No_End appended cutoff-table cycler, DECONSTRUCTED to
    musical content (ledger C1 + C19 33rd-occurrence rule; the canon play
    filter tail's `STA $D416` is NOPed — filter_cut_static — and this
    wrapper is the only cutoff writer). Play vector:
        LDX #x0 / LDA tab,X / STA $D416 / INC <the LDX operand> / JMP base+3
    and the init vector JMPs a stub that re-seeds the SMC operand:
        LDX #x0 / STX <play+1> / LDA #$00 / JMP base
    = one authored 256-entry cutoff table cycled at 1 entry/play, forever.
    Emitted as a `filter_mod` DIRECT entry ('target: cutoff'): start =
    tab[x0], steps = the delta-run encoding of one full cycle (exact by
    construction; sum of deltas wraps to 0 mod 256). Returns the encoded
    string, else None (build unchanged)."""
    P = s['play']
    if not (mem[P] == 0xA2 and mem[P + 2] == 0xBD and mem[P + 5] == 0x8D
            and _rd16(mem, P + 6) == 0xD416 and mem[P + 8] == 0xEE
            and _rd16(mem, P + 9) == P + 1 and mem[P + 11] == 0x4C
            and _rd16(mem, P + 12) == base + 3):
        return None
    I = s['init']
    if mem[I] == 0x4C:
        I = _rd16(mem, I + 1)
    if not (mem[I] == 0xA2 and mem[I + 2] == 0x8E
            and _rd16(mem, I + 3) == P + 1):
        return None
    x0 = mem[I + 1]
    tab = _rd16(mem, P + 3)
    vals = [mem[tab + ((x0 + i) & 0xFF)] for i in range(257)]
    runs = []
    for i in range(256):
        d = (vals[i + 1] - vals[i]) & 0xFF
        d = d - 256 if d >= 128 else d
        if runs and runs[-1][0] == d:
            runs[-1][1] += 1
        else:
            runs.append([d, 1])
    steps = ','.join(f'{d}:{f}' for d, f in runs)
    return f'0|{vals[0]}|0||{steps}|direct'
