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


def _encode_instrument(inst, original_size: int = 24) -> bytes:
    """Re-encode a USF Instrument back into the engine's N-byte
    program (inverse of `decode_instrument`). Padding bytes ($09,
    $0D, $13) are emitted as zero since the engine doesn't read
    them — they don't affect the instruction stream.

    For instruments with `original_size > 24` (Counterforce's 31-byte
    programs), the extra bytes are emitted as zero (TODO: RE those
    layouts properly).
    """
    prog = bytearray(max(24, original_size))

    # bit-flags ($00) — bidirectional sets BOTH bit 1 (bidir) AND
    # bit 2 (bound-swap); one_shot_swap only sets bit 2; one_shot_halt
    # sets neither.
    flags = 0
    if inst.freq_slide_config.mode != 'none':
        if inst.freq_slide_config.initial_dir == 'down':
            flags |= 0x01
        if inst.freq_slide_config.mode == 'bidirectional':
            flags |= 0x06               # bits 1 + 2
        elif inst.freq_slide_config.mode == 'one_shot_swap':
            flags |= 0x04               # bit 2
        if inst.freq_slide_config.high_oct_arp:
            flags |= 0x80
    prog[0x00] = flags

    # freq init ($01-$02) — not in Instrument schema; engine sets at
    # note-start from freq_table[note]. Emit 0 (engine overwrites).

    # freq slide bounds + step ($03-$08)
    s = inst.freq_slide_config
    if s.mode != 'none':
        upper = s.upper_delta & 0xFFFF
        lower = s.lower_delta & 0xFFFF
        prog[0x03] = upper & 0xFF
        prog[0x04] = (upper >> 8) & 0xFF
        prog[0x05] = lower & 0xFF
        prog[0x06] = (lower >> 8) & 0xFF
        prog[0x07] = s.step & 0xFF
        prog[0x08] = (s.step >> 8) & 0xFF

    # $09: padding — emit 0.

    # PWM ($0A-$12)
    if inst.pwm.mode != 'none':
        prog[0x0A] = (inst.pwm.init >> 8) & 0xFF
        prog[0x0B] = inst.pwm.phase1_bound & 0xFF
        prog[0x0C] = inst.pwm.phase1_step & 0xFF
        # $0D: padding.
        prog[0x0E] = 0xFF if inst.pwm.phase1_dir == 'down' else 0x00
        # $0F: osc state init — always 0.
        prog[0x10] = inst.pwm.max_hi & 0xFF
        prog[0x11] = inst.pwm.min_hi & 0xFF
        prog[0x12] = inst.pwm.speed & 0xFF

    # $13: padding.

    # CTRL ($14), AD ($15), SR ($16), CTRL alt ($17)
    prog[0x14] = inst.waveform[0] if inst.waveform else 0
    prog[0x15] = inst.adsr[0]
    prog[0x16] = inst.adsr[1]
    # CTRL alt = release_ctrl XOR ctrl_on (since release_ctrl was
    # decoded as ctrl_on | ctrl_alt). Reversing the OR isn't unique
    # without knowing which bits ctrl_alt contributes, but the
    # principal case is XOR.
    prog[0x17] = (inst.envelope.release_ctrl ^ prog[0x14]) & 0xFF

    return bytes(prog[:original_size])


def verify_instruments(name: str) -> dict:
    """Round-trip verify the instrument programs for one Type A SID.

    For each instrument: decode → re-encode → compare against the
    original program bytes. Padding bytes ($09, $0D, $13) and the
    freq init slots ($01, $02) are expected to differ (engine
    overwrites them at note-start), so we report a `semantic_match`
    that masks those positions.
    """
    json_path = f'pipelines/companion/jay_derrett/_extracted/{name}.json'
    dump = json.load(open(json_path))
    from pipelines.companion.jay_derrett.extract.instrument import (
        decode_instrument)

    # Mask: positions we expect to differ between decoded+re-encoded
    # and the original (engine-overwritten or padding).
    DONT_CARE = {0x01, 0x02, 0x09, 0x0D, 0x13, 0x0F}

    n_full = n_semantic = 0
    diffs = []
    for entry in dump['instrument_base_table']['instruments']:
        orig = bytes(entry['bytes'])
        inst = decode_instrument(entry['idx'], orig)
        recon = _encode_instrument(inst, original_size=len(orig))
        # Compare only the first 24 bytes (rest is unanalyzed for
        # larger layouts like Counterforce's 31-byte).
        cmp_len = min(24, len(orig))
        orig24 = orig[:cmp_len]
        recon24 = recon[:cmp_len]
        full = orig24 == recon24
        semantic = all(
            o == r for i, (o, r) in enumerate(zip(orig24, recon24))
            if i not in DONT_CARE)
        if full: n_full += 1
        if semantic: n_semantic += 1
        if not semantic:
            diffs.append({
                'idx': entry['idx'],
                'diffs': [(i, o, r) for i, (o, r) in enumerate(zip(orig24, recon24))
                          if o != r and i not in DONT_CARE],
            })
    return {
        'name': name,
        'n_instruments': len(dump['instrument_base_table']['instruments']),
        'n_full_match': n_full,
        'n_semantic_match': n_semantic,
        'diffs': diffs,
    }


def verify_one(name: str) -> dict:
    """Round-trip verify one Type A SID. Returns per-voice match info."""
    json_path = f'pipelines/companion/jay_derrett/_extracted/{name}.json'
    usf_path = f'hvsc85/MUSICIANS/D/Derrett_Jay/{name}.usf'

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
    print(f'Orderlist round-trip: {n_full}/{len(TYPE_A)} byte-exact')

    # Instrument round-trip check.
    print()
    print('Instrument decode→encode round-trip (masking engine-overwritten + padding bytes):')
    print(f'{"name":<18s} {"full":<10s} {"semantic":<12s} {"diffs":<8s}')
    print('-' * 60)
    full_all = sem_all = total_all = 0
    for name in TYPE_A:
        try:
            r = verify_instruments(name)
        except Exception as e:
            print(f'{name:<18s}  ERR: {type(e).__name__}: {e}')
            continue
        marker = '✓' if r['n_full_match'] == r['n_instruments'] else ' '
        sem_marker = '✓' if r['n_semantic_match'] == r['n_instruments'] else ' '
        print(f'{name:<18s} {marker} {r["n_full_match"]:2d}/{r["n_instruments"]:2d}   '
              f'{sem_marker} {r["n_semantic_match"]:2d}/{r["n_instruments"]:2d}     '
              f'{len(r["diffs"]):3d}')
        full_all += r['n_full_match']
        sem_all  += r['n_semantic_match']
        total_all += r['n_instruments']
    print()
    print(f'Instrument round-trip: full {full_all}/{total_all}  '
          f'semantic {sem_all}/{total_all}')

    return 0 if n_full == len(TYPE_A) else 1


if __name__ == '__main__':
    sys.exit(main())
