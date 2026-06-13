# Soundmaster V3.1 — German Manual (translated to English)

<!-- PROVENANCE
source_url: https://csdb.dk/getinternalfile.php/115254/Soundmaster_v3.1_[german].pdf
fetched_via: curl with Firefox UA (Mozilla/5.0 X11; Linux x86_64; rv:109.0 Firefox/115.0)
fetch_date: 2026-06-13
author: Walter Konrad (manual author, per PDF signature page 18)
content_date: 1989 (Soundmaster V3.1 release year per CSDb #90307)
reliability: PRIMARY — official manual, PDF fetched directly from CSDb file archive;
             18 pages, 111 KB; scanned/typed in C64 font by Walter Konrad.
             Note: CSDb release page #90307 credits the PDF upload to user "Fred" (March 2013),
             who states "I've also uploaded a german PDF file written by Walter".
-->

---

## Overview

Soundmaster V3.1 is a C64 music editor and player system by SoedeSoft (Jeroen Soede — player
code; Michiel Soede — editor). The manual opens with:

> "This program enables you to compose the best pieces of music with your C64 in a fast and
> unconventional way."

The system is organised around a **three-level song hierarchy**: Songs → Blocks → Bars → Steps,
with a separate **Sound editor** for instrument/timbre definition.

---

## Song Structure Hierarchy

### Level 1 — Steps (lowest level: the song arrangement)

The **step editor** ("Stepedit") is the top-level song arrangement view. Each step entry has:

```
nr   trk1 tp   trk2 tp   trk3 tp
00   03   fe   01   0c   05   03
```

Fields:
- `nr` — step number
- `trk1 / trk2 / trk3` — bar number assigned to each of the three tracks (voices) at this step
- `tp` (transpose) — per-track transpose value **added to every note in the current bar** (no
  "transpose off" override). Value `$fe` means subtract 2 from every note; value `$0c` adds 12
  (= 1 octave). This is a **signed offset applied note-by-note** at playback, not a pitch shift
  of the stored note bytes.

### Level 2 — Blocks

The **block editor** ("Blockedit") groups a range of steps into a playable block:

```
nr   b1-b2   tp   s1   s2   s3
00   00 03   06   00   01   03
```

Fields:
- `nr` — block number
- `b1-b2` — play from step $00 to step $03 (inclusive)
- `tp` — this value is **added to all transposes in all 3 tracks** for the entire block duration
- `s1/s2/s3` — add this value to every sound number (instrument index) for each track

Note: the "s3" column in the example adds 3 to every sound number in track 3.

### Level 3 — Bars (pattern data)

The **bar editor** ("Bar edit") contains the actual note/sound data, displayed one bar at a time.

Each bar row encodes:
```
45!01   ++   00   --   00   --   00   ; 45!=reverse
```

Column layout (left to right):
1. **Note + sound** — first number is note pitch, second is sound number
2. `++` and `--` — continuation/rest indicators
3. `!` suffix on a note = **reverse** (= the gate inversion flag; see below)

#### Note encoding (per-note byte format)

A note cell encodes multiple fields in a compact representation:

| Field | Bit position | Meaning |
|---|---|---|
| **Octave** | leftmost column | octave 0–7 |
| **Note name** | `0=C 1=C# 2=D 3=D# 4=E 5=F 6=F# 7=G 8=G# 9=A A=A# B=B` | chromatic semitone within octave |
| **Sound number** | `$00–$2F` | instrument / sound preset index (48 sounds) |
| **bit $40** | Transpose off flag | when set, the per-track transpose is NOT applied to this note |
| **bit $80** | Portamento flag | enables portamento on this note (C= key in editor) |
| **Sustain note** | separate flag | note rings until next note/rest |
| **Cycle trigger** | separate flag | triggers the arpeggio/waveform cycle |
| **Reverse** (!) | display marker | if note is NOT reverse, it is not played; if reverse, it IS played — this is the standard gate/note-on semantic |

The "first number is the note, the second is the sound number, etc." — the display alternates
note and sound columns per row.

#### Bar edit key commands

| Key | Function |
|---|---|
| F1 | Next bar |
| F3 | Previous bar |
| RETURN | Return to main menu |
| SHIFT+RETURN | Next row within bar |
| C= (Commodore key) | Toggle reverse/normal on current note |
| SHIFT+L | Copy current bar to buffer |
| SHIFT+S | Paste buffer into current bar |

---

## Main Menu Key Reference

| Key | Function |
|---|---|
| M | Restart current song from beginning |
| P | Toggle music on/off |
| F1 | Play song from current block |
| F3 | Set first step/block marker |
| F5 | Set last step/block marker |
| F7 | Enter block/track edit submenu |
| + | Advance 8 steps forward |
| - | Go 8 steps backward |
| RETURN | Edit current row |
| SHIFT+E | Erase bar — place cursor on bar number and press SHIFT+E |
| SHIFT+T | Transfer/copy steps from [first step] to [last step] to current cursor position (music must be stopped first) |
| SHIFT+D | Disk menu |
| S | Enter sound editor submenu |
| SHIFT 1/2/3 | Toggle voice/track 1/2/3 on/off for auditioning |
| CTRL+1 | Swap track 1 with track 3 |
| CTRL+2 | Swap track 2 with track 1 |
| CTRL+3 | Swap track 3 with track 2 |
| + / - (in block range) | Raise/lower all transposes from [first block] to [last block] |
| Init | Clears ALL music and sound data — WARNING, destructive |

---

## Special Functions (Spezial Funktionen)

Accessed from main menu. Global song parameters:

| Parameter | Description |
|---|---|
| **bar length** | Number of rows per bar (all bars share this length) |
| **Speed** | Playback speed (tempo) |
| **Filter mode/volume** | SID register $D418 (filter mode + master volume) |
| **Resonance/filtervoice** | SID register $D417 |
| **$D417 $xy** | Lower nibble y selects which voice is routed through the filter: y=1→voice 1, y=2→voice 2, y=4→voice 3 |
| **Filter start on voice** | When filter is on voice x, this value must be x−1 |
| **Filter count time** | When using "filter count" in a sound: this number gives the time interval at which the filter count value is added to $D416 filter frequency. Values > $80 = no time limit (free-running). |
| **Vibrato level** | Global vibrato speed (normal = 4) |
| **Filter type** | Can only be used when filter count time < $80. Values: $00 or $01. |
| **Levelinc. start** | When using "inc.vibrato", vibrato starts at this value |
| **Pulshigh max/min** | When using "pulse count" in a sound effect: defines the max/min of the pulse width high-byte during pulse sweep. |
| **Constant effect value** | Value $7F in the arpeggio table indicates "current note". Use this to create a tick at the start of a sound (waveform must be $81 for this to work). |
| **Highest bar number** | Highest bar number in use |
| **Unused bar number** | Lowest unused bar number |

---

## Disk Menu

| Key | Function |
|---|---|
| D | Show disk directory |
| L | Load music. Directory is loaded into memory; use SHIFT+Ln for second disk; +/- swap disk slots; cursor + RETURN to select/load; RUN/STOP to cancel |
| S | Save music (song data only). If filename already exists on disk, it is deleted first. RETURN to cancel. |
| R | Save music + player routine together. When loaded without Soundmaster, music can be started via `SYS $6000` or `SYS 6*4096`. |
| C | Save a single sound. First select the sound number in the sound editor, then save. |
| E | Load a sound. The sound is appended after the highest current sound number. (RUN/STOP aborts.) |
| N | Load a sound at the current position, replacing the existing sound there. (RUN/STOP aborts.) |

**Key fact:** `SYS $6000` is the canonical standalone player entry point for music saved with "R"
(music + routine). This maps to the PSID init address observed in HVSC: init=$6000, play=$6006.

---

## Sound Editor

### Structure

Each sound consists of **2 or 3 parts** (2 parts if no arpeggio/waveform table is used; 3 if
both are used):

- **Part 1:** Waveform + arpeggio/waveform table pointers
- **Part 2:** Envelope + pulse + vibrato + portamento + filter parameters
- **Part 3 (optional):** Arpeggio & waveform table data

Sound numbers run $00–$2F (48 sounds). The 4th number in Part 1 is the "2nd sound number"
($00–$1F, 32 possible) that provides envelope/pulse/etc. when the arp/wave table is active.

Sound editor key commands:
| Key | Function |
|---|---|
| F1 | Increment sound number |
| F3 | Decrement sound number |
| F7 | Toggle between arpeggio edit and sound edit |

---

### Part 1: Waveform / Arpeggio Pointer Block

**Field 1 (Waveform register 1):** Written to SID $D404 (voice control register) for every new
note. Bit 1 (gate) must be set, otherwise no sound is produced. See SID manual for waveform bit
definitions.

**Field 2 (Waveform register 2):** Also a waveform value, written to the voice control register
at every `--` (rest/gate-off) row in the bar. This is the "release waveform" — the waveform
applied when a note ends.

**If arpeggio/waveform table is NOT used:** the 3rd number (effect-end) must be $00.

**If arpeggio/waveform table IS used**, Part 1 becomes a 4-field pointer block:
1. Start address of arp & wave table ($00–$FF, table index)
2. Repeat address — the arp loops back here when it reaches the end
3. End address + 1
4. 2nd sound number ($00–$1F) — provides att/dec, sus/rel, pulse start, etc. for the duration
   of the arp/wave table. Range $00–$1F.

---

### Part 2: Envelope and Modulation Parameters

| Parameter | SID register / Meaning |
|---|---|
| **Attack/Decay** | SID $D405 — initialised from the waveform register |
| **Sustain/Release** | SID $D406 — Release phase starts when `--` appears in a bar row |
| **Pulse start** | Initial pulse width. Low nibble = high nibble of PWlo ($D402); high nibble = PWhi ($D403). ("1 nibble is half a byte" — the manual's own description of the 8-bit field packing.) |
| **Pulse count level** | Delta added to PWlo register per tick when pulse sweep is active. Added each time a new sound starts. |
| **Vibrato/increase** | < $80: vibrato amplitude. ≥ $80: the vibrato level addition rate (the amplitude increases while a sound plays). Vibrato starts from the "Levelinc. start" value in Special Functions. |
| **Delay/Portamento count high** | Bits 0–2: portamento count high byte ($00–$07). Bits 3–7: vibrato start delay. Example: $21 → delay=4, port.high=1; $08 → delay=1, port.high=0. |
| **Portamento count low** | Low byte of the portamento counter |
| **Filter start** | SID $D416 initial filter frequency |
| **Filter count** | Value added to $D416 each tick; $FE means $D416 = $D416 − 2 (decrement by 2) |

---

### Part 3: Arpeggio & Waveform Table

The arpeggio display looks like:
```
arp.: 00!7F!07!03   04   00   7f!00!   ; xx!=rev.
```

- `!` (reverse) marker on an arp entry — "yellow number" (played only once, not looped).
  Entries without `!` are "white numbers" (looped portion).
- `$7F` in the arp table = use the **constant effect value** (= the current note's pitch). This
  creates the "tick at start of sound" drum trigger effect when waveform is $81.
- A non-$7F entry = a semitone offset from the base note (signed).
- The arp table simultaneously specifies **arp entries AND waveform entries** in alternating
  fashion — the table interleaves frequency offsets with waveform bytes.
- The **repeat address** marks the loop-back point; entries before it play once (yellow/one-shot).
- **End address + 1**: the table scan stops here.

The **waveform table** (`wave:`) is a parallel sequence:
```
wave: 11  81  49  41  41  41  41
```

Each byte is written to the SID voice control register ($D404) during the arp cycle:
| Bit | Meaning |
|---|---|
| bit 1 | Gate |
| bit 2 | Sync |
| bit 3 | Ring Modulator |
| bit 4 ($08) | When set: allows vibrato or portamento to be used during the arpeggio |
| bits 5–8 | Waveform selection (triangle / saw / pulse / noise) |

---

## Player Entry Points and Memory Map

From the Disk Menu "R" save (music + routine together):

- `SYS $6000` or `SYS 6*4096` starts the music (init + play)
- In PSID context this maps to: init=$6000, play=$6006

This matches the most common init/play pair in HVSC for this engine
(309 out of 929 SIDs load at $6000, play at $6006; second most common is $2000/$2106 with 135).

The signature string embedded in the player binary: `"88 SOEDESOFT-"`

---

## Version Notes (from sidid.cfg byte signatures)

Three player variants are identified by sidid:

**Soundmaster V1.0** (sidid signature fragment):
```
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4
B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C
```

**Soundmaster V3.1** (sidid signature fragment):
```
A9 ?? 9D ?? ?? 4C ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```

**Soundmaster V3.2** (sidid signature fragment):
```
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ??
BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60
```

The V3.2 signature is longer and adds an `18 / 7D / 7D` (CLC + ADC indexed) pattern not present
in V3.1, suggesting an additional accumulation step in the frequency/note write path.

The top-level sidid group is `SoedeSoft` (not version-specific); the version sub-tags
`(Soundmaster_V1.0)`, `(Soundmaster_V3.1)`, `(Soundmaster_V3.2)` are sub-signatures.

---

## Summary: Effect Chain as Described by the Manual

The Soundmaster V3.1 effect chain (per-note, per-tick) includes:

1. **Waveform** — from sound Part 1 Field 1, written to $D404 on note trigger
2. **ADSR envelope** — Attack/Decay ($D405), Sustain/Release ($D406)
3. **Pulse width** — initial value ("Pulse start") + optional running sweep ("Pulse count level")
   bounded by "Pulshigh max/min"
4. **Arpeggio** — offset table cycling through semitone offsets; optional one-shot prefix +
   looped body; $7F = "use current note" sentinel
5. **Waveform table** — parallel to arpeggio, updates $D404 per arp step; bit 4 enables
   vibrato/portamento within the arp
6. **Vibrato** — amplitude or increasing-amplitude mode; speed set globally ("Vibrato level");
   per-sound delay and initial level
7. **Portamento** — 16-bit counter (high 3 bits in "Delay/Portamento count high", low byte in
   "Portamento count"); enabled per-note with bit $80 in the bar note byte
8. **Filter** — $D416 (cutoff freq) set by "Filter start" per sound; "Filter count" adds/subtracts
   per tick; "Filter count time" gates the sweep rate; "Filter type" ($D417 filter mode bit);
   "Resonance/filtervoice" ($D417 resonance + voice routing); "Filter mode/volume" ($D418)
9. **Global transpose** — per-track-per-step offset applied to all notes in bar
10. **Block-level transpose** — additional offset applied to all track transposes in a block
11. **Block-level sound offset** — per-track sound number base added to all sound indices in block
12. **Transpose-off flag** (bit $40 in note byte) — suppresses the track transpose for that note
13. **Portamento flag** (bit $80 in note byte) — triggers portamento on that note

The "sustain note" and "cycle trigger" flags in the bar note byte complete the per-note controls.
