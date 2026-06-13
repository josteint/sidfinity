# Music Assembler — versions, variants & binary fingerprints

> **Provenance**
> - source_url (fingerprints): https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
>   and https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
> - source (HVSC survey): local scan of all 6351 `engine='Music_Assembler'` tunes in `hvsc84.db`
> - fetched_via: direct (raw.githubusercontent.com) + local RE
> - fetch_date: 2026-06-13
> - reliability: HIGH — sidid is Lasse Öörni (cadaver)'s authoritative SID-engine
>   fingerprint DB; the canonical MA fingerprint was independently verified to
>   match the disassembled player. The HVSC offset survey is exhaustive (6351/6351).

This is the priority-3 deliverable: how to tell Music Assembler builds apart, and
what the variant family looks like.

## The MA player family (per sidid.nfo)

All of these share the SAME core player (the `BC ?? ?? C0 FE D0 09 ...` per-voice
decode); the editors differ:

| Name (sidid) | Released | By | Relationship |
|---|---|---|---|
| **Music Assembler** | 1989 | Marco Swagerman (MC) & Oscar Giesen (OPM), The Dutch USA-Team | the original. German commercial edition via Markt & Technik (1990). |
| **Music Assembler/MC** | 1989 | MC | a distinct fingerprint variant of the original player |
| **VoiceTracker (Composer)** | 1991 | Science 451 | "Editor based on the Music Assembler player" |
| **Music Mixer** | 1991 | Pawel Soltysinski (Polonus) / Padua | "Editor based on the Music Assembler player" |
| **DoubleTracker** | 1993 | Polonus / Padua | "Multispeed version of VoiceTracker" — MA player |
| **Ten Tracker** | 1991 | Moog / Keen Acid | "10x speed version of VoiceTracker" — MA player |

So HVSC's `Music_Assembler` engine class is really this whole lineage. A migration
should expect to parameterise the **speed divider** (`+$90` reload constant) and
small layout shifts across these builds rather than treat them as separate engines.

(sidid lists `C64_Speech_System` separately; a web search surfaced a claim that MA
was "probably derived from C64_Speech_System", but sidid does NOT assert that link
and the two fingerprints are unrelated. Treat the derivation claim as unverified
nostalgia, not RE fact.)

## Raw sidid fingerprints (verbatim from sidid.cfg)

`??` = wildcard byte; `AND` = sidid's continuation keyword (treat as a wildcard
for matching). These are scanned anywhere in the loaded image (reloc-invariant
where the bytes are not absolute addresses).

```
Music_Assembler
  BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60 B9 ?? ?? 85

Music_Assembler/MC
  EE 19 D0 20 ?? ?? 4C AND BD ?? ?? 85 ?? BC ?? ?? C8 C8 B1 FA C9 FF D0 02 A0 00 98 9D

VoiceTracker            (variant of Music_Assembler)
  BC ?? ?? C8 20 ?? ?? C9 FF D0 02 A0 00 98 9D AND C8 B1 FA C9 FD F0 01 60 C8 B1 FA

Ten_Tracker             (variant of Music_Assembler)
  CE ?? ?? A2 00 D0 ?? A2 0A

DoubleTracker           (variant of Music_Assembler)
  AD ?? ?? F0 05 A2 00 20 ?? ?? AD ?? ?? F0 05 A2 01 20 ?? ?? AD ?? ?? F0 05 A2 02

Music_Mixer             (variant of Music_Assembler)
  A9 F0 8D 17 D4 29 0F 8D A6

C64_Speech_System
  A0 ?? A5 ?? 0A 69 00 0A 69 00 85 ?? 29 03 AA ?? ?? ?? ?? ?? ?? BD ?? ?? 8D
```

### Verified matches against the disassembled canonical player ($3000 tune)

- `Music_Assembler` → matches at **base+$91** (the per-voice track-decode entry).
  This is the routine fully disassembled in `archive_player_writemodel.md`.
- `Music_Mixer` (`A9 F0 8D 17 D4 ...`) is *almost* MA's init (MA init does
  `A9 F0 8D 17 D4 29 0F` too), but Music_Mixer then stores the masked resonance to
  zero-page `$A6` (`8D A6 ..`) whereas canonical MA stores it to an absolute work
  byte inside the player. So `8D A6` is a genuine discriminator: Music_Mixer uses
  zero-page work bytes, canonical MA uses in-player absolute work bytes.
- `Music_Assembler/MC` and `VoiceTracker` did NOT match this particular tune —
  they are separate builds (different sequence-fetch loops), as expected.

## HVSC distribution survey (all 6351 Music_Assembler tunes)

Scanned every `engine='Music_Assembler'` SID header + searched each for the
canonical per-voice fingerprint:

- **Format:** 6289 PSID, 62 RSID.
- **Canonical per-voice fingerprint present in 6351 / 6351 (100%)** — confirms the
  whole engine class shares the MA core, and the fingerprint is a reliable detector.
- **Fingerprint offset from load base** (this is the best build discriminator):

  | offset from base | tunes | likely build |
  |---|---|---|
  | `+$91` | 5311 | canonical 1989 MA (the one disassembled here) |
  | `+$B5` | 718 | a shifted build (VoiceTracker / Music Mixer family) |
  | `+$70` | 119 | another build |
  | `+$191` | 43 | larger-header build |
  | `+$B9` | 40 | |
  | `+$71` | 18 | |
  | `+$7D1`, `+$691`, … | <10 each | outliers |

- **Load address** (231 distinct): `$1000` dominates with **4771** tunes, then
  `$C000` (408), `$9000` (83), `$1021` (74), `$0B00` (63), `$8000`/`$5000` (61),
  `$4000` (55), `$7000` (44). Confirms the manual's "$0400–$FF00 relocatable" claim;
  **$1000 is the de-facto default** and the natural target for a first migration.

- **PSID init/play offsets from base** (two big clusters — a real header convention
  split, NOT noise):

  | (init−base, play−base) | tunes | meaning |
  |---|---|---|
  | (`+$00`, `+$03`) | ~3387 / 3313 | header points at the IRQ-installer (init=base+$00, play=base+$03) |
  | (`+$48`, `+$21`) | ~2649 / 2618 | header points at the documented entries (init=base+$48, play=base+$21) |
  | (`+$27`, `+$1C` etc.) | hundreds | minor build/header variations |

  **Implication:** roughly half of HVSC MA tunes set the PSID `init`/`play` vectors
  to the *manual's* entry points (base+$48 / base+$21), and the other half point
  init at the **IRQ-installer** (base+$00) with play at base+$03. Both reach the
  same engine; the difference is whether the tune relies on PSID to set up the IRQ
  or installs its own. A migration must accept BOTH header conventions.

## Practical detection recipe

1. Is engine MA? → search loaded image for `BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60`.
2. Which build? → record the offset of that match from the load base
   (`+$91` = canonical 1989; others per the table above), and check for the
   `Music_Mixer`/`VoiceTracker`/`DoubleTracker`/`Ten_Tracker` discriminator
   signatures above.
3. Header style? → compare PSID `init`/`play` to base: `(+$48,+$21)` = documented;
   `(+$00,+$03)` = self-installing IRQ build.

## Leads to chase

- Acquire the **VoiceTracker / Music Mixer / DoubleTracker / Ten Tracker** editor
  disks (CSDb) to confirm each variant's `+$90` speed-divider and layout shift,
  and to map the `+$B5` / `+$70` / `+$191` offset clusters to named builds.
