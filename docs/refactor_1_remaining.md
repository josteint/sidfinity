# Refactor 1 — what's deferred and why

## Status (2026-06-03)

Phase B of Refactor 1 landed: every routine emitter in the composer
is `FxNames`-parameterised; the `_needs_hubbard85_path` discriminator
is dissolved; `emit_asm(model, usf)` is the single asm-emission
entry with a feature-named 5-way dispatch.

But the dispatch is engine-flavored in structure: each of the 5
branches maps roughly to one engine family.

| Branch | Engine family |
|---|---|
| every_tick + single_phase (atomic) | henrys_house, bowden_canonical |
| every_tick + two_phase (companion) | up_up_and_Away |
| tick_counter_decrement (pair) | yes_tune family |
| dur_counter_decrement + commands (cmd-stream) | clever_music |
| `not can_handle(model)` (bitpack) | Hubbard '85 family |

With one engine family per branch, the §8 cover-story risk is open:
the discriminator is feature-named but pragmatically routes uniformly
per engine family.

## Why we're not refactoring further now

Going further (one player skeleton subsuming the family flavors)
requires designing against the diversity of engine shapes the
composer has to handle. Today the corpus is narrow: 5 engine
families, ~150 subtunes. Designing a unified skeleton now overfits
to those 5 shapes.

DMC (~10k SIDs) and GT2 (~7k SIDs) bring real structural diversity:
DMC's sector-based patterns + per-instrument FX programs; GT2's
filter / pulse / waveform tables + hard-restart mechanics. Migrating
them first either vindicates the current feature dimensions
(multiple consumers per feature = genuine parametricity) or surfaces
new dimensions the dispatch needs. Either outcome informs the
unified-skeleton design honestly.

## When to revisit

Pick this back up when at least two of:

- DMC migration substantially started (even 50–100 verified subtunes
  gives the composer real DMC shape feedback).
- GT2 migration substantially started (`deprecated/gt2_pipeline/` has
  prior work; resuming it would reactivate a ~7k-SID corpus).
- 2+ other large engine families migrated (Music_Assembler ~6k,
  Future_Composer ~4k, Soundmonitor ~3.6k SIDs).

**Vocabulary: an engine family counts toward this trigger when it is
"uready" (unification-ready)** — the six-criteria maturity gate defined
in `.claude/memory/feedback_uready_vocabulary.md`: orig-free §9 builds,
no escape hatches, factored/reversible USF, representative verification
(variant census + wide-batch pass-rate), feature-dimension accounting,
documented residue. "Is this engine uready?" is the question to ask
before leaving a family.

### Trigger progress + shape evidence (2026-06-11)

The **standard ("vanilla") Future Composer player** (~2700 of FC's ~4k
SIDs, one fixed-layout relocatable image) is substantially migrated: a
12-SID load/variant-spread sample verifies play-stream exact with
trichotomy audio-equivalence; the wide batch is next. Shape evidence it
contributes to Move 1's design:

- **Reused dimensions** (evidence the feature space is sound): wave_arp,
  noise_tick (new 'standard' style), filter_programs (grown along the
  musical axis: variable seg count + onset), pulse programs (4-byte
  variant of the same threshold/step schedule), the portamento space
  (glide=N target-style vs glide_up/down+onset rate-style),
  Orderlist.loop_transpose (loop-pickup semantics).
- **New write-model shape**: conditional freq writes + chain-direct
  effect writes with per-effect lo/hi order asymmetries (the composer's
  fw_mode dispatch) — a per-voice write model none of the prior five
  families had.
- **Per-MEMBER player variants** (hacked operand bytes, NOPed writes,
  JSR hooks, wrapper inits) handled as factory-probed behavior knobs —
  a finer granularity than per-family configs; the unified skeleton's
  input surface must account for it.
- **An honest §8-shaped note**: the FC composer now carries its own
  Tel-vs-standard layout dispatch (gwo2 → std_wave_chain etc.) — the
  same engine-flavored branch structure this document describes for the
  Hubbard composer, deferred by the same corpus-richness logic. It
  belongs in Move 1's scope.

At that point the 5-way dispatch will have either grown to 7-10
branches (signaling the structural move is needed) or will have
absorbed new engines into the existing feature dimensions (signaling
the dimensions are sound).

### DMC v4↔v5 cross-engine reuse review (2026-06-18)

DMC migrated as **two full composers** beside the `emit_asm` skeleton:
`pipelines/dmc/composer_asm.py` (`build_dmc_sid`; v4 + family-2) and
`pipelines/dmc/v5/composer_v5.py` (`build_v5_sid`; family 3/4/5). So the
build-dispatch fan-out is now `emit_asm` (5 branches) **+ 2 standalone DMC
skeletons** — branch growth at the dispatch level, not inside `emit_asm`.
Both DMC composers are clean on the §8/§9 leak scans (no engine-name
dispatch, no `: bytes`/`*_idx`/`*Ptr`/`*Kind`, no verbatim-byte emission).

**Vindicated (reused, same form across v4 ↔ v5)** — these dimensions are
sound: `freq_table`, the song structure (subtunes/voices/orderlist/patterns/
`NoteRow`, incl. `Orderlist.transposes`), `init`+`init.sid` priming,
`Instrument.adsr`, **the wave envelope** (`waveform`+`wave_freq`+`loop` —
byte-identical form — plus `wave_programs[0]` as the idle wave),
`Instrument.vibrato` (shared `onset`+`amplitude` core), and
`PwmConfig.keep_running` (the one PwmConfig field v5 keeps is the one v4
also uses).

**Forked dimensions (same musical concept, two USF forms)** — the silent
divergence this review exists to catch, now surfaced. Four pending
unify-vs-keep decisions for Move 1:

1. **Pulse-width sweep.** v4 = `Instrument.pwm` (PwmConfig: bounded
   bidirectional oscillator — `mode='bidirectional'`, `init`/`min_hi`/
   `max_hi` bounds, `speed_steps` per-flip rate schedule). v5 =
   `Instrument.pulse_env` (`SweepEnvelope`: `start` + `phases[(rate,frames)]`
   + `loop`). SweepEnvelope is the **superset** (a bidirectional oscillator =
   `start` + `[(+s,n),(−s,n)]`, `loop=0`); the schema doc already names
   PwmConfig "a future unification target."
   **GATE PASSED (2026-06-18):** simulated v4's exact oscillator (BNE-exact
   bound check, speed_steps schedule, 16-bit wrap) over 1,868 real instruments
   in 200 v4 FULL members, derived the equivalent SweepEnvelope, re-walked it
   (v5 semantics), compared PW frame-by-frame — **100% expressible exactly**
   (incl. the min>max wrap-around runaway), 99.9% compact-loop (≤10 phases;
   runaways = 2 phases within a song horizon, handled by `_capture_env`'s
   reach + cap + terminal-hold). So the bound-checked-vs-frame-counted concern
   is resolved: equivalent on the write stream.
   *Converter algorithm (for the Move-1 landing — the gate script was scratch):*
   simulate v4's oscillator faithfully (note-init `composer_asm.py:743-784`:
   pwl=0, pwh=`init&0x0F`, dir=up, phase=0; per-frame `fx_pulse:859-901`:
   `step = (speed_steps[phase]&0xF0)+(speed_steps[0]&0x0F)`, add/sub 16-bit,
   flip dir only when the HIGH byte lands exactly on `min_hi`/`max_hi` via BNE,
   advance phase on each flip capped at 5); group the value stream into
   maximal constant-(diff mod 65536) runs = `SweepEnvelope.phases`; set `loop`
   to the phase-level period of the saturated (phase-5) tail; a rate-0 tail or
   no-period (runaway) = terminal (`loop=None`). v4's emitted pulse table then
   becomes v5's `(add,count)`-pair + `$90`-loop format, walked by a `pulse_run`
   clone — that's the D.2 runtime convergence.
   DECISION = **unify onto SweepEnvelope** (sound). BUT landing it is NOT a
   field swap: the convert-at-the-composer-boundary shortcut is circular, so
   the clean unify requires giving v4's composer a pulse **phase-walker** (the
   shape of v5's `pulse_run`) and retiring the bound-oscillator runtime — i.e.
   this is the **Move-1 D.2 runtime convergence** (per-voice state + runtime),
   touching the 4,786-member v4 FULL family, verify-gated. Recommend landing
   it AS the Move-1 effort (DMC isn't uready yet; nothing consumes the forked
   USF files until tokenization, which is downstream), not as a one-off now.

2. **Filter-cutoff sweep.** v4 = `Instrument.filter_prog.program` →
   `UsfFile.filter_programs[N]` (indexed library: `{res,mode,init,repeat,
   stop,steps:[(rate,frames)×6]}`). v5 = `Instrument.filter_env`
   (`SweepEnvelope`, inline). **v4's `filter_programs.steps` is ALREADY
   `(rate,frames)` pairs** — near-isomorphic to `SweepEnvelope.phases`
   (`init`→`start`, `repeat`→`loop`; the `res`/`mode` header maps to the
   already-separate `init.sid.filter.res_routing`). Cleanest unify candidate.
   DECISION: unify onto SweepEnvelope — or keep the indexed-library form
   (shared with FC's `filter_programs`; preserves the editor's program-share).

3. **Glide / portamento.** v4 = `Instrument.freq_slide_config`
   (`mode='run'`, unbounded continuous slide — per-INSTRUMENT, same form as
   Hubbard's skydive). v5 = `NoteRow.fx_flags` inline (`glide=spd` /
   `glide_to=pitch` — per-NOTE-EVENT, aligns with FC-standard's target-style
   portamento). Both attachment points already exist corpus-wide. DECISION:
   likely genuinely-two-behaviors (continuous instrument slide vs
   note-triggered portamento-to-target) — keep both as the two poles of one
   portamento dimension; do not force into one.

4. **Idle/default sweeps.** v5 has `UsfFile.default_pulse` (per-voice) +
   `UsfFile.default_filter` (V3-global) — play-time sweeps the engine runs
   unconditionally from table position 0. v4 has NONE (its pulse/filter are
   note-triggered only). DECISION: keep v5-only (single-consumer is justified
   — it encodes a real v5 engine behavior, not a leak). A future engine with
   idle sweeps reuses it.

**Escape-hatch surface to revisit (not a v4↔v5 divergence):** both use
`Params.fields` with disjoint string keys — v4: `slide_phase`,`cia_period`
(+ family-2: `cymbal_onset`,`vib_ramp`,`hold_gateoff`,`hard_restart`,
`rest_effects`); v5: `speed_ctr_init`,`fade_frac_init`. The family-2 keys
are behavior-named (good); the `*_init`/`*_phase`/`cia_period` keys are
uncleared init-phase state (borderline §7 — affect the write stream, so not
pure bookkeeping, but not musical content either). Flag for a future pass.

**Diff vs last review:** the only previously-recorded divergence was DMC
`SweepEnvelope` vs FC `filter_programs`/`pulse_programs`. This review adds
the DMC-INTERNAL v4↔v5 fork (3 musical concepts, 2 forms) — the first time
one engine family is shown representing the same concept two ways. DMC v4/v5
are NOT yet individually uready (criterion 4: v5 ~61%, v4 ~58-65% FULL;
residue not fully triaged/excluded), so they don't yet add to the Move-1
trigger count — but they supply the richest divergence evidence to date. The
implication: Move 1's skeleton must reconcile the PW/filter forms (decisions
1+2) BEFORE folding DMC in, or it bakes the fork into the unified shape.

### All-families uready review (2026-06-18) — cross-family divergence decisions

Periodic `/uready-review` (scope: all). Trigger MET (4 uready: Hubbard,
Companion, FC Tel, FC standard; DMC not yet — C3 freq_overrun-minimization +
C4 residue-triage gaps). Leak scans clean. The dispatch is GROWING branches
(DMC added 2 standalone composers beside `emit_asm` + FC's `composer_asm`) while
the feature DIMENSIONS are absorbing — so Move 1 should converge composers around
the already-validated dimensions below, not invent new ones. The full cross-family
divergence list Move 1 must reconcile (extends the DMC-only decisions 1-4 above):

- **D1 — PW sweep → `SweepEnvelope`** (4 forms: Hubbard `pwm` linear/bidi · FC
  `pulse_prog`+`pulse_programs` indexed-lib · DMC-v4 `pwm` bidi · DMC-v5
  `pulse_env`). Decision-1 gate proved the bounded oscillator is losslessly a
  SweepEnvelope; FC's indexed-library is the §7-adjacent form.
- **D2 — Filter sweep → `SweepEnvelope`** (FC + DMC-v4 `filter_programs` indexed-
  lib, whose `steps` are already `(rate,frames)` ≈ phases · DMC-v5 `filter_env`).
  NB an INTRA-family fork: DMC v4 vs v5 disagree.
- **D3 — Glide:** per-instrument continuous slide (Hubbard, v4) vs note-event
  portamento (FC, v5) — likely genuinely two behaviors; keep both poles.
- **D4 — Vibrato depth:** Hubbard `scale` (log right-shift) vs FC/DMC `amplitude`
  (linear) — unify the depth axis, or keep as shape variants?
- **D5 — Arpeggio:** per-inst `arp.offsets` (Hubbard) vs global `arp_programs`
  library (FC) — unify?
- **D6 — Orderlist transpose semantics — ✅ RESOLVED 2026-07-19 (same day):**
  unified on STATED everywhere. FC migrated: transpose + voiceinc stated
  marks (both sticky; `^0` reset distinguishable from absent), the wrap
  pickup `+T` now DERIVED from the marks, trailing wrap commands serialized
  as the stated terminator's `+T` (they set the carried value — a trailing
  reset flipped 61 members until represented; C20-diagnosed). Composer
  unchanged (consumes parser-derived effectives). Gates: FC batch 2528 FULL
  = exact baseline; regression green. `+c` now has ONE semantics across
  DMC + FC. **PIECE 2 ✅ RESOLVED 2026-07-20 — stated-duration pattern
  rows:** `len=L`, FC's (fc_id, init_len) pattern materialization
  (probe: 18,147 phantom duplicate patterns = +41% pool, 97% of
  members) and DMC's `~intro` variants (10,343 slots, ~100% vol/instr
  carry) all dissolved into stated NoteRow values (present iff the
  stream states the command; absent = inherit, over wraps and pattern
  boundaries; init.voice_state seeds) + ONE shared resolution
  interpreter `src/usf/resolve.py` consumed by both composers and
  Layer-3. Gates: FC golden 2527/2528 byte-identical (the 1 diff =
  the predicted deep-chain member, re-verified FULL) + DMC family-1
  golden 5394/5394; recoveries Man_of_Noise + Love_Boat_Tune
  partial→FULL. Ledger C32 canonicalized (2×). D6 is now FULLY closed
  — orderlist AND pattern-row sticky state are stated everywhere.
  **Uready-review verdict (2026-07-20, focused):** the stated form
  landed as ONE representation with ZERO new cross-family divergence —
  `src/usf/resolve.py` is a single shared interpreter with two composer
  consumers + Layer-3 (Move-1-style factoring done up front, the C21
  lesson applied); NoteRow stated duration/instr semantics, Pattern
  `length=` omission, and `stated_marks` are reused same-form across FC
  + DMC; `InitVoice.dur_field` gained a second consumer (resolver seed
  beside Hubbard's duration-counter init — same §4.5 concept; the
  grammar comment is still Hubbard-phrased, one-line doc fix
  candidate). Single-consumer-by-nature (not forks): FC
  `stated_vmarks`/`stated_trail` (voiceinc doesn't exist in DMC), DMC
  `~i` (fallback-only) / `!k` / `*_cmd` flags (sectpos arrangement) /
  per-subtune instr seed / stated `vol=`. Two corpus-unhit latents on
  file: the C32 mid-list-repeat boundary note + project_dmc's 2SID
  seed-merge gap.

**Vindicated this review:** `freq_overrun` flipped single-consumer → REUSED (FC
standard + DMC v5) — a dimension that looked FC-specific is now shared; recorded
canonical in the [convergence ledger](the_convergence_ledger.md) C6. The reused
dimensions (freq_table, wave envelope, ADSR, `init.sid`) confirm the feature
space is sound; the divergences D1-D5 are the work.

### DMC v4 rounds-22-41 principles audit (2026-07-06)

Focused `/uready-review` (user-prompted: "did the fast recent DMC progress
cut principle corners?"). Answer: **largely no** — no §7 schema leak, no §8
engine-identity dispatch, leak scans clean, the C3 off-table gap from the
06-18 review is CLOSED (raw `freq_overrun` window deleted; per-instrument
`offtable_freq` records, median 1/file; redirect rows carry 0 USF bytes).
Typed additions in the window (`wave_table_pos`, `filter_mod`,
`InitVoice.dur_reload`, PSID clock/SID capture) audited SOUND with
carrier-gated emission + byte-identical defaults.

Criterion-5 feature accounting (new since 06-18):
- **`filter_mod`** — global cutoff-LFO contour reusing C1's `fp_step` token;
  single-consumer today, but the form is the SweepEnvelope/contour family →
  feeds divergence D2's reconciliation rather than forking it.
- **`wave_table_pos`** — §8-arrangement (editor-typed table placement);
  single-consumer, gate is load-bearing (emit only for off-table-sonified
  verbatim layouts). Watch: never widen "for uniformity".
- **sectpos fx_flags (`dur_cmd/instr_cmd/vol_cmd/soft_cmd`)** — stated-command
  arrangement, same class as `otrk_rcmd`; borderline-accepted. Watch: any
  new `*cmd` token needs a fresh principle review (§9.4 generalization risk).
- **`play_unit_repeat`** (C24) — genuine generalization of voice_tick +
  filter-tail repeats into one behavior list.

Pending decisions added for the human (also in ledger C7 note):
1. ~~`dual_hack`/`dual_hack_steps`~~ **RESOLVED 2026-07-06 (user-ratified):
   the filter_mod comparison was a category error (C10 recoverable-structure
   vs C19 wedge — each got its class's canonical form). Decision = C7-(b)
   document-and-minimize; renamed `dual_freq_generator`/`dual_generator_steps`
   (behavior naming was the one real defect); steps-derivability checked and
   unavailable; the "lift to musical form" direction recorded as a §8 trap in
   ledger C7. Taurus_02 re-verified FULL 86118/86118 under the new names.
2. **`Params.fields` escape surface** — ✅ **RESOLVED 2026-07-09** (`docs/
   dmc_composer_to_extract_plan.md` Phase A). `offtable_redirect='0'` described
   orig memory geometry (the one thing config fields must never describe) and
   `sectpos_shadow` was probe-result transport; both DELETED from the USF and
   replaced by a per-read `live(...)`/`at(...)` behavioral flag on `offtable_freq`
   (the composer re-derives its redirect boolean from the flags — ledger C7).
   Byte-identical across all 5401 family-1 members. (The blanket "migrate all CSV
   knobs probe→typed" framing stays WITHDRAWN per the dual-generator resolution:
   C19 wedge knobs' canonical home IS params; typing is for recoverable musical
   structure.)
3. **`glide_to` off-table-target parse quirk** — documented Move-1 debt
   (dynamic-byte-terminated sweep representation), must not silently persist.

Process gaps (why DMC is still not uready — C4/C6, not representation):
f1 closeout batch pending (~5019/5401); f2 stale at 2413/2889 (Jul 4 — all
rounds 22-41 landed f1; the shared-composer fixes make a f2 recovery sweep
due); regression portfolio derived at 4770 FULL, re-derive due; v4+family2
RE_NOTES.md frozen Jun 14 while residue lives only in project memory. Minor:
no static extract↔USF roundtrip checker for DMC (behavioral-only validation).

---

## Move 2 (digi fold) — landable any time

The one cleanup that doesn't depend on corpus richness: retire
`_emit_bitpack_bytes`, `_emit_combined_sid_bp`, `_emit_sid_bp` by
folding digi orchestration into the unified pipeline.

**Plan (one session):**

1. Add `load_addr=LOAD` parameter to `emit_asm`. Thread to the
   bitpack chain (which already supports it).
2. Write `_emit_digi_psid(model, usf, usf_dir, digi_subs)` — lifted
   from `_emit_combined_sid_bp`, but calling `emit_asm(model, usf,
   load_addr=music_load)` instead of `_emit_sid_bp` for music asm
   during iterative auto-pack against the digi dispatcher base.
3. `emit_sid_from_usf` calls `_emit_digi_psid` when digi subtunes
   are present; non-digi path unchanged.
4. Delete `_emit_bitpack_bytes`, `_emit_combined_sid_bp`,
   `_emit_sid_bp` once callers are gone.
5. Verify Chimera 4/4 + full regression byte-exact. Commit.

**Decision points (when starting):**
- Where does `_emit_digi_psid` live — `composer.py` (already 5700+
  lines) or a sibling module?
- Inline header build, or factor `_digi_psid_header`?

**Payoff:** ~100 lines of orchestration duplication retired; the
composer's only structural exception (digi orchestration) folds into
the unified pipeline.

---

## Move 1 (composer skeleton unification) — deferred

**Move 1 consumes the [convergence ledger](the_convergence_ledger.md).** Each
recurring sub-problem's canonical (idiomatic-for-us) solution is pre-decided
there as we migrate engines (a record, not a refactor); Move 1's job is to
factor the recorded **factor-candidates** into shared code. The decisions are
already made, so the unification is mechanical, not archaeological.

The structural work to fully close §8 in the composer is: **collapse
the engine-family-flavored branches in `emit_asm` into one
feature-parametric skeleton.** The lifts done in Phase B (every chunk
`FxNames`-parameterized) are the foundation; what's needed next is
designing the unified runtime structure.

Sub-moves that would compose Move 1, smallest first:

**D.1 — Unified note codec.** `pattern.encoding` is already a USF
feature; build a `read_next_note(voice_idx, pattern_state, names)`
helper that dispatches on encoding internally (atomic / pair /
cmd-stream / bitpack). Each skeleton migrates to call it. Pattern
reading stops being per-skeleton-specific. Multi-session (3–5).

**D.2 — Unified per-voice state conventions.** Pick X-indexed (like
bitpack) or per-voice-scalars (like simple-shape); migrate skeletons
one at a time to match. The choice affects assembled byte size, so
byte-exact verify is the constraint. Multi-session.

**D.3 — Unified player skeleton (init / play / proc_voice).** Once
data layouts converge (D.1 + D.2), the top-level dispatch logic can
be one parametric shape. Multi-session.

The order matters: D.1 is most isolated (touches pattern reading
only), D.2 is the most invasive (runtime conventions), D.3
finalizes.

**Honest scope:** many sessions, possibly months. Don't try to land
Move 1 as a single arc. Each sub-move should land independently with
byte-exact verify intact.

---

## Move-1-era considerations (NOT before)

### Audio-equivalence verdict (former ledger C15 — removed 2026-07-01 by user decision)

**Policy until Move 1: every SID always gets the STRICT write-stream match.**
This design must not be used or proposed during per-engine migration work.
When an idle-freewheel divergence blocks a member today, REPRODUCE the writes
(the core tenet permits reproducing the original's mechanism — DMC
`idle_wave`/resting-voice and family-4 `f4_idle_notes` are the precedents).
It may be *considered* (not presumed) around Move 1, when most/all engines are
uready, as a residue-classification tool. The full design, preserved from the
ledger:

- **The problem:** an engine writes `$D400-$D418` for a voice that produces **no
  sound** — most commonly a voice that hasn't played its first note (or has gone
  silent) and freewheels freq/pulse from the SID-file's **pre-loaded editor-leftover
  state** (the player's per-voice RAM vars the init doesn't clear). These writes are
  in the stream, so the strict `(reg,val)` compare flags a divergence — but they are
  **inaudible**, and our clean composer naturally writes *different* (cleaner) silent
  bytes than the original's leftover freewheel. This is the mid-song analog of "init
  bytes differ but state matches" (`docs/the_trichotomy.md` §5/§6.4 — the verdict
  already drops the inaudible init frame).
- **USF discipline regardless:** carrying provably-inaudible editor leftovers as USF
  params (GoatTracker V1 `idle_chip`, reverted bb7b097) stays a C7 anti-pattern.
  Under strict-match-always the line is: *derivable-mechanism reproduction in the
  COMPOSER* (fine, USF untouched) vs *opaque leftovers in USF* (not fine).
- **The design — audio-equivalence verdict** (a `compare` mode, not a USF
  field): walk both streams tracking each voice's ctrl; **drop freq/pulse writes to a
  voice while `(ctrl & $F0)==0`** (no waveform selected ⇒ silent — NOT `ctrl==0`: a
  voice in release `$10` is still audible and must be kept). Compare the filtered
  streams; all ctrl/gate/AD-SR/`$D415-$D418` writes are always kept. USF stays clean.
- **⚠️ SOUNDNESS GATE — phase reset at note-on (the test bit).** The drop is only
  sound if the idle voice's freq does NOT reach the audio. A freq write to a silent
  (`ctrl & $F0 == 0`) voice STILL advances the oscillator PHASE accumulator, and the
  phase at the next gate-on affects the waveform onset — UNLESS the engine resets the
  phase with the **test bit ($08)** at note-on. So the drop is sound IFF the engine
  sets the test bit when (re)gating a voice. GoatTracker **V1.5/player1**: new-note
  ctrl = `$09` (test+gate) → phase reset → idle freq PROVABLY inaudible → SOUND.
  GoatTracker **player2/gamemusic**: first wave-step ctrl has NO `$08` → phase NOT
  reset → idle freq IS audible → UNSOUND; must REPRODUCE the idle freq instead.
  NB this is NOT provable by rendering PCM and comparing: rebuilds are
  per-frame-exact, not cycle-exact, so audio differs on cycle timing (Trap B) even
  when correct. The proof is the test-bit analysis, not audio.
- **Mandatory guard (the one real hole) — hard-sync / ring-mod:** a silent voice N's
  oscillator feeds consumer voice `(N+1)%3` when that consumer has sync (bit1 `$02`)
  or ringmod (bit2 `$04`) set → N's **freq is then audible via the consumer** and the
  effect is in the oscillator domain (NOT in N's write stream → not self-guarding).
  Pre-scan the stream; if consumer C uses sync/ringmod, permanently protect source
  `(C+2)%3`'s freq (keep it). Pulse never feeds sync (still droppable). Validated:
  GoatTracker V1 *Memoires* uses sync — the guard correctly KEEPS its idle freq and
  exposed that the naive (guardless) filter was a FALSE PASS.
- **Self-guarding cases:** toneporta/slide from an idle voice — the held idle freq is
  the slide start, but after re-gate the voice is audible (ctrl≠0) so the slide's
  per-frame freq writes are KEPT and diverge if the start differed → caught.
- **Validation record:** designed + validated 2026-06-29 on GoatTracker V1
  (`tmp/audioeq_validate.py` / `audioeq_sample.py`, ephemeral). Immediate coverage
  was small (+1 in a 60-tune sample — most strict-partials have real audible bugs
  underneath the idle noise). If ever adopted it belongs in the shared comparator
  (`pipelines/hubbard/verify_cycle.py`) as a mode, not per-engine.

---

## Open principle question for the next visit

Even after D.1+D.2+D.3 land, the unified skeleton's `pattern.encoding`
parameter has values like 'bitpack' that may still map 1-to-1 to
engine families. Is that the forbidden `*Kind: int` shape (§7)
wearing a different name? Or is it a legitimate small enum (`atomic
| pair | cmd | bitpack`) with musically-meaningful values?

The principle doc's test: "does the model have to learn what each
value means from scratch, with no structure given by the
representation?"

The honest answer probably depends on the corpus: when 'bitpack'
maps to one engine family, it's a covert engine identifier; when
multiple engines use 'bitpack' encoding, it's a real format choice.
Another reason migrating more engines first matters — it clarifies
whether `pattern.encoding` is a real musical feature or an engine
artifact.

---

## Summary

- **Current state is honest in framing, not yet in structure.**
  `_needs_hubbard85_path` is dissolved; `emit_asm` is one entry. But
  the 5-way dispatch is engine-flavored.
- **Closing the remaining gap requires corpus richness.** Migrate
  DMC / GT2 / large-engine families first; the unified skeleton's
  shape depends on what those add.
- **Move 2 (digi fold) is independent of the above** and can land
  any time as a clean cleanup.
- **Move 1 sub-moves are sketched but deferred.** D.1 (unified note
  codec) is the natural starting point when this picks back up.
