---
source_url: https://csdb.dk/release/?id=43348
fetched_via: WebFetch 2026-06-15
fetch_date: 2026-06-15
author: CSDb community
content_date: 1995 (release), 2017 (comment by CJ Warlock)
reliability: primary
---

# Reflextracker — CSDb & Pouet Notes

## CSDb release #43348 — Reflex-Tracker V1.1

**Type:** C64 Tool  
**Year:** 1995  
**Groups:** Reflex, The Obsessed Maniacs  
**Also known as:** Reflextracker

### Credits

| Role | Person |
|------|--------|
| Code | kb (Farbrausch, Reflex, Smash Designs, The Obsessed Maniacs), Quiss (Reflex, The Art Project Studios), Zorc (Reflex) |
| Music | PVCF (Reflex) |
| Design | kb, PVCF |
| Documentation & Sampling | PVCF |

### Demo songs included

1. Access Denied (remix)
2. Gubber
3. Trance 202

### Download links

- `http://csdb.dk/getinternalfile.php/160214/Reflextracker%20v1.1-Reflex-.zip` (286 downloads)
- `http://csdb.dk/getinternalfile.php/185033/Reflextracker_V1.1.zip` (82 downloads)

Both contain two D64 disk images (Side 1: tracker + player + docs + sample drivers + example songs; Side 2: sample library).

### CSDb comment (CJ Warlock, 2017-12-02)

> "I've set the year of release to 1995 (as I'm pretty sure of what I remember) and I've added two SID's that were on the ReflexTracker disk as demo songs"

Note: CJ Warlock added Gubber and Trance 202 to HVSC in 2017. The "Gubber" name may be intentional/joke (vs "Gabber" the music genre).

---

## Pouet.net — Reflex Tracker (#59064)

**URL:** https://www.pouet.net/prod.php?which=59064  
**Type:** Tool  
**Year:** 1995  
**Popularity:** 53%  
**Ranking:** #42635 all-time

### Key pouet comments

- "a 2 channel digi tracker" — confirmed by multiple commenters
- "weird, unruly interface [...] which is tradition on the 64"
- "a multi page instruction note file written in German by PVCF"
- "don't know if anyone besides the reflex guys used it for anything worthwhile" — inaccurate given 137 HVSC SIDs by 34 different authors
- Download mirror at c64.rulez.org (404 at time of check)

---

## Lemon64 forum thread (#4872)

**URL:** https://www.lemon64.com/forum/viewtopic.php?t=4872

### Key technical facts from forum

- QuadSID (QuadRaSID) songs cannot be directly converted to standard .sid format
- Reflextracker supported up to 10 channels with QuadSID hardware ("from 10 channels to 3 channels" conversion mentioned)
- HVSC only contains standard 3-voice / 2-digi-channel arrangements
- Polish scene: "there was a Reflextracker competition in Poland" (Brainbeat musicdisk series)
- A manual exists but "don't ask where" (the BESCHREIBUNG on disk is the manual — German only)
- "should also be a manual for the tracker" — the user didn't know about the BESCHREIBUNG PRG on disk

---

## Lemon64 forum thread (#77549) — Any quad SID demos?

**URL:** https://www.lemon64.com/forum/viewtopic.php?t=77549

Confirms:
- "several 4SID, one 8SID and even one 10SID" demos have been created
- "a ton of 2SID and 3SID" compositions exist
- Multi-SID demos run as executables (PRG files), not .sid files
- PSID format supports up to 3 SIDs via the dataOffset extension field, but HVSC chose not to extend further
- QuadSID hardware: addresses configurable; common = D400, D420, D500, D520

Reflextracker's QuadSID support is thus represented in C64 executables (demos), not in HVSC's SID collection.

---

## KB / Tammo Hinrichs CSDb profile

Search for `csdb.dk "Tammo Hinrichs"` returns SIDs attributed to kb:
- Turrican III Remix (1994, The Obsessed Maniacs) — load=$1000, play=$1003 (NOT Reflextracker engine; different player at $1000)
- 2nd Reality series (1997, Smash Designs) — kb moved on to PC demoscene (Future Crew, Farbrausch)

Reflextracker (1995) was kb's last major C64 contribution before transitioning to PC scene.
