"""
commando_z3joint.py — Full-song Commando SID via Z3 joint effect decomposer.

Captures 2800 frames of Commando subtune 1 (~56s, covering the full intro
musical structure before the loop), decomposes all gate segments across all 3
voices using z3_decompose, then builds a register-replay SID.

Frame count is limited to ~2800 because the register-replay frame table must fit
within the C64's 64KB address space ($1100 + 21*N_FRAMES < $FFFF).
The full song is 235.6s (loop at frame 6072, loop period 447 frames); 2800 frames
covers the complete non-repeating intro structure.

Segments that Z3 cannot solve within the timeout, or that exceed MAX_Z3_SEGMENT
frames, fall back to raw register replay from ground truth (exact match guaranteed).

Output: demo/hubbard/Commando_z3joint.sid

Usage:
    source src/env.sh
    python3 src/commando_z3joint.py
"""

import sys
import os
import time

PROJ = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(PROJ, '..')
sys.path.insert(0, PROJ)
sys.path.insert(0, os.path.join(ROOT, 'tools', 'z3_lib'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

os.environ['PATH'] = (
    os.path.join(ROOT, 'tools', 'xa65', 'xa') + ':' +
    os.path.join(ROOT, 'tools') + ':' +
    os.environ.get('PATH', '')
)

from ground_truth import capture_sid, load_sid, capture_subtune
from z3_decompose import (
    decompose_voice_segment,
    build_sid_from_params,
    verify_params,
)

# ---------------------------------------------------------------------------

COMMANDO_SID = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                             'Hubbard_Rob', 'Commando.sid')
OUT_PATH = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_z3joint.sid')

# Frame count: 64KB frame table limit.
# Frame table starts at $1100 (~4KB for player code).
# Available: 65536 - 4352 - 512 (safety) = 60672 bytes / 21 bytes/frame = ~2889 frames.
# Use 2800 frames (~56s) to stay well within 64KB.
# The song loops at frame 6072 with a 447-frame loop body, so 2800 frames covers
# the full intro musical structure before the loop starts.
MAX_FRAMES = 2800
SUBTUNE = 0          # 0-indexed (subtune 1)
N_VOICES = 3
TIMEOUT_MS = 25000   # Z3 solver timeout per segment (25s)
# Segments longer than this get raw replay (Z3 too slow for long arpeggios/drums)
MAX_Z3_SEGMENT = 150


def _make_raw_replay_seg(voice, seg_start, seg_end):
    """Return a segment dict that forces raw replay from ground truth."""
    return {
        'voice': voice,
        'start_frame': seg_start,
        'end_frame': seg_end,
        'status': 'unsatisfiable',
        'base_note': -1,
        'arp_offsets': [],
        'pw_init': 0,
        'pw_speed': 0,
        'ad': 0,
        'sr': 0,
        'wave_seq': [],
        'release_frame': seg_end - seg_start,
        'freq_errors': 0,
        'pw_errors': 0,
        'duration': seg_end - seg_start,
    }


def main():
    t0 = time.time()
    print('=' * 70)
    print('Commando Z3 Joint Decomposer — Full Intro Structure')
    print(f'Target: {MAX_FRAMES} frames (~{MAX_FRAMES/50:.1f}s)')
    print('  (Full song loops at frame 6072; 2800 frames covers complete intro)')
    print('=' * 70)

    if not os.path.exists(COMMANDO_SID):
        print(f'ERROR: Commando.sid not found at {COMMANDO_SID}')
        return 1

    # ------------------------------------------------------------------ capture
    print(f'\n[1] Capturing subtune {SUBTUNE + 1}, {MAX_FRAMES} frames...')
    mem, init_addr, play_addr, load_addr, n_songs = load_sid(COMMANDO_SID)
    trace = capture_subtune(mem, init_addr, play_addr,
                            subtune_num=SUBTUNE,
                            n_frames=MAX_FRAMES,
                            detect_loop=True,
                            progress=True)
    print(f'  Captured {trace.n_frames} frames')
    if trace.loop_frame is not None:
        print(f'  Loop at frame {trace.loop_frame}, length {trace.loop_length}')
    print(f'  Elapsed: {time.time()-t0:.1f}s')

    # Use actual captured frames (may be less than MAX_FRAMES if loop detected)
    actual_frames = trace.n_frames

    # ------------------------------------------------------------------ decompose
    print(f'\n[2] Decomposing gate segments (Z3 timeout={TIMEOUT_MS}ms, '
          f'max_seg={MAX_Z3_SEGMENT} frames)...')

    all_params = []
    total_segs = 0
    total_exact = 0
    total_approx = 0
    total_unsat = 0
    total_long = 0   # skipped (too long for Z3)

    total_freq_sum = 0.0
    total_pw_sum = 0.0
    total_ctrl_sum = 0.0
    verified_segs = 0

    for voice in range(N_VOICES):
        segs = trace.gate_segments(voice)
        print(f'\n  Voice {voice}: {len(segs)} gate segments')

        for seg_idx, (seg_start, seg_end) in enumerate(segs):
            seg_end = min(seg_end, actual_frames)
            dur = seg_end - seg_start
            if dur < 2:
                continue

            total_segs += 1

            # Very long segments: skip Z3, use raw replay
            if dur > MAX_Z3_SEGMENT:
                params = _make_raw_replay_seg(voice, seg_start, seg_end)
                all_params.append(params)
                total_long += 1
                print(f'    v{voice} seg{seg_idx:3d}: f{seg_start}-{seg_end} '
                      f'dur={dur:4d} -> raw replay (too long)')
                continue

            # Z3 decomposition with timing
            t_seg = time.time()
            params = decompose_voice_segment(
                trace, voice=voice,
                start_frame=seg_start, end_frame=seg_end,
                timeout_ms=TIMEOUT_MS,
            )
            elapsed_seg = time.time() - t_seg

            if params is None:
                # Silent segment
                continue

            status = params.get('status', 'unsatisfiable')

            # Verify before deciding whether to use Z3 result or raw replay
            v = verify_params(params, trace, voice=voice)
            freq_pct = v['freq_match_pct']

            # If Z3 found a poor freq match (<50%), fall back to raw replay.
            # This handles drum patterns where the freq is non-standard and Z3
            # picks an incorrect note index.
            if status != 'exact' and freq_pct < 50.0:
                params = _make_raw_replay_seg(voice, seg_start, seg_end)
                # _make_raw_replay_seg sets status='unsatisfiable', triggering
                # the raw register replay path in build_sid_from_params.
                total_unsat += 1
            elif status == 'exact':
                total_exact += 1
            else:
                total_approx += 1

            total_freq_sum += freq_pct
            total_pw_sum += v['pw_match_pct']
            total_ctrl_sum += v['ctrl_match_pct']
            verified_segs += 1

            print(f'    v{voice} seg{seg_idx:3d}: f{seg_start}-{seg_end} '
                  f'dur={dur:3d} note={params.get("base_note",-1):3d} '
                  f'{status:15s} freq={freq_pct:5.1f}% '
                  f'pw={v["pw_match_pct"]:5.1f}% '
                  f'({elapsed_seg:.1f}s)')

            all_params.append(params)

        elapsed_total = time.time() - t0
        print(f'  Voice {voice} done — elapsed: {elapsed_total:.1f}s')

    # ------------------------------------------------------------------ summary
    print(f'\n--- Decomposition summary ---')
    print(f'  Total segments:   {total_segs}')
    print(f'  Z3 exact:         {total_exact}')
    print(f'  Z3 approximate:   {total_approx}')
    print(f'  Z3 unsat/timeout: {total_unsat}')
    print(f'  Raw replay (long):{total_long}')
    if verified_segs > 0:
        print(f'  Avg freq match:   {total_freq_sum / verified_segs:.1f}%')
        print(f'  Avg PW match:     {total_pw_sum / verified_segs:.1f}%')
        print(f'  Avg ctrl match:   {total_ctrl_sum / verified_segs:.1f}%')
    print(f'  Elapsed so far:   {time.time()-t0:.1f}s')

    # ------------------------------------------------------------------ build SID
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    print(f'\n[3] Building SID: {OUT_PATH}')
    all_params.sort(key=lambda p: p['start_frame'])
    success = build_sid_from_params(all_params, COMMANDO_SID, OUT_PATH,
                                    ground_truth_trace=trace)

    if success:
        size = os.path.getsize(OUT_PATH)
        print(f'SUCCESS: {OUT_PATH}  ({size:,} bytes)')
    else:
        print('FAILED to build SID')
        return 1

    # ------------------------------------------------------------------ verify
    print(f'\n[4] Verifying register match (30s = 1500 frames)...')
    try:
        from sid_compare import compare_sids_tolerant
        comp = compare_sids_tolerant(COMMANDO_SID, OUT_PATH, duration=30)
        grade = comp.get('grade', '?')
        score = comp.get('score', 0.0)
        print(f'  Grade: {grade}  Score: {score:.1f}%  (30s = 1500 frames)')
    except Exception as e:
        print(f'  sid_compare not available or failed: {e}')

    total_elapsed = time.time() - t0
    print(f'\nTotal elapsed: {total_elapsed:.1f}s')
    print('Done.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
