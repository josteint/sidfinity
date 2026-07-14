---
name: reference-companion-etymology
description: "\"Companion\" in C64 SID lore = Keith Bowden's type-in driver from *The Companion to the Commodore 64* (Pan Books, 1984). Our `pipelines/companion/` is taxonomically defensible — every SID it contains fingerprints as \"Companion\" in sidid."
metadata: 
  node_type: memory
  type: reference
  originSessionId: ce060f8a-e40f-4b55-9551-2d4fc0bb3028
---

**What "Companion" actually means:** The 3-voice SID music driver published as a type-in listing in Keith Bowden's book *The Companion to the Commodore 64* (Pan Books, April 1984, ISBN 0-330-28479-7). NOT a publisher, a tracker, a musician, or a player tool — a manual type-in from a book.

**Lineage tree.** Bowden's listing was independently extended by several authors who all shared the `STA $D404,X / RTS` waveform-write tail that sidid fingerprints:

- **Rob Hubbard** — Up_up_and_Away (his first SID), Commodore_64_Music_Examples 2-15. Direct extension of the Bowden listing, pre-Monty.
- **Chris Murray** — Henrys_House (English Software, 1984). Independent extension, different freq table.
- **Clever Music team** (Steven Chapman / Jay Derrett / John McPhee) — Fairlight, Gyroscope, Back_to_the_Future (CRL releases 1985-87). Later rewritten further by Derrett into his own aperiodic Jay_Derrett variant.
- **Vic Berry** — SID_Sequencer, Aleatory_Composer programs. Embeds Companion-derived player code in real-time composition tools (the Bowden-canonical strain in our pipeline covers 12 of his SIDs).
- **Karl Hörnell** — Melonmania.
- **David Whittaker** — Yes_Tune, Soldier_of_Fortune. (Per sidid, also fingerprints as Companion.)

**sidid fingerprints** (`deprecated/gt2_pipeline/tools/sidid.cfg`) — all keyed off the `9D 04 D4 60` waveform-write tail:
- `Companion` (base): `BC ?? ?? C8 98 9D 04 D4 60`
- `(Sid_Sequencer)` / `(Aleatory_Composer)`: Vic Berry's tools
- `(Companion/Murray)`: base + Y=$80 wrap / Y=$FF restart
- `Companion/Jay_Derrett`: nibble-indexed double-table front end + Companion tail

**Verdict on `pipelines/companion/`:** taxonomically sound. Every sub-engine traces back to Bowden's 1984 book listing. The name carries real meaning — "engines derived from the Bowden Companion driver" — and matches HVSC's own sidid classification. Verified empirically: every SID in our regression's Companion bucket (44 subtunes across Up_up_and_Away, bowden_canonical/Vic Berry, clever_music, henrys_house, yes_tune, melonmania) returns `Companion` from sidid in hvsc84.db.

Related: [[project_jay_derrett]] (the Derrett rewrite branch — excluded due to aperiodic design), [[project_clever_music]], [[project_bowden_canonical]].

**Older research files** that informed this (under `deprecated/research_docs/Companion/docs/`): `sidid_source_companion_signature.md`, `keith_bowden_book.md`, `archive_org_companion_book.md`.

**External sources:**
- Centre for Computing History — The Companion to the Commodore 64: https://www.computinghistory.org.uk/det/60534/The-Companion-to-the-Commodore-64/
- cadaver/sidid on GitHub: https://github.com/cadaver/sidid
- GTW64 — Up Up and Away: https://www.gamesthatwerent.com/gtw64/up-up-and-away/
