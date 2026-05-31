# USF2 → 6502 emit rules

For each `InstSource` constructor, the codegen knows how to emit 6502
that computes the source's value at a given frame and writes it to
the target SID register.

This document is the codegen *contract*. Phase 2's `Codegen2.lean`
implements it. Phase 3+ depends on the rules being stable.

## Runtime layout the codegen assumes

Per-voice state stored in absolute RAM (not zero page — zero page is
the engine's working scratch). Labels referenced by the rules below:

| Label                | Purpose                                      |
|----------------------|----------------------------------------------|
| `v_pitch_v0/v1/v2`   | Current pitch byte for each voice            |
| `v_ctrl_v0/v1/v2`    | Last-loaded ctrl byte (saved for HR / cross-voice ref) |
| `v_inst_v0/v1/v2`    | Last-loaded inst index                       |
| `v_dur_v0/v1/v2`     | Remaining frames before note end             |
| `v_frame_v0/v1/v2`   | Frame counter SINCE NOTE START, per voice    |
| `v_pwmod_v0/v1/v2`   | Current pulse-mod accumulator (lo+hi pair)   |
| `freq_lo_table`      | 96-byte freq table, lo bytes                 |
| `freq_hi_table`      | 96-byte freq table, hi bytes                 |
| `v_sidoff_v0/v1/v2`  | SID register offset for this voice (0/7/14), so STA $D400,Y addresses voice's freq_lo |

`Y` register holds the voice's SID offset for the duration of the
voice's processing, so `STA $D400,Y` etc. address the right voice.
`X` register typically holds the voice index (0/1/2) for absolute,X
addressing into per-voice arrays.

## Source-by-source emit rules

### `const : USFByte`

```
  LDA #$<value>             ; 2 cyc, 2 bytes
```

### `pitchFreqLo` / `pitchFreqHi` with `USFFreqGenSpec`

The spec is `{ vibrato?, freqSlide?, arpeggio? }`. The emit order
matches Hubbard: vibrato sets base+delta, freqSlide adds, arpeggio
OVERWRITES (because arp re-does the freq table lookup at pitch+offset).

For the simplest case (`vibrato=none, freqSlide=none, arpeggio=none`):

```
  LDX v_pitch_vN           ; X = current pitch (or LDX zp pitch scratch)
  LDA freq_lo_table,X      ; A = freq_lo[pitch]
                            ; (caller writes A to target register)
```

With vibrato:
```
  LDA v_frame_vN           ; current frame_offset for this voice
  SEC: SBC #<onset>        ; frame_offset - onset (negative = no vib yet)
  BCC use_base_freq         ; if frame_offset < onset, no vibrato
  AND #<2*period - 1>      ; mask to LFO period
  CMP #<period>
  BCC vib_phase_ok         ; triangle fold (period 8 → fold at 4)
  EOR #<period - 1>
vib_phase_ok:
  STA $F6                  ; save LFO step
  LDX v_pitch_vN
  ; ... compute (freq_table[pitch+1] - freq_table[pitch]) >> depth ...
  ; ... add step * delta to base ...
  ; (full sequence — to be elaborated in Phase 2's Codegen2)
use_base_freq:
  LDX v_pitch_vN
  LDA freq_lo_table,X
```

With freqSlide:
```
  LDA v_frame_vN
  CMP #<startDelay>
  BCC no_slide_yet
  ; running freq = base + (frame - startDelay) * delta
  ; for stopAtZero, clamp at 0 from below
no_slide_yet:
  LDA freq_lo_table,X
```

With arpeggio:
```
  LDA v_frame_vN
  SEC: SBC #<startDelay>
  BCC no_arp_yet
  ; arp_step = (frame - startDelay) / stepEvery mod len(intervals)
  ; pitch_offset = intervals[arp_step]
  ; X = pitch + pitch_offset (clamped to 0..95)
  ; LDA freq_lo_table,X
no_arp_yet:
  ; just base freq
```

Combined: emit vibrato code, then freqSlide adjustment, then arpeggio
overwrite (arp's freq-table-at-shifted-pitch replaces the running
value). Each block guarded by its `startDelay` / `onset`.

### `pulseModLo` / `pulseModHi` with `USFPwGenSpec`

For `mode := .linear speed`:
```
  ; running_pwhi = init_pwhi + frame_offset * speed (mod 256)
  LDA v_frame_vN
  ; ... multiply by speed (use a per-voice accumulator instead of
  ; re-multiplying every frame — see Phase 2) ...
  CLC: ADC v_pwmod_vN     ; current accumulator
  STA v_pwmod_vN          ; save back
                            ; (caller writes A to pw_hi)
```

For `mode := .bidirectional lo hi speed`:
```
  ; running_pwhi oscillates between lo and hi at speed per frame.
  ; Use a stored direction bit + accumulator.
  ; (Detail: full sequence in Phase 2.)
```

### `waveProgStep` with `USFWaveProgSpec`

```
  ; step_index = min(frame_offset / stepEvery, len(program) - 1)
  ; if step_index < len: program[step_index]
  ; else:                program[loop]
  LDA v_frame_vN
  ; ... divide by stepEvery (usually 1 → no divide needed) ...
  CMP #<len(program)>
  BCS at_loop_step
  TAX
  LDA wave_program_inst_<N>,X    ; per-inst literal table emitted by codegen
  JMP done
at_loop_step:
  LDA #<program[loop]>
done:
  ; (caller writes A to ctrl)
```

### `otherVoiceCtrl : Fin V` (cross-voice runtime reference)

```
  LDA v_ctrl_v<V>          ; 3 cyc, 3 bytes
```

That's the entire thing — direct LDA on the named runtime variable.
NO freq-table-aliasing trick. The 6502 code is longer than Hubbard's
compact-aliasing version, but the value written to the SID is the
same.

### `otherVoicePitch : Fin V`

```
  LDA v_pitch_v<V>
```

### `otherVoiceInst : Fin V`

```
  LDA v_inst_v<V>
```

## Trigger emit rules

### `atFrame N`

The event fires once when the voice's `v_frame_vN` first reaches `N`.
For simplicity in Phase 2's codegen, all `atFrame 0` events are
hoisted into the note-load path (which runs exactly once at note
start) and emitted unconditionally. `atFrame N>0` events become
`CMP #N; BNE skip; ... ; skip:` guards in the per-voice update loop.

### `everyFrameFrom N`

The event fires on every frame where `v_frame_vN >= N`. Emit:
```
  LDA v_frame_vN
  CMP #<N>
  BCC skip_this_event
  ; ... compute source, write to target register ...
skip_this_event:
```

For `N=0`, the comparison is unconditional (and codegen can elide it).

### `atFrameBeforeNoteEnd N`

The event fires exactly when `v_dur_vN == N` (counted down from note
duration). Emit:
```
  LDA v_dur_vN
  CMP #<N>
  BNE skip
  ; ... write ...
skip:
```

If the instrument's `noRelease` flag is true, all
`atFrameBeforeNoteEnd` events are suppressed at emit time (no code
generated). Note that `noRelease` is currently on `USFInstrument2`
but should eventually move to the per-note level (set by the pattern
byte's bit 5 — a Phase 2+ refinement).

## Side-effect contract

All InstSource constructors are *pure functions of*:
- the note's `pitch` (loaded into a fixed location for the duration of
  the note),
- the voice's `frame_offset` (`v_frame_vN`, incremented every play() call),
- the cross-voice `v_ctrl` / `v_pitch` / `v_inst` registers (only used
  by `otherVoice*` sources).

There is no implicit per-instrument state beyond those. The PWM
running accumulator (`v_pwmod_vN`) and any other state used by the
generated code is voice-local engine state, not part of the source
semantics.

This is the "ML-friendly" property: an ML model that learns to
generate `USFInstrument2` literals doesn't need to know about Hubbard's
hub_off counter, dynamicFreqEntries, or any other implementation
detail. The grammar is closed under the source primitives.
