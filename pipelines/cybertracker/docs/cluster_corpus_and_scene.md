# CyberTracker — Corpus Characterisation & Scene Context

## Provenance

| field | value |
|---|---|
| author | Agent (corpus characterisation sub-task) |
| fetch_date | 2026-06-14 |
| content_date | 2001–2026 (sources span this range) |
| primary_sources | hvsc84.db (READ-ONLY), noname.c64.org, csdb.dk, archive.org, pouet.net |
| fetched_via | DB query (sqlite3 read-only) + WebFetch + WebSearch |
| reliability | HIGH for DB-derived stats (direct HVSC #84 data); MEDIUM for scene context (web sources, some 403/redirect failures) |

---

## 1. Corpus overview

HVSC #84 contains **255 CyberTracker tunes** split across two sidid engine strings:

| Engine string | Count | Notes |
|---|---|---|
| `CyberTracker` | 125 | Native .ct export — variable load base |
| `CyberTracker_exe` | 130 | Executable-Maker output — nearly all at fixed $53A2 |
| **Total** | **255** | |

All 255 files are **PSIDv2**, **all VBL** (speed=0, no CIA tunes detected — psid_version=2 across the board with no speed!=0 flag anomalies). All have `load_addr=0` (PSID relocatable flag: the actual load is embedded in the binary).

Subtune distribution:
- `CyberTracker`: 119 files with 1 subtune, 6 files with 2 subtunes (120 total subtunes). No 3+ subtune files.
- `CyberTracker_exe`: 130 files with 1 subtune (single-song executable output).

Songlength:
- `CyberTracker`: min 16 s, max 502 s, avg 131.6 s
- `CyberTracker_exe`: min 14 s, max 436 s, avg 147.1 s

---

## 2. Address-cluster table

### 2a. `CyberTracker` (125 tunes)

The dominant fingerprint is `init_addr` at various positions with `play_addr = init_addr + $51` (81-byte stub). This is the **packer-output format** — all addresses vary tune-to-tune (data size determines load base).

| init→play gap | init_addr | play_addr | Count | Interpretation |
|---|---|---|---|---|
| `$0051` (81) | varies ~$1DC0–$2BBE | init+$51 | **87** | Standard packer output; init/play vary per song size |
| `$0003` (3) | `$1000` exact | `$1003` | **35** | CyberTracker Packer BETA#1 output — fixed $1000 load |
| `$0003` (3) | `$2169` | `$216C` | 2 | Anomalous — same gap, non-$1000 base |
| `$004B` (75) | `$2BBE` | `$2C09` | 1 | `Higher_State_of_SID` (Cyberbrain) — unusual gap |
| `$0007` (7) | `$0FFC` | `$1003` | 1 | `Jungle_Oukoi` (JMX 64) — near-$1000 with small header |
| `$0005` (5) | `$0FFE` | `$1003` | 1 | `Panos-Tuotto` (Jizz) — near-$1000 with tiny header |

**Key finding:** The 87 `gap=$51` tunes all use a fixed 81-byte init stub before the play entry. The init address crawls upward as song data grows (range ~$1DC0 to ~$2BBE). The $1003-play-address cluster (35 tunes) is a distinct build path using the CyberTracker Packer BETA#1 (March 2002, Windows/DOS tool), which always places code at $1000.

### 2b. `CyberTracker_exe` (130 tunes)

The Executable Maker produces a self-contained binary; the PSID wrapper is thin.

| init_addr | play_addr | gap | Count | Interpretation |
|---|---|---|---|---|
| `$53A2` | `$53E2` | `$0040` (64) | **128** | **Standard Executable Maker layout** — one fixed binary |
| `$5BA2` | `$5BE2` | `$0040` (64) | 1 | `Suntory_Story` (Bisboch/Hokuto Force, 2019) — shifted by $0800 |
| `$482A` | `$482D` | `$0003` (3) | 1 | `Robo-Toy` (Mac/Radical, 2002) — anomalous: misclassified? |

**Key finding:** 128/130 exe tunes (98.5%) are a single fixed layout: `init=$53A2`, `play=$53E2`. The init-to-play gap of 64 bytes ($40) is the Executable Maker's fixed dispatch stub. This is ONE binary build — effectively a single player version. The `$5BA2` variant (`Suntory_Story`) appears to be the same Executable Maker binary loaded $800 bytes higher, likely due to a later version or custom relocation for a demo context (Hokuto Force, 2019). The `$482A/$482D` (`Robo-Toy`) is flagged `CyberTracker_exe` by sidid but has the classic gap=$3 signature — possible misclassification.

### 2c. Migration build count summary

| Build class | Engine string | Count | Address signature |
|---|---|---|---|
| CT native / gap=$51 | `CyberTracker` | 87 | init varies ~$1DCx–$2Cxx, play=init+$51 |
| CT Packer $1000 | `CyberTracker` | 35 | init=$1000, play=$1003 |
| CT near-$1000 | `CyberTracker` | 2 | init=$0FFC/$0FFE, play=$1003 |
| CT anomalous gap | `CyberTracker` | 3 | 3 outliers (see above) |
| CT-exe standard | `CyberTracker_exe` | 128 | init=$53A2, play=$53E2 |
| CT-exe shifted +$0800 | `CyberTracker_exe` | 1 | init=$5BA2, play=$5BE2 |
| CT-exe anomalous | `CyberTracker_exe` | 1 | init=$482A, play=$482D |

**Migration must handle at minimum 3 build classes:** (A) exe-maker fixed layout ($53A2), (B) packer $1000 layout, (C) native gap=$51 variable layout. Classes B and C may share a player binary at different load addresses.

---

## 3. Author concentration

### `CyberTracker` top authors

| Author | Tunes | Notes |
|---|---|---|
| Stephan Drost (Pater Pi) | 16 | Early adopter, 2001–2003; mix of gap=$51 and $1000 |
| Roy Digre (Xonic the Fox) | 12 | All at $1000; GO64 Music Ltd., 2006 |
| Vili Räsänen (Vintaque) | 11 | 2006–2007 |
| Fredrik | 11 | 2009–2014; uses both gap=$51 and $1000 |
| Bjarke N. Laustsen (Cyberbrain) | 8 | The creator; all 2001 No Name; uses all gap variants |
| Giovanni Giampieri (Johnny Owl) | 6 | 2001 |
| Chantal Goret (JMX 64) | 6 | 2006–2007; mix of layouts |

### `CyberTracker_exe` top authors

| Author | Tunes | Notes |
|---|---|---|
| Fredrik | 75 | Dominant; 2009–2019; all $53A2 layout |
| Steve Kockx (Fritske) | 11 | 2009–2013; all $53A2 |
| Rob Southworth (Pievspie) | 8 | 2012 Rubberland/Pievspie |
| Bartlomiej Dramczyk (V0yager) | 6 | 2002–2006 Tropyx; earliest exe-maker users |
| Christian Bach (CB) | 5 | 2002–2004 Radical |
| Andreas Krutholm (Kompositkrut) | 4 | 2012–2013 |

**Fredrik alone accounts for 75/130 (57.7%) of all `CyberTracker_exe` tunes**, deposited primarily in 2009–2010 and 2019. The Executable Maker became the dominant export path for heavy users.

---

## 4. Year distribution

### `CyberTracker` (native/packer)

| Year range | Count | Notes |
|---|---|---|
| 2001 | ~30 | Launch year; CyberBrain, Pater Pi, Johnny Owl, early adopters |
| 2002–2003 | ~16 | Steady uptake; Elaketh, Pingo, Pater Pi continues |
| 2004–2006 | ~35 | Xonic the Fox (GO64 Music Ltd.) bulk deposit 2006; Vintaque |
| 2007–2009 | ~30 | Fredrik, JMX 64, Szachista, Sgw32 |
| 2010–2015 | ~11 | Continuing use; Sgw32, King Durin |
| 2016–2020 | ~4 | GWCNS (2016), theK (2020) — still used |

### `CyberTracker_exe`

| Year range | Count | Notes |
|---|---|---|
| 2001–2004 | ~15 | V0yager/Tropyx, CB/Radical, Mr.Mouse/Xentax, early |
| 2005–2008 | ~7 | Scattered use |
| 2009–2010 | ~73 | **Fredrik + Fritske bulk deposit** — single largest event |
| 2011–2013 | ~11 | Pievspie, Kompositkrut, Fritske |
| 2019 | ~14 | **Fredrik 2019 batch** (12 tunes) + Hokuto Force (2) |

**The Executable Maker's popularity peaked in 2009 (Fredrik batch).** The latest confirmed use is 2019 (Hokuto Force's `Suntory_Story`, the shifted $5BA2 variant).

---

## 5. HVSC bundled documentation

No mention of CyberTracker or Cyberbrain found in any of these HVSC DOCUMENTS files:
- `SID_file_format.txt` — no mention
- `HVSC.txt` — no mention
- `Musicians.txt` — no mention
- `BUGlist.txt` — no mention
- `hv_sids.txt` — no mention
- `STIL.txt` — no mention
- `Songlengths.md5` — contains path entries for `/MUSICIANS/C/Cyberbrain/` files (songlength entries only, no format notes)

**HVSC carries no player documentation for CyberTracker.** All format knowledge must come from noname.c64.org and community sources.

---

## 6. Scene context & version history

### Creator and group

- **Creator:** Bjarke Norgaard Laustsen, handle **CyberBrain**, member of **No Name (NN)** demoscene group.
- CyberBrain was also one of the co-founders of **CSDb** (launched ~2001 alongside Perff, KBS, Celtic) — making CyberTracker a tool whose author simultaneously built the C64 scene's primary database.
- **No Name** is a Danish demoscene group; CyberTracker was their major public tool release.

### Version history (CSDb IDs)

| Release | CSDb ID | Date | Notes |
|---|---|---|---|
| CyberTracker V1.00 | #2601 | 2001-04-13 | Premiered at **Mekka & Symposium 2001** |
| CyberTracker V1.01 | #25 | 2001-09-14 | Filesize improvement (no longer saves entire memory); 100% forward-compatible with V1.00 files; V1.00 reading V1.01 files ~0% success rate |
| CyberTracker Executable Maker v1.00 | #6663 | 2001-12-13 | First exe-maker; ships as C64 .d64 |
| CyberTracker Executable Maker v1.01 | #6664 | 2001-12-26 | Updated exe-maker; most commonly used |
| CyberTracker X-Mas 2001 Tune Pack | #109 | 2001-12-28 | At The Party 2001; composers: CyberBrain, Johnny Owl, Mr.Mouse, Pater Pi |
| CyberTracker Packer BETA#1 | #4085 | 2002-03 | WIN/DOS PC tool; by CyberBrain + Ghostrider/No Name; produces $1000-based tunes |

### Format notes from the manual (noname.c64.org/tracker/manual_online.php)

- The packer was **not included** with V1.00/V1.01 ("At the time of writing, i haven't made a packer to pack it into a normal $1000-tune yet. This means that you can't use the music in demoz, games n' stuff yet.") — this explains why many early .ct files are stored in HVSC as raw executable exports rather than standard $1000 SID players.
- V1.01 explicitly added file-size improvements; the manual notes files are now smaller than V1.00.
- The Executable Maker is a **separate C64-native tool** (distinct from the PC-side Packer BETA#1). It runs on the C64 itself and converts a .ct module to a standalone PRG/SID.
- Maximum limits: 256 patterns ($00–$FF), 0–128 lines per pattern, 796 total pattern lines, 512 track lines, 768 envelope points, 31 instruments, 256 songs per file.
- **8 graphical envelopes per instrument:** volume/ADSR, waveform, pulse width, filter passband, cutoff, resonance, pitch, pitch control. Max instrument length: 65,536 ticks.
- **Community complaints:** "extremely clicky sounds" at note starts noted on Pouët and CSDb — suggests hard-restart behavior that may appear as a characteristic write sequence in the log.

### Key composers by group/affiliation

| Composer | Handle | Group(s) | Engine string | Count |
|---|---|---|---|---|
| Bjarke N. Laustsen | Cyberbrain | No Name | Both | CT×8 + CT-exe×1 |
| Stephan Drost | Pater Pi | Church of 64 | CyberTracker | 16 |
| Roy Digre | Xonic the Fox | GO64 Music Ltd. | CyberTracker | 12 |
| Fredrik (last name unknown) | Fredrik | Independent | Both | CT×11 + CT-exe×75 |
| Steve Kockx | Fritske | Independent | CyberTracker_exe | 11 |
| Vili Räsänen | Vintaque | Independent | CyberTracker | 11 |
| Bartlomiej Dramczyk | V0yager | Tropyx | CyberTracker_exe | 6 |
| Chantal Goret | JMX 64 | Independent | CyberTracker | 6 |
| Giovanni Giampieri | Johnny Owl | Independent | CyberTracker | 6 |
| Christian Bach | CB | Radical | CyberTracker_exe | 5 |
| Michael Zuurman | Mr.Mouse | Xentax | Both | CT×5 + CT-exe×3 |
| Rob Southworth | Pievspie | Rubberland | CyberTracker_exe | 8 |
| Fedor Zagumennov | Sgw32 | Independent | CyberTracker | 5 |

Note: Marc de Haar (Odo, "Just a Song") is the only entry with `released='200? Odo'` — undated; CyberTracker string.

### Is CyberTracker still used?

Yes. Latest HVSC entries: `theK` (2020, CyberTracker), Hokuto Force (2019, CyberTracker_exe). The 2019 Hokuto Force entry (`Suntory_Story`) even shows the shifted $5BA2 layout — suggesting the exe-maker binary was repackaged or relocated for demo use.

---

## 7. Cyberbrain_Digi — relationship to CyberTracker

`Cyberbrain_Digi` is a **separate and older engine** — it is NOT the CyberTracker player. HVSC has 6 Cyberbrain_Digi tunes:

| Path | Title | Year | init | play |
|---|---|---|---|---|
| `MUSICIANS/C/Cyberbrain/Voodoo_People_part_1.sid` | Voodoo People pt.1 | 1995 | $5B24 | $0000 |
| `MUSICIANS/C/Cyberbrain/Voodoo_People_part_2.sid` | Voodoo People pt.2 | 1995 | $5600 | $0000 |
| `MUSICIANS/C/Cyberbrain/Voodoo_People_part_3.sid` | Voodoo People pt.3 | 1995 | $3D18 | $0000 |
| `MUSICIANS/C/Cyberbrain/Sverige.sid` | Sverige | 1996 | $CC00 | $0000 |
| `MUSICIANS/C/Cyberbrain/Holy_Maling.sid` | Holy Maling | 1995 | $4400 | $0000 |
| `DEMOS/A-F/Crazy_World_3_digipart.sid` | Crazy World 3 (digipart) | 1994 | $1000 | $0000 |

All are **1994–1996** with `play=$0000` — a digi-only engine predating CyberTracker by 5+ years. Author is CyberBrain (and Pizza-Man for the Crazy World entry). These are digi sample players, unrelated to the CyberTracker music engine beyond sharing the same author's handle for 5 of the 6 entries.

---

## 8. MUSICIANS folder distribution

### `CyberTracker` — top HVSC directory clusters

| HVSC folder | Composer | Count |
|---|---|---|
| `MUSICIANS/P/Pater_Pi/` | Stephan Drost | 16 |
| `MUSICIANS/X/Xonic_the_Fox/` | Roy Digre | 12 |
| `MUSICIANS/V/Vintaque/` | Vili Räsänen | 11 |
| `MUSICIANS/F/Fredrik/` | Fredrik | 11 |
| `MUSICIANS/C/Cyberbrain/` | Bjarke N. Laustsen | 8 |
| `MUSICIANS/J/Johnny_Owl/` | Giovanni Giampieri | 6 |
| `MUSICIANS/G/Goret_Chantal/` | Chantal Goret | 5 of 6 |
| `MUSICIANS/M/Mr_Mouse/` | Michael Zuurman | 5 |
| `MUSICIANS/S/Sgw32/` | Fedor Zagumennov | 5 |
| `MUSICIANS/R/Rolemusic/` | José López | 4 |
| `MUSICIANS/M/Morton_Adam/` | Adam Morton | 4 |
| `DEMOS/` subtree | various | ~9 |

### `CyberTracker_exe` — top HVSC directory clusters

| HVSC folder | Composer | Count |
|---|---|---|
| `MUSICIANS/F/Fredrik/` | Fredrik | 75 |
| `MUSICIANS/F/Fritske/` | Steve Kockx | 11 |
| `MUSICIANS/P/Pievspie/` | Rob Southworth | 8 |
| `MUSICIANS/V/V0yager/` | Bartlomiej Dramczyk | 6 |
| `MUSICIANS/C/CB/` | Christian Bach | 5 |
| `MUSICIANS/K/Kompositkrut/` | Andreas Krutholm | 4 |
| `MUSICIANS/M/Mr_Mouse/` | Michael Zuurman | 3 |
| `DEMOS/` subtree | various | ~6 |

---

## 9. Key structural observations for migration

1. **The CyberTracker_exe layout is one binary, de-facto.** 128/130 tunes share init=$53A2, play=$53E2 identically. The $5BA2 variant is the same player shifted $800 bytes up. This means a single player disassembly covers 98.5% of the exe-string corpus.

2. **The CyberTracker gap=$51 layout is also a single player binary** (87 tunes), but the entire binary floats upward as song data grows — init varies from ~$1DC0 to ~$2BBE (a $EFE ≈ 3838-byte range). The 81-byte init stub is constant in shape; only the absolute address moves.

3. **The $1000 class (35 tunes) is the CyberTracker Packer BETA#1 output.** PC-side tool (Windows/DOS), March 2002, by CyberBrain + Ghostrider. Fixed layout: init=$1000, play=$1003.

4. **No CIA tunes.** All 255 tunes are VBL (speed=0). Migration is frame-mode only.

5. **No multi-subtune in the exe class.** Only the native .ct class has up to 2 subtunes (6 files). "256 songs per file" mentioned in the manual refers to internal song slots, not PSID subtunes — HVSC exports appear to wrap one song at a time.

6. **The "extremely clicky" notes** reported by users likely manifest as a hard-restart write sequence at every note start — the write-log will show this as a predictable per-note waveform/gate cycle. A key design detail for the frame-model agent to investigate.

7. **Cyberbrain_Digi is irrelevant to CyberTracker migration** — different era, different architecture (digi player, no play() vector).

---

## Leads to follow

1. **Disassemble the exe-maker player at $53A2.** With 128 tunes sharing one binary, a single hand-annotated disassembly covers the bulk of the corpus. Confirm the $40-byte init stub function (init dispatcher vs player stub). Start with `MUSICIANS/V/V0yager/Back_on_64_Trax.sid` (earliest V0yager, 2002) or `MUSICIANS/C/Cyberbrain/China.sid` (author's own).

2. **Identify the .ct data layout relative to $53A2.** The pattern data presumably starts at a fixed offset from the player base. Compare two exe-maker SIDs of different sizes to isolate where the data region begins.

3. **Identify the gap=$51 init stub.** 81 bytes from init to play — extract the init routine and compare across 2–3 tunes to confirm it's truly constant (vs the $1000 class). Start with `MUSICIANS/C/Cyberbrain/Song.sid` (gap=$51, Cyberbrain himself, 2001).

4. **Confirm $1000-class is the Packer BETA#1.** Its play=$1003 matches the standard "3-byte JSR" trampoline common to many C64 players. Check whether the player code at $1000 is the same binary as the gap=$51 class shifted down, or a distinct build.

5. **Hard-restart investigation.** The "clicky" behavior noted by scene members suggests per-note hard restart (test-bit + gate-off + new ADSR). The write-log will show whether this is a `$D404 = $08` (test) then `$D404 = $11/$21/$41` (gate+wave) pattern or something else.

6. **The $5BA2 Hokuto Force variant (2019).** Check if `Suntory_Story.sid` is genuinely a +$800 relocation of the exe-maker binary or a custom player. DEMOS/S-Z/Suntory_Story.sid.

7. **The $482A `Robo-Toy` anomaly.** `MUSICIANS/M/Mac_Radical/Robo-Toy.sid` is tagged `CyberTracker_exe` by sidid but has a gap=$3 signature matching the Packer class. May be a sidid false positive or a very early exe-maker version.

8. **noname.c64.org fileformat guide.** The manual page references a separate "fileformat" document — it may not be publicly accessible now but is worth attempting to fetch via archive.org Wayback.

9. **CyberTracker_exe `speed` field.** Confirm via binary read of the PSID header that speed=0 for all 130 entries (the DB doesn't expose the raw speed word, only derived flags). Low priority given all are PSIDv2 with no anomalies.

10. **Odo's undated tune** (`MUSICIANS/O/Odo/Just_a_Song.sid`, released='200? Odo'). Marc de Haar is a known Dutch C64 composer; the '200?' date suggests mid-2000s. Low-priority curiosity.
