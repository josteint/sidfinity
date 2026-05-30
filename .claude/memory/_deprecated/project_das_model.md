---
name: Das Model v2 — Lean verified compiler
description: USF → .sid file via Lean 4 compiler. Engine-agnostic model. Ground truth = sidplayfp --writelog. Pipeline working end-to-end.
type: project
---

**Das Model v2** — universal SID music representation with verified compilation.

**Architecture (2026-05-02):**
```
Original SID → decompiler (Python, untrusted) → USF
USF → Lean compiler → .sid file (6502 player + data)
Verification: writelog(original.sid) == writelog(compiled.sid)
```

**Key principle:** The Lean model is ENGINE AGNOSTIC. Engine quirks (Hubbard's T[104+],
nested speed counters, GT2 pattern format) are resolved by decompilers into clean USF.
The Lean compiler takes universal USF and produces a .sid with embedded 6502 player code.

**Ground truth (CRITICAL):** ALWAYS sidplayfp --writelog. Never py65 or reimplementations.

**Current Lean files:**
- SID.lean: types (SIDReg, Instrument, Song, EffectChain)
- Asm6502.lean: 6502 instruction set, byte-level assembler
- PSIDFile.lean: PSID v2 header + binary serialization
- Codegen.lean: USF Song → .sid file generator (init works, play = stub)
- CommandoData.lean: real Commando data (13 inst, 31 patterns, 120 freq entries)
- State.lean, Effects.lean, Compile.lean: mathematical stream computation (Phase 1)
- Properties.lean: 7 theorems (5 proved, 2 sorry)

**Pipeline status:** End-to-end working — Lean generates a valid .sid that sidplayfp plays.
Init routine correct (volume, ctrl clearing). Play routine needs implementation.

**Next:** Implement 6502 player in Codegen.lean (duration counter, pattern reader, register writes, gate-off, orderlist).

**Roadmap:** docs/PLAN_dasmodel_v2.md
