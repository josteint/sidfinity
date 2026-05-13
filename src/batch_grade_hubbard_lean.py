"""batch_grade_hubbard_lean.py — replaces batch_grade_hubbard.py.

Runs the canonical Lean V3 clone path on every Hubbard-engine SID in
HVSC:

  SID → das_model_gen.extract(sid_path, ft_base=discovered)
      → write src/formal/BatchV3.lean (with bv3 prefix, batchV3 name)
      → lake build sidgen_batch (incremental — only BatchV3 + exe rebuild)
      → ./.lake/build/bin/sidgen_batch → src/formal/batch_v3.sid
      → writelog_grade vs original
      → record grade

Replaces the rh_to_usf-based batch_grade_hubbard.py (which produced
0/285 Grade A and is now deprecated). This tool tests the LEAN V3
CLONE PATH instead.

Per-SID cost: ~10-15s (memtrace + Lean rebuild + grader). For 285
SIDs that's ~45-60 minutes serial. Not parallelized — Lean's build
serializes anyway since BatchV3.lean is a shared file.
"""
import os
import sys
import csv
import time
import subprocess
import traceback
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

FORMAL = os.path.join(ROOT, 'src', 'formal')
LAKE_BUILD_BIN = os.path.join(FORMAL, '.lake', 'build', 'bin')
BATCH_LEAN = os.path.join(FORMAL, 'BatchV3.lean')
BATCH_SID = os.path.join(FORMAL, 'batch_v3.sid')


# --- Lean code emit helpers (cloned from gen_monty_v3.py, prefix 'bv3') ---

def _lean_str(s):
    """Quote a Python string as a Lean string literal (double-quoted,
    backslash-escaped)."""
    out = (s.replace('\\', '\\\\')
            .replace('"', '\\"')
            .replace('\n', '\\n'))
    return f'"{out}"'


def hex_byte(n):
    return f"⟨{n & 0xFF}, by omega⟩"


def gen_freq_table(T):
    pairs = []
    for i in range(128):
        flo = T[i] & 0xFF if i < len(T) else 0
        fhi = (T[i] >> 8) & 0xFF if i < len(T) else 0
        if i == 104:
            flo = 0; fhi = 0
        pairs.append(f"({hex_byte(flo)}, {hex_byte(fhi)})")
    return "[" + ", ".join(pairs) + "]"


def gen_instrument(idx, inst):
    pw = inst['P']
    bit0 = inst.get('has_bit0', False)
    arp_off = inst.get('arp_offset', 0)
    vib = inst.get('vibrato_scale', 0)
    w = inst['W']
    waveform = w['steps']
    loop = w['loop']
    init_pw = pw['init_pw']
    init_lo = init_pw & 0xFF
    init_hi = (init_pw >> 8) & 0x0F

    if pw['speed'] == 0:
        pwmod = 'none'
    elif pw['mode'] == 'linear':
        pwmod = (f"some {{ mode := .linear {hex_byte(pw['speed'])}, "
                 f"stepEvery := 1, startDelay := 0 }}")
    else:
        pwmod = (f"some {{ mode := .bidirectional {hex_byte(pw['speed'])} "
                 f"{hex_byte(pw.get('min_hi', 8))} "
                 f"{hex_byte(pw.get('max_hi', 14))}, "
                 f"stepEvery := 1, startDelay := 0 }}")

    if vib == 0:
        vibspec = 'none'
    else:
        vibspec = (f"some {{ shape := .triangle, periodFrames := 8, "
                   f"semitoneShift := {vib + 1}, onsetFrames := 6, "
                   f"rampUpFrames := 0, unipolar := true }}")

    slidespec = ("some { kind := .monotonic (-1), stepEvery := 1, "
                 "startDelay := 9, stopAtZero := true }") if bit0 else 'none'
    arpspec = (f"some {{ intervals := [0, {arp_off}], stepEvery := 1, "
               f"phaseSource := .global, startDelay := 0 }}") if arp_off > 0 else 'none'

    eff_parts = []
    if vib > 0: eff_parts.append('.vibrato')
    eff_parts.append('.pwMod')
    if bit0: eff_parts.append('.freqSlide')
    if arp_off > 0: eff_parts.append('.arpeggio')
    eff_parts.append('.gateCheck')
    eff_order = '[' + ', '.join(eff_parts) + ']'

    waveform_lit = '[' + ', '.join(hex_byte(b) for b in waveform) + ']'

    return f"""def bv3I{idx} : USFInstrument := {{
  initCtrl := {hex_byte(waveform[0])}
  initPwLo := {hex_byte(init_lo)}
  initPwHi := {hex_byte(init_hi)}
  ad := {hex_byte(inst['E']['ad'])}
  sr := {hex_byte(inst['E']['sr'])}
  initFreqMod := .normal
  waveformProgram := {waveform_lit}
  waveLoop := {loop}
  waveStepEvery := 1
  pwMod := {pwmod}
  vibrato := {vibspec}
  freqSlide := {slidespec}
  arpeggio := {arpspec}
  effectOrder := {eff_order}
  release := {{ framesBeforeEnd := 3, zeroAdsr := true, noRelease := false }}
  filterEnabled := false
}}"""


def gen_note(note, tempo):
    pitch = note['pitch']
    dur = note['duration']
    inst_raw = note['instrument']
    no_release = bool(note.get('drum_trig', 0) & 0x80)
    inst = (inst_raw & 0xFF) | (0x20 if no_release else 0)
    tie = note.get('tie', False)
    frames = dur * tempo
    porta = note.get('drum_trig', 0) & 0x7F
    if tie:
        kind = '.tie'
    elif pitch == 104:
        kind = '.percussion .dynamicCtrl'
    elif pitch < 96:
        kind = f'.pitched {hex_byte(pitch)}'
    else:
        kind = '.percussion .dynamicCtrl'
    return (f"{{ kind := {kind}, durationFrames := {frames}, "
            f"instrument := {inst}, porta := {porta} }}")


def gen_pattern(idx, notes, tempo):
    note_strs = [gen_note(n, tempo) for n in notes]
    return f"def bv3P{idx} : USFPattern := {{ notes := [{', '.join(note_strs)}] }}"


def emit_batch_lean(sid_path: str, T, instruments, score,
                     title='?', author='?', released='?'):
    """Render the BatchV3.lean file for a single SID's data."""
    out = ["-- Auto-generated by src/batch_grade_hubbard_lean.py.",
           "-- Overwritten per-SID during batch grading.",
           f"-- Source: {sid_path}",
           "import USFv3", ""]
    out.append(f"def batchV3FreqTable : USFFreqTable := "
               f"{{ entries := {gen_freq_table(T)} }}")
    out.append("")
    for i, inst in enumerate(instruments):
        out.append(gen_instrument(i, inst))
        out.append("")

    # One subtune (subtune 0) — batch grading uses the start_song
    tempo = score['tempo']
    all_pats = {}
    for v in score['voices']:
        for pat_idx, pat_notes in v['patterns'].items():
            if pat_idx not in all_pats:
                all_pats[pat_idx] = pat_notes
    for idx in sorted(all_pats.keys()):
        out.append(gen_pattern(idx, all_pats[idx], tempo))
        out.append("")

    voice_defs = []
    for vi, v in enumerate(score['voices']):
        ol = '[' + ', '.join(str(p) for p in v['orderlist']) + ']'
        loop_pt = v.get('loop')
        loop_str = (f'some {loop_pt}' if loop_pt is not None and loop_pt >= 0
                    else 'none')
        voice_defs.append(
            f"def bv3V{vi} : USFVoice := "
            f"{{ orderlist := {ol}, loopPoint := {loop_str} }}")
    out.extend(voice_defs)
    out.append("")
    v_refs = ', '.join(f'bv3V{i}' for i in range(len(score['voices'])))
    out.append(f"def bv3S0 : USFSubtune := {{ voices := [{v_refs}], "
               f"tempo := {tempo} }}")
    out.append("")
    max_pat = max(all_pats.keys()) + 1 if all_pats else 0
    pat_refs = []
    for i in range(max_pat):
        pat_refs.append(f'bv3P{i}' if i in all_pats else '{ notes := [] }')
    inst_refs = ', '.join(f'bv3I{i}' for i in range(len(instruments)))
    pat_list = ', '.join(pat_refs)
    # Same engine quirks as Commando (Hubbard engine assumption — refine later)
    quirks = """{
    preserveNoteFlags := true
    voiceScratch := [
      { name := "hub_off", initial := ⟨0, by omega⟩ },
      { name := "seq_idx", initial := ⟨0, by omega⟩ }
    ]
    noteLoadOps := [
      .addByFlag 0 [
        (⟨0x40, by omega⟩, ⟨0x40, by omega⟩, ⟨1, by omega⟩),
        (⟨0x80, by omega⟩, ⟨0x80, by omega⟩, ⟨2, by omega⟩),
        (⟨0x00, by omega⟩, ⟨0x00, by omega⟩, ⟨3, by omega⟩)
      ],
      .resetIfNextEnds 0,
      .incIfNextEnds   1 ⟨1, by omega⟩
    ]
    patternEndOps := [ .reset 0, .increment 1 ⟨1, by omega⟩ ]
    dynamicFreqEntries := [
      { freqSlot := 100, loSource := .scratch ⟨1, by omega⟩ 0,
        hiSource := .scratch ⟨2, by omega⟩ 0, phase := .atFrameStart },
      { freqSlot := 104, loSource := .voiceCtrl ⟨0, by omega⟩,
        hiSource := .voiceCtrl ⟨1, by omega⟩, phase := .atFrameStart },
      { freqSlot := 98, loSource := .scratch ⟨0, by omega⟩ 1,
        hiSource := .scratch ⟨1, by omega⟩ 1,
        phase := .beforeVoice ⟨1, by omega⟩ },
      { freqSlot := 99, loSource := .scratch ⟨2, by omega⟩ 1,
        hiSource := .scratch ⟨0, by omega⟩ 0,
        phase := .beforeVoice ⟨1, by omega⟩ },
      { freqSlot := 105, loSource := .voiceCtrl ⟨2, by omega⟩,
        hiSource := .voicePitch ⟨0, by omega⟩,
        phase := .beforeVoice ⟨1, by omega⟩ },
      { freqSlot := 106, loSource := .voicePitch ⟨1, by omega⟩,
        hiSource := .voicePitch ⟨2, by omega⟩,
        phase := .beforeVoice ⟨1, by omega⟩ },
      { freqSlot := 107, loSource := .voiceInst ⟨0, by omega⟩,
        hiSource := .voiceInst ⟨1, by omega⟩,
        phase := .beforeVoice ⟨1, by omega⟩ },
      { freqSlot := 100, loSource := .scratch ⟨1, by omega⟩ 0,
        hiSource := .scratch ⟨2, by omega⟩ 0,
        phase := .beforeVoice ⟨0, by omega⟩ },
      { freqSlot := 104, loSource := .voiceCtrl ⟨0, by omega⟩,
        hiSource := .voiceCtrl ⟨1, by omega⟩,
        phase := .beforeVoice ⟨0, by omega⟩ }
    ]
  }"""
    out.append(f"""def batchV3 : USFSong := {{
  freqTable := batchV3FreqTable
  instruments := [{inst_refs}]
  patterns := [{pat_list}]
  subtunes := [bv3S0]
  voiceOrder := [⟨2, by omega⟩, ⟨1, by omega⟩, ⟨0, by omega⟩]
  filter := none
  playRate := .vbi
  engineQuirks := {quirks}
  title := {_lean_str(title)}
  author := {_lean_str(author)}
  released := {_lean_str(released)}
}}""")
    return '\n'.join(out) + '\n'


def process_one(sid_path: str) -> dict:
    """Discovery → extract → emit Lean → build → run → grade."""
    out = {'path': sid_path, 'name': os.path.basename(sid_path),
           'grade': '?', 'snap_pct': 0.0, 'top_diverging': [],
           'phase': '', 'error': ''}
    try:
        # 1. Discover landmarks
        out['phase'] = 'discover'
        from discover_hubbard_landmarks import discover_hubbard_landmarks
        lm = discover_hubbard_landmarks(sid_path)
        if not lm.found.get('freq_table_addr', False):
            out['error'] = 'no freq_table_addr discovered'
            return out

        # 2. Extract (T, I, S)
        out['phase'] = 'extract'
        from pipelines.commando.extract.engine_model import extract
        T, instrs, score = extract(subtune=0,
                                    sid_path=sid_path,
                                    ft_base=lm.freq_table_addr)

        # 3. Emit BatchV3.lean
        out['phase'] = 'emit_lean'
        lean_text = emit_batch_lean(sid_path, T, instrs, score,
                                     title=os.path.basename(sid_path))
        with open(BATCH_LEAN, 'w') as f:
            f.write(lean_text)

        # 4. Lake build (incremental)
        out['phase'] = 'lake_build'
        r = subprocess.run(['lake', 'build', 'sidgen_batch'],
                           cwd=FORMAL, capture_output=True, text=True,
                           timeout=120)
        if r.returncode != 0:
            out['error'] = f'lake failed: {r.stderr[:300]}'
            return out

        # 5. Run the exe
        out['phase'] = 'run_exe'
        r = subprocess.run([os.path.join(LAKE_BUILD_BIN, 'sidgen_batch')],
                           cwd=FORMAL, capture_output=True, text=True,
                           timeout=30)
        if r.returncode != 0 or not os.path.exists(BATCH_SID):
            out['error'] = f'sidgen_batch failed: {r.stderr[:200]}'
            return out

        # 6. Grade
        out['phase'] = 'grade'
        from writelog_grade import grade
        report = grade(sid_path, BATCH_SID, duration=10)
        out['grade'] = report.grade
        out['snap_pct'] = report.snapshot_match_pct
        sorted_div = sorted(report.diverging_registers.items(),
                            key=lambda kv: -kv[1])[:5]
        out['top_diverging'] = list(sorted_div)
    except subprocess.TimeoutExpired as e:
        out['error'] = f'timeout in {out["phase"]}'
    except Exception as e:
        out['error'] = f'{type(e).__name__}: {e}'
    return out


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--limit', type=int, default=None)
    p.add_argument('--out-csv', default='/tmp/lean_batch_grades.csv')
    p.add_argument('--restore-monty', action='store_true',
                   help='After batch, regenerate Monty\'s data (BatchV3 '
                        'is left at last-SID state otherwise).')
    args = p.parse_args()

    from sidid import scan_directory
    res = scan_directory(os.path.join(ROOT, 'data', 'C64Music'),
                         recursive=True)
    paths = sorted(r['path'] for r in res
                   if 'Hubbard' in (r.get('player') or ''))
    print(f'{len(paths)} Hubbard SIDs found')
    if args.limit:
        paths = paths[:args.limit]

    print(f'Processing {len(paths)} SIDs serially via Lean V3 clone path...')
    print(f'(Lean rebuilds incrementally — only BatchV3 + exe per SID)')
    t0 = time.time()
    results = []
    for i, p_ in enumerate(paths):
        t1 = time.time()
        r = process_one(p_)
        dt = time.time() - t1
        results.append(r)
        marker = ('A' if r['grade'] == 'A' else
                  'B' if r['grade'] == 'B' else
                  'C' if r['grade'] == 'C' else
                  '·' if r['grade'] == 'F' else
                  '!')
        print(f'  [{i+1:3d}/{len(paths)}] {marker} {r["name"]:40s} '
              f'{r["grade"]} {r["snap_pct"]:5.1f}%  ({dt:.1f}s)'
              + (f'  ERR: {r["error"][:60]}' if r['error'] else ''),
              flush=True)
    elapsed = time.time() - t0
    print(f'\nTotal: {elapsed:.0f}s ({elapsed/max(len(paths),1):.1f}s avg/SID)')

    # Aggregate
    grade_counts = Counter(r['grade'] for r in results)
    print(f'\n=== Grade distribution ===')
    for g in 'ABCDF?':
        n = grade_counts.get(g, 0)
        bar = '█' * int(60 * n / max(len(paths), 1))
        print(f'  {g}: {n:4d}  {100*n/len(paths):5.1f}%  {bar}')

    a_or_b = [r for r in results if r['grade'] in 'AB']
    if a_or_b:
        print(f'\n=== Grade A/B SIDs ===')
        for r in sorted(a_or_b, key=lambda x: -x['snap_pct'])[:30]:
            print(f'  {r["grade"]} {r["snap_pct"]:5.1f}% {r["name"]}')

    with open(args.out_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['path', 'name', 'grade', 'snap_pct',
                    'top_div_regs', 'phase', 'error'])
        for r in results:
            w.writerow([r['path'], r['name'], r['grade'],
                        f'{r["snap_pct"]:.2f}',
                        ' '.join(f'{reg:02X}:{c}' for reg, c in r['top_diverging']),
                        r['phase'], r['error'][:200]])
    print(f'\nFull results: {args.out_csv}')

    if args.restore_monty:
        print('\nRestoring Monty data in BatchV3.lean... (NOT NEEDED; '
              'Monty has its own MontyV3.lean)')


if __name__ == '__main__':
    main()
