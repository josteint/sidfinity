---
name: project_digi_organizer
description: "Digi-Organizer migration — the first parametric-digi family (volume_4bit technique, owner-approved digi{} schema). Round log NEWEST-FIRST; head = current status."
metadata: 
  node_type: memory
  type: project
  originSessionId: eeee45ad-d522-49c1-8391-1946b3565085
  modified: 2026-08-29T19:12:03.891Z
---

## 2026-08-29 (later) — standalone batch: 21/39 FULL cycle-strict, 0 partial

**Status: 21 FULL of the 39 standalone members (54%), 18 unsupported
(unprobed driver shapes), 0 partial / 0 error** — every member that
classifies verifies FULL Mode-2 at the ratified window
(`tmp/digi_organizer_results.jsonl`, store `digi_organizer` registered;
engine in `code_fingerprint.DEPS`). The driver-class registry
(`irq_vec` / `nmi_first` / `xreg` / `bare_stub`) + four cycle-level
levers did it:
- `digi_base_latch` — the pre-first-trigger TA latch is the NMI GRID
  ORIGIN (min(rate_cycles) was a wrong guess that coincided on
  Heavy-Beat; Lets_Do_It exposed it).
- `digi_port_preinit` — Morton's core-entry stub sets $01=$35 (its
  driver doesn't); the SAME stub sits UNREACHED in other members —
  probe gated on entry reachability (`digi_core_entry`).
- `digi_core_tail` — one tail byte (RTS vs NOP/CLI fall-through)
  shifts the idle-loop phase vs the NMI grid = constant per-write
  latency delta under Mode-2.
- `digi_driver_bit` — the Xmas xreg form carries a `BIT abs` filler in
  driver AND wrapper (4 cycles each).
Plus: past-EOF PCM served CPU-eye via `--peek-post-init` (C29 — the
power-on stripe is genuinely played; Gangstarr/You_Cant/Suffer FULL),
and overlapping sample-table ranges (three entries carving one
recording, Memomay) dedupe CONTENT-ADDRESSED in the composer's page
allocator (regions $1000-$8FFF / $A000-$CFFF / $E000-$FEFF; $D000+ is
I/O under port $35).
REMAINING 18: unprobed driver shapes — Morton poke variants (~5), Jer
Digimix ×3, Sphere ×2, Earbleed ×2, Digibeatz ×2, Bayliss
Second_Thoughts, Feekzoid Arnie-Rap, Damn_Fine_Digi, Digi-Zak_3,
Dont_Talk_to_Me. Same probe+emitter pattern, one shape each.
NOT yet: regression.py wiring, mass-write, the 92 music-paired members.

## 2026-08-29 — pipeline born; first member FULL cycle-strict

**Status (superseded by the entry above): 1 FULL (Heavy-Beat) of 131 corpus carriers.** Pipeline:
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
