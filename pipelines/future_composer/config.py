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

What lives here vs what stays family-wide:

- HERE (per-SID): data table addresses, table sizes, SFX page layout
- IN engine_model: sequence/pattern command byte encodings (FE/FF
  terminators, $80-$BF length, $E0-$EF glide, etc.). These are
  FC-family-stable and never go in the config.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FCConfig:
    """Per-SID configuration for the FC family extractor.

    All `*_addr` fields are CPU addresses in the SID's memory image
    after loading. Table sizes and the SFX layout vary across the
    family — Hawkeye has 96 freq entries, 16 instruments, 64 patterns,
    SFX records at page $92 with stride 2. Other FC SIDs will differ.
    """
    name: str                       # canary identifier (e.g. 'hawkeye')
    sid_path: str                   # path under hvsc84/

    # Data table addresses (CPU addresses in the loaded memory image)
    freq_lo_addr: int               # freq-table lo bytes
    freq_hi_addr: int               # freq-table hi bytes
    pattern_ptr_addr: int           # pattern pointer table base
    instr_records_addr: int         # per-instrument 8-byte records
    per_subtune_speed_addr: int     # X-indexed speedbyte per subtune
    per_subtune_smc_addr: int       # X-indexed SMC template lo per subtune
    per_subtune_mode_addr: int      # X-indexed mode flag per subtune
                                    # (music=$02, sfx=$00 for Hawkeye)
    template_base_hi: int           # high byte of template addr
                                    # (template = template_base_hi << 8 | smc_lo)

    # SFX layout
    music_subtune_count: int        # subtunes 0..N-1 are music; N..N+M-1 SFX
    sfx_page_base: int              # SFX records at page (sfx_page_base
                                    # + sfx_idx * sfx_page_stride)
    sfx_page_stride: int            # pages between SFX records

    # Table sizes
    freq_table_entries: int         # e.g. 96 for Hawkeye
    instr_count: int                # e.g. 16 for Hawkeye
    max_patterns: int               # upper bound on pattern pointer entries
