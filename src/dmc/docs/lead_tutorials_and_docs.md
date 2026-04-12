---
source_url: https://web.archive.org/web/20201231113135/https://tnd64.unikat.sk/music_scene.html, https://cadaver.github.io/rants/music.html, https://chipflip.wordpress.com/2009/08/17/note-duration-in-chipmusic-software/, https://silo.tips/download/demo-music-creator-40
fetched_via: wayback 2020-12-31
fetch_date: 2026-04-11
author: Richard Bayliss, Rio/Rattenrudel (TND64 tutorial); Lasse Oorni / Cadaver (cadaver.github.io); Anders Carlsson / goto80 (chipflip); unknown (C64 Turkiye)
content_date: 2009-07-23 (TND64 last updated); 2009-08-17 (chipflip); 2004-02 (C64 Turkiye issue)
reliability: primary
---

# DMC Research: Tutorials and Documentation

Fetched 2026-04-11. Four leads investigated.

---

## 1. TND64 Music Scene Tutorial (Richard Bayliss & Rio/Rattenrudel)

**URL:** http://www.tnd64.unikat.sk/music_scene.html (server returned 500)
**Wayback Mirror:** https://web.archive.org/web/20201231113135/https://tnd64.unikat.sk/music_scene.html (fetched successfully)

Last updated: 23rd July 2009. Comprehensive tutorial covering DMC V4.0 and V7.0 (sections 2.x) and DMC V5.0 (section 3.x). Written by Richard Bayliss and Rio/Rattenrudel.

### DMC Version History

- **GMC** (Game Music Creator) -- predecessor, also by Brian of Graffity
- **DMC V2.1** -- early version (by Graffity)
- **DMC V4.0** -- most widely used (by Graffity). Tutorial focuses on this.
- **DMC V5.0** -- "complete other music editor", more difficult. Different sound editor layout.
- **DMC V5.0+** -- updated by CREAMD/C64.SK
- **DMC V7.0** -- by Graffity + Unreal. Based on DMC V4 code with special functions (trace play mode).

### DMC V4/V7 Sound Editor -- Instrument Parameters

Up to 23 ($16) instruments. Parameters per instrument:

| Parameter | Description |
|-----------|-------------|
| AD | Attack/Decay (4-bit each, $0-$F) |
| SR | Sustain/Release (4-bit each, $0-$F) |
| L (before P) | Pulse limit -- min/max pulsewidth borders for modulation. Higher = narrower swing. 7 = no change. |
| P | Initial pulsewidth ($0-$F). 0=low, 8=middle, F=highest. |
| SPEEDS | 6 nibble values (each $0-$F) for PWM speed table. Alternates direction at borders. 0 = stop. |
| L (after SPEEDS) | PWM fine-speed tuning ($0-$F). Added to the 6-step speed values. |
| F | Filter set number ($0-$F). References a filter defined in Filter Editor. |
| V1 | Vibrato 1: high nibble = pause before vibrato starts, low nibble = range of pitch swing |
| V2 | Vibrato 2: 8-bit value for modulation with V1's range parameter |
| ## | Wavetable start point -- index into the shared wavetable where this instrument begins |
| FX | 8-bit FX flags (see below) |

### FX Byte Flags (CRITICAL)

FX is an 8-bit value. Each bit controls a specific feature:

**Low nibble (bits 0-3):**

| Bit | Name | Meaning |
|-----|------|---------|
| 0 | DRUM EFFECT | Pitch will be ignored in sector editor; in wavetable, pitch values step in higher range |
| 1 | NO FILT RES | For every played note, filter will NOT be reset anymore (global filter continues) |
| 2 | NO PULS RES | For every played note, pulse will NOT be reset anymore (global PWM continues) |
| 3 | NO GATE FX | Holds your note down until a GATE is set (suppresses automatic gate-off) |

**High nibble (bits 4-7):**

| Bit | Name | Meaning |
|-----|------|---------|
| 4 | HOLDING FX | Note will not be released (sustain indefinitely) |
| 5 | FILTER FX | Activates the filter defined by F parameter |
| 6 | DUAL EFFECT | Plays wavetable at half speed |
| 7 | CYMBAL FX | Adds short noise burst in front of a sound |

**Common FX values:**
- `$01` = DRUM EFFECT
- `$08` = NO GATE FX
- `$20` = FILTER FX (activate filter)
- `$22` = FILTER FX + NO FILT RES (global filter for following notes)
- `$28` = FILTER FX + NO GATE FX
- `$A1` = CYMBAL FX + FILTER FX + DRUM EFFECT

Bits can be freely combined. Example from tutorial: `$2A` = bit 5 (FILTER FX) + bit 1 (NO FILT RES) + bit 3 (NO GATE FX).

### Wavetable Format (DMC V4)

The wavetable is a **2-column** format displayed as three columns on screen:

| Column | Name | Content |
|--------|------|---------|
| ## | Position | Row index in the shared wavetable |
| WV | Waveform | Waveform byte OR loop/jump command |
| FX | Note offset | Relative or absolute note value (pitch parameter) |

**WV column byte layout** (identical to SID control register $D404):

Low nibble (bits 0-3):
- Bit 0: TEST bit (Key-Bit, activating ADSR of oscillator)
- Bit 1: SYNC bit (synchronize fundamental frequency of 2 oscillators)
- Bit 2: RING bit (ring modulation, only for triangle oscillator)
- Bit 3: GATE bit

High nibble (bits 4-7):
- Bit 4: Triangle
- Bit 5: Sawtooth
- Bit 6: Pulse
- Bit 7: Noise

**Standard waveform values:**
- `$11` = Triangle + gate
- `$21` = Sawtooth + gate
- `$41` = Pulse + gate (requires P > 0)
- `$81` = Noise + gate
- `$31` = Triangle + Sawtooth + gate
- `$51` = Triangle + Pulse + gate
- `$61` = Sawtooth + Pulse + gate
- `$71` = Triangle + Sawtooth + Pulse + gate

**Loop/jump commands** in WV column:
- Values `$90`-`$9F`: Loop back `x` steps (where x = low nibble)
- Values `$A0`-`$AF`: Loop back `x + 16` steps
- Values `$B0`-`$BF`: Loop back `x + 32` steps
- And so on -- each high nibble increment adds 16 more steps to the loop range
- This allows jumping to ANY wavetable start point

**FX column** (second data column): Contains the note offset.
- For arpeggios: relative note number (`$00` = unison, `$03` = minor third, `$04` = major third, `$07` = fifth, `$0C` = octave)
- For drums (FX bit 0 set): pitch values step in a higher range (e.g., `$FF` for high-pitched noise)
- `$00` beside a waveform = play at the note's own pitch

**Example -- Minor chord arpeggio:**
```
## WV FX
00 21 00  ; sawtooth+gate, root note
01 21 03  ; sawtooth+gate, minor third
02 21 07  ; sawtooth+gate, fifth
03 21 0C  ; sawtooth+gate, octave
04 94 00  ; loop back 4 steps
```

**Example -- Drum sound:**
```
0C 81 FF  ; noise+gate, high pitch
0D 81 FF  ; noise+gate, high pitch
0E 41 0C  ; pulse+gate, octave
0F 41 0A  ; pulse+gate
10 41 02  ; pulse+gate, low
11 91 00  ; loop back 1 step (sustain)
```

### Filter Editor Parameters

| Parameter | Description |
|-----------|-------------|
| R | Resonance/Rate ($0-$F, F = maximum) |
| T | Filter type bitmask: bit 0 = low pass, bit 1 = band pass, bit 2 = high pass. Combinable (e.g., 3 = LP+BP, 7 = all). |
| ## | CutOff frequency initial value |
| RT | Repeat step position ($01-$05). After full pass, loop back to this step. Values > 6 are buggy. |
| ST | Stop value -- stop envelope when cutoff reaches this value |
| S1-S6 | Speed values: $00=nothing, $01-$7F=up (slow..fast), $80=mid, $81-$FF=down ($FF=slowest down, $81=fastest down) |
| X1-X6 | Duration values for each speed step |

The 6 S/X pairs form a filter envelope that loops. Each step applies its speed for its duration, then moves to the next step.

### Sector Editor Commands (Pattern Data)

| Command | Key | Description |
|---------|-----|-------------|
| DUR.xx | C= + D | Duration between note steps. xx = number of frames between notes. |
| SND.xx | C= + S | Select instrument number xx |
| GLD.xy | C= + G | Glide/slide. Two modes (see below) |
| VOL.0x | C= + V | Set volume directly (only works without Attack/Decay). 00 resets to instrument ADSR. |
| SWITCH | C= + X | Played notes will not be reset by ADSR until next SWITCH or END |
| -GATE- | GBP key | Set gate for a played note (releases the note) |
| END! | = key | End of sector, switch to next sector in track |
| ------ | - key | Empty step (counts as a step for timing) |

**Glide modes:**
1. **Slide from current note** (`GLD.1y`): x=1, y=speed ($0=none, $1=slowest, $F=fastest). Next note in sector is the destination. Duration must be long enough for slide to complete.
2. **Glide between two notes** (`GLD.0y`): x=0, y=speed. The TWO notes following the GLD command are source and destination -- they count as ONE step together.

**Duration and timing:**
- DUR, SND, GLD, VOL, SWITCH are commands that do NOT count as steps
- Notes, GATE, and `------` (empty steps) ARE counted as steps
- Total sector duration = sum of all step durations
- All channels must have equal total sector duration (or exact multiples/halves) to stay synchronized
- With tune speed S: `Total duration = (S + 1) * sum_of_DUR_values_per_note`

### Track Editor Commands

| Command | Description |
|---------|-------------|
| TR+xx / TR-xx | Global transpose up/down for following sectors in this track |
| -END- xx | Jump to track position xx (loop point). DMC7 bug: always jumps to first line. |
| STOP! | Stop this track |

### Player Modes

- NORMAL Player (C= + 1): init $1000, play $1003
- DOUBLE Player (C= + 2): play $1006
- TRIPLE Player (C= + 3): play $1006
- QUADRO Player (C= + 4): play $1006
- QUINTUPLE Player (C= + 5): play $1006

Higher modes use $1006 instead of $1003 for the play address.

### DMC V4 Packer

Integrated packer relocates tune to $1000. No external packer needed. Init at $1000, play at $1003 (normal) or $1006 (multi).

### DMC V5 Sound Editor

DMC V5 instrument parameters:

| Parameter | Description |
|-----------|-------------|
| AD | Attack/Decay |
| SR | Sustain/Release |
| WV | Wavetable start index |
| PU | Pulse table start index |
| FL | Filter table start index |
| V1 | Vibrato #1 (delay) |
| V2 | Vibrato #2 |
| V3 | Vibrato #3 (special modes) |

DMC V5 has **separate** wavetable, pulse table, and filter table (unlike DMC V4 which integrates pulse/filter into instrument parameters).

### DMC V5 Wavetable Format

**2-column format**: each entry is `WV` + `note_offset` (same as DMC V4):
```
04 2100   ; sawtooth+gate, root
05 2100   ; sawtooth+gate, root
06 2103   ; sawtooth+gate, minor third
07 2103   ; sawtooth+gate, minor third
08 2107   ; sawtooth+gate, fifth
09 2107   ; sawtooth+gate, fifth
0A 9004   ; loop back to position 04
```

Loop command: `$90xx` jumps back to position xx.

### DMC V5 Sector Commands (additional vs V4)

| Command | Key | Description |
|---------|-----|-------------|
| ADSR.xx | Shift+Y | Change ADSR mid-sequence |
| FILT.xy | Shift+F | Set filter (x=type 1/3/4/5, y=volume). Required for filter to work in V5. |
| FREQ.xx | Shift+Q | Set filter frequency |
| SLD.xx | Shift+S | Slide command |

V5 filter note: filtered sounds should use track 3 for proper operation.

### DMC V5 Packer

Two packers available:
1. Graffity original packer (load packer, load music, G $2E00, enter target address like $1000)
2. Iceball/Motiv8 packer (simpler interface)

Packed tunes: init $1000, play $1003.

---

## 2. Cadaver's Music Rant (Lasse Oorni / GoatTracker author)

**URL:** https://cadaver.github.io/rants/music.html (fetched successfully)

### Wave Table Format Resolution

Cadaver describes waveform/arpeggio tables as containing **byte pairs**: "the other byte is what to put in the waveform register and the other is the note number; either relative (arpeggios) or absolute (drumsounds)."

**This confirms DMC's 2-column wave table format.** The "single-byte wave table" description from some sources likely refers to the waveform column only, not the full table entry. Both DMC V4 and V5, as well as GoatTracker, JCH, and other advanced players use 2-column (waveform + note) wavetables.

### Hard Restart Methods Compared

**Old method (Rob Hubbard era):**
- Clear gate bit and set ADSR to 0 a couple of frames before note end (e.g., when duration counter = 2)
- On new note, write registers in order: Waveform - Attack/Decay - Sustain/Release
- Works on both PAL and NTSC
- Not sensitive to timing

**Modern "testbit" method (JCH, DMC):**
- 2+ frames before next note: set ADSR to preset ($0000, $0F00, or $F800), clear gate bit
- Frame 1 of new note: write Attack/Decay and Sustain/Release FIRST, then write $09 to waveform (testbit + gate)
- Frame 2 of new note: write actual waveform value -- note is actually heard
- **Critical: AD/SR must ALWAYS be written before waveform**
- **PAL only** -- does not work reliably on NTSC
- Gives a nice sharp sound

### Other Technical Details from Cadaver

**Sequence data encoding** (GoatTracker example, similar concept to DMC tracks):
- $00-$7F = pattern numbers
- $80-$BF = transpose command
- $C0-$FE = repeat command
- $FF = jump command + position byte

**Pattern data encoding** (GoatTracker):
- $00-$5D = note numbers (with command + data bytes following)
- $5E = keyoff, $5F = rest (with command bytes)
- $60-$BD = note numbers (WITHOUT command bytes)
- $BE = keyoff, $BF = rest (without command bytes)
- $C0-$FE = long rest ($FE = 2 rows, $FD = 3 rows, etc.)
- $FF = end of pattern

**Frequency slides:** Rob Hubbard method uses delta between neighboring note frequencies as basis for vibrato/slide speed, to compensate for octave-dependent speed differences.

**Tied notes:** Don't reset gate, don't do hard restart, don't reset pulsewidth -- just change frequency. GoatTracker implements as infinitely fast toneportamento.

**Filter control:** Only one filter in SID, so either one voice controls it at a time, or filter is operated independently via pattern commands only.

**Sound effects:** Can interrupt music on a voice; underneath, song playback continues. During SFX, skip full music channel routine but keep note duration timing and sequencer position.

---

## 3. DMC V4.0 Documentation (C64 Turkiye)

**URL:** https://silo.tips/download/demo-music-creator-40
**Status:** Page loads but content is behind a download wall. Only metadata and a preview were accessible.

### What Was Extractable

The document is from **C64 Turkiye** magazine issue #$04 (February 2004). It is reportedly a Turkish-language manual for DMC V4.0.

Key points from the preview/metadata:
- Up to 8 different pieces per music file (tune switching)
- TIMER shows playback position
- RTIME displays raster time consumption (XX:YY format)
- 3 tracks (channels)
- Each track: 256 rows (00-FF)
- 64 sectors maximum (00-3F) for pattern storage
- Each sector: 256 rows for note/command data
- Filter frequency range: 30Hz-12kHz with 12dB/octave rolloff
- SID provides 4 waveforms (triangle, sawtooth, variable pulse, noise) per oscillator, 3 oscillators
- Attack range: 2ms-8s, Decay/Release range: 6ms-24s
- Chord construction uses offset values: 00-03-07-0C (minor), 00-04-07-0C (major)

**Note:** The full PDF could not be downloaded. The technical content largely overlaps with the TND64 tutorial which is far more detailed.

---

## 4. Chipflip Duration Analysis

**URL:** https://chipflip.wordpress.com/2009/08/17/note-duration-in-chipmusic-software/ (fetched successfully)

Author: Anders Carlsson (goto80)

### DMC Duration System

DMC (credited to Brian & DJB, 1997 for V5.1) is classified as an **"editor"** rather than a **"tracker"**:

- **Trackers** (JCH, SoundMonitor) use fixed step lengths -- every row takes the same amount of time, all channels are synchronized by row number
- **Editors** (DMC) use **explicit duration encoding** -- each note has a DUR.xx command specifying how long it lasts

Key insight: "step #8 (ADR.00) in this channel, might not be the same place in time as step #8 in the other channels." Channels maintain independent timing.

The author "cursed a lot when using this" because the decoupled timing makes it harder to align channels, but it enables polyrhythmic patterns without a unified master clock.

### Duration vs Step-Sequencer Comparison

In a tracker (step-sequencer), the position in the pattern directly maps to time. Row 0 = frame 0, row 1 = frame N, etc. Duration is implicit in the number of rows between notes.

In DMC (duration-based), the DUR command sets the time between notes explicitly. This means:
- More memory-efficient (no need for empty rows)
- Better raster timing (fewer rows to process)
- But harder to keep channels synchronized -- composer must manually ensure total durations match

### C64 ADSR Bug

The article notes a critical SID hardware issue: "You can never be completely sure that an instrument will play with the same volume envelope" because ADSR behavior depends on the state left by the previous instrument. This is why hard restart methods (old and testbit) exist.

### Historical Context

Peter Samson's Harmony Compiler (1960-1964) for PDP-1 used text notation like "7t4" (note 7, duration 4) -- the same explicit-duration concept that DMC would later use.

---

## Summary of Key Findings for Pipeline Development

### Wave Table Format: RESOLVED

**DMC V4 and V5 both use 2-column wave tables** (waveform byte + note offset byte). This is confirmed by:
1. TND64 tutorial: "The first column shows the wavetable position. The second column have to be filled up with Waveforms or Commands. Accessory parameters will be written in the last column."
2. All tutorial examples show 2-byte entries (e.g., `21 00`, `81 FF`, `41 0C`)
3. Cadaver independently confirms byte-pair wavetables for this class of player
4. DMC V5 examples also show 2-byte format (e.g., `2100`, `9004`)

Any source claiming "single-byte wave tables" for DMC V4 is either wrong or referring to the waveform column in isolation.

### FX Flags: COMPLETE

All 8 bits documented with exact meanings. This is essential for the dmc_parser.py instrument extraction.

### Duration System: CONFIRMED

DMC uses explicit DUR.xx commands, NOT fixed step lengths. Commands (DUR, SND, GLD, VOL, SWITCH) don't count as steps; only notes, GATE, and empty rows count. This has direct implications for the dmc_to_usf.py converter.

### Hard Restart: TESTBIT METHOD

DMC uses the modern testbit method ($09 written to waveform register), PAL-only. The V2 player will need to replicate this exactly for accurate reproduction.

### Key Addresses

- DMC V4/V7 packed: init $1000, play $1003 (normal) or $1006 (multi-speed)
- DMC V5 packed: init $1000, play $1003
