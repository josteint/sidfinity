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

At that point the 5-way dispatch will have either grown to 7-10
branches (signaling the structural move is needed) or will have
absorbed new engines into the existing feature dimensions (signaling
the dimensions are sound).

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
