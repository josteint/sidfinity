"""Tests for the FC data emitters (patterns + sequences + tables from USF).

The pattern encoder is checked by the tightest available proxy: encode a
USF pattern, decode it back through the engine's own decoder + the to_usf
lowering, and require the resulting NoteRows to match the input — i.e. the
emitted bytes carry the same musical content (the writelog verdict is the
final gate, exercised by verify_featuredriven in the regression).
"""
from __future__ import annotations

from pipelines.future_composer.engine_model import extract, _parse_pattern, Pattern as FCPattern
from pipelines.future_composer.cybernoid_ii.config import CYBERNOID_II
from pipelines.future_composer.to_usf import _build_pattern_rows
from pipelines.future_composer.data_emit import (
    encode_pattern, build_music_data, build_pattern_pool,
)


def _rowsig(rows):
    return [(r.pitch.name, r.pitch.octave, r.duration,
             r.instr.id if r.instr else None, tuple(sorted(r.fx_flags)))
            for r in rows]


def _materialized(rows, seed=1):
    """Resolve stated-inherited durations with a simple thread (seed=1 =
    the engine's init nootleng+1) so the encoder sees effective rows —
    what build_pattern_pool's interpreter feeds it."""
    import dataclasses
    out, cur = [], seed
    for r in rows:
        cur = r.duration if r.duration is not None else cur
        out.append(dataclasses.replace(r, duration=cur))
    return out


def test_pattern_encode_roundtrips_to_same_content():
    """Every Cyb II pattern: USF rows -> FC bytes -> decode -> lower must
    reproduce the same NoteRows (durations materialized, as the composer's
    resolution interpreter does)."""
    song = extract(CYBERNOID_II)
    assert song.patterns
    for fc_id, pat in song.patterns.items():
        rows, _ = _build_pattern_rows(pat)
        rows = _materialized(rows)
        encoded = encode_pattern(rows)
        assert encoded[-1] == 0xFF, f'pat {fc_id} not $FF-terminated'
        ev, _ = _parse_pattern(encoded)
        reb = FCPattern(id=0, start_addr=0, bytes_raw=encoded,
                        events=ev, notes_count=0)
        reb_rows, _ = _build_pattern_rows(reb)
        assert _rowsig(_materialized(reb_rows)) == _rowsig(rows), \
            f'pattern {fc_id} mismatch'


def test_build_music_data_layout_consistent():
    """build_music_data produces a block whose seq_table/pattern_ptr offsets
    fall inside the block and whose pointers are within the block span."""
    from src.usf import parse
    from src.usf.types import MusicSubtune
    from pathlib import Path
    usf_path = Path('hvsc85/MUSICIANS/T/Tel_Jeroen/Cybernoid_II.usf')
    if not usf_path.exists():
        return
    usf = parse(usf_path.read_text())
    subs = [s for s in usf.subtunes if isinstance(s, MusicSubtune)]
    base = 0xB718
    md = build_music_data(subs, base)
    assert md['base'] == base
    assert md['seq_table_addr'] == base
    assert md['pattern_ptr_addr'] > base
    assert md['size'] == len(md['block'])
    # pattern_ptr_table entries point inside the block span.
    span = range(base, base + md['size'])
    ppt = md['pattern_ptr_addr'] - base
    for slot in range(md['n_slots']):
        lo = md['block'][ppt + slot * 2]
        hi = md['block'][ppt + slot * 2 + 1]
        assert (lo | (hi << 8)) in span
