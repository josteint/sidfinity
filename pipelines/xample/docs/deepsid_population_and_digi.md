# X-Ample / Compotech — Population Analysis and Digi Scope

**Provenance:** Queried `hvsc84.db` (SQLite, read-only mode) + direct PSID
header reads from `hvsc85/` SID files. Date: 2026-06-13.
All counts are against HVSC #84.

---

## 1. Population overview

| `engine` value in hvsc84.db | Count | Notes |
|---|---|---|
| `X-Ample` | 380 | Core family — all sub-variants collapsed here |
| `Reflextracker` | 137 | Distinct engine; see §6 |
| `(XTracker_V4.2x)` | 1 | One tune separately tagged |
| `(Compotech_V2.x)` | 0 | sidid sees these as `X-Ample` base in HVSC |
| `(Sonic/SDS)` | 0 | Folded into `X-Ample` by HVSC sidid tagging |
| `(Thomas_Detert)` | 0 | Folded into `X-Ample` |
| `(XTracker_V4.1x)` | 0 | Folded into `X-Ample` |
| `(X-Ample_Digi)` | 0 | No separate tag in hvsc84.db |

**Total X-Ample family (excluding Reflextracker):** 381 tunes (380 + 1).

The sidid sub-variant tags `(Compotech_V2.x)` / `(Sonic/SDS)` / `(Thomas_Detert)`
/ `(XTracker_V4.1x)` are **additional** signatures in sidid.cfg that match
AFTER the base `X-Ample` pattern. HVSC's sidid run has tagged all of them
under the parent label `X-Ample`. The `(XTracker_V4.2x)` exception means
V4.2x matched ONLY its own signature (not the base `X-Ample` one), so it
got a distinct tag. This is an idiosyncrasy of sidid's first-match semantics.

---

## 2. PSID vs RSID split

For `engine='X-Ample'` (380 tunes):

| Type | Count |
|---|---|
| PSID (is_psid=1) | 379 |
| RSID (is_psid=0) | 1 |

The single RSID is:
- `MUSICIANS/S/Schneider_Markus/Hawkeye_II.sid`
  - Markus Schneider (the engine author), 1989
  - init=$6900, play=$0000
  - 18,873 bytes — the largest non-SoNiC X-Ample file
  - 355 seconds songlength

RSID with play=$0000 means the tune is entirely self-playing (it installs its
own CIA/NMI interrupt). This is a special case and likely requires RSID-mode
emulation for correct playback. No other X-Ample tunes are RSID.

---

## 3. CIA-timed (speed-bit set) tunes

**Summary:** 11 tunes have PSID `speed` field != 0 (CIA-timed subtunes).
All 11 are by Tufan Uysal (SoNiC). All are PSID (not RSID).

| Path | speed field | Subtunes | Init/Play |
|---|---|---|---|
| MUSICIANS/S/Sonic/In_Da_Mix.sid | 0x00000001 | 1 | $1800/$1813 |
| MUSICIANS/S/Sonic/B1_rotation_mix.sid | 0x00000001 | 1 | $07F6/$0803 |
| MUSICIANS/S/Sonic/Situations.sid | 0x00000001 | 1 | $2390/$1003 |
| MUSICIANS/S/Sonic/Concussion_in_the_brain.sid | 0x00000001 | 1 | — |
| MUSICIANS/S/Sonic/Side-Kick_salamander_mix.sid | 0x00000001 | 1 | — |
| MUSICIANS/S/Sonic/Man_with_No_Name_culture_mix.sid | 0x00000001 | 1 | — |
| MUSICIANS/S/Sonic/Experimental.sid | 0x00000001 | 1 | — |
| MUSICIANS/S/Sonic/Riff_Raff.sid | 0x00000001 | 1 | — |
| MUSICIANS/S/Sonic/Driss-The_Demo.sid | 0x00000001 | 1 | — |
| MUSICIANS/S/Sonic/Smash_Time.sid | 0x00000003 | 2 | $1FB5/$1FC8 |
| MUSICIANS/S/Sonic/Camel_Dance.sid | 0x00000001 | 1 | $1000/$1003 |

`speed=0x00000001` means subtune 1 is CIA-timed. `speed=0x00000003` means
subtunes 1 and 2 are both CIA-timed. This matches the verify_all CIA-path
(siddump `--writelog-per-irq`). These are **music tunes using CIA for tempo**,
not digi/sample tunes — their SID writes still go to $D400-$D418. They are
NOT out-of-scope; they require the CIA-mode capture path (Mode 1, CIA branch).

---

## 4. X-Ample_Digi scope assessment

The sidid `(X-Ample_Digi)` signature writes CIA1 registers $DD04/$DD05/$DD0E.
**No HVSC tunes are separately tagged as `(X-Ample_Digi)` in hvsc84.db.**

However, tunes using this digi extension may still be tagged `X-Ample` (if
the base signature also matches) or may not appear in the corpus at all (if
they were never submitted to HVSC). The SoNiC CIA-timed tunes above are
candidates — SoNiC is the most likely author to use the digi extension, and
his tunes show atypical init/play addresses and CIA timing.

**Migration scope for X-Ample_Digi:**
- If a tune sets CIA timer registers AND writes sample data to SID voices,
  it falls under Mode 2 (cycle-exact) or is out-of-scope for the standard
  $D400-$D418 frame-by-frame pipeline.
- The 11 CIA-timed SoNiC tunes warrant individual inspection before
  classifying as digi-out-of-scope vs CIA-tempo.
- Conservative estimate: 0-11 tunes may require digi/exclusion treatment.
  The majority (369/380 = 97%) are straightforward VBI PSID.

---

## 5. Init/play address spread

### Dominant cluster: standard $1000/$1003 layout

| Pattern | Count | % of 380 |
|---|---|---|
| init=$1000, play=$1003 | 151 | 39.7% |
| init=$1003, play=$1000 | 35 | 9.2% |
| **Subtotal standard $1000 cluster** | **186** | **48.9%** |

Note: init/play swap ($1000/$1003 vs $1003/$1000) means the two entry
points are 3 bytes apart — the first is the init routine, the second is
the play routine. The swap indicates whether the player was assembled
with init at the lower or higher address.

### Thomas Detert upper-RAM cluster

| Pattern | Count | Author |
|---|---|---|
| init=$A803, play=$A800 | 23 | Detert (17), others (6) |
| init=$B003, play=$B000 | 23 | Detert (21), others (2) |
| init=$AC03, play=$AC00 | 11 | Detert (11) |
| **Subtotal upper-RAM** | **57** | |

Detert's upper-RAM tunes (>= $A000) total 49 entries by him specifically.
These are relocations of the same engine to game-specific memory layouts.

### SoNiC cluster

Most SoNiC tunes land at $1000 (81/123). The remainder scatter across
$6800, $0900, $A000, and unusual multi-bank addresses — consistent with
demos embedding the player at demo-specific locations.

### Full spread (top 20 init/play groups)

| init | play | Count |
|---|---|---|
| $1000 | $1003 | 151 |
| $1003 | $1000 | 35 |
| $A803 | $A800 | 23 |
| $B003 | $B000 | 23 |
| $116C | $09D1 | 12 |
| $AC03 | $AC00 | 11 |
| $680C | $6812 | 8 |
| $2003 | $2000 | 7 |
| $0900 | $0903 | 6 |
| $A000 | $A003 | 5 |
| $E003 | $E000 | 5 |
| $E000 | $E006 | 4 |
| $3003 | $3000 | 3 |
| $07F6 | $0803 | 2 |
| $0D00 | $0D03 | 2 |
| $8000 | $8003 | 2 |
| $9000 | $9003 | 2 |
| $AC00 | $AC03 | 2 |
| $E000 | $E003 | 2 |
| (16 singletons) | | 16 |

**The $116C/$09D1 group (12 tunes)** is entirely by Vincent Merken (Dick).
These are all `MUSICIANS/M/Merken_Vincent/*.sid`. The highly non-standard
addresses suggest a personal modified player with a different memory layout.
All are PSID v2, VBI-timed, 3-6KB.

**All load addresses are $0000** (380/380): every X-Ample SID uses the
PSID "load address from file" convention, meaning the binary is a raw
PRG with the load address as the first two bytes. The actual load target
varies per tune.

---

## 6. Subtune distribution

| Subtunes | Tunes | % |
|---|---|---|
| 1 | 294 | 77.4% |
| 2 | 25 | 6.6% |
| 3 | 9 | 2.4% |
| 4 | 8 | 2.1% |
| 5 | 10 | 2.6% |
| 6 | 9 | 2.4% |
| 7 | 5 | 1.3% |
| 8 | 7 | 1.8% |
| 9 | 2 | 0.5% |
| 10 | 5 | 1.3% |
| 11-14 | 4 | 1.1% |
| 17 | 1 | 0.3% |
| 24 | 1 | 0.3% |

**Total subtunes: 757** across 380 SIDs (avg 1.99/SID).
The 24-subtune SID is `MUSICIANS/S/Sonic/Turrican_3.sid` (42,565 bytes —
the largest X-Ample SID).

---

## 7. Author breakdown (top 10)

| Author | Tunes | Notes |
|---|---|---|
| Tufan Uysal (SoNiC) | 123 | All CIA-timed tunes; largest files |
| Thomas Detert | 92 | Upper-RAM relocation cluster; the Thomas_Detert variant |
| Steven Diemer (A-Man) | 60 | Splits evenly between $1000/$1003 and $1003/$1000 |
| Markus Schneider | 38 | Engine author; includes Hawkeye_II (RSID) |
| Michael Pehl (The Noise Art) | 14 | |
| André Buerger (AEG) | 13 | |
| Vincent Merken (Dick) | 11 | The $116C/$09D1 cluster (all 11 + 1 via other handles) |
| Sanke Michael Choe (SMC) | 5 | |
| Kalle Norrman (Jadawin) | 3 | |
| Benni Pedersen (Emax) | 3 | |

---

## 8. File size distribution

| Size range | Tunes |
|---|---|
| < 4 KB | 151 (39.7%) |
| 4-8 KB | 204 (53.7%) |
| 8-16 KB | 17 (4.5%) |
| 16-32 KB | 7 (1.8%) |
| >= 32 KB | 1 (0.3%) |

The vast majority (93.4%) are small single-song files < 8 KB. The 7
larger-than-16KB files are all multi-subtune compilations by Detert (PP
Hammer, Eskimo Games, Mega Starforce, Tales of Boon) and Schneider
(Stümp, Hawkeye II) or SoNiC (Katakis 3D).

**Total listening time: 29.5 hours** (sum of songlength_s = 106,118 s;
avg = 279 s / SID).

---

## 9. PSID version

All 380 X-Ample SIDs are `psid_version=2`. No v1 or v3 files.

---

## 10. Migration priority

| Scope | Count | Treatment |
|---|---|---|
| VBI PSID, non-digi | 369 | Mode 1 (frame-by-frame) — primary target |
| CIA PSID (speed-bit set) | 11 | Mode 1 with CIA path (writelog-per-irq) |
| RSID, play=$0000 | 1 | Mode 1 or special case; inspect Hawkeye_II |
| Digi CIA writes ($DD04/$DD05) | 0 confirmed (up to 11 to investigate) | Mode 2 or exclude |

**Recommended factory approach:**
- Phase 1: Standard $1000/$1003 cluster (186 tunes, 48.9%) — the highest-
  leverage single group.
- Phase 2: Thomas Detert upper-RAM cluster ($A800/$B000/$AC00, 49 tunes)
  — same engine, different load address; likely handled by relocation
  in the factory.
- Phase 3: SoNiC scatter ($1000 + non-standard, 123 tunes) — includes the
  11 CIA-timed ones.
- Phase 4: Merken $116C/$09D1 cluster (12 tunes) — may need a separate
  player variant due to the non-standard addresses.
- Defer/investigate: Hawkeye_II (RSID), the 11 CIA-timed SoNiC tunes,
  any confirmed X-Ample_Digi tunes.

---

## 11. Reflextracker (not X-Ample)

137 tunes tagged `Reflextracker` in hvsc84.db:
- All RSID (is_psid=0, play=$0000)
- Dominant init: $C006 (130/137)
- Large files: median ~25 KB, consistent with embedded sample data
- Authors: Polish demoscene (Warlock, JFK, Data, Gregfeel, Mephisto, Randy)
- Entirely self-contained digi/MOD players; no relation to X-Ample Architectures
- **Out of X-Ample migration scope entirely**
