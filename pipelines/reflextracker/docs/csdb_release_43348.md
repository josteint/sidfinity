---
source_url: https://csdb.dk/release/?id=43348
fetched_via: direct
fetch_date: 2026-06-15
author: kb, Quiss, Zorc, PVCF (Reflex / The Obsessed Maniacs)
content_date: 1995
reliability: primary
---

# Reflex-Tracker V1.1 — CSDb Release #43348

## Core Details

- **Title:** Reflex-Tracker V1.1 (AKA: Reflextracker)
- **Type:** C64 Tool (PC cross-tracker that targets C64 SID)
- **Release Date:** 1995
- **Groups:** Reflex, The Obsessed Maniacs (TOM)
- **CSDb URL:** https://csdb.dk/release/?id=43348

## Credits

| Role | Person |
|------|--------|
| Code (editor) | Zorc / Reflex |
| Code (disk/optimise system) | kb / TOM |
| Code (sample menu) | kb / TOM |
| Code (sample packer + save) | Quiss / Reflex |
| Design (editor) | PVCF / Reflex |
| Design | kb (also) |
| Documentation | PVCF |
| Sampling | PVCF |
| Example songs | PVCF |
| Samples | PVCF / Reflex |

(Source: BESCHREIBUNG file extracted from D64, see below.)

## Downloads

Two archives available from CSDb:

1. `http://csdb.dk/getinternalfile.php/160214/Reflextracker v1.1-Reflex-.zip`
   — two D64 images (no block counts; possibly from no-fastloader copy)
2. `http://csdb.dk/getinternalfile.php/185033/Reflextracker_V1.1.zip`
   — two D64 images with correct block counts (preferred)

External mirror: Pokefinder.org (link on CSDb page).

## Bundled SID Demo Songs (on disk, also in HVSC)

- `MOD.ACCESS2/B` — "Access Denied (remix)", HVSC: `/MUSICIANS/P/PVCF/Access_Denied_remix.sid`
- `MOD.ENDLOSCHOOR` — "Endloschoor" (not in HVSC under this name?)
- `MOD.TRANCE202` — "Trance 202", HVSC: `/MUSICIANS/P/PVCF/Trance_202.sid`

Also mentioned in CSDb page: "Gubber" (SID ID 23564), HVSC: `/MUSICIANS/P/PVCF/Gubber.sid`

## Related CSDb IDs

| ID | What |
|----|------|
| 3 | Reflex (group) |
| 340 | The Obsessed Maniacs (group) |
| 655 | kb (scener) |
| 844 | Quiss (scener) |
| 836 | PVCF (scener) |
| 3677 | Zorc (scener) |
| 5828 | Farbrausch (group — kb's later group) |
| 188 | Smash Designs (group) |
| 118872 | Liquid Sound Designer (demo) — related C64-native editor, 1997 |

## User Comments (CSDb)

- CJ Warlock confirmed 1995 release date.
- "Gubber" might be a misspelling of "Gabber" (a rave music genre).
- Note: a translated (non-German) version was promised but does not appear to have been released. The documentation (BESCHREIBUNG) is entirely in German.

## Relationship to Liquid Sound Designer (LSD)

According to PVCF's comment on CSDb release #118872:
- LSD (1997) = "3 Channel Sidchip Duration Editor" — native C64 editor
- Reflextracker V1.1 = "2 channels Sample music" PC tracker targeting C64
- LSD was described as a "logical child" predecessor
- Note: PVCF describes it as the "PC version" — Reflextracker runs on PC, outputs C64-playable SID data

## QuadSID / Multi-Channel Notes

From the Lemon64 forum thread (https://www.lemon64.com/forum/viewtopic.php?t=4872):
- PVCF confirmed Reflextracker supports QuadSID (up to 10 channels via multiple SID chips)
- QuadSID tunes "can only be recorded as a MIDI stream" — they cannot be directly converted to standard single-SID format
- Standard output: 2 channels (two voices) — confirmed in BESCHREIBUNG: "ZWEIT STIMMIG" (two-voice)
- PVCF suggested: "it maybe would be possible to recompose them on a c64 with dmc and the changed polonus digieditor"
