# Cyberlogic SoundStudio — Corpus Shape, Address Clusters & Scene Context

## Provenance

| Field | Value |
|---|---|
| author | Claude (sonnet-4-6), SIDfinity agent |
| content_date | 2026-06-14 |
| fetch_date | 2026-06-14 |
| primary_sources | hvsc84.db (read-only), hvsc85/DOCUMENTS/STIL.txt, hvsc85/DOCUMENTS/Musicians.txt |
| web_sources | csdb.dk/release/?id=170632, csdb.dk/scener/?id=3288, archive.org/details/Demons_of_Sound_1992_Demons_of_Sound, hvmec.altervista.org/blog/?p=224, github.com/cadaver/sidid (sidid.nfo) |
| reliability | HIGH for DB/HVSC-local facts; MEDIUM for CSDb web extracts (page structure may have changed) |

---

## 1. Tool Identity

**Cyberlogic Sound Studio (CSS)**, version V4.0, 1992.
- Also referred to as C.S.S.
- sidid.nfo entry: `NAME: Cyberlogic Sound Studio / AUTHOR: Oliver Klee & Sascha Nagie / RELEASED: 1991`
- CSDb release #170632 dates the V4.0 disk image to 1992; sidid uses 1991 (likely earlier version).
- Code: Oliver Klee (handle: Odi); Music/Design/Concept: both creators.
- Available on CSDb as .d64 disk image (235 downloads recorded as of 2026-06-14).
- HVMEC classifies it as a "tracker" — 3-voice composition + sequencing tool for C64.
- Keyboard interface with CBM-key modifier (CBM-M = start, CBM-P = stop/pause, CBM-D = disk menu, 15+ other shortcuts).
- Odi's STIL notes confirm: CSS bundled its own player; tunes can be packed with the CSS packer (`Underground-Rock.sid` STIL: "The first tune to be packed with the packer of the CSS!").
- The CSS player supports a "special low-raster version" (~$10 raster lines, comparable to JCH Player V19 / Music Assembler) — noted in Odi's STIL for `Pocket_Funk.sid`.
- Odi notes a filter quirk: "I had figured out what number to add to the filter byte to get roughly the same sound as with normal filters" (`A_Groovy_Night.sid` STIL) — the filter handling differs from standard SID players.

---

## 2. HVSC Corpus Shape

### 2.1 Totals

| Metric | Value |
|---|---|
| Total SIDs tagged Cyberlogic_SoundStudio | 196 |
| PSID version | 2 (all 196) |
| CIA-timed (speed != 0) | not tracked in hvsc84.db schema; field absent |
| Multi-subtune SIDs (n_subtunes > 1) | 9 |
| Single-subtune SIDs | 187 |
| Distinct load/init/play address triples | 30 |

### 2.2 Subtune distribution

| n_subtunes | count |
|---|---|
| 1 | 187 |
| 2 | 3 |
| 3 | 1 |
| 4 | 3 |
| 12 | 1 |
| 20 | 1 |

Largest: `The_Blue_Ninja/Stroke_World.sid` (20 subtunes, 2053 s total).
Second: `Nagie_Sascha/Maze_of_the_Mummy.sid` (12 subtunes, 1332 s total — a game soundtrack from 2014 Magic Cap).

### 2.3 Songlength distribution

| Bucket | Count |
|---|---|
| < 1 min | 12 |
| 1–3 min | 93 |
| 3–5 min | 69 |
| 5–10 min | 17 |
| > 10 min | 5 |

- Min: 10 s (`Odi/Happy_Birthday.sid`)
- Max: 2053 s (`The_Blue_Ninja/Stroke_World.sid`, 20-subtune game OST)
- Mean: ~208 s (~3.5 min)
- Median is in the 1–3 min bracket — a tracker-typical loop length.

---

## 3. Address Cluster Table

All 196 SIDs have `load_addr = $0000` (PSID relocation flag: binary loads to a custom address). The `init_addr` and `play_addr` distinguish the relocation clusters.

### 3.1 Canonical clusters (corpus-wide)

| init_addr | play_addr | Count | Notes |
|---|---|---|---|
| **$1000** | $1003 | **133** | Canonical CSS layout (68%) |
| **$6000** | $6003 | **13** | Secondary — SID Nation series + Timeout tunes (7%) |
| $0FF4 | $1003 | 6 | Near-$1000 init, play stays at $1003 |
| $0FF0 | $1003 | 5 | Near-$1000 init |
| $0FF6 | $1003 | 5 | Near-$1000 init |
| $0FA0 | $1003 | 2 | Near-$1000 init |
| $0FD0 | $0FE2 | 2 | Near-$1000, non-standard play |
| $3300 | $3303 | 2 | Protovision intros (The_Blue_Ninja) |
| $6C00 | $6C03 | 2 | Lemmings tunes (The_Blue_Ninja) |
| $8000 | $8003 | 2 | Funk_Lake + Exodus_Level_1 |
| $A000 | $A003 | 2 | Haphazard + Vectormania_2_tune_2 |
| $E000 | $E003 | 2 | 7-3.sid + LaxMagazine.sid (Laxity releases) |
| $EB00 | $EB03 | 2 | SID_Nation_XII_8580_edit + No_More_Progress |
| $EC00 | $EC03 | 2 | Political_Maggots + Zero_Zone |
| 14 singletons | various | 14 | Game OSTs, previews, specialized relocations |

**Summary interpretation:**
- The `$1000 / $1003` pair is the canonical CSS player address — 133/196 = **68%** of the corpus.
- The `$6000 / $6003` cluster (13 tunes) is a systematic **secondary relocation** used entirely by Nagie's SID_Nation IV–XI series (all 2014 Genesis Project) plus The_Blue_Ninja's three Timeout tunes (1992–1993 Demons of Sound / Smash Designs). This is a deliberate alternate load point, likely a different version of the CSS player loaded at $6000.
- The `$0FFx` near-$1000 inits (6+5+5+2 = 18 tunes) are all Nagie_Sascha. Init precedes play by a short offset ($0FF0–$0FF6), but play remains at $1003. These are tunes where the init stub is placed just before the player — a known CSS packing variant (Odi's "Baroque_Parting" STIL describes stripping the player down to "almost nothing" for a zero-page version).
- X-Radical is the cleanest subset: all 28 tunes at $1000/$1003, no exceptions.
- Odi (Oliver Klee): 21/24 at $1000/$1003, 3 outliers (a preview at $1DBF/$1DD2, a loader tune at $1EFB/$1003, and one at $A000).

### 3.2 Per-artist canonical-address share

| Artist | Total | $1000/$1003 | $6000/$6003 | $0FFx near-$1000 | Other |
|---|---|---|---|---|---|
| Nagie_Sascha | 120 | 75 (63%) | 10 (8%) | 16 (13%) | 19 (16%) |
| Odi (Oliver Klee) | 24 | 21 (88%) | 0 | 0 | 3 (12%) |
| The_Blue_Ninja | 24 | 9 (38%) | 3 (12%) | 2 (8%) | 10 (42%) |
| X-Radical | 28 | 28 (100%) | 0 | 0 | 0 |

The_Blue_Ninja's high "Other" count reflects his game OST work (Ghost_Driver at $3E53, Metal_Dust at $4220, Stroke_World with init at $2100, Protovision intros at $3300, etc.) — standalone player stubs embedded in games.

---

## 4. Author & Folder Distribution

| HVSC folder | Real name | Handle | Count | Share |
|---|---|---|---|---|
| MUSICIANS/N/Nagie_Sascha/ | Sascha Nagie | celticdesign (DJ3D) | 120 | 61.2% |
| MUSICIANS/X/X-Radical/ | Frank Schanzenbächer | X-Radical | 28 | 14.3% |
| MUSICIANS/T/The_Blue_Ninja/ | Lars Hutzelmann | The Blue Ninja | 24 | 12.2% |
| MUSICIANS/O/Odi/ | Oliver Klee | Odi | 24 | 12.2% |

Nagie dominates with 61% of the corpus. The other three have nearly equal representation (12–14% each).

Source for real names: hvsc85/DOCUMENTS/Musicians.txt:
- `Nagie, Sascha (celticdesign {DJ3D}) / Demons of Sound - GERMANY`
- `X-Radical (Schanzenb cher, Frank) / Chromance - GERMANY` (encoding artifact around umlaut)
- `The Blue Ninja (Hutzelmann, Lars) / Demons of Sound - GERMANY`
- `Odi (Klee, Oliver) / MDG / Smash Designs - GERMANY`

**All four composers are German.**

---

## 5. Scene Context

### 5.1 Origin group: Demons of Sound (DOS)

The founding context is the German C64 group **Demons of Sound (DOS)**. Confirmed members in the CSS corpus:

- **celticdesign (Sascha Nagie)** — musician, core member; later: Security, Sunrise, Masters' Design Group (MDG), Genesis Project. Still releasing as of 2021.
- **The Blue Ninja (Lars Hutzelmann)** — coder & musician; later Protovision (game company). Musicians.txt: `Demons of Sound - GERMANY`.
- **Odi (Oliver Klee)** — coder & musician; later MDG, Smash Designs. The CSS tool co-creator. STIL for `Session_Tune.sid`: "I composed this piece at the Security group Meeting in December 1991 in Mannheim. Security (Demons of Sound [DOS] being part of it) was my second group at that time." Odi's STIL notes are the richest first-person source in the corpus — he uses CSS for 14/24 of his HVSC tunes.
- CSS V4.0 disk image (CSDb #170632) contains 25 demo tunes by Odi and Nagie, used as showcase tracks.
- DOS also co-released with Security (1991), Masters' Design Group, and Smash Designs.

Confirmed release: `Splitted Minds (1991)` — Code: The Blue Ninja, Music: celticdesign, releasing group: Demons of Sound / Security. Archive.org entry credits musician as "celtic."

### 5.2 X-Radical (Frank Schanzenbächer)

All 28 X-Radical tunes date to **1994–1995**, split between two groups:
- **Chromance** (13 tunes, 1994) — Hungarian group, but X-Radical credited as a German member; releases include `Quak_Quak` (529 s), `Techno_No_1` (483 s), `Temple_of_Love`.
- **Sound Style** (15 tunes, 1994–1995) — a music-label-style group or diskmag; all CSS, Germany.

Odi's STIL for `Uranium_Dioxide.sid` mentions: "For X-Radical of Nirvana." This is a separate Nirvana group reference (not the band), implying X-Radical was known to Odi by early 1993. X-Radical appears to have adopted CSS through the Demons of Sound / MDG network before going independent with Chromance/Sound Style.

### 5.3 The Blue Ninja (Lars Hutzelmann) — CSS as game engine

Lars Hutzelmann's CSS usage is distinctive: many of his tunes are embedded game soundtracks (Stroke_World game for Protovision, Metal_Dust, Ghost_Driver for CP Verlag, Protovision intros). The non-standard init addresses ($3300, $6C00, $4220, etc.) reflect game-specific memory maps where the CSS player is embedded alongside game code. This is the main driver of his high "Other" address count.

Notable: `Metal_Dust` (2005, Protovision) — a 4-subtune OST, total 1162 s. Released ~14 years after CSS first appeared, showing the player was still in production use for commercial C64 games in the 2000s.

### 5.4 Sascha Nagie (celticdesign) — long-running CSS composer

Nagie's 120 tunes span 1991 to 2021 — a **30-year active span** with CSS as his primary tool. Key observations:
- **1991–1993 Demons of Sound era**: ~35 tunes (canonical $1000 address, Odi's STIL notes collaborative "Sascha and I" origin on several).
- **2011–2016 return**: Joined Genesis Project (2013), prolific output through Genesis Project, Oxyron, Triad, Alpha Flight, Reset Magazine, Onslaught — international German demoscene groups.
- **SID Nation series** (I–XII, 2013–2014): 12 tunes across two address clusters ($1000 and $6000). The $6000 series (IV–XI and the 8580 edit of III) all released on Genesis Project 2014 — suggesting Nagie developed or adopted a second CSS player variant for this batch.
- `Oli_and_Sascha_Test.sid` — credited "Sascha Nagie & Oliver Klee" — a direct collaborative test piece from the DOS era.
- STIL note for `A_Real_Compose.sid`: released 1991–93, confirming the early window.
- Competition wins: `Raid_over_Germany` 1st at Arok 2014; `Quest_for_Peace` 1st at BCC Party 2015; `Jam_Pron` won CSDb online Summer SID Compo 2015.

### 5.5 Year / group release distribution

| Period | Releases | Primary groups |
|---|---|---|
| 1991–1993 | 68 | Demons of Sound (38 tunes), Oliver Klee self-releases (19 tunes) |
| 1994–1995 | 33 | Chromance (13), Sound Style (15), Rebels (3) |
| 1997–2010 | 7 | Masters' Design Group, Protovision, Cascade, DMAgic |
| 2011–2021 | 88 | Genesis Project (51), Laxity (7), Onslaught (5), Triad (3), others |

The corpus has two distinct activity peaks: the **1991–1993 founding era** and a **2013–2016 revival** (Nagie rejoining the active scene via Genesis Project).

---

## 6. HVSC Bundled Documentation

Checked: STIL.txt, Musicians.txt, hv_sids.txt, Creators.txt.

- **Musicians.txt**: All four composers confirmed with real names and GERMANY nationality.
- **STIL.txt**: **93 entries** found across the four musician folders. The Odi/Cyberlogic entries are the most informative — 14 tunes have detailed first-person STIL comments from Oliver Klee explicitly naming "the Cyberlogic Sound Studio... made by me and Sascha/MDG!" These are authoritative primary source text for the tool's history.
- **hv_sids.txt, Creators.txt**: No Cyberlogic-specific technical entries found.
- No dedicated Players.txt or format spec document exists in HVSC DOCUMENTS for CSS.
- No SID_file_format reference for CSS-specific data structure.

Key STIL quotes (Oliver Klee, confirmed first-person):
- Filter quirk: "I had figured out what number to add to the filter byte to get roughly the same sound as with normal filters." (`A_Groovy_Night`)
- Low raster version: "...it is possible to achieve low rastertime of about $10 (like Music Assembler/Voicetracker, JCH Player V19 or A.K.'s player)." (`Pocket_Funk`)
- CSS packer confirmed: "The first tune to be packed with the packer of the CSS!" (`Underground-Rock`)
- CSS player is bundled with tunes OR the zero-page variant strips it down (`Baroque_Parting`).
- Data Live '93 Dessau party: Odi's `Melt_Your_Brain` won 2nd place in the music competition there.

---

## 7. Technical Observations (for RE planning)

1. **Canonical init/play offset is +3 bytes**: At $1000, init at $1000, play at $1003. This means 3 bytes of preamble at init (likely `JMP $xxxx` or a short setup) before the play entry.
2. **Near-$1000 inits ($0FF0–$0FF6)** all play at $1003: the init vector is in the range $0FF0–$0FF6, not at $1000. This matches a "shrunken" player where the init/setup code is packed before the $1000 boundary but the play routine still lands at $1003.
3. **$6000 cluster** (13 tunes, all Nagie SID_Nation IV–XI + 3 Timeout tunes): systematic secondary relocation. Likely a deliberate different-address build of the same player for different memory map contexts.
4. **All load_addr = $0000**: PSID relocation header; the binary loads to the address given by init_addr (first two bytes of data in PSID v2 when load_addr=0 is the actual load addr embedded in the binary).
5. **All PSID version 2**: No version 1 or 3 in the corpus.
6. **No CIA-speed info** in hvsc84.db schema (speed field absent) — must be derived from PSID binary header field at offset $76 to determine if any tunes use CIA timing.

---

## 8. Leads to Follow

1. **Binary format RE**: Read the CSS player bytes at $1000 to determine the data layout — instrument table offset, pattern/sequence structure, effect table. Odi's STIL notes confirm vibrato (pulse width modification named in `Baroque_Parting`), portamento with arpeggio (`Cool_Is_Fool`), filter control (custom formula). Start with `Odi/Chips_in_Music.sid` (canonical $1000, simple tune, Odi STIL comment confirms CSS).

2. **CIA vs VBI timing**: Check PSID speed header bit (offset $76 in file) for the 196 SIDs. The sidid.nfo has no CIA flag for CSS — default assumption is VBI (50 Hz). Verify on a few tunes.

3. **Oli_and_Sascha_Test.sid**: The only joint credit tune. Worth examining for any init data that exposes the CSS format (test/debug artifacts).

4. **$6000 cluster vs $1000 cluster**: Are these the same player binary, just relocated? Or a different player version? Comparing the two at the 6502 level would answer this. Nagie's SID_Nation series (same artist, same tool, same period) is the ideal controlled experiment — `SID_Nation_III.sid` ($1000) vs `SID_Nation_III_8580_edit.sid` ($6000) are known related pairs.

5. **Near-$1000 init variants ($0FF0/$0FF4/$0FF6)**: These are all Nagie tunes. The init-before-$1000 pattern may reflect a different player version where extra init code was added (or the packer stub). Check if the bytes at $0FF0–$0FF6 are a JMP/JSR to a setup routine followed by a return to $1003.

6. **The Blue Ninja game OSTs**: `Stroke_World` (20 subtunes), `Metal_Dust` (4 subtunes), `Ghost_Driver` (3 subtunes) are game soundtracks. These may have custom embedded player versions with extended data layouts. Verify separately from the standalone CSS tunes.

7. **CSDb #170632 .d64 image**: Download and inspect for documentation files, format notes, or source hints embedded on the disk. The bundled 25 demo tunes may have uniform addresses that constrain the format.

8. **HVMEC page**: hvmec.altervista.org/blog/?p=224 references CSS V4.0 as a "tracker" with "15+ keyboard shortcuts." May have more technical detail on format if page has full text.

9. **X-Radical / Nirvana connection**: Odi's STIL for `Uranium_Dioxide` says "For X-Radical of Nirvana" — this places X-Radical in the Nirvana C64 group in the early DOS era, before his 1994 Chromance work. Trace this to understand CSS adoption path.

10. **Chromance / Sound Style group membership**: Frank Schanzenbächer / X-Radical's CSDb scener page (ID unknown) would confirm his group affiliations and whether CSS spread into Chromance via DOS network links.
