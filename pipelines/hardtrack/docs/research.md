## HardTrack Composer (1,170 tunes)

- **Authors:** Brush (code) and Longhair/Milosz Ignatowski (player routine), Elysium/Parados (Poland)
- **Year:** 1992
- **Source:** Available at elysium.filety.pl (depacker, editor, assembly source)
- **CSDb:** #74928 (V1.0), #36647 (V1.0+)
- **Scene:** Primarily Polish C64 scene

### Entry Points (typical load $1000)
- $1000: JMP init
- $1003: JMP play
- CIA timer-based (multispeed up to 6x)

### Memory Layout

| Offset | Purpose |
|--------|---------|
| +$000 | JMP init, JMP play |
| +$006 | Speed counter, subtune config |
| +$00A-$01B | Voice ADSR shadows, pattern pointers, track positions |
| +$01F | Metadata (song name, author, date) |
| +$060 | Init routine (~120 bytes) |
| +$0D8 | Play routine (~1200 bytes) |
| +$651 | Instrument macro data tables |
| +$880 | Frequency table hi (96 entries) |
| +$8E0 | Frequency table lo (96 entries) |
| +$919 | Track data |
| ~+$1020 | Pattern data |

Player code: ~1536 bytes. Total: 3000-6000 bytes.

### Track Data (per voice)
- $00-$7F: Pattern number
- $80-$FC: Change transposition (signed)
- $FD xx: Jump to position xx
- $FE: End (stop)
- $FF: Loop to beginning

### Pattern Data
- $00-$5F: Note (index into 96-entry freq table)
- $60: Rest/tie
- $61: DEL (gate off)
- $62: CUT (hard cut)
- $63 yy: Glissando up by yy
- $64 yy: Glissando down by yy
- $80-$FF: Set instrument (value AND $7F)
- $FF: End of pattern

### Instrument Macro Format
Pairs of xx yy bytes:
- xx = waveform register value
- yy = transposition ($00-$5C relative, $80-$DF absolute for drums)
- FX byte: hi nib = type (0=normal, 8=drum), lo nib = hard restart frames
- Additional: pulse start, filter start, vibrato width/add/end

### Features
Multispeed (up to 6x), hard restart, glissando up/down, instrument macros with waveform sequences, drum instruments (absolute pitch), pulse width and filter automation.

### Top Users
Bzyk (262), Klax (197), Randy (92), Remarque (87), Shapie (81).

---
