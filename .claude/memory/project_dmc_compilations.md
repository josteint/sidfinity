---
name: project_dmc_compilations
description: DMC files that pack N independent players + a per-subtune SMC dispatch wrapper (compilations) — a whole residue class; Abyssal_Karma is the first characterized
metadata: 
  node_type: memory
  type: project
  originSessionId: dc3e8ab6-14f1-45ad-97c8-053b066d511b
---

**DMC COMPILATIONS — one file, N independent DMC players, per-subtune dispatch.**
Characterized 2026-07-10 while fixing the first family-1 partial by path,
`MUSICIANS/B/Bayliss_Richard/Abyssal_Karma-Part_One.sid`. Ledger entry: C31.

## What it is
A single SID file packs **two or more fully-relocated copies of the SAME DMC v4
engine**, each with its OWN independent data pool (instruments, freq/wave/filter
tables, sectors, tracks, tune records). A small SMC wrapper at the PSID
init/play vectors dispatches per subtune:

```
init/play vector -> JMP wrapper
wrapper:  LDX subtune
          LDA base_hi_tab,X   -> STA <hi byte of BOTH the init and play JMP>
          LDA song_tab,X      -> A (the song# handed to the selected player)
          JMP selected_player
```

Abyssal_Karma: `base_hi_tab = [$80,$91,$91,$91,$91]`, `song_tab =
[$00,$00,$01,$02,$03]`. So subtune 0 -> (player@$8000, song 0); subtunes 1-4 ->
(player@$9100, songs 0-3). Player A ($8000) has 1 real song; player B ($9100)
has 4. Only ONE player runs per subtune -> the per-subtune write streams are
fully INDEPENDENT (unlike C27/C28 multi-SID, which run N players in PARALLEL on
N chips every frame).

## Why the current extractor gets it wrong
`factory._build_via_canon` base detection tries play-3 then LOAD. Both players
carry a valid canonical DMC jump table (`4C b+1D 4C b+85`); the LOAD-address
player (A) wins, so ALL subtunes get decoded from player A's tune table. sub0 is
genuinely player A song 0 -> **FULL**. Subtunes 1-4 read PAST player A's
1-record tune table into garbage (tracks -> `$FE` stops or out-of-image $3Cxx)
-> silence / off-image residue, diverge at frame 1. The masked-identity compare
does NOT catch it — A is a byte-valid player, just the WRONG one for subtunes
1-4. The live player B is the wrapper's JMP target ($9100), never considered.

Diagnosed via `siddump --memwatch` on the runtime track-ptr state (relocated
$1707->$9807) + `--pc-trace` (the live tune-record read is `LDA $9c3c,Y` at
$990D, i.e. player B's tunetab $9C3C — NOT the extractor's $8acf). py65
post-init does NOT reproduce this member's wrapper relocation (its $9C3C bytes
disagree with libsidplayfp), so `data_post_init` can't rescue it; libsidplayfp
memwatch/pctrace is the ground truth.

## Detection signature
Image contains **>=2 canonical DMC jump tables** at different bases
(`4C b+1D 4C b+85`). Bayliss folder alone = **15 members** (Balloonacy = 4
players, Lane_Crazy = 4, Defuzion_3 = 3, Heavy_Metal_Deluxe_beta = 3, …); the
pattern spans the DMC corpus. Confirm with the SMC dispatch wrapper (per-subtune
JMP-hi-byte patch + song# from `LDA tab,X`).

## Analogues
- FC **Adrenalin** ([[project_adrenalin]]) — "a COMPILATION, 3 engines + 4
  independent data pools".
- **5 Title Tunes** ([[project_five_title_tunes]]) — multiple independent songs
  UNIFIED into one engine via globally-renumbered instruments + per-subtune
  params. This is the likely playbook for the DMC merge shape.
- NOT C27/C28 multi-SID (parallel chips) — see the distinction above.

## BUILT 2026-07-10 — unified-merge (user chose "build compilation support now")
`pipelines/dmc/v4/compilation.py`. Extract-side only, NO USF/composer change
(the merged model flows through the ordinary `model_to_usf` -> composer). Wiring
in `factory.dmc_v4_config(base_override=)`, `to_usf.write_dmc_compilation_usf`,
and both `dmc_build_one` + `dmc_family_batch` (with a single-player fallback).

Pipeline:
1. `detect_compilation` — >=2 canonical JT bases + static wrapper decode (the
   two X-indexed `LDA tab,X` tables: base-hi + song) -> per-subtune (player,
   song) map. Requires >=2 DISTINCT players used (else None -> single-player).
2. `dmc_v4_config(base_override=B)` — extract each player standalone. Canon path
   for UNIFORM relocation (Abyssal_Karma); on its code-identity mismatch, the
   signature-based `_build_via_dataflow(base_override)` handles NON-uniformly-
   relocated players (packer moves state scratch — e.g. $100C active-flag array
   — independently of the code). Also mask the all-off/sfx JT entries
   ($1006-$100B) in the canon compare for base_override (packers point them at a
   SHARED all-off routine; write-stream-irrelevant).
3. `merge_models` — shared freq/vibdepth (verified identical), instruments
   renumbered+deduped into one <=28 pool, songs reordered by PSID subtune, rows'
   instr rewritten. FILTER-DEF: strategy-1 SHARE the start player's 17-record
   window when non-start defs coincide; strategy-2 COMPACT-remap+dedup on
   conflict, gated on no OVERRUN (C2 repeat<=5) and <=16 distinct.

Per-subtune master_vol rides `DmcSong.master_vol`. Idle priming is global-only
but verified UNREAD for this cluster (building player B with player A's priming
still verified FULL) — a priming-reading member would show partial, not wrong.

## Regression safety (PROVEN)
Census of all 5401 family-1 members: 17 compilations, ALL previously
partial/error/unsupported, NONE full. The >=2-distinct-player-dispatch signature
never coincides with a working single-player member. Both build paths fall back
to single-player on any merge/compose failure -> an unmergeable compilation
keeps its prior status.

## Results (2026-07-10)
- **FULL:** Abyssal_Karma (2p/5sub), Sharkz (2p/6sub), Para_Lander_DX,
  Race_n_Smash, Chwat, Poing_Ultra (compact-remap), **Balloonacy (4p/7sub —
  round 71)**. Goldrake: sub0 FULL, sub1 a separate residual divergence
  (dispatch correct).
- **PER-PLAYER `locate` FIXED (round 71, ledger C31):** the "edge player fails
  dataflow locate" residue was a co-packed player uniformly relocated for
  code+data-tables but keeping STATE at the canonical $1xxx AND carrying
  DEAD-CODE JMPs into a sibling player's code — the static trace bleeds into the
  sibling → every signature matches twice → ambiguous → None. FIX:
  `dataflow.locate(region=(base, base+0x900))` bounds the trace to the forced
  player's own code window (base_override-only). Balloonacy verified FULL; the
  region-bounded locate LIKELY also unblocks Lane_Crazy/Wiz_Max/Goldrake_plus_2/
  Mystery/Rogue_Ninja (unverified — next batch). Diagnose which code actually
  runs with `siddump --pc-trace --subtune N` (N is 1-BASED).
- **INSTRUMENT-POOL fit (round 71, ledger C8):** the 4-player merge overflowed
  the 28-inst 5-bit cap (29>28). `merge_models` now dedups on all fields EXCEPT
  `offtable_freq` (a C6 reachability artifact, not intrinsic content) and UNIONs
  the records per merged id (collision → distinct). 29→28. This is the general
  lever for instrument-overflow compilations (may help Heavy_Metal's 30>28).
- **RESIDUE (fall back, 0 regr):** 3 filter OVERRUN (repeat>5, need an
  adjacency-preserving window — Zap_Zone/Protox-1/Mission_Moon); 1 instrument
  overflow (Heavy_Metal 30>28 — retry with the offtable-union dedup). Next
  steps: (a) an overrun-adjacency-preserving filter window (or per-player
  contiguous blocks); (b) DUAL-PLAYER composer emit for the unmergeable tail.

## Diagnosis method (for the next compilation)
`siddump --memwatch` on the runtime track-ptr state + `--pc-trace` of the live
tune-record read gives ground truth (py65 post-init does NOT reproduce a
relocating wrapper). Ledger C31.

**Queue note:** `tools/dmc_next_partial.py` returned Abyssal_Karma first; now
FULL, so the queue advances. See [[project_dmc]].
