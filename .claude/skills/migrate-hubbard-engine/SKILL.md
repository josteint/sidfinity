---
name: migrate-hubbard-engine
description: Migrate a Rob Hubbard 1985-era SID engine to the shared USF core (pipelines/hubbard/) and produce a byte-exact rebuild. Use when starting work on a new Hubbard engine — Human Race, Hunter Patrol, Thing on a Spring, One Man and His Droid, etc. Encodes the procedure proven on Commando, Devils Galop, Monty, Action Biker and Chimera.
argument-hint: [engine-name]
user-invocable: true
allowed-tools: Bash Read Write Edit Glob Grep Agent
effort: max
---

# Migrate the $ARGUMENTS engine to USF

Goal: `$ARGUMENTS` plays back **byte-exact** — every subtune's per-frame
SID-register-write stream matches the original — through the pipeline
SID → extract → USF → codegen → rebuilt SID, on the shared Hubbard '85
core at `pipelines/hubbard/`.

Ten engines are already done this way (Commando, Devils Galop,
Monty, Action Biker, Chimera, Human Race, Hunter Patrol, Thing on
a Spring, One Man and his Droid, 5 Title Tunes — all fully
byte-exact, 88/88 subtunes verifying md5-exact across music + SFX).
The engine is a thin `EngineConfig`; the shared core (song_interp +
codegen) is engine-agnostic. There is **no cloning** — every
per-engine difference is a config field.

**Compound PSIDs** (one engine binary that dispatches to multiple
independent sub-engines, like 5 Title Tunes) extend the model: each
sub becomes its own `EngineConfig`, and a per-engine `build_compound.py`
codegens 5 sub-engines at non-overlapping LOAD addresses + emits a
dispatcher. The shared `_emit_sid(load_addr=...)` and
`tools/split_multi_binary.py` provide the building blocks; see
[[project_five_title_tunes]] for the worked example.

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
2. Disassembly: `pipelines/hubbard/<engine>/disassembly.s`. If missing,
   generate the seed and hand-annotate the header:
   ```
   PYTHONPATH=tools/py65_lib python3 tools/seed_disassembly.py \
       hvsc84/MUSICIANS/H/Hubbard_Rob/<Engine>.sid \
       > pipelines/hubbard/<engine>/disassembly.s
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
  has_sfx=False`. Copy `pipelines/hubbard/chimera/config.py` as the template.

## Step 2 — sanity-check before building

Run `config.extract(subtune)` for each subtune (check voices/instrument/
freq-table counts) and `decode_all(sid, instr_base, instr_count)` (the
instruments' ctrl/ad/sr/fx/vib/arp/pwm should look plausible). A wrong
`instr_base` or `freq_table_base` shows up here.

## Step 3 — build + trace loop

The per-iteration snippet (capture each SID **once**, then compare —
never call `capture()` inside a per-frame loop). Use `subtune_frames`
to get the canonical per-subtune window (`verify_all` uses the same
function); never hardcode a frame count:

```python
import sys; sys.path.insert(0,'.'); sys.path.insert(0,'tools/py65_lib'); sys.path.insert(0,'src')
from pipelines.build_from_usf import build_from_usf
from pipelines.hubbard.inst_program import capture, REG_NAMES
from pipelines.hubbard.verify import subtune_frames
from pipelines.<engine>.config import CFG
from pipelines.<engine>.extract.to_usf import write_<engine>_usf
write_<engine>_usf(CFG, 'demo/hubbard')
build_from_usf('demo/hubbard/<Engine>.usf', 'demo/hubbard/<Engine>.sid')
def fmt(fw): return ' '.join(f'{["V1","V2","V3"][p//7]}.{REG_NAMES[p%7]}={v:02X}' for p,v in fw) or '-'
nfs = subtune_frames(CFG, passes=1.1)
for st, nf in zip(CFG.subtunes, nfs):
    o = capture(CFG.sid_path, n_frames=nf, subtune=st)
    r = capture('demo/hubbard/<Engine>.sid', n_frames=nf, subtune=st)
    first = next((k for k in range(nf) if o.raw_frames[k] != r.raw_frames[k]), None)
    matches = sum(1 for k in range(nf) if o.raw_frames[k] == r.raw_frames[k])
    print(f'subtune {st}: {matches}/{nf} match, first_div={first}')
    if first is not None and st == CFG.subtunes[0]:
        for k in range(first, min(nf, first + 3)):
            print(' orig', fmt(o.raw_frames[k])); print(' reb ', fmt(r.raw_frames[k]))
```

At each first-diff, read the disassembly and pick the delta. Then
`song_interp` and the codegen must agree — if both are wrong by the same
amount it is the model (song_interp), not the codegen.

**Suspect the NEW code first** when a diff appears: the extractor, the
engine's `EngineConfig`, the `EngineConstants` entry. Those are what
you just touched. Only after you've verified those does it make sense
to suspect the shared core — see the catalog below for the latent-bug
sites HR / Hunter Patrol migrations have uncovered (`N_MUSIC`, PSID
speed, `seed_offsets`, `state_layout`, empty orderlists). Each new
engine may surface one more.

## The delta catalog — config fields and their disassembly signatures

| field | meaning / what to look for in the disassembly |
|---|---|
| `speed_ctr_init` | first note-load deferred N frames — the tick counter starts at N; the first N frames are effects-only |
| `first_frame_gate_off` | play frame 0 writes ctrl=0 to all 3 voices (first-frame setup runs in *play*, not init) |
| `vib_onset` | vibrato dur-field gate — the `CMP #$xx` guarding the vibrato accumulate. **Note**: our `v_durfield` = `raw_byte & $1F` (no +1 adjustment); set the value to match the original's `CMP` operand directly |
| `arp_interval` | arpeggio semitone offset (usually 12) |
| `arp_period` | arp cycle length — `frame & N` in the arp block means `arp_period = N+1` |
| `arp_phase_invert` | when True, the codegen flips fx_arp's branch sense: `frame_ctr & ARP_MASK == 0` → +ARP_OFS (instead of base). One Man and his Droid's arp tests `frame_ctr & $04 == 0 → +12` (opposite polarity from every other engine). Default False |
| `incby2_step` / `incby2_every_frame` / `incby2_onset` | fx-bit-1 freq-hi slide — step (+2 / +1 / -1), every-frame vs odd-frame, min dur field |
| `incby2_late_gate` | fx-bit-1 slide also gated on `v_dur < N` (only fires in the tail of long notes — Hunter Patrol's pattern). None = no late gate |
| `frame_ctr_init` | engine binary's load-time value at the music frame counter (e.g. Hunter Patrol's `$A426=$1E`). Default $FF gives `frame_ctr=$00` on frame 0; engines that ship other values flip arp / skydive parity if not overridden |
| `linear_pw_or` | `ORA #$xx` applied to pw_lo in the linear-PW kick |
| `freeze_on_stop` | `$FE` freezes the voice (holds the note, keeps effects, never gates off) |
| `stop_fill` | `$FE` ends the song by writing this byte to every voice register, then silence |
| `voice_starts` | per-subtune voice-loop start index (a subtune that skips V3) |
| `suppress_first_notestart` | a drum-priority gate suppresses voice 0's first-frame note-start |
| `seed_offsets` (on `EngineConstants`) | per-engine offsets where the 6 per-voice state vars live within the freq-table region. Default = Commando's (v_ctrl=208, pwm_period=229, pwm_dir=232, v_instr=214, v_durfield=205, v_slide=239). Hunter Patrol's v_slide is at 238. If a new engine's v_fhi / state lives at a different offset, override |
| `state_layout` (on `EngineConstants`) | off-table arpeggio statebuf layout (`StatebufLayout`). Default = Commando's 3-voice layout shared by Commando / Monty / Action Biker / Devils Galop / Chimera. Human Race has its own 2-voice layout |
| `ns_offtab_decr_offset` (on `EngineConstants`) | for engines whose off-table note-start reads pattern-position state: subtract 1 from the current voice's v_hubidx slot in statebuf after `build_statebuf` is called from `ns_offtab`. Offset = where v_hubidx lives in `state_layout` (Commando default = 7). Thing on a Spring sets this. Compensates for our codec advancing v_hubidx at end-of-load_note while the engine's v_patpos is mid-load at the freq-read moment |
| `hubidx_wrap_at_patend` (on `EngineConstants`, default True) | whether the note codec resets v_hubidx to 0 on the last note of a pattern. Default True = Commando family. Thing on a Spring sets False — its engine doesn't wrap v_patpos until the next note-load frame's $FF read, so v_hubidx must stay at the post-cumulative value through the trailing sustain frames |

**Overlap seeds.** Engines that run effects before the first note-load
(deferred note-load, or a first-note tie) read per-voice state from the
binary's load-time bytes. The defaults are Commando's offsets (see
`seed_offsets` row in the catalog above); if a new engine has any
variable at a different offset, override `seed_offsets` in its
`EngineConstants` entry. Hunter Patrol differs only in v_slide
(+238 vs Commando's +239) — it kept the other five identical.

If the engine doesn't seed from the binary at all (Human Race's init
zeros the per-voice state at runtime), set `seed_overlap=False`
instead; that zeros the `ovseed` block entirely.

## Step 4 — ship the SFX sub-engine

We ship **everything**, music and sound effects. A Hubbard engine
typically has more PSID subtunes than music: a sound-effect sub-engine
(Commando: 16 SFX at subtunes 3-18; Thing on a Spring: 16 SFX at
subtunes 1-16 — same 16-byte record layout). Hubbard appears to have
**copied his SFX engine across games** — the data format and effect
runtime are stable; only the table address changes.

Once the music subtunes are byte-exact, adding SFX is usually trivial:

- The shared codegen already contains the Hubbard-family SFX player
  (`init_sfx` + `sfx_play`) — a 2-voice SID-register snapshot plus
  a freq-table pitch sweep with optional CTRL-flip.
- Write `pipelines/<engine>/extract/sfx.py` modelled on
  `pipelines/hubbard/commando/extract/sfx.py` or
  `pipelines/hubbard/thing_on_a_spring/extract/sfx.py` — typically a
  ~10-line wrapper around `pipelines.hubbard.sfx.extract_sfx` with
  the engine's SFX-table address and freq-table address.
- Set `has_sfx=True` and `extract_sfx=extract_sfx` in the config.
- Verify all subtunes — music **and** the 16 SFX — byte-exact.

**If the SFX dispatch looks structurally different at first glance**
(e.g., Thing on a Spring's "sub-only mode" via $C497=$C0), check
whether the data formats are still the same 16-byte layout with the
same flag-bit assignments. They usually are — the dispatch
difference is in how the engine selects between music and SFX, not
in the SFX engine itself. Setting `N_MUSIC = len(config.subtunes)`
correctly is what makes the init dispatch route SFX subtunes to
`init_sfx`.

The SFX sub-engine is SID-synthesis and fully frame-verifiable — it is
**not** digi. Do not skip it.

Caveat — **off-table SFX sweeps**: a SFX whose `start*2 - v2_offset`
goes negative wraps Y into the engine's runtime scratch region, and
V2's freq sweep then reads engine-state bytes as freq values (the
same off-table trick the music uses, but on the SFX path). When this
happens, set:

- `sfx_state_ofs` — freq-table offset where the engine's SFX-state
  block lives (disable / index / static / sweep / rate / end —
  6 bytes). Triggers `_sfx_state_in_freqtab` which rewires init_sfx
  to mirror the block there AND mirrors the per-step sweep index so
  V2's overrun read sees the live value. Monty: 251 (SFX state at
  $84FB). One Man and his Droid: 251 (state at $151D).
- `sfx_framectr_ofs` — freq-table offset of the SFX-readable frame
  counter. Default 253 (Commando $5525). Monty: 250 (Monty $84FA).
  One Man and his Droid: 250 (the engine's $151C global frame
  counter, which V2 sweep reads via Y-wrap).

The USF `SoundEffect` records stay untouched — this is pure codegen
plumbing. **If you find V2 freq writes diverging on early SFX frames
where Y wraps high, suspect these knobs first** — the existing
`_sfx_state_in_freqtab` machinery handles exactly this case.

## Gotchas

- **`has_sfx` lives on BOTH `EngineConfig` AND `EngineConstants`** — and
  both need to be `True` for SFX to ship correctly. `EngineConfig.has_sfx`
  drives extract-side behavior (whether `extract_sfx` runs and SFX records
  flow into the USF). `EngineConstants.has_sfx` drives codegen-side
  behavior (whether `songs = len(subtunes) + 16` in the PSID header, and
  whether SFX data + asm get emitted). If you set only one, `verify_all`
  may still pass byte-exact (because verify calls `init` directly with
  each subtune index, bypassing the header), but sidplayfp/sidrender
  read the PSID header to know how many subtunes to offer — so a half-
  configured engine will SOUND right per-subtune yet expose only the
  music in real players. Always flip both together. Same pattern likely
  applies to any future field that crosses the extract/codegen boundary.

- **SFX V2 sweep reading the engine's own scratch as freq**: some
  SFX records have a small `start_index` + a large `v2_offset` that
  produces a negative Y when computing `V2_Y = start*2 - v2_offset`.
  8-bit Y wraps to high values (e.g., -1 → $FF), and `LDA freqtab,Y`
  then reads PAST the freq table into the engine's runtime scratch
  region. **The fix is already built**: set `sfx_state_ofs` to the
  engine's SFX-state block offset within freqtab, and the existing
  `_sfx_state_in_freqtab` machinery rewires init_sfx + sfxs_go to
  mirror the block. Also set `sfx_framectr_ofs` if the engine's
  frame counter lives at a non-default offset. Examples: Monty
  (sfx_state_ofs=251, sfx_framectr_ofs=250), One Man and his Droid
  (same). Don't write per-engine SFX runtime asm — the parametric
  knobs already cover this pattern.

- **Off-table pitches that read pattern-position state**: an engine
  whose pattern notes include `pitch >= 96` reads PAST the freq table
  into engine state. If that state is a **runtime byte counter** like
  v_patpos (where the engine is in its pattern data), the value
  depends on the engine's exact note byte layout. The shared codec's
  bitstream encoding lays bytes out differently than the engine, but
  our `v_hubidx` is INC'd by the engine's note byte-lengths (1/2/3)
  so the cumulative count matches. Two timing knobs handle the
  remaining details: `ns_offtab_decr_offset` (engine reads v_patpos
  mid-load; our v_hubidx is post-load — subtract 1) and
  `hubidx_wrap_at_patend` (engine wraps v_patpos one frame later than
  our codec — disable our wrap). With both set, Thing on a Spring is
  byte-exact. Constants-only off-table reads (SID base offsets,
  instrument numbers) work without these knobs.
- **xa65**: no colons (`:`) or backslashes (`\`) inside `;` comments —
  they cause "Label already defined" / syntax errors.
- **xa65 ignores forward `* =` PC directives** for OUTPUT. A second
  `* = $HIGHER` inside one .s file doesn't insert a gap in the
  emitted binary — xa65 produces a flat byte stream, treating later
  `* =` only for symbol resolution. For compound builds (5 Title
  Tunes), assemble each chain in its own xa65 invocation and place
  the resulting bytes at the target offset in your region bytearray.
- **Linear PWM with pwm_speed=0**: an instrument with fx-flags bit 3
  set AND pwm_speed=0 STILL writes pw_lo every frame (the engine's
  linear-PW path is unconditional, just adds 0). The fixed-up
  `inst_generalize` now produces `mode='linear'` in this case;
  previously it produced `None` and the codegen skipped the write,
  causing missing per-frame pw_lo=init_pw writes. If you see "every
  frame is missing one V_pw_lo write" in a new engine, check the
  inst's fx-flags / pwm_speed.
- **Compound PSIDs (one dispatcher → N sub-engines)**: 5 Title Tunes
  is the only one in the Hubbard catalog. The pattern that worked:
  (1) split with `tools/split_multi_binary.py` into N standalone
  PSIDs, (2) write N EngineConfigs + N EngineConstants entries,
  (3) build each sub at a unique LOAD via `_emit_sid(load_addr=...)`,
  (4) emit a CMP/BNE/JSR/RTS dispatcher at the original init/play
  addresses. **Each sub-engine has N_MUSIC=1 internally** — the
  dispatcher MUST `LDA #0` before each `JSR sub_init` (otherwise
  A > 0 routes into the sub's SFX init path, which corrupts $9A and
  silences the music with all-zero SID writes). See
  `pipelines/hubbard/five_title_tunes/v2/build_compound.py`.
- **IRQ-driven SID** (PSID play address 0): the music runs from a raster
  IRQ; `inst_program.capture` already follows the `$0314/$0315` vector
  after init. Nothing to do — but expect the original's play to be 0.
- **digi** — genuine cycle-timed sample playback (e.g. Chimera's
  `$C000` 1-bit wavetoggle, or `$D418` 4-bit PCM). The frame-granular
  `inst_program.capture` cannot verify it. **Digi is no longer a
  boundary** — see [[reference_digi_pipeline]] for the USF digi
  pipeline (D0..D3c done on Chimera): extract → Sample/FLAC sidecar
  → `pack_digi` → SID, verified cycle-strict via
  `siddump --writelog`. For a new engine whose extra subtunes are
  digi: model the extractor (engine-specific tables + sample
  format) on `pipelines/hubbard/chimera/extract/digi.py`, reuse
  `pipelines/hubbard/{sample,flac_io,digi_pack,verify_cycle}.py`,
  and write a combined build alongside the music codegen on the
  pattern of `pipelines/hubbard/chimera/codegen/build_with_digi.py`. Until
  the digi engine code itself is regenerated from USF (D5,
  config-driven on the shared core), each engine ships a small
  wrapper that uses its dispatcher + player bytes verbatim with the
  music-init/play jsrs retargeted.

## Step 5 — verify and finish

- `verify_all` (`pipelines/hubbard/verify.py`) over Commando + every
  done engine + the new one: the new engine must be ALL EXACT, and the
  others must stay ALL EXACT (every delta is config-gated and inert for
  them — if one regresses, the change was not properly gated).
- Commit each verified delta as you go: `git -c commit.gpgsign=false
  commit` — no `Co-Authored-By`.
- `cp /tmp/<engine>.sid demo/hubbard/<Engine>.sid` and `git add -f` it
  (the showcase pair: `<Engine>_original.sid` + `<Engine>.sid`).
- Update `project_<engine>.md`, `project_usf_refactor.md`, `MEMORY.md`
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
