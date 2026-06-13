# SID Duzz'It — CSDb Release History + Technical Notes

<!-- PROVENANCE
source_url: https://csdb.dk/search/?seinsel=releases&search=SID+Duzz+It&Go=Go (19 results)
            + individual release pages fetched per ID
fetched_via: WebFetch (csdb.dk HTML → markdown extraction)
fetch_date: 2026-06-13
author: CSDb community database
content_date: 1996–2017
reliability: HIGH for release dates and download links; MEDIUM for technical comments
             (user comments are community, not authoritative dev notes)
-->

---

## Complete Release Inventory (CSDb)

| CSDb ID | Title | Group | Year | Type |
|---------|-------|-------|------|------|
| 161716 | SID Duzz' It V1 [1996] | SHAPE | 1996 | C64 Tool |
| 121615 | SID Duzz' It V0.98 | SHAPE | 1998 | C64 Tool |
| 6106 | SID Duzz' It V0.98A | SHAPE | Sep 1999 | C64 Tool |
| 6107 | SDI Packer V1.0 | SHAPE | 1998 | C64 Tool |
| 6108 | SDI Relocator V1.04 | SHAPE | 1999 | C64 Tool |
| 6109 | Blues Muz' DE-Player V2.00 | Blues Muz'/SHAPE | 1999 | C64 Tool |
| 121619 | SID Duzz' It V1.3 | SHAPE | Apr 2001 | C64 Tool |
| 121622 | SID Duzz' It V1.5 | SHAPE | May 2002 | C64 Tool |
| 7175 | SID Duzz' It V1.801 | SHAPE | Oct 2002 | C64 Tool |
| 76999 | SID Duzz' It V2.0 Beta 7 | SHAPE | 2006 | C64 Tool |
| 84874 | SID Duzz' It V2.0 Beta 8 | SHAPE | 2009 | C64 Tool |
| 78942 | SID Duzz' It V1 [2009] | SHAPE | May 2009 | C64 Tool |
| 132363 | SID Duzz' It V2.1 | SHAPE | Jan 2013 | C64 Tool |
| 114693 | SID Duzz' It V2.1.6 | SHAPE | May 2013 | C64 Tool |
| 118973 | SID Duzz' It (V3.0) MIDI Preview | SHAPE | 2013 | C64 Tool |
| 119228 | SID Duzz' It (V3.0) MIDI Preview 2 | SHAPE | May 2013 | C64 Tool |
| 133692 | SID Duzz' It V2.1.7 | SHAPE | Oct 2014 | C64 Tool |
| 153760 | SID Duzz' It PDF Manual (SDI 2.1.7) | Psylicium/Atlantis | Feb 2017 | C64 Misc |
| 114644 | SDI V2.07 Player ADSR Fixed | SIDWAVE | Jan 2013 | C64 Tool |

### Auxiliary utilities (SDI ecosystem)

- **SDI Packer V1.0** (CSDb #6107, 1998) — unknown function (no technical docs in CSDb page)
- **SDI Relocator V1.04** (CSDb #6108, 1999, by 6R6) — relocates SDI player code; allows it to be placed at non-default addresses for demo/game embedding. Download: `csdb.dk/getinternalfile.php/1358/sdi98ar.zip`
- **Blues Muz' DE-Player V2.00** (CSDb #6109, 1999, by 6R6+GT) — standalone SDI player (alternate name: "sdi player" / "Sid Duzz' it player"). Website: `http://home.eunet.no/~ggallefo/html/sdi.html` (defunct). Download: `csdb.dk/getinternalfile.php/1359/bmdp2.zip`
- **SDI V2.07 Player ADSR Fixed** (CSDb #114644, Jan 2013, bug-fix by SIDWAVE) — fixed ADSR bug: "attack values giving no sound under certain conditions". Source code is 6R6+GT's; SIDWAVE only applied the fix.

---

## Developer Credits

**Geir Tjelta (GT)** of SHAPE / Maniacs of Noise — code, design  
**Glenn Rune Gallefoss (6R6 / GRG)** of SHAPE / Blues Muz' / Nostalgia / Onslaught — code, design, documentation  

Original website: `http://home.eunet.no/~ggallefo/sdi/` (defunct as of ~2010s)  
SourceForge project: `https://sourceforge.net/projects/sidduzzit/` (maintained by Glenn RG64)

---

## Version History — Technical Detail

### V1 [1996] (CSDb #161716)
No technical details on CSDb. Earliest public release.

### V0.98 / V0.98A (CSDb #121615 / #6106, 1998–1999)
No technical details. Code by GT; docs by 6R6.

### V1.3 (CSDb #121619, April 2001)
Code: 6R6 + GT. Documentation: 6R6.  
User note: assembler (BM-Tass) started with `SYS 36673`, password `adelsten`; later `SYS 36864`.

### V1.5 (CSDb #121622, May 2002)
Code + design: 6R6 + GT.  
No technical change notes on CSDb.

### V1.801 (CSDb #7175, October 2002)
Code: 6R6 + GT. Download: `csdb.dk/getinternalfile.php/67838/sdi18.zip`.  
No technical change notes on CSDb. This is the last V1.x release.

### V2.0 Beta 7 (CSDb #76999, 2006)
No technical details on CSDb.

### V2.0 Beta 8 (CSDb #84874, 2009)
Code: 6R6 + GT. Download: `csdb.dk/getinternalfile.php/81631/sdi2beta8.zip`.  
User note (SIDWAVE, 2013): "Use this player, it is ADSR bugfixed" — referring to CSDb #114644.

### V1 [2009] (CSDb #78942, May 2009)
GT's **unreleased version** from the pre-public era, added for archival (mentioned in a GT interview about Paul Norman). Format: `csdb.dk/getinternalfile.php/74931/forbidden.d64`.  
GT note: "V1 [2009] is an unreleased SDI version. I added this release cos of an interview with Paul Norman." Music files converted automatically.

### V2.1 (CSDb #132363, January 2013)
Code: 6R6 + GT. "Entry restored for archival purpose only. newer version SID Duzz' It V2.1.6."  
Downloads: main archive + `SDI21-keys.txt` + `SDI21-notetables.txt`.

### V2.1.6 (CSDb #114693, May 2013)
Code: 6R6 + GT. Download: `csdb.dk/getinternalfile.php/N/Sid_Duzz_It_v2.1.6-shape.zip` (CSDb 503 on fetch).  
Feature set (from vintageisthenewold.com): sequencer + tracker + sound editor + vibrato + pulse + filter + arpeggio + tempo + keyboard-tracking + tempo-programs/funktempo + gateoff-table-pointers + filter-shift + SID-export + executable-export + MIDI/XM conversion + MIDI-input hardware.

### V2.1.7 (CSDb #133692, 12 October 2014) — CURRENT STABLE
Code: 6R6 (Nostalgia, SHAPE) + GT (Maniacs of Noise, SHAPE).  
Download: `csdb.dk/getinternalfile.php/133177/Sid_Duzz_It_v2.1.7-shape.zip` (96.4 kB, 1974 downloads).

**Release notes (from `sdi217_releasenotes.txt` inside zip):**
> SDI v2.1.7 released today 12.10.2014  
> Fixed two bugs in the turbo assembler player sources:  
> * The filtercutoff routine was missing a small compare routine for fast downwards subtraction.  
>   This could result in difference in the sound output when compared to the editor.  
> * If you started your song with a gatetimeout setting of Ax, Cx or Ex the first note strike  
>   would sometimes not happen.  
> Greetings from GRG and GT of SHAPE.

**Zip contents:**
- `sdi217_editor.d64` — the editor disk
- `sdi217_bmtass.d64` — BM-Tass assembler disk (fastload; 1541/1571 only)
- `sdi217_seqsrc.d64` — Turbo Assembler player source disk with two SEQ files:
  - `SRC.SDI21-N50` (154 blocks) — singlespeed player source (PAL, loads at $1000 by default)
  - `SRC.SDI21-SPD50` (155 blocks) — multispeed player source
- `sdi217_releasenotes.txt` — quoted above

**User comments:**
- "An absolutely wonderful piece of software I can't do without" (Abynx, 2025)
- mstram (2015): V1.8 and V2.17 incompatible in VICE
- Bitbreaker (2014): criticises source code format / assembler limitations
- PAL (2015): "The tool was created for its developers; public access is supplementary"

---

## V3.0 MIDI Previews (Unreleased / Preview Only)

### MIDI Preview 1 (CSDb #118973, 2013)
### MIDI Preview 2 (CSDb #119228, 31 May 2013)

Code + design: 6R6 + GT.  
Downloads for Preview 2: `SDI-30-KEYS.txt` + `SDI-30.MIDI-Preview-2.zip`.

**V3.0 changes (6R6, 31 May 2013):** "Added some stuff. Removed some stuff and optimized some stuff." MIDI support tested successfully with Steinberg Research / Sequential Circuits interfaces on real C64. VICE has MIDI delay (20ms buffer). Key feature: MIDI input hardware support (responsive on real hardware).

Community quote (Stainless Steel): "I've stuck with SDI for the past 8 years and I'm thrilled to see this."

**V3.0 is not publicly released** — exists only as MIDI previews. No stable V3.0 on CSDb.

---

## SDI V2.07 Player ADSR Fixed (CSDb #114644, January 2013)

Bug-fix patch by SIDWAVE applied to the V2.07 player source.  
**Bug:** "attack values giving no sound under certain conditions, but there was more."  
Impact varies by tune — some tunes show no problem, others clearly exhibit the flaw.  
Code remains credited to 6R6 + GT; SIDWAVE only applied the fix.  
This is effectively the player that was later integrated into V2.1/V2.1.6/V2.1.7.

---

## Pouet Entry

`https://www.pouet.net/prod.php?which=59065` — "SID Duzz' It v2.0 by SHAPE", 2009.  
Type: Demotool. Code: 6R6. Popularity: 53%.  
Community notes: requests for expanded tracker support and MIDI (pre-V3.0 preview).  
No additional technical detail beyond CSDb.

---

## SourceForge Project

URL: `https://sourceforge.net/projects/sidduzzit/`  
Maintained by: Glenn RG64 (Glenn Rune Gallefoss)  
Last update: November 7, 2014 (V2.1.7 era)

Available files (SourceForge file listing, not directly downloadable):
- `SDI.2.1.6-docs.txt` (64.9 kB) — official text docs from V2.1.6
- `SDI.2.1.6-note_tables.txt` (3.3 kB) — note tables reference
- `sdi217_releasenotes_README.txt` (477 bytes) — V2.1.7 bugfix notes (same as in zip)
- `Sid_Duzz_It_v2.1.7-shape.zip` (96.4 kB) — full release

Note: SourceForge blocks direct downloads from scripts (GDPR/cookie wall). Content of
`SDI.2.1.6-docs.txt` is the basis for the Psylicium PDF manual (csdb_manual.md).

---

## HVSC Coverage

~934 SID files in HVSC #84 use the SDI engine. HVSC path: `MUSICIANS/` various.
The engine is classified as "SID Duzz' It" by sidid.

---

## Key Technical Points (from CSDb community comments + release notes)

1. **Player is modular**: all effects are compile-time flags (`rem_*`). Default player has most effects OFF (rem_pu=1, rem_wfd=1, rem_adsr=1, rem_mp=1, etc.). A tune must enable only the effects it uses.

2. **Two player types ship with V2.1.7**:
   - `SDI21-N50` — singlespeed (normal VBI-driven; fires once per PAL frame)
   - `SDI21-SPD50` — multispeed (CIA-timed; PAL raster = 312/speed, NTSC = 262/speed)
   Entry points: $1000=INIT, $1003=PLAY, $1006=FADEOUT, $1009=SPEEDPLAY.

3. **V2.1.7 player source is in Turbo Assembler format** (SEQ files on D64). 64tass conversion mentioned in Psylicium manual.

4. **V1.x ↔ V2.x incompatibility confirmed** by user (mstram, 2015): V1.8 and V2.17 files not interchangeable in VICE.

5. **ADSR bug in V2.0 Beta 8 player** fixed by SIDWAVE (CSDb #114644, Jan 2013) and presumably integrated into V2.1+.

6. **V2.1.7 player bug fixes** (from release notes): (a) filtercutoff missing compare for fast downwards subtraction; (b) gatetimeout $Ax/$Cx/$Ex causing missed first note strike.

7. **SID mirror banks**: `sid = $D400` (default). $D5C0 also works. C128: only $D400-$D500.

8. **Glide implementation**: two types — "hard restart glide" and "tie glide". FX range $21-$3F in sequencer. Glide speed = FX value - $20.

9. **Multispeed dispatch**: main PLAY call updates tracks + sequences + sounds; SPEEDPLAY call ($1009) does sound-only updates. For speed=4: 1× PLAY + 3× SPEEDPLAY per VBI.

10. **Filter model**: 11-bit filter possible via $F0-$F7 waveform command (sets lower 3 bits of $D415). Main filter cutoff through filter program (sets $D416). Band/resonance per instrument.
