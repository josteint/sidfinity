# CyberTracker Online Manual — Fetched Text
# Source: http://noname.c64.org/tracker/manual_online.php
# Fetched: 2026-06-14 (multiple fetch passes)
# Author: CyberBrain (Bjarke Nørgaard Laustsen), No Name
# Version: V1.01 (also covers V1.00)
# Reliability: HIGH — live site responding, content confirmed consistent across passes

---

## Overview / Core Structure

CyberTracker is a FastTracker-style music editor native to the Commodore 64, designed
by CyberBrain of No Name. It has two main editors:

- **Pattern Screen**: Compose notes across 3 SID channels
- **Instrument Editor**: Create sounds via 8 graphical envelopes

Navigation: Escape key goes back to main menu; F1 = play song; F3 = stop; F5 = play current pattern.

---

## Pattern Format

Each line has THREE channels. Line structure:
```
'--- 00000 --- 00000 --- 00000'
```
Per channel: `NOTE INSTRUMENT EFFECT`

- **Note** (3 chars): `C-4`, `C#4`, ..., `B-7`, or `---` (empty), `.` (gate/release), `,` (stop)
- **Instrument** (2 hex digits): `00`–`1F` (0 = last used)
- **Effect** (3 hex digits): effect-number (1 digit) + parameter (2 digits); Eyx uses 2+1

### Note ranges
- Notes: C through B, octave 0–7
- "The B-7 note is above the C64's frequency-range...the only note the C64 won't play correctly."
- Rshift+F1–F7 selects octaves 1,3,5,7; Lshift+F1–F5 selects octaves 2,4,6

### Special note values
- `---` = no note (no change)
- `.`  = gate note (triggers release/fade-out phase of envelope)
- `,`  = stop sound (immediate silence)

### Pattern constraints
- Max lines per pattern: **128** ($80)
- Max patterns total: **256** ($00–$FF)
- Total pattern memory: **796 lines** ($31C)

---

## Track / Song Structure

"A 'track' is simply an order of patterns. The track-editor has 2 columns - the left
column is the line-number in the track-editor (you can't change those), and the right
column are the number of the pattern."

- Each track line references one pattern number ($00–$FF)
- Max track lines: **255 per song** (512 total track memory / $200)
- Loop point set with `R` key
- Multiple songs per file: "all songs share the same patterns/instruments/whatever,
  the only difference between songs is which patterns that will be played after each other"
- Switch songs with `@` / `@`+Rshift
- Max songs per file: 255 (song numbers $01–$FF; $00 is a song)

---

## Instrument System

### Instrument count
- **31 instruments** ($01–$1F)
- Instrument 0 means "last used"
- Load/save individual instruments supported
- Max instrument length: **65,536 ticks** = 21.84 minutes

### The 8 Envelopes

Each instrument has exactly 8 envelopes. "The instrument is made out of 8 envelopes.
Each envelope does something different to the sound."

#### General envelope mechanics
- X-axis = time (rightward = later); Y-axis = value
- Add points with Insert; move cursor with cursor keys
- Move a point: Lshift + cursor
- "When an envelope has finished (reached the last point + no loop selected) it won't
  change the value anymore." (holds last value)
- Loop: press `L` to toggle; `S`+Lshift to set loop start point
- Sustain gate: a vertical dotted line; player halts here until the gate-note (`.`) is
  received in the pattern. Gate before reaching the line = fade from current volume.

#### Total envelope memory: **768 points** ($300) shared across all envelopes of all instruments

---

### Envelope 1: Volume

"ADSR-based with special first 4 points; sustain points movable."

- First 4 points are Attack, Decay, Sustain_level, Release — their TIME positions
  cannot be moved freely (locked to 16 ADSR values each: 0–$0F)
- The vertical dotted line is the sustain gate boundary
- Y-axis: volume 0–$0F

The gate note (`.`) in the pattern:
- If received before sustain line: fades from current level
- If received after sustain line: player has already passed it — no gate effect

---

### Envelope 2: Waveform

"Only the points themselves (not the lines between them) matter."

Selects from: **TRIangle, SAWtooth, PULse, NoiSE** (standard SID waveforms)
Y-axis values: encoded as SID waveform nibble bits

---

### Envelope 3: Pulse Width

For pulse waveform only.
- Y-axis range: **$000–$FFF** (0% to 100%)
- $800 = 50% duty cycle

---

### Envelope 4: Filter Pass

"Only the points themselves matter."

Controls filter bandpass selection and on/off.
- Value $0 = no filter
- Bit fields (values 0–7 usable): 0=lowpass, 1=bandpass, 2=highpass, 3=voice3off
  (bits can combine for multimode)

"Remember there can only be ONE filterpass/cutoff/resonance-value for ALL 3 CHANNELS
at one time! If you try to use different filter-values in the 3 channels they will
fight to get their value sent to the sid-chip. The lowest channel will win."

---

### Envelope 5: Cutoff

Controls filter cutoff frequency.
- Standard X/Y envelope (lines between points DO matter — continuous interpolation)
- Range: 0–2047 ($000–$7FF, 11-bit SID cutoff)

---

### Envelope 6: Resonance

Controls filter resonance.
- Y-axis range: 0–$0F

---

### Envelope 7: Pitch

Modifies pitch (frequency).
- Y-axis: $0000–$FFFF; **middle value $8000 = normal pitch** (no modification)
- Values above $8000 = pitch higher; below $8000 = pitch lower

---

### Envelope 8: Pitch Control

Controls the behavior of the pitch envelope.
- Y-axis: $0 or $1
  - $0 = relative pitch (normal; pitch-envelope modifies the note frequency)
  - $1 = absolute pitch (value sent directly to SID; the written note has no effect)
- "Only the points themselves matter" (same as waveform/filterpass)

---

## Vibrato / Arpeggio (per instrument)

Each instrument has a vibrato/arpeggio block separate from the 8 envelopes:

**Vibrato:**
- Speed: "should always be >$F0" (higher = faster)
- Depth: $00 = vibrato off; higher = more pitch modulation

**Arpeggio:**
- Makes chords using one channel
- First note = note written in pattern
- Second note = base note + x halftones
- Third note = base note + y halftones
- Cycles continuously until new note starts

---

## Effect Commands (Complete — Appendix B)

Format: X (effect number, 1 hex digit) + YZ (parameter, 2 hex digits)
Exception: Eyx effects use 2-digit effect code + 1-digit parameter.

### 0xy — Arpeggio
"Syntax: 0 + 1st halftone + 2nd halftone."
Creates chords by cycling base note / base+x / base+y halftones. `0FF` = disable arpeggio.
Continues until disabled or new note.

### 1xx — Portamento Up
"Syntax: (1 or 2) + speed."
Slides pitch upward each tick at given speed. `00` = reuse last value.

### 2xx — Portamento Down
Slides pitch downward. Same parameter behavior as 1xx.

### 3xx — Tone Portamento
"Syntax: 3 + speed."
Slides toward target note. No hardrestart; envelopes do NOT restart on combined note.

### 4xx — Vibrato
"Syntax: 4 + speed + depth."
Applies vibrato. `00` = disable. Continues until disabled or new note.

### 5xx — Cutoff-Add Slide Up
"Syntax: (5 or 6) + speed."
Increases cutoff add-value each tick. Persists across song until reset with `780`.

### 6xx — Cutoff-Add Slide Down
Decreases cutoff add-value.

### 7xx — Set Cutoff-Add
"Syntax: 7 + add-value."
- $80 = no add/subtract
- >$80 = add to cutoff
- <$80 = subtract from cutoff

### Axx — Pulse Width Slide Up
"Syntax: (A or B) + speed."
Increases pulse width each tick. `00` = reuse last value.

### Bxx — Pulse Width Slide Down
Decreases pulse width.

### Cxx — Set Sustain
"Syntax: C + (0 or 1) + sustain_volume."
- C0x = stop volume envelope (hold at value x)
- C1x = allow envelope to resume
- Max sustain value: $0F

### Dxx — Multi-Effects Jump
"Syntax: D + multieffect-linenumber."
Jumps to that line in the multi-effect table. Executes all effects sequentially until END.
`D00` = reuse last parameter (does NOT jump to line 00).

### E0x — Toggle Filter On/Off
"Syntax: E0 + value."
- 0 = filter off on channel
- 1 = filter on

### E1x — Set Attack
Override volume-envelope attack value ($0–$F).

### E2x — Set Decay
Override volume-envelope decay value ($0–$F).

### E3x — Set Release
Override volume-envelope release value ($0–$F).

### E4x — Set Waveform
"Syntax: E4 + waveform."
- Bit 0 = triangle
- Bit 1 = sawtooth
- Bit 2 = pulse
- Bit 3 = noise
"Avoid values above 8 (causes noise lockup)."

### E7x — Set Resonance
"Syntax: E7 + resonance."
Sets filter resonance for ALL channels. Replaces resonance-envelope value. Range $0–$F.

### E8x — Set Test/Ring Mod/Sync/Gate
"Syntax: E8 + value. Bits: 0=Gate, 1=Sync, 2=Ring mod, 3=Test."
Controls SID control register lower nybble directly.

### E9x — Set Filter Passband
"Syntax: E9 + passband."
- Bits: 0=lowpass, 1=bandpass, 2=highpass, 3=voice3off
- Values above 8 disable voice 3.

### ECx — Set Global Volume
"Syntax: EC + volume."
Default: $F (full volume). Range $0–$F.

### EDx — Pattern Break
"Syntax: ED + something."
Stops pattern execution after current line. Parameter has no effect.

### EEx — Skip Note Hard-Restart
"Syntax: EE + value."
MUST accompany a note. Value 1 = skip hardrestart; other value = normal hardrestart.
Hard restart technique credited to JCH/Vibrants documentation.

### Fxx — Set Speed
"Syntax: F + speed."
Number of ticks per pattern line. Lower = faster. F00 = stop playback.
"Speeds below 3 cause hardrestart issues."

---

## Multi-Effect Table

"The list is $FF lines long (line $00 is not used)."
- **255 usable lines** ($01–$FF)
- Same format as pattern effects (3 hex digits per line)
- Executed sequentially from Dxx jump target until END marker
- END: press `E` in the command column

---

## Tempo / Speed System

- Speed = ticks per pattern line (set by Fxx)
- 1 tick = 1/50 second (PAL) or 1/60 second (NTSC)
- BPM fixed at 125 PAL at default speed
- Swing: alternate different Fxx on consecutive lines
- Note: "Speeds below 3 cause hardrestart issues"

---

## Memory Constraints (Total shared pool)

| Resource            | Limit       | Hex    |
|---------------------|-------------|--------|
| Pattern lines       | 796         | $31C   |
| Track lines         | 512         | $200   |
| Envelope points     | 768         | $300   |
| Instruments         | 31          | $1F    |
| Multi-effect lines  | 255         | $FF    |
| Patterns            | 256         | $100   |
| Max pattern length  | 128 lines   | $80    |
| Max inst. duration  | 65,536 ticks| ~21.84 min |

---

## Version Compatibility

- V1.01 loads V1.00 files (100% backward compatible)
- V1.00 cannot reliably load V1.01 files

---

## Keyboard Reference (Appendix A — condensed)

### Universal
- F1 = Play song
- F3 = Stop
- F5 = Play current pattern
- Rshift+F1–F7 = octave 1,3,5,7
- Lshift+F1–F5 = octave 2,4,6

### Pattern Editor
- Letter/number = enter notes
- Space = insert empty (delete note)
- `,` = gate note; `.` = stop sound
- Del = delete line; Insert = insert line
- Home/Clr = first/last line
- Ctrl = tab to next/previous channel
- `/` = move 16 lines down/up
- `;` / Rshift+`;` = next/previous pattern
- `=` = scroll track window
- `@` = next song; Rshift+`@` = previous song
- `*` = increase pattern length; Lshift+`*` = make 32 lines
- `+`/`-` = increase/decrease instrument
- Lshift+`8`/`9`/`0` = toggle channels 1/2/3
- Restore = toggle edit mode
- Stop+3/4/5 = cut+copy/copy/paste CHANNEL
- C=+3/4/5 = cut+copy/copy/paste PATTERN
- Lshift+3/4/5 = cut+copy/copy/paste BLOCK
- Return = go to Track Editor
- Return+Rshift = go to Instrument Name Editor
- `~` = go to Multieffect Editor
- `<-` = go to Main Menu

### Track Editor
- `R` = set song restart point
- `@` / Shift+`@` = next/previous song
- Return/`~`/`<-` = exit

### Envelope Editor
- Cursor = select point
- Ctrl = jump 16 points
- Insert = insert point; Insert+Rshift = insert with current value
- Del = delete point
- Lshift+cursor = move point
- `L` = toggle loop; Lshift+`S` = set loop start
- `P` = push points left; Rshift+`P` = pull points right
- `~` = swap windows
- Return/Return+Rshift = go to/from Point Editor

---

## Site Structure (noname.c64.org/tracker/)

- `/` = main page (news, module releases, testimonials)
- `/features.php` = feature list
- `/downloads.php` = download links (tracker, packer, exe maker, instrument packs)
- `/manual.php` = manual index (links to Word .doc downloads + online manual)
- `/manual_online.php` = FULL online manual
- `/screenshots.php` = screenshots

### Manual downloads (from manual.php)
- V1.01 manual in zipped Word format
- V1.01 fileformat guide (fixed version) — "ct_v101_fileformat_fixed.zip"
- V1.00/V1.01 quick effect reference
- V1.00 manual (Word format)
- V1.00 fileformat guide (fixed version)
- "Getting started" guide

NOTE: The fileformat guide is a SEPARATE document from the online manual.
The fileformat guide ("fixed version: 13/11/2001") contains the binary layout
of .ct and .ci files. The online manual does NOT describe the binary format.
