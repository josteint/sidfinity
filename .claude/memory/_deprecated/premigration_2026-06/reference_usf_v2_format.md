---
name: reference_usf_v2_format
description: "USF v2 — the on-disk Universal Symbolic Format. Custom DSL, .usf + sibling .flac sidecars. The codegen's load-bearing input."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

USF v2 is the on-disk format the codegen reads. One `.usf` file +
N `<basename>.sampleN.flac` sidecars per tune. The codegen produces
the SID from these inputs alone — no peek at the original SID at
codegen time.

Spec: `docs/usf_v2_format.md` (the contract — read this first).

## Files

- `src/usf2/grammar.lark`    — Lark LALR grammar.
- `src/usf2/types.py`        — AST dataclasses (UsfFile, PsidMeta,
                               Params, InitState, Instrument,
                               MusicSubtune, DigiSubtune, etc.).
- `src/usf2/parser.py`       — `parse(text)` / `parse_file(path)`,
                               `UsfParseError` with line/col on
                               syntax errors.
- `src/usf2/writer.py`       — `write(usf)` / `write_file(usf, path)`.
                               Deterministic, round-trip stable.
- `src/usf2/validate.py`     — semantic validators: ref resolution
                               (instruments, patterns, samples),
                               per-pattern length-equals-sum,
                               sidecar files exist.

- `pipelines/hubbard/to_usf_v2.py`           — shared adapter:
  `EngineConfig + decode_all + extract → UsfFile + sidecar writes`.
  Engine-agnostic; used by all migrated Hubbard '85 engines.
- `pipelines/build_from_usf.py`              — public USF-only build
  entry. `build_from_usf(usf_path, out_path)` → `composer.emit_sid_from_usf`
  → composed asm → xa65 → PSID. NO `load_sid(config.sid_path)`.
  (Moved to `pipelines/build_from_usf.py` during the composer rewrite
  — was `pipelines/hubbard/build_from_usf.py` originally.)
- `pipelines/hubbard/engine_constants.py`    — per-engine constants
  (instrument-table address, freq-table address, voice_starts table,
  digi engine code if any). Engine code that's same across all tunes
  of one engine.
- `pipelines/<engine>/extract/to_usf_v2.py`  — engine-specific thin
  wrapper. Calls `pipelines.hubbard.to_usf_v2.write_usf(config, ...)`
  with engine-specific extras (Chimera's digi subtunes + FLAC writes).

## What the codegen reads (USF-only)

- USF text (parsed via `parse_file`) gives:
  - `psid:` — title, author, released, clock, sid model, start_song.
  - `params:` — engine config flags (arp_period, vib_onset,
    linear_pw_or, incby2_*, freeze_on_stop, stop_fill, etc.).
  - `init:` — per-voice initial state (ctrl, dur_field, pwm_period,
    pwm_dir, instr, slide_v) — replaces Hubbard's freq-table-overlap
    trick.
  - `instrument N [name]:` blocks — waveform, loop, pwm, adsr, arp,
    vibrato, envelope, fx flags (freq_slide, inc_by2).
  - `subtune N music:` / `subtune N digi:` blocks.
- Sidecar `.flac` files (per digi subtune) give:
  - Audio bits as PCM.
  - Vorbis comments: pace, bank, src, end, keep_screen, per_byte_repeat,
    boundary_vol, vol_envelope.
- Engine constants in `engine_constants.py` (per-engine code):
  - Instrument-table + freq-table addresses, voice_starts.
  - 320-byte freq-region (192-byte musical PAL table is shared across
    all Hubbard '85; 128-byte state region is per-engine).
  - Digi engine code (Chimera-only — dispatcher xa65 + digi player
    xa65, no verbatim engine bytes from the original SID).

## Engines on the USF-only path (as of 2026-05-24)

| engine        | subtunes              | USF | notes              |
|---------------|-----------------------|-----|--------------------|
| Action Biker  | 3 music               | ✓  |                    |
| Chimera       | 2 music + 2 digi      | ✓  | PSID, no KERNAL    |
| Commando      | 3 music + 16 SFX      | ✓  |                    |
| Devils Galop  | 1 music               | ✓  |                    |
| Monty         | 3 music + 16 SFX      | ✓  | off-table sweep    |

Verify_all on all 5 engines passes 46/46 subtunes; ALL of them
rebuild with the codegen reading ONLY their `.usf` + sidecars (no
peek at the original SID at codegen time).

## Format design lessons (worth keeping)

- **Custom DSL, not TOML/JSON/YAML.** Patterns are tracker-like
  blocks of note rows; the grammar is small (~50 lines) and gives
  precise error messages.
- **Hex with `$`, decimal bare.** `$40` and `40` never ambiguous.
- **No count fields.** The parser derives `n_voices`, `n_patterns`,
  etc. from the data — small edits can't desync counts.
- **Per-pattern `length=N`** validated against sum of durations.
  Catches the most common "I edited a duration and forgot to
  rebalance" footgun.
- **No cross-voice alignment check by default.** SID music
  routinely has polyrhythms; lockstep would reject most of it.
- **Note pitch up to octave 9** for off-table arpeggio extensions
  (pitch 104 = G#8 in Devils Galop).
- **Comments allowed (`;`) but lossy on round-trip.** Keeping
  comment preservation would cost ~50 lines for marginal value.
- **Engine bit names** for fx flags (`tie`, `no_release`, `porta=N`,
  `freq_slide`, `inc_by2`). Not generalised musical names.

## Where USF v2 is still incomplete

- **The 192-byte PAL freq table** is preserved verbatim because
  Hubbard's table is empirically hand-tuned (not strict equal-
  temperament — entry 95 is ~60 cents flat). Deriving from formula
  would change the intended pitches. Documented as engine data, not
  a smell to fix.
- **One 128-byte per-engine state region.** Engine scratch +
  arpeggio extension. Most bytes get overlaid from USF init; the
  remainder is opaque engine state. Could decode further in future
  work to make every byte semantically attributed.
