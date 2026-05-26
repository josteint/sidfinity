# Baselines for the USF instrument-program refactor

This directory holds writelog snapshots captured from original Hubbard
SIDs. These are the ground-truth targets that the new schema's rebuild
must match (frame-for-frame, register-for-register; cycle counters
within a frame may differ).

See `docs/usf_instrument_program_plan.md` for the broader plan.

## Files

- `commando_original_writelog.txt` — `siddump --writelog --force-rsid
  --duration 30 --raw` of `demo/hubbard/Commando_original.sid`.
  Each line is one PAL frame: CSV snapshot then `|W:cycle:reg:val:...`
  write stream. 1500 frames (30s of PAL @ 50Hz).

## Regenerate

```
tools/siddump demo/hubbard/Commando_original.sid \
  --writelog --force-rsid --duration 30 --raw \
  > tests/baselines/commando_original_writelog.txt
```

## Compare against

```
python3 src/writelog_diff.py demo/hubbard/Commando_original.sid <rebuild.sid>
```

(or against the .txt directly — the diff tool re-runs siddump for both
sides, so the snapshot is mainly a historical reference / regression
canary; if siddump itself changes behavior, we want to know.)
