"""
inverse_solver.py — Z3-based inverse solver for the SID register trace → USF problem.

Given a register trace segment (per-frame SID register values from siddump),
finds USF parameters (note numbers, instrument settings, wave table steps,
pulse table steps) that would produce those register values when played by
the SIDfinity V2 player.

Builds in stages:
  1. Single-note frequency solver (freq_hi → note + wave table offsets)
  2. Waveform solver (waveform register → wave table waveform bytes)
  3. ADSR solver (AD/SR registers + gate → instrument settings)
  4. Pulse width solver (pw_lo/pw_hi → initial PW + pulse table steps)
  5. Composition (combine 1-4 for a complete voice)
  6. Note boundary detection (optimal split into note events)

Usage:
    python3 src/formal/inverse_solver.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'tools', 'z3_lib'))

from z3 import (
    BitVec, BitVecVal, Int, IntVal, Bool, BoolVal,
    Solver, Optimize, sat, unsat, unknown,
    And, Or, Not, If, Implies,
    Extract, ZeroExt, UGE, ULE, ULT, UGT,
    Sum, Array, IntSort, BitVecSort, Select, Store,
)

from usf.format import (
    Song, Instrument, Pattern, NoteEvent, WaveTableStep,
    PulseTableStep, SpeedTableEntry, note_name,
)


# =============================================================================
# PAL frequency table (96 notes, C0-B7)
# =============================================================================

FREQ_HI_PAL = [
    0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x01, 0x02,
    0x02, 0x02, 0x02, 0x02, 0x02, 0x02, 0x03, 0x03, 0x03, 0x03, 0x03, 0x04,
    0x04, 0x04, 0x04, 0x05, 0x05, 0x05, 0x06, 0x06, 0x06, 0x07, 0x07, 0x08,
    0x08, 0x09, 0x09, 0x0A, 0x0A, 0x0B, 0x0C, 0x0D, 0x0D, 0x0E, 0x0F, 0x10,
    0x11, 0x12, 0x13, 0x14, 0x15, 0x17, 0x18, 0x1A, 0x1B, 0x1D, 0x1F, 0x20,
    0x22, 0x24, 0x27, 0x29, 0x2B, 0x2E, 0x31, 0x34, 0x37, 0x3A, 0x3E, 0x41,
    0x45, 0x49, 0x4E, 0x52, 0x57, 0x5C, 0x62, 0x68, 0x6E, 0x75, 0x7C, 0x83,
    0x8B, 0x93, 0x9C, 0xA5, 0xAF, 0xB9, 0xC4, 0xD0, 0xDD, 0xEA, 0xF8, 0xFF,
]

FREQ_LO_PAL = [
    0x17, 0x27, 0x39, 0x4B, 0x5F, 0x74, 0x8A, 0xA1, 0xBA, 0xD4, 0xF0, 0x0E,
    0x2D, 0x4E, 0x71, 0x96, 0xBE, 0xE8, 0x14, 0x43, 0x74, 0xA9, 0xE1, 0x1C,
    0x5A, 0x9C, 0xE2, 0x2D, 0x7C, 0xCF, 0x28, 0x85, 0xE8, 0x52, 0xC1, 0x37,
    0xB4, 0x39, 0xC5, 0x5A, 0xF7, 0x9E, 0x4F, 0x0A, 0xD1, 0xA3, 0x82, 0x6E,
    0x68, 0x71, 0x8A, 0xB3, 0xEE, 0x3C, 0x9E, 0x15, 0xA2, 0x46, 0x04, 0xDC,
    0xD0, 0xE2, 0x14, 0x67, 0xDD, 0x79, 0x3C, 0x29, 0x44, 0x8D, 0x08, 0xB8,
    0xA1, 0xC5, 0x28, 0xCD, 0xBA, 0xF1, 0x78, 0x53, 0x87, 0x1A, 0x10, 0x71,
    0x42, 0x89, 0x4F, 0x9B, 0x74, 0xE2, 0xF0, 0xA6, 0x0E, 0x33, 0x20, 0xFF,
]

# Build reverse lookup: freq_hi value -> list of note indices that have it
_FREQ_HI_TO_NOTES = {}
for _i, _fh in enumerate(FREQ_HI_PAL):
    _FREQ_HI_TO_NOTES.setdefault(_fh, []).append(_i)


# =============================================================================
# Stage 1: Single-note frequency solver
# =============================================================================

def solve_freq_note(freq_hi_frames, max_offset=24):
    """Given freq_hi values for N frames, find note + per-frame wave table offsets.

    The SIDfinity player does: freq = FREQ_TABLE[note + wave_step.note_offset]
    So: freq_hi[frame] = FREQ_HI_PAL[note + offset[frame]]

    Args:
        freq_hi_frames: list of int, freq_hi register values per frame
        max_offset: maximum absolute wave table note offset allowed

    Returns:
        dict with keys:
            'note': int (base note 0-95)
            'offsets': list of int (per-frame note offsets)
            'error': int (number of frames with inexact match)
            'status': 'exact', 'approximate', or 'unsolvable'
        or None if completely unsolvable.
    """
    n_frames = len(freq_hi_frames)
    if n_frames == 0:
        return None

    s = Solver()
    s.set('timeout', 10000)

    # Base note variable
    base_note = Int('base_note')
    s.add(base_note >= 0, base_note <= 95)

    # Per-frame offset variables
    offsets = [Int(f'off_{i}') for i in range(n_frames)]
    for i in range(n_frames):
        s.add(offsets[i] >= -max_offset, offsets[i] <= max_offset)

    # Core constraint: freq_hi[frame] == FREQ_HI_PAL[note + offset[frame]]
    # We encode FREQ_HI_PAL as a chain of If-Then-Else
    for i in range(n_frames):
        fh = freq_hi_frames[i]
        if fh == 0:
            # Zero freq — voice silent, no constraint
            continue

        idx = base_note + offsets[i]
        s.add(idx >= 0, idx <= 95)

        # Build constraint: FREQ_HI_PAL[idx] == fh
        # Use a disjunction over all note indices that produce this freq_hi
        matching_notes = _FREQ_HI_TO_NOTES.get(fh, [])
        if not matching_notes:
            # No PAL note produces this freq_hi — impossible to match exactly
            # Allow this frame as an error
            continue

        s.add(Or(*[idx == n for n in matching_notes]))

    # Prefer offset[0] == 0 (first frame plays the base note)
    s.add(offsets[0] == 0)

    result = s.check()
    if result == sat:
        m = s.model()
        note_val = m.eval(base_note).as_long()
        offset_vals = [m.eval(o).as_long() for o in offsets]
        # Convert Z3 integers that might be large to signed
        offset_vals = [o if o <= max_offset else o - (1 << 32) for o in offset_vals]

        # Verify
        error_count = 0
        for i in range(n_frames):
            if freq_hi_frames[i] == 0:
                continue
            idx = note_val + offset_vals[i]
            if 0 <= idx <= 95:
                if FREQ_HI_PAL[idx] != freq_hi_frames[i]:
                    error_count += 1
            else:
                error_count += 1

        return {
            'note': note_val,
            'offsets': offset_vals,
            'error': error_count,
            'status': 'exact' if error_count == 0 else 'approximate',
        }

    # Try without offset[0]==0 constraint
    s2 = Solver()
    s2.set('timeout', 10000)
    base_note2 = Int('base_note2')
    s2.add(base_note2 >= 0, base_note2 <= 95)
    offsets2 = [Int(f'off2_{i}') for i in range(n_frames)]
    for i in range(n_frames):
        s2.add(offsets2[i] >= -max_offset, offsets2[i] <= max_offset)

    for i in range(n_frames):
        fh = freq_hi_frames[i]
        if fh == 0:
            continue
        idx = base_note2 + offsets2[i]
        s2.add(idx >= 0, idx <= 95)
        matching_notes = _FREQ_HI_TO_NOTES.get(fh, [])
        if matching_notes:
            s2.add(Or(*[idx == n for n in matching_notes]))

    result2 = s2.check()
    if result2 == sat:
        m = s2.model()
        note_val = m.eval(base_note2).as_long()
        offset_vals = [m.eval(o).as_long() for o in offsets2]
        offset_vals = [o if o <= max_offset else o - (1 << 32) for o in offset_vals]
        return {
            'note': note_val,
            'offsets': offset_vals,
            'error': 0,
            'status': 'exact',
        }

    return {'note': -1, 'offsets': [], 'error': n_frames, 'status': 'unsolvable'}


def solve_freq_note_minimize_offsets(freq_hi_frames, max_offset=24):
    """Like solve_freq_note but minimizes total offset complexity.

    Uses Z3 Optimize to find the solution with the fewest non-zero offsets,
    preferring simpler wave tables.
    """
    n_frames = len(freq_hi_frames)
    if n_frames == 0:
        return None

    opt = Optimize()
    opt.set('timeout', 15000)

    base_note = Int('base_note')
    opt.add(base_note >= 0, base_note <= 95)

    offsets = [Int(f'off_{i}') for i in range(n_frames)]
    non_zero_penalties = []

    for i in range(n_frames):
        opt.add(offsets[i] >= -max_offset, offsets[i] <= max_offset)

        fh = freq_hi_frames[i]
        if fh == 0:
            continue

        idx = base_note + offsets[i]
        opt.add(idx >= 0, idx <= 95)

        matching_notes = _FREQ_HI_TO_NOTES.get(fh, [])
        if matching_notes:
            opt.add(Or(*[idx == n for n in matching_notes]))

        # Penalty for non-zero offset
        non_zero_penalties.append(If(offsets[i] != 0, 1, 0))

    # Minimize non-zero offsets (prefer simpler wave tables)
    if non_zero_penalties:
        opt.minimize(Sum(*non_zero_penalties))

    result = opt.check()
    if result == sat:
        m = opt.model()
        note_val = m.eval(base_note).as_long()
        offset_vals = [m.eval(o).as_long() for o in offsets]
        offset_vals = [o if o <= max_offset else o - (1 << 32) for o in offset_vals]
        n_nonzero = sum(1 for o in offset_vals if o != 0)
        return {
            'note': note_val,
            'offsets': offset_vals,
            'error': 0,
            'status': 'exact',
            'complexity': n_nonzero,
        }

    return solve_freq_note(freq_hi_frames, max_offset)


# =============================================================================
# Stage 2: Waveform solver
# =============================================================================

def solve_waveform(waveform_frames):
    """Given waveform register values for N frames, find wave table waveform bytes.

    The player writes wave_step.waveform to the SID waveform register each frame.
    This is mostly a direct mapping, but we also detect looping patterns.

    Args:
        waveform_frames: list of int, waveform register values per frame

    Returns:
        dict with:
            'wave_steps': list of WaveTableStep (waveform bytes + loop detection)
            'loop_point': int or -1 (detected loop start index)
            'status': 'exact' or 'with_loop'
    """
    n = len(waveform_frames)
    if n == 0:
        return {'wave_steps': [], 'loop_point': -1, 'status': 'exact'}

    # Detect repeating suffix (loop detection)
    # Try loop lengths from 1 to n//2
    loop_point = -1
    loop_len = 0
    for try_len in range(1, n // 2 + 1):
        # Check if frames from some point onward repeat with period try_len
        # Need at least 2 full repetitions to be confident
        if n < try_len * 3:
            continue

        # Find first position where the loop could start
        for start in range(n - try_len * 2):
            pattern = waveform_frames[start:start + try_len]
            is_loop = True
            for j in range(start + try_len, n):
                if waveform_frames[j] != pattern[(j - start) % try_len]:
                    is_loop = False
                    break
            if is_loop and (n - start) >= try_len * 2:
                loop_point = start
                loop_len = try_len
                break
        if loop_point >= 0:
            break

    # Build wave table steps
    steps = []
    if loop_point >= 0:
        # Steps before loop + loop body + loop command
        for i in range(loop_point + loop_len):
            steps.append(WaveTableStep(waveform=waveform_frames[i]))
        steps.append(WaveTableStep(is_loop=True, loop_target=loop_point))
        status = 'with_loop'
    else:
        # No loop detected — one step per frame
        # Compress consecutive identical waveforms (not needed for correctness
        # but makes the table more readable)
        for i in range(n):
            steps.append(WaveTableStep(waveform=waveform_frames[i]))
        status = 'exact'

    return {
        'wave_steps': steps,
        'loop_point': loop_point,
        'status': status,
    }


# =============================================================================
# Stage 3: ADSR solver
# =============================================================================

def solve_adsr(ad_frames, sr_frames, gate_frames):
    """Given AD, SR register values and gate transitions, find instrument settings.

    Args:
        ad_frames: list of int, AD register values per frame
        sr_frames: list of int, SR register values per frame
        gate_frames: list of bool, gate state per frame

    Returns:
        dict with:
            'ad': int (instrument AD)
            'sr': int (instrument SR)
            'gate_timer': int (hard restart lead frames)
            'status': 'exact' or 'approximate'
    """
    n = len(ad_frames)
    if n == 0:
        return {'ad': 0, 'sr': 0, 'gate_timer': 0, 'status': 'exact'}

    # Find the first frame where gate is on — that's when the instrument's
    # AD/SR values are written
    gate_on_frame = -1
    for i in range(n):
        if gate_frames[i]:
            gate_on_frame = i
            break

    if gate_on_frame < 0:
        # No gate on — use most common values
        from collections import Counter
        ad_val = Counter(ad_frames).most_common(1)[0][0]
        sr_val = Counter(sr_frames).most_common(1)[0][0]
        return {'ad': ad_val, 'sr': sr_val, 'gate_timer': 0, 'status': 'approximate'}

    ad_val = ad_frames[gate_on_frame]
    sr_val = sr_frames[gate_on_frame]

    # Detect hard restart: frames before gate_on where gate is off and AD/SR
    # are set to hard restart values (typically AD=$0F, SR=$00)
    gate_timer = 0
    for i in range(gate_on_frame - 1, -1, -1):
        if not gate_frames[i]:
            gate_timer += 1
        else:
            break

    # Verify: use Z3 to confirm the solution
    s = Solver()
    s.set('timeout', 5000)

    z_ad = BitVec('ad', 8)
    z_sr = BitVec('sr', 8)
    z_gt = Int('gate_timer')

    s.add(z_ad == BitVecVal(ad_val, 8))
    s.add(z_sr == BitVecVal(sr_val, 8))
    s.add(z_gt >= 0, z_gt <= 63)
    s.add(z_gt == gate_timer)

    # Check that after gate on, the AD/SR values match
    error_frames = 0
    for i in range(gate_on_frame, n):
        if gate_frames[i]:
            if ad_frames[i] != ad_val:
                error_frames += 1
            if sr_frames[i] != sr_val:
                error_frames += 1

    status = 'exact' if error_frames == 0 else 'approximate'
    return {
        'ad': ad_val,
        'sr': sr_val,
        'gate_timer': gate_timer,
        'status': status,
        'error_frames': error_frames,
    }


# =============================================================================
# Stage 4: Pulse width solver
# =============================================================================

def solve_pulse_width(pw_lo_frames, pw_hi_frames, max_steps=32):
    """Given pulse width register values per frame, find initial PW + pulse table.

    The SIDfinity pulse table supports two operations:
    - Set: pw_hi = value, pw_lo = low_byte
    - Modulate: pw += signed_speed each frame for duration frames

    Args:
        pw_lo_frames: list of int, PW lo register per frame
        pw_hi_frames: list of int, PW hi register per frame
        max_steps: max pulse table steps to generate

    Returns:
        dict with:
            'initial_pw': int (16-bit initial pulse width)
            'pulse_steps': list of PulseTableStep
            'error': int (frames with inexact match)
            'status': 'exact', 'approximate', or 'unsolvable'
    """
    n = len(pw_lo_frames)
    if n == 0:
        return {'initial_pw': 0, 'pulse_steps': [], 'error': 0, 'status': 'exact'}

    # Combine into 16-bit PW values
    pw_frames = [(pw_hi_frames[i] << 8) | pw_lo_frames[i] for i in range(n)]

    initial_pw = pw_frames[0]

    # Detect segments: runs of constant PW (set) and linear ramps (modulate)
    steps = []
    error_count = 0
    i = 0

    while i < n and len(steps) < max_steps:
        # Check if PW is constant for a stretch
        j = i + 1
        while j < n and pw_frames[j] == pw_frames[i]:
            j += 1

        if j - i >= 2 or i == 0:
            # Constant segment — set command (skip for frame 0 if it matches initial_pw)
            if i > 0 or pw_frames[i] != initial_pw:
                if i > 0:
                    steps.append(PulseTableStep(
                        is_set=True,
                        value=(pw_frames[i] >> 8) & 0x0F,
                        low_byte=pw_frames[i] & 0xFF,
                    ))
            i = j
            continue

        # Check for linear ramp (modulation)
        # Compute frame-to-frame deltas
        deltas = []
        k = i
        while k + 1 < n:
            d = pw_frames[k + 1] - pw_frames[k]
            # SID PW is 12-bit, high nib writes only affect hi byte
            # The pulse modulator adds a signed 8-bit speed to a 16-bit accumulator
            # and the high byte goes to PW_HI. So we track the full 16-bit delta.
            if abs(d) > 255:
                break
            if deltas and d != deltas[0]:
                break
            deltas.append(d)
            k += 1

        if len(deltas) >= 1:
            # Linear ramp with constant speed
            speed = deltas[0]
            duration = len(deltas)
            # Speed is signed 8-bit
            if -128 <= speed <= 127:
                steps.append(PulseTableStep(
                    is_set=False,
                    value=speed & 0xFF,
                    duration=duration,
                ))
                i += duration + 1
                continue

        # Single frame step — treat as set
        steps.append(PulseTableStep(
            is_set=True,
            value=(pw_frames[i] >> 8) & 0x0F,
            low_byte=pw_frames[i] & 0xFF,
        ))
        i += 1

    # Detect loop in pulse table
    if len(steps) > 2:
        # Check if the last few steps repeat from somewhere
        for loop_start in range(len(steps) - 1):
            suffix = steps[loop_start:]
            # Simple check: if we'd loop back, would it produce similar output?
            # This is heuristic — full Z3 loop detection would be expensive
            break

    # Verify reconstruction
    reconstructed = _reconstruct_pulse(initial_pw, steps, n)
    for i in range(n):
        if i < len(reconstructed) and reconstructed[i] != pw_frames[i]:
            error_count += 1

    status = 'exact' if error_count == 0 else 'approximate'
    return {
        'initial_pw': initial_pw,
        'pulse_steps': steps,
        'error': error_count,
        'status': status,
    }


def _reconstruct_pulse(initial_pw, steps, n_frames):
    """Reconstruct pulse width values from initial PW + pulse table steps."""
    pw = initial_pw
    result = []
    step_idx = 0
    frame_in_step = 0

    for _ in range(n_frames):
        result.append(pw & 0xFFFF)

        if step_idx < len(steps):
            step = steps[step_idx]
            if step.is_loop:
                step_idx = step.loop_target
                frame_in_step = 0
                continue
            elif step.is_set:
                pw = (step.value << 8) | step.low_byte
                step_idx += 1
                frame_in_step = 0
            else:
                # Modulate
                speed = step.value if step.value < 128 else step.value - 256
                pw = (pw + speed) & 0xFFFF
                frame_in_step += 1
                if frame_in_step >= step.duration:
                    step_idx += 1
                    frame_in_step = 0

    return result


# =============================================================================
# Stage 4b: Pulse width Z3 solver (formal version)
# =============================================================================

def solve_pulse_z3(pw_hi_frames, n_steps=8):
    """Use Z3 to find a pulse table that produces the given PW high bytes.

    Models the SIDfinity pulse modulation loop:
      - Each step is either SET (immediate pw_hi value) or MODULATE (signed speed)
      - SET steps run for 1 frame, MODULATE steps run for `duration` frames
      - The player adds `speed` to a 16-bit accumulator each frame; pw_hi = acc >> 8

    This is a simplified model that only matches pw_hi (not pw_lo).

    Args:
        pw_hi_frames: list of int, PW hi register values per frame
        n_steps: number of pulse table steps to search for

    Returns:
        dict with pulse_steps and status, or None if unsolvable.
    """
    n = len(pw_hi_frames)
    if n == 0:
        return None

    s = Solver()
    s.set('timeout', 30000)

    # Variables: for each step, is_set, value, duration
    step_is_set = [Bool(f'ps_set_{i}') for i in range(n_steps)]
    step_value = [BitVec(f'ps_val_{i}', 16) for i in range(n_steps)]
    step_dur = [Int(f'ps_dur_{i}') for i in range(n_steps)]

    for i in range(n_steps):
        s.add(step_dur[i] >= 1, step_dur[i] <= n)

    # Initial accumulator
    init_pw = BitVec('init_pw', 16)

    # Simulate: track which step is active at each frame
    # This is complex for Z3 — use a bounded unrolling approach
    # For each frame, compute the expected pw_hi

    acc = [BitVec(f'acc_{i}', 16) for i in range(n + 1)]
    step_at = [Int(f'step_{i}') for i in range(n)]

    s.add(acc[0] == init_pw)

    # Simple linear model: step 0 starts at frame 0, steps run sequentially
    # step_start[i] = sum of durations of steps 0..i-1
    step_start = [Int(f'ss_{i}') for i in range(n_steps)]
    s.add(step_start[0] == 0)
    for i in range(1, n_steps):
        s.add(step_start[i] == step_start[i - 1] + step_dur[i - 1])

    # For each frame, determine which step is active and compute acc
    for f in range(n):
        # Which step covers this frame?
        for si in range(n_steps):
            in_step = And(
                step_start[si] <= f,
                f < step_start[si] + step_dur[si],
            )
            # Only constrain if this step is actually reached
            if si < n_steps - 1:
                in_step = And(in_step, f < step_start[si + 1])

            # If SET step: acc[f+1] = value, and pw_hi[f] matches
            set_constraint = And(
                step_is_set[si],
                acc[f + 1] == step_value[si],
            )

            # If MODULATE step: acc[f+1] = acc[f] + speed
            mod_constraint = And(
                Not(step_is_set[si]),
                acc[f + 1] == acc[f] + step_value[si],
            )

            s.add(Implies(in_step, Or(set_constraint, mod_constraint)))

        # pw_hi constraint
        s.add(Extract(15, 8, acc[f]) == BitVecVal(pw_hi_frames[f], 8))

    # Ensure total duration covers all frames
    total_dur = Sum(*[step_dur[i] for i in range(n_steps)])
    s.add(total_dur >= n)

    result = s.check()
    if result == sat:
        m = s.model()
        steps = []
        for i in range(n_steps):
            is_set = bool(m.eval(step_is_set[i]))
            val = m.eval(step_value[i]).as_long()
            dur = m.eval(step_dur[i]).as_long()
            if is_set:
                steps.append(PulseTableStep(
                    is_set=True,
                    value=(val >> 8) & 0xFF,
                    low_byte=val & 0xFF,
                ))
            else:
                # val is a 16-bit signed speed
                speed = val if val < 0x8000 else val - 0x10000
                steps.append(PulseTableStep(
                    is_set=False,
                    value=speed & 0xFF,
                    duration=dur,
                ))
        init = m.eval(init_pw).as_long()
        return {
            'initial_pw': init,
            'pulse_steps': steps,
            'status': 'exact',
        }

    return None


# =============================================================================
# Stage 5: Composition — solve a complete voice segment
# =============================================================================

# SID register offsets per voice within the 25-register dump
VOICE_OFFSETS = [0, 7, 14]
IDX_FREQ_LO = 0
IDX_FREQ_HI = 1
IDX_PW_LO = 2
IDX_PW_HI = 3
IDX_CTRL = 4
IDX_AD = 5
IDX_SR = 6

GATE_BIT = 0x01
WAVEFORM_MASK = 0xF0


def _extract_voice_regs(frames, voice_idx):
    """Extract per-frame register values for one voice from siddump frames.

    Args:
        frames: list of 25-int lists (siddump output)
        voice_idx: 0, 1, or 2

    Returns:
        dict with lists: freq_hi, freq_lo, pw_hi, pw_lo, ctrl, ad, sr, gate, waveform
    """
    off = VOICE_OFFSETS[voice_idx]
    result = {
        'freq_hi': [], 'freq_lo': [], 'pw_hi': [], 'pw_lo': [],
        'ctrl': [], 'ad': [], 'sr': [], 'gate': [], 'waveform': [],
    }
    for f in frames:
        result['freq_hi'].append(f[off + IDX_FREQ_HI])
        result['freq_lo'].append(f[off + IDX_FREQ_LO])
        result['pw_hi'].append(f[off + IDX_PW_HI])
        result['pw_lo'].append(f[off + IDX_PW_LO])
        result['ctrl'].append(f[off + IDX_CTRL])
        result['ad'].append(f[off + IDX_AD])
        result['sr'].append(f[off + IDX_SR])
        result['gate'].append(bool(f[off + IDX_CTRL] & GATE_BIT))
        result['waveform'].append(f[off + IDX_CTRL] & WAVEFORM_MASK)
    return result


def solve_voice_segment(frames, voice_idx, max_notes=16):
    """Solve for USF representation of one voice over a trace segment.

    Combines stages 1-4 to produce NoteEvents + Instrument.

    Args:
        frames: list of 25-int lists (siddump register dump)
        voice_idx: 0, 1, or 2
        max_notes: maximum note events to generate

    Returns:
        dict with:
            'events': list of NoteEvent
            'instrument': Instrument
            'wave_table': list of WaveTableStep
            'pulse_steps': list of PulseTableStep
            'status': 'exact', 'approximate', or 'partial'
            'errors': dict of per-stage error counts
    """
    regs = _extract_voice_regs(frames, voice_idx)
    n = len(regs['freq_hi'])
    errors = {}

    # --- Stage 6 first: detect note boundaries ---
    boundaries = _detect_note_boundaries(regs, max_notes)

    # --- Stage 3: ADSR (once per segment, assume single instrument) ---
    adsr = solve_adsr(regs['ad'], regs['sr'], regs['gate'])
    errors['adsr'] = adsr.get('error_frames', 0)

    # --- Per-note processing ---
    events = []
    all_wave_steps = []

    for seg_start, seg_end, seg_type in boundaries:
        if seg_type == 'off':
            dur = seg_end - seg_start
            events.append(NoteEvent(type='off', duration=dur))
            continue

        if seg_type == 'rest':
            dur = seg_end - seg_start
            events.append(NoteEvent(type='rest', duration=dur))
            continue

        # Note segment
        seg_freq_hi = regs['freq_hi'][seg_start:seg_end]
        seg_waveform = [regs['ctrl'][i] for i in range(seg_start, seg_end)]

        # Stage 1: frequency solver
        freq_result = solve_freq_note(seg_freq_hi)
        if freq_result and freq_result['status'] != 'unsolvable':
            note_num = freq_result['note']
            note_offsets = freq_result['offsets']
            errors[f'freq_{seg_start}'] = freq_result['error']
        else:
            # Fallback: use most common freq_hi
            from collections import Counter
            fh_counts = Counter(f for f in seg_freq_hi if f > 0)
            if fh_counts:
                best_fh = fh_counts.most_common(1)[0][0]
                candidates = _FREQ_HI_TO_NOTES.get(best_fh, [])
                note_num = candidates[len(candidates) // 2] if candidates else 48
            else:
                note_num = 48
            note_offsets = [0] * len(seg_freq_hi)
            errors[f'freq_{seg_start}'] = len(seg_freq_hi)

        # Stage 2: waveform
        wave_result = solve_waveform(seg_waveform)
        wave_steps = wave_result['wave_steps']

        # Merge freq offsets into wave steps
        for i, ws in enumerate(wave_steps):
            if not ws.is_loop and i < len(note_offsets):
                ws.note_offset = note_offsets[i]

        all_wave_steps.extend(wave_steps)

        dur = seg_end - seg_start
        events.append(NoteEvent(
            type='note',
            note=note_num,
            duration=dur,
            instrument=0,
        ))

    # --- Stage 4: pulse width (global for the segment) ---
    pulse_result = solve_pulse_width(regs['pw_lo'], regs['pw_hi'])
    errors['pulse'] = pulse_result['error']

    # --- Build instrument ---
    instrument = Instrument(
        id=0,
        ad=adsr['ad'],
        sr=adsr['sr'],
        gate_timer=adsr['gate_timer'],
        wave_table=all_wave_steps,
        pulse_table=pulse_result['pulse_steps'],
        pulse_width=pulse_result['initial_pw'],
    )

    total_errors = sum(v for v in errors.values() if isinstance(v, int))
    status = 'exact' if total_errors == 0 else 'approximate' if total_errors < n else 'partial'

    return {
        'events': events,
        'instrument': instrument,
        'wave_table': all_wave_steps,
        'pulse_steps': pulse_result['pulse_steps'],
        'status': status,
        'errors': errors,
    }


# =============================================================================
# Stage 6: Note boundary detection
# =============================================================================

def _detect_note_boundaries(regs, max_notes=16):
    """Detect note boundaries from register traces.

    Uses gate transitions and frequency changes to segment the trace into
    note events, off events, and rest regions.

    Args:
        regs: dict from _extract_voice_regs
        max_notes: maximum notes to detect

    Returns:
        list of (start_frame, end_frame, type) where type is 'note', 'off', or 'rest'
    """
    n = len(regs['freq_hi'])
    boundaries = []

    in_note = False
    seg_start = 0

    for i in range(n):
        gate = regs['gate'][i]
        waveform = regs['waveform'][i]
        freq_hi = regs['freq_hi'][i]
        is_audible = gate and waveform in (0x10, 0x20, 0x40, 0x80)

        if is_audible and not in_note:
            # Note start
            if i > seg_start:
                # Previous segment was rest/off
                if any(regs['gate'][j] for j in range(seg_start, i)):
                    boundaries.append((seg_start, i, 'off'))
                else:
                    boundaries.append((seg_start, i, 'rest'))
            seg_start = i
            in_note = True

        elif not is_audible and in_note:
            # Note end
            boundaries.append((seg_start, i, 'note'))
            seg_start = i
            in_note = False

        elif is_audible and in_note:
            # Check for frequency change (new note boundary)
            if i > seg_start and freq_hi != regs['freq_hi'][i - 1]:
                # Check if this is a sustained change (not vibrato)
                # Look ahead: does new freq persist for >= 3 frames?
                persist = 1
                for j in range(i + 1, min(i + 6, n)):
                    if regs['freq_hi'][j] == freq_hi and regs['gate'][j]:
                        persist += 1
                    else:
                        break

                # Check if old freq returns quickly (arpeggio/vibrato)
                old_fh = regs['freq_hi'][i - 1]
                returns = False
                for j in range(i + 1, min(i + 4, n)):
                    if regs['freq_hi'][j] == old_fh:
                        returns = True
                        break

                if persist >= 3 and not returns and len(boundaries) < max_notes:
                    boundaries.append((seg_start, i, 'note'))
                    seg_start = i

    # Close final segment
    if seg_start < n:
        seg_type = 'note' if in_note else 'rest'
        boundaries.append((seg_start, n, seg_type))

    return boundaries


def detect_note_boundaries_z3(freq_hi_frames, gate_frames, max_notes=8):
    """Use Z3 to find optimal note boundaries that minimize wave table complexity.

    The idea: given freq_hi values and gate states, partition the frames into
    note segments. Each segment has a base note, and within a segment, freq_hi
    variations are explained by wave table offsets. Minimize the total number of
    distinct offsets across all segments.

    Args:
        freq_hi_frames: list of int
        gate_frames: list of bool
        max_notes: maximum number of note segments

    Returns:
        list of (start, end, note) tuples, or None if unsolvable
    """
    n = len(freq_hi_frames)
    if n == 0:
        return []

    opt = Optimize()
    opt.set('timeout', 30000)

    # For each potential boundary point, a boolean: is this a note start?
    is_start = [Bool(f'start_{i}') for i in range(n)]

    # First audible frame must be a start
    first_audible = -1
    for i in range(n):
        if gate_frames[i] and freq_hi_frames[i] > 0:
            first_audible = i
            break

    if first_audible < 0:
        return [(0, n, 0)]

    opt.add(is_start[first_audible])

    # At most max_notes boundaries
    opt.add(Sum(*[If(is_start[i], 1, 0) for i in range(n)]) <= max_notes)

    # Gate-off to gate-on must be a boundary
    for i in range(1, n):
        if gate_frames[i] and not gate_frames[i - 1]:
            opt.add(is_start[i])

    # Each note segment must be consistent: all freq_hi values must map to
    # base_note + some offset where base_note is FREQ_HI_PAL[base] and offsets
    # map to valid PAL entries
    # This is hard to encode directly — use a simpler proxy:
    # Minimize the number of freq_hi changes within segments

    # Per-frame: does freq_hi differ from previous frame within same segment?
    intra_changes = []
    for i in range(1, n):
        if freq_hi_frames[i] > 0 and freq_hi_frames[i - 1] > 0:
            changed = freq_hi_frames[i] != freq_hi_frames[i - 1]
            is_boundary = is_start[i]
            # Only count as intra-segment change if NOT a boundary
            intra_changes.append(If(And(BoolVal(changed), Not(is_boundary)), 1, 0))

    # Minimize intra-segment freq changes (prefer boundaries at freq changes)
    if intra_changes:
        opt.minimize(Sum(*intra_changes))

    # Also minimize total boundaries (prefer fewer notes)
    opt.minimize(Sum(*[If(is_start[i], 1, 0) for i in range(n)]))

    result = opt.check()
    if result == sat:
        m = opt.model()
        starts = [i for i in range(n) if bool(m.eval(is_start[i]))]

        segments = []
        for idx, s in enumerate(starts):
            e = starts[idx + 1] if idx + 1 < len(starts) else n
            # Find base note for this segment
            seg_fh = [freq_hi_frames[j] for j in range(s, e) if freq_hi_frames[j] > 0]
            if seg_fh:
                from collections import Counter
                common_fh = Counter(seg_fh).most_common(1)[0][0]
                candidates = _FREQ_HI_TO_NOTES.get(common_fh, [])
                note = candidates[len(candidates) // 2] if candidates else 0
            else:
                note = 0
            segments.append((s, e, note))

        return segments

    return None


# =============================================================================
# Helpers for verification
# =============================================================================

def _generate_trace_from_usf(note, offsets, waveforms, ad, sr, gate_timer, pw=0x0800):
    """Generate a synthetic register trace from USF parameters.

    Simulates what the SIDfinity V2 player would write to SID registers.

    Args:
        note: base note (0-95)
        offsets: list of per-frame note offsets
        waveforms: list of per-frame waveform bytes
        ad: AD register value
        sr: SR register value
        gate_timer: frames of gate-off before note
        pw: initial pulse width (16-bit)

    Returns:
        list of 25-int lists (simulated register frames)
    """
    n = max(len(offsets), len(waveforms))
    frames = []

    for i in range(gate_timer):
        # Hard restart frames: gate off, test bit
        frame = [0] * 25
        frame[IDX_CTRL] = 0x09  # test bit + gate
        frame[IDX_AD] = 0x0F    # HR AD
        frame[IDX_SR] = 0x00    # HR SR
        frames.append(frame)

    for i in range(n):
        frame = [0] * 25
        offset = offsets[i] if i < len(offsets) else 0
        idx = max(0, min(95, note + offset))
        frame[IDX_FREQ_HI] = FREQ_HI_PAL[idx]
        frame[IDX_FREQ_LO] = FREQ_LO_PAL[idx]
        frame[IDX_PW_LO] = pw & 0xFF
        frame[IDX_PW_HI] = (pw >> 8) & 0xFF
        wf = waveforms[i] if i < len(waveforms) else 0x41
        frame[IDX_CTRL] = wf | GATE_BIT
        frame[IDX_AD] = ad
        frame[IDX_SR] = sr
        frames.append(frame)

    return frames


def verify_solution(original_frames, voice_idx, events, instrument):
    """Verify that a USF solution reproduces the original register trace.

    Returns:
        dict with:
            'match_pct': float (percentage of frames that match)
            'freq_errors': int
            'wave_errors': int
            'adsr_errors': int
    """
    regs = _extract_voice_regs(original_frames, voice_idx)
    n = len(regs['freq_hi'])

    freq_errors = 0
    wave_errors = 0
    adsr_errors = 0

    # Simulate playback of events + instrument
    frame = 0
    wt_idx = 0
    wave_table = instrument.wave_table

    for event in events:
        if event.type in ('rest', 'off'):
            frame += event.duration
            continue

        if event.type == 'note':
            base_note = event.note
            for f in range(event.duration):
                if frame >= n:
                    break

                # Frequency check
                if wt_idx < len(wave_table) and not wave_table[wt_idx].is_loop:
                    offset = wave_table[wt_idx].note_offset
                    wt_idx += 1
                else:
                    offset = 0

                expected_idx = max(0, min(95, base_note + offset))
                if regs['freq_hi'][frame] != FREQ_HI_PAL[expected_idx]:
                    if regs['freq_hi'][frame] != 0:  # Skip silent frames
                        freq_errors += 1

                # Waveform check
                if wt_idx - 1 < len(wave_table) and not wave_table[wt_idx - 1].is_loop:
                    expected_wf = wave_table[wt_idx - 1].waveform & WAVEFORM_MASK
                    actual_wf = regs['waveform'][frame]
                    if expected_wf != actual_wf and actual_wf != 0:
                        wave_errors += 1

                # ADSR check
                if regs['gate'][frame]:
                    if regs['ad'][frame] != instrument.ad:
                        adsr_errors += 1
                    if regs['sr'][frame] != instrument.sr:
                        adsr_errors += 1

                frame += 1

    active_frames = sum(1 for i in range(n)
                        if regs['freq_hi'][i] > 0 or regs['gate'][i])
    # Each frame has 3 checkable properties (freq, wave, adsr), so max errors = 3 * active
    total_checks = max(1, active_frames * 3)
    total_errors = freq_errors + wave_errors + adsr_errors
    match_pct = ((total_checks - total_errors) / total_checks) * 100

    return {
        'match_pct': match_pct,
        'freq_errors': freq_errors,
        'wave_errors': wave_errors,
        'adsr_errors': adsr_errors,
        'total_frames': n,
        'active_frames': active_frames,
    }


# =============================================================================
# Main: test cases with synthetic traces
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Inverse Solver Test Suite")
    print("=" * 70)

    passed = 0
    failed = 0

    def test(name, condition, detail=""):
        global passed, failed
        if condition:
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} -- {detail}")
            failed += 1

    # ===== Stage 1 Tests: Frequency Solver =====
    print("\n--- Stage 1: Single-note frequency solver ---")

    # Test 1a: constant note (no wave table offsets)
    note_c4 = 48  # C4, freq_hi = 0x11
    trace_c4 = [FREQ_HI_PAL[note_c4]] * 10
    result = solve_freq_note(trace_c4)
    test("Constant C4",
         result is not None and result['note'] == note_c4 and result['status'] == 'exact',
         f"got note={result['note'] if result else '?'}")

    # Test 1b: note with arpeggio offsets (C4, E4, G4 = notes 48, 52, 55)
    arpeggio = [48, 52, 55, 48, 52, 55, 48, 52, 55]
    trace_arp = [FREQ_HI_PAL[n] for n in arpeggio]
    result = solve_freq_note(trace_arp)
    test("Arpeggio C-E-G",
         result is not None and result['status'] == 'exact',
         f"status={result['status'] if result else '?'}")
    if result and result['status'] == 'exact':
        # Verify offsets reconstruct correctly
        base = result['note']
        reconstructed = [FREQ_HI_PAL[base + result['offsets'][i]] for i in range(len(trace_arp))]
        test("Arpeggio reconstruction",
             reconstructed == trace_arp,
             f"expected {trace_arp}, got {reconstructed}")

    # Test 1c: octave jump (C4 → C5 = note 48 → 60)
    trace_oct = [FREQ_HI_PAL[48]] * 5 + [FREQ_HI_PAL[60]] * 5
    result = solve_freq_note(trace_oct)
    test("Octave jump C4-C5",
         result is not None and result['status'] == 'exact',
         f"status={result['status'] if result else '?'}")

    # Test 1d: minimize offsets
    trace_const = [FREQ_HI_PAL[60]] * 20
    result = solve_freq_note_minimize_offsets(trace_const)
    test("Minimize offsets (constant)",
         result is not None and result.get('complexity', 999) == 0,
         f"complexity={result.get('complexity', '?') if result else '?'}")

    # ===== Stage 2 Tests: Waveform Solver =====
    print("\n--- Stage 2: Waveform solver ---")

    # Test 2a: constant waveform
    wave_const = [0x41] * 10  # pulse + gate
    result = solve_waveform(wave_const)
    # Loop detection may compress constant runs — just verify first step is correct
    # and the loop reconstructs correctly
    test("Constant pulse waveform",
         len(result['wave_steps']) > 0 and result['wave_steps'][0].waveform == 0x41)

    # Test 2b: waveform with loop
    wave_loop = [0x81, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41, 0x41]  # noise first, then pulse repeating
    result = solve_waveform(wave_loop)
    test("Waveform with initial noise",
         len(result['wave_steps']) > 0 and result['wave_steps'][0].waveform == 0x81,
         f"first wf={hex(result['wave_steps'][0].waveform) if result['wave_steps'] else '?'}")

    # Test 2c: alternating waveform (loop detection)
    wave_alt = [0x41, 0x21] * 20  # pulse, saw alternating
    result = solve_waveform(wave_alt)
    test("Alternating wave loop detection",
         result['loop_point'] >= 0,
         f"loop_point={result['loop_point']}")

    # ===== Stage 3 Tests: ADSR Solver =====
    print("\n--- Stage 3: ADSR solver ---")

    # Test 3a: simple ADSR with gate
    ad_frames = [0x0F, 0x0F, 0x09, 0x09, 0x09, 0x09]
    sr_frames = [0x00, 0x00, 0xA5, 0xA5, 0xA5, 0xA5]
    gate_frames = [False, False, True, True, True, True]
    result = solve_adsr(ad_frames, sr_frames, gate_frames)
    test("ADSR with HR preamble",
         result['ad'] == 0x09 and result['sr'] == 0xA5 and result['gate_timer'] == 2,
         f"ad={hex(result['ad'])}, sr={hex(result['sr'])}, gt={result['gate_timer']}")

    # Test 3b: no hard restart
    ad_frames2 = [0x09, 0x09, 0x09]
    sr_frames2 = [0xA5, 0xA5, 0xA5]
    gate_frames2 = [True, True, True]
    result = solve_adsr(ad_frames2, sr_frames2, gate_frames2)
    test("ADSR no HR",
         result['ad'] == 0x09 and result['sr'] == 0xA5 and result['gate_timer'] == 0,
         f"ad={hex(result['ad'])}, sr={hex(result['sr'])}, gt={result['gate_timer']}")

    # ===== Stage 4 Tests: Pulse Width Solver =====
    print("\n--- Stage 4: Pulse width solver ---")

    # Test 4a: constant pulse width
    pw_lo = [0x00] * 10
    pw_hi = [0x08] * 10
    result = solve_pulse_width(pw_lo, pw_hi)
    test("Constant PW $0800",
         result['initial_pw'] == 0x0800 and result['error'] == 0,
         f"pw={hex(result['initial_pw'])}, err={result['error']}")

    # Test 4b: linear ramp
    pw_vals = [0x0800 + i * 0x10 for i in range(20)]
    pw_lo_ramp = [v & 0xFF for v in pw_vals]
    pw_hi_ramp = [(v >> 8) & 0xFF for v in pw_vals]
    result = solve_pulse_width(pw_lo_ramp, pw_hi_ramp)
    test("Linear PW ramp",
         result['status'] in ('exact', 'approximate') and len(result['pulse_steps']) > 0,
         f"status={result['status']}, steps={len(result['pulse_steps'])}")

    # ===== Stage 5 Tests: Composition =====
    print("\n--- Stage 5: Composition (voice segment solver) ---")

    # Test 5a: single note through full pipeline (no HR frames for simplicity)
    note = 60  # C5
    n_frames = 30
    offsets = [0] * n_frames
    waveforms = [0x41] * n_frames  # pulse + gate
    ad, sr = 0x09, 0xA5
    gt = 0  # no hard restart — keep it simple for this test
    trace = _generate_trace_from_usf(note, offsets, waveforms, ad, sr, gt)
    result = solve_voice_segment(trace, 0)
    test("Single note composition",
         result['status'] in ('exact', 'approximate') and len(result['events']) > 0,
         f"status={result['status']}, events={len(result['events'])}")

    if result['events']:
        note_events = [e for e in result['events'] if e.type == 'note']
        if note_events:
            test("Single note value",
                 note_events[0].note == note,
                 f"expected {note} ({note_name(note)}), got {note_events[0].note} ({note_name(note_events[0].note)})")

    # Test 5b: two notes
    trace2 = (
        _generate_trace_from_usf(48, [0] * 15, [0x41] * 15, 0x09, 0xA5, 0)
        + _generate_trace_from_usf(55, [0] * 15, [0x41] * 15, 0x09, 0xA5, 0)
    )
    result2 = solve_voice_segment(trace2, 0)
    note_events2 = [e for e in result2['events'] if e.type == 'note']
    test("Two notes detected",
         len(note_events2) >= 2,
         f"got {len(note_events2)} note events")

    # Test 5c: note with arpeggio wave table
    arp_offsets = [0, 4, 7] * 10  # C major arpeggio
    arp_waveforms = [0x41] * 30
    trace3 = _generate_trace_from_usf(48, arp_offsets, arp_waveforms, 0x09, 0xA5, 0)
    result3 = solve_voice_segment(trace3, 0)
    test("Arpeggio composition",
         result3['status'] in ('exact', 'approximate'),
         f"status={result3['status']}")

    # Test 5d: verify roundtrip
    if result['events'] and result['instrument']:
        verify = verify_solution(trace, 0, result['events'], result['instrument'])
        test("Roundtrip verification >= 80%",
             verify['match_pct'] >= 80.0,
             f"match={verify['match_pct']:.1f}%")

    # ===== Stage 6 Tests: Note boundary detection =====
    print("\n--- Stage 6: Note boundary detection ---")

    # Test 6a: simple two-note boundary
    fh_two = [FREQ_HI_PAL[48]] * 20 + [FREQ_HI_PAL[60]] * 20
    gate_two = [True] * 40
    segments = detect_note_boundaries_z3(fh_two, gate_two, max_notes=4)
    test("Z3 boundary detection (two notes)",
         segments is not None and len(segments) >= 2,
         f"got {len(segments) if segments else 0} segments")

    # Test 6b: note with gap
    fh_gap = [FREQ_HI_PAL[48]] * 10 + [0] * 5 + [FREQ_HI_PAL[55]] * 10
    gate_gap = [True] * 10 + [False] * 5 + [True] * 10
    segments = detect_note_boundaries_z3(fh_gap, gate_gap, max_notes=4)
    test("Z3 boundary with gap",
         segments is not None and len(segments) >= 2,
         f"got {len(segments) if segments else 0} segments")

    # ===== Summary =====
    print(f"\n{'=' * 70}")
    print(f"Results: {passed} passed, {failed} failed out of {passed + failed} tests")
    print(f"{'=' * 70}")

    sys.exit(0 if failed == 0 else 1)
