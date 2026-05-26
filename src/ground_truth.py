"""
ground_truth.py — Capture full ground truth register traces from any SID via py65.

Captures ALL subtunes for their full HVSC-specified duration.
Detects loop points by finding repeated register states.
Returns structured per-subtune traces ready for effect decomposition.

Usage:
    from ground_truth import capture_sid
    result = capture_sid('path/to/song.sid')
    for sub in result.subtunes:
        print(f"Subtune {sub.number}: {sub.n_frames} frames, loop at {sub.loop_frame}")
"""

import sys
import os
import struct
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'py65_lib'))
from py65.devices.mpu6502 import MPU


# SID register offsets per voice
VOICE_REGS = 7  # freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr
VOICE_OFFSETS = [0, 7, 14]
FILTER_OFFSET = 21  # $D415-$D418: fc_lo, fc_hi, res_route, vol_mode
N_VOICE_REGS = 21   # 3 voices × 7 registers
N_ALL_REGS = 25      # + 4 filter registers


def load_sid(sid_path):
    """Load a SID file, return (memory_image, init_addr, play_addr, load_addr, n_songs)."""
    with open(sid_path, 'rb') as f:
        data = f.read()

    magic = data[:4]
    if magic not in (b'PSID', b'RSID'):
        raise ValueError(f"Not a PSID/RSID file: {magic}")

    header_len = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    n_songs = struct.unpack('>H', data[14:16])[0]

    code = data[header_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', code[0:2])[0]
        binary = code[2:]
    else:
        binary = code

    mem = bytearray(65536)
    end = min(load_addr + len(binary), 65536)
    mem[load_addr:end] = binary[:end - load_addr]

    return mem, init_addr, play_addr, load_addr, n_songs


def get_durations(sid_path):
    """Get HVSC songlength durations for a SID file. Returns list of seconds per subtune."""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           '..', 'data', 'C64Music', 'DOCUMENTS', 'Songlengths.md5')
    if not os.path.exists(db_path):
        return None

    # Compute MD5
    with open(sid_path, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()

    # Search database (streaming — don't load entire 50MB file)
    with open(db_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('[') or line.startswith(';'):
                continue
            if '=' not in line:
                continue
            file_md5, durations_str = line.split('=', 1)
            if file_md5.strip().lower() == md5:
                durations = []
                for d in durations_str.strip().split():
                    # Parse m:ss or m:ss.mmm
                    if '.' in d:
                        time_part, ms_part = d.rsplit('.', 1)
                        frac = int(ms_part) / (10 ** len(ms_part))
                    else:
                        time_part = d
                        frac = 0.0
                    parts = time_part.split(':')
                    durations.append(int(parts[0]) * 60 + int(parts[1]) + frac)
                return durations
    return None


class SubtuneTrace:
    """Ground truth register trace for one subtune."""
    __slots__ = ['number', 'frames', 'n_frames', 'loop_frame', 'loop_length',
                 'duration_sec']

    def __init__(self, number):
        self.number = number
        self.frames = []       # list of 25-byte tuples (all SID registers)
        self.n_frames = 0
        self.loop_frame = None   # frame index where the loop body starts
        self.loop_length = None  # frames in one loop iteration
        self.duration_sec = 0.0

    def voice_stream(self, voice, register):
        """Extract a single register stream for a voice.

        voice: 0, 1, 2
        register: 'freq_lo', 'freq_hi', 'pw_lo', 'pw_hi', 'ctrl', 'ad', 'sr',
                  'freq' (16-bit), 'pw' (16-bit)
        """
        voff = voice * 7
        reg_map = {'freq_lo': 0, 'freq_hi': 1, 'pw_lo': 2, 'pw_hi': 3,
                   'ctrl': 4, 'ad': 5, 'sr': 6}

        if register == 'freq':
            return [(f[voff + 1] << 8) | f[voff] for f in self.frames]
        elif register == 'pw':
            return [(f[voff + 3] << 8) | f[voff + 2] for f in self.frames]
        elif register in reg_map:
            idx = voff + reg_map[register]
            return [f[idx] for f in self.frames]
        else:
            raise ValueError(f"Unknown register: {register}")

    def voice_frames(self, voice):
        """Extract all 7 registers for a voice as list of tuples."""
        voff = voice * 7
        return [tuple(f[voff:voff + 7]) for f in self.frames]

    def gate_segments(self, voice):
        """Segment into notes by gate-on transitions.

        Returns list of (start_frame, end_frame) tuples.
        """
        voff = voice * 7
        segments = []
        prev_gate = 0
        for i, f in enumerate(self.frames):
            gate = f[voff + 4] & 1
            if gate and not prev_gate:
                if segments:
                    segments[-1] = (segments[-1][0], i)
                segments.append((i, self.n_frames))
            prev_gate = gate
        return segments


class SIDTrace:
    """Complete ground truth trace for a SID file."""
    __slots__ = ['sid_path', 'subtunes', 'init_addr', 'play_addr', 'load_addr']

    def __init__(self, sid_path):
        self.sid_path = sid_path
        self.subtunes = []
        self.init_addr = 0
        self.play_addr = 0
        self.load_addr = 0


def capture_subtune(mem_template, init_addr, play_addr, subtune_num, n_frames,
                    detect_loop=True, progress=False):
    """Capture n_frames of ground truth for one subtune.

    Returns a SubtuneTrace with loop detection.
    """
    trace = SubtuneTrace(subtune_num)

    mpu = MPU()
    mpu.memory = bytearray(mem_template)  # fresh copy
    mpu.memory[0xFFF0] = 0x00  # BRK sentinel

    # Run init with subtune number in A
    mpu.stPush(0xFF)
    mpu.stPush(0xEF)
    mpu.pc = init_addr
    mpu.a = subtune_num  # 0-indexed subtune number
    for _ in range(100000):
        if mpu.memory[mpu.pc] == 0x00:
            break
        mpu.step()

    # Capture frames
    state_index = {}  # state_hash → (frame_index, musical_state)
    ret_addr = 0xFFF0 - 1
    # Only look for song-level loops after 50% of expected duration
    min_loop_start = n_frames // 2

    for frame in range(n_frames):
        mpu.stPush(ret_addr >> 8)
        mpu.stPush(ret_addr & 0xFF)
        mpu.pc = play_addr
        for _ in range(50000):
            if mpu.memory[mpu.pc] == 0x00:
                break
            mpu.step()

        regs = tuple(mpu.memory[0xD400 + i] for i in range(N_ALL_REGS))
        trace.frames.append(regs)

        # Build musical state (ignore PW accumulators)
        musical_state = tuple(
            regs[v * 7 + r]
            for v in range(3)
            for r in (0, 1, 4, 5, 6)  # freq_lo, freq_hi, ctrl, ad, sr
        )
        state_hash = hash(musical_state)

        # Record state for early frames (potential loop targets)
        if frame < min_loop_start:
            state_index[state_hash] = (frame, musical_state)

        # Only check for loops after min_loop_start
        if detect_loop and frame >= min_loop_start:
            if state_hash in state_index:
                candidate, candidate_state = state_index[state_hash]
                # Double-check hash collision
                if candidate_state != musical_state:
                    continue
                # Verify: check next 50 frames match
                loop_len = frame - candidate
                if loop_len > 20:  # ignore tiny loops
                    verified = True
                    verify_frames = min(50, n_frames - frame - 1,
                                       len(trace.frames) - candidate - 1)
                    for v in range(verify_frames):
                        # Need to run more frames to verify
                        mpu.stPush(ret_addr >> 8)
                        mpu.stPush(ret_addr & 0xFF)
                        mpu.pc = play_addr
                        for _ in range(50000):
                            if mpu.memory[mpu.pc] == 0x00:
                                break
                            mpu.step()
                        verify_musical = tuple(
                            mpu.memory[0xD400 + vc * 7 + r]
                            for vc in range(3)
                            for r in (0, 1, 4, 5, 6)
                        )
                        expected_musical = tuple(
                            trace.frames[candidate + 1 + v][vc * 7 + r]
                            for vc in range(3)
                            for r in (0, 1, 4, 5, 6)
                        )
                        if verify_musical != expected_musical:
                            verified = False
                            # Still need to add this frame
                            full_regs = tuple(mpu.memory[0xD400 + i] for i in range(N_ALL_REGS))
                            trace.frames.append(full_regs)
                            frame += 1
                            break

                    if verified:
                        trace.loop_frame = candidate
                        trace.loop_length = loop_len
                        trace.n_frames = frame + 1
                        if progress:
                            print(f"  Loop detected at frame {candidate}, length {loop_len} "
                                  f"({loop_len / 50:.1f}s)")
                        return trace

            state_index[state_hash] = (frame, musical_state)

        if progress and frame % 2000 == 0 and frame > 0:
            print(f"  ... {frame}/{n_frames} frames captured")

    trace.n_frames = len(trace.frames)
    return trace


def capture_sid(sid_path, subtunes=None, max_frames=None, detect_loop=True,
                progress=True):
    """Capture full ground truth for a SID file.

    Args:
        sid_path: path to .sid file
        subtunes: list of 1-indexed subtune numbers, or None for all
        max_frames: override max frames per subtune (default: from HVSC + 10%)
        detect_loop: attempt loop detection
        progress: print progress

    Returns: SIDTrace with all captured subtunes
    """
    mem, init_addr, play_addr, load_addr, n_songs = load_sid(sid_path)

    result = SIDTrace(sid_path)
    result.init_addr = init_addr
    result.play_addr = play_addr
    result.load_addr = load_addr

    # Get HVSC durations
    durations = get_durations(sid_path)

    # Determine which subtunes to capture
    if subtunes is None:
        subtunes = list(range(1, n_songs + 1))

    for sub_num in subtunes:
        if sub_num < 1 or sub_num > n_songs:
            continue

        # Determine frame count
        if max_frames:
            n_frames = max_frames
        elif durations and sub_num <= len(durations):
            dur = durations[sub_num - 1]
            n_frames = int(dur * 50 * 1.1)  # +10% margin for loop detection
        else:
            n_frames = 15000  # default: 5 minutes

        if progress:
            dur_str = f"{durations[sub_num - 1]:.1f}s" if durations and sub_num <= len(durations) else "unknown"
            print(f"Subtune {sub_num}/{n_songs}: {dur_str}, capturing {n_frames} frames...")

        trace = capture_subtune(mem, init_addr, play_addr, sub_num - 1, n_frames,
                                detect_loop=detect_loop, progress=progress)
        trace.duration_sec = durations[sub_num - 1] if durations and sub_num <= len(durations) else 0

        if progress:
            loop_str = f", loop at frame {trace.loop_frame} (len {trace.loop_length})" if trace.loop_frame else ", no loop found"
            print(f"  Captured {trace.n_frames} frames{loop_str}")

        result.subtunes.append(trace)

    return result


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 ground_truth.py <file.sid> [subtune]")
        sys.exit(1)

    sid_path = sys.argv[1]
    subtunes = [int(sys.argv[2])] if len(sys.argv) > 2 else None

    result = capture_sid(sid_path, subtunes=subtunes)

    for sub in result.subtunes:
        print(f"\nSubtune {sub.number + 1}:")
        print(f"  Frames: {sub.n_frames}")
        print(f"  Duration: {sub.duration_sec:.1f}s")
        if sub.loop_frame is not None:
            intro = sub.loop_frame
            loop = sub.loop_length
            print(f"  Intro: {intro} frames ({intro / 50:.1f}s)")
            print(f"  Loop: {loop} frames ({loop / 50:.1f}s)")
            print(f"  Total unique: {intro + loop} frames "
                  f"({(intro + loop) * 21 / 1024:.1f} KB raw)")
        for v in range(3):
            segs = sub.gate_segments(v)
            print(f"  Voice {v + 1}: {len(segs)} notes")
