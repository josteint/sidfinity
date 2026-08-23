#!/usr/bin/env python3
"""PreToolUse guard: WARN (never block) when py65 is about to be used, steering
toward siddump native-capture for any GROUND-TRUTH observation.

py65 is load-bearing infrastructure here — ~50 extract `engine_model.py` /
`dataflow.py` / `factory.py` files run it as an IDEALIZED SIMULATION to read
bytes the file image loaded or the member's own init wrote. That use is
sanctioned. What is NOT sanctioned is py65 as GROUND TRUTH for an observation /
measurement that feeds the SID write stream or the verdict ("what does init
write?", "what value does a played read produce?", which addresses a routine
touches) — py65's power-on fill / null-pointer playback diverge from
libsidplayfp, so a py65-measured value that reaches the write stream is wrong
(feedback_ground_truth, third failure mode; DMC Roots + Mega_Mix). Those go
through siddump native-capture: --pc-watch / --reinit-snapshot /
--memwatch-on-write / --peek-post-init.

No syntactic check can separate extraction from observation (same MPU class), so
this is a non-blocking nudge: it fires on the SMELL (an inline `from py65` /
`import py65` in a Bash heredoc/-c, or a Write introducing py65) and lets the
tool proceed. Committed code that merely runs a py65-importing tool
(`python3 pipelines/dmc/family_batch.py`) carries no inline import, so it never
fires — no alarm fatigue.

Reads the PreToolUse hook JSON on stdin; emits `additionalContext` when matched.
"""
import json
import re
import sys

WARN = (
    "py65 detected. py65 is ONLY sanctioned for IDEALIZED EXTRACTION sims "
    "(reading bytes the file image loaded or the member's own init wrote — the "
    "extract engine_model / dataflow paths). If this is an OBSERVATION or "
    "MEASUREMENT that feeds the SID write stream or the verdict (\"what does "
    "init write?\", \"what value does a played read produce?\", which addresses "
    "a routine touches), that is FORBIDDEN ground-truth misuse "
    "(feedback_ground_truth, third failure mode) — use siddump native-capture "
    "instead: --pc-watch / --reinit-snapshot / --memwatch-on-write / "
    "--peek-post-init. Proceed ONLY if this is a genuine extraction sim."
)

# `from py65...` / `import py65` — NOT a bare `tools/py65_lib` sys.path entry
# (that only makes the vendored lib importable; the ~50 tools import py65
# transitively via engine_model, which the running command text never shows).
_IMPORT = re.compile(r"(?:from|import)\s+py65")
_PYTHON = re.compile(r"\bpython[0-9.]*\b")


def _matches(tool, ti):
    """True iff this call is EXECUTING/AUTHORING py65 code (not merely mentioning
    it in prose). Bash: an inline import AND a python invocation — so a git
    commit message, grep pattern, or echo that names py65 does not fire, but a
    `python3 - <<EOF ... from py65 ...` heredoc / `python -c` does. Write: an
    import in a `.py` file — so a doc/memory that mentions the import is skipped
    while a scratch/tool script is caught."""
    if tool == "Bash":
        cmd = ti.get("command", "") or ""
        return bool(_IMPORT.search(cmd) and _PYTHON.search(cmd))
    if tool == "Write":
        path = ti.get("file_path", "") or ""
        return path.endswith(".py") and bool(_IMPORT.search(ti.get("content", "") or ""))
    return False


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    if not _matches(data.get("tool_name", ""), data.get("tool_input", {}) or {}):
        return
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": WARN,
        },
        "systemMessage": (
            "py65 usage detected — reminder injected "
            "(use siddump native-capture for observations)."
        ),
    }))


if __name__ == "__main__":
    main()
