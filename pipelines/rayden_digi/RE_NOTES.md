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

## NEXT (in order)

1. **Measure the V2 relocation**: `--peek-post-init` over the handler pages
   to find where the two handlers land and read their PATCHED operands
   (base, sample pointer, or_mask, CIA latch). That closes proposal §8's
   "V2 bit layout/pacing".
2. **Confirm the nibble packing** from the running handlers — handlerA does
   `AND #$0F` (low nibble) but handlerB has no shift in the image copy;
   resolve against the relocated code, not this one.
3. **V1 raster-burst**: measure which members use it and whether it is a
   fixed part of the player or per-member (proposal §8 open question 2).
   Boot_Zak_v2's stride-$10 run at $2200-$2498 is the anchor.
4. Only then: extract → `digi_voice` + `sample_instrument` rows, reusing the
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
