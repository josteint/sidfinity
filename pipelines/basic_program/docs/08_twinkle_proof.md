---
source_url: local: pipelines/basic_program/proof_twinkle.py
fetched_via: local read
fetch_date: 2026-06-23
author: SIDfinity orchestrator
content_date: 2026-06-23
reliability: primary
---

# Twinkle — one-tune end-to-end PROOF (Basic_Program → USF → SID)

`pipelines/basic_program/proof_twinkle.py` proves the full pipeline for one
representative tune: **`DEMOS/UNKNOWN/Twinkle_BASIC.sid`** (RSID-BASIC, the
canonical single-voice "POKE recipe").

## Result

```
WRITELOG VERDICT (flat): is_full=True  match=60/60 (orig) vs 60 (reb)
RHYTHM: 14 onsets orig / 14 reb; max inter-onset frame-gap diff = 4 frames (0.08s)
```

- **Writelog: FULL.** The rebuilt PSID's `$D400` write stream matches the
  original's exactly — 60/60 flat `(reg,val)` — by the project's own
  `compare_instruction_stream` (Mode-1 verdict).
- **Rhythm: faithful.** Real per-note hold durations recovered (note 7 = 30
  frames — the held note in "how I **won**der"); 14 onsets each; max gap diff 4
  frames (0.08 s), inherent BASIC-vs-50Hz quantization + Trap-C bucket drift,
  within the `duration_tol` these tunes need.

## The loop (SID → USF → SID)

1. **Capture** the RSID-BASIC original's writelog (ROM-enabled siddump).
2. **Lift** to a musical model: walk the stream into notes
   (`freq_hi, freq_lo, ctrl=gate_on, hold, ctrl=gate_off, rest`), map each freq
   to a note name/octave + a per-tune `freq_table` (exact bytes), read the
   instrument (triangle, AD/SR) + master volume from the init prefix. Durations
   come from a raw-frame capture (writelog_capture drops empty frames).
3. **USF**: write a real `.usf` (shared USF v2 schema, `src.usf.write_file`),
   reparse it (`parse_file`). See `example_Twinkle.usf` — it is pure musical
   content (note names + durations + tuning table + one instrument), zero engine
   artifacts.
4. **Build** a minimal dedicated PSID player from the PARSED USF. The Hubbard
   composer is not reused (it would add per-frame writes Twinkle doesn't have) —
   per the CORE TENET, the family gets its own runtime. The player walks pattern
   rows: pitched row → set freq + gate on; rest row → gate off.
5. **Verify** flat `(reg,val)` + a rhythm (inter-onset frame-gap) check.

## Findings that generalize to the family

- **Driver prefix.** An empty-init PSID emits a leading `$D418=$0F`; the capture
  of the RSID-BASIC original begins with the same driver write. Strip it from the
  emitted init so the rebuild doesn't duplicate it. (The init is otherwise
  reconstructed from USF semantics — instrument ADSR + `init.sid.master_vol` —
  not raw-byte replay.)
- **Play-once vs loop.** Twinkle `END`s (`IF HF=0 THEN END`); the player halts
  after the last note. Other tunes `GOTO`-loop — the orderlist loop terminator
  vs `stop` encodes this (here: `stop`).
- **Rhythm-blindness of the flat stream.** Each note is exactly 4 writes
  regardless of hold length (the `FOR i=1 TO DR` hold is pure delay), so the flat
  `(reg,val)` stream can't see rhythm — duration lives in the frame gaps. The USF
  must carry durations (it does), and a faithful verdict needs the frame-gap
  check on top of the flat match. `writelog_capture` drops empty frames, so
  durations come from a raw-frame capture (`capture_real`).
- **No new USF schema fields** were needed — note/duration/waveform/ADSR/master_vol
  + a per-tune freq_table all already exist in USF v2.

## What this de-risks for the wider build

The Path-B trace-lift works and produces principled USF. The remaining work to
scale to the 486 is generalization, not feasibility: multi-voice lift (Ahoy-style
legato + V3 sub-note cycling), looping tunes, the 1 digi tune (Mode 2), and
folding `capture_real` + the minimal player into a proper
`pipelines/basic_program/{extract,build,verify}` + the regression harness.
