# DMC V6 — reverse-engineering notes

**Status:** player RE first pass DONE (2026-06-21). Extract + composer NOT started.
Representative: `MUSICIANS/T/The_Syndrom/DMC_V6_note.sid` (The Syndrom = the DMC
author; load/init=$1000, play=$1003). Disassembly:
`pipelines/dmc/v6/dmc_v6_note/disassembly.s` (seed + this annotation).

## What V6 is

- **Internal/unreleased DMC version** by Brian + The Syndrom/TIA ("never publicly
  released, 7-8 rasterlines CPU" — research.md). 16 SIDs in HVSC #84 (9 by The
  Syndrom himself). sidid sig `DMC_V6.x`.
- **A genuinely separate player** from V4/V5 (fingerprint census: ~0.01 Jaccard to
  every other DMC family — "different player entirely"). So, like V5 vs V4, it
  needs its own extract + composer; NOT a config variant of v4/v5.
- BUT its **musical degrees of freedom are the same DMC shape** v5 already models
  (3-voice orderlist+pattern, per-inst ADSR/PW/wave-prog/filter, 96-entry freq
  table, wave arpeggio, PW oscillator, pitch slide). So the USF representation
  should largely REUSE the v5 dimensions; only the binary lifter + the composer's
  emitted code are new.
- All 16 are single-subtune; standard DMC entry (init=base, play=base+3); most at
  $1000 (relocated: Techno_Heat $6000, Scene_plus $E000, Coma_Chase $FB8,
  Unafterous wrapper init $1BB0/play $1BC2).

## Player architecture (from DMC_V6_note disassembly)

**init ($1050):** zero the per-voice work block, set V1/V2/V3 ctrl + $D411 = $08
(test bit), $D418=$1F, $D417=$F2, RTS. A clean universal-reset init → handle via
`init_style='universal_reset'` + trichotomy (no priming to model). Matches the
V6 sidid signature exactly.

**play ($107B):** `DEC $100F` (the per-row tick divider, reloaded to 2 at $10E9);
BMI → new-row path ($10E9); else per-frame effect path. Runs `sub_1230` (V1
per-frame) + `sub_1339` (V2 per-frame) every frame; `sub_1086` is the V3 wave/arp
stepper.

### Per-voice state block $1010-$101F (the "zero page" work area)
| addr | V1 | V2 | V3 | meaning |
|---|---|---|---|---|
| $1010/$1011/$1012 | ✓ | ✓ | ✓ | note DURATION counter (DEC per row → 0 = fetch next) |
| $1013/$1014/$1015 | ✓ | ✓ | ✓ | ORDERLIST index |
| $1016/$1017/$1018 | ✓ | ✓ | ✓ | PATTERN position (Y into ($zp),y) |
| $1019/$101A/$101B | ✓ | ✓ | ✓ | new-note flag (set on note-on, consumed next frame) |
| $101C/$101D/$101E | ✓ | ✓ | ✓ | wave-program position (X into $16C3/$1757) |
| $101F/$1040 | V1 | V2 | — | current note (V3 note path differs — see sub_1086) |

zp pointers: V1=$F8/$F9, V2=$FA/$FB, V3=$FC/$FD; $FE/$FF = V1 pitch-slide accum.

### Song structure
- **Orderlists:** V1 $17EB, V2 $1804, V3 $1835 (indexed by $1013/$1014/$1015).
  `$FF` = end → wrap to index 0. Each entry is a pattern id Y.
- **Pattern pointer tables:** lo $184E, hi $185E (indexed by the orderlist's
  pattern id Y) → the pattern's address into ($zp).
- **Pattern stream** (read via ($zp),y, loop until a note):
  - byte bit7 **clear** ($00-$7F) = a NOTE → store + trigger note-on; advance.
  - byte `$FD`, next byte → DURATION ($1049/$104A/$104B → copied to $1010..$1012).
  - any other byte with bit7 **set**, next byte → INSTRUMENT ($104C/$104D/$104E).
  - `$FF` in the pattern (peeked after a note at $127B/$13EB/$10B8) = pattern end →
    INC orderlist index + reset pattern position.

### Per-instrument tables (22-entry / $16 stride, indexed by instrument Y)
| addr | → | meaning |
|---|---|---|
| $15FD | $D405/0C/13 | AD (attack/decay) |
| $1613 | $D406/0D/14 | SR (sustain/release) |
| $1629 | $1041/$1042 | PW oscillator accumulator INIT |
| $163F | $1045/$1046 | PW oscillator STEP (added per frame) |
| $1655 | $101C/$101D/$101E | wave-program start position |
| $166B | $1043 | pitch-slide DELAY (==1 → octave-up slide via $FE/$FF; counts down) |
| $1681 | $1048 + $D416 | (V2/filter) filter cutoff INIT |
| $1697 | $1047 | (V2/filter) filter sweep COUNT |
| $16AD | (filter step) | (V2/filter) added to $1048 each frame → $D416 |

**The FILTER is V2-owned** (sub_1339 $13A8/$1356) — only V2's note-on arms the
filter sweep ($1681/$1697/$16AD). Analogous to v5's V3-global filter, different
voice. $D417=$F2 fixed at init (res+routing).

### Wave / freq / PW tables
- **Wave program:** $16C3 = ctrl byte (waveform $11/$41/$81…); $1757 = note offset
  (arpeggio, added to the note → freq index). `$FF` in $16C3 = loop: $1757 at that
  slot gives the loop-back position (TAX, re-read). Same idiom as v4/v5 wave tables.
- **Freq table:** lo $153D, hi $159D — **96 entries** ($159D-$153D = $60). Indexed
  by (wave-offset + note). `+ $FE/$FF` detune. (Off-table reads possible here, like
  v5 — WATCH for idx>95 → would be the v6 analog of the offtable_freq work.)
- **PW oscillator:** $1041/$1042 accumulator += $1045/$1046 step each frame; index
  (&$1F, +$20 if negative) into $13FD (PW lo) / $143D (PW hi) → $D402/3 (V1),
  $D409/A (V2). A bounded triangle — the SweepEnvelope / PwmConfig shape (ledger D1).
- **Pitch slide:** $1314 — when $1043 delay hits 1, adds $159D[note+$0C] (octave-up
  freq hi) into $FE/$FF; $1044 counts 3 frames then SMC $12EB=$08.

### SMC to emit clean (CORE TENET — do NOT reproduce the mechanism)
- $12EB: operand of an LDA, written $28 (init) / $08 ($1333) / set by the slide —
  emit clean code producing the same $D4xx writes.

## Migration plan (mirrors V5)
1. ✅ Player RE first pass (this doc + annotated disassembly).
2. **Extract** `pipelines/dmc/v6/extract/engine_model.py` + `to_usf.py`: lift
   (freq_table, per-inst ADSR/PW/wave-prog/filter, 3 orderlists, patterns, wave
   programs) → USF, reusing v5's USF dimensions where they coincide. Dataflow-trace
   the data-table addresses (they relocate per SID).
3. **Composer** `pipelines/dmc/v6/composer_v6.py`: USF → our own clean engine →
   xa65 → PSID (CORE TENET: match the writelog, our own layout; clean init +
   no SMC). Check whether v5's composer can be parametrized vs a fresh one.
4. **Verify** `verify_v6` (trichotomy, full songlength) + factory (detect the 16,
   handle the 4 relocated) + batch.
5. Wire a canary into `tools/regression.py`; the 16-member batch is the milestone.

## Open questions for the next pass
- The V3 note path (sub_1086) differs from V1/V2 (no PW; uses $16C3/$1757 wave +
  $D40F V3 freq hi only?) — confirm V3's exact write set.
- Off-table freq reads (idx>95 into $153D/$159D)? If present, reuse `offtable_freq`.
- Exact pattern-end + orderlist-advance interplay (the $FF peek vs duration).
- The 22-entry instrument-table count vs how many instruments are actually used.
