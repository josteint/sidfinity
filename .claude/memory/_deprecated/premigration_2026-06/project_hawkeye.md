---
name: hawkeye
description: "Future Composer family — Hawkeye (Tel_Jeroen). 12/12 subtunes FULL via featuredriven path. Sub 6 root cause was orig $8243-$826B bit-2 sweep (slow freq-hi creep), implemented as fx_freq_hi_rise effect (USF schema field FilterProgConfig.freq_hi_rise + composer's freq_rise_acc state). Identified via memwatch-on-write D401 at full songlength duration."
metadata: 
  node_type: memory
  type: project
  originSessionId: 02f65b25-1c68-4ebb-b180-7ebbd9c37c55
---

`hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid` — Future Composer family.
Current verify state (`verify_featuredriven(HAWKEYE)`):

| Sub | State | Notes |
|---|---|---|
| 0-11 | FULL | All subtunes match orig writelog exactly (Cyb II FULL too). |

(Sub 6 was the last partial — fixed 2026-06-06 via fx_freq_hi_rise.)

## Sub 6 root cause (CORRECTED 2026-06-06 — vibrato output mismatch)

### CORRECTION: prior "drum-path glide" hypothesis WAS WRONG

I read `$90DA = $15` (= wave-program step 21, drum bit set) from a 15s
memwatch capture and built the whole "drum-path glide" story on it.
But that capture's siddump frame 737 wasn't the writelog_capture frame
737 — siddump frame buckets ≠ PSID `play()` invocations (Trap C),
and at 15s the song hadn't progressed to the actual divergent frame.

`tools/find_first_divergence.py` uses `writelog_capture` with full
songlength duration. To get matched state, the memwatch capture must
use the same duration. With `--duration 110` (matching the 97s × 1.1
verify duration), the actual state at the divergent D401 write was
captured:

```
$9133=$0C   $9136=$23   $90DD=$47   $90E3=$0C   
$90D7=$3C   $90D4=$48   $90DA=$19   $90F6=$01
```

`$90DA=$19` = wave-program **step 25** (not 21). Inst record at $86D4:

```
PUL=$08 WAV=$11 AD=$08 SR=$DD FIL=$04 fx1=$43 fx2=$00 fx3=$05
                                                          ^^^
   filter_program ($01) + tone_arp ($04). NO drum, NO glide.
   fx1=$43 → vibrato amplitude=3, speed=4, direction=positive.
```

### Actual root cause: vibrato output

State trace at the divergent moment:

1. **nolengset** loaded current note idx $48 → `$90E3=$0C, $90DD=$47`
   (preserved freq lo/hi).
2. **tone_arp** at `$7E32-$7E5D` ran (gated by F9 bit 2 = fx3 bit 2,
   set on step 25). Computed Y = `$90D7 + arp_offset` = `$3C + $0C` =
   `$48`, then wrote `$9133 = lonote[$48] = $0C` (matches snapshot)
   and `$9136 = hinote[$48] = $47`.
3. **vibrato** at `$7E60-$7F3F` ran (gated by F7 = fx1 = $43, non-zero).
   The LFO loops at `$7EBB-$7F2B` (sub/add iterations based on
   `$9101`/`$9104` LFO state) modified `$911E:$911F` from base
   `($0C, $47)` to `($0C, $23)`. Then `$7F2E-$7F3F` wrote the result
   to `$9133/$9136`.
4. **Nextvoice** at `$830C-$831D` wrote D400 = `$9133` = `$0C` (write
   5201) and D401 = `$9136` = `$23` (write 5202).

Mine's `fx_vibrato` produces different LFO output, leaving `$9136`
at the table value `$47`. Hence the divergence at write 5202.

### Lesson learned: memwatch duration must match writelog_capture duration

`siddump --memwatch ADDR --duration T` captures state up to time T.
If T is shorter than `writelog_capture`'s duration, the state shown
is at a DIFFERENT engine-state moment than the divergent frame
`find_first_divergence.py` reports. Always pass the SAME `--duration`
to memwatch as the verify is using.

A quick rule: `verify_featuredriven` uses `songlength_s × 1.1 + 1`
per-subtune. Read it from `verify.py` and pass the same to memwatch.

### To finish sub 6 (next session)

Compare mine's `fx_vibrato` body (composer_asm.py:1625-1956 approx)
against orig `$7E60-$7F3F` line-by-line. The state variables to trace:

- `$911E`/`$911F` — vibrato base (loaded from freq table at `$90D4`)
- `$9120`/`$9121` — vibrato step (delta, right-shifted by amp)
- `$9101`/`$9104` — LFO state (direction + counter)
- `$90F6` (counter2) — controls when SUB loop is active (`CMP #$0C`)
- `$90FD`/`$90FE` — amplitude + speed cached

Use `tools/disasm_diff.py --orig SID --orig-range 7E60-7F3F --composer
composer_asm.py --composer-label fx_vibrato` for the side-by-side.

Expected: mine's LFO state diverges from orig's at some specific
operation (e.g., wrong INC/DEC, wrong CMP boundary, wrong sub-amount).
Fix per CLAUDE.md core tenet: produce the same writelog stream, not
necessarily the same 6502 mechanism.

V1 at frame 737 plays wave-program **step 21** (per-frame counter
`$90DA[V1]=$15`). Step 21's "inst" record at `$86B4` has `fx3=$11`
(drum + filter_program bits). Drum bit triggers orig's drum-path
branch at `$7E2D-$7E2F`:

```
$7E2B: AND #$10        ; F9 (cached fx3) AND drum bit
$7E2D: BEQ $7E32       ; NOT drum → normal effect chain  
$7E2F: JMP $7F42       ; DRUM → enter drum-path glide
```

The drum-path glide at `$7F42-$800E`:

```
$7F42: LDA $90E6,X         ; glide-active flag
$7F47: BNE $7F4F           ; non-zero → run glide
$7F49: JMP $8038           ; else skip everything

$7F4F-$7FF7: 16-step SMC-heavy glide-division — computes step
  size from delta = freq_table[$90D7] - freq_table[$912B], with
  direction (SEC/CLC) and operand (SBC #XX) SMC'd at $7FB3/$7FB6/$7FB9
  based on the sign of the delta.

$7FFA: LDA $90E3,X         ; preserved freq lo
$7FFE: SBC #$XX            ; (SMC) subtract glide step lo
$8000: STA $90E3,X
$8003: STA $9133,X         ; current freq lo shadow ← orig D400=$0C
$8006: LDA $90DD,X         ; preserved freq hi
$8009: SBC #$YY            ; (SMC) subtract glide step hi
$800B: STA $90DD,X
$800E: STA $9136,X         ; current freq hi shadow ← orig D401=$23
$8011: JMP $8038
```

At frame 737, orig has prev `$90E3[V1]=$E8`, `$90DD[V1]=$24`. Glide
step: SBC `#$DC` / SBC `#$01`. Result: `$90E3=$0C` (which matches
write 5201 `D400=$0C`), `$90DD=$23` (which matches write 5202
`D401=$23`).

### Why mine produces `D401=$47`

Mine's drum-path chain at `composer_asm.py:1557` is:

```
        beq fx_tone_arp        ; not drum — normal chain start
        jmp fx_glide           ; drum — skip tone-arp + vibrato
```

So mine's drum chain falls into `fx_glide`, but mine's `fx_glide` is
a DIFFERENT glide implementation than orig's drum-path glide at
`$7F4F-$800E`. Mine's `fx_glide` may not be exercised here (gate
mismatch) or compute a different step.

### To finish sub 6 (next session)

The drum-path glide is a separate engine effect from the non-drum
glide. Needs implementing as a new chain variant (`fx_drum_glide` or
similar — see CLAUDE.md schema discipline). Inputs:

- `$90E6[V1]` — glide-active flag
- `$912E[V1]` — glide control byte (hi nibble = step, lo nibble = dur)
- `$90D7[V1]` — source freq table idx
- `$912B[V1]` — target freq table idx
- `$90CB[V1]`, `$90CE[V1]` — frame counters (drives termination)

Outputs:
- Modifies `$90E3`/`$90DD` (preserved) AND `$9133`/`$9136` (current)
  in lockstep, with the same SBC value.

### Why the prior session went wrong

I started from py65 disasm fragments instead of reading the hand-
annotated `pipelines/future_composer/hawkeye/disassembly.s` (1051
lines) + `RE_NOTES.md` (608 lines) that were already in the repo.
Should have started with those, not raw disasm of inst regions I
hadn't characterised. Reflex for future engine investigations:
**check `pipelines/<engine>/disassembly.s` and `RE_NOTES.md` BEFORE
any session debugging an FC-family effect — they're already done.**

Frame 737, V1 mid-note. Single-byte divergence at write 5202 (5201
prefix matches): orig `D401=$23`, mine `D401=$47`. Surrounding writes
(D404=$11 ctrl, D400=$0C freq lo) match identically. So orig has SOME
routine that writes `$9136[V1]=$23` between nolengset and PC `$831D`
(the nextvoice block) — and mine doesn't replicate that write.

`$0C` matches freq table idx `$48` (`lonote[$48]=$0C, hinote[$48]=$47`)
in BOTH engines, so the divergence is specifically that orig modifies
`$9136[V1]` after nolengset's load whereas mine doesn't.

### Hypotheses ruled out (2026-06-06 session)

1. **+$20 freq-shift effect at orig `$8232-$8240`, gated by
   `fil_count bit 3` (orig `$910F`):** ruled out — NO Hawkeye music
   inst has `fil_count` bit 3 set (full dump above). This effect never
   fires for the music subtunes. `$910F` is the cached `fil_count`
   byte, not `fx3`.

2. **`tonesweep_up` at orig `$812E-$813A`, gated by `F9 bit 5`
   (= `fx3 bit 5`):** ruled out — NO Hawkeye music inst has `fx3` bit 5
   set. (`F9` is just the cached `fx3` byte: stored at `$7E29` from
   `$8613,Y` = inst byte +7.)

3. **`drum_dl` dynamic length vs orig's hardcoded `#3` CMP at orig
   `$82A0`:** ruled out by direct test — patching the composer's drum
   CMP from `drum_dl` to `#3` broke 8 of 12 Hawkeye subs (the dynamic
   length is necessary for the other subs). The hardcoded `#3` in
   orig's disasm at `$82A0` must be checking something OTHER than drum
   max-frames (perhaps a sub-routine selector).

### Candidate writers still in play

orig has 12 sites that `STA $9136,X` (see disasm). Of those, paired-
lo-then-hi writers cover nolengset, vibrato, glide-style routines.
Hi-only writers (no paired `$9133` store): `$813A` (tonesweep_up, ruled
out above), `$8240` (ruled out above), `$8269` (ruled out above),
`$82C9` (drum bit-4-clear path inside `$8272-$82D1`). Paired writers
not yet investigated for V1 frame 737:

- `$7E5D` (paired `$7E57`) — looks like tone-arp re-lookup
  (`LDA $8337,Y / STA $9133 / LDA $8396,Y / STA $9136`, Y derived from
  `$9107,X` + INY).
- `$7F3C` (paired `$7F33`) — glide target reload (reads `$911E/$911F`
  scratch and writes BOTH `$9133/$90E3` and `$9136/$90DD`).
- `$800E` (paired `$8003`) — not analysed.
- `$802D` (paired `$8024`) — not analysed.
- `$82C9` (no paired lo — paired `$82CE` writes `$9133=0`) — drum
  effect `$8272-$82D1` bit-4-clear path: `$9136 = $910B + $0D`. orig's
  drum effect IS unconditional for counter2 < 3, so this DOES write
  during drum.

### Recommended next-session approach

Use `siddump --pc-trace` filtered by PC range to identify which exact
routine writes `$9136[V1]` between frame 737 cycle 0 and cycle 1193.
The `effect_chain_profiler.py` tool exists but in the prior session it
displayed a confusing value (`$04`) for the divergent write — likely a
display bug. Investigate the profiler tool first; if its output is
trustworthy it should name the writer directly.

If the writer turns out to be a path I HAVE implemented (drum, glide,
tone_arp), the bug is in the implementation; if it's a path I haven't
implemented, design the schema addition per the principle doc.

## Composer prerequisite landed (2026-06-06)

`lonotesto2` (= orig `$90E3`) declared parallel to `hinotesto2` (= orig
`$90DD`). nolengset's `STA $9133,X` is mirrored by `STA $9136,X`-style
dual-store (`sta lonotesto2,x` next to `sta hinotesto2,x`).

Also: `hk_nt_release` (noise-tick release path, `hawkeye_constants`
style) now reads from `lonotesto2`/`hinotesto2` instead of `lonotesto`/
`hinotesto`, matching orig `$82F8`/`$8301` (preserved-freq release, not
modulated-freq release).

Neither change alters the writelog (sub 6 still partial at 5202; no
other sub regresses) because the +$20 shift effect itself isn't yet
implemented and noise-tick release path isn't exercised by this sub.
Both changes are structurally faithful to orig.

## To finish sub 6 (next session)

1. Add USF schema field for the +$20 shift effect (`fx_freq_shift` with
   `amount: int` — or principled subtype if the effect is broader than
   one engine). Follow [[feedback_schema_addition_discipline]]: exhaust
   derivation / existing-params alternatives first. Likely a new typed
   effect dataclass.
2. Detect during extract: per-instrument, check `$910F[inst] AND #$08`.
3. Composer emitter: emit the 5-instruction block reading `lonotesto2`/
   `hinotesto2` (already present from this session).
4. Also implement bit-2 sweep (`$8243-$826B`) — required for full sub 6.
5. Verify sub 6 → FULL. Should not regress any other sub.

## Cybernoid II — same family

`hvsc84/MUSICIANS/J/Jeroen_Tel/Cybernoid_II-The_Revenge.sid` — 2/2 FULL.
Same featuredriven path. Drove `pulse_run` separate-state infrastructure
([[project_cyb2_pulse_run]] — TODO if not present).

## Tooling that cracked this

`tools/find_first_divergence.py` (with the verify-matched duration) →
exact divergence position. Then `effect_chain_profiler.py` confirmed PC
$831D (the nextvoice block) wrote orig's D401=$23 — so the bug is in
the shadow at write-time, not the writer. Then PC-trace + disassembly
of all `STA $9136` sites in orig identified `$8240` as the only
candidate producing the asymmetric (`$0C`, `$23`) pair. Took ~10
minutes from divergence to root cause once the right tools were used.

## Related

- [[feedback_writelog_divergence_recipe]] — the protocol used here.
- [[feedback_verification_modes]] — Mode 1 (frame-by-frame instruction
  sequence) is the verdict for Hawkeye.
- [[feedback_deconstruct_not_reproduce]] — CORE TENET. The composer can
  invent its own state names + layout; what matters is the writelog
  stream. `lonotesto2` doesn't need to be at `$90E3` — it's wherever
  xa65 assembles it.
- [[feedback_schema_addition_discipline]] — required before adding the
  `fx_freq_shift` schema field.
