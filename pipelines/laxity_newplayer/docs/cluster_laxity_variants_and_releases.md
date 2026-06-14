---
source_urls:
  - "https://csdb.dk/release/?id=26563  (JCH NewPlayer 21.g4 Final, 2006-01-16)"
  - "https://csdb.dk/release/?id=20112  (JCH NewPlayer 21.g4 beta, 2005-08-27)"
  - "https://csdb.dk/release/?id=33785  (JCH NewPlayer 21.g5, 2006-05-09)"
  - "https://csdb.dk/release/?id=101622 (JCH NewPlayer 21.G6 by Samar Productions)"
  - "https://csdb.dk/release/?id=39519  (SID Factory 0.5 alpha 1, 2006-09-02)"
  - "https://csdb.dk/scener/?id=677     (Laxity scener profile)"
  - "https://carol6502.neocities.org/c6_ccutter_guide (CheeseCutter user guide, 'slightly inaccurate' warning)"
  - "https://sidpreservation.6581.org/sid-trackers/ (SID tracker catalogue, Q=quattro definition)"
  - "https://blog.chordian.net/computer-timeline/ (JCH timeline, Laxity/JCH/SF2 dates)"
  - "https://blog.chordian.net/sf2/ (SID Factory II feature log, driver 11.02-11.05)"
  - "https://www.vgmpf.com/Wiki/index.php/Thomas_Petersen (Laxity VGMPF entry)"
  - "local: tmp/dmc_hunt/CheeseCutter/src/c64/player_v4.acme (GPL, verbatim 6502 source)"
  - "local: hvsc84.db (mode=ro; query 2026-06-14)"
  - "cross-reference: pipelines/jch_newplayer/docs/ (READ-ONLY, not duplicated here)"
fetched_via: >
  WebFetch (CSDb direct — most pages returned HTTP 503; responses above came through
  on second attempts or via WebSearch snippets); WebSearch (Google); local READ-ONLY
  on CheeseCutter checkout + hvsc84.db.  CSDb was unreachable for id=101622 and
  id=39519 on first passes; data for those entries is from WebFetch + WebSearch
  snippet synthesis.  Where CSDb was unreachable the entry is flagged MEDIUM reliability.
fetch_date: 2026-06-14
author: Thomas Egeskov Petersen ("Laxity"), Maniacs of Noise / Vibrants; CheeseCutter
  player by Abaddon (Timo Taipalus); SID Factory II by JCH + Laxity + Youth.
content_date: NP21.G4 beta 2005-08-27; NP21.G4 final 2006-01-16; NP21.G5 2006-05-09;
  SID Factory 0.5 alpha 2006-09-02; SID Factory II from 2019 onward.
reliability: >
  HIGH for player_v4.acme content (verbatim local source).
  HIGH for NP21.G4/G5 CSDb release metadata (WebFetch direct, confirmed by WebSearch).
  MEDIUM for NP21.B6 differences (CheeseCutter user guide has a "slightly inaccurate"
  caveat; no original Laxity source obtained).
  MEDIUM for NP21.G6/Samar Productions (CSDb 503; identity from search snippet only).
  HIGH for hvsc84.db population data (direct READ-ONLY query).
  MEDIUM for SID Factory ↔ NP21 lineage (no explicit technical source linking SF
  driver format to NP21; derived from "based on JCH editor by JCH" narrative).
---

# Laxity NewPlayer V21 — Variants, Releases, and Lineage

Focus: the **Laxity-specific layer** that the JCH NewPlayer sweep
(`pipelines/jch_newplayer/docs/`) under-covered.  That sweep documented the
shared NP20/NP21 format, the CheeseCutter source semantics, and the SIDId
taxonomy.  This document adds:

1. The sub-variant sequence within the 21-series (G4 beta → G4 final → G5 → B6)
2. Whether a Q-series multispeed variant exists for NP21
3. Laxity's own releases and the NP21.G5 player download
4. The SID Factory / SF2 lineage question — did NP21 feed into SF2?
5. NP21.G6 by Samar Productions — a third-party fork, not Laxity

Cross-references:
- Shared format spec: `pipelines/jch_newplayer/docs/github_cheesecutter.md`
- SIDId signatures + HVSC population: `cluster_sidid_discrimination.md` (this dir)
- Full effect-chain routines: `cluster_np21_effect_routines.md` (this dir)

---

## 1. The NP21 sub-variant sequence

### 1a. NP21.B4 beta — CSDb #20112 (2005-08-27)

- **Title:** "JCH NewPlayer 21.g4 beta (21.b4)"
- **Author:** Laxity, Maniacs of Noise + Vibrants
- **Downloads:** 2,125
- **Significance:** The **first public NP21 artefact**.  The "b4" in the
  alternate name is the beta build number (not the same grammar as the
  later "B6" suffix — see §1e).

The beta (b4) and the final (G4) appear to share the same G4 player core;
"b4" is a pre-release label, not a generational suffix.

### 1b. NP21.G4 Final — CSDb #26563 (2006-01-16)

- **Title:** "JCH NewPlayer 21.g4 Final" (also "NP21.g4")
- **Author:** Laxity, Maniacs of Noise + Vibrants
- **Downloads:** 2,537
- **Bundled tunes:** three SIDs by Laxity: "21.G4 demo tune 1", "21.G4 demo
  tune 2", "21.G4 demo tune 3" (these are the 4 Laxity-authored
  `Laxity_NewPlayer_V21` entries in HVSC #84 — the 4th is "Ocean Reloaded").
- **Companion tool:** "JCH Editor V3.04 20G4" (user comments recommend pairing).

The CheeseCutter player source (`player_v4.acme`) header reads:
> `;;; Based on JCH NP 21.G4 by Laxity/VIB`

This is the canonical **NP21.G4** — the version CheeseCutter forked.  The
`Laxity_NewPlayer_V21` SIDId signature keys on this player's play-routine
shape (`STA $D404,Y` + `CMP #$FF` + `DEC abs,X`).

**Format break relative to NP20.G4 (the critical table-width change):**

| table | NP20.G4 (JCH) | NP21.G4 (Laxity) |
|---|---|---|
| Pulse rows | 2 bytes | **4 bytes** |
| Filter rows | 2 bytes | **4 bytes** |
| Max instruments | 32 (AA byte $A0-$BF) | **48 (INSNO=48)** |
| Instrument layout | row-major | **column-major** (stride = INSNO) |

These are the same 4-byte table widths used by CheeseCutter — the NP21.G4
format is what HVSC's Laxity_NewPlayer_V21 tunes use (see
`pipelines/jch_newplayer/docs/archive_version_history.md` §3 for the full
field-level byte semantics of those tables).

### 1c. NP21.G5 — CSDb #33785 (2006-05-09)

- **Title:** "JCH NewPlayer 21.g5"
- **Author:** Laxity, Maniacs of Noise + Vibrants
- **Downloads:** 2,791 (the highest of the three NP21 releases)
- **File:** "NewPlayer v21.G5 Final.zip"
- **User comment:** *"a big improvement over the classic NP players"*

**What changed from G4 to G5:** No explicit changelog was obtainable (the
download zip's internal docs were not extracted; CSDb was unreachable for
direct page scraping).  The only primary evidence of G4→G5 differences comes
from the CheeseCutter user guide (`carol6502.neocities.org/c6_ccutter_guide`),
which documents CheeseCutter's instrument Byte C as:

> *"Works mostly as in NP21.G5"*

This phrasing — "mostly as in G5, not G4" — implies G5 **refined the
hard-restart type logic** in instrument byte C relative to G4.  Specifically:

| hi-nibble | restart type | presence |
|---|---|---|
| `0x` | Gate-off 3 frames before next note, waveform cleared 1 frame before | G5+ |
| `4x` | Soft restart: gate-off 2 frames before next note | G5+ |
| `8x` | Regular hard restart: gate-off + HR ADSR written 2 frames before note | G5+ |
| **`Ax`** | **"Laxity restart": same as `8x` but AD envelope is NOT touched** | G5+ |

The **`Ax` Laxity restart** is named after Laxity himself in the guide.  It
is defined as preserving the AD (attack/decay) part of the ADSR while still
doing hard restart — a subtle variation that avoids re-triggering the attack
phase.  The CheeseCutter guide confirms CheeseCutter implements "mostly" the
G5 semantics, making G5 the effective **canonical NP21 instrument model**.

**Low nibble of Byte C:** wave program delay value (`0x-0xF`) — controls how
many frames the wave table is delayed at note start.  This was present in G4
(as `INS_HR` = `$x0 = HR type, $0x arp delay count` per `player_v4.acme`
line 22).  The low-nibble semantics appear unchanged from G4 to G5.

**Net:** the G4→G5 difference is narrow and restricted to the hard-restart
type logic in instrument byte C (hi-nibble 0x/4x/8x/Ax taxonomy).  The table
formats (4-byte pulse/filter, 48-instrument column-major) appear unchanged.
No write-model change is evidenced — this is a player-behavior refinement, not
a data-layout change.

**SIDId note:** there is NO separate `Laxity_NewPlayer_V21_G5` signature in
SIDId.  The single `Laxity_NewPlayer_V21` signature catches both G4 and G5
binaries.  This is consistent with G5 being a behaviour-only change — the
play-routine shape (`STA $D404,Y` + `CMP #$FF` + `DEC abs,X`) did not change.

### 1d. NP21.B6 — CheeseCutter "booty" era

No CSDb entry for NP21.B6 was found.  What is known from secondary sources:

1. **CheeseCutter about.html** (previously captured verbatim in
   `pipelines/jch_newplayer/docs/archive_version_history.md` §3):
   > *"[CheeseCutter] has almost all the features of NP21.B6 … which was
   > based on Laxity's NP21.G5."*

2. **"B" suffix grammar:** per the same source, "B stands for booty" — it is
   a CheeseCutter-era label, not a Laxity original.  So NP21.B6 is
   **Abaddon's label**, applied to the form of NP21 that was input to
   CheeseCutter's own player.

3. **Relationship:** G5 → B6 → CheeseCutter.  Abaddon took Laxity's G5,
   made further changes (labelled "B6"), then wrote CheeseCutter's
   `player_v4.acme` to have "almost all the features" of that B6 version.

4. **What B6 changed from G5:** not documented in any obtainable source.
   CheeseCutter's player is described as having "almost all" the features
   (implying some G5/B6 features were deliberately left out or reimplemented
   differently).  The known difference: CheeseCutter's byte C implements the
   "mostly" G5 semantics but not 100% — the "slightly inaccurate" caveat in
   the carol6502 guide may refer to exactly these edge cases.

5. **B6 is not in HVSC.**  HVSC's `Laxity_NewPlayer_V21` population (313 SIDs)
   are composed using the editor with the G4 final player; B6 is an
   intermediate step in the CheeseCutter lineage, not a separately published
   Laxity tool.

### 1e. Suffix grammar summary

| suffix | meaning | author | notes |
|---|---|---|---|
| G | "standard" single-speed | JCH (coined) / Laxity (used) | G0/G4/G5 = revision within major |
| Q | "quattro" = multispeed, CIA-timed | JCH (coined) | Only attested on JCH's NP20.Q0 — see §2 |
| B | "booty" | Abaddon / CheeseCutter | Only NP21.B6; not a Laxity label |
| b | pre-release beta | Laxity | Only "21.b4" (the beta of G4) |

---

## 2. The Q-series multispeed question

### 2a. No NP21.Q variant by Laxity

No `JCH NewPlayer 21.Q*` release exists in CSDb, and none appears in HVSC.
The **Q-series belongs to JCH's own NP20 era** — "17.Q?" (Jan 1991) and
"20.Q0" are the attested Q variants (per `pipelines/jch_newplayer/docs/
archive_version_history.md` §2).  When Laxity took over the 21-series
(2005–2006) he did not publish a Q variant.

**Why multispeed is a non-issue for NP21.G4/G5:**

CheeseCutter's `player_v4.acme` shows `MULTISPEED = TRUE` compiled in by
default, and the player has a full `mplay` entry at base+$06.  The G4/G5
players include the same CIA machinery.  The distinction is how it's
**activated** at composition time:

- Single-speed (G-type) tunes: the song-speed byte in `songsets` is 1; the
  CIA timer is not programmed; `play()` fires once per VBI at $1003.
- Multispeed tunes: the song-speed byte > 1; the CIA is set to `$4cc7` (×1
  default) and the `mplay` vector at base+$06 fires for the sub-frames.

The PSID header `speed` word distinguishes these: speed=0 → all subtunes are
VBI-timed; speed≠0 → CIA-timed.

### 2b. CIA fraction of HVSC V21 corpus

The `hvsc84.db` schema does not store the PSID `speed` word (no `psid_speed`
column), so the fraction cannot be directly queried.  The prior discrimination
doc noted:

> "The taxonomy doc's earlier note ('6 multi-subtune, 1 RSID') is consistent;
>  CIA multispeed status is not currently indexed."

**Proxy evidence:** DRAX (166/313) and G-Fellow (92/313) account for 83% of
the corpus.  DRAX's other engines (e.g. DMC V4 with its per-tune CIA variants)
show that prolific Danish-scene composers did use multispeed.  It is likely
that some V21 tunes by DRAX are CIA-timed, but confirmation requires parsing
raw PSID headers.  **Until `psid_speed` is indexed**, use `siddump
--writelog-per-irq` on any DRAX/G-Fellow tune before assuming VBI-only.

### 2c. Verify path for CIA tunes (when found)

CIA-timed `Laxity_NewPlayer_V21` tunes → `siddump --writelog-per-irq` capture
(drops init prefix, buckets by `play()` IRQ) → `compare_instruction_stream`
flat path.  This is the same path used for Human_Race, Battle, and DMC CIA
variants.

---

## 3. Laxity's own releases — full tool timeline

Derived from CSDb scener profile (id=677) + JCH computer timeline +
HVSC engine counts:

| year | tool | relation to NP21 |
|---|---|---|
| 1988 | Laxity reverse-engineered JCH's C64 player (told JCH to stop using Laxity's) | origin |
| 1989 | TFA Editor V3.24 (Laxity as The Flexible Arts founder) | pre-NP |
| 1990 | Laxity Editor v/32-3.34, v/34-3.35 | pre-NP |
| 1990–2004 | Hiatus from C64 programming | — |
| 2005-08-27 | **NP21.G4 beta** (CSDb #20112) | NP21 origin |
| 2006-01-16 | **NP21.G4 Final** (CSDb #26563) | canonical NP21 |
| 2006-05-09 | **NP21.G5** (CSDb #33785) | G5 hard-restart refinement |
| 2006-09-02 | **SID Factory 0.5 (alpha 1)** (CSDb #39519) | NEW editor; see §4 |

**The 4-month window (May–Sep 2006) produced both NP21.G5 and the first SID
Factory alpha.** This is strong circumstantial evidence that NP21.G5 was the
final iteration of the NP21-native player, and Laxity pivoted immediately to
building his own editor with its own driver.

---

## 4. SID Factory lineage — did NP21 feed into SF2?

### 4a. SID Factory 0.5 alpha 1 (2006)

- A tracker-style music editor for C64, Laxity's own creation.
- Ships **two drivers** (5.02 and 6.03) — these are Laxity's NEW driver
  format, not NP21 players.  Feature highlights: "dynamic multispeed
  switching", "tempo table", portamento (driver 5.02), bug fix (driver 6.03).
- The CSDb page contains no mention of NP21 and the drivers are numbered in
  the 5–6 range, not in NP21's G4/G5 range.  **SID Factory's driver format
  is a clean-break design**, not a derivative of the NP21 binary layout.
- User comment: *"not too hard to migrate when you're coming from a jch
  background"* — confirms the editor is conceptually familiar to JCH users
  but does not claim code-level inheritance from NP21.

### 4b. SID Factory II (2019–present)

- Co-authored by JCH, Laxity, and Youth.
- Ships multiple **numbered drivers** including driver 11 (the standard
  default).  Driver 11 changelog: 11.02 adds pulse-program index + tempo-change
  + main-volume commands; 11.03 adds filter-enable flag bit in instruments;
  11.04 adds note-delay; 11.05 adds pulse-reset flag.
- The SID Factory II **instrument format is row-oriented** with a flag byte
  (hard-restart flag = `$80`, test-bit = `$10`, combinable as `$90`) — a
  different encoding from NP21's 8-column column-major table (stride=48).
- SF2 ships a **`converter_jch.cpp`** to import old JCH NP20.gX packed
  binaries, confirming that NP21/JCH and SF2 have distinct formats.
- SIDId gives SF2 a completely separate signature (`C8 B1 ?? C9 FF D0 04 C8
  B1 ?? A8 98 && C9 7E F0 ?? 18`) — the double-indirect `(ptr),Y` + `$7E`
  sentinel is structurally distinct from V21's `99 04 D4` + `C9 FF` + `DE`.
- HVSC treats `SidFactory_II/Laxity` as a separate engine (377 SIDs).

### 4c. Lineage verdict

```
NP20.G4 (JCH, 1991)
  │
  └── Laxity takes over player maintenance
       ├── NP21.G4 beta (Aug 2005) ──► NP21.G4 Final (Jan 2006) ──► NP21.G5 (May 2006)
       │         │                            │
       │         │              used by DRAX+G-Fellow+others for HVSC corpus (313 SIDs)
       │         │                            │
       │         └── NP21.B6 (Abaddon label)  │
       │                   └── CheeseCutter player_v4.acme ("based on JCH NP 21.G4 by Laxity/VIB")
       │
       └── Laxity pivots to own editor (Sep 2006)
            SID Factory 0.5 alpha1 → SF1 (SidFactory/Laxity, 39 SIDs)
                                         → SID Factory II (2019+, 377 SIDs)
                                           (driver 11; own format; converter_jch for NP20 import)
```

**Answer to "did NP21 feed into SF2?":**
- **Conceptually yes** — SID Factory's editor model was "based on a popular driver
  and editor developed from 1988 to 1991 by JCH" (VGMPF), so it inherited the
  JCH/NP design philosophy (track/sequence grammar, hard-restart logic, table
  programs).
- **Format no** — SF2's driver format is a re-encoding (row-oriented instruments
  with flag byte, different sequence grammar, `converter_jch` needed to import old
  tunes).  SF2 is NOT a packed NP21 binary; it cannot be decoded by the NP21
  extractor.  Treat `SidFactory_II/Laxity` (377 SIDs) as a separate migration
  target with its own pipeline.

---

## 5. NP21.G6 by Samar Productions — a third-party fork

CSDb #101622 is titled "JCH NewPlayer 21.G6" and is attributed to **Samar
Productions (Poland)**, not Laxity.  The release date in CSDb appears to
predate Laxity's G4 (2005), which suggests either a mislabelled entry, a
retroactively uploaded file, or a separate "G6" numbering by Samar that is
unrelated to Laxity's G4/G5 line.

Key points:
- Laxity's G4 beta is dated 2005-08-27.  If Samar's G6 is from 2000 (as
  the search snippet suggests), it would predate G4 — impossible in the
  published Laxity timeline.  Most likely explanation: **Samar's "G6" is a
  different numbering**, possibly a fork of NP20.G4 that Samar internally
  labelled "G6" before Laxity published his own NP21 line.
- Samar Productions is a Polish demoscene group whose members were active
  C64 composers in the late 1990s–2000s.  Slajerek (Marcin Romanski) is
  the group's best-known member; he appears in the `Laxity_NewPlayer_V21`
  author list as "Marcin Romanowski (Sidder)" with 7 tunes — suggesting
  Samar-associated composers adopted Laxity's G4 player for their work.
- **Migration implication:** the "NP21.G6 by Samar" binary, if it hits the
  `Laxity_NewPlayer_V21` SIDId signature, is covered by the NP21 extractor.
  If it has a different player binary (hitting `JCH_NewPlayer` or no match),
  it requires separate investigation.  Do NOT assume it uses the G5 table
  format without confirming against the binary.

---

## 6. HVSC corpus summary — key facts for migration planning

From `hvsc84.db` (mode=ro, 2026-06-14):

| metric | value |
|---|---|
| Total `Laxity_NewPlayer_V21` | **313 SIDs** |
| Standard address ($1000/$1003) | 289 (92.3%) |
| Non-standard base (relocated) | 24 (7.7%) — mostly by DRAX/G-Fellow |
| Single-subtune | 307 (98.1%) |
| Multi-subtune | 6 (1.9%) |
| RSID | 1 |
| Top author: DRAX | **166 (53%)** |
| Second author: G-Fellow | **92 (29%)** |
| Laxity himself | 4 (1.3%) |
| CIA-multispeed fraction | **unknown** — `psid_speed` not in DB |

The engine is primarily used by DRAX and G-Fellow, not Laxity himself.  This
mirrors the JCH NewPlayer pattern where JCH authored relatively few of the
3,611 HVSC tunes but his player was adopted by the community.

---

## 7. Relationship between `Vibrants/Laxity` (pre-NP21) and NP21.G4

Laxity's earlier tunes (pre-2005) use the `Vibrants/Laxity` engine (127 SIDs
authored by Laxity).  This is a **completely different player** — SIDId gives
it a 5-line OR signature keying on a 16-bit freq-write model (`ADC abs,X;
ASL; TAY; LDA tbl,Y; STA $D401; STA $D400`) and a $D416 filter write.  Its
canonical play offset is base+**$06** (not +$03 like NP21).

The Vibrants/Laxity engine is Laxity's bespoke early-1990s player, predating
the JCH editor merger.  JCH's own timeline (chordian.net) states that in 1988
"[JCH] reverse engineered Laxity's C64 music player and started composing in
it", after which Laxity told JCH to build his own editor — this is the
historical origin of the JCH editor.

**Migration implication:** do NOT conflate `Vibrants/Laxity` with
`Laxity_NewPlayer_V21`.  They are different engines with different formats,
different play offsets, and different SIDId signatures.  The NP21 extractor
only targets `Laxity_NewPlayer_V21`.

---

## 8. Practical notes for extraction

1. **Format to use:** the NP21.G4/G5 format.  Use CheeseCutter's
   `player_v4.acme` + `cc_base.d` + `cc_dump.d` as the **write-model oracle
   and serialisation reference** (documented in `cluster_np21_effect_routines.md`
   and `pipelines/jch_newplayer/docs/github_cheesecutter.md`).

2. **Hard-restart byte C:** implement the G5 semantics (hi-nibble 0x/4x/8x/Ax;
   `Ax` = Laxity restart, preserves AD).  CheeseCutter's player is "mostly"
   G5; the exact G4 semantics for the 0x/4x nibbles are not independently
   documented, but CheeseCutter's implementation is close enough for the HVSC
   corpus (which was all composed on the G4/G5 player).

3. **INSNO stride:** `INSNO = 48` in CheeseCutter = the NP21 standard.  The
   NP20.G4 corpus uses 32.  V21 tunes always use 48.  Do not mix.

4. **CIA detection:** parse the raw PSID header speed word before choosing the
   verification path.  Any `speed != 0` subtune → `siddump --writelog-per-irq`.

5. **Relocation:** 7.7% of V21 tunes are relocated (non-standard base).  The
   extractor must be relocation-aware (similar to the FC standard factory
   `fc_standard_config(sid)` approach).

---

## Leads to follow

1. **NP21.G5 internal docs:** the "NewPlayer v21.G5 Final.zip" (CSDb #33785)
   almost certainly contains a README or in-player text documentation.
   Download + extract when CSDb is accessible to get the exact G4→G5 changelog.
   This would confirm or deny the "G5 only changed byte C hr-type" hypothesis.

2. **NP21.B6 binary:** if obtainable (possibly bundled with early CheeseCutter
   releases or Abaddon's private archive), disassembling the B6 player vs G5
   would reveal exactly what Abaddon changed.

3. **Parse `psid_speed` from PSID headers:** add a `psid_speed` column to
   `hvsc84.db` populated from the PSID header offset $12 (a 32-bit word, one
   bit per subtune, bit=0 VBI / bit=1 CIA).  This would immediately quantify
   the CIA fraction of the 313 V21 tunes.  Implementation: extend
   `tools/build_sid_db.py`'s per-file parser.

4. **NP21.G6 / Samar Productions (CSDb #101622):** fetch when CSDb accessible.
   Determine whether this binary hits the `Laxity_NewPlayer_V21` SIDId
   signature or a different one.  If it predates 2005, it is likely a
   NP20-family fork with a "G6" label assigned independently of Laxity's 21-series.

5. **NP21 native source code:** the CSDb #26563 download ("NewPlayer v21.G4
   Final.zip") may contain Laxity's original 6502 asm source for the G4 player
   (as opposed to CheeseCutter's reimplementation).  If so, this is the ground-
   truth reference for HVSC binary decoding (the native packed format, not
   CheeseCutter's in-RAM layout).  Retrieve + inspect when CSDb accessible.

6. **SID Factory 0.5 driver format:** the driver 5.02/6.03 files distributed
   with SID Factory 0.5 (CSDb #39519) are the first Laxity SF driver artefacts.
   If they are 6502 .prg files, they can be disassembled to see how far the
   format diverged from NP21 in 2006.  This would close the "conceptually yes
   / format no" SF lineage verdict with hard evidence.

7. **Vibrants/Laxity format research:** the 127 Laxity-authored `Vibrants/Laxity`
   tunes are a separate engine.  The sidpreservation.6581.org catalogue + the
   5-line SIDId signature are the starting points.  Out of scope for NP21, but
   the play=$1006 (+$06) offset is a reminder to keep the two engines distinct
   in any multi-engine extractor dispatcher.
