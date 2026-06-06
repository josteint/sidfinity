# Adrenalin (HeatWave) — RE notes

**SID:** `hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid`
**Engine:** MoN/FutureComposer (per sidid)
**Authors:** Marvin Severijns & M. de Bree
**Songlength:** 9:25 (565s), 4 subtunes
**PSID:** load=$0000 (inline-encoded), init=$50E0, play=$50E3
**Purpose:** 3rd FC family canary — diversifies away from Tel-only
canaries (Hawkeye, Cybernoid_II). See `docs/canary_picker.md` row 3
of engine #4 (MoN/FutureComposer).

## Addresses found (2026-06-06)

From py65 init + disassembly grep:

| Address | Meaning | Verification |
|---|---|---|
| `$17E3` | lonote (freq_lo) | `$17E3+$48 = $0C` matches Hawkeye freq idx $48 lo |
| `$1842` | hinote (freq_hi) | `$1842+$48 = $47` matches Hawkeye freq idx $48 hi |
| `$18A1` | per_subtune_speed | 4 bytes `$02 $02 $01 $01` for 4 subtunes |
| `$18A5` + `$18A7` | subtune seq-base pointer table | X-indexed lo (`$18A5+X`) + hi (`$18A7+X`) — engine SMCs LDA at `$7ACA` with these |
| `$18B5` | runtime 6-byte per-voice seq ptr slot | copied from subtune base at init |
| `$19AC` | instr_records | 8 bytes/inst, byte layout matches Hawkeye (+0 pulse_hi, +1 ctrl, +2 AD, +3 SR, +4 fil_count, +5 fx1, +6 fx2, +7 fx3) |
| `$1BA0` | pattern_ptr_table | 2 bytes/entry lo,hi (e.g. `$1BA0..$1BAF = {$001C, $061C, $341C, $451C, $561C, $7A1C, $8E1C, $B31C}`) |

Code-side identification points:
- Nolengset (new-note play) at `$7C8B-$7CB8`
- Inst record load at `$7CCA-$7DE9`
- Pattern dispatch + ASL+TAY+SMC at `$7BAC-$7BB9`
- Sequence-byte read via `($75),Y` indirect at `$7BC9`

## Structural finding: data tables populated at init

Adrenalin's data tables (lonote at `$17E3`, hinote at `$1842`,
per_subtune_speed at `$18A1`, instr_records at `$19AC`,
pattern_ptr_table at `$1BA0`) all live in **low memory `$17xx-$1Bxx`**
— BELOW the binary's load address (`$50E0`). They're zeroes in the
raw binary. At init time the engine code at `$50E0`-`$7AB3` copies
packed source data from higher addresses into `$17xx-$1Bxx`.

Source addresses found so far (via signature match in raw binary):
| Runtime addr | Source addr | What |
|---|---|---|
| `$17E3` (lonote) | `$68B3` | Canonical FC lonote bytes (`1C 2D 3E 51 66 7B ...`) found in raw binary at `$68B3` |
| `$1842` (hinote) | ? | Find by sig "01 01 01 01 01 01 01 02 02 02..." in raw binary |

**This is a NEW extract-path shape vs Hawkeye/Cyb II**, both of which
have data tables directly at their runtime addresses in the raw binary
(engine loads its data tables to their final positions).

Two options for the extract path:
1. **Run init in py65 first** to populate `$17xx-$1Bxx`, then read
   addresses from post-init memory. Cleanest. Requires extending
   `engine_model.py::extract` to optionally run init (a new FCConfig
   field like `requires_init=True`).
2. **Find all source addresses in the raw binary** and update the
   FCConfig addresses to source rather than runtime. Requires
   understanding the init copy mechanism in detail.

For byte-exact rebuild, the rebuild MUST place the source data at
the source addresses (so the init copy produces matching post-init
state). So either way, the source addresses are what get written
into the rebuild's data emission.

## Per-subtune engine instances (NEW FINDING 2026-06-06)

Adrenalin uses **MULTIPLE engine instances**, not just multiple
per-subtune data sets. Decoded from the init copy table at `$514E-$5175`:

| Sub | Copy src | Copy dst | Size  | Play vector |
|-----|----------|----------|-------|-------------|
|  0  | `$5176`  | `$17F3`  | `$06E7` | `$7A06` (the engine at `$7A00`) |
|  1  | `$575D`  | `$1021`  | `$0A73` | `$1006` (engine instance at `$1000+`) |
|  2  | `$60D0`  | `$1000`  | `$0DDD` | `$1006` |
|  3  | `$6DAD`  | `$1000`  | `$0D51` | `$1006` |

Init flow (`$50E6-$5107`):
1. `JSR sub_510A` — runs the memcpy loop with X = subtune\*2,
   pulling source/dest/size from the four 8-byte tables.
2. SMC the play vector at `$50E3-$50E5` with the per-subtune play
   handler from `$516E[X]/$516F[X]`.

The implication: sub 0 uses the `$7A00` engine we disassembled, and
its tables at `$17E3/$1842/$19AC/$1BA0` are valid. Subs 1/2/3 use a
DIFFERENT engine at `$1000-$1FFF` (a second relocated FC engine copy
with its own data layout).

## Engine prefix bytes — observation only (2026-06-06)

Comparing the first 9 bytes at each per-subtune copy destination:

```
Sub 0  $7A00: 4C B4 7A | 4C FC 7A | 4C 02 7B   (engine code already in raw binary)
Sub 2  $1000: 4C 00 CD | 4C FC 10 | 4C 02 11   (post-init at $1000)
Sub 3  $1000: 4C 00 9D | 4C FC 10 | 4C 02 11   (post-init at $1000)
Sub 1  $1021: A2 00 CE 90 10 30 0C 20 26       (post-init at $1021, no JMP prefix)
```

Measured directly via `_run_init_in_py65(sub=2)`: of the first 2048
bytes at offset 0 (i.e., comparing `$7A00..$81FF` to `$1000..$17FF`),
**1578/2048 = 77.1% bytes are identical**. The matching positions
include relative offsets `$FC` and `$102` (the 2nd and 3rd JMP
targets) and other internal labels.

This is consistent with **two distinct hypotheses** that the seed
disasm alone cannot distinguish:

1. **Multi-engine.** Adrenalin has multiple distinct engine instances:
   engine A statically present in the binary at `$7A00`, engine B
   copied into `$1000` at init (same family code, relocated). The 77%
   match is the byte-identical portion of relocated code; the 23%
   difference is the address operands that had to be rebased.

2. **Single engine + per-subtune data overlay.** Adrenalin has ONE
   engine at `$7A00` and the per-subtune copies place **data only**
   (with some shim/trampoline bytes that happen to start with JMP-
   shaped bytes because those are part of the packed data structure).
   The `JMP $CD00` at `$1000` is never executed; PSID's SMC'd play
   vector at `$1006` (= `JMP $1102`) trampolines into the `$7A00`
   engine.

Without a hand-annotated disassembly of BOTH `$7A00..$81FF` AND
`$1000..$1FFF` (post-init), I cannot rule out either hypothesis.
**Speculation prior to that disasm was a protocol violation per
`feedback_check_existing_engine_docs`.**

## Required next session — full decompile (protocol Step 0)

Before any FCConfig / composer / USF schema work, do the following
in order:

1. **Read the family-wide docs** at `pipelines/future_composer/docs/`
   (FC v4.1 manual, `csdb_fc_v4_player_disasm.md`, lineage notes) —
   already exist; haven't been fully consulted yet for this RE.

2. **Hand-annotate engine A** at `$7A00..$81D0` from the existing
   seed `disassembly.s` (967 lines, auto-traced). Identify structural
   labels: playirq, songinit, nolengset, arpset, the per-frame voice
   loop, etc. Use Hawkeye's `disassembly.s` as a model for annotation
   style.

3. **Generate and hand-annotate engine B** at `$1000..$1FFF`
   post-init. Use `_run_init_in_py65(sub=2)` to capture the post-init
   memory, write it as a synthetic SID, seed-disassemble with
   `tools/seed_disassembly.py --entry 0x1003 --entry 0x1006`, then
   hand-annotate.

4. **Compare engine A vs engine B routine-by-routine.** Determine
   from evidence whether engine B is:
   - engine A relocated (multi-engine hypothesis), or
   - a small trampoline that JSRs into engine A (single-engine
     hypothesis with shim).

5. **Generate and hand-annotate the sub 1 source** at `$575D..$61CF`
   (copies to `$1021`). This one has no JMP prefix — its structural
   purpose is genuinely unknown from current evidence.

6. **Determine FC v4 / FC v4.1 player layout.** Some FC variants
   support per-subtune player code as an explicit feature. If
   Adrenalin uses that mechanism, the existing FC docs may describe
   it.

7. **Only THEN** decide multi-engine vs single-engine architecture
   and write the FCConfig.

## What's already in place for either outcome

Phase 1 schema + Phase 2 extract refactor commits (`55c1f98`,
`5c5a4c3`, `6b60f4c`) added general infrastructure:

- `EngineInstance` dataclass + `instance_for_subtune` /
  `resolve_address` helpers on `FCConfig`.
- `_run_init_in_py65` to capture post-init memory.
- `extract()` is multi-engine aware via `engine=None` fallback for
  single-engine SIDs — no behavior change for Hawkeye/Cyb II.

These are general-purpose. If Adrenalin turns out single-engine,
`FCConfig.engines = None` and the new infrastructure simply isn't
used for this canary; it remains available for genuinely multi-engine
SIDs if one is encountered later.

If Adrenalin IS multi-engine, the infrastructure is ready and the
FCConfig only needs the EngineInstance tuple filled in based on the
hand-annotated disasm.

## Decision NOT YET MADE — pending full decompile

Three options for what canary #3 actually covers (DO NOT pick one
before the hand-annotated disasm work above is complete):

1. **Adrenalin sub 0 only** as a single-subtune canary. The engine
   at `$7A00` matches Hawkeye/Cyb II's shape (we already found the
   addresses). Works under the existing FCConfig if we treat the
   "songs" field as 1 instead of 4. Loses 3 of the 4 subtunes from
   coverage but DOES land a non-Tel FC canary cleanly.

2. **Full Adrenalin (all 4 subs)** — requires multi-engine-instance
   support in FCConfig + the composer. Significantly larger scope:
   the per-subtune copy table becomes a new schema element, and the
   composer needs to emit two engine instances. Realistically a
   multi-session refactor.

3. **Switch to a different non-Tel FC canary.** Eliminator (row 2,
   Tel) and Tomcat (row 4, Tel) don't help diversify. Adrenalin is
   the only non-Tel row. Without Adrenalin (in some form), the FC
   canary set stays Tel-only.

Recommendation: option (1) — extract sub 0 only, mark Adrenalin as
"partial canary" in `canary_picker.md`, and revisit multi-instance
support once it's the bottleneck. This gets us a non-Tel canary into
the regression in one more focused session without committing to a
schema-level refactor.

## Unknown — TODO next session

- `subtune_layout`: new shape (X-indexed lo+hi pointer table + 6-byte
  runtime slot at `$18B5`). Provisional `'flat_seqtabel'` in config;
  may need a new SubtuneLayout variant if extractor fails.
- `instr_count`: count from `$19AC` records area.
- `max_patterns`: count from `$1BA0..` table extent.
- Aux tables (`drumtabel`, `filterbytes`, `arplo`, `arphi`, `pulsetabel`,
  `vibtabwait`, `startlen`, `starttabel`, `wavearp`, `pulsearp`):
  not yet located.
- `voice_loop_layout`, `noise_tick_style`, `nextvoice_write_order`, all
  other Cyb II/Hawkeye discriminator knobs: provisionally Cyb II
  defaults; verify by examining the per-voice loop tail + drum effect
  in the disasm.

## Status (2026-06-06)

**Stalled at structural discovery.** The runtime layout differs
fundamentally from Hawkeye/Cyb II:

1. **Inline-load PSID.** Header load=$0000 means the first 2 bytes of
   code body hold the actual load address (=$50E0). Hawkeye/Cyb II
   are non-inline (header load=actual load).

2. **Self-decompressing engine.** PC trace at subtune 1, 0.5s shows
   execution flows from $50E0..$5100 area → $7A00-$8100 area. The
   binary occupies $50E0..$81D0 (~12.5kB), but the engine itself isn't
   visible at the load address — it gets *unpacked* into the
   $7Axx-$81xx range at init. Adrenalin's $50xx region is a
   decompressor + packed engine data.

3. **`tools/seed_disassembly.py` only traced 76 lines** because it
   follows reachable code from init+play+subtune-entries and the
   unpack stage SMC-installs further entry points it can't see ahead
   of time.

## To continue

The pre-decompression binary is opaque. To get a useful disassembly:

1. **Run init in py65 to completion** (the decompressor exits to RTS
   or the IRQ handler).
2. **Snapshot RAM after init**: `mem_post_init = py65.memory[$7A00:$8200]`
   (or wider — the actual range needs discovery).
3. **Write the snapshot as a synthetic PSID** with load=$7A00 and the
   actual play address from the IRQ vector.
4. **Re-run `tools/seed_disassembly.py`** on the synthetic PSID. Now
   the disasm sees the real engine code with proper entry points.
5. **Cross-reference with `pipelines/future_composer/docs/wiki_fc_v41_manual.md`**
   and `csdb_fc_v4_player_disasm.md` for FC instruction semantics.
6. **Hand-annotate** structural labels (per-frame routine, nolengset,
   tone_arp, vibrato, drum, etc.) following Hawkeye's
   `disassembly.s` as a model.

## Then the standard canary-extract path

Once a clean disassembly exists:

1. Find the ~12 address knobs (freq_lo/hi, pattern_ptr, instr_records,
   per_subtune_speed, drumtabel, filterbytes, arplo/hi, pulsetabel,
   vibtabwait, startlen, starttabel) via `lda <addr>,X` greps.
2. Choose FCConfig knobs (subtune_layout, pulse_run_style,
   noise_tick_style, voice_loop_layout, ...).
3. Address the inline-load PSID shape — may require a new FCConfig
   field or a small extension to `composer.py::_load_sid_psid` to
   handle inline at SID-write time.
4. Build canary: `pipelines/future_composer/adrenalin/config.py` →
   `ADRENALIN = FCConfig(...)`.
5. Extract: `from pipelines.future_composer.engine_model import
   extract; extract(ADRENALIN)`.
6. Verify byte-exact: `verify_featuredriven(ADRENALIN)`.
7. Add to `tools/regression.py::regress_future_composer` canaries
   list once 4/4 subtunes go FULL.

## Why we're adding Adrenalin

Hawkeye + Cybernoid_II are both Jeroen Tel tunes; their feature mix
overlaps heavily and doesn't exercise everything the FC engine can do.
HeatWave's Adrenalin is the only non-Tel candidate in `canary_picker`
row 3 of engine #4, and adds (at minimum):

- Different composer style → different per-instrument fx_bytes patterns
- Self-decompressing engine load shape
- Inline-encoded PSID header
- 4 subtunes (multi-sub regression coverage)
- Potentially: feature combinations no Tel tune uses (subtune SFX
  handling, different fil_count bits, different drum tables, etc.)

The composer's current feature coverage is honest only when at least
one canary structurally distinct from the existing two demonstrates
that the feature-driven composition path generalises beyond Tel's
subset.

## Tools to use (per [[feedback_writelog_divergence_recipe]])

- `tools/seed_disassembly.py` — generate skeleton (already done at
  76 lines; redo against post-init snapshot)
- `tools/find_first_divergence.py` — once a rebuild exists
- `siddump --memwatch-on-write` + `--memwatch` — state inspection
- The hand-annotated disassembly is the input to everything else.

## Related

- [[project_hawkeye]] — worked example of FC canary migration end-to-end
- [[feedback_check_existing_engine_docs]] — Step 0 protocol
- `pipelines/future_composer/docs/wiki_fc_v41_manual.md` — FC v4.1
  instruction format
- `pipelines/future_composer/docs/csdb_fc_v4_player_disasm.md` —
  player disasm reference
