"""Build a Chimera SID with all 4 subtunes (2 music + 2 digi).

Pipeline:

  Music subtunes (0, 1):
    SID → extract → USF → codegen (`pipelines.hubbard.codegen.build`)
    → music engine at $1000.

  Digi subtunes (2, 3):
    SID → extract → Sample → FLAC sidecar (engine-agnostic decoded
    audio) → read back → `pack_digi` → engine byte stream → patched
    into the digi region.

  Engine code (dispatcher at $9F80 + digi player at $C000): copied
  verbatim from the original SID. This is engine mechanism — re-
  emitting it from a structured representation is the user's plan's
  D3, but the simpler step here is to validate the data path
  end-to-end: every byte the engine reads is regenerated through USF,
  while the engine itself stays byte-stable.

  Dispatch glue: the original dispatcher's `jsr $C200` / `jsr $C206`
  call the original's music engine. We retarget those two 3-byte
  instructions to `jsr $1000` / `jsr $1003` so they hit our music.

The combined file is RSID v2 with inline load=$1000, init=$9F80,
play=$0000 (IRQ-driven via the dispatcher), matching the original's
format. KERNAL ROM is required at playback (the dispatcher does
`jmp $EA31` for IRQ exit), so siddump needs `--force-rsid` and the
KERNAL ROM image installed.
"""

from __future__ import annotations

import os
import struct

from pipelines.chimera.extract.digi import extract_digi, to_sample
from pipelines.hubbard.codegen import build as build_music
from pipelines.hubbard.digi_pack import pack_digi
from pipelines.hubbard.flac_io import read_sample, write_sample

LOAD = 0x1000
DISPATCHER_BASE = 0x9F80


def _read_psid(path: str) -> tuple[bytes, int, bytes]:
    """Read a PSID/RSID file; return `(header, load_addr, body)`."""
    data = open(path, 'rb').read()
    hdr_len = int.from_bytes(data[6:8], 'big')
    header = data[:hdr_len]
    load = int.from_bytes(data[8:10], 'big')
    if load == 0:
        load = int.from_bytes(data[hdr_len:hdr_len + 2], 'little')
        body = data[hdr_len + 2:]
    else:
        body = data[hdr_len:]
    return header, load, body


def _digi_region_from_original(orig_sid_path: str) -> bytearray:
    """Pull the $9F80-end region out of the original SID and apply the
    dispatcher patches so it calls our music at $1000 / $1003."""
    _, orig_load, orig_body = _read_psid(orig_sid_path)
    region = bytearray(
        orig_body[DISPATCHER_BASE - orig_load:])  # $9F80-end inclusive

    def patch(addr: int, expect: bytes, repl: bytes) -> None:
        off = addr - DISPATCHER_BASE
        if bytes(region[off:off + len(expect)]) != expect:
            raise ValueError(
                f'dispatcher patch at ${addr:04X}: expected {expect.hex()}, '
                f'found {bytes(region[off:off + len(expect)]).hex()}')
        region[off:off + len(repl)] = repl

    # $9F9A: jsr $C200 (music init) → jsr $1000
    patch(0x9F9A, bytes.fromhex('2000C2'), bytes.fromhex('200010'))
    # $9FA3: jsr $C206 (music play) → jsr $1003
    patch(0x9FA3, bytes.fromhex('2006C2'), bytes.fromhex('200310'))

    return region


def _patch_samples(region: bytearray, orig_sid_path: str,
                   flac_dir: str | None = None) -> dict:
    """For each digi subtune, USF round-trip and patch the sample bytes
    in the region. Returns a small report (subtune → sample length)."""
    report: dict[int, int] = {}
    for st in (2, 3):
        d = extract_digi(orig_sid_path, subtune=st)
        sample = to_sample(d)
        if flac_dir is not None:
            flac_path = os.path.join(flac_dir, f'sample{st}.flac')
            write_sample(sample, flac_path)
            sample = read_sample(flac_path)
        repacked = pack_digi(sample)
        off = d.src - DISPATCHER_BASE
        if off < 0 or off + len(repacked) > len(region):
            raise ValueError(
                f'subtune {st}: sample at ${d.src:04X}-${d.end:04X} falls '
                f'outside the digi region (${DISPATCHER_BASE:04X}-'
                f'${DISPATCHER_BASE + len(region) - 1:04X})')
        region[off:off + len(repacked)] = repacked
        report[st] = len(repacked)
    return report


def _build_psid_header(orig_sid_path: str, songs: int,
                       start_song: int) -> bytes:
    """Build the combined SID's PSID/RSID header — RSID v2, init=$9F80,
    play=$0000, hdr_len=$7C. Title/author/released are taken from the
    original (it's the same tune).
    """
    orig_header, _, _ = _read_psid(orig_sid_path)
    if len(orig_header) < 124:
        raise ValueError(
            f'original header is {len(orig_header)} bytes; '
            f'expected at least 124 (PSID/RSID v2)')

    h = bytearray(b'RSID')
    h += struct.pack('>HH', 2, 124)                # version=2, hdrLen=$7C
    h += struct.pack('>H', 0x0000)                  # load = inline
    h += struct.pack('>H', DISPATCHER_BASE)         # init
    h += struct.pack('>H', 0x0000)                  # play (IRQ-driven)
    h += struct.pack('>H', songs)
    h += struct.pack('>H', start_song)
    h += struct.pack('>I', 0)                        # speed
    h += orig_header[22:118]                         # title+author+released
    h += struct.pack('>H', 0x0014)                   # flags (PAL + 6581)
    h += struct.pack('>BBH', 0, 0, 0)                # start page/page len/reserved
    assert len(h) == 124, len(h)
    return bytes(h)


def build(config, out_path: str, flac_dir: str | None = None) -> str:
    """Build the combined Chimera SID with music + digi.

    `flac_dir`, if given, is where the digi samples are round-tripped
    through FLAC (proves the FLAC representation is also lossless). If
    None, the samples are pack_digi'd directly from the in-memory
    extract — useful for fast-builds that skip the disk round-trip.
    """
    # 1) music engine via the shared USF2 codegen
    music_sid_path = '/tmp/chimera_music_only.sid'
    build_music(config, music_sid_path)
    _, music_load, music_body = _read_psid(music_sid_path)
    if music_load != LOAD:
        raise ValueError(
            f'music codegen built at ${music_load:04X}, expected ${LOAD:04X}')

    # 2) digi region (dispatcher + digi player + tables + samples)
    region = _digi_region_from_original(config.sid_path)
    report = _patch_samples(region, config.sid_path, flac_dir=flac_dir)

    # 3) assemble the contiguous binary at $1000-end with a zero gap
    music_end = LOAD + len(music_body)
    if music_end > DISPATCHER_BASE:
        raise ValueError(
            f'music engine at ${LOAD:04X}-${music_end - 1:04X} overlaps '
            f'the digi region starting at ${DISPATCHER_BASE:04X}')
    gap = bytes(DISPATCHER_BASE - music_end)
    binary = music_body + gap + bytes(region)

    # 4) header — RSID v2, 4 subtunes
    n_music = len(config.subtunes)
    songs = n_music + 2  # 2 digi subtunes for Chimera
    orig_header, _, _ = _read_psid(config.sid_path)
    orig_start = (orig_header[0x10] << 8) | orig_header[0x11]
    start_song = max(1, min(orig_start, songs))
    header = _build_psid_header(config.sid_path, songs, start_song)

    # 5) file = header + inline load addr + binary
    out = bytearray(header)
    out += struct.pack('<H', LOAD)                   # inline load (little-endian)
    out += binary

    with open(out_path, 'wb') as f:
        f.write(bytes(out))

    print(f'built {out_path}: {len(out)} bytes')
    print(f'  music: ${LOAD:04X}-${music_end - 1:04X} ({len(music_body)} bytes)')
    print(f'  gap:   ${music_end:04X}-${DISPATCHER_BASE - 1:04X} ({len(gap)} bytes)')
    print(f'  digi:  ${DISPATCHER_BASE:04X}-${DISPATCHER_BASE + len(region) - 1:04X}')
    print(f'  samples patched: {report}')
    return out_path
