---
name: Hubbard strategy May 2026 — discovery-augmented das_model_gen
description: Current direction for "most Hubbard SIDs sound right". Generalize das_model_gen via discovery script for landmarks. Do NOT pursue rh_to_usf incremental bug fixing.
type: project
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
**Current direction (decided 2026-05-09):** generalize
`src/das_model_gen.py` to handle any Hubbard-engine SID, using the
engine-agnostic discovery script (`src/sidxray/discover.py`) to find
the per-song landmarks rh_decompile misses.

**Why this path, not rh_to_usf bug fixing:**
- Writelog grader baseline (committed `1e54d89`): 0/285 Hubbard SIDs
  get Grade A through `rh_to_usf` + Python `codegen_v3` pipeline.
  Even Commando is 1.0% match through that path.
- The byte-perfect Commando we have comes from `das_model_gen.extract`
  → CommandoV3.lean → Lean `CodegenV3.lean`. Different code path.
- `das_model_gen` has CORRECT structural understanding for Commando
  but is hardcoded to it (SID_PATH, ft_base=0x5428, etc.).
- Generalizing das_model_gen requires: per-song freq_table_addr,
  instrument table addr, song table addr, pattern data location.
  rh_decompile finds these for ~14% of Hubbard SIDs.
- Discovery script raises freq-table coverage to 87.4% (commit
  `6fb372c`). Other landmarks likely similarly lifted.

**Why:** Avoids the multi-month bug-by-bug grind through `rh_to_usf`.
Builds on a known-correct path (das_model_gen) instead of fixing a
known-broken one.

**How to apply:** When extending Hubbard support, augment
`das_model_gen.extract` with discovery-derived landmarks rather than
fixing `rh_to_usf`. Step-by-step plan:
  1. Build `discover_hubbard_landmarks(sid_path)` in src/ that returns
     all landmarks (freq_table, instr_addr, song_table, etc.) using
     discovery techniques. ~1-2 days.
  2. Parameterize `das_model_gen.extract` to take a SID path and
     landmark dict instead of hardcoding Commando. ~1-2 days.
  3. Add `(T, I, S) → USF Song` converter (gen_commando_v3.py has
     the logic but emits Lean; refactor to also emit Python USF). ~1 day.
  4. Re-run batch grader on all 285 Hubbard SIDs. Expect substantial
     improvement from 0/285 baseline.

**Disagreement note for freq-table discovery:** when both rh_decompile
and discovery find a freq table, discovery is consistently +95 bytes
(=$5F) higher. Discovery finds freq_hi base; rh_decompile finds
freq_lo base. To reconcile, look ±95 bytes from discovery's address
to find the lo/hi pair.
