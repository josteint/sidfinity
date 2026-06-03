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
