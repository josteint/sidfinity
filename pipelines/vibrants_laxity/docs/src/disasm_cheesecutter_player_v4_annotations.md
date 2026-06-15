---
source_url: https://github.com/theyamo/CheeseCutter/blob/master/src/c64/player_v4.acme
fetched_via: curl raw.githubusercontent.com 2026-06-15
fetch_date: 2026-06-15
author: abaddon (CheeseCutter project)
content_date: 2009-2014 (repo active)
reliability: primary (annotated 6502 ACME assembler source)
---

# CheeseCutter player_v4.acme — Annotated Analysis

## Overview

Header: "CCUTTER 2.x musicplayer by abad — Based on JCH NP 21.G4 by Laxity/VIB"

This is a 1763-line ACME assembly source file for the C64 SID music player
used in CheeseCutter 2.x. It is a direct descendant of Laxity/Vibrants NP21.G4
and constitutes the best-available annotated implementation of the Laxity
player family.

File saved as: cheesecutter_player_v4.acme

## Constants / Configuration

```
ZREG        = $fb          ; zero-page pointer (2 bytes)
INSNO       = 48           ; 48 instruments
CIA_VALUE   = $4cc7        ; multispeed CIA timer
BASEADDRESS = $1000        ; player base
```

## Instrument Table Layout (8 bytes per instrument, INSNO=48 instruments)

```
Offset from inst base | Name    | Description
----------------------+---------+---------------------------------------------
INS_AD  = 0*48        | ad      | Attack/Decay byte (nibble A=attack, D=decay)
INS_SR  = 1*48        | sr      | Sustain/Release byte
INS_HR  = 2*48        | hr      | Restart type ($x0) + arpeggio delay ($0x)
                      |         |   $x0 bits: $00=3-frame restart, $40=soft,
                      |         |             $80=hard restart
                      |         |   $0x: arpeggio delay value (0-F)
INS_4   = 3*48        | (hr wf) | Hard restart waveform
INS_FLTP= 4*48        | fltp    | Filter Table pointer
INS_PULSP= 5*48       | pulsp   | Pulse Table pointer ($00-$3F)
INS_7   = 6*48        | (hr sr) | Hard restart SR envelope value
INS_ARP = 7*48        | arp     | Wave Table pointer (starting row index)
```

Total: 8 * 48 = 384 bytes for instrument table

## Wave Table (arp1 + arp2 columns, 256 bytes each)

Each row: (arp1[y], arp2[y]) = (transpose/loop, waveform/delay/loop-ptr)

### Column 1 (arp1 = transpose/loop byte):
- $00-$5F: Relative transpose up (added to note value)
- $80-$DF: Absolute tuning ($80 = semitone 0, unaffected by note/transpose)
- $7E:     Loop to previous row
- $7F:     Loop to row (next byte in arp2 is loop target index)

### Column 2 (arp2 = waveform/control byte):
- $00:     Do nothing
- $01-$0F: Override instrument's Wave Delay for this row
- $10-$DF: Waveform = SID Control Register value (gate bit always added)
- $E0-$EF: SID Control Register value $00-$0F (low values)
- If arp1=$7F: arp2 = loop pointer index

## Pulse Table (pulstab, 4 bytes per entry)

```
Byte 0 (A): Duration + direction
            $00-$7F = add speed for N frames (direction = up)
            $80-$FF = subtract speed for N frames (direction = down)
            Bit 7 = direction: 0=add, 1=subtract
Byte 1 (B): Add/subtract value per frame
Byte 2 (C): Initial pulse value (nibbles REVERSED: $48 = pulse $8400)
            $FF = skip (don't set new pulse, continue current)
Byte 3 (D): Pointer to next set ($00-$3F) or $7F = stop pulse program
            $00 = auto-advance to next entry
```

Implementation notes from code:
- Nibble reversal on pulse init: AND #$F0 -> pulselo, AND #$0F -> pulsehi
- pulsehi goes to $D403, pulselo to $D402

## Filter Table (filttab, 4 bytes per entry)

```
Byte 0 (A): Duration or filter type
            $00-$7F = Duration (number of frames)
            $90-$F0 = Select filter type (bandpass bits to $D418)
Byte 1 (B): Add value OR filter resonance+channel mask (when byte 0 >= $80)
Byte 2 (C): Initial filter value ($00-$FE), or $FF = skip (keep current)
Byte 3 (D): Pointer to next set ($00-$3F) or $7F = stop filter program
            $00 = auto-advance
```

Filter adds in 10-bit resolution (filtlo carries bottom 3 bits into filter byte).
Speed direction via byte complement ("power of wrapping") — add $F0 = subtract $10.

## Sequence Format

Two bytes per step: (AA, BB)

### Byte AA (command/instrument byte):
- $00-$5E: Note value (directly)  [< $5F, no command byte follows]
- $5F:     Tie note flag (set tienote)
- $60-$BF: Note value with command byte follows
            - note_val = AA - $60  (yields 0..$5F)
            - next byte (BB) = super/command table pointer, or $00 = no cmd
- $C0-$DF: Instrument select  (AA - $C0 = instrument number 0..31)
            followed by iny, continue parsing
- $F0-$FF: Duration set  (AA & $0F = duration value 0..15)
            followed by iny, continue parsing

### Byte BB (after note value $60-$BF):
- $00:     No command
- >$00:    Index into super/command table

### Gate control (shnote low values):
- $00:     Gate off (tienote++)
- $01:     Gate off specific state A
- $02:     Gate off specific state B
- $03+:    Normal note

### End-of-sequence marker:
- $BF at current position = sequence end, triggers newseq flag

## Super/Command Table (cmd1, cmd2, cmd3 — 64 entries each)

```
cmd1[y]: Command number
cmd2[y]: Parameter byte 1 (high)
cmd3[y]: Parameter byte 2 (low)
```

### Sequence-embedded commands (via super byte, ranges):
- $00-$3F: Go to command table (iscmd branch)
- $40-$5F: Set pulse program pointer ((byte & $1F) << 2 = pulsenxt)
- $60-$7F: Set filter program pointer ((byte & $1F) << 2 = filtnxt)
- $80-$9F: Set chord program pointer
- $A0-$AF: Set attack nibble in AD
- $B0-$BF: Set decay nibble in AD
- $C0-$CF: Set sustain nibble in SR
- $D0-$DF: Set release nibble in SR
- $E0-$EF: Set volume (cmd & $0F -> D418 volume nibble)
- $F0-$FF: Set speed (cmd & $0F -> playspeed) or sync

### Command table commands (cmd1 values):
```
CMD_SLIDE_UP    = $00  — Slide up freq; cmd2=speed_hi, cmd3=speed_lo (signed 16-bit)
CMD_SLIDE_DOWN  = $01  — Slide down; same params
CMD_VIBRATO     = $02  — Vibrato; cmd2 lo-nibble=vibraflv (feel), cmd3 hi-nibble=speed, lo-nibble=depth
CMD_SET_OFFSET  = $03  — Detune (set shfreqhi=cmd2, shfreqlo=cmd3)
CMD_SET_ADSR    = $04  — Set ADSR: cmd2=new AD, cmd3=new SR
CMD_SET_LOVIB   = $05  — Lo-fi vibrato; cmd2=freq, cmd3=amplitude
CMD_SET_WAVE    = $06  — Set waveform directly (cmd3=waveform) [compiled out in this build]
CMD_PORTAMENTO  = $07  — Portamento: cmd2 lo-nibble=portahi, cmd3=portalo
CMD_STOP        = $08  — Stop portamento/slide (clear effstate)
```

### Effect state machine (effstate):
```
0    = no effect
1    = slide up
2    = slide down
3    = hi-fi vibrato
4    = lo-fi vibrato
$81  = portamento
```

## Orderlist / Track Format

Track stored as byte pairs (or single bytes):
- Normal entry: sequence_number (1 byte), repeat_count? — but from code it appears
  the track is a flat stream of bytes.

From updtrack code:
- If byte >= $80 and != $A0: it's a transpose value (byte - $A0 -> shtrans2[x])
  followed by sequence number
- If byte < $80: it's a sequence number directly
- After sequence number: next byte checked: if >= $F0, it's a wrap (loop)
  - (byte & $07) + twraphi -> trackhi (wrap the song)

Track wrap marker: byte >= $F0 (with next two bytes as new start address)

## Hard Restart Behavior

Hard restart triggered 3 frames before new note (tsync countdown):
1. tsync=3: nothing special
2. tsync=2 (dosync, first check): if not tied and synccnt>=2 and INS_HR has HR bit:
   - If bit $20 NOT set: apply hard restart AD (from cmd2 global = cmd table pos 0)
   - Always: apply INS_7 (HR SR value) to sr[x]
   - Set gate[x] = $FE (gate off + waveform mask)
3. tsync=1: go to dowave only
4. tsync=$FF (postsync): gate back on, set waveform

Gate states: gate[] = $FE (off) or $FF (on)
waveform[x] AND gate[x] -> $D404+voice*7

## SID Register Write Order (per voice, per frame)

From setsid:
1. freqlo -> $D400,y
2. freqhi -> $D401,y
3. sr     -> $D406,y  (Sustain/Release)
4. ad     -> $D405,y  (Attack/Decay)
5. pulselo -> $D402,y
6. pulsehi -> $D403,y
7. waveform AND gate -> $D404,y

Then global: filter/volume at end of all 3 voices:
- filtlo -> $D415
- filter -> $D416
- volume OR bandpass -> $D418

## Memory Map (player at BASEADDRESS=$1000)

```
$0FA0-$0FBF: Editor pointer table (init/play addresses, table pointers)
$0FC0-$0FCF: Data table pointers (arp1, arp2, filttab, pulstab, inst, tracks, seqlo, seqhi)
$0FD0-$0FFF: More editor pointers + version string "cc4.07"
$1000:       init (JSR target)
$1003:       play (JSR target)
$1006:       mplay (multispeed JSR)
$1008+:      subinit, subplay, submplay, main player code
$1500+:      freqtable_lo (96 bytes)
$1560+:      freqtable_hi (96 bytes)
```

Data tables (allocated after BASEADDRESS dynamically in editor at $2000+):
```
$2000:       songsets (6 bytes: 3× 16-bit track pointers + speed + voicon)
$2200:       track1 (1024 bytes, voice 0 orderlist)
$2600:       track2 (1024 bytes, voice 1 orderlist)
$2A00:       track3 (1024 bytes, voice 2 orderlist)
$2E00:       seqlo (128 bytes, sequence lo-address table)
$2F00:       seqhi (128 bytes, sequence hi-address table)
$3000-$BF00: 128 sequences, 256 bytes each (s0..s127)
$C000:       arp1 (256 bytes, wave table column 1: transpose)
$C100:       arp2 (256 bytes, wave table column 2: waveform)
$C200:       inst (48*8 = 384 bytes, instrument table)
$C400:       supertab: cmd1[64], cmd2[64], cmd3[64] (192 bytes)
$C500:       filttab (256 bytes)
$C600:       pulstab (256 bytes)
$C700:       chord (128 bytes) + chordindex (32 bytes)
```

## Chord Table

chord[]: pairs of (semitone_value, end_flag)
- If semitone >= $40: semitone |= $80 (negative chord interval)
- Next byte: if bit 7 set, it's the last entry; bits 6:0 = loop pointer

chordindex[32]: maps chord program slot (0..31) to start index in chord[]

## Multispeed

- CIA_VALUE = $4cc7 for 2x speed
- mplay entry (at $1006) sets state = $40, runs sound work only (no track/seq update)
- Normal play = subplay, does track+seq+sound
- submplay skips track/sequence advancement (sound work only)

## Init Call

init(A): A = subtune number (0-based)
- Shifts A left 3 times (×8), uses as index into songsets
- Sets twraplo/hi[3] from songsets (3 × 16-bit track pointers)
- Sets speed from songsets[6]
- Sets voicon[3] from songsets[7] bitmask
- Clears all state variables
- Sets state = 1 (triggers init sequence on first play call)

## Notes on Relationship to Original Laxity Engine

Per JCH's NP20.G4 documentation (20_G4_IN.TXT):
- NP20's pulse/filter table format is "the same system as used in LAXITY's player"
- Laxity's player also has the $7E arpeggio endmark (NP18 added this for compatibility)
- NP21.G4 (this player's basis) is Laxity's player lineage, not strictly JCH's own

The CheeseCutter player therefore implements the Laxity pulse/filter step-programming
paradigm directly. The key identifying features of the Laxity/JCH NP21 lineage:
1. 8-byte instrument table
2. 4-column pulse/filter tables with pointer-based chaining
3. 2-column wave table (transpose + waveform)
4. Super-table embedded in sequence via Sxx byte
5. Calculated vibrato using Rob Hubbard's algorithm
