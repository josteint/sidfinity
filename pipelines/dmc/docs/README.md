# pipelines/dmc/docs — index

DMC (Demo Music Creator) by Brian/Graffity, ~10,660 SIDs in HVSC (largest
single player). Research gathered across multiple waves; per-file provenance
headers inside each doc, full URL log in `provenance_log.md`.

| File | What |
|---|---|
| `research.md` | Wave-1 synthesis: versions, memory layout, instrument/sector/track formats, sidid signatures. |
| `fingerprint_census.md` | **The version census** (2026-06-12): 10,676 SIDs -> 134 families; V4 canonical = 5401 (50.6%), V4-derived = 2889, V5 line = 2181, V6 = 15. Migration target = V4 canonical. |
| `dmc4_player_embedded_1000.bin` + `dmc4editor_embedded_player_notes.md` | **The canonical V4 player binary** (load $1000, "player by brian of graffity 91"), carved from DMC 4 Editor 1.1 (Logan/Slackers, code by Brian) at exe offset 0x7F300. Seed for our own annotated disassembly — no community disassembly exists anywhere public. |
| `dmc4_editor_2025.md` | DMC 4 Editor 1.0/1.1 (2025): ReadMe verbatim, binary string analysis, CSDb + Lemon64 context. Closed source; embeds libsidplayfp. |
| `dmc_sector_commands.md` | Sector command byte synthesis ($C0-$DF/$E0-$FF hole work) from V4/V7 editor command sets + V5 docs. |
| `dmc_v5_docs_original.txt` | Original DMC 5.0 manual (The Syndrom/Crest+TIA noter text, ASCII rip) — the only first-party V5 documentation. |
| `dmc_v5_format_notes.md` | V5 format synthesis: 8-byte instrument, 2-byte tables, $4000 anchor. |
| `tnd_dmc_tutorial.txt` | TND64 "music scene" tutorial full text (DMC 4/7 + DMC 5 chapters; editor-level command semantics, FX flag examples). Live mirror: tnd64.dreamhosters.com. |
| `csdb_dmc_tools_survey.md` | CSDb inventory of every DMC tool release (relocators, packers, depacker, scanner, standalone players, speed hacks) + V7.0 heritage comments + HVMEC version list + FUNET/zimmers mirror contents. |
| `github_parser_survey_negative.md` | Verified negatives: SF2 / DeepSID / CheeseCutter / libsidplayfp / sidid / player-id / realdmx do NOT parse DMC. |
| `provenance_log.md` | Every URL attempted, per wave. |

Binary leads (gitignored): `tmp/dmc_hunt/` — V5 editor + packer + **depacker**
(depacker = packed-format knowledge), V5 scanner, standalone players
(V4.01+ by Xlcus, 5.1 by Onslaught), TND editors disk (V2.1/V4.0/V5.0/V5.0+/
V7.0 + docs noters), CreaMD v5.0+ toolkit d64, DMC 4 Editor win64.
