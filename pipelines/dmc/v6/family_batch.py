#!/usr/bin/env python3
"""DMC V6 batch — currently an ACCOUNTING batch, not a build batch.

    PYTHONPATH=tools/py65_lib:tools:src python3 pipelines/dmc/v6/family_batch.py

V6 (the unreleased internal DMC — sidid `DMC_V6.x`, 16 members) has its player
RE done (`pipelines/dmc/v6/RE_NOTES.md`) and an extract started, but NO
composer — nothing can build these members yet. This batch exists anyway,
because every coverage number in the project is computed from a family's
results file: a family WITHOUT one is not 0%, it is INVISIBLE (these 16 were
the last `no_store` bucket `route.py --gaps` reported). So each member gets an
honest row — `unsupported: no_composer` — stamped with the current dmc_v6
code fingerprint, and the family shows up as 0/16 instead of not at all.

When the v6 composer is built: replace `run_member` with the real
config -> extract -> USF -> compose -> verify chain (v5's family_batch is the
template), keep the store id (`dmc_v6` in src/batch_results.STORES) and this
file's name — the fingerprint's BATCH_CONSUMER entry names it — and the rows
here auto-invalidate, since any composer lands inside the hashed
`pipelines/dmc` closure.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
sys.path[:0] = [os.path.join(ROOT, 'tools', 'py65_lib'),
                os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src'), ROOT]

from src.batch_results import load_latest, store  # noqa: E402
from src.code_fingerprint import code_fingerprint  # noqa: E402


def members() -> list[str]:
    """The roster's v6 members — same source every other DMC batch uses."""
    from pipelines.dmc.route import load_roster, ROSTER
    _meta, rows = load_roster(ROSTER)
    return sorted(r['rel'] for r in rows if r.get('pipeline') == 'v6')


def main() -> int:
    st = store('dmc_v6')
    code_hash = code_fingerprint(st.engine)
    done = set()
    if os.path.exists(st.path):
        done = {p for p, r in load_latest(st.path, st.id_key).items()
                if r.get('code_hash') == code_hash}
    todo = [m for m in members() if m not in done]
    print(f'{len(done) + len(todo)} v6 members, {len(done)} current, '
          f'{len(todo)} to record', flush=True)
    with open(st.path, 'a') as f:
        for rel in todo:
            f.write(json.dumps({
                'path': rel, 'status': 'unsupported',
                'reason': 'no_composer',
                'detail': 'v6 composer not built (extract+RE exist; '
                          'see pipelines/dmc/v6/RE_NOTES.md)',
                'build_path': None, 'code_hash': code_hash}) + '\n')
    rows = load_latest(st.path, st.id_key)
    full = sum(1 for r in rows.values() if r['status'] == 'full')
    print(f'DONE  dmc_v6: {full}/{len(rows)} full '
          f'({len(rows) - full} unsupported: no_composer)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
