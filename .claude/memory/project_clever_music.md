---
name: clever-music-engine
description: "Clever Music Companion variant — Fairlight + Gyroscope instruction-sequence exact via pipelines/companion/clever_music. Duration counters, embedded commands, song-position sync."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`pipelines/companion/clever_music/` — third Companion engine strain.
Graham Jarvis & Rob Hartshorn's engine, used by Clever Music titles.
Two SIDs instruction-sequence exact end-to-end via `compare_instruction_stream`:

- Fairlight (4322/4322 writes across 46.9s)
- Gyroscope (3502/3502 writes across 60s)

## Engine model

Per-voice state:
- 16-bit pattern_ptr (engine reads bytes through it, advances)
- 5-byte timbre slot (set by $Dx commands, read by NORMAL_NOTE path)
- 8-bit duration_ctr (load_note fires when ==1, else decrement)

Global state:
- Tempo + tempo_ctr (CIA-dispatched at ~50Hz default)
- song_pos counter ($E0..$E5 cycling) — synchronises voices
- 16-instrument table (× 5 bytes each)
- Song dispatch table (6 entries × 2 bytes = pattern pointers)
- Engine-constant 128-entry freq table (identical Fairlight ≡ Gyroscope)

## Pattern byte commands

| byte | name | takes tick? | action |
|---|---|---|---|
| $00-$7F | NORMAL_NOTE | yes | freq + 5-byte timbre + gated ctrl |
| $80 | REST | yes | ctrl gate-off |
| $81 | SKIP | yes | no SID writes |
| $82 N | SET_DURATION | yes | gate off, dur_ctr=N, RTS |
| $B0-$BF | SET_TEMPO | no | tempo=low_nibble, recurse |
| $C0-$CF | SET_MASTER_VOL | no | $D418=low_nibble, recurse |
| $D0-$DF | SET_INSTRUMENT | no | copy 5 bytes from inst_table, recurse |
| $E0-$EF | PATTERN_JUMP | no | if matches song_pos: jump via song_table, advance song_pos, recurse |
| other bit-7 | SKIP_BYTE | no | recurse to next |

## Song-position sync

The global song_pos counter starts at $E0 and advances by 1 each time
a voice's $Ex byte matches it. Wraps $E5 → $E0. With 3 voices and
6 song_pos values, each voice gets 2 $Ex matches per full song cycle.
Voices whose $Ex doesn't match treat the byte as no-op + recurse,
keeping the pattern_ptr advancing without disrupting the song.

For Fairlight/Gyroscope: song_table maps $E0/$E3 → V1 start,
$E1/$E4 → V2 start, $E2/$E5 → V3 start. This re-restarts each voice
at the right point as song_pos advances.

## USF encoding (one byte per row)

Each engine byte → one USF NoteRow:
- $00-$7F → Pitch(name, octave) + duration 1
- $80 → Pitch.rest() + duration 1
- $81 → Pitch.rest() + duration 1 + fx:hold
- $Bx → Pitch.rest() + duration 1 + fx:tempo_N (N = low nibble)
- $Cx → Pitch.rest() + duration 1 + fx:vol_N
- $Dx → Pitch.rest() + duration 1 + instr_ref iN (1..16)
- $Ex → Pitch.rest() + duration 1 + fx:jump_N

Codegen inverts the mapping back to engine bytes.

## Codegen design

Mirrors the original engine's instruction structure for cycle-accurate
matching:
- Real PW loop using `ADC #$04` + CPY end_y loop (5 iterations)
- Recursive load_note with CPX cascade for $Ex dispatch
- (zp),Y indirect addressing requires zp pointers — uses $FB/$FC

This keeps cycle counts identical to the original, so per-VBI-frame
boundary effects don't drift between rebuild and original.

## Related

- [[project_bowden_canonical]] — sister strain (simpler, no per-voice
  duration counters)
- [[project_companion]] — original Hubbard Companion (Up_up_and_Away)
- [[feedback_observation_drift]] — bucketing drift vs music drift;
  why cycle-accurate codegen matters for the writelog verifier
