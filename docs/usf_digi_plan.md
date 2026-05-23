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

**v0: inline base64.** The sample blob lives in the USF text, base64-
encoded. Simple, self-contained, gets the first round-trip working.

**v1 (later): content-addressed store.** Samples keyed by SHA-256 in a
shared store; the USF carries `digi(ref=<hash>, rate=…)`. Digi SFX get
reused across a game's tunes — content-addressing dedups, and the
symbolic stream stays clean for the tokenizer (one `digi` token, the
waveform as a separate modality, exactly how multimodal ML references
assets).

**Store the engine-agnostic decoded sample**, not the raw packing.
For 1-bit digi that's the bit/±1 stream; for 4-bit, the nibble stream.
The packing is engine mechanism, re-encoded by the codegen.

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
  serialization (base64-inline for v0).
- The symbolic digi descriptor: rate, bit depth, sample reference,
  envelope, the per-byte repeat.

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
- **Tokenizer impact of v0 inline base64**: tolerable while we have a
  handful of digi tunes; migrate to v1 (content-addressed) before any
  serious ML training pass over a digi-heavy corpus.
