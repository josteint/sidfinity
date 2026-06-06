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
from dataclasses import dataclass

from pipelines.future_composer.config import (
    FCConfig, EngineInstance, instance_for_subtune, resolve_address,
)


# Sequence command byte ranges (verified by L_7C0D/L_7C1F/L_7C31 dispatch
# in Hawkeye disassembly; identical across the FC family by design).
SEQ_END = 0xFE
SEQ_WRAP = 0xFF
SEQ_TRANSPOSE_RANGE = (0x80, 0xBF)   # AND #$1F → toneadd
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


def _parse_sequence(raw: bytes) -> list[SeqCommand]:
    """Decode the sequence byte stream into structured commands."""
    out: list[SeqCommand] = []
    for b in raw:
        if b == SEQ_END:
            out.append(SeqEnd())
            break
        if b == SEQ_WRAP:
            out.append(SeqWrap())
            break
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
    """$E0-$EF, delay, target: 3-byte glide. The target byte is BOTH
    the glide target AND the next note's pitch (engine re-reads it)."""
    delay: int                 # 0-255


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
    tempo (speedbyte = frames per sequence step)."""
    id: int
    is_sfx: bool
    speedbyte: int
    seq_v0_addr: int
    seq_v1_addr: int
    seq_v2_addr: int


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
                        engine: EngineInstance | None = None
                        ) -> list[Instrument]:
    instr_base = resolve_address(cfg, engine, 'instr_records_addr')
    out: list[Instrument] = []
    for i in range(cfg.instr_count):
        base = instr_base + i * 8
        raw = bytes(mem[base:base + 8])
        out.append(Instrument(
            id=i, raw=raw,
            pulse_hi=raw[0], waveform=raw[1], ad=raw[2], sr=raw[3],
            fil_count=raw[4], fx1=raw[5], fx2=raw[6], fx3=raw[7],
        ))
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
                     max_bytes: int = 256) -> Sequence:
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
    commands = _parse_sequence(raw)
    return Sequence(start_addr=start_addr, bytes_raw=raw,
                    commands=commands, pattern_ids_used=pat_ids)


def _decode_pattern(mem: bytes, pat_id: int, start_addr: int,
                    max_bytes: int = 512) -> Pattern:
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

    `flat_seqtabel` (Cybernoid II): subtune N's 6-byte record (lo*3 then
      hi*3) sits at `seqtabel_addr + N * 6`. Speedbyte from
      `per_subtune_speed_addr + N`. No music/sfx distinction.

    `smc_template_with_sfx` (Hawkeye): X = sub_idx, sub_7B5A reads
      template lo from `per_subtune_smc_addr,X` and copies 6 bytes from
      `template_base_hi<<8 | lo` + 0..5. SFX subtunes (N >=
      music_subtune_count) take a record from page `sfx_page_base +
      sfx_idx * sfx_page_stride` instead; $918F forces X =
      music_subtune_count for the SFX path so speedbyte/mode come from
      that fixed index.
    """
    seqtabel = resolve_address(cfg, engine, 'seqtabel_addr')
    per_sub_speed = resolve_address(cfg, engine, 'per_subtune_speed_addr')
    if cfg.subtune_layout == 'flat_seqtabel':
        record_base = seqtabel + sub_idx * 6
        seq_lo = mem[record_base + 0:record_base + 3]
        seq_hi = mem[record_base + 3:record_base + 6]
        speedbyte = mem[per_sub_speed + sub_idx]
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
    pat_ids_total: set[int] = set()
    patterns: dict[int, Pattern] = {}

    for sub_idx in range(n_songs):
        if cfg.engines is None:
            # Single-engine: reuse mem_global (raw binary). engine=None
            # → resolve_address falls back to top-level FCConfig fields.
            mem = mem_global
            engine = None
        else:
            mem = _run_init_in_py65(sid_path, subtune=sub_idx)
            engine = instance_for_subtune(cfg, sub_idx)

        st = _decode_subtune(mem, cfg, sub_idx, engine)
        subtunes.append(st)
        for addr in (st.seq_v0_addr, st.seq_v1_addr, st.seq_v2_addr):
            if addr in seq_seen:
                continue
            seq_seen.add(addr)
            seq = _decode_sequence(mem, addr)
            sequences.append(seq)
            pat_ids_total.update(seq.pattern_ids_used)

    for pat_id in sorted(pat_ids_total):
        if pat_id >= len(pattern_ptr_table):
            continue
        addr = pattern_ptr_table[pat_id]
        patterns[pat_id] = _decode_pattern(mem_global, pat_id, addr)

    return FCSong(
        cfg=cfg, load_addr=load_addr, init_addr=init_addr,
        play_addr=play_addr, psid_songs=n_songs,
        freq_table=freq_table, instruments=instruments,
        pattern_ptr_table=pattern_ptr_table,
        patterns=patterns, sequences=sequences, subtunes=subtunes,
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
