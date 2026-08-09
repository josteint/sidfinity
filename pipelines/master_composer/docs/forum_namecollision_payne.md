# Master Composer — name collisions resolved: Patrick Payne + TFMX/MasterComposer

Provenance
- source_urls:
  - https://www.vgmpf.com/Wiki/index.php?title=Master_Composer (composer list)
  - https://www.vgmpf.com/Wiki/index.php?title=Chris_H%C3%BClsbeck (Hülsbeck's editors)
  - https://github.com/cadaver/sidid (sidid.cfg / sidid.nfo signatures + notes)
  - https://en.wikipedia.org/wiki/Test_Drive_(1987_video_game) (Payne credit)
  - WebSearch result text (steemit Hülsbeck timeline; VGMPF TFMX Editor)
  - local: `hvsc84.db` (engine + author columns) + byte verification of `hvsc85/` SIDs
- fetched_via: WebFetch + WebSearch + local SQLite (read-only) + local byte scan (read-only)
- fetch_date: 2026-06-13
- author/handle: various (see per-claim attribution)
- content_date: mixed (1983–2023 referents)
- reliability: HIGH on the local DB + sidid + byte evidence; MEDIUM on web biography snippets.

---

## A. "(Patrick_Payne)" is NOT a separate engine — it's a composer + a duplicate sidid sig

Three independent lines of evidence, all pointing the same way:

1. **HVSC/our DB treat Patrick Payne tunes as the `Master_Composer` engine.** Query of
   `hvsc84.db` (read-only):
   - `GAMES/S-Z/Test_Drive.sid` — engine=`Master_Composer`, author=`Patrick Payne`
   - `GAMES/A-F/Accolades_Comics.sid` — engine=`Master_Composer`, author=`Patrick Payne`
   - `MUSICIANS/H/Hatlelid_Kris/Power_at_Sea.sid` — engine=`Kris_Hatlelid`,
     author=`Kris Hatlelid & Patrick Payne`
   So Payne is recorded as a **composer/author**, and his Master Composer game tunes carry the
   ordinary `Master_Composer` engine tag — exactly like the 478 `DEMOS/UNKNOWN/Master_Composer/`
   tunes.

2. **VGMPF lists Patrick Payne among the editor's USERS.** The VGMPF "Master Composer" page lists
   Patrick Payne alongside Charles Callet, Graham Marsh and Tommy Dunbar as composers/arrangers
   **who used Master Composer** — i.e. a musician, not a tool author. (He composed C64 game music
   for Access Software / Accolade titles, incl. **Test Drive (1987)** and Accolade's Comics.)

3. **The sidid `Patrick_Payne` signature is the same engine's voice-1 slice.** sidid.cfg carries a
   second fingerprint labelled `Patrick_Payne`:
   `29 FE 8D 04 D4 4C ?? ?? A8 B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4`
   I verified (read-only) that this sig and the main `Master_Composer` sig
   (`… 29 FE 8D 0B D4 …`) **co-occur in EVERY Master Composer file**, a constant 53 bytes apart in
   the standalone-editor rips (74 in the game-embedded Test Drive). They are the **voice-1 vs
   voice-2 control/freq writes of one contiguous play routine** (see `forum_sidid_fingerprints.md`
   for the table + opcode reading). So `Patrick_Payne` is a near-duplicate signature of the SAME
   player — almost certainly seeded from Payne's Access Software game rips — not a distinct engine.

**Conclusion:** the `(Patrick_Payne)` parenthetical is an **author/credit + sidid-variant label**.
The extractor must use ONE code path for `Master_Composer` and `(Patrick_Payne)` tunes. (Watch the
game-embedded rips like Test Drive: same engine, but the inter-voice byte layout/relocation can
differ — confirm freq-table + table offsets per file.)

> Caveat: VGMPF rendered its composer list slightly differently across two fetches (Mark Darin,
> Systems Editoriale appeared once); Callet, Marsh, Payne, Dunbar are consistent. Not load-bearing.

---

## B. "MasterComposer" (one word, TFMX-based, 1990) IS a separate engine

This is a genuine, unrelated product that merely shares the string "Master[ ]Composer":

- **sidid.nfo (cadaver), verbatim:** TFMX/MasterComposer —
  *"AUTHOR: Playboy & Sir Tippitt  RELEASED: 1990  Bierfront"*, and it is an
  *"Editor that is based on the player of /MUSICIANS/H/Huelsbeck_Chris/Starball.sid."*
  Its sidid signature `F0 26 B1 06 48 4A 4A 4A 4A 9D` (indirect `(zp),Y` load + nibble shift +
  `STA abs,X`) shares **no bytes** with the Access Software player.
- **Our `hvsc84.db`** already separates them: engine=`TFMX/MasterComposer` has **5 tunes**;
  engine=`Master_Composer` has **1019**. Different fingerprint, different family.
- **Timeline** (WebSearch synthesis of the steemit Hülsbeck article + VGMPF Hülsbeck page):
  Access Software's **Master Composer = 1983/84 (C64)**; Chris Hülsbeck's own C64 editors were
  **Musicmaster** (driver, 1985), **Soundmonitor** (1986), **The Final Musicplayer** (1987), then
  **TFMX** (Amiga, 1988) — *Hülsbeck never made anything called "MasterComposer."* The
  1990 demoscene **MasterComposer V1.0** (→ TimeComposer) was an editor built **on top of the TFMX
  player** by others (Playboy & Sir Tippitt per sidid; the broader TFMX editor was by Peter
  Thierolf around Hülsbeck's format). VGMPF's Chris Hülsbeck page (verbatim) lists only
  *Musicmaster (1985), Soundmonitor (1986), The Final Musicplayer (1987), TFMX (1988)* — **"no
  mention of … 'MasterComposer'."**

**Conclusion:** the TFMX-ecosystem "MasterComposer" is a **completely separate engine** (Amiga/TFMX
lineage, 1990, only 5 HVSC tunes). It must never be conflated with our 1983 Access Software target.
HVSC already keeps them apart by engine tag; keep that boundary in the SIDfinity pipeline too.

### One-line summary table
| Name | Year | Platform | Author | Lineage | HVSC tag | Tunes |
|---|---|---|---|---|---|---|
| **Master Composer** (target) | 1983/84 | C64 | Paul Kleimeyer / Access Software | original | `Master_Composer` (+ `(Patrick_Payne)` credit) | **1019** |
| MasterComposer / TimeComposer | 1990 | Amiga/demoscene | Playboy & Sir Tippitt (on TFMX) | Hülsbeck TFMX player | `TFMX/MasterComposer` | 5 |
