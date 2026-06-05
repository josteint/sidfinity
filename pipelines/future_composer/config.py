"""FCConfig — per-SID configuration for the FC engine extractor.

The FC family (MoN/FutureComposer 1987-89) lacks a stable load
address: composers placed their SIDs at $0800, $1000, $1800, $2800,
$7AE0, $A600 and many other addresses, so every per-SID data table
(freq, patterns, instruments, per-subtune setup) lives at a different
CPU address even though the engine's structure is family-stable.

The shared `engine_model.extract(cfg)` walks the SID's memory image
using the addresses from `cfg`. Each canary SID gets its own
`pipelines/future_composer/<engine>/config.py` providing an `FCConfig`
instance.

Mirrors Hubbard's `EngineConfig` per-tune pattern.

What's per-SID vs what's family-stable:

- HERE (per-SID): data table addresses, table sizes, subtune layout
  discriminator
- IN engine_model: sequence/pattern command byte encodings (FE/FF
  terminators, $80-$BF length, $E0-$EF glide, etc.). These are
  FC-family-stable and never go in the config.

### Subtune layout variants

Different FC drivers store their per-subtune sequence pointers in
structurally different ways. Two layouts seen so far:

- `'flat_seqtabel'` (Cybernoid II): contiguous table; subtune N's
  6-byte sequence record lives at `seqtabel_addr + N * 6`. All
  subtunes are music — no SFX section.
- `'smc_template_with_sfx'` (Hawkeye): SMC-driven indirection — the
  table at `per_subtune_smc_addr` stores 1 lo-byte per subtune; combined
  with the fixed `template_base_hi`, this yields the per-subtune
  record's address. SFX subtunes are stored at fixed pages
  (`sfx_page_base + sfx_idx * sfx_page_stride`).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


SubtuneLayout = Literal['flat_seqtabel', 'smc_template_with_sfx']


@dataclass(frozen=True)
class FCConfig:
    """Per-SID configuration for the FC family extractor.

    Address fields are CPU addresses in the SID's memory image after
    loading. Table sizes and the subtune layout vary across the family.
    """
    name: str                       # canary identifier (e.g. 'hawkeye')
    sid_path: str                   # path under hvsc84/

    # Data table addresses (CPU addresses in the loaded memory image)
    freq_lo_addr: int               # freq-table lo bytes
    freq_hi_addr: int               # freq-table hi bytes
    pattern_ptr_addr: int           # pattern pointer table base
    instr_records_addr: int         # per-instrument 8-byte records
    per_subtune_speed_addr: int     # X-indexed speedbyte per subtune

    # Subtune layout discriminator (selects which variant fields apply)
    subtune_layout: SubtuneLayout

    # --- variant 'flat_seqtabel' fields ---
    seqtabel_addr: int = 0          # base of contiguous per-subtune
                                    # 6-byte (lo*3, hi*3) records

    # --- variant 'smc_template_with_sfx' fields ---
    per_subtune_smc_addr: int = 0   # X-indexed SMC template lo per subtune
    template_base_hi: int = 0       # high byte of template addr
                                    # (template = template_base_hi << 8 | smc_lo)
    per_subtune_mode_addr: int = 0  # X-indexed mode flag per subtune
                                    # (music=$02, sfx=$00)
    music_subtune_count: int = 0    # subtunes 0..N-1 are music; rest SFX
    sfx_page_base: int = 0          # SFX records at page (sfx_page_base
                                    # + sfx_idx * sfx_page_stride)
    sfx_page_stride: int = 0        # pages between SFX records

    # Table sizes (vary per SID even within the family)
    freq_table_entries: int = 96
    instr_count: int = 16
    max_patterns: int = 64

    # Aux-table addresses needed by the featuredriven asm composer.
    # These tables live in the verbatim aux region (not yet USF-derived);
    # the composer needs equates for them so the engine code can
    # reference them by name. Default 0 = "not yet located" (effect
    # that uses the table will error if invoked).
    drumtabel_addr: int = 0        # drum-program ptrs (4 bytes per drum)
    filterbytes_addr: int = 0      # filter-program ptrs (4 ptrs to 10-byte programs)
    # TODO as effects come online:
    # arplo_addr, arphi_addr (arpeggio program ptrs)
    # pulsetabel_addr (pulse-program data)
    # wavearp_addr, pulsearp_addr (wave/pulse-arp tables)
    # startlen_addr, starttabel_addr (noise-tick tables)
    # vibtabwait_addr (vibrato delay table)
