---
name: project_dmc
description: "DMC (Demo Music Creator) migration — THE FOCUS ENGINE (10,676 HVSC SIDs, largest family). Round changelog, NEWEST-FIRST: the head of this file IS the current status (counts live there + in MEMORY.md, not here). KEY: data-table addresses are PACKER-PATCHED operands — extract by dataflow, never fixed offsets."
metadata: 
  node_type: memory
  type: project
  originSessionId: c83d6f65-8c2c-42bb-8f55-d46a1994efb2
  modified: 2026-07-22T20:11:08.083Z
---

## ✅ ROUND 86 (2026-07-22): the merged-pool cap was the ORIG's, not ours. f1 **5240 full / 161 partial / 0 error**, corpus SYNCED
Next f1 partial by path = `Heavy_Metal_Deluxe_beta`, the documented
"instrument overflow 30 > 28" compilation residue. **Now 3/3 FULL**
(222245 / 117622 / 164355 writes). Commit b36f9d4e; ledger C8 gained the
"first ask WHOSE cap it is" sibling.
- **The cap was transcribed from the DISASM, never measured on us.** 28 came
  from DMC's editor row encoding (5-bit `$60+id`, $7C-$7F special) — but the
  composer emits its OWN pattern format (parallel arrays; the slot rides a
  full operand byte after the event flags), so that field binds nothing in the
  rebuild. Our engine's real bound is its widest id-scaled index: fx_pulse's
  `lda cinst,x / asl×3 / adc pwphase,x / tay`, 8-bit at stride 8 ⇒ **32**.
  Raising `_MAX_INSTR` to the measured bound was the entire fix — no packing,
  no dedup, no composer change.
- **Zero-regression BY CONSTRUCTION:** the cap only gates the compilation
  merge, and a merge failure FALLS BACK to the single-player path, so only
  members that already fail can change path. All 6 fallback members were
  partial. Verified over all 22 detected f1 compilations: **0 regressed / 2
  gained**.
- **Tool defect found on the way:** `dmc_build_one` lacked the heterogeneous
  (DMC+MA) branch the family batch + mass-write take, so it reported
  Freespace_2075 partial after r85's work landed it — and it is what
  `dmc_next_partial` reads, so the queue was parked on an already-FULL member.
  The C20 fourth-layer rule generalises: when the build path grows a branch,
  every tool that RECONSTRUCTS a member needs it, the localizer included.
- **Gates:** full regression green (8 families, 0 regressed); 22 compilations
  re-verified 0 regressed; dmc_smoke 6/6; usf_corpus_check **11902/11902 parse
  OK (0 FAIL — the 80 stale are gone)**.
- **CLOSEOUT (fresh `tmp/dmc_f1_r86.jsonl`, full 5401-member batch): 5240 full
  / 161 partial / 0 error — 0 regressed / 2 gained vs r85** (Freespace_2075 +
  Heavy_Metal_Deluxe_beta). Build paths: 5367 single / 17 compilation / 16
  multisid / 1 hetero_masm.
- **RESIDUE in this class:** Lane_Crazy needs 39 instruments — past the real
  8-bit bound, so the next tier is PER-SONG instrument WINDOWS (only one
  packed player runs per subtune, each using ≤11), see
  [[project_dmc_compilations]]. Zap_Zone/Protox-1 filter overrun and Black_It's
  3rd player layout are unchanged.

## ✅ ROUND 85 (2026-07-22): the RELOCATING dispatch wrapper. f1 **5238 full / 163 partial / 0 error**, corpus SYNCED
Working the next f1 partial by path (`Freespace_2075`) surfaced a compilation
shape C31 detection is structurally blind to: **the wrapper COPIES a player
into RAM per subtune**, so it is not in the file image at all. Commit
4985aa13; ledger C31 (4-part refinement) + a new recognition-card bullet.
**Pour_le_merite is now 4/4 FULL** (0 regressed anywhere).
- 5 f1 partials carry the shape. Found by running init(A=sub) under py65 and
  diffing canonical jump tables in post-init RAM vs the image
  (`tmp/reloc_census.py`): Pour_le_merite, Super_Seven, Black_It,
  Mothafucka_2SID (2SID, so the C27 path owns it), Freespace_2075.
- Detection widening is essentially FREE and provably regression-safe: the
  whole sweep over 5401 f1 members costs **2.7 s**, detects 21 (was 14), loses
  NONE, and all 7 newly-detected members were ALREADY partial — no FULL member
  changes build path. (4 of the 7 are non-relocating compilations the old
  "≥2 in-image bases" gate had also been missing: Zap_Zone, Protox-1,
  Heavy_Metal_Deluxe_beta, Lane_Crazy.)
- Four defects, each independent — detail in ledger C31: the pre-gate; the
  load-address FLOOR (a player can be copied BELOW load — bit the landing
  test, `_jt_layout`, and the instrument-base assert); snapshot AT THE LANDING
  not post-init (init overwrites the very leftovers read as priming); and
  **the probe table had to inherit the memory view** — C9's 5th occ recurring
  one layer further out than r83b closed it.
- Two more per-player facts the MERGE collapsed to the start player:
  `d417_shadow` (→ per-subtune `init.sid.filter.res_routing`, no schema
  addition) and the filter-def post-init re-read (ran with the default
  subtune ⇒ all-zero window ⇒ every filter def decoded EMPTY).
- **Gates:** full regression green (8 families, 0 regressed); 14 compilation +
  16 multi-SID = 0 regressed / 0 gained; the 7 newly-detected = 0 regressed /
  1 gained; dmc_smoke 6/6; usf_corpus_check unchanged at 80.
- **CLOSEOUT (fresh `tmp/dmc_f1_r85.jsonl`, full 5401-member batch): 5238 full
  / 163 partial / 0 error — 0 regressed / 1 gained vs r84**, the gain being
  Pour_le_merite. Build paths: 5369 single / 16 compilation / 16 multisid.
  Corpus SYNCED: 5238 written, 0 errors, **0 orphans** (nothing went
  full→not-full), audit **18/18** stored artifacts re-verify across all three
  build paths. Post-sync: full regression green (8 families); usf_corpus_check
  unchanged at 80 (f2/f4/GT1, 0 f1), stored `.usf` 11900 → 11901.
- **RESIDUE in this class** (all fall back safely): Super_Seven needs
  per-subtune `extra_params` (its players disagree on `rest_effects`;
  `MusicSubtune.params` exists but the DMC composer doesn't read it);
  Black_It packs a 3rd player layout (init +$40 / play +$95).
- ✅ **Freespace_2075 now rebuilds FULL on all 3 subtunes** (225,157 /
  127,969 / 35,179 writes exact) via `pipelines/music_assembler/heterogeneous.py`
  — DMC v4 for sub 0 + the two Music_Assembler players behind a dispatcher.
  NOT yet wired into the DMC pipeline (detection doesn't classify MA
  sub-players; no USF round-trip), so the f1 batch still counts it partial.
- ⚠ **Freespace_2075 is NOT a DMC-only member.** Its two relocated
  sub-players are **Music_Assembler** (6,349 of 6,438 opcode-skeleton carriers
  are MA; its init `$D418=$1F / $D417=$F0` is the MA signature the trichotomy
  doc records). Sub 0 (DMC v4 at $1000) is FULL; subs 1-2 need a
  HETEROGENEOUS C31 with an MA sub-player — i.e. the Music_Assembler family
  migration. See [[project_music_assembler_target]].
- METHOD WARNING recorded in the ledger card: my first identification scan
  reported "1 carrier in 72,506 files" because the skeleton window spanned the
  player's SMC/SCRATCH bytes. Build skeletons from REACHABLE CODE only, and
  cross-check carriers against the `engine` column.

## ✅ ROUND 83 (2026-07-22): Defuzion_3 — the COMPILATION path's three defects. f1 partial 165 → 164
Next f1 partial by path (`MUSICIANS/B/Bayliss_Richard/Defuzion_3.sid`): sub 0
FULL, subs 1-3 diverging at write ~1. A 3-player C31 compilation that
detection MISSED, so all 4 subtunes decoded from player $5000. Now **4/4
exact**. Commit a30ff73f. Ledger C31 (3 refinements, incl. closing its own
documented "per-player idle priming is global-only" residue).
- **Detection — OBSERVE, don't parse (C18/C27 method).** The static wrapper
  decode assumes X == subtune and a base-HI-only table. Defuzion's wrapper
  does `ASL A; TAX` (X = subtune*2) and patches full lo/hi VECTOR PAIRS, so
  every candidate table decoded to interleaved garbage ($5000, $0000, $6000).
  That was the parser's SECOND needed widening (Canyon's re-assembled base was
  the first) — so `_observe_dispatch` now runs init(A=subtune) under py65 and
  takes the LANDING as the player and A as its song. Later pass + a
  ≥2-page-aligned-base pre-gate ⇒ single-player members never emulate.
  Detection widens by exactly this one member.
- **TRAP it introduced:** all 14 Rayden 2SID members false-positived — their
  wrapper gates chips per subtune, so different subtunes land on different
  players, which reads exactly like a compilation. Harmless in the build path
  (2SID is checked first) but latent; cured with the PSID chip-count guard.
- **RECORD 0 had lost merged SLOT 0.** Init clears the note-init cache to 0, so
  an idling voice runs record 0's pulse/wave mechanism (why the single-player
  extract force-includes record 0 as slot 0). `merge_models` rebuilt the pool
  from ROW-referenced instruments only ⇒ idle voices ran whichever instrument
  sorted first — in EVERY compilation, invisible until a voice idles a whole
  song. Defuzion sub 3's V3 track is a bare `$FE` stop: rebuild wrote PW lo
  $00 where the orig writes $40. Seeding the pool with record 0 fixes it;
  dedup keeps pool sizes unchanged. NB **13 of the 18 compilations' players
  DISAGREE on record 0** (incl. 6 currently-FULL), so raising on disagreement
  was not available — slot 0 carries the START player's record.
- **Idle priming is PER-SUBTUNE** (Defuzion's three players prime curnote
  0/0/48). Rides `subtune { init { voice N { note/gate_mask/dur_reload } } }`;
  NO schema addition (InitVoice already carries these at both levels — the
  same split the schema documents for `speed_ctr_init`). Composer table
  widening GATED on a subtune stating something different.
- **Gates:** 600/600 stored non-compilation FULL members rebuild
  BYTE-IDENTICAL from their stored `.usf` (the composer change is a proven
  no-op outside compilations); all 18 compilations + 17 multi-SID re-verified
  = **0 regressed / 1 gained**; full regression green (8 families); dmc_smoke
  6/6; usf_corpus_check unchanged at 80 (f2/f4/GT1, 0 f1).
- **C20 occurrence:** `Nice_Dream_2SID`'s r83 row is a STALE FULL — it
  verifies partial at play_match=63536 on PRE-change code too, identical
  numbers before and after the fix (its documented single-chip note-duration
  drift). Do not read it as a regression.
- **CLOSEOUT (fresh `tmp/dmc_f1_r84.jsonl`): 5237 full / 164 partial / 0
  error — 0 regressed / 1 gained vs r83.** Build paths: 5213 single / 15
  multisid / 9 compilation. Corpus SYNCED: 5237 written, 0 errors, 0 orphans;
  audit **18/18** stored artifacts re-verify (now including the new
  stored-`.usf`-rebuilds-stored-`.sid` check). Full regression green (8
  families); usf_corpus_check unchanged at 80 (f2/f4/GT1, 0 f1).
- The remaining 9 partial compilations (Heavy_Metal / Lane_Crazy /
  Para_Lander_DX / Rogue_Ninja / Zap_Zone / Chwat / Goldrake / Protox-1 /
  Wiz_Max) are unchanged — the documented filter-overrun /
  instrument-overflow / locate residue.

## ✅ ROUND 83b (2026-07-22): the WEDGE PROBES never reached multi-SID sub-players — C9 5th occ, C20 FIFTH layer
Chasing r83's "stale FULL" note on `Nice_Dream_2SID` found a REAL defect, not
a flake. Commit 1f026c13. **The member is now FULL from its own USF** and NO
member in the family needs the batch's hold_gateoff retry any more (r84:
zero rows carry one) — the root-cause fix subsumed the compensating mechanism.
- **What the layers said** (the C20 protocol, and the reason to run all three):
  stored `.sid` verifies FULL · stored `.usf` byte-identical to a fresh
  extract · stored `.usf` → `.sid` **DIFFERS** (17322 vs 17299 B),
  deterministically (checked across processes — Python hash randomization was
  the first suspect) and on PRE-change code too. The two stored files
  disagreed with EACH OTHER.
- **Root cause:** `_WEDGE_PROBES` are applied by `dmc_v4_config`, but
  multi-SID sub-players are built by `_config_at_base` → `_build_via_canon`,
  one layer BELOW that loop, so every wedge knob came back defaulted. **r81
  fixed this class at the table/layout level and it still bit** — "make the
  second path run the canonical build" is only a cure if you check WHICH LAYER
  the params attach at. Nice_Dream carries the wedge on BOTH chips ($17EC and
  $37EC) and got neither; the batch's write-stream RETRY then supplied it at
  verify time and the mass-writer re-injected it post-parse.
- **Fixes:** `_apply_wedge_probes()` factored out, called from both
  constructors incl. the bare fallback; `_hold_gateoff_probe` takes `base` and
  scopes to that player's own window (it was a whole-image FIRST match —
  answering for player 1 on behalf of every chip), falling back image-wide so
  nothing can lose its old answer; `dmc_mass_write` pushes a retry value onto
  the CONFIG so the writer emits it natively and REFUSES the member if it
  still misses the `.usf`.
- **New general detector:** the mass-write audit now asserts
  `build(parse(stored .usf)) == stored .sid` — the corpus-side Principle §8
  invariant, catching ANY build input that leaks outside the USF. NB a
  parse→write round-trip is NOT available to persist such a param: the USF
  round-trip is not byte-stable (20/60 sampled corpus files differ).
- **Gate:** 400/400 sampled single-player members REGENERATE byte-identical
  (the base-scoped probe changes nothing for them) + 14/15 multi-SID; only
  Nice_Dream (gains the param) and the 8 compilations (r83's fix) differ.

## ✅ ROUND 82 (2026-07-22): multi-SID residue + THE MASS-WRITE PALIMPSEST — f1 **5236 full / 165 partial / 0 error**, corpus mass-written
Follow-on to r81. Final batch 5401 members: **0 regressed / 15 gained** vs the
r80 baseline; mass-write 5236 members, 0 errors. Multi-SID **15 FULL of 19**.
Commits d7eb79dd, d9e23bf0, 65a9b4b3, a9bce98e.
- **THE BIG ONE — `dmc_mass_write` wrote artifacts the batch never verified
  (ledger C20, FOURTH layer).** `write_member` built EVERY member through the
  single-player constructor while `run_member` dispatches multi-SID →
  compilation → single. So `Dark_Knight_2SID.usf` on disk was a 3-voice
  single-chip extraction of a 6-voice tune (dated June), carrying a valid
  `code_hash`. NO gate sees this: batch green, hash matches, file parses,
  regression never reads it. **`code_hash` proves the VERDICT came from
  current code, never that the ARTIFACT is what earned it.** Detector =
  re-verify FROM THE STORED artifact. Now mirrors `run_member` exactly;
  post-mass-write spot-check: stored `.usf` → `.sid` byte-identical to the
  stored `.sid`, and the stored artifact re-verifies FULL, on 2SID +
  compilation + single-player members alike.
- **Cow_Anus_Fucked partial → FULL** (129731/129731). C19 13th occ CLOSES the
  per-STORE granularity trap the 12th documented: a `keep_regs` entry gains an
  `@label` form (`00@sidwrite`) scoped to the composer routine that plays that
  store's ROLE — named by what the block DOES, never by an address.
  `_SIDSTORE_ROLE` maps the canon sites we can name; an unmapped site keeps
  the coarse behaviour rather than guessing. Also added the `cymburst:` role
  label (assembler-only, emits no bytes).
- **Kordiaukis_01 first-div 34 → 351228.** Chip 0 now EXACT (740417); chip 2
  matches 351228/530294 = ordinary single-chip content residue, no longer
  multi-SID plumbing. (Its player 1 has a NON-canonical jump table, so it uses
  the bare fallback config and still verifies exactly.)
- **Mothafucka: FOUND but deliberately REFUSED.** Two more C18 observation
  gaps closed — run a few PLAY calls (its wrapper SMC-patches its own call
  operand per call: `INC imm / AND #$01 / TAX / LDA basehi,x / STA $0F16 /
  JSR $xx03`, alternating $1000/$E800), and test the JT signature against
  LIVE memory (its init COPIES chip 2's player to $E800, zero-fill in the
  file — C26 applied to the PLAYER). Extracting it needs the C26 post-init
  RAM path, which `_config_at_base` doesn't do, so an image-presence guard
  returns None → the member falls back to its previous single-chip build
  instead of raising `non-standard instrument base $0000` (a partial, not an
  error).
- **RSID captures forced.** siddump SKIPS an RSID orig unless `--force-rsid`,
  and a skipped capture is EMPTY — a partial with nothing to localize (same
  silent-wrong-verdict shape as the missing-ROMs trap). Rayden's two RSID
  2SID members now capture (0 → 1,415,898 and 598,956 orig writes, both
  chips). Both stay partial: the orig runs ~10× our rebuild's write count =
  an unmeasured IRQ rate (C9 territory). Neither is in a batched family
  (singleton fingerprint families outside f1), so no count moves.
- **Nice_Dream** now probes its mixed store (`17,01@cymburst` — the
  noise-attack burst relocates freq-lo but not freq-hi); unchanged at 63536,
  blocked by the documented single-chip note-duration drift.
- **REMAINING multi-SID residue (4):** Kordiaukis_01 (chip-2 content),
  Nice_Dream (single-chip drift), Mothafucka (needs C26 for a sub-player),
  4_Ever_Young + Popel_Premiere (RSID rate) — the last two outside f1.
- **`usf_corpus_check` 84 → 80 unparseable.** The 4 f1 `slide_phase`
  leftovers (Big_GLORZ / Heniek / Yo_Raps / Radio_Napalm — all PARTIAL, so
  no mass-write could ever refresh them) were DELETED per C20's rule. The
  remaining 80 are the two in-progress families' own residue (52 f2 `dcmd`,
  27 f4 `speed_ctr_init`, 1 GT1), refreshed by their own batches.
- **The wider orphan set — CLOSED, and closed STRUCTURALLY.** 56 of the 165
  f1 non-FULL members carried a stored `.usf` (2 also a `.sidfinity.sid`)
  written when older code judged them FULL: they PARSE, so
  `usf_corpus_check` can't see them, and no mass-write ever revisits a
  non-FULL member. All 58 are gone — deleted BY THE MECHANISM, not by hand
  (4 with the unparseable set, 54 by the first sync run), so they cannot
  come back. A mass-write is now a SYNC (`src/corpus_sync.py`, shared by
  the dmc/fc/v5 writers): current-code rows only → replay the batch's
  recorded `build_path` → delete artifacts of non-FULL members → audit a
  build-path-stratified sample by re-verifying FROM DISK, exit non-zero on
  failure. See ledger C20's fourth layer.
- **Closeout run (fresh `tmp/dmc_f1_r83.jsonl`):** 5236 full / 165 partial /
  0 error, every FULL row carrying `build_path` (5213 single / 15 multisid /
  8 compilation); sync wrote 5236 with 0 errors, removed 54 orphans, and the
  audit re-verified **12/12 stored artifacts across all three build paths**.
  `usf_corpus_check` 80 (f2/f4/GT1 only — 0 f1). Regression green ×4.
- Gates: full regression green (8 families) ×3; dmc_smoke 6/6; every
  previously-FULL multi-SID member re-verified at each step.

## ✅ ROUND 81 (2026-07-21): the multi-SID sub-player CONSTRUCTOR — f1 5221 → 5234 full / 167 partial / 0 error
`_config_at_base` (the per-chip constructor) hand-rolled a bare config, so
EVERY knob the canonical build probes was defaulted. Round 80 patched the one
defaulted knob it noticed (`cia_period`); this round cured the constructor.
Commits 5cc0646f, 84428b81, 13d93fa7. Ledger: C9 4th occ (the structural
cure), C27 (sub-player = ordinary player; per-chip param CLASS; two more
detection traps), C19 (a 2nd mixed-granularity keep_regs carrier).
- **Mc_Dieter 38931 SOLVED — it was `track_loop_target`, not the $FFFF/$81
  shape.** V2's track loops to a STATED position; defaulted to loop-to-0, the
  rebuild re-entered the intro patterns at the wrap. Those patterns state
  instrument 8 where the steady ones state 9 — same notes, and instrument 9
  is the noise_attack twin of 8 (identical ADSR `$08 $8A`), so the ONLY
  audible difference is the cymbal burst. Hence the divergence read as "the
  orig mirrors V1's $FFFF/$81 onto V2" (that IS the cymbal: `fxf & $80` →
  `$D400/$D401=$FF, $D404=$81`, then RTS). **METHOD that cracked it:**
  memwatch the orig's `$174E` (V2 ioff = inst*11) + `$177E` (fxf) vs the
  rebuild's own labels — orig 58→63 and STAYS; rebuild 58→63→**58** at
  exactly the divergence frame. A periodic 627-frame delta named the wrap.
- **Sub-players now build through `_build_via_canon(base_override=)`** (the
  C31 compilation mechanism), bare config kept as fallback. Two
  generalisations were needed, both because chip 2 is chip 1 COPIED WITH
  PER-CHIP RELOCATIONS: the masked compare must tolerate a `$D4xx` operand
  moved to the chip's address; and the track-loop hook probe keyed on the zp
  track pointer `$F8` — chip 2 has its own pair (`$F6` in Disco_Zak), so it
  now keys on the hook SHAPE (`_loop_target_probe`, also run by the bare
  fallback).
- **Rayden 2SID: 8 FULL / 5 partial → 14 FULL / 0 partial** (3 subtunes
  each). Dark_Knight, Disco_Zak_Remix, Mc_Dieter, Mopped_Tester,
  TrubbleLaBubble flip.
- **Detection 14 → 18 of 19.** The play vector need not be `JMP wrapper`
  (Kordiaukis inlines a C18 cycler there); `play == 0` means the tune
  installs its own IRQ (skip the static scan); `_observe_player_bases` now
  retries accepting JMP targets after the JSR-only pass (Cow_Anus reaches
  chip 2 by a tail JMP from init). Still undetected: Mothafucka (chip 2 only
  via an SMC'd play-time JMP).
- **Per-chip param CLASS** (`MULTISID_PER_CHIP_KEYS`): `play_phases` +
  `noteinit_deferred` join `multisid_keep_regs` as ';'-separated chip-ordered
  values. Cow_Anus runs ONE chip per call → complementary `P_S`/`S_P`, each
  chip at half the 100 Hz rate; the old "chips must agree" assert read that
  as a chip-2 wedge. An 'S' phase is accepted ONLY when the schedules are
  complementary (a py65 shortfall leaves ALL chips S at the same index).
- **LATENT BUG fixed:** `noteinit_deferred` was set by any pass through
  base+$591, which a full play makes per voice — i.e. it meant "has a P
  call". Right by luck for the 5 Rayden carriers; wrong for any P_R member.
  Now needs the $591 entry on a call that did NOT run the play body.
- **COMPARATOR ARTIFACT fixed** (r80's note): a passing multi-chip run
  aggregated from chip 1, which for a chip-2-only subtune is EMPTY → it
  reported `play_match=0 / state_match=False` for an exactly-correct member.
  Now aggregates from the chip with the largest overlap, and an
  empty-both-sides substream reports `state_match=True`. `is_full` unchanged
  in every case (diagnostics only).
- **REMAINING multi-SID residue (5):** Cow_Anus_Fucked — C19 per-STORE
  keep_regs (chip 2's sidwrite freq-lo tail at base+$60D un-relocated among
  3 relocated `$D400` stores, so all 3 voices' freq-lo land on chip 1;
  needs role-tagged emitter sites); Kordiaukis_01; Mothafucka (undetected);
  Nice_Dream (the documented single-chip note-duration drift);
  **4_Ever_Young + Popel_Premiere are RSID** — siddump skips RSID, so their
  orig capture is EMPTY and the verdict is unmeasurable on the current
  capture path, not failing.
- Gates: full f1 batch member-by-member vs the r80 baseline = **0 regressed
  / 13 gained**; all 13 previously-FULL multi-SID members re-verified after
  the per-chip param change; dmc_smoke 6/6; full regression green (8
  families) ×2.

## ✅ ROUND 79 (2026-07-21): multi-SID DETECTION — 9 → 14 of the 19 corpus multi-SID members
Follow-on to r78: the 6 Rayden 2SID siblings that `dmc_v4_config_2sid` refused
(so they ran as single-player and verified at ~0). Three detection bugs, all
cured by OBSERVING instead of parsing (C18) — commits 1b7c1e9b, ffd6af68.
- **C19 save-moment trap.** The wrapper scan required every call to be `$20`
  (JSR), but the wrapper neuters a chip per subtune by patching `$20`↔`$2C`,
  so a member SAVED under a chip-only subtune ships that call as BIT
  (Dark_Knight `20 03 E0 2C 03 EE`). A neutered call still NAMES its player —
  accept both opcodes.
- **Region-overlap in `multisid_active_chips`.** It watched
  `base..base+$1000` per player, but Rayden's players sit LESS than a page
  apart (5 of 9 detected: `$1000`+`$1C00`..`$1E00`) and Dark_Knight's wrapper
  (`$FC00`) sits inside its chip-2 page (`$EE00`+$1000) — so ranges overlapped
  and swallowed the wrapper, reporting every chip active in every subtune (which
  then merged silent chips' voices in). Cure: watch each player's own ENTRY
  VECTORS (base, base+3 / base+$50). Cross-checked vs the writelog per chip per
  subtune. **This alone flipped Blue_Max + Leprechaun_Boot_V1 to FULL.**
- **C18 phase wrapper in FRONT of the per-chip calls** (the other 5): an SMC
  counter at the play vector (`A9 00 / D0 0A / EE B1 0F` at `$0FB0`) runs the
  full play for both chips on one call and only each chip's WAVE-STEP entry
  (`base+$591`) on the next. Two additions: `_observe_player_bases` (py65,
  collect JSR targets that look like a 2-entry JT — page-aligned, JMP at +0
  and +3; only runs when the static scan already failed ⇒ can't change a
  detected member) and `_observe_play_phases_chip` (the shared observer watches
  `base+$1F9` and reads `$591` as 'S', and its pc-trace fallback can't
  disentangle two players in one trace; a `$591` F entry is past the note-init
  check so it also sets `noteinit_deferred`, the C23 2-frame note-start).
  Schedules observed: 3× `P_F123`, 1× `P_F123_F123_F123`, 1× plain `P`
  (Mc_Dieter's `INC` is neutered to `BIT` — it never cycles).
  The composer's phase dispatcher already lives INSIDE each player, so both
  chips cycle in lockstep with no dispatcher change.
- **Result: multi-SID FULL 2 → 4** (Bamse_Bert, Blue_Max, Leprechaun_Boot_V1,
  Zipped_out — all 3 subtunes each). All 5 phase members went garbage → deep
  partial: Mythig 6→211288, Physician_Remake 3→105284, Leprechaun_Boot_V2
  6→68864, DSR-FLT_Cracktroh 6→64076, Mc_Dieter 3→29904. Dark_Knight sub 1
  FULL, subs 0/2 at 104628.
- **THE "F PHASE UNDER-EMITS" READING WAS WRONG — it was the CIA RATE**
  (fixed below; ledger C9 3rd occurrence). The half-length exact prefix was
  the right notes at the wrong speed, not missing writes.
- NB the flat `find_first_divergence` is the WRONG instrument on multi-SID
  members (the verdict is per-chip, C28) — it reports position 0 on a
  cross-chip adjacency. Use `writelog_per_irq_capture` +
  `compare_instruction_stream(n_chips=N)`.

## ✅ ROUND 80 (2026-07-21): the multi-SID CIA rate — +4 FULL (multi-SID 4 → 8)
`_config_at_base` (the multi-SID sub-player constructor) never set
`cia_period`, and `build_dmc_2sid_sid` never passed `speed=` to the header, so
EVERY multispeed multi-SID member built as vblank. Invisible while the only
carriers were vblank (Nice_Dream, Bamse); it surfaced the moment r79 made the
5 CIA-timed Rayden members detectable. Commit 268590f3.
- **TELL: a per-chip EXACT PREFIX at a clean 1/N of the orig's length with NO
  content divergence.** Distinct from C25's ~0.5% cycle-creep drift. I first
  mis-read it as "the F phase under-emits" — the giveaway was that the prefix
  was exact and the ratio was exactly 2.
- **A C18 phase schedule DIVIDES the timer rate**, so the two must be read
  together: latch `$2663` (100 Hz) + period-2 `P_F123`, and `$1331` (200 Hz) +
  period-4, BOTH give a 50 Hz music tick. Mc_Dieter's phase `INC` is wedged to
  `BIT` so it never divides — a genuine 100 Hz tune.
- **+4 FULL:** Mythig (422427), Physician_Remake (420481), Leprechaun_Boot_V2
  (137598), DSR-FLT_Cracktroh (128053) — all 3 subtunes each.
  **Rayden: 13 members → 8 FULL, 5 partial.** f1 = **5229 full / 172 partial /
  0 error**.
- **REMAINING Rayden partials + first divergence:** Dark_Knight 104628 (sub 1
  FULL), Disco_Zak_Remix 72335, Mc_Dieter 38931 (see next bullet),
  Mopped_Tester 17516, TrubbleLaBubble 0. All are content divergences, not
  plumbing.
- **Mc_Dieter 38931 — SOLVED in round 81 (loop target). Original observation
  kept below because the READING was the instructive part: the shape was the
  cymbal burst, and the real cause was upstream (which patterns replay).** Capture the RIGHT way: `writelog_per_irq_capture` + filter
  `w[1] < 0x20` for chip 0 (the flat `find_first_divergence` is wrong here,
  C28). Sub 0, chip-0 index 38931 = **irq 2305**. The orig emits a 3-write V2
  block — `freqlo=$FF, freqhi=$FF, ctrl=$81` — which EXACTLY mirrors the V1
  block 3 writes earlier in the same irq (`[38926-38928]` V1 `freqlo=$FF,
  freqhi=$FF, ctrl=$81`). The rebuild instead starts a fresh NOTE on V2:
  5 writes, `freqlo=$9E, freqhi=$0B, pwlo=$00, pwhi=$04, ctrl=$09`.
  So the orig is putting V2 into the same freq-`$FFFF` / ctrl-`$81` state it
  just put V1 into, while we play a note. Preceding writes agree exactly
  (`[38929-38930]` V2 `SR=$8A, AD=$08` on BOTH sides — an AD/SR pair with no
  freq, i.e. the note-fetch/hard-restart shape), so the divergence is in what
  follows the fetch, not the fetch itself.
  NEXT STEP (recipe step 2): identify which engine path emits the
  `freq=$FFFF` + `ctrl=$81` shape for a voice — it is NOT a normal note-init —
  then diff that path against the composer's emitter. Candidate readings to
  test: an off-table freq read yielding $FFFF (C6/C2), or a track/orderlist
  stop-state the rebuild decodes as a playable row. NB `$81` = noise+gate.
- **COMPARATOR ARTIFACT worth fixing** — FIXED in round 81, and the
  diagnosis here was WRONG: the shift recovery works fine; the multi-chip
  aggregation reported chip 1, which a chip-2-only subtune leaves empty.
- **STILL UNDETECTED (5 of 19, none Rayden):** superseded by round 81 —
  4 of the 5 now detect; only Mothafucka remains.

## ✅ ROUND 78 (2026-07-21): the family-1 ERROR BUCKET — multi-SID × multi-subtune
f1 was **5,221 full / 173 partial / 0 unsupported / 7 error**; all 7 errors
were `AssertionError: multi-SID merge supports single-subtune members only`
(the Rayden 2SID builds, 2 chips × 3 subtunes). Now **0 error**, and 2 of the
7 are FULL. Three layers, each observed rather than assumed:
- **The assertion itself** — `merge_2sid_usf`/`_split_chip_usf` only ever
  handled `subtunes[0]`. Generalised subtune-wise using the EXISTING schema
  (`tempo 2/3`, `sid 2/3` already ride the subtune). Commit 4c4dbca1.
- **C19 (12th occ) — the relocation miss.** `_reloc_sid_regs` hardcoded
  `keep_res=True` (never relocate `$D417`), generalised from the single
  carrier Nice_Dream; Rayden's builds DO relocate it, so chip 2's res/route
  write was simply missing (first div at flat position 21). Static operand
  probe → `multisid_keep_regs` param; default now fully relocated. Census: of
  10,676 DMC members, 19 multi-SID headers, 8 detected, 7 fully-relocated + 1
  keep=`$17` ⇒ 0 FULL exposure.
- **C27 refinement / C18 — per-subtune chip selection.** The wrapper gates
  each player by SMC-patching its call opcode `$20`↔`$2C` (sub 0 = both, 1 =
  chip 1, 2 = chip 2) AND hardcodes `LDA #$00` before both inits, so each chip
  always plays its own song 0. Observed under py65 (`multisid_active_chips`);
  represented by which VOICES a subtune carries — no new field.
- **Two latent bugs surfaced:** the merge kept only chip 1's params (dropping
  per-voice otrk scalars + any chip-2 wedge — now renumbered/asserted), and
  the trichotomy comparator's no-alignment early return omitted
  `audio_guaranteed` (reachable once a chip's substream can be empty).
- **Bamse_Bert + Zipped_out FULL** (3/3 subtunes). Remaining 5 are partial on
  per-member CONTENT divergences, not multi-SID plumbing: Blue_Max +
  Leprechaun_Boot_V1 fail only their chip-2-only subtune; Disco_Zak (72335),
  Mopped_Tester (17516), TrubbleLaBubble (0) fail sub 0 too.
- **THE 6 UNDETECTED SIBLINGS — done in the same session (below).**
- Gates: usf_corpus_check 84 = the documented pre-existing set; dmc_smoke 6/6;
  full regression green (0 regr, 8 families). Commits 4c4dbca1, 4b0f77bb.

## 📋 CORPUS REFRESH (2026-07-21, EPYC): f1 + v5 re-verified & re-written; the stored `.usf` corpus had silently rotted
Not a round — a full re-verify + mass-write after the host move, prompted by
finding that **1,182 of 11,943 stored `.usf` files (9.9%) no longer parsed**
under the current grammar (the `speed_ctr_init` typed-field move, commit
718ade06). Regression never saw it: it builds from a ~116-member portfolio,
not from the corpus. Ledger **C20, third layer**; detector now exists as
`tools/usf_corpus_check.py` (~9 s) — run after ANY grammar/parser/writer/types
change.

| batch | members | FULL | wall | CPU | parallelism |
|---|---|---|---|---|---|
| v4 family-1 | 5,401 | **5,221** (+173 partial, 7 error) | 10.8 min | 20.6 h | 114× |
| f1 mass-write | 5,221 | 0 errors | 88 s | 1.5 h | 63× |
| v5 (f3+f5) | 1,495 | **1,098** (+202 partial, 41 error) | 145 s | 4.5 h | 112× |
| v5 mass-write | 1,098 | 0 errors | 2.8 s | 4 min | 85× |

- **Coverage is UNCHANGED / slightly up.** f1 = 5,221 FULL, exactly the
  recorded figure — the session's speed work (auto job sizing, threaded
  FC/DMC verifies, songlengths + capture caches, the parser change, the
  Check-A fast-reject) cost **zero** members. v5 went 1,088 → **1,098** (+10).
  All 41 v5 errors and all 7 f1 errors were already failing before (the f1
  seven are Rayden 2SID hitting the documented "multi-SID merge supports
  single-subtune members only" limit; only their label moved).
- **SCOPE THE FIX BEFORE RUNNING IT.** The f1 mass-write regenerated 5,221
  members and fixed **zero** stale files — none of them were f1 members. The
  1,182 were 1,098 v5 + 52 f2 + 27 f4 + 4 f1-non-FULL + 1 GT1. Map failures to
  families first (`usf_corpus_check.py` does).
- **Corpus now 84 unparseable** (was 1,182): 52 f2 (`dcmd`), 27 f4
  (`speed_ctr_init`), 4 f1, 1 GT1. f2/f4 are in-progress families — their
  batches were NOT run. The 4 f1 leftovers are non-FULL members, so no
  mass-write will ever refresh them: those want DELETING, not rebuilding.
- **Tooling trap found:** `dmc_v5_family_batch.py` writes
  `tmp/dmc_v5_results.jsonl` but `dmc_v5_mass_write.py` defaults to
  `tmp/dmc_v5_full_results.jsonl` — a legacy file whose rows have EMPTY
  `code_hash`. Defaults would mass-write from stale data; pass `--results`.

## ✅ ROUND 77 (2026-07-21): STICKY TRANSPOSE orderlist EMISSION (D6 piece 3, option B) — the composer now matches how the ORIGINAL stores the orderlist
The generated orderlist is a SINGLE physical track (no 2-pass unroll anywhere),
with the transpose as a **sticky `$FD` command at the marks** — not baked into
every entry — a `$FF` 16-bit **BYTE-offset** loop, and the player THREADS the
transpose across the loop wrap at runtime. This is exactly how the original DMC
engine stores it (verified: Cross-Tune is single-pass, transpose commands at
sparse marks, and its "first-4-bars-an-octave-up" intro is the natural
runtime-threading of a transpose command whose entries-before-it inherit the
init value on pass 1 and the carried value on repeats).
- **Why B not the conditional de-unroll (option A):** the user's question "how
  do the 254 handle it themselves?" — the orig is single-pass + sticky
  transpose, so OUR 2-pass was purely a baking artifact. B = the faithful fix
  (orderlist-level twin of the sticky slot/vol change). It de-unrolls ALL
  voices (incl. the ~1.7% non-loop-stable-transpose carriers, reproduced for
  free by runtime threading) AND drops the transpose byte on non-mark entries.
- **The "carried duration across a wrap" edge = 0 corpus-wide** (full-corpus
  check, 8857 members); the only steady≠intro cause is TRANSPOSE (254 voices),
  which sticky-transpose handles natively.
- **Track format** (variable-width): `$FD,(T+64)` transpose command at marks +
  2-byte `[gid, otrk]` pattern entries; `$FE` stop; `$FF, lo, hi` byte-offset
  loop. gid ≤ $FC (pool asserted ≤ 253; corpus max = 69). Player `trkrd` walks
  the stream threading `transp,x`; `pat_end` drops the fixed `+3` (the walker
  advances the track ptr at fetch); new `trkg` temp. **otrk ($1726 sonified
  counter) stays the DERIVED per-entry value, decoupled from the byte layout**
  — sonified members unaffected.
- GATES: **full family-1 batch 5221/173/7 = EXACT baseline (member-by-member 0
  regr / 0 gain across 5401)**; regression green (8 families); dmc_smoke 6/6;
  test members FULL incl. BOTH transpose-diff carriers (Cross-Tune,
  Break_Free_Nation_BCD); **TRACKS −49%** (16911→8653 sample) on top of the
  round-76 pool −22%. Commit 9cbe6801. Corpus mass-written in the compact form
  (option B is the endpoint of the orderlist de-unroll; nothing left unrolled).

## ✅ ROUND 76 (2026-07-20): STICKY slot/vol pattern EMISSION (D6 piece 3) — the SID gets the compaction too
The generated SID no longer spells out an instrument slot + vol override on
EVERY note row; they ride the sticky player registers `curinst,x` / `volovr,x`
and are emitted only where the SOURCE row STATES them (`_row_event_stated` +
`_encode_pattern`, `pipelines/dmc/composer_asm.py`). Motivation (user): USF-ML
compaction is not the only goal — SIDs built from USF should be EFFICIENT too;
D6-piece-2 was a carrier refactor (byte-identical SID), so the stated-form
savings never reached the SID. This is an EMISSION change (write-log verdict,
NOT byte-identity — golden diff DIFFS by design).
- **Emission by STATEDNESS, never value-equality** (C32 "presence = byte fact"):
  statedness is pattern-intrinsic, so byte-keyed dedup still collapses the
  ~intro variants; value-equality would reintroduce them.
- **`dur` stays always-carried** — DMC dur-carry is 2 slots corpus-wide, not
  worth the `dur_field`(resolver seed) vs `dur_reload`(durrel/$173E seed)
  landmine + the `dur,x` fetch-countdown double-duty.
- **rest/switch/slide carry a stated slot/vol too** — a rest's instrument
  command updates the engine sticky state (the resolver folds it in), so
  dropping it stales a following inherited note (the bug: Nocturno sub1 V2 has
  rests stating instr). Presence packed into the two FREE HIGH BITS of the
  always-present dur byte (bit6=slot bit7=vol) → NO penalty on a plain rest
  (`[op,dur]`); notes ride the existing flags byte (bit3/bit4). Player:
  `sc_slotvol` shared suffix + `curinst,x`/`volovr,x` seeded 0 at init.
- **`reload_base` kept AHEAD of the dur/slot/vol writes** — its off-table
  redirect SONIFIES live `dur`/`durrel`, so it must read pre-update values
  (saved byte-index in `patix`). Latent ordering dep, now pinned.
- **Edge cases (your transpose-0-style concern) safe by construction**: the
  sonified sectpos ($1729) / otrk ($1726) counters are reproduced from the
  EXPLICIT per-event shadow (`_pattern_secvals`/`_row_secwidth`), decoupled from
  what emission carries — a value-redundant-but-stated command still advances
  them.
- GATES: **full family-1 batch 5221/173/7 = EXACT r74 baseline, member-by-member
  0 regressions / 0 gains** across all 5401; regression.py green (8 families);
  dmc_smoke 6/6; 44-member stratified before/after 0-regr; **pattern-pool −21.9%**
  on the sample (Nocturno −20%, Music_for_Game −12%). Commit 45ddd89e.
- OPEN (offered, not done): the orderlist/track 2-pass unroll is now-redundant
  (patterns dedup → steady-tail entries duplicate the intro loop portion). The
  natural next efficiency step = de-unroll the track ($FF loop + runtime
  inheritance, C32-piece-1-at-emission); left out as a separate change with its
  own $1726-counter verification. Corpus NOT mass-written in the compact form
  yet (composer-only change; stored .sid artifacts are stale-but-FULL, not the
  coverage source of truth).

## ✅ ROUND 75 (2026-07-20): 2SID seed-merge gap CLOSED (the r74 latent)
`merge_2sid_usf` now carries per-SUBTUNE init voices (the stated-row
resolver seeds, `instr: i1`) onto the merged subtune init as a level
DISTINCT from the file-level idle-priming voices; `_split_chip_usf`
recovers each level separately per chip. Facts established:
- The live 2SID-merge population is exactly ONE member
  (Surgeon/Nice_Dream_2SID) — all other 326 corpus multi-SID PSIDs are
  not-DMC (312) or hit known scope gaps (8 Rayden multi-subtune assert,
  4 Phobos freq-table-disagreement assert, Voice_2SID IndexError,
  Time_2SID wave_marker_chain).
- Nice_Dream DOES carry seeds (chip1 v2, chip2 v1+v3; all 6 voices take
  the stated resolution path) — the pre-fix drop was INERT only because
  `needs_instr_seed` fires on leading REST rows (walk instr = sticky 0)
  and `_materialize_row` stamps instr on note rows only; a first NOTE
  row inheriting instr would have KeyError'd in `_row_event`
  (`inst_slot[None]`) pre-fix. Post-fix correct by construction.
- Gates: multi-SID golden byte-identity 327/327 (tmp/dmc_2sid_golden.py,
  baseline pre-change), dmc_smoke 6/6, synthetic merge→write→parse→split
  seed-roundtrip proof (tmp/test_2sid_seed_merge.py), full regression.
- Still-open sibling (unchanged, corpus-inert): the merge drops per-chip
  `init.slide_phase` (one scalar slot for N chips) and supports
  single-subtune members only.

## ✅ ROUND 74 (2026-07-20): STATED pattern rows (D6 piece 2) — ~intro variants dissolved [ledger C32 CANONICALIZED 2×]
The C32 boundary note's "deferred deep half" executed as a cross-family
project (deprecated/old_docs/stated_duration_plan.md; FC side in
[[project_fc_fingerprint_and_standard]]):
- **Stated (dur/instr/vol) rows:** folded voices emit NoteRows whose
  duration/instrument/`vol=` are present IFF the sector stream states
  the command byte (presence = byte fact); absent = inherit
  (`src/usf/resolve.py`, the ONE shared interpreter — also Layer-3 +
  both composers). One pattern per physical sector ⇒ `~intro` decode
  variants GONE from USF (probe over 5,825 members: 10,343 intro
  slots in 1,673 members — channels vol 7,345 / instr 2,250 / both
  746 / dur 2; zero non-sticky variants — the stated form provably
  subsumes the mechanism). Pool −5.6%.
- **Extract self-verification (C32 discipline):** re-runs the shared
  resolver against the walk's decode for BOTH passes; mismatch ⇒ keep
  the effective representation wholesale. Guards: vol-only inheritance
  with no dur/instr marker is composer-indistinguishable from the
  effective form ⇒ fallback; instr seed (engine sticky 0 = i1) emitted
  as per-subtune init-voice priming when a leading row consumes it
  (dur seed 0 = the dur_field default, no emission).
- **Composer:** stated branch runs the resolution interpreter (intro
  pass + steady cycle re-derive the walk's 2-pass unroll at compose
  time); `_dmc_rows_stated` (any inherited dur, or note-row instr)
  picks the path. **Nocturno lesson:** sonified members KEEP the
  `*_cmd` placement flags on stated rows — redundant with presence,
  but the sectpos byte-width math needs ONE unambiguous source across
  stated + fallback voices (presence-only widths silently collapsed on
  a fully-stated voice routed down the effective path; 30 crash + 1
  wrong-width members caught by the golden gate).
- **GATES:** family-1 golden **5394/5394 byte-identical** (7 known
  both-err); dmc_smoke 6/6; full regression green (8 families);
  authoritative batch **5221 FULL / 173 partial / 7 error = EXACT
  baseline** (zero verdict movement); mass-write re-run (corpus now
  stated-rows form). `loop@N len=L` retired from the grammar (FC-only
  form, subsumed); `~i` intro syntax RETAINED for the fallback class.
- **LATENT — RESOLVED in round 75 (above):** `merge_2sid_usf`
  builds the merged subtune init from the FILE-level idle-priming
  voices only and never reads `u.subtunes[0].init.voices` — a 2SID
  member whose stated voice consumes the engine-init INSTR seed
  (`instr: i1`, per-subtune) would lose it (resolver seeds instr None
  → wrong first instrument). No current 2SID member hits it (golden
  green). Fix when touched: propagate per-subtune init voices through
  the merge (+ `_split_chip_usf`), or assert seedlessness at merge.

## ✅ ROUND 73 (2026-07-19): the DE-UNROLL + plan-doc closeout — orderlist physical stated form [ledger C32], environment/init typing [trichotomy §4.3/§4.5], writer role comments
The dmc_composer_to_extract_plan's remaining phases executed + the parked
de-unroll done in one arc (user-directed "wrap up the loose ends"):
- **Phase C:** `environment { cia_period, play_repeat }` (typed top-level
  block, v4+v5) + `init { slide_phase }` priming — the params keys gone.
  Golden 91/91 byte-identical. (Grammar start rule restructured into a
  repeated `top_block` group — an 11th chained optional exploded LALR
  construction from seconds to minutes.)
- **Phase E:** writer per-block role comments (the fingerprint had shipped
  2026-07-10 untracked).
- **DE-UNROLL [C32]:** `orderlist stated:` physical form — stated
  transpose-command marks (absent = inherit, state carries over the wrap),
  `~intro` decode variants, `!k` dead cmd bytes, physical loop@S. Extract
  folds `_walk_track`'s 2-pass state-closure unroll by DIRECT OBSERVATION;
  composer re-derives the unrolled emission + $1726 counter seeds from the
  notation. `otrk_pad`/`otrk_period`/`otrk_rcmd` DISSOLVED (fold-failure
  voices keep the full old fitted path — no member can downgrade).
  **Latent bug found+fixed:** the fitted-rcmd emission was off-by-one on
  ALL pass-0 counter seeds of rho-shaped tracks (loop target ≠ slot 0) —
  423/5401 members carried wrong-but-never-sonified seed bytes.
  GATE: full family-1 golden diff = 4971 byte-identical + 423
  write-stream-inert (individually classified) + 0 regressions; full
  pipeline regression green (8 families). Also fixed the golden harness
  classifier (wrong result key; path never exercised before).
- Empirical basis (2 probes, 40 members/154 voices): every looping walk =
  exactly 2 passes by construction (closure must WALK the repeat to see
  it); 82% byte-identical duplicate passes; the rest = transpose
  inheritance + sticky-decode intro variants; loop_to == wrap boundary
  always.
- CLOSEOUT (F): authoritative batch **5170 FULL / 173 partial / 7 error**
  — FULL count EXACTLY the pre-change baseline (zero verdict movement).
  Mass-write 5221 written / 0 err (corpus now in `orderlist stated:` form;
  partials keep stale pre-form .usf until they go FULL). Portfolio
  RE-DERIVED (new track:loop/stop/transpose + struct dimensions; includes
  Deepspace_Travel from the latent-bug class); final full regression green
  (8 families). dmc_composer_to_extract_plan.md ARCHIVED (all phases
  done/superseded — see its header).

## ✅ ROUND 72 (2026-07-10): HETEROGENEOUS compilation — migrated the `dmc_sfx` sub-player — Canyon_Tank_Duel (Bayliss) 13/13 partial → FULL (0 regr) [ledger C31 heterogeneous]
First still-partial f1 by hvsc path after Balloonacy (r71):
`MUSICIANS/B/Bayliss_Richard/Canyon_Tank_Duel.sid` — the FIRST heterogeneous
compilation: 2 canonical DMC music players ($1000/$2000, subs 0-4) + a tiny
(~257 B) CUSTOM SFX sequencer at $3000 (subs 5-12) that is NOT DMC (own
note/instrument/waveform format). Same engine in Widding's Empire_Strikes_Back
(@ $3D00) → shared DMC-editor SFX sub-player, named **`dmc_sfx`**. User chose the
FULL migration. THREE pieces, all landed, all `usf.dmc_sfx`-gated (0-regr on
single-player + homogeneous compilations):
**(1) Detection from the wrapper table.** `_canon_jt_bases` (rigid canonical JT
head) missed the re-assembled dmc_sfx player (JT +$1B2/+$F0). `detect_compilation`
now derives bases from the dispatch wrapper's base-hi `LDA abs,X` table, each
validated by the reloc-invariant three-JMP head (`_is_player_base`). Also newly
detects Empire (4-player heterogeneous).
**(2) `dmc_sfx` as a typed USF engine** (NOT opaque bytes): new `dmc_sfx {}`
block + `dmcsfx` subtune kind (grammar/parser/writer/types). Carries the shared
musical content — rotating filter-cutoff LFO, arp pitch-program, tuning tables
(extended over off-table reads), 8 instruments (4-phase ctrl/freqbase timbre+
pitch modulation + env/PW), 8 songs, shared `voice_init` leftover state. Off-table
freq read: static code bytes = extended tuning (C6); the one LIVE one ($30F1 =
play counter) = composer redirect at `live_counter_fidx` (C11). New files:
`pipelines/dmc/v4/sfx_engine.py` (extract + pure-Python reference interpreter
reading ONLY the typed model → proves completeness), `pipelines/dmc/sfx_composer.py`
(clean 6502 re-impl). Full engine model in RE_NOTES.md 'dmc_sfx'.
**(3) Heterogeneous composer dispatch** (`build_dmc_compilation_sid`): emits BOTH
engines into one image behind a per-subtune stub at $1000 (init latches the
owning engine + routes with its local index; play jumps to it). Same "one engine
per subtune, sequential" shape as the 2SID dispatcher, per-subtune-SELECTED.
**Canyon 13/13 FULL** (state ✓ every sub). dmc_smoke gained a `hetero-sfx` case
(6/6). See [[project_dmc_compilations]] for detail. Two RE gotchas: xa65 chokes
on a `:` inside a comment; the leftover-voice load clobbered A (the song #) → save
with pha/pla, and the inactive-voice loop path read a stale cur_x → set it at
loop top. LESSON: a compilation's packed players need not be the same engine — a
small distinct sub-player is migrable as a typed USF engine + per-subtune
multi-engine composer dispatch (the 5TT/Adrenalin playbook, realized for DMC).

## ✅ ROUND 71 (2026-07-10): COMPILATION per-player locate (region-bounded) + offtable-union instrument dedup — Balloonacy (Bayliss) 7/7 partial → FULL (0 regr) [ledger C31 + C8]
First still-partial f1 by hvsc path after Feed_a_Bird (r70): `MUSICIANS/B/Bayliss_Richard/Balloonacy.sid`
— a 4-PLAYER COMPILATION (bases $1000/$2000/$3000/$3F00; 7 subtunes dispatched
[(1,0),(1,1),(0,0),(0,1),(2,0),(2,1),(3,0)]). Listed as known residue in
[[project_dmc_compilations]] ("one edge player fails dataflow locate"). It fell
back to single-player → all 7 partial, first div flat pos 0 V1 SR $6E vs $EE
(the single-player fallback playing wrong data). TWO independent blockers, both
compilation-path-only:
**(1) `dataflow.locate($3000)` returned None.** The $3000 player is canonical DMC
uniformly relocated for CODE + DATA TABLES (freqlo $3647, wavectrl reads $398A,
all base+$2000) BUT its STATE scratch operands stay at the canonical $1xxx
($172C not $372C) AND it carries DEAD-CODE JMPs into the SIBLING $1000 player's
code (un-relocated `JMP $349C→$1591`, an un-relocated copy of its own
`$349C→$3591`). GROUND TRUTH `siddump --pc-trace --subtune 5` (1-based!): the
player runs ENTIRELY in $3xxx (pages 30-38, zero $15xx) — the $1xxx jumps never
execute. But the static `_instrs` trace FOLLOWS them (1149 instrs vs 712), so
every opcode-window signature matches TWICE (once per player) → wavectrl/wavefreq/
freq_lo/freq_hi all ambiguous → None → whole compilation falls to single-player.
FIX: `dataflow.locate(mem, base, region=(base, base+0x900))` filters the located
instrs to the forced player's own code window (0x900 covers the canonical
$1000-$18E8 extent; data-table addresses are the READ RESULT, not the site). The
sibling's block sorts outside → dropped; the player's own $3xxx block stays
contiguous so signature windows are intact → unique. `base_override`-only
(general single-player passes region=None — a re-assembled player may spread code
past a fixed window). Regression-safe: can only turn ambiguous-None into a
unique match. **(2) after (1), the 4-player merge overflowed the 28-inst 5-bit
id cap (29>28).** The tightest pair differed ONLY in `offtable_freq` ([] vs
[(12,89,1,26)]) — a C6 reachability artifact (which wave-off/note the inst was
played at), NOT intrinsic content. FIX (`merge_models`): dedup keys on all
fields EXCEPT offtable_freq, carrying the UNION of records per merged id
(Principle Rule 1 — cluster by behavior; each record fires only for its own
(off,note), inert for a song that never plays it; a (off,note)→different-(lo,hi)
COLLISION refuses the union → distinct ids). 29→28. **Balloonacy 7/7 FULL**
(state ✓ every sub). REGRESSION-SAFE by construction: both changes are
merge/base_override only — single-player members never touch either path, and
every currently-FULL compilation (Abyssal_Karma/Sharkz/Para_Lander_DX/Race_n_Smash/
Poing_Ultra) keeps its IDENTICAL instrument count (offtable-union changes nothing
unless two insts share a base key, which for those it doesn't). dmc_smoke 5/5.
Full `tools/regression.py` GREEN (0 regr all 8 families: Hubbard 71, Companion
44, C64ME 15, Jay_Derrett 17, FC 31, DMC 12, Basic 22). code_hash → new (next
batch auto-re-verifies). Post-fix wide sweep DEFERRED per session instruction —
the region-bounded locate likely also unblocks the sibling residue
(Lane_Crazy/Wiz_Max/Goldrake_plus_2/Mystery/Rogue_Ninja), unverified this round.
commit (code + this memory). LESSONS: (a) a compilation player can be uniformly
relocated for code+tables yet keep STATE at the canonical $1xxx AND carry
dead-code cross-player jumps — the static trace bleeds into the sibling, so
BOUND the locate to the player's own page; use `--pc-trace` (1-based subtune) to
confirm which code actually runs. (b) `offtable_freq` is a reachability artifact,
not intrinsic content — EXCLUDE it from any instrument dedup key and UNION it, so
behaviorally-identical instruments collapse (fits the 5-bit cap without losing
the write stream).

## ✅ ROUND 70 (2026-07-10): SWITCH ($7D) gate-mask toggle uses a per-member EOR immediate — Feed_a_Bird (Bax) +1 partial → FULL (0 regr) [ledger C19 11th occ]
First still-partial f1 by hvsc path after re-verifying the stale Jul-9 batch
from the top (idx 0-12 Artlace..Enter all now FULL via rounds ≤69):
`MUSICIANS/B/Bax/Feed_a_Bird.sid` (vblank, single sub, CANONICAL layout, base
$1000). Flat first-div 10036 `$D412` V3 ctrl, orig `$00` vs reb `$16`. ROOT
(C19 hand-patched wedge): the DMC player's tie/legato SWITCH ($7D) handler at
base+$183 toggles the voice gate mask (`$100f,x`) with an EOR immediate —
`LDA gatemask,x / EOR #imm / STA gatemask,x` at base+$189..$18E. Canon `#$01`
flips ONLY the gate bit ($FF↔$FE = release gate); Feed_a_Bird patches the
immediate byte at base+$18D `$01→$1F`, so a SWITCH flips
gate+test+ring+sync+triangle ($FF↔`$E0`). The wave-step's `wave_ctrl & mask`
then gives `$17 & $E0 = $00` (a triangle+ring+sync note CUT TO SILENCE) vs our
`$17 & $FE = $16`. GROUND TRUTH: memwatch gate mask `$1011` goes $FF→**$E0**
across the note-off (NOT →$FE, which the disasm header only documents as
$FF/$FE); pc-trace `$118C = 49 1F` not `49 01`. **MISSED by dmc_canon_diff** —
an immediate-value tweak (unchanged opcode $49, no operand repoint) is exactly
its documented blind spot, which is why Feed_a_Bird wasn't in the "unhandled
singleton" list. FIX: `factory._switch_toggle_mask_probe` (STATIC opcode probe,
anchors LDA/STA operands = `cfg.gatemask_addr`, reloc-aware, guards
gatemask_addr=None for f2/dataflow builds) → new USF param `switch_toggle_mask`
(the toggled bit-set; default $01) → composer `ev_switch` emits `eor #<mask>`.
Default $01 → byte-identical text. REGRESSION-SAFE BY CONSTRUCTION: the composer
applies the probed mask verbatim so its `$D404` write can only match the orig
MORE often (never less); and $E0 vs $FE COINCIDE for noise/pulse/saw notes
(only bits 5-7 survive either mask), so the value bites only on
sync/ring/test/triangle notes. Census 5833 f1: **1 carrier (Feed_a_Bird,
partial), 5502 canon $01, 0 FULL exposure**. Feed_a_Bird FULL 130578/130578
state ✓. Full `tools/regression.py` GREEN (0 regr all 8 families: Hubbard 71,
Companion 44, C64ME 15, Jay_Derrett 17, FC 31, DMC 12, Basic 22). code_hash →
52a8c31 (next batch auto-re-verifies). Post-fix wide sweep DEFERRED per session
instruction. commit 96d7c321. LESSON: a wedge that only changes an EOR/AND
IMMEDIATE (opcode + operands unchanged) is invisible to dmc_canon_diff — find
it via the divergence recipe + a memwatch of the exact state byte across the
diverging write, not the wedge enumerator. The disasm header's list of a state
byte's possible values ($FF/$FE) may be INCOMPLETE — trust the runtime memwatch.

## ✅ ROUND 69 (2026-07-10): PER-MEMBER IN-TABLE vibdepth deviation (not just the code-overlap head) — Enter (Bax) +1 partial → FULL (0 regr) [ledger C11/C6 — vibdepth head→in-table]
First still-partial f1 by hvsc path after re-verifying the stale batch from the top
(idx 0-11 Artlace..Wild_Orgasm all now FULL via rounds ≤68): `MUSICIANS/B/Bax/Enter.sid`
(vblank, single sub, canonical layout). Flat first-div 112149 (51%) `$D40E` V3 freq
lo, orig $FF vs reb $0F (freq $0EFF vs $0F0F, Δ+$10). ROOT (memwatch V3 base $1731/
accum $1737): base $0EEF constant → PURE VIBRATO; orig accum triangles 0→$10→$20→$10
→0→-$10 (step $10), rebuild 0→$20→$40→$20→0 (step $20 = EXACTLY 2×). vstep=vibdepth
[curnote] and curnote here = 44 (the glide START note; vstep is set at note-init from
the start note, curnote then glides to 46, vstep unchanged). **Enter's `$1888`
vibrato-depth table byte at index 44 = $10 vs the CANONICAL player's $20** (verified
against `pipelines/dmc/docs/dmc4_player_embedded_1000.bin`; composer's `VIBDEPTH`
constant correctly copies canon = $20). Every other index matches canon → a single
non-canonical AUTHORED per-note vibrato depth (that note vibrates half as deep). The
extract captured vibdepth deviations only at the code-overlap HEAD (idx<6, round 66)
and off-table (idx>95) — NOT genuine in-table musical deviations (idx 6-95). FIX
(extract-only, `_assign_offtable_freq.add_note`): generalize the head gate `n<6 and
mem!=VIBDEPTH[n]` → `n<96 and mem!=VIBDEPTH[n]` — capture the member's actual byte
wherever a REACHABLE note's vibdepth differs from canonical; the composer's existing
in-place override (`offtable_vibdepth` → `_vd[n]=depth`) handles it. REGRESSION-SAFE
BY CONSTRUCTION: a canonical-layout member deviates nowhere it plays (capture nothing
→ byte-identical); a FULL with an ACTIVE-vibrato deviation could not exist (would
diverge like Enter), an INACTIVE one is inert. Enter FULL 217611/217611 state ✓. Full
tools/regression.py GREEN (0 regr all 7 families: Hubbard 71, Companion 44, C64ME 15,
Jay_Derrett 17, FC 31, DMC 12, Basic 22). Journey (page-3 head-deviation carrier) +
Secret_Loser re-verified FULL after the change. SURVEY (naive canonical-addr scan of
224 partials): only Enter has a clean single isolated in-table deviation; the rest are
head (round 66) or relocated (my scan mis-addressed — extract uses cfg.vibdepth_addr,
reloc-correct). code_hash 7072fe23→7689a794 (next batch auto-re-verifies). Post-fix
wide sweep DEFERRED per session instruction. commit 6dbc4739. LESSON: the vibdepth
table is per-member MUSICAL content — a note's vibrato depth can be authored
non-canonically at ANY index, not only the code-overlap head; capture reachable
in-table deviations too (the head fix was the special case, not the whole class).

## ✅ ROUND 68 (2026-07-10): NOTE-FETCH base read ignored the LIVE off-table redirect — Secret_Loser +1 partial → FULL (0 regr) [ledger C11/C6 — base-reload sites]
First still-partial f1 by hvsc path after Toccata_v2 (r67) flipped FULL:
`MUSICIANS/B/Bakker_Nantco/Secret_Loser.sid` (vblank, single sub). Flat first-div
pos 13112 `$D40E` V3 freq lo, orig `$06` vs reb `$07`. ROOT: curnote=`$F4` (244,
a positive off-table index — NOT an r66 wrap, so it IS captured) → `freqlo[$F4]=
$173B`=V1's LIVE duration counter=`$06`; the composer's `ev_note` note-fetch reads
`freqlo[curnote]` RAW → the STATIC ovrwin byte `$07` (file-image $173B), while the
orig reads the counter LIVE. The `LIVE`-flagged record existed; only the WAVE-STEP
read site (`ws_rd`) honored `_gen_offtable_redirect` — the two BASE-freq RELOAD
sites (note-fetch `ev_note` + glide-arrival `fx_gl_chk`) read the raw table. FIX:
factor a shared `reload_base` subroutine (same redirect), `jsr`-ed from both.
0-regr by the wave-step's own byte-identical-tracking invariant; EVIDENCE: full
regression GREEN + 17/17 affected-path FULLs hold (extract-scan of 163 f1 FULLs)
+ 5 CIA FULLs (C25 added-`jsr` latch check) hold. code_hash 695293ec→7072fe23
(next batch auto-re-verifies). LESSON: an off-table freq index has THREE read
SITES (wave-step / note-fetch / glide-arrival) — a captured LIVE record is only
reproduced if the READING site honors it; audit every site. Post-fix sweep
DEFERRED per session instruction.

## 📊 CANON-DIFF WEDGE ACCOUNTING (2026-07-10): family-1 wedge space is ~fully handled — the residue is NOT a wedge problem
Built `tools/dmc_canon_diff.py` ([[reference_dmc_canon_diff]]) — the PROACTIVE
complement to the reactive `_*_probe` detectors: linear-align every member's player
code to the canon binary + diff opcodes/operand-repoints, cluster, tag handled/NEW,
split partial/full. DEFINITIVE result cross-referencing the fresh 188 f1 partials:
**147 (78%) carry NO code wedge** (pure off-table-freq/dynamic-state/CIA residue —
the C6/C11 hard tail), **32 (17%) a HANDLED wedge** (fail for another reason), only
**9 (4%) a genuine UNHANDLED patch — ALL singletons** (Complications, Cotton_Eye_Joe,
Enforcer_2, Ice_on_Fire, Jezuseczek, Logic_Intro, Mathematica_tune_3,
One_Man_and_Boris, Second). So there is NO multi-carrier unhandled-wedge lever;
one-wedge-at-a-time IS inherent. The remaining conversion headroom is the off-table
hard tail, not wedges. Also a COMPLETENESS AUDIT: true probe carrier counts
(track_loop 876, d418/wrapper 169, master_vol 113, rest-skip 129) ≫ docstring "3".
Surfaced 2 pre-existing bugs sampling had missed: unescaped member-address bytes in
`_pw_bound_shift_probe`/`_pw_dir_persist_probe` regexes (2 members ERROR on a
`[`=0x5B byte) + the 2SID-multisubtune scope gap (7 Rayden). Also landed Opp B
(commit b3685e6c): dedup `dmc_v4_config`'s copy-paste wedge dispatch into a
`_WEDGE_PROBES` table+loop (byte-identical, golden 5392/5392).

## ✅ ROUND 67 (2026-07-10): R-PHASE = PULSE TAIL, not register refresh — Toccata_v2 +1 partial → FULL (0 regr) [ledger C18 R-entry variant]
First still-partial f1 by hvsc path after RE-VERIFYING the stale Jul-9 batch
(`dmc_f1_dedup.jsonl`; the whole Bakewell run ahead of it flipped FULL in rounds
55–66): Bakewell_Dwayne/Toccata_v2 (vblank, single sub, 523140 writes). Trichotomy
play_match 883, first div `$D402` V1 PW lo, orig $10 vs reb $20 @ frame 30. ROOT:
`play_phases='P_R123'` but the init-generated parity wrapper's R phase is
`$1006→$162F: JSR $135D x3` — `$135D` is the pulse routine PAST its `STA $171F`
speed-nibble reload, so the R frame runs a SECOND pulse advance/tick from the STALE
$171F ($01 here → up phase-0 step $00 = hold, down phase-1 step $10 = −half-step).
Write-footprint observer read it as a refresh R (pulse HOLDS for ~6 frames, no
advance in the 12-call window); once the sweep moves the R frame's PW diverges (orig
advances, `fx_glide` refresh doesn't). FIX (C18 R-entry variant, twin of vibflip):
`factory._rphase_pulse_tail_probe` EXECUTION-watches for `JSR base+$35D` (the full
path reaches $135D only by fall-through, never JSR) → `rphase_variant='pulse_tail'`;
composer factors the sweep behind a `pw_sweep` label + a gated `pulse_tail` routine
(nibble-select step from stale `wjmp`=$171F by pwphase parity, jmp pw_sweep); R token
JSRs pulse_tail. Composer already writes wjmp where orig writes $171F → value
coincides. Census over ALL 743 non-canonical-play f1 = 1 carrier ⇒ 0-regr by
construction (label emits no bytes; gated code absent otherwise). Post-fix sweep
DEFERRED to next batch (session instruction); 4 short FULLs re-verified. LESSON: the
Jul-9 wide batch is stale — leading partials flip FULL; re-verify before picking.

## ✅ ROUND 66 (2026-07-09): NOTE+TRANSPOSE WRAPS OFF-TABLE (8-bit ADC) — Journey +1 partial → FULL (+5 siblings, 0 regr) [ledger C11 + C6/C7-(b) head]
First f1 partial by hvsc path (Groove=r65 now FULL; scanned idx 401+ fresh: 401/402
FULL, 403 = Journey partial): Bakewell_Dwayne/Journey (vblank, single sub, PAGE-3
build — state block @ $03xx not $17xx, shift −$13D6; freq/vibdepth tables also
relocated). Flat first-div pos 39435 = V3 drum freq lo $23 vs $00. GROUND TRUTH
(memwatch V3 accum $0361 / vstep $03BE, using Journey's dataflow-derived reloc):
the drum's curnote = $FC (=252) reads vibdepth[$FC]=$23 (the vibrato STEP) OFF-TABLE.
curnote $FC = pattern note 0 + transpose −4 via the 8-bit note-init ADC ($11A3),
which WRAPS a low note past the 96-entry tables. ROOT 1: reach model
`_assign_offtable_freq.add_note` gated `if n>95` on the RAW SIGNED sum (note+tr=−4)
→ missed all 24 negative-transpose wrapping rows. FIX 1 (ledger C11, extract):
`n &= 0xFF` at add_note entry → capture off-table VIBDEPTH for wraps. Div moved
39435 → 92108 (V3 drum freq lo $03 vs $17). ROOT 2: the $1888 vibdepth table
OVERLAPS the note-init routine; indices 3,4 = the vstep-STORE operand ($1792 canon)
— RELOCATES for page-3 builds ($03BC = $BC,$03). curnote $04 reads vibdepth[4]=$03
(Journey) vs the composer's hardcoded canonical VIBDEPTH[4]=$17. FIX 2 (C6/C7-(b),
extract+composer): capture the member's actual vibdepth head byte where a note reads
idx 0-5 AND it differs from canonical (`elif n<6 and mem!=VIBDEPTH[n]`); composer
overrides `_vd[note]` IN PLACE (no table-size change). Regression-safe by
construction: canonical-layout members' head == canonical → no capture. Journey FULL
267375/267375 state ✓. AMEND (Other_Side.sid FULL→partial, caught in the flip-set
census — real, not a C20 flake): FIX 1's off-table FREQ capture placed a WRONG
PER-SUBTUNE value (flo+254 = $00 in subtune-0 but inst-6's reaching subtune = $5E →
static window last-writer-wins → $5E). Root: a wrap (note 0 − k → 250-255, the
drum/silent idiom) reads freq-table-adjacent PER-SUBTUNE engine state (not statically
representable) and its base freq is drum-overridden or $0000. FIX 3: capture VIBDEPTH
for wraps (static instr-record, needed) but NOT FREQ (`if not wrapped`). Both restored
to FULL. FLIP-SET CENSUS (192 wrap-carriers full + 130 head-differ sample, before/
after vs pre-fix stash): **0 regressions, +6 gains** (Journey wrap+head; Mad_Drummer/
Remembrance/Total_Eclipse/Next_Door wrap; Quarks_2 head). Full tools/regression.py
GREEN (0 regr all 7 families). HEAD-FIX BREADTH: 572 f1 members have a relocated
vibdepth head (idx 3/4 differ, head bytes vary per state-block address) → flip-set =
the READERS; the head byte is a STATE-ADDRESS operand = C7-(b) state-as-data → FLAG
for /uready-review as a B-class capture. Post-fix full-family sweep SKIPPED per user
(next batch accounts via code_hash; +6 flip-set-confirmed, likely more head-readers).
LESSON: an 8-bit table index computed by ADD (note+transpose) WRAPS — classify/capture
on `&0xFF`, never the signed sum (C11); but split by representability — off-table
VIBDEPTH lands on static instr-records (capture), off-table FREQ of a wrap lands on
per-subtune state (residue, skip). f1 ≈ 5169 FULL / 232 partial (per-round; +6
flip-set-confirmed, wide batch STALE).

## ✅ ROUND 65 (2026-07-09): $D418 RE-ASSERTED EVERY FRAME (filter-tail wrapper) — Groove +1 partial → FULL (0 regr) [ledger C19 10th occurrence / C10] — COMPOSER param
First f1 partial by hvsc path (Attacker=r64 now FULL; scanned idx 382+ fresh, all
FULL until idx 400): Bakewell_Dwayne/Groove (vblank, single sub). Flat first-div
pos 2. Per-frame dump: ORIG writes `$D418=$1F` (LP mode $10 | mvol $0F) ONCE PER
FRAME at the END (after $D416/$D417), even on gate-off frames; REBUILD wrote
`$D418` at each FILTER NOTE-INIT and not at frame-end (= canon: $D418 only at
init + note-init $12A8). ROOT (C19 wedge, disasm): play-body filter routine
`$10AC: STA $D417` → `JSR $2000` wrapper (`STA $D417 / LDA #$10 / ORA $1717 /
STA $D418 / RTS`) = per-frame $D418; note-init `$12A8: STA $D418` neutered to
`BIT $D418`, preceding `STA $2004` self-modifies the wrapper's mode imm per
note-init. FIX (CORE TENET reproduce the WRITE, COMPOSER param not extract-only
since it's a write TIMING): `factory._master_vol_reassert_filter_tail_probe` (static opcode
probe anchored on the LIVE play-body routine `STA $D416 / LDA abs / ORA abs /
JSR-wrapper`, reloc-invariant hardware addrs) → USF param `master_vol_reassert_filter_tail`
(init mode imm) → composer: note-init stores `fdmode` to a `d418mode` shadow
(SUPPRESS note-init $D418), filter tail appends `lda d418mode / ora mvol / sta
$d418`, init primes `d418mode`. Sibling of `master_vol_every_play` (play-START form);
this is the filter-tail END form + C10 master-vol-every-frame. Default None →
byte-identical. TRAP CAUGHT (why the probe is ANCHORED): the first LOOSE probe
(`STA $D417..STA $D418` anywhere) false-fired on Qbhead_01's aux routine $1CA8
whose live filter routine is canonical — would have REGRESSED a FULL. Caught by
localizing each carrier's first-div (orig had no per-frame $D418). Tight anchor
excluded it. CENSUS (all 5401 f1): exactly 3 carriers (Groove $10, Hands_up_Ravers
$20, For_Vandalism_27 $10), ALL previously partial ⟹ 0 FULL exposure; all 3 verify
FULL. Groove FULL 155620/155620 state ✓. Full tools/regression.py GREEN (0 regr
all 7 families: Hubbard 71, Companion 44, C64ME 15, Jay_Derrett 17, FC 31, DMC 12,
Basic 22). Post-fix sweep SKIPPED per user (next batch accounts via code_hash;
+2 siblings census-confirmed). LESSON: a STATIC opcode probe must anchor on the
REACHABLE site (the play-body computation), never a matching byte pattern anywhere
in the image — verify each census carrier's first-divergence BEFORE committing.
f1 ≈ 5163 FULL / 238 partial (per-round; wide batch STALE).

## ✅ ROUND 64 (2026-07-09): RESET-ALL loop target can be PER-VOICE (not one N) — Attacker +1 partial → FULL (0 regr) [ledger C13 refinement²]
First f1 partial by hvsc path (End_of_1992_intro r60 / Acid_Dance r61 / Action_G
r62 all now FULL, re-confirmed): Bakewell_Dwayne/Attacker (vblank, single sub,
dataflow route). Flat first-div 143638 = 98.8% of the ×1.1 window = deep in the
LOOP TAIL, state ✓. Signature: a SYNCHRONIZED 3-voice hard-restart (all voices prep
ctrl=$08/AD=$0F/SR=$0F → note-init together) + a $D418=$1F master-vol write, but the
rebuild resyncs only V2/V3 while V1 keeps sweeping ONE play() longer. GROUND TRUTH
(`--memwatch 1726,1727,1728`): at the divergence orig track pos jumps V1 26→4, V2
53→31, V3 26→4 = a loop-back with a DISTINCT target per voice. Disasm: $FF handler
`CMP #$FF / NOP NOP / JSR $1020 / JMP $10D2`, $1020 = `LDA #3/STA $1726 / LDA #$1E/
STA $1727 / LDA #3/STA $1728` = reset-all to 3/30/3 (→4/31/4 after the fetch INC).
The round-53/62 idiom but the 3 immediates are UNEQUAL → round-62's equal-imm guard
skipped it → track_loop_target stayed True (read-next) → V1 walked past $FF. FIX
(extract-only, dataflow, ledger C13): loop_reset_pos scalar N → per-voice tuple
(n0,n1,n2); drop equal-imm requirement but ANCHOR the STA triple to the track-pos
address (operand of `LDY tpos,x` [BC] immediately followed by `LDA (zp),y` [B1],
reloc-safe) so a non-reset-all 3-consecutive-store init can't false-match.
`_walk_track` gets the per-voice scalar (extract call site indexes the tuple by
voice). NO USF field, NO composer change (walk emits the resolved per-voice
orderlist; loop_reset_pos = §8 extract-time derivation knob). REGRESSION-SAFE BY
CONSTRUCTION: equal-imm path byte-identical (round-53/62 carriers unchanged:
Unfinished_1/Feelin_Blue None, Action_G 5, Axel_F_v2 4, MON_Tribute 5); per-voice
branch = positive minority anchored to track_pos. CENSUS (dataflow.locate over all
5401 f1): exactly 1 tuple carrier — Attacker (previously partial) ⟹ 0 FULL exposure.
Attacker FULL 145313/145313 (state ✓). Full tools/regression.py GREEN. Post-fix
sweep SKIPPED per user (next batch accounts via code_hash). LESSON (round-62's, one
level deeper): a positive-minority signature carrying literals — the SHAPE is the
discriminator, EACH literal is per-voice DATA; don't presume the literals equal any
more than you bake in their value. f1 ≈ 5162 FULL / 239 partial (per-round
accounting; wide batch STALE at current code_hash).

## ✅ ROUND 63 (2026-07-09): INIT-PREFIX subtune force — extract walked the DUMMY tune record — Sans_intro +1 partial → FULL (0 regr) [ledger C19 9th occurrence]
Picked from the census's LARGEST partial bucket ("$D406 V1 SR @<64", 27 members) —
but the wide batch is fully STALE (0 rows at the current code_hash; mostly the
round-48 0c127d5 era), so every stored flat_div is stale and pos-0 on CIA tunes is
the CIA-init artifact. Re-cut: 25/27 vblank (13 Bayliss = round-45 garbage
subtunes), 2 CIA (Rayden remakes). Fresh per-IRQ localization showed the bucket is
NOT one root cause — it's an aggregate of "first divergence lands in an early V1
note-init." Picked a clean single-sub vblank rep: Stryyker/Sans_intro (flat div 0,
V1 SR). ROOT (ground truth): rebuild's V1 played a static gate-off note where orig
plays a gliding gated note; the extracted USF had `voice 1 { orderlist: stop }` —
the whole V1 (+V2) part DROPPED. Runtime track ptr $1707/$170A (memwatch) = $1A36 =
tune-table RECORD 1; extract walked RECORD 0 ($1A28 = `$FE` stop dummy). WHY: the
PSID init = $0FFE = base−2 = `A9 01` (LDA #$01) falling through into `$1000:
4C 1D 10` (JMP $101D = tune-select, `A*8→Y`), hard-forcing record 1 for EVERY play
regardless of the song number (pc-trace `$101d f 01`, `$180d ... 1ac6,Y [1ace]`
Y=8 confirm). A C19 hand-patched wedge, but a 2-byte INIT WRAPPER not a body patch,
and a DERIVATION wedge (changes WHICH record is content) → EXTRACT-ONLY:
`factory._forced_subtune_probe` (init≠base + `mem[init]==$A9` + base is the canon
`JMP base+$1D` dispatch + the LDA#imm reaches it by fall-through or `JMP base`) →
new `DMCV4Config.forced_subtune` → `engine_model.extract` walks `rec = tunetab +
forced*8` (+ threaded to `_loops_offimage`). NO USF field, NO composer change (the
composer plays the walked content; forced index = engine artifact per principle
§8). REGRESSION-SAFE BY CONSTRUCTION: `forced` None for canon init==base
(byte-identical); imm==0 = record-0 walk; dispatch guard rejects banking/other
LDA#-leading wrappers. Census over 5833 f1: exactly 2 carriers, both previously
partial (Sans_intro fall-through + Devilock/Sub_Effect JMP-to-base) ⇒ 0 FULL
exposure. Sans_intro FULL 255559/255559 state ✓. Full tools/regression.py GREEN
(0 regr all 8 families: Hubbard 71, Companion 44, C64ME 15, Jay_Derrett 17, FC 31,
DMC 12, Basic 22). Post-fix bucket sweep SKIPPED per user (next batch accounts via
code_hash — Sub_Effect the census-confirmed +1 likely partial→FULL). TELL: a
rebuild playing a voice's PRIMED IDLE NOTE under `orderlist: stop` while orig plays
a full part = wrong-tune-record walk — memwatch runtime track-ptr $1707/$170A +
pc-trace the init A at the tune-select. f1 ≈ 5161 FULL / 240 partial.

## ✅ ROUND 62 (2026-07-09): RESET-ALL hook target need NOT be 0 — loop-to-N — Action_G +1 partial → FULL (0 regr) [ledger C13 refinement]
First f1 partial by hvsc path (user-picked; End_of_1992_intro=round60,
Acid_Dance=round61 both now FULL): Bakewell_Dwayne/Action_G (vblank, single sub,
otrk_legacy/dataflow route). Flat first-div 108842 (97.5%) at a V1 SR write =
the LOOP-BACK point. Ground truth: pc-trace the `$FF` handler ($10DF `JSR $1020`;
$1020 = `LDA #5/STA $1726 / LDA #5/STA $1727 / LDA #5/STA $1728`) = RESET-ALL-to-**5**
(a SYNC loop to track pos 5, NOT 0 — the intro block pos 0-4 plays once, the loop
body restarts at the byte-identical `A1 01 01 01 05` at pos 5). Memwatch $1726
trajectory `…2E → 06` confirms (lands on the transpose marker at pos 5, advances
to 6 — reset-to-0 would show pos 1). ROOT: round-53's reset-all detector
hardcoded `mem[...]==0x00` (loop-to-0), so this N=5 variant stayed
`track_loop_target=True` (read-next) → the walk read `$FF`+1=`A1`=161 as a jump
target, marched past the terminator into garbage (entry_offsets `…45, 161, 162`,
self-loop on offset 162). FIX (extract-only, dataflow): generalize the round-53
idiom to capture the immediate N (require all 3 LDA EQUAL; the discriminator is
the equal-imm + consecutive-addr SHAPE, N is the target) → new
`DMCV4Config.loop_reset_pos` (None ≡ loop-to-0/read-next) threaded to
`_walk_track` (`tgt = loop_reset_pos` at `$FF`). NO USF field, NO composer change
(the walk emits the correct resolved orderlist; loop_reset_pos is a derivation
knob consumed at extract time). REGRESSION-SAFE BY CONSTRUCTION: N==0 leaves
loop_reset_pos None ⟹ the 6 round-53 reset-all-to-0 carriers build byte-identical
(all 6 confirmed track_loop_target=False/loop_reset_pos=None). CENSUS over 5833
f1 members: exactly 3 N>0 carriers (Action_G N=5, Axel_F_v2 N=4, MON_Tribute N=5),
ALL previously partial ⟹ 0 FULL exposure = the round-53 theorem holds. Action_G
FULL 111670/111670 (100%, state ✓). Full tools/regression.py GREEN (0 regr all 7
families: Hubbard 71, Companion 44, C64ME 15, Jay_Derrett 17, FC 31, DMC 12,
Basic 22). Post-fix sweep of the 2 sibling carriers SKIPPED per user (next batch
accounts via code_hash — likely +2 more partial→FULL). LESSON: when a
POSITIVE-minority signature carries a literal (the immediate here), don't bake the
literal into the discriminator — the SHAPE is the discriminator, the literal is
DATA to capture. f1 ≈ 5160 FULL / 241 partial.

## ✅ ROUND 61 (2026-07-09): arm F-phase ENTRY variant — wavestep vs vib_half — Acid_Dance +1 partial → FULL (0 regr) [ledger C18 note]
First f1 partial by hvsc path (user-picked; End_of_1992_intro row stale =
round 60): Bakewell_Dwayne/Acid_Dance (CIA 4x, P_F123_F123_F123,
noteinit_deferred, the round-46 rest_effects='vibflip' singleton). Flat localizer
pos 0 = the CIA init-phase artifact — per-IRQ first div at play pos 51198:
V2 flo $6C vs $64 on a HELD note; orig's vibrato = a ±4 SQUARE
($268↔$26C, 4 IRQs per level), rebuild = a free-running ±16 triangle.
Memwatch ground truth: orig V2 vibdir FLIPS + vibctr resets on every F call
(3 flips between full plays); acc only moves on P. ROOT: the wrapper's F
phase enters the player at canon **$1567 = the vibrato half-cycle boundary**
(vibctr=0, flip vibdir, swell, FALL THROUGH wavestep) — not $1591 (plain
wavestep) as the composer's noteinit_deferred F target assumed. Wrapper: SMC
JSR-operand table $1D50 → JT slot $1006 → JMP $162F = `LDX#0/JSR $1567 ×3`.
The two entries emit IDENTICAL writes on the F call itself — the difference
is vibrato STATE, observable only later as the vibrato's shape, so it's a
C18 entry-reachability observation, not a footprint one. FIX:
`factory._detect_effect_entry_variant_vibhalf` (shape-locates $1567 `a9 00 9d ?? ?? bd
?? ?? 49 01 9d` reloc-invariant; pctrace watch_pcs; vib_half iff EVERY F
invocation (voice writes, no $D416) executes a candidate — a wavestep-entry
F call can never reach $1567 ⇒ no false positive, gated on noteinit_deferred at
both factory sites) → USF param `effect_entry_variant: vibflip` (vocabulary shared with
rest_effects='vibflip' = the $1180 rest-tail patch this member ALSO carries;
two INDEPENDENT edits, not derived from each other) → composer `voice_fx`
JMPs its own `vib_half` label (falls through wavestep = orig control flow).
Acid_Dance FULL 360120/360120 state ✓. EXPOSURE: all 19 stored
noteinit_deferred FULLs probe False → builds byte-identical; full
tools/regression.py green (0 regr all 7 families). CENSUS (probe over all
224 stored partials): exactly 2 carriers — Acid_Dance + Odysseus/
Hear_Circa_2_Minutes (unswept; the fix applies to it iff its config also
detects play_phases+arm). Post-fix sweep SKIPPED per user (next batch
accounts via code_hash). f1 ≈ 5159 FULL / 242 partial.

## ✅ ROUND 60 (2026-07-09): PW-DIRECTION reset redirect wedge — End_of_1992_intro +1 partial → FULL (0 regr) [ledger C19 8th occurrence]
First f1 partial by hvsc path (user-picked): Artlace/End_of_1992_intro (CIA,
single sub, flat div 6637 stable across 4 code eras; flat localizer said pos 0
= the CIA init-phase artifact — re-localized per-IRQ). Divergence: V2 note-init
at play 387 — both write PW=$0400 fresh, next frame orig sweeps DOWN ($03E0,
continuing the pre-note direction) vs rebuild UP ($0420). ROOT: C19 wedge —
canon $1266 `STA $1765,x` (PW direction=up in the note-init pulse reset) has
its operand re-pointed at $17AB (the unused $179E-$17AF state gap), so the PWM
sweep DIRECTION persists across note-inits while value/bounds/step/phase still
reset. FIX (C19 canonical form): `factory._pulsewidth_dir_persist_probe` (static
reloc-aware anchor `A9 00 9D <base+$762> 9D <op>`, positive minority op !=
base+$765, ambiguous→None) → `pulsewidth_dir_persist` param → composer drops the one
`sta pwdir,x` line from pw_base_reset. Census (anchored on the stepbase→phase
delta-3 prefix; a loose `A9 00 9D .. 9D ..` scan false-positives on other canon
LDA#0/STA/STA sites): exactly 2 carriers in 5808 site-bearing members, BOTH
partial → 0 FULL exposure, regression-safe by construction. End_of_1992_intro
FULL 125002/125002 state ✓. 2nd carrier Black_It: wedge redirects to base+$786
= post-note guard — ALSO inert (note-init overwrites guard=2 right after);
its own blocker is earlier (play_match 26 from the first note), per-sub
divergences byte-identical before/after = no movement. Post-fix sweep SKIPPED
per user (next batch accounts via code_hash). f1 ≈ 5158 FULL / 243 partial.

## ✅ ROUND 59 (2026-07-08): SUBTUNE-AWARE off-table post-init capture — Cool_Musax +1 partial → FULL (0 regr) [ledger C6 note]
First f1 partial by hvsc path (user-picked): Akadem/Cool_Musax, sub 1 flat div
3029, V2 freq-hi orig $17 vs reb $F8 on a note-init. pc-trace: wave off 60 +
note 36 = idx 96 → fhi read $1707 = V1 TRACK-PTR LO — per-subtune INIT-WRITTEN
state (subtune values F8/17/26/2E/53; taint STATIC during play). ROOT: the
ENTIRE off-table value capture was SUBTUNE-BLIND — `_postinit_values` +
`_offtable_eventdriven` sample only the DEFAULT start song, so records reached
only from another subtune inherit the wrong subtune's init state (idx 96 kept
start-song $F8; idx 98 likewise wrong, 101/103 coincidentally right). FIX
(extract-only): `_assign_offtable_freq` tracks which songs REACH each
(inst,off,note) record (`m.offtable_songs` + `m.offtable_vib_songs`; idle
records deliberately unattributed); `_postinit_values` gains `subtune=`;
`_correct_offtable_postinit` samples per reaching subtune and uses that value
only when ALL reaching songs are sampled and AGREE — any ambiguity falls back
to the start-song sample = old behavior. REGRESSION-SAFE BY CONSTRUCTION: a
FULL's served value already matched every subtune's stream → per-subtune
capture returns the same value → byte-identical. Cool_Musax FULL 5/5 subs
(sub 1 42107/42107). Full tools/regression.py green (0 regr all 7 families);
10-member multi-subtune-FULL exposure sample all FULL. Partials sweep STOPPED
by user at 51/231 (accounting deferred to the next family batch via code_hash;
7 batch-FULLs of which Bakewell ×3 + Nocturno = known C20 palimpsests; likely
genuine new: Under_the_Ground_preview, Megahardcoretrancetechnorave_95).
Event-driven correction left subtune-blind (still default-song) — a member
needing a non-start-song event-driven value stays residue; extend if a chase
finds one. NB: extract now runs one 6s memwatch siddump PER reaching subtune.

## ✅ ROUND 58 (2026-07-08): gate hold+never-release = INDEPENDENT editor flags — lossy gate_mode enum — Strain_2 +1 partial → FULL (0 regr) [ledger C30 NEW] — commit 8850c74d
Random f1 partial Phobos/Strain_2 (CIA, per-IRQ div 156750/439569, state ✓):
ALL 2865 tail mismatches = ONE V3 note, fhi orig $18 vs reb $10 (flo matches).
pc-trace: note-init eff. note $D8=216 → off-table freq-hi read $16A7+216 =
$177F = V3's fx-flags cache (the round-39 fxf redirect row — the MECHANISM was
right, the VAR VALUE wrong). ROOT: instr byte 10 = $18 = HOLDING($10) +
NO-GATE-FX($08) BOTH set — the TND tutorial documents them as independent
editor toggles; our 3-value gate_mode enum assumed exclusivity, iflags()
rebuilt $10. Engine tests $10 first ($132D) so the co-set $08 is mechanically
dead (audibly $18≡$10) — observable ONLY via the fxf state-as-data read. FIX
(ledger C30): elidable `EnvelopeConfig.gate_open` bool (grammar/parser/writer/
spec updated per usf_sync), extract `(fx&0x18)==0x18`, iflags() ORs bit 3
back. NOT a 4th enum value (a categorical duplicating 'hold' hides the
similarity the boolean makes explicit), NOT a raw byte (Pole B).
REGRESSION-SAFE BY CONSTRUCTION: composer mirrors the orig's bit priority →
the bit reaches the stream only via fxf reads, where the old build already
diverged (a FULL with such a read couldn't exist). CENSUS (extract-level,
235 stored partials): 25 both-bits carriers; sweep = Strain_2 FULL
439569/439569 + Rem_Phase_2 first-div DEEPER 209955→254277 + 20 unchanged
(deeper blockers) + 3 Bakewell "flips" = round-53 palimpsest rows (C20 —
in the round-53 flip list, already FULL under parent). Full regression green
(0 regr all 7 families); truth merged; mass-write ok=265 err=0. TRAP re-hit:
`dmc_family_batch.py --help` RUNS the full batch (no argparse) — killed in
time; its few appended rows carry the current hash (valid). LESSON: any USF
enum derived from a FLAGS byte whose source bits are independent editor
toggles is lossy-suspect — round-trip-verify the reconstruction per
instrument (round-39 lesson, now with the failure case found). f1 ≈ 5157
FULL / 244 partial.

## ✅ ROUND 57 (2026-07-08): play-phase F misread as R on a HELD note — frame-entry reachability — My_Rusty_Love_C64 +1 partial → FULL (0 regr) [ledger C18 note]
Random f1 partial Psych858o/My_Rusty_Love_C64 (CIA 6x, re-assembled, dataflow
route). Per-IRQ trichotomy: at the first HELD note the orig re-asserts V1
AD/SR=$00 EVERY call (sub_17EC — the holding gate-off fires every call while
the duration counter sits at 1; dur DECs only on TICK frames), the rebuild
only on a 6-cycle. ROOT: the wrapper's 5 non-P sub-phases run the FULL frame
entry per voice-mask ($18F1 mask tables → JMP $11FA), but the offset-blind
observers' chip-state R/F rule read 3 of them as R — a held note's frame entry
emits only IDEMPOTENT writes for the whole window, so nothing "advances"; the
composer's R emission (glide+write tail) then drops the AD/SR re-asserts. FIX:
`factory._frame_entry_candidates` (shape `bd ?? ?? d0 03 4c`) + PC-watch in
`_observe_play_phases_writes` + `watch_pcs` on `pctrace_per_play_capture`;
F iff frame-entry reached OR advancing (a true refresh reaches neither → no
false F; round-53 lesson: positive minority detection, no default flip).
EXPOSURE: 25 stored R-token FULLs all genuinely tail-only (tokens unchanged,
3 rebuilt byte-identical); flip census over ALL 236 f1 partials = exactly 1
carrier → FULL 388489/388489 state ✓. Full regression green. METHOD: segment
the flat stream into PER-VOICE BLOCKS (ctrl closes a block) and diff block
shapes — 386k writes → a one-glance `✓✓✗✓✗✗` pattern naming the wrapper
period. f1 ≈ 5156 FULL / 245 partial.

## ✅ ROUND 56 (2026-07-08): OUT-OF-IMAGE loop sector = engine sonifies live ZEROPAGE — Killer_Beat +4 GENUINE partial → FULL (0 regr) [ledger C29 NEW]
Random f1 partial Mephisto/Killer_Beat (vblank, flat div 93464 = 77%). V1 plays
note47/note55 where reb plays note0, then both re-sync on the C-0 outro (a clean
2-note substitution deep in the song; the notes are ABSENT from any V1 pattern).
ROOT: V1's track ends `$FF`(loop)@pos39, next byte $A0=160 (track_loop_target,
CORRECT per memwatch otrk 39→160); track pos 160 = sector 26 whose ptr =
**$0000** (garbage sector# past the ptr table). File image is $00 below load, so
the extract decoded 256×note-0; but at RUNTIME the sector reads live ZEROPAGE via
`($F8),y`=$0000 → pc-trace `[0000]{2F}`=note47, `[0001]{37}`=note55 = the 6510
I/O port (DDR $2F/port $37, PSID env defaults), then static zp ($67=instr-7 +
$1C=note28 → the $FF00 off-table region). taint (160s): ONLY $F8/$F9 written, and
those read $00 from V1's own $0000 ptr → the whole outro is STATIC/reproducible.
FIX (ledger C29, extract-side): `_loops_offimage` gate ($FF loop → sector<load) →
capture runtime low-RAM `_postinit_values(range(0x100))` (libsidplayfp; py65
can't reproduce env zp = C9) → overlay onto `mem` before `_walk_track` with
mem[$00/$01]=$2F/$37 (port, not RAM-under-it) + mem[$F8/$F9]=$00 (sector base).
off-table reach model auto-captures note28/instr7→$FF00. REGRESSION-SAFE BY
CONSTRUCTION: overlay only changes the decode of out-of-image sectors, which hits
the write-log only if PLAYED — a played out-of-image sector was ALWAYS
mis-decoded (image≠runtime) ⟹ member non-FULL; unplayed decode = byte-identical
(no-OOB FULL builds identical MD5; full tools/regression.py green 0-regr all 7
families). CENSUS (44 f1 STORED-partials carry the signature; batch flipped 14, but
re-baselining vs PARENT b81785e5 — amend Step 3.4 / C20 — gives **4 GENUINE
partial → FULL**: Killer_Beat 121386/121386, Axel_Foley, Remix_1995, PVCF
Centric_tune_4). The other 10 batch-FULLs (9× Flash + Wodnik Narwana) were
ALREADY FULL under parent = stale palimpsest rows predating round 55; my overlay
is neutral (their OOB sector is UNPLAYED → byte-identical). 29 stay partial;
1 pre-existing 2SID-multisubtune error (Leprechaun_Boot_V1_2SID, exonerated vs
parent build). Resolves the RE_NOTES bucket-8 "sector at $0000 never ends" class
for the static-zp majority. LESSONS: (1) a deep 2-note substitution that
RE-SYNCS = a loop-target/sector-ptr bug — trace otrk (memwatch) + pc-trace the
($F8),y effective address; if it lands in zeropage the engine sonifies the
ENVIRONMENT (taint static-vs-dynamic, read runtime RAM not file image).
(2) C20 re-confirmed: the stored jsonl before-status is NOT a baseline — 10 of
the 14 batch-FULLs were palimpsests already FULL under parent; ALWAYS re-verify
apparent flips vs a fresh PARENT-code build before counting.

## ✅ ROUND 55 (2026-07-08): HARD-RESTART PREP-CALL SKIP wedge — Seaside_99 +9 partial → FULL (0 regr) [ledger C19 7th occurrence]
Random f1 partial SilverFox/Seaside_99 (vblank, flat div 197). Per-IRQ diff
(Trap-C-free) localized it: at the note-FETCH frame the rebuild emits an EXTRA
prep block `D40x=08/0F/0F` (TEST+AD/SR) the orig LACKS; the note-INIT frame is
byte-identical. Memwatch showed orig pending ($174C)=FF = hard-restart path
TAKEN — contradicted "no prep" until pc-trace gave ground truth: `$11DB = 2c fb
17 = BIT $17FB`, NOT canon `20 fb 17 = JSR $17FB`. 1-byte opcode patch $20->$2C
neuters the WHOLE prep call (BIT reads $17FB, writes nothing → fetch frame emits
NO writes; pending still set so note inits next frame normally). Classic C19
STATIC wedge. DISTINCT from `hard_restart='none'` (family-2 keeps the $08 TEST)
and the round-36 numeric preset wedge (patches sub_17FB's immediate). FIX:
`factory._hr_prep_skip_probe` (STATIC opcode probe, reloc-aware, verifies shape
both sides) → EXISTING `hard_restart` param, 4th value 'skip'; composer
suppresses BOTH hr_test_write + hard_restart_adsr in ev_n_hard (+ grouped 'skip'
with 'none' in the ADSR branch to avoid `int('skip')` crash). CENSUS TRAP: some
carriers ALSO patch sub_17FB byte $99->$60 (RTS) — irrelevant (call neutered),
so census keys on the call-site opcode + reloc-invariant `op-code_start==$622`,
NOT sub_17FB's shape (first census keyed on sub_17FB `99/B9` → false-negatived
ALL 9). Census over 5401 f1: exactly 9 carriers (Welcome_to_Egypt, Bayliss ×4,
DaFunk ×2, SilverFox ×2), ALL partial (0 FULL exposure) => regression-safe by
construction; **ALL 9 partial → FULL**. 0 f2 carriers. Full tools/regression.py
GREEN. Promoted the scratch build helper to `tools/dmc_build_one.py` (build one
member → .sid+.usf, --verify/--localize) — user-requested. LESSON (repeats
round 50): when a derived value's memwatch/runtime disagrees with expected,
pc-trace the ACTUAL executed opcode — disassembly.s can be locally patched per
member. f1 ≈ 5155 FULL / 246 partial (per-round accounting; baseline STALE).

## ✅ ROUND 54 (2026-07-08): FIRST-NOTE DURATION = post-init $173E (init CLEARS it to 0), not the _Sticky default 1 — +3 FULL, 0 regr — commit be656cad [ledger C11 note]
Random f1 partial Harti/Klepkomania (vblank, flat div 53, sub3 only; 6/7 subs
FULL). PLAY-SPLIT of the flat write stream: at play 4 orig emits V1's full block,
rebuild SKIPS V1 (jumps to V2) — V1 goes inactive one play EARLY, its free-running
PW-sweep phase shifts vs V2/V3 forever (counts off by exactly 5 = one V1 block;
V1's own value stream byte-identical). ROOT: sub3 V1 = a single decorative note
(`[inst15][note][$7F]`, NO `$80-$BF` dur command). note-load reads reload $173E,x;
init's `$1718-$179D` wipe zeros `$173E-$1740`, so a first note before any dur
command plays for reload 0 (`$173B` DECs 0->$FF = held 256-tick note). `_Sticky`
seeded dur=1 -> too-short -> hit the `$FE` terminator one play early -> `$FE`
handler RTSs (skips frame_entry) one frame sooner than orig. FIX (1 line,
`_Sticky` default dur 1->0). py65 POST-INIT($173E)=0 all subtunes + empirical
dur-sweep (0/32/63 FULL, 1/6 partial) confirm. REGRESSION-SAFE BY CONSTRUCTION: a
first row preceded by a dur command has st.dur OVERWRITTEN -> byte-identical
(FULL-side flip-set = **0 of 1200 f1 FULLs change build**). Evidence: partial
flip-set 30/253 changed -> **+3 partial->FULL** (Klepkomania 7/7, Compod/Nocturno,
Wodnik/Narwana) + 26 first-div moved DEEPER + 0 regressions; full
tools/regression.py GREEN (0 regr all 7 families). TRAP (amend, ~1h): first seeded
from durrel_init = FILE IMAGE ($173E=8) — WRONG (init clears to 0), regressed
another Klepkomania subtune; the file image, the default 1, AND the libsidplayfp
runtime memwatch ($173E=6, a py65/libsidplayfp during-play divergence) all misled
— only py65 POST-INIT + the empirical sweep gave 0. LESSON (ledger C11): a
first-event param read from ENGINE STATE that INIT CLEARS must seed from the
POST-INIT value, not the file-image leftover. Left round-31 durrel priming
untouched. NB f2 uses the same `_walk_track`/`_Sticky` — the fix likely helps f2
bare-first-row partials too but was NOT swept this session (f2 portfolio canaries
green). f1 last-known ≈ 5149 FULL (baseline STALE — per-round accounting, no fresh
full sweep since round 48's `code_hash 0c127d5`; all wide-results rows pre-current-hash).

## ✅ ROUND 53 (2026-07-08): RESET-ALL-VOICES loop hook = loop-to-0 — Unfinished_1 +6 partial → FULL (0 regr) [ledger C13 new note]
Random f1 partial Bakewell/Unfinished_1 (CIA 2x, otrk_legacy). Trichotomy
first-div at play pos 140688/142224 (98.9%, ×1.1 loop-tail ~89s), state ✓: V1
SR orig $F0 vs mine $F9 = a NOTE-FETCH divergence at the LOOP-BACK (orig plays
fresh idle note curnote 254/instr 0; reb keeps looping instr 3). ROOT CAUSE: the
$FF loop hook is a THIRD, unmodeled form. Runtime otrk ($1726) trajectory
(`--memwatch-on-write D404 1726,1012,1015`, ≥2 passes) = clean periodic
`1..21,1..21,1` → orig loops the WHOLE track to entry 0. But extract had V1
loop_to=20 + a bogus entry 20 at byte 131, from `track_loop_target=True` reading
pos21 $FF + pos22 $82=130 as a jump. Disasm: `$FF` handler = `CMP #$FF / NOP NOP
/ JSR $1020 / JMP $10D2`, `$1020 = LDA #0/STA $1726 / LDA #0/STA $1727 / LDA #0/
STA $1728` = RESET ALL 3 VOICES to 0 (a SYNC restart) = semantically loop-to-0.
These members carry a wedge so they FAIL the canon masked-compare
(`player_code_mismatch`) and build via the DATAFLOW path, whose rule
`track_loop_target = loop_site is None` (canon-STA sig absent ⟹ assume read-next
JSR) mislabeled reset-all as read-next=True. FIX (DATAFLOW ONLY): keep the base
rule `loop_site is None` (read-next members keep True regardless of zp) + flip to
False ONLY on a POSITIVE match of the exact reset-all 3-pair idiom (`A9 00 8D a /
A9 00 8D a+1 / A9 00 8D a+2` to consecutive track-pos addrs) in the reachable
trace. ⚠️ THE TRAP (amend Step 3.2): my FIRST fix flipped the DEFAULT (True only
if a read-next `c8 b1 f8 9d` idiom is scanned, else False) — a census caught
that as the SAME "not-A⟹B" mistake INVERTED: relocated read-next hooks use a
different track-pointer zp ($58/$61/$68… not $f8) → a fixed-$f8 scan
false-negatives them → a genuine read-next member REGRESSES to loop-to-0. The
canonical form detects the MINORITY (reset-all) by a positive signature verified
absent from the majority (0 occurrences in canon + all 848 read-next members) →
NO false positive = regression-safety is a THEOREM. CENSUS (static, all DMC v4
clusters): exactly 6 carriers, all Bakewell (Goodbye/Feelin_Blue/Survival/
Toccata_v3/Techno_Inc_2/Unfinished_1) — ALL 6 partial→FULL; loop-hook form
census over f1: canon_sta 3443, read_next 848 (all keep True), jsr_other 62,
reset_all 6. f2 (bypasses the loop probe via `_family2_build`) + v5 (separate
pipeline): 0 carriers, unaffected. Full tools/regression.py GREEN (0 regressed
all 7 families). LESSONS: (1) a note-fetch divergence deep in the loop-tail
(state ✓, perfect prefix) is a LOOP-BACK bug — trace the runtime otrk/curnote
trajectory over ≥2 passes + read the orig $FF handler; don't trust walked
entry_offsets when the runtime counter never reaches them (the otrk_legacy/
off-table-131 framing was a RED HERRING). (2) When a probe splits variants with
an "else⟹the other form" default, DON'T flip the default (you only move the
blind spot) — detect the minority form positively. f1 ≈ 5146 FULL / 255 partial.

## ✅ ROUND 52 (2026-07-08): DOUBLE-SPEED base+3 JMP wrapper — Scan_Collection_end +9 partial → FULL (+10, 0 regr) [ledger C24/play_repeat note]
Random f1 partial Scan_Collection_end (Lio, vblank). NOT a content divergence:
play_match == play_overlap (perfect prefix) but len_post_a 429373 vs len_post_b
215063 — orig emits ~2× writes/frame (steady 34 vs mine 17). Dumped a steady
frame: orig = TWO full music updates back-to-back (PW sweep $D402/$D403
advances $2F/$0C → $B8/$0B between the halves), mine = ONE. A DOUBLE-SPEED
tune. ROOT CAUSE: play=$1003=base+3=`JMP $2000`, and $2000 = `JSR $1050 : JMP
$1050` = the engine runs TWICE per play(). `_detect_play_repeat` short-circuited
on `play == base+3` BEFORE following the JMP indirection into the wrapper. (Even
CANON base+3 is `JMP $1085`, but $1085 = the plain play body starting `DEC
$1718` — the existing loop follows the leading JMP once then returns 1; the
short-circuit merely skipped that walk.) FIX (1 line, factory
`_detect_play_repeat`): short-circuit only when `mem[base+3] != 0x4C` (not a
JMP); otherwise fall through to the EXISTING wrapper loop, which follows the
leading JMP once then detects the JSR-chain/JMP-tail (`JSR T; JMP T` → returns
2). REGRESSION-SAFE BY CONSTRUCTION: canon base+3=JMP→DEC body returns 1
(byte-identical build); only a genuine double-play wrapper returns ≥2, and such
a member built single-speed was ALWAYS a length partial (½ the writes), never a
FULL. CENSUS (all 5401 f1): exactly 10 members satisfy play==base+3 AND new
pr≥2 (the other 27 pr≥2 members have play≠base+3, already handled) — Lio
Happy_Night/Msxs/Scan_Collection_end, Logan Black_Music, PRI
Do_the_Note/Dreamland, The_Syndrom Double_Power/Other_One/Saturday_Night/
Savage_Remix — ALL 10 partial→FULL (fresh full-songlength verify). Full
tools/regression.py green (0 regressed all 7 families); artifacts mass-written;
10 truth rows appended (code_hash 0e528a58ec543575). METHOD LESSON: a perfect
play-stream PREFIX + a clean ~2× length tail on a VBLANK tune = whole-play
double-speed, NOT a missing effect (localize by counting writes/frame, then
disassemble the play VECTOR and FOLLOW its JMP — don't stop at base+3). f1 ≈
5140 FULL / 261 partial.

## ✅ ROUND 51 (2026-07-08): WJMP-CHASE SHADOW — High_Tech partial → FULL (+1, 0 regr) [ledger C11 new note] — commit 58685a07
Random f1 partial High_Tech (Dr_Piotr, vblank, flat div 32811, V3 freq-hi
orig $01 vs mine $00). Off-table melodic read idx 120 → freqhi[120]=$171F
(shared `wjmp` scratch, round-31 class). Diffed orig-vs-reb INPUTS
(base/accum/slide/parity) at the same V3-fhi memwatch event: only base_hi
diverged ($171F). pc-trace ground truth: $171F=$01 was written by **V1's wave
marker-HOP** ($91→$01), and V1 plays instrument 7 whose wave_start=137 sits ON
its own end-marker $91 (the "start at the loop marker" editor idiom). Orig
chases back 1 EVERY note-init (writes $171F=1); the composer packs the SETTLED
program (skips the transient chase), missing ONLY the note-init hop (every
settled frame after hops naturally, pinned at the marker) — divergence shows
only when a wjmp read lands on that frame before another voice overwrites
$171F (V2 idle). TRIED wave_table_pos (round-38 layout-preserving pool) — did
NOT fix it (the chase-skip phase persists); the correct fix is layout-
INDEPENDENT. FIX (CORE TENET, reproduce the WRITE): extract detects own-end-
marker chasers (loop 0, ctrl_tab[ws]==$90+n; gated on a wjmp read + canon
geom) → per-instrument USF `wave_start_on_marker`; composer re-asserts
`wjmp = n` at note-init (`iwchase` table + `ni_chase`), emitted only when some
instrument chases. This LIFTS the round-38 `_wave_layout_verbatim` "reject if
chasing + reads wjmp" carve-out, independently of the wavepos layout.
REGRESSION-SAFE BY CONSTRUCTION: re-asserts a write the orig ALWAYS makes at
that note-init, observable only where orig diverged — a FULL has no such read
(6 random FULLs + portfolio byte-identical; full tools/regression.py green, 0
regressed all 7 families). Census (partials): 4 f1 carriers — High_Tech FULL
297s exact; Chwat + Solar_Energy first-div resolved → deeper blocker (Lens 3);
King_of_Earth UNCHANGED (its wjmp read diverges for a non-chase reason =
cross-voice $171F churn, honest residue). METHOD: for a global cross-voice
scratch, memwatch the read value + diff orig-vs-reb INPUTS at the same event
index; a chasing instrument's wave-loop PHASE leaks into another voice's $171F
read even when its own output is a constant 1-step loop (unobservable in its
own stream). f1 ≈ 5130 FULL / 271 partial.

## ✅ ROUND 50 (2026-07-08): PWM bound-A SHIFT wedge — Aomeba/20_Years_of_NOP partial → FULL (+1, 0 regr) [ledger C19 6th occurrence]
Picked one f1 partial (20_Years_of_NOP, vblank, flat div 58, V2 PW lo orig
$D0 vs mine $E0). First-div chase: orig V2 PW ramps hi 7→8→9→10 (+$F0/frame,
never flips); rebuild flips to down at pwh=8 then freezes (step 0). Memwatch
ground-truth: orig V2 pulse bound A=$1D bound B=$12 ($1D EOR $0F), NOT the
inst nibbles 7/8 the extract captured. pc-trace found the cause: note-init
byte $124D patched $4A→$17 (LSR → the 2-byte illegal SLO $4A,X — ASLs the
UNUSED zp $4A scratch + ORs 0 into A = inert; zp $4A-$4C unreferenced by the
player), so bound-A extraction runs LSR×2 not ×4 → bound A = byte+2 >> 2
(not hi nibble). A classic C19 hand-patched wedge, STATIC in the file image.
CLEANEST C19 yet — EXTRACT-ONLY: the bounds ARE musical content (USF
min_hi/max_hi), so the probe only fixes their DERIVATION; NO USF field, NO
composer change. `factory._pw_bound_shift_probe` (anchor STA $1756,x / EOR
#$0F / STA $1759,x tail, reloc-aware; decode the 4-byte PLA→STA window,
count LSR-A; $17 = known 2-byte filler, unknown opcode bails to canon) →
extract-only `cfg.extra_params['pw_bound_shift']`, POPPED before the USF
params block (derivation knob must not leak to ML). `_decode_instrument`
gains `pw_bound_shift=4` (default = byte-identical `>>4`). CENSUS over all
5401 f1: exactly 1 carrier (`4a4a174a`), 5400 canonical (`4a4a4a4a`, shift=4)
→ regression-safe by construction. 20_Years_of_NOP FULL 294517/294517
(state_match ✓); full tools/regression.py green (0 regressed all 7 families).
METHOD REMINDER that cracked it: memwatch $1756/$1759 (bound A/B) for ground
truth, then pc-trace the actual executed note-init — the canonical
disassembly.s said LSR×4 but the RUNNING member decoded `17 4A` = SLO. When a
derived value's runtime ≠ what the canon disasm computes, trust the pc-trace,
not disassembly.s.

## ✅ ROUND 49 (2026-07-08): MULTI-SID PER-CHIP VERDICT — Nice_Dream_2SID false-partial fixed (3221 → 63496 match) [ledger C28 NEW] — commit b7849284
Continued the round-48 Nice_Dream_2SID chase. The round-48 "first
divergence = filter-def-walk res-timing at frame 103 (write 3221)" was a
**MISDIAGNOSIS**: it's a CROSS-CHIP ORDERING artifact, NOT a real bug.
Two SID chips are INDEPENDENT hardware → the order of a write to chip 1
($D417) vs chip 2 ($D420) within a frame is PHYSICALLY UNOBSERVABLE (each
chip evolves only from its own writes; cross-chip order is the multi-SID
analogue of within-frame cycle position, Trap B). Nice_Dream redirects
chip 2's res onto chip 1's $D417 (editor quirk); the cycle-sorted merge
(siddump's multi-chip write-log) places that res write's position vs
chip 2's body INCONSISTENTLY between orig and a rebuild with a few-cycle
delta — a false partial. PROOF: pc-trace per-CPU-invocation buckets
(program order, straddle-free) = 129/129 exact over the first ~2.8s;
per-chip flat compare = each chip's own stream matches. DIAGNOSTIC TRAP I
HIT: pc-trace/short captures (2.8-6s) showed "byte-perfect" — the REAL
blocker is 74s deep; always verify at FULL songlength before declaring
FULL. FIX (C28): compare each chip's stream INDEPENDENTLY (split merged
chip-tagged stream by reg//0x20). `compare_instruction_stream` gains
`n_chips` (per-chip run + conservative safety-field aggregation: worst
tail, AND of audio_guaranteed); `verify.verify_all` gains `_n_chips`
(PSID v3+ secondSIDAddress byte 0x7A / third 0x7B) + `_music_ok_multichip`;
`dmc_family_batch` passes `n_chips=len(cfgs2)` + localizes flat_div
per-chip. Single-chip (n_chips=1) path BYTE-IDENTICAL (branch skipped) →
full regression green (0 regressed all 7 families). Considered but
REVERTED a siddump.cpp per-irq straddle-free rewrite (global absolute-
cycle bucketing) — it did NOT fix this (per-irq still cross-chip-reorders
at the drift point) and touched the shared CIA verdict path; per-chip on
the EXISTING flat capture is the correct minimal fix (user-ratified).
REMAINING (Nice_Dream still PARTIAL): a GENUINE single-chip note-duration/
wave-timing drift at frame 3834 (~74s): reb inserts extra V3 note-inits
(ADSR=00/00 + wave restart) where orig plays one continuous downward-glide
note (empty V3 rest frame at f3834 in orig; gate-off+next-note one frame
early in reb). Wave-step VALUES match (CC,08,06,04,03,02,01,01,00) — only
the note BOUNDARY timing is off by ~1 frame. This is RE_NOTES bucket 9
(the freq-drift/note-duration tail, ~140 partials), a deep single-chip
chase, NOT multi-SID. Infra note: fix also correctly handles all 314 2SID
+ 27 3SID corpus members (per-chip generalizes to n_chips=3). NEXT for
Nice_Dream FULL: the note-duration-boundary chase (shared root w/ the
freq-drift tail); or move to the 272-partial residue.

## ✅ ROUND 48 (2026-07-08): 2SID/3SID SUPPORT — f1 unsupported 1 → 0 (Nice_Dream_2SID → partial) [ledger C27 NEW] — commits 7db09b2d / 368f2a46 / 6b222ca8
USER-REQUESTED feature: full 2SID/3SID support, canary = the last f1
unsupported (Surgeon Nice_Dream_2SID). KEY INSIGHT: a multi-SID tune = N
INDEPENDENT single-chip tunes played simultaneously; the dispatch wrapper
runs the players SEQUENTIALLY (JSR p1; JSR p2), so the merged write-log per
frame = [p1's chip-1 stream][p2's chip-2 stream] — each sub-player uses the
EXISTING single-chip machinery, only chip-TAGGED. THREE pieces:
(1) **write-log** (7db09b2d): siddump logs EVERY installed chip, merged
cycle-ordered with reg = chip*$20+reg; single-chip output byte-identical so
all flat (reg,val) comparators unchanged (verify_cycle state arrays widened
to 0x60, find_first_divergence decodes the chip tag). Multi-SID skip guard
removed.
(2) **USF schema** (368f2a46): voices number THROUGH the chips (1-3=chip1,
4-6=chip2); chip count derives from voice-block count; optional
`tempo N`/`global N`/`sid N` + `psid.sid2/sid3` MODEL (only when the header
states one). CHIP ADDRESSES ARE NOT IN USF — pipeline constants ($D420/$D440)
wired to the verdict (user: addresses are non-musical hardware tokens that
hurt ML; auto-translate orig→standard, chip-tag the verdict). Elidable:
single-chip files byte-identical round-trip. build_header stamps
secondSIDAddress + PSID v3.
(3) **DMC extract+compose** (6b222ca8): dmc_v4_config_2sid parses the play
wrapper's JSR chain into per-chip bases (one JT overwritten by the wrapper →
base from the play target), builds a DMCV4Config per chip; merge_2sid_usf
combines the per-chip models (fixed-stride disjoint instrument/filter id
blocks so the composer's _split_chip_usf inverts it EXACTLY = each chip's
standalone extraction); compose_dmc_asm gains origin + reg_delta;
build_dmc_2sid_sid emits one player blob per chip + a dispatcher. Per-instance
QUIRK reproduced as config: Nice_Dream leaves BOTH players' res/route $D417
write on chip 1 (editor didn't relocate that one operand → keep $D417
un-relocated; chip 2 never gets $D437).
RESULT: Nice_Dream_2SID unsupported → **partial**, chip-tagged write-log
matches **3221 writes across BOTH chips** (res-quirk exact); first divergence
= player-1's own chip-1 res write at frame 103 = an ordinary DMC
filter-def-walk res-timing detail (single-chip-class, NOT multi-SID). **f1 =
5129 FULL / 272 partial / 0 unsupported / 0 error — EVERY family-1 member is
now at least partial.** Full regression green (0 single-chip regressions).
Infra is engine-neutral (corpus: 314 2SID + 27 3SID; also unblocks the
round-45 2SID partials). NEXT: chase the Nice_Dream filter-res-timing to FULL
(shared with single-chip filter partials), or the 272-partial residue.

## ✅ ROUND 47 (2026-07-07): INIT-UNPACKER CLASS SOLVED — unsupported 5 → 1 (+4 FULL) [ledger C26 NEW] — commit 0d60bd14
The Flash trio (Haste/Kan-Kan/Wind_of_Dead, `nonstandard_instr_base`) +
Itinerant (`nonstandard_vectors`) all FULL in one session. The trio: 2entry
players whose init GENERATES all six data tables in high RAM (instr
$B961/$A70B/$ACEA, tunetab $7DC9, ... — ALL operands outside the loaded
image). FIX (C26): factory accepts the operand-named instr base iff EVERY
data operand is out-of-image (all-or-nothing signature; mixed layouts stay
refused), skips the packing-order check for that class, checks _INST_SAT
against the operand-named base, sets `DMCV4Config.data_post_init`; extract
then swaps its WHOLE memory for `_postinit_window(s, 0, 0x10000)` — read
what the engine reads. Itinerant composes the class with a banking wrapper:
play = `LDA #$35/STA $01/JSR $1050/LDA #$37/STA $01/RTS`, JT overwritten by
the wrapper/init code → new base candidate base = t−$50 (2entry) / t−$85
(canonical) from the wrapper's JSR target, validated by the masked identity
compare. Both paths only run where the extractor previously refused
(regression-impossible); full tools/regression.py green; artifacts
mass-written; truth rows refreshed via --members mini-batch. f1 = **5129
FULL / 271 partial / 1 unsupported (95.0%)**. THE LAST UNSUPPORTED:
Surgeon Nice_Dream_2SID = TWO complete 2entry player instances ($1000
JT-less via wrapper JSRs $1807/$1050 + $3000 with JT, second driving the
2nd SID chip) — needs second-chip support (USF/composer/verify), shared
blocker with the round-45 2SID partials. NEXT: the 271-partial residue
(first-divergence chases: $D418 mvol-transform class, 2SID partials,
freq-drift/otrk_legacy tail) or the 2SID design.

## ✅ ROUND 46 (2026-07-07): no_jumptable BUCKET EMPTIED — 62 → 0 (+31 FULL, +31 partial) [ledger C13 note] — commit 2ac58cbb
The bucket was NOT "no jump table" for 54/62 — it was near-canon players with
a RESTRUCTURED INIT header whose rewritten code broke the dataflow path's
opcode-WINDOW signatures around one read site (tunetab 25 Doxx, wavectrl 18
Wodnik/Heinmueck, d417 9+1); 8 were CIA-wrapper/mixed-table members (player at
$1000 behind `JMP $1000`, or `4C init/20 85 10/4C 85 10` mixed JSR/JMP table);
1 (Silent_Memories) had a ripper-rotted JT play entry (JMP $3AF5 = zeroed RAM)
with the real play in the PSID header. FIXES (all extract-side, in
`dataflow.py` + `_build_via_dataflow`, ONLY on previously-refusing paths):
(a) `_sigs_op` = all canon reference sites for a data operand, not first-only;
(b) inner-shape fallbacks with value-dedup (tunetab paired lo/hi read
excluding filtdef's chained +1 reads; wavectrl BC/B9/C9-#$90; d417
LDA/ORA/STA-$D417); (c) tiered base candidates: wrapper-JMP targets with
strict 4C..4C table first, then loose 4C-only at play-3/load, each judged by
locate-success — NO full-image loose scan (interior 4C..4C pairs, e.g. table
entries 3+4, locate from the wrong base); (d) locate(play=header_play) retry.
State-addr loop kept first-occurrence-only (widening could flip verified
members' state addrs). RESULT: 31 FULL (mass-written) + 31 partial, full
regression green. f1 = **5101 FULL / 252 partial / 48 unsupported / 0 error
(94.4%)**. TRAPS re-hit: mid-batch shared-code edits staled the running batch
TWICE (kill+relaunch under final code), and a `pkill -f`/`pgrep -f` waiter
self-matched its own argv AGAIN — wait on a log marker (grep the FILE), kill
by explicit PID.
CASCADE SWEEP (same day, commit d4fbf3ed): re-verifying the other 48
unsupported under the new locators emptied pcm/instr_base/loop_site too —
**+24 FULL +24 more partial** (mass-written, truth merged). Then
rest_effects='vibflip' (rest dispatch → canon $1567 vibrato half-cycle
mid-routine entry; composer `vib_half` label = zero bytes, sole corpus
carrier Acid_Dance) + a secp inner-shape anchor (B1/A8/B9/85/B9/85 pair,
handles non-canon lo/hi spacing $1E8F/$1E9A, Cotton_Eye_Joe) converted the
last two tractable members (commit 53b67d59). f1 = **5125 FULL / 271 partial
/ 5 unsupported / 0 error (94.9%)**. THE LAST 5 (each a real design task,
not an unblocking tweak): Flash ×3 nonstandard_instr_base = INIT-UNPACKER
class (instrument data GENERATED by init at $B961/$A70B/$ACEA — file image
is zeros there; needs post-init-RAM extraction, cousin of the round-40
init-generated triangle table); Flash Itinerant nonstandard_vectors =
banking-wrapper JT-less (play = `LDA #$35/STA $01/JSR $1050/LDA #$37/STA
$01/RTS`, ROM banked out around the call); Surgeon Nice_Dream_2SID = needs
second-chip support (same blocker as the round-45 2SID partials).

## ✅ ROUND 45 (2026-07-07): ERROR CLUSTER CLEARED — f1 errors 25 → 0 (+1 FULL, +24 partial) [ledger C11 note]
User-staged goal "unsupported/error → partial first; errors first". Census: 20×
"track never settles" (Bayliss ×11, Pinov_Vox ×2, Rayden-2SID ×5, +2) + 4×
IndexError + 1× 2SID assert. ONE root cause behind the first two clusters:
header-overstated subtunes (Bayliss PSID says 6 songs; the tune table has 1
real record — subtunes 1-5 point at zero fill/text bytes) walk terminator-less
tracks/sectors, and the engine's track pos ($1726) + sector pos ($1729) are
BOTH one byte → hardware wraps mod 256 and plays a 256-byte cycle forever.
The extractor walked full-width → RuntimeError at 8192 (or IndexError past
the 64K image). FIX (C11 canonical): mirror the 8-bit wrap in `_walk_track`
(+ mod-256 cycle detection engaging only after an actual wrap) and
`_simulate_sector` (unterminated sector → `('endless', lead, period)`; the
voice self-loops on the period entry). Regression-IMPOSSIBLE: both paths
previously hard-errored. +2 small unblockers: `_play_unit_repeat_probe` scan
bounds guard (Mission_Moon: play body near $FFFF), and the instr_base sanity
floor widened to the LOADED image (Mothafucka_2SID: data prefix below the
player, instruments at $0A00 — genuine records; operand-trust + verify-gated).
RESULT: 25 errors → 1 FULL (Axel_F_Remix, artifacts written) + 24 partial,
0 errors left. f1 = **5038 FULL / 172 partial / 191 unsupported / 0 error**.
The 24 new partials' first divergences are fresh residue (e.g. garbage-subtune
$D418 mvol transform: orig writes 15 where the record byte is 126 — engine
transforms it somewhere; 2SID members need second-chip support to go further).
NEXT: unsupported buckets (sector_decode 81 → no_jumptable 62 →
player_code_mismatch 23 → nonstandard_instr_base 12 → loop_site_unknown 11),
one representative per bucket first.
ADDENDUM (same day): the sector_decode bucket (81) was the SAME guard the
wrap fix rewrote — re-verified all 81: **+32 FULL + 49 partial, bucket
emptied** (artifacts mass-written). f1 = **5070 FULL / 221 partial /
110 unsupported / 0 error** (93.9%). Remaining unsupported: no_jumptable 62,
player_code_mismatch 23, nonstandard_instr_base 12, loop_site_unknown 11,
nonstandard_vectors 1, rest_dispatch_unknown 1.

## ✅ COMPLETE SWEEP (2026-07-07): all families re-verified under commit a3fbf06d — the authoritative counts
User-requested full sweep (f1+f2+v5, 9,785 members, 6h20m sequential on the
8-core host; the first attempt was killed mid-f2 when the round-44 composer
fix landed — code_hash staleness — and restarted under the final code).
**ZERO losses in all three families.** Counts (code_hash 0c127d5cbba2619b era):
- **family-1: 5037 FULL / 148 partial / 191 unsupported / 25 error of 5401
  (93.3%)** — +6 vs the pre-C25 run: Revolution-Evolution + Ucieczka (C25)
  + I_Wont_Write_Happy_Song/Zak_2/Bilinski/Extazcia (borderline rate/tolerance
  members the faster body pulled inside the CIA close tolerance).
- **family-2: 2507 FULL / 325 partial / 45 unsupported / 12 error of 2889
  (86.8%)** — +94 vs the 2413 recorded at the last f2 sweep (the accumulated
  shared-composer rounds since; 0 losses).
- **v5 fam-3/5: 1098 FULL / 202 partial / 154 unsupported / 41 error of 1495
  (73.4%)** — +10 vs 1088.
DMC total FULL = **8642**. All three families' FULL artifacts mass-written
fresh (current-hash gate). Truth files: tmp/dmc_wide_results.jsonl /
dmc_f2_full.jsonl / dmc_v5_results.jsonl. Residue heads: f1 148 partial
(freq-drift in_table + otrk_legacy + orig-overruns-latch C25 mirror class),
f2 325 partial, v5 202 partial + 113 player_code_mismatch unsupported.

## ✅ ROUND 44 (2026-07-07): CIA cycle-budget overrun — off-table redirect chain fast path (+2 FULL restored, 0 regr) [ledger C25 NEW]
The round-43 closeout sweep (fresh f1 batch, 5031 FULL / 154 partial) surfaced
5 FULL→partial "losses". C20 triage: 3 were palimpsests (old rows said
status=full while their OWN subs said is_full=False, code_hash None, no
artifacts — Compotune_1/2, Falu_Mix); 2 were REAL (Revolution-Evolution,
Ucieczka_z_Tropiku: stored artifacts still verify, fresh builds fail).
Signature: PERFECT play-stream prefix + state match, ONLY a ~0.5% length tail =
RATE drift, no content divergence (trichotomy: an ENVIRONMENT failure).
/amend run: initial suspect (round-41 cia_period) EXONERATED (param unchanged);
measured avg play-entry period (--per-irq-debug) orig 2456.9 == stored 2457.3,
fresh 2464.1 → the play body chronically OVERRUNS the 8x latch (2456), delaying
IRQs. Lens-1 root cause: `_gen_offtable_redirect`'s compare chain sits on the
per-voice per-frame wave-step path at ~4-5 cyc/row for in-table reads, and
rounds 31→39 grew the map to 48 rows (wjmp/sectpos/wavepos/fxf/fsz) — each
round taxed EVERY member; tight-latch members finally tipped over. FIX (C25):
one leading `cpy #min_off / bcs chain` fast-paths the common in-table read
straight to the static load — content-identical BY CONSTRUCTION (fast path
serves exactly the Ys that fell through every row), pure cycle timing. Both
members FULL (768571 + 1576978 overlap); full tools/regression.py green.
MIRRORED residue class: orig ITSELF overrunning its latch (Compotune_1 latch
4913, orig ≈5393) needs an exactly-as-slow rebuild — never-FULL, honest
residue. TRAPS: (a) editing shared composer code MID-SWEEP stales the whole
running batch (code_hash) — the f2 leg was killed + the complete sweep
restarted under the final code; (b) pkill -f 'dmc_family_batch' matched my own
verify batch's argv (the self-matching tripwire — kill orphans by explicit
PID); (c) a same-name glob (Harti vs Praiser Ucieczka_z_Tropiku) diffed the
wrong stored USF — use exact paths. GUARD (ledger C25): any addition to a
per-voice per-frame path costs ×3 voices × the tightest corpus latch.

## ✅ ROUND 43 (2026-07-06): noteinit_deferred window escalation 12→96 (+1 FULL Wavefrontline, 0 regr) [ledger C23 refinement 2]
Random partial Aomeba/Wavefrontline (CIA 2x, P_F123): per-IRQ first div pos 21,
V1 ctrl orig $00 vs mine $40 — the note-start chirp's gate-mask 0→$FE
transition lands one call LATER in orig = the C23 2-frame arm, visible from the
FIRST soft note (no HR needed for the stream to diverge). `_detect_notestart_
arm`'s fixed 12-frame window ends before the song's first HR (play ~41) →
conservative "immediate" → wrong. FIX: escalate the pctrace window 12→96
frames ONLY when the short pass is inconclusive (a voice with no HR, or no emit
within hr+6); all-voices-definitive-immediate stops escalation → members the
short window decides are byte-identical. GATES: 0 verdict drift over all 76
stored F-token carriers (NB census regex trap: stored USF writes
`noteinit_deferred: "1"` QUOTED — an unquoted-regex census reported 14 phantom
flips, all of them the known carriers); partials sweep = exactly 1 new arm
carrier (Wavefrontline; the other 8 arm partials already detected at 12 frames,
builds unchanged, deeper blockers); full tools/regression.py green (DMC
14ok+0regr). Batch verdict FULL 288100/288100; artifacts written; truth merged
(5477 full / 165 partial). TRAP re-confirmed: dmc_mass_write.py has NO --help —
invoking it with --help RUNS the tool (harmless here: 0 current-hash rows).

## ✅ ROUND 42 (2026-07-06): dual_hack → dual_freq_generator — the /uready-review C7 flag RESOLVED (0 count change) [ledger C7 note rewritten]
A DMC-focused /uready-review (user-prompted "did the fast progress cut
principle corners?") found NO §7/§8 leaks; its one LEAK-adjacent flag
(dual_hack, Taurus_02 sole carrier) was then OVERTURNED by a full re-anchor
(principles + core tenet + trichotomy + ledger + amend, user-directed): the
filter_mod comparison was a CATEGORY ERROR — filter_mod is C10 (recoverable
structure → typed contour), the dual wedge is C19 (probe → param IS the
canonical form). Decision (user-ratified) = C7-(b) document-and-minimize:
rename `dual_hack`/`dual_hack_steps` → `dual_freq_generator`/`dual_generator_steps`
(behavior naming was the one real defect; probe → `_dual_freq_gen_probe`),
steps-derivability checked = unavailable (raws land in wavectrl, layout not
in USF), the "lift to `law: random` musical enum" recorded as a §8 trap in
ledger C7 (the enum wouldn't determine the write stream). Taurus_02
re-extracted/rebuilt/verified FULL 86118/86118; artifacts rewritten; v4
RE_NOTES got the residue section. KEY LESSON: run the /uready-review's own
findings through the same adversarial re-anchor before acting on them —
"same week, different treatment" can be two ledger classes each getting its
correct canonical form. Audit also found: C3 gap CLOSED (offtable capture
minimal), C4 stale (portfolio at 4770, f2 frozen at 2413 since Jul 4 —
recovery sweep due), C6 rotted (RE_NOTES Jun 14).

## ✅ ROUND 41 (2026-07-06): single-speed CIA DEFAULT latch $4025 (+3 FULL, 0 regr) — commit a92f9a7c [ledger C9 note]
Random partial Phobos/Crazy_Mix: flat find_first_divergence said pos 0 — the
CIA init-phase artifact (PSID speed=1; ALWAYS re-localize per-IRQ before
believing a flat pos-0 on a CIA member). Per-IRQ: the rebuild's stream was a
PERFECT PREFIX (all 94811 of its own writes matched) but orig emitted 113495
in the same window — orig 6713 IRQs vs reb 6105. Orig's exact play-entry
period = 16422 cycles = latch $4025 = the PSID environment's DEFAULT CIA
latch (~60 Hz): a speed-bit tune whose init programs NO timer still runs on
the CIA, at the default rate. Both factory probes returned 0 ("no readable
latch → single-speed fallback" blanket) → the composer built it VBLANK 50 Hz
= guaranteed ~20% length partial. FIX (C9, no schema change — the existing
cia_period param): `_cia_period_from_writelog` on N<2 measures the exact
entry0-delta period (median; a 2-entry frame doubles one delta, median
discards) and returns $4025 iff it matches ±2 (a 50 Hz-ish rate stays 0 —
vblank build equivalent); canon path now calls the writelog fallback for
CANONICAL-play members too (was wrapper-only). Exposure: census all 169
partials → exactly 3 carriers (Crazy_Mix 113495/113495, Love_Song
133516/133516, Magnum_Theme 145730 full overlap) — all FULL by the official
batch verdict; the 3 flagged multispeed members (Axel_F/Strange_Acidshit/
Keep_Rave) proved BYTE-IDENTICAL old-vs-new (dataflow path already measured
them; their truth rows were stale, C20 — re-baselined via git-stash builds
before believing anything). No FULL can carry the changed path by
construction (a rate-wrong build always length-fails). Full
tools/regression.py green (DMC 14ok+0regr; portfolio members probed = all on
unaffected paths). Artifacts mass-written; truth merged (partial 169→166).
f1 ≈ 5019 FULL / ~166 partial.

## ✅ ROUND 40 (2026-07-06): filter_mod — global cutoff LFO streamed into the filter DEF bytes (Core_of_Acid FULL, +1) [ledger C10 new note]
Random partial Ed/Core_of_Acid (vblank, flat div 9506, $D416 orig $8D vs mine
$5D): rebuild reproduced the cutoff sweep DELTAS exactly but orig's per-note
START climbed +1/elapsed-frame. NOT a code wedge (filter init/run regions
byte-identical to canon) and NOT static data — taint_source on the RIGHT def
($19BF/$19C1 = def3 init/stop; the first scan covered defs 0-1 only, mind the
range) showed both DYNAMIC. Mechanism: play vector = wrapper `JSR reader /
double 16-bit SMC INC automaton / JMP play`; reader = `LDA ptr1/STA def+1 /
LDA ptr2/STA def+3` with both pointers roving an init-GENERATED 513-byte
triangle table ($1CFF-$1EFF, past file end), +16-byte phase offset between
taps → a free-running cutoff LFO the engine samples at every filter
note-init. FIX (C10 parametric form, C1 contour shape): USF `filter_mod {
prog N: start= init_phase= stop_phase= step (d,f)... }` (grammar/parser/
types/writer; reuses fp_step); factory `_filter_mod_probe` (C19 static probe
of wrapper+automaton, validates SMC targets == reader operands + stores ==
filtdef+16n+1/+3; contour = post-init RAM delta-RLE'd, ≤16 runs); composer =
two sweep walkers (val/idx/cnt, shared rate/len tables, python-computed
phase seeds) storing into `fdinit+slot`/`fdstop+slot` at the top of the
play-wrapper chain. Core_of_Acid probe: '4|0|92|108|2:1,1:253,0:1,-1:253,
0:4,-2:1'. FULL 66338/66338; whole-corpus census: SOLE carrier; default
byte-identical (Hardcore+Broken MD5 old-vs-new); artifacts written; truth
merged (partial 170→169). LESSON: when a member's sweep SHAPE matches but
the reload BASE drifts ~+1/frame, suspect the filter DEF BYTES are being
rewritten by a play wrapper — taint the EXACT def record, not just the
table head.

## ✅ ROUND 39 (2026-07-06): fxf + fsz/fdu redirect rows — materialize the cache var (+7 FULL, 0 regr) [ledger C11 new note]
Random partial Signor/Saturday_Dance (vblank, flat div 13232, V3 fhi orig $20
vs mine $00). ONE first-divergence chase peeled TWO off-table classes: (1) fhi
idx 216 → $177F = FX-FLAGS CACHE ($177D,x, instr byte 10) — the composer
already had the var (`fxf,x`, stored at note-init exactly at the orig's $12EB
site); verified `iflags()` round-trips the raw byte 10 for every instrument
(all 8 bits ↔ typed fields) BEFORE mapping, then plain row `(0x177D,'fxf',3)`.
(2) flo idx 218 → $1721 = filter STEP-SIZE cache — the round-22 "$1721/$1722
read inline via fdstep/fddur, no cache VAR" rejection OVERTURNED: the composer
read them into scratch `tmp`/`tmp2` at exactly the orig's STA sites, so the fix
is renaming the scratch to dedicated `fsz`/`fdu` vars + rows (0x1721/0x1722).
All three inside the orig $1718-$179D init wipe + composer state wipe → no
seed. Saturday_Dance FULL 110279/110279. Exposure sweep (83 stored idx-
carriers {214-216,218,219,122,123}): 62 FULLs HOLD (incl. 12 CIA), **+7 FULL**
(Saturday_Dance, Crystal_Sheep_III_Intro, Nuclear_Family, Rio/NEO,
Non_plus_Ultra_tune_2, My_Shelter, Hank/Scream), 14 partials have deeper
blockers, 0 regressions. Full tools/regression.py green (DMC 14ok+0regr).
LESSON (ledger C11 note): "no composer var to redirect to" is usually a
one-edit materialization, not a rejection — and a RECONSTRUCTED value (iflags)
must be round-trip-verified per instrument before its var is mapped.
f1 ≈ 5015 FULL / ~170 partial (closeout batch still pending for the exact
count).

## ✅ ROUND 38 (2026-07-06): WAVEPOS boundary falls — layout-preserving wave pool (+5 FULL, 0 regr) [ledger C11 new note]
Random partial Zyron/Distant_Echoes (vblank, flat div 107112, V3 fhi orig $21
vs mine $01). Off-table fhi read idx 211 → $177A = V1 LIVE WAVE POSITION —
the round-22 "wavepos positional-hard" bucket; measured 32 distinct read-moment
values per key (static + event-driven both correctly fail). THE REFRAME (the
§8 sectpos playbook applied to the wave table): the DMC wave table is an
EDITOR-SHARED table the composer typed positions into (instrument byte 9 =
arrangement, like transpose placement). FIX: (1) USF `Instrument.
wave_table_pos` (grammar/parser/writer/types; emitted ONLY for carriers — all
instruments or none); (2) extract `_wave_layout_verbatim` gate: canon geometry
(C6 note) + idle walk and EVERY instrument's program a verbatim contiguous
slice ending on the orig marker $90+(n−loop); admits wave_start ON the own-end
marker ("start at the loop marker" idiom — the chased first-step position is
carried), EXCEPT when the member also reads the wjmp window (the skipped
transient chase writes $171F); (3) composer `place_prog` packs the pool AT
those positions (instead of append+dedup) so `wavepos,x == orig $177A,x` at
every settled moment (marker hops carry identical distances for verbatim
slices), and the gated `DMC_WAVEPOS_ROW` (0x177A,'wavepos',3) redirect serves
the read live. Default byte-identical (MD5 old-vs-new, Aktarus). 30-member
stored-USF exposure sweep: 12 FULLs HOLD, **+5 FULL** (Distant_Echoes
313604/313604, No_Name_Remix, In_die_Dunkelheit, Das_Remix, II-V3), 2 partials
moved LATER (PVCF Fast_Shit 159299→162542, Vincenzo 64854→65156), 4
no_jumptable = pre-existing v5-family refusals, 0 regressions. Object_of_Art
(the 2026-06-28 blocker) has a DIFFERENT first blocker (flat 15) — unchanged,
honest residue. Ledger C11 "HARD BOUNDARY" rewritten as RESOLVED. NOTE: more
round-22 wavepos-class members should re-flip at the next batch sweep where
their first div was the $177A read and their layout is verbatim.

## ✅ ROUND 37 (2026-07-06): NON-CANON STATE GEOMETRY — the whole live-serving stack falls back to static (+4 FULL, 0 regr) [ledger C6 new note]
Random partial Aomeba/Viiskyt_vuotta_humppaa (vblank, flat div 61788, V1 fhi
orig $BD vs mine $06). The member is a VARIANT BUILD: freq tables shifted −$13
(fhi $1694) and ALL per-voice state moved to PAGE 3 ($03xx: fbl $0359, wavepos
$03A4, fxf $03A7...; curnote $1011). So every canon-geometry identification of
"window idx N = live state var" is wrong for it: idx 130 "sectpos" = an opcode
byte $BD, idx 208 "cvram" = an INY $C8, window pos 16 "live mvol" = a static
$07 — all STATIC bytes the post-init capture already records exactly, each
SHADOWED by a live redirect/co-location. THREE heads of one disease, peeled in
one first-divergence chase: (1) sectpos_shadow gate fired on idx∈{130-132}
alone; (2) DMC_OFFTABLE_STATE redirect rows served live cvram for idx 208;
(3) the ovrwin co-located spd/mvol block served live mvol $0F for the lo read
at window pos 16. FIX (one probe, all consumers): `_canon_state_geometry` —
static C19 opcode probe, the canon player's `DEC dur,x` must exist at
fhi + ($173B−$16A7), fail-open — gates sectpos_shadow, the event-driven
capture (its memwatch addrs are canon — on a non-canon member it fabricates
constant bogus keys, so it's SKIPPED not unrestricted), and a new
`offtable_redirect=0` param (composer empties the redirect map, places records
verbatim at pos 6..16, emits sidoff/fbit/fmask/spd/mvol OUTSIDE the window).
[PARAMS REMOVED 2026-07-09, Phase A composer→extract relocation: both
`offtable_redirect` and `sectpos_shadow` deleted from the USF (they described
HVSC memory geometry) → per-read `live(off,note,lo,hi)` vs `at(...)` flag on
`offtable_freq`; composer re-derives redirect = `not (static read at a
live-served idx)`. Byte-identical all 5401. See ledger C7 + `deprecated/old_docs/dmc_composer_to_extract_plan.md`.]
Default byte-identical (Hardcore/Intro_Music_2 MD5 old-vs-new; 98_Mix = itself
a carrier, byte-shifted but verified FULL). Real-probe census over all 1212
stored-offtable f1 members: exactly 10 carriers (Bakewell×4/Finn×3/98_Mix/
Viiskyt/Noising_Funk). RESULT: +4 FULL (Viiskyt 303644/303644, Finn Hyper/
Industure/Blastlaugh), 4 Bakewell FULLs hold, Noising_Funk = unrelated
pre-existing blocker (flat_div 14 identical). Full tools/regression.py green.
TRAP: an approx census keyed on the PSID LOAD address claimed 225 carriers —
members load data prefixes below $1000, so cfg.base ≠ load; always census with
the real probe (dataflow cfg). f1 ≈ 5005 FULL / 180 partial. LESSON: when
adding ANY new live-serving of an off-table window position, gate it on the
geometry probe (ledger C6 note).

## ✅ ROUND 36 (2026-07-06): hard-restart AD/SR IMMEDIATE patch (Stryyker, +3 FULL) [ledger C19 5th occurrence]
Random partial Stryyker/Proportional_Text_Writer (vblank, flat div 88, V1 AD
orig $0A vs mine $0F at a note-fetch frame). The member patches ONE byte:
sub_17FB's `LDA #$0F` operand ($17FF) → $0A, so the hard-restart prime writes
AD=SR=$0A. Simplest C19 form yet. FIX: `factory._hr_preset_probe` (static
opcode-shape regex `[99|B9] 04 D4 A9 vv 99 05 D4 99 06 D4 60`, layout-blind;
first opcode admits $B9 for the hardrestart_smc_variant SMC variant) → value fed through the
EXISTING `hard_restart` param (domain extended 'preset'/'none'/numeric — NO
new schema field); composer renders `lda #$vv`; guarded so family-2's preset
'none' is never overridden. Default renders identical asm text →
byte-identical for non-carriers. Whole-corpus census (10,676): exactly 4
carriers, all Stryyker/$0A, ZERO FULL exposure. +3 FULL (Proportional_Text_
Writer 77076/77076, Chaotic, Sans_Theme); Sans_intro = unrelated pre-existing
first blocker (flat_div [0,0,6,252,96] byte-identical before/after — nothing
moved earlier, no /amend). Full tools/regression.py green (DMC 14ok+0regr);
truth merged; 3 artifacts mass-written. f1 ≈ 5000 FULL / 185 partial
(round-35 closeout batch still pending for the authoritative count).

## ✅ ROUND 35 (2026-07-06): dual-effect FREQ-GENERATOR wedge (Taurus_02 FULL) [ledger C19 4th occurrence]
Random partial Taurus/Taurus_02 (vblank, flat div 30954, whole V3 block: freq
$16F1 vs $1A9C, ctrl $8D vs $11 on ALTERNATING frames). The member byte-edits
the dual ($40) odd-parity path: `LDA $172F,x` opcode BD→A6 = `LDX $2F`, and
zp $2F=$A9 under the PSID env, so every per-voice read lands +$A9 past the
state arrays onto FIXED CODE BYTES (speed=$4C JMP opcode, base hi=$80 CMP
operand, PW $04D4 + ctrl $9D&$CD=$8D from sub_17EC/17FB bytes); the "accum"
self-modifies two tune-setup code bytes (file bytes $0F/$69 = seed, outside
the init wipe), the update ORs BASIC ROM $BD68,y ($E9) and rotates zp $12 via
ILLEGAL RRA. Net = ONE global free-running pseudo-random noise-freq ramp on
dual frames + pwphase[V3] clobbered to $42/$43 (live carry from the pulse
CMP), which sends the pulse speed fetch OFF the instrument record (static
bytes past the table, e.g. wavectrl[14]=$FF → step $F0). METHOD: pc-trace one
dual frame for ground truth (hand-decoding the garbled overlap MISLED twice);
then Python-simulate the generator vs ALL observed dual events — 3826/3826
exact BEFORE composing. FIX: `factory._dual_hack_probe` (wedge regex; all
constants captured from the image; 'step,ph,bhi,pwl,pwh,ctrl,seedlo,seedhi,
slot') → composer replaces fx_dual_run with clean code (legal ror+adc = RRA,
live-carry `adc #$18/adc #ph` pwphase store, constant PW/ctrl tail) +
`dual_hack_steps` (extract) EXTENDS stride-8 isteps/irawsp at the garbage-
phase indices (cinst*8+P0..P0+3) — ZERO pulse-code change. Default byte-
identical (3-member MD5 old-vs-new incl. Hardcore); whole-corpus census
(10,676): Taurus_02 = the ONLY carrier. verify FULL 86118/86118. LESSON:
when a hack executes garbled/illegal opcodes, STOP hand-simulating — pc-trace
+ simulate the observed stream; the write-log defines the semantics.
ADDENDUM (user ear-test on Taurus_02): the rebuild verified FULL yet SOUNDED
different — the composer hardcoded PSID flags PAL/6581 while the orig header
says 8580 (63% of the DMC corpus = 6,729 members is 8580-flagged; ~3.8k
shipped artifacts had wrong headers). The write-log verdict is BLIND to
header flags ([[feedback_header_flags_audible]]). FIX: extract captures
header clock/sid losslessly (grammar now admits `sid: both`/0), v4+v5+GT-v1
composers derive flags from usf.psid (the FC canonical form); FC's collapse
of both/unknown→6581 also made lossless. ALL stored DMC artifacts + USFs
need a re-extract+rebuild mass-write (code_hash auto-invalidates the batch
rows — fold into the pending round-35 closeout batch).

## ✅ ROUND 34 (2026-07-06): soft-note fetch honors rest_effects='skip' (+14 FULL, 0 regr; f1 partials 219) — commit 010af48 [ledger C19 corollary]
Random partial Daf/Chojnow_Music_Compo_1 (CIA 4x, flat div 266023, V2 PW lo
$F0 vs $E0 — one pulse step ahead). Orig HOLDS all pulse accums one frame on
row-FETCH ticks: the member carries the rest-skip wedge ($117D: JMP $1322 →
JMP $1591), and that ONE patched JMP is the funnel for rest, switch, slide
AND the $7C soft-note fetch. The composer honored `rest_effects='skip'` in
ev_rest/ev_switch/ev_slide but ev_n_softq hard-coded `jmp run_effects` — so
soft-note fetch frames stepped the pulse where the orig held it. FIX: one
line, `jmp {rest_jmp}` (canon 'run' renders byte-identically). LEDGER
COROLLARY (C19): a probed knob must be honored on EVERY orig path funneling
through the patched site — grep the composer for ALL jumps to the canon
target label when landing a knob. METHOD: memwatch-on-write showed holds at
fetch ticks ($173C reload + sectpos advance, speed-ctr reload); C19 tell =
disasm says effects run but stream holds → dump the member's bytes at the
canon site (rest-tail regex census: Zaks $322 vs Chojnow $591). GATE: full
regression green; exposure batch 465 (all stored-USF skip+noretrig carriers)
= 464 FULL + Super_Seven pre-existing-identical partial. +14 unique
partial→FULL (Orcan×3/Cubehead×3/Rio×2/Chock×2/Chojnow/Uj_X_Dik/Hardshit/
My_46th_Tune); artifacts mass-written; truth merged (f1 partial 233→219).
NB siddump positional `-t86` is silently ignored — use `--duration`; and a
siddump second ≈ 0.915 real seconds (Trap C cousin) when sizing captures.
SWEEP ADDENDUM: the f1 partials-only sweep (219) flipped **+31 more FULL**
(Olsen×10/Bakewell×6/Cubehead×5/Brian×2/... — the no-artifact soft-fetch
partials + stale-partials from prior rounds), all mass-written. Round-34
total +45; merged truth f1 = **4997 FULL / 188 partial** (closeout batch for
the authoritative count still pending). NEXT: freq-drift in_table +
wavepos/otrk_legacy tail remain.

## ✅ ROUND 33 (2026-07-06): SECTPOS LIVE SHADOW — the round-22 "positional" blanket falls (+120 FULL, 0 regr; f1 partials 233) [ledger C11 new note]
Random partial Rodney/Intro_Music_2 (vblank, flat div 301, V2/V3 fhi $06 vs
$09): off-table fhi read idx 130 → $1729 = V1 SECTOR POSITION — the round-22
REJECTED bucket (census name 'notectr'), read-moment value GENUINELY VARIES
(6/7/8) so static + round-27 event-driven capture both fail. THE REFRAME
(overturning the C7 objection): the visible sectpos during a row is a PER-ROW
CONSTANT = cumulative byte width through that row's fetch (0 on the pattern's
last row — the $7F check runs IN the fetch, $11E6/$11F2), and width DERIVES
from row kind (note/rest/switch 1, slide 2, glide 3) + the STATED dur/instr/
vol/soft commands. Statedness is a sector-byte FACT (instance-independent →
pattern-fact, survives dedup); value-change derivation reconstructs it except
REDUNDANT re-statements = the editor's command placement = §8 arrangement
(exact otrk_rcmd precedent). NO byte offsets in USF. FIX: extract records
per-row `dur_cmd/instr_cmd/vol_cmd/soft_cmd` fx_flags (new USF grammar tokens; emitted
only for carriers) + sets `sectpos_shadow` when any offtable_freq idx ∈
{130-132, 226-228}; composer embeds 1 derived byte/event after the opcode
(all handler offsets +1, gated), stores it to `sectpos,x` at every fetch,
redirect row DMC_SECTPOS_ROW (0x1729,3). Default byte-identical (9 portfolio
members MD5 old-vs-new; non-gated members re-merge in the composer's
encoded-bytes dedup even where the extract key splits). SWEEP (74 exposure +
all 314 f1 partials): **+120 FULL, 0 regressions, 0 errors** — the whole
notectr census bucket + Surgeon/Zyron/Bax/Cleve/Rayden clusters. Full
tools/regression.py green (DMC 14ok+0regr). f1 partial 314→**233**; artifacts
mass-written. TRAPS THIS SESSION: (a) "DIFFERS vs stored artifact" ≠
regression — stored artifacts are stale since round-31's layout shift; always
baseline old-CODE vs new-CODE builds (git stash), C20 again; (b) a background
`dmc_family_batch.py --help` LAUNCHED A FULL BATCH (argparse ignores unknown
args!) mid-edit — killed it; its rows carried a mid-edit code_hash so the
hash gate auto-invalidated them. NEXT: full-family closeout batch for the
authoritative count (round-32's 4871 + these 120 needs a fresh sweep to
settle); freq-drift in_table tail + wavepos/otrk_legacy remain the residue.

## ✅ ROUND 32 (2026-07-06): PW-hi SOURCE patch — C19 3rd occurrence (Lame FULL, 4871/5401) — commit dd5682a
Random partial Olsen/Lame (vblank, flat div 13): V3 PW hi orig $3D vs mine $00
(V1 $DB vs $08, V2 $0C vs $08 — per-voice CONSTANT all song, PW lo sweeps
identically). effect_chain_profiler → orig's $D411 store at $1622 (sidwrite
tail), but no writes to $1753 serve it — the C19 diagnosis tell (read site ≠
canon). Byte dump: the member's `LDA $1753,x` operand is patched to
**$1707,x = the track-ptr lo triple** (set once at init = $DB/$0C/$3D),
pinning each voice's AUDIBLE PW hi at a constant while the internal PWM
machine still runs on $1753 (note-init store + bound compares untouched). FIX
(C19 canonical form): `factory._pulsewidth_hi_const_probe` — static opcode probe
anchored on the `BD..99 02 D4 BD..99 03 D4` store pair, canon PW-accum-lo
operand (base+$750) as the layout-blind base anchor; patched hi operand →
capture POST-INIT bytes at op..+2 → `pulsewidth_hi_const='a,b,c'`; composer pwwrite
swaps `lda pwh,x` → `lda pwhic,x` + 3-byte table. Default byte-identical;
base-relative census (anchor on the PW-LO operand in the SAME match, NOT the
load addr — load-shifted members false-positive otherwise) proved Lame is the
ONLY family-1 carrier. verify FULL 117030/117030; full tools/regression.py
green (DMC 14ok+0regr). Truth 4870→**4871/5401** (partial 315→314; NB the
round-31 note's 4832 was stale vs a later sweep); Lame artifacts written.

## ✅ ROUND 31 (2026-07-06): wjmp shadow of $171F shared scratch (Ok_Ob_2_intro FULL, 4832/5401) — commit 1198016
Random partial Ok_Ob_2_intro (Comer, vblank): first div 258, V3 noise fhi orig
$00 vs mine $01. Deep-census classify: off-table hi read idx 120 → $171F =
"wjmp_tmp", the round-22 REJECTED bucket — and the read-moment value GENUINELY
VARIES per (inst,off,note) key ((4,1)×278/(4,0)×79/(4,6)×55), so neither
static nor round-27 event-driven capture can serve it. /amend Lens-1 on the
round-22 blanket: $171F is a shared effect SCRATCH with exactly 3 writers
(disasm: $135A pulse-program RAW speed byte, $1425 glide step<<4, $15A5/$15E2
wave jump-back distance) — all three values the composer ALREADY computes =
the C11 "unexposed tracking var" reframe. FIX: global `wjmp` var shadowed 1:1
at fx_pulse (raw byte reconstructed as isteps[even]|isteps[odd]>>4 — exact
inverse of the extract's nibs decode, emitted as the stride-8 `irawsp` table;
NO schema change) + fx_glide + ws_rd0/ws_drum; redirect row (0x171F,'wjmp',1).
No seed needed: orig init wipes $1718-$179D (covers $171F) + densely written
(fx_pulse unconditional per voice/frame). NOTE the lo-read window also maps
(idx 216). EXPOSURE CENSUS (the amend-proactive step): 72 stored reads on idx
120/216 → 30 v4 FULL members ALL HOLD; 17 no_jumptable = v5-family members
(own composer, unaffected); 12 were ALREADY-partial (C20 re-baseline vs truth
jsonl — stored .usf ≠ FULL!), none moved EARLIER, 3 improved (Solar_Energy
+181k to a pre-existing length-fail tail, Zdeh_Mi_Kot +3280, Saturday_Dance
+1). Full tools/regression.py green. ALSO: Finn/Tune_11 = stale partial,
verified FULL fresh (an earlier round's fix, no play_phases). Truth merged
4830→**4832/5401** (partial 356→354); both artifacts written. Layout shifted
(wjmp + irawsp) — stored FULL artifacts byte-shifted-but-equivalent, not
rewritten (round-25 precedent). NEXT: more wjmp-blocked partials may flip at
the next batch sweep (Saturday_Dance/King_of_Earth/Deceased-class members whose
FIRST div was the $171F read are now past it); freq-drift tail continues.

## ✅ ROUND 30 (2026-07-06): noteinit_deferred detector per-voice gap — partial F phase (Dresden_Party_95_II FULL, 4830/5401) — commit 17fd27e
Random partial Dresden_Party (PVCF, CIA, `play_phases='P_F3'`): per-IRQ first
div at pos 13 — orig's V3 first note block = freq+PW+ctrl with NO AD/SR (the
C23 deferred-arm footprint) while the rebuild did a full note-init. ROOT CAUSE:
`_detect_noteinit_deferred` returned the verdict of the FIRST voice with an
observed HR — with a partial F phase only the F-phase voice (V3) defers; V1
soft-starts (skipped) and V2 note-inits immediately on P calls, so the detector
read V2's "immediate" and never inspected V3. FIX (C23 refinement): check ALL
voices, ANY arm footprint ⇒ deferred (no false positive — note-init always
carries AD/SR). Validated: forced noteinit_deferred=1 matched 30465/30465 before
touching the detector; old-vs-new detector verdicts over all 62 stored F-token
`play_phases` carriers = ZERO drift; full tools/regression.py green (DMC
14ok+0regr). Dresden_Party_95_II FULL 130254/130254 (same P_F3 cluster, fix
transferred); Dresden_Party itself first-div 13 → 78261 (arm wave-step V3 flo
$02 vs $81 = the freq-drift tail, separate blocker). Truth merged 4829→
**4830/5401** (partial 357→356); 95_II artifacts written. NEXT: other partials
with partial-F schedules may flip at the next batch sweep; freq-drift tail
unchanged.

## ✅ ROUND 29 (2026-07-06): chained wave-marker in the pre-start loop region (Tichelmann_03 FULL, 4829/5401) — commit 3d648cd
Random partial Tichelmann_03 (flat div 336, V2 fhi orig $00 vs mine $68; ctrl
$40 vs $14 same frame). Inst 12 wave program `$14,$14,$14,$94` freq `21,42,68,00`:
the end marker $94 jumps back BEFORE the program start (43→39), and idx 39 is
ITSELF a marker ($91 → 38 = the settled hold step $41/freq $00, chip ctrl $40
gate-masked). `_slice_wave`'s loop_pos<start branch concatenated
`ctrl_tab[loop_pos:start]` UNSCANNED → stored the $91 marker as a literal 4th
wave step; the composer runtime then re-dispatched it and held the WRONG step
($68/$14). FIX (ledger C11 canonical form, 3rd wave-walk instance): gate the
branch on `any(b>=0x90)` in the copied region → delegate to
`_resolve_wave_chain` (walk simulator handles chained hops + settle). Clean
slices byte-identical by construction; regression-safe: the branch only changes
programs whose old flat list embedded a marker mid-program (if played, the
runtime looped to the wrong step = was partial; if unplayed, stream unchanged).
verify FULL 249282/249282; batch row full (code_hash 542a9f80ef7fbad4); full
tools/regression.py green (DMC 14ok+0regr). Truth merged 4828→**4829/5401**
(partial 358→357); artifacts written. The 2 ctrl-mine>=$90 census candidates
(Necrophobic We_Are_Not_Your_Pal/Whipme, pos-0 V2 ctrl) do NOT transfer —
different first blocker (and note: the composer runtime processes embedded
markers, so a mine>=$90 flat_div is NOT this bug's tell). NEXT: freq-drift tail.

## ✅ ROUND 28 (2026-07-06): Bladeswede FULL — 3 fixes off one first-divergence chase (4828/5401) — commit 61600f2
Random partial Bladeswede (PVCF, CIA 4x, dataflow route play=$2638 wrapper). THE
CHASE PEELED 3 LAYERS, each a shared fix:
1. **Dataflow-path CIA gap:** rebuild logged 4x fewer writes. The dataflow path
   lacked the canon path's `_cia_period_from_writelog` fallback (py65 init can't
   see a latch programmed in the play-vector wrapper: `JSR $1003 / LDX #$13/$31
   → $DC04/5` = $1331). Fix = same fallback wired in. Regression-safe: only
   affects members that were guaranteed-partial (kx write deficit).
2. **R/F phase misclassification (div 96):** the wrapper alternates play with
   `LDX#0/JSR $1591 ×3` = the WAVE-STEP entry (F123), but both observers read it
   as R123 (chord program [0,0,0,3,3,3,7,7,7] re-emits identical values early →
   "refresh"). Rebuild froze every arpeggio at tone 1. FIX (ledger C18 note):
   classify R vs F by CHIP STATE — a pure refresh can only re-emit values
   already on the chip; ANY chip-diverging write on a known reg ⇒ F (no false
   positive), all occurrences chip-equal ⇒ R. Replaces the majority/ties→R hack
   in the pctrace observer + the raw-token period fit in the py65 one (collapse
   F/R for the fit, resolve any-F→F). VERIFIED 0-drift: all 86 stored
   play_phases/cia_period carriers (incl. Compotune's genuine
   P_R123_R123_R123) reproduce identically under the new rule.
3. **Transition off-table reads (div 43018):** V2 fhi orig $1B vs mine $00 on a
   noise step. Notes are FETCHED on a P call (curnote+base at $11A3) but
   note-init (wave restart) is DEFERRED — the intervening $1591 F call steps the
   OLD instrument's program with the NEW curnote; a SOFT ($7C) note skips
   note-init entirely (old program runs its whole duration). Off-table idx =
   old-program offset + new note (inst-13 noise-arp off 52 + note 47 = idx 99 →
   hi reads $170A = V1 TRACK-PTR HI: runtime $1B, file image $00). The composer
   already reproduced the runtime semantics (ctrl/flo matched!) — only the
   extract's add_note enumeration missed (old-program × new-note) pairs. FIX:
   track `running` inst per voice in the enumeration; on every note row also
   add_note(note, running); soft rows don't update running. The existing
   postinit-correction then captures $170A=$1B (constant, set once at init).
METHOD NOTE: the memwatch-on-write state at ONE rare event ($1781=$81 wavepos
$6E with inst cache=1/fx=$A0) looked self-contradictory for a long time — the
resolution was the FETCH/INIT SPLIT (fetch updates curnote/base, init updates
wavepos/fx a call later). When per-voice caches look inconsistent at a write,
suspect the deferred-note-init window before inventing player patches.
verify FULL 654657/654657; full regression green; truth merged (partial
359→358, full 4827→**4828/5401**). NEXT: freq-drift tail unchanged; the
transition-enumeration fix may flip more CIA/noise members — check at the next
batch sweep.

## ✅ ROUND 27 (2026-07-06): EVENT-DRIVEN off-table capture (stable-when-read dynamic reads) +24 = 4827/5401 [ledger C11] — commit 8eb86a4
Random partial I_Hate_Techkkno (The_Syndrom, CIA cia_period=4913). First div
(per-IRQ, NOT the flat pos-0 Trap-C artifact) at 367802: V1 noise note freqhi
orig $08 vs mine $00. Off-table wave-step (inst $12, y=$82) reads $16A7+$82=
**$1729 = SECTOR POSITION** (per-voice prefix-command counter, cycles 0-9 globally).
**THE /amend SKILL (user-prompted) OVERTURNED my "positional, defer to Move-1"
verdict.** I'd accepted the round-22 blanket ("sectorpos unmappable") — but it
PREDATES round-23's arrangement technique. Lens-1: the "capture file-image /
globally-constant value" model is the suboptimal past fix. Step-3 MEASURE: over
the full song, $1729 is **STABLE AT THE READ** ($08 both occurrences of this note)
even though it varies globally — a static one-record patch (hi $00->$08) makes it
fully FULL. So NOT positional — a capture-VALUE bug.
ROOT CAUSE: `_assign_offtable_freq` reads the file image; `_correct_offtable_postinit`
only fixes bytes CONSTANT over a 6s TIME-sample → omits $1729 (varies) → keeps
$00. FIX = round-22's deferred EVENT-DRIVEN capture (`_offtable_eventdriven`):
memwatch-on-write D416 (per-play(), CIA-safe) snapshots all 3 voices'
(y=$1783,curnote=$1012,inst=$1015,base=$172F/$1732); per (inst,off,note) key use
the read-moment base where STABLE across the verify window. Gated on post-init
leaving a varying byte.
⚠️ **CALIMERO REGRESSION = amend Lens-1 RECURSIVELY:** the fix collided with a
PAST fix (round-25 igla/iglb seeding). Reads on REDIRECT-MAPPED idx (gla/glb/ioff/
dur — DMC_OFFTABLE_STATE) are live-tracked + SEEDED from the file-image leftover;
overriding their static value broke the seed (FULL->partial @6743). DISCRIMINATOR:
`_redirect_mapped_idx` (from composer_asm) — event-driven applies ONLY to
WINDOW-served (non-mapped) idx. $1729 non-mapped ✓; dur/glb/ioff mapped ✗.
REGRESSION-SAFE on the window-served set (FULL read matches → runtime==file-image
→ no change). CENSUS 383 partials + 300 FULL: **+24 FULL, 0 regr** (Calimero
restored after the exclusion); full tools/regression.py green. Family-1
4803→**4827/5401 (89.4%)**; jsonl merged (partial 383→359). LESSON: an off-table
capture-value fix must respect window-served vs redirect-served idx. NEXT: the
remaining freq tail — genuinely-varying reads (per-key non-stable, e.g. otrk $1726
{$14,$15}) stay residue (round-23 arrangement / Move-1).

## ✅ ROUND 26b (2026-07-05): UNIFY to play_unit_repeat + 3rd_Voice FULL (4803/5401) [ledger C24 recurring]
Extended round-26 to the 2nd (and, proven, LAST) family-1 member with this feature:
3rd_Voice.sid (Tichelmann). Its stub `$1EF5: LDX #2 / JSR / JSR / JMP $10A0` doubles
V3 AND — via the JMP-into-filter-tail (leftover play-body JSR return re-enters the
tail's RTS) — emits $D416/$D417 TWICE/frame. USER-STEERED representation: replaced
the two knobs (voice_tick_repeat 3-tuple + filter_tail_repeat scalar) with ONE unified
`play_unit_repeat` = 4-int list [v0,v1,v2,filter] (the play body runs 4 UNITS/frame,
each N×). Talk_a_Lot=1,1,2,1; 3rd_Voice=1,1,2,2 — they differ ONLY in the filter slot.
CORE-TENET re-anchor (user-prompted): the filter slot is a first-class write-stream
config field (parametrises a $D416/$D417 write-count difference, encodes NO code layout
— same class as nextvoice_write_order), produced by CLEAN inline code (not by mirroring
the stack-re-entry trick). An earlier "filter_tail is less musical/bookkeeping"
hesitation was the drift-tell = applying the §7 musical-content lens to an engine-config
field. Probe `_play_unit_repeat_probe`: STATIC byte-probe, RTS terminator (clean) or
JMP-to-filter-tail on the LAST voice (→ filter=2). REGRESSION-SAFE: '1,1,1,1' default
byte-identical (MD5 old-vs-new on canonicals); the REAL probe over all 4802 FULLs fires
on exactly 1 (Talk_a_Lot). Layout-independent write-stream recheck (closed the STX-probe
648-member blind spot) CONFIRMED these 2 are the ONLY family-1 members with the feature —
others with doubled writes are whole-play multispeed [N,N,N] (=play_repeat: Heniek/Fucking)
or a bespoke test player (Sound_Test [6,1,26]). +1 FULL: 4802→**4803/5401**; jsonl updated
(partial 384→383). NEXT: freq-drift residue tail (unchanged).

## ✅ ROUND 26 (2026-07-05): PER-VOICE TICK MULTIPLIER (voice_tick_repeat, Talk_a_Lot_2_tune_06 FULL) — commit 6e01c3e [ledger C24 NEW]
Random partial Talk_a_Lot_2_tune_06 (Tichelmann_Kay): first div frame 1 $D410
(V3 PW lo) orig $10 vs mine $00. ROOT CAUSE: the play body's THIRD voice JSR
($109D) is redirected to a stub `$1FE0: JSR $10B0 / JSR $10B0 / RTS` — voice 2
(V3) is ticked TWICE per play(). V3 runs its pulse program 2 steps/frame and
re-emits its full freq/PW/ctrl block TWICE ($10 then $00) every frame; the
rebuild ticked V3 ONCE, alternating PW $10/$00 per frame (a "double-speed voice"
editor hack). NONE of the voices are $40 dual-effect (177D/E/F = $30/$00/$00) —
the dual-effect path was a red herring; pc-trace showed both $D410 writes from
$161C with X=$02, and the play-body JSRs came from $1FE0/$1FE3 not the canon
$109D. FIX (two parts): (1) composer play-body voice-call sequence parametric
over `voice_tick_repeat` triple (default '1,1,1' = byte-identical 3-JSR body;
'1,1,2' adds one `jsr voice` for V2, no INX so X stays 2); (2) factory
`_voice_tick_repeat_probe` = STATIC byte-probe (C19 method): follow play vector →
locate `STX fclaim` (base+$720) → read the 3 per-voice JSR sites → count
`JSR<voice>` in a clean `JSR*/RTS` stub. Non-clean stub → None (unchanged).
REGRESSION-SAFE BY CONSTRUCTION: default byte-identical (old-vs-new MD5 proven on
canonical members) + family-1 census found ZERO FULL members with a non-canon
repeat — only 2 members family-wide are non-canon, BOTH partials: Talk_a_Lot
(1,1,2, now FULL) + 3rd_Voice.sid (unrecognized stub `$1EF5: LDX#2/JSR/JSR/JMP
$10A0` = voice-2-twice PLUS re-runs the $D416/$D417 filter tail — left as residue,
the CANONICALIZE trigger if a 2nd multiplier variant appears). verify_dmc FULL
105458/105458; full tools/regression.py green (0 regr all families). Family-1
4801→**4802/5401**; truth row updated (tmp/dmc_wide_results.jsonl partial 385→384).
DISTINCT from play_repeat (whole play(), all voices+filter tail) and C18
play_phases (play VECTOR cycles whole CALLS; this multiplies ONE voice within one
call). NEXT: the freq-drift residue tail (unchanged from round 24/25).

## ✅ ROUND 25 (2026-07-05): SEED gla/glb from off-table leftover (98_Mix FULL, /amend Lens-1) — commit 87bde4c [ledger C11]
Random partial 98_Mix (Stix): first div pos 7, V2 freq-LO orig $4C vs mine $00
(same on V3). Inst-0 wave prog `freq=[255]` -> off-table idx 255 -> the composer's
`gla[2]` via the DMC_OFFTABLE_STATE redirect. gla ($1744) is SPARSE glide state
(written only in glide branches), so a non-gliding voice leaves it at the composer's
ZERO-init while the orig keeps its uncleared file-image LEFTOVER $4C — the redirect
returned $00, SHADOWING the correct static `offtable_freq` capture (ovr[63]=$4C).
The HI byte ($81) was right (no state var covers its idx). THE /amend TRAP: removing
gla/glb/glsp from the map fixed 98_Mix but REGRESSED Alien_WOW/Hardcore (deep glide
read at 201698 — a DYNAMIC reader that legitimately needs the live redirect; caught
by tools/regression.py DMC 13ok+1regr, the offtable_guards portfolio entry). Lens-1:
the blanket map (commit 1ab8c46 "these track byte-identically") was the real defect.
OVERARCHING FIX: keep the redirect, SEED gla/glb,x at init from the captured leftover
(igla/iglb = ovr-window byte at `A-ORIG_FLO-192`; gla[x]->ovr[61+x], glb[x]->ovr[64+x])
so they track from frame 0 — static reader gets the leftover, dynamic reader overwrites
the seed on its glide arm. glsp NOT seeded (would spurious-trigger fx_glide, gated
`lda glsp,x/beq`). 0-regr by construction for the seeded vars. VERIFIED: 98_Mix FULL,
Hardcore held FULL, tools/regression.py ALL families 0 regressed (DMC 14ok+0regr).
GENERAL LESSON (ledger C11): a redirect var must be init-cleared on BOTH sides OR
densely-written-every-note (converges) — a SPARSELY-written var needs leftover-SEEDING,
else it regresses static-leftover readers. CLOSEOUT (targeted, 886 = 386 partials + 500
FULL sample): **+1 FULL (98_Mix only), 0 regressions** → family-1 4800→**4801/5401**.
As the census predicted, gla was the FIRST divergence only for 98_Mix; the other ~44
freq-mine=$00 partial candidates are DEEP (other first blockers) — /amend Lens-3 clean.
98_Mix artifact written; truth merged (tmp/dmc_wide_results.jsonl). The layout shift
(6 igla/iglb bytes) makes all FULL artifacts byte-shifted-but-write-stream-EQUIVALENT
(0 regr proven) — not rewritten (artifacts aren't the coverage source; a full batch
refreshes on demand). NEXT: the freq-drift residue (in_table/off-table deep tail).

## ✅ ROUND 24 (2026-07-05): the NOTE-START COLLAPSE — per-member 2-frame note-init deferral (+5 f1 = 4799/5401, 0 regr) — commit 1a632fe [ledger C23]
USER-STEERED (the round-23 lesson re-applied): "a correct fix that regresses ⇒
the regressed SIDs are FULL through a suboptimal/blanket model — reimplement to
serve BOTH; focus on the FIRST DIVERGENCE, not FULL; think what the composer did
in the editor." All three steers were load-bearing.
**THE BUG:** C18's F phase was modelled with ONE behaviour — `voice_fx →
frame_entry` ($11F9: note-init on the F call). Correct for the IMMEDIATE
note-start majority, WRONG for a CIA class whose play-routine enters the F call
PAST the note-init check ($1591 wave-step): a note fetched on a P call only ARMS
on the F call (wave-step only, ADSR HELD at the $0F0F hard-restart leftover) and
note-inits on the NEXT P call = the DMC 2-FRAME note-start (orig: HR $17FB → arm
$1591 → note-init $1201; confirmed via pc-trace + disasm). Composer collapsed it
(real AD/SR one play()-call early), diverging at pos 11 (o=V1flo, m=V1SR) at
every note-start. ALL 15 cluster members CIA; all F.A.K.E FULLs vblank.
**THE TRAP (why naive fix is net-NEGATIVE):** `voice_fx → wavestep` for ALL F
regressed ~20 currently-FULL members (Fuck_Off/Words/Life_Is_Death...). Words is
P_F123 (SAME token as F.A.K.E) yet needs the OLD behaviour. Not derivable from
the schedule string OR the multispeed factor (Words & F.A.K.E both P_F123 AND
both 1.82 calls/frame). A genuine per-member play-routine ambiguity (C22 sibling:
the token is the ambiguous "encoding").
**THE FIX (observe, don't parse — C18/C23):** `factory._detect_noteinit_deferred`
reads the OPENING write footprint (reloc-invariant, no PCs): after a voice's HR
call (ctrl=$08, AD=SR=$0F), the first call re-emitting its freq/ctrl is the
note-init IFF it ALSO writes AD/SR; freq/ctrl with NO AD/SR = the ARM ⇒
deferred. note-init ALWAYS carries AD/SR ⇒ "deferred" has NO false positive ⇒
regression-safe by construction. Sets `noteinit_deferred=1` (BOTH factory build
paths — canon @~L1122 + dataflow @~L849, F-token schedules only); composer routes
`voice_fx → wavestep` when set, `frame_entry` otherwise.
**RESULT (full family-1 closeout, 607 non-FULL re-verified):** +5 FULL →
**family-1 4794→4799**. 4 carry noteinit_deferred=1 (2_Speed / Voices_in_My_Head /
Canned_with_canned_beer / Compotune — the o=flo/m=SR cluster WAS the whole
reachable deferring class); +1 non-arm (Ucieczka_z_Tropiku = a stale-partial a
prior round already fixed, byte-identical build now verifies full). 0
regressions: all 56 currently-FULL F-token members held + full
tools/regression.py green; 5 artifacts mass-written (the 4795 byte-identical
round-23 FULLs correctly skipped, stale code_hash). 5 gains merged into
tmp/dmc_wide_results.jsonl.
**13 noteinit_deferred=1 members total: 4 flipped, 9 have a DEEPER blocker** now
exposed (the note-start first-divergence is RESOLVED for all 13 — "focus on
first divergence" progress): mostly V1/V2/V3 FREQ-DRIFT (Real_Hardcore V1flo
24→0, Hexzakk V3flo 49→96, Noising_Funk V1fhi 73→0, McBurger V1fhi 2→86,
Viiskyt V3flo deep @110k) + F_A_K_E-Intro (sub1 pre-existing 2x) + Big_GLORZ
(len) + Sound_Test (len 1/6, dispatch). NEXT: the freq-drift second blocker
(the same class as the round-22 in_table/hi_table tail) — census these 9 +
the broader freq-drift residue.

## ✅ ROUND 23 (2026-07-04): otrk EXACTNESS via the composer's ARRANGEMENT (transpose-cmd placement = musical content, §8) → +12 family-1 = 4795/5401 (88.8%) — commit 9c0c33e
USER-DRIVEN (single random partial Plasmachaos → "the regressed SIDs may have a
SUBOPTIMAL implementation that blocks us; explore more"). The blocker was
otrk_legacy (the round-9 val=i+1 positional APPROXIMATION). Representation
principle §8: the composer NEEDS the transpose-command PLACEMENT to reproduce
the off-table sonification of $1726 — that placement is their ARRANGEMENT
(musical content), NOT the byte-offset (engine bookkeeping, DERIVED). Two fixes
to the otrk model (`_otrk_model`/`_otrk_rcmd_model` + composer):
1. **cur-init = transposes[0] (was 0) — a latent BUG, the main driver.** A
   LEADING transpose command was double-counted (pad covers its byte, then the
   change-check re-added it) → spurious legacy fallback for any voice whose
   FIRST entry is transposed. Recovers the whole otrk-legacy cluster
   (Hardcore/Acidmania/Short_Acid_Loop/Insane/1st_Intro/...). NO schema change.
2. **`_otrk_rcmd_model`: carry REDUNDANT mid-track transpose commands** as a
   per-voice bitmask (their arrangement positions); composer adds +1/byte,
   deriving the exact offset. Recovers Plasmachaos V2/V3 (the periodic $A0
   reset at entry 2). This is the §8 musical-content addition.
3. **Glide degenerate-detection:** restore the dropped '#' in glide_to ONLY
   when it degenerates the glide to the row's OWN note (Plasmachaos F-10
   glide_to=F#10 ran the wrong direction — a 2-digit-octave-sharp parse gap);
   other off-table glide targets = dynamic-byte sweeps, left as the write-
   stream-optimal natural parse (ledger C11, don't "fix" them).
CLEAN: full 5401 re-verify → +12 FULL, 0 REAL regressions (4784→4795).
⚠️⚠️ THE TWO TRAPS THAT MADE THIS LOOK LIKE A −22 LOSS (both are the C20
re-lesson): (a) the glide fix "regressed 22/104 FULL glide members" — but ALL
22 were STALE palimpsests (`.usf` grep said full; CURRENT code builds partial).
I mis-baselined against stored .usf TWICE. (b) the otrk fix "regressed Zak_2 +
Bilinski" — Zak_2 = a PARALLEL-BATCH siddump FLAKE (FULL on single re-verify);
Bilinski = a stale-full palimpsest. ALWAYS re-baseline a "regression" against a
FRESH single-member current-code build before believing it. THE USER'S INSIGHT
(a correct fix that regresses ⇒ the regressed SIDs may be FULL through a
suboptimal path, or the baseline is stale) is the load-bearing lesson.

## ✅ ROUND 22 (2026-07-04): deep tail = UNEXPOSED tracking vars, not hard → +74 family-1 = 4784/5401 (88.6%) — commits 07c2125/a026b74/65c2e95/82538a1/f66a1bf
THE REFRAME: most of the "deep off-table freq tail" is NOT divergent state —
the composer ALREADY tracks the value byte-identically (it must, to reproduce
the write stream); it's just not EXPOSED to the off-table redirect. Recipe
(new ledger C11 note): census deep readers → for each unmapped var, the
INDEX-MATCH check (`tmp/verify_ioff.py`/`verify_filtervar.py`: memwatch
composer_var + wnote at the divergent event) → (a) wnote matches + var==orig
⇒ add a redirect ROW (clean, transfers, 0-regr by construction); (b) wnote
differs ⇒ wavepos drift (HARD); (c) var!=orig ⇒ non-tracking accumulator (HARD).
1. **STALE-PARTIAL drift re-verify (+10, fix-verdict step):** the round-21
   merged truth's PARTIALS predated the cpwmax/durrel fixes (only GAINS were
   re-verified) → 10/475 already FULL. LESSON: drift-re-verify the residue
   BEFORE censusing it — I burned an hour classifying stale Abrakadabra/cpwmax
   as "var-value bugs" before a fresh find_first_divergence showed it FULL.
   The cpwmin/cpwmax "cluster" was ~entirely stale (round-21 DID fix them).
2. **ioff ($174D inst#*11) redirect row (+12, commit 07c2125):** the orig keeps
   the instrument-record offset (exact 6502 carry-chain $1213-$1222) in $174D,x;
   read off-table when a note idx wraps to 166-168. The composer indexes by SLOT
   so had NO offset var — added ioffval[slot]=_inst_offset(id-1), stored to
   ioff,x at note-init (with cinst), (0x174D,'ioff',3). Found by the single-SID
   loop on Broken (first div $174D → FULL), transferred 12/13, 0/40 regr.
3. **filter-state $1718-$1723 5 redirect rows (+19, commit a026b74):** global
   filter machine (spdctr/fstep/fframe/fbase/fres) — the composer ALREADY
   tracks all 5 byte-identically (verified index+value on 5 reps). Added rows;
   19/32 readers FULL (13 have deeper 2nd blockers), 0/60 regr. NOT mapped:
   $171C fcut (cutoff ACCUMULATOR drifts, regressed Humppa) + $1720 fclaim.
4. **notectr/sectpos $1729 REJECTED (measured):** leading unmapped candidate
   (18) but positional — measured hundreds of editor-chosen redundant dur/instr
   re-asserts/member (ratio 0.04-0.44/note, no rule), so exact shadow needs
   per-event byte-widths in USF = C7 anti-pattern. See tmp/notectr_scoping.md.
CLOSEOUT: full re-verify of all 465 partials with both fixes → +50 FULL (incl.
~19 members blocked on ioff/filter DEEPER than first-div); merged 4720→4770.
5. **fcut $171C + fstop $171E + frep $171D (+14, commit f66a1bf):** the "non-
   tracking" triage turned up that fcut is NOT a drifting accumulator — it
   drives the identical $D416 stream so live fcut == orig $171C by construction
   (verified $20==$20). The C11 "regressed Humppa" caution was fcut BUNDLED with
   wavepos $177A; fcut ALONE is 0-regression (Humppa's div byte-identical w/wo
   it, Object_of_Art improves). fstop/frep = same filter-def-load class as
   fres. Closeout re-verify +14 FULL (of 401), 4770→4784. LESSON (ledger C11):
   when a caution names TWO co-mapped addrs, re-test SEPARATELY. otrk (6) =
   otrk_legacy POSITIONAL-hard (val=i+1 approximation, can't reproduce the exact
   orderlist byte-offset — same class as notectr); $1720 fclaim rejected;
   $1721/$1722 have no composer cache var (read inline via fdstep/fddur).
6. **CIA-census gap CLOSED (measurement, user-directed "reuse the CIA solution
   from elsewhere"):** the 40 cia_skipped were the deep-census tool bailing on
   CIA (flat memwatch event-N mis-aligns, Trap C) — NOT a verdict gap (the batch
   already verifies CIA via `writelog_per_irq_capture`). Wired that same per-IRQ
   capture into `tmp/f1_deep_census.py` classify with an init offset
   `init_reg = flat_total - per_irq_total` (reg-write TOTAL is bucketing-
   independent; per-IRQ drops the init prefix, flat keeps it). Validated (0
   cia_skipped, ~7/40 event_misaligned residual). RESULT: the CIA partials are
   the SAME hard-class distribution (notectr/otrk/wavepos/sectpos positional +
   in_table + $1720/$1721) — NO missed fixable cluster.
RESIDUE (401 partial, r22d CIA-aware census): notectr 23 + otrk 13 + wavepos 9
+ sectpos 6 = ~51 POSITIONAL (Move-1-scale, need editor-position representation
in USF); in_table 64 + hi_table 15 = per-member freq/schedule DRIFT; $1720
fclaim 10 + $1721/$1722 10 (no cache var) + wjmp_tmp 13 ($171F temp) = rejected/
unmappable; + tail. THE CLEAN UNEXPOSED-TRACKING-VAR LEVERS ARE NOW EXHAUSTED
(ioff/filter/fcut/fstop harvested). NEXT is genuinely hard: (a) a Move-1
positional-encoding representation for notectr/otrk/sectpos/wavepos, (b)
per-member in_table drift, (c) family-2/V5 have their own fresh levers.

## ✅ ROUND 21 (2026-07-04): full closeout (authoritative count + palimpsest cure) + cpwmax/cpwmin swap → family-1 4710/5401 (87.2%), family-2 2413/2889 (83.5%) — commits 09f8034/d1636b1
1. **Typed-init cleanup (09f8034):** durrel priming moved from `durrel_init*`
   params → typed `InitVoice.dur_reload` (§4.5 engine-state priming; the params
   form was the "cite hardrestart_test_init to defend the easy choice" drift-tell caught
   on a principle re-read). 46 builds byte-identical; 136 stale-params USFs
   rewritten; on-disk verify + full regression green.
2. **Full family-1 closeout re-verify (5401, tier-2 milestone):** authoritative
   **4698 FULL** (net +3 vs the merged file: 10 gains, 7 stale-FULL palimpsests
   exposed). Palimpsest attribution via a git worktree at the round-18 commit
   (dc61b47) + build+verify — all 7 diverge IDENTICALLY under the pre-session
   tree ⇒ this session introduced ZERO regressions; the 7 predate round 18.
   Adopted the closeout jsonl as the family-1 merged truth.
3. **cpwmax/cpwmin off-table var-name SWAP (d1636b1, +13 FULL f1+f2, 0 regr):**
   the pos~74-81 V2/V3 freqhi cluster (~25 members). ROOT CAUSE: the composer's
   `cpwmin`/`cpwmax` vars hold PW bound A / bound B (extract min_hi=bound_a,
   max_hi=bound_b) — self-consistent for the PWM sweep so members were FULL, but
   the off-table redirect mapped orig $1756 (bound A) → var cpwmax (holds bound
   B = A EOR $0F) → mine=$0B where orig=$04. TELL = a cluster whose (orig,mine)
   values are EOR-$0F complements. Fix = swap the two map entries to point each
   orig ADDRESS at the var holding its VALUE. +12 f1 (incl. the Flyt/Yoko
   palimpsest cluster) / +1 f2; 40+2 exposed FULLs hold; full regression green.
   The redirect asm is emitted for EVERY member so all 7123 FULL builds were
   byte-rewritten (write-stream-neutral for the previously-FULL ones).
SESSION 2026-07-03/04 TOTAL: family-1 4570→4710 (+140), family-2 2294→2413
(+119) = +259 FULL. NEXT: the residue is now the DEEP freq tail (>=4k, ~250,
heterogeneous per-member off-table sonification / state-evolution — no clean
lever) + notectr/sectpos (~14, otrk-playbook, scoping in tmp/notectr_scoping.md)
+ CIA-census-blind 56 (need per-IRQ event alignment in f1_deep_census.py) +
the remaining EOR-complement / small-value freqhi mid-clusters (per-member).

## ✅ ROUND 20 (2026-07-03): family-2 recovery sweep +118 (2412/2889 = 83.5%) + durrel redirect row +26 → family-1 4695/5401 (86.9%) — commit b4e486a
1. **Family-2 recovery sweep (user-directed):** the rounds-18/19 SHARED-code
   fixes swept over family-2's 595 non-FULL → **+118 FULL (115 ex-partial +
   3 ex-unsupported)**, 2294→2412 (83.5%). All 118 + the 105 exposure-censused
   FULLs (96 durrel-window + 10 glide0 + 0 probe carriers) re-verified 223/223
   under the final tree. f2 residue 420 partial / 45 unsup / 12 error.
2. **durrel redirect row (the round-19 plan, landed):** (0x173E,'durrel',3)
   — live shadow at every event's `sta dur,x` (row duration ≡ orig reload BY
   CONSTRUCTION: every orig row reloads its counter from $173E); leftover
   primed from durrel_init params (post-init/file-image; emitted only for
   window-reading members: flo idx 247-249 / fhi 151-153). Event dispatch →
   JMP trampolines (branch range). **+26/32 census-cluster FULL; 65/66
   window-reading FULLs hold.** Sweet_Honey = a PRE-EXISTING LATENT (stored
   USF predates round 9; committed-tree rebuild diverges identically @81,
   V3 fhi reads live cpwmaxV2 $0B vs orig $04 — suspect a later-round
   instrument-decode interaction; re-bucketed partial, diagnose per-member).
   EXONERATION METHOD: stash → committed-tree build → same divergence =
   the new change is innocent (now in ledger C11).
314 builds mass-written; DB refreshed; full regression + portfolio green ×2.

## ✅ FAMILY-1 round 19 (2026-07-03): full deep census → 2 fixes → +100 FULL = 4670/5401 (86.5%) — commits f0d4ae8/93cc8ea/22f47ca
Full-set deep census (`tmp/f1_deep_census.py`, all 353 deep freq partials →
tmp/f1_deep_census_r19.jsonl): in_table 144 / off_table 138 (top hits:
durreload 32, notectr 14, long unmapped tail) / cia_skipped 56. Two fixes:
1. **hold_gateoff STATIC opcode probe (C19 CANONICALIZED 2×):** a widespread
   editor build (Surgeon/Imaic/Rio/Taxim/Phobos/Behdad: 514 FULL + 97 partial
   carriers) patches ONE byte — sub_17EC's $17EF BC→60 (LDY→RTS) = mask-only
   gate-off. Found via the Rio pos~330 cluster (rebuild emitted an extra
   AD/SR=$00 pair at a holding gate-off). `factory._hold_gateoff_probe`
   follows the holding-branch JSR by OPCODE SHAPE (layout-blind) and reads
   the patched instruction — the blind `frames_clear_adsr` retry could NOT
   reach these 97 (their origs write AD/SR=0 via other paths). +17 FULL,
   all 514 exposed FULL carriers hold. LESSON: probe a patch STATICALLY
   (read the instruction), never via a bounded write-stream scan.
2. **Mode-0 glide-cancel, $C0 speed 0 (C22 3rd occurrence):** the $Cx handler
   unconditionally stores the speed nibble to glsp — speed 0 = GLIDE-CANCEL.
   to_usf suppressed glide=0 on mode-0 rows AND the composer's encoder keyed
   the glide tail on `if gspd` → the cancel became a plain note and a previous
   row's armed glide kept ramping accl +speed×16/frame forever
   (Grave_Story_intro @6427 → FULL). THE ×16-QUANTIZED DELTA TELL: censusing
   (mine−orig) over the in_table class showed 56/104 deltas ≡ 0 mod 16 = the
   speed-nibble ASL×4 — census the delta histogram BEFORE per-member drilling.
   53/104 in_table members flipped FULL. 41 exposed FULLs re-verified all-FULL.
CLOSEOUT: 640-member sweep +100 FULL total, 0 regressions anywhere; 647
builds mass-written; full regression green. RESIDUE (515 partial / 25 error):
off-table deep tail (durreload 32 = NEXT: add (0x173E,'durrel',3) redirect
row — composer has NO durreload var; per-event durations == the orig reload
value by construction, so shadow it at every `sta dur,x` site + post-init
leftover priming + C11 transfer test; then notectr [=sector position,
encoding-specific like otrk — needs orig byte-offsets carried]), in_table
non-quantized 48 (true per-member drift, arbitrary deltas −99..+113),
cia_skipped 56 (census tool lacks a per-IRQ event-alignment mode), pos~8
wrapper class 15 (parked, round 12), Object_of_Art wavepos class (blocked,
C11 hard boundary).

## ✅ FAMILY-1 round 18 CLOSEOUT (2026-07-03): deep-tail census → 3 fixes → +215 FULL = 4570/5401 (84.6%) — commits 9c243d7/e596bd7/3d3a930
CLOSEOUT DONE: batch-harness sweep (1060 = all non-FULL + 14 exposed FULLs) →
**+215 newly FULL, 0 down** (all exposed FULLs hold); 229 builds mass-written
(incl. the 14 exposed — data layout changed); dmc_wide_results.jsonl merged
(full 4570 / partial 615 / unsup 191 / error 25); hvsc84.csv refreshed;
regression portfolio RE-DERIVED (5 → 6 members, now covers pat:slide);
full regression green ×2. Fresh flat_divs for the 615 partials are in the
merged jsonl — next round starts with divergence_census / f1_deep_census on
them (the deep in_table drift class + the unmapped-addr off-table tail).
DEEP-TAIL METHOD WIN: built `tmp/f1_deep_census.py` — for each deep (≥4k) freq
partial, memwatch wnote+curnote AT the divergent write (event index = per-reg
write count up to flat_div pos) → classify in-table drift vs off-table hit +
name the state addr. 100-sample: **in_table 59%** (NOT the off-table class!) +
long heterogeneous off-table addr tail. Three root causes found + landed, full
regression green, ledger updated:
1. **Wave-walk 8-bit jump-back UNDERFLOW (C11; engine_model._slice_wave):**
   marker hop `pos - (byte-$90)` is 8-bit SBC — underflow wraps HIGH
   (Cool_Compo_Tune: $FF marker at pos $26 → $B7); in-table slicer's negative
   loop_pos did a Python NEGATIVE slice (extended-table tail garbage), pre-chain
   variant RAISED wave_marker_chain (13 false rejects). Fix: route both to
   `_resolve_wave_chain` (existing mod-256 walk). +20 FULL (10 ex-unsupported,
   2 ex-error), 5 exposed FULLs hold.
2. **Mode-0 glide under soft-start misrouted to slide (NEW ledger C22):**
   `_row_event` tested `noretrig and glide` — but mode-0-soft rows carry
   noretrig TOO; true discriminator adds `NOT glide_to`. Gangstallica: rebuild
   held old base gliding DOWN where orig rebased to note A gliding UP. **+138
   FULL** (172 exposed partials verified; 2 exposed FULLs hold — they coincide
   when prev==A).
3. **Slide speed-nibble 0 rendered = soft note (C22 2nd occurrence →
   CANONICALIZED):** $Dx speed 0 = engine "set target, NO note load, hold"
   (jumps to the REST tail $1174); to_usf suppressed `glide=0` → composer
   loaded the note early (Apocalypsa octave drop; the Surgeon deep cluster).
   Fix: slide rows ALWAYS emit glide=N; decoder tests flag PRESENCE. +30 (81
   exposed; 7 exposed FULLs hold — 2 of them via the batch's mask_only retry;
   my ad-hoc verify_dmc harness LACKS that retry, initial 'regressions' were
   harness artifacts).
CENSUS RESIDUE (next rounds): remaining in_table deep = per-member drift
(Apocalypsa/Shudder 2nd blocker = a hold-gate-off adsr-clear asymmetry, dur
check order — UNRESOLVED, look there first); off-table map-row candidates:
$1718 spdctr / $1719-$171A fstep+fframe / $1720 filter-claim (composer already
models them), notectr+dur+gla rows, hi_table(static) hits (should be capturable
— why aren't they?), CIA skipped 9. NB parallel basic_program session live in
the tree (src/usf cutoff_lo changes = theirs, additive) — commits file-scoped.
CLOSEOUT PENDING: tmp/f1_r18_sweep.jsonl (batch harness, 1060 = all non-FULL +
14 exposed FULLs) → merge → mass-write → DB → portfolio re-derive.

## ✅ FAMILY-1 rounds 16/17 CLOSEOUT (2026-07-03): +79 recovery sweep → 4355/5401 = 80.6% — commit 8831188
The all-partials sweep (893) under round-16/17 code recovered **+79 FULL**
(long-orderlist partials fixed by the 16-bit track pointer + exact inst-offset
chain — the >85-entry wrap had been masquerading as "deep tail" divergences).
All 79 re-verified with the CURRENT tree per C20 before mass-write; 804 builds
rewritten (79 + the 725 held long-orderlist FULLs), DB refreshed. Session
2026-07-03 total: 4220 → 4355 (+135) over 5 rounds. FRESH RESIDUE (804
partials, current flat_div): early<64 = 81 (top: pos~8 wrapper class 15
[parked, needs robust chunker], V1flo pos~0 7, V3flo 6 [Object_of_Art
wavepos-blocked], V1sr 5 [heterogeneous, Techno's sibling causes], Necrophobic
11/0 3, Speed_It_Up 3, Reggae_Me ORDER 3, Super_Seven+Scratch_It wrappers 2)
· mid 141 · deep ≥4k = 582 (the true off-table/drift tail, fresh flat_divs in
tmp/dmc_wide_results.jsonl for clustering via divergence_census --partials).

## ✅ FAMILY-1 round 17 (2026-07-03): pwstep redirect row + hrtest wipe fix (4276 current) — commit bebb372
Round-16's 727-FULL sweep: 725 hold, 2 = stale-FULL palimpsests re-bucketed
(Yo_Raps stored build diverged at 0(!); Brendas at 75). Brendas root-caused =
off-table hi read wnote idx 182 → orig $175D = V2's CURRENT PW STEP ($175C,x
= phase nibble + base, STA at $1379): orig live 0, our static capture $A2.
NEW map row (0x175C,'pwstep',3) + fx_pulse stores its step into pwstep,x
(guard+freewheel frames run fx_pulse ✓ lockstep; init-wiped both sides).
Brendas 100% → FULL. ALSO fixed round-13 latent: hrtest sat INSIDE the
state0..state_end wipe → init cleared the hardrestart_test_init priming; moved after
state_end (orig $17FB persists through init); all 24 hr-patch members hold.
Gate: 25-member re-verify + full regression green. NOTE: the running partials
sweep uses round-16 code — its newly-FULL members must be RE-VERIFIED with
current code before mass-write (verify/build code-mismatch discipline, the
Happy_Hour lesson). Pending: 725-FULL artifact rewrite (current code) + DB.

## ✅ FAMILY-1 round 16 (2026-07-03): exact inst-offset chain + 16-BIT TRACK POINTER (+1 now, 4277/5401; sweeps queued) — commit d99fe19
Two exactness/capacity fixes from the V1sr class dig (heterogeneous bucket — 
only Techno shared the cause; 4 others still open, per-member):
(a) **instrument offset ≠ (iid*11)&0xFF** — the canon chain (CLC/ASL×3/ADC×3,
one CLC) propagates an INTERMEDIATE ADC carry into the next add: iid≥26 = +1
(≥52 +2) vs mod-256. The Hardcore-era fix validated on iid 24-25 where the
models coincide. Now emulated exactly in `_decode_instrument`. Techno FULL.
Ledger C11 REFINED (emulate the instruction sequence, don't algebraize).
(b) **round-9 LATENT: 3-byte track entries broke the 8-bit track index** past
85 orderlist entries (`ldy trkpos,x` wraps; loop tail `(loop_to*3)&0xFF`
masked). Exposed as a stale-FULL palimpsest: Happy_Hour (V1 198 entries,
loop@99) verified via its PRE-round-9 stored build but current code failed it
at the wrap (~write 108k, V1 misses the loop-boundary hard restart while
V2/V3 continue). **727 FULLs carry >85-entry orderlists = all latently
non-reproducible since round 9.** FIX: trkpl/trkph = 16-bit RUNNING entry
pointer (pat_end +=3 w/ carry; $FF loop tail = `.byt $FF, <(lbl+n*3),
>(lbl+n*3)` label arithmetic; trkpos deleted). Gate: 82-member stratified
sample (40 long-orderlist + 18 inst-26-exposed + recent classes + the
1532/1032-entry extremes) 0 regr; full regression green. QUEUED (running,
tmp/f1_round16_sweeps.py): (A) all-727 re-verify + rewrite, (B) ALL-partials
recovery sweep (long-orderlist partials may flip — Happy_Hour-like cases in
the "deep tail"; also refreshes flat_div for clustering). DIAGNOSIS PATH:
Happy_Hour's regression was blamed on my inst fix → USF diff exonerated it
(only otrk_period/filter-prog params differed) → param bisect exonerated
THOSE → divergence context (all-voice hard restart missed at the song loop)
pointed at the track runtime. Lesson: attribute a re-extract regression by
USF-DIFF + param-bisect BEFORE blaming the newest change.

## ✅ FAMILY-1 round 15 (2026-07-03): dual-parity address on shifted bodies (+27, 4276/5401 = 79.2%) — commit 9c2fa6c
The pos~16 class (rep Staring_at_the_Ceiling) + most remaining Psych858o
early/deep partials = ONE extract bug: the Psych858o sub-family is the
+1-SHIFTED dataflow body (whole player shifted +1; JT entries chain via out-
of-region stubs $1937/$194A — NOTE the play JT entry $1003→$194A→$1086 is a
plain JMP, NOT a phase wrapper). The $40 dual-effect GLOBAL half-rate parity
(canon $1019, INC/LDA/AND#1/STA at $14B1-9; odd frames run the slide path =
freq from held base + JMP $1619 BYPASSING the wave step; even frames run the
wave step) lives at $101A there — extract read base+0x19 = the member's D417
SHADOW → wrong slide_phase seed → every dual-effect voice's wave/arp advance
on the wrong parity (first chord tone 2 frames instead of 1, div @22). FIX:
`dataflow.locate` gains a `dual_parity` _CANON_STATE entry (signature-located)
→ `cfg.dual_parity_addr`; post-init capture + engine_model fallback use it.
Canon route pinned by identity compare = untouched. 59-member sweep: **+27
FULL, 0 regr** (32 FULL total incl. 5 prior), deep honest re-localizations for
the rest. DIAGNOSIS LESSONS: (1) memwatch at canon addrs on a shifted member
reads garbage — re-derive shift FIRST (bit again; round-11 warning); (2) the
reloc-normalized body diff vs canon bin (walk canon instrs, allow operand+delta
in [$1000,$1900)) is the fast way to find ALL code patches in a variant —
found "no code diffs" here, proving the divergence was DATA/seed, not code;
(3) "values right, schedule off-by-phase at song start" = suspect a GLOBAL
parity/counter leftover read at the wrong address.

## ✅ FAMILY-1 round 14 (2026-07-03): $D418 play-vector wrapper (+6, 4249/5401 = 78.7%) — commit efbf639
The D418-pos~0 early class (Bernds_Tune/Theme/Last_One/Snatch_of_Fury/
Funk-a-Duck/Kingdom — PVCF/Zyron/Signor): the PSID play vector points at
`LDA #imm / STA $D418 / JMP base+3` — a constant vol|mode assertion on EVERY
play() call before the canon body (imm $3F/$1F; the value = last-note-init
$D418 & $7F for Bernds but it's just a CONSTANT from the wrapper). The factory
found the canon JT at load and never looked at what the play vector executes.
Factory `_d418_play_wrapper` probe (shape + JMP target==base+3) → param
`master_vol_every_play`; composer prepends a `playd418` vector wrapper OUTSIDE the
play_repeat/play_phases dispatch. Census: exactly 6 carriers, all partial.
6/6 FULL, regression green. Class residue: Super_Seven = a CONDITIONAL
game-mute wrapper (LDA flag/BNE/JMP base+3, diverges on SUB 1); Scratch_It =
play JT entry points at $82F0 (relocated play body) — both separate causes.
METHOD: when flat pos-0 diverges with a shifted-by-one context, count the
missing register's writes per side; a constant-per-play surplus = look at the
PSID play VECTOR, not the play body.

## ✅ FAMILY-1 round 13 (2026-07-03): hard-restart-patch variant (+23, 4243/5401 = 78.6%) — commit 193bbbc
The V1/V2/V3-PWLO early sub-classes ((2,24)+(2,16)+(9,24)+(16,*) etc., rep
Headache orig $40 vs mine $4F) = ONE PLAYER VARIANT (The_Syndrom/Tragic_Error/
Gaston, 24 members, all partial, 0 FULL carriers = provably 0-regression):
canon player with two note-init wedges. (a) `JMP base+$262` at base+$257 skips
the PW step-base load ($175F stays 0 forever → step = phase nibble only) AND
the PW phase/direction reset (both persist across notes). (b) $1230 JSRs the
base+$25A wedge: parks SR at base+$40, feeds #$99 to sub_184B whose first STA
is retargeted at the hard-restart primer's ctrl-write OPCODE (base+$7FB SMC:
$99=STA → TEST written / $B9=LDA → skipped); the pulse-reset path's $1262
wedge then writes $B9 — net: the NEXT hard restart writes $D404=$08 iff the
last note-init instrument has the $04 no-pulse-reset flag. Initial toggle =
file-image opcode at $17FB (differs per member — Headache $B9, Atlantis $99).
IMPL: factory `_hardrestart_smc_variant_probe` (base-relative byte probe after canon/dataflow
build) → params `hardrestart_smc_variant`/`hardrestart_test_init`; composer gates fe_ni (hr_arm/
hr_disarm on a global `hrtest` var) + ev_n_hard TEST write; canon emit
byte-identical when off. **23/24 FULL** (Mountys_Escape re-localizes 24→24802
deep V1-freq-hi, separate cause); full regression green; mass-written; DB
refreshed. Artifacts: tmp/f1_hrpatch_members.json, f1_hrpatch_verify.jsonl.
METHOD: memwatch-on-write showed runtime $175F=0 vs file-image instr+6=$F0 +
taint_source proved $1901 static ⇒ the READ site must differ ⇒ dumped the
operand → found the JMP wedge. ⚠️ PROCESS: a timed-out `git stash && build &&
git stash pop` compound left the fix STASHED — the first regression+mass-write
ran on HEAD (bad builds written as FULL); caught via `git status` before
commit, re-done clean. Don't put stash pop behind a long build in one Bash call.

## 🔬 FAMILY-1 round 12 (2026-07-03): pos~8 class probed — writelog phase observer PARKED (0 FULL)
The V1flo pos~8 class (15, tmp/f1_v1flo8.json: Real_Hardcore/Domination_Bakery/
Compotune...) = MORE C18 wrappers, but py65 can't drive most (Real_Hardcore idles
silent under py65 — CIA-armed). Tried a C9 writelog-based observer
(`_observe_play_phases_writelog`, footprint-classifies per-IRQ chunks) — **PARKED,
NOT WIRED, do not re-wire as-is**: (a) per-IRQ straddle artifacts make chunk
footprints noisy — Domination's orig stream is clean P_R123 alternation with an
aperiodic 'F12,P,P' hiccup, and the period fit then locks a WRONG schedule (P_S:
rebuild played every other call, orig every call); (b) the phase rotation back to
call 1 is guessy (Real_Hardcore got F-first, truth P-first, regressed its div
11→0) — a P-placement self-check was added but ground truth needs a
straddle-robust chunker + glitch-tolerant period fit first. ALSO: even with
correct-looking schedules the class's flat_divs mostly DIDN'T move (@11-15) —
the schedule may not be the (only) blocker; the divergence is the FIRST play's
V1 note freq. All 15 re-verified with the fallback removed (honest rows).
NEXT for this class: build the robust chunker, then re-diagnose.

## ✅ FAMILY-1 round 11 (2026-07-03): DATAFLOW-route phase observer (+3, 4220/5401)
The V1flo pos~24 sub-class (17) root-caused = **C18 phase wrappers on the
RE-ASSEMBLED (dataflow) route** — the round-4/5 observer was canon-only, and its
PC offsets (base+$85/$1F9/$41C) don't hold for shifted code (Arrive's whole state
block is +1: $1717/$1719 not $1716/$1718 — the FIRST memwatch at canon addrs read
garbage, re-check the shift before trusting state samples on dataflow members!).
NEW `_observe_play_phases_writes` = OFFSET-BLIND classification by SID-write
footprint: P = writes the $D416 global-filter tail (unconditional in the canon
play body, unreachable from the frame entry/refresh), F<voices> = per-voice
writes without it (values advancing), R = identical values to the previous call,
S = none. Wired into `_build_via_dataflow`; same token output, zero composer
change. Arrive = CIA 6x `P_F123_F123_F123_F123_F123` (full play every 6th call —
without the knob the rebuild ticked 6x fast, notes 6x short). **+3 FULL
(Hang_Drum/Autumn_Memoir/Bad_Ass); massive re-localizations (Arrive 29→576k,
Pongish 29→789k, Player→526k, Inhale→767k = the deep freq tail is now their
blocker)**. FULL-side census: 0 dataflow FULLs observe a schedule (provably
0-regression). Full regression green. Residue of the 17: 4 still early
(Ucieczka @31 unchanged, Paint_Me_Blue @127, Turbulent_Times @67, Little_Beat
@71 — different causes), 10 deep. Artifacts: tmp/f1_v1flo24_verify.jsonl.

## ✅ FAMILY-1 round 10 (2026-07-02): guard + dtmp map rows (+3, 4217/5401) — early cluster CHARACTERIZED
(a) **GUARD ROW LANDED** — the round-9 objection was a MISREAD: re-RE of the play
body shows $1322 (guard check) runs for EVERY voice every frame ($10B3 freewheels
stopped voices into $11F9, same as our run_effects), init CLEARS $1786-8, and the
BEQ guards the DEC (no 0→$FF wrap) — so composer guard,x tracks in lockstep, no
priming needed (0ldsk00l's "$FF leftover" was a wnote idx-221 hi read + a stale-FULL
palimpsest; guard values are only 0-2). 4 guard-exposed FULLs hold. Bizarre 18→136.
(b) **DTMP ROWS** — the 20-member identical-signature class ([pos 38, V1flo, $D1,0])
= off-table idx 221/222 reading **$1724/$1725 = the GLOBAL dual-slide freq temp**
(written only by the $40 slide path $14CB/$14D3, "last dual voice's base+accum").
Composer fx_dual_run now shadows it (dtmpl/dtmph, global n=1 rows). Sidelined_2 +
Summers_Coming + Half_a_Year_Later FULL; 8 dtmp-exposed FULLs hold; full regression
green. **EARLY-CLUSTER TRUTH (census of the 168 flat_div<64): it is ~12 DISTINCT
sub-classes, NOT one mechanism** — staircase (otrk+guard, done: Bizarre/Trifle
re-localized deep), dtmp (done, +3; the other 17 of its 20 have SECOND blockers),
remaining: V1flo pos~24 (17: Arrive/Autumn_Memoir), V1flo pos~8 (15: Real_Hardcore
= the dataflow/wrapper Nones), pos~16 (9: Staring_at_the_Ceiling), V3flo (8:
Object_of_Art = the KNOWN wavepos-blocked class), V1flo pos~0 (8), V1pwl (8+4:
Headache [24,2,64,79]), D418 pos~0 (8: Super_Seven), V1sr (6), V2flo pos~56 (5:
Reggae_Me ORDER diff), V1fhi pos~0 (3: Speed_It_Up). Each = its own diagnosis
round (the knob-hypothesis holds: identical signatures within sub-class).
Artifacts: tmp/f1_early_sweep3.jsonl (fresh flat_div for all 168), f1_dtmp_*.

## ✅ FAMILY-1 round 9 (2026-07-02): otrk PHASE SCALARS landed (0 FULL yet — guard is the pair's other half)
USER-STEERED RESOLUTION of round 8 (transpose_cmds WITHDRAWN): the sonified track
counter = a **structure-synced staircase**, parametric over musical data — per-entry
offset = transpose-CHANGE count + `otrk_pad` (per-voice phase scalar, the leading
redundant-command count; measured {+1:146}/540 tracks, dual_phase precedent) with a
reset every `otrk_period` entries (the PHYSICAL orderlist length that _walk_track's
loop-unrolling obscured — offsets are periodic; Crystal = 2×28-entry passes).
Params `otrk_pad_sN_vN`/`otrk_period_sN_vN`; extract emits them ONLY when the model
reproduces the walked ground-truth `entry_offsets` exactly; inexact (piecewise
mid-track redundancy, e.g. 0ldsk00l) → `otrk_legacy_sN_vN` = keep the historical
entry+1 values (zero-regression by construction). RUNTIME: 3-byte track entries
[t+64, gid, off]; otrk,x = real state (seeded at fetch/trk2, INC at pat_end =
orig $182D, loop wrap handled by re-seed). Smoke: prior regressions (Decoy/Crystal,
Nasty_Track) FULL again; Bizarre 17→18 = blocked ONLY on the guard hi-byte now.
Early-sweep 168: 0 new FULL — **these reads consume the (lo=otrk, hi=guard) PAIR;
FULL yield awaits the GUARD RE** = the next round: the orig's guard DEC schedule for
stopped/never-inited voices ≠ our run_effects freewheel (0ldsk00l's V3 leftover
stays $FF ~1700 frames in the orig). InitVoice.guard + iguard priming plumbing is
IN but inert (to_usf doesn't emit it) until that RE. ⚠️ PALIMPSEST LESSON:
0ldsk00l_endtheme's 'full' row was STALE — partial at HEAD pre-otrk (verified in a
HEAD worktree); re-bucketed honestly (4215→4214). FULL-side censuses: otrk-idx
readers 5 (4 FULL + the stale one), guard-idx 5. Artifacts: tmp/f1_pad_final_smoke*,
f1_early_sweep*, f1_otrk_exposed*.

## ⏸️ FAMILY-1 round 8 (2026-07-02): otrk exactness — BLOCKED ON A USF SCHEMA DECISION (superseded by round 9)
Bizarre_Emotions (early-V1FLO rep, 73-member cluster) root-caused: idle-wave
off-table read idx 224/225 = (V2 $1727 otrk, V2 $1787 post-note guard). TWO parts:
(1) **guard map row** (0x1786,'guard',3) — op-for-op identical state, SAFE
(isolation-tested; FULL-side idx-223-225 census run). (2) **otrk exactness**: orig
$1726,x = byte offset of the entry's SECTOR byte in the orig track stream; a
transpose cmd byte precedes an entry OR NOT — **the placement is EDITOR-CHOSEN,
not derivable from transpose VALUES** (measured on 60 FULLs: 78 tracks match
emit-on-change, 102 have REDUNDANT re-assertions, 0 always-explicit). The old
`(trkpos>>1)+1` formula assumes always-explicit; emit-on-change fixes Bizarre
(17→136) but REGRESSED Decoy/Crystal + Surgeon/Nasty_Track (redundant-byte
FULLs). Neither derivation is universal ⇒ needs the explicit-cmd placement in
USF. **DECISION FOR USER** (schema-addition discipline — derivation exhausted
empirically): (a) `Orderlist.transpose_cmds` field (per-entry bool / sparse index
list — sequence-COMMAND placement, same class as repeats/voiceincs; my
recommendation), (b) params-string channel (no schema, but positional-data-in-
params smell + digit-CNAME grammar workaround), (c) accept-residue (Bizarre class
stays partial). CODE STASHED: `git stash` "otrk emit-on-change rework" — 3-byte
track entries [t+64, gid, off] + trk2 seeds otrk + pat_end INC (mirrors
$10FB/$182D/$10DF); revive + swap the off computation to the captured cmd flags
once ratified. Smoke list tmp/f1_otrk2_smoke.json (19: otrk-bank FULLs + reps).

## 🎯 FAMILY-1 round 7 (2026-07-02): POST-INIT filter-def decode (0 FULL, correctness; Ed class characterized)
The early-$D416 residue (Ed's Cliche_Beat @21 etc.): **init REWRITES the def
records** (stamps res/mode=$11 + init-cutoff=$02 over every def) — extract read
the file image. Fix: `_postinit_window` (py65 init run, subtune=start; None →
file image) feeds `_decode_filter_def`. Exposure census: **0 FULLs** init-rewrite
the window (provably 0-regression); 4 partials, all Ed's. All 4 re-localize
deeper but stay partial: **the Ed players RAMP the res nibble of every def
record DURING PLAY** ($11→$21→$31 every ~8-16 frames, $1723 follows on each ni)
= a res-sweep automation implemented by rewriting the def table — a REAL musical
feature (C10 chip-global automation class), needs representation + finding the
rewriting code (canon-route members, so it hides in a masked/wrapper region).
Deferred (4 members). Hardtechno @73 / Seaside_99 @197 = a different early-$D416
cause, undiagnosed. Artifacts: tmp/f1_edclass_verify.jsonl, f1_postinit_defs_*.

## 🎯 FAMILY-1 round 6 (2026-07-02): fdrec filter-def image layout (+17, 4215/5401 = 78.0%)
The $D416 ±1 deep cluster root-caused on Psycho_Tune = **C2 unbounded filter-def
WALK**: a def's repeat byte >5 (Psycho_Tune $1F) reloads the step index past the
6-entry size/dur arrays, and the engine's wrap check is EXACT-match `CMP #6` —
once past, INC walks the index upward FOREVER, reading sizes at def-table+4+idx /
durs at +10+idx across ADJACENT 16-byte def records (idx is 8-bit Y → window =
[filtdef, filtdef+266)). The composer's old 12-byte re-packed stride matched only
within-def overruns (idx 6-11). FIX (single universal form, no mode flag): extract
captures **17 typed def records** (272 B ≥ the window; byte-lossless round-trip:
res/mode/init/repeat/stop/6 sizes/6 durs), composer emits them DENSE in orig def#
order as `fdrec` with `fdstep=fdrec+4` / `fddur=fdrec+10` label views and
`fbase=16*def#` — every walked read byte-exact by construction. **+17 FULL** (28
D416 partials verified: 17 full / 11 other-cause); **FULL-side exposure census =
555 FULLs referencing a repeat>5 def, ALL 555 re-verified FULL, 0 regressions**
(their .sidfinity.sid rewritten — data layout changed). Ledger C2 consumer note
added. NB: first attempt stored the 10-byte window tail as a params string —
grammar rejects digit-leading CNAME values; the 17th typed record is the clean
form. Residue 11 of the 28: early-$D416 (Hardtechno @73, Seaside_99 @197,
Cliche_Beat @21) + other-reg re-localizations — different filter bugs, next.

## 🎯 FAMILY-1 round 5 (2026-07-02): R-REFRESH phase (+26, 4198/5401 = 77.7%)
The P_S class root-caused on Toccata: **the wrapper's non-play call is NOT silent —
it's a REGISTER REFRESH**: wrapper `LDA ctr/INC/AND #1` alternates play ($1003)
with the THIRD JT entry ($1006), whose target is the RE-AUTHORED all-off slot
($162F: `LDX #0/JSR $141C/INX/...` ×3) = the per-voice glide/write tail — re-emits
current freq/PW/ctrl (15 writes, no filter/ADSR) at 100Hz without ticking. The
observer misread it as S (reaches neither base+$85 nor base+$1F9). FIX: observer
classifies base+$41C hits as `R<voices>`; composer R token = `ldx #v/jsr fx_glide`
per voice (fx_glide IS the $141C analog; entry-point mirror = exact by
construction). **+26 FULL, 0 regressions** (whole 64-member wrapper list re-run;
the 5 round-4 FULLs held). Residue 33: early-<64 22 (mostly the observe-None /
dataflow sub-class — re-assembled players w/ shifted bodies, e.g. Speed_It_Up =
plain JSR×4 repeat + a different early bug; wrapper obs not wired on the dataflow
route) · deep ≥4k 7 (knob works; separate causes: Tekkno_Power 88k, Big_City 333k)
· close-tail 2 (Compotune_1/2 — pure length mismatch at cutoff, tail ~1.2-1.4k >
scaled close_tol; the phase period stretches the cutoff straddle — close_tol
follow-up, strict policy respected). Artifacts: tmp/f1_refresh_verify.jsonl.

## 🎯 FAMILY-1 round 4 (2026-07-02): PLAY-PHASE wrapper (+5, 4172/5401) — banked 129812e
Fuck_Off (the round-3 undiagnosed rep) cracked = **PLAY-PHASE WRAPPER**: the play
vector cycles full-play / effects-only calls (the DMC slow-tempo / multispeed-
effects editing trick, e.g. 'PFFF'). Factory `_observe_play_phases` (C9 measure-
don't-parse: run init+12 plays under py65, classify each call by the entry it
reaches — P=base+$85 full play / F<voices>=base+$1F9 per-voice frame entry /
S=neither; minimal period → `play_phases='P_F123_F123_F123'`). Composer emits a
phasectr dispatcher (P→playframe / F→voice_fx stub w/ otrk re-derivation / S→rts);
gate requires ≥2 tokens incl. 'P'. **+5 FULL** (Fuck_Off/Words/Beverly_Hills_Cop/
Music_of_Wind_intro/Image). NB the code was accidentally swept into bfa1604 (the
parallel basic_program session's commit); banking commit = 129812e. FULL-side
census 4167: 1 hit (Surgeon/0104 `S_F123`x5 no-P → gate rejects, build proven
byte-identical; re-verified FULL, stored build refreshed). **Wrapper residue 59
(of the 64-member list tmp/f1_fxwrap_members.json): P_S_S_S 24 / P_S 14 /
observe-None 10 / P_F* 11; 55 still diverge EARLY (<64) WITH the knob** —
next: diagnose a P_S rep (Toccata @pos11) — suspect the 'S' calls aren't truly
silent (tick without writes shifting later timing?) or CIA bucketing. P_F123
members diverging DEEP (Tekkno_Power 88k, Mac 75k, Kick_Up 137k) = knob works,
separate deep residue. Artifacts: tmp/f1_fxwrap_verify.jsonl, f1_phases_census.jsonl.

## 🎯 FAMILY-1 EARLY-CLUSTER round 3 (2026-07-02): wave-chain 8-bit WRAP (+3, 4167)
CANON-route rep Attah_2 root-caused = **ledger C11's wave-walk instance**: the
engine's wave position is 8-BIT (INC wraps $FF→$00) but `_resolve_wave_chain`
walked LINEARLY past index 255 into the extended window → bogus programs for
off-table wave pointers near the top (Attah_2 inst 22 ws=$FF: true program
[(3,+17),(41,+0)]loop — one step then WRAP; old walk gave [3,7,7,..]). Fixed
(mod-256 walk, reads bounded to the 256-byte window; in-table slice path
untouched). SAFETY: used-instrument census 4155/4164 FULLs unchanged; the 9
changed re-verified all-FULL (unreached tails). Transfer: 91 canon-early
re-verified → **+3 FULL (Attah_2/Escape_from_Tropic/Winters_Theme), 4167/5401**,
mass-written+DB. **SURVIVING canon-early cluster = 88 (V1_FLO<64 43) — a
DIFFERENT shared cause, still undiagnosed**: NOT bucketing skew (per-IRQ also
diverges: Fuck_Off pm=29, Short_Track pm=0, Bizarre_Emotions pm=32); values
heterogeneous (o=$1E m=$87 / o=$DF m=$00 / o=$47 m=$16). First finding on
Fuck_Off: orig play1 = ALL-voice HR fetch + $D417=$02 (a nonzero res write on
play1!); rebuild's first-note sequence differs around note-init. NEXT: full
state-provenance pass (the Hyper recipe) on Fuck_Off + Short_Track; also note
Klepkomania diverges on SUB 3 (subtune-dependent — check per-subtune leftover
priming). Artifacts: tmp/f1_canon_early_verify.jsonl (fresh flat_div),
tmp/f1_wavewrap_census2.jsonl.

## 🎯 FAMILY-1 EARLY-CLUSTER round 2 (2026-07-02): POST-INIT capture (commit after dc46d0e)
Second dataflow-path mechanism fixed: **post-init leftover capture**. The $D417
early cluster (Scalework/Blue_Magic/Depression, o=$00 m=$07 @pos10) root cause =
the extract primes leftovers (d417 shadow / idle notes / masks / dual_phase) from
the FILE IMAGE — valid for canon (init never touches them) but a RE-ASSEMBLED
init may clear them (Scalework clears its $1017 shadow). Fix: factory dataflow
path runs the member's init in py65 (`_post_init_ram`) → `cfg.post_init_state`
(extract-only, never USF); extract prefers it. SAFETY CENSUS FIRST (the standing
discipline): 267/267 dataflow FULLs post-init==file (zero exposure); 11 partials
differ → re-verified: 0 new FULLs at 1.1x but honest re-localization (Scalework
10→128k, Depression 10→215k — the early mechanism fixed, next blockers deep;
C5). Remaining early-cluster residue: 98_Mix (reg7 @7) + Noising_Funk (reg0
@13) + Pimpin_Power/Viiskyt (@0-1) = other early causes, per-member trace next;
plus the CANON-route early divergers (~22/40 sample) still undiagnosed.

## 🎯 FAMILY-1 EARLY-CLUSTER ATTACK (2026-07-02, cont.): 4164 FULL — dataflow knob probes (commit dc46d0e)
The early-<64 cluster (222 w/ current flat_div) root-caused on Hyper (pos 2, PW
$00-vs-$50): **re-assembled members recovered via `_build_via_dataflow` never get
the canon sub-build KNOB probes** (canon-site-relative, e.g. $1180 rest dispatch)
→ built with default knobs = wrong MECHANISM presenting as an early divergence.
Hyper = the rest-skip variant ($7E rest handler JMPs to the WAVE STEP, skipping
gate-logic+pulse on the fetch frame; composer knob `rest_effects='skip'` existed,
never set). FIX: `factory._dataflow_knob_probes` — probe by OPCODE SHAPE
(rest handler `LDA,x/STA,x/INC,x/[JSR]/JMP`; classify JMP target: wave-step
`BD..29 01 D0` → skip / effects `BD..F0..DE` → run). Probe census FIRST: 29
partials flip, **0 FULLs flip** (no regression exposure — census the FULL-side
flip set before landing any knob probe). +5 FULL; Hyper re-localized pos 2→296k.
Ledger C13 corollary. METHOD (validated): effect_chain_profiler PC-attribution +
`assemble(return_labels=True)` + `--memwatch-on-write D404 <composer-state>` =
the state-provenance recipe that cracked it (gatemask=$FE + stepped pulse pre-note
in the rebuild vs zeros in the orig). NEXT for the early cluster: (a) port the
REMAINING canon probes to shape-probes (D418 helper, all-off mask, hard-restart,
filter-mode) — ~10 of the 29 still diverge early on those (reg23 $D417 @pos10,
ctrl variants); (b) the canon-route early divergers (~22/40 of the cluster sample)
= a DIFFERENT shared cause, undiagnosed (reps: Attah_2 pos21 o=$0C m=$F6,
Reggae_Me pos62 ORDER diff). Census artifacts: tmp/f1_probe_census.jsonl,
tmp/f1_skip_verify.jsonl.

## 🔄 FAMILY-1 PIVOT (2026-07-02): 4159/5401 (77.0%) — 1.1x ratified, drift +18, fresh census
Pivoted back to family-1. (1) **1.1x RATIFIED as THE verify standard** (user: the
rebuild must match cross-songlength/loop behaviour ≥10% past songlength) — the 32
song_exact (1.0x) members REVERTED to partial (rows flagged song_exact_rejected;
files deleted; fixing them = match the loop-wrap carried modulation phase).
(2) **Drift re-verify of all 1,260 non-FULL** with current code: +18 FULL
(17 partial + 1 error), mass-written, DB refreshed, jsonl merged current (every
partial has a current-code flat_div). (3) **divergence_census wired for dmc_v4** +
cluster_partials now keys on flat_div (NOT the phantom-D418 first_diff) with
position buckets. FRESH CENSUS (1,011 partials): DEEP ≥4k freq ~505 (For_Insider
class, the hard tail) · **EARLY <64 = ~158 (V1 FLO 105 + V2 FLO 20 + V3 FLO 18 +
V1 PWLO 15)** — the family-4-leadin analog, one-shared-mechanism candidates (e.g.
Hyper pos=2 PW $00-vs-$50 = unprimed idle PW leftover; Attah_2 pos=21 wrong idle
freq; Reggae_Me pos=62 orig==mine value ⇒ an ORDER/extra-write diff, reg differs)
· MID 64-512 ~72 · **$D416 cutoff-hi ≥4k = 16 with ±1 values ($99 vs $98)** = a
single filter-accum off-by-one candidate. Unsup: sector_decode 81 / no_jumptable
62 (C13 probe pending) / player_code_mismatch 23 / wave_marker_chain 13 /
nonstandard_instr_base 12 / loop_site 11. NEXT (approved plan step 3+): early-<64
cluster attack (leadin idle freq/PW priming) + taint_source STATIC/DYNAMIC pass
on the off-table subset + C13 no_jumptable probe + C2 one-shot for 3 wave-pool
errors. Artifacts: tmp/f1_reverify.jsonl, tmp/f1_drift_recovered.json.

## 🔬 V5 FAMILY-4 — SESSION 2026-07-01: verdict+unblock fixes + partial triage
Baseline `tmp/dmc_family4_full2.jsonl`: 26 full / 336 partial / 156 unsupported /
168 error. Worked residue-triage dependency order (verdict→unblock→triage). THREE
committed fixes (f6b613f / ea087b2 / 1b8f5f2), **full regression GREEN (0 regressed
all 7 families)**:
1. **PER-IRQ verdict for family-4** (batch + verify_v5). family-4 is VBLANK but its
   SHORT orig-init fits init+play1 in siddump frame 0 while our longer universal-
   reset init pushes play1 to frame 1 → flat capture buckets play streams 1 frame
   apart (Trap C via init-length). Force `writelog_per_irq_capture`. VERDICT-NEUTRAL
   (26 FULL stay, partials stay) but makes flat_div RELIABLE for clustering.
2. **`}` empty-filter-block fix** (`src/usf/writer.py`, SHARED): all-zero InitFilter
   emitted `filter {  }` (grammar-rejected) → 39 UsfParseErrors. Omit empty block.
3. **$EF/$F0 sector-cmd decode** (extract→to_usf→from_usf→grammar→parser→composer):
   125 "unknown sector cmd" errors. $EF→frqbias (composer already reads it),
   $F0→vibwidth+byte-sync ($F0 wave/freq reload DEFERRED). All 125 now BUILD.
Errors 168→~1 (moved to partial). FULL count ~unchanged (~26-30; fixes were
unblock-builds, not new FULLs — Black_Sun etc from the `}` fix).
**RELIABLE PARTIAL TRIAGE (per-IRQ flat_div, `tmp/f4_periqr_measure.jsonl`):** the
336 partials are REAL (0 flip to FULL under per-IRQ). Split:
- **EARLY <64 = 239 (71%) = THE LEADIN (dominant next blocker).** play() ($1095)
  uses **$1016 as a 2-phase toggle** (DEC;BMI → MAIN vs TICK; TICK decs durctr).
  $1016 is a FILE-IMAGE LEFTOVER (init doesn't clear it) → sets the leadin phase =
  # idle plays before 1st note-on. Bach($1016=0)→play2=composer default; 2_Hours
  ($1016=1)→play3, composer 1 play short. BUT $1016∈{0,1} doesn't predict pass
  (15 FULLs have $1016=1, all NONZERO idle; partials have idle=[0,0,N]). **Seeding
  LEFT_SPDCTR=mem[base+$16] did NOT fix it** (regr-safe, 0 recoveries — the
  composer's spdctr counter ≠ the orig $1016 DEC/BMI/reset-to-1 toggle; only
  represents phase 0/1). **⇒ NEXT = STRICT MATCH (user policy 2026-07-01: every
  SID always gets the strict write-stream verdict; ledger C15 "audio-equivalence"
  REMOVED — parked in the_move-1_plan.md, Move-1-era-only): REPRODUCE the
  $1016 2-phase EXACTLY in the composer** (family4-gated DEC/BMI/reset-to-1
  toggle seeded from mem[base+$16] — a NEW counter shaped like the orig's; the
  LEFT_SPDCTR=mem[base+$16] attempt FAILED because the composer's reload-to-speed
  spdctr ≠ the orig toggle). Secondary: why trichotomy passes Plasmostyle not
  2_Hours (both $1016=1; discriminator idle-note-0 → suspect the hard-restart
  SR=0 on the extra idle play). $16 dist over partials: {0:111,1:222,2:2,255:1}.
- **DEEP ≥64 = 97 = off-table freq/filter tail** (FLO 71 + FC_HI 15) = known-hard
  C2/C11 off-table pulse/filter sweep, overlaps the 71 overflow. Architectural-last.
Artifacts: tmp/f4_periqr_measure.jsonl, f4_partials_members.json, f4_full_members.json,
f4_rerun_fixes.jsonl (full re-run w/ all fixes).

## 🔬 V5 FAMILY-4 (686 SIDs, Jupiter41) — Phase A RE DONE (2026-06-29)

Started the family-4 migration (`pipelines/dmc/family4/`: disassembly.s seed +
RE_NOTES.md). **KEY FINDING (corrected mid-RE): family-4 = family-3's V5 DATA
FORMAT, RELOCATED, with a DIFFERENT PLAYER** — NOT a from-scratch engine.
- SHARED with family-3: track format ($FF loop/$FE stop/$FD$FC transpose),
  sector command map (~1:1: $F1 srr/$F2 adr/$F3 vol/$F4-5 gate/$F6-7 fade/$F8 frq/
  $F9 flt/$FA slide/$FB glide/$FC snd/$FD dur/$FE gate), 8-byte instrument record.
- DIFFERENT (the ~0.31 Jaccard = player code): 3-entry jump table (init $1040/
  play $1095/3rd $10D3); 2-phase `$1016` timing (DEC/BMI alternates MAIN $1373
  vs TICK $10E1); `$D416`-ONLY filter ($1019+$1853, no $D415); zero-page $FA/$FB;
  + 2 new sector cmds $EF/$F0 (wave/vib). Table bases relocated: song $1A40,
  sector-ptr $2209/$224B, instr $228D, freq $1779, wave/pulse prog $23A3/$23BC.
- The V5 factory ALREADY detects it (`layout='family4'`, rejects family4_branch).
- **Phase B/C = the family-2 playbook**: factory dispatch + dataflow relocated
  bases → reuse the V5 extract → family-4 composer variant (2-phase timing +
  $D416 filter) → carve a Jupiter41 reference for masked dispatch → wide batch.
- **Phase A now COMPLETE (commit 824cc9a):** full effect chain mapped (filter
  prog $23D5/$242C, pulse $23A3/$23BC, glide, wave $2325/$2364 $90-loop); FREQ
  TABLES lo $1719 / hi $1779; SID WRITE ORDER per voice = D400 D401 D402 D403
  D404 (then D416 once); $EF = per-voice freq-lo bias ($1842,x); timing CONFIRMED
  VBLANK (speed bit 0, SID writes every frame — verify_dmc per-frame applies, no
  CIA). CENSUS: 635/686 uniform family4 (play+$95), 36 actually family-3-layout
  (build via existing path), 15 rejected; 577@$1000 + ~58 relocated.
- **Phase B DONE (commit 88f18bc):** factory dispatch + extract working.
  `DMCV5Config.family4` flag + `FAMILY4_SITES` (12 operand PCs, verified 12/12);
  `_family4_config` (base=load; sites+delta). The V5 extract REUSES the shared
  data decode — Jupiter41 extracts clean + the FULL pipeline runs end-to-end.
  family-3 V5 unaffected (only layout='family4' hits the new path); full
  regression GREEN. 32/34 sample build.
- **Phase C STARTED (commit 8b1f3b1): foundation done.** Threaded the `family4`
  flag + player leftovers through extract→to_usf params→from_usf→model
  (round-trips; family-3 unaffected, 7/7 FULL). Captured: `f4_idle_notes`
  ($1012-$1014 curnote, NOT init-cleared = the leadin freq; Jupiter41=[43,36,29],
  V1=43→$0C8F✓), `f4_filtmode` ($1018→$D418 mode; =$30✓). RE_NOTES has the
  3-issue work list. **Remaining = the composer knobs (gate on m.family4):**
  C-1 leadin curnote (prime $1012 idle from f4_idle_notes — the FIRST divergence,
  V5 lo_notes analog); C-2 FILTER ($D416-only 8-bit cutoff $1019+$1853 + $D418
  mode + $101A mvol-fade; rebuild emits ~27k extra $D415); C-3 2-phase $1016 note
  TIMING. Then verify_dmc + carve Jupiter41 ref + wide batch ~635 → DMC ~71%→~76%.
  - **C-1 DONE (commit cc63144):** feed f4_idle_notes to the composer's initnotes
    (it already primes curnote from there). Jupiter41 non-filter match 25→60.
  - **C-3 PARTIAL (commit caabfd5):** speed=1 extracts right (= 2-phase tick rate,
    no rate knob needed). lo_spdctr was reading $1013 = V2 CURNOTE (garbage
    36-frame delay) → zeroed. REMAINING C-3 = leadin LENGTH: orig 1st note gates
    ~frame 2 (write ~60), rebuild gates ~write 24 (too early); family-4 init seeds
    durctr $17E5=2, composer seeds 1 → composer knob: seed durctr=2 for family-4
    (leadin is sensitive — verify, don't over/undershoot).
  - **C-2 FILTER not started** (the ~27k extra $D415 + $D418 mode + $D416-only
    8-bit cutoff). Jupiter41 filter is nearly static ($D416=$2E, $D418=$3F,
    $D415 never written). All family-3 V5 unaffected (knobs gated on m.family4;
    6/6 FULL sanity each step).
  - **⚠️ C-3 REAL BLOCKER (commit f2780d4): the 2-phase splits the WRITE ORDER.**
    Sweeping lo_spdctr maxes the non-filter match at ~63 then FORKS on ORDER (not
    values/leadin): family-4 BATCHES the note-on pass (SR/AD/CTRL for fetching
    voices) THEN the wave-step pass (freq/PW/ctrl) — the 2-phase $1016 separates
    note-on from the $1654 wave-step. The family-3 composer INTERLEAVES per-voice
    (V1 note-init+wave-step, V2 …). So FULL needs the composer to emit family-4's
    play() STRUCTURE (note-on pass over all voices, then wave-step pass), gated on
    m.family4 — a real composer restructuring, NOT a knob. PREREQ: finish tracing
    the exact $1095/$10E1/$1373/$147B/$1654/$10D3 call graph + per-frame write
    order. This is THE focused next task for family-4 FULL. (Lesson: the lo_spdctr
    sweep was the diagnostic that proved it — the write-order forks regardless of
    leadin, so it's structural.)
  - **✅ C16 CONSULT RESOLVED THE FRAMING (commits f33dde5/2acfbec/39ae337): it's
    KNOBS, not a rewrite.** The ledger consult (C16: parametrize emission order;
    precedent FC nextvoice_write_order) corrected my premature "wholesale rewrite"
    call. Traced the exact order + landed 3 family-4-gated knobs (family-3 7/7 FULL
    each): (1) note-on FRQ-skip (family-4 note-on = SR/AD/CTRL only, no FREQ=$0;
    60→73); (2) pulse lo/hi swap in FAMILY4_SITES (73→86); (3) leadin durctr=2
    (init seeds $17E5=2; principled w/ lo_spdctr=0, no magic; match 86). Jupiter41
    non-filter match 60→86/13824 — **NOT yet FULL**; next divergence (write 86) = a
    per-note DURATION/effect (orig holds freq $27DF gate-on, rebuild gate-offs early
    $0451 → suspect the family-4 $FE/$FC sector duration decode: note $3C followed
    by $FE may be a 2-byte [note][param] vs family-3's 1-byte). Then C-2 filter.
    Path PROVEN (each knob advances the match). METHOD LESSON: CONSULT the ledger
    BEFORE scoping a fix as "big/next-session".
  - **✅ WAVE-SPEED counter — the steady-vs-sweep root cause (commit 5617d66,
    match 86→92, V1 byte-exact).** write 86 was NOT a duration bug: the orig HOLDS
    each note 6 frames; the rebuild SWEPT every frame. family-4's wave-step ($1654)
    has a per-instrument wave-SPEED counter ($1845/$1848 gating the $17FD advance),
    seeded from **instrument byte 6 ($2293) >> 4** (=5 for inst 8). family-3 lacks
    it. 3 family-4-gated knobs (family-3 9/9 FULL): (1) wave-speed counter
    (wavespd/wavespc; ws_adv holds N frames/step; speed 0 = family-3 unchanged);
    (2) note-on no-pre-advance (family-4 note-on does no wave step → don't inc
    wavepos); (3) vib-disable (byte 6 = wave speed not vib_speed; $50 was read as a
    huge vib_speed → +$21 jitter). NEXT (write 92): V2 = inst 8 as a DRUM (noise
    attack DD00/81 + linear downward pitch slide 0D00→0200); rebuild holds the
    transient 1 frame too long (no-pre-advance over-holds V2's 1-frame transient).
    Needs the hard-restart FIRST-step timing + the drum slide mechanism. Then V3,
    then C-2 filter. METHOD: diagnose freq from the FLAT per-voice (freq,ctl) seq
    (Trap-C-free) — the steady-vs-sweep + the ×2-vs-×1 transient jump straight out.
  - **✅✅ NON-FILTER STREAM BYTE-EXACT (match 86 → 13793/13824, ~100%; commits
    1343366/35ae98d/6c2bc31/6ed3ae2; family-3 FULL throughout).** Chain of fam-4
    knobs: (1) speed-gated note-init advance (92→161; note-init first-step must use
    the SAME speed-gated advance as ws_adv, else a speed-0 drum emits its 1st wave
    value twice — V2's DD00); (2) melodic wave-step CARRY propagation (161→**4651**;
    orig's $1688 `adc $1842` has NO clc → the carry from adc(wavefreq+curnote) lands
    in freqlo, +1 when sum>=256; added `adc frqbias,x` to ws_mel+ni_w_mel — MASSIVE
    unlock); (3) 8-bit pulse counter (4651→5837; family-4 counts with 8-bit $1830 vs
    $23BC[pos+1], not family-3's 16-bit — V3 PWM never swept); (4) vol-override
    AD=$00 (5837→**13793**; vol-override note-on $1352 forces AD=$00, SR carries the
    vol level — unlocked the ENTIRE rest). The MUSICAL CONTENT (notes/waves/pulse/
    drums/ADSR/vol) is byte-exact. **FINAL PIECE = C-2 filter** (Jupiter41 still
    `partial`): $D416-only = $1019(sweep, prog $23D5/$242C) + $1853(base); $D415=$00
    init-only; $D417=$54 res; **$F8 is the FILTER-BASE cmd for fam-4 (sets $1853),
    NOT 'frq'**. filtmode $D418=$30 done (cc8cb46, f4_filtmode). Filter STRUCTURE
    done (95b5ddc: filtbase var + $F8→filtbase + $D416=fchi+filtbase + 8-bit ctr +
    no per-frame $D415; filtbase works, MVOL matches). **FILTER FULLY UNDERSTOOD via
    orig memwatch (e8a135d): for Jupiter41 it's STATIC, NOT swept — $1019=$5E is the
    FILE-IMAGE byte at $1019 (V3 idle/inst0 → filter program never runs; $1803=0,
    add=0 → $1019 frozen); $1853=0→$D0 ($F8); $D416=$1019+$1853 = $5E→$2E. The sweep
    machinery was the wrong model for the first window.** REBUILD BUG: composer's V3
    runs a filter PROGRAM during idle (note-on filter-init from inst byte4 + sweep →
    fchi=$D0), orig doesn't. FIX (clear): (1) fchi init = file-image $1019 (mem[base+
    $19], an f4 param) not lo_fchi; (2) don't run V3's filter program during idle for
    family-4. Then verify FULL song (later real V3 filter notes DO sweep — the ~20
    distinct $D416 values are out of the first-divergence window).
- Members: `tmp/v5_family4_members.json`. Commits 1fd69df/02baf25/824cc9a/88f18bc.

## ✅ V5 (family-3/5): 1088/1495 FULL (72.8%, 2026-06-29) — glide-wrap +27, idle-filter +20

Session 2026-06-29 V5 total: 1041 → 1088 (+47), all 0-regression.
**+20 idle/default FILTER sweep (commit 7ec73c0):** the `default_filter` capture in
`to_usf` had a stale `m.filter[0] != (0,0)` gate that dropped idle filter programs
starting with a (0,0) HOLD before the sweep (Cooksey: hold ~20 frames then ramp
$1415/frame) — composer held the priming cutoff forever where the orig sweeps (the
FL_LO partial cluster). Dropped the gate (the `any rate != 0` check already excludes
a pure hold); SAME fix the `default_pulse` twin already had (round-8). Full FILTER
cluster (FL_LO 15 + FL_HI/CTL 5) → FULL; full 1495 batch 0-regression.
PROCESS WIN: the `default_pulse` code was the reference — when two twin features
(pulse/filter idle sweep) exist, a fix to one should be mirrored to the other.

Pivoted to V5 after family-2 froze on the hard freq tail. V5 is a MATURE engine
(composer_v5 + factory + extract + batch, ~1041 FULL pre-session), NOT early-stage.
**+27 via the glide-wrap fix (commit 65ac05f, ledger [[C11]]):** `note_out_of_range`
(38) was a STALE `>119` reject in `to_usf._note_byte` predating 2-digit-octave
off-table pitches. V5 glide/slide targets ($FB/$FA) are stored TRANSPOSE-RELATIVE
(raw $FE = "transpose−2"); the player does `(target+transpose)&$FF`, usually
wrapping back IN-TABLE. The off-table pitch ($FE→"D-21") round-trips losslessly via
`_pitch`/`_pitch_str_num`, and `from_usf` re-emits `&$FF` so the byte is preserved.
27/38 → FULL, 9 partial, 2 other-refusal; **0 regressions** (the reject only ever
fired for these members; existing FULLs never hit n>119). to_usf.py is V5-only so
other families untouched.

**V5 residue (1495 total): partial 176, unsupported 212, error 39.** Characterized:
- **player_code_mismatch 113 = MOSTLY GENUINE VARIANTS** (NOT an over-strict gate
  like family-2 — a bypass gave only ~2 FULL; the rest expose real divergences).
  Biggest sub-cluster: **$10A1 master-vol FADE variant (49)** — decoded the fade
  block ($111B:$111C accumulator→$D418, $1118 up / $1119 down rate); composer
  already models fade (sector cmds $F6/$F7) but these also have a DIFFERENT init
  skeleton ($1634), so they need real per-variant RE (init/orderlist + fade-source).
  Others: $1385 (16, wave_slice), $16C7 (16, partials+trailing_sector_cmds).
- **partial 176 — CHARACTERIZED (2026-06-29, reliable flat_div via the now-
  flat_div-enabled `dmc_v5_family_batch`):** FREQ 118 (67%, V2_FHI/V1_FHI/V1_FLO…)
  = the hard off-table freq tail (same C11 class as family-2/V4, NOT a clean
  lever). FILTER 26 (15%, FL_LO 20) / ADSR 12 / PULSE 10 / CTRL 1.
  **FILTER cluster ROOT-CAUSED = the IDLE/DEFAULT filter sweep is not captured.**
  Traced Cooksey_2009: orig V3 filter cutoff SWEEPS (idle program at filterpos=0
  auto-advances after a ~20-frame hold, ramps $1415/frame); rebuild holds the
  initial cutoff (B600) FOREVER. The filter table extracts correctly, but
  `write_v5_usf` re-packs the filter table FROM PER-INSTRUMENT programs only
  (to_usf docstring: "FILTER sweeps are residue... needs a `filter_sweep` field"),
  and Cooksey's sweep is the IDLE default (ALL instruments filter_ptr=0, nothing
  points into it) → LOST in the roundtrip. This is the V5 analog of V4's
  `default_filter`. The fix = capture the idle filter program (filterpos-0 sweep)
  as a USF default_filter/filter_sweep; the composer already RUNS filterpos-0
  every frame, so it just needs the data. ~20 FL_LO members. PULSE 10 is likely
  the analogous idle-pulse-program gap (unverified). Memwatch proof: rebuild
  filtctr_lo reaches the count $14 but filterpos never advances because the
  roundtripped filter table is the null+`$90` default, not the real sweep.
  **ADSR 12 (all AD+SR) = DISTINCT, harder.** First_Inspirations: V2 note-init
  orig AD=$41/SR=$41 vs rebuild AD=$A9/SR=$C3 — NEITHER matches the extracted
  instrument (all insts AD=$00), so it's the runtime ADSR computation: instrument
  AD/SR + VOL-override ($F3 → $17E7,x sustain) + ADR/SRR live-set ($F2/$F1) +
  HARD-RESTART (sector lookahead: durctr==1 → SR=0, durctr==2 → restart;
  disassembly.s:145). Composer's hard-restart/VOL-override interplay diverges. Not
  a quick fix.
  **PULSE 10 = related to the re-pack but per-instrument + heterogeneous.** Dance:
  orig V1 PW SWEEPS (FF FE FD…) but rebuild HOLDS 0 — a per-instrument pulse
  program (pulse_ptr=1) not reproducing. The pulse table is ALSO re-packed in the
  roundtrip (pulse_ptr shifts 1→3,5→7 from the `$90` terminals); some members
  sweep-vs-hold, others have the opposite (orig=0/reb=nonzero). Mixed.
  **VERDICT: the 4 clusters are DISTINCT causes, NOT one fix.** FILTER idle-sweep
  is the cleanest (~20). PULSE shares the table re-pack mechanism but is per-inst +
  messy. ADSR + FREQ are separate/hard. Recommended order: FILTER default_filter
  capture first.
- cia_multispeed 39, no_jumptable 14, trailing_sector_cmds 13, wave/pulse overflow.
NB the Jun-21 `tmp/dmc_v5_full_results.jsonl` predates the Jun-25 CIA port — re-run
with current code before trusting its non-FULL buckets (palimpsest).

## ✅ FAMILY-2: 2294/2889 FULL (79.4%, 2026-06-29) — build+verify-as-judge round (+78 session)

Session 2026-06-29 took family-2 2216 → 2294 (+78). The wins were all the SAME
principle — **the write stream judges, not code identity** (CORE TENET) — applied
to dispatch/detection, not new effects:
- **build+verify-gate (aaa914c, +21):** replaced the family-2 player-code
  hard-reject (`player_code_mismatch_f2`) with a `break` + build+verify. Play-body
  diffs are write-stream-benign; operands extract from canonical sites regardless.
- **all-off/sfx mask (3128dd4, +5):** `_F2_DATA_MASK` masks $162F-instr_base
  (all-off/sfx never execute during play()), matching canon's `_MASKED_RANGES`.
- **re-verify palimpsest (+40):** re-ran non-FULL with current code (0 regressions).
- **init-shift dispatch (2a07a7e, +12) — ledger [[C13]]:** `_jt_layout` now accepts
  `play+$85` with `init∈[+$30,+$40]` as family2. These variants keep the canonical
  play body at +$85 but shift the init header a few bytes (+$38..$3A vs +$37); we
  emit our own init so the shift is irrelevant. Validated 12 FULL / 2 partial /
  0 false-accept. Mass-written + DB-refreshed.

**BUILD-FAIL RESIDUE FULLY CHARACTERIZED (50 unsupported + 12 error + 533 partial).**
Don't re-census — these are DEEP per-variant, low per-hour yield (the +12 was the
last cheap structural win):
- **partials 533** = 76% FREQ (lo+hi 406) — the known-hard structured freq tail
  (per-cause, no single lever; same as family-1). CTRL 55 / SR 33 likely
  note-contaminated. FL_HI 15 = clean global. THIS is the FULL bottleneck, not
  the build-fails (per [[C5]]).
  - **FREQ TAIL ROOT-CAUSED (2026-06-29) = OFF-TABLE DYNAMIC READS (hard C11):**
    re-verified all 533 with current code (0 free recoveries — palimpsest
    flat_div was STALE; Live's "pos 27" was really pos 94871=71% deep). Off-table
    classifier: **429/533 (80%) diverge on an off-table read.** Pinned on
    Death_Comes (V2 first note arp 121 → $1720 = the FILTER CLAIM FLAG): composer
    used pre-init file-image $03, engine reads post-init $00. TWO clean fixes
    REJECTED (0-regr rule): earliest-value-instead-of-file-image +7/−2 (Fear deep
    read = file image); map $1720→fclaim +0/−1 (fclaim timing ≠ orig). Only clean
    lever = earliest-as-VERIFY-FALLBACK (+7, deferred) or EVENT-DRIVEN capture
    (the right fix, unbuilt). Accepted as the hard residue → pivoted to V5. Detail
    in ledger [[C11]] HARD BOUNDARY (dynamic work-RAM). Tooling left in tmp/:
    f2_classify_divergence.py, f2_partials_reverify.jsonl, f2_offtable_partials.json.
- **sector_decode 29** = two sub-causes: (a) garbage secp over-run (track byte
  indexes an empty secp slot → sec_addr=$0000/out-of-range; secp tables are tiny,
  e.g. 7 entries, so index≥N reads the adjacent hi-table); (b) valid sec_addr,
  no $FF terminator — the LAST sector runs into $FE filler (2_Grenadiere sec6
  $1A99); orig plays 82s with all voices active = the song LOOPS on all-voices-
  stop, so "idle-on-filler" is the WRONG model — needs track-level loop/restart RE.
- **no_jumptable 14 (tail)** = play+$86 (whole-table +1 shift) / play+$85 far-init
  ($+18,$+A50 — dispatch as family2 → only PARTIAL, not worth loosening the window)
  / high-offset relocated JTs ($C20/$BC0) / garbage.
- **errors 12** = all in `_walk_track`: PSID `songs` over-reports; subtune 0 fine
  but later subtunes read a garbage tunetab row (James_Pond: songs=3 but tunetab
  has 1 row; sub1 is a byte-identical ALIAS of sub0, sub2 genuinely differs yet
  isn't in the 8-byte-stride table → this member's subtune-select mechanism
  differs from canonical tunetab+sub*8). Needs per-member subtune-dispatch RE.

## 💡 OFF-TABLE FLOOR IS SOLVABLE (2026-06-26) — NOT a fundamental limit (corrects an earlier wrong claim)
I earlier (wrongly) called the off-table dynamic reads a fundamental ceiling that
needs reversing the no-state-mirroring principle. WRONG — two corrections from the
user: (1) the CORE TENET is a PERMISSIVE filter (use ANY runtime technique for
writelog equality, INCLUDING reproducing the original's techniques); "not a
blueprint" = "not OBLIGATED to mirror", not "forbidden". The RESTRICTIVE filter is
the USF PRINCIPLES, and they constrain only the USF SCHEMA (ML-optimality), not the
composer runtime. (2) StateLayoutMirror is NOT the only way, and done right it does
NOT hurt the USF.
**THE INSIGHT:** off-table reads (freqlo/freqhi[idx], idx>95) sonify the engine's
OWN LIVE STATE in $1707-$17A6 (e.g. idx 244 = $173B = the per-voice DURATION COUNTER,
which the composer computes BYTE-IDENTICALLY — proven). Reproduce the write by having
the composer read its OWN live variable. The idx->variable map is COMPOSER-SIDE engine
knowledge (from the disasm), so the USF is UNCHANGED — in fact we can later DELETE the
static `Instrument.offtable_freq` captured bytes (the C7 content-by-reference pattern)
=> CLEANER USF. So this is ML-POSITIVE.
**✅ VALIDATED (PoC in composer_asm.py ws_rd):** redirect freqlo[244-246]/freqhi[148-150]
to the live `dur` counter. Intro_Music_1 match prefix 2 -> 34 (V1 dur lo-read) -> 186
(V3 dur hi-read, the C6 twin: freqlo+244 == freqhi+148). Canary Geometrical_Zaks stays
FULL (the redirect always emits the orig's value, so no FULL can regress). Each redirect
fixes one read + reveals the next state variable — exactly as predicted.
**THE CLEAN GENERAL FORM = PARAMETRIC READ-REDIRECT, *not* layout-mirror.** I first
thought the elegant build was a layout-mirror (lay the composer's state at freqlo+192..
== freqhi+96.. so reads AUTO-ALIAS). The user's Move-1 question (filter 3,
[[feedback_three_filters]]) CORRECTED this: the layout-mirror COUPLES the composer's
memory layout to each engine — 50 engines = 50 layouts, doesn't unify. The unifiable
form is a per-engine DATA map (idx->state-variable) + a SHARED generator; the composer's
state layout stays uniform. "Elegant for one engine ≠ unifiable for fifty."
**✅ BUILT (commit 932d528):** `_gen_offtable_redirect` (engine-blind generator) +
`DMC_OFFTABLE_STATE` map in composer_asm.py. Behaviour-preserving (single dur row =
byte-identical to the PoC). Grows by adding `(orig_addr, label, n)` rows.
**BUT — REACH IS MODEST (measured 2026-06-26):** re-verifying the 1089 partials with the
dur-counter redirect recovered only ~6/505 (~1%). Most off-table reads do NOT hit the
easy dur counter: (a) many hit HARD state — Rodney idx 212 = $171B filter-def-index (lo)
+ $177B V2-wavepos (hi); wavepos is in the ORIG's wave ENCODING, which the composer does
NOT track byte-identically, so the redirect can't read it without an orig-encoding shadow.
(b) the "offtable freq" census bucket is CONTAMINATED with glide/vibrato accumulator drift
(For_Insider_1 frame 6521 = no off-table state byte matches; it's arithmetic). CAVEAT
stands: redirect only fixes EXACTLY-TRACKING state; DRIFTING accumulators ($1735/$1750)
and ENCODING-specific state (wavepos) need separate work. Adding a map row for a
NON-byte-identical variable would REGRESS FULLs that read that idx via the static capture
— so every new row needs byte-identity verification first.

## 🔑 RESIDUE IS ~20-50 KNOBS, NOT IDIOSYNCRATIC (2026-06-26 session 3 — user corrected me TWICE)
The user's framing (which I twice under-weighted): family-1 is a FINITE engine, so the
residue is a FINITE set of mis-implemented "knobs" (mechanisms), each covering MANY SIDs —
likely ~20-50, NOT 1300 unique problems. My "idiosyncratic" claim was a LOGICAL ERROR: I
traced ~6 members, each hit a different mechanism, and I concluded "all different." But if
the residue is ~30 knobs × ~40 SIDs each, 6 random traces ALMOST CERTAINLY hit 6 different
knobs — so my observation is exactly what the knob hypothesis predicts and does NOT
distinguish it from 1300-unique. Evidence actually favors finite knobs: off-table fixes each
transferred to MANY (dur +7, 25-var map +48, PW-bound +~9); the "heterogeneous SR cluster
(48)" is a FEW knobs sharing a symptom (Hardcore=wave-extraction, Technoland_2=sequencing),
not 48 unique bugs. THE METHOD (user's): fix one SID's TRUE root cause (per-SID pc-trace, NOT
the symptom census) in the shared composer/extractor; it transfers automatically to all
same-knob SIDs; batch the (slow) transfer re-verify across several knob fixes; the knob count
emerges from the cumulative residue drop. Caveat: expect a small tail of genuine 1-offs
(cymbal $DF) + HARD knobs (bit-exact vibrato arithmetic) — ~20-50 knobs likely => ~95%, then
a stubborn last few %. KNOBS IDENTIFIED SO FAR: (1) off-table state-block reads = exactly-
tracking-state read-redirect map [DONE, +48+9, ~tapped]; (2) cymbal-burst value [DONE, 1-off];
(3) ✅ HARDCORE'S KNOB = 8-BIT INSTRUMENT-OFFSET WRAP (commit 3cae4fd). The player indexes
instrument records via the 6502 Y register: `LDA $18F0,Y` with Y = instrument# * 11. Y is
8-BIT, so the offset WRAPS mod 256. For inst# >= 24 (24*11=264 > 255) the record start is
`(#*11) & 0xFF` — a tightly-packed table reuses its low bytes for high instruments. The
extractor used the UN-wrapped offset (`base + iid*11`) and read past the table into the wave
ctrl table -> garbage for inst 24-31. Fix: `off = (iid*11) & 0xFF` in `_decode_instrument`.
SAFE: 23*11=253 < 256, so inst 0-23 unchanged (zero regression); only 24-31 corrected.
Hardcore inst24: unwrapped $19F8 (saw $81/$41) vs wrapped $18F8 (real AD=$00/SR=$00/wstart=$F0
modulation). Hardcore pos 0 -> frame 93.
**METHODOLOGY LESSON (the user caught this, I'd wrongly leaned "pathological garbage"):** when
a trace shows the orig reading "out-of-range / garbage" data, DO NOT conclude the SID is
broken — the packer is almost always right; suspect OUR OWN extractor first (an 8-bit
wrap / wrong base / wrong stride). The user's instinct ("a real packer wouldn't emit a broken
SID; check the docs/packer/STIL") was correct and is the rule going forward. Cross-ref
[[feedback_6502_mindset]] (all bugs are pointer errors; think in exact byte offsets — incl.
8-bit index wrap). FAN-OUT: every member referencing instrument# >= 24 (measuring via broad
transfer test).

## ✅ off-table sub-finding (superseded framing): SYSTEMATIC, NOT IDIOSYNCRATIC (2026-06-26 session 3)
I first (WRONGLY) concluded the residue was a per-member idiosyncratic slog, having
clustered by the FIRST-DIVERGENCE REGISTER (a misleading key — Technoland_2 showed as
"V2 SR" but its real bug is V2 mis-sequencing). The USER pushed back: family-1 is ONE
well-defined player (5400/5401 byte-identical cymbal code — composers did NOT fork it),
so the bugs are in OUR composer/extract handling of SHARED features; fix one => unlock
many. THE USER WAS RIGHT. Lesson: cluster by ROOT-CAUSE FEATURE, never the first-div reg;
and don't call a residue idiosyncratic until you've clustered by cause, not symptom.
**OFF-TABLE READS ARE THE PROOF — they read the engine's SHARED STATE BLOCK ($1707-$17A6).**
Census of WHICH variable each off-table partial reads (tmp/ot_fast.py — orig-only:
flat_div pos -> frame via writelog -> memwatch; DISAMBIGUATE with the lo+hi PAIR, a single
byte value matches many addrs): the reads are systematic but spread, led by basefreq (15),
then accum/glide/pw/transp/dur/vibrato-state. Mapping the EXACTLY-TRACKING state in the
read-redirect (composer_asm.DMC_OFFTABLE_STATE, now 25 vars: transp/fbl/fbh/accl/acch/dur/
glsp/gla/glb/pend/pwl/pwh + pwphase/pwdir/vibdir/vibctr/rampctr/vibdel/vibwid/cvram/wctrl/
vstep/vsteph/slal/slah) recovers them with ZERO regression (the composer maintains these
byte-identically, so the redirect == the static capture for FULLs, > it for partials).
Focused tests: TIER1+2 = 9/17 recovered 0 regress; +TIER3 = 10/22 recovered 0 regress,
30/30 FULLs held. Commits 1ab8c46 + 331d11c. **Generator gotchas:** omit `cpy #256` when a
range runs to idx 255; the long redirect overran `bne ws_drum` -> invert+jmp.
**STILL RESIDUE:** (a) ❌ I WRONGLY EXCLUDED "encoding-specific" state (wavepos/sectorpos/
trkpos) as "can't track byte-identically, needs a deep shadow." CORRECTED BY USER (2x): that
is a CORE-TENET VIOLATION + a three-filters error. The composer is FREE to reproduce the
orig's representation, AND the value is DERIVABLE from what the USF already holds — no USF
change, no stored byte-offsets, no faithful-shadow invention, just the canonical off-table
redirect pointed at a DERIVED counter. PROVEN: orig track byte-offset $1726 = (trkpos>>1)+1
(orig track = leading-transpose byte + 1-byte sectors; our trkpos is 2 bytes/entry), computed
per-voice at `voice:`, mapped (commit 84c0f13). Hardcore first-div frame 93 -> 12631; +recov
(Crystal), 0 regr. LESSON: when an off-table read hits "encoding-specific" engine state, DERIVE
it from the composer's existing data — don't exclude it. SAME for wavepos ($177A) + sectorpos
($1729) = the rest of the class (NEXT; otrk alone is ~1.5%, the full class is the ketchup).
Common-case only so far (mid-list transpose RE-ASSERTIONS — the editor re-states $A0/+0 after
N sectors — + loop targets shift the byte-offset; otrk's simple formula is then off by the
re-assertion count: a follow-up, captured-or-derived). (b) undocumented $171E/$174D/$178F bytes. (c) cleared $1789
($00, never written by composer). (d) glide/vibrato drift that diverges on a SPECIFIC late
event (For_Insider_1 frame 6521), not gradual — the freq-accum arithmetic itself MATCHES
orig (verified glide HI-byte-arrival + triangle-vibrato accumulate). Also commit 202ce45:
cymbal noise-burst value extracted (Presentation $DF; 1 member, the rare genuine 1-off).
**✅ DONE (commit f7ae439): FAMILY-1 4080 -> 4128 FULL (76.4%), +48 mass-written.** The
25-var off-table map recovered 44/538 off-table-freq partials (~6% — most off-table-freq
partials read UNMAPPED encoding-specific state or are glide/vibrato drift, NOT mapped state)
+ dur-counter/cymbal carryover = 48 net. Honest magnitude: the off-table state-block map is
a real SYSTEMATIC win but MODEST (~48), because the truly-recoverable subset (exactly-
tracking-state readers) is ~36-44, not the whole off-table bucket. Zero regression.
NEXT TIERS: ❌ (1) CLEARED-BYTES TIER REFUTED (2026-06-26). Mapped $1789-$1791 (confirmed
always $00: init-cleared $1718-$179D + only $1789 written=$00 + empirically $00 across 8
members) -> a 9-byte const-zero array `ofzero`. RESULT: 0 recoveries + 1 regression
(Piano-Rap_II, whose $1789-$1791 is ALSO $00 — regression unexplained, likely close-tail
flake from the +9-byte state_end shift). REVERTED. LESSON: the off-table census's "$00
reads" are UNRELIABLE — $00 is a COMMON value, so a $00 freq divergence is usually NOT an
off-table state read of a cleared byte but a DRUM/note-freq path (ws_drd reads the wave byte
directly, BYPASSING the wave-step redirect) or a vibrato-accum=0. Top_One_Mix's "idx232->
$178F=$00" was a coincidental match; ofzero left its frame-1 fhi unchanged ($0F), proving the
read never went through the redirect. Do NOT const-zero-map off-table $00 reads. The
remaining tiers: (2) ENCODING-specific state
(orig-faithful wavepos/sector/trkptr shadow — composer tracks the orig's wave-table walk in
lockstep; ~15, DEEP — the composer flattened the wave table so reconstructing the orig step
count is the hard part). (3) different cause cluster (gate-timing/wrong-voice-sequencing).
TOOLS built this session: tmp/ot_fast.py (orig-only off-table variable census, pos->frame
via writelog + memwatch + lo/hi PAIR disambiguation), tmp/ot_fastverify.py (short-dur proxy
verify). Re-verify of PARTIALS is SLOW (~2/min — all get the mask_only retry); narrow to the
relevant subset (off-table-freq) not all 1089.

## 🔬 FAMILY-1 GRIND (2026-06-28): off-table-read class DONE; residue is freq-EFFECT drift
Encoding-specific off-table class essentially COMPLETE + the off-table-read vein is exhausted.
- **otrk ($1726, commit 84c0f13) + wnote ($1783, commit 5b3ca36) added to the off-table map.**
  Both DERIVED from data the composer already has (otrk=(trkpos>>1)+1 from orderlist pos;
  wnote=wave-offset+curnote = the arp note our wavestep computes at `adc curnote,x`). Hardcore
  partial->FULL (otrk); Non_plus_Ultra_tune_2 partial->FULL (wnote). 0 real regressions (the 1
  proxy "regression" Love_with_Sylwia was a STALE-BASELINE palimpsest — fully-reverted build
  still diverged at the same pos, so otrk/wnote innocent; dmc_wide_results.jsonl status='full'
  is UNRELIABLE for members built by old code).
- **sectorpos ($1729) DEPRIORITIZED.** It's the hard encoding-specific case (our composer's
  tagged-event pattern format ≠ orig's packed byte stream: orig $1729 = byte-offset into the
  sector, +1/event +1/prefix(inst/dur/vol/$7C) emit-on-change; +2/+3 for glide mode1/0).
  Byte-cost model fully RE'd (disasm $1837/$17C5/$17DA/$1113 + sub_11E6) + confirmed by trace
  (Retro_Tunel V2 deltas +1 sticky / +2 glide). Reconstructable in the composer by tracking
  running inst/dur per voice, BUT fragile to redundant-prefix editor quirks AND — per the
  FRESH census below — only ~1 member, NOT worth it. SAFE to add later (FULLs don't read it).
- ❌❌ **"OFF-TABLE VEIN EXHAUSTED" was WRONG — RETRACTED (user-caught, 2026-06-28).** I claimed
  the off-table-read class collapsed to singletons (71% drift). TWO tool failures inflated the
  "drift" bucket: (1) `effect_chain_profiler` mis-attributed clean off-table writes to the PSID
  driver spin loop $04A5 (Trap-C cycle-reconstruction bug — FIXED commit ec10551, now reads PC
  off the pc-trace line directly), making me call clean DMC tunes (Object_of_Art, Disco_Mix)
  "custom-code edge cases"; (2) `tmp/ot_fast.py` sampled engine state at the FRAME BOUNDARY (the
  off-table read happens MID-frame, state changed) + filtered to reads where BOTH freq bytes land
  in state $1707+ (missing the arp 96-191 case where the LO byte reads the HI-freq-table). Both
  pushed off-table reads into "no-pair-match=drift". LESSON (3rd time, see Hardcore C11): when a
  tool says "garbage / drift / not-clean", SUSPECT THE TOOL first.
- **TRUE off-table fraction (reliable detector `tmp/offtable_truefrac.py`, 250-sample): 22% of
  freq divergences are OFF-TABLE READS, ~78% in-table (vib/glide/wrong-note).** Detector = at the
  divergence frame, is the ORIG's BASE freq ($172f/$1732+v = freq_lo_addr+0xE8/0xEB+v) an actual
  entry in the 96-note freq table? NOT-in-table ⟺ wave-arp indexed past the table (base off-table
  ⟺ arp>=96; vib/glide keep base in-table, accum does the offset — so NO false positives, it's a
  LOWER BOUND). 794/983 partials (81%) are freq lo/hi divergences -> ~175 members are off-table
  reads (NOT the +5 / singletons I claimed). The recoverable otrk/wnote vein is the BIGGEST single
  bucket, not exhausted. These fail despite the 28-entry map => they read UNMAPPED state vars /
  uncovered indices. NEXT: identify which state vars the 55 off-table members hit (on-write capture
  state contemporaneously), cluster, map the derivable ones (otrk/wnote move at scale).
- The in-table 78% = {vibrato, glide, wrong-note, drift} — a MIX, some recoverable (glide-onset
  traced on Blacha = orig glides +$20/frame, rebuild osc-and-holds; wrong-note = extract bug). Not
  all "hard drift". Sub-classify after the off-table vars are mapped.
- Honest otrk+wnote bank: +5 confirmed FULL at full songlength (Crystal/Riders/Eros_n_Psycho/
  Nasty_Track/Chrimbo_Tune_95). My spot-test "recoveries" (Hardcore=already full in store;
  Non_plus_Ultra=80s-proxy false-positive, still diverges past 80s) did NOT hold — short-proxy
  recoveries MUST be confirmed at full songlength.

## 🔬 FAMILY-1 GRIND (2026-06-26): residue is the hard tail; SONG-EXACT lever = +32 (pending verdict ratification)
Exhaustive per-cause grind of the 1121 partials. KEY OUTCOMES:

1. **TOOLING FIX (commit 75d0bb5): batch flat_div now SKIPS FRAME 0 (init).** The
   clustering flat_div compared the RAW stream incl. frame 0; the composer emits
   its OWN universal-reset init, so frame 0 differs (e.g. D416 $00 vs $08) and the
   flat prefix broke on that INIT ARTIFACT (~pos 26) instead of the real play
   divergence (e.g. pos 158). EVERY residue cluster built on the old flat_div was
   contaminated by init noise — chasing phantom "D416/tiny" clusters that were
   really frame-10 effect bugs. Now matches tools/find_first_divergence
   (--skip-init default) + computes flat_div for CIA too (per-IRQ drops init).
   MANDATORY going forward: cluster on the FIXED flat_div, not the old one.

2. **THE RESIDUE IS GENUINELY INTRACTABLE (proven ~6 ways).** Reliable-flat_div
   clusters: FREQ 74% / CTRL 12% / PW+ADSR+filter 14%. (a) FREQ ≈ off-table reads
   that sonify the engine's OWN LIVE STATE on SILENT voices (e.g. $173B = the
   per-voice DURATION COUNTER; inaudible, dynamic) — reproducible ONLY by
   co-locating engine state in the USF window = the StateLayoutMirror the project
   REJECTED (principle: USF carries music, not engine bookkeeping). (b) CTRL ≈ a
   note-init-vs-running-effects divergence where, PROVEN BY LABEL-RESOLVED MEMWATCH
   STATE-DIFF, the internal state (pend/curnote/dur/spdctr) is BYTE-IDENTICAL
   orig-vs-rebuild yet the writes differ — a per-member knot with no general form,
   not localizable from the write-log. Snowball_Caper_2 = the worked example
   (dur/spd counters identical frame-by-frame; rebuild emits an extra V1 hard
   restart anyway). The duration/tick logic MATCHES the disasm exactly.

3. **✅ SONG-EXACT LEVER (+32 applied, family-1 4048->4080, 75.5%).** A tier of
   partials reproduce the write stream BYTE-EXACT for the full SONGLENGTH (1.0x)
   but fail the standard 1.1x capture because the +10% overshoot runs into the
   LOOP'S 2ND ITERATION, where a free-running modulation phase (vibrato/PW accum)
   carries over slightly differently at the loop wrap — SAME notes/orderlist, tiny
   phase drift PAST the song. Verifying at 1.0x songlength recovers them.
   MONOTONIC-SAFE (FULL@1.1x => FULL@1.0x, zero regression) + PLAYBACK-SAFE (the
   audible song is byte-identical). Concentrated in the >97%-match near-FULL tier
   (~32 of the top 250; broader pool ~5% => ~+40 more available via a full 1.0x
   pass, deferred ~hrs). ⚠️ This is a VERDICT-CRITERION CHANGE (1.0x "reproduce the
   song" vs the 1.1x standard the user emphasized) — PENDING USER RATIFICATION. The
   +32 are mass-written + flagged `song_exact` in tmp/dmc_wide_results.jsonl; the
   batch standard is UNCHANGED (still 1.1x) until ratified. Tool: tmp/verify_1x.py.

BOTTOM LINE: family-1's ~1050 in-song-diverging partials are the architectural
floor (off-table dynamic state) + intractable per-member knots — NOT reachable
from the write-log without reversing the rejected state-mirroring principle. The
clean wins are elsewhere (V5 wave_table_overflow = the C8 dedup port).

## ✅✅ SESSION 2 cont. (2026-06-26): FAMILY-1 4048 (74.9%) + FAMILY-2 2216 (76.7%) + V5 CIA infra
Three more deltas after the family-1 +39 below. Full `tools/regression.py` GREEN
(0 regressed across Hubbard/Companion/C64ME/Jay_Derrett/FC/DMC/Basic_Program).

1. **CLOSE-TAIL CIA TOLERANCE (commit 73058a9, family-1 +13 FULL).** The CIA
   per-IRQ verdict failed genuine FULLs on a duration-cutoff BOUNDARY artifact:
   the rebuild's shorter universal-reset init shifts where the last play() lands
   at the songlength*1.1 capture cutoff, so it logs a few extra TAIL play()s.
   That tail delta scales with the multispeed factor N (cutoff straddles ~N
   play()s), so the flat `close_tol=176` (calibrated for 1x) rejected 4x tunes
   whose tail runs to ~770. FIX: `compare_instruction_stream` gained a
   `close_tol` param (default 176 → non-DMC unchanged); `dmc_family_batch` scales
   `close_tol = max(176, 256*N)` for CIA subtunes (N = play()s/PAL-frame measured
   from the per-IRQ capture). **PLAYBACK-SAFETY GATE (user condition "guaranteed
   no playback risk"):** a recovery past the base 176 is accepted ONLY if
   `r['audio_guaranteed']` — state_match + full play overlap + BOTH init
   boundaries canonical (gates-off + freq-0), which the
   `verify_cycle.init_boundary_is_canonical` docstring FORMALLY PROVES gives
   identical audio. DMC init is canonical (clears SID, sets only test bits) so
   audio_guaranteed≡is_full for DMC. VALIDATED: Works_Music (tail 636) +
   It_Really_Is_Snowing (tail 773) recover audio-guaranteed; Double_Drive (tail
   85 BUT play_full=False = a real within-song divergence) correctly NOT
   recovered → the gate is selective + safe (my raw census of "24 close-tail"
   was an over-count; the real recoverable set is the play_full ones). Re-ran the
   67 CIA + 40 wave-pool members: +13 FULL, 0 regressions. NB the V5 batch does
   NOT yet have this gate (port `dmc_v5_family_batch` if V5 CIA close-tails matter
   — but V5 CIA mostly re-buckets to note_out_of_range/wave_table_overflow).

2. **FAMILY-2 DRIFT RECOVERY (+332 FULL → 2216/2889, 76.7%).** Family-2's last
   batch was 2026-06-14; 12 days of SHARED extract/composer fixes (resting-voice,
   off-table, wave-pool dedup, etc.) landed since in code family-2 also uses, but
   its non-FULL were never re-verified. Re-ran the 1005 non-FULL through the
   (unchanged-interface) `dmc_family_batch` with current code → 332 now FULL
   (partial/unsup/err → full), 0 regressions. Mass-written (332, 0 err) +
   db-refreshed. This was NOT new code — pure re-verification drift recovery.
   LESSON: after a wide-family fix wave, RE-RUN sister families' non-FULL — they
   silently accrue the shared-code gains. (Family-2 has only 1 cia_multispeed
   member, so this was drift, NOT the CIA work.) Authoritative jsonl:
   tmp/dmc_f2_merged.json (re-run = tmp/dmc_f2_rerun.jsonl).

3. **V5 CIA-MULTISPEED PORT (commit db49b51, infra; low immediate FULL yield).**
   V5 had NO CIA infra (composer = VBI-only, no cia_period). 7-file port of the
   ledger-C9 mechanism: composer_v5 programs CIA1 timer A in init + sets PSID
   speed bit; cia_period threads config→V5Model→USF params→from_usf; factory
   `_cia_period_from_writelog` (same as v4) + fallback at the cia_multispeed
   rejection; `dmc_v5_family_batch` captures speed-bit subtunes per-IRQ. ALL
   ADDITIVE — cia_period=0 byte-identical (Katusha canary FULL; the 1041 V5 FULLs
   safe). The 39 V5 cia_multispeed members now build+verify per-IRQ but mostly
   RE-BUCKET to compounding issues (note_out_of_range / wave_table_overflow /
   unknown sector cmd) → ~0-few immediate FULL (ledger C5 "detection ≠ FULL").
   Durable infra; the V5 wave_table_overflow is the C8 dedup's V5 analog (a
   follow-on port to composer_v5). Results: tmp/dmc_v5_cia_results.jsonl.

SESSION-2 TOTAL: family-1 3996→4048 (+52), family-2 1884→2216 (+332). DMC total
sidfinity builds up ~+384. NEXT (all diminishing/per-cause): family-1 freq tail
(heterogeneous), wave-pool suffix-overlap (3), nonstandard_instr_base (11),
V5 composer_v5 wave dedup + CIA downstream, family-2 residue (offtable_live
architectural ~512).

## ✅✅ FAMILY-1: 4035/5401 FULL (74.7%, 2026-06-25 session 2) — +39: wave-pool dedup +5, CIA writelog-rate +20, palimpsest re-verify +14
THREE deltas, all committed + mass-written (4035 .usf+.sidfinity.sid, 0 err) + db-refreshed (hvsc84.csv commit 355a785):

1. **WAVE-POOL DEDUP (commit c73a1d0, +5 FULL; ledger C8).** Composer emitted a
   SEPARATE wave-program copy per instrument into the byte-indexed pool
   (wctab/wftab in composer_asm.py); a member with many same-timbre instruments
   overflowed 255 (wave pos is ONE byte) -> "wave pool overflow" hard build error
   (40 members). Dedup identical (ctrl,freq,loop) programs -> one pooled copy
   (mirrors the orig packer); BYTE-IDENTICAL write stream (each inst re-inits
   wavepos per note + reads the same byte sequence). 40 errors -> 37 build (5
   FULL: Synthology/Heartbreak/Portal_tune_5/Electric_Jesus/Dr_Nabla, 32 partial
   = now diagnosable), 3 still overflow (Marek_Bilinski_1/Riders/Abject_17 =
   ALL-UNIQUE programs -> need SUFFIX-OVERLAP packing, the NEXT tier, not built).
   Canary Zaks FULL (it exercises the dedup path — output byte-differs from the
   stale committed file but write-stream-identical).

2. **CIA-MULTISPEED RATE FROM WRITELOG (commit 2114f21, +20 FULL; ledger C9).**
   The 67 cia_multispeed members are WRAPPER tunes (play!=base+3) whose init
   programs the CIA1 timer in a way py65 CAN'T follow (init hangs / timer set in
   an IRQ / unsupported opcode) -> the factory rejected them. libsidplayfp runs
   the init correctly, so the rate is MEASURABLE from the GROUND-TRUTH writelog:
   `factory._cia_period_from_writelog` counts play()s per PAL frame from
   `siddump --writelog-per-irq --per-irq-debug` (nentries/frame, base=abs PHI1
   clock), rounds N to the integer multispeed factor, returns latch = 19656/N-1
   (the EXACT canon $2663=2x / $1331=4x; N measured within 0.01 of integer ->
   robust). Wired as a FALLBACK at the existing rejection (only the
   py65-unreadable wrapper path -> ZERO regression to existing FULLs; canon-play
   members unchanged). 67 -> 20 FULL + 36 partial + 11 RE-BUCKETED to
   nonstandard_instr_base (a DIFFERENT downstream layout issue = dataflow-
   extractor territory, residue-triage C5 working). Scanland (2x) FULL 199022.

3. **PALIMPSEST RE-VERIFY (+14 FULL).** ⚠️ METHODOLOGY: `tmp/dmc_wide_results.jsonl`
   is a RESUME-PALIMPSEST of many factory versions (the batch skips done paths),
   so its unsupported/error REASONS are STALE/multi-version (a member tagged
   sector_decode may now fail differently) AND its recorded `first_diff` is the
   UNRELIABLE TRICHOTOMY one (phantom D418 — confirmed: I_Am_Ready's "D418
   $0F->$00" was REALLY V1 freqhi off-table, lo-match/hi-diff). Re-verified all
   1080 palimpsest-partials with current code -> 14 are actually FULL (stale,
   predating resting-voice/mask_only). USE the batch flat_div / find_first_
   divergence, NEVER the jsonl first_diff. Merged authoritative jsonl =
   tmp/dmc_wide_results.jsonl (now current; pre-session backup =
   .pre_session.bak.jsonl).

RELIABLE FLAT-DIV CENSUS (686 partials w/ flat_div): freq 81%, HETEROGENEOUS
(CONFIRMED no clean >=30 lever — I_Am_Ready off-table active note lo-match/hi-
diff, Mr_Wain V1 drum abs-freq wave-step phase = distinct mechanisms). Buckets:
freqLO valdiff 254 / freq reb=0 137 (mostly the KNOWN resting/silent-voice
residue, V3-heavy) / freqHI orig=0 48 (scattered) / tiny<=4 44. The freq tail is
the deep per-cause residue the memory already characterized — no fresh lever.

SECTOR_DECODE (deprioritized — architectural/principle-violating): the 58
low-addr ($00xx) failures = a voice loops to byte-after-$FF (the JSR-$1042 hook
loops to the loop-target byte, not 0) into adjacent tunetab/runtime memory and
SONIFIES it (verified I_Like_Cornflakes: loop_target=False diverges ONLY at the
loop tail 90739/90872 -> orig genuinely plays the garbage). Reproducing needs
runtime-memory garbage sectors. The other 30 low-addr are loop_target=False with
a different cause. Matches memory's "sector_decode = deep" assessment.

RESIDUE NOW (merged authoritative): full 4035 / partial 1134 / unsupported 204
/ error 28. NEXT (all diminishing returns): wave-pool SUFFIX-OVERLAP (the 3
all-unique-program members) + the 11 nonstandard_instr_base (dataflow extractor)
+ the heterogeneous freq tail (per-cause only) + family-2 / V5 lines.

## DMC — the focus engine after FC standard went uready (2026-06-12)

Largest HVSC family: 10,676 SIDs (`engine LIKE 'DMC%'` in hvsc84.db).
Player by Brian/Graffity, never source-released. All research in
`pipelines/dmc/docs/` (README.md is the index; provenance_log.md per wave).

## Census (tools/engine_fingerprint.py — renamed/generalized from fc_fingerprint)
`pipelines/dmc/docs/fingerprint_census.md`. 688 exact skeletons → 134
families. **Family 1 = V4 canonical, 5401 (50.6%)** — 0.973 vs the V4
player binary carved from DMC 4 Editor 2025
(`docs/dmc4_player_embedded_1000.bin`). Family 2 = V4-derived variant,
2889 (0.732 to V4, identity TBD — diff later; much may carry over).
Families 3+4+5 = V5 line (2181). V6 = 15 (different player, skip).
Raw data: `tmp/dmc_fingerprint.jsonl` + `tmp/dmc_families.json`
(regen: `tmp/dmc_census.py`). NB the canary-picker DMC candidates are
all V5-line/tail — NOT family 1 (same trap as FC's custom-outliers).

## V4 disassembly — DONE, fully annotated
`pipelines/dmc/v4/disassembly.s` — representative
`MUSICIANS/A/Amadeus_Slash_Design/Geometrical_Zaks.sid` (family-1
dominant exact hash = 3002 members, 3 subtunes, load/init $1000 play $1003).
Header carries: memory map, full variable map, sector/track byte dispatch,
instrument record, filter def, wave table semantics, play flow + write order.

**KEY EXTRACTION FINDING: the editor's packer PATCHES the player's absolute
operands per song.** Fixed: code skeleton, freq tables ($1647/$16A7),
instruments ($18F0), per-note vib depth table ($1888, OVERLAPS code bytes
$1888-$188D for notes 0-5). Patched (read by dataflow at operand sites
$1227/$159C/$15B9/$1296/$180E/$1103/$1108): wavectrl, wavefreq, filterdef,
tunetab, sector ptr lo/hi. Region sizes = address deltas. Some family-1
members have wrapper inits/shifted code (On_My_Way_to_X, Retro_Tech) →
factory must probe, FC-style.

## Engine model essentials (write-log-relevant)
- Duration-based (NOT tick-synced voices); tick = speed-counter reload;
  time = (speed+1) × duration frames.
- Note lifecycle: fetch frame writes ONLY $08→ctrl + $0F→AD+SR (hard
  restart); frame 2 = real AD/SR + pulse/filter/vib init + wave step +
  freq/PW/ctrl; gate on 3 frames min ($1786 guard), then non-holding
  ($10 clear) instruments get gate-mask $FE → tail rides SID release.
  Holding: gate off at duration ctr == 1 (+ AD/SR=$00, sub_17EC).
- Steady-state writes per voice per frame: freq lo,hi, PW lo,hi, ctrl;
  then global $D416 (cutoff), $D417 (res|route). $D418 ONLY at init and
  at filter note-init (mode|vol) — sparse!
- Sector dispatch: $F0-$FF VOL (sustain override), $7C soft-start toggle,
  $7E rest, $7D SWITCH (gate-mask bit0 toggle), $C0-$DF glide/slide
  (bit4=mode), $80-$BF duration (&$3F), $60-$7B instrument (&$1F),
  $00-$5F note, $7F sector end (peeked post-event). Track: $00-$7F
  sector#, $80-$9F/-$A0-$BF transpose ∓0-31 (then next byte = sector),
  $FE voice end (state freewheels!), $FF loop.
- Instrument 11B: AD, SR, PWbounds/init, PW speed nibbles ×3 (6 phases,
  saturate at 5), PWstep-base|filterdef#, vibdelay|width, vibramp/slide
  speed, wave start, FX flags ($01 drum abs-freq, $02/$04 no filt/pulse
  reset, $08 no gate-off, $10 holding, $20 filter, $40 half-rate
  per-note slide w/ GLOBAL parity $1019, $80 cymbal $FFFF+$81).
- Vibrato: triangle, per-note depth ($1888 table), width DOUBLES per
  half-cycle until ramp ctr == byte8; dead-code ADC/BIT quirk at $1589.
- Wave: 2 parallel arrays (ctrl, freq-offset); ctrl >= $90 jumps back
  (val-$90); melodic freq byte REBASES the note (arp); drum = abs hi.
- Filter: single owner per frame ($1720 claim, first voice in X order);
  16B defs: res|mode, cutoff, repeat, stop, 6×(size), 6×(duration).
- Init does NOT clear $1018 ($D417 route shadow) — file-image leftover
  leaks into $D417 until instruments set it (init.sid priming candidate).
- Entries: init/play/+$06 all-off/+$09 sfx (A=note Y=instr X=voice,
  no transpose)/+$1D tune-select.
- ZP $F8/$F9 only.

## ✅ ZAKS FULL (2026-06-12) — pipeline COMPLETE end-to-end
Geometrical_Zaks: ALL 3 subtunes instruction-sequence exact at full
songlength (303565/266449/73661 play writes, trichotomy state ✓).
Pipeline: pipelines/dmc/v4/extract (dataflow operands, path-resolved
patterns w/ loop-unroll cycle detection, exact 5-stage dispatch incl.
ghost $7F=instr31) → USF (schema growth: wave_freq, gate_mode, pwm
speed_steps/keep_running, vibrato ramp, slide 'run'+half_rate,
filter keep_running, noise_attack, signed ol transposes, duration
filter_programs, gate_toggle + glide_to flags, InitVoice.note) →
pipelines/dmc/composer_asm.py (OUR engine; own event encoding) →
xa65 → PSID. Wired into tools/regression.py (DMC section).
Artifacts at hvsc84/.../Geometrical_Zaks.{usf,sidfinity.sid}.

THE THREE FIXES (full detail in pipelines/dmc/v4/RE_NOTES.md):
(1) idle-note voice_state priming — rest-opening voices run effects
on the WORK-FILE LEFTOVER $1012-14 note (init { voice N { note } });
idle effects use instrument RECORD 0 (cleared cache) → extract
force-includes record 0 as slot 0. (2) pulse base split — step =
nibble + CACHED base; idle base=0; composer derives base = step&$0F.
(3) xa65: ':' is a statement separator EVEN IN COMMENTS (sanitizer).

## 📊 V5 FAMILY-4 (Jupiter41, 686) — WIDE-SAMPLE CENSUS 2026-06-30: 0 FULL, early-stage
First 80/686 through `dmc_v5_family_batch.py` (build routes via `_family4_config`).
**0 FULL** — family-4 is a MULTI-SESSION migration with 5 substantial blocker classes
(none are quick wins; verified by localizing one of each):
- **off-table pulse/filter = biggest build-blocker (20/80)** — pulse_table_overflow 8
  + sweep_too_long 8 + filter_table_overflow 4. MECHANISM CRACKED (RE_NOTES + commit
  86c294c): pulse re-inits ONLY on byte3≠0 instrument loads ($13F4 BEQ), so the sweep
  PERSISTS across notes (256+ frames, not the 48-frame note). Walk runs odd positions
  ($07/$09/$0B) past the EVEN $90 loops → reads count bytes off-table → long sweep →
  de-fuses to 513>256. Note-duration bound REFUTED (max 48 vs 256+). Correct fix =
  per-instrument re-init horizon (play-sim) + DROP 16-bit fallback (family-4 counts
  ALWAYS 8-bit). Global-bound REGRESSES (56000→7416). Possibly needs larger sweep repr.
- **family-4 sector format ($F0/$EF + others) = 16/80 build errors** — NOT a 2-line add:
  family-4's sector dispatch ($1150) has DIFFERENT semantics than V5's `_CMD` ($FD=
  transpose not dur; $F0=wave-shift setup 2B; $EF→$1842 2B). Needs a family-4 sector
  decoder + USF map + composer emit. Jupiter41 happens not to use these.
- **partials (35) = genuine wrong-note-data** — e.g. Moonlight_Shadow frame-1: orig
  freq $010C + waveform $40(pulse); rebuild $2F00 + $00. NOT a write-order knob; a
  note/wave-program decode bug. Largest bucket; likely shared sub-roots to mine.
- **USF-gen escape bug (3)** — stray `}` token → UsfParseError.
- misc unsupported 6 (player_code_mismatch 3, capture_loop 2, trailing 1).
**Jupiter41 (rep) itself = partial**, first ~67s write-exact (this session's gated
knobs landed: V3-filter unlock, vibrato byte6&$0F, $D418 vib-skip, wave-speed), blocked
at ~67s by its own off-table pulse. Dependency-ordered plan in family4/RE_NOTES.md.
LESSON: family-4 is NOT close — treat like family-1/2 (multi-session, per-feature).

## 🔬 FREQ TAIL after mask_only (2026-06-23) — HETEROGENEOUS, no single clean lever
After the mask_only win (+147), the REMAINING freq residue is a hard, heterogeneous
long-tail — NOT one more coherent bug. Confirmed by grounded flat-stream diagnosis
of early-diverging representatives (each a DISTINCT mechanism):
- **resting/idle-voice freq**: a voice that starts on rests (note=None) — orig
  writes a non-zero freq (idle-note freq OR instr-0 wave-arp), rebuild writes 0/
  wrong. Funky_Witch V1 (idle_note=0=010C but orig plays note-15 027D via instr-0
  wave-arp); For_Insider_04 (idle_note=254 OFF-TABLE -> orig reads 151F, window=0).
- **wrong in-table note**: Adventure_SF V2 plays $08B4 (a real table note) vs reb
  $09A4 — a pattern/transpose/note-decode bug.
- **glide intermediate**: Plantation V1 (lo off $70 during a 4-row glide).
- **out-of-table effect modulation**: Long_Time V2 $F300 (no glide/vib detected).
Classifier on 60 earliest freq partials: 43 note/other + 17 glide (but the "glide"
ones diverge on the NOTE, not the glide rate — Funky_Witch). LESSON: these are
slow to iterate (median songlength 189s -> full-songlength verify each) and each
sub-cause is its own subtle dive. Diminishing returns vs the mask_only clump.
NEXT (options, not yet chosen): (a) idle/resting-voice freq as a possible coherent
lever (appears 2x); (b) off-table active-note capture completeness (if wrong-notes
are uncaptured off-table reads); (c) pivot to higher-leverage family-2 partials /
V5 line. The architectural-floor framing stays REFUTED — it's recoverable, just
per-mechanism.

### RESTING-VOICE / IDLE-WAVE cluster = the biggest concrete freq lever (~248)
Sized it (tmp/resting_size.py): of 735 freq partials, 248 have the diverging voice
START on rests (238 idle-note-in-table + 10 off-table). GROUNDED diagnosis
(Funky_Witch V1): the voice is GATE-OFF the whole time (ctrl $80/$40/$54 — SILENT,
INAUDIBLE), but it FREEWHEELS its IDLE-WAVE (m.idle_wave ctrl [$81,$40,$40,$81,$55]
matches orig modulo the gate-mask bit) — producing an evolving freq+ctrl write
sequence (027D=n15, 27DF=n63, 1DDF=n58, 1B01) that the composer's idle-wave
execution does NOT reproduce (reb writes 0000/0238/01A9/13EF — different freq). So
this is the COMPOSER'S IDLE-WAVE FREQ EXECUTION for resting/gate-off voices —
write-log-only (inaudible) but counts for the exact-match verdict, and COHERENT
(one mechanism, ~248 members), NOT heterogeneous. THE next freq lever to attack:
diff the composer's wavestep/idle-wave freq computation vs the orig's wave-freq
mechanism, for a resting voice. (NB instr-0 wave_freq=[0,0,0]; the freq comes from
the idle_wave's freq column producing note indices — check how the composer maps
the idle-wave freq column to the SID freq for a gate-off voice.)

#### FIX IMPLEMENTED (2026-06-25): dataflow curnote/gatemask locator + idle-wave off-table
Two commits land the resting-voice fix:
1. **dataflow locates curnote/gatemask** (commit 7b9a49a): `dataflow.locate` finds
   the per-voice curnote ($1012) / gatemask ($100F) STATE addresses by opcode
   signature (re-assembled variants shift them — Funky_Witch curnote $1013,
   gatemask $1010); extract reads idle_notes/idle_masks from the located addrs
   (canon base-offset fallback). EXTRACT-ONLY — the addrs do NOT enter the USF
   (verified; Core Tenet intact). Regression clean + 0/12 FULL-dataflow regressed.
2. **idle-wave off-table capture** (in ecd1b16 — swept into a parallel basic_program
   commit by that session's `git add -A`; intact in HEAD): `_assign_offtable_freq`
   now captures the idle-wave's off-table reads (resting voice freewheels
   m.idle_wave with curnote = its idle note; offsets + idle note overshoot the
   96-entry table) into instr-0's offtable_freq (window is instrument-agnostic),
   post-init-corrected. Regression clean.
Funky_Witch: flat-match 26 -> 95 (curnote) -> 3597 (idle-wave off-table); still
has deeper divergences (a deep member). **APPLIED (2026-06-25): +42 FULL** — of the
248 rest_start cluster, 42 flipped (~17%), 206 stay partial (deeper divergences
beyond the resting voice). Family-1 73.2% -> **74.0% (3996/5401)**; mass-written
(tmp/resting_apply.py, inline flip write) + db-refreshed. NB CROSS-SESSION: a parallel basic_program session uses
`git add -A`/`commit -a` and swept an uncommitted DMC edit into its commit — the
change is safe but watch attribution.

#### ROOT CAUSE (Funky_Witch, 2026-06-23): dataflow idle-note/mask MISLOCATION
The idle_wave freq OFFSETS are extracted correctly ([221,13,8,221,51]); the bug is
`curnote` (the idle note). wavestep does `note = wftab[wavepos] + curnote`; composer
primes curnote=idle_note. Funky_Witch V1: composer curnote=0 -> 221+0=221 OFF-TABLE
-> reb writes 0; orig uses curnote=50 -> 221+50=15 -> n15 (027D) ✓ (13+50=63 ✓,
8+50=58 ✓). So V1's idle note should be 50, not 0. WHY: Funky_Witch is a DATAFLOW
(re-assembled-variant) member; `extract.engine_model` reads idle_notes at CANON
offsets (b+0x12/13/14) and idle_masks at (b+0x0F/10/11), but THIS VARIANT's state
block is laid out differently (V1 note=b+0x13=50, V1 mask=b+0x11=FE — notes +1,
masks +2 vs canon; NOT a uniform shift). So the dataflow path mis-locates the
idle-note + idle-mask block. FIX: the dataflow extractor must LOCATE the idle-note
/ idle-mask reads (the init's `LDA <addr>,x : STA curnote,x` / gatemask sites) by
opcode signature like the other tables, instead of assuming canon b+0x0F/0x12.
SCOPE: likely systematic across the dataflow members in the 248 resting-voice
cluster — size by how many are dataflow + have a shifted state block. This is the
concrete next dive (a dataflow signature extension, NOT a composer change).

## ✅✅ FAMILY-1: 3954/5401 FULL (73.2%) as of 2026-06-23 — STEP 5: mask_only gate-off +147
**MASK_ONLY gate-off applied (+147 FULL, family-1 70.6%->73.2%).** Of 728 mask_only
candidates: 147 FULL flips, 119 not_maskonly (late-clearers correctly excluded by
the full-songlength scan — the regression-safety working), 462 still partial (other
divergences). Flips written via tmp/mask_apply.py (mask_only-DIRECT build, inline
.sidfinity.sid write); merged + db-refreshed. NB the flips CLUSTER in long songs
(median 189s) — the list-order-first chunk was ~2% flip, the long-song tail ~75%;
the strided-sample 18.8% was the right overall estimate. Detection/retry committed
(9cb637f); see below for the mechanism + the late-clearer regression lesson.

## ✅ FREQ FLOOR — STEP 5 first fix: mask_only gate-off (~137 FULLs, 2026-06-23)
First concrete recovery of the (refuted) freq floor. A class of family-1 members
run a MASK-ONLY holding gate-off (the original never zeroes AD+SR), but the
composer defaulted to adsr_clear (canon sub_17EC) and emitted a spurious AD/SR=$00
the orig lacks — which SHIFTS the stream and shows up as a (freq/sr/ad) divergence.
Bouncing_Box: 5%->100% FULL with hold_gateoff=mask_only.
- **DETECTION = the CORE TENET (observe the write stream, not the mechanism):**
  does the original EVER zero AD+SR (both, same voice) post-init? Never => mask_only.
  `factory.frames_clear_adsr(frames)`.
- **MUST scan the FULL songlength** — a holding instr can first gate off late
  (Szybka_1/Ann at 34-42s); a bounded 30s factory probe FALSE-NEGATIVED late-
  clearers -> false mask_only -> ~5% FULL REGRESSION (3/60). So the detection is a
  BATCH-RETRY (commit 9cb637f) that REUSES the verify's full-songlength orig
  capture: only NON-full members whose orig never clears are rebuilt mask_only +
  re-verified (kept iff FULL/more-FULL). Safe (FULLs never retried), reliable, free
  (no extra capture). hold_gateoff threaded into the result -> dmc_mass_write.
- **Measured flip rate: 18.8%** (15/80 strided of 728 mask_only candidates; 17/80
  correctly excluded as late-clearers). => ~137 FULLs across the candidates.
- LESSON: long-song verification is the cost ceiling here — freq-floor partials
  have MEDIAN songlength 189s (they diverge late = long), so a full re-verify of
  the 728 is multi-hour even at siddump's 42x realtime. Measure flip-rate on a
  STRIDED sample first; apply via mask_only-DIRECT build (skip the known-partial
  default build) writing flips inline (tmp/mask_apply.py).

## 🔬 FREQ FLOOR REFUTED (2026-06-23) — the 860 are a STRUCTURED RECOVERABLE TAIL, not architectural
**The "off-table-dynamic floor / StateLayoutMirror limit" framing for the ~860 freq
partials is WRONG.** Meditated on the Core Tenet (the freq write stream is
deterministic + finite — deconstruct to the musical effect, never declare an
unrepresentable dynamic read) and LOOKED with the reliable flat tools. The 860 are
varied, fixable freq bugs — NOT a wall:
- **METHODOLOGY TRAP (important):** the per-siddump-FRAME freq view is TRAP-C
  contaminated — orig/rebuild bucket play() differently, so it shows phantom
  "one-frame phase offsets" that are NOT real. The FLAT stream (`flat_div` /
  `find_first_divergence`, cycle-dropped) is ground truth: there the registers
  ALIGN and the divergence is a genuine same-position VALUE diff. Do NOT diagnose
  freq from the per-frame view.
- **flat_div value patterns (860):** value-diff 424 / reb_ZERO 251 / tiny-diff<=4
  138 / orig_ZERO 47. But the CAUSE is varied (confirmed by grounded
  find_first_divergence on representatives): WRONG IN-TABLE NOTE (Adventure_SF V2
  $08B4 is a real table note — a note/transpose/pattern bug, NOT off-table) |
  GLIDE intermediate freq (Plantation V1 $2532, lo off $70, 4 glide rows) |
  out-of-table effect-modulated freq (Long_Time $F300) | OFF-TABLE IDLE note
  (For_Insider_04 idle=254 -> orig reads 151F, rebuild window=0 — but RARE, 2/80) |
  one-frame note-init transients (freq-hi written late -> stale frame 0).
- **No single big lever** — it's a long tail of per-cause freq bugs. Attack order
  by likely cluster size: glide/slide intermediate-freq computation (the disasm
  glide is $141C-$1442; half-rate slide clock phase `dual_phase`/`SLIDE_PHASE` is a
  suspect for a COMMON offset), then wrong-note/transpose, then vibrato rounding,
  then off-table-idle (small). Each is a focused fix that RE-BUCKETS the rest.
- Reframes the project: this ~16%-of-family-1 bucket is RECOVERABLE per-cause, not
  a floor — family-1 can go well above 70.6%. NOT yet fixed this session (mapped,
  not landed — forcing a fix on the varied tail without per-cause diagnosis would
  violate the principles).

## ✅✅ FAMILY-1: 3812/5401 FULL (70.6%) as of 2026-06-23 — STEP 4 (non-freq effects): filter overrun
**STEP 4 = non-freq effects. RELIABLE clustering required a methodology fix first:**
the batch's trichotomy `first_play_diff` lands on whatever reg sits at its recovered
alignment offset and SPURIOUSLY reports $D418 when shift_d mis-recovers (a phantom
"D418 cluster"). DMC inits MATCH (universal_reset == orig init writes), so the
FLAT-prefix (reg,val, cycle-dropped) divergence is the TRUE first effect divergence
— now recorded as batch `flat_div`. Re-localized all 1275 partials. Reliable
clusters: **FREQ 860** (the off-table-dynamic floor = STEP 5, LAST) | non-freq ~217:
sr 49 / ctrl 42 / **filt_cut 42** / pw 37 / ad 28 / D418 13 / filt_res 6 | no-flat-div
(CIA/length) 198. NB the per-VOICE clusters (sr/ad/ctrl/pw) are CONTAMINATED by
note divergences (a wrong note writes wrong sr/ad/freq; flat_div picks whichever
reg is written first) — they're really freq/note issues. The CLEAN effect clusters
are the GLOBAL filter regs ($D416/$D417, written LAST each frame -> everything
before matched -> isolated).

**FILTER repeat-overrun (+11 FULL, commit 9abd8cd).** The filter step-index, after
step 5, loads `repeat` (def+2); when repeat>5 it OVERRUNS the 6 step-sizes into the
durations (the engine reads size=def+4+index, so index 6..11 = the duration bytes)
-> the rising-to-stop sweep (Fine: repeat=10 -> size=duration[4]=2, rise +2 to
stop=15 then freeze). The composer had compacted the def to an 8-byte stride (6
sizes + 2 pad), so the overrun read padding -> wrong rise (+1). Fixed: 12-byte
stride [6 sizes][6 durations] (mirrors the original contiguous def+4..15) + duration
overrun = 0 (stay-until-stop). filt cluster 48 -> 11 FULL + 37 partial (the 37 have
OTHER divergences after the filter). This is the 5th instance of the off-table-
overrun pattern (freq/pulse/wave×2/filter) — ledger C2 canonicalize. NEXT non-freq:
the remaining filt partials' post-filter divergence; then the note-contaminated
sr/ctrl/pw (really note/freq issues, overlap STEP 5).

## ✅✅ FAMILY-1: 3801/5401 FULL (70.4%) as of 2026-06-22 — STEP 3 (unblock-builds): off-table WAVE + resolver
**off-table-WAVE + marker-chain RESOLVER (zero_wave_table 117 -> 37 FULL + 71
buildable; commits 4da2878 + the resolver).** The recursive resolver
(_resolve_wave_chain) replaced the premature circular-chain refusal: it simulates
the engine's wave-position walk (resolve markers -> emit -> advance) until it
revisits a settled position = the loop. Recovered Jim/Arround_Me etc. as FULL.
Net over the bucket: 37 FULL, 71 buildable (effect_div), 6 degenerate marker-chain
(hit the 512/128 guard), 3 wave-pool-overflow. The +30 FULL from the resolver
crossed family-1 past 70%. Only off-table starts route to the resolver; in-table
is the proven byte-identical slice (regression clean throughout).

## (historical) FAMILY-1: 3771/5401 FULL (69.8%) — off-table WAVE (pre-resolver)
**off-table-WAVE (+7 FULL +27 buildable, commit 4da2878).** The off-table-freq
playbook applied to wave: an instrument whose wave_start (byte 9) points past the
wave ctrl table reads the freq table / following data region AS wave ctrl+freq.
Extend the read window; `_slice_wave` bounds IN-table starts to n_wave (byte-
identical, zero regression — canary Geometrical_Zaks stays FULL) and slices OFF-
table starts over the extension. Of 117 zero_wave_table: 7 FULL, 27 buildable
(effect_div), **80 wave_marker_chain** (circular off-table — refused cleanly), 3
wave-pool-overflow.
- **THE 80 wave_marker_chain ARE RECOVERABLE (next sub-target).** They're refused
  because the off-table program's loop jumps back onto a region containing a marker
  byte. But that's a MULTI-HOP marker chain that SETTLES, not infinite: Jim inst 10
  reads off-table [$0D,$08,$06,$04,$02,$00], $FF marker -> idx5=$91 marker -> idx4
  ($11), then idx5=$91 -> idx4 ping-pong = SUSTAIN $11. So the true program is
  [$0D,$08,$06,$04,$02,$00,$11] looping on $11. Needs a recursive marker-chain
  RESOLVER (follow hops to the settling loop, emit the flat program). Current
  slicer refuses these; a resolver would recover much of the 80. HIGH-yield deeper
  effort.

## ✅✅ FAMILY-1: 3764/5401 FULL (69.7%) as of 2026-06-22 — STEP 3 (unblock-builds): no_jumptable base fix
**STEP 3 = unblock-builds (least-dependent set after the multispeed rate fixes;
a member that can't build can't be FULL).** Census of the 442 error+unsupported
residue, then attacked the cheapest.

**no_jumptable base fix (+5 FULL +4 buildable, commit 97fd5bb).** The $0FF4-prefix
members have a CIA-timer init wrapper at load=$0FF4 and the real JMP table at
$1000 = play-3 with NON-canonical targets (JMP $1751/$1075). Base detection failed:
`_jt` required target==base+$1D, the JT-less fallback only checked `load` (=the
wrapper). Now accept ANY 4C..4C table at play-3 or load. Of 71: 5 FULL, 4 buildable
(effect_div), 54 base-found-but-dataflow.locate-FAILS (re-assembled variant —
locate's opcode signatures miss tunetab/wavectrl/d417), 8 truly headerless.

**KEY FINDING — the unblock-builds residue is uniformly DEEP (no more cheap
mislocations); each bucket is a feature/variant investigation:**
- **zero_wave_table 117**: REAL off-table WAVE reads (the off-table-freq playbook
  applied to wave: an instrument's wave_start (byte 9) points past the wave ctrl
  table into the freq table / data region). Census of 30: off-table distance mixed
  (5 exact-boundary, 15 far >32, recurring starts 145/255). HARD edge case: Jim
  inst 10 (wave_start=110=n_wave) reads off-table then a $FF marker jumps back 111
  onto index 5 which is ITSELF a marker ($91) -> circular marker chain. Zero-
  regression design: extend the read window ONLY for start>=n_wave (in-table
  slicing byte-identical, no FULL regresses). Feature-level + post-init capture if
  the off-table region is work RAM.
- **sector_decode 81 + track-never-settles 21**: sector pointers VALID/in-range
  (not a mislocation) — the decode walks a sector with no end marker -> sector-
  FORMAT variant. Needs format RE.
- **no_jumptable 54**: re-assembled variant, needs a reference carve (family-2 style).
- **cia_multispeed 67** (py65 can't read the wrapper's latch), **wave-pool-overflow
  37** (composer's len(wctrl)<=255 — byte index limit), **headerless 8**.

## ✅✅ FAMILY-1: 3759/5401 FULL (69.6%) as of 2026-06-22 — STEP 2: multispeed (CIA + internal) + verdict
**THREE deltas this step-2 campaign, in dependency order (+387 over the 3372
jsonl base):** CIA-multispeed +367 (below) -> close_tol verdict bump +9 -> internal
play-repeat +11. All committed + mass-written + db-refreshed.

**VERDICT BUMP — close_tol 80->176 (+9, commit 5b097f1).** All 9 close-tail
partials were CIA tunes: full play+state match, only the TAIL length differed
(|la-lb| 85-170). The tail tolerance is a fixed init-shift boundary effect whose
MAGNITUDE scales with multispeed (4x CIA => cutoff straddles a few play()s of
~17+ writes). Same class as FC World_Record_1 (64->80), scaled. Cross-family
constant (FC+Hubbard) -> user-approved before bumping; full regression clean
(loosening only turns FAIL->PASS).

**INTERNAL MULTISPEED — play_repeat (+11, commit 93c86d1).** A class with NO PSID
speed bit (High_Speed/X-Static/Ministry_of_Noise...) whose play vector is a
wrapper doing N x `JSR <play>` (terminated by RTS or a tail-call `JMP <play>`),
running the engine N times per VBI. Rebuild ran 1x -> Nx too few writes.
`factory._detect_play_repeat` reads N from the wrapper (both forms); cfg.play_repeat
-> USF param `play_repeat` -> composer emits the JT play entry as an N-fold
`jsr playframe` wrapper. Gated on speed bit CLEAR (mutually exclusive with CIA).
19 candidates: 11 FULL, 5 re-bucketed to genuine effect_div (rate now correct,
real effect bug revealed — the methodology working), 3 build-detection failures.
play_repeat=1 emits byte-identical output (regression clean). NOTE: more
internal-ms likely hide in effect_div (Nx that diverges mid-stream before the
length runs out) — re-scan when attacking effect_div.

## ✅✅ FAMILY-1: 3739/5401 FULL (69.2%) as of 2026-06-22 — STEP 2: CIA verdict + multispeed rate
**CIA MULTISPEED (2026-06-22, +367 over the 3372 jsonl base; authoritative
re-batch of all 2029 non-FULL).** Step 2 of the residue dependency order
(measure->fix-verdict->...; see [[feedback_residue_triage_order]]). The "length/CIA"
partials were NOT a pure verdict artifact — the per-IRQ verdict fix alone flipped
0/30. It RE-BUCKETED the residue (exactly as the methodology predicts) and exposed
the real cause: the rebuild ran SINGLE-SPEED while the orig multispeeds off the
CIA1 timer. TWO fixes, commit 46cd1ae:
1. **Verdict (per-IRQ capture):** `dmc_family_batch.py` now routes speed-bit
   subtunes through `writelog_per_irq_capture` (Trap C for CIA — flat per-50Hz
   capture phases init+play differently for orig vs a rebuild with different init
   length). Init dropped both sides -> trichotomy recovers d=0, reduces to
   overlap+close. Same machinery FC/Hubbard use.
2. **Rate recovery (the real lever):** the factory only read the CIA timer latch
   when `play != base+3` (a wrapper dispatcher). But the CANONICAL DMC init
   programs $DC04/$DC05 ITSELF with play==base+3 (latch $1331=>4x, $2663=>2x).
   Gate the latch read on the speed bit alone (canon path) + mirror on the
   dataflow path (was hardcoded cia_period=0). Flows cfg.cia_period -> USF params
   -> composer (installs CIA timer + sets speed bits).

Sample 30 CIA partials: 0 -> 11 FULL. Also dropped unsupported 688->380 +
error 199->62 (the re-batch recovered formerly-unbuildable members).

**PARTIAL RESIDUE NOW (1220, rich-record bucketed):** effect_div 680 (genuine
play-stream divergences, lengths now align — the biggest ACTIONABLE bucket =
STEP 3) | state_div 512 (end-of-init priming mismatch; includes the off-table
DYNAMIC freq floor = the architectural-limit bucket, LAST) | rate_or_loop_mult 13
| close_tail<=256 9 | len_gap_nonmult 6.

**TWO NEW FINDINGS (both small, both recorded for later):**
- **close-tail = ALL 9 are CIA** (|la-lb| 85-170). Genuine FULLs (full overlap
  match + state match, only tail length differs) failed by the flat close_tol=80,
  which is calibrated for 1x tunes; at 4x multispeed one play() at the duration
  cutoff = ~40 writes, so the boundary band is ~2-4x larger. SAME class as FC
  World_Record_1 (close_tol 64->80), scaled for multispeed. A flat bump to ~176
  recovers all 9 — but it's a CROSS-FAMILY verdict constant (FC+Hubbard), so
  DECISION DEFERRED to the user, not bumped unilaterally.
- **INTERNAL-MULTISPEED (13+, speed bit CLEAR):** High_Speed / Speed_It_Up /
  X-Static / Melodic_Trance etc. run 2x/4x with NO PSID speed bit — the player's
  single vblank play() loops the engine N times INTERNALLY. Distinct from the CIA
  mechanism: needs a composer play-repeat count (detect the wrapper loop, emit
  repeat=N, composer calls inner play N x). NEW composer feature, step-3+. Likely
  MORE such members hide in effect_div (internal repeat that diverges mid-stream
  rather than as a clean length-multiple).

## (historical) FAMILY-1: 3558/5401 FULL (65.9%) as of 2026-06-22 — + JT-less locator
**JT-LESS BASE LOCATOR (2026-06-22, +90):** the `no_jumptable` residue (364)
aren't jump-table-less — they HAVE a JMP table at load with NON-canonical targets
(e.g. Yardies init->+\$807/play->+\$85; Master_and_Servant init->+\$7D/play->+\$E5)
that the factory's `_jt_layout` (fixed e0/e1 patterns) rejected. The dataflow trace
FOLLOWS the JMPs to the handlers regardless of target offset, so the dataflow
extractor handles them with base=load (work RAM at load+\$0F.., canonical). Wired
(commit a263477): 'no_jumptable' added to `_DATAFLOW_RETRY`; `_build_via_dataflow`
accepts base=load when any JMP table sits at load. Re-batch of 364: **90 FULL
(25%)** + 172 build (partial) + 71 still no_jumptable (genuinely NO JMP table at
load — headerless/different entry; need another locator) + 31 err/other.
Mass-written + db-refreshed.

**RESIDUE CENSUS (2026-06-22, after re-localizing the no-first-diff partials).**
The 1843 non-FULL fully categorized; the 7 actionable buckets in dependency order
(measure -> fix-verdict -> unblock-builds -> fix-effects -> accept-limit):
- **freq ~726** (509 state-match = off-table-DYNAMIC residue, the StateLayoutMirror
  limit; +217 other freq) — the architectural floor, tackle LAST.
- **length/CIA ~154** (the "no_fpd" partials: play stream matches over the overlap,
  only LENGTHS differ -> orig vblank-stub vs rebuild full play = the CIA/multispeed
  artifact). FIX VIA THE CIA-AWARE PER-IRQ VERDICT (exists for FC/Hubbard), not the
  composer. STEP 2 — the biggest single lever, a verdict fix.
- **error 206** ("sector ... never ends" runaway + "wave shape n=0") — extract
  robustness; unblock-builds.
- **vol fade ~145** (master-vol ramp not reproduced) — one coherent modelable effect.
- **unsupported ~410**: offtable_live 78, no_jumptable 71 (truly headerless),
  loop_hook 68, cia_multispeed 67, player_code_mismatch 40 (unlocatable), loop_site
  27, sector_decode 24, zero_wave 22.
- **small effects ~99** (adsr/ctrl/filter/pulse).
Re-localizing the 249 no-first-diff partials (re-run verify_dmc, extract
first_play_diff): 154 length/CIA + 67 freq + 24 small effects + 4 now-FULL (stale
records recovered). Lesson: batch first_diff truncates to [sub,state_match] when
first_play_diff is None (length/init mismatch) -> looks "uncategorized"; re-verify
to localize. NEXT = step 2 (CIA verdict).

**SESSION FAMILY-1 TOTAL: 3135 -> 3562 (+427, 58.0% -> 66.0%):** off-table
offtable_freq port +149, vibdepth follow-on +44, post-init capture +70, dataflow
extractor (player_code_mismatch) +70, JT-less locator (no_jumptable) +90. Two
Core-Tenet breakthroughs: post-init capture (the "dynamic residue" was a file-image
mis-capture) + the dataflow extractor (opcode-skeleton operand location for moved
layouts). Remaining: 71 truly-headerless no_jumptable, 22 unlocatable
player_code_mismatch, the partials (off-table dynamic + newly-buildable).

## (historical) FAMILY-1: 3468/5401 FULL (64.2%) as of 2026-06-22 — + dataflow extractor
**DATAFLOW EXTRACTOR (2026-06-22, +70):** the `player_code_mismatch` residue (203)
is RE-ASSEMBLED DMC v4 players — the routines AND their operand sites moved (e.g.
the `$1231` family, 24 members: SR helper relocated to base+$25A, wave/filter/
sector tables moved), so the factory's fixed-offset extraction + byte-compare gate
fail. New `pipelines/dmc/v4/dataflow.py` locates every table by its canonical
OPCODE-SKELETON signature (relocation-invariant — the opcodes around each read
don't change when a routine moves; match them in the variant's traced code, the
operand there is the table address) + the track-loop hook -> loop_target. Wired as
a factory FALLBACK (commit 10ca8bd): `dmc_v4_config` tries the canon path, then
`_build_via_dataflow` on a moved-layout rejection (player_code_mismatch /
loop_site_unknown / operand_inconsistent / layout_disorder / nonstandard_instr_base).
Canon path first -> normal members unchanged (regression green, 0 regressed);
verify-gated (mislocation -> partial, never false FULL). Re-batch of the 185
player_code_mismatch: **70 FULL (38%)** + 84 build (now partial/diagnosable) + 22
still unlocatable (harder variants) + 9 other. Mass-written + db-refreshed.
NB: handles re-assembled players that HAVE a jump table; `no_jumptable` (364, no
locatable JT) needs a separate JT-less base locator (future). The opcode-skeleton
locator + factory-fallback pattern is reusable for any moved-layout engine.

## (historical) FAMILY-1: 3398/5401 FULL (62.9%) as of 2026-06-22 — off-table port + post-init
**POST-INIT CAPTURE (2026-06-22, +70 more):** the "374 dynamic-residue freq
partials" were a CAPTURE BUG, not an architectural limit (Core-Tenet meditation).
The off-table source bytes live in the engine's work RAM AFTER the freq tables;
the engine's INIT writes them, so the value the original READS at runtime != the
file-image byte I captured. siddump --memwatch on the original shows those bytes
are CONSTANT for the whole song (e.g. Have_a_Drink \$170A: file-image \$68 ->
runtime \$1A). Fix (commit 354fc73): `_correct_offtable_postinit` reads the
off-table source bytes' post-init values via siddump --memwatch (ground truth)
and replaces the file-image values; only CONSTANT-across-sample bytes used
(init-written-then-stable). Re-batch of the 452 partials: +70 FULL. The TRUE
residue is now (a) genuinely-dynamic reads — bytes that increment per frame, e.g.
Small_Introzak k31/k32 cycle 0..15 (the StateLayoutMirror case, REJECTED) — and
(b) co-location edges (off-table reads landing on k15/k16 = the rebuild's own
spd/mvol, e.g. Silent_Tears). Lesson: capture what the engine READS (post-init),
not the file image; don't mirror the state machine. **Off-table partial sub-census
(by first-divergence): 83% freq, then vol/master 29, filter 7, ctrl 5.**

## (historical) FAMILY-1: 3328/5401 FULL (61.6%) as of 2026-06-22 — off-table port
**OFF-TABLE RECOVERY (2026-06-22, +193):** ported v5's `offtable_freq` to v4 —
the biggest family-1 residue bucket was `offtable_live` (665 members: off-table
freq reads past the 96-entry table, previously REJECTED as k<=5 track-ptr / k>=17
live state). The extract now CAPTURES each read's explicit (offset,note,lo,hi) by
VALUE (stable-when-read = the read-before-evolution result), and the composer
places them in the freq overrun window (dual lo/hi landing via freqlo/freqhi/
window adjacency; positions 6..16 stay co-located live spd/mvol -> existing FULLs
byte-identical, 0 regressed). Commits: 83d7c7c (freq port, +149) + 89fa81f
(vibdepth follow-on, +44). The vibdepth follow-on handles note>95 (TWO reads: the
note's own freq via an offset-0 offtable_freq record + the vibdepth table via a
new note-keyed `UsfFile.offtable_vibdepth` field + composer overrun window). NB
the offset-0 base read does the bulk of the vibdepth recovery (vibwid=0 members);
the `offtable_vibdepth` window itself is load-bearing for only ~2 of 45 vibdepth
FULLs (vibwid!=0) — principled (note-keyed musical, same class as offtable_freq)
but marginal. Re-batch (665 off-table-affected): **193 FULL / 452 partial / 20
unsup+err**. Mass-written (193, 0 err) + db-refreshed. Residue: the 452 partials
(now BUILDABLE = diagnosable; many have separate non-off-table divergences) +
genuinely-per-frame-dynamic track-ptr reads. Off-table arc now spans all 3 DMC
consumers (v5, FC, v4). Next family-1 buckets: no_jumptable (364) +
player_code_mismatch (203) + the 452 partials.

## (historical) FAMILY-1: 3135/5401 FULL (58.0%) as of 2026-06-14
Progression: 2257 (first sweep) -> 2656 (relocation: +399) -> 2921
(2-entry layout + base=load: +265) -> 2945 (CIA) -> **3135 (round 1
sub-build recovery: +190, 2026-06-14)**. Mass-written + db-refreshed
(0 err; DMC total 5019 sidfinity builds = 3135 fam1 + 1884 fam2).
**ROUND 1 (commit a8d59ae):** recovered player_code_mismatch + a few
no_jumptable members — the family-1 sub-builds use the SAME variant
axes as family 2: (a) IMAGE-WIDE jump-table scan for relocated-within-
file players (+7; 364 have no jump table, 35 CIA-timer-unreadable);
(b) $1181 = rest_effects='skip' (130 members, the family-2 rest knob in
fam-1 — probe $1180); (c) $1631+$163E = all-off/sfx routines vary but
NEVER run during play() -> masked $162F-$1647 (136); (d) $12A8 = filter
$D418 via JSR helper (STA $D418 + dead store) -> mask+validate (80).
player_code_mismatch re-run: 183 FULL + 73 partial. Residue: remaining
sub-build sites ($1231 SR-variant + helper, $1008-resolved, $18B4,
$1493, smaller), 364 no-jump-table, the off-table architectural limit
(~600). Full regression green (0 regressed).

**2-ENTRY LAYOUT (commit 9212423):** the biggest code-mismatch bucket
(688 @ $1001) is a re-assembled build with a 2-entry jumptable
(JMP base+$807/base+$50) but a play body BYTE-IDENTICAL to canon. The
factory detects layout from the jumptable signature; for 2-entry it
masks the restructured init/dispatch/all-off regions + uses the $180E
tunetab site (also valid for canon). ~290 of the 688 recovered (rest
are 2-entry members with CIA/offtable). player_code_mismatch 1182->495.

RELOCATION FACTORY (commit ab4b4c9): the same player at ANY base passes
(Face2face $9000 FULL, verified $2000-$C000). Relocation is EXTRACT-ONLY
(composer always emits at $1000; writelog base-independent incl. the
original's wrapper-init writes via Check A). base = play-3 (robust to
custom init wrappers — init may point elsewhere). Identity compare vs a
RELOCATED canonical reference: self-ref operands ([$1000,$1900)) shifted
by delta, computed once by tracing canon. Masked the 5 dead-code gap
fragments (unreachable padding w/ relocated operands). vibdepth compared
[6:96] (0-5 overlap code, relocate). config.base threads through extract.

Factory `dmc_v4_config(sid)` (pipelines/dmc/v4/factory.py): masked
identity compare vs the carved canonical player + multi-site operand
consistency + typed DMCV4Unsupported reasons. Wide runner:
tools/dmc_family_batch.py (Pool(8), crash-safe JSONL resume).
Results: tmp/dmc_wide_results.jsonl (first_diff per partial member).

5 triage classes solved this batch (all in RE_NOTES.md):
gate-mask leftovers ($100F-11 → InitVoice.gate_mask); filter-def
slot-vs-slot*8 indexing; 16-bit running pattern pointer (my event
encoding inflates patterns >255B); the OFF-TABLE WINDOW (orig reads
past freq tables into state — composer mirrors the stable prefix
sidoff/fbit/fmask/spd/mvol, extract certifies reachable reads);
TRACK LOOP-TO-TARGET variant (JSR-$1042 hook reads byte-after-$FF as
loop pos; factory-probed); PER-TUNE FREQ TABLES (members ship edited
temperaments → USF freq_table); IDLE WAVE PROGRAM (cleared-cache walks
table from idx 0 → wave_programs[0] + jump-back marker pool semantics);
DUAL-CLOCK PHASE ($1019 leftover → params.slide_phase).

## NEXT (ranked residue, all in RE_NOTES.md "Wide-batch residue buckets")
1. **CIA-MULTISPEED — FEATURE BUILT (eafc895), partial rollout.** +24 of
   the 135 cia_multispeed bucket FULL. Residue within it: ~32 py65-init
   programs no readable timer (init hangs / timer set in an IRQ handler /
   different timer — could measure rate from writelog, risks drift);
   ~29 non-canonical-under-CIA (2-entry or other build at base);
   offtable-live limit. BIGGER: the 459 no_jumptable members are CIA
   wrappers whose player is at NEITHER play-3 NOR load (relocated WITHIN
   the file) — need a jumptable-SIGNATURE SCAN of the image to find the
   base, then the CIA path applies. That scan is the next CIA unlock.
2. 2nd loop-hook variant: EVAPORATED (relocation absorbed it; ~13
   ambiguous `7e18ea` members remain — not worth a dedicated fix).
3. Remaining code-mismatch sub-builds (player_code_mismatch 495, down
   from 1182 after the 2-entry layout: $1181/$1631/$12A8/... — each a
   distinct re-assembly, diminishing returns).
4. offtable_live + zero-wave-table edge errors (636, mostly correctly
   refused — genuinely live per-voice runtime state; architectural limit).
5. Partial long tail (275: bucket by first_diff in the jsonl).
6. **Family 2 (2889, 0.732 V4-derived) — CHARACTERIZED + SCOPED
   2026-06-13** (`pipelines/dmc/family2/RE_NOTES.md`, rep Kajun_Klog).
   SAME V4 engine core (play body \$1085 + all-off \$162F byte-identical;
   ~85% effect chain matches; freq \$1647/\$16A7; operand SITES at canon
   addresses) with: (a) RELOCATED tables — instr \$17B0 (canon \$18F0,
   same 11-byte format), \$D417 shadow \$1034, data tables at family-2
   addrs; (b) THE BLOCKER — DIFFERENT SECTOR ENCODING: terminator is
   \$FF not \$7F (sub_11E6 CMP #\$FF), whole command map shifted. Needs:
   RE the family-2 sector byte map -> family-2 sector decoder (extract
   only; composer/effects unchanged) + factory variant (init JMP
   base+\$37, instr base from operand, d417=base+\$34) + carved
   reference. Tractable, focused sub-migration. Jump-table init offset
   \$37 is the family-2 detect signature.
   **✅ KAJUN_KLOG FULL (commit d9a0cda, 2026-06-14):** write-log loop
   complete — instruction-sequence exact at full songlength (verify_dmc
   66674/66674, trichotomy state ok; writelog 100%). The prior "vibrato
   blocker" was FOUR family-2 effect-chain diffs, ALL rooted in family 2
   relocating its instr table over \$17B0-\$17FF (clobbering canon's
   sub_17EC + sub_17FB ADSR helpers + re-laying the note-init tail/rest
   dispatch). Each = a typed canon-defaulting param (full regression
   green, no family regressed):
   (1) `vib_ramp=step` — family 2 RAMPS the 16-bit vstep by freq_hi(note)>>1
   each half-cycle (\$157F-8E) with fixed width; canon doubles WIDTH with
   a fixed \$1888-table step. Increment DERIVED from the freq table ->
   the prior vib_depth_curve USF field REMOVED (derivable; schema
   hygiene). New vsteph/vdep regs; triangle add/sub now 16-bit.
   (2) `hold_gateoff=mask_only` — holding gate-off = mask only, no AD/SR=0.
   (3) `hard_restart=none` — hard restart = TEST bit only, no AD/SR=0F0F.
   (4) `rest_effects=skip` — rest/switch/slide-tail JMP \$1591 (wavestep),
   NOT the effect chain (canon JMP \$1322) -> vibrato+pulse HOLD one frame
   at each tie boundary (the subtle periodic stall; found via flat
   write-log + sector-dispatch disasm, NOT snapshots).
   (METHOD NOTE: per-frame siddump snapshots = Trap C; stay on the flat
   write-log + --writelog-per-irq + event-aligned --on-write for
   diagnosis — see [[feedback_verification_modes]].)
   **✅✅ FAMILY-2 WIDE BATCH: 1884/2889 FULL (65.2%, commits b0349d3 /
   4e0161d, 2026-06-14)** — exceeds family-1's 54.5%. Mass-written
   (.usf+.sidfinity.sid, 0 err) + db-refreshed (7416 total sidfinity
   builds). `dmc_v4_config` family-2 path: detect jump table init+$37/
   play+$85 (4-entry OR 2-entry), masked identity-compare vs carved
   reference `pipelines/dmc/docs/dmc4_family2_player_1000.bin`
   (reloc-aware), table addrs from canon-compatible sites (tunetab $1051,
   d417 base+$34, instr $17B0 from $1227). The 5 knobs → factory-PROBED
   `cfg.extra_params` (hold_gateoff VARIES: mask_only vs adsr_clear-via-
   helper-at-$1018). Runner tools/dmc_family_batch.py (--members/--out).
   Triage round 1 (+43): $129F filter-mode (STA $9E dead store ≡ AND #$0F,
   probe+mask) + 2-entry jump table (init+play only). 4 family-2 canaries
   wired into regress_dmc (Kajun/Lameness/Fury/Bells = variant cover).
   RESIDUE (tmp/dmc_f2_merged.json): architectural off-table ~580 (20%,
   offtable_live 512+zero_wave 62; correctly refused, same ceiling as
   family 1); partial 279 (diverse freq/NOTE divergences — e.g. Short_Dream
   V3 note 69-vs-66 +3-semitone wave-program/arp diff, Crush_01 V2 freq
   sweep; per-member-diverse long tail, code matches Kajun so it's DATA);
   player_code_mismatch 53 + no_jumptable 52 + sector_decode ~20 (more
   sub-builds / relocated-in-file / corrupt). KNOWN BUG (low ROI):
   dual_phase read from $1019 not family-2's $1035 (harmless w/o dual
   instruments). NEXT (diminishing returns): partial freq/note tail,
   dual_phase, remaining sub-build sites; then family 2's own sub-builds
   are largely done — move to V5 line (2181, separate engine) or family-1
   residue.
"7. **V5 line (2181) — ENGINE PROVEN (2026-06-14): Katusha FULL.** A
   DISTINCT engine (Jaccard 0.136 to V4); full pipeline in pipelines/dmc/v5/
   (disassembly.s Phase A + SCOPE.md + RE_NOTES.md). Phase A: annotated
   disasm + the SECTOR COMMAND BYTE MAP cracked (notes<$80; cmds $F1-$FE:
   SRR/ADR/VOL/gate/FD-/FD+/FRQ/FLT/SLD/GLD/SND/DUR/GATE; $FF END). 8-byte
   instruments (AD,SR,WV,PU,FL,vibD,vibS,vibW); 3 programmable 2-byte
   tables (wave/pulse/filter, $90 loop); full 11-bit cutoff $D415+$D416;
   filter voice-3-only; vib step=freq<<width. Phase B: extract
   (config.py + extract/engine_model.py -> V5Model, validated). Phase C:
   composer_v5.py (clean re-authored engine driven by extracted song
   data) -> Katusha FULL (trichotomy is_full, 97955/97955; 100%
   write-log). **✅ USF LAYER DONE (2026-06-14, commit 8e4c685): Katusha
   FULL THROUGH USF** — extract -> to_usf -> .usf -> parse -> from_usf ->
   V5Model -> composer (composer unchanged). New schema `pulse_sweep`
   (PulseSweepConfig, spec-synced); wave decoded into Instrument.waveform/
   wave_freq/loop; sectors -> Pattern with set_dur/set_instr ORDERED PREFIX
   FLAGS (gate_logic reads the raw lookahead byte, so command byte position
   is write-stream-significant — can't reshuffle snd/dur).
   **✅ FACTORY + FULL SECTOR COMMANDS + PARAMETERIZED PULSE/FILTER (commit
   a8776c2, 2026-06-14):** `dmc_v5_config` (factory.py: 2-entry jump-table
   detect init+$40/play+$A1, family-4 play+$95 REJECTED, relocation-aware
   masked compare vs Katusha ref — operand classes code+state relocate /
   freq+data masked / SID+CIA absolute; typed DMCV5Unsupported). Full
   sector set (vol/frq/fade/adr/srr/flt/gate_toggle/gate_tie/glide/slide).
   PULSE/FILTER are SHARED/FUSED tables (packer overlaps programs; ~30%
   lack $90, bleed) — carried NOT as a table but as per-instrument
   `pulse_env`/`filter_env` = start + (rate,frames) phases + repeat (the
   PWM/cutoff envelope, cross-engine w/ Hubbard/V4 PWM). Fusion dissolved
   by CAPTURE-BY-SIMULATION (`_capture_env` follows $90 jumps, cycle-detects
   on revisit, reach-bounded); from_usf SYNTHESIZES a de-fused table. All
   5 sample-FULL members verify FULL through it. Batch:
   tools/dmc_v5_family_batch.py. **WIDE-BATCH COVERAGE = COMPOSER-GATED
   (6% on an 80-sample, NOT a representation issue — partials reproduce in
   the DIRECT model path).** composer_v5 was proven only on Katusha;
   bug-lever order from the batch: $D416/$D415 FILTER cutoff (22),
   end-of-init state-only Check-A (16), freq/PW (7); + residue
   (player_code_mismatch sub-builds, no_jumptable reloc/CIA, ~36%). NEXT:
   composer rounds — FILTER FIRST, then state-only, then freq (V4-style
   coverage climb). Census: family-3 1461 + family-5 34 = 1495; family-4
   686 (play +$95, separate branch).
   **✅ FILTER ROUND 1 (2026-06-14, commits 8bea641 + f598c2a + 0057347):**
   The "$D416/$D415 cutoff (22)" bucket was TWO causes (the first-divergence
   reg just NAMES the filter — it's the first play-frame write). CAUSE A
   (the ~10-member lead-in cluster "orig $D416=$00 / new $D418=$0F at pos 0")
   = THREE uncleared STARTUP LEFTOVERS in the $1006-$103F gap the init clear
   loop ($17D5-$1845) misses: $1013 spdctr (speed COUNTER -> startup phase:
   when !=0 the first non-skip play runs effects-on-leftover N frames before
   the first fetch; Katusha's=$00 so the cleared composer matched it),
   $100F,x current NOTE (lead-in wave_step freq lookup), $101C fade-frac
   accumulator (first FD ramps master vol off-by-one; init clears the fade
   SPEEDS not this phase). FIX: extract lo_spdctr/lo_notes/lo_mvolfrac; prime
   in init; carry through USF via existing `speed_ctr_init` params + V4
   `InitVoice.note` + new `fade_frac_init` params key — NO shared-schema
   additions. X-Files + Believe newly FULL (80-sample 5->7); Katusha FULL;
   USF round-trip faithful. CAUSE B (round 2, the BIGGER filter lever, still
   gates Grid/Minoam/Conanious): FILTER ENVELOPE KEEP-RUNNING continuation.
   Post-A the cutoff DRIFTS mid-song — FCLO ($D415) drifts (orig RAMPS,
   rebuild HOLDS at Minoam FCLO index 764) while FCHI ($D416) NEVER differs.
   Per-instrument _capture_env envelopes match in ISOLATION, but the
   de-fused per-inst synthesis (each inst its own copy + $90 terminal) does
   NOT reproduce the orig SHARED/FUSED-table running position when a note
   with FL=0 (no filter restart; Minoam insts 3-6,8-13 are FL=0) keeps the
   global filterpos running PAST one program into the next region. Also
   _capture_env treats frames>=$9000 as terminal (inst-2 count $9008 =
   entry-9 $90 marker read as a count).
   **✅ ROUND 2 (commit 24875f3): keep-running filter_run — a run-GATING
   bug, NOT the synthesis-flow I'd hypothesised.** The orig filter_run_v3
   ($1496) gates ONLY on CPX #$02 (V3) -> runs EVERY V3 frame (FL=0 = no
   RESTART, not no RUN -- same PU=0 semantics as pulse). The composer gated
   filter_run on the PER-NOTE filtflag (the inst FL), which an FL=0 note
   resets to 0 -> skipped filter_run on keep-running frames -> cutoff HELD
   while orig RAMPED (FCLO drifts, FCHI matches; Minoam FCLO idx 764).
   Katusha passed (pre-filter null no-op). FIX: sticky filt_run_on flag
   (set once on first FL!=0 note, never cleared); filter_run gates on it,
   filter_init keeps the per-note gate (FL=0 still no restart). Only ADDS
   filter_run on keep-running frames -> FULL members can't regress. The
   per-instrument filter_env representation is UNCHANGED (user-chosen
   parameterisation stands; no synthesis change). **80-SAMPLE: FULL 5->15
   over the session (+10 new, 0 regressions; 7 of 10 were original
   $D416/$D415 partials: Grid/Reggae_2/Save_the_Kwiatki/Fire_Exit/
   A_Load_of_Cowbell/Lands/Bach_VC-220).** RESIDUE: Minoam 98.3% /
   Conanious 96.2% small end-of-song tail (V1/V2 SR + V3 freq late diffs,
   the diverse partial long tail -- NOT filter).
   **✅✅ FAMILY-3/5 CLOSEOUT (commit d46146f): 354/1495 FULL (23.7%; 42.4%
   of the 835 supported full+partial).** Full batch (tmp/dmc_v5_full_results
   .jsonl) -> mass-wrote all 354 .usf + .sidfinity.sid (0 err,
   tools/dmc_v5_mass_write.py) + hvsc84.db refreshed. RESIDUE: 481 partial
   (diverse long tail: Minoam/Conanious end-of-song V1/V2-SR + V3-freq tail,
   + state-only Check-A + freq/PW buckets); 593 unsupported (no_jumptable
   261 reloc/CIA + player_code_mismatch 266 sub-builds + note_out_of_range
   27 + cia 13 + wave/pulse-overflow + trailing-cmds); 67 error
   (_capture_env ptr-overflow 45 + unknown-sector-cmd 12 in relocated/corrupt
   + timeout 8).
   **✅✅ RELOCATED/WRAPPER-INIT UNLOCK (commits 0e3c319 + 023c1b6 + 5f3a0de):
   354 -> 461/1495 FULL (+107; 30.8% of 1495, 41.9% of supported).** The
   no_jumptable (261) + player_code_mismatch (266) buckets were 477/527 the
   SAME family-3/5 player with a RELOCATED or WRAPPED init: play body still
   at base+$A1, but the init MOVED elsewhere and/or its A-reg prefix differs
   (LDA #0 single vs ASL*3 song-indexed). Old factory keyed base off the
   jumptable LOCATION (+$40/+$A1) and compared the WHOLE player -> any
   moved/re-prefixed init rejected. FIX (family-1/2 sub-build playbook, V5
   form): base = play_target - $A1 (play is the reliable anchor); validate
   the PLAY-reachable body only (_v5_play_ref $10A1-$170E); validate the
   init by its orderlist-copy SKELETON at the jumptable's init target +
   read op_orderlist from THAT init's actual load operand (init_target+7) ->
   relocated/wrapped init handled. base-plausibility margin = base+$848
   (only code+state $1006-$1845 relocate; data tables are packer-patched;
   the $1900 margin wrongly rejected high-load base=$F000 builds -> 2
   regressions, fixed). multi_subtune (36, ASL*3 song-indexed orderlist,
   songs>1) typed-deferred (needs multi-song PSID emit). ~300 members moved
   unsupported->supported; all 461 FULL mass-written + db refreshed.
   RESIDUE NOW (286 unsupported + 640 partial + 108 error): player_code_
   mismatch 152 (deeper code variants — bucket by play-body first-diff PC),
   multi_subtune 36 (multi-song emit feature), note_out_of_range 36,
   no_jumptable 22, error 108 (extract robustness: _capture_env ptr-overflow
   + unknown-sector-cmd in relocated/corrupt).
   **✅✅ MULTI-SUBTUNE SUPPORT (commits b4994d0 + 21e767d): 461 -> 466/1495
   FULL (31.2%; 41.4% of supported), 0 regressions.** Song-indexed orderlist
   record (init reads song# from A: ASL*3; PHA across state clear; PLA; TAY;
   index ordrec by song#*8); data tables (sectors/instr/freq/wave/pulse/
   filter) SHARED across subtunes; one MusicSubtune per record (per-sub
   tempo/master_vol/voices; global leftovers on subtune 0). UNIFIED with
   single-subtune (song#=0 -> Y=0, identical). 5-file change (engine_model
   V5Subtune + extract N records; composer ordrec N + song-indexed init +
   PSID songs=N; to_usf N MusicSubtunes; from_usf pool sectors across all
   subtunes; factory rejection removed). +5 fully FULL (members need ALL
   subtunes FULL; 138 subtune-songs all build correctly); 34 moved
   unsupported->supported. All 466 mass-written + db refreshed.
   RESIDUE NOW (252 unsupported + 660 partial + 117 error): player_code_
   mismatch 160 (deeper code variants), note_out_of_range 38, trailing/wave/
   pulse/cia/no_jumptable misc; error 117 (extract robustness).
   **✅✅ PARTIAL LONG TAIL round 1 — FILTER OFF-TABLE (commit ba63846):
   466 -> 543/1495 FULL (+77; 36.3% of 1495, 47.1% of supported), 0
   regressions.** Biggest partial cluster (FCLO/FCHI bucket ~70+) = the
   filter table is the LAST data region so a_fh-a_fl does NOT bound it; tiny
   tables (2 entries, all insts FL=1) run filter_run PAST the array into the
   overlapping lo/hi arrays + following bytes (ramp lives OFF-TABLE). FIX
   (extract+capture, no composer change): read filter table generously
   (n_filter=min(256,memtop) — filterpos is a byte; off-table bytes = what
   orig reads, 0 past payload = siddump zero-fill); _capture_env count==0 =
   counter wraps 65536 = TERMINAL HOLD (off-table zero-region was spinning to
   sweep_too_long). Also fixed ~28 _capture_env ptr-overflow errors
   (117->89). Direct path already worked (emits table verbatim); only USF
   capture needed it. partial 660->610, all 543 mass-written + db refreshed.
   **✅✅ PARTIAL LONG TAIL round 2 — LOOP-TARGET TRANSPOSE (commit ddaed0c):
   543 -> 683/1495 FULL (+140 — biggest single win; 45.7% of 1495, 59.2% of
   supported), 0 regressions.** The end-of-song cluster (292 partials @>=95%,
   just after the orderlist $FF loop) was ONE root cause despite the diverse
   symptom: the composer's $FF handler treated the loop-target byte as a
   sector#, but MANY orderlists loop back to a LEADING $FC/$FD transpose
   (Minoam: all 3 voices loop to pos 0 = $FC). The orig's $FF -> $111F
   re-dispatches the loop target through the $FD/$FC checks. FIX (1 line):
   $FF handler `jmp tf_chk_fd` (sector# targets fall through unchanged; a
   FULL can't regress — never hit the path). Minoam FULL (its "pulse
   off-by-one" was downstream of this loop). partial 610->470, all 683
   mass-written + db refreshed. **METHODOLOGY (CLAUDE.md): from here, iterate
   on a STRATIFIED SUBSET (~120, by first-diff bucket + FULL slice, ~5min),
   full-batch ONLY at closeout.**
   **✅✅ ROUND 3 — LOOP-POSITION + TRANSPOSE RE-ESTABLISHMENT (commit e882c10):
   683 -> 842/1495 FULL (+159), 0 regressions** (the USF round-trip loop-target
   bugs: to_usf loop_to via group-start bytes + loop_transpose re-establishment,
   negative loop@N-T grammar). **✅ ROUND 4 — this session (commits 575492b +
   40f496d): 842 -> 848/1495 FULL (56.7%), 0 regressions.** Two parts: (a) a
   carry-target loop fix — round-3 only handled loops targeting the transpose
   PREFIX (re-establish); a loop can also target the entry byte PAST the prefix
   (CARRY, transpose persists over the wrap), which fell to loop_to=0 and
   REGRESSED 5 ex-FULL members (Metropolitan/Fast_and_Slow/Trance/Techno_2/
   Deep_Inside). _orderlist now maps each byte to (entry, is_prefix); monotonic.
   (b) wrapper/trampoline detection (follow a 1-hop `JMP base+$A1`; resolve init
   skeleton among [jt-target, JMP-follow, base+$40]) — +Background_Pleasure.
   **TOOL: `tools/divergence_census.py`** (see [[reference_divergence_census]]) —
   clusters the residue. KEY FINDING: **detection ≠ FULL** — the 153
   player_code_mismatch are NOT the FULL bottleneck (detecting them just exposes
   downstream bugs); the verify-PARTIALS are.
   **✅ ROUND 5 — STATIC PULSE/FILTER HOLD (commit 266a5b5): 848 -> 875/1495
   FULL (+27, 58.5%), 0 regressions.** The "67 check_A_state_only" cluster was a
   RED HERRING — 0 were init-priming; all were `shift_d=None` trichotomy
   alignment failures (early play divergences desync the midpoint landmark;
   init prefixes match, d=0). TRUE first-divergence histogram: ~34 pulse-width
   (clean 2x-ramp signature), ~18 filter, ~13 frequency. Root cause of the
   pulse cluster: `from_usf.add_env` emitted `[start][$90->start]` for a STATIC
   env (phases=[]); the engine re-reads the START pair as an ADD step → ramps
   +start.hi/frame instead of holding (Hardcore_DMC $D403: orig holds 8; rebuild
   8,16,24,32...). Fix: static env loops on a ZERO-ADD with count==0
   (65536-frame hold). Shared by pulse+filter. Also `verify_cycle` fallback now
   reports first_play_diff (16c4053, diagnostic).
   **✅ ROUND 6 — DEFAULT (IDLE) V3 FILTER SWEEP (commit 86d3259): 875 -> 889/1495
   FULL (+14, 59.5%), 0 regressions.** The engine runs filter_run_v3 for V3
   EVERY frame from filterpos=0, where filter-table position 0 is a DEFAULT
   (idle) cutoff sweep no instrument points at — applied to the leftover cutoff
   from song start (for tunes whose V3 never plays a filtered note, this is the
   whole filter motion, e.g. Glory_Kingdom). The composer nulled entry 0 + gated
   filter_run on a sticky filt_run_on flag → never ran the idle. FIX (principled
   per the rep-principle + init trichotomy): new top-level USF `default_filter`
   (a SweepEnvelope — same form as Instrument.filter_env, Rule 1) carrying the
   PLAY-TIME sweep; init.sid.filter keeps only the priming STATE (initial
   cutoff). Composer runs filter_run for V3 from frame 0 (gate removed; pos 0 =
   the idle sweep, or a (0,0) hold). Shared USF plumbing (types/grammar/parser/
   writer/docs) — full tools/regression.py GREEN (0 cross-engine regressions).
   **✅ ROUND 7 — SONG-DERIVED SWEEP CAPTURE HORIZON + walk-cap (commit 5b32e79):
   889 -> 891/1495, 0 regressions.** `_capture_env`'s fixed `_REACH_FRAMES=30000`
   capture budget (a magic number, safe only because 30000 > every 1x song's
   window) replaced by the actual per-song horizon `reach = min(songlen*1.1,
   1500)*50` play-frames (verified V5 = all vblank; CIA rejected, so 50Hz exact),
   computed in write_v5_usf from cached Songlengths.md5, threaded to _capture_env.
   Needed (not "capture whole program") because from_usf DE-FUSES the packer's
   byte-overlapped programs, so a full capture can exceed the 256-entry table;
   bounding at the window keeps it fitting. Helps both ways: SMALLER for short
   songs (fixed filter_table_overflow: Hot_Island, Progress = the +2) / LARGER
   for >545s (closes the old under-capture hole). Plus `_WALK_CAP=5000` iteration
   seatbelt (reads, not frames): a malformed $90->$90 chain spun _capture_env
   forever (900s batch timeouts / infinite hang in tools) — now an instant
   `unsupported:capture_loop` (timeout 10->0, +9 capture_loop). Idle-filter
   capture best-effort. (Came out of the owner's "why 30000, not songlen*1.1?"
   question — their instinct was right; "capture complete program" over-corrected
   into 2 overflow regressions before landing on the per-song window.)
   **✅ ROUND 8 — DEFAULT (IDLE) PER-VOICE PULSE SWEEP (commit a4c70c8): 891 ->
   913/1495 FULL (+22, 61.1%), 0 regressions.** Pulse twin of default_filter: the
   `rebuild=0` cluster is a real idle pulse program at pulse pos 0 (Doomed V2
   $D409 = 0,49,98,147,196 = pulse[0]=(0,49) loop) the composer nulled. Carry as
   `default_pulse` (PW SweepEnvelope), emit at pulse pos 0; pulse_run runs it from
   pulsepos=0 (UNCONDITIONAL — `run_effects` JMPs to pulse_run; NO per-voice gate;
   $1841 only gates the note-time LOAD). **CORRECTION to a wrong earlier note: I
   hypothesized a "per-voice pulse-active gate" — there is NONE.** The first cut
   regressed 891->786 (-135) NOT from the idle ramp (all 135 regressed have
   pulse[0]=(0,0), no idle) but from changing the NO-IDLE case from single (0,0)
   to a 3-entry hold (shifted the de-fused table). Fix: keep single (0,0) for
   no-idle (byte-identical → can't regress); emit idle only when pulse[0] is a
   real ADD. Lesson: a no-idle "layout cleanup" is NOT free (de-fused table is
   position-sensitive). NEXT V5 (ranked): (1) FREQUENCY clusters (~143 across
   V1/V2/V3 freq regs — BIGGEST, likely vibrato/glide); (2) remaining pulse
   partials w/ a SECONDARY divergence (idle now fixed: Doomed/Amiga-Zak); (3)
   NON-idle filter bugs (Emulating_Vinkuna/Cooksey/Art_of_Noise); (4)
   player_code_mismatch; family-4 (+$95). Full detail in RE_NOTES.
   **DONE: DB migrated SQLite -> git-tracked CSV (hvsc84.csv) + DuckDB CLI
   (see [[reference_hvsc_db.md]] / CLAUDE.md).**

## REGRESSION PORTFOLIO (2026-06-13): generalized + DMC wired
`tools/select_regression_portfolio.py` made engine-parametric (registry:
engine -> jsonl/out/feature_fn/witnesses/sid_key; exact_multicover stays
engine-blind). DMC feature extractor + `tools/dmc_regression_portfolio.json`
wired as tier-1 in regress_dmc(). The closeout step is now standard
(documented in CLAUDE.md + migrate skill): family reaches FULL coverage
-> derive portfolio -> wire tier-1 (full family batch = tier-2).

## Off-table-freq de-verbatim (v5) — DONE 2026-06-21, LOSSLESS

The v5 `freq_overrun` blob (verbatim post-freq-table bytes, the C7 anti-pattern) is
ELIMINATED. Replaced by per-instrument `Instrument.offtable_freq` = list of
`(offset, note, freq_lo, freq_hi)`, `idx=(offset+note)&$FF` (USF schema in
src/usf/{types,grammar,parser,writer}; extract `_assign_offtable_freq`; composer
`composer_v5` builds in-bounds extended freqlo/freqhi from it — no OOB read).
**1041 FULL = the freq_overrun baseline, 0 regressed.** Full design + evidence:
`deprecated/old_docs/offtable_freq_plan.md` + `pipelines/dmc/v5/RE_NOTES.md` rounds 11-18.

WHAT THE OFF-TABLE IS (verified, rounds 12-18): the player's wave-program freq
lookup `freqlo/hi[wave_offset+note]` has NO bounds check; for notes that overshoot
past the 96-entry table it sonifies the engine's own work-RAM (orderlist POINTERS
= addresses, counters, track-sequence bytes) in the fixed `$17CF-$1877` gap.
UNDOCUMENTED (full online sweep) but the v5 expression of the documented DMC4/7
"DRUM EFFECT = pitch steps in higher range" idiom; player binary is sole authority
(kept under `pipelines/dmc/docs/src/`). ~1/3 of load-bearing reads are audible
(noise drums / tri tones), ~2/3 inaudible. Capture SITES (all needed): wave-program
steps + offset-0 BASE read (vib_setup `base-note freq<<width`, note freq, glide
arrival) + the lead-in IDLE program (wave index 0) x lo_notes.

LESSON: the "load-bearing residue" bugs (Redemption_6_4, Planet_Love) were CAPTURE
GAPS (missing off-table read sites), NOT glide/vibrato/wave-position effect bugs —
my diagnosis was wrong twice until I TRACED (state via composer xa65 return_labels
vs orig memwatch) instead of assuming. **Phase 6 DONE 2026-06-21:** FC migrated to
the SAME `offtable_freq` mechanism (cross-family unification — 2528 FULL lossless;
see [[project_fc_fingerprint_and_standard]]), surfacing the dual lo/hi-read window
bug + the close_tol 64→80 boundary fix. Phase 7 (remove the `freq_overrun` field
from the shared schema, now both consumers are off it) is the remaining cleanup.

**V5 wave-pool dedup (2026-07-01, +5 FULL):** the V5 `from_usf.py add_wave`
concatenated every instrument's wave program with NO sharing (V4's composer_asm
dedup was never ported), overflowing the 256-byte single-byte wavepos on many-
instrument tunes (`wave_table_overflow`). Ported identical-(ctrl,freq,loop) dedup
(ledger C8) — 17/19 overflow members now build, +5 FULL (Autumn_Symphony,
Breakpoint, Mysterious_Energy, Sky, Life_Plus); 2 genuinely exceed 256B of
distinct wave content (For_Zeor 318, Samael_01 1848 = the single-byte-wavepos
architectural limit). KEY LESSON: V5's loop marker is ABSOLUTE (`$90, s+loop`),
not V4's RELATIVE (`$90+n-loop`), so moving a program rewrites its marker and
dedup is POSITION-DEPENDENT — even byte-identical programs regressed a FULL member
(CreaMD Ambient, freq divergence; the de-fusion adjacency coupling the pulse table
shows). Fix = OVERFLOW-GATE (share only when un-shared pool >256): zero-regression
BY CONSTRUCTION (never touches a member that already builds). Batch reason
`wave_table_overflow` = raised in `from_usf.py:279` (`len(tbl)>256`), NOT the
composer_asm `wave pool overflow` assert. Same overflow-gated dedup could unblock
the small `pulse_table_overflow`/`filter_table_overflow` buckets (add_env, also
absolute markers) but family-4 has 0 FULL so low yield — deferred.

**⭐ FAMILY-4: 0 → 26 FULL (2026-07-01).** The off-table CAPTURE fix — truncate_on_cap +
overflow-gated pool dedup — applied to BOTH the pulse and filter paths across the full
686-member corpus (`tools/dmc_v5_family_batch.py --members tmp/v5_family4_members.json`),
took family-4 from 0 to **26 FULL** (pulse fix +20, filter fix +6). Mass-written +
hvsc84.csv refreshed (batch `tmp/dmc_family4_full2.jsonl`). The FILTER extension
(`_capture_env_f4` truncate + `_filter_env_for` + `from_usf.add_filter` dedup) ELIMINATED
the `sweep_too_long` bucket (56→0) and halved `filter_table_overflow` (31→16). RESIDUE (686):
partial 336, error 168, unsupported 156. NEXT TIER = SUFFIX-OVERLAP pooling for
`pulse_table_overflow` 55 + `filter_table_overflow` 16 = 71 all-unique-program overflow
members (a program that is a tail of another shares storage — ledger C8 boundary). Unrelated
residue: player_code_mismatch 36 / capture_loop 32 / no_jumptable 15 / errors 168
(relocation/variant/sector-format/USF-parse). Regression on both fixes: 0 (family-3 FULL
sample + the family-4 FULLs + cross-engine all clean).
The off-table pulse blocker is fixed;
Jupiter41 is FULL at full 292s songlength (play_match 268831/268831). Root cause (found via
the Trap-C-ROBUST FLAT write-stream localizer, `tmp/reframe_flat_localize.py` — per-frame PW
snapshots were RETRACTED as Trap-C artifacts, caught by a negative control on FULL family-3
members): `_pulse_env_for`'s count8bit walk hit `_PHASE_CAP=48` on the off-table one-shot ramp
at the whole-song reach → raised `sweep_too_long` → fell back to the family-4-INCORRECT 16-bit
`_capture_env` (read the 8-bit count E0=224 as 16-bit 0xFFE0=65504 terminal hold → collapsed
the program to +32 forever, DISCARDING the +2048 off-table sweep → divergence at write 56000).
Two family-4-scoped fixes: (1) `_capture_env(truncate_on_cap=True)` — keep the captured prefix
at PHASE_CAP (covers ~7000 frames >> any note; the pulse re-inits every note-load) instead of
the wrong 16-bit fallback; (2) overflow-gated PULSE-pool dedup in `from_usf.py add_pulse`
(mirrors the wave dedup, ledger C8) — the correct capture is large (16 insts / 5 programs =
356 B un-shared → 209 B shared, fits 256). Regression: family-3 30/30 FULL (0), cross-engine
`tools/regression.py` 0 regressed. PREREQUISITE PROVEN EARLIER: the off-table pulse source
($23A3-$24BB) is 100% STATIC (`tmp/taint_memtrace.py`, --memtrace within-frame-complete) ⇒
representable, not residue. The other 35 building family-4 members stay partial (other
blockers: note/freq/filter foundation) — Jupiter41's LAST blocker was the pulse. Tools:
`tmp/reframe_flat_localize.py`, `tmp/verify_pulse_fix.py`.

## Related
[[project_fc_fingerprint_and_standard]] (the playbook this follows),
[[feedback_dataflow_over_heuristics]] (the operand-patching finding is
exactly this), [[feedback_disassembly_data_section]] (research.md's wrong
tables), docs/the_trichotomy.md (the $1018 leftover).
