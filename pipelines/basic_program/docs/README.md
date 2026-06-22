# Basic_Program — research dossier + migration strategy

**Category:** 486 HVSC SIDs labelled `Basic_Program`. Each is an RSID v2 file
(`load=init=play=0`, C64-BASIC flag set) whose payload is a **tokenized Commodore
BASIC V2 program at `$0801`** that POKEs the SID chip. There is **no machine-code
player** — the "engine" is the C64 BASIC + KERNAL ROM interpreter, and each tune is
its own hand-written micro-program. (Adjacent labels `Basic/Jim_Butterfield` (47)
and `Basically_Music` (12, a machine-code player — pun name) are NOT this category.)

Research sweep date: **2026-06-22**. Six clustered leaf agents + local recon.
This README is the synthesis; read the `cN_*.md` files for depth.

## Document index

| File | Cluster | Contents |
|------|---------|----------|
| `00_local_recon_findings.md` | local | Primary ground truth: header decode, sidid signature meaning, detokenized examples, the two blockers. READ FIRST. |
| `c1_scene_origin_corpus_map.md` / `_authors.md` / `_sources_online.md` | C1 | Where the 486 came from: 100% BASIC Project (62) + 1980s magazine type-ins; per-author profiles; archive.org source scans. |
| `c2_basic_tokenization_spec.md` | C2 | Canonical BASIC V2 detokenization spec: token table, NORMAL/IN_QUOTE/IN_REM state machine, link-pointer + `$030C` song-select rules, corpus edge cases. |
| `c3_interpreter_timing_and_nondeterminism.md` | C3 | Interpreter execution + timing model; the per-class determinism verdict; verification-mode recommendation. |
| `c4_basic_floatingpoint_core.md` / `_quickref.md` / `src/c4_reimplementations_assessment.md` | C4 | 5-byte float format, POKE=FLOOR conversion, RND algorithm, the deterministic MLTPLY bug; cbmbasic/VICE reimpl audit. |
| `c5_rsid_playback_roms_and_tooling.md` | C5 | RSID-BASIC playback in libsidplayfp; the `setRoms()` siddump patch; ROM sourcing/licensing; VICE oracle. |
| `c6_extraction_representation_strategy.md` | C6 | The standard POKE-recipe idiom catalogue; Path A vs Path B; USF representation; verdict-mode design. |

## Corpus characterization (EXACT — full-corpus detokenize, parse_fail = 0/486)

Feature usage across all 486 (a tune may appear in several rows):

| Feature | Count | Note |
|---|---|---|
| `DATA` (READ tables) | 389 (80%) | The tractable backbone. |
| `PEEK` | 171 | Mostly ROM/RAM melody-as-data; 5 read live CIA timers. |
| `GET` | 81 | Interactive — but no-key path is deterministic. Subset are "play-along" (no music without input). |
| `SYS` (→ machine code) | 79 | Hybrid BASIC+ML. Path B captures these transparently; Path A cannot. |
| `TI` (jiffy clock) | 73 | Deterministic IN-EMULATOR (cold-reset TI=0, fixed CIA rate). |
| `RND` (any) | 94 | of which: `RND(0)` = 8, `RND(neg/TI)` = 24 (most are fixed-seed `RND(-const)` = deterministic), `RND(+)` only = 62. |
| `SIN`/`COS` | 24 | Polynomial — fully deterministic. |
| `WAIT` | 20 | Usually `WAIT raster`. |

Origin streams (C1): 62 = The 100% BASIC Project (Alan Bond, 2013-15); ~150 from
1980s magazine type-ins (Family Computing/MicroTones, COMPUTE!, Commodore's own
PRG-guide examples, German mags); the rest a long publisher tail. Many have
**scanned human-readable originals on archive.org** → free detokenizer validation.

## The two blockers — and their resolutions

### Blocker 1 — ground-truth capture (TOOLING) → SOLVED pending a small patch
`tools/siddump` skips RSID and, even with `--force-rsid`, runs with stub ROMs so
BASIC never executes (one `$D418` write then silence). Fix: load real C64 ROMs and
call `engine.setRoms(kernal, basic, character)` before `engine.config()`.
- **The ROMs are already on this machine** at `~/.local/share/sidplayfp/{kernal,basic,chargen}`,
  MD5-verified canonical (basic `57af4a…`, kernal `3906549…`, chargen `12a4202…`).
- libsidplayfp already does the rest automatically: psiddrv patches the BASIC
  warm-start at `$BF53`/`$BF55`, writes the subtune to `$030C` (`setBasicSubtune`),
  clears `$0000-$03FF`, sets the PAL/NTSC flag, and lets the C64 run. (C5.)
- Licensing: these are original Commodore ROMs — **use locally, never commit/redistribute**
  (same posture as VICE). MEGA65 OpenROMs are NOT bit-exact enough for FP math —
  do not use for ground truth. (C5.)
- Estimated effort: ~25 lines / 1-2 h. Add `--roms-dir` (default the path above).

### Blocker 2 — USF representation + verdict (DESIGN) → recommended: Path B
- **Verdict mode:** a **flat, un-bucketed ordered `(reg,val)` write stream** (cycles
  dropped, no `play()` framing) — the existing `compare_instruction_stream`
  machinery with a new `duration_tol` (BASIC tempo is busy-wait-quantized, so allow
  a small length tolerance). (C3 + C6.)
- **Representation (Path B — trace-level lift):** capture the deterministic
  `--writelog` stream, then lift it into USF note events (engine-agnostic). This is
  the CORE-TENET fit ("the write-log stream is the target; engine code is a
  historical artifact"), and it transparently handles the `SYS`-to-ML (79),
  algorithmic (FP/PEEK), and `RND` tunes that a source-level decompile (Path A)
  cannot. **No new USF schema fields** — note/duration/waveform/ADSR/PW already cover
  it; the FOR/NEXT-delay mechanism is the artifact we discard. (C6.)
- Prior art to reuse: `deprecated/gt2_pipeline/` has a **universal register-trace →
  USF** path (`regtrace_to_usf` per C6) that is ~80% of the lift — but it consumes
  VBI-frame snapshots (Trap A). **Upgrade it to consume the `--writelog` ordered
  stream.** (C6.)

## Determinism — the corrected picture (important)

C4 framed `RND(0)`/`TI`/unmapped-`PEEK` as "nondeterministic"; that's the
**real-hardware / run-to-run** framing. For **Path B** it largely dissolves:
libsidplayfp is a **deterministic emulator from cold reset**, so its CIA timers,
TOD, and TI are deterministic functions of elapsed cycles — `RND(0)` returns the
same value every run. Path B **freezes one canonical realization** and replays it as
note events (we never re-execute RND), so **all 486 are capturable**. The genuine
exclusion question is curatorial — "is there music with no keypress?" for a subset of
the 81 `GET` play-along tunes (e.g. piano programs where `GET` selects the note) —
resolvable empirically AFTER the capture patch lands, not a reproducibility blocker.

This is the one place where Path A (re-execute / reimplement) and Path B (freeze a
trace) genuinely diverge: Path A inherits all of C4's nondeterminism; Path B does not.

## Recommended migration plan (proposed — not yet executed)

1. **Patch `tools/siddump`** to load ROMs via `setRoms()` (`--roms-dir`, default
   `~/.local/share/sidplayfp`). Verify on `Two_Lines_of_Code_1` + `Ahoy_Magazine`:
   expect a rich `$D400` stream instead of one `$D418`. *(unblocks everything)*
2. **Capture survey:** run the patched capture over all 486 at songlength; bucket by
   stream richness (real music vs empty/near-silent) to find the true
   no-music-without-input set. Confirm determinism by capturing each twice.
3. **Detokenizer hardening:** implement C2's full NORMAL/IN_QUOTE/IN_REM state
   machine + scan-by-`$00` (ignore link pointers); validate against the archive.org
   scans (C1) for a sample.
4. **Path-B lift:** revive + upgrade `deprecated/gt2_pipeline` regtrace→USF to the
   `--writelog` stream; add `duration_tol` to the comparator; stand up
   `pipelines/basic_program/{config.py,extract/}` + a verify entry.
5. **Iterate FULL** on a stratified subset (DATA-table / SYS-hybrid / algorithmic /
   GET), then a wide batch; exclusions → `tools/excluded_sids.json` for the curatorial
   no-music set only.

## Open decisions for the user
- **Path A vs Path B vs hybrid.** Recommendation: **Path B** (trace-lift) for the
  whole family — it's the CORE-TENET fit and the only path that covers SYS-hybrid +
  algorithmic + RND. (A hybrid that *also* decompiles the 277 pure DATA-table tunes
  to richer USF note structure is possible later, but is optional polish.)
- **Curatorial exclusions.** Decide the bar for "play-along, no music without input"
  tunes once the capture survey (step 2) quantifies how many are truly empty.

## Gaps / still-open (for a future wave)
- Empirical confirmation that the ROM-patched capture is bit-stable run-to-run
  (expected yes; must verify — step 2).
- The exact no-music-without-input subset of the 81 GET tunes (needs capture).
- `$B79E` FP-multiply full disassembly not fully fetched (C4 lead #7) — moot if we
  run the real ROM (we do).
- A few Simon's-BASIC-extension programs (C2) — confirm they still POKE the SID the
  same way (Path B is agnostic regardless).
