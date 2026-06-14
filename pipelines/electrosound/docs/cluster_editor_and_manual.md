# Electrosound 64 — Editor, Manual, and Musical Model

## Provenance

| Field | Value |
|---|---|
| author | Jostein Trondal (research sweep) |
| fetch_date | 2026-06-14 |
| content_date | 1985–1987 original; secondary sources 2006–2024 |
| primary_sources | VGMPF Wiki, Lemon64 forums, c64-music blogspot, remix64.com interviews, sidid.cfg, C64-Wiki (DE) |
| reliability | MEDIUM — no physical manual found; facts triangulated across ≥2 independent sources where possible |

---

## 1. The Editor

### Identity

- **Full name:** Electrosound 64  
- **Nickname:** Leccysound  
- **Publisher/developer:** Orpheus Ltd. (later: Orpheus Software)  
- **Author:** Steven Mellin (programmer and composer; also spelled "Steve Mellin")  
- **Year:** 1985 (editor); still in use 1986–1988  
- **Price:** £14.95 (UK retail)  
- **Platform:** Commodore 64  
- **Company address:** Hatley St George, Bedfordshire, UK (confirmed from The Young Ones game credits)

### Orpheus Ltd. context

Orpheus was a small UK developer/publisher active ~1985–1986. Their known C64 output:

- *Electrosound 64* (1985) — the music editor
- *The Young Ones* (1986) — adventure game (music by Steve Mellin using Electrosound)
- *Super Mario Bros.* (1986) — proposed C64 port; Nintendo declined, never released
- Paul Kaufman served as Orpheus director; previously at Tansoft (Oric)
- Orpheus is primarily remembered for Electrosound; the company appears to have dissolved around 1987

### CSDb entries

CSDb is returning 503 at time of research. Known release IDs (for follow-up when CSDb is accessible):

| CSDb ID | Title | Notes |
|---|---|---|
| 27433 | Electrosound | Original commercial release |
| 85170 | Electrosound 64 by The Snail (1985) | Scene crack |
| 150998 | Electrosound 64 by Elite Crackers (1986) | Scene crack |
| 254231 | Electrosound 64 | Additional entry |

SIDID fingerprint entry (from `sidid.cfg`):
```
Electrosound
F0 01 60 A9 64 9D ?? ?? BD ?? ?? C9 01 END
RELEASED: 1985 Orpheus
REFERENCE: https://csdb.dk/release/?id=27433
```
Single pattern — no version variants in sidid as of 2026-06-14. This matches ~297 HVSC SIDs.

### Known versions

No "PLUS", "v2.0", or sequel version has been found in any public source. Only one identified variant is known to the scene. The editor is treated as a single-version product across all documentation found.

---

## 2. The Musical Model

This is the highest-confidence section; cross-checked across VGMPF, c64-music blogspot, and Lemon64 forum.

### 2.1 Top-level data model

The composer's workflow proceeds in four ordered steps (as presented by the main menu):

1. **Instrument definition** — up to 10 instruments
2. **Sequence composition** — up to 20 sequences
3. **Track assembly** — sequences chained into songs
4. **File management** — save / load

The editor saves "5 songs and 10 instruments into one big source file." A separate instrument file (up to 10 instruments) can also be saved independently for reuse across songs or as SFX material.

### 2.2 Instrument model

Up to **10 instruments** (numbered 1–10 implied; exact numbering not confirmed from sources).

Per instrument the composer can set:
- **All SID chip registers** — this implies full access to: waveform, ADSR (attack+decay byte, sustain+release byte), pulse width (12-bit), filter cutoff, filter resonance/routing, ring mod, sync. Exact which registers are editable in the UI is not specified in public docs.
- **Modulators** — pitch, pulse width, cutoff frequency, key-down, key-up. Each of these can have its own modulator independently.

Per modulator the parameters are:
- **Delay** — number of frames before modulation begins
- **Speed** — rate of modulation (frames per step?)
- **Depth** — amplitude of modulation
- **Direction** — one of: up, down, vibrato, shuffle
- **Restart** — when to restart the modulator: "upon every note", "after every rest", or "not at all"

The "key-up" and "key-down" modulation targets are not further explained in public sources but likely correspond to gate-on (key pressed) and gate-off (key released) envelope phases — potentially controlling what happens to modulation when a note is triggered vs released.

"Shuffle" direction is mentioned but not explained in any found source. Likely a rhythmic-offset or swing mode for the modulator cycle (analogous to the same term in DR patterns).

The editor supports a **Commodore Music Maker overlay** for the keyboard — a physical plastic overlay that maps the C64's two-octave keyboard to musical notes, which makes live note input easier.

### 2.3 Sequence model

- Up to **20 sequences**
- Up to **240 notes** per sequence (steps)
- **16 note lengths** per pattern (per Peter Clarke interview)
- **3 instruments** assigned per sequence — one per SID voice, fixed for the entire sequence
- The instrument-to-voice assignment does not change mid-sequence
- When a voice rests, a **drum sound** may be inserted from a built-in library of **24 unmodifiable drum sounds**
- Per sequence, a **tempo** is set

The sequence model is pattern-based (not a linear tracker), analogous to the later MOD format's pattern table.

### 2.4 Track model (song)

A **track** is an ordered list of sequence references — sequences chained to form a full song. Up to **5 songs** can be stored in the main source file.

There is no confirmed per-track transpose or other track-level parameter documented in public sources.

### 2.5 Tuning

- **A = 423.9 Hz** (not A=440 Hz standard)
- Barry Leitch's games confirm this: all his Electrosound-era drivers are "tuned at 424 Hz" (briefly 434 Hz during 1988 before he switched tools)
- This is a fixed property of the compiler/player; the composer cannot change it

### 2.6 Driver characteristics

- **Does not loop** — the song plays once and stops; the calling game program is responsible for any looping
- **Requires the game program to redefine the tempos** — i.e., the compiled output's tempo table must be patched or supplied by the game at runtime for multi-speed tunes (or the game uses the compiled defaults)
- **CIA-timed** — the player uses CIA1 timer; location `$02AD` stores the active tempo value during playback. Dynamic tempo changes within a tune require the game programmer to patch CIA1 timer values manually (confirmed by the Lemon64 conversion thread)
- **Sound effects API** — the driver supports SFX calls that temporarily mute one musical voice, play a sound effect there, then restore the music. Described as "a bit complicated" to use
- **Poorest-performing known player** — described in multiple sources as "the slowest known on the C64"; poorest code quality among the era's editors (confirmed by TMR: "Electrosound's compiler was appalling")
- Jason Page (who used it briefly): "The code for running their audio data had bugs in it though"

### 2.7 Compiler

The editor produces a **source file** (music data only; no player code). A separate **Electrosound compiler** program converts this into a deployable `.prg`:

Compiler workflow:
1. Load compiler program
2. Load source file
3. Load up to 2 instrument files (optional extra instruments)
4. Enter a start address (dictated by the game programmer)
5. Compiler outputs a `.prg` file embedding music + player code starting at the given address

The compiled `.prg` has a known internal layout (from Lemon64 conversion thread, using load address `$1000` as example):

| Offset from load | Address (at $1000 load) | Purpose |
|---|---|---|
| +$0518 | $1518 | **Init entry point** (JSR here to initialise) |
| +$0A65 | $1A65 | **IRQ/play routine** (call this from IRQ or main loop) |
| — | $02AB | Tune number (0-based, i.e. tune-1) |
| — | $02FF | Tune speed |
| — | $02F9 | Play flag (set to $01 to enable playback) |
| — | $02AD | Current tempo (read-only during playback) |

IRQ routine bug: the compiler does not properly set up the IRQ chain; two `JMP $EA31` instructions inside the play routine must be patched to `RTS` at offsets `+$1A7B` and `+$1A84` (i.e. `$1A7B` and `$1A84` when loaded at `$1000`) for the routine to work correctly in a standalone SID context.

The data section starts at offset `+$007C` from load address (0x7C = 124 bytes of header/code before music data begins, based on Lemon64 example `data offset: 0x7c`).

Typical compiled size: `$1000`–`$53FF` = ~17 KB (Lemon64 example), though this will vary with song content.

---

## 3. Editor Operation (UI Keys)

From c64-music blogspot (moderate confidence — likely sourced from experience with the editor, not from a scanned manual):

### Sequence Write mode

| Key | Function |
|---|---|
| N | Play (start playback) |
| M | Pause / Continue |
| B | Stop |
| , (comma) | Step backward |
| . (period) | Step forward |
| A / S / D | Increase channel 1/2/3 volume |
| F / G / H | Toggle channel 1/2/3 switch (waveform?) |
| J / K / L | Filter modulation for channels 1/2/3 |
| ' (apostrophe) | Filters (emulator key mapping) |
| ` (backtick) | Reset sequences (emulator) |
| Arrow keys | Step adjustment |
| F1 | Switch channel |

### Track Write mode

| Key | Function |
|---|---|
| Z / Shift+Z | Decrease / increase track number |
| X / Shift+X | Decrease / increase sequence number |
| C / Shift+C | Delete / add sequences |

The UI is described as "probably the easiest to use without a manual" — the menu-driven approach and pre-built instruments let composers start without reading documentation.

---

## 4. Notable Composers and Games

| Composer | Connection to Electrosound |
|---|---|
| Barry Leitch | Primary tool 1986–1988; first game was *I.C.U.P.S.* (C64, 1986); used Electrosound on one C64 while imagining chords on another; all drivers tuned at 424 Hz |
| Peter Clarke | Used it before Ocean; composed *Repton 3* on it; wrote *Ocean Loader 3* on Electrosound first, then rewrote with Martin Galway's driver |
| Keith Tinman | Listed as notable user (VGMPF); no specific games identified in sources |
| Jason Page | Used it "for a while" before switching to other tools; noted bugs in the player code |
| Jonathan Dunn | "Dabbled" with it alongside college music studies early in career; no specific Electrosound-specific games identified |
| Matt Gray | Listed as notable user (VGMPF); no specific Electrosound games identified in sources found |
| Steve Mellin | Author of the editor; composed *The Young Ones* (1986) using it |

---

## 5. Historical Context

- Electrosound predates Soundmonitor (1987), which largely superseded it
- Described as "the most user-friendly" editor of its era, but without "bells and whistles" of more advanced editors regarding instrument creation
- One of the first C64 music editors; "wasn't quite a tracker" (the Soundtracker hadn't been written at the time)
- Used heavily in British demos (1986) and UK commercial game music
- Soundmonitor (by Charles Deenen, 1987) took over as the standard tool after 1987

---

## 6. What Was NOT Found

- **No physical manual scan** — the Scribd document "ELECTROSOUND-pdf" (18 pages, uploaded by Chiara Provvidenza) exists at https://www.scribd.com/document/460293234/ELECTROSOUND-pdf but requires a subscription to read. This is the highest-priority follow-up target.
- **No later versions** — no "PLUS", "v2.0", or updated edition found. The editor appears to have been a single product.
- **No magazine reviews found** — Zzap!64, Commodore User, Your Commodore from 1985–1986 likely reviewed Electrosound but no scanned issues with a confirmed Electrosound review were located. Zzap!64 issues 1–20 (May 1985–Dec 1986) are on archive.org but require manual search.
- **CSDb release pages** — all 503 at time of research (csdb.dk/release/?id=27433, 85170, 150998, 254231). Likely contain user comments with technical notes. Try via Wayback Machine: `web.archive.org/web/*/csdb.dk/release/?id=27433` (note: web.archive.org access is blocked in the current environment; must be accessed via a browser).
- **Disk image contents** — the archive.org D64 (`archive.org/details/d64_Electrosound_64_19xx_-`) contains "9 original files" but their names are not listed in metadata. Mounting the D64 in VICE would reveal if there are any README or documentation files on the disk.
- **Modulator "shuffle" semantics** — described but not explained in any source found.
- **Exact SID register mapping** — which specific SID registers the instrument editor exposes (e.g., does it expose $D406 waveform, $D401/$D400 freq, $D405/$D406 ADSR individually?) is not documented in public sources.
- **Drum sound list** — the 24 fixed drum sounds are not catalogued anywhere in found sources.
- **Exact note/step encoding** — how notes are stored in the sequence data (note number byte format, rest encoding, drum trigger encoding) is not documented.

---

## Leads to Follow

1. **Scribd manual (highest priority):** `https://www.scribd.com/document/460293234/ELECTROSOUND-pdf` — 18 pages, likely the actual user manual or a scan thereof. Access requires Scribd subscription or a cached/alternative source.

2. **CSDb release pages (when accessible):** IDs 27433, 85170, 150998, 254231. User comments on C64 scene releases often contain technical reverse-engineering notes. Try: `https://web.archive.org/web/2023/https://csdb.dk/release/?id=27433` in a browser.

3. **D64 disk image:** `https://archive.org/details/d64_Electrosound_64_19xx_-` — download the D64 and list its directory with `c1541 -attach *.d64 -list`. Any `.txt` or documentation files on the disk are primary source material.

4. **Zzap!64 archive search:** Zzap issues 5–15 (Sep 1985–Jul 1986) are the most likely window for a review. Search `https://archive.org/details/Zzap001May85` and the subsequent issues for "Electrosound" or "Orpheus".

5. **Commodore User / Your Commodore:** Both magazines are partially archived on archive.org. Search `https://archive.org/search?query=Commodore+User+magazine` and `https://archive.org/search?query=Your+Commodore+magazine` for 1985–1986 issues.

6. **Barry Leitch interview (VGMPF):** `https://www.vgmpf.com/Wiki/index.php?title=Barry_Leitch` — has detailed workflow notes. His early game SID files in HVSC (I.C.U.P.S., 1986 onwards) could be reverse-engineered to confirm the binary format.

7. **Waz (Lemon64 user):** The user "Waz" in the Lemon64 thread https://www.lemon64.com/forum/viewtopic.php?t=19807 has deep knowledge of the compiled format and offered to analyze .prg files. Consider contacting via Lemon64 PM.

8. **HVSC SID files themselves:** HVSC classifies ~297 SIDs as Electrosound. Disassembling the player code out of any compiled SID (they all share the same player at `load+$0A65`) would be the ground-truth source for the exact data format. The sidid fingerprint `F0 01 60 A9 64 9D ?? ?? BD ?? ?? C9 01 END` at offset ~`+$0A65` is the player start.

9. **Facebook group post:** `https://www.facebook.com/groups/c64com/posts/1036776763873033/` — "Any Electrosound 64 fans out there?" thread may have scene veterans with technical knowledge.
