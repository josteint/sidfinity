# Maniacs of Noise / Deenen — Archive.org & Author Site Research
# Provenance: fetched 2026-06-15 by research agent
# Purpose: Background for MoN/Deenen SID engine migration

---

## Sources checked

| URL | Status | Note |
|-----|--------|------|
| https://charlesdeenen.com | ECONNREFUSED | Domain not live |
| https://www.jeroentel.com | ECONNREFUSED | Domain not live |
| https://csdb.dk/search/?stype=all&search=maniacs+of+noise | OK | Returned group releases + tool list |
| https://csdb.dk/search/?stype=all&search=charles+deenen | OK | 55 SID compositions, tool releases |
| https://codebase64.org/doku.php?id=base:maniacs_of_noise | Empty | Page appears to not exist / no content |
| https://web.archive.org/web/20050101000000*/charlesdeenen.com | BLOCKED | web.archive.org blocked by Claude Code |
| https://web.archive.org/web/20100101000000*/jeroentel.com | BLOCKED | web.archive.org blocked by Claude Code |
| https://archive.org/details/Cybernoid_Music_1988_Maniacs_Of_Noise | OK | C64 one-file demo; "cybernoid 1 /mon" PRG |
| https://archive.org/search?query=maniacs+of+noise+C64+player | Not fetched | Skipped; no additional unique data expected |
| https://vgmpf.com/Wiki/index.php/Maniacs_of_Noise | OK | Key technical details about driver |
| https://vgmpf.com/Wiki/index.php/Charles_Deenen | OK | Gameography; no driver tech details |
| https://en.wikipedia.org/wiki/Charles_Deenen | OK | Biographical only |
| https://csdb.dk/scener/?id=1040 | OK | Charles Deenen CSDb profile |
| https://csdb.dk/scener/?id=8050 | OK (Jeroen Tel) | No driver tech details in profile |
| https://csdb.dk/group/?id=448 | OK | MoN group page; tool releases listed |
| https://www.c64.com/gt_display_interview.php?interview=8 | SSL error | Could not verify certificate |
| https://www.c64-wiki.com/wiki/Maniacs_of_Noise | OK | Confirms Deenen wrote driver when he saw Tel arrange a song |
| https://designingsound.org/2010/02/05/charles-deenen-special-exclusive-interview/ | OK | "We wanted to make our own music" only — no tech details |
| https://hugi.scene.org/online/hugi38/hugi38-demoscene-interviews… | OK | Tel hacked Hubbard's routine before getting own driver |
| https://www.gamejournal.it/driving-the-sid-chip-… | OK | Hubbard/Galway only; no MoN content |
| https://github.com/cadaver/sidid/blob/master/sidid.cfg | Partial (truncated) | MoN section in unpaged portion |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg | OK (raw) | Full signatures extracted |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo | OK (raw) | MoN/Deenen entry: minimal (author name only) |
| https://github.com/WilfredC64/player-id | OK | Player-id tool; no MoN-specific data visible |
| https://www.sidmusic.org/sid/jtel.html | ECONNREFUSED | Domain not live |

---

## Author background

### Charles Deenen
- Born Dutch; started composing on Commodore PET at age 13 (self-written sound driver).
- Around 1985 wrote a C64 sound driver (the earliest version of what became Musicfile).
- Co-founded **Maniacs of Noise** in 1987 with Jeroen Tel and others (Netherlands).
- Wrote the MoN music driver ("Musicfile") and a separate sound effects driver, both in **Turbo Ass** (Turbo Assembler).
- Composition method: typed hexadecimal numbers and labels directly into the driver's source code — no GUI tracker.
- Later moved to Amiga, then professional game audio (EA Games).
- Wikipedia page: https://en.wikipedia.org/wiki/Charles_Deenen
- CSDb ID 1040: https://csdb.dk/scener/?id=1040
- Aliases: "The Silver Surfer", "The Mercenary Cracker" (1985–1988)

### Jeroen Tel
- Co-founder of Maniacs of Noise.
- Initially **hacked into Hubbard's routine** to compose music in machine code (had no driver of his own).
- Used Deenen's Musicfile driver after it was available; later wrote his own driver (JT format, used on Amiga).
- The MoN HVSC folder (MUSICIANS/T/Tel_Jeroen/) is the largest single user of the MoN/Deenen engine in HVSC: ~60+ SIDs.
- CSDb ID 8050: https://csdb.dk/scener/?id=8050
- Retro Hour podcast interview (EP496): "The SID Chip Was My First Love" — https://audioboom.com/posts/8772654
- Podcast EP114 (YouTube): https://www.youtube.com/watch?v=d-L2WjIvBRQ

### Reyn Ouwehand
- Joined MoN at age 16; recruited by Deenen after being noticed in the demoscene.
- Used the Musicfile driver for his C64 game compositions (Flimbo's Quest, Last Ninja 3, Stormlord 2, etc.).
- His HVSC folder (MUSICIANS/O/Ouwehand_Reyn/) contains ~15+ MoN/Deenen SIDs.
- One SID is named "First_MON_tune.sid" — useful candidate for studying minimal/early driver usage.

---

## Driver technical details

### General architecture
- Driver name: **Musicfile** (internal; not a public format name).
- Written in Turbo Ass (Turbo Assembler).
- Two identified versions:
  - **MoN Old** (approx 1989–1990)
  - **MoN New** (approx 1990–1992)
  (Source: original research.md stub in this repo; not confirmed by additional sources found in this sweep.)
- Ported to **ZX Spectrum 128K** by Deenen.
- Supports **4-bit samples** — Deenen sent "a disk with Turbo Ass, his music driver, and some 4-bit samples" (VGMPF Maniacs_of_Noise page). This maps to the `MoN/Deenen_Digi` sidid variant (see signatures below).
- Separate **sound effects driver** exists alongside the music driver (the MON SFX Editor v1.00 tool, 1990, is its editor).

### Composition workflow
- Composers typed hexadecimal note data and labels directly into assembler source — no visual tracker UI.
- The assembled binary was the SID player + song data combined.
- After Deenen saw Jeroen Tel arrange a song in ~10 minutes, he created a driver to enable Tel and others to compose efficiently (c64-wiki source).

### PSID header observations (from binary analysis of HVSC SIDs)
Based on parsing Charles Deenen's SID files in HVSC:
- Load addresses vary widely (no fixed relocation): $0BAB, $0C5F, $0C40, $1000, $1273, etc.
- **Multi-subtune support**: up to at least 12 subtunes (Back_to_the_Future_III.sid, songs=11).
- **CIA timing**: speed field is non-zero for most SIDs (e.g., `0x00004166` = CIA-timed for some subtunes, VBL for others). After_the_War speed = `0x00004166` (bits 1,5,6 set → CIA subtunes).
- Play address typically points to the start of the binary (play=load or play=load+small offset).
- Init address is a few bytes after load (typically load+6 for After_the_War).
- At $0C82–$0C97 in After_the_War the string "MUSIC BY M.O.N./CD" is embedded in the player code — suggests the player carries a text banner.
- Music data starts immediately after the player code (data region follows code in the binary).

### Identified player variants in sidid.cfg
From `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg`:

**MoN/Deenen** — 8 signature patterns:
```
C9 60 B0 03 4C ?? ?? C9 FF D0 ?? A9 00 END
B9 ?? ?? F9 ?? ?? 9D ?? ?? BD ?? ?? 4A 4A 4A 4A A8 88 30 ?? 5E ?? ?? 7E ?? ?? 4C END
BD ?? ?? DD ?? ?? D0 ?? A9 FE 9D ?? ?? DE ?? ?? F0 ?? BD ?? ?? C9 FF F0 END
C9 C0 90 ?? 29 ?? 0A 0A 0A 9D ?? ?? C8 B1 ?? C9 ?? F0 END
C9 FF D0 0E A9 00 95 ?? B5 ?? F0 04 D6 ?? 10 END
C9 FF D0 17 A9 00 9D ?? ?? BD ?? ?? F0 05 DE ?? ?? 10 END
4C ?? ?? C6 ?? A4 ?? BD ?? ?? 86 ?? 0A 0A 0A AA 8E ?? ?? BD ?? ?? 85 ?? BD ?? ?? 25 ?? 99 04 D4 END
99 00 D4 C8 CA 10 F9 END
```

**MoN/Deenen_Digi** — 2 signature patterns (4-bit sample support):
```
A2 00 F0 ?? 98 0A A8 B9 ?? ?? 8D ?? ?? B9 ?? ?? 8D END
4A 4A 4A B8 50 ?? 4A 4A 4A 18 69 ?? 8D 18 D4 END
```

Notable patterns:
- `4A 4A 4A 4A` (four LSR A) = nibble shift, consistent with 4-bit sample output to $D418 (volume register) in the digi variant.
- `99 00 D4 C8 CA 10 F9` — tight loop writing to SID base ($D400), typical of voice parameter initialisation.
- `C9 FF` = compare A with #$FF — likely a "end of sequence" / "rest" sentinel.
- `C9 60` = compare A with #$60 — likely a note/command byte range discriminator.
- `C9 C0` = compare A with #$C0 — second command range discriminator.
- `0A 0A 0A` (three ASL A) = multiply by 8 — instrument table index (instrument * 8 bytes per entry is a common C64 driver layout).

---

## Format / data structure details

No public format specification document was found. The following is inferred from the sidid signatures and binary analysis:

### Inferred from signatures
- **Command byte encoding**: Two threshold comparisons (`C9 60` and `C9 C0`) suggest a 3-range byte scheme:
  - $00–$5F: note values (96 possible notes)
  - $60–$BF: effect/rest/tie commands
  - $C0–$FF: extended commands (instrument select likely in this range, matching `29 ?? 0A 0A 0A` = AND + 3× ASL = instrument index * 8)
- **Instrument table**: indexed by multiplying a 6-bit instrument number by 8 (`0A 0A 0A` = ×8), giving 8 bytes per instrument entry.
- **End-of-pattern sentinel**: `C9 FF` / `C9 FF D0 17` — $FF byte ends a sequence.
- **Voice counter / decrement**: `C9 FF D0 0E A9 00 95 ?? B5 ?? F0 04 D6 ?? 10` — per-voice countdown with zero-page state.
- **Freq table loop**: `B9 ?? ?? F9 ?? ?? 9D ?? ?? BD ?? ?? 4A 4A 4A 4A A8 88 30 ??` — loads two bytes, XOR or ADC, stores to abs,X, then 4× LSR into Y; counts down. Likely the frequency/portamento table update.
- **Relocation**: No fixed load address; player is not relocatable by a fixed offset (wide range of load addresses observed). Each SID binary is standalone at its composed address.

### Binary header (After_the_War.sid — representative MoN/Deenen SID)
```
Load:  $0C5F
Init:  $0C65  (offset +6 from load)
Play:  $0C5F  (same as load — play entry IS the playback routine)
Songs: 3
Speed: 0x00004166 (CIA-timed for subtunes 1,5,6; VBL for others)
```
- Embedded string at $0C82: "MUSIC BY M.O.N./CD" — the driver carries an authorship banner in the code.
- Frequency table (or note table) visible starting around $0CEF: standard SID frequency byte pairs ($3F52, $6676, $7B92, ...) — confirming MoN/Deenen uses a standard equal-tempered C64 frequency table.

---

## Source code or disassembly references

- **No public source code** for the Musicfile driver has been located. It was closed-source, used commercially.
- **sidid.cfg** (Cadaver/Lasse Öörni): https://github.com/cadaver/sidid/blob/master/sidid.cfg — contains the byte-level player identification signatures for both `MoN/Deenen` and `MoN/Deenen_Digi`.
- **player-id** (WilfredC64): https://github.com/WilfredC64/player-id — another player identification utility that covers MoN/Deenen.
- **DRAX test SID**: `MUSICIANS/D/DRAX/Test_in_Deenens_Routine.sid` — DRAX wrote a SID using the Deenen driver ("Test in Deenen's routine"). This is strong evidence the driver was distributed to other composers and is a useful reverse-engineering anchor (a minimal, named test case).
- **Turbo Ass**: The driver was assembled with Turbo Assembler (Turbo Ass) for C64. The original .asm source is not in HVSC or known public archives.

---

## Known games using MoN/Deenen driver

Derived from HVSC classification (engine='MoN/Deenen') — composers who used this driver:

**Charles Deenen** (15 SIDs classified as MoN/Deenen in HVSC):
- After the War (Dinamic, 1989)
- Astro Marine Corps
- B.A.T. (Ubisoft, 1990)
- Back to the Future III (Image Works, 1991) — 11 subtunes
- Constant Runner, Cool Tune, Ding van Charles
- Eye to Eye (intro), F1 Simulator, Hotline Intro, Hotline Intro Tune
- Koekoek, Lord of the Rings, Mantalos, Mr. Heli, Satan, Shitty Disco Dump
- Smooth Criminal, Zamzara

**Jeroen Tel** (~60+ SIDs): Cybernoid (via loader), Hawkeye, Turbo Outrun, Supremacy, Outrun Europe, North and South, Navy Moves, RoboCop 3, Lemmings, Teenage Mutant Hero Turtles, Smash TV, Golden Axe, 2400 AD, Mythm Dan Dare 3, Myth, Rubicon, and many demo/intro tunes.

**Reyn Ouwehand** (~15 SIDs): Stormlord 2, Flimbo's Quest intro, I Like Chopin, Tetris Plus, Terminator, Bad Blood series, Super Stock Car, CosMail tunes, Infinity, Deadlock, Blackmail Tune 1, Miss Ed, Merry New Year Scoop.

**Barry Leitch**: Shoe People, Super Kick Off.

**Other users**: Audial Arts/Prijt Francois (7 SIDs), Marc Francois (Robotix Theme), HJE (Megademo part 2), HeatWave/Yavin (Shortish), Holt Hein (2 SIDs), JVD (7 SIDs), No-XS (2 SIDs), Trugoy (2 SIDs), Joachim Wijnhoven (2 SIDs).

**Total in HVSC #84**: 135 SIDs classified as `MoN/Deenen`.

The `MoN/FutureComposer` engine (4024 SIDs) is entirely separate — it is the standard Future Composer player rebranded, not Deenen's Musicfile.

---

## Leads to follow

1. **Disassemble After_the_War.sid** — good entry point: 3 subtunes, medium size (6083 bytes), clear "MUSIC BY M.O.N./CD" banner. Init offset is only +6 from load, suggesting a minimal dispatcher. Run `tools/seed_disassembly.py` on it.

2. **DRAX/Test_in_Deenens_Routine.sid** — explicitly named as a test of the driver. Likely a minimal, clean implementation with no game-specific overhead. High priority for understanding the driver's bare structure.

3. **Reyn Ouwehand/First_MON_tune.sid** — named "First MON tune" — likely an early/simple usage. Compare with later Ouwehand SIDs to understand driver evolution.

4. **Binary-diff multiple MoN/Deenen SIDs** to find common player code region (the player bytes are fixed; only data/song changes). Comparing After_the_War, Astro_Marine_Corps, B_A_T, and a Jeroen Tel SID should isolate the player vs data boundary.

5. **Investigate CIA timing**: speed field varies across SIDs; need to understand how the driver handles multi-rate subtunes (speed mask per-song vs single global rate). Back_to_the_Future_III (11 subtunes, speed=0x00004261) is the most complex case.

6. **Try fetching c64.com interview** with a different tool or via HTTP (the SSL cert fails): `http://www.c64.com/gt_display_interview.php?interview=8` — this is specifically a Charles Deenen interview that may contain workflow details.

7. **CSDb tool releases to examine**:
   - MON SFX Editor V1.00 (1990): https://csdb.dk/ — search for release ID to get the actual binary. The SFX editor format may share data structures with the music driver.
   - MON SFX Relocator V1.0 — could reveal relocation mechanics.

8. **Jeroen Tel Retro Hour interview** (EP496, 2024): https://audioboom.com/posts/8772654 — may contain technical C64 driver details. Also EP114 on YouTube.

9. **Wayback Machine** for charlesdeenen.com and jeroentel.com — blocked from this agent; try fetching manually or via a different tool to get any archived technical documentation or download links.

10. **Check for alternate engine versions**: The sidid signatures include 8 patterns for the base driver. Multiple signatures may indicate two driver revisions (MoN Old / MoN New). Identify which SIDs match which subset of signatures to date the versions.

11. **Instrument table size**: The `0A 0A 0A` (×8) multiplier suggests 8 bytes per instrument. Cross-check by finding the instrument table start in a disassembled SID and counting entries to establish the instrument byte layout.

12. **4-bit digi variant**: `MoN/Deenen_Digi` signature has `4A 4A 4A 18 69 ?? 8D 18 D4` — writes to $D418 (volume register). Only 0 SIDs are classified as this variant in HVSC #84 (sidid may not identify them reliably, or they were reclassified). Search for "sample" or "digi" in Deenen's/Tel's SIDs manually.
