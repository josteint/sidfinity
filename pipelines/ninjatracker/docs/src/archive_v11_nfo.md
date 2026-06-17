---
source_url: https://www.pouet.net/prod_nfo.php?which=13462&font=none
fetched_via: direct
fetch_date: 2026-06-17
author: Lasse Öörni (Cadaver / Covert Bitops)
content_date: 2004-01-25
reliability: primary
---

# NinjaTracker V1.1 — Full NFO Text

(Reproduced verbatim from the pouet.net NFO for prod #13462)

## Version History (from NFO)

V1.05
- Slide duration calculator added
- Allow editing of sector 0 (init-sector)

V1.1
- Hardrestart is more solid (set both AD, SR to $00) and same in both
  standard & gamemusic versions
- INS in pulse & filtertable inserts a 00,00-row, instead of 90,00 as in
  wavetable
- Pulse/filter-pointers in wavetable are adjusted when INS/DEL is used in
  pulse- or filtertable
- Movement in patterns speed-optimized (no unnecessary workpattern->
  pattern conversion anymore)

## 1. Introduction

"NinjaTracker is a 11-rasterline max. music editor, with simple but flexible
musicdata and small playroutine."

This tool suits creators with strict memory constraints who understand its
operation. It is freeware with customization permitted.

WWW: http://covertbitops.c64.org
Email: loorni`student.oulu.fi  [pre-gmail address]

## 2. How to Use

Keyboard controls include cursor movement, insert/delete rows, hexadecimal
editing, track selection, playback functions, and help access. Special keys
vary by editor mode (track, sector).

### 2.1 Track editor special keys
Song selection, position marking, sector navigation.

### 2.2 Sector editor special keys
Octave selection, note entry, command functions (Wave, AD, SR, Filter),
copying, transposition.

## 3. The Musicdata

### 3.1 Track data
Maximum 16 songs with 3 tracks each; shared tables and 127 sectors.
Values represent loops, sectors, and transposition commands.

### 3.2 Sector data (= patterns in V1 terminology)
Three-column patterns containing:
  - Column 1: note / command
  - Column 2: wavetable pointer
  - Column 3: duration

### 3.3 Wavetable data
Controls instrument initialization with waveform, note, and pointer columns.

### 3.4 Pulsetable data
Three-column pulse modulation programs.

### 3.5 Filtertable data
Similar structure to pulsetable for filter control.

## 4. The filemenu
Packing and relocation options with baseaddress configuration.
Two modes: standard (playroutine included) and gamemusic (playroutine separate).
