# Music Assembler — publication trail & source inventory (Archive.org / Markt+Technik / scene)

> **Provenance**
> - sources: archive.org search + metadata API, csdb.dk, c64-wiki.com, zimmers.net
>   anonftp, raw.githubusercontent.com/cadaver/sidid, web search.
> - fetched_via: direct web fetch / search (CSDb release page itself was rate-
>   limited 503 on 2026-06-13 — details below are from the manual + search hits).
> - fetch_date: 2026-06-13
> - reliability: MIXED — disk-image / fingerprint findings are HIGH; the
>   Markt+Technik / 64'er publication specifics are MEDIUM (no printed source
>   listing or magazine issue with an MA format spec was located).

## What was searched and the verdict on each priority

### Priority target: a printed/published packed-format spec or player source

**Not found in any German-magazine / Markt+Technik channel.** Searched
archive.org `64er`/`64er_sonderheft` items, kultboy-style scan hits, c64-wiki's
Markt & Technik page, and general web. Markt & Technik **did** routinely print
6502 source listings in 64'er Magazin and its books, BUT:
- Music Assembler was a **closed commercial product**, not a type-in listing. The
  manual's own author (Swagerman) stresses the data is "intricate, to many people
  unreadable data" deliberately compressed — they did not publish the format.
- No 64'er issue, Sonderheft, or M&T book with an MA format/player listing
  surfaced. The 64'er archive items returned by search are generic
  (`64er_sonderheft_35`, `64er_sonderheft_1985_08`) with no MA content.
- **Conclusion:** the publication trail yields the *product* (disk + manual) but
  **not a documented binary format**. The format must be RE'd from binaries. The
  best raw material is the editor disk (`archive_editor_disk_1990.md`) + saved
  HVSC SIDs (`archive_player_writemodel.md`). This matches the prior research.md
  assessment.

### The product (publication facts, reliable)

- **Music Assembler** by Marco Swagerman (MC) & Oscar Giesen (OPM), **The Dutch
  USA-Team**, original release **February 1989** (CSDb #94388).
- Commercially **published by Markt & Technik** (German publisher of 64'er
  Magazin), the edition on archive.org dated **1990**. Per the manual prologue:
  *"Music Assembler was at the time being published by Markt+Technik, who sold
  quite a large number of copies, mainly in Germany."*
- The user **manual** is a 2010 retro-written PDF by Swagerman (v0.01b), already
  vendored here as `csdb_manual_0_01b.pdf` / `.txt`. It documents the *editor's*
  data model only — NOT the packed output format (Swagerman intentionally never
  documented it; see manual §"Why the term Assembler?").

## Primary artifacts located (download URLs)

| Artifact | URL | Status |
|---|---|---|
| **MA 1990 editor D64** (Markt & Technik) | https://archive.org/details/d64_Music_Assembler_1990_Markt_Technik — file `Music_Assembler_1990_Markt__Technik.d64` | **downloaded** → `masm_editor_1990.d64` (+ extracted `masm_editor_1990_OMUSICASSEMBLER.prg`) |
| MA 1.0 user manual PDF | https://csdb.dk/getinternalfile.php/137191/masm_manual_0_01b.pdf | already vendored (`csdb_manual_0_01b.pdf`) |
| sidid fingerprint DB | https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg + `.nfo` | fingerprints captured in `archive_versions_and_fingerprints.md` |
| **VoiceTracker v5 D64** (Polonus, 1990) | https://archive.org/details/d64_Voicetracker_v5_1990_Pawel_Soltysinski | NOT downloaded — MA-derived variant editor |
| VoiceTracker 2.6 / 4.2 PRG | https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/ (`voicetracker2.6.prg`, `voicetracker4.2.prg`) | available — MA-derived |
| Music Mixer 6 PRG | https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/ (`MusicMixer6.prg`) | available — MA-derived |

## Wayback Machine

No dead author/format pages required rescue: the live sources (archive.org item,
CSDb, sidid GitHub, zimmers.net FTP, the vendored manual) cover everything found.
`web.archive.org` is **not fetchable** through this harness's WebFetch tool (the
fetcher refuses the host); use `curl https://web.archive.org/web/<ts>id_/<url>` if
a dead scene page needs pulling in a future session. The two Lemon64 threads that
mention MA relocation / player engines (below) were 503-rate-limited on
2026-06-13 and are the main candidates for a Wayback pull.

## CSDb (rate-limited 2026-06-13)

`csdb.dk/release/?id=94388` (the MA V1.0 release) returned HTTP 503 on every
attempt today. Re-fetch later for: exact credits, the related-releases list (the
variant editors), and any technical user comments. The release is confirmed via
search: "Music-Assembler V1.0 by Dutch USA-Team (1989)".

## Leads to follow

- **archive.org item `d64_Music_Assembler_1990_Markt_Technik`** — DONE (disk
  pulled, dir parsed, player extracted). The remaining work on this item is to RE
  the editor's *save/assemble path* to fully specify the packed `s.`/`p.` format.
- **archive.org item `d64_Voicetracker_v5_1990_Pawel_Soltysinski`** — pull to
  characterise the VoiceTracker/Music Mixer/DoubleTracker variant family (maps the
  `+$B5`/`+$70` fingerprint-offset clusters in the HVSC survey to named builds).
- **zimmers.net editors FTP**: `voicetracker2.6.prg`, `voicetracker4.2.prg`,
  `MusicMixer6.prg` — the MA-derived editor binaries; cheap to diff against the
  canonical MA player to confirm the shared core + locate each variant's speed
  divider.
- **CSDb #94388** (`csdb.dk/release/?id=94388`) — re-fetch (was 503); read the
  related-releases + comments for variant disks and any format hints.
- **Lemon64 threads** (both 503 today, retry via Wayback `curl`):
  - `https://www.lemon64.com/forum/viewtopic.php?p=1071077` — mentions attaching/
    relocating the MA music routine and possible player-engine downloads
    ("paula8364.com" was referenced in search snippet).
  - `https://www.lemon64.com/forum/viewtopic.php?t=2029` — "Looking for a copy of
    Voicetracker for music work".
- **paula8364.com** — search snippet claimed "multiple versions of Music Assembler,
  with player engines downloadable from paula8364.com." Unverified; chase for
  packaged player-engine binaries / per-version notes.
- **64'er Magazin scans** (archive.org `64er*`, kultboy.com) — LOW priority: no MA
  format listing found, but a M&T product blurb / review with an order number
  could still surface in the German press if a future session needs publication
  provenance. Not expected to contain a format spec.
