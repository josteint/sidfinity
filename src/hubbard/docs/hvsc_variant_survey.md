---
source_url: local: data/C64Music/
fetched_via: local read
fetch_date: 2026-04-11
author: "compiled locally from HVSC SIDID scan (56,032 SIDs in MUSICIANS + 4,540 in GAMES/DEMOS)"
content_date: "2026-04-11 (scan date)"
reliability: secondary
---
# Rob Hubbard Player Variants — HVSC Survey

Full scan of 56,032 SIDs in HVSC MUSICIANS directory plus 4,540 SIDs in GAMES/DEMOS.
Scan date: 2026-04-11.

## SIDID Signature Architecture

The `sidid.cfg` file defines a hierarchy for Hubbard-related signatures:

```
Rob_Hubbard          — 6 signature patterns (main player)
  (Rob_Hubbard_Digi) — sub-variant: 4-bit PCM digi playback
  (Giulio_Zicchi)    — sub-variant: Zicchi's modifications
  (Bjerregaard)      — sub-variant: JB's version

Paradroid/HubbardEd  — separate signature (editor variant)
Paradroid/Lameplayer  — separate signature (simplified variant)
Jason_Page/RobTracker — separate signature (modern reimplementation)
```

Parenthesized names are sub-variants reported under their parent. SIDID reports the
PARENT name when a sub-variant matches -- so `Giulio_Zicchi` songs report as
`Rob_Hubbard`, and `Bjerregaard` songs report as... `Bjerregaard` (it has its own
top-level detection chain).

## Variant Counts in HVSC

### Rob_Hubbard (main signature)
Matches ~82 SIDs in Hubbard_Rob/ plus many elsewhere. Includes:
- All of Rob Hubbard's own compositions (except modern recreations)
- Giulio Zicchi's 7 SIDs (all report as Rob_Hubbard)
- Geir Tjelta's ~15 Hubbard-driver tunes (report as Rob_Hubbard)
- Laxity's 31 Hubbard-driver tunes (report as Rob_Hubbard)
- Scattered SIDs by other musicians who reused the driver

### Bjerregaard (sub-variant with own detection)
**65 SIDs total across HVSC MUSICIANS:**

In `/MUSICIANS/B/Bjerregaard_Johannes/` (61 SIDs detected as Bjerregaard):
Most of his catalog uses his own Bjerregaard variant of the Hubbard player.

Exceptions in the Bjerregaard directory that use OTHER players:
- `2nd.sid` — Antony_Crowther_V3
- `Mus86.sid` — Antony_Crowther_V3
- `Sarah.sid` — Antony_Crowther_V3
- `Skateboard.sid` — Antony_Crowther_V3
- `Tuba.sid` — Antony_Crowther_V3
- `Camel_Riders_Inc.sid` — Rob_Hubbard (original, not Bjerregaard variant)
- `Eagles.sid` — Rob_Hubbard
- `Ragtime_Anno_87.sid` — Rob_Hubbard
- `Spacegame_Music.sid` — Rob_Hubbard
- `Who_Is_Robb_Vol_1.sid` — Rob_Hubbard
- `USA_Tune.sid` — JCH_NewPlayer
- `Vikings_loader.sid` — David_Whittaker

Some Bjerregaard SIDs also detected as `MoN/Bjerregaard` (13 SIDs) — these use
the Masters of Noise variant of the Bjerregaard player.

Outside Bjerregaard directory:
- `J/Jensen_Henrik/Funitrax.sid` — Bjerregaard
- `J/Jensen_Henrik/Hot_Shoe_Song.sid` — Bjerregaard
- `J/Jensen_Henrik/Squelc_preview.sid` — Bjerregaard
- `S/Swallow/NightDawn_Remix.sid` — Bjerregaard

### Giulio_Zicchi (sub-variant, reports as Rob_Hubbard)
**7 SIDs in `/MUSICIANS/Z/Zicchi_Giulio/`:**
- Armourdillo.sid
- Electric.sid
- Gallery_1.sid
- Hell_for_Leather.sid
- Stunt_Bike_Simulator.sid
- Sweep.sid
- Zone_Z.sid

All 7 report as `Rob_Hubbard` via sidid (the Giulio_Zicchi signature is a sub-match).
No Giulio_Zicchi matches found elsewhere in HVSC (0 in MUSICIANS, 0 in GAMES/DEMOS).
Zicchi's modifications to the player are minimal and localized.

### Paradroid/HubbardEd
**0 SIDs matched** in the full HVSC scan. The signature `B1 FC 10 1B C9 FF F0 12 C9 FE F0 0A`
uses fixed ZP address $FC which is specific to the editor binary, not to song rips.
Songs composed in the Paradroid editor but ripped as standalone SIDs would match the
main Rob_Hubbard signature instead.

### Paradroid/Lameplayer
**21 SIDs in `/MUSICIANS/P/Paradroid/`:**
All of Paradroid's own compositions. This is a simplified variant of the Hubbard player.
Songs: Airwolf, Andy_2, Andy_3, Axel_F, Bangkok_Knight, Complications, Crack_Mix,
Diflex, Enola_Gay, Goldrunner, Griffs_Tune, I_Ball, Jays_Tune, Last_V8, PB_Intro,
Robocop, Tears, Terminator, Thing_on_a_Spring, Wings, Zoolook_Mix.

Note: Paradroid also has `Airwolf_88.sid` which uses MoN/FutureComposer instead.

### Jason_Page/RobTracker
**6 SIDs in Hubbard_Rob/ directory** (modern conversions by Jason Page):
- Go_Go_Dash, Lakers_vs_Celtics, Lion_Heart, Pacific_Coast, Radio_ACE, Sun_Never_Shines

These are NOT original Hubbard driver songs. Jason Page reimplemented a Hubbard-compatible
player called RobTracker and used it to compose new songs in the Hubbard style.

## Key Musicians Using Hubbard-Derived Players

| Musician | Player variant | SID count | Notes |
|----------|---------------|-----------|-------|
| Rob Hubbard | Rob_Hubbard | 82 | Original driver author |
| Johannes Bjerregaard | Bjerregaard + MoN/Bjerregaard | 65+ | Modified Hubbard player |
| Laxity (Thomas Mogensen) | Rob_Hubbard | 31 | Used Hubbard driver via editor |
| Paradroid | Paradroid/Lameplayer | 21 | Simplified variant |
| Geir Tjelta | Rob_Hubbard | ~15 | Via Moz(IC)art editor (ACE II) |
| Giulio Zicchi | Rob_Hubbard (Giulio_Zicchi sub) | 7 | Minor driver modifications |
| Henrik Jensen | Bjerregaard | 3 | Used Bjerregaard's variant |
| Jason Page | Jason_Page/RobTracker | 6 | Modern reimplementation |
| Adam Gilmore | Rob_Hubbard | 1 | New_Tune_1.sid |
| David Green | Rob_Hubbard | 1 | Dark_Shades.sid |
| Swallow | Bjerregaard | 1 | NightDawn_Remix.sid |

## Implications for Decompiler

1. **The Bjerregaard variant is the largest derived player family** (65+ SIDs). Its
   signature differs from Rob_Hubbard in the SID register write sequence. If we want
   to support Bjerregaard SIDs, we need a separate parser path.

2. **Giulio Zicchi's variant is tiny** (7 SIDs) and reports under Rob_Hubbard. These
   may work with the standard Hubbard decompiler or need minor adjustments.

3. **Paradroid/Lameplayer is self-contained** (21 SIDs, all by Paradroid). Worth
   supporting if we want to cover scene musicians who reused the driver.

4. **Laxity's 31 SIDs use the standard Rob_Hubbard signature** — they were composed
   with the Laxity Editor (CSDb #122333) which wraps the original Hubbard driver.
   These should work with the standard decompiler.

5. **RobTracker songs are modern** and use a different player entirely. Not worth
   targeting for the Hubbard decompiler.

## SIDID Signature Bytes

### Rob_Hubbard main (6 patterns)
```
BD ?? ?? 99 ?? ?? 48 BD ?? ?? 99 ?? ?? 48 BD ?? ?? 48 BD ?? ?? 99 ?? ?? BD ?? ?? 99 END
2C ?? ?? 30 ?? 70 ?? B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 98 38 END
AE ?? ?? AD ?? ?? 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? C9 FF D0 ?? A9 ?? 9D ?? ?? FE END
99 04 D4 BD ?? ?? 99 02 D4 48 BD ?? ?? 99 03 D4 48 BD ?? ?? 99 05 D4 END
2C ?? ?? 70 ?? FE ?? ?? AD ?? ?? 10 ?? C8 B1 ?? 10 ?? 9D ?? ?? 4C END
0A 0A 0A AA BD ?? ?? 8D ?? ?? BD ?? ?? 2D ?? ?? 99 04 D4 END
```

### Giulio_Zicchi sub-variant
```
CA 30 03 4C ?? ?? 60 A2 00 8E ?? ?? E8 8E ?? ?? 60 A0 00 END
```
DEX; BMI +3; JMP; RTS; LDX #$00; STX; INX; STX; RTS; LDY #$00
Init/reset sequence — different init code from standard Hubbard.

### Bjerregaard variant
```
99 03 D4 AE ?? ?? 9D ?? ?? 68 9D ?? ?? A9 01 9D END
```
STA $D403,Y (freq_hi); LDX; STA workspace; PLA; STA workspace; LDA #$01; STA
Different register write order from standard Hubbard.

### Paradroid/Lameplayer
```
90 2D C9 E0 B0 09 0A 0A 0A 9D END
```
BCC; CMP #$E0; BCS; ASL; ASL; ASL; STA
Simplified instrument lookup.
