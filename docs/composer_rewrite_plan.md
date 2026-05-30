# Composer rewrite plan — universal_codegen, no shapes

This is the living plan for rewriting `pipelines/universal_codegen.py` from
shape-based dispatch into a single composable engine-model codegen. Update
the checkboxes as work progresses. A fresh Claude session should be able
to pick up the work cold by reading this file.

**Status:** PLANNED. No phases executed yet. Last meaningful work:
commit `3d14b38` lifted Hubbard '85 into universal_codegen with
shape-based dispatch. The user pushed back on shape detection being
engine-identification in disguise; the composer rewrite replaces that
dispatch.


## Why this rewrite

The current `pipelines/universal_codegen.py` dispatches by "pattern_shape"
— `atomic`, `pair`, `command_stream`, `companion`, `hubbard85`. Each shape
is selected by content detection. Three problems:

1. The shape names are engine names (`hubbard85`, `companion`). Forbidden.
2. The detection criteria — "rich modulation programs OR multi-pattern
   orderlists OR SFX OR state_layout" for `hubbard85`; "gate_off_tick
   param" for `companion`; etc. — happen to identify precisely which
   engine produced the USF. Engine-identification by content. Forbidden.
3. Each shape is a separate monolithic emitter. The codegen can't grow by
   composing features; only by adding more shapes. The Nth engine becomes
   the Nth shape.

The composer rewrite removes shape dispatch. The codegen reads the USF's
features and emits the asm those features require. New engines = new
features, not new shapes.


## Principles — DO NOT VIOLATE

### Engine-blind dispatch

* **No `usf.engine` lookups in the build path.** Ever. The engine name in
  the USF is metadata, not control flow.
* **No data-block-size fingerprints.** `len(freq_table) == 256` vs `320`
  is engine identity in disguise. Same for any other "this engine's
  data is this size."
* **No "feature X is unique to engine Y" detection.** If a check would
  succeed iff the USF came from a specific engine, it's fingerprinting.
* **No engine-named shapes / functions / variables in the dispatch path.**
  `_is_hubbard85_shape` is the exact mistake. Name things by what they
  do, not by which engine does them.

### Instruction-stream is the contract

* **Only requirement: the per-frame SID-register instruction stream
  matches the original.** Cycle-strict where the test demands it
  (`compare_instruction_stream`); frame-md5 where that's the verdict
  (`verify_all`).
* **The 6502 code can look like anything.** Don't mimic the original
  engine's instruction shape — just produce the same per-frame writes.
* **Hubbard '85 verification = `pipelines.hubbard.verify.verify_all`.**
  Today: 71/71 across the 11 Hubbard engines. This must hold through
  every phase.
* **Companion-strain verification = `compare_instruction_stream`** from
  `pipelines.hubbard.verify_cycle`. Pre-existing partial cases stay
  partial; we don't fix them in this rewrite (Melonmania sub 1, Fairlight,
  Up_up_and_Away subs 0/1/2/4 1-event-short, sub 3 divergence).

### USF representation

* **Read `docs/usf_representation_principle.md` IN FULL before touching
  USF shape.** Forbidden shapes: `*Kind: int`, `*Ptr`, `*_idx: int`,
  `bytes`-typed fields that paper over a representation gap.
* **Effects are parametric over a musical basis; engine holds
  mechanism.** The engine-model layer is *where* mechanism lives. The
  USF stays musical.

### Working conventions

* **Each verified delta is one commit.** No batching.
* **No `Co-Authored-By` in commits.**
* **Propose options before code for non-trivial work.** Honest scope.
  Pause at decision points.
* **Commit at every green checkbox.** Tick the checkbox in this file in
  the same commit.


## The layered/onion architecture

The extraction pipeline is already layered:

```
SID bytes → 6502 disasm → engine-state model → musical events → USF
```

Each layer strips one type of engine-implementation detail. The build
direction is the inverse:

```
USF → musical events → engine model → asm → bytes → SID file
```

The middle layer — **engine model** — is the artifact this rewrite adds.
It's a Python representation of "what an engine does each frame,"
parametric over features. The model is configured by features the USF
carries; it does **not** know which engine produced the USF.

Layer responsibilities, top to bottom:

| Layer | Input | Output | Concern |
|---|---|---|---|
| **USF reader** | `.usf` file | `UsfFile` dataclass | Parse + validate |
| **Musical events** | `UsfFile` | per-voice event stream | Engine-blind decoding of pattern rows into note/rest/instr-change events with durations |
| **Engine model** | events + features | per-frame SID-write schedule (abstract) | Apply mechanism: tempo dispatch, modulation programs, terminators. Parametric over features the USF carries. **No engine identity.** |
| **Asm codegen** | schedule + features | 6502 asm source | Emit a play loop that, when called once per frame, produces the schedule's writes |
| **Assembler** | asm source | 6502 bytes | xa65 |
| **PSID wrapper** | bytes + USF meta | SID file | Header + load address |

The composer = engine-model + asm-codegen layers. The simpler layers
(parser, assembler, PSID) already exist and are stable.


## The feature matrix

Each USF declares (implicitly via content) which dimensions of the
feature matrix it uses. The composer emits exactly the code those
dimensions need. New engine = teaching the composer one or two new
features along one or two dimensions.

| Dimension | Values |
|---|---|
| Voice count | 1, 2, 3 |
| Pattern encoding | atomic bytes (1 byte/tick), (note,dur) pairs, command stream (1 byte/tick + embedded commands) |
| Voice timing | every-tick read, tick-counter state machine, dur-counter state machine |
| Tempo dispatch | single-tick, two-tempo (gate_off + note_load), CIA-driven |
| Modulation pipeline | (any combination of) vibrato LFO, PWM linear, PWM bidirectional, multi-step arpeggio, freq-hi slide (skydive), inc_by2 |
| Embedded commands | (any combination of) `$Bx` tempo, `$Cx` master vol, `$Dx` instrument change, `$Ex` song-pos jump, `$82` set duration |
| Terminator semantics | `$FE` stop, `$FF` loop, `$81` stop/skip (varies), `$80` rest, `$8C` rest, `$8D` end-song-on-Vn |
| Master vol handling | fixed at init, mutable mid-stream via `$Cx`, fade-progressive on voice's pattern-end |
| Inter-voice quirks | carry leak (bowden's 4-vs-5-byte timbre), `no_release` (Hubbard), `drum_prio` (Hubbard), hardcoded Vn PW sweep (Companion) |
| Voice-init seeding | zero-init, copy-from-overlap-region, copy-from-per-subtune-template |
| Off-table arpeggio | none, mirror engine-state region (`state_layout`) |
| Sub-engines | none, SFX (2-voice freq-sweep + register snapshot), digi (1-bit wavetoggle or 4-bit PCM dispatcher) |

The current 6 shapes correspond to specific points (or small clusters)
in this matrix. After the rewrite they're feature configurations.


## Current state — what's where

Before starting any phase, read:

* `pipelines/universal_codegen.py` — the file being rewritten. ~4400
  lines as of `3d14b38`. Five shape emitters + the lifted Hubbard '85
  parametric core (`_hubbard_emit_sid` + ENGINE asm template + `_Inputs`).
* `pipelines/build_from_usf.py` — 40-line wrapper around `emit_sid`.
* `pipelines/hubbard/note_codec.py` — `BitPackCodec` for Hubbard's
  pattern bitstream. Reused by the Hubbard '85 emitter.
* `pipelines/hubbard/inst_generalize.py` — `InstrumentModel` +
  `ArpSpec` / `VibratoSpec` / `PwmSpec`. The current Python-side
  representation of an instrument program.
* `pipelines/hubbard/types.py` — `Score` / `Voice` / `Note` —
  intermediate score representation the Hubbard '85 codegen uses.
* `pipelines/hubbard/sfx.py` — SFX sub-engine extraction + `SoundEffect`.
* `pipelines/hubbard/engine_constants.py` — digi player asm + digi
  region dispatch tables.
* `pipelines/hubbard/verify.py` / `verify_cycle.py` — the verdicts.
* `src/usf/types.py` — `UsfFile`, `MusicSubtune`, `DigiSubtune`,
  `SfxSubtune`, `Instrument`, `Pattern`, `NoteRow`, `Orderlist`, etc.
* `docs/usf_representation_principle.md` — load-bearing principle doc.
* HVSC: `hvsc84/`. Index DB: `hvsc84.db` (Python sqlite3, no CLI).

The 6 shapes that need to disappear:

1. **atomic 1-voice** — henrys_house. 1 voice; every-tick byte read;
   `$FF` resets master vol + pos.
2. **atomic 3-voice + carry leak** — bowden_canonical. 3 voices;
   inter-voice 4-vs-5-byte timbre quirk; `$FF` substitutes first byte.
3. **pair** — yes_tune family. 3 voices; tick-counter state machine;
   (note, dur) pairs; `$81` stop, `$FF` loop, `$82` set_dur.
4. **command_stream** — clever_music. 3 voices; every-tick byte read +
   embedded `$Bx`/`$Cx`/`$Dx`/`$Ex` commands; recursive interpreter;
   16-instr palette + song_pos sync.
5. **companion** — Up_up_and_Away. 3 voices; two-tempo (gate_off +
   note_load); V3 PW_LO sweep; `$80`+pitch = early release; `$8C` rest,
   `$8D` end-song-on-V3; 32-byte per-subtune init template.
6. **hubbard85** — 11 Hubbard '85 engines + 5_Title_Tunes (compound).
   Multi-pattern orderlists; full modulation pipeline (vibrato + PWM
   modes + arp + slide + inc_by2); pitch-byte dispatch; off-table arp
   via `statebuf`; SFX sub-engine; digi region builder.


## Phased plan

Each phase is a single commit with byte-exact regression-passing. Tick
the checkbox in the same commit that lands the work. If a phase grows
unexpectedly, split it.

### Phase 0 — Read in (no code)

- [ ] Read this plan in full.
- [ ] Read `docs/usf_representation_principle.md` in full.
- [ ] Check `~/.claude/projects/-home-jtr-sidfinity/memory/MEMORY.md`
      and any project memories the work touches.
- [ ] Confirm regression baseline runs (commands below).

Baseline commands:

```python
# Hubbard 71/71 baseline
from importlib import import_module
from pipelines.build_from_usf import build_from_usf
from pipelines.hubbard.verify import verify_all
HUB = [('commando','COMMANDO','Commando'),
       ('thing_on_a_spring','THING_ON_A_SPRING','Thing_on_a_Spring'),
       ('chimera','CHIMERA','Chimera'),
       ('monty','MONTY','Monty_on_the_Run'),
       ('action_biker','ACTION_BIKER','Action_Biker'),
       ('confuzion','CFG','Confuzion'),
       ('hunter_patrol','HUNTER_PATROL','Hunter_Patrol'),
       ('battle_of_britain','CFG','Battle_of_Britain'),
       ('human_race','HUMAN_RACE','Human_Race'),
       ('devils_galop','DEVILS_GALOP','Devils_Galop')]
base = 'hvsc84/MUSICIANS/H/Hubbard_Rob'
total_ok = total = 0
for nick, cn, fn in HUB:
    cfg = getattr(import_module(f'pipelines.hubbard.{nick}.config'), cn)
    out = f'{base}/{fn}.sidfinity.sid'
    build_from_usf(f'{base}/{fn}.usf', out)
    r = verify_all([(cfg, out)])
    rows = list(r.values())[0][0]
    p = sum(1 for _, b in rows if b)
    total_ok += p; total += len(rows)
print(f'Hubbard: {total_ok}/{total}')   # must print 71/71
```

```python
# Companion-strain baselines (instruction stream)
from pipelines.build_from_usf import build_from_usf
from pipelines.hubbard.verify_cycle import writelog_capture, compare_instruction_stream
import struct
TUNES = [
    ('hvsc84/GAMES/G-L/Henrys_House.sid', 8.0),
    ('hvsc84/MUSICIANS/B/Berry_Vic/Bach_Sonata.sid', 8.0),
    ('hvsc84/DEMOS/UNKNOWN/Yes_Tune.sid', 8.0),
    ('hvsc84/GAMES/S-Z/Soldier_of_Fortune.sid', 8.0),
    ('hvsc84/MUSICIANS/C/Clever_Music/Gyroscope.sid', 8.0),
    ('hvsc84/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.sid', 8.0),
]
for sid, dur in TUNES:
    out = sid.replace('.sid', '.sidfinity.sid')
    build_from_usf(sid.replace('.sid','.usf'), out)
    with open(sid,'rb') as f: raw = f.read(0x10)
    n_sub = struct.unpack('>H', raw[0x0E:0x10])[0]
    for st in range(n_sub):
        a = writelog_capture(sid, subtune=st, duration=dur)
        b = writelog_capture(out, subtune=st, duration=dur)
        r = compare_instruction_stream(a, b, skip_init=True)
        # Match the pre-rewrite baseline (some are partial pre-existing;
        # don't fix those, just preserve).
        print(sid, st, r)
```

### Phase 1 — Audit (no code, produces a spec)

The audit produces a feature-config spec for each current shape. The
spec drives Phase 2's engine-model design. Output: this section gets
filled in below.

- [ ] Audit `atomic 1-voice` (henrys_house) — fill in feature config below.
- [ ] Audit `atomic 3-voice + carry leak` (bowden_canonical).
- [ ] Audit `pair` (yes_tune family).
- [ ] Audit `command_stream` (clever_music).
- [ ] Audit `companion` (Up_up_and_Away).
- [ ] Audit `hubbard85` (the 11 Hubbard engines, considered as feature
      configurations — each engine's `EngineConfig` is already a
      feature-bag, so the audit is the projection of each into the
      composer's dimensions).
- [ ] Identify gaps where the feature matrix above doesn't cover an
      engine's mechanism. Update the matrix.
- [ ] Identify shared mechanism — features used by multiple engines.

#### Feature config — atomic 1-voice (henrys_house)

(to fill in during audit)

#### Feature config — atomic 3-voice + carry leak (bowden_canonical)

(to fill in during audit)

#### Feature config — pair (yes_tune)

(to fill in during audit)

#### Feature config — command_stream (clever_music)

(to fill in during audit)

#### Feature config — companion (Up_up_and_Away)

(to fill in during audit)

#### Feature config — hubbard85 (11 engines × their EngineConfig deltas)

(to fill in during audit)

### Phase 2 — Engine-model design

The engine-model layer is a Python representation of "what the engine
does each frame," parametric over features. Decisions to make:

- Single dataclass with many optional fields, or composition of feature
  objects? Probably the latter — each feature is a small dataclass that
  the composer chains.
- How does the model express per-frame timing? Probably as an explicit
  per-voice state machine spec (current state, transitions, register
  writes per state).
- How does the model express modulation programs? Probably as named
  modulation objects on each instrument — `Vibrato`, `PwmLinear`,
  `PwmBidirectional`, `Arpeggio`, `FreqSlide`, `IncBy2` — that the
  codegen layer emits per-frame asm for.

- [ ] Sketch the engine-model dataclass(es). Land in a new module
      `pipelines/engine_model.py` (or similar).
- [ ] Write a unit test: each current shape's USF can be converted into
      an engine-model instance. No asm yet — just verifying the model is
      expressive enough.
- [ ] Document the model in `docs/engine_model.md`.

### Phase 3 — Model → asm codegen (henrys first)

Start with the simplest engine. Build the asm-codegen layer just enough
to handle henrys_house's feature config. Verify byte-exact. Commit.

- [ ] Write `pipelines/composer.py` (or extend `universal_codegen.py`)
      with the model → asm transformer. Initial scope: enough features
      to reproduce henrys's instruction stream byte-exact.
- [ ] Wire `pipelines.build_from_usf.build_from_usf` to use the
      composer when the USF is henrys-shaped. Keep the old shape
      dispatch for the others (transitional).
- [ ] Verify henrys still byte-exact. Commit.
- [ ] Delete the `atomic 1-voice` shape emitter from
      `pipelines/universal_codegen.py`. Verify. Commit.

### Phase 4 — Add bowden's features

- [ ] Add inter-voice carry-leak feature to the engine model.
- [ ] Add `$FF` loop substitution semantics.
- [ ] Multi-subtune per-voice state seeding (init_pos_v1/v2/v3).
- [ ] Express bowden_canonical as a feature config. Verify the 17/18
      previously-passing tunes still match. Melonmania sub 1 stays
      pre-existing partial.
- [ ] Delete the `atomic 3-voice + carry leak` shape emitter. Commit.

### Phase 5 — Add yes_tune's features

- [ ] Tick-counter voice timing.
- [ ] (note, dur) pair pattern encoding.
- [ ] `$81` stop + `$FF` loop + `$82` set_dur terminator semantics.
- [ ] `gain_init` (full / preserve).
- [ ] Per-voice initial state byte (silent / load-pattern).
- [ ] Express yes_tune as a feature config. Verify 9/9.
- [ ] Delete the `pair` shape emitter. Commit.

### Phase 6 — Add clever_music's features

- [ ] Embedded `$Bx` (tempo) / `$Cx` (master vol) / `$Dx` (instrument)
      / `$Ex` (song-pos jump) command bytes.
- [ ] Recursive command interpreter / "command doesn't consume a tick"
      semantics.
- [ ] Mutable tempo + mutable master vol mid-stream.
- [ ] Instrument palette + dynamic timbre copy on `$Dx`.
- [ ] Song-pos sync counter (E0..E5 cycling).
- [ ] Express clever_music as a feature config. Verify (Gyroscope OK,
      Fairlight stays pre-existing partial).
- [ ] Delete the `command_stream` shape emitter. Commit.

### Phase 7 — Add companion's features

- [ ] Two-tempo dispatch (`gate_off_tick` + `note_load_tick`).
- [ ] Per-subtune 32-byte init template + per-voice locked timbre.
- [ ] `$80`+pitch = early-release feature.
- [ ] `$8C` rest, `$8D` end-song-on-Vn terminator semantics.
- [ ] Hardcoded Vn PW_LO sweep (V3 += 5 every other frame).
- [ ] Filter setup ($D416 + $D417 at init).
- [ ] Post-terminator orderlist padding bytes (engine reads past `$8D`).
- [ ] Express Up_up_and_Away as a feature config. Verify subs match
      pre-rewrite numbers (subs 0/1/2/4 1-event-short + sub 3
      divergence are pre-existing).
- [ ] Delete the `companion` shape emitter. Commit.

### Phase 8 — Absorb Hubbard '85

The largest phase. The Hubbard '85 parametric core is already
feature-bag-ish (`_Inputs` is essentially a feature config); the work
is **translating** it into the engine-model representation.

- [ ] Vibrato LFO feature.
- [ ] PWM linear feature.
- [ ] PWM bidirectional feature.
- [ ] Multi-step arpeggio feature (including off-table via state_layout).
- [ ] Freq-hi slide (skydive) feature.
- [ ] Inc_by2 odd-frame slide feature (with optional late-gate variant).
- [ ] Drum-slide (per-note portamento) feature.
- [ ] Multi-pattern orderlist dispatch (`$FE`/`$FF` terminators).
- [ ] Pitch-byte off-table arpeggio (via state_layout mirror).
- [ ] Hard-restart writes (gate-off + ad=0 + sr=0).
- [ ] Drum-priority gate (first-note suppression).
- [ ] No-release flag.
- [ ] Tie + drum_trig per-note effects.
- [ ] Master vol fade-progressive feature.
- [ ] Per-subtune mechanism overrides (5_Title_Tunes — per-sub
      speed_ctr_init / incby2_step / incby2_late_gate / ovseed).
- [ ] Stop-fill terminator behavior.
- [ ] Frame-ctr-init seeding.
- [ ] CIA1 timer programming.
- [ ] SFX sub-engine.
- [ ] Digi region builder (Chimera).
- [ ] Express each of the 11 Hubbard engines as a feature config.
      Verify 71/71 byte-exact preserved. Commit per engine.
- [ ] Delete the `hubbard85` shape emitter + `_hubbard_emit_sid` +
      ENGINE asm template + `_Inputs` + all the now-obsolete adapter
      code. Commit.

### Phase 9 — Cleanup

- [ ] Delete `pick_features`'s shape-detection branches. The composer
      reads the USF directly.
- [ ] Delete the `applies_to` shape detection. (Or: it just returns
      True for any well-formed USF since the composer is universal.)
- [ ] Delete `_is_pair_shape`, `_is_command_stream_shape`,
      `_is_companion_shape`, `_has_rich_modulation`,
      `_has_multi_pattern_orderlists`, `_has_sfx_subtunes`,
      `_has_state_layout`. No shape detection anywhere.
- [ ] Update `pipelines/universal_codegen.py`'s module docstring to
      describe the composer architecture.
- [ ] Update `docs/usf_representation_principle.md` if any of the
      USF/composer boundary changed.
- [ ] Update `CLAUDE.md`'s file table.
- [ ] Update or write project memory for the composer architecture.
- [ ] Final full regression — Hubbard 71/71 + all companion strains.


## Things to actively NOT do during the rewrite

* **Don't fix pre-existing partial cases.** Melonmania sub 1, Fairlight,
  Up_up_and_Away subs 0/1/2/4 + sub 3 — these are orthogonal to the
  composer rewrite. Note them; don't touch them. If a phase accidentally
  fixes one, great — but don't go hunting.
* **Don't change USF format.** The composer reads the existing USF.
  If the engine model needs information the USF doesn't carry, that's
  a separate USF design question requiring its own user decision.
* **Don't change verification tooling.** `verify_all` and
  `compare_instruction_stream` are stable contracts.
* **Don't optimize for code size or asm cycle count.** The composer's
  output is correct if the instruction stream matches. Performance
  optimization is later.
* **Don't add features speculatively.** Only add features a current
  engine uses. The composer grows engine-by-engine, not by anticipating
  hypothetical future engines.


## Open questions for future sessions

* **Should the engine model expose per-voice schedules explicitly, or
  emit asm directly?** The two extremes: (a) generate an in-memory
  per-frame trace, then trivially codegen a write-this-trace-to-SID
  loop — but the asm becomes huge for long songs; (b) generate
  parametric asm that, at runtime on the C64, *computes* the trace —
  which is what every existing shape does. (b) is correct and is what
  this rewrite assumes; (a) is a sanity-check / debug path worth having
  as a Python interpreter of the engine model.
* **Where do `EngineConfig` (legacy Python config objects in
  `pipelines/hubbard/<engine>/config.py`) fit in?** Today they drive
  extraction; nothing in the build path looks at them. After the rewrite
  they probably stay as extraction-side configs. Confirm and document.
* **How does the audit handle the 11 Hubbard engines? Are they 11
  feature configs or 11 small `EngineConfig` deltas on top of a base
  config?** Probably the second — most Hubbard engines share a base
  `_Inputs` and override a handful of fields. The composer should treat
  these the same way.
* **Compound builds (5_Title_Tunes).** A single PSID packs 5
  sub-engines with a dispatcher. The composer needs to support this
  layout. Today it's handled by `pipelines/hubbard/five_title_tunes/
  unified/`. Audit how this interacts with the engine model.


## Plan-update protocol

When work happens:

1. Tick the checkbox in this file.
2. If the work surfaced a new feature dimension or principle, add it
   here.
3. If an "open question" got answered, move the answer into the
   relevant section and remove the question.
4. The plan update lives in the same commit as the work it describes.
   Reviewer can read both at once.
