#!/usr/bin/env python3
"""
verify_note_extraction.py — Comprehensive verification of Das Model note extraction.

Runs both the original Commando SID and the Das Model rebuilt SID under py65 for
500 frames, recording register state at each frame. Compares:
  - Note pitch (freq_hi per voice, mapped back to note index if possible)
  - Note duration (how many frames each freq_hi value persists)
  - Instrument (ctrl + ADSR per voice)
  - Pattern boundaries (when freq_hi changes)

Reports discrepancies between original and rebuilt to identify extraction bugs.
"""

import os
import sys
import struct
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'py65_lib'))

ORIG_SID = os.path.join(ROOT, 'data', 'C64Music', 'MUSICIANS', 'H',
                         'Hubbard_Rob', 'Commando.sid')
DAS_SID  = os.path.join(ROOT, 'demo', 'hubbard', 'Commando_das_model.sid')
MAX_FRAMES = 500
N_VOICES = 3
VOICE_OFF = [0, 7, 14]   # SID register offsets per voice ($D400 base)


# ---------------------------------------------------------------------------
# SID loader + py65 runner
# ---------------------------------------------------------------------------

def load_sid_mem(sid_path):
    """Load SID file, return (mem, init_addr, play_addr, load_addr)."""
    with open(sid_path, 'rb') as f:
        data = f.read()
    if data[:4] not in (b'PSID', b'RSID'):
        raise ValueError(f"Not a SID: {sid_path}")
    hdr_len   = struct.unpack('>H', data[6:8])[0]
    load_addr = struct.unpack('>H', data[8:10])[0]
    init_addr = struct.unpack('>H', data[10:12])[0]
    play_addr = struct.unpack('>H', data[12:14])[0]
    payload   = data[hdr_len:]
    if load_addr == 0:
        load_addr = struct.unpack('<H', payload[:2])[0]
        binary    = payload[2:]
    else:
        binary = payload
    mem = bytearray(65536)
    mem[load_addr:load_addr + len(binary)] = binary
    return mem, init_addr, play_addr, load_addr


def run_sid(sid_path, max_frames=MAX_FRAMES):
    """
    Run a SID under py65 for max_frames frames.
    Returns list of dicts, one per frame:
      { 'flo': [v1,v2,v3], 'fhi': [v1,v2,v3],
        'plo': [...], 'phi': [...], 'ctl': [...], 'ad': [...], 'sr': [...] }
    """
    from py65.devices.mpu6502 import MPU

    mem, init_addr, play_addr, load_addr = load_sid_mem(sid_path)

    m = MPU()
    m.memory = bytearray(mem)
    # NMI/IRQ vectors point to BRK ($00) at $FFF0
    m.memory[0xFFFE] = 0xF0
    m.memory[0xFFFF] = 0xFF
    m.memory[0xFFFA] = 0xF0
    m.memory[0xFFFB] = 0xFF
    m.memory[0xFFF0] = 0x00   # BRK at $FFF0 = our "halt" sentinel

    # INIT: push fake return address, run
    m.stPush(0xFF)
    m.stPush(0xEF)   # return to $FFF0 = BRK
    m.pc = init_addr
    m.a  = 0         # subtune 0 (first song)
    for _ in range(200_000):
        if m.memory[m.pc] == 0x00:
            break
        m.step()

    frames = []
    for _ in range(max_frames):
        # PLAY
        m.stPush(0xFF)
        m.stPush(0xEF)
        m.pc = play_addr
        for _ in range(200_000):
            if m.memory[m.pc] == 0x00:
                break
            m.step()

        # Snapshot SID registers ($D400-$D412)
        frame = {}
        for name, base_off in [('flo',0),('fhi',1),('plo',2),('phi',3),
                                ('ctl',4),('ad',5),('sr',6)]:
            frame[name] = [m.memory[0xD400 + VOICE_OFF[v] + base_off]
                           for v in range(N_VOICES)]
        frames.append(frame)

    return frames


# ---------------------------------------------------------------------------
# Freq table reverse lookup
# ---------------------------------------------------------------------------

def build_fhi_to_note(freq_list):
    """Map freq_hi -> list of (note_idx, freq_value) for all freq table entries."""
    result = defaultdict(list)
    for idx, freq in enumerate(freq_list):
        fhi = (freq >> 8) & 0xFF
        result[fhi].append(idx)
    return result


# ---------------------------------------------------------------------------
# Per-voice note stream: extract (fhi, duration) runs from frame data
# ---------------------------------------------------------------------------

def extract_runs(frames, voice, key='fhi'):
    """
    Extract consecutive runs where SID register [key][voice] stays constant.
    Returns list of (value, start_frame, duration) tuples.
    """
    runs = []
    if not frames:
        return runs
    cur_val   = frames[0][key][voice]
    cur_start = 0
    for fr in range(1, len(frames)):
        val = frames[fr][key][voice]
        if val != cur_val:
            runs.append((cur_val, cur_start, fr - cur_start))
            cur_val   = val
            cur_start = fr
    runs.append((cur_val, cur_start, len(frames) - cur_start))
    return runs


# ---------------------------------------------------------------------------
# Note pitch runs: track meaningful note changes (skip instrument/gate frames)
# ---------------------------------------------------------------------------

def extract_note_events(frames, voice):
    """
    Return list of note events: (fhi_at_start, first_frame, total_frames_with_that_fhi)
    We consider a 'note event' = when fhi changes to a new value AND ctrl has gate ON.
    """
    events = []
    if not frames:
        return events
    prev_fhi = -1
    note_start = 0
    for fr, frame in enumerate(frames):
        fhi = frame['fhi'][voice]
        ctl = frame['ctl'][voice]
        gate = ctl & 1
        if fhi != prev_fhi and gate:
            if prev_fhi >= 0:
                events.append({'fhi': prev_fhi, 'start': note_start,
                                'dur': fr - note_start, 'ctl': frames[note_start]['ctl'][voice]})
            prev_fhi  = fhi
            note_start = fr
    if prev_fhi >= 0:
        events.append({'fhi': prev_fhi, 'start': note_start,
                        'dur': len(frames) - note_start, 'ctl': frames[note_start]['ctl'][voice]})
    return events


# ---------------------------------------------------------------------------
# Main comparison
# ---------------------------------------------------------------------------

def compare(orig_frames, das_frames):
    n = min(len(orig_frames), len(das_frames))
    results = {}

    for v in range(N_VOICES):
        vname = f'V{v+1}'
        mismatches = []

        # Frame-by-frame comparison
        for reg in ('fhi', 'ctl', 'ad', 'sr'):
            diffs = []
            for fr in range(n):
                ov = orig_frames[fr][reg][v]
                dv = das_frames[fr][reg][v]
                if ov != dv:
                    diffs.append((fr, ov, dv))
            if diffs:
                mismatches.append({'reg': reg, 'diffs': diffs})

        results[vname] = mismatches

    # Note event comparison
    note_results = {}
    for v in range(N_VOICES):
        vname = f'V{v+1}'
        orig_events = extract_note_events(orig_frames[:n], v)
        das_events  = extract_note_events(das_frames[:n], v)
        note_results[vname] = {
            'orig': orig_events,
            'das':  das_events,
        }

    return results, note_results


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def format_report(orig_frames, das_frames, reg_results, note_results,
                  out_path=None):
    n = min(len(orig_frames), len(das_frames))
    lines = []

    lines.append("# Note Extraction Verification — Commando.sid vs Das Model")
    lines.append("")
    lines.append(f"Frames compared: {n} (original) / {len(das_frames)} (das model)")
    lines.append("")

    # ---- Per-register difference summary ----
    lines.append("## Register Difference Summary")
    lines.append("")
    total_diffs = 0
    for vname, mismatches in reg_results.items():
        if not mismatches:
            lines.append(f"### {vname}: PERFECT — no register differences")
        else:
            for mm in mismatches:
                reg  = mm['reg']
                ndif = len(mm['diffs'])
                total_diffs += ndif
                pct  = 100.0 * ndif / n
                lines.append(f"### {vname} {reg}: {ndif}/{n} frames differ ({pct:.1f}%)")
                # Show first 20 differences in a table
                lines.append("")
                lines.append("| Frame | Orig | DasModel | Delta |")
                lines.append("|-------|------|----------|-------|")
                for fr, ov, dv in mm['diffs'][:20]:
                    lines.append(f"| {fr:5d} | ${ov:02X}  | ${dv:02X}     | {dv-ov:+4d}  |")
                if ndif > 20:
                    lines.append(f"| ... ({ndif-20} more) | | | |")
                lines.append("")
    lines.append("")
    lines.append(f"**Total register differences: {total_diffs} across {n} frames × 3 voices × 4 registers**")
    lines.append("")

    # ---- Note event comparison ----
    lines.append("## Note Event Comparison (gate-on transitions by voice)")
    lines.append("")
    for vname, evdata in note_results.items():
        oe = evdata['orig']
        de = evdata['das']
        lines.append(f"### {vname}: {len(oe)} original notes vs {len(de)} das model notes")
        lines.append("")

        max_ev = min(len(oe), len(de), 30)
        if max_ev == 0:
            lines.append("(no note events detected)")
            lines.append("")
            continue

        lines.append("| # | Orig fhi | Das fhi | Match | Orig dur | Das dur | Dur match |")
        lines.append("|---|----------|---------|-------|----------|---------|-----------|")
        pitch_ok = 0
        dur_ok   = 0
        for i in range(max_ev):
            o = oe[i]
            d = de[i]
            pmatch = "OK" if o['fhi'] == d['fhi'] else f"MISMATCH orig=${o['fhi']:02X} das=${d['fhi']:02X}"
            dmatch = "OK" if abs(o['dur'] - d['dur']) <= 1 else f"MISMATCH orig={o['dur']} das={d['dur']}"
            if o['fhi'] == d['fhi']: pitch_ok += 1
            if abs(o['dur'] - d['dur']) <= 1: dur_ok += 1
            lines.append(f"| {i:2d} | ${o['fhi']:02X}     | ${d['fhi']:02X}    | {'OK' if o['fhi']==d['fhi'] else 'DIFF'} | {o['dur']:6d}   | {d['dur']:6d}  | {'OK' if abs(o['dur']-d['dur'])<=1 else 'DIFF'} |")

        if len(oe) > 30 or len(de) > 30:
            lines.append(f"| ... (showing first 30 of {max(len(oe),len(de))}) | | | | | | |")
        lines.append("")
        lines.append(f"Pitch match: {pitch_ok}/{max_ev} ({100*pitch_ok/max_ev:.0f}%)")
        lines.append(f"Duration match (±1 frame): {dur_ok}/{max_ev} ({100*dur_ok/max_ev:.0f}%)")
        lines.append("")

    # ---- fhi run comparison (for timing analysis) ----
    lines.append("## fhi Consecutive-Run Comparison (first 40 runs per voice)")
    lines.append("")
    for v in range(N_VOICES):
        vname = f'V{v+1}'
        oruns = extract_runs(orig_frames[:n], v, 'fhi')
        druns = extract_runs(das_frames[:n], v, 'fhi')
        lines.append(f"### {vname}: {len(oruns)} orig runs / {len(druns)} das runs")
        lines.append("")
        lines.append("| # | Orig fhi | Orig dur | Das fhi | Das dur | Pitch | Dur |")
        lines.append("|---|----------|----------|---------|---------|-------|-----|")
        max_r = min(len(oruns), len(druns), 40)
        pitch_ok = 0
        dur_ok   = 0
        for i in range(max_r):
            ov, os_, od = oruns[i]
            dv, ds_, dd = druns[i]
            pm = "OK" if ov == dv else "DIFF"
            dm = "OK" if abs(od - dd) <= 1 else "DIFF"
            if ov == dv: pitch_ok += 1
            if abs(od - dd) <= 1: dur_ok += 1
            lines.append(f"| {i:2d} | ${ov:02X}     | {od:7d}  | ${dv:02X}    | {dd:6d}  | {pm:5s} | {dm:4s} |")
        if max_r < max(len(oruns), len(druns)):
            lines.append(f"| ... ({max(len(oruns),len(druns)) - max_r} more) | | | | | | |")
        lines.append("")
        if max_r > 0:
            lines.append(f"Pitch match: {pitch_ok}/{max_r} ({100*pitch_ok/max_r:.0f}%)")
            lines.append(f"Duration match (±1 frame): {dur_ok}/{max_r} ({100*dur_ok/max_r:.0f}%)")
        lines.append("")

    # ---- ADSR consistency check ----
    lines.append("## Instrument (ADSR) Consistency Check")
    lines.append("")
    lines.append("Check: does each unique fhi value always map to the same ad+sr in both streams?")
    lines.append("")
    for v in range(N_VOICES):
        vname = f'V{v+1}'
        # Build fhi -> set of (ad,sr) in original
        orig_fhi_adsr = defaultdict(set)
        das_fhi_adsr  = defaultdict(set)
        for fr in range(n):
            fhi = orig_frames[fr]['fhi'][v]
            ad  = orig_frames[fr]['ad'][v]
            sr  = orig_frames[fr]['sr'][v]
            orig_fhi_adsr[fhi].add((ad, sr))
            fhi = das_frames[fr]['fhi'][v]
            ad  = das_frames[fr]['ad'][v]
            sr  = das_frames[fr]['sr'][v]
            das_fhi_adsr[fhi].add((ad, sr))
        # Find fhi values with inconsistent ADSR in either stream
        inconsistent = []
        for fhi in sorted(set(list(orig_fhi_adsr.keys()) + list(das_fhi_adsr.keys()))):
            oa = orig_fhi_adsr.get(fhi, set())
            da = das_fhi_adsr.get(fhi, set())
            if len(oa) > 1 or len(da) > 1 or oa != da:
                inconsistent.append((fhi, oa, da))
        if not inconsistent:
            lines.append(f"{vname}: All fhi values have consistent ADSR in both streams.")
        else:
            lines.append(f"{vname}: {len(inconsistent)} fhi values with inconsistent/mismatched ADSR:")
            lines.append("")
            lines.append("| fhi | Orig (ad,sr) | Das (ad,sr) |")
            lines.append("|-----|-------------|------------|")
            for fhi, oa, da in inconsistent[:20]:
                oa_str = ' '.join(f'AD${x[0]:02X} SR${x[1]:02X}' for x in sorted(oa))
                da_str = ' '.join(f'AD${x[0]:02X} SR${x[1]:02X}' for x in sorted(da))
                lines.append(f"| ${fhi:02X} | {oa_str} | {da_str} |")
            if len(inconsistent) > 20:
                lines.append(f"| ... ({len(inconsistent)-20} more) | | |")
        lines.append("")

    # ---- Overall verdict ----
    lines.append("## Overall Verdict")
    lines.append("")
    # Count perfect frames
    perfect = 0
    for fr in range(n):
        ok = True
        for v in range(N_VOICES):
            for reg in ('fhi', 'ctl', 'ad', 'sr'):
                if orig_frames[fr][reg][v] != das_frames[fr][reg][v]:
                    ok = False
                    break
            if not ok:
                break
        if ok:
            perfect += 1
    lines.append(f"Perfect frames (fhi+ctl+ad+sr match all 3 voices): {perfect}/{n} ({100*perfect/n:.1f}%)")
    lines.append("")

    # Pitch-only (fhi) perfect frames
    fhi_perfect = 0
    for fr in range(n):
        if all(orig_frames[fr]['fhi'][v] == das_frames[fr]['fhi'][v] for v in range(N_VOICES)):
            fhi_perfect += 1
    lines.append(f"fhi-only match (pitch only, all voices): {fhi_perfect}/{n} ({100*fhi_perfect/n:.1f}%)")
    lines.append("")

    text = '\n'.join(lines)
    if out_path:
        with open(out_path, 'w') as f:
            f.write(text)
        print(f"Report written to {out_path}")
    return text


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    print(f"Loading original SID: {ORIG_SID}")
    if not os.path.exists(ORIG_SID):
        print("ERROR: Commando.sid not found")
        sys.exit(1)
    if not os.path.exists(DAS_SID):
        print(f"ERROR: Das model SID not found: {DAS_SID}")
        print("Run python3 src/das_model_gen.py first to build it.")
        sys.exit(1)

    print(f"Running original for {MAX_FRAMES} frames...")
    orig_frames = run_sid(ORIG_SID, MAX_FRAMES)
    print(f"Running Das Model for {MAX_FRAMES} frames...")
    das_frames  = run_sid(DAS_SID,  MAX_FRAMES)

    print("Comparing...")
    reg_results, note_results = compare(orig_frames, das_frames)

    out_path = os.path.join(ROOT, 'docs', 'note_extraction_verification.md')
    report = format_report(orig_frames, das_frames, reg_results, note_results,
                           out_path=out_path)
    # Also print a brief summary to stdout
    n = min(len(orig_frames), len(das_frames))
    perfect = sum(
        1 for fr in range(n)
        if all(orig_frames[fr][reg][v] == das_frames[fr][reg][v]
               for v in range(N_VOICES) for reg in ('fhi', 'ctl', 'ad', 'sr'))
    )
    print(f"\nPerfect frames: {perfect}/{n} ({100*perfect/n:.1f}%)")
    total_fhi_diffs = sum(
        1 for fr in range(n) for v in range(N_VOICES)
        if orig_frames[fr]['fhi'][v] != das_frames[fr]['fhi'][v]
    )
    print(f"Total fhi differences: {total_fhi_diffs} across {n*N_VOICES} voice-frames")
    print(f"Report: {out_path}")


if __name__ == '__main__':
    main()
