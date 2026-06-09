#!/usr/bin/env python3
"""Future Composer player-code fingerprinting (version identification).

Each FC version has distinct player code; the same version relocated keeps the
same OPCODE skeleton (relocation changes operand bytes, not opcodes). So the
reachable-code opcode sequence (traced from init+play) is a relocation-invariant
fingerprint of the player VERSION/variant — independent of the song data.

Two metrics:
  - exact opcode-skeleton SHA1   → groups identical player binaries fast
  - opcode 4-gram Jaccard        → merges relocated/trimmed variants into a
                                   version family (same-player ~0.9-1.0,
                                   different version <=0.65, validated on
                                   Adrenalin engine A vs Cyb II vs Hawkeye)

Goal: turn "which FC version + address layout does this SID use" from manual
RE into a lookup — point it at any FC SID (or a relocated sub-engine like
Adrenalin's) and read off its cluster, then reuse a cluster-mate's known layout.

Usage:
    PYTHONPATH=tools/py65_lib:tools:src python3 tools/fc_fingerprint.py [--corpus]
"""
import sys, os, hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py65_lib'))
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from seed_disassembly import trace, _INST_LEN, parse_psid


def opcode_skeleton(mem, init, play, extra=()):
    """Reachable-code opcode sequence from init+play (reloc-invariant).

    `mem` is a 64K image (list/bytes); addresses are absolute (load=0)."""
    payload = bytes(mem[i] for i in range(0x10000))
    _code, starts, _labels, _jsr = trace(payload, 0, init, play, tuple(extra))
    return bytes(mem[pc] for pc in sorted(starts))


def fingerprint_sid(path, run_init=False):
    """Opcode skeleton for a PSID. With run_init=True, runs the PSID init in
    py65 first (needed for self-decompressing FC SIDs whose player is unpacked
    at runtime, e.g. Adrenalin); otherwise fingerprints the raw binary."""
    s = parse_psid(path)
    load, init, play = s['load'], s['init'], s['play']
    if run_init:
        from pipelines.future_composer.engine_model import _run_init_in_py65
        mem = bytearray(_run_init_in_py65(path, subtune=0))
    else:
        mem = bytearray(0x10000)
        payload = s['payload']
        for i, b in enumerate(payload):
            if load + i < 0x10000:
                mem[load + i] = b
    ops = opcode_skeleton(mem, init, play)
    return ops, hashlib.sha1(ops).hexdigest()


def grams(b, n=4):
    return {bytes(b[i:i + n]) for i in range(len(b) - n + 1)}


def jaccard(a, b):
    A, B = grams(a), grams(b)
    return len(A & B) / len(A | B) if (A or B) else 0.0


def cluster_corpus(threshold=0.85):
    """Fingerprint every HVSC MoN/FutureComposer SID and cluster by version."""
    import sqlite3
    root = os.path.join(os.path.dirname(__file__), '..')
    db = sqlite3.connect(os.path.join(root, 'hvsc84.db'))
    # FC only — NB: LIKE '%MoN%' is case-insensitive and would sweep in
    # SoundMONitor, so match FutureComposer explicitly.
    rows = list(db.execute(
        "SELECT path FROM sids WHERE engine LIKE '%FutureComposer%'"))
    fps = []           # (path, ops, exact_hash)
    errs = 0
    for (rel,) in rows:
        p = os.path.join(root, 'hvsc84', rel)
        try:
            ops, h = fingerprint_sid(p)
            if len(ops) < 20:           # too little reachable code → likely packed
                ops2, h2 = fingerprint_sid(p, run_init=True)
                if len(ops2) > len(ops):
                    ops, h = ops2, h2
            fps.append((rel, ops, h))
        except Exception:
            errs += 1
    # 1. exact opcode-skeleton clusters
    exact = {}
    for rel, ops, h in fps:
        exact.setdefault(h, []).append(rel)
    # 2. merge exact clusters into version families by representative similarity
    reps = []          # (hash, representative ops)
    for h, members in exact.items():
        ops = next(o for r, o, hh in fps if hh == h)
        reps.append((h, ops))
    parent = {h: h for h, _ in reps}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            if jaccard(reps[i][1], reps[j][1]) >= threshold:
                parent[find(reps[i][0])] = find(reps[j][0])
    families = {}
    for h, members in exact.items():
        families.setdefault(find(h), []).extend(members)
    return fps, exact, families, errs


if __name__ == '__main__':
    if '--corpus' in sys.argv:
        fps, exact, families, errs = cluster_corpus()
        print(f'fingerprinted {len(fps)} FC SIDs ({errs} errors)')
        print(f'distinct opcode-skeleton hashes: {len(exact)}')
        print(f'version families (Jaccard>=0.85): {len(families)}')
        fam_sorted = sorted(families.items(), key=lambda kv: -len(kv[1]))
        print('\ntop families by size:')
        for fam, members in fam_sorted[:15]:
            print(f'  {len(members):5d}  e.g. {members[0]}')

        # Task 34: where do Adrenalin's sub-engines land?
        from pipelines.future_composer.engine_model import _run_init_in_py65
        root = os.path.join(os.path.dirname(__file__), '..')
        sid = os.path.join(root, 'hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid')
        targets = {
            'engine A (sub0 @7A00)': (_run_init_in_py65(sid, 0), 0x7A00, 0x7A06),
            'sub1 variant (@1021)':  (_run_init_in_py65(sid, 1), 0x1021, 0x1021),
        }
        print('\nAdrenalin sub-engines vs corpus families:')
        for name, (mem, init, play) in targets.items():
            q = opcode_skeleton(mem, init, play)
            best = sorted(
                ((max(jaccard(q, o) for r, o, h in fps if h == rep_h),
                  len(members), members[0])
                 for rep_h, members in families.items()),
                reverse=True)[:3]
            print(f'  {name}:')
            for sim, sz, ex in best:
                print(f'     sim={sim:.3f}  family size={sz}  e.g. {ex}')
    else:
        print(__doc__)
