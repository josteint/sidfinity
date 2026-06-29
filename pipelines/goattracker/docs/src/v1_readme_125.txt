GoatTracker v1.25
-----------------

Editor by Lasse Öörni (loorni@student.oulu.fi)
reSID engine by Dag Lem.
GoatTracker icon by Antonio Vera.

Distributed under GNU General Public License
(see the file COPYING for details)

Covert BitOps homepage:
http://covertbitops.cjb.net

Official latest GoatTracker version:
http://covertbitops.cjb.net/tools/goattrk.zip


Table of contents
-----------------

1. General information
1.1 About converting .SIDs to GoatTracker song format

2. Warnings

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
3.4 Instrument data

4. Using the included utilities
4.1 INS2SND.EXE
4.2 SNGSPLIT.EXE

5. Using the songs in your C64 programs
5.1 Playroutine 1: Original
5.2 Playroutine 2: Game (with sound effects)
5.3 Playroutine 3: Scene (author info + timing marks)
5.4 Playroutine 4: Everything (author info + timing marks AND sound effects)
5.5 Playroutine 5: Multispeed (author info + timing marks)
5.6 Tweaking instrument data

6. File/data formats description
6.1 GoatTracker song (.SNG) format
6.1.1 Song header
6.1.2 Song orderlists
6.1.3 Instruments
6.1.4 Patterns header
6.1.5 Patterns
6.2 GoatTracker instrument (.INS) format
6.3 Sound effect data format

7. Hints for creating SID sounds

8. Recompiling

9. Version history


1. General information
----------------------

This program is a C64 music editor running as a 32-bit Windows application
(should work on W9x/NT4/W2K etc.) Familiarity with tracker programs in general,
hexadecimal notation, and the C64's audio chip (consult the C64 Programmer's
Reference Guide, it's available at http://project64.c64.org) are required to
successfully utilize this program.

1.1 About converting .SIDs to GoatTracker song format
-----------------------------------------------------

This has been asked of me many times. First of all let me say that I won't
do such a converter. To know why, one must know what .SID-files contain.
They aren't any "standard" music module format like MOD, XM or IT but instead
they contain a playroutine in C64 machine language and the binary data that
the playroutine used. It's entirely up to the music composer/programmer how the
data is stored, what effects can be used etc. There are probably hundreds of
different C64 playroutines (considering all different versions) and very few of
them are documented, so severe reverse-engineering would be required to
understand the way each playroutine operates and stores data.

Furthermore, even if the music data was understood and extracted the effects
and instruments would likely be different than in GoatTracker, so the
conversion would often be "lossy" in some ways and sound worse. It was often
popular to store note durations instead of constant-step "patterns" so even the
conversion of notes to GoatTracker patterns could be problematic.

Of course, GoatTracker-made .SIDs could be converted losslessly back into .SNG-
format but I won't go to that because it could well lead into people expecting
more conversion capabilities.

I hope I didn't discourage too much, if someone else is eager to write a .SID
-> .SNG convertor for even one playroutine, go ahead :-)


2. Warnings
-----------

1. Always look at the end of this file for changes! Sometimes keyboard commands
   change etc.

2. Always save your songs in the .SNG-format with F11 key if you plan to
   continue editing! Packed & relocated songs (.PRG/.BIN/.SID) can't be loaded
   back into the editor.

3. A subtune must have at least one pattern in the orderlist for each channel
   for it to be saved. GoatTracker will terminate saving to the first "empty"
   subtune it encounters, so do not skip over any subtune-numbers!

4. Even the reSID emulation is in some cases quite far from the output of a
   real SID. Consider strongly testing your tune (especially if filters are
   in use) on a C64 or on a HardSID card. (Using filters has always been
   complicated because every SID tends to sound different.)

5. The editor will stop playing if the song restart position is illegal (beyond
   end of song) but the C64 playroutines won't! So don't use that as an endsong-
   mark. Create instead one empty pattern and set it to repeat indefinitely if
   you want the song to end.

6. Arpeggios don't sound as good as in the instrument editor when actually
   played in the song. This is caused by the playroutine that is skipping all
   continuous effects on tick 0 (reading new notes)


3. Using GoatTracker
--------------------

Command line options:

/Bxx Set number of 20ms sound buffers DEFAULT=10
/Exx Set emulated SID model (0 = 6581 1 = 8580) DEFAULT=6581
/Hxx Use HardSID (0 = off, 1 = HardSID ID0 2 = HardSID ID1 etc.)
/Kxx Note-entry mode (0 = PROTRK. 1 = DMC) DEFAULT=PROTRK.
/Mxx Set sound mixing rate DEFAULT=44100
/Sxx Set speed multiplier (2 for 2x tunes, 4 for 4x tunes etc.)
/N   Use NTSC timing
/P   Use PAL timing (DEFAULT)
/W   Write sound output to a file SIDAUDIO.RAW
/?   Show command line options

Try the command line options if there are any problems. For example, if you
experience choppy audio you can increase audio buffering with /B option.

HardSID support is available with the /H option. (use first HardSID = /H1,
second = /H2 etc., return to emulated output = /H0) You must have the HardSID
drivers and HardSID.DLL installed to use this feature.

Remember to enable normal operation with /S1 when you're finished working with
multispeed-tunes. Multispeeds higher than 2x don't seem to work too well with
the HardSID, because the Windows multimedia timer has 1ms granularity. With
emulated output, this problem doesn't exist, as the timing is based on sound
buffer sizes.

To use the PC64 cable, check out Daniel Illgen's HardSID-DLL-Clone at
http://home.t-online.de/home/lord_leinad/pages/_work.htm

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
SHIFT+F1  Play from beginning    (Follow play)
SHIFT+F2  Play from current pos. (Follow play)
F3        Stop playing & silence all sounds
F4        Mute current channel
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

0-9 & A-F  Enter pattern numbers
SPACE      Set start position for F2 key
SHIFT+SPACE Set start position on all channels
RETURN     Go to pattern
SHIFT+RET. Go to pattern on all channels
< >        Select subtune

3.1.4 Instrument edit mode
--------------------------

0-9 & A-F  Enter parameters
SPACE      Play test note
SHIFT+SPACE Play test note without filter
RETURN     Silence test note
- +        Select instrument
/ *        Select octave
SHIFT+X,C,V Cut,copy,paste instrument
SHIFT+N    Edit instrument name

NOTE: Filtered test notes will always use resonance 8.

3.1.5 Songname edit mode
------------------------

Use cursor UP/DOWN to move between song, author & copyright strings, and
other keys to edit them.

3.2 Song data
-------------

A song can consist of up to 32 sub-tunes. Each sub-tune has pattern-orderlists
for all 3 channels. The pattern-orderlist is a list of patterns to be played
(max. 254 columns long) followed by the RST (restart) endmark and restart
position for that channel.

3.3 Pattern data
----------------

Patterns are single-channel as there's a pattern-order list for each channel.
A pattern can have variable length, however 80 rows is the maximum. There can
be 254 different patterns in a song.

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

Commands 0,1 & 3 and 4 bear some resemblance to Soundtracker/Protracker/
Fasttracker effects. However, they are different in some ways, so read their
descriptions!!! Note that there is no "databyte 00 uses the last databyte"-
action in the commands.

The "continuous" commands 0, 1, 3 and 4, are executed only on ticks 1-N, where
N is tempo - 1, and commands 2, 5, 6 and 7 are executed on tick 0 (when a new
pattern row is also read)

Command 0XY: Arpeggio. Arpeggiates with the root note, then root note + X
             halftones and then root note + Y halftones. If the X value
             is 8 or higher, the arpeggio will be at half speed (8 will
             be subtracted from the value of X to get the amount of halftones)

Command 1XY: Portamento. Raises the pitch with (XY and 7F) * 2 each tick.
             Highest bit of XY decides direction: 0 is up and 1 is down.

Command 2XY: Set filter cutoff speed. The cutoff speed will be added to the
             cutoff frequency each tick, until stopped with a 200 command.
             (Values 80 and greater subtract the cutoff frequency because the
             cutoff frequency is only 8 bits)

Command 3XY: Toneportamento. Raises or lowers pitch until target note has been
             reached. Highest bit of XY decides direction of toneportamento
             (this is an optimization for the C64 playroutine, to keep it fast:
             you must know the direction yourself) and the actual speed used
             is (XY and 7F) * 2. By specifying the "wrong" direction you can
             get infinitely fast toneportamentos that go to the target note
             right away, for the "tie note" effect.

Command 4XY: Vibrato. X determines how fast the direction will change (E
             is slowest and the lowest bit doesn't matter) and Y*16+X is the
             amount of pitch change on each tick. (That weird formula is just c
             aused by playroutine optimizations)

Command 5XY: Set filter parameters. X is the filter resonance and Y is the
             bitmask of channels to be filtered.

               Bitvalue 01 = Channel 1
               Bitvalue 02 = Channel 2
               Bitvalue 04 = Channel 3

Command 6XY: Set sustain/release. Sets the channel's sustain/release register
             to XY.

Command 7XY: Set tempo. If highest bit is 1 (values 80-FF) the tempo
             (XY and 7F) will be set to current channel only, otherwise on
             all channels. A tempo lower than 3 can't be used.

             If there's both a "current channel" and "all channels" tempo
             change on a same row, the "all channels" tempo change must be
             on the lesser channel number or else the "current channel" tempo
             setting will be overrided.

             Playroutines 3 & 4 use values C0-FF for timing mark purposes,
             so they won't affect the tempo. When packing a song for
             playroutines 1 & 2 the timing marks will be removed from the
             output data, because those playroutines wouldn't understand them.

3.4 Instrument data
-------------------

If a description for a parameter is separated in two by a slash it means it
contains two different parameters: leftmost hexadecimal nybble is the first
parameter and rightmost is the second.

Attack/Decay          0 is fastest attack or decay, F is slowest

Sustain/Release       Sustain level 0 is silent and F is the loudest. Release
                      is a speed like attack & decay.

Pulse                 The starting value of pulsewidth (00-FF)
                      If this is 0 the current pulsewidth and pulsewidth
                      direction are left untouched.

Pulse Speed           The value that will be added to pulsewidth each tick
                      (0-F)

Pulse Limit Low       The pulsewidths where pulsewidth modulation will change
Pulse Limit High      its direction. The low nybble will be always 0 because of
                      optimizations.

                      If both limits are 0 the pulse will always be going in
                      decreasing direction.

Filter Freq/Type      Frequency is the highest 8 bits of cutoff frequency.
                      Filter type is a bitmask consisting of:

                        Bitvalue 01 = Lowpass filter
                        Bitvalue 02 = Bandpass filter
                        Bitvalue 04 = Highpass filter

                      This byte comes into effect when a new note is played.
                      If its value is 0 then filter cutoff & type will be
                      unchanged. Because there's only one filter, it's a good
                      idea to have filter-controlling instruments only on one
                      channel at a time :-)

                      NOTE: The low 4 bits (type) also affect cutoff frequency.
                      This is a playroutine optimization.

In addition to these parameters, each instrument has a wave/note table that
determines the waveforms and pitches to be used when a note starts. With
this table you can make either a simple sound that just has one waveform and
the note's base pitch, or a complex sound that has many waveform changes
(to make good-sounding drums), or anything in between.

The wave/note table consists of byte pairs. The leftmost byte is always the
waveform and the rightmost is the note. A pair that has FF in the waveform
ends wavetable execution (if note number is 0) or loops to position n (if note
number n > 0) NOTE: before the table ends, no portamento, vibrato or arpeggio
will be executed! Pulsemodulation will be executed, as of V0.94 onwards.

A waveform of 0 tells not to change the waveform, this is useful if you use
keyoffs (gatebit off) during wavetable execution.

Waveform byte consists of these bits:

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

Some examples of wave tables:

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

  41/00 A 4-note arpeggio sound with pulse waveform. (Arpeggio command itself
  00/04 uses only 3-note arpeggios) Note that waveform will not be changed
  00/07 after the initial setting of pulse waveform.
  00/0C
  00/00
  FF/02

Changing instrument in the middle of a note leads to some useful side-effects:

  - The pulse width modulation speed & limits are now taken from the "new"
    instrument
  - Next time the wavetable loops, it will loop to the new instrument's
    wavetable. So, if you create another instrument with exactly the same
    wavetable but gatebits off you can "simulate" a keyoff by changing
    instrument and can thus have "keyoff" even while changing waveforms
    in the wavetable loop (otherwise impossible)


4. Using the included utilities
-------------------------------

4.1 INS2SND.EXE
---------------

INS2SND.EXE converts GoatTracker instruments (.INS-files) into sound effects,
outputting the data as source code.

Usage: INS2SND <instrumentfile> <sourcecodefile>

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
it's more likely that the maximum orderlist length or the maximum number of
patterns are exceeded, and in that case an error message is displayed.

5. Using the songs in your C64 programs
---------------------------------------

Press F9 in the editor to enter the packer/relocator. Choose startaddress,
zeropage baseaddress and file format (.PRG or .BIN), then type the filename.

Playroutines 1-2 use 3 bytes starting from zeropage baseaddress as temporary
variables (by default $FC, $FD, $FE). Playroutines 3 & 4 use in addition a 4th
byte (by default $FF) to store timing mark data. Playroutine 5 is for multi-
speed tunes, otherwise it behaves just like playroutine 3.

There's also a special musicdata-only save mode, activated by pressing spacebar
when selecting the playroutine. This is meant for saving diskspace: playroutine
can be embedded in the main program code. Email me (loorni@student.oulu.fi) if
you want that playroutine (sourcecode only, DASM format)


5.1 Playroutine 1: Original
---------------------------

Music playing will take 12 rasterlines max. This player has the smallest size.

To init music:

        LDA #tunenumber         ;Starting from 0
        JSR startaddress

To play music:

        JSR startaddress+3

To change volume:

        LDA #volume             ;0-F, F is default
        JSR startaddress+6

5.2 Playroutine 2: Game (with sound effects)
--------------------------------------------

Music playing will take 13 rasterlines max. without sound effects, or possibly
more with sound effects playing.

To init music:

        LDA #tunenumber         ;Starting from 0
        JSR startaddress

To play music:

        JSR startaddress+3

To change volume:

        LDA #volume             ;0-F, F is default
        JSR startaddress+6

To play a sound effect

        LDA #<sound             ;Address of sound effect data
        LDX #>sound
        LDY #channel            ;0-2
        JSR startaddress+9

The actual sound data can be created from an instrument with the included
INS2SND tool or you can look below for the data format description.

5.3 Playroutine 3: Scene (author info + timing marks)
-----------------------------------------------------

Music playing will take 12 rasterlines max.

To init music:

        LDA #tunenumber         ;Starting from 0
        JSR startaddress

To play music:

        JSR startaddress+3

To change volume:

        LDA #volume             ;0-F, F is default
        JSR startaddress+6

To use timing marks:

        Put a tempo command (7) with parameter C0-FF in the music data.
        Now tempo won't be set, but the parameter is copied to the 4th zeropage
        address (by default $FF) when this command is encountered.

Author-info can be read at startaddress+$20 (32 bytes).

5.4 Playroutine 4: Everything (author info + timing marks + sound effects)
--------------------------------------------------------------------------

Music playing will take 13 rasterlines max. without sound effects, or possibly
more with sound effects playing.

To init music:

        LDA #tunenumber         ;Starting from 0
        JSR startaddress

To play music:

        JSR startaddress+3

To change volume:

        LDA #volume             ;0-F, F is default
        JSR startaddress+6

To play a sound effect

        LDA #<sound             ;Address of sound effect data
        LDX #>sound
        LDY #channel            ;0-2
        JSR startaddress+9

To use timing marks:

        Put a tempo command (7) with parameter C0-FF in the music data.
        Now tempo won't be set, but the parameter is copied to the 4th zeropage
        address (by default $FF) when this command is encountered.

Author-info can be read at startaddress+$20 (32 bytes).

5.5 Playroutine 5: Multispeed (author info + timing marks)
----------------------------------------------------------

No guarantees about rasterline use.

To init music:

        LDA #tunenumber         ;Starting from 0
        JSR startaddress

To play music:

        JSR startaddress+3      ;Call several times in a frame

To change volume:

        LDA #volume             ;0-F, F is default
        JSR startaddress+6

To use timing marks:

        Put a tempo command (7) with parameter C0-FF in the music data.
        Now tempo won't be set, but the parameter is copied to the 4th zeropage
        address (by default $FF) when this command is encountered.

Author-info can be read at startaddress+$20 (32 bytes).


5.6 Tweaking instrument data
----------------------------

Look into the SRC subdirectory to see the current size of the playroutine
you're using (the files are player1.bin, player2.bin, player3.bin, player4.bin
& player5.bin.) Add this size to the startaddress and you'll have the
instrument data startaddress. Instruments reside as 8-byte structures starting
from this address.

        Instr. 1 AD              instrument startaddress+$0
        Instr. 1 SR              instrument startaddress+$1
        Instr. 1 Pulse           instrument startaddress+$2 *
        Instr. 1 Pulsespeed      instrument startaddress+$3 *
        Instr. 1 Pulselimit Low  instrument startaddress+$4 *
        Instr. 1 Pulselimit High instrument startaddress+$5 *
        Instr. 1 Filt. Freq/Type instrument startaddress+$6
        Instr. 1 Wavetbl. Index  instrument startaddress+$7
        Instr. 2 AD              instrument startaddress+$8 etc.

Observe that parameters marked with (*) have actually the nybbles reversed
from what they look like in the editor.

See also the GoatTracker Tweak Utility (for C64) at
http://covertbitops.cjb.net/tools.htm


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

6.1.2 Song orderlists
---------------------

The orderlist structure repeats first for channels 1,2,3 of first subtune,
then for channels 1,2,3 of second subtune etc., until all subtunes
have been gone thru.

Offset  Size    Description
+0      byte    Length of this channel's orderlist n - 1
+1+n    n       The orderlist data:
                Values 0-254 are pattern numbers
                Value 255 is the RESTART endmark, followed by a byte that
                indicates the restart position

6.1.3 Instruments
-----------------

This structure repeats for each of the 31 instruments. Instrument 0 (the
empty instrument) is not stored.

Offset  Size    Description
+0      byte    Attack/Decay
+1      byte    Sustain/Release
+2      byte    Initial pulse width *
+3      byte    Pulse speed *
+4      byte    Pulse limit low *
+5      byte    Pulse limit high *
+6      byte    Filter freq/type
+7      byte    Size of wavetable in bytes n
                (NOTE: this is always an even number)
+8      16      Instrument name
+24     n       Wavetable, containing the waveform/note pairs as seen on
                the editor screen.

* = nybbles reversed compared to how they appear in the editor

6.1.4 Patterns header
---------------------

Offset  Size    Description
+0      byte    Number of patterns n

6.1.5 Patterns
--------------

Repeat n times, starting from pattern number 0.

+0      byte    Size of pattern in bytes m
+1      m       Groups of 3 bytes for each row of the pattern:
                1st byte: Notenumber
                          Values 0-93 are the notes C-0 - A-7
                          Value 94 is the KEYOFF-command
                          Value 95 is a rest
                2nd byte: Bits 3-7 Instrument number (0-31)
                          Bits 0-2 Command number (0-7)
                3rd byte: Command databyte

6.2 GoatTracker instrument (.INS) format
----------------------------------------

Offset  Size    Description
+0      4       Identification string GTI!
+4      byte    Attack/Decay
+5      byte    Sustain/Release
+6      byte    Initial pulse width *
+7      byte    Pulse speed *
+8      byte    Pulse limit low *
+9      byte    Pulse limit high *
+10     byte    Filter freq/type
+11     byte    Size of wavetable in bytes n
                (NOTE: this is always an even number)
+12     16      Instrument name
+28     n       Wavetable, containing the waveform/note pairs as seen on
                the editor screen.

* = nybbles reversed compared to how they appear in the editor

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
                        Value 255 tells to repeat the same note & wave once
                        Value 254 tells to repeat the same note & wave twice
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


7. Hints for creating SID sounds
--------------------------------

(Very short and not so in-depth section. Contributions are welcome)

Pulse:

- Pulse is "widest" and loudest at middle pulse width 80, the sound thins out
  towards both extremities (00 and FF). Pulsewidth 80 is most useful as a
  part of drum sounds but may sound too dominating for other instruments.
  For bass sounds, 40 is usually good. For harpsichord or acoustic guitar,
  you can go even more towards 00.

- Don't let the pulsewidth cross its entire range or an ugly "pop" sound will
  be heard; use the limits to limit it between 10 & F0 or even closer. When
  a sound starts, the pulsewidth will be first increasing.

- Using small pulsewidth speeds creates a "peaceful" sound while high pulse-
  speeds are more menacing & aggressive (or ugly, depending how you view it)

Combination waveforms:

- Experiment with combination waveforms; for example waveform 51 (pulse and
  triangle combined) is a thin and weird sound.

Waveforms in sequence, and variations in the note pitch (with wavetable):

- An "oriental" sounding flute can be created with the following wavetable:

        41/01
        11/00
        FF/00

  It plays the first frame with pulse waveform, one halftone sharp. Then it
  goes to original pitch and triangle waveform for the rest of the sound.

ADSR:

- The higher a sound is, the more dominating it will be. So lower its
  sustain level to keep things balanced.

- Using small (or zero) attack & decay values creates sharp & "modern"-sounding
  sounds.

- Use zero sustain & release with some decay to get a sound that starts
  decaying immediately, like a piano (you probably knew this :-))

- Set drums' sustain mercilessly to full for maximum power! :-)

Synchronize & ring-modulation:

- A "screaming guitar" type sound (like Sanxion loader song) can be created
  by using synchronize bit in combination with the pulse waveform. It is highly
  dependant on what the synchronizing channel is playing, so experiment!

- Using ring-modulation or synchronize with the triangle waveform creates cool
  "eerie" sounds, like those in Fist II cave music.

Filter:

- One word: Experiment. The lowpass filter might be most widely used, beware
  of using too small cutoff frequencies though, because they might result in
  practically inaudible sound on some SID chips.

- If you have an instrument that sets the filter frequency/type (freq/type
  byte nonzero) and don't want the frequency to be reset on each subsequent
  note, create a copy of that instrument with the filter freq/type byte zeroed
  and then you can control cutoff speed freely with the 2XY command.


8. Recompiling
--------------

Currently GoatTracker has been compiled with Borland's 32-bit C/C++ compiler
but any decent 32-bit C/C++ compiler capable of producing Windows console
programs should work, if you edit the makefile accordingly. You will also need
DATAFILE & EXELINK utilities from the Blasphemous Multimedia Engine and some
version of the DASM crossassembler.

A link to BME and my own port of DASM can be found from the same page as this
program: http://covertbitops.cjb.net/tools.htm


9. Version history
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

1.25      - Added musicdata-only save mode (no playroutine!)
          - Fixed command 6 stopping sound effect playback.
