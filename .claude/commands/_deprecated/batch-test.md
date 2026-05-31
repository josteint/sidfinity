Run full batch test across all supported engines and update status.

## Procedure

1. Run the full scope through the pipeline (all parseable SIDs)
2. Collect Grade S/A/B/C/F counts per engine
3. Update grades.db with per-song results
4. Append a row to docs/benchmark.csv
5. Update CLAUDE.md status line
6. Update project_pipeline_status.md memory
7. Rebuild regression registry if Grade A count increased
8. Report: total Grade A, per-engine breakdown, delta from last run

## Key files
- `src/gt2_triage.py` — batch test (has find_gt2_sids, parallel pipeline)
- `data/grades.db` — per-song grade history
- `docs/benchmark.csv` — Grade A count over time
- `src/player/regression_test.py` — regression suite + registry rebuild
