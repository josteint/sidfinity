"""FCSong → USF v0 converter.

Takes the decoded `FCSong` (from `engine_model.extract(cfg)`) and
produces a `UsfFile` per the schema designed in
`pipelines/future_composer/docs/usf_schema_v0.md`.

Design decisions for v0:

1. **Sequence baking.** `SeqTranspose` and `SeqRepeats` are baked in
   at extract time. A `SeqTranspose(N)` shifts the pitch of every
   subsequent `SeqPatternJump` until the next `SeqTranspose`; each
   unique (FC_pattern_id, transpose) combination becomes a distinct
   USF pattern. `SeqRepeats(N)` followed by a pattern jump emits the
   jumped-to pattern `N+1` times in the orderlist.

2. **Pattern events** become note rows with these attributes:
   - `PatNote(pitch)` → `Pitch` (named note + octave). Pitches that
     would extend past octave 9 after transpose are clamped.
   - `PatSetLength(N)` → `NoteRow.duration`. Chained: a second
     length-byte ($80-$FF) extends; tracked as (first - 1) + (second & $7F).
   - `PatInstrumentChange(id)` → `i:{id+1}` on the next note row.
   - `PatGlide(delay)` + `PatNote(target)` → `glide=N` on that row.
   - `PatNoGlide` → drop pending glide.
   - `PatWaveAdjust(delta)` → `wave_adjust=N` on the next note.
   - `PatFilterSet(v)` → `filter=$NN` on the next note.
   - `PatEnd` → end of pattern.

3. **Sequence terminators.** `SeqEnd` → orderlist `stop=True`.
   `SeqWrap` → orderlist `loop@0`.

4. **`SeqVoiceinc(N)` — known v0 limitation.** Voiceinc affects
   wave-table position per voice and is musically meaningful, but it
   isn't yet representable as a per-pattern attribute. v0 silently
   drops it and stamps the value into the pattern's id-key so
   different voiceinc states still produce distinct USF patterns
   (the orderlist will at least sequence them correctly even though
   the voiceinc value itself isn't recoverable). The composer will
   need this to rebuild — a v1 follow-up.

5. **Instruments.** `pulse_hi` + `waveform` go into the USF
   `waveform` field as a 2-byte tuple. `ad`/`sr` go into `adsr`.
   The four `fc_*` bytes (`fil_count`, `fx1/2/3`) go into the v0
   `fc_*` instrument fields — opaque, pending decomposition (see
   schema doc §7).

6. **Freq table.** Flattened to lo/hi-interleaved bytes (192 entries
   for a full 96-entry table). FC tunes with truncated tables
   (Cybernoid II's 87) zero-pad to 192.

7. **PSID metadata** read directly from the SID file.
"""
from __future__ import annotations

import struct
from pathlib import Path

from src.usf import (
    UsfFile, PsidMeta, Params, InitState,
    Instrument, MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow,
    Pitch, InstrumentRef, VibratoConfig, PulseProgConfig, FilterProgConfig,
)
from pipelines.future_composer.config import FCConfig
from pipelines.future_composer.engine_model import (
    FCSong, Instrument as FCInstrument, Pattern as FCPattern, Sequence,
    Subtune as FCSubtune,
    SeqPatternJump, SeqRepeats, SeqVoiceinc, SeqTranspose,
    SeqEnd, SeqWrap,
    PatNote, PatInstrumentChange, PatSetLength, PatWaveAdjust,
    PatGlide, PatNoGlide, PatFilterSet, PatEnd,
)


# ---------------------------------------------------------------------------
# Pitch encoding (FC pitch byte → musical name + octave)
# ---------------------------------------------------------------------------

_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
_MAX_OCTAVE = 9          # grammar accepts single-digit octave


def _pitch_from_byte(p: int) -> Pitch:
    """FC pitch byte → `Pitch`. Pitches 0..95 index the 96-entry musical
    freq table (8 octaves × 12 notes). Pitches above clamp to G-9."""
    if p < 0:
        p = 0
    octave = p // 12
    if octave > _MAX_OCTAVE:
        octave = _MAX_OCTAVE
        idx = 11           # B
    else:
        idx = p % 12
    return Pitch(name=_NOTE_NAMES[idx], octave=octave)


# ---------------------------------------------------------------------------
# PSID header read
# ---------------------------------------------------------------------------

def _read_psid_meta(sid_path: str) -> PsidMeta:
    with open(sid_path, 'rb') as f:
        d = f.read()
    assert d[:4] == b'PSID', f'expected PSID, got {d[:4]!r}'
    start_song = struct.unpack('>H', d[16:18])[0]
    title    = d[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author   = d[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = d[0x56:0x76].rstrip(b'\x00').decode('latin-1')
    flags = struct.unpack('>H', d[0x76:0x78])[0] if len(d) > 0x77 else 0
    clock_bits = (flags >> 2) & 0x3
    sid_bits   = (flags >> 4) & 0x3
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[clock_bits]
    sid_model = {0: 0, 1: 6581, 2: 8580, 3: 6581}[sid_bits]
    speed = struct.unpack('>I', d[0x12:0x16])[0]
    return PsidMeta(title=title, author=author, released=released,
                    clock=clock, sid=sid_model or 6581,
                    start_song=start_song or 1, speed=speed)


# ---------------------------------------------------------------------------
# Instruments
# ---------------------------------------------------------------------------

def fx_bytes_from_inst(usf_inst: Instrument) -> tuple[int, int, int, int]:
    """Inverse of `_decompose_fx_bytes` — re-encode an Instrument's
    named v1 fields back into the four FC bytes (fil_count, fx1, fx2, fx3).

    Used by the composers (binary-patch + asm-data) to write the engine's
    8-byte instrument record. Round-trip invariant:
    fx_bytes_from_inst(_inst_to_usf(fc_inst)) == (fc_inst.fil_count,
    fc_inst.fx1, fc_inst.fx2, fc_inst.fx3).
    """
    v = usf_inst.vibrato
    fx1 = (v.amplitude & 0x0F) | ((v.speed & 0x07) << 4)
    if v.direction == 'down':
        fx1 |= 0x80
    pp = usf_inst.pulse_prog
    fp = usf_inst.filter_prog
    fx2 = (pp.program & 0x07) | ((pp.increment & 0x0F) << 4)
    if fp.strange:
        fx2 |= 0x08
    fil_count = (fp.program & 0x0F) | (fp.aux_bits & 0x70)
    if fp.double_voice:
        fil_count |= 0x80
    bit_for = {v: k for k, v in _FX3_BIT_TO_NAME.items()}
    fx3 = 0
    for name in usf_inst.effects:
        fx3 |= bit_for[name]
    return fil_count, fx1, fx2, fx3


# --- FC v1 fx-byte bit decomposition ---
# Maps the four raw FC instrument bytes (fil_count, fx1, fx2, fx3) into
# named musical fields. See pipelines/future_composer/docs/usf_schema_v1.md
# for the verified bit table.

_FX3_BIT_TO_NAME = {
    0x01: 'filter_program',
    0x02: 'pulse_run',
    0x04: 'tone_arp',
    0x08: 'pulse_arp',
    0x10: 'drum',
    0x20: 'tonesweep_up',
    0x40: 'wave_arp',
    0x80: 'noise_tick',
}


def _decompose_fx_bytes(fil_count: int, fx1: int, fx2: int,
                         fx3: int) -> dict:
    """Decompose FC's four opaque instrument bytes into named fields.
    Returns a dict matching the USF Instrument fields:
      vibrato (VibratoConfig with amplitude/speed/direction set)
      pulse_prog (PulseProgConfig)
      filter_prog (FilterProgConfig)
      effects (frozenset[str])
    """
    # fx1 → vibrato (amplitude/speed/direction)
    vibrato = VibratoConfig(
        amplitude=fx1 & 0x0F,
        speed=(fx1 & 0x70) >> 4,
        direction='down' if (fx1 & 0x80) else 'up',
    )
    # fx2 → pulse_prog (program / increment) + filter_prog.strange (bit 3)
    pulse_prog = PulseProgConfig(
        program=fx2 & 0x07,
        increment=(fx2 & 0xF0) >> 4,
    )
    # fil_count → filter_prog.program (lo nibble), double_voice (bit 3),
    # aux_bits (remaining high-nibble bits whose musical meaning isn't
    # fully RE'd)
    filter_prog = FilterProgConfig(
        program=fil_count & 0x0F,
        strange=bool(fx2 & 0x08),
        double_voice=bool(fil_count & 0x80),
        aux_bits=fil_count & 0x70,   # bits 4-6 of fil_count, TBD musical meaning
        freq_hi_rise=bool(fil_count & 0x04),
    )
    # fx3 → effects flag set
    effects = frozenset(
        name for bit, name in _FX3_BIT_TO_NAME.items() if fx3 & bit
    )
    return dict(vibrato=vibrato, pulse_prog=pulse_prog,
                filter_prog=filter_prog, effects=effects)


def _inst_to_usf(inst: FCInstrument) -> Instrument:
    """FC 8-byte instrument record → USF Instrument (v1 schema).

    waveform = [pulse_hi, ctrl_byte]; adsr = (ad, sr). The four FC
    effect bytes (fil_count, fx1, fx2, fx3) are decomposed into named
    fields per usf_schema_v1.md.
    """
    fields = _decompose_fx_bytes(inst.fil_count, inst.fx1, inst.fx2,
                                  inst.fx3)
    return Instrument(
        id=inst.id + 1,           # USF uses 1-based instrument ids
        waveform=[inst.pulse_hi, inst.waveform],
        adsr=(inst.ad, inst.sr),
        **fields,
    )


# ---------------------------------------------------------------------------
# Patterns
# ---------------------------------------------------------------------------

def _build_pattern_rows(fc_pat: FCPattern) -> tuple[list[NoteRow], int]:
    """Walk FC pattern events; emit note rows.

    The pattern body stores the *pure motif* — neither transpose nor
    voiceinc is folded in. Both are sequence-level modifiers carried on
    the orderlist (`Orderlist.transposes` / `Orderlist.voiceincs`):
    transpose offsets note pitch, voiceinc ("sound transpose") offsets
    the wave/inst index `(pattern_byte & $1F) + voiceinc` at the engine's
    $C0-$DF handler. Keeping both out of the pattern means one pattern is
    reused unchanged at every (transpose, voiceinc) it appears with, so
    the pattern pool stays at the base motif count (<=64).

    Returns (rows, total_length_in_frames).
    """
    rows: list[NoteRow] = []
    pending_glide: int | None = None
    pending_wave_adjust: int | None = None
    pending_filter: int | None = None
    cur_length: int = 1            # frames per note (set by PatSetLength)
    cur_instr: InstrumentRef | None = None
    length_seen_first = False      # for chained PatSetLength tracking

    for evt in fc_pat.events:
        if isinstance(evt, PatSetLength):
            if not length_seen_first:
                cur_length = max(1, evt.length - 1)
                length_seen_first = True
            else:
                # Chained second PatSetLength extends length by (b & $7F)
                cur_length += evt.length
        elif isinstance(evt, PatInstrumentChange):
            cur_instr = InstrumentRef(id=evt.instr_id + 1)
        elif isinstance(evt, PatGlide):
            pending_glide = evt.delay
        elif isinstance(evt, PatNoGlide):
            pending_glide = None
        elif isinstance(evt, PatWaveAdjust):
            pending_wave_adjust = evt.delta
        elif isinstance(evt, PatFilterSet):
            pending_filter = evt.value
        elif isinstance(evt, PatNote):
            length_seen_first = False    # next length byte starts fresh
            pitch_val = evt.pitch & 0xFF
            pitch = _pitch_from_byte(pitch_val)
            flags: list[str] = []
            if pending_glide is not None:
                flags.append(f'glide={pending_glide}')
                pending_glide = None
            if pending_wave_adjust is not None:
                flags.append(f'wave_adjust={pending_wave_adjust}')
                pending_wave_adjust = None
            if pending_filter is not None:
                flags.append(f'filter=${pending_filter:02X}')
                pending_filter = None
            rows.append(NoteRow(
                pitch=pitch, duration=cur_length,
                instr=cur_instr, fx_flags=tuple(flags),
            ))
            cur_instr = None         # only attach on the row after a change
        elif isinstance(evt, PatEnd):
            break

    total_length = sum(r.duration for r in rows)
    return rows, max(total_length, 1)


# ---------------------------------------------------------------------------
# Voices
# ---------------------------------------------------------------------------

def _voice_to_usf(voice_id: int, seq_addr: int,
                  song: FCSong) -> VoiceBlock:
    """Walk one voice's sequence stream → orderlist + USF patterns.

    Each unique (fc_pattern_id, transpose, voiceinc) tuple becomes a
    distinct USF pattern, keyed sequentially as 0, 1, 2 ...
    """
    seq = next((s for s in song.sequences if s.start_addr == seq_addr), None)
    if seq is None:
        # No matching sequence: empty voice with stop terminator.
        return VoiceBlock(
            id=voice_id,
            orderlist=Orderlist(stop=True),
            patterns=[],
        )

    orderlist_entries: list[int] = []
    # Patterns are pure motifs — dedup by fc_id ALONE. Transpose and
    # voiceinc ride the orderlist; repeats stay run-length-encoded.
    pattern_key_to_id: dict[int, int] = {}    # fc_id -> usf_id
    pattern_specs: dict[int, int] = {}         # usf_id -> fc_id

    orderlist_transposes: list[int] = []
    orderlist_voiceincs: list[int] = []
    orderlist_repeats: list[int] = []
    transpose = 0
    repeats = 0
    voiceinc = 0
    loop_to: int | None = None
    stop = False

    for cmd in seq.commands:
        if isinstance(cmd, SeqTranspose):
            transpose = cmd.semitones
        elif isinstance(cmd, SeqRepeats):
            repeats = cmd.count
        elif isinstance(cmd, SeqVoiceinc):
            voiceinc = cmd.inc
        elif isinstance(cmd, SeqPatternJump):
            key = cmd.pattern_id
            if key not in pattern_key_to_id:
                new_id = len(pattern_key_to_id)
                pattern_key_to_id[key] = new_id
                pattern_specs[new_id] = key
            usf_pat_id = pattern_key_to_id[key]
            orderlist_entries.append(usf_pat_id)
            orderlist_transposes.append(transpose)
            orderlist_voiceincs.append(voiceinc)
            orderlist_repeats.append(repeats + 1)   # FC count = extra plays
            repeats = 0
        elif isinstance(cmd, SeqEnd):
            stop = True
            break
        elif isinstance(cmd, SeqWrap):
            loop_to = 0
            break

    usf_patterns: list[Pattern] = []
    for usf_id in sorted(pattern_specs):
        fc_id = pattern_specs[usf_id]
        if fc_id not in song.patterns:
            usf_patterns.append(Pattern(id=usf_id, length=1, rows=[]))
            continue
        rows, length = _build_pattern_rows(song.patterns[fc_id])
        usf_patterns.append(Pattern(id=usf_id, length=length, rows=rows))

    # Omit each modifier list when it carries no information.
    if not any(orderlist_transposes):
        orderlist_transposes = []
    if not any(orderlist_voiceincs):
        orderlist_voiceincs = []
    if all(r == 1 for r in orderlist_repeats):
        orderlist_repeats = []
    orderlist = Orderlist(entries=orderlist_entries,
                          loop_to=loop_to, stop=stop,
                          transposes=orderlist_transposes,
                          voiceincs=orderlist_voiceincs,
                          repeats=orderlist_repeats)
    return VoiceBlock(id=voice_id, orderlist=orderlist,
                      patterns=usf_patterns)


# ---------------------------------------------------------------------------
# Subtunes
# ---------------------------------------------------------------------------

def _subtune_to_usf(sub: FCSubtune, song: FCSong) -> MusicSubtune:
    voices = [
        _voice_to_usf(1, sub.seq_v0_addr, song),
        _voice_to_usf(2, sub.seq_v1_addr, song),
        _voice_to_usf(3, sub.seq_v2_addr, song),
    ]
    return MusicSubtune(
        id=sub.id + 1,                  # USF subtunes are 1-based
        tempo=sub.speedbyte + 1,        # frames per step
        voices=voices,
        is_sfx=sub.is_sfx,
    )


# ---------------------------------------------------------------------------
# Freq table
# ---------------------------------------------------------------------------

def _freq_table_bytes(song: FCSong) -> list[int]:
    """Flatten 96 16-bit freq entries into 192 lo,hi-interleaved bytes.
    Tunes with truncated tables (Cybernoid II's 87) zero-pad to 96."""
    out: list[int] = []
    for i in range(96):
        v = song.freq_table[i] if i < len(song.freq_table) else 0
        out.append(v & 0xFF)
        out.append((v >> 8) & 0xFF)
    return out


# ---------------------------------------------------------------------------
# Top-level converter
# ---------------------------------------------------------------------------

def fcsong_to_usf(song: FCSong, root: str | None = None) -> UsfFile:
    """Convert decoded `FCSong` to `UsfFile` per the v0 schema."""
    if root is None:
        root = str(Path(__file__).resolve().parents[2])
    sid_path = str(Path(root) / song.cfg.sid_path)
    psid = _read_psid_meta(sid_path)

    instruments = [_inst_to_usf(i) for i in song.instruments
                   if any(i.raw)]
    subtunes = [_subtune_to_usf(s, song) for s in song.subtunes]

    return UsfFile(
        psid=psid,
        params=Params(fields={}),
        init=InitState(),
        freq_table=_freq_table_bytes(song),
        instruments=instruments,
        subtunes=subtunes,
    )


def write_canary_usf(cfg: FCConfig, out_path: str | None = None,
                     root: str | None = None) -> str:
    """Run extract + convert + write USF. Returns the written path."""
    from pipelines.future_composer.engine_model import extract
    from src.usf import write
    song = extract(cfg, root=root)
    usf = fcsong_to_usf(song, root=root)
    if out_path is None:
        # Default: alongside the .sid file with .usf extension
        if root is None:
            root = str(Path(__file__).resolve().parents[2])
        out_path = str(Path(root) / cfg.sid_path).removesuffix('.sid') + '.usf'
    with open(out_path, 'w') as f:
        f.write(write(usf))
    return out_path
