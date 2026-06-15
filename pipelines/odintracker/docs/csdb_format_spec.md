---
source_url: https://csdb.dk/getinternalfile.php/154684/OdinTracker113src.zip (defines.s, vplayer.s, tracker.s, help/help.in)
fetched_via: curl 2026-06-15
fetch_date: 2026-06-15
author: Zed (Zoltan Konyha)
content_date: 2001-04-17 (v1.13)
reliability: primary (directly from source code)
---

# OdinTracker v1.13 — Format Specification (from source)

Derived entirely from `defines.s`, `vplayer.s`, and `help/help.in` in `OdinTracker113src.zip`.

## Memory Map (editor / unpacked song)

```
$0810–$3800   Editor code + initialized/readonly data
$3800–$3A00   Font
$3A00–$3F80   Key mapping + read/write and uninitialized editor data
$3F80–$3FC0   Track row highlight sprite
$3FC0–$4000   Cursor sprite
$4000–$4100   Orderlist (256 bytes)
$4100–$4120   Song title (32 bytes)
$4120–$4200   [unused]
$4200–$4800   Patterns (256 patterns × (3 track numbers + 3 transposes) = $600 bytes)
$4800–$4A00   Instruments (32 instruments × 16 bytes = $200 bytes)
$4A00–$4C00   Instrument names (32 × 16 bytes = $200 bytes)
$4C00–$4D00   Wave table (256 bytes)
$4D00–$4E00   Arpeggio table (256 bytes)
$4E00–$4F00   Filter table (256 bytes)  ← added in v1.10
$4F00–$5000   Song start positions (256 bytes)  ← for multi-song packed files
$5000–$B000   Tracks (128 tracks × 64 rows × 3 bytes = $18000 bytes = 6000h = $B000)
$B000–$BF00   Relocatable player (vplayer)
$BF00–$C000   Opcode list (for packer/relocator)
$C000–$CE00   Editor's player (eplayer)
$CE00–$D000   Instrument format conversion buffer (old→new)
$D000–$xxxx   Help text
```

## Limits

- MAX_ORDERS = 256
- MAX_PATTERNS = 256
- MAX_TRACKS = 128
- MAX_INSTRUMENTS = 32 (instrument 0 = no instrument; 31 usable instruments, 1–31)
- SONGTITLELEN = 32 bytes
- INSTRUMENTLEN = 16 bytes
- INSTRUMENTNAMELEN = 16 bytes
- Track rows: 64 rows per track
- Track bytes: 64 × 3 = 192 bytes per track

## Instrument Format (16 bytes, offsets 0–15)

```
$00  INST_AD              Attack/Decay (SID format)
$01  INST_SR              Sustain/Release (SID format)
$02  INST_WAVETABLESTART  Wave table start index (0–255)
$03  INST_WAVETABLEEND    Wave table end index (0–255)
$04  INST_WAVETABLELOOP   Wave table loop index (0–255; if end reached, jump here)
$05  INST_ARPTABLESTART   Arpeggio table start index
$06  INST_ARPTABLEEND     Arpeggio table end index
$07  INST_ARPTABLELOOP    Arpeggio table loop index
$08  INST_VIBDELAY        Vibrato delay (ticks before vibrato starts)
$09  INST_VIBDEPTH_SPEED  High nybble = depth, low nybble = speed
$0A  INST_PULSEWIDTH      Pulse width bits 11..4 (8 MSBs of 12-bit PW)
$0B  INST_PULSESPEED      Pulse variation speed (added to 8 LSBs of PW each tick)
$0C  INST_PULSELIMITS     Low nybble = lower limit bits 11..8; high nybble = upper limit bits 11..8
$0D  INST_FILTERTABLESTART Filter table start index  ← added v1.10
$0E  INST_FILTERTABLEEND   Filter table end index    ← added v1.10
$0F  INST_FILTERTABLELOOP  Filter table loop index   ← added v1.10
```

Instruments are stored TRANSPOSED in memory:
- All 32 AD bytes at $4800+0*32 = $4800
- All 32 SR bytes at $4800+1*32 = $4820
- All 32 WAVETABLESTART at $4800+2*32 = $4840
- etc. (struct-of-arrays layout, not array-of-structs)

## Pattern Format

Patterns at $4200: 256 patterns, each entry is 6 bytes:
- 3 track numbers (one per voice)
- 3 transpose values (one per voice)

Total: 256 × 6 = $600 bytes.

Track transpose: $0C = octave up, $8C = octave down (per help).

## Track Row Format (3 bytes per row)

```
Byte 0: note + bit 7 of effect number
  bits 6..0: note (0=empty, 1=C-0 .. 96=B-7, 97=note off)
  bit 7:     high bit of effect number

Byte 1: instrument number + 3 low bits of effect number
  bits 4..0: instrument number (0=no instrument, 1–31)
  bit 7:     rotated into effect number as bit 3 (i.e. effect bit 3 = input bit 7, rotated right)
  bits 6..5: effect bits 2..1 (after ROR + 4× LSR)
  bit 0: effect bit 0

Byte 2: effect parameter (0–255)
```

From `fetchrow` in vplayer.s:
```
lda (player_trackptr),y    ; byte 0: note+high effect bit
cmp #$80                   ; sets C = bit7
and #$7f                   ; note 0..127
...
lda (player_trackptr),y    ; byte 1
ror                         ; shift bit7 into C (= effect bit 3), bit0→C old C
lsr / lsr / lsr / lsr      ; shift right 4 more → bits 7..4 of orig become bits 3..0
sta chn_effect,x           ; effect = 4 bits (0–15)
...
lda (player_trackptr),y    ; byte 2: effect parameter
sta chn_effectpar,x
```

Effect number is 4 bits (0–15 = 0x0–0xF), packed across 2 bytes:
- bit 3: from byte 0 bit 7
- bits 2..0: from byte 1 after ROR+4×LSR (i.e. the original high nybble of byte 1, with carry from byte 0's bit 7)

## Wave Table

256 bytes at $4C00. Each byte is written directly to SID voice waveform register ($D404/$D40B/$D412 respectively).

Special: if byte == $FF, waveform AND ADSR parameters (AD, SR) are set to 0.
Gate bit: if bit 0 of wave table byte is 0, gate is released (note off). Gate stays set if bit 0 is 1.

## Arpeggio Table

256 bytes at $4D00. Each byte is added to the base note.
- Byte < $80: relative arpeggio (add to note + transpose)
- Byte >= $80: absolute arpeggio (use byte-$80 as note number; note 1 = C-0; no transpose applied)

## Filter Table

256 bytes at $4E00 (v1.10+). Each byte is the 8 MSBs of the filter cutoff frequency ($D416 bits 7..0, the high byte of the 11-bit cutoff). Played back with start/end/loop from instrument.

## Song Start Positions

$4F00: list of orderlist indices, one per sub-song. Terminated by $FF.
Used only in packed songs for multi-song files.

## Player API (vplayer.s, relocatable)

```
$xx00   Init — A = song number (0-based index into SONGSTARTTABLE)
$xx03   Play frame — call every VBI (50 Hz PAL)
$xx06   Stop — shuts up SID (resets all registers to 0/$08/0 pattern)
$xx09   Quick driver hack — plays until key pressed (RETURN/RUN-STOP)
```

Zero-page used: $FB–$FE (player_trackptr at $FB/$FC, player_patternptr / player_vibratotemp at $FD/$FE).
Player takes ~$30 raster lines per frame (noted as "slow" in HISTORY).

Default speed: 6 ticks/row. Speed 0 stops song playback but continues effects.

## Effects (0x0–0xF)

| Effect | Name | Description |
|--------|------|-------------|
| 0 | None | No effect |
| 1 | Slide | param<$80: slide down; param>=$80: slide up by param-$80. Speed multiplied by 16. |
| 2 | Set pulse width | param = bits 11..4 of pulse width |
| 3 | Slide to note | Slide toward new note frequency (like MOD effect 3). No hardrestart when active. |
| 4 | Vibrato | High nybble = depth, low = speed. Overrides instrument vibrato. |
| 5 | Set pulse speed | param → chn_plsspeed |
| 6 | Set pulse limits | High nybble = lower limit bits 11..8; low nybble = upper limit bits 11..8 |
| 7 | Set AD | param → chn_ad (Attack/Decay) |
| 8 | Set SR | param → chn_sr (Sustain/Release) |
| 9 | Set waveform | param → chn_waveform (overrides wave table) |
| A | Arpeggio | High nybble = +semitones note 1; low nybble = +semitones note 2; base note on off-ticks. Like MOD Axy. Overrides arp table. |
| B | Order jump | param → jump to this orderlist position |
| C | Set filter cutoff | param = 8 MSBs of cutoff. Overrides filter table. |
| D | Pattern break | param = row to start next pattern at (hex). |
| E | Filter resonance/input | High nybble = resonance; bits 0,1,2 = enable filter for voice 1,2,3 → $D417 |
| F | Multi-purpose (see below) |

### Effect F sub-commands

| F param | Action |
|---------|--------|
| $00–$7F | Set speed (0 = stop playback, continue effects) |
| $80–$8F | Set global volume to low nybble |
| $90–$9F | Set filter mode: bit0=LP, bit1=BP, bit2=HP, bit3=cut voice 3 → $D418 high nybble |
| $A0–$AF | Fine slide down (only on speedcounter==0; amount×4) |
| $B0–$BF | Fine slide up (only on speedcounter==0; amount×4) |
| $C0–$CF | Note cut at tick = low nybble |
| $D0–$DF | Note delay (TODO in source, not implemented) |
| $E0–$EF | Select instrument for filter cutoff control (low nybble = instrument number; 0 = disable filter table) |
| $F0–$FF | Set hard restart ticks for this voice to low nybble |

## Hard Restart

Default: 2 ticks before new note. Controlled per-voice via F$Fx effect.
FF0 disables hard restart (useful for tied notes).
Hard restart is always disabled when effect 3 (slide to note) is active.

## SID Register Write Order (per frame, from vplayer.s pp_dump2sid)

For each voice (x=2,1,0):
1. $D402+y = chn_plswidthlo  (pulse width low)
2. $D403+y = chn_plswidthhi  (pulse width high)
3. $D400+y = chn_finfreqlo   (frequency low)
4. $D401+y = chn_finfreqhi   (frequency high)
5. if waveform==$FF: $D404+y=$00, $D405+y=$00 (silence/hard reset)
   else: $D404+y = chn_waveform & chn_gateon  ($D404 = wave+gate)
         $D405+y = chn_ad
6. $D406+y = chn_sr

Then global:
7. $D416 = filter_cutoff
8. $D417 = filter_input (resonance + voice routing)
9. $D418 = globalvolume | filter_mode

## Init Behavior

From player_init (vplayer.s):
1. Clear all player state (playercleardata region)
2. sta forcenewpattern = $80 (force new pattern fetch)
3. Read SONGSTARTTABLE,x → ordernumber + nextordernumber
4. Speed = 6, speedcounter = 5
5. chn_hardrestart[0..2] = 2 (default 2 ticks)
6. globalvolume = $0F

player_stop resets all SID registers: writes $08 then $00 to each of $D400..$D418 in reverse order.

## Frequency Table

Generated by `freqtab/freqtab.cpp` from PAL clock (985248 Hz). Two 256-byte tables:
`freqtablelo` and `freqtablehi`. Note 0 = empty (never looked up); note 1 = C-0; note 96 = B-7.

## Vibrato

Sine-based, 256-byte table (64 entries per depth level, 4 depth levels per table entry).
Vibrato position cycles 0..63 (6 bits): bits 5..4 select add/subtract phase quadrant.
Speed/depth from instrument or effect 4.

## Packed Song File Layout

After packing/relocation:
- Player relocatable to any page boundary (default $B000 but configurable)
- Song data: $4000..end-of-last-used-track (saved RLE-compressed in v1.1x)
- Song title saved at packed_base+$20 (de facto standard as of v1.12)
- Track pointers (lo/hi) and transposes are pre-computed for each voice/order:
  TRACKTRANSPOSES0/1/2, TRACKPOINTERSLO0/1/2, TRACKPOINTERSHI0/1/2
  at runtime pages $F0–$F8 in the editor; relocated with the player.

## Format Change v1.0x → v1.1x

- Filter table added ($4E00–$4F00)
- Instrument bytes 13–15 added (filter table start/end/loop)
- Vibrato algorithm changed (pitch-independent vibrato removed)
- Pulse width modulation refined
- Multi-song support added (song start positions at $4F00)
- Old 1.0x songs can be imported (losing filter settings)
