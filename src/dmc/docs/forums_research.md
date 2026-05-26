---
source_url: https://csdb.dk/release/?id=2596, https://cadaver.github.io/rants/music.html, https://www.lemon64.com/forum/viewtopic.php?t=24476, https://www.lemon64.com/forum/viewtopic.php?t=48548
fetched_via: direct
fetch_date: 2026-04-11
author: multiple sources (CSDb community, Lasse Oorni/Cadaver, Lemon64 forum users, Chordian/JCH, Brian/Graffity in forum posts)
content_date: 1991-2025
reliability: secondary
notes: multiple sources — aggregated from Usenet archives, Lemon64, CSDb, Pouet, HVMEC, Chordian, SID Preservation, Cadaver, Scene.hu, Demozoo, and chipmusic.org. Cadaver's technical rant (cadaver.github.io) is the most authoritative single source cited; most other content is forum discussion with no primary specs available.
---

# DMC (Demo Music Creator) — Forum & Web Research

Compiled 2026-04-11. Sources: Usenet archives, Lemon64, CSDb, Pouet, HVMEC,
Chordian, SID Preservation, Cadaver, Scene.hu, Demozoo, chipmusic.org, and
general web searches.

**Overall finding:** DMC's source was never publicly released. No full
disassembly or format specification has been published online. The information
below is assembled from scattered forum posts, editor comparison tables,
tutorials, CSDb comments, and player-identification databases. The deepest
technical details still come from our own reverse-engineering in
`dmc_parser.py` and `docs/players/dmc.md`.

---

## 1. CSDb Releases & Comments

### DMC V4.0 (CSDb #2596)
- https://csdb.dk/release/?id=2596
- Released: September 1991 by Brian/Graffity
- "DMC is to C64 what Protracker is to Amiga" (user comment on Pouet)
- "plenty of different versions/hacks of this program" — users created
  V4.05, V4.19, V4.3 variants
- Multiple users describe it as their "fave editor of all times"
- No technical format documentation in comments

### DMC V5.0 (CSDb #2594)
- https://csdb.dk/release/?id=2594
- Released: 1993 by Brian/Graffity
- Single user comment: "Very powerful, but hard to use Music-Editor,
  unless you have a good knowledge of the I/O between the SID and C64"
- No format details in CSDb page

### DMC V5.4 by Samar (CSDb #36658)
- https://csdb.dk/release/?id=36658
- By Glover/Samar Productions
- **Hard restart improvement**: "better hard restart and some other things"
- **Rastertime savings**: "the good thing about this version of the music
  composer is saving raster time"
- **Buggy packer**: "the packer is very buggy — I composed several music
  with editor — but packer was able pack only one of them. In packed music
  was some bugs, like false notes and so."
- Some users preferred V5.1 over V5.4, finding V5.4 "too hard to handle
  to make really good sounds and filters"

### DMC V7.0 by Unreal (CSDb #2629)
- https://csdb.dk/release/?id=2629
- Based on V4.0 code (NOT V5/V6)
- Ray (co-developer) explains: team chose to improve V4 rather than use
  V5/V6, finding V4 superior for their musicians
- **Key enhancements**: 1-5 multiple songs per file, multi-channel playback,
  play from any line/note, sector length display, cassette/turbotape support
- Code grew ~50% vs V4, making further improvements difficult
- Led to development of TFX as successor
- DMC V7.1 exists separately with "player improvements" and new capabilities
  around "filters and direct AD/SR sets"

### DMC V5.1+ Package (CSDb #2600)
- https://csdb.dk/release/?id=2600
- 1994 package by Graffity and Motiv 8

### DMC 4 Editor 1.0 (CSDb #250645)
- https://csdb.dk/release/?id=250645
- March 2025, cross-platform Windows editor by Logan/Slackers
- Code by Brian (Graffity) and Logan (Slackers)
- Maintains original DMC V4.0 format compatibility
- Can import PRG/SID files from V4.0, V7.0A, V7.0B

### DMC 4 Editor 1.1 (CSDb #251057)
- https://csdb.dk/release/?id=251057
- March 2025 update
- **Sector duration display** (useful for sync between tracks)
- Sound bank import/export
- Octave up/down for selection
- Track editor: play from any selected position
- Music relocator in Export PRG
- Ability to name sounds

---

## 2. Lemon64 Forum Discussions

### DMC 4.0 Player — Idle Channel (t=48548)
- https://www.lemon64.com/forum/viewtopic.php?t=48548
- User reports that even unused channels are not truly "free" — the DMC
  player resets channel state every IRQ call
- Speculation: "My guess is because the DMC player is not actually leaving
  the channel completely free. Maybe it doesn't use it, but it is resetting
  its state every time the IRQ is called."
- **Implication for our pipeline**: DMC V4 player writes to all 3 channels
  every frame regardless of whether they have active notes. The player
  doesn't skip SID register writes for silent voices.

### DMC V4 is Back in 2025 (t=86611)
- https://www.lemon64.com/forum/viewtopic.php?p=1055912
- Discussion of Logan's cross-platform DMC 4 Editor
- **Critical technical detail about pattern system**: "DMC uses duration
  based patterns, they can be any length, no syncing is done at all
  (that's one of the drawbacks of this system)"
- Advantage: "you can program sounds much more direct (you are not limited
  to one or two commands per tick) and triplets can be done way easier"
- V1.1 reportedly "brings some improvements and should help with pattern
  synchronization"

### DMC 6 (t=24476)
- https://www.lemon64.com/forum/viewtopic.php?t=24476
- DMC 6.0 by Brian + Syndrom/TIA
- **Never publicly released**
- **7-8 rasterlines** CPU usage (vs 23-27 for V4)
- Achieves low rastertime through deliberate constraints: "pulse or filter
  only on some channel(s)"
- Has "a complete editor too (no need to edit anything in the sourcecode)"
- DMC 7.0/7.1 were "heavily modified versions of DMC 4.0"

### DMC 4 Instructions (t=80234)
- https://www.lemon64.com/forum/viewtopic.php?t=80234
- Users point to Richard Bayliss' tutorial at TND64
  (http://www.tnd64.unikat.sk/music_scene.html) — now has SSL issues
- Tutorial covers basics to advanced music composing with DMC V4.0

---

## 3. Cadaver's Music Player Technical Rant

- https://cadaver.github.io/rants/music.html
- By Lasse Oorni (Cadaver), author of GoatTracker

### Testbit Hard Restart (DMC & JCH Method)
Exact sequence documented:
1. **2+ frames before next note**: ADSR set to preset ($0000, $0F00, or
   $F800). Gate bit cleared. (ADSR setting can be skipped.)
2. **First frame of new note**: AD and SR values written first. Then $09
   written to waveform register (test bit + gate).
3. **Second frame**: Actual waveform value loaded from wave table.

**Critical**: "Attack/Decay and Sustain/Release are always written before
Waveform" — write order matters for reliable hard restart.

Works reliably on PAL only. This is the method used by both DMC and JCH
players.

### Vibrato Implementation (Generic SID Players)
Parameters:
- Time in frames before starting vibrato (delay)
- Speed of vibrato (how much frequency changes each frame)
- Width of vibrato (how many frames before changing direction)

Key detail: "When vibrato starts, the first part of pitch going up must
only be half as long as the rest, to make the frequency go up & down
around the correct frequency of the note."

Can be table-based for more possibilities.

### Pulse Width Modulation (Generic SID Players)
Parameters:
- Initial pulse width value
- Modulation speed (added/subtracted each frame)
- Pulse width limit low and high

"Advanced routines might have a table-based pulsewidth modulation control"
with commands like "add the value to pulsewidth for N frames" or "set
pulsewidth to X."

### Filter Implementation (Generic SID Players)
"There's only one filter so chaos would result if multiple voices tried to
control it at the same time."

Control includes: filter type, voices affected, cutoff, resonance.
"Cutoff can also be changed smoothly (modulation)" — implemented as
table-based effect with commands like "add to cutoff frequency for N frames."

### Wave Table Format (Generic SID Players)
Wave tables contain "byte pairs; the other byte is what to put in the
waveform register and the other is the note number; either relative
(arpeggios) or absolute (drumsounds)."

Include "jump command and a command to end the waveform/arpeggio
execution." Waveform 0 = no change.

**Note**: DMC V4 uses single-byte wave tables (waveform only, no paired
note byte), unlike the generic 2-byte format described here. V5 uses
2-byte wave table entries.

---

## 4. Chordian C64 Editors Comparison

- http://chordian.net/c64editors.htm
- https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/

### DMC V5.0 Specifications (from comparison table)
- **Release**: 1993 by Brian/Graffity
- **SID chips**: 1 (single SID)
- **Channels**: 3 visible
- **Speed**: 1x only (no multispeed)
- **Digi/samples**: No
- **Max instruments**: 32
- **Sub-tunes**: No (listed as unsupported in V5)
- **CPU consumption**: "Most of the screen" (high rastertime)
- **Zero page**: At least 5 bytes ($FB-$FF)
- **Arpeggio**: "10 bytes for each instrument" in wave tables, hi-freq mode
- **Pulsating**: "Range sweeping only" (limited PWM)
- **Filtering**: "Raw sweeping only" (limited control)
- **Vibrato**: "No" (listed as not natively supported in V5!)
- **Hard restart**: "No?" (uncertain)
- **Sectors**: 96 sectors, each up to 250 rows
- **Pattern system**: Multi-channel sequence blocks
- **Follow-play**: No
- **Undo**: No
- **Transpose**: No

**Note**: This characterization of V5 differs significantly from V4. V4
has explicit vibrato parameters (Vib1, Vib2 instrument bytes) and hard
restart via testbit method. The comparison may reflect the stripped-down
V5 instrument format (8 bytes vs V4's 11 bytes).

---

## 5. SID Preservation (sidpreservation.6581.org)

- https://sidpreservation.6581.org/sid-editors/

### DMC Overview
- "DMC used the same principles as Future Composer but added way much more
  advanced editing features"
- "The first versions of DMC was hungry on the rastertime but the latter
  versions were excellent"
- "DMC V4 is one of the most used editors. It has lots of nice features
  and also one of the most user friendly in the DMC series"
- "SID-Wizard merged lots of style from both DMC, and JCH" — confirming
  DMC's influence on later editors

---

## 6. HVMEC (High Voltage Music Engine Collection)

- https://hvmec.altervista.org/blog/?p=700 (V5.0)
- https://hvmec.altervista.org/blog/?p=504 (V2.1+)
- https://hvmec.altervista.org/blog/?p=570 (V4.0 pro)
- https://hvmec.altervista.org/blog/?p=541 (V4.0 [2x])
- https://hvmec.altervista.org/blog/?p=630 (V4.3++)

### V4.0 Pro (by Morbid/Onslaught)
- Enhanced version of V4.0
- Track editor with start/stop/continue/fast play
- Sector editor with note transportation, gate, continuation, duration,
  sound selection, glide
- Voice/music toggling capability

### V2.1+ [4x] (by Keen Acid)
- Quadruple speed variant of V2.1
- Original code by Brian/Graffity, quad speed by Moog/Keen Acid
- Source: not available

### V4.3++ (by Moog/Keen Acid)
- Quadruple speed variant

### V5.0
- References three editing modes: Track editor, Sound editor, Sector editor
- Comments reference unreleased V6.0 and note that V7.x versions were
  "hacked 4.0 editors"

---

## 7. Graffity Group History (CSDb & Scene.hu)

- https://csdb.dk/group/?id=193
- https://www.scene.hu/tag/graffity/

### Group Timeline
- Founded October 1990 by Brian, Jay, Matrix, Maxwell (Hungary)
- Dissolved October 1994, revivals 1996-1999
- Brian was Coder + Musician from start

### DMC Version Timeline (from CSDb releases)
| Version | Year |
|---------|------|
| GMC V1.0 | 1990 |
| DMC V1.2 | 1991 |
| DMC V2.0 | 1991 |
| DMC V3.0 | 1991 |
| DMC V4.0 | 1991 |
| DMC V4.05 | 1992 |
| DMC V5.0 | 1993 |
| DMC V5.1+ | 1994 |
| DMC 4.0 Pro | 1995 |

- "By March 1991, DMC 2.0 was ready and became a de facto scene standard"
- Graffity described as "the most iconic Hungarian C64 team of the first
  half of the '90s"
- DMC called "the most successful C64 music editor that ever existed"
- Brian later developed music software for other platforms (AdLib Music
  Creator, DreamStation)

### DMC 6.0 — The 8-rasterline Editor
- Scene.hu mentions "an unnamed music editor reportedly only 8 raster lines
  in size, distributed informally among select musicians" — this matches
  the DMC 6.0 described in Lemon64 threads
- Created by Brian + Syndrom/TIA
- 7-8 rasterlines only (vs 23-27 for V4)
- Achieves this by limiting pulse/filter to certain channels only

---

## 8. Pouet.net

### DMC 4.0 (pouet.net #13452)
- https://www.pouet.net/prod.php?which=13452
- "DMC is to c64 what protracker is to amiga"
- "plenty of different versions/hacks of this program"
- User-created variants: DMC 4.19, DMC 4.3
- "fave editor of all times" / "love this :D"
- Some users found newer alternatives (NinjaTracker, SidWinder, JCH)
  superior technically

---

## 9. Generic SID Player Architecture (from dflund.se/~triad)

- https://dflund.se/~triad/krad/sidmidi.html
- By Linus Walleij (Triad)
- Not DMC-specific but describes the same architecture DMC uses

### Vibrato Types
1. **Frequency vibrato**: Modulates pitch by adding instrument's default
   additive curve to frequency registers ($D400/$D401). Configurable
   amplitude and period. Optional LFO control.
2. **Pulse width vibrato**: Similar but "larger amplitude can be used",
   updates $D402/$D403.

### Pulse Width Modulation
- Can be in macros or via separate LFO
- Updates via $D403 (hi byte); most C64 players omit $D402 (lo byte)

### Filter Control
- Three modes: instrument defaults, macro tables (with loop/end), or
  wheel modulation
- Registers: $D415 (lo cutoff), $D416 (hi cutoff), $D417 (resonance, 4 bits)

### Hard Restart
- "Write 0x00 to all registers at $D400-$D406 2/50 second (2 frames)
  before next attack" — the JCH/DMC testbit method

### Note Tables
- 95 entries (C-0 through A-7)
- "The numbers in the C64 hardware reference manual are simply WRONG"

---

## 10. Player Identification (SIDId / player-id)

### SIDId Signatures (from cadaver/sidid)
- https://github.com/cadaver/sidid/blob/master/sidid.nfo

Four DMC variants identified:
1. **DMC** (base) — Released 1991, CSDb #2598
2. **DMC_V4.x** — Released 1991, CSDb #2596
3. **DMC_V5.x** — Released 1993, CSDb #2594
4. **DMC_V6.x** — By Brian, no date/reference

Signatures (from our docs/players/dmc.md, confirmed by sidid.cfg):
```
DMC base: 18 7D ?? ?? 99 ?? ?? BD ?? ?? 7D ?? ?? ?? ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 99 ?? ?? BD ?? ?? 3D ?? ?? 99 ?? ?? 60
DMC V4.x: FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D ?? ?? BD ?? ?? 69 00 2C ?? ?? BD ?? ?? 29 01 D0
DMC V5.x: BC ?? ?? B9 ?? ?? C9 90 D0 AND BD ?? ?? 3D ?? ?? 99 ?? ?? 60
DMC V6.x: A9 02 9D ?? ?? A9 00 9D ?? ?? CA 10 F3 8D ?? ?? A9 08 8D 04 D4 ...
```

### WilfredC64/player-id
- https://github.com/WilfredC64/player-id
- Cross-platform utility using BNDM search algorithm
- Scans SID files against 787+ known player signatures
- Uses sidid.cfg configuration

### Restore64.dev
- https://restore64.dev/
- Browser-based C64 PRG disassembler
- Auto-depacks 370+ packer formats
- Detects 787 SID player engines including DMC variants
- Could be useful for verifying our own disassembly

---

## 11. CSDb Sound Design Forum (General SID, Mentions DMC)

- https://csdb.dk/forums/index.php?roomid=14&topicid=97576&showallposts=1

### DMC Feature: Sweep-Reset Disable
- DMC (alongside SID-Wizard) supports a "sweep-reset" disable feature
- This allows wavetable sweeps to continue across notes rather than
  resetting on each note trigger
- Useful for expressive solos where timbre continuity matters
- Composers use "separate instruments in parts of the solos" as workaround
  in editors without this feature

---

## 12. Chipmusic.org Forums

- https://chipmusic.org/forums/topic/8104/c64-music-for-dummies-c64-tutorial/

### DMC Tutorial References
- Tutorial uses "Graffity's Demo Music Creator V4.0"
- Sound editor sections: WFARP (waveform + arpeggio), PULSE, FILT.
- **WFARP**: Commands to set waveform (WF) and pitch (ARP) per frame.
  All instruments must have entries here.
- **PULSE**: Commands to change pulse width. Required for pulse waveform
  instruments.
- **FILT.**: Commands to operate the SID filter.
- Waveforms in the DMC 4 wavetable are "the same types used in the DMC 5
  wavetable" (1-byte entries in V4, 2-byte entries in V5)

---

## 13. Russian/Eastern European Scene

No specific Russian C64 scene sites with DMC technical internals were found.
The Hungarian connection (Graffity being Hungarian) produced the most relevant
Eastern European content:
- Scene.hu (Hungarian demoscene portal) has historical articles
- Tehernaplo blog conducted a lengthy interview with Graffity (referenced
  but not accessible)
- No technical format details from these sources

---

## 14. Key Version Differences Summary (Compiled from All Sources)

| Feature | V4 | V5 | V6 | V7 |
|---------|----|----|----|----|
| Author | Brian/Graffity | Brian/Graffity | Brian + Syndrom/TIA | Axl+Ray/Unreal |
| Code base | Original | Separate branch | Unknown | Fork of V4 |
| Year | 1991 | 1993 | ~1993? | 1995 |
| Released | Yes | Yes | **No** | Yes |
| Instrument bytes | 11 | 8 | Unknown | 11 (V4 code) |
| Max sectors | 64 | 96-127 | Unknown | 64 |
| Max subtunes | 8 | 8-31 | Unknown | 1-5 |
| Player size | ~2000 bytes | <1900 bytes | Unknown | ~3000 bytes |
| Rastertime | 23-27 lines | 28-33 lines | **7-8 lines** | 23-27 lines |
| Wave table | 1 byte/entry | 2 bytes/entry | Unknown | 1 byte/entry |
| Vibrato | Yes (Vib1/Vib2) | **Not in V5 table** | Unknown | Yes (V4 code) |
| Hard restart | Testbit | Uncertain | Unknown | Testbit (V4 code) |
| Packer | Built-in | SYS $2E00 | Unknown | Built-in + turbotape |
| Pulse/filter limit | All channels | All channels | **Some channels only** | All channels |

### V5 Missing Features vs V4
The Chordian comparison table lists V5 as having **no vibrato** and **no hard
restart** support. This aligns with the reduced 8-byte instrument format
(V4 has 11 bytes including Vib1, Vib2). V5 may implement vibrato through
the 2-byte wave table entries instead (waveform + note offset per frame),
trading per-instrument vibrato for more flexible wave table control.

### V7.1 Specific Additions
- "Player improvements"
- "Filters and direct AD/SR sets" — suggests additional sector commands for
  real-time ADSR/filter changes during playback

---

## 15. Gaps — What We Still Don't Know

The following details were NOT found in any online source:

1. **V5 instrument format**: Exact mapping of the 8-byte V5 instrument
   format. Which fields were removed/consolidated from V4's 11 bytes?

2. **V5 wave table 2-byte format**: What do the two bytes mean? Likely
   waveform + note/transpose (matching Cadaver's generic description),
   but unconfirmed.

3. **Drum/cymbal synthesis details**: FX byte bits 0 ($01=drum) and 7
   ($80=cymbal) trigger special synthesis modes. No source describes
   exactly what the player does differently in these modes (likely rapid
   noise-to-wave transitions for drums, sustained noise for cymbals).

4. **Pulse width 3-byte implementation**: PW1/PW2/PW3 in the instrument
   map to entries in the pulse speed table at +$0644, but the exact
   cycling algorithm (how the 3 bytes interact, when direction reverses
   based on PW-L limit) is only known from disassembly.

5. **Filter definition 6-step envelope**: The exact algorithm for the
   filter step processor (how R, T, Cutoff, RT, ST, S1-S6, X1-X6
   interact) is not documented anywhere online.

6. **Glide implementation**: $A0-$BF sector commands trigger portamento,
   but the pitch-slide algorithm (linear? per-frame delta? target-based?)
   is undocumented.

7. **$C0-$DF command range**: These sector commands are listed as
   "additional commands (volume, etc.)" but their exact meanings are
   unknown from public sources.

8. **V6 format**: Completely unknown. 7-8 rasterlines suggests
   significant player simplification.

9. **DMC V3.0**: Listed in CSDb release timeline but no information found
   about what changed from V2.

10. **"Dual effect" FX flag (bit 6, $40)**: Described as "half-speed
    processing" but exact behavior undocumented.

---

## Sources

### CSDb (Commodore Scene Database)
- [DMC 4.0](https://csdb.dk/release/?id=2596)
- [DMC V5.0](https://csdb.dk/release/?id=2594)
- [DMC V7.0](https://csdb.dk/release/?id=2629)
- [DMC V5.1+ Package](https://csdb.dk/release/?id=2600)
- [DMC V5.4 by Samar](https://csdb.dk/release/?id=36658)
- [DMC 4 Editor 1.0](https://csdb.dk/release/?id=250645)
- [DMC 4 Editor 1.1](https://csdb.dk/release/?id=251057)
- [Graffity group page](https://csdb.dk/group/?id=193)
- [Sound Design hints & tips forum](https://csdb.dk/forums/index.php?roomid=14&topicid=97576&showallposts=1)

### Lemon64
- [DMC 4.0 Player idle channel](https://www.lemon64.com/forum/viewtopic.php?t=48548)
- [DMC V4 is back in 2025](https://www.lemon64.com/forum/viewtopic.php?p=1055912)
- [DMC 6](https://www.lemon64.com/forum/viewtopic.php?t=24476)
- [DMC 4 Instructions](https://www.lemon64.com/forum/viewtopic.php?t=80234)

### Technical References
- [Cadaver — Building a musicroutine](https://cadaver.github.io/rants/music.html)
- [Triad — A SID player routine](https://dflund.se/~triad/krad/sidmidi.html)
- [Chordian — C64 editors comparison table](http://chordian.net/c64editors.htm)
- [Chordian — Comparison blog post](https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/)
- [SID Preservation — Editors](https://sidpreservation.6581.org/sid-editors/)
- [Restore64.dev — C64 disassembler](https://restore64.dev/)

### Player Identification
- [cadaver/sidid](https://github.com/cadaver/sidid/blob/master/sidid.nfo)
- [WilfredC64/player-id](https://github.com/WilfredC64/player-id)

### Scene History
- [Scene.hu — Graffity](https://www.scene.hu/tag/graffity/)
- [Demozoo — Brian/ABS/AxA/GRF/TIA](https://demozoo.org/sceners/1711/)
- [Demozoo — DMC tagged productions](https://demozoo.org/productions/tagged/dmc/)

### Tutorials & Documentation
- [TND64 — Music Scene tutorial](http://www.tnd64.unikat.sk/music_scene.html) (SSL issues, use HTTP)
- [HVMEC — DMC V5.0](https://hvmec.altervista.org/blog/?p=700)
- [HVMEC — DMC V2.1+](https://hvmec.altervista.org/blog/?p=504)
- [HVMEC — DMC V4.0 pro](https://hvmec.altervista.org/blog/?p=570)
- [HVMEC — DMC V4.0 2x](https://hvmec.altervista.org/blog/?p=541)
- [HVMEC — DMC V4.3++](https://hvmec.altervista.org/blog/?p=630)
- [Chipmusic.org — C64 Music for Dummies](https://chipmusic.org/forums/topic/8104/c64-music-for-dummies-c64-tutorial/)

### Pouet.net
- [DMC 4.0](https://www.pouet.net/prod.php?which=13452)

### Other
- [Zimmers.net — C64 audio editors FTP](https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html)
- [Driving the SID chip (academic paper)](https://www.gamejournal.it/driving-the-sid-chip-assembly-language-composition-and-sound-design-for-the-c64/)
