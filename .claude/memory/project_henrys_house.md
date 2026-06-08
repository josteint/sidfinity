---
name: henrys-house-engine
description: "Chris Murray's Henrys_House — stripped single-voice Companion variant. Instruction-sequence exact via pipelines/companion/henrys_house."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`pipelines/companion/henrys_house/` — fifth Companion strain. Chris
Murray's Henrys_House, a stripped single-voice variant. Instruction-sequence exact:
434/434 cycle-ordered writes match.

## Engine semantics

- **1 voice only.** Engine has no V2/V3 logic at all.
- **Tempo hardcoded to 8.** Tempo gate uses `CPX #$08` immediate, not
  `CPX abs` like other Companion strains.
- **$FF restart-init.** When $FF is read, the engine jumps to its
  init routine which writes `$D418=$0F` and zeroes the V1 position
  counter, then RTS. The $FF tick produces a `$D418=$0F` SID write
  but plays NO note that tick — different from bowden_canonical's
  "set pos=1 + play orderlist[0] in same tick".
- Same byte encoding as bowden_canonical: `$00-$7F` NORMAL_NOTE,
  `$80` REST, `$81` SKIP.
- Freq table identical to Clever Music's (engine constant).

## Implementation notes

- Mini-strain (~370 LOC including extract+codegen). Engine is small
  enough to be standalone rather than parameterising bowden_canonical.
- USF requires 3 voice blocks per the grammar — padded with empty
  placeholder voices. The codegen ignores V2/V3 and emits only V1
  logic + data.

## Related

- [[project_bowden_canonical]] — closest sibling; similar note encoding
- [[project_clever_music]] — shares the same freq table
