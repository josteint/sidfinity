---
name: reference_dmc_canon_diff
description: "tools/dmc_canon_diff.py — a-priori wedge enumerator: diff every member's player code vs the canonical player binary, cluster deviations by site, tag handled/NEW, split partial/full. Proved DMC family-1's wedge space is essentially fully handled."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 5c8305f4-b394-4c76-b68a-f7ff5fb5da03
---

`tools/dmc_canon_diff.py` (built 2026-07-10) — the PROACTIVE complement to the
reactive `pipelines/dmc/v4/factory.py::_*_probe` wedge detectors. Answers "can we
predict the residue wedges a priori instead of one-divergence-at-a-time?"

## What it does
Every DMC family-1 SID = canonical player + relocation + per-member WEDGES + song
data. The packer patches only data-table OPERANDS (canon's point BELOW $1000, at
$09xx-$0Exx); a hand-patch WEDGE flips an OPCODE or repoints an operand INTO the
player's own code/state ($1000-$17FF). So: linear-align each member's reachable
player instructions to the 4KB canon binary
(`pipelines/dmc/docs/dmc4_player_embedded_1000.bin`, via `dataflow._canon_instrs`),
diff OPCODES + in-player OPERAND-REPOINTS, Δ-mode-filter bulk state/table
relocations (a moved state block repoints ~346 sites by ONE Δ — not a wedge),
cluster by canon site, tag handled-vs-NEW (`_KNOWN_SITES`), and split each cluster
into partial/full carriers with `--status BATCH.jsonl`.

`python3 tools/dmc_canon_diff.py [--members family1|FILE.json] [--status
tmp/dmc_wide_results.jsonl] [--csv out.csv] [--new-only] [--limit N]`

## The finding it produced (2026-07-10) — the residue is NOT a wedge problem
Of 188 fresh family-1 partials:
- **147 (78%) carry NO code deviation** → pure off-table-freq / dynamic-state / CIA
  residue (the ledger's hard-by-design tail; NOT wedges).
- **32 (17%) carry a HANDLED wedge**, fail for another reason.
- **9 (4%) carry a genuinely UNHANDLED code-patch — ALL singletons** (max
  multi-carrier site = $10E2 at 2): Complications, Cotton_Eye_Joe, Enforcer_2,
  Ice_on_Fire, Jezuseczek, Logic_Intro, Mathematica_tune_3, One_Man_and_Boris,
  Second.

So the wedge space is ESSENTIALLY FULLY HANDLED — there is NO multi-carrier
unhandled-wedge lever, and one-wedge-at-a-time is inherent to the residue's
long-tail structure, not a code smell. It also doubles as a completeness AUDIT of
the probes' TRUE carrier counts (track_loop_hook 876, d418/wrapper 169, master_vol
113, rest-skip $1180 129, hardrestart 25) — far more than several docstrings'
"3 carriers" claims.

## Limits (in the tool docstring)
- Misses IMMEDIATE-value tweaks (hr_preset $0F->X, cymbal $FF->X — a value diff,
  not an opcode/address diff).
- Misses same-opcode BRANCH-OPERAND repoints (proven 2026-07-27, r121: Dreck's
  $7D dispatch BEQ $56→$2B — the $7D-retrig wedge, C19 24th occ — reported as
  "only the $10DF hook"). A "0 NEW" report does NOT cover branch operands;
  fallback = raw byte-diff vs the canon binary, then filter operand/data runs.
- Skips RE-ASSEMBLED members (1107/5401; linear-align only — an opcode-skeleton
  align would cover them).
- `_KNOWN_SITES` handled/NEW tags are hand-maintained instruction-site windows.

Surfaced 2 pre-existing bugs on the full sweep (sampling had missed them):
unescaped member-address bytes in `_pw_bound_shift_probe`/`_pw_dir_persist_probe`
regexes (2 members ERROR on a `[`=0x5B byte), + the 2SID-multisubtune scope gap
(7 Rayden members). Related: [[reference_divergence_census]], [[project_dmc]].
