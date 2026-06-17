---
source_url: multiple — primary: cadaver.github.io/tools/ninjatr204.zip (readme.txt + nt2play.s + src/*), cadaver.github.io/tools/ninjatrk.zip (V1), cadaver.github.io/tools/gt2nt2.zip (gt2nt2.c)
fetched_via: curl
fetch_date: 2026-06-17
author: Lasse Öörni (Cadaver / Covert Bitops)
content_date: 2002 (V1), 2006 (V2.0), 2013 (V2.04)
reliability: primary
---

# NinjaTracker — Format Specification

Derived from primary sources: `readme.txt` (V2.04 + V1), `nt2play.s` (V2.04 + V1),
`src/ninjatr2.s`, `src/nt2songdata.s`, `src/nt2var.s`, `src/nt2packer.s`, and
`gt2nt2.c` (GT2→NT2 converter). All files saved under `docs/src/`.

## 1. Overview

NinjaTracker is a minimal C64 music editor by Lasse Öörni (Cadaver) of Covert Bitops.
Two major version lines exist:

| Version | CSDb ID | Release | HVSC count |
|---------|---------|---------|------------|
| V1.x (V1.1 latest) | #7206 | 2002 | 18 SIDs |
| V2.0 | #39374 | 2006 | — |
| V2.04 (canonical) | #119721 | 2013 | 93 SIDs |

The player source (`nt2play.s`) ships as DASM format assembly and IS the canonical
format documentation. It requires DASM assembler + Pucrunch + Cadaver's c64tools to rebuild.

GoatTracker2→NinjaTracker2 converter (`gt2nt2.zip`) provides a C implementation of
the on-disk `.sng` format, useful as a second reference.

## 2. Constants (from src/ninjatr2.s)

```
MAX_SONGS       = 16       ; subtunes (0-15)
MAX_PATT        = 127      ; patterns (1-127); pattern 0 is unused
MAX_CMD         = 127      ; commands/instruments (1-127)
MAX_CMDNAMELEN  = 9        ; display-only name length (bytes, padded)
MAX_PATTLEN     = 192      ; bytes per pattern (editor internal, NOT packed)
MAX_SONGLEN     = 256      ; bytes per song/orderlist per channel
MAX_TBLLEN      = 255      ; table entries (1-indexed; 0 = no table)
MIN_OCTAVE      = 1
MAX_OCTAVE      = 7
MAXDUR          = 65       ; maximum note duration (frames)
MINDUR          = 3        ; minimum note duration (frames)

; Note encoding (raw byte before right-shift)
ENDPATT         = $00      ; end-of-pattern sentinel
CMD             = $01      ; command-only row (no note)
KEYON           = $04      ; +++ (gate on without new command)
KEYOFF          = $08      ; --- (gate off)
FIRSTNOTE       = $18      ; C-1 (lowest note, raw byte value)
LASTNOTE        = $BE      ; B-7 (highest note, raw byte value)
DUR             = $C0      ; duration prefix flag
ESCBYTE         = $BF      ; RLE escape byte in .sng files

DEFAULT_HRPARAM  = $00     ; hardrestart SR (sustain=0, release=0)
DEFAULT_FIRSTWAVE = $09    ; init waveform (gate off, test bit on; V2.02+)
```

## 3. On-disk .sng File Format

The editor saves songs as RLE-compressed binary. The file starts with magic bytes `'N', '2'`
followed by compressed sections. The decompressor uses escape byte `$BF`:

```
$BF <val> <count>  →  <val> repeated <count+1> times
$BF $BF $01        →  literal $BF
```

### 3.1 Section order in .sng

```
[N][2]                                     ; magic
[ntwavetbl]       MAX_TBLLEN bytes (255)   ; wave table left col (waveform/cmd)
[ntnotetbl]       MAX_TBLLEN bytes (255)   ; wave table right col (arpeggio/note)
[ntpulsetimetbl]  MAX_TBLLEN bytes (255)   ; pulse table left col (duration/cmd)
[ntpulsespdtbl]   MAX_TBLLEN bytes (255)   ; pulse table right col (speed)
[ntfilttimetbl]   MAX_TBLLEN bytes (255)   ; filter table left col (duration/cmd)
[ntfiltspdtbl]    MAX_TBLLEN bytes (255)   ; filter table right col (speed)
[ntpatterns]      127 × 192 bytes          ; all patterns (packed rows, zero-padded to MAX_NTPATTLEN)
[nttracks]        16 × 256 bytes           ; all song orderlists (3 channels interleaved per song)
[ntcmdad]         127 bytes                ; command attack/decay
[ntcmdsr]         127 bytes                ; command sustain/release
[ntcmdwavepos]    127 bytes                ; command wave table pointer
[ntcmdpulsepos]   127 bytes                ; command pulse table pointer
[ntcmdfiltpos]    127 bytes                ; command filter table pointer
[ntcmdnames]      127 × 10 bytes           ; command names (padded with spaces, null-terminated)
[ntsonglen]       16 × 3 bytes             ; per-song track lengths [ch0, ch1, ch2]
[nttbllen]        3 bytes                  ; used table lengths [wave, pulse, filt]
[ntcmdlen]        1 byte                   ; number of commands used
[nthrparam]       1 byte                   ; hardrestart SR value
[ntfirstwave]     1 byte                   ; init frame waveform byte
```

Source: `gt2nt2.c` function `saventsong` + `src/nt2packer.s` `prsavecommon` block.

## 4. Gamemusic (Headerless) Binary Format

In "Gamemusic mode" the playroutine is NOT saved with the music. Instead the
music data starts with a 6-byte header (`NT_HEADERLENGTH = 6`) containing section
sizes, followed by the packed data sections.

### 4.1 Gamemusic header (6 bytes)

```
byte 0: gamewavetblsize    ; number of used wave table entries
byte 1: gamepulsetblsize   ; number of used pulse table entries
byte 2: gamefilttblsize    ; number of used filter table entries
byte 3: gamecmdsize        ; number of commands (normal, with ADSR)
byte 4: gamelegatocmdsize  ; number of commands (legato extension)
byte 5: gamepatttblsize    ; number of patterns used
```

Source: `src/nt2var.s` `gamedatastart` block + `src/nt2packer.s` `prsavegame`.

### 4.2 Data sections after the header (in order)

```
wavetbl_left        [gamewavetblsize bytes]
wavetbl_right       [gamewavetblsize bytes]
pulsetbl_left       [gamepulsetblsize bytes]
pulsetbl_right      [gamepulsetblsize bytes]
filttbl_left        [gamefilttblsize bytes]
filttbl_right       [gamefilttblsize bytes]
cmdad               [gamecmdsize bytes]           ; attack/decay
cmdsr               [gamecmdsize bytes]           ; sustain/release
cmdwavepos          [gamelegatocmdsize bytes]     ; wave table ptr
cmdpulsepos         [gamelegatocmdsize bytes]     ; pulse table ptr
cmdfiltpos          [gamelegatocmdsize bytes]     ; filter table ptr
patttbllo           [gamepatttblsize bytes]       ; pattern address lo bytes
patttblhi           [gamepatttblsize bytes]       ; pattern address hi bytes
songtbl             [lastsong+1 entries × 3 bytes each]  ; {addrlo, addrhi, songpos0}
patterns            [variable — packed pattern data, back-to-back]
tracks              [variable — orderlist data, all 3 channels for each used song]
```

The `NT_NEWMUSIC` routine (A=lo, X=hi of music blob address) walks the fixup table
(21 entries, `NT_NUMFIXUPS = 21`) to rewrite player internal pointers to point into
this layout. The `NT_ADD*` constants give byte offsets relative to section boundaries
within the fixup computation.

### 4.3 Relocation API (V2)

```asm
; Load music:
lda #<musicdata_address
ldx #>musicdata_address
jsr NT_NEWMUSIC

; Select song:
lda #song_number   ; 0-15
jsr NT_PLAYSONG

; Play one frame (call from interrupt):
jsr NT_MUSIC

; Play SFX:
lda #<sfx_address
ldx #>sfx_address
ldy #channel       ; 0, 7, or 14
jsr NT_PLAYSFX
```

V1 API: `RELOCATEMUSIC` / `PLAYTUNE` / `PLAYSFX` / `MUSIC` (same concept, different labels).

## 5. Track / Orderlist Format

Each of 3 channels has an independent orderlist (max 256 bytes). The combined
length of all 3 tracks for one subtune cannot exceed 256 bytes.

```
Byte value  Meaning
----------  -------
00          Loop marker (followed by 1-byte loop destination position)
01-7F       Pattern number (1-indexed, shared across all songs)
80-BF       Transpose downwards (value - $C0 gives signed downward offset)
C0-FF       Transpose upwards (C0 = transpose 0; C1 = +1 semitone, etc.)
```

Notes:
- Transpose cannot be immediately followed by loop.
- A silent-pattern infinite loop is the standard "play once" idiom.
- V2.04 fix: transpose resets to 0 when playback starts from the beginning.

## 6. Pattern Data Format

Patterns are stored as a variable-length sequence of rows, terminated by `$00`.
Each row occupies 2-3 bytes in packed form (editor internal). The packer
compresses equal-duration rows.

### 6.1 Packed row encoding

The first byte encodes the note/event type AND whether a new command follows:

```
raw_byte = (note_index << 1) | has_new_command
```

Special values (raw byte, before right-shift):
```
$00        End of pattern
$01        Command-only (no note), has_new_command=1
$04        Keyon (+++) without new command
$05        Keyon (+++) with new command
$08        Keyoff (---) without new command
$09        Keyoff (---) with new command
$18-$BE    Note C-1 to B-7 (even = no new cmd; odd = new cmd follows)
```

Note index arithmetic: `note_index = raw_byte >> 1`. The frequency table is
accessed as `nt_freqtbl-24, y` where y = `note_index * 2`.

### 6.2 Command byte (present iff has_new_command)

If `raw_byte & 1`:
```
$01-$7F   Normal command (triggers hard-restart, ADSR load, gate)
$81-$FF   Legato command (same table, but skips hard-restart + ADSR)
```
Legato command index = command byte & $7F.

### 6.3 Duration byte (optional)

A duration byte ≥ `$C0` immediately follows the command byte (or the note byte
if no command). It replaces the "last used duration" for subsequent rows.
Duration value = `(raw_duration_byte & $3F) + 1` (range: 3-65 frames).
If no duration byte is present, the previous duration stays active.

### 6.4 End of pattern

`$00` terminates the pattern. The player then reads the next orderlist entry.

## 7. Table Formats

All tables are 2-column (left side = command/type, right side = parameter).
Index 0 in any table means "not running" (pointer stays at 0 = off).

### 7.1 Wavetable (left = ntwavetbl / nt_wavetbl, right = ntnotetbl)

```
left 00-8F  Set waveform ($D404 value); right = arpeggio:
              00-7F  relative semitone offset (added to note index)
              8C-DF  absolute note (freq table index)
left 90-BF  No waveform change; delay arpeggio (right ignored); delay = (left & $1F) frames
              (used for vibrato onset delay)
left C0-DF  Vibrato; speed = (left & $1F); right = depth (unsigned)
left E0-FE  Slide (toneportamento); speed hi = (left - $E0); right = speed lo
              Speed = 16-bit: {(left-$E0), right_side}
              Slide stops when freq reaches target note and jumps back to last
              'set waveform' step
left FF     Jump; right = destination (1-indexed); 00 = stop table execution
```

Vibrato continues indefinitely. A delay-arpeggio step (90-BF) can precede vibrato
to create an attack delay.

### 7.2 Pulse table (left = ntpulsetimetbl, right = ntpulsespdtbl)

```
left 01-7F  Modulate pulse for N frames (N = left value); right = signed speed (two's complement)
left 80-FE  Set pulse to right-side value directly
left FF     Jump; right = destination (1-indexed); 00 = stop
```

Pulse written to both `$D402,x` and `$D403,x` (lo = hi byte, byte-width).

### 7.3 Filter table (left = ntfilttimetbl, right = ntfiltspdtbl)

```
left 01-7F  Modulate cutoff for N frames; right = signed modulation speed
left 80-FE  Set filter:
              resonance    = left nybble of left byte (bits 7-4)
              passband     = next nybble (bits 3 of left byte)
              channels     = low nybble of left byte (written to $D417)
              cutoff       = right byte (written to $D416)
left FF     Jump; right = destination (1-indexed); 00 = stop
```

Specifically: `$D417 = left & $7F` (or `left` with bit 7 clear → passband + channels).
When `left >= $80`: `sta $D417` then extract top nybble → master volume bits in $D418.

## 8. Command (Instrument) Format

5 fields per command (stored in 5 parallel arrays):
```
ntcmdad[cmd]       attack/decay  (written to $D405,x)
ntcmdsr[cmd]       sustain/release (written to $D406,x)
ntcmdwavepos[cmd]  wave table start index (0 = leave current table running)
ntcmdpulsepos[cmd] pulse table start index (0 = leave current table running)
ntcmdfiltpos[cmd]  filter table start index (0 = leave current filter running)
```

Command range: 1-127. Command 0 is unused.

Normal mode (cmd $01-$7F): loads ADSR, triggers 2-frame hard-restart, sets gate=open,
  then loads table pointers.
Legato mode (cmd $81-$FF): skips hard-restart, ADSR load, gate open. Only table pointers
  are updated. Useful for slides and smooth transitions.

Legato optimization: the packer can omit ADSR data for commands only ever used in
legato mode (if placed at the end of the command list). The `gamelegatocmdsize` header
field covers commands that extend beyond `gamecmdsize`.

## 9. Sound Effect Format

SFX can be played on any channel (X=0, 7, or 14) with built-in priority (higher
address preempts lower):

```
Byte 0    Sustain/Release (written to $D406,x)
Byte 1    Attack/Decay (written to $D405,x)
Byte 2    Pulsewidth (nybbles reversed: pulse $0400 → stored as $04)
Bytes 3+  Note,Wave pairs:
          - note byte: $8C-$DF (maps to freq table C-1 through B-7)
          - optional wave byte: $01-$81 (if waveform changes)
Byte n    $00 = end of SFX
```

Priority: SFX at higher memory address preempts lower. Once SFX ends, the music
channel resumes.

Source: `nt2play.s` `NT_PLAYSFX` + `nt_sfxexec` routine; V1 `readgam.txt`.

## 10. Frequency Table (V2.04)

96 entries, 2 bytes each (little-endian 16-bit), covering C-1 to B-7:

```
$022D, $024E, $0271, $0296, $02BE, $02E8, $0314, $0343, $0374, $03A9, $03E1, $041C,
$045A, $049C, $04E2, $052D, $057C, $05CF, $0628, $0685, $06E8, $0752, $07C1, $0837,
$08B4, $0939, $09C5, $0A5A, $0AF7, $0B9E, $0C4F, $0D0A, $0DD1, $0EA3, $0F82, $106E,
$1168, $1271, $138A, $14B3, $15EE, $173C, $189E, $1A15, $1BA2, $1D46, $1F04, $20DC,
$22D0, $24E2, $2714, $2967, $2BDD, $2E79, $313C, $3429, $3744, $3A8D, $3E08, $41B8,
$45A1, $49C5, $4E28, $52CD, $57BA, $5CF1, $6278, $6853, $6E87, $751A, $7C10, $8371,
$8B42, $9389, $9C4F, $A59B, $AF74, $B9E2, $C4F0, $D0A6, $DD0E, $EA33, $F820, $FFFF
```

Same table in V1 and V2. Accessed as `nt_freqtbl-24,y` (y = note×2, so note 12 → offset 0).

## 11. Playback Architecture (nt2play.s V2.04)

### 11.1 Zeropage

V2: 2 bytes at `nt_zpbase` (default `$FC`): `nt_temp1` + `nt_temp2`.
V1: 5 bytes (`$FB-$FF`).

### 11.2 Per-channel state (X-indexed, stride 7: X ∈ {0, 7, 14})

```
nt_chnpattpos,x    pattern byte position (within current pattern)
nt_chncounter,x    duration countdown (counts up; 0 → fetch new row, 2 → reload)
nt_chnnewnote,x    latched note index ($FF = no pending note)
nt_chnwavepos,x    current wavetable position (0 = not running)
nt_chnpulsepos,x   current pulse table position (0 = not running)
nt_chnwave,x       current waveform byte (ANDed with gate mask → $D404)
nt_chnpulse,x      current pulse hi-byte ($D402/$D403)
nt_chngate,x       gate mask ($FF = gate open, $FE = gate closed)
nt_chntrans,x      current transpose offset (semitones)
nt_chncmd,x        current command index
nt_chnsongpos,x    current orderlist byte position
nt_chnpattnum,x    current pattern number
nt_chnduration,x   current note duration (reload value)
nt_chnnote,x       current note (×2 = freq table index)
nt_chnfreqlo,x     current SID freq lo
nt_chnfreqhi,x     current SID freq hi
nt_chnwavetime,x   wave delay counter / vibrato direction
nt_chnpulsetime,x  pulse modulation timer
nt_chnsfx,x        SFX frame counter (0 = music active)
nt_chnsfxlo,x      SFX pointer lo
nt_chnsfxhi,x      SFX pointer hi
nt_chnwaveold,x    saved wavetable position (for slide return)
```

### 11.3 Per-frame execution order

1. Init check: if pending subtune change → reset all channel state + load song table
2. Filter execution: modulate $D416 / write $D417, $D418
3. Channel 0 execution (X=0)
4. Channel 1 execution (X=7)
5. Channel 2 execution (X=14)

Per-channel within `nt_chnexec`:
- Increment counter; at 0 → read new pattern row (2 bytes ahead of note start)
- At counter=2 → reload duration; check for new note / command execution / track advance
- Pulse table execution
- Wave table execution (arpeggio / vibrato / slide)
- Write `nt_chnwave & nt_chngate` → `$D404,x`

### 11.4 Hard restart (V2.03+)

On new note: 2 hard-restart frames (gate=$FE, SR=`NT_HRPARAM`=$00,
wave=`NT_FIRSTWAVE`=$09 "test bit") + 1 silent frame, then note starts.
V2.02 was 2 frames; V2.01 was 1 frame.
Global setting `hrparam` / `firstwave` can be adjusted per-song.

### 11.5 Timing / optimization notes

- Pattern data is read **3 frames before note start**. On that pre-read frame:
  slide, vibrato, and pulse execution are all skipped.
- Track orderlist data is read **1 frame before note start** (if needed).
  Pulse is skipped on that frame too.
- When executing a command without a note: pulse and wavetable both skip 1 frame.
- Use long note durations to reduce optimization artifacts.

### 11.6 Fixup mechanism (gamemusic relocation)

`NT_NEWMUSIC` uses a table of 21 fixup entries (`nt_fixuplo`, `nt_fixuphi`, `nt_fixupadd`).
Each entry gives a player-code address to patch + an `NT_ADD*` constant specifying
which section's start address to write there. The 6-byte header sizes are summed
cumulatively to compute each section's base address from the music blob start.

## 12. V1 vs V2 Differences

| Feature | V1.x | V2.04 |
|---------|------|-------|
| Zeropage | 5 bytes ($FB-$FF) | 2 bytes ($FC-$FD) |
| Commands vs instruments | Separate | Unified "commands" |
| Table columns | Different structure | Two-column (left/right) |
| Slide | Continuous portamento | Stops at target, returns to last wave step |
| Hard restart | 1 frame | 2 frames + 1 silent (V2.03+) |
| Duration range | Not specified | 3-65 frames |
| Songs | 16 | 16 |
| Min octave | Octave 0 exists | Octave 1 (octave 0 removed in gamemusic V1 even) |
| Relocation API | `RELOCATEMUSIC` + `PLAYTUNE` + `MUSIC` | `NT_NEWMUSIC` + `NT_PLAYSONG` + `NT_MUSIC` |
| Fixups | Full code reloc table | 21 fixups, 2 ZP bytes |
| SFX byte order | PW, AD, SR, notes... | SR, AD, PW, notes... |

V1 player (`ntplay.s`) uses `musiczpbase`=$FB and has a different header structure
(5 bytes: table length fields). The V1 music area uses `REL_*` offset constants.
V1 SFX: byte order is `{PW, AD, SR, notes}` vs V2's `{SR, AD, PW, notes}`.

## 13. Comparison with GoatTracker 2

NinjaTracker shares lineage/author with GoatTracker2 but is intentionally smaller:

| Feature | GoatTracker 2 | NinjaTracker 2 |
|---------|---------------|----------------|
| Tables | 3-column (time, val, wave) | 2-column |
| Instruments | Full multi-table instruments | Commands = ADSR + 3 table ptrs |
| Arpeggio | Explicit arp table | Part of wave table right col |
| Filter control | Separate filter instrument | Single shared filter table |
| Vibrato | Separate cmd ($04) | Wave table left $C0-$DF |
| Slide | Separate cmd ($07) | Wave table left $E0-$FE |
| Songs | 32 | 16 |
| Pattern rows | unlimited | Max 192 bytes per pattern |
| Memory (player) | ~2 KB | <1 KB (gamemusic mode) |
| Zeropage | more | 2 bytes |

GT2NT2 converter (`gt2nt2.c`) maps GT2 to NT2:
- GT2 waveform commands → NT wave table entries
- GT2 vibrato (cmd $04) → NT delay-arpeggio entries + vibrato wave step
- GT2 slide → NT slide entry ($E0-$FE)
- GT2 unsupported features: octave 0, filter resonance ctrl alone, wavetable cmds, cmds 7/C/D/E

## 14. Leads to Follow

1. **goatninj.c** (GT V1.xx → NT V1.x converter, `tmp/ninjatracker_research/goatninj.zip`):
   the earlier converter; reveals V1 data format differences not obvious from V1 player source.
2. **SIDFactory II** (github.com/SIDFactoryII): check for NT import/export support.
3. **DeepSID**: web-based player with engine annotations; may have NT-specific metadata.
4. **Ninjaforce convert tool**: http://www.ninjaforce.com/html/ninjatracker_convert.php
   (separate tool, not yet inspected).
5. **V2 changelog V2.01–V2.04**: all documented in `docs/src/readme_v204.txt` —
   key changes are duration range (3-65), hard-restart timing (2+1 frame), and
   transpose-reset-on-play fix (V2.04).
6. **Pattern compression ratio**: the editor's `getpattsize` function in `nt2packer.s`
   shows exact row encoding — rows without new duration save 1 byte, rows reusing
   last command save 1 byte. Worth measuring for HVSC corpus.
