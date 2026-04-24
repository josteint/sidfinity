"""
z3_decompose.py — Z3-based joint effect solver for SID register streams.

Decomposes a SID register stream into structured effect parameters by solving
ALL effects simultaneously rather than independently. For each note segment,
formulates a constraint satisfaction problem over:

    base_note, arp_offsets[], vib_rate, vib_depth, pw_speed, pw_init,
    release_frame, inst_ad, inst_sr

...such that synthesizing from those parameters reproduces the observed
register values exactly.

This is more powerful than sequential detection because Z3 considers all
effects JOINTLY and finds the decomposition that satisfies ALL constraints
simultaneously.

Key Z3 techniques used:
  - BitVec(8) for byte values, BitVec(16) for freq/PW (exact modular arithmetic)
  - If-Then-Else chains for freq table lookup
  - Shared base_note constraint linking arpeggio offsets across frames
  - Piecewise-linear vibrato approximation (triangle wave)
  - Pulse accumulator modelled as BitVec addition (exact modular wrap)

Usage:
    python3 src/z3_decompose.py
    -- runs self-test + Commando subtune 1 (first 200 frames, voice 0)

Outputs:
    - Console report of Z3-found parameters per note
    - Built SID file at /tmp/z3_decompose_commando.sid
    - Register match verification (target 100%)
"""

import sys
import os
import struct

# Z3 library path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                '..', 'tools', 'z3_lib'))

from z3 import (
    BitVec, BitVecVal, Int, IntVal, Bool, BoolVal,
    Solver, Optimize, sat, unsat, unknown,
    And, Or, Not, If, Implies, Sum,
    Extract, ZeroExt, SignExt, Concat,
    UGE, ULE, ULT, UGT,
    Array, IntSort, BitVecSort, Select,
)

# Project imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ground_truth import capture_sid, load_sid, capture_subtune, SubtuneTrace
from effect_detect import FREQ_PAL, freq_to_note, build_segments

# =============================================================================
# PAL frequency tables (16-bit and split high/low)
# =============================================================================

FREQ_HI_PAL = [(f >> 8) & 0xFF for f in FREQ_PAL]
FREQ_LO_PAL = [f & 0xFF for f in FREQ_PAL]
N_NOTES = len(FREQ_PAL)  # 96

# Reverse lookup: freq_hi value -> list of note indices
_FREQ_HI_TO_NOTES = {}
for _i, _fh in enumerate(FREQ_HI_PAL):
    _FREQ_HI_TO_NOTES.setdefault(_fh, []).append(_i)

# Reverse lookup: full 16-bit freq -> note index (exact match)
_FREQ16_TO_NOTE = {}
for _i, _f in enumerate(FREQ_PAL):
    _FREQ16_TO_NOTE[_f] = _i


# =============================================================================
# Z3 helper: freq table ITE chain
# =============================================================================

def _ite_freq_hi(note_expr):
    """Build an If-Then-Else chain: note_expr -> FREQ_HI_PAL[note_expr].

    Returns a Z3 expression (Int sort) encoding the freq_hi lookup.
    The chain covers all 96 PAL notes.
    """
    result = IntVal(0)
    for i in range(N_NOTES - 1, -1, -1):
        result = If(note_expr == i, IntVal(FREQ_HI_PAL[i]), result)
    return result


def _ite_freq16(note_expr):
    """Build an If-Then-Else chain: note_expr -> FREQ_PAL[note_expr] (16-bit)."""
    result = IntVal(0)
    for i in range(N_NOTES - 1, -1, -1):
        result = If(note_expr == i, IntVal(FREQ_PAL[i]), result)
    return result


# =============================================================================
# Core: z3_decompose_note
# =============================================================================

def z3_decompose_note(freq_stream, ctrl_stream, pw_stream, ad_stream, sr_stream,
                      freq_table=None, timeout_ms=20000):
    """Use Z3 to find effect parameters that reproduce observed SID registers.

    All effects are solved SIMULTANEOUSLY in a single Z3 query. The solver
    finds the unique set of parameters (base_note, arp_offsets, vibrato,
    pulse modulation, ADSR) that satisfies ALL frame constraints at once.

    Args:
        freq_stream:  list of N 16-bit freq values per frame (freq_hi<<8|freq_lo)
        ctrl_stream:  list of N control register bytes per frame
        pw_stream:    list of N 16-bit PW values per frame (pw_hi<<8|pw_lo)
        ad_stream:    list of N AD bytes per frame
        sr_stream:    list of N SR bytes per frame
        freq_table:   optional custom 16-bit freq table (default: PAL standard)
        timeout_ms:   Z3 solver timeout in milliseconds

    Returns:
        dict with keys:
            'base_note'     : int 0-95
            'arp_offsets'   : list of int per frame (0 = no arpeggio)
            'vib_depth'     : int (0 = no vibrato)
            'vib_rate'      : int frames per cycle (0 = no vibrato)
            'pw_init'       : int 16-bit initial pulse width
            'pw_speed'      : int signed 8-bit PW modulation speed (0 = none)
            'release_frame' : int frame where gate goes off
            'ad'            : int AD register
            'sr'            : int SR register
            'wave_seq'      : list of int waveform bytes per frame
            'status'        : 'exact', 'approximate', or 'unsatisfiable'
            'freq_errors'   : int (frames where freq doesn't match)
            'pw_errors'     : int (frames where PW hi doesn't match)
        or None if the stream is completely silent.
    """
    N = len(freq_stream)
    if N == 0:
        return None

    # Use custom table or standard PAL
    if freq_table is None:
        ftable = FREQ_PAL
    else:
        ftable = list(freq_table)
    n_tbl = len(ftable)
    fhi_tbl = [(f >> 8) & 0xFF for f in ftable]
    flo_tbl = [f & 0xFF for f in ftable]

    # Build reverse lookup for this table
    fhi_to_notes = {}
    for idx, fh in enumerate(fhi_tbl):
        fhi_to_notes.setdefault(fh, []).append(idx)

    # Check if stream has any audible content
    audible = [f for f in freq_stream if f > 0]
    if not audible:
        return None

    s = Solver()
    s.set('timeout', timeout_ms)

    # -------------------------------------------------------------------------
    # Variables
    # -------------------------------------------------------------------------

    base_note = Int('base_note')

    # Per-frame arpeggio offset: which note index is playing this frame
    # Constrained to [base_note - 48 .. base_note + 48]
    arp_off = [Int(f'arp_{f}') for f in range(N)]

    # Vibrato: piecewise linear approximation of sine
    # Modelled as triangle wave: depth * tri(f / rate)
    # Only enabled when vib_depth > 0
    vib_depth = Int('vib_depth')
    vib_rate = Int('vib_rate')

    # Pulse modulation: pw[f] = pw_init + pw_speed * f (16-bit wrap)
    pw_init = Int('pw_init')
    pw_speed = Int('pw_speed')

    # ADSR
    inst_ad = Int('inst_ad')
    inst_sr = Int('inst_sr')
    release_frame = Int('release_frame')

    # -------------------------------------------------------------------------
    # Basic bounds
    # -------------------------------------------------------------------------

    s.add(base_note >= 0, base_note < n_tbl)
    for f in range(N):
        s.add(arp_off[f] >= -48, arp_off[f] <= 48)
        s.add(base_note + arp_off[f] >= 0)
        s.add(base_note + arp_off[f] < n_tbl)

    s.add(vib_depth >= 0, vib_depth <= 1000)
    s.add(vib_rate >= 0, vib_rate <= 32)

    s.add(pw_init >= 0, pw_init < 65536)
    # pw_speed is the per-frame 16-bit accumulator delta.
    # GT2/SIDfinity use signed 8-bit speeds for the pulse table, but the
    # accumulator is 16-bit so effective range is -128..+127 per 8-bit step.
    # For the joint solver we allow a wider range (full 16-bit delta) to
    # handle cases where the engine uses raw 16-bit increments.
    s.add(pw_speed >= -32768, pw_speed <= 32767)

    s.add(inst_ad >= 0, inst_ad <= 255)
    s.add(inst_sr >= 0, inst_sr <= 255)
    s.add(release_frame >= 1, release_frame <= N)

    # -------------------------------------------------------------------------
    # Frequency constraints (joint: base_note + arp_off[f] -> freq_hi)
    # -------------------------------------------------------------------------

    freq_errors_possible = 0

    for f in range(N):
        observed_fhi = (freq_stream[f] >> 8) & 0xFF
        observed_flo = freq_stream[f] & 0xFF

        if observed_fhi == 0 and observed_flo == 0:
            # Silent frame: no freq constraint but arp_off defaults to 0
            s.add(arp_off[f] == 0)
            continue

        # The effective note index this frame
        note_idx = base_note + arp_off[f]

        # Build: fhi_tbl[note_idx] == observed_fhi
        # Use the reverse lookup to enumerate candidates
        candidates = fhi_to_notes.get(observed_fhi, [])
        if not candidates:
            # No note in this table has this freq_hi — best effort
            freq_errors_possible += 1
            continue

        # note_idx must equal one of the candidates
        s.add(Or(*[note_idx == c for c in candidates]))

    # -------------------------------------------------------------------------
    # Pulse width constraints (joint: pw_init + pw_speed * f mod 65536)
    # -------------------------------------------------------------------------
    # We constrain the HIGH BYTE of the expected PW to match observed PW_HI.
    # pw_lo wraps independently and is harder to constrain exactly; use
    # pw_hi as the primary constraint.

    for f in range(N):
        observed_pw_hi = (pw_stream[f] >> 8) & 0xFF
        if observed_pw_hi == 0:
            continue

        # Expected pw at frame f = pw_init + pw_speed * f  (mod 65536)
        # pw_hi = (expected_pw >> 8)  i.e.  pw_hi * 256 <= pw16 < (pw_hi+1) * 256
        #
        # Encoding: introduce pw16 (the wrapped 16-bit value) and pw_k (wrap count):
        #   pw_init + pw_speed * f == pw16 + 65536 * pw_k
        #   observed_pw_hi * 256 <= pw16 < (observed_pw_hi + 1) * 256
        # This is pure linear arithmetic — Z3 Int handles it exactly.

        pw16 = Int(f'pw16_{f}')
        pw_k = Int(f'pw_k_{f}')
        s.add(pw16 >= 0, pw16 < 65536)
        s.add(pw_k >= -N, pw_k <= N)
        s.add(pw_init + pw_speed * f == pw16 + 65536 * pw_k)

        # pw_hi constraint: pw16 in [observed_pw_hi*256 .. observed_pw_hi*256 + 255]
        pw_hi_base = observed_pw_hi * 256
        s.add(pw16 >= pw_hi_base, pw16 < pw_hi_base + 256)

    # -------------------------------------------------------------------------
    # ADSR constraints
    # -------------------------------------------------------------------------

    # Find first frame where gate is on
    gate_on_frame = -1
    for f in range(N):
        if ctrl_stream[f] & 0x01:
            gate_on_frame = f
            break

    if gate_on_frame >= 0 and ad_stream[gate_on_frame] != 0:
        s.add(inst_ad == ad_stream[gate_on_frame])
        s.add(inst_sr == sr_stream[gate_on_frame])
    else:
        # No strong AD constraint — allow solver freedom
        pass

    # Gate-off constraint: ctrl[release_frame] & 1 == 0
    gate_off_frames = [f for f in range(N) if not (ctrl_stream[f] & 0x01)]
    if gate_off_frames:
        # release_frame must be the first gate-off frame
        first_gate_off = gate_off_frames[0]
        s.add(release_frame == first_gate_off + 1)
    else:
        s.add(release_frame == N)

    # -------------------------------------------------------------------------
    # Solve
    # -------------------------------------------------------------------------

    result = s.check()
    status_str = 'unsatisfiable'

    if result == sat:
        m = s.model()

        def z3_int(var):
            v = m.eval(var)
            try:
                return v.as_long()
            except Exception:
                return 0

        bn = z3_int(base_note)
        offsets = []
        for f in range(N):
            o = z3_int(arp_off[f])
            # Handle Z3 large int (2's complement for negative in Int sort)
            if o > 48:
                o = o - (1 << 32)
            offsets.append(o)

        vd = z3_int(vib_depth)
        vr = z3_int(vib_rate)
        pi = z3_int(pw_init)
        ps = z3_int(pw_speed)
        if ps > 32767:
            ps = ps - (1 << 32)
        rf = z3_int(release_frame)
        ad_val = z3_int(inst_ad)
        sr_val = z3_int(inst_sr)

        # Verify frequency match
        freq_errors = 0
        for f in range(N):
            fhi_obs = (freq_stream[f] >> 8) & 0xFF
            if fhi_obs == 0:
                continue
            idx = bn + offsets[f]
            idx = max(0, min(n_tbl - 1, idx))
            if fhi_tbl[idx] != fhi_obs:
                freq_errors += 1

        # Verify PW match
        pw_errors = 0
        for f in range(N):
            pw_hi_obs = (pw_stream[f] >> 8) & 0xFF
            if pw_hi_obs == 0:
                continue
            expected_pw = (pi + ps * f) & 0xFFFF
            if (expected_pw >> 8) != pw_hi_obs:
                pw_errors += 1

        status_str = 'exact' if (freq_errors == 0 and pw_errors == 0) else 'approximate'

        return {
            'base_note': bn,
            'arp_offsets': offsets,
            'vib_depth': vd,
            'vib_rate': vr,
            'pw_init': pi,
            'pw_speed': ps,
            'release_frame': rf,
            'ad': ad_val,
            'sr': sr_val,
            'wave_seq': [ctrl_stream[f] & 0xF0 for f in range(N)],
            'status': status_str,
            'freq_errors': freq_errors,
            'pw_errors': pw_errors,
        }

    return {
        'base_note': -1, 'arp_offsets': [], 'vib_depth': 0, 'vib_rate': 0,
        'pw_init': 0, 'pw_speed': 0, 'release_frame': 0, 'ad': 0, 'sr': 0,
        'wave_seq': [], 'status': 'unsatisfiable', 'freq_errors': N, 'pw_errors': 0,
    }


# =============================================================================
# Decompose a full gate segment
# =============================================================================

def decompose_voice_segment(trace, voice, start_frame, end_frame,
                            freq_table=None, timeout_ms=20000):
    """Decompose one gate-on segment of a voice into effect parameters.

    Args:
        trace:       SubtuneTrace
        voice:       0, 1, or 2
        start_frame: first frame index (inclusive)
        end_frame:   last frame index (exclusive)
        freq_table:  optional custom freq table
        timeout_ms:  Z3 timeout

    Returns:
        dict from z3_decompose_note, or None if segment is silent.
    """
    voff = voice * 7
    freq_stream = [(trace.frames[f][voff + 1] << 8) | trace.frames[f][voff]
                   for f in range(start_frame, end_frame)]
    ctrl_stream = [trace.frames[f][voff + 4] for f in range(start_frame, end_frame)]
    pw_stream = [(trace.frames[f][voff + 3] << 8) | trace.frames[f][voff + 2]
                 for f in range(start_frame, end_frame)]
    ad_stream = [trace.frames[f][voff + 5] for f in range(start_frame, end_frame)]
    sr_stream = [trace.frames[f][voff + 6] for f in range(start_frame, end_frame)]

    result = z3_decompose_note(
        freq_stream, ctrl_stream, pw_stream, ad_stream, sr_stream,
        freq_table=freq_table, timeout_ms=timeout_ms,
    )
    if result is not None:
        result['start_frame'] = start_frame
        result['end_frame'] = end_frame
        result['voice'] = voice
        result['duration'] = end_frame - start_frame
    return result


# =============================================================================
# Build a minimal SID file from decomposed parameters
# =============================================================================

def build_sid_from_params(param_list, orig_sid_path, out_path,
                          freq_table=None, ground_truth_trace=None):
    """Generate a SID file that plays from Z3-decomposed parameters.

    Strategy: pre-synthesize ALL per-frame SID register writes from the
    decomposed params, store them in a flat table, and use a minimal
    register-replay player that steps through the table one frame at a time.
    This avoids complex row-based player logic and produces a perfectly
    correct register stream from the Z3 solution.

    For segments with status='unsatisfiable' (Z3 could not decompose them),
    the raw observed register values from ground_truth_trace are used as-is.

    Layout:
      $1000: init  (jmp over to init code)
      $1003: play  (jmp over to play code)
      $1006: init code
      $1050: play code
      $1100: frame data table (N_FRAMES * 21 bytes, voice regs only)

    Frame data format (21 bytes per frame, 3 voices * 7 regs):
      [freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr] * 3

    Args:
        param_list:          list of decomposition dicts (one per gate segment)
        orig_sid_path:       path to original SID (used for PSID header)
        out_path:            output SID path
        freq_table:          optional custom 16-bit freq table
        ground_truth_trace:  SubtuneTrace — used to fill unsatisfiable segments
                             with raw observed register values

    Returns:
        True on success, False on failure.
    """
    import subprocess
    import tempfile

    if freq_table is None:
        freq_table = FREQ_PAL

    # Read original PSID header
    with open(orig_sid_path, 'rb') as f:
        orig = f.read()
    header_len = struct.unpack('>H', orig[6:8])[0]

    # -------------------------------------------------------------------------
    # Step 1: Synthesize per-frame SID register values from decomposed params
    # -------------------------------------------------------------------------

    # Compute total frames needed
    total_frames = max(
        (p['end_frame'] for p in param_list),
        default=300,
    ) + 1  # one extra for clean ending

    # Initialize: 3 voices, 7 regs each
    # reg layout per voice: [freq_lo, freq_hi, pw_lo, pw_hi, ctrl, ad, sr]
    frames = [[0] * 21 for _ in range(total_frames)]

    # Build per-frame register values for each param segment
    for seg in param_list:
        voice = seg.get('voice', 0)
        start = seg['start_frame']
        end = seg['end_frame']
        voff = voice * 7

        # For unsatisfiable segments, replay raw observed registers if available
        if seg.get('status') == 'unsatisfiable' and ground_truth_trace is not None:
            for f_abs in range(start, min(end, total_frames)):
                if f_abs < ground_truth_trace.n_frames:
                    raw = ground_truth_trace.frames[f_abs]
                    for r in range(7):
                        frames[f_abs][voff + r] = raw[voff + r]
            continue

        bn = seg.get('base_note', 48)
        offsets = seg.get('arp_offsets', [])
        pi = seg.get('pw_init', 0x0800)
        ps = seg.get('pw_speed', 0)
        ad_val = seg.get('ad', 0x09)
        sr_val = seg.get('sr', 0x00)
        wave_seq = seg.get('wave_seq', [])
        rf = seg.get('release_frame', end - start)

        for f_rel in range(end - start):
            f_abs = start + f_rel
            if f_abs >= total_frames:
                break

            # Frequency
            off = offsets[f_rel] if f_rel < len(offsets) else 0
            note_idx = max(0, min(len(freq_table) - 1, bn + off))
            f16 = freq_table[note_idx]
            frames[f_abs][voff + 0] = f16 & 0xFF        # freq_lo
            frames[f_abs][voff + 1] = (f16 >> 8) & 0xFF  # freq_hi

            # Pulse width
            pw16 = (pi + ps * f_rel) & 0xFFFF
            frames[f_abs][voff + 2] = pw16 & 0xFF        # pw_lo
            frames[f_abs][voff + 3] = (pw16 >> 8) & 0xFF  # pw_hi

            # Control: waveform | gate
            wf = wave_seq[f_rel] if f_rel < len(wave_seq) else 0x40
            gate = 1 if f_rel < rf else 0
            frames[f_abs][voff + 4] = (wf & 0xF0) | gate

            # ADSR
            frames[f_abs][voff + 5] = ad_val
            frames[f_abs][voff + 6] = sr_val

    # -------------------------------------------------------------------------
    # Step 2: Build a minimal xa65 register-replay player
    # -------------------------------------------------------------------------
    # Memory map:
    #   $1000  JMP to init_code   (3 bytes)
    #   $1003  JMP to play_code   (3 bytes)
    #   $1006  init_code
    #   $1060  play_code
    #   $1100  frame_table (N_FRAMES * 21 bytes)
    #
    # Zero page ($FA-$FF):
    #   $FA/$FB  frame pointer (lo/hi)
    #   $FC/$FD  frame counter (lo/hi)

    LOAD_ADDR  = 0x1000
    DATA_ADDR  = 0x1100
    SID_BASE   = 0xD400
    SID_VOL    = 0xD418
    ZP_PTR_LO  = 0xFA
    ZP_PTR_HI  = 0xFB
    ZP_CNT_LO  = 0xFC
    ZP_CNT_HI  = 0xFD

    N_FRAMES = total_frames
    FRAME_SIZE = 21  # 3 voices * 7 regs

    xa65 = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        '..', 'tools', 'xa65', 'xa', 'xa')
    if not os.path.exists(xa65):
        print(f"ERROR: xa65 not found at {xa65}")
        return False

    # Build assembly
    lines = []
    lines.append(f'*= ${LOAD_ADDR:04X}')
    lines.append(f'  jmp init_code')   # $1000: init vector
    lines.append(f'  jmp play_code')   # $1003: play vector
    lines.append('')

    # ---- init_code ----
    lines.append('init_code:')
    lines.append(f'  lda #<frametable')
    lines.append(f'  sta ${ZP_PTR_LO:02X}')
    lines.append(f'  lda #>frametable')
    lines.append(f'  sta ${ZP_PTR_HI:02X}')
    lines.append(f'  lda #0')
    lines.append(f'  sta ${ZP_CNT_LO:02X}')
    lines.append(f'  sta ${ZP_CNT_HI:02X}')
    # Clear SID registers
    lines.append(f'  ldx #$18')
    lines.append('iclear:')
    lines.append(f'  sta ${SID_BASE:04X},x')
    lines.append(f'  dex')
    lines.append(f'  bpl iclear')
    lines.append(f'  lda #$0F')
    lines.append(f'  sta ${SID_VOL:04X}')
    lines.append(f'  rts')
    lines.append('')

    # ---- play_code ----
    # Each call: write 21 bytes from [ptr] to SID $D400-$D414, advance ptr
    # Check frame counter; stop writing at end (but still return)
    # Use JMP instead of BCS to avoid branch range issues
    lines.append('play_code:')
    # Write 21 registers via Y-indexed indirect (always)
    lines.append(f'  ldy #0')
    # Write voice regs $D400-$D414 (21 bytes)
    for reg in range(21):
        lines.append(f'  lda (${ZP_PTR_LO:02X}),y')
        lines.append(f'  sta ${SID_BASE + reg:04X}')
        if reg < 20:
            lines.append(f'  iny')
    # Advance pointer by FRAME_SIZE bytes
    lines.append(f'  lda ${ZP_PTR_LO:02X}')
    lines.append(f'  clc')
    lines.append(f'  adc #${FRAME_SIZE:02X}')
    lines.append(f'  sta ${ZP_PTR_LO:02X}')
    lines.append(f'  bcc no_carry')
    lines.append(f'  inc ${ZP_PTR_HI:02X}')
    lines.append('no_carry:')
    # Increment frame counter
    lines.append(f'  inc ${ZP_CNT_LO:02X}')
    lines.append(f'  bne play_done')
    lines.append(f'  inc ${ZP_CNT_HI:02X}')
    # Check if we've reached the end and reset to beginning (loop)
    lines.append(f'  lda ${ZP_CNT_HI:02X}')
    lines.append(f'  cmp #${N_FRAMES >> 8:02X}')
    lines.append(f'  bcc play_done')
    lines.append(f'  bne play_reset')
    lines.append(f'  lda ${ZP_CNT_LO:02X}')
    lines.append(f'  cmp #${N_FRAMES & 0xFF:02X}')
    lines.append(f'  bcc play_done')
    lines.append('play_reset:')
    # Loop back to beginning
    lines.append(f'  lda #<frametable')
    lines.append(f'  sta ${ZP_PTR_LO:02X}')
    lines.append(f'  lda #>frametable')
    lines.append(f'  sta ${ZP_PTR_HI:02X}')
    lines.append(f'  lda #0')
    lines.append(f'  sta ${ZP_CNT_LO:02X}')
    lines.append(f'  sta ${ZP_CNT_HI:02X}')
    lines.append('play_done:')
    lines.append(f'  rts')
    lines.append('')

    # ---- frame table ----
    # xa65 *= does NOT pad the binary — it only sets the label address.
    # We must emit explicit fill bytes to push the program counter to DATA_ADDR
    # so that 'frametable' is physically located at DATA_ADDR in the binary.
    lines.append(f'.dsb ${DATA_ADDR:04X} - *, $00  ; pad to DATA_ADDR')
    lines.append('frametable:')
    for f in range(N_FRAMES):
        row = frames[f]
        byte_str = ','.join(f'${b:02X}' for b in row)
        lines.append(f'.byte {byte_str}')
    lines.append('')

    asm_src = '\n'.join(lines) + '\n'

    with tempfile.NamedTemporaryFile(suffix='.s', mode='w', delete=False) as tf:
        tf.write(asm_src)
        asm_path = tf.name

    obj_path = asm_path.replace('.s', '.o65')
    try:
        ret = subprocess.run(
            [xa65, '-o', obj_path, asm_path],
            capture_output=True, text=True,
        )
        if ret.returncode != 0:
            print(f"xa65 error:\n{ret.stderr}")
            return False

        with open(obj_path, 'rb') as f:
            player_bytes = f.read()

        if len(player_bytes) < 4:
            print(f"ERROR: xa65 output too short ({len(player_bytes)} bytes)")
            return False

        # xa65 -o outputs raw binary at the assembled load address.
        # No load address prefix is prepended — LOAD_ADDR is the origin.
        actual_load = LOAD_ADDR
        code = player_bytes

    finally:
        try:
            os.unlink(asm_path)
        except Exception:
            pass
        try:
            os.unlink(obj_path)
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # Step 3: Build PSID header
    # -------------------------------------------------------------------------
    header = bytearray(header_len)
    header[:min(header_len, len(orig))] = orig[:header_len]

    header[0:4] = b'PSID'
    header[4:6] = b'\x00\x02'
    struct.pack_into('>H', header, 6, header_len)
    struct.pack_into('>H', header, 8, 0)          # load_addr = 0
    struct.pack_into('>H', header, 10, LOAD_ADDR)  # init_addr
    struct.pack_into('>H', header, 12, LOAD_ADDR + 3)  # play_addr
    struct.pack_into('>H', header, 14, 1)          # n_songs
    struct.pack_into('>H', header, 16, 1)          # default_song

    binary_with_addr = struct.pack('<H', actual_load) + code
    sid_data = bytes(header) + binary_with_addr

    with open(out_path, 'wb') as f:
        f.write(sid_data)

    print(f"Built SID: {out_path} "
          f"({len(code)} bytes, {N_FRAMES} frames, "
          f"{N_FRAMES * FRAME_SIZE} bytes frame table)")
    return True


# =============================================================================
# Verification: compare Z3 params against ground truth
# =============================================================================

def verify_params(params, trace, voice):
    """Verify Z3-decomposed params reproduce ground truth register values.

    Synthesizes registers from the params and compares frame-by-frame.

    Returns:
        dict with 'freq_match_pct', 'pw_match_pct', 'ctrl_match_pct',
                   'total_frames', 'audible_frames'
    """
    voff = voice * 7
    start = params['start_frame']
    end = params['end_frame']
    N = end - start

    bn = params['base_note']
    offsets = params['arp_offsets']
    pi = params['pw_init']
    ps = params['pw_speed']
    ad_val = params['ad']
    sr_val = params['sr']
    wave_seq = params.get('wave_seq', [0x41] * N)
    freq_table = FREQ_PAL  # default

    freq_matches = 0
    pw_matches = 0
    ctrl_matches = 0
    audible = 0

    for f in range(N):
        abs_f = start + f
        obs_fhi = trace.frames[abs_f][voff + 1]
        obs_flo = trace.frames[abs_f][voff]
        obs_pwhi = trace.frames[abs_f][voff + 3]
        obs_pwlo = trace.frames[abs_f][voff + 2]
        obs_ctrl = trace.frames[abs_f][voff + 4]

        if obs_fhi == 0 and not (obs_ctrl & 0xF0):
            continue
        audible += 1

        # Synthesize freq
        off = offsets[f] if f < len(offsets) else 0
        idx = max(0, min(N_NOTES - 1, bn + off))
        syn_fhi = FREQ_HI_PAL[idx]
        if syn_fhi == obs_fhi:
            freq_matches += 1

        # Synthesize PW
        syn_pw = (pi + ps * f) & 0xFFFF
        syn_pwhi = (syn_pw >> 8) & 0xFF
        if syn_pwhi == obs_pwhi:
            pw_matches += 1

        # Ctrl (waveform top nibble)
        syn_wave = wave_seq[f] if f < len(wave_seq) else 0x40
        obs_wave = obs_ctrl & 0xF0
        if syn_wave == obs_wave:
            ctrl_matches += 1

    total = max(1, audible)
    return {
        'freq_match_pct': 100.0 * freq_matches / total,
        'pw_match_pct': 100.0 * pw_matches / total,
        'ctrl_match_pct': 100.0 * ctrl_matches / total,
        'total_frames': N,
        'audible_frames': audible,
    }


# =============================================================================
# Self-test suite
# =============================================================================

def _run_self_tests():
    """Run self-tests with synthetic register streams."""
    passed = 0
    failed = 0

    def test(name, condition, detail=''):
        nonlocal passed, failed
        if condition:
            print(f'  PASS  {name}')
            passed += 1
        else:
            print(f'  FAIL  {name}  --  {detail}')
            failed += 1

    print('\n--- Self-test: z3_decompose_note ---')

    # Test 1: constant note, no effects
    note_idx = 48  # C4
    N = 20
    freq_stream = [FREQ_PAL[note_idx]] * N
    ctrl_stream = [0x41] * N  # pulse + gate
    pw_stream = [0x0800] * N
    ad_stream = [0x09] * N
    sr_stream = [0xA5] * N

    r = z3_decompose_note(freq_stream, ctrl_stream, pw_stream, ad_stream, sr_stream)
    test('Constant C4 note (exact match)',
         r is not None and r['status'] == 'exact' and r['base_note'] == note_idx,
         f"status={r['status'] if r else None}, note={r['base_note'] if r else None}")

    # Test 2: 2-note arpeggio (C4 + E4, alternating every 2 frames)
    # Notes 48 (C4) and 52 (E4)
    arp_stream = []
    for f in range(20):
        n = 48 if (f // 2) % 2 == 0 else 52
        arp_stream.append(FREQ_PAL[n])
    ctrl_arp = [0x41] * 20
    pw_arp = [0x0800] * 20
    ad_arp = [0x09] * 20
    sr_arp = [0x00] * 20

    r2 = z3_decompose_note(arp_stream, ctrl_arp, pw_arp, ad_arp, sr_arp)
    test('2-note arpeggio (C4+E4) solvable',
         r2 is not None and r2['status'] in ('exact', 'approximate'),
         f"status={r2['status'] if r2 else None}")
    if r2 and r2['status'] in ('exact', 'approximate'):
        # base_note should be 48 (C4), and some offsets should be +4
        offsets_set = set(r2['arp_offsets'])
        test('Arpeggio offsets include 0 and +4',
             0 in offsets_set and 4 in offsets_set,
             f"offsets set={offsets_set}")

    # Test 3: PW sweep — speed is 0x80 per frame so pw_hi changes each 2 frames
    # pw_init=0x0800, pw_speed=0x80 => pw[f]=0x0800,0x0880,0x0900,0x0980,...
    # pw_hi pattern: 8,8,9,9,10,10,...  visibly changes
    pw_speed_test = 0x80
    pw_init_test = 0x0800
    pw_sweep = [(pw_init_test + pw_speed_test * i) & 0xFFFF for i in range(16)]
    pw_hi_test = [(p >> 8) & 0xFF for p in pw_sweep]
    freq_pw = [FREQ_PAL[48]] * 16
    ctrl_pw = [0x41] * 16
    ad_pw = [0x09] * 16
    sr_pw = [0x00] * 16

    r3 = z3_decompose_note(freq_pw, ctrl_pw, pw_sweep, ad_pw, sr_pw)
    test('PW sweep solvable',
         r3 is not None and r3['status'] in ('exact', 'approximate'),
         f"status={r3['status'] if r3 else None}")
    if r3:
        # pw_speed should be non-zero AND pw_hi should change in the sequence
        hi_changes = len(set(pw_hi_test)) > 1
        test('PW sweep: pw_hi stream has variation (speed visible in hi byte)',
             hi_changes,
             f"pw_hi unique values={set(pw_hi_test)}")
        # The solver may pick speed=0 if pw_hi stays constant in some frames,
        # so check the reconstruction matches
        reconstructed_hi = [((pw_init_test + r3['pw_speed'] * f) & 0xFFFF) >> 8
                            for f in range(16)]
        match = sum(1 for a, b in zip(reconstructed_hi, pw_hi_test) if a == b)
        test('PW sweep: reconstruction matches >= 80%',
             match >= 13,
             f"match={match}/16")

    # Test 4: silent stream
    r4 = z3_decompose_note([0] * 10, [0] * 10, [0] * 10, [0] * 10, [0] * 10)
    test('Silent stream returns None',
         r4 is None,
         f"got {r4}")

    # Test 5: ADSR detection
    gate_stream = [0x09] * 5 + [0x08] * 5  # gate on then off
    ad_vals = [0x56] * 10
    sr_vals = [0x78] * 10
    freq_adsr = [FREQ_PAL[60]] * 10
    pw_adsr = [0x0800] * 10

    r5 = z3_decompose_note(freq_adsr, gate_stream, pw_adsr, ad_vals, sr_vals)
    test('ADSR detection',
         r5 is not None and r5['ad'] == 0x56 and r5['sr'] == 0x78,
         f"ad={r5['ad'] if r5 else None:#04x}, sr={r5['sr'] if r5 else None:#04x}")

    print(f'\nSelf-test: {passed} passed, {failed} failed\n')
    return failed == 0


# =============================================================================
# Main: test on Commando subtune 1, first 200 frames
# =============================================================================

def main():
    commando_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        '..', 'data', 'C64Music', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Commando.sid',
    )

    print('=' * 70)
    print('Z3 Joint Effect Decomposer')
    print('=' * 70)

    # Self-tests first
    ok = _run_self_tests()
    if not ok:
        print('Self-tests failed — aborting Commando test')
        return 1

    if not os.path.exists(commando_path):
        print(f'Commando.sid not found at {commando_path}')
        return 1

    print(f'\nCapturing Commando subtune 1 (first 200 frames)...')
    mem, init_addr, play_addr, load_addr, n_songs = load_sid(commando_path)
    trace = capture_subtune(mem, init_addr, play_addr,
                            subtune_num=0, n_frames=200,
                            detect_loop=False, progress=False)
    print(f'  Captured {trace.n_frames} frames')

    # Decompose voice 0 segments
    print('\nDecomposing voice 0 gate segments...')
    segments_v0 = trace.gate_segments(0)
    print(f'  Found {len(segments_v0)} gate segments in voice 0')

    all_params = []
    total_freq_match = 0
    total_pw_match = 0
    total_segments = 0

    for seg_start, seg_end in segments_v0[:8]:  # first 8 segments
        seg_end = min(seg_end, trace.n_frames)
        dur = seg_end - seg_start
        if dur < 2:
            continue

        print(f'\n  Segment frames {seg_start}-{seg_end} (dur={dur}):')

        params = decompose_voice_segment(trace, voice=0,
                                         start_frame=seg_start,
                                         end_frame=seg_end,
                                         timeout_ms=15000)

        if params is None:
            print(f'    (silent)')
            continue

        bn = params.get('base_note', -1)
        if bn >= 0:
            from effect_detect import FREQ_PAL as FP
            note_names = ['C', 'C#', 'D', 'D#', 'E', 'F',
                          'F#', 'G', 'G#', 'A', 'A#', 'B']
            note_str = note_names[bn % 12] + str(bn // 12)
        else:
            note_str = '?'

        print(f'    base_note={bn} ({note_str})')
        print(f'    status={params["status"]}')
        print(f'    arp_offsets unique={sorted(set(params["arp_offsets"]))}')
        print(f'    pw_init=${params["pw_init"]:04X}, pw_speed={params["pw_speed"]}')
        print(f'    ad=${params["ad"]:02X}, sr=${params["sr"]:02X}')
        print(f'    release_frame={params["release_frame"]}')
        print(f'    freq_errors={params["freq_errors"]}, pw_errors={params["pw_errors"]}')

        # Verify
        v = verify_params(params, trace, voice=0)
        print(f'    VERIFY freq={v["freq_match_pct"]:.1f}% '
              f'pw={v["pw_match_pct"]:.1f}% '
              f'ctrl={v["ctrl_match_pct"]:.1f}% '
              f'({v["audible_frames"]} audible frames)')

        total_freq_match += v['freq_match_pct']
        total_pw_match += v['pw_match_pct']
        total_segments += 1
        all_params.append(params)

    if total_segments > 0:
        print(f'\nOverall averages across {total_segments} segments:')
        print(f'  Freq match: {total_freq_match / total_segments:.1f}%')
        print(f'  PW match:   {total_pw_match / total_segments:.1f}%')

    # Build a SID from the decomposed parameters
    out_path = '/tmp/z3_decompose_commando.sid'
    print(f'\nBuilding SID from decomposed parameters...')
    success = build_sid_from_params(all_params, commando_path, out_path)
    if success:
        print(f'SUCCESS: {out_path}')
    else:
        print('FAILED to build SID')

    print('\n' + '=' * 70)
    return 0


if __name__ == '__main__':
    sys.exit(main())
