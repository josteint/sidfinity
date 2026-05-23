# USF2 — digi support plan

Handle digitised-sample playback in the USF2 pipeline. First target:
Chimera's two SFX subtunes (1-bit waveform-toggle digi at `$D404`).
Generalises later to `$D418` 4-bit digi (DMC, JCH, etc.).

## Representation

A digi sample has three layers, and they belong in three different
places.

| layer | example | where |
|---|---|---|
| symbolic descriptor | "digi instrument, rate, bit depth, envelope" | the USF text — tokenizable |
| sample data | the waveform blob | a payload, NOT tokenizable |
| engine mechanism | 1-bit MSB-first packing, CIA-timed `$D404` toggle | the codegen |

**Storage: FLAC with Vorbis comments, as a sidecar file alongside
the USF.** The sample data lives in the FLAC; the USF text carries
the symbolic descriptor plus a reference to the file. Lossless,
arbitrary sample rates, rich metadata via Vorbis comments, ~5–10×
smaller than WAV, universally readable.

The FLAC stores the **engine-agnostic decoded sample** at the native
sample rate (the bit/nibble stream, padded to 8-bit if native bit
depth is < 8). The original engine packing is engine mechanism, re-
encoded by the codegen on emit.

Vorbis comments — the standardised tags:

- `native_bits` — original bit depth (`1`, `4`, `8`).
- `method` — playback method (`d404_1bit_wavetoggle`,
  `d418_4bit_pcm`, …).
- `timer_source` — `cia1` / `cia2` / `raster`.
- `engine` — the originating engine (`chimera`, …).
- per-engine extras (the per-byte repeat, the pacing value, …).

Filename convention: `<usf_basename>.sample<N>.flac` next to the
USF file. The USF text references each sample by id and the loader
resolves to the sibling filename. Content-addressing (dedup keyed by
SHA-256) is a possible later optimisation once the corpus is large
enough that duplicate samples across tunes matter.

## Verification — the foundation

`inst_program.capture` is frame-granular and physically cannot verify
cycle-timed digi (and would blow its step budget on a blocking
`sei`-locked digi routine). Digi verifies against
**`siddump --writelog`** — the cycle-timed `(cycle, reg, val)` stream
from libsidplayfp. This is the project's ground-truth rule applied
where it actually matters.

## Phased plan

### D0 — cycle-accurate verification harness
- Parse `siddump --writelog` output.
- A compare function: two writelogs → match / first cycle of divergence.
- Calibrate on the *music* subtunes first (original vs current rebuilds)
  to learn what tolerance "cycle-exact" actually needs.

### D1 — Chimera digi extractor
- `pipelines/chimera/extract/digi.py`: read the `$A000` bank table +
  subtune→bank map (`$9FE2`) → `{sample blob, length, rate $A10A,
  per-byte repeat}`.
- Decode the 1-bit packed blob to the engine-agnostic bit/±1 stream.

### D2 — USF representation
- A `Sample` (and/or `DigiSample`) type in `usf.py` + `usf_text.py`
  serialization — references a sidecar FLAC by id, NOT inline.
- A small read/write helper for FLAC + Vorbis comments (likely
  `soundfile` + `mutagen`, or a thin subprocess wrapper around `flac`).
- The symbolic digi descriptor in the USF: rate, bit depth, sample
  reference, envelope, the per-byte repeat.

### D3 — digi codegen
- Emit a digi-player routine: the CIA-timed 1-bit busy-wait loop,
  re-encoding the sample to Chimera's MSB-first 1-bit packing.
- The digi blob in the rebuilt SID.
- Wire it as a *digi subtune kind* — structurally unlike a music
  subtune (`sei`-blocked, one-shot, not per-frame). The codegen's
  subtune dispatch grows a digi path.

### D4 — verify + ship Chimera complete
- `siddump --writelog`: original Chimera subtunes 2 and 3 vs rebuilt.
- Cycle-exact (or characterise the busy-wait tolerance — D0 calibration
  tells us what's achievable).
- Demo: Chimera ships all 4 subtunes (2 music + 2 digi SFX), playable.

### D5 — generalise
- Make digi config-driven on the shared core: playback method
  (`$D404` 1-bit toggle vs `$D418` 4-bit), timer source, rate.
- Then DMC and `$D418`-digi engines reuse this without re-deriving it.

## Risks / open

- **Cycle-exact vs tolerance**: D0 calibration tells us whether
  cycle-EXACT match is achievable for the busy-wait loop or whether a
  small defined tolerance is needed.
- **`sei`-blocked one-shot routine**: the codegen's existing per-frame
  play model doesn't fit a blocking digi routine. D3 introduces the
  digi-subtune dispatch.
- **FLAC tooling**: pin a Python lib (probably `soundfile` for
  the audio, `mutagen` for Vorbis comments) so the read/write path is
  one well-supported dependency, not a fragile subprocess dance.
