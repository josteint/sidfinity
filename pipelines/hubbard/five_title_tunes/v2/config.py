"""EngineConfigs for 5 Title Tunes (USF v2 byte-exact path).

5 Title Tunes is a compilation PSID: 5 standalone Hubbard '85 engines
selected by a dispatcher at $0B10/$0B40. Each sub-engine is migrated
as its own EngineConfig (TUNE0..TUNE4) using the standalone PSIDs
written by `tools/split_multi_binary.py` (see /tmp/five_tt_subs/ or
`pipelines/hubbard/five_title_tunes/work_subs/`).

The compound build (codegen-relocated 5 engines + dispatcher → one
PSID) is a separate step (see build_compound.py). Each TUNE-N config
here is also a working standalone — it produces a self-contained
5_Title_Tunes_N.sid playing only that sub-tune.

Per-sub parameters were identified by:
  - decompile() auto-discovery of instr_base, freq_table_base, song table
  - manual CMP/AND scan of each sub-engine's code range. Subs 1/2/4
    have CMP #$10 + CMP #$18 in the fx-bit-1 slide path (Hunter Patrol /
    OMaHD pattern → incby2_onset=$10, incby2_late_gate=$18). Subs 0/3
    don't — they use the simpler Chimera-style slide.
"""

from __future__ import annotations

import os

from pipelines.hubbard.config import EngineConfig
from pipelines.hubbard.five_title_tunes.v2.extract import engine_model as _em

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))

# Standalone sub PSIDs (written by tools/split_multi_binary.py). The
# `_ensure_subs()` helper regenerates these on demand so the configs
# are usable even without pre-running the splitter.
WORK_SUBS = os.path.join(ROOT, 'pipelines', 'five_title_tunes', 'work_subs')

PARENT_SID = os.path.join(ROOT, 'hvsc84', 'MUSICIANS', 'H',
                          'Hubbard_Rob', '5_Title_Tunes.sid')


def _ensure_subs():
    """Run the splitter if work_subs/ is missing or empty."""
    if os.path.exists(os.path.join(WORK_SUBS, 'sub_0.sid')):
        return
    import subprocess
    os.makedirs(WORK_SUBS, exist_ok=True)
    subprocess.run(
        ['python3', os.path.join(ROOT, 'tools', 'split_multi_binary.py'),
         PARENT_SID, WORK_SUBS],
        check=True,
    )


# Per-sub bases (from decompile auto-discovery on each sub_N.sid):
SUB_BASES = {
    0: dict(instr_base=0x1065, freq_table_base=0x0F6A),
    1: dict(instr_base=0x1D02, freq_table_base=0x1C07),
    2: dict(instr_base=0x245B, freq_table_base=0x2360),
    3: dict(instr_base=0x2C9B, freq_table_base=0x2BA0),
    4: dict(instr_base=0x35BE, freq_table_base=0x34C3),
}


def _sub_sid_path(i: int) -> str:
    return os.path.join(WORK_SUBS, f'sub_{i}.sid')


def _make_extract(i: int):
    """Per-sub extract closure — decompiles sub_i.sid via the Chimera-
    family engine_model with the correct ft_base."""
    def _extract(subtune=0):
        _ensure_subs()
        return _em.extract(
            sid_path=_sub_sid_path(i),
            subtune=subtune,
            ft_base=SUB_BASES[i]['freq_table_base'],
        )
    return _extract


def _make_resetspd(i: int):
    def _resetspd(subtune, binary, load):
        # Speed = tempo - 1 (tick divider). Each sub has its own
        # speed in the decompile output. The extract result already
        # encodes tempo = speed + 1.
        return _make_extract(i)(subtune).score.tempo - 1
    return _resetspd


def _make_config(i: int, **deltas) -> EngineConfig:
    _ensure_subs()
    return EngineConfig(
        name=f'five_tt_sub{i}',
        sid_path=_sub_sid_path(i),
        instr_base=SUB_BASES[i]['instr_base'],
        instr_count=deltas.pop('instr_count'),
        freq_table_base=SUB_BASES[i]['freq_table_base'],
        extract=_make_extract(i),
        resetspd=_make_resetspd(i),
        subtunes=(0,),
        arp_interval=12,
        arp_period=deltas.pop('arp_period', 8),
        vib_onset=deltas.pop('vib_onset', 8),
        **deltas,
    )


# Sub 0 — title tune 1. Tempo 4, 32 sequences, 8 instruments.
# Tempo 4 means first note-load is deferred 3 frames.
# Arp mask = $01 → arp_period = 2 ($0F3C `AND #$01`).
TUNE0 = _make_config(0, instr_count=8, speed_ctr_init=3, arp_period=2)

# Sub 1 — title tune 2. Tempo 2, 12 sequences. Has CMP #$10/#$18
# pattern (Hunter-Patrol-style fx-bit-1 late-gate). 1-frame deferred
# init (orig frame 0 writes only V1+V2+V3 freq=$0116; frame 1 = full).
TUNE1 = _make_config(1, instr_count=12,
                     speed_ctr_init=1, arp_period=2,
                     incby2_step=-1, incby2_onset=0x10, incby2_late_gate=0x18)

# Sub 2 — title tune 3. Tempo 3, 16 sequences. Hunter-Patrol pattern.
# No speed_ctr_init delay — this sub's init does its own first-frame setup.
TUNE2 = _make_config(2, instr_count=12, arp_period=2,
                     incby2_onset=0x10, incby2_late_gate=0x18)

# Sub 3 — title tune 4. Tempo 3, 15 sequences. Chimera-style. 1-frame
# deferred init (orig: frame 0 = V1+V2 freq=$0116, frame 1 = full).
TUNE3 = _make_config(3, instr_count=12,
                     speed_ctr_init=1, arp_period=2)

# Sub 4 — title tune 5. Tempo 2, 11 sequences. Hunter-Patrol pattern.
# 1-frame deferred init.
TUNE4 = _make_config(4, instr_count=12,
                     speed_ctr_init=1, arp_period=2,
                     incby2_onset=0x10, incby2_late_gate=0x18)

ALL_TUNES = (TUNE0, TUNE1, TUNE2, TUNE3, TUNE4)
