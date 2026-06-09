# Adrenalin — finish via the 5-Title-Tunes UNIFICATION (plan)

## Goal
Finish Adrenalin. Sub 0 done (`Adrenalin[0] 1/1`). Subs 1/2/3 remain.

## Adrenalin is the 5-Title-Tunes situation
5TT = a parent PSID selecting 5 standalone Hubbard '85 sub-engines (not
identical — different data). The project's answer was a **unification**: ONE
Hubbard engine + per-subtune tables (freq-base, instr-base, orderlist, params)
+ globally-renumbered instruments. The 5 engine copies collapse to one emit.

Adrenalin is the same with FC:
- subs 0/2/3 = engine A's design (the original packs a relocated copy at
  `$1000` for memory reasons — irrelevant to our rebuild).
- All subs use the **canonical FC freq table** (same table Cyb II/Hawkeye use;
  each sub takes a different *slice*). So freq is shared/canonical, like 5TT.
- instruments / patterns / sequences differ per sub.
- sub 1 = a different engine (handle separately; see Phase 3).

## The unification (subs 0/2/3) — one engine A + per-subtune data
Reuse the FC composer's existing multi-subtune machinery (per-sub `seq_table` +
`snelheid` already exist) and add the one missing 5TT piece: **per-subtune
freq/instrument bases**.

- **Instruments:** concatenate subs 0/2/3 instruments into one global table
  (dedup identical), renumber; rewrite each sub's pattern instrument refs to the
  global ids (5TT's globally-renumbered instruments). No per-sub instr_base
  needed if refs are renumbered globally.
- **Freq table:** one shared canonical FC table; each sub's notes normalized to
  it (the per-sub freq-slice offset is an extraction concern → canonical note
  values, exactly как 5TT handled per-sub `freq_table_base`).
- **Patterns / sequences:** already per-subtune in the model; carry per sub.
- **Speed / init:** per-subtune `snelheid` + per-voice init (already supported).
- **Engine:** ONE engine A emit; standard FC subtune dispatch selects the
  active sub's sequences. No relocated copies, no pools.

## Phases (each ends green + committed)

**Phase 1 — unified extract + build (subs 0/2/3).**
- Per-sub extract of each subtune's full content from its post-init memory
  (prototype proven: sub 2 yields real freq/16 instr/10 patterns/3 seqs).
- Merge: concat+dedup+renumber instruments across subs; rewrite pattern instr
  refs; normalize notes to the canonical freq table.
- Produce a multi-subtune FCSong/USF (subs 0/2/3); build via the FC composer
  (one engine A); verify each subtune's write-log (trichotomy + `audio✓`).
- Gate: `Adrenalin[0,2,3]` pass. Other engines untouched.

**Phase 2 — sub 1.** RE the different engine @ `$1021`; decide unify-or-separate;
build + verify → Adrenalin 4/4.

**Phase 3 — integration + full regression + ear-test.**

## Notes / risk
- **No USF schema invention.** Instruments list grows (renumbered); subtunes
  carry their own patterns/seqs/speed (existing fields). The only composer
  addition is per-subtune freq/instr base support if shared-table normalization
  proves insufficient — measure first.
- Sub 1 is the open-ended unknown (possibly non-FC).
- Verdict already does per-subtune trichotomy + `audio✓`.
