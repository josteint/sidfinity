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


def _load(sid_path: str):
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
                         n_calls: int = 12,
                         max_steps: int = 200_000):
    """OBSERVE a play-vector wrapper's phase behaviour (C9: measure, don't
    parse). Some canon members ship a PLAY WRAPPER (play != base+3) that
    cycles a counter and runs the FULL canon play only every Nth call,
    dispatching the other calls to a per-voice frame-entry stub (effects
    only, no tick, no $D416/$D417 tail) hidden in a compare-masked region
    (the copyright string, the re-authored all-off slot) — the DMC
    'multispeed effects / slow tempo' editing trick. Wrapper SHAPES vary
    (SMC JSR-operand table, DEC counter + dual JMP, INC+AND) so parsing is
    fragile; instead run init then call play() n times under py65 and
    classify each call by the engine entry it reaches:
        P = the full play body (base+$85)
        F = the per-voice frame entry (base+$1F9) without the play body
        S = neither (silent no-op)
    Returns the minimal repeating period as a 'PFFF'-style string, or None
    when observation fails / the sequence doesn't settle into a period.
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

    def run(pc, acc):
        mpu.stPush(0x00)
        mpu.stPush(0x00)           # RTS sentinel -> PC = $0001
        mpu.pc = pc
        mpu.a = acc
        hit_play = False
        fx_voices = set()          # X values seen at the frame entry
        rf_voices = set()          # X values seen at the glide/write tail
        for _ in range(max_steps):
            if mpu.pc == 0x0001:
                return hit_play, fx_voices, rf_voices
            if mpu.pc == base + 0x85:
                hit_play = True
            elif mpu.pc == base + 0x1F9:
                fx_voices.add(mpu.x & 0x03)
            elif mpu.pc == base + 0x41C:
                rf_voices.add(mpu.x & 0x03)
            try:
                mpu.step()
            except Exception:
                return None
        return None

    if run(s['init'], subtune) is None:
        return None
    seq = []
    for _ in range(n_calls):
        r = run(s['play'], 0)
        if r is None:
            return None
        hp, fv, rv = r
        if hp:
            seq.append('P')
        elif fv:                   # F + the voice set it ran (stubs vary:
            seq.append('F' + ''.join(str(v + 1)  # some NOP out a voice)
                              for v in sorted(fv)))
        elif rv:                   # R = register REFRESH: the wrapper calls
            seq.append('R' + ''.join(str(v + 1)  # the per-voice glide/write
                              for v in sorted(rv)))  # tail ($141C) directly —
        else:                      # re-emits current freq/PW/ctrl (Toccata's
            seq.append('S')        # re-authored all-off slot: LDX/JSR $141C x3)
    for p in range(1, n_calls // 2 + 1):
        if all(seq[i] == seq[i % p] for i in range(n_calls)):
            return '_'.join(seq[:p])
    return None


def _observe_play_phases_writes(sid_path: str, subtune: int,
                                n_calls: int = 12,
                                max_steps: int = 200_000):
    """OFFSET-BLIND play-phase observation for RE-ASSEMBLED (dataflow-route)
    members, where the canon entry-point offsets don't hold. Classify each
    play() call by its SID-WRITE FOOTPRINT instead of PCs:
      P = writes $D416 (the canon play body's unconditional global-filter
          tail — the per-voice frame entry and the refresh stub never reach it)
      F<voices> = per-voice writes without the $D416 tail, values ADVANCING
          vs the previous call (effects ran)
      R<voices> = per-voice writes identical in value to the previous call's
          per-voice writes (pure register refresh, no state advance)
      S = no SID writes.
    Same 'P_F123...' output as _observe_play_phases; the verify gate is the
    net for any misclassification (C18: observe, don't parse)."""
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__),
                                    '..', '..', '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mpu = MPU()
    mem = ObservableMemory()
    writes = []
    mem.subscribe_to_write(range(0xD400, 0xD419),
                           lambda addr, val: writes.append((addr, val)))
    for i, b in enumerate(s['payload']):
        if s['load'] + i < 0x10000:
            mem[s['load'] + i] = b
    mpu.memory = mem

    def run(pc, acc):
        mpu.stPush(0x00)
        mpu.stPush(0x00)           # RTS sentinel -> PC = $0001
        mpu.pc = pc
        mpu.a = acc
        del writes[:]
        for _ in range(max_steps):
            if mpu.pc == 0x0001:
                return list(writes)
            try:
                mpu.step()
            except Exception:
                return None
        return None

    init_writes = run(s['init'], subtune)
    if init_writes is None:
        return None
    # R vs F by CHIP STATE, not the previous call's write set: a pure register
    # refresh can only re-emit values already on the chip, while an effects
    # call (wave-step) eventually writes a value that DIFFERS from the current
    # register content (e.g. a chord program stepping +3). Comparing against
    # the previous call misreads a wave-step whose early steps repeat values
    # (chord [0,0,0,3,...]) as R — Bladeswede played its arpeggio's first tone
    # forever. A true refresh can never be misread as F under this rule.
    chip = {}
    for a, v in init_writes:
        chip[a & 0x1F] = v
    seq = []
    for _ in range(n_calls):
        w = run(s['play'], 0)
        if w is None:
            return None
        if not w:
            seq.append('S')
            continue
        regs = {a & 0x1F for a, _ in w}
        advancing = False
        for a, v in w:
            if (a & 0x1F) in chip and chip[a & 0x1F] != v:
                advancing = True
            chip[a & 0x1F] = v
        if 0x16 in regs:
            seq.append('P')
        else:
            voices = sorted({r // 7 for r, _ in
                             ((a & 0x1F, v) for a, v in w) if r < 21})
            vs = ''.join(str(v + 1) for v in voices)
            seq.append(('F' if advancing else 'R') + vs)
    # Period fit on a COLLAPSED key (F<v>/R<v> both -> 'x<v>'): an effects
    # phase reads R on occurrences where its program happens to repeat values,
    # which would spuriously break the raw-token period. Once fit, a position
    # is F if ANY occurrence advanced (a refresh can never advance), else R.
    def _key(t):
        return t if t in ('P', 'S') else 'x' + t[1:]
    keys = [_key(t) for t in seq]
    for p in range(1, n_calls // 2 + 1):
        if not all(keys[i] == keys[i % p] for i in range(n_calls)):
            continue
        out = []
        for k in range(p):
            toks = [seq[i] for i in range(k, n_calls, p)]
            if toks[0] in ('P', 'S'):
                out.append(toks[0])
            else:
                anyF = any(t[0] == 'F' for t in toks)
                out.append(('F' if anyF else 'R') + toks[0][1:])
        return '_'.join(out)
    return None


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

    Same 'P_F123'-style output + minimal-period fit as _observe_play_phases_writes
    (P = the $D416 filter tail; F<voices>/R<voices>/S). The verify gate is the
    net for any misclassification (C18: observe, don't parse). Returns None when
    the sequence doesn't settle into a clean period from call 0."""
    try:
        from pipelines.hubbard.verify_cycle import pctrace_per_play_capture
        # ~2 invocations per 50 Hz frame under 2x CIA; capture enough for a
        # period<=n_calls//2 fit plus headroom.
        plays = pctrace_per_play_capture(sid_path, subtune, play_addr,
                                         n_frames=max(10, n_calls))
    except Exception:
        return None
    if len(plays) < 8:
        return None
    # R vs F by CHIP STATE (same rule as _observe_play_phases_writes): a pure
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
    for w in plays[:n_calls]:
        regs = {r for r, _ in w}
        advancing = False
        for r, v in w:
            if r in chip and chip[r] != v:
                advancing = True
            chip[r] = v
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


def _detect_play_repeat(mem, play: int, base: int, load: int) -> int:
    """INTERNAL multispeed: a play vector that is N consecutive `JSR T` (same
    target T) terminated by RTS runs the engine N times per VBI (e.g. High_Speed
    play=$1E80 = `JSR $1003` x4 : RTS). Returns N (>=2) or 1. A leading JMP at
    the play vector is followed once. Verify-gated: a misread N yields a partial.
    """
    if play == base + 3:
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


def _hr_patch_probe(path: str, base: int):
    """Hard-restart-patch variant probe (The_Syndrom / Tragic_Error /
    Gaston, 24 members): note-init has `JMP base+$262` at base+$257 (skips
    the PW step-base load + phase/direction reset) and the base+$25A wedge
    parks SR at base+$40 then feeds #$99 to sub_184B, whose first STA is
    retargeted at the hard-restart primer's ctrl-write OPCODE (base+$7FB,
    SMC: $99 = STA -> TEST written, $B9 = LDA -> TEST skipped; toggled per
    note-init by the instrument's $04 flag). Returns the initial toggle
    (1 iff the file-image opcode is $99) or None when not this variant."""
    mem, _ = _load(path)
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


def _hold_gateoff_probe(path: str):
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
    shape probe misses."""
    mem, _ = _load(path)
    m = _HOLD_BRANCH.search(bytes(mem))
    if not m:
        return None
    t = m.group(1)[0] | (m.group(1)[1] << 8)
    if mem[t] == 0x9D and mem[t + 3] == 0x60:
        return 'mask_only'
    return None


# sub_17FB hard-restart prime: `STA $D404,y / LDA #$0F / STA $D405,y /
# STA $D406,y / RTS`. First opcode admits $B9 too — the _hr_patch_probe
# variant SMC-toggles it STA<->LDA. Group(1) = the AD/SR immediate.
_HR_PRIME = re.compile(rb'[\x99\xB9]\x04\xD4\xA9(.)\x99\x05\xD4\x99\x06\xD4\x60',
                       re.DOTALL)


def _hr_preset_probe(path: str):
    """Hard-restart AD/SR immediate probe (STATIC opcode probe, C19 5th
    occurrence — Stryyker/Proportional_Text_Writer): the member patches ONE
    byte, sub_17FB's `LDA #$0F` immediate ($17FF), so the hard-restart prime
    writes AD=SR=that value on every note-fetch frame. Anchor on the
    routine's opcode shape (layout-blind); return the immediate when it
    differs from the canon $0F, else None (build unchanged)."""
    mem, _ = _load(path)
    m = _HR_PRIME.search(bytes(mem))
    if m is None or m.group(1)[0] == 0x0F:
        return None
    return m.group(1)[0]


_PW_HI_WRITE = re.compile(rb'\xBD(..)\x99\x02\xD4\xBD(..)\x99\x03\xD4',
                          re.DOTALL)


def _pw_hi_const_probe(path: str, base: int):
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
    mem, s = _load(path)
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


def _filter_mod_probe(path: str, op_filtdef: int):
    """Detect the filter-def modulation wrapper and lift its LFO as musical
    content: return 'prog|start|init_phase|stop_phase|d:f,d:f,...' (the
    contour value at position 0, the two taps' start phases, and the
    piecewise-constant-rate delta runs over one period), or None (build
    unchanged). The contour bytes come from the post-init RAM (the table is
    generated by the member's init wrapper); the probe validates that the
    SMC automaton targets exactly the reader's two LDA operands and that the
    stores hit filterdef + 16n + 1 / + 3 (the init/stop cutoff bytes of one
    definition)."""
    mem, s = _load(path)
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


# The dual-effect wedge: canon `LDY $170D,x / LDA $172F,x / ... / STA $1724`
# byte-edited into `LDY $170D,x / LDX $2F / ADC #$18 / ADC $1735,x / STA <tgt>`
# (opcode BD->A6 turns the base-freq load into `LDX $2F`, re-indexing every
# subsequent per-voice read +$A9 past the state arrays — onto fixed CODE
# bytes). Anchor on the wedge itself; group(1) = the repointed STA operand.
_DUAL_HACK_SITE = re.compile(rb'\xBC\x0D.\xA6\x2F\x69\x18\x7D\x35.\x8D(..)',
                             re.DOTALL)


def _dual_freq_gen_probe(path: str, base: int, freq_lo: int):
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
    mem, s = _load(path)
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


def _d418_play_wrapper(path: str, base: int):
    """$D418 play-vector wrapper probe: the PSID play address points at
    `LDA #imm / STA $D418 / JMP base+3` (PVCF / Zyron / Signor) — a constant
    master-vol|filter-mode write on every play() call before the canon play
    body. Returns imm, or None when the play vector isn't this shape."""
    mem, s = _load(path)
    p = s['play']
    if (mem[p] == 0xA9 and bytes(mem[p + 2:p + 5]) == b'\x8d\x18\xd4'
            and mem[p + 5] == 0x4C
            and mem[p + 6] | (mem[p + 7] << 8) == base + 3):
        return mem[p + 1]
    return None


def _play_unit_repeat_probe(path: str, base: int):
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
    mem, s = _load(path)
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
    sites = []                    # (site_addr, target) per per-voice JSR
    for _ in range(20):
        op = mem[q]
        if op == 0x20:            # JSR abs = a per-voice call
            sites.append((q, mem[q + 1] | (mem[q + 2] << 8))); q += 3
        elif op == 0xE8:          # INX = step to the next voice
            q += 1
        else:
            break
        if len(sites) >= 3:
            break
    if len(sites) < 3:
        return None
    vaddr = sites[0][1]
    filter_tail_addr = sites[2][0] + 3   # the play body continues here
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

    reps = [_count(i, t) for i, (_, t) in enumerate(sites)]
    if any(r is None for r in reps):
        return None
    units = reps + filt
    if all(u == 1 for u in units):
        return None
    return ','.join(str(u) for u in units)


def dmc_v4_config(sid_path: str, hvsc_root: str = 'hvsc84') -> DMCV4Config:
    """Primary canonical-layout build; on a moved-layout rejection, fall back
    to the layout-independent dataflow extractor (pipelines.dmc.v4.dataflow).

    hold_gateoff: the STATIC opcode probe (_hold_gateoff_probe) detects the
    1-byte sub_17EC patch ($17EF BC->60 = mask_only) directly — it reads the
    patched instruction, so it cannot false-negative on late-gate-off members
    (unlike a bounded write-stream scan). The verify batch's frames_clear_adsr
    mask_only retry remains as the fallback for shapes the probe misses."""
    try:
        cfg = _build_via_canon(sid_path, hvsc_root)
    except DMCV4Unsupported as e:
        if e.reason not in _DATAFLOW_RETRY:
            raise
        cfg = _build_via_dataflow(sid_path, hvsc_root)
        if cfg is None:
            raise
    # extracted per-member cymbal noise-burst value (canon $FF; rare patches)
    cb = _cymbal_burst_byte(os.path.join(hvsc_root, sid_path))
    if cb is not None and cb != 0xFF:
        cfg.extra_params['cymbal_burst'] = cb
    hr = _hr_patch_probe(os.path.join(hvsc_root, sid_path), cfg.base)
    if hr is not None:
        cfg.extra_params['hr_patch'] = 1
        cfg.extra_params['hr_test_init'] = hr
    dp = _d418_play_wrapper(os.path.join(hvsc_root, sid_path), cfg.base)
    if dp is not None:
        cfg.extra_params['d418_every_play'] = dp
    hg = _hold_gateoff_probe(os.path.join(hvsc_root, sid_path))
    if hg is not None:
        cfg.extra_params['hold_gateoff'] = hg
    # family-2 sets hard_restart='none' (no sub_17FB at all) — never override
    if 'hard_restart' not in cfg.extra_params:
        hrv = _hr_preset_probe(os.path.join(hvsc_root, sid_path))
        if hrv is not None:
            cfg.extra_params['hard_restart'] = str(hrv)
    pur = _play_unit_repeat_probe(os.path.join(hvsc_root, sid_path), cfg.base)
    if pur is not None:
        cfg.extra_params['play_unit_repeat'] = pur
    pwc = _pw_hi_const_probe(os.path.join(hvsc_root, sid_path), cfg.base)
    if pwc is not None:
        cfg.extra_params['pw_hi_const'] = pwc
    dh = _dual_freq_gen_probe(os.path.join(hvsc_root, sid_path), cfg.base,
                          cfg.freq_lo_addr)
    if dh is not None:
        cfg.extra_params['dual_freq_generator'] = dh
    fm = _filter_mod_probe(os.path.join(hvsc_root, sid_path), cfg.op_filtdef)
    if fm is not None:
        cfg.extra_params['filter_mod'] = fm
    return cfg


def _build_via_dataflow(sid_path: str, hvsc_root: str):
    """Build a config by locating every table via opcode-skeleton signatures
    (handles re-assembled players whose routines + operand sites moved). Returns
    None if the base or any table can't be located; the verify gate is the net."""
    from pipelines.dmc.v4 import dataflow
    mem, s = _load(os.path.join(hvsc_root, sid_path))
    load = s['load']

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
        extra_params=_dataflow_knob_probes(mem, load), **loc)
    # PLAY-PHASE wrapper on the RE-ASSEMBLED route (C18): canon entry-point
    # offsets don't hold here, so observe by SID-write footprint instead of
    # PCs (P = the $D416 global-filter tail; F/R = per-voice writes without
    # it). E.g. Arrive: CIA 6x with full play every 6th call, effects-only
    # between — without the knob the rebuild ticks 6x too fast.
    if cfg.play_repeat == 1:
        ph = _observe_play_phases_writes(os.path.join(hvsc_root, sid_path),
                                         s['start'] - 1)
        # py65 couldn't observe (None) OR observed an 'S' (silent) frame — under
        # py65 a CIA/IRQ-armed member's effect frames don't run, so they read as
        # S; the ground-truth pc-trace shows they actually run effects (F/R). In
        # both cases fall back to the straddle-free pc-trace observer and adopt
        # its clean, S-free P-cycle. Verify-gated; a clean non-S py65 answer is
        # left untouched.
        if ph is None or 'S' in (ph or ''):
            pf = _observe_play_phases_pctrace(
                os.path.join(hvsc_root, sid_path), s['start'] - 1, s['play'])
            if pf and '_' in pf and 'P' in pf.split('_') and 'S' not in pf:
                ph = pf
        if (ph and '_' in ph and 'P' in ph.split('_')):
            cfg.extra_params['play_phases'] = ph
            # Per-member: does the F phase DEFER note-init (the 2-frame arm)?
            # Only F-token schedules have the ambiguity (the arm lives on an F
            # call). Observe it — not derivable from the schedule/multispeed.
            if any(t and t[0] == 'F' for t in ph.split('_')) and \
                    _detect_notestart_arm(os.path.join(hvsc_root, sid_path),
                                          s['start'] - 1, s['play']):
                cfg.extra_params['notestart_arm'] = '1'
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


def _build_via_canon(sid_path: str, hvsc_root: str = 'hvsc84') -> DMCV4Config:
    mem, s = _load(os.path.join(hvsc_root, sid_path))

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
    def _jt_layout(b):
        if not (0 < b and s['load'] <= b and b + 0x8E7 < 0x10000
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
    for b in (s['play'] - 3, s['load']):
        layout = _jt_layout(b)
        if layout:
            base = b
            break
    if base is None:
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
                if s['play'] != base + 3:
                    raise DMCV4Unsupported(
                        'cia_multispeed',
                        f"play=${s['play']:04X} CIA latch unreadable "
                        "(py65 + writelog)")
                cia_period = 0
    # INTERNAL multispeed (vblank wrapper, no speed bit) — independent of CIA.
    play_repeat = (1 if (s.get('speed', 0) & 1)
                   else _detect_play_repeat(mem, s['play'], base, s['load']))
    # PLAY-PHASE wrapper (not an N-JSR repeat): the play vector cycles
    # full-play / effects-only calls — with the CIA speed bit this is TRUE
    # multispeed EFFECTS (e.g. $1331 4x + 'PFFF' = engine ticks at 50Hz,
    # effect chain runs at 200Hz); without it, a slow-tempo cycler. A pure
    # CIA rate wrapper (every call a full play) observes as 'P' = no knob,
    # so the existing cia_multispeed members are untouched. Observed under
    # py65 (C9: measure, don't parse — wrapper shapes vary: SMC operand
    # table, DEC+dual-JMP, INC+AND, stubs hidden in compare-masked regions).
    play_phases = None
    if play_repeat == 1 and s['play'] != base + 3:
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
    # the loop target. Both operands relocate with base.
    loop_target = False
    op = mem[at(_LOOP_SITE)]
    if op == 0x9D and _rd16(mem, at(_LOOP_SITE) + 1) == reloc(0x1726):
        pass                                     # canonical loop-to-0
    elif op == 0x20:                             # JSR hook
        hook_at = _rd16(mem, at(_LOOP_SITE) + 1)
        ok = (bytes(mem[hook_at:hook_at + 4]) == bytes.fromhex('c8b1f89d')
              and _rd16(mem, hook_at + 4) == reloc(0x1726)
              and mem[hook_at + 6] == 0x60)
        if not ok:
            raise DMCV4Unsupported(
                'loop_hook_unknown', bytes(mem[hook_at:hook_at + 14]).hex())
        loop_target = True
    else:
        raise DMCV4Unsupported(
            'loop_site_unknown',
            bytes(mem[at(_LOOP_SITE):at(_LOOP_SITE) + 3]).hex())
    for i in range(_LOOP_SITE, _LOOP_SITE + 3):
        masked[i - 0x1000] = 1
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
            extra['notestart_arm'] = '1'
    # rest/switch/slide-tail dispatch ($1180): canon JMP $1322 (run
    # effects); a sub-build JMP $1591 (wavestep) — the modulators hold one
    # frame at each tie (the family-2 rest_effects='skip' behavior).
    if mem[at(0x1180)] == 0x4C:
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
        track_loop_target=loop_target, cia_period=cia_period,
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
