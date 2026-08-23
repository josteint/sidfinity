#!/usr/bin/env python3
"""migrate_verdict_rows.py — carry verdict rows across a KEY change, or refuse.

A change to `code_fingerprint` itself (a new input folded into the key, a
widened file filter, an EPOCH bump) invalidates every stored verdict in every
family — even though not one INPUT actually moved. That is a false
invalidation: the rows are still correct, the key just describes them
differently. Re-verifying instead costs ~8.5 hours for DMC alone.

Restamping is safe ONLY under a proof, and this tool refuses without one.
It is deliberately not a "mark everything current" button:

  1. Take the family's stamp time (the results file's mtime — the run that
     wrote the current-generation rows ended then).
  2. Expand the family's NEW dependency closure to actual files.
  3. Ask whether ANY of them changed after the stamp time.
  4. If any did, REFUSE that family and name the files. Otherwise append
     restamped rows carrying the old hash, the delta list and the evidence,
     so the decision is auditable and the originals remain (the jsonl is
     append-only, last-wins).

⚠ THE ASSUMPTION, STATED: the file mtime marks the END of the stamping run,
so a file changed DURING that run would slip through. That is the existing
"never land while a batch is in flight" rule, not something this tool can
prove. Everything else is mechanical.

⚠ NOT a substitute for re-verification when an input really moved. A refusal
means re-run the batch for that family.

Precedent: the same argument, hand-rolled, salvaged 8,369 DMC v4 rows on
2026-08-22 after a v5 edit moved the shared `pipelines/dmc` fingerprint.
Once every row carries `fingerprint_components` (pilot b), this becomes a
component diff and the mtime assumption goes away.

Usage:
    python3 tools/migrate_verdict_rows.py --dry-run     # report only
    python3 tools/migrate_verdict_rows.py               # restamp what proves
    python3 tools/migrate_verdict_rows.py --engine dmc_v4
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.code_fingerprint import (code_fingerprint, resolve_roots,   # noqa: E402
                                  _iter_files, fingerprint_components)
from src.batch_results import load_latest                            # noqa: E402
from src.tslog import ts                                             # noqa: E402

# Every family's verdict store. One entry per results file that a batch stamps.
STORES = {
    'dmc_v4': [('tmp/dmc_f1_85_results.jsonl', 'path'),
               ('tmp/dmc_f2_85_results.jsonl', 'path')],
    # ⚠ ONLY THE FAMILY'S LIVE STORE BELONGS HERE. The stamp time is taken from
    # the file's MTIME, which is a lie for any file that was later REWRITTEN:
    # `dmc_v5_85_results.jsonl` (the pre-#85-list baseline) and
    # `dmc_v5_merged.jsonl` were both edited after their rows were produced, so
    # their mtimes postdate the code that made them and a blanket run would
    # have restamped genuinely PRE-FIX verdicts as current — the exact
    # palimpsest C20 is about. They are historical snapshots now; the live
    # store is the post-fix batch.
    'dmc_v5': [('tmp/dmc_v5_r2_results.jsonl', 'path')],
    'fc_standard': [('tmp/fc_std_wide_results.jsonl', 'sid')],
    'music_assembler': [('tmp/masm_wide_results.jsonl', 'sid')],
    'goattracker_v1': [('tmp/gt_v1_results.jsonl', 'path')],
    'basic_program': [('tmp/basic_program_research/family_batch.jsonl', 'path')],
}


def closure_files(engine: str) -> list[Path]:
    roots, _prov = resolve_roots(engine)
    out = []
    for rel in roots:
        out.extend(_iter_files(Path(ROOT) / rel))
    return out


def _commit_at(when: float) -> str | None:
    """The commit that was HEAD at `when`."""
    import subprocess
    iso = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(when))
    r = subprocess.run(['git', 'rev-list', '-1', f'--before={iso}', 'HEAD'],
                       capture_output=True, text=True, cwd=ROOT)
    return r.stdout.strip() or None


def changed_after(files, when: float) -> tuple[list[str], list[str]]:
    """(changed, unverifiable) inputs since `when`.

    CONTENT, not mtime, for everything git tracks: `git diff <commit-at-when>`
    compares the working tree to the exact bytes that were checked out then.
    mtime is a bad change detector — a file that was modified and restored (a
    measurement probe, a checkout, a failed edit) has a fresh mtime and
    identical content, and reading that as "changed" refuses a migration that
    is provably safe. It errs safe, but it errs so often it is useless.

    Untracked files (the built toolchain, .pylocal packages) have no such
    record, so they fall back to mtime and are reported SEPARATELY — the
    caller decides whether to accept them, and the decision is recorded in
    the row rather than assumed here.
    """
    import subprocess
    rels = [f.relative_to(ROOT).as_posix() for f in files]
    tracked = set(subprocess.run(
        ['git', 'ls-files', '--'] + rels, capture_output=True, text=True,
        cwd=ROOT).stdout.split())
    changed = []
    commit = _commit_at(when)
    if commit and tracked:
        # RENAME DETECTION (-M) IS LOAD-BEARING, not a nicety. The fingerprint
        # hashes each file's PATH as well as its bytes, so relocating a tool
        # (e.g. engine tools moving from tools/ into pipelines/<family>/)
        # changes every affected family's key even though not one byte of
        # behaviour moved. Without -M, `git diff` reports the new paths as
        # added-and-changed and this tool refuses every family — turning a pure
        # move into a full re-verification of the whole corpus.
        #
        # With -M, git pairs old->new by content and reports the pair as R100;
        # a 100%-similarity rename is exactly the case where restamping is
        # provably safe. Anything else (R0xx = renamed AND edited, M, A, D)
        # still counts as changed.
        out = subprocess.run(
            ['git', 'diff', '-M', '--name-status', commit, '--'],
            capture_output=True, text=True, cwd=ROOT).stdout
        for line in out.splitlines():
            parts = line.split('\t')
            status = parts[0]
            if status.startswith('R') and len(parts) == 3:
                if status == 'R100':
                    continue          # pure move: content identical
                changed.append(parts[2])
            elif len(parts) >= 2 and parts[-1] in tracked:
                changed.append(parts[-1])
        changed = [c for c in changed if c in tracked]
    untracked = [f for f in files
                 if f.relative_to(ROOT).as_posix() not in tracked]
    unverifiable = sorted(f.relative_to(ROOT).as_posix() for f in untracked
                          if f.stat().st_mtime > when)
    return sorted(set(changed)), unverifiable


def migrate(engine: str, store: str, path_key: str, dry: bool,
            accept_untracked: str = '') -> dict:
    p = os.path.join(ROOT, store)
    if not os.path.exists(p):
        return {'store': store, 'action': 'absent'}
    stamp = os.path.getmtime(p)
    rows = load_latest(p, path_key=path_key)
    cur = code_fingerprint(engine)
    stale = {k: r for k, r in rows.items() if r.get('code_hash') != cur}
    if not stale:
        return {'store': store, 'action': 'already-current', 'rows': len(rows)}

    files = closure_files(engine)
    changed, unverifiable = changed_after(files, stamp)
    old_hashes = sorted({r.get('code_hash') for r in stale.values()})
    info = {'store': store, 'rows': len(rows), 'stale': len(stale),
            'old_hashes': old_hashes, 'changed_inputs': changed,
            'unverifiable': unverifiable, 'n_files': len(files),
            'stamped': time.strftime('%Y-%m-%dT%H:%M',
                                     time.localtime(stamp))}
    if changed:
        info['action'] = 'REFUSED'
        return info
    if unverifiable and not accept_untracked:
        info['action'] = 'REFUSED-untracked'
        return info
    info['action'] = 'restamp' if not dry else 'would-restamp'
    if dry:
        return info
    comps = fingerprint_components(engine)
    with open(p, 'a') as f:
        for r in stale.values():
            row = dict(r)
            row['code_hash'] = cur
            row['restamp_from'] = r.get('code_hash')
            row['restamp_reason'] = (
                'key-definition change (toolchain + verdict inputs folded in, '
                'derived closure); NO input file changed since these rows were '
                'stamped')
            row['restamp_evidence'] = (
                f'migrate_verdict_rows: 0 of {info["n_files"]} closure files '
                f'changed (git content vs the commit at {info["stamped"]})'
                + (f'; untracked accepted: {unverifiable} — '
                   f'{accept_untracked}' if unverifiable else ''))
            row['fingerprint_components'] = comps
            f.write(json.dumps(row) + '\n')
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', action='append')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--accept-untracked', default='',
                    help='REASON for accepting untracked inputs (built '
                         'toolchain, .pylocal) whose mtime moved but whose '
                         'content is known unchanged. Recorded in every row.')
    a = ap.parse_args()
    engines = a.engine or list(STORES)
    refused = 0
    for eng in engines:
        for store, key in STORES.get(eng, []):
            r = migrate(eng, store, key, a.dry_run, a.accept_untracked)
            act = r['action']
            if act == 'absent':
                continue
            if act == 'already-current':
                ts(f'{eng:16s} {store:46s} {r["rows"]:6d} rows already current')
                continue
            ts(f'{eng:16s} {store:46s} {r["stale"]}/{r["rows"]} stale '
               f'(stamped {r["stamped"]}, was {r["old_hashes"]}) -> {act}')
            if act.startswith('REFUSED'):
                refused += 1
                for f in r['changed_inputs'][:10]:
                    ts(f'    CHANGED SINCE STAMP (git content): {f}')
                for f in r['unverifiable'][:10]:
                    ts(f'    UNTRACKED, mtime moved: {f}')
                ts('    -> re-run this family\'s batch; rows NOT restamped')
            elif r.get('unverifiable'):
                ts(f'    untracked accepted: {r["unverifiable"]}')
    if refused:
        ts(f'{refused} store(s) refused — those families need re-verification')
    return 1 if refused else 0


if __name__ == '__main__':
    sys.exit(main())
