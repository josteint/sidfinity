# The Music Shop — Manual, Program & Data Model

provenance:
  primary_source: The Music Shop Users Manual (archive.org)
  source_url: https://archive.org/details/The_Music_Shop_Users_Manual
  full_text_url: https://archive.org/stream/The_Music_Shop_Users_Manual/The_Music_Shop_Users_Manual_djvu.txt
  fetched_via: WebFetch (archive.org djvu OCR full-text)
  fetch_date: 2026-06-14
  content_date: 1984
  reliability: HIGH — OCR of scanned original manual, 50 pages at 600 PPI

  secondary_sources:
    - Commodore 64 & 128 Music Software Guide (Lolita Walker Gilkes, 1986; archive.org)
    - Compute! Gazette Issue 26, Aug 1985 — "Review: The Music Shop" by Philip I. Nelson (p. 50; full text not accessible via WebFetch but TOC confirmed)
    - Lemon64 forum thread t=45281 (2012/2016 — file format analysis by "scatha")
    - Lemon64 forum thread t=36765 (MIDI version)
    - C64-music.blogspot.com review (undated, post-2009)
    - atarimagazines.com (Compute! issue 60 — original announcement, $44.95 price, IBM PCjr/Mac plans)
    - CSDb #23970 (1985 crack release entry)
    - HVSC hvsc84.db (182 SIDs, engine='MusicShop')

---

## 1. Provenance & Author

| Field | Value |
|---|---|
| Title | The Music Shop |
| Author/Programmer | Don Williams (also archived as "Dan Williams" — two IA entries differ; "Don" is more likely correct per user-task briefing) |
| Publisher | Brøderbund Software, Inc. |
| Release date | 1984-09-27 (date on archived disk images) |
| Price | $44.95 USD |
| Platform | Commodore 64 |
| Physical medium | 5.25" floppy disk |
| Manual | 50 pages; archived at archive.org (PDF + djvu.txt) |

The program was published by Brøderbund as part of the same 1984 wave as The Print Shop. The
Compute! issue 60 announcement noted IBM PCjr and Apple Macintosh versions were planned for
spring 1985 (unconfirmed whether shipped). The program is physically preserved at The Strong
National Museum of Play (Rochester, NY) as part of the Doug Carlston / Brøderbund donation.

**Name ambiguity:** Two separate Archive.org entries exist — one credits "Don Williams", the other
"Dan Williams". The HVSC credits the composer as "Don Williams <?>". No further biographical
information about the programmer was found; they do not appear to be the country music singer.

---

## 2. MIDI Version (1985)

| Field | Value |
|---|---|
| Title | The Music Shop for MIDI |
| Publishers | Brøderbund + Passport Designs |
| Year | 1985 |
| Price | $99.95 USD |
| Required hardware | Passport MIDI interface card, joystick, dot-matrix printer with graphics interface |

The MIDI version grew from the original when Passport Designs contacted the programmer and asked
for a version using MIDI output instead of the C64's internal SID voices. MIDI was one year old
at that point and Passport was a pioneer in the technology.

Key differences from the original:
- **Output:** 8 MIDI voices across 4 MIDI channels/keyboards (instead of 3 SID voices)
- **Print formats:** Piano, single staff, or quartet (expanded from the original)
- **Auto page turn:** "automatically turns to the next page of music, eliminating scrolling"
- **Interface:** Described as "Macintosh style" — same pull-down menus/windows as original
- **Score length:** Up to 20 pages (same as original double-staff mode)
- **MIDI interface:** Likely Passport MH01 or MH02 card (MIDI In/Out; drum/tape sync)

The MIDI version's manual reportedly did not mention MIDI functionality explicitly — causing
confusion for preservationists who disk-imaged it (Lemon64 thread t=36765, user "ckult").
A working .g64 image was created via Kryoflux and runs on 1541 Ultimate II hardware.
Archive.org: https://archive.org/details/the-music-shop-for-midi

---

## 3. Data Model: Graphical Staff Notation (NOT a tracker)

The Music Shop is a **graphical music-notation composition program**, not a tracker. The user
interface presents a conventional five-line musical staff and places note/rest symbols onto it
using a joystick or keyboard. The underlying data model follows standard music notation, not
tracker step-sequences.

### 3.1 Score / Page structure

- Maximum composition length: **20 pages** (double-staff mode) or **13 pages** (single-staff mode)
- Display: one page at a time — no horizontal scrolling within a page
- Two stave configurations: **single staff** (one five-line staff) or **double staff** (treble +
  bass clef pair)
- Clefs: treble and/or bass

### 3.2 Voices / Polyphony

- **3 simultaneous voices** (mapped to the 3 SID oscillators)
- In the notation display: up to **3 simultaneous notes per column** (vertical position on the
  staff determines which of the 3 SID voices carries that note — the manual does not spell this
  mapping out explicitly, but HVSC SIDs confirm 3-voice polyphony)
- Each voice (V1, V2, V3) has completely independent synthesizer settings

### 3.3 Pitch representation

Pitch is entered by selecting a note symbol from the Get Notes window and positioning it
**vertically on the staff** — the vertical position encodes pitch (standard staff notation).
The range is:
- Treble clef: F below bottom staff line to D above top staff line
- Bass clef: A below bottom staff line to F above top staff line
- Octave marks can shift a section up one octave (opening + closing bracket pair); must be placed
  on both staves in double-staff mode

Accidentals:
- Sharp (S key): raises pitch one half-step
- Flat (F key): lowers pitch one half-step
- Natural (N key): cancels sharp/flat
- Key signatures carry accidentals through the piece

### 3.4 Duration / Rhythm representation

Duration is encoded by the **note type** selected in the Get Notes window:
- Note types: whole, half, quarter, eighth, sixteenth, thirty-second
- Dotted variants: extend duration by one-half (dotted whole through dotted thirty-second)
- Rests: corresponding rest symbols for each note type
- Triplets: three-in-the-time-of-two (T key toggles triplet mode; visual "t" shadow appears;
  triplet marker placed from Get Notes window)
- Ties: curved line connecting same-pitch adjacent notes → single sustained tone

**Keyboard shortcuts for note entry:**
- 1-6 = whole through thirty-second notes
- SHIFT+1-6 = corresponding rests

### 3.5 Rhythm structure / Time signatures

- Time signatures placeable mid-composition
- Supported: 4/4, 3/4, and others (generic — top number = beats/measure, bottom = beat value)
- Verify Timing tool: checks beat count against time signature; halts at incorrect measures;
  defaults to 4/4 if no signature placed
- Bar lines: single (measure boundary) or double (key changes, section starts/ends, repeats)
- First and second endings: "1." and "2." markers for repeat sections

### 3.6 Key signatures

- All major and minor keys supported
- Placed via K key after the clef
- Can be changed mid-composition (double bar line indicates change)
- Examples given: C major (0 accidentals), G major (1 sharp, F#), Bb major (2 flats, Bb + Eb)

### 3.7 Notation → SID mapping

The program's player converts the staff-notation score to SID register writes at playback time.
The manual's "Sound and the Commodore 64" chapter explains the mapping explicitly:

- Each voice's **vertical staff position** encodes a pitch → maps to an SID frequency register
  value (via a frequency table; not explicitly documented in the manual, but standard 8580/6581
  equal-tempered tuning)
- The note type + tempo setting determines **gate timing** (how long a note's gate bit is held
  high and when the release phase begins)
- The voice's current synthesizer settings (ADSR, waveform, pulse width, filter) are written to
  SID registers at voice initialization
- **Vibrato:** implemented by the program's player (intensity set via Vi slide); modulates the
  frequency register during the sustain phase
- **Dynamic preset changes:** COMMODORE + preset-number (1-8) mid-composition triggers a
  synthesizer-setting change at that measure position — these are stored as events in the score

---

## 4. Synthesizer Controls (Per Voice)

All three voices (V1, V2, V3) have fully independent synthesizer controls accessible via
"Adjust Sound" (F2). These map directly to SID registers:

### 4.1 Envelope (ADSR) — SID $D405/$D406 per voice

| Control | SID register field | Description |
|---|---|---|
| A (Attack) | Attack nibble | Time to reach peak volume (0-15) |
| D (Decay) | Decay nibble | Time from peak to sustain level (0-15) |
| S (Sustain) | Sustain nibble | Held volume level (0-15) |
| R (Release) | Release nibble | Time from gate-off to silence (0-15) |

(Manual does not state the 0-15 range explicitly, but this follows SID hardware.)

### 4.2 Waveform (TSPN) — SID $D404 control register bits 4-7

| Key | Waveform | SID bit | Tone character |
|---|---|---|---|
| T | Triangle | bit 4 | Mellow, flute-like |
| S | Sawtooth | bit 5 | Brassy, trumpet/saxophone |
| P | Pulse | bit 6 | Reedy, oboe-like (width-adjustable) |
| N | Noise | bit 7 | Percussion, white noise |

### 4.3 Control Register (GSRV) — SID $D404 bits 0-3

| Key | Function | SID bit | Notes |
|---|---|---|---|
| G | Gate | bit 0 | Voice on/off (note trigger) |
| S | Sync | bit 1 | Synchronizes oscillator with neighbouring voice |
| R | Ring Modulation | bit 2 | Metallic/bell tones; requires triangle wave |
| V | Vibrato | (player-side) | Frequency modulation; intensity via Vi slide |

Voice combinations for Sync/Ring (follow SID hardware pairing):
- Voice 1 syncs/ring-mods with Voice 3
- Voice 2 syncs/ring-mods with Voice 1
- Voice 3 syncs/ring-mods with Voice 2

### 4.4 Pulse Width (CMf) — SID $D402/$D403 per voice

Three-level adjustment for the pulse waveform duty cycle:
- C = Coarse adjustment
- M = Medium adjustment
- F = Fine adjustment
Note: must be set when using pulse waveform or no sound is produced.

### 4.5 Filter (LBH, cmfR) — SID $D417/$D418

| Control | Function |
|---|---|
| L (Low-Pass) | Passes low freqs; removes mid/high |
| B (Band-Pass) | Passes mid freqs only |
| H (High-Pass) | Passes high freqs; removes low/mid |
| C/M/F | Cutoff frequency (coarse/medium/fine) — SID $D415/$D416 |
| R (Resonance) | Filter Q/sharpness — SID $D417 upper nibble |

### 4.6 Preset Sounds

- 8 selectable complete voice configuration presets (full ADSR + waveform + pulse width + filter)
- Selected by preset number (1-8)
- Type R to restore defaults
- **Mid-composition preset changes:** COMMODORE + preset-number at a measure position triggers
  a voice-setting change embedded in the score data

### 4.7 Global controls

| Control | Function |
|---|---|
| Tp (Tempo) | Playback tempo (slider) |
| Vo (Volume) | Master volume (SID $D418 low nibble) |
| Vi (Vibrato) | Vibrato intensity (global) |

---

## 5. Save / File Format

Songs are saved to a formatted **data disk** (program disk is write-protected). The file format
is **proprietary** and uses a `.seq`-like structure. Based on analysis by Lemon64 user "scatha"
(Nov 2016):

> "They do not store the pitch and length of the notes, but the layout information, as in three
> entries per column. Of course it has to be, the layout is a necessity. Each symbol (quarter
> note, #, b, [1], etc.) that can be used in the score had its own code, plus the vertical
> placement of each."

Key implications for the data model:
- The file stores **screen layout** (symbol codes + vertical position per column), not abstract
  musical pitch + duration
- Three data entries per vertical column (one per voice/layer)
- Vertical position encodes staff pitch
- Symbol code encodes note type, rest type, barline type, accidentals, repeat markers, etc.
- Scatha reported writing a C64 BASIC converter to transform SEQ data to standalone playable music
- Format is NOT MIDI and NOT directly convertible without reverse-engineering the symbol table and
  column layout

---

## 6. Editing

- **Capture:** Rectangular region selection
- **Cut:** Remove selected region; remaining notes shift left to fill gap; undoable
- **Copy:** Copy region to clipboard; paste elsewhere; undoable
- **Clear:** Erase region without shifting; undoable
- **Paste:** Place clipboard content at current position; beeps if insufficient space
- **Undo:** Single-level undo for last edit action (cut/copy/paste/clear/clear-page)
- Page-level: **Clear Page** (single page erasure; undoable); **Clear Score** (full erasure; NOT undoable)

---

## 7. Output / Printing

- **Print Page:** Prints current screen page
- **Print Score:** Prints all pages from current position to last note
- Compatible printers: VIC-1525, MPS-801, and alternatives (loaded via `LOAD "MSP",8,1`)
- Print output: conventional sheet music notation
- Double-staff mode: 6 staves per printed page; single-staff: 9 staves per printed page

---

## 8. Program Disk Demo Scores

The program disk ships with 12+ built-in demo scores that play automatically on startup:
confirmed titles include "Fantasy in G" (opening demo), "TEAPOT" (tutorial piece), and
Pachelbel's Canon in D. Full program disk includes works by J.S. Bach, Tchaikovsky, Mozart,
Beethoven, Scott Joplin, traditional carols, and original pieces (26+ total).

---

## 9. HVSC Corpus

HVSC #84 contains **182 SID files** classified with engine='MusicShop'. These are the demo/
tutorial scores from the program disk plus compositions made by various users around the world
and submitted to HVSC.

### Authors in HVSC
| Author | # SIDs | Notes |
|---|---|---|
| Don Williams <?> | 28 | Original program disk + demo scores |
| <?> (unknown) | ~120+ | DEMOS/UNKNOWN/Music_Shop/ — Polish/German/international contributions |
| Louis Ewens | 2+ | External composer |
| Ace64 | 2+ | External composer |
| Mehdi Safavy | 1+ | External composer |
| Grzegorz Struminski (Gregfeel) | 1+ | External composer |
| Marek & Olaf Roth | 1+ | External composer |
| Francis Mechner | 1+ | External composer |
| E.T, Ratti, T. Mierzwa | 1 each | External composers |

### SID addresses (uniform across ALL 182 SIDs)
| Field | Value (decimal) | Value (hex) |
|---|---|---|
| load_addr | 0 | (uses embedded load address) |
| init_addr | 41037 | $A04D |
| play_addr | 22362 | $575A |
| n_subtunes | 1 | (each SID = one song) |

NOTE: init_addr $A04D falls in the Kernal ROM region ($A000-$BFFF). This likely means the
player uses a short stub in RAM that jumps into a relocated or in-ROM routine, OR the PSID
wrapping caused this address to be set unusually. All 182 SIDs share the same init/play
addresses, confirming a single shared player engine.

### Representative HVSC scores (Williams_Don)
Classical/baroque: 1812 Overture, Bolero, Canon in D, Für Elise, Greensleeves,
Bach Inventions VIII & XIII, Jesu (Bach), Nutcracker, Russian Dance, Sugar Plum, Sonata in C

Ragtime: Maple Leaf Rag, Peacherine Rag, Elite Syncopations

Carols: Deck the Hall, God Rest You, Heard on High, Jingle Bells, Silent Night

Original: Princess Tulip, Teapot

Community additions (DEMOS/UNKNOWN): wide variety — pop (Ghostbusters, Axel F, Major Tom,
Let It Be, Careless Whisper), classical (Dolannes Melodie, Badinerie, Entertainer, Hooked on
Mozart), Polish/German folk songs, hymns, etc.

---

## 10. Comparison to Activision's Music Studio

The Lemon64 review notes: "Activision's Music Studio is probably more inviting than Broderbund's
Music Shop because of its icon-based interface. Music Shop caters probably more to the serious
music composer."

The Commodore 64 & 128 Music Software Guide confirms Music Shop "uses whole to 32nd notes. Music
is displayed on a double or single staff, on treble and/or bass clefs. Users may change keys,
time signature, sound quality, and tempo in mid-composition."

Music Shop's differentiators for serious composers:
- Dotted notes and ties supported
- Triplets supported
- First and second endings (repeat notation)
- Mid-composition sound changes (preset events embedded in score)
- Full ADSR control per voice
- Full filter control (LBH + resonance)
- Sync and ring modulation available
- Sheet music print output

---

## 11. CSDb Coverage

| CSDb entry | Details |
|---|---|
| #23970 | 1985 crack by Agent 16 + The Dark Knight; released 1985-01-26; two .d64 variants |
| #82453 | Original program entry (per task briefing — this is the canonical Broderbund release entry) |

---

## 12. Leads to Follow

1. **Compute! Gazette Vol.3 No.8 (Aug 1985) — "Review: The Music Shop" by Philip I. Nelson,
   p.50.** The full text was not accessible via WebFetch (the djvu.txt and PDF exceeded fetch
   limits / page-routing issues). This is the primary contemporary published review. To read it:
   download the PDF from https://archive.org/details/1985-08-computegazette and go to page 50.
   It likely includes a feature checklist and the reviewer's assessment of notation completeness.

2. **SEQ data format reverse engineering.** Lemon64 user "scatha" (Nov 2016, thread t=45281)
   partially decoded the format and wrote a C64 BASIC converter. The full symbol table (codes for
   each note/rest/barline/marker type + vertical-position encoding) was not extracted here. If
   USF representation is ever attempted, the scatha BASIC program is the starting point.

3. **Player at $575A.** All 182 HVSC SIDs share play_addr=$575A and init_addr=$A04D. A
   disassembly of any HVSC SID (e.g. Canon_in_D.sid) would reveal the player's actual note/voice
   dispatch, ADSR write sequence, vibrato modulation, and preset-change event handling. This is
   the ground truth for what the player actually writes to $D400-$D418 per frame.

4. **Init address ambiguity.** $A04D is in Kernal ROM space. This may be a PSID wrapping
   artifact (the SID was created by stripping the program's player from the full binary, and the
   init stub was placed at a Kernal address). Needs investigation when attempting disassembly.

5. **Preset definitions.** The 8 factory presets shipped with the program are not documented in
   the manual text (only their existence is noted). They would need to be read from the program
   disk binary or from HVSC SID headers to enumerate the ADSR/waveform values.

6. **Vibrato implementation.** The manual says vibrato is controlled by a "Vi" intensity slider
   and a per-voice toggle (V in GSRV). The implementation in the player (sine LUT? triangle wave?
   frequency-step table?) is not documented — needs disassembly.

7. **Tempo encoding.** The Tp (tempo) slider value and how it maps to the SID play-rate (likely
   a CIA timer value or a frame-counter divisor) is undocumented in the manual.

8. **Don vs Dan Williams.** Two separate Archive.org uploads spell the name differently. The
   authoritative attribution is unclear. No biography or other credits were found for this
   programmer. Cross-referencing the Brøderbund corporate records (Doug Carlston archive at The
   Strong National Museum of Play) might resolve this.

9. **IBM PCjr and Macintosh versions.** The Compute! issue 60 announcement noted these were
   planned for Spring 1985. No evidence found that they shipped. Worth checking old PCjr/Mac
   software catalogs if the USF pipeline ever considers multi-platform concordance.
