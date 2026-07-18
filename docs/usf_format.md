# USF — format contract

USF is the on-disk format for the project's *Unified SID Format*
representation of SID music. One `.usf` file holds everything except
sample audio; samples live in sibling `.flac` files.

The format is the load-bearing input to the composer. The composer
MUST NOT peek at any other source — `usf + flacs → sid` is the whole
input.

**The block-by-block reference IS `src/usf/grammar.lark`.** Its
comments are normative: every block, field, and flag is defined and
documented at its rule site, and there is deliberately no second
copy of that reference here (a prose duplicate of the grammar drifted
badly twice; this document now carries only what the grammar cannot —
conventions, design rationale, and cross-component contracts).
Parser/writer live in `src/usf/`.

## Goals

- Single source of truth for one tune.
- Human-readable, human-editable in any text editor.
- Footgun-minimal: a small edit either keeps the song consistent or
  fails parse with a precise error.
- Round-trip stable: `parse → write` is byte-identical.
- Engine-agnostic structure; engine-specific fields live in
  `params:` and named effect tokens.

## Files

For tune `Chimera`:

```
Chimera.usf
Chimera.sample2.flac           ; only present if subtune 2 is digi
Chimera.sample3.flac           ; only present if subtune 3 is digi
```

- The `.usf` file is UTF-8.
- Sample files use the convention `<basename>.sample<N>.flac` where
  `N` is the PSID subtune index (0-indexed). References are relative
  filenames, resolved against the USF's own directory at build time.
- Sample sidecars carry per-sample metadata in Vorbis comments
  (`native_bits`, `method`, `timer_source`; see
  `.claude/memory/reference_digi_pipeline.md`).

## Lexical conventions

- Comments start with `;` and run to end of line. They are lossy —
  the writer does not preserve them across a parse/serialize round
  trip.
- Whitespace and blank lines are not significant beyond separating
  tokens.
- Identifiers: `[A-Za-z_][A-Za-z0-9_]*`.
- Integers: bare decimal (`12`), or `$`-prefixed hex (`$40`). Never
  `0x40`.
- Strings: double-quoted, e.g. `"Rob Hubbard"`. Used only for PSID
  metadata fields where the content is free-form.
- Block delimiters: `{` and `}`. List delimiters: `[` and `]`,
  comma-separated (byte lists are space-separated).

## Top-level shape

The grammar's `start` rule enforces the order: `psid`, `params`,
`init`, then the optional engine-behavior blocks, then the FC aux
program/table blocks (any order among themselves), then `instrument`
blocks, then `subtune` blocks. A minimal file is `psid { ... }
params { } init { }` plus one subtune.

## No `version:`, no `engine:` — deliberately

Earlier revisions opened with `version:` and `engine:` fields. Both
are gone. There is no format version token (the grammar IS the
version), and there is deliberately no engine identity anywhere in
the file: the composer is engine-blind (`docs/the_principle.md` §8) —
per-engine differences ride `params` values and named feature fields,
never an engine name the build could dispatch on. For the same
reason no `params` key is ever a `*Kind` enum: every field is a
value or a small musically-named keyword set (§7).

## The elidability principle

Every dimension is omitted at its identity value: a single-chip tune
never mentions chips, an untransposed orderlist entry is a bare
pattern id, an instrument without an effect omits the field cleanly.
The written file contains only what the music uses.

## Multi-SID (2SID / 3SID) model

A multi-SID tune is N independent single-chip tunes in one file:

- **Voices number through the chips** — voices 4-6 are chip 2, 7-9
  chip 3 (`chip = (voice-1)//3 + 1`). No `chip:` keyword exists.
- Chip COUNT is derived from the voice-block count (3, 6 or 9); chip
  I/O ADDRESSES are pipeline constants (chip 2 = `$D420`, chip 3 =
  `$D440`) stamped into the rebuilt PSID v3/v4 header — the
  original's addresses are environment plumbing, normalized away at
  extract (the I/O-space analogue of "the composer always emits the
  player at $1000").
- Per-chip forms extend the bare ones: `tempo N:`, `global N { }`,
  `init { sid N { } }`, `psid.sid2/sid3` (only when the original
  header states the extra chip's model explicitly).
- Verification is chip-tagged: the write-log encodes each write's
  chip as `reg = chip*$20 + reg`, each chip's substream is compared
  independently (cross-chip write order is physically unobservable —
  ledger C28).

## The `global` track — why named fields

Chip-global automation (`$D415-$D418`: dynamics + filter) cannot ride
a voice's note row, so it gets a sparse per-step event track whose
events name musical fields (`dyn`, `cutoff`, `res`, `mode`, `route`),
each holding its last value until re-named (running state). The
composer re-packs fields into registers; the per-tune write template
fixes their order relative to voice writes — the track says *what*
the global state is at each step, never *when within the frame* it is
written. A `GlobalEvent` is structurally a `NoteRow`: several named
fields on one row. The forbidden shape is an opaque register dump or
a library index, not multiple-named-fields-per-row.

## Validation layers

Layer 1 — parse: grammar check, produces a typed AST or precise
syntax error (line, column, expected vs got).

Layer 2 — references: every `iN` / `i:name` in a pattern resolves to
a defined `instrument`; every orderlist entry resolves to a defined
`pattern` in the same voice.

Layer 3 — lengths: per-pattern, durations sum to declared `length=`.

Layer 4 — sidecars (build time, not parse time): each referenced
`.flac` must exist next to the USF with internally consistent Vorbis
comments; the digi build fails cleanly otherwise.

Layers 1-3 must pass before the composer runs; layer 4 at digi build.

## Round-trip invariant

For any well-formed `Chimera.usf`, `write(parse(text)) == text` as
bytes. The writer:

- Emits fields in a fixed order within each block.
- Uses a canonical layout (one space after `:`, aligned columns in
  pattern bodies where feasible).
- Always emits `length=` on every pattern.
- Always emits `loop@N` even when N == 0.
- Never invents fields the parser would not produce.

## Things the format deliberately does NOT have

- Count fields. The parser derives `n_voices`, `n_patterns`,
  `n_subtunes`, `n_instruments` from the data.
- Implicit defaults that mask typos. Unknown tokens are errors.
- A `kind:` field on instruments. Instrument behavior is fully
  parametric.
- An `engine:` field or any engine identity (see above).
- `0x` hex (only `$`), `0` octal, scientific notation.
- Per-tick `@offset` markers (creates redundancy footgun).
- A cross-voice alignment check (free by default; lockstep would
  reject most polyrhythmic SID music).
- Comment preservation across round-trips.
