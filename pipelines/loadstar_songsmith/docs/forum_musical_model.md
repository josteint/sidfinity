---
source_url: multiple (see per-section headers)
fetched_via: WebSearch + WebFetch
fetch_date: 2026-06-14
author: research session (Claude Code)
content_date: 2026-06-14
reliability: secondary (synthesized from primary sources in docs/src/)
---

# Loadstar SongSmith — Musical Model (Community/Forum Research)

## Summary

SongSmith is a **traditional-notation C64 music editor** (not a tracker). It uses
**3 SID voices**, note entry via keyboard (W/H/Q/E/S for duration), and supports
key/time signature and tempo. Song data is split across two file types: **m. prefix**
(melody/notes) and **w. prefix** (waveform/ADSR, 1 block). SIDSmith proves the
conversion to Compute's SID Player .mus format is feasible, meaning SongSmith's
musical model is comparable in power to .mus (note+duration+ADSR+waveform) but
simpler to enter.

---

## Primary Source: t.songsmith Documentation (Loadstar 237, 2004)

**Source URL:** https://discmaster.textfiles.com/view/5218/237.d81/t.songsmith
**File:** t.songsmith, 79 lines, 2.1 KB, dated 2004-01-01, in Loadstar 237 (237.d81)
**Author:** Dave Moorman (documentation); Joe Garrett (program)
**reliability:** primary

### Musical Model Confirmed by Documentation:

**Voices:** 3 SID voices — selected with keys **1**, **2**, **3**

**Note Duration Entry (keys):**
- **W** = Whole note
- **H** = Half note
- **Q** = Quarter note
- **E** = Eighth note
- **S** = Sixteenth (or smaller; key S)
- **D** = Dot modifier (dotted note)
- **R** = Rest

**Song Parameters (set from Main Menu):**
- **<K>** = Key Signature
- **<T>** = Time Signature
- **<S>** = Speed/Tempo
- **<N>** = New (start composing)

**Measure management:** Program tracks "beats per voice" and prevents overfilling measures.

**Navigation:** Backslash key navigates between screens.

**Loading:** Program loads with a bluegrass demo piece.

**Tied notes:** Simulated by setting a long Release rate (14–15) and placing a rest at
the start of the next measure. (OPEN: This is a workaround, not a native tied-note
command, suggesting the format does NOT natively support tied notes across measure lines.)

**General model:** Classical-music transcription style ("traditional notation" vs
tracker's "non-traditional notation"). HVSC corpus confirms: folk songs, anthems,
Bach/Beethoven/Vivaldi transcriptions — not demoscene productions.

---

## File Format Evidence: m. and w. Prefix Files

**Source:** t.sidsmith and t.smithsid documentation, Loadstar 237 (Discmaster 237.d81)

### SongSmith File Naming Convention:
- **m.** prefix: music/note data (the melody)
- **w.** prefix: waveform/ADSR data (1 block = 254 bytes or one C64 disk block)

This is confirmed by two converter programs:

**SIDSmith** (converts SongSmith → SID Player .mus):
> "Files use 'm.' and 'w.' prefixes [for SongSmith]; output format: '.mus' files
> compatible with SID EDITOR and SID PLAYER."
> "Processing speed: all done at ML speeds."
> (Source: t.sidsmith, Loadstar 237)

**SmithSID** (converts SID Player .mus → SongSmith):
> "Output: SONGSMITH format files beginning with 'm.' and 'w.'
> An additional 1-block 'w.' file stores ADSR values and timbre information."
> (Source: t.smithsid, Loadstar 237)

### Inference: What the w. File Contains
The SmithSID documentation confirms the w. file holds **ADSR values and timbre
(waveform/tone color) information**. This is the instrument definition file. It is
"1 block" (= 254 usable bytes on a C64 1541 disk).

OPEN: Exact byte layout of the m. and w. files requires RE of the SongSmith binary.
The sidid signatures (v2/v3) show the player reads note bytes and looks up frequencies
in a table, then writes to $D400/$D401/$D404. The w. file likely maps to ADSR writes
($D405–$D406 per voice) and possibly waveform control ($D404 bits 4–7).

---

## Relationship to Compute's SID Player (.mus Format)

**Source:** t.sidsmith + t.smithsid documentation, Loadstar 237

SIDSmith (1988, Debby Cruz + Scott Resh) was written specifically to bridge SongSmith
→ SID Player. The documentation frames the two as competing systems:

- **SongSmith**: Traditional notation style, easier for beginners, developed by Joe
  Garrett for Loadstar/Softdisk. "Quickly and easily entered."
- **SID Player** (Compute's Gazette, Craig Chamberlain + Harry Bratt): Non-traditional
  notation, "industry standard with thousands of SID musicians," more powerful. Supports
  "triplets and use filtering."

SIDSmith converts SongSmith files to .mus with optional:
- Measure markers
- Credit preservation
- Key signature transposition
- Tempo selection

SmithSID converts in the reverse direction; warns that quality degrades if the original
.mus has "a lot of enhanced sounds."

### Implication for USF Design:
SongSmith's musical model is a SUBSET of SID Player's capability. If we can convert
SongSmith → SID Player (via SIDSmith), then SongSmith data is encodable in a note+duration
+ per-instrument ADSR/waveform structure. The SID Player .mus format (fully documented
in `docs/github_sidplayer_mus_format.md`) gives us the ceiling of what SongSmith
can express.

---

## Instrument Model

**Source:** sidid signatures (sidid_signatures.md) + converter documentation

The sidid v2/v3 signatures show:
```
SEC / SBC #$01 / ASL A → (note - 1) × 2 = word-table index
LDA freq_table,Y   → freq-lo
STA $D400
INY
LDA freq_table,Y   → freq-hi
STA $D401
... (control byte write to $D404)
```

This is a **frequency-table lookup player** — notes are integers mapping into a
pre-built frequency table. The table is:
- v2: at fixed address $C290 (hardcoded, not relocated)
- v3: at a relocated address (wildcarded in sidid signature)

The w. file presumably provides the ADSR settings ($D405, $D406) and control
byte bits ($D404 bits 4–7: waveform select). There is no evidence from the docs
of a multi-instrument program system (instrument programs cycling through wave/ADSR
sequences) — SongSmith appears to use a STATIC ADSR+waveform per voice per song.

OPEN: Confirm via RE whether the w. file defines per-voice or per-note instrument
assignments, or a single global setting.

---

## Voice/Polyphony Model

All evidence points to standard 3-voice polyphony:
- 3 SID voices (V1=$D400, V2=$D407, V3=$D40E)
- Each voice composed independently (keys 1/2/3 to select)
- No evidence of arpeggio, vibrato, or per-tick effects (unlike trackers)
- "Tied notes" are a workaround (long release + rest), not a native feature

The .mus format that SongSmith converts TO supports: vibrato (VDP/VRT), portamento (POR),
pulse sweep (P-S), filter (F-C/F-S/F-M), LFO, etc. — but the text says these are added
"for the final touches" IN SID EDITOR after SIDSmith conversion. This implies SongSmith
itself does NOT support these effects natively.

---

## Tempo Model

**Source:** t.songsmith documentation

Tempo is set from the Main Menu with <S> (Speed). No specific BPM values are documented
in community sources. The SID Player .mus format (which SIDSmith targets) uses a 64-entry
tempo table mapping to metronome markings (56–1800 M.M.) in jiffies (1/60s CIA timer
values). SongSmith's tempo may use the same underlying timer mechanism.

---

## Key and Time Signature

**Source:** t.songsmith documentation

Explicit Key Signature (<K>) and Time Signature (<T>) controls exist. This is consistent
with the classical-transcription use case. In the sidid signatures, there is no evidence
of key-signature data being written to SID registers — key signature is an editor UI
feature only, mapping to actual note frequencies at entry time.

---

## Corpus Characteristics (HVSC Evidence)

From `github_parser_search.md` (prior session):
- Total: 337 SIDs (308 unversioned + 19 v1 + 3 v3 + 1 v2 + 6 Song_Writer)
- Demo tunes packaged with SongSmith v2005: 7 folk songs (Alouette, Funiculi Funicula,
  Meadowlands, Muss I Denn, Scarborough Fair, Skye Boat Song, The Parting Glass)
- Heaviest HVSC cluster: MUSICIANS/O (Mario Oropesa, classical transcriptions)
- Known composers: Beggerow_Alan, Cruz_Debby, Davis_John_S, Marquis_Dave (unconfirmed
  for SongSmith — may use SID Editor), plus likely many unnamed hobbyists

The corpus is overwhelmingly **classical + folk + traditional transcriptions**, consistent
with SongSmith's traditional-notation UI and non-demoscene user base.

---

## Leads to Follow

1. **OPEN — Exact m. file format**: The note/duration byte layout in the m. file is
   unknown from community sources. Requires RE of the SongSmith binary (CSDb .d64).
   Working hypothesis: simple (note_number, duration_code) pairs per voice,
   possibly measure-delimited. The sidid v2 signature suggests note_number is a
   single byte that goes through (n-1)*2 → freq table lookup.

2. **OPEN — w. file layout**: 254 bytes encoding ADSR for 3 voices = ~84 bytes of
   envelope data + waveform control. Unknown padding/header. RE target.

3. **OPEN — How voices are interleaved**: Are m. data for all 3 voices in one file
   (interleaved), or in 3 separate m.* files? SmithSID outputs "m. files" (plural in
   some contexts) suggesting one per voice is possible.

4. **OPEN — Note-number encoding**: The sidid signature uses `CMP #$19 / BCC / CMP #$1D`
   in v1 (rest/sentinel detection?). In v2/v3: `SEC / SBC #1 / ASL` (note 1 = lowest
   pitch). Minimum note = 1 (after SBC); rest may be 0. Maximum determined by freq table
   size (typically 96 half-steps = 8 octaves on C64).

5. **OPEN — Measure/bar structure**: Does the m. file encode measure boundaries
   explicitly, or is measure tracking only in the editor? The "beats per voice" tracking
   mentioned in the doc suggests measures ARE tracked during entry, but they may not
   be stored.

6. **SIDSmith 1988 question**: If SIDSmith was written in 1988, it predates SongSmith
   proper (© 2005). Either: (a) There was a 1988 SongSmith that the converter targeted,
   implying the format predates the 2005 version significantly, OR (b) "1988" is a
   misremembering or refers to when the PRECURSOR format was used. This has major
   implications for version history.
