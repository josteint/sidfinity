---
source_url: local: tmp/dmc_census.py over hvsc84.db (engine LIKE 'DMC%')
fetched_via: local read
fetch_date: 2026-06-12
author: SIDfinity census (pipelines/future_composer/engine_fingerprint.py, opcode-skeleton clustering)
content_date: 2026-06-12
reliability: primary
---

# DMC fingerprint census — 2026-06-12

10,676 SIDs (engine LIKE 'DMC%'), 0 errors. 688 distinct opcode-skeleton
hashes → 134 version families at Jaccard ≥ 0.85. Raw per-SID fingerprints:
`tmp/dmc_fingerprint.jsonl`; family membership: `tmp/dmc_families.json`
(regenerate with `tmp/dmc_census.py` if lost — repo tmp/ survives).

## Top families (97.8% of corpus in the top 4)

| # | SIDs | % | Identity | Evidence | Example |
|---|------|----|----------|----------|---------|
| 1 | 5401 | 50.6% | **DMC V4 canonical** | Jaccard **0.973** vs the carved Brian/Graffity V4 player (`dmc4_player_embedded_1000.bin`); sidid V4.x sig hits | `DEMOS/G-L/Knallen_Wars_Remix.sid` |
| 2 | 2889 | 27.1% | **V4-derived variant** (identity TBD: V2.x early / V4 pro / speed hack?) | 0.732 vs V4 — related but not the same player; no V4.x or V5.x_a sig | `DEMOS/G-L/Kajun_Klog.sid` |
| 3 | 1461 | 13.7% | **V5 line** | sidid V5.x sig; 0.832 to family 5 (sibling), 0.136 to V4 | `DEMOS/G-L/Katusha.sid` |
| 4 | 686 | 6.4% | **V5 line, distinct branch** | sidid V5.x sig; only 0.310 to family 3 | `DEMOS/G-L/Jupiter41.sid` |
| 5 | 34 | 0.3% | V5 sibling of family 3 (0.832, just under merge threshold) | | `MUSICIANS/E/Ed/Femmin3.sid` |
| 6 | 15 | 0.1% | **V6** | sidid V6.x sig; ~0.01 to everything else (different player entirely) | `MUSICIANS/B/Bayliss_Richard/Follow_That_Storm.sid` |

Remaining 128 families: ≤10 members each (long tail of hacks/customs).

## Pairwise Jaccard (top-6 reps)

```
        1      2      3      4      5      6
1   1.000  0.732  0.136  0.121  0.128  0.011   Knallen_Wars_Remix (V4)
2   0.732  1.000  0.158  0.145  0.152  0.012   Kajun_Klog (V4-derived)
3   0.136  0.158  1.000  0.310  0.832  0.025   Katusha (V5)
4   0.121  0.145  0.310  1.000  0.278  0.018   Jupiter41 (V5 branch)
5   0.128  0.152  0.832  0.278  1.000  0.026   Femmin3 (V5 sibling)
6   0.011  0.012  0.025  0.018  0.026  1.000   Follow_That_Storm (V6)
```

## Migration implications

- **Family 1 (V4 canonical, 5401 SIDs) is the target** — same FC lesson:
  one player, half the catalogue. We hold its exact player binary
  (carved from DMC 4 Editor 2025) as the disassembly seed, and V4 is the
  best-documented version (research.md + TND tutorial).
- Family 2 (2889) at 0.732 to V4 likely shares most of the V4 write
  model — identify it during/after the V4 migration by diffing its rep's
  disassembly against the annotated V4 one. If it's a V4 speed/pro hack,
  much of the extractor may carry over.
- V7 SIDs (V4 data-compatible per CSDb testimony) presumably land inside
  family 1 or 2 — the sidid classifier collapsed all of these to 'DMC'.
- Families 3+4+5 (2181) = the V5 line; V5's 8-byte instrument + 2-byte
  tables documented in `dmc_v5_format_notes.md`, but sector-command
  encoding still needs RE.
- Family 6 (V6, 15 SIDs) + the 128-family tail: deprioritize.
