# Soundmonitor / MusicMaster — Per-frame SID Write Model ($D400–$D418)

> **Provenance**
> - **primary source:** `local: tmp/jc64/doc/example/SoundMonitor_shades.dis` (gzip JC64dis project file, decoded `gunzip -c`). JC64dis disassembly of "Shades (filter corrected)", Chris Hülsbeck, (c) 1986 Markt & Technik. All asm quoted below is verbatim from this file (whitespace normalised).
> - **blog (REQUESTED, UNAVAILABLE):** `https://namelessalgorithm.com/computer_music/blog/soundmonitor/` — HTTP **404** (bare path) / **403** (index) via WebFetch; web.archive.org blocked here. Write model derived from the disassembly (a primary artifact; higher reliability than a blog for register-level facts).
> - **fetched_via:** Bash `gunzip -c`/`tr`; WebSearch.
> - **fetch_date:** 2026-06-13
> - **reliability:** HIGH — every `$D4xx` store below is quoted verbatim with its source label. This is the Mode-1 instruction-stream target (CORE TENET). Cycle timing within a frame is NOT modelled (Trap B).

---

## 0 — Verification mode

Soundmonitor is **tracker music → Mode 1 (per-frame instruction sequence)**. The verdict is the ordered `(reg,val)` write sequence to `$D400-$D418` per `play()`, frame by frame (`verify_cycle.compare_instruction_stream`). Within-frame cycle positions are observation, not signal. Use the **trichotomy** comparator if our composer emits its own init (it will — see §6). **OPEN(speed):** if tempo is CIA-driven (instr `$0E → $DC05`), use the CIA per-play capture (`siddump --writelog-per-irq`) — see §5/§7.

---

## 1 — `play()` dispatch (`playSound`, verbatim)

```
playSound:
  lda  soundOn
  beq  soundToStop          ; song not active?
  jmp  playSoundOn          ; (re)start path

soundToStop:
  jsr  swapNotePointer       ; swap $A5..$AC <-> $07E9.. (double-buffer)
  lda  effectFlag
  bne  makeEffects
  lda  #$00
  sta  $D418                 ; **silence**: master volume = 0  (only when effectFlag==0)
  jmp  setBankAndExit

makeEffects:
  jsr  makePortamentoEffect  ; (A) per-frame, all voices
  jsr  makeVibratoEffect     ; (B)
  jsr  makeFilterCutEffect   ; (C)
  jsr  makeWavePulseEffect   ; (D) = PWM
  lda  actualTwoCounter
  beq  reloadCounter
  dec  actualTwoCounter      ; tempo divider not yet 0 -> EFFECTS-ONLY frame
  jmp  setBankAndExit
reloadCounter:
  lda  twoCounter
  sta  actualTwoCounter
  ... sta $01 ($36) ...
  jsr  fadeOut               ; master-volume fade (writes $D418 via processNote/outFilter)
  lda  currentIndex
  cmp  tableSize             ; end of bar?
  bcc  noIncProgrIndex
  jsr  incProgrIndex         ; advance order list, reload pointers + instrument
noIncProgrIndex:
  jmp  processNote           ; NEW NOTE COLUMN: read note for V1,V2,V3 + full out

setBankAndExit:
  ... restore $01 ... jsr swapNotePointer ; rts
```

**Two kinds of frame:**
- **Effects-only frame** (`actualTwoCounter != 0`): run (A)-(D) then exit. Writes are *only* whatever portamento/vibrato/PWM/filter emit this frame (often a handful of `$D400/01`, `$D402/03`, `$D415/16`). No ADSR/control writes.
- **Note frame** (`actualTwoCounter == 0`, reloaded): run (A)-(D), `fadeOut`, maybe advance order, then `processNote` → `outVoice1/2/3` + `outFilter` = the **full register refresh** for that column.

`twoCounter` (instr-independent global, set in `playSoundOn` to `#$02`, reloadable) = **frames-per-column = tempo**. Default `2` ⇒ new column every 2 frames (a "2x"/multispeed-ish base; the editor "SP" tempo field maps here). **OPEN(speed)** above governs whether CIA also gates `play()` rate.

---

## 2 — Per-voice register write order (`outVoice1/2/3`, verbatim)

Each voice's "out" routine flushes the 7-byte `actualVoiceN` mirror to SID. **The control register ($D404/$D40B/$D412) is written LAST**, after freq/PW/ADSR — this is the gate-edge ordering that matters for Mode 1.

### `outVoice1` (verbatim, $D4xx stores only + order)
```
lda actualVoice1   -> sta $D400   ; V1 freq lo
... (interleaved instrument reads into portLevel/relFreq/freqLevel/waveAmount state) ...
lda actualVoice1+1 -> sta $D401   ; V1 freq hi
lda actualVoice1+2 -> sta $D402   ; V1 PW lo
lda actualVoice1+3 -> sta $D403   ; V1 PW hi
lda actualVoice1+5 -> sta $D405   ; V1 attack/decay
... read portEffectV1 ...
lda actualVoice1+4 -> sta $D404   ; V1 CONTROL (gate/waveform) -- LAST
jmp outFilter
```
**V1 write order:** `$D400, $D401, $D402, $D403, $D405, $D404` (note `$D406`=SR is written at the *top of* `outVoice2`).

### `outVoice2` (verbatim)
```
lda actualVoice1+6 -> sta $D406   ; V1 sustain/release  (yes: emitted at start of outVoice2)
... instrument reads ...
lda actualVoice2   -> sta $D407   ; V2 freq lo
lda actualVoice2+1 -> sta $D408   ; V2 freq hi
lda actualVoice2+2 -> sta $D409   ; V2 PW lo
lda actualVoice2+3 -> sta $D40A   ; V2 PW hi
lda actualVoice2+5 -> sta $D40C   ; V2 attack/decay
lda actualVoice2+6 -> sta $D40D   ; V2 sustain/release
... read portEffectV2 ...
lda actualVoice2+4 -> sta $D40B   ; V2 CONTROL -- LAST
jmp outFilter
```
**V2 order:** `$D406, $D407, $D408, $D409, $D40A, $D40C, $D40D, $D40B`.

### `outVoice3` (verbatim)
```
lda actualVoice3   -> sta $D40E   ; V3 freq lo
... instrument reads ...
lda actualVoice3+1 -> sta $D40F   ; V3 freq hi
lda actualVoice3+2 -> sta $D410   ; V3 PW lo
lda actualVoice3+3 -> sta $D411   ; V3 PW hi
lda actualVoice3+5 -> sta $D413   ; V3 attack/decay
lda actualVoice3+6 -> sta $D414   ; V3 sustain/release
... read portEffectV3 ...
lda actualVoice3+4 -> sta $D412   ; V3 CONTROL -- LAST
(falls through to outFilter)
```
**V3 order:** `$D40E, $D40F, $D410, $D411, $D413, $D414, $D412`.

> The interleaved `lda ($AB),y / sta <state>` reads inside these routines write only to **page-3 state vars** (portLevel, relFreq, freqLevel, waveAmount, portEffect) — NOT to SID. They prime the per-frame effect engine for subsequent effects-only frames. They are invisible to the `$D4xx` stream but must be modelled if you re-implement the engine (the composer is free to compute these however it likes; only the `$D4xx` outputs are the target).

### `outFilter` + `setFilterVol` (verbatim)
```
outFilter:
  lda actualCutFreqLo  -> sta $D415   ; filter cutoff lo (bits 2-0)
  lda actualCutFreqHi  -> sta $D416   ; filter cutoff hi
  lda actualFilterRes  -> sta $D417   ; resonance + filter routing
  ldx actualFilterCtrlVol
  lda fadeOutSpeed
  beq setFilterVol      ; if NOT fading -> write volume now
  rts                   ; if fading -> $D418 is owned by fadeOut/processNote path
setFilterVol:
  stx $D418             ; master volume + filter mode
  rts
```
**Filter/volume order (per voice-out):** `$D415, $D416, $D417`, then `$D418` (only when `fadeOutSpeed==0`). `outFilter` is `jmp`'d to at the end of **each** of `outVoice1/2/3`, so `$D415-$D417` are re-emitted up to 3× per note frame (with the same values, since they come from per-note state) — **this repetition is part of the stream and must be reproduced.**

---

## 3 — Per-frame "out" composite for a NOTE frame

For a column where all three voices fire a fresh note, the `$D4xx` writes (in order) are approximately:

```
V1: D400 D401 D402 D403 D405 [D404]            ; (D404 control written inside processNote BEFORE outVoice1 too — see §4)
    D406                                        ; (top of outVoice2)
    D415 D416 D417 [D418]                       ; outFilter after V1
V2: D407 D408 D409 D40A D40C D40D [D40B]
    D415 D416 D417 [D418]                       ; outFilter after V2
V3: D40E D40F D410 D411 D413 D414 [D412]
    D415 D416 D417 [D418]                       ; outFilter after V3
```
Exact ordering of the `$D404/$D40B/$D412` control writes is subtle: `processNote` writes the control register **directly** (`sta $D404`) *before* calling `outVoiceN` (to set the waveform with gate off), and `outVoiceN` then re-writes it from `actualVoiceN+4` with gate **on**. See §4. **Reproduce both writes.**

---

## 4 — `processNote`: gate edges + note triggering (verbatim, V1; V2/V3 analogous)

```
processNote:
  ldy currentIndex
  lda ($A5),y            ; note byte V1
  sta actualNoteLo
  bne notZeroV1
  jmp testGateOffV1      ; $00 -> rest path

notZeroV1:
  cmp #$80
  bne limitNoteV1
  jmp processNoteV2      ; $80 -> tie/hold: emit NOTHING for V1

limitNoteV1:
  and #$7F
  ldy #$0F
  ldx specialCtrlVoice
  beq addTranspV1
  cmp #$30               ; split threshold
  bcs skipAddTranspV1
addTranspV1:
  clc
  adc transpVoice1       ; note += transpose
skipAddTranspV1:
  tax                    ; X = note index
  lda ($AB),y            ; instr $0F (portamento level lo)
  beq readNoteFreq1      ; ==0 -> no portamento: load freq into actualVoice (immediate)
  ; portamento active: load target into freqV1 (slid toward by makePortamentoEffect)
  lda frequencyHi,x -> freqV1+1
  lda frequencyLo,x -> freqV1
  lda actualNoteV1 ; cmp #$80; beq noReadNoteFreq1   ; if prev was tie, don't snap actual
readNoteFreq1:
  lda frequencyHi,x -> actualVoice1+1   ; V1 actual freq hi
  lda frequencyLo,x -> actualVoice1     ; V1 actual freq lo
noReadNoteFreq1:
  ldy #$00
  lda actualNoteLo; and #$80; bne testGateOffV1
  lda specialCtrlVoice; beq noExtraFilterTestV1
  cpx #$30; bcs extraFilterTestV1
noExtraFilterTestV1:
  lda ($AB),y           ; instr $00 = control (waveform, gate=0)
  sta $D404             ; <-- CONTROL WRITE #1 (gate OFF, sets waveform)
  lda #$00; sta allowFilterExtraTest
  lda ($AB),y; ora #$01 ; gate ON
  sta actualVoice1+4    ; staged control with gate on (emitted by outVoice1 -> $D404 #2)
readParV1:
  ldy #$1B; lda ($AB),y -> delayV1        ; instr $1B vibrato delay
  ldy #$23; lda ($AB),y -> actualVoice1+2 ; instr $23 PW lo
  iny;      lda ($AB),y -> actualVoice1+3 ; instr $24 PW hi
  lda #$01; jsr readFilterParam            ; voice-1 filter enable bit
  ldy #$29; lda ($AB),y -> waveUpCounterV1 ; instr $29
  ldy #$2C; lda ($AB),y -> waveDownCounterV1 ; instr $2C
  jsr outVoice1          ; full flush incl. CONTROL WRITE #2 (gate ON)
  jmp processNoteV2

testGateOffV1:           ; rest ($00) or high-bit note-off
  lda actualNoteV1
  beq processNoteV2      ; nothing was playing -> skip
  lda actualVoice1+4; and #$FE ; gate OFF
  sta actualVoice1+4
  jsr outVoice1          ; flush with gate cleared -> $D404 gets gate-off
  jmp processNoteV2
```

**Gate-edge model (the Mode-1-critical part):**
- **Note-on** (`$01-$7F`): `$D404` written **twice** — first the raw control byte (gate=0, selects waveform), then via `outVoice1` the same byte `OR #$01` (gate=1). Two consecutive `$D404` writes (gate low→high) = the SID "hard restart"-ish retrigger edge. **Both writes are in the stream.**
- **Tie** (`$80`): voice emits **no writes at all** (jumps straight to next voice). The note keeps sounding from prior state.
- **Rest / note-off** (`$00`, or high-bit `$8x` non-$80 in the and-#$80 path): if a note was playing, `$D404` written once with gate cleared (`AND #$FE`); else nothing.
- **specialCtrlVoice + `#$30` threshold:** when `specialCtrlVoice != 0` and `note >= $30`, take `extraFilterTestV1` — `$D404` gets `specialCtrlVoice` (a different control/waveform) and the **secondary filter param set** (instr `$33..$39`) is loaded. This is the editor's "sound transpose"/split-keyboard feature. Notes `< $30` skip the transpose add (`bcs skipAddTransp`).

V3 is identical in shape and additionally `inc currentIndex; sta actualNoteV3` at the tail (`skipReleaseV3`) — column advances once per frame, after all 3 voices.

---

## 5 — Effect → register-delta mapping (the per-frame engines)

All four run **every** `makeEffects` frame (both note and effects-only frames), each iterating voices 1/2/3 (SID index x = `$00/$07/$0E`; state index = `$00/$01/$02`).

### (A) Portamento — `makePortamentoEffect` → writes `$D400,x / $D401,x` (freq)
Gated by `portLevelLoVn != 0`. Mode from `portEffectVn` (instr `$3C..$3E`):
- `0` (glide): step `actualVoiceN` freq toward target `freqVn` by `actualPortLevel` (lo/hi) each frame; clamp/restore at target (`restoreFromFreqDn/Up`) then clear the "force delay" bit.
- `1` (down): `actualVoiceN -= actualPortLevel`, write `$D400,x/$D401,x`, force `delayVn |= $02`.
- `2` (up): symmetric add.
Per frame, emits `$D400,x` then `$D401,x` for each gliding voice. Verbatim (portDown):
```
sec; lda actualVoice1,x; sbc actualPortLevelLo; sta actualVoice1,x; sta $D400,x
     lda actualVoice1+1,x; sbc actualPortLevelHi; sta actualVoice1+1,x; sta $D401,x
```

### (B) Vibrato — `makeVibratoVoice` → writes `$D400,y / $D401,y` (freq)
Gated by `freqLevelVn != 0`. `delayVn` = onset delay (decrement; when it hits 0, two `makeRelFreqDown` calls + reset `counterVn`). Then triangle LFO: `counterVn` cycles; while ascending add `relFreqVn` (`makeRelFreqUp`), at peak (`cmp freqLevelVn / bcs setCounter`) reload counter negative, descending subtract `relFreqVn` (`makeRelFreqDown`). Each tick writes the voice freq AND mirrors into `freqVn` (so portamento target tracks). Verbatim (up):
```
clc; lda actualVoice1,y; adc relFreqV1,x; sta actualVoice1,y; sta $D400,y; sta freqV1,y
     lda actualVoice1+1,y; adc #$00; sta actualVoice1+1,y; sta freqV1+1,y; sta $D401,y
     inc counterV1,x
```
So vibrato depth = `relFreq` per tick, half-period = `freqLevel` ticks. Emits `$D400,y`+`$D401,y` per active voice per frame.

### (C) Filter EG — `makeFilterCutEffect` → writes `$D415 / $D416` (cutoff)
A two-phase up/down envelope on the cutoff. While `filterCountUpTime != 0`: `actualCutFreqLo += filterCountLevelLo` (3-bit lo with carry into hi += `filterCountLevelHi`), decrement up-time. Else while `filterCountDownTime != 0`: subtract, decrement. Each step emits:
```
lda actualCutFreqLo; sta $D415
lda actualCutFreqHi; sta $D416
```
(`$D415` masked to 3 bits via `and #$07`.) The filter is **global** (one cutoff EG shared by whichever voices have their filter-enable bit set in instr `$20`, mask {1,2,4}). Note `$D415/$D416` are emitted **both** by this effect (when active) **and** by `outFilter` during note frames → expect repeated cutoff writes; reproduce all.

### (D) PWM — `makeWavePulseEffect` → writes `$D402,y / $D403,y` (V1), `$D409/$D40A` (V2), `$D410/$D411` (V3)
Per voice, SID PW index y = `$02/$09/$10` (so `$D400+y` = the voice's PW-lo reg). Gated by `waveUpCounterVn` / `waveDownCounterVn`. Up phase: `actualVoiceN_PW += waveAmountVn`, decrement up-counter. Down phase (only when up-counter==0): subtract `waveAmount`. Verbatim (up):
```
clc; lda actualVoice1,y; adc waveAmountV1,x; sta actualVoice1,y; sta $D400,y   ; PW lo (=D402/D409/D410)
     lda actualVoice1+1,y; adc #$00; sta actualVoice1+1,y; sta $D401,y          ; PW hi (=D403/D40A/D411)
     dec waveUpCounterV1,x
```
Emits the voice's two PW registers per active voice per frame.

### Arpeggio
No dedicated per-frame arp routine in the Shades play path. Likely realised via instr `$39..$3B` ("relative low freq to add") feeding the freq path, or via rapid column advance. **OPEN(arp):** confirm by tracing an arpeggiating tune (which `$D400/01` retrigger source). Until resolved, model arp as fast freq offsets on `$D400/01`.

---

## 6 — Init / priming writes

The Shades `initSongs` is **stubbed** (`nop×11; lda #$01; sta soundOn; rts`) — no SID writes — because Shades is a relocated single-tune rip. The **canonical `$C000` init** (not present verbatim in this .dis) is expected to: zero the state page `$033C-$0379`, set `effectFlag`, load the first order entry (`playSoundOn` → `incProgrIndex` → first instrument's ADSR/filter/Timer-A), and prime pointers. The very first `play()` then emits the first full column.

For SIDfinity: the composer emits its **own** universal-reset + typed priming (init.sid block), NOT a byte-copy of the original init. Because our init length differs, **use `compare_instruction_stream(mode='trichotomy')`** — it recovers the play-stream shift, checks end-of-init chip STATE (priming) + aligned play stream.

**Priming state to capture into USF `init.sid`:** initial master volume + filter mode (`$D418` from instr `$0A`), per-voice initial ADSR (instr `$03-$08`), initial PW (instr `$23-$28`), filter cutoff/res (instr `$09`,`$0C/$0D`). **OPEN(init):** capture the canonical `$C000` init's exact first-frame writes via `siddump --writelog`.

---

## 7 — Tempo / dispatch rate

- `twoCounter` (default `$02`) = **frames per played column** (software divider in `playSound`). The editor "SP" step-param tempo maps to this and/or to per-step length.
- Instr `$0E` is stored to **`$DC05` (CIA1 Timer A hi)**. If these tunes use CIA-timed `play()` (PSID `speed` bit set), the writelog frame buckets will straddle init/play out of phase → **use `siddump --writelog-per-irq`** + the CIA per-play verdict (`writelog_per_irq_capture`), exactly as for Hubbard's Human_Race/Battle. **OPEN(speed):** census PSID `speed` bits for `engine='Soundmonitor'` to decide vblank vs CIA path before declaring a build verified.
- `fadeOut`: when `fadeOutSpeed != 0`, ramps `actualVolume` down over `actualFadeSpeed` frames; the faded volume reaches `$D418` through the `processNote`/`outFilter` path (note `outFilter` *skips* its own `$D418` write while fading, leaving volume to the fade logic). Song-end fade ⇒ `$D418` ramps to 0.

---

## 8 — Summary: registers touched, by source

| Register(s) | Written by | When |
|---|---|---|
| `$D400/$D401` (V1 freq) | `outVoice1`, portamento(A), vibrato(B) | note frame + any effect frame |
| `$D402/$D403` (V1 PW) | `outVoice1`, PWM(D) | note frame + PWM frames |
| `$D404` (V1 control) | `processNote` (gate-off byte), `outVoice1` (gate-on) | note-on writes it **twice**; note-off once |
| `$D405/$D406` (V1 AD/SR) | `outVoice1`/top of `outVoice2` | note frame |
| `$D407-$D40D` (V2) | `outVoice2`, A/B/D | as V1 |
| `$D40B` (V2 control) | `processNote`+`outVoice2` | as V1 control |
| `$D40E-$D414` (V3) | `outVoice3`, A/B/D | as V1 |
| `$D412` (V3 control) | `processNote`+`outVoice3` | as V1 control |
| `$D415/$D416` (cutoff) | `outFilter` (×3/note frame), filter EG(C) | note frame + filter-EG frames |
| `$D417` (res/routing) | `outFilter` (×3/note frame) | note frame |
| `$D418` (vol/filter mode) | `setFilterVol` (when not fading), `playSound` silence path (`#$00` when `effectFlag==0`), fade path | every frame in some form |

**Control-register double-write and the thrice-repeated `$D415-$D417` per note frame are load-bearing for the Mode-1 verdict — reproduce them exactly.**

---

## Leads to follow

- **OPEN(speed)** vblank vs CIA: census `engine='Soundmonitor'` PSID `speed` bits (`hvsc84.db`, READ-ONLY); trace one tune's `play()` cadence. Picks `writelog` vs `writelog-per-irq` verdict path.
- **OPEN(init)** capture canonical `$C000` init writes (`siddump --writelog`, first frames) for the trichotomy priming half.
- **OPEN(arp)** confirm the arpeggio data path (instr `$39..$3B`?) by tracing an arpeggiating tune's `$D400/01` retriggers.
- **Cross-check** the editor-facing field names against the namelessalgorithm blog once it can be fetched (404/403 + archive blocked from this environment); not required — the disasm is authoritative for the write stream.
- **First build target:** pick a short `init=$C000 play=$C020` tune from `hvsc84.db`, capture `siddump --writelog`, and validate this write model frame-0..N before generalising to the `+$475`/Rockmonitor variants.
