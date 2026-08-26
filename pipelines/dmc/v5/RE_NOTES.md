# DMC V5 — RE notes (Phase A complete)

## 🔎 2026-08-26 — THE RESIDUE, RE-CENSUSED PROPERLY: it is FREQUENCY VALUES

Everything below about a "$D418 lever" is superseded. A flat-stream shape
census over a 150-member stratified sample of the 702 partials
(`tmp/v5_shape_census2.py`, classified 150/150) says:

| bucket (shape of the first FLAT divergence) | share |
|---|---:|
| **VALUE** — right registers, right order, WRONG VALUE | **58%** |
| MISSING — orig writes registers we do not | 23% |
| MIXED | 15% |
| LENGTH — one stream just ends earlier | 3% |
| **REORDER (C16)** | **0%** |

Diverging register ROLE, orig side: **frequency dominates** — v1.freqlo 35,
v3.freqlo 29, v2.freqlo 15, v1.freqhi 13, v2.freqhi 7, v3.freqhi 5 = **104 of
150**. `fchi` 16. **`$D418` is 4.** Depth: median 3.7% into the song, and 50 of
150 diverge inside the FIRST 1%.

⇒ The v5 residue is a WRONG FREQUENCY VALUE, usually early — not a phase, not a
write-order, and not $D418. Two coherent sub-patterns inside the 57
VALUE+freq members:

  * **`delta=+1` — 14 members (25%)**: our freq-lo is EXACTLY ONE higher than
    the orig's. An off-by-one in an accumulator/rounding, not a wrong note.
  * **`mine==0` — 14 members (25%)**: we write $00 where the orig writes a real
    frequency — a note that never loaded, or an accumulator left clear.
  * remaining 19 are unrelated values (wrong note / wrong table entry).

### The `delta=+1` sub-class, mechanism identified (Bakewell/Illusions)

Worked example, first divergence at flat play position 74 (play ~4, so very
early) — the ONLY difference in the window is V1 freq lo, orig `$82` vs our
`$83`, with freq hi `$0F` on both:

    orig  0B=09 17=F4 14=89 13=00 12=09 16=5E 00=82 01=0F 02=00 03=05 04=41 07=00
    mine  0B=09 17=F4 14=89 13=00 12=09 16=5E 00=83 01=0F 02=00 03=05 04=41 07=00

Established:
  * The freq TABLE is not the problem — it round-trips through the USF with 0
    differing entries, and entry 46 is exactly `($0F,$82)`, the value the orig
    writes. We are writing table+1.
  * The mechanism IS already modelled. family-4's wave step is

        $1680  CLC
        $1681  ADC $1012,x     ; wavefreq + curnote — SETS THE CARRY if >= 256
        $1684  TAY
        $1685  LDA $1719,y     ; freqlo[y]
        $1688  ADC $1842,x     ; + frqbias, INHERITING that carry  <-- the +1
        $1691  ADC #$00        ; freqhi + carry

    and the composer's `wave_step_carry` block emits exactly this shape. The
    flag is a blanket family-4 default, and it IS set for this member.

⇒ So the carry differs because OUR INPUTS differ. For the table index to
coincide (same entry 46, same freq hi) while the carry differs, our
`wavefreq[step] + curnote` must exceed the orig's by exactly 256 — i.e. the two
sums agree mod 256 but not in magnitude. Some combination of our wave-step freq
offset and our `curnote` is wrong in a way the mod-256 index hides.

⛔ **REFUTED — DO NOT RE-RUN: "our wave program is one step ahead; defer the
note-init wave landing".** The reasoning was tempting and wrong. Watching the
ORIGINAL at the diverging write (`--memwatch-on-write D400 1012,1013,1014,
1842,1843,1844`) shows the orig itself writes `$82` then `$83` on consecutive
frames with `curnote=$33` and `frqbias=$00` throughout: `wavefreq+curnote =
$FB+$33 = $12E` >= 256, so the orig's `$83` IS the carry-propagated value one
step later. That reads as "we are one wave step ahead", and it agrees with the
separate observation that our note-load play lands freq where the orig's lands
AD/SR. Both point the same way — and the experiment still fails.

Tested directly (composer patched to `jmp ni_pulse` before the note-init wave
step, so the first step defers to the next play, then reverted):

    Illusions      partial, play_match 74     -> UNCHANGED (74)
    Just_for_Her   partial, play_match 11990  -> WORSE (57)

So the note-init wave landing is NOT the cause: Illusions' first divergence is
not produced by it at all, and family-4's canon behaviour really does land the
step at note-init. Two agreeing observations still did not make a cause — the
oracle (build it and compare) is what settled it, in ten minutes.

**NEXT MEASUREMENT:** watch both inputs at the diverging write, on BOTH sides —
`siddump --memwatch-on-write D400 <curnote $1012,x>` on the original, and the
same against our rebuild's label (get it from `assemble(..., return_labels=True)`;
v5 has no `state_addr` equivalent yet). That names which input is wrong in one
step. Do NOT infer it from the wave program alone: the index agrees mod 256, so
a static comparison of the decoded program will look correct.

⚠ **TWO CENSUSES BEFORE THIS ONE WERE ARTEFACTS. Do not repeat either.**
  1. The `flat_div` register census ("284 members emit an extra `$D418`") counts
     whichever registers align at the first differing POSITION; once any write is
     one slot out, the frequently-written `$D418` appears by construction.
  2. My own first shape census (`tmp/v5_shape_census.py`, KEPT as the worked
     example) compared the two captures PER PLAY — but a rebuild routinely has a
     different NUMBER of plays than the original (Confused_Again: 1946 vs 1962
     over 40s with byte-identical per-voice write totals), so play *k* on one
     side is not the same musical moment as play *k* on the other. It reported
     that member as "missing the whole v3 block at play 17"; its real first
     divergence is a `$D416` VALUE at flat position 48014. Trap C, plainly.
  THE VERDICT COMPARES THE FLAT CONCATENATION, SO THE CENSUS MUST TOO.

## 🔎 NEXT LEVER (2026-08-24) — 268 partials: we emit ONE $D418 TOO MANY

The single biggest partial cluster in v5, and it is now cleanly isolated
because `flat_div` finally records BOTH registers.

**Fresh batch (2,031 roster members): 1,181 FULL / 693 partial.** Of the 693:

| | members |
|---|---:|
| STREAM OUT OF STEP (orig reg != our reg) | **291 (42%)** |
| ...of which family-4 | **273 (94%)** |
| ...where OUR register is `$D418` | **268** |
| same-register (a genuine value bug) | 402 |

So on family-4 we emit a `$D418` where the orig emits a voice register — one
EXTRA write per frame — and everything after is out of step. Worked example
(Angee/Just_for_Her, first divergence 11990):

    orig frame:  V1blk  18=3F  V2blk  18=3F  V3blk  16=54     (18 writes, 2x D418)
    mine frame:  18=3F  V1blk  18=3F  V2blk  18=3F  V3blk 16   (19 writes, 3x D418)

**WHAT IS KNOWN.** The count is not fixed: profiling the ORIG at frame 690
shows THREE `$D418` stores, all from `$1651`, while the diverging frame 685 has
two. So the orig skips the per-voice `$D418` on some frames, and the skip is
the vib-REVERSAL bypass — the only paths that reach the voice step without
passing `$1651`:

    $15C9  JMP $1654   ; UP reversal, $1812 != 0
    $15DA  JMP $1654   ; UP reversal, $1812 == 0   -> UP ALWAYS skips
    $160F  JMP $1654   ; DOWN reversal, $1812 != 0 ; $15FE BEQ $1612 writes when == 0

The composer models the UP reversal only (`d418_skip_vib_reversal` sets
`vibrev` on the `inc vibdir,x` path).

**WHAT IS REFUTED — do not re-run this.** The obvious completion (set `vibrev`
on the DOWN reversal too, gated on step-doubling `$1812 = instr byte7 >> 4`,
which the extract currently MASKS OFF as `vib_width = b[7] & 0x07`) does NOT
explain the population. Measured over 200 members per group
(`tmp/v5_vibdbl_probe.py`): a vib instrument with `byte7 >> 4 != 0` appears in
only **5.5%** of the out-of-step members versus **19%** of the same-register
partials and **10%** of currently-FULL members — i.e. it is LESS common in the
affected group. Some other condition is skipping the write.

### ⚠ 2026-08-25 — THREE CORRECTIONS TO THE ABOVE, all measured

Do not act on the "vib reversal" framing as written; two of its load-bearing
claims are false, and the third (the counting model) does not fit the data.

**1. "The only paths bypassing `$1651` are `$15C9`/`$15DA`/`$160F`" IS WRONG.**
`$1651 STA $D418` sits in the fade block's common tail at `$1612`, and FOUR more
sites jump over it straight to the wave step — all in the GLIDE region that runs
BEFORE vibrato:

    $1528  JMP $1654   ; glide UP step   ($183C/$183F += $17F7,x)
    $1555  JMP $1654   ; glide DOWN step ($183C/$183F -= $17F7,x)
    $1569  JMP $1654   ; glide ARRIVAL   (curnote = target, clear accum+speed)
    $1579  JMP $1654   ; accumulator clear, gated on $17F4,x != 0  ($156C)

The dispatch is `$14EE LDA $17F7,x / BNE $14F6` (glide active -> glide paths) /
`$14F3 JMP $156C` (no glide -> $17F4 test -> vib). So ANY voice running a glide
skips its `$D418`, which is far more common than a vib reversal — and that alone
explains why the static `byte7>>4` census came out at 5.5%: it was censusing the
wrong mechanism.

**2. THE WORKED EXAMPLE CANNOT BE A VIB CASE AT ALL.** On Angee/Just_for_Her,
`--memwatch-on-write D418` over the whole run shows `$1809` (vib period),
`$1806` (delay), `$1836` (direction) and `$1812` (step increment) are **$00 for
all three voices in all 1,728 sampled events** — vibrato never executes on this
member, so every vib-concerned path reaches the fade via `$1581`. Any hypothesis
tested on this member must not involve the vib reversal.
NB `$1812,x = (instr byte & $F0) >> 3` (`$13A2-$13AA`), i.e. nonzero exactly
when `byte7>>4 != 0` — so the refuted static census did test the right BYTE, just
for the wrong mechanism.

**3. THE COUNTING MODEL IS WRONG: `$D418` IS NOT ONE-PER-VOICE.** Predicting
`d418_per_frame == 3 - (glide_active OR $17F4 != 0)` holds for 510 of 626 frames
and FAILS for 116 — including frames with only 1-2 writes where every skip
condition is zero, and **one frame with FOUR writes against three voices**. More
writes than voices means `$D418` is also emitted outside the per-voice fade tail
(canon's `note_init2` writes `$D418 = vol|filtmode` at note start). So the true
per-frame count is (voices reaching the fade tail) + (note-inits this frame),
and the frames with too FEW writes are probably voices that never ran effects at
all, not voices that took a bypass.

### ✅ 2026-08-25 (cont.) — THE ATTRIBUTION WAS RUN. It is the NOTE-INIT frame.

`effect_chain_profiler --register D418` over Just_for_Her plays 600-700:

  * **EVERY `$D418` write comes from `$1651`** — the per-voice fade tail. So on
    family-4, unlike canon, `note_init2` does NOT write `$D418` at all. There is
    exactly ONE producer, which kills correction 3's "note-init also writes it".
  * A play emits **3 writes or 0**, never 1 or 2, across the whole window (75
    plays with 3, 17 with 0). ⚠ MY OWN EARLIER COUNTS (1/2/4 per frame) WERE A
    TRAP-C ARTIFACT: `--memwatch` reports per SIDDUMP FRAME, which holds 0, 1 or
    2 play() calls. Count per PLAY invocation, never per frame.
  * The 0-write plays line up with NOTE STARTS: p609 writes ctrl `$09,$09,$09`
    (all three voices note-on) and emits no `$D418`; p610, the follow-up play,
    likewise. A voice that starts a note runs `note_init2` and never reaches the
    fade block, so it emits no `$D418`.

**PREDICTION `d418 == 3 - (voices starting a note)` holds for 77 of 92 plays.**
Residue: a third zero-play at a fixed offset in each 12-play cycle (603, 615,
627, ... — normal ctrl writes, no `$09`, yet no `$D418`). That is the remaining
unknown; it is periodic with the tempo, so suspect the family-4 `DEC $1016`
MAIN/TICK toggle or the duration-counter path rather than an effect.

⇒ (The note-init observation about the ORIGINAL is correct and worth keeping.
But see the next section: our composer ALREADY reproduces it, so it is not the
bug.)

### ⛔ 2026-08-26 — IT IS NOT AN EXTRA `$D418` AT ALL. IT IS WRITE ORDER (C16).

The "we emit ONE `$D418` too many" framing — which has driven this lever since
2026-08-24 — is WRONG, and so was my own note-init conclusion above. Two
measurements kill it:

  * **Our `$D418` emission already matches the original exactly.** Comparing the
    per-PLAY `$D418` counts of the ORIG against OUR REBUILD of Just_for_Her over
    plays 560-700: **102 plays compared, 0 differing** — same plays emit 3, same
    plays emit 0. The composer's `noteload_no_d418` + `d418_skip_vib_reversal`
    already reproduce the note-init and reversal skips.
  * **The first divergence is a SWAP, not an insertion.** `build_one --localize`
    at flat play position 11990:

        orig  0E=00 0F=F0 10=00 11=02 12=81 16=54  00=95 01=20 02=20 03=08 04=41  18=3F
        mine  0E=00 0F=F0 10=00 11=02 12=81 16=54  18=3F  00=95 01=20 02=20 03=08 04=41

    Identical writes; the orig puts `$D418` AFTER V1's register block and we put
    it BEFORE. One position apart.

⇒ THIS IS LEDGER **C16** (per-frame SID write-ORDER differs), whose canonical
answer is to PARAMETRIZE the composer's EMISSION order — explicitly NOT to
rewrite the player, and NOT to chase a missing effect. Precedent: FC's
`nextvoice_write_order`.

⚠ AND THE CENSUS THAT NAMED THIS LEVER IS AN ARTEFACT. "678 of 702 partials are
out-of-step, 284 with our register = `$D418`" counts `flat_div`, which reports
whichever registers happen to align at the first differing POSITION. Once any
write is one slot out, every later position misaligns and the frequently-written
`$D418` shows up by construction. The 284 is not 284 members with a `$D418` bug.
Re-cluster this class by the SHAPE of the divergence (swap vs insert vs delete —
compare the two windows as multisets) before sizing it again.

### ⇒ 2026-08-26 (final, per-IRQ trace) — IT IS A MISSING NOTE-LOAD PLAY (C18/C23)

Tracing the literal per-PLAY register sequence around the flip settles it, and
it is not a `$D418` knob either. `writelog_per_irq_capture`, plays 681-686:

    orig p681:  18 06 00 01 02 03 04 18 0D 07 08 09 0A 0B 18 14 0E 0F 10 11 12 16
    mine p681:  18    00 01 02 03 04 18    07 08 09 0A 0B 18    0E 0F 10 11 12 16
    orig p682:  06 05 04 0D 0C 0B 17 14 13 12 16
    mine p682:  00 01 02 03 04 07 08 09 0A 0B 0E 0F 10 11 12 16
    orig p683:  00 01 02 03 04 07 08 09 0A 0B 0E 0F 10 11 12 16
    mine p683:  18 00 01 02 03 04 18 07 08 09 0A 0B 18 0E 0F 10 11 12 16

Two facts:
  * At p681 the orig writes the SR registers (`06`/`0D`/`14`) that we omit —
    the hard-restart prep.
  * At p682 the orig runs a play whose whole shape is SR/AD/CTRL per voice plus
    `$D417`/`$D416` and NO `$D418` — family-4's NOTE-LOAD (TICK) play, exactly
    the shape `noteload_no_d418`'s comment describes. We emit an ordinary
    effects play there instead.

So the original has a play WE DO NOT PRODUCE. From p683 on our stream is one
play out of phase, and every later flat position misaligns — which is where the
"extra `$D418`" and the "swap" both come from. Both were symptoms.

⇒ This is the C18 / C23 family (per-call play phases and the per-member
note-init/deferred ambiguity), NOT C16 and NOT a `$D418` effect. The machinery
already exists: `play_phases` tokens plus the C23 discipline of classifying the
per-IRQ write FOOTPRINT all-or-nothing per member. The next step is to classify
family-4's per-play footprints into {full play, note-load play} and check whether
the composer's phase schedule can express the note-load play as its own token.

⚠ Read C18 and C23 in FULL before starting — C23's own entry warns that a
high-multispeed member's per-IRQ capture can MERGE two play()s into one bucket,
which is exactly the kind of artefact that would corrupt this classification.

**SUPERSEDED — the attribution below has now been done; kept for its method.**
Use per-PC attribution:
`tools/effect_chain_profiler.py hvsc85/MUSICIANS/A/Angee/Just_for_Her.sid
--subtune 1 --register D418 --frames 680-695` to tag every `$D418` with the PC
that wrote it ($1651 fade tail vs the note-init store), then for the frames that
come up short, establish which voices ran `run_effects` at all. Only then choose
the composer condition. (The measurement below was the previous plan and is
superseded — it samples vib state, which this member does not use.)

**SUPERSEDED MEASUREMENT** (kept so it is not re-run): on Just_for_Her at the
diverging frame, find WHICH voice the orig skipped and why —
`siddump --memwatch-on-write D418 <vibctr,vibdir,vibspd,$1812 for x=0..2>`
(resolve the addresses with the member's base) and compare the three voices at
frames 684/685 against frame 690 where all three wrote. That names the
condition directly instead of inferring it from the disassembly's branch
structure. NB `$1812,x` is a per-voice RUNTIME cell, not the instrument byte —
the instrument byte only seeds it, which is one reason the static census above
can be misleading.

## ✅ 2026-08-24 (overnight) — the `$90` marker is followed EXACTLY ONCE

`capture_loop` refused 47 members. It is a `_WALK_CAP` seatbelt for a `$90`
chain that cycles without landing on a captured phase — and the first guess
(unused instrument slots holding garbage) was REFUTED by measurement: 46 of the
47 reach the offending program from a played instrument.

The real cause is that `_capture_env` / `_capture_env_f4` CHASED `$90` chains
(`pos = tgt; continue`), while the engine follows one marker and then uses the
target cell as a VALUE. Canon v5 `filter_run_v3`:

    $14A0  CMP #$90
    $14A2  BNE $14AE          ; not a marker -> use it
    $14A4  LDA $19C7,y        ; target
    $14A7  STA $17F9          ; new filterpos
    $14AA  TAY
    $14AB  LDA $19C6,y        ; re-read AT THE TARGET
    $14AE  STA $101F          ; ...and USE it. No second check.

family-4's pulse/filter handler ($14B4) has the same shape. So a target that is
itself `$90` is a literal ADD value, not another jump.

⚠ THE WAVE WALKER ALREADY KNEW THIS. `_slice_wave` documents both engine facts
("wave_step resolves a $90 marker by re-reading at the redirect target WITHOUT
a second check — a marker pointing at another marker plays the second one's
bytes raw"). Only the pulse/filter walkers chased chains, so this fix CONVERGES
the three on one documented rule rather than inventing a fourth reading.

MEASURED — exact exposure set (build all 2,151 before/after, MD5, verify the
delta): 66 members changed, of which **30 newly build** and 33 changed bytes
(13 of them previously FULL). Verdict: **7 new FULL · 0 REGRESSED · 23
unsupported/error -> partial**. 3 members moved into the (deferred) table-
overflow bucket because the corrected decode makes their programs slightly
longer — backlog item 19. Smoke 6/6, corpus 12,595/12,595, regression green.

⚠ ALSO FIXED, and it invalidates earlier clustering: the batch's `flat_div`
recorded ORIG's register with MINE's VALUE and no mine-register, so a row could
not distinguish "wrong value at this register" from "the streams are out of
step". That is why partial clusters read as e.g. "V1 freqlo mine=$3F" — we were
emitting `$D418=$3F` where the orig emitted a note. Both DMC batches now append
mine's register as a 6th element, and `divergence_census` clusters those
separately (`[STREAM OUT OF STEP]`) and prints a NOTE when reading pre-fix rows.
The v5 RE_NOTES had flagged this in the morning ("fix the batch's field before
clustering on it again"); it is now fixed.

## ✅ 2026-08-23 (later) — family-4's LEAD-IN OFF-TABLE FREQ (ledger C6)

Three bugs in one capture, worked example + measurements in
[`../family4/RE_NOTES.md`](../family4/RE_NOTES.md) (2026-08-23 section). In
short: `_assign_offtable_freq` ran BEFORE the family-4 block that re-points
`lo_notes` from canon `$100F` to the variant's `$1012`, so the lead-in capture
enumerated decoy bytes that indexed in-table and every family-4 lead-in
off-table read was silently dropped; the block was additionally gated on
`any(lo_notes)`, which skips members idling at note `$00` even though the idle
program's own step offsets run off-table; and the captured value was the
file-image byte where the engine reads a POST-INIT (init-zeroed) one.

Gate = build all 2,151 members before/after and MD5-compare, then verify only
the changed set: **167 changed, ALL family-4, ZERO canon**; deeper 11 ·
shallower 0 · **regressed 0** · new FULL 0. Lead-in bucket (1-63) 29 → 18.
An UNBLOCKING lever — score it by depth, not full/partial (ledger C5).

⚠ **TWO METHOD TRAPS THIS ROUND, both cost real time:**

* **THE BATCH ROWS WERE STALE AND I CLUSTERED ON THEM ANYWAY.** `dmc_v5_r2`
  ran at 00:42; FIVE substantive commits landed after it (08:52-12:43),
  including the C18 phase port (+9 FULL) and the family-4 CIA/phase defaulting
  fix (37 members). The "1,167/2,151" headline and every partial row predate
  them. A census built on those rows produced a confident, wrong picture — a
  "324-member $D418 class" that dissolved on measurement. Ledger C20: coverage
  is a FRESH batch. **Check the results file's mtime against `git log` before
  clustering anything.**
* **The first shallow carrier I picked was a SINGLETON.** Vextacy's per-voice
  `JSR` sites are repointed at a 6-byte `JSR $1373 / JMP $1373` stub = the
  voice unit runs TWICE per play (a clean ledger C24 unit-repeat, and the
  divergence is legible at position 7). A static census of the call sites over
  all 642 family-4 members found **638 canon, 1 carrier (Vextacy), 3 with a
  non-JSR site** — so it is worth almost nothing as a lever. Censusing the
  carriers BEFORE building the fix (C19's rule) is what stopped it.
  `tmp/f4_unitrepeat_census.py` is the probe if anyone wants those 4.

## 🔎 NEXT LEVER (2026-08-23) — the CANON shallow $D418 cluster is a TICK-PHASE bug

After the family-4 startup lever (see `pipelines/dmc/family4/RE_NOTES.md`), the
post-fix batch is **1,167/2,151 FULL**. Residue split by player branch:

| branch | partials | dominant first divergence |
|---|---:|---|
| family-4 | 466 (69%) | voice FREQ-LO, deep (55 @10k+, 46 @1k-10k) |
| canon f3/f5 | 207 | freq-hi deep (52 @10k+) + **a shallow $D418 cluster (26)** |

**THE SHALLOW CANON CLUSTER — 26 members, first divergence at play position 0.**
⚠ Its `flat_div` reads `orig=$1F mine=$A9/$AD/$E4/…`, which looks like we are
writing 6502 OPCODES to $D418. We are not: the batch's `flat_div` records
ORIG's register with MINE's value. The honest per-IRQ diagnosis
(`pipelines/dmc/v5/build_one.py --localize`) shows the truth —
`fpd=[0, [24,31], [6,169]]`: orig writes `$D418=$1F`, we write `$D406=$A9`.
Fix the batch's field before clustering on it again.

**WHAT IT ACTUALLY IS** (Astovel/Cyber_Brain, CIA `$0F5A` = 5 plays/frame):

    orig play3:  18=1F 06=00 00=4B 01=3F 02=00 03=00 04=00 | (x3 voices)
    mine play3:  06=A9 05=00 04=09 00=00 01=00 0D=A9 ...

The orig's first real frames are PREP frames — per voice `$D418`, `SR=$00`,
`ctrl=$00` — and the note-init lands LATER. Ours goes straight to the
note-init (instrument SR `$A9`, ctrl `$09`). We are ONE TICK AHEAD, exactly the
family-4 failure on the canon branch. It also explains the second symptom: our
filtmode reaches `$30` (so `$D418=$3F`) a frame before the orig, which is still
at `$10`/`$1F`.

**GROUND TRUTH, measured** (`siddump --memwatch-on-write D418 1012,1013,1015`):

    after init:   $1012 (speed reload) = $00   <- the record's speed, NOT the
                                                  image's stale $01; the
                                                  extract's speed=0 is CORRECT
    $1013 (spdctr) = $01 for ~12 consecutive $D418 writes (~4 plays), THEN $00
    $1015 (filtmode) = $10 -> $30 at the real note-init

⚠ **THAT LAST LINE IS THE OPEN QUESTION.** Our model of canon play is
`DEC $1013 / BPL / reload from $1012`, which from a leftover of 1 reaches 0
after ONE play and stays there. The orig holds `$1013 = $01` across ~4 plays.
So on this member the play routine is NOT decrementing every call — the
strong suspicion is a play-vector WRAPPER (ledger C18 phase schedule) that
CIA-multispeed canon members carry and we do not model, which would also
explain the orig's per-frame `$D418` count pattern `[3,3,3,3,0]`.

**CONFIRMED — IT IS A LEDGER C18 PLAY-VECTOR WRAPPER, AND V5 HAS NO PHASE
SUPPORT AT ALL.** Cyber_Brain's PSID play vector is `$2317`, NOT the jump
table, and it is an SMC counter living in an `LDX #imm` OPERAND:

    $2317: CE 1B 23   DEC $231B      ; $231B IS the LDX operand below
    $231A: A2 00      LDX #$00       ; loads the counter; Z set iff it hit 0
    $231C: D0 08      BNE $2326
    $231E: A2 05      LDX #$05       ; reload
    $2320: 8E 1B 23   STX $231B
    $2323: 4C 03 10   JMP $1003      ; FULL play (canon $10A1)
    $2326: 4C 06 10   JMP $1006      ; EFFECTS-ONLY pass

`$1006` is a THIRD jump-table entry (canon f3/f5 has only two) pointing at an
appended routine that runs canon `run_effects` ($1332) per voice, gated by a
per-voice table indexed by a counter — a per-voice phase schedule. The member
also has a re-implemented init at `$2269` (ledger C13: variant dispatch, canon
play body). With CIA `$0F5A` = 5 plays/frame and reload 5, exactly ONE full
play lands per PAL frame and four are effects-only.

⇒ THIS RESOLVES THE OPEN QUESTION ABOVE: `$1013` holds `$01` across ~4 plays
because it is DEC'd only inside the FULL play, which runs once in five.

**SCOPE — 48 carriers, ZERO of them FULL** (34 partial, 13 unsupported, 1
error). Wrapper shapes vary exactly as the C18 card warns:

| shape | example |
|---|---|
| SMC counter in an `LDX #imm` operand | Astovel/Cyber_Brain (reload 5) |
| `INC / AND #$03 / BNE` modulo gate | Glover/Plus_60k_Scheme |
| `INC / CMP #$04 / BNE` + SMC store | Lemmie_Eat_the_Rastertime |
| per-call CIA-LATCH SWING from a table (`STA $DC05`) | Arkanoid — also ledger C9 8th occ |
| bare `JMP $1003` trampoline (no phase) | Bayliss/Last_Amazon_2 — NOT this class |

⚠ EVERY carrier runs an effects-only pass on the non-full calls — there is no
"pure rate divider" sub-case. That matters because a pure divider would have
had a cheap fix (just divide the measured CIA rate); this class does not, and
the measured `cia_period` counts ALL IRQs including the effects-only ones.

**✅ PORTED 2026-08-23.** `_observe_play_phases` (factory) + `_apply_play_phases`
(composer), threaded model -> USF `params.play_phases` -> from_usf. Token
vocabulary is v4's exactly, so both families speak one language.

MEASURED over the 34 buildable carriers + 40 currently-FULL members:

| depth | before | after |
|---|---:|---:|
| position 0 | 17 | 3 |
| 1-63 | 16 | 8 |
| 64-999 | 0 | 2 |
| 1k-10k | 0 | 2 |
| 10k+ | 1 | 10 |
| **FULL** | **0** | **9** |

deeper 13 · shallower 0 · **regressed 0** · regression sample 40/40 still FULL.
Full pipeline regression GREEN (387 tasks, 0 regressed anywhere).
Schedules seen: `P_F123_F123_F123` (6), `P_F123`×5 (6), `P_F123`×4 (5),
`P_F123` (3), `P_F123_F123` (2), `P_F12_F12_F12` (1).

⚠ **AND IT SURFACED A LEDGER C9 DEFAULTING BUG.** `_family4_config` is a SECOND
constructor and it measured NEITHER the CIA latch NOR the phase schedule — so
every family-4 member carrying the PSID speed bit had been built as VBLANK:
**37 members, of which ZERO were FULL**. C9's recorded cure applies verbatim
("fix the CONSTRUCTOR, not the knob"); both are now measured there.
Lame_as_Rambo went from `cia=$0000` to `cia=$2663, phases='P_F123'`.

RESIDUE ON THIS CLASS: 3 still at position 0 and 8 in 1-63 — the leading-frame
shape differs (the orig's effects pass is GATED per voice by its own table, so
its first F calls emit nothing while ours emit 21 writes). That is invisible to
the flat verdict (empty frames contribute nothing), so it is not what blocks
them; the deeper ones are ordinary content bugs, e.g. Cyber_Brain now diverges
at 3,503/581,300 on V2 freq-hi.


Rep: `DEMOS/G-L/Katusha.sid` (family-3, 1461 + family-5 sibling 34 = the
dominant V5 player). Phase A (full disassembly + annotation) DONE
2026-06-14 → `pipelines/dmc/v5/disassembly.s`. Scope + plan in
`pipelines/dmc/v5/SCOPE.md`; format research in
`pipelines/dmc/docs/dmc_v5_{format_notes,docs_original}.md` +
`dmc_sector_commands.md`.

## ✅ Resolved in Phase A (all in disassembly.s header)

- **Sector command byte map** (the flagged unknown): notes `<$80`;
  commands `$F1-$FE` (SRR/ADR/VOL/gate×2/FD-/FD+/FRQ/FLT/SLD/GLD/SND/DUR/
  GATE) + `$FF` END. Track (orderlist): `$FC/$FD` transpose, `$FE`
  voice-end, `$FF pp` loop.
- **8-byte instrument** order confirmed from runtime: AD, SR, WV, PU, FL,
  vib-delay, vib-speed, vib-width(&$07).
- **3 programmable 2-byte tables** (wave/pulse/filter), `$90`=loop;
  filter is **voice-3 only** (`CPX #$02` @ $1496). Vib step = base-note
  freq << width. Full 11-bit filter cutoff ($D415 lo + $D416 hi).
- **Per-voice write order** (sid_write $16E6): freq lo/hi, PW lo/hi, ctrl
  (AND gate mask). Global $D415/$D416 once per play; $D418 in fade;
  $D417 at FLT cmd. Hard restart via gate-mask $F6 + SR=0 (gate_logic).

## Phase B (extract) — operand sites for dataflow

The packer places the data tables per song (like V4 — these addresses
are operand-patched; Katusha's values are the disassembly's). The extract
reads the base of each table by dataflow from these CODE sites (operand
lo-byte address = the listed PC + 1):

| table | Katusha addr | read sites (PC) |
|---|---|---|
| orderlist ptr | $1878 | $1046, $1059 (init) |
| sector ptr lo/hi | $196E / $1972 | $114E / $1153 |
| instrument | $1976 | $12CB/$12CF (note_on), $134F.. (note_init2) |
| freq lo/hi | $170F / $176F | $13A5/$13AB, $168C/$1692, $153B/$1541 |
| wave ctrl/freq | $199E / $19AB | $1385/$165E, $19AB reads alongside |
| pulse lo/hi | $19B8 / $19BF | $13C0/$13C9, $143C/$1450 |
| filter lo/hi | $19C6 / $19C7 | $13EF/$13F5, $149D/$14B1 |

NB confirm whether WV/PU/FL instrument pointers are entry indices or
need ×2 — the player uses them as ENTRY indices into the 2-byte tables
(reads `$199E,y` / `$19AB,y` with y = the pointer, not ×2). So pointers
are entry indices; the table arrays are split lo/hi (parallel), not
interleaved 2-byte records.

## Phase B/C open items

1. Packed memory map for ARBITRARY members (Katusha's table addresses are
   operand-patched — generalize via the dataflow sites above; build a
   `dmc_v5_config` factory like V4/family-2).
2. USF schema: the 3 programmable tables (content-by-reference), fade
   (FD+/-), ADR/SRR live register-sets, full filter cutoff, vib-step=
   freq<<width. Reuse `_offtable_check` pattern.
3. NEW V5 composer (the V4 composer does NOT apply). Write-log-first on
   Katusha. Verdict: `verify_dmc` (engine-neutral, reuse as-is).
4. **family-4 branch (686, Jupiter41, play +$95):** distinct (~0.31
   Jaccard) — diff its disasm against family-3's once family-3 is FULL.

## ✅ Phase B (extract) — DONE + validated (2026-06-14)

`pipelines/dmc/v5/config.py` (DMCV5Config, the operand sites above) +
`extract/engine_model.py` (`extract(cfg) -> V5Model`). Lifts Katusha to
a complete structured model — freq tables, 5 instruments (8-byte),
wave(13)/pulse(7)/filter(1) tables, speed/mastervol, 3 orderlists (with
loop), 4 sectors decoded into event streams. Region sizes from address
deltas (instr|wave_ctrl|wave_freq|pulse_lo|pulse_hi|filter_lo|filter_hi).
The sector-command decode (Phase-A byte map) is implemented + validated:
sectors lift to sensible `dur/snd/note/gate/...` event streams.

Validated on Katusha:
  sector 0: dur 04, snd 00, a note+gate melody
  sector 1/2: dur 02, snd 01/02 fast arps
  sector 3: dur 04, snd 03 melody with rests

## ✅✅ Phase C (composer) — Katusha FULL (2026-06-14)

`pipelines/dmc/v5/composer_v5.py` — a clean re-authored V5 engine
(labeled routines + relabeled state block) driven by the extracted song
data (orderlists/sectors/instruments/freq/tables emitted via labels;
index-based, relocatable). Katusha verifies instruction-sequence exact
at full songlength (trichotomy is_full + state_match, 97955/97955 play
writes; find_first_divergence 98880/98880 = 100%).

The write-log loop (key fixes, each via find_first_divergence + py65):
1. init clears state BEFORE loading track pointers (was wiping them).
2. prime file-image leftovers $1015/$1016/$1017 (filtmode/cutoff).
3. voice tick decs durctr every tick (removed an extra guard).
4. step_commit (gate-off/slide/tied-note) falls through to wave_step +
   writes the steady frame (note_on instead rts's — note_init2 next).
5. pulse_run ALWAYS advances — PU=0 = "no restart", NOT "no run" (the
   running-pulse-program semantics). This was the last fix to 100%.

NOTE — composer keeps the V5 state at the original absolute addresses +
data via labels; it's a faithful clean re-author (the per-frame logic
must match to match the write stream). NOT yet through USF (prototype
extract->model->composer); the USF layer + schema co-design is a
follow-up (the model IS the musical content, so serialization is
mechanical).

## ✅✅ USF layer — DONE (2026-06-14): Katusha FULL through USF

Pipeline is now `extract -> to_usf -> UsfFile -> from_usf -> V5Model ->
build_v5_sid` (composer UNCHANGED — model-driven). Katusha verifies
instruction-sequence exact THROUGH USF (trichotomy is_full + state_match,
97955/97955 play; find_first_divergence 98880/98880 = 100%). Verdict:
`pipelines/dmc/v5/verify_v5.py:verify_v5` (build_from_cfg goes through a
real .usf file). Test: `tests/test_dmc_v5_usf.py`.

Files: `extract/to_usf.py` (model_to_usf + write_v5_usf), `from_usf.py`
(usf_to_model), `verify_v5.py`.

REUSED existing USF types:
- AD/SR -> `Instrument.adsr`; vib delay/speed/width -> `VibratoConfig`
  onset/speed/amplitude (inverted in from_usf).
- WAVE program: `_slice_wave` follows the V5 $90 marker (ctrl==$90 -> the
  parallel freq byte is the ABSOLUTE loop target) into
  `Instrument.waveform`/`wave_freq`/`loop` — decodes away wave_ptr.
  `wave_freq` kept RAW (each step's melodic-vs-abs mode is its own ctrl
  bit 3, visible in `waveform`). Idle walk (table[0]) -> `wave_programs[0]`.
- freq table -> `freq_table` (96 lo + 96 hi). speed -> tempo. master_vol +
  $1015/$1016/$1017 leftovers -> `init.sid` (master_vol +
  InitFilter cutoff_lo/cutoff_hi/res_routing).
- Sectors -> `Pattern`/`NoteRow`: notes = pitch rows, gates ($FE) = `tie`
  rows. Orderlists -> `Orderlist` (entries + signed transposes + loop;
  loop byte-offset <-> entry index).

NEW schema (one principled field, spec-synced — types/grammar/parser/
writer/docs/test):
- `Instrument.pulse_sweep` (`PulseSweepConfig`): inline PW envelope
  `start=$NNNN seg (add, frames) ... [loop=N]` — decodes away pulse_ptr.
  Non-restarting instruments (ptr 0) carry `pwm.keep_running=true`; the
  position-persistence the keep-running relies on is ENGINE MECHANISM
  (per-voice pulse position), not stored content.

KEY WRITE-LOG LESSON (cost one fix-round): V5 `gate_logic` reads the
LOOKAHEAD byte — the raw next byte after a note/gate — to decide the
hard-restart gate-off. So sector command BYTE POSITIONS are write-stream-
significant; the `$FC` snd / `$FD` dur commands may NOT be reshuffled
relative to the notes/gates. They are carried as ORDERED PREFIX FLAGS
(`set_dur` / `set_instr`) on the following note/gate row, re-emitted
verbatim. (First attempt stamped instr per-row + re-emitted on change ->
moved a snd from before a gate to after it -> flipped one $D404 gate bit.)

The full sector command set is now handled (dur/snd/vol/frq/fade/adr/srr/
flt/gate_toggle as ordered prefix flags; gate_tie $F4; glide $FB = note +
glide; slide $FA = tie + glide). Sectors are still decoded in isolation
(family members self-establish dur/snd per sector — path-resolution like
V4 is residue if a member inherits sticky state across sectors).

## ✅✅ FACTORY + PARAMETERIZED PULSE/FILTER (2026-06-14)

`dmc_v5_config(sid)` factory (`pipelines/dmc/v5/factory.py`): 2-entry
jump-table detect (init+$40 / play+$A1; family-4 play+$95 REJECTED),
relocation-aware masked identity-compare vs the Katusha reference. Operand
classification (verified by tracing): code+state ([$1006,$170F) ∪
[$17CF,$1878)) RELOCATE; freq+data tables ([$170F,$17CF) ∪ [$1878,$19D0))
MASKED (packer-patched); SID/CIA (≥$19D0) absolute. Typed
`DMCV5Unsupported` (player_code_mismatch / no_jumptable / family4_branch /
cia_multispeed). Batch runner: `pipelines/dmc/v5/family_batch.py`.

PULSE/FILTER REPRESENTATION — **parameterized, NOT a shared table.** The
engine's pulse/filter tables are SHARED, FUSED resources (the packer
overlaps per-instrument programs to save bytes; ~30% have no $90, programs
bleed). Carrying them whole (content-by-reference flat table) is correct
but ML-worst (raw-byte program = Pole B + opaque index = Pole A). The
chosen form (user: "most principled / ML-optimal"): per-instrument
`pulse_env` / `filter_env` = `start + [(rate, frames)] phases + repeat` —
the PWM/cutoff envelope, the SAME musical family as Hubbard/DMC-V4 PWM
(cross-engine, §9 test 4). The packer's fusion is dissolved by
CAPTURE-BY-SIMULATION: `_capture_env` walks each instrument's reachable
phases (FOLLOWS $90 jumps — a loop target may be a count slot the engine
re-reads as a step — and detects a true cycle only on revisiting a
captured position; bounded by _REACH_FRAMES so bleeding past the horizon
is dropped). `from_usf` SYNTHESIZES a de-fused table (each instrument its
own copy + a $90 terminal); keep-running (pulse_ptr 0 -> pwm.keep_running)
continuations stay faithful because each continues whatever (faithfully
synthesized) program the prior restart-instrument was running. Validated:
all 5 sample-FULL members stay FULL through the parameterization (two
capture bugs fixed: $90 at the last table slot was skipped; $90 to a
count slot must be FOLLOWED+unrolled, not read as a phase index).

WIDE-BATCH COVERAGE — gated by COMPOSER/EXTRACT, not the representation.
80-member sample: 5 FULL (6%), 45 partial, 29 unsupported. The partials
reproduce in the DIRECT model path (no USF) — `composer_v5.py` was only
proven on Katusha. Bug distribution (the rounds, in lever order): $D416/
$D415 filter cutoff (22), end-of-init state-only Check-A (16), freq/PW (7);
plus expected residue (player_code_mismatch sub-builds, no_jumptable
relocated-in-file/CIA, ~36%). NEXT: composer rounds — FILTER FIRST (the
#1 lever), then state-only, then freq — like V4's coverage climb.

## ✅ FILTER ROUND 1 (2026-06-14) — startup-leftover priming (commits 8bea641, f598c2a)

The "$D416/$D415 filter cutoff (22)" bucket was TWO distinct causes; the
first-divergence register only NAMED the filter (it's the first write of
the play frame). Diagnosed via find_first_divergence + per-IRQ + ordered
FCHI/FCLO sequence diff.

**Cause A — uncleared STARTUP LEFTOVERS (the lead-in cluster, ~10 of the
22; "orig $D416=$00 / new $D418=$0F at play pos 0").** The V5 init sets
$1012 (speed reload) but the clear loop ($1067-$106E) only covers
$17D5-$1845, so THREE work-RAM bytes in the $1006-$103F gap keep their
file-image leftover values:
  - $1013 spdctr (speed COUNTER). When !=0 the first non-skip play() runs
    effects-on-leftover for N frames BEFORE the first note fetch (tick =
    speed==spdctr); those lead-in frames write freq from the leftover note.
    Katusha's $1013=$00 (0 lead-in frames) so the cleared-to-0 composer
    matched it; members with $1013!=0 diverged at play write 0.
  - $100F,x per-voice current NOTE. Read by the lead-in frames' wave_step
    (ADC $100f,x freq-table lookup) before the first fetch overwrites it.
  - $101C fade fractional accumulator. Init clears the fade SPEEDS
    $1018/$1019 but not this sub-integer phase, so a tune's first FD+/FD-
    ramps master vol from the leftover phase ($D418 vol off-by-one).
FIX: extract lo_spdctr/lo_notes/lo_mvolfrac; prime spdctr/curnote/mvolfrac
in init; carry through USF via the existing cross-engine `speed_ctr_init`
params key + `InitVoice.note` (V4 idle-note) + a new `fade_frac_init`
params key — NO shared-schema additions. Result: X-Files + Believe newly
FULL; whole cluster advances (Believe was 95%). Katusha still FULL; USF
round-trip faithful (direct==USF first_play_diff).

## ✅ FILTER ROUND 2 (2026-06-14, commit 24875f3) — keep-running filter_run

**Cause B — FILTER KEEPS RUNNING across FL=0 notes (a run-GATING bug, NOT
the synthesis-flow issue first hypothesised).** After cause A the cluster
(Grid/Minoam/Conanious) still drifts mid-song: FCLO ($D415) drifts (orig
RAMPS +1/frame, rebuild HOLDS) while FCHI ($D416) NEVER differs (the ramp
step is (0,+1) -> fchi+=0). Per-instrument `_capture_env` envelopes match
in ISOLATION (verified 200 frames) -> NOT a synthesis bug. ROOT CAUSE: the
orig `filter_run_v3` ($1496) gates ONLY on `CPX #$02` (voice 3) — it runs
EVERY V3 frame; FL=0 = "no filter RESTART", not "no filter RUN" (the SAME
PU=0 semantics as pulse_run). The composer gated `filter_run` on the
PER-NOTE `filtflag` (the instrument's FL byte), which an FL=0 note resets
to 0 -> the composer SKIPPED filter_run on keep-running frames -> the
cutoff held while the orig kept ramping. Katusha passed because its
pre-filter null is a no-op (the gate happened not to matter). FIX: a
STICKY `filt_run_on` flag, set once when any FL!=0 note inits the filter,
never cleared; `filter_run` gates on it instead of `filtflag`
(`filter_init` keeps the per-note gate, so FL=0 still = no restart). Only
ADDS filter_run on keep-running frames so FULL members can't regress (their
held positions were no-ops). The per-instrument `filter_env` representation
is UNCHANGED — this was a run-gating bug, not a synthesis/flow problem, so
the user-chosen parameterisation (option a, "faithful") stands without any
table change. RESULT (80-sample): FULL 5->15 over the whole session (the
filter rounds: +10 new FULL, NO regression; 7 of the 10 were original
$D416/$D415 partials — Grid/Reggae_2/Save_the_Kwiatki/Fire_Exit/
A_Load_of_Cowbell/Lands/Bach_VC-220). RESIDUE: Minoam 98.3% / Conanious
96.2% have a small end-of-song tail (per-register late diffs show V1/V2 SR
+ V3 freq, not filter — the diverse partial long tail, separate bug).

## ✅✅ RELOCATED / WRAPPER-INIT UNLOCK (2026-06-15, commits 0e3c319 + 023c1b6 + 5f3a0de)

The `no_jumptable` (261) + `player_code_mismatch` (266) unsupported buckets
were 477/527 the SAME family-3/5 player with a RELOCATED or WRAPPED init.
TWO sub-shapes (both found by dumping the jump table + init/play targets):
  - **wrapper/relocated init** (most `no_jumptable`): jump table at load,
    play entry -> base+$A1 (standard), but the INIT entry points elsewhere
    (e.g. $1CE9) — the init is byte-identical to the std init, just MOVED;
    the orderlist record is read by that moved init (operand at init+7).
  - **re-prefixed init** (most `player_code_mismatch` "opcode at $1040"):
    jump table +$40/+$A1, init at $1040 but its first bytes differ
    (`0A 0A 0A` = ASL*3 song-index vs Katusha `A9 00` = LDA #0). Single-
    subtune (A=0 -> Y=0) so the orderlist read still works at init+7.
Old factory keyed base off the jump-table LOCATION (fixed +$40/+$A1) and
compared the WHOLE player (init+play) -> any moved/re-prefixed init -> reject.

FIX (the family-1/2 sub-build playbook, V5 form) in `factory.py`:
  - `base = play_target - $A1` (the play routine is the reliable anchor; the
    jump table's play entry gives base regardless of where the init lives).
  - validate the PLAY-reachable body ONLY (`_v5_play_ref`, $10A1-$170E);
  - validate the init by its orderlist-copy SKELETON at the jump table's
    init target (`<4-byte prefix> A2 00 B9 lo hi 9D <17CF+delta>`) and read
    `op_orderlist = init_target + 7` (the moved init's actual load operand);
  - base-plausibility = `base + $848 <= $10000` (only code+state
    $1006-$1845 relocate; data tables are packer-patched — masked compare's
    job. The earlier $1900 margin wrongly rejected high-load base=$F000
    builds -> 2 regressions, fixed);
  - **multi_subtune** (ASL*3 prefix, `songs>1`, 36 members) typed-deferred —
    needs a multi-song PSID build the composer doesn't emit yet.
RESULT: ~300 members unsupported -> supported; **FULL 354 -> 461/1495
(+107; 30.8%; 41.9% of supported)**; all 461 mass-written + db refreshed.
RESIDUE: player_code_mismatch 152 (deeper code variants — bucket by
play-body first-diff PC), multi_subtune 36, note_out_of_range 36,
no_jumptable 22, error 108 (extract robustness), 640 partial (long tail).
NEXT: multi-song emit (multi_subtune) > partial long tail > deeper variants
> extract errors > family-4 (686, play +$95).

## ✅✅ MULTI-SUBTUNE SUPPORT (2026-06-15, commits b4994d0 + 21e767d)

Multi-subtune members index the orderlist record by song#: the init does
`ASL*3; TAY` -> Y = song#*8, then copies record N (3 track ptrs + speed +
master vol) into the work RAM. The data tables (sectors/instruments/freq/
wave/pulse/filter) are SHARED across subtunes; only the orderlist record +
its referenced orderlist streams are per-subtune.

5-file change: `engine_model` (V5Subtune dataclass; extract reads one record
per song at op_orderlist+N*8, tables shared, top-level fields mirror subtune
0) -> `composer_v5` (ordrec = one 8-byte record per subtune; init reads
song# from A: `ASL*3; PHA` across the state clear; `PLA; TAY`; index ordrec
by song#*8; PSID `songs` = subtune count — UNIFIED with single-subtune since
song#=0 gives Y=0, identical play) -> `to_usf` (one MusicSubtune per record,
per-sub tempo/master_vol/voices; the GLOBAL file-image leftovers — filter
cutoff, speed_ctr_init/fade_frac_init, idle notes — on subtune 0) ->
`from_usf` (pool sectors across ALL subtunes' voices into one shared pool;
read per-subtune speed/mvol/orderlists) -> `factory` (multi_subtune
rejection removed). RESULT: FULL 461 -> 466/1495 (+5; 31.2%, 41.4% of
supported), 0 regressions; 34 moved unsupported->supported; all 138
subtune-songs build correctly. A member counts FULL only if ALL its subtunes
are FULL, so the fully-FULL gain is modest — the partial multi-subtune
members have a subtune hitting the diverse long-tail bug. Single-subtune
unaffected (init change transparent). All 466 mass-written + db refreshed.

## ✅✅ PARTIAL LONG TAIL round 1 — FILTER OFF-TABLE read (2026-06-16, commit ba63846)

The biggest partial cluster (the FCLO/FCHI first-divergence bucket, ~70+
members; e.g. Bayliss A_Wonder/Alone_in_Bed: FCLO ramps +$39/+$29 vs orig
+$14, diverging at frame ~4). Root cause: the filter table is the LAST data
region, so its lo/hi-array delta (a_fh-a_fl) does NOT bound the program. A
TINY filter table (e.g. 2 entries) whose instruments all use filter ptr 1
runs filter_init (set start) then filter_run advances filterpos PAST the
array boundary, reading the OVERLAPPING lo/hi arrays + the bytes after them
as further (step,count) phases — the ramp lives OFF-TABLE. (Confirmed:
A_Wonder a_fl=$1E42/a_fh=$1E44, n=2, but the +$14 ramp step/count sit at
a_fl+2.../a_fh+2... right after the arrays, decoded by simulating the raw
memory.)

FIX (extract + capture, no schema/composer change):
- engine_model: read the filter table generously — n_filter = min(256,
  memtop) (filterpos is a byte; off-table bytes are exactly what the orig
  reads; reads past payload are 0, matching siddump's zero-fill). The
  wave/pulse tables are NOT last (bounded by the next table) so they keep
  the delta sizing. This also fixed ~28 _capture_env ptr-out-of-range errors.
- to_usf _capture_env: count==0 = the engine's 16-bit phase counter wraps
  (65536 frames) = a TERMINAL HOLD (treat frames 0 as 0x10000). The
  off-table zero-region decodes to (0,0) entries that otherwise spin to
  PHASE_CAP -> unsupported:sweep_too_long. (NB the direct model path already
  worked — it emits the 256-entry table verbatim; only the USF capture path
  needed this.)

RESULT (full family-3/5 batch): FULL 466 -> 543/1495 (+77; 36.3% of 1495,
47.1% of supported), 0 regressions; partial 660->610, errors 117->89. All
543 mass-written + db refreshed. RESIDUE: 610 partial (now led by the
Minoam-style END-OF-SONG tail — V1/V2 SR + V3 freq late diffs — + freq/PW),
player_code_mismatch 160, note_out_of_range 38, error 89, +2 new
filter_table_overflow (synthesized off-table env > 256 entries; rare).
NEXT: the end-of-song / freq-PW partial tail; then deeper variants.

## ✅✅ PARTIAL LONG TAIL round 2 — LOOP-TARGET TRANSPOSE (2026-06-16, commit ddaed0c)

The END-OF-SONG cluster (292 of 610 partials diverging at >=95%, just after
the orderlist $FF loop; songlength*1.1 captures ~1.1 loops). Root cause: the
composer's $FF loop handler set trkpos to the loop position, read the
loop-target byte, then jumped straight to tf_sector (treating it as a
sector#). But MANY orderlists loop back to a LEADING $FC/$FD transpose
command (e.g. Minoam: all 3 voices loop to pos 0 = $FC). The orig's $FF
handler jumps to $111F = the $FD/$FC re-dispatch, applying the transpose at
the loop target; the composer skipped it -> wrong note (+ downstream
pulse/SR drift -- the symptom looked diverse but the root cause was the same
loop) on EVERY loop iteration.

FIX (composer, 1 line): $FF handler now `jmp tf_chk_fd` (re-dispatch the
loop-target byte through the $FD/$FC transpose checks, then fall through to
tf_sector) -- structurally identical to the orig's $FF -> $111F. A sector#
loop target falls through unchanged, so non-transpose loops are unaffected;
a FULL member can't regress (it never hit this path). Verified the
trkpos/transp arithmetic matches the orig exactly.

RESULT (full family-3/5 batch): FULL 543 -> 683/1495 (+140 — the biggest
single win; 45.7% of 1495, 59.2% of supported), 0 regressions; partial
610->470. Minoam now FULL (its "pulse off-by-one" was downstream of this
loop). All 683 mass-written + db refreshed. RESIDUE: 470 partial (the
EARLY-diverging <50% set + remaining late diffs), player_code_mismatch 160,
note_out_of_range 38, error 89. NEXT: bucket the 470 partials by first-diff
(use a STRATIFIED SUBSET for iteration per CLAUDE.md — don't full-batch each
experiment); then deeper variants + family-4 (686, play +$95).

## PARTIAL LONG TAIL round 3 — loop-position + transpose RE-ESTABLISHMENT (commit e882c10)

FULL 683 -> 842/1495 (+159), 0 regressions. Two USF orderlist round-trip bugs
near the loop: (1) to_usf loop_to records each entry's GROUP-START byte
(transpose prefix if present) so a loop target at a $FD/$FC prefix is found
(was falling to loop_to=0); (2) loop-target transpose RE-ESTABLISHMENT (reuses
FC's Orderlist.loop_transpose) — the orig re-applies the transpose each wrap;
from_usf force-emits it. USF DSL gained negative loop@N-T (for $FC targets).

## PARTIAL LONG TAIL round 4 — carry-target loop fix + wrapper detection + triage tool

FULL 842 -> 848/1495 (56.7%), 0 regressions.

(a) **Carry-target loop fix** (commit 40f496d): round-3 handled loops targeting
the transpose PREFIX (re-establish) but NOT loops targeting the entry SECTOR
byte PAST the prefix (CARRY — the player keeps the running transpose over the
wrap). Those matched no group-start byte and fell to loop_to=0, REGRESSING 5
ex-FULL members (Metropolitan, Fast_and_Slow, Trance, Techno_2, Deep_Inside —
e.g. Deep_Inside v1 loops to byte $07, the entry just past an `fd 00` prefix).
_orderlist now maps each byte offset to (entry, is_prefix): sector byte ->
(i, carry), prefix byte -> (i, re-establish); a loop target lands on exactly
one (offsets unique). Monotonic — only rescues past-prefix loop_to=0 fallbacks.

(b) **Wrapper / trampoline detection** (commit 575492b): follow a 1-hop
`JMP base+$A1` relink stub to the real player base; resolve the init skeleton
among [jt-target, JMP-follow, base+$40]. +Background_Pleasure (carry fix pushed
it 98.4%->FULL). The masked compare was factored into return-first-divergence
helpers (_diff_play_body/_diff_init_skel) shared by the raising dmc_v5_config
and a new non-raising v5_diagnose.

**Triage tool — tools/divergence_census.py** (commit 575492b): clusters the
non-FULL residue. KEY FINDING: **detection != FULL** — the 153
player_code_mismatch are NOT the FULL bottleneck (the 7 wrapper members it
detects stay non-FULL; detecting just exposes downstream bugs). The
verify-PARTIALS are. (A by-hand "$10A1 = 52 trampolines" guess was corrected by
the tool to 2 — the cluster was heterogeneous; split opcode clusters by the byte.)

## PARTIAL LONG TAIL round 5 — static pulse/filter HOLD (commit 266a5b5)

FULL 848 -> 875/1495 (+27, 58.5%), 0 regressions.

The "67 check_A_state_only" bucket was a RED HERRING: 0 were init-priming. All
were `shift_d=None` trichotomy ALIGNMENT FAILURES — early play-stream
divergences that desync the midpoint landmark (the init prefixes MATCH, d=0).
The `[sub, False]` first_diff (no play diff recorded on the fallback path) made
them indistinguishable from a true Check-A state diff. The TRUE first-divergence
register histogram (flat prefix from 0): **~34 pulse-width** (this fix), ~18
filter, ~13 frequency.

Pulse-width root cause: clean 2x-per-frame ramp. `from_usf.add_env` emitted
`[start][$90 -> start]` for a STATIC env (phases=[]); pulse_run/filter_run treat
the $90 loop target as the next ADD step and re-read the START pair as a step,
so PW ramps +start.hi/frame instead of holding (Hardcore_DMC V1 $D403: orig
holds 8; rebuild 8,16,24,32,40...). Fix: a static env now loops on a ZERO-ADD
with count==0 (65536-frame hold): `[start][00 00][00 00][$90 -> the zero-ADD]`.
Shared by pulse + filter (both call add_env); phases!=0 path unchanged. Also
`verify_cycle` shift_d=None fallback now reports first_play_diff (16c4053,
diagnostic) so future batches don't mis-bucket these.

NEXT: the ~18 FILTER + ~13 FREQUENCY first-divergence clusters (distinct bugs —
filter is non-2x cutoff divergence; freq likely vibrato/glide); then remaining
non-static pulse partials; player_code_mismatch variants; family-4 (+$95).

## PARTIAL LONG TAIL round 6 — default (idle) V3 filter sweep (commit 86d3259)

FULL 875 -> 889/1495 (+14, 59.5%), 0 regressions.

The engine runs filter_run_v3 for V3 EVERY frame from filterpos=0, where
filter-table position 0 is a DEFAULT (idle) cutoff sweep no instrument points
at — applied to the leftover cutoff from song start, before/between explicit
filter notes (for tunes whose V3 never plays a filtered note, this IS the whole
filter motion, e.g. Glory_Kingdom). The composer nulled entry 0 and gated
filter_run on a sticky filt_run_on flag (its own comment flagged this as an
approximation), so it never ran the idle — Little_Sara $D415/$D416 held (0,182)
2 frames where the orig swept to (8,190) via entry-0 ADD (8,8).

Representation (principled per docs/the_principle + the init
trichotomy): the idle filter is the SAME musical object as a per-instrument
filter (a cutoff SweepEnvelope, Rule 1). It is PLAY-TIME content (a sweep the
play loop performs), NOT init priming — so init.sid.filter keeps only the
starting cutoff STATE; the new top-level USF `default_filter` carries the SWEEP
(phases). Musically named, no engine index, read by the engine-blind composer.
Shared USF plumbing: UsfFile.default_filter (SweepEnvelope), grammar
default_filter_block (reuses swenv_args), parser + writer + docs/usf_format.md.

Composer: filter_run runs for V3 from frame 0 (filt_run_on gate removed;
filterpos init=0 via state clear). from_usf emits position 0 = the default_filter
sweep, or a (0,0)/count==0 HOLD when absent (so filter_run never reads an OOB
count). Extract: _capture_env(has_start=False) reads the idle program from
filter position 0 when entry 0 is a real ADD. Full tools/regression.py GREEN.

## PARTIAL LONG TAIL round 7 — song-derived sweep capture horizon + walk-cap (commit 5b32e79)

FULL 889 -> 891/1495 (+2), 0 regressions; timeout 10 -> 0, +9 capture_loop.

`_capture_env`'s sweep capture was bounded by a FIXED `_REACH_FRAMES=30000` —
"capture this many frames then stop." A magic number unrelated to the song,
safe only because 30000 > every 1x song's verify window. Replaced by the actual
per-song horizon: `reach = min(songlen*1.1, 1500) * 50` play-frames (= the
verify window; verified V5 members are all vblank — CIA/multispeed rejected
upstream — so 50Hz is exact). Computed in write_v5_usf from cached
Songlengths.md5; threaded model_to_usf -> _instrument_to_usf / idle ->
_capture_env. Fallback 30000 when songlength unknown.

WHY a horizon (not "capture the whole program to its loop/hold"): from_usf
DE-FUSES the editor packer's overlapped/byte-shared programs into a fresh table,
so a complete capture can exceed the original's 256-entry cap. Bounding at the
window (what the verify actually plays) keeps the de-fused table fitting. Helps
both ends: SMALLER for short songs (fixed filter_table_overflow on Hot_Island,
Progress = the +2) / LARGER for >545s songs (closes the old fixed-30000
under-capture hole). A real $90 loop or hold terminal still wins when it occurs
before `reach`.

WALK-CAP (separate seatbelt, in READS not frames): a malformed table where a
$90 targets another $90 in a cycle (appending no phase) made the walk spin
forever — a 900s batch timeout, or an infinite hang in any tool without a
timeout. `_WALK_CAP=5000` now raises `unsupported:capture_loop` instantly. The
idle-filter capture is best-effort (a malformed idle table -> no default_filter,
composer holds; never a member-wide error).

(Provenance: the owner questioned "why 30000, not songlen*1.1?" — the instinct
was right. An interim "capture the complete program" over-corrected and
overflowed 2 de-fused tables before this landed on the per-song window. The
deeper lesson: extraction is STATIC, but the write-log verdict is the judge —
REACH passed only because verify windows stayed under it; the horizon makes the
capture provably cover exactly what the write-log checks.)

NEXT (ranked by size): (1) FREQUENCY (~143 across V1/V2/V3 freq regs — the
BIGGEST cluster now, likely vibrato/glide); (2) remaining pulse partials with a
SECONDARY divergence (idle now fixed, e.g. Doomed/Amiga-Zak); (3) NON-idle
filter bugs (Emulating_Vinkuna, Cooksey, Art_of_Noise); (4) player_code_mismatch
variants; family-4 (+$95).

## PARTIAL LONG TAIL round 8 — default (idle) per-voice PULSE sweep (commit a4c70c8)

FULL 891 -> 913/1495 (+22), 0 regressions. The pulse cluster's dominant
`rebuild=0` sub-pattern is a real idle pulse program at pulse position 0 (e.g.
Doomed V2 $D409 = 0,49,98,147,196 = pulse[0]=(0,49) loop) that the composer
nulled. Fix: carry it as `default_pulse` (pulse twin of `default_filter` — a PW
SweepEnvelope, play-time content), emit at pulse pos 0; pulse_run runs it from
pulsepos=0 (UNCONDITIONAL — `run_effects` JMPs straight to pulse_run; there is NO
per-voice gate; `$1841` only gates the note-time pulse LOAD, not the steady run).

**The instructive false start (do not repeat the layout part):** the first cut
regressed 891 -> 786 (-135). The cause was NOT the idle ramp and NOT a missing
"gate" (an earlier note wrongly hypothesized a per-voice pulse-active gate — the
disassembly's `run_effects` disproves it). ALL 135 regressed members have
`pulse[0]=(0,0)` (no idle). The bug was changing the NO-IDLE case from the single
`(0,0)` entry to a 3-entry hold `[(0,0),(0,0),($90,0)]`, which shifted the
de-fused pulse table. FIX: keep the single `(0,0)` for no-idle members
(byte-identical to the prior FULL state → cannot regress); emit the idle ONLY
when `pulse[0]` is a real ADD. (The filter's 3-entry hold WAS needed because
round-6 un-gated filter_run; pulse_run was never gated, so its single `(0,0)` +
benign OOB-count read was always correct.) Lesson: a no-idle layout "cleanup"
is NOT free — the de-fused table is position-sensitive.

## DETECT-REJECT round 1 — work-RAM scratch relocation (reloc@$10E5)

`divergence_census --cluster player_code_mismatch` ranked the 153 PCM
detect-rejects; the top cluster (41) diverged at `$10E5` (and `$1119`),
`[reloc] ref=$1006 member=$22xx`. Probe (`tmp/reloc_probe.py`): both sites are
the SAME work var (`LDA $1006,x` = voice-active flag), the ONLY two divergences,
and the freq table ($170F) + data region ($1878) are byte-identical to Katusha
at delta=0. So these are the **exact family-3/5 player with only the $1006-$103F
work-RAM scratch block relocated** (a relink moved it up near a wrapper). That
block is RUNTIME STATE, not musical content, and the composer rebuilds its own
engine — so its address is a don't-care for detection AND extraction.

FIX (factory.py): new `'state'` opclass for operands valued in the scratch gap
`_STATE=((0x1006,0x1040),)`; `_diff_play_body` skips the operand compare for
`'state'` (like `'patched'`). CODE operands in the same `_CODE_STATE` span still
relocate by delta exactly (checked first by range order). **Detection-loosening
only → cannot reject any previously-accepted member (zero regression risk).**

RESULT (live re-cluster of the 153): 8 newly accepted (VBI) → **+5 FULL**
(Olsen/{Ah,Fuzzy,Short_Zak}, Kordiaukis/{Octavarium,Rotting_Christ}); 3 partial
(join the freq/pulse partial residue). The fix also SURFACED **32 cia_multispeed**
members (previously blocked at the reloc check — they're wrapper members with the
PSID speed bit set; VBI-only verify can't validate them → a distinct, larger
problem) + 106 still mismatching at other sites ($10A1 opcode variants, $1385
JSR-patch, $16C7 BIT-nop) + 7 init_skeleton. Reaffirms the census lesson:
**detection ≠ FULL** — accepting at detection just moves a member to its next
failure mode.

## PARTIAL LONG TAIL round 9 — PULSE off-table program (+17)

The pulse-partial cluster (52, census `--partials` reg $D402/$D409/$D410/$D403)
top sub-pattern: a long match then PW-lo holds where orig RAMPS (Lectro_64:
matches 41s, then orig PW-lo ramps +8/frame from $77 while mine holds at $77).
Cause: the pulse table was bounded by `n_pulse = a_ph - a_pl` (the lo-array
length), but `pulsepos` is a byte — an instrument whose program is longer than
the lo array runs `pulse_run` PAST it, reading the overlapping hi/filter arrays
+ trailing bytes as further (step,count) phases. Lectro inst pulse_ptr 17 starts
at $7777 (table[17]) so its phases begin at pos 18 = past `a_ph-a_pl`=18 →
`_capture_env` saw `pos>=len(table)` → empty phases → HOLD. The ramp ((0,8) rate
+ (67,28)=17180-frame count) lives off-table. This is the EXACT case already
handled for the filter table (the last region); pulse just wasn't bounded the
same way.

FIX (engine_model.py): `n_pulse = min(256, 0x10000-a_pl, 0x10000-a_ph)` (was
`a_ph-a_pl`); `_capture_env` bounds the reachable program per ptr (loop/terminal/
reach), so it only ADDS correct phases for off-table-running programs and leaves
in-table ones unchanged → cannot regress. RESULT: **+17/52** pulse partials →
FULL, 24/24 regression-FULL clean. The remaining 35 are OTHER pulse sub-bugs
(orig=0↔mine=val holds, a +12 start offset, V2/V3 variants) — a heterogeneous
cluster, drain separately.

FOLLOW-UP — WAVE off-table (same bug class), DONE (+6): the `wave_slice` ERROR
cluster (11) is the identical off-table case on the WAVE table — `_slice_wave`
raises "no $90" because the program's loop marker is past `n_wave = a_wf - a_wc`
(Compotune wave_ptr 68 finds its $90 only with the table extended to 256). Applied
the same `min(256,…)` bound to `n_wave`. RESULT: **+6/11** → FULL, 24/24 regression
clean. Residual 4: 2 `wave_table_overflow` (the de-fused wave program now exceeds
the 256-entry table cap — a separate downstream cap sub-bug the longer capture
exposes) + 2 still `wave_slice` (program > 256 / different structure) + 1 partial.
(Distinct from the ~150 freq partials, which are a wave-freq VALUE bug, not
off-table.)

## PARTIAL LONG TAIL round 10 — default_pulse leading-(0,0) phase (+25)

After round-9 off-table (+17), the pulse cluster's residual 35 were NOT a data
bug — proven via memwatch: at the divergence the full V1 note-state (gateflag,
secpos, trkpos, durctr, notestart) is IDENTICAL between orig and mine; only PW
differs. orig's `pulsepos` advances 0→2 purely by RUNNING the pos-0 idle program
([(0,256),(80,…)] = +0 for 256 frames then +80 ramp); mine's idle held. Root
cause: the round-8 `default_pulse` detection gated on `pulse[0] != (0,0)` + a
nonzero-rate phase — but **a leading (0,0) is a valid zero-rate phase** whose
count is at pos 1, not "no idle". So:
- A (mine holds, orig ramps): orig idle = +0-then-ramp, mine captured None → held.
- B (mine ramps, orig holds): orig idle = pure +0 hold, mine's null pos-0 BLED
  into the adjacent instrument program (its de-fused pos-1 = an inst start) →
  spurious ramp.

FIX (extract/to_usf.py): capture pos-0 FAITHFULLY via
`_capture_env(pulse, 0, has_start=False)` (drop both gates); emit `default_pulse`
unless the idle is a TRIVIAL terminal hold (single zero-rate phase, count
>= 0x9000) — that genuine no-idle case stays the single (0,0) null to preserve
the 891-FULL de-fused layout (round-8 showed a fabricated multi-entry hold there
shifts pptrs + regresses). RESULT: pulse cluster **42/52 FULL** (off-table 17 +
default_pulse 25), **200/200 regression clean**. CORE TENET: mine's pos-0 idle is
now the same PW program orig runs, captured parametrically — no mechanism copied.
Residual 10: the +12 start-offset trio (Triiod/X-Bass/Summer_Zak), a few pwhi/V3
pulse, and 2 that GRADUATED to the freq cluster (pulse fixed, freq now first-diff).

## PARTIAL LONG TAIL round 11 — off-table FREQ lookup (freq_overrun) (+44)

The freq cluster (163, the dominant partial residue) localized Trap-C-FREE via
the C4 technique (`assemble(return_labels)` + memwatch our wave-state vs orig's
disasm addresses — no "spinning" like prior sessions): at the divergence the note
(curnote) matches, only the freq output differs. Root cause (Elysium inst8/9):
the melodic wave path computes `(wave_freq[step] + curnote) & $FF` and reads
freqlo/freqhi there; index 64+60=124 falls past the 96-entry tables. orig's
off-table byte is real content (freq_hi[124]=0); we emitted only 96 entries, so
the read hit garbage. This is the SAME problem FC solved with `freq_overrun` —
recorded as convergence-ledger C6 (consult-the-ledger working as designed).

FIX: ported FC's `freq_overrun` TECHNIQUE (not code — v5 is a separate composer).
`engine_model._freq_overrun` captures the reachable off-table freq-hi window
(melodic wave values × notes/glide/slide targets × transposes, conservative);
threaded through USF (`freq_overrun` field, already shared); `composer_v5._emit_data`
emits it contiguously after `freqhi` so off-table indices resolve. Content-by-
reference → cannot regress. RESULT: **+44/163** freq partials → FULL, 200/200
regression clean.

The residual 119 are a SEPARATE sub-cause: the de-fused WAVE PROGRAM steps to a
different LOGICAL position than orig (mine's wavepos lands elsewhere → different
wave_freq → different index → different freq), even at a matching note. Ceti_22 /
Elysium-V2 are this — next sub-investigation. (Also: v5's freq_overrun capture is
conservative, not minimized like FC's uready-round-A; minimize later.)

## Round 12 (2026-06-20): WHAT the off-table read actually IS — provenance census + packer RE

Driven by "why are RAM scratch bytes in the SID if not a kind of init?" + "RE the
packer to see if it places anything after the freq table."

**Packer RE (`docs/src/DMC_V5.0_PACKER.prg`, uncrunched — disasm in
`docs/src/packer.disasm.txt`):** reads editor source tables (`$4000` instruments,
`$4200-$4700`), embeds a player template (the spacing-3 work-RAM pattern at a
`$0900` working base = the `$17CF+` Katusha block shifted), builds a *relocatable*
output. Places **no deliberate table after the freq slot** — the after-freq region
is the player per-voice WORK RAM. (Depacker is crunched; the player disassembly +
factory operand list are the layout authority anyway.)

**Provenance census (504 off-table members, all `fhi_off=$76F`):** map each
off-table HI read address `a_fhi+Y` (canonical offset `$76F+Y`) onto the work-RAM
var via `disassembly.s`. The off-table read lands on:
- **~84% ADVANCING state** — dominantly `trkptr` (first 6 work-RAM bytes, right
  after freqhi, so the smallest overshoot Y≈96-101 hits them) + `trkpos`/`secpos`.
  `trkptr` is the per-voice **track-read cursor = a memory ADDRESS** (orderlist-
  loaded track base + byte-advance). So the dominant off-table "frequency" is
  **the engine playing its own track pointer (an address) as a pitch** — pure
  mechanism, no musical pitch.
- ~10% PER-FRAME counters (durctr/wavepos/pulsepos/pw/vib accumulators).
- ~4% static note-params (durrel/instr/vib settings).

**Refuted prediction (confirmation-bias guard):** "advancing-landing → partial"
is FALSE. FULL off-table members = 83% advancing-landing; PARTIAL = 86% — same.
Landing-class does NOT decide pass/fail; the determinant is whether the
freq_overrun STATIC snapshot still equals the RUNTIME value when each *reached*
off-table read fires (init-state vs evolved-state) — a runtime fact.

**Honest conclusion.** Both user instincts right: it's NOT random scratch (it's
the structured track pointer/counters), and its value STARTS as init state (track-
start address loaded at init = the file-image byte freq_overrun captures). BUT the
value is engine-POSITIONAL (`trkptr` = layout address). The CORE TENET forbids
layout-matching ("shifting data addresses" = the named hack = P1, rejected), and
clean layout-independent code cannot synthesize an address → the advancing-`trkptr`
writes are, in the project's own terms, **not cleanly reproducible as music**.
`freq_overrun` recovers the read-before-evolution subset by capturing the init
address (trichotomy "engine bookkeeping" — positional, OUT of musical USF, NOT a
pitch). The evolved subset needs engine-state-mechanism reproduction (P1-class) or
per-frame replay — both rejected. The rare genuinely-mechanism boundary; this is
the principles WORKING (refusing to encode an address as music), not a duck.
STRATEGIC CALL pending: reproduce-the-mechanism vs bookkeeping-capture + documented
residue.

## Round 13 (2026-06-20): IS the overshoot ever AUDIBLE? — ground-truth (libsidplayfp)

Question: does any SID overshoot the freq table and play the value as audible sound?
Method: predict off-table (lo,hi) freq pairs from the file image (FULL members →
file image == runtime at reached reads), capture the libsidplayfp `--writelog`,
reconstruct per-voice (freq,ctrl) + master vol, count frames where a predicted
off-table pair plays on a waveform+gate voice with vol>0.

**ANSWER: YES, but rare + static analysis MASSIVELY over-counts.** Static (wave-
program × all-notes) predicted e.g. 40 audible overshoots for Happy_Man → **0**
actual (instruments only play specific notes, not every note in the song). Of 32
FULL off-table members sampled: only **6 REACH** an off-table read at all; only
**2 reach it AUDIBLY**. Concrete audible cases (ground truth):
- `MUSICIANS/A/Angee/Compotune.sid` — V3 pulse bass `$0A00` (~150Hz), 44 frames.
- `MUSICIANS/B/Bayliss_Richard/Dead_End.sid` — V2 noise drum `$FF00`, 17 frames.

**Big practical consequence:** the `freq_overrun` verbatim blob is emitted in
100% of v5 FULLs but **dead padding for ~81%** (never reached → removing it there
is FREE, zero regression). Only ~19% reach the read (need the byte for writelog-
exactness); ~6% audibly. Note the audible values seen ($0A, $FF) look like
constants/counters, NOT track-pointer addresses ($10-$1A) — HYPOTHESIS (unverified):
the audible overshoots land on stable/decodable bytes while the address-reads are
the never-reached / inaudible ones. If true, the clean-decode path FULLs the
audible cases and the messy trkptr-address cases are never heard anyway.
NEXT: (1) precisely census reached-vs-unreached over all v5 (drop blob where
unreached — free de-verbatim of the majority); (2) test the audible-lands-on-
stable hypothesis.

## Round 15 (2026-06-21): authoritative load-bearing measurement (verify-gated)

Built every non-empty-blob member WITH and WITHOUT freq_overrun (monkeypatch
`_freq_overrun -> []`) and diffed the writelog verdict. Of 1217 members with a
non-empty blob:
- **997 (82%) DEAD-PADDING** — FULL both ways; the blob does nothing → drop it
  (free de-verbatim, the ~81% the round-13 audibility census predicted).
- **44 LOAD-BEARING** (= the historic +44) — FULL with, PARTIAL without. Stable
  reads. Characterized (value-matching, reliable for stable): dominantly
  **layout-independent** (filtpos+, pulsepos, glidetgt, gateflag, vol, instr,
  transp, wavepos), only 2 on `trkptr_hi` (near-constant page) → **all clean
  absolute-freq candidates** (ML-musical fixed pitch).
- **176 PARTIAL-WITH-BLOB** — ~70 other-cause (non-freq / freq-but-not-offtable),
  ~9 no-diff, ~**97 off-table-dynamic**.

**RESOLVED (the 176 are NOT the blob's problem).** The 176 are partial *with* the
blob, so the blob is not their fix — replacing/dropping it leaves them unchanged.
Spot-check confirmed: e.g. Bax/Sixtime first_diff is reg 14 (v2 freq **lo**), and
a lo off-table read at idx 96-191 lands in the `freqhi` *table* (in the USF), i.e.
a wave-position/index divergence, not an off-table-data problem. And the 44
load-bearing are **all stable by definition** — a static snapshot can only fix a
stable read; a dynamic read lands in `partial-with-blob`, never `load-bearing`. So:
- **44 load-bearing → absolute-freq wave step** (all stable → ML-clean, exact).
- **997 dead-padding → drop the blob.**
- **176 partials → untouched** (pre-existing, separate causes: index/wavepos bugs,
  dynamic state, non-freq).

Consequences: the de-verbatim is **LOSSLESS** (no FULL lost), ML-clean, and
**StateLayoutMirror is NOT needed** — there is no load-bearing *dynamic* tier (it
can't exist by the definition of load-bearing). The earlier "+70-90 recoverable
via StateLayoutMirror" was an artifact of static value-matching being unreliable on
dynamic reads; genuine recoverable coverage in the 176 (index fixes, maybe a few
real dynamic counters) is SEPARATE future work, not this de-verbatim. The
absolute-freq plan (`deprecated/old_docs/offtable_freq_plan.md`) is correct; drop its StateLayoutMirror
mentions + its "dynamic residue" framing (the de-verbatim has no residue).

## Round 16 (2026-06-21): offtable_freq SHIPPED + what the blob actually IS

**The blob, fully understood.** The freq tables are at FIXED `$170F`/`$176F`; the
first data table (orderlist) is always `$1878+`. The fixed gap `$17CF-$1877` holds
the player's INITIAL ENGINE STATE + the per-voice track sequences. Verified: the
work-RAM trkptr at `$17CF` (`48 52 6C / 18 18 18`) == the orderlist record's
pointers at `$1878` (`$1848 $1852 $186C`); trkptr_hi=`$18` is the orderlist page,
constant across tunes. So the off-table read (unchecked `freqlo/hi[offset+note]`,
no bounds check) sonifies the engine's own memory — orderlist POINTERS (addresses),
counters, and track-sequence bytes. NOT authored pitch.

**Documentation (online sweep: CSDb, codebase64, Chipmusic, Lemon64, Chordian,
GitHub, the 2025 closed-source DMC4 Editor by Brian).** The off-table is
UNDOCUMENTED anywhere. But it is the v5 expression of a DOCUMENTED DMC-family drum
idiom: DMC4/7's wavetable FX bit 0 = "DRUM EFFECT: pitch values step in higher
range" (TND tutorial). v5 dropped the FX byte; its drum/fixed-freq sounds come via
the TEST-bit mode (documented) + the off-table overshoot (emergent). The player
binary is the sole authority.

**Audibility (ground truth, 44 load-bearing):** ~14 AUDIBLE (noise drums + tri/
pulse tones — incl. Message_Unknown's sustained tri lead), ~30 inaudible / writelog-
only. So `offtable_freq` is the drum/fixed-freq primitive for the audible; the
inaudible are bookkeeping (audibility derivable downstream from gate/sequence).

**SHIPPED.** Extract emits per-instrument `offtable_freq` (step,note,lo,hi);
composer builds in-bounds extended freqlo/freqhi from it; `freq_overrun` blob gone.
Authoritative batch: **1039 FULL** (vs 1041 freq_overrun baseline) — net **-2**,
exactly the 2 coincidence-masked members. Mass-written + db-refreshed.

**The -2 (SEPARATE work, NOT off-table):** `Behdad_Arman/Redemption_6_4` (0
off-table records; diverges on an in-table freq @ reg0) + `Simon_Laszlo/Planet_Love`
(its 1 real off-table read captured; diverges on a COMPUTED glide/vibrato freq).
Both were FULL only because the blob's ~160 bytes shifted later-table addresses and
accidentally masked a pre-existing freq-computation bug. Dropping the blob (correct)
exposed them.

## Round 17 (2026-06-21): offset-keyed offtable_freq + base read -> 1040; the -2 re-diagnosed

**Schema refined to OFFSET-keyed** `(offset, note, lo, hi)`, idx=(offset+note)&$FF.
Besides wave-program step offsets, now capture the **offset-0 BASE read** =
`freqtable[effective_note]` used by vib_setup (vib step = base-note freq << width),
the note's own freq, and glide arrival — a site the wave-step-only walk missed.
Composer computes idx directly (drops the wave_ptr lookup). Batch: **1040 FULL**
(step-keyed 1039 + Redemption_6_4 recovered, 0 regressed). Mass-written + db-
refreshed.

**Redemption_6_4 RESOLVED** — it was exactly the base-read gap: V1's note wraps to
effective 252 via transpose, so vib_setup's `freqtable[252]` base read off-tabled
and was uncaptured. (Only ~1 of the 17 eff>95 partials recovered; the other 16 are
partial for other reasons.)

**Planet_Love RE-DIAGNOSED — NOT glide.** Trace of the ORIGINAL's V1 glide state at
the divergence: speed $17ED=0, accum $1835/$1838=0, target $17F0=0 — glide INACTIVE.
The freq is wave-program-driven (`$1811` steps FF,0C,08,06,05,04,01 = an arpeggio/
percussion pitch drop). Our rebuild diverges to $4104. So it's a **WAVE-POSITION
divergence**. CORRECTED below.

## Round 18 (2026-06-21): Planet_Love RESOLVED — idle-program off-table gap -> 1041 (LOSSLESS)

Traced the rebuild's wavepos (via composer xa65 `return_labels`) vs orig's $17F3:
**wavepos MATCHED** (both 7 post-INC) at the divergence — so NOT a wave-position
divergence either. The frame-9 wave step uses wavepos **6** (pre-INC): the IDLE
program's step 6 (`wave_freq[6]=$E0`) x idle note 26 -> idx **250** (off-table). The
value at idx 250 is STABLE ($0100, file-image == runtime every frame) — orig reads
$0100; our rebuild read $4104 because `ext[250]` was UNCOVERED: the IDLE program
(wave index 0, played at lo_notes during the lead-in) was not in the per-instrument
walk. FIX: `_assign_offtable_freq` now also captures the idle program x lo_notes
(attributed to instrument 0; composer dedups by idx). Planet_Love -> FULL, 25/25
FULL sample clean.

**BOTH "-2" bugs were CAPTURE GAPS, not effect bugs.** Neither was glide/vibrato/
wave-position — both were missing off-table read SITES: (Redemption) the vib_setup
offset-0 base read; (Planet_Love) the lead-in idle program. The off-table capture
is now COMPLETE: wave-program steps + offset-0 base reads + the idle program.
RESULT: **1041 FULL = the freq_overrun baseline, blob eliminated — fully lossless.**

## (historical) factory + wide-batch plan
`dmc_v5_config` factory (jump-table detect init+$40/play+$A1, the
operand sites above, carved reference) + reuse pipelines/dmc/family_batch.py
over family-3/5 (1495). Then the family-4 branch (686, play +$95).

## (historical) Phase C plan

A NEW hand-authored V5 engine (the V4 `composer_asm.py` does NOT apply —
8-byte instruments, table-based pulse/filter, full filter cutoff, the
14-command sector model). Must be RE-AUTHORED clean (the tenet forbids
emitting verbatim/relocated player bytes). USF schema co-designed
write-log-first: the 3 programmable tables (content-by-reference), fade,
ADR/SRR, full cutoff, vib-step=freq<<width. Verdict: `verify_dmc`
(engine-neutral, reuse). Then factory + wide batch (family-3/5, 1495),
then the family-4 branch.
