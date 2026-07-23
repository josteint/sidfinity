---
name: project_dmc_compilations
description: DMC files that pack N independent players + a per-subtune SMC dispatch wrapper (compilations) — a whole residue class (ledger C31). Unified-merge built; 7 members FULL incl. the heterogeneous dmc_sfx case (Canyon 13/13)
metadata: 
  node_type: memory
  type: project
  originSessionId: dc3e8ab6-14f1-45ad-97c8-053b066d511b
  modified: 2026-07-23T09:38:50.994Z
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
- **RESIDUE (fall back, 0 regr) — as of round 87:** 2 filter OVERRUN
  (repeat>5, need an adjacency-preserving window — Zap_Zone/Protox-1); 1
  third player layout (Black_It, `base_override_not_player: $1000`). The
  instrument-overflow class is CLOSED (rounds 86+87). Next step: an
  overrun-adjacency-preserving filter window (or per-player contiguous
  blocks).

## ✅ INSTRUMENT CAP — it was the ORIG's, not ours (round 86, 2026-07-22)
`Heavy_Metal_Deluxe_beta` (3 players, 30 merged instruments) was the
documented "30 > 28 instrument overflow" residue. The 28 came from DMC's
EDITOR row encoding (5-bit `$60+id`), which our composer does not use — it
emits its own pattern format where the slot is a full operand byte. The
composer's real bound is its widest id-scaled index, fx_pulse's
`lda cinst,x / asl×3 / adc pwphase,x / tay` (8-bit, stride 8) ⇒ **32**.
Cap raised to 32, nothing else changed, **3/3 FULL** (222245/117622/164355).
Zero-regression by construction (only fallback members can change path; all
6 were partial) — verified over all 22 detected f1 compilations: 0 regressed.
Ledger C8 gained the "first ask WHOSE cap it is" sibling.

## ✅ PAST THE CAP — widen the index (round 87, 2026-07-22)
`Lane_Crazy` (4 players, 6 subtunes, **39** merged instruments) — **6/6 FULL**.
Raising the constant is only half the job: fx_pulse reaches an instrument's
step records with `id*8 + pwphase`, an 8-bit index, so ids ≥32 ALIAS onto
instrument 0's records (subs 4+5 diverged at V1 PW lo, write 24). The fix is
C8's "widen the composer's own index", in the cheap form: above 32 instruments
pack the records at their TRUE width (6 — the 8 existed only to make the index
a shift) and give each instrument a base byte (`ldy cinst,x / lda istepbase,y /
adc pwphase,x`). Index stays 8-bit, cap becomes 256/6 = **42**, and the lookup
is one cycle CHEAPER than the three shifts.
- GATED on the count ⇒ everything at ≤32 emits identical code. Proof: all
  **5240 stored f1 members rebuild BYTE-IDENTICAL** from their stored `.usf`
  (which re-confirms the C20 fifth-layer invariant corpus-wide in the same
  pass). 22 compilations re-verified: 0 regressed / 1 gained.
- `dual_freq_generator` + >32 instruments is REFUSED, not approximated — the
  wedge's off-the-end reads are stride-8 POSITIONS with no compact-layout form
  (empty intersection today: single-player probe vs merged compilation).
- Per-song instrument WINDOWS (the other candidate design — each subtune runs
  one packed player and uses ≤16 here) were NOT needed and are not implemented;
  revisit only if a merge exceeds 42.

## ✅ RELOCATED HETEROGENEOUS (round 94, 2026-07-23) — Black_It 9/9
`The_Syndrom/Black_It` = in-image V4 ($4200, subs 1-7, NON-identity song map)
+ RELOCATED V4 ($F200, sub 8) + RELOCATED **family-4 V5** copied to $1000
(sub 0, head `+$40/+$95`). Commit `8f82ffc9`; detail in [[project_dmc]] r94.
C31's relocating-wrapper rule composed with r93's heterogeneous machinery:
`_base_kind` learned the family-4 head + the observe path classifies kinds AT
THE LANDING on RAM; `post_init_sub` threaded through DMCV5Config and BOTH v5
`_load`s; the V4 unit owns the merged file's file-level slot regardless of
player index (`unit_order`). **The `base_override_not_player` residue class
is EMPTY.** Next partial by path: re-run `dmc_next_partial`.

## ✅ HETEROGENEOUS V4 + V5 (round 93, 2026-07-23) — Super_Tau-Zeta 5/5
`Super_Tau-Zeta` (r90's `base_override_not_player` residue) = 2 canonical V4
players ($A400/$9000, subs 0-3) + a **DMC V5** player at $B400 (sub 4, head
`JMP +$40 / JMP +$A1`) — the first V4+V5 member. Commit `48d7624e`; detail in
[[project_dmc]] r93. Machinery (all in pipelines/music_assembler/
heterogeneous.py + v5 factory):
- static `detect_compilation` now returns per-base `kinds` ('dmcv5' via the
  play+$A1 vector); any non-'dmc' kind routes to the heterogeneous builder
  (build_path `hetero_v5`; mass-write accepts both hetero names).
- `dmc_v5_config(base_override=, n_songs=)`; masked compare admits a
  PARTIALLY-RELOCATED copy (dead paths left at canon by the re-linker).
- V4 players merge via the homogeneous path as ONE unit; group-aware
  instrument blocks; `set_instr=` refs first-class; per-subtune
  `wave_programs` override carries the V5 idle program.
- **RESIDUE**: `The_Syndrom/Black_It` now detects as a compilation under the
  new code but subs 4/5/8 stay partial (play_match 26/26/1 — the "third
  player layout" note below; different class). Next partial by path:
  re-run `dmc_next_partial`.

## ✅ TWO-JMP PLAYER HEAD + reach-refined filter merge (round 90, 2026-07-23)
`Quad_Core` (3 players, 4 subtunes) needed BOTH a detection and a merge fix.
- **Detection: RE-ASSEMBLED players with a TWO-JMP head.** Bases `$2000/$1000/
  $2F00` carry `JMP base+$807` (init) / `JMP base+$50` (play) then DATA at +6 —
  not the canonical three-JMP head, so `_is_player_base` (three `4C` at +0/+3/+6)
  rejected them and the file fell to single-player. Generalised the player-base
  signature to the two essential vectors (init +0 / play +3) + a reloc-invariant
  target-range guard (`[base, base+$1000)`) replacing the third JMP. `_is_player_head`
  is the shared no-floor predicate; `_is_player_base`/`_is_player_base_ram` wrap it.
  Over all 5401 f1 members exactly TWO change detection (Quad_Core +
  Super_Tau-Zeta, both None→compilation); NO existing spec changes → 15 FULL
  compilations byte-identical.
- **Merge: the `repeat>5` refuse was an over-approximation.** A def whose reached
  step has dur=0 stays pinned in-record no matter how large `repeat` is
  (Quad_Core p1 def1: repeat=8, settles in-record). Replaced with `_walk_filter`
  (exact `fx_filter` sim): a def overruns iff its step index actually advances to
  ≥6. Genuine single-player overrun → strategy 3 `_overrun_anchored_window` (op's
  window verbatim at native indices up to reach R, others in free slots R+1..15;
  cap 16). **Closes the Zap_Zone/Protox-1 genuine-overrun residue**: Zap_Zone via
  compact (false overrun), Protox-1 via strategy 3.
- **REGRESSION SCARE:** first cut regressed Lane_Crazy + Mystery — the reach sim
  hit `_cap` on a LOOPING (repeat≤5 / non-settling) def and mis-flagged it as an
  overrun. `_def_overruns` now fast-paths repeat≤5→False and keys on "reached
  step ≥6", never on settling. 0 regressed after.
- **Gains: Quad_Core 4/4, Zap_Zone 2/2, Protox-1 2/2.** 0 regressed over all 24
  detected compilations + full regression (9 families).
- **RESIDUE update:** the filter-overrun class is now CLOSED. Remaining:
  Black_It + Super_Tau-Zeta = `base_override_not_player` (a co-packed player the
  dataflow locate can't find → unmergeable → single-player fallback). Next.

## HETEROGENEOUS compilation — DMC players + a `dmc_sfx` sub-player (round 72, 2026-07-10)
Canyon_Tank_Duel (Bayliss) = the FIRST heterogeneous compilation: 2 canonical
DMC music players ($1000/$2000, subtunes 0-4) + a tiny (~257 B) CUSTOM SFX
sequencer at $3000 (subtunes 5-12) — its OWN note/instrument/waveform format,
NOT DMC. Also in Widding's Empire_Strikes_Back (@ $3D00) → two authors, so it's
a shared DMC-editor SFX sub-player, named **`dmc_sfx`** (neutral, not
person-named). **Canyon 13/13 FULL** (all subs state ✓). Three pieces:
1. **Detection from the WRAPPER TABLE** — `_canon_jt_bases` (rigid canonical
   `4C b+1D 4C b+85` head) missed the re-assembled dmc_sfx player (JT at
   +$1B2/+$F0). `detect_compilation` now reads the dispatch wrapper's base-hi
   `LDA abs,X` table directly, each base validated by the reloc-invariant
   three-JMP head (`_is_player_base`). Also newly detects Empire (4-player
   heterogeneous). 0-regr on Abyssal_Karma/Balloonacy/Sharkz (re-verified FULL).
2. **`dmc_sfx` migrated as a typed USF engine** (NOT opaque bytes): new
   `dmc_sfx {}` block + `dmcsfx`-kind subtunes (grammar/parser/writer/types).
   Carries filter-cutoff LFO, arp pitch-program, tuning (extended over off-table
   reads), 8 instruments (4-phase ctrl/freqbase timbre+pitch modulation +
   env/PW), 8 songs, shared `voice_init` leftover state. Off-table read: static
   code bytes = extended tuning (C6); the ONE live one ($30F1 play counter) =
   composer redirect at `live_counter_fidx` (C11). Files:
   `pipelines/dmc/v4/sfx_engine.py` (extract + a pure-Python reference interp
   reading ONLY the typed model → proves completeness), `pipelines/dmc/
   sfx_composer.py` (clean 6502 re-impl). Full engine model in
   `pipelines/dmc/v4/RE_NOTES.md` section 'dmc_sfx'.
3. **Heterogeneous composer dispatch** — `build_dmc_compilation_sid` emits BOTH
   the DMC engine + the dmc_sfx interp into one image behind a per-subtune stub
   at $1000 (init latches the owning engine + routes with its local index; play
   jumps to the latched engine). Same "one engine per subtune, sequential" shape
   as the 2SID dispatcher, but per-subtune-SELECTED.
Gated on `usf.dmc_sfx` presence → single-player + homogeneous compilations never
touch it. dmc_smoke gained a `hetero-sfx` case. LESSONS: (a) a compilation's
packed players need not be the same engine — validate bases by the three-JMP
head, not the canonical offsets; (b) a distinct small sub-player is migrable as
a typed USF engine + a per-subtune multi-engine composer dispatch (the
5TT/Adrenalin playbook, realized for DMC); (c) the "leftover voice state" the
engine plays for non-song voices is deterministic file-image data → capture it
as a typed `voice_init`, not residue.

## Diagnosis method (for the next compilation)
`siddump --memwatch` on the runtime track-ptr state + `--pc-trace` of the live
tune-record read gives ground truth (py65 post-init does NOT reproduce a
relocating wrapper). Ledger C31.

**Queue note:** `tools/dmc_next_partial.py` returned Abyssal_Karma first; now
FULL, so the queue advances. See [[project_dmc]].
