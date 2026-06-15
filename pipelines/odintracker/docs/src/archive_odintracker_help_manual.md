---
source_url: https://csdb.dk/getinternalfile.php/154684/OdinTracker113src.zip (file: help/help.in)
fetched_via: direct
fetch_date: 2026-06-15
author: Zed (Zoltán Konyha)
content_date: 2001-04-17
reliability: primary
---

# OdinTracker 1.13 In-Editor Help / Manual

Extracted from `help/help.in` inside `OdinTracker113src.zip`.
This is the complete in-tracker help text shown when pressing F1.

---

## Welcome

Welcome to Odin Tracker 1.13 for C64
released by Zed on 17 Apr 2001.

Use Up/Down/Left/Right to navigate back and forth in this help. Any other key exits.

If the editor happens to hang, restart it with SYS2064 after reset.

---

## Song Structure

The song is structured in the good old tracker style. The orderlist found in the top
left corner contains pattern numbers. Each pattern consists of 3 track numbers and the
transpose values for each of them. You can see these above the pattern display.

---

## Global Keys

These keys work in all editor screens.

```
      SPACE   play song/stop playing
SHIFT+SPACE   play pattern

   F1   show this help
   F2   context help (well, sort of)
   F3   orderlist editor
   F5   pattern editor
   F7   instrument editor
   F4   config menu
   F6   specials menu
   F8   disk menu
  ./,   select instrument
  -/+   inc/dec order position
 C=+I   init SID and player
```

RUNSTOP and SHIFT+RUNSTOP work like TAB and SHIFT+TAB on PC.

### Controlling Voices
```
  C=+1..3   mute/unmute voice 1,2,3
     C=+4   mute/unmute all voices
```

---

## Instrument Editor (F7)

Instrument parameters:

```
  0-1. Attack/Decay/Sustain/Release
    2. Wave table start: index of first element in wave table.
    3. Wave table end: index of last element in wave table.
    4. Wave table loop: if the player has reached the end index,
       it continues from this index. If you want no loop, set end=loop.
  5-7. Arpeggio table start/end/loop: All similar to wave table.
    8. Vibrato delay: number of ticks before starting instrument vibrato.
    9. Vibrato depth/speed: high nybble is depth, low nybble is speed.
       Larger number means deeper and faster vibrato.
   10. Pulse width: 8 MSBs of initial pulse width.
   11. Pulse speed: value added to the 8 LSBs of pulse width in each tick.
   12. Pulse limits: high nybble is 4 MSBs of lower limit,
                     low nybble is 4 MSBs of upper limit.
13-15. Filter table start/end/loop: All similar to wave/arp table.
```

### Wave Table
The wave table bytes are dumped to SID waveform registers in each tick.
When $FF is found in the wave table, waveform and ADSR parameters are set to 0.
This helps creating sharp short sounds.

### Arpeggio Table
The arpeggio table bytes are added to the note, so looping $00,$04,$07 creates a
major chord. Arpeggio bytes >= $80 are absolute note values; note is set to byte-$80.
Not even track transpose is added to absolute arpeggio values.

### Filter Table
Select filter type with track effect F9x, filter input and resonance with effect Exx.
The filter cutoff frequency's 8 MSBs will be read from the filter table using
start/end/loop indices specified in the instrument you select with FEx.
Effect Cxx can override the filter table cutoff frequency.

NOTE: Instrument 0 cannot be defined.

### Instrument Editor Keyboard
```
Moving around:
  CURSORS,HOME   as expected
       RUNSTOP   next field
      SHIFT+RS   previous field
     =/SHIFT+=   page up/down in tables
        RETURN   go to wave/arp/filter table (and back)
          C=+N   edit instrument name
           ./,   select instrument
      INST/DEL   in tables only

Copying instruments:
  C=+X   cut instrument
  C=+C   copy instrument
  C=+V   paste instrument

Keyjazz:
        CTRL+1..7   select octave
  SHIFT+Z..M,Q..P   test instrument

Editing filter table:
  C=+B/C=+E   mark block begin/end
       C=+R   unselect block
  C=+Q/C=+A   increment/decrement data in block
       C=+F   fill block with data linearly interpolated between block begin/end
```

---

## Pattern Editor (F5)

Looks like any other tracker: note, instrument, effect, and effect parameter for all
3 voices. You edit separate tracks (unlike MOD). The track number and transpose value
appear above the track's data. Transpose $0C is an octave up, $8C is an octave down.

### Pattern Editor Effects

```
0  Do nothing.
1  If parameter<$80: slide down; else slide up by parameter-$80.
2  Set pulse width. Parameter is 8 MSBs of pulse width.
3  Slide to note. Just like in MOD.
4  Vibrato. High nybble is depth, low is speed. Temporarily overrides instrument vibrato.
5  Set pulse speed. See instrument editor.
6  Set pulse limits. See instrument editor.
7  Set Attack/Decay.
8  Set Sustain/Release.
9  Set waveform. Overrides wave table.
A  Arpeggio. Parameters like in MOD. Overrides arpeggio table.
B  Order jump. Just like in MOD.
C  Set filter cutoff frequency. Parameter is 8 MSBs of frequency. Overrides filter table.
D  Pattern break. Parameter is hex (unlike in MOD).
E  Filter resonance/input control. High nybble is resonance; bit 0,1,2 enable filter
   for voice 1,2,3.
F  If parameter<$80: set speed. Speed 0 stops the player.
   If parameter=$8x: set global volume to x.
   If parameter=$9x: set filter mode.
     bit 0: low pass, bit 1: band pass, bit 2: high pass,
     bit 3: cut off voice 3's output.
   If parameter=$Ax: fine slide down.
   If parameter=$Bx: fine slide up.
   If parameter=$Cx: note cut.
   If parameter=$Ex: select instrument that controls the filter cutoff.
   If parameter=$Fx: set hard restart ticks to x. See tips.
```

### Pattern Editor Keyboard
```
Moving around:
   CURSORS,HOME   as expected
        RUNSTOP   next voice
  SHIFT+RUNSTOP   previous voice
      =/SHIFT+=   page down/up
       INST/DEL   as expected
      \/SHIFT+\   del/ins in all tracks
         RETURN   play from current row

Entering notes:
        CTRL+1..7   select octave
        Z..M,Q..P   enter notes
  SHIFT+Z..M,Q..P   keyjazz
                /   enter note off
                ^   delete note/effect
              ./,   select instrument
        _/SHIFT+_   inc/dec cursor step

Editing song structure:
   */@   inc/dec pattern for current order
   ;/:   inc/dec track for current voice
  C=+Y   enter track number for voice

Editing track transpose:
  C=+W/C=+S   inc/dec track transpose
       C=+D   enter track transpose

Copying effects:
  C=+G/C=+F   grab/drop effect

Selection keys:
  C=+B/C=+E   mark block begin/end
       C=+T   select whole track
       C=+R   unselect block

Block operations:
       C=+X   cut block
       C=+C   copy block
       C=+V   paste block (overwrite)
       C=+M   paste block (mix)
  C=+Q/C=+A   transpose block up/down (all instruments)
  C=+P/C=+L   transpose block up/down (current instrument only)
       C=+Z   undo last block operation
```

### Pattern Editor Tips

- If there is no instrument in the track besides a note, instrument vibrato and pulse
  width will not be reset.
- To avoid entering an instrument number at the same time as a note, select instrument 0.
- The Gate bit in SID is released when the wave table element has bit 0 clear, and also
  when a note off is found in the track.
- To create long sounds, set bit 0 to 1 in each wave table element for the instrument,
  and enter a note off when you want to start decaying.
- Effect FFx sets the number of ticks for hard restart before the new note (per-voice).
  Default value is 2 ticks. FF0 disables hard restart and ties notes.
  Hard restart is always disabled when slide-to-note effect is used.
- Reuse tracks (with track transpose) to save memory. Each track costs 192 bytes.
- Use absolute arpeggio for drums so they do not get transposed.
- **IMPORTANT:** Effects don't remember their parameters like in MODs. Always enter
  parameters! E.g. "300" does not continue sliding but stops sliding.

---

## Orderlist Editor (F3)

256-element orderlist. Most editing done from pattern editor with -/= and */@.

```
Moving around:
   CURSORS,HOME   as expected
       INST,DEL   as expected
      SHIFT+A,Z   page up/down
      =/SHIFT+=   page up/down, too
  SHIFT+Q,W,E,R   go to position $00,$40,$80,$C0

Enter order numbers using 0-9,A-F or use */@.
```

---

## Config Menu (F4)

Set up colours. SHIFT+1..4 loads default colour sets.

---

## Specials Menu (F6)

- Clear song: clears tracks, patterns, and orderlist but keeps instruments.
- Replace instruments in a set of tracks or patterns.
- Swap tracks in a set of patterns.
- Song start positions: list first orderlist indices for subsongs (packed songs only).
  Use effect Bxx to loop the songs. Put $FF after last position used.

---

## Disk Menu (F8)

### File Format Note
The file format changed in version 1.1x. Old format (1.0x) songs must be loaded
using "Import 1.0x song". WARNING: Filter settings not imported; cannot load 1.1x+
format back into 1.0x.

### Saving
Save song: saves memory from $4000 to the end of the last track used, with no player
routine. Songs are saved RLE-packed to save space.

Read/write tracks: enables remixing songs.

### Packer/Relocator
WARNING: Packed songs CANNOT be loaded back into the tracker! Keep unpacked copies.

Before packing:
- Put $FF after the last position used in the orderlist and song start positions list.
- Unused tracks are automatically discarded.
- Unused instruments are NOT remapped; use a continuous block to minimize file size.

Relocatable player: relocate to page boundaries. Can save player + tracks as one file
or in separate files for split-memory layouts.

### Player API (from packed songs)
```
Init: LDA <songnumber>
      JSR $xx00
Play: JSR $xx03
Stop: JSR $xx06
```
(xx = relocated page)

Player uses zero page $FB-$FE, takes ~$30 rasterlines.

---

## Contact (from help text)

http://www.inf.bme.hu/-zed/tracker
mailto:zed@inf.bme.hu

"Wotan mit uns."
