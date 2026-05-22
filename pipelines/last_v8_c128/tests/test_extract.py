"""Smoke tests for the Last V8 (C128) extract pipeline.

Run from repo root:  pytest pipelines/last_v8_c128/tests/
"""
from __future__ import annotations

import pytest

from pipelines.last_v8_c128.extract.engine_model import extract


def test_header_parses_as_rsid() -> None:
    m = extract()
    assert m.header.magic == "RSID"
    assert m.header.load_addr == 0x4800
    assert m.header.init_addr == 0x7F40
    assert m.header.play_addr == 0x0000          # IRQ-driven
    assert m.header.songs == 18
    assert m.header.start_song == 1              # 1-indexed in header
    assert m.header.name == "The Last V8 (C128 version)"
    assert m.header.author == "Rob Hubbard"


def test_subtune_routes_match_dispatcher_in_disassembly() -> None:
    m = extract()
    kinds = [r.kind for r in m.routes]
    # Per $7E80: <3 music, 3..5 sample, >=6 sfx.
    assert kinds[:3] == ["music"] * 3
    assert kinds[3:6] == ["sample"] * 3
    assert kinds[6:] == ["sfx"] * (m.header.songs - 6)


def test_sample_records_match_disassembly() -> None:
    m = extract()
    samples = m.samples
    assert len(samples) == 3
    assert (samples[0].subtune, samples[0].start, samples[0].end) \
        == (3, 0x4800, 0x582F)
    assert (samples[1].subtune, samples[1].start, samples[1].end) \
        == (4, 0x5830, 0x690D)
    assert (samples[2].subtune, samples[2].start, samples[2].end) \
        == (5, 0x690E, 0x7B2F)
    # All samples share the same CIA Timer A threshold ($C0).
    for s in samples:
        assert s.rate_constant == 0xC0


def test_relocator_window_matches_disassembly() -> None:
    m = extract()
    assert m.relocator_src == 0x7B40
    assert m.relocator_len == 0x0400
    assert m.relocator_dst == 0xC000


def test_freq_table_starts_with_classic_hubbard_value() -> None:
    """First entry of the $843B freq table is $0116, same as Action Biker
    and every other 1985 Hubbard SID that ships its own 96-semitone table."""
    m = extract()
    assert m.freq_table[0] == (0x16, 0x01)
    # 96 semitones, all non-zero.
    assert len(m.freq_table) == 96
    for lo, hi in m.freq_table:
        assert (lo, hi) != (0, 0)


def test_subtune_out_of_range_raises_value_error() -> None:
    with pytest.raises(ValueError, match=r"subtune"):
        extract(subtune=99)


# ----- orderlist + pattern decoding ----------------------------------

def test_three_music_subtunes_decoded() -> None:
    m = extract()
    assert len(m.music_subtunes) == 3
    assert [s.subtune for s in m.music_subtunes] == [0, 1, 2]
    for s in m.music_subtunes:
        assert len(s.voices) == 3
        assert [v.voice for v in s.voices] == [0, 1, 2]


def test_subtune_0_is_the_title_loop() -> None:
    """Subtune 0 is the long title track — orderlists loop via $FF."""
    m = extract()
    s0 = m.music_subtunes[0]
    for v in s0.voices:
        assert v.terminator == 'restart', f'voice {v.voice}'
    # V2 is the bass line and is the longest orderlist in this binary.
    assert max(len(v.indices) for v in s0.voices) == len(s0.voices[2].indices)


def test_subtunes_1_and_2_are_jingles() -> None:
    """Subtunes 1 and 2 are short jingles that terminate via $FE."""
    m = extract()
    for s in m.music_subtunes[1:]:
        for v in s.voices:
            assert v.terminator == 'end_song', f'subtune {s.subtune} V{v.voice}'


def test_orderlist_indices_in_pattern_range() -> None:
    """Every referenced pattern index must resolve to a decoded pattern."""
    m = extract()
    valid = {p.index for p in m.patterns}
    for s in m.music_subtunes:
        for v in s.voices:
            for idx in v.indices:
                assert idx in valid, (
                    f'subtune {s.subtune} V{v.voice} references '
                    f'undecoded pattern {idx}'
                )


def test_pattern_count_matches_max_referenced() -> None:
    m = extract()
    referenced = {idx for s in m.music_subtunes for v in s.voices
                  for idx in v.indices}
    assert len(m.patterns) == max(referenced) + 1


def test_pattern_5_first_event_matches_disassembly() -> None:
    """Pattern 5 at $8932 starts with hold $83 (FX-follows, hold=3),
    FX byte $04 (instrument 4), pitch byte 62. Spot-check decoder."""
    m = extract()
    p5 = m.patterns[5]
    assert p5.addr == 0x8932
    ev0 = p5.events[0]
    assert ev0.kind == 'note'
    assert ev0.hold_byte == 0x83
    assert ev0.hold == 3
    assert ev0.instrument == 4
    assert ev0.arp_mode is None
    assert ev0.pitch == 62


# ----- instrument table ----------------------------------------------

def test_instrument_table_size_excludes_padding() -> None:
    """19 records carry real data; the rest are all-zero padding."""
    m = extract()
    assert len(m.instruments) == 19
    for i in m.instruments:
        assert not i.is_empty, f'instrument {i.id} is empty'


def test_instrument_0_matches_disassembly_dump() -> None:
    """Instrument 0 at $85A1: PW=$0800 ctrl=$11 AD=$04 SR=$0F vib=$02 pwm=$00 fx=$01."""
    inst0 = extract().instruments[0]
    assert inst0.id == 0
    assert inst0.pulse_width == 0x0800
    assert inst0.ctrl == 0x11           # triangle + gate
    assert inst0.ad == 0x04
    assert inst0.sr == 0x0F
    assert inst0.vib_shift == 0x02
    assert inst0.pwm == 0x00
    assert inst0.fx_flags == 0x01
    assert inst0.has_portamento is True
    assert inst0.has_note_cut is False


def test_fx_flag_bits_decode() -> None:
    """Spot-check instruments with notable fx_flags from the dump."""
    insts = {i.id: i for i in extract().instruments}
    # Inst 2: fx=$08 → only pulse-arp set
    assert insts[2].has_pulse_arp and not insts[2].has_arpeggio
    # Inst 6: fx=$04 → arpeggio
    assert insts[6].has_arpeggio and not insts[6].has_pulse_arp
    # Inst 13: fx=$02 → note-cut
    assert insts[13].has_note_cut and not insts[13].has_portamento


def test_every_referenced_instrument_has_an_entry() -> None:
    m = extract()
    referenced = {ev.instrument for p in m.patterns for ev in p.events
                  if ev.instrument is not None}
    ids = {i.id for i in m.instruments}
    assert referenced.issubset(ids), (
        f'patterns reference {referenced - ids} but those have no instrument '
        f'records'
    )


def test_ctrl_byte_has_gate_bit_set() -> None:
    """Every Hubbard instrument's ctrl byte has bit 0 (gate) set, so the
    waveform is held until note-off explicitly clears it."""
    for inst in extract().instruments:
        assert inst.ctrl & 0x01, (
            f'instrument {inst.id}: ctrl=${inst.ctrl:02X} has no gate bit'
        )


def test_every_pattern_terminates_inside_binary() -> None:
    m = extract()
    end = m.header.load_addr + len(m.payload_bytes)
    for p in m.patterns:
        assert p.addr < p.end_addr <= end, (
            f'pattern {p.index} bounds: ${p.addr:04X} → ${p.end_addr:04X}'
        )
