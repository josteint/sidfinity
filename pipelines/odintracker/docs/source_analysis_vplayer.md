---
source_url: local: /home/jtr/sidfinity/tmp/odintracker_research/OdinTracker113src/vplayer.s
fetched_via: local read (from OdinTracker113src.zip, CSDb #2628)
fetch_date: 2026-06-15
author: Zoltan Konyha (Zed), zed@inf.bme.hu
content_date: 2001-04-17 (v1.13)
reliability: primary (official source code)
---

# OdinTracker v1.13 — vplayer.s Deep Analysis

This is the relocatable C64 player saved with packed songs.
Full source at: /home/jtr/sidfinity/pipelines/odintracker/docs/src/vplayer.s

## Entry points (all at user-chosen relocation base)

```
$xx00  player_init    — Input A = song number; clears player state, sets up
$xx03  player_play    — Call every frame (every VBI). Processes one tick.
$xx06  player_stop    — Shut up SID ($D400..$D418 = 0).
$xx09  quickdriver    — Quick hack: play song until key pressed.
$xx20  (32 bytes)     — Song title (ASCII, 32 bytes).
```

## Player state machine — init

On `player_init`:
1. Clear all `playercleardata` area (zero all channel state).
2. Set `forcenewpattern=$80` (forces immediate pattern fetch on first tick).
3. Set `ordernumber` = `SONGSTARTTABLE[song_number]`.
4. Set `speed=6`, `speedcounter=5`.
5. Set `chn_hardrestart[0,1,2] = 2` (default 2 ticks).
6. Set `globalvolume = $0F`.
7. Then falls through to `player_stop` to reset SID.

## Player state machine — per-frame play() dispatch

Per tick (`player_play`), in order:

### 1. Mod3 counter (for arpeggio effect A)
```
dec mod3counter   ; countdown 2→1→0→2→...
```

### 2. Speed counter → new row decision
- If `speed==0`: skip to per-frame effects (speed 0 = effects-only, no new rows).
- Else: `speedcounter++`; if `speedcounter < speed` skip to per-frame section.
- On new row: `speedcounter=0`, advance `trackrow` (or load next pattern).

### 3. Pattern/orderlist advance
- `trackrow` increments each new row; at 64 → load next pattern from orderlist.
- `forcenewpattern` bit 7 set → force pattern load immediately (set by B/D effects).
- New pattern: `ordernumber = nextordernumber; nextordernumber++`.
- `firsttrackrow` (set by effect D "pattern break") used as new row start.

### 4. Fetch rows for all 3 voices
For each voice (0, 1, 2): read `(TRACKTRANSPOSESN[ordernumber], TRACKPOINTERSLON[ordernumber], TRACKPOINTERSHI N[ordernumber])` → call `fetchrow`.

### 5. Per-frame section (all ticks including non-row ticks)
For each voice X (2 → 1 → 0):
- Clear `chn_vibdepth[x] = 0`.
- If instrument set: call `process_instrument`.
- Dispatch effect handler via `effectpointerslo/hi[chn_effect[x]]`.
- After effect: load freq from `freqtablelo/hi[chn_finalnote[x]]` + `chn_slidefreqlo/hi[x]`.
- Apply vibrato: call `calcvibrato` → `chn_finfreqlo/hi[x]`.

### 6. Filter table advance
If `filter_idx != 0`: advance through filter table by index, loop at `filter_end`.

### 7. Hard-restart lookahead
Look one row ahead (into next pattern if needed): if next row has a note
(not note-off, not slide-to-note effect), clear `chn_waveform/ad/sr[x] = 0`
exactly `chn_hardrestart[x]` ticks early.

### 8. SID dump (write order per channel, x=2→1→0)
For each voice x (2, 1, 0) via `sidregindex[x]` = (14, 7, 0):
```
$D402+y = chn_plswidthlo[x]    ; pulse width low
$D403+y = chn_plswidthhi[x]    ; pulse width high
$D400+y = chn_finfreqlo[x]     ; frequency low
$D401+y = chn_finfreqhi[x]     ; frequency high
if chn_waveform[x] == $FF:     ; Note: $FF = hard restart / silence
    $D404+y = $00              ; waveform = 0
    $D405+y = $00              ; AD = 0
else:
    $D404+y = chn_waveform[x] AND chn_gateon[x]   ; waveform + gate
    $D405+y = chn_ad[x]        ; Attack/Decay
$D406+y = chn_sr[x]            ; Sustain/Release (always written)
```
Then global:
```
$D416 = filter_cutoff
$D417 = filter_input
$D418 = globalvolume | filter_mode
```

**KEY WRITE ORDER: for each voice, PW before FREQ before CONTROL/ADSR. Then filter/vol.**

## fetchrow — track row decoder

Each row is 3 bytes at `(trackptr + trackrow*3)`:

**Byte 0** = note byte:
- bit 7: high bit of effect number (contributes to 4-bit effect).
- bits 6..0: note value. 0 = no note. 97 ($61) = note-off. 1..96 = C-0..B-7.

**Byte 1**:
- bits 7..5: low 3 bits of effect number. Combined with byte0 bit7 → 4-bit effect (0x0..0xF).
- bits 4..0: instrument number (0..31). 0 = keep current instrument.

**Byte 2** = effect parameter (8 bits).

Effect number assembly: `effect = ((byte0 & $80) >> 4) | ((byte1 & $E0) >> 5)`
Wait — more precisely from the source:
```asm
lda (player_trackptr),y   ; byte 0
cmp #$80                  ; move bit7 into C
and #$7f
sta fr_nextnote+1         ; save note
iny
lda (player_trackptr),y   ; byte 1
ror                        ; C → bit7, shift right = C is now the MSB of effect
lsr
lsr
lsr
lsr
sta chn_effect,x          ; effect = (byte0.bit7 << 3) | (byte1 >> 5)  [4 bits]
```
So: **effect = (byte0 & $80) ? $08 : $00 | (byte1 >> 5)**
Range: 0..15 (4-bit effect number).

**Instrument**: `byte1 & $1F` (bits 4..0). 0 = keep old.

On new note (not 0, not 97):
- Copy AD, SR, wavetable start/arp start from instrument.
- Reset `chn_slidefreqlo/hi = 0`.
- Set `chn_gateon = $FF` (gate on).
- If effect is 3 (slide-to-note): update `chn_notefreqlo/hi` only (don't reset slide).

On note-off (97):
- Set `chn_gateon = $FE` (gate off = bit 0 = 0, rest = 1).

## process_instrument — per-tick instrument engine

Called every tick (from per-frame section) if `chn_inst[x] != 0`.

1. **Vibrato delay**: if `chn_vibdelay[x] > 0`, decrement and skip vibrato setup.
   Otherwise: read `INSTRUMENTS_VIBDEPTH_SPEED[inst]` → copy to `chn_vibdepth/speed[x]`.

2. **Pulse width modulation**:
   - If `chn_plsspeed[x] != 0`:
   - Direction `chn_plsdir[x]`: 0 = up, nonzero = down.
   - Down: subtract `chn_plsspeed[x]` from `chn_plswidthlo/hi[x]`; if < `chn_plslimitdown[x]` → reverse.
   - Up: add `chn_plsspeed[x]` to `chn_plswidthlo/hi[x]`; if >= `chn_plslimitup[x]` → reverse.
   - `plslimitdown/up` are the high bytes of the limit (bits [11:8]).

3. **Wave table**: `chn_waveform[x] = WAVETABLE[chn_waveidx[x]]`.
   Advance `chn_waveidx[x]`; if >= `INSTRUMENTS_WAVETABLEEND[inst]` → loop to `WAVETABLELOOP`.

4. **Arpeggio table** (skipped if effect 3 active):
   `delta = ARPEGGIOTABLE[chn_arpidx[x]]`.
   - If delta < $80: `finalnote = chn_note[x] + chn_transpose[x] + delta`.
   - If delta >= $80: `finalnote = (delta & $7F) + 1` (absolute, no transpose).
   Advance `chn_arpidx[x]`; if >= `INSTRUMENTS_ARPTABLEEND[inst]` → loop.

## calcvibrato

Sine-table vibrato (64-entry quarter-sine, 4 depth levels × 16 table entries = 256 B).
```
pos = chn_vibpos[x]  (0..63, wrapping)
phase bit4 → table index within quarter
phase bit5 → add or subtract
depth → selects which 16-entry block of vibrato_table
chn_finfreqlo/hi[x] = chn_freqlo/hi[x] ±vibrato_table[depth*16 + (pos & $0F)]
chn_vibpos[x] += chn_vibspeed[x]
```

## Effect reference (complete)

| Effect | Code | Parameter | Action |
|--------|------|-----------|--------|
| 0 | $00 | — | No-op |
| 1 | $01 | $00–$7F=down, $80–$FF=up | Frequency slide (accumulates in `chn_slidefreqlo/hi`) |
| 2 | $02 | 8 MSBs of PW | Set pulse width (overrides instrument PW) |
| 3 | $03 | speed | Slide to note (slide toward target `chn_notefreqlo/hi`, no hardrestart) |
| 4 | $04 | hi=depth, lo=speed | Vibrato (overrides instrument vibrato this tick) |
| 5 | $05 | speed | Set pulse sweep speed |
| 6 | $06 | hi=lower-limit bits[11:8], lo=upper-limit bits[11:8] | Set pulse limits |
| 7 | $07 | $AD | Set Attack/Decay |
| 8 | $08 | $SR | Set Sustain/Release |
| 9 | $09 | waveform | Set waveform byte (overrides wave table) |
| A | $0A | hi=note1, lo=note2 | Protracker-style arpeggio (base→+hi→+lo, 3-tick cycle via mod3counter) |
| B | $0B | order | Jump to order (order list jump, like MOD Bxx) |
| C | $0C | 8 MSBs cutoff | Set filter cutoff frequency |
| D | $0D | row (hex) | Pattern break (unlike MOD, param is hex not decimal) |
| E | $0E | hi=resonance, lo=voice-enable-mask | Filter resonance + voice routing |
| F | $0F | $00–$7F = set speed; $8x = set globalvolume; $9x = set filter mode; $Ax = fine slide down; $Bx = fine slide up; $Cx = note cut; $Dx = note delay (TODO); $Ex = select filter instrument; $Fx = set hard restart ticks | Multi-function |

### Effect F sub-commands in detail

- `$00...$7F`: Set tempo (`speed`). Speed=0: effects run, no new rows.
- `$8x` (x=0..F): Set `globalvolume = x` (0..15 → $D418 bits[3:0]).
- `$9x`: Set `filter_mode = x << 4` (written to $D418 hi nybble).
  bit0=LP, bit1=BP, bit2=HP, bit3=disconnect voice 3.
- `$Ax`: Fine slide down — subtract `x*4` from `chn_slidefreqlo/hi`, once per row (only when speedcounter==0).
- `$Bx`: Fine slide up — add `x*4` to `chn_slidefreqlo/hi`, once per row.
- `$Cx`: Note cut — at tick x within row: set `chn_gateon[x] = $FE` (release gate).
- `$Dx`: Note delay — TODO in source (not implemented in v1.13).
- `$Ex`: Select filter instrument at tick 0 only — reads filter table start/end/loop from instrument `x`, sets `filter_idx/end/loop`.
- `$Fx`: Set hard restart ticks = x for this voice.

## Wave table special value

`WAVETABLE[idx] == $FF` causes:
- `chn_waveform[x] = $FF` → triggers special branch in SID dump.
- In dump: `$D404+y = $00` (waveform=0), `$D405+y = $00` (AD=0).
- SR is still written: `$D406+y = chn_sr[x]` (current SR value).
- Effect: silences the voice (clears waveform + attack/decay) while preserving release.

## Note encoding

Notes are 7-bit values: 0=none, 1..96=C-0..B-7 (8 octaves), 97=note-off.
Frequency is looked up from `freqtablelo/hi` (256-entry PAL freq table, 2×256=512 bytes).

## Channel state layout (all 3 bytes each, indexed by voice 0/1/2)

```c
uint8  chn_hardrestart[3]  // ticks to clear before new note (default=2)
// --- cleared on init ---
uint8  chn_gateon[3]       // $FF=gate on, $FE=gate off
uint8  chn_plsdir[3]       // 0=PW up, nonzero=PW down
uint8  chn_transpose[3]    // per-order track transpose
uint8  chn_note[3]         // current note (1..96)
uint8  chn_inst[3]         // current instrument (1..31)
uint8  chn_effect[3]       // current effect (0..15)
uint8  chn_effectpar[3]    // effect parameter
uint8  chn_finalnote[3]    // note after arpeggio
uint8  chn_waveform[3]     // from wave table or effect 9
uint8  chn_ad[3]           // Attack/Decay
uint8  chn_sr[3]           // Sustain/Release
uint8  chn_plswidthlo[3]   // pulse width low byte
uint8  chn_plswidthhi[3]   // pulse width hi byte (bits 11:8)
uint8  chn_plsspeed[3]     // PW sweep speed
uint8  chn_plslimitdown[3] // PW lower limit (hi byte)
uint8  chn_plslimitup[3]   // PW upper limit (hi byte)
uint8  chn_vibdelay[3]     // vibrato delay countdown
uint8  chn_vibdepth[3]     // vibrato depth
uint8  chn_vibspeed[3]     // vibrato speed
uint8  chn_waveidx[3]      // wave table index
uint8  chn_arpidx[3]       // arpeggio table index
uint8  chn_notefreqlo[3]   // target freq lo (for slide-to-note)
uint8  chn_notefreqhi[3]   // target freq hi
uint8  chn_freqlo[3]       // freq after arpeggio + slide
uint8  chn_freqhi[3]
uint8  chn_finfreqlo[3]    // final freq after vibrato (written to SID)
uint8  chn_finfreqhi[3]
uint8  chn_vibpos[3]       // vibrato counter (0..63)
uint8  chn_slidefreqlo[3]  // accumulated slide (signed 16-bit)
uint8  chn_slidefreqhi[3]
// --- global ---
uint8  mod3counter          // cycles 2→1→0→2 (effect A arpeggio phase)
uint8  filter_idx           // current filter table index (0=no filter table)
uint8  filter_end           // filter table end index
uint8  filter_loop          // filter table loop index
uint8  filter_cutoff        // filter cutoff 8 MSBs → $D416
uint8  filter_input         // filter resonance + voice enable → $D417
uint8  filter_mode          // filter mode (written to $D418 as part of globalvolume | filter_mode)
```

## Zero-page usage

```
$FB/$FC  player_trackptr      (16-bit, destroyed by player_play)
$FD/$FE  player_patternptr / player_vibratotemp  (shared, never used simultaneously)
```

## Relocation

The player code is relocatable to any page boundary. The packer:
1. Scans all absolute addresses in player code instructions.
2. Adjusts internal addresses by `(dest_page - VPLAYER_page)`.
3. Adjusts 16 effect pointer high bytes (effectpointershi[]) by same delta.
4. Data tables (freqtable, vibrato_table) and variable region follow code unchanged.
5. 9 per-voice tables follow player: TRACKTRANSPOSES0/1/2, TRACKPOINTERSLO0/1/2, TRACKPOINTERSHI0/1/2.
6. Then 16× instrument parameter columns (instruments 1..N, no instrument 0).
7. Then wave table, arpeggio table, filter table (trimmed to used length).
8. Tracks follow (optional second file).

## Timing

Help text: "takes around $30 rasterlines." (Very slow by C64 standards.)
Player is called once per frame (VBI, 50Hz PAL). No CIA multi-speed.
All subtunes are single-speed (50Hz).

## SID write sequence summary (per frame, for USF purposes)

Per voice x=2,1,0 (reversed — voice 2 first, then 1, then 0):
1. `$D402+y` = pulse width lo
2. `$D403+y` = pulse width hi
3. `$D400+y` = frequency lo
4. `$D401+y` = frequency hi
5. `$D404+y` = waveform+gate (or 0 if waveform=$FF)
6. `$D405+y` = AD (or 0 if waveform=$FF)
7. `$D406+y` = SR

Global (once per frame, after all voices):
8. `$D416` = filter cutoff
9. `$D417` = filter input (resonance + voice routing)
10. `$D418` = globalvolume | filter_mode
