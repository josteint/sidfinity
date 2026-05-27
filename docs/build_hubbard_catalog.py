"""Build a chronological catalog of all Hubbard SIDs.

For each SID:
  - relative path
  - title (PSID header name field)
  - released field (year + publisher)
  - engine type (via sidid, plus rh_decompile probe for the classic early engine)
"""
import os
import re
import subprocess
import sys

sys.path.insert(0, 'src')
sys.path.insert(0, 'tools/py65_lib')

ROOT = '/home/jtr/sidfinity'
SCAN_ROOT = os.path.join(ROOT, 'hvsc84/MUSICIANS')
SIDID = os.path.join(ROOT, 'tools/sidid')
SIDID_CFG = os.path.join(ROOT, 'tools/sidid.cfg')


def parse_psid(path: str) -> dict:
    with open(path, 'rb') as f:
        hdr = f.read(0x7C)
    def s(o):
        return hdr[o:o+32].split(b'\x00')[0].decode('latin1', 'replace')
    return {
        'title':    s(0x16),
        'author':   s(0x36),
        'released': s(0x56),
    }


def parse_year(released: str) -> int | None:
    """Extract leading 4-digit year, e.g. '1985 Gremlin Graphics' → 1985."""
    m = re.match(r'^\s*(\d{4})', released)
    return int(m.group(1)) if m else None


def find_hubbard_sids() -> list[str]:
    paths = []
    for root, _dirs, files in os.walk(SCAN_ROOT):
        for f in files:
            if not f.endswith('.sid'):
                continue
            p = os.path.join(root, f)
            meta = parse_psid(p)
            if 'Hubbard' in meta['author'] or 'hubbard' in meta['author'].lower():
                paths.append(p)
    return paths


def sidid_classify(paths: list[str]) -> dict[str, str]:
    """Run sidid in batch mode on each containing dir; map basename → engine."""
    classes: dict[str, str] = {}
    # Group by directory for efficient sidid invocation
    by_dir: dict[str, list[str]] = {}
    for p in paths:
        by_dir.setdefault(os.path.dirname(p), []).append(p)
    for d, ps in by_dir.items():
        out = subprocess.run([SIDID, f'-c{SIDID_CFG}', '-d', d],
                              capture_output=True, text=True).stdout
        for line in out.splitlines():
            line = line.rstrip()
            if not line or ':' in line or line.startswith('Using'):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].endswith('.sid'):
                classes[os.path.join(d, parts[0])] = parts[-1]
    return classes


def is_classic_hubbard(path: str) -> bool:
    """Probe rh_decompile to see if this SID uses the classic early engine."""
    try:
        from rh_decompile import decompile
    except Exception:
        return False
    try:
        d = decompile(path)
        return d is not None and len(d.instruments) > 0
    except Exception:
        return False


def relpath(p: str) -> str:
    return os.path.relpath(p, ROOT)


def main() -> None:
    paths = find_hubbard_sids()
    classes = sidid_classify(paths)
    rows = []
    for p in paths:
        meta = parse_psid(p)
        year = parse_year(meta['released'])
        engine = classes.get(p, '?')
        if engine == 'Rob_Hubbard' and is_classic_hubbard(p):
            engine = 'Rob_Hubbard (early/classic)'
        elif engine == 'Rob_Hubbard':
            engine = 'Rob_Hubbard (variant)'
        rows.append({
            'year': year, 'title': meta['title'], 'released': meta['released'],
            'author': meta['author'], 'engine': engine, 'path': relpath(p),
        })
    # Sort: year asc, title asc; unknown year goes last
    rows.sort(key=lambda r: (r['year'] is None, r['year'] or 0, r['title']))
    # Dump as TSV; the consumer renders Markdown
    print('year\ttitle\tengine\tauthor\treleased\tpath')
    for r in rows:
        print(f"{r['year'] or '?'}\t{r['title']}\t{r['engine']}\t{r['author']}\t{r['released']}\t{r['path']}")


if __name__ == '__main__':
    main()
