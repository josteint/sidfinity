---
source_url: local: /home/jtr/sidfinity/hvsc84.db + /home/jtr/sidfinity/hvsc84/ SID headers
fetched_via: local read
fetch_date: 2026-06-15
author: HVSC #84 / SIDId classification
content_date: 2024
reliability: primary
---

# OdinTracker HVSC Corpus Analysis

## Corpus size

**159 SIDs** in HVSC #84 classified as OdinTracker.

## PSID version

All 159 are PSID v2.

## Top authors

| Author                              | Count |
|-------------------------------------|-------|
| Otto Järvinen (SounDemoN)           | 50    |
| Michal Hoffmann (Smalltown Boy)     | 22    |
| Factor6                             | 16    |
| Antti Mäkynen (Monk)                | 14    |
| Robert Dörfler (LordNikon)          | 13    |
| Ahti                                | 10    |
| Joel Toivonen (hukka)               | 6     |
| Marcin Romanowski (Sidder)          | 4     |
| fieserWolF                          | 4     |
| Jericho Swathe                      | 3     |
| Others (10 authors)                 | 17    |

Note: Author "Zoltan Konyha (Zed)" does NOT appear directly in HVSC SID author
metadata — Zed was the tracker author, not a composer using his own tracker.
No hits for "odin", "zoltan", "konyha", "zed" in Musicians.txt, hv_sids.txt,
STIL.txt, BUGlist.txt, or Creators.txt.

## Year distribution (from `released` field)

| Year  | Count |
|-------|-------|
| 2000  | 76    |
| 2001  | 28    |
| 2002  | 8     |
| 2003  | 10    |
| 2004  | 18    |
| 2005  | 11    |
| 2006  | 4     |
| 200?  | 1     |
| 2010  | 1     |
| 2012  | 1     |
| 2019  | 1     |

Peak usage in 2000, which aligns with OdinTracker 1.00 release (Feb 2000).

## Subtune counts

| Subtunes | Count |
|----------|-------|
| 1        | 145   |
| 2        | 9     |
| 3        | 2     |
| 4        | 2     |
| 6        | 1     |

The 6-subtune SID is `MUSICIANS/J/Jammer/Lemmings_II_Tunes.sid`.
Multi-subtune songs use the `SONGSTARTTABLE` mechanism (one start orderlist
position per subtune, up to 256 max per the defines). Jump with effect Bxx loops.

## Songlength distribution

| Bucket | Count |
|--------|-------|
| < 1 min | 11   |
| 1–3 min | 79   |
| 3–5 min | 41   |
| > 5 min | 28   |

Typical lengths: 80–250 seconds. Longest: SounDemoN/Tomhet (1664 s, 2 subtunes).

## Load/Init/Play address relocation

### Primary cluster (dominant)

| Init addr | Play addr | Count | Notes |
|-----------|-----------|-------|-------|
| $1000     | $1003     | 126   | Default relocation (79.2%) |
| $4000     | $4003     | 7     | Ahti's songs (7 SIDs) |
| $6FE8     | $6FF4     | 4     | SounDemoN Nine_Inch_Ninjas (unusual init≠play-3) |
| $6000     | $6003     | 3     | LordNikon (3 SIDs) |
| $5000     | $5003     | 2     | Finnr + LordNikon |
| $A00      | $A03      | 2     | SounDemoN Lemmings + Mirror_Sound |
| $BFF0     | $BFF3     | 2     | SounDemoN Arpeggioland + Firelord_old |
| various   | —         | 13    | Scattered (see full list below) |

All `load_addr` values in DB are 0 — load address is embedded as the first two
bytes of the SID data block (the standard PSID convention for load_addr=0).

The standard init/play offset is exactly 3 bytes apart ($1000/$1003, $4000/$4003,
etc.) matching the JMP table at vplayer start:
```
$xx00: JMP player_init
$xx03: JMP player_play
$xx06: JMP player_stop
```

### Anomalous entries

- `$3180` init / `$1003` play (Come_Along.sid): player relocated to $1000,
  init routine elsewhere (init body not at standard offset).
- `$FF0` init / `$1003` play (CiaTno.sid): init just before $1003.
- `$3803` init / play=0 (Dirt_Ball.sid): RSID format, play=0 (uses its own IRQ).
- `$9600` init / play=0 (Gods_preview.sid): RSID format, play=0.
- `$A29` init / `$A67` play (Whirl.sid): non-standard offsets, unusual build.

### RSID entries (play_addr=0)

Two SIDs are RSID (Real SID) format with play=0:
- `MUSICIANS/S/SounDemoN/Dirt_Ball.sid` — RSID v2, flags=$14, init=$3803
- `GAMES/G-L/Gods_preview.sid` — RSID v2, flags=$14, init=$9600

These install their own IRQ handler rather than using the standard PSID call model.

## CIA-timed entries (speed bit set)

Only **1 SID** has speed bit set:
- `MUSICIANS/S/SounDemoN/CiaTno.sid` — PSID v2, speed=$1 (CIA-timed), flags=$34

156 SIDs are VBI-timed (speed=0), 2 are RSID (IRQ-driven).

## HVSC documentation notes

No mention of OdinTracker, Zed, Zoltan Konyha, or related terms found in:
- `DOCUMENTS/STIL.txt` — no STIL entries for OdinTracker tunes
- `DOCUMENTS/Musicians.txt` — no entry for Zed/Konyha
- `DOCUMENTS/hv_sids.txt` — no references
- `DOCUMENTS/BUGlist.txt` — no known bugs listed
- `DOCUMENTS/Creators.txt` — no entry

## Key HVSC paths for test SIDs

Good test targets (varied features, single subtune, known authors):
- `MUSICIANS/S/SounDemoN/Martin_Hubbabubba.sid` — 2 subtunes, official tracker demo
- `MUSICIANS/F/Factor6/Frozen_Fish.sid` — canonical early Factor6 tune
- `MUSICIANS/M/Monk/Beyond_Fluctuation.sid` — longer tune (279 s)
- `MUSICIANS/H/Hoffmann_Michal/Nukes_Jaguar_XJ220.sid` — 4 subtunes
- `MUSICIANS/J/Jammer/Lemmings_II_Tunes.sid` — 6 subtunes (most subtunes in corpus)
- `MUSICIANS/S/SounDemoN/CiaTno.sid` — CIA-timed (only one in corpus)
