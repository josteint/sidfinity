"""
build_commando_holyscale.py -- Build Commando_holyscale.sid.

Pipeline:
  1. Capture ground truth via py65 with real loop detection (loops at frame 3840)
  2. Build USF Song via holy_scale (extracts musical structure)
  3. Generate SID via holy_scale_codegen (raw per-frame PW = exact match)
     Note: min_loop_note=200 avoids spurious 32-note loop in early intro section
  4. Verify frame-by-frame with py65, reporting per-register error counts

The holy_scale_codegen uses raw per-frame register data from the ground truth,
ensuring exact PW match for both V1 (bidirectional 16-bit sweep, frames 774-900+)
and V3 (8-bit linear accumulation, frames 0-767).

The simple_codegen.py PW synthesis is verified separately via --test-simple:
  V1-style: bidirectional 16-bit sweep with min/max pw_hi boundaries
  V3-style: linear 8-bit wrap, pw_hi fixed (pw_max==$FF mode)

Output: demo/hubbard/Commando_holyscale.sid

Usage:
    source src/env.sh
    python3 src/build_commando_holyscale.py [--verify N] [--test-simple]
"""

import os
import sys
import struct
import argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

os.environ['PATH'] = (
    os.path.join(ROOT, 'tools', 'xa65', 'xa') + ':' +
    os.path.join(ROOT, 'tools') + ':' +
    os.environ.get('PATH', '')
)
os.environ.setdefault('SIDFINITY_ROOT', ROOT)

from ground_truth import load_sid, capture_subtune
from holy_scale import holy_scale
import holy_scale_codegen as _hsc
from holy_scale_codegen import verify_against_trace

COMMANDO_SID = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                             'Hubbard_Rob', 'Commando.sid')
OUT_SID = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_holyscale.sid')

# Minimum loop block length to avoid spurious early repeats in Commando's intro.
# The intro's main melody repeats every 32 notes; requiring >=200 forces the
# detector to find only genuine structural loops.
MIN_LOOP_NOTE = 200


# ---------------------------------------------------------------------------
# Per-register error analysis
# ---------------------------------------------------------------------------

def analyse_errors(out_sid, trace, n_frames):
    """Run py65 comparison and print per-register error counts."""
    from py65.devices.mpu6502 import MPU

    with open(out_sid, 'rb') as f:
        data = f.read()

    hdr_len   = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]

    code = data[hdr_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code

    mem = bytearray(65536)
    end = min(load_addr + len(binary), 65536)
    mem[load_addr:end] = binary[:end - load_addr]
    mem[0xFFF0] = 0x00

    mpu = MPU()
    mpu.memory = mem
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = 0
    for _ in range(200000):
        if mpu.memory[mpu.pc] == 0x00:
            break
        mpu.step()

    n = min(n_frames, trace.n_frames)
    ret_addr = 0xFFF0 - 1

    reg_names = []
    for vi in range(3):
        for r in ('FL', 'FH', 'PL', 'PH', 'CT', 'AD', 'SR'):
            reg_names.append(f'V{vi+1}_{r}')
    for ri in range(4):
        reg_names.append(f'FLT{ri}')

    err_counts = [0] * 25
    match_frames = 0
    first_mismatches = []

    for frame in range(n):
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr
        for _ in range(200000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()

        got = tuple(mpu.memory[0xD400 + i] for i in range(25))
        expected = tuple(trace.frames[frame])

        if got == expected:
            match_frames += 1
        else:
            diffs = [(i, expected[i], got[i]) for i in range(25) if got[i] != expected[i]]
            for i, _, _ in diffs:
                err_counts[i] += 1
            if len(first_mismatches) < 5:
                diff_str = ', '.join(
                    f'{reg_names[i]}={e:02X}->{g:02X}'
                    for i, e, g in diffs
                )
                first_mismatches.append(f'  frame {frame:4d}: {diff_str}')

    print(f'Match: {match_frames}/{n} frames ({100.0*match_frames/n:.1f}%)')
    if match_frames < n:
        print('First mismatches:')
        for m in first_mismatches:
            print(m)
        print('Error counts:')
        for i, cnt in enumerate(err_counts):
            if cnt > 0:
                print(f'  {reg_names[i]:12s}: {cnt:4d} errors ({100.0*cnt/n:.1f}%)')
    else:
        print('PERFECT MATCH — 0 errors across all 25 registers')

    plo_errs = err_counts[2] + err_counts[9] + err_counts[16]
    phi_errs = err_counts[3] + err_counts[10] + err_counts[17]
    if plo_errs + phi_errs > 0:
        print(f'PW errors:  V1_PL+V2_PL+V3_PL={plo_errs} ({100.0*plo_errs/n:.1f}%)'
              f'  V1_PH+V2_PH+V3_PH={phi_errs} ({100.0*phi_errs/n:.1f}%)')
    else:
        print('PW: 0 errors (exact match on all 3 voices)')

    return match_frames, n


# ---------------------------------------------------------------------------
# simple_codegen PW unit test
# ---------------------------------------------------------------------------

def test_simple_codegen_pw():
    """Verify simple_codegen PW synthesis on a synthetic song.

    Tests two modes:
      V1-style: bidirectional 16-bit sweep (speed=$00E0, min=$08, max=$0E, init=$0900)
      V3-style: linear 8-bit wrap (speed=$16, pw_hi=$01 fixed, pw_max=$FF)

    Expected behaviour (write-then-accumulate):
      Frame N: write stored PW → compute next → boundary check → store next PW
    """
    from py65.devices.mpu6502 import MPU
    from simple_codegen import simple_codegen
    from usf.format import (Song, Instrument, Pattern, NoteEvent,
                             WaveTableStep, PulseTableStep)

    print('\n--- simple_codegen PW unit test ---')

    song = Song()
    song.freq_lo = bytes([0x00, 0x18, 0x37, 0x51, 0x6E, 0x8E])
    song.freq_hi = bytes([0x00, 0x1D, 0x3A, 0x57, 0x74, 0x92])
    song.tempo = 1

    # Instrument 0: bidirectional sweep (V1-style)
    # speed=$00E0, pw_min_hi=$08, pw_max_hi=$0E, init=$0900
    # PulseTable encoding: is_set=False → speed; is_set=True → min/max
    inst0 = Instrument(id=0, ad=0x29, sr=0x5F, pulse_width=0x0900)
    inst0.wave_table = [
        WaveTableStep(waveform=0x41, note_offset=0),
        WaveTableStep(is_loop=True, loop_target=0),
    ]
    inst0.pulse_table = [
        PulseTableStep(is_set=False, value=0xE0, low_byte=0, duration=0),  # speed_lo=$E0
        PulseTableStep(is_set=True, value=0x08, low_byte=0x0E, duration=0),  # min=$08, max=$0E
    ]

    # Instrument 1: linear 8-bit wrap (V3-style)
    # speed_lo=$16, pw_hi=$01 fixed, pw_max=$FF → no flip
    inst1 = Instrument(id=1, ad=0x09, sr=0x9F, pulse_width=0x0180)
    inst1.wave_table = [
        WaveTableStep(waveform=0x41, note_offset=0),
        WaveTableStep(is_loop=True, loop_target=0),
    ]
    inst1.pulse_table = [
        PulseTableStep(is_set=False, value=0x16, low_byte=0, duration=0),
        # No is_set step → pw_min=$FF, pw_max=$FF (linear 8-bit wrap)
    ]

    # Instrument 2: no PW modulation
    inst2 = Instrument(id=2, ad=0x06, sr=0x4B, pulse_width=0x0800)
    inst2.wave_table = [
        WaveTableStep(waveform=0x41, note_offset=0),
        WaveTableStep(is_loop=True, loop_target=0),
    ]

    song.instruments = [inst0, inst1, inst2]

    for v in range(3):
        pat = Pattern(id=v)
        pat.events.append(NoteEvent(type='note', note=1, duration=50, instrument=v))
        song.patterns.append(pat)
        song.orderlists[v].append((v, 0))

    tmp_sid = '/tmp/test_simple_pw.sid'
    result = simple_codegen(song, tmp_sid)
    if not result:
        print('  FAILED: assembly error')
        return False

    with open(tmp_sid, 'rb') as f:
        data = f.read()

    hdr_len = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    code = data[hdr_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code

    mem = bytearray(65536)
    mem[load_addr:load_addr + len(binary)] = binary
    mem[0xFFF0] = 0x00
    mpu = MPU()
    mpu.memory = mem
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = 0
    for _ in range(200000):
        if mpu.memory[mpu.pc] == 0x00:
            break
        mpu.step()

    # Python simulation of expected PW values (write-then-accumulate)
    v1_pw = 0x0900   # init value
    v1_dir = 0       # 0=up, 1=down
    v1_speed = 0x00E0
    v1_min = 0x08    # min pw_hi
    v1_max = 0x0E    # max pw_hi

    v2_pw_lo = 0x80  # init pw_lo
    v2_pw_hi = 0x01  # init pw_hi (stays fixed)
    v2_speed = 0x16

    ret_addr = 0xFFF0 - 1
    errors = 0

    for frame in range(45):
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr
        for _ in range(200000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()

        got_v1_pl = mpu.memory[0xD402]
        got_v1_ph = mpu.memory[0xD403]
        got_v2_pl = mpu.memory[0xD409]
        got_v2_ph = mpu.memory[0xD40A]

        exp_v1_pl = v1_pw & 0xFF
        exp_v1_ph = (v1_pw >> 8) & 0x0F

        if got_v1_pl != exp_v1_pl or got_v1_ph != exp_v1_ph:
            print(f'  V1 frame {frame}: exp={exp_v1_ph:01X}{exp_v1_pl:02X} '
                  f'got={got_v1_ph:01X}{got_v1_pl:02X}  dir={v1_dir}')
            errors += 1
        if got_v2_pl != v2_pw_lo or got_v2_ph != v2_pw_hi:
            print(f'  V2 frame {frame}: exp={v2_pw_hi:02X}{v2_pw_lo:02X} '
                  f'got={got_v2_ph:02X}{got_v2_pl:02X}')
            errors += 1

        # Advance expected V1 PW (bidirectional 16-bit, boundary on pw_hi)
        if v1_dir == 0:  # up
            v1_pw = (v1_pw + v1_speed) & 0xFFFF
            if (v1_pw >> 8) >= v1_max:
                v1_pw = (v1_max << 8) | (v1_pw & 0xFF)
                v1_dir = 1
        else:            # down
            v1_pw = (v1_pw - v1_speed) & 0xFFFF
            new_hi = (v1_pw >> 8) & 0xFF
            if new_hi <= v1_min:
                v1_pw = (v1_min << 8) | (v1_pw & 0xFF)
                v1_dir = 0

        # Advance expected V2 PW (8-bit linear, pw_hi fixed at $01)
        v2_pw_lo = (v2_pw_lo + v2_speed) & 0xFF

    if errors == 0:
        print(f'  PASS: 45 frames, 0 PW errors (V1 bidirectional + V2 linear)')
    else:
        print(f'  FAIL: {errors} errors in 45 frames')
    return errors == 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', type=int, default=2000,
                        help='Frames to verify against ground truth (default 2000)')
    parser.add_argument('--test-simple', action='store_true',
                        help='Run simple_codegen PW unit test and exit')
    args = parser.parse_args()

    if args.test_simple:
        ok = test_simple_codegen_pw()
        return 0 if ok else 1

    import time
    t0 = time.time()
    print('=' * 60)
    print('Commando HolyScale Builder')
    print(f'  Verify: {args.verify} frames')
    print('=' * 60)

    os.makedirs(os.path.dirname(OUT_SID), exist_ok=True)

    # Step 1: Capture with loop detection
    print('\n[1] Capturing Commando ground truth (loop detection enabled)...')
    mem, init_addr, play_addr, load_addr, n_songs = load_sid(COMMANDO_SID)
    trace = capture_subtune(mem, init_addr, play_addr, 0,
                            n_frames=8000, detect_loop=True, progress=True)
    print(f'    Captured {trace.n_frames} frames'
          + (f', loop at frame {trace.loop_frame} (len {trace.loop_length})'
             if trace.loop_frame else ', no loop found'))

    # Step 2: Build USF Song
    print('\n[2] Building USF Song (holy_scale)...')
    song = holy_scale(trace, COMMANDO_SID)
    print(f'    tempo={song.tempo}, {len(song.instruments)} instruments, '
          f'{len(song.patterns)} patterns')

    # Step 3: Generate SID via holy_scale_codegen with patched loop detection.
    # The default min_loop_note=2 finds a spurious 32-note loop in Commando's
    # intro (the main melody repeats every 32 notes before the drum section).
    # Using min_loop_note=200 forces the detector to skip this early repeat.
    print(f'\n[3] Generating SID: {OUT_SID}')
    print(f'    (min_loop_note={MIN_LOOP_NOTE} to skip spurious 32-note intro repeat)')

    # Patch _detect_note_loop to require longer loops
    orig_detect = _hsc._detect_note_loop
    _hsc._detect_note_loop = (
        lambda segs, voff, trace, min_loop_note=2:
        orig_detect(segs, voff, trace, min_loop_note=MIN_LOOP_NOTE)
    )
    try:
        stats = _hsc.holy_scale_codegen(song, OUT_SID,
                                        orig_sid_path=COMMANDO_SID,
                                        trace=trace, progress=True)
    finally:
        _hsc._detect_note_loop = orig_detect

    sz = os.path.getsize(OUT_SID)
    print(f'\n    Player code: {stats["player_code_size"]} bytes')
    print(f'    Freq table:  {stats["n_freqs"]} entries')
    print(f'    Instruments: {stats["n_instruments"]} ({stats["inst_data_size"]} bytes)')
    print(f'    Binary:      {stats["bin_size"]} bytes')
    print(f'    SID:         {sz} bytes ({sz/1024:.1f} KB)')

    # Step 4: Verify frame-by-frame
    n_verify = min(args.verify, trace.n_frames)
    print(f'\n[4] Verifying {n_verify} frames (py65 frame-by-frame)...')
    match_count, total, mismatches = verify_against_trace(
        OUT_SID, trace, max_frames=n_verify, progress=True)
    pct = 100.0 * match_count / total if total else 0.0
    print(f'    Match: {match_count}/{total} frames ({pct:.1f}%)')

    # Step 5: Detailed per-register analysis
    print(f'\n[5] Per-register error analysis ({n_verify} frames):')
    analyse_errors(OUT_SID, trace, n_verify)

    elapsed = time.time() - t0
    print(f'\nDone in {elapsed:.1f}s')
    print(f'Output: {OUT_SID}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
