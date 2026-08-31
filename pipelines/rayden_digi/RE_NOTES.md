# Rayden_Digi — reverse-engineering notes

**Status (head = current). EXTRACT BUILT AND GATED 2026-08-31; no composer
yet.** This is phase 3 of `docs/digi_parametrization_proposal.md` (schema
landed 2026-08-29; Digi-Organizer, phase 2, closed at 39/39). 17 carriers,
all `MUSICIANS/R/Rayden/`.

`pipelines/rayden_digi/extract.py` decodes the score, the sample table and
the playback core; `verify_score.py` gates the result against the
libsidplayfp `$D418` write stream. Morbital, Morbital_plus and
Spelling_Around pass BOTH checks (every one of 390,050 / 385,155 / 654,065
digi writes explained, per-event timing residual p90 ≤ 0.3%);
Embarassed_Emotions passes CONTENT but its timing is not corroborated (see
the 2026-08-31 extract section). No USF writer yet.

⚠ **The V1/V2 label is dead for build purposes** — 13 of the 17 carriers,
NINE of them sidid `Rayden_Digi_V1`, run the SAME sequencer. See "one
sequencer, two playback cores" below; it is the measured backing for the §8
guard, not just an argument.

## 2026-08-31 — family opened; V1 vs V2 are DIFFERENT PACING TOPOLOGIES

Before this session the family had nothing — no `pipelines/rayden_digi/`, no
disassembly, no RE notes, and no `engine_docs` row (state `NONE`). The only
prior RE is the proposal's §2 static pass on V1 (Boot_Zak_v2). This file
opens the family and answers the proposal's §8 first open question.

### Carriers (sidid `engines`)

    Rayden_Digi_V1  13   1970s_style_Hammond_Organ, 4_Ever_Young_2SID,
                         Boot_Zak_v2, Cyclones_Birthday, Fast_Moving,
                         Im_So_Excited-I_Just, Knusprig_Sampl_Checka,
                         Lost_Patrol_v2, Lost_Super_Scrotum_Elefantiasis,
                         Panzer_im_Kopp, Popel_Premiere_Intr0h_2SID,
                         Smooth_Mumu_Operating, Trinkhoffs_and_Doenerpuste
    Rayden_Digi_V2   4   Embarassed_Emotions, Morbital, Morbital_plus,
                         Spelling_Around

All 17 are **RSID with `play=$0000`** — init installs an interrupt and never
returns (ledger C40's self-driven class). 16 sit beside a DMC player;
Spelling_Around sits beside a Rob_Hubbard player and is not a DMC member.

### MEASURED from the write stream (siddump, 120 s, `force_rsid=True`)

| member | ver | $D418/frame | value shape | `or_mask` |
|---|---|---:|---|---|
| Boot_Zak_v2 | V1 | 166.2 | `$07 $08 $06 …` | none |
| Lost_Patrol_v2 | V1 | 110.3 | `$0B $08 $07 …` | none |
| Morbital | V2 | 137.1 | `$39 $3A $38 …` | **`$30`** |
| Embarassed_Emotions | V2 | 143.3 | `$18 $17 $19 …` | **`$10`** |
| Spelling_Around | V2 | 216.6 | `$08 $07 $09 …` | none |

**`or_mask` varies PER MEMBER, not per version** — it is the filter-mode bits
held high while the digi drives the volume nibble ($10 = LP, $30 = LP+BP), so
the music's filter routing survives the digi owning the register. This is
exactly the schema's existing `DigiConfig.or_mask`; no new field needed.
Playback rate likewise varies per member (110-217 writes/frame) → the
existing `SampleInstrument.rate_cycles`.

### THE V1/V2 SPLIT IS REAL, and it is the PACING TOPOLOGY

    V1 (Boot_Zak_v2)  43 `STA $D418` sites, most in a contiguous run at
                      $2218/$2228/$2238/… stride $10 = the UNROLLED
                      RASTER-BURST player the proposal §2 spotted
                      ($2200-$2498, 3 writes/badline).
    V2 (Morbital)     3 `STA $D418` sites; TWO of them ($28C7, $28DC) are
                      two NMI handlers that SWAP THE VECTOR at each other
                      (`LDA #$3D / STA $FFFA` and `LDA #$20 / STA $FFFA`).
                      The third ($105C) is the music player's.

So **V2 is the two-vector-swapped-handler shape, the same topology as
Digi-Organizer** (proposal §2), which is the family we have already built.
That is the useful finding: V2 should reuse phase-2 machinery, and V1's
raster-burst is the genuinely new pacing.

> ⛔ **§8 GUARD — READ BEFORE WRITING ANY COMPOSER CODE FROM THAT SENTENCE.**
> "Reuse the phase-2 machinery" means reuse the PARAMETRIC EMITTER. It does
> NOT mean "detect V2 and call the Digi-Organizer player", and it does not
> mean a `rayden_v1` / `rayden_v2` branch anywhere in the composer. That is
> Principle §8 exactly — engine identification selecting an engine library —
> and this codebase committed it here, in this family's sibling, on
> 2026-08-30: fourteen hand-written driver templates chosen by name from
> `params['digi_driver']`, six of them single-carrier (backlog 35, ledger
> C40 points 1-2, since corrected).
>
> The composer may branch ONLY on measured, musically-named facts —
> `technique`, `or_mask`, `rate_cycles`, the score — never on which author's
> player or which sidid version string a member came from. Note the measured
> support for this: `or_mask`, the rate model and the raster burst ALL vary
> per MEMBER and cut across the V1/V2 line, so a version branch would be
> wrong on the facts as well as on the principle. The V1/V2 label is a
> research shorthand for a pacing topology; it must not reach the build.

V2 handler skeleton, as it sits in the file image (Morbital $28B8/$28D5):

    handlerA  STA $3b / LDA <smc ptr> / CMP #$1F  (in-stream terminator)
              BEQ end / STA $40 / AND #$0F        (low nibble)
              ORA #<smc mask> / STA $D418
              LDA #$3D / STA $FFFA                (swap to handlerB)
              BIT $DD0D / RTI
    handlerB  STA $56 / LDA <smc ptr> / ORA #<smc mask> / STA $D418
              INC $23 / BNE / INC $24             (advance the pointer)
              LDA #$20 / STA $FFFA                (swap back)
              BIT $DD0D / RTI

`CMP #$1F` is the same in-stream terminator the proposal measured for V1.

### ⚠ THE FILE IMAGE LIES HERE — MEASURE, DON'T READ

Both handlers' operands are SMC slots left as `$EA` filler in the image, and
a plain STA-abs scan finds NO writer for them:

    $28BB/$28BC = $EA $EA   handlerA sample pointer
    $28C6       = $00       handlerA or_mask immediate
    $28D8/$28D9 = $EA $26   handlerB sample pointer
    $28DB       = $00       handlerB or_mask immediate

The static `ORA #$00` says mask `$00`; the write stream says `$30`. Reading
the image would have produced a confidently wrong `or_mask` for every V2
member. And the vector stores write LOW BYTES `$3D`/`$20` while this code
sits at `$28B8`/`$28D5` — so **the handlers are RELOCATED before they run**
(the Digi-Organizer C26 flavour). The running code is not in the file image
at all.

CONSEQUENCE for the extract: every V2 runtime value (sample pointers,
or_mask, rate latch, the relocated handler base) must come from
**siddump native capture** — `--peek-post-init`, `--memwatch-on-write`,
`--pc-watch` — never py65, and never the image byte
([[feedback_ground_truth]] third failure mode; the hook fired on exactly
this during the session and was right to).

## 2026-08-31 (later) — V2 PLAYBACK CORE FULLY DECODED (proposal §8 q1 CLOSED)

**The handlers are copied into ZERO PAGE.** `--pc-trace` settles it: the
executing PCs are $0020/$0022/$0025/$0027 and $0037/$003A/$003C (~205 hits
each in 2 frames), while $28A2 is just the `CLI / JMP *` idle loop. That is
why `$FFFB` reads `$00` — the NMI vector really is `$00xx`. Zero page is
chosen so the sample pointer can BE an instruction operand and be `INC`d
directly (below).

Read back with `--peek-post-init 0020-0060` (zero page is RAM — no banking
question, unlike `$FFFA` under the KERNAL):

    $0020  STA $3B            save A (never restored — the idle loop is a
                              bare `JMP *`, so a clobbered A is harmless)
    $0022  LDA $2A00          ⟵ the operand bytes ARE $0023/$0024 = the
                              16-bit sample pointer, self-modified in place
    $0025  CMP #$1F           in-stream terminator (same as V1)
    $0027  BEQ $0058          → LDA #$00/STA $23, LDA #$2A/STA $24 = LOOP
                              the pointer back to $2A00
    $0029  STA $40            raw byte → handler B's LDA operand LOW byte
    $002B  AND #$0F           LOW nibble
    $002D  ORA #$30           ⟵ or_mask  (THE FILE IMAGE SAYS $00)
    $002F  STA $D418
    $0032  LDA #$3D / STA $FFFA      swap NMI vector → handler B
    $0037  BIT $DD0D / RTI           ack CIA2

    $003D  STA $56
    $003F  LDA $2699          ⟵ operand LO was written by A = table[raw]
    $0042  ORA #$30
    $0044  STA $D418
    $0047  INC $23 / BNE / INC $24   advance the sample pointer (ONE byte
                                     per PAIR of writes ⇒ 2 samples/byte)
    $004D  LDA #$20 / STA $FFFA      swap back → handler A
    $0052  BIT $DD0D / RTI

**Nibble packing, confirmed by reading the table**: `--peek-post-init
2600-262F` returns `00 ×16, 01 ×16, 02 ×16 …` — i.e. `table[b] = b >> 4`, a
256-byte high-nibble lookup at $2600. So the high nibble is fetched by TABLE
READ rather than four `LSR`s (cheaper in the NMI), and handler A's `STA $40`
is what indexes it.

So V2 = **2 samples per byte, LOW nibble first then HIGH**, two
vector-swapped zero-page handlers, `$1F` terminator, pointer self-modified in
the operand. NB Digi-Organizer's order is HIGH then LOW (proposal §2) — same
technique, opposite phase; the composer must not assume one.

Everything here is MUSICAL CONTENT the schema already has: the nibble stream
is the sample (FLAC sidecar, C7-C), `$30` is `DigiConfig.or_mask`, the
pointer/terminator/table/vector-swap are all MECHANISM and stay in the
composer.

## 2026-08-31 (later still) — THE RATE MODEL (proposal §8, `rate_cycles`)

CIA2 timer A latch, read by watching each member's OWN `STA $DD04`/`$DD05`
sites (`--pc-watch`, A sampled pre-instruction on a 3-byte store) and then
counting every runtime write to `$DD04` over 60 s:

| member | ver | init latch | distinct latches at runtime | model |
|---|---|---|---:|---|
| Boot_Zak_v2 | V1 | `$0072` (114c, 8643 Hz) | **1** | fixed |
| Spelling_Around | V2 | `$0042` (66c, 14928 Hz) | **1** | fixed |
| Lost_Patrol_v2 | V1 | `$008A` | 7 (`$A4 $9B $8A $B8 $AE …`) | per-event |
| Morbital | V2 | `$0068` | 10 (`$68 $7B $6E $8A $52 …`) | per-event |
| Morbital_plus | V2 | `$0068` | — | (same player as Morbital) |
| Embarassed_Emotions | V2 | `$00CF` | 7 (`$68` ×103, `$74` ×35, …) | per-event |

**Per-event pitch appears in BOTH V1 and V2, and so does the fixed-rate
case** — like `or_mask`, the rate model is a PER-MEMBER property, not a
version property. Latch high byte is `$00` on all six.

Maps onto the landed schema with nothing new: `SampleInstrument.rate_cycles`
carries the per-sample default, a per-row rate override carries the pitched
events (the proposal's "optional rate override"). Carry the LATCH, not Hz —
the integer cycle count is the authored quantity (Principle §9 tiebreaker).

⚠ TWO TRAPS, both hit while measuring this:
- **The init latch is NOT the playback rate.** Embarassed_Emotions programs
  `$CF` at init and then uses it 4 times out of 165; its real workhorse is
  `$68`. An extract that reads the init store alone gets a rate that is
  wrong by 2× for most of the song. Read the runtime distribution.
- **The store SITES differ per member** ($08CE/$08D4 on Morbital,
  $08DA/$08E0 on Embarassed + Spelling, $0CA0/$0CA6 on Boot_Zak,
  $08D2/$08D8+$2854 on Lost_Patrol). Watching one member's PCs against
  another's image returns a plausible WRONG latch — it did here, reporting
  `$7E70` and `$486F` before the sites were scanned per member. Locate the
  store in each image first; never generalise an address.
- Cross-check that validates the whole method: Boot_Zak's latch `$72` = 114
  cycles and its dominant measured inter-write delta is 114c ×362,052.

## 2026-08-31 — THE RASTER BURST IS ONE MEMBER (proposal §8 q2 ANSWERED)

§8 asked: "the Rayden raster-burst mode — per-member schedule, or a fixed
part of the V1 player?" **Neither: it is ONE MEMBER of 17.** Census over all
carriers, 30 s each, share of inter-write deltas at 63 ±2 cycles (the PAL
raster line):

    Boot_Zak_v2 (V1)   21.1%      <-- the only carrier
    everyone else      <= 0.7%    (14 of 16 are 0.0-0.1%)

Boot_Zak_v2 runs its 114-cycle CIA NMI AND a 63-cycle per-rasterline burst
concurrently; that is the stride-$10 unrolled run at $2200-$2498. It is also
the member the proposal RE'd, which is exactly why the burst read as "a
second pacing topology within V1" — a one-carrier feature seen through the
one member that was disassembled.

CONSEQUENCE: the composer needs the CIA-NMI path for 16 of 17 members, and
the burst for Boot_Zak_v2 alone. Do not design the family around it.

### ⚠ METHOD — two plausible detectors were WRONG first; recorded so the
### next reader does not re-derive them

1. **"share of deltas in 55-70c"** — flagged Spelling_Around at 42.7%. FALSE
   POSITIVE: its programmed latch is `$42` = 66 cycles, so that window is its
   own NMI rate. A fixed cycle window cannot separate "burst" from "a member
   whose latch happens to be fast".
2. **"deltas not explainable by any programmed latch"** — flagged 15 of 17.
   FALSE POSITIVE twice over: the unexplained mass is inter-burst GAPS
   (263c, 488c — longer than any latch, i.e. silence between samples), and
   the latch set itself was polluted by non-digi `$DD04` writes (it reported
   a "5-cycle latch" for Popel, which is physically impossible).
3. **A 63 ±2 population** — physically grounded (one PAL rasterline), and it
   separates with a 30x gap. Use this one.

GENERAL LESSON, worth more than the answer: both wrong detectors were
THRESHOLDS over a derived quantity; the right one is a PHYSICAL CONSTANT of
the machine. When a census needs a magic number, suspect it.

## 2026-08-31 — V2's DATA MODEL, COMPLETE (the family is extract-ready)

Found by pc-tracing and grepping the trace for the WRITERS of each state
byte, rather than by reading the image (which is a pre-relocation template).

### The trigger routine — $08B3, called per sample event

    $08B3  LDY $F2                  ; sample index
    $08B5  LDA $1C00,Y -> STA $23   ; sample start pointer LO
    $08BA  LDA $1C01,Y -> STA $24   ; sample start pointer HI  (= the NMI's
                                    ;   self-modified operand, see above)
    $08BF  LDA $1C20,Y -> STA $59   ; second pointer LO  (end / length)
    $08C4  LDA $1C21,Y -> STA $5D   ; second pointer HI
    $08C9  LDY $F3                  ; rate index
    $08CB  LDA $1C60,Y -> STA $DD04 ; CIA2 timer-A latch LO
    $08D1  LDA $1C61,Y -> STA $DD05 ; latch HI
    $08D7  LDA #$81 / STA $DD0E     ; start timer + arm NMI
    $08DF  RTS

⚠ **$08CE/$08D4 are NOT init code.** They are this subroutine, called once
per event — which is exactly why the "init latch" is unrepresentative
(above): it is just the first call. Anything that reads them as init is
reading one sample's rate and calling it the member's rate.

### Parallel tables (Morbital), all Y-indexed with stride 2

    $1C00 / $1C01 , Y=$F2   sample START pointer (lo,hi)
    $1C20 / $1C21 , Y=$F2   sample END pointer   (lo,hi)
    $1C60 / $1C61 , Y=$F3   CIA2 latch = PLAYBACK RATE (lo,hi)

Observed: `$F2=0` → start `$2A00`, end `$2A00`; `$F3=$30` → latch `$0068`.
The `$2A00` the NMI's terminator branch resets to is therefore the CURRENT
sample's start, reloaded — not a fixed base.

### The score — a command byte stream at ($F0),Y

    $0867  LDA ($F0),Y      ; next score byte
    $0869  CMP #$FF         ; $FF = end / loop
    $0879  BPL $0899        ; < $80 -> RATE path ; >= $80 -> SAMPLE path
    $0899  ASL A / STA $F3  ; rate index (byte $18 -> $30, which is exactly
                            ;   the Y the trigger routine then uses)
    $089D  LDA ($F0),Y      ; following byte -> $07   (duration)
    $08A3  INY / TYA / CLC  ; advance the stream pointer

`$F0/$F1` is the score pointer, seeded at $082B from `$0826/$0827`. So the
score is the proposal's predicted **(sample, rate, duration) event stream**,
encoded as a command-byte stream with a `$FF` terminator — high bit selects
sample-vs-rate, and each command is followed by its duration byte.

### How this maps to the LANDED schema — still nothing new needed

| engine fact | USF |
|---|---|
| sample start/end pointers ($1C00/$1C20) | the PCM window → FLAC sidecar (C7-C) |
| latch table ($1C60) | `SampleInstrument.rate_cycles` + per-row override |
| score stream at ($F0),Y | the digi voice's ROWS (instrument + rate + duration) |
| `$30` or_mask, `$1F` terminator | `DigiConfig.or_mask`; terminator is mechanism |
| zero-page handlers, table lookup, vector swap, SMC pointer | composer mechanism |

**V2 is extract-ready.** Every musical degree of freedom has a home and the
composer keeps every mechanism.

## 2026-08-31 — ONE SEQUENCER, TWO PLAYBACK CORES (the V1/V2 label dies)

The sequencer is located by a signature that assumes nothing about the
version: a `JMP reset / JMP tick` head whose tick opens with the duration
countdown `DEC zp / BEQ +1 / RTS`. Run over all 17 carriers it finds **13**,
and nine of those are sidid `Rayden_Digi_V1`:

    found (13)   1970s_style_Hammond_Organ $0820  4_Ever_Young_2SID   $0840
                 Cyclones_Birthday        $0820  Embarassed_Emotions $0820
                 Fast_Moving              $0820  Im_So_Excited-I_Just $0820
                 Lost_Patrol_v2           $0820  Lost_Super_Scrotum   $0820
                 Morbital                 $0820  Morbital_plus        $0820
                 Panzer_im_Kopp           $2620  Popel_Premiere_2SID  $0820
                 Spelling_Around          $0820
    not found (4) Boot_Zak_v2, Knusprig_Sampl_Checka,
                  Smooth_Mumu_Operating, Trinkhoffs_and_Doenerpuste

So the family splits as **one score/sample/rate model + (at least) two
playback cores**, not as two engines. What sidid calls V1 vs V2 is the CORE
(unrolled raster burst vs vector-swapped NMI handlers), and the raster-burst
census already showed that burst has exactly ONE carrier. The build must
branch on the measured core, never on the version string — the §8 guard
above now has a measurement behind it.

⚠ The head is NOT at the PSID load address on every member: Spelling_Around
loads at `$0801` with the module at `$0820`, and Panzer_im_Kopp's module is
at `$2620`. Locate it; do not compute it.

## 2026-08-31 — THE EXTRACT, AND WHAT THE WRITE STREAM PROVES

### The sequencer, decoded from its own operands

    head+0  JMP reset      reset:  clear sample/rate/block vars, load the
    head+3  JMP tick               score pointer from head+6, set dur = 1
    head+6  score start pointer (lo,hi)
    head+8  loop-back pointer   (lo,hi)

`tick` is called from the member's raster IRQ (Morbital: from 2 of its 4
multispeed slots ⇒ a measured 2.0025 ticks/frame). It counts the duration
down and, on expiry, decodes the next command:

    byte >= $80   SAMPLE: sample# = byte & $0F, then a RATE byte follows
    byte <  $80   RATE only: re-trigger the CURRENT sample at a new pitch
    then          a DURATION byte, in ticks ($00 = 256)

Every command ends in the trigger, so **a rate-only command is a full
re-trigger** — every event is a note-on. Two-level members
(Embarassed_Emotions, Spelling_Around) put an ORDERLIST of block indices in
front of this, each entry indexing a word table of block pointers; `$FF`
ends a block, `$FF` in the orderlist reloads from head+8. Single-level
members (Morbital) run one block that `$FF` loops directly.

Two SMC knobs ride the sample path and are simulated, never modelled:
Morbital patches the LATCH TABLE BASE (`LDX #$60 / STX <operand>`),
Embarassed patches a rate-index BIAS (`ADC #imm`, $0C for samples 0-1 and
$00 above — a per-sample rate-table bank), Spelling has both patch stores
neutered to `BIT` and a fixed latch immediate. All of it collapses into the
resolved per-event latch.

### The sample table's second word is a LOOP pointer, not an end pointer

`(start, loop)` word tables, both indexed by sample#×2. Playback runs from
`start` to the in-stream `$1F` terminator, then reloads the pointer from
`loop`. That target is either DATA (a sustain loop — Morbital's sample 1
plays $2A02.. then loops $3200..) or **the terminator byte itself**, which
makes the sample a ONE-SHOT: the handler then re-terminates every NMI and
the voice is silent until the next trigger (every Spelling sample, and
Embarassed's 2-6). Morbital's sample 0 is a 1-byte `$99` + terminator — a
constant level 9, i.e. the tune's silence.

### The latch table is a 12-TET TUNING TABLE

`$1C60` (Morbital) / `$0F00` (Embarassed) hold `$019E $0187 $0171 $015C
$0149 $0136 $0125 $0114 $0105 $00F6 …` — successive ratios 1.0588…, against
2^(1/12) = 1.0595. The score's rate byte is therefore a NOTE INDEX and the
digi voice is a pitched, melodic channel, not a drum track.

🔶 **OWNER QUESTION, not acted on.** The landed schema carries this as a
per-row `rate=$XXXX` latch override, which is what this extract will emit —
a genuine parameter (ordered, interpolable), so it is not the §7 forbidden
shape and needs no approval. But `SampleInstrument.rate_cycles` + per-row
latches spend a tuning table's worth of structure on magic constants, where
SID voices get `Pitch` + a `freq_table`. Carrying the digi voice as
note + digi tuning table would put both channels in ONE parameter space
(§9 test 4) and is what the §9 tiebreaker's "relationship over the frozen
measurement" points at. It is a schema change, so it is parked as a
question rather than taken.

### What the write stream proves (`verify_score.py`)

The model predicts the entire `$D418` stream, so the extract has a verdict
without a composer. CONTENT walks the measured stream and requires the
current event to explain every write until it breaks, and each break to be
either an insertion or the next event's onset; TIMING fits ONE
cycles-per-tick constant across all segments.

Measured over each member's FULL songlength (see the warning below — a 60 s
window gave a materially different, better-looking answer):

| member | digi writes explained | events | ticks/frame | residual p90 |
|---|---:|---:|---:|---:|
| Morbital (280 s) | 1,957,156 / 1,957,156 | 468 | 2.0017 | 0.151% |
| Morbital_plus (460 s) | 3,152,731 / 3,152,731 | 737 | 2.0004 | 0.140% |
| Spelling_Around (345 s) | 3,704,788 / 3,704,790 | 1388 | 1.1169 | 3.454% |
| Embarassed_Emotions (270 s) | 1,935,059 / 1,935,065 | 964 | — | ⚠ not corroborated |

Morbital and Morbital_plus land on their raster IRQ's two tick calls per
frame to within 0.09% — an independent confirmation of the whole chain
(score walk, sample tables, `latch + 1` NMI period, terminator ratio).

Spelling's fitted RATE reads ~12% low AND its residuals cluster around a
systematic ~3.4%, because its 67-cycle NMI period is short enough that VIC
badlines swallow interrupts; the residual SPREAD, not the absolute scale, is
what validates the score there.

### ⚠ THE 60-SECOND ANSWER WAS WRONG, AND IT LOOKED BETTER THAN THE TRUE ONE

At a 60 s capture all three of those members reported "every write
explained". At full songlength the same code lost alignment at 28-65% of
each song. The cause is a genuinely ambiguous case, not a model error: a
re-trigger INSIDE a long constant run of the outgoing sample is locally
invisible — the cursor sails past the true boundary and only breaks where
the run ends, so no candidate near the break is right. Morbital's silence
sample is one byte (`$99` + terminator), so its runs are tens of thousands
of writes long.

The fix is a TWO-PASS alignment: pass 1 fits the tick rate from whatever
aligns unambiguously, pass 2 uses it to place the hidden onsets, and pass 2
is kept only if it explains more of the stream. The consequence to remember
is that CONTENT and TIMING are then **not fully independent** — a member
leaning on the prior has a content result that partly assumes timing, which
is why `verify` reports `run_resolved_onsets`.

This is the project's "measure a digi member over its FULL songlength" rule
paying for itself (it was written for a different failure — a short window
landing in an idle intro). Note the shape: **the short measurement did not
look truncated or noisy, it looked CLEAN.** A partial capture of a looping
score reports a perfect prefix.

Embarassed passes CONTENT but 1.2% of its writes go through the insertion
path, because its dominant sample is a 1-byte constant AND its IRQ asserts
an idle level every frame — so event boundaries inside a silent run are not
pinned down and its durations/latches stay unverified. `verify_score`
reports this explicitly (`timing_ok`) rather than calling it a pass.

### Three engine facts the gate had to learn (all visible in the stream)

1. **Re-trigger phase.** The trigger does NOT reset the NMI vector. With
   handler B pending, B writes one STALE nibble (the previous sample byte's
   high nibble, still sitting in its own `LDA` operand) and INCs the
   pointer PAST the new sample's first byte — so the event starts at sample
   offset 2. Both phases occur throughout every member.
2. **Per-frame idle assertion.** Embarassed's raster IRQ runs
   `JSR <music play> / LDA <or_mask slot> / ORA #$0A / STA $D418 / JSR
   <digi tick>` — an idle-level write inserted into the sample stream every
   frame without touching the digi pointer. That is the schema's
   `DigiConfig.idle_level`; Morbital and Spelling have no such write.
3. **The NMI period is `latch + 1`.** Per-write deltas ALTERNATE (Morbital
   at latch $68: 96 / 219 for a 2-writes-per-3-NMI sample) because handler
   A reaches its `STA $D418` ~9 cycles later than handler B; only the
   pair-sum is a clean multiple. The `latch+1` model is what makes the
   timing fit land on exactly 2.0025 ticks/frame.

### or_mask is the MUSIC's filter mode, poked into the handlers

The DMC player's filter note-init at `$12A5`/`$12A7` (Morbital `$12A7`/
`$12A9`) does `LDA filtdef,y / AND #$0F / ASL ×4 / STA <handler A mask> /
STA <handler B mask>` — a C19-family wedge that re-points the canon
`$D418` mode|vol store into the digi's `ORA #imm` operands. So the mask is
literally the music's filter routing, carried through because the digi owns
the register. It is CONSTANT per member over the whole song (measured, all
four), which is why `DigiConfig.or_mask` is the right home — but the
extract MEASURES it and refuses on any member where it moves, rather than
assuming. A member whose filter defs disagreed would need a per-event
carrier.

### A latent USF round-trip bug the first digi EXTRACT surfaced

Building the objects (`to_usf.roundtrip`) immediately failed
`parse(write(x)) == x`: the shared orderlist grammar rule hands back a
per-entry `None` for every absent transpose/voiceinc modifier, `voice_block`
collapses those to `[]`, and `digi_voice_block` did not — so a digi voice
parsed as `transposes=[None]*n` while any extract CONSTRUCTS it as `[]`.

`usf_spec_lint` structurally cannot see this: its round-trip starts from a
PARSED object, so it compares `[None]*n` with itself and passes. It only
bites when something builds an Orderlist directly — which, before Rayden,
only Digi-Organizer's `to_usf` did, and it never compared. Fixed in
`src/usf/parser.py`; 12,731 stored `.usf` still parse and `usf_spec_lint` is
clean. Worth remembering as a shape: **a writer/parser asymmetry is
invisible to any check that starts from the parser's own output.**

### ⚠ `--pc-watch` UNDER-COUNTS on an NMI-paced member (ledger C36 corollary)

Counting sequencer calls with `--pc-watch` gave 1.79 ticks/frame where the
write stream proves 2.0025 — a systematic ~10% loss. C36's execution
discriminator needs three consecutive ascending bus reads, and an NMI firing
every ~105-210 cycles regularly lands between a watched instruction's opcode
and operand fetches, breaking the signature. There is deliberately no
tick-rate probe in `extract.py` for this reason; the rate comes out of the
timing fit instead. (The tick's own entry is additionally invisible to
pc-watch: `DEC zp` is 2 bytes and its third bus read is the zero-page
operand, not PC+2 — watch the head's 3-byte `JMP` instead.)

## OPENER FOR A FRESH SESSION (written 2026-08-31)

⚠ An opener rots — backlog item 18's had to be banner-marked SUPERSEDED.
THIS FILE is the durable entry point; the block below is a convenience.
Before pasting it, check that the ✅ marks in "NEXT" below still match
reality, and re-date or delete this block when V2's extract lands.

▎ Continue the Rayden_Digi migration (phase 3 of
▎ docs/digi_parametrization_proposal.md). Read
▎ pipelines/rayden_digi/RE_NOTES.md FIRST — the player is decoded, the
▎ five RE questions are closed, and the extract is built and gated.
▎
▎ The extract (extract.py) + its ground-truth gate (verify_score.py) are
▎ done: 3 of the 4 sidid-"V2" members explain their ENTIRE $D418 stream.
▎ Next is to_usf.py (NEXT item 7), then the 9 other members the locator
▎ already finds — they are sidid "V1" but run the SAME sequencer, and
▎ only their playback CORE is undecoded (decode_core refuses anything
▎ outside zero page, so it will say so). Boot_Zak_v2 additionally needs
▎ a raster-burst path and is the ONLY carrier of it.
▎
▎ Non-negotiables, all of which cost time to learn:
▎ - The file image LIES. V2's handlers are copied to zero page and their
▎   operands are $EA filler; the static ORA says $00 where the runtime
▎   says $30. Every value comes from siddump (--peek-post-init,
▎   --pc-watch, --memwatch-on-write), never py65 and never an image byte.
▎ - Locate every store PER MEMBER. Watching one member's PCs against
▎   another's image returns a confidently wrong answer.
▎ - Measure over the FULL songlength. A short window on a bursty digi
▎   reports a constant value and reads as a stuck master volume.
▎ - §8 GUARD: no rayden_v1/rayden_v2 branch in the composer, and no
▎   "detect V2 -> call the Digi-Organizer emitter". Branch only on
▎   technique/or_mask/rate_cycles/score. All three of those vary per
▎   MEMBER and cut across the V1/V2 line anyway.
▎
▎ The schema is landed and needs nothing new — but the per-row
▎ `rate=$XXXX` override has NO producer and no corpus member, so Rayden
▎ is its first real user. Round-trip it early.
▎
▎ Verification: split the stream by $D418 ownership — music Mode 1 flat,
▎ digi Mode 2 cycle-strict (proposal §5).
▎
▎ Open design question, unmeasured: Digi-Organizer's members are
▎ digi-only, so nothing has tested a SHARED music+digi init. Rayden's
▎ music and digi init come from one routine. Settle it on a real member
▎ before writing the composer's init path.

## NEXT (in order, updated 2026-08-31 after the extract landed)

1. ~~Measure the V2 relocation~~ ✅ zero page.
2. ~~Confirm the nibble packing~~ ✅ `table[b]=b>>4`, low-first.
3. ~~The CIA2 latch (playback rate)~~ ✅ MEASURED; and the table is 12-TET.
4. ~~The sample TABLE / score~~ ✅ MAPPED and decoded.
5. ~~V1 raster-burst~~ ✅ ANSWERED. ONE carrier in 17.
6. ~~Extract~~ ✅ `extract.py` + `verify_score.py`; 3 of 4 V2 members pass
   both checks against the write stream.
7. **`to_usf.py`** — `digi {}` + `sample_instrument` + a `digi_voice` whose
   rows are (instr, `rate=$XXXX`, duration). Two-level members map straight
   onto orderlist+patterns; single-level ones are a one-entry looping
   orderlist. Rayden is the FIRST producer of the per-row `rate=` override,
   so round-trip it through `usf_corpus_check` + `usf_spec_lint` early.
   ⛔ **BLOCKED on backlog item 38 for 3 of the 4 gated members**: the
   sample LOOP POINT has no home in `SampleInstrument`, and Rayden's engine
   uses all three forms (loop-to-start / one-shot / attack+sustain loop).
   Parked as an owner decision, NOT worked around via `params`. A writer can
   serve one-shot-only members (Spelling_Around) meanwhile.
8. **Run the locator + gate over the other 9 located members** (all sidid
   V1). Their playback core is not yet decoded — `decode_core` refuses
   anything outside zero page — so expect the refusal to name the work.
9. **The 4 members with no head match** (Boot_Zak_v2, Knusprig_Sampl_Checka,
   Smooth_Mumu_Operating, Trinkhoffs_and_Doenerpuste): find out whether the
   sequencer is a variant shape or genuinely different.
10. The composer, and with it the §5 verification split. NOTE the measured
    complication: in Embarassed the DIGI ENGINE itself writes `$D418` from
    the raster IRQ every frame (the idle level), so "the digi owns $D418"
    holds but "one writer" does not — the composer must reproduce that
    write's placement, and it is Mode-2 signal.

## Verification (from the proposal §5, unchanged)

Split the captured stream by register ownership: the digi owns `$D418`
exclusively during play (the music player's `$D418` stores are patched away —
the C19 static-$D418 family; Popel's chip-1 probe already reads
`master_vol_static: 9`, which is the digi's IDLE LEVEL written once by init,
not a static master volume). Music verifies Mode 1 flat, digi verifies Mode 2
cycle-strict.

⚠ Measure any digi member over its FULL songlength. A short capture lands in
an idle intro and reports a CONSTANT value, which reads as a stuck master
volume rather than a sample (hit on Popel, 2026-08-31; backlog 28).
