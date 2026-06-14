# John Player — research corpus

**doc_state: `OK`** (research-player sweep complete, 2026-06-14).

John Player, a beginner-friendly C64 SID tracker by **Aleksi Eeben ("Heatbeat") of
CNCD/Cyberiad** (Finland), 2001–02 (created because he found other editors unintuitive).
183 HVSC #84 tunes; 0 migrated. Player base $1000, init $1000, play $1003; under 8 raster
lines. **★ The complete WLA-6510 assembler SOURCE was recovered** (V1.0 + V1.4 ship
`source.zip`; V1.6 player source also obtained) — the strongest-sourced family in the
sweep. Exact byte offsets, data layout, and playback logic are all from primary source.

(Other `John_*` sidid strings — Darnell, Hancock, Prince, Klonaris, Kyle Johnson — are
unrelated engines, NOT this family.)

## ★ Source code (the holy grail — `src/`)

| Path | Contents |
|---|---|
| `src/v10/` | **V1.0** (2001-09-03) full source — `player.asm`, `editor.asm`, `packer.asm`, `disk.asm`, `help.asm`, `mem.inc` |
| `src/v14/` | **V1.4** (2001-09-29) full source (+ `presets.bin`) |
| `src/player.asm` (+ `editor/packer/disk.asm`, `mem.inc`, `*.bin`) | **V1.6** player + editor source + assets |
| `src/johnhelp_v16.txt`, `src/johnhelp_v20beta.txt` | V1.6 + V2.0b help/changelog |
| `src/bytemap_version_discriminators.md` | the 4-version binary fingerprints |

(V1.5 / V2.0b source not public — only `.d64` binaries + the V2.0b help text exist.)

## File index

| Topic | File | Reliability |
|---|---|---|
| Tool + source recovery + feature model | `cluster_tool_source_and_author.md` | primary (source) |
| Per-frame write model + binary structure + 4 versions | `cluster_write_model_and_versions.md` | primary (source+binary) |
| HVSC corpus / address clusters / scene | `cluster_corpus_and_scene.md` | primary (DB) |

## What's solved (from source)

**Data layout** (reloc=$1000, V1.x): `FreqTab` +$0358 (84 B = 42 word entries / semitones),
`VibTab` +$0400 (32 B sine, 16 lo+16 hi), `SoundTab` +$0420 (**11 B/sound** descriptor),
shared **64-step** per-step tables `FilTab` +$0500 / `WaveTab` +$0540 / `ArpTab` +$0580,
`Sequencer` +$05C0 (orderlist), `BlockData` +$0600 (patterns).
- **Sound descriptor (11 B)**: AD, SR, trig-pos, end-pos, loop-pos, PWM-init, PWM-rate,
  PWM-top, PWM-bottom, filter-reso/ch-sel ($D417), filter-type/vol ($D418).
- **Per-step (3 shared columns)**: waveform → `$D404`; arpeggio ($00–$7E relative semitone,
  $80–$FF absolute pitch-hi); filter-cutoff addend → `$D416` (voice 1 only).
- **Uncompressed block step (8 B)**: [—][—][v1-note][v1-sound][v2-note][v2-sound][v3-note]
  [v3-sound]; notes 0=empty, $01–$7F=index, **$FE = gate-off mask** (patched into the
  voice's `AND #$FE` gate instr — NOT a loop command).
- **8 block commands**: 1=End, 2=Brk, 3=Flt (filter base), 4=Tmp (tempo), 5=Ini (vibrato
  init/width), 6=Vib (rate), 7=Mod (activate channel), 8=Off (deactivate). One shared
  modulator does vibrato XOR slide.
- **ZP $40–$4C** (13 B): cmdtick, fbase, c1/2/3hold, count, speed, seqpos, step-lo, block-hi,
  vibpos, mod-lo (SMC), mod-hi (SMC).

**Per-frame write model** (3-voice, 50 Hz VBI; per voice on new-note trigger):
`$D404`←0 (gate-off, hard restart) → `$D405` AD → `$D406` SR → `$D404`←$09 (test+gate) →
`$D417` reso/route → `$D418` mode/vol → `$D416` (FilTab[step] + ZP$41 transpose) → `$D404`←
WaveTab[step] AND $FE → `$D402/$D403` PW (SMC from SoundTab+6..8) → `$D400/$D401`
FreqTab[note×2] (+ optional vibrato ADC via SMC). The **triple `$D404` write** (gate-off →
test+gate $09 → waveform+gate) is the intentional hard-restart. **`$D415` is never written**
(stays 0 from init). Heavy SMC: step pointers, gate mask, vibrato on/off (CMP↔ADC), PWM
direction (EOR #$80) live as operand bytes — the rebuild emits clean code per the CORE TENET.

**Four versions** (sidid-discriminated, source-confirmed):

| Version | HVSC | Difference |
|---|---|---|
| V1.0 | 0 | absent from HVSC |
| V1.4 | 13 | hardcoded `LDA #$09` ctrl in the voice block |
| **V1.6** | **93 (dominant)** | voice block loads SoundTab+2/+3/+4 (pos/end/loop) via `LDA abs,Y` |
| V2.0b | 77 | **restructured data**: SoundTab→$1520 (**7-B records**), WaveTab→$1680, ArpTab→$1700, FreqTab→$1460; **64-step→128-step** tables, 32 sounds; play dispatch at $10BA; initial Tmp/Flt/Vol in step 00; **songs incompatible with V1.x** → SEPARATE decoder. |

**⚠ Frequency**: Aleksi published a **corrected freq table in 2024** — the engine assumed
1.0 MHz but PAL is 985248 Hz. The USF note codec must use the corrected table.

## Corpus shape (183 tunes — all PSID v2)

89.6% canonical $1000/$1003; 17 relocations (13 init addresses — Reed $0500, TDS
$5000/$6000/$7000/$B200, Eeben $4000/$B000). 180/183 single-subtune (Greenrunner 11,
Aquarius 4, Boogie Factor 2). Peak 2001–2006 (75%), active again 2020–25 (Aleksi 5 in 2025).
Aleksi = 53/183 (29%); 30+ composers, broad geography. A few `play=$0000` anomalies =
likely CIA mode (verify). No HVSC DOCUMENTS/STIL entries.

## What remains (migration — mostly mechanical, source in hand)

- **V1.6 extractor straight from `src/player.asm`** — the table offsets are exact; this is
  the dominant 93 SIDs. Then V1.4 (13, near-identical).
- **V2.0b SEPARATE decoder** (77 SIDs) — the help text documents it but no source; confirm
  the 128-step / 7-B-sound / $1520-$1700 layout against a binary (one disassembly).
- **Use the 2024-corrected 985248 Hz freq table** for the note codec (not the buggy 1 MHz one).
- **Audit the `play=$0000` tunes** for CIA mode → `--writelog-per-irq`; otherwise flat VBI.
- **Per-SID version fingerprinting** (V1.4 vs V1.6 vs V2.0b) — `src/bytemap_version_discriminators.md`
  has the byte patterns; the extractor keys on them.

## Top leads

1. ~~Player source~~ — **OBTAINED** (V1.0/V1.4/V1.6 in `src/`).
2. **V2.0b source** — not in the public release (only `.d64` + help); ask Aleksi Eeben (active)
   or disassemble a V2.0b SID to confirm the 128-step layout.
3. The 2024 corrected freq-table post (Aleksi/CSDb) — grab the exact 42 word values.

Full provenance in each file + `provenance_log.md`.
