#!/usr/bin/env python3
"""composer_param_lint — the composers' params-surface gate.

Every `params.fields` key a COMPOSER consumes is a REPRESENTATION decision:
it either carries MUSIC (the model can learn it) or reproduces a MECHANISM
the write stream demands — and the difference is exactly the principle's
section-8 line. This tool makes that review MECHANICAL (the usf_spec_lint
lesson: a declared principle without a mechanical check eventually drifts):

  * scans each registered composer file for string-literal keys reaching
    `params.fields.get('k')` / `params.fields['k']`;
  * ERRORS on any consumed key absent from tools/composer_params.json —
    adding a composer param forces registering it with a category
    (musical-content / mechanism-knob / temporal-dispatch / environment)
    and the ledger entry / canon section that licenses it;
  * WARNS on registry entries no longer consumed (stale rows).

Run beside usf_corpus_check + usf_spec_lint after any composer change that
touches the params surface. Born 2026-08-12 after a driver-mechanism param
(`pulsebyte_anim`) reached a verified build before the C19 33rd-occurrence
test ("does the wedge change a MUSICAL VALUE? -> deconstruct") was applied;
the reviewed registry asks that question at build time, not in review.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REGISTRY = os.path.join(ROOT, 'tools', 'composer_params.json')

_KEY_RE = re.compile(
    r"params\.fields(?:\.get\(|\[)\s*'([a-z0-9_]+)'")
# typed-field readers with a params-fields FALLBACK (the DMC `_artic`
# helper): the params key is the SECOND argument — invisible to the direct
# pattern above (found 2026-08-13 when vib_ramp_persist's fallback slipped
# past the first regex).
_ARTIC_RE = re.compile(r"_artic\(\s*'[a-z0-9_]+',\s*'([a-z0-9_]+)'")
# per-SUBTUNE params reads (the _Model.subtunes dicts carry
# MusicSubtune.params as sub['params']): `sub['params'].get('k')` /
# `sub['params']['k']` — a C31 per-subtune override key is as much a
# consumed composer param as a file-level one (found 2026-08-20 when
# idle_pulse_instr's only read took this form).
_SUBP_RE = re.compile(r"\['params'\](?:\.get\(|\[)\s*'([a-z0-9_]+)'")

# MODEL-MEDIATED PARAMS — the blind spot this lint had until 2026-08-23.
#
# A composer need not read `params.fields` at all: DMC v5's `from_usf` layer
# reads the keys, stores them as MODEL attributes, and the composer branches on
# `m.family4` / `m.play_phases`. Every regex above sees literal keys in the
# COMPOSER file, so v5's entire params surface was invisible — the lint
# reported "clean" while three of its four keys (`family4`, `f4_filtmode`,
# `f4_fcinit`) were registered nowhere at all. A gate that cannot see a
# consumer is not a gate for it.
#
# Cure: scan the READER too and attribute its keys to the composer they feed.
# The binding is explicit rather than inferred from directory layout, so a new
# arrangement has to be declared instead of silently escaping again.
_MODEL_MEDIATED = {
    'pipelines/dmc/v5/composer_v5.py': ['pipelines/dmc/v5/from_usf.py'],
}


def _reader_keys(src: str) -> set:
    """Params keys read in a from_usf-style layer.

    Finds whatever local name is bound to `usf.params.fields` (v5 calls it
    `pf`) and collects the literal keys taken off it — precise, so an
    unrelated `.get('x')` on some other dict cannot masquerade as a param.
    """
    keys = set()
    for var in set(re.findall(r"(\w+)\s*=\s*usf\.params\.fields", src)):
        keys |= set(re.findall(
            rf"\b{re.escape(var)}(?:\.get\(|\[)\s*'([a-z0-9_]+)'", src))
    return keys


def main() -> int:
    reg = json.load(open(REGISTRY))
    reg_files = {f: set(keys) for f, keys in reg.items()
                 if not f.startswith('_')}
    errors, warnings = [], []
    consumed = {}
    for relf in reg_files:
        path = os.path.join(ROOT, relf)
        if not os.path.exists(path):
            errors.append(f'registered composer file missing: {relf}')
            continue
        _src = open(path).read()
        consumed[relf] = set(_KEY_RE.findall(_src)) | \
            set(_ARTIC_RE.findall(_src)) | set(_SUBP_RE.findall(_src))
        for _rd in _MODEL_MEDIATED.get(relf, ()):
            _rp = os.path.join(ROOT, _rd)
            if os.path.exists(_rp):
                consumed[relf] |= _reader_keys(open(_rp).read())
    # composer files with a params surface that are NOT registered at all
    for relf in ('pipelines/dmc/composer_asm.py',
                 'pipelines/dmc/v5/composer_v5.py',
                 'pipelines/dmc/sfx_composer.py',
                 'pipelines/future_composer/composer_asm.py',
                 'pipelines/music_assembler/composer_asm.py',
                 'pipelines/composer.py',
                 'pipelines/goattracker/v1/composer_asm.py'):
        path = os.path.join(ROOT, relf)
        if not os.path.exists(path) or relf in reg_files:
            continue
        found = set(_KEY_RE.findall(open(path).read()))
        for _rd in _MODEL_MEDIATED.get(relf, ()):
            _rp = os.path.join(ROOT, _rd)
            if os.path.exists(_rp):
                found |= _reader_keys(open(_rp).read())
        if found:
            errors.append(
                f'{relf} consumes params keys but has no registry section: '
                + ', '.join(sorted(found)))
    for relf, keys in consumed.items():
        for k in sorted(keys - reg_files[relf]):
            errors.append(
                f'{relf}: UNREGISTERED composer param {k!r} — add it to '
                f'tools/composer_params.json with a category and the ledger '
                f'entry that licenses it (music or mechanism? C19-33rd test)')
        for k in sorted(reg_files[relf] - keys):
            warnings.append(f'{relf}: registry key {k!r} no longer consumed '
                            f'(stale row — delete or re-home it)')
    n_keys = sum(len(v) for v in consumed.values())
    print(f'composer_param_lint: {len(consumed)} composer file(s), '
          f'{n_keys} consumed key(s) checked against the registry')
    for w in warnings:
        print(f'  WARNING: {w}')
    for e in errors:
        print(f'  ERROR: {e}')
    if not errors and not warnings:
        print('  clean')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())
