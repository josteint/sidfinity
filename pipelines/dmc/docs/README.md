# pipelines/dmc/docs — index

DMC (Demo Music Creator) by Brian/Graffity, 10,774 SIDs in HVSC #85 (largest
single player). Research gathered across multiple waves; per-file provenance
headers inside each doc, full URL log in `provenance_log.md`.

## ⚠ Read this first: `V4/V5/V6` and `family-N` are TWO DIFFERENT NAMINGS

They are orthogonal, and confusing them is the single most common way to
misread anything in this tree:

* **`V4` / `V5` / `V6` are REAL** — actual Demo Music Creator editor releases,
  identified by sidid signatures (`DMC_V4.x`, `DMC_V5.x`, `DMC_V6.x`).
* **`family-N` is OURS** — a cluster id from the 2026-06-12 opcode-skeleton
  census in `fingerprint_census.md` (10,676 SIDs → 134 clusters at Jaccard
  ≥ 0.85), **numbered by size**. Nothing in DMC calls them that. It belongs in
  RE notes; it is never a routing concept.

| family | identity | pipeline |
|---|---|---|
| 1 | V4 canonical | `v4` |
| 2 | V4-derived (re-laid-out tables + its own sector encoding) | `v4` — same composer |
| 3 | V5, dominant player | `v5` |
| 4 | V5, distinct branch (Jupiter41) | `v5` — same composer, 14 knobs |
| 5 | V5, sibling of family-3 (0.832, just under the merge threshold) | `v5` |
| 6 | V6 — a genuinely different player | `v6` (RE done, not migrated) |
| 7-134 | ≤10 members each; hacks/customs | mostly unclaimed |

**A pipeline is a COMPOSER, not a bucket** (the Principle §8 / ledger C35
boundary: "more than one COMPOSER", not "more than one engine"). That is why
family-2 and family-4 are not pipelines — they are variants inside one.
There is deliberately no `vX`: an unclaimed member has no composer, so there
would be nothing to put in the directory.

**Which pipeline owns a given SID is answered by `pipelines/dmc/route.py`,
never by a stored list** (ledger C13 — dispatch on the signature). Its
`roster.json` accounts for every DMC member in exactly one bucket; run
`python3 pipelines/dmc/route.py --summary` to read it.

## One FILE, several engine families

A single `.sid` can pack players from DIFFERENT families behind a per-subtune
dispatch wrapper (ledger C31). Three exist in DMC, and the pattern is a
Bayliss habit — `Bayliss/Freespace_2075` packs one DMC player and TWO
Music_Assembler players; `Bayliss/Super_Tau-Zeta` and `The_Syndrom/Black_It`
each pack DMC v4 beside v5. All three are FULL.

They split into two sub-cases, and the line between them is **how many
COMPOSERS are needed** — the Principle §8 / C35 boundary, not "how many
engines are in the file":

* **One composer suffices → unified merge, no tagging.** DMC + `dmc_sfx` is
  this: `extract_heterogeneous` merges the DMC players and lifts the sfx
  player to a typed `SfxEngine`, and the DMC composer emits both behind a
  per-subtune dispatcher. Nothing in the USF names an engine.
* **Genuinely needs two composers → `origin_engine` (C35).** DMC + MA, and
  DMC v4 + v5, are this. Each packed player is extracted by ITS OWN family's
  extractor; the result is ONE `.usf` carrying every player, with
  `MusicSubtune.origin_engine` naming which composer builds each subtune, and
  `music_assembler/heterogeneous.build_from_usf` dispatching on it.
  `src/usf/validate.py` enforces the scaffold's constraints (all-or-nothing,
  ≥2 distinct values), and Move 1 deletes it.

For the roster this means **owner ≠ content**: all three are owned by `v4`
(v4's compilation machinery drives detection and the merge), and the
`build_path` recorded beside them — `hetero_masm` / `hetero_v5` — is what
makes the other families' content visible. Owner alone would hide it.

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
