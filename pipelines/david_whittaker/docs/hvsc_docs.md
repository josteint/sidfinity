---
source_url: local: hvsc84/DOCUMENTS/Update00.hvs, Update02.hvs, Update_Announcements/20020817.txt, Update_Announcements/20240630.txt, STIL.txt
fetched_via: local read
fetch_date: 2026-06-17
author: HVSC Crew (Update files); various HVSC contributors (STIL)
content_date: Update00 ~1997-1999; Update02 ~1999-2000; 20020817 = 2002-08-17; 20240630 = 2024-06-30
reliability: primary
---

# HVSC Documentation — David Whittaker

## Update00.hvs — Initial batch additions

The `Whittaker, David` section records the **first HVSC additions** for this composer
(during the very first or second update cycle, ~1997–1999):

```
Whittaker, David
  Knight Games - (9 tunes) /The Mage
  Super G-Man - /The Mage
```

Rippers credited: "The Mage" (for Knight Games 9-tune SID and Super G-Man).

The `Info` section in the same update lists **known misattributions** to be aware of:

```
Whittaker
  Bosconia - not Whittaker!
  PowerDrift - not Whittaker!
  Prince Clumsy - not Whittaker!
  Robin of the Wood - same as Super Robin Hood
  Shadow - same as Cosmonaut
  Shadow of the Beast - only Amiga version is by Whittaker
  Sonic Graffiti?
```

Key reclassifications:
- **Bosconia** — NOT Whittaker (misattributed in early scene rips)
- **PowerDrift** — NOT Whittaker
- **Prince Clumsy** — NOT Whittaker
- **Robin of the Wood** = same tune as Super Robin Hood (duplicate removed)
- **Shadow** = same tune as Cosmonut (duplicate — note: HVSC uses "Cosmonut" spelling)
- **Shadow of the Beast** — only the Amiga version is by Whittaker; the C64 version is different
- **Sonic Graffiti** — flagged with `?` (uncertain attribution, likely not Whittaker)

## Update02.hvs — Iron Horse re-attribution

```
\games\euro_g-l\ironhors.dat
David Whittaker
```

This records that `Iron_Horse.sid` (originally in a games subfolder, `ironhors.dat`)
was re-attributed to David Whittaker during Update02. No technical notes; just a
credit correction.

## Update_Announcements/20020817.txt — Back in Time Live 3

Whittaker mentioned in a non-technical context as a performer at the Back in Time
Live 3 concert event:

```
* Live performances from ... David Whittaker, Richard Joseph and Ben Daglish
  as compere for the evening's live shows
```

No technical driver information in this file.

## Update_Announcements/20240630.txt — Prg2Sid 1.20 adds "2 variants"

HVSC Update 81 (June 30, 2024) includes release notes for **Prg2Sid 1.20** by
iAN CooG (CSDb release ID 238521):

```
Since 1.15 the following has been changed:
...
- new players identified:
  DMC 4.x patched (only those needing a patch at $0ff9)
  Anvil
  Whittaker (2 variants)
```

**Significance:** Prg2Sid is a tool that attaches PSID headers to raw game music
rips — it identifies players and sets `init/play` addresses, patching the header
and code as needed. Adding "Whittaker (2 variants)" in Prg2Sid 1.20 (released
2024, after 30+ years) means that previously-unripped Whittaker games were being
ripped for HVSC, and Prg2Sid needed to handle two distinct driver layouts to
correctly set the PSID header fields.

The **2 variants** here refer to 2 binary layouts that Prg2Sid must identify and
patch, not necessarily 2 musically distinct engine families. The most likely
interpretation (based on binary analysis below) is:
- **Variant A** — the dominant layout (79 SIDs): uses `DEC abs` to decrement a
  duration counter (`CE ?? ??`) followed by `STX $D404` gate-toggle sequence
- **Variant B** — the alternate layout (10 SIDs): uses `STA $D406` then `LDX abs`
  + `STX $D404` gate-toggle sequence (different register-write ordering)

See `sidid_signature.md` for the full binary analysis.

## STIL.txt — No per-tune technical notes

The STIL has **no entries** in the `/MUSICIANS/W/Whittaker_David/` section
(the section header exists but no COMMENT/TITLE/ARTIST annotations for
his own tunes). STIL mentions "David Whittaker" only as an artist credit
for cover tunes by other composers.

The one Whittaker-related STIL note of interest is for a **Demos** SID:
```
/DEMOS/G-L/Lazy_Jones.sid
  TITLE: Lazy Jones, Tune #21
 ARTIST: David Whittaker
COMMENT: This tune was later used in the dance hit "Kernkraft 400", by Zombie Nation.
```

This confirms the Lazy Jones tune #21 is the "Kernkraft 400" hook.

## Database cross-check — HVSC attribution vs sidid detection

From the local `hvsc84.csv` database:

| Category | Count |
|---|---|
| SIDs under MUSICIANS/W/Whittaker_David/ | 103 |
| Detected as `David_Whittaker` by sidid | 95 |
| Detected as `David_Whittaker` in other folders | 15 |
| Total `David_Whittaker` engine detections | 110 |
| SIDs in Whittaker folder with NULL engine | 8 |

The 8 NULL-engine SIDs in the Whittaker folder are a **database artefact**, not
a genuine detection failure: 7 of the 8 (`4_Soccer_Sims_Soccer_Skills`,
`All_Terrain_Vehicle_Simulator`, `Buffalo_Bills_Wild_West_Show`,
`Lone_Wolf_the_Mirror_of_Death`, `Professional_Snooker_Simulator`,
`Trantor_The_Last_Storm_Trooper`, `War_Cars_Construction_Kit`) match P1 in
direct binary search. The DB was built with an older sidid run that apparently
had a bug or different config for these files.

The one genuine outlier is **Exorcist.sid** — a small (1471 bytes) player that
does NOT match any of the 5 sidid signatures. Analysis shows it is structured as
a data-heavy player that writes only to V2/V3 registers (no $D404 gate writes
at all), and has a different architecture than the standard Whittaker driver.
May be a special-purpose player written for the Exorcist game rather than the
canonical Whittaker engine.

## Leads to follow

- `hvsc84/DOCUMENTS/Update33.hvs` — 100 mentions (2002 era mass re-rip of Whittaker
  back-catalogue; confirm if it contains any technical notes beyond the SID listing)
- `hvsc84/DOCUMENTS/Update25.hvs` — 30 mentions (possible batch re-rip)
- CSDb release 238521 (Prg2Sid 1.20 by iAN CooG) — download the .7z to read the
  full changelog; the 2-variant description may have more detail inside
- CSDb release for Prg2Sid v1.25 (posted June 2025, comment by iAN CooG on
  release 238521) — may refine the variant definition further
