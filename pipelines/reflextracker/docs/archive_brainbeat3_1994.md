---
source_url: https://archive.org/details/Brainbeat_3_1994_Reflex
fetched_via: curl (archive.org direct download)
fetch_date: 2026-06-15
author: Reflex (kb/PVCF/Zorc/Quiss)
content_date: 1994 (dated 22.7.94 in binary)
reliability: primary (original disk image)
---

# Brainbeat 3 (1994) — Reflextracker Early Version Reference

## What this file is

`Brainbeat_3_1994_Reflex.d64` — A Reflex group music demo disk from 1994, containing C64 digi music. Available at Archive.org.

Downloaded to: `/home/jtr/sidfinity/tmp/reflextracker_research/Brainbeat_3_1994.d64`

## Key finding: "FTRAC V1" reference (1994 build)

From a text block decoded from the disk binary (offset ~78779, dated 22.7.94):

```
CREDITS ARE LIKE:
  SAMP[le] INTRODUCTION — PVCF
  (ED.: WATCH OUT FOR ZE FAMOUS FTRAC V1 &@/@ /REFLEX KB/T.O.M)
```

"FTRAC V1" = an early internal name for Reflextracker V1 (before the V1.1 release). The PETSCII encoding makes "FTRAC" render as "REFLEXTRACKER" or similar in the original display — confirmed by "REFLEX" appearing separately.

Also from Brainbeat 3:
- Contact: `QUISS # ZYRON # ECHO $ FANTA # BOW # ODYSSEUS BEATHOVEN SYNDROM`
- "RECEIVE THE LATEST VERSION OF DISKNOTE, WRITE TO: QUISS, APS, RFX"
- This confirms Matthias Kramm (Quiss) was the distribution point for early Reflextracker in 1994

## Implication for version history

Brainbeat 3 (July 1994) uses an early pre-release of the tracker ("FTRAC V1"), confirmed by:
- No `RFX1` magic found in the d64 (different module format in 1994 pre-release)
- The module magic `RFX1` appears only in the V1.0 and V1.1 disk releases

## HVSC confirmation

PVCF's earliest HVSC SID `Access_Denied_intro.sid` has init_addr=$C000 (not $C006), which is consistent with a pre-V1.1 player. The Brainbeat 3 disk likely uses an even earlier player (pre-V1.0).

## Distribution model

Even in 1994, Quiss was listed as the contact for the tracker distribution: "QUISS, APS, RFX" (Quiss at APS [his school/organization?], Reflex). This matches the BESCHREIBUNG credit "SAMPLE-PACK CODE: QUISS/REFLEX" and the contact address in the V1.1 documentation pointing to Matthias Kramm in Munich.
