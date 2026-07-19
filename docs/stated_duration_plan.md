# Stated-duration pattern rows — D6 piece 2 (2026-07-19)

The deferred deep half of D6 (docs/refactor_1_remaining.md) / the C32
boundary note: FC's `len=L` wrap pickup, FC's `(fc_id, init_len)`
pattern-variant materialization, and DMC's `~intro` orderlist decode
variants are ONE phenomenon — **sticky pattern-row state (duration, and
for DMC also instrument/volume) carried by the engine across pattern
boundaries**, which the extractors have been materializing into
EFFECTIVE per-row values, duplicating patterns per entry-context.

Endpoint: rows become **stated notation** — a row carries a
duration/instrument/volume only where the source stream states a
command; an absent value inherits from the previously played row
(across pattern boundaries, orderlist play order, over the loop wrap).
The three per-engine mechanisms dissolve into one engine-blind
representation + one shared resolution interpreter.

## Probe (2026-07-19, tmp/probe_{fc,dmc}_stated_dur.py)

FC standard family, all 2670 full+partial members:

| measure | count |
|---|---|
| physical fc patterns referenced | 43,963 |
| materialized `(fc_id, init_len)` USF patterns | 62,110 |
| **redundant duplicates (identical decode)** | **18,147 (+41% pool), in 2,580 members (97%)** |
| TRUE behavioral variants (decode differs) | 156, in 41 members |
| patterns with inherit-dependent head rows | 705, in 108 members |
| `len=L` voices today | 20 (19 members) |
| deep-chain wrap rejects (stuck partial today) | 6 voices (4 members) |

DMC v4 families 1+2, all 5,825 full+partial members:

| measure | count |
|---|---|
| members with `~intro` variants | 1,673 (29%), over 10,343 slots |
| variant carry channels | **vol 7,345 · instr 2,250 · instr+vol 746 · dur 2** |
| pattern pool effective → stated | 124,434 → 117,514 (−5.6%) |
| patterns with inherit-dependent head rows | 1,654 |
| fold-fail voices (stay on the legacy fallback) | 319 |

The decisive finding: DMC's `~intro` variants are ~100% **volume and
instrument** carry (duration carry: 2 slots corpus-wide), and zero
variants differ by anything besides the three sticky channels — so the
DMC side states all three (which the sector stream states uniformly as
command bytes; the extract already records them as `dcmd/icmd/vcmd`
byte facts), and the stated form provably subsumes the whole `~intro`
mechanism.

## Representation (shared, engine-blind)

- `NoteRow.duration: Optional[int]` — None = inherited. Grammar:
  `note_row: pitch INT? instr_ref? fx_flag*` (duration column omitted
  when absent). `NoteRow.instr` absent = inherit (ALREADY the FC
  convention — unchanged semantics, now normative). `vol=N` fx flag
  present iff the stream states a volume command (including `vol=0`);
  absent = inherit; leading-absent = 0 (the existing USF default).
- `Pattern.length: Optional[int]` — underivable without context for
  patterns with inherited rows; `length=` clause becomes optional and
  is omitted for such patterns. (No consumer reads it today except the
  Layer-3 sum check.)
- **Resolution interpreter** (`src/usf/resolve.py`, shared): walks a
  voice's orderlist in play order (intro pass + loop cycle for stated
  orderlists), threading (duration, instr, vol) sticky state through
  pattern rows; returns per-entry effective rows. Seeds: per-voice
  `init.voice N { dur_field }` (existing InitVoice field, trichotomy
  §4.5 engine-state priming; FC emits `dur_field: 1` only for voices
  whose leading rows actually resolve from engine init) and
  `init.voice N { instr }` (existing field) for a leading-absent
  instrument. DMC's seeds are 0 = the field defaults (no emission).
- **Layer 3** becomes: patterns with all-stated rows + declared length
  keep the sum check; voices containing inherited rows are checked by
  running the resolver — every omitted value must resolve (prior
  statement or seed), else a precise validation error.
- Dissolved: `Orderlist.loop_length` (`len=L`), `Orderlist.
  intro_entries` (`~i`), FC's `(fc_id, init_len)` dedup key, DMC's
  `dur_cmd`/`instr_cmd`/`vol_cmd` fx flags (statedness = value
  presence now carries the byte fact for every member; `soft_cmd=N`
  stays — it has no value channel).

## Composers — the interpreter at compose time (carrier refactor)

Both composers keep their EMISSION exactly as today by materializing
effective rows per orderlist entry at compose time (the resolver),
then feeding their existing encoders:

- **DMC**: the stated-orderlist branch resolves per-slot effective
  rows for the intro pass + steady cycle (reproducing the extract
  walk's 2-pass unroll); `_encode_pattern` + byte-keyed pool dedup are
  unchanged, so the emitted image is byte-identical. `_row_secwidth`
  derives the stated-command byte widths from value PRESENCE instead
  of the `*_cmd` flags. Fold-fail voices keep the legacy effective
  representation wholesale (fallback rule — no member downgrades).
- **FC**: `build_pattern_pool`/`encode_sequence` key emission per
  (pattern, incoming-length) materialized variant (dedup by encoded
  bytes collapses the redundant 97%), reproducing today's slot
  streams; the `loop_length` head-omission is re-derived from the
  stated head (row-0 duration absent + carried length differs).
  Byte-identical EXCEPT the 4 deep-reject members, whose heads now
  correctly inherit at runtime (expected-diff class: verify those
  members directly — they can only improve).

## Gates

1. src/usf capability lands first (nothing emits it) — full
   regression tier 1.
2. FC migration — full-family golden byte-identity
   (tools/golden_sid_diff.py) with the 4 deep-reject members
   individually verified; regression green.
3. DMC migration — dmc_smoke, then full family-1 golden
   byte-identity; regression green.
4. Cleanup (grammar clauses + dead machinery) — golden again.
5. Closeout — full FC batch (baseline 2528 FULL) + full DMC batch
   (baseline 5170 FULL / 173 partial / 7 error), full
   tools/regression.py, mass-writes, C32/D6/memory updates.

Fallback rule (user-ratified scope): any member that doesn't fold
keeps its current representation wholesale.

## Outcome (2026-07-20)

- src/usf capability + resolver: regression green, committed 83776309.
- FC: golden 2527/2528 byte-identical (1 predicted expected-diff,
  re-verified FULL); full batch **2530 FULL / 140 partial** = baseline
  + 2 recoveries (Man_of_Noise, Love_Boat_Tune — the deep-chain wrap
  class), 0 regressions; corpus mass-written 2530/0 err (15d4c87d).
- DMC: family-1 golden **5394/5394 byte-identical** (7 known both-err);
  dmc_smoke 6/6; regression green (ca22acce). The Nocturno lesson
  (sectpos width source) + the vol-discriminability fallback guard are
  recorded in ledger C32.
- `len=L` retired end-to-end + spec updated (acf52066); C32
  canonicalized 2×, D6 fully closed (d77603f6).
- DMC full family batch + mass-write: see project_dmc round 74.
