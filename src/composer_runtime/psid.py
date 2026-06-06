"""PSID v2 header construction.

Builds the 124-byte PSID v2 header. Subsumes five pre-existing
copies of the same struct-pack sequence:
  - pipelines/composer.py::_psid_header  (model-driven, computes
    flags from EngineModel.psid.clock + sid_model)
  - pipelines/composer.py (inlined at the usf2_commando + the
    digi-combined emitters)
  - pipelines/companion/c64_music_examples/build.py::_psid_header
  - pipelines/companion/jay_derrett/build.py::_wrap_psid (returns
    header + body in one call)

PSID v2 layout (124 bytes total, big-endian unless noted):
  +0   magic 'PSID' (4)
  +4   version 0x0002 + dataOffset 0x007C (4)
  +8   loadAddress (2) — 0 means inline-encoded in code body
  +10  initAddress (2)
  +12  playAddress (2)
  +14  songs (2)
  +16  startSong (2, 1-indexed)
  +18  speed (4) — bit per subtune: 0 = VBI 50Hz, 1 = CIA timer A
  +22  title (32, latin-1, zero-padded)
  +54  author (32)
  +86  released (32)
  +118 flags (2) — bit0=MUS, bit2-3=clock, bit4-5=sidModel, bit6-7=sid2Model
  +120 startPage + pageLength + secondSID (4)
"""
from __future__ import annotations

import struct


# Flag combinations frequently used in this project. The flags word at
# byte +118 encodes clock + SID model:
#   clock bits 2-3: 0=unknown, 1=PAL, 2=NTSC, 3=both
#   sid_model bits 4-5: 0=unknown, 1=6581, 2=8580, 3=both
FLAGS_PAL_6581 = (1 << 2) | (1 << 4)


def build_header(
    *,
    load: int,
    init: int,
    play: int,
    songs: int,
    start_song: int = 1,
    speed: int = 0,
    title: str | bytes = '',
    author: str | bytes = '',
    released: str | bytes = '',
    flags: int = FLAGS_PAL_6581,
) -> bytes:
    """Build a 124-byte PSID v2 header.

    `load=0` selects inline-load encoding: the first two bytes of the
    code body (after the header) hold the actual little-endian load
    address. Callers using inline form must prepend those two bytes
    to their code themselves.

    `title`/`author`/`released` accept str (latin-1 encoded internally,
    `errors='replace'`) or pre-encoded bytes; either form is truncated
    or right-padded with NUL to exactly 32 bytes.

    `speed` is the PSID speed bitfield: one bit per subtune
    (LSB = subtune 1), 0 = VBI (50Hz), 1 = CIA timer A.
    """
    h = bytearray(b'PSID')
    h += struct.pack('>HH', 2, 124)
    h += struct.pack('>H', load)
    h += struct.pack('>H', init)
    h += struct.pack('>H', play)
    h += struct.pack('>H', songs)
    h += struct.pack('>H', start_song)
    h += struct.pack('>I', speed)
    h += _pad32(title)
    h += _pad32(author)
    h += _pad32(released)
    h += struct.pack('>H', flags)
    h += struct.pack('>BBH', 0, 0, 0)
    assert len(h) == 124, len(h)
    return bytes(h)


def _pad32(s: str | bytes) -> bytes:
    if isinstance(s, str):
        b = s.encode('latin-1', errors='replace')
    else:
        b = s
    return b[:32].ljust(32, b'\x00')
