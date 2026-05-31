---
name: usf3-universal
description: "USF v3 — engine-name-blind, self-contained USF. All 12 Hubbard '85 engines + 4 Companion strains build byte-exact through the universal codegen with no `engine: <name>` dispatch."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

USF v3 is the principled endgame: a .usf file that carries everything
the codegen needs to produce its SID, with no engine-name lookup. The
`engine:` token in a v3 file is metadata only.

## What v3 USFs carry (in addition to v2 content)

- `freq_table { ... }` block — the per-tune 320-byte freq region
  (192 musical bytes + 128 engine state/scratch). Normalised at
  extract time so engine-specific overlap offsets land at canonical
  positions; the codegen reads at fixed offsets.
- Named `params { }` overrides — every mechanism knob that deviates
  from the canonical Commando flavor (e.g. `vib_onset: 8`,
  `master_vol_subtrahend_voice: 2`, `tie_preserves_slide: true`).
  No opaque integers; every field is named.
- Per-subtune `params { }` for compound-engine deltas (5_Title_Tunes:
  per-sub speed_ctr_init / incby2_step / incby2_late_gate /
  tick_divider / voice_start).
- `state_layout { ... }` block — for engines (Human Race) whose
  off-table-arp statebuf differs from Commando's 3-voice layout.
  Each slot is named: `scalar <off> const $XX` or
  `per_voice <off> var <name>`.
- `digi_player: <name>` in params + a small in-process registry — the
  residual named coupling for tunes with a digi subengine. The player
  bytes (6502 code) stay in engine_constants; only the registered
  name appears in the USF.

## Build path

`pipelines/hubbard/usf3_build_from_usf.py` :: `build_from_usf3`.
Reads only from the USF, no `ENGINE_CONSTANTS[usf.engine]` lookup.
Validates `usf.version == 3` and `freq_table is not None`.

## Verified

12 Hubbard '85 engines × 89 subtunes byte-exact:

- Commando 19/19, Devils Galop 1/1, Monty 19/19, Action Biker 3/3,
  Chimera 4/4 (incl. 2 digi), Human Race 5/5, Hunter Patrol 1/1,
  Thing on a Spring 17/17, One Man and his Droid 14/14, Battle of
  Britain 1/1, Confuzion 1/1 — `verify_all`.
- 5_Title_Tunes 4/5 — `compare_instruction_stream`. Sub 2 fails
  identically to baseline (pre-existing skip_init alignment).

## Grammar additions (v2 → v3)

Three new optional blocks:

```lark
freq_table_block: "freq_table" "{" byte_list "}"
state_layout_block: "state_layout" "{" sl_field+ "}"
sl_field: "n_voices" ":" INT
        | "scalar" INT ("const" byte | "var" CNAME)
        | "per_voice" INT ("const" byte | "var" CNAME)
```

Plus init becomes `init_voice*` (zero or more) so v3 USFs can ship
empty `init { }`.

## What's still v2

- Companion pipeline USFs (4 strains: bowden_canonical, henrys_house,
  yes_tune, clever_music). Different pipeline architecture; would
  need its own v3 migration if/when worthwhile.
- HVSC's on-disk `Commando.usf` etc. files. The v2 dispatched-build
  path still works on them; conversion to v3 .usf files on disk is
  a separate step (the in-memory v3 round-trip is proven).

## Related

- [[feedback_usf_representation_principle]] — the driving principle
- [[project_hubbard_principled_usf]] — Phase 1-3 (preparation)
- [[project_companion_principled_usf]] — Phase 1 (Companion strains)
