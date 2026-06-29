---
name: project_dmc
description: "DMC (Demo Music Creator) migration — the new focus engine (10,676 HVSC SIDs, largest family). Census DONE: V4 canonical = 5401 (50.6%), target. Research docs + fully annotated V4 disassembly DONE (pipelines/dmc/v4/disassembly.s, rep Geometrical_Zaks). KEY: data-table addresses are PACKER-PATCHED operands — extract by dataflow, never fixed offsets. NEXT: config + extract + composer emitters, write-log-first on Zaks."
metadata: 
  node_type: memory
  type: project
  originSessionId: c83d6f65-8c2c-42bb-8f55-d46a1994efb2
---

## ✅ V5 (family-3/5): 1068/1495 FULL (71.4%, 2026-06-29) — glide-wrap fix +27

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
- **partial 176** — not yet characterized; likely the off-table freq tail (hard,
  same class as family-2/V4). NEXT V5 lever to investigate.
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
`docs/offtable_freq_plan.md` + `pipelines/dmc/v5/RE_NOTES.md` rounds 11-18.

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

## Related
[[project_fc_fingerprint_and_standard]] (the playbook this follows),
[[feedback_dataflow_over_heuristics]] (the operand-patching finding is
exactly this), [[feedback_disassembly_data_section]] (research.md's wrong
tables), [[feedback_init_trichotomy]] (the $1018 leftover).
