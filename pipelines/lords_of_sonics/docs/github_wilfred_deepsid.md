---
source_url: multiple (see body)
fetched_via: direct
fetch_date: 2026-06-16
author: unknown
content_date: 2026-06-16
reliability: primary
---

# LordsOfSonics/MS — GitHub / WilfredC64 / DeepSID Research

## Summary

"LordsOfSonics/MS" is a C64 SID player engine authored by Markus Schneider (MS = Markus Schneider)
of the demo/music group **Lords of Sonics** (LOS), a German C64 group founded in 1988.
The engine is distinct from the later **X-Ample** family (though Schneider joined X-Ample in 1989
and co-created **Compotech** there). The `sidid.cfg` detection database confirms this as a separate
engine entry from X-Ample, with one named sub-variant: **(Parsec)**.

---

## 1. sidid.cfg — cadaver/sidid (primary source)

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg

The LordsOfSonics/MS entry appears between Martin_Wheeler and Luigi_Recanatese:

```
Martin_Wheeler
A2 02 A9 00 9D ?? ?? 9D ?? ?? BD ?? ?? A8 BD ?? ?? 99 02 D4 BD ?? ?? 99 03 D4

LordsOfSonics/MS
79 ?? ?? 0A A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? AC ?? ?? BD ?? ?? 99 ?? D4
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4
(Parsec)
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06

Luigi_Recanatese
```

### Interpretation of signatures

**Base LordsOfSonics/MS signature (line 1):**
```
79 ?? ?? 0A A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? AC ?? ?? BD ?? ?? 99 ?? D4
```
- `79 ?? ??` = ADC ($addr),Y — adding with Y index, likely a note/freq table lookup
- `0A` = ASL A (shift left)
- `A8` = TAY
- `B9 ?? ??` = LDA ($addr),Y — table read with Y
- `9D ?? ??` = STA ($addr),X — write to indexed location
- `99 ?? D4` = STA $D4??,Y — SID write via Y indexing

This pattern suggests a 3-voice loop iterating with X (0..2) writing SID registers, with
Y used for note/freq table indexing and a SID write via Y-indexed store `99 ?? D4`.

**Base LordsOfSonics/MS signature (line 2):**
```
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4
```
- `AC ?? ??` = LDY $addr — load Y from absolute address
- `AD ?? ?? 29 04 C9 04 F0 ??` = LDA $addr; AND #$04; CMP #$04; BEQ ?? — test bit 2
- `BD ?? ??` = LDA $addr,X
- `99 01 D4` = STA $D401,Y — voice freq high write (Y-indexed)
- `BD ?? ??` = LDA $addr,X
- `99 00 D4` = STA $D400,Y — voice freq low write (Y-indexed)
- `3D ?? ??` = AND $addr,X
- `99 04 D4` = STA $D404,Y — voice control register write (Y-indexed)

This is the core frequency + control register dispatch; writes $D400, $D401, $D404 via Y-indexed
STA, suggesting voices are laid out with Y stepping by 7 (standard SID voice stride).

**(Parsec) sub-variant signature:**
```
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06
```
- `9D ?? ?? 9D ?? ?? 9D ?? ??` = STA $addr,X × 3 — clearing 3 consecutive table slots with X index
- `CA 10 E5` = DEX; BPL -27 — countdown loop (X from some value, likely $18=24 or similar, clearing the table)
- `A9 ?? 8D ?? ??` = LDA #imm; STA $addr — load immediate and store (chip init)
- `A9 01 8D ?? ??` = LDA #$01; STA $addr — write 1 to some control register
- `A2 18 A9 00 9D 00 D4 CA 10 FA` = LDX #$18; LDA #$00; STA $D400,X; DEX; BPL -6 — zero all 25
  SID registers ($D400..$D418) by counting X down from $18 to 0 (standard SID reset loop)
- `60` = RTS
- `A9 ?? 8D 18 D4` = LDA #imm; STA $D418 — set master volume
- `A2 02 8E ?? ??` = LDX #$02; STX $addr — set voice count or loop index to 3

This is the **init routine** of the Parsec variant: clears 3 table ranges, resets all SID registers
to zero, RTS, then sets master volume and initializes voice loop counter.

---

## 2. WilfredC64/player-id — sidid.cfg copy

Source: https://github.com/WilfredC64/player-id
Config directory: https://github.com/WilfredC64/player-id/tree/master/config

Files present: `sidid.cfg`, `sidid.nfo`, `tedid.cfg`

The `sidid.cfg` in WilfredC64/player-id contains **identical** LordsOfSonics/MS entry to the
cadaver/sidid version (confirmed by cross-fetch). The player-id tool is a Rust reimplementation
of cadaver's sidid utility; it uses the same signature file format.

The entry in WilfredC64's `sidid.cfg`:

```
LordsOfSonics/MS
79 ?? ?? 0A A8 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? AC ?? ?? BD ?? ?? 99 ?? D4
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4
(Parsec)
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06
```

---

## 3. X-Ample — separate but related engine (context)

The X-Ample entry is **distinct** from LordsOfSonics/MS in sidid.cfg. Markus Schneider joined
X-Ample Architectures in 1989 (after ~7 weeks of driver-merging work). The sub-variant
`(Compotech_V2.x)` under X-Ample is credited to X-Ample Architectures, not Lords of Sonics
directly.

X-Ample entry in sidid.cfg (for comparison):

```
X-Ample
9D ?? ?? BD ?? ?? 29 7F 9D ?? ?? C8 98 9D ?? ?? BD ?? ?? 29 80 9D ?? ?? BC ?? ?? B9 ?? ?? 29 0F 9D ?? ?? 9D
(Compotech_V2.x)
A9 ?? 8D ?? ?? CE ?? ?? 10 ?? A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 90 ?? 20 ?? ?? ?? ?? 69 07 AA ?? 15 90 ?? A9 ?? 09 ?? 8D
(Sonic/SDS)
BD ?? ?? D0 1B 9D 04 D4 F0 19 A9 00 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 02 8D ?? ?? 4E ?? ?? 90 B3 20 ?? ?? 8A 18 69 07 AA C9 15 90 EF A9 00 09 ?? 8D 18 D4 A9 00 8D 16 D4 A9 00 F0 12 CE ?? ?? 10
(Thomas_Detert)
8D ?? ?? CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 20 ?? ?? 8A 18 69 07 AA C9 15 90 F1 A9 ?? 09 0F 8D 18 D4 A9 ?? 8D 16 D4 A9 00 F0 03 20 ?? ?? 60
(XTracker_V4.1x)
CE ?? ?? 10 05 A9 ?? 8D ?? ?? A2 00 20 ?? ?? A2 ?? 20 ?? ?? A2 ?? 20 ?? ?? A9 ?? 09 ?? 8D 18 D4 A9 ?? 8D 16 D4
(XTracker_V4.2x)
A0 00 F0 01 60 A9 ?? 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 ?? 8D ?? ?? 4E ?? ?? B0 07 29 00 9D 04 D4 F0 03 20 ?? ?? 8A 18 69 07 AA C9 15 90 E8 A9 ?? 09 ?? 8D 18 D4
(X-Ample_Digi)
29 1F 8D ?? ?? C8 B1 ?? C9 80 90 ?? 29 3F 8D ?? ?? C8 B1 ?? AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD AE ?? ?? BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A9 ?? 8D 0E DD
```

The Compotech_V2.x variant is listed under X-Ample, not LordsOfSonics. CSDb release
`https://csdb.dk/release/?id=122614` confirms: **Compotech V2.1** (Aug 1995) is credited to
X-Ample Architectures with authors Chap Bizarre, Joachim Fräder, and Markus Schneider.

---

## 4. Group & Author Information

### Lords of Sonics (LOS)

- Founded: 1988, Germany
- Members: Markus Schneider (musician/programmer), Jens Blidon (musician)
- Type: Demo Group + Music Group
- CSDb group page: https://csdb.dk/group/?id=757

Releases (from CSDb group page, all music):
1. The Music of Platou (1988)
2. Beyond the Zero (1988)
3. Babylon Five (1988, one-file demo)
4. No Mercy Title (1989)
5. No Mercy Music (1989)
6. Double Density (1989)
7. Demo Musics (1989)

### Markus Schneider (MS) — player author

Source: https://www.vgmpf.com/Wiki/index.php?title=Markus_Schneider

- Spent ~2 months in 1988 writing a sound driver for Jens Blidon
- This driver became **Parsec Music Editor** — the early LordsOfSonics/MS engine
- After LOS era, merged driver technologies with X-Ample (~7 weeks, 1989)
- Joined X-Ample Architectures as composer + programmer
- Co-created **Compotech** at X-Ample (→ classified under X-Ample in sidid.cfg, not LOS)
- For Amiga work, received a special version of TFMX-Editor from Chris Hülsbeck (1990)

### Engine lineage

```
1988: Markus Schneider writes LordsOfSonics/MS (a.k.a. Parsec Music Editor)
       └── Used for LOS group music releases (No Mercy, Double Density, etc.)
1989: MS joins X-Ample; merges driver tech
       └── Compotech V2.x → classified as X-Ample sub-variant in sidid.cfg
```

The "MS" suffix in the sidid.cfg entry name stands for "Markus Schneider."

---

## 5. HVSC path

Markus Schneider's SIDs live at:
```
HVSC/MUSICIANS/S/Schneider_Markus/
```

Files visible via DeepSID and textfiles archive include:
- Double_Density_Commercial.sid
- No_Mercy.sid (13+ subtunes)
- Xiphoids.sid
- Second_World.sid
- Lingo.sid (CSDb entry: https://csdb.dk/sid/?id=25598)

These would be the primary corpus for LordsOfSonics/MS engine SIDs in HVSC.

---

## 6. DeepSID

Source: https://deepsid.chordian.net/

DeepSID provides a profile/stats tab for each SID showing player detection (derived from sidid).
No new LordsOfSonics information beyond what sidid.cfg provides was found via DeepSID web pages
directly (the player detection JS/config is driven by the same sidid.cfg).

---

## 7. Compotech V2.1 (CSDb release context)

Source: https://csdb.dk/release/?id=122614

- Title: Compotech V2.1 (also listed as Comptech V2.1)
- Year: August 1995
- Type: C64 Tool
- Developer: X-Ample Architectures
- Authors: Chap Bizarre, Joachim Fräder, Markus Schneider
- Format: D64 disk image

This is the evolution of the LordsOfSonics/MS Parsec driver into the X-Ample organisation.
The sidid.cfg correctly distinguishes the two: LordsOfSonics/MS = pre-X-Ample era Parsec engine;
Compotech_V2.x = X-Ample Architectures era.

---

## Leads to follow

1. **Disassemble HVSC/MUSICIANS/S/Schneider_Markus/ SIDs** — confirm which files are detected
   as LordsOfSonics/MS vs X-Ample/Compotech. Run `sidid` on each. The pre-1989 releases
   (No_Mercy, Double_Density, Demo_Musics) are the most likely LordsOfSonics/MS candidates.

2. **CSDb SID entry for Lingo** (https://csdb.dk/sid/?id=25598) — fetch when CSDb is up (was
   503 at fetch time). Should confirm the player classification for an early LOS SID.

3. **Total SID count in HVSC under Schneider_Markus/** — run `find hvsc84/MUSICIANS/S/Schneider_Markus/ -name "*.sid"` locally to get the complete list.

4. **Confirm sidid detection of the Parsec sub-variant** — the (Parsec) signature is an INIT
   routine pattern; the two base signatures are the PLAY routine. Most SID files will match
   one of the two base lines; the Parsec variant is an additional discriminator for the
   Parsec Music Editor version specifically.

5. **X-Ample / Compotech separation** — determine whether any Schneider_Markus/ SIDs are
   classified as X-Ample vs LordsOfSonics. The 1989+ titles (after joining X-Ample) may
   use the Compotech engine.

6. **Check STIL entries** — the HVSC STIL (SID Tune Information List) often records the
   player tool used. Check `STIL.txt` for entries under `Schneider_Markus/`.

7. **WilfredC64/player-id sidid.nfo** — fetch https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.nfo
   for human-readable notes on each player, including LordsOfSonics/MS description.

8. **CSDb search for "Parsec" editor** — the Parsec Music Editor may have its own CSDb tool
   entry with version history and download. Try: https://csdb.dk/search/?seinsel=releases&search=Parsec+Music+Editor

9. **Game credits** — the VGMPF page notes Schneider scored games 1988–1992 with this driver.
   Identifying which games used LordsOfSonics/MS vs Compotech would confirm the engine's
   active deployment period.
