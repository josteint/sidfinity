# Tests

Pytest smoke tests for the CrazyComets extract path: instrument count, skydive
detection, PW bound check, error handling. From the repo root:

```bash
PYTHONPATH=tools/py_test_lib python -m pytest pipelines/crazy_comets/tests/
```

pytest + mypy live in-tree (`tools/py_test_lib/`, gitignored). If missing:

```bash
pip install --target=tools/py_test_lib pytest mypy
```

For codegen invariants (compile-time theorems), see `../codegen/CrazyComets/Properties.lean` — Lake runs those automatically on build.
