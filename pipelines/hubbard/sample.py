"""Digi sample type for the USF2 pipeline.

A digi sample has three layers (see docs/usf_digi_plan.md):

- The symbolic descriptor — engine, method, native bit depth, rate.
  Lives in the USF text and is tokenisable.
- The decoded waveform blob — engine-agnostic PCM padded to 8-bit.
  Lives in a FLAC sidecar alongside the USF file (NOT inline).
- The engine packing — the 1-bit MSB packing for $D404 toggle, or the
  4-bit nibble packing for $D418 PCM. Re-encoded by the codegen on
  emit; never carried in the USF.

`Sample` is the type that holds the first two: a decoded blob plus the
descriptor needed to play it back. The third layer is engine code in
the codegen and never sits in this dataclass.

`extras` carries per-engine mechanism hints that don't fit the core
fields (the per-byte repeat, the pacing constant, the vol envelope).
They round-trip through Vorbis comments verbatim.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Sample:
    """An engine-agnostic decoded digi sample.

    `audio` is the decoded stream padded to 8-bit. For 1-bit Chimera-
    style digi, every byte is `$00` or `$FF`. For 4-bit $D418 PCM, one
    byte per output sample (the high nibble is the value, low nibble
    is zero). Sample count = `len(audio)`.

    `sample_rate` is the ideal playback rate in Hz at PAL.

    `native_bits` is the original bit depth (1 / 4 / 8). The FLAC
    stores the 8-bit-padded form regardless; this field records what
    the engine actually consumed.

    `method` is the playback method:
      - `d404_1bit_wavetoggle` — Chimera-style waveform toggle.
      - `d418_4bit_pcm`        — $D418 master-vol DAC trick.

    `timer_source` is `cia1` / `cia2` / `raster`.

    `engine` is the originating engine name (`chimera`, etc.). The
    codegen uses this to pick a re-encoder.

    `extras` is per-engine state — pacing values, per-byte repeats,
    vol envelopes — encoded as strings (Vorbis comments are strings).
    Each engine documents its own keys.
    """

    audio: bytes
    sample_rate: int
    native_bits: int
    method: str
    timer_source: str
    engine: str
    extras: dict[str, str] = field(default_factory=dict)
