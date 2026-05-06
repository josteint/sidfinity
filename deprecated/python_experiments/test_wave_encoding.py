"""
test_wave_encoding.py — Test wave table absolute_note encoding through the full pipeline.

Tests that a USF Song with a custom freq table and absolute_note wave table steps
produces correct SID register output (correct frequencies) via the codegen pipeline.

Covers the known encoding bugs:
1. absolute_note=0 bug (mapped to keep_freq) — fixed by dummy at index 0
2. Instrument indexing off-by-one — 0-indexed in USF, packer adds +1
3. Wave table loop target calculation
4. 8-frame startup delay before first note sounds
"""

import sys
import os
import struct

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'py65_lib'))
sys.path.insert(0, os.path.dirname(__file__))

from py65.devices.mpu6502 import MPU
from usf.format import Song, Instrument, Pattern, NoteEvent, WaveTableStep
from converters.usf_to_sid import usf_to_sid


def run_sid_frames(sid_path, n_frames=30, subtune=0):
    """Run a SID file in py65 for n_frames, return list of (freq_lo, freq_hi, ctrl) per frame."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr_raw = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]

    code = data[header_len:]
    if load_addr_raw == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        load_addr = load_addr_raw
        binary = code

    mem = bytearray(65536)
    mem[load_addr:load_addr + len(binary)] = binary
    mem[0xFFF0] = 0x00  # BRK sentinel

    mpu = MPU()
    mpu.memory = mem
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = subtune
    for _ in range(100000):
        if mpu.memory[mpu.pc] == 0x00:
            break
        mpu.step()

    results = []
    for _ in range(n_frames):
        mpu.stPush(0xEF >> 8)
        mpu.stPush(0xEF & 0xFF)
        mpu.pc = play_addr
        for _ in range(50000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()

        freq_lo = mpu.memory[0xD400]
        freq_hi = mpu.memory[0xD401]
        ctrl = mpu.memory[0xD404]
        results.append((freq_lo, freq_hi, ctrl))

    return results


def test_absolute_note_encoding():
    """Test that absolute_note in wave table steps produces correct frequencies.

    Custom freq table:
      Index 0: dummy (0x0001) — avoids absolute_note=0 ambiguity
      Index 1: freq 0x0116  (C-0 in standard PAL)
      Index 2: freq 0x0127  (C#-0)
      Index 3: freq 0x0138
      Index 4: freq 0x014B

    Wave table: abs_note=1, abs_note=2, loop → abs_note=1
    Expected frames 8+: alternating freq 0x0116 / 0x0127
    """
    song = Song()
    song.tempo = 6
    song.nowavedelay = True

    # Custom freq table (5 entries, index 0 is dummy)
    song.freq_lo = bytes([0x01, 0x16, 0x27, 0x38, 0x4B])
    song.freq_hi = bytes([0x00, 0x01, 0x01, 0x01, 0x01])

    # Instrument 0 (0-indexed): saw wave, alternates abs_note 1 and 2
    inst = Instrument(id=0, ad=0x0F, sr=0x00, waveform='saw')
    inst.wave_table = [
        WaveTableStep(waveform=0x21, absolute_note=1),  # saw+gate, note 1
        WaveTableStep(waveform=0x20, absolute_note=2),  # saw, note 2
        WaveTableStep(is_loop=True, loop_target=0),     # loop back to step 0
    ]
    song.instruments = [inst]

    patt = Pattern(id=0)
    patt.events = [NoteEvent(type='note', note=0, duration=20, instrument=0)]
    song.patterns = [patt]
    song.orderlists = [[(0, 0)], [], []]
    song.orderlist_restart = [0, 0, 0]

    sid_path = '/tmp/test_wave_encode_abs.sid'
    usf_to_sid(song, sid_path)
    frames = run_sid_frames(sid_path, n_frames=25)

    # Frames 0-7: init delay (freq=0, ctrl=0 or 0x41)
    # Frame 8+: alternating freq 0x0116 / 0x0127
    active = [(fl, fh, c) for fl, fh, c in frames if (fh << 8 | fl) != 0]
    assert active, "No active frames — wave table never produced freq output"

    # Find first non-zero frame
    first_active = next(i for i, (fl, fh, c) in enumerate(frames) if (fh << 8 | fl) != 0)
    assert first_active < 15, f"First active frame too late: {first_active}"

    # Check alternating pattern starting from first active frame
    for i, (fl, fh, c) in enumerate(frames[first_active:first_active + 10]):
        freq = (fh << 8) | fl
        if i % 2 == 0:
            assert freq == 0x0116, f"Frame {first_active+i}: expected freq 0x0116, got 0x{freq:04X}"
        else:
            assert freq == 0x0127, f"Frame {first_active+i}: expected freq 0x0127, got 0x{freq:04X}"

    print(f"  PASS: absolute_note encoding, first active frame={first_active}, "
          f"alternating freqs 0x0116/0x0127")
    return True


def test_absolute_note_zero_workaround():
    """Test that absolute_note=0 is avoided by using dummy at index 0.

    Without the dummy, sng_r = 0x80 + 0 = 0x80, XOR 0x80 = 0x00 = keep_freq.
    With dummy at index 0, real freqs start at index 1.
    This test verifies the dummy pattern works correctly.
    """
    song = Song()
    song.tempo = 6
    song.nowavedelay = True

    # Index 0 = dummy, index 1 = first real freq
    song.freq_lo = bytes([0xFF, 0x14, 0xAF])  # dummy at 0, two real entries
    song.freq_hi = bytes([0x00, 0x05, 0x14])

    inst = Instrument(id=0, ad=0x0F, sr=0x00, waveform='saw')
    inst.wave_table = [
        WaveTableStep(waveform=0x21, absolute_note=1),  # must NOT use index 0
        WaveTableStep(is_loop=True, loop_target=0),
    ]
    song.instruments = [inst]

    patt = Pattern(id=0)
    patt.events = [NoteEvent(type='note', note=0, duration=20, instrument=0)]
    song.patterns = [patt]
    song.orderlists = [[(0, 0)], [], []]
    song.orderlist_restart = [0, 0, 0]

    sid_path = '/tmp/test_wave_encode_zero.sid'
    usf_to_sid(song, sid_path)
    frames = run_sid_frames(sid_path, n_frames=20)

    active = [(fl, fh) for fl, fh, c in frames if (fh << 8 | fl) != 0 and (fh << 8 | fl) != 0x00FF]
    assert active, "No active frames with correct freq"
    fl, fh = active[0]
    freq = (fh << 8) | fl
    # Should be freq_lo[1]=0x14, freq_hi[1]=0x05 → 0x0514
    assert freq == 0x0514, f"Expected freq 0x0514 (index 1), got 0x{freq:04X} (got index-0 dummy?)"
    print(f"  PASS: absolute_note=0 workaround, got correct freq 0x{freq:04X}")
    return True


def test_instrument_indexing():
    """Test that 0-indexed instruments in USF map correctly through the packer.

    The packer adds +1 when encoding instrument bytes: inst_id=0 → pattern byte $01.
    The player reads $01, loads mt_insad-1+1 = mt_insad[0] = first instrument. ✓
    Previously bug: 1-indexed inst_id=1 → pattern byte $02 → mt_insad[1] = second (OOB).
    """
    song = Song()
    song.tempo = 6
    song.nowavedelay = True
    song.freq_lo = bytes([0x01, 0x16])  # dummy + one freq
    song.freq_hi = bytes([0x00, 0x01])

    # TWO instruments (0-indexed: 0 and 1)
    inst0 = Instrument(id=0, ad=0xA0, sr=0x00, waveform='saw')  # AD=0xA0
    inst0.wave_table = [WaveTableStep(waveform=0x21, absolute_note=1),
                        WaveTableStep(is_loop=True, loop_target=0)]

    inst1 = Instrument(id=1, ad=0x50, sr=0x00, waveform='pulse')  # AD=0x50
    inst1.wave_table = [WaveTableStep(waveform=0x41, absolute_note=1),
                        WaveTableStep(is_loop=True, loop_target=0)]

    song.instruments = [inst0, inst1]

    # Pattern uses instrument 0 only
    patt = Pattern(id=0)
    patt.events = [NoteEvent(type='note', note=0, duration=20, instrument=0)]
    song.patterns = [patt]
    song.orderlists = [[(0, 0)], [], []]
    song.orderlist_restart = [0, 0, 0]

    sid_path = '/tmp/test_inst_index.sid'
    usf_to_sid(song, sid_path)
    frames = run_sid_frames(sid_path, n_frames=20)

    # With correct indexing, instrument 0 (saw, AD=0xA0) plays
    # With wrong indexing (+1 bug), instrument 1 (pulse, AD=0x50) would play
    # Check that freq from wave table is correct (freq_lo[1]=0x16)
    active = [(fl, fh, c) for fl, fh, c in frames if (fh << 8 | fl) != 0]
    assert active, "No active frames"
    fl, fh, c = active[0]
    freq = (fh << 8) | fl
    assert freq == 0x0116, f"Expected 0x0116 (inst 0 wave table), got 0x{freq:04X}"
    # Waveform: saw=0x21 (gate+saw) → ctrl bit = 0x21
    assert (c & 0x60) == 0x20, f"Expected saw waveform (ctrl & 0x60 = 0x20), got 0x{c:02X}"
    print(f"  PASS: instrument indexing, freq=0x{freq:04X}, ctrl=0x{c:02X}")
    return True


def test_multi_instrument_wave_table():
    """Test two instruments with different absolute notes in their wave tables."""
    song = Song()
    song.tempo = 6
    song.nowavedelay = True
    song.freq_lo = bytes([0x01, 0x16, 0x27, 0x4B, 0x96])
    song.freq_hi = bytes([0x00, 0x01, 0x01, 0x01, 0x01])

    # Instrument 0: abs_note=1 (freq 0x0116)
    inst0 = Instrument(id=0, ad=0x0F, sr=0x00, waveform='saw')
    inst0.wave_table = [WaveTableStep(waveform=0x21, absolute_note=1),
                        WaveTableStep(waveform=0x20, absolute_note=1),
                        WaveTableStep(is_loop=True, loop_target=1)]

    # Instrument 1: abs_note=3 (freq 0x014B)
    inst1 = Instrument(id=1, ad=0x0F, sr=0x00, waveform='saw')
    inst1.wave_table = [WaveTableStep(waveform=0x21, absolute_note=3),
                        WaveTableStep(waveform=0x20, absolute_note=3),
                        WaveTableStep(is_loop=True, loop_target=1)]

    song.instruments = [inst0, inst1]

    # Voice 1 uses inst 0, voice 2 uses inst 1
    patt_v1 = Pattern(id=0)
    patt_v1.events = [NoteEvent(type='note', note=0, duration=20, instrument=0)]
    patt_v2 = Pattern(id=1)
    patt_v2.events = [NoteEvent(type='note', note=0, duration=20, instrument=1)]
    patt_v3 = Pattern(id=2)
    patt_v3.events = [NoteEvent(type='rest', note=0, duration=20, instrument=-1)]

    song.patterns = [patt_v1, patt_v2, patt_v3]
    song.orderlists = [[(0, 0)], [(1, 0)], [(2, 0)]]
    song.orderlist_restart = [0, 0, 0]

    sid_path = '/tmp/test_multi_inst.sid'
    usf_to_sid(song, sid_path)
    frames = run_sid_frames(sid_path, n_frames=25)

    # Voice 1: D400/D401 should be 0x0116
    # Voice 2: D407/D408 should be 0x014B
    with open(sid_path, 'rb') as f:
        data = f.read()
    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr_raw = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    code = data[header_len:]
    if load_addr_raw == 0:
        la = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        la = load_addr_raw
        binary = code
    mem = bytearray(65536)
    mem[la:la + len(binary)] = binary
    mem[0xFFF0] = 0x00
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'py65_lib'))
    from py65.devices.mpu6502 import MPU as M6
    mpu = M6()
    mpu.memory = mem
    mpu.stPush(0xFF); mpu.stPush(0xEF)
    mpu.pc = init_addr; mpu.a = 0
    for _ in range(100000):
        if mpu.memory[mpu.pc] == 0x00: break
        mpu.step()

    v1_ok = v2_ok = False
    for frame in range(20):
        mpu.stPush(0xEF >> 8); mpu.stPush(0xEF & 0xFF)
        mpu.pc = play_addr
        for _ in range(50000):
            if mpu.memory[mpu.pc] == 0x00: break
            mpu.step()
        v1 = (mpu.memory[0xD401] << 8) | mpu.memory[0xD400]
        v2 = (mpu.memory[0xD408] << 8) | mpu.memory[0xD407]
        if v1 == 0x0116: v1_ok = True
        if v2 == 0x014B: v2_ok = True

    assert v1_ok, "Voice 1: never saw freq 0x0116 for instrument 0"
    assert v2_ok, "Voice 2: never saw freq 0x014B for instrument 1"
    print(f"  PASS: multi-instrument wave tables, V1=0x0116, V2=0x014B")
    return True


def run_all():
    tests = [
        ("Absolute note encoding", test_absolute_note_encoding),
        ("Absolute note=0 workaround", test_absolute_note_zero_workaround),
        ("Instrument indexing (0-based)", test_instrument_indexing),
        ("Multi-instrument wave tables", test_multi_instrument_wave_table),
    ]

    passed = 0
    failed = 0
    for name, fn in tests:
        print(f"\n[TEST] {name}")
        try:
            fn()
            passed += 1
        except AssertionError as e:
            print(f"  FAIL: {e}")
            failed += 1
        except Exception as e:
            import traceback
            print(f"  ERROR: {e}")
            traceback.print_exc()
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed}/{passed+failed} passed")
    return failed == 0


if __name__ == '__main__':
    ok = run_all()
    sys.exit(0 if ok else 1)
