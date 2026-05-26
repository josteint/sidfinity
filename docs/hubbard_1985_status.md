# 1985 Hubbard pipelines — first-pass status

17 1985 classic-engine SIDs (Commando + Monty already done) cloned into
sibling pipelines via `tools/clone_hubbard_pipeline.py` and batch-built
via `tools/batch_1985.py`. Each clone got auto-discovered per-SID
constants (ft_base, pulsedelay/pulsedir init from the binary) and a
music-subtune list derived from HVSC Songlengths (any subtune ≥ 30 sec).

## Per-pipeline grade after first build

| SID | Music subs | Pipeline | First-build grade |
|---|---|---|---|
| 5 Title Tunes | 0,1,2,3,4 | `pipelines/five_title_tunes/` | **extract error** — rh_decompile finds 1 song, PSID claims 5 |
| Action Biker | 0,1 | `pipelines/action_biker/` | F (0%) |
| Battle of Britain | 0 | `pipelines/battle_of_britain/` | F (0%) |
| Chimera | 0,1 | `pipelines/chimera/` | **lake build error** |
| Confuzion | 0 | `pipelines/confuzion/` | F (3.3%) |
| Crazy Comets | 0,1 | `pipelines/crazy_comets/` | F (3.9%) |
| Devils Galop | 0 | `pipelines/devils_galop/` | **D (44.3%)** |
| Gremlins | 0,1,2,3,4,5,6 | `pipelines/gremlins/` | F (5.8%) |
| Hunter Patrol | 0 | `pipelines/hunter_patrol/` | F (0%) |
| One Man and his Droid | 0 | `pipelines/one_man_and_his_droid/` | **D (37.5%)** |
| Rasputin | 0 | `pipelines/rasputin/` | F (0%) |
| Sample Music from I.Karate | 0 | `pipelines/sample_music_i_karate/` | F (0%) |
| Human Race | 0,1,2,3,4 | `pipelines/human_race/` | **extract error** — pattern shared across subtunes at different tempos |
| Last V8 | 0 | `pipelines/last_v8/` | **lake build error** |
| Last V8 (C128) | 0..2 | `pipelines/last_v8_c128/` | **scaffold + tombstone** — real extract (RSID, dual-engine: tracker + relocated sample player); codegen emits a 1-byte RTS; disassembly at `docs/hubbard_last_v8_c128_disassembly.s` |
| Master of Magic | 0 | `pipelines/master_of_magic/` | F (2.8%) |
| Thing on a Spring | 0 | `pipelines/thing_on_a_spring/` | F (4.8%) |

## Honest interpretation

This first pass was a **scaffolding exercise**, not a "17 working pipelines"
exercise. What worked: 17 pipeline folders exist, lakefile entries added,
12 of them build and produce a valid SID file, baseline grades captured.

What didn't work, and **why**:

- **Monty's codegen is Monty-specific.** The clones inherit Monty's skydive
  emit block, notenum→freq-table aliasing into slots 105.hi/106.lo/106.hi,
  HR threshold = 1, and PWM init data layout. Most 1985 SIDs DON'T need
  the notenum overlap (different memory layout) and they have different
  per-SID quirks Monty's codegen knows nothing about.
- **rh_decompile is incomplete for some 1985 SIDs.** 5 Title Tunes,
  Chimera, Last V8 etc. expose decompiler edge cases. The decompiler
  was tuned against Commando + Monty; other binaries trip it up.
- **Multi-subtune patterns at different tempos** (Human Race) need
  tick-based duration encoding, which our pipeline collapses at extract
  time. That's a USF schema gap.

## What the two Grade-D results tell us

`devils_galop` (44.3%) and `one_man_and_his_droid` (37.5%) match orig on
roughly 40-45% of frames purely from the auto-discovered constants
(ft_base + pulsedelay/dir). That's the value of the cloning approach:
even with Monty's wrong-for-this-SID codegen overrides, the rebuild
gets the basics right when the binary structure happens to match.

These two are the natural next targets — they're close enough that
per-SID investigation (which Monty-isms to disable, which quirks to add)
should push them to Grade A relatively quickly.

## Tools added

- `tools/clone_hubbard_pipeline.py` — clones the Monty pipeline as a new
  Hubbard pipeline. Auto-discovers ft_base + pulsedelay/dir from the
  binary, patches the clone's emit_usf and Codegen.
- `tools/batch_1985.py` — runs the clone for every 1985 SID, updates
  the lakefile, builds, runs, grades, prints a table.

## What "next" actually looks like

Per-SID work, not bulk automation, from here on:

1. Pick one Grade-F or Grade-D pipeline (Devils Galop is the highest-grade).
2. Trace where the rebuild diverges from orig (py65, like we did for Monty).
3. Disable Monty-specific codegen blocks that don't apply.
4. Discover and add the SID's actual quirks.
5. Get it to Grade A.
6. Move to the next.

This was effectively the Monty→Commando experience all over again, except
17 times. The bulk infrastructure is now in place; the per-SID craft is
what remains.
