---
name: reference_divergence_census
description: "tools/divergence_census.py — residue-triage tool that clusters a family's non-FULL members into ranked root-cause buckets"
metadata: 
  node_type: memory
  type: reference
  originSessionId: 61079d2b-5be1-445b-9baa-b2959d4e0ea3
---

`tools/divergence_census.py` — residue triage for a wide engine family.
Turns a flat batch-results jsonl into ranked ROOT-CAUSE clusters. Automates
the "stratify by first-diff bucket" methodology (CLAUDE.md wide-family
iteration) that was previously done by hand each family.

Two stages:
1. **CENSUS** — buckets every member by status+reason (collapsing per-member
   hex/line noise), separating composer/data residue (verify partials) from
   factory/layout residue (detect-rejects).
2. **CLUSTER** — two modes:
   - default: re-runs the engine's non-raising `diagnose` LIVE and histograms
     detect-rejects by first-divergence site (each cluster: a representative +
     ref-vs-member bytes). LIVE means re-running after a factory fix shows the
     cluster shrink — a cheap fix-impact measure, no full re-batch (an 'ok'
     bucket counts members the current factory now accepts).
   - `--partials`: clusters verify partials by first writelog divergence from
     the jsonl `first_diff` (register→chip-role; **family-agnostic** — the SID
     register map is universal).

Usage: `python3 tools/divergence_census.py --engine dmc_v5 --results
tmp/dmc_v5_full_results.jsonl [--partials] [--cluster REASON] [--top N] [--reps N]`

Wired today: **dmc_v5** (via `pipelines.dmc.v5.factory.v5_diagnose`). Adding a
family = one `ENGINES` registry entry (diagnose/cluster_key/context). The
factory's masked compare was factored into return-first-divergence helpers
(`_diff_play_body`/`_diff_init_skel`) shared by the raising `dmc_v5_config` and
the non-raising `v5_diagnose`.

**Key triage finding (2026-06-16):** detection-unlock ≠ FULL. The DMC-V5
detect-reject residue (160 player_code_mismatch) is NOT the FULL bottleneck —
detecting them just exposes downstream extract/verify bugs (7/7 tested stay
non-FULL). The **verify-partials** are the bottleneck. Built on
[[reference_pc_trace_tool]] / `find_first_divergence`. Next step would be a
`triage-residue` SKILL (the per-cluster byte-level diagnosis + layout-vs-
sub-version classification) once the tool runs on a 2nd family.
