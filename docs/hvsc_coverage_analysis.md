# HVSC Coverage Analysis — Das Model Addressable Market

**Date:** 2026-04-29  
**Method:** Full sidid scan of HVSC (MUSICIANS + GAMES + DEMOS directories)  
**Tool:** `tools/sidid` with `tools/sidid.cfg`

## Summary

| Metric | Count | % of Total |
|--------|------:|----------:|
| Total SIDs scanned | 60,572 | 100.0% |
| Engine-identified | 59,267 | 97.8% |
| Unidentified | 1,305 | 2.2% |
| Unique engine signatures | 644 | — |

**Total addressable market (Das Model):** **59,428 SIDs (98.1%)**

Breakdown by directory:

| Directory | Total | Identified | Unidentified |
|-----------|------:|----------:|-------------:|
| MUSICIANS | 56,032 | 55,510 | 522 |
| DEMOS | 3,015 | 2,879 | 136 |
| GAMES | 1,525 | 878 | 647 |
| **Total** | **60,572** | **59,267** | **1,305** |

Note: GAMES has higher unidentified rate (42%) — many game sound effects use one-off custom players without signatures in the sidid database.

---

## Tier Classification

Das Model conversion difficulty is classified into 5 tiers based on:
1. Whether a static binary parser already exists
2. Whether the engine uses CIA timer (multispeed) vs VBI-only
3. Whether digi samples are mixed with music
4. Whether `regtrace_to_usf` produces usable output

### Tier 1 — Already Supported (23,783 SIDs, 39.3%)

Static parsers or active Das Model work. Grade A songs already counted in pipeline.

| Engine | Count | Status |
|--------|------:|--------|
| GoatTracker_V2.x | 7,550 | Full static parser, 4,968 Grade A |
| JCH_NewPlayer | 3,678 | regtrace_to_usf, 107 Grade A |
| GoatTracker_V1.x | 1,384 | Same format as V2, static parser covers it |
| DMC | 10,738 | regtrace_to_usf, partial static parser |
| DMC_V6.x | 16 | DMC variant |
| Rob_Hubbard | 289 | Das Model in progress, 77 Grade A |
| JCH_Protracker | 94 | JCH variant, regtrace_to_usf |
| JCH_OldPlayer | 32 | JCH variant |
| GoatTracker_V2/Mini | 1 | GT2 mini variant |
| GoatTracker_V2/Mini2 | 1 | GT2 mini2 variant |

**Total Tier 1: 23,783**

Current Grade A count across Tier 1: ~5,152 (GT2: 4,968, JCH: 107, Hubbard: 77).  
Remaining Tier 1 headroom: ~18,631 songs.

### Tier 2 — Easy: Structured Trackers (19,179 SIDs, 31.7%)

Well-structured music-only tracker formats with standard SID usage patterns. `regtrace_to_usf` produces high-quality output for these. Static parser development is straightforward once the format is documented. Most use VBI (frame-rate) interrupts, not CIA.

**Top engines:**

| Engine | Count | Notes |
|--------|------:|-------|
| Soundmonitor | 3,663 | Classic tracker, very regular patterns |
| MoN/FutureComposer | 4,085 | Well-documented format, standard SID |
| RoMuzak_V6.x | 593 | Structured tracker |
| X-Ample | 387 | Structured |
| Loadstar_SongSmith | 334 | Structured editor |
| CheeseCutter_2.x | 306 | Modern tracker |
| Electrosound | 301 | Standard patterns |
| Ubik's_Musik | 293 | Well-known format |
| SidFactory_II/Laxity | 380 | Modern tracker by known dev |
| Hermit/SidWizard_V1.x | 1,074 | Well-documented modern tracker |
| SidTracker64 | 264 | Modern tracker |
| David_Whittaker | 117 | Standard game music player |
| Ben_Daglish/Gremlin | 60 | Standard game music |
| Martin_Galway | 55 | Well-studied |
| NinjaTracker_V2.x | 97 | Standard format |
| DefleMask_v12 | 245 | Modern multi-platform, known format |
| DefMon | 107 | Structured |
| Vibrants/Laxity + JO | 309 | Structured variants |
| MoN/FutureComposer | 4,085 | (see above) |
| MoN/Deenen + Bjerregaard | 285 | Standard SID patterns |
| (+ 100+ smaller engines) | ~5,000 | Individually <100 songs each |

**Total Tier 2: 19,179**

Expected conversion rate with regtrace_to_usf: 80–90% Grade A for pure-music engines.  
FutureComposer alone (4,085 songs) would be a major win — it is a well-documented format.

### Tier 3 — Medium: CIA Timer / Complex Features (14,089 SIDs, 23.3%)

These engines use CIA timer interrupts for multispeed playback (2x–16x per frame), or have complex effects (filter sweeps, sync/ring modulation patterns, heavy pulse modulation). Regtrace still captures output but V2 player needs CIA support to play them back correctly.

**CLAUDE.md status note:** "703 songs currently 100% F-rate due to CIA timer — V2 player needs CIA timer setup." This tier is the primary bottleneck for future Grade A gains.

**Top engines:**

| Engine | Count | Complexity |
|--------|------:|-----------|
| Music_Assembler | 6,403 | CIA common, complex effects |
| HardTrack_Composer | 1,170 | Likely CIA multispeed |
| Master_Composer | 1,075 | CIA timer widespread |
| Geir_Tjelta/SIDDuzz'It | 994 | CIA-based |
| SoedeSoft | 950 | Complex effects |
| Digitalizer_V2.x | 680 | Multispeed |
| GMC/Superiors | 446 | Game Music Creator, CIA |
| Laxity_NewPlayer_V21 | 314 | Complex features |
| EMS/Odie | 197 | Complex sound effects |
| Jeff | 192 | Complex player |
| John_Player | 184 | Complex |
| MusicShop | 182 | Complex |
| TFX | 269 | Complex tracker |
| Geir_Tjelta/* (4 variants) | 143 | CIA-based |
| Sidbang64_1+2/Warp8 | 57 | Bankswitching |
| TFMX / variants | 50 | Amiga port, samples |
| (+ many smaller engines) | ~800 | |

**Total Tier 3: 14,089**

Key bottleneck: CIA timer support in V2 player. Once added, a significant fraction of Tier 3 becomes accessible. Music_Assembler alone at 6,403 songs would be transformative.

### Tier 4 — Hard / Out of Scope: Digi Samples (614 SIDs, 1.0%)

These players mix or replace SID synthesis with PCM sample playback (digi). The SID chip is used primarily as a DAC. Das Model targets synthesis-based instruments only — digi playback is fundamentally different and requires separate handling.

Examples: Yip_MegaSound (78), Digi-Organizer (39), Dutch-USA_Team/ProDrum (11), Algorithm/Frodigi (7), 8bitDigi/Mahoney (3), and ~50 other `*_Digi` engines.

**Total Tier 4: 614** (not addressable by Das Model without digi extension)

### Tier 5 — Out of Scope: Non-Music (530 SIDs, 0.9%)

| Category | Count | Reason |
|----------|------:|--------|
| Basic_Program | 522 | BASIC programs, not SID music players |
| Crunched:Exomizer | 3 | Need unpacking before analysis |
| Crunched:PUCrunch | 1 | Need unpacking |
| SoftwareAutomaticMouth | 1 | Speech synthesis, not music |
| Silas_Warner | 2 | Early non-music programs |
| Kawasaki_Rhythm_Rocker | 1 | Hardware rhythm box |

**Total Tier 5: 530** (not music — skip)

### Unclassified (1,072 SIDs, 1.8%)

207 engine names not explicitly classified. Most are composer-attributed players (e.g., `Ariston`, `Henning_Andersen`, `PlayStar`) or small one-off engines. Breakdown:

- 148 `Ariston` — custom player, likely structured, probably T2
- 48 `Basic/Jim_Butterfield` — BASIC-adjacent but may have music
- ~876 spread across 205 engines (<30 songs each)

For the addressable market estimate, unclassified engines are counted conservatively as reachable via `regtrace_to_usf`.

**Unidentified (1,305 SIDs, 2.2%):** sidid has no signature for these. Most are one-off engines or variants. `regtrace_to_usf` is the fallback — it works on any engine by capturing register output directly.

---

## Addressable Market Summary

| Tier | Songs | Reachable? | Expected Grade A Rate |
|------|------:|:----------:|----------------------:|
| T1 — Already supported | 23,783 | Yes (pipeline exists) | 22% current, ~70% potential |
| T2 — Easy trackers | 19,179 | Yes (regtrace + static parser) | ~80% with static parser |
| T3 — CIA/complex | 14,089 | Yes (after CIA timer support) | ~50% with CIA support |
| Unclassified | 1,072 | Yes (regtrace fallback) | ~40% estimate |
| Unidentified | 1,305 | Yes (regtrace fallback) | ~30% estimate |
| **Subtotal addressable** | **59,428** | **98.1%** | |
| T4 — Digi/samples | 614 | No (out of scope) | — |
| T5 — Non-music | 530 | No (not music) | — |
| **Total HVSC** | **60,572** | **98.1% addressable** | |

**Conservative Grade A estimate (addressable only):**
- Tier 1 at 70% potential: 16,648
- Tier 2 at 80%: 15,343
- Tier 3 at 50%: 7,045
- Unclassified/unidentified at 35%: 825

**Total potential Grade A: ~39,861 (65.8% of all HVSC)**

---

## Priority Roadmap for Maximum Coverage

### Phase 1 (immediate, high ROI): CIA Timer in V2 Player
- Unlocks **14,089 Tier 3 songs** immediately via regtrace_to_usf
- Also fixes the known 703-song F-rate problem in current GT2 pipeline
- Music_Assembler (6,403) alone justifies the work

### Phase 2: FutureComposer Static Parser
- 4,085 songs (MoN/FutureComposer)
- Well-documented format, similar complexity to GT2
- Expected 85%+ Grade A with static parser

### Phase 3: SidWizard / CheeseCutter Parsers
- SidWizard: 1,074 songs, modern format, documented
- CheeseCutter 2.x: 306 songs, open-source tracker
- Both are well-studied community tools

### Phase 4: HardTracker / Master_Composer
- 1,170 + 1,075 = 2,245 songs
- CIA-based, need timer characterization

### Phase 5: Soundmonitor / Ubik's Musik
- Soundmonitor: 3,663 songs — classic era, standard VBI
- Ubik's Musik: 293 songs — well-known format

### Phase 6: Batch regtrace_to_usf sweep
- Apply to all Tier 2 engines without static parsers
- Expected ~80% Grade A from pure-music structured trackers
- Covers the long tail of 100+ smaller engines

---

## Data Notes

- Scan performed 2026-04-29 with `tools/sidid` on full HVSC
- sidid.cfg contains 644 unique engine signatures
- MUSICIANS directory: 56,032 SIDs (largest, best coverage at 99.1% identified)
- GAMES directory: lower identification rate (57.6%) — game sound effects use custom one-off players
- Multiple engine variants (e.g., `Jeff/Airwalk`, `Jeff/BullSID`) counted separately but share underlying engine
- Grade A rates are estimates based on current pipeline performance on known engines
