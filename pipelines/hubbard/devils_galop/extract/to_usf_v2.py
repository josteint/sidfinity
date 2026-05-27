"""Devils Galop → USF v2 — thin wrapper over the shared adapter.

No SFX, no digi — straight call into `pipelines.hubbard.to_usf_v2`.
"""

from pipelines.hubbard.to_usf_v2 import write_usf


def write_devils_galop_usf(config, out_dir: str) -> str:
    """Write Devils_Galop.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
