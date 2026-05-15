# Tests

Pytest smoke test for the Dragon's Lair Part II extract path. Scaffold
level only — see the README in the parent directory and
`test_extract.py` for what's covered. From the repo root:

```bash
PYTHONPATH=tools/py_test_lib python -m pytest pipelines/dragons_lair_part_ii/tests/
```

pytest + mypy live in-tree (`tools/py_test_lib/`, gitignored). If missing:

```bash
pip install --target=tools/py_test_lib pytest mypy
```

For codegen invariants (compile-time theorems), see
`../codegen/DragonsLairPartIi/Properties.lean` — Lake runs those
automatically on build.
