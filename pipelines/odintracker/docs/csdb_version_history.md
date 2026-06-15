---
source_url: https://csdb.dk/getinternalfile.php/15294/OdinTracker112.zip (HISTORY file inside)
fetched_via: curl + unzip 2026-06-15
fetch_date: 2026-06-15
author: Zed (Zoltan Konyha)
content_date: 2001-03-20
reliability: primary (verbatim from HISTORY file in OdinTracker112.zip)
---

# OdinTracker — Full Version History

Verbatim from `HISTORY` file in `OdinTracker112.zip`.

```
                      Odin Tracker history


Odin Tracker is a music editor for the C64. Coded in Hungary
almost two decades after the computer's debut.


Legend:
  + feature added
  * bugfix or correction
  - feature gone


20 Mar 2001 - version 1.12
  + history is now reverse-sorted, clap your hands!
  + elements referenced by the current instrument are highlighted in the
    wave, arpeggio and filter tables.
  + you can select blocks in the filter table. data in the block can be
    incremented/decremented. you can also fill a block with data linearly
    interpolated between the block begin and end position.
  + drive status is displayed in the disk menu.
  and many small fixes:
  + the song will not be cleared when load from disk fails.
  + some keyboard shortcuts have been added. RETURN jumps from orderlist to
    pattern editor, HOME works as expected in the instrument tables.
    RETURN in pattern editor plays from current row.
  + RUN/STOP escapes numeric and string input where applicable.
  * can use disk devices 8-31. maybe it works with hard drives? tell me.
  * song title is saved at $xx20 in packed songs, as it is the de facto
    standard.
  * config menu was buggy, default color sets were not displayed.
  * color sets modified.
  * horribly awkward key mapping to increment/decrement order position is
    changed to +/-. :)
  + page up / page down is back, use = key.
  * frequency table is modified for PAL clock, quite close to JCH's values.
  * vibrato depth scale is made finer, code is also a bit faster.
  * some text was output to the wrong location in the "specials" menu.
  * the source package is cleaned up.

31 Mar 2000 - version 1.11
  * track transpose had no effect on arpeggio command
  * huh, directory listing was broken

27 Mar 2000 - version 1.10
  + packer at last. you can save everything in a single file,
    or relocate the player and the tracks to different locations
    and save them separately.
  - pitch-independent vibrato had to go because it was a bit too expensive
    at one multiplication per voice.
  * other small optimizations in the player have improved it from being
    'horribly slow' to 'slow', still around $30 lines. :(
  * pulse width modulation is refined, limits are handled hopefully bug-free
  + new filter control - works exactly like the arpeggio table. read help.
  + this means new file format. you can still load old (1.0x) files,
    you won't be able to import the filters, though. vibratos may sound a
    bit different, too.
  + you can test instruments on-the-fly in instrument and pattern editor
  - page up/down, etc, had to go to free keys for on-the-fly instrument test.
    sorry.
  + you can play a single pattern with shift+space
  + you can make more songs in one file
  + cut instrument is implemented (how could it be forgotten?)
  + automagically go to start of song after load
  * entering a note off entered garbage into instrument and effects fields :)
  * entering track numbers >= $80 in specials and disk menu killed the editor

29 Feb 2000 - version 1.03
  * damn, delete in orderlist did not work. fixed.

28 Feb 2000 - version 1.02
  + the playroutine finally has hard restart, better late than never
  + you can save a player with your song. this is horribly rotten and
    is a temporary hack till the packer is done. dont even tell me it
    sucks, i know already.
  * speed 0 works somewhat ProTracker compatible
  * bug when editing tracktranspose hopefully gone
  + help included in printable format (plain ASCII, that is)
  * some typing errors in the help corrected
  * absolute arpeggio in arpeggio table was not mentioned in the help
  * absolute arpeggio was in fact buggy, played a semitone deeper the expected
  * background color was sometimes messed up when leaving pattern editor
  - because of silly mem organization the player may miss some interrupts
    while you are reading the help. this is not likely to happen, though.
    (can someone with a good understanding of VIC interrupts examine the
    code of write_helppage in tracker.s near line 4500?)

17 Feb 2000 - version 1.01
  + added pound/shift+pound (insert in emulator) to delete/insert
    a row in all tracks visible in editor
  * when on a note field SHIFT+RUNSTOP jumps to the previous channel,
    just as it used to. when not on a note field, it now jumps to the
    note field of the current channel.
    this is closer to the behaviour of Fast Tracker 2, and also more
    comfortable.
  + disk device defaults to the device Odin Tracker was loaded from

15 Feb 2000 - version 1.00
  First release featuring:
  + MOD-like song organization - no DUR commands
  + 256 element orderlist, 256 patterns, each consisting of 3 tracks and
    3 transpose values, 128 total tracks
  + 31 instruments, 256 bytes of waveform and arpeggio table shared among
    instruments, waveform and arpeggio table loop
  + true sine vibrato
  + pulse width variation
  + filter cutoff frequency variation
  + many track effects including slide, vibrato, arpeggio, pulse width and
    filter control, setting waveform and ADSR parameters on-the-fly
  + pattern editor with many nice features like block cut/copy/paste,
    slide block, undo
  + detailed help
  + and more


http://www.inf.bme.hu/~zed/tracker
mailto:zed@kempelen.inf.bme.hu


Wotan mit uns.
```

## Additional v1.13 changes (from CSDb release page notes)

From CSDb release #2628 notes (not in HISTORY file, which was v1.12's):
- RLE encoding for song saves (maintaining backward compatibility)
- Wave table: $FF now sets waveform AND ADSR to 0 (sharp sounds)
- Bug: slide effect was non-functional (ignored parameter) — FIXED
- Bug: vibrato depth at maximum had a bug — FIXED
- Bug: song save omitted final byte — FIXED
