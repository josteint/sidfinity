# SIDfinity

![alpha](https://img.shields.io/badge/status-alpha-orange)

The eventual goal: train a neural network to generate new C64 SID music as playable `.sid` files.

To get there, we first have to take ~60,000 existing SID files from the [HVSC archive](https://hvsc.de/) and translate them into a single uniform format a model can learn from. That's what this repo is mostly about right now. The model itself is downstream.

## What's a SID file, and why is this hard?

A `.sid` file isn't audio. It isn't notes-and-instruments either. It's **6502 machine code** — a tiny program that, when run on a Commodore 64, writes registers to the SID sound chip 50 times a second.

That means *every SID file is its own music player*. There is no standard music format underneath. Different composers used different "engines": Rob Hubbard's player, GoatTracker, JCH NewPlayer, DMC, Galway, Cybertracker, [dozens more](pipelines/). Each engine has its own custom binary layout for the music data — instruments, note patterns, orderlists — that *only that engine's player code* knows how to interpret. From the outside, every SID is a black box.

This makes machine-learning on SIDs awkward. You can't train on raw bytes — they don't have shared structure. You need to first translate every black box into a common language. That's hard for several reasons.

**You have to reverse-engineer each engine.** Most C64 music engines are 30–40 years old, sometimes from lost source. To extract music from a SID file, you have to disassemble the player code, watch what bytes it reads from where, and infer what those bytes mean. Each engine is days-to-weeks of reverse engineering.

**Engines have *quirks*.** Even after you've extracted the data, the player code does subtle things to it that aren't in the data. Concrete examples we hit in Hubbard's player:

- **Drum noise burst.** Drum instruments emit a 3-frame `$80` (noise waveform) burst at the start of every note. That burst lives only in the player's code, not in the instrument data.
- **Aliased frequency table.** The freq table has 96 entries (8 octaves) but the player aliases slot 104 to "voice 1's control byte". When a percussion note "plays pitch 104," it's actually triggering a hardcoded audio behaviour by indexing past the table.
- **Per-voice direction state.** Bidirectional pulse-width modulation tracks its direction *per voice, not per instrument*. Switching to a new bidirectional instrument inherits the previous one's direction. We had a working pipeline that flipped one voice's PWM 180° out of phase for an entire song before we noticed.
- **Vibrato carry leak.** Vibrato's last `ADC` doesn't `CLC` first, so its carry flag leaks into the *next* unrelated instruction (the linear PWM update), making PW occasionally `+speed+1` instead of `+speed`. This isn't a bug in Hubbard's code — it's an intentional cycle-saving trick. But it's not in the data anywhere.

If your converter doesn't replicate these quirks, the rebuilt song *plays the right notes but sounds wrong*. We found all of those by listening, not by reading code. A typical bug report from the user listening to a candidate rebuild was *"sounds a bit washed out, like the lead voice is afraid of being itself."* That turned out to be a 32-frame stretch where one specific instrument byte was being misread, swapping a lead instrument for a bass instrument's envelope. Frame-by-frame register comparison hadn't caught it; the ear did.

**Different engines have entirely different quirks.** Hubbard's quirks aren't Bowden's, which aren't GoatTracker's. We're now two engine families in, and each family has surfaced its own family-specific tricks. A second family validating the approach was a major milestone — but it's still only two of the ~5–10 families needed to cover HVSC.

**60,000 files.** Even if each engine takes a couple of weeks, ~5–10 engines will cover most of the catalogue. The trick is getting each one *right*, because subtle errors compound: a model trained on subtly wrong data learns subtly wrong music.

**The ear is the final judge.** We compare the rebuilt SID's chip register state to the original frame-by-frame, and that catches a lot. But sometimes the registers match and the audio still sounds off — intra-frame timing differences, envelope retrigger nuances. The user noticing "this doesn't sound right" is sometimes the only signal we have. We try to track those down to a concrete data difference, but it's not always frame-aligned.

## How we approach it

The architectural bet: **engine mechanism stays out of the universal format; only the musical content goes in.**

```
  any SID  ──►  per-engine extract  ──►  USF song  ──►  shared composer  ──►  rebuilt SID
              (binary → musical data)   (universal)        (universal)
```

What's universal:

- **One format**, USF (Unified SID Format) — engine-name-blind, self-contained. It describes notes, patterns, instruments, effects in engine-neutral terms. The reader/writer lives in [`src/usf/`](src/usf/); the spec is in [`docs/usf_format.md`](docs/usf_format.md); the representation principle ([`docs/usf_representation_principle.md`](docs/usf_representation_principle.md)) is load-bearing for any schema change.
- **One composer**, [`pipelines/composer.py`](pipelines/composer.py) (~5,300 lines). 18 routine-chunk emitters + data emitters + USF-to-input adapters, parameterised by typed feature dataclasses (`StateLayoutMirror`, `FadeProgressive`, `SubtuneSpec`, …). No `if engine == "Hubbard"` branches anywhere; engine-specific behaviour is data on `EngineConfig`, never a code path.

What's per-engine:

- **An extract** that knows how to parse that engine's binary layout (e.g. `pipelines/hubbard/commando/extract/`).
- **A typed config** that captures the engine's quirks declaratively (per-engine `config.py` + `engine_constants.py`).

The bet that "every engine quirk reduces to typed musical data" has held up so far. The Human Race migration is a small case study: it surfaced five new effects (downslide, drumarp, skydive, PWmode, per-note slide) — all five collapsed cleanly into shared-core effects (`freq_slide`, `fx_arp`, `fx_incby2`, `fx_pwm`, `fx_drumslide`) without growing the schema.

## Where we are

**130 subtunes byte-exact across two engine families** (as of June 2026):

- **Hubbard '85 family** — 12 engines, 71/71 subtunes byte-exact. Action Biker, Battle of Britain, Chimera (incl. 1-bit digi), Commando, Confuzion, Devils Galop, 5 Title Tunes, Human Race, Hunter Patrol, Monty on the Run, One Man and his Droid, Thing on a Spring.
- **Companion family** — 44/44 subtunes byte-exact across six sub-engines. Hubbard's 1984 *Up, up & Away!*; the Bowden-canonical engine from the *Companion to the Commodore 64* type-in book (12 SIDs); Clever_Music (Fairlight, Gyroscope, plus the Back_to_the_Future banking trampoline variant); Henrys_House (single-voice); Yes_Tune (incl. Soldier_of_Fortune, 8 subtunes); Commodore_64_Music_Examples (15 subtunes across two bundled engine families).

`tools/regression.py` is the verdict. Cycle-strict instruction-stream verified via `siddump --writelog` (not just per-frame register snapshots).

The verification path matters here. We compare per-frame `$D400–$D418` register snapshots from py65 (md5-exact) for the music engines, and switch to cycle-strict `siddump --writelog` comparison for digi (Chimera) and any tune where dispatch timing matters. py65 silently misses dispatch bugs — CIA timer, PSID speed — so any new engine also gets an ear-test in real sidplayfp before declaring done.

### Honest limitations

- **Two engine families is not five.** The next family (likely DMC or JCH NewPlayer) is the next real test of "the composer doesn't grow `if engine == ...` branches." Each new family probes the architecture differently.
- **Some SIDs can't fit the principled USF at all.** The Jay_Derrett engine (25 SIDs) is aperiodic by design — voices never simultaneously realign, the song is conceptually infinite, and storing a finite trace requires either an arbitrary cut-off or sub-jump-table positional info that violates the representation principle. Those are listed in [`tools/excluded_sids.json`](tools/excluded_sids.json) and refused by the pipeline with a pointer back to the JSON.
- **Quirk discovery is still manual.** We hand-discover quirks per engine via py65 tracing + listening. Auto-extracting them from a binary (symbolic execution, abstract interpretation) is the highest-leverage thing we don't have yet.
- **The ear remains the final judge.** Frame-exact register comparison catches most things, cycle-strict instruction comparison catches more, but neither guarantees the audio sounds right. That doesn't scale to 60k files; we'll need a more automated signal eventually.

### What's next

1. **A non-Hubbard, non-Companion engine family.** DMC, JCH NewPlayer, or Galway. Each new family is the next real test of the architecture; pick by HVSC coverage.
2. **In-progress migrations.** Jay_Derrett (25 SIDs; scanner + 15/25 Type-A engine data dumped to JSON; USF schema + composer + verify still pending).
3. **HVSC coverage queries.** [`hvsc84.db`](hvsc84.db) is the SQLite index — engine classification + per-SID build status. Drives "which engine should we pick next" by coverage / runtime.
4. **Auto-quirk extraction.** Long-tail: symbolic execution over the original 6502 to surface engine quirks without hand-RE. Drops "weeks per engine" to "hours". The single biggest leverage point for HVSC scale.

## Pipelines

```
pipelines/
├── composer.py         The shared composer (~5,300 lines)
├── build_from_usf.py   Public entry point
├── engine_model.py     Typed feature dataclasses
├── hubbard/            Hubbard '85 family — shared core + 12 per-engine subdirs
│   ├── verify.py             per-frame snapshot verification
│   ├── verify_cycle.py       cycle-strict instruction-stream verification
│   ├── engine_constants.py   freq tables, digi player asm
│   ├── note_codec.py         bitstream note encoder + decoder asm
│   ├── inst_*.py             instrument modelling
│   ├── sfx.py / sample.py / digi_pack.py / flac_io.py
│   └── <engine>/             config.py + extract/{engine_model,to_usf}.py
└── companion/          Companion family — shared core + 6 per-engine subdirs
    ├── config.py / engine_constants.py / to_usf.py
    └── <engine>/             config.py + extract/
```

Adding a new Hubbard '85 engine is one `config.py` + one `extract/` package; the
shared composer is unchanged. See the `migrate-hubbard-engine` skill at
`.claude/skills/migrate-hubbard-engine/` for the full procedure, and
[`pipelines/README.md`](pipelines/README.md) for the per-pipeline layout.

| Step | File |
|---|---|
| 1. Parse engine binary | `<family>/<engine>/extract/decompile.py` |
| 2. Lift to engine model `(T, I, S)` | `<family>/<engine>/extract/engine_model.py` |
| 3. Engine config / parameters | `<family>/<engine>/config.py` |
| 4. Emit USF | `<family>/<engine>/extract/to_usf.py` |
| 5. Compose 6502 player + PSID wrap | `pipelines/composer.py` (shared) |
| 6. End-to-end build | `pipelines/build_from_usf.py` |
| 7. Verify (byte-exact) | `pipelines/hubbard/verify.py` or `verify_cycle.py` |

## Build

```bash
source src/env.sh                              # PATH for siddump etc.
bash tools/build.sh                            # libsidplayfp + siddump (one-time)

# Full pipeline regression — Hubbard + Companion + C64ME (~130 subtunes)
python3 tools/regression.py

# Rebuild one engine end-to-end (example: Commando)
python -c "
from pipelines.hubbard.commando.extract.to_usf import write_commando_usf
from pipelines.hubbard.commando.config import COMMANDO
from pipelines.build_from_usf import build_from_usf
write_commando_usf(COMMANDO, 'hvsc84/MUSICIANS/H/Hubbard_Rob')
build_from_usf('hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.usf',
               'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')
"

# Verify byte-exact (per-frame SID register md5)
python -c "
from pipelines.hubbard.verify import verify_all
from pipelines.hubbard.commando.config import COMMANDO
print(verify_all([(COMMANDO, 'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.sidfinity.sid')]))
"

# Extract smoke tests
pytest pipelines/
```

Requires: g++ (C++17), Python 3.10+. The xa65 assembler lives in-tree at
`tools/xa65/xa/xa`.

## HVSC index — `hvsc84.db`

A SQLite catalogue of every SID in `hvsc84/` with engine classification +
per-SID build status. The pipeline updates it automatically (build →
`sidfinity_md5`, USF write → `usf_path`, verify → `verify_*`). Initial
populate / full rebuild via `tools/build_sid_db.py` (~20 s incremental).

There's no `sqlite3` CLI on this system — query with Python:

```python
import sqlite3
db = sqlite3.connect('hvsc84.db')
for path, title in db.execute(
    "SELECT path, title FROM sids "
    "WHERE engine='Rob_Hubbard' AND pipeline IS NULL "
    "ORDER BY songlength_s DESC LIMIT 10"
): print(path, title)
```

## Layout

```
pipelines/         Active engines — hubbard/ (Hubbard '85) + companion/ + shared composer
src/               USF grammar + reader/writer, shared utilities, exclusions, env.sh
docs/              Specs — USF format, representation principle, init report, plan
tools/             Build tools (xa65, siddump, libsidplayfp) + regression.py + excluded_sids.json
hvsc84/            HVSC #84 collection (not in git, gitignored)
hvsc84.db          SQLite index over HVSC (build status, engine classification)
deprecated/        Earlier project phases — see deprecated/<topic>/README.md
```

Earlier workstreams (pre-USF-v2 codegen, GT2 / GoatTracker pipeline, Lean 4
codegen, USF v1 engines, Grade S/A/B/C/F bucketing tools, player
reverse-engineering toolkit, accumulated research material) all live under
`deprecated/<topic>/` with their own READMEs.

## Docs

- [USF specification](docs/usf_format.md)
- [USF representation principle](docs/usf_representation_principle.md) — load-bearing for any schema change
- [SID init report](docs/sid_init_report.md) — empirical init trichotomy across HVSC
- [Development plan](docs/PLAN.md)
- [Per-engine research notes](pipelines/) — `pipelines/<engine>/docs/` for ~47 SID engines

## License

The SIDfinity pipeline (Python code, USF format, composer) is released under
the **MIT License**. See [LICENSE](LICENSE).

The C/C++ tools (`siddump`, `sidrender`) link against GPL v2 libraries and are
distributed under **GPL v2**. See [tools/LICENSE](tools/LICENSE).

## Acknowledgments

[libsidplayfp](https://github.com/libsidplayfp/libsidplayfp) is used for SID emulation (GPL v2). [xa65](https://github.com/af65/xa65) is used for 6502 assembly (GPL v2).
