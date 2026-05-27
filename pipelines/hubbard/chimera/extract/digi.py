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
  `$A10B[i]` — bank-VALIDATION table. The player scans this to confirm
              the requested bank is known, then *discards* the scan
              index — the bank table is indexed by the bank value
              itself, not the scan position.
  `$A000 + bank*4` = `{src_lo, src_hi, end_lo, end_hi}` (end-address;
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

Both Chimera samples live inside the SID body. (`$A000-$A003` is a
dead entry — bank `$00` is not in the `$A10B` validation table.)
"""

from __future__ import annotations

from dataclasses import dataclass

from pipelines.hubbard.sample import Sample


PAL_CLOCK = 985248  # PAL system clock, Hz


@dataclass
class ChimeraDigi:
    """One Chimera digi subtune as extracted from the binary.

    Engine-specific fields preserved for traceability (`pace`, `bank`,
    `src`, `end`, `keep_screen`, `vol_envelope`, `boundary_vol`) — the
    codegen consumes these to re-emit the original engine packing.
    """

    subtune: int           # PSID subtune (2 or 3)
    pace: int              # $9FE2[X]
    bank: int              # $9FE4[X]
    src: int               # sample source address
    end: int               # one-past-last sample byte
    keep_screen: bool      # $A108 (false → engine blanks VIC)
    raw_bytes: bytes       # the [src, end) blob
    bits: list[int]        # decoded 1-bit audio stream (0 / 1)
    vol_envelope: list[int]  # raw vol bytes (one per 17-byte group)
    boundary_vol: int        # byte at `end` — the player reads it as a
                             # final vol update before exiting (a small
                             # quirk of the loop's $F9-wrap edge case).
                             # Carries through the USF so cycle-strict
                             # writelog match holds at the very last frame.


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


def extract_digi(sid_path: str, subtune: int) -> ChimeraDigi:
    """Extract one Chimera digi sample.

    `subtune` is the PSID subtune (Chimera's digi pair is 2 and 3).
    """
    load, body = _load_sid(sid_path)

    def b(addr: int) -> int:
        off = addr - load
        if 0 <= off < len(body):
            return body[off]
        raise ValueError(
            f'address ${addr:04X} is outside SID body '
            f'(${load:04X}-${load + len(body) - 1:04X})')

    x = subtune - 2
    if x < 0:
        raise ValueError(
            f'subtune {subtune}: Chimera digi subtunes are 2 and 3')
    pace = b(0x9FE2 + x)
    bank = b(0x9FE4 + x)

    # The $A10B table validates that `bank` is a known value; the player
    # then discards the scan index and indexes the bank table by the bank
    # value itself (`$C045-$C049`: `lda $97 / asl / asl / tax`).
    tbl_len = b(0xA103)
    known = [b(0xA10B + i) for i in range(tbl_len)]
    if bank not in known:
        raise ValueError(
            f'subtune {subtune}: bank ${bank:02X} not in validation '
            f'table at $A10B (known: {[f"${v:02X}" for v in known]})')

    entry = 0xA000 + bank * 4
    src = b(entry) | (b(entry + 1) << 8)
    end = b(entry + 2) | (b(entry + 3) << 8)
    keep_screen = bool(b(0xA108))

    raw = bytes(body[src - load : end - load])
    boundary_vol = body[end - load]  # the byte AT `end`; player reads it on exit

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
        keep_screen=keep_screen,
        raw_bytes=raw, bits=bits, vol_envelope=vol_env,
        boundary_vol=boundary_vol,
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
            'keep_screen': '1' if digi.keep_screen else '0',
            'per_byte_repeat': '16',
            'boundary_vol': f'{digi.boundary_vol:02X}',
            'vol_envelope': ','.join(f'{v:02X}' for v in digi.vol_envelope),
        },
    )
