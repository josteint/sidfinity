---
source_url: https://www.pouet.net/prod_nfo.php?which=26206&font=none
fetched_via: direct
fetch_date: 2026-06-17
author: Lasse Öörni (Cadaver / Covert Bitops)
content_date: 2006-08-30
reliability: primary
---

# NinjaTracker V2.0 — Full NFO Text

(Reproduced verbatim from the pouet.net NFO for prod #26206)

## Contents (package)

- ninjatr2.d64   — Disk image with editor and example tunes
- example.prg    — Gamemusic player example program
- nt2play.s      — DASM format sourcecode for gamemusic player
- ins2nt2.exe    — Utility for converting GoatTracker instruments (GT V1.x/V2.x)
- /src directory — Editor & example sourcecode

## 1. Introduction

"NinjaTracker V2.0 is still a somewhat minimal music editor."

Key improvements over V1.x include:
- General purpose commands (also used as instruments)
- Two-column tables (vs. V1's three-column)
- A slide function that knows to stop at the target pitch

Software is freeware. Customization is allowed and encouraged.

Contact: loorni@gmail.com
Web: http://covertbitops.c64.org

## 2. How to Use

### 2.1 General Keys
Function keys control playback (F1-F8); navigation uses arrow keys and
bracket/comma/period keys; hexadecimal data entry uses 0-9 and A-F.
Cut/copy/paste operations use Shift+X/C/V.

### 2.2-2.4 Editor Modes
Track, pattern, and command editors each have specialized key bindings for
note entry, transposition, and testing functionality.

## 3. The Musicdata

### 3.1 Track Data
- Maximum 16 songs with 3 tracks each
- All songs share 127 patterns, tables, and commands
- Track values:
  - Loop marker
  - Patterns: 01-7F
  - Transpose operations: 80-BF (downward), C0-FF (upward)

### 3.2 Pattern Data
Patterns contain FOUR columns (vs. V1's three-column "sector" format):
  1. Note / keyoff / keyon
  2. Command number
  3. Duration
  4. Command name

Notes range from C-1 to B-7. Minimum duration: 2 frames.

### 3.3 Table Data
- Wavetable, pulse table, and filter table
- Two-column format (vs. V1's three-column)
- Jump destinations and modulation parameters
- Tables control instrument synthesis behaviour

### 3.4 Command Data
Commands function as BOTH instruments and general pattern modifiers:
- Set ADSR
- Set table pointers (wave, pulse, filter)

### 3.5-3.6 Global Settings and Optimizations
Sustain/release and waveform initialization are configurable and saved per song.

## 4. Packing / Relocating

Two modes:
- Normal mode: playroutine included with musicdata
- Gamemusic mode: playroutine stored separately (saves diskspace when a game
  has many music modules — one shared playroutine, many data files)

## 5. Closing Words
Included example tunes demonstrate practical implementation.
Examples were converted from GoatTracker 2 format.

## V2.x Version History (from Lemon64 forum thread, assembled from Lasse's posts)

V2.0   (30 Aug 2006) — Initial V2 release (total rewrite of V1)
                        "May be even somewhat easier to use"
                        Playroutine "slower than the previous versions"
V2.01  (2 Sep 2006)  — Editor improvements
V2.02  (2 Sep 2006)  — Warning: "slightly slower and bigger playroutine"
V2.03  (3 Sep 2006)  — "Sexy hardrestart"; attempted rastertime optimization;
                        "the player is yet bigger"
                        Attack fluctuation hidden by using silent first frame of note
V2.04  (19 Jun 2013) — Fixes transpose not resetting when playback started
                        from beginning
                        (Long gap between V2.03 and V2.04 — 7 years)
