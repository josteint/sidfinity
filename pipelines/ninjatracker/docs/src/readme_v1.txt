---
source_url: https://cadaver.github.io/tools/ninjatrk.zip (readme.txt)
fetched_via: curl
fetch_date: 2026-06-17
author: Lasse Oeorni (Cadaver)
content_date: 2009-09
reliability: primary
---
NinjaTracker V1.1
-----------------


Version history
---------------

V1.05 - Slide duration calculator added
      - Allow editing of sector 0 (init-sector)

V1.1  - Hardrestart is more solid (set both AD,SR to $00) and same in both
        standard & gamemusic versions
      - INS in pulse & filtertable inserts a 00,00-row, instead of 90,00 as in
        wavetable
      - Pulse/filter-pointers in wavetable are adjusted when INS/DEL is used in
        pulse- or filtertable
      - Movement in patterns speed-optimized (no unnecessary workpattern->
        pattern conversion anymore)


Instructions (also as online help within the program)
-----------------------------------------------------

1. Introduction

NinjaTracker is a 11-rasterline max. music editor, with simple but flexible
musicdata and small playroutine.

This editor is only recommended if you have strict rastertime/memory require-
ments and know what you're doing! Customization is allowed and encouraged!

WWW: http://covertbitops.c64.org
Email: loorni@student.oulu.fi


2. How to use

NinjaTracker is operated on keyboard; here are the general keys:

  Cursors     Move around
  Ins/Del     Delete rows
  Shift+Ins   Insert rows
  0-9, A-F    Edit hexadecimal data
  Shift+1,2,3 Enter tracks 1,2,3
  Shift+4     Enter sector (pattern)
  Shift+5,6,7 Enter wave/pulse/filttbl.
  Shift+Z     Fast scroll up
  Shift+X     Fast scroll down
  F1          Play from song beginning
  F3          Stop playing
  F5          Play from selected pos.
  F7          Toggle fastforward mode
  F8          Enter help screen
  <-          Enter disk menu


2.1 Track editor special keys

  ;:          Select song to work on
  SPACE       Mark playing position
  RETURN      Go to sector under cursor


2.2 Sector editor special keys

  ,.          Select octave
  ;:          Select sector to work on
  ZSXDCVGBH.. Enter lower octave notes
  Q2W3ER5T6.. Enter upper octave notes
  Shift+D     Calculate slide duration
  Shift+W     Wave command
  Shift+A     AD command
  Shift+S     SR command
  Shift+F     Flt command
  Shift+C     Copy sector
  Shift+V     Paste sector
  Shift+N     Transpose halfstep down
  Shift+M     Transpose halfstep up
  SPACE       Rest / empty (zero) column
  RETURN      Go to wavetable entry
              under cursor (when in wave
              column)

SPACE or RETURN also silences test note.

To use slide duration calculator, you must place the cursor on a sector line
between 2 notes, containing a wavetable pointer to a slide program. Example:

SECTOR   C-2 02 02 WAVETABLE 91 40 30
Cursor-> --- 30 08 (pos. 30)
         G-2 04 10

Here we see a slide from C-2 to G-2, the G-2 being a 'tie' note. The slide
program at wavetable pos. 30 uses speed 40 and loops infinitely.

When you press Shift+D, the program will calculate the correct duration for the
slide. If it is > 65, or there is some other error, the screen will flash red.


3. The musicdata

3.1 Track data

There can be a maximum of 16 different songs (subtunes), each with 3 tracks.
All songs share the same tables & 127 sectors.

Values in the track data:

  00    Loop (followed by loop position)
  01-7F Sector to play
  80-BF Transpose upwards
  C0-FF Transpose downwards

- Sector 00 has been reserved for song initialization and therefore can't be
  referenced in the track data.
- A transpose command must be always followed by a sector number.
- Imagine the transpose being added to note number and then ANDed with 7F;
  therefore transpose FF is one halfstep down and 81 is one halfstep up.
- A song that plays only once can be realized by creating one empty sector
  (with just one rest note) and looping to it indefinitely.


3.2 Sector data

A sector (pattern) consists of three columns; from left to right they are:

- Note/Command
- Wavetable pointer/Command parameter
- Duration (using decimal notation)

A note can range from C-0 to F-7 (use transpose to reach the highest notes).
When a note is encountered, it will use the last wavetable pointer remembered,
or a new wavetable pointer if one exists on the wave column at same position.

If duration column is empty then the last remembered duration will be used.
Duration minimum is 2 and maximum is 65. For longer notes, use the rest command.

Note: the packer isn't 'smart': to save memory, you must make sure yourself that
there are no unnecessary duplicate values.

The commands:

  === Rest, do nothing (except change
      wavetable pointer, if exists)
  Wav Change channel waveform (useless
      if wavetable is also controlling
      the waveform)
  AD  Change channel's Attack/Decay
  SR  Change channel's Sustain/Release
  Flt Change filtertable pointer

Note: Wav,AD,SR,Flt imply a 'rest' in addition to the action they perform.

An example. Let's assume that wavetable pointer 01 contains an instrument and 0A
contains a vibrato loop (more of these later)

  C-3 01 12 Play note, dur. 12 frames
  === 0A -- Begin vibrato program + rest
  SR  6A -- Set sustain & release + rest
  Wav 40 36 Set waveform + rest
  D-3 01 12 Waveptr. 01 needed again now
  E-3 -- -- but not for subsequent notes
  F-3 -- -- with same instrument


3.3 Wavetable data

The wavetable controls note/instrument initialization fully (no separate instr.
data.) It consists of 3 columns, from left to right:

- Waveform/command column
- Note/slidespeed column
- Pointer to next step-column

The waveform column values are:

  00    Hardrestart note init
  01    Legato note init
  02    Set ADSR (2nd frame of noteinit)
  03-8F Waveform & Note change
  90    Note without waveform change
  91-FF Pitch slide (duration as
        negative value)

A complete note init requires 3 steps, an example follows below. Note that
00,01,02 always go to the step directly below because the 'next'-column is used
for parameters. Furthermore, 02 assumes that a normal Wave/Note step follows
(executed on the same frame!)

Never put 00 or 01 to anywhere else but the first step of a waveprogram or play-
back will go out of time!

  Hardrestart + Set Pulse & Filter
  |
  |  Pulse initial value (00=unchanged)
  |  |
  |  |  Filt. initial value (00=unchg.)
  |  |  |
  00 01 01
  02 04 8A - ADSR parameters (048A)
  41 00 04 - Normal Waveform/Note step

The hardrestart sets waveform 00 and sustain/release FF. To avoid ADSR bug,
don't use full (F) sustain or release!

An example of pitch slides (a vibrato program, starting from step 01):

  F8 00 02 Freq. unchanged for 8 frames
  FD 02 03 Speed 2 slide up    3 frames
  FD FC 04 Speed 4 slide down  3 frames
  FD 04 03 Speed 4 slide up    3 frames,
           loop back to previous step

Notes 00-5F are relative notes and 80-DF are absolute (independent of note base
pitch). Examples of wave/note changes, each example starting at step 01:

  21 00 02 Sawtooth, note's base pitch

  81 C8 02 High absolute noise
  41 00 03 Pulse, note's base pitch

  90 00 02 A looping major arpeggio with
  90 04 03 no waveform changes (now you
  90 07 04 can use Wav-command in the
  90 0C 01 sector data for gate-off)

Note: step 00 is reserved for pitch slide, using it in the next step column
causes unpredictable results (likely, a previous pitch slide continues).

To terminate a waveform program, it's preferable to jump into a long, zero
speed pitch slide, that loops itself indefinitely (step 01 in this example):

  91 00 01


3.4 Pulsetable data

The pulsetable consists of 3 columns, from left to right:

- Duration column
- Speed column
- Pointer to next step-column

A value >= $80 in the duration tells to set the pulse to the value indicated
by speed column. Otherwise it will add speed column to pulse for amount of
frames indicated by duration.

Because of the peculiar nybble-reversed arithmetic used with pulse, you must
subtract one from all negative speeds (speed FF is the same as 00!)

An example of a pulse program:

  80 10 02 Set pulse to value 20
  40 01 03 Pulse up (speed 1, 64 frames)
  40 FE 02 Pulse down (speed 1, 64 fr.)

Unlike with wavetable, you can use step 00 in the next step-column to end pulse-
table execution.


3.5 Filtertable data

The filtertable consists of the same columns and operates almost in the same
way as the pulsetable.

Duration values > $80 are used to set filter passband, channels to be filtered
and initial cutoff value.

The high nybble of the duration value (highest bit is ignored) is the pass-
band and low nybble is the bitmask of channels to be filtered. Resonance is
hard-coded to F (highest value).

Examples of filter programs:

  91 40 02 Lowpass on Chn1, cutoff 40

  7F 01 03 Up with speed 1, 127 frames
  7F FF 02 Down with speed 1, repeat

  97 20 00 Lowpass on all channels,
           cutoff 20, stop filter

           execution

Note: The first step in the filtertable is used when the song starts.


4. The filemenu

Everything in here should be self-explanatory. When packing/relocating, you
have to choose baseaddress and zeropage baseaddress; 5 zeropage bytes are
used.

Init: LDA #song; JSR <baseadr>
Play: JSR <baseadr+3>


