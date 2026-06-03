---
source_url: https://github.com/libsidplayfp/libsidplayfp
fetched_via: git clone (depth 1)
fetch_date: 2026-06-03
author: libsidplayfp team (Leandro Nini et al.)
content_date: actively maintained
reliability: primary
---

# libsidplayfp — Negative result (no FC-specific handling)

Cloned and grepped `libsidplayfp` for any FutureComposer / MoN /
Hawkeye references in C++ source.

## Result: NONE

```
$ grep -ri "future\|hawkeye\|fc_v\|MoN" libsidplayfp/src --include="*.cpp" --include="*.h"
# (no matches)
```

## Why this is the expected result

`libsidplayfp` is a **chip-level emulator**, not a tracker/format parser.
It only knows about the **PSID/RSID file wrapper** (which is what every
HVSC SID — FC-driven or otherwise — uses as its container).

The `src/sidtune/` directory contains parsers for:
- `PSID.cpp / PSID.h` — PlaySID file format (RSID is a v2 extension)
- `MUS.cpp / MUS.h` — Compute!'s SidPlayer/MUS format
- `p00.cpp / p00.h` — PC64 P00 format
- `prg.cpp / prg.h` — Raw PRG with load address

No tracker-format awareness. The 6502 in the player code is what
"interprets" the FC format at runtime; libsidplayfp just feeds CPU
cycles to the player code and reads the resulting `$D400-$D418` writes.

## What this means for our work

We **cannot** lean on libsidplayfp to identify or parse FC. We need:
1. The driver byte-pattern detection (sidid signatures — see
   `github_sidid_signatures.md`).
2. A handwritten C/Python parser for the FC V3.x in-memory layout
   (built from the realdmx MoN disassemblies + the editor binaries
   from CSDb).

libsidplayfp is still our **ground-truth replay engine** (per the
project's ground-truth rule) — we run our rebuilt SID through
`tools/siddump --writelog` (which is libsidplayfp-based) and
cycle-compare against the original. But it gives zero help on the
format-parsing side.
