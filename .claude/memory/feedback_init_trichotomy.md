---
name: init-trichotomy
description: "TRIPWIRE. Init writes split into three universal categories — reset/priming/environment — plus engine bookkeeping that stays OUT of USF. The composer's init is universal infrastructure; USF carries only the per-tune musical priming as typed parameters. No engine-name dispatch, no shape detection."
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

## The trichotomy

Every byte an engine's init routine writes — to SID, RAM, CIA,
anywhere — falls into one of four categories. The first three are
universal across engines; the fourth stays out of USF entirely.

1. **Reset writes** — erase the past. Silence-clear `$D400-$D417`,
   set `$D418` baseline ($0F), optional test-bit oscillator-phase
   clear on all three voices. **The composer always emits these,
   identical bytes for every tune. Invisible to USF.**

2. **Priming writes** — shape the future. Specific SID state the
   play loop will rely on but doesn't itself emit (master_vol
   non-default, filter cutoff/resonance/routing, per-voice
   envelope_prime, per-voice pulse-width init). **The composer
   emits these parameterised by USF. Each is a typed musical
   parameter field in `init.sid {}`.**

3. **Environment** — the playback rate. CIA timer programming, IRQ
   install. **Top-level USF param** (`playback_rate_hz`), orthogonal
   to init.sid.

4. **Engine bookkeeping** — RAM-internal flags, scratch pointers,
   deferred-init markers (Hülsbeck's `$033C=1` flag, etc.). **Stays
   OUT of USF entirely.** Our composer has its own engine, its own
   bookkeeping; doesn't reproduce the original engine's RAM state.

## Why

Why: aligns the catalogue. Validated empirically across 100% of
HVSC (top 100 engines = 89% + tail survey + unclassified = full
catalogue scope). All ~60,000 SIDs' inits fit the trichotomy. No
engine surfaces a new category.

How to apply: when migrating any engine, walk its init writes:

- If a write would happen for any tune regardless of musical
  content → it's RESET. The composer's universal reset handles
  it; nothing goes in USF.
- If a write encodes a per-tune musical decision (master vol,
  filter cutoff, envelope prime) → it's PRIMING. Goes in USF as
  a typed field under `init.sid {}`.
- If it programs CIA timer or sets playback rate → it's
  ENVIRONMENT. Top-level USF param.
- If it's RAM-internal engine machinery → it's BOOKKEEPING.
  Doesn't go in USF at all; our composer's engine has its own
  needs.

## Forbidden shapes

NEVER do these for init handling:

- **Shape detection** that maps a content marker (like the
  carry_leak quirk) to a constants table (like BOWDEN_INIT_SID_WRITES).
  That's engine-name dispatch with extra steps. The principled
  alternative: USF carries the values directly.
- **Engine-named init fields** (e.g. `bowden_envelope_prime`).
  Use universal names (`voice.envelope_prime`) that any engine can
  use.
- **Opaque-bytes init field** (`sid_writes: [($05, $09), ...]`).
  Forbidden shape from
  [[feedback_usf_representation_principle]]: carries engine bytes
  rather than musical parameters.
- **Inferring init from music content.** Init is generally NOT
  inferable from patterns (only the rare Hubbard-style
  freq-table-overlap case where engine-constant data IS the init).
  Don't try.

## Canonical reference

The full reasoning, empirical survey, design trade-offs, and
verification consequences live in
[`docs/sid_init_report.md`](../../../sidfinity/docs/sid_init_report.md)
— ~750 lines. Companion long-form research (PSID/RSID spec quotes,
libsidplayfp source) at `docs/sid_init_research.md`.

Re-read the report **before** designing init handling for a new
engine migration.

## Why our own init introduces NO audio change

Emitting our own reset instead of reproducing the engine's init writes is
audibly safe, and the report proves why (`docs/sid_init_report.md` §2b
"noise-burst bucket dissected" + §5.3 edge cases). What a SID tune SOUNDS like
is fully determined by (1) the chip STATE at the moment music starts and (2)
the play() write stream from there. Every init technique — clean clear,
test-bit phase clear, noise-burst sweep, multi-pass paranoid clear, a $01/$00
descending sweep — **converges to the same final register state**; only the
transient TRACE during init differs, and play() overwrites a silenced chip
before anything is heard. So if (A) our end-of-init state matches register-by-
register over $D400-$D418 and (B) the play stream matches, the audio is
identical even though the init write SEQUENCE is ours. The trichotomy verdict
checks exactly those two things. (Caveat: a deliberate audible init signature
like FC's `$00→$41→$00` noise tick would be removed — but a $01/$00 sweep with
no waveform bit set, as in Adrenalin, is silent, so nothing audible is lost.)
This is the "various inits affect the song / ours doesn't change the audio"
reasoning. See [[project_adrenalin]] for the worked case.

## Verification consequence

Strict Check A (chip state at end of init matches register-by-
register) is **not** simply "compare end-of-frame-0 state" — VBI
frame boundaries aren't CPU init-RTS events, so init-cycle drift
between orig and rebuild causes asymmetric play() writes to spill
into frame 0. The principled fix needs cycle-precise py65
emulation at extract time, stopping at init's RTS, capturing chip
state at that moment, encoding it in USF priming. Until that
lands, regression uses legacy mode (which accepts EITHER
match_all OR match_post_init as a full match).

## See also

- [[usf-init-sid-block]] — current implementation state of the
  init.sid block in USF + composer.
- [[feedback_usf_representation_principle]] — the broader
  principle that init follows.
- [[feedback_schema_addition_discipline]] — the bar each new
  init.sid field must clear before being added.
