#!/usr/bin/env python3
"""Regenerate tools/sidid_full.txt — the engine column's source.

    python3 tools/gen_sidid_dump.py            # ~3 min

Existed as a bare shell command whose THREE non-obvious rules lived only in the
output file's own header, where nothing could enforce them:

 1. `-m` (multi-signature). Without it sidid's loop breaks on the first hit, so
    the answer is whichever signature comes first in sidid.cfg and every other
    match is discarded. 48.2% of HVSC matches more than one player, and the
    discarded part holds the SUB-VERSIONS (`(DMC_V4.x)` vs `(DMC_V5.x)`) and
    the HETEROGENEOUS files (one .sid packing players from two families).
 2. Drop our own `*.sidfinity.sid` rebuilds. sidid scans every .sid it finds,
    including the ~12.7k we wrote into the tree; they are outputs, not sources.
 3. Drop the trailing per-player summary + statistics block — those lines parse
    as bogus paths in a {path: engines} map.

The un-truncated long paths depend on tools/sidid_no_truncate.patch (applied by
tools/build.sh at clone time); upstream cuts paths at 56 chars, which silently
dropped 1,384 members (2.3% of HVSC). This script FAILS if that regresses,
rather than writing a quietly-lossy dump.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIDID = ROOT / 'tools' / 'sidid' / 'sidid'
CFG = ROOT / 'tools' / 'sidid' / 'sidid.cfg'
HVSC = ROOT / 'hvsc85'
OUT = ROOT / 'tools' / 'sidid_full.txt'

# Lines that begin the trailing report; everything from here on is not data.
_TAIL = ('Detected players:', 'Statistics:')


def _git_rev(repo: Path) -> str:
    try:
        return subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=repo,
                              capture_output=True, text=True,
                              check=True).stdout.strip()
    except Exception:
        return 'unknown'


def main() -> int:
    for p in (SIDID, CFG, HVSC):
        if not p.exists():
            print(f'error: missing {p}  (run tools/build.sh)', file=sys.stderr)
            return 1
    print(f'  scanning {HVSC} with sidid -m (~3 min) ...', flush=True)
    r = subprocess.run([str(SIDID), str(HVSC), f'-c{CFG}', '-m'],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return 1

    kept, cur_kept, n_files, n_matches, n_multi, dropped = [], False, 0, 0, 0, 0
    for line in r.stdout.splitlines():
        if line.startswith(_TAIL):
            break
        if not line.strip() or line.startswith('Using'):
            continue
        if line[0].isspace():                      # continuation of `cur`
            if cur_kept:
                kept.append(line)
                n_matches += 1
                n_multi += 1
            continue
        parts = line.rsplit(None, 1)
        if len(parts) != 2:
            continue
        rel = parts[0]
        # sidid prints paths relative to its argument's PARENT, so strip the
        # tree name to match the catalogue's repo-relative form.
        rel = rel[len(HVSC.name) + 1:] if rel.startswith(HVSC.name + '/') else rel
        cur_kept = not rel.endswith('.sidfinity.sid')
        if not cur_kept:
            dropped += 1
            continue
        kept.append(f'{rel:<56} {parts[1]}' if len(rel) < 56
                    else f'{rel} {parts[1]}')
        n_files += 1
        n_matches += 1

    if not any(len(k.rsplit(None, 1)[0]) > 56 for k in kept if not k[0].isspace()):
        print('error: no path longer than 56 chars — the de-truncation patch '
              '(tools/sidid_no_truncate.patch) is NOT applied; that silently '
              'drops 2.3% of HVSC. Re-run tools/build.sh.', file=sys.stderr)
        return 1

    hdr = [
        '--- SIDId engine classification for HVSC #85 (hvsc85/).',
        f'--- generator: tools/gen_sidid_dump.py; sidid @ {_git_rev(SIDID.parent)}',
        '---   PATCHED to not truncate paths at 56 chars -- see '
        'tools/sidid_no_truncate.patch.',
        '--- MULTI-SIGNATURE (-m): a file may have SEVERAL matches. The 2nd and',
        '---   later ones are printed with a BLANK name field (leading spaces);',
        '---   a parser keyed on "every line starts with a path" drops them all',
        '---   SILENTLY. Use tools/build_sid_db.load_engine_map.',
        '--- scope: HVSC originals only; our own *.sidfinity.sid rebuilds are',
        f'---   excluded ({dropped:,} dropped). Trailing summary block dropped.',
        f'--- {n_files:,} files, {n_matches:,} matches, '
        f'{n_multi:,} extra matches beyond the first.',
    ]
    OUT.write_text('\n'.join(hdr + kept) + '\n')
    print(f'  wrote {OUT.relative_to(ROOT)}: {n_files:,} files, '
          f'{n_matches:,} matches ({n_multi:,} beyond the first), '
          f'{dropped:,} rebuilds dropped')
    return 0


if __name__ == '__main__':
    sys.exit(main())
