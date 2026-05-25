---
source_url: https://www.vgmpf.com/Wiki/index.php?title=Clever_Music
         + https://www.vgmpf.com/Wiki/index.php?title=Jay_Derrett
fetched_via: WebFetch
fetch_date: 2026-05-25
author: Video Game Music Preservation Foundation wiki editors
content_date: ongoing
reliability: secondary
---

# Companion ancestry — who wrote what

## Clever Music (company)

- British music house: Robert Hartshorne (front of house) + **Graham Jarvis**
  (the "electronics whizz").
- Did radio/TV jingles AND C64 game soundtracks.
- **Graham Jarvis "expanded The Companion to the Commodore 64."** (VGMPF Clever
  Music page, verbatim.)
- Clients/games scored: Wizardry, **Gyroscope**, **Fairlight**, Space Doubt,
  **Back to the Future**, **Blade Runner**, Tubular Bells, Shao-Lin's Road,
  Soundwave — all the SIDs sidid tags `Companion` or `Companion/Jay_Derrett`
  under `MUSICIANS/C/Clever_Music/`.
- The wiki says Steven Chapman, Jay Derrett and probably John McPhee
  "reprogrammed it their own way" — so there are AT LEAST 3 known forks of the
  Companion player beyond the Murray base.

## Jay Derrett

- Born ~1967-68, British, hired by CRL Group (Clem Chambers) in July 1984
  while still a teenager.
- **Did NOT write the Companion driver himself.** Per VGMPF: Clever Music
  pitched score writing for CRL games using their own sequencer; Chambers
  "asked [Derrett] to write some technical interfaces and SID drivers" to
  convert Clever Music's compositions into C64 game code. When Clever Music
  was overloaded, Derrett took over as main tune writer.
- His ~20 known C64 SIDs in HVSC under `MUSICIANS/D/Derrett_Jay/` all tag as
  `Companion/Jay_Derrett` — meaning his "technical interfaces and SID drivers"
  WERE the Companion player with Derrett's specific front-end re-write (the
  `AND #$0F, ASL, TAY` nibble-indexed double-table lookup signature).
- Games composed by Derrett (Lemon64 / VGMPF): Spindizzy (US version), Death
  or Glory, The Rocky Horror Show, Blade Runner, Dracula, Ninja Hamster,
  Mandroid, Sqij, Osmium, Discovery, Stratton, Road Warrior, Trigger Happy,
  Counterforce, Thundercross, ZIP, Destruct, Jetboys, Equalizer, Traxxion,
  Lifeforce, Vengeance. (Note: 1xn.org and forum threads suggest Derrett
  dislikes his own compositions in retrospect.)

## "Murray" identification

The `Companion/Murray` sub-tag refers to **Chris Murray** (Henry's House,
English Software, 1984). Murray was 16 when he wrote Henry's House. The
"Companion" book by Keith Bowden (Pitman, 1984) contained a music driver as
example code; Murray adapted it, Jarvis expanded it for C64, Hubbard borrowed
it (1984), and Clever Music's composers each forked it for their own use. The
CSDb ice00 comment quoted in `csdb_csm_commodore_music_examples_driver.md`
confirms the Murray-origin lineage with the 423 Hz A4 tuning fingerprint.

## Three known forks of Companion in HVSC

| Sub-tag                  | Front end re-write                        | Voice/waveform tail               | Composers using it                |
|--------------------------|-------------------------------------------|-----------------------------------|-----------------------------------|
| `Companion` (base)       | various                                   | `BC ?? ?? C8 98 9D 04 D4 60`      | Hubbard, Berry, Hoernell, Clever  |
| `Companion/Murray`       | wrap on Y=$80, restart on Y=$FF           | same `9D 04 D4 60` tail           | Hubbard (Up_up_and_Away)          |
| `Companion/Jay_Derrett`  | `AND $0F, ASL, TAY, B9..B9..` double-LUT  | (front-end-only signature)        | Derrett's 20 SIDs, Raeburn 1 SID  |

Steven Chapman's and possibly John McPhee's forks are not separately
signatured in sidid.cfg as of today — they presumably hit the base `Companion`
match.
