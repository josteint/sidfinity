---
name: project-usf-pitch-naming-semantics
description: "USF note names (C-5, B-7, …) are POSITIONAL — labels for indices into the tune's freq_table, not absolute pitch claims. Within a tune this is perfect; across tunes the same label can mean different actual pitches (e.g. Hubbard's entry 95 is ~60 cents flat). Endgame question: keep positional and document, or make frequency-normative (extract assigns closest 12-TET name) — bring up when nearing end of HVSC→USF migration."
metadata: 
  node_type: memory
  type: project
  originSessionId: 5de7672a-c130-4ad2-aabb-e29393a10065
---

USF note names work positionally. `C-5` in a USF means "semitone-60-relative index 60 in this tune's freq_table," not "523.25 Hz." Both extract and composer use `name ↔ semitone ↔ table-index` purely as indexing — neither side measures or asserts a frequency.

This is leak-free WITHIN a single tune: the freq_table travels inline with the USF, so the same bytes get read back out, and the rebuild plays the same pitches as the original. Deviation from strict 12-TET (e.g. Hubbard's entry 95 plays ~59 cents flat at ~3807 Hz vs 12-TET's ~3938 Hz) is preserved automatically.

The semantic ambiguity shows up across tunes / engines:

- Two USFs both say `B-7` but sound at different pitches if their freq_tables differ at index 95.
- A reader (musician or model) sees `B-7` as one token but the underlying pitch varies by tens of cents at the top of the range.
- For ML training specifically: a model conflates engine tunings unless it also reads the freq_table as auxiliary input, OR all freq_tables are normalised.

Two clean design options for the endgame slimming pass:

1. **Keep positional, document the leak.** Cheap. Downstream consumers (ML pipeline, notation export) read the freq_table when they need real frequency. No audio change, no rebuild break.
2. **Make names frequency-normative.** Extract maps each table entry to its closest 12-TET name — e.g. Chimera's entry 95 might write as `A#7` instead of `B-7` since 3807 Hz is closer to A#7 than B-7. Names become musically honest but no longer match table positions, so the pattern-byte encoding gets a name→index lookup that's per-tune (or per-table). Bigger refactor; changes what a USF note *means*.

**Why:** The user flagged this on 2026-06-02 during the section-by-section USF walkthrough. We were going through Chimera's freq_table and computed the 59-cent flatness at index 95. The user explicitly asked for a flag so we revisit it when the migration phase settles.

**How to apply:** Raise this when the USF schema-slimming endgame discussion starts (see [[project-usf-ml-optimality]] for that timing — not before HVSC→USF coverage is largely complete). Don't propose mid-migration: the choice between positional and frequency-normative names is a semantic change to USF, would touch every extract + composer + tokenizer, and shouldn't be conflated with rebuild-regression risk. Pair it with the freq_table split discussion (engine-shared pitch table vs per-tune spillover).
