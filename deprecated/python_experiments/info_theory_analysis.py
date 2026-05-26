#!/usr/bin/env python3
"""
info_theory_analysis.py — Information theory analysis of SID compression.

Computes:
1. Shannon entropy H(trace) of register traces (bits/frame)
2. Entropy H(USF) of the USF symbolic representation
3. Mutual information I(USF; trace)
4. Conditional entropy H(trace | USF)
5. Theoretical minimum file sizes for lossless trace reproduction

Run as: python3 src/info_theory_analysis.py
"""

import sys
import os
import subprocess
import json
import math
import struct
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, '/home/jtr/sidfinity/src')

# --- Environment ---
SIDFINITY_ROOT = '/home/jtr/sidfinity'
SIDDUMP = f'{SIDFINITY_ROOT}/tools/siddump'
env = os.environ.copy()
env['PATH'] = f"{SIDFINITY_ROOT}/tools:{SIDFINITY_ROOT}/.pylocal/bin:{SIDFINITY_ROOT}/tools/xa65/xa:{SIDFINITY_ROOT}/local/bin:" + env.get('PATH', '')
env['LD_LIBRARY_PATH'] = f"{SIDFINITY_ROOT}/local/lib:" + env.get('LD_LIBRARY_PATH', '')
env['PYTHONPATH'] = f"{SIDFINITY_ROOT}/.pylocal/lib/python3.12/site-packages:{SIDFINITY_ROOT}/src:" + env.get('PYTHONPATH', '')


# =========================================================================
# Siddump helpers
# =========================================================================

def get_register_trace(sid_path, n_frames=200):
    """Run siddump on a SID file and return list of frame register dicts."""
    result = subprocess.run(
        [SIDDUMP, sid_path],
        capture_output=True, text=True, env=env
    )
    lines = result.stdout.strip().split('\n')
    if len(lines) < 2:
        raise RuntimeError(f"siddump failed for {sid_path}: {result.stderr[:200]}")

    # First line is JSON metadata
    meta = json.loads(lines[0])
    # Second line is CSV header
    headers = lines[1].split(',')
    frames = []
    for line in lines[2:2 + n_frames]:
        if not line.strip():
            continue
        vals = [int(x, 16) for x in line.split(',')]
        frames.append(dict(zip(headers, vals)))

    return meta, headers, frames


# =========================================================================
# Entropy computation
# =========================================================================

def shannon_entropy(counter):
    """H(X) in bits, from a Counter."""
    total = sum(counter.values())
    if total == 0:
        return 0.0
    h = 0.0
    for count in counter.values():
        p = count / total
        if p > 0:
            h -= p * math.log2(p)
    return h


def joint_entropy(pairs):
    """H(X,Y) from an iterable of (x,y) pairs."""
    counter = Counter(pairs)
    return shannon_entropy(counter)


def conditional_entropy_from_joints(joint_counter, marginal_counter):
    """H(Y|X) = H(X,Y) - H(X)."""
    total = sum(joint_counter.values())
    h = 0.0
    for (x, y), cnt in joint_counter.items():
        p_xy = cnt / total
        p_x = marginal_counter[x] / total
        if p_xy > 0 and p_x > 0:
            h -= p_xy * math.log2(p_xy / p_x)
    return h


def analyze_trace_entropy(frames, headers):
    """
    Compute per-register and joint-frame entropy of a register trace.

    Returns a dict with:
      - per_register: {name: H_bits_per_frame}
      - joint_frame: H(frame) as a whole
      - joint_consecutive: H(frame_t | frame_{t-1}) — first-order Markov entropy
      - delta_joint: H(delta_frame) — entropy of frame-to-frame deltas
    """
    n_regs = len(headers)
    n_frames = len(frames)

    # Per-register entropy
    per_reg = {}
    for h in headers:
        vals = [f[h] for f in frames]
        per_reg[h] = shannon_entropy(Counter(vals))

    # Joint entropy of a full frame (treat tuple of all 25 regs as one symbol)
    frame_tuples = [tuple(f[h] for h in headers) for f in frames]
    joint_frame_entropy = shannon_entropy(Counter(frame_tuples))

    # First-order Markov: H(frame_t | frame_{t-1})
    pairs = list(zip(frame_tuples[:-1], frame_tuples[1:]))
    pair_counter = Counter(pairs)
    prev_counter = Counter(frame_tuples[:-1])
    markov_entropy = conditional_entropy_from_joints(pair_counter, prev_counter)

    # Delta entropy: encode as differences
    def frame_delta(f1, f2):
        return tuple((b - a) & 0xFF for a, b in zip(f1, f2))

    deltas = [frame_delta(frame_tuples[i], frame_tuples[i+1])
              for i in range(len(frame_tuples)-1)]
    delta_entropy = shannon_entropy(Counter(deltas))

    # Sum of independent per-register entropies (upper bound ignoring correlations)
    sum_independent = sum(per_reg.values())

    return {
        'n_frames': n_frames,
        'n_regs': n_regs,
        'per_register': per_reg,
        'sum_independent': sum_independent,
        'joint_frame': joint_frame_entropy,
        'markov_frame': markov_entropy,
        'delta_joint': delta_entropy,
    }


# =========================================================================
# USF entropy — analyse the symbolic representation
# =========================================================================

def analyze_usf_file(sid_path):
    """
    Load USF via rh_to_usf and compute entropy of its symbolic tokens.
    Returns dict with size estimates and token entropies.
    """
    from converters.rh_to_usf import rh_to_usf
    try:
        song = rh_to_usf(sid_path)
    except Exception as e:
        return {'error': str(e)}

    # Flatten USF into tokens — each field is one token
    tokens = []

    # Freq table (192 bytes of uint16 pairs, 96 entries × 2 bytes each)
    for entry in getattr(song, 'freq_table', []):
        if isinstance(entry, (list, tuple)) and len(entry) == 2:
            tokens.append(('freq_lo', entry[0]))
            tokens.append(('freq_hi', entry[1]))
        else:
            tokens.append(('freq', entry))

    # Instruments
    for inst_id, inst in enumerate(getattr(song, 'instruments', [])):
        for step_i, step in enumerate(getattr(inst, 'wave_table', [])):
            tokens.append(('wave_wf', getattr(step, 'waveform', 0)))
            tokens.append(('wave_note_off', getattr(step, 'note_offset', 0)))
            tokens.append(('wave_delay', getattr(step, 'delay', 0)))
        for step in getattr(inst, 'pulse_table', []):
            tokens.append(('pulse_val', getattr(step, 'pulse', 0)))
        for step in getattr(inst, 'speed_table', []):
            tokens.append(('speed_val', getattr(step, 'speed', 0)))
        tokens.append(('inst_ad', getattr(inst, 'attack_decay', 0)))
        tokens.append(('inst_sr', getattr(inst, 'sustain_release', 0)))

    # Patterns / score
    for pat in getattr(song, 'patterns', []):
        for event in getattr(pat, 'events', []):
            tokens.append(('note', getattr(event, 'note', 0)))
            tokens.append(('inst', getattr(event, 'instrument', 0)))
            tokens.append(('dur', getattr(event, 'duration', 0)))

    # Token entropy
    token_counter = Counter(t[1] for t in tokens)  # value only
    type_counter = Counter(t[0] for t in tokens)   # type only
    joint_counter = Counter(tokens)                  # (type, value)

    h_token_val = shannon_entropy(token_counter)
    h_token_joint = shannon_entropy(joint_counter)

    # Total bits needed to encode all tokens (entropy coding lower bound)
    total_bits_lower = h_token_joint * len(tokens) if tokens else 0

    return {
        'n_tokens': len(tokens),
        'n_unique_tokens': len(joint_counter),
        'h_token_bits': h_token_joint,          # bits per token
        'h_value_bits': h_token_val,            # bits per value (ignoring type)
        'total_bits_lower_bound': total_bits_lower,
        'total_bytes_lower_bound': total_bits_lower / 8,
        'token_types': dict(type_counter),
    }


# =========================================================================
# File-level analysis
# =========================================================================

def analyze_sid_file_bytes(sid_path):
    """Byte-level entropy of the SID file itself."""
    data = Path(sid_path).read_bytes()
    # Skip PSID header (0x76 bytes typically)
    header_size = struct.unpack('>H', data[6:8])[0] if len(data) > 8 else 0x76
    music_data = data[header_size:]
    counter = Counter(music_data)
    h = shannon_entropy(counter)
    return {
        'file_size': len(data),
        'header_size': header_size,
        'music_data_size': len(music_data),
        'byte_entropy': h,
        'compressed_lower_bound': h * len(music_data) / 8,
        'unique_bytes': len(counter),
    }


# =========================================================================
# Mutual information: I(USF; trace) = H(trace) - H(trace|USF)
# =========================================================================

def compute_mutual_information(orig_frames, das_frames, headers):
    """
    Compute mutual information between original and Das Model traces.

    I(USF; trace) ≈ H(trace) - H(trace | USF_trace)

    We proxy H(trace | USF_trace) as:
    H(orig_frame | das_frame) — the uncertainty in the original given the Das Model.

    The two traces must be the same length.
    """
    n = min(len(orig_frames), len(das_frames))
    orig_tuples = [tuple(f[h] for h in headers) for f in orig_frames[:n]]
    das_tuples  = [tuple(f[h] for h in headers) for f in das_frames[:n]]

    h_orig = shannon_entropy(Counter(orig_tuples))

    # H(orig | das) = H(orig, das) - H(das)
    joint = Counter(zip(orig_tuples, das_tuples))
    das_counter = Counter(das_tuples)
    h_cond = conditional_entropy_from_joints(joint, das_counter)

    mutual_info = h_orig - h_cond

    # Per-register mutual information
    per_reg_mi = {}
    for h in headers:
        orig_vals = [f[h] for f in orig_frames[:n]]
        das_vals  = [f[h] for f in das_frames[:n]]
        h_o = shannon_entropy(Counter(orig_vals))
        j = Counter(zip(orig_vals, das_vals))
        das_marg = Counter(das_vals)
        h_c = conditional_entropy_from_joints(j, das_marg)
        per_reg_mi[h] = h_o - h_c

    return {
        'h_orig_bits_per_frame': h_orig,
        'h_cond_bits_per_frame': h_cond,
        'mutual_info_bits_per_frame': mutual_info,
        'per_register': per_reg_mi,
    }


# =========================================================================
# Theoretical minimum sizes
# =========================================================================

def compute_theoretical_limits(orig_frames, das_frames, headers, n_frames_total):
    """
    Theoretical minimum file sizes for different encoding strategies.
    """
    n = min(len(orig_frames), len(das_frames))
    orig_tuples = [tuple(f[h] for h in headers) for f in orig_frames[:n]]
    das_tuples  = [tuple(f[h] for h in headers) for f in das_frames[:n]]

    # H(trace) — entropy of original trace
    h_trace = shannon_entropy(Counter(orig_tuples))

    # H(trace | das) — what Das Model doesn't capture
    joint = Counter(zip(orig_tuples, das_tuples))
    das_counter = Counter(das_tuples)
    h_cond = conditional_entropy_from_joints(joint, das_counter)

    # Markov: H(frame_t | frame_{t-1}) for original
    pairs = list(zip(orig_tuples[:-1], orig_tuples[1:]))
    pair_counter = Counter(pairs)
    prev_counter = Counter(orig_tuples[:-1])
    h_markov = conditional_entropy_from_joints(pair_counter, prev_counter)

    # Delta encoding
    def frame_delta(f1, f2):
        return tuple((b - a) & 0xFF for a, b in zip(f1, f2))
    deltas = [frame_delta(orig_tuples[i], orig_tuples[i+1])
              for i in range(len(orig_tuples)-1)]
    h_delta = shannon_entropy(Counter(deltas))

    results = {}

    # Strategy 1: Raw trace, no compression
    raw_bytes = n_frames_total * len(headers)
    results['raw_trace'] = {
        'bytes': raw_bytes,
        'description': f'Raw register trace ({n_frames_total} frames × {len(headers)} regs)',
    }

    # Strategy 2: Entropy code the raw trace
    results['entropy_coded'] = {
        'bytes': h_trace * n_frames_total / 8,
        'description': f'Entropy-coded frames (H={h_trace:.2f} bits/frame)',
    }

    # Strategy 3: First-order Markov (delta) compression
    results['markov_coded'] = {
        'bytes': h_markov * n_frames_total / 8,
        'description': f'First-order Markov coding (H(t|t-1)={h_markov:.2f} bits/frame)',
    }

    # Strategy 4: Delta encode then entropy code
    results['delta_entropy'] = {
        'bytes': h_delta * n_frames_total / 8,
        'description': f'Delta + entropy coding (H(Δ)={h_delta:.2f} bits/frame)',
    }

    # Strategy 5: Das Model — only need to store residuals
    results['das_model_residual'] = {
        'bytes': h_cond * n_frames_total / 8,
        'description': f'Das Model stores residuals only (H(trace|USF)={h_cond:.2f} bits/frame)',
    }

    return results


# =========================================================================
# Main
# =========================================================================

def main():
    orig_sid = '/home/jtr/sidfinity/data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid'
    das_sid  = '/home/jtr/sidfinity/demo/hubbard/Commando_das_model.sid'

    N_FRAMES = 200   # for entropy estimates
    N_FRAMES_TOTAL = 3000  # full song (60 sec × 50 fps)

    print("=" * 70)
    print("INFORMATION THEORY ANALYSIS — SID Compression Limits")
    print("=" * 70)
    print(f"\nOriginal: {orig_sid}")
    print(f"Das Model: {das_sid}")
    print(f"\nUsing {N_FRAMES} frames for entropy estimation")

    # --- Load traces ---
    print("\n--- Loading register traces via siddump ---")
    orig_meta, headers, orig_frames = get_register_trace(orig_sid, N_FRAMES)
    das_meta,  _,       das_frames  = get_register_trace(das_sid,  N_FRAMES)

    print(f"Original: {orig_meta['frames']} total frames, {len(headers)} registers/frame")
    print(f"Das Model: {das_meta['frames']} total frames")
    print(f"Register names: {', '.join(headers)}")

    # --- File byte analysis ---
    print("\n--- File-level byte analysis ---")
    orig_bytes = analyze_sid_file_bytes(orig_sid)
    das_bytes  = analyze_sid_file_bytes(das_sid)

    print(f"\nOriginal SID:")
    print(f"  File size:         {orig_bytes['file_size']} bytes")
    print(f"  PSID header:       {orig_bytes['header_size']} bytes")
    print(f"  Music data:        {orig_bytes['music_data_size']} bytes")
    print(f"  Byte entropy:      {orig_bytes['byte_entropy']:.3f} bits/byte")
    print(f"  Entropy lower bound: {orig_bytes['compressed_lower_bound']:.0f} bytes")
    print(f"  Unique bytes:      {orig_bytes['unique_bytes']}")

    print(f"\nDas Model SID:")
    print(f"  File size:         {das_bytes['file_size']} bytes")
    print(f"  PSID header:       {das_bytes['header_size']} bytes")
    print(f"  Music data:        {das_bytes['music_data_size']} bytes")
    print(f"  Byte entropy:      {das_bytes['byte_entropy']:.3f} bits/byte")
    print(f"  Entropy lower bound: {das_bytes['compressed_lower_bound']:.0f} bytes")
    print(f"  Unique bytes:      {das_bytes['unique_bytes']}")

    # --- Register trace entropy ---
    print("\n--- 1. Shannon entropy of register trace H(trace) ---")
    orig_ent = analyze_trace_entropy(orig_frames, headers)
    das_ent  = analyze_trace_entropy(das_frames,  headers)

    print(f"\nOriginal trace ({N_FRAMES} frames):")
    print(f"  Sum of independent per-register H: {orig_ent['sum_independent']:.2f} bits/frame")
    print(f"  Joint H(frame):                    {orig_ent['joint_frame']:.2f} bits/frame")
    print(f"  Markov H(frame|prev_frame):        {orig_ent['markov_frame']:.2f} bits/frame")
    print(f"  Delta H(Δframe):                   {orig_ent['delta_joint']:.2f} bits/frame")
    print(f"  (25 registers × 8 bits = 200 bits/frame uncompressed)")

    print(f"\nPer-register entropy (original):")
    for name, h in sorted(orig_ent['per_register'].items()):
        print(f"    {name:20s}  H={h:.3f} bits")

    print(f"\nDas Model trace ({N_FRAMES} frames):")
    print(f"  Sum of independent per-register H: {das_ent['sum_independent']:.2f} bits/frame")
    print(f"  Joint H(frame):                    {das_ent['joint_frame']:.2f} bits/frame")
    print(f"  Markov H(frame|prev_frame):        {das_ent['markov_frame']:.2f} bits/frame")
    print(f"  Delta H(Δframe):                   {das_ent['delta_joint']:.2f} bits/frame")

    # --- USF entropy ---
    print("\n--- 2. Entropy of USF representation H(USF) ---")
    usf_ent = analyze_usf_file(orig_sid)
    if 'error' in usf_ent:
        print(f"  [USF analysis failed: {usf_ent['error']}]")
    else:
        print(f"  Total tokens in USF:    {usf_ent['n_tokens']}")
        print(f"  Unique tokens:          {usf_ent['n_unique_tokens']}")
        print(f"  H(token) per token:     {usf_ent['h_token_bits']:.3f} bits")
        print(f"  Lower bound (entropy):  {usf_ent['total_bytes_lower_bound']:.0f} bytes")
        print(f"  Token type breakdown:   {usf_ent['token_types']}")

    # --- Mutual information ---
    print("\n--- 3. Mutual information I(USF; trace) ---")
    mi = compute_mutual_information(orig_frames, das_frames, headers)
    print(f"  H(orig trace):            {mi['h_orig_bits_per_frame']:.3f} bits/frame")
    print(f"  H(orig | das):            {mi['h_cond_bits_per_frame']:.3f} bits/frame")
    print(f"  I(USF; trace):            {mi['mutual_info_bits_per_frame']:.3f} bits/frame")

    capture_pct = 100 * mi['mutual_info_bits_per_frame'] / max(mi['h_orig_bits_per_frame'], 1e-9)
    print(f"  USF captures:             {capture_pct:.1f}% of trace entropy")
    print(f"\n  Per-register mutual information:")
    for name, mi_val in sorted(mi['per_register'].items(), key=lambda x: -x[1]):
        print(f"    {name:20s}  I={mi_val:.3f} bits")

    # --- Conditional entropy ---
    print("\n--- 4. Conditional entropy H(trace | USF) ---")
    print(f"  H(trace | USF) = {mi['h_cond_bits_per_frame']:.3f} bits/frame")
    print(f"  This is information in the trace that USF does NOT capture:")
    residual_pct = 100 * mi['h_cond_bits_per_frame'] / max(mi['h_orig_bits_per_frame'], 1e-9)
    print(f"  = {residual_pct:.1f}% of total trace entropy")
    print(f"  Sources: timing jitter, phase drift, register-write ordering artifacts")

    # --- Theoretical limits ---
    print("\n--- 5. Theoretical minimum file sizes ---")
    limits = compute_theoretical_limits(orig_frames, das_frames, headers, N_FRAMES_TOTAL)

    print(f"\nFor full song ({N_FRAMES_TOTAL} frames = {N_FRAMES_TOTAL//50} seconds at 50fps):")
    print(f"  {'Strategy':<45} {'Size':>10}")
    print(f"  {'-'*57}")
    for strategy, data in limits.items():
        print(f"  {data['description']:<45} {data['bytes']:>8.0f} B")

    print(f"\n  Actual SID file size (original):  {orig_bytes['file_size']:>8} B")
    print(f"  Actual SID file size (Das Model): {das_bytes['file_size']:>8} B")

    # Compression ratios
    raw_bytes = N_FRAMES_TOTAL * len(headers)
    print(f"\n  Compression ratios vs raw trace ({raw_bytes} B):")
    print(f"    Raw SID / raw trace:      1:{raw_bytes / orig_bytes['file_size']:.0f}x")
    print(f"    Das Model / raw trace:    1:{raw_bytes / das_bytes['file_size']:.0f}x")
    for strategy, data in limits.items():
        if data['bytes'] > 0:
            print(f"    {strategy:<30}: 1:{raw_bytes / data['bytes']:.1f}x")

    # --- Summary statistics ---
    print("\n--- Summary ---")
    print(f"  Observed per-frame entropy (independent regs): {orig_ent['sum_independent']:.1f} bits/frame")
    print(f"  Observed per-frame entropy (joint frame):      {orig_ent['joint_frame']:.1f} bits/frame")
    print(f"  Intra-frame correlation savings:               {orig_ent['sum_independent'] - orig_ent['joint_frame']:.1f} bits/frame ({100*(1-orig_ent['joint_frame']/orig_ent['sum_independent']):.0f}%)")
    print(f"  Inter-frame (Markov) savings:                  {orig_ent['joint_frame'] - orig_ent['markov_frame']:.1f} bits/frame")
    print(f"  USF residual (unexplained by Das Model):       {mi['h_cond_bits_per_frame']:.1f} bits/frame ({residual_pct:.0f}%)")

    return {
        'orig_ent': orig_ent,
        'das_ent': das_ent,
        'mi': mi,
        'usf_ent': usf_ent,
        'limits': limits,
        'orig_bytes': orig_bytes,
        'das_bytes': das_bytes,
        'headers': headers,
        'N_FRAMES_TOTAL': N_FRAMES_TOTAL,
    }


if __name__ == '__main__':
    results = main()
