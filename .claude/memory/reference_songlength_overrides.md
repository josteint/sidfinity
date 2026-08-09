---
name: songlength-overrides
description: tools/songlength_overrides.json corrects anomalous HVSC songlengths. Apply when an HVSC duration is clearly defaulted/wrong (e.g. 4s for a 56s natural loop).
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

`tools/songlength_overrides.json` is the durable home for corrections
to HVSC's `Songlengths.md5`. `build_sid_db.py` applies it after the
HVSC ingest step, so the corrected values persist across HVSC
re-fetches and into the `songlength_s` column of `hvsc85.parquet`.

## When to use

When HVSC has a clearly anomalous duration for a SID we've migrated.
Diagnostic pattern:

1. Original SID stops far short of its natural musical content
2. Engine has no song-end mechanism — it just loops
3. Sibling tunes in the same cluster/composer use a consistent
   "natural / 1.2" rule but this one was defaulted (often to ~4s)

For these, deriving the correct songlength from the engine's
deterministic state model is principled and easy.

## How to derive

For a loop-forever engine like Bowden-canonical, the natural song
duration is one full play of the longest voice's orderlist:

    natural_s = max(K_v) × tempo / 50

If most sibling tunes in the cluster use `HVSC = natural / 1.2`,
apply the same rule to outliers; otherwise just use `natural`.

## Format

```json
{
  "<md5 hex>": {
    "seconds": <float>,
    "path": "MUSICIANS/.../Foo.sid",
    "reason": "one-line justification"
  }
}
```

Keyed by md5 of the original SID file (same key HVSC uses).

## Related

- [[reference_hvsc_db]] — the parquet catalogue where these values land
- [[project_bowden_canonical]] — the cluster that surfaced the need
- [[feedback_subtune_frames_not_arbitrary]] — verify windows are
  derived from songlength_s × 1.1, so corrections here directly
  widen the verify window
