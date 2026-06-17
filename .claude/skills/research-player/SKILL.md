---
name: research-player
description: Research a C64 SID player engine online. Gathers documentation, source code, disassemblies, and format specs from CSDb, GitHub, Archive.org, forums, HVSC docs, and more. Saves everything to pipelines/<engine>/docs/.
argument-hint: [player-name]
user-invocable: true
allowed-tools: Agent Bash Read Write Glob Grep WebFetch WebSearch
effort: medium
---

# Research $ARGUMENTS Player Engine

You are researching the **$ARGUMENTS** C64 SID player engine to gather everything needed to build a decompiler and USF converter for it.

## Scope: GATHER + SUMMARISE only — NOT reverse-engineering (cost discipline)

This task collects external knowledge and summarises it. It does **not** reverse-
engineer the engine — that work belongs to the migration phase (`disassembly.s` +
the extractor), which redoes it properly, so doing it here just burns tokens twice.

- **DO:** fetch + read player source, format specs, manuals, sidid signatures,
  version history, and *existing* annotated disassemblies; summarise them into the
  docs; keep useful third-party source under `docs/src/`.
- **DO NOT:** run `siddump`/py65, disassemble binaries byte-exact, decode packed
  data, write emulators, or otherwise RE the engine yourself. If a claim needs RE
  to confirm, record it as an **OPEN with the exact trace to run later** — don't
  run it now. (`siddump`/py65 are out of scope despite `Bash` being available.)
- **Model:** launch the research subagents on **sonnet** (`model: 'sonnet'` in each
  `Agent()` call) — web research + summarisation is well within sonnet, and the
  parts that needed Opus were the RE we're deliberately cutting. Reserve Opus for
  the migration/RE phase. The orchestrating session can run at medium effort or lower.

## What we need (in priority order)

1. **Original player source code** — the 6502 player source. This is the holy grail: exact byte offsets, data format, playback logic.
2. **Other tools' parsers** — battle-tested implementations that already parse this format (SIDFactory II, CheeseCutter, GoatTracker import, libsidplayfp, VICE, DeepSID). These solved edge cases we'll hit.
3. **Format specifications** — byte-level data layout, version differences, feature flags.
4. **Annotated disassemblies** — people who've already reverse-engineered the player.
5. **Effect documentation** — exactly how each effect modifies SID registers per frame.
6. **Version/variant differences** — what changed between player versions.

## Where to search

Cast a wide net across ALL of these sources. Launch parallel research agents for maximum coverage:

### Primary sources (highest value)
- **CSDb (csdb.dk)** — the primary C64 scene database. Release pages, editor downloads, source code, comments with technical details.
- **GitHub** — search for repos containing parsers, editors, or tools that handle this format. SIDFactory II is open source and imports many formats.
- **Archive.org / Wayback Machine** — original author pages, scene group sites, old C64 documentation that's no longer live. Many 90s/2000s scene pages only survive here.

### Secondary sources (good technical detail)
- **HVSC DOCUMENTS/ directory** — HVSC ships technical docs about player engines alongside the music. Check our local copy at `data/C64Music/DOCUMENTS/`.
- **libsidplayfp source** — the reference SID emulation library, may contain player-specific handling.
- **Codebase64 wiki** — C64 programming reference, often has player analysis articles.
- **Lemon64 forums** — active C64 community, discussions about player internals.
- **Pouet.net** — demoscene database, productions often have detailed technical comments.

### Tertiary sources (fill gaps)
- **Usenet archives (Google Groups)** — comp.sys.cbm, comp.sys.cbm.c64 from the early 90s. Primary source material from when these players were new.
- **DeepSID** — online SID player with player detection notes and technical metadata.
- **YouTube** — demos of editors showing features, workflows, and edge cases that never get written down.
- **Russian/Eastern European C64 scene sites** — very active communities, sometimes have the deepest technical analysis.
- **SIDId signatures** — the exact byte patterns that identify player versions. Check `tools/sidid.cfg`.

## What to check in our own codebase first

Before going online, check what we already have:
- `docs/players/` — existing player analysis docs
- `src/sidid.py` — run against sample SIDs to see version detection
- `tools/sidid.cfg` — signature patterns
- `data/C64Music/DOCUMENTS/` — HVSC bundled docs
- Any existing parser code in `src/`

## Output

Save everything useful to `pipelines/<engine_snake_case>/docs/` as individual files with clear names:
- `{source}_player_source.md` — actual player source code or disassembly
- `{source}_format_spec.md` — data format specifications
- `{source}_parser_notes.md` — notes from other tools' implementations
- `{source}_forum_discussion.md` — relevant technical discussions
- `{source}_version_differences.md` — version/variant documentation
- `README.md` — index of all gathered docs with summary of what we found and what gaps remain

### Provenance (REQUIRED)

Every saved file MUST start with a provenance header:

```
---
source_url: <exact URL fetched, or "local: path/to/file" for local sources>
fetched_via: <"direct" | "wayback YYYY-MM-DD" | "curl" | "local read">
fetch_date: <YYYY-MM-DD>
author: <original author if known, otherwise "unknown">
content_date: <date of original content if known, e.g. "1993-03" for C=Hacking #5>
reliability: <"primary" (source code, disassembly) | "secondary" (analysis, forum post) | "tertiary" (wiki, summary)>
---
```

This ensures we can always trace back WHERE information came from, WHEN it was written, and HOW reliable it is. When two sources disagree, provenance lets us pick the more authoritative one.

Also maintain a `provenance_log.md` file that lists every URL attempted (fetched or failed) with status and date, so future research waves don't re-fetch the same sources.

## Strategy

### Phase 1: Check what we already have
Check the codebase first (existing docs, sidid detection, HVSC docs, any existing parser code).

### Phase 2: Broad sweep (parallel agents)
Launch 5-6 parallel background research agents, one per source cluster:
- CSDb + scene databases (CSDb, Pouet)
- GitHub + open source tools (SIDFactory II, libsidplayfp, CheeseCutter)
- Archive.org + Wayback Machine (historical docs, original author pages)
- Forums + wikis (Lemon64, Codebase64, Usenet/Google Groups)
- HVSC docs + SIDId + DeepSID
- Disassemblies + technical articles (C=Hacking, scene magazines)

**Launch each agent as a LEAF (non-recursive) worker.** The research agents are
spawned as general-purpose agents, which hold the `Agent` tool and will otherwise
recursively spawn their OWN helper sub-agents — a 6-agent sweep became 30+ live
agents and blew the session token limit (2026-06-17). There is no Write-capable
agent type that lacks the `Agent` tool, so this MUST be enforced at the prompt
level: the FIRST hard constraint below forbids sub-spawning, and it is not
optional. One cluster = exactly one agent that does all its own work. Keep the
sweep to **5-6 agents total** and do NOT launch follow-up waves that themselves
fan out.

**MANDATORY — every agent prompt MUST include these hard constraints** (a
separate Claude session may be editing the same repo concurrently):
- **You are a LEAF agent — NEVER spawn sub-agents.** Do NOT use the `Agent` /
  `Task` tool, and do NOT start background tasks or delegate to other agents.
  Perform ALL searching, fetching, reading, and file-writing YOURSELF within this
  single agent. (Research agents recursively spawning helpers caused a token
  blow-up + session-limit kill — one agent = one worker, no exceptions.)
- **Never run any `git` command** — no `restore` / `checkout` / `reset` /
  `add` / `commit` / `clean` / `stash`. If a tracked file (e.g. `hvsc84.db`)
  shows as modified, **leave it — it is not yours**. (A research agent once
  ran `git restore hvsc84.db` on the false premise that its read-only query
  had dirtied the file, reverting another session's live state — see
  `.claude/memory/feedback_subagents_no_git.md`.)
- **Write ONLY inside `pipelines/<engine>/docs/`, and only ADD new files** —
  never delete, rename, or overwrite an existing file (especially `research.md`,
  which is pre-existing context). Do not modify any other
  repo file or `pipelines/<other-engine>/`. Keep useful third-party source
  (player asm, format specs) under `pipelines/<engine>/docs/src/` so it's
  committed and the docs' `file:line` citations don't rot. Put large
  downloads / scratch in a FRESH `tmp/<engine>_research/` dir — do NOT touch
  any other `tmp/` subdir (another session may own e.g. `tmp/dmc_hunt/`).
- **Open shared SQLite DBs read-only**: `sqlite3.connect('file:hvsc84.db?mode=ro', uri=True)`
  — never a writable connection (it must not be flipped to WAL).
- The orchestrator (not the agents) writes `README.md` + `provenance_log.md`,
  so agents use distinct `{cluster}_*.md` filenames to avoid collisions.

**IMPORTANT:** Tell each agent to collect not just information but also **leads** — URLs, names, tools, files, or references that look promising but that the agent didn't have time to fully chase. Each agent should end its output with a "## Leads to follow" section listing these.

### Phase 3: Follow leads (iterative)
After all Phase 2 agents complete, review their findings AND their leads. This is the critical step most research misses.

For each promising lead:
- **A URL to a page not yet fetched** → fetch it
- **A tool that can be tried online** (e.g., Restore64.dev disassembler, online C64 emulators) → try it with a sample SID
- **A downloadable file** (disk image, editor release, PRG) → check if it contains README/docs
- **A person mentioned as knowledgeable** → search for their other work, personal pages, blog posts
- **A related project or tool** → search for its source code
- **A cross-reference to another release/page** → fetch that page

Launch a second wave of targeted agents to follow the most promising leads. Repeat if the second wave surfaces further leads, up to 3 waves total.

### Phase 4: Gap analysis
After all waves complete, assess what critical knowledge is still missing. Organize gaps into:
- **Fillable from our own binaries** — things we can discover by disassembling player code we already have (10,738 DMC SIDs, etc.). Note these but don't do the disassembly here.
- **Fillable from online sources we haven't tried** — suggest specific searches.
- **Probably unfillable online** — only discoverable through reverse engineering. These become the priority list for sidxray work.

### Phase 5: Save results
Save each find as a separate file in `pipelines/<engine_snake_case>/docs/`. Write a README.md summarizing:
1. What was found (with quality assessment)
2. What leads were followed and what they yielded
3. What gaps remain and how to fill them

## Following leads: what makes a good lead

A "lead" is a reference found during research that points to potentially valuable information not yet retrieved. Good leads to follow:

- **Specific URLs** mentioned in forum posts, comments, or docs that weren't fetched yet
- **Named tools or editors** that import/export the format — their source or docs reveal format details
- **Author names** — search for their other work, personal sites, blog posts, scene releases
- **Disk images or PRG downloads** — these often contain bundled README files, manuals, or example data
- **Cross-references between releases** — "this is based on V4 code" → find the V4 release page
- **Online interactive tools** — disassemblers, emulators, SID players that might expose player internals
- **Related formats** — if format X evolved from format Y, understanding Y illuminates X (e.g., JCH evolved from DMC)
- **Scene magazine articles** — C=Hacking, Vandalism News, etc. sometimes had deep technical articles about music players

Bad leads (don't follow):
- General scene history pages without technical content
- Music reviews or playlists
- Broken links with no Wayback Machine archive
- Pages already fetched by another agent

## What NOT to collect

- General C64 history or music reviews
- Scene drama or personal anecdotes
- Duplicate information (if two sources say the same thing, keep the more detailed one)
- Anything that doesn't help us parse the format or reproduce register-accurate playback

## Quality bar

For each document saved, it should help answer at least one of:
- How do we parse the binary data layout?
- How does effect X modify SID registers per frame?
- What are the differences between player versions?
- What edge cases will we hit?
