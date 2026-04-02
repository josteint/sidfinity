"""
gt2_tempo.py — Robust DEFAULTTEMPO extraction for GT2 packed SID binaries.

Tries three strategies in order:
1. Pattern-match LDA #xx / STA abs,X / LDA #$01 / STA abs,X in init code
2. greloc.c formula: if last instrument has AD >= 2 and wave_ptr == 0,
   use AD - 1. Otherwise use 5 (single-speed default).
3. Validate via siddump: first note should appear around frame tempo+1 (+-2).
"""

import os
import subprocess


def _find_siddump():
    """Find siddump binary, checking worktree-relative and repo-root paths."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, '..', 'tools', 'siddump'),
        os.path.join(script_dir, '..', '..', '..', 'tools', 'siddump'),
        os.path.join(script_dir, '..', '..', '..', '..', 'tools', 'siddump'),
    ]
    for c in candidates:
        c = os.path.normpath(c)
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    # Also try finding via SIDDUMP env var or PATH
    env_path = os.environ.get('SIDDUMP')
    if env_path and os.path.isfile(env_path):
        return env_path
    return None


SIDDUMP = _find_siddump()


def extract_default_tempo(binary, la, code_end, ni=None, col_data=None, sid_path=None):
    """Extract DEFAULTTEMPO from a GT2 packed SID binary.

    Args:
        binary: raw SID binary (after PSID header)
        la: load address
        code_end: offset in binary where player code ends (freq table starts)
        ni: number of packed instruments (optional, for greloc.c fallback)
        col_data: dict of column name -> list of values (optional, for fallback)
        sid_path: path to .sid file (optional, for siddump validation)

    Returns:
        int: DEFAULTTEMPO value (typically 3-12 for single-speed)
    """
    tempo_pattern = None
    tempo_instrument = None

    # Strategy 1: Pattern-match in init code
    # Look for LDA #xx / STA abs,X / LDA #$01 / STA abs,X
    # (mt_initchn sets counter=1, tempo=DEFAULTTEMPO)
    scan_end = min(code_end - 8, len(binary) - 8)
    for i in range(max(0, scan_end)):
        if (binary[i] == 0xA9 and binary[i + 2] == 0x9D and
                binary[i + 5] == 0xA9 and binary[i + 6] == 0x01 and
                binary[i + 7] == 0x9D):
            tempo_pattern = binary[i + 1] + 1  # stored as tempo-1 in binary
            break

    # Strategy 2: greloc.c formula from last instrument data
    # In greloc.c: if instr[MAX_INSTR-1].ad >= 2 and wave_ptr == 0, use ad-1
    # In the packed binary, the last instrument (index ni-1, 0-based) holds
    # this special data when the composer set a custom default tempo.
    if ni is not None and ni > 0 and col_data is not None:
        ad_col = col_data.get('ad', [])
        wp_col = col_data.get('wave_ptr', [])
        if len(ad_col) >= ni and len(wp_col) >= ni:
            last_ad = ad_col[ni - 1]
            last_wp = wp_col[ni - 1]
            if isinstance(last_ad, str):
                last_ad = int(last_ad, 16)
            if isinstance(last_wp, str):
                last_wp = int(last_wp, 16)
            if last_ad >= 2 and last_wp == 0:
                tempo_instrument = last_ad - 1
            else:
                tempo_instrument = 5  # GT2 default for single-speed

    # If both strategies agree, return immediately
    if tempo_pattern is not None and tempo_instrument is not None:
        if tempo_pattern == tempo_instrument:
            return tempo_pattern

    # Pick a candidate: prefer instrument method (more reliable when init
    # code pattern varies), fall back to pattern match
    candidate = tempo_instrument if tempo_instrument is not None else tempo_pattern
    if candidate is None:
        candidate = 6  # safe GT2 default

    # Strategy 3: Validate with siddump output
    # The player counts down from DEFAULTTEMPO to 0 before processing the
    # first row, so the first audible note appears at ~frame DEFAULTTEMPO+1.
    if sid_path is not None and SIDDUMP is not None:
        try:
            proc = subprocess.run([SIDDUMP, sid_path, '--duration', '2'],
                                  capture_output=True, text=True, timeout=15)
            if proc.returncode in (0, 2):
                lines = proc.stdout.strip().split('\n')[2:]  # skip header
                first_note_frame = _find_first_note_frame(lines)

                if first_note_frame is not None:
                    expected = candidate + 1
                    if abs(first_note_frame - expected) <= 2:
                        return candidate

                    # Both strategies exist but disagree -- pick the one
                    # that matches siddump better
                    if tempo_pattern is not None and tempo_instrument is not None:
                        err_pat = abs(first_note_frame - (tempo_pattern + 1))
                        err_ins = abs(first_note_frame - (tempo_instrument + 1))
                        if err_pat < err_ins and err_pat <= 2:
                            return tempo_pattern
                        elif err_ins < err_pat and err_ins <= 2:
                            return tempo_instrument

                    # Neither matches well -- derive from siddump directly
                    derived = first_note_frame - 1
                    if 1 <= derived <= 50:
                        return derived
        except Exception:
            pass

    return candidate


def _find_first_note_frame(csv_lines):
    """Find the first frame where any voice plays an audible note.

    Returns frame index (0-based) or None if no note found.
    """
    for fi, line in enumerate(csv_lines):
        try:
            vals = [int(v, 16) for v in line.split(',')]
        except (ValueError, IndexError):
            continue
        for voice in range(3):
            base = voice * 7
            if base + 4 >= len(vals):
                break
            fhi = vals[base + 1]
            wav = vals[base + 4]
            # A real note: non-zero freq and audible waveform
            # (not $00=off, $08=test, $09=test+gate during hard restart)
            if fhi > 0 and wav not in (0x00, 0x08, 0x09):
                return fi
    return None
