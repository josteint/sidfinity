"""Monty on the Run → USF v2 — thin wrapper over the shared adapter.

3 music subtunes + 16 SFX subtunes. SFX are extracted by
`extract_sfx` (per config) and the shared adapter converts each into
a USF v2 `SfxSubtune`. No digi.
"""

from pipelines.hubbard.to_usf import write_usf


def write_monty_usf(config, out_dir: str) -> str:
    """Write Monty_on_the_Run.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
