# Last V8 pipeline

Goal: rebuild Rob Hubbard's *The Last V8* (1985, MAD/Mastertronic) SID through
the SID→USF→SID pipeline, matching the original byte-for-byte under
`siddump --writelog`.

## Status (2026-05-15)

| Metric | Value |
|---|---|
| Pipeline scaffolding | yes (Lean codegen + Python extractor, cloned from Commando) |
| Disassembly | yes — see `docs/hubbard_last_v8_disassembly.s` |
| Rebuilt SID metadata | correct (title/author/released wired through `song.title`) |
| Music match vs original | **Grade D (46.3% snapshot match)** |
| Digi samples | not handled |
| Sfx subtunes (5–16) | not handled |

The remaining 54% gap is mostly **vibrato/freq-slide phase drift** on V2
(594 frames differ on V2_freq_hi, the single biggest diverging register).
Concretely: Hubbard's freq-slide effect (`i_bit0` Path A) DECs `v_fhi` and
writes the OLD value to SID; our codegen does the same, but starts the
descent one frame earlier on some notes and skips the descent on others
(because the `v_dur < 3` countdown guard fires at slightly different
points). The trace shows orig V2 going `$3A,$3A,$3A,$39,$38,$37,$3A,$3A`
while new goes `$3A,$3A,$3A,$39,$3A,$38,$3A,$3A` — a 1-frame skip pattern.
Closing this requires tracing Hubbard's exact countdown semantics at
`$83C7..$8438` and re-tuning the codegen's Path A guard.

## What got fixed this session

### Decompiler — `extract/decompile.py`

- **`num_songs` is now capped by the song-table → seqlo gap.** The PSID
  header claimed 17 subtunes; the real song table only has 18 bytes
  (`$8797..$87A8`) = 3 entries of 6 bytes. The old code ran the song-parse
  loop for all 17 subtunes, reading past the table into the pattern-pointer
  lo region as if those bytes were more song pointers. That produced 5
  "valid"-looking phantom songs whose orderlists pointed into pattern data
  and code, decoding into nonsense patterns with random "instrument" bytes
  up to 120. Capping to 3 real subtunes brings extracted state down to
  the correct 3 songs / 28 patterns / 19 instruments (was 8 / 29 / 121).

### Codegen — `codegen/LastV8/Codegen.lean`

- **`v_inst` initial values are now `[6, 1, 3]`** (extracted from the
  Last V8 binary at `$8511..$8513`). Hubbard's player relies on these
  pre-baked per-voice instrument indices for tied first-frame notes —
  on subtune 0 V1's pattern 0 is a 32-frame TIE, so the player reads
  `v_inst[V1] = 6` from the binary and writes instrument 6's ctrl
  (`$41`, gate-cleared to `$40`), PW `$0900`, ADSR `$0700`. Our codegen
  was initializing `v_inst` to `[0, 0, 0]`, so V1 fired with instrument
  0's settings (`ctrl $11`, `PW $0800`, `ADSR $040F`) → frame-1 mismatch
  on every register. **F → D (31.1%).**

- **Play warmup-skip.** The very first `play()` call exits immediately
  after marking a flag, so the rebuilt player is offset by exactly one
  frame against `siddump`'s snapshot grid. Aligns our compact 3.2KB
  player (whose play takes ~1000 cycles, finishes within one frame)
  with Hubbard's original (whose play takes ~5000 cycles, spans two
  frames). **D 31.1% → D 35.7%.**

- **Drum effect threshold `SBC #4` → `SBC #3`.** Path B of the i_bit0
  freq-slide block writes `$80` (noise burst) for Hubbard's drum
  attack. The original burst is 1 frame; our codegen was emitting 2.
  Tightening the duration-vs-countdown threshold from `SBC #4` to
  `SBC #3` matches the original. **D 35.7% → D 46.3%.**

- **PSID header now reads `title`/`author`/`released` from `song.*`**
  instead of being hardcoded to "Commando" / "1985 Elite".

### Grading — `src/writelog_grade.py`

- **`siddump --force-rsid` is now passed unconditionally** so RSID
  originals (like Last V8) can be graded. Was previously failing with
  "Skipping RSID". The flag is a no-op for PSID files.

### Metadata — `extract/emit_usf.py`

- Title corrected from "LastV8 on the Run" to "The Last V8" /
  "1985 MAD/Mastertronic".

## What's still wrong

py65 trace (using a KERNAL-RTI stub at `$EA00..$FFFF` so play() exits
cleanly) of ORIG vs NEW for play frames 0-11:

```
frame 0  ✓  17 writes byte-identical
frame 1  ✓  12 writes byte-identical (different ORDER for pw_lo/pw_hi)
frame 2  ✗  V2ct=$10 (orig) vs $80 (new)
frame 3  ✗  V2fh=$39 vs $3A  +  pw_lo/pw_hi order swap
frame 4  ✗  V2fh=$38 vs $39
frame 5  ✗  V2fh=$37 vs $3A  +  pw order
frame 6  ✓
frame 7  ✗  pw order
frame 8  ✓
frame 9  ✗  pw order
frame 10 ✗  V2ct=$40 vs $80
frame 11 ✗  V2fh=$40 vs $41  +  pw order
```

Two patterns:

1. **V2 ctrl bytes ($10/$40 vs $80).** Instrument 0 has `fx_flags & 1`
   set (drum). Hubbard's drum effect fires noise (`$80`) for a 3-frame
   burst then drops to gate-off (`$10`/`$40`). The new rebuild's drum
   burst extends longer than the original's. Likely a drum-counter
   off-by-one or a different model of when the noise burst ends.

2. **V2 vibrato position drift.** Hubbard's vibrato is a triangle LFO
   driven by the global frame counter (`$8535`) — period 8 frames,
   phase 0,1,2,3,3,2,1,0. The rebuild's vibrato either has a different
   phase reset point or a different depth scaling. Visible as a
   slow-growing freq_hi divergence on V2 from frame 3 onward.

3. **PW lo/hi write order swap.** Hubbard writes pw_hi at `$82B5`
   THEN pw_lo at `$82BC` in the bidirectional-PWM effect path. Our
   codegen writes pw_lo then pw_hi. This DOESN'T affect the writelog
   grade (siddump captures snapshots at frame boundaries, not mid-
   instruction, and both bytes end up at the same value either way) —
   but it does mean the per-instruction trace looks different.

## Concrete next steps for Grade A

1. **Fix the drum-effect duration.** Biggest single remaining leverage.
   The current `engine_model.py` emits the drum waveform program as
   `[ctrl|1, $80, $80, $80, ctrl&~1]` with `wave_loop=4`. Hubbard's
   actual drum is shorter — looks like 1-2 frames of `$80` before
   dropping to gate-off. A `py65` step-trace through `$8085..$8093`
   (waveform program advance in the music tracker) on the original
   would pin down the exact frame count. Should fix the V2_ctrl
   divergence in the 285 frames currently differing.

2. **Match the vibrato phase.** The codegen's vibrato uses a fixed
   8-frame triangle with `semitoneShift := 3` and `onsetFrames := 6`,
   but the original modulates V2_freq_hi by `-1/-2/-3` over 6+ frames
   (visible in py65 trace). Trace Hubbard's vibrato code at `$81B0..
   $823D` to find the exact onset point, depth-scaling formula
   (instrument byte 5), and phase reset behavior. Should close most
   of the V2_freq_hi divergence in 724 frames.

3. **Initialize `v_ctrl`/`v_pwlo`/`v_pwhi` from binary.** Same pattern
   as `v_inst` — extract from `$850B..$850D` etc., emit as initial
   values in the data block. Marginal effect on the grade (snapshots
   are cycle-bounded) but cleaner semantics.

4. **Move the hardcoded initial values into `engine_model.py`** so the
   pipeline is data-driven rather than Last-V8-coded. Pipe them through
   `ExtractedSong` → `USFSong.engineQuirks` → `Codegen.lean`.

5. (Once music is Grade A) decide whether the digi/sfx subtunes need
   USF representation. They probably don't — the USF schema is
   tracker-oriented and the digi/sfx engines are fundamentally
   different code paths.

## Why the grade is stuck at 31% despite mostly-correct writes

The writelog grader compares per-frame snapshots after audibility
masking. Two effects compound:

- **Cycle-timing offset.** Our 3.2KB rebuilt player completes play()
  in fewer cycles than the original's 13.8KB player. siddump's
  snapshot at end-of-frame N captures the rebuild "done with play N+1"
  but the original "still mid-play N". Manifests as a ~1-frame phase
  offset (raw match at shift +1 = 11.9% vs shift 0 = 7.8%).

- **Drift accumulation.** Once vibrato/drum timing diverges by one
  frame, the V2 freq snapshot disagrees indefinitely. With 724
  diverging V2_freq_hi frames out of 1500, that single bug accounts
  for ~48% of the missing match.

Fixing items 1 and 2 above should move the needle from 31% toward
70-80%. Getting to byte-perfect (98%+ like Commando) likely requires
cycle-equivalent codegen as well.

## How to run

```bash
PYTHONPATH=src python -m pipelines.last_v8.extract.emit_usf 0
source src/env.sh && lake build sidgen_last_v8
./.lake/build/bin/sidgen_last_v8
python src/writelog_grade.py --duration 30 \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Last_V8.sid \
    pipelines/last_v8/build/last_v8.sid
# Expected: Grade D, snapshots ~31%, 467/1500
```
