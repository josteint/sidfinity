---
source_url: https://web.archive.org/web/20010421172156/http://www.inf.bme.hu/~zed/tracker/history.html
fetched_via: wayback 2026-06-15
fetch_date: 2026-06-15
author: Zed (Zoltán Konyha)
content_date: 2001-04-21
reliability: primary
---

# OdinTracker Version History / Changelog

Verbatim from history.html (archived 2001-04-21). Legend: + feature added, * bugfix, - feature gone.

---

## 17 Apr 2001 — version 1.13
+ Songs are saved RLE-encoded; can still load old songs.
+ Entering $FF in the wave table sets waveform and ADSR parameters to 0 (useful for sharp short sounds).
* Version 1.12 had many bugs, some fixed:
  - Slide effect was buggy, did not use the parameter.
  - The largest vibrato depth was buggy.
  - Save song forgot the last byte.

## 20 Mar 2001 — version 1.12
+ History is now reverse-sorted.
+ Elements referenced by the current instrument are highlighted in wave, arpeggio and filter tables.
+ Block selection in filter table; block data can be incremented/decremented; fill with linear interpolation.
+ Drive status displayed in disk menu.
+ Song not cleared when load from disk fails.
+ Some keyboard shortcuts added: RETURN jumps from orderlist to pattern editor; HOME works in instrument tables;
  RETURN in pattern editor plays from current row.
+ RUN/STOP escapes numeric and string input where applicable.
* Can use disk devices 8-31 (possibly hard drives).
* Song title saved at $xx20 in packed songs (de facto standard).
* Config menu was buggy; default colour sets not displayed.
* Colour sets modified.
* Horribly awkward key mapping to increment/decrement order position changed to +/-.
+ Page up/down back; use = key.
* Frequency table modified for PAL clock, close to JCH's values.
* Vibrato depth scale made finer; code is also a bit faster.
* Some text was output to wrong location in "specials" menu.
* Source package cleaned up.

## 31 Mar 2000 — version 1.11
* Track transpose had no effect on arpeggio command.
* Directory listing was broken.

## 27 Mar 2000 — version 1.10
+ Packer at last. Save everything in a single file, or relocate player + tracks separately.
- Pitch-independent vibrato removed (too expensive: one multiplication per voice).
* Other small optimizations: player improved from "horribly slow" to "slow", still ~$30 rasterlines.
* Pulse width modulation refined; limits handled hopefully bug-free.
+ New filter control: works exactly like the arpeggio table.
+ New file format (1.0x files can still be loaded; filter not imported; vibrato may sound different).
+ On-the-fly instrument testing in instrument and pattern editor.
+ Page up/down removed to free keys for on-the-fly instrument test.
+ Play single pattern with SHIFT+SPACE.
+ Multiple songs in one file (subsong support).
+ Cut instrument implemented.
+ Auto go to start of song after load.
* Note off entering wrote garbage into instrument and effects fields.
* Entering track numbers >= $80 in specials and disk menu killed the editor.

## 29 Feb 2000 — version 1.03
* Delete in orderlist did not work. Fixed.

## 28 Feb 2000 — version 1.02
+ Player finally has hard restart.
+ Save a player with the song (temporary hack until packer done).
* Speed 0 works somewhat ProTracker compatible.
* Bug when editing track transpose hopefully fixed.
+ Help included in printable format (plain ASCII).
* Some typos in help corrected.
* Absolute arpeggio in arpeggio table was not mentioned in help.
* Absolute arpeggio was buggy (played a semitone too deep).
* Background colour sometimes messed up when leaving pattern editor.
- Player may miss some interrupts while reading help (unlikely).

## 17 Feb 2000 — version 1.01
+ Added pound/shift+pound (insert in emulator) to delete/insert a row in all tracks visible in editor.
* SHIFT+RUNSTOP on a note field jumps to previous channel; on other fields jumps to note field
  of current channel (closer to Fast Tracker 2 behaviour).
+ Disk device defaults to the device Odin Tracker was loaded from.

## 15 Feb 2000 — version 1.00 (First release)
Features:
+ MOD-like song organisation — no DUR commands.
+ 256-element orderlist, 256 patterns (3 tracks + 3 transpose values each), 128 total tracks.
+ 31 instruments (NOTE: later versions have 32).
+ 256 bytes of wave table + 256 bytes of arpeggio table, shared among instruments with loop.
+ True sine vibrato.
+ Pulse width variation.
+ Filter cutoff frequency variation.
+ Track effects: slide, vibrato, arpeggio, pulse width and filter control, set waveform + ADSR on-the-fly.
+ Pattern editor: block cut/copy/paste, slide block, undo.
+ Detailed help.

---

## Notes on Format Versions
- **v1.0x format:** No filter table in instrument; filter controlled only by track effects.
- **v1.1x+ format:** Filter table added as instrument parameter (start/end/loop indices).
  Incompatible with v1.0x; v1.1x+ can import v1.0x songs but loses filter settings.
- **v1.13:** Songs RLE-packed when saved; backwards compatible for loading.

---

## News Timeline (from news.html, archived 2001-04-21)

```
17 Apr 2001   OdinTracker 1.13 released.
15 Apr 2001   Dat2Sid 1.1 now handles multispeed tunes.
20 Mar 2001   OdinTracker 1.12 released. Dat2Sid utility available for Windows and Linux.
              FAQ created.
29 Jan 2001   Some songs added. Page re-edited.
20 Nov 2000   Some songs added.
19 Apr 2000   Completely new web page.
27 Mar 2000   Version 1.10: new song format + packer included. New songs.
28 Feb 2000   Version 1.02: first useful version (hard restart). Source provided separately.
              Web page created.
15 Feb 2000   First public version of Odin Tracker born.
```
