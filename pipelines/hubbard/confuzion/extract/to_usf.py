"""Confuzion → USF v2 — thin wrapper over the shared adapter."""

from __future__ import annotations

from pipelines.hubbard.to_usf import write_usf


def write_confuzion_usf(config, out_dir: str) -> str:
    """Write Confuzion.usf to `out_dir`."""
    return write_usf(config, out_dir)
