# SIDfinity Plan — Pointer

This file used to hold the project's top-level development plan. That
document (dated 2026-04-09) is now historical and has been moved to
[`deprecated/old_docs/PLAN_2026_04.md`](../deprecated/old_docs/PLAN_2026_04.md).

It still captures the project's long-term **vision** (text/MP3/MIDI →
neural net → Universal Symbolic Format → SIDfinity player → playable
`.sid` files on real C64 hardware), so it's worth reading if you want
the original framing.

## Current operational plan

The plan has split into two living documents:

- **[`canary_picker.md`](canary_picker.md)** — the breadth-first
  migration corpus. One canary SID per engine family in HVSC's top 50,
  ~84% of HVSC by volume. Each canary lands byte-exact through the
  per-engine pipeline at `pipelines/<family>/<engine>/`.

- **[`refactor_1_remaining.md`](refactor_1_remaining.md)** — the
  composer-unification refactor. Deferred until the canary corpus is
  rich enough that designing one engine-blind universal composer
  doesn't overfit to today's five engine families. Trigger condition
  documented in that file.

The current per-engine working conventions (extract path, verify
modes, tools, memory layout) live in [`../CLAUDE.md`](../CLAUDE.md) —
that file is what you should read first when sitting down to work.
