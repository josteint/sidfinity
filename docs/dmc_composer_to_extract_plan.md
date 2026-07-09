# Plan — DMC family-1: relocate composer→extract, tidy USF representation, add readability

**Status:** proposed, not started. Verdict-relevant work (Phase A/B) + representation
tidy-ups (Phase C/D) + human-readability (Phase E). Author handoff doc — written so a
fresh session with only `CLAUDE.md` + `.claude/memory/` + the codebase can execute it.

---

## 0. TL;DR — what and why

A review of the DMC **family-1** pipeline (`pipelines/dmc/v4/`) asked one question:
*is anything currently done in the **composer** stage that would be better done in the
**extract** stage?* Six improvements came out of it. Exactly one is a genuine
stage-relocation that touches the verdict; the rest are representation / readability
clean-ups.

| # | Change | Kind | Risk |
|---|---|---|---|
| 1 | Eliminate `offtable_redirect` + `sectpos_shadow`; carry the off-table serving decision **per-read** | composer→extract relocation (fixes a Core-Tenet leak) | **high** (verdict-relevant) |
| 2 | Structure `otrk_rcmd` as **orderlist content** instead of a params bitmask | representation (data→extract, derivation stays composer) | medium (verdict-relevant) |
| 3 | Type `cia_period` + `play_repeat` as a top-level **environment** field | representation only | low |
| 4 | Type `slide_phase` as **init priming** | representation only | low |
| 5 | Rename cryptic USF keywords (functional names, never register-named) | representation (ML tokens + readability) | low |
| 6 | Emit `;` **comment lines** in generated USF (flagship: derived instrument fingerprint) | writer-only, human readability | very low |

The unifying safety idea: **#1–#5 are *carrier* refactors — they move where information
lives without changing what the composer emits — so "nothing broke" is proven by the
rebuilt `.sid` being byte-identical (MD5) to a pre-change baseline.** Byte-identity ⇒
identical `$D400–$D418` write-stream ⇒ identical verdict, which is stronger and cheaper
than re-verifying. #6 never reaches the composer, so its `.sid` is trivially identical.

---

## 1. Required reading + the decision rule

Before touching representation, re-read these IN FULL (they are load-bearing; a slogan
drops the discipline that does the work):

1. **The Core Tenet** — `CLAUDE.md` top section. Verdict = the `$D400–$D418` write-log,
   not the engine code. Corollary that drives #1: *per-engine config fields parametrise
   differences between engines' write-log streams; **they never describe HVSC's code
   layout.***
2. **The Principles** — `docs/usf_representation_principle.md`. §7 forbidden shape
   (an index into an engine-defined library); §8 the composer must not pick which 6502
   to emit by sniffing engine identity/geometry.
3. **The Trichotomy** — `docs/sid_init_report.md`. init = reset (composer, invisible) +
   priming (typed USF) + **environment** (top-level USF field — drives #3) + bookkeeping
   (out of USF).
4. **The Convergence Ledger** — `docs/convergence_ledger.md`. Entry **C19** (canonicalized
   10×) is the exact decision rule; entry **C7** already flags #1's two fields as open.

**The decision rule (C19, verbatim intent):** *EXTRACT-only when the lever changes a
derived musical value; COMPOSER param when it changes a write-stream TIMING.* Combine
with the Core-Tenet corollary to get the two-axis test used below.

### The two-axis test (why only #1 truly relocates)

Every per-member lever is judged on two independent axes:

- **Axis A — can it leave the composer?** Only if, once extract resolves the difference
  into content, the composer has *nothing member-specific left to do*. If the composer
  must emit different 6502 (program a timer, repeat the play body, change a gate-off,
  re-assert `$D418`) the action is irreducible → it **stays** a composer param.
- **Axis B — is it a leak?** Does the value serialized in USF *describe HVSC memory/code
  geometry*? If yes it must not be in USF at all.

Result: the C19 timing wedges fail A (can't leave) but pass B (legitimate behavioral
params). `cia_period`/`play_repeat` fail A, pass B (fine where they are; only representation
can be tidied — #3). `offtable_redirect` fails **both** (relocatable *and* a geometry leak)
— it is the one real relocation; `sectpos_shadow` rides with it because the two are
entangled through the same geometry decision.

> **Every one of these params is already computed at extract.** "Extract vs composer" is
> never about where the value is *produced* — it is about who must *act* on it, and whether
> the serialized form is a leak.

---

## 2. Architecture context a fresh session needs

### 2.1 Where things live (DMC family-1 = "v4")

| File | Role |
|---|---|
| `pipelines/dmc/v4/config.py` | `DMCV4Config` — the **extract-path** config. Its fields are **extract-only** (base, operand sites `op_*`, table `*_addr`, `forced_subtune`, `data_post_init`, `post_init_state`, `extra_params`); they never reach USF except via `extra_params`/derived model fields. |
| `pipelines/dmc/v4/factory.py` | `dmc_v4_config(sid_path)` / `dmc_v4_config_2sid(...)` — probes the binary and builds the config (all the `_*_probe` functions). |
| `pipelines/dmc/v4/extract/engine_model.py` | binary → `DmcModel`. **Sets `sectpos_shadow`/`offtable_redirect` here** (see §2.4). `_canon_state_geometry` at line ~1468. |
| `pipelines/dmc/v4/extract/to_usf.py` | `DmcModel` → `UsfFile` (`model_to_usf`, `write_dmc_usf`, `merge_2sid_usf`). Positive prior art: `filter_mod` is *popped* out of `extra_params` into a typed block (lines ~283–291). |
| `pipelines/dmc/composer_asm.py` | **the DMC composer** (USF → 6502 → PSID). `build_dmc_sid(usf)` (~2408), `build_dmc_2sid_sid(usf)` (~2348). `_Model` distils the USF (~424). |
| `src/usf/types.py` | shared dataclasses: `Instrument` (589; `offtable_freq: list[tuple]` @589), `Orderlist` (91), `Params` (749), `InitState` (740), `InitSid` (729), `NoteRow` (74), `MusicSubtune` (196), top-level `offtable_vibdepth` (~1007). |
| `src/usf/grammar.lark` | grammar. `params_block` is generic `CNAME : value`. **Comments already supported:** line ~591 `COMMENT: ";" /[^\n]*/` + `%ignore COMMENT`. |
| `src/usf/writer.py` | `_write_params` (~100) + `_write_*` helpers (where #6 lands). |

Build path (single-chip): `dmc_v4_config(path)` → `write_dmc_usf(cfg, out_dir)` →
read `.usf` → `build_dmc_sid(usf)` → PSID bytes. Wrapped by
`tools/dmc_build_one.py <path> --verify --localize`.

### 2.2 `params.fields` IS serialized and ML-visible

The DMC "composer params" are **not** a side-channel — they are `usf.params.fields`,
serialized by `writer._write_params` under `params { ... }` (grammar `params_block`) and
read back by the composer via `usf.params.fields.get(...)`. The `.usf` file *is* the ML
training data. Therefore a mechanism/geometry flag sitting in `params` is itself a mild
§7/§8 concern, and "move to extract" concretely means **resolve the difference into
geometry-free / musical content so the composer needs no descriptor bit.**

### 2.3 Full composer-param classification (the review's output)

Params read by `composer_asm.py` via `usf.params.fields.get(...)` and their verdict:

| Param(s) | Changes | Verdict |
|---|---|---|
| `hold_gateoff`, `rest_effects`, `pw_hi_const`, `hr_patch`, `hr_test_init`, `pw_dir_persist`, `play_phases`, `notestart_arm`, `fx_entry`, `d418_every_play`, `d418_filter_tail`, `play_unit_repeat`, `dual_freq_generator`, `dual_gen_steps`, `cymbal_onset`, `cymbal_burst`, `vib_ramp`, `hard_restart` | write-stream **timing / mechanism** (C19 wedges) | **stays composer** (moving them = baking mechanism into USF = forbidden shape) |
| `cia_period`, `play_repeat` | **environment / rate** | stays composer-consumed; **#3** re-types the carrier only |
| `slide_phase` | runtime phase **priming** | stays composer-consumed; **#4** re-types the carrier |
| `otrk_pad`/`otrk_period`/`otrk_rcmd`/`otrk_legacy` | **arrangement** → composer derives byte-offsets | **#2**: structure the data; derivation stays composer |
| `sectpos_shadow` | proxy for "a read hits the sector-position window" | **#1**: dissolve |
| `offtable_redirect` | "original state geometry is non-canonical" (**layout leak**) | **#1**: dissolve |

### 2.4 The off-table serving machinery (critical for #1)

When a wave/effect step rebases a freq-table index (`wftab[pos] + curnote`) past the
96-entry freq table, the read overshoots `freqlo/freqhi` into the engine's live STATE
region and the byte read gets **sonified as a frequency**. Three serving mechanisms exist,
selected in `composer_asm.py` (~1515):

```python
otmap = (DMC_OFFTABLE_STATE if m.offtable_redirect else []) \
    + ([DMC_SECTPOS_ROW] if sectpos_on else []) \
    + ([DMC_WAVEPOS_ROW] if m.wavepos_layout else [])
```

- `DMC_OFFTABLE_STATE` (composer_asm ~73): `[(orig_addr, composer_label, n)]` map — reads
  landing on tracked live vars (transp/fbl/fbh/accl/dur/durrel/glide/…) are served **live**
  from the composer's own byte-identical variable via `_gen_offtable_redirect` (~241).
- `DMC_SECTPOS_ROW = (0x1729,'sectpos',3)` (~229) — a read on the per-voice sector-position
  counter; served by a live `sectpos,x` shadow whose per-row values come from row command
  flags (`dcmd`/`icmd`/`vcmd`/`softcmd`).
- `DMC_WAVEPOS_ROW = (0x177A,'wavepos',3)` (~238) — a read on the live wave position.

**How each discriminator is obtained in `_Model.__init__` (~424):**
```python
self.sectpos            = params['sectpos_shadow'] == '1'      # ~432  ← params BIT
self.offtable_redirect  = params.get('offtable_redirect','1')!='0'  # ~438  ← params BIT
self.wavepos_layout     = all(i.wave_table_pos is not None ...)     # ~448  ← DERIVED from content
```
`wavepos_layout` is already the clean pattern (derived from per-instrument
`wave_table_pos`); the other two are leaky params bits — that is the inconsistency #1 fixes.

**Where the two bits are SET (extract, `engine_model.py` ~1008–1037):**
```python
canon_geom = _canon_state_geometry(mem, cfg)            # static opcode probe of the ORIG
...
if canon_geom and <any offtable_freq idx in _SECTPOS_IDX>:  m.extra_params['sectpos_shadow']='1'
if not canon_geom and <any instrument has offtable_freq>:   m.extra_params['offtable_redirect']='0'
```
So the decision is **already extract's**; today it is merely *published* as an ML-visible
geometry bit and *re-read* by the composer.

**The member-global window-layout flip (the delicate part), `composer_asm.py` ~1367–1384:**
`offtable_redirect` also chooses the *window layout* — canon members co-locate the live
`spd`/`mvol`/`sidoff`/`fbit`/`fmask` structures INSIDE the overrun window at positions
6..16; non-canon members place pure static-capture bytes there and put the live structures
OUTSIDE. This is why a naive per-read reduction can leave an **inert binary-data
difference** at window pos 6..16 for corner members (see the #1 known risk in §3).

### 2.5 Multi-SID naming (drives #5's register→function rename)

For 2SID/3SID members the composer standardises chip bases: chip 2 = `$D420`, chip 3 =
`$D440` (`composer_asm.py` ~2403; register-word rewrite ~657). So `$D418` is really three
registers (`$D418`/`$D438`/`$D458`). A key named `d418_*` is therefore ambiguous under
multi-chip → #5 renames it to a functional name (`master_vol_*`), which removes the
ambiguity *and* is more principled ($D418 names chip geometry; "master volume" names the
musical role).

### 2.6 Cross-engine blast radius (shared schema)

`offtable_freq` (used by **FC standard, DMC v5, GoatTracker V1**), `Orderlist`, `init`,
`params` are **shared**. So #1–#4 touch types/grammar/reader/writer that other engines
also traverse. Every schema change must be **additive + optional + default-to-current**
so those engines stay byte-identical (proven by their golden-diffs + full regression).

---

## 3. The six improvements — rationale, locations, design, invariant

### #1 — per-read off-table serving (composer→extract; the only leak fix)

- **Why:** `offtable_redirect='0'` literally serializes "the original's state block is not
  at the canon offset" — a statement about HVSC memory geometry in ML-visible USF (Core
  Tenet corollary violation; Ledger C7 open item). `sectpos_shadow` is a redundant proxy
  entangled with the same geometry decision.
- **Design:** replace both member-global bits with a **per-read behavioral property** —
  each off-table read is `static` (serve the captured `lo/hi`) or `live` (reproduce from
  the composer's own equivalent var, looked up by index from the existing map). This is a
  2-value *behavioral* property ("this sonified byte varies vs is fixed"), **not** a
  geometry bit and **not** an engine-address index (stays clear of §7). Follow the
  `wavepos_layout` template (§2.4): the DMC composer derives the map application per-read;
  the serialized signal is behavioral. Keep the field **optional on the shared
  `offtable_freq` record** so FC/v5/GT V1 are untouched (§2.6).
- **Extract (`engine_model.py`):** set each read's mode from the `canon_geom` probe +
  index sets it already computes; **stop** emitting `offtable_redirect`/`sectpos_shadow`
  into `extra_params`. Keep sectpos row-flags (`dcmd`/`icmd`/`vcmd`/`softcmd`) exactly as
  today (they are the arrangement content the shadow consumes).
- **Composer (`composer_asm.py`):** derive `otmap` + the window-layout choice as functions
  of the per-read modes; delete the `params.fields.get('sectpos_shadow'/'offtable_redirect')`
  reads (~432, ~438).
- **INVARIANT:** for every off-table read the **served value is identical to today** ⇒
  the write-stream is identical for every member (canon and non-canon).
- **AS-BUILT derivation (the byte-identity-preserving form):** the composer's
  `redirect_on` is `not (any STATIC read whose idx ∈ live-served set)`. Rationale: the
  redirect/co-location only *affects the write stream* for reads at a live-served idx, so
  the only member that must turn it OFF is the **non-canon** one — uniquely detectable as
  a `at(...)` read sitting at a live-served idx (its geometry moved the state elsewhere, so
  that byte is unrelated code/data). Everyone else — canon (has `live(...)` reads), reads
  only at fixed positions, or no reads — keeps it ON, **byte-identical to the old default**.
  The live-served idx set = `DMC_OFFTABLE_STATE ∪ sectpos ∪ wavepos` rows PLUS the
  co-located `spd`/`mvol` slots (hi 111/112, lo 207/208); single source of truth =
  `composer_asm.offtable_live_idx()`, shared by extract's `live` stamp. A first (wrong)
  attempt used `redirect_on = (not has_reads) or has_live`, which dropped the (dead)
  redirect routine for ~429 canon members that read only the track-ptr region — **write-
  stream-identical but not byte-identical** (999 B smaller `.sid`). The classifier initially
  mis-flagged those as regressions (it compared legacy `match` against `len`, which are on
  different bases); the correct inertness test is `first_diff is None AND len_a == len_b`.

### #2 — `otrk_rcmd` → orderlist structure (data extract-side; derivation stays composer)

- **Why:** `otrk_rcmd_s{song}_v{voice}` (`to_usf.py` ~215–239) is genuine *arrangement*
  (where redundant transpose commands are notated) but encoded as an opaque per-voice
  **bitmask** in the params junk-drawer — the ML sees an integer, not structure (§8).
- **Design:** express the redundant-command placement as structure alongside
  `Orderlist.transposes` (per-entry marker). The **byte-offset derivation MUST stay in the
  composer** — storing the offsets themselves would be the C7 forbidden shape (engine
  byte positions). The composer keeps deriving offsets; it just reads structured marks
  instead of a bitmask.
- **Coupling to watch:** the otrk offsets feed the off-table sonification of the track
  counter `$1726`, adjacent to the sector-position counter `$1729` that #1 handles.
  Sequence #2 right after #1 and re-run the golden-diff so any interaction surfaces.
- **INVARIANT:** derived byte-offsets identical ⇒ composer output identical ⇒ MD5-identical.

### #3 — type `cia_period` + `play_repeat` as a top-level environment field

- **Why:** these are the Trichotomy's *environment* category (§4.3), meant to be a typed
  top-level USF field, not `params` keys. **NOT a stage move** — the composer still
  programs the CIA latch / emits N× play (irreducible mechanism).
- **Design:** add an optional top-level env field (e.g. `playback_rate` / `cia_period`);
  DMC extract writes it, DMC composer reads it there; other engines default absent (§2.6).

### #4 — type `slide_phase` as init priming

- **Why:** `slide_phase` is runtime phase priming (Trichotomy `voice_state`, §4.5), not a
  generic knob. **NOT a stage move.**
- **Design:** move it into a typed `init` priming field; composer reads it from there.

### #5 — rename cryptic keywords (functional, never register-named)

- **Why:** keys like `otrk_rcmd`, `dcmd`, `hr_patch`, `d418_filter_tail` are opaque at a
  glance and (for `d418_*`) ambiguous under 2SID/3SID (§2.5). These are also ML tokens, so
  clearer names help the model, not just the human.
- **Rules:** spell out domain abbreviations (`pw`→`pulsewidth`, `hr`→`hardrestart`,
  `vib`→`vibrato`, `otrk`→`orderlist`); **never name by register** — `d418`→`master_vol`.
  Apply the rename **atomically** (extract emit + composer read in one commit). Rename
  **only survivors** of #1/#2 (skip anything already deleted). See rename table, Appendix B.
- **Check at implementation:** confirm row `fx_flags` (`dcmd`/`icmd`/`vcmd`) are generic
  grammar strings (then no grammar change) vs tokens (then update grammar too). The
  grammar's `params_block` is generic `CNAME`, so param-key renames need no grammar change.

### #6 — `;` comments in generated USF (writer-only; human readability)

- **Why:** make generated `.usf` self-explanatory. Grammar already `%ignore`s `;` comments
  (§2.1), so this is **writer-only** and cannot break round-trips.
- **Flagship — derived instrument fingerprint:** a one-line `;` comment per instrument,
  a **pure function of the instrument's USF fields** (regenerated each write → never
  drifts), written in **temporal/musical order** (attack → body → modulation → release):
  - waveform (pulse/saw/tri/noise/combined; "PWM sweep" if pulse+pwm) — from `waveform`;
  - articulation (plucked/sustained/stab) — from `adsr`;
  - pitch behavior (drum / arpeggio / static tone / noise hit) — from `wave_freq`+`effects`;
  - modulation (vibrato w/ onset, portamento, filtered) — from `vibrato`/`freq_slide`/`filter_prog`.
  - e.g. `instrument i4 { ; noise-attack drum — percussive, no melodic pitch`
- **Rules:** describe musical *role* only, **never engine addresses** (a comment naming
  `$1726` re-leaks what the schema keeps out). Reference chips by index, not register.
  Keep to derivable facts (avoid guessing "bass" vs "lead" unless marked heuristic).

---

## 4. Safety methodology

### Invariants — the definition of "not broken" (hold at every commit)

- **INV-1 (byte-identity):** for #1–#5, every member in the golden set rebuilds to an
  MD5-identical `.sid` vs baseline. Any diff is stop-the-line (not an "improvement"). The
  sole sanctioned exception is the #1 inert-window-byte corner (§3), which passes on
  **write-stream identity** instead — verified per member with `find_first_divergence`.
- **INV-2 (regression green):** `tools/regression.py` (all families) passes before each
  commit — mandatory because every step touches `src/usf/*` or shared composer.
- **INV-3 (additive/optional schema):** each schema change defaults to current behavior so
  FC / Hubbard / companion / DMC v5 / GT V1 stay byte-identical (verified via their
  golden-diffs + regression).
- **INV-4 (USF sync):** update `types.py` + `grammar.lark` + reader + `writer.py` +
  `composer_asm.py` + `extract/to_usf.py` + `docs/usf_format.md` + tests **together**
  (memory `feedback_usf_sync`).
- **INV-5 (round-trip):** generated `.usf` reparses; read→write→read is stable (modulo
  comments) after every writer/schema change.
- **INV-6 (real-player ear-test):** ear-test 2–3 members in `sidplayfp` after verdict-
  relevant phases (py65/writelog miss dispatch bugs; memory `feedback_py65_misses_dispatch_bugs`).
- **INV-7 (living-doc referential integrity):** whenever a keyword/field/param is
  **removed or renamed**, grep the whole repo — `docs/` (esp. `convergence_ledger.md`,
  `refactor_1_remaining.md`, per-topic plans), `.claude/memory/*`, `pipelines/**/RE_NOTES.md`,
  `CLAUDE.md` — and update every reference *in the same commit*, so no living document ever
  names a token that no longer exists. **Distinguish carefully:** a removed *param*
  (`offtable_redirect`) is not the same token as a same-named *function*
  (`_gen_offtable_redirect`, unchanged) — update the former, keep the latter. For a removed
  field, rewrite references to "resolved → `<new form>`" (preserve history); for a rename
  (#5), substitute the new name.

### Why byte-identity is the right gate

`.sid` bytes are a deterministic function of the pipeline; identical bytes ⇒ identical
`$D400–$D418` stream ⇒ identical verdict for every subtune, FULL or partial. It catches
even inaudible changes (conservative) and needs no per-subtune verify. It is the primary
gate for #1–#5. For #6 the composer never sees comments, so `.sid` MD5 is trivially
unchanged and the gate is INV-5 (round-trip).

### The golden-diff harness (build first — Phase 0)

`tools/golden_sid_diff.py`:
- `--capture`: for a member list, run the full pipeline at the **current** commit
  (`extract → USF → compose → SID`) and record `{member: (sid_md5, verify_status,
  n_subtunes)}` to a baseline JSON (checked in under `tmp/` per memory `feedback_repo_tmp_dir`).
- default: rebuild the same list at current code, diff MD5 vs baseline. For any mismatch,
  auto-run `tools/find_first_divergence.py ORIG REBUILD --subtune N` and classify
  **write-stream-identical (inert)** vs **write-stream-divergent (regression)**.
- resume-safe; honors `src/code_fingerprint.py` code_hash where practical.

This one harness is the workhorse for #1–#5. (Tooling reflex, CLAUDE.md: <1 hr to build;
add to `tools/INVESTIGATION_BACKLOG.md`.)

---

## 5. Phased checklist

> Iterate on the stratified golden set for speed; run the **full** `dmc_family_batch.py`
> only at the closeout of verdict-relevant phases (memory: don't full-batch every
> experiment). Full-batch is ~1 hr; run it in background via the harness
> (`feedback_background_jobs_harness`), never a self-matching `pgrep` waiter
> (`feedback_no_self_matching_waiters`).

### Phase 0 — safety harness & baseline (no product changes)

- [ ] Build `tools/golden_sid_diff.py` (`--capture` + diff + write-stream fallback classify).
- [ ] Assemble and freeze the **golden set** (Appendix C): portfolio + **all** off-table
      carriers + otrk/cia/slide carriers + named canaries + ~100 random FULL + cross-engine
      samples + ≥1 each 2SID/3SID.
- [ ] `golden_sid_diff.py --capture` → commit the baseline JSON to `tmp/`.

### Phase A — #1 (lead; verdict-relevant)

- [ ] Design note: fix the per-read `live/static` representation on `offtable_freq`
      (optional, default = other engines' current behavior). State the served-value
      invariant + the window-layout reproduction rule (§3 KNOWN RISK).
- [ ] Extract: set per-read mode from `canon_geom` + index sets; stop emitting the two bits.
- [ ] Composer: derive `otmap` + window layout from per-read modes; delete ~432 + ~438 reads.
- [ ] INV-4 sync (types/grammar/reader/writer/docs/tests).
- [ ] **Gate:** `golden_sid_diff.py` over the full golden set → zero `.sid` diffs
      (incl. FC/v5/GT V1/Hubbard/companion = INV-3). Any diff → classify; only the
      inert-window corner (§3) may pass on write-stream identity, documented per member.
- [ ] Confirmatory: `regression.py` green; `pattern_stream_verify.py --engine dmc_v4`;
      full `dmc_family_batch.py` FULL count ≥ baseline; INV-6 ear-test.
- [ ] Commit (no `Co-Authored-By`). Update Ledger C7-note → `offtable_redirect`/
      `sectpos_shadow` **resolved**; cross-ref C6/C11.

### Phase B — #2 — ⛔ DEFERRED 2026-07-09 (re-anchor overturned the easy move)

Occurrence census over 249 members: `otrk_period` 90%, `otrk_pad` 55%, `otrk_rcmd`
25%, `otrk_legacy` 6%. The field the review wanted to structure (`otrk_rcmd`) is a
minority; the DOMINANT field `otrk_period` is a **loop-unroll artifact** and
`otrk_legacy` is a **residue flag** — both pure byte-counter-reconstruction MECHANISM,
not musical content. Moving them onto the *musical* `Orderlist` would stamp mechanism
onto ~90% of orderlists = the inverse of #1's fix (mechanism masquerading as content).
By the ledger C19 rule (a lever that changes a write-stream value → composer param),
`otrk`'s canonical home IS params — where it already lives. **No net-positive
representation change available at Phase-B scope.**

The genuinely clean fix is a separate, larger task: **de-unroll the DMC orderlist**
(store the physical `period` entries + loop instead of the loop-unrolled walk) — then
`period`/`legacy` largely dissolve and redundant marks become per-entry. That rewrites
DMC orderlist extract + the composer walk (verdict-relevant), so it is tracked as its
own future item, NOT folded into this readability pass. `otrk_*` keys are renamed in
place by #5 (Phase D) for legibility; the structural move waits for the de-unroll task.

### Phase C — #3 + #4 (representation only)

- [ ] #3: optional top-level env field; DMC extract writes, composer reads; drop `params` keys.
- [ ] #4: `slide_phase` → typed init priming; composer reads it there.
- [ ] INV-4 sync (both).
- [ ] **Gate:** `golden_sid_diff.py` → zero diffs; `regression.py` green. Commit (one each).

### Phase D — #5 (rename)

- [ ] Apply Appendix B renames atomically (extract emit + composer read, same commit),
      survivors only; `d418_*`→`master_vol_*`; verify `fx_flags` grammar handling.
- [ ] **Gate:** `golden_sid_diff.py` → zero `.sid` diffs (renames don't reach composer
      output); `.usf` reparses (INV-5); `regression.py` green. Commit.

### Phase E — #6 (comments; writer-only)

- [ ] Writer emits `;` role comments per block; flagship instrument fingerprint (derived,
      temporal order, musical role only, chip-by-index).
- [ ] **Gate:** `.sid` MD5 unchanged for the whole golden set; every generated `.usf`
      reparses + round-trips (INV-5); `regression.py` green. Commit.

### Phase F — closeout

- [ ] Re-derive the DMC v4 regression portfolio (`tools/select_regression_portfolio.py
      --engine dmc_v4`) — #1 changed the off-table feature dimension.
- [ ] Full `dmc_family_batch.py` + `dmc_v5`/FC/GT V1 batches (or samples) confirm no family
      regressed; `regression.py` green.
- [ ] Update `docs/usf_format.md`; memories (`project_dmc.md`, off-table memory, `MEMORY.md`);
      Ledger. Mass-write refreshed FULL `.usf`/`.sid` (code_hash-gated).

---

## 6. Appendices

### Appendix A — extract-only config fields (already correct; do NOT touch)

`DMCV4Config` fields consumed at extract and never serialized (except via derived model
content): `base`, `op_instr/op_wavectrl/op_wavefreq/op_filtdef/op_tunetab/op_secp_lo/
op_secp_hi`, `freq_lo_addr/freq_hi_addr/vibdepth_addr/d417_shadow_addr`,
`curnote_addr/gatemask_addr/dual_parity_addr`, `track_loop_target`, `loop_reset_pos`,
`sector_format`, `data_post_init`, `forced_subtune`, `post_init_state`, and
`extra_params['pw_bound_shift']` (popped before USF). These are the model of a clean
extract-only knob — leave them.

### Appendix B — rename table (#5; apply to survivors only)

| Current | Suggested | Note |
|---|---|---|
| `dcmd` / `icmd` / `vcmd` (row flags) | `dur_cmd` / `instr_cmd` / `vol_cmd` | single letters opaque |
| `otrk_rcmd` | `orderlist_redundant_transpose_marks` | (likely dissolved by #2) |
| `otrk_pad` / `otrk_period` / `otrk_legacy` | `orderlist_bytepos_pad` / `_period` / `_approx` | (likely dissolved by #2) |
| `hr_patch` | `hardrestart_smc_variant` | `hr` collides with `hard_restart` |
| `hr_test_init` | `hardrestart_test_init` | spell out `hr` |
| `pw_hi_const` | `pulsewidth_hi_const` | |
| `pw_dir_persist` | `pulsewidth_dir_persist` | |
| `fx_entry` | `effect_entry_variant` | "entry" of what |
| `notestart_arm` | `noteinit_deferred` | name the behavior (C23) |
| `d418_every_play` | `master_vol_every_play` | register→function; multi-SID safe |
| `d418_filter_tail` | `master_vol_reassert_filter_tail` | register→function; multi-SID safe |
| `dual_gen_steps` | `dual_generator_steps` | minor |

Keep already-clear keys as-is: `hold_gateoff`, `rest_effects`, `cymbal_onset`, `vib_ramp`
(→`vibrato_ramp` optional), `cia_period`, `play_repeat`, `play_phases`, `slide_phase`.

### Appendix C — golden-set definition (Phase 0)

- DMC v4 regression portfolio (`select_regression_portfolio.py --engine dmc_v4`).
- **All** current off-table carriers: fresh-build members emitting `offtable_freq` /
  `offtable_vibdepth`, or setting `offtable_redirect` / `sectpos_shadow`, plus all
  `wave_table_pos` (wavepos) carriers — this is #1's exact blast radius; cover exhaustively.
- `otrk_*` carriers (#2); `cia_period`/`play_repeat` carriers (#3); `slide_phase` carriers (#4).
- Named ledger canaries: Sans_intro, Groove/Bakewell_Dwayne, 98_Mix, Viiskyt_vuotta_humppaa,
  Attacker, Alien_WOW/Hardcore, Bladeswede, Cool_Musax, Staring_at_the_Ceiling, Taurus_02,
  Stryyker, SilverFox/Seaside_99, Aomeba/20_Years_of_NOP, Apocalypsa, Grave_Story_intro.
- ~100 random **FULL** members (catches accidental common-path changes).
- Cross-engine samples: FC standard, DMC v5, GoatTracker V1, Hubbard, companion (INV-3).
- ≥1 known 2SID and ≥1 3SID member (multi-chip naming path).

Enumerate carriers from a fresh family batch (coverage source of truth per CLAUDE.md), not
from stored `.usf`. Existing `.usf` files may be grepped only as an enrichment *hint*.

### Appendix D — commands

```bash
source src/env.sh
# build+verify one member
python3 tools/dmc_build_one.py MUSICIANS/S/SilverFox/Seaside_99.sid --verify --localize
# localize a divergence
python3 tools/find_first_divergence.py ORIG.sid REBUILD.sid --subtune N
# roundtrip pattern-stream region
python3 tools/pattern_stream_verify.py --engine dmc_v4
# residue triage / carrier census
python3 tools/divergence_census.py --engine dmc_v4 --results tmp/<batch>.jsonl --partials
# regression portfolio (tier-1) / full family batch (tier-2)
python3 tools/select_regression_portfolio.py --engine dmc_v4
python3 tools/dmc_family_batch.py          # ~1 hr; run backgrounded
# full pipeline regression (all families) — the commit gate
python3 tools/regression.py
```

### Appendix E — do-not-move list (bounds the scope honestly)

The C19 timing wedges (`hold_gateoff`, `rest_effects`, `pw_hi_const`, `hr_patch`,
`hr_test_init`, `pw_dir_persist`, `play_phases`, `notestart_arm`, `fx_entry`,
`d418_every_play`, `d418_filter_tail`, `play_unit_repeat`, `dual_freq_generator`,
`dual_gen_steps`, `cymbal_*`, `vib_ramp`, `hard_restart`) change **write-stream timing**
and are the sanctioned behavioral-param category (Core Tenet). Do **not** relocate them to
extract — that would encode engine mechanism as USF content (the forbidden shape). They may
be *renamed* (#5) but not moved. `cia_period`/`play_repeat`/`slide_phase` stay
composer-*consumed*; #3/#4 only re-type their carrier.
