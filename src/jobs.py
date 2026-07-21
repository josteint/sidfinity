"""Worker-pool sizing — the one place that decides how wide a batch runs.

Every parallel batch in the repo (regression, the family batches, the
mass-writers, the census/portfolio tools) sizes its pool from here instead
of hardcoding a literal. That literal used to be `8`, pinned to the 8-core
X230; on a 64-core/128-thread host it left ~94% of the machine idle.

Precedence, highest first:

  1. the tool's own env var (e.g. ``REGRESSION_JOBS``) — per-tool override
  2. ``SIDFINITY_JOBS`` — one knob for every batch at once
  3. the CPU budget (affinity-aware, so ``taskset``/cgroup limits are honoured)

``cap`` bounds the pool by the work actually available: spawning 128 workers
to run 116 tasks costs process setup for nothing.

NESTING (important): ``multiprocessing.Pool`` workers are daemonic, and a
daemonic process may not create children — a Pool inside a Pool worker dies
with ``AssertionError: daemonic processes are not allowed to have children``.
So an inner helper that itself parallelises (``hubbard.verify.verify_all``)
must be passed ``jobs=1`` when called from inside a worker. The outer pool is
already providing the parallelism; the inner one would only oversubscribe.
"""

import os

_ENV_GLOBAL = 'SIDFINITY_JOBS'


def cpu_budget() -> int:
    """Usable CPU count, honouring `taskset` / cgroup affinity."""
    try:
        return len(os.sched_getaffinity(0))
    except AttributeError:          # not Linux
        return os.cpu_count() or 1


def default_jobs(env: str | None = None, *, cap: int | None = None,
                 reserve: int = 0) -> int:
    """Worker count for a batch pool. See module docstring for precedence.

    `cap`     — never exceed the number of tasks available.
    `reserve` — leave this many CPUs for the parent process / OS.
    """
    for name in (env, _ENV_GLOBAL):
        if name and os.environ.get(name):
            try:
                return max(1, int(os.environ[name]))
            except ValueError:
                pass
    n = max(1, cpu_budget() - reserve)
    if cap is not None:
        n = min(n, max(1, cap))
    return n
