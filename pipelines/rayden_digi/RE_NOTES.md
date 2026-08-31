# Rayden_Digi — reverse-engineering notes

**Status (head = current). Family OPENED 2026-08-31; no extract, no composer
yet.** This is phase 3 of `docs/digi_parametrization_proposal.md` (schema
landed 2026-08-29; Digi-Organizer, phase 2, closed at 39/39). 17 carriers,
all `MUSICIANS/R/Rayden/`.

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

## NEXT (in order)

1. ~~Measure the V2 relocation~~ ✅ done above (zero page).
2. ~~Confirm the nibble packing~~ ✅ done above (`table[b]=b>>4`, low-first).
3. ~~The CIA2 latch (playback rate)~~ ✅ MEASURED — see below.
4. ~~The sample TABLE / score~~ ✅ MAPPED — see below. V2 is extract-ready.
5. ~~V1 raster-burst~~ ✅ ANSWERED — see below. ONE carrier in 17.
6. Only then: extract → `digi_voice` + `sample_instrument` rows, reusing the
   Digi-Organizer path for V2.

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
