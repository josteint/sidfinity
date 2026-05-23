"""FLAC + Vorbis-comments I/O for `Sample` (see docs/usf_digi_plan.md).

The sample blob is stored as mono 16-bit FLAC at `sample.sample_rate`,
the 8-bit padded byte values mapped to int16 by `(b - 128) * 256`
(byte 0x00 → -32768, 0xFF → +32512). The mapping is exact and
losslessly reversible since FLAC is lossless. Stream-flat int16 keeps
every popular audio tool able to render the file.

The descriptor (engine, method, timer source, native bit depth) plus
`Sample.extras` go in Vorbis comments. Read-back is verbatim by-key.

Filename convention: `<usf_basename>.sample<N>.flac` next to the USF.
"""

from __future__ import annotations

import numpy as np
import soundfile as sf
from mutagen.flac import FLAC

from pipelines.hubbard.sample import Sample


# The fixed Vorbis-comment keys (Sample fields). Anything else is an extra.
_CORE_KEYS = {'native_bits', 'method', 'timer_source', 'engine'}


def _audio_to_int16(audio: bytes) -> np.ndarray:
    """Map 8-bit padded sample bytes to int16 PCM."""
    return ((np.frombuffer(audio, dtype=np.uint8).astype(np.int32) - 128)
            * 256).astype(np.int16)


def _int16_to_audio(pcm: np.ndarray) -> bytes:
    """Inverse of _audio_to_int16."""
    bytes_arr = ((pcm.astype(np.int32) // 256) + 128).clip(0, 255)
    return bytes_arr.astype(np.uint8).tobytes()


def write_sample(sample: Sample, path: str) -> None:
    """Write a `Sample` to `path` as FLAC + Vorbis comments."""
    pcm = _audio_to_int16(sample.audio)
    sf.write(path, pcm, sample.sample_rate, format='FLAC', subtype='PCM_16')
    f = FLAC(path)
    f['native_bits'] = str(sample.native_bits)
    f['method'] = sample.method
    f['timer_source'] = sample.timer_source
    f['engine'] = sample.engine
    for k, v in sample.extras.items():
        f[k] = v
    f.save()


def read_sample(path: str) -> Sample:
    """Read a `Sample` back from a FLAC written by `write_sample`."""
    pcm, rate = sf.read(path, dtype='int16')
    audio = _int16_to_audio(pcm)
    f = FLAC(path)
    extras = {k: f[k][0] for k in f.keys() if k not in _CORE_KEYS}
    return Sample(
        audio=audio,
        sample_rate=int(rate),
        native_bits=int(f['native_bits'][0]),
        method=f['method'][0],
        timer_source=f['timer_source'][0],
        engine=f['engine'][0],
        extras=extras,
    )
