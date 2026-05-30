---
name: Last V8 pipeline state
description: pipelines/last_v8 status — Grade D 31.1%, what's fixed, what's left
type: project
originSessionId: f6f9e14c-9398-4e50-b856-89e3b8d85f3e
---
Last V8 (Hubbard, 1985 MAD/Mastertronic, RSID, 17 PSID subtunes split as
music=0..2 / digi=3..4 / sfx=5..16, init=$8D80, play=$8DB3 discovered via
py65 sim of init reading $0314/5).

**Status (2026-05-15): Grade D 46.3% (was F 1.6% at session start).**

What's fixed:
- `pipelines/last_v8/extract/decompile.py` — caps `num_songs` to
  `(seqlo - songs_addr) / bytes_per_song`. Was reading past the real
  3-entry song table into pattern-pointer data, fabricating ghost songs
  whose orderlists pointed into code, decoding as patterns with random
  "instrument" bytes up to 120. Fix gets 3 real songs / 19 instruments
  (was 8 / 121). **General fix — applies to any Hubbard SID with
  phantom subtunes.**
- `pipelines/last_v8/codegen/LastV8/Codegen.lean` —
  1. `v_inst` initialized to `[6, 1, 3]` from binary `$8511..$8513`
     (was `[0,0,0]`). Engine reads pre-baked v_inst on tied first-
     frame notes; without this V1 fires with inst-0 instead of inst-6.
     **F 1.6% → D 31.1%.**
  2. Play warmup-skip: first play call exits early after setting a
     flag, aligning our compact player (~1000 cycles/play) with
     Hubbard's original (~5000 cycles/play, spans two frames).
     **D 31.1% → D 35.7%.**
  3. Drum threshold `SBC #4` → `SBC #3` in i_bit0 Path B (line ~1169).
     Hubbard's drum noise burst is 1 frame; ours was 2.
     **D 35.7% → D 46.3%.**
- PSID header now reads `title`/`author`/`released` from `song.*`
  (was hardcoded "Commando" / "1985 Elite").
- `src/writelog_grade.py` — passes `--force-rsid` so RSID originals
  can be graded (was failing).

**Why: jumping deeper into codegen burns hours per single-byte gain;
the remaining work is structural (cycle-timing + vibrato model).**

**How to apply:** when next attempting Last V8 (or any other Hubbard
SID showing similar Grade-D plateau), the next leverage points in
priority order are:
1. The drum effect duration (`i_bit0` Path B threshold at line ~1151
   of Codegen.lean — `SBC #4`). Tuning this to 1 frame instead of 3
   would close ~285 V2_ctrl divergences, but the SBC immediate is
   tightly coupled with the cycle-timing offset, so changing it in
   isolation regresses the grade. Fix the timing first.
2. Cycle-timing match. Our compact 3.2KB rebuilt player completes
   play() in fewer cycles than the original 13.8KB; snapshots at
   fixed raster boundaries see different fractions of play
   completion. ~1-frame phase offset.
3. Vibrato phase model. V2 vibrato is the single biggest divergent
   register (724 frames).

**Key file:** `docs/hubbard_last_v8_disassembly.s` is the
authoritative annotated 6502 disassembly (Action-Biker style). Read
this before touching Last V8 codegen — it documents the music tracker
($8022), digi player ($8E00), sfx engine ($83B8/$8541), and all data
table addresses.

**Subtunes 3..16 (digi/sfx) are NOT music tracker data.** The
extractor must only process subtune 0..2; the PSID header's count of
17 is misleading.
