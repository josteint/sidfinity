"""Round-trip tests for the per-entry orderlist transpose (USF schema).

The FC family keeps transpose as a sequence-level modifier (one motif
reused at several pitches) rather than baking it into note pitches.
That is carried in USF as `Orderlist.transposes` and the `N+T`
orderlist-entry syntax. These tests pin the parse/write round-trip and
the backward-compatible default (no transposes → no `+` in output).
"""
from pathlib import Path

import pytest

from src.usf import parse, write
from src.usf.types import Orderlist, MusicSubtune

_ROOT = Path(__file__).resolve().parents[1]
_USF = _ROOT / 'hvsc85' / 'MUSICIANS' / 'T' / 'Tel_Jeroen' / 'Cybernoid_II.usf'


def _first_music_voice_orderlists(usf):
    for sub in usf.subtunes:
        if isinstance(sub, MusicSubtune):
            return sub.voices
    return []


def test_orderlist_default_has_no_transpose_token():
    """An orderlist with no transposes serializes with no `+` suffix."""
    o = Orderlist(entries=[0, 1, 2], loop_to=0)
    from src.usf.writer import _write_orderlist
    assert _write_orderlist(o) == '0 1 2 loop@0'
    assert o.transposes == []
    assert o.transpose_at(1) == 0


def test_orderlist_transpose_serialization():
    o = Orderlist(entries=[0, 1, 2], transposes=[0, 7, 12], stop=True)
    from src.usf.writer import _write_orderlist
    assert _write_orderlist(o) == '0 1+7 2+12 stop'


def test_orderlist_all_modifiers_serialization():
    # a[*b][+c][^d] — pattern, repeats, transpose, voiceinc combined.
    o = Orderlist(entries=[0, 5, 8, 2],
                  repeats=[1, 7, 4, 1],
                  transposes=[0, 0, 3, 0],
                  voiceincs=[0, 0, 0, 2],
                  loop_to=0)
    from src.usf.writer import _write_orderlist
    assert _write_orderlist(o) == '0 5*7 8*4+3 2^2 loop@0'


def test_orderlist_all_modifiers_roundtrip():
    o = Orderlist(entries=[0, 5, 8, 2],
                  repeats=[1, 7, 4, 1],
                  transposes=[0, 0, 3, 0],
                  voiceincs=[0, 0, 0, 2],
                  loop_to=0)
    from src.usf.writer import _write_orderlist
    from src.usf.parser import _T
    from lark import Lark
    from pathlib import Path
    grammar = (Path(__file__).resolve().parents[1] /
               'src' / 'usf' / 'grammar.lark').read_text()
    # Parse just the orderlist fragment via the full grammar's start.
    text = _write_orderlist(o)
    p = Lark(grammar, start='orderlist', parser='lalr')
    ol = _T().transform(p.parse(text))
    assert ol.entries == o.entries
    assert [ol.repeat_at(i) for i in range(4)] == [1, 7, 4, 1]
    assert [ol.transpose_at(i) for i in range(4)] == [0, 0, 3, 0]
    assert [ol.voiceinc_at(i) for i in range(4)] == [0, 0, 0, 2]


def test_orderlist_modifier_validation():
    for bad in ('transposes', 'voiceincs', 'repeats'):
        with pytest.raises(ValueError):
            Orderlist(entries=[0, 1], **{bad: [7]})  # length mismatch


@pytest.mark.skipif(not _USF.exists(), reason='Cyb II USF not present')
def test_full_usf_roundtrip_stable():
    """write(parse(x)) round-trips a real USF unchanged through a second
    parse (structural stability of the new grammar)."""
    src = _USF.read_text()
    usf1 = parse(src)
    out1 = write(usf1)
    usf2 = parse(out1)
    out2 = write(usf2)
    assert out1 == out2


@pytest.mark.skipif(not _USF.exists(), reason='Cyb II USF not present')
def test_injected_transpose_survives_roundtrip():
    """Inject per-entry transposes into a real USF; they survive a
    write → parse round-trip with `N+T` syntax."""
    usf = parse(_USF.read_text())
    voices = _first_music_voice_orderlists(usf)
    assert voices, 'expected a music subtune with voices'
    ol = voices[0].orderlist
    n = len(ol.entries)
    assert n >= 2
    injected = [(i * 3) % 24 for i in range(n)]   # some zero, some non-zero
    ol.transposes = injected

    text = write(usf)
    assert '+' in text   # at least one non-zero transpose emitted

    usf2 = parse(text)
    ol2 = _first_music_voice_orderlists(usf2)[0].orderlist
    assert ol2.entries == ol.entries
    # All-zero suffix is omitted on write; transpose_at reconstructs it.
    assert [ol2.transpose_at(i) for i in range(n)] == injected
