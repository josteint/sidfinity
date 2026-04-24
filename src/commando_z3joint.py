"""
commando_z3joint.py — Build Commando SID using the Z3 joint effect solver.

Captures ground truth for Commando subtune 1 (1500 frames, all 3 voices),
decomposes each gate segment with z3_decompose_note, then synthesises a
register-replay SID from the recovered parameters.

Output: demo/hubbard/Commando_z3joint.sid
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools', 'z3_lib'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ground_truth import capture_sid, load_sid, capture_subtune
from z3_decompose import (
    decompose_voice_segment,
    build_sid_from_params,
    verify_params,
)

# ---------------------------------------------------------------------------

COMMANDO_SID = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'data', 'C64Music', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Commando.sid',
)
OUT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..', 'demo', 'hubbard', 'Commando_z3joint.sid',
)
MAX_FRAMES = 1500
SUBTUNE = 0          # 0-indexed (subtune 1)
N_VOICES = 3
TIMEOUT_MS = 20000   # Z3 solver timeout per segment


def main():
    print('=' * 70)
    print('Commando Z3 Joint Effect Solver')
    print('=' * 70)

    if not os.path.exists(COMMANDO_SID):
        print(f'ERROR: Commando.sid not found at {COMMANDO_SID}')
        return 1

    # ------------------------------------------------------------------ capture
    print(f'\nCapturing subtune {SUBTUNE + 1}, {MAX_FRAMES} frames...')
    mem, init_addr, play_addr, load_addr, n_songs = load_sid(COMMANDO_SID)
    trace = capture_subtune(mem, init_addr, play_addr,
                            subtune_num=SUBTUNE,
                            n_frames=MAX_FRAMES,
                            detect_loop=False,
                            progress=True)
    print(f'  Captured {trace.n_frames} frames')

    # ------------------------------------------------------------------ decompose
    all_params = []
    total_segs = 0
    total_exact = 0
    total_approx = 0
    total_unsat = 0

    total_freq_sum = 0.0
    total_pw_sum = 0.0
    total_ctrl_sum = 0.0
    verified_segs = 0

    for voice in range(N_VOICES):
        segs = trace.gate_segments(voice)
        print(f'\nVoice {voice}: {len(segs)} gate segments')

        for seg_start, seg_end in segs:
            seg_end = min(seg_end, trace.n_frames)
            dur = seg_end - seg_start
            if dur < 2:
                continue

            params = decompose_voice_segment(
                trace, voice=voice,
                start_frame=seg_start, end_frame=seg_end,
                timeout_ms=TIMEOUT_MS,
            )

            if params is None:
                continue

            total_segs += 1
            status = params.get('status', 'unsatisfiable')
            if status == 'exact':
                total_exact += 1
            elif status == 'approximate':
                total_approx += 1
            else:
                total_unsat += 1

            v = verify_params(params, trace, voice=voice)
            total_freq_sum += v['freq_match_pct']
            total_pw_sum += v['pw_match_pct']
            total_ctrl_sum += v['ctrl_match_pct']
            verified_segs += 1

            print(f'  V{voice} f{seg_start}-{seg_end} ({dur}fr) '
                  f'note={params["base_note"]} status={status} '
                  f'freq={v["freq_match_pct"]:.0f}% '
                  f'pw={v["pw_match_pct"]:.0f}% '
                  f'ctrl={v["ctrl_match_pct"]:.0f}%')

            # Always include segment — unsatisfiable ones get raw replay fallback
            all_params.append(params)

    # ------------------------------------------------------------------ summary
    print(f'\n--- Decomposition summary ---')
    print(f'  Segments: {total_segs}  exact={total_exact}  approx={total_approx}  unsat={total_unsat}')
    if verified_segs > 0:
        print(f'  Avg freq match:  {total_freq_sum / verified_segs:.1f}%')
        print(f'  Avg PW match:    {total_pw_sum / verified_segs:.1f}%')
        print(f'  Avg ctrl match:  {total_ctrl_sum / verified_segs:.1f}%')
        overall_pct = (total_freq_sum / verified_segs)
        print(f'  Overall (freq):  {overall_pct:.1f}%')

    # ------------------------------------------------------------------ build SID
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    print(f'\nBuilding SID: {OUT_PATH}')
    success = build_sid_from_params(all_params, COMMANDO_SID, OUT_PATH,
                                    ground_truth_trace=trace)

    if success:
        size = os.path.getsize(OUT_PATH)
        print(f'SUCCESS: {OUT_PATH}  ({size} bytes)')
        if verified_segs > 0:
            print(f'Match: {total_freq_sum / verified_segs:.1f}% (freq), '
                  f'{total_ctrl_sum / verified_segs:.1f}% (waveform)')
    else:
        print('FAILED to build SID')
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
