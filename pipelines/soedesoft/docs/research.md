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
