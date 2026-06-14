# SidTracker64 — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

SidTracker64, a modern **iOS/iPad** C64-music tracker app by **Daniel Larsson
("Pernod")**, released 2015 (last app update Oct 2019; still in active use). Native
`.s64` format; exports to `.sid`/`.prg`/`.m4a`. 259 HVSC #84 tunes; 0 migrated.
Exported player: load/init $1000, play $1003. Closed-source commercial app.

## ⚠ Target = the exported `.SID` player, not the `.s64` app format

HVSC ships the `.sid` EXPORT — a custom Pernod player + song data in one memory block.
The `.s64` iOS authoring format is irrelevant to us (and undocumented anywhere). The
app's documented FEATURE SET tells us what the player reproduces; the binary analysis
(from 259 HVSC exports) tells us how.

## File index

| Topic | File | Reliability |
|---|---|---|
| Exported-player write model + binary structure + pattern encoding | `cluster_write_model_and_binary.md` | secondary (binary) |
| App feature/effect model + `.s64` + version history | `cluster_app_and_format.md` | secondary |
| HVSC corpus / address clusters / scene | `cluster_corpus_and_scene.md` | primary (DB) |

(`src/` empty — the app is closed-source; no player source or format spec is public.)

## What's solved

**Exported player structure** (byte-stable per app version; relocatable):
- Init = `load_addr` (3-byte `JMP` trampoline); play = `load_addr+$0003`.
- Player code **1930–2258 bytes** across ~14 size-variants = app versions (code grew
  upward with updates). Work area (~$6A bytes) immediately after code; then static
  tables (ADSR, waveform, pulse, filter, freq, pattern streams, orderlists).
- Player is **fixed per app version**, song data appended — version is identifiable by
  code size (`work_area_offset − load_addr`).
- **Relocation** (load address user-selectable) added in **v1.0.5 (Oct 2019)**; before
  that everything was $1000. Same code, just relocated.
- **SMC per-song slots** baked into the player code: `$105F` tempo, `$107D` orderlist
  length, `$101D` filter mode/enable, `$101F`/`$1D` filter routing.

**Per-frame write model** (each `play()`):
1. voice-writer sub ×3 (X=0,7,14) → `$D400..$D406` per voice from a shadow work area;
2. `$D415/$D416` (filter cutoff, 0 or swept from the FX stream);
3. `$D417` filter routing (SMC `$101D/$1F`); 4. `$D418 = $0F | vol`;
5. tempo counter → pattern-step advance; 6. per-voice duration countdown → next step event.
The sidid sig `29 FE 9D 04 D4` = `LDA ctrl,X; AND #$FE; STA $D404,X` (gate-clear in the
hard-restart path); the `18 69` ops = glide step (`ADC #$44` per frame) / page-advance / note-step.

**Pattern encoding**: `$00–$7F` = duration ticks (1–2 bytes); `$80–$FF` = note event +
instrument select (2–3 bytes); 128-byte page boundary advances the stream with an
optional loop marker. Orderlist = 8 parallel lo/hi tables, ≤40 entries.

**Feature model** (app docs — what the player must reproduce):
- **32 instruments/song**: full ADSR + wavetable (waveform sequence) + pulse table (PWM)
  + filter table (cutoff/mode) + vibrato + PWM-sweep envelope. 8 waveforms incl. combined
  + "nowave". Hard sync + ring mod per voice; hard-restart (gate-off timer). **Arpeggio =
  wavetable hi-frequency mode** (not a separate column). "Reset" wavetable effect added v1.0.5.
- **Patterns**: 3 voice tracks **+ 1 FX track** per pattern, ≤128 patterns × 128 rows.
  The **FX track is the unusual feature** — per-step volume (`$D418`), filter
  (`$D415/$D416`), **and speed/tempo (BPM can change mid-pattern)**.
- Per-step note effects: glide, sustain, vibrato, filter-reset, pulse-reset, **tie**
  (suppresses wavetable/sweep restart).

**⚠ Timing — BPM-based, CIA always**: ST64 uses exact integer BPM, NOT the 50.125 Hz PAL
VBI rate; **the player always sets CIA Timer A even when the PSID `speed` header says VBI**.
In the corpus, 47% (122/259) carry the CIA `speed` flag, but CIA is used internally in all.
→ **Plan for the Trap-C `--writelog-per-irq` verdict path across the whole family**, not
just the flagged subset (verify against the `--pc-trace` oracle).

## Corpus shape (259 tunes — all PSID v2, 86% 8580+PAL)

81% canonical $1000/$1003 (220 SIDs); the rest are relocations enabled by v1.0.5
($A000/$E000/$0800/$2000/$4000/$8000 — same player) plus 8 "data-ptr init" tunes where
`init` points into the data area (sub-song select) while play stays $1003. 18 distinct
(init,play) pairs, all one player. Active 2015–2025 (peaks 2016 & 2021; 10 tunes in 2025).
Top authors: Jason Page (33), acrouzet (31), Lula (20), Vaz (18). No HVSC DOCUMENTS or
STIL mention; DeepSID tags it magenta.

## What remains (migration-phase RE)

The player code FLOW is mapped; the DATA encoding is the open work (no public source):
- **Disassemble one canonical $1000 export** to pin: the work-area byte map, the
  note→frequency table, the 32-instrument definition block, and the wavetable / pulse /
  filter table byte encodings.
- **The FX-track stream encoding** (the per-step volume/filter/BPM 4th track) — distinctive
  and central to this engine.
- **The BPM→CIA-timer mapping** + confirm the whole family verifies on the
  `--writelog-per-irq` path (BPM ≠ 50 Hz).
- **Multi-song dispatcher** for the few multi-subtune exports + the data-ptr-init variants.
- **Version→code-size table**: map the ~14 code sizes to app versions so the extractor
  keys on the right layout.

## Top leads (if migration needs more)

1. **Disassemble across 2–3 code-size variants** — the only path to the data layout
   (closed source); a small + large variant brackets the version drift.
2. **Pernod / Daniel Larsson** — CSDb profile + any blog/forum posts; he may have
   described the export player or `.s64` format. (No source found this sweep.)
3. **App in-app help / YouTube walkthroughs** — for the exact FX-track + wavetable command
   semantics not in the App Store blurb.

Full provenance in each file + `provenance_log.md`.
