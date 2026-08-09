---
source_url: local: /home/jtr/sidfinity/hvsc84.db (read-only), /home/jtr/sidfinity/hvsc85/DOCUMENTS/STIL.txt, /home/jtr/sidfinity/hvsc85/DOCUMENTS/Musicians.txt, /home/jtr/sidfinity/hvsc85/DOCUMENTS/hv_sids.txt
fetched_via: local read
fetch_date: 2026-06-15
author: HVSC #84 maintainers
content_date: HVSC #84
reliability: primary
---

# Reflextracker — HVSC Corpus Census

## Summary

- **Total HVSC members:** 137 SIDs
- **PSID version:** All 137 are PSID v2
- **Subtunes:** All 137 have exactly 1 subtune
- **Multi-SID (PSID v3+):** None (no 2SID or QuadSID SIDs in HVSC)
- **Pipeline status:** None migrated (pipeline=NULL for all 137)

## Per-author counts (HVSC `author` field)

| Count | Author |
|-------|--------|
| 23 | Piotr Grabowski (Warlock) |
| 13 | Radoslaw Staszak (Data) |
| 12 | Jaroslaw Kotlinski (JFK) |
| 11 | Grzegorz Struminski (Gregfeel) |
| 9 | Róbert Tihanyi (Mephisto) |
| 7 | Tomasz Szymczak (Randy) |
| 7 | Krzysztof Cybura (Mini Cat) |
| 6 | Manik |
| 6 | Kai Walter (PVCF) |
| 4 | Pawel Ruczko (H.M.Murdock) |
| 3 | Sebastian Zelek (Cliff) |
| 3 | Michal Kirsz (Killer) |
| 3 | Krzysztof Cybura (The Spear) |
| 3 | Gábor Pogonyi (Jonny) |
| 3 | Aleksander Marchwiak (Leming) |
| 2 | Wojciech Wardynski (Praiser) |
| 2 | Szymon Kedzia (Stice) |
| 2 | Piotr Grabowski (CJ Warlock) |
| 2 | Pawel Mach (Rea) |
| 2 | Krzysztof Cybura (Vegeta) |
| 1 each | Zsolt Kajtár (Soci), Warlock & Killer, Tomasz Sobierajski (Alg), The Bisel, Szymon Kedzia (Stice) & Micro, Stefan Sebastian (Brizz), Marek Murawski (Copieya), Kamil Wolnikowski (Jammer), K. Cybura & Jaroslaw Kotlinski, Jaroslaw Kotlinski & K. Cybura, Clemens (Quasar), Claudius Henrichs (Flip), Bartek Wilk (Bax), <?> |

The corpus is primarily **Polish demoscene composers** (1995–2008). The original Reflex group authors (PVCF/Kai Walter) account for only 6 SIDs; the tracker spread most heavily in Poland.

## Songlength distribution

| Bucket | Count | Range |
|--------|-------|-------|
| < 30s | 4 | 14–26s |
| 30–60s | 7 | 35–54s |
| 1–2 min | 50 | 64–119s |
| 2–5 min | 67 | 120–260s |
| > 5 min | 9 | 300–431s |

Median ~2 min. The majority (67+9=76) are 2+ minutes — these are real digi songs, not short jingles. Warlock's "Xtraterrestrial" (362s) and "Raving" (377s) are the longest.

## File size distribution

| Bucket | Count | Range |
|--------|-------|-------|
| 10–20 KB | 32 | 12–19 KB |
| 20–30 KB | 35 | 20–29 KB |
| 30–40 KB | 28 | 30–39 KB |
| 40–50 KB | 41 | 40–49 KB |
| > 50 KB | 1 | 51 KB |

Large files (40–50 KB): samples dominate. SIDs include player + sample data + song data all concatenated in one binary.

## Release year distribution

| Year | Count |
|------|-------|
| 1994 | 2 |
| 1995 | 5 |
| 1996 | 16 |
| 1997 | 39 |
| 1998 | 28 |
| 1999 | 18 |
| 199? | 8 |
| 2000 | 5 |
| 2001 | 6 |
| 2002 | 4 |
| 2003 | 1 |
| 2006 | 1 |
| 2007 | 1 |
| 2008 | 3 |

Peak: 1997. Active use continued through 2008.

## PSID address distribution

| init_addr | play_addr | Count | Notes |
|-----------|-----------|-------|-------|
| $C006 | $0000 | 130 | Standard layout — player at $C000, init entry $C006 |
| $C050 | $0000 | 3 | PVCF early songs (Gubber, Trance 202, Originalzak) |
| $C000 | $0000 | 1 | PVCF's very first song (Access Denied intro) |
| $C103 | $0000 | 1 | PVCF's Brainbeat 3 Introrap |
| $CF40 | $0000 | 1 | Manik / I Love Punk (init at $CF40 — unusual, player relocated?) |
| $1C06 | $0000 | 1 | Jonny / Future Come — **outlier: player NOT at $C000** |

**All 137 have play_addr=0** — the player installs its own CIA2 IRQ. PSID emulators call init() once; the player installs the CIA IRQ vector and never returns a playback entry point to the PSID wrapper.

### Address outliers

**$C006 (n=130) — dominant standard:** Player loads at $C000. First 6 bytes ($C000–$C005) appear to be the JMP table (2 × 3-byte JMP instructions: JMP $C02C and JMP $C016, confirmed in player binary). Init entry is at $C006 = the setup routine that installs CIA2 timer + IRQ.

**$C050 (n=3) — PVCF early variant:** Same player, different layout in data. The 3 SIDs (Gubber, Trance 202, Originalzak) are all 1995 PVCF compositions included in the Reflextracker v1.1 distribution disks. The higher init address suggests either a slightly different player build or that $C006–$C04F is occupied differently (larger init stub).

**$C000 (n=1) — PVCF's very first:** Access Denied (intro) is identified in STIL as the first song made with the tracker ("3–4 hours to compose this track in our new developed and finished Reflex-Tracker"). The PSID init at $C000 instead of $C006 suggests an early version before the $C006 convention was established.

**$C103 (n=1) — Brainbeat 3 Introrap:** Same author (PVCF). Unusual address; may be a different build configuration or the init stub is at $C103 for some structural reason in this song.

**$CF40 (n=1) — I Love Punk (Manik, 1997 Amnesia):** The player appears relocated or replaced; at $CF40 the standard player would be at $C740, near the end of the normal $C000–$C7FF region. This may be a re-packed or differently assembled variant.

**$1C06 (n=1) — Future Come (Jonny, 1997 Ideal):** The init at $1C06 places the player at $1C00, not $C000. **This is the only non-$Cxxx player.** The file is 40,703 bytes (largest non-Manik file). This is likely a completely relocated player build. SIDId still matches because the signature pattern is location-independent.

## STIL findings

No Reflextracker-specific technical STIL comments found except for PVCF's own tunes. The Polish scene users have only titles/credits, no technical annotations. No STIL entry mentions "QuadSID" or multi-SID for any of the 137 corpus members.

## Multi-SID / QuadSID in HVSC

**Zero PSID v3+ entries** in the Reflextracker corpus. The tracker's QuadSID capability (up to 10 channels) is NOT represented in HVSC — the forum discussion confirms "QuadSID songs cannot be easily converted to standard formats since they use four SID chips simultaneously" and "must run the assembled executable" (PRG files), not .sid files. The HVSC corpus consists entirely of standard 3-voice tunes or 2-digi-voice tunes remixed to fit the player's 2-channel architecture.

### Related: Data/Banditti_2SID.sid

This SID (PSID v3, attributed to "Comer/Sample_Studio" engine) is in the Data folder but is NOT a Reflextracker file — different engine classification.
