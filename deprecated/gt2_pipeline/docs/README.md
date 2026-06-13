# Moved — GoatTracker player docs are now family-wide canon

The deep GoatTracker player-format docs that used to live here were
GoatTracker *player* research (current knowledge), not artifacts of this
deprecated USF-v1 pipeline. They were moved to the canonical family-doc
location on 2026-06-13 so future sessions discover them via CLAUDE.md's
"do we have engine-family docs?" check:

    pipelines/goattracker/docs/

Specifically:

| Was `docs/…` here          | Now at `pipelines/goattracker/docs/…` |
|----------------------------|---------------------------------------|
| `player_algorithm.md`      | `player_algorithm.md`                 |
| `player_variables.md`      | `player_variables.md`                 |
| `table_algorithms.md`      | `table_algorithms.md`                 |
| `gt2_data_layout.md`       | `gt2_data_layout.md`                  |
| `gt2_player_versions.md`   | `gt2_player_versions.md`              |

Relative `docs/…` references in this directory's archived Python
(`gt2_decompile.py`, `gt2_detect_version.py`) and README now point here;
follow the table above. The bundled GoatTracker source distributions
(`GoatTracker_2.65` … `2.77`, with `player.s`, `greloc.c`,
`goat_tracker_commands.pdf`) remain in this deprecated tree as the
ground-truth reference.
