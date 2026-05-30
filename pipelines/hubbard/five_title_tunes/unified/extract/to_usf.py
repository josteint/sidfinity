"""5 Title Tunes → 5 USF v2 files — one per sub-engine.

`write_5tt_usfs(out_dir)` writes `5_Title_Tunes_0.usf` through
`5_Title_Tunes_4.usf` to `out_dir`. Each is a self-contained
single-subtune Hubbard '85 USF playing one of the 5 title tunes.
"""

from __future__ import annotations

from pipelines.hubbard.to_usf import write_usf
from pipelines.hubbard.five_title_tunes.unified.config import ALL_TUNES


def write_5tt_usfs(out_dir: str) -> list[str]:
    """Write the 5 sub USFs. Returns the list of usf paths."""
    return [write_usf(cfg, out_dir) for cfg in ALL_TUNES]
