---
source_url: https://discmaster.textfiles.com/view/5218/237.d81/t.sidsmith
         + https://discmaster.textfiles.com/view/5218/237.d81/t.smithsid
fetched_via: direct (discmaster.textfiles.com)
fetch_date: 2026-06-14
author: t.sidsmith: unattributed (documents program by Debby Cruz + Scott Resh)
        t.smithsid: unattributed (documents program by Doreen Horne)
content_date: 2004-01-01 (disk date for both)
reliability: primary
---

# Loadstar 237 — SIDSmith and SmithSID Documentation

Two converter programs on Loadstar 237 bridge SongSmith ↔ Compute's SID Player format.
These documentation files are the BEST publicly available description of the SongSmith
file format from a community source.

---

## SIDSmith (SongSmith → SID Player)

**Program authors:** Debby Cruz and Scott Resh
**Original creation date:** 1988 (per SmithSID's docs)
**Direction:** SongSmith format → Compute's SID Player .mus format

### What SIDSmith Does

Converts music "quickly and easily entered in SONGSMITH" to "SID format for the
final touches" in SID EDITOR / SID PLAYER.

Motivations: SID Player has "thousands of SID musicians" and more powerful capabilities
(triplets, use of filtering) that SongSmith lacks.

### SongSmith File Format (Input)
- Music data: files with **"m."** prefix (e.g., m.mysong)
- Waveform/ADSR data: files with **"w."** prefix (e.g., w.mysong)

### SID Player File Format (Output)
- Files with **".mus"** suffix
- Compatible with SID EDITOR and SID PLAYER (Craig Chamberlain's system)

### Conversion Options
The converter supports:
- Measure marker inclusion/exclusion
- Credit preservation
- Key signature transposition
- Tempo selection

### Performance
- Processing runs at "ML speeds" (machine language, fast)

---

## SmithSID (SID Player → SongSmith)

**Program author:** Doreen Horne
**Direction:** Compute's SID Player .mus format → SongSmith format

### What SmithSID Does

"Accomplishes the impossible: it will convert sophisticated SID songs into simple
SONGSMITH songs."

Use case: Access the large online library of .mus files within SongSmith's
simpler/more accessible editor.

### Input Format
- SID music files ending in ".mus" (Compute's SID Player / Enhanced Sidplayer format)

### Output Format
- SongSmith format files:
  - Music data: files beginning with **"m."**
  - Instrument data: files beginning with **"w."**
    - The w. file: exactly **1 block** (254 usable bytes)
    - Content: **ADSR values and timbre information** (waveform settings)

### Performance
- Users with SuperCPU experience faster conversion
- Standard C64: up to 1 minute per medium-sized file

### Quality Limitation
"The converted music may sound degraded compared to original SID versions,
especially if there are a lot of enhanced sounds in the original SID file."

After conversion, users can refine in SongSmith's editor.

### Historical Note
SmithSID is described as the "reverse counterpart to SIDSMITH (created by Scott
Resh and Debbie Cruz in 1988)."

---

## Implications for Format Analysis

### File Naming Convention Confirmed:
- SongSmith music file: **m.SONGNAME** (notes/melody data)
- SongSmith instrument file: **w.SONGNAME** (ADSR + waveform, 1 disk block)
- Both files required together to play a SongSmith song

### What the w. file contains:
Per SmithSID output specification:
- **ADSR values**: Attack/Decay/Sustain/Release for each of the 3 SID voices
  ($D405/$D406 per voice = 6 bytes for 3 voices; plus possibly 3×$D404 control bits)
- **Timbre information**: waveform selection (Triangle/Sawtooth/Pulse/Noise bits
  in $D404 bits 4–7 for each voice)
- Total: 1 disk block = 254 usable bytes

### What the m. file contains:
Not directly specified in documentation; inferred from:
1. Sidid signatures: note data is indexed by an integer (1-based), converted via
   (note-1)×2 for a word-table (freq-lo, freq-hi) lookup
2. Duration data: encoded as the W/H/Q/E/S key choices at entry time → stored as
   duration codes in the stream
3. Voice structure: 3-voice data, exact interleaving unknown
4. Measure boundaries: may be tracked in the editor but possibly not stored in file
   (inferred from "beats per voice" being editor-state)

### Relationship to .mus Format:
SIDSmith was originally written in 1988, making it contemporary with the Garrett/Gardner
precursor tool era. The SmithSID round-trip converter (plus quality degradation warning)
confirms SongSmith is a SUBSET of SID Player's expressive range:
- SongSmith LACKS: triplets, filtering, LFO, portamento, pulse sweep, ring/sync
- SongSmith HAS: notes (3 voices), durations (W/H/Q/E/S), ADSR per voice, waveform
  per voice, key signature, time signature, tempo

The SID Player .mus format specification is in:
`pipelines/loadstar_songsmith/docs/github_sidplayer_mus_format.md`
