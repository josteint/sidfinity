# TFX — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

TFX, a C64 SID music editor by **Lada "Ray" Lostak** of **Unreal** (Czech Republic;
UI by PseudoGrafx; later player fixes + docs by Jaymz Julian / A Life in Hell),
1995–2005. 269 HVSC #84 tunes; 0 migrated. Player base $1000, play $1003.

**This is the best-documented unmigrated commercial-style family yet** — the
**actual player source** (`Player.ass`, signed Ray/Unreal 1995-2002), the **full
v2.99 manual**, the key-guide, the changelog, and a **PC-side unpacker
(`hyperPacker.c`) that exposes the on-disk binary layout** were all recovered from
the official `Tfx_2_99.zip` (unreal64.net). All saved under `src/`.

## ⚠ Two corrections to the old `research.md` stub

- **Czech, not Polish.** Unreal is a Czech group; Ray = Lada Lostak (ray@unreal64.net).
  ("Area Team" is unconfirmed — CSDb lists only Unreal.)
- **TFX descends directly from DMC** (Ray said so on CSDb; a 1996 DMC→TFX converter
  exists). **DMC is our focus engine and already `OK`** — the hard-restart +
  programmable-table machinery in `pipelines/dmc/` is the natural starting point.

## File index

| Topic | File | Reliability |
|---|---|---|
| Per-frame write model + binary structure + pattern encoding | `cluster_write_model_and_binary.md` | primary (source+binary) |
| Editor + full feature model + source hunt | `cluster_editor_and_scene_source.md` | primary (manual+source) |
| HVSC corpus / address clusters / version cohorts | `cluster_corpus_and_versions.md` | primary (DB) |
| **Player source (NP — the oracle)** | `src/Player-v2.99.ass` (73 KB, signed Ray/Unreal) | primary |
| On-disk binary layout (PC unpacker) | `src/hyperPacker-v2.99.c` | primary |
| Manual / keys / changelog | `src/tfx-manual-v2.99.txt`, `src/tfx-keys-v2.99.txt`, `src/tfx-news-v2.99.txt` | primary |
| Disasm fragments | `src/atariada_disasm_fragments.s` | secondary |

## What's solved

**Player source in hand** (`src/Player-v2.99.ass`) — the migration's semantics oracle;
the points below are grounded in it + the manual + binary inspection.

**Binary layout ($1000 base, v2.x standard)**:
- First 9 bytes = 3 JMP vectors (init=$10FA, play=$1003, 3rd/SFX=$1914).
- `$1009–$1037`: PETSCII apostrophe-delimited version string + song title.
- Freq table lo `$103A` (96 bytes), hi `$109A` (96 bytes); 8-byte subtune descriptors
  at ~`$1BCF`; pattern data follows. Total song image $1000–$2FFF (8 KB).

**Per-frame write model** (per voice): **SR → AD → ctrl → PWhi → PWlo → freqhi → freqlo**
(`$D406→$D405→$D404→$D403→$D402→$D401→$D400`); global regs after all voices: `$D418`,
`$D416`, `$D417`. The sidid sig anchors on the X-indexed hard-restart sub (AD=0/SR=0/ctrl).

**Pattern encoding** (byte ranges):
`$00–$5F` note index · `$60–$7F` secondary speed · `$80–$BF` primary duration ·
`$C0–$CF` ADSR nibble · `$D0–$ED` instrument/event · `$EE` vibrato · `$EF` glide ·
`$F1–$FF` global effects (filter, gate-off, pulse, loop, voice-off, pattern-end).

**Feature model** (from the manual — complete):
- Sector-based 3-voice sequencer; ≤80 sectors, ≤5 subsongs.
- **Instruments**: 8-byte records (ADSR + wave/pulse/filter table ptrs + 8 flags +
  vibrato delay/depth/speed); ≤32 instruments.
- **Wave table**: 2-byte entries; modes NRM/SHI/SHL/RHI/RHL/HRD; cmds AD,SR,DEL,JMP,JWG,USE,SPD.
- **Pulse table**: 8-bit (hi-8 of 12-bit); cmds SET, SAC (16-bit accurate, v2.99), ADD,
  SUB, DEL, JMP, JWG, SPL (split dual-program, v2.97), USE.
- **Filter table**: same structure; SET = type/resonance/cutoff; all 11 filter bits (v2.98+).
- 6 table variables settable per sector; **multispeed 1×–12× (all ch) / 72× (per ch)** +
  `$1003/$1006` split mode.
- **Sector effects (~20+)**: GLIDE, SLIDE, SWITCH, DUR, VOL, FVOL, A GATE, FADE±, CTRL
  (waveform override), RLEN (per-channel hard-restart length), VSPD/VDEP, NOPL, NOFL.
- SFX game entry at init+9 (v2.99).

**Multispeed (CIA)**: two confirmed mechanisms — CIA1 Timer-A (e.g. Bloedzuster 100 Hz,
Julian_Jaymz 451 Hz) AND a play-wrapper frame-skip DEC counter (Anubis v1.3). → the
Trap-C `--writelog-per-irq` path applies to the CIA subset.

## Corpus shape (269 tunes — all PSID v2)

Authors are **Czech/Slovak/AU scene**, top 4 ≈ 92% (Sad/David Cwik 108 still active 2025,
Factor6, PCH, JJ). Span 1993–2025. Address clusters = version cohorts:

| Group | init | play | Count | Era / who |
|---|---|---|---|---|
| A canonical V2.x | $1000 | $1003 | 154 | all authors, 1994–2022 |
| B V1.x (PCH-era) | $1106 | **$1100** | 11 | PCH/PseudoGrafx 1993–96 — **different freq-table map** |
| C "Sad" priming | $FF0/$FF4/$FF6 | $1003 | 43 | David Cwik only, 1999–2025 |
| D high-init (data ptr) | $1C52–$28E0 | $1003 | 23 | various 2002–18 |
| E1 relocated V2.x | play−3 | non-std | 9 | relocations |
| E2 V1.x native export | play−18/−19 | $1D00–$2200 | 25 | PCH/PseudoGrafx/Sad 1995–2007 |
| F anomalous | various | various | 5 | audit |

**Versions are a long series** (V1.0, 1.2, 1.3, 2.4–2.7, 2.8, 2.92–2.99), NOT just
"1.0/1.2/2.4". A **single sidid sig covers them all**. The major split is **V1.x
(play=$1100, freq table at $1000, different layout) vs V2.x (play=$1003, the manual's
layout)** — the extractor needs both maps.

## What remains (migration-phase RE)

Most of the format is *documented* (rare for this size) — the work is binding the source
to the binaries:

- **Confirm the v2.x binary layout against `Player.ass` + `hyperPacker.c`** by
  disassembling one canonical $1000 tune; pin the table/pointer offsets the extractor reads.
- **Map the V1.x layout** (Group B/E2, play=$1100) — `Player.ass` is v2.99; v1.x freq
  table sits at $1000 and pre-dates several features. Needs its own offset map (no v1.x
  manual exists).
- **v2.94 anomaly**: shortened 32-entry lo freq-table + a 36-byte dispatch block before
  the version string — detect and handle.
- **CIA/multispeed subset** → `--writelog-per-irq` verdict (two mechanisms: CIA Timer-A +
  frame-skip DEC).
- **Leverage `pipelines/dmc/`** — TFX is a DMC descendant; the hard-restart + table model
  should partly transfer.

## Top leads (if migration needs more)

1. **`src/Player-v2.99.ass` + `src/hyperPacker-v2.99.c`** are the primary oracles — read
   them directly during extraction (already local).
2. **A v1.x editor/source** — the only real gap (Group B/E2 layout). CSDb #110111 (v1.0)
   / #38900 (v1.2) editor disks (CSDb 503 this session) — retry for a v1.x binary to map.
3. unreal64.net/tfx main page (not recovered) — possible additional version docs.

Full provenance in each file + `provenance_log.md`.
