"""Music Assembler — the verdict: write-stream comparison against HVSC.

Mode 1 (per-frame instruction sequence) in TRICHOTOMY form: the composer emits
its own init (universal reset + typed priming), so the streams differ by an
init prefix and a flat compare would diverge at write 0 (ledger C21).
"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))

from pipelines.hubbard.verify_cycle import (      # noqa: E402
    compare_instruction_stream, writelog_capture)
from src.songlengths import get_durations, load_database   # noqa: E402


def verify(rel: str, rebuilt_path: str, hvsc_root: str = 'hvsc84',
           subtune: int = 0) -> dict:
    """Compare `rebuilt_path` against the HVSC original over songlength*1.1
    (the ratified verify window — never an arbitrary N)."""
    orig = os.path.join(hvsc_root, rel)
    db = load_database(os.path.join(hvsc_root, 'DOCUMENTS', 'Songlengths.md5'))
    d = get_durations(orig, db)
    dur = (d[subtune] if d and subtune < len(d) else 110) * 1.1
    a = writelog_capture(orig, subtune=subtune, duration=dur)
    b = writelog_capture(rebuilt_path, subtune=subtune, duration=dur)
    return compare_instruction_stream(a, b, mode='trichotomy')
