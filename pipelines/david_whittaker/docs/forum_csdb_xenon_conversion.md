---
source_url: https://csdb.dk/release/?id=233756
fetched_via: direct (WebFetch 2026-06-17)
fetch_date: 2026-06-17
author: Bansai (CSDb user; Lemon64 user "Bansai")
content_date: 2023-07-12
reliability: primary (author's own release notes describing their conversion method)
---

# CSDb: Xenon (ZX128 conversion) by Bansai (2023)

Full URL: https://csdb.dk/release/?id=233756

This C64 SID is a conversion of David Whittaker's ZX Spectrum 128K music for
Xenon (Bitmap Brothers, 1988). Highly relevant: the author (Bansai) performed
an **automatic** ZX128→C64 format conversion, exposing the structural similarity
between Whittaker's ZX and C64 data formats.

---

## Release details

- **Type:** C64 Music
- **Released by:** Bansai
- **Date:** 12 July 2023
- **Downloads:** Xenon_ZX128.sid (185), Xenon_ZX128_.prg (115)

---

## Bansai's technical notes (from release comments, exact quotes)

> "Subsong and track pointers are the same exact format as C64."

> "Looking at the patterns, song pattern data is very close to C64 with some minor
> differences."

> "Pattern commands were parsed and converted automatically."

> "Arpeggio tables, glides, and vibrato passed right through to the C64."

> "I theorised that Whittaker used an assembler-based mostly compatible macro
> command structure across platforms enabling easy song data portability."

---

## Extraction method

Bansai extracted the ZX Spectrum 128K song data from a **hacked aylet emulator**
on Linux. Aylet is a Z80/AY-3-8910 emulator; by instrumenting its memory, Bansai
captured the live song data structures at runtime.

---

## Structural conclusions from the conversion

| Data | ZX Spectrum 128K | C64 |
|------|-----------------|-----|
| Sub-song pointer table | Identical format | Identical format |
| Track pointer sequences | Identical format | Identical format |
| Pattern command bytes | Near-identical; Spectrum missing SID-waveform commands | Full command set |
| Arpeggio tables | Present; identical | Present; identical |
| Glide/portamento data | Present; identical | Present; identical |
| Vibrato data | Present; identical | Present; identical |
| End-of-pattern byte | $87 (ZX) | $88 (C64) |

**Minor differences**: ZX Spectrum lacks C64-specific waveform select commands
($8A noise, $8B pulse, $8C saw, $8D tri, $8E flag, $8F pulsehi, $92 ring-tri,
$93 sync-square). Everything else maps 1:1. The conversion replaced ZX end markers
($87) with C64 end markers ($88) and stripped/added waveform commands as needed.

---

## Community response

**iAN CooG** (HVSC committee, SIDId author, `sidid.cfg` contributor):
> Questioned whether it was "automatic conversion of some sort" or manual recreation,
> noting the quality suggests an original composition.

This confirms that the automatic conversion produces output audibly indistinguishable
from a Whittaker C64 original — validating the structural compatibility.

**blitzed:** Contrasted Xenon's ZX128 "ear-bleed" (AY chip) favorably against
the C64 version done by Paul Tonge (not Whittaker).

**ChristopherJam:** "Nicely reconstructed Whittaker composition."

---

## Bansai's Lemon64 forum post (related)

In the Lemon64 thread https://www.lemon64.com/forum/viewtopic.php?t=81385 (July 2023):

> "His players between Spectrum and C64 were quite compatible with the Spectrum
> missing commands here and there for the additional SID waveforms among other
> things, but nothing that was a dealbreaker with getting a reasonable conversion.
> All the usual Whittaker arpeggios tables and such are there in the Spectrum data."

> "I have full player source/song data for Xenon [offered via PM]."

> "Data conversion isn't size optimized and can be improved a lot, broken into
> separate memory regions."

Also mentions a successful conversion of Platoon (another Whittaker ZX128 title):
> "Command sets from both Xenon and Platoon were ported to C64 players with very
> little difficulty and sound like native C64 tunes."

---

## Implications for C64 driver migration

1. The Whittaker cross-platform macro system is so consistent that ZX→C64 is
   automatable without manual rearrangement.
2. Arpeggio tables have the same byte layout on ZX and C64 (confirmed).
3. Voice pointer + track sequence tables have identical layout.
4. Only SID-specific waveform commands need platform mapping; all other pattern
   data is portable.
5. Glide (portamento) and vibrato parameters are identical in size and layout.

---

## Leads to follow

- Bansai's Lemon64 profile: search for "Bansai" on lemon64.com — offered full
  Xenon source via PM (could be a second Whittaker disassembly)
- Platoon ZX128 conversion: Bansai mentioned this also works; could be another
  source for format validation
- Source code of the automatic converter: not publicly released; PM Bansai on
  Lemon64 or CSDb
- CSDb Bansai scener page: search csdb.dk for user "Bansai" to find other releases
