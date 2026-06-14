# The Music Shop Users Manual — Full Text Extract

provenance:
  source_url: https://archive.org/stream/The_Music_Shop_Users_Manual/The_Music_Shop_Users_Manual_djvu.txt
  fetched_via: WebFetch (archive.org djvu.txt full-text OCR)
  fetch_date: 2026-06-14
  content_date: 1984 (manual ships with software released 1984-09-27)
  reliability: HIGH — OCR of scanned original, 50 pages, ABBYY FineReader 11.0 at 600 PPI

---

## TABLE OF CONTENTS

- Opening Night: "Fantasy in G"
- The Orchestra Tunes Up: Getting Started
- Instruments Ready: How to Use the Music Shop
- The Performance Begins: The Music Shop Step by Step
- Program Notes: Variations on the Main Theme
- Warranty Information

---

## OPENING NIGHT

The introduction positions The Music Shop as composing software for the Commodore 64. Users can
"create original musical compositions easily and quickly by placing musical symbols onto the staff
on your screen." Key capabilities include adjusting tempo, sound, key and time signatures
mid-composition, editing features, and printing as professional sheet music.

---

## THE ORCHESTRA TUNES UP: GETTING STARTED

**System Requirements:**
- Commodore 64
- Disk drive
- TV or monitor
- Optional: joystick (control port 2), data disk, graphics printer (VIC-1525 or MPS-801)

**Loading Instructions:**
Type `LOAD "MS",8,1` (standard printer) or `LOAD "MSP",8,1` (alternative printers), then press
RETURN. Program loads in under two minutes. Demo mode plays first 12 program disk scores
automatically; press space bar to advance or RUN/STOP to exit.

---

## INSTRUMENTS READY: HOW TO USE THE MUSIC SHOP

**Control Methods:**
1. **Joystick:** Controls arrow position; button makes selections. Must be in control port 2.
2. **Keyboard:** CRSR keys move arrow; RETURN makes selections. F3/F5 adjust slides; F5/F3 turn
   pages.
3. **Combination:** Multiple methods available throughout program.

**Interface Structure:**
- Pull-down menus (Tools, The Music Shop/Title, Edit)
- Windows contain selection tools
- Dialog boxes request information or provide warnings
- Exit windows via small exit box or RUN/STOP key

---

## CREATING YOUR FIRST COMPOSITION

The manual walks through creating a three-voice harmony using the pre-loaded composition "TEAPOT":

1. Select Get Notes from Tools menu (or press F1)
2. Choose note type and place on staff
3. Music plays automatically as notes drop
4. Use Adjust Sound (F2) to modify synthesizer settings
5. Save to formatted data disk
6. Print using Print Page/Print Score options

---

## THE PERFORMANCE BEGINS: THE MUSIC SHOP STEP BY STEP

### MUSIC BOX
Status display showing: arrow position by staff/note, play control (pressing button plays full
score), and menu direction indicator.

### TOOLS MENU

#### Get Notes
- Displays available notes, rests, and musical symbols
- Supports up to three simultaneous notes per column
- Keyboard shortcuts: 1-6 for whole to thirty-second notes; SHIFT 1-6 for rests
- Special commands:
  - B = bar line
  - S = sharp
  - F = flat
  - N = natural
  - U = stem direction toggle
  - T = triplet mode
  - INST = insert space
  - DEL = delete space

#### Setup Screen
- Staff grouping: single or double staves
- Clef selection (treble/bass)
- Background/foreground colors
- Key signature selection (placed via K key)
- Note: changing staff grouping erases existing music

#### Adjust Sound
Provides three independent voice controls (V1, V2, V3) for full synthesizer access.

**Envelope (ADSR):**
- A (Attack): time to reach peak volume
- D (Decay): time from peak to sustain level
- S (Sustain): held volume level
- R (Release): time from note stop to silence

**Waveform (TSPN):**
- T (Triangle): mellow, flute-like
- S (Sawtooth): brassy trumpet/saxophone
- P (Pulse): reedy oboe (adjustable via width)
- N (Noise): percussion/white noise

**Control Register (GSRV):**
- G (Gate): voice on/off
- S (Sync): synchronizes two voice pitches
- R (Ring Modulation): metallic/bell tones (requires triangle wave)
- V (Vibrato): waving effect

**Pulse Width (CMf):**
- C (Coarse): large adjustments
- M (Medium): moderate adjustments
- F (Fine): small adjustments

**Filter (LBH, cmfR):**
- L (Low-Pass): allows low frequencies; removes mid/high
- B (Band-Pass): allows mid frequencies only
- H (High-Pass): allows high frequencies; removes low/mid
- C/M/F controls cutoff frequency
- R (Resonance): filter strength

**Preset Sounds:** Eight selectable complete voice configurations; type R to restore defaults.

**Dynamic Changes:** Use COMMODORE + preset number (1-8) to change sound mid-composition at
specific measure positions.

**Volume/Tempo/Vibrato:**
- Tp: tempo control
- Vo: volume control
- Vi: vibrato intensity

#### Verify Timing
Checks measure beats against time signature. Type V or select from Tools menu. Stops at measures
with incorrect beat count. Assumes 4/4 time if no signature placed.

---

### TITLE MENU

#### Load Score
Retrieves compositions from program or data disk. Type exact filename and press Load button.

#### Save Score
Saves to formatted data disk only (program disk protected). Dialog prompts for file replacement if
duplicate name exists.

#### List Titles
Displays directory of available scores. Scroll via hollow arrow; click title to load directly.

#### Enter Title
Creates or changes score title. Each title becomes unique file for multiple versions.

#### Format Disk
Prepares data disk for saving (destroys existing data). Point to Format button and confirm.

#### Print Page
Prints current screen page only. Requires compatible printer setup. Save first to prevent data
loss.

#### Print Score
Prints from current position to last page with notes. Double-staff mode produces 6 staves per
printed page; single-staff produces 9 staves per page.

#### Clear Page
Erases single page. Undo available via Edit menu.

#### Clear Score
Erases entire composition (cannot Undo). Warning dialog appears before deletion.

#### Quit
Exits program with unsaved-score warning.

---

### EDIT MENU

#### Capture
Marks rectangular area for editing. Arrow carries dashed line; press button at section start, then
move to encompass desired area. Press again to confirm.

#### Cut
Removes captured section; remaining notes shift left to fill gap. Undo available.

#### Copy
Places captured section in memory without removing original. Use Paste to place elsewhere.

#### Clear
Erases captured section without shifting remaining notes.

#### Paste
Places previously cut/copied/cleared section at new location. Arrow shows paste brush symbol.
Cannot paste if insufficient space (beep indicates error). Use F5/F3 to turn pages while pasting.

#### Undo
Reverses last edit action. Works for cut, copy, paste, clear, and Clear Page function.

---

### PAGE BOX
Displays current page number (1-20 for double staves, 1-13 for single staves). Navigate via
joystick (up/down while holding button) or F3 (previous)/F5 (next) keys.

---

## PROGRAM NOTES: VARIATIONS ON THE MAIN THEME

### BASICS OF MUSIC THEORY

#### Staff & Clefs
Music uses five-line staff with four spaces. Treble clef indicates higher notes (F below bottom
line to D above top line in double-staff mode). Bass clef indicates lower notes (A below bottom
line to F above top line in double-staff mode).

#### Notes & Rests
Eight note types: whole, half, quarter, eighth, sixteenth, thirty-second notes, plus corresponding
rests. Dotted versions increase duration by one-half original value.

#### Accidentals
- Sharp (#): raises pitch one half-step
- Flat (b): lowers pitch one half-step
- Natural (♮): cancels sharp/flat

#### Measures & Bar Lines
Single bar line marks measure boundaries. Double bars indicate key changes, section starts,
section ends, or repeats.

#### Leger Lines
Short lines extending staff for notes above/below normal range.

#### Time Signatures
Fraction-like symbols after key signature. Top number indicates beats per measure; bottom
indicates note value receiving one beat. 4/4 time = four quarter-note beats per measure. 3/4 time
= three quarter-note beats per measure.

#### Note Stems
Generally point down for notes on/above middle line, up for notes below. Can toggle via U key.
Groups typically share direction for readability.

#### Ties
Curved lines connect same-pitch adjacent notes, creating single sustained tone. Position at same
note height. Place before/after bar lines when crossing measures.

#### Intervals
Distance between two pitches. Harmonic intervals (simultaneous) include thirds (space or line
separation).

#### Octave
Eight-note interval (e.g., E to next E). Program provides octave-up symbol pair: place opening
mark before section, closing mark after. Affects current staff only; must place on both staves in
double-staff mode.

#### Scales
Major scale: eight consecutive tones following whole-step/half-step pattern (W-W-H-W-W-W-H).
Minor scales exist in harmonic and melodic varieties with different interval patterns.

#### Key Signatures
Sharps/flats placed after clef, indicating accidentals throughout piece unless marked with
natural. Examples provided for G major (one sharp), B-flat major (two flats), C major (no
accidentals).

#### Triplets
Three notes played in time of two. Enable via T key; shadow "t" appears. Place triplet symbol
from Get Notes window above/below for visual reference.

#### First & Second Endings
Repeat notation: place "1." marking at first ending, "2." at alternate ending.

---

## SOUND AND THE COMMODORE 64

### The SID Chip
Sound Interface Device enables three independent oscillators (voices), each with programmable
envelope, waveform, vibrato, and filter options.

### Sound Waves
Air disturbances from vibrating sources. Different waveforms produce distinct tone qualities.

### Envelope Generator (ADSR)
Shapes sound progression:
- Attack phase reaches peak
- Decay phase falls to sustain level
- Sustain phase holds volume
- Release phase falls to silence

### Waveforms (TSPN)
- Triangle: mellow (flute-like)
- Sawtooth: brassy (trumpet/saxophone)
- Pulse: reedy (oboe, varied by width)
- Noise: white noise (percussion)

### Control Register (GSRV)
- Gate: enables/disables voice
- Sync: combines two voice frequencies for varied tones
- Ring Modulation: metallic/bell effects (requires triangle waveform for selected voice)
- Vibrato: produces waving effect (intensity set via Vi slide)

Voice combinations for Sync/Ring:
- Voice 1 + Voice 3
- Voice 2 + Voice 1
- Voice 3 + Voice 2

### Pulse Width (CMf)
Adjusts pulse waveform width; must set or no sound produced.

### Filter (LBH, cmfR)
Three filter types modify tone quality by controlling frequency ranges:
- Low-Pass: preserves low frequencies; removes mid/high
- Band-Pass: preserves mid frequencies; removes low/high
- High-Pass: preserves high frequencies; removes low/mid

Cutoff frequency adjusted via C/M/F controls; resonance (sharpness) adjusted via R.

---

## MUSIC SHOP PROGRAM DISK TITLES

Compositions include works by J.S. Bach, Tchaikovsky, Mozart, Beethoven, Scott Joplin,
traditional carols, and original pieces. Total of 26+ titles covering classical, rag, and
children's songs. Named titles confirmed: "TEAPOT" (tutorial), "Fantasy in G" (opening
demonstration), Pachelbel's Canon in D, and a variety of carols and classical arrangements.

---

## WARRANTY INFORMATION

90-day disk replacement warranty from purchase date. Software sold "AS IS" without performance
warranties. Defective products may be replaced/repaired at Broderbund's option within 90 days
with proof of purchase.
