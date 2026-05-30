"""Extract → USF v2 for the Clever Music Companion engine.

USF encoding (one engine byte per row, except $81 which folds into
the preceding row's duration):

  $00-$7F NORMAL_NOTE  → Pitch(name, octave) + duration N
  $80     REST         → Pitch.rest()        + duration N
  $81     SKIP         → folded — adds 1 to duration of preceding row
  $B0-$BF SET_TEMPO    → Pitch.rest() + duration 1 + tempo=<N>
  $C0-$CF SET_MASTER_VOL → Pitch.rest() + duration 1 + vol=<N>
  $D0-$DF SET_INSTRUMENT → Pitch.rest() + duration 1 + instr_ref (i<N+1>)
  $E0-$EF PATTERN_JUMP → Pitch.rest() + duration 1 + song_pos=<N>

`tempo=N`, `vol=N`, `song_pos=N` are parametric fx flags (same
shape as the existing `porta=N`) — N is musically meaningful (BPM-
adjacent, 0..15 master vol, song-section index).

Per-voice patterns are extracted from start through the LAST byte the
voice's pattern_ptr reaches during one full song cycle, which we
detect empirically by simulating the engine.
"""

from __future__ import annotations

import os
import struct

from src.usf import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, Instrument,
    PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig, MusicSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    write_file, validate,
)
from pipelines.companion.clever_music.extract.engine_model import (
    load_state_from_sid, _load_note, _run_init,
)


_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


def _row_from_byte(b: int) -> NoteRow | None:
    """Encode one Clever-Music pattern byte as a USF NoteRow, or
    return None if the byte should fold into the preceding row's
    duration ($81 SKIP).
    """
    if b < 0x80:
        # NORMAL_NOTE — pitch byte (octave << 4) | semitone
        semitone = b & 0x0F
        octave = (b >> 4) & 0x07
        if semitone >= 12:
            # Engine's freq table has extra slots at semitone 12..15
            # (freq=0 in Fairlight / Gyroscope). Never seen in their
            # actual pattern data; keep as raw fallback.
            return NoteRow(pitch=Pitch.rest(), duration=1,
                           fx_flags=(f'fx:raw_{b:02x}',))
        return NoteRow(
            pitch=Pitch(name=_NOTE_NAMES[semitone], octave=octave),
            duration=1,
        )
    if b == 0x80:
        return NoteRow(pitch=Pitch.rest(), duration=1)
    if b == 0x81:
        # SKIP — caller folds into preceding row's duration.
        return None
    nibble = b & 0x0F
    if 0xB0 <= b <= 0xBF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'tempo={nibble}',))
    if 0xC0 <= b <= 0xCF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'vol={nibble}',))
    if 0xD0 <= b <= 0xDF:
        # SET_INSTRUMENT — encoded by the instr_ref on a rest row.
        return NoteRow(
            pitch=Pitch.rest(), duration=1,
            instr=InstrumentRef(id=nibble + 1),
        )
    if 0xE0 <= b <= 0xEF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'song_pos={nibble}',))
    # Anything else ($82 SET_DURATION et al — engine no-ops in this
    # corpus). Keep raw escape so we don't silently drop bytes.
    return NoteRow(pitch=Pitch.rest(), duration=1,
                   fx_flags=(f'fx:raw_{b:02x}',))


def _rows_from_bytes(pat_bytes: bytes) -> list[NoteRow]:
    """Decode the full pattern byte sequence into NoteRows, folding
    $81 SKIP bytes into the preceding row's duration.
    """
    rows: list[NoteRow] = []
    for b in pat_bytes:
        row = _row_from_byte(b)
        if row is None:
            # $81 SKIP — extend last row's duration.
            if not rows:
                # Defensive: pattern starts with $81 — treat as a 1-tick
                # rest extended to dur=2 by this $81.
                rows.append(NoteRow(pitch=Pitch.rest(), duration=2))
            else:
                rows[-1].duration += 1
            continue
        rows.append(row)
    return rows


def _extract_voice_pattern(state, voice: int) -> bytes:
    """Simulate the engine for one full song cycle and return the bytes
    voice `voice` reads (in pattern_ptr order, deduplicated by ptr).

    Strategy: run the emulator until the global song_pos returns to its
    initial value (after the first time it advances). Track every
    pattern_ptr position each voice's load_note visited. The pattern
    bytes for this voice = memory at those positions.
    """
    # We need a custom run that tracks ptrs. For simplicity, we capture
    # the bytes from the voice's start address through the highest
    # pattern_ptr value reached in one song cycle. The engine's natural
    # $Ex sync wraps it back to start.
    start_ptr = state.pattern_ptr[voice]
    initial_song_pos = state.song_pos
    visited_ptrs = set()
    max_ptr_seen = start_ptr
    advance_count = 0
    max_ticks = 50000  # safety cap

    # Capture ptr positions on every load_note call.
    # We can't easily instrument the existing _load_note without a callback.
    # Instead, take a different tactic: simulate and on each tick, record
    # state.pattern_ptr[voice] for each voice.
    for _ in range(max_ticks):
        # Record current ptr for this voice (before play() advances it)
        from pipelines.companion.clever_music.extract.engine_model import (
            play_one_frame)
        play_one_frame(state)
        visited_ptrs.add(state.pattern_ptr[voice])
        if state.song_pos != initial_song_pos and advance_count == 0:
            advance_count = 1
        if (state.song_pos == initial_song_pos
                and advance_count > 0
                and state.pattern_ptr[voice] in visited_ptrs
                and state.duration_ctr[voice] == 1):
            # Song cycle complete + voice at familiar ptr
            break
        if state.pattern_ptr[voice] > max_ptr_seen:
            max_ptr_seen = state.pattern_ptr[voice]

    # Extract bytes from start_ptr to max_ptr_seen (inclusive)
    length = max_ptr_seen - start_ptr + 1
    return bytes(state.memory[start_ptr:start_ptr + length])


def _instrument_from_block(idx: int, block: bytes) -> Instrument:
    """Encode one 5-byte instrument block as a USF Instrument.

    Block layout: (pw_lo, pw_hi, ctrl, ad, sr).
    """
    pw_lo, pw_hi, ctrl, ad, sr = block
    pw = (pw_hi << 8) | pw_lo
    return Instrument(
        id=idx + 1,
        waveform=[ctrl],
        loop=0,
        pwm=PwmConfig(mode='none', speed=0, init=pw, min_hi=0, max_hi=0),
        adsr=(ad, sr),
        arp=ArpConfig(offsets=[0], period=1),
        vibrato=VibratoConfig(scale=0),
        envelope=EnvelopeConfig(),
    )


def _psid_meta_from_sid(sid_path: str) -> PsidMeta:
    raw = open(sid_path, 'rb').read()
    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')
    flags = int.from_bytes(raw[0x76:0x78], 'big')
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[(flags >> 2) & 0x03]
    sid_model = {0: 6581, 1: 6581, 2: 8580, 3: 6581}[(flags >> 4) & 0x03]
    start_song = int.from_bytes(raw[0x10:0x12], 'big')
    speed = int.from_bytes(raw[0x12:0x16], 'big')
    return PsidMeta(title=title, author=author, released=released,
                    clock=clock, sid=sid_model, start_song=start_song,
                    speed=speed)


def build_usf(sid_path: str) -> UsfFile:
    """Extract a Clever Music SID into an in-memory UsfFile."""
    state = load_state_from_sid(sid_path)

    # Capture init's SID writes (for codegen replay)
    _, init_sid_writes, init_cia = _run_init(sid_path)

    # 16 instruments
    instruments = []
    for i in range(16):
        block = state.inst_table[i * 5: (i + 1) * 5]
        instruments.append(_instrument_from_block(i, block))

    # Per-voice pattern extraction. Use a FRESH state per voice so
    # walks don't interfere with each other.
    voices = []
    voice_pattern_bytes = []
    for v in range(3):
        fresh = load_state_from_sid(sid_path)
        pat_bytes = _extract_voice_pattern(fresh, v)
        voice_pattern_bytes.append(pat_bytes)
        rows = _rows_from_bytes(pat_bytes)
        total_ticks = sum(r.duration for r in rows)
        pat = Pattern(id=1, length=total_ticks, rows=rows)
        voices.append(VoiceBlock(
            id=v + 1,
            orderlist=Orderlist(entries=[1], loop_to=0),
            patterns=[pat],
        ))

    # Subtune params — engine constants + per-voice initial pointer
    # offset (always 0 for Clever Music's natural song layout).
    subtune_params = Params(fields={
        'init_tempo_ctr': state.tempo_ctr,
        'init_song_pos': state.song_pos,
    })
    if init_cia.get(0xDC04) or init_cia.get(0xDC05):
        subtune_params.fields['cia1_timer_a'] = (
            init_cia.get(0xDC04, 0) | (init_cia.get(0xDC05, 0) << 8))

    music = MusicSubtune(
        id=0,
        tempo=state.tempo,
        voices=voices,
        params=subtune_params,
    )

    # Top-level init — voices default to their starting instruments
    # (which are set by the FIRST $Dx in their pattern, so default is
    # irrelevant; we keep the slot for grammar compliance)
    top_init = InitState(voices=[
        InitVoice(id=v + 1, instr=InstrumentRef(id=1)) for v in range(3)
    ])

    # Inline the freq table — engine-neutral data the USF carries.
    from pipelines.companion.clever_music.engine_constants import (
        CLEVER_FREQ_HI, CLEVER_FREQ_LO,
    )
    freq_table = list(CLEVER_FREQ_HI) + list(CLEVER_FREQ_LO)

    return UsfFile(
        engine='clever_music',
        psid=_psid_meta_from_sid(sid_path),
        params=Params(),
        init=top_init,
        instruments=instruments,
        subtunes=[music],
        freq_table=freq_table,
    )


def write_usf(sid_path: str, out_path: str | None = None) -> str:
    if out_path is None:
        base, _ = os.path.splitext(sid_path)
        out_path = base + '.usf'
    usf = build_usf(sid_path)
    validate(usf)
    write_file(usf, out_path)
    try:
        from src.sid_db import record_usf
        record_usf(out_path)
    except Exception:
        pass
    return out_path


if __name__ == '__main__':
    import sys
    sid = sys.argv[1] if len(sys.argv) > 1 else \
        'hvsc84/MUSICIANS/C/Clever_Music/Fairlight.sid'
    p = write_usf(sid)
    print(f'wrote {p}')
