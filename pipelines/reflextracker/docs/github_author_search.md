---
source_url: https://github.com/kebby + https://github.com/matthiaskramm + https://www.quiss.org/legacy.html
fetched_via: direct
fetch_date: 2026-06-15
author: Tammo Hinrichs (kebby), Matthias Kramm (Quiss)
content_date: 2026-06-15
reliability: primary
---

# Author GitHub / Web Search Results

## Tammo Hinrichs ("kb", "kebby") — github.com/kebby

GitHub profile: https://github.com/kebby

Active repositories (pinned):
- **Capturinha** — real-time screen/audio capture for Windows using NVENC (C++)
- **ultimate-launcher** — "run stuff on your C64 with U1541 directly from your Desktop" (C#)
- **RocketNet** — GNU Rocket client (C#)
- **Werkkzeug4** — demoscene tool (C++)
- **pouet-discord-bot** — Discord bot (TypeScript)

**Finding:** No Reflextracker source code or any 1995-era C64 tools on GitHub. The `ultimate-launcher` is a modern C64 integration tool (USB-based), not the tracker. No C64/SID tracker code visible.

Tammo is also co-author of V2 synthesizer (V2/ViruzII): https://github.com/murkymark/v2synth
TinySID SID emulator: the "6510/6581 emulation is based on routines by Tammo Hinrichs (kb)" — used in TitchySID and other projects.

**Conclusion for Reflextracker source:** NOT on GitHub under kebby.

## Matthias Kramm ("Quiss") — github.com/matthiaskramm + quiss.org

GitHub: https://github.com/matthiaskramm
Repos visible: gfxpoly, mrscake, soul_on_fire (4k entry X2024), corepy, gfxmatrix, cagekeeper — no C64 content.

Website: https://www.quiss.org/legacy.html
C64 legacy tools listed:
- **CCC (C64 cross compiler)** — "A c64 cross compiler and bootloader"
- **Starnoter** — disk notes utility
- **LSD (Liquid Sound Designer)** — "A music and sound editor for the 6581 SID chip"

**Finding:** Reflextracker is NOT listed on Matthias's legacy page. His C64 SID tool is "LSD" (Liquid Sound Designer) — a different program. Reflextracker was primarily Zorc + KB code; Quiss contributed the sample-pack code (see MODULE header).

From the ENDLOSCHOOR module header string at $BA58:
"REFLEXTRACKER 0 MODULE (UNPKD)CODE BY ZORC/REFLEX AND KB/T.O.M"
- ZORC = main engine code
- KB = Tammo Hinrichs (The Obsessed Maniacs)
- T.O.M. = The Obsessed Maniacs

From BESCHREIBUNG documentation:
"EDITORCODE: ZORC/REFLEX"
"EDITORDESIGN: PVCF/REFLEX"
"DISK UND OPTIMYZESYSTEM: KB/TOM"
"CODE UND SAMPLEMENUEDESIGN: KB/TOM"
"BESCHREIBUNG: PVCF"
"BEISPIELLIEDER: PVCF"
"SAMPLEPACK CODE: QUISS/REFLEX" ← Quiss did the sample packing code only
"SALES: PVCF/REFLEX"

**Conclusion:** Quiss's contribution was the sample packing/compression subsystem only. Main engine = Zorc + KB.

## VentuzTammoHinrichs — github.com/VentuzTammoHinrichs

Secondary GitHub account for Tammo, used for his Ventuz work (presentation software). No C64 content.
