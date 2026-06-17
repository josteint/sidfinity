---
source_url: index (see individual files + provenance_log.md)
fetched_via: research-player sweep (6 leaf agents, clean re-run)
fetch_date: 2026-06-17
author: research synthesis (Jostein Trondal session)
content_date: 2026-06-17
reliability: primary (Panther disassembly + two open-source parsers) + secondary (interviews/wikis)
---

# David Whittaker — research docs index

Research-player sweep **completed 2026-06-17** (clean re-run after an earlier
interrupted attempt; this run used non-recursive leaf agents). Family state
bumped `LITTLE → OK`. There is **no original GPL source** — Whittaker hand-coded
every game's data as macro-expanded 6502 with absolute pointers and never
released a driver — but we have enough to disassemble confidently: one full
annotated C64 disassembly, **two battle-tested open-source cross-platform
parsers**, a complete format synthesis, a driver-variant census, and the sidid
signatures.

## Engine identity

- **David Whittaker** — one of the most prolific UK C64 game composers
  (Compunet handle "TS1"; CSDb scener #2598). Hand-coded his music as
  **macro-expanded 6502 assembly** (Tony Bybell: *"not true assembled tunes per
  se, but music data is macro expanded and uses absolute pointers"*), NOT a
  music editor.
- **HVSC #84: 110 SIDs** tagged `David_Whittaker` (+ the same driver appears
  under other composers: Wally Beben, Gary Foreman, Tony Williams, Jason Brooke
  / Tiger_Road). Note 7 NULL-engine SIDs in `hvsc84.csv` are sidid
  false-negatives that actually match the main variant (DB refresh would fix).
- **Driver lineage (drives the variant axes):**
  - **Pre-Brooke / early** (~1984–mid 1986, e.g. Lazy Jones): minimalist, 424 Hz
    tuning.
  - **June 1986 Jason Brooke rewrite** (Panther onward): shorter, faster,
    flexible chords/envelopes/pitch-bends. Brooke wrote it on an Einstein with
    Mikes Assembler.
  - **Stable 1987+**; filter used pre-autumn-1987, then dropped except for
    engine/SFX sounds.
  - **Ported** to ZX Spectrum / Amstrad CPC / Amiga / NES / Atari ST with
    compatible data structures (confirmed by Bansai's ZX→C64 conversion).

## Driver variants (the key deliverable for the extractor)

**sidid carries 5 alternative byte-patterns under a SINGLE `David_Whittaker`
entry** — it does NOT distinguish driver versions. A binary fingerprint census
of the 103 C64 SIDs (in `sidid_signature.md`) splits them into:

| Variant | Idiom | Count | Notes |
|---|---|---|---|
| **P1 main** | `DEC / STX $D404` gate-toggle | 86 | dominant; Panther is P1 |
| **P2 alt-reg** | SR-write-first, then `LDX`/gate | 10 | shares P1's data format, different register write order |
| **P3 early** | init-path loader | 4 | earliest engine (Demo_2/3, Max_HR_preview) |
| **P5 tiny** | bare freq-update loop | 3 | <500 bytes (Humphrey/Mayhem/Pandoras_Box) |
| **unknown** | — | 1 | Exorcist.sid — V2/V3-only, different architecture; may not be Whittaker's driver |

`iAN CooG`'s **Prg2Sid 1.20** independently reports "Whittaker (2 variants)" (two
binary layouts needing different PSID header patching) — consistent with the
P1/P2 split. **Practical extractor target: ~2 main C64 format families (P1+P2,
likely one data format) + early/tiny edge cases.** Only P1 (Panther) is
disassembled publicly — see Gaps.

## Format in brief (C64 — confirmed from Panther.asm + parsers)

- **Song/sub-song table:** 7 bytes/subtune — `<speed, v1lo, v1hi, v2lo, v2hi,
  v3lo, v3hi>`. **Absolute (non-relocatable) pointers** throughout. (NES variant
  = 9 bytes/subtune.)
- **Pattern stream:** notes `$00–$7F`; commands `$80–$93` (≈18–20 named:
  waveform select, ADSR, arpeggio select, PWM, ring-mod, sync, stop). A higher
  dispatch (`pspecial`) maps byte RANGES to arp / ADSR / tempo / duration —
  **two docs give slightly different range boundaries** (`forum_wiki_synthesis.md`
  vs `disasm_panther_command_detail.md`): reconcile against Panther.asm at
  migration. End-of-pattern byte = `$88` (C64) / `$87` (ZX) / `$FF` (NES).
- **Tables:** 84–91-entry note-frequency table (8 octaves, PAL/424 Hz); 13
  arpeggio patterns. **Arpeggio sequences reset on any byte ≥ `$54`** (range
  check, not an exact `$88` match — a `disasm_panther_command_detail.md` finding).
- **Per-voice state block:** 36–40 bytes, offsets `$00–$23` labelled
  (`disasm_panther_command_detail.md`, `forum_wiki_synthesis.md`).
- **Gate model (critical for USF):** gate-off is an **atomic note-retrigger
  (reset + restart), NOT release-then-note-on** — a one-frame hard-restart via
  the `VD_B19` flag + `INX/STX $D404` trick. Confirmed independently by DeepSID's
  named jsSID "Whittaker workaround". Model as hard-restart, not ADSR release.
- **All effects are software-computed in the player** (no autonomous hardware
  state) — simplifies USF effect modelling.

## Cross-platform parsers to mine at migration (battle-tested)

- **NostalgicPlayer** (`neumatho/NostalgicPlayer`, C#) — **most complete**;
  distinguishes "old (QBall)" vs "new" Amiga player, 3 period tables, full
  channel/sample/position-list struct extraction via 68000 opcode scan. See
  `techarticle_nostalgicplayer_amiga_format.md` + `github_nostalgicplayer_csharp.md`.
- **c-flod** (`rofl0r/c-flod`, C) — detects **42 Amiga player variants**
  (index 0–41) via 68000 opcode patterns. See `github_cflod_amiga_player.md`.
- **UADE** `players/DavidWhittaker` — the original 68000 Amiga binary (lead).
- **Bansai's Xenon ZX→C64 conversion** — confirms ZX/C64 share sub-song pointer
  tables + near-identical pattern commands (`forum_csdb_xenon_conversion.md`).

These are Amiga/68000, but the data structures are documented as **compatible
across platforms**, so they illuminate the C64 format too.

## Doc map

- `format_spec.md` — **start here.** Full C64 + Amiga format synthesis (~22 KB).
- `disasm_panther_command_detail.md` — deep Panther.asm command-decoder trace +
  full table dumps.
- `sidid_signature.md` — the variant census (5 patterns, 103-SID breakdown).
- `src/Whittaker_David_Panther.asm` — dmx87's full annotated P1 disassembly
  (the migration starting point). `src/cflod_dwplayer_notes.md` — c-flod raw URLs.
- CSDb: `csdb_scener_and_releases.md`, `csdb_player_technical.md`.
- GitHub: `github_research_index.md` (master tool index), `github_sidid_signatures.md`,
  `github_realdmx_panther_disassembly.md`, `github_cflod_amiga_player.md`,
  `github_nostalgicplayer_csharp.md`, `github_format_cross_platform.md`.
- Interviews/archive: `wayback_interviews_and_workflow.md`,
  `archive_nes_driver_and_vgmpf.md`, `archive_amiga_dw_format.md`.
- Forums/wikis: `forum_wiki_synthesis.md`, `forum_csdb_xenon_conversion.md`,
  `wiki_vgmpf_nes_driver.md`, `wiki_vgmpf_jason_brooke.md`, `hvsc_docs.md`,
  `deepsid_notes.md`, `techarticle_nostalgicplayer_amiga_format.md`.

## Gaps (mostly fillable from OUR binaries at migration)

1. **Only P1 (Panther) is disassembled publicly.** To bound the P2/P3/P5 format
   deltas, disassemble a representative of each from the 103 HVSC SIDs we already
   hold (named in `sidid_signature.md`) — OR ask `realdmx` on GitHub for Lazy
   Jones / Glider Rider / Red Max. **Highest-priority migration prerequisite.**
2. **`pspecial` byte-range map** has a minor cross-source disagreement —
   reconcile against Panther.asm during the disassembly pass.
3. **PSID speed flag (VBI vs CIA) per subtune** — not nailed down here; confirm
   from the SIDs at migration (affects the verify capture path).
4. **Exorcist.sid** — V2/V3-only outlier; confirm whether it's Whittaker's driver
   at all (candidate exclusion).
5. `hvsc84.csv` has 7 P1 false-negatives (NULL engine) — `tools/build_sid_db.py`
   refresh would fix the count (110 → 117).

## Migration starting point

- Disassembly seed: `src/Whittaker_David_Panther.asm` (P1). Format: `format_spec.md`
  + `disasm_panther_command_detail.md`. Cross-platform cross-check:
  NostalgicPlayer (C#) + c-flod (C).
- Canary candidates: Panther (P1, fully decoded) + one P2 (e.g. Red_Max /
  Knight_Games) to validate the register-order delta + one P3 early tune.
- Model the gate as a hard-restart retrigger (not ADSR release); effects are all
  software-side. Verdict = standard write-log instruction-sequence match.
