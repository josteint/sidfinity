# Live-Signal Modulation — USF schema draft (for review)

**Status: DRAFT 2026-07-28 — not adopted. Written for owner review; nothing
in the pipeline implements this yet.** Companion evidence:
`tmp/live_signal_census.out` (2026-07-27 census over 8,943 stored `.usf` +
fresh extracts of all 102 queued partials); diagnosis that triggered the
design: `project_dmc` r125 open note (Imaic/Fantastic_Dreams).

---

## 1. The musical concept

A voice's pitch (today; potentially PW/filter later) can be driven by a
**live engine signal** — a value that evolves as the tune plays, sampled at
the moment a wave step or note event reads it. In synthesis terms this is
cross-modulation: "pitch follows the neighbour voice's sequencer position."
In HVSC DMC family-1 this arises from the engine's unchecked 96-entry pitch
table — a wave step's pitch offset pushes the index past the table into the
state block — but per the Core Tenet the *mechanism* is irrelevant: what the
music does is sample a named, describable generator. The census proves this
is a family-wide trait, not a curiosity: **~750+ landed members** already
depend on live-served reads.

The design goal, per the owner's direction: make this a first-class,
complete USF feature — "totally fine to sonify this way" — rather than
per-member patches. Some tunes may even do it deliberately; either way the
repertoire is richer and the representation is honest.

## 2. What exists today (the half-measure being replaced)

`Instrument.offtable_freq` records: `at(off, note, lo, hi)` for static
window bytes (values inline — fine, unchanged in spirit) and
`live(off, note, lo, hi)` for live-served reads. The **meaning** of a live
read — *which* engine variable the index lands on — lives in a
composer-side Python table (`DMC_OFFTABLE_STATE` + the sectpos/wavepos
rows), keyed by raw window index. The USF speaks in indices; the semantics
hide in the composer. That is the §8 smell in miniature, and every new
carrier class is a bespoke fight (redirect rows, gating booleans,
`wavepos_layout`, …).

## 3. The schema

### 3.1 Signal references replace the `live` flag

One record form, where each of the two byte slots is either a literal or a
**named signal**:

```
offtable_freq: at(163, 48, $12, wave_position(v1))
               at(96,  48, sector_position(v3), $07)
               at(131, 48, $00, glide_note(v2))
```

- Literal ⇒ the static captured byte (exactly today's `at`).
- `signal(voice)` ⇒ the value is sampled live from that generator at each
  read. The `live(...)` record form is deleted after migration.

The composer maps each signal name to its own internal variable — that
mapping is *mechanism* (engine-side, address-free, allowed); what §8
forbids — USF meaning defined by a composer table — is gone.

### 3.2 The signal vocabulary (census-driven, tier 1)

Only names with verified HVSC carriers enter the vocabulary. From the
census (live members, landed corpus):

| Signal | Musical shape | Carriers |
|---|---|---|
| `glide_note(v)` | the voice's stored glide start note — steppy held pitch | ~340 |
| `sector_position(v)` | row cursor in the current sector — sawtooth per sector | ~130 |
| `wave_position(v)` | wavetable cursor — ramp with program-defined hops | ~77 |
| `freq_base_lo(v)` / `freq_base_hi(v)` | the voice's current base pitch bytes — follows the melody | dozens |
| `note_offset(v)` (wnote) | last wave-step pitch index | seen |
| `transpose(v)`, `row_duration(v)`, `speed_counter`, … | long tail | few each |

**Growth rule:** a new signal name requires ≥1 verified carrier (the C6/C11
event capture is the discovery mechanism). Un-named state reads stay
honest residue. This keeps the enum small and each value learnable —
passing the Principle §7 test (these are generators with describable
shapes, not opaque engine indices).

### 3.3 Value fidelity: the arrangement data each signal needs

A signal reference is only complete if USF carries whatever content makes
its *values* reproducible:

- `glide_note`, `freq_base_*`, `transpose`, `row_duration`: the composer
  already tracks these 1:1 (they are musical state) — **no new data**.
- `sector_position`: solved in r120 (`runon` flag + per-entry base
  threading) — the feature re-homes its serving, no new data.
- `wave_position`: needs the **editor wave arrangement** — the position
  labels the original's cursor shows. Two fields:
  - `wave_table_pos: N` (existing) — the consecutive case: step *k* is at
    label N+k.
  - `wave_step_pos: [p0, p1, …]` (NEW, optional, len == len(wave_ctrl)) —
    the general case for non-linear walks (off-table hoppers like
    Fantastic_Dreams' instrument 15). `wave_table_pos` is its degenerate
    shorthand; both are §8 arrangement, same category.
  - Idle/leftover walks: the walk's *starting label* for a voice that
    freewheels before its first note is per-subtune engine-state priming —
    a `wavepos` seed in the existing `init.voice_state` block (trichotomy
    §4.5; same home as the C31 per-subtune idle priming).

### 3.4 Composer mechanism (sketch)

Per-voice one-byte **label shadow** `owpos,x` = "the label the original's
cursor would show": updated at every wave step — `+delta` (assemble-time
constant, `orig_start − our_start`) for consecutive programs, table lookup
(`wave_step_pos`) for non-linear ones; seeded from the per-subtune priming.
Signal reads are served from the shadow (or directly from the composer's
existing variables for the no-new-data signals). All emission is gated on
the member carrying signal references — non-carriers stay byte-identical.

## 4. Migration plan (phased, each phase gated)

1. **Grammar/writer/parser**: accept the signal form; keep `live(...)`
   parseable during transition. Gate: `usf_corpus_check` green.
2. **Re-homing (carrier refactor, C33 discipline)**: extract emits named
   signals instead of `live` flags; composer derives its redirects from
   the names. USF text changes; every already-FULL member's rebuilt `.sid`
   must be **MD5-identical** (golden gate over the portfolio + a carrier
   sample per signal). Then delete the `live` form + the index-keyed
   meaning of `DMC_OFFTABLE_STATE`.
3. **`wave_position` completion (new behaviour)**: `wave_step_pos` +
   label shadow + idle seed. Normal verify gates; targets the census'
   wavepos partials (Fantastic_Dreams, Supreme, Rabies_Babies,
   Calf_Love_2_everytime, Kordiaukis_01_2SID, Deprave_7_tune_3).
4. **Corpus sync**: fold the regenerate into the pending (post-r112)
   mass-write; full regression before each commit.

## 5. The Principle's four tests

1. **Completeness**: each signal round-trips on its carriers
   (`verify_all`-grade write-stream proof); the census supplies the
   carrier lists.
2. **No escape hatch**: names, not indices; the composer's name→variable
   map is mechanism (no USF content selects engine identity); the raw
   window index disappears from the schema... *(note: `off`/`note` in the
   record remain — they are the musical cause of the read and stay.)*
3. **Interpolation sanity**: signal choice is a genuine categorical (like
   `shape: triangle|square`) — interpolation is undefined *by design*;
   the numeric fields (`wave_step_pos`, offsets) are ordered arrangement
   ints.
4. **Cross-engine reuse**: wavetable cursors and row cursors exist in FC /
   GoatTracker / most trackers — the names are engine-neutral and reusable
   verbatim if those families ever surface the same idiom.

## 6. Open questions for review

- Vocabulary cut: tier-1 names only now, or also pre-name the observed
  long tail (`pwstep`, `wjmp`, `filter_cutoff`, …) whose carriers are the
  wide-walking partials (Kordiaukis_01_2SID, Deprave_7_tune_3, …)?
- `wave_step_pos` vs representing DMC wave content as a position-indexed
  table block (C32-style "stated notation") — the list is smaller and
  non-disruptive; the table block is bolder but migrates every member's
  wave storage. Draft chooses the list.
- Whether phase 2's deletion of `live(...)` waits for the corpus sync or
  rides it (draft: rides it).
