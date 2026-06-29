GoatTracker v1.53
-----------------

Editor by Lasse Öörni (loorni@student.oulu.fi)
Uses reSID engine by Dag Lem and SDL library.
GoatTracker icon by Antonio Vera.

Distributed under GNU General Public License
(see the file COPYING for details)

Covert BitOps homepage:
http://covertbitops.cjb.net

Official latest GoatTracker version:
http://covertbitops.cjb.net/tools/goattrk.zip

Notice: (Linux users) libbme.a is missing for a reason,
you need to recompile it from source! See chapter 7.


Table of contents
-----------------

1. General information

2. Warnings
2.1 About converting .SIDs to GoatTracker song format

3. Using GoatTracker
3.1 Keyboard commands
3.1.1 General keys
3.1.2 Pattern edit mode
3.1.2.1 Protracker note-entry mode
3.1.2.2 DMC note-entry mode
3.1.3 Song edit mode
3.1.4 Instrument edit mode
3.1.5 Songname edit mode
3.2 Song data
3.3 Pattern data
3.3.1 Using funktempo
3.3.2 Master volume fader
3.4 Instrument data
3.5 Wavetable data
3.6 Filter data
3.7 Changing instrument on the fly
3.8 ADSR & Wavetable examples

4. Using the included utilities
4.1 INS2SND.EXE
4.2 SNGSPLIT.EXE
4.3 MOD2SNG.EXE

5. Using the songs in your C64 programs
5.1 Playroutine 1: Standard
5.2 Playroutine 2: Game (with sound effects)

6. File/data formats description
6.1 GoatTracker song (.SNG) format
6.1.1 Song header
6.1.2 Song order-lists
6.1.3 Instruments
6.1.4 Patterns header
6.1.5 Patterns
6.2 GoatTracker instrument (.INS) format
6.3 Sound effect data format

7. Recompiling

8. Version history


1. General information
----------------------

This program is a tracker-like C64 music editor running on Win32 or Linux
platforms (using the SDL library, see http://www.libsdl.org)

Familiarity with tracker programs in general, hexadecimal notation, and the
C64's audio chip (consult the C64 Programmer's Reference Guide, available at
http://project64.c64.org) are required to successfully utilize this program.

For filesize reasons, precompiled binaries exist only for Win32 platform.

Check also out the separate stereo-SID version!


2. Warnings
-----------

1. Always look at the end of this file for changes! Sometimes keyboard commands
   change etc.

2. Always save your songs in the .SNG-format with F11 key if you plan to
   continue editing! Packed & relocated songs (.PRG/.BIN/.SID) can't be loaded
   back into the editor.

3. Even the reSID emulation is in some cases quite far from the output of a
   real SID. Especially if filters are in use, consider strongly testing your
   tune on a C64 or on a HardSID card. (Using filters has always been
   complicated because every SID tends to sound different.)

4. The editor will stop playing if the song restart position is illegal (beyond
   end of song) but the C64 playroutines will probably hang in that case. So
   don't use that as an endsong-mark. Create instead one empty pattern and set
   it to repeat indefinitely if you want the song to end.

5. Songs made with versions prior to 1.3 will load fine but the effect
   parameters & instrument parameters will be incorrect, as they have changed
   a lot. You have to adjust them manually.

6. From version 1.3 onwards arpeggio & vibrato use the same internal register
   for calculations. Mixing arpeggio & vibrato in the same note may cause
   unexpected results.

7. As of version 1.4, filter parameters have changed. Old songs need to be
   adjusted for this.

8. As of version 1.5, hard restart has changed. Your songs might sound quite
   totally different..


2.1 About converting .SIDs to GoatTracker song format
-----------------------------------------------------

This has been asked of me many times. First of all let me say that I won't
write such a converter. To know why, one must know what .SID-files contain.
They aren't any "standard" music module format like MOD, XM or IT but instead
they contain a playroutine in C64 machine language and the binary data that
the playroutine uses. It's entirely up to the music composer/programmer how the
data is stored, what effects can be used etc. There are probably hundreds of
different C64 playroutines (considering all different versions) and very few of
them are documented, so severe reverse-engineering would be required to
understand the way each playroutine operates and stores data.

Furthermore, even if the music data was understood and extracted the effects
and instruments would likely be different than in GoatTracker, so the
conversion would often be "lossy" in some ways and sound worse. It was often
popular to store note durations instead of constant-step "patterns" so even the
conversion of notes to GoatTracker patterns could be problematic.

I hope I didn't discourage too much, if someone else is eager to write a .SID
-> .SNG convertor for even one playroutine, go ahead :-)

Another approach to making such a convertor would be to emulate the execution
of the playroutine, and after each frame, look at the SID register values. By
looking for gatebit going off->on note starts could be recognized, by looking
at the frequency register the note pitches could be recognized. And by looking
at the waveform changes, wavetables for each instrument could be reconstructed.
This would be complicated as well, but completely general. As far as I know,
SID2MIDI (http://www.geocities.com/SiliconValley/Lakes/5147/sid2midi.html) by
Michael Schwendt works somewhat like this.


3. Using GoatTracker
--------------------

Command line options:

/Axx Set hard restart ADSR parameter in hex. DEFAULT=0f00
/Bxx Set sound buffer length in milliseconds DEFAULT=200
/Cxx Use CatWeasel MK3 PCI SID (0 = off, 1 = on)
/Exx Set emulated SID model (0 = 6581 1 = 8580) DEFAULT=6581
/Ixx Set reSID interpolation (0 = off 1 = on) DEFAULT=off
/Hxx Use HardSID (0 = off, 1 = HardSID ID0 2 = HardSID ID1 etc.)
/Kxx Note-entry mode (0 = PROTRK. 1 = DMC) DEFAULT=PROTRK.
/Mxx Set sound mixing rate DEFAULT=44100
/R   Set hard restart length (1 or 2 frames) DEFAULT=2
/Sxx Set speed multiplier (2 for 2x tunes, 4 for 4x tunes etc.)
/N   Use NTSC timing
/P   Use PAL timing (DEFAULT)
/W   Write emulated sound output to a file SIDAUDIO.RAW
/?   Show command line options

Try the command line options if there are any problems. For example, if you
experience choppy audio you can increase audio buffering with /B option. SDL
seems to have trouble with some soundcards under Windows; you might want to
try even a 500ms buffer, or tweak the hardware acceleration level of the
soundcard (from Control Panel).

HardSID support is available with the /H option. (use first HardSID = /H1,
second = /H2 etc., return to emulated output = /H0) You must have the HardSID
drivers and HardSID.DLL installed to use this feature.

CatWeasel MK3 PCI SID support is available with /C option (/C1 to turn on).

Remember to enable normal operation with /S1 when you're finished working with
multispeed-tunes. Multispeeds higher than 2x don't seem to work too well with
the HardSID, because the operating system timers' granularity comes into play.
With emulated output this problem doesn't exist, as the timing is based on
sound buffer sizes.

Hard restart length 1 (/R1) can be unreliable in ADSR operation on full sustain,
but use it if you prefer the sound.

To use the PC64 cable under Windows, check out Daniel Illgen's HardSID-DLL-Clone
at http://home.t-online.de/home/lord_leinad/pages/_work.htm

This program is entirely operated on keyboard. For a list of keyboard commands
press F12 in the tracker or see the table below:

3.1 Keyboard commands
---------------------

NOTE: SHIFT & CTRL are interchangeable in the commands.
You can also use [ ] or ( ) instead of < >.

3.1.1 General keys
------------------

TAB       Cycle between editing modes (forwards)
SHIFT+TAB Cycle between editing modes (backwards)
F1        Play from beginning
F2        Play from current pos.
F3        Play one pattern from current pos.
F4        Stop playing & silence all sounds
SHIFT+F1  Play from beginning                (Follow play)
SHIFT+F2  Play from current pos.             (Follow play)
SHIFT+F3  Play one pattern from current pos. (Follow play)
SHIFT+F4  Mute current channel
F5        Go to pattern editor
F6        Go to song editor
F7        Go to instrument editor
F8        Go to songname editor
F9        Pack, relocate & save PRG,SID etc.
F10       Load song (Pattern/Song/Songname mode) or instrument (Instrument mode)
F11       Save song (Pattern/Song/Songname mode) or instrument (Instrument mode)
F12       Online help screen
INS       Insert row (Press INS/DEL on endmark to change pattern length)
DEL       Delete row
SHIFT+ESC Clear musicdata & set default pattern length
ESC       Exit program

3.1.2 Pattern edit mode
-----------------------

0-9 & A-F   Enter parameters
SPACE       Switch between jam/editmode
RETURN      (or CAPSLOCK) Insert keyoff
BACKSPACE   Insert rest
- +         Select instrument
/ *         Select octave
< >         Select pattern
SHIFT+Q     Transpose halfstep up
SHIFT+A     Transpose halfstep down
SHIFT+CRSR UP,DOWN Mark pattern
SHIFT+CRSR LEFT,RIGHT Select pattern
SHIFT+L     Mark/unmark entire pattern
SHIFT+M,N   Choose highlighting step size
SHIFT+X,C,V Cut,copy,paste pattern
SHIFT+E,R   Copy,paste effects
SHIFT+Z     Cycle autoadvance-mode

There are 2 modes for note entering:

3.1.2.1 Protracker note-entry mode
----------------------------------

This is the default or activated with command line option /K0. There are
two rows of a piano keyboard:

  Lower octave     Higher octave
 S D  G H  K L    2 3  5 6 7  9 0
Z X CV B NM , .  Q W ER T Y UI O P

Octave (0-7) is selected with / and * keys on the numeric keypad.

In this mode there's 2 different autoadvance-modes (the mode can be
seen from the color of the jam/editmode indicator)

GREEN - Advance when entering notes & command-databytes
RED - Do not advance automatically

3.1.2.2 DMC note-entry mode
---------------------------

Activated with command line option /K1, there is one row of piano keyboard

 W E  T Y U  O P
A S DF G H JK L

and octave of a note (sets default octave at the same time) is changed with
number keys 0-7.

In this mode there's 3 different autoadvance-modes:

GREEN - Advance when entering notes, octaves or command-databytes
YELLOW - Advance when entering notes or command-databytes, not octaves
RED - Do not advance automatically

3.1.3 Song edit mode
--------------------

0-9 & A-F   Enter pattern numbers
SPACE       Set start position for F2 key
RETURN      Go to pattern
< >         Select subtune
- +         Insert Transpose down/up command (shown as -/+ in the order-list)
SHIFT+R     Insert Repeat command (shown as "R" in the order-list)
SHIFT+X,C,V Cut,copy,paste orderlist
SHIFT+SPACE Set start position on all channels
SHIFT+RET.  Go to pattern on all channels

3.1.4 Instrument edit mode
--------------------------

0-9 & A-F  Enter parameters
SPACE      Play test note
RETURN     Silence test note (or go to filterparameters, if on the filter num)
- +        Select instrument
/ *        Select octave
SHIFT+X,C,V Cut,copy,paste instrument
SHIFT+H    Toggle hard restart for this instrument
SHIFT+N    Edit instrument name

The test note will be played on the channel you last were on in the pattern
editor. To hear filtering as intended, be sure to play it on a channel that has
been selected for filtering in the filter parameters.

3.1.5 Songname edit mode
------------------------

Use cursor UP/DOWN to move between song, author & copyright strings, and
other keys to edit them.

3.2 Song data
-------------

A song can consist of up to 32 sub-tunes. Each sub-tune has pattern order-lists
for all 3 channels. The pattern-orderlist is a list of patterns to be played
(max. 254 columns long), possible transpose/repeat commands, ended by the RST
(restart) endmark and restart position for that channel.

Transpose up/down is measured in halftones. Transpose up can be 0-14 halftones
and transpose down can be 1-15. Transpose is automatically reset upon starting
the song only (not on the RST endmark).

A repeat command will repeat the pattern following it 1-16 times. A repeat of
16 times is shown as "R0".

3.3 Pattern data
----------------

Patterns are single-channel as there's a pattern-order list for each channel.
A pattern can have variable length, however 80 rows is the maximum. There can
be 208 different patterns in a song.

The explanation of a pattern row:

 Note name
 |
 | Octave
 | |
 | | Instrument number (01 - 1F, or 00 for no change)
 | | |
 | | |  Command (0 - 7)
 | | |  |
 | | |  | Databyte
 | | |  | |
 C-1 00 0 00

Commands 0-4 bear some resemblance to Soundtracker/Protracker/Fasttracker
effects. However, they are different in some ways, so read their
descriptions!!! Note that there is no "databyte 00 uses the last databyte"-
action in the commands.

The "continuous" commands 1, 2, 3 and 4, are executed only on ticks 1-N,
where N is tempo - 1, and commands 5, 6 and 7 are executed on tick 0 (when a
new pattern row is also read). Command 0 (arpeggio) executes on every tick.

Command 0XY: Arpeggio. Arpeggiates with the root note, then root note + X
             halftones and then root note + Y halftones. If the X value
             is 8 or higher, the arpeggio will be at half speed (8 will
             be subtracted from the value of X to get the amount of halftones)

Command 1XY: Portamento up. Raises the pitch with (XY) * 4 each tick.

Command 2XY: Portamento down. Lowers the pitch with (XY) * 4 each tick.

Command 3XY: Toneportamento. Raises or lowers pitch until target note has been
             reached. Speed 00 achieves a "tie note" effect. From version 1.3
             onwards direction is determined automatically and the amount of
             pitch change on each tick is XY * 4.

Command 4XY: Vibrato. X determines how fast the direction will change and
             Y*16+X is the amount of pitch change on each tick. (That weird
             formula is just caused by playroutine optimizations)

Command 5XY: Set filter parameters. XY is the filter number (00-3F) to use.
             Note that upon song start, filter number 00 is always activated.

Command 6XY: Set sustain/release. Sets the channel's sustain/release register
             to XY.

Command 7XY: Set tempo. If highest bit is 1 (values 80-FF) the tempo
             (XY and 7F) will be set to current channel only, otherwise on
             all channels. A tempo lower than 3 can't be used, but tempo
             parameter 00 will be used for funktempo (see below)

             If there's both a "current channel" and "all channels" tempo
             change on a same row, the "all channels" tempo change must be
             on the lesser channel number or else the "current channel" tempo
             setting will be overrided.

             Parameter EF will increase the timing mark byte (see Section 5),
             and parameters F0-FF control the master volume fader. Note that if
             you use the master volume fader, you must remember to reset it
             yourself in the beginning of the tune. Also, if you use it, it
             will clash with any manual fades you might be doing.

3.3.1 Using funktempo
---------------------

This is somewhat of a hack, and works like this: write the first tempo to
Filter 0 Freq/Spd and the second tempo to Filter 0 Next Step.

Now, set tempo 00 with the command 7 when you wish to activate funktempo.
The 2 tempos will be alternated automatically on each pattern row.

3.3.2 Master volume fader
-------------------------

New from version 1.5 onwards, this allows to do fadeins/outs within the song
without having to use filter commands. Use effect 7xx (set tempo) with
parameter F0 (silence) to FF (maximum volume.)

If you're also doing fadeout/fadein in your own C64 program while the music is
running, 7xx commands will clash with that operation.

Note that in the editor, master volume fader is only reset when loading a song
or clearing songdata, and in packed/relocated songs, it isn't reset anywhere!!!
If you use the fader, remember to reset it in the beginning of your song.

3.4 Instrument data
-------------------

If a description for a parameter is separated in two by a slash it means it
contains two different parameters: leftmost hexadecimal nybble is the first
parameter and rightmost is the second.

Attack/Decay          0 is fastest attack or decay, F is slowest

Sustain/Release       Sustain level 0 is silent and F is the loudest. Release
                      is a speed like attack & decay.

Pulse                 The starting value of pulsewidth (00x-FEx, where x = 0)
                      If this is 0 the current pulsewidth and pulsewidth
                      direction are left untouched. Note that bit 0 can't
                      be used because it is reserved for the hard restart
                      indicator.

Pulse Speed           The value that will be added to pulsewidth each tick
                      (x00-xFE, where x = 0)

Pulse Limit Low       The pulsewidths where pulsewidth modulation will change
Pulse Limit High      its direction. The low nybble will always be 0 because of
                      optimizations.

                      If both limits are 0 the pulse will always be going in
                      decreasing direction.

Filter To Use         The filter number which this instrument will use. 0
                      means "leave filter settings unchanged" so instruments
                      can use only filter numbers 01-3F.

                      Note: because there's only one filter, it's a good idea
                      to have filter-controlling instruments only on one
                      channel at a time.

3.5 Wavetable data
------------------

In addition to these parameters, each instrument has a wave/note table that
determines the waveforms and pitches to be used when a note starts. With
this table you can make either a simple sound that just has one waveform and
the note's base pitch, or a complex sound that has many waveform changes
(to make good-sounding drums), or anything in between.

The wave/note table consists of byte pairs. The leftmost byte is always the
waveform and the rightmost is the note. A pair that has FF in the waveform
ends wavetable execution (if note number is 00) or loops to position n (if note
number n > 00) NOTE: before the table ends, no portamento, vibrato or arpeggio
will be executed!

A waveform of 00 tells not to change the waveform.

Waveforms 01-08 will delay the wavetable execution for 1-8 frames, and will not
change the waveform.

Waveform byte consists of these bits, combine (add) them as necessary, but
observe the special rules listed below.

  Bitvalue 01 = Gate bit. THIS IS IMPORTANT TO GET AN AUDIBLE SOUND! Gate bit
                initiates the attack/decay/sustain phase of a sound. When it
                goes zero, the release phase begins.
  Bitvalue 02 = Synchronize bit. Will synchronize with an another channel
                (Consult C64 Programmer's Reference Guide for details)
  Bitvalue 04 = Ring-modulation bit. Will ring-modulate with an another channel
                (Consult C64 Programmer's Reference Guide for details)
  Bitvalue 08 = Test bit. Will silence the channel and reset the random-seed
                of a channel if the noise random generator has "locked up"
                because of using noise waveform in combination with another
                waveform. This value is automatically used when a song starts
                playing!
  Bitvalue 10 = Triangle waveform
  Bitvalue 20 = Sawtooth waveform
  Bitvalue 40 = Pulse waveform. There must be nonzero pulsewidth on the
                instrument or else this waveform will be silent!
  Bitvalue 80 = Noise waveform. Don't combine with other waveforms!

Note byte consists of these values:

  00-5F       = Relative notes. Will be added to the current note playing
                on that channel to get the final pitch
  80-DF       = Absolute notes C-0 - B-7.

Values outside of this range will result in a pitch that isn't any correct
note.

3.6 Filter data
---------------

There are 64 possible filtertable steps to use (step-programming is new as of
V1.4) The parameters available in each step are:

Filter Control        The leftmost nybble is the resonance (0-F) of the filter
                      and the rightmost nybble is the channel bitmask. Add 
                      bitvalues together if you require to filter multiple 
                      channels.

                        Bitvalue 01 = Filter channel 1
                        Bitvalue 02 = Filter channel 2
                        Bitvalue 04 = Filter channel 3
                        Bitvalue 08 = Filter external input

                      The byte must be nonzero whenever you want to set new
                      filter parameters and cutoff. Zero value marks cutoff
                      modulation instead.

Filter Type/Time      The leftmost nybble is a bitmask determining what
                      filter(s) will be used, and rightmost is the SID master
                      volume (0-F, default F). Add bitvaluess together if you 
                      require multiple filters.

                        Bitvalue 01 = Low-pass filter
                        Bitvalue 02 = Band-pass filter
                        Bitvalue 04 = High-pass filter
                        Bitvalue 08 = Silence channel 3

                      If Control is zero, this byte marks the duration of 
                      filter cutoff modulation in frames instead.

Filter Freq/Spd       New cutoff frequency (00 keeps unchanged.) If Control
                      is zero, marks cutoff modulation speed instead.

Filter Next Step      The number of next filter step that will be executed.
                      Filter loops can be constructed by pointing into a
                      previous step. Use step 00 to stop filter execution.

                      Note that in filter 00 the "Next Step" function is
                      disabled, because of the funktempo hack.

To clarify, here's an example of how to set a filter with certain parameters
and cutoff, and then modulate the cutoff back and forth. The filter program
begins at step 01. The parameters are presented in a format slightly different
of the editor, to clarify the idea of step-execution:

  Step  Ctrl  T/Ti  F/Sp  Next
   01    81    1F    60    02  ;Resonance 8, chn.1, lowpass, vol 15, cutoff $60
   02    00    40    01    03  ;Sweep cutoff forwards at speed 1 for $40 frames
   03    00    40    FF    02  ;Sweep cutoff backwards (speed -1) for $40
                               ;frames and loop to the beginning

There are two ways to activate a filter: Either with the command 5xx or by
having a non-zero filter step number on an instrument. If the filter-setting is
in the instrument, and the filter has a nonzero cutoff, the cutoff frequency
will be reset on each note triggered. This does not happen if the filter is set
only once by using the 5xx command.

Note that because the filter settings also contain the SID master volume, it's
possible to do master volume fade-in/out by using the 5xx command. However, as
of version 1.5 onwards it's much more preferred to keep filters' mastervolume
always at maximum (F) and use the master volume fader command (7F0-7FF)
instead! See chapter 3.3.2 for details.

A filter setting with channels selected for filtering but no filter type
selected (type = 0) will result in silence on those channels!

3.7 Changing instrument on the fly
----------------------------------

Changing instrument in the middle of a note leads to some useful side-effects:

  - The pulse width modulation speed & limits are now taken from the "new"
    instrument.
  - Next time the wavetable loops, it will loop to the new instrument's
    wavetable.

3.8 ADSR & Wavetable examples
-----------------------------

Here's a diagram to help you visualize the Attack, Decay, Sustain & Release
phases. Attack, Decay and Release are "speeds": 0 is fastest attack, decay &
release and F is slowest. Sustain is a volume level: 0 is almost silent and F
is loudest.

     V      /\            |<- gatebit reset (key-off) at this point
     O     /  \           |
     L    /    \__________|
     U   /                |\
     M  /                 | \
     E /                  |  \
TIME ---------------------------->
         A   D      S       R

ADSR settings are crucial to getting any sound at all. If all of them are zero
just a very short "click" will be heard. Some simple examples:

  A/D 0x Will produce a sound that starts from full volume right away and fades
  S/R 00 to silence automatically. The higher x is, the longer the fade will
         take.

  A/D 0x (Where x is something like 0-3) A sound that goes very fast from full
  S/R 8A volume to sustain level 8. After the gatebit is reset (key-off
         command), starts fading out with speed A.

  A/D CC A sound that rises slowly to maximum volume, then decays slowly to the
  S/R AF sustain level A and after key-off, fades out to silence very slowly.

On multispeed songs, using Attack 0 might result in a very silent first row of
the wavetable. Nonzero attack produces better results. You might also want to try
adding one or more rows of 09/00 (testbit+gate) to the beginning of the
wavetable.

Some examples of wave tables:

  41/00 Pulse waveform on note's original pitch
  FF/00

  21/00 Sawtooth waveform on note's original pitch
  FF/00

  81/C8 A snaredrum sound, using all absolute notes so it doesn't depend on
  41/A8 which note it's played. Use pulsewidth 80 for best result.
  41/A0
  80/C8
  80/C4
  FF/00

  81/C8 A pulse sound on original pitch, preceded with a short noise (like
  41/00 a hi-hat or something) that has always an absolute pitch of G#6
  FF/00

  41/00 A 4-note looping arpeggio sound with pulse waveform (Arpeggio command
  00/04 uses only 3-note arpeggios.) Note that waveform will not be changed
  00/07 after the initial setting of pulse waveform.
  00/0C
  00/00
  FF/02

  21/00 A delayed minor chord arpeggio with sawtooth waveform. Each step
  02/03 takes 3 frames.
  02/07
  02/00
  FF/02

You may find the instruments in included example songs useful as a basis for
your own experiments.


4. Using the included utilities
-------------------------------

4.1 INS2SND.EXE
---------------

INS2SND.EXE converts GoatTracker instruments (.INS-files) into sound effects,
outputting the data as source code.

Usage: INS2SND <instrumentfile> <sourcecodefile> <options>
Options:
-c output in CovertScript format

Look at section 6.3 or run the program without parameters to see the
limitations of the sound effect system.

4.2 SNGSPLIT.EXE
----------------

SNGSPLIT.EXE splits the patterns of a GoatTracker song into smaller pieces for
memory use optimization. It is comfortable to compose with large patterns but
usually more efficient memory-wise to use small patterns. Remember! Always keep
the original song because a pattern-splitted song is much harder to edit
further.

Usage: SNGSPLIT <sourcesong> <dest.song> [splits]

Default number of splits is 4 and maximum is 8. With a higher amount of splits
it's more likely that the maximum order-list length or the maximum number of
patterns are exceeded, and in that case an error message is displayed.

4.3 MOD2SNG.EXE
---------------

Dedicated exclusively to T.M.R, this program converts the pattern & orderlist
data of 4-channel, 31-instrument MOD-files into GoatTracker .SNG files. You
must choose one channel to leave out, and obviously instruments aren't
converted, except for their names. You can also specify a transpose in
halfsteps.

Usage: MOD2SNG <mod> <sng> [channel to leave out (1-4), 4 default]
       [transpose, 0 default]


5. Using the songs in your C64 programs
---------------------------------------

Press F9 in the editor to enter the packer/relocator. Choose playroutine,
startaddress, and file format (.PRG or .BIN), then type the filename.

Look at /examples/example1.prg - example3.prg to get an idea how much these
playroutines take rastertime. No promises!!!

5.1 Playroutine 1: Standard
---------------------------

To init music:

        LDA #tunenumber         ;Starting from 0
        JSR startaddress

To play one frame of music:

        JSR startaddress+3

To use timing marks:

        Put a tempo command (7) with parameter EF in the music data.
        A certain memory location will be incremented (playerbase+$445,
        might change in the future)

To fade out/fade in music:

        Seek for the command sequence
        LDA #$xx
        AND #$FF
        STA $D418
        from the beginning of player, and change the parameter of the AND
        command (currently playerbase+$6d) from between $F0 to $FF to fade the
        music. Note that the master fader function (7F0-7FF) also modifies this
        same location, so it will clash if you use both methods..

Author-info can be read at startaddress+$20 (32 bytes).

From version 1.5 onwards, zeropage use is insignificant as the playroutine
saves the zeropage locations it touches!

5.2 Playroutine 2: Game-oriented (with sound-FX support)
--------------------------------------------------------

The ideology of this player is that the playroutine is not saved with the
musicdata. Instead it's saved only once within your game main module, and you
load music modules (may contain several subtunes, as usual) to a certain area
in memory.

The playroutine source is gmusic.s (in DASM format) in the GoatTracker root
directory. A precompiled binary is not available. Simply include the source
in your game main module source, with the following defines set:

        mt_musicdata - Address where you load music data.
        mt_zpbase    - Zeropage baseaddress. 2 consecutive locations required.
        mt_sfxtbllo  - Low and high startaddress-1 (!) of each sound effect. See
        mt_sfxtblhi    example2.s in /examples/src dir for details. If you don't
                       use sound effects, these are insignificant, but they
                       must still be defined for the playroutine to compile
                       successfully.

Note that if you get an error while compiling (ERR directive encountered) you
must locate the playroutine to another address within a page, so that the
effect code doesn't pagecross. The easiest way to do this is to start the
playroutine from the beginning of a page ($0800, $0900 etc.)

After loading music: (to make sure the player reads musicdata correctly)

        JSR relocatemusic

To init music:

        LDA #tunenumber ;starting from 0
        JSR playtune

To play one frame of music: (do not call this before/during relocatemusic)

        JSR music

To play a sound effect: (see /examples/src/example2.s for details)

        LDA #effectnumber ;starting from 0
        LDX #channel      ;0-2 for channels 1-3
        JSR playsfx


6. File/data formats description
--------------------------------

The sections in the files come in the sequential order in which they're
described.

6.1 GoatTracker song (.SNG) format
----------------------------------

6.1.1 Song header
-----------------

Offset  Size    Description
+0      4       Identification string GTS!
+4      32      Song name, padded with zeros
+36     32      Author name, padded with zeros
+68     32      Copyright string, padded with zeros
+100    byte    Number of subtunes

6.1.2 Song order-lists
----------------------

The orderlist structure repeats first for channels 1,2,3 of first subtune,
then for channels 1,2,3 of second subtune etc., until all subtunes
have been gone thru.

Offset  Size    Description
+0      byte    Length of this channel's orderlist n - 1
+1      n       The orderlist data:
                Values 0-207 are pattern numbers
                Values 208-223 are repeat commands
                Values 224-254 are transpose commands
                Value 255 is the RST endmark, followed by a byte that indicates
                the restart position

6.1.3 Instruments
-----------------

This structure repeats for each of the 31 instruments. Instrument 0 (the
empty instrument) is not stored.

Offset  Size    Description
+0      byte    Attack/Decay
+1      byte    Sustain/Release
+2      byte    Initial pulse width
+3      byte    Pulse speed
+4      byte    Pulse limit low
+5      byte    Pulse limit high
+6      byte    Filter freq/type
+7      byte    Size of wavetable in bytes n
                (NOTE: this is always an even number)
+8      16      Instrument name
+24     n       Wavetable, containing the waveform/note pairs as seen on
                the editor screen.

Note that lowest bit of pulse width is the hard restart indicator (0 = use
hard restart, 1 = don't use)

6.1.4 Patterns header
---------------------

Offset  Size    Description
+0      byte    Number of patterns n

6.1.5 Patterns
--------------

Repeat n times, starting from pattern number 0.

Offset  Size    Description
+0      byte    Size of pattern in bytes m
+1      m       Groups of 3 bytes for each row of the pattern:
                1st byte: Notenumber
                          Values 0-93 are the notes C-0 - A-7
                          Value 94 is the keyoff-command
                          Value 95 is a rest
                2nd byte: Bits 3-7 Instrument number (0-31)
                          Bits 0-2 Command number (0-7)
                3rd byte: Command databyte

6.1.6 Filtertable
-----------------

Offset  Size    Description
+0      256     All filters from the filter table.
                1st byte: Filter 0 resonance/channels
                2nd byte: Filter 0 type/volume
                3rd byte: Filter 0 cutoff
                4th byte: Filter 0 cutoff speed
                5th byte: Filter 1 resonance...

6.2 GoatTracker instrument (.INS) format
----------------------------------------

Offset  Size    Description
+0      4       Identification string GTI!
+4      byte    Attack/Decay
+5      byte    Sustain/Release
+6      byte    Initial pulse width
+7      byte    Pulse speed
+8      byte    Pulse limit low
+9      byte    Pulse limit high
+10     byte    Filter number
+11     byte    Size of wavetable in bytes n
                (NOTE: this is always an even number)
+12     16      Instrument name
+28     n       Wavetable, containing the waveform/note pairs as seen on
                the editor screen.
+28+n   4       If filter number nonzero, filter settings of this instrument

6.3 Sound effect data format
----------------------------

Offset  Size    Description
+0      byte    Attack/Decay
+1      byte    Sustain/Release
+2      byte    Pulse width. This value has nybbles reversed from what it looks
                like in the editor so a middle pulse $80 will be stored as $08,
                and the sound effect routine will put this value to both $D402
                and $D403 registers.
+3      ?       Wavetable. Contains note/waveform pairs (different order than
                in instrument wavetable), from which the waveform can be
                omitted if unchanged, as the value ranges don't overlap:
                        Value 0 ends the sound effect
                        Values 1-129 are waveforms
                        Values 130-223 are absolute notes D-0 - B-7
                        etc.

                Note that a note can't be omitted to store only waveform
                changes!

As you can see, the sound effect format is very simplistic. When converting an
instrument to a sound effect with INS2SND, following things cause an error
message:

        - If the resulting sound effect is more than 128 bytes
        - If the instrument's wavetable contains relative notes, absolute
          notes C-0 or C#0, or waveforms > 129 ($81)

The instrument's pulsewidth modulation & filter settings will be completely
discarded.


7. Recompiling
--------------

To recompile for Win32, you need the MinGW development enviroment, use the
file src/makefile.win as makefile.

To recompile for Linux, use src/makefile. You need to recompile the BME library
http://www.student.oulu.fi/~loorni/software/bme.zip first and place libbme.a
into the linux subdirectory before compiling GoatTracker.

In both cases you need the SDL development libraries in addition to the SDL
runtime. See http://www.libsdl.org for details.


8. Version history
------------------

0.9 Beta  - Original public release

0.91 Beta - Corrected a crash caused by an uninitialized pointer when executing
            wavetable on the last row of a pattern. This same bug also caused
            sounds being cropped one tick too early on the last row.
          - Corrected the description of ringmodulation in the docs
          - A drum test song added (when making it the crash was discovered)

0.92 Beta - Orderlist editing simplified (one cursor position for all channels)
          - SPACE in orderlist sets now play position for F2 key
          - Pattern wrap also when trying to enter notes on the last pattern
            row

0.93 Beta - Vibrato was practically useless on odd speeds (3, 5 etc.) because
            it went a bit out of tune. Now the whole vibrato routine has been
            rewritten and the meaning of the speed parameter has changed.
          - Playroutine optimizations in filter cutoff setting & vibrato pitch
            change: the second parameter will also affect them, however it's
            the 4 lowest bits so it doesn't matter much.

0.94 Beta - Reworked wavetable system making wavetable loops possible. Also,
            now pulsemodulation is executed during wavetable. Still the player
            takes only 12 lines!
          - Note that you have to change the wavetable end byte manually from
            00 to FF if you load songs or instruments made with old versions.
          - Command 6 (set sustain/release) is no longer overridden by
            wavetable execution.
          - Wavetable maximum length (for packed & relocated songs) is now
            510 bytes.
          - Added musicdata clear option (SHIFT+ESC).

0.95 Beta - Some reordering in the playroutine, however retaining the same
            size as in 0.94. Init music & Set volume subroutines added to the
            playroutine.
          - Wavetable maximum length is now 512 bytes.

0.96 Beta - $d404 must come before $d405 & $d406 in note initialization to get
            sharper attack.
          - Had to remove the Init & Set volume subroutines. (no room for them)
          - Instruments with looped wavetables didn't always play correctly
            when entering notes in the editor - fixed.
          - The playroutine startaddress is now remembered when packing/
            relocating multiple songs during one session.

0.97 Beta - Added screenmode options.

0.98 Beta - Added Follow Play option (SHIFT+F1/F2)
          - Added fast scrolling with PAGE UP & PAGE DOWN keys.
          - SHIFT+RETURN in orderlist editor updates pattern numbers of all
            channels.

0.99 Beta - Added HardSID support. Use /H1 option to utilize first HardSID, /H2
            for second etc. and /H0 to return to emulated output.

1.0       - Added HOME/END to go to the beginning/end of an orderlist or a
            pattern.
          - Note and hexvalue entry work now also with SHIFT or CAPS-LOCK down.

1.01      - Added choice of emulated SID model with /E option. /E0 for 6581
            (default) and /E1 for 8580.
          - Added NTSC timing (with /N option, return to PAL timing with /P)
          - Frequency table corrected for A-440Hz tuning.

1.02      - SIDs saved are now in PSID V2 format.
          - Added mention of the HardSID-DLL-Clone for PC64 cable support.
          - Added suggestion to not rely only on reSID emulation.

1.03      - Added \ to drive names in the fileselector to make them work
            better under Win9x.

1.1       - Added Playroutines 2-4:
            "Game-playroutine" with sound effect support
            "Scene-playroutine" with author info at startaddress+$20 and
            timing mark support
            "Everything-playroutine" that has those features combined
          - Added DMC note-entry mode as an option.
          - Added configurable playroutine zeropage address.
          - Added default pattern length selection when clearing patterns.
          - Added possibility to turn auto-advance off.
          - Added documentation of the song, instrument & sound effect data
            formats.
          - Added hints on creating SID sounds.
          - Added sound effect converter INS2SND.EXE. This turns instrument
            files to sound effects (with certain limitations)
          - Added pattern splitter utility SNGSPLIT.EXE, for optimizing song
            memory usage.
          - Added 4 C64 example programs that show features of each
            playroutine.
          - Follow play follows now also orderlist.
          - Relocator fileformat and saveaddress saved in config now.
          - Restructured all playroutines with a "jump table" for easy access
            of features.
          - Changed directory sorting to be case-insensitive.
          - Changes in keyboard commands:
            SHIFT+X,C,V Cut,copy,paste (pattern & instrument mode)
            SHIFT+Q,A Transpose
            SHIFT+cursor keys Mark pattern
            SHIFT+L Mark whole pattern
            F5-F8 go directly to different editing modes
          - Fixed hex-editing of instrument/command data in jam mode:
            it shouldn't be possible.

1.11      - Optimized playroutines 1, 2 & 4 to take less memory.
          - Rearranged ADSR and pulsewidth in the sound effect data.

1.12      - Added SHIFT+E,R to copy/paste effects row.

1.13      - Added icon by Antonio Vera. Thanks to him!

1.14      - DirectDraw replaced by GDI functions.
          - Foreign letters should now display correctly, because Windows
            fonts are being used.
          - Added font selection with SHIFT+F.
          - Added information about recompiling.
          - Configuration file format changed; it's necessary to be binary
            data because the Windows font structure is saved with it.
          - Screen updates made more frequent as now only changed areas are
            being re-drawn.
          - Removed the screenmode & fullscreenmode command line options.

1.15      - Added more example songs.
          - Added information about the useful side-effects of changing
            instrument number in the middle of a note.
          - Removed the END SONG command; now the RESTART command is followed
            by the restart position instead.
          - Maximum number of patterns is now 255 (one more)
          - Maximum orderlist length is now 254 (one less)

1.16      - Added feature of leaving pulse width unchanged if it's 0 in the
            instrument data.
          - Added information about the side-effects of pulse width limits.
          - Note entry uses now rawkey-codes.
          - Fixed DMC note-entry mode: it must check SHIFT/CTRL too.

1.17      - Added D642PRG.EXE and PRG2D64.EXE utilities for file extraction/
            writing on D64 images.
          - Added highlighting of every 4 pattern rows (by default); the
            stepsize can be changed with SHIFT+M,N
          - Added highlighting of playing position also in normal play mode.
          - Added possibility to jam while the song is playing.
          - Added automatic adding of file extension to file names if missing.
          - Added "advertisement" of the BME library to the beginning of this
            document.
          - SHIFT+X,C,V,Q,A affect now whole pattern if there isn't a
            marked area
          - SHIFT+arrows LEFT/RIGHT change current pattern too.
          - SHIFT+L will unmark area if there is one already.
          - SHIFT+TAB will cycle edit modes backwards.
          - SHIFT+N is now required to access instrument name in the instrument
            editor.
          - SHIFT+SPACE in orderlist editor sets start position for all
            channels at once.
          - Filter will now always be reset on song start/stop.
          - Test sounds with non-zero filter byte will be played with
            filter activated (with default resonance 8)
          - This file is now called README.TXT.
          - Reverted to BME library (DirectDraw/DibSection) for graphics
            output. Windows GDI screen updating didn't work correctly for
            everyone.
          - Reverted to old configuration file format.

1.18      - GoatTracker uses now BME library's sound routines. This allows use
            of DirectSound for low latency and generally gives better working
            output for WaveOut too.
          - Added /D command line option to choose sound device: WaveOut or
            DirectSound.
          - /B command line option now takes the buffer size as milliseconds.

1.19      - Will try DibSection mode if DirectDraw fails.
          - Command line options now in this document too.
          - Windowed mode is default.

1.2       - GoatTracker is now a console application to finally make it work
            "well" in all systems.
          - Reverted back to original sound routines (no BME library anymore.)
          - /B option back in original meaning: number of 20ms buffers.
          - /D option gone, using always WaveOut now (console applications
            can't use DirectSound.)
          - /F & /S options gone as well.
          - Screen dimensions changed a bit (less visible pattern rows now)
          - Online help is now scrolling.
          - Fixed a buffer overrun problem in making the OemToChar & CharToOem
            translation tables.

1.21      - Added a chapter on .SID -> .SNG conversion (shortly: I won't do it)
          - Fixed ADSR-init in playroutines; when switching tunes at just
            a "wrong" moment notes could be left ringing.
          - Updated for CovertBitOps site launch: D642PRG and PRG2D64 are now
            included on the CovertBitOps site among the other command-line
            tools so they are no longer a part of the GoatTracker distribution.

1.22      - Fixed dependance of carry flag being clear for correct cut-off
            slide

1.23      - ReSID 0.13 integrated
          - Added instrument parameters to online help.
          - INSERT/DELETE in orderlist always changes song length; one doesn't
            necessarily have to be on the endmark anymore.
          - Now pulse initial value $00 doesn't reset pulse direction. This
            made the playroutines a bit bigger.
          - New example songs and some instruments added.
          - Removed the example SIDs as unnecessary.
          - Fixed crash in relocator if using only 1 instrument with a big
            wavetable (was allocating too little workspace.)

1.24      - Added multispeed support (/S command line option.)
          - Added mention of the GoatTracker Tweak Utility to docs.
          - Fixed NTSC timing with HardSID.
          - Fixed time counting in NTSC timing.

1.25      - Fixed command 6 stopping sound effect playback.
          - Added musicdata-only save mode (no playroutine!)

1.3       - Added hard restart toggle to instruments (SHIFT+H).
          - Added transpose & repeat commands to song-orderlist.
          - Added odd vibrato speeds.
          - Added tablebased filter execution.
          - Added separate portamento down command.
          - Fixed system slowdown on emulated output+high multispeeds.
          - Only one of name,author,copyright shown at a time.
          - Pulse speed has finer resolution.
          - Toneportamento is more userfriendly, and achieves faster speeds.
          - Portamento achieves faster speeds as well.
          - No wavetable/arpeggio skip on tick 0 anymore.
          - Now contains 3 playroutines: Scene, Game and Multispeed.
          - Game playroutine supports loading of music modules without having
            to store the playroutine within each module.
          - No rastertime limit promises anymore! :)

1.31      - Speed-optimized pulsemodulation code, and made it actually utilize
            the full 12 bits of pulsewidth! :)

1.32      - Added CovertScript output mode to INS2SND.
          - Removed the restriction of saving music under I/O area. Doing that
            is recommended only for those who know what they're doing (requires
            modification of playroutine code)
          - Some corrections & additions in the documentation.

1.33      - Uses SDL library for portability -> back to using a framebuffer.
          - Buffer length is in milliseconds again.
          - Added option to repeat current pattern indefinitely (F3).

1.34      - Command 6 (set Sustain/Release) can also be used on a new note.
          - Fixed crash when an orderlist started with a repeat command.

1.35      - Packer/Relocator should be endian-independent.

1.4       - Filter is now step-programmable.
          - MOD2SNG utility added.
          - Fixed a lockup-prevention countermeasure causing possible missed
            patterns in case of repeat & transpose on all channel orderlists.
          - Fixed a bug with the 6xx command and multispeeds in the editor's
            playroutine.
          - Fixed hard restart length at multispeeds in the editor's
            playroutine.

1.4b      - 1-frame hard restart option added.
          - CatWeasel MK3 PCI SID support by doj / cubic added.

1.4c      - Better hard restart (one more frame of wavetable executed in
            conjunction), but this increases rastertime use even more!
          - Added support for fadeout (seek for and #$ff; sta $d418 in player
            code, modify the and instruction to perform fades)

1.4d      - $d418 bug in playroutine fixed
          - Arpeggio execution bug in editor fixed
          - Added AD parameter (-A option) and instructions/example how to get
            sharper hard restart using the testbit.

1.4e      - Updated to use ReSID 0.15

1.4f      - Funktempo capability added (see section 3.3.1)

1.5       - Playroutine rewritten. Uses testbit hard restart from now on for
            much sharper sounds
          - ADSR parameter for hard restart configurable (previously only AD)
          - Added orderlist cut/copy/paste
          - Added indicators for ADSR parameter & hard restart length to the
            title bar
          - Added delayed wavetable execution
          - Added proper gateoff, so keyoff in the patterns works correctly
            even if your wavetable has gatebit set to 1
          - Added master fader command (7F0-7FF)
          - Timing mark is now command 7EF
          - Standard playroutine saves all zeropage locations it uses
          - INS2SND modified, now it will no longer insert delays, as these are
            unsupported by the new gamemusic playroutine

1.51      - Funktempo hack works differently
          - Copybuffer no longer erased on song load

1.52      - Frequency table should have better tuning now
          - Relocation address no longer significant for gamemusic tunes
          
1.53      - Fixed packer behaviour with no hardrestart/no pulseinit instruments
          - Optimized pulseinit routine a few cycles (at cost of one byte)
