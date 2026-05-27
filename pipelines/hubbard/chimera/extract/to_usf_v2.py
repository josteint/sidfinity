"""Chimera → USF v2 — thin wrapper over the shared adapter.

Chimera's only engine-specific contribution is its two digi subtunes.
The music + instruments + init state + params all go through the
shared `pipelines.hubbard.to_usf_v2` core unchanged.
"""

from __future__ import annotations

import os

from pipelines.hubbard.flac_io import write_sample
from pipelines.hubbard.to_usf_v2 import write_usf, _basename_for
from pipelines.hubbard.chimera.extract.digi import extract_digi, to_sample
from src.usf2 import DigiSubtune


def chimera_to_usf_v2(config):
    """Build the in-memory UsfFile (digi subtunes injected). Use
    `write_chimera_usf` for the on-disk version with FLAC sidecars."""
    from pipelines.hubbard.to_usf_v2 import to_usf_v2
    digi_subtunes = [
        DigiSubtune(id=st,
                    sample=f'{_basename_for(config.name)}.sample{st}.flac')
        for st in (config.digi_subtunes or ())
    ]
    return to_usf_v2(config, extra_subtunes=digi_subtunes)


def write_chimera_usf(config, out_dir: str) -> str:
    """Write Chimera.usf + Chimera.sample{N}.flac sidecars."""
    base = _basename_for(config.name)
    digi_subtunes = [
        DigiSubtune(id=st, sample=f'{base}.sample{st}.flac')
        for st in (config.digi_subtunes or ())
    ]

    def _write_sample_for(st: int):
        sample = to_sample(extract_digi(config.sid_path, st))
        def _w(path: str):
            write_sample(sample, path)
        return (f'{base}.sample{st}.flac', _w)

    sidecars = [_write_sample_for(st) for st in (config.digi_subtunes or ())]
    return write_usf(config, out_dir,
                     extra_subtunes=digi_subtunes,
                     extra_sidecar_writes=sidecars)
