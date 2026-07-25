# Plan: replace py65 observation with a native, ground-truth mechanism

**Status (2026-07-25): Phase 0 DONE — architecture DECIDED; Phase 1 DONE.**
The Phase-0 design-space survey + decision live in
[`siddump_native_capture_decision.md`](siddump_native_capture_decision.md),
which SUPERSEDES this file's "Candidate architecture (STRAWMAN)" section:
declarative siddump flags over observe-only overlay taps (A-first); a thin
in-process binding over the same taps is a deferred escalation; VICE-monitor /
DBI / record-then-query rejected. Phase 1 shipped `--reinit-snapshot` and
migrated the DMC ghost sim (`_reinit_windows_via_siddump`; py65 path deleted;
gates: byte-identical windows + For_Party FULL; false-fire lesson = ledger
C36). Phase 2 STARTED: `--pc-watch` (executed-PC events with A/X/Y +
play-index + RAM windows) shipped and `_observe_dispatch` (C31 compilation
dispatch) migrated, py65 loop deleted — spec-identical on all 5 observe-path
members; `_observe_play_phases` (canon C18) migrated (204-carrier A/B,
py65 twin deleted). ASSESSED + LEFT ON py65: `_postinit_window` (a
simulation, 2c), and the DMC MULTI-SID trio (`_observe_play_phases_chip` /
`multisid_active_chips` / `_observe_player_bases`, 2d — not divergence-prone
or slow, and the per-chip --pc-watch anchor breaks cross-chip phase
alignment for complementary schedules: Cow_Anus_Fucked FULL->PARTIAL,
reverted). Remaining DMC candidate: `_observe_play_phases_writes`
(fallback-order swap onto its existing pctrace twin).

**Phase 3 DONE (audit, 2026-07-25): the CORRECTNESS goal is MET — no
divergence-driven migration remains anywhere.** A full classification of the
~32 non-DMC py65 sites (their verdicts recorded per-site) found: every
divergence-prone (C29-class) site is in `pipelines/dmc/` and is already
handled; every non-DMC site is either (a) an init-only read of image /
init-written / init-copied bytes on a clean engine (not divergence-prone,
correctly on py65 per the ground-truth rule), (b) a standalone dev/analysis
tool, or (c) a SIMULATION that must NOT migrate — the audit surfaced the
second known instance, MA `heterogeneous._landing_memory` (the twin of
`_postinit_window`), and it is now docstring-guarded BEFORE anyone tried.
The ONLY sites tripping the rule do so on the **slow** axis alone — three
clean-engine, low-volume, non-batched sims (`jay_derrett._run_play_capture`
~2000 frames, `jay_derrett/type_b` ~1000, `hubbard/inst_program.capture`
~1500) — all zero-correctness-benefit, low-ROI; deferred (do only if a speed
need appears). Tooling-hygiene follow-ups the audit noted (not part of this
initiative): `src/usf/audit.py` duplicates `tools/voice_writelog.py`,
`src/hubbard_emu.verify_against_py65` validates a proxy against a proxy, and
`jay_derrett/build.capture_writes_via_py65` is now test-only dead weight —
candidates for deletion/consolidation.

The sections below are kept for the inventory, the phased
path, and the gating disciplines. Read `feedback_ground_truth.md` first.

## Phase 0 — survey the design space FIRST (gates everything; do not build until done)

This is a well-studied problem — program observability / dynamic instrumentation
/ emulator introspection — so learn from the prior art before committing to an
architecture. The initial sketch below (patch libsidplayfp's overlay → add
siddump CLI flags → maybe a Python binding) is ONE point in a large space and
should be evaluated against, not assumed.

**Questions the research must answer:**
- How do mature emulators / VMs expose execution introspection to host tooling
  WITHOUT (a) perturbing behaviour (the observer effect — our non-negotiable
  ground-truth constraint) and (b) paying per-event IPC? Prior art to study:
  **VICE's binary monitor protocol** (same C64 domain — start here), **QEMU**'s
  TCG plugin API + gdbstub, **Bochs** instrumentation hooks, **DTrace / eBPF**
  (the canonical "safe, compiled, observe-only probe running at native speed with
  no IPC-per-event" model).
- **Live-observe vs record-then-query.** Is capturing ONE native execution trace
  and querying it offline (rr / time-travel debugging, trace databases) a better
  fit for our "many small queries per member" pattern than live callbacks? It may
  beat both the CLI-flags and the binding.
- **Interactive boundary.** When is a command protocol (gdb Remote Serial
  Protocol, DAP — interaction at breakpoints, not per instruction) sufficient vs
  a native in-process binding? (Recall: interactive PER-STEP across a subprocess
  = IPC-per-instruction = the real trap, not "interactive" as such.)
- **Native-binding tradeoffs** (pybind11 / cffi / ctypes) and the maintenance
  cost of a native extension vs a CLI.
- **Domain prior art** — does the C64/SID ecosystem (VICE monitor, the sidplayfp
  tooling, existing RE frameworks) already provide something to adopt instead of
  building?
- **Probe-effect / non-perturbing-instrumentation** literature — how to
  *guarantee* observe-only.

**Facts the research must design around (constraints/assets, not decisions):**
- We ALREADY patch libsidplayfp cleanly via `tools/libsidplayfp-overlay/`
  (`build.sh` step 2 copies it over pristine upstream `tools/libsidplayfp/`), and
  `--writelog` — the project's core ground-truth tap — IS such an overlay patch.
  So an observe-only overlay tap is a proven, available mechanism (an asset), and
  keeping the base pristine bounds the fork cost.
- **Ground truth is non-negotiable:** any instrumentation must be observe-only —
  never change emulation timing/values — or it poisons the verdict for the WHOLE
  project (the py65 trap one level up).
- The real access pattern is mostly "run to a condition, capture," plus occasional
  data-dependent exploration.

**Deliverable (Phase 0):** a short decision doc — the mapped design space, 2-3
viable architectures with tradeoffs (probe effect, speed, IPC, maintenance, fit
to our access pattern), and a recommendation. That doc REPLACES the strawman
below and drives the implementation phases. Only then proceed.

(A `deep-research` skill run is a natural way to do Phase 0.)

## Why

The extract uses **py65** (a pure-Python 6502 emulator) to OBSERVE a member's
own execution — run its init/play, watch PCs, read RAM/CPU state — to derive
USF content. py65 is:

1. **A reimplementation, so not ground truth.** For any value that depends on
   memory the file image did not load or the code did not provably write
   (uninitialized RAM; deep playback of a C29-class player with null / off-image
   / environment reads), py65's result can DIFFER from libsidplayfp — the verdict
   engine. This ate most of a session (DMC `Hank/Roots`: py65 read a loop target
   of `$00` and played noise where libsidplayfp read `$87` and played silent).
   See `feedback_ground_truth.md` §"third failure mode".
2. **~100-1000× slower** than native libsidplayfp (Python interpreter vs C++).
   Fine for short init runs; painful for deep playback (the DMC ghost sim plays
   ~9000 frames = 30-60 s).

**`tools/siddump.cpp` is ours** (702 lines) and already wraps libsidplayfp with
the exact hooks these observations need — `engine.debug(bool, FILE*)` for a
per-instruction CPU hook (that's how `--pc-trace` works) and `engine.cpuPeek(a)`
for MMU-aware reads. So the fix is INCREMENTAL siddump features, not a new
emulator.

**The win is correctness first, speed second.** A value siddump produces is
ground-truth **by construction** — it eliminates the whole py65-divergence bug
class, of which the interim guardrails (`_TaintMemory`, the "verify against
siddump" discipline) are only a fallback. Speed is a bonus, concentrated on the
deep-playback cases.

## The practice this establishes

**Prefer extending siddump (the ground-truth engine) over py65 for OBSERVATION.**
When a py65-shaped or ad-hoc observation recurs, add a declarative siddump hook
instead. This is the existing CLAUDE.md "tooling reflex" ("what tool would have
collapsed this to <5 min? build it") narrowed to a default. Record new hooks in
`tools/INVESTIGATION_BACKLOG.md`; the C++ change is scoped on its own, never
folded into an unrelated fix.

## Current py65 footprint (~30 sites) — classify before touching

Do a real inventory first (`grep -rlnE "from py65|MPU\(\)" pipelines/ src/ tools/`
minus `deprecated/` and `tools/py65_lib/`). Four classes, prioritized by
(divergence-risk × speed-cost):

- **Class D — deep-playback state capture. HIGH priority.** Plays many frames
  then reads arbitrary state. SLOW *and* divergence-prone. Members:
  `dmc/v4/factory._simulate_reinit_ghosts` (the ghost sim), plus any full-song
  py65 register trace (audit these). **Migrate first** — biggest robustness +
  speed win.
- **Class C — run init, observe LANDING / reachable PCs. MEDIUM.** Needs
  PC-level observation siddump lacks today. Members:
  `dmc/v4/compilation.py` (relocating-compilation dispatch — run init(A=sub),
  where does it JMP?), `dmc/v4/factory` play-phase / base observers (C18/C27),
  `_postinit_window(stop_at_player=…)`. Correctness + modest speed.
- **Class B — run init(+play), read post-init/post-play RAM. LOW.** Reads
  file-image / init-written bytes; low divergence risk. Largely already coverable
  by `--peek-post-init` / `--memwatch`. Members: `_postinit_window`,
  `_post_init_ram`, `_cia_period_from_init`, commando freq-table extension.
  Migrate opportunistically; not urgent.
  ⚠ **BOUNDARY (found the hard way, 2026-07-25): a py65 site whose PURPOSE is
  an IDEALIZED/counterfactual environment is a SIMULATION, not an observation
  — do not migrate it.** `_postinit_window` wants "the memory as if only the
  image + init existed"; the real machine cannot produce that (psiddrv is
  always resident — at $48xx on Super_Seven — plus real zp/vector/stack
  state), so a libsidplayfp RAM snapshot fed driver bytes into the
  extraction's base memory and Super_Seven sub 1 went partial (caught by the
  end-to-end verify behind a wrongly-"inert" golden diff; migration
  reverted). Genuine environment reads are already served by the C29
  `--peek-post-init` path. Ask of every candidate site: does it observe the
  real machine, or simulate an idealized one?
- **Class A — call a SPECIFIC subroutine with chosen registers, capture its SID
  writes. LEAVE (for now).** The dominant Hubbard/companion use
  (`inst_program.py`: run an instrument program with A=n, capture its
  `$D4xx` writes to derive the USF instrument). DETERMINISTIC (reads program
  data, no environment reads) → **not divergence-risky**, and short → fast in
  py65. siddump is PSID-init/play-oriented, so "invoke arbitrary routine" is the
  HARDEST to add and buys speed only. Skip unless a concrete win appears.

Rule of thumb: **migrate a py65 site iff it is divergence-prone OR slow.** A
deterministic short routine run that only reads loaded/written bytes can stay.

## Candidate architecture (STRAWMAN — evaluate in Phase 0; do NOT treat as decided)

Everything in this section is one candidate — "add declarative flags to siddump,
backed by observe-only overlay taps where needed." It is written concretely so
Phase 0 has a baseline to compare the prior-art options against (record-and-query,
a native binding, a compiled probe, a command protocol). Phase 0's decision doc
supersedes it. The three-layer shape of THIS candidate:

```
libsidplayfp-overlay   observe-only taps (--writelog today; a CPU/PC hook next)
      ↓
siddump (CLI)          declarative features on top of the taps
      ↓ (optional)
Python binding          interactive in-process on the same taps → replaces py65
```

Note that even this candidate likely needs an overlay CPU-state tap (Feature 1
wants A/X/Y at a PC; `debug()` today only dumps PC text to a FILE), and a
concrete overlay win independent of the py65 goal is a **PC-attributed writelog**
(tag each write with its store PC natively, obsoleting the `effect_chain_profiler`
pc-trace-and-align dance).

### siddump features (this candidate)

Design constraint on ALL of them: **declarative, not interactive.** py65 runs
in-process so the extract interleaves "step, decide in Python, step". siddump is
a subprocess, so each feature states "capture X when condition Y" and computes it
in ONE run. Model every new flag on the existing `--memwatch-on-write` /
`--writelog` / `--peek-post-init` — parse a spec, run once, emit one result
block. Reuse those implementations as templates.

### Feature 1 — PC-triggered capture (unlocks Class D, part of C)

`--capture-at-pc PC[:A] ADDR[,ADDR...]` (name TBD): while running, each time the
CPU's PC equals `PC` (optionally with A==`A`), emit a snapshot of the requested
RAM addresses **and the CPU registers A/X/Y/SP**. This is `--memwatch-on-write`
with a PC trigger instead of a register-write trigger, plus CPU-reg output. The
`engine.debug` hook already sees every PC; add the compare + snapshot + one
output line per hit. Absorbs: the ghost sim's "stop at the wedge, read the SID
burst + the poked state block", and any "at instruction X, what were the
registers / memory" observation.

### Feature 2 — init landing / reachable-PC report (unlocks Class C)

`--init-landing SUB` (name TBD): run `init(A=SUB)` and report (a) the first
"player head" PC control reaches (a page-aligned three-JMP head — see
`_is_player_head`), and/or (b) the set of entry-point PCs from a caller-supplied
watch list that executed. Absorbs: compilation dispatch detection, C18 play-phase
classification, C27 multi-SID base discovery. `_is_player_head` logic ports from
Python to C++ (small) or the watch-list variant keeps it caller-side.

### Feature 3 (optional, later) — call-routine capture (Class A)

Only if Class A ever justifies it: `--call ADDR:A [ADDR:A ...]` that JSRs a
routine with chosen registers (RTS-sentinel like the py65 harness) and captures
its `$D4xx` writes. Lower priority (deterministic, not a robustness win, hardest
to fit siddump's PSID model). Note here so it isn't rediscovered from scratch.

## Execution path (incremental — never big-bang)

**Phase 0 (research + decision doc) gates all of the below.** The phases here
assume the strawman candidate; if Phase 0 picks a different architecture
(record-and-query, a binding, etc.), rewrite these to fit — but keep the same
disciplines: incremental, per-site fallback, byte-identity gating.

Each phase is its own scoped commit; keep the py65 path as a per-site fallback
until that site's migration is verified, then delete it.

1. **Phase 1 — prove the pattern.** (After Phase 0.) Add Feature 1. Migrate `_simulate_reinit_ghosts`
   (Class D) to it. GATE: For_Party still verifies FULL, the extracted burst +
   pokes are IDENTICAL to the py65 version (golden diff of the `.usf` /
   `track_ff_reinit_ghost` param), and it's faster. This validates the C++ hook
   design AND the interactive→declarative reformulation on the highest-value
   site.
2. **Phase 2 — Feature 2 + Class C.** Migrate the compilation dispatch detector
   and the play-phase / base observers. GATE: `dmc_smoke` + the C31/C18/C27
   members re-verify unchanged (build path + verdict identical).
3. **Phase 3 — sweep remaining Class D / divergence-prone sites** across families
   (audit the Hubbard/FC/companion py65 uses for any that play deep or read
   environment memory).
4. **Leave Class A/B** unless a concrete win. Class B can migrate opportunistically
   to `--peek-post-init` / `--memwatch` where it simplifies code.

## Verification / gating (per migration)

- The migration must reproduce the extract's output **byte-identical** (or
  provably equivalent) to the py65 path — golden-diff the affected `.usf` (and
  `.sid`) over the touched members before deleting the py65 code. This is the
  same carrier-refactor discipline as CLAUDE.md's byte-identity gate.
- Re-run the family's verify (and `tools/regression.py` before commit, since a
  shared extract helper is touched).
- Only after green: delete the py65 code path for that site. Do NOT leave both
  live (dual paths rot; C20).

## Risks / notes

- **C++ build cost per feature.** `bash tools/build.sh` rebuilds libsidplayfp +
  siddump; note the two-host wall-clock (X230 ~16× the EPYC). Keep features small.
- **Don't break existing siddump consumers.** `verify_cycle.writelog_capture`,
  the DMC verify, `find_first_divergence`, `dmc_offtable_probe`, etc. all shell
  out to siddump — new flags must be additive, and siddump already HARD-ERRORS on
  unrecognised args (a deliberate guard, keep it).
- **ROMs.** siddump needs `tools/c64roms/` (env.sh sets `SIDFINITY_ROMS_DIR`);
  the new hooks run the full environment, which is the point (ground truth).
- **Keep the guardrails** (`_TaintMemory`, the ground-truth discipline) until the
  migration is complete — they cover whatever py65 remains.

## Definition of done

Every divergence-prone or slow py65 observation is served by a native siddump
hook; the remaining py65 (if any) is only deterministic short routine runs that
read loaded/written bytes. The "prefer siddump over py65 for observation" default
is recorded in `INVESTIGATION_BACKLOG.md` and future sessions follow it.
