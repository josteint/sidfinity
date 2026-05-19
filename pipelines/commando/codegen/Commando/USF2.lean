/-
  USF2.lean — instrument-as-program schema (Phase 1 of the refactor).

  See docs/usf_instrument_program_plan.md.

  Goal: replace the typed-fields USFInstrument (which leaks Hubbard
  engine knowledge — `dynamicFreqEntries`, `voiceScratch`,
  `preserveNoteFlags`, etc.) with a behavioral spec: each instrument
  is a list of per-frame SID-register-write events, where each write's
  value comes from one of a small set of named SOURCES.

  This file sandboxes the new schema alongside the existing USF.lean.
  No production codegen wires up to it yet. Phase 2 onwards will:
    - hand-encode one Commando instrument here,
    - write a minimal Codegen2.lean that emits 6502 from one instrument,
    - verify the writelog matches the original frame-for-frame.

  Empty for now — Phase 1.1+ fills it in.
-/

namespace USF2

end USF2
