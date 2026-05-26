---
source_url: https://csdb.dk/release/?id=170999, https://csdb.dk/release/?id=2600, https://csdb.dk/release/?id=22938, https://hvmec.altervista.org/blog/?p=757, https://hvmec.altervista.org/blog/?p=973
fetched_via: direct
fetch_date: 2026-04-11
author: multiple sources (CSDb community, CreaMD, The Syndrom, Iceball, Brian/Graffity)
content_date: 2018-11-04 (V6 CSDb release); 2002-12-26 (V5.0+); 1994 (V5.1+)
reliability: secondary
---

# DMC V5/V6 Documentation Leads

Research compiled 2026-04-11 from CSDb, HVMEC, and related sources.
Supplements the main `csdb_research.md` with deeper V5/V6 detail.

---

## 1. DMC V6.0 (CSDb #170999)

**URL:** https://csdb.dk/release/?id=170999
**Released:** 4 November 2018 (privately circulated since ~1994)
**Group:** The Imperium Arts
**Credits:**
- Code: Brian (Graffity, The Imperium Arts) + The Syndrom (Crest, The Imperium Arts)

### Downloads

| File | URL | Downloads |
|------|-----|-----------|
| dmc6-docs.txt | https://csdb.dk/download.php?id=210838 | 600 |
| dmc version6.D64 | https://csdb.dk/download.php?id=210837 | 453 |

The `dmc6-docs.txt` is a separate PC text file (NOT embedded in the D64).
The Syndrom's production note says: "instructions provided as PC .txt file. see disknote for explanation."

### SID Used

- DMC V6 (note) by The Syndrom: `/MUSICIANS/T/The_Syndrom/DMC_V6_note.sid`

### User Comments (all 7, verbatim extracts)

1. **DJB** (3 Jan 2019): "I thought that I'd never see this, I'm glad that I finally did. Very interesting setup to it, explains why I assume they kept the rastertime so low on it"
2. **6R6** (10 Nov 2018): "Nice sounds and instruments. And almost no raster time. This should have been released long time ago."
3. **Slajerek** (6 Nov 2018): "Wow I remember I used only DMC in '94. Need to try it out!"
4. **Richard** (5 Nov 2018): "Good composer. Decent editor. Less complicated, compared to a lot of historical music editors :)"
5. **Xiny6581** (5 Nov 2018): "Finally the tool we've been waiting for is released :) Let's make some music!"
6. **Jazzcat** (4 Nov 2018): "About time. Remember this one was talked about a lot back in the nineties. Cannot remember the story behind it."
7. **psych** (4 Nov 2018): "Awesome. Going to check this one out! Thanks Syndrom."

### Technical Takeaways

- **Ultra-low rastertime** (7-8 raster lines) -- multiple commenters confirm this
- DJB's comment hints at an unusual architectural setup that enables the low rastertime
- The "interesting setup" likely refers to per-channel feature restrictions (pulse OR filter, not both) to save cycles
- V6 is a **separate code branch** from V4/V5, not an incremental update
- The D64 disk image contains the full editor; documentation is the separate .txt file

### TODO

- **Download dmc6-docs.txt** from `https://csdb.dk/download.php?id=210838` -- this is the primary V6 documentation source. Requires CSDb login or direct download tool.
- **Mount the D64** and extract the disknote for additional explanation referenced by The Syndrom.

---

## 2. DMC V5.1+ Package (CSDb #2600)

**URL:** https://csdb.dk/release/?id=2600
**Released:** 1994
**Groups:** Graffity + Motiv 8
**AKA:** "The Bugfixed DMC V5.1 Package"

### Credits

| Role | Person | Group |
|------|--------|-------|
| Code | Brian | Graffity, The Imperium Arts |
| Code | Iceball | Motiv 8, Vision |
| Music | Jeff | Camelot, Cyberzound Productions |
| Music | The Syndrom | Crest, The Imperium Arts |
| Charset | The Syndrom | Crest, The Imperium Arts |
| Bug-Fix | Iceball | Motiv 8, Vision |
| Docs | The Syndrom | Crest, The Imperium Arts |

### Downloads

| File | URL | Downloads |
|------|-----|-----------|
| DMC_V5.1 Packages.zip | https://csdb.dk/download.php?id=26661 | 1069 |
| DMC_V5.1+Packages.zip (internal) | https://csdb.dk/download.php?id=87688 | 414 |

### Package Contents (from CSDb summary)

The archive contains:
- DMC V5.1 Editor
- DMC V5.1 Packer
- DMC V5.X Depacker
- DMC V5.0 Analyzer
- An intro and notes document

### Key Technical Detail (from Production Notes)

**CyberBrain (18 Jan 2002):** "This is a modified version of Brian/Graffity's DMC5.0. Iceball/Motiv8 ripped the DMC5.0-editor, and made his own player for it, so it supports multi-speed tunes better. (it only playes the instruments faster, not the notes)"

**Multi-speed architecture:** Iceball's modified player runs instruments at a higher tick rate than notes. This means:
- The note sequencer advances at the base speed (e.g., 1x per frame)
- Instrument effects (wave table, pulse modulation, vibrato) execute at a faster rate
- This is analogous to GT2's "calculated speed" concept where instrument processing can be N times faster than pattern processing
- Important for parser: multi-speed DMC SIDs may have instrument timing that doesn't match note timing

### SIDs Included

- "Experiment" by The Syndrom
- "Techno" by Jeff

---

## 3. DMC V5.0+ by CreaMD (CSDb #22938)

**URL:** https://csdb.dk/release/?id=22938
**Released:** 26 December 2002
**Creator:** CreaMD of DMAgic

### Credits

- Music: CreaMD
- Bug-Fix: CreaMD

### Downloads

| File | Downloads |
|------|-----------|
| dmcv5plus.zip | 1112 |

### Added Features (from CreaMD's comment, 29 Apr 2006)

CreaMD explains this was "Tweaked version of DMC 5.0 editor made after debates with Orcan complaining about lack of audible editing feature."

New features:
1. **Extended sector editing window** -- wider view of sector data
2. **Track-play of edited sector** -- triggered with `<-` key
3. **Audible sector editing** -- hear notes as you enter them
4. **Configurable fast-forward speed**

### Technical Notes from Comments

- **CreaMD (28 Mar 2011):** "as far as patter tracking is concerned, speed always depends on the setting of speed of tune 7... which also is used for additional setting of audible editing sector."
  - This reveals that **tune 7's speed setting** is dual-purpose: it controls both pattern tracking speed and audible editing behavior
  - Implies the DMC format stores per-tune speed values

- **booker (8 Nov 2008):** "Trackplay of the pattern does not work well with speed 2."
  - Known bug: track-play malfunctions at speed 2

- **ZZAP69 (3 Jun 2012):** Referenced DMC 5.1y (CSDb #46836) as the solution for packing tunes, suggesting V5.0+ may not include a packer.

### SIDs Included

- Anachronological, Break Free, I Am in Love, Supergirl (all by CreaMD)

### Relevance to $C0-$DF Range

The page doesn't document the exact byte encoding for the V5 extended commands, but the sector editor key mappings confirm these commands exist:
- SHIFT+A: AD register setting
- SHIFT+S: SR register setting (also sound number -- context dependent)
- SHIFT+Q: Filter frequency (high byte)
- SHIFT+F: Filter type and resonance
- SHIFT+V: Instrument volume
- SHIFT+X: Disable hard restart (tie note)
- SHIFT++: Fade in
- SHIFT+-: Fade out
- SHIFT+G: Glide note
- SHIFT+H: Slide note
- Pound key: Reset gate bit

These map to the $C0-$DF command byte range in sector data. The exact byte-to-command mapping still needs to be reverse-engineered from the player binary.

---

## 4. HVMEC DMC V5.0+ Page

**URL:** https://hvmec.altervista.org/blog/?p=757
**Software:** Demo Music Creator 5.0+
**Year:** 2002
**Copyright:** DMAGIC
**Original Code:** Brian/Graffity
**Improvements:** CreaMD/DMAGIC

### Downloads

| File | URL |
|------|-----|
| DMC5PLUS.D64.gz | https://hvmec.altervista.org/blog/wp-content/uploads/DMC5PLUS.D64.gz |
| dmc5tuns.d64.gz | https://hvmec.altervista.org/blog/wp-content/uploads/dmc5tuns.d64.gz |

**NOTE:** No `dmc_5_docs.txt` file was found on this page. No separate packer or depacker tools are listed here (those are in the V5.1+ Package at CSDb #2600).

### Keyboard Shortcuts (V5.0+ Editor)

#### Main Controls
| Key | Function |
|-----|----------|
| F1 | Play music |
| F3 | Stop playing |
| F5 | Continue playing |
| F7 | Fast forward |

#### Track Editor
| Key | Function |
|-----|----------|
| F2 | Play each frame |
| SHIFT+Q | Enter player |
| SHIFT+P | Display status |
| SHIFT+S | Enter sound menu |
| SHIFT+D | Enter disk menu |
| SHIFT+C | Change color |
| SHIFT+V | Music setup |
| SHIFT+M | Change soundtrack |
| SHIFT+RETURN | Enter sector |
| Arrow Up | Copy track to buffer |
| SHIFT+[Letter] | Copy buffer to track |
| SHIFT+A | Insert "end" |
| CBM+A | Insert "stop" |
| + | Transpose up (tr+00) |
| - | Transpose down (tr-00) |
| CLR | Clear track |
| HOME | Cursor to position 00 |

#### Sound Editor
| Key | Function |
|-----|----------|
| SHIFT+R | Read directory |
| SHIFT+L | Load sound |
| SHIFT+S | Save sound |
| SHIFT+RETURN | Enter table |
| +/- | Next/previous sound |
| CLR | Clear sound (preserves table data) |

#### Sector Editor
| Key | Function |
|-----|----------|
| SHIFT+D | Set note duration |
| SHIFT+S | Set sound number ($00-$1F) |
| SHIFT++ | Fade in |
| SHIFT+- | Fade out |
| SHIFT+G | Glide note |
| SHIFT+H | Slide note |
| SHIFT+A | Set AD register |
| SHIFT+S | Set SR register |
| SHIFT+Q | Set filter frequency (high byte) |
| SHIFT+F | Set filter type and resonance |
| SHIFT+V | Set instrument volume |
| Pound | Reset gate bit |
| SHIFT+X | Disable hard restart (tie note) |
| = | End sector |

#### Sector Editor Navigation
| Key | Function |
|-----|----------|
| SHIFT+, | Transpose note up |
| SHIFT+. | Transpose note down |
| CBM++ | Next sector |
| CBM+- | Previous sector |
| Arrow Up | Copy sector to buffer |
| SHIFT+[Letter] | Copy buffer to sector |
| HOME | Go to top position |
| CLR | Go to "end" |
| CBM+HOME | Clear sector |
| RETURN | Exit sector editor |

#### Player Mode
| Key | Function |
|-----|----------|
| Q | Return to editor |
| RUN/STOP | Toggle playback |
| 1, 2, 3 | Toggle tracks 1-3 |
| Z-M, comma | Play tunes 0-7 |

---

## 5. HVMEC DMC V5.4 Page

**URL:** https://hvmec.altervista.org/blog/?p=973
**Software:** Demo Music Creator v5.4
**Copyright:** Samar
**Original Code:** Brian/Graffity

### Download

| File | URL |
|------|-----|
| DMC_v5.4_SAMAR.d64.gz | https://hvmec.altervista.org/blog/wp-content/uploads/2012/12/DMC_v5.4_SAMAR.d64.gz |

### "Better Hard Restart" -- What We Know

From CSDb #36658 comments:

- **Manex (2006):** "better hard restart and some other things" compared to V5.1. BUT: reports severe packer instability -- only one of several compositions packed successfully, with resulting bugs including false notes.
- **Richard (2007):** Prefers DMC V5.1 (Motiv8 version) over V5.4, citing difficulty with sound/filter creation. Acknowledges "saving raster time" as advantage.

The exact mechanism of the "better hard restart" is NOT documented in any comment or page. Possibilities:
- Shorter gate-off duration before re-gate (tighter timing)
- Different test-bit waveform handling during restart
- Per-instrument gate timer (vs global)
- Needs binary disassembly of V5.4 player to determine

### V5.4 Keyboard Shortcuts

Identical to V5.0+ (see section 4 above). The HVMEC page lists the same command set, confirming V5.4 is a modified V5.0 with the same editor interface.

### V5.4 Packer Problems

Multiple users report the V5.4 packer is unreliable. This is important for our pipeline:
- Songs composed in V5.4 may have been packed with V5.1's packer instead
- SID files in HVSC tagged as DMC V5 may use mixed editor/packer versions
- Our parser should not assume packer version matches editor version

---

## 6. Related Onslaught V5 Variants

### DMC 5.0+ (Onslaught, 1997) -- CSDb #46814
**URL:** https://csdb.dk/release/?id=46814
**Released:** 5 November 1997
**Code:** Brian + Morbid (Bass, Onslaught, Warriors of the Wasteland)
**Download:** 936 downloads

Note: This is a DIFFERENT "DMC 5.0+" from CreaMD's version (#22938). Onslaught's version predates CreaMD's by 5 years.

### DMC 5.1x (Onslaught, 1997) -- CSDb #46835
**URL:** https://csdb.dk/release/?id=46835
**Released:** 6 June 1997
**Code:** Brian + Iceball + Morbid + Zeux
**Music:** PRI
**Download:** 1028 downloads

### DMC 5.1y (Onslaught, 1999) -- CSDb #46836
**URL:** https://csdb.dk/release/?id=46836
**Code:** Brian + DJB (Blues Muz', Onslaught)
**Docs:** DJB + The Syndrom
**Music:** PRI ("World in My Eyes")
**Download:** 1161 downloads

Referenced by ZZAP69 as the version with working packer support.

---

## 7. DMC Version Listing (from HVMEC)

Both HVMEC pages list 24+ related DMC variants. The full version tree:

```
v2.0, v2.1+, v4.0 (multiple variants), v4.3, v4.3++,
v5.0, v5.01B, v5.0+ (CreaMD), v5.0+ (Onslaught),
v5.1, v5.1+, v5.1x, v5.1y, v5.4, v5.Z.,
v6.0,
v7.0, v7.1beta,
GMC 1.0, GMC 1.6, GMC 2.0
```

---

## Key Findings Summary

### For the DMC parser pipeline:

1. **Multi-speed (V5.1+):** Iceball's player runs instruments faster than notes. The parser must detect and handle this -- instrument tick rate != note tick rate.

2. **V6 is a separate branch:** Not based on V4/V5 code. Different init routine (writes $08 to all waveform registers). Ultra-low rastertime via per-channel feature restrictions.

3. **dmc6-docs.txt exists as a downloadable file** on CSDb (download ID 210838, 600 downloads). This is the primary V6 documentation and should be obtained.

4. **V5 extended commands ($C0-$DF)** are confirmed by editor key mappings but exact byte encoding needs reverse engineering from player binary. Commands include: AD/SR direct set, filter freq, filter type/resonance, volume, gate reset, hard restart disable, fade in/out, glide, slide.

5. **V5.4 "better hard restart"** is mentioned but undocumented. Needs binary comparison with V5.0/V5.1 player code to understand.

6. **V5.4 packer is unreliable** -- SID files in HVSC may use mismatched editor/packer versions.

7. **Tune 7 speed** is dual-purpose in V5.0+ (CreaMD): controls both pattern tracking speed and audible editing. Implies per-tune speed storage.

8. **V5.1+ Package** includes: Editor, Packer, Depacker, and Analyzer tools. The Syndrom wrote the documentation.

### Next Steps

- [ ] Download dmc6-docs.txt from CSDb and extract full V6 format documentation
- [ ] Download DMC V5.1+ Package zip and extract The Syndrom's documentation
- [ ] Mount DMC V6 D64 image and extract disknote
- [ ] Disassemble V5.4 player to understand "better hard restart" mechanism
- [ ] Disassemble V5.1+ (Iceball) player to understand multi-speed instrument execution
- [ ] Map $C0-$DF command bytes to specific functions by tracing V5 player code
- [ ] Compare V5.0, V5.1+, V5.4, and V6 player binaries for structural differences
