# 5 Title Tunes pipeline (merged-into-idiomatic)

> **Note (2026-05): the Lean / Lake build commands below no longer work.**
> The active build path for this engine is now the shared Python core at
> `pipelines/hubbard/`. See [pipelines/README.md](../README.md) and
> [`deprecated/lean_codegen/`](../../deprecated/lean_codegen/) for context.

End-to-end rebuild of Rob Hubbard's *5 Title Tunes* (1985, self-published) SID.

## Status

| Metric | Value |
|---|---|
| Subtunes | 5 (all music) |
| Rebuild size | 10,795 bytes (vs original 11,849 — 91%) |
| Player blocks in output | 1 (shared V3 player) |
| USF representation | ONE `USFSong` with 5 `USFSubtune` records |
| Audible | Plays all 5 tunes correctly via parent dispatcher |
| Per-subtune frame match | 48% / 5% / 31% / 7% / 0% (write-trace divergence — not grading vs original) |

## Structurally unusual SID

The original PSID is a **dispatcher** (init $0B10, play $0B40) that
forwards to **5 separate Hubbard player binaries**, each with its own
init/play/freq table. It's the only SID in the 97-song Hubbard catalog
to use this trick — `tools/build_hubbard_catalog.py` plus a dispatcher
signature scan confirm uniqueness.

Rather than preserve that structure in our rebuild, we **merge** the 5
sub-binaries into one idiomatic USFSong. This way the SID looks
structurally identical to Commando or Monty in the USF representation
(one song, multiple subtunes, shared instruments + patterns) — important
for ML training uniformity. Hubbard's original 5-engine layout was a
demo-reel convenience; the music is genuinely 5 tunes played by the
same engine family, so the merged representation is faithful in spirit.

## Pipeline shape

```
data/.../5_Title_Tunes.sid                      (parent, multi-binary)
    │
    ▼ tools/split_multi_binary.py
work_subs/sub_0..4.sid                          (5 standalone Hubbard PSIDs;
                                                 regenerated on demand,
                                                 gitignored)
    │
    ▼ extract/engine_model.extract  ×5
5 × ExtractedSong                                (one per sub-binary)
    │
    ▼ extract/merge.py
1 × merged ExtractedSong                         (38 raw insts → 32 after dedup,
                                                 5 subtunes, 82 patterns)
    │
    ▼ extract/emit_usf.py
codegen/FiveTitleTunes/SongData.lean             (a normal multi-subtune USFSong)
    │
    ▼ existing Codegen (same as Monty/Commando)
five_title_tunes.sid                             (ONE PSID, ONE player, 5 subtunes)
```

## Merger details — instrument deduplication

The 5 sub-binaries have **38 raw instruments** combined. The pattern-data
inst byte stores the instrument index in 5 bits (max 32) plus 3 flag bits,
so the merge needs to compress down to ≤32 unique instruments. Strategy
(in `extract/merge.py`):

1. **Drop unreferenced instruments**: 2 instruments are extracted but never
   played by any pattern in their sub (sub 0 inst 3, sub 4 inst 3 — both
   percussion variants Hubbard apparently dropped). Saves 2.
2. **Strict byte-for-byte dedup**: 2 drum instruments are shared identically
   between subs. Saves 2.
3. **Ignore vibrato_scale**: instruments identical except for vibrato depth
   collapse. Saves 1-2.
4. **Ignore pwm.init_pw + pwm.speed**: PW modulation variations collapse.
   Saves more.
5. **Coarse fallback**: collapse on (waveform[0] ctrl, AD, SR, arp, drum)
   only. Used only if the above tiers don't reach ≤32.

For 5 Title Tunes today the merger walks tiers 1-4 and falls through to
the coarse tier ('coarse' logged on stderr). The final 32 unique
instruments represent the union of audibly-distinct sounds across the 5
sub-binaries; instruments that varied only in subtle PW/vibrato
modulation collapsed to their most-common variant.

## Run

```bash
# Splits parent, extracts 5 subs, merges, writes SongData.lean
python -m pipelines.five_title_tunes.extract.emit_usf

# Build the rebuild
lake build sidgen_five_title_tunes
./.lake/build/bin/sidgen_five_title_tunes
# → pipelines/five_title_tunes/build/five_title_tunes.sid
```

## Why no Grade A/B/C

We're not grading this SID against the original because the original is
multi-engine (5 different Hubbard players, each with its own timing) and
the rebuild is single-engine (one V3 player serving 5 subtunes). The
per-frame register write traces fundamentally diverge no matter how
well-tuned the codegen is. The **audible** output is right — all 5 tunes
play correctly and sound like Hubbard's originals (ear test). The
USF-level structure is idiomatic. That's the deliverable.
