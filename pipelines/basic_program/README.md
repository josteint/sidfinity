# Basic_Program pipeline — SID → USF → SID for RSID-BASIC tunes

The Basic_Program family is unlike every other family in this repo: there is
**no machine-code player to reverse-engineer**. Each member is an RSID v2 file
whose payload is a tokenized Commodore BASIC V2 program at `$0801` that POKEs
the SID chip; the "engine" is the C64 BASIC + KERNAL ROM interpreter, and each
tune is its own hand-written micro-program (magazine type-ins, the 100% BASIC
Project, 1980s scene one-offs). The pre-migration research dossier lives in
[`docs/`](docs/README.md) — format spec, interpreter timing, float core,
provenance; read it for anything about the *originals*. THIS file documents
the **pipeline as built** and its current state.

Because there is no player, the pipeline is a **trace-lift**: capture the
original's SID write stream under libsidplayfp (ground truth; needs the C64
ROMs — `SIDFINITY_ROMS_DIR`, see the top-level CLAUDE.md), lift the stream
into a semantic model (steps, voices, notes, globals), write USF, rebuild a
PSID from the USF with our own 6502 player, and verify the rebuild's write
stream against the original. The core tenet applies unchanged: the verdict is
the write stream, never the BASIC program's structure.

## Build path

```
hvsc85/<member>.sid                             (RSID, BASIC payload)
  └─ semantic_lift.build_model(sid, dur)        capture_real → segmentation →
  │                                             steps/templates/glides/sweeps
  └─ usf_roundtrip.model_to_usf(model, nf=…)    → UsfFile (NF or legacy form)
  └─ usf_roundtrip.usf_to_model(usf)            the READER (reconstruction)
  └─ build_psid(model)                          our 6502 player + PSID header
  └─ verify: trichotomy verdict                 Check A end-of-init state +
                                                aligned play stream (C21)
```

- **`usf_roundtrip.best_attempt(rel, dur)`** is the production entry: it runs
  the NORMAL-FORM attempt chain FIRST and falls back through the legacy
  variant ladder (force_split / min_trim / detect_song_end /
  detect_modulation / multi_template / glide, then gap_exact passes), so NF
  adoption can never regress coverage — a member that can't take the normal
  form keeps its legacy encoding, and only a FULL verify wins at all.
- **`family_batch.py`** sweeps the whole family (resumable, code_hash-gated
  rows; `--write` mass-writes `.usf` + `.sidfinity.sid` beside the HVSC
  original for FULL members).
- **`usf_roundtrip.verify_usf(usf_rel, sid_rel, dur)`** is the
  production-path regression verdict: STORED `.usf` → model → SID → writelog
  vs the original. ⚠ Known limitation: it captures at the given duration with
  no music-start probe, so a tune with a long pre-music intro ("PLEASE WAIT"
  screens) false-fails at the raw DB songlength — `best_attempt` probes up to
  240 s for the real music start; `verify_usf` does not. Known artifacts:
  God_Save_the_King, Casino_Poker, Pong (all verify clean at honest windows).
- The regression tier is `pipelines/basic_program/regression_portfolio.json`,
  wired into `tools/regression.py`.

## The two USF forms

**Legacy (packed write model)** — the C17 canonical form for arbitrary write
schedules: K per-shape templates + per-step template ids + packed scalar
params (`bp_atk*/bp_t*/bp_tid*/bp_init*/…`). Complete and exact, but the
params block is a per-tune engine program — the representation principle's §3
"complete but unlearnable" pole. It remains the fallback and the honest
residue form.

**Normal form (NF)** — the target representation, structurally identical to
the tracker families:

- **Rows are true tracker events**: notes with durations (hold = sounding
  span), at most one merged rest between events, timbre-setup rests carrying
  their instrument, `tie`/`no_release` fx, glide heads with
  `glide_up/down/ticks/hold` fx (intermediates are implied, not stored).
- **Named order declarations** (`bp_order_<sig>: "v1_flo v1_fhi / v1_ctrl"`)
  carry the per-event-type register WRITE ORDER (attack / release) — the one
  place engine mechanism legitimately lives, the C16 knob shape. Signatures
  use adaptive coarseness: the writer picks the minimal flag subset
  ({bytes, tie, norel, ins}) that yields a conflict-free sig→order map, so
  typical tunes carry ~2 readable declarations.
- **Init is typed** (`init.sid` priming via the trichotomy: master_vol,
  filter, envelope_prime, ctrl_init, freq_init) — no raw init byte lists.
- **Sections as patterns**: a tune whose poke loop CHANGES between sections
  splits each voice's rows into one Pattern per section, sequenced by the
  Orderlist (the multi-pattern structure of FC/DMC), with declarations scoped
  per section (`bp_order_p{N}_<sig>`). The writer segments greedily at finest
  signature detail, caps at 8 sections (beyond = interleaved alternation,
  honest residue), and refuses boundaries that would split a note row.
- **Sweeps are readable** (`bp_sweep{v}_values/_sections`, ledger C1 shape);
  `bp_song_end` is a readable register string; rho/legato/loop_period are
  DERIVED, not stored. NF params reduce to `bp`, `bp_loop_to`, and the order
  declarations.
- **The reader is a parser** (2026-08-11): the stored declarations form a
  GRAMMAR over step groupings, and reconstruction parses the per-(onset,
  voice) ordered event queues against it — each step consumes the next
  unconsumed event of some voice subset (per-voice order preserved), must
  resolve a stored declaration, and must have instruments established for its
  instrument registers. The parse is whole-song with backtracking (iterative,
  node-capped) because a wrong local grouping changes the step count and
  drifts every later step's global-event alignment. This is what represents
  the interpreter's slowness faithfully WITHOUT putting the write schedule in
  the USF: a BASIC chord whose pokes span 3-4 frames (splitting mid-voice)
  round-trips through clean rows + the decl grammar. `BP_NF_DEBUG=1` traces
  parse rejects.

## State (2026-08-11 — refresh this section, per-round history lives in `.claude/memory/project_basic_program.md`)

- Catalogue: **524 members** on HVSC #85 (#85 added 38: 2 new + 36 newly
  classified after the sidid path-truncation fix).
- Coverage: **493/524 (94.1%) FULL**, stored + audited (every stored `.usf`
  production-verifies; 3 known verify_usf window artifacts, above).
- NF adoption: **304/493 (62%)**; 189 legacy-form FULLs.
- Verification: full write-stream match (trichotomy verdict), window =
  songlength × 1.1 (extended by the music-start probe where the intro
  exceeds it, capped 240 s).

### Residue taxonomy (all measured; census data in `tmp/bp_*census*.json`)

| bucket | ~n | nature |
|---|---:|---|
| interleaved order alternation (>8 sections) | 55 | honest residue (July call, reaffirmed 2026-08-11) — the tune's poke loop alternates orders too finely for sectioning |
| verify-diverge legacy | 56 | writer+reader reconstruct, stream diverges — value-level causes, NOT yet censused (the next lever) |
| writer misc | ~40 | `nf_conflict` 17 (release-timbre / beyond-$D418), `pure_global` 13 (no row anchor for a global-only step), `section_span` 3, small tails |
| not FULL at all | 31 | the coverage tail: `too_many_pitches` (vibrato > 96 freq slots — needs a vibrato effect representation), `legato_variable`, `overlap_diverge`, 1 round-trip-unstable (Somewhere_over_the_Rainbow: in-memory FULL but stored `.usf` rebuilds long — C20 fifth-layer shape, artifacts removed) |

## Gotchas that have each cost a session hour

- **Use the DB songlength for any per-tune probe.** A hardcoded duration
  changes the capture window and thereby the LIFTED MODEL; a longer window
  can make a convertible member look unconvertible (Chromatic_Boogie,
  In_Your_Head). The batch/sweep tooling derives dur from the catalogue.
- **verify_usf's window** has no music-start probe (see above) — a false
  fail at raw dur with `len_b=0` and tiny `len_a` is the signature.
- **A backtracking parse failure reports the deepest retreat point**, not
  the cause site; the true dead end may be a k-alignment drift introduced
  hundreds of steps earlier.
- **Without the C64 ROMs, every member reports `unsupported:too_few_steps`**
  — a silent wrong verdict, not a crash (the BASIC interpreter never runs).
