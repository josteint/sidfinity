---
name: project_music_assembler_target
description: "Music_Assembler — the largest un-migrated HVSC family with completed research (6,351 SIDs, engine_docs OK). Why it is the designated next family, and the DMC member that already depends on it."
metadata: 
  node_type: memory
  type: project
  originSessionId: fc3f0dc2-7e5f-4a76-bce6-958991c22a69
  modified: 2026-07-22T11:09:14.607Z
---

STATUS (2026-07-22): **STARTED — the anchor + family census are in.**
`pipelines/music_assembler/locate.py` locates the player and its tables;
`tools/masm_census.py` is the family census. **5,618 / 6,351 (88.5%) locate
cleanly, ALL at signature offset +$91 — one dominant build.** Next: decode the
sequence stream + preset table into a model (extract), then a composer.

## Census result (tools/masm_census.py, 2026-07-22)

| | |
|---|---:|
| locate OK | 5,618 (88.5%) |
| no player found | 733 (11.5%) |
| signature offset from base | `+$91` on **all** 5,618 |
| PSID vectors `init=base+$48/play=base+$21` | 2,746 |
| PSID vectors `init=base+$00/play=base+$03` | 2,561 |
| other vector convention | 311 |
| song speed 2 / 3 / 1 / other | 3,296 / 990 / 819 / 513 |
| single-subtune members | 5,509 |
| player materialised by init (packed, C26) | 9 |

The 733 misses are the predicted version tail (V1.1 / V1.4 Triad,
VoiceTracker derivative, multispeed DoubleTracker/Ten Tracker) — not yet
triaged. `tmp/masm_census.jsonl` holds the per-member rows.

## Two corrections to the research docs (verified, not assumed)

Both are annotated at the head of
`pipelines/music_assembler/docs/spec_player_RE_grounded.md`:

- **Seq pointer LO is `$C675`, HI is `$C669`** — the doc's data-table row has
  them swapped (its own disassembly and byte dumps say otherwise). Checked on
  300 sampled members: 296 resolve as located, **0** need the swap.
- **The base anchor is init's fixed prefix at base+$48**
  (`A9 1F 8D 18 D4 A9 F0 8D 17 D4`), NOT `signature - $91` and NOT
  `seqnum - $8D` — those offsets are build-dependent and cost ~50 members plus
  4 false positives when used as the primary anchor. With the init anchor the
  signature offset collapses to a single value (`+$91`) family-wide, which
  also supersedes README.md's `+$91/+$B5/+$70/+$191` spread.

## Why it is next

By CLAUDE.md's stated rule — *next family = the largest un-migrated family
whose `engine_docs` state is OK* — Music_Assembler IS the next family:

| family | SIDs | state |
|---|---:|---|
| dmc | 10,676 | migrated |
| goattracker | 8,670 | migrated |
| **music_assembler** | **6,351** | **OK, un-migrated ← next** |
| future_composer | 4,024 | migrated |
| soundmonitor | 3,625 | OK, un-migrated |
| jch_newplayer | 3,611 | OK, un-migrated |

## What is already known about its shape

From `docs/the_trichotomy.md` §2 (the init survey), Music_Assembler is the
"barely anything" init bucket and its signature is unusually sharp:

- init writes exactly **3 bytes**: `$D417 = $F0`, `$D418 = $1F`. Nothing else.
- It therefore **relies on the previous tune's chip state** for voice ctrl,
  freq, pulse width — our universal reset makes the rebuild *more* defined
  than the original here (trichotomy §5.3: Check A still passes, because the
  host stub starts from a clean reset).
- The player is compact (~1 KB of code) and its data model is DMC-like in
  outline: 2-byte track entries, `$FF` end-of-track / `$FE` stop markers,
  instrument select at `$60 + 5-bit id`, per-voice state arrays indexed by X,
  sector-pointer lo/hi tables, a freq table read as `freqlo[y]`/`freqhi[y]`.
  **Do NOT mistake that outline for DMC** — 0 of 11 DMC canon locate-sites
  match, and `dataflow.locate` returns None on it.

## The dependency that surfaced it

`MUSICIANS/B/Bayliss_Richard/Freespace_2075.sid` (DMC f1 partial) is a
HETEROGENEOUS C31 compilation: subtune 0 runs a DMC v4 player at `$1000`
(**FULL** today), while subtunes 1-2 run **Music_Assembler** players that the
init wrapper relocates into RAM (`$2000→$4700`, `$2800→$3700`). Its C31
detection half is done (round 85, commit 4985aa13); the member cannot go FULL
until an MA extractor exists and is wired as an MA sub-player — the
`dmc_sfx` precedent in ledger C31 (Canyon_Tank_Duel) is the pattern to follow.

Identification method + the trap that nearly hid it: [[project_dmc]] round 85
and the C31 recognition card (an opcode skeleton spanning a player's
SMC/scratch bytes reported "1 carrier in HVSC" for a 6,349-member family).

## Before starting

Run CLAUDE.md's three MANDATORY questions — `pipelines/music_assembler/docs/`
exists and must be read first; there is no `disassembly.s` or `RE_NOTES.md`
yet, so seed one with `tools/seed_disassembly.py` and annotate before coding.
