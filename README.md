# SIDfinity

![alpha](https://img.shields.io/badge/status-alpha-orange)

The eventual goal: train a neural network to generate new C64 SID music as playable `.sid` files.

To get there, we first have to take ~60,000 existing SID files from the [HVSC archive](https://hvsc.de/) and translate them into a single uniform format a model can learn from. That's what this repo is mostly about right now. The model itself is downstream.

## What's a SID file, and why is this hard?

A `.sid` file isn't audio. It isn't notes-and-instruments either. It's **6502 machine code** — a tiny program that, when run on a Commodore 64, writes registers to the SID sound chip 50 times a second.

That means *every SID file is its own music player*. There is no standard music format underneath. Different composers used different "engines": Rob Hubbard's player, GoatTracker, JCH NewPlayer, DMC, Galway, Cybertracker, [dozens more](docs/players/). Each engine has its own custom binary layout for the music data — instruments, note patterns, orderlists — that *only that engine's player code* knows how to interpret. From the outside, every SID is a black box.

This makes machine-learning on SIDs awkward. You can't train on raw bytes — they don't have shared structure. You need to first translate every black box into a common language. That's hard for several reasons.

**You have to reverse-engineer each engine.** Most C64 music engines are 30–40 years old, sometimes from lost source. To extract music from a SID file, you have to disassemble the player code, watch what bytes it reads from where, and infer what those bytes mean. Each engine is days-to-weeks of reverse engineering.

**Engines have *quirks*.** Even after you've extracted the data, the player code does subtle things to it that aren't in the data. Concrete examples we hit in Hubbard's player:

- **Drum noise burst.** Drum instruments emit a 3-frame `$80` (noise waveform) burst at the start of every note. That burst lives only in the player's code, not in the instrument data.
- **Aliased frequency table.** The freq table has 96 entries (8 octaves) but the player aliases slot 104 to "voice 1's control byte". When a percussion note "plays pitch 104," it's actually triggering a hardcoded audio behaviour by indexing past the table.
- **Per-voice direction state.** Bidirectional pulse-width modulation tracks its direction *per voice, not per instrument*. Switching to a new bidirectional instrument inherits the previous one's direction. We had a working pipeline that flipped one voice's PWM 180° out of phase for an entire song before we noticed.
- **Vibrato carry leak.** Vibrato's last `ADC` doesn't `CLC` first, so its carry flag leaks into the *next* unrelated instruction (the linear PWM update), making PW occasionally `+speed+1` instead of `+speed`. This isn't a bug in Hubbard's code — it's an intentional cycle-saving trick. But it's not in the data anywhere.

If your converter doesn't replicate these quirks, the rebuilt song *plays the right notes but sounds wrong*. We found all of those by listening, not by reading code. A typical bug report from the user listening to a candidate rebuild was *"sounds a bit washed out, like the lead voice is afraid of being itself."* That turned out to be a 32-frame stretch where one specific instrument byte was being misread, swapping a lead instrument for a bass instrument's envelope. Frame-by-frame register comparison hadn't caught it; the ear did.

**Different engines have entirely different quirks.** Hubbard's quirks aren't GoatTracker's quirks. The drum noise burst, the aliased freq table, the per-voice PWM direction — those are Hubbard-specific. GoatTracker has its own set we haven't fully surveyed.

**60,000 files.** Even if each engine takes a couple of weeks, ~5–10 engines will cover most of the catalogue. The trick is getting each one *right*, because subtle errors compound: a model trained on subtly wrong data learns subtly wrong music.

**The ear is the final judge.** We compare the rebuilt SID's chip register state to the original frame-by-frame, and that catches a lot. But sometimes the registers match and the audio still sounds off — intra-frame timing differences, envelope retrigger nuances. The user noticing "this doesn't sound right" is sometimes the only signal we have. We try to track those down to a concrete data difference, but it's not always frame-aligned.

## How we approach it

The architectural bet: **engine quirks live as *data*, not as code branches**.

```
  any SID  ──►  decompiler   ──►  USF song   ──►  universal codegen   ──►  rebuilt SID
              (engine-spec.)     (universal)         (universal)
```

What's universal:

- **One format**, USF (Universal Symbolic Format). It describes notes, patterns, instruments, effects in engine-neutral terms. The on-disk USF v2 grammar and reader/writer live in [`src/usf2/`](src/usf2/); the spec is in [`docs/usf_v2_format.md`](docs/usf_v2_format.md).
- **One codegen per engine**. Each pipeline's `Codegen.lean` reads its USF song and emits 6502. There are no `if engine == Hubbard:` branches anywhere; engine-specific behaviour lives in the USF data + per-pipeline codegen, not in shared conditionals.

What's per-engine:

- **A decompiler** that knows how to parse that engine's binary layout (e.g. `rh_decompile.py` for Hubbard).
- **An adapter** that lifts the engine-specific data into USF and *attaches a quirks block*: a declarative `engineQuirks` description of what that engine's player does that's unusual. The codegen iterates that block and emits the appropriate 6502 sequences mechanically.

So when we hit "the drum needs a 3-frame `$80` burst," that goes into the song's `engineQuirks` as a few lines of data, not a branch in the codegen. When we hit "freq slot 104 should alias voice 1's ctrl byte," that's a `dynamicFreqEntries` entry in the quirks block. The codegen reads the quirks block once at compile time and emits the per-frame 6502 that implements them.

Adding a new engine should mean: write a decompiler + write an adapter + spell out that engine's quirks. The codegen and Lean infrastructure shouldn't change. Whether that ambition holds up under contact with a *second* engine is one of the next things to find out.

### Note on Lean (historical, 2026-05)

Earlier the schema and codegen were written in [Lean 4](https://lean-lang.org/),
one self-contained codegen per engine. The Lean trees and Lake build have been
moved to [`deprecated/lean_codegen/`](deprecated/lean_codegen/). The active
codegen is now a shared Python core (`pipelines/hubbard/codegen.py`)
parameterised by per-engine `EngineConfig` objects — adding a new engine no
longer involves writing Lean. The 12 byte-exact Hubbard engines all share this
single codegen. See `deprecated/lean_codegen/README.md` for what the Lean path
looked like and how to revive it if needed.

## Where we are

**Validated end-to-end on two songs, same engine family.**

- Rob Hubbard's *Commando* — all three music subtunes — round-trips into a single multi-subtune SID file that's audibly indistinguishable from the original. Frame-by-frame register comparison is byte-perfect against the original via siddump writelog. Rebuild md5 `1964b77e8b542a5187fdd0a6db2d0186` is locked in.
- Rob Hubbard's *Monty on the Run* — the three music tracks — Grade A (98.8% snapshot match in siddump, **zero divergence over 1500 frames in py65**). The remaining gap is libsidplayfp emulator-internals (CIA timer, cycle-exact bus contention), not codegen bugs.

Adding Monty required cloning the entire pipeline (per [`pipelines/README.md`](pipelines/README.md)'s rationale) and discovering three more Hubbard quirks beyond Commando's: the skydive effect (fx_flags bit 1), pulsedelay/pulsedir initial state extracted from the binary (not the ACME source's `!by $00,$00,$00`), and a notenum/freq-table memory overlap that causes V2's vibrato to read V1's current notenum.

Getting Commando clean took finding five universal-Hubbard quirks; Monty added three more. None of those eight are SID-specific — they should apply to every Hubbard song in the early-engine family. Whether they actually do is what a third Hubbard SID would tell us.

**An older GT2-only pipeline alongside.** Before V3 we built a separate Python pipeline targeted at GoatTracker V2 specifically. It reaches **4,968 Grade A** on GT2 SIDs with engine-specific code — works at scale, useful as a baseline, but doesn't share the V3 architecture and won't generalise. Long term we'd like to retire it; short term it's the only thing that handles GT2 at all.

### Honest limitations

- **The "universal codegen" claim is unproven outside the Hubbard early-engine family.** Until V3 runs on a non-Hubbard engine and Just Works, the architectural bet hasn't paid out. We've discovered eight Hubbard quirks across two songs; we don't know how many universal-GT2 quirks exist, or universal-JCH, or whether the schema is expressive enough to encode them all.
- **Even within Hubbard, the two pipelines are clones, not a shared codegen.** Sharing them is gated on a third Hubbard song being wired through, so the abstraction is exercised by three cases instead of two.
- **Subtunes 4+ of either game aren't round-tripping.** Most are sound effects that take a different code path in Hubbard's player; the others reuse music patterns at conflicting tempos and need a tick-based duration model we haven't built.
- **Lean discipline catches a lot of bugs at compile time** (per-pipeline `Properties.lean`), **but the substantive proofs (round-trip soundness, schema completeness) aren't written.** Maybe 30% of Lean's potential value realised.
- **Audio comparison via `siddump` has frame-boundary jitter** that masks real differences. Ear remains the final test, which doesn't scale.

### What's next, by leverage-per-effort

1. **A third Hubbard SID through the existing pipeline structure.** Cheap; the right point to validate before merging the two clones into one. Likely candidate: Sanxion, Skate Crazy, or BMX Kidz.
2. **Merge Commando + Monty into one parameterised pipeline.** Trade some duplication for a single source of truth — once we know the abstraction handles three engines, not two.
3. **Auto-extract Hubbard quirks from any binary.** Right now we hand-discover quirks per song via py65 tracing. A tool that infers them (symbolic execution, abstract interpretation) drops "weeks per SID" to "hours". Highest-leverage item for HVSC scale.
4. **Property tests on the codegen.** Cheap discipline win — `Properties.lean` exists per pipeline but the theorem set is thin. Catches "I forgot to handle this quirk variant" earlier.
5. **Eventually: formal round-trip soundness proof for tracker music.** Months of work, but would let us convert HVSC at scale with machine-checked confidence rather than per-song listening.

## Pipelines

Each Hubbard SID has a per-engine `pipelines/hubbard/<engine>/` directory;
the shared 6502 codegen lives at `pipelines/hubbard/`. 12 engines are byte-exact
through this path (Commando, Monty, Action Biker, Battle of Britain, Chimera,
Confuzion, Devils Galop, 5 Title Tunes, Human Race, Hunter Patrol, One Man
and his Droid, Thing on a Spring). See [`pipelines/README.md`](pipelines/README.md)
for the full layout + run instructions.

Per pipeline:

| Step | File |
|---|---|
| 1. Parse Hubbard binary | `<engine>/extract/decompile.py` |
| 2. Lift to engine model `(T, I, S)` | `<engine>/extract/engine_model.py` |
| 3. Engine config / parameters | `<engine>/config.py` |
| 4. Emit USF v2 | `<engine>/extract/to_usf_v2.py` |
| 5. Generate 6502 player + PSID wrap | `pipelines/hubbard/codegen.py` (shared) |
| 6. End-to-end build | `pipelines/hubbard/build_from_usf.py` |
| 7. Verify (byte-exact) | `pipelines/hubbard/verify.py` |

## Build

```bash
source src/env.sh                              # PATH for siddump etc.
bash tools/build.sh                            # libsidplayfp + siddump (one-time)

# Build one engine end-to-end (example: Chimera)
python -m pipelines.hubbard.chimera.extract             # writes the .usf + FLAC sidecars
python -c "from pipelines.hubbard.build_from_usf import build_from_usf; \
           build_from_usf('hvsc84/MUSICIANS/H/Hubbard_Rob/Chimera.usf', 'hvsc84/MUSICIANS/H/Hubbard_Rob/Chimera.sidfinity.sid')"

# Verify (byte-exact via md5 of per-frame SID register snapshots)
python -c "from pipelines.hubbard.verify import verify_all; \
           from pipelines.hubbard.chimera.config import CHIMERA; \
           print(verify_all([(CHIMERA, 'hvsc84/MUSICIANS/H/Hubbard_Rob/Chimera.sidfinity.sid')]))"

# Tests
PYTHONPATH=tools/py_test_lib python -m pytest pipelines/        # extract smoke tests
```

Requires: g++ (C++17), Python 3.10+, xa65 assembler. Optional: CUDA / Z3
(only used by V2 pipeline tools).

The earlier per-engine Lean 4 codegen has been moved to
[`deprecated/lean_codegen/`](deprecated/lean_codegen/) — see that
directory's README for context.

## Layout

```
pipelines/                Per-engine V3 pipelines (see pipelines/README.md)
  commando/               Rob Hubbard's Commando
  monty/                  Rob Hubbard's Monty on the Run
src/                      V2 pipeline + shared utilities
  rh_decompile.py         Hubbard SID parser (also cloned into each pipeline)
  gt2_*.py, dmc_*.py      V2 pipeline (GT2, DMC engines)
  player/                 V2 6502 code generator + optimisation tools
  sidxray/                Player reverse-engineering tools
  formal/                 Research utilities (Z3, abstract interp, etc.)
demo/                     Demo artefacts; build_das_model_<engine>.py emits readable asm
docs/                     Specs (USF, GT2 data layout, player engine notes)
tools/                    Build tools (xa65, siddump, libsidplayfp) + in-tree pytest/mypy
deprecated/               Earlier pipeline iterations + dead experiments
```

## Docs

- [USF Specification](docs/usf_spec.md)
- [Development Plan](docs/PLAN.md)
- [GT2 Data Layout](docs/gt2_data_layout.md)
- [Player Engine Notes](docs/players/) — 48 SID engines

## License

The SIDfinity pipeline (Python code, USF format, V2 code generator) is released under the **MIT License**. See [LICENSE](LICENSE).

The C/C++ tools (`siddump`, `sidrender`, `gt2asm`) link against GPL v2 libraries and are distributed under **GPL v2**. See [tools/LICENSE](tools/LICENSE).

## Acknowledgments

The V2 SIDfinity player implements algorithms from Lasse Öörni's GoatTracker V2 playroutine — wave table execution, effect dispatch, pattern reading, hard restart timing. The V2 code generator (`codegen_v2.py`) was written from scratch in Python but the player logic it generates faithfully follows Lasse Öörni's design. A copy of the original GT2 playroutine source is preserved in `deprecated/old_player/sidfinity_gt2.asm`. Lasse Öörni's license: *"free for any purpose, commercial or noncommercial."*

[libsidplayfp](https://github.com/libsidplayfp/libsidplayfp) is used for SID emulation (GPL v2). [xa65](https://github.com/af65/xa65) is used for 6502 assembly (GPL v2).
