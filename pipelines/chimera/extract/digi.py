"""Chimera digi sample extractor.

Chimera's two SFX subtunes (PSID 2 and 3) are 1-bit-per-sample digital
audio played via V1 waveform toggle between pulse+gate (`$41`) and
triangle+gate (`$49`), CIA2-paced. The digi player at `$C000` also
modulates `$D418` master volume from a vol byte interleaved into the
sample stream.

Format in the SID binary:

  `$9FE2[X]` — per-subtune (X = subtune - 2) sample-rate pacing byte
              (the CIA2 wait threshold; smaller = slower).
  `$9FE4[X]` — per-subtune bank-hi identifier ($97 in the player).
  `$A103`    — sample-table length (number of banks).
  `$A10B[i]` — bank-match table. Linear scan: i where
              `binary[$A10B + i] == bank-hi`.
  `$A000 + i*4` = `{src_lo, src_hi, end_lo, end_hi}` (end-address;
                  length = `end - src`).
  `$A108`    — "keep screen on" flag (bool, 0 blanks VIC).

The sample bytes at `[src, end)` are structured as 17-byte groups
`[vol_byte, audio_byte × 16]`:

  - The first byte of each group is a VOL update (`$D418` master vol,
    high nibble cap'd at `$0F`, minus the running bias `$FD = 0`).
  - The following 16 bytes are AUDIO; each byte's 8 bits play
    MSB-first, each bit picks `$41` (0) or `$49` (1) for V1 ctrl.

Per-bit timing: the CIA2 timer is reloaded with `$FFFF` each bit and
the loop waits until DD04 (timer LO) < pace. The high byte hasn't
yet decremented, so the wait is `($FF - pace)` timer ticks plus ~17
cycles of code, giving:

    bit_rate = PAL_CLOCK / (($FF - pace) + 17)

Bank source: most banks point inside the SID body, but Chimera also
points into KERNAL ROM (`$E000-$FFFF`) as "free" sample bytes — a
classic Hubbard space trick. The extractor reads from a supplied
KERNAL ROM image if the bank's src is in ROM.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from pipelines.hubbard.sample import Sample


PAL_CLOCK = 985248  # PAL system clock, Hz
DEFAULT_KERNAL_ROM = os.path.expanduser('~/.local/share/sidplayfp/kernal')


@dataclass
class ChimeraDigi:
    """One Chimera digi subtune as extracted from the binary.

    Engine-specific fields preserved for traceability (`pace`, `bank`,
    `src`, `end`, `keep_screen`, `vol_envelope`) — the codegen consumes
    these to re-emit the original engine packing.
    """

    subtune: int           # PSID subtune (2 or 3)
    pace: int              # $9FE2[X]
    bank: int              # $9FE4[X]
    src: int               # sample source address
    end: int               # one-past-last sample byte
    keep_screen: bool      # $A108 (false → engine blanks VIC)
    src_in_kernal: bool    # sample lives in KERNAL ROM, not the SID
    raw_bytes: bytes       # the [src, end) blob
    bits: list[int]        # decoded 1-bit audio stream (0 / 1)
    vol_envelope: list[int]  # raw vol bytes (one per 17-byte group)


def _load_sid(sid_path: str) -> tuple[int, bytes]:
    """Read a PSID/RSID; return `(load_addr, body)`."""
    data = open(sid_path, 'rb').read()
    hdr_len = int.from_bytes(data[6:8], 'big')
    load = int.from_bytes(data[8:10], 'big')
    if load == 0:
        load = int.from_bytes(data[hdr_len:hdr_len + 2], 'little')
        body = data[hdr_len + 2:]
    else:
        body = data[hdr_len:]
    return load, body


def _read_bytes(addr: int, count: int, load: int, body: bytes,
                kernal: bytes | None) -> bytes:
    """Read `count` bytes at `addr`, transparently spanning SID body and
    KERNAL ROM ($E000-$FFFF)."""
    out = bytearray()
    for k in range(count):
        a = addr + k
        if load <= a < load + len(body):
            out.append(body[a - load])
        elif 0xE000 <= a <= 0xFFFF and kernal is not None:
            out.append(kernal[a - 0xE000])
        else:
            raise ValueError(
                f'address ${a:04X} is outside SID body '
                f'(${load:04X}-${load + len(body) - 1:04X}) '
                f'and KERNAL ROM (${0xE000:04X}-${0xFFFF:04X})')
    return bytes(out)


def extract_digi(sid_path: str, subtune: int,
                 kernal_rom_path: str | None = None) -> ChimeraDigi:
    """Extract one Chimera digi sample.

    `subtune` is the PSID subtune (Chimera's digi pair is 2 and 3).
    `kernal_rom_path` defaults to the sidplayfp install location; pass
    explicitly if you have it elsewhere.
    """
    load, body = _load_sid(sid_path)

    kernal: bytes | None = None
    rom_path = kernal_rom_path or DEFAULT_KERNAL_ROM
    if os.path.isfile(rom_path):
        kernal = open(rom_path, 'rb').read()
        if len(kernal) != 8192:
            raise ValueError(
                f'{rom_path}: expected 8192 bytes, got {len(kernal)}')

    def b(addr: int) -> int:
        return _read_bytes(addr, 1, load, body, kernal)[0]

    x = subtune - 2
    if x < 0:
        raise ValueError(
            f'subtune {subtune}: Chimera digi subtunes are 2 and 3')
    pace = b(0x9FE2 + x)
    bank = b(0x9FE4 + x)

    tbl_len = b(0xA103)
    idx = None
    for i in range(tbl_len):
        if b(0xA10B + i) == bank:
            idx = i
            break
    if idx is None:
        raise ValueError(
            f'subtune {subtune}: bank ${bank:02X} not found in sample '
            f'table at $A10B (length {tbl_len})')

    entry = 0xA000 + idx * 4
    src = b(entry) | (b(entry + 1) << 8)
    end = b(entry + 2) | (b(entry + 3) << 8)
    keep_screen = bool(b(0xA108))

    src_in_kernal = src >= 0xE000
    if src_in_kernal and kernal is None:
        raise FileNotFoundError(
            f'subtune {subtune}: sample at ${src:04X}-${end:04X} lives in '
            f'KERNAL ROM but no ROM image was found at {rom_path}. Provide '
            f'`kernal_rom_path=` or install the ROM at the default path.')

    raw = _read_bytes(src, end - src, load, body, kernal)

    bits: list[int] = []
    vol_env: list[int] = []
    for off in range(0, len(raw), 17):
        group = raw[off:off + 17]
        if not group:
            break
        vol_env.append(group[0])
        for byte in group[1:]:
            for bit in range(7, -1, -1):
                bits.append((byte >> bit) & 1)

    return ChimeraDigi(
        subtune=subtune, pace=pace, bank=bank, src=src, end=end,
        keep_screen=keep_screen, src_in_kernal=src_in_kernal,
        raw_bytes=raw, bits=bits, vol_envelope=vol_env,
    )


def to_sample(digi: ChimeraDigi) -> Sample:
    """Wrap a `ChimeraDigi` as an engine-agnostic `Sample`."""
    # 8-bit-padded 1-bit audio: 0 → $00 (pulse), 1 → $FF (tri).
    audio = bytes(0xFF if v else 0x00 for v in digi.bits)
    # Bit rate: ($FF - pace) timer ticks + ~17 cycles of code overhead.
    cycles_per_bit = (0xFF - digi.pace) + 17
    sample_rate = PAL_CLOCK // cycles_per_bit
    return Sample(
        audio=audio,
        sample_rate=sample_rate,
        native_bits=1,
        method='d404_1bit_wavetoggle',
        timer_source='cia2',
        engine='chimera',
        extras={
            'pace': f'{digi.pace:02X}',
            'bank': f'{digi.bank:02X}',
            'src': f'{digi.src:04X}',
            'end': f'{digi.end:04X}',
            'src_in_kernal': '1' if digi.src_in_kernal else '0',
            'keep_screen': '1' if digi.keep_screen else '0',
            'per_byte_repeat': '16',
            'vol_envelope': ','.join(f'{v:02X}' for v in digi.vol_envelope),
        },
    )
