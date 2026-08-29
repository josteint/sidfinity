"""code_fingerprint.py — content hash of an engine's build+verify dependency
set, used by the family batches to invalidate resume-cache rows whose verdict
predates a code change.

A batch's results jsonl is a persisted verdict store: on resume it skips
already-done paths. That is a palimpsest trap — a member recorded FULL under
older code silently carries its stale verdict across a fix, and later surfaces
as a phantom "my fix regressed N FULLs". The cure: stamp every result row with
`code_fingerprint(engine)` and, on resume, reuse a row ONLY if its stored
code_hash equals the current fingerprint. Any code change to the engine's
dependency set re-runs exactly the members it could have affected.

This is safe-by-construction (no need to remember to delete the jsonl) AND
correct under parallel sessions on different engines: a SHARED-code edit
(src/usf, verify_cycle) changes every dependent engine's fingerprint so each
re-verifies; an OTHER-engine edit is not in this engine's dependency set, so it
does not needlessly invalidate this one.

=== THE TWO AXES (Rothermel & Harrold), and which one bites ===

  PRECISION failure  — the set is too BROAD: re-verification we didn't need.
                       Costs compute. CANNOT produce a wrong answer.
  INCLUSIVENESS      — the set is too NARROW: a cached FULL that current code
  (safety) failure     cannot reproduce. SILENTLY WRONG. This is a ninth layer
                       of ledger C20, sitting in the invalidation function.

Everything below is arranged so that the safe direction is the default. Three
inclusiveness holes were measured on 2026-08-22 and are closed here:

  1. `*.py`-ONLY GLOBBING left `pipelines/dmc/docs/*.bin` — the CANON PLAYER
     BINARIES the DMC factory dispatches and probes against — unhashed, though
     they sit inside a declared dir. Regenerate one and every DMC verdict still
     reads "current". Now: an INERT-suffix denylist (documentation and research
     artifacts), so a new file TYPE is hashed by default.
  2. THE TOOLCHAIN WAS NOT HASHED. `tools/siddump` sits on BOTH SIDES of the
     comparison — it produces the REFERENCE trace too. Rebuild it, or relink
     against a different libsidplayfp, and ground truth moves with nothing
     invalidated. (Bazel documents this verbatim as a known remote-caching
     issue; ccache treats hashing the compiler as non-negotiable; REAPI
     requires tools inside the input root.) Same for `xa65`, which assembles
     the bytes we then measure.
  3. VERDICT INPUTS WERE NOT HASHED. `src/composer_runtime/` EMITS the bytes;
     `src/songlengths.py` + `tools/songlength_overrides.json` set the verify
     WINDOW (C20's eighth layer was exactly a window change silently
     invalidating verdicts); `tools/seed_disassembly.py` supplies subtune count
     and vectors to extract AND verify; `src/usf/grammar.lark` parses the USF.

=== DECLARED vs DERIVED ===

Hand-declared-and-unenforced is the one combination nobody ships: Google does
hand-declare deps in BUILD files, but an under-declaration is a sandbox failure
or a strict-deps BUILD error, never a silent cache hit. So `DEPS` below is the
FALLBACK, not the source of truth. When `tools/engine_deps.json` carries a
derived set for (engine, consumer) — produced by `tools/derive_deps.py` from a
`sys.modules` snapshot over a PATH-STRATIFIED sample — that set is used
instead. It captures function-local imports by construction (a static walk
cannot) and separates sibling families that merely share a directory.

⚠ A DERIVED SET GOES STALE when a new import appears, and stale-narrow is the
unsafe direction. Two guards, both here:
  * `_ALWAYS` is unioned into every fingerprint regardless of derivation, so a
    derivation that missed the toolchain or the USF grammar cannot under-hash.
  * `check_derived_closure()` lets a batch re-snapshot `sys.modules` after its
    first member and assert no repo module outside the stored set was loaded.
    That converts a silent cache hit into a loud failure — the property Azure
    TIA calls safe fallback.

=== EPOCH ===
`EPOCH` is a bumpable salt (REAPI's `salt`, sccache's cache-buster) for "I know
something moved that the hash cannot see". Bump it and every verdict
invalidates. Use it when a dependency is discovered to have been outside the
key all along, and there is no cheap way to prove which rows were affected.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Bump to invalidate every verdict in every family. See module docstring.
EPOCH = 1

# Documentation and research artifacts: never read by build/verify code, and
# edited constantly (RE_NOTES.md changes every round). Hashing them would make
# the gate unusable and push us toward switching it off, which is worse than
# the precision loss. Everything NOT listed here is hashed — so a new file type
# lands on the safe side by default.
_INERT_SUFFIXES = frozenset({
    '.md', '.txt', '.s', '.pdf', '.zip', '.d64', '.prg', '.prg_',
    '.png', '.jpg', '.gif', '.html', '.log',
})

# The tools that PRODUCE the compared traces and the compared bytes. Hashing
# these is the single most important fix in this module: siddump generates the
# reference trace as well as ours.
_TOOLCHAIN = ['tools/siddump', 'tools/xa65/xa/xa']

# Inputs that shape the verdict without being "engine code".
_VERDICT_INPUTS = [
    'src/composer_runtime',            # xa65 driver + PSID header: emits bytes
    'src/songlengths.py',              # the verify WINDOW (C20 eighth layer)
    'tools/songlength_overrides.json', # ... and its corrections
    'tools/seed_disassembly.py',       # parse_psid: subtune count + vectors
]

# Unioned into EVERY fingerprint, derived or declared. A derivation that missed
# one of these cannot under-hash the key.
_ALWAYS = ['src/usf', 'pipelines/hubbard/verify_cycle.py'] + _VERDICT_INPUTS + _TOOLCHAIN

# Shared build+verify dependencies every batched engine imports.
_SHARED = list(_ALWAYS)

# Per-engine dependency roots — the FALLBACK when no derived set exists.
# A directory is hashed recursively; a file is hashed directly.
DEPS: dict[str, list[str]] = {
    'dmc_v4':         ['pipelines/dmc'] + _SHARED,
    'dmc_v5':         ['pipelines/dmc'] + _SHARED,
    'dmc_v6':         ['pipelines/dmc'] + _SHARED,
    'fc_standard':    ['pipelines/future_composer'] + _SHARED,
    'goattracker_v1': ['pipelines/goattracker/v1'] + _SHARED,
    'basic_program':  ['pipelines/basic_program'] + _SHARED,
    'music_assembler': ['pipelines/music_assembler'] + _SHARED,
    'digi_organizer':  ['pipelines/digi_organizer',
                        'pipelines/hubbard/sample.py',
                        'pipelines/hubbard/flac_io.py'] + _SHARED,
}

# The consumer that STAMPS each engine's verdict rows. Everyone who computes a
# fingerprint for that engine — the batch that stamps, `corpus_sync` that
# checks — must use the SAME closure, or they disagree about what is current.
# So `code_fingerprint(engine)` resolves through here by default, and only a
# consumer measuring something else (a different tool's closure) passes an
# explicit name.
BATCH_CONSUMER: dict[str, str] = {
    'dmc_v4':          'dmc_family_batch',
    'dmc_v5':          'dmc_v5_family_batch',
    'dmc_v6':          'dmc_v6_family_batch',
    'fc_standard':     'fc_family_batch',
    'goattracker_v1':  'goattracker_v1_family_batch',
    'basic_program':   'basic_program_batch',
    'music_assembler': 'masm_family_batch',
    'digi_organizer':  'digi_organizer_family_batch',
}

# {engine: {consumer: [repo-relative files]}} — written by tools/derive_deps.py.
DERIVED_PATH = ROOT / 'tools' / 'engine_deps.json'

_DERIVED_CACHE: dict | None = None


def _derived() -> dict:
    global _DERIVED_CACHE
    if _DERIVED_CACHE is None:
        try:
            _DERIVED_CACHE = json.loads(DERIVED_PATH.read_text())
        except (OSError, ValueError):
            _DERIVED_CACHE = {}
    return _DERIVED_CACHE


# Cache-management code, not build/verify code: a batch imports this module to
# COMPUTE the key, so a derived closure captures it — and then every edit to
# the hashing logic invalidates every verdict in every family, including edits
# that only widen what the key covers. It cannot affect a verdict (nothing here
# runs during extract, compose or verify), so it is excluded by name. Anything
# that reads it and CAN affect a verdict would have to be listed separately.
_KEY_MANAGEMENT = frozenset({'src/code_fingerprint.py'})

# Test-SELECTION artifacts: they decide WHICH members tier 1 runs, never what a
# build emits. Once the engine tools moved into `pipelines/<family>/`, these
# landed inside the hashed dirs — and then re-deriving a portfolio would
# invalidate that family's verdicts, which is backwards: choosing a different
# sample cannot change what the composer produces. Matched by suffix so a new
# family's portfolio is excluded automatically.
#
# `roster.json` (pipelines/dmc/route.py) is the same category one level up: it
# decides which members a FAMILY BATCH iterates. Without this exclusion it
# self-invalidates — the roster stamps the dmc_v4/dmc_v5 fingerprints into
# itself, lives inside `pipelines/dmc`, and so moves the key it just recorded
# (observed immediately on landing; ledger C20's ninth layer, "the key
# SELF-INVALIDATED"). Excluding it is SAFE in the direction that matters: a
# roster change alters the SET of members a batch visits, never the bytes any
# one member builds to, and verdict rows are per-member.
_SELECTION_SUFFIXES = ('_regression_portfolio.json', 'roster.json')


def _iter_files(root: Path):
    """Every hashable file under `root` (or `root` itself if it is a file).

    Skips __pycache__, dotfiles, and the inert suffixes. Sorted for
    determinism across processes and filesystems.
    """
    if root.is_file():
        try:
            rel = root.relative_to(ROOT).as_posix()
            if rel in _KEY_MANAGEMENT or rel.endswith(_SELECTION_SUFFIXES):
                return
        except ValueError:
            pass
        yield root
        return
    if not root.is_dir():
        return
    out = []
    for f in root.rglob('*'):
        if not f.is_file():
            continue
        if '__pycache__' in f.parts:
            continue
        if f.name.startswith('.'):
            continue
        if f.suffix.lower() in _INERT_SUFFIXES:
            continue
        rel = f.relative_to(ROOT).as_posix()
        if rel in _KEY_MANAGEMENT or rel.endswith(_SELECTION_SUFFIXES):
            continue
        out.append(f)
    yield from sorted(out)


def _hash_roots(roots) -> str:
    h = hashlib.sha256()
    h.update(f'epoch={EPOCH}\0'.encode())
    for rel in roots:
        p = ROOT / rel
        if p.is_file() or p.is_dir():
            for f in _iter_files(p):
                h.update(f.relative_to(ROOT).as_posix().encode())
                h.update(b'\0')
                h.update(f.read_bytes())
                h.update(b'\0')
        else:
            # A declared input that is absent is itself a fact about the build
            # (an unbuilt toolchain); record it rather than crashing or, worse,
            # silently hashing nothing.
            h.update(f'{rel}\0<ABSENT>\0'.encode())
    return h.hexdigest()[:16]


def _declared_data_files(engine: str) -> list[str]:
    """Non-code inputs inside the engine's declared dirs.

    ⚠ A DERIVED SET CANNOT SEE DATA. It is a `sys.modules` snapshot, and
    `sys.modules` holds Python modules — so switching an engine to a derived
    set silently DROPPED `pipelines/dmc/docs/*.bin`, the canon player binaries
    the DMC factory dispatches and probes against. That is precisely the file
    class the toolchain fix was about, un-hashed again one commit later by the
    fix that was supposed to make the key more accurate.

    So the split is: DERIVED covers CODE (it alone can see function-local
    imports), DECLARED covers DATA (no import mechanism can reveal a file the
    code merely opens). Data files are few and change rarely, so taking all of
    a family's declared data costs almost no precision.
    """
    out = []
    for rel in DEPS.get(engine, []):
        for f in _iter_files(ROOT / rel):
            if f.suffix.lower() != '.py':
                out.append(f.relative_to(ROOT).as_posix())
    return out


def resolve_roots(engine: str, consumer: str | None = None) -> tuple[list[str], str]:
    """(roots, provenance) for `engine`/`consumer`.

    Prefers the derived set; falls back to the declared one. `_ALWAYS` and the
    declared DATA files are unioned in either way.
    """
    consumer = consumer or BATCH_CONSUMER.get(engine)
    d = _derived().get(engine, {})
    if consumer and consumer in d:
        return (sorted(set(d[consumer]) | set(_ALWAYS)
                       | set(_declared_data_files(engine))),
                f'derived:{consumer}')
    try:
        return DEPS[engine], 'declared'
    except KeyError:
        raise KeyError(f'unknown engine {engine!r}; add it to '
                       f'code_fingerprint.DEPS') from None


def code_fingerprint(engine: str, consumer: str | None = None) -> str:
    """16-hex-char content hash of `engine`'s dependency file set.

    `consumer` names the tool whose module closure was derived (e.g.
    'dmc_family_batch'); the closure is per-(engine, consumer), NOT per-engine
    — measured 2026-08-22, the DMC batch worker loads 55 repo modules while the
    regression harness's verify_member path loads 57 and includes
    pipelines/dmc/verify.py, which the batch never touches. Omit it to use the
    declared fallback.
    """
    roots, _prov = resolve_roots(engine, consumer)
    return _hash_roots(roots)


def fingerprint_components(engine: str, consumer: str | None = None) -> dict:
    """Per-root component hashes + provenance, for recording in a result row.

    Debian's `.buildinfo` idea: when a key is later found to have
    under-approximated, the components identify WHICH rows are suspect instead
    of invalidating a whole family at once.
    """
    roots, prov = resolve_roots(engine, consumer)
    return {
        'epoch': EPOCH,
        'provenance': prov,
        'roots': {rel: _hash_roots([rel]) for rel in roots},
    }


def repo_modules_loaded() -> set[str]:
    """Repo-relative paths of every currently-imported module inside the repo.

    The measurement behind the derived dependency set: after a real build +
    verify, `sys.modules` holds exactly what the work actually needed —
    including function-local imports a static walk cannot see.
    """
    import sys
    out = set()
    for m in list(sys.modules.values()):
        f = getattr(m, '__file__', None)
        if not f:
            continue
        p = Path(f)
        # A module whose __file__ is not a real path ('<stdin>', a frozen or
        # namespace module) resolves against the CWD and lands inside ROOT,
        # which would report a phantom dependency.
        if not p.exists():
            continue
        try:
            rel = p.resolve().relative_to(ROOT)
        except ValueError:
            continue
        if '__pycache__' in rel.parts:
            continue
        out.add(rel.as_posix())
    return out


def check_derived_closure(engine: str, consumer: str) -> list[str]:
    """Repo modules loaded but ABSENT from the stored derived set.

    A batch calls this after its first member: a non-empty result means the
    derived set under-approximates and every row stamped under it is suspect.
    Returns [] when no derived set exists (the declared fallback is in force,
    which is over-broad and therefore safe).
    """
    d = _derived().get(engine, {})
    if consumer not in d:
        return []
    stored = set(d[consumer])
    covered = set(_KEY_MANAGEMENT)      # imported to COMPUTE the key, and
                                        # deliberately unhashed — it would
                                        # otherwise be reported as an escapee
                                        # by every single batch.
    for rel in stored | set(_ALWAYS):
        p = ROOT / rel
        for f in _iter_files(p):
            covered.add(f.relative_to(ROOT).as_posix())
    return sorted(repo_modules_loaded() - covered)
