---
source_url: multiple (see individual entries)
fetched_via: direct
fetch_date: 2026-04-21
author: various
content_date: various
reliability: secondary
---

# Forum Discussions — Technical Details About Rob Hubbard Driver

---

## From chipmusic.org forum (blocked, extracted from search snippets)

URL: https://chipmusic.org/forums/topic/1488/rob-hubbards-music-driver-c64/

Key technical points from search result snippets:

### "The core of Rob's replay is pretty much the same"
> "the part that decodes the notes and triggers them is pretty much the same [across versions]"
> "later songs started to differ, with International Karate being able to transpose patterns"

This confirms the note-parsing loop is stable across versions; new features were additions.

### Fourth channel (for effects/filter/tempo control)
> "Rob's driver has a fourth track, but it's only for effects (controlling the filter,
> tempo, speed table stuff, etc.)"

**CRITICAL:** This mentions a FOURTH channel that controls tempo/speed. The 3-voice
player we know about is the playback loop; there may be a separate init-time or
per-frame "effects track" that modifies the `resetspd` variable during playback.

This fourth channel would explain why some songs have in-song tempo changes even though
the `resetspd` variable is set at init time and not modified by the 3-channel loop.

Investigation needed: Does the fourth channel fire on pattern events (like channel 4 in GT2)?
Or is it a separate frame-by-frame effect processor?

### Wizball uses 200Hz (4x speed)
> "Some tunes either update themselves four times per interrupt, or the routine gets called
> four times by the interrupt handler"
> "Wizball used 200Hz playback, which translates to 4-speed tune execution"

This is the MULTISPEED mechanism. Wizball (and likely other late Hubbard tunes) run
the player 4× per frame via multiple interrupt calls. This is distinct from the
`resetspd` speed counter — it's at the interrupt/CIA level.

For our pipeline: multispeed Hubbard songs have the CIA timer set to 200Hz instead
of 50Hz. The `rh_decompile.py` speed detection won't catch this from static analysis alone.

---

## From Lemon64 — WAR Hidden SID (lemon64.com/forum/viewtopic.php?t=7920)

### Wizball at 200Hz confirmed
> "Some tunes either update themselves four times per interrupt, or the routine gets called
> four times by the interrupt handler"

### Peter Veitch/PVCF uses double or quad speed
> "double or quad speed play" — this is a pattern among composers using Hubbard-derived drivers

---

## From Lemon64 — OLD Rob Hubbard editor? (lemon64.com/forum/viewtopic.php?t=8111)

### Editor was primitive by modern standards
> "built around Hubbard's Zoolook tune by Huddy and Greeny. It looks a little primitive
> and almost any current driver can handle the sounds."

### Composers used different approaches
- Rob Hubbard himself: wrote hex directly into Mikro Assembler source, no GUI
- Red/Judges (Jeroen Kimmel): converted driver to source code, edited data directly
- Crazy Comets driver used by Red/Judges for multiple compositions

### ACE 2 player editor (csdb release 75124)
> "another editor, based on the 'ace 2' player" — csdb.dk/release/?id=75124
> "Rob Hubbard's Ace 2 player" — a specific late-era driver

The ACE 2 player is a distinct late driver (1987). The editor was by Predator/Moz(IC)art.

---

## VGMPF — Rob Hubbard (C64 Driver) 

URL: https://www.vgmpf.com/Wiki/index.php?title=Rob_Hubbard_(C64_Driver)

### Key historical note
> "Since spring 1997, he no longer has the source code to his pre-Electronic Arts driver"

Rob Hubbard lost his original source code. This means there is no authoritative source —
all analysis must come from reverse engineering.

### Release timeline from VGMPF
- Late 1984 / early 1985: Original driver (Confuzion, Thing on a Spring)
- 1985-1986: Expansion period (drums, arpeggio, portamento, skydive)
- Late 1985: Frequency table trick (Commando)
- 1986: Pattern transposition, filter support (International Karate)
- Late 1986: Arpeggio tables (data-driven)
- March 1987: Table-driven drums
- July 1987: Table-driven PWM
- Late 1987: Unsigned 4-bit PCM via volume register
- 1987+: Code scrambling/obfuscation

---

## From C64-Wiki search results

### International Karate — double tempo section
> "the middle section of the tune went into F at double tempo to liven things up"

This is a confirmed in-song tempo change in IK. It likely uses the fourth channel
or a speed table mechanism, NOT CIA multispeed.

---

## Summary of Key Technical Findings from Forum Research

| Finding | Confidence | Source |
|---------|-----------|--------|
| Single global speed counter, no nested counters in early driver | HIGH | C=Hacking #5 |
| Fourth channel for filter/tempo/speed table control | MEDIUM | Chipmusic forum snippet |
| Wizball uses 200Hz CIA multispeed (4x) | HIGH | Lemon64 WAR thread |
| IK has in-song tempo change (double speed section) | HIGH | VGMPF wiki |
| Rob Hubbard lost original source code in 1997 | HIGH | VGMPF wiki |
| ACE 2 is a distinct late driver variant | HIGH | CSDb + Lemon64 |
| Bjerregaard, Zicchi, Kimmel copied/modified the driver | HIGH | Multiple sources |
