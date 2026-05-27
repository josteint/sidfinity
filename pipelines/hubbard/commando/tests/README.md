# Tests

Pytest smoke tests for the Commando extract path: instrument count, dataclass
shape, error handling. From the repo root:

```bash
PYTHONPATH=tools/py_test_lib python -m pytest pipelines/hubbard/commando/tests/
```

pytest + mypy live in-tree (`tools/py_test_lib/`, gitignored). If missing:

```bash
pip install --target=tools/py_test_lib pytest mypy
```

For codegen invariants (compile-time theorems), see `../codegen/Commando/Properties.lean` — Lake runs those automatically on build.
