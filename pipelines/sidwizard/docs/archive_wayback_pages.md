<!--
provenance:
  topic: Wayback Machine findings — old Hermit/SIDRIP pages, early SID-Wizard announcements, archived release-file list, dead format docs
  primary_source_urls:
    - http://web.archive.org/web/20121126024440id_/http://sourceforge.net/projects/sid-wizard/   (earliest archived SourceForge project page, 2012-11-26)
    - http://web.archive.org/web/20170626033955id_/http://hermit.sidrip.com/                     (Hermit's software homepage, 2017-06-26)
    - http://web.archive.org/cdx/search/cdx?url=sourceforge.net/projects/sid-wizard/files/release/* (Wayback CDX: archived release ZIP listing, snapshot 2018-06-18)
    - http://web.archive.org/cdx/search/cdx?url=hermit.sidrip.com*                                 (Wayback CDX: hermit.sidrip.com snapshot inventory)
  fetched_via: "wayback 2026-06-13" — Wayback CDX API + id_ raw archived copies fetched via curl (web.archive.org is NOT reachable through WebFetch in this environment; the CDX API and the dated id_ raw-content endpoints ARE reachable via curl).
  fetch_date: 2026-06-13
  author: Mihaly Horvath ("Hermit") for the site content; SourceForge for the project-page chrome.
  content_date: archived snapshots span 2012-07-12 .. 2026-01-03 (Hermit homepage); release-dir listing as-of 2018-06-18
  reliability: HIGH for the archived release-ZIP filename list and the project tagline (read straight from archived HTML / CDX). MEDIUM for narrative around redirects (hermit.sidrip.com went 302/301 between ~2018 and ~2025, so the live content for those years isn't captured).
-->

# SID-Wizard — Wayback Machine findings

Companion docs: `archive_version_history.md`, `archive_version_player_diffs.md`. This doc
captures what the Internet Archive holds for the *old* hosting (Hermit's site + the original
SourceForge files), which fills gaps the live pages no longer show.

## 1. The original SourceForge release-file set (the canonical "what shipped where")

The live SourceForge files page today shows only `SID-Wizard-1.7.zip`. The Wayback CDX index
of `sourceforge.net/projects/sid-wizard/files/release/*` (richest snapshot 2018-06-18) preserves
the **complete original release-ZIP listing** — these are the exact filenames Hermit uploaded:

| Archived file | Maps to version | Note |
|---------------|-----------------|------|
| `SID-Wizard-1.0-rc.zip`        | V1.0 RC | the 2012-07 beta |
| `SID-Wizard-1.0-stable.zip`    | V1.0    | the 2012-08-31 "100%" release |
| `SID-Wizard-1.2-full-pack.zip` | V1.2    | "full-pack" naming (the 1.2 release bundled examples/manual) |
| `SID-Wizard-1.4.zip`           | V1.4    | |
| `SID-Wizard-1.5.zip`           | V1.5    | |
| `SID-Wizard-1.6.zip`           | V1.6    | |
| `SID-Wizard-1.7.zip`           | V1.7    | last classic SourceForge ZIP (also mirrored on hermit.sidrip.com) |

**Key negative result: there is NO `SID-Wizard-1.8.zip` (or any 1.9x ZIP) in the SourceForge
`release/` directory.** This corroborates the version-history finding that SourceForge
hosting effectively stopped at V1.7 (2014); V1.8 only ever entered SourceForge via the 2021 SVN
*source* import (r393/r394), and the **V1.8+ binaries live on CSDb + the author's site**, never
as a SourceForge release ZIP. → For provenance of an HVSC tune: a 1.0-rc/1.0-stable/1.2/1.4/1.5/
1.6/1.7 binary could have come from SourceForge; a 1.8+ binary did not.

> Download note: live `web.archive.org` page fetches are blocked in this environment, but the
> archived ZIPs are retrievable by a sibling/future session via the dated raw URL form, e.g.
> `http://web.archive.org/web/20180618003424id_/https://sourceforge.net/projects/sid-wizard/files/release/SID-Wizard-1.5.zip/download`
> (use the `id_` infix to get the original bytes without Wayback chrome). Not pulled here —
> the source player.asm is already covered via the SVN per-revision raw.

## 2. Earliest SourceForge project page (2012-11-26)

The project (`group_id=815641`, owner **`hermitsoft`**) was on SourceForge from launch
(earliest CDX hit 2012-07-12, the day after SVN r1). The archived project page gives the
**original one-line project description**, used consistently ever since:

> "Featureful native Commodore 64 music tracker with MIDI/XM converter"

Topics tagged on the page: *sound, c, assembly, audio-editors, midi, multimedia, composition*.
Nothing format-spec-level here, but it confirms the project's framing from day one (a **native
C64** tracker — the cross-platform PC build is a much later, V1.9 addition).

## 3. Hermit's software homepage — hermit.sidrip.com (2017 snapshot)

`hermit.sidrip.com` ("Hermit Software Hungary") is the author's own distribution page. Snapshot
inventory (CDX): live `200` captures in **2017** (2017-06-26, 2017-07-13) and again in **2025**
(2025-09-15); in between (~2018-11 .. ~2025) the root returns `302`/`301` redirects, so that
middle period's content isn't archived. The **2017-06-26** capture (the cleanest old one) lists
Hermit's whole tool suite — useful context for where SID-Wizard sits and for the lineage of the
emulator that later powers the PC editor:

- **SID-Wizard 1.7** — "Featureful Commodore64 tracker-style music editor" (6.4 MB) ← the SID-Wizard download as of 2017 was still 1.7.
- **TEDzakker 1.0** — Plus4/C16 TED-music tracker (sister tracker; cf. this repo's own TEDzakker references).
- **1raster-tracker 1.0** — one-rasterline C64 SID tracker (Hermit's minimalist tracker; SID-Wizard's V1.5 "absolute note-view" features were cross-pollinated from it per the ChangeLog).
- **MIDItrk-1.4** — cross-platform MIDI tracker (SDL + RtMidi).
- **HermIRES-1.29**, **HerMIDI** hardware (the MIDI interface SID-Wizard supports natively).
- **cSID-light** — "Non-cycleexact version of cSID with much less CPU-usage." ← **This is the ancestor of the `cRSID` engine** that the V1.9+ cross-platform SID-Wizard editor uses for emulation/playback (V1.94 ships cRSID-1.56). i.e. the PC port's audio core is Hermit's own SID emulator, developed alongside the tracker.
- Link to "My Commodore64 release page at CSDB" — the canonical home for the V1.8+ C64 releases.

The page also mentions the WTF-license/open-source stance consistent with the SourceForge repo.

## 4. Dead / moved format docs

- **No standalone "SWM format spec" web page was ever published** that the Archive holds — the
  format spec lives only inside the source tree (`sources/SWM-spec.src`) and the per-version
  User Manuals (`manuals/`). The authoritative format doc for SIDfinity is `SWM-spec.src` itself
  (see `research.md` + `archive_version_player_diffs.md` §SWM), not a web page.
- The **CSDb release pages** (the human-facing per-version notes for V1.0/V1.2/V1.4/V1.8/V1.91)
  are **not in the Wayback Machine** (CDX returns no captures for those `release/?id=` URLs) and
  were **not directly fetchable this session** (csdb.dk returned HTTP 503 to both WebFetch and
  curl on 2026-06-13 — appears to block automated agents). Their dates/notes in the other docs
  come from search-result snippets. A future session on a residential IP / browser UA should
  retry csdb.dk directly for the verbatim release notes (ids: 109698, 110942, 112716, 131846,
  165302, 220489, 221555, 255544).
- **Forum64 thread for V1.91** (`forum64.de/.../128497-sid-wizard-1-91`) returned HTTP 403 and
  has no Wayback capture — the V1.91 changelog is the one gap not yet recovered verbatim.

## Bottom line for SIDfinity

- The **player/format-relevant source** for every fingerprintable version (1.0-rc..1.8) is fully
  recoverable: 1.4..1.7 + 1.8 from the live SVN per-revision raw; 1.0..1.2 from the archived
  SourceForge ZIPs (Wayback). Nothing player-side is truly "lost".
- The **post-V1.8 story is editor/PC-side** (cSID→cRSID), not C64-player evolution — so for the
  HVSC-tune extraction goal, the source/format work is bounded by the 2012-2018 C64 releases.

## Leads to follow
- **CSDb verbatim release notes (ids 109698 / 110942 / 112716 / 131846 / 165302 / 220489 / 221555 / 255544):** blocked by HTTP 503 this session (csdb.dk rejects automated fetchers). Retry from a browser/residential context to capture the human-facing per-version "what's new" — especially the **V1.91** notes (the one changelog gap) and the **V1.8** CSDb description (to confirm the 2018 public-release date vs the 2021 SVN import).
- **Pull the archived early-version source the byte-diff couldn't reach:** fetch `SID-Wizard-1.0-stable.zip` and `SID-Wizard-1.2-full-pack.zip` from Wayback (`id_` raw URLs in §1) and diff their `player.asm`/`exporter.asm` against the r214 (V1.4) source — this turns the V1.0→V1.2→V1.4 deltas from ChangeLog-prose into hard byte diffs (closing the MEDIUM-LOW reliability gap in `archive_version_player_diffs.md`).
- **Confirm the `SWversion` build constant's per-release values** (it's referenced as `TrackerID .text " SID-WIZARD ",SWversion," "` but defined elsewhere — likely `settings.cfg`/`version.inc`): grep each release ZIP / the SVN `settings*.inc` at each tag rev to get the exact embedded `" SID-WIZARD <ver> "` byte string per version → a ground-truth in-binary version stamp for the classifier.
- **Byte-diff V1.5→V1.6→V1.7→V1.8 player.asm** (r312 vs r357 vs r389 vs r393) the same way r214/r312 were diffed here — to confirm whether sidid needs implicit 1.6/1.7/1.8 fingerprints beyond the named V1.0/1.2/1.4/1.5 (the **V1.8 SR-AD reorder** at r390 and the **V1.6 instrument-memory rearrange** are the prime suspects).
- **Verify the `HARDRESTYPES_ON` / driver-variant gating empirically:** the AD-SR vs SR-AD path, the `$D418`-in-init behaviour, and ghost-register coverage are all `.if feature.*`-gated — decode a handful of real HVSC SID-Wizard tunes (bare/light/medium/normal/extra/demo) with `siddump --writelog` and confirm which write-model knobs actually fire per variant before encoding them as `EngineConfig` fields.
- **Retry hermit.sidrip.com 2025-09-15 (200) capture** for the current download/version list and any late changelog notes the author posts there (the 2018-2025 redirect gap means the modern page content isn't yet seen).
