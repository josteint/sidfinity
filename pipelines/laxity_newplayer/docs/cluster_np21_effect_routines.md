<!--
source_url: https://github.com/theyamo/CheeseCutter  (GPL)
local_source: /home/jtr/sidfinity/tmp/dmc_hunt/CheeseCutter/src/c64/player_v4.acme
full_asm_copy: docs/src/player_v4_acme_full.asm
fetched_via: local read-only checkout (Read tool on pre-existing checkout)
fetch_date: 2026-06-14
author: "CCUTTER 2.x musicplayer by abad / Based on JCH NP 21.G4 by Laxity/VIB"
content_date: CheeseCutter 2.10  (player header "cc4.07", player_v4.acme comment "feb '12")
reliability: PRIMARY  (real 6502 ACME source, read verbatim from repo checkout)
prior_doc: pipelines/jch_newplayer/docs/github_cheesecutter.md
  (captured sections 1-8: entry points, orderlist, sequence alphabet, note trigger,
   setsid block, filter, .ct format, freq table — all verbatim from the same source)
gap_filled_here: full per-frame effect-command routines, hard-restart types,
   main-loop control flow detail, tsync state machine, waveform column-B semantics,
   chord engine detail, lo-fi vibrato, portamento algorithm, super-high inline cmds
-->

# NP21.G4 — Full Effect-Command & Table-Processing Routines

This document fills the gap identified in `github_cheesecutter.md` §Leads:
*"Read CheeseCutter's full play loop — the $00-$08 effect-command routines are the
NP21 write oracle."* Every section below is derived directly from `player_v4.acme`
line references.

---

## 1. `tsync` State Machine — the Heart of Note-to-SID Timing

`tsync,x` is the per-voice synchronisation counter that spreads a note trigger
across exactly **3 frames** before gate-on. It is the primary control for HR timing.

```
tsync value   meaning / action taken in updsound
-----------   -----------------------------------------------------------
$fe           idle (sync done): skip dosync entirely (bpl skips to syncskip)
$ff           new note ready: dec → $fe ... wait, actually: $ff is not used
              in the normal flow; tsync starts at $fe, is set to #2 on nextnote,
              counts down:
  2           first frame after nextnote: not tied → syncnottied → cmp #1 → no →
              goto syncgate → cmp #$ff → not $ff → syncskip (just updates wave/pulse)
  1           second frame: syncnottied → cmp #1 → YES → HR check:
                if synccnt>=2 AND inst+INS_HR bit7 set → load HR-AD/SR → set gate=$fe
              else: just gate=$fe (syncnohr path)
              then JMP dowave (no pulse/sfx this frame — only wave table!)
  0           third frame: syncnottied → cmp #1 → no; syncgate → cmp #$ff → no → syncskip
              (pulse/sfx run; wave runs; setsid writes; then postsync runs)
 $ff          gate-on frame: tsync reaches $ff via: tsync was #2 initially, but...
```

Wait — re-reading more carefully. From `nextnote` (line 448):
```asm
        lda #2
        sta tsync,x           ; set tsync=2 on new note
```

And `dosync` (line 545):
```asm
dosync  dec tsync,x           ; decrements each frame
```

So the sequence is:

| Frame | tsync before dec | after dec | tienote=0 path | Action |
|-------|-----------------|-----------|-----------------|--------|
| F0 (nextnote) | set=2 | — | — | tsync←2, durcnt←duration |
| F1 (updsound) | 2 | 1 | syncnottied: cmp #1 → YES | HR check; gate←$fe; jmp dowave |
| F2 (updsound) | 1 | 0 | syncnottied: cmp #1 → no; syncgate: cmp #$ff → no | pulse+sfx+wave run; setsid writes; postsync: dec tsync → $ff |
| F3 (updsound) | 0 → postsync made it $ff | dosync sees $ff, dec → $fe: bpl dosync ... wait |

Re-reading: `dosync` is reached only when `tsync >= 0` (bpl branch from `lda tsync,x : bpl dosync`). When tsync = $fe (negative), it skips to syncskip. When tsync = $ff after postsync sets it:

Actually postsync (line 1336) runs AFTER setsid:
```asm
postsync    dec tsync,x           ; $ff → $fe (idle again)
```

So the full tsync lifecycle:
1. `nextnote` fires: `tsync ← 2`
2. **Frame A** (tsync=2 entering updsound): `dec tsync` → 1; tienote=0: cmp #1 → YES → HR frame (gate←$fe, wave only)
3. **Frame B** (tsync=1 entering updsound): `dec tsync` → 0; cmp #1 → no; syncgate: cmp #$ff → no → `syncskip` (pulse+sfx+wave+setsid run); then postsync: `dec tsync` → $ff
4. **Frame C** (tsync=$ff entering updsound? No — $ff is negative, so `bpl dosync` skips, goes to `syncskip`): pulse+sfx+wave+setsid run; then after setsid: `cmp #$ff` → YES → `postsync`: `dec tsync` → $fe

Wait — tsync goes $ff→$fe via postsync, so:
- Frame B postsync: tsync: 0 → dec → $ff... but postsync dec tsync is AFTER setsid.

Let me be precise. tsync entering the frame:

```
Init (nextnote):     tsync ← 2
Frame 1 entry tsync=2:  dosync: dec → 1.  tienote=0: cmp #1 YES → HR frame (gate=$fe, jmp dowave, setsid, next). postsync NOT reached (tsync≠$ff after dec).
Frame 2 entry tsync=1:  dosync: dec → 0.  tienote=0: cmp #1 NO; syncgate: cmp #$ff NO → syncskip (full update). After setsid: tsync=0 ≠ $ff → skippostsync. [gate is still $fe here from FR1]
Frame 3 entry tsync=0:  dosync: dec → $ff (wraps). bpl dosync: $ff is negative → jmp syncskip (full update, pulse/sfx/wave/setsid). After setsid: tsync=$ff → postsync: dec tsync → $fe. Now gate=$ff (set in syncgateon on this frame? NO...)
```

Hmm — I'm conflating. Let me re-read syncgateon. `syncgate: cmp #$ff / beq syncgateon`. So syncgateon fires when tsync (AFTER the dec) = $ff. That is frame 3 (tsync went 0→$ff via wrap).

**Corrected timeline:**

| Frame | tsync entering dosync | after `dec tsync` | Code path | Gate action | setsid? |
|-------|-----------------------|-------------------|-----------|-------------|---------|
| F+1 | 2 | 1 | `cmp #1` YES → HR block | `gate ← $fe` | YES (via jmp dowave → setsid) |
| F+2 | 1 | 0 | `cmp #1` NO; `syncgate: cmp #$ff` NO | gate still $fe | YES (syncskip path) |
| F+3 | 0 | $ff ($ff via 0−1=wraps to $ff) | `cmp #1` NO; `syncgate: cmp #$ff` YES → syncgateon | gate ← $ff (gate ON) | YES; then postsync dec tsync→$fe |
| F+4+ | $fe | negative → `bpl dosync` branches to syncskip | full update | gate $ff | YES |

So the **3-frame restart sequence** is:
- **F+1**: HR frame — set AD/SR from HR sources, `gate ← $fe`, wave-only update, SID write
- **F+2**: intermediate — full update but gate still $fe (no HR writes; instrument not re-loaded)
- **F+3**: gate-on — instrument ADSR loaded, pulse/filter reset, waveform set, `gate ← $ff`; SID write includes gate=1 on D404

---

## 2. Hard-Restart Types (4 types from `INS_HR` byte2 top 2 bits)

From `syncnottied` (lines 551–573) + instrument descriptor at `$f000`:

```
INS_HR byte (inst byte index 2):
  bits 7-6 combined with bit 5:
    $00 ($0x, no bit7): NO hard restart at all  → synccnt still clears gate, but no ADSR change
    $40 (bit6 only):    SOFT restart — bit7=0 so syncnohr skips HR; ALSO cmp #$40 → wavenotoff
                        Effect: gate goes $fe but waveform NOT forced to HR waveform (stays current)
    $80 (bit7 set, bit5=0): NORMAL hard restart
                        AD ← cmd2[0]  (global HR-AD from command-table row 0)
                        SR ← inst+INS_7  (instrument byte 6)
    $a0 (bit7+bit5):    LAXITY hard restart
                        AD is NOT changed  (laxhr: skips the cmd2 load)
                        SR ← inst+INS_7  (same as normal)
```

### Hard-restart exact per-frame write sequence

For both `$80` and `$a0` restart types (normal vs Laxity), the difference is ONLY in
what gets loaded into `ad,x` at F+1. The SID write sequence is identical:

**F+1 (HR frame, tsync=1→0 after dec = wait, tsync=2→1):**
```
[normal $80]:  ad,x ← cmd2[0]  (HR attack/decay byte from global cmd table row 0)
               sr,x ← inst+INS_7  (HR sustain/release)
[laxity $a0]:  ad,x  UNCHANGED  (retains whatever AD was set at previous note)
               sr,x ← inst+INS_7
gate,x ← $fe
→ setsid writes: D400+o (freqlo), D401+o (freqhi), D406+o (sr=HR-SR), D405+o (ad=HR-AD or prev-AD),
                 D402+o (pulselo), D403+o (pulsehi), D404+o (waveform & $fe = gate cleared)
```

**F+2 (intermediate):** no HR-specific writes, gate still $fe. Full pulse/sfx/wave/setsid.

**F+3 (gate-on, syncgateon):**
```
ad,x ← shad,x  (instrument's actual AD)
sr,x ← shsr,x  (instrument's actual SR)
gate,x ← $ff
waveform,x ← inst+INS_4 | 1  (unless soft restart: cmp $40 → wavenotoff)
→ setsid writes: D400+o, D401+o, D406+o (instr SR), D405+o (instr AD), D402+o, D403+o,
                 D404+o (waveform | gate=1)
```

### `$40` Soft Restart (no waveform hard-set)
```
bit7=0 → syncnohr branch taken (no AD/SR HR load at all)
gate,x ← $fe   (written in syncnohr)
→ F+1: D404 gate cleared, but AD/SR not changed
F+3: gate-on: cmp #$40 → wavenotoff (SKIP waveform set — waveform stays whatever wave table had)
     gate,x ← $ff
```

### `$00` / `$0x` "3-frame restart" (no bit7)
```
bit7=0 → syncnohr taken
gate,x ← $fe   (only change)
This is described in idescr2: "$00 = 3 Frame Restart"
Wave delay from low nibble of INS_HR still applies.
No AD/SR change. No waveform force.
```

**Summary table:**

| `INS_HR` top bits | Name | F+1 AD change | F+1 SR change | F+3 waveform forced? |
|-------------------|------|---------------|---------------|----------------------|
| `$00` (bit7=0) | 3-frame restart | No | No | Yes (unless $40) |
| `$40` (bit6) | Soft restart | No | No | **No** |
| `$80` (bit7, !bit5) | Normal HR | cmd2[0] | inst byte6 | Yes |
| `$a0` (bit7+bit5) | Laxity HR | **Unchanged** | inst byte6 | Yes |

---

## 3. Main Play Loop Control Flow

```
subplay:
  if state != 0:
    ONE-TIME INIT (first call after init):
      - zero all state vars (clrfirst..clrlast)
      - synccnt[0..2] ← 2  (HR allowed from start)
      - tsync[0..2] ← $fe  (sync done — no phantom HR on first note)
      - volume ← $0f
      - filter ← 0, bandpass ← 0
      - $d417 ← $f0
      - state ← 0
      - RTS

  run:
    dec speedcnt
    if speedcnt < 0:
      [BREAKSPEED: if speed<2, read next byte from chord table as tempo]
      speedcnt ← speed  (reset tempo counter)
    
    for x = 2, 1, 0  (V3, V2, V1):
      if voicon[x] == 0: skip voice (jmp next)
      inc synccnt[x]   (frame counter for HR eligibility)
      
      if speedcnt == 0:  → updseq  (new sequence row)
      if speedcnt == 1:  → updtrack  (advance orderlist)
      else:              → updsound  (sound only)
    
    [after all 3 voices: filter block runs, then RTS]
```

### speedcnt flow and what fires per frame

The tempo (`speed` bytes) counts **down** from `speed` value to 0. When it
hits 0, a new sequence row is fetched. When it hits 1, the orderlist is
stepped. All other values: sound-only update.

For `speed=4`: row fires every 4 frames, orderlist steps at frame 3.
For `speed=1`: row fires every frame, orderlist steps every frame too (back-to-back).
For `speed=0`: BREAKSPEED path — reads tempo list from chord table.

### updseq — sequence row decode

1. `dec durcnt,x`; if ≥0, skip to updsound (still counting down current row)
2. At 0: fetch next row from the packed sequence stream
3. On each row fetch: `tsync ← 2` (arms the 3-frame restart clock)
4. Decode sequence bytes per alphabet (§3 of github_cheesecutter.md)
5. After storing shnote/shinst/shsuper:
   - `durcnt ← duration`  (reload from last `$fX` byte)
   - If `newcmdflag` set and shsuper < $40 and cmd1[shsuper] == CMD_PORTAMENTO:
     parse portamento params immediately, set `effstate ← $81`

---

## 4. Effect Command Dispatch — Full Detail

### 4a. Command routing

When `checksuper` fires (at tsync=$ff gate-on frame after setsid), if `newcmdflag[x]`:
```
shsuper[x] < $40  → iscmd: look up cmd1/cmd2/cmd3 table at row shsuper
shsuper[x] >= $40 → superparse2: inline high-range actions (see §4c)
```

### 4b. Command-table commands (`iscmd`, cmd index 0..8)

All commands in this block write to per-voice state registers (no direct SID writes here).
The SID writes happen via setsid on the *next* frame.

#### CMD $00 — Slide Up (`effstate ← 1`)
```
Parameters:  cmd2[y] → slidehi[x]
             cmd3[y] → slidelo[x]
             effstate[x] ← 1
Per-frame effect (effslideup, runs every frame until CMD_STOP):
  shfreqlo[x] += slidelo[x]   (16-bit add with carry)
  shfreqhi[x] += slidehi[x]
  → no direct SID write; shfreq feeds into freq calculation in dowave
```

#### CMD $01 — Slide Down (`effstate ← 2`)
```
Parameters:  cmd2[y] → slidehi[x]
             cmd3[y] → slidelo[x]
             effstate[x] ← 2
Per-frame effect (effslidedown):
  shfreqlo[x] -= slidelo[x]   (16-bit subtract with borrow)
  shfreqhi[x] -= slidehi[x]
```

#### CMD $02 — Hi-Fi Vibrato (`effstate ← 3`)
```
Parameters:
  cmd2[y] low nibble  → vibraflv[x]  ("feel" add per frame)
  cmd3[y] low nibble  → vibraamp[x]  (amplitude, used as right-shift count - vibracor correction)
  cmd3[y] high nibble → vibrafrq[x]  (= (cmd3>>4)+1, frequency = frames per half-period)
  vibradir[x] ← 0, vibrafl[x] ← 0, vibrafh[x] ← 0
  vibracnt[x] ← vibrafrq >> 1  (start at half period so first direction switch is centred)
  vibracor[x] += 1 if vibrafrq was odd (correction factor)

Per-frame effect (effvibrato):
  delta_lo = freqtable_lo[notereal+1] - freqtable_lo[notereal]  (semitone interval)
  delta_hi = freqtable_hi[notereal+1] - freqtable_hi[notereal]
  shift = vibracor[x] + vibraamp[x]   (total right-shift count)
  while shift > 0: delta >>= 1, shift--
  delta += {vibrafl[x], vibrafh[x]}   (add "feel" component)
  vibrafl[x] += vibraflv[x]           (ramp the feel)
  if vibradir[x] bit0 == 0: shfreq += delta
  else:                      shfreq -= delta
  vibracnt[x]++; if vibracnt[x] >= vibrafrq[x]: vibradir[x]++, vibracnt[x] ← 0
```

#### CMD $03 — Set Offset / Detune
```
Parameters:  cmd2[y] → shfreqhi[x]
             cmd3[y] → shfreqlo[x]
Immediate:   sets shfreq directly (16-bit signed offset from note's natural frequency)
No effstate change — one-shot, no per-frame loop.
```

#### CMD $04 — Set ADSR for Current Note
```
Parameters:  cmd2[y] → ad[x]    (attack/decay; writes directly, not via shadow)
             cmd3[y] → sr[x]    (sustain/release)
One-shot; no effstate change.
SID write: ad[x] → D405+o and sr[x] → D406+o on next setsid.
```

#### CMD $05 — Lo-Fi Vibrato (`effstate ← 4`)
```
Parameters:  cmd2[y] → vibrafrq[x]  (frames per half-period)
             cmd3[y] → vibraamp[x]  (amplitude, used as left-shift count)
             vibradir[x] ← 0
             vibracnt[x] ← vibrafrq >> 1

Per-frame effect (effdo3, effstate==4):
  amplitude = vibraamp[x] << 2    (left shift twice: "sta ZREG; asl ZREG; rol; asl ZREG; rol")
  → falls into vibrealadd (shared with hi-fi path):
    if vibradir[x] bit0 == 0: shfreq += amplitude
    else:                      shfreq -= amplitude
  vibracnt[x]++; if >= vibrafrq[x]: vibradir[x]++, vibracnt[x] ← 0

Key difference from hi-fi: fixed amplitude (no semitone scaling, no feel ramp).
```

#### CMD $06 — Set Waveform (DISABLED in CC default build)
```
INCLUDE_CMD_SET_WAVE = FALSE in player_v4.acme
Parameters: cmd3[y] → waveform[x]
When enabled: directly overrides waveform register shadow.
SID write: waveform[x] → D404+o via setsid.
NOTE: This command is absent from a standard CheeseCutter export.
```

#### CMD $07 — Portamento (`effstate ← $81`)
```
Parameters:  cmd2[y] low nibble → portahi[x]   (glide speed high byte)
             cmd3[y]            → portalo[x]    (glide speed low byte)
Special: parsed IMMEDIATELY at nextnote time (before updsound) when a tie note follows.

Per-frame effect (effporta, effstate==$81):
  target_freq = freqtable[notereal[x]]
  diff = {phi[x], plo[x]} - target_freq   (16-bit subtract)
  if diff >= 0 (gliding down):
    plo/phi -= porta_speed
    if plo/phi < 0: snap to target (portaset)
  else (gliding up):
    plo/phi += porta_speed
    if plo/phi >= 0: snap to target (portaset)
  shfreqlo[x] = plo[x] - freqtable_lo[notereal[x]]
  shfreqhi[x] = phi[x] - freqtable_hi[notereal[x]]

plo/phi is initialised to freqtable[previous_note] when a new (non-portamento) note plays.
```

#### CMD $08 — Stop Portamento / Slide
```
Parameters: none (cmd2/cmd3 unused)
Action: effstate[x] ← 0
Immediately halts any running slide, vibrato, or portamento.
Note: This is the only way to stop lo-fi or hi-fi vibrato as well.
```

---

## 4c. Super-High Inline Commands (sequence index $40..$ff)

These are parsed by `superparse2` at the gate-on frame (`tsync=$ff`). They are
byte-index ranges — the index value itself encodes the parameter.

| Index range | Action |
|-------------|--------|
| `$40..$5f` | Set pulse program: `(idx & $1f) * 4 → pulsenxt[x]`; `pulsecnt[x] ← 0` |
| `$60..$7f` | Set filter program: `(idx & $1f) * 4 → filtnxt`; `filtcnt ← 0` |
| `$80..$9f` | Set chord: `chordindex[idx & $1f] → chordtpos[x]` |
| `$a0..$af` | Set Attack nibble: `(idx & $0f) << 4` OR'd into `ad[x]` high nibble |
| `$b0..$bf` | Set Decay nibble: `idx & $0f` OR'd into `ad[x]` low nibble |
| `$c0..$cf` | Set Sustain nibble: `(idx & $0f) << 4` OR'd into `sr[x]` high nibble |
| `$d0..$df` | Set Release nibble: `idx & $0f` OR'd into `sr[x]` low nibble |
| `$e0..$ef` | Set master volume: `idx & $0f → volume` (→ $D418 next frame) |
| `$f0..$ff` | Set speed/tempo: low nibble=0 → `inc sync`; else → `speed ← low_nibble` |

Notes:
- `$a0..$af` / `$b0..$bf`: Set Attack/Decay WITHOUT touching SR (nibble-patching `ad[x]`).
- `$c0..$cf` / `$d0..$df`: Set Sustain/Release WITHOUT touching AD (nibble-patching `sr[x]`).
- These take effect on the current frame's `setsid` writes (they modify `ad[x]`/`sr[x]` in-place).
- `$e0..$ef` volume: affects ALL voices (global `volume` var) immediately via `$D418`.
- `$f0..$ff` speed = $0: toggles `sync` flag (used by the breakspeed mechanism).

---

## 5. Wave Table Processing — Full Detail (`dowave`)

Wave table: two parallel byte arrays `arp1[256]` (column A = transpose/loop) and
`arp2[256]` (column B = waveform/delay/loop-ptr). `wavepos[x]` is the row index.
`wavecnt[x]` counts down per frame; at 0 a new row is read. `wavetime[x]` (from
`inst+INS_HR & $0f`) = reload value.

### Column A (`arp1`) decode

```
$00..$5f   relative transpose up (added to notereal + chordvalue → freq table lookup)
$80..$df   absolute pitch: (val & $7f) → direct freq table index, ignores note/transpose
$7e        loop to previous row (stay at current wavepos, don't advance)
$7f        loop: jump — next col A byte IS the jump target row, col B byte = new wavepos
```

### Column B (`arp2`) decode

```
$00        do nothing (leave waveform unchanged); ALSO: if arp2[wavepos+1]==0 → retain wavecnt
$01..$0f   override wavecnt (wave delay) for this row — set wavecnt[x] ← this value
$10..$df   SID control register value → waveform[x]  (written to D404+o via setsid)
$e0..$ef   SID control register $00..$0f → waveform[x] & $0f  (low-SID-ctrl-range)
           (decoded as: `and #$0f → waveform,x`)
If arp2[wavepos+1] == 0 AND <$10: override wavecnt (wave delay override check in wavenotend2)
```

### Chord engine (runs inside `dowave`, after wavestore)

`chordtpos[x]` = position into `chord[]` table. `$80` = inactive.

```
ldy chordtpos,x
bmi chorddone       ; bit7 set → chord inactive
lda chord,y
cmp #$40
bcc chordnotneg
ora #$80            ; $40-$7f: sign-extend to negative arpeggio offset ($80-$bf)
chordnotneg:
sta chordvalue,x    ; = chord offset added to freq calc
inc chordtpos,x
lda chord+1,y       ; peek at next byte
bpl chorddone       ; if next byte >= 0: continue advancing
and #$7f            ; if < 0 (bit7 set): loop — target = val & $7f
sta chordtpos,x
```

Chord table entries: `$00..$3f` = positive semitone offset; `$40..$7f` = sign-extends
to negative ($40→$c0 etc.); a byte with bit7 set in the second position = loop marker,
low 7 bits = restart position.

### Final frequency computation

```
if wavetrans[x] >= $80:     (absolute mode)
    freqlo[x] = freqtable_lo[wavetrans & $7f]
    freqhi[x] = freqtable_hi[wavetrans & $7f]
else:                        (relative mode)
    idx = wavetrans[x] + notereal[x] + chordvalue[x]
    freqlo[x] = freqtable_lo[idx] + shfreqlo[x]  (16-bit add)
    freqhi[x] = freqtable_hi[idx] + shfreqhi[x]
```

`shfreqlo/hi[x]` accumulates slide/vibrato/portamento offsets.

---

## 6. Pulse Program — Complete Row Format

4 bytes per row. `pulsenxt[x]` = byte offset into `pulstab` (= row_index × 4).

```
Byte 0 (duration + direction):
  bit7 = 0: ADD mode for this row
  bit7 = 1: SUBTRACT mode
  bits 6-0: frame count for this row (= pulsecnt reload value)

Byte 1 (add value):
  Amount added/subtracted to pulselo[x] per frame (with 16-bit carry into pulsehi[x])

Byte 2 (initial PW, nibbles reversed):
  $ff = retain current PW (skip)
  else: upper nibble → pulselo[x] (D402 = PW low)
        lower nibble → pulsehi[x] (D403 = PW high)
  Example: $48 → pulselo=$40, pulsehi=$08 → D402/D403 = $0840

Byte 3 (jump):
  $00 = advance to next row (+4)
  $7f = stop program (pulsenxt ← 0, stops advancing)
  else = jump: (val << 2) → pulsenxt[x]  (direct byte offset)
```

`pulselo[x]` → D402+o, `pulsehi[x]` → D403+o in setsid every frame.

### Direct pulse (INCLUDE_DIRECT_PULSE)

When `inst+INS_PULSP` has bit7 set (value >= $80):
```
pulsehi[x] ← inst+INS_PULSP & $0f   (D403 = PW high nibble from instrument byte5 low nibble)
pulselo[x] ← 0                       (D402 = 0)
No pulse program runs (pulsenxt bypassed, pulsecnt ← 0)
```

---

## 7. Filter Program — Complete Row Format

4 bytes per row. `filtnxt` = byte offset (shared — ONE filter program for all voices).

```
Byte 0 (type/duration):
  bit7 = 0: duration — pulsecnt reload value (sweep row)
  bit7 = 1: INIT row — bits 4-6 → bandpass type OR'd into $D418:
            $90 = lowpass  ($10 → bandpass=$10)
            $a0 = bandpass ($20 → bandpass=$20)
            $b0 = both     ($30 → bandpass=$30)
            $f0 = high     ($70 → bandpass=$70)
            etc. (any bit4-6 combination)
            On INIT row: byte1 → $D417 (resonance + channel mask) immediately
            filtcnt ← 0

Byte 1 (add value / res+routing):
  On sweep row: frequency add value (10-bit, split across filtadd and filtadd+1)
    The 10-bit sweep add is encoded as: bits 1-0 → filtadd+1 (high 2 bits); rest → filtadd
    Decoding:
      filtadd+1 = (byte1 & 3) << 1
      filtadd = (byte1 >> 1) with two ROR (cmp #$80 ror ; cmp #$80 ror)
  On INIT row: written directly to $D417 (filter resonance + channel routing)

Byte 2 (initial cutoff):
  $ff = skip (retain current filter value)
  else → filter[x] ← byte2  (D416 = cutoff high); filtlo ← 0 (D415 = cutoff lo)

Byte 3 (jump):
  $00 = advance (+4)
  $7f = stop (filtnxt ← 0)
  else = jump: (val << 2) → filtnxt
```

### Filter writes per frame

On every frame (inside `maindone` filter block):
```
If new row (filtcnt reached 0):
  If INIT row: $D417 ← byte1 (res+routing)  [CONDITIONAL WRITE]
  filtcnt ← byte0 (or 0 for init row)
  filtadd computed from byte1
  If byte2 != $ff: filter ← byte2; filtlo ← 0

Sweep accumulation (every frame, new row or not):
  filtlo += filtadd+1; if carry out: wrap filtlo mod 8
  filter += filtadd + carry

Always:
  $D415 ← filtlo    (cutoff frequency low)
  $D416 ← filter    (cutoff frequency high)
  $D418 ← volume | bandpass
```

`$D417` is ONLY written on a filter INIT row, not on sweep rows.

---

## 8. Exact Per-Frame $D400-$D418 Write Order

This is the canonical sequence every play() call produces:

```
For x = 2 (V3), 1 (V2), 0 (V1):
    [voice offset o = voice[x] = {14, 7, 0}]
    
    [pulse program runs — updates pulselo[x]/pulsehi[x] in RAM only]
    [sfx effects run — updates shfreqlo[x]/shfreqhi[x] in RAM only]
    [dowave runs — computes freqlo[x]/freqhi[x], waveform[x] from wave table]
    [checksuper: runs super commands at gate-on frame — may modify ad[x]/sr[x]/volume/etc.]
    
    setsid:
      STA $D400+o  ← freqlo[x]    (frequency lo)
      STA $D401+o  ← freqhi[x]    (frequency hi)
      STA $D406+o  ← sr[x]        (sustain/release — written BEFORE AD)
      STA $D405+o  ← ad[x]        (attack/decay)
      STA $D402+o  ← pulselo[x]   (pulse width lo)
      STA $D403+o  ← pulsehi[x]   (pulse width hi)
      STA $D404+o  ← waveform[x] AND gate[x]  (ctrl+gate)
                                   gate[x] = $ff (on) or $fe (off)

After all 3 voices — filter block:
    [conditional] STA $D417       ← filttab[1] on INIT row only
    STA $D415  ← filtlo           (filter cutoff lo)
    STA $D416  ← filter           (filter cutoff hi)
    STA $D418  ← volume | bandpass
```

**Important ordering notes:**

1. D406 (SR) is written **before** D405 (AD) — reversed from naive ADSR order. This matches the SID chip's ADSR priority: SR change takes effect on the running envelope immediately; AD is latched at the next attack phase.

2. Voices are processed V3→V2→V1 (x=2,1,0), so in the write stream V3's registers appear first.

3. `$D417` is only written when a filter INIT row triggers (not every frame). No filter program running → `$D417` retains its init value ($f0 from the first play() reset).

4. On the HR frame (tsync=2→1): setsid runs but the path is `jmp dowave` (bypasses pulse/sfx). Only D400-D404 for that voice change. Gate is $fe.

5. On the gate-on frame (tsync=0→$ff): checksuper runs AFTER setsid but in the same frame (postsync path). Super commands that set $a0-$af ADSR nibbles take effect in the current setsid because they modify `ad[x]`/`sr[x]` before the setsid call.

---

## 9. State Variables Reference

Complete listing of per-voice (indexed by x={0,1,2}) and global state, in memory order (`clrfirst`..`clrlast`):

| Variable | Per-voice | Function |
|----------|-----------|----------|
| `newinsflag` | yes | instrument changed this row |
| `newcmdflag` | yes | command pending |
| `hardon` | yes | 1 = new gate-on this frame (skip wave table) |
| `duration` | yes | current row duration (frames) |
| `durcnt` | yes | countdown to next row |
| `tsync` | yes | 3-frame sync machine ($fe=idle, 2→1→$ff→$fe) |
| `synccnt` | yes | frames since last note (HR guard; must be ≥2) |
| `tienote` | yes | tie flag (skip gate-on) |
| `notereal` | yes | transposed note value → freq table index |
| `effstate` | yes | 0=none,1=slup,2=sldown,3=hifi,4=lofi,$81=porta |
| `shtrans` | yes | shadow transpose (from orderlist) |
| `shnote` | yes | shadow note (from sequence) |
| `shinst` | yes | shadow instrument number |
| `shsuper` | yes | shadow super/command index |
| `shad` | yes | shadow AD (from instrument at gate-on) |
| `shsr` | yes | shadow SR |
| `shfreqlo/hi` | yes | frequency offset accumulator (slide/vib/porta) |
| `freqlo/hi` | yes | final computed frequency → D400/D401 |
| `trans` | yes | current active transpose |
| `gate` | yes | gate mask: $ff=on, $fe=off |
| `curseq` | yes | current sequence number |
| `seqcnt` | yes | position in packed sequence stream |
| `bandpass` | global | filter type bits OR'd into $D418 |
| `filter` | global | filter cutoff high → $D416 |
| `filtcnt` | global | filter row countdown |
| `filtcur` | global | current filter table row offset |
| `filtnxt` | global | next filter table row offset |
| `filtadd` | global | sweep add value (2 bytes, 10-bit) |
| `filtlo` | global | filter cutoff low → $D415 |
| `vibracnt` | yes | vibrato period counter |
| `vibradir` | yes | vibrato direction (bit0: 0=up,1=down) |
| `vibraamp` | yes | vibrato amplitude (right-shift count for hi-fi; left-shift ×4 for lo-fi) |
| `vibrafrq` | yes | vibrato half-period (frames) |
| `vibracor` | yes | hi-fi amplitude correction (1 if vibrafrq was odd) |
| `vibrafl/fh` | yes | hi-fi "feel" accumulator (16-bit) |
| `vibraflv` | yes | hi-fi "feel" add per frame |
| `slidelo/hi` | yes | slide speed (16-bit) |
| `pulsecur` | yes | current pulse table byte offset (for this frame's read) |
| `pulsenxt` | yes | next pulse table row offset |
| `pulsecnt` | yes | pulse row frame countdown |
| `pulselo/hi` | yes | pulse width → D402/D403 |
| `ad` | yes | attack/decay → D405 |
| `sr` | yes | sustain/release → D406 |
| `waveform` | yes | SID ctrl reg → D404 (ANDed with gate) |
| `wavetrans` | yes | arp1[] value for this wave step (transpose/loop) |
| `wavecnt` | yes | wave row countdown |
| `wavepos` | yes | index into arp1[]/arp2[] |
| `wavetime` | yes | wave row duration (from INS_HR low nibble) |
| `chordtpos` | yes | chord table position ($80 = inactive) |
| `chordvalue` | yes | current chord transpose offset |
| `portahi/lo` | yes | portamento speed |
| `plo/phi` | yes | portamento running frequency accumulator |

---

## 10. Breakspeed / Variable Tempo

When `speed < 2`, the player reads tempo from the **chord table** as a tempo program:

```
speedalt:
  ldy speedsub
  lda chord,y       ; read byte from chord table at position speedsub
  bpl nowrap
  ldy #0            ; bit7 set = loop: restart at position 0
  sty speedsub
  lda chord,y
nowrap:
  inc speedsub      ; advance to next chord-table byte next time
  [use this as the speed value, fall into speedok]
```

This allows per-song variable tempo sequences stored inside the chord table.
An `$f0` super-command with low nibble 0 toggles `sync` instead of setting speed.
`SF2's JCH converter rebuilds this as a dedicated Tempo table (see github_sidfactory2.md §Tempo).`

---

## 11. Init Sequence — First play() Call

The one-shot init block in `subplay` (when `state != 0`):

```
SID state after first play():
  $D417 ← $f0        (filter off, no routing)
  $D418 ← $0f        (volume=15, no filter)
  [all voice D400-D406 written via setsid: freqlo/hi=0, sr=0, ad=0, pw=0, ctrl=0]
  filter = bandpass = 0
  synccnt[0..2] = 2   (HR allowed immediately)
  tsync[0..2] = $fe   (idle — no phantom note)
  volume = $0f
```

Note: the SID writes for D400-D406 happen when the main loop runs after init for all
3 voices (since all state vars cleared to 0, the first setsid writes all-zero). The
explicit init is only `$D417 ← $f0` plus the volume write.

---

## 12. PSID `speed` / CIA Timer Notes

CC exports use multispeed if `MULTIPLIER > 1`. The CIA value `$4cc7` sets the CIA A timer.
`mplay` = `jmp submplay` = `lda #$40 : sta state` then runs updsound for all 3 voices
(bit6 path — skips sequence/track advance). This is the multispeed "extra tick" per VBI.

For standard (1×) CC exports: PSID `speed = 0` (VBI), single `play()` per frame.
The `sync` flag (toggled by `$f0` speed command) is used by the editor for sync effects;
not relevant to the SID write oracle.

---

## Leads to Follow

1. **NP20.G4 vs NP21.G4 register stride difference**: NP20 uses 32 instruments (stride 32,
   base $1CCB fixed); NP21/CC uses 48 (stride 48, relocatable). The 8 instrument fields
   are identical. Any HVSC NP20 extractor must probe stride before extracting.

2. **CMD_SET_WAVE ($06) is disabled in CC default build** (`INCLUDE_CMD_SET_WAVE=FALSE`).
   Classic HVSC JCH NP20/21 tunes may or may not use it depending on the player variant.
   Check per-fingerprint whether the command-6 slot is included.

3. **`cmd2[row 0]` as global HR-AD**: the command table row 0 is reserved as the global
   hard-restart AD value. Any extractor must read `cmd2[0]` and route it to `EngineConfig`
   rather than treating it as a normal command.

4. **Direct pulse encoding** (inst byte5 >= $80): nibble-reversed (`$80+lo_nib` → pulsehi).
   The extractor must distinguish pulse-table-pointer (byte5 < $80) from direct-PW (byte5 >= $80).

5. **Portamento immediate-parse**: CMD_PORTAMENTO ($07) is parsed at `nextnote` time, not at
   `checksuper` time. This means portamento can start BEFORE the gate-on frame. Any
   extractor/composer for NP21 must model this early-parse semantics.

6. **10-bit filter sweeps**: the filtadd encoding is non-obvious (split across two bytes via
   two ROR-with-carry operations). Verify against a known filter-sweep tune before coding
   the extractor.

7. **Chord table dual use**: the chord table is ALSO used as a tempo program when `speed < 2`.
   An extractor must determine which voice/position ranges are tempo data vs. chord data.
   SF2's JCH converter separates these into Tempo and Chord tables; see github_sidfactory2.md.

8. **`wdescr1` $01-$0f wave-delay-override vs waveform**: wave column B `$01..$0f` overrides
   the wave step delay (wavecnt), NOT the waveform register. This is easy to misread.
   `$10..$df` = SID ctrl value; `$e0..$ef` = SID ctrl $00..$0f.

9. **Filter init row vs sweep row**: `$D417` is only written on an INIT row (byte0 bit7 set).
   On sweep rows `$D417` is never touched. Confirm this matches the write-log when modeling
   filter programs.

10. **`tools/ct2util.d` + `src/ct/build.d`/`purge.d`** (not yet read): hold the .ct→.sid
    export packer and table-purge logic. Mine for the exact exported memory layout and
    which tables get stripped on export. These are in the CheeseCutter repo at
    `src/ct/build.d`, `src/ct/purge.d`.
