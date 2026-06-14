# CyberTracker — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

CyberTracker, a native C64 SID tracker by **Bjarke Nørgaard Laustsen ("CyberBrain")
of No Name** (Denmark; debuted at Mekka & Symposium, 13 Apr 2001). 255 HVSC #84 tunes
across two SIDId strings; 0 migrated. **Well-documented** — the full feature manual is
public at noname.c64.org/tracker/ (saved verbatim under `src/`).

(`Cyberbrain_Digi` is a SEPARATE 1994-96 digi player by the same author — not this
family. `Cyberlogic_SoundStudio` is a different engine entirely.)

## ⚠ One musical format, TWO player implementations (+ build classes)

`CyberTracker` (125) and `CyberTracker_exe` (130) are the **same musical format** but
**different player implementations** produced by different export tools — they differ in
packaging AND per-frame write ORDER, so the migration needs two extract/compose paths
(or one USF + a `write_order` flag):

| SIDId string | tool | base / layout | HVSC | freq write order |
|---|---|---|---|---|
| `CyberTracker` (_ct) | the tracker itself (PSID save) | engine FOLLOWS song data; init floats $1DC0–$2BBE (play=init+$51) | 87 native | **interleaved per voice**: V1(lo,hi),V2(lo,hi),V3(lo,hi) |
| `CyberTracker` (_ct) | **Packer** BETA#1 (Mar 2002, PC) | fixed $1000/play $1003 | 35 packed | (same _ct engine) |
| `CyberTracker_exe` | **Executable Maker** (Dec 2001) | fixed $0800; engine $4800–$5600; init $53A2/play $53E2 (gap $40) | 128 (98.5%) | **all-lo-then-all-hi**: V1lo,V2lo,V3lo,V1hi,V2hi,V3hi |

CTRL/ADSR/SR/filter/vol order is **identical** between the two; only freq & PW lo/hi
ordering differs. The `_ct` engine is **position-dependent** (absolute addresses patched
at save → no single canonical byte sequence; the Executable-Maker `_exe` form is the
fixed-layout one and covers ~51% of all tunes from a single disassembly).

## File index

| Topic | File | Reliability |
|---|---|---|
| **Byte-level `.ct`/`.ci` file format (author's own spec)** | `cluster_byte_format.md` | primary (author spec) |
| ↳ verbatim spec text | `src/ctfileformat-1_01.txt` | primary |
| Per-frame write model + binary structure + the 2-variant relationship | `cluster_write_model_and_variants.md` | secondary (binary) |
| Full feature/data model from the manual + effect catalogue | `cluster_manual_and_format.md` | primary (manual) |
| ↳ verbatim manual text | `src/manual_online_fetched.md` | primary |
| HVSC corpus / address build-classes / scene | `cluster_corpus_and_scene.md` | primary (DB) |

> **✅ The #1 gap is CLOSED.** CyberBrain's own `.ct`/`.ci` byte-format spec
> (`ct fileformat V1.01`, 13/11/2001) was recovered and is in `cluster_byte_format.md`
> (+ `src/ctfileformat-1_01.txt`): header magic, every length-prefixed table offset, the
> 3-byte pattern-cell encoding, the 768-point split-table envelopes, track/multi-effect
> layouts. **"No packing anywhere in the files"** — on-disk tables are the raw runtime
> tables. The DATA model now needs no RE; only the file↔in-memory ($10xx/$53A2) offset
> binding remains (one disassembly).

## What's solved

**Per-frame write model** (both variants): ~**25 SID registers per `play()`** + optional
hard-restart writes. Sequence: (per pending HR voice) SR→AD=0→ctrl gate-clear→ctrl gate-set;
then freq lo+hi ×3, ctrl ×3, AD ×3, SR ×3, PW lo+hi ×3, filter ctrl, vol, filter lo/hi.
The freq/PW lo-hi ORDER is the only inter-variant difference (above). The "clicky notes"
scene reports = audible hard-restart writes in the log.

**State-page map (_ct, $10xx)** recovered: voice Y-base `$1046 = {00,07,0E}`; freq cache
`$1090-95`, PW `$1096-9B`, ctrl `$10B1-B3`, ADSR `$10B4-B9`, filter `$10A8/$10A9/$10BA`,
vol `$10BB`. `_ct` data header magic `60 60 60 63 74 ...` at `$1006` (`'ct'`=$63$74).
`_exe` has a 13-entry envelope dispatch table at `$47F6` + ZP state.

**Complete musical/data model** (from the manual — `cluster_manual_and_format.md`):
- **Patterns**: 3-channel FastTracker-style, per line `NOTE(3) INST(2hex) EFFECT(3hex)`;
  notes C–B oct 0–7; `---` empty, `.` gate/release, `,` stop. ≤128 lines/pattern, 256
  patterns, 796 shared pattern lines. Multiple songs share patterns+instruments (only the
  orderlist/track differs); 512 track lines, 255/song; restart marker `R`.
- **31 instruments** ($01–$1F), each = **8 graphical envelopes** + vibrato + arpeggio +
  name; 768 shared envelope points. The 8 envelopes → registers:
  1 Volume (0–$F, ADSR-structured, sustain gate, interpolated) · 2 Waveform (TRI/SAW/PUL/NOI,
  step) · 3 Pulse Width ($000–$FFF, $800=50%, interp) · 4 Filter Pass (LP/BP/HP/v3off bits,
  step) · 5 Cutoff (0–$7FF 11-bit, interp) · 6 Resonance (0–$F, interp) · 7 Pitch
  ($0000–$FFFF, $8000=normal, interp) · 8 Pitch Control ($0 relative / $1 absolute, step).
- **Effects** (20 codes): `0xy` arpeggio, `1/2xx` porta up/down, `3xx` tone porta, `4xx`
  vibrato, `5/6xx` cutoff slide, `7xx` set cutoff-add, `A/Bxx` PW slide, `Cxx` set sustain,
  `Dxx` **multi-effect jump** (chain multiple effects/line via a 255-line multi-effect table
  — CyberTracker's signature feature), `E0x–E9x/ECx/EDx/EEx` extended, `Fxx` set speed.
- **Filter**: one filter for all 3 channels, lowest channel number wins; per-channel routing
  toggled with `E0x`. **Tempo**: `Fxx` ticks/line (1 tick=1/50 s PAL); speeds <3 cause HR issues.

**Corpus** (255 tunes, all PSID v2, **all VBL speed=0 — zero CIA**, ≤2 subtunes): three
build classes (native exe-maker gap=$51 / Packer $1000 / `_exe` $53A2). Versions V1.00
(CSDb #2601) → V1.01 (CSDb #25, fwd-compatible) → Executable Maker → Packer BETA#1. Authors:
Fredrik dominates `_exe` (75/130); V0yager, Odo, theK. Used 2001 and again 2019–2020. No
HVSC DOCUMENTS/STIL mention.

## What remains (migration-phase RE)

The musical model, write model, AND the byte-level **file** format are now mapped (the
file spec is in `cluster_byte_format.md`). Remaining migration work:
- **Bind the file tables to the in-memory layout** by disassembling one `_exe` ($53A2)
  tune (covers 51% from one disasm) + one native `_ct` tune — i.e. map the file's
  VIBDPT/ADSR/ENVX-Y/PATTERNS/PTNLEN/TRKMEM tables to their $10xx / $53A2 runtime addresses
  (the file spec says they're the raw unpacked tables, so this is a 1:1 relocation map).
- **Encode the two write-orders** (`_ct` interleaved vs `_exe` all-lo-then-hi) as a USF/config
  flag — the Mode-1 verdict depends on it.
- **Filter "lowest channel wins"** conflict resolution — exact per-frame write behaviour.
- No CIA → the flat Mode-1 path applies family-wide.

## Top leads

1. ~~`ct_v101_fileformat_fixed.zip` byte-format spec~~ — **OBTAINED** (user-supplied Wayback
   capture; see `cluster_byte_format.md` + `src/ctfileformat-1_01.txt`).
2. The same `noname.c64.org/download.php/ctmisc/` Wayback directory may hold other CyberBrain
   notes (player internals, Executable-Maker layout) — worth a directory listing from a
   networked host.
3. CSDb #2601/#25 editor disks + the Executable Maker / Packer tools — useful for the
   file↔memory offset binding if the disassembly is ambiguous.

Full provenance in each file + `provenance_log.md`.
