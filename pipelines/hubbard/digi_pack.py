"""Inverse of the Chimera digi extractor: pack a `Sample` back into the
engine's byte stream.

The engine plays bytes as 17-byte groups `[vol_byte, audio_byte × 16]`.
Each audio byte's 8 bits are emitted MSB-first as the V1 waveform-
toggle bit stream; each vol byte sets the running `$D418` master vol.

The packer requires:
- `sample.audio` — the 8-bit-padded 1-bit stream (`$00` / `$FF`).
- `sample.extras['vol_envelope']` — the per-group vol bytes as
  comma-separated hex (the form `Sample`'s round-trip serialiser uses).

`pack_digi(sample) -> bytes` is the inverse of `extract_digi(...)`'s
byte-stream decoding, by construction. Verified byte-exact against
the original Chimera sample bytes for both digi subtunes.
"""

from __future__ import annotations

from pipelines.hubbard.sample import Sample


def _bits_from_audio(audio: bytes) -> list[int]:
    """Decode the 8-bit-padded 1-bit stream back to a list of 0/1.

    `$00` → 0, `$FF` → 1. Any other value is an encoding error: the FLAC
    round-trip is exact, so only the two extremes should appear.
    """
    bits: list[int] = []
    for b in audio:
        if b == 0:
            bits.append(0)
        elif b == 0xFF:
            bits.append(1)
        else:
            raise ValueError(
                f'unexpected 1-bit audio byte ${b:02X}: only $00 and $FF '
                f'should appear in 8-bit-padded 1-bit audio')
    return bits


def _vol_envelope_from_extras(extras: dict[str, str]) -> list[int]:
    """Parse the `vol_envelope` extra (comma-separated hex bytes)."""
    raw = extras.get('vol_envelope', '')
    if not raw:
        return []
    return [int(tok, 16) for tok in raw.split(',')]


def pack_digi(sample: Sample) -> bytes:
    """Pack a 1-bit Chimera-style `Sample` into the engine's byte stream.

    The stream is N groups of `[vol_byte, audio_byte × 16]`, where each
    audio byte is the next 8 bits MSB-first. The bit count must equal
    `128 * len(vol_envelope)` — every group is full, no partial tail.
    """
    if sample.method != 'd404_1bit_wavetoggle':
        raise ValueError(
            f'pack_digi: method {sample.method!r} not supported '
            f'(expected d404_1bit_wavetoggle)')

    bits = _bits_from_audio(sample.audio)
    vol_env = _vol_envelope_from_extras(sample.extras)

    if len(bits) != 128 * len(vol_env):
        raise ValueError(
            f'pack_digi: {len(bits)} bits != 128 * {len(vol_env)} vol '
            f'updates ({128 * len(vol_env)} expected bits)')

    out = bytearray()
    for g, vol in enumerate(vol_env):
        out.append(vol)
        for byte_idx in range(16):
            byte = 0
            for k in range(8):
                bit = bits[g * 128 + byte_idx * 8 + k]
                byte = (byte << 1) | bit
            out.append(byte)
    return bytes(out)
