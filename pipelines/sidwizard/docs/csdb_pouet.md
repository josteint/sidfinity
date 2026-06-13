# SID-Wizard — Pouet productions + community reception

> **Provenance**
> - **source_url:** `https://www.pouet.net/prod.php?which=59899`
>   (Pouet entry for **SID-Wizard**, group **SIDrip Alliance & Singular Crew**; the page is currently
>   titled for the latest build, v1.93, but the entry tracks the whole tool lineage.)
> - **corroborating:** `https://www.pouet.net/` search; `http://csdb.dk/getinternalfile.php/108351/`
>   (V1.0 manual PDF — link surfaced from the Pouet entry).
> - **fetched_via:** WebFetch (Pouet); `curl` HEAD for the CSDb internal-file manual link.
> - **fetch_date:** 2026-06-13
> - **author:** code = **Hermit (Mihály Horváth)**; music in the release = **NecroPolo**.
>   Group billing: **SIDrip Alliance & Singular Crew**.
> - **content_date:** Pouet entry first added 2012 (comments span 2012→present); page header reflects
>   v1.93 (June-2018 lineage date shown by Pouet, the latest patch 2025).
> - **reliability:** MEDIUM. Pouet for a *tool* carries reception/credits + download pointers, not a format
>   spec. Treated as corroboration of credits/lineage + a stable manual-download lead, not as primary
>   format documentation.

---

## 1. Production facts

- **Type:** **Demotool** (Pouet classifies SID-Wizard as a demotool, not a demo/intro).
- **Platform:** Commodore 64.
- **Lineage date on Pouet:** June 2018 (the v1.8 wave); the entry is now labelled for **v1.93**.
- **Credits:** **Hermit** — code; **NecroPolo** (Péter Nagy-Miklós) — music; under **SIDrip Alliance &
  Singular Crew**. (Consistent with the manual's thank-you list: NecroPolo + Nata for testing &
  example-tunes; Soci/Zsolt Kajtár for SVN + optimisation; Unreal for box graphics; Leon for the splash.)

## 2. Community reception (all comments, verbatim)

> 1. "Pretty cool new SID tracker project. Open source too."
> 2. "Respect! A new SID tracker in 2012, open source with manual wow!"
> 3. "Yeah!!"
> 4. "Great tracker, needs more thumb-ups"
> 5. "Cool!"
> 6. "thumbs up for not being another JCH clone!"
> 7. "thumbs up for being goat tracker clone! .]"
> 8. "Superawesome! Great functions & manual, easy to understand."
> 9. "Lovely. I felt not in phase with goattracker and I founded this great tool, lucky!"

**Signal for SIDfinity (no deep tech in the comments, but the lineage framing is consistent):**
the scene positions SID-Wizard between **Goattracker** (shared FX-number convention $01/$02/$03; "goat
tracker clone" / "not in phase with goattracker") and the **JCH editor** ("not another JCH clone"). This
matches the manual: pattern-FX numbering borrowed from Goattracker, automatic per-track filter handling
borrowed conceptually from JCH. No commenter contradicts the format details captured in
`csdb_hermit_site_manual.md`.

## 3. Download / documentation links exposed by the Pouet entry

- **C64 release (CSDb):** `https://csdb.dk/release/download.php?id=314031`
- **Linux/PC build (CSDb):** `https://csdb.dk/release/download.php?id=314029`
- **V1.0 User Manual (PDF):** `http://csdb.dk/getinternalfile.php/108351/SID-Wizard%201.0%20User%20Manual.pdf`
  — **VERIFIED reachable** via `curl` (HTTP 200, 718 KB, `application/octet-stream`). NOTE: the CSDb
  `getinternalfile.php` endpoint is **NOT** behind the Cloudflare JS-challenge that blocks the
  `csdb.dk/release/?id=...` HTML pages, so this is a **stable scriptable download URL** for the docs
  cluster. (The V1.4 manual PDF — the most detailed — is mirrored at c64.cz / retrotime.hu; see
  `csdb_hermit_site_manual.md`.)
- **Source:** `http://sourceforge.net/projects/sid-wizard/` (early versions) → GitHub forks
  (anarkiwi, M64GitHub) for 1.8.x.
- **CSDb entry (v1.93):** `https://csdb.dk/release/?id=255544`; **Demozoo:** `http://demozoo.org/productions/99999/`.

## 4. Other Hermit / SID-Wizard-adjacent Pouet items (leads)

- Hermit's broader Pouet author page lists his **cRSID** (a portable SID emulator/replayer) and SIDRIP
  Alliance demoscene work — relevant only as cross-reference for his SID-engine know-how, not for the SWM
  format. (cRSID is a useful independent reference replayer for validating SID-Wizard write streams.)
- No SID-Wizard *productions* on Pouet carry engine-internal technical comments beyond the tool entry
  above; the technical substance lives in the manual + CSDb release notes + the source.
