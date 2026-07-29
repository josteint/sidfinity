# Live-Signal Modulation + the Wave-Table Normal Form — USF schema draft (rev 2, for review)

**Status: rev 2 APPROVED by the owner 2026-07-28. Phase 1 (§5.1 —
grammar/writer/parser/types) LANDED 2026-07-28. Phase 2 (§5.2 — the wave
normal form: shared resolver `src/usf/resolve.py::resolve_wave_table`,
extract re-derivation assert, composer materializer, OPT-IN emission via
`write_dmc_usf`) LANDED 2026-07-28: A/B byte-identity 59/59 incl. every
chain-resolved hard case, adoption 58/59, corpus check + full regression
green. Phase-2 lesson: normal-form emission is opt-in per writer and any
merge path consuming a written part must `denormalize_wave_table` — the
regression caught the pointer-orphaning class twice (2SID merge sketch,
MA heterogeneous). Phase 3 SCAFFOLDING landed 2026-07-28 (full vocabulary + grammar/types/
writer/parser incl. voiceless globals; extract stamping + composer
dual-form derivation) with EMISSION GATED OFF: implementation surfaced
that sparse-signal records' captured values are LOAD-BEARING INIT PRIMING
(the composer seeds its sparse glide vars igla/iglb from them, ledger
C11) — "signal replaces the value" drops them, so the promised MD5 gate
is unattainable as drafted. §8 RESOLVED (owner, 2026-07-28): option (a) — the sparse-glide seeds
moved to typed `init.voice_state` fields (`glide_note`/`glide_target`),
and PHASE 3 LANDED 2026-07-28: named-signal emission is the default
(SIDFINITY_SIG_OLDFORM = the A/B lever, retired at the corpus sync);
the composer window-fill skips signal slots and sources igla/iglb from
the init fields (legacy fallback kept for old-form files). Gate: A/B
write-stream identity 16/16 across all live-signal classes (6 seeded
gla carriers, sectpos, dense-state, plain, chain-resolved), corpus
11,973/11,973, full regression green. PHASE 4 LANDED 2026-07-28
(§5.4): positional pool emission for wave_position carriers — the
composer emits the full 256-cell stated table verbatim at its
positions when a carrier's USF has one (proof: every program resolved
over the emitted table equals its materialized form, else fall back
to the repack), the norm's wavepos_layout / start-on-marker
exclusions lifted (chasers' wave_start = the raw marker cell; the
chase and its wjmp write happen natively on the positional path), the
2SID merge carries the CARRIER chip's table (others stay
resolved-copy; both-carriers-differing falls back), and the
_wave_layout_verbatim relaxation gate re-keyed on the READ-TARGET
voice's programs. Targets: Fantastic_Dreams + Supreme + Rabies_Babies
FULL (+3); Kordiaukis_01_2SID play streams now fully match — its
residual is a per-IRQ-trichotomy Check-A artifact (the orig defers
chip-2 init into frame 2, see project_dmc); Calf_Love_2 sub 1 /
Deprave_7_tune_3 blocked elsewhere (track-walk decode / continuation
into unstated cells). The §3.3 idle-walk `wavepos` seed was NOT
needed by any carrier and per §3.2 name-on-proof is NOT added until
one proves it. PHASE 5 (corpus sync) LANDED 2026-07-29: full f1
batch re-run on r128b code (5338/5401 FULL + 63 partial, 0 error),
`dmc_mass_write` sync (5338 written, 0 err, 4 drifted ex-FULL orphans
removed, 9/9 path-stratified disk audit), `usf_corpus_check`
12,001/12,001. The SIDFINITY_WT_OLDFORM / SIDFINITY_SIG_OLDFORM A/B
levers RETIRED (byte-identity gate 15/15 fresh-vs-stored .usf+.sid,
smoke 6/6, full regression). The `live(...)` PARSE form and the
resolved-copy wave fields are NOT deleted: 52 stored .usf outside f1
(v5 / family-2 — extracts not yet migrated) still carry live(), and
the resolved-copy form is load-bearing on the 2SID/compilation/
heterogeneous merge paths. Their deletion rides the v5/family-2
extract migration (the §7 remaining question), not this sync.**

## 8. Phase-3 open decision — sparse-signal seeds

A live record's captured (lo, hi) bytes are noise for DENSE signals but
are the INIT-LEFTOVER PRIMING for SPARSE ones (`glide_note` /
`glide_target`: written only by glide rows, so the capture = the file
image's leftover, which the composer must seed its vars from — C11).
Options: (a) move the seeds to `init.voice_state` (their §4.5 home;
schema fields + extract/composer moves; signals then cleanly replace
slots); (b) keep the record's int slots AND add the signal as extra
record elements (no seed migration; the slot value's meaning becomes
"captured/seed byte"). (a) is the principled shape; (b) is the smaller
diff. Owner decision pending. Rev 1 proposed a per-step
position list (`wave_step_pos`); review against C32 ("stated notation")
replaced it with the wave-table normal form (§4) — the list was a
projection of the table, stored redundantly beside resolved copies.
Companion evidence: `tmp/live_signal_census.out` (2026-07-27 census over
8,943 stored `.usf` + fresh extracts of all 102 queued partials);
triggering diagnosis: `project_dmc` r125 open note
(Imaic/Fantastic_Dreams).

---

## 1. The musical concept

A voice's pitch (today; potentially PW/filter later) can be driven by a
**live engine signal** — a value that evolves as the tune plays, sampled at
the moment a wave step or note event reads it. In synthesis terms this is
cross-modulation: "pitch follows the neighbour voice's sequencer position."
In HVSC DMC family-1 it arises from the engine's unchecked 96-entry pitch
table — a wave step's pitch offset pushes the index past the table into the
state block — but per the Core Tenet the *mechanism* is irrelevant: what
the music does is sample a named, describable generator. The census proves
this is a family-wide trait: **~750+ landed members** already depend on
live-served reads. Per the owner's direction this becomes a first-class,
complete USF feature — part of the repertoire, whether tunes reached it
deliberately or by data accident.

## 2. What exists today (the two half-measures being replaced)

1. **Live reads via index + hidden map.** `Instrument.offtable_freq`
   records: `at(off, note, lo, hi)` for static window bytes and
   `live(off, note, lo, hi)` for live-served reads, whose *meaning* (which
   engine variable the window index lands on) lives in a composer-side
   Python table (`DMC_OFFTABLE_STATE` + sectpos/wavepos rows). The USF
   speaks in raw indices; the semantics hide in the composer — the §8
   smell in miniature.
2. **Wave programs as resolved per-instrument copies.** The editor's
   actual medium is ONE shared, position-indexed wave table with jump
   markers; instruments are start pointers into it. USF today stores
   per-instrument resolved copies (+ `wave_table_pos` when layout had to
   be preserved) — effective materializations of the stated table, i.e.
   exactly the redundancy class C32 canonicalized away for orderlists and
   pattern state (the FC phantom-duplicate lesson). The duplication is
   also why live `wave_position` serving kept failing: the labels the
   music sonifies belong to the table, and the copies had lost them.

## 3. Feature 1 — named live signals

### 3.1 Signal references replace the `live` flag

One record form; each byte slot of an off-table record is either a literal
or a **named signal**:

```
offtable_freq: at(163, 48, $12, wave_position(v1))
               at(96,  48, sector_position(v3), $07)
               at(131, 48, $00, glide_note(v2))
```

- Literal ⇒ the static captured byte (today's `at`, unchanged).
- `signal(voice)` ⇒ the value is sampled live from that generator at each
  read. The `live(...)` form is deleted after migration.

The composer maps each signal name to its own internal variable — that
mapping is *mechanism* (engine-side, address-free, allowed). What §8
forbids — USF meaning defined by a composer-side table keyed on raw
indices — is gone. (`off`/`note` stay in the record: they are the musical
cause of the read.)

### 3.2 The signal vocabulary — name-on-proof

**Growth rule (resolves rev-1 open question 1): a signal name enters the
vocabulary when a member verifies FULL using it** — observation of a read
alone does not mint a name. This is the Completeness test applied as an
admission rule; it keeps the enum small and every value learnable (§7:
generators with describable shapes, not opaque engine indices).

Tier-1 names, carriers already landed (census live-member counts):

| Signal | Musical shape | Carriers |
|---|---|---|
| `glide_note(v)` | the voice's stored glide start note — steppy held pitch | ~340 |
| `sector_position(v)` | row cursor in the current sector — sawtooth per sector | ~130 |
| `wave_position(v)` | wave-table cursor — ramp with program-defined hops | ~77 |
| `freq_base_lo(v)` / `freq_base_hi(v)` | current base pitch bytes — follows the melody | dozens |

Observed-but-unproven tail (`note_offset`, `transpose`, `row_duration`,
`speed_counter`, `pwstep`, `wjmp`, …): stays honest residue until its
carrier lands; the C6/C11 event capture is the discovery mechanism.

### 3.3 Value fidelity per signal

- `glide_note`, `freq_base_*`: the composer already tracks these 1:1 —
  no new data.
- `sector_position`: solved in r120 (`runon` + per-entry base threading) —
  the feature re-homes its serving, no new data.
- `wave_position`: made faithful *structurally* by Feature 2 — the labels
  the signal shows are the stated cell positions of the wave table (§4);
  no shadow mechanism, no auxiliary position field. The walk's starting
  label for a voice freewheeling before its first note is per-subtune
  engine-state priming — a `wavepos` seed in the existing
  `init.voice_state` block (trichotomy §4.5, same home as the C31
  per-subtune idle priming).

## 4. Feature 2 — the wave-table normal form (stated notation, C32)

### 4.1 Representation

DMC wave content becomes a **sparse position-indexed table block** — the
editor's own data structure:

```
wave_table {
  0:   ctrl $09 freq $02
  1:   ctrl $03 freq $02
  ...
  5:   jump 4          ; the $90+n marker, stated as a jump distance
  160: ctrl $09 freq $02
  ...
}
```

- Cells keyed by position 0-255 (the engine's cursor is 8-bit; every walk,
  including Fantastic_Dreams' wrapping hopper, lives inside this one
  position space — rev 1's "off-table walk" was a signed-arithmetic
  misreading).
- Markers are stated as `jump` cells (musical: "loop back n"), not raw
  `$90+n` bytes.
- **Sparse and reachability-bounded (C7 discipline): only cells the music
  reaches** — programs, walked/wrapped cells, C19 poke targets — are
  stated; co-located junk the music never reads is never carried.
- Instruments' `wave_ctrl` / `wave_freq` / `wave_loop` /
  `wave_table_pos` / `wave_start_on_marker` dissolve into a single
  `wave_start: <position>` pointer (+ the existing per-instrument
  non-wave fields, unchanged).

What this buys, beyond honesty:

- **Shared content stated once.** Overlapping programs and shared tails
  (common in the corpus) stop being duplicated — the C8 dedup/overflow
  machinery loses its reason to exist for this family.
- **`wave_position` labels are inherent.** The sonified values ARE the
  stated positions; no second field can disagree with the content.
- **Runtime pokes become natural.** The C19 animator/glide-neutered
  wedges that poke wave cells target one stated cell, not N copies.
- **Cross-engine shape.** FC and GoatTracker share the
  pointers-into-shared-tables medium; the block is engine-neutral.

### 4.2 Composer mechanism

- **Carrier members** (any `wave_position` signal reference): the pool is
  emitted AT the stated positions — the composer's live cursor then equals
  the original's labels natively. No shadows, no label tables.
- **Non-carriers**: the composer stays free (Core Tenet) to keep today's
  repacked pool — programs reconstructed from the table through the ONE
  shared resolution interpreter (C32's `src/usf/resolve.py` pattern) and
  packed exactly as today, keeping every already-FULL member's build
  **byte-identical** and the migration gateable.
- The extract RE-RUNS the resolver against its own walk (both passes) and
  refuses wholesale on mismatch — C32's re-derivation assert, verbatim.

## 5. Migration plan (phased, each phase gated)

1. **Grammar/writer/parser** for the signal form + the `wave_table` block;
   `live(...)` and the per-instrument wave fields stay parseable during
   transition. Gate: `usf_corpus_check` green.
2. **Wave normal form (carrier refactor, C33/C32 discipline)**: extract
   emits the table block; composer reconstructs via the shared resolver
   and repacks as today. USF text changes corpus-wide; every already-FULL
   member's rebuilt `.sid` must be **MD5-identical** (golden gate over the
   portfolio + a stratified sample; full regression).
3. **Signal re-homing (carrier refactor)**: named signals replace `live`
   flags; composer derives redirects from names; delete the index-keyed
   meaning of `DMC_OFFTABLE_STATE`. Same MD5 gate.
4. **`wave_position` completion (new behaviour)**: positional pool
   emission for carriers + idle-walk seed. Normal verify; targets the
   census wavepos partials (Fantastic_Dreams, Supreme, Rabies_Babies,
   Calf_Love_2_everytime, Kordiaukis_01_2SID, Deprave_7_tune_3).
5. **Corpus sync**: fold the regenerate + the `live`/old-field deletion
   into the pending (post-r112) mass-write; full regression before each
   commit.

## 6. The Principle's four tests

1. **Completeness**: each signal round-trips on its carriers
   (write-stream proof); admission to the vocabulary REQUIRES the proof
   (§3.2).
2. **No escape hatch**: names, not indices; the composer's name→variable
   map is mechanism; no USF content selects an engine identity; the
   stated table is the author's own medium, not a byte blob (sparse,
   reachability-bounded, markers as musical `jump` cells).
3. **Interpolation sanity**: signal choice is a genuine categorical (like
   `shape: triangle|square`) — interpolation undefined by design; cell
   positions and jump distances are ordered arrangement ints.
4. **Cross-engine reuse**: wave-table cursors and row cursors exist across
   the tracker genre; both the signal names and the table block transfer
   verbatim if other families surface the idiom.

## 7. Resolved (rev 1 → rev 2) and remaining questions

- ~~`wave_step_pos` list vs table block~~ → **table block** (C32; the
  list was a redundant projection; rev 1 §3.3 superseded).
- ~~Vocabulary cut~~ → **name-on-proof** (§3.2).
- ~~`live(...)` deletion timing~~ → **rides the corpus sync** (C20
  machinery covers it).
- Remaining: none blocking — implementation ordering within phase 2
  (which families' extracts move first: DMC v4 only, or v5 in the same
  pass) to be decided at phase-2 start from the corpus-check family map.
