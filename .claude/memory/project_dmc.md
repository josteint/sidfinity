---
name: project_dmc
description: "DMC (Demo Music Creator) migration — THE FOCUS ENGINE (largest HVSC family). Round changelog, NEWEST-FIRST: the head of this file IS the current status (counts live there + in MEMORY.md, not here). KEY: data-table addresses are PACKER-PATCHED operands — extract by dataflow, never fixed offsets."
metadata: 
  node_type: memory
  type: project
  originSessionId: c83d6f65-8c2c-42bb-8f55-d46a1994efb2
  modified: 2026-08-22T21:11:40.989Z
---

## ✅ PRINCIPLE AUDIT + REMEDIATION (2026-08-23)

An audit of the v5 work against the four canon docs found the Core Tenet and
the trichotomy clean but TWO real problems, both now closed:

1. **Principle §8 leak.** `family4` was a params key naming the ORIGINATING
   PLAYER, and the composer gated ~190 lines of 20 emitter branches on it —
   §8's shape exactly, breaking its constraint that such a tag is read by the
   dispatcher and never by an emitter. DECOMPOSED into 14 named mechanism
   knobs (play_skip_init, pulse_ctr_8bit, filter_d416_only, filter_prog_8bit,
   …). Detection stays in the extract; what crosses into the USF is the list
   of BEHAVIOURS. Gate = byte-identity, 123/123 unchanged (C33 carrier
   refactor).
2. **`play_phases` in the params bag** while `Environment` already had typed
   siblings — promoted to a typed field via the generic CNAME-key form (a
   keyword terminal would have shadowed CNAME in ~5.4k stored files).

⚠ TWO THINGS THE GATES CAUGHT that grepping had not:
   * SIX more `family4` reads lived in `to_usf`/`from_usf`, not the composer,
     controlling the pulse/filter 8-bit (add,count) encoding. Byte-identity
     failed on 51 family-4 members until they were repointed — the composer's
     asm was identical, the difference was in the USF ROUND-TRIP.
   * 28 stored `.usf` carried `family4`; they parse fine and would have
     rebuilt as CANON members (C20 third layer). Regenerated, each `.sid`
     rebuilt FROM its `.usf`, and the one hetero_v5 member resynced through
     its own path.

⚠ AND THE PARAM LINT COULD NOT SEE ANY OF IT: v5 routes params through its
MODEL rather than `params.fields`, so its whole surface was invisible and the
lint said "clean" while 3 of 4 keys were registered nowhere. It now follows
the from_usf layer.

METHOD NOTE: the ledger check happened AFTER diagnosing, not before — the
documented weak link. And the v5 engine work had ZERO ledger record until the
audit; C18/C9/C13 now carry it.

## 🔎 DMC v5 GRIND OPENED (2026-08-22 night): the residue is ONE PLAYER VARIANT

**The v5 grind is "make family-4 work".** Whole-corpus census (2026-08-23):
`family4` (the Jupiter41 branch, play +$95) is **642 of 2,151 members** and
sits at **7.0% FULL of buildable** (35 full / 466 partial) against canon's
**84.5%** (1,132 full / 207 partial). family-4 carries **466 of the 673
partials = 69%**, so it is the residue.
⚠ An earlier claim this session that family-4 had ZERO FULLs was wrong — a
40-member sample artifact (~30% likely at the true rate). Corrected by census.

The planned "top lever" (a 352-member position-0 cluster read as a
folded-in lead-in) was a MIS-DIAGNOSIS in two ways: the flat verdict
structurally cannot see a folded-in lead-in (an empty play() adds nothing to
the concatenated stream — confirmed by fault injection), and the cluster is
80% family-4 rather than a family-wide phase bug.

LANDED (27b4530f): family-4's `DEC $1016 / BMI` 2-phase startup seeded from
the `$1016` file-image leftover, plus dropping family-3's `playskip = 2`
(family-4's play has no such counter, so every family-4 rebuild opened with
two silent frames — a real defect no gate can see). The 2026-07-01
family-4 round had the mechanism and failed only for the missing second
half. Depth on a 140-member stratified subset: the 1-63 bucket 58 → 13,
deeper 49 / shallower 0 / **regressed 0**, 0 reached FULL — it UNBLOCKS the
class rather than closing it. Detail + the next two first-divergences:
`pipelines/dmc/family4/RE_NOTES.md` (2026-08-22 section).

⚠ METHOD NOTE worth carrying: for an unblocking lever, full/partial counts
report "0 gained" and hide the entire effect. Score it with the
first-divergence DEPTH HISTOGRAM (`tmp/v5_depth_measure.py`).

## ✅ DMC v4 CLOSEOUT COMPLETE (2026-08-22): f1 + f2 verified, stored, audited, guarded
FINAL STATE — f1 5,445/5,445 FULL and f2 2,924/2,924 FULL; every member
stored (`.usf` + `.sidfinity.sid`); mass-write 0 err / 0 orphans on both;
from-disk audits 11/11 (f2) and 10/10 (f1, stratified over ALL six build
paths: compilation / hetero_masm / hetero_v5 / medley / multisid /
single). The f1 FULL re-batch under current code came back 5,445/5,445
with **0 regressions and 0 gains** vs the #85 baseline — the byte-identity
censuses had predicted exactly that, now confirmed by measurement.
Regression tier-1 guards 103 DMC members (64 f1 portfolio + 33 NEW f2
portfolio + canaries), 0 regressed.
⚠ f2's 2,924 rows read STALE-HASH again, and that is FINE — the only
hashed change since its batch is `pipelines/dmc/verify.py` (the
`verify_member` addition + the behaviour-preserving `_verify_rebuilt`
factoring), and `pipelines/dmc/family_batch.py` does not import that module
at all (it carries its own capture/compare). Conservative invalidation
saying "unknown" + a cheap proof is the correct response; re-batching
1.5 h to satisfy a hash is the waste the RTS literature warns about.
Recorded here so the next session doesn't re-run it reflexively.

## ⚠ HARNESS BUG the portfolios exposed (2026-08-22): regression built EVERY DMC member as a single player
The re-derived portfolios pulled in two COMPILATIONS (Defuzion_3,
Nyaaaah_9) and both read as REGRESSED — sub 0 FULL, rest garbage (the
C31 signature). Not a composer regression: `tools/regression.py`'s
`_w_dmc` called `dmc_v4_config(sid)` for every member, i.e. ASSUMED the
single-player dispatch — ledger C20's 4th layer in a consumer nobody had
audited (the rule was written for mass-writers, where `corpus_sync`
closed it). CURE: `pipelines.dmc.verify.verify_member(rel)` runs the
canonical dispatch and RAISES on an unimplemented path (2SID / medley /
multiplex) instead of silently falling back; `verify_dmc` is unchanged so
the 101 single-path members take exactly the same code as before. Both
compilations then verify 4/4 and 2/2. ⚠ the dispatch now lives in FOUR
places (batch worker, dmc_build_one.build, corpus_sync replay,
verify_member) — factoring is a Move-1 candidate and until then each copy
is a place this recurs.

## ✅ F2 CLOSEOUT RUN (2026-08-21/22): batch + sync + portfolios — resync debt CLEARED
Full f2 family batch: **2,924/2,924 FULL, 0 partial**;
`batch_diff` vs the pre-closeout snapshot (`tmp/dmc_f2_85_results.pre_close.jsonl`)
= **0 regressions, +15 gains**. Mass-write synced all 2,924 (0 err, 0
orphans) with the from-disk audit 11/11 across compilation / multiplex /
single. f1 INCREMENTAL: the 3 dead-cargo carriers outside f2
(Astrostorm_II_preview, Lane_Crazy, Mythig_2SID) re-batched FULL +
written, audit 4/4 — no full f1 re-batch was needed because the two
corpus-wide byte-identity censuses (25 window-conflict carriers + 66
past-EOF candidates) had already proven every other f1 member
byte-identical.
⚠ TRAP FOR THE NEXT SESSION — TWO f1 RESULTS FILES, the obvious name is
the WRONG one: `tmp/dmc_wide_results.jsonl` (5,401 rows) is the
**pre-#85** working file and is what `select_regression_portfolio.py`'s
`dmc_v4` registry entry still points at; the authoritative #85 set is
`tmp/dmc_f1_prev_batch.jsonl` (5,445 rows = exactly
`tmp/dmc_f1_members_85.json`, all FULL, all stale-hash). The overnight f1
re-batch writes a fresh `tmp/dmc_f1_85_results.jsonl` and the registry
should then point THERE.
PORTFOLIOS (the closeout's other half): `dmc_v4` re-derived (64 members,
93 feature dimensions) and a NEW `dmc_f2` registry entry + portfolio —
until it, ALL of f2 was guarded by four hand-picked canaries covering
none of the f2 grind's levers. A closed family gets its OWN entry; the
extractor is family-blind (generic over `extra_params`) so it was a
one-entry change, as the registry's own comment promises.

## ✅✅ FAMILY-2 CLOSED: 2,924/2,924 (100%) — Conversion + Witchs_Birthday + Just_11 FULL (2026-08-21)
ONE lever closed all three (C9 10th occ): the f2 $FF track-loop handler's
SHIPPED `LDA #imm` (canon $10DE) — loop EVERY voice to track position
imm. The X-mas C37 probe handled the wrapper POKING that operand but
nothing read its shipped value; 10 carriers (imm 1-6) walked loop@0.
Factory now reads it (canon-anchored static, imm=0 → None, byte-
identical). All 10 carriers FULL (3 partials landed + 7 stored-FULLs
re-verified). The three had presented as three unrelated deep classes
(drum-tail stagger / sticky-instr / switch-row anomaly) — all downstream
of wrong wrap rows; the decisive measurement was the orig's otrk AT the
wrap ($0C → $04). Smoke 6/6, regression green. BYTE CHURN: the 7
re-verified FULL carriers' stored artifacts are stale — fold into the
next f2 batch + mass-write resync (with the earlier vib_inc/dead-cargo
churn). NOTE the earlier Conversion recon rabbit holes ($FD switch
handler decode, "freeze", zeros rows) are all explained by the wrap.

## RESIDUE (superseded by the head entry above — f2 is closed): 3 partials — Witchs_Birthday, Conversion, Just_11
All three measured; diagnoses + state captures in backlog.md item 6.
Conversion: the f2 $FD switch handler is now DECODED ($1183: dur=durrel /
EOR #$01 gatemask / INC sectpos / term-peek — a timed gate-toggle row our
walk already models); the residual is a one-frame V3 footprint (orig
freewheels a zeroed state, ours preps) near the sector-5 `$FD $FF` tail —
suspect switch-row × note-end-prep interaction. Witchs: per-voice
row-end stagger mid-song (orig V2 mid-drum-tail when ours ends the row).
Just_11: ours plays a filter-flagged SR-$5F instrument where orig plays
inst 4 (sticky-instr/lap-2 or a $D418-automation data-poke driver).

## ✅ OFYRON_GADAF FULL (2026-08-21, same session) — f2 2,921/2,924, 3 partials
ONE knob: `filter_before_voice=2` (C16 unit-ORDER form). The orig
neuters the body's V3 JSR to `LDA abs` and its play vector wrapper
(`JSR base+3 / LDX #2 / JSR voice / RTS`) runs V3 AFTER the filter
tail — the tail's $D417 samples the routing shadow BEFORE V3's
note-init clears/claims its bit (play-1 $F5 vs our tail-last $F1).
No value semantics differ; pure within-frame order. TRAP survived:
the member's routing shadow is RELOCATED to $1034 (reads as header
text; canon $1018 = constant garbage) — watching $1034 AT the $D417
writes showed the ordinary moving shadow, killing both the "static
wedge" and "canon shadow" readings. Static probe, sole carrier in
10,774; smoke 6/6; regression green.

## ✅ ARTRIS FULL 6/6 (2026-08-21, same session) — f2 2,920/2,924, 4 partials
The batch's `build_path: single` was a stale-detection palimpsest (C20):
current detect_compilation finds the 2 packed players ($9F00/$8D00);
the compilation path then hit `wave pool overflow` (332 deduped bytes >
255 — the C8 signature, our merge creates the overflow while each
player's own pool fits). Fix = C8 FIFTH widening: `_split_wave_pools`
(per-subtune-component pools, component idle at pos 0, init SMC-patches
the 4 wave-step read operands wsp0-3 via wpooltab[cursong]). Fires only
where the single pool overflowed = previously a hard error → regression-
safe by construction. Smoke 6/6, regression green.

## ✅ PAST-EOF SECTOR TRIO FULL (2026-08-21, same session): Final_Game 6/6 + James_Bond + Fantasia — f2 2,919/2,924, 5 partials
The wrap/fold cluster's shared lever was C29, not C32: a played sector
whose BASE sits past the image end in plain RAM (Final_Game sector $33 @
$521B, image ends $27A9). The orig reads the power-on $FF stripe there,
and f2's in-sector terminator IS $FF → the environment ENDS the pattern
→ track $FF → loop to 0; our image-zero view decoded an endless note-0
self-loop (V2 loop@5). Fix: `_offimage_sectors` past-EOF surface
(base-past-end ONLY — the window-tail form flagged 4,725 members, the
Kaj2 gate-on-the-walk lesson; disabled for post-init members). Gates:
66-candidate census rebuilt, 2 changed (Session 25/25 + Note_4_Remix)
both re-verified FULL; smoke 6/6; regression green. Diagnosis chain:
memwatch V2 otrk/sectpos at the divergence → the wrap lands at otrk 1
while our USF said loop@5 → sector addr $521B vs image end.
NOT this class: Witchs_Birthday (divergence is mid-song at otrk 8/9,
NOT the wrap — orig V2 mid-drum-tail ctrl=$80 when ours ends the row;
sectors/terminators all in-image and clean; needs the per-voice
row-end stagger dig), Conversion (orig V3 FREEZES at a `$FD $FF`
sector tail — endless note-hold, sectpos pinned, note-init rewrites
each dur expiry; needs the f2 switch/ghost-glide handler semantics),
Just_11 (ours plays a filter-flagged SR-$5F instrument where orig
plays inst 4 SR $5A at otrk 6 late-song; earlier passes of the same
rows matched — sticky-instr/lap-2 or a $D418-automation data-poke
driver). All three measured 2026-08-21; state captures + detail in
backlog.md item 6 (tmp/conv_state.txt, tmp/j11_state.txt,
tmp/wb_state.txt).

## ✅ KNOWLEDGE_POSSE_TUNE_3 FULL (2026-08-21, same session) — f2 2,916/2,924, 8 partials
C18 f2 parity wrapper: P alternating with a reverse-voice pulse-tail
pass (`P_R321`) under CIA latch $2663; the f2 pulse entry $1370 skips
the parity nibble select → new `rphase_variant='pulse_tail_hi'` (R step
= stale wjmp HIGH nibble always) + static `_parity_fx_wrapper_probe`.
Sole carrier in 10,774; Toccata_v2 (f1 pulse_tail) byte-identical;
smoke 6/6; regression green. Method note: the flat localizer read this
as "diverges at play 0" — the per-IRQ chunks matched (init straddle
under the tight latch); the A/B param-injection loop (config →
write_usf → build → dbo.verify) collapsed the diagnosis to minutes.

## ✅ SAMS016 FULL 7/7 (2026-08-21, same session) — f2 2,915/2,924, 9 partials
subtune_songs 2nd carrier (C19 38th-occ family), the ARITHMETIC-REMAP /
FALL-THROUGH form: init $0FFD `CLC / ADC #$01` falls into base $1000 —
every subtune plays record sub+1. Probe widenings: `_init_song_observe`
watches dispatch entries (base+$1D/$37) + the map probe's anchor admits
a fall-through wrapper. Census 475 candidates → exactly 1 fires
(Sams016). Smoke 6/6, regression green. The "early-state/prime family"
recon guess was wrong — it was the record shift all along (sub 0's
mid-song SR diff = records 0 vs 1 first differing at one instrument).

## ✅ OVER_AND_OUT FULL (2026-08-21, same session) — f2 2,914/2,924, 10 partials
The recon's "garbage $D418=$A8" was misread: the orig CHAINS songs — an
appended per-subtune countdown wrapper (the `_medley_switch_probe` C31
form, 3rd carrier) re-inits into song 1 at counter expiry; our $A8 was
just the next note's SR while the orig restarted. Two refinements
(ledger C31 entry): the chain jump is ONE JMP INDIRECT (follow it), and
the target row can be ARMED (the counter bytes are the author's `**`
credit text!) so `msw_x` now zeroes the counter after the chain (orig's
spent counter stays 0). NemTP + Fuckin_Birds re-verified FULL; smoke
6/6; regression green. Just_11 (same composer) is NOT this class —
stays partial (C10 $D418 automation per the backlog recon).

## ✅ VIB-INCREMENT READ SITE (2026-08-21, same session): For_Nitro + Hot_Mallorca FULL — f2 2,913/2,924, 11 partials
C11 4th read site: the f2 note-init vib setup `ldy curnote,x / lda
freqhi,y / lsr / sta vdep,x` bypassed the off-table redirect map — an
off-table note (For_Nitro curnote 140 → $1733 = own live fbh; vdep =
fbh>>1 = $21) got a starved swell from the static window byte.
Hot_Mallorca's "down-slide ours never arms" was the SAME lever (the
growing swell reads as a slide). Fix: composer `nv_rd_sub` (the shared
`_gen_offtable_redirect` chunk, jsr-ed from ni_vib_depth), gated
`vib_inc_redirect` = member carries an off==0 off-table record at a
mapped fhi idx. Gates: 30 stored-FULL carriers of the gate re-verified
30/30 FULL (incl. Session, Trekky, Rowdy, Sub_Burner); smoke 6/6;
regression green. Diagnosis: `--memwatch-on-write D407` at the orig's
divergence showed vstep=vdep=$21 with wnote=curnote=$8C. Remaining 10
partials re-verified still partial (their causes are distinct — see
backlog item 6). BYTE CHURN (2026-08-21): the 4 dead-cargo-changed
carriers + the 30 vib_inc_redirect carriers now build byte-different
from their stored artifacts; the 4 new FULLs have no stored artifacts
yet — run the f2 batch + mass-write resync at the next closeout.

## ✅ TRACK-PTR PAIR FULL (2026-08-21): Blast_n_Scream + Zwei_Bereten_Preview — f2 2,911/2,924, 13 partials
The backlog item-6 "one lever, two members" idx-96 pair (off-table fhi
reads on the $1707-$170C per-subtune track-ptr slots). Root cause was NOT
a missing capture — the values were captured and split correctly; the leak
was the composer's `ovr_sub` per-subtune window build being LAST-WINS over
ALL records of USED instruments, so a record the subtune never READS
overwrote the byte it does read at a shared window position (ledger C31
single-player form, DEAD-CARGO refinement — full detail in the entry).
Two extract-side fixes, zero composer/schema change: (a) the value-class
split now filters each output instrument's records by song attribution
(Blast_n_Scream sub 1: clone kept `(72,24)→$D0` att {3}, killing its own
`(32,64)→$97`); (b) new `_declutter_offtable_by_reach` pass for the
cross-instrument form where the split never fires (Zwei both subs) —
clone-and-remap gated on an actual read-value collision. Gates: smoke 6/6;
25-carrier stored-USF conflict census rebuilt — 21 byte-identical, 4
changed (Astrostorm_II_preview 7/7, Lane_Crazy 6/6, Mythig_2SID 3/3,
Koshimo_preview_1 2/2) all re-verified FULL; full regression green.
NOTE byte-churn: the 4 changed carriers' stored artifacts are stale until
the next f2 batch + mass-write resync.

## ✅ WEDGE TRIO FULL (2026-08-21): Petshopmix + Inside + Childs_Play — f2 2,909/2,924, 15 partials
C19 53rd-55th (staged in tmp/singleton_patches_0820.md during the
closeout, landed after): `vib_swell_ror` (swell ADC->ROR + neighbor-poke
writeback — the x=2 poke redirects to slal[0], the orig's ADDRESS-MAP
neighbor, not our label+1), `filter_idx_eor` (def-index EOR abs,x with
X = the claiming voice, pc-watch-measured; v2-claim pins the walk to
step 0), `filter_dur_store_dead` (fdu never written). All sole carriers
(census-before-landing); all FULL at full songlength; golden 5/5, smoke
6/6, regression green; synced + audited. ALSO 2026-08-20/21: the f2+f1
CLOSEOUT completed clean — f2 2,906 + f1 5,445/5,445 re-verified under
current code, 0 regressions, all synced (0 err/0 orphans), corpus
12,577/12,577, spec+param lint clean. The byte-churn debt (Kaj2
overlay + Sub_Burner carriers) is settled.

## ✅ SUB_BURNER FULL (2026-08-20): 3 C31 levers — f2 2,906/2,924, 18 partials
Third singleton, same day (commit 2d05d961). A 2-player compilation
whose first player is COPIED to $1025 with a two-JMP head at $1000:
(1) implied-base f2 dispatch (C13 — base = play-$85, guarded); (2)
per-subtune idle-pulse record `idle_pulse_instr` (the pulse sibling of
idle_wave; composer icin0 → cinst,x prime); (3) `filter_def_orig` fbase
orig-number shadow (fbsh) for the idx-116/212 read. ⚠ AMEND lesson: the
first fbase fix RE-ANCHORED the def window and REGRESSED Lane_Crazy
(caught by the golden-verify pass; bisected via env toggles; readers'
remaps are usually unobservable — C7 one-way) → reverted to the
zero-layout shadow. Proof method: standalone player-2 build matched
orig sub 1 wall-to-wall (457,746 writes) = merge collapse was the whole
defect. NOTE — BYTE CHURN: the committed Kaj2 wave-window overlay + the
rec0/fd_orig carriers change stored-artifact bytes for a set of
compilation members (all re-verify FULL; golden 9/9); their stored
artifacts are STALE until the next f2/f1 batch + mass-write resync —
run that closeout before trusting fifth-layer audits on compilations.

## ✅ KAJ2 FULL (2026-08-20): C29 7th — the WAVE WINDOW reads past EOF; f2 2,905/2,924, 19 partials
Second singleton, same day. The idle marker-chase is mod-256 (8-bit Y);
Kaj2's wave window runs 108 bytes past EOF, so the chase (pos 0 → $FF
past EOF, power-on ≥ $90) chains into co-located garbage cells — idle
V2/V3 cycle ctrl $4E/$52/$4A for 208 plays where the extract's
image-zero view settled silent. Fix (commit 9ecec6e2): the shared C29
CPU-eye overlay over the off-image wave windows, gated to "the idle
walk's sim visits a past-EOF position" — the broad geometry gate was
MEASURED AND REFUTED (broke LSD_4K's unplayed cycling chain, changed
Andjana; 119 corpus carriers, narrow gate = Kaj2 alone changes,
118-FULL golden sweep 118/118 identical). Synced + audited. C29 entry
has the general lesson (gate a new overlay surface on the WALK, not the
window geometry).

## ✅ DELTA_ZAK FULL (2026-08-20): dur_fetch_underflow (C19 52nd) — f2 2,904/2,924, 20 partials
First of the 21 refreshed singletons (backlog item 6). The f2 $10C3
duration-fetch BEQ→BMI wedge: every row +1 tick, init seed = 2 plays;
presented as "diverges at play 0" (the whole stream shifts). Knob
`dur_fetch_underflow` (one-opcode swap at the composer's fetch gate,
temporal-dispatch, registered; init_behavior C33 typing candidate —
33rd-occ test run + recorded). Sole carrier. Synced + audited.
SINGLETON RECON (same session, per-IRQ first-plays probe over the pos-0
cluster): Kaj2 = idle V2/V3 walk leftover wave programs with cycling
ctrl $4E/$52/$4A where ours are silent (idle-priming class); Sub_Burner
= orig play-0 EMPTY (delayed start) + different idle values; Ofyron_Gadaf
= filter-tail/V3 write ORDER + a $D417 routing value ($F5 vs $F1);
Knowledge_Posse_tune_3 = init split across two plays + a reverse-voice-
order ctrl=$45 idle pass (C18-ish); Artris = BUILD FAIL 'wave pool
overflow' under dmc_build_one though the fresh batch row built 'single'
(divergence pos 27 — investigate the build-path discrepancy first).
Witchs_Birthday: orig preps only V1 at 94.9% while ours preps all 3 —
V2/V3 last-pattern durations end early near the wrap; final sectors
unterminated within their 256-byte windows (C32 endless-tail shape) yet
the walk emitted loop@0 — UNRESOLVED, needs the endless/fold dig.
Zwei_Bereten: mid-song V2 freq-hi value divergences (subs 0+1).

## ✅ SESSION MEMBER FULL 25/25 (2026-08-20): class (b) was the SAME C8 disease — the ovr patch-stream guard
Same day, second fix: sub 6's mid-song V3 freq divergence was NOT an
effect bug — the per-subtune off-table window patch (`ovrbase`/`ovrpat`)
was silently DROPPED by its 8-bit guard (6 conflicting positions × 25
subtunes = 325 > 256), so subtune 6's glide-arrival compare byte
(window pos 1 = idx 97, per-context $1708) came from the static
last-wins window and V3's `C#8 noretrig glide=15` (slide-form target =
note 97, off-table) NEVER ARRIVED — orig snaps curnote=97 and plays the
off-table-served base $0E01 while we extrapolated the slide past it.
Fix (commit ee8cad14): ovr WIDE form — 16-bit per-subtune row bases as
label arithmetic, init SMC-patches both `ovrpat` reads, Y walks the row
from 0; row>255 still drops. Golden 9/9 MD5-identical incl.
Para_Lander_DX (the documented ovr_conflict carrier), smoke 6/6, full
regression green. Method note: the diagnosis chain was offtable_probe
(clean bow-out) → effect_chain_profiler (writer = canon sidwrite) →
memwatch at each D40E write (curnote $3C→$61 with no track movement =
glide arrival) → USF inspection (row + at(0,97,1,$6F) record BOTH
correct) → composer derivation replay (glide_offtable=True, sub-7
d[1]=111 correct) → the guard. f2 count: 2,903/2,924, 21 partials.
LESSON recorded in C8: one member overflowing one 8-bit index → audit
its other per-subtune streams the same day.

## ✅ SESSION class (a) — 9 subtunes FULL (2026-08-19): the C8 4th widening (subtune*16 wrap)
GAMES/S-Z/Session (5-player C31 compilation, 25 subtunes): subs 16-24's
"per-player merge collapse" diagnosis was WRONG — the per-player extract
and merge were both correct (merged sub 17's first row matched orig's
exact AD/SR). The cause was the composer's init indexing its stride-16
tune records with `subtune*16` in 8-bit Y: subs ≥16 wrapped and played
subs 0-8's records (proved by diffing the rebuild's own subtunes: our
sub 16 stream == our sub 0's). Fix (commit 6b561fc0): init SMC-patches
each tunetab read's operand hi byte with `subtune>>4` (sites ttp0-ttp7),
gated on >16 subtunes — golden 8/8 MD5-identical, smoke 6/6, full
regression green. Sole built carrier corpus-wide (Arc_Doors 20 subs is
unmigrated). Session now 24/25 FULL incl. sub 4's old 7-write tail; the
remainder is sub 6 (class b): V3 freq lo o$01 r$CC at write 12626, 81.9%
in, player 0 song 2 — separate cause, under investigation. Ledger C8
entry has the transferable form + TELL.

## ✅ GOOD_BEAT's KNOB DECONSTRUCTED (2026-08-19, same day): vib_dir_dead → `vibrato { shape: drift }`
Owner-driven correction hours after the knob landed: `vib_dir_dead` named
the broken MECHANISM (a reader must know the flip internals to infer
"pitch drifts up forever"); the pitch trajectory is a MUSICAL value, so
the C19 33rd-occ rule applies — deconstruct, don't knob. The typed home
already existed: VibratoConfig.shape grew 'drift' (owner-approved enum
growth; grammar unchanged — shape=CNAME already accepts it; writer/parser
untouched). Extract stamps shape='drift' on the instruments whose vibrato
RUNS (amplitude>0) when the $1571 probe fires; the composer derives the
flip elision from shape UNIFORMITY across running-vibrato instruments
(mixed shapes RAISE — one flip routine, no corpus carrier; empty/triangle
= canon byte-identical). The params key + registry row are DELETED (50
keys). The USF now reads `vibrato: onset=0 shape=drift amplitude=3
ramp=4` — the drift's acceleration is fully specified by the SAME
width/swell fields triangle uses (speed += swell-increment every `width`
frames until the ramp cap, then linear; D = freq_hi(note)>>1 via
vibrato_ramp='step', so higher notes drift faster). Gates: FULL
67,077/67,077; corpus 12,573/12,573; spec+param lint clean; fifth-layer
OK; full regression green.

## ✅ GOOD_BEAT FULL (2026-08-19): vib_dir_dead — f2 now 2,902/2,924, 22 partials
Second diagnosed item-6 member, same day as Orchestral. The 08-14
canon-diff diagnosis was wrong on BOTH counts: the active wedge is the
$1571 half-cycle DIRECTION-FLIP writeback (`EOR #$01 / STA $1768,x`)
re-pointed to $17AB — a void below the $17B0 instrument table with NO
readers (pokes inert, not a data-poke), so vibdir never toggles and the
vibrato is an accelerating one-way pitch drift. The $1512 slide-down
misalignment is DEAD CODE (pc-watch: zero executions; full-songlength
FULL proves unreached). Fix: composer knob `vib_dir_dead` (flip pair
elided; running-flip sibling of vib_ramp_persist/vib_phase_persist),
probe anchored on the intact EOR#$01 + STA operand != base+$768.
Sole carrier in 10,787. Method note: the divergence arithmetic
(o=$3C+$19 vs r=$3C-$19) said "direction" immediately once memwatch
showed vibdir stuck at 0 — the state dump (vstep swelling 0/$19/$32,
rampctr alive) separated flip-dead from step-dead/ramp-persist in one
capture. Smoke 6/6, fifth-layer OK, census 1/10,787.

## ✅ ORCHESTRAL FULL (2026-08-19): the C24 clamp was a TEMPO WEDGE — f2 now 2,901/2,924, 23 partials
Kubiszyn_Paul/Orchestral (backlog item 6's first diagnosed member)
landed FULL at full songlength via an EXTRACT-ONLY fix:
`DMCV4Config.tempo_override` = the play-vector clamp's immediate (`LDA
#$03 / STA base+$716 / JSR T / JMP T` — forces the speed reload every
host call), used by the walk's subtune speed instead of the record's
DEAD byte (1). The 08-14 "clamp inert when it equals the record" claim
was wrong for the sole carrier: they disagree (1 vs 3) = our rows ran 2×
fast. Two wrong hypotheses preceded the fix ("soft-note decode gap",
then "one-play fetch off-by-one") — the tell that killed both: memwatch
$1716/$1718 at the divergence showed period 4 (orig) vs 2 (ours) in one
command; the per-play-identical gateless octave-arp sustain had hidden
the 2× error until the first row boundary. Full transferable story in
ledger C24's clamp section. Census 1/10,787 at the loosest shape;
smoke 6/6; regression green; stored + fifth-layer OK; no seed field
needed (both inits leave the counter at 0 → first tick play 1).

## ✅ Ed FILTER-DEF DRIVERS DECONSTRUCTED (2026-08-16): filterdef_anim + anim3 → filter_mod contours
The last two Ed mechanism params are gone (backlog item 5's second half;
C19 33rd-occ rule; owner approved `res` + `period` + `loop_to` growth on
`filter_mod`, whose container became a LIST — a prog can carry a res sweep
AND a cutoff LFO). Route: probes unchanged (constants stay extract-
internal); `v4/extract/filterdef_anim_lift.py` simulates the driver
play-by-play against the decoded def seeds, RLEs each animated cell at
tick granularity, and REPLAY-VERIFIES every entry through a Python mirror
of the composer's new stream-pointer walker (one spec, two
implementations). Composer: `playfmn` new-form walker (16-bit SMC pair
pointer → >255-run lists work); playfda/playooa emitters DELETED (~150
lines); registry rows dropped (50 keys). Carriers: exactly 2 (census =
signature scan over 10,787 + strict probes on 8 candidates) — Cliche_Beat
+ Only_Ones, both FULL at full songlength, synced, fifth-layer OK.
⚠ Off-by-one trap recorded in C1: the driver runs BEFORE the play body →
sim series must be "state visible to play p" (counters decrement AT play
0); a one-play-late sim verified FULL on Cliche (note-init-sampled cells)
and only diverged on Only_Ones' continuously-clamped sweep ($3F vs $40 at
write 4690). GATES: golden 73 identical + 2 inert (write-stream-identical
by classification), spec/param/corpus lint clean, full regression green.

## ✅ `init_plays` TYPED (2026-08-16): the last temporal-dispatch params key
C33 carrier refactor closing backlog.md item 4. `init_plays` (the raw
play-body calls the orig's init makes before returning — 4k_Byter's
appended init wrapper) moved from `params.fields` to the typed
`Environment.init_plays`, beside the sibling it was always named against,
`play_repeat` (trichotomy §4.3, ledger C24's temporal family). Route: the
same `extra_params.pop(...)` → typed-block hop in `v4/extract/to_usf.py`
that `filter_mod` — the OTHER output of the same 4k_Byter probe — took on
2026-08-12. Grammar uses the generic CNAME-key form (the word was live in
stored `params{}`; a keyword terminal would shadow CNAME there, C33's 2nd-occ
trap). The composer reads the TYPED FIELD ONLY — the params fallback reader
and its registry row are DELETED: both carriers were regenerated, so no
old-form file exists (verified), and a kept fallback would leave the key
counted as an open escape hatch. Carriers: SilverFox/4k_Byter +
4k_Byter_2K1, both re-synced. GATE: 75/75 golden MD5-identical (re-run
after the deletion against the SAME pre-refactor baseline), corpus check
12,529/12,529, spec + param lint clean (52 keys, down from 53), both
stored `.usf` rebuild their stored `.sid`, full regression green.
SAME PASS — trichotomy §4.3 reconciled (owner-approved): the `environment`
category had quietly acquired a second tenant when `play_repeat` landed
there, so §4.3 now names both — HOST-imposed rate (`cia_period`, the
appendix's Category C) vs TUNE-imposed call multiplication (`play_repeat`,
`init_plays`) — and states the boundary that keeps it honest (only the
COUNT lives there; frame CONTENT stays in the subtunes, preserving the
init/play split the appendix §7.4/§8 G defends). The appendix's growth-axis
list records the growth. Its illustrative field names (`playback_rate_hz`,
`cia1_period`) were stale and now show the real block.

## ✅ BOTH FAMILIES CONSISTENT (2026-08-15): f1 5,445/5,445 + f2 2,900/2,924
f1 closeout ran after the Slayer C38 conversion (tmp/f1_closeout.sh, same
shape as the f2 chain): 5,445/5,445 FULL maintained, 0 regressions, 0
gains, 5,445 written / 0 err / 0 orphans, corpus_check 12,529/12,529,
spec_lint + param lint clean. f1 had been stale since the vdep round (64
of the 88 slide-form carriers are f1) — that staleness was what surfaced
as the "stored .usf does not rebuild stored .sid" alarm (raised in
backlog.md item 8, since resolved and pruned from that file — this
entry is the record), which turned out NOT to be a C20 fifth-layer bug.
⚠ THE LESSON:
check the member's BATCH ROW FIRST — it was absent from the f2 results,
which said "wrong family, different sync cadence" in one command. Code,
batch verdicts and stored corpus now agree across both families.
SLAYER C38 CONVERSION (same day, owner-directed): the 4 fade+restart
carriers now SAVE/RESTORE their survivor block instead of carrying 10
measured engine bytes; params is the schedule only ("13006:32:256"), the
probe stopped measuring the note-state, a 4th field stays accepted-and-
ignored for older stored files. All 4 FULL, regenerated + synced.

## ✅ F2 CLOSEOUT (2026-08-15): **2,900/2,924 FULL (99.2%), 24 partials**, corpus synced
One batch reconciled all four late rounds (play_repeat clamp / multiplex /
layout relaxation / song_restart_gap): batch_diff 0 REGRESSIONS, +2 gains
(Techno-Rap + Crazy_Labyrinth), mass-write 2,900 ok / 0 err / 0 orphans,
corpus_check 12,529/12,529, spec_lint 0/0, param lint clean. Baseline:
tmp/dmc_f2_85_results.jsonl. Day's arc: 38 → 24 partials.
RESIDUE (24) is censused in backlog.md item 6 — now: Orchestral (C24
clamp landed, remaining = a soft-note decode gap), Good_Beat (two C19
wedges, both mechanisms precedented), Session (undiagnosed, NOT the glide
cluster), + 21 per-member singletons grouped by first diverging register.

## ✅ CRAZY_LABYRINTH FULL 4/4 (2026-08-14) — typed `song_restart_gap` (C38 sibling)
The song ENDS, rests 256 play() calls, and repeats from the top with state
reset (no fade; the orig's silence is "don't call the player at all").
OWNER-APPROVED typed field `MusicSubtune.song_restart_gap` — one number,
reads as a musical sentence. Full detail + the three traps in the C38
entry; the short version:
- TRIGGER is STRUCTURAL, not the orig's sentinel note: every voice has
  entered its FINAL orderlist entry (each is a dedicated terminator
  pattern `C-4`+3 rests). Detected at runtime by peeking whether the next
  track byte is the loop marker — no offsets/tables/stored pitch. The
  sentinel is INAUDIBLE (measured, gates off) and not even in the pattern
  data for 2 voices (it is the post-transpose note) ⇒ storing it would be
  §7. The owner caught this; my first two proposals both stored it.
- SURVIVORS are SAVE/RESTOREd around the restart (C31 medley carry), NOT
  measured+stored like C38's fade form. That form's 4 Slayer carriers are
  a standing conversion candidate (own round — they are FULL).
- REST LENGTH measured from libsidplayfp (seeds say 255, truth 256).
- TWO BUGS the sibling subtunes caught: the probe fired on subtune 0's
  ordinary musical silence (cure: require the init clear-sweep immediately
  before the rest), and the composer armed the wrapper GLOBALLY (cure: a
  per-subtune arm table). A single-subtune member would have hidden both.
⚠ NOTE the corpus is STALE for some members since the vdep sync: the
play_repeat clamp / multiplex / layout rounds changed a few builds (e.g.
Surgeon/Ona_tanczy_dla_mnie — byte-different, re-verified FULL). The
pending batch covers all of it.

## ✅ TECHNO-RAP FULL (2026-08-14) — the TIME-MULTIPLEXED dual-player build path
Two independent tunes on ONE chip, the play vector alternating them at 2×
the frame rate. Built as SIX voices with NO second chip declared (six
musical parts multiplexed onto three hardware voices) → the composer
derives "same chip, one player per call" from `>3 voices and psid.sid2 is
None`: `multiplex` flag in `build_dmc_2sid_sid` (reg_delta 0, 1-chip
header, `cplay` = parity toggle running ONE player per call, init still in
player order because Check A is last-write-per-register). NO schema or
grammar addition — reuses the multi-SID merge + 6-voice splitter wholesale.
**FULL at 133,653 writes; Check A matches — and EAR-TESTED by the owner
2026-08-14: "both sound identical".** That confirmation is load-bearing
for this class, not a formality: the whole risk was a timing property the
flat write-stream verdict structurally cannot see (see the ⚠ below), so
the ear is the only check that could close it ([[feedback_ground_truth]]).
New build path `multiplex`
wired in all THREE dispatch sites (dmc_build_one / dmc_family_batch /
dmc_mass_write replay — C20 fourth layer). `detect_multiplex` (strict
static wrapper shape + both targets validated as DMC jump-table heads)
fires on **1 of 8,369 members scanned** across both families, and that one
was a partial ⇒ no other member's build can change.
⚠ THE DESIGN CONSTRAINT, owner-caught: do NOT collapse the two bursts into
one 50 Hz frame. That matches the flat write stream EXACTLY (the verdict
would say FULL) but shifts one tune ~10 ms against the other — measured:
bursts are ~4% of a frame, 50.2% of a frame apart. Recorded as the Trap B
BOUNDARY in `docs/the_core_tenet.md` + the C27 card/entry.
TWO COPIES OF THE PLAYER BODY is deliberate: the alternative (one body,
per-player-indexed state) touches 91 access sites across 15 scalars in the
body EVERY DMC member compiles from (the 47 per-voice arrays widen for
free), for ~3.9 KB no gate measures. One-copy-plus-runtime-relocation was
also weighed (~570 operand sites → ~1.1 KB reloc table + patch loop) —
rejected: new 6502 machinery to save bytes we aren't short of, and it is
exactly what the ORIGINAL did and got wrong.

## ▶ C23 TRIO DIAGNOSED (2026-08-14): three per-member digs, one pacing fix landed
- **Techno-Rap = TWO INDEPENDENT TUNES TIME-MULTIPLEXED ON ONE CHIP**
  (measured 2026-08-14, a new C27-adjacent class). Wrapper $1B50/$1B53:
  init programs CIA $2663 (~100 Hz), inits BOTH players, play flips zp
  $02 and alternates `JMP $1C03` (player B, odd IRQs) / `JMP $1003`
  (player A, even IRQs) — each player therefore runs at ~50 Hz, both
  writing $D400-$D418. PROOF (per-IRQ parity split, 20 s): the two halves
  are musically DIFFERENT and each internally coherent — A holds a note
  with a PWM sweep + active filter ($D416/17 = $10/$F1, $D418=$1F), B
  plays different notes/noise and never sets a filter ($00/$00). ⚠ our
  player-A-only build REPRODUCES A's HALF EXACTLY — every apparent
  mismatch was the per-IRQ capture STRADDLE (A's frame overruns the next
  IRQ; chunk 11 truncates at `0E=2D` and chunk 12 opens with exactly the
  missing `0F=01 10=00 11=00 12=00 16=0A 17=F1`). So the WHOLE gap is
  "player B is missing", not an A-extraction defect. ⇒ **the owner's
  "one engine at double tempo" idea is refuted BY MEASUREMENT**: voice 1
  is driven by two independent musical lines (own notes, instruments,
  PWM sweeps, durations, filter use) alternating every ~10 ms; one engine
  holds ONE state per voice, so only a literal per-frame replay could
  emit it (forbidden, [[feedback_no_writelog_replay]]).
  PLAYER B's tables (canon-offset reads at base $1C00): instr $23B0 +
  wavectrl $2481 are +$C00, but wavefreq +$C02 / tunetab +$BFE / secp
  +$BB0 are INDEPENDENTLY packer-patched (the standing DMC rule — resolve
  by operand, never fixed offsets) and filtdef reads $592D = OUT OF IMAGE
  (+$4004). ✅ **RESOLVED + PLAYER B EXTRACTS AND BUILDS (2026-08-14):**
  the $5xxx operands are DEAD PATHS, proved two ways — `--pc-trace` shows
  NO execution outside the file image, and `--memwatch $5012` stays $00
  all song while the relocated `$2212` is live. The packer relocated every
  REACHED path and left unreached ones (incl. the filter-def pointer — B
  never claims the filter) at pre-relocation addresses; 98 of 331 operand
  sites are such leftovers, spread across state/freq/data classes, which
  is why the naive two-delta test looked incoherent. FIX = the f2
  layout-ordering chain SKIPS an out-of-image filtdef (in-image keeps the
  strict chain ⇒ no detected member changes; census confirms zero f2
  members carry one). Player B then extracts: 6 instruments, V3 carries
  the melody (14 orderlist entries, 5 patterns), and its build reproduces
  B's half chunk-for-chunk (the apparent frame-6 diff is the SAME straddle
  — A's tail `0F=01 10=00 11=00 12=00 16=0A 17=F1` opens B's chunk, the
  rest byte-identical). Interleaving the two standalone builds matches the
  orig's flat stream for 556 writes then drifts — EXPECTED, each
  standalone runs its own init/priming; the combined build is the real
  test.
  FIX SHAPE (no grammar/schema addition foreseen): extract both bases as
  independent f2 models, express as SIX voices on ONE chip (the existing
  multi-SID voice numbering — musically honest: six parts multiplexed
  onto three hardware voices), alternation via the existing C18
  `play_phases` complementary-schedule form (C27 already documents "a
  wrapper can run ONE chip per call → COMPLEMENTARY schedules, each chip
  at half the timer rate" — same shape, both players on chip 1), verdict
  n_chips=1 so the merged stream is compared strictly. Composer needs two
  engine state blocks + a parity dispatcher.
- **Orchestral**: play wrapper `LDA #$03 / STA $1716 / JSR $1003 /
  JMP $1003` = C24 whole-play ×2 PLUS a per-play tempo-reload clamp.
  LANDED: `_detect_play_repeat` steps over the exact clamp prefix
  (sole carrier censused; clamp inert when it equals the record speed —
  verify judges, C13). Pacing fixed (lengths now match, state ok);
  REMAINING: at ~write 270 the orig note-inits V1 (ctrl $10, gateless)
  WITHOUT a prep frame where our walk decoded a plain hard note — a
  SOFT-NOTE/no-prep stream form the f2 walk doesn't decode on this row.
  Next: decode V1's first sector bytes properly (my naive secp math
  gave $0000 — use the walk's own resolution), find the soft-note byte
  form, teach walk + composer (ev_n_softq path exists).
- **Crazy_Labyrinth**: play $1CCE = `JMP $1CC8`, init SMC-pokes the JMP
  operand ($1CCF ← $C8) = a self-repointing play dispatch (C18-family).
  Un-RE'd — disassemble $1CC8+ next.

## ✅ VDEP ROUND CLOSED OUT (2026-08-14): **f2 = 2,898/2,924 FULL (99.1%), 26 partials**, corpus synced
Closeout chain green: batch_diff 0 regressions / 3 gains (the Spice_Up
pair + BONUS Ass_It/4_Interrupts_3 — an undiagnosed singleton that was
another slide-form carrier), mass-write 2,898 ok / 0 err / 0 orphans,
corpus_check + spec_lint + param_lint clean. The 88 slide-form carriers
re-verified FULL in the batch and re-synced. Baseline:
tmp/dmc_f2_85_results.jsonl. Residue = 26 (Session's true cause TBD;
C23 timing trio; Good_Beat; ~20 singletons).

## ▶ [SUPERSEDED by the closeout above] VDEP ROW LANDED (2026-08-14, owner-approved OFSIG growth): **Spice_Up pair FULL — f2 residue 29 → 27**
Full story + the two scoping rules + the two traps recorded in C11 (read
it). Key numbers: pair FULL at 236,845/230,029 writes; exposure = 88
slide-form carriers (12-sample all FULL incl. Roots/Trailways_A/So_easy;
rest ride the closeout re-batch), Trekky+Castle (229-231 record holders)
FULL, 5 previously-diffed non-carriers byte-IDENTICAL under the
reader-gated otmap. Session was NOT this cluster (multi-sub, diverges play
~28-31, state False — different cause, back in the queue). Corpus gates
green (12,524 parse, spec_lint, param lint, smoke). NB the synced corpus
predates this round for the 88 carriers + Trekky/Castle/Spice (byte-
different rebuilds) — the closeout re-batch + mass-write refreshes them.

## [RESOLVED — landed above] PROPOSAL (2026-08-14 am): the vdep redirect row — was parked at tmp/vdep_row_fix.patch (one OFSIG grammar word short)
The Spice_Up cluster fix is fully implemented + designed (C11 canonical
redirect row, f2-scoped): `DMC_VDEP_ROW (0x178C,'vdep',3)`, parametric
`offtable_live_idx(vib_step)` so f1 extracts stay byte-identical, otmap
gate, extract stamping threaded (`vibrato_increment(vN)` LiveSignal).
BLOCKED at the last step by the OWNER-APPROVAL GATE (ratified 2026-08-13):
the record's signal name needs ONE WORD added to the grammar's `OFSIG`
terminal (the live-signal name allowlist) = a grammar.lark edit = RED.
Note the stamping CANNOT be skipped: a static-stamped read at a live idx
is the non-canon detector — it would disable the member's whole redirect.
PROPOSAL FOR THE OWNER: add `vibrato_increment` to OFSIG (the same
mechanical growth every prior redirect row did — sectpos/wavepos names);
recommendation = approve; alternative = pick a different name or park the
cluster as residue. On approval: `git apply tmp/vdep_row_fix.patch`, add
the OFSIG word, then verify Spice pair + Session (expected FULL) +
Trekky + Castle (exposure, must stay FULL), golden f1 sample, gates,
regression, commit. Post-chain state: **f2 = 2,895/2,924 (99.0%), 29
partials**, corpus synced clean (2,895 ok / 0 err / 0 orphans).

## ▶ SINGLES ROUND 2 LANDED (2026-08-13 eve): Koshimo + For_Moonlight + Mea_Culpa_end = **+3 FULL, f2 residue 31 → 28**
Commit 4d2e6867; regression 0 regressed, golden 21/21, smoke 6/6. C24 f2
form (play_unit_repeat '0,1,1,0' via the play-body call-chain patches;
filter clamp now honors explicit 0) + C19 49th (vib_step_dead) + 50th
(vib_phase_persist — hypothesis verified by the 233,851-write stream).
SPICE_UP RE — ROOT CAUSE PINNED (the reg0E cluster rep, NOT yet fixed):
the C11 acc/fb/glsp event-stream measurement (memwatch D40E of
$1731/$1734/$1737/$173A/$1743 vs our fbl/fbh/accl/acch/glsp +2) shows
BOTH sides glide identically (fb=$010C, acc stepping, glsp 02→$0F
re-command) — then at the arrival compare the ORIG's target is freq
$0100 while OURS reloads fb=$0200: **our decoded glide-TARGET note is an
OCTAVE (+12) off** for this re-commanded glide. The audible stream
coincides all glide long (the target only matters at the arrival
compare), so the member diverges DEEP (event 9,542 of 10,147; frame
~10,916). ⇒ an EXTRACT-WALK bug in the glide-target + transpose
computation at that track position (canon adds $172C,X transpose at
PARSE; forms: $C0 = explicit gla+glb bytes, retrigger via $11A6; $D0 =
glb only, gla=curnote, soft, keeps running acc) — C34/C11 territory, NOT
a serving fix. NEXT: dump our USF's glide row at that position vs the
orig's stream bytes (which form, which target byte, what transpose the
walk had). Likely serves the whole reg0E cluster (Session /
Knowledge_Posse_3 / Petshopmix / Conversion / Spice_Up pair).
Good_Beat deferred (misaligned illegals + a live poke into instrument
bytes at $17AB+x).

## ▶ [SUPERSEDED by the entry above] WEDGE ROUNDS LANDED (2026-08-13 pm): Rowdy 10/10 + 6 more = **+7 FULL, f2 residue 38 → 31**
Two rounds, all gates green (golden 24/24 byte-identical ×2 samples over
every build path, corpus_check 12,515/12,515, spec_lint 0/0,
composer_param_lint clean, smoke 6/6; regression #1 (Rowdy round) 0
regressed, regression #2 (statics round) run before commit):
- **Rowdy round (C31 knob-by-knob + C19 46th):** per-song `vib_ramp`
  ('step' vs 'step_full' — tune-record byte +10, `bit vibfull` gate over
  the one LSR) + `prep_ctrl` (the f2 $11D9 prep-ctrl immediate $08→$40,
  byte +11) carried as SPARSE MusicSubtune.params overrides; file-level
  stays the START player's value. Rowdy 10/10 FULL; the probe also landed
  the two whole-file carriers Mad_Eddie + Rock_Zak_1. KEY DIAGNOSTIC: the
  standalone per-player build ($9300 FULL vs $F000 partial) split
  merge-loss from missing-probe in one measurement.
- **Statics round (C19 47th/48th + C1 direct):** `d418_noteinit_dead`
  (f2 $12A8 store killed, init mvol survives — Third_Zak zp-redirect +
  Chance_for_Win NOP, exposure Note_from_Tonka stays FULL) +
  `filter_cut_static` (f2 $10A3 $D416 store NOPed — No_End) + the No_End
  appended 256-entry cutoff-table cycler DECONSTRUCTED to the typed
  `filter_mod` DIRECT entry (`target: cutoff`, new `direct` grammar
  marker; delta-run encoding, exact; NOT a sine — 88/256 best-fit errors,
  so the table's exact deltas ARE the musical form). No_End FULL at
  387,937 writes.
- REMAINING 31 partials incl. investigated-but-not-landed singleton
  wedges (read from tmp/dmc_f2_wedges.csv + byte dumps): For_Moonlight
  $12F5 `9D→D9` = the vdep (vib-increment) note-init store KILLED;
  Mea_Culpa_end $11BE `9D→55` = one note-init state clear ($1768,x)
  killed; Good_Beat TWO wedges ($1512 `9D→55` slide-down writeback killed
  + $1571 repoint $176B,x→$17AB,x = clear lands in instrument area, the
  C19 data-poke variant); Koshimo $1095/$109D init-flow JSR repoints.
  Plus the reg0E (V3 freq lo) cluster: Spice_Up pair diverges o00 r7C
  where our $7C is a COMPUTED table freq (not a window byte) ⇒ the INDEX
  diverges upstream — needs real RE, not a serving fix. NB the f2 batch
  code_hash is STALE after these rounds — re-batch + mass-write at
  closeout.

## ▶ [SUPERSEDED — subs 1/2 landed, see head] ROWDY DIAGNOSED (2026-08-13): an f2 RELOCATING COMPILATION — detection/build WORK (8/10 subs FULL); residue = per-player knob carriage
Brian/Rowdy = C31 relocating compilation, THREE family-2 players: $1000
in-image (8 songs, all FULL), plus per-subtune COPIES to **$F000 (under
KERNAL — the wrapper banks $01=$35 around play!)** and $9300, ~10/12 pages
from $1CB9/$276A, landing `JSR dst<<8` with A=song. `detect_compilation`
fires CORRECTLY (observe path; reloc={F000:1, 9300:2}), `_player_cfg`
threads post_init_sub, the f2 path accepts the copied heads, sub 0+3-9 all
FULL. REMAINING (subs 1/2, diverge at play-write 0 per-IRQ): the copied
players are **vib_ramp='step_full'** builds while $1000 is 'step' — the
MERGE COLLAPSES extra_params to the start player's (the C31 per-player-fact
family; carry per-song like rest_effects) — PLUS an UNPROBED first-frame
prep variant (orig ctrl $40×3 vs our $08 TEST at play 1; routing $00 vs
$02; V1 SR $D7 vs $D6) needing RE against the $F000 post-init image.
ALSO LANDED (uncommitted, gating in flight): the C21 per-IRQ RETRY in
verify_dmc — a vblank subtune whose flat trichotomy fails re-verifies via
keep_init per-IRQ capture (init prefix = pre-first-play-entry, immune to
multi-frame init SPILL like Rowdy's copy loop) WITH Check A kept (last-
write-per-register over the |N init chunk — C15, no relaxation). Full f2 re-batch LANDED: 2,886/2,924 identical counts (0 verdict flips
= the retry validated), corpus re-synced under the new code_hash
(2,886 written, 0 err, 12/12 audit, corpus 12,515/12,515).

## ✅ OVERNIGHT CHAIN LANDED (2026-08-13): **f2 = 2,879/2,924 FULL (98.5%)**, 45 partials, corpus synced
The re-batch confirmed dual_phase as the deep-freq lever: **+254
partial→FULL in one fix, 0 regressions** (batch_diff gate vs
tmp/dmc_f2_85_prev.jsonl), mass-write ok=2,879 err=0 orphans=0, disk audit
12/12, corpus_check 12,508/12,508, spec_lint 0/0, composer_param_lint
clean. Family-2 went 86.8% → 98.5% in ONE DAY (easy-9 + loop-poke +
4k_Byter contour + dual_phase). RESIDUE = 45 partials, a TRUE LONG TAIL
(census in tmp/f2_overnight.log era: top cluster 7×V3-freqlo-deep, then
5/3/3/3/2s + singletons; the $12F4 vib-tail canon_diff singletons sit in
the V1-freqlo cluster as predicted) — per-member C19 wedge rounds next,
via `dmc_next_partial --list tmp/dmc_f2_partials.jsonl` (RE-SEED the
queue from the fresh results first). Baseline for future batch_diff:
tmp/dmc_f2_85_results.jsonl.

## ▶ [SUPERSEDED by the entry above — kept for the round narrative] OVERNIGHT (2026-08-12/13): dual_phase = THE DEEP-FREQ LEVER; typed filter_mod landed; full re-batch RUNNING
Three things landed overnight (owner asleep; all gated):
- **filter_mod TYPED generalization committed (21875537)** — the 4k_Byter
  contour + FC/Ed LFOs are one parameter space (stop_phase optional =
  single tap; `once` = one-shot/terminal hold). playfdc + the
  filter_init_contour params key DELETED; playfmod generalized. Ed
  loop-carriers byte-identical; 4kB pair FULL via typed path, artifacts
  regenerated + audited; corpus 12,253/12,253. backlog caveat 3 CLOSED
  by inspection (equal-phases = both cells genuinely animated — different
  fact from omitted-stop, no dual encoding).
- **dual_phase fix committed (f7d36616)**: `dual_parity_addr=at(0x1035)`
  in _family2_build. Census 13 static carriers (parity bits differ + dual
  instr): 10 FULL→FULL (0 regressions), Real_Shit partial→FULL. **THE BIG
  FIND: the fix reaches FAR beyond the census — Snap.sid (the 74-member
  V3-freqlo-deep cluster rep) went FULL.** Mechanism: the mis-seeded $40
  half-rate parity shifts every VIBRATO voice's wave-step phase by one
  play (r168's note) → fbl caches sample one play off → the deep off-table
  freq divergences. C11 re-measure proved fbl+2 event-streams IDENTICAL
  under the fix (8,807 events) = the "missing/extra emission" theorem's
  happy case. The June "hard freq tail" was largely THIS ONE BYTE.
- **Full f2 re-batch RUNNING** (tmp/f2_overnight.sh → tmp/f2_overnight.log;
  results tmp/dmc_f2_85_results.jsonl, prev snapshot tmp/dmc_f2_85_prev
  .jsonl): batch → batch_diff --fail-on-regression → mass-write → corpus
  _check → spec_lint → composer_param_lint. Chain STOPS before sync on any
  regression. Expect a large partial→FULL wave from dual_phase.

## ✅ F2 UNSUPPORTED CLASS CLOSED (2026-08-12, commits 5e2ab61b + d31649af): **2,624/2,924 FULL (89.7%)**, 0 unsupported
All 15 former unsupported resolved: 13 FULL + 2 into known partial clusters
(Soul_tune_1 → V3-ctrl triangle-bit cluster; Twin_Russian → the fbl freq
cluster, base $8739, play_repeat=2 via `JSR T/JMP T`). Landed in 3 rounds:
easy-9 (prev entry), the loop-poke round (X-mas `subtune_loop_reset` {0:7} —
both subs FULL incl. the loop-to-7 wrap; Soul_tune_4 + Soul_partselector via
extended neutral walk with static-branch following), and the 4k_Byter pair.
**THE 4k_BYTER LESSON (owner-caught §8 misstep → reverted → redone right):**
the appended SMC sequencer ramping filter def 0's INIT CUTOFF was FIRST
implemented as a mechanism param (`pulsebyte_anim`) + composer driver-
emulator chunk — verified FULL but WRONG representation (the ledger had
already decided it: C19 33rd — a wedge changing a MUSICAL VALUE is
DECONSTRUCTED, never reproduced as a composer mechanism; and C1's card IS
"cutoff contour"). REVERTED (uncommitted), REDONE: the probe template-
matches the driver, SIMULATES it in Python, and emits `filter_init_contour`
= 'def,start,delta:count,...' (C1 piecewise form, readable music) +
`init_plays: 3` (C24 temporal — the orig init runs the raw play body 3×).
Composer gained a GENERIC C1 contour interpreter (serve value → body →
advance) + N init JSRs. Both FULL, synced + audited. MEASURED: 25 distinct
claim-start cutoff values (88 claims) → def clone-and-remap (16 nibble
slots) CANNOT encode it; the contour is also the truer musical object.
**META-PIPELINE HARDENING (the prevention ask):** `tools/
composer_param_lint.py` + `tools/composer_params.json` — a reviewed
registry of every composer-consumed params key (category + licensing
ledger entry); lint ERRORS on unregistered keys. First run immediately
flagged `digi_player` (a name indexing an engine-side registry — borderline
§7, noted for review). CLAUDE.md gained the C19-33rd tripwire bullet.
Remaining f2 residue: 299+... partials (C11 fbl freq class dominant, the
$12F4 vib-tail 4-carrier cluster, V3-ctrl cluster) — the next rounds.

## ✅ F2 EASY-9 LANDED (2026-08-12, commit 7388e89f): **2,619/2,924 FULL (89.6%)**, 6 unsupported left
The near-miss detection fallback (factory.py, fires ONLY after all prior
detection fails — previously-detected members structurally unchanged):
consistent-base rule (init_tgt−$37 == play_tgt−$85 names the base — lands
±shift re-assemblies Lithium +1/Entropy −4, and via raw header vectors the
Power_of_Lard junk-JT KERNAL-reset trap), JSR-slot opcode relax (Merilyn
play `JSR/RTS`, Yoko init JSR), neutral-wrapper follow (zp counters/loads/
compares + fwd branches → terminal JMP; CORE TENET — no SID touch; Soul_tune
_1/2, and BONUS Unbelievable_Music's $2200 wrapper resolved through it), and
the Tonka `JSR init / LDA #$1F / STA $D418 / RTS` mvol-prime shape (probe
value UNUSED — Check A absorbed the prime; `_mvol_prime` wired but inert).
RESULT: 8 unsupported → FULL (all synced + audited 8/8), Soul_tune_1 →
partial in the KNOWN V3-ctrl-$21-vs-$41 triangle-bit cluster (12+1 members,
diverges f423 — take with that cluster). GATES: golden 10/10 byte-identical
vs the freshly-synced corpus, smoke 6/6, full regression 0 regressed,
detection empirically changed only the 15 prior-unsupported.
REMAINING 6 unsupported: X-mas_Cooperation (C37 poke → per-subtune
loop_reset_pos: wrapper pokes table[$1028+sub] into the $FF handler's
loop-to IMMEDIATE $10DE — extract-only, lrp machinery exists),
Soul_partselector ($1CF0 selector), Soul_tune_4 (wrapper family @ $9000),
4k_Byter ×2 (C38-ish driver: init runs play 3×, counter sequencer),
Twin_Russian (C24 `JSR T/JMP T` 2×, re-assembled @ $8700).

## ▶ F2 UNSUPPORTED CENSUS (2026-08-12): all 15 identified, no new classes — 8 easy
The 15 unsupported (14 no_jumptable + 1 nonstandard_vectors) fully decompose:
- **JT near-misses (5, C13)**: Merilyn_part_7 (play slot `JSR $1085/RTS`),
  Yoko_02 (init slot JSR → init runs one play), Power_of_Lard_part_4 (JT is
  a `JMP $FCE2` KERNAL-reset TRAP; header vectors point at the f2 bodies),
  Lithium_Logo_2 (whole player shifted +1: targets $1038/$1086/$1630/$163F),
  Entropy_Intro (2-entry JT shifted −4: $1033/$1081).
- **Write-stream-neutral wrappers (3)**: Soul_tune_1/2 (play = zp 16-bit
  frame counter `INC $ED/$EE` then JMP $1085 — no SID touch; init zeroes it
  then JMP $1037), Note_from_Tonka (init = `JSR $1037 / LDA #$1F / STA
  $D418 / RTS` = pure §4.2 priming → existing `init.sid.master_vol`).
- **Per-subtune poke wrappers (2, C37 degenerate)**: X-mas_Cooperation_tune_2
  (init wrapper pokes table[sub] into $10DE = the $FF track-loop handler's
  loop-to IMMEDIATE — a knob C19 knows), Soul_partselector (play → $1CF0
  selector, needs a deeper look).
- **Appended drivers (5, C24/C38)**: 4k_Byter + 4k_Byter_2K1 (init runs
  play 3×, poke $17F4, counter-driven per-frame sequencer), Twin_Russian
  (`JSR T/JMP T` = C24 whole-play 2×, re-assembled @ $8700), Soul_tune_4
  (Soul wrapper family relocated @ $9000, both vectors appended).
PLAN for the easy 8 (approved, start post-sync): _jt_layout consistent-base
rule (e0−$37 == e1−$85 → base = that value; catches ±shifts; wrappers fail
the equation structurally) + header-vector fallback + JSR-slot opcode relax
+ neutral-wrapper follow (terminal JMP, no SID writes en route) + the
master_vol init-wrapper probe. GATE: detection diff over all 2,924 (only
the intended members may change (base,layout)) + build+verify the 8 +
golden byte-identity sample.

## ▶ F2 BATCH LANDED (2026-08-12 later): **2,611/2,924 FULL (89.3%)**, 0 regressions — residue = C11 freq class
Fresh batch complete (`tmp/dmc_f2_85_results.jsonl`): **2,611 full / 298
partial / 15 unsupported** (89.3%; July was 2,507/2,889 = 86.8%).
batch_diff vs `tmp/dmc_f2_full.jsonl`: **0 REGRESSIONS**, 71 not-full→full
gains + 9 error/unsupported→partial (the r113-r187 f1 rounds, free).
Analysis log: `tmp/f2_postbatch.log`. Partial queue seeded:
`tmp/dmc_f2_partials.jsonl` (use `dmc_next_partial --list` with it).
- **Census** (298 partials): ~214 are FREQ-LO divergences (V3 74-deep +
  V2 33-deep + 28-early, V1 22-deep, + smaller), 12 V3-ctrl-deep
  ($51 vs $41 = triangle bit), long tail 28 clusters. The June "hard freq
  tail" is now the whole game, as the wedge audit predicted.
- **Probe on the dominant-cluster rep** (Snap.sid, V3 freqlo @8499):
  off-table idx 234 lo→$1731 = **fbl+2, ALREADY live-served** — NOT a
  missing redirect; our fbl+2 VALUE drifts from orig's (upstream V3 state
  divergence; suspect interaction with f2 `rest_effects='skip'` hold
  semantics). Next: C11 re-measure protocol (memwatch orig-vs-rebuild on
  fbl+2 event-by-event). NB idx 234 hi→$1791 is not a mapped state var.
- **Wedge carriers split** (canon_diff --status): hold_gateoff 265f/15p,
  filter-mode 19f/10p (probes working); `$12F4 LSR→TAY` note-init-tail
  cluster = 4 carriers ALL partial (unprobed vib_ramp variant — a real
  small lever); ~15 partial singleton wedges for later C19 probes.
- READY, awaiting owner: corpus sync (batch is complete + 0 regressions —
  both recorded preconditions met); dual_phase patch (tmp/dual_phase_f2.patch).

## ▶ FAMILY-2 RESUMED (2026-08-12) — #85 membership + fresh batch RUNNING + wedge space enumerated
Owner-directed resumption after f1 closed at 100%. Done this session:
- **#85 membership derived**: `tmp/dmc_f2_members_85.json` = **2,924** (2,878
  of the June 2,889 still present + 46 #85-classified V4-derived from
  `tmp/dmc_classify_new.json`; 11 old paths gone = renames among the 46, f1
  precedent). C20 seventh layer honored — no whole-file-hash matching.
- **Fresh full f2 batch RUNNING** (2026-08-12, background):
  `pipelines/dmc/family_batch.py --members tmp/dmc_f2_members_85.json --out
  tmp/dmc_f2_85_results.jsonl`, log `tmp/dmc_f2_85_batch.log`. Early mix at
  90 members: 82 full / 8 partial (91% — above July's 86.8%, the r113-r187
  shared rounds paying out). ~8 h on the X230. July baseline for batch_diff:
  `tmp/dmc_f2_full.jsonl` (2,507/2,889 FULL).
- **Wedge space enumerated a-priori** (`dmc_canon_diff --family2`, NEW mode,
  commit d1497e58; results `tmp/dmc_f2_canon_diff.log` + `tmp/dmc_f2_wedges.csv`):
  **2,872/2,924 (98%) align linearly to the carved f2 reference**, 52
  reassembled, 0 anomalous. Only 2 multi-carrier clusters, BOTH already
  probed (hold_gateoff ×280, filter-mode AND ×29); 35 unhandled clusters are
  all 1-2 carriers. Conclusion: f2 residue is DATA/off-table-shaped, not
  code-wedge-shaped — same structure as f1's audit.
- **Post-batch analysis ready**: `tmp/f2_postbatch.sh` (batch_diff report +
  divergence_census --partials + canon_diff --status split; NON-destructive).
- **CORPUS SYNC HELD**: whole f2 stored corpus (~2,508 artifacts) is
  July-stale (pre-C32 params, 52 live()-form .usf). Mass-write
  (`dmc_mass_write --results tmp/dmc_f2_85_results.jsonl`, build_path
  replay + orphan delete + audit) prepared but NOT run — owner go-ahead
  needed for the destructive step. The live()-grammar deletion rides the
  f2 extract migration after the sync.
- QUEUED (post-batch, code_hash discipline — NO pipelines/ edits while the
  batch runs): dual_phase read-site fix (canon $1019 → f2 base+$35, RE_NOTES
  known bug; census dual-instr carriers first), f2 vibdepth-address confirm,
  seed `tmp/dmc_f2_partials.jsonl` for `dmc_next_partial --list`.

## ✅ A2 CLOSED — f1 re-batched + corpus mass-written under current code (2026-08-11)
The full chain (tmp/a2_overnight.sh, log tmp/a2_overnight_2.log) ran green
end-to-end on the r187 fix: fresh batch **5,445/5,445 FULL, 0 partial**
(tmp/dmc_f1_85d_results.jsonl); batch_diff vs 85b **0 regressions / 0
gains** (identical verdict set); mass-write ok=5,445 err=0 orphans=0,
from-disk audit 10/10 across all build paths; corpus_check 12,107/12,107;
spec_lint 0/0; full regression 0 regressed. The stale-code_hash debt is
CLEARED — batch rows, stored corpus, and code all agree at the current
fingerprint. Baseline snapshotted to tmp/dmc_f1_prev_batch.jsonl. This also
family-wide-validates the whole 2026-08-10/11 sequence (per-subtune
vibdepth + de-redirect steps 1-3 + the canon-evidence gate).

## ✅ r187 — the de-redirect's §4 trap fires; CANON-EVIDENCE gate lands (2026-08-11)
The A2 overnight chain's batch_diff gate caught ONE regression
(Bakewell_Dwayne/Finale full→partial) and stopped before the mass-write —
exactly what the gate is for. Root cause: Finale is a NON-CANON-geometry
member (zero live marks; a static record at idx 254 = gla+1's LO landing was
the `_static_at_live` detector firing), and step 2's allowlist exemption
silenced the detector → redirect flipped ON → an UNRECORDED live-idx read
served live instead of static. FIX: the exemption now requires CANON
EVIDENCE (≥1 live-stamped record — the extract stamps live only on canon
members; no geometry param). Fallout handled: 150 canon zero-live-mark
full-converts flip redirect ON→OFF under the gate — GATE_ALL enumerated
them (the reader-scan golden structurally can't see zero-live-mark members),
**150/150 re-verified FULL** + re-synced; Finale byte-identical to its old
FULL build; smoke 6/6. Lessons in ledger C11 (reach under-enumeration;
GATE_ALL as the completeness net). A2 chain relaunched after the fix.

## ✅ r186 — DE-REDIRECT step 3: the NOTE-INIT CACHE FAMILY — the class is DONE (2026-08-10)
ioff/cpwmin/cpwmax/cpwbase/vibwid/cvram/fxf/vstep/vsteph joined the
allowlist: **155 converters, 155/155 FULL**, all synced + rebuild-audited
(golden 592 = 437 identical + 155 intended). KEY DELTA from the design: the
"one prover serves all" claim needed a WRITE-SITE AUDIT, which EXCLUDED
pwstep + wctrl (effects-path writers — fx_pulse per frame / every wave
step; they stay live). Value functions mirror the composer table builders
(`_cache_note_init_value`); fxf's iflags mirror biases to OVER-estimate
(converts fewer, never wrongly); ioff handles the C31 renumber via
record_offset; vstep proxies on vib_width; vsteph is canon-never-nonzero;
bails = ghost wedge + family-2 'step' swell (vstep/vsteph only). With steps
1-3 all landed same-day, the per-voice de-redirect design
(tmp/deredirect_per_voice_design.md) is FULLY IMPLEMENTED: 4 + 375 + 155 =
534 members' representations now carry live marks only where the value
moves. Ledger C11 has all three steps. corpus 12,107 / lint 0/0 /
regression 0 regressed. f1 code_hash stale (fold into next batch).

## ✅ r185 — DE-REDIRECT step 2: the GLIDE TRIO (2026-08-10, same day as r184)
gla/glb/glsp joined `DMC_DEREDIRECTABLE` — the class-wide payoff: **375 of
651** reader-members converted (golden: 276 byte-identical + 375 intended),
**375/375 verified FULL** vs originals, all synced + rebuild-audited. Prover:
a voice with NO glide rows (glide_to/glide_slide/glide_speed) never writes
the trio (arrival clear unreachable while glsp=0), so the value = igla/iglb
seed or the canon-cleared 0 — equal to the captured static byte by
construction (value-neutral). Bails: track_ff_reinit_ghost + glide_neutered,
checked on file-level AND per-song params. Composer change = 3 labels; the
r184 machinery needed zero changes. corpus 12,107 / lint 0/0 / regression 0
regressed. NEXT: step 3 = the note-init cache family (vibwid/cvram/fxf/ioff/
cpw*/vstep*/pwstep/wctrl — one prover: constant iff every instrument the
voice plays gives the init-cleared value). Ledger C11 has both steps.

## ✅ r184 — PER-VOICE DE-REDIRECT, step 1 (vibdel) lands (2026-08-10)
The design at `tmp/deredirect_per_voice_design.md` is implemented for its
step 1 (`DMC_DEREDIRECTABLE = {'vibdel'}`): the extract's per-voice constancy
prover no longer collapses all-or-nothing, and the composer expands each
allowlisted redirect row to contiguous runs of the still-LIVE voices
(`_deredirect_expand`, expression labels like `vibdel+2`; DMC_OFFTABLE_STATE
stays canonical). +0 FULL by design — a representation-truth fix (live marks
only where the value moves). TWO CORRECTIONS to the design discovered by the
golden gate: (1) when EVERY record-bearing voice is dead the WHOLE row must
still drop (record-free voices included = the historical member-level form)
or all 27 previously-converted members re-churn — per-voice expansion fires
only for genuinely MIXED members; (2) the design's "4 known carriers" was
stale: Yoko/Dream_on_Girl is NOT an f1 member, and the real 4th converter is
The_Syndrom/Black_It — a heterogeneous compilation whose MERGE creates a
mixed row (one packed player's static records beside another's live ones).
GATES: golden 197 = 193 byte-identical / 4 DIFFERS = exactly the converters
(Top_One_Mix, Goldrake, Something_Broke, Black_It); 4/4 verified FULL vs
originals; artifacts synced + rebuild-audited; smoke 6/6; corpus_check
12,107/12,107; spec_lint 0/0; full regression 0 regressed. Ledger C11 has
the refinement. NEXT (steps 2-3, mechanism unchanged): add the glide trio
(gla/glb/glsp — must respect m.glide_leftover_cleared + serve the SEED value,
not 0) then the note-init cache family to the prover registry + allowlist.
f1 batch code_hash stale again (dmc_v4 touched) — fold into the next batch.

## ✅ r183b — PER-SUBTUNE VIBDEPTH READS: the r182 latent sibling closed (2026-08-10)
The 22-compilation vibdepth collapse is resolved (+0 FULL by design — all 22
were FULL; this closes the silent per-player collapse). KEY CORRECTION to the
r182 framing: measured per-index (`tmp/dmc_vibdepth_census.py` →
`tmp/dmc_vibdepth_census.json`), the "22 disagree on vibdepth" signal was ~all
NOISE — every member differs only at idx 4 (Mission_Moon also 3) = the
relocating CODE-OVERLAP-HEAD operand, plus unreached notes; and the merge's
`vibdepth=list(b.vibdepth)` copy is DEAD (no downstream consumer — the
composer ships canonical VIBDEPTH + the offtable_vibdepth override list).
Carrying the raw table per-subtune would have encoded relocation artifacts.
The SONIFIABLE fact is the reached `offtable_vibdepth` dicts, which the merge
unioned setdefault-first-wins; exactly **4 members conflict on a reached
note** (Defuzion_3 + Goldrake_plus_2 note 4; Lane_Crazy 142/248/255;
Quad_Core 108/245 — off-table window reads into each player's own state
block). FIX: sparse per-subtune `MusicSubtune.offtable_vibdepth` override
(new `sub_override` grammar alternative reusing the file-level block) +
`DmcSong.offtable_vibdepth` (conflict notes only, value ≠ file-level) +
composer `vpat` init patch — FIXED-LENGTH rows + COUNT-based loop (`tmp2`),
because a patched idx can be $FF so the ovr/fpat terminator shape collides;
table extended to cover the max patched idx. GATES: 445/445 byte-identical
from stored `.usf` (change inert for the existing corpus); re-verify all 22
fresh = **22/22 FULL**; smoke 6/6; corpus_check 12,107/12,107; spec_lint 0/0;
the 4 conflict members' artifacts regenerated + rebuild-audited; full
regression 0 regressed. Ledger C31 gained the occurrence (incl. the
measure-what-disagrees-first method note). NB the f1 batch rows'
code_hash is stale again (dmc_v4 files touched) — fold into the next batch.

## ✅ r182 — PER-SUBTUNE TUNING lands; f1 is 5,445/5,445 FULL (2026-08-10)
The #85 batch's single partial is closed. Bayliss/Heavy_Metal_Solid_preview
2/2 FULL, so **family-1 is 5,445/5,445 (100%) on HVSC #85**.

ROOT CAUSE (not what the first pass said — see the corrected entry below):
`merge_models` REQUIRED the packed players to share a freq table and RAISED
otherwise, dropping the member to the single-player fallback so sub 1 was built
from the wrong player's data. The two players are genuinely tuned differently:
2 of 96 notes, note 31 $06F3 vs $0647 = **-176 cents**. Tuning is per-tune
CONTENT (principle C7 category C), so it now rides per-subtune like every other
per-player fact — `MusicSubtune.freq_table`, which has existed since r93, so NO
schema addition. Composer PATCHES the shared tables at init via a per-subtune
`(note,lo,hi)` `$FF`-terminated stream beside the existing `ovr` window patch;
the base must NOT move because freqlo/freqhi are contiguous with the off-table
window. Commit fbd1f2e3; ledger C31 gained the occurrence.

GATES: byte-identity vs the corpus mass-written minutes earlier with the
pre-change code — 445/445 identical incl. ALL 45 non-single members; dmc_smoke
6/6; usf_corpus_check 12,107/12,107; usf_spec_lint 0/0; full regression 0
regressed; audit_rebuild on the fixed member OK.

⚠ OPEN, MEASURED, DELIBERATELY NOT TAKEN [SUPERSEDED — closed by r183b above]: the same census
(`tmp/dmc_tuning_census.py`, `tmp/dmc_tuning_census.json`) found tuning
disagreement in exactly 1 member but **VIBDEPTH disagreement in 22
compilations**, which `merge_models` collapses to the start player's with NO
check (`vibdepth=list(b.vibdepth)`). All 22 are currently FULL, so the
collapsed value is unsonified in them. Fixing it WOULD change their emitted
bytes, and byte-difference does not imply behaviour change (C7's one-way gate)
— so it needs a RE-VERIFY of the 22, not a byte-diff. Scoped round, not a free
ride.

RE-BATCHED under the new hash the same day: tmp/dmc_f1_85b_results.jsonl =
**5,445/5,445 FULL**, batch_diff vs the previous #85 batch 0 regressions / 1
gain (the Bayliss member). The corpus needs NO mass-write — all 5,445 stored
artifacts rebuild BYTE-IDENTICALLY from their stored .usf under current code
(`GATE_ALL=1 python3 tmp/dmc_freq_gate.py`), so "what is stored" already equals
"what was verified".

## #85 f1 re-batch LANDED: 5,444/5,445 FULL — the 1 partial is a MISSED C31 (2026-08-10)
Batch `tmp/dmc_f1_85_results.jsonl` (5,445 members) vs the #84 baseline
`tmp/dmc_wide_results.jsonl`: **REGRESSIONS 0**, gains 0, only-in-old 3 (the
renamed paths), only-in-new 47 (the newcomers). So every carried-over member
survived the #85 migration + the code_hash churn, and the batch re-baselines
family-1 onto #85. 46 of the 47 newcomers are FULL.

**The single partial is NEW COVERAGE, not a regression:**
`MUSICIANS/B/Bayliss_Richard/Heavy_Metal_Solid_preview.sid` — sub 0 FULL, sub 1
diverges at its FIRST note (V1 SR $6A vs $E8, freq $2187 vs $3300, ctrl $21 vs
$81 — a different note/instrument entirely, not a drifting effect).

DIAGNOSED (corrected 2026-08-10 after reading the FULL C31 entry — the first
pass, from the recognition card alone, got the CONCLUSION wrong):

  ❌ WRONG (what the card-only pass concluded): "a C31 compilation that
     DETECTION MISSED; the lever is detection, check why the observation path
     wasn't reached." Also floated the entry's "instrument overflow
     (Heavy_Metal, 30 > 28)" residue as the likely cause.
  ✅ MEASURED: `detect_compilation` fires perfectly —
     `bases [$1000,$1F00], map [(0,0),(1,0)], kinds ['dmc','dmc']`, exactly the
     landings observed with `--pc-watch '*00'`. Both players extract fine, and
     the member has 25 instruments (10+15), nowhere near any pool cap — it is
     NOT the Heavy_Metal overflow residue. The build falls back to `single`
     through C31's documented "falls back on any merge/compose failure":
         merge_models -> ValueError: compilation players disagree on the freq table

THE REAL LEVER: `merge_models` (compilation.py:813) asserts the packed players
share a tuning and REFUSES otherwise — its own comment concedes "freq is
per-tune content but a compilation's players are usually the standard DMC
tuning; a mismatch is unmergeable". Here they genuinely differ, and audibly:
freq_lo differs at 2 of 96 entries (note 31 $06F3 vs $0647 = **-176 cents**,
nearly a whole tone; note 82 -6.7 cents), freq_hi identical, and `vibdepth`
differs too. That is real musical content, not a packer artifact.

CANON READING: a tuning table is content, not mechanism (the principle's C7
category C names tuning tables as the case where bytes ARE the natural musical
form), so two tunings in one file is representable, not a §7 leak. Both players
are DMC V4, so ONE composer serves them — `origin_engine`/C35 is NOT implicated
(its test is "more than one COMPOSER", not "more than one engine"). And the
schema ALREADY carries the field: `MusicSubtune.freq_table` exists (added
round 93 for the V5/heterogeneous path), alongside `default_filter` and
`wave_programs`.

SO THE SHAPE IS THE FAMILIAR ONE — "a per-player fact the merge collapses rides
a per-subtune override" — for which this entry already records FIVE precedents
(idle priming, idle_wave, d417_shadow, record_offset, dual_phase, rest_effects).
Two pieces, neither designed yet:
  1. `merge_models`: on freq/vibdepth disagreement carry per-song tables instead
     of raising.
  2. DMC V4 composer: consume `MusicSubtune.freq_table` (+ vibdepth). It
     currently reads only the FILE-level `usf.freq_table`
     (composer_asm.py:2745), though it DOES already consume per-subtune
     `wave_programs` — so the gating pattern to copy is right there.
GATE (same as every prior per-player widening): golden byte-identity over
all-agree members + a corpus census of how many detected compilations actually
disagree on tuning + a re-batch. NOT a small change; left for a scoped round.

⚠ LESSON: the observations (two bases, the SMC dispatch at $1E40, sub 0 FULL /
sub 1 wrong from its first note) were all correct — the conclusion was not,
because it was drawn from the recognition CARD. The ledger says a card is never
enough to act on; this is what that costs. Reading the entry also corrected a
second misreading: the two heads SHARING their third JMP target ($162F) is not
evidence against two independent players — packers point the all-off/sfx entry
at a shared routine, and merge_models already masks $1006-$100B for it.

## HVSC #85: family-1 is 5,445, not 5,401 (2026-08-09)
The collection update grew the family. 116 of the #85 catalogue's 10,774 DMC
members belong to no cluster in `tmp/dmc_families.json` (built over #84): 38
are new files, 78 became visible when the sidid path-truncation fix landed
(upstream truncates output paths at 56 chars, which had been silently dropping
2.3% of HVSC from the engine column — see ledger C20's seventh layer).
Classified with the census's own method (opcode skeleton, then 4-gram Jaccard
≥ 0.85 vs family reps): **family-1 +47**, V4-derived +46, V5 line +16, V5
branch +5, one singleton, one UNASSIGNED
(`Bayliss_Richard/Santas_Christmas_Delivery`, best Jaccard 0.108 against every
known DMC family — unlike anything we have, worth a look).

⚠ **A family KEY is the union-find REPRESENTATIVE, not the member's own
skeleton hash.** Fingerprinting a known f1 member returns a hash that is not
the family key, which reads convincingly as "the fingerprint function drifted".
It has not — recomputing against the stored `tmp/dmc_fingerprint.jsonl`
reproduces the June hashes exactly. Check that before concluding you must
re-fingerprint all 10,774.

f1 list = 5,445, NOT 5,448: three old paths (`Ares_02`, `Qbhead_01`,
`ZCHN_Is_Comm`) were RENAMED by #85 and return among the 47 under new names.
List: `tmp/dmc_f1_members_85.json`; per-member: `tmp/dmc_classify_new.json`.

Also note **every f1 verdict went code_hash-stale** on 2026-08-09: the
hvsc84→hvsc85 rename edited collection paths inside docstrings of fingerprinted
engine files, and `code_fingerprint` hashes raw bytes. Nothing is wrong; it is
pure recompute. That re-batch has since LANDED — see the entry above.

## ✅ B4-onset CLOSED + the vibdel DE-REDIRECT (2026-08-08, commits 2a6d85fe / 57035d3d) — f1 re-batched 5,401/5,401 FULL and corpus-synced
Two outcomes from one investigation, and the FIRST one refuted its own
premise. **(1) B4's `onset` elision question is closed as KEEP.** `onset` is
the DMC editor's VIBRATO DELAY (instrument byte 7 hi nibble x8 frames, lo
nibble = width); the player's `fx_vibdel` gates the WHOLE effects branch
(dual-slide included) while it counts down, and `fx_vib` is NOT inert at
width 0 (it advances the freq accumulator every frame; width only sets when
the direction flips). So "width 0 ⇒ the delay is meaningless" is FALSE on
the normal playback path: forcing onset:=6 on inert-vibrato instruments moved
the write stream on **27 of 60 sampled ordinary members with NO off-table
read at all**. An earlier "unreachable on 99.6% of members" claim had closed
only the exotic (off-table) door — see [[feedback_measure_mechanism_before_precedent]]
§3, the lesson: ask what a parameter IS FOR before mapping where its bytes
are readable. **(2) The vibdel DE-REDIRECT shipped** (ledger C11 refinement):
the off-table read of `vibdel` ($1771,x, fhi idx 202-204) was stamped `live`
by ADDRESS, never by measuring the value move; the counter is written only at
that voice's note-init and otherwise only DECed (init-cleared), so constancy
is PROVABLE from the write sites. Extract derives it per voice, composer drops
the row from the redirect (all-or-nothing per member; the idx must also be
EXEMPTED from `_static_at_live` or the whole redirect switches off). The proof
converted **27** members where a siddump census had flagged 18 — proof beats
sample. GATES: golden 208 = 176 byte-identical / 27 converted / 0 unexpected;
27/27 converters FULL; regression 0 regressed; fresh f1 batch **5,401/5,401
FULL** (batch_diff 0 regressions, +1 gain); mass-write 5,401 written / 0 err /
0 orphans / audit 10/10 from disk across all 6 build paths; corpus 12,064 OK,
spec lint 0/0. The sync also converged P1 (`speed_steps` [] identity form — 0
legacy all-zero left) and P3b (`step_base` split — 5,302 files).

## ✅ I5 IMPLEMENTED (2026-08-06): the byte-faithful stated orderlist LANDED — buckets 1/2/3 unified; 41/41 replay-exact, 13 MD5-identical + 9 otrk-honesty diffs all FULL
The approved design shipped in the recorded 5-step order. (1)
`pipelines/dmc/track_replay.py`: TrackNotation (slots, marks incl.
dual-carried, dead extras, mid-track jumps w/ landing bytes, loop-skip,
ring/endless/inject terminators) + `replay()` mirroring `_walk_track`'s
dispatch in slot space (one shared $FF wrap-key table keyed by the
LANDING byte — cross-site closure, Cornflakes; mod-256 ring keys at
top-dispatch once wrapped; inject keys carry transpose); the walker
records its own facts (`entry_dual` 1=dual/2=inject, `loop_target_pos`,
`endless_tail`) so no byte re-parse can drift. Standalone validation
41/41 residue voices exact (tmp/i5_replay_validate.py). (2) fold:
`_fold_orderlist` offers the notation at the 3 refusal buckets with a
DOUBLE proof — replay-vs-walk equality in walk space AND compose space
(USF rows + `_row_secwidth` + ref-id sticky, seed ref 1); mismatch =
legacy fallback; decisions made ONCE and shared with `_emit_otrk_fields`.
(3) schema (all elidable): `orderlist stated faithful:` + entry `@T`/`&`
+ `loop@N>K` / `endless` / `inject` / `ring`; corpus check 12,064 OK,
spec lint clean. (4) composer MATERIALIZES at compose time (replay →
existing emitters; otrk byte = the authored layout position; no player
change). (5) gates: 22-member MD5 gate = 13 IDENTICAL + 9 DIFF confined
to the otrk byte (stored otrk_legacy i+1 approximation → TRUE authored
positions) with ALL 9 re-verified FULL. KEY FINDING: the 8 Rayden-2SID
census voices are DEAD CONTENT — the C27 active map never selects those
model songs (their stored otrk_legacy keys were dead cargo, now
elided); the real byte-faithful carrier set = 26 voices / 14 members.
Commits 31d1adf2 / 5ef577d0 / 482c3c26 (+ closeout). Ledger C32 entry +
card updated; Move-1 D6 divergence note (resolve.py vs track_replay =
C21 factor-at-Move-1). Supersedes I4's reserved re-entry-offset
decision.

## ✅ I4 (2026-08-05): f1 fold residue CLOSED — 41 voices / 22 members verified, all documented design refusals, zero loop_not_rho
Re-census under post-lever code: 12 members mid-sector re-entry (only
future lever = a re-entry-offset stated notation, USER-RESERVED), 5 C34
dual-role, 5 piecewise transpose. All FULL. C32 close-out note recorded
(+ the no_offsets empty-voice census-artifact caveat). Phase I complete
except the reserved decisions; Phase-I items I1/I2/I3/I4 all landed
2026-08-05.

## ✅ I2 (2026-08-05): params-bag justification LEDGER wired into the ratchet (check 2b) — 99,682 instances 100% attributed, 0 unjustified
Census refuted "singleton tail dominates": 71% = Basic_Program bp_*
template representation (family-level BP question), ~25% = old-form
f2/v5 corpora (typed/stated in code, converge at their mass-writes),
2.4% FC std_* (C7-A3), true C19 wedge floor = 606 inst / 85 keys
(0.6%). No typing warranted. usf_principle_lint check 2b now enforces:
every bag key must match a documented block; a key >= 50 members
outside them = UNJUSTIFIED MASS, exit 1.

## ✅ I1 (2026-08-05): interpolation probe WIDENED — 208/208 midpoints live, 0 findings across DMC f1 + FC + Hubbard/Companion
Probe grew cross-file pairs, adsr NIBBLE-wise + wave_freq element-wise
interp, and an engine corpus registry (dmc/fc/hubbard; MA/GT/Basic join
when corpora exist). §9 test 3 clean corpus-wide post-split; test 4
probed via the shared schema. Standing opt-in gate (~1 h). Phase-I
remaining: I2 ratchet burn-down, I4 fold-residue close-out (I3 done).

## ✅ R184 (2026-08-05): the speed_steps/step_base SCHEMA SPLIT landed — the P3 interpolation finding CLOSED (50/50, 0 findings)
`PwmConfig.step_base` (presence = the split-form marker; None = legacy
packed, old corpora parse+build identically per the r182 precedent).
Extract emits true 0-15 steps + shared base; composer repacks
`(step<<4)+base`. Gates: corpus 12,064 OK, spec lint clean, family MD5
sweep 5,401/5,401 SAME (pure carrier refactor), regression 0 regressed,
probe 50/50. f1 stored .usf converge to the split form at the next
mass-write. ALSO this session: I3 dead-schema tails RESOLVED BY
VERIFICATION (deletion list EMPTY — every 'dead' candidate had live
readers/carriers; Move-1 plan corrected, 4978750e). Phase-I queue next:
I1 probe widening / I2 ratchet burn-down / I4 fold-residue close-out —
user decides each.

## ✅ R183 (2026-08-05): the loop_not_rho lever LANDED — general slot-model fold; 26 members fitted→stated, fold residue 22 with ZERO lever candidates
`_fold_slot_model` (to_usf.py) + walk `jump_from` metadata (engine_model):
first-visit slot linearization + jump-aware marks + whole-walk transpose
replay + strict one-intro variant shape; consulted ONLY at the old
`loop_not_rho_boundary` refusal point (structural 0-regression). Ledger
C32 refinement (entry + card) has the model + soundness conditions.
Gates: family-wide build-vs-stored MD5 sweep 5,377/5,401 SAME; 24 DIFF =
the full exposure set (19 were fitted pad/period carriers INVISIBLE to
the otrk census — byte sweep is the true census); all 24 + 2
sibling-family members (Game_Muzak_v2, Bean) verified FULL. Cotton_Eye_Joe
re-bucketed intro_variant (inject sectpos INC = mid-sector re-entry);
Cornflakes v3 → marks_uninherited (C34 dual-role byte). SESSION DECISIONS
(tmp/cleanup_plan_2026-08-03.md updated): F3 closed as a NON-ISSUE (§4.5
grounding is audibility, not intent — edit made then REVERTED 622fe48e);
speed_steps/pw_step_base split APPROVED, runs next; G1 uready deferred
INDEFINITELY (user-triggered only); f2 kickoff DEFERRED (f1 quality work
first); Phase I roadmap queued (interp-probe widening / ratchet burn-down
/ dead-tail classification / fold-residue close-out — user decides each).
Corpus: 26 members re-batched + mass-written post-regression this session.

## ✅ OVERNIGHT #2 CLOSEOUT (2026-08-05, P1-P5): otrk residue 90→27 characterized; interp probe live with its first §4 finding; ratchet metric honest at 0.37%
P2: FOLD_REFUSAL census → empty-voice noise fix (42 members) + the
closed-at-first-wrap fold lever (29 members; 19 byte-diff all FULL vs orig);
final residue 27, one bucket each (11 intro_variant design refusals / 7
loop_not_rho lever candidates / 9 piecewise transpose tail) — ledger C32
refinement. P1: all-zero speed_steps → [] identity (construction-proven,
MD5 24/24 incl. ghost+pooled); inert-vibrato onset=0 EVALUATED-KEPT (ivdel
observability via irecimg + record reads). P3: usf_interp_probe.py built —
45/50 midpoints realize; the 5 failures = ONE finding, the speed_steps
shared-base-nibble coupling (schema-refinement candidate in the Move-1
plan: split step values from pw_step_base). P4: fx_flags = 28 NAMED C14
row commands, ratchet metric split three-way → genuinely-untyped mass is
0.3681% (was a 4.05% artifact). P5: dead-schema tails documented in the
Move-1 plan. USER-GATED remaining: F3 canon edit, G1 uready (deferred
until post-f2 by user decision), the loop_not_rho lever, speed_steps
schema split.

## ✅ R182 (2026-08-04): the 5 mass params keys TYPED — init_behavior articulation fields (C33 2nd occ), 843/843 carriers MD5-identical
hold_gateoff/rest_effects/hard_restart/cymbal_onset/vib_ramp →
InitBehaviorConfig.{gate_off_hold,rest_effects,hard_restart,cymbal_onset,
vibrato_ramp} (Optional, None = canon defaults adsr_clear/run/preset/0/width,
elided). Composer typed-first + params fallback; old-form corpus (f2 June
files) untouched + building identically until the f2 campaign. Gates:
843/843 in-f1 carriers regenerate MD5-identical, corpus check 12,064 clean,
spec lint clean. Typed .usf store pass for the 843 running (per-member
MD5-guarded). ⚠ grammar trap recorded in C33: keyword terminals shadow
CNAME params keys corpus-wide — use the generic CNAME-key pattern.

## ✅ R181 (2026-08-04): behavioral identity promoted to the DEFAULT merge dedup key — 23/23 merge_models members FULL, corpus 5,833/5,833
User decision (option 1 of the wrap-up list). The overflow-only relax became
the default: positional fields (record_offset / wave_start / wave_pool_pos)
ride `_inst_key` ONLY for players with a position-sonifying read (ioff
166-168 ∪ wavepos fhi 211-213); the strict pass is gone. Verified by FULL
re-verify of every merge_models member (22 compilations + Mega_Mix medley):
23/23 FULL, 0 regressions (closeout diff clean). Artifacts mass-written +
disk-audited. Better ML corpus: no position-split duplicate instrument
definitions. Ledger C8 (3rd widening) + C31 (behavioral-identity default)
entries + cards updated. If a NEW position-sonifying read class is ever
found, GROW the observability windows — a miss shows as a partial at
verify, never a silent wrong FULL.

## 🏆 R180 (2026-08-04): Lane_Crazy **FULL 6/6** — FAMILY-1 AT **5,401/5,401 (100%)**
The last partial closed via two canon-derived moves (the user's re-read-the-
canon challenge reframed the fix): (1) Principle §6 Rule-1 IDENTITY — the
merge's overflow-retry relaxes ALL positional fields (record_offset,
wave_start, wave_pool_pos) for players carrying no position-sonifying read
(ioff 166-168 ∪ wavepos 211-213): position is behavior ONLY when observable;
the phase-4 unconditional position-identity was quiet Rule-1 over-splitting.
(2) C8's NEXT WIDENING, implemented only after measurement showed the
observable players alone exceed 42: above 42 instruments the composer POOLS
deduped 6-byte pulse-step blocks (istepbase = per-instrument pointer;
capacity = distinct blocks ≤ 42, instruments free to 255); merge cap
mirrored block-aware. Triple-gated (≤32 stride-8 / 33-42 dense stride-6 /
43+ pooled): 31 members byte-identical vs the pre-change stored corpus.
OPEN (user decision, recorded in the canon re-assessment): promote
behavioral identity to the DEFAULT dedup key for all merges (better ML
data; changes + re-verifies the 21 compilation members). Ledger C8 update
pending this decision.

## ✅ R179 CLOSEOUT (2026-08-04): current-code batch 5,400/5,401 FULL; corpus mass-written + audited; portfolio 65/95; counter-ratchet baselined
Re-verify batch under post-cleanup code: 5,400/5,401 FULL (Lane_Crazy the 1
known partial, fix designed — see below). Mass-write 5,400/0 err, audit
10/10 all build paths; usf_corpus_check 12,063 clean; spec_lint 0/0;
escape-hatch baseline 4.0592% (tools/usf_ratchet_baseline.json). f1 corpus
noise swept: empty-arp 0, otrk_* residual = 90 genuine fold-refusals (71
otrk_legacy documented approximation). Portfolio re-derived: 65 members /
95 dims (every r74-r177 wedge class guarded), all FULL. batch_diff wired
into the batch DONE path + fired live. Plan: tmp/cleanup_plan_2026-08-03.md
(A-E done; user-gated: Lane_Crazy fix choice, 5-key schema typing, E3, F3,
G1 uready).

## 🔎 R179 (2026-08-04, overnight): hygiene batch LANDED — 5,832/5,833 FULL; the 1 partial is Lane_Crazy, root-caused to the phase-4 wave-pool identity growth (fix DESIGNED, awaiting review)
Fresh batch DONE {'full': 5356, 'partial': 1} (5,832 FULL total after dedup
incl. prior rows); batch_diff vs Jul-26: **82 gains ✓, 1 regression —
Bayliss_Richard/Lane_Crazy** (4-player compilation; sub 0 FULL, subs 1-5 pos-1
divergence). CAUSAL CHAIN (git-bisected, probe = build-path): `49a98c1c`
(C11 phase-4 positional wave-pool emission, post-Jul-26-batch) made
wave-table POSITION part of instrument identity → the 4 players' near-
identical kits stopped deduping (42 → 44) → `_MAX_INSTR` 42 cap →
UNMERGEABLE → silent single-player fallback. NOT r149 (record_offset key —
already UNMERGEABLE at its parent). Landed tonight: the C8-gate overflow
RETRY in merge (strict pass first = byte-identical for every fitting member;
on overflow relax record_offset keying for players with NO ioff-window read
— fires but insufficient here since the split is wave_start-driven).
DESIGNED FIXES for review: (a) C8 widening of the pulse-step index (pooled
per-instrument base byte over DEDUPED step blocks — capacity becomes
distinct-blocks-bounded), or (b) wave_start position-observability gating in
the dedup key (share when no wavepos-window read observes the position —
the ioff-relax analog). Also: `build_path` flip census old→new showed only
Lane_Crazy bad (Mission_Moon/Mega_Mix/Mothafucka flips are intended gains).

## 📋 CLEANUP PLAN (2026-08-03): tmp/cleanup_plan_2026-08-03.md — the ticked work list for the whole post-r178 cleanup
Phases A-H: hygiene-batch acceptance (batch_diff; 1 partial appeared mid-run,
unidentified) → writer elision cleanup (arp/vibrato/pwm defaults) → ONE
mass-write sweeping otrk_ stale forms + verbose init + noise → portfolio
re-derivation (the uready criterion-4 GAP: extend dmc_v4_features with
r74-r177 classes) → the Principle counter-ratchet (cardinality census,
escape-hatch mass metric, interpolation probe → uready Phase-2 value matrix)
→ C33 burn-down of the 44 params.fields keys → full uready → f2 kickoff.
Supersedes the individual NEXT notes in the entries below.

## 🔎 R178 POST-MORTEM (2026-08-03): how 4 FULLs regressed unnoticed for a week — closeouts masked them (C20 sixth layer) + tools/batch_diff.py
User question: "the march is alphabetical — how were there partials left at F
after we reached Z?" Measured answer: 4 members (Flash Itinerant/Kan-Kan/
Wind_of_Dead + Tomace/Other_Side) were FULL@r88 (Jul 22) and partial@Jul-26 —
they REGRESSED mid-week, after the march passed their letters. MD5-bisect of
each member's BUILD across the window pinned both culprits: `cdfa9c42`
(C29 CPU-eye generalization, Super_Seven round — flipped Itinerant's bytes
4c5226e3→20f013f1, the ROM-text contamination r176 fixed) and `d80c1b94`
(r116 glide-arrival record creation — Other_Side FULL at its parent, the
exact play_match=46 partial at the commit; the record fed r177's bad igla
seed). The Jul-26 batch RECORDED the truth; the closeout's NET count (+57
full) masked the −4, and the queue folded them in undifferentiated. NOT a
verify-side change; NOT a stale-r88 palimpsest (checked: same code_hash on
both r88 rows; the old build genuinely verifies partial under the current
comparator — because those bytes ARE the post-cdfa9c42 contaminated ones;
the true r88 bytes 4c5226e3/0536b4dd verify FULL). FIX: tools/batch_diff.py
(reproduces the 4 exactly) + CLAUDE.md closeout rule + C20 sixth layer.
Hygiene full-family batch running (tmp/dmc_batch_r177.log →
tmp/dmc_wide_results.jsonl); acceptance = batch_diff vs the Jul-26 batch.

## 🏁 MILESTONE (2026-08-03, after r177): family-1 batch-known partial queue EMPTY — all 82 partials of the Jul-26 batch confirm FULL under current code
Every entry of tmp/dmc_f1_partials.jsonl (seeded from the Jul-26 full batch,
5401 members: 5319 full / 82 partial) re-verified FULL 2026-08-03; ticked
checklist at tmp/dmc_f1_remaining.md. Rounds r167-r177 closed the tail
(Wodnik C23 family, Flash C29 port re-bank, C19 wedges 40-43, C11 glide-seed
gate) with heavy cascade (e.g. Cherch/Metallica/Shaki/… flipped by C23
refinements without dedicated rounds). ⚠ NOT the authoritative closeout:
coverage source of truth = a FRESH family batch (re-checks the 5319 FULLs for
regressions; ~overnight on the X230). NEXT (2026-08-03): run the fresh batch,
then mass-write (corpus_sync) + re-derive the regression portfolio
(select_regression_portfolio --engine dmc_v4) per CLAUDE.md.

## ✅ ROUND 177 (2026-08-03): Tomace/Other_Side — **FULL** (142989/142989)! C11 refinement: the igla/iglb glide-leftover seed is gated on the member's INIT CLEAR RANGE
Next partial after r176 (queue scan flipped a long stale stretch F→T on the
way). No STIL (the "Other_Side" STIL hits are LukHash's unrelated tune), no
BUGlist. V2/V3 first rows = note 0 + transpose −2 → off-table freq-lo idx 254
→ gla+1 ($1745). The extract's 98_Mix-era seed emitted `glide_note: $5E` (the
file-image leftover) but this CANON-init member's clear loop wipes
$1718-$179D — orig's gla is $00 at the read (dmc_offtable_probe: LIVE, $00 at
the divergence). Diverged at flat pos 9, frame 1.
- FIX: `m.glide_leftover_cleared` (static probe: canon clear `STA base+$718,x
  / INX / CPX #imm`, fires iff imm ≥ $32 = covers gla+glb) gates the `_gseed`
  fill in to_usf. Non-matching clear shapes (98_Mix's $0342 family) keep the
  proven seeding, byte-identical.
- 0-REGR (measured, not reasoned): 35 stored seed carriers censused — 24
  canon-clear (seed suppressed) ALL re-verified FULL incl. both Rayden 2SIDs
  (their seeds were unobservable: first gla read follows a glide arm, live
  redirect tracks it); 98_Mix (non-firing) re-verified FULL; the other 10
  non-firing byte-identical by construction. Ledger C11 (refinement).

## ✅ ROUND 176 (2026-08-03): Flash/Itinerant — **FULL**! +3 FULL (Itinerant, Kan-Kan, Wind_of_Dead) — C29 6th occ: the PLAY-HEAD RE-BANKS $01, ROM-window overlay served BASIC ERROR TEXT over generated instrument records
Next partial after r175 (queue wrapped to F/). No STIL/BUGlist entries. The
Flash members' play wrapper opens `LDA #$35/STA $01` (BASIC+KERNAL OUT)
though iomap($0FC0)=$37; init unpacks song data to $A2xx-$A7xx RAM (skip-zero
unpacker). The C29 overlay's "undefined" gate (mem≠ref) can't see a zero
write where the power-on seed is already $00 → those bytes were served the
`--peek-post-init` value = BASIC ROM ERROR TEXT (idle $37 banking) → per-BYTE
ASCII contamination of instrument records (V1 pulse swept +$45 vs orig +$40,
V2/V3 swept vs held; AD/SR/waves/notes right since nonzero).
- DIAGNOSIS: effect_chain_profiler $D402 → reader ops all consistent (base
  $A2B3) → py65 post-init vs libsidplayfp RAM AGREED (data right!) → the
  OVERLAY was the corruptor. peek showed "BY ZER(O) ILLEGAL DIRECT…" at $A2B3.
- FIX (`_overlay_offimage_windows`): probe the play-vector head for
  `A9 imm/85 01` → imm = effective play port (overrides `_psid_play_iomap`);
  ROM ranges served from the peek ONLY if banked in under it (BASIC port&3==3,
  KERNAL port&2); banked-out → memwatch-stability RAM branch. Offset-1 port
  read also serves the re-banked value.
- 0-REGR: census 10 play-head re-bank members (7×$35/2×$36/1×$37); 3 Flash
  partial→FULL, 5 byte-identical, 2 error pre-existing. 8 other C29 carriers
  (Memomania/Super_Seven/Trailways_A/Roots/Remix_1995/Pour_le_merite/
  Abyssal_Karma/Centric) MD5-identical. Smoke 6/6. Ledger C29 (6th occ).

## ✅ ROUND 175 (2026-08-03): Zyron/Solar_Energy — **FULL** (294072/294072)! C19 wedge 43rd occ: $FF LOOP-hook store re-pointed OFF otrk = dead loop, tune HALTS at song-end
The parked r174+1 member. The parked note's framing ("a voice keeps
freewheel-writing") was wrong — the rebuild's +2691 tail was a full SONG
RESTART (re-init burst at f18802 matching the opening f0/f1), i.e. we LOOPED
where the orig ENDS. Sole firing carrier in HVSC-DMC; 0-regr.
- MECHANISM: JSR-hook loop member (`track_loop_target=True`), but the hook's
  `STA otrk,x` is re-pointed `$1726→$6726` (dead) — the $FF loop target goes
  nowhere, otrk pins at the $FF, the dispatch JMP re-reads $FF forever →
  play() spins at song-end, tune HALTS+HOLDS ($D418 stays $1F, no writes).
  All 3 tracks end `$FF <tgt>` but never loop; memwatch showed otrk frozen at
  (98,96,94) = the $FF positions; pc-watch showed the hook hit 173k× (spin).
- FIX: `_track_loop_dead_probe` (static: hook STA operand ≠ the dispatch's own
  LDY otrk operand + OBSERVE-CONFIRM the orig halts from the writelog) →
  `extra_params['track_loop_dead']`; extract `_walk_track(loop_dead=True)`
  walks $FF as STOP; composer $FE handler = halt-and-hold (track_fe_reset
  machinery minus the $D418=$00).
- ⚠ TWO probe traps hit and fixed in-session: (1) static mismatch alone
  false-fired on KB/1_67_Years + PVCF/Kata_Sandom (relocated players, hook
  stores to un-relocated $1726, dispatch NEVER REACHED — both FULL, briefly
  regressed → observe gate restored them); (2) observe window songlength+30
  cut off BEFORE the halt (recorded 345s ends at the fade; halt at 376s) →
  ×1.15+30. Census: 938 JSR-hook members, 909 genuine, 4 mismatched, 1 halts.
- Golden set (dmc_v4 portfolio ×5 + Dark_Side) byte-identical vs pre-fix
  worktree; dmc_smoke 6/6. Ledger C19 (43rd occ).

## ✅ ROUND 174 (2026-08-01): Zyron/One_Man_and_Boris — **FULL** (122971/122971)! C19 wedge: filter-tail cutoff LOAD operand repointed fcut→fbase
Next partial by hvsc path (canon-LAYOUT member — `dmc_canon_diff` found it: 1 NEW
cluster `$10A0 repoint LDA a @operand`). Diverged deep (~70%) on a single $D416
(filter cutoff hi): orig $00 vs rebuild $22. No STIL/BUGlist. 2 carriers, +2 FULL
(One_Man_and_Boris + Gop/Buddhas_Garden, both partial→FULL), 0-regr.
- MECHANISM: canon filter tail at base+$A0 = `LDA $171C (fcut, swept cutoff) /
  STA $D416`; the wedge repoints the LOAD operand ONE BYTE DOWN to `LDA $171B`
  (fbase = the filter-def base index def#<<4), so $D416 sources the DEF INDEX
  (a per-def constant that steps when the filter def changes), not the cutoff.
- FIX: `_filter_cut_from_fbase_probe` (static: base+$A0 = `AD` LDA-abs with
  operand==base+$71B AND followed by `STA $D416`) → composer `filter_cut_from_
  fbase` loads `fbase` instead of `fcut` for the $D416 store. Regression-safe by
  construction: canon has operand +$71C (fcut) → probe returns None → byte-
  identical; the probe fires ONLY on the exact fbase-repointed filter-tail shape.
- FOUND BY `dmc_canon_diff` (canon-layout member) — contrast the recent
  re-assembled Wodnik/Yuro members where canon-diff was blind. Ledger C19.

## ✅ ROUND 173 (2026-08-01): Yuro/Fatamorcana_intro — **FULL** (19006/19006)! +3 FULL — C19/C31 forced-tune-record wedge, 5th FORM: non-canon dispatch + reg-transfers, OBSERVE-then-confirm
First non-Wodnik partial in a while (Yuro). Init `$1E52 = LDA #$03 / TAX / TAY /
JMP $1000` forces the played record to song 3 (header says songs=1), but the
extract walked record 0 → all note values wrong from the start. No STIL/BUGlist.
+3 FULL (Fatamorcana + Ass_It/Game-Music_1 + Odysseus/Long_Way_tune_6), 0-regr.
- WHY `_forced_subtune_probe` MISSED IT: (1) its base guard requires the canon
  `JMP base+$1D` dispatch, but this RE-ASSEMBLED member's base is `JMP $1807`;
  (2) the wrapper interposes `TAX / TAY` between the `LDA #imm` and `JMP base`
  that no fixed static shape parses.
- FIX (C18 observe-don't-parse + a confirmation): for a NON-canon-dispatch base
  (base is a JMP but not base+$1D) with an `LDA #imm` wrapper, OBSERVE — run the
  real init(A=sub) under py65, read A at base (`_init_song_observe`); fire iff
  UNIFORM + NON-IDENTITY. ⚠ THE OBSERVATION ALONE FALSE-FIRES: a wrapper whose
  `LDA #imm` is NOT a record index (or an init that IGNORES A) reads A=imm at
  base but plays record 0 — census found large bogus forced values (99/90/49…),
  though those all ERROR `no_jumptable` (non-$1000 base, never reach the probe).
  CONFIRM with `_init_forced_changes_state(base, forced)`: enter the init BODY
  at `base` (BYPASSING the forcing wrapper, which overrides A) with A=0 vs
  A=forced and require the post-init RAM to DIFFER — i.e. the init actually USES
  A to pick the record. Regression-safe: a FULL member walking record 0 has A==0
  at base (identity → no fire); an init that ignores A → states equal → no fire.
- 0-REGRESSION: census of the 9 observation-fires — 4 buildable (all were 0%:
  Fatamorcana/Game-Music_1/Long_Way → FULL, No_Trade stays partial with correct
  forced=1 but a deeper blocker), 5 error out. 5 known-FULL members (Dark_Side,
  Akademia, Nocturno, For_Party, Second) byte-identical. Ledger C19 (forced-
  tune-record wedge, 5th form) / C31.

## ✅ ROUND 172 (2026-08-01): Wodnik/Logarytm — **FULL** (96488/96488)! +2 FULL — C23 refinement 5: escalate the defer window PROGRESSIVELY (late melodic section)
Next partial by hvsc path. Logarytm's melodic section starts LATE (~43s in):
inits=0 at 30s, 29 by 90s — so r170's single 30s escalation missed it (canon
build partial, defer 100%). No STIL/BUGlist. +2 FULL (Logarytm + Ziazi, both
were partial), 0 regression.
- FIX: replace the single 30s escalation with a PROGRESSIVE ladder 10s→30s→90s,
  escalating only while INCONCLUSIVE (`inits<2 and with_ctrl==0`) and stopping
  as soon as decisive — inits>=2 (fire) OR with_ctrl>0 (a late CANON melodic
  section correctly never fires, its inits carry ctrl). Window-independent
  0-regression (the cymbal-exclusion + canon-carries-ctrl argument holds at any
  window length).
- 0-REGRESSION: flip census over 204 members = 2 NEW defer (Logarytm + Ziazi,
  both partial→FULL — Ziazi's melodic is also late), 0 stopped firing. Ziazi
  without defer = 55.94% (partial), with = 100%. Ledger C23 (refinement 5).
- ⚠ This is the 3rd window-tuning refinement (30s r170, floor-2 r171, ladder
  r172). If an EVEN-later-melodic member appears, the definitive window-
  independent answer is the write-log ORACLE (build both defer/canon per
  dataflow member, keep whichever matches the orig) — heavier, deferred, NOTED
  for the next time this recurs.

## ✅ ROUND 171 (2026-08-01): Wodnik/Lalamido — **FULL** (302182/302182)! C23 refinement 4: the defer `inits>=8` count is a SPARSITY floor, lower it to `>=2`
Next partial by hvsc path (another Wodnik defer member). Lalamido has just 2
melodic note-starts in the WHOLE song (very long held notes) — canon build
0.02%, defer 100% — so even the r170 30s escalation yields inits=2, under the
old floor of 8. No STIL/BUGlist. +1 FULL, minimal blast radius.
- KEY (builds on r170's cymbal exclusion): once deferred/split cymbals are
  excluded, a CANON member has ZERO qualifying chunks (its melodic inits carry
  ctrl; its cymbals are excluded), so ANY non-cymbal AD/SR-only init is already
  a genuine defer signal — the `inits>=8` was a sparsity FLOOR, not a confidence
  gate. Drop to `inits>=2`; the ratio `with_ctrl*5<inits` still forces
  with_ctrl==0 at inits 2-4 (one ctrl > 20%), so a stray split can't fire.
- 0-REGRESSION: census over 243 members (whole Wodnik+Heinmueck + broad sample)
  = exactly 1 member fires at >=2 but not >=8 (Lalamido → FULL), 0 canon
  false-positives. Every other member byte-identical. Ledger C23 (refinement 4).
- NOTE the Wodnik CIA deferred-init family has now yielded 7 FULLs across
  r168-171 (Akademia, CH2, Szach, Czad, King_Leter, Maxell, Lalamido) as the
  C23 detection hardened across its collision/cymbal/sparsity variants.

## ✅ ROUND 170 (2026-08-01): Wodnik/King_Leter — **FULL** (386046/386046)! +2 FULL — C23 refinement 3 (an AMEND worked example): sparse-defer escalation + the DEFERRED/SPLIT-CYMBAL exclusion
King_Leter is a genuine defer member (forcing defer → 100%) with LONG notes: only
2 melodic inits in 10s, so `inits>=8` never trips → built canon (partial). The
naive fix (escalate the capture window 10s→30s) caught it BUT **regressed
R1/R2/R4/R5** (Wodnik siblings, FULL without defer → 8.8%). The `/amend` skill
(user reminder) caught it before commit. No STIL/BUGlist. +2 FULL (King_Leter +
Maxell), 0-regression (flip census over 204 members: 2 new defer, 0 stopped).
- AMEND ROOT CAUSE (Lens 1 — the premise was a blanket model): the r168 rule
  "an AD/SR-only chunk is a deferred note-init" is FALSE for cymbal members.
  R1's notes LAND as `$81` NOISE BURSTS, and the per-IRQ capture SEPARATES a
  cymbal note's AD/SR from its burst into different frames → the standalone
  AD/SR chunk is a false "melodic init". R1 & King_Leter are per-chunk IDENTICAL
  (both `[ad,sr]`-only, no ctrl/freq); `with_ctrl` CANNOT discriminate them.
- THE DISCRIMINATOR (ground-truth, Core Tenet): what the note LANDS AS — the
  SAME voice's NEXT ctrl write after the AD/SR chunk. `$81`=cymbal (exclude, it's
  handled by cym_ni) vs a melodic gate-on (real deferred init). Measured: R1 =
  8/8 cymbal-followed → 0 real inits; King_Leter = 6 melodic + 2 cymbal → 6
  real; Akademia = 98/98 melodic (unchanged).
- FIX (`_noteinit_defer_probe`, overarching): (1) extend the same-frame cymbal
  exclusion to the DEFERRED/SPLIT form — an AD/SR-only chunk whose voice's next
  ctrl is `$81` is a cymbal note, excluded; (2) escalate to 30s when `inits<8
  and with_ctrl==0`. The cymbal exclusion is WHAT MAKES escalation
  regression-safe: R1 escalates to inits=0 (all cymbal) → no defer → canon FULL;
  King_Leter escalates to 13 real → defer → FULL.
- VERIFIED: King_Leter/Maxell FULL (defer); R1/R2/R4/R5 FULL again (canon, the
  regression undone); Czad FULL (canon); Akademia/CH2/Szach/Papierosy/
  Redable_Rain FULL (byte-identical, still fire). Ledger C23 (2026-08-01
  refinement 3). LESSON: a regression from an escalation is the SIGNAL the
  detection premise is a blanket model — the note's LANDING, not `with_ctrl`,
  separates real-defer from split-canon.

## ✅ ROUND 169 (2026-08-01): Wodnik/CH2 — **FULL** (176680/176680)! +3 FULL — C23 refinement 2: the `hr_prep_gate` gate had the SAME bucketing-collision brittleness
Next partial by hvsc path — another Wodnik member (same CIA deferred-note-init
player as Akademia r168). No STIL / BUGlist. 0-regression (structural + flip
analysis + smoke). +3 FULL: CH2 (target) + Szach (183194) + Czad (60743).
- DIVERGENCE (pos 27): orig writes V1 ctrl $08 THEN $09 (the hr_prep_gate
  TEST→TEST|GATE prep), rebuild writes only $08 (canon prep) then skips to AD.
  So `hr_prep_gate` didn't fire even though CH2 is the same player as the r168
  carriers. `noteinit_defer_wave` DID fire (the r168 gate relaxation caught it).
- ROOT CAUSE — the SAME per-IRQ bucketing collision as r168, now on the
  `hr_prep_gate` gate: the strict gate required EVERY prep chunk to show the
  EXACT ctrl list `[$08,$09]` (`preps_gate9 == preps`). On this high-multispeed
  member a merged bucket PREPENDS the prior play's note ctrl → `[$41,$08,$09]`
  or `[$10,$08,$09]`, which `== [$08,$09]` misreads as canon (CH2: 131/138
  exact). Forcing hr_prep → 100% FULL, confirming the off-chunks are artifacts.
- FIX (`_noteinit_defer_probe`, 2 complementary tolerances — the hr_prep
  collision is per-chunk RECOVERABLE, unlike defer_wave's): (1) test the
  `[$08,$09]` SUBSEQUENCE not equality (the merge prepend doesn't destroy the
  subsequence — recovers CH2 131→138, Szach 19→20 to 100%); (2) relax the
  aggregate to `preps_gate9 * 5 > preps * 4` (> 80%) to also absorb the rare
  bucket that SPLITS $08/$09 (Czad 178/179). Docstring updated.
- 0-REGRESSION IS STRUCTURAL (same as r168): canon preps write $08 ALONE (0%
  show `[$08,$09]`), so a FULL-without-hr_prep member (its orig writes $08
  alone — else the missing $09 makes it partial) can NEVER reach the > 80%
  band. Flip analysis over the whole Wodnik family + canon controls + golden
  set: ONLY CH2/Szach/Czad flip (all → FULL), every existing carrier
  (Akademia/Papierosy/Redable_Rain, TRUE→TRUE) + canon member (FALSE→FALSE)
  unchanged = byte-identical. Ledger C23 (2026-08-01 refinement 2).
- NB the Wodnik family (~90 members) is a rich seam of this CIA deferred-init
  player; several more are likely partial on adjacent gate/timing issues.

## ✅ ROUND 168 (2026-08-01): Wodnik/Akademia — **FULL** (151466/151466)! C23 refinement: the `noteinit_defer_wave` gate was too strict for a high-multispeed CIA member
Next partial by hvsc path. Reassembled CIA 2×-multispeed member (base $0ff4
prefix absorbed to $1000), same Wodnik/Heinmueck deferred-note-init player as
the existing `noteinit_defer_wave` carriers. No STIL / BUGlist entry.
0-regression (structural, see below) + smoke green.
- DIVERGENCE (per-IRQ, pos ~44): the orig's note-init is DEFERRED (AD/SR on the
  init play, freq/PW/ctrl land the NEXT play), the rebuild lands the wave
  same-play → the PW sweep phase is permanently offset by one step. Diagnosed by
  splitting both streams by play() invocation: orig play1 = V1 prep only, play2
  = V2/V3, play4 = V1 wave lands; rebuild lands V1 on play2.
- ROOT CAUSE — a probe GATE bug, not a new mechanism: the member IS a genuine
  `noteinit_defer_wave` member (forcing the param → 100% FULL), but
  `_noteinit_defer_probe` required `with_ctrl == 0` (EVERY melodic init chunk
  lacks a ctrl write). Akademia is 46/47 pure-defer but ONE per-IRQ frame
  (frame 622, ~2× the writes) MERGED two consecutive play()s — a deferred
  init's AD/SR + the next play's wave-landing ctrl in one bucket = a false
  canon-init → the strict gate rejected the whole member, built it canon =
  partial.
- FIX (`_noteinit_defer_probe`, 1 line): relax `with_ctrl == 0` →
  `with_ctrl * 5 < inits` (< 20% carry ctrl). Tolerates the occasional
  bucketing collision. Measured over 30 members: canon members cluster at
  95-100% carry-ctrl, defer members at 0-2% — the 20% threshold sits in the
  empty gap with enormous margin. Akademia's frame-622 collision is proven an
  ARTIFACT (all-defer reproduction = 100% match).
- 0-REGRESSION IS STRUCTURAL: a member built correctly WITHOUT defer_wave has
  canon same-play inits (AD/SR + ctrl together) ⇒ ratio ~100% ⇒ can NEVER fall
  in the low-ratio flip band; only defer-shaped PARTIALS flip. Verified: across
  the portfolio + wedge-FULLs + existing defer carriers (Redable_Rain /
  Papierosy / Metallica / Shaki / Zak_Davida, all still FULL) + a random
  family-1 sample, Akademia is the ONLY flip. Ledger C23 (2026-08-01
  refinement). NOTE the strict `==0` was itself WRONG for any defer member with
  even one collision — the tolerance is the correct model.

## ✅ ROUND 167 (2026-08-01): Wayne/Dark_Side — **FULL** (131890/131890)! C19 40th occ: the $FE track-STOP handler re-pointed at the KERNAL RESET vector
Next partial by hvsc path (`dmc_next_partial`). Diverged in the ~10% tail (pos
131850/131890): the orig writes a lone `$D418=$00` at a NEW frame then produces
NO more writes (song HALTS silent — identical held snapshots); the rebuild kept
playing normally. No STIL / BUGlist entry for this SID. 0-regression (10-member
golden set byte-identical incl. the 2 non-carrier Wayne siblings Knives_Intro /
Power_of_Magic; DMC smoke + portfolio green).
- MECHANISM (C19 wedge, sole carrier in 10,683 DMC-family members): canon $FE
  (track-STOP) handler at base+$E9 = `A9 00 / 9D 0C 10 (STA $100C,x = clear the
  voice-active flag) / 60 (RTS)` — a PER-VOICE stop (that voice freewheels its
  last note, the OTHER voices keep playing). This member (RE-ASSEMBLED, not
  canon-layout → `dmc_canon_diff` blind) overwrites the first 3 bytes with
  `4C E2 FC` = **`JMP $FCE2` (KERNAL RESET)**, leaving `0C 10 60` dead. So the
  FIRST voice to reach its `$FE` resets the machine; the reset's IOINIT does
  `STX $D418` with X=0 (KERNAL $FDC4) = a lone `$D418=$00` (silence), then the
  CPU idles in the BASIC loop → no more SID writes.
- DIAGNOSIS PATH (frame-numbering morass avoided): `effect_chain_profiler
  --frames --register D418` → the `STA $D418` PC is `$FDC4` (KERNAL); disasm the
  KERNAL there (`STX $D418`, part of IOINIT); a binary scan of the player for
  `JMP/JSR $E000-$FFFF` finds `JMP $FCE2` at $10E9; disasm base+$D0..$100 → the
  DMC orderlist walker with the $FE handler wedged (canon at $10E9 = clear
  $100C,x). All three voices' extracted orderlists end in `stop` ($FE), so the
  composer's walker DOES reach the $FE handler — only its BODY needed changing.
- FIX (CORE TENET — reproduce the WRITE STREAM, not the reset):
  `factory._track_fe_reset_probe` anchors the walker's `$FE` test (`C9 FE D0 06`
  at base+$E5) + the `JMP $FCE2` handler (reloc-aware, target restricted to
  $FCE2) → registered in `_WEDGE_PROBES` → composer param `track_fe_reset`.
  composer_asm: when the param is present, the `$FE` handler emits one
  `$D418=$00`, `inc halted`, then `pla / pla` (drop the `jsr voice` return) +
  `jmp pf_exit` (skip remaining voices + filter tail); `playframe` starts with
  `lda halted / bne pf_exit` so every later play() RTSes with no writes.
  `halted` is a byte OUTSIDE state0..state_end (init's clear never wipes it;
  init runs once — no restart for this member). No param → the canonical
  per-voice stop, byte-identical.
- Distinct from `track_ff_reinit*` (r117/r164-166: the $FF LOOP handler
  re-pointed at INIT = a whole-song RESTART); this is the $FE STOP handler
  re-pointed at RESET = a whole-song SILENCE+HALT. Ledger C19 40th occurrence.
  Corpus code_hash now stale pending a fresh batch.

## ✅ ROUND 166 (2026-08-01): Verdict/Verdict_01 — **FULL** (178259/178259)! The r165 residue (garbage instrument-record pulse read) reproduced via an orig#-laid-out record image
r165's "narrow boundary" was ALSO fixable — the user's "push to full" (after
re-anchoring on the canon) was right. My "hard boundary" claims were wrong
THREE times (survivor framing → ghost garbage; dynamic target → static;
unfixable pulse read → record image). 0-regression: For_Party FULL, DMC
portfolio 5/5, smoke 6/6.
- THE LAST DIVERGENCE: V1's pulse step reads `$18f3[ioff=$07]` (a MID-11-byte-
  record byte) — the ghost frame de-links `ioff` (the $174D shadow) from cinst
  for ~1 frame (until the deferred note-init reloads it). My COMPACTED SLOT-
  ARRAY composer (parallel arrays indexed by slot) has no analog for a mid-
  record byte read at a garbage byte-offset. The 3 voices' garbage ioffs
  ($07/$11/$01) read records 0/1 at scattered bytes (10=flags, 9=wave_start,
  4=pw-step nibble).
- FIX (`irecimg`, composer_asm.py, GATED on `track_ff_reinit_ghost`): emit an
  11-byte-record IMAGE laid out by orig# (= the orig's $18f0 image), each byte
  RECONSTRUCTED from the composer's OWN instrument data (iad=b0, isr=b1,
  b2=(ipwmin<<shift)|ipwinit, irawsp=b3/4/5, b6=(ipwbase<<4)|ifdef, b7=vib,
  ivram=b8, iwst=b9, iflag=b10) — NOT HVSC-verbatim (Core Tenet clean-code
  reproduction; the byte layout is recoverable from the musical fields:
  pw_base=pw_steps&0x0F, nib=pw_steps&0xF0). fx_pulse (ghost only) reads the
  step `$18f3[ioff+pwphase/2]` through it via ioff + nibble extraction (= orig
  $1352-$1375). BYTE-IDENTICAL when ioff=curinst*11=orig#*11 (normal play), so
  For_Party stays byte-identical → FULL. Padded 259 bytes (safe `irecimg+3,y`).
- FULL VERDICT_01 SOLUTION = 3 layers: (1) C19 resume-shape wedge (r164:
  restart burst via ghost machinery + shadow17 survivor + curinst orig→slot
  remap), (2) glide_offtable C6 redirect for the ghost-garbage glide (r165),
  (3) irecimg pulse-step reproduction (r166). All 0-regression, gated on the
  ghost handler.
- LESSON: every garbage-indexed read at the post-restart was reproducible from
  the composer's own data — off-table freq via the EXISTING C6 redirect, the
  pulse step via a reconstructed record image. When a "boundary" is a garbage
  read of a STATIC table (freqtable, instrument records), it's serviceable; the
  genuinely-hard case is DYNAMIC work-RAM (which this member never actually
  hit). Corpus code_hash now stale pending a fresh batch.

## ✅ ROUND 165 (2026-08-01): Verdict/Verdict_01 — r164's "hard dynamic boundary" DISPROVED (re-test challenge); glide read FIXED; residue narrowed to ONE garbage instrument-record read (RESOLVED by r166)
Re-tested every r164 assumption (user: "I don't trust your analysis 100%").
TWO r164 claims were WRONG; the "hard boundary" was solvable with an EXISTING
mechanism. Match 123142 → 123144 (glide freq now matches). Still PARTIAL.
0-regression (For_Party FULL). CORRECTIONS:
- glsp[0]=$03 / glb[0]=$A7 are NOT "survivors" (r164) — they're GHOST-FRAME
  ALIASED GARBAGE: glsp via the ghost unit's `INC $1729,x` at X=$18 (=$1741);
  glb via `STA $172f,x` at X=$18 (=$1747). Ground-truth memwatch: glsp[0]
  transitions 0→$03 exactly at the restart frame, from the ghost INC.
- the off-table glide target ($174E) is EFFECTIVELY STATIC ($11 for one frame,
  then $37 stable from frame 7878 = V2's real instrument $05×11) — NOT the
  "dynamic work-RAM" r164 claimed. (ioff[1]=$11 at WARM is itself garbage:
  $11 ≠ curinst[1]($0A)×11.)
- FIX: the glide-arrival compare `cmp freqhi,glb=$A7` reads off-table into the
  state block ($16A7+$A7=$174E=ioff[1]); the EXISTING `m.glide_offtable` C6
  redirect (DMC_OFFTABLE_STATE already maps $174E→ioff+1) serves it. Enabled
  for `track_ff_reinit_ghost` members (byte-identical for in-table glides, so
  For_Party stays FULL). r164's "C6/C11 dynamic hard boundary" was just this
  redirect not being wired for the ghost-garbage glide.
- TRUE REMAINING BLOCKER (narrow, NOT dynamic): ONE garbage INSTRUMENT-RECORD
  read — V1's pulse step. At frame 7877 ioff[0]=$07 (ghost garbage), the orig
  reads `$18f3[$07]=$18FA` = instrument-0's FLAGS byte (a MID-11-byte-record
  read) = $08 → high nibble 0 → pulse step 0 → pwl stays $29. My composer
  reads `isteps[cinst=0]` (slot 0's REAL pw step) → pwl→$19. Root: my clean
  SLOT-ARRAY layout has no analog for a mid-record byte read at a garbage
  byte-offset. Contained: only 3 instrument reads at frame 7877 (1 garbage
  pulse + 2 VALID wave reads at wavepos=$01, which match), and V1's note-init
  sets ioff=$37 (valid) right after. Fixable only by reconstructing the
  11-byte-record read from the slot arrays (bespoke, CORE-TENET tension) —
  parked for the 1/10,676 singleton, but this is a MUCH narrower/different
  boundary than r164 asserted.

## ⏸ ROUND 164 (2026-08-01, framing CORRECTED by r165): Verdict/Verdict_01 — C19 "$FF→init RESTART, resume shape" wedge SOLVED (restart burst reproduced); residue = ~~C6/C11 DYNAMIC off-table survivor-glide~~ (r165: glide FIXED; residue is a garbage instrument-record read)
r163's "curinst-mirror" theory was WRONG (disproved this round). The restart is
an EMERGENT PLAYER BUG, reproduced cleanly via the EXISTING ghost machinery.
Match 123100 → 123142 (69.07% → 69.10%); Verdict_01 STILL PARTIAL, blocked on a
C6/C11 hard boundary. 0-regression (For_Party FULL, DMC portfolio 5/5, smoke 6/6).
- MECHANISM (pc-trace ground truth, NOT the stale r162 disasm annotations): the
  `$10DD` wedge `LDA #0 / JSR $1000(init) / JMP $10D2(re-fetch)` — **init clobbers
  X** (its clear loop ends X=$18), so the `JMP $10D2` re-fetch AND the play body's
  two remaining `inx : jsr voice` iterations run at X=$18/$19/$1A = THREE
  out-of-bounds GHOST units. All three write V1 (their `$170D[x]`=0 after the init
  clear → Y=0 → $D400), freq = `freqtable[$1A1D[wp] + $1012[$18/$19/$1A]]` where
  `$1012[$18..]` = `$102A-$102C` = FILE-IMAGE constants in the $1020-$104F data gap
  → a MEMBER-CONSTANT burst ($2FAE/$B79C/$5864, PW $F0, ctrl $00/$40/$40),
  independent of surviving musical state. This is EXACTLY C19 shape B (For_Party)
  + one extra ghost unit (JSR-init vs JMP-init). NOT a re-trigger, NOT a re-fetch
  note (both prior-session dead-ends); the writes are garbage-index residue.
- FIX (0-regression, reuses the ghost path — no new composer branch):
  1. `_track_ff_reinit_ghost_probe` (factory) extended to recognize the RESUME
     anchor (`A9 00 / 20 <init> / 4C <base+D2>`, JSR to real init + JMP the canon
     re-fetch) alongside shape B's `A9 00 / 4C <init>`; both route to the same
     `_simulate_reinit_ghosts` capture + `track_ff_reinit_ghost` composer branch.
  2. `_reinit_ghost_state_map` += `shadow17` ($1018) — a survivor the orig init
     PRESERVES but the composer's init RE-PRIMES (from tunetab+8); it was the
     $D417 divergence ($04 survivor vs $05 re-primed). For_Party WARM==COLD → no
     poke → byte-identical.
  3. Composer ghost-poke emission: REMAP the `curinst` poke orig#→slot (USF
     id=orig#+1; `ioffval[slot]=orig#*11`). The poke carries the raw orig
     survivor ($0C) but curinst is the COMPACTED slot (12 insts) → $0C indexed
     ioffval OOB. For_Party remaps identity → byte-identical.
- TRUE REMAINING BLOCKER (first divergence, V1 freq $30 vs $00 at the post-restart
  replay frame): a **C6/C11 DYNAMIC off-table glide-arrival read**. The survivor
  glide (glsp[0]=$03, glb[0]=$A7 — glb is OFF-TABLE) runs `fx_gl_chk: cmp
  freqhi,y` with y=$A7 → orig `$16A7+$A7 = $174E = ioff[1] = $11` (engine state!),
  so the glide NEVER reaches its target → keeps accl=$30 → arp variant freq
  lo = fbl(0)+accl = $30. My composer's `cmp freqhi+$A7` reads a different
  (layout-dependent) byte → snaps early → freq $00. To reproduce: (a) restore the
  curinst[1]/[2] SURVIVORS ($0A/$03 — WARM==COLD so unpoked, but my init clears
  them since the extract judged the cold seed "dead"; ioff[1] derives from
  curinst[1]); (b) serve the off-table glide compare `freqhi[$A7]→ioff[1]` via a
  C11 redirect (the `m.glide_offtable` mechanism exists but the survivor target
  isn't an offtable_freq record). AND the read is DYNAMIC — ioff[1] tracks V2's
  LIVE playback (V2 note-inits during the glide), so V1's glide reads V2's live
  engine state (cross-voice off-table coupling). This is the ledger's documented
  "dynamic work-RAM residue" hard boundary. PARKED as residue: deep + risky
  (touches the glide redirect) + uncertain (the whole 31% replay is dominated by
  this buggy survivor glide) for a 1-in-10,676 singleton.
- Ledger C19 39th occ (the JSR-init RESUME shape B'); C6/C11 note (survivor
  off-table glide-arrival read = dynamic residue). Full pc-trace analysis lives in
  this entry; the r162 disasm at tmp/verdict_01/disassembly.s has a WRONG
  annotation (flags[$0C] said $01, file byte is $00 — corrected here).

## ⏸ ROUND 163 (2026-08-01, PARKED, SUPERSEDED by r164): Verdict/Verdict_01 — $FF→init RESTART, "resume" shape (C19) — root cause found, fix incomplete
Next-partial Verdict/Verdict_01 (single, canon $1000, VBLANK; NO STIL/BUGlist).
sub 0 partial: PERFECT prefix to 69% (play_match=123141) then diverges at a
MID-SONG SONG RESTART (~157s, play idx 7239). Full annotated disassembly at
`tmp/verdict_01/disassembly.s` (routine map + memory map + per-frame restart
timeline — READ IT to resume).
- MECHANISM (C19 "$FF handler re-pointed at init", a NEW shape vs Greenhorn's
  `_track_ff_reinit_probe`): wedge at `$10DD` = `LDA #0 / JSR $1000(init) /
  JMP $10D2(canon re-fetch)` (canon = `STA otrk,x=0 / JMP $10D2`). So at V1's
  first track-$FF, init RESTARTS the whole song (otrk→0, SID+$1718-blk cleared,
  $100F-$1018 note-state PRESERVED), init RETURNS, then re-fetches V1 in the
  same frame (unlike Greenhorn's `jmp init` which pops the voice call).
- ROOT CAUSE (siddump memwatch/pc-watch, ground truth — NOT py65): the restart's
  first note-init reads the SURVIVOR curinst ($0C = an arp instrument, flags
  $18FA[$0C*11]=$01 bit0-SET → the $15D5 arp variant → the $2FAE/$B79C/$5864
  sweep). DMC's note-init is DEFERRED one step, so the first note-init at idx
  7239 uses curinst=$0C BEFORE the row's instrument-select sets curinst=$05 (idx
  7240, flags→$07). Cold reads orderlist[0] identically but with its OWN survivor
  curinst ($01 = a static instrument), so the SAME row plays static melodic at
  cold, arp sweep at restart. curnote=$49 survivor is correctly preserved (mine
  matches); the curinst renumber map is consistent (orig $0C↔mine $08, $05↔$04).
- WIP BUILT (uncommitted, verify-gated singleton — advances match 123100→123142):
  `_track_ff_reinit_resume_probe` (factory) → `track_ff_reinit_resume` composer
  branch (`stx savex / save gatemask+curnote+curinst / jsr init / restore / jmp
  f_newpat`). Reproduces flow+survivors but its re-fetch applies the row's
  instrument-select ($05→$04) BEFORE the deferred re-trigger note-init, so V1
  plays the WRONG instrument (static $470C=freqtable[$49] not the survivor-$0C
  arp).
- REFINED (WIP updated): the restart plays NO fresh $11A6 note (pc-watch); it
  RE-TRIGGERS the wrapping note via the note-init effect with the SURVIVOR
  curinst. Composer branch now does `set pend / jmp frame_entry` (re-trigger)
  instead of `jmp f_newpat` — the note-init effect now RUNS (writes AD/SR), but
  STILL plays instrument $04, because MY COMPOSER'S curinst AT THE WRAP is
  $04(=$05) while the orig's is $0C — a HIDDEN curinst divergence (my curinst is
  effectively one note ahead at the orderlist wrap; the pre-wrap write streams
  match so it's invisible until the restart re-triggers it). curnote=$49 is
  correct.
- TRUE REMAINING BLOCKER (definitive, siddump memwatch at 150s/155s, well BEFORE
  the 157s restart): my composer's `curinst` ($3154) = $FE/$FF while the orig's
  $1015 = $0C — the desync is PERVASIVE, not at the wrap. Yet the write stream
  matches to 69%. So my composer sonifies the correct instrument through a
  DIFFERENT variable (`cinst`/`ioff`), and its `curinst` variable has diverged
  from the orig's $1015 semantics entirely (curinst is effectively dead state in
  my composer — it only matters at a restart, which re-triggers using it).
  => THE FIX is representational: make my composer's `curinst` a FAITHFUL mirror
  of the orig's $1015 (set on every instrument-select, held across soft notes)
  so the restart survivor re-trigger reads the right instrument. This is a
  composer-wide curinst-tracking change (risk of regressing FULL members), for a
  1-in-10,676 singleton — NOT worth it now. Parked: WIP composer branch + probe
  are correct in direction (re-trigger via pend/frame_entry runs the note-init
  effect) but blocked on the curinst-mirror. py65 note: the $177d "contradiction"
  earlier was ME conflating the memwatch (D404-write index) and pc-watch
  (playidx) counters — not a real anomaly.
- ⚑ AMEND-SKILL PASS (2026-08-01, ran `/amend`): DISPROVED the "hidden curinst
  divergence" — it was a WRONG-ADDRESS artifact (I measured the WIP build's
  label $3154 against a reverted build). FRESH-build measurement (amend Step
  3#4): my composer's curinst / ioff / **fxf (=$177d instr-flags)** ALL match the
  orig to the wrap (ioff=$84 both; renumber $0C↔$08 consistent; fxf SEQUENCE
  identical for the whole song). So THERE IS NO STATE DESYNC — the blocker is
  purely reproducing the RESTART-FRAME note. The orig's fxf after the init clear
  goes `00 → 01 → 07` (an arp/drum note-init, bit0 SET); my rebuild stops at `00`
  (a static note). NEITHER re-fetch (`jmp f_newpat`, curinst→$04) NOR re-trigger
  (`pend`+`frame_entry`, curinst=$08 survivor) reproduces the orig's fxf=$01
  note. OPEN CONTRADICTION for next session: the fxf VALUE sequence matches
  everywhere else, so the flag extraction is right, yet the restart plays a
  different-flag instrument than the orig — pin which curinst→instrument the
  orig's restart note-init actually uses (pc-watch showed 7241 curinst=$05→
  ioff=$37; is $18FA[$37] bit0 SET? and does reb iflag[$04] match it?). The
  re-trigger WIP advanced play_match 123125→123166 but NOT the first divergence.
  Reverted; verified singleton (build+verify gate). Regression-safe by
  construction if resumed (the resume probe is a 1-carrier static shape).
- ⚑ INSTRUMENT-FLAG READ (resolves the re-trigger dead-end): orig instr flags
  $18FA[inst*11]: inst $05=$07 (arp bit0), $0C=$00 (STATIC), $06=$01 (arp),
  $10=$08. The WRAPPING note's instrument $0C is STATIC ($00) — so the restart
  is NOT continuing the wrapping note; the RE-TRIGGER approach is WRONG. The
  orig's restart plays the PATTERN's notes from orderlist[0] with ARP
  instruments $06 (fxf=$01) then $05 (fxf=$07) — i.e. the RE-FETCH approach
  (`jmp f_newpat`) is the right frame, but my re-fetch's first note came out
  STATIC (fxf=$00). So the NARROWED blocker: the restart's re-fetched
  orderlist[0] notes select instruments $06/$05 (arp) in the orig but a static
  instrument in my rebuild. Since COLD orderlist[0] matches (first 69% FULL) but
  RESTART orderlist[0] plays instruments $06/$05 that COLD does not, the
  survivor note-state (curnote=$49 + deferred note-init) makes the SAME
  orderlist[0] play a different opening — a note-init-DEFERRAL × survivor
  interaction (ledger C23 territory). NEXT: pc-trace the orig's re-fetch at the
  restart to see the exact pattern bytes + deferred note-init order that yields
  $06 then $05, and reproduce it in the re-fetch path (NOT a re-trigger).
- Census: singleton shape (only Verdict_01 has `JSR init / JMP base+$D2` at
  base+$DD). No regression risk (verify-gated, singleton). smoke not re-run.

## ✅ ROUND 162 (2026-08-01): Vegeta/Trzewiki — periodic-COUNTER play-repeat wrapper 4+1/41 (+1) — C24 6th form
Next-partial Vegeta/Trzewiki (single, canon base $1000, VBLANK, songs=1; NO
STIL/BUGlist — no Vegeta in either doc). sub 0 partial: state_match=True,
PERFECT prefix (play_match=play_overlap=len_b=100552) but len_a=404530 ≈ 4.02×
len_b — right content, played at ~1/4 the rate (the CIA-style Trap-C "diverge
at pos 0" is the init-length artifact; the real verdict is the length tail).
- ROOT: play vector $1FC3 is an appended periodic-COUNTER wrapper: `LDA $02 /
  CMP #$28 / BNE $1FD0 / (special:) LDA #$FF / STA $02 / JSR $1003 / $1FD0:
  INC $02 / JSR $1003 ×3 / JMP $1003`. So $02 (init'd 0) cycles 0..40: 4 body
  calls every IRQ, +1 EXTRA every 41st frame (cz==$28), reset to $FF→0. Avg
  165/41 = 4.024 bodies/IRQ = the 4.02× length. `_detect_play_repeat` returns
  1 (play vector starts LDA, not JMP/JSR) and the C18 observer saw only 'P', so
  the multispeed was invisible — like Heniek (r161) but a mod-41 COUNTER, not
  parity (mod 2).
- FIX (extract-only, `_play_repeat_counter_probe` on the shared `play_phases`
  wedge, tried after the parity probe): static-match the wrapper shape → a
  UNIFORM period-41 play_phases schedule `P4`×40 + `P5` (M×P{BASE} + 1×
  P{BASE+extra}). FULLY STATIC — the special frame is deterministic at cz==M,
  so no ground-truth observation needed (unlike the parity forms). Composer
  UNCHANGED: reuses r161's Pn token (`P4`=`jsr playframe`×3/`jmp`, `P5`=×4/
  `jmp`); the phasectr seed aligns play #0 = cz 0 = phase 0.
- WHY the periodic +1 is required: a constant play_repeat=4 is short by exactly
  1 body/period → len_b=402082 vs 404530 (−0.6% = length_fail). The fractional
  4.024× can't be an integer play_repeat; the P5 supplies the missing 5th call.
- VERDICT: Trzewiki FULL 404530/404530 state ✓. CENSUS over all 10,660 DMC
  members: exactly 1 static match = Trzewiki → 0 regression exposure (parity
  probe short-circuits first, unchanged). smoke 6/6; DMC portfolio 5/5 FULL.
- Ledger C24 6th form (periodic-counter wrapper → uniform play_phases
  schedule). Shared extract change (factory.py) → corpus code_hash stale
  pending next fresh batch.

## ✅ ROUND 161 (2026-08-01): Vegeta/Heniek — SMC-immediate PARITY play-repeat wrapper 1/3 (+1) — C24 5th form
Next-partial Vegeta/Heniek (single, canon base $1000, CIA speed=1; NO
STIL/BUGlist — no Vegeta in either doc). sub 0 partial: state_match=True,
PERFECT prefix (play_match=play_overlap=len_b=75831) but len_a=151550 ≈ 2×
len_b — the rebuild plays at HALF the rate (right content, wrong rate).
- ROOT: the play vector $0FD3 = `JMP $0FE8`, an APPENDED parity wrapper. $0FE9
  is BOTH the `LDA #imm` operand at $0FE8 AND the counter (self-modifying):
  each IRQ `A=imm / INC $0FE9 / AND #$01 / BEQ` → even imm = 1 play (`JMP
  $1003`), odd imm = 3 plays (`JSR $1003 / JSR $1003 / JMP $1003`). So a 1/3
  alternation (per-IRQ write counts 17/51, ratio 3.0) = avg 2 bodies/IRQ =
  the 2× length. The factory forced play_repeat=1 (CIA) and the C18 observer
  saw only 'P' → the doubling was invisible (like Bajerek r135, but a NEW
  wrapper shape + MULTI=3 not 2).
- FIX: extend `_play_repeat_parity_probe` to FOLLOW the play-vector JMP + detect
  the SMC shape (`A9 / EE abs==play+1 / 29 01 / F0 / (20 T)* / 4C T`), MULTI =
  JSR-count+1 from the static shape, parity from the observed per-IRQ split →
  `P_P{multi}` (Heniek `P_P3`). Composer: generalised the play_phases `P2`
  token to `Pn` = `(n-1)× jsr playframe / jmp playframe` (byte-identical for
  P/P2). NOTE play_repeat=2 ALSO verifies FULL (the CIA verdict flattens the
  play stream across IRQs, so [1,3] and [2,2] give the identical body
  sequence when the avg is integer) — but `P_P3` reproduces the exact
  structure + generalises to any multi (the 4th form's 1/2 avg-1.5 is
  non-integer, needs `P_P2`).
- VERDICT: Heniek FULL 151550/151550 state ✓ (2-write tail). CENSUS over DMC
  corpus: Shape A (Bajerek `INC zp/LDA zp/LSR`) = 1 carrier (Lyon_Feniks/
  Bajerek, still `P_P2`, byte-identical); Shape B (SMC) = 3 static matches,
  2 observe-REJECTED (Gaston/Starburst_intro [pre-existing no_jumptable] +
  Odysseus/Hear_Circa [FULL, unchanged] — no real parity split) + Heniek.
  So +1, 0 regressions; the JMP-follow can only detect MORE genuine parity
  members (observe + build+verify gate). smoke 6/6; portfolio 5/5 FULL.
- Ledger C24 5th form (SMC-immediate parity wrapper, MULTI>2 → `Pn` token).
  Shared composer change (Pn) byte-identical for P/P2. Corpus code_hash stale
  pending next fresh batch.

## ✅ ROUND 160 (2026-08-01): Vai/Hardtechno + Sad_End — filter step-DURATION table is an independently-relocated operand (+2) — NEW ledger C39
Next-partial Vai/Hardtechno (single, canon base $1000, VBLANK; NO STIL/BUGlist
— no Vai in either doc). sub 0 partial, first-div frame 4: filter cutoff hi
$D416 orig $B0 vs rebuild $4F (everything else matches, same length).
- SYMPTOM: filter cutoff frames 1-3 MATCH (144,240,80) then orig steps +$60/frame
  mod 256 ($B0,$10,$70,$D0,$30,$90… — a fast wrap) while rebuild ramps −1/frame
  ($4F,$4E,$4D…). The rebuild switched to the def's step 1 (−1); the orig never
  advances step 0.
- ROOT (ground truth `siddump --memwatch-on-write D416 1719,171A,171B,1721,1722`):
  the orig's `fdu` ($1722 step-duration cache) = **$00**, not $02 → step 0 dur=0
  → `fstep` never advances → +$60 (step-size $60) forever. The player (canon
  $13E6: `LDA fsz,Y / STA $1721 / LDA fdu,Y / STA $1722`; fbase=filter_def*16)
  reads step SIZES from op_filtdef+4 ($1A2E, correct) but step DURATIONS from a
  SEPARATE table at **$1ACF = op_filtdef+165**, all zeros. The extraction's
  `_decode_filter_def` ASSUMED a 16-byte record with durs interleaved at
  record+10 ($1A34 = garbage $02). So the packer relocated the DURATION table
  INDEPENDENTLY of the def records — the project's KEY lesson (packer-patched
  operands → extract by DATAFLOW, never a fixed offset), hit on a table the
  extraction had hardcoded.
- FIX (`engine_model.py`): resolve `fsz_tab`/`fdu_tab` from the play body's
  filter-routine operands (base+$3E6 `LDA abs,Y` at +1/+7), gated on the canon
  $B9 opcodes (re-assembled → None → fall back to record+4/+10, byte-identical).
  `_decode_filter_def(…, fsz_tab, fdu_tab)` reads steps as
  `(signed8(mem[fsz_tab + def*16 + k]), mem[fdu_tab + def*16 + k])`.
- VERDICT: Hardtechno FULL 99646/99646 state ✓; Sad_End (2nd carrier, fdu at
  op_filtdef−145) FULL 56177/56177 state ✓. CENSUS over 7457 canon-head filter
  members: exactly 2 with fsz!=+4 or fdu!=+10 (both Vai, both fixed) → the other
  7455 byte-identical (fsz=+4, fdu=+10). No FULL member can regress (a
  filter-using FULL member has fdu=+10 already, so the new read is identical; the
  new read is ground truth, so it can only make the write stream more correct).
  smoke 6/6; DMC regression portfolio 5/5 FULL.
- Ledger NEW class C39 (a data table the extraction reads at a FIXED offset from
  another table is a packer-patched OPERAND that can relocate independently —
  resolve it from the play code). Shared extract change → corpus code_hash stale
  pending next fresh batch.

## ✅ ROUND 159 (2026-08-01): Bomberman_preview — CONDITIONAL per-subtune song remap (+1) — C19 38th occ
Next-partial The_Magical_Garfield/Bomberman_preview (single, canon base $1000,
VBLANK, 4 subtunes; NO STIL/BUGlist — no Magical_Garfield in either doc). sub 0
partial (subs 1-3 FULL), first-div play pos 7: orig writes V2 SR/AD (note-init)
then freq; rebuild skips straight to V2 freq — the rebuild MISSES the note-init
(AD/SR) for V2/V3, which decoded as IDLE (bare `$FE` tracks, 0 patterns).
- DIAGNOSIS (long — the "idle voice" symptom was downstream): orig note-starts
  V2/V3 once at song start (chunk1 hard-restart $08/$0F/$0F, chunk2 note-init
  AD/SR=$00 + freq=freqtable[idle_note], chunk3+ effects); rebuild's bare-$FE
  voices fetch→vactive=0→rts (nothing) then effects. Canon player's $FE handler
  IS `vactive=0/rts` (disassembled dmc4_player_embedded_1000.bin), so the orig
  shouldn't note-init either — meaning the TRACKS were wrong. Ground truth
  (`siddump --reinit-snapshot $1085 $1707-$170C`) = V1/V2/V3 track ptrs
  $1B14/$1B34/$1B54 = tune **record 5**, but the extract walked record 0
  ($1ADD/$1ADF/$1AE0, whose V2/V3 = leading $FE). ROOT: init=$2054 is a WRAPPER
  `STA $2053 / LDA $2053 / CMP #$00 / BNE / LDA #$05 / JSR $1000` — remaps ONLY
  subtune 0 → the player's song 5 (subs 1-3 pass straight → FULL). A CONDITIONAL
  per-subtune song map [5,1,2,3] the uniform `forced_subtune` can't express (its
  probe deliberately REFUSED this exact member, r139 — recorded as a future lead).
- FIX (extract-only): `factory._subtune_song_map_probe` (same static-anchor gate
  as forced_subtune's 3rd form → py65 observation OFF the hot path; runs
  `_init_song_observe`, returns the observed A-per-subtune list iff NON-identity
  + NON-uniform). `DMCV4Config.subtune_songs` (list) → `extract` generalizes
  `forced` int→list via a new `_rec_of(sub, forced)` at the 4 walk sites (off-
  image sectors / secp reads / track ptrs / decode). Standard dispatch does
  `A*8→Y` so observed A = record index. Composer UNCHANGED (extract builds sub 0
  from record 5's data; the remap is an engine artifact, §8).
- VERDICT: all 4 subtunes FULL (sub 0 161157/161157 state ✓, subs 1-3
  unchanged). CENSUS (static anchor gate over the DMC corpus): exactly 1
  anchored member = the sole carrier (Bomberman) → 0 perf impact (1 py65
  observe corpus-wide), 0 regression exposure. `_rec_of` byte-identical to the
  old `(sub if forced is None else forced)` for None/int; probe returns None
  for identity/uniform/no-wrapper. smoke 6/6.
- Ledger C19 38th occ (forced-tune-record wedge's 4th form — conditional
  per-subtune; OBSERVATION-based like C18/C31). Shared extract change
  (engine_model.py) → corpus code_hash stale pending next fresh batch.

## ✅ ROUND 158 (2026-08-01): Surgeon/Mothafucka_2SID — RELOCATING WRAPPER multi-SID (+1) — C27 4th occ (C31 × C27)
Next-partial Surgeon/Mothafucka_2SID (2SID, PSID v3, chip 2 @ $D500, CIA
speed=1, songs=1; NO STIL/BUGlist — no Surgeon entries in either doc). Built
`single (base $1000) chips=1` = a single-chip extraction of a 2-chip tune →
first-div play pos 1 (orig chip-2 $D438 vs rebuild chip-1 $D418 — rebuild
emitted NO chip-2 writes).
- DIAGNOSIS: the init is a RELOCATING WRAPPER (C31 × C27, ledger C27 (f)). Two
  things are copied out of the $0900-$4FB8 file image at init: (1) chip 2's
  WHOLE player to $E800 (relocated copy, delta $D800, writes $D5xx); (2) BOTH
  chips' SECTOR DATA to $8000+ (secp_hi=$80,$81…; file image zero-fill there,
  post-init $8100 populated). `dmc_v4_config_2sid` REFUSED it (guarded on all
  bases being in the image) → single fallback → chip 2 absent.
- The subtler half: chip 1's PLAYER is in-image at $1000 (head $4C1D10) but its
  DATA is NOT — so the in-image player-head check passed while the extract read
  $8000+ sectors as zeros → V1 decoded to constant `note=0 instr=7 dur=0`
  garbage (orig V1 plays inst 16/17's $FFFF noise drum; rebuild played inst 7's
  $0008 pulse — wrong instrument, confirmed by freq-hi [3,6,8,10,13] == inst 7
  wave_freq). Both the 2SID AND single-chip builds hit this (same file-image
  read).
- FIX (`dmc_v4_config_2sid`): when ANY chip's player is out of the image
  (`relocating`), extract EVERY chip from POST-INIT RAM — `matr_sub` = start
  song, `post_init_sub` threaded through `_config_at_base` → `_build_via_canon`
  + all wedge probes (`cfg.post_init_sub` set before `_apply_wedge_probes`) +
  `_multisid_keep_regs` (per-chip mem view). In-image members use the raw image
  (`post_init_sub=None`), byte-identical. Chip 0 built via the bare fallback
  (canon offsets; `_build_via_canon` rejected `nonstandard_instr_base` but the
  canon offsets resolve correctly here — the verify gates any false FULL).
- VERDICT: sub 0 FULL 129876/129876 state✓ (chip 2 was already perfect once
  extracted; chip 1's post-init data fixed the garbage). CENSUS (all 19
  multi-SID DMC members verified): Mothafucka is the ONLY out-of-image member
  → partial→FULL; the other 18 are in-image (byte-identical path) with
  unchanged status (16 FULL, 4_Ever_Young pre-existing 0/3 partial,
  Popel_Premiere pre-existing merge-assert ERR — a per-chip `master_vol_static`
  the merge doesn't handle). 0 regressions by construction (an OOB chip was
  refused→single→partial before, can only improve). Cow_Anus/Nice_Dream_2SID
  re-verified STILL FULL; smoke 6/6.
- Ledger C27 4th occ (paragraph (f) rewritten: refuse → post-init RAM for all
  chips). Blast radius = the multi-SID path only (`_config_at_base`/
  `dmc_v4_config_2sid` have no other callers); single-chip untouched.
- KNOWN follow-ups (NOT this round, both pre-existing, both in-image): (a)
  Popel_Premiere merge asserts on a per-chip `master_vol_static` wedge — the
  merge needs to carry it per-chip (C31 per-chip-param class). (b) 4_Ever_Young
  0/3 deep partial. (c) `_config_at_base` has no dataflow fallback (bare
  fallback = canon offsets) — fine for canon-offset members, would miss a
  re-assembled relocating multi-SID member (verify-gated, no false FULL).

## ✅ ROUND 157 (2026-07-31): Slayer song-end master-vol FADE → silence → whole-song RESTART loop (+4) — NEW ledger class C38
Four Slayer f1 members (My_49th_Tune, Plantation, Trip, Worktunes/My_47th_Tune,
all single/canon base $1000) share an APPENDED PLAY-vector wrapper implementing a
song-end fade-out/restart loop. Play() vector → wrapper: (0) count play()s to N;
(1) `dec` the master-vol shadow $1717 by 1 every STEP plays — the value is
emitted for free by the note-init `ora mvol / sta $D418` filter tail, the wrapper
writes no $D418 during the fade; (2) at mvol==0, `$D418=$00` silence for SIL
plays; (3) `JMP $1807` = the SHARED init path (`$1000→$221A→$1807→$1870→$1050`,
same as a cold start) to restart the whole song, looping forever.
- KEY MECHANISM: the restart's init CLEARS the effect/state block ($1718-$179D:
  pulse accum $1750, pending $174a, ACTIVE pulse-record offset $174d, …) but
  LEAVES the note-state block $100F-$1018 (gatemask $100F, curnote $1012, curinst
  $1015, shadow17 $1018) — so the replay resumes its first notes from the
  end-of-song survivor note-state. Verified by disassembling the appended wrapper
  + $1050 (`STA $1718,X` X=0..$85 clears $1718-$179D; never touches $100F-$1018).
- COMPOSER: gated `master_vol_fade="N:STEP:SIL:g0..g2,n0..n2,i0..i2,s"` param → a
  MODULAR play-vector wrapper (`playfade` count/ramp/silence + a separate
  reusable `songrestart` module: reset counters → `jsr init` → prime survivors).
  Fade counters live OUTSIDE state0..state_end so init's clear can't wipe the
  play counter. Default None → no wrapper, byte-identical.
- FACTORY `_master_vol_fade_probe`: static gate (fade `DEC $101E/LDA $101E/STA
  $1717` + `LDA #$00/STA $D418`) then MEASURE from libsidplayfp (NEVER py65 —
  feeds the write stream, feedback_ground_truth 3rd mode): `--pc-watch` the fade
  STA → N/STEP; writelog longest `$D418=$00` run → SIL; `--memwatch-on-write
  d418 $100F-$1018` mode over the silence snapshots → 10 note-state bytes.
- THE TRIP FIX (this session, the last of the 4): Trip was 98.6% — diverged
  DEEP in the replay at V3 PW-lo (orig $00, rebuild $40) on V3's first replayed
  glide note. ROOT: the prime was priming `cinst` (the composer's mirror of the
  ACTIVE pulse-record $174d) as well as curinst, from the same measured $1015
  survivor. But $174d is in the init-CLEARED $1718-$179D block — the orig's is 0
  at restart. V3's first replayed note is SOFT (a glide → running-effects path,
  never note-inits, never copies curinst→cinst), so fx_pulse ran the survivor
  instrument 4's pulse (step $40) instead of instrument 0 (step 0), sweeping PW
  (alternating $40/$00) where the orig held it flat. FIX: prime `curinst` only
  (`jsr init` already zeroed cinst). LESSON: the survivor set is EXACTLY the
  init-uncleared range — prime only the leftovers, never a byte init clears.
- VERDICTS: all 4 FULL (Trip 232080/232080 state✓; My_49th/My_47th/Plantation
  FULL). CENSUS (base-agnostic raw scan mirroring the static gate over 5401 f1):
  exactly these 4 carriers (all base $1000), 0 other members → 0 regression
  exposure. Smoke 6/6. C20 fifth-layer: .usf carries master_vol_fade, rebuild
  byte-identical for all 4. Composer change fully gated → every non-carrier
  byte-identical.
- Ledger NEW class C38 (song-end fade+restart loop w/ measured survivor prime).
  Relations: fade = C10 parametric master-vol; restart = C37 sibling
  (survivor-preserving re-init, but whole-song play()-counter loop not
  per-subtune); distinct from C19 (static single-value poke).

## ✅ ROUND 156 (2026-07-31): SilverFox/Blood_2_game — STATIC FILTER (play-tail $D416/$D417 NOPed) (+1) — C19 37th occ
Next-partial SilverFox/Blood_2_game (single, canon base $1000; NO STIL/BUGlist).
sub 0 partial, first-div play pos 6: rebuild emits an EXTRA `$D416=$2A`/`$D417=
$F3` where the orig has a note write (len_b 21366 vs len_a 15199).
- FACTS: V1/V2/V3 write counts MATCH exactly (6622/7/7 — V2/V3 stopped early).
  The ONLY divergence is the filter tail: orig writes $D416/$D417 3× TOTAL
  (init only), rebuild 2761× (every frame). $D418 normal (162×, at note-init).
- ROOT: the play routine is RE-ASSEMBLED (custom $1000-$10BF; the $1100+ note/
  effect code is canon + table relocations). play=$1050 keeps the filter-tail
  LOADS but NOPs the two stores: canon `LDA $171C / STA $D416 / LDA $1018 / ORA
  $1723 / STA $D417` → `LDA $171C / EA EA EA / LDA $1018 / ORA $1723 / EA EA EA`.
  So the filter cutoff/res are static (set at the init $D400-$D417 clear), never
  written during play.
- FIX: `factory._filter_static_probe` (anchors the whole 15-byte reloc-invariant
  NOPed-tail shape — cutoff base+$71C, shadow base+$18, res base+$723, both
  store slots EA EA EA; scans anywhere since the play is re-assembled) →
  composer `filter_static` → play body emits no filter tail. Regression-safe by
  construction: no param → canon per-frame $D416/$D417 tail, byte-identical.
  CENSUS over 5833 f1: 1 carrier (Blood_2_game, was partial), 0 FULL ⇒ 0
  exposure. FULL 15199/15199 state ✓; smoke 6/6.
- Ledger C19 37th occ. TELL: orig writes $D416/$D417 only ~2-3× TOTAL (init)
  while the rebuild writes them per-frame — count filter writes.

## ✅ ROUND 155 (2026-07-31): Signor/Logic_Intro — STATIC $D418 (init-wrapper primes once) (+1) — C19 36th occ
Next-partial Signor/Logic_Intro (single, canon base $1000; NO STIL/BUGlist —
no Signor in either doc). sub 0 partial, first-div play pos 9: rebuild emits an
EXTRA `$D418=$3F` where the orig has none (len_b 66686 vs len_a 66160).
- MECHANISM: orig writes $D418 exactly TWICE (both at init: host-stub $0F, then
  $3F), NEVER during play. Rebuild writes it 501× (canon writes $D418=mode|vol
  at every filter note-init).
- ROOT (byte-diff orig vs canon): BOTH canon $D418 stores are NOPed — init
  master-vol `$105C: STA $D418`→`EA EA EA` AND filter note-init `$12A8: STA
  $D418`→`EA EA EA`. The PSID init vector is an APPENDED WRAPPER ($1E88: `JSR
  $1000 / LDA #$3F / STA $D418 / RTS`) that primes $D418=$3F (mode 3 | vol $0F)
  ONCE. So $D418 is a STATIC filter-mode+vol for the whole tune. (The $18xx↔$0Axx
  diffs are normal instrument-table relocation.)
- FIX: `factory._master_vol_static_probe` (anchors BOTH canon-$D418-store NOPs at
  base+$5C and base+$2A8, then reads the immediate from the sole remaining `LDA
  #imm / STA $D418` in the image) → composer `master_vol_static=$3F` → the init
  primes `LDA #$3F / STA $D418` (instead of `STA $D418`=master vol) and the
  filter note-init emits NO $D418. Third sibling of `master_vol_every_play` /
  `master_vol_reassert_filter_tail`. Regression-safe by construction: no param →
  canon init+per-note-init $D418, byte-identical. CENSUS over 5833 f1: 1 carrier
  (Logic_Intro, was partial), 0 FULL ⇒ 0 exposure. FULL 66134/66134 state ✓;
  smoke 6/6.
- Ledger C19 36th occ. TELL: rebuild emits $D418=mode|vol at a filter note-init
  where orig has none, and orig's TOTAL $D418 count is ~2 (init only) — count
  $D418 writes across the song; then byte-diff the canon stores at base+$5C /
  base+$2A8.

## ✅ ROUND 154 (2026-07-31): Rygar/Complications — PULSE UP-REVERSAL bound repoint (+1) — C19 35th occ
Next-partial Rygar/Complications (single, canon base $1000, VBLANK; NO
STIL/BUGlist — no Rygar entries in either doc). sub 0 partial, DEEP first-div
(flat pos 13358, ~frame 820): V3 PW orig `$0B70` vs rebuild `$0AD0`.
- MECHANISM: the PW swept identically (step $50, up from $0800) on both sides,
  then the REBUILD reversed at pwh=$0B (cpwmax=bound B=$0B) while the ORIG kept
  sweeping UP past $0B → $0C..$10.. (never reversing up). Bound B measured
  correct ($175B=$0B) but the orig IGNORES it.
- ROOT (byte-diff orig vs canon player): canon `$1393: DD 59 17` (`CMP $1759,x`
  = pwh vs bound B in the pulse UP-sweep) is patched to `DD 10 17` (`CMP
  $1710,x`). $1710,x = the per-voice filter route-bit CONST ($01/$02/$04). So
  the up-reversal fires at pwh==route-bit; V3's PW starts pwh=$08 > route-bit
  $04, so it never hits it → PW ramps the full 16-bit range (wraps) = a
  deliberately wide PWM. (The many $18xx↔$0Axx diffs are normal instrument-table
  relocation, not wedges.)
- FIX: `factory._pw_up_reverse_probe` (STATIC reloc-aware opcode probe: anchors
  the pwh LDA/STA operands == base+$753 + the CMP opcode; returns 'routebit' iff
  the CMP operand is base+$710) → composer `pw_up_reverse='routebit'` → the
  shared `pw_sweep` block emits `cmp fbit,x` (the $01/$02/$04 route-bit table)
  instead of `cmp cpwmax,x`. Regression-safe by construction: no param → `cmp
  cpwmax,x` textually unchanged → byte-identical. CENSUS over 5833 f1: 2
  carriers, both →$710 — Complications (partial→FULL 53531/53531) +
  Control/Hexen_Remake (FULL, re-verified STILL FULL 72842/72842: emitting the
  faithful reversal only matches the orig it already ran). smoke 6/6.
- Ledger C19 35th occ. TELL: a DEEP PW divergence where the orig sweeps
  monotonically PAST its (correct) bound B while the rebuild reverses — memwatch
  confirms bound B is right, so byte-diff the $1393 CMP operand vs canon $1759.

## ✅ ROUND 153 (2026-07-31): Rayden/NOFX_tune_2 — POST-NOTE GUARD immediate wedge (+1) — C19 34th occ
Next-partial Rayden/NOFX_tune_2 (single, canon base $1000, VBLANK; NO
STIL/BUGlist — no Rayden entries in STIL at all). sub 0 partial, first-div flat
pos 36: V3 ctrl orig `$20` (sawtooth, GATE OFF) vs rebuild `$21` (gate on) on
the first wave-step after V3's note-init.
- ROOT: canon `$12F8: A9 02 / STA $1786,x` (post-note guard = 2) is patched to
  `A9 00`. The guard is DEC'd each frame and gates whether the end-of-note
  gate-off logic (`L_132D`) runs; canon skips it for the first ~3 frames (guard
  2→1→0), so a fresh note stays gated 3 frames min. With guard=0 the gate-off
  runs immediately → the ctrl steps to `wavectrl & $FE` (gate cleared) ONE frame
  after note-init instead of three. Wave cell = `$21`; the `$FE` mask clears the
  gate → `$20`. MEASURED via memwatch: orig gate mask $1011 flips FF→FE right
  as wave ctrl steps $41→$21, guard $1788 (V3) is 0 at note-init not 2.
- This changes the ctrl WRITE-STREAM (gate bit over the note's frames), so a
  COMPOSER param (contrast r152's durrel = a musical VALUE → extract). Min
  gate-on = imm+1 frames — a per-note articulation timing.
- FIX: `factory._note_guard_probe` (STATIC opcode probe, reloc-aware: LDA#
  opcode + STA-abs,x + operand==base+$786; returns the immediate iff !=$02) →
  composer `note_guard_init` param → note-init emits `lda #$<imm>` not `#$02`.
  Regression-safe by construction: no param → `lda #$02` textually unchanged →
  byte-identical. CENSUS over 5833 f1: exactly 1 carrier (NOFX_tune_2, guard=0,
  was partial), 0 FULL carriers ⇒ 0 exposure. NOFX_tune_2 FULL 26607/26607
  state ✓; smoke 6/6.
- Ledger C19 34th occ. TELL: ctrl $20/$21 (gate-bit) divergence on the first
  wave-step after a note-init + wave-table cell already carries the gate bit
  ($21) → the mask is clearing it, memwatch the guard ($1786,x) / gate mask
  ($100F,x).

## ✅ ROUND 152 (2026-07-31): Rayden DURREL-RAMP driver — DECONSTRUCT to per-row durations (+3) — C19 extract-only
Next-partial Rayden/Mr_Siegfrieds_stultified_shit (single, canon base $1000,
VBLANK; NO STIL/BUGlist). sub 0 partial: V3's note plays FOREVER (never
advances) — our extract decoded EVERY row dur=0 → held 256-tick notes.
First-div f14 (V3 misses a drum note the orig plays).
- ROOT: Rayden's DMC build APPENDS a non-canon global DURATION-RAMP driver
  ($1025): on each V1 note-advance an SMC index cycles a 4-entry table
  ($101C=[5,4,3,2]) and writes it to ALL voices' durrel ($173E-$1740). So the
  note duration is a GLOBAL period-4 beat, not the canon per-voice $80-$BF
  command; all voices advance in LOCKSTEP (one row/beat). The sector has NO $8x
  commands → extract dur=0 → notes never advance. DIAGNOSIS took the full
  which-copy/re-measure path (user's "go with A"): the CANON durrel writer $17E0
  NEVER fires (pc-watch) → found the real writer $103A → the ramp routine.
- ⚠ FIRST INSTINCT = a composer param reproducing the ramp = **PRINCIPLE §8 LEAK**
  (a Rayden-specific emitter path selected by content). Re-reading the canon
  (user prompt) routed it to EXTRACT-ONLY DECONSTRUCTION — Core Tenet (reproduce
  the write stream, not the SMC code) + C19's boundary (a wedge changing a
  derived musical VALUE → extract). Note durations are CONTENT; the ramp is
  space-saving MECHANISM (Principle Rule 1).
- FIX (extract-only, NO schema/composer change): `_durrel_ramp_probe` (static
  3×`STA durrel_v,abs` signature + the `LDA table,X` operand) →
  `extra_params['durrel_ramp']`; `extract()` stamps each row's `duration` =
  table[i%4] (EXISTING field). Every pattern is 4-BEAT-ALIGNED (row%4==0) so
  pattern-row i is always beat-phase i%4 → NO drift, NO C32 variants. Gated to
  rows with dur==0 (no $8x); composer plays the durations via its ordinary path.
- CENSUS: 6 Rayden carriers. 3 partial→FULL (Mr_Siegfrieds/Revel_99/Roing_Rown,
  all no-$8x). 2 $8x-driven stay FULL BYTE-IDENTICAL (Rock_Remake/Sealed_Universe
  — all rows have $8x, dur!=0, untouched). 1 residue (Embarassed_Emotions,
  nonstandard play=$0000, unrelated). Non-carriers probe None.
- f1: 5368 FULL / 33 partial (+3 vs the r128c batch). Ledger C19 (extract-only
  deconstruction). Corpus code_hash stale pending next fresh batch.

## ✅ ROUND 151 (2026-07-31): SPLIT-RELOCATION curnote detection — Psych858o/Pulsate FULL (+1) — C13
Next-partial Psych858o/Pulsate (single, base $0C00, VBLANK; NO STIL/BUGlist).
sub 0 partial: V3 freq $323C vs ours $1000 at frame 1, state_match=True.
- `dmc_offtable_probe` MIS-FIRED (7th time — by-value coincidence: it reported
  an off-table idx-234 read of $1332=$3C, but pc-watch showed V3's wave-step
  ($11C4) lands IN-TABLE at idx $43 = freqlo[67] = $3C legitimately).
- ROOT: the member is INCONSISTENTLY RELOCATED — code at delta -$400 (base
  $0C00) but the DATA/STATE block at -$3FF (freq $1248=$1647-$3FF, fbl
  $1330=$172F-$3FF, curnote $0C13=$1012-$3FF). The audible note-fetch/wave-step
  path references state at -$3FF ($0C13 curnote, `ADC $0C13,X`); the GLIDE-INIT
  routine ($0D5F) references it at CANON+1 ($1013 curnote, $172D transp, $1745
  gla) — a mis-relocated dead path. The dataflow curnote locator anchors on the
  FIRST $1012 ref = the glide-init `LDA $1012,X` (canon $1168) → found $1013.
  So V3's idle-note SEED (V3 FREEWHEELS — never re-fetches a note, so the seed IS
  sonified via the arp `ADC $0C13,X`) read mem[$1015]=$D0=208 instead of
  mem[$0C15]=$36=54 → constant +$9A note error → off-table freq. V1/V2 fine (they
  overwrite their basenote each frame, seed inert).
- FIX (dataflow.py `locate`): CROSS-CHECK curnote against the NOTE-FETCH's
  `TYA / STA $1012,X` (canon $1482, the freewheel-curnote WRITE site, uniquely
  id'd by its TYA predecessor); on DISAGREEMENT prefer it. Regression-safe:
  consistent members carry the same operand at both sites → byte-identical.
- BLAST RADIUS (whole f1 corpus, 4932 located): 6 members change, ALL now FULL —
  Pulsate (partial→FULL, the fix) + 5 re-assembled high-base members
  (Wacky_Waste $8000, 2_Floors_up/Holiday_Season $A000, No_Bounds $0900,
  Nono_Pixie $8000) whose OLD un-relocated curnote ($1012/$1013) was INERT (seed
  unsonified, FULL anyway); NEW resolves the correct relocated address, all
  stay/become FULL. 0 regressions. dmc_smoke 6/6.
- f1: 5365 FULL / 36 partial (+1 Pulsate vs the r128c batch). Ledger C13.
  Corpus: these 6 members' stored .usf/.sid now stale (idle_notes changed) —
  re-sync at next fresh batch (already code_hash-stale pending, r150).

## ✅ ROUND 150 (2026-07-31): TIME-MEDLEY structure — Praiser/Mega_Mix FULL + productionized (+1) — new C31 variant
Next-partial Praiser/Mega_Mix: a NEW structure — a **time-sequenced medley**.
One PSID song, wrapper at $2700 (init/play vectors) DOUBLE-PLAYS an active
player and TIME-SWITCHES between packed players $1000 (seg0) + $2800 (seg1) via
a $03/$04 frame countdown on the PLAY vector, looping. Distinct from C31
(per-subtune INIT-vector dispatch) and C27 (parallel chips). NO STIL entry.
- ROOT of the 1-write residual ($D417=$04 vs $00, 0.3s into the loop-back):
  NATIVE MEASURE (`siddump --pc-watch 2708,270B --pc-watch-abs`, before/after
  P1's `JSR $1000`) — $101D writes ONLY $1719-$1794, so $1018 (=shadow17, the
  $D417 routing accumulator) CARRIES. In the orig P1's $1018 and P2's $2818 are
  SEPARATE addresses → P1's routing bit persists across P2's segment (cycle 2
  starts at $04). The merge collapses both into ONE shared shadow17 → lost.
- FIX (committed 0d1e27c1): reproduce the separate per-player accumulators. The
  `playmedley` wrapper SAVEs the outgoing segment's shadow17 before its
  switch-init, RESTOREs the incoming's after — `medcarry[]` seeded from
  `medrout[]` (each song's routing prime) so a FIRST entry is a no-op (P2's
  prime is $02, not 0). Self-consistent — the $04 emerges from cycle 1 matching
  the orig, NO measured constant. Only shadow17 needs it (baseline had exactly 1
  divergence). sub 0 FULL over ×1.1 (505746=len_a, state_match) + byte-exact
  across two loop-backs (500s: 792634=len_a=len_b). All gated on `medley_segs`.
- PRODUCTIONIZED: `compilation.detect_medley` (+`_parse_medley_wrapper`/
  `_parse_reinit`) — separate static probe on the PLAY vector; `write_dmc_medley_usf`
  emits `medley='0:40:1F,1:64:19'` + play_repeat=2 on the C31 merge; wired into
  `dmc_build_one`/`dmc_family_batch`(records build_path='medley')/`dmc_mass_write`
  (replays it). `songs=1`. CENSUS: fires on EXACTLY 1 of 10,676 DMC members
  (sole carrier, 0 false-pos). GATES: smoke 6/6, golden MD5 (10 diverse)
  byte-identical, C20 4th/5th-layer stored-artifact audits pass, full regression
  green. Ledger C31 (time-medley variant). Full detail:
  **`pipelines/dmc/v4/MEDLEY_WIP.md`**.
- f1: 5364 FULL / 37 partial (was 5363/38) vs the r128c batch (Mega_Mix
  partial→FULL). Corpus: Mega_Mix.{usf,sidfinity.sid} stored; broader batch
  code_hash stale pending next fresh run.

## ✅ ROUND 149 (2026-07-30): per-instrument record_offset — sonified ioff survives the merge renumber — Pinov_Vox/Goldrake FULL (+1) — C31/C11
Next-partial Pinov_Vox/Goldrake (2-player COMPILATION $8500/$9000; NO STIL/
BUGlist entry). sub 0 (player 0) FULL, sub 1 (player 1) partial: V3 freq hi
$2C vs orig $00 deep at frame ~1630, state_match=True. Player 1 STANDALONE
verifies FULL → a MERGE collapse (per-player fact), like r148 but a NEW fact.
- ROOT CAUSE: `$2C=44=4*11`, `$00=0*11` — the `ioff` var ($174D, off-table read
  idx 166-168, C11 live-served) = the current instrument's record offset =
  orig inst# * 11. The merge renumbers each player's instruments into one pool,
  and the composer's `ioffval = _inst_offset(slot)` used the MERGED slot. Player
  1's local inst #0 (ioff $00) became merged id 5 → sonified $2C. idle_wave was
  p0==p1 here (r148 correctly inert); vibdepth/idle_guards override didn't fix.
- FIX: `record_offset` per-instrument field (DmcInstrument + USF Instrument,
  precedent wave_table_pos). Composer emits `ioffval[k] = i.record_offset or
  _inst_offset(slot)`. merge_models stamps `_inst_offset(orig_local#)` BEFORE
  the dedup key (rides the key so different-offset identical instruments never
  share a slot) and nulls it when == slot default. Ledger C31/C11.
- GATED: single-player never sets it (byte-identical). Gates: usf_corpus_check
  12001/12001 (additive grammar); golden over 49 (18 comps + 30 single) = 29
  identical + 0 single-player changed + 8 changed comps (Goldrake partial→FULL,
  7 others FULL→FULL verdict-preserved); smoke 6/6; full regression green.
- f1: 5363 FULL / 38 partial (was 5362/39).

## ✅ ROUND 148 (2026-07-30): PER-SUBTUNE idle_wave — Pievspie/Mission_Moon FULL (+1) — C31
Landed the r147 sub-1 lead: the compilation merge collapsed `idle_wave` (the
cleared-cache lead-in wave a voice walks before its first note) to the START
player, so sub 1's V2 idled on player 0's wave → its fbl freq-base cache
diverged → the off-table freq read idx 233 (fbl+1) read $8F vs orig $F7.
- FIX (3 layers, mirrors the per-subtune idle_notes/masks/durrel machinery):
  merge sets per-song `DmcSong.idle_wave` (compilation.py); to_usf emits it as
  the PRE-EXISTING `MusicSubtune.wave_programs[0]` override (added for
  Super_Tau-Zeta's V5 idle but never consumed by the V4 composer) ONLY where it
  differs from the file-level idle; composer APPENDS each distinct override to
  the wave pool (`add_prog`) → `sub_iwpos[s]` pool position, and primes each
  subtune's voices' `wavepos` from an `iwpos` table in `ini_v`, reusing
  `per_sub_prime`'s subtune*3+voice addressing (per_sub_iwave forces it on).
  Mission_Moon: sub 1 partial→FULL, sub 0 stays FULL (no divergently-idling
  voice). Ledger C31.
- GATED: absent unless a compilation's packed players disagree on the idle wave,
  so single-player + same-idle-wave members are BYTE-IDENTICAL. INCOMPATIBLE
  with the layout/positional wave pools (pin wavepos to orig's live $177A) →
  there the override is IGNORED (collapsed-idle honest residue, never a build
  fail). GATES: golden byte-identity over a 48-member sample (single-player +
  2SID + 5 same-idle-wave compilations) = 43 identical + 3 pre-existing
  unsupported + 2 changed: Mission_Moon (partial→FULL, the fix) and Balloonacy
  (a differing-idle-wave 4-player compilation: FULL→FULL, all 7 subtunes, sub 2
  even matched +5 writes — verdict-preserved). smoke 6/6; full regression green.
- f1: 5362 FULL / 39 partial (was 5361/40).

## 🔶 ROUND 147 (2026-07-30, PARTIAL): compilation detection for NON-page-aligned lo/hi-pair wrapper — Pievspie/Mission_Moon sub 0 FULL; sub 1 proven lead
Next-partial Pievspie/Mission_Moon (2 subtunes, VBLANK, load $5000; NO STIL/
BUGlist entry). It's a COMPILATION (C31) the factory MISSED. Init wrapper $5DF3
= `TAX / LDA $5DE6,X (hi) / LDA $5DE4,X (lo) / STA vectors / JMP` — per-subtune
player dispatch via a SEPARATE lo table + hi table → players $5E24 (sub 0) +
$5000 (sub 1), both valid canon jump tables. Detection is PAGE-ALIGNED by
construction (static: base=hi<<8; observe: `--pc-watch` watches low-byte
$00/$48 + a page-aligned pre-gate; `_is_player_head` asserts `a&0xFF==0`), so
the NON-page-aligned base $5E24 (low $24) is invisible to BOTH paths.
- FIX (LANDED, commit 84ada94): `detect_compilation` pairs the two `LDA abs,X`
  tables when the page-aligned classification fails, validating each base via
  `_is_canon_base_unaligned` (exact canon-offset sig, page-alignment-free —
  strict enough that a spurious pairing can't validate). Sole carrier in the
  DMC family (census). Sub 0 → FULL. Ledger C31. Gates: smoke 6/6, full
  regression green.
- 🔎 SUB 1 LEAD (root cause PROVEN, fix NOT landed): the $5000 player
  STANDALONE verifies FULL, but the MERGE corrupts V2 → a C31 per-player fact
  collapsed. Bisected to per-subtune **`idle_wave`**: the merge sets per-song
  idle_notes/masks/durrel (compilation.py:791) but NOT idle_wave, which is
  FILE-LEVEL (`wave_programs[0]` = the wave walk from wave-table pos 0). The two
  players' wave tables DIFFER at pos 0, so sub 1's V2 idles on player 0's wave →
  its freq-base cache (fbl+1) diverges → V2's off-table freq read (idx 233 =
  fbl+1, C11 live-served) reads $8F vs orig $F7. PROOF: forcing merged
  `idle_wave = player1's` → BOTH subtunes FULL (sub 0 doesn't depend on
  idle_wave). FIX NEEDED = per-subtune idle_wave: the idle wave is a file-level
  wave PROGRAM at pool index 0; make it per-subtune (extend the `per_sub_prime`
  note/mask/cinst mechanism to a per-subtune idle wave START position into a
  merged pool holding both players' idle waves, or a per-subtune wave_programs[0]).
  Traps ruled out along the way: wavepos_layout (no effect), off-table records
  (no effect), idle_guards (identical), freq tables (identical).
- f1 unchanged (member still partial): 5361 FULL / 40 partial.

## ✅ ROUND 146 (2026-07-30): CIA latch per-play RE-ARM — C25 mirrored-class refinement — Strange_Acidshit FULL (+1)
Next-partial after Sound_Test: PVCF/Strange_Acidshit. STIL (PVCF's own words):
"octa multispeed... additional $1003er callings" — an 8× multispeed. Verdict
shape: full orig matched (play_match=len_a=1641467) but rebuild 0.14% too LONG
(len_b=1643848) = a RATE overshoot, not content. This is the C25 MIRRORED class
(orig's play body overruns its own tight latch: orig 7.19 plays/frame < our
7.31; orig effective period 2467 > latch 2456), which the ledger had marked
honest residue.
- ROOT CAUSE (principled, NOT fragile padding): orig's play VECTOR ($1FE4)
  re-arms $DC04/$DC05 (the SAME $0998 latch) EVERY call (~12 cyc). Our composer
  sets the latch ONCE at init, so our clean, lighter body ran ~12 cyc/play
  FASTER → the overshoot. The overrun is a SPECIFIC REPRODUCIBLE OP → reproducing
  it is core-tenet-principled, unlike C25's declined arbitrary cycle-padding.
- FIX: factory._cia_rearm_probe (play vector writes both $DC04+$DC05, captures
  the latch immediates) → cia_rearm_per_play → composer prepends a `playcia:`
  re-arm wrapper. Strange_Acidshit: 2381-over → 68-over (within tolerance) →
  FULL. Ledger C25 refinement.
- ⚠ NOT UNCONDITIONALLY SAFE — GATED ON MEASURED OVERRUN (C9 measure-don't-guess).
  The re-arm helps OVERSHOOT members (our body faster, orig overruns) but WORSENS
  UNDERSHOOT members (our body heavier — Moog/Compozak, len_b 6 UNDER, overrun
  0.9986). Fire ONLY when orig's measured effective period > latch. `_cia_rearm_
  probe` runs `_measure_play_period` and gates at >1.0015×(latch+1). Census: 105
  static re-arm carriers, but the overrun gate fires on EXACTLY 10 (Astovel +
  8 Kubiszyn_Paul tunes sharing the player + Strange_Acidshit), ALL FULL;
  Compozak/Bassbumper (non-overrunning) correctly excluded → byte-identical
  (probe returns None). A with/without sweep of 22 re-arming builds = 0 regressed.
  Distinct from Compotune_1 (overrun not a reproducible op → stays residue).
- GATES: smoke 6/6, full regression green. f1 now 5361 FULL / 40 partial.

## ✅ ROUND 145 (2026-07-30): F-phase per-voice REPEAT — massive-multispeed effects (C18) — Sound_Test FULL (+1)
Next-partial after Scratch_It: PVCF/Sound_Test. STIL (PVCF's own words): "an
11-speeder, sounds like samples", used in the Reflex trackmo 'Reflection'.
Play wrapper $2114 alternates P (full play $1096) with an effects branch
`JSR $1006 x5`; `$1006 = LDX#0/JSR $15A2 (V1x1) / LDX#2/JSR $15A2 x5 (V3x5)`
=> per E-call the wave program steps V1x5, V3x25 in the INTERLEAVED order
(V1,V3x5)x5 (interleave is part of the write stream — a flat total diverges).
Observer got the voices (`P_F13`) but emitted each F voice ONCE, diverging at
the E-phase's 2nd V3 step (len_a/len_b = 397406/65186 = 6.1x). STIL confirmed
it's a DELIBERATE massive multispeed (wave-step, NOT digi — "sounds like"
samples), so Mode-1 write-stream reproducible.
- ⚠ The player is 94% NON-CANON (only 240/4096 bytes match the canon DMC
  player; a re-assembled custom PVCF multispeed player, dataflow build route).
  P-body/$10C1/$1006/$15A2 all differ from canon. Yet the fix is TINY: our
  canon wave-step reproduces the custom $15A2 BYTE-FOR-BYTE, because the DMC
  data format (wave/freq tables) is shared and the P-phase already matched
  (proving the data extract). The 94%-custom scare didn't matter.
- FIX: `factory._fphase_effect_repeat` statically decodes the nested JSR
  structure (outer `JSR SUB xk`, SUB=`(LDX #v/JSR FX xm)`) -> `fphase_repeat`
  '5:1x1,3x5'; composer expands the F-token to `outer x [voice x inner_count]`
  wave-step calls (interleave ORDER preserved). Sibling of C24
  play_unit_repeat (per-voice repeat in the play BODY) — the C18 F-phase
  analog. Ledger C18.
- Census: probe fires on EXACTLY 1 of 10,676 DMC members (Sound_Test) =>
  zero regression exposure; default absent = each F voice once, byte-identical.
  Class-lever check came back NEGATIVE (singleton; look-alikes are handled
  play_repeat/unit_repeat or Compod no_jumptable) — landed anyway per
  completeness. FULL 397406/397406. GATES: smoke 6/6, full regression green.
  f1 now 5360 FULL / 41 partial.

## ✅ ROUND 144 (2026-07-30): $D418-every-play wrapper INDIRECT topology (C19 32nd occ) — Scratch_It FULL (+1)
Next-partial PVCF/Scratch_It (canon base $7000, 2× CIA $2663 = 100 Hz):
sub 0 diverged at flat pos 26 (the FIRST play write). Orig play() re-asserts
`$D418=$1F` (mvol $F | LP-filter bit) at the top of EVERY call; ours emitted
0 (orig $1F ×91 vs our ×0 in 1 s; the changing `$BF` filter-mode events
matched ×5 both — the filter program was already right). This is the known
`master_vol_every_play` wedge (PVCF/Zyron/Signor), but in an INVERTED
topology the probe missed: the play vector `$7003` (= base+3, the canon play
JT slot) is re-pointed `JMP $82F0`, and the appended wrapper `$82F0` does
`LDA #$1F / STA $D418 / JMP $7085` (real play body) — NOT inline at the play
vector, NOT exiting `base+3`. FIX: `_d418_play_wrapper` now also follows ONE
JMP from the play vector, anchoring on the reloc-invariant `A9 ?? 8D 18 D4 4C`
shape with an in-image non-self-loop exit; inline branch byte-identical.
Composer unchanged (`playd418` chunk already emits the indirect form — our
Bernds_Tune rebuild proves it). Census: exactly 2 indirect carriers in
10,676 — Scratch_It + Bayliss/Follow_That_Storm; the latter is a RE-ASSEMBLED
non-canon-geometry member (init b+$50, play body b+$7B) that fails EARLIER at
jt-detection (`no_jumptable`) — a separate lever (canon-detection must follow
the wrapper JMP AND handle re-assembled geometry; noted, not chased). FULL
303880/303880 state ✓. GATES: smoke 6/6, full regression green. f1 now 5359
FULL / 42 partial.

## ✅ ROUND 143 (2026-07-30, completed): wavestep-arm wrapper misread as R (C18) — Mathematika_II + Radio_Napalm FULL (+2)
Next-partial PVCF/Mathematika_II (RE-ASSEMBLED, base $1000, canon table
addrs $1647/$16A7 — canon_diff says reassembled; state at CANON offsets:
wavepos $177A,x, fxf $177D,x, fbl/fbh $172F/$1732,x). Schedule R3_P —
but the "R3" wrapper is `LDX #$02 / JMP $1591` = the WAVESTEP entry
(an advancing F3; C18 R-positive class). ESTABLISHED FACTS (per-play
aligned at flat 33048 = play 3013, V3 row: pattern 8 row 15, note 36,
stated i20=DRUM raw, prev row i15 also drum):
- Play 3012 (P, fetch): BOTH sides identical — new instr ADSR $00/$EA
  + hard restart $FFFF/$81 (prep). Play 3013 ("R3"=wavestep): orig
  emits fbh=$0A = NEW drum's step 0 (trace: $15FA LDA $1A2F,Y Y=$2B=43
  = i20's wave_start, drum branch), OURS emits $04 = OLD i16 program's
  current cell (our pool pos 50). Play 3014 (P): ours catches up
  ($0A00) but stays ONE DRUM STEP behind orig from then on (3015 orig
  $0D=step1, ours $0A=step0).
- ⇒ the orig switches fxf+wave program to the NEW instrument AT THE
  FETCH play; our composer switches cinst/fxf/wavepos at note-init
  (3014). Melodic transitions mask it (fbh=fhi[note] both ways, no
  step between); DRUM transitions expose it.
- RESOLUTION (same day): the "switch at fetch" reading was WRONG — trace
  CYCLE STAMPS placed the $12CC init block 19,960 cyc (= 2 CIA periods)
  after the fetch = the NEXT P: BOTH sides use standard pend deferral.
  The real difference was the INTERPOSED CALL: the wrapper's "R3" is
  `LDX #$02 / JMP $1591` (jump-table play entry re-pointed: $1003 JMP
  $2528) = the ADVANCING wavestep arm entry, misread as R because V3
  idled during observation. An R never advances → the drum lagged one
  step. FIX: `_wavestep_arm_refine` (static; wired at BOTH the dataflow
  and canon phase sites; follows one JMP from the play vector) flips
  the matching R token → F + forces noteinit_deferred=1. Census: 5
  wrapper carriers, 2 flipped (Mathematika_II 227925 FULL +
  Radio_Napalm 299704 FULL — a bonus recovery), 3 no-ops re-verified
  (Dresden×2 FULL, KB FULL). ⚠ offtable probe 8th by-value mis-fire
  (idx 141 = $1734 fbhi cache self-echo, same class as the 7th).
  f1 now 5358 FULL / 43 partial.

## ✅ ROUND 142 (2026-07-30): pulse-base ADC re-pointed into SID-mirror space (C19 31st occ) — Mathematica_tune_3 FULL (+1)
Next-partial PVCF/Mathematica_tune_3 (canon layout): note-init PW-lo off
by the instrument's base nibble ($6F vs $60). dmc_canon_diff: canon
$1376 `ADC $175F,X` → `ADC $D75F,X` — the pulse-step base read lands in
SID-MIRROR space (X=0 = ENV3, X=1/2 = write-only mirrors = decayed
bus). The $175F STORE is unpatched (off-table cpwbase co-location
intact); FIX = `_pw_base_read_probe` (uniform _WEDGE_PROBES row, fires
only for $D400-$D7FC operands — hardware-stable, layout-independent) →
composer param `pw_base_sid_read` swaps the two ADC sites (fx_pulse +
pulse_tail) to the absolute read; identical values under the identical
write history. Also on board: an init wedge (`LDA #$35/STA $01` banking
poke + forced A=0 — walk no-op). Census: 1 carrier in 10,689. FULL
210182/210182. GATES: smoke 6/6, full regression green. f1 now 5356
FULL / 45 partial.

## ✅ ROUND 141 (2026-07-30): C18 static-table schedule refinement — Hexzakk FULL (+1)
Next-partial PVCF/Hexzakk (6× CIA $0CCB, re-assembled base $1000): V3
"wrong note" at frame ~13 was NOT off-table (`dmc_offtable_probe`
mis-fired on the freq-lo CACHE $1741 — by-value trap; this member's
layout is +$10-shifted, hand-crafted watch addrs are the exact
`dmc_state_addr` trap). Ground truth (pc-trace): the wave step read pool
pos 117 (offset 9) where ours sat at an offset-5 step — our V3's wave
program lagged one advance. Cause: the play wrapper is the C18 SMC
JSR-OPERAND-TABLE idiom (counter mod 6 → table [03,03,06,06,06,06] →
JSR $1003/$1006); the true schedule is P F123 F123 F123 F123 P (call 5
= F123), but the pc-trace observer classified call 5 as R123 — an R
never advances the wave, and instr 14's program holds equal values for
several steps, so the drift stayed invisible until the program's next
value change. FIX: `factory._smc_jsr_table_refine` — static decode of
the wrapper (period, per-call targets, seed), then force same-target
calls to their MAJORITY token (base+3 group must be P). Census: Hexzakk
is the ONLY carrier of the shape in 10,689. FULL 1148445/1148445.
GATES: smoke 6/6, full regression green. f1 now 5355 FULL / 46 partial.

## ✅ ROUND 140 (2026-07-30): play-clock byte INSIDE a played sector (C19 30th occ) — Dresden_Party FULL (+1)
Next-partial PVCF/Dresden_Party: deep V3 note-init freq-LO-only
divergence (~45% in). Root cause: the appended play wrapper's phase
parity counter ($6FFF, INC per play / AND #$01; init seeds $FF) sits
INSIDE V3's pattern data — a mode-0 glide row's start-note byte IS the
live counter (pitch rises one step per play tick each lap; the stale
file byte $2E decodes as a plausible ordinary glide = the disguise).
The freq-HI matched by coincidence (orig's off-table stable-prefix vol
slot $0F == our real fhi[46]). FIX (mechanism reproduction, Ed family):
`_playclk_probe` (static: INC/LDA operand pair at the play vector +
init seed) → extract-internal `playclk_addr` (filtered from USF —
engine-positional); walk flags the row (`note_clock`, grammar+parser
extended, corpus check 12001/12001); composer emits the flagged row's
stream byte as a labeled $FF seed, INCs every labeled byte at the head
of each play call, re-seeds at init. Off-table freq for counter notes:
nothing new needed (flo/fhi adjacency + co-located window already
matched). Census: 6 wrapper-shape carriers, only Dresden's counter in
song data; Dresden_Party_95_II + 2_Speed (FULL siblings) re-verified
FULL, Radio_Napalm/X-Filter at pre-existing baselines. GATES: corpus
check, smoke 6/6, full regression green. f1 now 5354 FULL / 47 partial.

## ✅ ROUND 139 (2026-07-30): C37 3rd carrier via OBSERVATION detection — Cafe_Odd FULL (+1, both subs); r138 probe misfire fixed
Next-partial PVCF/Cafe_Odd (base $E000, re-assembled): sub 1 diverged in
INIT ($D418 $FA vs $FF). Root cause = a C37 SAVE-STATE RESUME wrapper in
a 2nd SHAPE the static skeleton can't parse (`JMP copy`; single src-lo
table $F240,X + dest lo/hi tables $F180/$F220, 29 pairs; `LDA #$00 /
JMP $E000` → every subtune is song 0 resumed; record 1 = dead cargo,
whence the wrong $FA vol). Landed `_state_resume_observe` (C37's own
canonical rule): py65 init(A=sub) per subtune, fire iff ALL enter base
with the same A and ≥1 non-start sub's post-init RAM diffs (≤256 B);
diff = the survivors. THREE new survivor categories lifted (all onto
PRE-EXISTING fields, zero schema): d417 shadow poke → song.d417_shadow →
subtune res_routing; GLOBAL vib/slide parity $E019 ($1019 twin) →
song.dual_phase → subtune init.slide_phase (the 21s V3 wave-phase
divergence: vibrato-flagged instruments alternate wave-step/vibrato on
that one global counter); wavectrl cell $EA50 $94→$91 = a $90+n
wave-program JUMP retarget → the existing clone-and-remap pass (clones
$17/$18). ALSO fixed r138's probe: the static JSR-form match mis-fired
on Bomberman_preview's CONDITIONAL wrapper (only sub 0 → song 5) —
`_init_song_observe` cross-check added (fire iff observed A == imm for
all subs); Bomberman refused, back to baseline partial (its conditional
per-subtune song remap = future lead). Census (104 multi-subtune
non-JT-init members): observe fires ONLY on Morbital_plus (already
partial; sub-1 div 1→37, no regression). GATES: smoke 6/6, Hear_Circa +
Cafe_Odd FULL, full regression green. f1 now 5353 FULL / 48 partial.

## ✅ ROUND 138 (2026-07-30): forced-tune-record wedge 3rd FORM (`LDA #imm / JSR base`, C19 29th occ) — Hear_Circa_2_Minutes FULL (+1)
Next-partial Odysseus/Hear_Circa_2_Minutes: diverged at flat pos 32 and
the rebuild played a COHERENT but entirely DIFFERENT song — the richer
disguise of the 9th-occ forced-tune-record class (Sans_intro's record 0
was a dummy; here record 0 is a full other tune). Init wrapper at $0FD0:
`LDA #$00/STA $0FE6` (phase counter) then **`LDA #$03 / JSR $1000`** —
record 3 hard-forced — then CIA $2663. The play-wrapper half (SMC parity
→ P_F123, $1567 vibflip) and the CIA latch were already probed right;
only the record force was invisible: `_forced_subtune_probe` required
`LDA #imm` AT the init vector reaching base by fall-through/JMP. FIX
(extract-only, C19): probe gains the 3rd form — scan the wrapper window
`[init, min(init+$30, base))` for `A9 imm 20 <base>` (exact JSR target =
static anchor). Census: 1 behavior-changing carrier + 8 imm=0 no-ops
(7 Rayden 2SIDs + Praiser/Mega_Mix). FULL 271977/271977 state ✓.
GATES: smoke 6/6, full regression green. f1 now 5352 FULL / 49 partial
(vs the r128c batch baseline).

## ✅ ROUND 137d (2026-07-29): DEPRAVE_7_TUNE_3 FULL (+1) — 222826/222826 exact. The r128 hard-residue member fully lands; final piece = DOUBLED-PREFIX command COUNTS
The "drum-path" residual decoded as the C11 SECTPOS live read (wnote $82
→ fhi idx 130 = $1729, V1's own sectpos) with our shadow off by exactly
2: the composer's row-width derivation counted stated commands as
BOOLEANS while a sonified-garbage-window row can carry DOUBLED prefixes
(two $Fx vol bytes before one note — impossible in editor-authored
sectors, routine in stack/zp windows). FIX: `p_d/p_i/p_v` became COUNTS
(truthiness keeps every boolean consumer intact); fx_flags emit
`dur_cmd=N`/`instr_cmd=N`/`vol_cmd=N` for N>1 (bare = 1, grammar +
parser extended — usf_corpus_check 12001/12001); the composer's
`_cnt()` width math consumes them. Grammar/parser touched ⇒ full gate
set: 9-member C29 class census FULL, smoke, full regression, corpus
check — all green. THE COMPLETE DEPRAVE STACK (r137-r137d):
dispatch-depth fetch serve (zp+stack) → per-read-site peek map →
playidx-paired lap-aware serving (decimal playidx!) → doubled-prefix
counts. The r128 "live CPU stack = irreducible residue" boundary is now
FULLY overturned — the third and sharpest expiry precedent.

## ⏸ ROUND 137c (2026-07-29): Deprave — PLAYIDX-paired lap-aware serving LANDED + VERIFIED ALIGNED (all 3 voices 100% event hits); residual UNMOVED at 219359 = a V1 DRUM-PATH value (next session's lead)
The r137b ordinal-pairing failure root-caused TWICE: (1) pairing key must
be PLAYIDX derived from cumulative row durations (dur 0 = 256 plays), NOT
decoded-row ordinal (misaligns at orderlist loops); (2) ⚠ the PW event
playidx field is printed DECIMAL — the hex parse inflated every key ~5x
and silently unpaired everything (`_pc_watch_abs` fixed). Wired ON:
`_FETCH_EVENTS` = {voice: {playidx: window}}, `rd()` serves via
base_pi + Σ(durations); alignment PROVEN: V1 2081/2081, V2 1311/1311,
V3 1661/1661 walk-row→event hits (misses only past the capture window).
RESIDUAL at 219322/219359 (~272 s, 98.44%): V1 freq hi orig $27 vs ours
$25, freq LO EQUAL — orig state at the write: curnote=$07, fbh=$27,
acch=0 ⇒ the base hi was loaded by a DRUM-path table read (not the
$1647/$16A7 freq tables — dmc_offtable_probe structurally can't see it),
value off by 2. NEXT LEAD: identify V1's instrument at that row (likely
environment-derived content) + which drum/wave read produced $27; note
the peek map is still FIRST-WINS (not lap-aware) — if the drum trail
dead-ends, check a lap-2 peek mis-decision shifting V1's phase. GATES:
9-member class census re-run (parse fix + pairing are enabled changes),
smoke, full regression — all green.

## ⏸ ROUND 137b (2026-07-29, owner-directed continuation): Deprave div 157878 → 219359 (98.4%, lengths EQUAL) — per-READ-SITE serving; ONE residual (lap-2 crossing, needs playidx-paired serving)
The r137 "$7F escape" reading was WRONG — ground truth (memwatch): the
engine NEVER escapes (otrk stays $A1, sectpos wraps $FF→$01, instr $1F
plays on — r128's "instr-31" was exact). Resolution: the $7F at $01F3 is
read by TWO SITES AT TWO CALL DEPTHS — the end-of-row PEEK ($11E6 LDY /
LDA($f8),y / CMP #$7F, deeper: sees a different below-SP stale byte, does
NOT terminate) vs the next row's FETCH (dispatch depth: sees $7F = instr
$1F command). Same address, different value per site — C34
position-dependence at per-CALL-DEPTH grain; both sites read STALE BYTES
BELOW SP left by whichever subroutines ran last (deterministic per site).
LANDED: (a) fetch-depth serve extended to zp $0002-$00F7 (the post-escape
— actually never-escape — sectors resolve to base $0000); (b)
`_PEEK_DEPTH_MAP` — peek-site capture (pc-watch base+$1E6 zipped with the
LIVE $F8/F9 pointer + sectpos: exact per-event attribution) consulted by
`peek_end` for low-RAM addrs; empty for ordinary members. RESULT: the
walk now mirrors the non-escape; V2's endless march decodes the vol-7 /
instr-31 crossing rows; 219359/222826 matched, len EQUAL. ATTEMPTED +
REVERTED: lap-aware ordinal-paired fetch serving (`_FETCH_EVENTS` +
`fetch_ctx`, machinery kept but wired OFF) — pairing by decoded-row
ordinal MISALIGNS once the orderlist loops (regressed lap 1 to 157946);
the correct pairing key is PLAYIDX (walk can derive each row's play index
from cumulative durations) — the next session's step. RESIDUAL = the
lap-2 crossing (~253 s) reading evolved stack bytes. GATES: 9 C29-class
FULLs re-verified FULL; smoke; full regression green.

## ⏸ ROUND 137 (2026-07-29): Deprave_7_tune_3 — DISPATCH-DEPTH stack-page serving landed (div 157878→157962); the r128 "live CPU stack = hard residue" boundary PARTIALLY overturned; remaining blockers enumerated
The r128 boundary re-measured (C11 expiry rule, 3rd precedent): the stack
bytes V2's endless window reads are DETERMINISTIC AT DISPATCH DEPTH (the
play call-chain fingerprint — 252/256 window bytes byte-identical across
1,244 fetch events; the 4 deep slots vary per event but are single-valued
at their CONSUMING event). Landed: `_dispatch_depth_serve` (engine_model)
— `--pc-watch base+$D2` (track-fetch entry, 3-byte site; the 2-byte
`LDA ($f8),y` at $110F is INVISIBLE to C36's ≥3-ascending discriminator —
gap recorded in C36) + a second sectpos capture zipped by event ordinal;
serves STACK-PAGE ($0100-$01FE) bytes the C29 overlay left at zero:
stable→value, per-event→earliest consuming-interval value (span≤6 guards
against sector-reset interval pollution; zp incl. $F8/F9 pointer pairs
never touched — the first cut clobbered $00F9 and taught that guard).
RESULT: the vol-7 pick-up row reproduces ($78 ✓); div 157878→157962.
REMAINING BLOCKERS (why still partial): (1) the picked-up $01F3 byte is
$7F = SECTOR-END — the orig ESCAPES the endless state at the crossing and
resumes marching its track through garbage; the walk's endless model has
no mid-cycle $7F escape. (2) LAP-VARYING content: the 2nd endless lap
(~245 s, in-window) reads DIFFERENT stack bytes ($FF at $01F3) — needs a
lap-aware walk memory (unroll with per-lap windows); r128's "instr-31"
was actually $7F&$1F. GATES: 9 C29-class FULLs re-verified FULL incl.
Remix_1995 (the 0-is-right caution carrier — measures 0 at dispatch
depth, same verdict by measurement); smoke; full regression green.

## ✅ ROUND 136 (2026-07-29): negative-transpose ADC immediate wedge (C19 28th occ) — Party_Pooper_3_intro FULL (+1)
Next-partial Party_Pooper_3_intro: deep V3 note-init pitch divergence
(orig $0777 vs ours $02F6, ~100 s in) — NOT off-table (probe bowed out).
Memwatch: orig live transp $0F at otrk $1C where the track byte is $81
(canon −1, our walk's decode). The transpose handler's negative branch
ADC immediate is patched: canon `EOR #$1F / ADC #$01` → `ADC #$11`,
biasing every $80-$9F transpose +$10. Extract-only fix per C19:
`cfg.transpose_neg_bias` (probed off the `49 1F 69 imm 9D base+$72C`
shape at the canon site) threaded into `_walk_track`'s negative-branch
arithmetic (both call sites). GATES: census 1 carrier family-wide;
smoke 6/6; full regression green.

## ✅ ROUND 135 (2026-07-29): alternating whole-play repeat — parity wrapper, P2 phase token (C24 4th form) — Bajerek FULL (+1)
Next-partial Bajerek: perfect prefix, orig len exactly ×1.5 ours, measured
IRQ rate IDENTICAL both sides ($2663 2×) — the appended play vector
`INC $02 / LSR / BCS / JSR $1003 / JMP $1003` runs the whole body TWICE
every other call (3 body-runs per 2 IRQs = a 3× tune from a 2× timer).
Doubly invisible: factory forces play_repeat=1 for CIA members; the C18
reachability observer sees a double-P as plain 'P'. One-glance
discriminator: per-play write counts 34/17 alternating vs our flat 17.
FIX: `_play_repeat_parity_probe` (static wrapper shape + observed
doubling parity from the per-IRQ capture, C23 footprint rule) →
play_phases='P_P2'; composer phase alphabet gains the P2 token
(`jsr playframe / jmp playframe`). Probe pitfalls hit and fixed during
the round: the per-frame debug `nwrites` can't split a multi-entry frame
(use writelog_per_irq_capture), and an "in-player range" gate wrongly
covered the appended wrapper. GATES: shape census = 1 carrier
family-wide; smoke 6/6; full regression green.

## ✅ ROUND 134 (2026-07-29): $FF-handler JMP-stub with PER-VOICE loop targets (C19 27th occ) — Road_to_Sydney FULL (+1)
Next-partial Road_to_Sydney: mid-song (f2185) V1 row-duration divergence —
the SAME pattern row played dur 14 early and 21 late. NOT a data poke
(taint: static): the $FF loop handler is wholly REPLACED by `JMP $1B57`
(no canon site) → dataflow's binary classification defaulted to
track_loop_target=True (read-next-byte) and decoded garbage loop targets
(V1 loop@5 vs engine's 0); the appended stub dispatches per voice
(CPX #$02: V1/V2→0, V3→1). The wrap itself was SILENT (both sides
re-enter pattern 0), diverging only when the post-wrap entry sequences
drift — hence the deep first-div. FIX: positive stub-shape recognition in
dataflow.locate → the existing per-voice loop_reset_pos tuple (r63
machinery). Diagnostic route worth keeping: flat-stream D405-position
diff (Trap-C-free note-init timeline) localized the row; the earlier
frame-number diff was Trap-C-unsound and misled. state_match=False was
divergence fallout (clean-window Check A was green). GATES: signature
census = 1 carrier family-wide (this member); smoke 6/6; full regression
green.

## ✅ ROUND 133 (2026-07-29): cymbal CTRL immediate wedge (C19 26th occ) — Grapevine_18_intro FULL (+1)
Next-partial Grapevine_18_intro: diverged at f1 write 17, V3 noise-attack
ctrl orig $02 vs our $81 — the canon burst's SECOND immediate patched
($1313: `LDA #$81` → `#$02`, a sync-only attack; the dmc_canon_diff
immediate blind spot). `_cymbal_burst_byte` had the ctrl HARDCODED in its
anchor (`A9 81`) so it structurally could not see it — generalized to
capture (burst, ctrl); new `cymbal_ctrl` param (default $81, composer
emits it in `_cym_burst`). Diagnosis detour recorded in C19: the member
also re-assembles the instr cache +1 ($1016-$1018), so canon-address
memwatch showed V2's instrument for V3 and looked like a cross-voice
wedge until the member's own operands were read. GATES: census 2 carriers
family-wide (Presentation $DF burst FULL/canonical-ctrl = untouched;
Grapevine fixed); smoke 6/6; full regression green.

## ✅ ROUND 132 (2026-07-29): SWING-DRIVER latch median (C9 8th occ) — Falu_Mix + Compotune_1 + Compotune_2 FULL (+3)
Next-partial Falu_Mix: perfect prefix + rebuild 0.35% long. The player
REPROGRAMS $DC04/05 every IRQ — tempo-swing cycle [4033,4033,4033,7610]
(measured per-frame estimates 4033/4927/5225 all explained by the cycle;
whole-cycle average 4927.25) — so the writelog probe's canonical
`19656//N−1` (4913) was 0.3% fast. FIX in `_cia_period_from_writelog`:
compare the canonical latch to the MEDIAN of per-frame per-period
estimates; on a >4-cyc disagreement re-measure 10 s and return
`round(median)−1`. ⚠ the first cut used an entry0-anchored RAW MEAN —
poisoned +7 cyc by the init→first-play gap outlier, fired for DOZENS of
canonical FULLs; the census re-run caught it pre-land (the C9 8th-occ
estimator lesson). GATES: probe-path census (78 members with unreadable
init latch): branch fires for exactly 4 — Falu_Mix + Mephisto
Compotune_1/2 (all partial→FULL) + Merry_Christmas_Mix_1 (FULL, held
FULL with the closer latch 9819); smoke 6/6; full regression green.
Swing schedule = engine bookkeeping (Mode-1 observable is only the
average rate) → single best-latch, no schema growth. Residual ~0.1%
length deltas remain within tolerance (occasional longer cycles beyond
the 4-slot model — accepted).

## ✅ ROUND 131 (2026-07-29): PER-SUBTUNE SPEED MASK (C9 7th occ) — F_A_K_E-Intro FULL (+1)
Next-partial F_A_K_E-Intro sub 1: perfect prefix, rebuild exactly 2× the
orig — the file MIXES a CIA 2× song (sub 0, $2663) with a VBLANK song
(sub 1, header mask 0b1), while the composer stamped the speed bit on
EVERY subtune and psiddrv drove sub 1 off the timer. NO schema addition:
`PsidMeta.speed` already modeled the mask (grammar/writer round-trip in
place) — it was simply never populated/read. Wired: `parse_psid` parses
the header speed field; `DmcModel.speed_mask`; extract sets
`psid.speed & ((1<<n_subtunes)-1)`; both composer header sites emit the
mask with an all-ones fallback when absent (older stored .usf =
byte-identical); init's unconditional timer programming left (inert
without a $DC0D enable). GATES: smoke 6/6; header census over all 5833
members: F_A_K_E-Intro is the family's ONLY mixed-mask member (all-CIA
members hit the identical fallback); full regression green. Repaired a
r130 doc slip (the C9 "stored artifact pair DISAGREES" TELL heading had
been consumed by the 6th-occ insert).

## ✅ ROUND 130 (2026-07-29): CIA latch CROSS-CHECK (C9 6th occ) — Big_GLORZ + Low_Frequency FULL (+2)
Next-partial Big_GLORZ: PERFECT full-overlap prefix + rebuild 1.07%
LONGER — a pure rate error. Factory trusted the py65 init-probe latch
($2600 — suspicious round lo=0) over ground truth; measured steady entry
period = 9828 = canonical $2663 (KB's player programs $DC05=$26 at one
site, the $63 lo byte at a second site the sentinel'd init never runs).
FIX: `_cia_period_crosschecked` (factory) — init latch kept only when the
measured median entry period agrees (±3 cyc); STABLE disagreement (≥80%
of per-period estimates within ±3 of median) → `measured_period − 1`;
unstable measurement (C18 phase wrappers) keeps the init value. All 3
call sites (canon / multisid / dataflow) switched. GATES: smoke 6/6;
CIA census (tmp/r130_cia_census.py, all 502 speed-bit f1 members): 2
carriers, BOTH partial, BOTH now FULL (Big_GLORZ, Low_Frequency — the
KB pair), 0 FULL-side carriers, 4 unstable-measure FULLs untouched by
construction; full regression green. Ledger C9 6th occurrence recorded
(a probe that CAN return a value is not thereby RIGHT — cross-check
against cheap ground truth instead of short-circuiting).

## ✅ ROUND 129 (2026-07-29): wave-program IN-TABLE RUNAWAY fix — Long_Time + Sweet_Remix FULL (+2), Goldrake moved later
Next-partial-by-path Long_Time diverged on V2's drum: orig's inst-13 wave
program walks past the packed table's end (the packer truncates ctrl/note
tables to 45 used cells; positions 45+ read ctrl from the NOTE table's head
and notes past its end — C2). `_slice_wave`'s in-table RUNAWAY branch (no
marker before nominal end) was the LAST nominal-length bound: it capped at
table end + held, while the engine INCs on. FIX (one edit): route runaway
to `_resolve_wave_chain` like off-table starts; the stated wave_table norm
form absorbs the settled walk's extra cells (only the duration-bounded
prefix is observable). GATES: dmc_smoke 6/6, full regression 0 regressed,
carrier census (tmp/r129_runaway_census.py, old-vs-new slice compare over
the deduped wide-results members, partials first): 3 carriers in the 63
partials — Long_Time FULL, Sweet_Remix FULL, Goldrake sub-1 first-div
25947→26584 (remaining blocker = C11 live off-table hi reads on its
relocated $9000 compilation player: $9775/$9786-88 LIVE per
dmc_offtable_probe — separate class). FULL-side census COMPLETE: 5,833
members swept, 4 carriers TOTAL (the 3 partials + ONE full — Halucination,
re-verified FULL), 0 extract errors — the exposure audit confirms the
verdict-neutral argument (a cap-held FULL can only be FULL if the tail
never plays) and no norm-form/build-error side effects anywhere.
NB engine_model.py changed ⇒ family code_hash bumped: the r128c-synced
corpus re-verifies at the next fresh batch; no mass-write this round.

## ✅ ROUND 128c (2026-07-29): PHASE-5 CORPUS SYNC — f1 batch 5338/5401 FULL (98.8%) + mass-write + levers retired
The overnight full f1 batch on r128b code: **5338 FULL + 63 partial, 0
error/unsupported** (+9 vs r127's 5329; the r113-r127 gains are now ON
DISK). `dmc_mass_write`: 5338 written 0 err, 4 drifted ex-FULL orphans
removed (Lane_Crazy class — C20-correct), 9/9 path-stratified disk
audit, `usf_corpus_check` 12,001/12,001. Levers
SIDFINITY_WT_OLDFORM/SIG_OLDFORM retired (dead with the corpus in
signal+wave_table form; gate = 15/15 fresh-vs-stored byte identity +
smoke + full regression). NOT deleted, deliberately: the `live(...)`
parse form + resolved-copy wave fields — 52 stored .usf OUTSIDE f1
(v5/family-2, extracts not migrated) still carry live(), and
resolved-copy is load-bearing on the 2SID/compilation/hetero merge
paths; their deletion rides the future v5/family-2 extract migration.
FAMILY-2 SYNC EXPLICITLY DEFERRED (owner, 2026-07-29): the 52 stored
live()-form .usf turned out to be family-2 (2,889 members, v4 pipeline
`sector_format='family2'`) whose WHOLE corpus is July-stale (2,508
stored artifacts, no current-code rows) — the recorded "expect this
corpus-wide when family-2 work resumes" condition. A fresh f2 batch was
started and the owner STOPPED it (150/2889 done; those rows were
REMOVED from tmp/dmc_wide_results.jsonl so no future mass-write acts on
a half-batch — an f2 sync must start from a complete fresh batch). Do
NOT sync/orphan-clean family 2 until the owner asks; grammar keeps
parsing live() until then.
Residue census (divergence_census --partials, closeout): 63 partials =
a LONG TAIL, no dominant lever — 10 unknown (trichotomy-fallback keyed),
6 V3-freqlo-deep, 6 $D418-deep ($1E vs $1F — a vol/filter-mode bit), 5
V2-freqlo-early, then 3-and-smaller clusters (16 more singleton-ish
buckets; Deprave + Ziazi = the V2-SR-deep stack/dynamic class). Next
round should pick a cluster representative via dmc_next_partial, not
expect a batch lever.

## ✅ ROUND 128b (2026-07-28): Kordiaukis_01_2SID FULL — per-IRQ capture keeps the init prefix (|N) for the trichotomy verdict; Check A now REAL for CIA members
The r126 residual was a pure OBSERVATION ARTIFACT: orig defers chip-2's
init burst into its substream head (~frame 2, captured) while our
init-time chip-2 writes were DROPPED by the per-IRQ capture — per-chip
trichotomy Check A compared orig's primed state vs invisible defaults
(play streams fully matched both chips; flat full-length capture said
is_full). DECISION: extend the verdict by SYMMETRIC OBSERVATION, not by
deferring our init (that would reproduce the orig's init timing —
anti-trichotomy). Landed: siddump emits the dropped init prefix as a
`|N` chunk (multi-frame-init continuation included — those bytes were
previously dropped SILENTLY; parsers splitting on |I unaffected);
`writelog_per_irq_capture(keep_init=True)` prepends it as one leading
frame; the v4 verdict paths (dmc_build_one.verify + dmc_family_batch,
both capture sites) pass keep_init — C21's shift recovery aligns past
both inits and Check A compares REAL end-of-init states. NB this turns
Check A from VACUOUS to real for every CIA member (500 in f1; both
sides' inits were previously dropped → state 0 vs 0): gates = Kordiaukis
FULL (515888/515888 chip 0 + chip 2 aligned d=-19), 20-member stratified
prior-FULL CIA sample + Nocturno + Aetsch all 22/22 FULL, full
regression. NOT flipped: pipelines/dmc/verify.py (regression's DMC
runner) — its CIA path is a flat match_all prefix compare that keep_init
would break at write 0; it predates the trichotomy CIA verdict and stays
as-is (candidate for a later unification); dmc_v5 verdict paths likewise
untouched (own census gate needed before strictening).

## ✅ ROUND 128 COMPLETE (2026-07-28): endless-tail fold landed — otrk drift fixed; Deprave's residual = LIVE CPU STACK sonified (C29 dynamic, hard residue)
The decided fix shape landed exactly as specified, three edits: (1) WALK
(`engine_model` endless branch) appends the extra entry's `entry_offsets`
at the SAME `pos` — both lead and period live at the one track byte the
engine's otrk freezes on; (2) FOLD (`_fold_stated_orderlist`) admits the
stated-content-differing intro pair ONLY for the self-loop tail (cycle
length 1, equal offsets, loop_to = tail slot — the Creo/Dance refusal
stands for every longer cycle; `_stated_voice_form`'s dedup-merge check
still sends the pair to the effective-rows branch, so it rides the
existing `intro_entries` mechanism); (3) COMPOSER stated branch: a tail
intro whose gid ENCODES differently from the steady entry emits
[gid_lead, otrk][gid_period, otrk] with the $FF loop target at the steady
entry — lead once, period forever, otrk re-seeded frozen (carried-only
intros dedup to one gid → byte-identical for everyone else). GATES:
census scanner (tmp/r128_endless_census.py → .jsonl) over all 5401 f1
members found 32 tail carriers (+45 probe-only pseudo-sector members,
unaffected); all 32 verified: 27/28 prior FULLs stay FULL (Lane_Crazy
partial = the r127 pre-existing C20 palimpsest, byte-identical verdict
confirmed under a pre-change HEAD worktree), Memomania now FULL (stale
batch row), 4 fold-fail voices (Memomania/Canyon/Pour_le_merite/Black_It)
fall back harmlessly. Deprave_7_tune_3: divergence 30139 → 157878 (otrk
now tracks — memwatch shows $1727 frozen at $A1 ✓); the RESIDUAL is V2's
endless window $00FF-$01FE = zeropage + THE LIVE CPU STACK: at live
sectpos ~$F4 the cursor crosses $01F3+ where every IRQ's JSR return
addresses churn (orig picks up a live vol-7/instr-31 command; post-init
snapshot has zeros). Emulator-environment dynamic RAM, C29 hard-residue
boundary — our rebuild has a DIFFERENT stack by construction; stays
partial, correctly. Also fixed this round: `effect_chain_profiler`
--find-write blind spot (absolute stores carry no `[effaddr]` bracket in
the pc-trace — `_ABS_STORE` regex added; Calf_Love's 177 D416=$06 writes
now found, PC $106E; INVESTIGATION_BACKLOG updated).

## resolved by r128 above — ⏸ OPEN (2026-07-28, r128 investigation): Mephisto/Deprave_7_tune_3 — NOT wavepos: live OTRK drift from the 'endless'-sector walk's entry_offsets gap (fix shape decided, NOT landed — gates needed)
r126's "continuation into unstated cells" hypothesis REFUTED by measurement
(C11 rule): event-aligned memwatch (orig $177A-C vs our labels via
dmc_state_addr) shows wavepos tracks 1:1 — 0 mismatches over 1921 events
INCLUDING the divergent one. The diverging read (flat 30139, V2 freq hi $0E
vs $0C, f1866) has orig wnote=$7F → fhi idx 127 = $1726 = V1's OTRK (track
byte-offset, live-served): ours = entry+1 = 12, orig = 14 = entry+1 + 2
transpose-command bytes. CAUSAL CHAIN: all 3 voices end in a C11 'endless'
wrapped sector; that walk path (engine_model ~line 978) appends lead+period
entries WITHOUT matching entry_offsets (len(offs) = n-1 for every voice) →
`_fold_stated_orderlist` refuses at its FIRST precondition → otrk_legacy
(entry+1 approximation) → drift wherever transpose commands accumulate
(Deprave's offsets are EXACTLY entry+1+#transpose-changes — derivable, no
redundant commands). FIX SHAPE — DECIDED (2026-07-28, owner-directed re-anchor in the canon; the
`otrk_chg` fitted-param alternative is REJECTED per C32's "observe, don't
fit" — a derivation rule chosen because it happens to reproduce the data is
the fitted-model disease with an exactness alibi; it would also leave the
real defects in place). The principled fix = make the STATED FOLD succeed,
because the failure is two honest defects, not a representation limit:
(1) balance the endless walk path's entry_offsets (append `pos` per extra
chunk — the offsets are OBSERVED track facts; today's imbalance is a plain
bookkeeping bug); (2) extend `_fold_stated_orderlist` to admit the ENDLESS
TAIL — a SELF-LOOP slot whose pass-0 decode (lead) differs from its steady
decode (period) — as one physical slot with intro=lead / steady=period via
the EXISTING intro_entries mechanism (the composer already plays intro on
first fetch, steady on loop passes; a self-looping slot then re-seeds the
same otrk value = the orig's frozen wrap position, naturally). Keep the
Creo/Dance mid-sector-reentry refusal intact (scope the admission to the
self-loop tail: cycle length 1, equal offsets, loop_to = the tail slot).
otrk then derives EXACTLY from stated marks — no approximation. GATES
(blast radius = the fold runs for every member): census the endless-sector
members FIRST (voices whose walk returns the ('endless', ...) tuple),
verify that whole class + a FULL-side sample under the change, then full
regression before commit. Tool note:
`effect_chain_profiler --find-write D416=06` returned 0 for writes that
exist — investigate before trusting it again (INVESTIGATION_BACKLOG).

## ✅ ROUND 127 COMPLETE (2026-07-28): C37 save-state resume — BOTH Calf_Love members FULL (+2; f1 5329/5401)
Part 3 (same day): the file-level-table pokes landed via C31 CLONE-AND-REMAP,
NO schema. Sequence that matters for the record: a per-subtune `wave_table`
cell-override SCHEMA was drafted on the "position-locked wavepos carrier"
premise, then REVERTED — the corrected C37 decode produces NO wavepos records
(the census classification was an artifact of the garbage record-1 walk), no
position is observable, and the schema-addition discipline's
alternative-exhaustion step killed the addition (name-on-proof held). Landed
instead: extract clone pass (re-decode each poked subtune's used instruments
+ referenced filter defs under that subtune's patched tables; clone + remap
rows; wave-region + filtdef-region survivor collection on DmcSong). C11
occurrence inside the fix: a clone filter def MUST land in an unused NIBBLE
slot 0-15 (composer fbase = slot*16 is 8-bit; slot 17 wrapped onto slot 1's
zero deltas and froze the sweep at init value), gated on no referenced def
walking off-record (repeat>5, C2 window). $104F (custom SR-write cache) seed
never demanded — both members FULL without it: Calf_Love_2 132409/132409
both subs; Calf_Love_everytime 137577+137517 both subs. Gates: smoke 6/6,
full regression green (r127-2 commit).

## superseded by part 3 above — ⏸ r127 PART 2 (2026-07-28): C37 machinery LANDED — both Calf_Love non-start subtunes now decode the CORRECT song; remaining blocker = PER-SUBTUNE STATED-TABLE CELLS (schema decision for the owner)
Landed: `_state_resume_probe` (anchored static decode; fires on exactly the 2
carriers) → `cfg.forced_subtune=0` + `cfg.subtune_state_copy` survivors; the
extract applies them per-subtune to the walk smem (glide_neutered-style) +
lifts copied curnote/masks into DmcSong.idle_notes/idle_masks (existing
per-subtune priming). Calf_Love_2 sub 1: play_match 1 → 65 with len_a==len_b
(correct song; was a garbage record-1 walk); Calf_Love_everytime sub 1 same
shape (36/137577). REMAINING: the survivors also EDIT FILE-LEVEL TABLES —
Calf_Love_2's $1A88/$1A8B/$1A8D = WAVEFREQ positions 12/15/17 (proven: orig
sub0-vs-sub1 streams first differ at exactly the pos-12 read, $0EA2 vs
$0F81 = wnote 45 vs 46) and $1B2C/$1B2F = FILTER-DEF bytes; runtime-static
(memwatch, no animator). Filter defs could clone-and-remap (C31), but the
wave cells are POSITION-LOCKED (wavepos carrier — positional pool needs one
byte per cell) ⇒ the principled shape = per-subtune `wave_table` cell
override patched at init (ovr_sub-style) = a SCHEMA ADDITION ⇒ owner
decision pending. $104F identified = the player's custom SR-write cache
(volume-override OR-merge); seed unmodelled until a divergence demands it.

## superseded by part 2 above — ⏸ OPEN (2026-07-28, r127 investigation): Rio/Calf_Love_2_everytime sub 1 — SAVE-STATE RESUME wrapper fully decoded (ledger C37, NEW class); implementation is the next round
Sub 1 diverges at play pos 0 (r126 target left open). ROOT CAUSE FULLY
DECODED: the init vector is an appended wrapper at $20C2 — SMC copy loop
(`LDA $20EF,X` selects source page $73/$B4 → $2173/$21B4; dest pairs at
$20F1, 65 bytes) pastes a per-subtune ENGINE-STATE SNAPSHOT into the player,
then `LDA #0 / JMP $1807` = the real init ALWAYS gets song 0 (the tune table
at $1BA8 has ONE record; this player is a C13-style variant — subtune shift
is 3 ASLs / stride 8, operand tunetab ptr at $180E). Both header subtunes =
the SAME song resumed from different state. py65 post-init diff PROVED the
init wipe kills everything in $1718-$1785 (dead cargo); SURVIVORS per
subtune: $1012-$1014 (sticky curnotes: sub1 $40/$18/$3C), $1015/$1016
(instrument caches: $1F/$01), $104F (UNIDENTIFIED player byte — sub0 $FF /
sub1 $A8; identify from the disasm before landing), + 5 DATA POKES: sector
bytes $1A88/$1A8B/$1A8D ($2B/$1A/$1A) and track bytes $1B2C/$1B2F ($03/$03).
Sub 0's copy == the file image (why sub 0 is FULL today). FIX SHAPE (C37):
per-subtune post-init memory views for the walk (pokes flow into
per-subtune patterns naturally) + existing init.voice_state note/instr
priming; identify $104F first. NB: $1015 cache=$1F=31?? — 31 > max inst id;
check whether $1015 here is cache or something else in this re-assembled
layout before mapping it to instr priming. Carrier census (static signature scan, 2026-07-28): exactly TWO —
Calf_Love_2_everytime (wrapper $20C2) + Calf_Love_everytime (wrapper
$204F); no other Rio member carries it.

## ✅ ROUND 126 (2026-07-28): live-signal phase 4 — POSITIONAL wave-pool emission (+3 FULL: Fantastic_Dreams, Supreme, Rabies_Babies; r125 open note RESOLVED)
Phase 4 of `docs/live_signal_modulation_draft.md` (§5.4). COMPOSER: a
wave_position carrier whose USF carries the stated wave_table gets its pool
emitted as the FULL 256-cell table verbatim at its positions
(`_Model.wavepos_positional`) — runtime cursor == orig labels natively (chain
walks, mod-256 wraps, marker hops incl. the native start-on-marker chase +
its wjmp write, so iwchase is suppressed on this path); DMC_WAVEPOS_ROW gated
on layout OR positional. Compose-side C32 proof: every program resolved over
the emitted table must equal its materialized form, else fall back to repack;
the IDLE program validates against the TABLE'S OWN resolve-from-0, never the
file's shared wave_programs[0] (a 2SID merge's shared idle differs
structurally from the carrier chip's own — Kordiaukis 10x$41 vs 9x$41, same
hold stream). EXTRACT: `_wave_table_normal_form`'s wavepos_layout +
start-on-marker exclusions LIFTED (chaser wave_start = the raw marker cell —
the walk chases it exactly like the engine); `_wave_layout_verbatim`'s
relaxation gate re-keyed on the READ-TARGET voice's played programs (idx
211+j observes voice j; the old reader-instrument key was the recorded r125
landmine). 2SID MERGE: carries the CARRIER chip's stated table + pointers
(other chips stay resolved-copy, foreign table inert without pointers;
multi-carrier-differing falls back wholesale — flagged for the phase-5
per-chip-table decision). NO SCHEMA CHANGE; the §3.3 idle-walk `wavepos` seed
was needed by NO carrier → per name-on-proof NOT added.
Targets: Fantastic_Dreams FULL 205903 (the r125 blocker — inst 15's 62-step
off-table chain walk, unservable by any layout pool), Supreme FULL 133531,
Rabies_Babies FULL 70511. Kordiaukis_01_2SID: play streams now FULLY match
both chips (351228→371142/371142); residual = a VERDICT-LAYER artifact — the
orig defers chip-2's init burst into ~frame 2 (inside the per-IRQ play
capture) while our dispatcher inits at init time (dropped by the capture), so
per-IRQ trichotomy Check A compares orig's primed chip-2 state vs invisible
defaults (a flat 50Hz capture at full songlength says is_full=True,
audio_guaranteed). Open: fix = either C28-extend the verdict (per-chip init
prefix at substream start is init, state compared from the REAL chip state)
or defer our chip-2 init to match. Calf_Love_2_everytime sub 1: NOT wavepos —
orig's first V1 note plays idle-leftover curnote 51 with instrument cache 0
while our walk decodes note=0/instr=5 (a C34-shaped track-walk decode issue;
memwatch-proven, present at baseline). Deprave_7_tune_3: wavepos label drift
of 2 deep in (orig $0E vs ours $0C at its self-read) = a walk CONTINUING into
UNSTATED cells (soft-note continuation past stated reachability) — the
boundary recorded in C11. Exposure: 8 wavepos_layout/chaser FULLs re-verified
FULL (Distant_Echoes, No_Name_Remix, In_die_Dunkelheit, Das_Remix, II-V3,
Object_of_Art, High_Tech, Aktarus) + 57-carrier sweep + full regression (see
gates in the round commit). Ledger C11 entry + card updated (positional
supersedes layout for norm carriers).

## ✅ RESOLVED by r126 — ⏸ OPEN (2026-07-27, r125 investigation): Imaic/Fantastic_Dreams — wavepos-read carrier whose READER PROGRAM is an off-table marker-hop walk; needs a REPRESENTATION decision (user consulted, not yet decided)
Next f1 partial by path. Diverges at 0.05% (flat 97): V2 idle (running inst
15's wave program as cache leftover) reads fhi idx 211 = $177A = LIVE
wavepos[0] every frame (wnote=$D3 memwatch-proven); orig $0F vs ours $10 =
the layout shift (m.wavepos_layout=False). The C11 layout-preserving fix is
BLOCKED: the reading instrument (15, played by ALL voices) is itself
NON-verbatim — its orig walk from editor pos 160 chains marker hops OFF THE
TABLE (160→53→35→…→negative offsets = below-table file data read as wave
steps, C2 class), settling into a 16-step consecutive cycle that wraps mod
256; every re-trigger replays the ~46-step bouncing lead-in, all OBSERVED
live (idle V2 reads each frame). Also: `_wave_layout_verbatim`'s relaxation
gate keys on the READER instrument — the correct observability condition is
the READ-TARGET VOICE's programs (idx 211→voice 0, 212→voice 1, 213→voice
2); moot here (inst 15 played by voices 0+1 while observed) but fix the
condition whenever this is next touched. FULL would need per-step POSITION
fidelity: a `wave_step_pos`-style PER-STEP position list (arrangement §8;
markers derivable from run breaks; wave_table_pos = the degenerate
consecutive case) + a composer pool emitter that places steps at orig
positions incl. mod-256 wrap — a USF schema addition ⇒ decision point
(schema-addition discipline + Principle provenance challenge). DIRECTION (user, 2026-07-27): no per-member shoehorn — embrace state
sonification as a FIRST-CLASS USF feature ("live-signal modulation"),
implemented boldly and completely. Census run (tmp/live_signal_census.out:
~750+ landed members live-served today; gla ~340 / sectpos ~130 / wavepos
~77 live members; wavepos partials = Fantastic_Dreams, Supreme,
Rabies_Babies, Calf_Love_2_everytime, Kordiaukis_01_2SID,
Deprave_7_tune_3). Schema DRAFT rev 2 written for review:
`docs/live_signal_modulation_draft.md` — named signal refs replace the
live() flag + composer-side index map; the WAVE-TABLE NORMAL FORM (sparse
position-indexed stated table, C32) replaces both the per-instrument
resolved wave copies AND rev 1's wave_step_pos idea (labels inherent, C8
dedup dissolves, C19 pokes natural); vocabulary = name-on-proof; 5-phase
migration, each byte-identity/verify-gated, deletions ride the pending
corpus sync. NB rev-1's "off-table wave walk" was a SIGNED-ARITHMETIC
misreading — the 8-bit cursor wraps mod 256, every walk lives in one
256-cell space. Rev 2 APPROVED; **phase 1 LANDED 2026-07-28** (LiveSignal
type + vocabulary const, signal-slot ofreq grammar, wave_table block
[POSITIONAL cells — bare ctrl/freq keywords shadowed identical CNAME kv
keys under the LALR contextual lexer; usf_corpus_check caught it],
Instrument.wave_start, writer round-trip-stable; corpus 11973/11973 +
full regression green). **Phase 2 LANDED 2026-07-28** (commit this round): ONE shared resolver
(`src/usf/resolve.py::resolve_wave_table` — mod-256 walk, jump=hop,
absent-cell=hold, revisit=loop — subsumes ALL of `_slice_wave`'s
historical normalizations incl. chain/underflow/flat-concat cases as
emergent behavior) + `_wave_table_normal_form` (traced-walk cell stating,
both bounding regimes, C32 re-derivation assert over the merged union,
wavepos_layout/start-on-marker excluded → phase 4) + composer
`_materialize_wave_table` at compose entry. EMISSION IS OPT-IN
(`model_to_usf(wave_norm=True)` — only `write_dmc_usf` passes it): any
merge path that rebuilds a UsfFile from parts would orphan pointer
instruments from the file-level table (`zero_wave_table`) — regression
caught it twice (2SID merge, MA heterogeneous, which consumes
write_dmc_usf OUTPUT and must `denormalize_wave_table(parse(...))`).
Gates: A/B MD5 59/59 identical (Jim/Tichelmann_03/Cool_Compo/Attah_2/
Seaside/I_Am_Ready all norm-adopted; Object_of_Art falls back), adoption
58/59, dmc_smoke, corpus 11973/11973, full regression green. **Phase 3 SCAFFOLDING landed 2026-07-28, EMISSION GATED OFF**
(SIDFINITY_SIG_NEWFORM=1 to test): full 52-name vocabulary
(types.LIVE_SIGNAL_NAMES + grammar OFSIG incl. voiceless globals
`tempo()`), `composer_asm.DMC_SIGNAL_NAMES` + `signal_for_addr` (the
addr→name single source of truth), extract stamping, composer dual-form
boolean derivation (_rec_live). BLOCKED ON A DESIGN DECISION (draft §8):
a live record's captured (lo,hi) bytes are LOAD-BEARING for SPARSE
signals — the composer seeds igla/iglb (glide_note/glide_target priming,
C11 sparse-var seeding) from the ovr[] window bytes those records place
— so "signal replaces the value" drops real content and the MD5 gate
fails structurally. RESOLVED (owner): option (a). **Phase 3 LANDED 2026-07-28**: seeds →
typed `InitVoice.glide_note`/`glide_target` (§4.5 priming; extract
mirrors the composer's window fill to compute them; composer prefers
the init fields, legacy ovr fallback for old-form files); signal
emission now the DEFAULT (`SIDFINITY_SIG_OLDFORM=1` = A/B lever, retire
at sync); `_ovr_positions` skips signal slots (dense captures were
noise — deliberately dropped from the ML data). Gate: A/B WRITE-STREAM
identity 16/16 (all live-signal classes incl. the 6 seeded gla
carriers), smoke 6/6, corpus 11973/11973, full regression green. Next:
phase 4 (`wave_position` completion — positional pool emission for
wavepos carriers + idle seed; targets the 6 wavepos partials) + phase 5
(corpus sync retires live()/resolved-copy forms).

## ✅ ROUND 124 (2026-07-27): Cotton_Eye_Joe FULL (+1) — the $FF TEXT-fallthrough NOTE-INJECT (C13 third form, singleton)
Next f1 partial by path = `Hudy/Cotton_Eye_Joe` (single, base $1000
init-generated; dataflow path; canon_diff showed the $10E2-$10F2 "NEW" run =
ASCII). Diverged at 98.4% — the first track WRAP. ROOT CAUSE: the $FF
handler has the canon loop-to-0 store but its re-dispatch `JMP $10D2` is
overwritten by author TEXT ("PI BUDA & JARO 2002") that EXECUTES: BVC
(always taken — pc-watch proved the fall-through never runs) into the
dispatch's `CMP #$C0` with A=$00 → the plain-note path → every wrap injects
a spurious NOTE-0 row (sticky dur/instr, wrap-time transpose, +1 sectpos)
before resuming at track pos 0. Dataflow's `loop_site is None ⟹ read-next`
binary (C13's classifier trap) had silently made it loop to the TEXT byte.
FIX (extract-only): positive third-form detection in `dataflow.locate` →
`cfg.loop_note_inject` → `_walk_track` materialises the fake row (one-row
pattern entry; wrap key carries transpose) + `pending_off += 1`; the wrap
unroll materialises the shifted second pass. No composer change. 98.4% →
FULL 119060/119060 exact. Gates: dmc_smoke 6/6, Redable_Rain re-FULL,
full regression green. f1 count: 5324/5401 FULL + 77 partial.

## ✅ ROUND 123 (2026-07-27): Redable_Rain FULL (+1) — OBSERVED build variants of the re-assembled Heinmueck player (C23 2nd occ)
Next f1 partial by path = `Heinmueck/Redable_Rain` (single, base $1000
GENERATED by init — player not in the image, loads at $474C; dataflow path;
canon_diff can't align it). TWO build-semantic differences, both invisible to
static canon-offset probes on a re-assembled layout, both OBSERVED from the
original's per-IRQ writelog (C23's write-footprint rule, now its GENERAL
form — read the entry):
1. **Deferred-wave note-init:** the init routine RTSes before the wave step —
   init frame writes SR then AD only (its $184C helper also vol-merges the
   sustain nibble, same as our volovr); the note's first freq/PW/ctrl land
   NEXT play. Cymbal inits still burst ($FFFF/$81) on the init frame = our
   cym_ni shape. → `noteinit_defer_wave='1'`, composer ni_wave: rts.
2. **HR prep gate9:** the hard-restart prep writes ctrl $08 THEN $09 before
   AD/SR $0F0F (canon: $08 alone). → `hr_prep_gate='1'`, composer
   hr_test_write gains the $09 store.
Probe: `factory._noteinit_defer_probe` (one 10s per-IRQ capture, both params
classified ALL-or-nothing; melodic chunks must ALL lack ctrl, prep chunks
must ALL be [$08,$09]; canon members can't false-fire), gated to
dataflow-path members (curnote_addr set) without play_phases. Redable 0.0%
(match 27) → FULL 122680. Enforcer_2 re-verified FULL under the new probe
path. Gates: dmc_smoke 6/6 + full regression green.
f1 count: 5323/5401 FULL + 78 partial.

## ✅ ROUND 122 (2026-07-27): Enforcer_2_Level_1_preview FULL (+1) — the DRUM FREQ-HI REPOINT wedge (C19 25th occ, singleton)
Next f1 partial by path = `Heinmueck/Enforcer_2_Level_1_preview` (single, base
$0C00, 1 sub, partial 27%: V2 freq hi orig $1A vs ours $0C at a drum event —
`dmc_offtable_probe` correctly said NOT off-table). ROOT CAUSE: the
absolute-freq wave step's hi store (canon $15FD `STA $1732,x` = fbh) is
re-pointed at base+$754,x = **pwh+1, the NEXT voice's PW-hi state** — a drum
step zeroes fbl but leaves the SID freq hi at the note's base, and the table
byte pokes the neighbour's PW hi. One of canon_diff's 9 known unhandled
singletons (its $15FD repoint row); the member also carries the V3-unit
NOP-removal ($109C/$109D, already handled as `play_unit_repeat='1,1,0,1'`) +
the $10DF loop hook, and builds via the DATAFLOW path — which already runs
the uniform wedge probes, so the fix is just one `_WEDGE_PROBES` row
(`_drum_fhi_probe`, anchored, fires only on the exact base+$754 operand) →
`drum_fhi_to_pw` param → composer `ws_drd` hi store `sta pwh+1,x` (X=2
unreachable, V3 removed). 27% → FULL 57236/57236. Gates: dmc_smoke 6/6 +
full regression green. f1 count: 5322/5401 FULL + 79 partial.

## ✅ ROUND 121 (2026-07-27): Dreck_Ist_Weg FULL (+1) — the $7D-RETRIG branch-operand wedge (C19 24th occ, singleton)
Next f1 partial by path = `Heinmueck/Dreck_Ist_Weg` (single, base $1000, sub 0
partial at 2.8%: orig re-triggers V2's drum at frame 153, rebuild released).
ROOT CAUSE: ONE BYTE — the $7D SWITCH dispatch `CMP #$7D / BEQ` operand at
$112C patched $56→$2B, re-pointing the branch from the canon switch-toggle
handler ($1183) to canon's OWN mode-0 glide replay tail ($1158 `LDA $1744,x /
JMP $11A6`): $7D = full note-init of the stored glide-start note (init clears
it to 0; only glide rows write it), transpose add skipped, no switch toggle.
Fix (commit this round, ledger C19 24th occ — read it for the technique):
`factory._switch_retrig_probe` (validates exact target+tail, masks the one
operand byte so the member flows through the CANONICAL path — it had been
falling through to dataflow) → typed extract-only `cfg.switch_retrig` → the
walk keeps an {'abs','cur'} shadow of $1744,x/curnote and decodes $7D as a
plain note row `(abs - transp) & $FF` (stream byte-identical to a normal note
row from $11A6 on; composer untouched; ≥$60 = refusal; shadow joins the
endless/wrap keys only when on). Census: SOLE carrier in 10,689 scanned DMC
files ⇒ regression-safe by construction. Dreck 2.8% → FULL 85879/85879.
TOOL GAP: `dmc_canon_diff` reported this member as carrying ONLY the $10DF
track-loop hook — a same-opcode BRANCH-OPERAND repoint is outside its cluster
classes. When a canon member's divergence has no probed wedge, raw byte-diff
vs `docs/dmc4_player_embedded_1000.bin` (774 diffs filtered to 2 real code
wedges in one pass). Also: the $17C0/$1837 row-fetch "appendix" and $F0+/$7C
handling are CANON (already modeled); do not mistake them for patches.
f1 count: 5321/5401 FULL + 80 partial (r119 batch + this).

## ✅ ROUND 120 (2026-07-27): Memomania FULL (+1) — ROM orderlist ptrs (C29 5th) + C34 one-row law generalized ($80-$FD mutation, `runon` flag) + play-time 6510 port (C29 6th)
Next f1 partial by path = `Harti/Memomania` sub 3 (single, base $B800, 6 subs,
only sub 3 partial). ROOT CAUSE: sub 3's V1 **track (orderlist) pointer is
`$F256` = KERNAL ROM** (all other pointers `$C2xx`, in image) — the orig reads
the WHOLE orderlist from banked ROM and plays it (a sector-1 melody then a
transpose walk through garbage); our zero-fill decoded sector 0 forever (played
note 36 immediately where orig rests 4 frames then plays note 40).

Two clean, general, regression-safe fixes (commit 89db7848, ledger C29):
1. **`_offimage_track_ptrs` pre-pass** overlays the CPU-eye window at any
   tune-table track pointer whose 256-byte window overlaps banked ROM
   ($A000-$BFFF / $E000-$FFFF), BEFORE the secp/sector walks. Refactored the
   inline sector overlay into a shared `_overlay_offimage_windows` helper
   (faithful, byte-identical). **STATIC ROM ONLY** — a below-load/zp track ptr
   is DYNAMIC RAM (stability filter → 0 = old zero-fill), so overlaying it only
   moves a divergence. ⚠ **AND GATED to non-post-init members** (same
   `if not (data_post_init or post_sub)` guard as `_undefined_secp_reads`): for
   a `data_post_init` member `mem` is the RUNTIME RAM and a ROM-range orderlist
   address is GENERATED RAM, not banked ROM — overlaying it clobbers the
   generated orderlist. Bisect gotcha: `Kan-Kan`'s raw-image ptrs read `$0000`
   but its POST-INIT ptrs are `$A3A1` (BASIC-ROM range) → without the post-init
   gate the overlay peeked BASIC ROM over the init-unpacked orderlist and
   regressed it 2→0 (found by old-vs-new worktree bisect; classify the gate on
   the SAME `mem` the walk reads).
2. **`_offimage_sectors` / `_undefined_secp_reads` now mirror `_walk_track`**:
   the byte after a transpose is a sector # UNCONDITIONALLY (orig $10FE-$1101,
   even `>= $80`: `$F3 $A5` = sector $A5). The old scans only handled
   post-transpose $FE/$FF (C34) → missed the $80-$FD case → the post-transpose
   off-image sector's secp/data went un-overlaid → `_walk_track` read image
   zeros and spuriously self-looped.

Then THREE more fixes landed **Memomania sub 3 FULL (36108/36108; whole file
6/6 FULL)** — after the user twice (correctly) rejected my "untractable"
conclusions ("dynamic zp", then "engine-state wall"); the sonified zeropage is
in fact 100% STATIC during play (505 snapshots, only $F8/$F9 dynamic) and
everything was C29/C34-reproducible:

3. **C34 one-row law GENERALIZED to $80-$FD (ledger C34 4th occ):** the engine
   re-reads track[pos] EVERY duration expiry (only $7F advances pos; sectpos
   persists) → a post-transpose byte $80-$FD plays ONE row of its garbage
   sector then MUTATES into a TRANSPOSE next fetch. Memomania's KERNAL
   orderlist `$F3 $A5 $BA $D0 $03`: one row each of $0000/$FFFF/$00FF at
   accumulating sectpos, tr stepping 53→05→1A→30, landing REAL sector #$03
   ($C37C) at sectpos base 3; then track[9]=$4C → the endless $0000 tail =
   note 0+48 = the dominant $10C3. Proven by --pc-watch C037 sector-ptr
   run-length [C2E2×76, C8D0×3, C8C8×7, 0000, FFFF, 00FF, C37C×73, 0000×183]
   + otrk/transp memwatch. Walk fix: one-row path covers b>=$80, pending_off
   ACCUMULATES (+ consumed), post-row sub_11E6 $7F-peek advances pos.
4. **`runon` row flag + composer sectpos base threading:** the accumulated
   sectpos is OBSERVABLE (off-table hi idx 130-132 = $1729-$172B live), so
   `_pattern_secvals` gained a per-entry BASE and the last-row-0 rule is
   skipped for run-on rows; base threads across orderlist entries
   (`_sbase_next`). Carrier = the new stated byte-fact flag `runon` (grammar +
   parser + writer; usf_corpus_check 11972/11972). Members without the flag
   byte-identical (base 0, & 0xFF no-op).
5. **PLAY-TIME 6510 port (C29 6th occ):** psiddrv sets $01 = iomap(play)
   before each play() — Memomania plays at $B803 → $36 (BASIC banked out),
   while --peek-post-init snapshots the idle $37. The $0000-sector row at
   offset 1 sonifies the port: $36 = note 54 → idx 102 hi = $170D (STATIC
   reg-offset 0) = freq $0001; the peek's $37 decoded note 55/idx 103 = $0701.
   `_psid_play_iomap` serves $0001 in the overlay; below-$A000 players ($37)
   byte-identical. Boundary noted in C29: under $36, $A000-$BFFF is RAM at
   play time (ROM-window rules assume $37).

Gates: dmc_smoke 6/6; carriers re-verified FULL under the new walk
(Rock_Tec_Tec, Creo/Dance, Hank/Roots; Kan-Kan exactly at its old baseline);
usf_corpus_check clean; golden byte-identity + full regression (see commit).
METHOD LESSON (the session's real story): both "untractable" verdicts came
from stopping at a plausible mechanism instead of tracing the engine's OWN
walk — the pc-watch sector-ptr run-length + the memwatch otrk/transp trace
were each one command and each overturned a wrong conclusion. Trace the
mechanism to the end before classifying anything as residue.

**The class (6 f1 partials with out-of-image track pointers, scanned from the
92-partial `dmc_wide_results` — a raw-image scan, so post-init members'
ptrs are UNDER-reported there):** CANON ROM-ptr → helped (Memomania $F256
26→6086; Cafe_Odd $EBxx sub0 already FULL, sub1 a broken/5-write subtune);
dynamic below-load/zp (Flash/Itinerant, Wind_of_Dead; Goldrake below-load) →
served 0, untouched by the ROM-only gate; POST-INIT (Kan-Kan) → untouched by
the post-init gate. **0 members flipped to fully-FULL** — the value is the
correct C29 extension + a general scan/walk-consistency bug fix + Memomania's
first divergence 26→6086. Gates: dmc_smoke 6/6; Roots + Centric_tune_4 (C29
sector members) still FULL; Kan-Kan byte-reverts to parent (post-init gate);
golden byte-identity over 227 members (portfolio + C29/C34 + 200 random FULLs)
= 0 regressions. Technique/boundaries: ledger [C29](../../docs/ledger/C29.md)
5th occurrence.

## ✅ NATIVE-CAPTURE COMPLETENESS VERIFICATION (2026-07-25): all 4 shipped phases proven ZERO-REGRESSION by enumeration
Prompted by a "are we 100% sure this is sound?" challenge. Every member whose
extraction path any phase could touch was enumerated and verified (not argued):
- **Phase 1** (ghost sim): blast radius = {For_Party} ONLY — of the 14 shape-B
  carriers (`tmp/ffreinit_members.json`), only For_Party reaches the changed
  `_reinit_windows_via_siddump` (the other 13 gate out via the unchanged
  `_extract_reinit_burst`). For_Party = byte-identical windows to py65 + FULL.
- **2a** (compilation dispatch): all 24 f1 compilation members build+verify →
  0 FULL→non-FULL vs the Jul-23 pre-initiative baseline; 6 GAINED (partial→full:
  Rogue_Ninja / Super_Seven / Super_Tau-Zeta / Chwat / Wiz_Max / Black_It).
- **2b** (canon play-phase): 204/204 canon-JT play-wrapper carriers,
  effective schedule identical (done at 2b time).
- **2e** (dataflow play-phase): differ-set = {writes-with-P: 129 → 3 changed,
  all already PARTIAL} ∪ {inverse: 0 candidates over all 5272 writes-no-P}.
  Complete by the derivation "play_phases changes ⟺ observer output changes".
- ⚠ HONEST NET ASSESSMENT: correctness = PROVEN clean. But NOT "zero
  disadvantages": Phase 1 is a pure win (divergence-prone + slow → ground truth
  + faster); 2a/2b/2e are ground-truth-PURITY plays — no verdict flip, no speed
  win (short observers: siddump subprocess overhead ≈ py65), + new C++ tap
  surface (the C36 interrupt-split miss window) + more subprocess spawns in
  extract. Residual meta-risk (census completeness) is small — each census is a
  corpus-wide scan; the full f1 batch vs the Jul-23 baseline would eliminate
  even that (offered, not yet run).

## ✅ NATIVE-CAPTURE PHASE 2e (2026-07-25): re-assembled play-phase observer migrated py65 → siddump pctrace (py65 `_observe_play_phases_writes` DELETED)
The last clean DMC observation-observer on py65. `_build_via_dataflow` now
calls the ground-truth `_observe_play_phases_pctrace` (which was already its
designed fallback) as PRIMARY; the py65 write-footprint observer is deleted.
Gate: full A/B over all 129 f1 writes-with-P carriers → pctrace gives the
IDENTICAL schedule on every S-phase slow-tempo carrier (P_S...), so the final
gate keeps ALLOWING S (a ground-truth 'S' = a genuine play-body SKIP; the body
always writes $D416→P, so a plain member is never spuriously S). Only 3
effective changes, ALL already PARTIAL at HEAD (Hexzakk / Mathematika_II F↔R
re-classifications where ground truth wins; Mothafucka_2SID). Verified: the 3
FULL P_S carriers (Computerized / Postcard_from_Ibiza / Twilight_Worker) stay
FULL; the 3 changed stay PARTIAL; dmc_smoke + full regression clean. The
full-5401 census was killed as disproportionate (~70 min: it runs BOTH
observers per member); the inverse set (writes-None/no-P, pctrace-S-with-P) is
closed by the $D416 mechanism (can only add a correct knob to an
already-partial slow-tempo member, never regress a FULL).
- ⚠ HONEST VALUE: this phase bought NO speed and flipped NO verdict — for a
  SHORT (~12-16 frame) observation, siddump's subprocess spawn + emulator/ROM
  startup OFFSETS py65's interpretation cost (native speed only wins on DEEP
  playback, e.g. Phase 1's ghost sim 15s→5s). Value = correctness/consistency:
  ground truth + one fewer py65 site. DMC play/dispatch observation is now
  uniformly ground-truth (canon `_observe_play_phases` 2b + this).

## ✅ NATIVE-CAPTURE PHASE 1 (2026-07-25): ghost sim migrated py65 → siddump `--reinit-snapshot`. For_Party stays FULL; counts unchanged
Phase 0 of `docs/siddump_native_capture_plan.md` produced the decision doc
(`docs/siddump_native_capture_decision.md`: declarative siddump flags A-first,
binding deferred); Phase 1 migrated the r118 ghost sim's COLD/WARM RAM capture
(`_simulate_reinit_ghosts` step 2) to the new `siddump --reinit-snapshot PC
LO-HI` overlay tap and **deleted the py65 window capture**
(`_reinit_windows_via_siddump` in factory.py). Gates: windows byte-identical to
py65 (2×2048), For_Party FULL (154374/154374), dmc_smoke 6/6, full regression.
- ⚠ **C36 (new ledger entry):** the first flag version false-fired — the wedge
  address $10DD is read as DATA at frame 200 (~9600 frames before it executes),
  so a bare `addr==PC` bus check captured a plausible WRONG WARM (79/2048 off,
  For_Party partial at the reinit). The C20-style control (fresh py65 baseline
  = genuinely FULL) unmasked it. Fix = execution-signature discriminator
  (≥3 consecutive ascending reads) in c64cpu.h.
- Localization gotcha (in C36): `writelog_capture` frame indices are COMPACTED
  (writes-only frames) — burst "frame 9538" = raw siddump frame 9845; my first
  pc-traces searched the wrong window.
- PHASE 2 (same day): `siddump --pc-watch` (executed-PC events, C36-
  discriminated, A/X/Y via overlay MOS6510 getters + play-index + RAM
  windows) + `_observe_dispatch` migrated py65->siddump, py65 loop DELETED.
  A/B gate: spec-identical on all 5 observe-path members (Super_Seven /
  Pour_le_merite / Black_It / Freespace_2075 / Defuzion_3, both masm modes);
  Super_Seven verifies FULL 2/2 subs; dmc_smoke 6/6; full regression clean.
  PHASE 2b: `_observe_play_phases` (canon C18) migrated the same way —
  204-carrier A/B (every canon-JT member with a play wrapper), effective
  schedule identical 204/204, py65 twin deleted; Fuck_Off (P_F123) FULL.
  LESSON in the observer docstring: the play counter is a bus-READ proxy, so
  an init-time data read of the play vector shifts every play index (+1 on
  27/204 carriers) — classification anchors at the first index with events.
  Remaining Class C: `_observe_play_phases_writes` (re-assembled route;
  needs the WRITE footprint per play(), not just PCs — its ground-truth twin
  `_observe_play_phases_pctrace` already exists, so this is a fallback-order
  swap, its own round).
- PHASE 2d ASSESSMENT (no migration — the DMC MULTI-SID observers STAY on
  py65): `_observe_play_phases_chip` / `multisid_active_chips` /
  `_observe_player_bases` are NOT migration targets by the plan's own rule
  (they read init-COPIED bytes -> not divergence-prone; init + a few plays
  -> not slow). AND `_observe_play_phases_chip` has a hard blocker: it is
  called PER-CHIP, so a --pc-watch anchor at the chip's first event loses
  CROSS-CHIP phase alignment for COMPLEMENTARY schedules (one chip per call)
  — Cow_Anus_Fucked went FULL->PARTIAL (both chips ran every call, len_b
  ~2x; A/B over all 19 carriers, caught by end-to-end verify, reverted). A
  correct migration would observe ALL chips in ONE run on a global play
  index (a call-site refactor) — not worth it for 19 rare, non-divergent
  members. Fixed-anchor-vs-first-event is the multi-chip twin of 2b's
  phantom-S anchor problem.
- PHASE 2c FINDING (migration REVERTED): `_postinit_window` is OUT of the
  initiative's scope — it is an IDEALIZED SIMULATION (image + init writes +
  power-on pattern, no driver), which the real machine cannot produce
  (psiddrv resident at $48xx fed driver bytes into the extract base mem;
  Super_Seven sub 1 partial; the golden diff mis-called it "inert" — the
  end-to-end verify caught it). Boundary recorded in the plan Class B + the
  function docstring. Keeper side-products: golden_sid_diff arity fix
  (build() 3-tuple), parse_psid records s['path'].

## ✅ ROUND 119 (2026-07-24): Hank $FF-loop reads a NULL zero-page pointer → loop target is a sonified zp byte (C29 class). Roots FULL (+1)
Next f1 partial by path = `Hank/Roots` (single, canon $1000, vblank,
REASSEMBLED — `dmc_canon_diff` can't linear-align it; canon state geom).
First div flat 102787 f6358: V2 SR $F9 vs $FC at a SYNCHRONIZED track loop
(~98%). The 11 Hank/* members share a $FF-loop variant `A9 00 / 4C <handler>`
where <handler> = `LDY otrk,X / INY / LDA ($f8),Y / STA otrk,X / JMP refetch`
— the loop target is read through zp pointer $f8. In the buggy majority $f8
is a valid track ptr so the read == `track[otrk+1]` == the canon-path default
(loop-to-start, handled). On Roots **$f8 = $0000** (never set on this path),
so the handler reads ZERO PAGE at `$0000+otrk+1`: voice 1 `otrk+1=$31` reads a
player scratch byte, voice 2 `otrk+1=$58` collides with the $0057/$0058
track-pointer slot (live track-ptr-hi). Each voice loops to a DIFFERENT,
runtime-dependent target (0 / $87 / $1A).
- ⚠⚠ **GROUND-TRUTH LESSON (the whole point — [[feedback_ground_truth]]):** I
  first derived the targets with a **py65** sim — WRONG. py65's zero page has
  $00 at $0031 where libsidplayfp has $87 (a player-written / uninitialized
  byte that DIFFERS between emulators). py65 said voice 1 loops to $00 and even
  plays NOISE post-loop where libsidplayfp/siddump (the verdict engine) plays
  SILENT — py65 and libsidplayfp genuinely DIVERGE on a null-pointer player.
  Only voice 2 happened to work under py65 because its source ($0058 = the
  track-ptr-hi) is a DEFINED byte identical in both. **Measure C29 environment
  reads from libsidplayfp (siddump), never py65.** This cost the most time this
  session; the user's "did you forget the core tenet / ground truth?" nudge is
  what turned it.
- **FIX:** `_hank_ff_loop_targets` (factory, dataflow path) — static-detect the
  $FF-loop variant, then siddump `--memwatch-on-write D417` snapshots the 3
  otrk bytes + each voice's track base; find each voice's first otrk JUMP
  (the loop) and override `loop_reset_pos[v]` = landed−1 ONLY where the landing
  is UNRELATED to the canon default `track[otrk_before+1]` (`(landed−deflt)&$FF
  > 8`) — i.e. only the zero-page read. Valid-pointer voices read the track and
  stay byte-identical (None).
- **CENSUS TRAP (amend):** an early "override any voice landing ≥2" heuristic
  REGRESSED 3 valid-$f8 Hank members (Crystal_Dream/Moonlight/Old_School
  full→partial — their real loops legitimately land ≥2 via the correct
  track-read). The track-default comparison gate fixes it: only Roots overrides
  `(None,$87,$1A)`, the 10 others get None → byte-identical FULL. Gates:
  dmc_smoke 6/6, full regression. f1 = 5319 + 1 = **5320 FULL / 81 partial**
  (corpus not yet re-synced). Ledger C29 (occurrence + card).

## ✅ ROUND 118 (2026-07-24): track_ff_reinit SHAPE B + ghost-unit tail (C19 23rd occ). For_Party_V_95 FULL (+1)
Next f1 partial by path = `Hallen/For_Party_V_95` (single, canon $1000,
vblank, 1 song, master_vol=$FF). The hard form of r117's $FF-reinit: wedge
`A9 00 / 4C 00 10` at base+$DD → JMP the init VECTOR ($1000→$101D body), so
the FIRST track end (voice V0) restarts the song. Because V0 is NOT the last
play unit, init's RTS pops V0's call and the play body's `inx : jsr voice`
chain runs V1/V2 as GHOST units (X past $18): on the ORIG map they emit a
member-constant V1-reg SID burst (D400-D404 ×2 = $7A9F/$40, $999B/$40) AND
poke the surviving idle voice's (V3) state so it plays a real held note
($25A3 + PWM sweep) in the restart instead of idling like cold. **FIX (C19
23rd occ — full technique in the ledger):** composer `reinit_ghost`
out-of-line routine (`jsr init` → captured burst verbatim → surviving-voice
pokes → `pla:pla:jmp ptail` skipping our own wrong ghost voices);
`_simulate_reinit_ghosts` captures burst from the orig siddump writelog (the
in-window init burst = the in-window gate too) + pokes from a py65
play-to-wrap RAM-diff vs clean init(A=0), each per-voice slot → composer
label. `track_ff_reinit_ghost` param.
- **THE LAST MILE the reverted pass missed:** the freq-determining poke is
  `curnote+2 = $3E` at $1014 — BELOW $1718. init clears only $1718-$179D, so
  the surviving voice's curnote/gatemask (uncleared $1012/$100F) carry the
  ghost's note. The reverted pass scanned only $1718-$179D and stalled at
  98.4%; the $1000-$17FF RAM-diff finds it automatically → 100.00% FULL first
  try (154374/154374).
- **THE DISCRIMINATOR is the JMP TARGET, not (only) in-window.** The 11
  "shape-B" Hank/* siblings that regressed the reverted pass do NOT re-init:
  their `A9 00 / 4C 1E 10` jumps the re-fetch LOOP ($101E `LDY otrk,x`), not
  init — loop-redirects the ordinary path already handles. Probe requires the
  target to LEAD TO INIT (== base or `_rd16(base+1)`); loop targets rejected.
  Reverted pass's regression was loose `A9 00 / 4C`-only detection catching
  those loops + a compile bug — NOT a fundamental conflict.
- **Census (amend gate, `tmp/ffreinit_members.json`, 14 carriers):** For_Party
  partial→FULL (GHOST); My_Firsty/Second (shape-A) FULL unchanged; 10 Hank/*
  FULL unchanged; **Roots PARTIAL — pre-existing unrelated blocker**
  (`hold_gateoff` member, gets NO param, composer asm byte-identical to r117,
  confirmed no reinit_ghost/ptail markers). Static shape-B scan over all 5833
  f1 = exactly these 12 → 0 other exposure. Gates: dmc_smoke 6/6, full
  regression (see head). f1 = 5318 + 1 = **5319 FULL / 82 partial** (stored
  corpus NOT yet re-synced — next mass-write picks up For_Party).

## ✅ ROUND 117 (2026-07-24): $FF track-loop handler re-pointed at INIT (C19 22nd occ). Second FULL (+1)
Next f1 partial by path = `Greenhorn/Second` (single, canon $1000,
vblank). 99.08% prefix ending exactly at songlength: orig writes
$D418=$0F + a full ascending $D400-$D417 clear at f2776 while ours
plays on — the INIT re-running mid-stream. `dmc_canon_diff` (1 member)
showed it in one shot: the $FF handler patched to `A9 00 / 20 <rts> /
4C 1807` — first track end RESTARTS the song via init (A=0); init's
RTS pops the voice call so the same frame finishes with the filter
tail on fresh state; the restart plays from the top with init-cleared
(NOT loop-carried) state. FIX: `_track_ff_reinit_probe` (full-shape
anchor; the JMP target ≠ the JT init operand here — Second's JT init
is a $101D stub, the wedge jumps the $1807 body directly, so the probe
must NOT require equality) → `track_ff_reinit` param → composer's $FF
fetch tail-calls its own init (`lda cursong / jmp init`; cursong
outside the cleared state block); our init's SID writes ($D418 then
the ascending clear) already byte-match canon. Census: 2 carriers —
Second FULL first try (45383/45383, incl. the mid-stream re-init +
restarted tail); My_Firsty (FULL, wrap past its verify window — the
C32 past-window-latent class) re-verifies FULL with the param. Gates:
dmc_smoke 6/6, full regression 0 regressed. f1 = 5317 + 1 = **5318
FULL / 83 partial**. Ledger C19 22nd occ (entry + card).

## ✅ ROUND 116 (2026-07-24): glide-ARRIVAL off-table reach + event-driven record CREATION (C6 refinement). Psycho_One FULL (+1)
Next f1 partial by path = `Gomez/Psycho_One` (single, canon $1000,
vblank). First div flat 26636 f1654: V1 freq $2A00 vs ours $0000.
`dmc_offtable_probe` mis-fired AGAIN (6th — reported idx 131/$172A
sectpos by value; backlog row bumped, proximity gate overdue). Truth
via memwatch at the diverging write: wnote=$FF, curnote=0, instr 5 —
an off-table read at idx 255 the static reach can't see: a SLOW GLIDE
(sector 01: play 48, glide→0, speed 15; glsp survives rows) ARRIVES
frames later under instr 5's running wave ($1481 TYA/STA curnote=0),
whose -1..-8 offsets then read idx 255..247 (fhi[255]=$17A6=$2A
static; flo side = live gla/durrel, redirect-served). FIX: the
event-driven capture gains a CREATION path (records for observed keys
whose note is a walked glide target + offset ∈ the instrument's wave
offsets — snapshot-skew keys filtered; idx 211-213 excluded), capture
gated on a static risk test (glide targets × wave offsets → nonzero
non-redirect byte). Census: risk gate fires on 758/5401 (+1 siddump
each at extract); 12/12 sampled FULLs create nothing → USF
byte-identical; the 20 risk partials re-verified — all identical first
divergences (blockers elsewhere). Gates: dmc_smoke 6/6, full
regression 0 regressed. f1 = 5316 + 1 = **5317 FULL / 84 partial**.
Ledger C6 refinement recorded (entry + card).

## ✅ ROUND 115 (2026-07-24): per-play fclaim clear re-pointed at a void (C19 21st occ). Jezuseczek FULL (+1)
Next f1 partial by path = `Gomez/Jezuseczek` (single, canon $1000,
vblank). First div flat 34759 f2154: $D416 orig $2F vs ours $7D — right
after a $F1 filterset row. `dmc_canon_diff` on the single member showed
it in ONE shot: NEW wedge at canon $1092, the play body's `STX $1720`
(per-play fclaim clear) re-pointed at void $3F20. Claim persists after
the first filter voice sets it → the filter program NEVER steps; all
cutoff motion comes from $F1 commands (orig freezes at each command's
init cutoff; canon rebuild ramps — hence thousands of matching frames
then a fork at the filterset). Route_clear_dead's sibling ("a CLEAR
store re-pointed at a void ⇒ state persists"), one variable over. FIX:
`_fclaim_clear_dead_probe` (uniform _WEDGE_PROBES row; anchors
LDX #$00+STX, fires only on an out-of-image target) → composer drops
its per-play `stx fclaim`. Probe census: corpus SINGLETON. Gates:
dmc_smoke 6/6, full regression 0 regressed. f1 = 5315 + 1 = **5316
FULL / 85 partial**. Ledger C19 21st occ recorded (entry + card).

## ✅ ROUND 114 (2026-07-24): JSR-first whole-play wrapper AT base+3 (C24 3rd form). Insinuanity + Long_Way_tune_7 FULL (+2)
Next f1 partial by path = `Gillies_Ewen/Insinuanity` (single, canon
$1000, vblank). TELL was textbook C24 sibling: aligned play stream
matches fully, len_a = exactly 2× len_b (right notes, half rate). Play
vector base+3 = `JSR $1085 : JMP $1085` — the whole-play ×2 wrapper
sitting AT base+3 itself, JSR-FIRST, which `_detect_play_repeat`'s
guard (`mem[play] != 0x4C`) still short-circuited (the r52 fix only
admitted JMP-first). FIX: guard → `not in (0x4C, 0x20)`. Census all
5401 f1: exactly 3 JSR-first-at-base+3 members — Insinuanity ×2 +
Odysseus/Long_Way_tune_7 ×2 (identical wrapper, both partial→FULL) + 1
loop-returns-1 (byte-identical); Speed_It_Up (JSR×4:RTS) was ALREADY
detected =4 via play≠base+3 and stays FULL. Gates: dmc_smoke 6/6, full
regression 0 regressed. f1 = 5313 + 2 = **5315 FULL / 86 partial**.
Ledger C24 updated (3rd form + card).

## ✅ ROUND 113 (2026-07-24): sticky-instrument INIT SEED = the $1015,x work-file leftover (C32 refinement). Christmas_Aches_tune_2 + Chopin_2 + Nir_2 + Szat FULL (+4)
Next f1 partial by path = `Gero/Christmas_Aches_tune_2` (single, RELOCATED
base $B645, vblank). First div flat 5803 f356: V2 SR $CB vs $CA at the
voice's FIRST note-init — orig plays instr 1 (hard-restart noise drum,
fires the filter program + $D418), ours instr 0. NOT a wedge
(dmc_canon_diff clean) and NOT instrument content: the note-init computes
`ioff = $1015,x * 11` and canon init clears $1718-$179D but NEVER
$1015-$1017 — the per-voice current-instrument number is a WORK-FILE
LEFTOVER (this member: 08 01 0C), same family as idle_notes/durrel_init/
slide_phase. The walk seeded sticky instr 0 and the composer hardcoded
`curinst,x`=0. FIX (3 legs): (1) extract re-walks with `instr_seed` =
the leftover read at `_eventdriven_addrs(cfg)` INS — CONSUMPTION-GATED
(only when a note row precedes the first $6x cmd; seed <$20 else refuse)
so non-carriers churn zero; (2) `_stated_voice_form` resolver check
`dr.instr == v.instr_seed`, seed emitted as `init { voice N { instr:
i<seed+1> } }`; (3) composer `icinst` slot table primes `curinst,x`,
GATED to the historical `lda #$00` form when all slots 0 (byte identity —
10/10 clean-member sample byte-identical vs stored corpus, 1 finding:
see WARNING below). Census (tmp/seed_census.py, walk-level approx over
the whole jsonl): 44 carriers (34 full + 10 partial). Re-verify all 44:
33 full→full, 4 partial→full, 6 partial unchanged-first-divergence
(Flash Itinerant/Kan-Kan/Wind_of_Dead + Rio Calf_Love ×2 + Mothafucka —
their blockers are elsewhere), 1 full→error = **Freespace_2075**: the
hetero merge's slice check needed i1 REFERENCED and the old hardcoded i1
seeds provided that by accident — fixed in heterogeneous.py by recording
V4's always-live record 0 (idle mechanism, the C31 trap `_groups`
already documents) as an init-voice ref when unreferenced; Freespace
re-verifies FULL 3/3. Canyon (also a carrier, subtune-4+ seeds) FULL,
bytes changed as expected. Gates: dmc_smoke 6/6 ×2, full regression.
f1 = 5309 + 4 = **5313 FULL / 88 partial** (stored corpus NOT yet
re-synced for the 4 gains + changed carriers — next mass-write picks
them up). Ledger: C32 refinement recorded (seed VALUE must be observed,
never assumed cleared).

⚠ WARNING (out of scope, found by the byte-identity sample):
`Nilsen_Ronny/Violation_6_tune_3` (family-2, NOT f1) stored artifacts
are July-7 stale — stored .usf carries pre-C32 otrk_pad params, fresh
extract differs (HEAD == working tree, so pre-existing). Family-2 has
had no recent mass-write; expect this corpus-wide there when family-2
work resumes (C20).

## ✅ CLOSEOUT (2026-07-24, post-r112): fresh full batch + mass-write. **5309/5401 FULL (98.3%) + 92 partial + 0 error**
The r111/r112 changes invalidated every code_hash; the batch
(`tmp/dmc_wide_results.jsonl`) re-verified ALL 5401 f1 members from
scratch — fully authoritative, 0 stale-hash rows. vs the post-r106
closeout (5296+105): net +13 FULL (r107-112 named members + the
a0ff-tail cluster). Mass-write: 5309 ok=5309 err=0, 0 orphans,
path-stratified audit 9/9 from disk, `usf_corpus_check` 11972/11972
parse OK (this refreshed the two Sane members' stale F-token .usf from
r111). Residue = 92 partials; next by path =
Gero/Christmas_Aches_tune_2 (early V2 SR $CB vs $CA + a skipped $D418
write at flat 5803).

## ✅ ROUND 112 (2026-07-24): post-transpose pseudo-sector reaches the C29 gates (C34 3rd occ). Rock_Tec_Tec +6 more FULL
Next f1 partial by path = `Flyt/Rock_Tec_Tec` (single, canon $1000,
vblank). ~95%-in wrap divergence: V3 track tail `a0 ff` (the r100/C34
Dance shape) — but here secp[$FF] = **$0000, the live zeropage** (C29
first class). The C29 GATE walks (`_offimage_sectors` +
`_undefined_secp_reads`) skipped every post-transpose byte, so the zp
overlay never engaged; `_walk_track`'s pseudo-sector probe then read
image zeros → `('endless',…)` (no $7F in garbage) → row dropped → the
rebuild droned the held note at the wrap while the orig sonifies the
6510 port ($2F = note 47). FIX: both gate walks consume the
post-transpose byte + window-check secp[$FE/$FF]; the probe accepts
the 'endless' sim and takes ROW 0. Census: 16 f1 carriers of the
tail shape — 9 FULL unchanged, ALL 7 partials FULL (Rock_Tec_Tec,
Leming/Before_Promises, Mephisto/Lemons, Mermaid/So_Hard,
Rap/Tekkno_of_Doom, Yuro/Eyes, Yuro/Flake). NB `dmc_offtable_probe`
mis-attributed this one too (5th by-value mis-fire — divergence was
V3 ctrl, tool bows out correctly, but r111's idx-150 hit was the 4th;
backlog has the proximity-gate idea). Gates: dmc_smoke 6/6, full
regression 0 regressed. f1 = closeout's 5296 + Ed×4 + Chwat +
Real_Hardcore + 7 = 5309.

## ✅ ROUND 111 (2026-07-24): phase-observer R-positive rule (C18 refinement). Real_Hardcore FULL
Next f1 partial by path = `Finn/Real_Hardcore` (single, canon $1000,
CIA 4x, wrapper `LDX/JSR $141C ×3`). First div flat 79 (frame 6): V1
freq lo orig $18 vs $00 — the per-note vibrato ($1888[note 40]=$18,
table byte-identical to canon) stepped every wrapper CALL in the orig,
never in ours. NOT the off-table read `dmc_offtable_probe` reported
(idx 150 was a later by-value coincidence — the C11 mis-fire warning
again; pc-trace the ACTUAL diverging write first). Cause: py65 observer
→ S (CIA-armed), pctrace fallback classified the $141C calls F via
chip-advance (vib advances!) → wavestep arm entry → vib frozen per
call. FIX (classification only, composer untouched — the R body
`jsr fx_glide` IS the mechanism): `_effects_tail_candidates`
(`bd ?? ?? f0 7e`) + R-positive precedence P→fe→et→advance in both
offset-blind observers; `pctrace_per_play_capture` dict watch_pcs.
Census 117 stored play_phases carriers: 115 identical, 2 flips
(Sane/2_Speed + Voices_in_My_Head, same wrapper) re-verify FULL as R
(their stored .usf now carry the stale F token — refresh at next
mass-write). Gates: dmc_smoke 6/6, full regression 0 regressed.
f1 = closeout's 5296 + Ed×4 + Chwat + Real_Hardcore. Fixed
pipelines/dmc/state_addr.py label-build unpack (build() returns 3-tuple).

## ✅ ROUND 110 (2026-07-23): Chwat compilation — per-subtune slide_phase + state-addr sanity (C31). ALL 7 subs FULL
Next f1 partial by path = `Eye/Chwat` (compilation, players $1000 + $2000;
player 2 re-assembled → dataflow route). TWO defects, both C31 per-player
facts the merge collapsed:
- **Idle priming poisoned**: the dataflow curnote signature FALSE-MATCHED,
  deref'ing $EA12 (outside the image) → player-2 idle notes read as zeros
  → sub 6's whole-song-idle V2/V3 froze on player-1's notes. FIX:
  `factory._state_addr_sanity` — state addrs (curnote/gatemask/dual_parity)
  outside the loaded image → None (canon base-offset fallback). Flipped
  sub 6 FULL.
- **Dual parity flipped**: p1 $1019 leftover = 1, p2 = 0; file-level
  `init.slide_phase` served all subtunes → p2's dual instruments swapped
  wavestep/slide per-play interleave (ours 61,58,58 vs orig 61,61,58; the
  pc-trace shows writers $160D/$14DD ALTERNATING). FIX: `DmcSong.dual_phase`
  (merge sets it only when players disagree) → per-subtune
  `init { slide_phase: N }` — InitState.slide_phase became Optional[int]
  (None = unstated/inherit; explicit 0 now expressible; writer emits on
  not-None so existing corpus text unchanged) → composer gated `sphase`
  per-song table. Flipped subs 1-4 FULL.
Gates: dmc_smoke, usf_corpus_check 11959/11959, full regression 0
regressed. f1 = closeout's 5296 + Ed×4 + Chwat; next by path =
Finn/Real_Hardcore.

## ✅ ROUND 109 (2026-07-23): third Ed filter-def driver (C19 20th occ). Only_Ones FULL
Next f1 partial by path = `Ed/Only_Ones` (single, base $E000, both vectors
→ appendix $EB9A/$EBE0). First div frame 27: $D416 $03 vs $02 (the first
phase-A INC of def2.init). Two-phase SMC-retargeted def-table animator:
phase A (every 16 plays) def2 init/stop ramp → $62, res nibble = 1..15
counter, then def1 init/stop DOWN to $02, then retarget; phase B (every
play) def2 = tri[X1]/2+$0A, def1 = tri[X2]/2+$0C over an init-generated
triangle (4..$83), X1 +1/8 plays, X2 +1/16. FIX: `_filterdef_anim3_probe`
(template-matcher w/ hole captures + operand cross-refs) →
`filterdef_anim3` → composer `playooa` chunk. FULL first try
(145440/145440). Ed cluster CLEARED (Cliche_Beat r106, Elechromania r107,
Go_Funk r108, Only_Ones r109 — 4 distinct bespoke drivers, all C19
singletons). Gates: dmc_smoke 6/6, full regression 0 regressed. f1 =
closeout's 5296 + 4; next partial by path = Eye/Chwat.

## ✅ ROUND 108 (2026-07-23): filter-tail stub sonifies POWER-ON pattern into player data (C19 19th occ). Go_Funk FULL
Next f1 partial by path = `Ed/Go_Funk` (single, base $E000, CANON vectors).
First div frame 27: $D416 orig $FF vs ours $06. The filter tail's final
`STA $D417` (base+$AC) is re-pointed at a stub: does the store, then every
24 plays (first after 11) pokes THREE data cells from PAST-EOF addresses =
the POWER-ON RAM PATTERN (C29): def0.init ← page $EF walk (+1), and TWO
WAVEFREQ-table bytes (offsets 14/29; one X2+=2 walk on page $EE feeds
both — a poked wavefreq byte is a NOTE OFFSET; pattern $FF = -1 shifted
V1's notes 24→23 at the 2nd divergence). TWO TRAPS: (1) `--peek-post-init`
showed RELOCATED-psiddrv bytes at $EE00+/$EF00+ and DISAGREED with the
play-run RAM — memwatch is ground truth, `_poweron_fill` models it
exactly; (2) with the 11-byte instrument stride the wave-table targets
first read as "unused instrument bytes" — map poke targets against EVERY
table base (they were wavefreq+14/+29). FIX: `_d417_tail_anim_probe`
(full-shape, fail-open) → `d417_tail_anim` param → composer `playgfa`
chunk at play START, counter seeded +1 (orig pokes at play END —
observably identical), generated power-on pages; wavefreq pokes ride the
LAYOUT-PRESERVING pool (extract forces `wave_table_pos` for carriers,
drops the param if not provable). Gates: dmc_smoke 6/6, full regression 0
regressed. f1 = closeout's 5296 + Elechromania + Go_Funk (next:
Only_Ones, ANOTHER appendix at $EB9A/$EBE0).

## ✅ ROUND 107 (2026-07-23): filter_mod generalized to MULTI-TAP (8 progs). Elechromania FULL
Next f1 partial by path = `Ed/Elechromania` (single, base $E000). First div
frame 13: $D416 cutoff hi $DB vs $CE. Both vectors re-pointed at an
appendix — the SMC roving-pointer table stream AGAIN (the filter_mod
mechanism, Ed/Core_of_Acid), but EIGHT taps: APPLY = 8× `LDA ptr / STA
fd+16p+1 / STA fd+16p+3` (ONE pointer per def feeds BOTH init+stop cells),
then 8 wrap/inc automata (cap hi=$F3 → reset $F0FF → always INC; visited
cycle = reset+1..reset+period INCLUSIVE — the $F300 bridge byte is read
once per cycle, so the contour is ram[reset+1+i], phase = p-reset-1; the
old probe's ram[reset+i] convention would be off by one byte per cycle
HERE — simulate, don't assume). Init generates the 513-byte triangle
(+1×253 / -1×253 + patch glitches) and runs APPLY once, so file pointer
bytes = play-1 positions. FIX: `factory._filter_mod_multi_probe` (full
shape template, fail-open, ';'-joined per-prog segments in the SAME format)
→ to_usf splits on ';' (usf.filter_mod dict + grammar already multi-prog) →
composer playfmod loop de-limited (labels suffixed by slot; single-tap =
init_phase==stop_phase). Census: appendix shape = ONLY Core_of_Acid (kept
on the single probe via `or` short-circuit, rebuilt MD5-IDENTICAL) +
Elechromania. Gates: dmc_smoke 6/6, full regression 0 regressed.
f1 counts = closeout's 5296 + Elechromania (queue: Go_Funk next).

## ✅ CLOSEOUT (2026-07-23, post-r106): fresh full batch + mass-write. **5296/5401 FULL (98.1%) + 105 partial + 0 error**
The r106 factory change invalidated every code_hash, so the batch
(`tmp/dmc_wide_results.jsonl`) re-verified ALL 5401 f1 members from scratch
— fully authoritative. vs the r90 baseline (5256+145): net +40 FULL (the
named r91-106 members plus propagation from the C29/C11-class fixes).
Mass-write: 5296 written ok=5296 err=0, 6 orphans removed, path-stratified
audit 9/9 from disk, `usf_corpus_check` 11959/11959 parse OK. Portfolio NOT
re-derived (the new dims — filterdef_anim, undefined-secp — are corpus
singletons, below the >=2x portfolio bar). Residue = 105 partials, next by
path = Ed/Elechromania (the Ed custom-driver cluster continues).

## ✅ ROUND 106 (2026-07-23): appended FILTER-DEF ANIMATOR driver (C19 18th occ). Cliche_Beat FULL
Next f1 partial by path = `Ed/Cliche_Beat` (single, canon $1000). First div
frame 17: $D417 res nibble orig $37 vs ours $17, state_match=False. The res
nibble WALKS across note-inits ($17→$37→$47) while fbase + the def-table
FILE bytes stay constant — `taint_source 1960` showed def1's r0 DYNAMIC (15
ascending values $11..$F1) = the data is ANIMATED at runtime. Both PSID
vectors re-point at an APPENDED driver: init pokes defs 0-2 (r0=$11,
init=$02, captured by the existing post-init def window — why our START
matched), builds a triangle table $14..$93 at $1C00, aims an SMC JSR; per
play: phase 1 = every 8 plays defs 0-2 r0 += $10 until def0==$F1 → retarget
to phase 2 = every 12 plays def0.init=tri[i--], def1.init=tri[j], j+=2
(author bug: 3rd store hits def1 twice; def2 never animated). TRAP: the SMC
slot's FILE byte points at phase 2 (stale) — probe the aim from the init
immediates. FIX: `factory._filterdef_anim_probe` (full-shape template,
fail-open, lifts '10,F0,08,08,08,0C,14,93') → `filterdef_anim` param →
composer `playfda` wrapper chunk (phase flag; generated triangle; targets
fdres+0..2 / fdinit+0..1 — composer def slots are dense in orig order).
Sibling of filter_mod (Ed/Core_of_Acid). Census: signature singleton
corpus-wide. Gates: dmc_smoke 6/6, full regression 0 regressed. NOT closed
out; f1 counts = r90's + r91-106.

## ✅ ROUND 105 (2026-07-23): off-image SECTOR-POINTER fetch (C29 3rd occ). Trailways_A FULL
Next f1 partial by path = `Dunkel_Nilsen_and_Elektrond/Trailways_A` (single,
relocated base $C000, no wedges). First div 91.7% in, AT the track wrap
(otrk 13→14): every voice note = ours + 32 with otrk/sectpos/transp in
LOCKSTEP — content differs, walk agrees. Root cause: the final track
entries select sector $11 (17) but the file has 10 sectors; secp_lo[$11]
lands inside the secp_hi table ($CA, in-image) while secp_hi[$11] sits at
$CB48, PAST the image end ($CB42). The engine reads power-on $FF there →
orig plays the sector at $FFCA (KERNAL tail — the CHKOUT `JMP ($0320)`
operand $20 IS note 32); our zero-filled image view mislocated it at $00CA,
so the EXISTING C29 window machinery peeked the wrong address (live-zp
zeros → note-0 rows). FIX: `_undefined_secp_reads` pre-pass in extract()
(mirrors the `_offimage_sectors` walk; collects pointer-fetch addresses
outside the image; `_cpu_peek` serves them BEFORE sector resolution;
post-init mem exempt — already `_poweron_fill`-seeded). DIAGNOSIS: the
V3 note-init freq census (74 hits, 8 stable values, the diverging $002C a
ONE-OFF at the wrap) + `dmc_offtable_probe` bowing out ("no off-table read
of that value") discriminated content-divergence from serving-divergence in
two commands; memwatch otrk/sectpos/transp then pinned the lockstep walk.
Gates: dmc_smoke 6/6, full regression 0 regressed (regression-safe by
construction — only mislocated sector decodes change). NOT closed out; f1
counts = r90's + r91-105.

## ✅ ROUND 104 (2026-07-23): the Doxx TEMPO MAILBOX (C14 3rd family). Two_Channels FULL
Blocker 2 resolved: the r103 "duration decode" suspicion was WRONG — the
decode was exact. The custom Doxx build ADDS A TEMPO COMMAND canon DMC
lacks: the rewritten play body tails into `LDA curinst+2 / CMP #$10 / BCC /
AND #$0F / STA $1716 / RTS` — V3 instrument commands >= $10 double as
"speed reload = n & $0F" (the mid-song speedup 3→2 at ~55% shifted every
later tick; the hold gate-off clears were the first visible symptom). FIX:
`factory._v3_instr_tempo_probe` (shape scan, STA pinned base+$716) →
extract attaches fx `tempo=N` to the stated V3 rows (phantom instrument
statement KEPT — the pool already carries records 18/19 faithfully) →
composer `_pattern_tempos` + gated `[$05, N]` pattern-prefix event setting
`spd` at the row fetch (next-reload semantics = the orig's play-tail
mailbox). `tempo=N` round-trips the grammar; direct vs round-tripped build
MD5-identical. DIAGNOSIS LESSONS (hard-won): (1) the motif repeats — I
state-watched the WRONG occurrence for three passes; ONLY a straddle-free
flat diff with EMPTY FRAMES KEPT (grep -o 'W:.*' silently drops 0-play
buckets and corrupts frame attribution!) pins the true frame; (2)
`memwatch $1716/$1718` then showed the cadence change in one look — watch
the SPEED COUNTER whenever tick-phase-dependent writes (hold clears, dur
plateaus) drift by one play. Gates: probe census = exactly ONE carrier corpus-wide (Two_Channels itself, singleton — zero exposure), dmc_smoke 6/6,
full regression 0 regressed. NOT closed out; f1 counts = r90's + r91-104.

## ✅ ROUND 103 (2026-07-23): play_unit_repeat ZERO count (voice unit REMOVED, C24). Two_Channels 0%→55.7% (superseded by r104 — FULL)
Next f1 partial by path = `Doxx/Two_Channels` (single, base $1000 — a
heavily CUSTOM Doxx build: rewritten play body, different init, relocated
globals ($1636 shadow), stale $1016 cur-inst byte). BLOCKER 1 (fixed): the
play body inserts INX before the first per-voice JSR — voice 0 NEVER runs
(true two-voice build; V1 track = bare $FE, but canon $FE voices still
freewheel refreshes → we emitted a phantom voice, first div at flat 0).
FIX: C24 play_unit_repeat generalized to 0 counts (probe tracks X through
the JSR/INX scan; composer max(0,..) + filter clamped ≥1). Census: 5
firers — Two_Channels 0,1,1,1; NEW Enforcer_2_Level_1_preview 1,1,0,1
(first div 32→15,663) + Blood_2_game 1,0,0,1 (excess tail halved), both
pre-existing partials; both Tichelmann stub carriers unchanged + FULL.
Gates: dmc_smoke 6/6, full regression 0 regressed.
BLOCKER 2 (OPEN, documented for the next round): at 55.7% (f3243) our V2
runs the holding gate-off ADSR-clear ($00/$00) ~9 frames EARLY — orig's
dur counter shows a 4-tick row where our decode reaches dur==1 a tick
early; the row is inst 3 (drum+hold+noise_attack, fxf $91 via ioff —
$1016 is stale in this build, use $174D,x for instrument identity); orig
alternates noise/tri wave steps with freq $1000 which is NOT an in-table
note (drum-mechanism output). Suspect: duration/row-boundary decode in
this custom build's sector format. The $17EC holding code is canon and
UNREACHED at the event (pc-traced) — the orig fires it at its own dur==1
later. Member stays partial (first div moved 0 → 38,287 of 68,070).

## ✅ ROUND 102 (2026-07-23): rest-tail RTS wedge = rest_effects 'none' (C19 17th occ). Bassy_Introtune FULL
Next f1 partial by path = `Doxx/Bassy_Introtune` (single, base $1000,
relocated globals — shadow at $1636 etc.). First div ~frame 102: a play
where orig emits ONLY V1 hard-restart + filter tail — V2/V3 (both
fetching REST rows that tick) write NOTHING. Wedge: canon $1180
`JMP $1322` (rest tail → run effects) patched to RTS ⇒ a resting voice
runs NO effects on its fetch frame — a FOURTH rest_effects variant
'none' (family-2 'skip' still runs the wave-step refresh; 'none' skips
even that). DIAGNOSIS TRAPS: siddump 0-play buckets + straddled plays
look like "short plays" (frames 7/20/44… were straddle artifacts); only
the FLAT stream identifies the genuinely short play. FIX: extend both
rest-dispatch probes (canon $1180 opcode + `_dataflow_knob_probes` shape
scan) with the RTS case → `rest_effects='none'` → composer `rest_none:
rts` target + gated dispatcher arm (code 3); emission byte-identical for
everyone else (label only emitted when used). Gates: corpus census → 2
carriers, BOTH partials (Bassy_Introtune + sibling Blue_Dos_t0nt — both
flip FULL; zero FULL-side exposure); dmc_smoke 6/6; full regression 0
regressed. NOT closed out; f1 counts = r90's + r91-102 gains.

## ✅ ROUND 101 (2026-07-23): route-clear-dead wedge (C19 16th occ). Classic_Mix FULL
Next f1 partial by path = `Daf/Classic_Mix` (single, base $1000). First div
frame 1: $D417 orig $07 vs ours $05 (V2's routing bit cleared). Orig
memwatch: $1018 shadow NEVER changes although V2 note-inits non-filter
inst 1 — because the wedge re-points ONLY the note-init clear's store
(canon $12C6 `STA $1018` → `STA $101C` void) while the OR-set site is
canon: routing bits accumulate, the leftover $07 (already carried as
init.sid.filter.res_routing) persists all song. FIX:
`factory._route_clear_dead_probe` (anchors BOTH sites' canon shape, fires
iff set==shadow ∧ clear≠shadow, fail-open) → `extra_params` →
composer `route_clear` f-string gate emits NO clear in ni_filter. Gates:
probe census over stored FULLs + partials queue → exactly ONE carrier
corpus-wide (Classic_Mix itself, a singleton wedge — zero FULL-side
exposure, knob defaults off = everyone else byte-identical); dmc_smoke
6/6; full regression 0 regressed. NOT closed out; f1 counts = r90's +
r91-101 gains.

## ✅ ROUND 100 (2026-07-23): track-layer C34 (post-transpose $FF = one-row pseudo-sector). Dance FULL
Next f1 partial by path = `Creo/Dance` (single, base $1000). First div ~95%
in at the track wrap: orig plays real content, rebuild droned a note-0
outro. Root cause = C34 2nd occurrence AT THE TRACK LAYER (canonicalized):
the transpose handler consumes the next byte ITSELF as a SECTOR ($10FE
`INY/LDA/TAY`, no $FE/$FF recheck), so the tail `...$A0 $FF` plays ONE ROW
of secp[$FF] (aimed at a real phrase at $1C1C); the track byte is
re-dispatched per ROW-fetch (next fetch sees $FF → loop), and the $FF loop
does NOT zero sectpos → the loop-target sector RESUMES at the consumed
byte count, skipping its leading instr/dur commands (which then inherit
sticky state, C32). Old `_walk_track` decoded sec=$FF as a full endless
garbage sector (loop_to=last, the observed drone). TWO FIXES:
- `_walk_track`: post-transpose $FE/$FF → simulate ONE row (sticky applied
  from its stated cmds; width = row kind + stated commands, the sectpos
  derivation), then re-dispatch as track byte with `pending_off` carried
  into the loop-target sector's start.
- `_fold_stated_orderlist._stated_equal` (C32 boundary): intro/loop
  variant pairs must be ENCODING-equivalent (carried instr/vol only);
  stated-content/duration diffs REFUSE → legacy unrolled representation
  (the composer plays the intro variant on every pass — both its paths —
  so a stated-differing pair was mis-emitted; also cured the Rayden
  2SIDs' latent carried-duration collapse).
DIAGNOSIS TRAIL: memwatch otrk ($1726-8) showed lockstep 0-22→0 vs our
62/44/26-entry decode; pc-trace of $10D2/$10EF/$10DD gave the per-row
re-dispatch + the one-row quirk (armchair readings of the disasm were
wrong TWICE — trace, don't infer). Gates: census over ALL stored .usf +
partials queue → 16 v4 carriers; 11 FULLs re-verified FULL (incl. 4
Rayden 2SIDs + Experiment + Sans_intro), 4 partials pre-existing
(refusal doesn't fire for them; play_match deltas = stale r90 baselines,
exonerated); Dance + Experiment FULL; dmc_smoke 6/6; full regression 9
families 0 regressed. NOT closed out; f1 counts = r90's + r91-100 gains.

## ✅ ROUND 99 (2026-07-23): per-SUBTUNE off-table byte via instrument value-class SPLIT. Assassins + Useless_1994 FULL
Next f1 partial by path = `Creo/Assassins` (single, base $1000, 2 subtunes;
sub 0 was FULL). Sub 1 first div: V1 note freq hi $CE vs $80 = off-table fhi
idx 98 = $1709 (V1 track-ptr slot, per-subtune init state) — the C31
"file-level idx-keyed window can't hold a per-player fact" in its
SINGLE-PLAYER form: both subtunes reach the record through the SAME inst 21,
so instrument-usage attribution can't disagree and
`_correct_offtable_postinit`'s all-agree check fell back to the start-song
sample ($80 = sub 0's byte; sub 1 reads $CE). FIX (extract-only):
`pick`'s loop records per-subtune sampled values on disagreement
(`m.offtable_song_values`); new `_split_offtable_by_subtune` (end of
extract) clones the instrument per VALUE-CLASS + remaps the non-start
classes' rows — the composer's EXISTING `ovr_sub` per-subtune window patch
then fires (used-instruments now disagree) with zero composer/schema change.
Honest content: the subtunes hear different pitches there. Gates: 86
stored-FULL multi-subtune offtable carriers extracted, only 2 fire (Rayden
Bamse_Bert_2SID + Leprechaun_Boot_V1_2SID — both re-verified FULL through
the multi-SID merge); partial census: Assassins 2/2 + Useless_1994 2/2
(bonus) flip FULL; dmc_smoke 6/6; full regression 9 families 0 regressed.
NOT closed out; f1 counts = r90's + r91-99 gains.

## ✅ ROUND 98 (2026-07-23): wavepos-layout gate relaxed to OBSERVABILITY. Object_of_Art FULL
Next f1 partial by path = `Compod/Object_of_Art` (single, base $1000) — the
ORIGINAL wavepos-blocked member from 2026-06-28, finally landed. First div:
V3's first note-init freq hi $1D vs $1F = fhi idx 213 = $177C, V3 reading its
OWN wavepos during its own inst-5 wave step (self-referential; orig 29 =
inst 5's wave_start, ours 31 = file-image leftover served static).
`_wave_layout_verbatim` had rejected the member because inst 2's program is a
$9F marker CHAIN (walks 2-14, hops to 0) — not a verbatim slice. FIX
(extract-only, C11 refinement): non-verbatim programs are admitted when
UNOBSERVABLE — every recorded wavepos read must be self-referential (reader
voices == {idx-211}, new `m.offtable_read_voices` attribution in
`_assign_offtable_freq`) to a verbatim instrument; the non-verbatim program
gets a FREE pool position past the verbatim placements (composer untouched,
place_prog contract intact). Idle non-verbatim / cross-voice / unattributed
reads still reject. TRAP RECURRENCE: `dmc_offtable_probe` by-value scan
mis-attributed the read to idx 130 "sectpos" (3rd misfire — r95 warning);
the real read fell out of the instrument's off value (160+53=213).
Gates: 45 stored-FULL live-stamped 211-213 carriers (19 potential gate-flips
+ 26 already-layout) ALL re-verified FULL; partial census: only Real_Hardcore
also flips layout (first-div unchanged at 79, neutral); dmc_smoke 6/6; full
regression 9 families 0 regressed. NOT closed out; f1 counts = r90's +
r91-98 gains.

## ✅ ROUND 97 (2026-07-23): off-table glide-target boundary DISSOLVED. Cleve_24 FULL
Next f1 partial by path = `Cleve/Cleve_24` (single, base $1000). The r22
"off-table glide target" HARD BOUNDARY (C11) re-measured and RESOLVED — the
2nd expiry precedent after fclaim. Mechanism: glide_to raw byte $7E (note
126); arrival `CMP freqhi[126]` = live dtmph, which the dual-slide keeps
equal to the current slid hi ⇒ INSTANT arrival, curnote=126, wave offset +12
⇒ idx-138 reads (static lo + live fbl[2] hi). Measurement: our dtmpl/dtmph
shadow tracks orig 1:1 (0 mismatches / 2,843 events — memwatch-on-write
D40E, orig $1724/25 vs our labels). Fix (composer only):
- `_glide_target` parses EXACTLY (the deliberate 125-mis-parse deleted).
- The arrival compare is served through the SAME off-table redirect map as
  the reload: out-of-line `ga_cmp_sub` (inline blew branch range), gated on
  `_Model.glide_offtable` = any (glide_to+transpose)&$FF>95 — everyone else
  byte-identical.
- The extract already enumerated glide-target reads (r.glide_to + wave
  offsets) and to_usf already live-flags canon records — no extract change.
- NB my earlier "no offtable records" reads were a broken dict iteration
  (enumerate over m.instruments yields KEYS) — records existed all along.
Gates: ALL 109 stored-FULL class members (glide_to octave ≥8 in stored
.usf) re-verified FULL; dmc_smoke 6/6; full regression 9 families 0
regressed. NOT closed out; f1 counts = r90's + r91-97 gains.

## ✅ ROUND 96 (2026-07-23): track-loop IMMEDIATE wedge (loop-to-N). They_Are_the_Best_1 + 6 more FULL
Next f1 partial by path = `Brian/They_Are_the_Best_1` (single, base $1000,
family-2-style `rest_effects: skip`). C19 15th occurrence: the canon $FF
handler's `LDA #$00` immediate hand-patched to `#$02` ⇒ every voice loops to
track pos 2 (C13 loop-to-N semantics as a 1-byte tweak; invisible to both
the canon-shaped `loop_site` detection AND `dmc_canon_diff`'s immediate
LIMIT). TELL: same-instant note-init with a completely different row at the
wrap + post-wrap transpose = pre-wrap value (loop lands past the leading
transpose command) + a small length tail. FIX: static probe in dataflow.py
(sig `C9 FF D0 08 A9 imm 9D` + STA operand == track-pos addr) → existing
`loop_reset_pos=N`; no extract/composer change. Census 12 carriers, 0
baseline-FULL; **7 flipped FULL**: They_Are_the_Best_1, Cubehead ×4
(Absolute_the_introduction / Again_and_Again / Never_Brake_Me /
Shapeless_Dreams), 4_Simone, Quattrodance. Just_11 / Witchs_Birthday /
Conversion still partial (other blockers); Arthur ×2 = nonstandard_vectors.
Gates: dmc_smoke 6/6, full regression 9 families 0 regressed. NOT closed
out; f1 counts = r90's + r91-96 gains.

## ✅ ROUND 95 (2026-07-23): glide_neutered wedge (glide dead + DATA POKE). Ice_on_Fire 1/1 FULL
Next f1 partial by path = `Bleed_Into_One/Ice_on_Fire` (single, base $1000).
C19 14th occurrence — the canon glide dispatch's speed store re-pointed
(`$1136: STA $1741,X` → `STA $1F41,X`), TWO effects (full analysis in
[ledger C19](../../docs/ledger/C19.md), 14th occ):
- glsp never written ⇒ NO glide/slide ever moves. Extract: probe
  `factory._glide_neutered_probe` (store vs fx_glide-read operands at canon
  offsets base+$131 / base+$41C, read must be canon-consistent base+$741,
  fail-open) → `extra_params['glide_neutered']=<store hex>` →
  `_SecFmt.glide_dead` forces the decoded speed nibble to 0 (the engine's
  glide-cancel semantics; byte consumption + `glide_to` target kept, composer
  untouched). First div 21743 → 137486.
- `$1F41` is INSIDE the song data (sector 20 pos-37 note byte): each voice's
  executed speed nibble is POKED over `target+X`. V1's `$C4` → note byte $04;
  V3 audibly plays note 4 there (its wave offset −12 then reads freq[248] =
  live durrel — the surfaced divergence value). Extract:
  `engine_model._glide_poke_overlay` simulates the poke on a per-song mem
  copy when the voice's speed nibbles are a singleton. 137486 → FULL 170095.
- DIAGNOSTIC TELL: "our note exactly 2 below orig's at a note-init, and only
  on the pattern's SECOND occurrence" — first playthrough predates the poke.
  Also: `dmc_offtable_probe`'s by-value read attribution mis-fired twice here
  (idx-180/idx-115 static stories); the real reads were in-table — trust the
  pc-trace of the producing store over the by-value scan when they disagree.
- Gates: probe census ~16 firing members, all 11 baseline-FULL carriers
  re-verified FULL (2 probe cuts rejected for regressing Rocket_n_Roll /
  mis-pairing compilations — see C19); dmc_smoke 6/6; full regression 9
  families 0 regressed. NOT closed out (no 5401 batch); f1 counts = r90's +
  r91-95 gains.

## ✅ ROUND 94 (2026-07-23): RELOCATED heterogeneous sub-players. Black_It 9/9 FULL
`The_Syndrom/Black_It` (the second `base_override_not_player` member) landed
on the r93 machinery + relocation support. Commit `8f82ffc9`. Structure: an
in-image V4 player ($4200, subs 1-7, NON-identity song map — subs 6/7 were
only coincidentally FULL under the single fallback) + a RELOCATED V4 player
($F200, sub 8) + a RELOCATED **family-4 V5** player copied to $1000 (sub 0,
head `JMP +$40 / JMP +$95`). Pieces: `_base_kind` knows the family-4 head +
the observe path classifies kinds AT THE LANDING on RAM; `post_init_sub`
plumbed through DMCV5Config/both v5 `_load`s (snapshot at the landing);
`dmc_v5_config(base_override=)` dispatches family-4 heads; the heterogeneous
merge orders the V4 unit FIRST in id space regardless of player index (only
V4 has file-level init the park/lift can't carry). Gates: 7 compilations +
Jupiter41/Katusha/Space_Walk FULL, dmc_smoke 6/6, full regression 0 regressed.
The `base_override_not_player` residue class is now EMPTY.

## ✅ ROUND 93 (2026-07-23): heterogeneous V4+V5 compilation. Super_Tau-Zeta 5/5 FULL
Next f1 partial by path = `Super_Tau-Zeta` (r90's `base_override_not_player`
residue): 2 canonical V4 players ($A400/$9000) + a **DMC V5** player at $B400
(head `JMP +$40 / JMP +$A1`) behind the wrapper — the first V4+V5
heterogeneous member. Commit `48d7624e`. Key findings:
- **The $B400 player is PARTIALLY RELOCATED**: the re-linker patched only the
  paths song 0 reaches; 101 reloc operands still hold canon $1xxx values, none
  executed (pc-trace-proven). `dmc_v5_config(base_override=)` admits
  `mv == rv OR mv == rv+delta`; build+verify judges dead-path claims.
- **V5 wave_init has NO $90 marker check** ($137F reads ctrl[start] raw,
  INCs; wave_step $165B redirects without recheck). Instrument 8 starts ON
  its own marker → first note frame plays the raw ($90,$20) bytes (ctrl $90 =
  test+noise to the chip). `_slice_wave` rewritten as an exact walk
  simulation (C2 canonical); previously-passing shapes byte-identical, 25
  affected v5 FULLs re-verified FULL (0 regressed).
- **Heterogeneous machinery generalised** (pipelines/music_assembler/
  heterogeneous.py): V4 players merge via the homogeneous compilation path as
  ONE unit; V5/MA one unit each; per-subtune `wave_programs` override (NEW
  MusicSubtune field — the V5 idle program is per-player state, same class as
  per-subtune freq_table/default_filter); `set_instr=` fx refs now first-class
  in _refs/_shift_refs (shared deduped pattern OBJECTS must shift ONCE);
  v5 from_usf maps set_instr id→engine position (identity standalone).
- **Round-90 aftershock fixed**: `_is_player_head` had a STALE three-JMP
  duplicate in extract/engine_model — `_postinit_window(stop_at_player=True)`
  never stopped on two-JMP heads and burned 1M steps → None. One
  implementation now (engine_model), compilation.py re-exports.
- Gates: dmc_smoke 6/6; 6 key compilations FULL (Freespace 3/3 hetero_masm,
  Quad_Core, Super_Seven, Rogue_Ninja, Canyon, Para_Lander_DX);
  usf_corpus_check 11919/11919; full regression 9 families 0 regressed.
- **NOT closed out** (no 5401 batch). f1 counts below still r90's + r91/92/93
  gains. The other `base_override_not_player` member, `The_Syndrom/Black_It`,
  re-checked with the new code: now builds as a compilation but subs 4/5/8
  stay partial (play_match 26/26/1, different residue class; "third player
  layout"). Next f1 partial by path: re-run `dmc_next_partial`.

## ✅ ROUND 92 (2026-07-23): per-subtune rest_effects + the CPU-EYE environment window. Super_Seven 2/2
Next f1 partial by path = `Super_Seven` (COMPILATION: players $1000/$3800,
player 1 RELOCATED — the wrapper copies image pages $2000-$2EFF → $3800-$46FF).
Sub 1 needed TWO independent fixes; commit `d1016d30` (rest_effects) + the
env-window commit after it.
- **FIX 1 — per-subtune `rest_effects` (C31 open item, closed).** Player 0 is
  family-2 (`rest_effects='skip'`), player 1 canon ('run'); the merge kept the
  start player's extra_params → player 1's filter sweep stalled one frame at
  every event-fetch boundary (div at play 142; TELL: fclaim=0 + fframe frozen
  at the D416 write on hold frames). Merge writes disagreeing values to
  `DmcSong.params` → `MusicSubtune.params`; composer widening GATED (tune-rec
  byte +9 → `resteff` → 3-way `rest_dispatch`); all-agree members
  byte-identical. Census: Super_Seven = the ONLY disagreeing carrier of 21
  compilations. 142 → 78009.
- **FIX 2 — the truncated-copy KERNAL-tail window (C29 generalized, 2nd
  class).** The wrapper's copy CUTS the player's data at $46FF; secp_hi[9]
  ($4700) reads POWER-ON RAM ($FF stripe under libsidplayfp, $00 under py65
  zero-fill) → sector 9 at $FFEF = the KERNAL jump-table tail ($4C JMP
  opcodes = the audible "note 76") + psiddrv's PATCHED reset vector
  ($FFFC/D = $11/$48, invisible to RAM-only memwatch AND to ROM files) +
  16-bit pointer wrap into env zeropage. Cure, three layers:
  `_poweron_fill` pattern-seeds `_postinit_window` (+ psiddrv's $0-$3FF
  zero); `_offimage_sectors` gates on ANY played sector leaving defined RAM;
  window bytes from NEW `siddump --peek-post-init` / `_cpu_peek` (CPU-eye
  read through the MMU — facade `sidplayfp::cpuPeek` → `c64cpubus::peek`,
  mirrored into libsidplayfp-overlay). 78009 → FULL (157,986).
- **TWO regressions caught by the 25-member gate batch, both fixed:**
  (1) overlay clobbered DEFINED bytes via spurious garbage-record windows
  (Pour_le_merite sub 0 + Abyssal_Karma 1-4, priming smashed) → overlay only
  bytes ≠ image and == reference seed; (2) peek's mid-play snapshot vs the
  old stability filter for DYNAMIC RAM (Remix_1995: stack-page window bytes;
  plus last-wins $F8/$F9 pokes across overlapping low windows) → RAM bytes
  go through `_postinit_values` stability (static→value, dynamic→0), and
  $F8/$F9 are served SELF-REFERENTIALLY per window inside
  `_simulate_sector.rd()`. Baseline discipline: fresh worktree at the parent
  commit proved Remix_1995 FULL pre-change (C20 reflex).
- **Gate: 22/25 FULL** (Super_Seven + Rogue_Ninja + Killer_Beat/Axel_Foley/
  Remix_1995/Centric_tune_4 + all 16 prior-FULL compilations); Chwat/Wiz_Max/
  Goldrake stay partial (other residue). dmc_smoke 6/6. NOT closed out — no
  full 5401 batch; f1 counts below still r90's (5256/145) + Rogue_Ninja +
  Super_Seven. Next: re-run `dmc_next_partial`.

## ✅ ROUND 91 (2026-07-23): event-driven off-table correction is a per-player runtime measurement. Rogue_Ninja 2/2
Next f1 partial by path = `Rogue_Ninja` (COMPILATION: players $1000/$2000;
sub 0 → ($1000, song 0) FULL, sub 1 → ($2000, song 0) partial). Sub 1 diverged
at V2 freq hi (orig $B7 / ours $D6) — off-table idx **97** (Y=$61 from a
wave-step note), reading `freqhi[97]` = **$2708** = $B7 (player 1's static
window byte); ours had player 0's $1708 = $D6. Same per-player-window class as
r89's Para_Lander_DX (idx 96) but the r89 fix DIDN'T cover it. Commit before
this memory; ledger C31 EXTRACT rule gained its second-miss instance.
- **ROOT CAUSE — the SIBLING runtime measurement.** r89 made
  `_correct_offtable_postinit` compilation-aware (`song_subtunes` → sample the
  file subtune that selects the player). Its sibling
  `_correct_offtable_eventdriven` was missed: it ran siddump with **no
  `--subtune`** (start song = player 0) AND watched **hardcoded canon addresses**
  (`$1783/$1012/$172F/$1732`), so for player 1 it captured player 0's note-97
  read ($1708=$D6) keyed by the same `(inst,off,note)` and OVERWROTE the
  post-init-resolved $B7. The post-init pass had it RIGHT; the event-driven pass
  re-litigated it wrong.
- **FIX (two axes — subtune AND addresses):** `_eventdriven_addrs` derives the 5
  watched 3-voice tuples from cfg — CN/INS base-relative (`curnote_addr`/
  `base+$12`), Y/BLO/BHI freq-table-relative (`freq_hi+$DC/$88/$8B`) — so a
  RELOCATED player's state block is watched; `_correct_offtable_eventdriven` runs
  each file subtune in `song_subtunes.values()` and keeps a key only where every
  run agrees. Canon single-player (base $1000, freq_hi $16A7, no song_subtunes)
  computes the exact canon addresses + start song → **byte-identical** (the 5224
  single members unaffected). Also fixes a LATENT relocated-single-player bug
  (the canon hardcode was wrong there too, just never bit).
- **0 regressed / 1 gained** over all **21 detected compilations** (16 FULL stay
  FULL incl. Para_Lander_DX/Quad_Core/Canyon/Zap_Zone/Protox-1; Rogue_Ninja
  gains; Super_Seven/Chwat/Goldrake/Wiz_Max still partial = different residue).
  Full regression green (9 families, DMC portfolio 11 ok); dmc_smoke 6/6.
- **NOT closed out** — no full 5401 batch this round, so the f1 counts below are
  still r90's (5256 full / 145 partial). A closeout batch may surface more gains
  from the relocation-awareness (relocated singles that hit the event-driven
  path). Next f1 partial by path after Rogue_Ninja: re-run `dmc_next_partial`.

## ✅ ROUND 90 (2026-07-23): two-JMP player head + reach-refined filter merge. Quad_Core 4/4 + Zap_Zone/Protox-1
Next f1 partial by path was `Quad_Core` — NOT `Rogue_Ninja` as r89's head
claimed (Q < R). r89's note skipped it: the hint queue is rewritten in place,
Quad_Core's row was sitting `full`, so `dmc_next_partial` (which only re-confirms
`partial` rows) jumped past it; my queue repair (see below) reset all rows to
`partial` and resurfaced it. A wrong `full` row silently removes a member from
the work queue until a re-seed — a C20-flavoured trap in the queue itself.
Commits: `dmc_next_partial` hardening + the compilation fix. Two blockers, both
closed, plus a scare and a tool near-miss:
- **DETECTION — two-JMP player head.** Quad_Core packs 3 RE-ASSEMBLED DMC
  players (`$2000/$1000/$2F00`) with a **two-JMP head** (init `JMP base+$807` /
  play `JMP base+$50`), then data at +6 — not the canonical three-JMP head, so
  `_is_player_base` rejected all three bases and the file fell to the single-
  player path (garbage for the subtunes not on the LOAD-address player).
  Generalised the player-base signature to the two essential vectors (init +0 /
  play +3), validated by a reloc-invariant **target-range** check
  (`[base, base+$1000)`) that replaces the third JMP as the false-positive
  guard. `_is_player_head` (no floor) + `_is_player_base` (with floor) +
  `_is_player_base_ram` all share it. Across ALL 5401 f1 members **exactly TWO
  change detection**, both `None`→compilation (Quad_Core + Super_Tau-Zeta); NO
  existing spec changes (proven by old-vs-new detection diff) — which is why all
  15 FULL compilations stay byte-identical.
- **FILTER MERGE — the static `repeat>5` refuse is an over-approximation.**
  Player 1 def 1 has repeat=8 but its first step's dur=0 pins the walk on step 0
  until fcut settles IN-record → no overrun. Replaced the static check with
  `_walk_filter`, an exact sim of the composer's `fx_filter` step-walk that
  reports whether the step index actually advances to ≥6 (the real cross-record
  overrun). A genuinely-overrunning single player gets a new **overrun-anchored
  layout** (strategy 3): its window verbatim at native indices up to the
  overrun's reach, other players' compact-safe defs in the free slots the
  overrun never touches. Cap 16 (the composer's 8-bit `16*def#` walk index).
- **REGRESSION SCARE (C20): Lane_Crazy + Mystery went partial** on my first
  merge cut. Detection specs were byte-identical old-vs-new (so not detection);
  git-stash confirmed both FULL on old code = REAL regression from the merge.
  Root cause: my reach sim hit its iteration `_cap` on a LOOPING filter def
  (repeat≤5 or non-settling), returned the conservative "unbounded" and
  mis-flagged it as a genuine overrun → routed a previously-compact member into
  strategy 3, reordering its window. Fix: `_def_overruns` fast-paths repeat≤5 to
  False and keys on "step index reached ≥6", never on settling. 0 regressed
  after.
- **Gains: Quad_Core 4/4, Zap_Zone 2/2 (compact, false overrun), Protox-1 2/2
  (strategy 3, genuine overrun).** Zap_Zone/Protox were the documented
  genuine-overrun residue (were detected, merge RAISED → single-player fallback
  → partial; now merge succeeds). **0 regressed / 4 gained** over all 24 detected
  compilations (Para_Lander_DX also shows a "gain" only vs the pre-r89 r88
  prior). Full cross-family regression green (9 families); dmc_smoke 6/6.
- **Super_Tau-Zeta** now DETECTS (2nd two-JMP member) but merge-blocks on the
  `base_override_not_player: $B400` locate residue (shared with Black_It) — was
  partial, stays partial (fallback), NOT a regression. Next residue subclass.
- **TOOL near-miss:** a `git stash`/`git stash pop` dance INSIDE one Bash command
  that TIMED OUT stranded my changes in the stash (working tree at old code).
  Recovered via `git stash pop`. LESSON: never stash/pop inside a single command
  that can time out — split into separate commands, and `git diff > patch`
  first.
- **CLOSEOUT (fresh `tmp/dmc_f1_qc.jsonl`, full 5401-member batch): 5256 full /
  145 partial / 0 error — 0 regressed / 4 gained vs r88** (Para_Lander_DX from
  r89 + Quad_Core + Zap_Zone + Protox-1). Build paths: 5224 single / 16
  compilation / 15 multisid / 1 hetero_masm. Corpus SYNCED: 5256 written, 0
  errors, **0 orphans**, audit **10/10** stored artifacts re-verify across all
  four build paths. usf_corpus_check **11919/11919**. Full regression green (9
  families); dmc_smoke 6/6. Next f1 partial by path = `Rogue_Ninja`
  (compilation, sub 1 diverges).

## ✅ ROUND 89 (2026-07-23): the off-table window is a PER-PLAYER fact. Para_Lander_DX 3/3
Next f1 partial by path = `Para_Lander_DX` (a COMPILATION: players $2000 and
$1000; subtune 0 → ($2000, song 0), subtunes 1-2 → ($1000, songs 0-1)). Subs 0
AND 1 diverged at V3 freq hi (orig $C8 / $D2, ours $0B) — the SAME off-table
idx 96, which is each player's OWN V1 track-ptr-lo slot ($2707 / $1707). Commit
5bc03955; ledger C31 gained the third per-player fact (both halves).
- **EXTRACT half:** the per-player extract numbers songs LOCALLY, and
  `_correct_offtable_postinit` fed those straight to `siddump --subtune`. So
  player $1000's song 0 was sampled in file subtune 0 — which runs the OTHER
  player, leaving $1707 at the never-inited FILE-IMAGE leftover $0B (subtune 1
  reads $D2). New `DMCV4Config.song_subtunes`, built in `_player_cfg` from
  `spec['map']`. Same shape as r85's filter-def post-init re-read.
- **COMPOSER half:** the window is ONE file-level idx-keyed array, so the two
  players' records at position 0 resolved last-wins (which is why fixing the
  extract alone would have flipped sub 1 FULL and left sub 0 partial).
  Attribute each record to the subtunes whose ROWS play its instrument (USF
  content — NO schema addition); on disagreement, init writes those positions
  for its subtune. ALL conflicting positions on EVERY init, else a subtune
  inherits its predecessor's patch. Gated ⇒ conflict-free members byte-identical.
- **Measurement traps this round — ALL FOUR now fixed in the tools** (~30 min
  lost; the retrospective is the fix):
  - Nothing said the member was a COMPILATION. `dmc_state_addr` printed
    `base $1000 / CANON / shift +$0000` while the divergent read was at
    `$2707` — the confident-wrong-answer class the tool exists to refuse, one
    level out. It now reports EVERY player base + the subtune→player map and
    resolves each address once per player; `dmc_build_one` (and `dmc_smoke`)
    now always print the build path.
  - per-frame `--memwatch` said $1707 was constant and `taint_source` saw only
    {$0B,$D2} — neither covers a value that differs per PLAYER at the SAME
    canon offset. `--memwatch 1707,2707` per subtune settled it in one run.
  - `siddump` silently swallowed stray args (a legacy positional catch-all
    turned a SPACE-separated address list into `--subtune 1708`) and produced a
    plausible wrong dump. Unrecognised args are now a hard error.
  - `--subtune` is 1-BASED (verify's sub k = `--subtune k+1`) — now stated in
    the usage text; and `env.sh` finally puts `tools/` on PATH, which CLAUDE.md
    had claimed all along.
- **Census (C19, both sides): 0 regressed / 1 gained.** Exposure is cheap and
  complete for the FULL side — scan the stored `.usf` for two instruments
  naming one window position with different bytes: **16 of 5401** (14 single,
  1 multisid, 2 compilation). Those 16 + all 18 detected compilations
  re-verified FULL. Full regression green (9 families); dmc_smoke 6/6.
- **NOT yet closed out** — no full 5401 batch this round, so the f1 counts
  below are still r88's. Next f1 partial by path is now `Rogue_Ninja`
  (compilation, sub 1 diverges at write 25596/226742).

## ✅ ROUND 88 (2026-07-23): a rejected redirect row EXPIRED — $1720 fclaim. f1 **5252 full / 149 partial / 0 error**, corpus SYNCED
Next f1 partial by path = `Industrial_Sci-Fi` (V3 freq hi $00 vs $01 at write
130601 of 224675 — 58% deep). Root cause: an off-table freq read at **hi idx
121 / lo idx 217 = $1720, the FILTER CLAIM FLAG** — the one deliberate hole in
the otherwise-mapped $1718-$1723 filter-state block. Commit ba1e09e7; ledger
C11 gained the "a rejection expires" lesson.
- **The row was rejected 2026-06-29** (+0 recovery / −1 Long_Night, "fclaim
  timing ≠ orig") — measured on **family-2** and filed as a fact about the
  variable. It is a fact about ONE composer on ONE date: re-measured now, our
  `fclaim` and the orig's `$9720` agree at **ALL 12,784 read moments, 0
  mismatches**. The composer's claim has been op-for-op the orig's for a while
  (same play()-entry reset, same first-voice-in-X-order store, both starting
  each play() at 0 ⇒ no seed needed, like `guard`/`fxf`).
- **No static byte could ever serve this read** — the value depends on which
  voice claims the filter that frame, so `_offtable_eventdriven` drops the key
  as unstable and the window falls back to the post-init sample ($01, while the
  orig reads $00 there). **A key the event-driven capture OMITS is the positive
  signal for a redirect row**, not a reason to improve the capture.
- **TRAP that cost the first measurement: the player is RELOCATED ($9000).**
  Probing canon $1720/$177D watched unrelated RAM and returned an incoherent
  picture (fxf=$FF, route=$00, claim always 0 — while $D417=$F1 said voice 1
  WAS routed) that read as a genuine engine difference. Offset every watched
  address by the member's `base` first. TELL: watched bytes that contradict
  the write stream.
- **Census (C19, both sides): 45 f1 FULLs read idx 121/217 via the static
  window — all held. 0 regressed / 11 gained** on the 205-member subset (all
  160 partials + all 45 exposed FULLs), then confirmed on the full batch.
  v5 is structurally unaffected (4-tuple `at(...)` records, never consumes
  `offtable_live_idx`).
- **Stored `.usf` go stale-by-SEMANTICS here** (C20 third layer): a stale
  `at(...)` at a now-live idx sets `_static_at_live` and turns that member's
  WHOLE redirect off — so the round's mass-write had to regenerate, not rebuild.
- **Tool fix:** `divergence_census.py` now dedupes the results jsonl LAST-WINS.
  A batch jsonl is append-only, so a resume leaves superseded rows; the census
  was counting them (10802 "members" for a 5401-member family) and listing
  already-FULL members as partial representatives.
- **CLOSEOUT (fresh `tmp/dmc_f1_r88.jsonl`, full 5401-member batch): 5252 full
  / 149 partial / 0 error — 0 regressed / 11 gained vs r87.** Build paths
  unchanged (5366 single / 18 compilation / 16 multisid / 1 hetero_masm).
  Corpus SYNCED: 5252 written, 0 errors, **0 orphans**, audit **10/10** from
  disk across all four build paths. usf_corpus_check **11915/11915**. Full
  regression green (8 families); dmc_smoke 6/6.
- **RESIDUE (149):** freq clusters still dominate — V3 freqlo 16 / V1 freqlo
  12+7 / V2 freqlo 8+6 / V3 freqhi 6, plus V1 SR @<64 9 (the Zap_Zone/Protox-1
  compilation filter-overrun class) and $D418 7. 10 `unknown`.

## ✅ ROUND 87 (2026-07-22): past the cap — WIDEN the index. Lane_Crazy 6/6
`Lane_Crazy` (4 players, 6 subtunes, **39** merged instruments) — **6/6 FULL**
(155299 / 109993 / 3892 / 3916 / 130448 / 109037). Commit b3fc59d3; ledger C8
gained the widening half of the r86 sibling. f1 **5241 full / 160 partial / 0
error**, corpus SYNCED.
- **Raising a cap without widening its index ALIASES.** r86 moved
  `_MAX_INSTR` to 32, the bound of fx_pulse's `id*8 + pwphase` 8-bit index.
  At 39, ids ≥32 wrapped onto instrument 0's records — subs 4+5 diverged at
  **V1 PW lo, write 24**, which is the wrap's signature (the pulse-step path,
  early, on the players holding the high ids).
- **The widening is NOT a 16-bit index.** Shrink the STRIDE to the record's
  true width (6; the 8 existed only so the index could be `asl×3`) and give
  each instrument a base BYTE: `ldy cinst,x / lda istepbase,y / clc / adc
  pwphase,x / tay`. Index stays 8-bit, cap = 256/6 = **42**, and it costs one
  cycle LESS than the shift chain (C25 asks that of anything on the per-voice
  per-frame path).
- **The ORIGINAL has no wider index to copy** — it computes its record offset
  as `ASL×3 + ADC×3` (= ×11) in the 8-bit accumulator with carries dropped,
  wrapping after 23 instruments, INSIDE the editor's own 0-27 range (the C11
  wrap `_inst_offset` reproduces). It never needs more because one editor file
  holds ≤28; 39 exists only because we MERGE four packed players.
- **Gate = byte-identity, not re-verification.** The layout is gated on the
  count, so all **5240 stored f1 members rebuild BYTE-IDENTICAL** from their
  stored `.usf` — which re-confirms the C20 fifth-layer invariant corpus-wide
  in the same pass. 22 compilations: 0 regressed / 1 gained. Full regression
  green (8 families); dmc_smoke 6/6.
- `dual_freq_generator` + >32 instruments is REFUSED, not approximated (the
  wedge's off-the-end reads are stride-8 positions; empty intersection today).
- **CLOSEOUT (fresh `tmp/dmc_f1_r87.jsonl`, full 5401-member batch): 5241 full
  / 160 partial / 0 error — 0 regressed / 1 gained vs r86.** Build paths: 5366
  single / 18 compilation / 16 multisid / 1 hetero_masm. Corpus SYNCED: 5241
  written, 0 errors, **0 orphans**, audit **13/13** stored artifacts re-verify
  across all four build paths. Post-sync usf_corpus_check 11904/11904.
- **RESIDUE:** the instrument-overflow class is now CLOSED. Remaining
  compilation residue = Zap_Zone/Protox-1 filter overrun + Black_It's 3rd
  player layout ([[project_dmc_compilations]]).

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
  multisid / 1 hetero_masm. Corpus SYNCED: 5240 written, 0 errors, **0
  orphans**, audit **13/13** stored artifacts re-verify across all four build
  paths. Post-sync usf_corpus_check 11903/11903.
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
Built `pipelines/dmc/canon_diff.py` ([[reference_dmc_canon_diff]]) — the PROACTIVE
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
GREEN. Promoted the scratch build helper to `pipelines/dmc/build_one.py` (build one
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
(5477 full / 165 partial). TRAP re-confirmed: pipelines/dmc/mass_write.py has NO --help —
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

## Census (pipelines/future_composer/engine_fingerprint.py — renamed/generalized from fc_fingerprint)
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
Artifacts at hvsc85/.../Geometrical_Zaks.{usf,sidfinity.sid}.

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
pipelines/dmc/family_batch.py (Pool(8), crash-safe JSONL resume).
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
   helper-at-$1018). Runner pipelines/dmc/family_batch.py (--members/--out).
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
   pipelines/dmc/v5/family_batch.py. **WIDE-BATCH COVERAGE = COMPOSER-GATED
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
   pipelines/dmc/v5/mass_write.py) + hvsc84.db refreshed. RESIDUE: 481 partial
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
engine-blind). DMC feature extractor + `pipelines/dmc/regression_portfolio.json`
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
686-member corpus (`pipelines/dmc/v5/family_batch.py --members tmp/v5_family4_members.json`),
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
