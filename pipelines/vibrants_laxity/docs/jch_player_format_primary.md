---
source_url: local: /home/jtr/sidfinity/tmp/vibrants_laxity_research/jch_np15_instructions.txt + jch_20g4_instructions.txt + jch_ed3_commands.txt + jch_ED37_SRC.txt
fetched_via: local read (files previously downloaded by concurrent session to tmp/vibrants_laxity_research/)
fetch_date: 2026-06-15
author: Jens-Christian Huus (JCH)
content_date: 1990-1991 (primary); addenda 1995
reliability: primary (JCH's own documentation and source code)
---

# JCH NewPlayer Format — Primary Source Documentation

**All content below is extracted verbatim or paraphrased from JCH's own documentation files
found in `/home/jtr/sidfinity/tmp/vibrants_laxity_research/`.** This is the canonical
reference for the JCH editor / NewPlayer format.

---

## Source files available

- `jch_ED37_SRC.txt` (96170 bytes, 5697 lines) — Full assembler source code for
  JCH Editor v3.03. Danish + English comments. Contains ZP layout (see below).
- `jch_20g4_instructions.txt` (307 lines) — Instructions for NewPlayer v20.G4 (May 1991)
- `jch_np15_instructions.txt` (542 lines) — Instructions for NewPlayer v15.G6 (Jul 1990)
- `jch_ed3_commands.txt` (178 lines) — Key guide for JCH Editor V3.02
- `jch_editor_zip/ed_texts/` — Full instruction set for all player versions:
  - 12_G3_IN, 14_G0_V2, 15_G6_IN, 17_G1_IN, 19_G1_V2, 20_G4_IN (player docs)
  - ED2_53_K, ED3_02_K (editor key guides)
  - ED6_EPIL (epilogue)
  - MEMO-V12 through MEMO-V18 (version memos)
  - PACK_5_3 (NP-Packer documentation)
- `jch_editor_zip/` — JCH's complete 1998 package (README.TXT, ED37_SRC.TXT, ED_TEXTS.ZIP, D64.ZIP)
- `jch_source/LAXITY.ZIP`, `jch_source/NP_15-20.ZIP`, `jch_source/SOURCE.ZIP`

---

## Zero-page layout (from ED37_SRC.TXT, lines 18–75)

This is the editor's ZP layout — the player's ZP layout will differ but share some conventions:

```
voicon  = $a0    ; voice-on control (00=on, 07=v2-off, 0E=v3-off, 19=v1-off)
vol     = $a2
credits = $a4
tpoin   = $a6
sinit   = $a8
ain     = $aa
getinit = $ac
getcom  = $ae
get2    = $b0
getins  = $b2
real    = $b4
setsid  = $b6
notes   = $b8
fintun  = $ba
arp1    = $bc
arp2    = $be
filttab = $c0
pulstab = $c2
instr   = $c4
v1      = $c6    ; voice 1 sequence pointer (lo)
v2      = $c8    ; voice 2 sequence pointer (lo)
v3      = $ca    ; voice 3 sequence pointer (lo)
lobyt   = $cc
hibyt   = $ce
slidtab = $d0
s0      = $d2    ; slide state voice 1
s1      = $d4    ; slide state voice 2
s2      = $d6    ; slide state voice 3
s3      = $d8
gat     = $da
nog     = $dc
trans1  = $de
sflag   = $e0
not     = $e2
vhzl    = $e4    ; vibrato hz low
vhzh    = $e6    ; vibrato hz high
next    = $e8
insnr   = $ea
ge02    = $ec
```

Voice sequence pointers: v1=$c6, v2=$c8, v3=$ca (2 bytes each = lo/hi of pointer).
Slide state: s0/s1/s2 at $d2/$d4/$d6 per voice.
Voice index stride in the EDITOR: voices at $c6, $c8, $ca (step = 2 bytes per voice).
This matches the player convention seen in sidid signatures (X=2/1/0 outer loop, step 2).

---

## The 8-Byte Instrument Table (NewPlayer V20.G4)

From `jch_20g4_instructions.txt`:

```
         00  00  00  00  00  00  00  00
         --  --  --  --  --  --  --  --
         A   B   C   D   E   F   G   H
```

- **Byte A**: ADSR Attack/Decay (SID $D405 format: hi nibble = attack, lo nibble = decay)
- **Byte B**: ADSR Sustain/Release (SID $D406 format: hi nibble = sustain, lo nibble = release)
- **Byte C**: Control flags (split nibbles in V20):
  - Bit 6 ($40): HiFreq drum mode (ON if set)
  - Bit 7 ($80): Hard restart (ON if set)
  - Low nibble ($0F): Arpeggio SPEED (0=fastest, F=slowest)
  - Examples: $40=hifreq, $83=hard-restart+arp-speed-3, $CF=both+very-slow-arp
- **Byte D**: Filter nibbles:
  - Hi nibble: Filter resonance (usually $F)
  - Lo nibble: Filter on/off switch + filter passband (same as V14)
- **Byte E**: Pointer to filter-sweep table entry
- **Byte F**: Pointer to pulsating table entry
- **Byte G**: Arpeggio pointer (gate ON = "+++" steps)
- **Byte H**: Arpeggio pointer (gate OFF = "---" steps; if G==H, only G used)

**Note from V15 docs:** In V15 the instrument is identical except byte C only controls
hifreq (no hard restart, no arp speed). V20 expanded byte C.

---

## Sequence Format (V20.G4)

From NP V15 instructions (the packing explanation):

### Unpacked sequence bytes

In the editor, every sequence step is:
- Note value (e.g., `30` = C-4)
- `7E` = "+++" (continue / tie note)
- `00` = "---" (rest)
- Each step is preceded by an `80` (duration = 0-length mini-step)

Example for `C-4 +++ +++ +++ +++ --- --- ---`:
```
80 - 30 - 80 - 7E - 80 - 7E - 80 - 7E - 80 - 7E - 80 - 00 - 80 - 00 - 80 - 00
```

### Packed sequence format (after NP-Packer)

After packing: `84 - 30 - 82 - 00`
- `84` = packed duration 4 for the following note
- `30` = note value (C-4)
- `82` = packed duration 2 for following rest
- `00` = rest

**Duration encoding:** High bit of the duration byte is SET ($80 base) + duration count.
So `84` = note lasting 4 duration-units, `82` = rest lasting 2 units.

**"Sxx" commands in sequence:** A super/slide table pointer (position xx in slide table).
When packer encounters `Sxx` it must emit the command byte + the pointer value.

### Sequence sentinel values

From V20 docs (arpeggio table section):
- `$7F` = arpeggio end mark (followed by loop pointer, like a sample)
- `$7E` = arpeggio repeat-last-step mark

From the sidid signatures and V3 player notes:
- `$FF` = sequence end
- `$FE` = sequence rest (silence this voice)
- `$FD` = sequence loop/restart
- `$7E` = tie note / continue (also used as arpeggio repeat)

---

## Super/Slide Table (V20.G4)

From `jch_20g4_instructions.txt`:

The super table is indexed by `Sxx` commands in sequences. Position $00 is **reserved for
hard restart settings** (default `0F 00`). All `Sxx` commands should start from position $01.

Commands present in V20 (unchanged from V18, except $8x removed):
- **Slide** (`$0x/$1x/$2x/$3x` first nibble)
- **Vibrato** (`$4x/$6x` first nibble)
- **Speed change** (`E0 0x`) — improved in V20 (no voice desync)
- **Volume** — in super table
- **Sustain** — in super table
- **Chord-change** (arpeggio change for instrument, $Cx range: `C0-DF`)

The hard restart `$8x` command is REMOVED from V20's super table (it's now in instrument byte C).

### Slide command (V15 format, unchanged in V20)

2-byte entry in super table:
```
         00 00
         -----
         AB CD

Nibble A = Recognize, direction and ignore-bit: 0/1/2/3
Nibble B/C/D = 3-digit speed (12-bit speed, $000-$FFF)
```
- `00 80` = Slide up speed $80 from note
- `10 80` = Slide up speed $80 from +++ or ---
- `20 80` = Slide down speed $80 from note
- `30 80` = Slide down speed $80 from +++ or ---

### Vibrato command (V15 format, unchanged in V20)

2-byte entry:
```
         AB CD

Nibble A = 4 (at note) or 6 (at +++ or ---)
Nibble B = "Feeling" / add value: 0=no feeling, 1-F adds to width each frame
Nibble C = Vibrato speed: 1=fast, F=siren-like, normally 3
Nibble D = Vibrato width: 0=maximum, 7=barely any, normally 0-3
```
Examples: `40 13` = speed 1, width 3 at note; `60 21` = speed 2 width 1 at +++

**Note from V15 docs:** The vibrato routine was originally done by Rob Hubbard and is used by
Laxity, JOZZ, Charles Deenen, and others. Makes vibrato equal across all octaves.

### Hard restart (old, in V15 super table, NOT in V20)

In V15, `$8x` = hard restart command (moved to instrument byte C in V20):
```
Nibble A = always 8
Nibble B = duration timer (0=off, 2=most common, max=GAME_SPEED)
Nibble C/D = new SUSTAIN value ($00 for true hard restart; other = echo/reverb effect)
```

### Arpeggio-change command (V15+, also V20)

```
Nibble A/B = instrument number (C0-DF: inst 0-31)
Nibble C/D = new arpeggio pointer value (00-FF)
```
Example: `C5 32` = instrument 5 gets new arp pointer $32.
Always stores new arp in BOTH byte G and byte H of instrument.

---

## Pulsating Table (V20.G4 — redesigned from V18)

From `jch_20g4_instructions.txt`. This is the "same system as used in LAXITY's player":

4-byte set:
```
         00  00  00  00
         --  --  --  --
         A   B   C   D
```

- **Byte A**: Start pulse width (lo-nibble = lo-pw, hi-nibble = hi-pw). $FF = don't change, continue current.
  Note: $08 = loud pulse, $10 = weak pulse
- **Byte B**: Speed of pulsating ($00-$FF)
- **Byte C**: Life-time of this set ($00-$7F frames) + direction bit (bit 7: 0=up, 1=down)
  Duration $00-$7F; add $80 to puls downward: `$84` = 4 frames downward
- **Byte D**: Pointer to next set (set number × $04 = byte offset)

JCH notes this is "the same system as used in LAXITY's player" — the Vibrants/Laxity
pulsating table uses 4-byte sets with jump pointers for looping programs.

Example (swing puls from $0C toward $0F then back):
```
00: 0C 40 08 04   ; start=$0C, add=$40, 8 frames up, → set 04
04: FF 40 84 08   ; continue, add=$40, 4 frames DOWN ($80 added), → set 08
08: FF 40 04 04   ; continue, add=$40, 4 frames up, → set 04 (loop)
```

---

## Filter Sweep Table (V20.G4 — redesigned from V18)

4-byte set, almost same as pulse table:
- **Byte A**: Start filter cutoff value ($00-$FE); $FF = don't change current
- **Byte B**: Speed (adding value; wraps — $FF subtacts 1 by wrap arithmetic)
- **Byte C**: Duration frames ($00-$7F); no direction bit — uses wrap arithmetic in B instead
- **Byte D**: Pointer to next set

First 4 reserved bytes (control bytes):
```
         02  03  00  00
         --  --  --  --
         A   B   C   D
```
- **Bytes A/B**: Half-speed selectors (speed 0 = use these two bytes as alternating speeds, 2-9 range)
- **Byte C**: Unused in V20.G3+
- **Byte D**: Voice-selector for filter sweep controller (00=voice1, 01=voice2, 02=voice3)

Filter adds ONLY (no subtract bit) — use $FF = subtract 1, $F0 = subtract 16 via byte wrap.
JCH notes this saves raster time.

---

## Arpeggio Table

From V15 docs and V20 docs:
- `$7F` = end mark + next byte = loop target pointer (like sample loop)
- `$7E` = repeat-last-step mark (added in V20; also in Laxity's and Jozz's players)
- `$80` and above = frequency offsets (positive)
- `$00-$7D` = notes (direct note values)
- Green highlight in editor for `$7F` entries; no highlight for `$7E`

---

## Register Write Model (derived from V20 docs)

Per frame (play() invocation):

1. **For each voice (X=2,1,0)**:
   - If hard-restart: at timer=$2 before note, write control=$88 ($D404/$D40B/$D412)
   - At note-on: write ADSR bytes A/B to $D405+voice/$D406+voice
   - Write freq lo/hi via freq table lookup to $D400+voice/$D401+voice
   - Apply vibrato: freq += vibrato_value (calculated)
   - Apply slide: freq += slide_speed (3-digit)
   - Write pulsating: $D402+voice / $D403+voice
   - Write control byte (waveform + gate) to $D404+voice
   - Apply filter sweep: write $D415 / $D416 / $D417 / $D418

2. **Once per frame**:
   - $D418 = master volume (typically $0F unless vol command active)
   - Filter: $D415 (cutoff lo), $D416 (cutoff hi), $D417 (filter mode/resonance)

**V20 specific:** Hard restart writes $88 to control then $00 on next frame to clear gate.
The timer=$2 means: 2 frames before next note trigger, begin hard restart sequence.

---

## Version History (from JCH's docs, confirmed by sidid)

| Player | Year | Key changes |
|--------|------|-------------|
| OldPlayer | 1987 | Nibble-field notes, no sequences |
| V5/V6 | 1989 | First production players with editor |
| V12 | 1990 | See MEMO-V12 (details not yet read) |
| V14 | 1990 | Direct Arpeggio Pointers, hifreq drum mode |
| V15 | 1990 | Super-table (slide+vib+hard-restart+arp-change), gate-on/gate-off arp |
| V17 | 1990 | Lower raster time variant |
| V18 | 1991 | Speed-change commands, various improvements |
| V19 | 1991 | Even lower raster time |
| V20 | 1991 | Last standard player — instrument byte C redesigned, pulse/filter redesigned |
| V21 (NP21.g4) | 2006 | Laxity's rewrite for modern use (same base format) |

---

## Laxity's Player vs JCH's Player (from JCH's 1988 README)

From `jch_source/-README-.TXT`:

- JCH got Laxity's player in **Turbo Assembler source form** on C64 in 1988
- Laxity composed "directly in a machine-code monitor" (no editor!)
- JCH composed in Laxity's player then was told to stop by Laxity at Dexion's copy-party
- JCH then wrote his own player ("NewPlayer")
- Laxity later joined Vibrants; both gained respect for each other

**Key technical fact from JCH docs on V20 pulse/filter tables:** "the same system as used
in LAXITY's player" — confirming that Laxity's pulse and filter tables used 4-byte sets
with loop-pointer chaining, and JCH copied this design in V20 (after using a different
approach in V14-V18).

**Vibrato routine credit:** "originally done by ROB HUBBARD - used by Laxity, JOZZ, Charles
Deenen among others" — the frequency-normalized vibrato calculation.

---

## Unread documents (in tmp dir, not yet processed)

- `jch_editor_zip/ed_texts/14_G0_V2.TXT` — V14 format docs (Direct Arpeggio Pointers)
- `jch_editor_zip/ed_texts/17_G1_IN.TXT` — V17 format docs
- `jch_editor_zip/ed_texts/18_IN.TXT` — V18 format docs (not listed in directory, may be in ZIP)
- `jch_editor_zip/ed_texts/MEMO-V12.TXT` through `MEMO-V18.TXT` — per-version change notes
- `jch_editor_zip/ed_texts/PACK_5_3.TXT` — packer docs (describes binary format produced)
- `jch_source/LAXITY.ZIP` — Laxity's original player source (if available)
- `jch_source/NP_15-20.ZIP` — Players V15-V20 source code
- `jch_source/SOURCE.ZIP` — Additional source
- `jch_editor_zip/d64_files/` — D64 disk images including JCH_SRC.D64 (V17/V19/V20 source)
