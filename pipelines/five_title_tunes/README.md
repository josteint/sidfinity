# 5 Title Tunes — multi-binary pipeline

The parent SID is a **dispatcher** that JSRs to one of 5 separate
Hubbard players based on the requested subtune. This pipeline rebuilds
each player independently (one sub-pipeline each) then overlays the 5
V3 binaries into the parent's address space and patches the
dispatcher's 10 JSR targets to point at our V3 init/play addresses.

## Status (auto-discovery, no per-sub tuning)

| Subtune | Length | Sub-pipeline | V3 base | Match rate |
|---:|---:|---|---:|---:|
| 1 | 1:01 | `pipelines/five_tt_0/` | $1000 | 48% |
| 2 | 0:40 | `pipelines/five_tt_1/` | $2500 |  5% |
| 3 | 0:51 | `pipelines/five_tt_2/` | $2F00 | 67% |
| 4 | 1:48 | `pipelines/five_tt_3/` | $3B00 | 44% |
| 5 | 2:00 | `pipelines/five_tt_4/` | $4900 |  0% |

All 5 subtunes are reachable through the dispatcher in the rebuilt
PSID (verified by siddump producing distinct writes per `--subtune N`).
The match rates reflect how well each sub's V3 rebuild — built from
Monty's clone with auto-discovered ft_base + PWM init only — matches
the original per-frame.

## Run

```bash
# 1. Split the parent into 5 sub PSIDs (idempotent; produces work_subs/)
python tools/split_multi_binary.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.sid \
    pipelines/five_title_tunes/work_subs

# 2. Extract USF for each sub
for n in 0 1 2 3 4; do python -m pipelines.five_tt_$n.extract; done

# 3. Build the 5 sub PSIDs (each at a different base address)
lake build sidgen_five_tt_0 sidgen_five_tt_1 sidgen_five_tt_2 sidgen_five_tt_3 sidgen_five_tt_4
for n in 0 1 2 3 4; do ./.lake/build/bin/sidgen_five_tt_$n; done

# 4. Overlay + dispatcher-patch → final PSID
python pipelines/five_title_tunes/combine.py
# → writes five_title_tunes.sid at repo root
```

## Architecture

```
data/.../5_Title_Tunes.sid        (parent, multi-binary)
    │
    ▼ tools/split_multi_binary.py
work_subs/sub_0.sid .. sub_4.sid   (5 standalone PSIDs)
    │ ┌──────────┐
    │ │ 5 × clone_hubbard_pipeline.py
    ▼ ▼
pipelines/five_tt_0/ .. five_tt_4/  (5 cloned Monty sub-pipelines)
    │
    ▼ extract + lake build + run
five_tt_0.sid .. five_tt_4.sid     (5 V3 rebuilds at non-overlapping
                                     base addrs: $1000/$2500/$2F00/$3B00/$4900)
    │
    ▼ combine.py
five_title_tunes.sid               (parent dispatcher + 5 V3 sub-binaries)
```

## Why per-sub base addresses

The V3 player + data is bigger than Hubbard's original binary for each
sub. The 5 V3 rebuilds can't all live at $1000 (the codegen default)
and they don't fit in the parent's original sub-binary memory
regions ($0C06, $18A3, ...). So each sub's `Codegen.lean`'s
`generateSID` is called with a different `baseAddr` parameter, and
`combine.py` places each V3 binary at its build-time base. The parent
dispatcher's JSR targets are patched to the V3 init/play addresses.

## Open work

Each sub-pipeline starts as a Monty clone with auto-discovered ft_base
and PWM init bytes. To push each subtune toward Grade A is the usual
per-SID investigation (py65 tracing, find which Monty-specific
codegen decisions don't apply, add this sub's own quirks).

Subtune 5 at 0% match is the most divergent — probably needs the most
attention. Subtunes 1, 3, 4 are in D-grade territory and likely have
similar issues to Monty's early days.
