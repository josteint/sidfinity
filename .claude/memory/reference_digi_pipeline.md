---
name: reference_digi_pipeline
description: "USF2 digi pipeline — extract → Sample/FLAC sidecar → pack → SID. Cycle-strict via siddump --writelog. First engine: Chimera (1-bit wavetoggle)."
metadata: 
  node_type: memory
  type: reference
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

The USF2 digi support, phased D0..D5 in `docs/usf_digi_plan.md`.
Phases D0..D3c are done (2026-05-23, commits 8052172..922f59c).

## Files

- `pipelines/hubbard/verify_cycle.py` — siddump --writelog harness
  (D0). `writelog_capture(sid, subtune, duration, force_rsid)` returns
  per-frame `[(cycle_in_frame, reg, val)]`. `compare_strict` =
  cycle-exact (use for digi). `compare_writeset` = ignore cycle (use
  for music). `subtune` is 0-indexed (PSID convention); the wrapper
  adds 1 internally for siddump's 1-indexed `--subtune` flag.

- `pipelines/hubbard/sample.py` — the engine-agnostic `Sample`
  dataclass: 8-bit-padded `audio`, `sample_rate`, `native_bits`,
  `method`, `timer_source`, `engine`, `extras` dict.

- `pipelines/hubbard/flac_io.py` — `write_sample(s, path)` /
  `read_sample(path)` round-trip the blob through FLAC + Vorbis
  comments. The audio is mapped int16 by `(byte-128)*256`; the
  descriptor and extras live as Vorbis tags. Filename convention:
  `<usf_basename>.sample<N>.flac`.

- `pipelines/hubbard/digi_pack.py` — `pack_digi(sample)` is the
  inverse of `extract_digi`: 1-bit audio + comma-hex `vol_envelope`
  extra → engine `[vol_byte, audio_byte × 16]` byte stream,
  MSB-first. Lossless instruction-sequence exact round-trip verified.

- `pipelines/chimera/extract/digi.py` — Chimera's extractor. Per
  subtune X = subtune-2: pace at `$9FE2[X]`, bank at `$9FE4[X]`;
  bank-table at `$A000 + bank*4 = {src_lo, src_hi, end_lo, end_hi}`
  (end-address, length = end - src); `$A108` = keep_screen flag;
  `$A10A` = pace (overwritten); `$A10B[i]` = bank VALIDATION table.

- `pipelines/chimera/codegen/build_with_digi.py` — combined Chimera
  build: music (regenerated, $1000) + digi region (verbatim from
  original, two 3-byte dispatcher patches retarget the music-init
  and music-play jsrs) + samples (re-packed from USF). RSID v2,
  inline load=$1000, init=$9F80, play=0.

## Representation principle (per `docs/usf_digi_plan.md`)

- **Symbolic descriptor** (rate, bit depth, method, engine, sample
  reference): in the USF text. Tokenisable.
- **Sample data** (the decoded blob): in a FLAC sidecar. NOT
  tokenisable. Stored at the native sample rate, 8-bit padded.
- **Engine packing** (1-bit MSB groups, vol interleave, CIA pacing):
  in the codegen. Re-encoded on emit. NEVER carried in the USF.

## Gotchas the first build hit

1. **The bank table is bank-indexed, NOT scan-indexed.** The
   `$A10B` validation table is a check that the bank is one of the
   known ones; the player then reloads `X = bank * 4` and reads
   `$A000,X`. An earlier extractor used the scan position and
   mis-routed Chimera subtune 3 into a dead entry that pointed at
   KERNAL ROM. Fix: index by the bank value itself. (And: don't
   confabulate a "Hubbard plays KERNAL ROM as audio" story when the
   bytes there are obvious 6502 instructions — see
   [[feedback_user_nudge_pattern]].)

2. **siddump's --subtune is 1-indexed** with 0 as the `startSong`
   sentinel; `inst_program.capture` and the Python wrapper are
   0-indexed (PSID convention). Off by one captured silence on the
   first digi attempt. `writelog_capture` now bridges this
   internally.

3. **Digi runs in init, not play.** A `sei`-blocked one-shot
   routine; libsidplayfp's first `play(cycles)` call drives it
   forward across many "frames" of the writelog output, but the
   per-frame `play()` Python model in `inst_program.capture` cannot
   verify it. Verify digi via `siddump --writelog --force-rsid` —
   that's exactly what D0 is for.

4. **Chimera is RSID, not PSID.** Init installs a raster IRQ at
   `$9FA0` (for music) or jumps into the digi player directly (for
   digi); play address is 0. Combined rebuild must ship as RSID
   too, with the inline load address. KERNAL ROM is required at
   playback for the IRQ exit (`jmp $EA31`) — install at
   `~/.local/share/sidplayfp/{kernal,basic,chargen}`.

## Music vs digi verification — what tool does what

| subtune kind | tool                                           | granularity |
|--------------|------------------------------------------------|-------------|
| music        | `inst_program.capture` (py65, 25 SID regs)     | frame       |
| digi         | `siddump --writelog --force-rsid` (libsidplayfp) | cycle      |

`compare_strict` on music writelogs will fail even on a 100%-correct
codegen — py65 and libsidplayfp differ on KERNAL/CIA init writes.
This is a measurement-tool artifact, not a player divergence.
