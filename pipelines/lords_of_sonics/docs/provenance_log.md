# Provenance log — LordsOfSonics/MS research sweep (2026-06-16)

Every source attempted, with status. Future waves: don't re-fetch these.

## Fetched successfully
| URL / source | status | yielded |
|---|---|---|
| github.com/cadaver/sidid (sidid.cfg) | OK | LordsOfSonics/MS 2-line play sig + (Parsec) init sub-variant; full X-Ample blocks (→ `src/sidid_signatures.txt`) |
| github.com/WilfredC64/player-id (config/sidid.cfg) | OK | identical signatures (Rust reimpl) |
| github.com/Chordian/sidfactory2 | OK | no Parsec/LOS importer |
| github.com/JohanPeeters/DeepSID | OK | uses sidid; no LOS-specific handling |
| local: hvsc85/MUSICIANS/**/*.sid (123 LordsOfSonics/MS) | OK | PSID-header survey, 5 dispatch-variant clusters, engine-header bytes, load-addr spread |
| local: hvsc85/DOCUMENTS/ (STIL, Musicians) | OK | group bio, composer notes, "new sound player" quote |
| remix64.com/interviews/interview-markus-schneider.html | OK | driver origin (1988, ~2 months), Compotech optimisation by Kozielek/van Zeist |
| vgmpf.com/Wiki — Markus_Schneider | OK | Parsec→Compotech lineage, game credits |
| csdb.dk/group/?id=757 (Lords of Sonics) | OK | founded 1988; 7 releases listed |
| csdb.dk/scener/?id=6003 (Schneider) / ?id=2205 (Blidon) | OK | scener bios |
| csdb.dk/release/?id=10744 (Parsec Music Editor V5.1) | OK | **public editor D64** — Mnemonic Designs 1989; code MS+Nic+ADT |
| csdb.dk/release/?id=122614 (Compotech V2.1) | OK | X-Ample Architectures 1995; .d64 |

## Attempted but failed / blocked
| URL / source | status |
|---|---|
| Wayback Machine (web.archive.org) | mostly blocked by fetch tool |
| csdb.dk (some pages) | intermittent HTTP 503 — retry on direct IDs |
| Several agents (CSDb/Pouet, Archive, Forums, HVSC-headers) | hit session-token limit mid-run, but all had written their docs file (with closing Leads section) before cutoff — verified intact |
| Disasm/tech-articles cluster | died before writing on first attempt; **re-run successfully** (disasm_findings.md, 438 lines) — recovered the embedded version-history block + "Docs 2 Compotech" lead |

## Confirmed NOT FOUND
- No open-source parser/decompiler/importer for the LordsOfSonics/Parsec format
  (SIDFactory II, libsidplayfp, CheeseCutter, realdmx/c64_6581_sid_players,
  SIDdecompiler, DeepSID).
- No published annotated disassembly of the player.

## CSDb #253740 "Docs 2 Compotech" — DOWNLOADED + CHECKED (2026-06-16)
Both disk images fetched via csdb.dk/storage redirect and saved to `src/`
(`d2ct.d64`, `Compotech The Force full release.d64`). Directory parsed + the
docs PRG text decoded in pure Python. **Result: dead end for a format spec** —
the "docs" PRG is a scene greetings/credits scroller, not a manual; the
companion disk holds the Compotech editor/player but Compotech = the separate
`xample` family. Full write-up: `src/compotech_disks_NOTES.md`.

## Key not-yet-executed lead (belongs to migration phase, not this sweep)
- **Download Parsec Music Editor V5.1 D64 (CSDb #10744)** and disassemble its player
  stub + read its data layout → authoritative format spec for THIS family.
  Disassembling a player is RE (out of GATHER scope here), deferred to migration.

## Notes
- X-Ample / Compotech is a SEPARATE sidid family (`xample`, already OK). Material on it
  here is lineage context for the LOS→Parsec→Compotech evolution, not LOS format itself.
- Raw fetches retained under `tmp/lords_of_sonics_research/` (gitignored scratch).
