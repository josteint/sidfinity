# Provenance log — Vibrants/JO research sweep (2026-06-16)

Every source attempted, with status. Future waves: don't re-fetch these.

## Fetched successfully
| URL / source | status | yielded |
|---|---|---|
| github.com/cadaver/sidid (sidid.cfg, sidid.nfo) | OK | 10 Vibrants/JO signatures (→ `src/sidid_vibrants_jo_signatures.txt`); nfo stub (AUTHOR-only) |
| github.com/WilfredC64/player-id (sidid.cfg) | OK | confirms cadaver signatures |
| local: hvsc84/MUSICIANS/J/JO/*.sid + H/HJE/*.sid | OK | PSID-header survey, code-size band, V22 version string, layout map |
| local: hvsc84/MUSICIANS/J/JO/Multi_Move.usf | OK | full USF analysis (prior partial migration) |
| local: hvsc84/DOCUMENTS/ (STIL, Musicians, etc.) | OK | bio + STIL excerpts |
| csdb.dk/scener/?id=1926 (JO) | OK (wave 2; 503 in wave 1) | one coder credit (Music Demo #001, 1989); no tool release |
| csdb.dk/scener/?id=2273 (HJE) | OK | HJE identity, ex-Esonix, Amok 1990–91 |
| demozoo.org/sceners/6764/ (JO) | OK | group/career history |
| github.com/realdmx/c64_6581_sid_players | OK | no Vibrants/JO entry |
| chordian.net / blog.chordian.net | OK | JO→JCH hard-restart provenance; JO assembler-only workflow |

## Attempted but failed / blocked
| URL / source | status |
|---|---|
| csdb.dk (most pages, wave 1) | HTTP 503 (recovered in wave 2) |
| csdb.dk search (short names: amok/vibrants/jesper olsen) | returns 0 results — broken for common terms; use direct IDs |
| www.vibrants.dk / vibrants.dk/jo.htm | timeout / unreachable; Wayback not reachable via fetch tool |
| deepsid.chordian.net per-file metadata | JS-rendered, not scrapable |
| codebase64.org music_players page | empty/JS-rendered |
| Wayback Machine (web.archive.org) | blocked by fetch tool throughout |

## Confirmed NON-EXISTENT (searched, not found anywhere)
- JO player source code, format spec, annotated disassembly, GUI editor —
  none on CSDb, GitHub, Archive.org, Codebase64, Lemon64, Usenet, or scene mags.
- No CSDb technical/forum article on the format.

## Notes
- A first agent burst drifted onto **JCH NewPlayer** (different engine, same group).
  Those 4 files (`csdb_research.md`, `forums_research.md`, `archive_research.md`,
  `github_research.md`) were deleted 2026-06-16. Any JCH facts here are incidental
  context for distinguishing the engines, not JO format knowledge.
- Raw fetches retained under `tmp/vibrants_jo_research/` (gitignored scratch).
