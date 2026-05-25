"""Thing on a Spring → USF v2 — thin wrapper over the shared adapter."""

from pipelines.hubbard.to_usf_v2 import write_usf


def write_thing_on_a_spring_usf(config, out_dir: str) -> str:
    """Write Thing_on_a_Spring.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
