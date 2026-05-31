---
name: project_fingerprint_db
description: "Deferred: instrument-writelog fingerprint database. Maps (writelog observation) → (USF parameter values) to accelerate future engine audits and serve as ML training data."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Future move (not active yet, 2026-05-25): build a database of
audited instruments keyed by their *observable* writelog
fingerprint rather than by engine name. The fingerprint maps
`(register-write sequence under standardized conditions)` to the
`(USF parameter values)` we derived during the audit.

**Why:** two goals collapse into the same artifact.
1. Each new Hubbard '85 engine's audit is currently from-scratch.
   A new engine's drumarp inst with `arp_period=8` produces the
   same writelog shape as HR's; recognising that shape from a
   database would let us skip the manual audit and propose the
   parameter set immediately.
2. The `(writelog, parameters)` pairs are supervised training data
   for an eventual classifier that suggests USF parameters from a
   raw register trace. That's a downstream ML step
   (see [[reference_tokenization]]).

**How to apply:** revisit after the next three engines are
migrated (Hunter Patrol, Thing on a Spring, One Man and his
Droid). By then we'll have ~150 audited instruments — a corpus
large enough to:
- Determine the right "atom" (single note? first 32 frames after
  note-start? per-effect probe?) by examining what patterns
  actually repeat.
- Choose a distance metric (Hamming, edit distance, perceptual)
  by checking what threshold separates true matches from false.
- Confirm cross-engine repeatability is actually present at the
  rate the idea assumes.

If by the third engine each one is still introducing genuinely
new parameter points, the database's payoff is lower than hoped
and we should reconsider.

## Open design questions

1. **What's the atom?** A whole-song writelog is too big. Probably
   per-instrument-per-note, captured under standardised conditions
   — e.g. play the SID, isolate one voice playing one note at a
   known pitch, record the first 32 frames after note-start.
   `src/usf/audit.py` (see [[reference_audit_tool]]) already does
   most of the capture; needs a "fingerprint" mode that probes
   under canonical conditions instead of a frame range.

2. **Schema.** Rough sketch — SQLite for portability:
   ```sql
   CREATE TABLE inst_fingerprint (
     id           INTEGER PRIMARY KEY,
     engine       TEXT,           -- e.g. 'human_race'
     inst_idx     INTEGER,        -- 0-indexed in that engine
     ad           INTEGER, sr INTEGER, ctrl INTEGER, pw INTEGER,
     fx_flags     INTEGER,
     pitch_probe  INTEGER,        -- pitch used during capture
     writelog     BLOB,           -- normalised 32-frame sequence
     parameters   JSON            -- the USF parametric form
   );
   ```

3. **Matching / similarity.** Byte-equality won't work — pitch,
   vibrato phase, frame_ctr alignment all introduce noise. Need
   normalisation: subtract base freq, quantise relative timing,
   ignore non-effect writes. Then a distance metric (Hamming or
   edit distance) with a threshold tuned against the existing
   audited corpus.

4. **Standardised probe conditions.** Need an "audit fingerprint
   probe" that runs the SID's init, then forces a specific note
   onto a specific voice and records N frames. Probably wrap
   `inst_program.capture` with an instrument-specific setup
   harness.

5. **Interaction with ML training.** Two uses:
   - Supervised dataset for a (writelog → parameters) classifier.
   - Conversion-time check: rebuilt USF compiled back to SID must
     produce a writelog within tolerance T of the original's
     fingerprint. Stronger than md5-exact verify_all (which is
     necessary, see [[feedback_py65_misses_dispatch_bugs]]) but
     more useful as a guide.

## Why "not now"

Three reasons:
- Hubbard '85 has 3 engines left. Doing those without the
  database first tells us how much manual-audit pain is real vs.
  imagined. Maybe the next 3 are easier than HR was.
- We don't yet know if the parameter space is stable enough.
  Three more engines may add new parameters that retroactively
  invalidate stored fingerprints.
- ML training (the consumer of this dataset) is itself a
  downstream move. Building the database before the consumer
  exists risks shaping it for an imagined use case rather than a
  real one.

## Why "but record the idea"

The idea connects two future workstreams (audit acceleration + ML
training data) into one artifact. Easy to lose; worth keeping a
pointer so when either workstream picks up, the other one's
requirements are already visible.

Related: [[reference_audit_tool]] is what the fingerprint capture
would extend. [[reference_tokenization]] is the eventual ML
consumer. [[feedback_principle_first_analysis]] is what the
classifier would automate (the parametric-form discipline).
