# Tests

Pytest smoke tests for the Last V8 (C128) extract path: RSID header,
subtune routing, sample records, relocator window, freq table.

From the repo root:

```bash
PYTHONPATH=tools/py_test_lib tools/py_test_lib/bin/pytest \
    pipelines/last_v8_c128/tests/ -q
```

pytest + mypy live in-tree (`tools/py_test_lib/`, gitignored). If missing:

```bash
pip install --target=tools/py_test_lib pytest mypy
```

For codegen invariants (compile-time theorems), see
`../codegen/LastV8C128/Properties.lean` — Lake runs those automatically
on build.
