---
source_url: https://github.com/libsidplayfp/libsidplayfp/search?q=companion
fetched_via: WebFetch
fetch_date: 2026-05-25
author: libsidplayfp maintainers
content_date: ongoing
reliability: primary (zero-result code search)
---

# libsidplayfp has NO Companion-specific code

GitHub repo code search `repo:libsidplayfp/libsidplayfp companion` returned
**0 matches**. This is expected: libsidplayfp is a chip-and-CPU emulator
(reSID + MOS6502), not a format-aware player. It executes whatever 6502 code
the SID file ships; it has no per-engine awareness for any player (Hubbard,
Galway, JCH, DMC, GT, Companion, …).

Practical consequence for our migration: libsidplayfp is the verification
oracle (via `--writelog`, per project convention), not a source of format
knowledge. The Companion-specific work must be done elsewhere.
