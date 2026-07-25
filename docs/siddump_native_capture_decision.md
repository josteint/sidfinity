# Decision doc: how to observe a tune's execution from ground truth (Phase 0 deliverable)

**Status:** proposed 2026-07-25. This is the Phase 0 deliverable of
[`siddump_native_capture_plan.md`](siddump_native_capture_plan.md). Per that
plan, this doc **supersedes the "Candidate architecture (STRAWMAN)" section**
and drives the implementation phases — *pending user review*. It does not yet
edit the plan or write any implementation code (Phase 0 gates the build).

**One-line recommendation:** **(A) extend siddump with declarative capture
flags as the default mechanism**, adding exactly one new observe-only overlay
primitive (a PC-triggered CPU+RAM snapshot); **hold (B) a thin in-process
`pybind11`/`nanobind` binding over the *same* overlay taps as a deferred
escalation** reserved for genuinely data-dependent sites that don't reduce to a
one-shot spec; **reject (C) record-then-query and the VICE-monitor family
outright.** Rationale below.

---

## 1. What this decides

The goal (settled by the plan): stop deriving extract values from **py65** where
that is divergence-prone or slow, and observe from the **ground-truth engine
(libsidplayfp)** instead. This doc decides the *mechanism*.

The research was run as a `deep-research` fan-out (6 angles, 23 sources, 101
extracted claims, adversarial 3-vote verification). Session limits truncated the
verification pass and the automated synthesis on both runs, so **the synthesis
below is authored by hand** from the verified output. The load-bearing claims
this recommendation rests on are all **3-0 confirmed** (zero refutations);
where a claim is sourced but its vote was cut off, it is marked *[sourced]* and
is not load-bearing. Full claim/source list in §8.

---

## 2. The real access pattern (from a code inventory, not the plan's abstraction)

Before mapping the design space, I inventoried the **50 py65 call-sites across
36 non-deprecated files** (`grep -rlnE "from py65|MPU\(\)"`). Every one follows
a single shape:

> **set up CPU registers → run to a condition → read state**, with the
> orchestration (loops, diffs, label-mapping, retries) in Python.

Three representative sites, spanning the plan's priority classes:

| Site | Class | Shape |
|---|---|---|
| `dmc/v4/factory._simulate_reinit_ghosts` | **D** (crown jewel) | run `init`→RTS, snapshot `$1000-$1800`; fresh run, `play()` **up to ~9000×** until `PC==wedge`, snapshot again; **diff** the two windows; map differing bytes to composer labels. Slow *and* divergence-prone (relies on `_poweron_fill` guessing libsidplayfp's power-on RAM — the exact Roots bug). |
| `dmc/v4/compilation._observe_dispatch` | **C** | run `init(A=sub)`, report **where control lands** + the `A` carried there; a **2-pass retry** admitting Music-Assembler landings if the first pass finds nothing. |
| `hubbard/inst_program.capture` | **A** (leave) | JSR a routine with `A=n`, run to an RTS sentinel, capture its `$D4xx` writes. Deterministic (reads program data, no environment reads) → not divergence-risky, short → fast. |

**The decisive observation: nobody steps per-instruction from Python.** Even the
"data-dependent exploration" (the 2-pass dispatch) is *coarse* — a handful of
run-to-condition round trips, not millions of step-decide-step iterations. This
directly determines which prior-art tradeoffs bind us and which don't (§4).

---

## 3. The asset that reframes the whole decision

Our overlay `sidplayfp` (`tools/libsidplayfp-overlay/`, ~12-file patch over
pristine upstream, applied by `build.sh` step 2) **already exposes a rich
observe-only in-process C++ API** — not just `--writelog`:

- `debug(bool, FILE*)` — per-instruction PC hook (drives `--pc-trace`)
- `getSidStatus(sidNum, regs[32])` — non-perturbing bulk register read *[sourced: stock upstream API]*
- `enableReadTrace / getReadLog / clearReadLog` — memory-read trace
- `peekRam(addr)` / `cpuPeek(addr)` — RAM and MMU-aware (banked) reads
- `getPlayCount / getPlayEntryCycles` — play()-invocation counters
- `setMemWatchOnWrite(trigger, addrs[])` + `getMemWatchEvent(i)` — event-log capture
- `getCia1TimerA()` — CIA state for multispeed observation *[sourced: stock upstream API]*

Emulation is driven by `play(cycles)`. **The expensive part of a native binding
— an emulator with observe-only taps — is already built.** This is why the
plan's framing ("maybe a Python binding later") understates option B's
readiness and why the design-space question is narrower than it first appears.

**The one capability gap** for a py65 drop-in: there is **no PC-triggered
capture** (snapshot CPU regs A/X/Y/SP + chosen RAM when `PC==target`) and no
"where did `init(A=sub)` land" report. `debug()` only dumps PC *text to a FILE*;
it can't hand a caller "at PC X, the registers/RAM were…". Both are small
additions modeled on the existing `setMemWatchOnWrite` event-log pattern
(trigger + address list + event vector), triggering on a **PC match** instead of
a write and additionally recording CPU registers.

---

## 4. The mapped design space (five families)

Each family rated on the plan's four axes: **observer-effect safety**,
**per-event cost / IPC**, **fit to "run-to-condition-then-capture + occasional
interactive"**, **implementation + maintenance cost**.

### Family 1 — declarative-CLI-flags · *exemplar: our own siddump (`--writelog`, `--memwatch-on-write`, `--peek-post-init`)*
- **Observer effect:** safe by construction — the tap reads host-side emulated
  state and appends to a host log; it never touches the emulated bus or clock.
  `--writelog` is *already* such a tap and is the project's ground-truth oracle.
- **Per-event cost / IPC:** no per-event IPC. One subprocess spawn **per query
  per member** — coarse, and identical to how the whole corpus already runs
  siddump. Not per-event.
- **Fit:** excellent for "run-to-condition-then-capture" (that IS the one-shot
  declarative model). **Awkward** for data-dependent orchestration: each
  interactive decision must be pre-encoded into the flag's spec or split across
  multiple subprocess runs.
- **Cost:** lowest marginal cost — extends proven, parallel-safe machinery; no
  new build system or language boundary; each flag is a small C++ addition.
  siddump already hard-errors on unknown args (keep that guard; additive flags).

### Family 2 — in-process-native-binding · *exemplars: `zynamics/bochs-python-instrumentation` (embeds a Python interpreter in Bochs, callbacks by name — 3-0), `mtimmerkamp/libsidplayfp-python` (a **cffi** binding over libsidplayfp — proven in-domain)*
- **Observer effect:** identical safety to Family 1 — it wraps the *same*
  overlay taps. Non-perturbation is a property of the taps, not the language
  boundary.
- **Per-event cost / IPC:** no per-event IPC — callbacks/reads run in the
  emulator's own process/address space, "which eliminates the context switches…
  that per-event IPC-based observation pays" (arXiv 2508.00682, 3-0). One
  process serves a member's *many* small queries.
- **Fit:** best for the data-dependent Class-C sites — the Python orchestration
  (diff, label-map, 2-pass retry, loop-until-wedge) stays cheap because a state
  read is a function call, not a subprocess.
- **Cost:** highest — a new C++↔Python build boundary to maintain. Tool choice:
  **`pybind11`/`nanobind`, not cffi** — our overlay API is C++ (`std::vector`,
  structs), and cffi needs a C ABI so it "mostly cannot wrap C++ APIs" *[sourced:
  Behnel]*; the existing `libsidplayfp-python` gets away with cffi only against
  the plainer stock C++ surface. `nanobind` ~10× lower per-call overhead than
  `pybind11` *[sourced: nanobind PyPI]*. Risk to manage: it must wrap the *same*
  taps as siddump, never become a **second, divergent way to drive the
  emulator** (C20-flavoured rot).

### Family 3 — command-protocol-at-breakpoints · *exemplars: VICE binary monitor + `pyvicemon` / `IceBroLite`; gdb RSP; DAP*
- **Observer effect:** the protocol *halts* the emulator to interact (VICE: "the
  transmission of any command causes the emulator to stop", 3-0) — safe for
  reads, but it's a different interaction model.
- **Per-event cost / IPC:** out-of-process over a **TCP socket** (3-0).
  Breakpoint-granularity ("run to a checkpoint, notify") avoids per-instruction
  IPC (VICE checkpoints, IceBroLite "only updates state after you've stopped" —
  both 3-0). But **per-instruction stepping IS one IPC round-trip per step**
  (VICE `Advance Instructions 0x71`, 3-0); single-stepping over a process
  boundary is measured **>100,000× slower** than in-process instrumentation
  (arXiv 2508.00682, 3-0) — the "IPC-per-instruction trap".
- **Fit / cost:** **DISQUALIFIED on ground truth, not on IPC.** VICE is a
  *different emulator* from libsidplayfp (our verdict engine). Observing via the
  VICE monitor would reintroduce **exactly the py65 disease** — observation from
  one emulator, verdict from another, free to diverge on uninitialized /
  environment reads. The mature, adoptable C64-domain tooling (VICE monitor,
  pyvicemon, IceBroLite) is real and it is the obvious "don't build it" answer —
  and the ground-truth constraint kills it. This is the single most important
  *negative* finding of the research.

### Family 4 — DBI-style-compiled-probe · *exemplars: QEMU TCG plugins (3-0), Intel Pin, DTrace/eBPF*
- **Observer effect:** fastest model (probes compiled into translated blocks,
  in-process, no per-event IPC — QEMU 3-0; kprobe ~56 ns/event — 3-0). **But**
  observe-only is *opt-in discipline, not enforced* (QEMU gates even register
  reads behind a capability flag, 3-0), and complete transparency is
  "structurally unachievable" for DBI on a real target (shared address space +
  resource contention + JIT overhead — 2-1). Note that last result is about
  instrumenting a *real* process; instrumenting an *emulator* sidesteps it (§6).
- **Fit / cost:** **N/A for us.** libsidplayfp is a hand-written software
  interpreter — there is no TCG/JIT to compile probes into. This family requires
  a JIT-DBT engine we don't have and won't build. Its *lesson* transfers (§6);
  the *mechanism* doesn't.

### Family 5 — record-then-query-trace · *exemplars: rr, WinDbg TTD, Pernosco, qira*
- **Observer effect:** replay is deterministic/non-perturbing *[sourced]*.
- **Cost / fit:** records once (rr keeps only nondeterministic inputs; TTD ~10–20×
  record slowdown *[sourced]*), then serves **many queries against ONE long
  expensive execution**. **Our workload is the inverse:** many *short* executions
  (per member/subtune), *few* queries each. The record cost buys nothing and the
  indexed-trace machinery is a large build over libsidplayfp that nobody has
  written. **Reject** — wrong shape, and disproportionate cost.

---

## 5. Applying the constraints → the decision

Two constraints collapse the space hard:

1. **Ground truth is non-negotiable → observe from libsidplayfp itself.** This
   eliminates Family 3 (VICE) and Family 4 (needs a different, JIT-based engine).
   Only Families 1, 2, and 5 are *over libsidplayfp* — and Family 5 is the wrong
   workload shape and a large from-scratch build.
2. **Our access pattern is run-to-condition, not step-per-instruction.** This
   means the "IPC-per-instruction trap" that the plan's Phase 0 worried about
   **does not bind our migration targets** — both Family 1 and Family 2 avoid it.
   So the A-vs-B choice is *not* about the trap; it's about
   declarative-one-shot-fit vs cheap-in-process-orchestration, and about build
   cost.

That leaves **A vs B, both over our own libsidplayfp overlay.** Deciding between
them:

- The **crown-jewel, highest-value + highest-risk site (the DMC ghost sim,
  Class D)** is pure "run to condition, capture." It reduces cleanly to a single
  declarative one-shot — *run to `PC==wedge`, snapshot CPU regs + `$1000-$1800`;
  and separately snapshot after init* — needing exactly **one new primitive**
  (the PC-triggered capture of §3). The Python-side diff + label-map stays in
  Python either way. Option A serves this with the least new surface.
- Option B's decisive advantage (cheap in-process orchestration) only pays off
  on the **data-dependent Class-C sites** (the 2-pass dispatch), which are
  **lower priority** and fewer.
- Option A extends **proven, parallel-safe, zero-new-build** machinery; Option B
  adds a C++↔Python build boundary and a standing "don't let it diverge from the
  CLI" maintenance burden. The plan's own disciplines — *incremental, per-site
  fallback, byte-identity gating* — favour the lower-surface path first.

**Therefore:**

- **(A) Declarative CLI flags is the default.** Add the one PC-triggered
  capture primitive; migrate the ghost sim (Class D) to it first — the plan's
  Phase 1, unchanged in spirit.
- **(B) A thin in-process `pybind11`/`nanobind` binding over the same overlay
  taps is a *deferred escalation*, triggered only if a specific Class-C
  data-dependent site proves genuinely un-declarative** (i.e. encoding its
  decision procedure into a flag is clearly worse than orchestrating in Python).
  If we ever build it, it wraps the **same** taps siddump uses — never a second
  emulator-driving path — and uses pybind11/nanobind (not cffi, which can't
  cleanly wrap our C++ API).
- **(C) and Family 3/4 are rejected**, for the reasons in §4–§5.

This is a **hybrid, A-first** stance: same conclusion as the plan's strawman for
the *mechanism of the first phases*, but now **grounded in the design space and
with three alternatives explicitly disqualified** (VICE/command-protocol on
ground truth; DBI on "no JIT to instrument"; record-then-query on workload
shape) — which is what Phase 0 was for. The one substantive change from the
strawman: **B is downgraded from "likely next step" to "deferred escalation,
only on proven need,"** because the access-pattern inventory shows the
interactive/per-instruction pressure that would justify an in-process binding
is largely absent from the migration targets.

---

## 6. How we guarantee observe-only (the non-perturbation discipline)

Phase 0 asked how to *guarantee* the tap is non-perturbing. The research gives
both the hazard and the guarantee:

- **Hazard (confirmed):** for DBI on a *real* target, complete transparency is
  structurally unachievable — shared address space, OS-resource contention, JIT
  overhead (ACM 10.1145/3478520, 2-1). QEMU even makes register *reads* an
  opt-in capability (3-0). Observe-only is a *discipline*, not a free property.
- **Why it IS achievable for us:** we instrument an **emulator**, not a real
  process. The observation runs in the **host's state space**, entirely separate
  from the emulated 6502's state space; the emulated machine has no channel to
  observe the host reading its RAM/registers. (This is the "engine-integrated
  instrumentation executes in the engine's state space, not the emulated
  program's" principle *[sourced: arXiv 2403.07973]*, and it is exactly why
  `--writelog` is already trusted as ground truth.) The DBI non-transparency
  result does **not** transfer, because its three causes are all about sharing
  the *target's* address space — which an out-of-target emulator tap does not do.

**The concrete rules a new tap must obey** (all satisfied by the existing taps):
1. **Read emulated state, never write it.** `peekRam`/`cpuPeek` read through the
   MMU without a bus write; `getSidStatus` reads the register file. A capture tap
   appends to a host vector.
2. **Consume no emulated cycles and touch no scheduler state.** A "run until
   `PC==X`" primitive is implemented as *clock the emulator normally and check
   the host's PC variable between steps* — the mechanism `debug()` already uses.
   It must **not** insert a breakpoint the emulated CPU can see, and must not
   alter timing.
3. **Keep the base pristine.** The tap lives in `tools/libsidplayfp-overlay/`;
   upstream stays untouched, bounding the fork.

**The gate that PROVES non-perturbation for any new tap** (make this mandatory,
per-feature): capture `--writelog` for a set of members **with the new tap
enabled and disabled**, and require the two write streams **byte-identical**. If
enabling the observation changes the write stream, the tap perturbed emulation
and the feature is rejected. This is a cheap, project-native check — the same
byte-identity discipline as the carrier-refactor gate — and it turns
"observe-only" from an assertion into a test.

---

## 7. What this means for the implementation phases (supersedes the strawman)

The plan's phased path survives almost intact; the changes are: name the
mandatory non-perturbation gate, and reclassify B as deferred.

- **Phase 1 — prove the pattern (Family 1).** Add the **PC-triggered capture**
  primitive (overlay tap + one siddump flag: on `PC==target` [optionally with
  `A==a`], emit CPU regs A/X/Y/SP + a snapshot of requested RAM addresses).
  Migrate `_simulate_reinit_ghosts` to it. **Gates:** (a) the new
  non-perturbation byte-identity check (§6) passes; (b) For_Party still verifies
  FULL; (c) the extracted burst + pokes (`track_ff_reinit_ghost`) are **identical**
  to the py65 version (golden `.usf` diff); (d) it's faster. Then delete that
  site's py65 path (no dual paths — C20).
- **Phase 2 — init-landing / reachable-PC report (still Family 1).** Add the
  "run `init(A=sub)`, report the landing PC + which watch-list PCs executed"
  flag. Migrate the compilation dispatch detector + play-phase / base observers.
  **Gate:** `dmc_smoke` + the C31/C18/C27 members re-verify unchanged (build path
  + verdict identical). **Decision checkpoint:** if any of these sites is
  genuinely un-declarative (its data-dependent orchestration can't reduce to a
  one-shot spec without contortion), that is the trigger to build **(B)** the
  thin binding — scoped to those sites, wrapping the same taps.
- **Phase 3 — sweep remaining Class-D / divergence-prone sites** across families
  (audit Hubbard/FC/companion py65 uses for deep-playback or environment reads).
- **Leave Class A** (`inst_program`, deterministic short routine runs) and
  migrate **Class B** opportunistically to `--peek-post-init`/`--memwatch`.

Every phase: its own scoped commit; py65 kept as a per-site fallback until that
site is verified byte-identical, then deleted; `tools/regression.py` before
commit (shared extract helpers are touched).

A concrete overlay win worth taking alongside Phase 1, independent of the py65
goal: a **PC-attributed writelog** (tag each write with its store PC natively),
which would obsolete the `effect_chain_profiler` pc-trace-and-align dance.

---

## 8. Sources & verification status

Research method: `deep-research` fan-out, 6 angles, 23 sources, 101 claims,
3-vote adversarial verification (need 2/3 refutes to kill). Session limits
truncated the verification pass and automated synthesis on both runs; **this
doc's synthesis is hand-authored** from the verified output. **Load-bearing
claims are 3-0 confirmed; none were refuted.** Claims marked *[sourced]* had
their verification votes cut off — they are corroborative, not load-bearing.

**3-0 confirmed (load-bearing):**
- VICE binary monitor = out-of-process command protocol over TCP; `Advance
  Instructions 0x71` = per-step IPC; checkpoints/`pyvicemon`/`IceBroLite`
  interact at breakpoint granularity, state read only after halt. —
  `vice-emu.sourceforge.io/vice_13.html`, `github.com/Galfodo/pyvicemon`,
  `github.com/Sakrac/IceBroLite`
- QEMU TCG plugins = in-process shared libs, callbacks compiled into translated
  blocks, no per-event IPC; observe-only is opt-in (register access gated by
  `QEMU_PLUGIN_CB_RW_REGS`). — `qemu.org/docs/master/devel/tcg-plugins.html`
- In-process DBI runs callbacks in the target's address space → eliminates
  per-event context switches/IPC; GDB single-step >100,000× slower than in-proc
  Pin; breakpoint/trap observation ~free when idle but degrades fast with event
  rate; Pin overtakes GDB after ~100 events/100M instr. — `arxiv.org/pdf/2508.00682`
- Bochs instrumentation is compile-time (`--enable-instrumentation=python_hooks`),
  embeds a Python interpreter in-process, callbacks registered by name — no
  per-event IPC. — `github.com/zynamics/bochs-python-instrumentation`
- Compiled in-place kernel probe per-event cost ~tens–hundreds ns (bpftrace
  kprobe 56 ns, DTrace 280 ns). — AsiaBSDCon 2024, `papers.freebsd.org/2024/asiabsdcon/…`
- Complete transparency structurally unachievable for in-target DBI (shared
  address space + resource contention + JIT overhead) — *about real targets, not
  emulators* (2-1). — `dl.acm.org/doi/fullHtml/10.1145/3478520`

***[sourced]* (corroborative, verification cut off):**
- `libsidplayfp-python` is an in-process **cffi** binding over libsidplayfp
  (proven in-domain; needs a C compiler + `cffi>=1.0` + `libsidplayfp>=1.8`);
  cffi mostly can't wrap C++ APIs (needs a C ABI). — `github.com/mtimmerkamp/libsidplayfp-python`, `blog.behnel.de`
- `nanobind` ~10× lower per-call overhead than `pybind11`. — `pypi.org/project/nanobind`
- libsidplayfp stock API already has observe-only `getSidStatus(sidNum, regs[32])`
  and `getCia1TimerA()`. — `libsidplayfp.github.io/…/classsidplayfp.html`
- Engine-integrated instrumentation executes in the engine's state space, not the
  emulated program's (the non-perturbation-by-construction principle). — `arxiv.org/pdf/2403.07973`
- rr records only nondeterministic inputs + replays deterministically; TTD ~10–20×
  record slowdown; Pernosco = record-once, query an offline omniscient database. —
  `arxiv.org/pdf/1705.05937`, `learn.microsoft.com/…/time-travel-debugging-overview`, `pernos.co`

Workflow transcript: `…/workflows/wf_9b5033cf-606/journal.jsonl`.
