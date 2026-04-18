"""
test_semantics.py — Property tests for the formal USF semantics.

Tests specific USF features against expected register behavior,
independent of siddump and the V2 compiled player. These tests
verify the SPECIFICATION, not the implementation match.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from usf.format import (Song, Instrument, Pattern, NoteEvent, WaveTableStep,
                         PulseTableStep, FilterTableStep, SpeedTableEntry)
from formal.usf_semantics import USFPlayer, verify_determinism, verify_prefix


FREQ_HI_PAL = [
    0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x01,0x02,
    0x02,0x02,0x02,0x02,0x02,0x02,0x03,0x03,0x03,0x03,0x03,0x04,
    0x04,0x04,0x04,0x05,0x05,0x05,0x06,0x06,0x06,0x07,0x07,0x08,
    0x08,0x09,0x09,0x0A,0x0A,0x0B,0x0C,0x0D,0x0D,0x0E,0x0F,0x10,
    0x11,0x12,0x13,0x14,0x15,0x17,0x18,0x1A,0x1B,0x1D,0x1F,0x20,
    0x22,0x24,0x27,0x29,0x2B,0x2E,0x31,0x34,0x37,0x3A,0x3E,0x41,
    0x45,0x49,0x4E,0x52,0x57,0x5C,0x62,0x68,0x6E,0x75,0x7C,0x83,
    0x8B,0x93,0x9C,0xA5,0xAF,0xB9,0xC4,0xD0,0xDD,0xEA,0xF8,0xFF]


def make_simple_song(notes, tempo=6, ad=0x09, sr=0x00, waveform=0x41):
    """Create a minimal song with one voice playing the given notes."""
    events = []
    for note in notes:
        if note >= 0:
            events.append(NoteEvent(type='note', note=note, duration=1, instrument=0))
        else:
            events.append(NoteEvent(type='rest', duration=1))
    # Pad with rests to fill one tick
    while len(events) < tempo:
        events.append(NoteEvent(type='rest', duration=1))

    song = Song(
        tempo=tempo,
        instruments=[
            Instrument(id=0, ad=ad, sr=sr, waveform='pulse',
                       wave_ptr=1, gate_timer=2),
        ],
        patterns=[Pattern(id=0, events=events)],
        orderlists=[[(0, 0)], [], []],
        orderlist_restart=[0, 0, 0],
        # Wave table: waveform + relative note 0 (uses current note's freq),
        # then loop. Right=$00 = relative +0 in .sng format.
        shared_wave_table=[
            (waveform, 0x00),   # waveform + relative note 0 → freq lookup
            (0xFF, 0x01),       # loop to position 1
        ],
        nowavedelay=True,
    )
    return song


def test_determinism():
    song = make_simple_song([48, -1, -1, -1, -1, 50])
    assert verify_determinism(song), "Determinism failed"


def test_prefix():
    song = make_simple_song([48, -1, -1, -1, -1, 50])
    assert verify_prefix(song), "Prefix property failed"


def test_single_note_frequency():
    """A single note should produce the correct freq_hi."""
    song = make_simple_song([48])  # C4
    player = USFPlayer(song)
    trace = player.run(20)
    # Find the first frame with non-zero freq_hi on voice 1
    for i, frame in enumerate(trace):
        if frame[1] > 0:
            assert frame[1] == FREQ_HI_PAL[48], \
                "Note 48 (C4) should have freq_hi=$%02X, got $%02X at frame %d" % (
                    FREQ_HI_PAL[48], frame[1], i)
            return
    assert False, "No frequency output found"


def test_note_sequence():
    """Two consecutive notes should produce different frequencies."""
    song = make_simple_song([48, -1, -1, -1, -1, 60])  # C4, then C5
    player = USFPlayer(song)
    trace = player.run(60)  # Need enough frames for second note
    fhis = [frame[1] for frame in trace]
    found_48 = FREQ_HI_PAL[48] in fhis
    found_60 = FREQ_HI_PAL[60] in fhis
    assert found_48, "Note 48 not found in trace"
    assert found_60, "Note 60 not found in trace"


def test_gate_on_off():
    """Note should have gate on, off event should have gate off."""
    song = make_simple_song([48])
    # Add an off event
    song.patterns[0].events.append(NoteEvent(type='off', duration=1))
    song.patterns[0].events.append(NoteEvent(type='rest', duration=4))

    player = USFPlayer(song)
    trace = player.run(50)
    # Find frames with waveform
    gate_on_found = False
    gate_off_found = False
    for frame in trace:
        wav = frame[4]
        if wav & 0x01:
            gate_on_found = True
        if (wav & 0xF0) and not (wav & 0x01):
            gate_off_found = True
    assert gate_on_found, "Gate-on frame not found"
    assert gate_off_found, "Gate-off frame not found"


def test_adsr_on_note():
    """ADSR should be set from instrument on note frame."""
    song = make_simple_song([48], ad=0x12, sr=0x34)
    player = USFPlayer(song)
    trace = player.run(20)
    for frame in trace:
        if frame[5] == 0x12 and frame[6] == 0x34:
            return  # Found correct ADSR
    assert False, "ADSR $12/$34 not found"


def test_hard_restart():
    """Hard restart should set AD=$0F, SR=$00 before new note."""
    song = make_simple_song([48, -1, -1, -1, -1, 50])
    song.instruments[0].gate_timer = 2
    player = USFPlayer(song)
    trace = player.run(25)
    # Look for HR pattern: AD=$0F before note 50
    hr_found = False
    for i in range(1, len(trace)):
        if trace[i][5] == 0x0F and trace[i][6] == 0x00:
            hr_found = True
            break
    assert hr_found, "Hard restart (AD=$0F) not found before second note"


def test_volume():
    """Master volume should be $0F."""
    song = make_simple_song([48])
    player = USFPlayer(song)
    trace = player.run(10)
    for frame in trace:
        vol = frame[24] & 0x0F
        assert vol == 0x0F, "Volume should be $0F, got $%X" % vol


def test_filter_cutoff():
    """Filter cutoff command should change register $D416."""
    events = [
        NoteEvent(type='note', note=48, duration=1, instrument=0,
                  command=0xC, command_val=0x80),  # Set filter cutoff $80
    ]
    for _ in range(5):
        events.append(NoteEvent(type='rest', duration=1))

    song = Song(
        tempo=6,
        instruments=[Instrument(id=0, ad=0x09, sr=0x00, wave_ptr=1, gate_timer=0)],
        patterns=[Pattern(id=0, events=events)],
        orderlists=[[(0, 0)], [], []],
        orderlist_restart=[0, 0, 0],
        shared_wave_table=[(0x41, 0x80)],
        shared_filter_table=[],
        nowavedelay=True,
    )
    player = USFPlayer(song)
    trace = player.run(15)
    cutoff_found = any(frame[22] == 0x80 for frame in trace)
    assert cutoff_found, "Filter cutoff $80 not found in register $D416"


def test_tempo_change():
    """Tempo command should change tick rate."""
    events = [
        NoteEvent(type='note', note=48, duration=1, instrument=0,
                  command=0xF, command_val=3),  # Set tempo to 3
    ]
    for _ in range(20):
        events.append(NoteEvent(type='rest', duration=1))

    song = Song(
        tempo=6,
        instruments=[Instrument(id=0, ad=0x09, sr=0x00, wave_ptr=1, gate_timer=0)],
        patterns=[Pattern(id=0, events=events)],
        orderlists=[[(0, 0)], [], []],
        orderlist_restart=[0, 0, 0],
        shared_wave_table=[(0x41, 0x80)],
        nowavedelay=True,
    )
    player = USFPlayer(song)
    trace = player.run(20)
    # With tempo=3, the player should read patterns faster
    # Check that voice 1 tempo is 3
    assert player.voices[0].tempo == 3, "Tempo should be 3, got %d" % player.voices[0].tempo


def test_wave_table_arpeggio():
    """Wave table with note offsets should produce arpeggio."""
    song = Song(
        tempo=6,
        instruments=[
            Instrument(id=0, ad=0x09, sr=0x00, wave_ptr=1, gate_timer=0),
        ],
        patterns=[Pattern(id=0, events=[
            NoteEvent(type='note', note=48, duration=6, instrument=0),
        ])],
        orderlists=[[(0, 0)], [], []],
        orderlist_restart=[0, 0, 0],
        # Arpeggio: C4 (+0), E4 (+4), G4 (+7), loop
        shared_wave_table=[
            (0x41, 0x80),  # pulse+gate, keep freq (base note)
            (0x41, 0x84),  # pulse+gate, absolute note 4 (E0)...
            # Actually .sng right: $84 = absolute note 4 ($84 - $80 = 4)
            # But we want relative +4: .sng right $04 = relative +4
        ],
        nowavedelay=True,
    )
    # Fix: use relative note offsets
    song.shared_wave_table = [
        (0x41, 0x00),   # pulse+gate, relative +0
        (0x41, 0x04),   # pulse+gate, relative +4
        (0x41, 0x07),   # pulse+gate, relative +7
        (0xFF, 0x01),   # loop to position 1
    ]
    player = USFPlayer(song)
    trace = player.run(25)
    fhis = set(frame[1] for frame in trace if frame[1] > 0)
    # Should see freq_hi values for notes 48, 52, 55
    expected = {FREQ_HI_PAL[48], FREQ_HI_PAL[52], FREQ_HI_PAL[55]}
    assert expected.issubset(fhis), \
        "Arpeggio should produce fhi values %s, got %s" % (expected, fhis)


# ============================================================
# Run all tests
# ============================================================

if __name__ == '__main__':
    tests = [
        test_determinism,
        test_prefix,
        test_single_note_frequency,
        test_note_sequence,
        test_gate_on_off,
        test_adsr_on_note,
        test_hard_restart,
        test_volume,
        test_filter_cutoff,
        test_tempo_change,
        test_wave_table_arpeggio,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print("  PASS  %s" % test.__name__)
            passed += 1
        except AssertionError as e:
            print("  FAIL  %s: %s" % (test.__name__, e))
            failed += 1
        except Exception as e:
            print("  ERROR %s: %s" % (test.__name__, e))
            failed += 1

    print("\n%d passed, %d failed out of %d tests" % (passed, failed, len(tests)))
