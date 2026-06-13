# HardTrack Composer — External Tooling Survey (GitHub + parsers + emulators)

> **Provenance.** Web research cluster (GitHub + other tools' parsers + JC64dis +
> libsidplayfp). Conducted 2026-06-13 by the SIDfinity web-research agent. All
> findings below are from live fetches of the named GitHub repos / raw files and
> web search on 2026-06-13. This file records EXTERNAL tooling only — the
> already-extracted Elysium SDK asm (`src/sdk/extracted/`) is a sibling
> agent's territory.
>
> **Headline result: NO existing format-aware HardTrack parser/converter/player
> exists in any surveyed open-source tool.** Every general-purpose SID tool is
> engine-blind (emulation / register-stream based). The only HardTrack-aware
> artifacts found anywhere are the *playroutine-identity signature* in
> sidid / player-id (one signature, no sub-variants).

---

## 1. GitHub code & repository search — NEGATIVE

| Query (GitHub API / web) | Result |
|---|---|
| repos `HardTrack C64 SID` | `total_count: 0` |
| repos `HardTrack Composer` | `total_count: 0` |
| web `"HardTrack" Composer C64 SID parser converter github` | no dedicated repo; only generic SID tools (desidulate, sidtool, SID Factory II) |

No repository on GitHub is named after, or describes itself as handling,
HardTrack Composer. No code file implementing a HardTrack pattern/instrument
parser was located. (GitHub *code* search via web UI requires sign-in and
could not be queried unauthenticated; the repository-search API — which does
not require auth — returned zero, and no engine name surfaced in any code-tool
README inspected below.)

**Net:** there is no prior parser to lean on. SIDfinity's extractor will be
the first format-aware HardTrack reader in the open-source ecosystem.

---

## 2. ChiptuneSAK (c64cryptoboy/ChiptuneSAK) — ENGINE-BLIND, no HardTrack

Source inspected: `chiptunesak/sid.py` (rendered module docs).

- ChiptuneSAK's `SID` importer **does not detect player engines by name.** It
  emulates the 6502/6510 against a "thin C64 layer" and captures `$D4xx`
  register writes into RChirp — generic across any engine.
- It infers multispeed / interrupt mode from the PSID `speed` header bits and
  by watching CIA-timer writes during init — *not* from engine identity.
- **No string `HardTrack` / `GoatTracker` / `Hubbard` / `Future Composer`** in
  the SID module. Confirmed negative.

Implication for SIDfinity: ChiptuneSAK corroborates only the generic
write-stream observation model (same family of approach as `siddump`); it
contributes nothing format-specific.

## 3. sid2midi (mortenstark/sid2midi) — ENGINE-BLIND, no HardTrack

Source inspected: `sid2midi.py` (the whole repo is this one script + a sample
`Robs_Life.sid`).

- Operates on SID voice dumps (freq/waveform/ADSR over time) and does
  note/instrument classification from pitch ranges + timing. **No engine names
  referenced at all.** Confirmed negative.

## 4. desidulate (anarkiwi/desidulate) — ENGINE-BLIND, no HardTrack

Source inspected: `README.md`.

- Works directly on **SID register log files** (VICE `-sounddev dump`); "can
  parse music from any C64 software that VICE can run." No per-engine handling.
  Confirmed negative. (Same observation tier as our `siddump --writelog`.)

## 5. libsidplayfp / libsidtune — ENGINE-BLIND BY DESIGN (negative, expected)

Source inspected: `libsidplayfp/libsidplayfp` file tree (`src/sidtune/`).

- The tune loaders are **format containers only**: `PSID.cpp`, `MUS.cpp`,
  `p00.cpp`, `prg.cpp`, plus `SidTuneBase`. There is **no per-playroutine
  recognition** anywhere in libsidtune — a PSID is loaded as opaque 6502 code +
  init/play vectors and run on the emulated CPU.
- **libsidplayfp has zero HardTrack handling — it is an engine-blind PSID
  loader/executor.** This is the expected and desired property: it is our
  ground-truth oracle precisely *because* it doesn't know or care which engine
  emitted the writes. (This is the same library behind `tools/siddump`.)

---

## Cross-tool conclusion

The entire open-source SID-tooling landscape treats HardTrack tunes the same
way it treats every other engine: run the 6502, observe `$D4xx`. **No tool
decodes HardTrack patterns/instruments.** The only HardTrack-specific knowledge
that exists publicly is:
  1. the **sidid / player-id signature** (engine *identification* only — see
     `github_player_id_signature.md`), and
  2. the **Elysium SDK source** already pulled into `src/sdk/`
     (sibling-agent territory).

This makes the SIDfinity write-log verification model (libsidplayfp `--writelog`
as oracle; our own composer reproducing the `$D400-$D418` stream) the correct
and only viable corroboration path — there is no second independent decoder to
cross-check a USF extraction against. Per-frame write-model corroboration must
come from **our own siddump capture of the HVSC originals + the Elysium asm
source**, not from any third-party parser.

## Sources

- https://github.com/c64cryptoboy/ChiptuneSAK — `chiptunesak/sid.py`
- https://github.com/mortenstark/sid2midi — `sid2midi.py`
- https://github.com/anarkiwi/desidulate — `README.md`
- https://github.com/libsidplayfp/libsidplayfp — `src/sidtune/` tree
- GitHub repository-search API (`/search/repositories?q=...`), 2026-06-13
