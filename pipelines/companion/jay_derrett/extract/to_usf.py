"""Extract → USF for Type A jay_derrett SIDs.

Consumes the JSON dumps in `pipelines/companion/jay_derrett/_extracted/`
(produced by `dump_type_a.py`) and emits a USF file per SID. Output
lands at `hvsc84/MUSICIANS/D/Derrett_Jay/<NAME>.usf`.

Row vocabulary (per voice byte stream):

  $00..$7F   → NoteRow(Pitch(name, octave), duration=1)
              (engine freq-table padding region — semitone 12..15 →
               `fx:raw_NN` rest row)
  $80        → NoteRow(rest, duration=1)
  $81        → folded into preceding row's duration (+1)
  $82 N      → NoteRow(rest, duration=1+N, fx_flags=('set_dur=$NN',))
              (the $82 byte takes 1 frame to process + N idle frames)
  $Bx        → NoteRow(rest, duration=1, fx_flags=('tempo=N',))
  $Cx        → NoteRow(rest, duration=1, fx_flags=('vol=N',))
  $Dx        → NoteRow(rest, duration=1, instr=InstrumentRef(id=N+1))
              (engine INCs the value — the +1 quirk handled here)
  $Ex        → NoteRow(rest, duration=1, fx_flags=('section_end=N',))
  other      → NoteRow(rest, duration=1, fx_flags=('fx:raw_NN',))

Each voice gets one `Pattern` with all decoded rows, an orderlist
that loops the pattern (`orderlist: 1 loop@0`). The composer is free
to invent any per-voice loop scheme — only the SID register-write
stream needs to match.

Top-level USF carries:
  - PSID metadata
  - empty params (per-tune mechanism is engine-private)
  - init.voice (placeholder instr=i1 — first $Dx in stream sets actual)
  - freq_table (engine's 256-byte tables inlined)
  - N instruments (decoded via `instrument.py`)
  - One music subtune (id=0)
"""

from __future__ import annotations

import json
import os

from src.usf import (
    UsfFile, PsidMeta, Params, InitState, InitVoice, InstrumentRef,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
    write_file, validate,
)
from pipelines.companion.jay_derrett.extract.instrument import (
    decode_instrument,
)


_NOTE_NAMES = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')


def _row_from_byte(b: int, follow: int) -> tuple[NoteRow | None, int]:
    """Decode one stream byte → (NoteRow | None, bytes_consumed).

    Return (None, 1) for `$81` (SKIP — caller folds into preceding
    row's duration). Otherwise (NoteRow, 1) for most bytes; (NoteRow, 2)
    for `$82 N` which consumes its operand.
    """
    if b < 0x80:
        # Note byte — high nibble = octave, low nibble = semitone.
        octave = (b >> 4) & 0x07
        semitone = b & 0x0F
        if semitone >= 12:
            # Engine's per-octave freq-table padding region (notes
            # 12..15 give freq=0 → silent). Encode as rest with raw
            # escape to preserve byte fidelity.
            return NoteRow(pitch=Pitch.rest(), duration=1,
                           fx_flags=(f'fx:raw_{b:02x}',)), 1
        return NoteRow(
            pitch=Pitch(name=_NOTE_NAMES[semitone], octave=octave),
            duration=1,
        ), 1
    if b == 0x80:
        return NoteRow(pitch=Pitch.rest(), duration=1), 1
    if b == 0x81:
        return None, 1                              # caller folds
    if b == 0x82:
        # SET DURATION: this byte + operand byte; engine idles for
        # `follow` frames after processing.
        return NoteRow(pitch=Pitch.rest(), duration=1 + follow,
                       fx_flags=(f'set_dur=${follow:02X}',)), 2

    # NOTE: callers must check for the trailing-$82 edge case (where
    # the engine touched $82 but never read its operand because the
    # capture exited mid-instruction). See `_rows_from_bytes`.
    nibble = b & 0x0F
    if 0xB0 <= b <= 0xBF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'tempo={nibble}',)), 1
    if 0xC0 <= b <= 0xCF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'vol={nibble}',)), 1
    if 0xD0 <= b <= 0xDF:
        # Engine INCs the value; USF stores instr id = nibble+1.
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       instr=InstrumentRef(id=nibble + 1)), 1
    if 0xE0 <= b <= 0xEF:
        return NoteRow(pitch=Pitch.rest(), duration=1,
                       fx_flags=(f'section_end={nibble}',)), 1
    # $83..$AF, $F0..$FF — engine's proc_note dispatch falls through
    # to a skip path. Preserve byte fidelity via raw escape.
    return NoteRow(pitch=Pitch.rest(), duration=1,
                   fx_flags=(f'fx:raw_{b:02x}',)), 1


def _rows_from_bytes(bytes_seq: list[int]) -> list[NoteRow]:
    """Walk the captured per-voice byte stream → list of NoteRows.

    `$81` SKIP bytes fold into the preceding row's duration. The
    stream's terminating byte often isn't on a clean boundary (we
    captured everything in `min..max` ptr range); we walk
    instruction-by-instruction and stop when no more bytes can be
    consumed.
    """
    rows: list[NoteRow] = []
    i = 0
    while i < len(bytes_seq):
        b = bytes_seq[i]
        # Trailing-$82 edge case: capture exit happened at a $82 byte
        # before the engine could read the operand. The $82 byte is in
        # the captured stream but its operand is past the buffer end.
        # Encode as raw to preserve byte fidelity (round-trip == $82
        # alone, no operand).
        if b == 0x82 and i + 1 >= len(bytes_seq):
            rows.append(NoteRow(pitch=Pitch.rest(), duration=1,
                                fx_flags=('fx:raw_82',)))
            i += 1
            continue
        follow = bytes_seq[i + 1] if i + 1 < len(bytes_seq) else 0
        row, consumed = _row_from_byte(b, follow)
        if row is None:
            # $81 SKIP — extend last row's duration.
            if not rows:
                rows.append(NoteRow(pitch=Pitch.rest(), duration=2))
            else:
                rows[-1].duration += 1
            i += consumed
            continue
        rows.append(row)
        i += consumed
    return rows


def _read_psid_meta(sid_path: str) -> PsidMeta:
    raw = open(sid_path, 'rb').read()
    return PsidMeta(
        title=raw[0x16:0x36].rstrip(b'\x00').decode('latin-1'),
        author=raw[0x36:0x56].rstrip(b'\x00').decode('latin-1'),
        released=raw[0x56:0x76].rstrip(b'\x00').decode('latin-1'),
        clock={0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[
            (int.from_bytes(raw[0x76:0x78], 'big') >> 2) & 3],
        sid={0: 6581, 1: 6581, 2: 8580, 3: 6581}[
            (int.from_bytes(raw[0x76:0x78], 'big') >> 4) & 3],
        start_song=int.from_bytes(raw[0x10:0x12], 'big'),
        speed=int.from_bytes(raw[0x12:0x16], 'big'),
    )


def build_usf(json_path: str) -> UsfFile:
    """Build a UsfFile from a Type A JSON dump."""
    d = json.load(open(json_path))

    psid = _read_psid_meta(d['sid_path'])

    # Instruments: decode each program. USF inst id = engine
    # instrument-table index (= v_instr value after the engine's
    # $Dx-then-INC quirk). The dump skips leading invalid table
    # entries; for Ninja_Hamster + Counterforce both have entry
    # idx 0 invalid (garbage pointer) so first instrument id = 1.
    instruments = [
        decode_instrument(entry['idx'], entry['bytes'])
        for entry in d['instrument_base_table']['instruments']
    ]

    # Init: placeholder instr= the LOWEST defined instrument id. The
    # first `$Dx` in each voice's stream sets the actual instrument;
    # the placeholder only matters for validate()'s ref-resolution.
    placeholder_id = instruments[0].id if instruments else 1
    init = InitState(voices=[
        InitVoice(id=v + 1, instr=InstrumentRef(id=placeholder_id))
        for v in range(3)
    ])

    # Per-voice patterns from captured byte streams.
    voices = []
    for v_idx, vb in enumerate(d['voice_bytes']):
        rows = _rows_from_bytes(vb['bytes'])
        length = sum(r.duration for r in rows)
        voices.append(VoiceBlock(
            id=v_idx + 1,
            orderlist=Orderlist(entries=[1], loop_to=0),
            patterns=[Pattern(id=1, length=length, rows=rows)],
        ))

    # Top-level params: empty (engine-private mechanism stays out).
    params = Params()

    # Freq table: engine carries lo + hi each as 128 bytes; concat.
    freq_table = list(d['freq_table']['lo']) + list(d['freq_table']['hi'])

    # Single music subtune at id 0. tempo not used by jay_derrett's
    # engine the same way as Hubbard; the engine's `$Bx` rows carry
    # the actual tempo changes. Default tempo=1 so the validator
    # accepts the subtune.
    music = MusicSubtune(id=0, tempo=1, voices=voices)

    return UsfFile(
        psid=psid, params=params, init=init,
        instruments=instruments, subtunes=[music],
        freq_table=freq_table,
    )


def write_usf_for(name: str) -> str:
    """Build + validate + write `<NAME>.usf` for one Type A SID.

    Refuses excluded SIDs (see `tools/excluded_sids.json`).
    """
    from src.exclusions import check_or_raise
    sid_path = f'hvsc84/MUSICIANS/D/Derrett_Jay/{name}.sid'
    check_or_raise(sid_path)

    json_path = (f'pipelines/companion/jay_derrett/_extracted/{name}.json')
    usf = build_usf(json_path)
    out_path = f'hvsc84/MUSICIANS/D/Derrett_Jay/{name}.usf'
    out_dir = os.path.dirname(out_path)
    validate(usf)
    write_file(usf, out_path)
    return out_path


TYPE_A = [
    'Counterforce', 'Destruct', 'Discovery', 'Jetboys', 'Lifeforce',
    'Mandroid', 'Ninja_Hamster', 'Osmium', 'Road_Warrior', 'Stratton',
    'Thundercross', 'Traxxion', 'Trigger_Happy', 'Vengeance', 'ZIP',
]


def write_all_type_a() -> list[str]:
    """Write all 15 Type A USFs. Returns the list of output paths."""
    out_paths = []
    for name in TYPE_A:
        out_paths.append(write_usf_for(name))
    return out_paths


if __name__ == '__main__':
    paths = write_all_type_a()
    for p in paths:
        print(f'  wrote {p}')
    print(f'\nTotal: {len(paths)} USFs')
