"""FC-standard FAMILY batch (tier 2): every HVSC FutureComposer SID
through the factory -> USF -> featuredriven build -> writelog verify.

Tier-1 (every change) is the 11-member feature-cover portfolio inside
tools/regression.py. Run THIS at milestones / after standard-chain work:
results stream to tmp/fc_std_wide_results.jsonl (resume-safe: delete the
records you want re-verified — tmp/strip_stale.py pattern — and re-run).

Results stream to tmp/fc_std_wide_results.jsonl (one JSON object per
SID, crash-safe append). Statuses:
  flagged  - fc_standard_config raised FCStandardUnsupported (reason)
  full     - every subtune is_full at songlength*1.1+1s
  partial  - some subtune diverges (first_play_diff signature kept)
  error    - unexpected exception (traceback tail kept)

Run:  PYTHONPATH=.:tools/py65_lib:tools:src python3 tmp/run_wide.py
"""
import json, os, sys, traceback
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.environ['TMPDIR'] = os.path.join(ROOT, 'tmp', 'work')

OUT = os.path.join(ROOT, 'tmp', 'fc_std_wide_results.jsonl')

# Resume-cache invalidation on code change (see src/code_fingerprint.py).
from src.code_fingerprint import code_fingerprint  # noqa: E402
from src.jobs import default_jobs  # noqa: E402
CODE_HASH = code_fingerprint('fc_standard')


def run(sp):
    from pipelines.future_composer.standard.config import (
        fc_standard_config, FCStandardUnsupported)
    from pipelines.future_composer.to_usf import write_canary_usf
    from pipelines.future_composer.verify import verify_featuredriven
    rec = {'sid': sp}
    usf_path = None
    try:
        cfg = fc_standard_config('hvsc85/' + sp)
        usf_path = write_canary_usf(cfg)
        r = verify_featuredriven(cfg)
        subs = {}
        for s, v in r['subtunes'].items():
            subs[str(s)] = {
                'is_full': v['is_full'],
                'play_match': v.get('play_match'),
                'play_overlap': v.get('play_overlap'),
                'shift_d': v.get('shift_d'),
                'state_match': v.get('state_match'),
                'state_diff': v.get('state_diff'),
                'first_play_diff': v.get('first_play_diff'),
                'len_post': (v.get('len_post_a'), v.get('len_post_b')),
                'duration_used': v.get('duration_used'),
            }
        rec['status'] = 'full' if r['all_full'] else 'partial'
        rec['subs'] = subs
    except FCStandardUnsupported as e:
        rec['status'] = 'flagged'
        rec['reason'] = e.reason
    except Exception:
        rec['status'] = 'error'
        rec['error'] = traceback.format_exc()[-600:]
    if rec['status'] != 'full' and usf_path and os.path.exists(usf_path):
        os.unlink(usf_path)          # keep hvsc85 clean of unverified USFs
    return rec


def members() -> list[str]:
    """Every HVSC member this batch enumerates, HVSC-relative.

    Module level so `tools/verdict_gaps.py` can ask the batch itself what it
    claims instead of re-writing the query (backlog item 37): a gap check
    that duplicates the enumeration drifts away from it, and the drift is
    invisible in exactly the direction that matters.
    """
    import sys as _sys
    _sys.path.insert(0, ROOT)
    from src import sid_db
    return [p for (p,) in sid_db.connect().execute(
        "SELECT path FROM sids WHERE engine LIKE '%FutureComposer%' "
        "ORDER BY path")]


if __name__ == '__main__':
    import sys as _sys
    _sys.path.insert(0, ROOT)
    sids = members()
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            for line in f:
                if not line.strip():
                    continue
                d = json.loads(line)
                if d.get('code_hash') == CODE_HASH:
                    done.add(d['sid'])
    todo = [s for s in sids if s not in done]
    print(f'{len(sids)} FC SIDs, {len(done)} done, {len(todo)} to run',
          flush=True)
    counts = {}
    with Pool(default_jobs(cap=len(todo))) as pool, open(OUT, 'a') as out:
        for i, rec in enumerate(pool.imap_unordered(run, todo), 1):
            rec['code_hash'] = CODE_HASH
            out.write(json.dumps(rec) + '\n')
            out.flush()
            counts[rec['status']] = counts.get(rec['status'], 0) + 1
            if i % 50 == 0:
                print(f'{i}/{len(todo)} {counts}', flush=True)
    print('DONE', counts, flush=True)
