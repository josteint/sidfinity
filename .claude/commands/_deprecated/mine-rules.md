Mine the trace equivalence relation for new tolerance rules.

This is the highest-ROI approach for increasing Grade A count (+393 songs from 3 rules so far).

## Procedure

1. Sample 50 Grade B songs across all engines (closest to Grade A threshold)
2. For each, run the pipeline and get the comparison results
3. Classify every `note_wrong` and `wave_wrong` frame:
   - What's the waveform? (gate on/off, which waveform bits?)
   - What's the frequency difference? (vibrato range? octave? unrelated?)
   - Is it a timing shift? (does the value appear ±5-20 frames away?)
   - Is it during release? (both gates off?)
4. Find patterns: if >50% of songs share the same type of "wrong" that's actually inaudible
5. Propose a new tolerance rule in sid_compare.py
6. Test broadly — does Grade A count increase across all engines?
7. Run full regression — zero regressions allowed
8. If positive: commit, run full batch, update benchmark.csv and CLAUDE.md

## Key files
- `src/sid_compare.py` — the comparison function
- `src/formal/trace_equivalence.py` — formal version (update to match)

## Check mathematical properties after any change
- Reflexivity: T ≈ T (must always hold)
- Symmetry: compare(A,B) == compare(B,A)
- Grade monotonicity: removing a rule never improves the grade
