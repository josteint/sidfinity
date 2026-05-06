# Deprecated Lean files (USF v1 / v2 era)

These were the codegen, verification, and CPU emulator files from earlier
attempts. The active pipeline lives entirely under `src/formal/`'s V3 set
(`USFv3.lean`, `CodegenV3.lean`, `CommandoV3.lean`, `SidgenV3Main.lean`,
plus shared infra `Asm6502.lean`, `PSIDFile.lean`, `SID.lean`).

| File | What it was |
|---|---|
| `Codegen.lean` | V2 per-song 6502 codegen (replaced by `CodegenV3.lean`) |
| `CommandoData.lean` | V1 hand-coded Commando data (replaced by generated `CommandoV3.lean`) |
| `CommandoMain.lean` | V1 entry point |
| `Compile.lean` | V1 compiler from a USF-ish AST |
| `Effects.lean` | V1 effect semantics |
| `Main.lean` | V1 main entry |
| `Properties.lean` | V1 formal properties / proofs |
| `SidgenMain.lean` | V1 sidgen entry |
| `State.lean` | V1 voice/song state |
| `CPU6502.lean` | Cycle-precise 6502 emulator (used by the V1 verifiers below) |
| `ValidateModel.lean` | V1 model validator |
| `VerifyMain.lean` | V1 verification main |
| `CompareMain.lean` | V1 SID-vs-SID comparator |

Resurrect anything from here only if there's a concrete reason. The V3
pipeline in `src/formal/` is the canonical implementation.
