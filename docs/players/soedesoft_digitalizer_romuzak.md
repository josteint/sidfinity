# SoedeSoft, Digitalizer, RoMuzak

## SoedeSoft / Soundmaster (950 tunes)

- **Authors:** Jeroen Soede (code/music routine) and Michiel Soede (editor/music), Netherlands
- **Year:** 1988-1989
- **Source:** Not public
- **CSDb:** #10735 (V1.0), #90307 (V3.1 with German PDF docs)
- **Versions:** SoedeSound Editor V1.0 (1988), Soundmaster V1.0-V3.2 (1989)

### Entry Points
- +$0000: JMP init
- +$0003: JMP play

### Technical Details
- Player code: ~884 bytes
- Variables at page 3 ($0333-$039D, ~106 bytes)
- Init clears variable area: `LDA #$00; LDY #$69; STA $0333,Y; DEY; BNE`
- Uses indexed addressing (`STA $D4xx,X`) for per-voice registers (X=0/7/14)
- Embedded signature: `"88 SOEDESOFT-"` in data area
- Load address relocatable (seen at $1800, $2000, $3800, $6000, $F000, $F400)
- VBlank/50Hz timing

### Effects
Arpeggios, wave patterns (waveform cycling), pulse width modulation, filter modulation. "Nothing was ripped" — developed from scratch.

### Notable Users
Nagie Sascha (157 tunes), Danko Tomas (52), Vulgarik (48), Doussis Stello (46), Drumtex (40).

---

## Digitalizer V2.x (680 tunes)

- **Author:** Olav Morkrid (OFF / Omega Supreme) of Panoramic Designs, Norway
- **Year:** 1989-1995
- **Source:** Not public
- **CSDb:** #33646 (V2.2), #33649 (V3.0)
- **Versions:** V2.2 (1989), V2.5, V2.7, V2.8 (1991), V3.0 (1992), V3.5 (1995)

### Entry Points
- +$0000: JMP init (~offset +$04BD)
- +$0003: JMP speed_handler (~offset +$0495)
- +$0005: JSR main_player
- +$0025: ASCII credit string `"MUSIC AND PLAYER BY OLAV M0RKRID"` or `"PLAYER BY OLAV/PD"`

### Technical Details
- Player code: ~1200 bytes
- Variables at page 3 ($0334-$03A4)
- Uses both `STA $D4xx,X` and `STA $D4xx,Y` for voice registers
- Self-identifying via embedded credit string
- Speed divider at $033D (counter for variable playback speeds: 1x, 2x, 3x)
- Load address relocatable (commonly $1000, $9000)
- Typical total size: 2400-4000 bytes

### Notable Users
Blues Muz / Glenn Gallefoss (154 tunes), Olav Morkrid (8). Primarily Norwegian scene.

### Note
Olav Morkrid later co-founded Funcom and worked at Opera Software.

---

## RoMuzak V6.x (593 tunes)

- **Author:** Oliver Blasnik (ROM), Germany. Published by Digital Marketing.
- **Year:** 1989-1990
- **Source:** Not public
- **CSDb:** #17814 (V6.3), #17819 (V7.96)
- **Versions:** V6.3 (1989), V7.96 (March 1990)

### Entry Points (3 entry points)
- +$0000: JMP init
- +$0003: JMP play
- +$0006: JMP stop/reset
- +$0009: Signature string `"ROMUZAK89"` (9 bytes)

### Data Structure
- +$0012: Three 2-byte pointers to per-voice pattern data
- +$0018: Instrument parameter block (~136 bytes): per-instrument ADSR, waveform, pulse width, filter, vibrato/portamento
- +$00A2: Standard frequency table (96 entries, identical across all V6.x tunes)
- +$0202: Player code (~2636 bytes, largest of the three)

### Technical Details
- Uses `STA $D4xx,Y` (Y = 0/7/14 for voices)
- Writes: control, ADSR, pulse width, frequency, filter cutoff, volume/mode
- Default load at $8000, V7.96 at $7000
- VBlank/50Hz timing
- Total size: 2747-4041 bytes

### Key Feature: Future Composer Conversion
Can convert FC V1.0 songs. Many HVSC entries annotated "RoMuzak conversion of [FC tune]." Popular choice for German sceners repurposing existing FC tunes.

### Notable Users
Ass It (56), Stefan Hartwig (54), Sony (27), Thomas Detert (21), Goesta Feiweier (20). Predominantly German scene.
