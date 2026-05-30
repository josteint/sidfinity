"""Hunter Patrol → USF v2 — thin wrapper over the shared adapter."""

from pipelines.hubbard.to_usf import write_usf


def write_hunter_patrol_usf(config, out_dir: str) -> str:
    """Write Hunter_Patrol.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
