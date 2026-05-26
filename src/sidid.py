#!/usr/bin/env python3
"""Python wrapper for the sidid player identification tool.

sidid identifies which player engine a SID file uses by matching
binary signatures. This module wraps the CLI tool and provides:
  - identify_player(sid_path) -> dict with player name
  - scan_directory(dir_path) -> list of (path, player) tuples
  - batch_identify(file_list) -> list of dicts using multiprocessing
"""

import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

# Resolve paths relative to this file
_THIS_DIR = Path(__file__).resolve().parent
_TOOLS_DIR = _THIS_DIR.parent / "tools"
_SIDID_BIN = _TOOLS_DIR / "sidid"
_SIDID_CFG = _TOOLS_DIR / "sidid.cfg"

UNIDENTIFIED = "*Unidentified*"


def _check_prereqs():
    if not _SIDID_BIN.exists():
        raise FileNotFoundError(f"sidid binary not found: {_SIDID_BIN}")
    if not _SIDID_CFG.exists():
        raise FileNotFoundError(f"sidid config not found: {_SIDID_CFG}")


def _parse_file_lines(output: str) -> list[tuple[str, str]]:
    """Parse sidid output lines into (filepath, player) pairs.

    Each result line has the format:
        filename.sid                                             PlayerName
    or for full paths:
        path/to/file.sid                                         PlayerName

    The summary section starts with a blank line followed by
    'Detected players:' and is excluded.
    """
    results = []
    lines = output.split("\n")
    for line in lines:
        # Skip header, blank lines, and summary section
        if not line.strip():
            continue
        if line.startswith("Using configfile"):
            continue
        if line.startswith("Detected players:"):
            break
        # Parse: filename is left-aligned, player is right-aligned
        # They are separated by whitespace, but filenames can have spaces.
        # sidid pads with spaces so player starts at a consistent column.
        # The player name never starts with a space, and the gap is large.
        # Strategy: find the last run of 2+ spaces and split there.
        m = re.match(r"^(.+?)\s{2,}(\S.*)$", line)
        if m:
            filepath = m.group(1).strip()
            player = m.group(2).strip()
            results.append((filepath, player))
    return results


def identify_player(sid_path: str | Path) -> dict:
    """Identify the player engine for a single SID file.

    Returns dict with keys:
        path: str - the input path
        player: str - identified player name, or '*Unidentified*'
        identified: bool - True if a player was matched
    """
    _check_prereqs()
    sid_path = Path(sid_path)
    if not sid_path.exists():
        raise FileNotFoundError(f"SID file not found: {sid_path}")

    # sidid operates on directories, so copy file to a temp dir
    with tempfile.TemporaryDirectory(prefix="sidid_") as tmpdir:
        tmp_file = Path(tmpdir) / sid_path.name
        shutil.copy2(sid_path, tmp_file)
        result = subprocess.run(
            [str(_SIDID_BIN), f"-c{_SIDID_CFG}", "-d", "-u", tmpdir],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        pairs = _parse_file_lines(output)

    player = UNIDENTIFIED
    if pairs:
        # Match by filename
        for fname, pname in pairs:
            if fname == sid_path.name or fname.endswith("/" + sid_path.name):
                player = pname
                break
        else:
            # Fallback: use first result
            player = pairs[0][1]

    return {
        "path": str(sid_path),
        "player": player,
        "identified": player != UNIDENTIFIED,
    }


def scan_directory(dir_path: str | Path, recursive: bool = True,
                   include_unidentified: bool = True) -> list[dict]:
    """Scan a directory for SID files and identify their players.

    This is much faster than calling identify_player() per file because
    sidid scans an entire directory tree in one invocation.

    Returns list of dicts with keys: path, player, identified
    """
    _check_prereqs()
    dir_path = Path(dir_path)
    if not dir_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {dir_path}")

    args = [str(_SIDID_BIN), f"-c{_SIDID_CFG}", "-u"]
    if not recursive:
        args.append("-d")
    args.append(str(dir_path))

    result = subprocess.run(
        args, capture_output=True, text=True, timeout=600
    )
    pairs = _parse_file_lines(result.stdout)

    results = []
    for filepath, player in pairs:
        identified = player != UNIDENTIFIED
        if not include_unidentified and not identified:
            continue
        # sidid outputs paths relative to cwd or the scanned dir
        # Reconstruct full path
        full_path = filepath
        if not os.path.isabs(filepath):
            # Try as-is first (sidid may output relative to cwd)
            if not os.path.exists(filepath):
                full_path = str(dir_path / filepath)
        results.append({
            "path": full_path,
            "player": player,
            "identified": identified,
        })
    return results


def _identify_one(sid_path: str) -> dict:
    """Worker function for batch_identify (must be top-level for pickling)."""
    try:
        return identify_player(sid_path)
    except Exception as e:
        return {
            "path": str(sid_path),
            "player": f"ERROR: {e}",
            "identified": False,
        }


def batch_identify(file_list: list[str | Path], workers: int = 64) -> list[dict]:
    """Identify players for a list of SID files using multiprocessing.

    Note: For large batches, scan_directory() is MUCH faster since it
    runs sidid once on the whole tree instead of per-file.
    """
    paths = [str(p) for p in file_list]
    with Pool(workers) as pool:
        return pool.map(_identify_one, paths)


def player_summary(results: list[dict]) -> dict:
    """Summarize results by player engine.

    Returns dict with keys:
        counts: Counter of player -> count
        total: int
        identified: int
        unidentified: int
    """
    counts = Counter(r["player"] for r in results)
    identified = sum(1 for r in results if r["identified"])
    return {
        "counts": counts,
        "total": len(results),
        "identified": identified,
        "unidentified": len(results) - identified,
    }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <sid_file_or_directory> [--top N]")
        sys.exit(1)

    target = sys.argv[1]
    top_n = 20
    if "--top" in sys.argv:
        idx = sys.argv.index("--top")
        top_n = int(sys.argv[idx + 1])

    if os.path.isdir(target):
        print(f"Scanning directory: {target}")
        results = scan_directory(target)
        summary = player_summary(results)
        print(f"\nTotal: {summary['total']}  "
              f"Identified: {summary['identified']}  "
              f"Unidentified: {summary['unidentified']}")
        print(f"\nTop {top_n} players:")
        for player, count in summary["counts"].most_common(top_n):
            print(f"  {count:6d}  {player}")
    else:
        result = identify_player(target)
        print(f"{result['path']}: {result['player']}")
