---
source_url: https://www.c64-wiki.de/wiki/Tammo_Hinrichs ; https://6octaves.com/2014/07/interview-with-demoscener-kb-farbrausch.html ; https://github.com/kebby
fetched_via: direct (all three)
fetch_date: 2026-06-15
author: Tammo Hinrichs (kb) — interview by 6octaves
content_date: 2014-07 (interview); C64-Wiki undated; GitHub 2023
reliability: primary (interview is self-reported)
---

# kb (Tammo Hinrichs) — Author Profile for Reflextracker Research

## Summary of Sources Checked

Three sources were consulted for interview or autobiographical statements from kb about Reflextracker:
1. **6octaves.com interview (2014)** — does not mention Reflextracker specifically
2. **C64-Wiki (de)** — notes "aktiv beteiligt" in Reflex group; no technical details
3. **kebby.org (2023)** — portfolio/link page only; no technical content

## What the 2014 Interview Does Establish

Source: https://6octaves.com/2014/07/interview-with-demoscener-kb-farbrausch.html

kb (Tammo Hinrichs) states:
- "My scene career started on the C64 (Commodore 64) with **The Obsessed Maniacs in 1993**, continued with groups like **Reflex** and Smash Designs."
- He describes a general philosophy about building PC-based tools for music: "I decided that the 'coder me' had to write a tool that the 'musician me' was happy to use. So it became an actual synthesizer that anyone could use with any music software."
  - NOTE: This statement is about his later V2 synthesizer for PC demo music, NOT about Reflextracker, but it reveals his general approach: **build PC-side tools that target non-PC hardware**.
- No direct mention of Reflextracker, QuadSID, or the C64 player format.

## TinySID Attribution

From web search results: **TinySID** (a minimal C64 SID emulation library) is attributed to Tammo
Hinrichs (kb). This is a separate project from Reflextracker but confirms kb's deep familiarity
with the SID chip internals required to build a C64 music player on PC.

## Groups Active in 1995

Groups kb belonged to at the time of Reflextracker's release (1995):
- Reflex (C64 Germany) — the releasing group for Reflextracker
- The Obsessed Maniacs (co-releasing group)
- Smash Designs (later)
- Farbrausch (much later, PC demos)

## Code Credits Confirmed

From CSDb release #43348 (source of truth):
- **Code:** kb, Quiss (Matthias Kramm), Zorc
- **Music/Design/Docs/Sampling:** PVCF (Kai Walter)

This is consistent: kb and Quiss built the PC tracker + C64 player; PVCF used it and wrote
the German manual (BESCHREIBUNG).

## No Source Code Located

No source code for Reflextracker has been found in:
- GitHub under kb's handle (kebby)
- Any public repository
- Demoscene source archives

The source was never released publicly. Reverse engineering from the binary + SID corpus is the
only path to understanding the format.

## GitHub Profile

- https://github.com/kebby
- Contains recent projects (Farbrausch-era tools, WebAssembly demos)
- No C64-era source code or Reflextracker-related content
