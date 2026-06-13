<!--
source_url: https://deepsid.chordian.net/ ; https://csdb.dk/sid/?id=19169 ;
            https://github.com/cadaver/sidid (sidid.cfg + sidid.nfo) ;
            local: tmp/dmc_hunt/DeepSID/ (php/, sidid_100/, special_updating.sql)
fetched_via: direct (WebFetch/WebSearch) + local read
fetch_date: 2026-06-13
author: DeepSID = Jens-Christian Huus (JCH/Chordian); sidid = Cadaver + HVSC crew; CSDb community
content_date: MA editor 1989; manual ~2019 (Swagerman's "20 years" note); sidid V1.09 / format V2.0
reliability: HIGH for the sidid.nfo/cfg verbatim quotes and the CSDb release facts;
             MEDIUM for the DeepSID live player-info panel text (JS/AJAX-rendered; not
             directly fetchable — reconstructed from the local DeepSID source + the live
             players_info DB schema, which is NOT in the local checkout).
-->

# Music Assembler — DeepSID + web findings

## What DeepSID shows / how it identifies MA tunes

DeepSID (deepsid.chordian.net, by JCH/Chordian) is an online player for HVSC +
Compute's Gazette. Its per-file pages are JS/AJAX-rendered, so the player-info
panel text is NOT fetchable as static HTML. Reconstructed from the local
checkout (`tmp/dmc_hunt/DeepSID/`):

- **Player identification path** (`php/sid_id.php`): DeepSID runs its OWN
  reimplementation of SIDId — "inspired by the SIDId script by Cadaver that
  HVSC uses" — reading the same `sidid.cfg` to name the player. So the player
  string DeepSID prints for an MA tune is literally **`Music Assembler`**
  (the `Music_Assembler` sidid name, de-underscored for display).
- **Player-info panel** (`php/player.php`, `php/player_list.php`): the prose
  description shown under "Players/Editors" comes from a live MySQL table
  `players_info` (columns incl. `title`, info text). That table is server-side
  and NOT in the local checkout, so the exact panel prose can't be quoted here.
  The schema confirms each player gets a one-row info blurb.
- **STIL notes**: come from HVSC's `STIL.txt`, per-file, not player-level —
  nothing MA-player-specific.

### DeepSID's manual MA correction (local, actionable)
`php/_update/special_updating.sql` re-tags two tunes the MA signature
false-positives onto:
```
/* Replace 'Music Assembler' with 'Padua's Music Mixer' which used the same player */
UPDATE files SET player = "Padua's Music Mixer" WHERE id = 32528  -- MUSICIANS/N/Nebula/Catman.sid
UPDATE files SET player = "Padua's Music Mixer" WHERE id = 32543  -- MUSICIANS/N/Nebula/Flodder.sid
```
=> "Padua's Music Mixer" is a derivative that reuses the MA player and matches
the same sidid signature. A handful of "MA" hits are really this. Worth a
verification carve-out.

## Authorship / release facts (CSDb + manual, corroborated)

- The MA editor used by the 6351 HVSC `Music_Assembler` tunes is
  **"Music-Assembler V1.0", a 1989 tool by the Dutch USA Team**, written by
  **Marco Swagerman (MC)** with **Oscar Giesen (OPM)** (CSDb sid #19169 page:
  "Parallax / Marco Swagerman (MC) / 1989 / Dutch USA Team"; the page lists
  "Music-Assembler V1.0" as a 1989 Dutch USA-Team tool release). The local
  manual (`csdb_manual_0_01b.txt`, "Music Assembler 1.0 User Manual, Version
  0.01b, Written by Marco Swagerman") corroborates: MC + OPM, sold via
  Markt+Technik, "mainly in Germany."
- Provenance of the manual: Swagerman wrote it retrospectively ("I just took a
  little break for about 20 years"), so the PDF is a modern (≈2019) re-doc of
  the 1989 product, NOT period documentation.

## NAMING COLLISION — flag for classification (NEW, important)

The upstream **Cadaver `sidid.nfo`** (info file paired with `sidid.cfg`,
fetched from github.com/cadaver/sidid) attributes the `Music_Assembler`
signature name to a DIFFERENT product:
```
Harald_Rosenfeldt
     NAME: Music Assembler V3.1
   AUTHOR: Harald Rosenfeldt
 RELEASED: 1989 64'er/Markt & Technik
```
So in the HVSC/sidid universe there are TWO unrelated "Music Assembler"s, both
1989, both with a Markt & Technik connection:
1. **Swagerman/Giesen "Music-Assembler V1.0"** (Dutch USA-Team) — the editor
   the 6351 HVSC tunes were made with, matching the `Music_Assembler` /
   `(Music_Assembler/MC)` byte signatures. This is OUR target.
2. **Harald Rosenfeldt "Music Assembler V3.1"** (64'er magazine / Markt &
   Technik type-in) — what the sidid.nfo NAME field happens to label the
   signature. Likely the nfo author conflated the two, OR the signature also
   catches Rosenfeldt's player.

Action: do NOT trust the sidid.nfo `NAME/AUTHOR` blindly when documenting MA —
the byte signature is the Swagerman tool's (confirmed by disassembling HVSC
binaries, see `sidid_signature_analysis.md`); the "Harald Rosenfeldt / V3.1"
attribution in the nfo is suspect and should be treated as a separate product
unless a future RE proves the players are the same code.

## sidid provenance chain (so future sessions trust the bytes)

- Local `tmp/dmc_hunt/sidid/sidid.cfg`, `player-id/config/sidid.cfg`,
  `DeepSID/utility/sidid_100/sidid.cfg` all carry the SAME `Music_Assembler`
  base signature, and it is byte-identical to the live upstream
  `github.com/cadaver/sidid/sidid.cfg` (verified by direct fetch 2026-06-13).
- SIDId itself: V1.09, by Cadaver (loorni@gmail.com), signatures from Ian Coog,
  Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos. The `player-id` Rust fork
  uses the V2.0 signature-file format (`&&` token, optional `END`).
