---
name: project_digi_organizer
description: "Digi-Organizer migration — the first parametric-digi family (volume_4bit technique, owner-approved digi{} schema). Round log NEWEST-FIRST; head = current status."
metadata: 
  node_type: memory
  type: project
  originSessionId: eeee45ad-d522-49c1-8391-1946b3565085
  modified: 2026-08-29T20:05:08.446Z
---

## 2026-08-29 (late night) — round 3: 30/39 FULL, verdicts CURRENT

**Status: 30 FULL / 4 partial / 5 unsupported of 39 standalone**
(aa059cda; 0 regressions). New: `kernal_irq` / `kernal_lock` / `arnie`
driver classes; the STUB-FORM registry (`jmp` | `nopslide` | `romcopy`
— the KERNAL $E000-$FFFF copy-under-itself, ~131k pre-timer cycles);
the **`digi_nmi_vec` CORE VARIANT** — KERNAL-path members (port $36)
re-point ALL NINE NMI vector-swap operands at $0318/$0319 (the KERNAL
NMI RAM vector); probe requires all-site consistency, composer
substitutes globally. Patterns past image end served CPU-eye (C29).
Digi-Zak_3 FULL first try.
RESIDUE: partials Second_Thoughts (content-complete, +5-then-−1-cycle
idle-phase) + Arnie-Rap (322/10081 fr) + Trace_Loop (1551/2028) +
Digi_Zak_1 (first-tick phase slip, extensively measured);
unsupported Damn_Fine (song-select head, decoded, needs emitter) +
Digibeatz ×2 (D011=0 screen-off + busy-wait-raster wrapper + pre-init
speed pokes, decoded, needs emitters) + Digimix_2 (152-page blob —
suspect a garbage used-id (s,e) first) + Digi_Zak_2 (garbage id-55
table row admitted by the extract — gate used ids on sanity).

## 2026-08-29 (night) — driver-zoo round 2: 29/39 FULL, verdicts CURRENT (superseded above)

**Status: 29 FULL / 2 partial / 8 unsupported of 39 standalone** (fresh
batch, 0 regressions). Four more driver classes landed: `jer_lock`
(Jer ×3, JMP-self lock, env-relative $D011 AND-writeback), `poke_stub`
(Morton delayed ×4 — flag-gated wrapper + busy-wait start delay +
RUNTIME SPEED POKE: the poked value IS the tempo, the image byte is
only the first-row seed → typed `speed_ctr_init`; two gate forms
cmp1/ackfirst_beq), `earbleed` (×2), plus `bare_stub` wrap-NOPs and
`xreg` BIT-filler variants. TWO C40 refinements measured (recorded in
the entry): PAGE-ALIGN emitted loops (a page-crossing taken branch =
+1 cyc/iteration — shifted a stream by exactly the 11 outer
iterations), and the shifted-perfect-prefix diagnosis (first-tick
phase slip; wall-frame burst indices, never compacted frame counts).

RESIDUE (named): 6 driver singles (Damn_Fine songs-counter driver,
Second_Thoughts JSR-core-first + $0314 vector, Arnie-Rap, Digi-Zak_3
$0314 vector + JMP tail, Digibeatz ×2 speed-poke variants) · the
SPHERE PAIR (Digi_Zak_1 partial / _2 refused on a garbage id-55 table
row): perfect content prefix at EVERY horizon, whole stream lags one
initial raster-IRQ phase slip vs the env $D012 latch neither side
writes — first-tick phase, measured extensively, parked ·
Digimix_2: a 152-page (38KB) blob exceeds the largest contiguous free
region — check whether one used id's (s,e) is a garbage row first ·
Trace_Loop: deep partial (77% prefix, equal totals) — ordinary
first-divergence grind.

## 2026-08-29 (later) — standalone batch: 21/39 FULL cycle-strict, 0 partial (superseded above)

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
