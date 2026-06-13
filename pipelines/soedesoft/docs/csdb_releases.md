# SoedeSoft / Soundmaster — CSDb Release History and Technical Commentary

<!-- PROVENANCE
source_urls:
  - https://csdb.dk/release/?id=10735   (Soundmaster V1.0 / Fire-Eagle, Feb 1989)
  - https://csdb.dk/release/?id=90307   (Soundmaster V3.1 / Soedesoft, 1989)
  - https://csdb.dk/release/?id=91649   (Contact Demo / Soedesoft, 1989)
  - https://csdb.dk/scener/?id=5983     (Jeroen Soede scener page)
  - http://artscene.textfiles.com/music/c64/HVSC/SoedeSoft/  (HVSC SID listing)
  - https://remix64.com/interviews/interview-michiel-soede-www-soedesoft-com.html (interview)
  - https://www.vgmpf.com/Wiki/index.php?title=Jeroen_Soede
  - https://www.soedesoft.com/  (modern SoedeSoft / SIDmaster plugin page)
  - http://www.pouet.net/groups.php?which=8188
  - hvsc84.db (local HVSC #84 catalogue, engine='SoedeSoft', 929 entries)
  - /home/jtr/sidfinity/deprecated/gt2_pipeline/tools/sidid.cfg (byte signatures)
fetched_via: curl Firefox UA + WebFetch + local DB query
fetch_date: 2026-06-13
reliability: PRIMARY for CSDb page data (HTML fetched directly);
             SECONDARY for interview (via WebFetch extraction);
             LOCAL for sidid.cfg signatures and hvsc84.db stats.
-->

---

## Authors

| Name | Role | Dates active (C64) |
|---|---|---|
| **Jeroen Soede** | Player code / programming | 1985–1989 (SoedeSoft), then Amiga |
| **Michiel Soede** | Editor / compositions | 1985–1989 (SoedeSoft), then Amiga |

Both born 1970; twins; Netherlands. Jeroen focused on the player engine; Michiel on the editor
UI and compositions. Their first C64 work predates the Soundmaster name (see SIDs from 1985–1986
like "Yep" and "Ritme" in the HVSC listing, attributed to SoedeSoft).

Group affiliations: **SoedeSoft** (founders) and **Fire-Eagle** (1987–1989). The V1.0 release
was distributed under the Fire-Eagle label; V3.1 under Soedesoft directly.

Jeroen later composed music for games (Artax C64 1989, Future Shock Amiga 1991, etc.) and
continues to compose under the SoedeSoft name; the modern SIDmaster Reason plugin (post-2010)
explicitly implements "effects used in the old days of the C64 based on SoedeSoft's original
music routine of the 80's (such as arpeggios, wave patterns, modulating the pulse width or
filter)."

---

## Version Timeline

### SoedeSound Editor V1.0 (pre-Soundmaster branding, ~1987–1988)

The earliest SoedeSoft SIDs in HVSC date from 1985–1986 ("Yep", "Ritme", "Stijl", "Real_Crazy",
etc.). These use the early incarnation of the engine before it was versioned as "Soundmaster."

### Soundmaster V1.0 — CSDb #10735

- **Release date:** February 1989
- **Group:** Fire-Eagle (= SoedeSoft / Fire-Eagle joint release)
- **CSDb type:** C64 Tool
- **AKA:** Sound Master v1.0, Sound Editor from FE
- **Credits:**
  - Code: Jeroen Soede (Fire-Eagle), Michiel Soede (Fire-Eagle)
  - Music: Jeroen Soede (Fire-Eagle), Michiel Soede (Fire-Eagle)
- **Demo SIDs included:** Airwolf (Michiel Soede), Last Ninja Mix (Michiel Soede)
- **Intro:** Fire Eagle Intro 02 by Fire-Eagle / Soedesoft
- **Downloads:**
  - `http://csdb.dk/getinternalfile.php/115262/Soundmaster_V1_FireEagle.t64`
  - `https://csdb.dk/getinternalfile.php/239985/Soundmaster V1.0 [fe].d64`
- **CSDb user comment (Fred, March 2013):** "I've replaced the download with the Fire Eagle only
  release since this release is the non-import version. This release was present on a disk with
  some demos released in February 1989 so I think this one is released in 1989 as well."
- **OPEN:** No V2.x releases found on CSDb — the jump from V1.0 to V3.1 suggests either
  unreleased intermediate versions or a renumbering.

### Soundmaster V3.1 — CSDb #90307

- **Release date:** 1989
- **Group:** Soedesoft
- **CSDb type:** C64 Tool
- **AKA:** Sound Master V3.1
- **Credits:** No credits listed in the CSDb entry (the release was added later from preserved
  copies)
- **Downloads:**
  - `http://csdb.dk/getinternalfile.php/87430/soundmaster3.1.prg` (384 downloads as of fetch)
  - `http://csdb.dk/getinternalfile.php/115254/Soundmaster_v3.1_[german].pdf` (166 downloads)
    — German-language manual PDF, 18 pages, written by Walter Konrad (see `csdb_manual_de.md`)
  - `http://csdb.dk/getinternalfile.php/115243/Soundmaster_V3_1_Docs.prg` (136 downloads)
    — C64 in-program documentation
- **CSDb user comments:**
  - Fred (23 March 2013): "I've found the Docs file made by SoedeSoft and uploaded it. I've
    also uploaded a german PDF file written by Walter"
  - DRAX (5 September 2010): "I also did a couple of tunes in this editor... and I still trying
    to find them... Might have sent them to some nato or noise members back then... Maduplec? ;)"
  - Stainless Steel (5 June 2010): "I actually liked this one back then."
- **Note on T64 at getinternalfile.php/90307:** Fetching the release ID as an internal file
  returns a T64 tape image titled "DIGITAL DUNGEON" — this is NOT the manual; it is an
  unrelated file stored at that ID number. The manual is at /115254/, the editor at /87430/.

### Soundmaster V3.2

- No CSDb release page found for V3.2 specifically. The version is identified by sidid byte
  signatures (see below) and appears in HVSC SIDs, indicating a V3.2 was distributed (likely
  embedded with music files rather than as a standalone tool release on CSDb).

---

## Contact Demo — CSDb #91649

- **Release date:** 1989
- **Group:** Soedesoft
- **CSDb type:** C64 Music Collection
- **Credits:**
  - Music: Jeroen Soede (Fire-Eagle), Michiel Soede (Fire-Eagle)
- **SIDs included:**
  - Airwolf (Michiel Soede)
  - Contact Demo tune 1 (Jeroen Soede)
  - Funky Stuff (Jeroen Soede)
  - MacGyver Title (Jeroen Soede)
  - Snik v2 (Jeroen Soede)
  - Swing (Michiel Soede)
- **Download:** `http://csdb.dk/getinternalfile.php/89015/Contact_Demo.t64`
- **CSDb user comments:**
  - marty (8 September 2014): "Funny, that's right around the corner, but never heard about
    them at all."
  - GT (28 July 2010): "A nice collection of tunes that deserves a comment. Really digged the
    Funky_Stuff.sid back then, and still do. When it comes to Airwolf I prefer Charles Deenen's
    version."

This is the known contact/demo disk that Soedesoft used to distribute sample music alongside
the editor. Standard practice for commercial/semi-commercial C64 music editors of the era.

---

## Pouet.net

SoedeSoft entry: http://www.pouet.net/groups.php?which=8188 (added 23 December 2007)

Productions listed (5 total, all Commodore 64):
1. Cracktro — "Crucible ++" (with Fire-Eagle, 2007)
2. Intro — "Fire Eagle Intro" (1989)
3. Demo — "Magic Colours" (with Fire-Eagle)
4. Musicdisk — "Music from Hammer & Jarre" (with Fire-Eagle)
5. Demo — "Trail Mix" (with Fire-Eagle, 1988)

No technical comments about Soundmaster on Pouet. The group is a minor entry; most SoedeSoft
productions are catalogued under CSDb and HVSC rather than Pouet.

---

## HVSC Catalogue Coverage

Data from hvsc84.db (local HVSC #84 SQLite catalogue):

| Metric | Value |
|---|---|
| Total SIDs with engine='SoedeSoft' | **929** |
| SIDs in MUSICIANS/S/SoedeSoft/ (textfiles listing) | 67 (SoedeSoft's own compositions) |
| Other authors using the engine | ~862 SIDs by ~150+ composers |
| Date range (released field) | 1988 ("1988 Diamonds") to 2025 ("2025 Slackers") |
| SIDs with 1 subtune | 899 (96.8%) |
| SIDs with 2 subtunes | 12 |
| SIDs with 3 subtunes | 6 |
| Multi-subtune (4+) | 12 total |

### Top authors by SID count (engine='SoedeSoft'):

| Author | SID count |
|---|---|
| Sascha Nagie (celticdesign) | 156 |
| Vulgarik | 70 |
| Tomas Danko | 52 |
| Stello Doussis | 44 |
| Vidar Bang (Drumtex) | 40 |
| Jeroen Soede | 38 |
| Anders Elmén (Moon) | 37 |
| Wolfgang Reszel (Tekl) | 30 |
| M. Nilsson-Vonderburgh (Yankee) | 29 |
| Tom Hoffer (MAC2) | 28 |

Jeroen Soede himself accounts for only 38 of 929 SIDs — the engine was widely adopted by other
composers across the late 1980s and 1990s.

### Common load/init/play address pairs:

| Load | Init | Play | Count | Notes |
|---|---|---|---|---|
| ? | $6000 | $6006 | 309 | "R" save: music+routine at $6000 |
| ? | $2000 | $2106 | 135 | — |
| ? | $2029 | $2106 | 45 | — |
| ? | $1027 | $1106 | 36 | — |
| ? | $1029 | $1000 | 35 | — |
| ? | $1000 | $1003 | 34 | — |
| ? | $3803 | $3806 | 29 | — |
| ? | $6000 | $6003 | 29 | Variant: play offset +3 not +6 |
| ? | $8427 | $8506 | 22 | High-memory load |
| ? | $1029 | $1106 | 13 | — |

The play address offset patterns ($6006 vs $6003, $2106 vs $1106) suggest the init/play gap
varies by version or by how the player was assembled/relocated. The $6000/$6006 pair (309 SIDs)
corresponds to the V3.1 manual's documented `SYS $6000` standalone entry.

---

## HVSC SID Listing (SoedeSoft's own compositions — textfiles.com)

Source: `http://artscene.textfiles.com/music/c64/HVSC/SoedeSoft/` — 67 files, 405,974 bytes
total. Notable titles and approximate date range:

Early era (1985–1987): Yep, Ritme, Stijl, Real_Crazy, Gloom, Luc, Mess, Walkaway, Spooky,
Sloom, Harikiri, Biggles, Action, Choice, Lazer_Duel, Crazy_2, Science_Fighter, Sad_Day,
Real_Heavy, Sphinx_Amiga, Boozy, Snik, Delta, Showmusic, Burp, War_Music, Kazkade_preview,
Last_Ninja_Mix, MacGyver_Title, Magic_Colours, Magic_Drums_PSID, Magnetic_Fields_Part2_PSID,
Forever_Tonight_PSID, Let_It_Be_PSID, Yahtzee

Mid era (1988–1989): Airwolf, Airwolf_Title, 7_Runes, Awful, Battlestar_Galactica, Blobber,
Contex, Drifty, Dull, Filter_Mania, Floep, Funky_Stuff, Funny_Stuff, Ghostbusters_Tune,
Ik_ben_vandaag_zo_vrolijk, JT_Intro_Clone, Jing_Jang, Mania, Matt_Gray_Style, Magic_Funk,
New_Music_2, Polter_Geist, Scoutsmusje, Science_Fighter_1, Simple_Music, Swing, TrailMix,
TrailMix_intro

Late era (1988–1989, likely V3.x): Artax, Hollywood, Years_Later

Several titles contain "PSID" in their filename, indicating non-standard (digitised sample or
non-relocatable) content: Forever_Tonight_PSID, Let_It_Be_PSID, Magic_Drums_PSID,
Magnetic_Fields_Part2_PSID — these are likely the "Magic Drums" digi-sample tunes Michiel Soede
was known for.

---

## sidid Byte Signatures (from sidid.cfg)

Three player variants are fingerprinted:

```
SoedeSoft
(Soundmaster_V1.0)
9D ?? ?? BD ?? ?? D0 ?? 18 B9 ?? ?? 7D ?? ?? 99 ?? ?? 99 00 D4 B9 ?? ?? 69 ?? 99 ?? ?? 99 01 D4 4C END

(Soundmaster_V3.1)
A9 ?? 9D ?? ?? 4C ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60 END

(Soundmaster_V3.2)
A9 ?? 9D ?? ?? 4C ?? ?? 18 BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ?? 7D ?? ?? 9D ?? ?? BD ?? ?? 9D 00 D4 BD ?? ?? 9D 01 D4 60 END
```

The top-level `SoedeSoft` tag lacks a standalone signature line — it groups the three
version-specific sub-tags.

**V3.1 vs V3.2 delta:** V3.2 adds `18 BD ?? ?? 7D ?? ?? 9D ?? ??` before writing to $D400/$D401
(SID freq low/high). The `18` is `CLC`, `7D` is `ADC abs,X`, suggesting V3.2 adds an offset
(portamento/transpose accumulation?) to both freq bytes before writing, where V3.1 does a
simple indexed store. This may implement the portamento count differently.

**V1.0 vs V3.x:** The V1.0 signature is substantially different in structure — it includes `D0`
(BNE branch), separate `99 00 D4 / 99 01 D4` writes (freq lo/hi via stack-indexed store), and
a `69` (ADC #imm) — suggesting V1.0's write path uses a different loop/dispatch structure.

---

## Technical Context from Interviews

From the Remix64 interview with Michiel Soede
(https://remix64.com/interviews/interview-michiel-soede-www-soedesoft-com.html):

- "My brother created the routine, and I created an editor" — clear division of labour
- Motivation: Chris Huelsbeck's Soundmonitor had limitations — "the creation of sounds was too
  limited and the size of the music was too much" — so they built from scratch
- "Nothing was ripped" — completely original engine
- Copying Rob Hubbard's drum sounds was "one of the first things they did" when building the
  engine — the characteristic "drum tick" effect ($7F arp sentinel + $81 waveform) is the
  technical mechanism (see manual notes)
- The Amiga successor "SoundMaster II" was "based on our C64 routine" — architectural lineage

From the VGMPF wiki on Jeroen Soede:
- Born 21 November 1970
- "They worked mainly on demos and later on a few games"
- Jeroen plays electric lead guitar as of 2001

From the modern SoedeSoft.com SIDmaster plugin description:
- "Implements effects used in the old days of the C64 based on SoedeSoft's original music
  routine of the 80's (such as arpeggios, wave patterns, modulating the pulse width or filter)"
- This confirms the four core effects named in the manual are the defining features of the engine.
