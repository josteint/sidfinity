"""EngineConfig for the Companion engine (Hubbard-extended variant).

The base Companion player is from Keith Bowden's *The Companion to the
Commodore 64* (Pan Books, 1984) — a type-in driver. Rob Hubbard
extended it at $C900 for `Up_up_and_Away.sid` (1984 Starcade) and
related tunes, adding:

  - Per-subtune orderlist addressing via self-modifying code at init
  - Dual tempo dividers (gate-off-tick + note-load-tick) for staccato
  - $8C / $8D sentinels and bit-7 "play with early release" flag
  - Global V3 PW_LO += 4 sweep (hardcoded period 2 frames)
  - 5-subtune dispatch via per-subtune init routines

See `src/Companion/docs/` for the full research dossier
and `pipelines/companion/up_up_and_away/disassembly.s` for the local
disassembly we model.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SID = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Up_up_and_Away.sid')


@dataclass
class CompanionConfig:
    name: str = 'companion'
    sid_path: str = SID

    # Engine entry points (from PSID header, used for verification).
    # Init at $C900 (subtune dispatch), play at $C703 (VBI handler).
    init_addr: int = 0xC900
    play_addr: int = 0xC703

    # Freq tables (128 entries each, lo+hi paired).
    freq_hi_base: int = 0xC000
    freq_lo_base: int = 0xC080

    # Per-subtune init template source addresses (each 32 bytes;
    # bytes 0..6=V1, 7..13=V2, 14..20=V3, 21..31=globals).
    template_addrs: tuple = (0xC4F0, 0xC1C0, 0xC260, 0xC580, 0xC690)

    # Per-subtune init address (entry of the per-subtune init routine).
    # These are the JMP targets the init dispatcher patches at $C913/$C914.
    init_dispatch: tuple = (0xC831, 0xC7ED, 0xC80F, 0xC853, 0xC875)

    # Per-subtune SID volume/filter-mode value written to $D418
    # (low nibble = volume, high nibble = filter mode + 3-off bit).
    vol_filter: tuple = (0x0F, 0x0F, 0x1F, 0x0F, 0x0F)

    # Per-subtune SID filter cutoff hi ($D416) value.
    filter_cutoff_hi: tuple = (0x00, 0xFF, 0x46, 0xFF, 0xFF)

    # 5 music subtunes (indices into all of the per-subtune tuples).
    subtunes: tuple = (0, 1, 2, 3, 4)


CFG = CompanionConfig()
