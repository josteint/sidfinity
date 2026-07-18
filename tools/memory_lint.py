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

    lint_ledger(errors, warnings)
    lint_usf_spec(errors, warnings)

    for e in errors:
        print(f"ERROR   {e}")
    for w in warnings:
        print(f"warning {w}")
    n = len(files)
    print(f"memory_lint: {n} files, {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


def lint_ledger(errors: list[str], warnings: list[str]) -> None:
    """Convergence-ledger two-layer consistency (docs/the_convergence_ledger.md
    = recognition layer; docs/ledger/C<n>.md = full entries)."""
    main = REPO / "docs" / "the_convergence_ledger.md"
    entry_dir = REPO / "docs" / "ledger"
    if not main.exists() or not entry_dir.is_dir():
        errors.append("L0 ledger: main file or docs/ledger/ missing")
        return
    text = main.read_text()
    card_ids = set(re.findall(r"^### C(\d+) ", text, re.M))
    index_ids = set(re.findall(r"\| C(\d+) \|", text))
    file_ids = {re.match(r"C(\d+)$", p.stem).group(1)
                for p in entry_dir.glob("C*.md")
                if re.match(r"C(\d+)$", p.stem)}
    for i in sorted(card_ids - file_ids, key=int):
        errors.append(f"L1 ledger: card C{i} has no entry file docs/ledger/C{i}.md")
    for i in sorted(file_ids - card_ids, key=int):
        errors.append(f"L2 ledger: entry file C{i}.md has no recognition card")
    for i in sorted(index_ids - card_ids, key=int):
        errors.append(f"L3 ledger: index row references C{i} but no card exists")
    for i in sorted(card_ids - index_ids, key=int):
        warnings.append(f"L4 ledger: card C{i} has no index row (keywords help recognition)")
    for i in sorted(card_ids & file_ids, key=int):
        card = re.search(rf"^### C{i} .*?(?=^### C\d+ |\Z)", text, re.M | re.S).group(0)
        if f"ledger/C{i}.md" not in card:
            warnings.append(f"L5 ledger: card C{i} lacks its FULL ENTRY pointer")
        head = re.match(r"### C\d+ [^\n]*", (entry_dir / f"C{i}.md").read_text())
        if not head:
            errors.append(f"L6 ledger: entry file C{i}.md does not start with its heading")
    print(f"ledger_lint: {len(card_ids)} cards, {len(file_ids)} entry files checked")


def lint_usf_spec(errors: list[str], warnings: list[str]) -> None:
    """Anti-fiction check: docs/usf_format.md must never present a format
    token (`name:` / `name {` / `name=`) the grammar doesn't define. The
    doc is the contract-and-rationale layer; src/usf/grammar.lark is the
    normative block-by-block reference (asymmetric merge, 2026-07-18)."""
    doc_p = REPO / "docs" / "usf_format.md"
    gram_p = REPO / "src" / "usf" / "grammar.lark"
    if not doc_p.exists() or not gram_p.exists():
        errors.append("U0 usf spec or grammar missing")
        return
    doc = doc_p.read_text()
    gram = gram_p.read_text()
    # skip the sections that talk about tokens which deliberately DON'T exist
    doc = doc.split("## Things the format deliberately does NOT have")[0]
    doc = re.sub(r"## No `version:`.*?(?=\n## )", "", doc, flags=re.S)
    vocab = set(re.findall(r'"([a-z_][a-z0-9_]*)"', gram))
    vocab |= set(re.findall(r"^([a-z_][a-z0-9_]*):", gram, re.M))
    n = 0
    neg = re.compile(r"\bNo\b|\bnot\b|\bnever\b|gone|deliberately", re.I)
    for line in doc.splitlines():
        if neg.search(line):
            continue
        for snippet in re.findall(r"`([^`]+)`", line):
            # a snippet PRESENTED AS SYNTAX: `name:` `name=` `name { ... }`
            m = re.fullmatch(r"([a-z_][a-z0-9_]*)(?:\s+N)?\s*(?::|=|\{.*)", snippet)
            if not m:
                continue
            n += 1
            tok = m.group(1)
            if tok not in vocab:
                errors.append(f"U1 usf_format.md presents `{tok}` as a format "
                              f"token but the grammar does not define it")
    print(f"usf_spec_lint: {n} format tokens checked against the grammar")


if __name__ == "__main__":
    sys.exit(main())
