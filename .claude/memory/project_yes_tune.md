---
name: yes-tune-engine
description: "Yes_Tune — Companion variant with per-voice state machine and 2-byte (note, duration) pattern format. Byte-exact via pipelines/companion/yes_tune."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`pipelines/companion/yes_tune/` — sixth Companion strain. Per-voice
state machine engine with 2-byte (note, duration) format. Used by:

- Yes_Tune (anonymous 1986 demo) — 4542/4542 writes match
- Soldier_of_Fortune (Michael Draper, 8 subtunes incl. 5 SFX) —
  8/8 subtunes byte-exact

Same engine code relocated ($6000 base for Yes_Tune, $B600 for
Soldier_of_Fortune). Layout detection scans play loop for the
`LDA abs,X / CMP #$02` state-byte pattern; freq tables at
voice_base-$100 / -$80.

## Engine semantics

Per-voice state at `$6200+X` (X = 0/7/14):
- `+$00` tick_ctr — countdown; play next pair when it hits 0
- `+$01` state — 0=skipped, 1=normal-play, 2=load-pattern
- `+$02..+$06` timbre (5 bytes)
- `+$15/+$16` mutable pattern_ptr (lo/hi)
- `+$17/+$18` immutable pat_start (lo/hi, used by state=2 reset)

Globals:
- `$622A` tempo_ctr, `$622B` tempo
- `$6100..$617F` freq_hi, `$6180..$61FF` freq_lo (identical to Clever Music)

## Pattern format

**Two-byte per event.** Each musical event = (note, duration) pair.

| First byte | Second byte | Meaning |
|---|---|---|
| $00-$7F | duration | NORMAL_NOTE: play freq + 5-byte timbre + gated ctrl; tick_ctr=duration; advance ptr by 2 |
| $80 | duration | REST: gate off; advance ptr by 2 |
| $81 | — | STOP_VOICE: gate off, state=0 (silent forever); ptr stays |
| $FF | — | LOOP: reset ptr to pat_start, recurse play_note |

Duration 0 is special-cased to 1.

## Init

Minimal — does NOT silence the SID. Just:
- `$D418 = $0F`
- per-voice state[1] = 2 (load on first play tick)
- CIA1 timer setup (handled by psiddrv in PSID dispatch)

## USF encoding

One row per pattern event:
- Normal pair → `Pitch(name, octave) + duration N`
- $80 rest → `Pitch.rest() + duration N`
- $81 → `Pitch.rest() + duration 1 + fx:stop`
- $FF → `Pitch.rest() + duration 1 + fx:loop`

Pattern's USF `length` field is the sum of row durations (total ticks),
not row count — required for USF validation.

## Related

- [[project_henrys_house]] — sibling single-voice strain
- [[project_clever_music]] — shares the freq table
- [[project_bowden_canonical]] — sibling 3-voice strain
