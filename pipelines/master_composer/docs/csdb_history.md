# Access Software / Paul Kleimeyer — provenance & leads

> **Provenance**
> - **source_url:**
>   - https://csdb.dk/scener/?id=19061 (Paul Kleimeyer, CSDb)
>   - https://en.wikipedia.org/wiki/Access_Software
>   - https://www.filfre.net/2014/08/access-software/ (The Digital Antiquarian, deep history)
>   - https://www.mobygames.com/person/1084/bruce-carver/
>   - local: `hvsc84/MUSICIANS/K/Kleimeyer_Paul/`, `hvsc84/DEMOS/UNKNOWN/Master_Composer/`, `hvsc84.db`
>   - https://www.pouet.net/ (searched — no match)
> - **fetched_via:** curl (Firefox/128 UA) for CSDb scener; WebSearch for Access Software /
>   Pouet; local fs + read-only `hvsc84.db` for HVSC corpus
> - **fetch_date:** 2026-06-13
> - **content_date:** CSDb scener (current); Digital Antiquarian article 2014; company history 1982–
> - **reliability:** HIGH for company facts (Wikipedia + Digital Antiquarian, well-sourced) and
>   for the local HVSC corpus counts. MEDIUM for the inference that Kleimeyer's HVSC tunes are
>   the canonical Master Composer reference renditions (corroborated by CSDb comments, not a
>   primary doc).

---

## Paul Kleimeyer (the engine author)

- CSDb scener id **19061**, function **Musician**, **67–78 credited releases, 1984–2023**
  (an active, long-lived C64 musician — the Master Composer authorship is from sidid.nfo, not
  from a self-credit on this page; CSDb does not list the editor itself under his scener
  credits).
- `sidid.nfo` is the authoritative attribution: *"Master Composer — AUTHOR: Paul Kleimeyer —
  RELEASED: 1983 Access Software Inc."*
- **His own HVSC tunes are the best reference renditions of the engine.** Present locally at
  `hvsc84/MUSICIANS/K/Kleimeyer_Paul/`:
  `Bill_Bailey, Brandenburg_1, Brandenburg_2, Demosongs, Entertainer, Flashdance, Fuer_Elise,
  Greensleeves, Maniac, Maple_Leaf_Rag, She_Works_Hard_for_the_Money` (11 SIDs).
  CSDb comments single out **Maniac.sid** ("perfect rendition using plain and simple
  waveforms") and **Flashdance.sid** as quality examples — good first migration candidates
  because they exercise the engine "without any fuss".
- No "Patrick Payne" appears among his credits or anywhere in CSDb for Master Composer — that
  string is only a **sidid variant tag** (see `csdb_releases.md`), not a person tied to this
  editor.

---

## Access Software, Inc. (the publisher)

- US boxed-software house, **founded November 1982** in **Salt Lake City, Utah** by **Bruce
  Carver** and **Chris Jones** (Bruce's brother **Roger Carver** also involved).
- Catalogue relevant for cross-artifact hunting: **Beach-Head (1983)**, **Raid Over Moscow
  (1984)**, **Beach Head II**, the **Leader Board** golf series, later **Links** golf and the
  **Tex Murphy / Mean Streets** FMV adventures. Acquired by **Microsoft (1999)** → became
  *Indie Built*.
- Deep, well-cited history: **The Digital Antiquarian, "Access Software" (2014-08)** —
  https://www.filfre.net/2014/08/access-software/ . A good lead for any contemporary mention of
  the Master Composer product line and the people around its audio tooling.
- Master Composer was a **$39.95 boxed productivity/utility product** (1983–84), not a game —
  so its surviving artifacts are a **printed manual** (not yet scanned, see `csdb_manual.md`),
  the **editor disk** (4 cracks on CSDb), and the bundled **Music Translator V1.2** export tool.

---

## HVSC corpus footprint (local, read-only)

- `hvsc84.db`: **`engine='Master_Composer'` → 1019 SIDs** (matches the task brief's ~1,019).
  A second small ambiguous bucket exists: **`engine='TFMX/MasterComposer'`** — sidid
  double-match candidates worth auditing during migration (TFMX vs Master Composer
  disambiguation).
- `hvsc84/DEMOS/UNKNOWN/Master_Composer/` exists — the dedicated HVSC folder for the (mostly
  uncredited) tunes made with the tool, e.g. `Mr_Sandman, Kitten_on_the_Keys, Viva, Pan_3,
  Bread_and_Butter, Superman_2, Lonely, A_View_to_a_Kill_2, …`.
- `hvsc84/DEMOS/M-R/MasterComposer_sample.sid` — note: this is the demo SID bundled with the
  **unrelated Bierfront "Mastercomposer V1.0"** scene tool (CSDb 4298), *not* Access Software's
  engine. Exclude it from the Access-Software corpus.
- **The Mighty Bogg** is the one named scener who used the tool for many releases (4mat, CSDb).

---

## Pouet

- **No Master Composer match on Pouet** (prodlist filter `master composer` returns nothing;
  Pouet skews Amiga/PC demoscene and indexes few C64 boxed-software tools). Not a useful source
  for this engine.

---

## Leads to follow

1. **Disasm/parser source — pull the editor disks.** No public source exists, so the binary IS
   the spec. Fetch (CSDb-hosted d64; see `csdb_releases.md` for the four URLs):
   - `Master Composer (1983)(ASI).d64` (id 184807 — the **original**, highest fidelity),
   - `Mastercomposer-ICG.d64` (id 31047 — bundles **Music Translator V1.2**, which itself
     documents the on-disk song-data layout by virtue of converting it).
   Then `seed_disassembly.py` the player at the relocated entry (init≈`$7580`, play≈`$7587`;
   `SYS 30120` = `$75A8` is the built-in player entry). Use the sidid `(Patrick_Payne)` /
   `(Lope_Pulse_Sweep)` byte patterns to locate the play loop + the optional PWM hack.
2. **Printed manual — still missing.** Retry **Lemon64 thread t=55611 "Master composer manual
   scan?"** from a non-blocked egress (it 503'd here, Retry-After 3600). Then sweep
   `lemon64.com/museum` (manuals), c64preservation.com, archive.org (search "Access Software"
   manuals), and US C64 collector Discords. A boxed $39.95 product's manual very likely exists
   in a private collection.
3. **Period press for an ad/review.** **Compute!'s Gazette 1984 issues are on archive.org**
   (issues 008/Feb–016/Oct 1984 surfaced in search) — grep the OCR for "Master Composer" /
   "Access Software" for an advertisement or review describing the page/block/bar model. Also
   check RUN, Ahoy!, and Commodore Power/Play 1984.
4. **Music Translator V1.2** (bundled with the ICG crack) — reverse this tool; a *converter*
   encodes the exact song-data byte format, often more legibly than the player.
5. **TFMX/MasterComposer ambiguity** — audit those SIDs against the sidid signature during
   migration; some may be mis-bucketed Master Composer tunes (or genuine TFMX).
6. **The Digital Antiquarian Access Software article** + **Bruce Carver obituary**
   (gamedeveloper.com) — for any interview or staff note that names the Master Composer author
   or its tooling lineage.
