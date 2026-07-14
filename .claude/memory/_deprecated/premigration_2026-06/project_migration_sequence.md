---
name: project-migration-sequence
description: "User's stated migration sequence as of 2026-06-02. Five phases in strict order — (1) finish Companion SIDs, (2) finish rest of Rob Hubbard's SIDs, (3) all OTHER SIDs that use Hubbard's '85 engine, (4) freq_table spillover decomposition refactor (Hubbard '85 only), (5) instrument representation ML-target refactor (all engines). Phases 4+ are the slimming-endgame triggers."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5de7672a-c130-4ad2-aabb-e29393a10065
---

The user laid out the next phase of work as a five-step sequence on 2026-06-02:

1. **Finish Companion SIDs.** Wraps up the `pipelines/companion/` family (Up_up_and_Away, Bowden-canonical, Clever_Music, Henrys_House, Yes_Tune, Melonmania, plus whatever's still in flight — Jay_Derrett, Commodore_64_Music_Examples). See [[project-companion]], [[project-bowden-canonical]], [[project-clever-music]], [[project-henrys-house]], [[project-yes-tune]], [[project-jay-derrett]], [[project-c64-music-examples]].
2. **Finish the rest of Rob Hubbard's SIDs.** Whatever Hubbard '85 (and adjacent) SIDs in HVSC are not yet byte-exact. Existing core at `pipelines/hubbard/`.
3. **All OTHER SIDs that use Hubbard's '85 engine.** Non-Hubbard composers who built tunes on Hubbard's engine — presumably matched via sidid's "Hubbard_Rob_or_Compatible" or similar in `hvsc84.db`. Goes through the same shared core; per-tune config + extract only.
4. **Refactor the extended part of Hubbard's freq_table.** Decompose the 128-byte spillover (notenum tables, SFX sweep state, drum data, off-table arpeggio extensions, per-instrument scratch) into typed USF schema fields, engine by engine. **Hubbard '85 only — bounded scope.** End state: every Hubbard '85 USF carries only the 192-byte pitch table — and that pitch table can then be hoisted to engine_constants. See [[project-usf-ml-optimality]] for the broader slimming umbrella, and [[reference-usf-v2-format]]:113-116 which already flags this as known incomplete.
5. **Instrument representation ML-target refactor.** All engines — unpack packed bytes (waveform, ADSR) into named features, add descriptive musical forms (attack_ms, sustain_level, initial_duty) alongside or in place of raw register values, hoist engine-fixed PWM bounds to engine_constants, default-elide no-op blocks, rename register encodings to musical concepts (release_ctrl=$40 → silence_on_release=true). Punch list in [[project-usf-instrument-ml-target]]. Broader blast radius than phase 4 (touches every engine), so sequenced after phase 4 so phase 4 validates the slimming methodology first.

**Why:** This sequence puts the slimming refactors at the point where they have maximum leverage and minimum risk. By the time phases 1-3 are done, every targeted SID in HVSC is byte-exact through the current schema — which means phases 4 and 5 each have a comprehensive regression set to validate against, and the schema stops being a moving target. Doing either refactor earlier would mean reworking it for every newly-migrated engine. Phases 4 and 5 are sequenced (not bundled) because their blast radii differ: phase 4 is Hubbard '85 only; phase 5 touches every engine. Keeping them separate lets any regression be attributed to one or the other cleanly.

**How to apply:** When asked "what's next?" default to the next item in this sequence. When proposing work, propose within the current phase, not the next one. Specifically, do NOT propose freq_table spillover decomposition (phase 4) or instrument representation refactor (phase 5) work until phase 3 is complete — the timing rationale in [[project-usf-ml-optimality]] applies: mid-migration schema changes couple unrelated risk surfaces. Adjacent: [[project-usf-pitch-naming-semantics]] (positional vs frequency-normative naming) is a separate slimming question that pairs naturally with phase 4-5 timing.
