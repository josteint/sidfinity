#!/usr/bin/env python3
"""Mechanical hygiene lint for .claude/memory/ — catches the rot classes the
2026-07-16 memory audit found by hand. Fast (<1 s); run before committing any
memory change (CLAUDE.md "Memory hygiene").

Checks (ERRORS, exit 1):
  E1  every active memory file is linked from MEMORY.md exactly once
  E2  every MEMORY.md link points at an existing file
  E3  every [[wiki-link]] resolves (file basename or frontmatter `name:`)
  E4  every cited repo path exists (unless the line marks it historical)

Checks (WARNINGS, exit 0):
  W1  live-status markers (RUNNING / IN PROGRESS / NEXT: / RESUME) in files
      not git-touched for STALE_DAYS — status frozen at write-time
  W2  frontmatter `description:` carrying live-status markers — descriptions
      must be timeless (status belongs in MEMORY.md + the body head)
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MEM = REPO / ".claude" / "memory"
STALE_DAYS = 30

# A cited path on a line with one of these words is a deliberate historical
# reference (today's supersession notes), not rot.
HISTORICAL = re.compile(
    r"gone|deleted|dissolved|archived|superseded|deprecated|removed|"
    r"old layout|no longer|was |pre-USF|GT2-era|renamed",
    re.I,
)
PATH_RE = re.compile(
    r"\b((?:pipelines|tools|src|docs)/[A-Za-z0-9_./-]+\.(?:py|md|s|asm|json|lark|cpp|sh))\b"
)
STATUS_RE = re.compile(r"\bRUNNING\b|IN PROGRESS|\bNEXT:|\bRESUME\b|\bTODO:")


def active_files() -> list[Path]:
    return sorted(p for p in MEM.glob("*.md") if p.name != "MEMORY.md")


def frontmatter_field(text: str, field: str) -> str:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return ""
    fm = m.group(1)
    f = re.search(rf"^{field}:\s*(.*)$", fm, re.M)
    return f.group(1).strip().strip('"') if f else ""


def git_age_days(path: Path) -> float:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", str(path)],
            cwd=REPO, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if not out:
            return 0.0  # untracked = new = not stale
        return (time.time() - int(out)) / 86400
    except subprocess.CalledProcessError:
        return 0.0


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    index = (MEM / "MEMORY.md").read_text()
    files = active_files()
    names = {p.name for p in files}

    # Resolvable [[wiki-link]] targets: basenames (sans .md) + frontmatter names.
    link_targets = {p.stem for p in files}
    texts: dict[Path, str] = {}
    for p in files:
        texts[p] = p.read_text()
        n = frontmatter_field(texts[p], "name")
        if n:
            link_targets.add(n)

    # E1 / duplicate index links
    index_links = re.findall(r"\(([a-z_0-9-]+\.md)\)", index)
    for p in files:
        c = index_links.count(p.name)
        if c == 0:
            errors.append(f"E1 {p.name}: not linked from MEMORY.md")
        elif c > 1:
            errors.append(f"E1 {p.name}: linked {c}x from MEMORY.md (duplicate)")

    # E2 dead index links
    for link in set(index_links):
        if link not in names:
            errors.append(f"E2 MEMORY.md: link to missing file {link}")

    # E3 dead wiki-links, E4 dead paths, W1/W2 per file
    for p, text in texts.items():
        for wl in set(re.findall(r"\[\[([a-z_0-9-]+)\]\]", text)):
            if wl not in link_targets:
                errors.append(f"E3 {p.name}: dead wiki-link [[{wl}]]")
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            for m in PATH_RE.finditer(line):
                path = m.group(1)
                if (REPO / path).exists():
                    continue
                # historical marker may sit on a neighboring (wrapped) line
                window = "\n".join(lines[max(0, i - 2): i + 1])
                if not HISTORICAL.search(window):
                    errors.append(f"E4 {p.name}:{i}: cited path missing: {path}")

        desc = frontmatter_field(text, "description")
        if STATUS_RE.search(desc):
            warnings.append(
                f"W2 {p.name}: description carries live status "
                f"({STATUS_RE.search(desc).group(0).strip()!r}) — make it timeless"
            )
        body = re.sub(r"^---\n.*?\n---", "", text, count=1, flags=re.S)
        hits = sorted({m.group(0).strip() for m in STATUS_RE.finditer(body)})
        if hits and git_age_days(p) > STALE_DAYS:
            warnings.append(
                f"W1 {p.name}: live-status markers {hits} but file untouched "
                f"for >{STALE_DAYS} days — verify still true"
            )

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"warning {w}")
    n = len(files)
    print(f"memory_lint: {n} files, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
