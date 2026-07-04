"""Convert extracted Companion subtune data into a USF v2 UsfFile and
write it to disk.

This is the *extract → USF* direction. The reverse direction (USF → SID)
lives in `pipelines/universal_codegen.py` and is routed through the
top-level `pipelines.build_from_usf.build_from_usf` entry point by USF
content. Once the USF exists, the SID build only needs the USF; the
original binary is no longer consulted.

USF representation choices (no schema-level engine flavoring):

- 5 music subtunes; each subtune carries its own `init { ... }` block
  (3 InitVoice records, one per Companion voice) and `params { ... }`
  block (gate_off_tick, note_load_tick, init_tempo_counter,
  init_pwm_ctr, vol_filter, filter_cutoff_hi).
- 15 instruments (5 subs × 3 voices). Each Companion voice has a
  locked timbre (ctrl, pw_lo, pw_hi, ad, sr) — naturally a USF
  Instrument with no fx, no PWM mode (init pw only), no arp/vibrato.
- Each voice's orderlist is `[1] stop`; pattern 1 holds the full
  pre-$8D byte sequence as note rows. The `stop` terminator stands
  in for the $8D byte the engine reads to gate off + (V3 only) end
  the song.

The Companion engine keeps reading past `$8D`, gathering bytes
adjacent in memory (it doesn't check song_alive). Those bytes are
*not* music and not in the USF — they're a deterministic function
of the codegen's binary layout. Specifically: the codegen lays out
each subtune as `[V1 ord][V2 ord][V3 ord][template]`, mirroring the
original's adjacency. Past V1's `$8D` falls into V2's first bytes;
past V2's falls into V3's; past V3's falls into the per-subtune
init template (encoded directly from the USF `init { ... }` block).
Engine mechanism stays in the engine; the USF stays clean.

Note byte → NoteRow mapping:
  byte 0x00..0x7F (valid semitone)    → Pitch + no flags
  byte 0x80..0xFF with valid semitone → Pitch + fx:early_release
  byte 0x8C ($80 + $0C)               → rest + fx:early_release (rest sentinel)
  byte 0x8D ($80 + $0D)               → encoded by `stop`; not emitted as a row
"""

from __future__ import annotations

import os
import struct

from pipelines.companion.config import CFG
from pipelines.companion.extract import extract_all, SubtuneData, VoiceState
from src.usf import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, Instrument,
    PwmConfig, ArpConfig, VibratoConfig, EnvelopeConfig, MusicSubtune,
    VoiceBlock, Orderlist, Pattern, NoteRow, Pitch, InstrumentRef,
    write_file, validate,
)

_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


def _pitch_from_note_byte(b: int) -> Pitch:
    """Decode Companion's (octave << 4) | semitone encoding.

    Caller must ensure `b & 0x0F < 12` (valid semitone). For sentinel
    bytes ($8C, $8D) or invalid semitones, use `Pitch.rest()`.
    """
    octave = (b >> 4) & 0x07
    semitone = b & 0x0F
    return Pitch(name=_NOTE_NAMES[semitone], octave=octave)


def _row_from_byte(b: int) -> NoteRow:
    """Decode one orderlist byte into a NoteRow.

    The caller must NOT pass $8D — that byte is the orderlist `stop`
    terminator, handled at the orderlist level, not as a row.
    """
    if b == 0x8C:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=('fx:early_release',))
    early_release = bool(b & 0x80)
    semitone = b & 0x0F
    octave = (b >> 4) & 0x07
    if semitone >= 12:
        # Bit-7-clear with invalid semitone (e.g. $0C, $0D, $0E, $0F):
        # the freq-table entry is $0000 so the engine writes V_FREQ=0.
        # Companion's musical content never has these in the song-proper;
        # they only appear in the post-$8D garbage which goes into the
        # `trailing` byte array, not into rows.
        raise ValueError(
            f'note byte ${b:02X} has invalid semitone {semitone} — '
            f'not representable as a NoteRow; should be in trailing bytes')
    flags = ('fx:early_release',) if early_release else ()
    return NoteRow(pitch=Pitch(name=_NOTE_NAMES[semitone], octave=octave),
                   duration=1, fx_flags=flags)


def _instrument_from_voice_state(inst_id: int, vs: VoiceState) -> Instrument:
    """Each Companion voice has a single locked timbre. Map it to a
    USF Instrument with no effects."""
    init_pw = (vs.pw_hi << 8) | vs.pw_lo
    # Waveform = ctrl byte. Companion stores the gate-off version in
    # state and writes (ctrl | 1) for gate-on; the USF carries the
    # gate-off form verbatim and the codegen handles the gate trick.
    return Instrument(
        id=inst_id,
        name=None,
        waveform=[vs.ctrl_noGate],
        loop=0,
        pwm=PwmConfig(mode='none', speed=0, init=init_pw, min_hi=0, max_hi=0),
        adsr=(vs.ad, vs.sr),
        arp=ArpConfig(offsets=[0], period=1),
        vibrato=VibratoConfig(scale=0),
        envelope=EnvelopeConfig(),
    )


def _voice_orderlist_bytes_to_voice_block(
        voice_id: int, ord_bytes: bytes) -> VoiceBlock:
    """Take the bytes BEFORE the $8D terminator as the pattern rows.
    Post-$8D bytes are engine ringoff (not music) and the codegen
    reproduces them deterministically from the binary layout — they
    don't go into the USF.
    """
    end_idx = ord_bytes.index(0x8D)
    rows = [_row_from_byte(b) for b in ord_bytes[:end_idx]]
    pattern = Pattern(id=1, length=len(rows), rows=rows)
    return VoiceBlock(
        id=voice_id,
        orderlist=Orderlist(entries=[1], stop=True),
        patterns=[pattern],
    )


def _params_for_subtune(s: SubtuneData) -> Params:
    return Params(fields={
        'gate_off_tick': s.gate_off_tick,
        'note_load_tick': s.note_load_tick,
        'init_tempo_counter': s.init_tempo_counter,
        'init_pwm_ctr': s.init_pwm_ctr,
        'init_pwm_ctr_2': s.init_pwm_ctr_2,
        'vol_filter': s.vol_filter,
        'filter_cutoff_hi': s.filter_cutoff_hi,
        # Per-voice engine layout — the Companion engine reads past
        # each voice's $8D into the bytes the original binary
        # happened to place adjacently. (count, byte) is enough
        # because the padding is always a uniform fill.
        'v1_pad_count': s.v1_padding.count,
        'v1_pad_byte':  s.v1_padding.byte,
        'v2_pad_count': s.v2_padding.count,
        'v2_pad_byte':  s.v2_padding.byte,
        'v3_pad_count': s.v3_padding.count,
        'v3_pad_byte':  s.v3_padding.byte,
    })


def _init_state_for_subtune(s: SubtuneData,
                            v1_inst: int, v2_inst: int, v3_inst: int) -> InitState:
    """Build a per-subtune InitState; each voice points at the
    subtune's locked-timbre instrument."""
    voices = []
    for vi, (vs, inst_id) in enumerate(
            [(s.v1_state, v1_inst), (s.v2_state, v2_inst), (s.v3_state, v3_inst)],
            start=1):
        voices.append(InitVoice(
            id=vi,
            ctrl=vs.ctrl_noGate,
            dur_field=0,
            pwm_period=0,
            pwm_dir='up',
            instr=InstrumentRef(id=inst_id),
            slide_v=0,
        ))
    return InitState(voices=voices)


def _read_psid_meta(sid_path: str) -> PsidMeta:
    raw = open(sid_path, 'rb').read()
    title    = raw[22:54].rstrip(b'\x00').decode('latin-1', errors='replace')
    author   = raw[54:86].rstrip(b'\x00').decode('latin-1', errors='replace')
    released = raw[86:118].rstrip(b'\x00').decode('latin-1', errors='replace')
    flags = int.from_bytes(raw[118:120], 'big')
    clock = {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[(flags >> 2) & 3]
    sid = {0: 0, 1: 6581, 2: 8580, 3: 0}[(flags >> 4) & 3]
    return PsidMeta(title=title, author=author, released=released,
                    clock=clock, sid=sid,
                    start_song=int.from_bytes(raw[16:18], 'big'),
                    speed=int.from_bytes(raw[18:22], 'big'))


def build_usf() -> UsfFile:
    """Build the in-memory UsfFile for Up_up_and_Away.sid."""
    subs, _freq_hi, _freq_lo = extract_all()

    # 15 instruments (one per voice per subtune), id 1..15.
    instruments = []
    inst_ids_per_sub = []  # per subtune, the 3 instrument ids (V1, V2, V3)
    for i, s in enumerate(subs):
        v1_id = 3 * i + 1
        v2_id = 3 * i + 2
        v3_id = 3 * i + 3
        instruments.append(_instrument_from_voice_state(v1_id, s.v1_state))
        instruments.append(_instrument_from_voice_state(v2_id, s.v2_state))
        instruments.append(_instrument_from_voice_state(v3_id, s.v3_state))
        inst_ids_per_sub.append((v1_id, v2_id, v3_id))

    # Music subtunes.
    music = []
    for i, s in enumerate(subs):
        v1_id, v2_id, v3_id = inst_ids_per_sub[i]
        voices = [
            _voice_orderlist_bytes_to_voice_block(1, s.orderlist_v1),
            _voice_orderlist_bytes_to_voice_block(2, s.orderlist_v2),
            _voice_orderlist_bytes_to_voice_block(3, s.orderlist_v3),
        ]
        music.append(MusicSubtune(
            id=i, tempo=1, voices=voices,
            params=_params_for_subtune(s),
            init=_init_state_for_subtune(s, v1_id, v2_id, v3_id),
        ))

    psid = _read_psid_meta(CFG.sid_path)

    # No top-level mechanism params for Companion — the codegen always
    # emits LOAD=$1000 so the old instr_base/freq_table_base/instr_count
    # placeholders were vestigial. Per-subtune `params` blocks (which
    # still carry per-tune engine state) are a separate concern.
    params = Params(fields={})

    # Top-level init is a placeholder (sub 0's). Per-subtune overrides
    # are what the codegen actually consumes.
    top_init = _init_state_for_subtune(subs[0], *inst_ids_per_sub[0])

    # Inline the freq table — engine-neutral data the USF carries.
    from pipelines.companion.engine_constants import (
        COMPANION_FREQ_HI, COMPANION_FREQ_LO,
    )
    freq_table = list(COMPANION_FREQ_HI) + list(COMPANION_FREQ_LO)

    return UsfFile(psid=psid, params=params, init=top_init,
                   instruments=instruments, subtunes=music,
                   freq_table=freq_table)


def write_usf(out_dir: str) -> str:
    usf = build_usf()
    validate(usf)
    out_path = os.path.join(out_dir, 'Up_up_and_Away.usf')
    write_file(usf, out_path)
    return out_path


if __name__ == '__main__':
    import sys
    out_dir = sys.argv[1] if len(sys.argv) > 1 else 'demo/hubbard'
    p = write_usf(out_dir)
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
