"""
sidxray.trace — Capture and parse memory traces from siddump --memtrace.
"""

import subprocess
import os
from dataclasses import dataclass, field


SIDDUMP = os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'siddump')


@dataclass
class MemAccess:
    """A single memory read."""
    addr: int
    value: int


@dataclass
class FrameTrace:
    """All data-area memory reads in one frame."""
    frame: int
    reads: list  # list of MemAccess


def capture(sid_path, duration=10, siddump_path=None):
    """Run siddump --memtrace and return parsed frame traces.

    Returns (metadata_dict, list_of_FrameTrace).
    """
    cmd = siddump_path or SIDDUMP
    result = subprocess.run(
        [cmd, sid_path, '--memtrace', '--duration', str(duration)],
        capture_output=True, text=True, timeout=duration + 30)

    if result.returncode not in (0, 2):
        raise RuntimeError(f'siddump failed (exit {result.returncode}): {result.stderr[:200]}')

    lines = result.stdout.strip().split('\n')
    if not lines:
        return {}, []

    # First line is JSON metadata
    import json
    metadata = {}
    if lines[0].startswith('{'):
        metadata = json.loads(lines[0])
        lines = lines[1:]

    # Skip header line if present
    if lines and lines[0].startswith('V1_'):
        lines = lines[1:]

    frames = []
    for line in lines:
        if not line.startswith('F'):
            continue
        parts = line.split()
        frame_num = int(parts[0][1:])
        reads = []
        for p in parts[1:]:
            if '=' in p:
                addr_s, val_s = p.split('=')
                reads.append(MemAccess(int(addr_s, 16), int(val_s, 16)))
        frames.append(FrameTrace(frame_num, reads))

    return metadata, frames
