<!--
provenance:
  source_url: Cadaver's SIDId config (sidid.cfg) — canonical copy mined locally from
              tmp/dmc_hunt/player-id/config/sidid.cfg and deprecated/gt2_pipeline/tools/sidid.cfg
              (both identical for the Soundmonitor block); upstream maintained at
              github.com/WilfredC64/player-id (/config, format /doc/Signature_File_Format.txt)
              and the original cadaver/sidid (Covert Bitops). HVSC naming cross-checked against
              the local hvsc84.db (engine column) opened READ-ONLY.
  fetched_via: local file read (READ-ONLY) + read-only sqlite query of hvsc84.db + WebFetch of the
              WilfredC64/player-id GitHub page for provenance/spelling.
  fetch_date: 2026-06-13
  author: signatures by Cadaver / iAN CooG / Wilfred Bos / Ice00 et al. (SIDId / player-id project).
  content_date: SIDId V1.09 (2012) lineage; player-id signatures maintained through 2020s.
  reliability: PRIMARY for the byte signatures + HVSC naming (verified against local DB);
              SECONDARY for upstream repo structure (from the GitHub page).
-->

# SoundMonitor — detection (SidId / player-id) signatures + HVSC naming

## TL;DR for SIDfinity
- **HVSC / sidid engine name = `Soundmonitor`** (one word, that exact casing). Our local
  `hvsc84.db` has **3625** SIDs tagged `Soundmonitor` + **11** tagged `Chris_Huelsbeck` (the
  Hülsbeck-digi variants), matching the task's ~3,625 estimate.
- The canonical signature DB is **Cadaver's `sidid.cfg`** (XSidplay2/SIDId V1.09 format),
  maintained today at WilfredC64/player-id. JC64dis embeds the same engine
  (`SidId.java`: "SIDId V1.09 by Cadaver (C) 2012").
- A single `Soundmonitor` section holds the **master signature plus ~20 sub-variant patterns**
  (Rockmonitor 2/3/3h/4/5.0/5.1, MusicMaster 1/2/TMM, DrumMaker2, DigiMonitor, JamMasterV1,
  Karl_XII/BeatBox, Huelsbeck_Digi V1/V2, plus related digi packers). All match → reported as
  `Soundmonitor`.
- **Our repo's `tools/sidid.cfg` does not exist** (no SoundMonitor entry to lack); the durable
  copies are in `tmp/dmc_hunt/player-id/config/sidid.cfg` and
  `deprecated/gt2_pipeline/tools/sidid.cfg`. If we wire sidid into the SoundMonitor pipeline,
  copy the block below.

## SidId .cfg format primer
Per-player section = a name line, then one or more hex byte-pattern lines. Tokens:
`??` = any single byte (wildcard); `AND` (or `&&`) = both adjacent sub-patterns must be present;
`END` terminates a pattern (Cadaver's original uses explicit `END`; the WilfredC64 fork's
`/doc/Signature_File_Format.txt` documents the same with `&&`). Matching is a substring scan over
the loaded C64 image. Engine source: `tmp/jc64/src/sw_emulator/software/SidId.java`
(`identifyBuffer`), constants `END=-1, ANY=-2, AND=-3, NAME=-4`.

## The canonical `Soundmonitor` signature block (verbatim, from Cadaver's sidid.cfg)

```
Soundmonitor
D0 16 BD ?? ?? 29 10 F0 2A BD ?? ?? 9D ?? ?? BD
(DUSAT/RockMon2)
48 29 0F AA CA 68 4A 4A 4A 4A 18 69 ?? 8D ?? ?? 4C
(MusicMaster_1)
8D 0C CE 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 F4
(DUSAT/RockMon3)
4A 4A 4A 4A AA BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A2 ?? 8A 48 20 ?? ?? 68 CA D0 ?? A9 ?? 8D 18 D4
(DUSAT/RockMon3h)
8D 0C CE 20 70 CE 60 A0 17 A9 00 99 00 D4 99 F4
(DUSAT/RockMon4)
8D 0C CE 4C 18 CA 60 A0 17 A9 00 99 00 D4 99 F4
(DUSAT/RockMon5.0)
8D 04 D4 8D 0B D4 8D 12 D4 A9 00 99 00 D4 99 AE
(DUSAT/RockMon5.1)
8D 04 D4 8D 0B D4 8D 12 D4 A9 00 99 00 D4 99 B0
(BeatBox/Karl_XII)
8D 1E ?? 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 06
(Karl_XII)
8D CC CD 8D 18 D4 60 A0 17 A9 00 99 00 D4 99 B4
(DigiMonitor)
AA CA 8E ?? ?? 8E ?? ?? AD ?? ?? 8D ?? ?? AD ?? ?? 29 F0 0D ?? ?? 8D ?? ?? AD 18 D4 60
(JamMasterV1)
B9 ?? ?? 8D 18 D4 20 ?? ?? E8 E8 D0 ?? BD ?? ?? 18 7D ?? ?? A8 B9 ?? ?? 8D 18 D4
(Syndicate/BB)
AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD BD ?? ?? 8D ?? ?? A9 00 85 ?? BD ?? ?? 85 ?? BD ?? ?? 8D
(Digitronix)
8D 0C CE 8D FE 9F 60 A0 17 A9 00 99 00 D4 99 F4
(MusicMaster_2)
8D 72 CE 60 A0 17 A9 00 99 00 D4 99 5A CE 99 73 && BD 00 9C 8D 04 DD BD 00 9D
(DrumMaker2)
8D 72 CE 60 A0 17 A9 00 99 00 D4 99 5A CE 99 73 && BD 00 9C 20 60 CC BD 00 9D
(MusicMaster_TMM)
8D 0C CE 8D FF ?? 60 A0 17 A9 00 99 00 D4 99 F4
(Huelsbeck_Digi_V1)
A0 ?? A5 ?? CD ?? ?? F0 ?? B1 ?? 8D ?? ?? 29 0F
(Huelsbeck_Digi_V2)
A0 ?? A5 ?? C5 ?? F0 ?? B1 ?? 85 ?? 29 0F 4A 18 69 ?? 8D 18 D4
(Cavi_Digi)
4A 4A 4A 8D 18 D4 A4 ?? 88 D0 ?? 60 29 0F 8D 18 D4 A4 ?? 88 D0 ?? 60
(ReD_Packed)
F0 01 60 20 ?? ?? A9 ?? 8D FB ?? 4C 05 ?? 4C
(Mahoney_Digi)
```
(In Cadaver's distribution every pattern line is terminated with `END`; the `&&` in
MusicMaster_2 / DrumMaker2 = the `AND` composite-match operator. The lines above are the
content; append `END` per-line for the strict Cadaver format.)

## Decoding the most useful patterns (cross-checked against our disasm)

- **`(MusicMaster_1)` `8D 0C CE  8D 18 D4  60  A0 17  A9 00  99 00 D4  99 F4 …`**
  = `STA $CE0C : STA $D418 : RTS` (end of an effect/`setFilterVol`) immediately followed by the
  **init clear loop** `LDY #$17 : LDA #$00 : STA $D400,Y : STA $CEF4,Y`. This is the canonical
  **standalone MusicMaster** at base `$Cxxx` with work area at **`$CExx`** (`$CEF4` = the
  `actual*` shadow block; `$CE0C` = `actualFilterCtrlVol`-equivalent). It confirms the standalone
  `init=$C000 / play=$C020` layout, of which the JC64dis "Shades" (work area at `$73xx`/`$03xx`,
  player at `$7000/$742E`) is a relocated copy. `LDY #$17` (=23) clears 24 SID registers.
- **`(MusicMaster_TMM)` `8D 0C CE 8D FF ?? …`** and **`(Digitronix)` `8D 0C CE 8D FE 9F …`** —
  MusicMaster variants that additionally poke a flag (`$FF??` / `$9FFE`) after `$CE0C`.
- **`(DUSAT/RockMon5.0/5.1)` `8D 04 D4 8D 0B D4 8D 12 D4 A9 00 99 00 D4 99 {AE,B0}`** =
  `STA $D404 : STA $D40B : STA $D412` (the three voice **control** registers — gate handling)
  then a SID clear loop ending at `$??AE`/`$??B0`. Matches the Rockmonitor5 disasm
  (`outCtrlV1/V2/V3` + `clearDataArea`).
- **`(Huelsbeck_Digi_V1/V2)` `A0 ?? A5 ?? C5/CD ?? F0 ?? B1 ?? … 29 0F …`** = the 4-bit-nibble
  sample player (`AND #$0F` extracts a nibble; `STA $D418` plays it) — the digi sub-engine seen
  in Rockmonitor/`NMIRoutine`. These are the tunes HVSC files under `Chris_Huelsbeck`.

## HVSC naming (verified against local hvsc84.db, READ-ONLY)
- Engine column value: **`Soundmonitor`** (3625 rows). Example paths:
  `DEMOS/0-9/1988_Carat_tune_1.sid`, `DEMOS/A-F/A_Funky_Toon.sid`,
  `MUSICIANS/K/Kohal/Rock_tune_1.sid`, `MUSICIANS/K/Koske_Erich/Tune_1.sid`,
  `MUSICIANS/U/Unknown_Composer/Beatles-Penny_Lane.sid`.
- **`Chris_Huelsbeck`** (11 rows) is a *separate* engine tag in HVSC — these are the
  Hülsbeck-digi tunes, matched by a different sidid section:
  ```
  Chris_Huelsbeck
  A8 29 04 D0 0C 98 29 03 F0 07 29 01 D0 34 4C
  99 04 D4 A5 ?? 18 69 01
  ```
  (Note: `Chris_Huelsbeck` ≠ the `Soundmonitor`-block `Huelsbeck_Digi_V1/V2` sub-variants; HVSC's
  SidId mapping routes them differently. Treat the 11 `Chris_Huelsbeck` tunes as a related-but-
  distinct target, likely "The Final Musicplayer"/custom Hülsbeck players, not the M&T MusicMaster.)
- The Rockmonitor/MusicMaster/DrumMaker sub-variants all collapse to the single HVSC engine name
  **`Soundmonitor`** — the parenthesised sub-names above are *informational comments inside the
  one section*, not separate engine labels in HVSC.

## Practical notes
- The standalone MusicMaster is at `init=$C000 / play=$C020`; most HVSC copies are relocated.
  SidId is **relocation-robust** because its anchors are `STA $D4xx` (absolute SID addresses,
  unaffected by relocation) plus short opcode runs — that's why one signature set covers all the
  shifted copies (e.g. Shades @ $7000).
- To detect SoundMonitor in SIDfinity: scan the loaded image for the `Soundmonitor` master
  pattern (`D0 16 BD ?? ?? 29 10 F0 2A …`, the `processNote` note-test `AND #$10`) OR any
  MusicMaster/Rockmonitor sub-pattern; on hit, label `Soundmonitor`. The `AND #$10 / BNE`
  master pattern corresponds to the per-note **option-nibble test** (bit 4) in the bar decoder.
