---
source_url: https://web.archive.org/web/20241113150429/https://sidpreservation.6581.org/sid-editors/
fetched_via: wayback 2024-11-13
fetch_date: 2026-04-11
author: Cris "Xiny6581" Ekstrand
content_date: 2024-11-13
reliability: secondary
---

# SID Preservation — DMC-Related Information

Source: https://sidpreservation.6581.org/sid-editors/
Retrieved via Wayback Machine snapshot: 2024-11-13
(Live site was returning 503 at time of retrieval)
Author: Cris "Xiny6581" Ekstrand

---

## DMC Overview (from the SID Editors page)

The editors page introduces DMC in the context of SID music editors on the Commodore 64:

> "There was another competitor out there called 'Demo Music Creator', it used the same principles as Future Composer but added way much more advanced editing features. The first versions of DMC was hungry on the rastertime but the latter versions were excellent."

Key points:
- DMC stands for **Demo Music Creator**
- It competed directly with Future Composer (FC)
- DMC used the same general principles as FC (player-driven, command-based editing)
- Early DMC versions had high raster time usage; later versions were efficient
- DMC V4 is specifically called out as "one of the most used editors" with "lots of nice features" and "one of the most user friendly in the DMC series"

---

## DMC V4 — Editor Description

Screenshot referenced: `wp-content/uploads/2015/11/DMC_4.png`

> "DMC V4 is one of the most used editors. It has lots of nice features and also one of the most user friendly in the DMC series."

This implies there are multiple versions in the DMC series (at least V1 through V4), with V4 being the most widely used.

---

## General Editor Architecture (applies to DMC)

The editors page uses "Comptech V2.1" as a worked example but states:
> "The principles are the same, it's just the names and functions that are different from program to program."

All the FC-family editors (including DMC) share this architecture:

### Song arrangement
- Divided into **Tracks** (typically 3, one per SID voice) and a **Sector** (block) list
- Track arranger maps sectors to play positions
- Commands: `$A0` = loop, `$FF` = end, `$EF` = init; can also transpose a sector

### Sector / Block commands
- Commands are prefixed with `.` (dot); notes are entered as `C-0` through `H-7` (note + octave)
- `.SND #nn` — select sound patch nn
- `.DUR #nn` — set duration/speed (number of frames per row); value > $7F wraps/reverses
- `.GLD` / `.SLD` — glide/slide (portamento); e.g. `.GLD C-3 C-5 $5C` = glide from C3 to C5 at speed $5C
- Up to **six effects per line** possible (vs. two in a typical tracker)
- More effects per line = higher raster time cost

### Sound patch definition (waveform/envelope)
Fields observed in the worked example:
- **Waveon** — waveform byte with gate-on bit (e.g. `$41` = pulse + gate)
- **Waveon Frames** — how many frames the waveon state rings (e.g. `$04`)
- **Waveoff** — waveform byte with gate-off (e.g. `$40`)
- **Attack/Decay** — combined ADSR byte 1 (e.g. `$0E`)
- **Sustain/Release** — combined ADSR byte 2 (e.g. `$EA`)
- **Pulse modulation** — 5 fields: pulse start, add amount, add rate, subtract amount, subtract rate
  (e.g. start `$41`, add `$A4`, hold `$12` frames, fall fast, fall `$12` frames)
- **FX byte / vibrato** — e.g. `$02` for light vibrato

### Packing
- Editors export raw "unpacked" data with lots of zero padding
- Packer removes unused data, packs track data and wavetables
- Some editors export to TurboAssembler (TASM) format for manual inspection/optimization

---

## Editors Mentioned (with raster time context)

| Editor | Raster Time | Notes |
|--------|-------------|-------|
| DMC V4 | Good (later versions) | Most used DMC version, user-friendly |
| Future Composer V4.1 | "Not the best" | Improved editor functions, faster packer vs older FC |
| FCS Future Composer 00.18 V1.0 | — | Finnish Cracking Service hack of Charles Deenen's (Maniacs of Noise) player |
| Sync V1.02/V1.44 | Excellent (very little) | Made by The Syndrom; quality with low raster time |
| RoMuzak V6.3 | — | Advanced Sector/Commands; considered "the composer" |
| 20CC editor | — | Unofficial FC-based frontend hacked from the 20CC player |
| Comptech V2.1 | — | Used as the worked example; can export to TASM |

---

## Historical Context

- DMC and Future Composer were direct competitors in the C64 demoscene
- Larger groups (e.g. Finnish Cracking Service) customized players/editors for their own needs
- Competition drove optimization: shorter raster time was a status symbol
- The FC lineage traces back to Charles Deenen / Maniacs of Noise (the original music routine)

---

## Site Structure (no dedicated DMC page found)

The site has no dedicated DMC sub-page. All DMC content is on the SID Editors page. Other SID-related pages on the site:
- `https://sidpreservation.6581.org/sid-editors/` — Editor overview (this source)
- `https://sidpreservation.6581.org/sid-trackers/` — Tracker overview
- `https://sidpreservation.6581.org/sid-preservation/` — SID preservation methods

No search result for `site:sidpreservation.6581.org DMC` returned additional dedicated pages.

---

## Wayback Machine Snapshot History (editors page)

Most relevant snapshots:
- 2024-11-13: https://web.archive.org/web/20241113150429/https://sidpreservation.6581.org/sid-editors/
- 2024-07-20: https://web.archive.org/web/20240720154259/https://sidpreservation.6581.org/sid-editors/
- 2023-09-22: https://web.archive.org/web/20230922113525/https://sidpreservation.6581.org/sid-editors/
- 2018-07-16: https://web.archive.org/web/20180716030321/http://sidpreservation.6581.org/sid-editors/

Content appears stable between 2023 and 2024 (same hash for Jul/Nov 2024 snapshots).
