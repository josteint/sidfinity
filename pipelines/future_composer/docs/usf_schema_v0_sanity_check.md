# USF v0 schema — cross-engine sanity check

Run against 9 FC-family SIDs to test whether the engine_model + USF
schema design hold beyond Hawkeye.

## Result: schema is probably fine, extract layer needs rework

Tested with `pipelines/future_composer/hawkeye/engine_model.extract()`:

| SID | Engine | Load | Result |
|---|---|---|---|
| Hawkeye (Tel) | MoN/FutureComposer | $7AE0 | OK 12 subs / 15 insts / 64 pat_ptrs / 890 notes |
| Cybernoid II (Tel) | MoN/FutureComposer | $A600 | empty (0 insts / 0 pat_ptrs / 0 notes) |
| Noisy Pillars t1 (Tel) | MoN/FutureComposer | $1800 | empty |
| Domino Dancing (Bjerregaard) | MoN/Bjerregaard | $0825 | empty |
| Stormlord_V2 (Bjerregaard) | MoN/Bjerregaard | $1000 | empty |
| Flimbos_Quest (Bjerregaard) | MoN/Bjerregaard | $47B4 | empty |
| Slimbo4 (Bjerregaard) | MoN/Bjerregaard | $0804 | empty |
| Catalypse | MoN/FutureComposer | $2800 | empty |
| Golden Pyramids (Klink) | MoN/FutureComposer | $2E00 | empty (but 16 insts decoded — coincidental table-region overlap) |

Every non-Hawkeye SID decoded as empty content. The extract didn't
crash because Python doesn't object to reading zero bytes from
uninitialised memory — but the actual engine data isn't AT those
addresses for these SIDs.

## Root cause

The engine_model hardcodes addresses derived from Hawkeye's load address
($7AE0):

```python
ADDR_FREQ_LO_TABLE = 0x8337   # in Hawkeye, this is $7AE0 + 0x857
ADDR_FREQ_HI_TABLE = 0x8396
ADDR_PATTERN_PTR_TABLE = 0x8409
ADDR_INSTR_RECORDS = 0x860C
ADDR_PER_SUBTUNE_SPEED = 0x83F5
ADDR_PER_SUBTUNE_SMC = 0x83FC
ADDR_PER_SUBTUNE_7BAE = 0x7AFF
ADDR_TEMPLATE_BASE_HI = 0x7B
```

For Cybernoid II at load $A600, the corresponding tables live at
different addresses entirely. The same applies to every other SID.

## What this means

The **USF schema (the .md doc) is probably fine** — it describes
musical content (notes, instruments, sequences, freq table) that's
engine-family-wide, not Hawkeye-specific.

The **engine_model.py extract function is per-SID hardcoded** and only
works for Hawkeye. Treating it as "the FC family extractor" is wrong.

This mirrors a known pattern: Hubbard has per-tune `EngineConfig`
files (`pipelines/hubbard/commando/config.py` etc.) that carry the
per-SID addresses. The shared core `pipelines/hubbard/` only works
because each config supplies its addresses. For FC we'd need the
same — but the scaling problem is bigger:

- Hubbard '85 family: ~287 HVSC SIDs (and we have configs for ~12)
- MoN/FutureComposer family: 4,024 HVSC SIDs (and we'd need configs
  for all of them)

Manually writing 4,024 configs is not viable.

## Two paths forward

### Option A: Per-canary configs only (deferred-scale)

Write a `FCConfig` per canary (Hawkeye, then maybe Cybernoid II as a
second). The corpus of "FC SIDs the project can rebuild" stays small
— a hand-picked feature-coverage sample, like the canary picker
strategy proposes. Don't try to migrate all 4,024.

Cost: limited scale, fits the canary-only migration model. The
existing engine_model.py becomes one config among many.

### Option B: Auto-discovery extract

Instead of hardcoded addresses, AUTO-DISCOVER the FC data tables from
binary patterns + py65 trace. The Hawkeye work has already shown how:
- `tabcount` / `begcount` etc. located by signature scan
- Freq table identified by monotonic-ratio pattern detection
- Pattern pointer table identified by "pointers that point into the
  code region" pattern
- Instrument table located by following `LDA $XXXX,X` references
  inside the play loop

A per-SID `discover()` function could automate all of this, taking
only the SID binary as input. Then `extract(sid_path)` works for any
FC-family SID without manual config.

Cost: substantially more code (~hundreds of lines of heuristics), and
edge cases per variant (some SIDs may not have a discoverable freq
table, some may use different sequence layouts, etc.). High up-front
investment.

Discovery technique would need to be FC-family-aware (knowing what to
look for) but generalizable enough that one extractor handles all
FC-lineage SIDs.

### Recommendation

**Both, sequentially.**

1. **Now**: stay on Option A. Refactor `engine_model.py` to take an
   `FCConfig` dataclass; create `pipelines/future_composer/hawkeye/
   config.py`. That makes the existing work principled (per-tune
   config like Hubbard) without trying to scale yet.

2. **Then add a second canary** — pick from Cybernoid II (we have ACME
   source) or Domino Dancing (small Bjerregaard tune with +6 offset).
   Write its `config.py`. This forces us to learn what's actually
   FC-family-stable vs Hawkeye-specific.

3. **Maybe later**: auto-discovery via signature scan + py65 trace,
   once we know what's stable across at least 2-3 manual configs and
   have hypotheses about what makes discovery practical.

This is the same migrate-canaries-first / refactor-later sequencing
the deferred-composer-unification reasoning argues for. Don't try to
build the auto-discoverer before we have ≥2 worked examples of the
manual configs to design against.

## USF schema findings (the original question)

The cross-engine test surfaced ZERO new musical concepts. Every FC
family SID we examined fits the same conceptual shape: subtunes →
sequences → patterns → events. The schema doc (`usf_schema_v0.md`)
holds.

**Concrete schema impact:** none. The schema describes music, the
extract code is what needs the per-SID work.

## Updated next steps

1. **Refactor engine_model.py** to take a `FCConfig` parameter; move
   Hawkeye's constants into `pipelines/future_composer/hawkeye/config.py`.
2. **Add Cybernoid II as a second canary** (we have its full ACME
   source — easiest second case). Write `pipelines/future_composer/
   cybernoid_ii/config.py`.
3. **THEN** implement `to_usf.py` against the parameterised
   extract. Both Hawkeye and Cybernoid II produce USF; schema
   validates against both.
4. **THEN** composer + verify.
5. **Defer** auto-discovery to once we have 2+ manual configs.

## Cross-family note (for the deferred composer-unification work)

The Bjerregaard family showed wild structural variance — same
"sidid" label `Bjerregaard` covers tunes with +3, +4, +6, +13, +21,
+30110, +77, +144, +160, and negative play-init deltas. These can
NOT all share one engine config shape. Each play_addr-relative-to-
init reveals a different binary layout.

This is exactly the kind of cross-engine diversity the
"migrate-more-engines-first" recommendation in
`docs/refactor_1_remaining.md` argues for. The FC sanity check
confirms: even within the "MoN/FutureComposer" sidid umbrella, there
are multiple structural shapes the current extract can't handle.

Don't generalize the composer until the engine_model's per-config
shape has stabilized across more variants.
