"""xa65 invocation — assemble a 6502 source string to raw bytes.

xa65 is the assembler at `tools/xa65/xa/xa`. We invoke it via subprocess
on a tempfile. Concurrent calls are safe because each invocation gets
its own TemporaryDirectory.

Subsumes the four pre-existing _assemble functions in:
  - pipelines/composer.py
  - pipelines/future_composer/composer_asm.py
  - pipelines/companion/jay_derrett/build.py
  - pipelines/companion/c64_music_examples/build.py

Two flags vary across callers:
  - `masm_mode=True` passes `-M` (MASM-compat: ':' may appear in
    comments without being misread as a label). FC + JD need this.
    Hubbard + C64ME don't use ':' in comments and historically pass
    no flag — keep the default off so their behavior is unchanged.
  - `return_labels=True` passes `-l <file>` and parses the resulting
    `name, 0xaddr, 0, 0xext` lines into a dict. Only JD needs this.

Errors raise `RuntimeError` with xa65's stdout+stderr.
"""
from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

_ROOT = str(Path(__file__).resolve().parents[2])
_XA = os.path.join(_ROOT, 'tools', 'xa65', 'xa', 'xa')


def assemble(asm_src: str, *,
             masm_mode: bool = False,
             return_labels: bool = False
             ) -> bytes | tuple[bytes, dict[str, int]]:
    """Run xa65 on `asm_src`, return the assembled raw bytes.

    xa65's default output is the raw byte stream starting at the lowest
    emitted address (no load-address prefix). The asm's `* = $XXXX`
    directive sets the address SYMBOL context only — the file starts at
    the lowest emitted byte. Gaps are zero-padded by xa65.

    With `return_labels=True`, returns (bytes, labels_dict) where the
    dict maps label name → 16-bit address.
    """
    with tempfile.TemporaryDirectory() as td:
        src = os.path.join(td, 'src.s')
        obj = os.path.join(td, 'out.bin')
        lbl = os.path.join(td, 'out.labels')
        with open(src, 'w') as f:
            f.write(asm_src)
        cmd = [_XA]
        if masm_mode:
            cmd.append('-M')
        cmd += [src, '-o', obj]
        if return_labels:
            cmd += ['-l', lbl]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(
                f'xa65 failed (rc={r.returncode}):\n'
                f'stdout: {r.stdout}\nstderr: {r.stderr}')
        with open(obj, 'rb') as f:
            raw = f.read()
        if not return_labels:
            return raw
        labels: dict[str, int] = {}
        if os.path.exists(lbl):
            for line in open(lbl):
                # xa65 label-file format: name, 0xaddr, 0, 0xext
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 2:
                    try:
                        labels[parts[0]] = int(parts[1], 16)
                    except ValueError:
                        pass
        return raw, labels
