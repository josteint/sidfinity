"""FC-family engine model + extractor (shared core).

Typed model of the FutureComposer / MoN-1987 engine family. The
sequence/pattern byte encodings are FC-family-stable and live here.
Per-SID data table addresses + table sizes come in via `FCConfig`
(see `pipelines/future_composer/config.py`).

Use:
    from pipelines.future_composer.engine_model import extract
    from pipelines.future_composer.hawkeye.config import HAWKEYE
    song = extract(HAWKEYE)

Or run a canary's config as a script:
    python3 pipelines/future_composer/hawkeye/config.py
"""
from __future__ import annotations

import os
import struct
from dataclasses import dataclass, field

from pipelines.future_composer.config import (
    FCConfig, EngineInstance, instance_for_subtune, resolve_address,
)


# Sequence command byte ranges (verified by L_7C0D/L_7C1F/L_7C31 dispatch
# in Hawkeye disassembly; identical across the FC family by design).
SEQ_END = 0xFE
SEQ_WRAP = 0xFF
# Engine walker treats ALL of $80-$FF (minus $FE/$FF) as transpose
# (AND #$1F). The earlier (0x80,0xBF) bound mis-classified $C0-$FD as
# pattern jumps — invisible for music (transpose stays <=$97) but it
# corrupts SFX sequences, which use high-transpose bytes.
SEQ_TRANSPOSE_RANGE = (0x80, 0xFD)   # AND #$1F → toneadd
SEQ_VOICEINC_RANGE  = (0x60, 0x7F)   # AND #$0F → voiceinc
SEQ_REPEATS_RANGE   = (0x40, 0x5F)   # AND #$3F → repeatsto
SEQ_PATTERN_RANGE   = (0x00, 0x3F)   # ASL → index pattern-ptr table


@dataclass
class Instrument:
    """8-byte FC instrument record.

    The 8 raw bytes are preserved; the named fields are the
    interpretation per the research docs (FC V4.1 manual + Cybernoid II
    disassembly). Fx semantics still partly unverified.
    """
    id: int
    raw: bytes                  # 8 bytes
    pulse_hi: int               # +0
    waveform: int               # +1 (ctrl byte: waveform + gate/sync/ring/test)
    ad: int                     # +2 attack/decay
    sr: int                     # +3 sustain/release
    fil_count: int              # +4 filter-table pointer (TBD exact format)
    fx1: int                    # +5 — vibrato-related (TBD)
    fx2: int                    # +6 — arpeggio-related (TBD)
    fx3: int                    # +7 — drum/skydive flags (TBD)
    vib_onset: int = 0          # vibtabwait[id]: vibrato onset delay (frames)


# ---------------------------------------------------------------------------
# Sequence commands (decoded from byte ranges in L_7C0D/L_7C1F/L_7C31/L_7C43)
# ---------------------------------------------------------------------------

@dataclass
class SeqPatternJump:
    """$00-$3F: play pattern N. Triggers a 2*N index into the pattern
    pointer table."""
    pattern_id: int            # 0-63


@dataclass
class SeqRepeats:
    """$40-$5F: set the per-voice pattern-repeat counter (`repeatsto`).
    The pattern then replays N times before sequence advances."""
    count: int                 # 0-31


@dataclass
class SeqVoiceinc:
    """$60-$7F: set per-voice wave-table advance step (`voiceinc`)."""
    inc: int                   # 0-15 (AND #$0F)


@dataclass
class SeqTranspose:
    """$80-$BF: set per-voice transpose offset (`toneadd`)."""
    semitones: int             # 0-31 (AND #$1F)


@dataclass
class SeqEnd:
    """$FE: section end → triggers `songout` (gate all voices off)."""
    pass


@dataclass
class SeqWrap:
    """$FF: wrap → reset tabcount/begcount/nootcount and re-read."""
    pass


SeqCommand = (SeqPatternJump | SeqRepeats | SeqVoiceinc | SeqTranspose
              | SeqEnd | SeqWrap)


def _parse_sequence(raw: bytes,
                    seq_format: str = 'tel') -> list[SeqCommand]:
    """Decode the sequence byte stream into structured commands.

    `seq_format='standard'` — the vanilla player's dispatch ($1873-$18BE)
    differs from Tel: $FE/$FF first, then bit7 → transpose (& $1F), then
    bit6 → REPEATS (& $3F — the WHOLE $40-$7F range; the standard player
    has NO voiceinc command), else $00-$3F pattern jump. Tel's $60-$7F =
    voiceinc reading swallowed e.g. Crocketts_Theme's $60 = 'play the
    next pattern 33 times'.
    """
    out: list[SeqCommand] = []
    for b in raw:
        if b == SEQ_END:
            out.append(SeqEnd())
            break
        if b == SEQ_WRAP:
            out.append(SeqWrap())
            break
        if seq_format == 'standard':
            if b & 0x80:
                out.append(SeqTranspose(b & 0x1F))
            elif b & 0x40:
                out.append(SeqRepeats(b & 0x3F))
            else:
                out.append(SeqPatternJump(b))
            continue
        if SEQ_TRANSPOSE_RANGE[0] <= b <= SEQ_TRANSPOSE_RANGE[1]:
            out.append(SeqTranspose(b & 0x1F))
        elif SEQ_VOICEINC_RANGE[0] <= b <= SEQ_VOICEINC_RANGE[1]:
            out.append(SeqVoiceinc(b & 0x0F))
        elif SEQ_REPEATS_RANGE[0] <= b <= SEQ_REPEATS_RANGE[1]:
            out.append(SeqRepeats(b & 0x3F))
        else:  # $00-$3F
            out.append(SeqPatternJump(b))
    return out


@dataclass
class Sequence:
    """A per-voice sequence stream: bytes consumed left-to-right by
    the engine until $FE (end) or $FF (wrap to start).

    `bytes_raw` is the verbatim source. `commands` is the decoded
    command list. `pattern_ids_used` is the unique pattern ids
    referenced by SeqPatternJump.
    """
    start_addr: int
    bytes_raw: bytes
    commands: list[SeqCommand]
    pattern_ids_used: list[int]


# ---------------------------------------------------------------------------
# Pattern events (decoded from dispatch logic at L_7C64 .. L_7D22)
# ---------------------------------------------------------------------------
#
# Pattern byte ranges (verified by reading the disassembly's dispatch
# chain in order $F0 → $E0 → $C0 → $70 → $80 → fallthrough):
#   $FF        end-of-pattern
#   $F1, p     direct $D417 write with parameter p
#   $F0, n     no-glide marker; n = next note
#   $E0..$EF, d, t : glide command (delay d, target/note t)
#   $C0..$DF   wave-position adjust (& $1F = offset added to voiceinc)
#   $80..$BF   set note-length (& $3F - 1 = frames). Can chain.
#   $70..$7F   instrument change (low nibble = instr id 0-15)
#   $00..$6F   note (pitch index 0-95; $60-$6F is off-table)

@dataclass
class PatNote:
    """Play a note at `pitch` (index into freq table 0-95). $60-$6F is
    off-table (reads engine state region; rare in well-formed patterns)."""
    pitch: int


@dataclass
class PatInstrumentChange:
    """$70-$7F: change current instrument to N (low nibble)."""
    instr_id: int              # 0-15


@dataclass
class PatSetLength:
    """$80-$BF: set the length of the next note(s). The engine may chain
    multiple PatSetLength to extend the length further."""
    length: int                # 0-63 (frames; engine subtracts 1)


@dataclass
class PatWaveAdjust:
    """$C0-$DF: adjust wavetable position by (byte & $1F) + voiceinc."""
    delta: int                 # 0-31


@dataclass
class PatGlide:
    """Portamento, two shapes sharing one event:

    Tel ($E0-$EF, delay, target): slide-to-target; `delay` set, standard
    fields None. The target byte is BOTH the glide target AND the next
    note's pitch (engine re-reads it).

    Standard FC ($Ex, param, note): directional constant-rate slide —
    cmd bit0 → direction, cmd bits1-3 → speed hi, param hi nibble →
    speed lo, param lo nibble → onset threshold (elapsed ticks)."""
    delay: int                 # 0-255 (Tel; 0 for standard)
    direction: str | None = None   # 'up' | 'down' (standard)
    speed: int | None = None       # 16-bit rate per frame (standard)
    onset: int | None = None       # elapsed-tick threshold (standard)


@dataclass
class PatNoGlide:
    """$F0: prefix that disables glide for the immediately-following
    note (the next byte is the note pitch)."""
    pass


@dataclass
class PatFilterSet:
    """$F1, value: direct write to $D417 (filter resonance/routing)."""
    value: int                 # 0-255


@dataclass
class PatEnd:
    """$FF: end of pattern. Triggers sequence-advance + repeat logic."""
    pass


PatEvent = (PatNote | PatInstrumentChange | PatSetLength | PatWaveAdjust
            | PatGlide | PatNoGlide | PatFilterSet | PatEnd)


def _parse_pattern(raw: bytes) -> tuple[list[PatEvent], int]:
    """Decode pattern bytes into structured events. Returns
    (events, consumed_byte_count). Stops at first $FF (inclusive)."""
    events: list[PatEvent] = []
    i = 0
    while i < len(raw):
        b = raw[i]
        if b == 0xFF:
            events.append(PatEnd())
            i += 1
            break
        if b == 0xF1:
            if i + 1 >= len(raw):
                break
            events.append(PatFilterSet(raw[i + 1]))
            i += 2
            continue
        if b == 0xF0:
            events.append(PatNoGlide())
            i += 1
            continue
        if 0xE0 <= b <= 0xEF:
            if i + 2 >= len(raw):
                break
            delay = raw[i + 1]
            target = raw[i + 2]
            events.append(PatGlide(delay))
            events.append(PatNote(target))     # the glide target IS the note
            i += 3
            continue
        if 0xC0 <= b <= 0xDF:
            events.append(PatWaveAdjust(b & 0x1F))
            i += 1
            continue
        if 0x70 <= b <= 0x7F:
            events.append(PatInstrumentChange(b & 0x0F))
            i += 1
            continue
        if 0x80 <= b <= 0xBF:
            events.append(PatSetLength(b & 0x3F))
            i += 1
            continue
        # $00..$6F: note
        events.append(PatNote(b))
        i += 1
    return events, i


def _parse_pattern_standard(raw: bytes) -> tuple[list[PatEvent], int]:
    """Decode STANDARD ("vanilla") FC pattern bytes — parser $18DD-$1957.

    This is a structurally different dispatch from the Tel variant
    (`_parse_pattern`); the byte ranges mean different things:

      $FF        end-of-pattern ($19CC / sub_19ED peek)
      $F0..$FE   tie/no-retrigger prefix: the FOLLOWING byte is a note that
                 plays WITHOUT reloading the instrument ($2180,x=1 skips the
                 note-load at $1986). Low nibble is ignored. → PatNoGlide
                 (which carries the 'noretrig' legato flag in to_usf) + PatNote.
      $E0..$EF   3-byte glide [$Ex][param][note]: param low nibble = dir(bit0)+
                 speed(bits1-3>>1); 3rd byte is the note. → PatGlide + PatNote.
      $C0..$DF   instrument-select, low 5 bits = instrument id (0-31). This is
                 the key divergence from Tel ($Cx = wave-adjust there): the
                 standard player chooses its instrument here. → PatInstrumentChange.
      $80..$BF   note-length, low 6 bits (1-63). Modal prefix. → PatSetLength.
      $00..$7F   note (pitch index). → PatNote.

    The standard format reuses the existing PatEvent vocabulary — only the
    dispatch differs — so to_usf / the composer consume it unchanged.

    DISPATCH STRUCTURE (exact, from the disasm — the ranges above are the
    common case, but the orig is a little state machine, and rips exploit
    the corners):

      FULL ($18DD, every tick start): $Fx (INCLUDING a pattern-initial
        $FF!) = tie → next byte is the note, ANY value; $Ex = glide,
        consume param, go RESTRICTED; $Cx = instr, go AFTER-CX; $8x =
        length, peek, back to FULL; else note.
      AFTER-CX ($193F → $1942): peek $FF = end; $8x = length, peek, back
        to FULL; else NOTE — any byte (an $Ex/$Fx/$Cx here is a pitch!).
      RESTRICTED ($192E → L_1930, after a glide param): $Cx → AFTER-CX;
        $8x → length, peek, FULL; else NOTE — any byte.
      post-note/$8x/$Cx peeks ($19CC / sub_19ED): $FF = end. A $FF can
        therefore only be a tie at the very start of the pattern.

    Ghost-march corollary (Baster_Blaster): a pattern-initial $FF ties to
    whatever byte follows in RAM and the voice marches through it until a
    post-note $FF — the march content is captured by value, off-table
    pitches (>= 96, up to 255) ride the 2-digit-octave USF pitch.
    """
    events: list[PatEvent] = []
    i = 0
    n = len(raw)

    def _note(j: int) -> int:
        events.append(PatNote(raw[j]))
        return j + 1

    def _setlen(j: int) -> int:
        # The player plays (raw & $3F) + 1 ticks ($2127 = raw, DEC/BMI
        # counts raw+1 underflows); USF carries the ACTUAL tick count.
        # Consecutive $8x OVERWRITE ($2127 = raw each time, no tick) —
        # collapse to the last so to_usf's Tel chaining never mis-adds.
        ev = PatSetLength((raw[j] & 0x3F) + 1)
        if events and isinstance(events[-1], PatSetLength):
            events[-1] = ev
        else:
            events.append(ev)
        return j + 1

    def _after_cx(j: int) -> int:
        # $1942 via the $193F peek: $8x-or-NOTE only. Returns next index,
        # or -1 when the peek ended the pattern.
        if j >= n:
            return j
        if raw[j] == 0xFF:
            events.append(PatEnd())
            return -(j + 2)              # signal: ended at j+1
        if (raw[j] & 0xC0) == 0x80:
            j = _setlen(j)
            return j                     # back to FULL
        return _note(j)                  # ANY other byte is the pitch

    while i < n:
        b = raw[i]
        if b == 0xFF and i > 0:
            # post-note/post-command peek position ($19CC / sub_19ED)
            events.append(PatEnd())
            i += 1
            break
        if (b & 0xF0) == 0xF0:           # $F0..$FF tie/no-retrigger
            if i + 1 >= n:
                break
            events.append(PatNoGlide())          # carries the noretrig flag
            events.append(PatNote(raw[i + 1]))   # next byte = note, ANY value
            i += 2
            continue
        if (b & 0xF0) == 0xE0:           # $E0..$EF glide: [$Ex][param]...
            if i + 1 >= n:
                break
            param = raw[i + 1]
            events.append(PatGlide(
                0,
                direction='down' if (b & 0x01) else 'up',
                speed=(((b & 0x0E) >> 1) << 8) | (param & 0xF0),
                onset=param & 0x0F))
            i += 2
            # RESTRICTED (L_1930): $Cx → AFTER-CX; $8x → len + FULL;
            # else the byte IS the note (Excite: [$Ex][param][$8F][note]).
            if i >= n:
                break
            if (raw[i] & 0xE0) == 0xC0:
                events.append(PatInstrumentChange(raw[i] & 0x1F))
                i = _after_cx(i + 1)
            elif (raw[i] & 0xC0) == 0x80:
                i = _setlen(i)
            else:
                i = _note(i)
            if i < 0:
                i = -i - 1
                break
            continue
        if (b & 0xE0) == 0xC0:           # $C0..$DF instrument-select (0-31)
            events.append(PatInstrumentChange(b & 0x1F))
            i = _after_cx(i + 1)
            if i < 0:
                i = -i - 1
                break
            continue
        if (b & 0xC0) == 0x80:           # $80..$BF note-length
            i = _setlen(i)
            continue
        # $00..$7F: note
        i = _note(i)
    return events, i


@dataclass
class Pattern:
    """A pattern stream: bytes consumed left-to-right by the per-voice
    pattern reader until $FF (end)."""
    id: int
    start_addr: int
    bytes_raw: bytes
    events: list[PatEvent]
    notes_count: int


@dataclass
class Subtune:
    """Per-subtune setup: which sequence each voice plays + the
    tempo (speedbyte = frames per sequence step).

    `seqs` / `patterns` carry this subtune's sequences and the patterns
    they reference, resolved in THIS subtune's memory context. They are
    per-subtune because some engines (Hawkeye SFX) reuse the same
    sequence/pattern addresses across subtunes with different content
    (the SFX records reload $8FC5 + pattern slots 54-63 at init), so a
    single SID-global addr/id-keyed dict would collide. Music subtunes
    on a single-engine SID just resolve from the static image.
    """
    id: int
    is_sfx: bool
    speedbyte: int
    seq_v0_addr: int
    seq_v1_addr: int
    seq_v2_addr: int
    seqs: tuple = ()                       # (Sequence, Sequence, Sequence)
    patterns: dict | None = None          # fc_id -> Pattern (this subtune)


@dataclass
class FCSong:
    """The full decoded FC model for one SID."""
    cfg: FCConfig
    load_addr: int
    init_addr: int
    play_addr: int
    psid_songs: int

    freq_table: list[int]
    instruments: list[Instrument]
    pattern_ptr_table: list[int]
    patterns: dict[int, Pattern]
    sequences: list[Sequence]
    subtunes: list[Subtune]
    arp_programs: dict = field(default_factory=dict)  # N -> signed offsets
    pulse_programs: dict = field(default_factory=dict)  # N -> sweep shape
    filter_programs: dict = field(default_factory=dict)  # N -> cutoff env
    drum_programs: dict = field(default_factory=dict)  # N -> wave/tone steps
    attack_len: list = field(default_factory=list)
    attack_wave: list = field(default_factory=list)
    wave_arp: list = field(default_factory=list)
    pulse_arp: list = field(default_factory=list)
    # Vanilla-FC wave-program envelope library: {sel: {'ctrl':[15],'freq':[15]}}
    std_wave_programs: dict = field(default_factory=dict)
    # Off-table freq reads as ML-musical per-instrument records (the v5 form):
    # {inst_id: [(offset, note, lo, hi)]}, idx=(offset+note)&$FF. `offset` is a
    # wave/arp delta (0 = note-load/glide-arrival base read, 1 = vibrato, wave
    # freq-program values, arp3 offsets). The off-table-read representation.
    offtable_freq: dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Binary loading helpers
# ---------------------------------------------------------------------------

def _load_psid(sid_path: str) -> tuple[int, int, int, int, bytes]:
    """Return (load_addr, init_addr, play_addr, songs, code_bytes)."""
    with open(sid_path, 'rb') as f:
        d = f.read()
    assert d[:4] == b'PSID', f'expected PSID magic, got {d[:4]!r}'
    hl = struct.unpack('>H', d[6:8])[0]
    la = struct.unpack('>H', d[8:10])[0]
    init = struct.unpack('>H', d[10:12])[0]
    play = struct.unpack('>H', d[12:14])[0]
    songs = struct.unpack('>H', d[14:16])[0]
    code = d[hl:]
    if la == 0:
        la = struct.unpack('<H', code[:2])[0]
        code = code[2:]
    return la, init, play, songs, code


def _materialize_memory(load_addr: int, code: bytes) -> bytes:
    """Return a 64K memory image with the code mapped at load_addr."""
    mem = bytearray(65536)
    mem[load_addr:load_addr + len(code)] = code
    return bytes(mem)


def _run_init_in_py65(sid_path: str, subtune: int,
                      max_cycles: int = 10_000_000) -> bytes:
    """Load the SID, run its PSID init handler in py65 with A=subtune,
    return the 64K memory image after init returns.

    For multi-engine FC SIDs (Adrenalin and similar) where data tables
    live at runtime addresses that are BELOW the load address — populated
    at init by a per-subtune memcpy. The raw-binary `_materialize_memory`
    image has zeroes at those runtime addresses; running init populates
    them.

    For single-engine SIDs (Hawkeye, Cyb II) init still runs but it's
    a no-op as far as data extraction goes — the runtime addresses
    already hold their final values in the raw binary. Existing
    `extract()` callers don't need this helper.

    Termination: init returns to a fake RTS sentinel; the loop also
    bails after `max_cycles` (default 10M) as a safety net.
    """
    import sys
    sys.path.insert(0, 'tools/py65_lib')
    from py65.devices.mpu6502 import MPU
    from py65.memory import ObservableMemory

    load_addr, init_addr, _play_addr, _n_songs, code = _load_psid(sid_path)
    mem_bytes = _materialize_memory(load_addr, code)

    mpu = MPU()
    mem = ObservableMemory()
    for i, v in enumerate(mem_bytes):
        mem[i] = v
    mpu.memory = mem

    # Push a fake return-target address onto the stack so when init
    # finishes with RTS, PC lands at $0001 (an unmapped sentinel),
    # not somewhere unpredictable. 6502 RTS pulls lo then hi then
    # increments — so push hi=$00, lo=$00, and RTS lands at $0001.
    mpu.stPush(0x00)
    mpu.stPush(0x00)
    mpu.pc = init_addr
    mpu.a = subtune
    mpu.x = 0
    mpu.y = 0

    for _ in range(max_cycles):
        if mpu.pc == 0x0001:
            break
        mpu.step()
    else:
        raise RuntimeError(
            f'_run_init_in_py65: init did not return after {max_cycles} '
            f'cycles for {sid_path} sub {subtune}')

    return bytes(mem[i] for i in range(0x10000))


# ---------------------------------------------------------------------------
# Decoders (parametric over FCConfig)
# ---------------------------------------------------------------------------

def _decode_freq_table(mem: bytes, cfg: FCConfig,
                       engine: EngineInstance | None = None) -> list[int]:
    freq_lo = resolve_address(cfg, engine, 'freq_lo_addr')
    freq_hi = resolve_address(cfg, engine, 'freq_hi_addr')
    return [
        mem[freq_lo + i] | (mem[freq_hi + i] << 8)
        for i in range(cfg.freq_table_entries)
    ]


def _decode_instruments(mem: bytes, cfg: FCConfig,
                        engine: EngineInstance | None = None,
                        count: int | None = None) -> list[Instrument]:
    instr_base = resolve_address(cfg, engine, 'instr_records_addr')
    vib_base = resolve_address(cfg, engine, 'vibtabwait_addr')
    std = getattr(cfg, 'instr_format', 'tel') == 'standard'
    out: list[Instrument] = []
    for i in range(count if count is not None else cfg.instr_count):
        base = instr_base + i * 8
        raw = bytes(mem[base:base + 8])
        if std:
            # Vanilla FC 8-byte record (standard/RE_NOTES.md, from disasm
            # note-load $1986-$19C9 + per-frame $1A11-$1A1D):
            #   +0 PW-hi  +1 param($2179/$212d)  +2 AD  +3 SR  +4 param($216c)
            #   +5 filter/wave selector ($2153)  +6 pulse default ($2154)
            #   +7 effect-enable flags ($2155: $01 filter,$10 wave,$40 fx)
            # Carry the standard effect bytes in the fx slots: fx1=+5 (wave
            # selector low nibble + mode bit4), fx2=+6 (pulse default), fx3=+7
            # (effect-enable flags: $10 wave, $01 filter, $40 fx). The standard
            # voice_loop_layout BYPASSES the Tel effect chain (gwo2 →
            # std_wave_chain), so these drive ONLY the standard effects — the
            # Tel vibrato/arp never run on them. Waveform (raw[1]) is the
            # note-load ctrl; the wave program overrides it per frame.
            out.append(Instrument(
                id=i, raw=raw,
                pulse_hi=raw[0], waveform=raw[1], ad=raw[2], sr=raw[3],
                fil_count=raw[4], fx1=raw[5], fx2=raw[6], fx3=raw[7],
                vib_onset=0,
            ))
        else:
            out.append(Instrument(
                id=i, raw=raw,
                pulse_hi=raw[0], waveform=raw[1], ad=raw[2], sr=raw[3],
                fil_count=raw[4], fx1=raw[5], fx2=raw[6], fx3=raw[7],
                vib_onset=(mem[vib_base + i] if vib_base else 0),
            ))
    return out


def _decode_std_wave_programs(mem: bytes, cfg: FCConfig,
                              instruments: list,
                              engine: EngineInstance | None = None) -> dict:
    """Decode the vanilla-FC wave-program envelope library (standard/RE_NOTES.md).

    The pointer-table base (cfg.std_wave_ptr_addr) holds, per selector s:
      ctrl_ptr = base+s | (base+2+s)<<8     freq_ptr = base+4+s | (base+6+s)<<8
    Each program is two parallel 15-entry tables: ctrl[] (waveform → $D404) and
    freq[] (→ $D400/$D401, absolute +$0D or relative per the instrument's mode
    bit). Selector = instrument raw[5] & $0F; enabled iff raw[7] & $10. Returns
    {sel: {'ctrl': [15], 'freq': [15]}} for the selectors instruments use.
    """
    base = resolve_address(cfg, engine, 'std_wave_ptr_addr')
    if not base:
        return {}
    sels = sorted({i.raw[5] & 0x0F for i in instruments
                   if len(i.raw) >= 8 and (i.raw[7] & 0x10)})
    progs: dict[int, dict] = {}
    for s in sels:
        cptr = mem[base + s] | (mem[base + 2 + s] << 8)
        fptr = mem[base + 4 + s] | (mem[base + 6 + s] << 8)
        # Content-by-reference: read what the player would read — a junk
        # pointer near the top of memory wraps at 64K on the 6502 (grown
        # instrument decodes can reference selectors with garbage ptrs).
        progs[s] = {
            'ctrl': [mem[(cptr + j) & 0xFFFF] for j in range(15)],
            'freq': [mem[(fptr + j) & 0xFFFF] for j in range(15)],
        }
    return progs


def _std_offtable_freq(mem: bytes, cfg: FCConfig,
                       engine: EngineInstance | None,
                       subtunes: list, instruments: list,
                       wave_programs: dict) -> dict:
    """Per-instrument off-table freq records (standard) — the v5 `offtable_freq`
    form (the off-table-read representation). Returns {inst_id: [(offset, note,
    lo, hi)]}, idx=(offset+note)&$FF, lo/hi = the orig's off-table freq bytes.

    Reachable capture of the image bytes after hinote (standard).

    The standard player indexes lonote/hinote with 8-bit indices that can
    pass the 96-entry table; off-table reads must resolve to the orig's
    following image bytes (content-by-reference — what it reads IS what
    plays). Capturing the whole 160-byte window for every member stuffs
    the corpus with junk, so capture only what the tune can REACH, as a
    conservative over-approximation:

      noho candidates  = every pattern note pitch × every seq transpose
                         (cross product — pairing notes to the transposes
                         they actually play under would under-capture on
                         a mismodel; extra candidates only cost bytes)
      delta candidates = 0  (note-load / glide-target lookup)
                         1  (vibrato's semitone-delta +1 read), if any
                            inst can run vibrato (fx1!=0, fx3 bits2/4 clear)
                         wave freq-program values (relative-mode insts:
                            fx3 bit4 + fx1 bit4; entries 0..13 reachable)
                         arp3 offsets (any fx3-bit2 inst: the baked init
                            slots + every $2030-path rewrite candidate —
                            vibrato-skipped insts' fx1 nibbles / $0C,$18)

    The note↔instrument PAIRING matters: a relative-mode program full of
    negative vals ($F4..$FD) only wraps off-table when its inst plays a
    LOW note, so each voice's orderlist is walked (transpose + current
    instrument carried through patterns, and across the $FF wrap — the
    loop-pickup carry — via a second pass) and deltas applied per the
    instrument actually sounding. A naive notes×deltas cross product
    re-captures ~160 bytes for nearly every wave-relative tune.

    Window = hinote indices {(noho+delta)&$FF} ≥ entries, up to the max.
    Empty when nothing reaches off-table. An under-capture cannot pass
    silently: the composer lays the next data section right after the
    window, so an unmodeled off-table read diverges in verify.
    """
    entries = cfg.freq_table_entries
    insts = list(instruments)

    # arp3 offsets are GLOBAL state (slots 1-2 last-runner-wins across
    # voices each frame): any vibrato-skipped inst's rewrite can be live
    # when any fx3-bit2 inst reads the table.
    arp_cands = set(cfg.std_arp3_init)
    for i in insts:
        if len(i.raw) >= 8 and ((i.fx3 & 0x14) or not i.fx1):
            arp_cands.update((i.fx1 >> 4, i.fx1 & 0x0F) if i.fx1
                             else (0x0C, 0x18))

    delta_cache: dict[int, set] = {}

    def _deltas(idx: int) -> set:
        if idx not in delta_cache:
            d = {0}                          # note-load / glide-target lookup
            if 0 <= idx < len(insts) and len(insts[idx].raw) >= 8:
                i = insts[idx]
                if i.fx1 and not (i.fx3 & 0x14):
                    d.add(1)                 # vibrato's semitone-delta +1 read
                if (i.fx3 & 0x10) and (i.fx1 & 0x10):
                    prog = wave_programs.get(i.fx1 & 0x0F)
                    if prog:
                        d.update(v & 0xFF for v in prog['freq'][:14])
                if i.fx3 & 0x04:
                    d.update(a & 0xFF for a in arp_cands)
            delta_cache[idx] = d
        return delta_cache[idx]

    import collections as _collections
    lo_base = resolve_address(cfg, engine, 'freq_lo_addr')
    hi_base = resolve_address(cfg, engine, 'freq_hi_addr')
    recs: dict = _collections.defaultdict(set)   # inst_id -> {(offset,note,lo,hi)}
    for st in subtunes:
        pats = st.patterns or {}
        for seq in (st.seqs or ()):
            transpose, cur = 0, 0            # toneadd + current instrument
            for _pass in range(2):           # pass 2 = the $FF wrap carry
                wrapped = False
                for cmd in seq.commands:
                    if isinstance(cmd, SeqTranspose):
                        transpose = cmd.semitones
                    elif isinstance(cmd, SeqWrap):
                        wrapped = True
                    elif (isinstance(cmd, SeqPatternJump)
                          and cmd.pattern_id in pats):
                        for e in pats[cmd.pattern_id].events:
                            if isinstance(e, PatInstrumentChange):
                                cur = e.instr_id
                            elif isinstance(e, PatNote):
                                noho = (e.pitch + transpose) & 0xFF
                                for d in _deltas(cur):
                                    idx = (noho + d) & 0xFF
                                    if idx >= entries:
                                        recs[cur].add(
                                            (d & 0xFF, noho,
                                             mem[lo_base + idx],
                                             mem[hi_base + idx]))
                if not wrapped:
                    break
    return {k: sorted(v) for k, v in recs.items()}


def _decode_arp_programs(mem: bytes, cfg: FCConfig,
                         engine: EngineInstance | None = None) -> dict:
    """Decode the FC arp library (arplo/arphi) into {N: signed offsets}.

    Each entry N (selected by a pattern $7x command) points to a program
    `[count, off0, off1, ... off_count]`; the engine cycles the count+1
    offsets. We store the offsets as signed semitone deltas; count is
    recovered as len-1 on emit. Entries with a garbage hi byte (< $80)
    are skipped (unused slots), matching the composer's table scan.
    """
    lo = resolve_address(cfg, engine, 'arplo_addr')
    hi = resolve_address(cfg, engine, 'arphi_addr')
    if not (lo and hi):
        return {}
    progs: dict[int, tuple[int, ...]] = {}
    hi_min = getattr(cfg, 'arp_ptr_hi_min', 0x80)
    for n in range(16):                      # engine masks $7x with $0F
        if mem[hi + n] < hi_min:
            continue
        ptr = mem[lo + n] | (mem[hi + n] << 8)
        count = mem[ptr]
        offs = [mem[ptr + 1 + j] for j in range(count + 1)]
        # store signed (0xE9 -> -23): downward arps read naturally
        progs[n] = tuple(o - 256 if o >= 128 else o for o in offs)
    return progs


def _decode_pulse_programs(mem: bytes, cfg: FCConfig,
                           instruments: list,
                           engine: EngineInstance | None = None) -> dict:
    """Decode the FC pulse-sweep library (pulsetabel) into {N: shape}.

    Program N (an instrument's fx2 & $07, 1-based) lives at offset (N-1)*8:
      [0] lo bound (low nibble) + wrap (bit7); [1] hi bound;
      [2,4,6] segment thresholds (bit7 = direction flip); [3,5,7] steps.
    We store only the programs actually referenced by an instrument — unused
    slots are dead data, not musical content.
    """
    base = resolve_address(cfg, engine, 'pulsetabel_addr')
    if not base:
        return {}
    if getattr(cfg, 'pulse_prog_format', 'tel') == 'standard':
        # Vanilla FC: 4-byte programs [thr_a, step1, thr_b, step2] at
        # base + (n-1)*4, n = an instrument's fx2 & 7 (1-based). Decode
        # every program some instrument REFERENCES — the player indexes
        # blindly, so n >= 4 reads past the nominal table into whatever
        # data follows (Prato: prog 7 lands in the pattern-ptr region).
        # Those 4 bytes are still the instrument's effective pulse-schedule
        # parameters — musical content; their provenance in the orig image
        # is irrelevant (capturing them by VALUE keeps the rebuild's own
        # layout free). See standard/RE_NOTES.md (pulse $1E95).
        ns = sorted({(i.fx2 & 0x07) for i in instruments} - {0})
        # fx2&7 == 0 with fx2 != 0: the player computes (0-1)*4 = $FC and
        # reads table+$FC (8-bit index) — whatever 4 bytes sit there form
        # the instrument's EFFECTIVE program (Obelisk: [11 12 13 10] →
        # step1=$12). Captured by value as prog "0".
        if any(i.fx2 and not (i.fx2 & 0x07) for i in instruments):
            ns = [0] + ns
        progs: dict[int, dict] = {}
        for n in ns:
            off = base + ((n - 1) * 4 if n else 0xFC)
            b = [mem[off + j] for j in range(4)]
            # Carry in the EXISTING Tel pulse-program shape so the USF
            # writer/reader round-trip unchanged. The emitter reinterprets
            # seg[0]/seg[1] as the standard 2-threshold step schedule when
            # cfg.pulse_prog_format=='standard' (bounds $01/$0F hardcoded).
            progs[n] = {'lo': 0x01, 'hi': 0x0F, 'wrap': False,
                        'segs': [(b[0], b[1], False),     # (thr_a, step1)
                                 (b[2], b[3], False),     # (thr_b, step2)
                                 (0, 0, False)]}
        return progs
    kmax = max((i.fx2 & 0x07) for i in instruments) if instruments else 0
    progs: dict[int, dict] = {}
    for n in range(1, kmax + 1):
        off = base + (n - 1) * 8
        b = [mem[off + j] for j in range(8)]
        segs = [(b[2] & 0x7F, b[3], bool(b[2] & 0x80)),
                (b[4] & 0x7F, b[5], bool(b[4] & 0x80)),
                (b[6] & 0x7F, b[7], bool(b[6] & 0x80))]
        progs[n] = {'lo': b[0] & 0x0F, 'hi': b[1],
                    'wrap': bool(b[0] & 0x80), 'segs': segs}
    return progs


def _decode_filter_programs(mem: bytes, cfg: FCConfig,
                            instruments: list,
                            engine: EngineInstance | None = None) -> dict:
    """Decode the FC filter library (filterbytes ptr table) into {N: env}.

    filterbytes[N] is a 2-byte pointer to a 10-byte program fb[0..9]:
      fb[0] init cutoff; fb[1..3] segment adds; fb[4] final cutoff;
      fb[5] $D418 routing; fb[6..8] segment thresholds; fb[9] end threshold.
    Stored as {init, d418, final, end, segs:[(threshold, add)*3]}. Only the
    programs referenced by an instrument (fil_count & filter_prog_mask) are
    kept — the hi-byte scan alone yields false positives past the real data.
    """
    base = resolve_address(cfg, engine, 'filterbytes_addr')
    if not base:
        return {}
    if getattr(cfg, 'filter_prog_format', 'tel') == 'standard':
        # Vanilla FC: ONE 12-byte program at base = [6 cutoffs][6
        # thresholds]. Mapped into the shared envelope shape: onset =
        # thr[0] (band-0 entry), init = cutoff[0], segs = (thr[k],
        # add[k]) for the incremental bands k=1..4, end = thr[5],
        # final = cutoff[5]. No d418 byte. Decoded only when some
        # instrument enables the filter (+7 bit0) — otherwise the 12
        # bytes are dead data.
        if not any((i.fx3 & 0x01) for i in instruments):
            return {}
        cut = [mem[base + j] for j in range(6)]
        thr = [mem[base + 6 + j] for j in range(6)]
        return {0: {'init': cut[0], 'onset': thr[0], 'd418': 0,
                    'final': cut[5], 'end': thr[5],
                    'segs': [(thr[k], cut[k]) for k in range(1, 5)]}}
    # Program count = where the pointer table ends = (first pointer - base)/2.
    # Extract ALL of them (not just instrument-referenced): SFX subtunes
    # reference programs no music instrument does, and matching orig's table
    # size keeps the rebuilt layout aligned.
    first_ptr = mem[base] | (mem[base + 1] << 8)
    count = (first_ptr - base) // 2
    if not (1 <= count <= 8):
        return {}
    progs: dict[int, dict] = {}
    for n in range(count):
        ptr = mem[base + n * 2] | (mem[base + n * 2 + 1] << 8)
        fb = [mem[ptr + j] for j in range(10)]
        segs = [(fb[6], fb[1]), (fb[7], fb[2]), (fb[8], fb[3])]
        progs[n] = {'init': fb[0], 'd418': fb[5], 'final': fb[4],
                    'end': fb[9], 'segs': segs}
    return progs


def _decode_drum_programs(mem: bytes, cfg: FCConfig,
                          engine: EngineInstance | None = None) -> dict:
    """Decode the FC drum library (drumtabel) into {N: {wave, tone}}.

    drumtabel is 4 bytes/drum: a `dwa` pointer (waveform program
    [length, w1..w_{L-1}]) and a `dto` pointer (tone program [t0..t_{L-2}]).
    Each frame plays (dwa[k+1], dto[k]); we store the wave/tone steps as two
    parallel lists (length L-1; the leading length byte = len+1 is derived).
    Program count = where the pointer table ends = (first dwa ptr - base)/4;
    extract ALL drums (SFX may reference drums no music instrument does).
    """
    base = resolve_address(cfg, engine, 'drumtabel_addr')
    if not base:
        return {}
    first_dwa = mem[base] | (mem[base + 1] << 8)
    count = (first_dwa - base) // 4
    if not (1 <= count <= 16):
        return {}
    progs: dict[int, dict] = {}
    for d in range(count):
        dwa = mem[base + d * 4] | (mem[base + d * 4 + 1] << 8)
        dto = mem[base + d * 4 + 2] | (mem[base + d * 4 + 3] << 8)
        L = mem[dwa]
        wave = [mem[dwa + 1 + j] for j in range(L - 1)]
        tone = [mem[dto + j] for j in range(L - 1)]
        progs[d] = {'wave': wave, 'tone': tone}
    return progs


def _decode_flat_aux(mem: bytes, cfg: FCConfig,
                     engine: EngineInstance | None = None) -> dict:
    """Decode the small flat per-index aux tables (attack_len/attack_wave =
    startlen/starttabel, wave_arp/pulse_arp = wavearp/pulsearp).

    startlen/starttabel are parallel per-wavecount tables; their length is the
    gap between them. wavearp/pulsearp are cyclic value tables read with a
    fixed mask (counter2 & 3 -> 4 entries, & 7 -> 8 entries).
    """
    out = {'attack_len': [], 'attack_wave': [], 'wave_arp': [], 'pulse_arp': []}
    sl = resolve_address(cfg, engine, 'startlen_addr')
    st = resolve_address(cfg, engine, 'starttabel_addr')
    if sl and st and st > sl:
        n = st - sl
        out['attack_len'] = [mem[sl + i] for i in range(n)]
        out['attack_wave'] = [mem[st + i] for i in range(n)]
    wa = resolve_address(cfg, engine, 'wavearp_addr')
    if wa:
        out['wave_arp'] = [mem[wa + i] for i in range(4)]
    pa = resolve_address(cfg, engine, 'pulsearp_addr')
    if pa:
        out['pulse_arp'] = [mem[pa + i] for i in range(8)]
    return out


def _decode_pattern_ptr_table(mem: bytes, cfg: FCConfig,
                               load_addr: int, code_len: int,
                               engine: EngineInstance | None = None
                               ) -> list[int]:
    """Walk pattern pointer table; stop at first pointer outside the
    loaded code region."""
    pat_ptr_base = resolve_address(cfg, engine, 'pattern_ptr_addr')
    out: list[int] = []
    lo_hi_end = load_addr + code_len
    for i in range(cfg.max_patterns):
        lo = mem[pat_ptr_base + i * 2]
        hi = mem[pat_ptr_base + i * 2 + 1]
        addr = lo | (hi << 8)
        if addr < load_addr or addr >= lo_hi_end:
            break
        out.append(addr)
    return out


def _decode_sequence(mem: bytes, start_addr: int,
                     max_bytes: int = 256,
                     seq_format: str = 'tel') -> Sequence:
    raw_buf = bytearray()
    pat_ids: list[int] = []
    seen_pat = set()
    for k in range(max_bytes):
        b = mem[start_addr + k]
        raw_buf.append(b)
        if b == SEQ_END or b == SEQ_WRAP:
            break
        if SEQ_PATTERN_RANGE[0] <= b <= SEQ_PATTERN_RANGE[1]:
            if b not in seen_pat:
                seen_pat.add(b)
                pat_ids.append(b)
    raw = bytes(raw_buf)
    commands = _parse_sequence(raw, seq_format=seq_format)
    if raw and raw[-1] not in (SEQ_END, SEQ_WRAP):
        # Terminator-less stream: the engine's per-voice seq cursor is
        # 8-bit, so after byte 255 it wraps to 0 — semantically a loop
        # to start. DEMOS rips park idle voices on zero-filled seq
        # regions with no $FE/$FF (Baster_Blaster V1).
        commands.append(SeqWrap())
    return Sequence(start_addr=start_addr, bytes_raw=raw,
                    commands=commands, pattern_ids_used=pat_ids)


def _decode_pattern(mem: bytes, pat_id: int, start_addr: int,
                    max_bytes: int = 512,
                    pattern_format: str = 'tel') -> Pattern:
    if pattern_format == 'standard':
        # Positional capture: a pattern-INITIAL $FF is a tie, not an end
        # (the $18DD dispatch has no $FF exclusion) — the voice marches
        # through following RAM until a post-note $FF. Read the full
        # 8-bit-cursor window and let the parser decide the consumed
        # length. No end within 256 bytes = pattern-cursor wrap — capped
        # here; a member exercising the wrap will flag in verify.
        window = bytes(mem[start_addr + k] for k in range(256))
        events, consumed = _parse_pattern_standard(window)
        raw = window[:consumed]
    else:
        raw_buf = bytearray()
        for k in range(max_bytes):
            b = mem[start_addr + k]
            raw_buf.append(b)
            if b == 0xFF:
                break
        raw = bytes(raw_buf)
        events, _consumed = _parse_pattern(raw)
    notes = sum(1 for e in events if isinstance(e, PatNote))
    return Pattern(id=pat_id, start_addr=start_addr, bytes_raw=raw,
                   events=events, notes_count=notes)


def _decode_subtune(mem: bytes, cfg: FCConfig, sub_idx: int,
                    engine: EngineInstance | None = None) -> Subtune:
    """Reconstruct per-subtune setup. Dispatches on `cfg.subtune_layout`.

    `flat_seq_table` (Cybernoid II): subtune N's 6-byte record (lo*3 then
      hi*3) sits at `seq_table_addr + N * 6`. Speedbyte from
      `per_subtune_speed_addr + N`. No music/sfx distinction.

    `smc_template_with_sfx` (Hawkeye): X = sub_idx, sub_7B5A reads
      template lo from `per_subtune_smc_addr,X` and copies 6 bytes from
      `template_base_hi<<8 | lo` + 0..5. SFX subtunes (N >=
      music_subtune_count) take a record from page `sfx_page_base +
      sfx_idx * sfx_page_stride` instead; $918F forces X =
      music_subtune_count for the SFX path so speedbyte/mode come from
      that fixed index.
    """
    seq_table = resolve_address(cfg, engine, 'seq_table_addr')
    per_sub_speed = resolve_address(cfg, engine, 'per_subtune_speed_addr')
    if cfg.subtune_layout == 'flat_seq_table':
        record_base = seq_table + sub_idx * 6
        seq_lo = mem[record_base + 0:record_base + 3]
        seq_hi = mem[record_base + 3:record_base + 6]
        speedbyte = mem[per_sub_speed + sub_idx]
        is_sfx = False
    elif cfg.subtune_layout == 'runtime_slot':
        # Post-init memory already holds active subtune's pointers in
        # the fixed runtime slot. No per-subtune indexing — just read
        # the slot. Caller must have run init for the subtune via
        # `_run_init_in_py65` (i.e., multi-engine FCSong path).
        slot = cfg.runtime_seq_ptrs_addr
        seq_lo = mem[slot + 0:slot + 3]
        seq_hi = mem[slot + 3:slot + 6]
        speedbyte = mem[cfg.runtime_speed_addr]
        is_sfx = False
    elif cfg.subtune_layout == 'smc_template_with_sfx':
        # smc_template_with_sfx uses several FCConfig-only fields
        # (per_subtune_smc_addr, template_base_hi, per_subtune_mode_addr,
        # sfx_page_base, sfx_page_stride, music_subtune_count) which
        # don't have EngineInstance overrides — this layout shape is
        # single-engine-only today (Hawkeye). If a multi-engine SID
        # ever needs it, add the corresponding fields to EngineInstance.
        if sub_idx < cfg.music_subtune_count:
            template_lo = mem[cfg.per_subtune_smc_addr + sub_idx]
            template_addr = (cfg.template_base_hi << 8) | template_lo
            seq_lo = mem[template_addr + 0:template_addr + 3]
            seq_hi = mem[template_addr + 3:template_addr + 6]
            speedbyte = mem[per_sub_speed + sub_idx]
            mode = mem[cfg.per_subtune_mode_addr + sub_idx]
        else:
            sfx_idx = sub_idx - cfg.music_subtune_count
            record_base = ((cfg.sfx_page_base
                            + sfx_idx * cfg.sfx_page_stride) << 8)
            seq_lo = mem[record_base + 0:record_base + 3]
            seq_hi = mem[record_base + 3:record_base + 6]
            # $918F forces X = music_subtune_count for SFX path
            speedbyte = mem[per_sub_speed + cfg.music_subtune_count]
            mode = mem[cfg.per_subtune_mode_addr + cfg.music_subtune_count]
        is_sfx = (mode == 0x00)
    else:
        raise ValueError(f'unknown subtune_layout: {cfg.subtune_layout!r}')

    v0_addr = seq_lo[0] | (seq_hi[0] << 8)
    v1_addr = seq_lo[1] | (seq_hi[1] << 8)
    v2_addr = seq_lo[2] | (seq_hi[2] << 8)
    return Subtune(
        id=sub_idx, is_sfx=is_sfx, speedbyte=speedbyte,
        seq_v0_addr=v0_addr, seq_v1_addr=v1_addr, seq_v2_addr=v2_addr,
    )


# ---------------------------------------------------------------------------
# Top-level extract
# ---------------------------------------------------------------------------

def extract(cfg: FCConfig, root: str | None = None) -> FCSong:
    """Decode an FC-family SID per its `FCConfig`. `root` defaults to
    the sidfinity repo root (auto-detected from this file's location).

    Single-engine SIDs (cfg.engines is None): reads from the raw-binary
    memory image. This is the Hawkeye/Cybernoid II path — fast, no
    py65 needed. Per-decoder `engine=None` falls back to FCConfig's
    top-level address fields via `resolve_address`.

    Multi-engine SIDs (cfg.engines is set): runs the PSID init in py65
    once per subtune (each subtune may load different packed-source
    data into its runtime layout), and decodes per-subtune content
    using the EngineInstance overrides. Shared content (freq_table,
    instruments, pattern_ptr_table) is read from sub 0's post-init
    memory using sub 0's EngineInstance. This is the Adrenalin path.
    """
    if root is None:
        root = os.path.dirname(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))))
    sid_path = os.path.join(root, cfg.sid_path)

    load_addr, init_addr, play_addr, n_songs, code = _load_psid(sid_path)

    # --- shared (engine-A / sub 0 / top-level) data ---
    if cfg.engines is None:
        mem_global = _materialize_memory(load_addr, code)
        engine_for_shared = None
    else:
        # Run init for sub 0 to populate sub 0's engine layout in memory.
        mem_global = _run_init_in_py65(sid_path, subtune=0)
        engine_for_shared = instance_for_subtune(cfg, 0)

    freq_table = _decode_freq_table(mem_global, cfg, engine_for_shared)
    instruments = _decode_instruments(mem_global, cfg, engine_for_shared)
    pattern_ptr_table = _decode_pattern_ptr_table(
        mem_global, cfg, load_addr, len(code), engine_for_shared)

    # --- per-subtune data ---
    subtunes: list[Subtune] = []
    sequences: list[Sequence] = []
    seq_seen: set[int] = set()
    patterns: dict[int, Pattern] = {}

    for sub_idx in range(n_songs):
        # Pick this subtune's memory context. SFX subtunes (smc layout)
        # need POST-INIT memory: their sequences/patterns live in runtime
        # areas ($8FC5, pattern slots 54-63) that the static image leaves
        # empty until init copies the per-SFX record in. Music subtunes on
        # a single-engine SID resolve from the static image.
        sfx_needs_init = (
            cfg.engines is None
            and cfg.subtune_layout == 'smc_template_with_sfx'
            and sub_idx >= cfg.music_subtune_count)
        # runtime_slot on a single-engine SID: a custom init installs the
        # active subtune's 6-byte seq record into the fixed runtime slot
        # (standard-family wrapper inits, e.g. Intense_Intro) — the static
        # image's slot is stale, so read post-init memory per subtune.
        slot_needs_init = (
            cfg.engines is None and cfg.subtune_layout == 'runtime_slot')
        if cfg.engines is None:
            mem = _run_init_in_py65(sid_path, subtune=sub_idx) \
                if (sfx_needs_init or slot_needs_init) else mem_global
            engine = None
        else:
            mem = _run_init_in_py65(sid_path, subtune=sub_idx)
            engine = instance_for_subtune(cfg, sub_idx)

        st = _decode_subtune(mem, cfg, sub_idx, engine)

        # Resolve this subtune's 3 voice sequences + the patterns they
        # reference, IN this subtune's memory context (so SFX pattern slots
        # 54-63 read the post-init record, not the empty static image).
        pat_ptr_base = resolve_address(cfg, engine, 'pattern_ptr_addr')
        sub_seqs: list[Sequence] = []
        sub_pat_ids: set[int] = set()
        for addr in (st.seq_v0_addr, st.seq_v1_addr, st.seq_v2_addr):
            seq = _decode_sequence(
                mem, addr,
                seq_format=getattr(cfg, 'pattern_format', 'tel'))
            sub_seqs.append(seq)
            sub_pat_ids.update(seq.pattern_ids_used)
        sub_patterns: dict[int, Pattern] = {}
        for pid in sorted(sub_pat_ids):
            paddr = (mem[pat_ptr_base + pid * 2]
                     | (mem[pat_ptr_base + pid * 2 + 1] << 8))
            sub_patterns[pid] = _decode_pattern(
                mem, pid, paddr,
                pattern_format=getattr(cfg, 'pattern_format', 'tel'))
        st.seqs = tuple(sub_seqs)
        st.patterns = sub_patterns
        subtunes.append(st)

        # Legacy SID-global views (print_song / pattern_stream_verify).
        # First-seen wins; SFX collisions are expected and harmless here
        # because to_usf reads the per-subtune seqs/patterns, not these.
        for seq in sub_seqs:
            if seq.start_addr not in seq_seen:
                seq_seen.add(seq.start_addr)
                sequences.append(seq)
        for pid, pat in sub_patterns.items():
            patterns.setdefault(pid, pat)

    # Patterns may select instrument ids beyond cfg.instr_count (the $C0-$DF
    # command carries 5 bits = ids 0-31; the player indexes the record table
    # blindly). Grow the decoded instrument list to cover every id a pattern
    # references — the records are real per-tune content wherever they sit.
    max_ref = max((e.instr_id
                   for st in subtunes for p in (st.patterns or {}).values()
                   for e in p.events if isinstance(e, PatInstrumentChange)),
                  default=-1)
    if max_ref >= len(instruments):
        instruments = _decode_instruments(
            mem_global, cfg, engine_for_shared, count=max_ref + 1)

    std_wave_programs = _decode_std_wave_programs(
        mem_global, cfg, instruments, engine_for_shared)
    return FCSong(
        cfg=cfg, load_addr=load_addr, init_addr=init_addr,
        play_addr=play_addr, psid_songs=n_songs,
        freq_table=freq_table, instruments=instruments,
        pattern_ptr_table=pattern_ptr_table,
        patterns=patterns, sequences=sequences, subtunes=subtunes,
        arp_programs=_decode_arp_programs(mem_global, cfg, engine_for_shared),
        pulse_programs=_decode_pulse_programs(
            mem_global, cfg, instruments, engine_for_shared),
        filter_programs=_decode_filter_programs(
            mem_global, cfg, instruments, engine_for_shared),
        drum_programs=_decode_drum_programs(
            mem_global, cfg, engine_for_shared),
        std_wave_programs=std_wave_programs,
        # Standard: off-table 8-bit freq lookups (idx = note + wave/arp delta)
        # that pass the 96-entry table read the orig's following image bytes.
        # Captured as per-instrument `offtable_freq` records (the ML-musical v5
        # form). See _std_offtable_freq.
        offtable_freq=(
            _std_offtable_freq(mem_global, cfg, engine_for_shared,
                               subtunes, instruments, std_wave_programs)
            if getattr(cfg, 'pattern_format', 'tel') == 'standard' else {}),
        **_decode_flat_aux(mem_global, cfg, engine_for_shared),
    )


# ---------------------------------------------------------------------------
# Pretty-printer (shared CLI dump for any canary)
# ---------------------------------------------------------------------------

def print_song(song: FCSong) -> None:
    cfg = song.cfg
    print(f'{cfg.name}: load=${song.load_addr:04X} '
          f'init=${song.init_addr:04X} play=${song.play_addr:04X}')
    print(f'PSID songs: {song.psid_songs}')

    print(f'\nFreq table: {len(song.freq_table)} entries, first 5 = '
          + ' '.join(f'${v:04X}' for v in song.freq_table[:5]))
    print(f'  range: ${min(song.freq_table):04X} '
          f'.. ${max(song.freq_table):04X}')

    print(f'\nInstruments: {len(song.instruments)}')
    for inst in song.instruments:
        if inst.raw == b'\x00' * 8:
            print(f'  inst {inst.id}: <all zero>')
        else:
            print(f'  inst {inst.id}: pulse=${inst.pulse_hi:02X} '
                  f'ctrl=${inst.waveform:02X} AD=${inst.ad:02X} '
                  f'SR=${inst.sr:02X} fil=${inst.fil_count:02X} '
                  f'fx1=${inst.fx1:02X} fx2=${inst.fx2:02X} '
                  f'fx3=${inst.fx3:02X}')

    print(f'\nPattern pointer table: {len(song.pattern_ptr_table)} '
          f'valid entries')
    notes_total = sum(p.notes_count for p in song.patterns.values())
    print(f'\nReferenced patterns: {len(song.patterns)} '
          f'({notes_total} notes total)')

    print(f'\nSubtunes: {song.psid_songs}')
    print(f'{"sub":>3} {"kind":>5} {"speed":>5} {"V0_seq":>7} '
          f'{"V1_seq":>7} {"V2_seq":>7} pat_count')
    for st in song.subtunes:
        kind = 'sfx' if st.is_sfx else 'music'
        pat_count = sum(1 for s in song.sequences
                        if s.start_addr in (st.seq_v0_addr,
                                            st.seq_v1_addr,
                                            st.seq_v2_addr)
                        for _p in s.pattern_ids_used)
        print(f'{st.id:>3} {kind:>5} ${st.speedbyte:02X}    '
              f'${st.seq_v0_addr:04X}  ${st.seq_v1_addr:04X}  '
              f'${st.seq_v2_addr:04X}  {pat_count}')

    print(f'\nDistinct sequences: {len(song.sequences)}')
    for s in song.sequences[:6]:
        cmd_summary: dict[str, int] = {}
        for c in s.commands:
            cmd_summary[type(c).__name__] = cmd_summary.get(
                type(c).__name__, 0) + 1
        print(f'  ${s.start_addr:04X}: {len(s.bytes_raw)} bytes, '
              f'{len(s.commands)} commands, '
              f'patterns={s.pattern_ids_used[:8]}, '
              f'cmd types: '
              + ', '.join(f'{k}={v}' for k, v in cmd_summary.items()))
