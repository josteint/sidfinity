---
name: project_digi_organizer
description: "Digi-Organizer migration — the first parametric-digi family (volume_4bit technique, owner-approved digi{} schema). Round log NEWEST-FIRST; head = current status."
metadata: 
  node_type: memory
  type: project
  originSessionId: eeee45ad-d522-49c1-8391-1946b3565085
  modified: 2026-08-30T07:29:34.090Z
---

## 2026-08-30 — round 4: **39/39 FULL — the standalone family is CLOSED**

**Status: 39 FULL / 0 partial / 0 unsupported of 39 standalone**
(full re-batch, `batch_diff` 0 regressions at every step). Nine members
landed this round, from 30/39.

CLOSEOUT DONE: tier-1 portfolio (22 members over 34 dimensions,
`pipelines/digi_organizer/regression_portfolio.json`) derived and wired
into `regression.py` — BOTH the summary line and the exit-code list —
with `_w_digiorg` verifying via `compare_strict` (the only Mode-2
family in the harness); 22/22 green. `mass_write.py` written (the
corpus_sync binding + a PCM-sidecar orphan sweep, which
ARTIFACT_SUFFIXES cannot see). Backlog item 30 DONE: 18 params keys →
15 while the driver-class registry grew 11 → 14, all byte-identical.

STILL OPEN for this family: the 92 music-paired members (C31-hetero +
the $D418-ownership split verdict), and Rayden_Digi (item 28) on the
same schema.

The last three partials were ONE cause, and the most transferable
finding of the round: the engine CLAMPS a sample row whose end <= its
start to `end = start+1` **through a branch**, so two rows describing
the same single page by different arithmetic play identical audio 2
cycles apart — signal under Mode 2. Not derivable (19 explicit vs 5
degenerate one-page rows in the corpus; a blanket rule traded three
partials for two regressions when measured). Ledger C40 3e.

The other six:

- **Digi_Zak_1 + _2 (Sphere)** — the parked "first-tick phase slip"
  was the **NTSC header flag**. The raster-IRQ tick runs at the FRAME
  rate, so these are 60 Hz streams and the PAL-defaulted rebuild ran
  at exactly 5/6 speed with a perfect content prefix at every horizon.
  Header clock/sid now parsed → typed `PsidMeta.clock`/`sid` → derived
  into the rebuilt header. A SLOPE, not the one-time slip it mimics
  (C40 diagnosis table). _2 additionally had an UNTERMINATED orderlist
  whose walk ran into the sphere driver's own code at $9240 ("pattern
  120 repeat 41" + the garbage latch-$00 sample row that refused the
  build) → the walk now stops at a located-code barrier.
- **Digimix_2 (Jer)** — plays a 152-page sample (its table carves the
  whole $0800-$A000 memory; every other sample a sub-range). No
  canonical hole is that big → the player block became RELOCATABLE
  (page-granular, whole-block; `_layout`). See C40 3d for the two
  layout invariants this surfaced.
- **Digibeatz_1 + _2 (Morton)** — new driver classes `rwait_lock` /
  `rwait_rts`: no raster line is ARMED, the wrapper BUSY-WAITS
  `cmp $d012` until the beam reaches its line (screen blanked, so no
  badline perturbs it), and a PRE-core-init poke of the tick's speed
  immediate makes the image byte stale for seed AND reload. _2 needed
  the PCM overlap JOIN (12 windows into one recording: 429 pages
  separate, 216 merged, ~223 available).
- **Damn_Fine_Digi** — new class `song_head`: an SMC song-select head
  that decides nothing (one song, init ignores A) but whose cycles are
  grid phase, so it is mirrored exactly.

RESIDUE (3, all one class — content-complete, sub-frame cycle phase):
Second_Thoughts (+5-then-−1 idle phase) · Arnie-Rap (322/10081 fr) ·
Trace_Loop (1551/2028). Trace_Loop measured this round: its trigger
path and BOTH NMI handlers are byte-identical to a FULL sibling's, and
both inter-write delta patterns (74/88 and 77/85, same mean) occur on
BOTH sides — so it is phase accumulated at a sample switch, not
structure. Next step is a pc-trace comparison across the switch, which
is the first real investment any of the three needs.

NOT yet: regression.py wiring, mass-write, the 92 music-paired members,
backlog item 30 (params consolidation, scheduled for closeout).

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
