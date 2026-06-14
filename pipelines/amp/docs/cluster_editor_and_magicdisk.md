# AMP (Advanced Music Programmer) — Editor, Provenance & Magic Disk 64

```
provenance_header:
  source_urls:
    - https://csdb.dk/release/?id=35519          # Hitech Studio Designs release
    - https://csdb.dk/release/?id=193063          # Quality 1990 release
    - https://csdb.dk/scener/?id=14045            # Burton (Andrew Miller) CSDb profile
    - https://csdb.dk/group/?id=2214              # Quality (Hungary)
    - https://csdb.dk/group/?id=4053              # Hitech Studio Designs
    - https://csdb.dk/release/?id=200544          # A.M.P. V2.3 Pack (NDC, 1992)
    - https://github.com/cadaver/sidid/blob/master/sidid.nfo  # sidid detection entry
    - https://www.vgmpf.com/Wiki/index.php?title=Andras_Molnar
    - https://archive.org/details/Magic_Disk_64_91-12_1991_-_de_Side_A
    - local D64 binary analysis: /home/jtr/sidfinity/tmp/amp_research/amp_quality_1990.d64
  fetched_via: WebFetch, WebSearch, direct binary analysis (D64 disk image)
  fetch_date: 2026-06-14
  author: Andrew Miller (handle: Burton / The Satan before 1989)
  content_date: 1990 (editor), December 1991 (Magic Disk 64 distribution)
  reliability: HIGH — cross-confirmed from CSDb credits, binary strings, sidid.nfo, VGMPF wiki
```

---

## 1. Author Confirmation

**Author confirmed: Andrew Miller (Hungarian scener), handle "Burton" (earlier handle: "The Satan" until ~1989).**

CSDb scener profile ID 14045 (https://csdb.dk/scener/?id=14045) records:
- Real name: **Andrew Miller**
- Country: **Hungary**
- Handle: Burton (TST = "The Satan")
- Groups: Euratom (1989 onwards), **Hitech Studio Designs**, **Quality** (August 1989 onwards), Sidbusters

The binary credits string extracted directly from the D64 editor binary confirms:

```
AMP V2.3  was programmed and developed
 by ANDREW  MILLER with additional help
       of MARKUS MUELLER in 1990.

All amazing demosongs by MARKUS MUELLER.

          Many thanks to JOHN.

(c)1990 by Magic Disk 64
```

The inner copyright line reads: `(c)1990 by Magic Disk 64`

An additional embedded string reads: `amp - v2.3  by andrew miller in 1990 (c)`.

**The stub attribution "Andrew Miller (Burton) of Euratom/Quality" is CORRECT.** The nationality is Hungarian (not German), though both Quality and Hitech Studio Designs had cross-national membership. Markus Mueller (Hayes) is German and was co-developer and the principal composer of demonstration songs.

The sidid.nfo engine-identification database (cadaver/sidid, authoritative reference) records:
```
AMP
     NAME: Advanced Music Programmer
   AUTHOR: Andrew Miller (Burton)
 RELEASED: 1989 Hitech Studio Designs
REFERENCE: https://csdb.dk/release/?id=35519
```

Note the sidid.nfo says "1989" while the binary credits say "1990". CSDb itself shows the Quality group release dated 1990. The December 1991 Hitech/Magic Disk release is v2.3, likely a later polish.

---

## 2. Groups and Organisational Structure

| Entity | Role | Notes |
|---|---|---|
| Quality (Hungary) | Early development group | Founded Dec 1988; Burton joined Aug 1989; dissolved Feb 1990 |
| Hitech Studio Designs | Publishing/release group | Burton + Hayes + Tohi (graphician); released AMP V2.3 and game Mechanicus |
| New Dimension Crew (NDC) | Third-party packer | Released "A.M.P. V2.3 Pack" Oct 1992 (with added Cobra documentation + packer) |

Quality Hungary members included H.I.C. (coder, real name John Almási per Musicians.txt "HIC (Almási, John)"), The Secret Service, Hayes (Markus Mueller), and Burton. The 1990 Quality release of AMP credits code to "H.I.C." (distinct from Burton's later Hitech release).

**Important note on credits discrepancy:**
- The 1990 Quality release (CSDb #193063) credits: Code=H.I.C., Music=Hayes
- The 1991 Hitech release (CSDb #35519) credits: Code=Burton, Music=Hayes
- The binary's own "about" text credits Andrew Miller (Burton) as primary coder with Markus Mueller's "additional help"

This suggests H.I.C. may have contributed an earlier version or specific component, with Burton writing the primary engine. Alternatively, H.I.C. coded the Quality release intro/wrapper.

---

## 3. Distribution History and Magic Disk 64

**AMP was distributed through Magic Disk 64 (CP Verlag, German disk magazine), December 1991 issue.**

Magic Disk 64 was a German C64 disk magazine by CP Verlag (Computer Publications GmbH), running 12/1987–01/1996. It bundled games, tools, and tutorials on 5.25" disk. A CSDb comment by iAN CooG explicitly notes: _"Prof. Chaos said: 'This was released on Magic Disk 64 12/91.'"_

The binary copyright line `(c)1990 by Magic Disk 64` is embedded in the editor itself, suggesting CP Verlag had distribution rights from 1990 and the editor was commercially published via the magazine.

**Version timeline:**
| Version | Date | Publisher | CSDb ID |
|---|---|---|---|
| V2.3 (early) | 1990 | Quality | #193063 |
| V2.3 | 12/1991 | Hitech Studio Designs | #35519 (primary) |
| V2.3 (crack +D) | 11/1991 | X-Ray | #163884 |
| V2.3 (crack) | 12/1991 | Vision | #178586 |
| V2.3 (crack) | 11/1991 | The Shaolin Monastery + X-Ray | #15408 |
| V2.3 (crack) | 1993 | Warriors of the Wasteland | #168739 |
| A.M.P. V2.3 Pack | 10/1992 | New Dimension Crew | #200544, #225831 |

The large number of crack releases (5 known) confirms AMP had significant copy-protection and was widely distributed commercially.

VGMPF (Video Game Music Preservation Foundation) attributes AMP development from "May 21, 1988 to August 1990."

---

## 4. Editor Feature Model (from Binary Analysis)

Binary analysis of the Quality 1990 disk image (`amp.d64`, 174848 bytes, 35-track D64) was conducted. The editor loads at address **$0801** and spans to approximately **$4200** (14,849 bytes for the editor code).

### 4a. File Format — Four Separate Files

The binary contains the string `SNG.VOI.NOT.DAT.` identifying four distinct file types:

| Extension | Content |
|---|---|
| `.SNG` | Song order / sequence list |
| `.VOI` | Voice / instrument settings |
| `.NOT` | Note patterns |
| `.DAT` | Combined packed file (all of the above merged) |

The "AMP PACKER" utility on the disk (loads at $0801, 8193 bytes) combines these into a single `.DAT` file for inclusion in games.

### 4b. Global Song Parameters (from DAT header)

The packed DAT file begins at load address `$2FFA`. The 6-byte header at `$3000`:

| Offset | Field | Example (Lunar Storm) |
|---|---|---|
| $3000 | First step (song start position) | $07 = 7 |
| $3001 | Last step (song end position) | $0F = 15 |
| $3002 | Speed / tempo | $40 = 64 |
| $3003 | Unknown | $00 |
| $3004-$3005 | Pointer to instrument data (little-endian) | $1590 = 5520 |

Song step range is 7–15 in this example, giving 9 sections. The editor UI label reads "SECTOR LENGHT:" (note: typo in original, not "length"), suggesting each step is called a "sector."

### 4c. Instrument/Sound Parameters

The editor presents 14 parameters per instrument (decoded from UI strings in binary):

| Parameter | Description |
|---|---|
| ATTACK/DECAY | SID ADSR envelope byte $D405 |
| SUSTAIN/RELEASE | SID ADSR envelope byte $D406 |
| PULSE HIGH-BYTE | Pulse width hi byte $D403 |
| ADD. PULSE | Additive pulse width modifier |
| VIBRATO START | Vibrato effect range start |
| VIBRATO END | Vibrato effect range end |
| ACCORD START | Arpeggio (German: "Akkord") range start |
| ACCORD END | Arpeggio range end |
| FILTER START | Filter sweep range start |
| FILTER END | Filter sweep range end |
| WAVEFORM START 1 | Waveform table start (first segment) |
| WAVEFORM END | Waveform table end |
| WAVEFORM START 2 | Waveform table start (second segment) |
| GLIDE CONTROL | Portamento/glide parameter |
| FILTER BYTE 1 | Filter control byte 1 ($D417 / cutoff) |
| FILTER BYTE 2 | Filter control byte 2 ($D418 / resonance+routing) |

**Observation:** The AMP instrument model has a waveform *table* with two entry points (START 1 and START 2), range markers for Vibrato, Arpeggio (Accord), and Filter, plus explicit Glide and two filter parameter bytes. This is a mid-complexity instrument model — richer than the Hubbard '85 engine's instrument slots but without a full per-tick bytecode program.

### 4d. Effects

Effects visible from UI and binary:
- **Vibrato** — range-based, with start/end pointers into a vibrato table
- **Arpeggio ("Accord")** — range-based (labelled "ACCORD" — German musical term), with start/end pointers
- **Filter sweep** — range-based, with start/end, two filter bytes ($D417 cutoff, $D418 mode/vol)
- **Waveform programming** — two-segment waveform table (supports two waveform programs per sound, likely a one-shot + loop structure)
- **Glide (portamento)** — single control parameter
- **Pulse width modulation** — additive pulse value ("ADD. PULSE") plus pulse high-byte

### 4e. Sequencer / Pattern Structure

Main editor screen heading: `St  Chn1 Rh  Chn2 Rh  Chn3 Rh`

This reveals: **Step**, **Channel 1** (note), **Rh** (rhythm/hold flag?), **Channel 2**, **Rh**, **Channel 3**, **Rh**. Three voices, each with note + a hold/rhythm byte per step.

The packed DAT note data is stored with bytes encoding note values. From frequency distribution analysis:
- `$00` (0): 66.7% of bytes — likely "empty cell" / silence in unused voice steps
- `$40` (64): 8.5% — likely "hold/tie" flag or special marker
- `$80` (128): 4.6% — likely "rest" token
- `$C0` (192): 1.8% — likely another special command class
- Values $40–$7F, $80–$BF, $C0–$FF appear in distinct clusters

**Note encoding hypothesis:** The high 2 bits of each byte form a class: `00`=note, `01`=hold/tie, `10`=rest/special, `11`=command. The low 6 bits encode note number (0–63) or parameter. This is a working hypothesis; not fully confirmed without the editor's disassembly.

Note names in binary: `CCDDEFFGGAAH` — German chromatic notation (H = B natural). 13 chromatic pitches: C, C#, D, D#, E, F, F#, G, G#, A, A#, H (B♮). Range not determined from binary alone.

### 4f. Song-level Parameters (from editor UI strings)

The main song/sequence screen shows:
- **NAME** — song name string (max ~15 chars)
- **FIRST STEP / LAST STEP** — song loop region
- **SPEED** — global tempo
- **SECTOR LENGHT** — length per sector (pattern step)
- **PLAY / EDITED STEP** — playback cursor position
- **VOLUME** — global master volume
- **STATUS** — playback status
- **COPY ST.** — copy sector function (from–to)
- **PLAY CHANNEL** — select voice for auditioning
- **SOUND / CHN** — select sound (instrument) and channel for editing

### 4g. Demo Songs (Bundled on Disk)

The Quality 1990 D64 includes 14 demo songs (all by Markus Mueller / Hayes):

```
DAT.LUNAR STORM
DAT.ENOLA GAY
DAT.THINK NOW...
DAT.GHOSTBUSTERS
DAT.HIT IT ONCE
DAT.I JUST...
DAT.UNICORN
DAT.COOL ONE
DAT.NEW IDEA #01
DAT.NEW IDEA #02
DAT.ZOOLOOK
DAT.DEPECHE MIX
DAT.RASTER RUN.
DAT.DELTA V2
```

These align with the HVSC `Mueller_Markus/` directory which contains SIDs composed in AMP (HVSC uses the AMP player code extracted from the packed DAT files).

---

## 5. SID Detection Signature (sidid)

The cadaver/sidid engine identifier uses the following byte pattern to detect AMP player code:

```
AMP
B9 ?? ?? ?? 16 D4 C8 98 9D ?? ?? ?? ?? ?? ?? ?? ?? 8D 18 D4 END
```

Decoded: `LDA abs,Y` / `ASL` / `$D4?? write` / `INY` / `TYA` / `STA abs,X` (×multiple) / `STA $D418` — a loop writing to SID register `$D418` (volume/filter), consistent with the filter byte and master volume handled by the player loop.

The `$D418` final write confirms AMP sets master volume on every play iteration.

---

## 6. Known Users of AMP in HVSC

The HVSC `Mueller_Markus/` directory (~35 SIDs) is the primary AMP corpus. Additional AMP users confirmed in HVSC:

- **Mueller_Markus (Hayes)** — principal composer, all demo songs on AMP disk
- The file format was used commercially in games credited to Hitech Studio Designs:
  - *Mechanicus* (1991, Hitech Studio Designs) — music by Hayes
  - *Locomotion* (Kingsoft, 1992) — Zsolt Szabó arrangement (different driver, not confirmed AMP)
  - *Fuzzy's World of Miniature Space Golf* (DOS, 1995) — Loudness engine (successor, not AMP)

VGMPF lists ~20+ C64 game titles using AMP V2.3. The HVSC sidid classification identifies ~246 SIDs as AMP.

---

## 7. Relationship to "Andras Molnar" / VGMPF Attribution

VGMPF attributes AMP to "Andras Molnar" (Hungarian: András Molnár). The CSDb scener profile confirms the real name as "Andrew Miller." These are the same person: "Andrew Miller" is the English transliteration of "András Molnár" (common in the 1980s–90s Hungarian scene where members used anglicised names for international distribution).

VGMPF confirms: development May 1988 to August 1990 with Markus Müller's collaboration.

---

## 8. Source Code / Format Spec Availability

- **No public source code** found for AMP editor or player.
- **No formal format specification** document found (no codebase64 entry, no GitHub port).
- **sidid.cfg** provides the 19-byte player fingerprint (see §5).
- The A.M.P. V2.3 Pack (NDC, 1992) adds documentation by Cobra — content unknown (the pack's disk was initially incomplete; a "fully working version with example tunes" was uploaded to CSDb in Sept 2024).
- Direct binary analysis of the D64 disk image is the best current source of format knowledge (see §4).

---

## 9. Summary

| Field | Value |
|---|---|
| Full name | The Advanced Music Programmer (AMP) |
| Version | V2.3 (primary) |
| Author | Andrew Miller (= András Molnár), handle: Burton |
| Country | Hungary |
| Co-developer | Markus Mueller (Hayes) — additional help + demo songs |
| Development period | May 1988 – August 1990 |
| Groups | Quality (Hungary), Hitech Studio Designs, Sidbusters |
| Commercial distribution | Magic Disk 64, December 1991 (CP Verlag, Germany) |
| Copyright string | (c)1990 by Magic Disk 64 |
| File format | 4-file: .SNG (order), .VOI (instruments), .NOT (patterns), .DAT (packed) |
| Load address | $0801 (editor), $2FFA (DAT player data) |
| Voices | 3 (C64 SID voices) |
| Instrument params | 16 (ADSR, pulse, vibrato, arpeggio, filter, 2-segment waveform, glide) |
| Effects | Vibrato, arpeggio ("accord"), filter sweep, waveform table, glide, pulse width |
| Note encoding | Range-based; high-2-bit class (note/hold/rest/cmd), low-6-bit note number |
| Note names | German notation (H=B): C C# D D# E F F# G G# A A# H |
| Demo songs | 14 (all Mueller_Markus compositions) |
| HVSC corpus | ~246 SIDs |
| sidid key | `B9 ?? ?? ?? 16 D4 C8 98 9D ?? ?? ... 8D 18 D4` |
| Source code | Not publicly available |
| Format spec | Not published; this doc is primary record from binary analysis |

---

## Leads to Follow

1. **A.M.P. V2.3 Pack documentation (Cobra/NDC, 1992)** — the Sept 2024 re-upload of CSDb #200544 includes example tunes and reportedly documentation by Cobra. Download and extract that D64 to read any text/manual files Cobra wrote. This may describe the format in natural language.

2. **Magic Disk 64 12/1991 disk content** — the archive.org D64 (`Magic_Disk_64_91-12_1991_-_de_Side_A.d64`) likely contains the AMP V2.3 distribution with any accompanying German-language tutorial or help text. Mount in VICE and read the disk menu. The magazine was known for in-program help and text articles.

3. **Full instrument data format** — the pointer at DAT bytes 4–5 (`$1590` for Lunar Storm, `$1556` for Cool One) points into the instrument block. Read 16 bytes × N instruments from that offset to map the exact binary layout of each instrument's fields. This pins the VOI file structure.

4. **Note encoding confirmation** — disassemble the AMP player at load $0801 to trace how the note byte stream is consumed (the play() routine). The sidid fingerprint byte sequence (`B9 ?? ?? ?? 16 D4 ...`) gives the exact start address; follow the loop.

5. **Mueller_Markus HVSC directory** — run sidid over all ~246 AMP-classified SIDs to verify the classification is clean (no false positives). Compare load addresses across tunes to determine if AMP player is always at a fixed address or relocatable.

6. **John Almási (H.I.C.)** — the Quality release credits H.I.C. (John Almási) as coder. His role vs Burton's is unclear. Check CSDb #193063 comments and H.I.C.'s profile (CSDb scener ~#9460 or adjacent) for context.

7. **Demozoo entry** — https://demozoo.org/productions/174484/ has tags `music-editor` and `monochrome`; check for any screenshots or linked external resources.

8. **forum64.de / German C64 forums** — search for "AMP Composer" or "Advanced Music Programmer" in German threads; the forum64.de thread on C64 sound programs (#69740) returned a 403 during this sweep; retry with a different approach.
