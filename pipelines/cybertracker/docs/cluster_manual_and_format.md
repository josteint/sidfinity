# CyberTracker — Manual & Format Research Cluster

## Provenance

| Field           | Value |
|-----------------|-------|
| source_url      | http://noname.c64.org/tracker/manual_online.php (primary); http://noname.c64.org/tracker/ (main); https://csdb.dk/release/?id=2601 (V1.00); https://csdb.dk/release/?id=25 (V1.01) |
| fetched_via     | WebFetch (live site, multiple passes); WebSearch (CSDb, pouet.net, sidid.nfo, chipmusic.org) |
| fetch_date      | 2026-06-14 |
| author          | Bjarke Nørgaard Laustsen ("CyberBrain"), No Name group, Denmark |
| content_date    | 2001 (V1.00 released 13 April 2001 at Mekka & Symposium 2001; V1.01 released 14 September 2001) |
| reliability     | HIGH — primary source (noname.c64.org) is live and consistent across multiple fetch passes |

Full fetched manual text: `docs/src/manual_online_fetched.md`

---

## 1. Software Overview

CyberTracker is a native Commodore 64 music tracker in the FastTracker/ProTracker style,
written in C by CyberBrain (Bjarke Nørgaard Laustsen) of the No Name group (Denmark).
Released 2001. The main innovation is an 8-envelope graphical instrument editor.

**CSDb entries:**
- V1.00: https://csdb.dk/release/?id=2601 (released at Mekka & Symposium 2001)
- V1.01: https://csdb.dk/release/?id=25 (September 2001)
- Packer BETA#1: https://csdb.dk/release/?id=4085 (March 2002; co-coded Ghostrider/No Name)
- Executable Maker V1.00: December 2001
- Executable Maker V1.01: released later

**SIDID identification** (cadaver/sidid.nfo):
- `CyberTracker` — Bjarke Nørgaard Laustsen (CyberBrain); CSDb #2601
- `CyberTracker_exe` — tunes created with the CyberTracker Executable Maker; CSDb #6663
- `Cyberbrain_Digi` — separate digi player by same author

**HVSC #84 corpus** (from hvsc84.db):
| Engine            | SID count |
|-------------------|-----------|
| CyberTracker      | 125       |
| CyberTracker_exe  | 130       |
| Cyberbrain_Digi   | 6         |
| **Total**         | **261**   |

**CyberTracker composers in HVSC (sampled):** Akira_K, Cyberbrain, Fredrik, Fritske, Johnny_Owl,
King_Durin, Latvamaeki_Aki, Mis, Morton_Adam, Odo, Pater_Pi, Pingo, Rolemusic, Sgw32, TheK,
TSM, Vintaque, Xonic_the_Fox, and ~18 others.

**Note:** The user-stated count "~255 HVSC tunes" roughly matches the 261 found in HVSC #84
(125 + 130 + 6 = 261). The split CyberTracker / CyberTracker_exe is a SIDID classification
of packed vs non-packed output.

---

## 2. Tools Ecosystem

### CyberTracker V1.00 / V1.01 (native C64 tracker)
- Download: `noname.c64.org/download.php/cybertracker1_01-d64.zip` (d64 disk image, ~185 KB)
- Also available on commodore.software and CSDb
- V1.01 is 100% backward compatible with V1.00 files

### CyberTracker Packer BETA#1 (WIN/DOS)
- Released March 2002; Windows/DOS executable
- Converts CyberTracker song + player into a standalone C64 SID/PRG
- Download: `noname.c64.org/download.php/ct_packer_beta1_(win+dos).zip` (1,502 downloads)
- Code: CyberBrain + Ghostrider/No Name

### CyberTracker Executable Maker V1.00/V1.01 (native C64)
- Released December 2001
- Produces standalone C64 executables from CT tunes
- Used in HVSC `CyberTracker_exe` engine classification

### Instrument Disk
- Released July 2001; categorised: bassdrum, snaredrum, keys, basses, backing, percussion, misc
- Created by CyberBrain and Kilroy/No Name

---

## 3. Complete Data Model

### 3.1 Pattern Format

Each pattern line contains three channels, laid out as:
```
'--- 00000 --- 00000 --- 00000'
```

Per channel (one segment):
```
NOTE(3)  INSTRUMENT(2 hex)  EFFECT(3 hex)
```

**Note field (3 chars):**
- Normal note: `C-4`, `C#5`, `D-3`, ... `B-7` (note-name + octave)
- `---` = no note / empty
- `.`  = gate note — triggers the sustain-line in the volume envelope (release phase)
- `,`  = stop note — immediately silences the channel

**Instrument field (2 hex chars, `00`–`1F`):**
- `00` = use last-used instrument (does NOT reset to instrument 0)
- `01`–`1F` = instruments 1–31

**Effect field (3 hex chars):**
- Format: `XYZ` where X = effect number (1 hex digit), YZ = parameter (2 hex digits)
- Exception: `Eyx` — effect code is 2 digits (E + y), parameter is 1 digit (x)
- CyberTracker supports **more than one pattern effect per line** via the `Dxx` multi-effect
  jump (manual calls this "worlds first!!")

**Pattern constraints:**
- Max lines per pattern: **128** ($80)
- Max patterns: **256** ($00–$FF)
- Total shared pattern memory: **796 lines** ($31C)

### 3.2 Track / Orderlist Format

- The track editor has two columns: line-number (auto, read-only) and pattern-number
- Each line references one pattern by its number ($00–$FF)
- Max lines per song (track): **255**
- Total track memory (shared across all songs): **512 lines** ($200)
- Loop/restart: set with `R` key at any track line
- Multiple songs per file — all share the same patterns + instruments; only the orderlist differs

### 3.3 Instrument Model

**Count:** 31 instruments ($01–$1F). Instrument 0 = "last used."

Each instrument contains:
1. **8 graphical envelopes** (see 3.4)
2. **Vibrato parameters** (speed + depth)
3. **Arpeggio parameters** (2 halftone intervals)
4. **Name** (ASCII, edited in Instrument Name Editor)

Max instrument duration: **65,536 ticks** (~21.84 minutes at 50 Hz PAL)

Total shared envelope memory: **768 points** ($300), shared across all envelopes of all instruments.

### 3.4 The 8 Envelopes

General mechanics:
- X-axis = time (rightward = later in ticks)
- Y-axis = value (specific meaning per envelope type)
- Envelope holds its last value when exhausted (no-loop case)
- Loop: toggle with `L`; loop-start point set with Lshift+`S`
- Sustain gate: vertical dotted line boundary; player halts here until gate-note `.` in pattern
- "Only the points themselves matter" = applies to step envelopes (waveform, filterpass, pitchcontrol)
  where interpolation between points is irrelevant

| # | Name            | Y-axis range        | Interpolated? | Notes |
|---|-----------------|---------------------|---------------|-------|
| 1 | Volume          | 0–$0F               | Yes           | First 4 pts = A/D/S/R (locked x-pos, 16 values); sustain gate line |
| 2 | Waveform        | SID waveform bits   | No (step)     | TRI/SAW/PUL/NOI; only point values matter |
| 3 | Pulse Width     | $000–$FFF           | Yes           | $800 = 50%; pulse waveform only |
| 4 | Filter Pass     | 0–7 (bit field)     | No (step)     | 0=lowpass,1=bandpass,2=highpass,3=voice3off; $0=no filter |
| 5 | Cutoff          | 0–$7FF (11-bit)     | Yes           | Filter cutoff frequency |
| 6 | Resonance       | 0–$0F               | Yes           | Filter resonance |
| 7 | Pitch           | $0000–$FFFF         | Yes           | $8000=normal; >$8000=higher; <$8000=lower |
| 8 | Pitch Control   | $0 or $1            | No (step)     | $0=relative; $1=absolute (sent direct to SID, note ignored) |

### 3.5 Vibrato / Arpeggio Block

Per instrument (separate from the 8 envelopes):

**Vibrato:**
- Speed: 1 byte; >$F0 recommended ("higher = faster")
- Depth: 1 byte; $00 = vibrato off; higher = more modulation

**Arpeggio:**
- Two halftone intervals (x and y), each 1 byte
- Creates pseudo-chord: cycles base-note → base+x → base+y → base+x → ...
- Active until new note

### 3.6 Filter Architecture

- ONE filter for ALL 3 channels simultaneously
- Filter passband, cutoff, and resonance cannot differ per channel
- If multiple channels write conflicting filter values: **lowest channel number wins**
- Channel filter routing: each channel can be filtered or not (E0x per channel)

### 3.7 Multi-Effect Table

- **255 usable lines** ($01–$FF; line $00 not used)
- Same format as pattern effects (3 hex digits per line)
- `Dxx` in pattern jumps to line xx, executes sequentially until END marker
- END: press `E` in command column during editing
- `D00` = reuse last effect parameter (does NOT jump to line 00)
- Enables chaining multiple effects on a single pattern line (the unique CT feature)

---

## 4. Complete Effect Reference

Format: `X` (1 hex digit, effect number) + `YZ` (2 hex digits, parameter)
Except `Eyx` commands: 2-digit code + 1-digit parameter.

| Code | Name                  | Syntax         | Description |
|------|-----------------------|----------------|-------------|
| 0xy  | Arpeggio              | 0 + ht1 + ht2  | Cycles base/base+x/base+y halftones. `0FF`=off. Continues until new note. |
| 1xx  | Portamento Up         | 1 + speed      | Pitch slides up per tick. `00`=reuse last. |
| 2xx  | Portamento Down       | 2 + speed      | Pitch slides down per tick. `00`=reuse last. |
| 3xx  | Tone Portamento       | 3 + speed      | Slides toward target note. No hardrestart. Envelope does NOT restart. |
| 4xx  | Vibrato               | 4 + spd + dep  | Vibrato. `00`=disable. Continues until new note. |
| 5xx  | Cutoff-Add Slide Up   | 5 + speed      | Increases cutoff add-value per tick. Persists until reset (`780`). |
| 6xx  | Cutoff-Add Slide Down | 6 + speed      | Decreases cutoff add-value per tick. |
| 7xx  | Set Cutoff-Add        | 7 + value      | $80=none; >$80=add; <$80=subtract from cutoff. |
| Axx  | PW Slide Up           | A + speed      | Increases pulse width per tick. `00`=reuse last. |
| Bxx  | PW Slide Down         | B + speed      | Decreases pulse width per tick. `00`=reuse last. |
| Cxx  | Set Sustain           | C + (0/1) + vol| C0x=stop envelope+hold vol; C1x=resume envelope. Max vol $0F. |
| Dxx  | Multi-Effect Jump     | D + line       | Jump to multi-effect table line xx, execute until END. D00=reuse last param. |
| E0x  | Filter Toggle         | E0 + (0/1)     | 0=filter off on channel; 1=filter on. |
| E1x  | Set Attack            | E1 + value     | Override ADSR attack ($0–$F). |
| E2x  | Set Decay             | E2 + value     | Override ADSR decay ($0–$F). |
| E3x  | Set Release           | E3 + value     | Override ADSR release ($0–$F). |
| E4x  | Set Waveform          | E4 + bits      | Bits: 0=tri,1=saw,2=pul,3=noi. "Avoid >8 (noise lockup)." |
| E7x  | Set Resonance         | E7 + value     | All channels. Overrides resonance envelope. $0–$F. |
| E8x  | Test/Sync/Ring/Gate   | E8 + bits      | SID control reg low nybble: bit0=gate,1=sync,2=ring,3=test. |
| E9x  | Filter Passband       | E9 + bits      | 0=LP,1=BP,2=HP,3=v3off. >8=disable voice 3. |
| ECx  | Global Volume         | EC + vol       | Master volume $0–$F. Default $F. |
| EDx  | Pattern Break         | ED + x         | Stop pattern after current line (param ignored). |
| EEx  | Skip Hardrestart      | EE + (0/1)     | Must accompany a note. 1=skip hardrestart; else=normal. |
| Fxx  | Set Speed             | F + speed      | Ticks per line. F00=stop. Speeds <3 = hardrestart issues. |

**Note:** Effects 8, 9 are not mentioned (gap in published list).

---

## 5. Tempo System

- Speed = ticks per pattern line (set by Fxx)
- 1 tick = 1/50 s (PAL) or 1/60 s (NTSC)
- Default BPM ~125 PAL at default speed
- Swing: alternate different Fxx values on consecutive lines
- Hard restart: standard SID technique (gate+test bit trick); credited to JCH/Vibrants docs

---

## 6. Memory Layout Summary

| Resource             | Limit        | Hex   |
|----------------------|--------------|-------|
| Pattern lines        | 796          | $31C  |
| Track lines          | 512          | $200  |
| Envelope points      | 768          | $300  |
| Instruments          | 31           | $1F   |
| Multi-effect lines   | 255          | $FF   |
| Patterns             | 256          | $100  |
| Max lines/pattern    | 128          | $80   |
| Max inst. duration   | 65,536 ticks | 21.84 min |
| Note octave range    | 0–7          | (B-7 out of SID range) |

---

## 7. File Format — Known & Unknown

### What is known from the manual
- V1.01 files are forward-incompatible with V1.00 player (0.3% success loading new files in old)
- V1.00 files load fine in V1.01 (100% backward compat)
- Song files contain: patterns + instruments + track/orderlist + multi-effect table + song-names
- Instrument files (.ci) can be saved/loaded independently

### File format guide (SEPARATE DOCUMENT — NOT captured in this sweep)
The manual.php page lists:
- "Download the CyberTracker version 1.01 fileformat guide (fixed version)" — `ct_v101_fileformat_fixed.zip`
- "Download the CyberTracker version 1.00/1.01 quick effect reference"

These are **ZIP downloads** from noname.c64.org. The fixed fileformat guide is dated 13/11/2001.
WebFetch to `noname.c64.org/download.php/ct_v101_fileformat_fixed.zip` returned empty content
(likely a binary ZIP that WebFetch cannot read). The Word document inside that ZIP contains
the actual binary offset map for .ct and .ci files.

**The Just Solve File Format wiki** confirmed the fileformat document exists but was ECONNREFUSED
when fetched. Its Wikidata entry is: https://www.wikidata.org/wiki/Q27967130

### CyberTracker_exe vs CyberTracker (SIDID distinction)
- `CyberTracker` = tunes where the CyberTracker player routine is embedded as a PSID
- `CyberTracker_exe` = tunes produced via the Executable Maker (packed, self-contained C64 exe)
- Both play identically (same player); different packaging method

### Cyberbrain_Digi
- Separate player by same author (6 SIDs in HVSC #84, all in Cyberbrain's folder)
- SIDs: Voodoo_People_part_{1,2,3}, Sverige, Holy_Maling, Hardware_Accelerated_Samples
- Likely a digi (sample playback) player; no public format docs found

---

## 8. Author & Group

**CyberBrain (Bjarke Nørgaard Laustsen):**
- Group: No Name, Denmark
- Website: noname.c64.org
- Also authored: Cyberbrain_Digi player
- HVSC composer folder: `MUSICIANS/C/Cyberbrain/` (16 SIDs, mix of CyberTracker + Cyberbrain_Digi)
- Musicians.txt entry: "Cyberbrain (Laustsen, Bjarke Norgaard) / Noname - DENMARK"

**No Name group:**
- Website: noname.c64.org (live as of 2026-06-14)
- Members credited: CyberBrain (code), Ghostrider (packer co-code), Kilroy (instruments)

---

## 9. Community Reception

- Praised for ProTracker/FastTracker familiarity; good for PC/Amiga tracker users transitioning to C64
- Criticized for "clicky sounds" (hardrestart technique; noted on VICE and real hardware)
- Instrument editor praised for graphical approach; commented as slow for sound design
- Player code received mixed reviews on pouet.net
- CSDb V1.01 quote: "one of the most friendly editors available"

---

## Leads to Follow

1. **Binary fileformat guide** — `noname.c64.org/download.php/ct_v101_fileformat_fixed.zip` is the
   primary artifact. Contains binary offset map for .ct (song) and .ci (instrument) files.
   WebFetch cannot read it (ZIP binary). Next step: download with curl or wget to tmp/, extract
   the .doc/.txt, read it. This is the single most important missing piece.

2. **Just Solve wiki pages** were ECONNREFUSED: `justsolve.archiveteam.org/wiki/CyberTracker_instrument`
   and `CyberTracker_module`. These may have partial binary format from a prior researcher.
   Try again or try Wayback Machine (web.archive.org was also blocked in this session).

3. **chipmusic.org forum thread** (#12725 "C64 Data Methods Cybertracker") was HTTP 403.
   This thread may contain user-researched binary format data. Try a different user-agent or
   the Wayback Machine snapshot.

4. **Cyberbrain_Digi format** — no documentation found. 6 SIDs in HVSC. SIDID has a signature
   for it but cadaver/sidid.nfo gives no format details. Would require binary RE of the SIDs
   in `hvsc85/MUSICIANS/C/Cyberbrain/`.

5. **CyberTracker Packer** (WIN/DOS binary, March 2002) — describes the output SID layout.
   Download `ct_packer_beta1_(win+dos).zip` and inspect it for any bundled docs or reverse-engineer
   the output format. The packer is relevant for understanding CyberTracker_exe SID structure.

6. **Effect gaps** — effects 8xx and 9xx are absent from the published effect list. Confirm
   these are truly unassigned in V1.01 or look for them in the binary fileformat guide.

7. **Getting Started guide** — listed on manual.php as a separate download; content unknown.

8. **Word document manuals** — two .doc downloads (V1.00 and V1.01) exist. May contain diagrams
   or byte layouts not in the online manual. Fetch via curl → extract text.

9. **Envelope point binary encoding** — the online manual describes the graphical model but not
   how points are encoded on disk (x-coord = ticks? absolute? delta-encoded? how many bytes per
   point?). The fileformat guide (#1 above) is the answer.

10. **Waveform envelope bit encoding** — "TRIangle, SAWtooth, PULse, NoiSE" = SID register bits
    at $D404/$D40B/$D412. The exact mapping (tri=1, saw=2, pul=4, noi=8 for the upper nibble of
    the waveform control register) is not stated in the manual — confirm from fileformat guide or
    binary inspection.
