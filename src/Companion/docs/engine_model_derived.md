---
source_url: local: docs/hubbard_up_up_and_away_disassembly.s + binary inspection
fetched_via: local read + py65 disassembly
fetch_date: 2026-05-25
author: derived (this document)
content_date: 2026-05-25
reliability: secondary (derived from 6502 disassembly of Up_up_and_Away.sid; not yet cross-checked against Bowden's book or Murray's Henry's House)
---

# Companion engine model (base variant, Bowden lineage)

Derived from `docs/hubbard_up_up_and_away_disassembly.s` and direct
inspection of `demo/hubbard/Up_up_and_Away_original.sid`. Cross-check
against Bowden's book or Henry's House is still pending.

## Memory map (relative to load $C000)

```
$C000 - $C07F   Freq hi table (128 entries — pitch index 0..127)
$C080 - $C0FF   Freq lo table (128 entries)
$C100 - $C4EF   ... (unverified, possibly more tables or padding)
$C4F0 - $C50F   32-byte init template (copied to $C6C0 by init)
$C5B0 - $C5F7   V1 orderlist
$C5F8 - $C63F   V2 orderlist
$C640 - $C6BF   V3 orderlist
$C6C0 - $C6DF   Live runtime state (32 bytes; init template image)
$C700 - $C914   Engine code (init + play + voice processing)
$C915 - $C91D   Per-subtune dispatch table (5 lo + 5 hi)
```

## Runtime state layout (`$C6C0 - $C6DF`, 32 bytes)

```
+0..+6   V1: orderpos, gateoff_flag, pw_lo, pw_hi, ctrl_saved, ad, sr
+7..+13  V2: same fields, offset 7 (engine indexes by X=0/7/14)
+14..+20 V3: same fields
+21..+31 Globals: $C6D5=gate-off tick, $C6D6=note-load tick,
                  $C6D7=tempo counter, plus 8 more global bytes (TBD)
```

Reading the Up,up&Away init template at `$C4F0`:
- V1: pw=`$0C00`, ctrl=`$40` (pulse, gate off), ad=`$07`, sr=`$85`
- V2: pw=`$0800`, ctrl=`$40`, ad=`$07`, sr=`$85`
- V3: pw=`$0100`, ctrl=`$40`, ad=`$09`, sr=`$57`
- gate-off-tick=`$09`, note-load-tick=`$0D` → 9/13 ≈ 70% sustain at the
  template tempo (with counter starting at `$0C`).

## Note encoding (orderlist byte format)

Each orderlist byte is one "row" / one tempo step.

| Byte value | Meaning |
|---|---|
| `$00..$7F` | Play pitch (low 7 bits = pitch index into freq table); gate ON |
| `$80+pitch` (bit 7 set, low 7 = pitch) | Play pitch AND schedule gate-OFF at next gate-off tick |
| `$8C` (= `$80 + $0C`) | Sentinel: "no new note" — keep playing previous (write current ctrl, no freq change) |
| `$8D` (= `$80 + $0D`) | Sentinel: same as `$8C`, but if voice == V3 → end song (set volume = 0) |

The dual interpretation of `$00..$7F` vs `$80..$FF` means the engine
can express "staccato" vs "legato" without using extra bytes — bit 7
is the "release-this-step" flag.

## Play loop per VBI frame (`$C703`)

```
INC global_PWM_counter              ; $C6DE, drives V3 PW sweep
if global_PWM_counter == $01:
    global_PWM_counter = 0
    V3.PW_LO += 4                   ; one-step PW sweep on V3 only
INC tempo_counter                   ; $C6D7
if tempo_counter == $C6D5:          ; gate-off tick
    for X in (0, 7, 14):
        if state[X].gate_off_flag has bit 7 set:
            write V_CTRL = state[X].ctrl_saved   ; gate goes off
            state[X].gate_off_flag = 0
elif tempo_counter == $C6D6:        ; note-load tick
    tempo_counter = 0
    for X in (0, 7, 14):
        Y = orderlist[X][state[X].orderpos]
        state[X].orderpos += 1
        if Y has bit 7 set:
            state[X].gate_off_flag = Y
            Y = Y & $7F
            if Y == $0C: write V_CTRL = ctrl_saved (no change)
            elif Y == $0D:
                write V_CTRL = ctrl_saved
                if X == 14: end song (vol = 0)
            else:
                # bit-7-with-pitch case: play pitch AND schedule gate-off
                fall through to normal-note path with Y = pitch
        else:
            # Normal note: pitch index
            V_FREQ_HI = freq_hi_table[Y]
            V_FREQ_LO = freq_lo_table[Y]
            V_PW_LO = state[X].pw_lo (for V1/V2 only — V3 PW driven by sweep)
            V_PW_HI = state[X].pw_hi
            V_AD = state[X].ad
            V_SR = state[X].sr
            V_CTRL = state[X].ctrl_saved + 1   ; gate ON
```

## Subtune dispatch

Init at `$C900`:
1. `LDA $C915,X` → patches lo byte of JMP operand at `$C913`
2. `LDA $C91D,X` → patches hi byte of JMP operand at `$C914`
3. `LDA #$0F; STA $D418` (vol on)
4. `JMP $C831` (now patched to JMP to per-subtune init)

Per-subtune init at `$C915/$C91D[i]` does whatever setup is needed for
subtune `i` — typically setting starting orderlist position and tempo.
For Up,up&Away, the 5 targets are: `$C831, $C7ED, $C80F, $C853, $C875`.

The main init at `$C831`:
- Copies the 32-byte template from `$C4F0` to `$C6C0`
- Resets PW HI on V3, sets vol=$0F
- (per-subtune route may override fields before this)

## Variants (NOT yet modeled)

- **Murray variant** — Henry's House style. Adds Y=$80/$FF orderlist
  wrap+restart sentinels; uses 423 Hz A4 tuning (different freq table).
- **Jay Derrett variant** — nibble-indexed double-LUT front end (see
  sidid signature decoding). Different orderlist format.

For now, the migration plan covers ONLY the base variant
(Up,up&Away's 5 subtunes). The Murray variant for Music Examples
subtune 1 is a separate scope.

## USF representation

This engine has NO effects (no arpeggio, vibrato, PWM, skydive,
drum). Per the USF representation principle: Companion music expresses
in USF v2 with all fx parameters at their default/none values.

- **Patterns + orderlist**: each voice has one big "pattern" containing
  the entire note sequence; orderlist references that one pattern. The
  USF schema's existing pattern abstraction handles this as the
  degenerate "one pattern, used once" case.
- **Instruments**: per-voice ctrl/pw/ad/sr from the init template
  become USF instruments. V3 gets a "linear PWM" mode (pwm.speed=4) to
  encode the +4 sweep. Note: this is the SAME parametric form as
  Hubbard '85's linear-PW instruments — no new schema needed.
- **Note durations**: each orderlist byte = one "row" = one duration
  unit. The USF `duration` field is set to 1 for every note; the row
  length comes from `params.tick_divider` (= note-load-tick value).
- **Gate-off mid-row**: when a note byte has bit 7 set, the USF note
  carries the implicit gate-off (release fires within the row, not at
  the next row). Conceptually similar to a "no_release" flag inverted
  — or to a duration shorter than a row. We can model this as a
  per-note flag `early_release` in the USF, OR as two duration values
  on the instrument (note-on→gate-off and gate-off→next-note). The
  latter is more general (matches the engine's runtime gate-off-tick
  vs note-load-tick).

The cleanest USF representation:
- New optional engine params: `gate_off_tick`, `note_load_tick`.
- Per-note flag: `early_release` (gate is released at gate-off-tick of
  this row rather than the next).
- Everything else fits existing USF v2 unchanged.
