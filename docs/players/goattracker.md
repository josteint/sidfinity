# GoatTracker V1/V2

## Overview

- **HVSC count:** V2: 7,550 tunes, V1: 1,384 tunes (total 8,934)
- **Author:** Lasse Oorni (Cadaver) of Covert Bitops
- **Source:** https://github.com/leafo/goattracker2 (V2 mirror), https://sourceforge.net/projects/goattracker2/
- **Player license:** Free for any purpose including commercial (non-GPL)
- **Key refs:** GoatTracker guide, ChiptuneSAK docs, cadaver's miniplayer repos

## Entry Points (exported SID)

| Offset | Function |
|--------|----------|
| base+0 | JMP init (A = subtune number, 0-based) |
| base+3 | JMP play (call once per frame) |
| base+6 | JMP playsfx (optional) |
| base+9 | JMP setmastervol (optional) |

## Song File Format (.SNG) - "GTS5"

### Header (101 bytes)

| Offset | Size | Description |
|--------|------|-------------|
| +0 | 4 | ID: `GTS5` (V2.59+), older: `GTS3`, `GTS4` |
| +4 | 32 | Song name |
| +36 | 32 | Author name |
| +68 | 32 | Copyright |
| +100 | 1 | Number of subtunes |

### Orderlists (per channel per subtune)

Each orderlist: 1 byte length (n), then n+1 bytes (data + restart position).

- `$00-$CF`: Pattern numbers (max 208)
- `$D0-$DF`: Repeat 1-16 times
- `$E0-$EF`: Transpose down 0-15 halftones
- `$F0-$FE`: Transpose up 0-14 halftones ($F0=none)
- `$FF`: End mark, next byte = restart position

### Instruments (max 63)

| Offset | Field |
|--------|-------|
| 0 | Attack/Decay |
| 1 | Sustain/Release |
| 2 | Wave table pointer (1-based, 0=unused) |
| 3 | Pulse table pointer |
| 4 | Filter table pointer |
| 5 | Vibrato param (speed table ptr) |
| 6 | Vibrato delay |
| 7 | Gate-off timer (bits 0-5), bit 6=legato, bit 7=no hard restart |
| 8 | 1st frame waveform ($00=skip, $01-$FD=waveform, $FE-$FF=skip+gate) |
| 9-24 | Instrument name (16 bytes) |

### Tables (4 sections: Wave, Pulse, Filter, Speed)

Each: 1 byte row count (n), n bytes left column, n bytes right column. Max 255 rows.

#### Wave Table
- Left $00: no change; $01-$0F: delay; $10-$DF: waveform; $E0-$EF: inaudible wave; $F0-$FE: wave commands; $FF: jump
- Right: $00-$5F relative note up, $60-$7F relative down, $80 keep freq, $81-$DF absolute note

#### Pulse Table
- Left $01-$7F: modulation duration; $80-$FF: set pulse width; $FF: jump
- Right: signed speed (modulation) or low 8 bits (set)

#### Filter Table
- Left $00: set cutoff; $01-$7F: modulation duration; $80-$FF: set filter params; $FF: jump
- Right: cutoff/speed/resonance+routing depending on left byte

#### Speed Table (vibrato/portamento/funktempo)
- Vibrato: left=speed (bit 7=note-independent), right=depth
- Portamento: 16-bit value (left=MSB, right=LSB)
- Funktempo: left=tempo1, right=tempo2

### Patterns (max 208, max 128 rows)

Each row in .sng = 4 bytes:
- Byte 0: Note ($60-$BC = C-0 to G#7, $BD=rest, $BE=keyoff, $BF=keyon, $FF=end)
- Byte 1: Instrument ($00-$3F)
- Byte 2: Command ($00-$0F)
- Byte 3: Command data

### Pattern Commands

| Cmd | Name | Description |
|-----|------|-------------|
| 0 | Do nothing | Instrument vibrato |
| 1 | Porta up | Speed table index |
| 2 | Porta down | Speed table index |
| 3 | Tone porta | Speed table index ($00=tie) |
| 4 | Vibrato | Speed table index |
| 5 | Set AD | Value |
| 6 | Set SR | Value |
| 7 | Set wave | Waveform value |
| 8 | Set wave ptr | Wave table index |
| 9 | Set pulse ptr | Pulse table index |
| A | Set filter ptr | Filter table index |
| B | Set filter ctrl | Resonance(hi) + routing(lo) |
| C | Set filter cutoff | Value |
| D | Set master vol | $00-$0F=volume |
| E | Funktempo | Speed table index |
| F | Set tempo | $03-$7F=global, $83-$FF=channel-only |

## Packed/Exported SID Format

The `greloc.c` packer/relocator heavily optimizes the .sng into a completely different binary format. Source: [github.com/leafo/goattracker2](https://github.com/leafo/goattracker2)

### Exact Data Section Order (from greloc.c)

```
1. Player code (player.s, assembled at base address)
2. Frequency table lo (mt_freqtbllo, trimmed to used note range)
3. Frequency table hi (mt_freqtblhi)
4. Song table lo (mt_songtbllo, songs*3 entries)
5. Song table hi (mt_songtblhi)
6. Pattern table lo (mt_patttbllo, num_patterns entries)
7. Pattern table hi (mt_patttblhi)
8. Instrument columns (column-major, see below)
9. Wave table left (mt_wavetbl), then right (mt_notetbl)
10. Pulse table left (mt_pulsetimetbl), right (mt_pulsespdtbl) [if !NOPULSE]
11. Filter table left (mt_filttimetbl), right (mt_filtspdtbl) [if !NOFILTER]
12. Speed table left (mt_speedlefttbl), right (mt_speedrighttbl) [extra zero prepended]
13. Song orderlists (raw bytes per song per channel)
14. Pattern data (packed bytes per pattern)
```

### Instrument Column Layout (Column-Major)

Each column is `ni` bytes (number of used instruments). Columns are contiguous. Some are conditionally omitted:

| Index | Label | Content | Condition |
|-------|-------|---------|-----------|
| 0 | `mt_insad` | Attack/Decay | Always |
| 1 | `mt_inssr` | Sustain/Release | Always |
| 2 | `mt_inswaveptr` | Wave table ptr (remapped) | Always |
| 3 | `mt_inspulseptr` | Pulse table ptr | Only if `!NOPULSE` |
| 4 | `mt_insfiltptr` | Filter table ptr | Only if `!NOFILTER` |
| 5 | `mt_insvibparam` | Speed table ptr (vibrato) | Only if `!NOINSVIB` |
| 6 | `mt_insvibdelay` | Vibrato delay - 1 | Only if `!NOINSVIB` |
| 7 | `mt_insgatetimer` | Gate timer & $3F | Only if `!FIXEDPARAMS` |
| 8 | `mt_insfirstwave` | First frame waveform | Only if `!FIXEDPARAMS` |

Player accesses as `LDA mt_insXX-1,Y` where Y is 1-based instrument number.

### Instrument Sorting

Instruments are reindexed by type:
1. Normal HR instruments (indices 1 to NUMHRINSTR)
2. No-HR instruments (from FIRSTNOHRINSTR)
3. Legato instruments (from FIRSTLEGATOINSTR)

### Packed Pattern Encoding

Variable-length byte stream per pattern:
- `$00`: End of pattern
- `$01-$3F`: Instrument change (1-based index)
- `$40-$4F`: Effect + note follows (`$40 + effect_number`, param byte if cmd!=0)
- `$50-$5F`: Effect + rest (`$50 + effect_number`, param byte if cmd!=0)
- `$60-$BC`: Note values (FIRSTNOTE-relative)
- `$BD`: Rest, `$BE`: Keyoff, `$BF`: Keyon
- `$C0-$FF`: Packed rests (count = 256 - value)

### Conditional Compilation Flags

~40 flags set by the relocator based on song analysis:
```
NOPULSE, NOFILTER, NOVIB, NOINSTRVIB, NOTONEPORTA, NOPORTAMENTO,
NOEFFECTS, NOSETAD, NOSETSR, NOSETWAVE, NOSETWAVEPTR,
NOSETPULSEPTR, NOSETFILTPTR, NOSETFILTCTRL, NOSETFILTCUTOFF,
NOSETMASTERVOL, NOFUNKTEMPO, NOCHANNELTEMPO, NOGLOBALTEMPO,
NOWAVEDELAY, NOWAVECMD, NOFIRSTWAVECMD, NOTRANS, NOREPEAT,
SIMPLEPULSE, FIXEDPARAMS, NOCALCULATEDSPEED, NONORMALSPEED,
ZPGHOSTREGS, BUFFEREDWRITES, SOUNDSUPPORT, VOLSUPPORT
```

Player size varies from ~200 to ~800+ bytes depending on which flags are set.

### Wave Table Format (in packed SID)

Left column (`mt_wavetbl`):
- `$00`: No waveform change
- `$01-$0F`: Delay N frames (if `NOWAVEDELAY==0`)
- `$10-$DF`: Waveform value (player subtracts $10 before use? NO — see below)
- `$E0-$EF`: Inaudible wave / command
- `$F0-$FE`: Wave commands
- `$FF`: Loop/jump (right column = target index, 1-based)

Right column (`mt_notetbl`):
- `$00-$5F`: Relative note up
- `$60-$7F`: Relative note down (two's complement from $80)
- `$80`: Keep current frequency
- `$81-$DF`: Absolute note

**Important:** Wave table values in packed format differ from .sng format. The packer maps instrument `firstwave` and wave table entries through `tablemap[][]` which can remap indices.

### Channel State (stride 7 for X=0,7,14)

```
mt_chnsongptr, mt_chntrans, mt_chnrepeat, mt_chnpattptr,
mt_chnpackedrest, mt_chnnewfx, mt_chnnewparam, mt_chnfx,
mt_chnparam, mt_chnnewnote, mt_chnwaveptr, mt_chnwave,
mt_chnpulseptr, mt_chnpulsetime, mt_chnsongnum, mt_chnpattnum,
mt_chntempo, mt_chncounter, mt_chnnote, mt_chninstr,
mt_chngate, mt_chnvibtime, mt_chnvibdelay, mt_chnwavetime,
mt_chnfreqlo, mt_chnfreqhi, mt_chnpulselo, mt_chnpulsehi,
mt_chnad, mt_chnsr, mt_chngatetimer, mt_chnlastnote
```

## V1 vs V2 Differences

- V1 IDs: `GTS3`, `GTS4`; V2: `GTS5`
- V1 had arpeggio command; V2 replaced with wave tables
- V2 added 63 instruments, uniform step-programming tables, more commands
- V2 can load V1 songs

## References

- [GoatTracker V2 source (GitHub mirror)](https://github.com/leafo/goattracker2)
- [GoatTracker official page](https://cadaver.github.io/tools.html)
- [Cadaver's miniplayer](https://github.com/cadaver/miniplayer)
- [ChiptuneSAK GT2 docs](https://github.com/c64cryptoboy/ChiptuneSAK/blob/master/docs/goattracker.rst)
