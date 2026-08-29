---
name: project_digi_organizer
description: "Digi-Organizer migration — the first parametric-digi family (volume_4bit technique, owner-approved digi{} schema). Round log NEWEST-FIRST; head = current status."
metadata: 
  node_type: memory
  type: project
  originSessionId: eeee45ad-d522-49c1-8391-1946b3565085
  modified: 2026-08-29T14:55:38.349Z
---

## 2026-08-29 — pipeline born; first member FULL cycle-strict

**Status: 1 FULL (Heavy-Beat) of 131 corpus carriers.** Pipeline:
`pipelines/digi_organizer/` (extract.py + to_usf.py + composer_asm.py +
RE_NOTES.md). Schema landed 532b3931 (digi{} block, sample_instruments,
digi_voice — design `docs/digi_parametrization_proposal.md`, owner-approved).

- **Heavy-Beat (2NY): FULL, Mode-2 CYCLE-STRICT** at the ratified window
  (99 s): 4,249/4,249 frames, 535,034 writes, zero divergence — on the
  FIRST build. Composer synthesizes the player from `digi { technique:
  volume_4bit, or_mask }` + the digi_voice score; cycle skeleton mirrors
  the canonical core instruction-for-instruction (mechanism), every data
  byte regenerated from USF + FLAC sidecars. NOT ear-tested (cycle-exact
  match implies identical audio, but the convention stands — play it).
- Player RE in `RE_NOTES.md`: ONE canonical core in 131/131 carriers
  (signature census); orderlist (pat, repeat) pairs / 32-row patterns
  ($FF break) / 4-byte sample table with PER-SAMPLE CIA latch = pitched
  drums / nibble-packed page-aligned PCM / `|$10` or_mask / NO idle
  write. The "$908E init speed byte" IS the tick's LDA #imm operand
  (code-as-data — one engine byte, carried as `tempo`).
- The standalone DRIVER varies per member: strict shape probe (C13) —
  Digitune + Digi_Music_1 REFUSE cleanly ("driver shape mismatch").
  NEXT LEVER: parametrize the driver (raster line + wrapper shape
  variants), then batch the 39 standalone members.
- `digi_tick_raster` / `digi_tick_d011` params keys registered
  (temporal-dispatch); typed `environment` sibling flagged in the
  proposal for the owner.
- AFTER standalone: the paired members (51 beside Music_Assembler, 14
  beside DMC — init copies the core to $9000; C31-heterogeneous merge +
  the music engine's own verify mode per stream: split by $D418
  ownership, music Mode 1 / digi Mode 2). Rayden_Digi (17, item 28
  bucket A) shares the schema; its composer needs the event-stream
  score form + its own cycle skeleton (V2 undisassembled).
- No batch harness / regression wiring yet (1 member). Wire
  `digi_organizer` into regression.py (summary + exit-code list) when
  the standalone batch lands.
