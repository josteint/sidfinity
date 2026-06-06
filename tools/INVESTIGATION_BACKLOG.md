# Investigation tooling backlog

Durable list of diagnostic-tool ideas + ROI estimates. The premise: the
analysis pipeline is the long pole, not the code. A tool that saves 20
minutes per investigation pays back enormously across the migration
roadmap.

**Discipline:**
- After each non-trivial debugging session, ask "what tool would have
  collapsed this to <5 min?" Add it here (with rough estimate) or build
  it if it's <1 hour.
- If a tool starts producing misleading output, MODIFY or REMOVE it.
  Bad tools (silent failure, wrong-by-default, broken assumptions) cost
  more than no tool.
- When you build or modify a tool, update CLAUDE.md + the relevant
  memory so the next session knows it exists.

## Built (active)

| Tool | Use case | Memory pointer |
|---|---|---|
| `tools/find_first_divergence.py` | Locate first (reg, val) mismatch in writelog between orig + rebuild. Names voice/role. | [feedback_writelog_divergence_recipe](.claude/memory/feedback_writelog_divergence_recipe.md) |
| `siddump --memwatch HEX[,HEX...]` | Per-frame RAM snapshot at specific addresses. libsidplayfp-accurate (ground truth, not py65). Use for engine-state tracing. | (in this file + CLAUDE.md) |
| `tools/state_diff.py` | Wrapper around `--memwatch`: takes orig+rebuild SIDs + an address-mapping file, finds first frame where any mapped pair diverges. | (in this file + CLAUDE.md) |
| `tools/seed_disassembly.py` | Generate a labelled disasm from a SID's binary as the starting point for hand-annotation. | (migrate-hubbard-engine skill) |

## Backlog (not built yet)

| Idea | Use case | Rough ROI | Build estimate |
|---|---|---|---|
| **`siddump --play-aligned` / `--writelog-per-irq`** (PRIORITY) | Hook the PSID `play()` vector and emit one writelog "frame" per IRQ invocation, not per `cyclesPerFrame`. ALSO let `--memwatch` capture at IRQ boundaries. Eliminates Trap C at the source (`feedback_verification_modes`). | Very high — Trap C burned a full Hawkeye sub 10 investigation. Without this, state_diff stays a hint-only tool. | 2-3 hours libsidplayfp overlay |
| `tools/voice_writelog.py` | Filter writelog to one voice; auto-attribute writes to likely effects (AD/SR write = nolengset; freq-only = glide; etc.) | Saves 10-15 min/session on "which effect produced this write?" | 30 min |
| `tools/pattern_stream_decode.py` | Given (SID, engine config, subtune, voice), decode pattern stream as human-readable command list | Saves 30-60 min/session on pattern-dispatch bugs | 1-2 hours, engine-specific |
| `tools/disasm_diff.py` | Side-by-side compare orig disasm region vs composer emitter, with state-name alias substitution | Saves 15-20 min/session on effect comparisons | 1-2 hours |
| State map generator | Auto-derive orig↔rebuild address map from xa65 labels + a per-engine annotation file (so state_diff.py becomes one-shot) | Saves 5-10 min/session and removes a footgun (wrong manual maps) | 1 hour, ongoing per-engine annotation |
| `siddump --memwatch-events` | Snapshot RAM addresses on a CPU event (PC enters range), not per-frame. For tracing when state changes mid-frame. | Very high for SMC and conditional updates | 1 hour C++ |
| `tools/effect_chain_profiler.py` | Attribute each `$D4xx` write to the routine that produced it (via PC-trace cross-reference). Output: "$D408 = $47 written by nolengset at PC $7CXX." | Definitive answer to "which routine produced this write." Saves ~20 min/session. | 2-3 hours |
| Pattern-stream USF-vs-binary verifier | Verify USF's extracted pattern stream byte-matches what the engine would have read from HVSC's binary | Catches USF extraction bugs at extract time, not rebuild time | 1 hour per engine family |

## Hurt list (built tools that didn't earn their keep — to be modified or removed)

| Tool | Why it hurt | Resolution |
|---|---|---|
| `tools/state_diff.py` (mitigated, not removed) | Misleads when siddump frame buckets are misaligned with PSID `play()` invocations (Trap C). Hawkeye sub 10 session: reported a `nootcount[V1]` "divergence" at f277 that turned out to be IRQ-count drift — orig had 0 IRQs in that siddump frame. Real bug was elsewhere. | KEPT — still useful for HINTS when cross-checked against writelog. Added explicit caveat in docstring + runtime warning in output. Permanent fix: build `siddump --play-aligned` (PRIORITY in Backlog above) so memwatch samples at IRQ boundaries. Until then: any state_diff "divergence" MUST be cross-checked against `find_first_divergence.py` before trusting. |

When entering: write what the tool was supposed to do, what it actually
did (silent failures, wrong defaults, etc.), what to do (delete? fix?
add a tripwire?).

## Process rules

- **Every entry in "Backlog" should have a session that wanted it.** No
  speculative additions. Examples: "If we'd had X, the Hawkeye sub 1
  V2 freq divergence would have taken N minutes instead of N hours."
- **Every entry in "Built" must point to its memory / CLAUDE.md home.**
  If a future session doesn't naturally find the tool, it might as well
  not exist.
- **Promotions and demotions happen here.** When a backlog idea gets
  built, move to Built. When a Built tool hurts more than helps, move
  to Hurt list with the reason.
