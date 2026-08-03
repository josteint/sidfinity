#!/usr/bin/env python3
"""Mechanical enforcement of the USF format spec's own invariants.

Why this exists (2026-08-03): the spec (docs/usf_format.md) DECLARES
invariants — the elidability principle, the canonical-fixpoint round trip —
but nothing enforced them. The init.voice_state block emitted five
default-valued fields on every voice of every member for months (11k+ files
carrying `arp: offsets=[] period=1` / `vibrato: scale=0 onset=0` /
`dur_field: $00` noise) and no check existed to notice: uready-review audits
the Principle (§7/§8), not the format spec. Checks that depend on someone
remembering to look eventually fail — this tool makes the spec's invariants
mechanical, cheap, and gating.

Four checks:

1. ROUND-TRIP OBJECT EQUALITY (error): parse(write(x)) == x over a
   stratified corpus sample. The guarantee that makes writer changes safe
   (identical parsed objects => identical built .sid by construction).
2. CANONICAL FIXPOINT (error): write(parse(t1)) == t1 where t1 =
   write(parse(file)) — the spec's declared round-trip invariant.
3. DEFAULT-NOISE CENSUS (warning): tokenize the CURRENT writer's output and
   flag any key whose value is constant across >= NOISE_SHARE of its
   occurrences (with a floor on occurrence count). This is the engine-blind
   detector that would have caught the elidability violations without
   knowing the defaults in advance. Warnings, not errors: some constants
   are legitimately constant — review a flag, then either fix the writer
   (elide it) or add it to ALLOWLIST below with a reason.
4. §7 FORBIDDEN SHAPES (error): dataclass fields in src/usf/types.py whose
   NAME or TYPE matches the principle's forbidden shapes (*Kind:int, *_ptr,
   *_idx, bytes-typed) — the schema half of the uready criterion-2 grep,
   made a standing gate instead of a periodic manual one.

Usage:
    python3 tools/usf_spec_lint.py [--sample N] [--full] [--seed S]

Exit 1 on any check-1/2/4 failure; census findings print as warnings.
Run after ANY change to src/usf/{grammar.lark,parser.py,writer.py,types.py}
— alongside tools/usf_corpus_check.py (which checks the STORED corpus still
parses; this tool checks the CURRENT writer's behaviour).
"""
from __future__ import annotations

import argparse
import glob
import os
import random
import re
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'src'))

# Reviewed legitimately-constant tokens. Add entries ONLY with a reason.
ALLOWLIST: dict[str, str] = {
    # (empty at birth — every current flag is a real elidability finding,
    #  scheduled for the writer-elision cleanup)
}

# Census thresholds: a key is flagged when its top value covers >= SHARE of
# occurrences AND it occurs at least MIN_OCC times in the sample's output.
NOISE_SHARE = 0.99
NOISE_MIN_OCC = 300

# Members that must always be in the sample (known non-default carriers —
# Hubbard init fields, DMC work-file leftovers).
MUST_INCLUDE = [
    'hvsc84/MUSICIANS/H/Hubbard_Rob/Commando.usf',
    'hvsc84/MUSICIANS/D/Doxx/Bassbumper.usf',
]


def _corpus() -> list[str]:
    pats = ['hvsc84/MUSICIANS/*/*/*.usf', 'hvsc84/MUSICIANS/*/*/*/*.usf',
            'hvsc84/DEMOS/*/*.usf', 'hvsc84/GAMES/*/*.usf']
    out: list[str] = []
    for p in pats:
        out.extend(glob.glob(os.path.join(ROOT, p)))
    return sorted(out)


def _stratified_sample(files: list[str], n: int, seed: int) -> list[str]:
    """~n files spread over the letter directories (one bucket per
    MUSICIANS/<L>/), so no family dominates the sample."""
    rng = random.Random(seed)
    buckets: dict[str, list[str]] = defaultdict(list)
    for f in files:
        parts = f.split(os.sep)
        try:
            key = parts[parts.index('MUSICIANS') + 1]
        except ValueError:
            key = parts[-3]
        buckets[key].append(f)
    per = max(1, n // max(1, len(buckets)))
    picked: list[str] = []
    for key in sorted(buckets):
        b = buckets[key]
        picked.extend(b if len(b) <= per else rng.sample(b, per))
    for m in MUST_INCLUDE:
        mp = os.path.join(ROOT, m) if not os.path.isabs(m) else m
        if os.path.exists(mp) and mp not in picked:
            picked.append(mp)
    return picked


# key=value tokens (speed=0, mode=bidirectional, offsets=[..]) and
# key: value tokens (dur_field: $00, pwm_dir: up). Values are single
# non-space words or a bracketed list; multi-word values (byte runs) are
# out of scope — the census targets scalar per-field noise.
_TOK_EQ = re.compile(r'\b([a-z_][a-z0-9_]*)=(\[[^\]]*\]|[^\s\]]+)')
_TOK_COLON = re.compile(
    # value must not itself be a `sub=`-style key (block headers like
    # `arp: offsets=[]` would otherwise read as key 'arp', value 'offsets')
    r'\b([a-z_][a-z0-9_]*):\s+(\$[0-9A-Fa-f]+|-?\d+\b|[a-z_][a-z0-9_]*\b(?!\s*=))')


def _census(texts: list[str]) -> list[tuple[str, str, int, float]]:
    vals: dict[str, Counter] = defaultdict(Counter)
    for t in texts:
        for line in t.splitlines():
            if ';' in line:
                line = line.split(';', 1)[0]      # strip comments
            for k, v in _TOK_EQ.findall(line):
                vals[k][v] += 1
            for k, v in _TOK_COLON.findall(line):
                vals[k][v] += 1
    flags = []
    for k, c in sorted(vals.items()):
        total = sum(c.values())
        if total < NOISE_MIN_OCC:
            continue
        top, n = c.most_common(1)[0]
        share = n / total
        if share >= NOISE_SHARE and k not in ALLOWLIST:
            flags.append((k, top, total, share))
    return flags


_SHAPE_PATTERNS = [
    (re.compile(r'^\s+\w*[Kk]ind\w*\s*:\s*(int|Optional\[int\])'), '*Kind: int'),
    (re.compile(r'^\s+\w+_ptr\s*:'), '*_ptr'),
    (re.compile(r'^\s+\w+_idx\s*:\s*(int|Optional\[int\])'), '*_idx: int'),
    (re.compile(r'^\s+\w+\s*:\s*(bytes|Optional\[bytes\])\b'), ': bytes'),
]


def _forbidden_shapes() -> list[str]:
    hits = []
    path = os.path.join(ROOT, 'src', 'usf', 'types.py')
    for i, line in enumerate(open(path), 1):
        code = line.split('#', 1)[0]
        for pat, label in _SHAPE_PATTERNS:
            if pat.match(code):
                hits.append(f'src/usf/types.py:{i}: {label}: {line.strip()}')
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=int, default=150)
    ap.add_argument('--full', action='store_true')
    ap.add_argument('--seed', type=int, default=7)
    args = ap.parse_args()

    from src.usf.parser import parse_file, parse
    from src.usf.writer import write

    files = _corpus()
    picked = files if args.full else _stratified_sample(
        files, args.sample, args.seed)
    print(f'usf_spec_lint: {len(picked)} of {len(files)} stored .usf '
          f'({"full corpus" if args.full else "stratified sample"})')

    errors = 0
    eq_fail = fix_fail = parse_fail = 0
    texts = []
    for f in picked:
        try:
            a = parse_file(f)
            t1 = write(a)
            b = parse(t1)
            if a != b:
                eq_fail += 1
                print(f'  EQUALITY FAIL  parse(write(x)) != x : {f}')
            t2 = write(b)
            if t1 != t2:
                fix_fail += 1
                print(f'  FIXPOINT FAIL  write not canonical  : {f}')
            texts.append(t1)
        except Exception as e:
            parse_fail += 1
            print(f'  PARSE/WRITE FAIL {type(e).__name__}: {f}')
    errors += eq_fail + fix_fail + parse_fail
    print(f'check 1 round-trip equality : {len(picked) - eq_fail - parse_fail}'
          f'/{len(picked)} ok')
    print(f'check 2 canonical fixpoint  : {len(picked) - fix_fail - parse_fail}'
          f'/{len(picked)} ok')

    flags = _census(texts)
    print(f'check 3 default-noise census: {len(flags)} flagged key(s) '
          f'(warnings — writer-elision candidates or ALLOWLIST entries)')
    for k, top, total, share in flags:
        print(f'  ⚠ {k!r}: value {top!r} in {share:.1%} of {total} occurrences')

    shapes = _forbidden_shapes()
    if shapes:
        errors += len(shapes)
        print(f'check 4 §7 forbidden shapes : {len(shapes)} HIT(S)')
        for h in shapes:
            print(f'  ✗ {h}')
    else:
        print('check 4 §7 forbidden shapes : clean')

    print(f'{"FAIL" if errors else "OK"}: {errors} error(s), '
          f'{len(flags)} warning(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
