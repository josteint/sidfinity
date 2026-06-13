<!--
provenance:
  doc: JCH NewPlayer — per-frame $D400-$D418 write model (Mode-1 verdict target)
  sources:
    - local: tmp/jch/player_v4.acme   (CheeseCutter player source, 1763 lines)
      source_url: https://raw.githubusercontent.com/theyamo/CheeseCutter/master/src/c64/player_v4.acme
      fetched_via: curl (raw.githubusercontent.com)
      fetch_date: 2026-06-13
      author: abad (Aleksi Eeben), "Based on JCH NP 21.G4 by Laxity/VIB"
      content_date: header "cc4.07"
      reliability: HIGH — the actual per-frame SID-write routine (`setsid`), gate /
                   hard-restart sequence, and per-effect register math are read
                   VERBATIM here. The WRITE ORDER and the gate/HR logic are believed
                   identical between NP20.G4 and NP21 (same engine lineage); the
                   DATA ENCODING differs (see spec_extraction_plan.md §0).
    - local: hvsc84/MUSICIANS/O/Odkin/Wild.sid (packed NP20.G4 ground-truth binary)
      fetched_via: direct binary read (read-only); fetch_date 2026-06-13
      reliability: HIGH for instrument/table bytes; the actual write stream must be
                   confirmed with `tools/siddump --writelog` (NOT yet run here).
    - local: hvsc84.db (read-only) + PSID 'speed' field — CIA vs vblank census.
  STATUS: write order + per-effect math = source-confirmed. Frame-exact HR timing
          (how many frames gate-off precedes gate-on) is DERIVED from the source
          counters and marked OPEN-W1 pending a `--writelog` capture.
-->

# JCH NewPlayer — Per-frame $D400-$D418 Write Model

This is the Mode-1 verification target: each `play()` ($1003) call emits an ordered
sequence of `$D400-$D418` writes; the rebuild matches iff that per-`play()` sequence
matches the HVSC original frame-by-frame (within-frame ORDER matters; cycle
timestamps do not). See CLAUDE.md "Mode 1".

All asm line numbers below reference `tmp/jch/player_v4.acme`.

---

## 1. The per-voice write set + ORDER (`setsid`, lines 1308-1323)

For each voice (processed voice 2 → 1 → 0; the main loop runs `ldx #2 … dex …
bmi`, lines 380-381 / `next` 1372-1373), the engine writes EXACTLY these registers
in EXACTLY this order:

```asm
setsid      ldy voice,x          ; voice,x = 0 / 7 / 14  (voice base offset)
            lda freqlo,x
            sta $d400,y          ; 1. FREQ LO
            lda freqhi,x
            sta $d401,y          ; 2. FREQ HI
            lda sr,x
            sta $d406,y          ; 3. SUSTAIN/RELEASE   (SR BEFORE AD)
            lda ad,x
            sta $d405,y          ; 4. ATTACK/DECAY
            lda pulselo,x
            sta $d402,y          ; 5. PULSE WIDTH LO
            lda pulsehi,x
            sta $d403,y          ; 6. PULSE WIDTH HI
            lda waveform,x
            and gate,x           ; gate ANDed into waveform (gate byte $fe or $ff)
            sta $d404,y          ; 7. CONTROL REG (waveform | gate-bit)
```

Per-voice write order (the invariant the verdict checks):
**$D400, $D401, $D406, $D405, $D402, $D403, $D404.**

Notes:
- `voice,x` = `0, 7, 14` (line 1550 `voice !8 0,7,14`) → `$d400,y` resolves to the
  per-voice register block ($D400 / $D407 / $D40E).
- **$D404 (control) is written EXACTLY ONCE per voice per frame** — there is no
  separate gate-edge write; the gate bit is folded in via `and gate,x`. `gate,x` =
  `$FE` (gate-off mask: clears bit0) or `$FF` (gate-on mask: keeps bit0). The
  waveform byte itself carries the gate bit ($x1) when noted (e.g. arp2 `$41` =
  pulse+gate). So gate transitions appear as the bit0 of the $D404 value changing
  between frames, NOT as extra writes. (Contrast Hubbard engines that emit explicit
  gate-clear writes — JCH does NOT.)
- AD/SR (`$D405/$D406`) are written every frame from the per-voice shadow `ad,x`/
  `sr,x` — so an ADSR change (from a super command or hard restart) is visible the
  frame it is applied.

### Global writes (end of `play()`, after all 3 voices)

Filter + master volume, written ONCE per frame (NOT per voice), lines 1467-1476:
```asm
            lda filtlo
            sta $d415            ; FILTER CUTOFF LO  (only if INCLUDE_FILTER)
            lda filter
            sta $d416            ; FILTER CUTOFF HI
            lda volume
            ora bandpass         ; bandpass/routing high bits
            sta $d418            ; MASTER VOL / FILTER MODE
```
And on a filter INIT row (bit7 of filttab byte0), additionally:
```asm
            lda filttab+1,y
            sta $d417            ; FILTER RES + VOICE ROUTING  (init row only)
```
`$D417` is written ONLY when a filter program starts an init row (lines 1415-1416),
NOT every frame.

> **Global write order at end of frame: $D415, $D416, [$D417 on init], $D418.**
> The filter cutoff ($D415/$D416) is written every frame even when no filter program
> runs (it stores the current `filtlo`/`filter`, which stay 0 if unused → benign
> $D415=$00 $D416=$00 writes). **OPEN-W2:** confirm the packed NP20.G4 also emits
> $D415/$D416 unconditionally every frame (CheeseCutter does iff INCLUDE_FILTER;
> a packed tune with the filter feature stripped may omit them). Confirm with
> `--writelog` on a no-filter tune.

### Init ($1000 → subinit) writes
On the FIRST `play()` after init (`state != 0` path, lines 324-357):
```asm
            lda #$0f / sta volume          ; volume default $0F
            lda #0   / sta filter / sta bandpass
            lda #$f0 / sta $d417           ; $D417 = $F0 (resonance high, no routing)
```
So the init/priming chip state is: master vol $0F, filter cutoff/mode cleared,
$D417=$F0. There is a universal SID reset before this (PSID convention / player).
This maps to the USF `init.sid` block: `master_vol=$0F`, filter off,
per-voice envelope/PW primed by the first note's instrument. (Per the
init-trichotomy: reset = universal, priming = these typed values, environment =
top-level USF, bookkeeping = out of USF.)

---

## 2. Where each written value comes from (per-voice signal chain)

Per frame, before `setsid`, the engine computes the shadow registers:

| reg written | source var | computed by |
|-------------|-----------|-------------|
| $D400/$D401 | `freqlo,x`/`freqhi,x` | wave-table step (`waveprocess`, 1003-1024): freqtable[note+transpose+arp(+chord)] + shfreq accumulator; OR absolute freqtable[A&$7F] |
| $D405 (AD)  | `ad,x` | instrument byte0 on note-on; overwritten by HR (`cmd2`), Set-ADSR cmd ($4), or att/dec super ($Ax/$Bx) |
| $D406 (SR)  | `sr,x` | instrument byte1 on note-on; overwritten by HR (`inst+INS_7` = byte6), Set-ADSR, or sus/rel super ($Cx/$Dx) |
| $D402/$D403 | `pulselo,x`/`pulsehi,x` | pulse-table step (`updatepulse`, 690-746); reversed-nibble init; per-frame add/sub |
| $D404 (ctrl)| `waveform,x` & `gate,x` | wave-table col B (waveform) or HR waveform (byte3); gate from sync state |
| $D415/$D416 | `filtlo`/`filter` | filter-table step (global) |
| $D417       | filttab+1 | filter init row (global) |
| $D418       | `volume \| bandpass` | volume default $0F, set by $Ex super / $Fx-vol; bandpass from filter routing |

`freqlo/freqhi` are recomputed EVERY frame from the wave table even on held notes —
this is how arpeggios + vibrato + slide manifest as per-frame $D400/$D401 deltas.

---

## 3. Gate + hard-restart sequence (the 4 HR types)

The note lifecycle uses `tsync,x` (a down-counter set to a small value at note
trigger) and `synccnt,x` (frames-since-note, for HR eligibility). The whole dance
is in `updsound`/`dosync`/`syncnottied`/`syncgateon` (lines 539-684).

### Trigger setup (when a new note row is read, `nextnote`, line 448)
```asm
            lda #2
            sta tsync,x          ; tsync = 2  → 2-frame restart window
```
`synccnt,x` is INCremented each frame the track is on (line 384 `inc synccnt,x`),
and RESET to 0 on gate-on (line 679-680). HR is allowed only when `synccnt >= 2`
(line 555-557: `lda synccnt,x / cmp #2 / bmi syncnohr`) — i.e. the previous note
must have sustained ≥2 frames before a hard restart can fire.

### The countdown (each frame while tsync >= 0, `dosync`, lines 545-577)
```asm
dosync      dec tsync,x          ; tsync: 2 → 1 → 0(=$ff after) ...
            lda tienote,x
            bne ... (skip; tie note → no restart)
syncnottied lda tsync,x
            cmp #1
            bne syncgate         ; tsync != 1 → check gate-on path
            ; ---- tsync == 1 frame: the RESTART frame ----
            lda synccnt,x / cmp #2 / bmi syncnohr     ; HR eligible?
            ldy shinst,x / lda inst+INS_HR,y          ; instrument byte2
            bpl syncnohr                              ; bit7 clear ($0x/$4x) → no ADSR HR
            and #$20 / bne laxhr                      ; bit5 set ($Ax) → Laxity
            lda cmd2 / sta ad,x                       ; $8x HARD: AD ← global HR-AD
laxhr       lda inst+INS_7,y / sta sr,x               ; $8x & $Ax: SR ← instr byte6
syncnohr    lda #$fe / sta gate,x                     ; GATE OFF (mask $fe)
            jmp dowave                                ; only wave-table updates this frame
syncgate    cmp #$ff
            beq syncgateon       ; tsync wrapped to $ff (== "0 then dec") → GATE ON frame
```

### Gate-on frame (`syncgateon`, lines 579-677)
```asm
syncgateon  ... load instrument ADSR into shad/shsr ...
            ... set freq from note (unless porta) ...
            ... set wavepos = inst byte7, ad/sr, pulse, filter ...
            lda inst+INS_HR,y / and #$c0 / cmp #$40 / beq wavenotoff  ; $4x SOFT → skip wave-force
            lda inst+INS_4,y / ora #1 / sta waveform,x / inc hardon,x ; force HR waveform (byte3 | gate)
wavenotoff  lda #$ff / sta gate,x                      ; GATE ON (mask $ff)
            lda #$00 / sta synccnt,x                   ; reset synccnt
```

### The four HR types — per-frame register effect

Let frame T = the note's "restart" frame (tsync==1), frame T+1 = gate-on frame.

| byte2 hi-nibble | type | frame T (tsync==1) | frame T+1 (gate-on) |
|-----------------|------|--------------------|---------------------|
| `$0x` (bit7=0, bits7-6=00) | **3-frame** | $D404 gate bit → 0 (mask $fe); AD/SR unchanged | gate→1; waveform forced from byte3; AD←instr0, SR←instr1 |
| `$4x` (bits7-6=01) | **Soft** | gate→0; AD/SR unchanged | gate→1; **waveform NOT forced** (keeps prior); AD←instr0, SR←instr1 |
| `$8x` (bits7-6=10) | **Hard** | gate→0; **AD←cmd2 (global HR-AD)**, **SR←instr byte6** | gate→1; waveform forced from byte3; AD←instr0, SR←instr1 |
| `$Ax` (bits7-6=11) | **Laxity** | gate→0; **AD untouched**, **SR←instr byte6** | gate→1; waveform forced from byte3; AD←instr0, SR←instr1 |

> So at the $D405/$D406 register level:
> - `$8x` produces a **two-step ADSR write**: frame T sets AD=`cmd2` (e.g. $0F) +
>   SR=byte6 (typically a fast-release like $00 or $F0) to FLUSH the envelope, then
>   frame T+1 restores the instrument's real AD/SR. This is the audible "hard
>   restart click suppression".
> - `$Ax` (Laxity) writes only SR=byte6 at frame T, leaving AD from the prior note —
>   a softer restart.
> - `$0x`/`$4x` write no ADSR change at frame T; the envelope is re-gated only.
> - The DIFFERENCE between `$0x` and `$4x` is at frame T+1: soft ($4x) does NOT
>   re-force the waveform from byte3 (it keeps whatever the wave table produced),
>   while 3-frame ($0x) forces byte3.

> **OPEN-W1 (frame count).** `tsync` is initialised to `2` (line 448). The sequence
> is: trigger frame (tsync 2→1, the `dosync` runs AFTER `dec`, so first processed
> value is 1 = RESTART frame), then next frame tsync 1→0→processed-as-`$ff` =
> GATE-ON frame. So the model is a **2-frame restart**: 1 frame gate-off, then gate
> on. The codebase64/research note "$0x = Gate off 3 frames before, waveform clear 1
> frame before" describes a DIFFERENT (older NP) HR timing with a 3-frame window.
> **The packed NP20.G4 timing must be confirmed by `--writelog`:** capture the
> $D404 gate-bit transitions across a note-on on a real tune and count the gate-off
> frames. CheeseCutter source = 2-frame; NP20.G4 may be 2 or 3. THIS IS THE #1
> write-model unknown. Close with:
> `tools/siddump --writelog Wild.sid` → grep $D404 transitions around a note start;
> cross-check `tools/voice_writelog.py --voice 1`.

> **Reconciliation with `sibling: forum_hard_restart_and_write_model.md`.** The
> sibling doc (Cadaver / SF2) describes the GENERAL C64 idiom of writing
> `$D404 = $09` (testbit+gate) on the first note frame. **This specific player does
> NOT emit a `$09` testbit write** -- verbatim `setsid` (lines 1321-1323) writes
> `waveform AND gate` only, and the gate-on frame forces `inst+INS_4 | 1` (byte3
> HR-waveform OR gate), not `$09`. So JCH NewPlayer's HR is a gate-off then
> gate-on-with-real-waveform sequence, NOT the testbit idiom. The two docs agree on
> the ADSR-before-waveform write ORDER and the ~2-frame gate-off window; they differ
> only on the testbit, and the source settles it (no `$09`). The sibling's own
> Section 7 flags this open for "the classic NP20 player specifically" -- resolved
> here for the NP21/CheeseCutter code path; confirm NP20.G4 with `--writelog` (the
> OPEN-W1 capture also answers whether NP20.G4 inserts a testbit).

---

## 4. Super-table command + table-step → register deltas

Each maps to per-frame writes already covered by §1's register set; the command
just changes the SOURCE variable. Summary (CheeseCutter semantics, see
spec_extraction_plan.md §8 for full decode):

| command / step | per-frame register effect |
|----------------|---------------------------|
| Slide up/down (cmd 0/1) | `shfreq` += / −= 16-bit rate each frame → $D400/$D401 drift |
| Vibrato (cmd 2, lo-fi cmd 5) | `shfreq` oscillates → $D400/$D401 wobble |
| Detune / Set-offset (cmd 3) | `shfreq` = fixed offset → $D400/$D401 bias |
| Set ADSR (cmd 4) | `ad`/`sr` set → next-frame $D405/$D406 |
| Portamento (cmd 7) | `shfreq` glides note→note → $D400/$D401 ramp; runs until cmd 8 |
| Stop (cmd 8) | clears effstate → freq settles |
| Set pulse ($40-$5F) | re-points pulse program → $D402/$D403 sweep restarts |
| Set filter ($60-$7F) | re-points filter program → $D415/$D416 (+$D417 on init) |
| Set chord ($80-$9F) | arpeggio table index → $D400/$D401 per-frame note cycling |
| Set Att/Dec/Sus/Rel ($A0-$DF) | partial $D405/$D406 nibble update |
| Set Volume ($E0-$EF) | $D418 lo nibble |
| Set Speed ($F0-$FF) | song tempo (frames per row); $F0 = sync toggle |
| Wave-table step (every frame) | $D400/$D401 (transpose/abs) + $D404 (waveform col B) |
| Pulse-table step (every frame) | $D402/$D403 |
| Filter-table step (every frame) | $D415/$D416 (+$D417 init) + $D418 (bandpass bits) |

None introduces a register write OUTSIDE the §1 set or order — they only feed the
shadow vars that §1 then writes in the fixed per-voice / global order.

---

## 5. The frame skeleton (what the verdict sees per `play()`)

```
play():
  (advance song speed counter; maybe advance order list + sequences this frame)
  for x in [2, 1, 0]:                 ; voice 2, then 1, then 0
     updsound:  sync/HR/gate decisions → set ad,sr,gate,waveform,wavepos
     updatepulse: step pulse → pulselo,pulsehi
     effects: slide/vibrato/porta → shfreq
     dowave:   step wave table → freqlo,freqhi
     checksuper: parse pending super command → effstate / pulse / filter / adsr / vol
     setsid:   WRITE $D400,$D401,$D406,$D405,$D402,$D403,$D404   (for this voice)
  filter routine (global): step filter → WRITE $D415,$D416,[$D417]
  WRITE $D418  (volume | bandpass)
  rts
```

So a single `play()` emits, in order:
`[V2: D400 D401 D406 D405 D402 D403 D404] [V1: …] [V0: …] D415 D416 [D417] D418`.
That ordered tuple is the per-frame instruction sequence the Mode-1 comparator
(`compare_instruction_stream`) checks. **OPEN-W3:** confirm the voice processing
order is 2→1→0 (so writes are V2,V1,V0) in the PACKED NP20.G4 — the CheeseCutter
`main0` loops `ldx #2 … dex`, but a packed variant could differ. Confirm with
`--writelog` ($D40E/$D407/$D400 ordering within a frame).

---

## 6. Mode-1 verdict + multispeed (Q-series) handling

- **Mode-1 applies** (per-frame instruction-sequence exact) for the standard
  vblank (50Hz) tunes — the overwhelming majority. PSID `speed` field = 0.
  HVSC census (sampled 200 JCH tunes): **196 vblank (speed=0), 4 CIA (speed!=0).**
  So ~98% take the plain flat-prefix `compare_instruction_stream` path.
- **Multispeed Q-series** (`G` = vblank 50Hz; `Q` = multispeed/CIA-timed): the
  player has `MULTISPEED=TRUE`, an `mplay`/`submplay` entry (lines 258-260, 316-319)
  that does SOUND WORK ONLY (`state=$40`, jumps to `syncskip` — no sequence advance),
  and a CIA timer setup (`cinit`, `CIA_VALUE=$4cc7`, lines 1487-1495). These tunes
  set the PSID `speed` bit and fire `play()` more than once per frame. **The flat
  per-50Hz-frame capture buckets init + plays out of phase (Trap C / CIA case)** —
  so for `speed != 0` JCH subtunes the verdict MUST use
  `tools/siddump --writelog-per-irq` (`writelog_per_irq_capture`, init prefix
  dropped), flat-comparing the per-`play()` stream — exactly as `verify_all` already
  does for Hubbard Human_Race / Battle CIA tunes (see
  `project_hubbard_remaining_partials`). Detect via the PSID `speed` bit; vblank
  subtunes use the flat path unchanged.
- The `mplay` (sound-only) calls still emit the §1 per-voice writes (no order-list /
  sequence advance), so the per-IRQ stream alternates "full play" and "sound-only"
  IRQs in the Q-series — the per-IRQ comparator handles both as long as it buckets
  per `play()` entry.

---

## OPEN items index (each with its closing trace)
- **OPEN-W1** HR frame count (2-frame vs 3-frame gate-off window) — `siddump
  --writelog Wild.sid`, count $D404 gate-bit-0 transitions around a note start;
  `tools/voice_writelog.py --voice 1`. **#1 write-model unknown.**
- **OPEN-W2** are $D415/$D416 emitted every frame on a no-filter packed tune? —
  `--writelog` on a filter-less JCH tune.
- **OPEN-W3** voice processing order (2→1→0) in packed NP20.G4 — `--writelog`
  intra-frame $D40E/$D407/$D400 order.

## Leads to follow
1. **Run `tools/siddump --writelog Wild.sid` now** (the build is available per
   CLAUDE.md `bash tools/build.sh`). One capture closes OPEN-W1/W2/W3 simultaneously
   and validates the entire §1+§3 model against ground truth — this is the single
   highest-value next action and needs no disassembly.
2. **Pair the write model with the extraction blockers** (extraction OPEN-3 seq
   rebase + OPEN-6 super-table stride): once a sequence can be decoded, build a
   minimal USF for one short tune and diff the rebuilt write stream with
   `tools/find_first_divergence.py` — the first divergence will pinpoint which of
   §1-§4 is mis-modelled.
3. **HR-AD source**: confirm the global HR-AD (`cmd2`) location in the PACKED
   super-table (extraction OPEN-6). The write model says `$8x` HR writes AD=`cmd2`
   at the restart frame — getting that byte wrong shows up as a wrong $D405 on the
   first frame of every hard-restarted note (a classic, easily-localised divergence).
4. **Q-series canary**: pick one `speed!=0` JCH tune (e.g.
   `MUSICIANS/H/Haldor/Media_Life.sid`) early to exercise the
   `--writelog-per-irq` path before the wide batch, so the CIA dispatch is proven
   (py65 misses dispatch bugs — ear-test in sidplayfp too).
