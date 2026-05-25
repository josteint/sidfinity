"""One Man and his Droid → USF v2 — thin wrapper over the shared adapter."""

from pipelines.hubbard.to_usf_v2 import write_usf


def write_one_man_and_his_droid_usf(config, out_dir: str) -> str:
    """Write One_Man_and_his_Droid.usf into `out_dir`. No sidecars."""
    return write_usf(config, out_dir)
