---
source_url: https://codebase64.org/doku.php?id=base:sidwinder
fetched_via: direct
fetch_date: 2026-06-17
author: various
content_date: various
reliability: secondary
---

# SidWinder — Codebase64 Wiki + Lemon64 Forum Research

## Result summary

**Codebase64 wiki:** No SidWinder page exists at `base:sidwinder` or via search.
The wiki returned empty pages for all SidWinder queries. Codebase64 has no
technical article on this engine.

**Lemon64 forums:** SidWinder is occasionally listed alongside other C64 trackers
(e.g. in the MIDI-tracker thread t=26647) but there are zero dedicated threads and
no technical discussion of its format or player internals found in any searched thread.
The Lemon64 search system blocked unauthenticated scraping entirely.

---

## Confirmed provenance

From `cadaver/sidid` (sidid.nfo, the canonical C64 player identification database):

```
SidWinder
   AUTHOR: Balázs Takács (Taki)
 RELEASED: 1999 Natural Beat
REFERENCE: https://csdb.dk/release/?id=66494
```

CSDb releases:
- **SIDwinder V01.22** — id=66494, 1999, Natural Beat (C64 tool)
- **SIDwinder V01.23** — id=101758, 2000-03-15, Natural Beat (C64 tool, 534 downloads)
- **SIDwinder V1.23 Enhanced!!** — id=99574, 2011-04-17, PCH (adds "live piano", improved stay function, extra M-key menus; based on GPL TLC/CNS V01.23 port)
- **SIDwinder V0.2 - Preview** — id=253271, 2025-05-24, Genesis Project — NOTE: this is a MODERN tool of the same name, unrelated to Taki's 1999 editor.

---

## Technical content found (from Plus/4 World page + CSDb comments)

The Plus/4 World page for `SIDwinder_V01_23`
(https://plus4world.powweb.com/software/SIDwinder_V01_23) contains the most
detailed technical description found anywhere online. Content below is extracted
verbatim or closely paraphrased from that page.

### Data format

- File format: compact data format (NOT bare memory images; bare images discontinued)
- Backward compatibility: loads/edits songs from V01.2x; song data format unchanged except identity field
- Subtunes: up to 32 per file
- Sectors: up to 96 sectors with 256 instructions per sector
- Instruments: up to 64 sound definitions

### Player memory architecture

- Zeropage pointer pair: `$FB–$FC` (user-configurable at pack time)
- SID base address: `$D400` (C64) or `$FD40` (Plus/4 SID card)
- Identity field storage: player start address + `$20`
- PAL-only (clock sync for frequency tables); NTSC may work at single speed only

### Effect / modulation tables (4 systems)

1. **Wave/Arpeggio Table** — waveform selection (`$00–$8F`) with arpeggio offsets; supports repeat and jump instructions
2. **Filter Table** — cutoff frequency + resonance modulation with filtertype specification
3. **Pulse Width Table** — amplitude modulation for pulse-wave instruments
4. **Slide/Vibrato Table** — frequency modulation with glide/slide and absolute-frequency modes

### Performance / multispeed

- Up to 16× music speed (supported in editor)
- Multispeed implemented as distributed player calls throughout the VBI frame
- Independent volume control via registers `$1673` and `$165D` (likely player-internal addresses, not SID registers)
- Gate bit masking eliminates channel-off clicking artifacts

### Platform differences (C64 vs Plus/4)

- Separate frequency tables required: C64 derives from 1.789 MHz; Plus/4 SID card uses 885 kHz nominal
- ADSR speeds: 9/10 relationship (Plus/4 vs C64)
- Glide/slide speeds need 10/9 multiplication when porting C64 compositions to Plus/4
- Zeropage `$FB` conflicts with Plus/4 ROM config; `$FC` recommended for Kernal compatibility

### Software components

- **Editor** — full composition interface: track, sector, sound editors
- **Packer** — completely rewritten in V01.23; multi-pass optimisation; removes unused components; relocation + custom ZP config; generates identity metadata
- **Utilities** — ASCII viewer with PETSCII conversion, TAB support, print; runs on C64 or Plus/4 (16K minimum)

### Source availability

Full source code released under GPL with V01.23. Archive at Zimmers:
- `SIDwinder_V0123_src.zip` (341 KB) — contains:
  - `SRC/ED.ASM` — editor
  - `SRC/PACKER.ASM` — packer
  - `SRC/PLAYER.ASM` — player (the ground truth for format RE)
  - `SRC/SIDR.ASM` — SID-related routines
  - `SRC/VIEWER.ASM` — viewer
  - `SRC/CHARS.BIN`, `MASKS.BIN`, `SECTORS.BIN`, `TRACKS.BIN`, `VCHARS.BIN` — binary data
  - `COPYING`, `GENERAL`, `HISTORY`, `PLUS4`, `PROGRAM`, `README`, `SUMMARY` — docs
  - `SIDW0122` — technical spec for V01.22
  - `PLAY0122.ASM`, `PLAY0122.SEQ` — V01.22 player source

### Known bugs (from CSDb V1.23 Enhanced comments)

- Packer bug reported by Luca (FIRE): "years ago, I spotted out a bug in that version's packer, and TLC coded and released a fixed SIDwinder V01.23 packer on Plus/4 which works ok."
- PCH (Enhanced author): "Only one music [has] problem with END MUSIC mark … maybe is it this problem; I do not study packer."
- Luca: "the longer the tune, the higher the probability to collect bugs in endpoints and/or glide/slide."

---

## Disambiguation: modern "SIDwinder" tool

There is a 2025 web tool at https://sidwinder.netlify.app/ called "SIDwinder — C64 SID Music Linker" by Genesis Project. This is a DIFFERENT product (a SID linker utility, not a music editor) and is unrelated to Taki's 1999 editor. The Genesis Project CSDb release id=253271 is also a different V0.2 Preview. Do not confuse the two.

---

## Leads to follow

1. **Source code — primary RE target:**
   - `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_src.zip`
   - Download and read `SRC/PLAYER.ASM` directly — this is the ground truth for all format details (sector layout, instrument block offsets, table formats, ZP usage).
   - `SIDW0122` doc file inside the zip is the written V01.22 technical spec.
   - `HISTORY` file will document version-to-version changes.

2. **Plus/4 World page** (richest online description found):
   - https://plus4world.powweb.com/software/SIDwinder_V01_23
   - May have additional user comments or links not visible in the scrape.

3. **CSDb releases to check for comments:**
   - V01.22: https://csdb.dk/release/?id=66494
   - V01.23: https://csdb.dk/release/?id=101758
   - V1.23 Enhanced: https://csdb.dk/release/?id=99574 (PCH + Luca comments already captured above)

4. **Disk image (editor + player on-disk):**
   - https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/SIDwinder_V0123_C64.d64.gz
   - Mount in VICE + disassemble the packed player binary to get relocated addresses.

5. **sidid.nfo signature bytes:**
   - The cadaver/sidid database lists SidWinder as a known player family but contains no fingerprint bytes in the nfo text. Check `sidid.cfg` in the same repo — it may carry the actual byte signatures used by the detector.
   - https://github.com/cadaver/sidid/blob/master/sidid.cfg (worth fetching)

6. **HVSC DOCUMENTS folder:**
   - Check `hvsc84/DOCUMENTS/` for any SidWinder-specific format doc (some editors have `.txt` specs bundled).

7. **Lemon64 threads listing trackers** (SidWinder mentioned but no technical content):
   - https://www.lemon64.com/forum/viewtopic.php?t=26647 (MIDI trackers thread)
   - https://www.lemon64.com/forum/viewtopic.php?t=63783 (Friendliest SID tracker)
   - https://www.lemon64.com/forum/viewtopic.php?t=51003 (Easy to use SID tracker)

8. **TLC's Plus/4 fixed packer** — referenced by Luca in CSDb comments as fixing the packer bug. May be a separate CSDb release worth finding; search csdb.dk for "TLC" + "sidwinder".
