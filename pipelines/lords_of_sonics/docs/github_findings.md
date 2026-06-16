---
source_url: multiple (see body)
fetched_via: direct
fetch_date: 2026-06-16
author: research agent + local DB query
content_date: 2026-06-16
reliability: primary
---

# LordsOfSonics/MS — GitHub / Open-source Findings

## Summary

"LordsOfSonics/MS" is a C64 SID player engine authored by **Markus Schneider** (MS) of the demo
group **Lords of Sonics (LOS)**, Germany, 1988. Also known as the **Parsec Music Editor**.
123 SIDs in HVSC #84 are detected as this engine (confirmed via local `hvsc84.csv` DB query).

The engine is DISTINCT from the later X-Ample family, though Schneider joined X-Ample in 1989
and co-created Compotech there (sidid.cfg classifies Compotech under X-Ample, not LordsOfSonics).

---

## 1. sidid Detection Signatures

**Source repos (identical content):**
- https://github.com/cadaver/sidid — `sidid.cfg` (canonical)
- https://github.com/WilfredC64/player-id — `config/sidid.cfg` (Rust reimplementation, same file)

Raw signatures in: `src/sidid_signatures.txt`

### Play-routine signatures (two lines required for detection)

**Line 1:**
```
79 ?? ?? 0A A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? AC ?? ?? BD ?? ?? 99 ?? D4
```
Decoded:
- `79 ?? ??` = `ADC ($addr),Y` — accumulator add via Y-indexed indirect; freq/note table lookup
- `0A` = `ASL A` — shift left (×2; double a note index for a 2-byte-per-entry table)
- `A8` = `TAY` — result → Y (now a freq-table byte index)
- `B9 ?? ??` = `LDA ($addr),Y` — load freq byte (lo or hi) from table
- `9D ?? ??` = `STA ($addr),X` — store to voice working buffer (X = voice 0/1/2)
- `99 ?? D4` = `STA $D4??,Y` — SID write using Y as register offset (Y-indexed voice stride)

Implies: Y holds the per-voice SID register offset (0, 7, 14), X is the voice loop index (2→0),
double-index lookup for freq table (2 bytes per note), ADC used to accumulate freq index.

**Line 2:**
```
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4
```
Decoded:
- `AC ?? ??` = `LDY $addr` — load Y (voice SID offset: 0/7/14)
- `AD ?? ?? 29 04 C9 04 F0 ??` = `LDA $addr; AND #$04; CMP #$04; BEQ` — test bit 2 of gate/ctrl byte
- `BD ?? ??` = `LDA $addr,X` — load freq hi from voice table
- `99 01 D4` = `STA $D401,Y` — write freq hi (Y-indexed)
- `BD ?? ??` = `LDA $addr,X` — load freq lo
- `99 00 D4` = `STA $D400,Y` — write freq lo (Y-indexed)
- `3D ?? ??` = `AND $addr,X` — mask control byte with waveform/gate mask
- `99 04 D4` = `STA $D404,Y` — write voice control register (Y-indexed)

Core frequency + gate dispatch. Writes $D400 (freq lo), $D401 (freq hi), $D404 (ctrl/gate)
per voice via Y-indexed STA. Y strides by 7 (standard SID voice register spacing).

### (Parsec) sub-variant — init routine signature

```
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06
```
Decoded:
- `9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5` = three `STA $addr,X`; `DEX; BPL -27` — zero-clear 3 table regions (X countdown loop, clears ~27 bytes per region)
- `A9 ?? 8D ?? ??` = `LDA #imm; STA $addr` — init a control flag
- `A9 01 8D ?? ??` = `LDA #1; STA $addr` — write 1 to a register (possibly tempo/enable)
- `A2 18 A9 00 9D 00 D4 CA 10 FA` = `LDX #$18; LDA #$00; STA $D400,X; DEX; BPL -6` — standard SID reset loop: zero all 25 SID registers ($D418..$D400, X from $18 to $00)
- `60` = `RTS` — init returns here
- `A9 ?? 8D 18 D4` = `LDA #imm; STA $D418` — set master volume (post-init play entry)
- `A2 02 8E ?? ??` = `LDX #$02; STX $addr` — initialize voice loop counter (3 voices, 2→0)
- `CE ?? ?? 10 06` = `DEC $addr; BPL +6` — voice loop control

This is the **init subroutine** of the Parsec variant. The base two-line signature matches the
PLAY routine; Parsec sub-variant tag is an additional discriminator.

---

## 2. HVSC Corpus Count

**Local DB query result (`hvsc84.csv`, 2026-06-16):**
- `LordsOfSonics/MS` total: **123 SIDs**
- Under `MUSICIANS/S/Schneider_Markus/`: 23 LordsOfSonics/MS (+ 38 X-Ample, 18 FC, etc.)
- Engine is shared: composers using it include A-Man, Babyface, Jens Blidon, and others

Top composers by path prefix (partial list from DB):
- `MUSICIANS/A/A-Man/` — 7+ SIDs (Lord, Shock, World_of_Confusion, etc.)
- `MUSICIANS/B/Babyface/` — 10+ SIDs
- `MUSICIANS/S/Schneider_Markus/` — 23 SIDs (earliest, pre-X-Ample era)
- `GAMES/` — 5 game SIDs (Arcade_Pilot, Peter_Pilot, Mean_Car, Shoot_Out, Xytris)

---

## 3. Engine Lineage

```
1988: Markus Schneider writes the driver for Jens Blidon / Lords of Sonics
       └── Engine = "Parsec Music Editor" (also called LordsOfSonics/MS in sidid)
       └── Shared with other composers: A-Man, Babyface, etc.
1989: MS joins X-Ample Architectures
       └── Driver tech merged → Compotech V2.x (classified separately as "X-Ample" in sidid)
1995: Compotech V2.1 released (CSDb #122614) — X-Ample Architectures credit
```

Markus Schneider corpus engine breakdown (Schneider_Markus/ dir):
- LordsOfSonics/MS: 23 (early, 1988–1989)
- X-Ample: 38 (1989+, after joining X-Ample)
- Geir_Tjelta/Comptech-X: 4 (later Compotech variant)
- MoN/FutureComposer: 18 (separate tool, unrelated lineage)

---

## 4. Related Tools / Detection

- **sidid** (cadaver/sidid): C utility that scans SID binaries against sidid.cfg patterns. The
  LordsOfSonics/MS detection requires BOTH signature lines to match (AND logic between lines,
  OR logic for sub-variants in parentheses). Source: https://github.com/cadaver/sidid
- **player-id** (WilfredC64/player-id): Rust reimplementation of sidid. Same sidid.cfg.
  Source: https://github.com/WilfredC64/player-id
- **DeepSID**: Uses sidid-derived classification; no additional player-specific handling found.
  Source: https://github.com/JohanPeeters/DeepSID

No dedicated parser/decompiler for LordsOfSonics/MS format was found in open-source tools.

---

## 5. X-Ample Lineage — Full Signature Block

The X-Ample entry (distinct from LordsOfSonics/MS) has sub-variants:
- `(Compotech_V2.x)` — Schneider's Compotech contribution
- `(Sonic/SDS)` — another X-Ample composer tool
- `(Thomas_Detert)` — Thomas Detert's variant
- `(XTracker_V4.1x)`, `(XTracker_V4.2x)` — XTracker versions
- `(X-Ample_Digi)` — digi variant

The core X-Ample play-routine signature:
```
9D ?? ?? BD ?? ?? 29 7F 9D ?? ?? C8 98 9D ?? ?? BD ?? ?? 29 80 9D ?? ?? BC ?? ?? B9 ?? ?? 29 0F 9D ?? ?? 9D
```
Key differences from LordsOfSonics/MS: uses `29 7F` (AND #$7F, mask bit 7) and `29 80`
(AND #$80, isolate bit 7) suggesting a different waveform/noise dispatch. No `99 ?? D4`
(Y-indexed SID write) — uses different register indexing than LordsOfSonics/MS.

---

## Leads to Follow

1. **sidid.nfo** — fetch https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.nfo
   for human-readable per-engine notes. May contain Parsec Music Editor description.

2. **CSDb search for Parsec Music Editor** — https://csdb.dk/search/?seinsel=releases&search=Parsec+Music+Editor
   May have a tool release with version history and download (D64 disk image).

3. **CSDb group page for Lords of Sonics** — https://csdb.dk/group/?id=757
   Releases list with download links to the actual SID players.

4. **Confirm Parsec vs base variant split** — run sidid locally on Schneider_Markus/ SIDs to
   see which match base vs Parsec sub-variant. The Parsec sub-variant's init differs (table
   clears before SID reset) — may indicate a version boundary in the tool.

5. **Geir_Tjelta/Comptech-X** — 4 Schneider SIDs classified as this engine. Check sidid.cfg
   for its signature block; determine if it's a third distinct branch or a later Compotech label.

6. **Game SIDs** — 5 game SIDs use LordsOfSonics/MS (Arcade_Pilot, Peter_Pilot, Mean_Car,
   Shoot_Out, Xytris). These are likely licensed uses of the Parsec editor and may have
   cleaner/simpler data structures good for initial decompilation.

7. **STIL.txt cross-reference** — check HVSC STIL for LordsOfSonics/MS entries; may record
   tool version or composition credits that identify which Parsec version was used.

8. **A-Man / Babyface CSDb pages** — these composers used the LordsOfSonics/MS engine heavily.
   Their CSDb pages may link to releases where the tool is identified by name.

9. **SIDFactory II** — check if SF2 (https://github.com/Chordian/sidfactory2) has any importer
   for Parsec/LordsOfSonics format. SF2 supports multiple C64 player formats.
