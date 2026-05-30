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

- [x] Read this plan in full.
- [x] Read `docs/usf_representation_principle.md` in full.
- [x] Check `~/.claude/projects/-home-jtr-sidfinity/memory/MEMORY.md`
      and any project memories the work touches.
- [x] Confirm regression baseline runs (commands below).

**Baseline as of plan commit `1e6de93`:**
* Hubbard 71/71 byte-exact through `verify_all`.
* Henrys_House, Bach_Sonata (bowden), Yes_Tune, Soldier_of_Fortune
  (8 subs), Gyroscope, Up_up_and_Away 4/5 — all match pre-rewrite
  numbers via `compare_instruction_stream`. Up_up_and_Away sub 3 is
  the only pre-existing partial in this set.

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
spec drives Phase 2's engine-model design.

- [x] Audit `atomic 1-voice` (henrys_house) — fill in feature config below.
- [x] Audit `atomic 3-voice + carry leak` (bowden_canonical).
- [x] Audit `pair` (yes_tune family).
- [x] Audit `command_stream` (clever_music).
- [x] Audit `companion` (Up_up_and_Away).
- [x] Audit `hubbard85` (the 11 Hubbard engines, considered as feature
      configurations — each engine's `EngineConfig` is already a
      feature-bag, so the audit is the projection of each into the
      composer's dimensions).
- [x] Identify gaps where the feature matrix above doesn't cover an
      engine's mechanism. Update the matrix (see "Audit-derived feature
      matrix updates" below).
- [x] Identify shared mechanism — features used by multiple engines
      (see "Cross-shape mechanism table" below).

#### Feature config — atomic 1-voice (henrys_house)

Sole tune: `hvsc84/GAMES/G-L/Henrys_House.sid` (1 subtune).
Emitter: `_emit_1voice_init` / `_emit_1voice_play` in universal_codegen.

| Dimension | Value |
|---|---|
| Voice count | 1 active (slots 2, 3 are placeholders with empty orderlists) |
| Pattern encoding | atomic byte per tick |
| Voice timing | every-tick read |
| Tempo dispatch | single-tick, `tempo_const` RAM byte loaded from per-subtune `tempo_tab` (in practice fixed across this tune's 1 subtune at value 8) |
| Modulation | NONE |
| Embedded commands | NONE |
| Terminator semantics | `$00-$7F` = note (play freq + 5-byte timbre + ctrl|1); `$80` = rest (write ctrl gate-off); `$81` = skip (no SID write); `$FF` = loop (write `$D418=master_vol` + reset pos to 0) |
| Master vol | fixed at init (`$0F` written at boot AND on every `$FF` loop) |
| Inter-voice quirks | N/A (1 voice) |
| Voice-init seeding | zero (v_pos=0, tempo_ctr=0, timbre fields loaded from per-subtune table) |
| Off-table arpeggio | NONE |
| Sub-engines | NONE |
| Freq table | 128 + 128 (256 bytes, Clever Music's table) |

#### Feature config — atomic 3-voice + carry leak (bowden_canonical)

Tunes: 18 SIDs (Berry Vic family, Hyper_Blast, Memory_1991,
Roundabout, Titanic, Surfchamp, Melonmania — Bowden_Bobby).
Emitter: `_emit_3voice_*` in universal_codegen.

| Dimension | Value |
|---|---|
| Voice count | 3 active |
| Pattern encoding | atomic byte per tick, indirect-(zp),Y reads per voice |
| Voice timing | every-tick read, V1 → V2 → V3 sequential dispatch |
| Tempo dispatch | single-tick, per-subtune `tempo_const` |
| Modulation | NONE |
| Embedded commands | NONE |
| Terminator semantics | `$00-$7F` = note; `$80` = rest; `$81-$FE` = skip (sets carry-leak flag on this voice); `$FF` = loop substitution (pos=1, replay orderlist[0] this tick) |
| Master vol | fixed at init (`$0F` once) |
| Inter-voice quirks | **carry leak**: a voice playing a skip ($81-$FE) sets `next_skip_sr`; the next voice writes 4-byte timbre (omit SR) instead of 5. On `$FF` loop, V1/V2 force the next voice's `this_skip_sr=1`; V3's `$FF` leaves it at 0. |
| Voice-init seeding | per-subtune tables: `init_v{1,2,3}_pos_tab`, `init_tempo_ctr_tab`, plus 5-byte timbre arrays × 3 voices |
| Off-table arpeggio | NONE |
| Sub-engines | NONE |
| Other | optional CIA1 timer A programming (Surfchamp: $40C7 for ~60Hz) |
| Freq table | 128 + 128 (256 bytes) |

#### Feature config — pair (yes_tune)

Tunes: 2 SIDs (Yes_Tune 1 subtune, Soldier_of_Fortune 8 subtunes — mix
of music + SFX). Emitter: `_emit_pair_*` in universal_codegen.

| Dimension | Value |
|---|---|
| Voice count | 3 slots; some voices silent (initial state byte = 0) |
| Pattern encoding | (note, dur) byte pairs |
| Voice timing | tick-counter state machine: `tick_ctr` decrements; play on 0 |
| Tempo dispatch | single-tick, `tempo_const` per-subtune |
| Modulation | NONE |
| Embedded commands | NONE |
| Terminator semantics | `$00-$7F dur` = note + arm tick_ctr; `$80 dur` = rest with duration; `$81` = stop voice (write ctrl gate-off + state=0); `$FF` = loop (reset ptr + recurse play_note) |
| Master vol | per-subtune `gain_init` ("full" writes `$D418=$0F`, "preserve" skips the write — SFX subtunes ride existing vol) |
| Inter-voice quirks | NONE |
| Voice-init seeding | per-voice 5-byte timbre (3 voices) + `pat_start lo/hi` per voice + initial state byte (0 silent / 2 load-pattern) per voice, all from per-subtune tables; `tick_ctr=0` |
| Off-table arpeggio | NONE |
| Sub-engines | NONE |
| Note | `fx:raw_NN` flag passthrough used by SoF SFX subtunes for muted-pitch triggers |
| Freq table | 128 + 128 (Clever Music's table) |

#### Feature config — command_stream (clever_music)

Tunes: 2 SIDs (Fairlight, Gyroscope — 1 subtune each).
Emitter: `_emit_cmd_*` in universal_codegen.

| Dimension | Value |
|---|---|
| Voice count | 3 |
| Pattern encoding | atomic byte per tick + embedded command bytes that don't consume a tick |
| Voice timing | dur-counter state machine: `dur_ctr` starts at 1, decrements per frame; `load_note` runs on `dur_ctr == 1` |
| Tempo dispatch | single-tick, `tempo_const` mutable mid-stream via `$Bx` |
| Modulation | NONE |
| Embedded commands | `$Bx` SET_TEMPO, `$Cx` SET_MASTER_VOL, `$Dx` SET_INSTRUMENT (copy 5 bytes from `inst_table`), `$Ex` PATTERN_JUMP (if `Y == song_pos`: jump via `song_table`, advance + wrap song_pos), `$82 dur` SET_DURATION (gate off + dur_ctr=N), unrecognized bit-7 = SKIP_BYTE + recurse |
| Terminator semantics | `$80` = rest (gate off); `$81` = skip (return); `$FF` = loop (reset ptr to `pat_start` + recurse). No song-end terminator — the engine reads adjacent memory past nominal end (similar to companion's read-past behavior) |
| Master vol | per-subtune init (`init_master_vol`), mutable mid-stream via `$Cx` |
| Inter-voice quirks | NONE |
| Voice-init seeding | `song_table[0..5]` → V1/V2/V3 ptrs; dur_ctr=1; per-subtune `init_song_pos` + `init_tempo_ctr` |
| Off-table arpeggio | NONE |
| Sub-engines | NONE |
| Other | 16-instrument palette (5-byte rows in `inst_table`); 6-entry `song_table` for `$Ex` dispatch (E0/E3 → V1, E1/E4 → V2, E2/E5 → V3); optional CIA1 timer A |
| Freq table | 128 + 128 (Clever Music's table) |

#### Feature config — companion (Up_up_and_Away)

Sole tune: `hvsc84/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.sid` (5 subtunes).
Emitter: `_emit_companion_*` in universal_codegen.

| Dimension | Value |
|---|---|
| Voice count | 3 |
| Pattern encoding | atomic byte per tick (no skip-byte runs — duration comes from `note_load_tick`) |
| Voice timing | global `g_tempo_ctr` increments per frame; on `== gate_off_tick` fires `maybe_gate_off` for all voices; on `== note_load_tick` resets and advances each voice's orderlist by 1 |
| Tempo dispatch | **two-tempo**: `gate_off_tick` (early-release timer) + `note_load_tick` (next-note timer), both per-subtune |
| Modulation | **hardcoded V3 PW_LO sweep**: `g_pwm_ctr` toggles 0/1 every frame; on the 1→0 transition, V3 pw_lo += 5 (carry=1 from `CMP #$01`) + write `$D410` |
| Embedded commands | NONE |
| Terminator semantics | `$00-$7F` = note (play pitch); `$80+pitch` = play pitch + schedule early release at next `gate_off_tick` (bit-7 flag held); `$8C` = rest (gate off); `$8D` = end-or-rest (gate off; on V3 also writes `$D418=0` + clears `g_song_alive`); engine reads past `$8D` into adjacent memory (`v{1,2,3}_pad_count` bytes) |
| Master vol | per-subtune fixed at init (`vol_filter` table); V3's `$8D` also writes `$D418=0` |
| Inter-voice quirks | V3's `$8D` is end-song (clears `g_song_alive` + writes `$D418=0`); V1/V2 `$8D` is just rest |
| Voice-init seeding | copy-from-per-subtune-32-byte-template (V1/V2/V3 each: pos=0, gate_off_flag=0, 5-byte timbre; plus globals: gate_off_tick, note_load_tick, init_tempo_counter, 6 zeros, init_pwm_ctr × 2). `g_tempo_ctr` and `g_pwm_ctr` aliased to `v_state+23` / `v_state+30` so the template copy seeds the runtime counters. |
| Off-table arpeggio | NONE |
| Sub-engines | NONE |
| Other | filter setup at init (`$D416 = filter_cutoff_hi`, `$D417 = 0`); orderlist post-`$8D` padding bytes per voice (`v{1,2,3}_pad_count`/`v{1,2,3}_pad_byte` per-subtune params); `ctrl_noGate` is per-voice (from `InitVoice.ctrl`), NOT from the instrument's waveform field |
| Freq table | 128 + 128 (Companion's own table) |

#### Feature config — hubbard85 (11 engines × their EngineConfig deltas)

The 11 Hubbard '85 engines + 5_Title_Tunes (compound) share one
parametric core (`ENGINE` asm + `_hubbard_emit_sid`). The `_Inputs`
dataclass is already a feature config — most fields below correspond
directly to `_Inputs` fields.

| Dimension | Value (defaults / range) |
|---|---|
| Voice count | 3; per-subtune `voice_start` table (2 = run V1+V2+V3; 1 = skip V3; 0 = also skip V2 — Action Biker sub 0 uses this) |
| Pattern encoding | bitpack codec — `BitPackCodec.dur_bits` + `BitPackCodec.inst_bits` per-engine. Per-pattern: 1 leading byte (note count) + packed bitstream of (pitch, duration, instr-change, tie, drum_trig) tuples |
| Voice timing | dur-counter state machine: per-voice `v_dur` decrements; on `< 0` calls `load_note` (codec-supplied). Sustain frames run effects only. |
| Tempo dispatch | single-tick global `speed_ctr` decrements; on underflow → `cur_resetspd` (per-subtune `subResetspd`) and one tick fires |
| Modulation | up to 6 pipelines per instrument: vibrato LFO (triangle), PWM linear (accumulator), PWM bidirectional (period+step+bounds), multi-step arpeggio (frame & ARP_MASK gates the +ARP_OFS semitones), freq-hi slide / "skydive" (fx bit 0), inc_by2 (odd-frame slide on `v_slide`, fx bit 1) — gated by `instrument.fx_flags` byte. Plus drum_slide (per-note portamento via `v_drumtrig`). |
| Embedded commands | NONE (instrument-change lives in the per-note instr byte; tie/no_release/porta in fx flags) |
| Terminator semantics | orderlist: `$FE` = stop (variants: plain stop, `freeze_on_stop` engines hold the note instead, `stop_fill` engines write `$D400-$D417 = STOP_FILL` byte and silence); `$FF` = loop (wraps to `orderLoop`). Per-note: tie ($40 high bit on inst byte), drum_trig (low 7 bits), no_release ($80 on drum_trig) |
| Master vol | fixed at init (`$0F`) for most engines; optional fade-progressive (`master_vol_subtrahend_voice` + `master_vol_base` + `master_vol_trigger`: `inst_change` vs `every_note`) — increments `vol_progress` on the configured voice's pattern-end, writes `$D418 = clamp(base - vol_progress, 0..$0F)` |
| Inter-voice quirks | `drum_prio` (first-frame note-start suppression on V1 — Hubbard suppresses voice 0's first note when set); per-note `no_release` (skips hard-restart writes) |
| Voice-init seeding | `ovseed` block: 6 per-voice state bytes (v_ctrl/pwm_period/pwm_dir/v_instr/v_durfield/v_slide) × 3 voices = 18 bytes, **read from offsets within the freq table** (engine state overlaps freq table at +205, +208, +214, +229, +232, +239 by default; per-engine `seed_offsets` overrides). `seed_overlap=False` zeros it (Human Race inits per-voice state at runtime). For 5_Title_Tunes: per-subtune ovseed (`per_subtune_ovseed`). |
| Off-table arpeggio | `state_layout` block defines a 48-byte mirror (`statebuf`) of engine state. Pitch ≥ 96 reads `statebuf[(pitch-96)*2]` for freq instead of the freq table. Layouts: `COMMANDO_STATEBUF_LAYOUT` (Commando family default) and Human Race's HR-specific layout. Optional `ns_offtab_decr_offset` for Thing on a Spring (decrements v_hubidx slot pre-read). |
| Sub-engines | **SFX**: 16 sound-effect records (`sfxdata`, 32 bytes each) + `init_sfx` + `sfx_play` — 2-voice register snapshot + freq-table pitch sweep. PSID header's `songs` count = `len(subtunes) + 16` when `has_sfx`. Engines: Commando, Monty, Action Biker, Chimera, Thing on a Spring, One Man and his Droid (all 16). Optional `sfx_state_ofs` rewires SFX state into the freq-table off-table region (Monty, One Man — engines whose SFX V2 sweep overruns into engine state). **Digi**: cycle-strict 1-bit wavetoggle or 4-bit PCM player; combined music+digi region via `_emit_combined_sid` + `chimera_psid_dispatcher`. Only Chimera today. |
| Engine knobs | `arp_interval` (default 12), `arp_period` (default 2), `arp_phase_invert` (One Man), `linear_pw_or`, `incby2_step` (default 2), `incby2_every_frame` (Human Race), `incby2_onset` (default 3), `incby2_late_gate` (Hunter Patrol — only fires when `v_dur < N`), `suppress_first_notestart`, `freeze_on_stop`, `speed_ctr_init` (delayed first note-load), `first_frame_gate_off`, `frame_ctr_init` (HP $1E vs default $FF), `tie_preserves_slide` (Confuzion, BoB), `hubidx_wrap_at_patend` (False for Thing on a Spring), CIA1 timer programming (via `psid_speed` bitmask) |
| Compound (5_Title_Tunes) | 5 sub-engines packed at non-overlapping LOAD addresses + dispatcher at original init/play vectors. Per-subtune mechanism overrides (`per_subtune_speed_ctr_init`, `per_subtune_incby2_step`, `per_subtune_incby2_late_gate`, `per_subtune_ovseed`) when any subtune diverges from the top-level defaults. |
| Freq table | 320 bytes (128 hi + 128 lo musical entries + 64 bytes of engine-state overlap region) |

### Audit-derived feature matrix updates

The original matrix needs these refinements:

* **Pattern encoding** — three distinct cases:
  - *atomic per-tick with skip runs*: 1 byte = 1 tick; duration encoded
    as note-byte + (D-1) skip bytes. (henrys, bowden, clever_music)
  - *atomic per-tick, no skip runs*: 1 byte = 1 note period (period
    duration comes from per-tune tempo dividers). (companion)
  - *(note, dur) pairs*: 2 bytes per row, duration in the second byte.
    (yes_tune)
  - *bitpack codec*: variable-bit-width pitch/dur/instr fields packed
    into a bitstream, 1 leading note-count byte per pattern.
    (Hubbard '85)
* **Voice-init seeding** — four variants:
  - zero (henrys)
  - per-subtune position + tempo tables (bowden, yes_tune, clever, Hubbard '85's per-subtune mechanism mode)
  - copy-from-32-byte-template (companion)
  - copy-from-overlap (Hubbard '85's ovseed reading freq-table bytes
    205/208/214/229/232/239)
* **Inter-voice quirks** — full set:
  - carry leak (bowden — 4 vs 5-byte timbre based on prior voice's note byte)
  - drum_prio (Hubbard — first-frame V1 note suppression)
  - no_release (Hubbard — per-note fx flag)
  - end-song-on-V3 (companion — V3's `$8D` clears `song_alive` + vol=0)
  - hardcoded Vn PW sweep (companion — V3 PW_LO += 5 every other frame)
* **Embedded command bytes** — clever_music's set is the union: $Bx
  tempo, $Cx vol, $Dx instrument, $Ex song-pos jump, $82 set_dur.
  Other shapes have none.
* **Master vol handling** — four variants:
  - fixed at init (most engines)
  - per-subtune fixed (yes_tune's `gain_init`, companion's `vol_filter`)
  - mutable mid-stream via embedded command (clever_music's `$Cx`)
  - fade-progressive (Hubbard '85 — TOAS, etc.)
* **Pattern terminators** — wide vocabulary:
  - `$80` rest, `$81` skip/stop, `$82` set_dur (only clever_music)
  - `$8C` rest (companion), `$8D` end-song-on-V3 (companion)
  - `$FE` stop, `$FF` loop (Hubbard '85), `$FF` loop substitution (bowden)
  - The same byte means different things in different shapes — the
    composer must model "what bytes terminate" as a feature, not
    assume specific values.
* **Modulation pipeline** — composable subset:
  - vibrato LFO (Hubbard, Confuzion)
  - PWM linear (Hubbard)
  - PWM bidirectional (Hubbard, Confuzion)
  - multi-step arpeggio (Hubbard) — plus off-table variant via state_layout
  - freq-hi slide / skydive (Hubbard)
  - inc_by2 odd-frame slide (Hubbard)
  - drum_slide per-note portamento (Hubbard)
  - hardcoded Vn PW sweep (companion — distinct from per-instrument PWM)
* **Sub-engines** — orthogonal additions:
  - SFX (Hubbard family — 16 records, 2-voice freq-sweep + register snapshot)
  - digi (Chimera 1-bit wavetoggle)
* **Off-table arpeggio** — `state_layout` block defines a per-engine
  scalar + per-voice layout. Triggered when pitch ≥ 96. Only Hubbard
  '85 uses this.
* **Compound builds** — 5_Title_Tunes packs N sub-engines + dispatcher
  in one PSID. Distinct from the per-subtune mechanism model — the
  sub-engines have non-overlapping LOAD addresses and the dispatcher
  routes by PSID subtune index.

### Cross-shape mechanism table

Mechanism reuse across shapes — features the composer can implement
once and have multiple shapes consume:

| Mechanism | Used by |
|---|---|
| per-subtune tempo_const RAM byte | bowden, yes_tune, clever_music, companion, Hubbard '85 |
| per-subtune init_pos / init_tempo_ctr tables | bowden, yes_tune, clever_music, companion, Hubbard '85 (per-subtune mechanism mode) |
| per-voice 5-byte timbre (pw_lo, pw_hi, ctrl, ad, sr) | bowden, yes_tune, clever_music, companion |
| pitch byte = (octave<<4) \| semitone | henrys, bowden, yes_tune, clever_music, companion |
| pitch byte = absolute semitone (semis = note + 12*octave) | Hubbard '85 |
| atomic-byte-per-tick play loop | henrys, bowden, clever_music |
| every-tick-read-but-tempo-gated voice dispatch | henrys, bowden, yes_tune, clever_music, Hubbard '85 |
| `$FF` = loop (reset ptr) | henrys, bowden (substitution variant), yes_tune, clever_music |
| `$D418 = $0F` master vol init | henrys, bowden, yes_tune (when `gain_init=full`), Hubbard '85 |
| optional CIA1 timer A programming | bowden (Surfchamp), clever_music, Hubbard '85 (`psid_speed` bitmask) |
| 256-byte freq table (128 hi + 128 lo, Clever Music's table) | henrys, yes_tune |
| 256-byte freq table (Companion's own) | bowden, companion |
| 320-byte freq table (Hubbard's, with state overlap) | Hubbard '85 only |
| recursive command interpreter | clever_music only |
| state_layout off-table arp | Hubbard '85 only |
| bitpack codec | Hubbard '85 only |
| SFX sub-engine | Hubbard '85 only |
| digi sub-engine | Hubbard '85 only (Chimera) |
| two-tempo dispatch (gate_off + note_load) | companion only |
| inter-voice carry leak | bowden only |
| hardcoded Vn PW sweep | companion only |
| early-release flag on pitch byte | companion only |

### Open audit findings

1. **Pitch byte encoding differs.** Companion/yes_tune/clever_music/
   bowden/henrys encode pitch as `(octave<<4) | semitone` (high nibble
   = octave, low nibble = semitone, 12 semitones per octave). Hubbard
   '85 encodes pitch as absolute semis (`semis = note + 12*octave`,
   running 0..95). The musical content is identical; only the byte
   layout differs. The composer's "musical events" layer should
   normalize to one representation (probably absolute semis since it's
   cleaner) and the encoder layer chooses the byte format.

2. **Freq table is engine mechanism, not USF content.** The 128-entry
   musical table is essentially identical across all engines (same
   12-TET frequencies for the SID's freq registers). The 64-byte
   "engine state overlap region" Hubbard uses is purely engine
   mechanism. The companion-strain "256-byte freq table" inlining in
   USFs today is data that should arguably live in the engine model,
   not the USF — but moving it is out of scope for this rewrite
   (which targets engine-model architecture, not USF format).

3. **`InitVoice.ctrl` is the per-voice ctrl byte** for companion (the
   `ctrl_noGate` in its template). Every other shape derives ctrl from
   `instrument.waveform[0]`. The composer needs both modes available
   under one model — probably as a per-voice "ctrl source" feature
   (instrument-derived vs init-voice-derived).

4. **The terminator byte vocabulary varies.** Same byte means
   different things across shapes (`$81` is skip in bowden/henrys but
   stop-voice in yes_tune; `$8D` is end-song in companion but unused
   elsewhere). The engine model needs to express "what bytes are
   terminators and what each means" as a per-engine parameter, not
   assume a canonical mapping.

5. **5_Title_Tunes compound** is genuinely structural — a PSID with
   5 packed sub-engines + dispatcher. The engine model needs to
   represent this as a top-level construct ("a single SID can hold
   N independent engine instances + a dispatcher"). Not just a "Hubbard
   '85 feature."

6. **Hubbard '85's `_Inputs` dataclass is the closest thing to an
   engine model we have today.** It's a feature bag the parametric
   ENGINE asm reads via xa65 equates + sentinel substitutions. The
   engine model design in Phase 2 should plausibly start by
   generalizing `_Inputs` — strip its Hubbard-specific assumptions
   and add the cross-shape features the audit surfaced.

### Phase 2 — Engine-model design

The engine-model layer is a Python representation of "what the engine
does each frame," parametric over features.

- [x] Sketch the engine-model dataclass(es). Land in a new module
      `pipelines/engine_model.py` (or similar).
- [x] Write a unit test: each current shape's USF can be converted into
      an engine-model instance. No asm yet — just verifying the model is
      expressive enough.
- [x] Document the model in `docs/engine_model.md`.

**Outcome (commit pending):**
* `pipelines/engine_model.py` defines the `EngineModel` top-level
  dataclass plus 14 sub-dataclasses spanning every feature dimension
  the audit found. Mostly optional fields — USFs that don't use a
  feature get `None`.
* `from_usf(usf)` builder reads each feature dimension independently
  from USF content (no engine identity, no shape selection). Phase 3+
  refines it as the codegen consumes the model.
* `tests/test_engine_model_audit.py` runs the builder against one+
  USFs per shape (11 tests). All pass — every shape's features are
  representable in the model.
* `docs/engine_model.md` documents the model + the builder's
  behavior + open items for Phase 3+.

**Audit findings landed in the model:**
* Pitch byte format split: `octave_semi_nibble` (5 shapes) vs
  `absolute_semi` (Hubbard '85). PatternConfig.pitch_byte_format.
* ctrl_source per-voice: `instrument_waveform` (5 shapes) vs
  `init_voice_field` (companion). VoiceConfig.ctrl_source.
* Terminator vocabulary as `byte_map: dict[int, TerminatorBehavior]`
  — captures the per-shape byte semantics without engine names.
* Hardcoded V3 PW sweep as `HardcodedPwSweep` — describes the
  mechanism (voice_idx + delta + period), not the engine.
* Compound builds (5_Title_Tunes) as `CompoundSpec` — top-level
  construct, not a Hubbard '85 feature.

**Decisions made during Phase 2:**
* `VoiceTimingMode` lists 3 values (`every_tick`, `dur_counter_decrement`,
  `tick_counter_decrement`). Removed an earlier `speed_ctr_underflow`
  proposal — that conflated tempo dispatch with voice timing. Hubbard's
  voice timing is `dur_counter_decrement` (per-voice `v_dur`); its
  tempo dispatch is `single_phase` (the global `speed_ctr` underflow
  is just an implementation of single-phase gating).
* Per-voice terminator dictionary lives on `TerminatorVocab`, not
  scattered across per-shape emitter functions. The codegen reads
  `byte_map[byte]` directly.
* Modulation programs are explicit fields on `InstrumentProgram`
  (not a `list[Modulation]` variant). Each modulation has a fixed
  slot; codegen emits asm for non-None slots.

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
