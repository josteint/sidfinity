---
source_url: https://csdb.dk/getinternalfile.php/154684/OdinTracker113src.zip (file: vplayer.s)
fetched_via: direct
fetch_date: 2026-06-15
author: Zed (Zoltán Konyha)
content_date: 2001-04-17
reliability: primary
---

# OdinTracker 1.13 Relocatable Player Internals

Extracted from `vplayer.s` in `OdinTracker113src.zip`.
This is the player routine saved with packed songs (VPLAYER = $b000 in editor layout;
packed songs relocate this to a user-specified page boundary).

## Player Entry Points

```asm
; Default layout (before relocation): base = $1000 example in comments
VPLAYER+$00:  JMP player_init    ; Init, song number in A register
VPLAYER+$03:  JMP player_play    ; Play one frame (call every VBI)
VPLAYER+$06:  JMP player_stop    ; Stop playing, silence SID
VPLAYER+$09:  Quick driver hack  ; Play song until keypress (fills space to song title)
```

### Song Title Location
Song title (32 bytes) is stored just after the quick driver code, before player_init proper.
This means the packed binary starts with: [JMP table (9 bytes)] [quick driver] [song title (32 bytes)] [player code].

## player_init (VPLAYER+$00)
Input: A = song number (0-based index into SONGSTARTTABLE)

```
1. Clear all player work RAM.
2. Set ordernumber and nextordernumber from SONGSTARTTABLE[song_number].
3. Init speed = 6, speedcounter = 5.
4. Init hard restart ticks: chn_hardrestart[0..2] = 2.
5. Set globalvolume = $0F (maximum).
```

## player_stop (VPLAYER+$06)
```
Reset all SID registers $D400..$D418 to $08 then $00 (SID reset sequence).
Return.
```

## player_play (VPLAYER+$03)
Called every frame (once per VBI). Main player loop:

### Timing / Row Advance
- Uses `mod3counter` (mod-3 counter for arpeggio effect Axy, same as MOD-style).
- `speed` = ticks per row (default 6); speed=0 stops row advance but continues effects.
- `speedcounter` counts ticks; when `speedcounter == speed`, advance to next row.

### Row Fetch
On new row: reads from pattern data for each voice:
- `TRACKTRANSPOSES{0,1,2}[ordernumber]` → `chn_transpose[voice]`
- `TRACKPOINTERSLO{0,1,2}[ordernumber]` + `TRACKPOINTERSHI{0,1,2}[ordernumber]` → track pointer
- Each row: `jsr fetchrow` reads [note, instrument+fx_hi, fx_lo]

### Pattern Advance
- 64 rows per pattern.
- `nextordernumber` set by effect Bxx (order jump); otherwise increments.
- `firsttrackrow` set by effect Dxx (pattern break, hex parameter).
- `forcenewpattern` flag triggers new-pattern fetch immediately.

## Key State Variables (player zero page / work RAM)
```
player_trackptr   = $FB   ; 16-bit pointer to current track row
player_patternptr = $FD   ; 16-bit pointer to pattern (alias: player_vibratotemp)

ordernumber         ; Current position in orderlist
nextordernumber     ; Next order position (may be set by Bxx)
trackrow            ; Current row in pattern (0-63)
trackrow3           ; 3*trackrow (byte offset into track)
firsttrackrow       ; Row to start from in next pattern (Dxx sets this)
forcenewpattern     ; Flag: force fetch of new pattern
speed               ; Ticks per row
speedcounter        ; Current tick count
mod3counter         ; Arpeggio modulo-3 counter
globalvolume        ; $D418 lower nybble ($0F = max)
chn_hardrestart[3]  ; Hard restart ticks remaining per voice (default 2)
chn_transpose[3]    ; Track transpose per voice
```

## Player Performance Note (from source comments + intro page)
"The player is nothing advanced and altogether is painfully slow."
"Takes around $30 rasterlines." (~$30 rasterlines = ~768 cycles @ PAL)
The player was intended for demos/games needing a relocatable, simple player.
Pitch-independent vibrato was removed in v1.10 (too expensive: 1 multiplication/voice/frame).

## Packed Song Binary Layout
```
[JMP player_init]        ; 3 bytes
[JMP player_play]        ; 3 bytes
[JMP player_stop]        ; 3 bytes
[Quick driver code]      ; variable
[Song title, 32 bytes]   ; at fixed offset from player base
[player code...]
```
After player code: (at SONGSTARTTABLE offset) subsong start indices, then music data
(orderlist $4000, patterns $4200, instruments $4800, tables $4C00-$4FFF, tracks $5000+).

## Dat2Sid Integration
The Dat2Sid utility wraps a packed OdinTracker binary (player + data) into a PSID file:
- Load address: the relocated player base address
- Init address: player base + $00
- Play address: player base + $03
- Song number passed in A to init
