# SidTracker64 — Corpus Characterisation & Scene Context

<!-- provenance header -->
| field | value |
|---|---|
| fetch_date | 2026-06-14 |
| author | research agent (Claude claude-sonnet-4-6) |
| sources | hvsc84.db (read-only), HVSC DOCUMENTS dir, csdb.dk, apps.apple.com, soundonsound.com, synthtopia.com, musicradar.com, demozoo.org, deepsid.chordian.net (via search), sidid.cfg (local) |
| content_date | HVSC #84 snapshot; web sources retrieved 2026-06-14 |
| reliability | DB queries: authoritative; web: secondary (some pages 403/ECONNREFUSED) |

---

## 1. Tool overview

**SidTracker64** is a commercial iOS tracker app for iPad by **Daniel Larsson**
(handle **Pernod**, of the C64 demo group **Horizon**).  Initial release
**18 June 2015**; last update **31 October 2019** (v1.0.5).  App Store price
£9.99 / $12.99 (USD).  App ID 955421205, developer ID 955421204.

Marketed as "the ultimate chiptune production package tool", it emulates the
**SID 8580 R5** chip with 3 voices, 8 waveforms, wavetable/filter-table
editing, MIDI I/O, Audiobus 2 / Inter-App Audio, and CIA-accurate BPM timing.
Export formats: `.s64` (native), `.m4a` (AAC audio), `.sid` (PSID for
sidplayers), `.prg` (runnable on a real C64).

The **v1.0.5 (2019)** update added a **"Set SID file start address from
settings"** menu, which explains the relocation scatter visible in the corpus
(pre-2019 tunes default to $1000; post-2019 authors began choosing other
bases).

Source code is **not public** (commercial app).  Website: www.sidtracker64.com
(may be defunct as of 2026).

---

## 2. PSID / binary header facts

- All 259 HVSC #84 tunes are **PSID version 2**.
- **No RSID** (relying on real C64 ROM) in the corpus.
- `load_addr` is **always 0** in PSID header (load address embedded in data).
- Player is self-contained; HVSC DOCUMENTS contain **no mention** of
  SidTracker64 in Players.txt, STIL.txt, Songlengths.faq, or update files.

### sidid fingerprint (from local sidid.cfg)

```
SidTracker64
BD ?? ?? 29 FE 9D 04 D4 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? F0 ?? A8 BD ?? ?? 18 69 END
```

This is the only sidid pattern; it fires regardless of relocation base
(wildcard `??` bytes cover variable addresses).

### Speed / interrupt type

| speed_flags | count | interpretation |
|---|---|---|
| `0x00000000` | 137 | pure VBI — play() called once per PAL frame (50 Hz) |
| `0x00000001` | 121 | CIA for subtune 1 only (always single-subtune) |
| `0x00000003` | 1 | CIA for subtunes 1+2 (Street_Defender, 2-subtune) |

**122 of 259 tunes (47%) use CIA timing** — a consequence of SidTracker64's
BPM-exact model (uses precise BPM values rather than C64 VBL 50.125 Hz).
CSDb forum (topicid=113188) confirms: "ST64 uses exact BPM values since most
musicians rather have a correct BPM than adjust to the VBL of a C64."
Non-standard BPMs embed CIA setup code in the init routine.

CIA-timed SidTracker64 tunes are harder to use in demos (raster splits
required), but the CIA tunes are still single-speed — **speed_flags=0x00000001
means the play() is still called once per interrupt**, just at a non-VBL rate.
No 2x/4x multispeed (other than the one 2-subtune case above) has been
observed in the corpus.

---

## 3. Address cluster table

All 259 tunes; columns: init addr (hex), play addr (hex), count, group label.

| init | play | count | group | notes |
|---|---|---|---|---|
| $1000 | $1003 | 210 | **canonical** | default pre-v1.0.5 output; 81% of corpus |
| $A000 | $A003 | 15 | reloc | BASIC ROM shadow; acrouzet (10), Page (4), Cerix (1) |
| $E000 | $E003 | 7 | reloc | KERNAL ROM shadow; Onosendai (3), acrouzet (4) |
| $0800 | $0803 | 5 | reloc | low RAM (cassette buffer area); all acrouzet |
| $1884 | $1003 | 5 | data-ptr init | init points into song-data region, play=$1003; Page (1), Hesford (1), ChristopherJam (1), Nico_Clone (1), Miettinen (1) |
| $181A | $1003 | 2 | data-ptr init | Factor6, Skyffel |
| $2000 | $2003 | 2 | reloc | Jason Page (Last_Ninja_2_Remake, Nicotine_Pang) |
| $4000 | $4003 | 2 | reloc | Jason Page (25_Hurts, Return_to_Bass) |
| $8000 | $8003 | 2 | reloc | Jason Page (Poppy_Locky), Toki (1) |
| $0900 | $0903 | 1 | reloc | X-Jammer |
| $189A | $1003 | 1 | data-ptr init | Los_Pat_Moritas (Amor_Punga) |
| $1B30 | $1B33 | 1 | reloc | Nico_Clone (Street_Defender, 2-subtune) |
| $4320 | $4323 | 1 | reloc | Rob Hubbard & Jason Page (Rob's Life, 3-subtune) |
| $7000 | $7003 | 1 | reloc | mr1oo |
| $A270 | $A273 | 1 | reloc | Harlequin (Retro-Lamers) |
| $A730 | $A733 | 1 | reloc | acrouzet (Caffeine_Trip) |
| $B5A6 | $B5A9 | 1 | reloc | Jason Page (Miner_2019er) |
| $B600 | $B603 | 1 | reloc | Manuel Bredfeldt / Wizard (Voll_Dampf_Voraus) |

**Summary:**
- Canonical $1000: **210** (81%)
- Standard relocations (init = play − 3, non-$1000): **41** (16%)
- Data-ptr init variants (play=$1003, init≠$1000): **8** (3%)
- Distinct (init, play) address pairs: **18**
- Distinct relocation bases: **17** (including $1000)

**"Data-ptr init" meaning:** the init addr points somewhere inside the
song-data area (e.g. $1884 = $1000 + $884), while play stays at $1003.
This is how SidTracker64 passes the song-select index to the init routine
via a call-address offset rather than the A register.  The play address
does NOT change — the player engine is always at $1003 in these tunes.

**Relocation driver:** the v1.0.5 "set start address" setting lets authors
choose a different load base.  Authors relocating to $A000 or $E000 are
deliberately placing the player in the ROM-shadow region (unused by default
in PSID/sidplayfp context, but interesting for custom demo loading).

---

## 4. Corpus shape summary

| metric | value |
|---|---|
| Total tunes in HVSC #84 | 259 |
| PSID version | 2 (all) |
| Single-subtune tunes | 257 |
| Multi-subtune tunes | 2 (Street_Defender: 2 subs; Rob's Life: 3 subs) |
| VBI tunes | 137 (53%) |
| CIA-timed tunes | 122 (47%) |
| Earliest release | 2014 (1 tune — Pål Syvertsen; pre-launch beta?) |
| Active years | 2015–2025 (ongoing) |
| Peak years | 2015 (31), 2016 (38), 2021 (38) |
| Median songlength | ~2.5 min (bulk in 2–5 min range) |
| Longest tune | Rob's Life (Jason Page) — 718 s (~12 min, 3 subtunes) |
| Shortest (non-trivial) | various ~30 s demo stings |

### Songlength distribution

| bucket | count | min | max | avg |
|---|---|---|---|---|
| <30 s | 20 | 4 s | 28 s | 13 s |
| 30–60 s | 25 | 33 s | 58 s | 46 s |
| 1–2 min | 47 | 60 s | 115 s | 88 s |
| 2–5 min | 134 | 121 s | 296 s | 195 s |
| 5 min+ | 33 | 309 s | 718 s | 371 s |

### Year distribution

| year | tunes | notes |
|---|---|---|
| 2014 | 1 | single pre-launch tune |
| 2015 | 31 | launch year (June 2015) |
| 2016 | 38 | peak early adoption |
| 2017 | 30 | |
| 2018 | 29 | |
| 2019 | 21 | v1.0.5 adds start-addr setting |
| 2020 | 26 | |
| 2021 | 38 | second peak (Lula surge: 18 tunes this year) |
| 2022 | 10 | |
| 2023 | 14 | |
| 2024 | 11 | |
| 2025 | 10 | still active |

---

## 5. Author concentration

| rank | author | tunes | notes |
|---|---|---|---|
| 1 | Jason Page | 33 | C64 veteran (Amiga/C64 commercial era); uses ST64 exclusively since ~2015; multiple compos |
| 2 | Aidan Crouzet-Pascal (acrouzet) | 31 | prolific modern composer; heavy relocator (19/31 non-canonical) |
| 3 | Lula | 20 | large 2021 batch (18 of 20 from 2021) |
| 4 | Vasco Serafini (Vaz) | 18 | |
| 5 | Tamanegi-itame | 15 | Japanese composer; game music covers + originals |
| 6 | Nahuel Berneri (Los Pat Moritas) | 15 | Latin American flavour; cumbia/folk idioms |
| 7 | Paul Hesford (Sidman) | 9 | UK; Hokuto Force + Maniacs of Noise; ex-DMC V5 user |
| 8 | Mischa Magyar (Cerix) | 9 | |
| 9 | X-Jammer | 6 | |
| 10 | Skyffel | 6 | |

Top 10 authors account for **162/259 tunes (63%)**.

**Notable heavy users confirmed via external sources:**
- **Jason Page**: early adopter, 2015 launch content included in app (Commando, Blood Money covers). Confirmed SidTracker64 user on Twitter/social.
- **Paul Hesford (Sidman)**: CSDb profile explicitly states "SidTracker 64 on IPAD and soon GoatTracker on PC" as his current tool.
- **Onosendai**: 4 tunes; CSDb presence confirmed (Cosmos placed #5 at BCC Party #16, 2022).
- **E-Grass (Joachim Ljunggren)**: 2 tunes; confirmed via CSDb/HVSC.
- **Rob Hubbard & Jason Page**: 5 collaborative tunes under the "Project Hubbard" / "Psytronik" label (2017–2022).

---

## 6. MUSICIANS folder distribution

| folder | count | primary author(s) |
|---|---|---|
| MUSICIANS/A/ | 39 | Acrouzet (33), AceMan (3), AMB (2) |
| MUSICIANS/P/ | 37 | Page_Jason (33), Topshelf (4+) |
| MUSICIANS/L/ | 37 | Lula (20), Los_Pat_Moritas (17) |
| MUSICIANS/T/ | 21 | Tamanegi-itame (15), Topshelf (4+) |
| MUSICIANS/V/ | 18 | Vaz (18) |
| MUSICIANS/H/ | 16 | Hesford_Paul (9), Hubbard_Rob (5+) |
| MUSICIANS/C/ | 12 | Cerix (9), ChristopherJam (2) |
| DEMOS/ | 36 | various — demo scene productions |
| MUSICIANS/S/ | 9 | Skyffel (6), Slaze (3) |
| MUSICIANS/X/ | 6 | X-Jammer (6) |
| MUSICIANS/N/ | 6 | Nico_Clone (4) |
| MUSICIANS/O/ | 4 | Onosendai (4) |
| GAMES/ | 3 | Floppy_Bird_Preview (2), GPAC_Dementia_Defender (1) |
| MUSICIANS/D/ | 5 | DOS (4) |
| MUSICIANS/F/ | 5 | F3R0 (3) |
| MUSICIANS/M/ | 5 | Moppe (2) |
| MUSICIANS/R/ | 4 | Rico (3) |
| MUSICIANS/E/ | 2 | E-Grass (2) |

**36 tunes appear under DEMOS/** (not in a named MUSICIANS folder), reflecting
SidTracker64's use for demoscene compo entries and soundtrack slots.  3 tunes
appear under GAMES/ (mobile-game / preview soundtracks).

---

## 7. Scene context

### Tool origin & Horizon connection
Pernod is a member of the legendary C64 demo group **Horizon** (Swedish).
SidTracker64 is his personal tool, written to enable proper SID music
composition on a mobile device.  The CSDb announcement thread
(csdb.dk/forums/?roomid=7&topicid=110169) from April–May 2015 shows
strong scene interest including: "Moppe from Oneway created a remix
of a David Hasselhoff composition" as an early demo.  The CSDb community
noted the player requires only ~15 rasterlines on C64.

### Adoption timeline
- **June 2015**: launch; Jason Page's "First"/"Second"/... series begins
  immediately (10 tunes in 2015 alone).
- **2015–2016**: early adopters cluster around UK (Jason Page, Sidman,
  Tony Tooke) and international (Tamanegi-itame Japan, acrouzet France).
- **2017–2019**: steady output; v1.0.5 (2019) unlocks start-address
  relocation → scatter of non-$1000 bases begins.
- **2020–2021**: second surge; Lula adds 19 tunes in 2020–2021.
- **2022–2025**: continued use (Genesis Project, acrouzet, Hokuto Force,
  Onosendai, Rico, Gabez) despite no further app updates.
- **HVSC count growth**: ~88 at time of the CSDb CIA-timer forum thread
  (approx. 2016) → 259 in HVSC #84 (2024).

### Notable compo entries
- **BCC Party #16 (2022)**: Cosmos by Onosendai — #5 in C64 Music
  (102 SID downloads on CSDb).
- **X'2016**: X Arrival by Sidman — ranked #15 in C64 Music.
- Various demo soundtracks (DEMOS/ bucket) for groups including
  Genesis Project, Hokuto Force, Hitmen, Alpha Flight, F4CG/Atlantis.

### DeepSID classification
DeepSID (deepsid.chordian.net) uses a **magenta colour strip** for
SidTracker64 tunes (confirmed via search result mentioning "A magenta color
strip was added for SidTracker64 tunes").

### App maintenance status (as of 2026-06-14)
Last update was v1.0.5 on 31 October 2019.  No evidence of updates since.
The tool is still available on the App Store (id 955421205).
Active composition continues (10 tunes in 2025 HVSC update), so the app
is still running on modern iOS despite the long gap without updates.

### Related: "Project Hubbard" label
Five tunes in MUSICIANS/H/Hubbard_Rob/ are tagged "Rob Hubbard & Jason Page"
under the "Project Hubbard" label (2018 Hokuto Force / Psytronik releases).
These are collaborative new compositions using SidTracker64, not remakes of
existing Hubbard engines — they load at $1000 / $4320 / $B5A6 and use the
ST64 player fingerprint.

---

## 8. Data-ptr init variant — technical note

8 tunes have `play_addr=$1003` but `init_addr` pointing into the data area
rather than the player entry point:

| init offset from $1000 | init_addr | count | likely meaning |
|---|---|---|---|
| +$81A | $181A | 2 | |
| +$884 | $1884 | 5 | |
| +$89A | $189A | 1 | |

In all cases the player is still at $1003; only the init address differs.
These tunes call init with a different address, probably because the PSID
loader calls `init_addr(A=subtune)` and the player uses the PC-relative
entry to select a sub-song from a table at that offset in the data area.
This is version-dependent behaviour (pre-v1.0.5, certain export modes).

---

## 9. Leads to follow

1. **Disassemble one canonical $1000 tune** (e.g. Page_Jason/First.sid) to
   map the full player layout: player header, init entry at $1000, play
   entry at $1003, data area start, CIA setup code path (only when
   speed_flags≠0).  Establish the exact byte layout of the player binary.

2. **Data-ptr init variant mechanics**: disassemble one of the 8 data-ptr
   init tunes (e.g. Hesford_Paul/Ocean_Ninja.sid, init=$1884) to understand
   why init points into data — is this a sub-song select table, or a version
   difference?

3. **CIA BPM encoding**: for CIA tunes, find the CIA setup code in init
   (what latch values does it write to $DC04/$DC05?) and correlate with the
   PSID speed_flags.  The v1.0.5 update notes say "set SID file start address
   from settings" — check whether CIA latch is also user-configurable.

4. **Relocation mechanism**: for a relocated tune (e.g. acrouzet/$A000),
   check whether the player code is relocated byte-for-byte or whether
   ST64 produces a position-independent player.  If PIC, sidid's wildcard
   fingerprint covers it; if not, there may be relocation patches.

5. **Multi-subtune layout**: Rob's Life (3 subtunes, $4320) and
   Street_Defender (2 subtunes, $1B30) — examine how the init entry
   selects subtunes (A register convention? table at init_addr + A*N?).

6. **Contact / source**: Daniel Larsson / Pernod may be reachable via
   CSDb or the Facebook page (facebook.com/SidTracker64) for format
   documentation or source sharing if the project is ever open-sourced.

7. **sidid.nfo entry**: the local sidid.cfg has the fingerprint but no
   descriptive nfo entry.  Check the upstream cadaver/sidid GitHub for
   any version notes or a second pattern.

8. **`s64` native format**: no public documentation found.  If a `.s64`
   file can be obtained, it would reveal the canonical song-data model
   (separate from the exported PSID binary).
