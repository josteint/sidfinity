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
