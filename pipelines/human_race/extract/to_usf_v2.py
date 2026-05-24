"""Human Race → USF v2 — thin wrapper over the shared adapter.

5 music subtunes (V1 + V2 only — V3 is silent). No SFX, no digi.
"""

from pipelines.hubbard.to_usf_v2 import write_usf


def write_human_race_usf(config, out_dir: str) -> str:
    """Write Human_Race.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
