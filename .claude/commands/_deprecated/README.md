# Deprecated slash-commands

Four commands built around the older Grade A counting methodology
(sid_compare, F-grade investigation, rule mining). The USF v2 / Hubbard
byte-exact workflow doesn't use them — verdicts come from
`pipelines.hubbard.verify.verify_all` (byte-exact), not Grade A/B/C/F
buckets.

- `batch-test.md` — was: run full HVSC GT2 scope through pipeline, collect Grade S/A/B/C/F counts, update grades.db
- `crack-sid.md` — was: identify engine, try static parsing, build, compare grade
- `investigate.md` — was: find highest-scoring F-grade song, trace first wrong frame
- `mine-rules.md` — was: sample 50 Grade B songs, classify divergences, propose tolerance rules

If you want to revive one, move it back up one level and re-anchor it on
the current `verify_all` flow instead of the older sid_compare grading.
