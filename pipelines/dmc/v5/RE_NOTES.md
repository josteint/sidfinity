# DMC V5 — RE notes (Phase A complete)

Rep: `DEMOS/G-L/Katusha.sid` (family-3, 1461 + family-5 sibling 34 = the
dominant V5 player). Phase A (full disassembly + annotation) DONE
2026-06-14 → `pipelines/dmc/v5/disassembly.s`. Scope + plan in
`pipelines/dmc/v5/SCOPE.md`; format research in
`pipelines/dmc/docs/dmc_v5_{format_notes,docs_original}.md` +
`dmc_sector_commands.md`.

## ✅ Resolved in Phase A (all in disassembly.s header)

- **Sector command byte map** (the flagged unknown): notes `<$80`;
  commands `$F1-$FE` (SRR/ADR/VOL/gate×2/FD-/FD+/FRQ/FLT/SLD/GLD/SND/DUR/
  GATE) + `$FF` END. Track (orderlist): `$FC/$FD` transpose, `$FE`
  voice-end, `$FF pp` loop.
- **8-byte instrument** order confirmed from runtime: AD, SR, WV, PU, FL,
  vib-delay, vib-speed, vib-width(&$07).
- **3 programmable 2-byte tables** (wave/pulse/filter), `$90`=loop;
  filter is **voice-3 only** (`CPX #$02` @ $1496). Vib step = base-note
  freq << width. Full 11-bit filter cutoff ($D415 lo + $D416 hi).
- **Per-voice write order** (sid_write $16E6): freq lo/hi, PW lo/hi, ctrl
  (AND gate mask). Global $D415/$D416 once per play; $D418 in fade;
  $D417 at FLT cmd. Hard restart via gate-mask $F6 + SR=0 (gate_logic).

## Phase B (extract) — operand sites for dataflow

The packer places the data tables per song (like V4 — these addresses
are operand-patched; Katusha's values are the disassembly's). The extract
reads the base of each table by dataflow from these CODE sites (operand
lo-byte address = the listed PC + 1):

| table | Katusha addr | read sites (PC) |
|---|---|---|
| orderlist ptr | $1878 | $1046, $1059 (init) |
| sector ptr lo/hi | $196E / $1972 | $114E / $1153 |
| instrument | $1976 | $12CB/$12CF (note_on), $134F.. (note_init2) |
| freq lo/hi | $170F / $176F | $13A5/$13AB, $168C/$1692, $153B/$1541 |
| wave ctrl/freq | $199E / $19AB | $1385/$165E, $19AB reads alongside |
| pulse lo/hi | $19B8 / $19BF | $13C0/$13C9, $143C/$1450 |
| filter lo/hi | $19C6 / $19C7 | $13EF/$13F5, $149D/$14B1 |

NB confirm whether WV/PU/FL instrument pointers are entry indices or
need ×2 — the player uses them as ENTRY indices into the 2-byte tables
(reads `$199E,y` / `$19AB,y` with y = the pointer, not ×2). So pointers
are entry indices; the table arrays are split lo/hi (parallel), not
interleaved 2-byte records.

## Phase B/C open items

1. Packed memory map for ARBITRARY members (Katusha's table addresses are
   operand-patched — generalize via the dataflow sites above; build a
   `dmc_v5_config` factory like V4/family-2).
2. USF schema: the 3 programmable tables (content-by-reference), fade
   (FD+/-), ADR/SRR live register-sets, full filter cutoff, vib-step=
   freq<<width. Reuse `_offtable_check` pattern.
3. NEW V5 composer (the V4 composer does NOT apply). Write-log-first on
   Katusha. Verdict: `verify_dmc` (engine-neutral, reuse as-is).
4. **family-4 branch (686, Jupiter41, play +$95):** distinct (~0.31
   Jaccard) — diff its disasm against family-3's once family-3 is FULL.

## ✅ Phase B (extract) — DONE + validated (2026-06-14)

`pipelines/dmc/v5/config.py` (DMCV5Config, the operand sites above) +
`extract/engine_model.py` (`extract(cfg) -> V5Model`). Lifts Katusha to
a complete structured model — freq tables, 5 instruments (8-byte),
wave(13)/pulse(7)/filter(1) tables, speed/mastervol, 3 orderlists (with
loop), 4 sectors decoded into event streams. Region sizes from address
deltas (instr|wave_ctrl|wave_freq|pulse_lo|pulse_hi|filter_lo|filter_hi).
The sector-command decode (Phase-A byte map) is implemented + validated:
sectors lift to sensible `dur/snd/note/gate/...` event streams.

Validated on Katusha:
  sector 0: dur 04, snd 00, a note+gate melody
  sector 1/2: dur 02, snd 01/02 fast arps
  sector 3: dur 04, snd 03 melody with rests

## ✅✅ Phase C (composer) — Katusha FULL (2026-06-14)

`pipelines/dmc/v5/composer_v5.py` — a clean re-authored V5 engine
(labeled routines + relabeled state block) driven by the extracted song
data (orderlists/sectors/instruments/freq/tables emitted via labels;
index-based, relocatable). Katusha verifies instruction-sequence exact
at full songlength (trichotomy is_full + state_match, 97955/97955 play
writes; find_first_divergence 98880/98880 = 100%).

The write-log loop (key fixes, each via find_first_divergence + py65):
1. init clears state BEFORE loading track pointers (was wiping them).
2. prime file-image leftovers $1015/$1016/$1017 (filtmode/cutoff).
3. voice tick decs durctr every tick (removed an extra guard).
4. step_commit (gate-off/slide/tied-note) falls through to wave_step +
   writes the steady frame (note_on instead rts's — note_init2 next).
5. pulse_run ALWAYS advances — PU=0 = "no restart", NOT "no run" (the
   running-pulse-program semantics). This was the last fix to 100%.

NOTE — composer keeps the V5 state at the original absolute addresses +
data via labels; it's a faithful clean re-author (the per-frame logic
must match to match the write stream). NOT yet through USF (prototype
extract->model->composer); the USF layer + schema co-design is a
follow-up (the model IS the musical content, so serialization is
mechanical).

## ✅✅ USF layer — DONE (2026-06-14): Katusha FULL through USF

Pipeline is now `extract -> to_usf -> UsfFile -> from_usf -> V5Model ->
build_v5_sid` (composer UNCHANGED — model-driven). Katusha verifies
instruction-sequence exact THROUGH USF (trichotomy is_full + state_match,
97955/97955 play; find_first_divergence 98880/98880 = 100%). Verdict:
`pipelines/dmc/v5/verify_v5.py:verify_v5` (build_from_cfg goes through a
real .usf file). Test: `tests/test_dmc_v5_usf.py`.

Files: `extract/to_usf.py` (model_to_usf + write_v5_usf), `from_usf.py`
(usf_to_model), `verify_v5.py`.

REUSED existing USF types:
- AD/SR -> `Instrument.adsr`; vib delay/speed/width -> `VibratoConfig`
  onset/speed/amplitude (inverted in from_usf).
- WAVE program: `_slice_wave` follows the V5 $90 marker (ctrl==$90 -> the
  parallel freq byte is the ABSOLUTE loop target) into
  `Instrument.waveform`/`wave_freq`/`loop` — decodes away wave_ptr.
  `wave_freq` kept RAW (each step's melodic-vs-abs mode is its own ctrl
  bit 3, visible in `waveform`). Idle walk (table[0]) -> `wave_programs[0]`.
- freq table -> `freq_table` (96 lo + 96 hi). speed -> tempo. master_vol +
  $1015/$1016/$1017 leftovers -> `init.sid` (master_vol +
  InitFilter cutoff_lo/cutoff_hi/res_routing).
- Sectors -> `Pattern`/`NoteRow`: notes = pitch rows, gates ($FE) = `tie`
  rows. Orderlists -> `Orderlist` (entries + signed transposes + loop;
  loop byte-offset <-> entry index).

NEW schema (one principled field, spec-synced — types/grammar/parser/
writer/docs/test):
- `Instrument.pulse_sweep` (`PulseSweepConfig`): inline PW envelope
  `start=$NNNN seg (add, frames) ... [loop=N]` — decodes away pulse_ptr.
  Non-restarting instruments (ptr 0) carry `pwm.keep_running=true`; the
  position-persistence the keep-running relies on is ENGINE MECHANISM
  (per-voice pulse position), not stored content.

KEY WRITE-LOG LESSON (cost one fix-round): V5 `gate_logic` reads the
LOOKAHEAD byte — the raw next byte after a note/gate — to decide the
hard-restart gate-off. So sector command BYTE POSITIONS are write-stream-
significant; the `$FC` snd / `$FD` dur commands may NOT be reshuffled
relative to the notes/gates. They are carried as ORDERED PREFIX FLAGS
(`set_dur` / `set_instr`) on the following note/gate row, re-emitted
verbatim. (First attempt stamped instr per-row + re-emitted on change ->
moved a snd from before a gate to after it -> flipped one $D404 gate bit.)

The full sector command set is now handled (dur/snd/vol/frq/fade/adr/srr/
flt/gate_toggle as ordered prefix flags; gate_tie $F4; glide $FB = note +
glide; slide $FA = tie + glide). Sectors are still decoded in isolation
(family members self-establish dur/snd per sector — path-resolution like
V4 is residue if a member inherits sticky state across sectors).

## ✅✅ FACTORY + PARAMETERIZED PULSE/FILTER (2026-06-14)

`dmc_v5_config(sid)` factory (`pipelines/dmc/v5/factory.py`): 2-entry
jump-table detect (init+$40 / play+$A1; family-4 play+$95 REJECTED),
relocation-aware masked identity-compare vs the Katusha reference. Operand
classification (verified by tracing): code+state ([$1006,$170F) ∪
[$17CF,$1878)) RELOCATE; freq+data tables ([$170F,$17CF) ∪ [$1878,$19D0))
MASKED (packer-patched); SID/CIA (≥$19D0) absolute. Typed
`DMCV5Unsupported` (player_code_mismatch / no_jumptable / family4_branch /
cia_multispeed). Batch runner: `tools/dmc_v5_family_batch.py`.

PULSE/FILTER REPRESENTATION — **parameterized, NOT a shared table.** The
engine's pulse/filter tables are SHARED, FUSED resources (the packer
overlaps per-instrument programs to save bytes; ~30% have no $90, programs
bleed). Carrying them whole (content-by-reference flat table) is correct
but ML-worst (raw-byte program = Pole B + opaque index = Pole A). The
chosen form (user: "most principled / ML-optimal"): per-instrument
`pulse_env` / `filter_env` = `start + [(rate, frames)] phases + repeat` —
the PWM/cutoff envelope, the SAME musical family as Hubbard/DMC-V4 PWM
(cross-engine, §9 test 4). The packer's fusion is dissolved by
CAPTURE-BY-SIMULATION: `_capture_env` walks each instrument's reachable
phases (FOLLOWS $90 jumps — a loop target may be a count slot the engine
re-reads as a step — and detects a true cycle only on revisiting a
captured position; bounded by _REACH_FRAMES so bleeding past the horizon
is dropped). `from_usf` SYNTHESIZES a de-fused table (each instrument its
own copy + a $90 terminal); keep-running (pulse_ptr 0 -> pwm.keep_running)
continuations stay faithful because each continues whatever (faithfully
synthesized) program the prior restart-instrument was running. Validated:
all 5 sample-FULL members stay FULL through the parameterization (two
capture bugs fixed: $90 at the last table slot was skipped; $90 to a
count slot must be FOLLOWED+unrolled, not read as a phase index).

WIDE-BATCH COVERAGE — gated by COMPOSER/EXTRACT, not the representation.
80-member sample: 5 FULL (6%), 45 partial, 29 unsupported. The partials
reproduce in the DIRECT model path (no USF) — `composer_v5.py` was only
proven on Katusha. Bug distribution (the rounds, in lever order): $D416/
$D415 filter cutoff (22), end-of-init state-only Check-A (16), freq/PW (7);
plus expected residue (player_code_mismatch sub-builds, no_jumptable
relocated-in-file/CIA, ~36%). NEXT: composer rounds — FILTER FIRST (the
#1 lever), then state-only, then freq — like V4's coverage climb.

## ✅ FILTER ROUND 1 (2026-06-14) — startup-leftover priming (commits 8bea641, f598c2a)

The "$D416/$D415 filter cutoff (22)" bucket was TWO distinct causes; the
first-divergence register only NAMED the filter (it's the first write of
the play frame). Diagnosed via find_first_divergence + per-IRQ + ordered
FCHI/FCLO sequence diff.

**Cause A — uncleared STARTUP LEFTOVERS (the lead-in cluster, ~10 of the
22; "orig $D416=$00 / new $D418=$0F at play pos 0").** The V5 init sets
$1012 (speed reload) but the clear loop ($1067-$106E) only covers
$17D5-$1845, so THREE work-RAM bytes in the $1006-$103F gap keep their
file-image leftover values:
  - $1013 spdctr (speed COUNTER). When !=0 the first non-skip play() runs
    effects-on-leftover for N frames BEFORE the first note fetch (tick =
    speed==spdctr); those lead-in frames write freq from the leftover note.
    Katusha's $1013=$00 (0 lead-in frames) so the cleared-to-0 composer
    matched it; members with $1013!=0 diverged at play write 0.
  - $100F,x per-voice current NOTE. Read by the lead-in frames' wave_step
    (ADC $100f,x freq-table lookup) before the first fetch overwrites it.
  - $101C fade fractional accumulator. Init clears the fade SPEEDS
    $1018/$1019 but not this sub-integer phase, so a tune's first FD+/FD-
    ramps master vol from the leftover phase ($D418 vol off-by-one).
FIX: extract lo_spdctr/lo_notes/lo_mvolfrac; prime spdctr/curnote/mvolfrac
in init; carry through USF via the existing cross-engine `speed_ctr_init`
params key + `InitVoice.note` (V4 idle-note) + a new `fade_frac_init`
params key — NO shared-schema additions. Result: X-Files + Believe newly
FULL; whole cluster advances (Believe was 95%). Katusha still FULL; USF
round-trip faithful (direct==USF first_play_diff).

## ✅ FILTER ROUND 2 (2026-06-14, commit 24875f3) — keep-running filter_run

**Cause B — FILTER KEEPS RUNNING across FL=0 notes (a run-GATING bug, NOT
the synthesis-flow issue first hypothesised).** After cause A the cluster
(Grid/Minoam/Conanious) still drifts mid-song: FCLO ($D415) drifts (orig
RAMPS +1/frame, rebuild HOLDS) while FCHI ($D416) NEVER differs (the ramp
step is (0,+1) -> fchi+=0). Per-instrument `_capture_env` envelopes match
in ISOLATION (verified 200 frames) -> NOT a synthesis bug. ROOT CAUSE: the
orig `filter_run_v3` ($1496) gates ONLY on `CPX #$02` (voice 3) — it runs
EVERY V3 frame; FL=0 = "no filter RESTART", not "no filter RUN" (the SAME
PU=0 semantics as pulse_run). The composer gated `filter_run` on the
PER-NOTE `filtflag` (the instrument's FL byte), which an FL=0 note resets
to 0 -> the composer SKIPPED filter_run on keep-running frames -> the
cutoff held while the orig kept ramping. Katusha passed because its
pre-filter null is a no-op (the gate happened not to matter). FIX: a
STICKY `filt_run_on` flag, set once when any FL!=0 note inits the filter,
never cleared; `filter_run` gates on it instead of `filtflag`
(`filter_init` keeps the per-note gate, so FL=0 still = no restart). Only
ADDS filter_run on keep-running frames so FULL members can't regress (their
held positions were no-ops). The per-instrument `filter_env` representation
is UNCHANGED — this was a run-gating bug, not a synthesis/flow problem, so
the user-chosen parameterisation (option a, "faithful") stands without any
table change. RESULT (80-sample): FULL 5->15 over the whole session (the
filter rounds: +10 new FULL, NO regression; 7 of the 10 were original
$D416/$D415 partials — Grid/Reggae_2/Save_the_Kwiatki/Fire_Exit/
A_Load_of_Cowbell/Lands/Bach_VC-220). RESIDUE: Minoam 98.3% / Conanious
96.2% have a small end-of-song tail (per-register late diffs show V1/V2 SR
+ V3 freq, not filter — the diverse partial long tail, separate bug).

## ✅✅ RELOCATED / WRAPPER-INIT UNLOCK (2026-06-15, commits 0e3c319 + 023c1b6 + 5f3a0de)

The `no_jumptable` (261) + `player_code_mismatch` (266) unsupported buckets
were 477/527 the SAME family-3/5 player with a RELOCATED or WRAPPED init.
TWO sub-shapes (both found by dumping the jump table + init/play targets):
  - **wrapper/relocated init** (most `no_jumptable`): jump table at load,
    play entry -> base+$A1 (standard), but the INIT entry points elsewhere
    (e.g. $1CE9) — the init is byte-identical to the std init, just MOVED;
    the orderlist record is read by that moved init (operand at init+7).
  - **re-prefixed init** (most `player_code_mismatch` "opcode at $1040"):
    jump table +$40/+$A1, init at $1040 but its first bytes differ
    (`0A 0A 0A` = ASL*3 song-index vs Katusha `A9 00` = LDA #0). Single-
    subtune (A=0 -> Y=0) so the orderlist read still works at init+7.
Old factory keyed base off the jump-table LOCATION (fixed +$40/+$A1) and
compared the WHOLE player (init+play) -> any moved/re-prefixed init -> reject.

FIX (the family-1/2 sub-build playbook, V5 form) in `factory.py`:
  - `base = play_target - $A1` (the play routine is the reliable anchor; the
    jump table's play entry gives base regardless of where the init lives).
  - validate the PLAY-reachable body ONLY (`_v5_play_ref`, $10A1-$170E);
  - validate the init by its orderlist-copy SKELETON at the jump table's
    init target (`<4-byte prefix> A2 00 B9 lo hi 9D <17CF+delta>`) and read
    `op_orderlist = init_target + 7` (the moved init's actual load operand);
  - base-plausibility = `base + $848 <= $10000` (only code+state
    $1006-$1845 relocate; data tables are packer-patched — masked compare's
    job. The earlier $1900 margin wrongly rejected high-load base=$F000
    builds -> 2 regressions, fixed);
  - **multi_subtune** (ASL*3 prefix, `songs>1`, 36 members) typed-deferred —
    needs a multi-song PSID build the composer doesn't emit yet.
RESULT: ~300 members unsupported -> supported; **FULL 354 -> 461/1495
(+107; 30.8%; 41.9% of supported)**; all 461 mass-written + db refreshed.
RESIDUE: player_code_mismatch 152 (deeper code variants — bucket by
play-body first-diff PC), multi_subtune 36, note_out_of_range 36,
no_jumptable 22, error 108 (extract robustness), 640 partial (long tail).
NEXT: multi-song emit (multi_subtune) > partial long tail > deeper variants
> extract errors > family-4 (686, play +$95).

## ✅✅ MULTI-SUBTUNE SUPPORT (2026-06-15, commits b4994d0 + 21e767d)

Multi-subtune members index the orderlist record by song#: the init does
`ASL*3; TAY` -> Y = song#*8, then copies record N (3 track ptrs + speed +
master vol) into the work RAM. The data tables (sectors/instruments/freq/
wave/pulse/filter) are SHARED across subtunes; only the orderlist record +
its referenced orderlist streams are per-subtune.

5-file change: `engine_model` (V5Subtune dataclass; extract reads one record
per song at op_orderlist+N*8, tables shared, top-level fields mirror subtune
0) -> `composer_v5` (ordrec = one 8-byte record per subtune; init reads
song# from A: `ASL*3; PHA` across the state clear; `PLA; TAY`; index ordrec
by song#*8; PSID `songs` = subtune count — UNIFIED with single-subtune since
song#=0 gives Y=0, identical play) -> `to_usf` (one MusicSubtune per record,
per-sub tempo/master_vol/voices; the GLOBAL file-image leftovers — filter
cutoff, speed_ctr_init/fade_frac_init, idle notes — on subtune 0) ->
`from_usf` (pool sectors across ALL subtunes' voices into one shared pool;
read per-subtune speed/mvol/orderlists) -> `factory` (multi_subtune
rejection removed). RESULT: FULL 461 -> 466/1495 (+5; 31.2%, 41.4% of
supported), 0 regressions; 34 moved unsupported->supported; all 138
subtune-songs build correctly. A member counts FULL only if ALL its subtunes
are FULL, so the fully-FULL gain is modest — the partial multi-subtune
members have a subtune hitting the diverse long-tail bug. Single-subtune
unaffected (init change transparent). All 466 mass-written + db refreshed.

## (historical) factory + wide-batch plan
`dmc_v5_config` factory (jump-table detect init+$40/play+$A1, the
operand sites above, carved reference) + reuse tools/dmc_family_batch.py
over family-3/5 (1495). Then the family-4 branch (686, play +$95).

## (historical) Phase C plan

A NEW hand-authored V5 engine (the V4 `composer_asm.py` does NOT apply —
8-byte instruments, table-based pulse/filter, full filter cutoff, the
14-command sector model). Must be RE-AUTHORED clean (the tenet forbids
emitting verbatim/relocated player bytes). USF schema co-designed
write-log-first: the 3 programmable tables (content-by-reference), fade,
ADR/SRR, full cutoff, vib-step=freq<<width. Verdict: `verify_dmc`
(engine-neutral, reuse). Then factory + wide batch (family-3/5, 1495),
then the family-4 branch.
