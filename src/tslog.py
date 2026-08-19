"""Timestamped, flushed progress logging for development tools.

Born 2026-08-19 after an evening of phantom hangs: dmc_build_one spent
7½ silent single-core minutes in its build phase (read as a hang and
killed), its verify output sat invisible in a block-buffered redirect,
and a background run's completion was mistaken for a 2-minute build.
Every one of those confusions is answered by lines that say WHAT phase
started WHEN.

Convention (CLAUDE.md → Tooling reflex): every development tool that can
run for more than a few seconds prints `ts()` phase lines — at minimum
one when a phase starts (with its input scale, e.g. "25 subtunes x2,
8 workers") and one when it ends (with the elapsed). Always flushed, so
redirects and `tail -f` see them live.

    from src.tslog import ts, phase

    ts('build start')
    with phase('capturing 25 subtune pairs (8 workers)'):
        ...
"""
from __future__ import annotations

import sys
import time
from contextlib import contextmanager
from datetime import datetime


def ts(msg: str) -> None:
    """One timestamped, flushed progress line."""
    print(f'[{datetime.now():%H:%M:%S}] {msg}', flush=True)


@contextmanager
def phase(name: str):
    """Timestamped phase banner: start line now, end line (with elapsed)
    when the block exits — also on exception, so a crash's last log line
    names the phase that died."""
    t0 = time.monotonic()
    ts(f'{name} ...')
    try:
        yield
    except BaseException:
        ts(f'{name} FAILED after {time.monotonic() - t0:.1f}s')
        raise
    ts(f'{name} done in {time.monotonic() - t0:.1f}s')


def _self_test() -> None:  # pragma: no cover
    ts('tslog self-test')
    with phase('sleep phase'):
        time.sleep(0.05)


if __name__ == '__main__':  # pragma: no cover
    _self_test()
    sys.exit(0)
