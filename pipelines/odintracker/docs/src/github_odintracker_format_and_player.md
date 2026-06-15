---
source_url: https://csdb.dk/getinternalfile.php/154684/OdinTracker113src.zip
fetched_via: curl (direct download)
fetch_date: 2026-06-15
author: Zoltán Konyha (Zed)
content_date: 2001-04-17
reliability: primary
---

# OdinTracker 1.13 — Complete Format and Player Reference

Derived from primary source: `OdinTracker113src.zip` (vplayer.s, defines.s, eplayer.s, help.txt, HISTORY).
Also available at zimmers.net as OdinTracker113src.zip.

---

## 1. Memory Map (editor / unpacked song)

From `defines.s`:

```
$0801           BASIC
$0810           EDITOR code
$3800           FONT
$3A00           RWDATA (editor read/write + uninitialized data)
$3F80           SPRITEHILIGHT
$3FC0           SPRITECURSOR

$4000           ORDERLIST       (256 bytes — order list)
$4100           SONGTITLE       (32 bytes — song title)
$4200           PATTERNS        (256 patterns × 6 bytes = $600 bytes)
$4800           INSTRUMENTS     (32 instruments × 16 bytes = $200 bytes, column-major)
$4A00           INSTRUMENTNAMES (32 names × 16 bytes)
$4C00           WAVETABLE       (256 bytes)
$4D00           ARPEGGIOTABLE   (256 bytes)
$4E00           FILTERTABLE     (256 bytes)
$4F00           SONGSTARTTABLE  (256 bytes — start order positions for sub-songs)
$5000           TRACKS_BASE     (128 tracks × 64 rows × 3 bytes = $5800 bytes → top at ~$A800)

$B000           VPLAYER         (relocatable player, stored here in editor)
$BF00           OPCODELIST      (256 bytes — 6510 instruction lengths, for packer)
$C000           PLAYER          (editor's player, separate from vplayer)
$CE00           INSTRUMENTBUFFER (used when converting from old format)
$D000           HELPTEXT        ($3000 bytes)
```

After packing, the player + data is relocated by the user to any page boundary.

---

## 2. Song File Format (unpacked, ".sid"-less raw save)

Saved with CBM sequential file: raw memory $4000 to end-of-last-used-track.  
Load address: $4000 for plain saves, $4C52 for RLE-packed saves ("RL" in ASCII = the magic at load address).

RLE scheme (from tracker.s comments):
- Escape byte: $FF
- The file is the RLE-packed image of $4000..end-of-song

**Song title** at SONGTITLE ($4120 in the file), i.e. $xx20 in the packed file (de-facto standard per HISTORY).

---

## 3. Patterns

`PATTERNS = $4200`: 256 pattern entries, each 6 bytes:

```
byte 0,1,2: track number for voice 1,2,3 (index 0..127 into TRACKS_BASE)
byte 3,4,5: transpose for voice 1,2,3 (signed, $0C = +octave, $8C = -octave)
```

Pattern indices go into ORDERLIST ($4000, 256 bytes). Orderlist entry $FF = end of song.

---

## 4. Tracks

128 tracks, each 64 rows × 3 bytes = 192 bytes, base at $5000.
Track N starts at: $5000 + N × 192.

**Row format (3 bytes per row):**

```
Byte 0: note + bit 7 = high bit of effect number
  bits 6..0: note number (0=no note, 1=C-0, 96=B-7, 97=note off)
  bit 7: high bit of effect (effect bit 3)

Byte 1: instrument + 3 low bits of effect
  bits 7..5: 3 low bits of effect number (effect bits 2..1..0) — but decoded by ROR
  bits 4..0: instrument number (0=no instrument, 1..31=instrument)

  Decoding (from fetchrow in vplayer.s):
    lda byte1
    ror        ; C = bit7 of byte1 → rotated into bit3 of effect via carry from byte0 cmp
    lsr
    lsr
    lsr
    lsr
    → effect = (carry<<3) | (byte1 >> 5)  (4-bit effect number)

Byte 2: effect parameter (0..255)
```

Note numbering: C-0 = 1, C-1 = 13, ... B-7 = 96, note off = 97, no note = 0.

---

## 5. Instrument Format

32 instruments (indices 0..31; instrument 0 = "no instrument", cannot be defined).
Stored COLUMN-MAJOR: all 32 values of field N are stored contiguously.

```
INSTRUMENTS_AD              = $4800 + 0*32   AD (attack/decay)
INSTRUMENTS_SR              = $4800 + 1*32   SR (sustain/release)
INSTRUMENTS_WAVETABLESTART  = $4800 + 2*32   wave table start index (0..255)
INSTRUMENTS_WAVETABLEEND    = $4800 + 3*32   wave table end index (inclusive)
INSTRUMENTS_WAVETABLELOOP   = $4800 + 4*32   wave table loop index
INSTRUMENTS_ARPTABLESTART   = $4800 + 5*32   arpeggio table start
INSTRUMENTS_ARPTABLEEND     = $4800 + 6*32   arpeggio table end (inclusive)
INSTRUMENTS_ARPTABLELOOP    = $4800 + 7*32   arpeggio table loop
INSTRUMENTS_VIBDELAY        = $4800 + 8*32   vibrato delay (ticks before starting)
INSTRUMENTS_VIBDEPTH_SPEED  = $4800 + 9*32   vibrato: hi nybble=depth, lo=speed
INSTRUMENTS_PULSEWIDTH      = $4800 +10*32   pulse width: bits 11..4 (8 MSBs)
INSTRUMENTS_PULSESPEED      = $4800 +11*32   pulse variation speed (added to 8 LSBs each tick)
INSTRUMENTS_PULSELIMITS     = $4800 +12*32   pulse limits: hi nybble=lower limit bits 11..8,
                                             lo nybble=upper limit bits 11..8
INSTRUMENTS_FILTERTABLESTART= $4800 +13*32   filter table start
INSTRUMENTS_FILTERTABLEEND  = $4800 +14*32   filter table end (inclusive)
INSTRUMENTS_FILTERTABLELOOP = $4800 +15*32   filter table loop
```

Per-struct offsets (INSTRUMENTLEN=16):
```
$00  AD
$01  SR
$02  wave start
$03  wave end
$04  wave loop
$05  arp start
$06  arp end
$07  arp loop
$08  vib delay
$09  vib depth/speed
$0A  pulse width
$0B  pulse speed
$0C  pulse limits
$0D  filter start
$0E  filter end
$0F  filter loop
```

---

## 6. Wave Table ($4C00, 256 bytes)

Each byte = SID waveform value ($D404/$D40B/$D412).
- Gate bit (bit 0) is AND-ed with the channel's gate-on flag (see below).
- $FF = special: sets waveform AND ADSR to 0 (used for sharp/short sounds).

---

## 7. Arpeggio Table ($4D00, 256 bytes)

Each byte = semitone offset to add to current note.
- 0..$7F: relative — added to note + transpose
- $80..$FF: absolute — note = (byte AND $7F) + 1 (no transpose added)

---

## 8. Filter Table ($4E00, 256 bytes)

Each byte = 8 MSBs of filter cutoff frequency (→ SID $D416).
Stepped through using instrument filter start/end/loop indices.

---

## 9. Player Entry Points (packed/relocated player)

Player relocated to address $xx00 (page boundary chosen at pack time).

```
$xx00  JSR player_init    Init. A = song number (0-based index into SONGSTARTTABLE).
$xx03  JSR player_play    Play one frame. Call every VBI (~50Hz).
$xx06  JSR player_stop    Stop and silence SID.
$xx09  Quick driver       Plays song 0 until keypress (fills space before title).
$xx20  Song title         32 bytes ASCII (de-facto standard).
```

Zeropage used: $FB–$FE (player_trackptr at $FB/$FC, player_patternptr/$FD/$FE).

---

## 10. Effects (0–$F)

| Effect | Name | Parameter description |
|--------|------|----------------------|
| 0 | No-op | — |
| 1 | Slide | param < $80: slide down; param ≥ $80: slide up by param-$80. Step = param×16. |
| 2 | Set pulse width | param = 8 MSBs of pulse width (bits 11..4) |
| 3 | Slide to note | Like MOD portamento. Step = param×16. No hard restart. |
| 4 | Vibrato | hi nybble = depth, lo = speed. Overrides instrument vibrato. |
| 5 | Set pulse speed | param = pulse variation speed |
| 6 | Set pulse limits | hi nybble = lower limit bits 11..8; lo = upper limit bits 11..8 |
| 7 | Set AD | param = new attack/decay |
| 8 | Set SR | param = new sustain/release |
| 9 | Set waveform | param = waveform. Overrides wave table. |
| A | Arpeggio | ProTracker-style. hi nybble = note1 semitones, lo = note2. |
| B | Order jump | param = new order position |
| C | Set filter cutoff | param = 8 MSBs of cutoff. Overrides filter table. |
| D | Pattern break | param = first row of next pattern (hex, not decimal) |
| E | Filter resonance/input | hi nybble = resonance; bits 0,1,2 = voice 1,2,3 filter enable |
| F | Multi-function: | |
| | F $00–$7F | Set speed. Speed 0 = stop song, continue effects. Default = 6. |
| | F $80–$8F | Set global volume (low nybble) |
| | F $90–$9F | Set filter mode (low nybble: bit0=LP, bit1=BP, bit2=HP, bit3=cut V3 output) |
| | F $A0–$AF | Fine slide down (once per row only; step = param×4) |
| | F $B0–$BF | Fine slide up (once per row only; step = param×4) |
| | F $C0–$CF | Note cut at tick = low nybble |
| | F $D0–$DF | Note delay (TODO in source — not implemented!) |
| | F $E0–$EF | Select instrument (low nybble) as filter controller |
| | F $F0–$FF | Set hard restart ticks (low nybble). Default = 2. FF0 = disable. |

---

## 11. Channel State (per-voice runtime variables)

From vplayer.s variable layout:

```
chn_hardrestart[3]   ticks to silence before new note (NOT cleared on play start)
--- playercleardata (zeroed on init) ---
chn_gateon[3]        $FF = gate on, $FE = gate off (AND-ed with waveform bit0)
chn_plsdir[3]        0 = pulse increasing, nonzero = decreasing
chn_transpose[3]     track transpose from pattern
chn_note[3]          current note (1=C-0, 96=B-7, 0=none)
chn_inst[3]          current instrument (1..31)
chn_effect[3]        current effect (0..15)
chn_effectpar[3]     current effect parameter
chn_finalnote[3]     note after arpeggio + transpose
chn_waveform[3]      waveform from wave table or effect 9
chn_ad[3]            attack/decay
chn_sr[3]            sustain/release
chn_plswidthlo/hi[3] current pulse width (12-bit, split across 2 bytes)
chn_plsspeed[3]      pulse modulation speed
chn_plslimitdown[3]  pulse lower limit (4 MSBs = bits 11..8)
chn_plslimitup[3]    pulse upper limit (4 MSBs = bits 11..8)
chn_vibdelay[3]      vibrato delay countdown
chn_vibdepth[3]      vibrato depth (hi nybble * 16)
chn_vibspeed[3]      vibrato speed
chn_waveidx[3]       wave table index
chn_arpidx[3]        arpeggio table index
chn_notefreqlo/hi[3] target frequency (for slide-to-note)
chn_freqlo/hi[3]     frequency after arpeggio/slide
chn_finfreqlo/hi[3]  final frequency after vibrato
chn_vibpos[3]        vibrato position (0..63 counter: bits 0..3 = phase, bit4 = invert, bit5 = direction)

mod3counter          cycles 2→1→0→2: used by arpeggio effect (A)

filter_idx           filter table current index
filter_end           filter table end index
filter_loop          filter table loop index
filter_cutoff        current filter cutoff (→ $D416)
filter_input         filter resonance + voice routing (→ $D417)
filter_mode          filter mode shifted left 4 (→ $D418 | globalvolume)
```

Global variables NOT cleared on play start:
```
globalvolume   current master volume (0..15)
speed          ticks per row (default 6)
speedcounter   counts 0..speed-1
trackrow       current row in pattern (0..63)
firsttrackrow  first row (usually 0; set by pattern break)
ordernumber    current orderlist index
nextordernumber next orderlist index
forcenewpattern $80 = force new pattern (set at start, by Bxx, by Dxx)
```

---

## 12. SID Write Order (per frame, from pp_dump2sid)

For X = 2, 1, 0 (voices 3, 2, 1 in that order):
```
$D402+Y  pulse width lo
$D403+Y  pulse width hi
$D400+Y  freq lo
$D401+Y  freq hi
$D404+Y  waveform AND gate  (or $00 if waveform=$FF or muted)
$D405+Y  AD
$D406+Y  SR
```
Then global:
```
$D416    filter cutoff
$D417    filter input/resonance
$D418    globalvolume | filter_mode
```
Where Y = sidregindex[X] = {0, 7, 14} for voices 1, 2, 3.

---

## 13. Hard Restart

On new note (unless effect 3 / slide-to-note), the player looks ahead 1 row.
If the next row has a note AND the current tick satisfies:
  `speedcounter + chn_hardrestart[X] >= speed`
then AD, SR, and waveform are set to 0 (clearing the envelope and silencing the voice)
before the new note fires. Default = 2 ticks. Disabled by effect FF0.

---

## 14. Vibrato Implementation

Vibrato uses a 256-byte table (included from vibrato/vibrato.s) containing 16 ¼-sine tables
of varying depths. `chn_vibpos` is a 6-bit counter split as:
- bits 3..0: position within the quarter-sine (0..15)
- bit 4: reverse phase (EOR $0F to mirror)
- bit 5: add vs subtract (direction of the full sine)

Result: ±vibrato_table[depth*16 + phase_index] added to/subtracted from chn_freq.

---

## 15. Packed Song Binary Layout

The packed song (output of the packer) is a relocatable binary loaded by a C64 depacker.
The packer reorganizes the music data into:
```
[player code: vplayer.s compiled to target address]
[effect pointer tables: effectpointershi + effectpointerslo (32 bytes)]
[sidregindex (3 bytes)]
[freqtable lo+hi (2×97 bytes)]
[vibrato table (256 bytes)]
[player variables (zeroed at load)]
[INSTRUMENTS (column-major, all 16 fields × 32 slots)]
[WAVETABLE (256 bytes)]
[ARPEGGIOTABLE (256 bytes)]
[FILTERTABLE (256 bytes)]
[ORDERLIST (up to 256 bytes, trimmed)]
[SONGSTARTTABLE (trimmed)]
[PATTERNS (trimmed)]
[TRACKTRANSPOSES0/1/2, TRACKPOINTERSLO0/1/2, TRACKPOINTERSHI0/1/2 — decompiled from PATTERNS]
[TRACKS (only used tracks, renumbered)]
```

Note: in the packed player, the track data is accessed via pre-computed per-order pointer
tables (TRACKTRANSPOSES0-2, TRACKPOINTERSLO0-2, TRACKPOINTERSHI0-2) rather than 
dynamically computing track addresses from pattern data. This is the key structural 
difference between vplayer.s (packed) and eplayer.s (editor): the editor computes 
track pointers dynamically at pattern change.

---

## 16. Frequency Table

Generated by `freqtab/freqtab.cpp` for PAL clock = 985248 Hz, A-4 = 440 Hz.
96 notes (C-0 to B-7) + 1 padding entry (note 0 = freq 0).
Stored as freqtablelo[97] + freqtablehi[97] in the player.
B-7 on NTSC would overflow 16 bits and is clipped to $FFFF.

---

## 17. Multi-song Support

Multiple sub-songs within one file. `SONGSTARTTABLE` ($4F00) stores the starting 
orderlist index for each sub-song. Song number passed in A to player_init.
Effect Bxx (order jump) used to loop each sub-song.
Sub-song count set in the "Specials" menu.

---

## 18. Notes for USF Conversion

- **No GitHub repo found.** Source only available via CSDb + zimmers.net (both as OdinTracker113src.zip).
- **libsidplayfp / VICE / DeepSID:** none contain OdinTracker-specific player handling. 
  sidplayfp plays OdinTracker SIDs as generic PSID (the packed player is self-contained).
- **159 OdinTracker SIDs in HVSC #84** (engine='OdinTracker' in hvsc84.db).
  Primary composers: SounDemoN (50+ SIDs), Monk, Hoffmann_Michal, LordNikon, Factor6, 
  Hukka, Sidder, Swathe_Jericho, FieserWolF, Ahti.
- **Format is fully documented by the source.** No missing pieces for a decompiler.
- **Effect $Fd0 (note delay)** is TODO in the source — not implemented in any version.
  SIDs that use it will silently ignore it (the handler does `rts` immediately).
- **Arpeggio table absolute mode ($80-$FF):** bypass transpose entirely.
- **Wave table $FF:** zeroes waveform + ADSR. Creates percussive/sharp sounds.
- **Slide to note (effect 3) inhibits hard restart.** Also inhibits arpeggio table.
- **Pulse width encoding:** 12-bit value, split as (hi_byte * 256 + lo_byte) where
  both are partial — the instrument stores 8 MSBs, speed/limits are relative to hi-byte only.
  lo_byte is the fractional part accumulated by pulse speed.
