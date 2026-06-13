# GMC / Superiors — DeepSID Labeling and Population Analysis

**Provenance:** Static analysis of local DeepSID source tree
(`tmp/dmc_hunt/DeepSID/`) and read-only queries against `hvsc84.db`.
No web fetches performed; DeepSID source is a local checkout.
Date: 2026-06-13.

---

## 1. DeepSID sidid Integration

DeepSID uses its own bundled sidid at `utility/sidid_100/`. The active config is
`sidid.cfg` (the newer variant without `END` terminators). The GMC entries in DeepSID's
config are **byte-identical** to all other copies (see `sidid_signature_analysis.md`).

DeepSID therefore labels GMC tunes using exactly the same two signatures as sidid:
- `GMC/Superiors` — V1 (all years)
- `GMC_V2.0/Superiors` — V2.0 (2010–2023 only)

No additional version tags beyond V2.0 have been detected in any of the five sidid.cfg
copies. There is no `GMC_V1.0/Superiors` label — the base `GMC/Superiors` entry IS V1.

---

## 2. No GMC-Specific PHP/JS Logic Found

A search of `tmp/dmc_hunt/DeepSID/php/` and `tmp/dmc_hunt/DeepSID/js/player.js` for
"GMC", "Game Music", and "Superiors" returned no hits in PHP files and one irrelevant
index.php hit (a URL template, not GMC-specific). DeepSID treats GMC as a pure sidid-
classified engine — no special rendering, subtune routing, or version-specific UI code.

---

## 3. GMC / DMC Relationship in DeepSID Config

In DeepSID's `sidid_100/sidid.cfg`, the GMC and DMC entries are listed in the same
file at lines 728–531 (GMC at ~728, DMC at ~510). Both are present as separate engine
entries with no explicit cross-referencing. The file order is alphabetical.

DeepSID would label a SID as either GMC or DMC based solely on which signature matches
— there is no explicit "GMC is a predecessor to DMC" annotation in DeepSID's tooling.

---

## 4. Population Summary (hvsc84.db, read-only)

### 4.1 Total Counts

| Engine label | Count |
|---|---|
| `GMC/Superiors` | 446 |
| `GMC_V2.0/Superiors` | 9 |
| **Total** | **455** |

### 4.2 PSID vs RSID

All 455 tunes are PSID version 2 header format.
- `GMC/Superiors`: 442 PSID (`is_psid=1`), 4 RSID (`is_psid=0`)
- `GMC_V2.0/Superiors`: 9 PSID (all)

The 4 RSID tunes all have `play_addr=0` (no IRQ vector declared), which is typical for
tunes that use a real CIA timer and self-install their IRQ handler. All 4 are from
1990–1993:
- `Andy/I_Like_It.sid` (1990 Graffity, init=$5000)
- `DOS/Delame_93_tune_3.sid` (1993 Lethargy, init=$9400)
- `DOS/Mistery_Arts_Intro.sid` (1992 Mistery Arts, init=$9440)
- `PVCF/Hamburger_Special_Happy_PVCF-Mix.sid` (1993 BBP/Reflex, init=$8F00)

### 4.3 Init/Play Address Distribution (GMC/Superiors V1)

Three clusters account for 96.4% of V1 tunes:

| Cluster | init | play | Count | % |
|---|---|---|---|---|
| **Dominant** | $18EA | $14EA | 289 | 64.8% |
| **Canonical** | $1000 | $1003 | 114 | 25.6% |
| Other relocations | various | various | 43 | 9.6% |

**Dominant cluster ($18EA/$14EA):** The player is loaded at $14EA (play entry) with
init at +$0400 = $18EA. This is a 1024-byte player image. Brian's own 1990 Graffity
tunes (33 SIDs) are 100% in this cluster, as is the majority of pre-1995 material.
This represents the **native player address as distributed by Graffity/Superiors**.

**Canonical cluster ($1000/$1003):** Play at $1003, init at $1000 (init is 3 bytes
before play — the init entry is a JMP to the actual init routine at $1000+3). This is
the "clean" PSID convention where the player is relocatable and the PSID header uses
$1000 as a standard entry. First seen 1990 (1 tune), predominant in 1991–1993, still
in use through 2024. This layout accounts for the majority of international (non-
Hungarian) GMC users.

**Note on $1000/$1003 vs $18EA/$14EA:** The PSID's `init_addr` and `play_addr` fields
may have been set by the HVSC submitter or extraction tool, not necessarily by the
original SID image. Both clusters share the same underlying GMC player binary; the
difference is where the binary was loaded and what address the PSID header declares.

**GMC_V2.0 addresses:**
- $1000/$1003: 7 tunes (dominant, all 2010–2021)
- $5000/$5003: 1 tune (2010, Wacek)
- $1B90/$1B93: 1 tune (2023, NecroPolo — unusual offset)

### 4.4 Init-to-Play Offset Analysis

| Offset (init - play) | Count | Interpretation |
|---|---|---|
| +$0400 (1024) | 314 | Player is 1024 bytes, init at top |
| −$0003 (−3) | 122 | init is 3 bytes before play (JMP stub) |
| +$0003 (+3) | 3 | play is 3 bytes before init (reversed; possibly PSID typo) |
| Other (incl. 0) | 7 | Relocations / RSID with play=0 |

The 3 tunes with offset +3 (init > play by only 3 bytes) are unusual:
- `Marbloid_preview.sid` (1993, Ati, init=$EE03, play=$EE00)
- `Dark_Caves.sid` (1994, Zimmermann, init=$2E83, play=$2E80)
- `Sword_of_Honour.sid` (1992, Ziphoid/Carehag, init=$6C55, play=$6C52)

These have the pattern init = play + 3, which is the exact **inverse** of the canonical
$1000/$1003 convention (play + 3 = init vs canonical init + 3 = play). This may indicate
PSID header fields were swapped, or that these tunes use a different calling convention
where the 3-byte entry stub is at the play address and the init routine is just above it.

### 4.5 Subtune Distribution

| Subtune count | SID count |
|---|---|
| 1 | 422 (94.6%) |
| 2 | 5 |
| 3 | 8 |
| 4 | 2 |
| 5 | 5 |
| 7 | 1 |
| 8 | 1 |
| 11 | 1 |
| 14 | 1 |

**GMC is overwhelmingly single-subtune** (94.6%). The GMC editor's "8 tunes per file"
capacity is rarely used in HVSC — most SIDs contain exactly one tune. The 14-subtune
outlier is `Zimmermann_Jan/Mystery.sid`; 11-subtune is `NecroPolo/Geister.sid`.

### 4.6 PSID Speed Bit

All GMC SIDs in HVSC are PSID header version 2. No `speed` bit analysis was done at
the column level (the DB schema doesn't expose the raw PSID speed dword separately from
`is_psid`). However, the 4 RSID entries with `play_addr=0` are equivalent to speed=CIA
in effect. The remaining 451 are standard VBI-driven (50 Hz play call via PSID vector).

### 4.7 Authors and Era

Top 5 authors by SID count:
1. Adam Waclawski (Wacek) — 96 SIDs
2. Ádám Papp (Paco) — 35 SIDs
3. Balázs Farkas (Brian) — 33 SIDs (the engine creator)
4. Rene Griebel (Bleed Into One) — 32 SIDs
5. Péter Nagy-Miklós (NecroPolo) — 31 SIDs (+ most V2.0 authorship)

Primary scene origin: **Hungarian demoscene** (Graffity, 1990). Rapidly adopted across
Central/Eastern European groups (Yugoslavia: Chaos/String; Poland: MPC Digital, Wacek;
Germany: Ass It/Lehmann, Creatures/Griebel). Still actively used as of 2024.

Primary years: 1990–1994 peak, with significant Arise-group activity through 1997–1998
and a revival cluster from Arise and NecroPolo in 2009–2014.

### 4.8 File Location Distribution

| HVSC directory | SID count |
|---|---|
| MUSICIANS/ | 428 |
| DEMOS/ | 15 |
| GAMES/ | 3 |

GMC is nearly exclusively a **music composer** tool (MUSICIANS/ = 94%), with minimal
game or demo integration. This contrasts with DMC, which has significant GAMES/ and
DEMOS/ penetration.

### 4.9 Songlength Distribution

| Duration bucket | Count |
|---|---|
| < 1 minute | 83 (18.6%) |
| 1–5 minutes | 342 (76.6%) |
| 5–10 minutes | 19 (4.3%) |
| > 10 minutes | 2 (0.4%) |

Longest: `Brian/Music_Pack_1.sid` (831s = 13.8 min, 1990 Graffity) — a compilation
pack with one subtune containing a long medley. Second longest: `NecroPolo/Geister.sid`
(681s = 11.4 min, 11 subtunes).

---

## 5. GMC / DMC Relationship in DeepSID Data

DeepSID labels these as entirely separate engine families. From the HVSC population
perspective:
- GMC/Superiors: 455 SIDs, all classified by the GMC signature
- DMC: 10,676+ SIDs, classified by the DMC V4/V5/V6 signatures

No SID in hvsc84.db is simultaneously tagged GMC and DMC. The two engines have
**disjoint** sidid signatures (confirmed by the structural analysis in
`sidid_signature_analysis.md`). DeepSID would never show a GMC tune as DMC or vice versa.

---

## Leads to follow

- **V2.0 distributor:** NecroPolo authored 5/9 V2.0 tunes (including 2023 LHS releases).
  Check CSDb for a "GMC V2.0" tool release or NecroPolo tool upload around 2010.
- **Wacek's V2.0 tune** (`Forgotten_short_version.sid`, 2010) uses $5000/$5003 — atypical
  for V2.0; whether this is an independent V2.0 tool instance or a relocated copy of
  NecroPolo's V2.0 player is unknown without binary inspection.
- **The 43 "other relocation" V1 tunes** span 1990–2016. Some may use the GMC editor's
  relocation feature; others may be PSID conversion artifacts. The $A8EA/$A4EA cluster
  (6 tunes) and $E8EA/$E4EA cluster (5 tunes) suggest specific relocated play addresses
  that are systematically offset from $14EA by multiples of $3000 and $D000 respectively
  — worth checking if these are all from the same group/era.
- **PSID speed bit for CIA-timed GMC tunes:** The 4 RSID/play=0 tunes may use CIA timer
  rather than VBI. Confirming this (and whether the GMC player itself supports CIA-speed
  or relies on the host) is relevant to the `verify_all` CIA-path coverage question.
- **Multi-subtune handling:** Does GMC use a single player with a subtune index passed
  in A on init, or does it store multiple independent tune headers? This determines
  whether multi-subtune SIDs need special extract handling.
