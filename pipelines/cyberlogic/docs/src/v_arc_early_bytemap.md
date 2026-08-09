# v_arc_early binary map — A_Real_Compose.sid (load=$1000)
# SID: hvsc85/MUSICIANS/N/Nagie_Sascha/A_Real_Compose.sid
# Load=$1000, Init=$10A1, Play=$112B, End=$219D, Size=4509 bytes

## Jump table ($1000)

```
$1000  4C A1 10  JMP $10A1   ; init
$1003  4C 2B 11  JMP $112B   ; play
$1006  4C E1 10  JMP $10E1   ; voice_reset (call at note trigger)
$1009  4C DD 10  JMP $10DD   ; sub (called from voice_reset)
$100C  4C CE 10  JMP $10CE   ; sub (gate-off helper)
$100F  4C D3 12  JMP $12D3   ; sub (pattern advance)
```

## ASCII ID string ($1012)

```
$1012: 'MUSIC SASCHA NAGIE,PLAYER O.KL'
Hex: 4D 55 53 49 43 20 53 41 53 43 48 41 20 4E 41 47 49 45 2C 50 4C 41 59 45 52 20 4F 2E 4B 4C
```

## Config / runtime state block ($1032-$10A0)

```
$1032  frame counter (main, counts down each play() call)
$1033  speed sub-counter (reloads to value from $1C3E,section; typical: 2 or 3)
$1034  filter cutoff shadow (from $1C2E,section)
$1035  per-voice done flag / section advance trigger
$1036  reserved / song length counter
$1037  song-done flag (nonzero = song complete, play() exits)
$1038  voice 1 current pattern# (index into freq/pattern table)
$1039  voice 2 current pattern#
$103A  voice 3 current pattern#
$103B  voice 1 stream position (Y offset into current pattern stream)
$103C  voice 2 stream position
$103D  voice 3 stream position
$1041  voice 1 current instrument# (loaded at section change)
$1042  voice 2 current instrument#
$1043  voice 3 current instrument#
$1044,X  per-voice instrument# (hi-nibble of note byte, post LSR*4)
$1047,X  per-voice note lo-nibble (low 4 bits of note byte)
$104A  voice 1 duration counter hi (top nibble of duration byte)
$104B  voice 2 duration counter hi
$104C  voice 3 duration counter hi
$1053,X  per-voice remaining duration ticks
... (many more voice state bytes through $109E,X)
```

## SIDId signature location

```
Signature at $14D5 (approximately):
  9D ?? ?? B0 ?? DE ?? ?? A9 0F EA 4A 4A 4A 4A DD ?? ?? D0 ?? A9 00
  (STA abs,X; BCS; DEC abs,X; LDA #$0F; NOP; LSR*4; CMP abs,X; BNE; LDA #$00)
  Context: ADSR frame counter -- reload to $0F on new note, count down via DEC abs,X
  LSR*4 extracts hi-nibble = current ADSR phase index
```

## Frequency table ($1928 / $1987)

```
$1928  freq lo table: 95 entries (notes 0..94, ~7 octaves + 11 semitones)
       Octave 0 (C..B): 0E 13 25 37 3F 47 59 6B 7B 80 90 98
$1987  freq hi table: 95 entries (same index range)
       Octave 0 (C..B): 1D 1D 1D 1D 1D 1D 1D 1D 1D 1D 1D 1D

NOTE: same memory region serves dual purpose as PATTERN POINTER table.
      Pattern address for pattern N = {$1987[N] << 8} | {$1928[N]}
      Pattern# == note# (no separate pointer table).
```

## Instrument tables

32 instruments (index 0-31). Each property is a parallel array of 32 bytes.
Tables identified from play() code access trace.

```
$17D8  waveform_gate         D404 value with gate bit. $41=pulse+gate, $40=pulse, $11=noise+gate
       [0..15]: 00 00 00 00 41 00 00 00 41 41 41 00 41 41 41 00
       [16..31]: 00 00 00 41 41 00 00 11 00 00 00 00 40 00 00 00

$17F0  waveform_release      D404 value for gate-off (release phase). Gate bit cleared.
       [0..15]: 00 00 00 00 40 00 00 00 40 40 40 00 40 40 40 00
       [16..31]: 00 00 00 40 40 00 00 10 00 04 05 02 00 04 08 00

$1800  flags_a               Effect enable flags. Bit $40=hw_restart, $10=?, $04-$08=arp/vibrato mode
       [0..15]: 00 00 00 40 40 00 00 10 00 04 05 02 00 04 08 00
       [16..31]: 08 00 00 00 00 00 00 00 00 00 00 00 00 CB BA 00

$1808  flags_b               Effect parameter byte A (arp table index or vibrato depth select)
       [0..15]: 00 04 05 02 00 04 08 00 08 00 00 00 00 00 00 00
       [16..31]: 00 00 00 00 00 CB BA 00 C8 E9 D6 63 88 A9 89 00

$1820  attack_decay          D405: hi-nibble=attack, lo-nibble=decay
       [0..15]: C8 E9 D6 63 88 A9 89 00 89 9F 69 8A 7D 8A 49 C9
       [16..31]: C9 C9 C9 7A 7A 9C AC C9 88 08 A1 00 02 00 08 00

$1838  sustain_release       D406: hi-nibble=sustain, lo-nibble=release (note-on value)
       [0..15]: 88 08 A1 00 02 00 08 00 08 08 08 08 54 08 07 04
       [16..31]: 04 04 04 41 41 02 02 00 00 00 00 00 20 00 20 00

$1850  hw_restart_ad         D405 value used during hard-restart gate-off phase
       [0..15]: 00 00 00 00 20 00 20 00 20 10 10 40 35 00 10 40
       [16..31]: 40 40 40 54 54 20 20 00 00 00 00 00 95 00 00 00

$1868  vibrato_depth         Vibrato / arp depth per instrument (0=off)
       [0..15]: 00 00 00 00 95 00 00 00 00 64 64 45 85 45 00 00
       [16..31]: 00 00 00 85 85 00 00 85 00 00 00 00 15 00 00 00

$1880  vibrato_speed         Vibrato / arp speed per instrument
       [0..15]: 00 00 00 00 15 00 00 00 00 0E 2E 20 15 20 00 00
       [16..31]: 00 00 00 10 10 00 00 05 00 00 00 00 20 00 00 00

$18B0  release_sr            D406 sustain/release for gate-off. Typical: $F0=sustain_hi, instant release
       [0..15]: F0 F0 F0 F0 10 F0 F0 F0 F0 F0 00 F0 F0 F0 F0 F0
       [16..31]: F0 F0 F0 F0 F7 F0 F0 F0 3A 4D 04 00 00 00 51 00

$18C8  filter_cutoff         Per-instrument D416 filter cutoff value; $00 = no filter write
       [0..15]: 3A 4D 04 00 00 00 51 00 00 00 00 08 00 00 00 12
       [16..31]: 1A 26 32 00 00 41 41 00 41 51 08 04 00 04 58 00

$18F8  pulse_width           Pulse width low byte (D402) or PW sweep parameter
       [0..15]: 40 50 07 03 00 03 57 00 00 00 00 08 00 00 00 12
       [16..31]: 1A 26 32 00 00 41 41 00 05 05 05 05 01 05 05 00

$1910  portamento            Portamento speed per instrument (0=off, higher=slower glide)
       [0..15]: 05 05 05 05 01 05 05 00 01 01 01 05 01 01 01 05
       [16..31]: 05 05 05 01 01 05 05 01 0E 13 25 37 3F 47 59 6B
```

## Section / orderlist tables ($1C0E-$1C7E+)

Parallel arrays indexed by section# (Y register). Song advances through N sections;
all three voices share a single section counter.

```
$1C0E[Y]  section loop-count sentinel (SMC: dynamically rewrites CPY opcode in play code)
$1C1E[Y]  voice 2 section parameter (role partially unclear; drives section-end detection)
$1C2E[Y]  per-section filter cutoff ($D416); $FF = no change this section
$1C3E[Y]  per-section tempo: speed sub-counter reload value (observed: 2 or 3 frames/tick)
$1C4E[Y]  per-section meta flag (purpose TBD)
$1C5E[Y]  per-section $D418 value (volume + filter mode bits: $81, $80, $41, $40...)

Voice-to-pattern mapping per section:
$19E6[Y]  voice 1 starting pattern# for section Y
$1A9E[Y]  voice 2 starting pattern# for section Y
$1B56[Y]  voice 3 starting pattern# for section Y
```

First 16 sections of A_Real_Compose.sid:
```
Section  V1-pat  V2-pat  V3-pat  filter  tempo  vol+mode
     0      03      01      00      0F      03     81
     1      04      02      00      0F      03     81
     2      03      05      00      0F      03     80
     3      04      06      00      0F      03     80
     4      03      01      00      0F      03     81
     5      04      02      00      0F      03     41
     6      03      01      00      0F      03     81
     7      04      02      00      FF      02     80
     8      0F      01      11      FF      02     41
     9      0F      02      11      FF      02     41
    10      10      05      12      FF      02     41
    11      10      06      12      FF      02     41
    12      0F      01      11      0F      03     41
    13      0F      02      11      0F      03     40
    14      0F      01      11      0F      03     41
    15      0F      02      11      0F      03     41
```

## Pattern streams

Pattern data begins at $1D0E (this SID). 95 patterns (0-94).
Pattern N starts at address { ($1987[N] << 8) | $1928[N] }.

Pattern stream byte encoding:
```
$00..$5F  note byte (pitch index 0-94 into freq table)
          Next byte is a duration byte:
            duration[7:4] = frame count hi-nibble
            duration[3:0] = frame count lo-nibble (sub-tick or combined)
$60..$7F  instrument select: inst# = byte & $1F  (selects inst 0-31)
$80..$FB  effect commands (exact semantics TBD per opcode; see Leads section)
$FC        command with 1-byte argument (observed in patterns: $FC $F0, $FC $98...)
$FD        command with 1-byte argument (pitch transpose or key shift)
$FA        loop-point marker (repeat from here in pattern)
$FF        end of pattern; advance to next section
```

## Voice write order ($1660 STA sequence)

```
Per-voice (Y = voice# * 7, iterating X=2,1,0 for voices 3,2,1):
  STA $D401,Y  ; freq hi  (UNUSUAL: hi written before lo)
  STA $D400,Y  ; freq lo
  STA $D402,Y  ; pulse lo
  STA $D403,Y  ; pulse hi
  STA $D405,Y  ; attack/decay
  STA $D406,Y  ; sustain/release
  STA $D404,Y  ; ctrl/waveform (gate bit written last)

Filter and volume (global, written once per frame):
  STA $D416    ; filter cutoff hi   (@ $169A)
  STA $D417    ; filter resonance + voice routing  (@ $16A1)
  STA $D418    ; master volume + filter mode  (@ $16F4)
```

## LSR*4 usage sites

```
$12C1  instrument# extract from note-stream byte (hi-nibble -> inst slot $1044,X)
$14E0  ADSR counter hi-nibble -> current ADSR phase (this is the SIDId match site)
$1518  vibrato/arp speed nibble extract
```
