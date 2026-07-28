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
        return 19656 // n - 1
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
    $D400,y; STA $D401,y; LDA #$81; STA $D404,y). Canon is $FF; a few demos
    patch it for a different noise timbre (e.g. Presentation's $DF). Read from
    the file image so it is layout-independent. None if the pattern is absent."""
    import re
    data = open(path, 'rb').read()
    doff = int.from_bytes(data[6:8], 'big')
    m = re.search(rb'\xa9(.)\x99\x00\xd4\x99\x01\xd4\xa9\x81\x99\x04\xd4',
                  data[doff:])
    return m.group(1)[0] if m else None


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
    — Sans_intro (fall-through form) + Devilock/Sub_Effect (JMP-to-base form)."""
    mem, s = _load(path, post_init_sub)
    init = s['init']
    if init == base or not (0 <= init and init + 4 <= 0xFFFF):
        return None
    if mem[init] != 0xA9:                          # LDA #imm
        return None
    # base must be the standard tune-select dispatch: JMP base+$1D
    if not (mem[base] == 0x4C and
            (mem[base + 1] | (mem[base + 2] << 8)) == (base + 0x1D) & 0xFFFF):
        return None
    nxt = init + 2                                 # LDA #imm must REACH base
    reaches = (nxt == base or
               (mem[nxt] == 0x4C and
                (mem[nxt + 1] | (mem[nxt + 2] << 8)) == base))
    return mem[init + 1] if reaches else None


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
             (0x1015, 'curinst', 3)]
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
    is patched to `A9 00 / 4C <init>` (JMP straight to init; the canon re-fetch
    tail left as dead code) — vs shape A's byte-preserving neutered-JSR form.
    Because the wrap voice is not the last play unit, the restart also runs the
    remaining voices as GHOST units (see `_simulate_reinit_ghosts`).

    STATIC anchor for the shape (LDA #$00 + JMP away from the canon re-fetch),
    then the ghost sim GATES on the wrap being in the verify window (its burst
    capture returns None past-window) and captures the burst + pokes. Returns
    the `track_ff_reinit_ghost` spec, or None (not shape B / past window / no
    ghost tail — every non-For_Party carrier stays byte-identical)."""
    if base is None:
        return None
    mem, _ = _load(path, post_init_sub)
    site = base + 0xDD
    if site + 5 > 0x10000:
        return None
    if mem[site] != 0xA9 or mem[site + 1] != 0x00 or mem[site + 2] != 0x4C:
        return None
    jmp_tgt = mem[site + 3] | (mem[site + 4] << 8)
    if jmp_tgt == base + 0xD2:                    # canonical re-fetch loop
        return None
    # the JMP must lead to init: the member's init vector (base = `JMP body`)
    # or that body itself. A false lead yields a partial, never a wrong FULL.
    init_body = mem[base + 1] | (mem[base + 2] << 8) if mem[base] == 0x4C else None
    if jmp_tgt != base and jmp_tgt != init_body:
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
    """$D418 play-vector wrapper probe: the PSID play address points at
    `LDA #imm / STA $D418 / JMP base+3` (PVCF / Zyron / Signor) — a constant
    master-vol|filter-mode write on every play() call before the canon play
    body. Returns imm, or None when the play vector isn't this shape."""
    mem, s = _load(path, post_init_sub)
    p = s['play']
    if (mem[p] == 0xA9 and bytes(mem[p + 2:p + 5]) == b'\x8d\x18\xd4'
            and mem[p + 5] == 0x4C
            and mem[p + 6] | (mem[p + 7] << 8) == base + 3):
        return mem[p + 1]
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
    Cymbal (noise-burst) inits write freq+ctrl=$81 ON the init frame in BOTH
    variants (the composer's cym_ni path already bursts + RTSes), so
    burst-shaped chunks (ctrl $81 + both freq bytes) are excluded from the
    classification. `noteinit_defer_wave='1'` needs >= 8 MELODIC init
    chunks with NONE carrying a ctrl write. A canon member's melodic inits
    always carry ctrl, so any such chunk disqualifies — an exotic
    hard-restart preset or a noise-only member cannot false-fire (they
    yield 0 melodic chunks = the canon default).

    The SAME capture also classifies the hard-restart PREP chunks (AD=SR=
    $0F): the build writes ctrl $08 THEN $09 (TEST, then TEST|GATE) where
    canon writes $08 alone — `hr_prep_gate='1'` when >= 8 prep chunks all
    show the exact [$08, $09] ctrl sequence.

    Returns a (possibly empty) dict of composer params."""
    from pipelines.hubbard.verify_cycle import writelog_per_irq_capture
    try:
        frames = writelog_per_irq_capture(path, subtune=subtune,
                                          duration=10.0)
    except Exception:
        return {}
    inits = with_ctrl = preps = preps_gate9 = 0
    for fr in frames:
        per, ctrls = {}, {}
        for _cyc, reg, val in fr:      # reg = $D4xx offset (0-$18)
            if 0 <= reg <= 0x14:
                v, r = divmod(reg, 7)
                per.setdefault(v, {})[r] = val
                if r == 4:
                    ctrls.setdefault(v, []).append(val)
        for v, regs in per.items():
            if 5 not in regs or 6 not in regs:
                continue
            if (regs[5], regs[6]) == (0x0F, 0x0F):
                preps += 1
                if ctrls.get(v) == [0x08, 0x09]:
                    preps_gate9 += 1
                continue
            if (regs[5], regs[6]) == (0x00, 0x00):
                continue
            if regs.get(4) == 0x81 and 0 in regs and 1 in regs:
                continue                   # cymbal burst — both variants
            inits += 1
            if 4 in regs:
                with_ctrl += 1
    out = {}
    if inits >= 8 and with_ctrl == 0:
        out['noteinit_defer_wave'] = '1'
    if preps >= 8 and preps_gate9 == preps:
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
                    name: str, chip_addr: int = 0) -> DMCV4Config:
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
                               chip_addr=chip_addr)
        cfg.name = name
        # `_build_via_canon` sits BELOW the caller that runs the C19 wedge
        # probes, so a sub-player built straight off it had every wedge knob
        # defaulted (see _apply_wedge_probes). Probe against THIS chip's base.
        _apply_wedge_probes(os.path.join(hvsc_root, sid_path), cfg)
        return cfg
    except DMCV4Unsupported:
        pass
    d = base - 0x1000
    at = lambda a: a + d                                       # noqa: E731
    # The bare fallback still runs the STANDALONE static probes — a knob left
    # at its default here is silently wrong music, not a refusal (the track
    # loop target decides whether the song repeats its whole orderlist or the
    # tail from a stated position).
    mem = _load(os.path.join(hvsc_root, sid_path))[0]
    cfg = DMCV4Config(
        sid_path=sid_path, name=name, base=base,
        op_instr=at(0x1227), op_wavectrl=at(0x159C), op_wavefreq=at(0x15B9),
        op_filtdef=at(0x1296), op_tunetab=at(0x180E),
        op_secp_lo=at(0x1103), op_secp_hi=at(0x1108),
        freq_lo_addr=at(0x1647), freq_hi_addr=at(0x16A7),
        vibdepth_addr=at(0x1888), d417_shadow_addr=at(0x1018),
        track_loop_target=_loop_target_probe(mem, base),
        switch_retrig=_switch_retrig_probe(mem, base))
    _apply_wedge_probes(os.path.join(hvsc_root, sid_path), cfg)
    return cfg


def dmc_v4_config_2sid(sid_path: str, hvsc_root: str = 'hvsc84'):
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
    # The observer finds a player wherever it RUNS, including one an init
    # COPIES out of the image (Surgeon/Mothafucka relocates chip 2 to $E800,
    # zero-fill in the file). Extracting that chip needs the C26 post-init
    # RAM path, which this constructor does not do — its tables would read as
    # zeros — so refuse the member here and let it fall back to the
    # single-chip build it had before, rather than raising mid-extract.
    if not all(mem[b] == 0x4C and mem[b + 3] == 0x4C for b in bases):
        return None
    base0 = os.path.splitext(os.path.basename(sid_path))[0]
    addrs = [0xD400, _sid_header_multi(path)[1], _sid_header_multi(path)[2]]
    cfgs = [_config_at_base(sid_path, hvsc_root, b, f'{base0}_chip{i + 1}',
                            chip_addr=addrs[i])
            for i, b in enumerate(bases)]
    # CIA multispeed (C9: measure, don't assume). The dispatch wrapper is
    # driven by the timer it programs at init, and a C18 phase schedule
    # DIVIDES that rate (Rayden: latch $2663 = 100Hz with a period-2 P_F123
    # schedule, or $1331 = 200Hz with period 4 — both a 50Hz music tick).
    # Built as vblank, such a member plays at 1/N speed: a per-chip EXACT
    # PREFIX of ~1/N the original's length, with no content divergence.
    cia = 0
    if s.get('speed', 0) & 1:
        cp = _cia_period_from_init(path, 0)
        if not (0x0100 <= cp <= 0xFFFF):
            cp = _cia_period_from_writelog(path, 0)
        if 0x0100 <= cp <= 0xFFFF:
            cia = cp
    for ci, cfg in enumerate(cfgs):
        cfg.cia_period = cia
        keep = _multisid_keep_regs(mem, cfg.base, addrs[ci])
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
_WEDGE_PROBES = [
    ('master_vol_every_play',           lambda p, c: _d418_play_wrapper(p, c.base, c.post_init_sub)),
    ('master_vol_reassert_filter_tail', lambda p, c: _d418_filter_tail_probe(p, c.base, c.post_init_sub)),
    ('hold_gateoff',                    lambda p, c: _hold_gateoff_probe(p, c.base, c.post_init_sub)),
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
    ('v3_instr_tempo',                  lambda p, c: _v3_instr_tempo_probe(p, c.base, c.post_init_sub)),
    ('filterdef_anim',                  lambda p, c: _filterdef_anim_probe(p, c.base, c.op_filtdef, c.post_init_sub)),
    ('d417_tail_anim',                  lambda p, c: _d417_tail_anim_probe(p, c.base, c.op_filtdef, c.op_wavefreq, c.post_init_sub)),
    ('filterdef_anim3',                 lambda p, c: _filterdef_anim3_probe(p, c.base, c.op_filtdef, c.post_init_sub)),
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


def dmc_v4_config(sid_path: str, hvsc_root: str = 'hvsc84',
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
    # cymbal noise-burst timbre: only when patched off the canon $FF.
    cb = _cymbal_burst_byte(path)
    if cb is not None and cb != 0xFF:
        cfg.extra_params['cymbal_burst'] = cb
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
    # forced_subtune is a cfg ATTRIBUTE, not a param; 0 == the default walk.
    fs = _forced_subtune_probe(path, cfg.base, post_init_sub)
    if fs:
        cfg.forced_subtune = fs
    # C37 save-state resume wrapper: every subtune plays the forced song,
    # differentiated only by the wrapper's surviving state copy.
    sr = _state_resume_probe(path, cfg.base, post_init_sub)
    if sr is not None:
        cfg.forced_subtune, cfg.subtune_state_copy = sr
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
        cp = _cia_period_from_init(os.path.join(hvsc_root, sid_path),
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
            cfg.extra_params['play_phases'] = ph
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


def _build_via_canon(sid_path: str, hvsc_root: str = 'hvsc84',
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
        cia_period = _cia_period_from_init(
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
    # the hi nibble either way, so $D418 is identical). Both equivalent.
    fmop = mem[at(0x129F)]
    if not ((fmop == 0x29 and mem[at(0x129F) + 1] == 0x0F) or fmop == 0x85):
        raise DMCV4Unsupported('filter_mode_variant', hex(fmop))
    gop = mem[at(0x133D)]
    if gop == 0x9D:                       # STA $100f,x — mask only
        hold_gateoff = 'mask_only'
    elif gop == 0x20:                     # JSR helper — clears AD/SR=$00
        hold_gateoff = 'adsr_clear'
    else:
        raise DMCV4Unsupported('hold_gateoff_unknown', hex(gop))
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
    if not (instr < wavectrl < wavefreq < filtdef < tunetab
            < secp_lo < secp_hi):
        raise DMCV4Unsupported(
            'layout_disorder_f2',
            f'instr=${instr:04X} wc=${wavectrl:04X} wf=${wavefreq:04X} '
            f'fd=${filtdef:04X} tt=${tunetab:04X} '
            f'sl=${secp_lo:04X} sh=${secp_hi:04X}')
    return DMCV4Config(
        sid_path=sid_path,
        name=os.path.splitext(os.path.basename(sid_path))[0],
        base=base,
        op_instr=at(0x1227), op_wavectrl=at(0x159C), op_wavefreq=at(0x15B9),
        op_filtdef=at(0x1296), op_tunetab=at(0x1051),
        op_secp_lo=at(0x1103), op_secp_hi=at(0x1108),
        freq_lo_addr=at(0x1647), freq_hi_addr=at(0x16A7),
        vibdepth_addr=at(0x1888), d417_shadow_addr=at(0x1034),
        track_loop_target=False, cia_period=cia_period,
        play_repeat=play_repeat,
        sector_format='family2',
        extra_params={'cymbal_onset': 1, 'vib_ramp': 'step',
                      'hold_gateoff': hold_gateoff, 'hard_restart': 'none',
                      'rest_effects': 'skip'},
    )
