---
source_url: https://github.com/Chordian/deepsid
fetched_via: direct
fetch_date: 2026-06-14
author: Chordian (Thomas Egeskov Petersen)
content_date: unknown (repo continuously updated)
reliability: primary (negative finding)
---

# DeepSID — SongSmith-Specific Notes

## Finding: No SongSmith-Specific Code in DeepSID

A search of the `Chordian/deepsid` GitHub repository for "SongSmith" returned **zero
matches** across all files. DeepSID does NOT have dedicated SongSmith player-detection
logic or player-name handling at the code level.

Sources checked:
- `https://github.com/Chordian/deepsid/search?q=SongSmith` — 0 results
- `https://github.com/Chordian/deepsid/blob/master/js/player.js` — no SongSmith
  reference; player selection is via explicit constructor parameter (emulator name),
  not engine detection
- `https://github.com/Chordian/deepsid/blob/master/php/backend.php` — HTTP 404
  (file does not exist at that path)

## DeepSID Architecture for Player Tagging

DeepSID's `SIDPlayer` constructor in `js/player.js` selects emulator backends by
a named parameter (e.g. `"resid"`, `"jsidplay2"`, `"websid"`) — NOT by detecting
the SID engine embedded in the file. Player-type identification (the "Loadstar_SongSmith"
label that DeepSID may display) comes entirely from the HVSC metadata (the `engine`
field in the SID file headers or from sidid's classification of HVSC), NOT from
DeepSID's own analysis.

## Composer-Icon Tagging ('L' Icon)

A secondary web source (search result, unverified with source HTML) mentions that
DeepSID shows an 'L' focus icon for composers who exclusively used Loadstar SongSmith.
This is a **UI display feature** based on HVSC engine metadata, not a detection
algorithm. It tells us:
- DeepSID tracks "SongSmith-only composers" as a display category.
- The set of such composers is known from HVSC classification.
OPEN: Verify which composers get the 'L' icon by checking the DeepSID codebase more
thoroughly (the PHP or JS that renders focus icons) — the relevant logic was not found
in the fetched pages.

## CSDb Reference from sidid.nfo

The `sidid.nfo` file (cadaver/sidid) explicitly references CSDb release
https://csdb.dk/release/?id=122855 as the REFERENCE entry for Loadstar_SongSmith.
That CSDb page is titled "Songsmith" (C64 Tool), has 141 downloads, download URL
`http://csdb.dk/getinternalfile.php/121491/Songsmith-Loadstar.d64`, and lists seven
SID compositions by Cruz, Debby as associated files:

- Alouette
- Funiculi Funicula
- Meadowlands
- Muss I Denn
- Scarborough Fair
- Skye Boat Song
- The Parting Glass

No creator credit is listed in the CSDb entry. The .d64 filename `Songsmith-Loadstar.d64`
confirms this is the Loadstar-published version of the tool.

A second CSDb entry exists at https://csdb.dk/release/?id=121491 — the search returned
this URL pointing to the same download. Both IDs appear to resolve to the same release
(the download link in the search result for id=122855 points to the internal file
`/121491/Songsmith-Loadstar.d64`, suggesting id=122855 is a re-record or alias of
the canonical release at id=121491).

OPEN: Direct fetch of https://csdb.dk/release/?id=122855 returned "The Sound FX Kit"
content — likely a CSDb search/session redirect artefact. The canonical Songsmith
release is at id=122855 (Songsmith C64 Tool) with download via internal file path
121491. Needs re-verification via a fresh CSDb request.

## JSIDPlay2

JSIDPlay2 uses SIDId for player identification (per its user guide). No SongSmith-
specific handling exists in JSIDPlay2 itself — it inherits the `Loadstar_SongSmith*`
labels from SIDId's `sidid.cfg`. Source:
https://haendel.ddns.net/~ken/UserGuide.html (confirmed: no "SongSmith" or "Loadstar"
in user guide content; only mention is that players are identified by SIDId memory
analysis).

## libsidplayfp / sidplayfp

No SongSmith-specific handling found (web search confirmed no hits for
"libsidplayfp SongSmith"). libsidplayfp is a SID emulator, not a player-engine
classifier — it plays all PSID files using 6510+SID emulation regardless of the
embedded engine type.

## Leads to Follow

- Fetch the DeepSID PHP template/rendering files to find the 'L' focus-icon logic
  and confirm which HVSC-engine strings trigger it (e.g. does it check for all four
  `Loadstar_SongSmith*` variants or just `Loadstar_SongSmith`?).
- Directly fetch https://csdb.dk/release/?id=122855 in a clean session to get the
  canonical CSDb Songsmith release data unambiguously.
- The CSDb .d64 download `Songsmith-Loadstar.d64` is the primary binary to disassemble.
  Download from http://csdb.dk/getinternalfile.php/121491/Songsmith-Loadstar.d64.
