"""Music Assembler FAMILY batch (tier 2): every HVSC Music_Assembler SID
through locate -> model -> USF -> composed player -> writelog verify.

The full pipeline is exercised, SID -> USF -> SID: the batch writes each
member's .usf and rebuilds FROM it, so a member counted FULL here is one whose
stored USF really does specify the music (no model shortcut).

Tier 1 (every change) is the feature-cover portfolio in tools/regression.py.
Run THIS at milestones. Results stream to tmp/masm_wide_results.jsonl, one
JSON object per SID, crash-safe append and resume-safe: a row is reused only
when its `code_hash` matches the current fingerprint, so a code change
re-verifies exactly the members it could have affected (see
src/code_fingerprint.py).

Statuses:
  full        every subtune is_full over songlength*1.1
  partial     some subtune diverges (first divergence signature kept)
  unsupported no player located / decode refused (reason kept)
  error       unexpected exception (traceback tail kept)

Each row records `build_path` so the mass-write REPLAYS the path the verdict
came from rather than re-deriving it (ledger C20, fourth layer).

Run:  python3 tools/masm_family_batch.py
"""
import json
import os
import sys
import traceback
from multiprocessing import Pool

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [ROOT, os.path.join(ROOT, 'tools'), os.path.join(ROOT, 'src')]
os.chdir(ROOT)
os.environ['TMPDIR'] = os.path.join(ROOT, 'tmp', 'work')

OUT = os.path.join(ROOT, 'tmp', 'masm_wide_results.jsonl')

from src.code_fingerprint import code_fingerprint   # noqa: E402
from src.jobs import default_jobs                   # noqa: E402

CODE_HASH = code_fingerprint('music_assembler')


def run(sp):
    import tempfile
    from pipelines.music_assembler.extract.model import extract
    from pipelines.music_assembler.extract.to_usf import model_to_usf
    from pipelines.music_assembler.from_usf import build_masm_sid
    from pipelines.music_assembler.verify import verify
    from src.usf.parser import parse_file
    from src.usf.writer import write_file

    rec = {'sid': sp, 'build_path': 'single'}
    try:
        m = extract(sp)
        td = tempfile.mkdtemp()
        up = os.path.join(td, 'a.usf')
        write_file(model_to_usf(m), up)
        sid = os.path.join(td, 'a.sid')
        with open(sid, 'wb') as f:
            f.write(build_masm_sid(parse_file(up)))
        r = verify(sp, sid)
        rec['status'] = 'full' if r.get('is_full') else 'partial'
        rec['play_match'] = r.get('play_match')
        rec['play_len_a'] = r.get('play_len_a')
        rec['play_len_b'] = r.get('play_len_b')
        rec['state_match'] = r.get('state_match')
        if not r.get('is_full'):
            rec['first_play_diff'] = r.get('first_play_diff')
    except ValueError as e:
        rec['status'] = 'unsupported'
        rec['reason'] = str(e)[:120]
    except Exception:
        rec['status'] = 'error'
        rec['error'] = traceback.format_exc()[-600:]
    return rec


if __name__ == '__main__':
    from src import sid_db
    sids = [p for (p,) in sid_db.connect().execute(
        "SELECT path FROM sids WHERE engine LIKE '%Music_Assembler%' "
        "ORDER BY path")]
    done = set()
    if os.path.exists(OUT):
        with open(OUT) as f:
            for line in f:
                if line.strip():
                    d = json.loads(line)
                    if d.get('code_hash') == CODE_HASH:
                        done.add(d['sid'])
    todo = [s for s in sids if s not in done]
    print('%d MA SIDs, %d done, %d to run' % (len(sids), len(done), len(todo)),
          flush=True)
    counts = {}
    with Pool(default_jobs(cap=max(1, len(todo)))) as pool, open(OUT, 'a') as out:
        for i, rec in enumerate(pool.imap_unordered(run, todo), 1):
            rec['code_hash'] = CODE_HASH
            out.write(json.dumps(rec) + '\n')
            out.flush()
            counts[rec['status']] = counts.get(rec['status'], 0) + 1
            if i % 100 == 0:
                print('%d/%d %s' % (i, len(todo), counts), flush=True)
    print('DONE', counts, flush=True)
