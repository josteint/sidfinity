# Deprecated sub-agent

The `sidfinity` sub-agent that pre-briefed a Sonnet delegate with SIDfinity
context. Briefly: spawn-able via the `Agent` tool with
`subagent_type=sidfinity`, gave the sub-agent a list of "READ THIS FIRST"
files and key paths.

Two reasons it's deprecated:

1. **Stale content.** The briefing referenced files that no longer exist
   at the cited paths (`src/usf/format.py`, `src/converters/...`,
   `src/sid_compare.py`, `docs/formal/procedure.md`) and pointed at the
   pre-byte-exact diagnosis memory (`project_hubbard_diagnosis.md`, also
   now under `memory/_deprecated/`). A delegate spawning this agent would
   get briefed on a codebase that no longer exists.

2. **Not used in practice.** The interactive workflow is the main session
   (Opus) doing the work directly. The sub-agent was never invoked in
   recent sessions. If/when delegation to a Sonnet worker becomes useful
   again, rebuild the briefing from current `CLAUDE.md`.

If you want to revive it, move the file back up one level and rewrite the
"BEFORE DOING ANYTHING" + "Key Files" sections to match the USF v2 layout
in `pipelines/hubbard/`.
