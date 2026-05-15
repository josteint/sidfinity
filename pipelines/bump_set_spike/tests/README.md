# Tests

Pytest smoke tests for the Bump Set Spike extract path: scaffold-level
shape checks (freq table base, voice count, both subtunes extractable,
hardcoded PWM bounds match the disassembly). From the repo root:

```bash
PYTHONPATH=tools/py_test_lib:src:tools/py65_lib python -m pytest pipelines/bump_set_spike/tests/
```

These tests do NOT verify musical correctness — see the top-level
README in the pipeline for the current Grade F status.

pytest + mypy live in-tree (`tools/py_test_lib/`, gitignored). If missing:

```bash
pip install --target=tools/py_test_lib pytest mypy
```

For codegen invariants (compile-time theorems), see `../codegen/BumpSetSpike/Properties.lean` — Lake runs those automatically on build.
