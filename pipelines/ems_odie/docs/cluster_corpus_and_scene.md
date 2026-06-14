# EMS/Odie — Corpus Characterisation & Scene Context

```
provenance:
  sources:
    - url: "file:hvsc84.db"
      fetched_via: "sqlite3 read-only Python query"
      fetch_date: 2026-06-14
      content_date: "HVSC #84 (December 2025)"
      reliability: authoritative (local HVSC mirror)
    - url: "https://csdb.dk/release/?id=4649"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: ongoing
      reliability: high (primary scene DB)
    - url: "https://csdb.dk/scener/?id=1181"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: ongoing
      reliability: high
    - url: "https://github.com/cadaver/sidid/blob/master/sidid.nfo"
      fetched_via: WebFetch (raw)
      fetch_date: 2026-06-14
      content_date: ongoing
      reliability: high (sidid engine fingerprint DB)
    - url: "file:hvsc84/DOCUMENTS/STIL.txt"
      fetched_via: local read (latin-1)
      fetch_date: 2026-06-14
      content_date: HVSC #84
      reliability: authoritative
    - url: "https://www.lemon64.com/forum/viewtopic.php?t=5725"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: medium (scene forum, anecdotal)
    - url: "https://www.lemon64.com/forum/viewtopic.php?t=10753"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: medium
    - url: "https://remix64.com/member/merman/"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: medium
    - url: "https://demozoo.org/sceners/50015/"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: medium
  author: corpus-agent
```

---

## 1. Engine Family Overview

**EMS = "The Electronic Music System"** — a native C64 SID music editor and
player engine written by Sean Connolly (handle: **Odie**) of Cosine Systems /
Sonix Systems, UK. Version 7.03 is publicly documented (CSDb #4649, released
18 January 1997). sidid also identifies V9.x and V10.x sub-variants in binary
signatures. EMS is described in scene forums as "good but advanced" —
professional-tier but with a steep learning curve; competitors cited are DMC
and JCH.

Key scene quote (Lemon64 thread t=5725, attributed to TMR/Cosine):
> "EMS only gained an editor at V4.3 (the latest is V8 and there isn't an
> editor for that either)"

Odie himself "normally works in source code rather than an editor" (same
thread). He also used earlier Rockmonitor and PulsePlayer before EMS.

---

## 2. Related sidid Engine Strings — All Sean Connolly

All five detection labels in sidid point to the same author.

| sidid label     | n (HVSC #84) | Year span                           | Description |
|-----------------|:---:|-------------------------------------|-------------|
| `EMS/Odie`      | 196 | 1989 – 2024                         | Main family; canonical form |
| `Odie/Cosine`   |   9 | 1987 – 19??                         | Early Cosine-era works; pre-EMS or early EMS variant |
| `Odie_tiny`     |   3 | 1998 – 1999                         | Compact player variant (4k party/digi-competition entries) |
| `Odie/Pulse`    |   2 | 1987 – 1988                         | Oldest: Pulse Productions era, pre-Cosine |
| `(EMS_V10.x)`   |   1 | 2025                                | V10 sub-variant; single SID (Rescued_Pixels_3 by Arkanix Labs) |

**`Digital_Systems` (n=3)**: three SIDs by Arjen Bokhoven (Harlequin) / Silicon
Limited (1991). Same init=$1000/play=$1003 address pattern but a different
sidid signature — NOT Sean Connolly; coincidentally similar address layout.

**Interpretation**: `Odie/Cosine` and `Odie/Pulse` are pre-EMS or earliest-EMS
works from 1987–1990 (Sonix Systems / Pulse Productions era); they share Odie
authorship but an older player binary. `Odie_tiny` is a minimised variant from
1998–1999, consistent with the demo-compo context (4k size constraint).
`(EMS_V10.x)` is a later sub-signature detected within the main EMS family —
it covers at least one 2025 release. All are the same Sean Connolly family.

---

## 3. HVSC Corpus Shape — EMS/Odie (n=196)

### 3.1 Load / Init / Play Address-Cluster Table

All 196 EMS/Odie SIDs have **load_addr = $0000** (PSID relocation header
convention; actual load is embedded in the PSID data offset). The init and play
addresses indicate where the engine relocates to.

| Init addr  | Play addr  | Count | % total | Label / notes |
|------------|------------|------:|--------:|---------------|
| `$1000`    | `$1003`    |   142 |  72.4%  | **Canonical form** — the dominant layout |
| `$E000`    | `$E003`    |     8 |   4.1%  | High-page relocation ($E000 = 57344) |
| `$8000`    | `$8003`    |     4 |   2.0%  | Mid-high ($8000 = 32768) |
| `$9000`    | `$9003`    |     3 |   1.5%  | Mid-high ($9000 = 36864) |
| `$1100`    | `$1103`    |     3 |   1.5%  | Near-canonical ($1100 = 4352) |
| `$1E00`    | `$1E03`    |     2 |   1.0%  | |
| `$0900`    | `$0903`    |     2 |   1.0%  | |
| `$4000`    | `$4003`    |     2 |   1.0%  | |
| `$0F00`    | `$0F03`    |     2 |   1.0%  | |
| various    | various    |    28 |  14.3%  | One-off relocations, see §3.2 |

**Address pattern**: init and play always differ by exactly 3 bytes
(`play = init + 3`) in 186 of 196 cases. The 3-byte gap is the init routine
entry point (does full chip reset + data init), with the play routine starting
3 bytes later. This is the EMS player calling convention.

Exceptions to the +3 pattern (10 SIDs):
- `Brian_the_Lion` ($0FD0/$0FE2, +18 bytes, 1 CIA subtune)
- `Cyberwing` ($2A5A/$2A73, +25 bytes)
- `Euro_Soccer` ($1003/$1006, init and play both near $1000 but unusual)
- `Feelin_Good` ($1000/play=$0000, digi-like)
- `Get_em_DX` ($0FF0/$0FF8, +8 bytes)
- `Wonderland` ($0FFB/$1003, straddles the $1000 boundary)
- several others with custom layouts for game integration

### 3.2 Relocation Cluster Summary

| Cluster | Init range | Count | Notes |
|---------|-----------|------:|-------|
| Canonical $1000 | $1000–$10FF | 143 | 73% |
| High ($8000–$FFFF) | $8000–$EF00 | 17 | 8.7% — game/demo use |
| Sub-page ($0800–$0FFF) | various | 11 | 5.6% — tight memory budgets |
| Mid ($2000–$7FFF) | various | 10 | 5.1% — game integration |
| Near-$1000 ($1100–$1FFF) | various | 8 | 4.1% |
| One-off ($3000+) | various | 7 | 3.6% |

Distinct (init,play) address pairs: **37** unique pairs across 196 SIDs,
indicating genuine relocation diversity rather than a single fixed layout.

---

## 4. Author / Folder Concentration

| HVSC folder | Composer | Count | % |
|-------------|----------|------:|--:|
| `MUSICIANS/M/Merman` | Andrew Fisher (Merman) | 99 | 50.5% |
| `MUSICIANS/C/Connolly_Sean` | Sean Connolly (Odie) | 61 | 31.1% |
| `MUSICIANS/T/TMR` | Jason Kelk (TMR) | 13 | 6.6% |
| `MUSICIANS/B/Bayliss_Richard` | Richard Bayliss | 10 | 5.1% |
| `MUSICIANS/P/Peabrain` | Andreas Timmermann (Peabrain) | 4 | 2.0% |
| `MUSICIANS/G/Gillgrass_Dan` | Dan Gillgrass (Danny G) | 3 | 1.5% |
| `MUSICIANS/F/Francois_Marc` | Marc François (Skywave) | 2 | 1.0% |
| `MUSICIANS/F/Fuzz` | Dustin Chambers (Fuzz) | 2 | 1.0% |
| `MUSICIANS/J/Julian_Jaymz` | Jaymz Julian | 1 | 0.5% |
| `MUSICIANS/S/Sack` | Adam Hay (Sack) | 1 | 0.5% |

**Merman dominates with 99 SIDs (50.5%)** — more than Connolly (the author)
himself. All Merman EMS SIDs are concentrated in 1999–2004 with 69 alone in
"1999 Ozone" (his music label), 7 in "2001 Ozone", and 10 in "2002 People of
Liberty/ROLE".

Merman note (from STIL.txt section header):
> "Andrew Fisher's (Merman) own comments are denoted (AF)."

Andrew Fisher (Merman) acquired a C64 in 1985, started serious composing in
1990 after getting a disk drive (Remix64 profile). His 99 EMS SIDs in HVSC
represent a fraction of his total output (800+ SIDs total per Remix64).

**TMR = Jason Kelk** (also "The Magic Roundabout", "The Cybernetic Man") —
Cosine group coder and musician. His EMS SIDs span 1993–2004. TMR also provided
the charset for EMS V7.03 (credited as "The Magic Roundabout" in CSDb).

**Marc François = Skywave** — co-authored the EMS V7.03 intro music (CSDb
credits him for music alongside Odie). Two EMS SIDs in HVSC: one 1989 Sonix
Systems, one 1991.

---

## 5. Year / Release Distribution

| Year | Count | Key labels |
|------|------:|------------|
| 1989 | 3  | Bigtime Software, Sonix Systems |
| 1990 | 5  | Cosine, Sonix, Microvalue |
| 1991 | 7  | Cosine, Sonix, System 3, Flair |
| 1992 | 3  | Creative Edge, Ready Soft, Sonix |
| 1993 | 5  | Cosine Systems |
| 1994 | 1  | Bigtime Software |
| 1995 | 10 | Cosine, Psytronik, Bigtime |
| 1996 | 6  | Cosine Systems |
| 1997 | 6  | Cosine Systems (EMS V7.03 released this year) |
| 1998 | 3  | Cosine Systems, Sonic Dreams |
| **1999** | **82** | **Ozone (69!), Faque, Cosine, Suicyco, Mirage, Binary Zone** |
| 2000 | 9  | Ozone, The New Dimension, Binary Zone |
| 2001 | 7  | Ozone |
| 2002 | 14 | People of Liberty/ROLE, ROLE |
| 2003 | 1  | ROLE |
| 2004 | 4  | Cosine, People of Liberty |
| 2007 | 3  | Cosine, The New Dimension |
| 2008 | 2  | People of Liberty/ROLE, Retro64 |
| 2009 | 2  | Cosine |
| 2010 | 1  | Retro64 |
| 2011 | 2  | Cosine, Achim Volkers |
| 2012 | 3  | Psytronik, Sean Connolly, Achim Volkers |
| 2013 | 2  | Cosine, Geir Straume/Sean Connolly |
| 2014 | 1  | Geir Straume |
| 2016 | 1  | Cosine |
| 2017 | 1  | The New Dimension |
| 2018 | 1  | Cosine |
| 2019 | 1  | Geir Straume |
| 2020 | 4  | Cosine |
| 2021 | 2  | The New Dimension, Cosine |
| 2022 | 1  | Cosine/Psytronik |
| 2023 | 1  | The New Dimension |
| 2024 | 1  | The New Dimension |
| (no year) | 1 | |

**The 1999 spike (82 SIDs) is almost entirely Merman's Ozone collection** (69
SIDs). EMS was adopted broadly in the UK scene around 1997–1999. The engine is
still used as of 2024–2025 (Bayliss/Richard at The New Dimension; Connolly's
2025 Arkanix Labs release triggering the EMS_V10.x detection).

---

## 6. PSID Format Parameters

| Parameter | Distribution |
|-----------|-------------|
| PSID version | v2: 195, v3: 1 |
| Speed (VBI/CIA) | VBI (speed=0): 195; CIA (subtune 1): 1 (`Brian_the_Lion.sid`) |
| load_addr | $0000 (PSID convention): 196/196 |

**Single-subtune dominance**: 171 of 196 SIDs (87%) have exactly 1 subtune.
Multi-subtune SIDs are predominantly Connolly originals, not Merman covers:

| SID | Subtunes | Notes |
|-----|:--------:|-------|
| `Cyberwing` (Connolly, 1995) | 25 | Multi-song game soundtrack |
| `Turbocharge` (Connolly, 1991) | 22 | System 3 commercial game |
| `Hammer_Down` (Connolly, 2022) | 12 | |
| `Brilliant_Maze` (Connolly, 2014) | 8 | |
| `Get_em_DX` (Connolly, 2012) | 8 | |
| `Alpacalypse` (Bayliss, 2024) | 7 | |
| `For_Speed_We_Need_3` (Bayliss, 2023) | 7 | |
| `Dice_Skater` (Connolly, 2019) | 7 | |
| `Euro_Soccer` (Connolly, 1992) | 6 | |

**PSIDv3**: one SID — `Lovefunk_2SID.sid` (Connolly, 2020, Cosine Systems).
The 2SID suffix + PSIDv3 signals a dual-SID configuration.

**Songlength**: min=12s, max=1338s (22 min!), mean=214s, median=174s.
93 SIDs exceed 3 minutes (47%). This is consistent with EMS being a cover-music
tool where the full song plays out.

---

## 7. Scene Context

### 7.1 Sean Connolly (Odie) — the Author

- **Real name**: Sean Connolly; handle "Odie" from the dog in Garfield (CSDb).
- **Country**: United Kingdom.
- **Active**: 1989–present (2025 release documented).
- **Groups**: Cosine Systems (primary, still active), Sonix Systems (early work).
- **Roles**: Coder, Musician, Organizer, Webmaster.
- **CSDb ID**: 1181.
- **EMS V7.03** (CSDb #4649): released 18 January 1997 by Cosine. Credits —
  Code+Design: Odie; Music: Odie + Skywave (Marc François); Graphics+Charset:
  The Magic Roundabout (Jason Kelk). Download count on CSDb: 396 (moderate).

EMS version history inferred from sidid + forum quotes:
- Pre-V4.3: player only, no built-in editor (Lemon64 t=5725)
- **V4.3**: first version with an editor
- **V7.03** (Jan 1997): publicly released tool (CSDb #4649)
- **V8**: driver-only (no editor); used in `In_My_Life_My_Mind.sid` (2000,
  Cosine) and `Combo_Racer.sid` (1999, Cosine); Lemon64 post notes "V8 driver
  exists already"
- **V9.x**: separate sidid sub-signature; release date unknown
- **V10.x**: latest detected; `Rescued_Pixels_3.sid` (2025, Arkanix Labs)

### 7.2 Cosine Systems

Founded 1986 by Skywave (Marc François) in the UK. Cracking division shut 1989.
151+ documented CSDb releases spanning demos, games, intros, tools. Key members
in EMS context: Odie (coder/musician), TMR (coder/musician), Merman (musician,
adjacent — part of People of Liberty/ROLE/Ozone, not Cosine member per se).

Cosine still active as of 2020+ (Blok Copy DTV 2009, Vallation 2013,
Firepower 2020, Carl Lewis Challenge 2021, Hammer Down 2022).

Website: cosine.org.uk (per Lemon64 posts; not fetched — SSL issues at
query time).

### 7.3 Merman (Andrew Fisher) — the Power User

Andrew Fisher (Merman) is the single largest contributor to the EMS/Odie HVSC
corpus: **99 of 196 SIDs (50.5%)**. He is NOT a Cosine member — his releases
go through:
- **Ozone**: his personal music label (1999–2001, 80 SIDs)
- **People of Liberty / ROLE**: a UK scene diskmag group (2002–2008, 16 SIDs)

Fisher started C64 composing in 1990 (disk drive acquired). He chose EMS as
his primary tool. His compositions are nearly all covers of pop/rock songs
(Beatles, Oasis, Police, Queen, Jarre, etc.) — explaining the long average
songlength (full song playthrough). The STIL.txt index for Merman includes
song titles and original artists for almost every SID.

His 99 EMS SIDs in HVSC are a small fraction of his 800+ total SID output —
the others likely use different tools or are not yet in HVSC.

### 7.4 The Network: Cosine + Ozone + People of Liberty

The EMS scene forms a tight UK network:
- **Cosine** (Odie, TMR) — the engine source and Cosine game/demo use
- **Ozone** (Merman) — mass cover-music production using EMS
- **People of Liberty / ROLE** (Merman, others) — diskmag scene, also EMS users
- **The New Dimension** (Richard Bayliss) — still using EMS in 2023–2024
- **Faque / Suicyco / Psytronik** — smaller scene labels with 1–4 EMS SIDs each

---

## 8. HVSC DOCUMENTS — EMS References

Searched: STIL.txt (108,101 lines, latin-1), Musicians.txt, HVSC.txt,
Players.txt (not present), Creators.txt.

**STIL.txt**: One direct EMS mention —
```
/MUSICIANS/M/Merman/EMS_Collection_1_Intro.sid
(#1) NAME: Whooosh!
COMMENT: "Inspired by the Apex intro to Creatures 2." (AF)
(#2) NAME: Intro tune
COMMENT: "Backdrop for intro inspired by 'Velvet Underground' album sleeve..." (AF)
```
No direct STIL comments reference the EMS engine by name.

Merman's STIL section header notes: "Andrew Fisher's (Merman) own comments are
denoted (AF)." His individual SID entries have rich ARTIST/TITLE attribution
(pop originals) but no tool/engine commentary.

The Connolly_Sean STIL section (28,279 onwards) covers 50+ SIDs with TITLE/
ARTIST/COMMENT metadata; no EMS engine commentary appears there either.

**Musicians.txt**: searched; no Merman/Connolly/EMS content found (file may
be a stub or in a different encoding — zero matches for these names).

---

## 9. sidid Binary Signatures (from sidid.cfg)

Main `EMS/Odie` uses 5 independent signature patterns (any match = EMS/Odie):
```
B9 ?? ?? 85 F8 B9 ?? ?? 85 F9 BC ?? ?? B1 F8 C9 FF D0 ...
BD ?? ?? 85 F8 BD ?? ?? 85 F9 BC ?? ?? B1 F8 C9 40 90 ...
B9 ?? ?? AC ?? ?? 99 06 D4 AD ?? ?? 99 05 D4 AD ?? ?? 29 FE 99 04 D4
BC ?? ?? B9 ?? ?? 85 ?? 0A 85 ?? 18 65 ?? ... 4C
85 ?? 06 ?? 26 ?? 26 ?? 26 ?? 38 A5 ?? E5 ?? AA A5 ?? E5 ?? 90
```

Sub-signatures:
```
(EMS_V7.03): 8D ?? ?? A0 16 A9 00 99 00 D4 88 10 FA A9 ?? 8D 04 D4 8D 0B D4 8D 12 D4 60
(EMS_V9.x):  A2 02 A0 0E 20 && A0 07 20 && A0 ?? 86 ?? 84 ?? BD
(EMS_V10.x): A0 00 B9 ?? ?? 0A 99 ?? ?? B9 ?? ?? 2A 99 ?? ?? C8 C0 53 D0
Odie/Cosine: 60 BD ?? ?? 38 FD ?? ?? 9D && 38 DE && 18 7D ?? ?? 9D && FE ?? ?? BD ?? ?? C9 ?? F0
Odie/Pulse:  9D 00 D4 E8 E0 20 D0 F5 A9 ?? 8D 18 D4 A9
Odie_tiny:   18 7D ?? ?? 29 7F A8 B9 ?? ?? 48 B9 ?? ?? BC ?? ?? 99 01 D4 68 99 00 D4 FE
```

The `&&` tokens in sidid mean "address that appears earlier in the code"
(self-referential address pattern). The V10.x signature's `C0 53` = CPY #$53
(compare Y to 83 decimal) likely reflects a table-size or loop-count constant
in the V10 player.

`Digital_Systems` (Harlequin, Silicon Limited, 1991) has a completely different
signature despite similar addresses — confirmed unrelated to EMS/Odie.

---

## 10. Address Overlap with Other Engines

The canonical $1000/$1003 is the most common HVSC address pair (27,697 SIDs
total). EMS/Odie's 141 canonical SIDs are 0.5% of all $1000/$1003 SIDs —
sidid's pattern matching is needed to distinguish them from DMC (8943),
GoatTracker_V2.x (4717), JCH_NewPlayer (3195), Music_Assembler (2987), etc.

---

## Leads to Follow

1. **EMS V8 driver binaries**: two SIDs explicitly identified as V8-era in forum
   (`In_My_Life_My_Mind.sid`, `Combo_Racer.sid`) but sidid classifies them as
   generic `EMS/Odie` (not V8 sub-variant). What distinguishes V8 from V7.03 at
   the binary level? sidid.cfg has no V8 signature — check if it's subsumed
   under the generic patterns.

2. **EMS V9.x / V10.x exact release dates**: CSDb tool releases for V9 and V10
   not found in searches — no CSDb IDs known beyond #4649 (V7.03). The V10.x
   2025 SID is by Arkanix Labs, not Cosine; suggests EMS was distributed beyond
   Cosine by V10.

3. **Merman's non-EMS tools**: 800+ total Merman SIDs but only 99 in HVSC tagged
   EMS/Odie. What does he use for the rest? Likely JCH or DMC (he is noted
   in the C64 magazine scene). Cross-reference Merman's other engine tags.

4. **`Odie/Cosine` vs `EMS/Odie` boundary**: the 9 Odie/Cosine SIDs range
   1987–19??. Their addresses vary wildly ($EA0A/$CEB2/$65C0 etc.) — much
   more than EMS/Odie. These may be Odie's pre-EMS works with a different
   player or very early EMS without the canonical $1000 relocation.

5. **`Lovefunk_2SID.sid` (PSIDv3 / dual-SID)**: only PSIDv3 in the corpus.
   The EMS player handles 2SID? Or is this a hybrid build? Check how the
   player at $52A0 integrates with the second SID chip.

6. **The `Brian_the_Lion` CIA subtune**: sole CIA-timed SID in the corpus
   (speed bit 1 set). What triggers CIA mode in EMS? Is it a player flag or
   host-set PSID header?

7. **cosine.org.uk archive**: site was cited as EMS download host; not
   successfully fetched (SSL error). Wayback Machine or direct access may
   reveal version change notes, older EMS manuals, or the full EMS editor UI.

8. **`EMS_Collection_1_Intro.sid` (Merman, 1999)**: the title implies an
   "EMS Collection #1" music disk was released under Ozone. This could be
   a significant artifact documenting the EMS format / Merman's working
   method. Locate on CSDb.

9. **Peabrain (Andreas Timmermann) + Faque label**: 4 EMS SIDs in 1999.
   Faque appears to be a small Belgian/German scene label. Peabrain's
   connection to Cosine/EMS is not documented — was EMS distributed widely
   enough to reach non-UK sceners?
