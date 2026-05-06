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

- **One format**, USF (Universal Symbolic Format). It describes notes, patterns, instruments, effects in engine-neutral terms. The schema lives in [`src/formal/USFv3.lean`](src/formal/USFv3.lean).
- **One codegen**. [`src/formal/CodegenV3.lean`](src/formal/CodegenV3.lean) reads any USF song and emits 6502. There are no `if engine == Hubbard:` branches anywhere.

What's per-engine:

- **A decompiler** that knows how to parse that engine's binary layout (e.g. `rh_decompile.py` for Hubbard).
- **An adapter** that lifts the engine-specific data into USF and *attaches a quirks block*: a declarative `engineQuirks` description of what that engine's player does that's unusual. The codegen iterates that block and emits the appropriate 6502 sequences mechanically.

So when we hit "the drum needs a 3-frame `$80` burst," that goes into the song's `engineQuirks` as a few lines of data, not a branch in the codegen. When we hit "freq slot 104 should alias voice 1's ctrl byte," that's a `dynamicFreqEntries` entry in the quirks block. The codegen reads the quirks block once at compile time and emits the per-frame 6502 that implements them.

Adding a new engine should mean: write a decompiler + write an adapter + spell out that engine's quirks. The codegen and Lean infrastructure shouldn't change. Whether that ambition holds up under contact with a *second* engine is one of the next things to find out.

### Why Lean

The schema and codegen are written in [Lean 4](https://lean-lang.org/) for two reasons:

1. **Type safety.** The schema is enforced at compile time, so a malformed song doesn't compile. When we add a new variant to the quirks DSL — say a new kind of note-load operation — the codegen *fails to build* until we handle it. This is how data-driven engine quirks stays honest: the compiler won't let us silently forget a quirk type.

2. **Future formal proofs.** We'd like to eventually prove that the codegen's output is sound — that for any USF song the rebuilt SID matches the original under a chosen equivalence (frame-state for tracker music, cycle-precise for digi/demos). We *haven't* done those proofs yet. Right now Lean is buying us discipline more than it's buying us proofs. Maybe 30% of its potential value. The door is open for the rest.

## Where we are

**Validated end-to-end on one engine, one song.** Rob Hubbard's *Commando* — all three music subtunes (game, title, intro) — round-trips into a single multi-subtune `.sid` file that's audibly indistinguishable from the original. Verified by ear and by frame-by-frame register comparison.

Concrete demo: [`demo/hubbard/Commando_v3pipe_all.sid`](demo/hubbard/Commando_v3pipe_all.sid). Play it in [VICE](https://vice-emu.sourceforge.io/) or [`sidplayfp`](https://github.com/libsidplayfp/libsidplayfp) and switch between subtunes 1, 2, and 3.

Getting that one song clean took finding five universal-Hubbard quirks (the four listed above, plus a `no_release`-flag-suppresses-HR-at-note-end behaviour and a portamento freq slide) and encoding them into `CodegenV3.lean`. None of them are Commando-specific; they should apply to every Hubbard song. Whether they actually do is the next thing to test.

**An older GT2-only pipeline alongside.** Before V3 we built a separate Python pipeline targeted at GoatTracker V2 specifically. It reaches **4,968 Grade A** on GT2 SIDs with engine-specific code — works at scale, useful as a baseline, but doesn't share the V3 architecture and won't generalise. Long term we'd like to retire it; short term it's the only thing that handles GT2 at all.

### Honest limitations

- **The "universal codegen" claim is unproven for any engine other than Hubbard.** Until V3 runs on a second engine and Just Works, the bet hasn't paid out. We've discovered five universal-Hubbard quirks; we don't know how many universal-GT2 quirks exist, or universal-JCH, or whether `USFEngineQuirks` is expressive enough to encode them all.
- **Even within Hubbard, only one tune has been validated.** *Monty on the Run* is the next planned check. If it needs codegen changes, the architecture is leakier than we hope.
- **Subtunes 4–19 of Commando aren't round-tripping yet.** Most are sound effects that take a different code path in Hubbard's player; the others reuse music patterns at conflicting tempos and need a tick-based duration model we haven't built.
- **Lean discipline catches a lot of bugs at compile time, but the substantive proofs (round-trip soundness, schema completeness) aren't written.** That's a fair chunk of unrealised value.
- **Audio comparison via `siddump` has frame-boundary jitter** that masks some real differences. Ear remains the final test, which doesn't scale.

### What's next, by leverage-per-effort

1. **Validate V3 on a second Hubbard tune** (Monty on the Run). Cheap; either falsifies the architecture or strengthens it.
2. **Auto-extract `engineQuirks` from a player binary.** Right now we hand-write the quirks block per engine after RE'ing the player. If we had a tool that infers them from the binary (symbolic execution, abstract interpretation), adding an engine drops from "weeks" to "hours". This is the single highest-leverage item for HVSC scale.
3. **Property tests on `CodegenV3`.** Cheap discipline win; catches "I forgot to handle this quirk variant" earlier.
4. **Eventually: formal round-trip soundness proof for tracker music.** Months of work, but would let us convert HVSC at scale with machine-checked confidence rather than per-song listening.

## Pipeline (V3)

For Commando today, the active transformations are:

| File | What it does |
|---|---|
| `src/rh_decompile.py` | Parse Hubbard binary → instruments, patterns, songs, freq table, per-subtune speed |
| `src/das_model_gen.py` | Lift implicit Hubbard player behaviour into explicit data |
| `src/gen_commando_v3.py` | Hubbard data → USF v3, attach `engineQuirks` block, emit Lean source |
| `src/formal/CodegenV3.lean` | Universal 6502 player codegen — reads any USF song |
| `src/formal/SidgenV3Main.lean` | Entry point; packs the result into a PSID |

Static infrastructure: `src/formal/USFv3.lean` (the schema), `src/formal/CommandoV3.lean` (USF data, generated by step 3), `src/formal/{Asm6502,PSIDFile,SID}.lean` (6502 / PSID helpers).

For a different engine, only the first three files change. The Lean side stays put — that's the architectural bet.

## Build

```bash
source src/env.sh
bash tools/build.sh                  # libsidplayfp + siddump (one-time)

cd src/formal && lake build sidgen_v3
./.lake/build/bin/sidgen_v3          # writes src/formal/commando_v3.sid
```

Requires: g++ (C++17), Python 3.10+, Lean 4 / lake, xa65 assembler.
Optional: CUDA / Z3 (only used by V2 pipeline tools).

## Layout

```
src/
  rh_decompile.py        Hubbard SID parser
  das_model_gen.py       Hubbard adapter (extract instruments/patterns/songs)
  gen_commando_v3.py     Hubbard → USF v3 → CommandoV3.lean
  gt2_*.py, dmc_*.py     V2 pipeline (GT2, DMC engines)
  player/                V2 6502 code generator + optimisation tools
  sidxray/               Player reverse-engineering tools
  formal/                Lean V3 pipeline
demo/hubbard/            Reference + generated Commando SIDs
docs/                    Specs (USF, GT2 data layout, player engine notes)
tools/                   Build tools (xa65, siddump, libsidplayfp)
data/                    HVSC collection (not in git)
deprecated/              Earlier pipeline iterations + dead experiments
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
