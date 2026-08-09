#!/usr/bin/env python3
"""Refresh ONLY engine_docs.csv from tools/engine_docs.json.

The full tools/build_sid_db.py also (re)writes engine_docs, but it re-walks
and re-hashes 60k SIDs. This is the cheap path: after editing engine_docs.json
(e.g. bumping a family LITTLE -> OK once its research-engine sweep lands), run
this to rewrite just engine_docs.csv in seconds. It reads the existing
catalogue parquet for the per-engine SID counts (no re-walk / re-hash).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools'))
import build_sid_db as b               # noqa: E402
from src import sid_db                 # noqa: E402


def main() -> int:
    rows = sid_db.read_all()
    if not rows:
        print('no hvsc85.parquet yet — run tools/build_sid_db.py first',
              file=sys.stderr)
        return 1
    docs = b.build_engine_docs(rows)
    sid_db.write_engine_docs(docs)
    print(f'engine_docs: {len(docs)} families applied to '
          f'{sid_db.ENGINE_DOCS_CSV.relative_to(ROOT)}')
    # quick tally for confirmation
    order = {'OK': 0, 'SOME': 1, 'LITTLE': 2}
    tally: dict[str, int] = {}
    for d in docs:
        tally[d['doc_state']] = tally.get(d['doc_state'], 0) + 1
    print('  tally:', {s: tally[s]
                       for s in sorted(tally, key=lambda x: order.get(x, 3))})
    return 0


if __name__ == '__main__':
    sys.exit(main())
