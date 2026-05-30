"""Extract → USF v2 for the Bowden-canonical Companion variant.

Reads a Vic Berry SID, lifts the per-voice orderlists + timbres +
tempo + init positions, and writes a `.usf` alongside the original.

USF representation:
  - 1 music subtune (PSID songs=1 in this cluster)
  - 3 instruments (one per voice) — locked timbre: waveform/ctrl, PW,
    AD, SR. PW never modulates so pwm.mode='none' with `init` carrying
    the fixed PW.
  - Per-voice patterns of K rows (pitches and rests), where K is the
    orderlist's length up to (excluding) the engine's $FF terminator.
  - `orderlist: 1 loop@0` per voice — the engine's flat orderlist is
    a single looping pattern; the $FF byte is the loop marker, not a
    musical row.
  - V2/V3 initial phase offset carried in `subtune.params`
    (`init_pos_v2`, `init_pos_v3`). V1 always starts at 0 (zeroed by
    engine init).
"""

from __future__ import annotations

import os

from src.usf import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, Instrument,
    PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig, MusicSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    write_file, validate,
)
from pipelines.companion.bowden_canonical.engine_constants import (
    note_byte_to_pitch,
)
from pipelines.companion.bowden_canonical.extract.engine_model import (
    load_state_from_sid,
)


def _row_from_note_byte(b: int) -> NoteRow:
    if b == 0x80:
        return NoteRow(pitch=Pitch.rest(), duration=1)
    if b & 0x80:
        # bit-7 set, not $80, not $FF (FF is the orderlist terminator,
        # filtered out before this is called). The engine treats these
        # as skip — falls through to a bare RTS at $C108. Musically:
        # the prior note continues without retrigger. Encoded as
        # rest + fx:hold.
        return NoteRow(pitch=Pitch.rest(), duration=1, fx_flags=('fx:hold',))
    name, octave = note_byte_to_pitch(b)
    return NoteRow(pitch=Pitch(name=name, octave=octave), duration=1)


def _pattern_from_orderlist(pattern_id: int, ol: bytes) -> Pattern:
    """Build a USF Pattern from one engine orderlist (excluding $FF)."""
    body = ol[:-1] if ol and ol[-1] == 0xFF else ol
    rows = [_row_from_note_byte(b) for b in body]
    return Pattern(id=pattern_id, length=len(rows), rows=rows)


def _instrument_from_timbre(instr_id: int, tb: bytes) -> Instrument:
    """5-byte timbre (pw_lo, pw_hi, ctrl, ad, sr) → USF Instrument.

    The engine's per-voice timbre maps to a 'frozen' Instrument:
      - waveform = [ctrl]  (engine writes ctrl, then ctrl|1 for gate)
      - pwm = mode=none  init=(pw_hi<<8|pw_lo)
      - adsr = (ad, sr)
      - arp/vib/envelope = no modulation
    """
    pw = (tb[1] << 8) | tb[0]
    return Instrument(
        id=instr_id,
        waveform=[tb[2]],
        loop=0,
        pwm=PwmConfig(mode='none', speed=0, init=pw, min_hi=0, max_hi=0),
        adsr=(tb[3], tb[4]),
        arp=ArpConfig(offsets=[0], period=1),
        vibrato=VibratoConfig(scale=0),
        envelope=EnvelopeConfig(),
    )


def _psid_meta_from_sid(sid_path: str) -> PsidMeta:
    """Read the PSID header strings + clock + sid model."""
    raw = open(sid_path, 'rb').read()
    title = raw[0x16:0x36].rstrip(b'\x00').decode('latin-1')
    author = raw[0x36:0x56].rstrip(b'\x00').decode('latin-1')
    released = raw[0x56:0x76].rstrip(b'\x00').decode('latin-1')
    flags = int.from_bytes(raw[0x76:0x78], 'big')
    clock_bits = (flags >> 2) & 0x03
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[clock_bits]
    sid_bits = (flags >> 4) & 0x03
    sid = {0: 6581, 1: 6581, 2: 8580, 3: 6581}[sid_bits]
    start_song = int.from_bytes(raw[0x10:0x12], 'big')
    speed = int.from_bytes(raw[0x12:0x16], 'big')
    return PsidMeta(
        title=title,
        author=author,
        released=released,
        clock=clock,
        sid=sid,
        start_song=start_song,
        speed=speed,
    )


def _n_subtunes(sid_path: str) -> int:
    """Read the PSID header's songs count."""
    with open(sid_path, 'rb') as f:
        raw = f.read(0x10)
    import struct as _struct
    return _struct.unpack('>H', raw[0x0E:0x10])[0]


def build_usf(sid_path: str) -> UsfFile:
    """Extract a Bowden-canonical SID into an in-memory UsfFile.

    Iterates over all subtunes declared in the PSID header. Each
    subtune's per-tune state (timbres, tempo, orderlists, init_pos)
    is captured by re-running init with A=subtune_index. Per-subtune
    instruments are numbered (sub_i * 3) + voice (so 3 instruments per
    subtune; sub 0 = i1..i3, sub 1 = i4..i6, sub 2 = i7..i9, etc.).
    """
    n_sub = _n_subtunes(sid_path)
    states = [load_state_from_sid(sid_path, i) for i in range(n_sub)]

    instruments = []
    music_subtunes = []
    for s_idx, state in enumerate(states):
        # Per-subtune timbres → 3 instruments per subtune
        base_id = s_idx * 3 + 1
        for v in range(3):
            instruments.append(_instrument_from_timbre(
                base_id + v, state.timbre[v]))

        voices = []
        for v in range(3):
            pat = _pattern_from_orderlist(1, state.orderlists[v])
            voices.append(VoiceBlock(
                id=v + 1,
                orderlist=Orderlist(entries=[1], loop_to=0),
                patterns=[pat],
            ))

        sub_init = InitState(voices=[
            InitVoice(id=v + 1, instr=InstrumentRef(id=base_id + v))
            for v in range(3)
        ])

        sub_fields = {
            'init_pos_v1': state.v_pos[0],
            'init_pos_v2': state.v_pos[1],
            'init_pos_v3': state.v_pos[2],
            'init_tempo_ctr': state.tempo_ctr,
        }
        if state.cia1_timer_a:
            # Engine programs CIA1 timer A to set play() dispatch rate.
            # Default (when 0) is libsidplayfp's PSID standard (~50Hz PAL).
            # Surfchamp programs $40C7 = ~60Hz.
            sub_fields['cia1_timer_a'] = state.cia1_timer_a
        subtune_params = Params(fields=sub_fields)

        music_subtunes.append(MusicSubtune(
            id=s_idx,
            tempo=state.tempo,
            voices=voices,
            init=sub_init,
            params=subtune_params,
        ))

    # Top-level init defaults to subtune 0's instruments
    top_init = InitState(voices=[
        InitVoice(id=v + 1, instr=InstrumentRef(id=v + 1))
        for v in range(3)
    ])

    return UsfFile(
        engine='bowden_canonical',
        psid=_psid_meta_from_sid(sid_path),
        params=Params(),
        init=top_init,
        instruments=instruments,
        subtunes=music_subtunes,
    )


def write_usf(sid_path: str, out_path: str | None = None) -> str:
    """Extract a Bowden-canonical SID and write `.usf` next to it."""
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
        'hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.sid'
    p = write_usf(sid)
    print(f'wrote {p}')
