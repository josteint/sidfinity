---
provenance:
  primary_source: "local: docs/src/SRC.SDI21-N50.txt (PETSCII-decoded from sdi217_seqsrc.d64)"
  secondary_source: "local: docs/src/SRC.SDI21-SPD50.txt (speed player variant)"
  tertiary_source: "local: tmp/sidduzzit_research/SDI.2.1.6-docs.txt"
  manual_source: "local: tmp/sidduzzit_research/sdi_217_manual.txt"
  fetch_date: 2026-06-13
  authors: "Geir Tjelta & Glenn Rune Gallefoss (SHAPE)"
  content_date: "2014-05-16 (player source v2.1 n50/spd50)"
  reliability: HIGH — sourced from original Turbo Assembler player source; cross-checked
    with official docs.
---

# SID Duzz'It v2.1 — Per-Frame Write Model

## Overview

The SDI player is a frame-driven tracker.  Each call to `play` ($1003) processes one
frame for all voices.  In the normal (single-speed) player:
- `$1003` = main play call: updates tracks, sequences (note events), AND sound effects
  (waveform programs, pulse, filter, vibrato, arpeggio).
- `$1006` = fadeout call (when `rem_fad = 0`).

In the speed player (`SRC.SDI21-SPD50`):
- `$1003` = `splay` (main): updates tracks + sequences + sounds.
- `$1009` = `splay` equivalent; calling code uses the `JMP splay` at $1009.
  Wait — actually in the speed player:
  - `$1003` = `JMP play` (sound update only)
  - `$1009` = `JMP splay` (full update: calls `play` internally, then track/seq logic)

  **CORRECTION from source analysis**: In `SRC.SDI21-SPD50`, `splay` calls `jsr play`
  internally, then does the screen/tod/voices update.  So `splay` = full main call
  (what the external caller calls as $1003 or $1009), and `play` is the sound engine.

From the speed player source:
```
;$1000: jmp init
;$1003: jmp play     ← sound update only
;$1006: jmp fadeout  ← (if rem_fad=0)
;$1009: jmp splay    ← full main call (calls play internally + track/seq update)
```

And `splay`:
```
splay:
  jsr play           ; run sound update
  ; (display/tod/voices housekeeping)
```

**OPEN [WM-1]**: Confirm which entry point ($1003 vs $1009) the PSID header
`play` address points to in HVSC speed-player SDI SIDs.  This determines whether
`verify_all` uses the flat (single-entry) or per-IRQ writelog path.  Check with
`siddump --writelog-per-irq` + `--pc-trace` on a multispeed SDI SID.

**OPEN [WM-2]**: Confirm whether any HVSC SDI SIDs have the PSID `speed` bit
set (CIA-timed), which would require the per-play() writelog path.  Most tracker
SIDs are VBlank (speed=0) but SDI's multispeed mode uses raster IRQs — which are
external to the PSID wrapper.  A PSID with speed=0 but multispeed music will call
play() once per VBlank and the raster sub-calls to $1009 are player-internal.

---

## Verification Mode

SDI is a **tracker** — all music is driven by a frame counter with deterministic
per-frame writes.  This means:

**Mode 1 (frame-by-frame instruction sequence)** applies — not Mode 2 (cycle-exact).

Within each `play()` call the ORDER of writes to $D400–$D418 matters; the cycle
timestamp within the frame does NOT.

For the multispeed player: the `splay`/`play` split means the PSID `play` call
(at $1003 or the raster IRQ target) may call `play` once per VBlank, but the
sound update runs at (speed × 50 Hz) internally.  This is standard tracker
multispeed as in the Hubbard family.

**OPEN [WM-2]** (repeated): To be confirmed during migration with
`siddump --writelog-per-irq --pc-trace`.

---

## Play Loop Structure (Normal Player, Sound Engine)

Entry: `play` at $1003.

```
play:
  ldx #channels*7     ; X = 21 (3 voices) or 28 (4 voices)
  ; [optional: voice-on/off check via voff]
  ; [optional: channel 4 / conductor update (tempo/transpose/filter)]
  ; --- INNER LOOP (decrement X by 7 each pass) ---
part1:
  [gate timeout update]       ; if rem_gout=0: dec gatedec; if zero → gate off
  lda duration,x              ; load frame counter for this voice
  bpl bn33                    ; positive → still counting down, skip to part2
  [load new note from sequencer / advance sequence]
  [set note, instrument, programs]
part2:
  [pulse program update]
  [glide routine]
  [vibrato routine]
  [waveform program step]
  [sid_next: decrement X by 7, loop to part1]
  ; --- AFTER LOOP ---
  [fadeout]
  [filter routine]
  rts
```

The per-voice loop runs voices from voice 3 down to voice 1 (X=14→7→0).
Voice 4 (channel 4 / conductor) is processed at the top if `rem_4ch=0`.

---

## Per-Voice State Machine

### Duration Counter

Each voice has a two-part duration:
- `dur,x` = reload value (set when a new note event is parsed from the sequence)
- `duration,x` = countdown (decremented by the tempo countdown each frame)

The **tempo** counter (`tempo,x` at a special ZP location) is a global frame
counter decremented each play() call.  When it hits zero it reloads from the
current tempo value and decrements all per-voice `duration` counters.

From source:
```
part1:
  lda duration,x
  bpl bn33           ; still ticking → skip to part2
tempo:
  lda #0             ; [SMC: tempo value embedded here]
  beq setval         ; tempo == 0 → special case?
cur_tem:
  cmp #0             ; [SMC: current-tempo register]
  beq *+5
bn33:  jmp part2
  jmp sequ2          ; → step sequencer
```

**OPEN [WM-3]**: The exact tempo counter mechanism uses `tempo+1` (an SMC slot)
and `cur_tem+1` (another SMC slot).  Trace when `tempo+1` is decremented vs.
when `duration` is decremented.  The `cur_tem` value controls tempo subdivisions
(1=full tempo, 2=half tempo, 3=third, etc.).

### Note Event Processing

When `duration,x` expires, the sequencer steps:

1. Read next byte from sequence stream (via `(mzero),y` where mzero points to
   current sequence, y = `seqp,x`).
2. Decode FX byte + note byte (see spec_extraction_plan.md §5).
3. Set `note2,x`, `sound2,x`, `arpnum2,x`, `glidadd2,x` from decoded bytes.
4. If new instrument: reload `gatedec,x`, `detunhi,x`, `detunlo,x`, `vible,x`,
   pulse program, filter program, ADSR from instrument columns.
5. Trigger gate: `wf,x |= 1` → write `sid+4,x`.

### Gate and Hard Restart

From the source and docs (gate-timeout field `z3,y`):

```
lda z3,y           ; gate timeout byte
and #$1f           ; lower 5 bits = timeout value (frames * 2)
asl a
sta gatedec,x
```

The `gatedec,x` counter counts down from `timeout * 2` each play() call:
- While counting: no gate action.
- When reaches zero: `lda #$fe; sta gate,x` — forces gate bit off.

Then on note trigger, the new waveform byte ANDs the gate from `gate,x` before
writing to $D404.

**Hard restart variants** (docs line 449–454):
- `$01–$1F` = gate timeout + normal hard restart ($D406 briefly set to $0F)
- `$21–$3F` = gate timeout + hard restart 2
- `$41–$5F` = gate timeout + hard restart 3
- `$61–$7F` = gate timeout + hard restart 4
- `$81–$9F` = gate timeout + soft restart 1 (noted as "removed?" in docs)
- `$A1–$BF` = gate timeout + soft restart 2 (same)
- `$C1–$DF` = gate timeout + soft restart 3 (same)
- `$E1–$FF` = gate timeout + soft restart 4 / tie-like
- `$00,$20,$40,$60,$80,$A0,$C0,$E0` = no timeout (immediate gate-off at note trigger)

From source, the `gatsum = rem_gout * rem_adsr` conditional: when `rem_gout=0`,
gate timeout is active; the `gatedec` counter fires gate-off.

**OPEN [WM-4]**: The "hard restart 2/3/4" variants differ in how $D406 is
manipulated at note trigger.  Trace the `z3,y and #$1f asl` → `gatedec` →
`no_hard` / `no_rls` branches in `ack` / `track_init` to determine the exact
ADSR write sequence for each variant.  Key code path from source:
```
lda z3,y
asl a
bmi no▁rls          ; hi bit of z3 set → skip hard restart
and #$40
beq no▁hard
adc #$e0
sta sid+6,x          ; SR = $xx (brief ADSR flush)
lda #$0f
sta sid+5,x          ; AD = $0F
no▁hard  lda #$fe
sta gate,x           ; force gate off
```

---

## Per-Frame Register Write Order

On a note trigger (new instrument, gate restart), the write sequence is
approximately:

1. `$D406,x` (SR) ← `z2[inst] & $F0 | $0F` (sustain init)
2. `$D404,x` (control) ← `wf[wfp] | 1` (gate on, first waveform byte)
3. (if detuning enabled) `$D400,x` ← freq lo (note freq + detune)
4. (if detuning enabled) `$D401,x` ← freq hi
5. (if gate timeout) decrements gatedec — later triggers gate off via `$D404,x` write
6. (if pulse program) `$D402,x` / `$D403,x` ← pulse start values
7. `$D405,x` ← `z1[inst]` (AD on attack; or from seqsust on tie)
8. `$D406,x` ← SR (from `z2[inst]`)

On a tie note (no instrument restart):
- Frequency may be updated (glide or waveform note step).
- Waveform program continues stepping.
- No ADSR reinit.

**Key write order within waveform program** (from `wfrout2` / `wf_loop`):
1. Check for $FF → jump; check for $FE → delay; check for $FD → ADSR; check for
   $FB → multipulse; check for $FA → repeat; check for $F0–$F7 → $D415; then
   check for pulse commands ($EE/$ED/$EC/$EB); then check for noise trick ($E2–$E7).
2. Normal waveform byte: `sta sid+4,x` (write $D404).
3. Load note byte → compute freq → `sta sid+0,x` / `sta sid+1,x`.
4. (After loop) pulse program update → `sta sid+2,x` / `sta sid+3,x`.
5. (After loop) filter routine → `sta sid+$15` ($D415) / `sta sid+$16` ($D416) /
   `sta sid+$17` ($D417) / `sta sid+$18` ($D418, volume).

**OPEN [WM-5]**: The exact order of $D400–$D418 writes within a single `play()`
call must be confirmed by `siddump --writelog` on a real SID.  The above is derived
from source analysis but the TASS conditional assembly (`*= *-(...)`) makes it
difficult to read the absolute write order statically.  The `siddump --writelog`
flat sequence is authoritative.

---

## Waveform Program Stepping

Each play() call:
1. Load `wfp,x` (current table index).
2. Load `w[wfp]` = waveform byte.
3. If `$FF`: jump to `f[wfp]` index.
4. If `$FE`: set `wf_del,x = f[wfp]`; advance; stall next N frames.
   - `wf_del,x` is decremented each play(); when zero, wfp advances.
5. If `$FD`: ADSR command (see §ADSR command below).
6. If `$FB`: multipulse setup.
7. If `$FA`: repeat: set `wf_repet,x = f[wfp]`; advance; on reach of next $FF,
   decrement repeat counter; when exhausted, continue past the $FF.
8. If `$F0–$F7`: write low 3 bits to $D415 (filter cutoff lo).
9. If `$EE/$ED/$EC/$EB`: pulse direct commands.
10. If `$E2–$E7`: noise trick (write value to $D404).
11. Otherwise: `wf,x = byte; sta sid+4,x`.
12. Load `f[wfp]` = note byte → compute freq.
13. Advance `wfp,x` (unless `wf_del,x` nonzero after step 4).

The gate bit: `sta sid+4,x` writes `wf[wfp] AND gate,x`.  `gate,x` is normally
$FF (gate on); set to `$FE` on gate-off condition.

---

## Vibrato Routine

Entry when `vible,x != 0` (vibrato program pointer nonzero):

```
vibrato:
  ldy vible,x       ; vible = index into v[] array (= vib_ptr * 3)
  beq bn63          ; zero → no vibrato
  asl a
  adc vible,x       ; y = vible * 3
  tay
  lda vibdec,x      ; vibrato delay counter
  bne bn16          ; not zero → decrement delay, continue
  ; delay expired: load next vibrato program byte
  lda v-3,y        ; v[vible*3] = delay/command byte
  beq detun         ; $00 → detuning+continue
  cmp #$fe
  beq detun2        ; $FE → detuning+hold
  ; normal vibrato step:
  sta vibdec,x      ; reload delay counter
  lda v+1-3,y       ; v[vible*3+1] = width byte
  cmp #$80
  and #$7f
  sta vibwid,x      ; vibrato width (half)
  ror a
  sta vibdir,x      ; direction flag
  lda v+2-3,y       ; v[vible*3+2] = speed byte
bn16:
  ; if $FF → infinite loop (don't advance vible)
  ; else dec vibdec, advance vible when expired
```

The vibrato adds/subtracts a frequency offset each frame, cycling between +width
and -width at the specified speed.

"Crazy Comet" variant (`rem_cc=0`): when `v+2-3,y >= $80`, the vibrato enters
a special mode producing a "comet" pitch-sweep effect.

---

## Glide Routine

Entry when `glidadd,x != 0`:

```
glide:
  lda glidadd,x
  bmi glide_it     ; glide active
  bne *+5
  jmp vibrato      ; glidadd=0 → go to vibrato
  ; initialize glide direction
glide_it:
  ; current freq = note,x + addlo/addhi
  ; target freq = freqlo/hi[glidto,x]
  ; step += addval_l/h,x toward target
  ; when freq crosses target: snap to target, clear glidadd
  jmp wfrout       ; continue with waveform
```

Glide sets `glidadd,x` from the sequencer FX byte ($A0–$BF range): 
`glidadd2,x = (fx & $1F) << 2`.

---

## Pulse Program Routine

Entry when `pulsle,x != 0` (pulse program pointer nonzero):

```
pulse3:
  lda pulsle,x
  bmi no_pulse      ; $80+: no pulse
  bne go_pulse      ; nonzero: run pulse
no_pulse:
  jmp glide
go_pulse:
  asl a; asl a
  tay              ; y = pulsle * 4
  lda pulsdec,x
  bne bn22         ; mid-sweep: continue stepping
  ; start of new program entry:
  lda p-4,y        ; pulse lo
  sta sid+2,x
  lda p-4+1,y      ; pulse hi
  sta sid+3,x
  ; mode byte p-4+3,y → determines sweep behavior
  ; speed byte p-4+2,y → set pulsdec
```

Pulse sweep: each frame, sweep hi value by step from start toward target.
When target reached: jump or loop per mode byte.

Multipulse (`rem_mp=0`): when `pulsle2,x != 0`, alternates between two pulse
programs each `pulsdec2` frames.

---

## Filter Routine

Entry after the voice loop:

```
setfi:  lda #0      ; [SMC: filter program pointer]
        beq filtok  ; zero → skip
filtok:
  dec filtspd       ; filter speed counter (optional)
  bmi fspeed        ; → load next filter entry
  jmp filtch        ; → write current cutoff
fspeed:
  lda #0; sta filtspd  ; reload filter speed
filtle:
  lda #0            ; [SMC: filter program pointer × 4]
  asl a; bne *+5    ; nonzero → step filter
  jmp filtch        ; zero → no filter step
  tay
filtdec:
  lda #0            ; [SMC: countdown]
  bne bn38          ; not expired → update cutoff only
  ; load new filter entry:
  lda fi-4,y        ; cutoff hi
  lda fi+1-4,y      ; bne *+7 → normal sweep; zero → filter frame
  ; filter frame: use fi+2-4,y for band+res, fi+3-4,y for delay
  ; normal: sweep cutoff hi toward target with fi+2-4,y speed
```

The filter writes:
- `$D415` (cutoff lo): written by $F0–$F7 waveform command or direct
- `$D416` (cutoff hi): written by filter routine
- `$D417` (filter channel + resonance): `filtch+1 | filtena+1 | res`
- `$D418` (volume + filter mode): `vol+1 | band+1`

**$D418 write is the LAST write** in each play() call — it combines the master
volume (maintained by fadeout) and the filter mode (band/hi/lo pass).

---

## Fadeout Routine

Active when `rem_fad = 0`.  Entered via `$1006` with A = `$00–$7F` (speed).

From the `fade` label in source:
```
r▁fad4  fade  lda #0      ; [SMC: target volume, negative = fade down]
               beq nofade
               dec fadeco  ; fadeco = frame counter
               bpl nofade
               ; fadeco expired: step volume
               clc; adc #1; lsr a  ; new fadeco from speed
               sta fadeco
               [if fade down: dec vol+1; if underflow → mute all voices]
               [if fade up: inc vol+1; if max → stop fadeout]
nofade:
```

The fadeout `A` value passed to $1006 is stored as `fade+1` (SMC) and `fadeco`.
Volume is written to $D418 each play() call.

---

## $1009 Speedplay Entry (Speed Player Only)

The speed player is used for "multispeed" tunes where the sound effects run faster
than the track/sequence update.  From the docs (lines 1769–1790):

```
; Example for speed=4:
irq:  jsr $1003    ; main call — updates tracks, sequences and sounds
      jsr $1009    ; sound update call (×3)
      jsr $1009
      jsr $1009
```

But looking at the actual source more carefully:
- `$1003` in the speed player is `JMP play` — sound effects ONLY (no track step).
- `$1009` is `JMP splay` — full update (calls `play` + handles track/seq advance).

So in a speed=4 raster setup the CALLER does:
```
jsr $1009    ; splay = track+seq+sounds (the "1 main call" per VBlank)
jsr $1003    ; play = sounds only (×3 more calls for multispeed)
jsr $1003
jsr $1003
```

**OPEN [WM-6]**: Which entry ($1003 or $1009) is actually the "main" call in
the speed player?  The docs say "You will need one Main call to the player,
and the remaining calls must go to the speedplay call" and call $1003 the "main
call" and $1009 the "sound update call" — but the actual source has `splay` (the
FULL update) at `jmp splay` = $1009, and `play` (sound only) at $1003.  There
is a discrepancy between the docs example and the source structure.

Resolve with: `siddump --writelog-per-irq --pc-trace` on a known multispeed SDI
SID.  The raster structure must be inferred from the IRQ handler code in the PSID.

**Multispeed PSID speed bit**: SDI multispeed tunes use RASTER IRQs set up by
the music's own init — they are NOT CIA-timed.  The PSID header `speed` bit
should therefore be 0 (VBlank) for all SDI SIDs.

**OPEN [WM-7]**: Confirm PSID `speed` bit for all HVSC SDI SIDs by querying
`hvsc84.db`:
```python
db.execute("SELECT speed, count(*) FROM sids WHERE engine='SID_Duzz_It' GROUP BY speed")
```

---

## $D400–$D418 Register Map (Per Play Call)

Within one `play()` invocation, registers are written in approximately this order
(derived from source structure; confirm with `siddump --writelog`):

**Voice processing (per voice, inner loop)**:
| Register | Source | Condition |
|----------|--------|-----------|
| $D404+voice | wf[wfp] AND gate | Every play() (wf program step) |
| $D400+voice | freqlo[note] + detune | Every play() (after wf note decode) |
| $D401+voice | freqhi[note] + detune | Every play() |
| $D402+voice | pulse lo | When pulse program active |
| $D403+voice | pulse hi | When pulse program active |
| $D405+voice | AD from z1[inst] | On note trigger or ADSR cmd |
| $D406+voice | SR from z2[inst] | On note trigger |
| $D415 | filter cutoff lo | When $F0-$F7 wf cmd or WF pulse cmd |

**Global registers (after voice loop)**:
| Register | Source |
|----------|--------|
| $D415 | Filter cutoff lo (from filter routine, if not written in wf loop) |
| $D416 | Filter cutoff hi (filter routine) |
| $D417 | Filter channel select + resonance (`filtch | filtena | res`) |
| $D418 | Volume + filter mode (`vol+1 | band+1`) |

**OPEN [WM-5]** (repeated): Full register write ORDER is authoritative only
from `siddump --writelog`.

---

## Init Sequence ($1000, X = subtune)

From the `init` subroutine (source, end of file):

1. Clear all $D400–$D418 registers (zero fill, loop from $14 down to 0).
2. Load `c[subtune]` → `voff+1` (channel-on mask).
3. Load `s[subtune]` → `tem_prg+1` (default tempo program).
4. Set `tempo+1 = 1`, `cur_tem+1 = 1`.
5. Load `fs[subtune]` → filter speed + `filtena+1` (forced filter channels).
6. Load `fv[subtune]` → `vol+1` (initial volume), push for later.
7. Set `trk_end` byte ($60 or $E0 depending on `rem_4ch`).
8. Load `tp[subtune]` → Y (track pointer index).
9. For each active channel (X=21→7→0):
   - Clear `tdelay,x`, `dur,x`, `seqp,x`, `transp,x`, `tracky,x`.
   - Set `pulsle2,x = 0`, `srco,x = 0`, `filtre,x = 0`, `wf_repet,x = 0`.
   - Set `gate,x = $FE` (gate off).
   - Set `note2,x = $FE`, `duration,x = $FE`, `sound,x = $FE`.
   - Load `tl[y]` → `trklo,x`; `th[y]` → `trkhi,x`.
   - Call `track_init` (to prime first sequence byte).
   - Decrement Y.
10. Initialize `filtspd = 0`, `filtch+1 = 0`.
11. Write `$07` to `$D417` (filter mode, but why 7? — forces filter to ch1+2+3).
12. Pop and set `fade+1` and `fadeco` (initial volume fade from `fv[subtune]`).
13. RTS.

**Note**: Init writes `$07` to `$D417` from:
```
ldy #$07
sty sid+$15      ; = sid+$15 = $D415 ... wait, that's filter cutoff lo
```
Actually: `sid+$15` = $D415 ($D400+$15 = $D415 = filter cutoff lo).  But the
comment context suggests this is filter-related.  The `$D417` (filter ch+res) is
written separately by `filtch+1 | filtena+1 | res`.

**OPEN [WM-8]**: Confirm the init register write sequence with
`siddump --writelog` on a known SDI SID (first 20 frames, looking for the
$D400–$D418 clear + the initial register priming).  The init writes
determine the `init.sid` block in the USF.

---

## Per-Engine Config Fields (Anticipated USF Parameters)

Based on the write model, these features require parametrisation:

| Feature | USF parameter |
|---------|--------------|
| Number of subtunes | `subtune_count` (from init) |
| Default tempo per subtune | per-subtune `tempo_program` |
| Initial volume per subtune | per-subtune `init_volume` |
| Forced filter channels | per-subtune `filter_channels_mask` |
| Filter speed delay | per-subtune `filter_speed` |
| Fade-in rate | per-subtune `fadein_rate` |
| Gate timeout mode | per-instrument `gate_timeout` (z3 byte) |
| Hard restart variant | per-instrument `hard_restart_mode` |
| Assembly flags active | per-SID (detection needed) |
| Normal vs speed player | per-SID variant flag |
| Waveform delay (FE cmd) | per-wf-program |
| ADSR command (FD cmd) | per-wf-program |
| Multipulse (FB cmd) | per-wf-program |
| Waveform repeat (FA cmd) | per-wf-program |
| Pulse program type | per-instrument (sweep vs hold vs direct) |
| Filter program type | per-instrument (sweep vs frame) |
| Filter speed delay applied | per-song or global |
| Vibrato delay/detune/crazycomet | per-vibrato-program |
| Glide | per-note (from sequencer FX byte) |

---

## Leads to Follow

1. **PSID speed bit census**: Query `hvsc84.db` for `speed` field on all SDI SIDs.
   Expected: all 0 (VBlank).  Any CIA-timed SDI SIDs need the per-IRQ writelog path.

2. **Speed player identification**: Check how many HVSC SDI SIDs use the speed player
   variant (JMP at $1009).  These are multispeed tunes needing careful raster-IRQ
   handling.

3. **Assembly flag diversity**: Sample 10 HVSC SDI SIDs, disassemble $1000+, detect
   which `rem_*` flags were set.  Identify the most common flag set (the "canonical"
   variant to target first).

4. **Music data anchor**: For the canonical flag set, determine the exact offset of
   the first music data byte (i.e., where `w` starts) by disassembling the player
   and reading `lda w-1,y` absolute address.

5. **Gate-timeout variant 2/3/4**: The docs note the soft-restart variants
   ($81–$FF) may have been "removed" in v2.x.  Confirm from source: the `no_rls`
   branch skips the hard-restart write entirely when the hi bit of z3 is set.

6. **z7 band/resonance access**: The `z7,x` access (voice index) vs `z7,y`
   (instrument index) suggests band/resonance is voice-specific state, not
   per-instrument.  Verify by tracing filter routine in the source.

7. **Channel 4 format**: For SIDs with `rem_4ch=0`, decode the channel-4 sequence
   command set fully (tempo, filter, transpose, filter-force commands).

8. **$D418 write frequency**: Confirm $D418 is written EVERY play() call (it is
   the combined volume + filter-mode write at the bottom of the player).  This is
   important for the verify model.

9. **Aperiodic/non-looping tunes**: Some SDI tunes may not loop naturally.  Check
   for a "STOP" track marker in HVSC examples.  The PSID `songlength` determines
   the verify frame count.

10. **Sequence size limit**: Docs state max $7F rows, max 256 bytes per dumped
    sequence.  For extraction, this bounds the sequence decode loop.
