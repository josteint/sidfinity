# CheeseCutter 2.x — Release History, Scene Context & HVSC Corpus Shape

<!-- provenance header -->
<!--
  Primary sources:
    - GitHub repo: https://github.com/theyamo/CheeseCutter  (tags, source)
    - Triad site: https://www.triad.se/members/abaddon  (biography)
    - Triad release pages: triad.se/releases/cheesecutter-*
    - CSDb: csdb.dk (releases: 106959, 118865, 132739, 136752, 148677, 157512)
    - Demozoo: https://demozoo.org/productions/358057/
    - BattleOfTheBits Lyceum: https://battleofthebits.com/lyceum/View/CheeseCutter
    - VintageIsTheNewOld: vintageisthenewold.com/cheesecutter-*
    - NightfallCrew: nightfallcrew.com  (v0.4.0 article)
    - Lemon64 forum: lemon64.com/forum (SFX thread)
    - Debian package: packages.debian.org/sid/cheesecutter
    - Local clone: /home/jtr/sidfinity/tmp/dmc_hunt/CheeseCutter  (Version=2.10)
    - Local DB: /home/jtr/sidfinity/hvsc84.db  (read-only, 302 CheeseCutter_2.x SIDs)
  fetched_via: WebFetch / WebSearch + local file reads
  fetch_date: 2026-06-14
  author: Claude (sidfinity research agent)
  reliability: HIGH for corpus stats (live DB); MEDIUM for release notes
    (most CSDb pages returned 503 at fetch time; content reconstructed from
    web search snippets, Triad release pages, and source-code inspection).
    The version-to-player-string mapping is sourced directly from the tagged
    ACME source in the repo and is HIGH-reliability.
-->

---

## 1. Background & Developer

**CheeseCutter** is an open-source cross-platform SID music tracker written in
the D programming language by **Timo Taipalus "Abaddon"** (Finnish demoscener).
Development started ~2009; active release period 2011–2017; maintenance commits
continue to 2026 (SDL2 port merged 2026-03-29, tagged v2.10).

Abaddon's scene history:
- Late 1990s: Damage
- 2003–2011: Fairlight (CheeseCutter 0-series developed here)
- 2012–Jan 2017: Triad (CheeseCutter 2.x developed and released under Triad banner)
- After 2017: project formally complete, maintenance mode

**Mac OSX / D2 port**: Ruk of Booze Design, 2013.

**License**: GNU GPL.

**Official site**: http://theyamo.kapsi.fi/ccutter  (serves 401 as of 2026-06-14; old
about page also 401; Wayback blocked; Debian/FreshPorts still reference it).

---

## 2. The 0-Series vs 2-Series Divide

The "0-series" (0.4.0, 0.5.0, released 2011) aimed for **JCH Editor compatibility**
on C64. Most JCH Editor files loaded in it. The player was NP21.G4 by Laxity / VIB.

The **2-series** (2.x) is a complete rewrite:
- JCH compatibility dropped entirely.
- 3-byte command table (was 2-byte in 0-series): byte 1 = command number,
  bytes 2–3 = parameter.
- New effects not in JCH: portamento, lo-fi vibrato, breakspeed/swing,
  vibrafeel, INCLUDE_SYNC, direct pulse.
- The .ct file format is a compressed binary (`CC2` magic + zlib) with an
  internal `SONG_REVISION` counter (currently 12 in v2.10; oldest supported
  at load time is 6; ≥128 signals a stereo/2SID file, rejected by the
  main editor).
- The player source is embedded in the D binary as a compile-time string
  import of `src/c64/player_v4.acme` and assembled at export time via
  embedded Acme 0.91.

---

## 3. Release Timeline

All tagged releases are on GitHub at https://github.com/theyamo/CheeseCutter/tags

| Version | CSDb date | GitHub tag | Player string | Key changes |
|---------|-----------|------------|---------------|-------------|
| 0.4.0 | ~Mar 2011 | — | — | reSID-fp integration, real-time SID register display, autoconf build, JCH compat |
| 0.5.0 | May 9 2011 | — | — | Playback tracking toggle, filter-preset keyboard shortcuts, "spartan" mode, instrument swap |
| 2.2.6a | ~Mar 2012 | — | — | First 2-series public snapshot (exact date uncertain; CSDb not indexed) |
| 2.3.0 | Mar 20 2012 | — | — | CSDb id 106959; Abaddon-only credit (not yet Triad) |
| 2.4.0 | Sep 24 2012 | — | — | CSDb id 117096; Abaddon joins Triad; Mac/D2 port work begins |
| 2.5.0 | May 13 2013 | — | — | CSDb id 118865; "improvements for the help function, aspect ratio correction, multispeed driver, wave program and the packer"; companion CSDb "Release The Cheese" composition competition |
| 2.6.1 | Jun 13 2014 | — | — | CSDb id 132739; Ruk (Booze Design) credited for help docs; Windows/Mac/Linux/src all provided |
| 2.7.1 | Jan 11 2015 | `v2.7.1` | `cc4.03` | Player string cc4.03; INCLUDE_SYNC added |
| 2.8.0 | Nov 28 2015 | `v2.8-release` | `cc4.04` | CSDb id 148677; player bumped to cc4.04; also `v2.8s-release` (stereo beta?) same date |
| 2.8rc1 | Nov 21 2015 | `v2.8rc1` / `v2.8rc1s` | — | Release candidate; "s" suffix = stereo variant |
| 2.9.0 | Apr 13 2017 | `v2.9-beta-3` | `cc4.07` | CSDb id 157512; player bumped to cc4.07; INCLUDE_SYNC; last Abaddon Triad release |
| 2.9-stereo | Apr 10 2017 | `v2.9-beta-3-stereo` | `cc4.07` | PSID v3 header; PSID_SECOND_SID_ADDR=$D420; SID model bits 6-7 for chip 2; SONG_REVISION≥128 marks stereo .ct; NOT merged to master |
| 2.10 | Mar 29 2026 | `v2.10` | `cc4.07` | SDL2 port merged (SDL2 bindings work started Nov 2021); window resize support; CLI cleanup; Debian 2.10-3 |

**Notes on the stereo branch**:
- Tagged as `v2.9-beta-3-stereo` (2017-04-10), never merged to master.
- Generates PSID v3 (`0x00 0x03` in header bytes 4–5).
- Hardcodes second SID address at $D420 (`PSID_SECOND_SID_ADDR = 0x42`).
- Second SID model flags packed into bits 6–7 of PSID byte $77.
- The main editor detects stereo .ct files by `SONG_REVISION >= 128` and
  refuses to load them ("The song appears to be a stereo SID file and
  doesn't work with this editor").
- GitHub issue #7 (open) documents a known bug: ct2util sets `start_song`
  field = 0 in 2SID exports (should be ≥1 per spec); also missing SID
  model flag copy for second chip when both chips are the same model.

---

## 4. Player Architecture (from source)

File: `src/c64/player_v4.acme` (1763 lines; embedded via D `import()`)

**Lineage**: explicitly `;;; Based on JCH NP 21.G4 by Laxity/VIB`

**Internal version tag** at `$fee` in assembled binary: `!pet "cc4.07"` (v2.8 = cc4.04; v2.7.1 = cc4.03). This is the `playerID` field the D code reads back to warn about player version mismatches.

**PSID export**:
- Default load address: `BASEADDRESS = $1000`; init = BASEADDRESS, play = BASEADDRESS + 3.
- PSID header written by `build.d`; default template has title "Swamp Poo",
  author "Thomas Mogensen (DRAX)" (placeholder).
- `PSID_DATA_START = 0x7c` → 124-byte header (PSID v2, flags at 0x76/0x77).
- PAL flag: `0x04`; SID model: `0x10` (6581) or `0x20` (8580).
- **Multispeed**: when `song.multiplier > 1`, speed table = 0xFF (CIA-timed),
  CIA_VALUE = `$4cc7 / multiplier` (PAL_CLOCK / multiplier). PSID sets USE_MDRIVER.
  The `mplay` entry point at BASEADDRESS+6 is the CIA-driven sub-frame call.

**Feature flags** (all `TRUE` by default in editor mode; `build.d` strips unused ones
at export time by scanning the sequence data):
- `INCLUDE_CMD_SLUP/SLDOWN` — slide up/down (signed 16-bit speed)
- `INCLUDE_CMD_VIBR` — hi-fi vibrato (feel nibble, speed nibble, depth divider)
- `INCLUDE_CMD_PORTA` — portamento on tie notes
- `INCLUDE_CMD_SET_ADSR` — per-note ADSR override
- `INCLUDE_CMD_SET_OFFSET` — note detune (signed 16-bit)
- `INCLUDE_CMD_SET_LOVIB` — lo-fi vibrato (speed / depth)
- `INCLUDE_CMD_SET_WAVE = FALSE` — always disabled (unimplemented)
- `INCLUDE_SEQ_SET_PULSE/CHORD/ATT/DEC/SUS/REL/SPEED/VOL` — sequence inline commands
- `INCLUDE_DIRECT_PULSE` — direct pulse value write
- `INCLUDE_VIBRAFEEL` — vibrato "feel" modulation variant
- `INCLUDE_BREAKSPEED` — swing/breakbeat speed alternation (reads from chord table)
- `INCLUDE_CHORD` — chord arpeggio
- `INCLUDE_FILTER` — filter table programming
- `INCLUDE_SYNC` — voice synchronisation mechanism (added v2.7.1+)
- `MULTISPEED` — CIA-driven multiframe support

**Instrument table layout** (48 instruments × 8 bytes per instrument field):
- INS_AD: Attack/Decay
- INS_SR: Sustain/Release
- INS_HR: restart type ($00=3-frame, $40=soft, $80=hard) + arp delay (bits 0–3)
- INS_4: Hard restart waveform
- INS_FLTP: filter table pointer
- INS_PULSP: pulse table pointer ($00–$3F)
- INS_7: hard restart SR envelope
- INS_ARP: wave table pointer

**Table formats** (from in-editor help strings in `player_v4.acme`):
- *Pulse table*: [duration/direction byte] [add value] [initial pulse (nibbles reversed: $48=$8400)] [next pointer or $7F=stop]
- *Filter table*: [duration or $90–$F0 filter type select] [add value or resonance+mask] [initial value or $FF=skip] [next pointer or $7F=stop]
- *Wave table*: [transpose] [waveform / wave delay / loop pointer]
  - Transpose $00–$5F = relative up; $80–$DF = absolute (unaffected by note); $7E = loop previous; $7F = loop to next-byte row
  - Waveform: $00 = do nothing; $01–$0F = override wave delay; $10–$DF = SID ctrl byte; $E0–$EF = ctrl $00–$0F; $00–$FF = loop target if Byte 1 = $7F

**No SFX support**: CheeseCutter exports a self-contained PSID with no runtime
SFX channel-reservation mechanism. Community workaround is "SFX Anywhere" by
4Mat (discussed in Lemon64 forum).

---

## 5. .ct File Format (binary layout)

- Magic: `CC2` (3 bytes), then zlib-compressed blob (167832 bytes uncompressed).
- At uncompressed offset 0: 65536 bytes of C64 memory image (SID data/patterns).
- At offset 65536: metadata record:
  - `ver` (SONG_REVISION, currently 12; ver < 6 = too old; ver ≥ 128 = stereo)
  - `clock`, `multiplier`, `sidModel`, `fppres`
  - `songspeeds[32]` (one per subtune, if ver ≥ 6)
  - `highlight`, `highlightOffset` (if ver > 10)
- Title/author/release at `DatafileOffset.Title`
- 48×32 instrument name labels
- Subtune data (tracks × 32 subtunes)

---

## 6. Scene Reception & Tooling

**Adoption breadth**: 302 SIDs in HVSC #84 spanning 2011–2025; peak years 2015 (60 tunes), 2017 (41), 2013 and 2016 both prominent. Active community through at least 2024–2025 with new HVSC entries.

**Key users** (from HVSC corpus, top 5):
1. Markus Klein / LMan (55 tunes, ~18%) — heaviest user; also developed the $D418=$0F/$0F LMan-variant export (24 tunes with init=$080D / play=0 characteristic; these are likely a custom player or SCC-extended variant)
2. Carsten Berggreen / Scarzix (51 tunes, ~17%) — co-developer of the stereo branch; most of his $E000-based tunes (15 SIDs, init=$E000) are from 2013–2016
3. Richard Bayliss (25 tunes, ~8%)
4. Esteban Palladino / Uctumi (19 tunes)
5. Timo Taipalus / Abaddon himself (17 tunes)

**CSDb community reception**: consistently warm. Comments on 2.6.1: "Best JCH editor/player ever made." Competition "Release The Cheese" (2013 CSDb) accompanied 2.5.0.

**Comparison to peers**: cited as "feature parity with GoatTracker 2 and SID Duzz' It". Key difference from GoatTracker: CheeseCutter uses *independent per-voice sequence stacking* (each voice has its own track position); GoatTracker uses a single shared multi-channel pattern block. CheeseCutter sequences are up to 64 rows ($40); max 128 sequences ($80).

**SID Factory II** (Chordian/Jens-Christian Huus) includes a CC .ct file importer, confirming scene awareness of CheeseCutter's .ct format. SID Factory II's own player is also JCH NP21.G4-derived, making the two tools musically compatible at the intermediate representation level.

**DeepSID**: the GitHub search finds `Chordian/deepsid` references in connection with CheeseCutter but no dedicated CheeseCutter plugin. DeepSID plays exported .sid files natively via the standard PSID path; no special CheeseCutter detection needed.

**BattleOfTheBits** has a CheeseCutter Lyceum entry, indicating cross-platform chiptune community awareness.

**Debian/FreeBSD packaging**: `cheesecutter` in Debian `sid` branch (2.10-3); FreshPorts FreeBSD `audio/cheesecutter`; Arch Linux AUR. Binary packages available via repology. The Debian maintainer is Alex Myczko.

**Video tutorials**: Scarzix created a video tutorial series for CheeseCutter (referenced in ChipMusic.org thread id 15141).

**Facebook group**: CheeseCutter has a Facebook community where users share compositions and ask for help.

---

## 7. HVSC Corpus Shape (hvsc84.db, read-only query, 2026-06-14)

Total SIDs: **302**, all engine=`CheeseCutter_2.x`.

### 7.1 Load/Init/Play Address Distribution

All 302 SIDs have `load_addr = $0000` (PSID standard: load address in data header).

**Init address distribution** (dominant = default $1000 export):

| init_addr | count | notes |
|-----------|-------|-------|
| $1000 | 208 | Default ct2util export (`-r` not set) |
| $080D | 25 | All LMan; play_addr=0 → these are RSID/CIA-only or non-standard player (see §7.3) |
| $E000 | 15 | Scarzix-heavy; $E003 play; ROM bank region |
| $0C00 | 7 | — |
| $A000 | 6 | — |
| $8000 | 4 | — |
| $0FED | 4 | Abaddon + Vent early tunes (2013); play=$0FE2; slightly before $1000 |
| $9000 | 3 | — |
| Many other single/small groups | ~30 | Various `-r` reloc values |

The init+3 = play pattern holds for **all** non-$080D entries — confirming the
`init_addr + 3 = play_addr` invariant from `build.d` for all standard exports.

**The $0FED group** (4 SIDs: Abaddon + Vent, 2013): init=$0FED, play=$0FE2 — this is
13 bytes *below* $1000, implying a slightly different player that starts 13 bytes
earlier. These are early tunes when the player layout was possibly slightly different.

### 7.2 PSID Version & 2SID

- **PSID v2**: 293 SIDs (standard single-SID export)
- **PSID v3**: 9 SIDs (2SID — dual SID chip)

The 9 PSID v3 (2SID) SIDs:

| Path | Author | init |
|------|--------|------|
| Et1999cc/Overdrive-Title_Theme_2SID.sid | Esteban Trujillo | $1000 |
| LMan/Blade_Runner_Main_Titles_2SID.sid | Markus Klein | $1000 |
| LMan/Tuneful_Eight_tune_1_2SID.sid | Markus Klein | $8100 |
| LMan/Tuneful_Eight_tune_2_2SID.sid | Markus Klein | $7180 |
| LMan/Tuneful_Eight_tune_3_2SID.sid | Markus Klein | $A7E0 |
| LMan/Tuneful_Eight_tune_4_2SID.sid | Markus Klein | $A7E0 |
| Scarzix/Auxillary_Love_2SID.sid | Scarzix | $1000 |
| Scarzix/Singularity_2SID.sid | Scarzix | $1000 |
| Steel/Game_of_Thrones_2SID.sid | Mario Laugell | $1000 |

All 2SID entries are flagged by their filename suffix `_2SID`. The Tuneful Eight
has non-standard relocation addresses (different per-subtune-file). As noted in
§3, the 2SID export is in a separate `v2.9-beta-3-stereo` branch, never merged to
master, meaning these 9 SIDs were exported with that branch.

### 7.3 The LMan $080D / play=0 Group (25 SIDs)

25 SIDs by LMan with init=$080D, play=0. In PSID/RSID format, play_addr=0 means
the player uses its own interrupt mechanism (RSID or CIA-driven without PSID
play pointer). These tunes appear to use a modified/custom player layout or an
extended SCC/SID player rather than standard CheeseCutter export. Titles include
"La Mer (SCC Extended)", "Vortex", "Concert Thrust Main", "Deep Kiss". The
"SCC Extended" title suggests MSX Sound Custom Chip emulation or a different
player engine entirely, possibly not standard CheeseCutter PSID format at all.
The sidid engine tag `CheeseCutter_2.x` may be a false positive or these may be
CheeseCutter-composed tunes packed into a different player wrapper by LMan.

**This group should be audited before starting CheeseCutter pipeline work**:
if they use a non-CC player, they are out-of-scope for the CC USF pipeline.

### 7.4 Subtune Distribution

| subtunes | count |
|----------|-------|
| 1 | 280 (92.7%) |
| 2 | 10 |
| 3 | 6 |
| 4 | 2 |
| 6 | 1 |
| 7 | 1 |
| 11 | 1 |
| 15 | 1 |

The largest (15 subtune) SID is likely a compilation. Multi-subtune SIDs are rare —
CC supports up to 32 subtunes (`SUBTUNE_MAX = 32`) but composers rarely use more than 3–4.

### 7.5 Songlength Distribution

| bucket | count |
|--------|-------|
| < 30 s | 16 |
| 30–60 s | 29 |
| 1–2 min | 70 |
| 2–5 min | 160 |
| > 5 min | 27 |

- min: 7.7 s; max: 1016.0 s (~17 min); mean: 170.8 s (~2.85 min)
- Total corpus duration: **~860 minutes** (14.3 hours)
- Distribution is strongly 2–5 min, consistent with demo/musicdisk loop lengths.

### 7.6 Release Year Distribution

| year | tunes |
|------|-------|
| 2011 | 1 |
| 2012 | 5 |
| 2013 | 32 |
| 2014 | 31 |
| 2015 | 60 |
| 2016 | 29 |
| 2017 | 41 |
| 2018 | 26 |
| 2019 | 17 |
| 2020 | 23 |
| 2021 | 13 |
| 2022 | 12 |
| 2023 | 8 |
| 2024 | 2 |
| 2025 | 2 |

Peak usage 2015–2017 (during Abaddon's Triad membership and active development).
Post-2017 steady-state ~15–25 tunes/year; still alive as of 2024–2025.

### 7.7 Author Concentration

Top 10 authors account for ~72% of the corpus (218/302). LMan + Scarzix alone =
35% (106/302). This high concentration means the pipeline has clear "canonical"
test cases from the dominant composers.

---

## 8. Known Quirks & Open Issues

1. **2SID header bug** (GitHub issue #7, open): `ct2util` stereo export sets
   `start_song = 0` (should be ≥ 1); second SID model flags not propagated.

2. **$0FED init** (4 early 2013 tunes): non-standard player base. These may use
   a pre-2.7.1 player version or a one-off custom relocation.

3. **LMan play=0 group** (25 SIDs): likely not standard CC PSID format. Needs audit.

4. **Player version mismatch warning**: the D code warns at export time if the
   song was composed with an older player than the currently linked one
   (`cc4.03` vs `cc4.07` etc.) — tunes composed with an older CC may emit
   slightly different write behaviour than tunes composed with a newer one.
   HVSC does not record which CC version was used to compose a given SID.

5. **Dead website**: `theyamo.kapsi.fi/ccutter` returns 401; changelog/about
   pages not accessible. Wayback Machine blocked by fetch policy for this agent.

6. **No SFX mechanism**: exported SIDs have no channel-reservation or SFX
   interrupt hook. This is a known limitation compared to GoatTracker 2.

7. **INCLUDE_CMD_SET_WAVE = FALSE**: the "Set wave" command ($06 in the command
   table, described in the in-player help strings) is permanently disabled
   and not assembled even in editor mode. Sequences referencing cmd $06 are
   silently dropped on export.

---

## Leads to Follow

1. **Audit LMan play=0 group** — verify whether init=$080D / play=0 SIDs are
   genuine CheeseCutter PSID exports or a different player wrapper. Load one
   in siddump + check the machine code at $080D to see if it matches the CC
   player_v4 pattern.

2. **Recover website changelog** — `theyamo.kapsi.fi/ccutter/about.html` is the
   canonical changelog page; it was accessible in prior months (cached HTML
   exists). Use a Wayback Machine CLI tool or request a Wayback-unblocked fetch
   for `https://web.archive.org/web/20240101000000*/theyamo.kapsi.fi/ccutter/about.html`
   to recover the 2.3–2.9 feature history.

3. **CSDb comments for 2.8 and 2.9** — pages returned 503 on 2026-06-14.
   Retry fetches for csdb.dk/release/?id=148677 (v2.8.0) and
   csdb.dk/release/?id=157512 (v2.9.0) for community comments and detailed
   feature lists.

4. **v2.8s vs v2.8 difference** — both tagged on 2015-11-28. The `s` suffix likely
   = stereo beta. Diff `v2.8rc1s` vs `v2.8rc1` in the repo to confirm whether
   stereo work began during the 2.8 cycle or started fresh for 2.9.

5. **playerID to .sid mapping** — siddump/sidid could read the `cc4.0x` string
   from actual SID binaries in HVSC to establish which CC player version each
   tune uses. This would let the pipeline detect player-version-specific quirks
   (e.g., INCLUDE_SYNC absent in cc4.03 era tunes).

6. **$0FED group RE** — disassemble one $0FED SID (e.g.,
   `MUSICIANS/A/Abaddon/Zoo_to_Yoo.sid`) to see if it's a standard player_v4
   with a 13-byte prefix or something structurally different.

7. **Multispeed distribution** — none of the 302 SIDs were confirmed multispeed
   from the DB query alone (the `speed` PSID header field isn't in the DB schema).
   Check with: `siddump --writelog MUSICIANS/L/LMan/some_tune.sid` and look for
   `mplay` entries, or query via `python3` + `psid_version` + direct binary reads.
