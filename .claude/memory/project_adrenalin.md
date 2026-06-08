---
name: project_adrenalin
description: "Adrenalin (HeatWave) — intended 3rd FC canary, IN PROGRESS/diagnosis. DEEP DIAGNOSIS 2026-06-07: it's a COMPILATION — THREE distinct engines + FOUR independent data pools in one PSID. Sub 0 = engine A @ $7A00 (canonical FC); subs 2/3 = engine A relocated to $1000 (proven byte-for-byte reloc), each its own pool; sub 1 = a DIFFERENT engine @ $1021 (4% code match). Every subtune has its own freq/instr/pattern/sequence (NOT shared-pool FC multi-subtune). Sub-0-only = a clean FC canary (just needs runtime_slot→flat_seq_table emission); full Adrenalin needs multi-independent-song FC support (new schema+composer feature). User chose DIAGNOSE-ONLY, not build."
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
- **THREE distinct engines + FOUR independent data pools** (CONFIRMED
  2026-06-07; full table in RE_NOTES "DIAGNOSIS" section):
  - sub 0 → engine A @ `$7A00` (canonical FC, full features).
  - subs 2/3 → engine A *relocated* to `$1000` (entry `$1006`) — PROVEN: sub2
    nolengset `$128B` == engine A `$7C8B` byte-for-byte, addrs reloc `$7A`→
    `$10`. Sub2≈sub3 engine code (99%); different data.
  - sub 1 → a DIFFERENT, smaller engine @ `$1021` (only 4% code match to
    subs 2/3; `DEC $1090` speed ctr, `JSR $1226/$1225`). NOT identified as FC
    yet; needs its own RE.
  - Shared IRQ harness `$1E00-$1EFF` (100% identical): installs IRQ, banks
    `$01=$37`, idle-spins `JMP $1EA5`, calls play via `JMP ($1E04)`→`$50E3`.
- **Every subtune has an INDEPENDENT pool** (CONFIRMED): freq/instr/
  pattern_ptr/pattern/sequence bytes ALL differ between subs 0/2/3 (sub2&3
  share only the freq table). They sit at engine A's SAME runtime addresses
  but each subtune's init copies different VALUES. So these are 3 separate FC
  songs reusing engine A's design — NOT shared-pool FC multi-subtune.
- **extract(ADRENALIN) only captures sub 0's pool** for the shared fields
  (freq/instr/patterns from sub 0's post-init mem), so subs 2/3 in that
  FCSong carry sub 0's WRONG data. Only sub 0 is faithfully extractable today.

## Key addresses (engine A, post-init, from RE_NOTES)
lonote $17E3, hinote $1842, per_subtune_speed $18A1 (`02 02 01 01`),
subtune seq-base ptr table $18A5(lo)+$18A7(hi), 6-byte runtime per-voice seq
slot $18B5, instr_records $19AC (8B/inst, Hawkeye layout), pattern_ptr_table
$1BA0 (2B/entry). lonote source found in raw binary at `$68B3`.

## PROGRESS 2026-06-07 (cont.) — composer UNBLOCKED; sub-0 init divergence
- `compose_fc_asm_featuredriven` normalizes `runtime_slot`→`flat_seq_table`
  at entry (emission only; extract keeps runtime_slot). Adrenalin config:
  `emit_data_from_usf=True`, `load_addr=0x0E00` (engine below the fixed
  $17E3+ data tables). It now BUILDS (5975 B). Cyb II 2/2 + Hawkeye 12/12
  unaffected.
- Sub-0 still FAILS frame-exact: engine A has a MULTI-FRAME init the generic
  FC composer doesn't reproduce. ORIG: f0=`$D418=$0F` only; f1=78-write
  `$01,$00` descending reset sweep across all SID regs; music from f2.
  REBUILD: f0=generic FC init; music from f1 → off by one frame, diverges at
  pos 0 (vblank, speed=0, so no CIA issue). Next: an FCConfig "init_style"
  knob emitting engine A's f0/f1 init shape (disasm $7A00 first-play path for
  the exact 78-write sweep). Full detail in RE_NOTES "PROGRESS" section.

## PROGRESS 2026-06-07 (cont. 3) — layout decoupling DONE; now per-voice notes
- Layout decoupling SHIPPED (commit 7984e88). The cont-2 "engine+state overlaps
  data" guess was WRONG. Real cause: original packs data tables so tightly that
  emitting at orig addresses OVERLAPS (pulsetabel/vibtabwait vs instruments) →
  xa65 backward `* =` desyncs file vs CPU addr by $38 → d4point (per-voice SID
  offset table) loads as zeros → all voices write V1. Fix: new FCConfig
  `contiguous_data_layout` (Adrenalin-only) packs data tables contiguously +
  rewrites cfg addrs. d4point survives; voices fixed.
- `nextvoice_write_order` → (2,3,4,0,1) (orig writes PW before ctrl/freq).
- Divergence progression: pos 1→50 (init_style)→51 (voices all-V1)→55 (layout
  decoupling)→70 (nextvoice). CURRENT: pos 70 = V1 note content (orig new note
  freq $02CC+AD/SR/PW/ctrl; rebuild different freq, no AD/SR — held-vs-new-note
  or pitch/sequence mismatch). Per-voice musical accuracy now; structurally
  sound (flat lengths 4941 vs 4953). Cyb II 2/2 + Hawkeye 12/12 unaffected.

## PROGRESS 2026-06-07 (cont. 2) [HYPOTHESIS WAS WRONG — see cont. 3]
- `init_style='fc_clear_sweep'` knob (commit a1bbba2) emits engine A's $7AE2
  init sweep. Adrenalin sub-0 init now byte-exact (full-flat pos 0..50); first
  divergence at pos 51 (music).
- Music divergence ROOT-CAUSED: rebuild writes ONLY V1 ($D400-$D406); V2/V3
  never. Per-voice SID offset `d4point` (.byt $00,$07,$0E at $2410) reads 0 at
  runtime — the BUILT .sid has `00 00 00` at $2410. Engine+state block from
  load_addr=$0E00 is ~5.6KB, OVERLAPS the data tables ($17E3) + music_data;
  the `* =` section emission zero-fills over the state region. NOT ok2 (d4point
  is before tabcount). Composer requires load_addr < data-section addrs, but
  engine+state (~5.6KB) doesn't fit below the fixed-low $17E3 tables.
- NEXT (composer layout, needs design): decouple extract data addrs ($17E3,
  read orig) from emit placement so emit_data_from_usf puts data tables ABOVE
  the engine+state (like Cyb II/Hawkeye whose data sits above load_addr). Then
  re-verify from pos 51. Full detail in RE_NOTES "PROGRESS ... (cont. 2)".

## THE BLOCKER (last commit 17f7618) — RESOLVED (see PROGRESS above)
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
