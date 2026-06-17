---
source_url: local: /home/jtr/sidfinity/hvsc84/DOCUMENTS/ (Musicians.txt, hv_sids.txt, STIL.txt, BUGlist.txt, HVSC.txt, Songlengths.md5, Creators.txt)
fetched_via: local read (grep)
fetch_date: 2026-06-17
author: HVSC Team
content_date: HVSC #84 (2025)
reliability: primary
---

# SidWinder — HVSC Documentation Findings

## Summary

HVSC classifies 117 SID files as engine "SidWinder" via the sidid classifier.
The files live under five artists in the MUSICIANS/ tree:

| Artist dir | Count |
|---|---|
| Factor6    | 38 |
| Luca       | 25 |
| Taki       | 21 |
| Eclipse    | 19 |
| PCH        |  5 |
| Zapac      |  4 |
| Puterman   |  4 |
| Phobos     |  1 |

**Total: 117** (from `hvsc84.csv`; `sidid_full.txt` independently shows 119 — minor delta likely from DB vs sidid-batch differences).

## hv_sids.txt

`hv_sids.txt` contains zero lines matching "SidWinder". It has a different
classification scheme from Musicians.txt; the engine tags are from a separate
sidid run populating the second column of Musicians.txt / sidid_full.txt.

## Musicians.txt / sidid_full.txt

The second column of HVSC's Musicians.txt (engine) is populated by sidid.
Representative entries:

```
MUSICIANS/L/Luca/Enterprise.sid                  SidWinder
MUSICIANS/L/Luca/Little_Sara_Sister.sid          SidWinder
MUSICIANS/F/Factor6/Wind_to_Your_Mind.sid        SidWinder
MUSICIANS/F/Factor6/Settlers.sid                 SidWinder
MUSICIANS/T/Taki/Victory.sid                     SidWinder
MUSICIANS/T/Taki/Agricola.sid                    SidWinder
...
```

All 21 Taki MUSICIANS/T/Taki/ SIDs carrying a SidWinder classification are listed
in `hvsc84/DOCUMENTS/Songlengths.md5`. Their titles include: Agricola, Bastard_tune_2,
Black_Art, Classical, Craft, Damnation, Dankos_Remix, Draxish, Drummer, Foolish,
For_Skyhigh, Funshine, Glorious, Gossip_Column series, Happiness, Hopeless,
Immortal, Improving, Impulse, Introduce, Just_4_Fun, Lost_Love, Memories,
Mr_Thomas, Out_of_Time, Precisely, Prince_of_Persia_1, Proof, Radiation,
Realbeat, Revive, Reynbow, Save_Me, Southern, Speed_Up, Surprise, Uncertain,
Victory, Weird_Dreams.

(Not all Taki SIDs are SidWinder — his earliest works predating the engine are
classified differently.)

## STIL.txt

Zero mentions of "sidwinder", "natural beat", or "taki" in `STIL.txt`.
Taki's entries in STIL.txt are absent (no STIL annotations for his files).

## BUGlist.txt, HVSC.txt, Creators.txt, Disclaimer.txt

Zero mentions of "sidwinder" or "natural beat" in any of these documents.

## Update files (.hvs)

Zero mentions of "sidwinder" or "natural beat" in any HVSC update announcement
files (Update01.hvs through Update84.hvs).

## Songlengths.md5

`Songlengths.md5` contains HVSC-measured song duration entries for all Taki
files. Cross-reference with `hvsc84.csv` for individual subtune durations.
The file itself carries no engine classification — the "taki" grep here hit only
the comment lines (`;`) above each SID's MD5 block.

## Key observations

- HVSC does not document SidWinder's format in any of its text documents.
- The engine identification is entirely driven by sidid byte signatures.
- Taki composed under SidWinder from at least 1994 (player coded) through the
  late 1990s. Factor6 (Alan Petrik, Czech Republic) is the LARGEST SidWinder
  user in HVSC with 38 classified SIDs.
- Eclipse (Zoltán F. Földi, Hungary) has 19 SidWinder SIDs, some dated as late
  as 2025, confirming the engine is still in active use among the Hungarian/
  Central-European scene decades after its creation.

## Leads to follow

- Factor6's 38 SIDs: investigate whether a specific SidWinder sub-variant or
  version is concentrated there (Factor6 is Czech, not Hungarian — how did
  he adopt the engine?). CSDb scener page: https://csdb.dk/search/?q=factor6&type=scener
- Eclipse's 2025 SIDs: up-to-date engine instances; potentially useful for
  verifying that the V01.22/V01.23 format was not extended for recent releases.
- STIL.txt absence: no per-SID technical notes have been added by HVSC admins
  for any SidWinder tune — contrast with DMC/FC families where STIL often
  records quirks.
