"""Per-sub engine model — thin wrapper over Chimera's.

5 Title Tunes' 5 sub-engines are standard Hubbard '85 engines (same
code, just relocated). Chimera's engine_model already implements the
standard extract; this module re-exports it so the v2 config can pass
each sub's `sid_path` + `ft_base` cleanly.
"""

from pipelines.chimera.extract.engine_model import extract  # noqa: F401
