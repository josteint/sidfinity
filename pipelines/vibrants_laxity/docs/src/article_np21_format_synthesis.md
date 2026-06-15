---
source_url: multiple (see individual files)
fetched_via: synthesis 2026-06-15
fetch_date: 2026-06-15
author: synthesized from primary sources (JCH docs, Glover source, CheeseCutter)
content_date: 2026-06-15
reliability: primary (synthesized from primary sources)
---

# Laxity/JCH NP21 Player Format — Synthesis

This document synthesizes byte-level format knowledge from:
1. `jch_np21g4_source_glover.txt` — NP21.G4 source by Glover/Samar (assembly, 1014 lines)
2. `jch_np21g5_source_glover.txt` — NP21.G5 source by Glover/Samar (1033 lines)
3. `jch_np21g6_glover_notes.txt` — NP21.G6 format notes by Glover
4. `cheesecutter_player_v4.acme` — CheeseCutter player based on NP21.G4 by Laxity (1763 lines)
5. `jch_np20g4_full_instructions.txt` — Original JCH NP20.G4 documentation
6. `jch_np15g6_full_instructions.txt` — Original JCH NP15.G6 documentation

## Lineage

```
Laxity original player (~1987-1990, "Laxity Editor")
    |
    +-- JCH NP14/15/17/18/20 (JCH's own design, then adopts Laxity pulse/filter format in NP20)
    |
    +-- JCH NP21.G4 (2005, Laxity/JCH collaboration, Glover ports)
    |       |
    |       +-- NP21.G5 (speed 3 variant)
    |       +-- NP21.G6 (Glover's extended version, ~2000 via Samar Productions)
    |
    +-- CheeseCutter player_v4 (abaddon, based on NP21.G4)
    |
    +-- SID Factory II drivers (sf2driver11_xx etc., JCH+Laxity+Michel de Bree, 2020+)
```

## Memory Layout (NP21.G4 at $1000)

From NP21.G4 source (jch_np21g4_source_glover.txt, lines 180-1013):

```
$0FA0-$0FEA: Editor pointer table ($0FA0=voicon, $0FA2=vol, etc.)
$1000:       init (JMP sinit)
$1003:       drive / play (JMP main)
$1006+:      voicon (3 bytes), shspeed, fltcyc, reson, state variables
```

Data tables (relative to tpoin, fixed offsets of 256 bytes each):
```
tpoin:    v1/v2/v3 pointers (6 bytes) + speed + voicon-byte
arp1:     = tpoin+$100   (wave table column 1: 256 bytes)
arp2:     = arp1+$100    (wave table column 2: 256 bytes)
filttab:  = arp2+$100    (filter table: 256 bytes, first 2 bytes = half-speed selectors)
pulstab:  = filttab+$100 (pulse table: 256 bytes)
instr:    = pulstab+$100 (instrument table: 8 * INSNO bytes)
lobyt:    = instr+$100   (sequence lo-byte table: 128 bytes)
hibyt:    = lobyt+$100   (sequence hi-byte table: 128 bytes)
supertab: = hibyt+$100   (super/command table: 256 bytes)
v1:       = supertab+$100 (voice 1 orderlist: 1024 bytes)
v2:       = v1+$400      (voice 2 orderlist: 1024 bytes)
v3:       = v2+$400      (voice 3 orderlist: 1024 bytes)
s00/s01/s02: sequence data (128 slots × 256 bytes each)
```

NOTE: The tpoin area is relocated by the JCH packer. The player code at $1000
is fixed; data tables can float. The packer writes the number of tpoin sets
in the byte after the $FC,$3C marker (before tpoin).

## Instrument Table (8 bytes per instrument)

From NP21.G4 source comments + NP21.G6 notes:

```
Byte 0 (AD):   Attack/Decay  (hi nibble=attack, lo nibble=decay)
Byte 1 (SR):   Sustain/Release  (hi nibble=sustain, lo nibble=release)
Byte 2 (ctrl): Wavetable speed settings
               hi nibble = first-position speed (arp delay at note trigger)
               lo nibble = full wavetable delay speed
               [In NP21.G4 source comment: "wavetab speed first pos/second pos."]
Byte 3 (fx):   Flags/drum mode
               $01 = drum effect (hifreq mode)
               $02 = filter no restart
               $04 = pulse no restart
               $80+ = hard restart bits (see NP20 docs for bit interpretation)
Byte 4 (filt): Resonance + filter type
               [NP21.G6: "resonans/filter type"]
Byte 5 (fp):   Filter table pointer (entry number, 0-based ×4 = byte offset)
               $FF = smooth filter change (don't reset)
Byte 6 (pp):   Pulse table pointer (entry number, 0-based ×4 = byte offset)
               $FF = smooth pulse change (don't reset)
Byte 7 (wp):   Wave table pointer (entry index into arp1/arp2)
```

### NP21.G6 variant (Glover extension):
```
Byte 0-1: ADSR (same)
Byte 2:   wavetab speed first pos / second pos
Byte 3:   fx flags (01=drum, 02=filter no restart, 04=pulse no restart)
Byte 4:   resonance/filter type  [F nibble = type, R nibble = resonance]
Byte 5:   filtertab number
Byte 6:   pulsetab number
Byte 7:   wavetab number
```

### CheeseCutter variant (NP21.G4 base, 8 bytes per instrument, 48 instruments):
```
INS_AD   [0]:  Attack/Decay
INS_SR   [1]:  Sustain/Release
INS_HR   [2]:  Restart type ($x0 nibble) + arpeggio delay ($0x nibble)
               $00 = 3-frame restart, $40 = soft, $80 = hard restart
INS_4    [3]:  Hard restart waveform byte
INS_FLTP [4]:  Filter Table pointer (0-63, ×4 = byte offset, or 0=no filter)
INS_PULSP[5]:  Pulse Table pointer (0-63, ×4 = byte offset, or 0=no pulse)
               If bit 7 set: direct pulse (AND #$0F -> pulsehi, lo=0)
INS_7    [6]:  Hard restart SR envelope value
INS_ARP  [7]:  Wave Table pointer (index into arp1/arp2 columns)
```

## Wave Table (arp1 + arp2, 2 × 256 bytes)

Each row Y:  (arp1[Y], arp2[Y])

### arp1[Y] — Transpose / Loop column:
- $00-$5F: Add this value to the playing note (relative transpose up)
- $80-$DF: Absolute frequency index ($80+n uses freqtable[n] directly)
            (bit 7 set = absolute; value & $7F = semitone index)
- $7E:     Loop — repeat this row forever (NP20+ feature, from Laxity orig)
- $7F:     Loop — next position is loop target index in arp2

### arp2[Y] — Waveform / Delay / Loop-ptr column:
- $00:     Do nothing (keep last waveform)
- $01-$0F: Override wave delay for this step only
- $10-$DF: Set waveform = SID control register value (gate bit added by player)
- $E0-$EF: Set SID control register to value $00-$0F (for test/reset bit)
- (if arp1=$7F): arp2 = loop target index

## Pulse Table (pulstab, 4 bytes per entry, pointer ×4 = byte offset)

From CheeseCutter source + NP20.G4 docs + NP21.G6 notes:

```
Byte 0 (A): Duration + direction
            Bits 6:0 = frame count (0-127)
            Bit 7    = direction: 0=add (sweep up), 1=subtract (sweep down)
Byte 1 (B): Add/subtract value per frame ($00-$FF)
Byte 2 (C): Initial pulse value [NIBBLES REVERSED from display]
            $FF = skip (keep current pulse)
            $48 display = pulse $8400 on hardware
            In code: AND #$F0 -> pulselo (-> $D402), AND #$0F -> pulsehi (-> $D403)
Byte 3 (D): Next entry pointer (×4 = byte offset)
            $00 = advance to next entry automatically (+4)
            $7F = stop (pulse stays at current value)
            Other = jump to entry D×4
```

Note: NP21.G6 has slightly different encoding:
```
Byte A: HI pulse byte / add value  [reversed from NP20]
Byte B: LO pulse byte / add value
Byte C: add value
Byte D: next line number ($7F=end)
```

## Filter Table (filttab, 4 bytes per entry)

From CheeseCutter source + NP20.G4 docs + NP21.G6 notes:

```
Byte 0 (A): Duration OR filter type
            $00-$7F: Duration in frames
            $80+:    Select bandpass/filter type bits for $D418
                     $90-$F0 range: AND #$70 -> bandpass bits
Byte 1 (B): Add value (signed via complement), OR resonance+channel mask
            When byte 0 >= $80: this byte -> $D417 directly
            Direction via wrap: $F0 = subtract $10 (Laxity's "power of wrapping")
            In CheeseCutter: 2-bit portion goes to filtadd+1, rest to filtadd
            Filter frequency updated in 10-bit resolution (filtlo carries 3 bits)
Byte 2 (C): Initial filter cutoff ($00-$FE), or $FF = skip (keep current)
Byte 3 (D): Next entry pointer (×4 = byte offset)
            $00 = advance automatically
            $7F = stop
            Other = jump to entry D×4
```

Special bytes 0-3 of filttab (NP20+):
- filttab[0], filttab[1]: Half-speed selectors (speed values 2-9 for alternating)
- filttab[2]: Unused in v20.G3+ (was raster decrease in earlier versions)
- filttab[3]: Filter-to-voice routing (bitmask for which voices get filtered)

## Super/Command Table (supertab)

Two-byte entries: (cmd_byte, parameter_byte)

### From sequence: "Sxx" command = index into supertab

When embedded byte in sequence (after note byte) is non-zero:
Range determines action in CheeseCutter (extended from NP21):
- $00-$3F: Command table entry (cmd table at supertab)
- $40-$5F: Set pulse program pointer for this voice
- $60-$7F: Set filter program pointer (global? depends on version)
- $80-$9F: Set chord program pointer
- $A0-$AF: Set attack nibble in AD
- $B0-$BF: Set decay nibble in AD
- $C0-$CF: Set sustain nibble in SR
- $D0-$DF: Set release nibble in SR
- $E0-$EF: Set volume ($D418 bits 0-3)
- $F0-$FF: Set speed or sync

### NP21.G4 Super table (from Glover source header comments):
```
0h,lo:      Slide up (BCD speed = hi nibble, lo byte)
1h,lo:      Slide down
2x,yy:      Vibrato 1 (x=speed, yy=add value)
3?,sr:      Set Sustain/Release
4?,xy:      Half-speed (x,y point to speed bytes in filter table)
5?,xx:      Set filter frequency add
60-7f,xx:   New filter table pointer for sound (60=instr0, 7F=instr31)
80-9f,xx:   New pulse table pointer for sound
a0-bf,xx:   New waveform table pointer for sound
c0-df,xx:   New wave speed pointer for sound
e?,?x:      Volume (x = 0-F)
fx,yz:      Vibrato 2 (x=feel, y=speed, z=add value)
```

### NP21.G6 Super table (from Glover notes):
```
A:0  Glide UP (BCD speed)
A:1  Glide DOWN (BCD speed)
A:2  Vibrato: B=speed, CD=add value
A:3x Set Sustain/Release (C:sustain, D:release)
A:4x Set tempo (C: 1st value, D: 2nd value) [half-speed]
A:5x Set filter frequency CD: 00-FF
A:6x 60-7F set new Filtertable for instrument 00-1F (60=instr0, 7F=instr31)
A:8x 80-9F set new Pulsetable for instrument 00-1F
A:Ax A0-BF set new Wavetable for instrument 00-1F
A:Cx C0-DF set new wave speed for instrument 00-1F
A:Ex Dx set music volume 0-F
A:Fx Precise vibrato: B=depth, C=speed, D=add value
```

## Sequence Format

Two bytes per step: (NOTE_BYTE, CMD_BYTE)

The sequence is variable-length, terminated by end-of-sequence marker.

### NOTE_BYTE encoding (from CheeseCutter player_v4.acme):
```
$00-$5E:  Direct note value (no command byte follows)
$5F:      Tie note (flag tienote, no new note triggered)
$60-$BF:  Note value + command byte follows
           Actual note = byte - $60 (gives range 0..$5F)
           Next byte = super-table index (0=no command)
$C0-$DF:  Instrument select (byte - $C0 = instrument 0..31, up to 47 in CC)
           Continue parsing
$F0-$FF:  Duration set (byte & $0F = duration value 0..15)
           Continue parsing
$BF:      End-of-sequence marker (triggers newseq to advance orderlist)
```

### Gate control (low note values):
```
$00:   Gate off (tienote++)
$01:   Gate-off state A
$02:   Gate-off state B
$03+:  Normal playing note
```

### Note-to-frequency:
Player has a 96-entry (8-octave) frequency table. Note byte is direct index.
In NP21.G4 (from source): notes table at line 901 — 96 word entries covering
$0116-$FD2E range for SID registers.

## Orderlist / Track Format

Per voice (v1/v2/v3), format is a flat byte stream:

```
If byte < $80:   Sequence number (direct index into lobyt/hibyt)
If byte = $8C:   Special marker (in default init: $8C,$00,$FF)
If byte >= $80 and != $8C: Track wrap/loop marker
                $FF in some versions = end of track (wrap to tpoin pointer)
```

From NP21.G4 source (lines 998-1003):
```
v1: .byte $8C,$00,$FF    ; song start: select seq 0, no transpose, wrap
v2: .byte $8C,$00,$FF
v3: .byte $8C,$00,$FF
```

In CheeseCutter (more detailed from updtrack code):
```
byte >= $80 but not $A0-type: transpose value (byte - $A0 -> shtrans2)
                              then next byte = sequence number
byte < $80:  Sequence number
After seq num, next byte:
  >= $F0: wrap/loop marker; (byte & $07) + twraphi -> new trackhi
           advances track pointer to song start
```

## Hard Restart Behavior

Hard restart timing from CheeseCutter/NP21:
- tsync countdown: starts at 2 (two frames before gate-on)
- At tsync=2: if synccnt >= 2 and HR flag in INS_HR:
  - Apply hard restart AD (from cmd table position 0: 0F 00 by default)
  - Apply INS_7 (HR SR value) as SR — typically $00 for maximum release
  - Set gate = $FE (gate off + preserve waveform bits)
- At tsync=1: dowave only (runs wavetable without gate change)
- At tsync=$FF (gate-on frame): apply ADSR from instrument, set gate $FF

Default hard restart ADSR: $0F, $00 (attack+decay 0F, sustain+release 00)
Can be customized via supertab position 0 (first two bytes).

## SID Register Write Order Per Voice

From CheeseCutter setsid routine:
1. freqlo    -> $D400 + voice_offset
2. freqhi    -> $D401 + voice_offset
3. sr        -> $D406 + voice_offset  (Sustain/Release)
4. ad        -> $D405 + voice_offset  (Attack/Decay)
5. pulselo   -> $D402 + voice_offset
6. pulsehi   -> $D403 + voice_offset
7. waveform AND gate -> $D404 + voice_offset

Then global (after all 3 voices):
8. filtlo    -> $D415
9. filter    -> $D416
10. volume | bandpass -> $D418

Voice offsets: voice[0]=0, voice[1]=7, voice[2]=14

## Init/Play Addresses

NP21.G4: init=$1000, play=$1003
Standard for all JCH/NP players since NP14.

Subtune selection: init(A) where A=subtune number (0-based)
- Shifts A left 3 (×8) as index into tpoin (3 × 16-bit track pointers + speed + voicon)
- Sets track pointers for all 3 voices
- Clears state buffers
- Sets state=1 for deferred initialization on first play()

## Key Differences Between NP21.G4 and NP21.G5

NP21.G5 is the "speed 3 up" variant (from filename "21.g5spd3up.src.prg").
The source is nearly identical to G4, with modifications for 3× multispeed
CIA timer. The sequence/instrument format is unchanged.

## Relationship to HVSC Vibrants Tunes

The 179 Laxity tunes in HVSC (most filed under Laxity/ or Vibrants/) use:
- The "Laxity" player variant (binary format, never published as source)
- OR JCH NewPlayer (NP14-NP21 variants, documented above)
- SIDID engine string: "Vibrants" or "JCH" identifies which

The original Laxity editor (v/32-3.34 through v/35, CSDb #122333) used
Laxity's own player format. JCH noted (NP20 docs) that NP20's pulse/filter
tables are "the same system as used in LAXITY's player" — so the 4-byte
step-program format above was Laxity's invention, later adopted by JCH.

## What We Do NOT Have

1. Original Laxity player source (binary-only on CSDb, format not published)
2. Laxity Editor format documentation (never publicly documented per research.md)
3. NP14/NP17/NP18 sources (only NP21.G4/G5/G6 available; NP15 docs available)
4. Complete orderlist format spec (track format is partially inferred from source)

## Comparison to SID Factory II Driver 11 (modern descendant)

SF2 driver 11 is a redesign, but follows the same concepts:
- 6-byte instrument table (dropped HR waveform byte, added filter-enable flag)
- Same wave/pulse/filter table format (4-byte entries, pointer-chained)
- T-commands instead of Sxx (T0=slide, T1=vibrato, T2=portamento, T3=arp, T8=set ADSR)
- Same orderlist with transpose byte + sequence number pairs
- init=$1000, play=$1003 preserved
- Hard restart: instrument flag + 2-frame countdown (same mechanism)
