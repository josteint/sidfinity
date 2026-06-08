---
name: project_human_race_audit
description: "Per-effect audibility audit for Human Race's effects vs Commando's. The principle-driven Rule 1 check; verdict for each."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

For Human Race Option A1, each HR effect must be audited via writelog
comparison against Commando's analogous effect. Rule 1 (cluster by
behavior) collapses two implementations if the per-frame
`(reg, val)` writeset is identical for matched musical inputs; only
genuine writeset differences justify new USF parameters.

The audit procedure: pick an HR instrument that uses ONLY one
effect, find a frame range in the corpus where that instrument
plays, capture orig + rebuild writelogs filtered to one voice, diff.

## Per-effect verdict

| effect | bit | verdict | notes |
|---|---|---|---|
| downslide | bit 0 | **Rule 1 COLLAPSE** with `freq_slide` | confirmed via PC trace + V1-only writelog diff on inst 6 (downslide-only) in subtune 1 frames 225-234. Writes byte-identical. |
| skydive  | bit 1 | **Rule 1 COLLAPSE** with shared-core `fx_incby2` | confirmed via `src/usf/audit.py` on V1 inst 21 (skydive+PWmode) subtune 4 frames 575-604: $0CAA writes OLD v_fhi to V_FREQ_HI on odd frames once (v_flags & $1F) >= $11, then INC v_fhi. Shape identical to shared-core `fx_incby2`; parameters: `incby2_step=1` (HR INC's by 1, Commando defaults to 2), `incby2_onset=17` (HR uses $11, Commando uses 3), `incby2_every_frame=False` (HR + Commando both odd-frame-only). Per-voice running state: HR `v_fhi` at $0DD7 ≡ shared `v_slide`. Note: my first audit attempt mis-identified inst 8 (drumarp+downslide+PWmode) as inst 21 because both share sr=$9A; needed PC-trace on $0DE0 writes (fx_flags cache) to disambiguate. Lesson: use a unique fx_flags value as discriminator, not ADSR. |
| drumarp  | bit 2 | **Rule 1 COLLAPSE** with shared-core `fx_arp` | confirmed via `src/usf/audit.py` on V1 inst 16 (drumarp-only) subtune 3 frames 512-555: HR writes period-8 cycle (1 base + 7 +12 octave), keyed on `frame_ctr & 7`. Shared-core `fx_arp` already implements `(frame_ctr & ARP_MASK) == 0 ? base : base+ARP_OFS` — set HR's EngineConfig `arp_period=8` (currently defaults to 2) and the writeset matches. No new USF parameter, no new opaque kind. Same mechanism Commando uses with `arp_period=2`. Note: subtune 0's instruction-sequence exact match holds because subtune 0 doesn't exercise any drumarp instrument — the test was insensitive to this parameter. |
| PWmode   | bit 3 | **Rule 1 COLLAPSE** with shared-core `fx_pwm` mode='linear' | confirmed via HR disasm $0B86-$0B97 + shared `fx_pwm`. Per-instrument decoder (`inst_generalize.py:173`) already tags HR's bit-3 insts as `pwm.mode='linear'`. The HR-specific bit: `ORA #$40` (force pw_lo bit 6) → set `linear_pw_or=$40` in HR's EngineConfig (Commando uses 0). Audit measurement on V1 inst 15 (PWmode-only) subtune 3 frames 1537+: pw_lo sequence $FF $7E $FD $7C $FB $7A ... matches `(prev_pw + 127) \| $40`. |
| per-note slide | (note field) | **Rule 1 COLLAPSE** — already implemented | The audit's prior prediction of needing a new USF field was WRONG. The shared codegen has `fx_drumslide` (codegen.py:538) and `v_drumtrig` (note_codec.py:186), and the USF carries `porta=N` on `NoteRow.fx_flags`. Algorithm matches HR's $0C04..$0C4B exactly. HR's subtune 3 patterns 58-59 carry 10 actual per-note slides (`porta=17`/`porta=25`/etc.) that round-trip cleanly through the USF. The remaining HR subtune-1-4 verify failures are unrelated — subtune 3/4 are broken from FRAME 0 (init/setup bug), subtune 1/2 have first-divergence at frames 33/13 (separate effect bugs). |

## Audit method that works (for the file)

The PC-trace approach in py65 is decisive. Reproduce by:

```python
# Set up py65 with the SID's binary at its inline-load address,
# stub $EA31 as RTS, install a write observer on $D400-$D418
# capturing (PC, addr, val).
mem[0xEA31] = 0x60
mem.subscribe_to_write(range(0xD400, 0xD419), observer)

# Run init then play() N times to reach the target frame.
# Each play() returns when PC hits the stack-pushed $F000-1
# return address (or BRK byte).

# Frame trace shows which engine PC writes each SID byte. Cross-
# reference with disassembly labels (e.g. `$0C7F = downslide
# early-path freq write`) to identify which effect produced
# which byte.
```

This worked first try. Earlier "look at the writelog" wasn't enough
because writes from multiple voices interleave — V1 + V2 + V3 all
write to the same $D400-$D418 range, and the captured frame shows
all of them. Filter by `sidoff` ($0DA6 in HR) or by voice register
range (`$D400+v*7..$D406+v*7`) to isolate one voice's contribution.

## Common slip during the audit

Looking at the writelog from `inst_program.capture` and assuming
voice attribution from register address is enough — it's not. The
captured frame contains writes from all three voices interleaved.
"V2 wrote $24$DC therefore V2 plays inst with that freq" is wrong;
the $D407/$D408 writes might come from any code path that targets
those registers. PC tracing is the only reliable disambiguator.

## How to apply

For each remaining HR effect (skydive, drumarp, PWmode, per-note
slide):
1. Find an HR instrument that has ONLY that effect.
2. Find a frame in the corpus where that voice plays that inst.
3. Run the PC-trace tool, filter to that voice's writes during the
   relevant frame range.
4. Diff against Commando-engine rebuild's same frames.
5. If writes match → Rule 1 collapse, no new USF parameter.
6. If writes differ → enumerate the difference as a candidate
   parametric distinction; do NOT mint an opaque `*Kind`.

Per-note slide is the only one expected to need a new USF
parameter (composer-chosen per-note content, not engine mechanism).
