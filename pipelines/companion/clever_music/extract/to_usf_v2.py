"""Extract → USF v2 for the Clever Music Companion engine.

Each voice's pattern is a sequence of engine command bytes. We encode
ONE engine byte per USF NoteRow:

  $00-$7F NORMAL_NOTE  → Pitch(name, octave) + duration 1
  $80     REST         → Pitch.rest() + duration 1
  $81     SKIP         → Pitch.rest() + duration 1 + fx:hold
  $82     SET_DURATION → Pitch.rest() + duration 1 + fx:set_dur
  $B0-$BF SET_TEMPO    → Pitch.rest() + duration 1 + fx:tempo_<N>
  $C0-$CF SET_MASTER_VOL → Pitch.rest() + duration 1 + fx:vol_<N>
  $D0-$DF SET_INSTRUMENT → Pitch.rest() + duration 1 + i:i<N+1>
  $E0-$EF PATTERN_JUMP → Pitch.rest() + duration 1 + fx:jump_<N>

The engine's `duration` field is the *number of pattern bytes the row
represents* (always 1 for this engine — there's no multi-byte $82 N
encoding in Fairlight or Gyroscope, but reserving the field allows
$82 N to be encoded as `--- N fx:set_dur` later if needed).

Per-voice patterns are extracted from start through the LAST byte the
voice's pattern_ptr reaches during one full song cycle, which we
detect empirically by simulating the engine.
"""

from __future__ import annotations

import os
import struct

from src.usf2 import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, Instrument,
    PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig, MusicSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    write_file, validate,
)
from pipelines.companion.clever_music.extract.engine_model import (
    load_state_from_sid, _load_note, _run_init,
)


_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


def _row_from_byte(b: int) -> NoteRow:
    """Encode one Clever-Music pattern byte as a USF NoteRow."""
    if b < 0x80:
        # NORMAL_NOTE — pitch byte (octave << 4) | semitone
        semitone = b & 0x0F
        octave = (b >> 4) & 0x07
        # Engine's freq table is indexed 0..127. The 12-tone musical
        # range covers semitone 0..11; semitones 12..15 are extra slots
        # the engine treats as valid notes but with custom freq values
        # set by the per-tune freq table. Map them to NoteRow with
        # synthetic pitches using # spelling (we'll never see them in
        # well-formed Clever Music tunes).
        if semitone >= 12:
            # Unusual; encode with fx flag carrying the raw byte
            return NoteRow(pitch=Pitch.rest(), duration=1,
                           fx_flags=(f'fx:raw_{b:02x}',))
        return NoteRow(
            pitch=Pitch(name=_NOTE_NAMES[semitone], octave=octave),
            duration=1,
        )
    if b == 0x80:
        return NoteRow(pitch=Pitch.rest(), duration=1)
    if b == 0x81:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=('fx:hold',))
    if b == 0x82:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=('fx:set_dur',))
    nibble = b & 0x0F
    if 0xB0 <= b <= 0xBF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'fx:tempo_{nibble}',))
    if 0xC0 <= b <= 0xCF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'fx:vol_{nibble}',))
    if 0xD0 <= b <= 0xDF:
        # SET_INSTRUMENT — use instr_ref (1-indexed in USF)
        return NoteRow(
            pitch=Pitch.rest(), duration=1,
            instr=InstrumentRef(id=nibble + 1),
            fx_flags=('fx:set_inst',),
        )
    if 0xE0 <= b <= 0xEF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'fx:jump_{nibble}',))
    # Anything else — engine no-ops. Encode raw.
    return NoteRow(pitch=Pitch.rest(), duration=1,
                   fx_flags=(f'fx:raw_{b:02x}',))


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
        rows = [_row_from_byte(b) for b in pat_bytes]
        pat = Pattern(id=1, length=len(rows), rows=rows)
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

    return UsfFile(
        version=2,
        engine='clever_music',
        psid=_psid_meta_from_sid(sid_path),
        params=Params(),
        init=top_init,
        instruments=instruments,
        subtunes=[music],
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
