---
source_url: index (see provenance_log.md)
fetched_via: research-player sweep (INTERRUPTED by session-token limit 2026-06-17)
fetch_date: 2026-06-17
author: research synthesis (Jostein Trondal session)
content_date: 2026-06-17
reliability: mixed — see per-file headers
---

# David Whittaker — research docs index

> ⚠️ **This sweep was INTERRUPTED.** The 2026-06-17 research-player run launched
> 6 cluster agents, but they were spawned as recursive `general-purpose` agents
> that fanned out into 30+ sub-agents and exhausted the session token budget
> before most of them could write their summaries. **Only one artifact was
> salvaged** (a high-value one — see below). The skill has since been fixed
> (leaf-agent / no-sub-spawn constraint) so a clean re-run is safe. **Family
> state remains `LITTLE`** until the sweep is re-run.

## Engine identity (from the pre-existing `research.md`)

- **David Whittaker** — one of the most prolific C64 game composers. Hand-coded
  his music in 6502 (Supersoft tools), **not** a music editor; used a
  Music-Macro-Language style. Driver ported to NES / Amiga / Atari ST / CPC /
  ZX Spectrum with compatible data structures.
- **HVSC #84: 110 SIDs** tagged `David_Whittaker` (107 under MUSICIANS, 3 under
  GAMES). His player **evolved across years/games** → expect multiple driver
  variants (a key open question for the migration phase).

## What was salvaged

| File | What it is | Quality |
|------|-----------|---------|
| `src/Whittaker_David_Panther.asm` | **Full annotated disassembly** of *Panther* (David Whittaker, 1986 Mastertronic), ACME syntax, 1476 lines / 134 comments. "Reversed by dmx87". Includes the PSID header reconstruction, `init`/`play` entry points, and **named command handlers** (`cmd_Pulse`, `cmd_PulseHi`, `csetwave`, `ptempo`) — i.e. the command-dispatch playroutine. Reconstructs to a byte-identical SID via ACME `!to ...,plain`. | **primary** — a complete reconstructible player source for one Whittaker tune. The single best starting point for the migration `disassembly.s`. |

This one file is genuinely useful: it shows the Whittaker player as a
**command-stream interpreter** (per-voice command handlers dispatched from a
sequence), which matches the "MML / macro-language" description in `research.md`.
It is ONE tune's driver, though — Whittaker's routine varies across games, so it
characterises a variant, not necessarily the whole family.

## What is still missing (the sweep did NOT complete)

Almost everything the other 5 clusters were meant to gather was lost to the kill:

- **CSDb / scene** — his scener page, any ripped driver source, version history.
- **GitHub / tools** — libsidplayfp / DeepSID detection notes; the dmx87 source's
  ORIGIN repo (the .asm is here but its URL was not recorded — find it).
- **Archive.org / interviews** — his documented MML workflow + cross-platform
  (Amiga/ST) data-structure writeups (those ports are often better documented
  and illuminate the C64 format).
- **Forums / wikis** — Codebase64 / Lemon64 / AtariAge threads on the routine.
- **HVSC docs + SIDId** — **how many sidid signatures exist for Whittaker**
  (= how many driver variants we must support). 4 local HVSC `DOCUMENTS` files
  mention him (Update00/02.hvs, Update_Announcements 20020817 + 20240630) —
  these were never read. THIS is the highest-value missing piece.
- **Disassemblies / articles** — more dmx87 (or other) disassemblies of OTHER
  Whittaker tunes, to diff variants; any scene-mag tech article.

## Next step

**Re-run `/research-player david_whittaker`** now that the skill enforces
leaf agents. The existing `research.md` + the salvaged `Panther.asm` +
`provenance_log.md` give the re-run a head start. Priorities for the re-run:
(1) the sidid variant count, (2) the dmx87 source's origin (likely more tunes
there), (3) cross-platform port docs, (4) read the 4 HVSC `DOCUMENTS` mentions.
