Investigate the highest-scoring F-grade song and fix its root cause.

This is the standard bug investigation methodology — see memory `feedback_bug_investigation.md`.

## Procedure

1. Find the highest-scoring F-grade song (closest to Grade C threshold)
2. Run the pipeline, get the comparison
3. Find the first frame with `note_wrong` or `wave_wrong`
4. Identify: which voice? which register? what's the expected vs actual value?
5. Trace backward: is the USF data correct? Is the codegen correct?
6. Classify: decompiler bug, codegen bug, missing USF feature, or comparison artifact?
7. Fix the root cause (not the symptom)
8. Run regression — zero regressions allowed
9. If the fix helps multiple songs, run batch test and update benchmark

## Key principle
Fix bugs, not symptoms. Don't widen tolerance to hide real bugs.
One root cause fix often improves dozens of songs.
