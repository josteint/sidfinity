---
source_url: https://csdb.dk/getinternalfile.php/154684/OdinTracker113src.zip (file: defines.s)
fetched_via: direct
fetch_date: 2026-06-15
author: Zed (Zoltán Konyha)
content_date: 2001-04-17
reliability: primary
---

# OdinTracker 1.13 Data Format — defines.s

Extracted from `defines.s` inside `OdinTracker113src.zip`. This is the authoritative
layout of the OdinTracker song data format as assembled in DASM.

## Memory Layout (editor layout)

```asm
BASIC           = $0801
EDITOR          = $0810
FONT            = $3800
RWDATA          = $3a00         ; Editor's read/write and uninitialized data.
SPRITEHILIGHT   = $3f80         ; Track row highlight sprite.
SPRITECURSOR    = $3fc0         ; Cursor sprite.

; Locations of music data.
ORDERLIST       = $4000         ; 256 bytes for orderlist.
SONGTITLE       = $4100         ; 32 bytes for song title.
PATTERNS        = $4200         ; 256 patterns; 3 track numbers + 3 transposes each = $600 bytes total.
INSTRUMENTS     = $4800         ; 32 instruments, each 16 bytes.
INSTRUMENTNAMES = $4a00         ; 32 instrument names, each 16 bytes.
WAVETABLE       = $4c00         ; 256 bytes for wave table.
ARPEGGIOTABLE   = $4d00         ; 256 bytes for arpeggio table.
FILTERTABLE     = $4e00         ; 256 bytes for filter table.
SONGSTARTTABLE  = $4f00         ; Song start positions (subsong support).
TRACKS_BASE     = $5000         ; 128 tracks, each 64*3 bytes = 192 bytes per track.
VPLAYER         = $b000         ; Relocatable player.
OPCODELIST      = $bf00         ; Number of bytes per 6510 instruction.
PLAYER          = $c000         ; Editor's player.
INSTRUMENTBUFFER = $ce00        ; Used when converting instruments from old format.
HELPTEXT        = $d000         ; $3000 bytes for help text.
```

## Song Data Structure

### Constants
```asm
MAX_ORDERS      = 256
MAX_PATTERS     = 256
MAX_TRACKS      = 128
MAX_INSTRUMENTS = 32
SONGTITLELEN    = 32
INSTRUMENTLEN   = 16
INSTRUMENTNAMELEN = 16
```

### Instrument Structure (16 bytes each, at INSTRUMENTS = $4800)
```asm
INST_AD                 = $00  ; Attack/Decay.
INST_SR                 = $01  ; Sustain/Release.
INST_WAVETABLESTART     = $02  ; Wave table start index.
INST_WAVETABLEEND       = $03  ; Wave table end index.
INST_WAVETABLELOOP      = $04  ; Wave table loop index.
INST_ARPTABLESTART      = $05  ; Arpeggio table start index.
INST_ARPTABLEEND        = $06  ; Arpeggio table end index.
INST_ARPTABLELOOP       = $07  ; Arpeggio table loop index.
INST_VIBDELAY           = $08  ; Number of ticks before starting vibrato.
INST_VIBDEPTH_SPEED     = $09  ; Vibrato: high nybble=depth, low nybble=speed
INST_PULSEWIDTH         = $0a  ; Pulse width bits 11..4 (8 MSBs)
INST_PULSESPEED         = $0b  ; Pulse variation speed bits 7..0.
INST_PULSELIMITS        = $0c  ; Pulse variation limit.
                               ;   Low nybble  = lower limit bits 11..8
                               ;   High nybble = upper limit bits 11..8
INST_FILTERTABLESTART   = $0d  ; Filter table start index.
INST_FILTERTABLEEND     = $0e  ; Filter table end index.
INST_FILTERTABLELOOP    = $0f  ; Filter table loop index.
```

### Instrument Table AOS Layout
Instruments are stored as Arrays Of Structs at $4800, but the INSTRUMENTS_* constants
also exist for column-stride access (each column = one field for all 32 instruments):
```asm
INSTRUMENTS_AD               = 0*MAX_INSTRUMENTS+INSTRUMENTS   ; $4800
INSTRUMENTS_SR               = 1*MAX_INSTRUMENTS+INSTRUMENTS   ; $4820
INSTRUMENTS_WAVETABLESTART   = 2*MAX_INSTRUMENTS+INSTRUMENTS   ; $4840
INSTRUMENTS_WAVETABLEEND     = 3*MAX_INSTRUMENTS+INSTRUMENTS   ; $4860
INSTRUMENTS_WAVETABLELOOP    = 4*MAX_INSTRUMENTS+INSTRUMENTS   ; $4880
INSTRUMENTS_ARPTABLESTART    = 5*MAX_INSTRUMENTS+INSTRUMENTS   ; $48A0
INSTRUMENTS_ARPTABLEEND      = 6*MAX_INSTRUMENTS+INSTRUMENTS   ; $48C0
INSTRUMENTS_ARPTABLELOOP     = 7*MAX_INSTRUMENTS+INSTRUMENTS   ; $48E0
INSTRUMENTS_VIBDELAY         = 8*MAX_INSTRUMENTS+INSTRUMENTS   ; $4900
INSTRUMENTS_VIBDEPTH_SPEED   = 9*MAX_INSTRUMENTS+INSTRUMENTS   ; $4920
INSTRUMENTS_PULSEWIDTH       = 10*MAX_INSTRUMENTS+INSTRUMENTS  ; $4940
INSTRUMENTS_PULSESPEED       = 11*MAX_INSTRUMENTS+INSTRUMENTS  ; $4960
INSTRUMENTS_PULSELIMITS      = 12*MAX_INSTRUMENTS+INSTRUMENTS  ; $4980
INSTRUMENTS_FILTERTABLESTART = 13*MAX_INSTRUMENTS+INSTRUMENTS  ; $49A0
INSTRUMENTS_FILTERTABLEEND   = 14*MAX_INSTRUMENTS+INSTRUMENTS  ; $49C0
INSTRUMENTS_FILTERTABLELOOP  = 15*MAX_INSTRUMENTS+INSTRUMENTS  ; $49E0
```

### Pattern Structure (at PATTERNS = $4200)
256 patterns. Each pattern = 3 track numbers + 3 transpose values = 6 bytes.
Total $600 bytes for all patterns ($4200..$47FF).

### Track Structure (at TRACKS_BASE = $5000)
128 tracks. Each track = 64 rows * 3 bytes = 192 bytes.
Per row: [note] [instrument + effect_hi] [effect_lo]
(Note: this is a C64 3-voice tracker; 3 tracks per pattern.)

### Player Zero Page
```asm
player_trackptr   = $fb    ; 16-bit pointer to current track (2 bytes: $fb/$fc)
player_patternptr = $fd    ; 16-bit pointer to current pattern (2 bytes: $fd/$fe)
player_vibratotemp = player_patternptr  ; Alias (never used simultaneously)
```

### Packed Song Format
Songs are RLE-packed (as of v1.13). Data saved from $4000 to end of last track.
No player routine included in saved data. $FF terminates orderlist and subsong list.

Song start table at SONGSTARTTABLE = $4f00 (subsong support).

### Player Relocation
Packed songs can relocate player to any page boundary. Unpacked player at VPLAYER = $b000.

Packed song API:
```
Init: LDA <songnumber>; JSR $xx00
Play: JSR $xx03
Stop: JSR $xx06
```

## Source Files in OdinTracker113src.zip
```
6510.s          Number of bytes per 6510 instruction.
Makefile        Build orchestrator (aliases makefile.unx)
README          Build instructions (DASM required; gcc/Watcom/MSVC for utils)
defines.s       All constants and memory layout (THIS FILE)
eplayer.s       Editor's player (non-relocatable).
kernal.s        Kernal entry points + key codes.
tracker.s       Editor's main module (243,572 bytes — the bulk of the editor).
vplayer.s       Relocatable player (36,094 bytes).
vplayeri.s      Hack to tell relocator where player code ends (69 bytes).
testirq.s       IRQ test stub.
labels.awk      AWK script: converts DASM symbol dump to VICE label file.
c64pack/        PC-side packer (c64pack.cpp) + C64 depacker (depacker.s).
font/           Font converter (tga2bm.cpp) + font.tga.
freqtab/        Frequency table generator (freqtab.cpp).
help/           Help text system: help.in (source) + paginate.cpp + help.s.
vibrato/        Vibrato table (vibrato.s).
```

## Key Format Notes
- **Instrument 0:** Cannot be defined; acts as "no instrument change".
- **Wave table $FF:** Sets waveform + ADSR to 0 (sharp gate-off effect; added v1.13).
- **Absolute arpeggio:** Arp byte >= $80 → note = byte - $80 (ignore transpose).
- **Filter changed in v1.10:** Separate filter table per instrument instead of track effect only.
- **Hard restart:** Default 2 ticks; per-voice via effect FFx; FF0 disables (tie notes).
- **Pulse width:** INST_PULSEWIDTH = bits 11..4; INST_PULSESPEED adds to bits 7..0 per tick.
  INST_PULSELIMITS: low nybble = lower limit bits 11..8, high nybble = upper limit bits 11..8.
- **Vibrato:** INST_VIBDEPTH_SPEED = depth (hi nybble) | speed (lo nybble); true sine table.
