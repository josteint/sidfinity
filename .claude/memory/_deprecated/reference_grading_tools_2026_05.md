---
name: Grading + discovery tools built May 2026
description: Pointers to writelog grader, batch grader, discovery freq-table tool. Use these for honest measurement, not sid_compare.py.
type: reference
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
**Tools built this session for measuring pipeline quality and finding
landmarks:**

`src/writelog_grade.py` — replaces sid_compare.py for "is this
rebuild correct" questions. Compares per-frame snapshots from
siddump --writelog with audibility mask for known hardware-ignored
bits (pulse_hi 4-bit, filter cutoff lo 3-bit). Calibrated:
  - Lean V3 perfect Commando: 98.4% snapshot match → A
  - Broken rh_to_usf rebuild: 0-1% → F
  - Threshold A ≥ 98% is acknowledged-heuristic; for "no false
    positives ever" needs the Lean comparator. For grinding phase
    it's adequate signal.

`src/batch_grade_hubbard.py` — runs writelog grader on every
Hubbard-engine SID in HVSC (285 found via sidid). Outputs per-SID
grade + clusters failures by top-diverging-register signature.
Use after every meaningful pipeline change to confirm impact.

`src/discover_freq_tables.py` — uses the engine-agnostic discovery
script (src/sidxray/discover.py) to find freq tables across all
Hubbard SIDs. Result: 249/285 vs rh_decompile's 40/285. Runs in
~30s on 285 SIDs (32 workers). Cached memtraces in
/tmp/freq_disc_traces/.

`src/sidxray/discover.py` — the engine-agnostic discovery
infrastructure. Combines static 6502 disasm (from PSID's init/play
entries) with dynamic siddump --memtrace. Discovers code regions,
data tables, role labels via SID-register dataflow, struct sizes,
pointer-table pairs, and pattern regions via pointer dereferencing.
Used as primitive layer for landmark detection across engines.

`src/sidxray/discover_to_usf.py` — Option A demo: discovery for
landmarks + rh_decompile for parsers + rh_to_usf for interpretation.
Showed that discovery COULD drive the pipeline if extended; current
state proves the discovery layer is structurally sound.

**Do not trust sid_compare.py for verdicts.** It returns Grade A on
audibly-broken rebuilds (the false-A trap). Use writelog_grade.py.
sid_compare's per-voice diff classification is useful for *human-
readable diagnosis* of WHICH register diverged, not for grading.
