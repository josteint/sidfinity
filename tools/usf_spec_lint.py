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
   The census runs at TWO grains: whole-corpus AND per engine FAMILY
   (path -> catalogue engine -> build_sid_db.engine_to_family). A constant
   that only one family emits is share-diluted below the whole-corpus
   threshold by every other family's varied values (the B4 gap,
   2026-08-11) — the per-family pass sees it. Family resolution needs the
   duckdb CLI; when unavailable the census degrades to whole-corpus only,
   loudly. Per-family flags allowlist as 'family:key'.
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
# Global keys apply everywhere; 'family:key' entries apply to that family's
# per-family census only.
ALLOWLIST: dict[str, str] = {
    'lo': 'FC pulse-program bound (prog N: lo=.. hi=..); dict-carried (no '
          'dataclass default to elide against) and a genuine musical bound '
          '— the corpus is predominantly full-range 1..15 (2026-08-03)',
    'hi': 'see lo — the paired upper pulse-program bound',
    'hubbard:min_hi': 'Hubbard PWM lower flip threshold — HARDCODED $08 in '
                      'the engine (reference_hubbard_pwm_bounds), so family-'
                      'constant genuine content; the writer already elides '
                      'the dataclass default 0 (2026-08-11)',
    'hubbard:max_hi': 'see hubbard:min_hi — the paired upper threshold $0E',
    # --- elided-at-default enums/flags: the writer only prints the
    # NON-default value, so when the corpus uses exactly one non-default
    # value the census sees a "100% constant" BY CONSTRUCTION. Working as
    # intended — the default half is already elided. (2026-08-11 full run)
    'initial_dir': "slide dir enum elided at 'up'; only 'down' slides exist "
                   'corpus-wide (5,120 occ, every family) — supersedes the '
                   'former hubbard:initial_dir entry',
    'direction': "FC vibrato/slide dir enum elided at 'up'; only 'down' "
                 'occurs in the stored FC corpus',
    'gate_open': 'presence-only C30 co-field (`if e.gate_open: gate_open=1`);'
                 ' absence is the elided default',
    'slide_phase': 'priming scalar emitted only when observed (is not None); '
                   'value 1 = the dominant global half-rate parity',
    'dmc:speed_ctr_init': 'priming scalar emitted only when truthy; 1 is the '
                          'dominant observed work-file leftover',
    'dmc:instr': 'init.voice_state starting instrument, emitted only when '
                 'primed; i1 dominance is a musical fact of the corpus',
    'soft_cmd': 'NoteRow fx-flag parameter (stated command, C14); presence = '
                'the byte fact, and 1 is the only parameter value the corpus '
                'states today',
    # --- old-form params{} keys DEFERRED to their families' campaigns:
    # F1 (2026-08-04) typed these but left the stored f2/f4/v5 corpora
    # old-form on purpose ("swaps at its own campaign").
    'hard_restart': 'f2 probed param set, old-form params{} until the '
                    'family-2 campaign (F1 decision 2026-08-04)',
    'rest_effects': 'see hard_restart',
    'cymbal_onset': 'see hard_restart',
    'gate_off_hold': 'see hard_restart',
    'vib_ramp': 'see hard_restart',
    'otrk_pad_s1_v1': 'C32 legacy fitted orderlist params in f4/v5 corpora; '
                      'stated-fold swaps them at those campaigns\' '
                      'mass-writes',
    'otrk_pad_s1_v2': 'see otrk_pad_s1_v1',
    'otrk_pad_s1_v3': 'see otrk_pad_s1_v1',
    'dmc:otrk_legacy_s1_v3': 'the documented entry+1 otrk approximation '
                             '(C32 residue), carried until stated-fold '
                             'covers it',
    # --- dict-carried / required fields with a family-constant value
    'd418': 'FC filter-program field, dict-carried like lo/hi (no dataclass '
            'default to elide against); 0 = no volume-nibble writes, the '
            'dominant musical case',
    'basic_program:sid': 'required PSID header model field '
                         '(feedback_header_flags_audible); every RSID-BASIC '
                         'rip is a 6581 tune — a collection fact',
    'basic_program:tempo': 'required MusicSubtune field (no default); the '
                           'trace-lift grid is 1 frame/step by construction',
    'basic_program:bp_init0': 'legacy-form encoded init write ((reg<<8)|val; '
                              '$180F = D418=$0F, every BASIC player\'s first '
                              'write); disappears as members adopt NF',
    'basic_program:bp_multi': 'presence-only marker (set to 1 only in the '
                              'multi-template branch); absence is the elided '
                              'default',
    'basic_program:mode': 'global-track stated nibble (Optional, None=carry; '
                          'presence = the $D418 write stated it, C32 stated '
                          'notation) — BASIC tunes just never set filter-mode '
                          'bits, so the stated value is always $00',
}

# Structural keywords the colon-tokenizer must not read as fields (their
# "value" is the following content token, not a field value).
SKIP_KEYS = {
    'stated',                   # `orderlist stated: <entries>`
    'offtable_freq',            # `offtable_freq: at(...)` — 'at' is the
                                # read-flag head, not a value
}

# Census thresholds: a key is flagged when its top value covers >= SHARE of
# occurrences AND it occurs at least MIN_OCC times in the sample's output.
NOISE_SHARE = 0.99
NOISE_MIN_OCC = 300
# Per-family grain: lower floor (a family's slice of the sample is smaller),
# and every family is topped up to FAM_SAMPLE_MIN files so small families
# (hubbard: 12 stored .usf, companion: 25) are census-visible at all.
NOISE_MIN_OCC_FAM = 60
FAM_SAMPLE_MIN = 20

# Members that must always be in the sample (known non-default carriers —
# Hubbard init fields, DMC work-file leftovers).
MUST_INCLUDE = [
    'hvsc85/MUSICIANS/H/Hubbard_Rob/Commando.usf',
    'hvsc85/MUSICIANS/D/Doxx/Bassbumper.usf',
]


def _family_map(files: list[str]) -> dict[str, str | None]:
    """{usf path -> engine family} via the catalogue + engine_to_family.

    Returns {} when the catalogue/duckdb is unavailable (census then runs
    whole-corpus only — the caller prints the degradation)."""
    try:
        sys.path.insert(0, os.path.join(ROOT, 'tools'))
        from build_sid_db import engine_to_family
        from src import sid_db
        eng = dict(sid_db.query('SELECT path, engine FROM sids'))
    except Exception as e:
        print(f'  ⚠ per-family census unavailable ({type(e).__name__}: {e})')
        return {}
    pref = os.path.join(ROOT, 'hvsc85') + os.sep
    out: dict[str, str | None] = {}
    for f in files:
        rel = f[len(pref):] if f.startswith(pref) else f
        sid = rel[:-len('.usf')] + '.sid'
        e = eng.get(sid)
        out[f] = engine_to_family(e) if e else None
    return out


def _corpus() -> list[str]:
    pats = ['hvsc85/MUSICIANS/*/*/*.usf', 'hvsc85/MUSICIANS/*/*/*/*.usf',
            'hvsc85/DEMOS/*/*.usf', 'hvsc85/GAMES/*/*.usf']
    out: list[str] = []
    for p in pats:
        out.extend(glob.glob(os.path.join(ROOT, p)))
    return sorted(out)


def _stratified_sample(files: list[str], n: int, seed: int,
                       fam: dict[str, str | None]) -> list[str]:
    """~n files spread over the letter directories (one bucket per
    MUSICIANS/<L>/), so no family dominates the sample; then every engine
    family is topped up to FAM_SAMPLE_MIN files so the per-family census
    has material for small families too."""
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
    have = set(picked)
    by_fam: dict[str, list[str]] = defaultdict(list)
    for f in files:
        if fam.get(f):
            by_fam[fam[f]].append(f)
    for family in sorted(by_fam):
        short = FAM_SAMPLE_MIN - sum(1 for f in have if fam.get(f) == family)
        pool = [f for f in by_fam[family] if f not in have]
        for f in (pool if len(pool) <= short else rng.sample(pool, short)) \
                if short > 0 else []:
            picked.append(f)
            have.add(f)
    for m in MUST_INCLUDE:
        mp = os.path.join(ROOT, m) if not os.path.isabs(m) else m
        if os.path.exists(mp) and mp not in have:
            picked.append(mp)
    return picked


# key=value tokens (speed=0, mode=bidirectional, offsets=[..]) and
# key: value tokens (dur_field: $00, pwm_dir: up). Values are single
# non-space words or a bracketed list; multi-word values (byte runs) are
# out of scope — the census targets scalar per-field noise.
_TOK_EQ = re.compile(r'\b([a-z_][a-z0-9_]*)=(\[[^\]]*\]|[^\s\]]+)')
_TOK_COLON = re.compile(
    # value must not itself be a `sub=`-style key (block headers like
    # `arp: offsets=[]` would otherwise read as key 'arp', value 'offsets').
    # Keyword values may be UPPERCASE (`clock: PAL`) — a lowercase-only value
    # class silently dropped those and censused `clock` as 100% 'unknown'
    # (the only lowercase value), the 2026-08-11 full-run artifact.
    r'\b([a-z_][a-z0-9_]*):\s+(\$[0-9A-Fa-f]+|-?\d+\b|[A-Za-z_][A-Za-z0-9_]*\b(?!\s*=))')


def _tokenize(text: str) -> Counter:
    c: Counter = Counter()
    for line in text.splitlines():
        if ';' in line:
            line = line.split(';', 1)[0]          # strip comments
        for k, v in _TOK_EQ.findall(line):
            c[(k, v)] += 1
        for k, v in _TOK_COLON.findall(line):
            if k not in SKIP_KEYS:
                c[(k, v)] += 1
    return c


def _flag(vals: dict[str, Counter], min_occ: int,
          allow_prefix: str = '') -> list[tuple[str, str, int, float]]:
    flags = []
    for k, c in sorted(vals.items()):
        total = sum(c.values())
        if total < min_occ:
            continue
        top, n = c.most_common(1)[0]
        if set(c) == {'true'}:
            # presence-only boolean: this codebase's writers emit bool
            # fields conditionally (`keep_running=true` only when true),
            # so an all-'true' key is 100%-constant BY CONSTRUCTION —
            # absence already IS the elided default. An unconditionally
            # emitted default bool would show 'false' and still flag.
            continue
        share = n / total
        if share >= NOISE_SHARE and k not in ALLOWLIST \
                and (allow_prefix + k) not in ALLOWLIST:
            flags.append((k, top, total, share))
    return flags


def _census(texts: list[tuple[str | None, str]]) -> tuple[
        list[tuple[str, str, int, float]],
        list[tuple[str, str, str, int, float]]]:
    """(global flags, per-family flags). texts = [(family or None, text)].

    A per-family flag is reported only when the key is NOT flagged globally
    (a global flag already covers every family)."""
    glob_vals: dict[str, Counter] = defaultdict(Counter)
    fam_vals: dict[str, dict[str, Counter]] = defaultdict(
        lambda: defaultdict(Counter))
    for family, t in texts:
        for (k, v), n in _tokenize(t).items():
            glob_vals[k][v] += n
            if family:
                fam_vals[family][k][v] += n
    global_flags = _flag(glob_vals, NOISE_MIN_OCC)
    seen = {k for k, *_ in global_flags}
    fam_flags = []
    for family in sorted(fam_vals):
        for k, top, total, share in _flag(
                fam_vals[family], NOISE_MIN_OCC_FAM, family + ':'):
            if k not in seen:
                fam_flags.append((family, k, top, total, share))
    return global_flags, fam_flags


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
    fam = _family_map(files)
    picked = files if args.full else _stratified_sample(
        files, args.sample, args.seed, fam)
    n_fams = len({f for f in fam.values() if f})
    print(f'usf_spec_lint: {len(picked)} of {len(files)} stored .usf '
          f'({"full corpus" if args.full else "stratified sample"}, '
          f'{n_fams} families)' if fam else
          f'usf_spec_lint: {len(picked)} of {len(files)} stored .usf '
          f'({"full corpus" if args.full else "stratified sample"}, '
          f'NO family map — whole-corpus census only)')

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
            texts.append((fam.get(f), t1))
        except Exception as e:
            parse_fail += 1
            print(f'  PARSE/WRITE FAIL {type(e).__name__}: {f}')
    errors += eq_fail + fix_fail + parse_fail
    print(f'check 1 round-trip equality : {len(picked) - eq_fail - parse_fail}'
          f'/{len(picked)} ok')
    print(f'check 2 canonical fixpoint  : {len(picked) - fix_fail - parse_fail}'
          f'/{len(picked)} ok')

    flags, fam_flags = _census(texts)
    print(f'check 3 default-noise census: {len(flags)} global + '
          f'{len(fam_flags)} per-family flagged key(s) '
          f'(warnings — writer-elision candidates or ALLOWLIST entries)')
    for k, top, total, share in flags:
        print(f'  ⚠ {k!r}: value {top!r} in {share:.1%} of {total} occurrences')
    for family, k, top, total, share in fam_flags:
        print(f'  ⚠ [{family}] {k!r}: value {top!r} in {share:.1%} of '
              f'{total} occurrences')

    shapes = _forbidden_shapes()
    if shapes:
        errors += len(shapes)
        print(f'check 4 §7 forbidden shapes : {len(shapes)} HIT(S)')
        for h in shapes:
            print(f'  ✗ {h}')
    else:
        print('check 4 §7 forbidden shapes : clean')

    print(f'{"FAIL" if errors else "OK"}: {errors} error(s), '
          f'{len(flags) + len(fam_flags)} warning(s)')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
