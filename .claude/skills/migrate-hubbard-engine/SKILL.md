---
name: migrate-hubbard-engine
description: Migrate a Rob Hubbard 1985-era SID engine to the shared USF2 core (pipelines/hubbard/) and produce a byte-exact rebuild. Use when starting work on a new Hubbard engine — Human Race, Hunter Patrol, Thing on a Spring, One Man and His Droid, etc. Encodes the procedure proven on Commando, Devils Galop, Monty, Action Biker and Chimera.
argument-hint: [engine-name]
user-invocable: true
allowed-tools: Bash Read Write Edit Glob Grep Agent
effort: max
---

# Migrate the $ARGUMENTS engine to USF2

Goal: `$ARGUMENTS` plays back **byte-exact** — every subtune's per-frame
SID-register-write stream matches the original — through the pipeline
SID → extract → USF2 → codegen → rebuilt SID, on the shared Hubbard '85
core at `pipelines/hubbard/`.

Five engines are already done this way. The engine is a thin
`EngineConfig`; the shared core (song_interp + codegen) is engine-
agnostic. There is **no cloning** — every per-engine difference is a
config field.

## The principle — do not violate this

Every per-engine difference is an `EngineConfig` field describing engine
**mechanism** (a threshold, an address, a step size, a flag). It is
**never** a `*Kind` enum or a library index in the USF data. If you find
yourself wanting to add an opaque "kind" tag, stop and read
`docs/usf_representation_principle.md` in full — effects are parametric
over a musical basis; the engine holds mechanism, the data stays
abstract.

## The method — trace ONE diff at a time

Never guess deltas or batch-apply them. The loop is: build → capture
original vs rebuilt → find the **first** differing frame → read the
disassembly at that exact point → identify the one delta → make it a
config field → re-measure. Repeat. Each delta is one commit.

## Step 0 — pre-work (do not skip)

1. Search memory for `project_<engine>.md` — prior sessions' root-cause
   analysis. Read it if it exists.
2. Disassembly: `docs/hubbard_<engine>_disassembly.s`. If missing,
   generate the seed and hand-annotate the header:
   ```
   PYTHONPATH=tools/py65_lib python3 tools/seed_disassembly.py \
       demo/hubbard/<Engine>_original.sid > docs/hubbard_<engine>_disassembly.s
   ```
3. Read the disassembly header for: load / init / play addresses,
   **freq-table base**, **instrument-table base + record count**,
   **subtune count**, and the per-voice variable layout. Hubbard '85
   instrument records are 8 bytes: `pw_lo, pw_hi, ctrl, ad, sr,
   vib_depth, pwm_speed, fx_flags`.

## Step 1 — scaffold

- `cp data/C64Music/MUSICIANS/H/Hubbard_Rob/<Engine>.sid demo/hubbard/<Engine>_original.sid`
- Add `stop: bool = False` to the `Voice` dataclass in
  `pipelines/<engine>/extract/types.py` (right after `loop`).
- Add the `$FE` handler to `pipelines/<engine>/extract/engine_model.py`'s
  orderlist loop: `elif entry[0] == 'stop': voice.stop = True`.
- Write `pipelines/<engine>/config.py` — an `EngineConfig` with module-
  level `_extract(subtune)` and `_resetspd(subtune, binary, load)`
  wrappers. Start minimal: `name, sid_path, instr_base, instr_count,
  freq_table_base, extract, resetspd, subtunes, arp_interval=12,
  has_sfx=False`. Copy `pipelines/chimera/config.py` as the template.

## Step 2 — sanity-check before building

Run `config.extract(subtune)` for each subtune (check voices/instrument/
freq-table counts) and `decode_all(sid, instr_base, instr_count)` (the
instruments' ctrl/ad/sr/fx/vib/arp/pwm should look plausible). A wrong
`instr_base` or `freq_table_base` shows up here.

## Step 3 — build + trace loop

The per-iteration snippet (capture each SID **once**, then compare —
never call `capture()` inside a per-frame loop):

```python
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'tools/py65_lib'); sys.path.insert(0,'src')
from pipelines.hubbard.codegen import build
from pipelines.hubbard.inst_program import capture, REG_NAMES
from pipelines.<engine>.config import CFG
build(CFG, out_path='/tmp/<engine>.sid')
def fmt(fw): return ' '.join(f'{["V1","V2","V3"][p//7]}.{REG_NAMES[p%7]}={v:02X}' for p,v in fw) or '-'
for st in CFG.subtunes:
    o=capture(CFG.sid_path,n_frames=6000,subtune=st)
    r=capture('/tmp/<engine>.sid',n_frames=6000,subtune=st)
    first=next((k for k in range(6000) if o.raw_frames[k]!=r.raw_frames[k]),None)
    print(f'subtune {st}: first diff f{first}')
    if first is not None and st==CFG.subtunes[0]:
        for k in range(first,first+3):
            print(' orig',fmt(o.raw_frames[k])); print(' reb ',fmt(r.raw_frames[k]))
```

At each first-diff, read the disassembly and pick the delta. Then
`song_interp` and the codegen must agree — if both are wrong by the same
amount it is the model (song_interp), not the codegen.

## The delta catalog — config fields and their disassembly signatures

| field | meaning / what to look for in the disassembly |
|---|---|
| `speed_ctr_init` | first note-load deferred N frames — the tick counter starts at N; the first N frames are effects-only |
| `first_frame_gate_off` | play frame 0 writes ctrl=0 to all 3 voices (first-frame setup runs in *play*, not init) |
| `vib_onset` | vibrato dur-field gate — the `CMP #$xx` guarding the vibrato accumulate |
| `arp_interval` | arpeggio semitone offset (usually 12) |
| `arp_period` | arp cycle length — `frame & N` in the arp block means `arp_period = N+1` |
| `incby2_step` / `incby2_every_frame` / `incby2_onset` | fx-bit-1 freq-hi slide — step (+2/+1/-1), every-frame vs odd-frame, min dur field |
| `linear_pw_or` | `ORA #$xx` applied to pw_lo in the linear-PW kick |
| `freeze_on_stop` | `$FE` freezes the voice (holds the note, keeps effects, never gates off) |
| `stop_fill` | `$FE` ends the song by writing this byte to every voice register, then silence |
| `voice_starts` | per-subtune voice-loop start index (a subtune that skips V3) |
| `suppress_first_notestart` | a drum-priority gate suppresses voice 0's first-frame note-start |

**Overlap seeds.** Engines that run effects before the first note-load
(deferred note-load, or a first-note tie) read per-voice state from the
binary's load-time bytes. The shared core seeds these from
`freq_table_base + offset`: `v_durfield` +205, `v_ctrl` +208,
`v_instr` +214, `pwm_period` +229, `pwm_dir` +232, `v_slide` +239. If a
new engine reads another uninitialised per-voice variable, seed it the
same way (song_interp `__init__` + codegen `iniov`).

## Gotchas

- **xa65**: no colons (`:`) or backslashes (`\`) inside `;` comments —
  they cause "Label already defined" / syntax errors.
- **IRQ-driven SID** (PSID play address 0): the music runs from a raster
  IRQ; `inst_program.capture` already follows the `$0314/$0315` vector
  after init. Nothing to do — but expect the original's play to be 0.
- **digi / SFX subtunes** ($D418, cycle-timed playback): out of scope.
  The frame-granular capture cannot verify them. Migrate only the music
  subtunes; leave SFX unshipped.

## Step 4 — verify and finish

- `verify_all` (`pipelines/hubbard/verify.py`) over Commando + every
  done engine + the new one: the new engine must be ALL EXACT, and the
  others must stay ALL EXACT (every delta is config-gated and inert for
  them — if one regresses, the change was not properly gated).
- Commit each verified delta as you go: `git -c commit.gpgsign=false
  commit` — no `Co-Authored-By`.
- `cp /tmp/<engine>.sid demo/hubbard/<Engine>.sid` and `git add -f` it
  (the showcase pair: `<Engine>_original.sid` + `<Engine>.sid`).
- Update `project_<engine>.md`, `project_usf2_refactor.md`, `MEMORY.md`
  and `docs/usf_instrument_program_plan.md` (the Phase 6.2 checklist).
- **Evolve this skill** — see below.

## Evolve this skill

This skill is the distilled procedure, not holy writ — it captures what
the first five engines taught. Each new engine may teach more. Before
you finish, update this `SKILL.md` and commit it alongside the engine's
commits:

- A new per-engine difference became an `EngineConfig` field → add it to
  the delta catalog **with its disassembly signature** (the catalog is
  only useful if it says how to *recognise* the delta).
- You hit a new gotcha — an assembler quirk, a capture edge case, an
  engine variant — → add it to Gotchas.
- An engine read an uninitialised per-voice variable from a new
  freq-table-overlap offset → record the offset.
- The procedure misled you or a step was unclear → fix the wording.
- A field or file got renamed → correct every mention.

The skill should be strictly better after every engine than before it.
If it isn't evolving, it is quietly going stale.

## Reference

- Shared core: `pipelines/hubbard/{config,types,inst_program,
  inst_generalize,inst_interp,note_codec,song_interp,codegen,verify}.py`.
- Worked examples: the `project_{commando,devils_galop,monty,
  action_biker,chimera}.md` memories — read the closest-looking one.
- `docs/usf_representation_principle.md` — load-bearing, read before
  changing any effect/instrument representation.
