---
name: reference_audit_tool
description: src/usf/audit.py — PC-traced per-voice SID-write capture. Use for Rule 1 collapse audits when frame-level writelog conflates voices.
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`src/usf/audit.py` runs any SID through py65 with a SID-write
observer, capturing `(frame, PC, addr, value)` for every write to
$D400-$D418. Filters to one voice (0/1/2 via per-voice register
range) and optionally cross-references PCs against a disassembly
file for engine-instruction attribution.

## When to use

- **Per-effect Rule 1 audits** (see [[feedback_principle_first_analysis]]
  question 3): does effect X in engine A produce the same writes as
  effect Y in engine B? Plain frame-level writelog comparison
  conflates V1/V2/V3 writes on the same $D400-$D418 range. PC trace
  + voice filter is the disambiguator.
- New-engine effect-dispatch reverse-engineering — which 6502
  routine wrote which SID byte at which frame?
- Debugging codegen divergence — when the rebuilt SID's writelog
  diverges from the original, the tool tells you which voice and
  which engine PC produced each divergent write.

## Usage

    python src/usf/audit.py <sid> --subtune N --frames a:b \
        [--voice 0|1|2] [--disasm path/to/disasm.s]

Frame range is `start:end` (end-exclusive). `--voice` is 0-indexed
(0=V1). Subtune is 0-indexed (PSID convention).

## Validated

Reproduces the Human Race downslide Rule 1 COLLAPSE verdict
recorded in [[project_human_race_audit]] — V1 inst 6 (downslide-
only) frames 225-234 produce the same writes (write-for-write) as a Commando-engine
`freq_slide` rebuild.

## How to apply

Whenever you're about to audit an effect's writes for Rule 1
collapse and the frame-level writelog conflates voices, this tool
is the next step. Don't re-implement the py65 setup ad-hoc.

Related: [[feedback_usf_representation_principle]] is the principle
the tool serves. [[feedback_principle_first_analysis]] is the
checklist that names the moment to reach for it.
