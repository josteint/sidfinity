---
name: project_adrenalin
description: "Adrenalin (HeatWave) — the 3rd Future Composer canary, IN PROGRESS/stalled. Non-Tel FC tune to diversify away from Hawkeye+Cybernoid_II (both Jeroen Tel). Structurally hard: inline-load PSID, self-decompressing/relocating engine, multiple per-subtune engine instances. Full disassembly.s + 649-line RE_NOTES.md done; FCConfig has a new runtime_slot subtune_layout. BLOCKED: compose_fc_asm_featuredriven doesn't know runtime_slot, so no rebuild SID / no verdict yet."
metadata: 
  node_type: memory
  type: project
  originSessionId: fea5d0c1-61d2-49f9-8e14-4e5916b95622
---

**SID:** `hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid` (Marvin Severijns & M.
de Bree). MoN/FutureComposer per sidid. 4 subtunes, 9:25. PSID load=$0000
(inline-encoded → real load $50E0), init=$50E0, play=$50E3.

**Why:** 3rd FC family canary. Hawkeye + Cybernoid_II are both Jeroen Tel;
their feature mix overlaps. Adrenalin is the only non-Tel candidate in
`docs/canary_picker.md` row 3 of engine #4 — proves the feature-driven FC
composer generalises beyond Tel's subset.

**Authoritative notes:** `pipelines/future_composer/adrenalin/RE_NOTES.md`
(649 lines) + hand-annotated `disassembly.s` (engine A). READ THOSE FIRST.

## What makes it structurally distinct (vs Hawkeye/Cyb II)
- **Inline-load PSID** — first 2 body bytes hold the real load ($50E0).
- **Self-decompressing engine** — init copies packed source data from high
  addrs into low memory `$17xx-$1Bxx` (zeros in the raw binary) and unpacks
  engine code into `$7Axx-$81xx`. The raw binary at the load addr is a
  decompressor + packed data, NOT the runnable engine.
- **Multiple engine instances per subtune** (init copy table `$514E-$5175`):
  sub 0 → engine A at `$7A00` (play `$7A06`); subs 2/3 → relocated engine at
  `$1000` (play `$1006`); **sub 1 is the outlier** (play `$1021`, post-init
  data at engine-A addrs looks invalid) — likely a shim/SFX subtune.
- Subs 0/2/3 share sequence-pointer addrs + speed, yet HVSC lists 4 distinct
  durations → the per-subtune copy likely writes the same pointer addrs with
  DIFFERENT pointed-to sequence/pattern bytes. UNCONFIRMED — verify at the
  byte level before committing to single- vs multi-subtune scope.

## Key addresses (engine A, post-init, from RE_NOTES)
lonote $17E3, hinote $1842, per_subtune_speed $18A1 (`02 02 01 01`),
subtune seq-base ptr table $18A5(lo)+$18A7(hi), 6-byte runtime per-voice seq
slot $18B5, instr_records $19AC (8B/inst, Hawkeye layout), pattern_ptr_table
$1BA0 (2B/entry). lonote source found in raw binary at `$68B3`.

## THE BLOCKER (last commit 17f7618)
`compose_fc_asm_featuredriven` only knows `subtune_layout` ∈
{`flat_seqtabel`, `smc_template_with_sfx`}; Adrenalin's config uses a new
`runtime_slot` variant it can't emit → no rebuild SID → no
`verify_featuredriven` verdict. Two ways out (per RE_NOTES §"Composer build
is BLOCKED"):
1. Teach the composer `runtime_slot` (emit a songinit that copies per-subtune
   data into the runtime slot from a synthesized flat seqtabel).
2. **(simpler, recommended)** Keep `runtime_slot` out of the composer: have
   the extract path synthesize a flat 4-record `seqtabel` from each subtune's
   post-init runtime slot, set `subtune_layout='flat_seqtabel'`, reuse the
   existing composer path. Per the CORE TENET the rebuild needn't mirror the
   decompressor — only the writelog.

## Resume order
1. Confirm whether subs 0/2/3 differ at the sequence/pattern byte level
   (decides single- vs multi-subtune scope; sub 1 deferred regardless).
2. Apply option 2; build; `find_first_divergence`; `verify_featuredriven`.
3. Add to `tools/regression.py::regress_future_composer` canaries when FULL.

## Related
[[project_fc_principled_composer]] (FC de-verbatim work),
[[feedback_check_existing_engine_docs]] (Step 0 protocol),
[[feedback_writelog_divergence_recipe]]. FC docs:
`pipelines/future_composer/docs/wiki_fc_v41_manual.md` +
`csdb_fc_v4_player_disasm.md`.
