# HardTrack Composer — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-13).

HardTrack Composer, by **Brush** (editor = Krzysztof Dąbrowski) + **Longhair**
(player = Miłosz Ignatowski), group **Elysium / Parados (Poland)**, 1992. ~1,170
HVSC tunes (9th-largest family), 0 migrated. Polish C64 scene; sold on cassette
via Tim-Soft. CSDb #74928 (V1.0), #36647 (V1.0+ "[6 speed]").

A six-cluster sweep ran 2026-06-13 (a first attempt was killed by a session
limit after downloading the SDK; the re-run finished). Outcome: **strongly
documented** — the released elysium SDK source was recovered AND the player was
disassembled byte-exact and verified against `siddump --writelog`. This corrects
several errors in the old `research.md`. It's structurally a **DMC cousin**
(operand-derived data tables), so the DMC dataflow-extract approach transfers.

## Start here (canonical, disassembly-grounded)

1. **`spec_extraction_plan.md`** — ordered binary→USF checklist + OPEN items.
2. **`spec_write_model.md`** — per-frame `$D400-$D418` write model (Mode-1 target).
3. **`csdb_player_source.md`** — the player routine disassembled + annotated, with
   the **323-entry original Polish symbol table** recovered from the SDK (the
   RAM-map Rosetta Stone: `PRZES`=transpose, `GORA`/`OPUSZ`=gliss up/down,
   `WOLNE`=speed divider, `WAV`/`PULST`/`FILST` macros, …).

## Corrections to `research.md` (now authoritative)

- **Entry: init = BASE+$60, play = BASE+$D8** (the load+$0/$3 are a `JMP` table;
  init takes A=subtune, `AND #$07`).
- **Freq tables: lo = BASE+$588, hi = BASE+$5E8** (not +$880/+$8E0).
- **Instruments = parallel SoA arrays**, variable count N per tune (= array
  stride; e.g. 32 or 13), AD array at a base + each field at `base + k·N` — *not*
  interleaved 8-byte records.
- **Patterns = 2-byte (note, command) fixed-length steps**, looped by the track
  (no in-pattern end sentinel). Note opcodes: `$00-$5F` note, `$60` tie, `$61`
  DEL (gate off), `$62` CUT, `$63 yy` gliss-up, `$64 yy` gliss-down. Command
  byte: `$00` none, `$6F` legato, else **instrument = byte AND $1F** (5-bit, 32).
- **Data-table bases are operand-derived** (read from code operands at fixed code
  addresses) — DMC-style dataflow extraction, not fixed offsets. ~117/1170 are
  relocated off $1000, so walk the init-copied live pointers.

## Per-frame write model

Per voice (**V3→V2→V1**): PW-lo, PW-hi, freq-hi, freq-lo, **control last**
(waveform AND gate-mask). **ADSR ($D405/$D406) written only on note-on** (sparse
in the writelog). Hard restart = `$D404 = $09` (gate+TEST). Once per frame:
`$D416` (cutoff) and `$D418` (`$1F` = vol $0F | LP). **`$D417` is a shared
accumulated register** — each voice's note-on ORs its FILTn routing bit into a
software shadow (`$101F` V1.0 / `$101E` V1.1), note-off ANDs it out; resonance
nibble shifted into bits 7-4. (This OR/AND accumulation is exactly what the sidid
signature fingerprints — `sidid_signature_analysis.md` §1.) Model `$D417` as a
running OR/AND of per-voice bits + last resonance, **not** a per-voice snapshot.

## ⚠ Verification mode: flat Mode-1, NOT per-IRQ

Despite the "multispeed ≤6×" authoring feature, **no CIA multispeed survives in
HVSC renders** — only 5/1170 set the PSID speed bit; HardTrack programs CIA
Timer A itself but the PSID header stays VBI (~1 `play()`/frame). So use the flat
`siddump --writelog` (Mode-1) verdict. (My initial assumption that this needed
the per-IRQ path was wrong — corrected by the disasm + census.)

## Versions (single format)

One song-data format across all versions; the USF model is version-independent.
- **V1.0** (Elysium 1992): Brush + Longhair.
- **V1.1**: Longhair player-only revision (+58 bytes; `$D417` shadow `$101F`→`$101E`,
  code shifted ~$25 later). No standalone disk — lives in the SDK.
- **V1.0+ "[6 speed]"** (~1997): third-party by **Glover/Samar** (Łukasz Baran);
  raises multispeed to 6×. OPEN: whether it alters dispatch only or data too.
- **Tape** version = packaging variant of V1.0. A **V2.0** (beta ~2002, separate
  lineage: decoupled data/player, pattern compression, tempo/volume opcodes,
  `$1006` vector) exists but should NOT appear in HVSC V1.x data.
The **single sidid signature matches all 1170/1170** (version- + relocation-
agnostic by construction; the cheap V1.0/V1.1 discriminator is the `$101F`/`$101E`
shadow operand). No format-aware parser exists in any tool — SIDfinity will be the first.

## File index

| Topic | Canonical | Corroborating |
|---|---|---|
| Extraction plan + OPEN items | `spec_extraction_plan.md` | — |
| Per-frame write model | `spec_write_model.md` | `sidid_signature_analysis.md` (`$D417`) |
| Player source + symbol table | `csdb_player_source.md` | `_artifacts/player_v1.0_disasm.s` (raw) |
| Versions / release notes | `csdb_release_notes_and_versions.md` | `archive_authors_versions.md`, `forum_synthesis.md` |
| Releases / authorship | `csdb_releases.md` | `forum_csdb_releases.md`, `archive_authors_versions.md` |
| elysium SDK contents + readme | `archive_elysium_contents.md` | — |
| sidid signature / population | `sidid_signature_analysis.md` | `deepsid_population_and_versions.md`, `github_player_id_signature.md` |
| Tool landscape (negative) | `github_tooling_survey.md` | `github_jc64dis.md` |
| Polish-scene provenance | `forum_polish_scene.md` | `forum_c64power_v2.md` |

Provenance headers on every file; `provenance_log.md` lists URLs hit/blocked.

## What's solved

- **Released SDK source recovered** (editor/packer/depacker `.SRC` + V1.0/V1.1
  player) + **player disassembled byte-exact** and verified vs `siddump`.
- Binary layout, per-frame write model, `$D417` accumulation, hard-restart, the
  pattern/track/instrument/freq encodings — all grounded.
- Version taxonomy + the single-signature/relocation story + Polish provenance
  (the readme was decrunched via a one-off 6502 emulator, `decrunch_readme.py`).

## What remains (migration, not research)

- **Build `pipelines/hardtrack/<engine>/disassembly.s`** — annotate $10D8–$1587
  with the recovered symbol labels (INIT/OPSK/DRUM/PULST/FILST/…).
- **$101F-vs-$101E census** (relocation-aware) → the real V1.0 vs V1.0+ split.
- **Operand-derived table extraction** (DMC-style dataflow) — reuse `pipelines/dmc/`
  machinery; walk init-copied live pointers for the ~117 relocated tunes.
- **Defer**: the multi-copy/compilation variant (e.g. `Scortia.sid` = 2 player
  copies / 4 subtunes, Adrenalin-like) behind the 1035 clean-$1000 tunes.
- First canary: **`MUSICIANS/W/Wodnik/HT_7_1.sid`** (V1.0, clean $1000, 1 subtune).

## Binary specimens

The elysium SDK (`hardtrack_sdk.d64` + zips) and extracted player/source `.bin`
are git-ignored (kept locally for RE; reproducible from elysium.filety.pl — the
source content is captured in `csdb_player_source.md`). Committed as text:
`_artifacts/player_v1.0_disasm.s` (raw seed disasm) + `_artifacts/decrunch_readme.py`.

## Top leads

1. **`PLAYER_V1.1.bin` build stamp** + diff vs V1.0 emit order (expect identical,
   addresses shifted) — `Shogoon/Tribute_to_Laxity.sid` is a clean V1.1 $1000 tune.
2. **`HARDTRACK V1.0+6` disasm** — is Glover's 6× change replay-only or data-format?
3. **`groups/Elysium/misc/hardtrack_cracks.zip`** (game deployment census) +
   the boxed **Tim-Soft printed Polish manual** (only first-party prose spec;
   auctioned per c64scene.pl t=584).
4. **c64power.com topic 4120 pages 2-4** (V2.0 dev thread; only page 1 fetched).
