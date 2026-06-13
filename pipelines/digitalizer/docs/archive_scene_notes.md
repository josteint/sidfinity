---
source_url: multiple — CSDb, Recollection, Demozoo, disk image strings, archive.org
fetched_via: direct (WebFetch + WebSearch + curl extraction) 2026-06-13
fetch_date: 2026-06-13
author: synthesised from scene sources
content_date: 1989–2023
reliability: secondary (synthesis); primary for disk image quotes
---

# Digitalizer — Norwegian C64 Scene Context and Network Notes

## Norwegian C64 Scene Ecosystem (Digitalizer-relevant subset)

### Groups connected to Digitalizer development

```
Prosonix ──────────────────────────────────────────────────────────────────┐
  Lars Hoff                                                                │
  Ole-Marius Pettersen                                ← SteinTronic        │
  Stein Pedersen ←── borrowed editor → Olav Mørkrid                       │
                                                                           │
Mozicart ──────────────────────────────────────────────────────────────────┤
  Geir Tjelta ─── "helpful discussions" ← Olav Mørkrid                    │
  Trond Lindanger                     ↓                                   │
                              Digitalizer V2.2 (1989)                     │
                                                                           │
The Shadows ───────── Omega Supreme/Olav ──────────────────────────────── │
Rawhead ─────── early groups before Panoramic Designs                     │
                                                                           │
Panoramic Designs (1990) ──────────────────────────────────────────────── │
  Olav Mørkrid (coder, Digitalizer)                   ← Prosonix overlap  │
  Bjørn Røstøen (coder)                                                   │
  Stein Pedersen (musician, PD from 1990)                                 │
  Richard Nygaard (graphician)                                            │
  Henning Rokling (musician)                   → Digitalizer V2.5–V3.0   │
  Lars Hoff (musician) ──────────────────────────────────────────────────┘
  Ole-Marius Pettersen (musician)
                              ↓
                      Digitalizer V3.0 (1992)
                      ← Funcom co-founded 1993 (Olav leaves active C64 dev)
                              ↓
                       SHAPE / Blues Muz' collaboration
                         6R6 (GRG) ──── credited V2.2+V2.5 (1989)
                         Kjell Nordbo ─ SHAPE from 1990
                              ↓
                      Digitalizer V3.5 (1995) — GRG + Kjell re-assembly
                              ↓
                      SID Duzz' It (SDI) ─ GRG + Geir Tjelta (2001+)
                              ↓
                      DTZ2SDI Converter ─ DJ GRUBY/TRIAD (2023)
```

---

## Norwegian Scene Geography Note

From Recollection #2 interview:
> "Norway is extremely long" — Olav Mørkrid on why cross-group collaboration was difficult.

The key groups were geographically distributed:
- **Oslo area:** The Shadows, Rawhead, United Norwegian Crackers, Panoramic Designs (main), Stein Pedersen's circle
- **Megastyle:** Northern Norway (rivals of Panoramic in the early 1990s — "quite childish from both sides")
- **Bergen:** Glenn Rune Gallefoss (6R6/GRG) and Geir Tjelta (SHAPE) — this is why Mozicart/SHAPE collaboration was notable despite the distance

The Oppegård postal code (N-1415) from V3.0 help text places Olav south of Oslo.

---

## The Prosonix Connection (Critical Lineage)

From Recollection #2 interview (Olav Mørkrid, Recollection vol. 2, interviewer Jazzcat):

Olav admitted to using Stein Pedersen's music editor as a "freeze backup" — meaning he froze the running program with a cartridge (Action Replay or similar), extracted the binary, and studied/copied the code.

This is confirmed by the V3.0 help file (1992):
> "I would like to thank prosonix for inspiration (vi kaller det herming!)"
— "herming" = Norwegian slang for copying/mimicry, used self-deprecatingly

The sequencing:
1. Stein Pedersen writes the **Prosonix Music Editor** (aka SteinTronic, CSDb ID 179618) — pre-1989
2. Olav freeze-backs it → uses it as base for Digitalizer V2.1/V2.2 (1989)
3. Stein Pedersen later joins Panoramic Designs (1990) — by then Digitalizer is V2.8
4. As of June 1992 (V3.0 help), Stein is still a Prosonix member AND Panoramic member, listed in Olav's hire roster

**Implication for format RE:** The earliest Digitalizer format (V2.2) may share structural DNA with Prosonix Music Editor. If Prosonix's format is known, it could accelerate Digitalizer V2.x RE. The Prosonix editor CSDb page (179618) is a priority target.

---

## The GRG / 6R6 Early Credit Mystery

Glenn Rune Gallefoss is credited as `-GRG-` in both V2.2 (1989) and V2.5 (1989) disk images.

His official scene database membership (CSDb, Demozoo) shows:
- SHAPE: August 1990–2005
- Blues Muz': 1994–2011

He was NOT officially in Panoramic Designs, and not in Blues Muz' until 1994. Yet he appears in the Digitalizer disks in 1989.

**Possible explanations:**
1. **GRG contributed music** to the demo/example data included on the Digitalizer editor disks. The `-GRG-` credit is for a song, not for editor code.
2. **GRG was in an early unlisted group** (he had many affiliations: Calix, Collision, Digital Designs, Foxbat, Kraftverk, Pandora, The Freaks — most undated).
3. **GRG was known locally** as a Bergen musician and Olav included one of his songs as a demo tune.
4. **Pre-scene-database activity** — before CSDb systematically tracked group membership, collaborations happened informally.

The V2.2 intro string `-GRG-` (not a credit sentence, just a handle tag) suggests a song attribution rather than a code credit. The V3.5 editor binary "2085 V3.5 BY GRG" is unambiguously a code credit.

---

## The Mozicart Circle

Mozicart was a Norwegian music group active circa 1990–1993. Members include Geir Tjelta and Trond Lindanger (both acknowledged in Digitalizer V3.0). Mozicart later became part of SHAPE.

From sidid.cfg: there is a separate "Mozicart" player signature (not fetched this session). Mozicart's player is distinct from Digitalizer's player. The two groups shared musical knowledge (hence Olav's "helpful discussions" acknowledgment) but maintained separate tools.

Geir Tjelta later co-authored SID Duzz' It (SDI format) with Glenn Rune Gallefoss — connecting the Mozicart → SHAPE transition to the SDI ecosystem that later received the DTZ2SDI Digitalizer converter.

---

## SID Duzz' It (SDI) Format Relationship

SID Duzz' It is a separate C64 music editor/tracker with:
- **Authors:** Geir Tjelta + Glenn Rune Gallefoss (6R6/GRG) of SHAPE
- **First version:** ~2001–2002 (V1.3, April 2001 on Demozoo)
- **SourceForge:** maintained by "glennrg64" (Glenn's SourceForge handle)
- **CSDb:** V2.1.7 (2014) = CSDb ID 133692

**SDI features (from SourceForge documentation):**
- 3-channel music tracker + 4th control channel (tempo/transpose/effects)
- 32 tunes, 128 sequences, 32–48 instruments
- 48 arpeggios, 85 vibrato programs, 64 filter programs, 64 pulse programs, 48 tempo programs
- 11-bit filter capability
- Effects: vibrato, pulse, filter, arpeggio, tempo

**Format description (from Lemon64 forum):**
SDI saves as PRG with player + data combined. "DUMP" mode saves data only (without player). To produce a .sid file: use dump mode → Turbo Assembler to compile with player → save as binary → rip to .sid. The source player code is modifiable to omit unused features.

**DTZ2SDI converter (2023, by DJ GRUBY / TRIAD):**
Converts Digitalizer V3.x format to SDI. The disk image strings confirm:
- "COMPLETELY AUTOMATIC" conversion
- Requires loading Digitalizer music into RAM first
- Only one music bank in use at a time
- The `$30` constant may set C64 memory banking ($30 = %00110000 = RAM visible at $A000+$E000)

The existence of this 2023 converter confirms that as recently as 2023, there are composers still wanting to migrate from Digitalizer V3.x to the more modern SDI format.

---

## Wayback Machine — Failed / Blocked URLs

The following were attempted but returned errors (Wayback blocked):
- `web.archive.org/web/*/panoramic-designs.com`
- `web.archive.org/web/19990201000000*/panoramic-designs.no`
- (All web.archive.org URLs returned "Claude Code is unable to fetch from web.archive.org")

No alternative mirrors of Panoramic Designs or Olav Mørkrid personal pages were found. The ExoticA wiki page (exotica.org.uk) returned a browser verification block.

---

## Archive.org Items Found

Direct archive.org searches found:

| Item | URL | Content |
|------|-----|---------|
| Bluez Muz Intro 1994 (Shape) | archive.org/details/Bluez_Muz_Intro_1994_Shape | 707KB d64; code+music by 6R6 (1994 demo intro) |
| 82 Ditties (Blues Muz' & SHAPE) | archive.org/details/82_c64 | 4.2MB d64; 73 files; Blues Muz comp (2006) |

Neither item contained Digitalizer-specific documentation, but both confirm the Blues Muz'/SHAPE music circle that inherited the Digitalizer ecosystem.

---

## Norwegian Demoscene Scene Structure (1989–1995)

From Recollection Crackers' Map (Norway):

Major Norwegian cracking/demo groups in the Digitalizer era:
- **Abnormal** (est. June 1988 → disbanded 1989 → folded into Illusion)
- **Illusion** (est. 1989 → disbanded 1993) — "Scandinavia's #1"
- **Jazzcat Cracking Team** (1986–1987)
- **Raw Deal Inc.** (1986–1991)
- **Razor 1911** (est. 1985; reborn on Amiga 1987)
- **Panoramic Designs** (est. 1989–1990 → present) — the Digitalizer group
- **Megastyle** — northern Norway; rivals of Panoramic ("quite childish from both sides")

The Norwegian scene was small enough that key figures (Olav, Stein, Geir, Glenn) all knew each other and cross-collaborated extensively. Panoramic Designs' emphasis on design + real names was a deliberate differentiation from the cracking-oriented groups.

---

## Leads to Follow

1. **Prosonix Music Editor (SteinTronic) — CSDb ID 179618** — fetch the release page, download the disk image, extract strings. This is the probable ancestor of Digitalizer V2.2.

2. **Mozicart sidid signature** — sidid.cfg likely has a "Mozicart" entry. Fetching it would show format overlap or divergence with Digitalizer.

3. **HVSC STIL.txt comments on Blues Muz / Glenn Gallefoss tunes** — STIL (SID Tune Information List) often has composer notes like "made with Digitalizer V3.0". The Glenn Gallefoss HVSC directory has 154 tunes. STIL entry for these tunes may document which editor version was used. STIL.txt is at https://www.hvsc.c64.org/ or Sannic mirror.

4. **Recollection diskmag disk image** — Recollection is a scene diskmag; it may have a CSDb entry. If a D64 version exists, the Olav Mørkrid interview text would be available verbatim (rather than through WebFetch which is limited by copyright restrictions).

5. **DJ GRUBY / TRIAD identity** — The DTZ2SDI converter author "DJ GRUBY / TRIAD" is unknown beyond this credit. Triad is a Swedish C64 group (https://csdb.dk/group/?id=... Triad). This suggests a non-Norwegian contributed the 2023 converter, motivated by a desire to rescue Digitalizer compositions into SDI format.

6. **6R6 Soundcloud** — https://soundcloud.com/glennrg-2 — Glenn Gallefoss's current music page. May have biographical notes or comments about his Digitalizer/C64 history. Not fetched this session.

7. **Notemaker V7.2 (1992) by Kjell Nordbo** — This utility (listed in Kjell Nordbo's CSDb credits) is separate from Digitalizer but contemporary. If it's a music-related utility, it may use similar patterns or data formats. CSDb search for "Notemaker V7.2" would clarify.

8. **OmegaSupreme_Digi sidid entry** — already documented in `github_sidid_signature.md` and `csdb_version_differences.md`. The `STA $01` bank-switch in this entry deserves RE attention: it may explain how Digitalizer accesses sample data across C64 memory banks, which would be confirmed by the DTZ2SDI `$30` constant (bank configuration).
