---
name: sidfinity
description: SIDfinity pipeline worker. Use for ANY task involving SID files, USF conversion, grading, player codegen, or engine reverse-engineering.
tools: Read, Grep, Glob, Bash, Edit, Write
model: sonnet
---

You are working on the SIDfinity project at /home/jtr/sidfinity.

## BEFORE DOING ANYTHING

1. Read `CLAUDE.md` for project status, conventions, and invariants
2. Read the relevant diagnosis memory if investigating a specific engine:
   - Hubbard: `~/.claude/projects/-home-jtr-sidfinity/memory/project_hubbard_diagnosis.md`
3. Read `docs/formal/procedure.md` for the decision framework on which tool to use

## USF Capabilities (what the player CAN do)

USF WaveTableStep fields — these are ALL available in the V2 player:
- `waveform`: SID waveform byte (pulse, saw, tri, noise, ring, sync, test)
- `note_offset`: relative semitone offset from current note
- `absolute_note`: absolute note (overrides note_offset)
- `keep_freq`: don't change frequency this step
- `freq_slide`: signed per-frame freq_hi delta (-128..+127). USE THIS FOR DRUM PITCH SWEEPS.
- `delay`: delay N frames before this step
- `cycle_delay`: sub-frame delay in CPU cycles
- `is_loop` / `loop_target`: wave table looping

USF also supports: pulse modulation tables, filter tables, speed tables (vibrato/portamento),
pattern commands 0-F (set AD/SR/wave/tempo/filter/volume), portamento up/down, tone portamento,
vibrato, funktempo, hard restart, legato, multi-song, custom freq tables.

## Key Files

| File | Purpose |
|------|---------|
| `src/usf/format.py` | USF data structures — READ THIS to know what's possible |
| `docs/usf_spec.md` | Full USF specification |
| `src/player/codegen_v2.py` | V2 6502 code generator |
| `src/sid_compare.py` | Register comparison with tolerance rules |
| `src/converters/gt2_to_usf.py` | GT2 → USF |
| `src/converters/rh_to_usf.py` | Hubbard → USF |
| `src/converters/regtrace_to_usf.py` | Universal register trace → USF |
| `src/converters/usf_to_sid.py` | USF → rebuilt SID |
| `src/rh_decompile.py` | Hubbard binary decompiler |
| `src/formal/taint_tracker.py` | 6502 taint tracking for driver analysis |

## Critical Rules

- Run regression (`python3 src/player/regression_test.py`) before committing pipeline changes
- The regression baseline is FROZEN — never modify it during a test run
- Do NOT use regtrace_to_usf as a fallback for engines that have static parsers — fix the parser
- Do NOT mix decompiled and trace-detected tempos — they're coupled to duration formulas
- Check `docs/decisions.md` for known dead ends before investigating
- Always `source src/env.sh` before running Python

## Environment

- 64-core EPYC, 512GB RAM, dual 3090
- `source src/env.sh` sets PATH
- py65 at `tools/py65_lib`
- Z3 at `tools/z3_lib`
- xa65 at `tools/xa65/xa/xa`
