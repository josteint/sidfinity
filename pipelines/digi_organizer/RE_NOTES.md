# Digi-Organizer — RE notes

Player RE from static disassembly, 2026-08-29 (Heavy-Beat standalone +
Piano_Fun_93 DMC-paired). Design + corpus census:
`docs/digi_parametrization_proposal.md`. 131 HVSC carriers, ONE canonical
core (both nibble-play signatures present in 131/131), small per-member
address shifts (Heavy-Beat seq tick $9089 vs Piano_Fun's copy $9087) →
locate every consumed site by signature, read tables from OPERANDS (C39).

## The core (runtime base $9000; standalone members load there directly,
## paired members' init COPIES it there)

Entry points: `$9000: JMP <core_init>` · `$9003: JMP <seq_tick>`.

**Core init** (`$9040` in Heavy-Beat): CIA2 TA latch = `$0070` (base rate,
per-member operand), TB=0, CRA=$11, CRB=$51 (TB counts TA underflows),
NMI mask $DD0D=$82; `$D418 = $18` (vol 8 | the held $10 filter bit =
`or_mask`); NMI vector → idle stub; state: order pos $9082=0, row $9083=0,
repeat ctr $9086=$91 (negative ⇒ first order fetch latches its entry's
repeat), speed ctr $9081 = init-speed byte `$908E`.

**Sequencer tick** (`$9089`, called once per raster IRQ by the driver):
- `DEC $9081; BMI` — speed counter; reload = the IMMEDIATE at tick+7
  (`LDA #$06` in Heavy-Beat — per-member; NB init uses `$908E`, steady
  state uses this immediate: extract BOTH).
- row pos == 0 ⇒ fetch orderlist entry at `$9200 + pos*2` (2-byte
  entries): byte0 = pattern# | `$FE` = HALT (arm idle NMI vector, stop) |
  `$FF` = LOOP to order pos 0. byte1 & $7F = pattern REPEAT count,
  latched via SMC (`$91C7`: stores into the `LDA #imm` reload at $91D1)
  ONLY when the repeat counter is negative ⇒ entry plays repeat+1 times.
- pattern base = `$9500 + pat#*32` (the `ADC #$95` immediate names the
  page base), SMC-patched into the row-fetch operand ($90FA/$90FB).
- row byte at base+rowpos: `$00` = rest row · `$FF` = pattern BREAK (end
  pattern now: row=0, DEC repeat, maybe advance order) · else = SAMPLE
  TRIGGER: row*4 indexes the sample table at `$92FC`:
    +0 start PAGE (SMC → both NMI handlers' `LDA $xx00` hi operands;
       lo pointers zeroed — samples are page-aligned)
    +1 end PAGE (exclusive; if start >= end, end = start+1)
    +2 CIA TA latch LO → `$DD04` = PER-SAMPLE RATE (pitched drums:
       Heavy-Beat plays one sample at latches $70/$80/$90/$A0)
    +3 pad (unused, $A0 fill)
  then NMI vector lo → the hi-nibble handler; playback starts.
- row advance: `INC $9083`, wrap at 32 → row=0, `DEC $9086`; negative ⇒
  order pos = (pos+1) & $7F.

**NMI handlers** (vector-swapped pair; ~1 nibble per TA underflow):
- HI: `STA $F8 / LDA $xxyy / LSR×4 / ORA #$10 / STA $D418 / INC ptr /
  vector→LO / ack / RTI`
- LO: `STA $F8 / LDA $xxyy / AND #$0F / ORA #$10 / STA $D418 / INC own
  ptr (page wrap: INC hi, CMP #endpage → past end: arm idle vector) /
  vector→HI / ack / RTI`
- Samples are NIBBLE-PACKED two per byte, HIGH nibble first; each write
  is `nibble | $10`. At sample end NOTHING is written (volume holds the
  last nibble) — `digi.idle_level` absent for this family.

## Standalone driver (Heavy-Beat `$9340`)
SEI; port=$35; IRQ vector $FFFE→wrapper; raster $81, $D011=$1B, CIA1 TA
stopped, raster IRQ enabled; A=0 JSR $9000 (core init); CLI; **RTS —
init RETURNS** (RSID play=$0000, IRQ-driven; unlike Rayden's
never-returning init). IRQ wrapper: ack $D019, `JSR $9003`, RTI.

## Per-member data to extract (all via located operands)
speed (init byte + steady immediate), orderlist ($9200 words), patterns
($9500+pat*32, truncated at $FF), sample table ($92FC 4-byte entries),
per-sample PCM pages (nibble-unpacked), base TA latch, the $D418 init
value (vol nibble + or_mask).

## USF mapping (schema landed 532b3931)
`digi { technique: volume_4bit, or_mask: $10 }` (no idle_level);
`sample_instrument N { sample, rate_cycles=<table latch lo> }` — same
PCM at different latches = distinct instruments sharing a FLAC;
`digi_voice` orderlist = pattern ids with `repeats[i] = byte1+1`,
`loop@0` / stop for $FF/$FE; patterns = 32 rows (or fewer when
$FF-broken), rest rows for $00, `iN` trigger rows otherwise; tempo =
the steady speed reload (duration 1 per row).
