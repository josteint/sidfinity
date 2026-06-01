"""Round-trip verifier for jay_derrett Type A extracts.

Reconstructs each voice's orderlist byte stream from the USF's
NoteRows + compares against the bytes captured by play-capture
(stored in the JSON dump). If they match for all 15 SIDs, the USF
schema fully captures the orderlist musical content — Phase 5's
composer codegen has a known-correct target to emit.

The round-trip is the inverse of `to_usf._row_from_byte()`:

  Note(pitch, ...)                  → octave << 4 | semitone
  rest                              → $80
  + $81 SKIP folds: previous row's `duration > 1` → trailing $81s
  fx_flags=('set_dur=$NN',)          → $82 NN
  fx_flags=('tempo=N',)              → $B(N)
  fx_flags=('vol=N',)                → $C(N)
  instr=InstrumentRef(id=N+1)        → $D(N)
  fx_flags=('section_end=N',)        → $E(N)
  fx_flags=('fx:raw_NN',)            → NN

Run:
    PYTHONPATH=. python3 pipelines/companion/jay_derrett/extract/verify_extract.py
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))))

from src.usf import parse_file


_NOTE_INDEX = {n: i for i, n in enumerate(
    ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'))}


def _bytes_for_row(row) -> list[int]:
    """Encode one NoteRow back to engine bytes. Returns the byte(s)
    for the row's primary instruction; `$81` SKIP folds are computed
    separately by the caller based on the row's duration.
    """
    # FX flags first — they take precedence over pitch/instr for
    # state-changing commands.
    flags = row.fx_flags or ()
    for f in flags:
        if f.startswith('set_dur='):
            # set_dur=$NN → $82 NN  (2 bytes)
            v = int(f.split('=', 1)[1].lstrip('$'), 16)
            return [0x82, v & 0xFF]
        if f.startswith('tempo='):
            return [0xB0 | (int(f.split('=', 1)[1]) & 0x0F)]
        if f.startswith('vol='):
            return [0xC0 | (int(f.split('=', 1)[1]) & 0x0F)]
        if f.startswith('section_end='):
            return [0xE0 | (int(f.split('=', 1)[1]) & 0x0F)]
        if f.startswith('fx:raw_'):
            return [int(f.split('_', 1)[1], 16)]
        if f == 'tie' or f == 'no_release' or f.startswith('porta=') or f.startswith('song_pos='):
            # Unhandled jay_derrett-style fx? Skip-pass through.
            continue

    # Instrument-change row ($Dx).
    if row.instr is not None and row.pitch.is_rest:
        # $D(N) where N = instr_id - 1 (engine INC quirk).
        return [0xD0 | ((row.instr.id - 1) & 0x0F)]

    # Note byte.
    if not row.pitch.is_rest:
        semi = _NOTE_INDEX[row.pitch.name]
        octave = row.pitch.octave
        return [((octave & 0x07) << 4) | (semi & 0x0F)]

    # Rest with no special flags → $80 (gate off).
    return [0x80]


def _voice_to_bytes(voice) -> bytes:
    """Reconstruct one voice's full byte stream from its single Pattern."""
    out = bytearray()
    if not voice.patterns:
        return bytes(out)
    pat = voice.patterns[0]
    for row in pat.rows:
        primary = _bytes_for_row(row)
        out.extend(primary)
        # Duration > number-of-cycles-this-row-occupies means $81 SKIP
        # extension. For $82 N, the row's intrinsic span is (1+N) cycles
        # (1 for the cmd byte + N idle). For everything else, intrinsic
        # span is 1 cycle. Trailing $81s fill any remaining duration.
        if len(primary) == 2 and primary[0] == 0x82:
            # $82 N takes (1 + N) cycles intrinsically.
            intrinsic = 1 + primary[1]
        else:
            intrinsic = 1
        skips = max(0, row.duration - intrinsic)
        out.extend([0x81] * skips)
    return bytes(out)


def verify_one(name: str) -> dict:
    """Round-trip verify one Type A SID. Returns per-voice match info."""
    json_path = f'pipelines/companion/jay_derrett/_extracted/{name}.json'
    usf_path = f'hvsc84/MUSICIANS/D/Derrett_Jay/{name}.usf'

    dump = json.load(open(json_path))
    usf = parse_file(usf_path)

    music = next(s for s in usf.subtunes if s.kind == 'music')
    voices = sorted(music.voices, key=lambda v: v.id)

    result = {'name': name, 'voices': []}
    for v_idx, voice in enumerate(voices):
        captured = bytes(dump['voice_bytes'][v_idx]['bytes'])
        reconstructed = _voice_to_bytes(voice)
        match_len = 0
        for a, b in zip(captured, reconstructed):
            if a != b:
                break
            match_len += 1
        result['voices'].append({
            'idx': v_idx,
            'captured_len': len(captured),
            'reconstructed_len': len(reconstructed),
            'match_prefix_len': match_len,
            'full_match': captured == reconstructed,
        })
    result['all_match'] = all(v['full_match'] for v in result['voices'])
    return result


def main() -> int:
    from pipelines.companion.jay_derrett.extract.to_usf import TYPE_A
    n_full = 0
    print(f'{"name":<18s} {"V1":<28s} {"V2":<28s} {"V3":<28s}')
    print('-' * 110)
    for name in TYPE_A:
        try:
            r = verify_one(name)
        except Exception as e:
            print(f'{name:<18s}  ERR: {type(e).__name__}: {e}')
            continue
        cols = []
        for v in r['voices']:
            marker = '✓' if v['full_match'] else '✗'
            ratio = v['match_prefix_len'] / max(1, v['captured_len'])
            cols.append(
                f'{marker} {v["match_prefix_len"]:4d}/{v["captured_len"]:4d}'
                f' ({100*ratio:5.1f}%)')
        if r['all_match']:
            n_full += 1
        print(f'{name:<18s} {cols[0]:<28s} {cols[1]:<28s} {cols[2]:<28s}')
    print()
    print(f'{n_full}/{len(TYPE_A)} byte-exact round-trip')
    return 0 if n_full == len(TYPE_A) else 1


if __name__ == '__main__':
    sys.exit(main())
