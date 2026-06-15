---
source_url: multiple — Wayback Machine (web.archive.org), c64.rulez.org, hornet.org, quiss.org, kebby.org
fetched_via: curl + Wayback CDX API
fetch_date: 2026-06-15
author: various
content_date: 1996–2026
reliability: primary (direct downloads), secondary (Wayback snapshots)
---

# Reflextracker — Archive.org / Wayback / Scene Mirror Research

## Summary of findings

No PC-side Reflextracker executable exists in any known public archive. **Reflextracker is a C64-native tracker (runs on Commodore 64), NOT a PC cross-tool.** The confusion in the research brief comes from the demoscene context: "PC cross-tracker" is a misclassification. It composes C64 digi music on the C64 hardware itself.

---

## Scene Mirror: c64.rulez.org

URL: `http://c64.rulez.org/pub/c64/Demos/t/The_Obsessed_Maniacs/Tools/`

Directory listing (fetched 2026-06-15):
```
Reflextracker_Player_V1.1[sys49158].zip   2001-05-18   1.5K
Reflextracker_V1.1.zip                   2001-05-18   196K
```

Both files **confirmed downloaded** to `/home/jtr/sidfinity/tmp/reflextracker_research/`.

### Reflextracker_Player_V1.1[sys49158].zip

Contains: `Reflextracker Player V1.1 (SYS 49158) [Reflex + TOM].t64` (T64 tape image, 2144 bytes)

The T64 file contains one entry: `RFXT PLAYER V1.1` — exactly 2048 bytes of player code.

**Player binary analysis:**
- Load address: $C000
- Total size: 2048 bytes → player occupies $C000–$C7FF
- First instructions:
  ```
  $C000: 4C 2C C0   JMP $C02C   ; init dispatch
  $C003: 4C 16 C0   JMP $C016   ; play dispatch
  $C006: 78         SEI          ; init entry point (SYS 49158 = $C006)
  $C007: A9 36      LDA #$36    ; banking: RAM+I/O
  $C009: 85 01      STA $01
  $C00B: 20 2C C0   JSR $C02C   ; clear SID + setup CIA
  ```
- Confirmed identical to the `RFXT PLAYER V1.1.prg` extracted from the D64 disk image
- SYS 49158 = SYS $C006 = confirmed standard init address

**Saved to:** `/home/jtr/sidfinity/tmp/reflextracker_research/rfxt_player_v1.1_from_t64.prg`

---

## Wayback Machine: Hornet Archive

URL: `https://hornet.org/cgi-bin/scene-search.cgi?search=reflextracker`

Result: **0 matches** — Reflextracker is not in the Hornet Archive.

The Hornet Archive search for "reflex" returns 12 results, none of which are the C64 tracker:
- Music by "KB, Reflex" (Reflex PC demogroup, 1995): `rainsymp.zip` — unrelated Amiga/PC music
- Graphics by "Felijae of Reflex": `mek-26.zip` — also unrelated

---

## Wayback Machine: reflex-studio.de

Earliest archived snapshot: 2000-12-19 (`20001219235900`)
URL: `http://web.archive.org/web/20001219235900/http://www.reflex-studio.de:80/`
**Status: Access Denied (server-side restriction preserved in Wayback)**

Archived pages under reflex-studio.de (CDX scan 2000–2013):
```
http://www.reflex-studio.de:80/             (2000-12-19 — Access Denied)
http://www.reflex-studio.de:80/pvcf         (2000-11-18)
http://www.reflex-studio.de:80/pvcf/mp3/    (2001-11)
http://www.reflex-studio.de:80/pvcf/PVCF+main+page.htm  (2001-06 — 404)
http://www.reflex-studio.de:80/rbkey.txt    (2002-04)
http://www.reflex-studio.de:80/robots.txt   (2001-04)
```

**Key finding:** No Reflextracker download page, no tool zip, no documentation page found under reflex-studio.de in Wayback. The site hosted PVCF's music (MP3s via Java applet) and info about the Erasmus project; no tracker distribution.

The rbkey.txt file (2002-04-13 snapshot) was not fetched (likely a text key file for something, not the tracker).

---

## Wayback Machine: kebby.org

Author: Tammo "kb" Hinrichs

Earliest archived snapshot: 2002-03-25
CDX-indexed pages (2002–2006): `home.html`, `demos.html`, `articles/*.html`, `code.html`

**code.html** (fetched 2002-01-21): Content = "not yet" — no code released on the site at that time.

**demos.html** (fetched 2002-01-21): Lists all C64 demos kb produced:
- "1.67 Years" (The Obsessed Maniacs, C64, 1994)
- "F.A.K.E" (C64, 1994) — 6th place, The Party 4
- "J**P!" (C64, 1995)
- "LatX" (C64, 1995) — 2nd place, Wired '95
- "Second Reality 64" (C64, 1997)
- Plus PC/Amiga demos

**Note:** No Reflextracker mentioned on kebby.org, no download link, no documentation. kb did not use his personal site to distribute the tracker.

**Relevant archived articles at kebby.org:**
- `articles/h14a2.html` = "F***ing Learn To Code Again" (demo coding article in Hugi #14) — PC demo scene article, not C64-specific
- `articles/inkb.html` — unknown; not fetched
- `articles/fr08snd*.html` — articles about PC audio in Farbrausch demos

No C64-specific tool documentation or Reflextracker material found.

---

## Wayback Machine: quiss.org

Author: Matthias "Quiss" Kramm

Earliest snapshot: 2001-11-30 (redirected to SWFTools homepage)
CDX-indexed pages: mostly SWFTools (Flash conversion library), Caiviar (Java ISDN library), and other software projects.

**Legacy page** (`quiss.org/legacy.html`, current): Lists C64 projects but NOT Reflextracker. Lists:
- CCC (C64 cross compiler + bootloader)
- Starnoter (disk notes utility)
- LSD (Liquid Sound Designer) — different SID editor

No Reflextracker code, source, or documentation at quiss.org in any Wayback snapshot.

---

## Insider #6 (Reflex Diskmag, 1996)

CSDb: https://csdb.dk/release/?id=5064

Downloaded to: `/home/jtr/sidfinity/tmp/reflextracker_research/insider_06.zip`

Table of contents from D64 binary scan:
```
01. EDITORIAL !
02. NEWS
03. CHARTS
04. INTERVIEW 1
05. INTERVIEW 2
06. THE PARTY 5
07. CONVENTION 96
08. DEMOREVIEWS 1
09. DEMOREVIEWS 2
0A. DEMOREVIEWS 3
0B. MAGREVIEWS
0C. COVERREVIEWS
0D. SPECIAL REVI.
0E. MIXED CHAPT.1
0F. MIXED CHAPT.2
10. TRACKERINSTR.    ← "TRACKER INSTRUCTIONS" — Reflextracker English doc candidate
11. PARTYINVITAT.
12. ADDIES
```

**Chapter 10 ("TRACKERINSTR.")** is a strong candidate for the English Reflextracker documentation promised in the BESCHREIBUNG ("A TRANSLATED VERSION SOON!"). However, the D64 content is stored as C64 machine code display program (BASIC + ML charset renderer), making plain-text extraction unreliable without running the actual C64 software.

The REFLEX-TRACKER reference found at byte offset 57632: "REFLEX-TRACKER Vq.q*" — this is a direct reference within the disk data.

**Recommendation:** Mount insider_06.d64 in a C64 emulator (VICE) and navigate to chapter 10 to read the English Reflextracker instructions.

---

## Files Downloaded

| File | Size | Source | Contents |
|------|------|--------|---------|
| `Reflextracker_Player_V1.1.zip` | 1.5K | c64.rulez.org | T64 with 2048-byte player |
| `reflextracker_rulez_mirror.zip` | 196K | c64.rulez.org | Same D64 as CSDb (side 1+2) |
| `insider_06.zip` | 134K | CSDb #5064 | Reflex diskmag; ch.10=TRACKERINSTR |

---

## Negative findings (confirming no PC tool exists)

1. **Hornet Archive**: 0 matches for "reflextracker"
2. **Scene.org FTP**: No Reflextracker file in browsable archives
3. **kebby.org**: No C64 tools page ("not yet" in 2002)
4. **quiss.org**: No Reflextracker listing (LSD is a different tool)
5. **reflex-studio.de**: Access denied; no tracker download page found
6. **Wayback CDX search for `*reflextracker*`**: Only CSDb and Lemon64 pages
7. **PVCF's own statement**: "reflextracker (PC) song" — PVCF calls it a "PC" tracker because the DESCRIPTION FILE is read/written on PC? Or it may run on C64 but the workflow involves a PC for sample transfer. The BESCHREIBUNG describes running entirely on C64.

**Most likely interpretation:** Reflextracker V1.1 is a native C64 tracker (code on C64 disk, runs on C64). The "PC" description in some sources may refer to sample transfer via Amiga/PC parallel cable (documented in BESCHREIBUNG), not that the tracker itself runs on PC.
