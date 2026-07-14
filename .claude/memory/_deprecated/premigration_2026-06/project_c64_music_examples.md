---
name: project-c64-music-examples
description: Commodore_64_Music_Examples.sid (Hubbard 1985) migration in progress. RE complete (see pipelines/companion/c64_music_examples/RE_NOTES.md). Two engine families bundled (not five as agent first claimed). Multi-session work pending — directory scaffolding in place; no extract/composer code yet.
metadata: 
  node_type: memory
  type: project
  originSessionId: ce060f8a-e40f-4b55-9551-2d4fc0bb3028
---

`hvsc84/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid` is the last unmigrated base-`Companion` SID. Rob Hubbard, 1985. PSID v2, 15 subtunes, 14782 bytes. Init `$087C`, play `$086D`.

**Status (DONE — session 17):** **ALL 15 SUBTUNES BYTE-EXACT** through the full composer pipeline (xa65 asm → PSID → writelog-verified against orig). The migration is complete.

Composer at `pipelines/companion/c64_music_examples/build.py`:
- `emit_subtune_asm(subtune)` — V1 family (subs 0/2/3) parameterized by `FamilyABindings` (dispatch variant, PWM variant, PW bounds, state offsets, init quirks).
- `emit_v2_subtune_asm(subtune)` — V2 engine (subs 4-14): different voice event router, AD/SR helper, gate flag, $0D-for-V3 song-end, different freq tables, 7-byte-per-voice state layout, no vibrato, increment PWM.
- `build_subtune_sid_b(1)` — Family B (sub 1): pragmatic pack of the original engine code + data at orig addresses (\$1119+) with a custom init at \$1000 (state-copy from snapshot) + play wrapper at \$1003 (mimics orig's \$086D-\$087D \$A2 swap so vibrato sees the right frame counter).

Final verification (15s capture per subtune):
  ALL 15 subtunes: 0 divergence, every reb write matches orig prefix.



  - Subs 0, 2, 3: emulated via `FamilyAEmulator` with per-instance bindings (dispatch variant, PWM variant, PW bounds). Each is its own hand-customized V1-router variant.
  - Subs 4-14: emulated via `V2Emulator` (different voice event router with AD/SR helper, no duration-nybble path, gate flag at $0384, $0D-for-V3 sets song-end at $0383).
  - Sub 0/2/3: full-song verified (2500/2500 plays each). Subs 4-14: 200/200 verified per sub.
  - Total: 2800/2800 plays across 14 subs match orig writelog.

Emulator code: `pipelines/companion/c64_music_examples/extract/engine_model.py`. JSON dumps: `pipelines/companion/c64_music_examples/_extracted/sub{NN}.json`.

**Architecture (verified):** Two engine families bundled in one SID.

- **Family A** (14 of 15 subtunes): same engine logic instantiated at 4 different addresses. Sub 0 → `$0903`, sub 2 → `$1D8B`, sub 3 → `$2A23`, subs 4-14 → shared `$33DB`. Each instance is byte-for-byte identical opcodes with different operand addresses pointing at different state regions and pattern data. Engine has per-voice phase counters, tempo counter, JSR-based note-step routines, zp pointers (`$1C/1E/20` for sub 0) reading pattern bytes. Pattern format: low bytes (< $09) = duration-like, $09-$0E = control events, ≥ $80 = "note with extended flag" (high bit masked off and routed slightly differently than the bare note value).
- **Family B** (sub 1 only): distinct engine at `$1119`. Pattern-jump-driven shape. Not yet RE'd in detail.

**Why:** Hubbard bundled a music-examples collection — the SID's purpose is demonstrating 14 example tunes through his canonical 1984/85 engine, plus 1 outlier using a different player technique.

**How to apply (next session):**

1. **DONE** ✓ — sub 0 emulator (200/200 + 2500/2500 full-song)
2. **DONE** ✓ — voice-event router decoded for both V1 (sub 0/2/3) and V2 (sub 4-14) variants
3. **TODO** — build extract path: per-subtune walk pattern bytes + state → USF. Currently dumps to JSON (`_extracted/sub{NN}.json`). Need USF schema design.
4. **TODO** — build composer asm. Will need TWO new emitter families: one for V1-router variants (sub 0/2/3 each have own quirks: vibrato/no_vibrato/bne_loop + sweep/increment PWM + custom PW bounds + custom state offsets) and one for V2-router (subs 4-14 share via dispatch-tables of stubs).
5. **DONE** ✓ — verified byte-exact for sub 0, 2, 3 (Family A V1) and subs 4-14 (V2)
6. **DONE** ✓ — extended to all 14 Family A instances
7. **TODO** — sub 1 (Family B) RE + emulator. Handler at `$1119`. Per-voice loop with X=0/1/2 (NOT SID-voice offsets 0/7/14). Uses `$1408,X` per-voice phase, `$1412,X` durations, `$1433/$1434` tempo, `$1436/$1439` per-voice ptrs lo/hi, `$143C+` data table. End-of-pattern is byte `$FF` (not `$8E` like Family A).
8. **TODO** — multi-subtune composer wrapper for all 15 (or 14 if sub 1 gets excluded).

**Budget estimate (revised after family collapse from 5→2):** 4-7 sessions, not 5-10 as originally feared.

**Directory layout (set up, ready for code):**
```
pipelines/companion/c64_music_examples/
├── RE_NOTES.md              ← full RE writeup
├── disassembly.s            ← auto-generated seed (107 bytes traced — most of binary is data)
├── __init__.py
└── extract/
    └── __init__.py
```

**Related:** [[reference_companion_etymology]] (sidid base-`Companion` fingerprint context), [[project_companion]] (Up_up_and_Away — same author, similar era, but completely different engine code despite shared fingerprint), [[feedback_full_decompile_hubbard]] (always disassemble init+play first).

**Don't forget:** the agent's first RE pass had table-indexing errors — it labeled subtunes by raw table index 0..15, but real PSID dispatch reads with `X = subtune + $0F` (subs 0..3) or `X = $13` (subs 4..14), so only entries 15..19 are used. The "sub 0 → $10E5" / "sub 15 → $0903" mapping in any stale notes is wrong. Verified via py65 `_run_init` + reading `$0878-$0879`.
