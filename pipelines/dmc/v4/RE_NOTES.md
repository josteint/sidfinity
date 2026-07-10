# DMC V4 — RE notes / migration log

## ✅ ROUND 67 (2026-07-10): R-PHASE = PULSE TAIL, not register refresh — Toccata_v2 +1 partial → FULL (0 regr) [ledger C18 R-entry variant]
First still-partial f1 member by hvsc path after re-verifying the stale Jul-9
batch (the Bakewell_Dwayne run ahead of it — End_of_1992_intro/Acid_Dance/
Action_G/Attacker/Axel_F_v2/Groove/Journey/MON_Tribute/Mad_Drummer — all flipped
FULL in rounds 55–66): `MUSICIANS/B/Bakewell_Dwayne/Toccata_v2.sid` (vblank,
single sub, 523140 writes). Trichotomy play_match 883, state ✓ at true length;
first divergence `$D402` V1 PW lo, orig `$10` vs rebuild `$20` on frame 30.

ROOT: `play_phases='P_R123'` — the member's init generates a parity play-vector
wrapper (`$2702: LDA/INC $26EF / AND #$01 / BEQ→$1003 full / JMP $1006`), and
`$1006 → $162F: JSR $135D x3`. `$135D` is the pulse routine ($134E) PAST its
`LDA $18f3,y / STA $171F` speed-nibble reload, so the R phase runs a SECOND
pulse advance per music tick, computing its step from the STALE `$171F` (=$01
here) left by the prior full-play frame (up-sweep phase 0 → `$01&$F0`=$00 = hold;
down-sweep phase 1 → `($01&$0F)<<4`=$10 = the −$10 half-step). The write-footprint
observer read the R phase as a plain refresh (the pulse HOLDS its value for the
first ~6 frames, so no advance shows in the 12-call window); once the sweep
moves (~frame 30) the R frame's PW diverges — orig advances, the rebuild's
`fx_glide` refresh re-emits the stale value. The full-play path reaches `$135D`
only by FALL-THROUGH from `$134E`; a JSR to it is uniquely the wrapper's R entry.

FIX (C18 R-entry variant, twin of `effect_entry_variant='vibflip'` for the F
phase): `factory._rphase_pulse_tail_probe` runs a few play() calls under py65 and
watches for a `JSR base+$35D` (execution ground-truth — "observe, don't parse")
→ param `rphase_variant='pulse_tail'`. Composer factors the pulse up/down sweep
behind a `pw_sweep` label and adds a gated `pulse_tail` routine (nibble-select
the step from the stale `wjmp`=$171F by `pwphase` parity, + `cpwbase`, `jmp
pw_sweep`); the R token's body JSRs `pulse_tail` instead of `fx_glide`. The
composer already writes `wjmp` at the same sites the orig writes $171F, so the
stale value coincides. Regression-safe by construction: census over ALL 743
non-canonical-play f1 members = exactly 1 carrier (Toccata_v2); every other build
is byte-identical (the label emits no bytes; the gated routine + `r_call` are
absent when the param is). Verdict FULL 523140/523140, state ✓. Post-fix sweep
DEFERRED to the next batch (per session instruction); 4 short-FULL sanity members
re-verified FULL.

## ✅ ROUND 65 (2026-07-09): $D418 RE-ASSERTED EVERY FRAME (filter-tail wrapper) — Groove +1 partial → FULL (0 regr) [ledger C19 10th occurrence / C10 master-vol-every-frame]
First f1 partial by hvsc path (Attacker=r64 now FULL, everything ≤ idx 381
re-confirmed FULL): `MUSICIANS/B/Bakewell_Dwayne/Groove.sid` (vblank, single sub).
Flat first-div at position 2 — very early. Per-frame dump nails it: the ORIG
writes `$D418=$1F` (filter LP mode `$10` | master vol `$0F`) EXACTLY ONCE PER
FRAME, at the END (after the `$D416`/`$D417` filter writes) — even on frames with
no note-init (f50 gate-off still emits it). The REBUILD instead wrote `$D418=$1F`
at each FILTER NOTE-INIT (V1+V2 in f1) and NOT at frame-end — the canonical DMC
behavior (`$D418` written only at init + filter note-init `$12A8`; `$D416`/`$D417`
every frame).

ROOT (C19 hand-patched wedge, disassembled from the orig image): the play-body
global filter routine's `$10AC: STA $D417` is REPLACED by `JSR $2000`, and the
`$2000` wrapper is `STA $D417 / LDA #$10 / ORA $1717(mvol) / STA $D418 / RTS` — so
`$D418 = mode | mvol` is re-written every frame. The canon filter note-init
`$12A8: STA $D418` (`8D`) is patched to `BIT $D418` (`2C`) — neutered — and the
preceding `$12A5: STA $2004` SELF-MODIFIES the wrapper's `LDA #imm` to the current
filter's mode nibble per note-init. Net write-stream: `$D418` once per frame at the
filter-tail END, never at note-init.

FIX (CORE TENET — reproduce the WRITE, not the SMC mechanism): `factory.
_d418_filter_tail_probe` (STATIC opcode probe, reloc-invariant on the fixed
hardware `$D416`/`$D417`/`$D418` addresses) anchors on the LIVE play-body filter
routine — `STA $D416 / LDA abs / ORA abs / JSR <wrapper>` at +9 — and returns the
wrapper's initial mode immediate. → USF param `d418_filter_tail` (C10
master-vol-every-frame parametric form). Composer: at filter note-init store
`fdmode,y` into a `d418mode` shadow (SUPPRESS the note-init `$D418` write); append
`lda d418mode / ora mvol / sta $d418` to the per-frame filter tail; prime
`d418mode` from the probed immediate in init. Default None → canonical (note-init
writes `$D418`), the else-branch reproduces the original template verbatim →
byte-identical build.

TRAP CAUGHT (the whole reason the probe is anchored, not a bare byte-scan): the
first, LOOSE probe (`STA $D417` followed by `LDA #imm` + `STA $D418` ANYWHERE)
FALSE-FIRED on Cubehead/Qbhead_01 — whose aux/init routine at `$1CA8`
(`STA $D416 / LDA #imm / ... / STA $D418`) matches the bytes but is NOT the
per-frame path (Qbhead's LIVE filter routine at `$10A3` is canonical
`STA $D417 / RTS`, no per-frame `$D418`). That would have REGRESSED Qbhead_01
(a FULL) → partial. Caught by localizing each census carrier's first divergence
(orig had no per-frame `$D418`). Tightening the anchor to the play-body routine's
`STA $D416 / LDA abs / ORA abs / JSR-wrapper` shape excluded it — Qbhead_01
probe → None → byte-identical → FULL. LESSON: detect the exact REACHABLE site
(anchored to the play-body computation), never a matching byte pattern anywhere in
the image.

REGRESSION-SAFE BY CONSTRUCTION: `d418_filter_tail` None for every canon member
(probe None → byte-identical). CENSUS (static probe over all 5401 f1): exactly
**3** carriers — Groove (`imm=$10`), Rap/Hands_up_Ravers (`$20` BP), Rorschach/
For_Vandalism_27 (`$10`) — ALL previously partial ⟹ 0 FULL exposure. Groove FULL
155620/155620 (100% flat match, state ✓); the 2 siblings also verify FULL
(census-confirmed +2 the next batch accounts for). Full `tools/regression.py`
GREEN (0 regr all 7 families: Hubbard 71, Companion 44, C64ME 15, Jay_Derrett 17,
FC 31, DMC 12, Basic 22). Post-fix bucket sweep SKIPPED per user (next batch
accounts via code_hash). f1 ≈ 5163 FULL / 238 partial (per-round accounting; wide
batch STALE).

## ✅ ROUND 64 (2026-07-09): RESET-ALL loop target can be PER-VOICE (not one N) — Attacker +1 partial → FULL (0 regr) [ledger C13 refinement]
First f1 partial by hvsc path (End_of_1992_intro=r60, Acid_Dance=r61, Action_G=r62
all now FULL): `MUSICIANS/B/Bakewell_Dwayne/Attacker.sid` (vblank, single sub,
dataflow route). Flat first-div 143638 = 98.8% of the ×1.1 window = deep in the
LOOP TAIL, state ✓. The write signature is a SYNCHRONIZED 3-voice hard-restart (all
voices prep `ctrl=$08/AD=$0F/SR=$0F` → note-init together) + a `$D418=$1F` master-vol
write, but the rebuild resyncs only V2/V3 while V1 keeps sweeping ONE play() longer.
GROUND TRUTH (`--memwatch 1726,1727,1728`): at the divergence the orig track position
jumps V1 `26→4`, V2 `53→31`, V3 `26→4` — a loop-back with a DISTINCT target per voice.
Disasm: the `$FF` handler is `CMP #$FF / NOP NOP / JSR $1020 / JMP $10D2`, and
`$1020 = LDA #3/STA $1726 / LDA #$1E/STA $1727 / LDA #3/STA $1728` = reset-all to
**3/30/3** (→4/31/4 after the fetch INC). This IS the round-53/62 reset-all idiom,
but the three immediates are NOT equal, so round-62's equal-immediate guard skipped
it → `track_loop_target` stayed True (read-next) → V1 walked past `$FF` (`$00`) as a
jump target and drifted off the loop.

FIX (extract-only, dataflow — ledger C13): generalize `loop_reset_pos` from a scalar N
to a per-voice tuple `(n0,n1,n2)`. Drop the equal-immediate requirement; to stay
regression-safe REQUIRE the STA triple to BE the track-position address, derived
relocation-safely as the operand of the orderlist-fetch read `LDY tpos,x` (`BC`)
immediately followed by `LDA (zp),y` (`B1`). `_walk_track` receives the per-voice
scalar (the extract call site indexes the tuple by voice). NO USF field, NO composer
change — the walk emits the resolved per-voice orderlist; `loop_reset_pos` is an
extract-time derivation knob (§8 arrangement per the principle).

REGRESSION-SAFE BY CONSTRUCTION: the equal-immediate path is left byte-identical
(round-53/62 carriers unchanged: Unfinished_1/Feelin_Blue `None`, Action_G `5`,
Axel_F_v2 `4`, MON_Tribute `5`); the per-voice branch is a POSITIVE minority signature
anchored to `track_pos`, so a non-reset-all init storing 3 consecutive immediates can
never false-match. CENSUS (`dataflow.locate` over all 5401 f1 members): exactly **1**
tuple carrier — Attacker itself (previously partial) ⟹ 0 FULL exposure. Attacker FULL
145313/145313 (state ✓). Full `tools/regression.py` GREEN. Post-fix sweep SKIPPED per
user (the next family batch accounts for it via code_hash).

LESSON (round-62's lesson, one level deeper): when a positive-minority signature
carries literals, the SHAPE is the discriminator and EACH literal is per-voice DATA —
don't assume the literals are equal any more than you bake in their value. f1 last
known ≈ 5162 FULL / 239 partial (per-round accounting; wide batch STALE at the current
code_hash).

## ✅ ROUND 57 (2026-07-08): play-phase F misread as R on a HELD note — frame-entry reachability for the offset-blind observers — My_Rusty_Love_C64 +1 partial → FULL (0 regr) [ledger C18 new note]
Random f1 partial Psych858o/My_Rusty_Love_C64 (CIA 6x, re-assembled layout,
canon route rejects no_jumptable → dataflow). Trichotomy (per-IRQ): play_match
1287, state ✗ — at the first HELD note the orig re-asserts `V1 AD=$00/SR=$00`
EVERY play() call while the rebuild does it only on a `✓✓✗✓✗✗` 6-cycle.
V1-block segmentation of the flat stream showed orig blocks n=7 (with AD/SR)
vs reb alternating n=7/n=5. ROOT: the member's wrapper `$26CA` runs full play
every 6th call and `$1006→$1937→$18F1` on the rest — `$18F1` = a 5-sub-phase
dispatcher with per-voice MASK tables (V1 `[1,1,1,1,1]`, V3 `[0,0,1,1,1]`)
whose per-voice call is `JSR $1944 = JMP $11FA` = the FULL frame entry (this
re-assembled variant shifts it +1 off canon $11F9; state arrays individually
re-laid-out too, pwstep base $175A). So the truth is `P_F1_F1_F13_F13_F13` —
but the offset-blind writes-observer's chip-state R/F rule read
`P_F1_R1_F13_R13_R13`: a HELD note's frame entry emits only IDEMPOTENT writes
(freq/PW/ctrl re-emit held values) for the whole 12-call window, so nothing
"advances" and the calls false-read as R; the composer's R emission
(glide+write tail) then drops exactly the holding gate-off `AD/SR=$00`
(sub_17EC fires every call while the duration counter sits at 1 — dur DECs
only on TICK frames, so slow tempos hold it at 1 for many calls). FIX (ledger
C18 note — restore the CANONICAL entry-reachability form on the offset-blind
paths): `_frame_entry_candidates` locates the frame entry BY SHAPE
(`bd ?? ?? d0 03 4c` = `LDA pending,X / BNE +3 / JMP`); the py65 writes
observer watches those PCs per call, the pctrace fallback gets a `watch_pcs`
param on `pctrace_per_play_capture`; F iff (frame-entry reached OR chip-state
advanced) — a true refresh reaches no frame entry and can never advance, so
no false F (round-53 lesson: detect the minority form positively, don't flip
the default). EXPOSURE: 25 stored R-token FULLs corpus-wide (Finn ×20,
Bakewell Toccata/Big_City, Quick_Tune_2, Demora, Use_Me) — all genuinely
tail-only wrappers, tokens unchanged, 3 rebuilt byte-identical; flip census
over all 236 current f1 partials = exactly 1 carrier (My_Rusty_Love → FULL
388489/388489 state ✓); 1 py65-None partial (Cow_Anus_Fucked_2SID) → pctrace
None both ways. Full tools/regression.py green. METHOD: the CIA flat pos-0
artifact again — localize per-IRQ; then segment the flat stream into
PER-VOICE BLOCKS (ctrl closes a block) and diff block SHAPES (has-AD/SR, n)
— it turned 386k writes into a one-glance `✓✓✗✓✗✗` phase pattern that named
the wrapper period immediately. f1 ≈ 5156 FULL / 245 partial.

## ✅ ROUND 56 (2026-07-08): OUT-OF-IMAGE loop sector = engine sonifies live ZEROPAGE — Killer_Beat +4 GENUINE partial → FULL (0 regr) [ledger C29 NEW]
Random f1 partial Mephisto/Killer_Beat (vblank, flat div 93464 = 77%). V1 plays
note47(B-3)/note55(G-4) where reb plays note0(C-0), then both re-sync on the
C-0 outro — a clean 2-note substitution deep in the song, notes ABSENT from any
V1 pattern. ROOT: V1's track (orderlist) ends with `$FF` (loop) at pos 39; the
byte after is `$A0`=160 (track_loop_target=True, CORRECT — memwatch confirms
orig otrk 39→160), and track pos 160 holds byte `$1A`=sector 26, whose pointer
`secp[26]` = **$0000** (a garbage sector# past the pointer table). The file
image is all-$00 below load ($1000), so the extract decoded 256×note-0; but at
RUNTIME the sector reads live ZEROPAGE via `LDA ($F8),y` with $F8/$F9=$0000 →
pc-trace ground truth `[0000]{2F}`(=note47), `[0001]{37}`(=note55) = the 6510
I/O port (DDR $2F / processor port $37, PSID env defaults), then static zp bytes
(note0, then `$67`=instr-7 prefix + `$1C`=note28 → the `$FF00` off-table region).
taint_source over 160s: only $F8/$F9 written during play, and those read $00
from V1's own $0000 sector ptr → the whole sonified outro is STATIC/reproducible.
FIX (ledger C29, extract-side): `_loops_offimage` gate (a $FF loop reaching a
sector `< load`) → capture runtime low-RAM via `_postinit_values(range(0x100))`
(libsidplayfp; py65 can't reproduce env zp = C9) → overlay onto `mem` before
`_walk_track`, with read-time corrections mem[$00/$01]=$2F/$37 (port, not the
RAM under it) + mem[$F8/$F9]=$00 (sector base). `_simulate_sector` decodes the
true endless outro; the off-table reach model auto-captures the new note28/
instr7 → $FF00. Killer_Beat FULL 121386/121386 (V1+V2 both loop $0000; V3
in-image). REGRESSION-SAFE BY CONSTRUCTION: overlay only changes the decode of
out-of-image sectors, which only affects the write-log if PLAYED — a played
out-of-image sector was always mis-decoded (image≠runtime) so its member was
non-FULL; unplayed decode = byte-identical (a no-OOB FULL builds identical MD5;
full tools/regression.py green 0-regr all 7 families). CENSUS (44 f1
STORED-partials carry the signature; the batch flipped 14 to FULL, but
re-baselining each vs the PARENT commit b81785e5 — amend Step 3.4 / ledger C20 —
gives **4 GENUINE partial → FULL**: Killer_Beat, Axel_Foley, Remix_1995, PVCF
Centric_tune_4_v8). The other 10 batch-FULLs (9× Flash [Illusion/Keepsake/
Last_Days/Mozart/Nice/Reallight/Shattered_Past/Together/Worm] + Wodnik Narwana)
were ALREADY FULL under parent — their stored 'partial' rows are stale
palimpsests predating round 55; my overlay is neutral for them (their
out-of-image sector is UNPLAYED in the verify window → byte-identical). 29 stay
partial (dynamic-zp / deeper blockers); 1 pre-existing error (Rayden
Leprechaun_Boot_V1_2SID = 2SID + 3 subtunes, to_usf merge single-subtune-only —
exonerated vs a parent build). This is the RE_NOTES bucket-8 "sector at $0000
never ends" class, now RESOLVED for the static-zp majority. LESSONS: (1) a deep
2-note substitution that re-syncs = a LOOP-target/sector-pointer bug — trace otrk
(memwatch) + pc-trace the actual `($F8),y` effective address; when it lands in
zeropage, the engine is sonifying the environment (taint-classify static vs
dynamic, read the runtime RAM not the file image). (2) C20 re-confirmed: the
stored jsonl before-status is NOT a baseline — re-verify each apparent flip vs a
FRESH PARENT-code build before counting (10 of the 14 were palimpsests).

## ✅ ROUND 55 (2026-07-08): HARD-RESTART PREP-CALL SKIP wedge — Seaside_99 +9 partial → FULL (0 regr) [ledger C19 7th occurrence]
Random f1 partial SilverFox/Seaside_99 (vblank, flat div 197). Per-IRQ diff
(Trap-C-free) of V3: at the note-FETCH frame (irq13) the rebuild emits an EXTRA
prep block `D412=08 (TEST) / D413=0F (AD) / D414=0F (SR)` that the orig LACKS;
the note-INIT frame (irq14: real ADSR + gate $81) is byte-identical. The
memwatch showed the orig's pending ($174C) going FF = hard-restart path TAKEN,
which contradicted "no prep" — so pc-trace was the ground truth: `$11DB = 2c fb
17 = BIT $17FB`, NOT the canon `20 fb 17 = JSR $17FB`. A 1-byte opcode patch
($20->$2C) neuters the WHOLE prep call: `BIT` reads $17FB but writes nothing, so
the fetch frame emits NO writes (sub_17FB's TEST $08 + AD/SR $0F0F all skipped),
while $11E3 still sets pending so the note inits normally next frame and the old
note rings through the fetch frame. A classic C19 hand-patched wedge, STATIC in
the file image (confirmed: body byte $11DB=$2C). DISTINCT from `hard_restart=
'none'` (family-2, which KEEPS the $08 TEST write) and the 5th-occurrence numeric
preset wedge (patches sub_17FB's immediate; call intact). FIX:
`factory._hr_prep_skip_probe` (STATIC opcode probe, reloc-aware base+offset;
verifies the shape both sides — LDA #$08, the $17FB operand = base+$7FB, LDA
#$FF) → the EXISTING `hard_restart` param, domain extended to a 4th value 'skip';
composer suppresses BOTH `hr_test_write` AND `hard_restart_adsr` in `ev_n_hard`
(also fixed the `int('skip')` crash by grouping 'skip' with 'none' in the ADSR
branch). CENSUS TRAP: some carriers ALSO patch sub_17FB's first byte $99->$60
(RTS) — irrelevant since the call is neutered, so the base-independent census
keys on the call-site opcode + the reloc-invariant `op - code_start == $622`,
NOT on sub_17FB's shape (my first census keyed on the sub_17FB `99/B9` and
false-negatived ALL carriers). Census over all 5401 f1: exactly 9 carriers
(Welcome_to_Egypt, Bayliss ×4, DaFunk ×2, SilverFox ×2), ALL partial (0 FULL
exposure) => regression-safe by construction; ALL 9 partial -> FULL (fresh
full-songlength verify). 0 f2 carriers. Also promoted the scratch build helper
to `tools/dmc_build_one.py` (build one member -> .sid + .usf, --verify /
--localize). LESSON (repeats round 50): when a derived value's memwatch/runtime
disagrees with "what should happen", pc-trace the ACTUAL executed opcode — the
canonical disassembly.s can be locally patched in a given member. f1 ≈ 5155
FULL / 246 partial.

## ✅ ROUND 54 (2026-07-08): FIRST-NOTE DURATION = post-init $173E (init CLEARS it to 0), not the _Sticky default 1 — +3 FULL, 0 regr [ledger C11 note]
Random f1 partial Harti/Klepkomania (vblank, flat div 53, sub3 only; 6/7 subs
already FULL). First-div chase (play-split of the flat write stream): at play 4
the orig emits V1's full block but the rebuild SKIPS V1 (jumps straight to V2) —
V1 goes inactive one play EARLY and its whole free-running PW-sweep phase shifts
vs V2/V3 forever (counts differ by exactly 5 = one V1 block; V1's own value
stream is byte-identical). ROOT CAUSE: sub3 V1 = a single decorative note (sector
= `[inst15][note C-7][$7F]`, NO `$80-$BF` duration command). The note-load reads
the duration RELOAD `$173E,x`; the engine's INIT clears `$1718-$179D` (which
SPANS `$173E-$1740`) to 0, so a first note reached before any duration command
plays for reload 0 (`$173B` DECs 0->$FF = a held 256-tick note). The extraction's
`_Sticky` seeded `dur=1` (default) -> too-short note -> hit the track `$FE`
terminator one play early -> the `$FE` handler RTSs (skips frame_entry that play)
one frame sooner than the orig. FIX (1 line, `_Sticky.__init__` default
`dur=1`->`0`): the note's reload before any sector duration command is the
post-init value, which is 0 for the whole DMC v4 engine (the `$1718-$179D` wipe).
py65 post-init(`$173E`)=0 for every subtune + empirical dur-sweep (dur=0/32/63
all FULL, dur=1/6 partial) both confirm the note holds. The durrel_init capture
comment "orig init never writes $173E" is FACTUALLY WRONG — init clears it; left
that (round-31 priming) untouched, changed only the sticky seed.

REGRESSION-SAFE BY CONSTRUCTION: a voice whose first sector event is preceded by
a duration command has `st.dur` OVERWRITTEN before the row -> BYTE-IDENTICAL
build (proven: FULL-side flip-set = **0 of 1200 random f1 FULLs change build**);
only a BARE first row (the decorative/degenerate case) changes, and 0 is exactly
the value the orig reads there. Evidence: partial flip-set 30/253 changed ->
re-verify = **+3 partial->FULL** (Klepkomania 7/7, Compod/Nocturno,
Wodnik/Narwana) + 26 first-div moved DEEPER (deeper blockers, honest progress) +
0 partial regressions; 1200-FULL flip-set 0 build changes; full
tools/regression.py GREEN (0 regressed all 7 families: Hubbard 71 / Companion 44
/ C64ME 15 / Jay_Derrett 17 / FC 31 / DMC 11 / Basic_Program 22).

TRAP (amend Step 2, cost ~1h): first tried seeding from `durrel_init` = the FILE
IMAGE (`$173E`=8) — WRONG (init clears it to 0), regressed another Klepkomania
subtune (V1 seed 8 too long). The file image, the default 1, AND the LIBSIDPLAYFP
memwatch runtime (`$173E`=6 during play — a py65/libsidplayfp divergence red
herring) all misled; only py65 POST-INIT + the empirical dur-sweep gave the true
value (0). LESSON (ledger C11 note): when a first-event parameter is read from
ENGINE STATE that INIT CLEARS, the extract's seed/default must be the POST-INIT
(cleared) value, not the file-image leftover (init overwrites it) and not a
hardcoded default. Localize on the write-stream + the PLAY-SPLIT view (which
play() drops the voice), NOT a memwatch of the reload register (Trap-C /
py65-divergence confused). f1 ≈ 5149 FULL (baseline stale — see project note).

## ✅ ROUND 53 (2026-07-08): RESET-ALL-VOICES loop hook classified loop-to-0 — Unfinished_1 +6 → FULL (0 regr) [ledger C13 new note]

Random f1 partial `MUSICIANS/B/Bakewell_Dwayne/Unfinished_1.sid` (CIA 2x,
`otrk_legacy`). Trichotomy first-div at play pos 140688 / 142224 (98.9%, in the
×1.1 loop-tail ~89s of an 82s song), state_match ✓: V1 SR orig `$F0` vs mine
`$F9` — a NOTE-FETCH divergence (orig plays a fresh idle note curnote=254/instr
0; reb keeps looping instr 3). The whole song + 7s of the loop matched exactly,
then the LOOP-BACK diverged.

Ground truth (`--memwatch-on-write D404 1726,1012,1015`): the orig's V1 otrk
($1726) trajectory is a clean periodic `1..20,21, 1..20,21, 1` — it **loops the
whole track back to entry 0** every pass. But extract had V1 `loop_to=20` with a
bogus entry 20 at byte offset **131**, from `track_loop_target=True` reading pos
21 (`FF`) + pos 22 (`82`=130) as a jump to byte 131. So the reb looped to entry
20 (a 256-row `note 0 inst 3` drone) forever; the orig replays from the top.

ROOT CAUSE — the loop hook is a THIRD form the classifier didn't know. Disasm:
the `$FF` handler is `$10D9: CMP #$FF / NOP NOP / JSR $1020 / JMP $10D2`, and
`$1020 = A9 00 8D 26 17 / A9 00 8D 27 17 / A9 00 8D 28 17` = **reset all 3
voices' track positions to 0** — a SYNCHRONIZED loop-to-start restart,
semantically `track_loop_target=False`. These members carry a code wedge so they
FAIL the canon masked-compare (`player_code_mismatch`) and build via the
**dataflow** path, whose rule `track_loop_target = loop_site is None` (canon STA
sig absent ⟹ assume the read-next JSR hook `INY/LDA($f8),y/STA $1726,x`)
mislabeled the reset-all hook as read-next=True → the walk read `$FF`+1 as a
loop-target jump. (The canon loop-hook probe is NOT the culprit — it never gets
there.)

THE TRAP I NEARLY LANDED (amend Step 3.2 — recorded so the next session doesn't
repeat it): the first fix flipped the DEFAULT — `True` only when a read-next
idiom (`c8 b1 f8 9d`) is scanned, else `False`. A census exposed that as the
SAME "not-A ⟹ B" mistake inverted: relocated read-next hooks use a DIFFERENT
track-pointer zp (`$58/$61/$68…` not `$f8`), so a fixed-`$f8` scan
false-NEGATIVEs them → a genuine read-next member regresses to loop-to-0.

CANONICAL FIX (dataflow-only, regression-safe as a THEOREM): keep the base rule
`loop_site is None` UNCHANGED — every read-next member keeps `True` regardless
of zp — and flip to `False` ONLY on a POSITIVE match of the exact reset-all
3-pair idiom (`A9 00 8D a / A9 00 8D a+1 / A9 00 8D a+2` to consecutive track-pos
addrs) in the reachable trace. That idiom has 0 occurrences in the canon player
and in all 848 read-next members, so the "changed" verdict has NO false positive.

CENSUS (static, all 5401 f1 + every other DMC v4 cluster): exactly **6** members
carry the 3-voice reset-all hook — all Bakewell (Goodbye, Feelin_Blue, Survival,
Toccata_v3, Techno_Inc_2, Unfinished_1) — **all 6 flip partial → FULL** on a
fresh full-songlength verify. Loop-hook form census over all f1: canon_sta 3443,
read_next 848 (all keep True), jsr_other 62, reset_all 6, no_base 1026. Family-2
(bypasses the loop probe via `_family2_build`) and v5 (separate pipeline): 0
carriers, unaffected. Full `tools/regression.py` GREEN (0 regressed all 7
families).

METHOD LESSON: a note-fetch divergence deep in the ×1.1 loop-tail (state ✓,
perfect prefix) is a LOOP-BACK bug — trace the runtime otrk/curnote trajectory
(`--memwatch-on-write D404 1726,1012,...`) over ≥2 passes to see the true loop
period, then read the orig's `$FF` handler (don't trust the extract's walked
`entry_offsets` when the runtime counter never reaches them). The
`otrk_legacy`/off-table-131 framing was a RED HERRING — the real bug was one
mis-probed variant flag.

## ✅ ROUND 52 (2026-07-08): DOUBLE-SPEED base+3 JMP wrapper — Scan_Collection_end +9 → FULL (+10, 0 regr) [ledger C24/play_repeat note]

Random f1 partial `MUSICIANS/L/Lio/Scan_Collection_end.sid` (vblank). The
batch row looked odd: `play_match == play_overlap == 215063` (a PERFECT
prefix) yet `len_post_a=429373` vs `len_post_b=215063` — orig's play stream is
~2× mine's over the SAME duration. Not a content divergence: counting writes
per frame gave orig ≈34, mine ≈17 in steady state, and a steady-frame dump
showed orig = **two full music updates back-to-back** (the PW sweep
`$D402/$D403` advances `$2F/$0C → $B8/$0B` between the two halves). It is a
DOUBLE-SPEED tune.

Root cause: the play VECTOR is `$1003: JMP $2000` (the `$1000` page is just
title text), and `$2000: JSR $1050 : JMP $1050` = the engine at `$1050` runs
**twice per play()** — the classic `_detect_play_repeat` "`JSR T; JMP T` =
n+1" wrapper. But the probe never reached that analysis: line-680
`if play == base+3: return 1` short-circuited (play=$1003=base+3) BEFORE
following the JMP. Note the canonical player ALSO has `$1003: JMP $1085`, but
`$1085` is the plain play body (`DEC $1718` speed-counter) — the wrapper loop
already follows a leading JMP once and returns 1 for a plain body; the
short-circuit merely skipped that walk.

FIX (one line): short-circuit only when `mem[base+3] != 0x4C` (base+3 is NOT a
JMP); otherwise fall through to the existing loop, which follows the leading
JMP once and detects the JSR-chain / JMP-tail wrapper (returns 2 here).
REGRESSION-SAFE BY CONSTRUCTION: canon `base+3 = JMP → DEC play body` still
returns 1 (byte-identical build); only a genuine `JSR T; JMP T` double-play
wrapper returns ≥2 — and any such member, built single-speed, was ALWAYS a
length partial (½ the writes), never a FULL, so no FULL can regress.

Census over all 5401 f1 members: exactly **10** satisfy `play==base+3 AND new
play_repeat≥2` (the other 27 `play_repeat≥2` members have `play≠base+3` and
already went through the loop) — Lio Happy_Night / Msxs / Scan_Collection_end,
Logan Black_Music, PRI Do_the_Note / Dreamland, The_Syndrom Double_Power /
Other_One / Saturday_Night / Savage_Remix. **All 10 flip partial → FULL** on a
fresh full-songlength verify. Full `tools/regression.py` green (0 regressed all
7 families); artifacts mass-written.

METHOD LESSON: a perfect play-stream PREFIX plus a clean ~2× length tail on a
VBLANK tune is whole-play double-speed, not a missing effect — localize by
counting writes/frame, then disassemble the play VECTOR and FOLLOW its JMP;
don't stop at `base+3`.

## ✅ ROUND 51 (2026-07-08): WJMP-CHASE SHADOW — High_Tech partial → FULL (+1, 0 regr) [ledger C11 new note]

Random f1 partial High_Tech (Dr_Piotr, vblank, flat div 32811, V3 freq-hi
orig $01 vs mine $00). First-div chase (memwatch + pc-trace ground truth):
the V3 note's base freq = an OFF-TABLE melodic read at idx 120 → freqhi[120]
= $171F, the shared `wjmp` scratch (round-31 class). All other inputs (accum,
slide, parity) matched; only `wjmp` diverged (orig $01, mine $00). Root cause:
`$171F` at that read = V1's wave marker-HOP distance ($91→$01), and V1 plays
**instrument 7 whose wave_start=137 sits ON its own end-marker $91** (the
"start at the loop marker" editor idiom). The orig, starting on the marker,
chases back 1 EVERY note-init (writing $171F=1); the composer packs the
SETTLED program (skips the transient chase) so it misses the note-init hop —
every subsequent frame it hops naturally, so the ONLY missed write is the
note-init one, and it only shows when a wjmp read lands on that frame before
another voice overwrites $171F (V2 idle that frame). FIX (CORE TENET — layout-
independent, reproduce the WRITE): extract `wave_start_on_marker` (own-end
marker + loop 0, gated on a wjmp read + canon geom) → USF per-instrument flag
→ composer re-asserts `wjmp = n` at note-init (`iwchase` table + `ni_chase`,
emitted only when some instrument chases). REGRESSION-SAFE BY CONSTRUCTION:
re-asserts a write the orig ALWAYS makes; observable only where orig diverged
(6 random FULLs + all portfolio byte-identical; full tools/regression.py green,
0 regressed all 7 families). Census: 4 f1 partial carriers — High_Tech FULL
297/297s exact; Chwat + Solar_Energy first-div resolved → deeper blocker (Lens
3); King_of_Earth's wjmp read diverges for a non-chase reason (honest residue).
METHOD REMINDER: for a global cross-voice scratch, memwatch the read value +
diff orig-vs-reb INPUTS (base/accum/slide/parity) at the same event index to
isolate which term diverges; a chasing instrument's phase leaks into another
voice's $171F read even when its own output is a constant 1-step loop.

## Status (2026-06-12)

**✅ Geometrical_Zaks FULL** — all 3 subtunes instruction-sequence exact
at full songlength ×1.1 (sub0 303565, sub1 266449, sub2 73661 play
writes; trichotomy Check A state ✓). First DMC member through the
SID → USF → SID pipeline. Wired into `tools/regression.py` (DMC
section). Verdict tool: `pipelines.dmc.verify.verify_dmc(cfg)`.

Pipeline: `pipelines/dmc/v4/extract/` (dataflow operand reader +
path-resolved pattern simulation) → USF → `pipelines/dmc/composer_asm.py`
(our own engine; own event encoding, parallel instrument arrays,
pre-split pulse nibble/base tables) → xa65 → PSID.

## The three write-log iterations that got Zaks FULL

1. **Idle-note voice_state priming.** A voice whose track opens with
   rests (Zaks V3) still runs the full effect chain; the original's
   wave-freq lookup reads the WORK-FILE LEFTOVER current-note bytes at
   $1012-$1014 (uncleared by init). Carried as
   `init { voice N { note: M } }` (engine-state priming, trichotomy
   §4.5). The leftover $1015-$1017 instrument bytes do NOT matter (the
   note-init CACHE is what the effects read, and init clears it to 0 —
   i.e. idle voices run instrument RECORD 0's pulse/wave mechanism).
   Extract therefore force-includes record 0 as USF slot 0.

2. **Idle pulse base separation.** The pulse step = table nibble +
   CACHED base ($175F). Idle voices have base 0 (cleared) but read
   record 0's nibbles — so the effective steps `(nib<<4)+base` cannot
   be pre-baked. USF carries effective `speed_steps`; the composer
   derives base = step & $0F (asserts all six share it) and the engine
   adds the cached base at runtime (0 while idling). Exact for both.

3. **xa65 gotchas** (composer-side): ':' acts as a statement separator
   even inside ';' comments (sanitizer strips them); branch-out-of-range
   at frame_entry; non-ASCII in comments is a syntax error.

## Family semantics the engine reproduces (see disassembly.s for all)

- 3-frame minimum gate ($1786 guard), then release_early instruments
  get the $FE gate mask; hold = gate-off + AD/SR=$00 at duration ctr 1;
  open = never.
- Hard-restart fetch frame writes ONLY ctrl=$08, AD=$0F, SR=$0F.
- Inactive ($FE'd) voices keep writing their 5 regs every frame.
- Dual effect: GLOBAL half-rate parity shared across voices; odd-frame
  freq = base+accum_lo (hi takes carry only, NOT accum_hi) − slide.
- Filter: single owner per frame (claim, X order); $D418 written only
  at init and at filter note-init (mode|vol).
- $D417 routing shadow primed from the file-image leftover ($1018,
  uncleared by the original init) = `init.sid.filter.res_routing`.

## Residue / uready accounting (open, not blocking Zaks)

- **Family rollout not started**: one member FULL. Factory
  (`dmc_v4_config(sid)` probing the 7 patched operands + wrapper-init
  members like On_My_Way_to_X / Retro_Tech) is the next phase, then
  the wide batch over family 1 (5401 SIDs).
- **Idle-state assumptions**: idle voices reproduce the original only
  when (a) USF slot 0 == original record 0 (extract enforces) and
  (b) record 0's wave_start == 0 (true for Zaks; factory must check —
  otherwise the idle wave walk starts elsewhere in the table).
- **Off-table reads not modeled**: wave-freq offset + note > 95 reads
  past the freq table (the original reads the adjacent table/state
  bytes — the FC freq_overrun analog); same for vibdepth with
  note+transpose > 95. Extract should assert; currently silent.
- **Gate-mask leftovers**: $100F-$1011 assumed 0 in the file image
  (true for Zaks; probe in the factory).
- **Aux entry points** (+$06 all-off, +$09 sfx-note, +$1D tune-select
  chaining semantics incl. the routing shadow surviving re-init) are
  not emitted — PSID playback never calls them.
- **V5/V6/V7 + family 2** (the 0.732 V4-derived variant, 2889 SIDs):
  separate work; V5 sector encoding still needs RE.
- **Ear test PASSED** (2026-06-12, user) on Geometrical_Zaks.

## ✅ ROUND 1 sub-build recovery (2026-06-14): 2945 -> 3135 FULL (+190)

The big `player_code_mismatch` buckets turned out to be EQUIVALENT-write
sub-builds or PSID-sub-entry variation — the family-1 sub-builds use the
SAME variant axes as DMC family 2. Fixed in `factory.py`:
- **$1181 (130): rest/switch/slide-tail JMP $1591 (skip effects)** vs
  canon JMP $1322 — the family-2 `rest_effects='skip'` behavior in
  family-1 members. Probe $1180 -> `cfg.extra_params['rest_effects']`.
- **$1631+$163E (136): all-off (+$06) / sfx (+$09) routines** vary per
  sub-build but are NEVER executed during play() (verify only drives the
  play vector). Masked $162F-$1647.
- **$12A8 (80): filter $D418 write via a JSR helper** (STA $D418 + a
  dead store) vs inline STA $D418 — identical write. Mask + validate.
- **IMAGE-WIDE jump-table scan** for relocated-within-file players (at
  neither play-3 nor load): +7 (most no_jumptable have NO jump table or
  a CIA-timer the py65 init probe can't read).
4 family-2 canaries + the v4 portfolio guard this in regress_dmc.
RESIDUE still open: remaining sub-build sites ($1231 = a real SR-compute
variant + different helper; $18B4; $1493; smaller), 364 no-jump-table
(no findable base), 35 cia_multispeed (timer unreadable), the off-table
architectural limit (~600, correctly refused).

## Wide-batch residue buckets (family 1 = 5401, ranked by size)

Each is its own next-round triage target. Sizes from the first full
sweep; the factory's typed reasons make these greppable in
`tmp/dmc_wide_results.jsonl`.

1. **Relocated 2-entry layout (~621, `player_code_mismatch` first
   diff at $1001).** A whole sub-build: 2-entry jump table
   (`$1000 JMP $1807` init / `$1003 JMP $1050` play) vs canonical's
   4-entry, with the body shifted (play body $1050 vs $1085, etc.) and
   vars starting $1006 not $100C. Same engine, different assembly —
   needs a second canonical reference binary + a layout-variant probe
   (FC reloc-factory analogue). HIGHEST-VALUE next target.
2. **Other code-mismatch sub-builds (~430): first diff at $1181 (101),
   $1631 (79), $12A8 (76), $163E (31), $1231 (24), $119B (22), ...**
   each a distinct patch/variant; triage by diffing the region against
   canonical.
3. **Second loop-hook variant (~162, `loop_site_unknown` site bytes
   `c8 20 4d` = INY/JSR $..4D).** Like the $1042 hook but a different
   helper address; generalize the loop probe to accept any JSR whose
   target matches the 7-byte hook signature, OR decode the hook to find
   the loop-target semantics. + smaller site variants (`8d 9d 17` 15,
   `7e 18 ea` 12, ...).
4. **nonstandard_vectors (~1184).** init/play not at $1000/$1003 —
   relocated members; needs the load-addr-relative operand probe
   (most are probably canonical code at a different base).
5. **dual_parity_leftover (486) — FIXED this session** (params.slide_phase).
6. **offtable_live (errors, ~200).** wave-freq offset or note>95 reads
   land on the LIVE state block ($1707+k for k≥17 or the track-ptr
   slots k≤5). Consistent sub-buckets k=[159] (18), k=[30] (18),
   k=[0] (14): worth checking whether $1707+k is a stable-zero byte
   that the composer window could extend to cover, vs genuinely live.
7. **wave n=0 (56) — FIXED this session** (marker-chain slice start).
8. **`sector at $0000 never ends` (9).** tune-pointer record reads a
   $0000 voice pointer — member declares more subtunes than it has
   data for, or the tunetab operand probe is off for these. Guard +
   investigate.
9. **partial (140).** factory-passing but writelog diverges — the true
   long tail; bucket by first_diff signature (carried in the jsonl).

## Documented residue — the dual-effect FREQ GENERATOR (Taurus_02, 2026-07-06)

**`dual_freq_generator` + `dual_gen_steps` params (renamed from
`dual_hack`/`dual_hack_steps`; ledger C19 4th occurrence, C7-(b)
document-and-minimize decision, user-ratified 2026-07-06).**

Taurus/Taurus_02.sid — the ONLY carrier in all 10,676 DMC members — byte-edits
the dual ($40) odd-parity path: the `LDA $172F,x` opcode is patched BD→A6
(`LDX $2F`; zp $2F=$A9 under the PSID environment), so every subsequent
per-voice `,x` read lands +$A9 past the state arrays onto fixed CODE bytes.
Net audible behaviour: ONE global free-running pseudo-random freq ramp on dual
frames (the "accumulator" self-modifies two tune-setup code bytes whose
file-image values seed it; the update ORs a BASIC ROM byte and rotates a
feedback byte via an illegal RRA) + fixed PW/ctrl from code bytes + a pwphase
clobber that drives the pulse-speed fetch off the instrument record.

Representation status (why this is residue, deliberately NOT schema):
- `factory._dual_freq_gen_probe` (static wedge-anchored regex) captures the 9
  write-determining constants → `dual_freq_generator` param; the composer
  emits the generator as CLEAN legal code (ror+adc = RRA; the BASIC-ROM bytes
  are environment constants, same category as zp $2F=$A9). Default
  byte-identical; verify FULL 86118/86118.
- `dual_gen_steps` = the static bytes the clobbered pulse fetch reads past the
  record (C2 class, same as offtable_freq but for pulse speeds). Derivability
  CHECKED and unavailable (inst-6 raws land past the table end in the wavectrl
  region, whose layout is not in USF for this member) → justified-minimal
  capture (2 entries).
- The "lift to a musical form" direction (e.g. a `law: random` enum) is a §8
  TRAP recorded in ledger C7: the enum value would not determine the write
  stream — the chaos generator would become hidden composer mechanism; putting
  its arithmetic in USF is Pole B. The param transcript is the maximally
  principled form for chaos content: all determining constants in USF, one
  fixed mechanism in the composer.

## Gate flags $10/$08 are INDEPENDENT editor toggles — `gate_open` (2026-07-08, ledger C30)

Instrument byte 10 bit 4 (HOLDING FX) and bit 3 (NO GATE FX) are independent
DMC editor toggles (TND tutorial), and the corpus carries instruments with
BOTH set (fx = $18 shape; Strain_2 has 2 used carriers). The engine tests
$10 first ($132D), so $08 is mechanically dead when $10 is set — audibly
$18 ≡ $10 — but the raw byte is cached in $177D,x and read AS DATA by the
off-table freq-hi lookup (idx 214-216 → the fxf redirect rows, round 39).
The old `gate_mode` 3-value enum was LOSSY over this pair: `iflags()`
rebuilt $10, the orig read $18, first-divergence at every off-table fxf read.

Fix: `EnvelopeConfig.gate_open: bool` (elidable, default False) carries the
co-set never-release flag alongside `gate_mode='hold'`; extract sets it from
`(fx & 0x18) == 0x18`; `iflags()` ORs bit 3 back. Regression-safe by
construction (the bit only reaches the stream via the fxf reads, where the
old build already diverged). Strain_2 partial → FULL 439569/439569.
