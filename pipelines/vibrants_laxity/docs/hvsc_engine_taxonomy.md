---
source_url: local: /home/jtr/sidfinity/hvsc84.db + /home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg + https://blog.chordian.net/computer-timeline/ + https://csdb.dk/release/?id=122333 + https://csdb.dk/release/?id=39519 + https://csdb.dk/release/?id=26563 + https://csdb.dk/release/?id=210571 + https://csdb.dk/release/?id=14037
fetched_via: local read + WebFetch
fetch_date: 2026-06-15
author: various (JCH/chordian.net timeline primary; CSDb primary; sidid cadaver primary)
content_date: 2026-06-15
reliability: primary
---

# HVSC Laxity/Vibrants/JCH Engine Taxonomy

## Lineage

```
1987 — JCH OldPlayer (no sequences, nibble-field notes)
1988 — JCH reverses Laxity's C64 player; starts JCH Editor V1 (no sequences)
1988 — JCH Editor V2 (sequences introduced)
1989 — JCH NewPlayer V5/V6/V12/V14/V15 (production players)
1990 — JCH NewPlayer V15/V17/V18/V19/V20 (Laxity joins Vibrants Sep 1990)
1990 — LAXITY EDITOR (pre-dates SidFactory; never public; CSDb #122333 = 1990 release)
       → Vibrants/Laxity (179 SIDs — Laxity's own tunes + Vibrants collaborators)
1991 — JCH NewPlayer V20 (JCH's "last standard player on C64", May 1991)
1991 — JCH Editor V3 final (ED3.04/D15/20.G4)
       → JCH_NewPlayer (3611 SIDs — the dominant format, all versions V1–V21 combined by sidid)
2000 — JCH NewPlayer 21.G6 (Samar Productions)
2005 — JCH NewPlayer 21.g4 beta (Maniacs of Noise + Vibrants)
2006 — JCH NewPlayer 21.g4 final (Laxity, Jan 2006)
       → Laxity_NewPlayer_V21 (313 SIDs — Laxity's rewrite of NP for modern use)
2006 — SID Factory 0.5 Alpha 1 (Laxity, Sep 2006) — FRESH REWRITE
       → SidFactory/Laxity (39 SIDs)
2011 — JCH-Editor 3.1 + NP22-25 (Dane/Booze Design)
       → (Dane_NewPlayer) (5 SIDs)
2020 — SID Factory II first public release (Laxity + JCH + Michel de Bree + Thomas Jansson)
       → SidFactory_II/Laxity (377 SIDs, ongoing)
```

## Engine Counts (HVSC #84)

| Engine name (sidid)       | Count | Key author(s) | Era        | Relationship                     |
|---------------------------|-------|---------------|------------|----------------------------------|
| JCH_NewPlayer             | 3611  | JCH           | 1989–2006  | Main JCH family (all sub-vers)   |
| SidFactory_II/Laxity      | 377   | Laxity+JCH+MB | 2020–      | Modern rewrite, open source      |
| Laxity_NewPlayer_V21      | 313   | Laxity        | 2006       | Laxity's update of JCH NP format |
| Vibrants/Laxity           | 179   | Laxity (TEP)  | ~1990      | The original Laxity editor       |
| Vibrants/JO               | 130   | JO (PJO)      | ~1990s     | Vibrants member, different engine |
| JCH_Protracker            | 94    | JCH           | ~1991      | Compact NP variant (PW focused)  |
| Glover_NewPlayer_V21      | 67    | Glover        | ~2006      | Another NP V21 user              |
| SidFactory/Laxity         | 39    | Laxity        | 2006       | SidFactory 0.5 Alpha             |
| JCH_OldPlayer             | 32    | JCH           | 1987–1988  | Pre-sequence format              |
| (Dane_NewPlayer)          | 5     | Dane          | 2011       | NP22-25 variant                  |
| JCH_DigiPlayer            | 4     | JCH           | 1991       | Digi sample player               |
| 256bytes/Laxity           | 2     | Laxity        | unknown    | 256-byte demo intro player       |
| **TOTAL**                 | **4853** |             |            |                                  |

## Key technical distinctions by engine

### Vibrants/Laxity (the "Laxity Editor")
- Released 1990 (CSDb #122333), authored by Thomas Egeskov Petersen + Scortia
- Five demo tunes ship with it: DXYCP Scroll, Fast Stuff 1, In the Mood Mix, Lethal C., Spacemilk
- 5 signature fragments covering: freq write (abs,Y indexed with voice Y-offset), control
  reg write ($D404/$D40B/$D412 via `99 04 D4`), 4× DEC duration counters, ADSR nibble
  split, filter sweep ($D416)
- Voice stride: Y = 0/7/14 (same stride as standard SID layout, set via `AC ?? ??` LDY abs)
- No source ever released. JCH based his editor on reverse-engineering this player.
- The sidid signature covers a SPECIFIC version; the 179 HVSC SIDs may span slight internal
  variants. Since Laxity never released the editor publicly, all 179 are author-produced
  or produced by Vibrants members with direct access.

### Laxity_NewPlayer_V21
- Laxity's NEW player code written for JCH Editor V3 compatibility (2006 final, CSDb #26563)
- Uses `99 04 D4` (STA ($D404),Y) = same voice-stride control write as Vibrants/Laxity
- Duration counter: `DE ?? ??` (DEC abs,X) + `C9 FF F0` ($FF end sentinel)
- Inherits JCH's 3-sentinel system ($FD=loop, $FE=rest, $FF=end) from NP V3+
- Single-fragment signature → less distinctive than base Vibrants/Laxity

### JCH_NewPlayer (V1–V21)
- All sub-versions require BOTH the base 4 fragments AND one version-specific fragment
- 3-voice model: voice loop X=2,1,0 (DEX/BPL or E0 03/D0)
- Sequence pointer: ZP indirect (B1 ??) from V6 onwards; abs,Y (B9 ??) in early versions
- 3-sentinel system from V3: $FD=loop/restart, $FE=rest, $FF=end
- $7E/$7F = in-sequence command bytes (tie note, tempo change)
- Hard-restart (V0x init): $88 to all 3 $D404/$D40B/$D412, then zero-fill $D400-$D418
- Wave/pulse tables: separate tables advanced by `FE ?? ?? D0` (INC + BNE) from V5+
- Master vol: `A9 0F 8D 18 D4` = $0F to $D418 in base fragment 4 (written every frame?)
- V20 = last "standard" player (1991); V21 = Laxity's 2006 rewrite of same format

### SidFactory/Laxity (2006)
- SEPARATE ENGINE from NP family — Laxity wrote it from scratch in 2006
- Features: dynamic multispeed switching, tempo table, portamento (Driver 5.02+),
  parallel instrument + slide, pointer config to various tables from voices
- Signature is ~30 bytes — much shorter than Vibrants/Laxity (5 fragments = ~100 bytes)
- Bit-flag manipulation ($29 02 / D0 / $29 FD) = toggle pattern unlike NP

### SidFactory_II/Laxity (2020–)
- Open source, cross-platform (Chordian/sidfactory2 on GitHub)
- JCH's "contiguous sequence stacking system" + Protracker note input
- Driver 11.xx series (11.05 current as of 2026)
- B1 ?? (LDA (zp),Y) sequence access; $FF = end; $7E = command marker
- Supports import from Goattracker, CheeseCutter, MOD
- SF2 file format (.sf2 project files) stores song data
- Order list: 2-byte words = [transpose_byte, sequence_number]; $A0 = no transpose
- Sequences: up to 128, up to 1000+ rows; instrument column per row
- Driver versions 11.01–11.05 are the relevant HVSC-era drivers
  (11.03 = filter enable flag, 11.04 = note delay, 11.05 = pulse reset flag)

## Example SIDs (for disassembly target selection)

### Vibrants/Laxity
- `MUSICIANS/H/HeatWave/Intromusic.sid` (by Marvin Severijns & Michel de Bree)
- `MUSICIANS/L/Laxity/Screw_Normal.sid` is under SidFactory/Laxity, NOT Vibrants/Laxity

### Laxity_NewPlayer_V21
- `MUSICIANS/H/Hultink_Gerard/Little_Jazz_Cafe.sid`
- `MUSICIANS/B/Bayliss_Richard/Blazon_Slideshow.sid`

### SidFactory/Laxity
- `MUSICIANS/L/Laxity/Screw_Normal.sid`
- `MUSICIANS/F/Freqvibez/El_Quip_Nut.sid`

### JCH_NewPlayer
- `MUSICIANS/O/Odkin/Dance1.sid`

## Version number conventions

Sidid uses "V1" through "V21" for the version field; the CSDb releases use the "G" suffix
for "generation" (G4 = generation 4, meaning 4th major release of a given version). So
"NewPlayer V20.G4" = player version 20, 4th generation build.

The "V0x" sub-signature in sidid = the INIT pattern common across all JCH NewPlayer versions
(the hard-restart init fragment $98 99 00 D4 C8 C0 19 D0 F8 + $A9 88 for all control regs).
