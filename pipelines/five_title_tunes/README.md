# 5 Title Tunes pipeline

End-to-end rebuild of Rob Hubbard's *5 Title Tunes* (1985, self-published) SID.

## Structurally unusual SID

This is **not** a single Hubbard player serving 5 subtunes. The PSID
wraps a **dispatcher** at $0B10 (init) and $0B40 (play) which forwards
to one of **5 separate Hubbard sub-binaries**, each with its own
init/play and its own freq table:

| Subtune | Init | Play | Freq table | Length |
|---:|---:|---:|---:|---:|
| 0 | $1850 | $0C06 | $0F6A | 1:01 |
| 1 | $1FA9 | $18A3 | $1C07 | 0:41 |
| 2 | $280C | $1FFC | $2360 | 0:51 |
| 3 | $310C | $283C | $2BA0 | 1:48 |
| 4 | $38CF | $315F | $34C3 | 2:01 |

`rh_decompile` parses only the first sub-binary (it finds 1 valid
song, not 5).

## Current state

| Metric | Value |
|---|---|
| Subtunes rebuilt | 1 (subtune 0 only — the first sub-binary's tune) |
| Verification | Grade D, 44.7% snapshot match against original |
| Open work | Investigate divergences; add other 4 sub-binaries |

Auto-discovered constants applied to the Monty clone:
- ft_base: $0F6A (subtune 0's freq table)
- pulsedelay init: [$00, $00, $01]
- pulsedir init:   [$00, $00, $01]

These give Grade D out of the box from the cloning automation. The
remaining ~55% snapshot gap is the usual per-SID work: our V3 player
emits a much fatter `init` write trace than Hubbard's, and the ctrl/AD
write timing differs across the song.

## To rebuild all 5 sub-tunes

The pipeline would need a **multi-binary mode**: extract each sub-binary
into its own SongData, build 5 separate codegen libs, and emit a
dispatcher PSID that forwards to the right one. That's a bigger
structural change to our codegen than any single-binary 1985 SID needs.

## Run

```bash
python -m pipelines.five_title_tunes.extract     # default subtune 0
lake build sidgen_five_title_tunes
./.lake/build/bin/sidgen_five_title_tunes
python src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.sid \
    five_title_tunes.sid
```
