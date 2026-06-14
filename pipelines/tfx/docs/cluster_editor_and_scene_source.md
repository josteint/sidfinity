# TFX Music Editor — Editor, Scene & Source Research Cluster

## Provenance header

| field | value |
|---|---|
| primary_source_url | https://www.unreal64.net/downloads/c64/Tfx_2_99.zip |
| secondary_source_url | https://csdb.dk/release/?id=18562 (v2.99), https://csdb.dk/release/?id=38900 (v1.2), https://csdb.dk/release/?id=110111 (v1.0) |
| fetched_via | WebFetch + Bash unzip |
| fetch_date | 2026-06-14 |
| author | Lada "Ray" Lostak / Unreal (Czech Republic); documentation co-authored by Jaymz Julian "A Life in Hell" / Warriors of the Wasteland (Australia) |
| content_date | 1995–2005 (player source: (c) 1995–2002; manual copyright: 1995–2004) |
| reliability | HIGH — primary sources (zip from official unreal64.net mirror; CSDb cross-checked). Manual, player assembler source, and hyperpacker C source all extracted from the v2.99 release zip. |

---

## 1. Author and group

**Ray** = Lada 'Ray' Lostak, Czech Republic. Current member of Unreal (also known as Orcave inc.). His real name appears in the Commy.ass C64 base-constants file: `(c) Lada 'Ray' Lostak (c) Orcave inc.`. Contact at the time of v2.99: ray@unreal64.net.

**Unreal** — Czech C64 demoscene group. Website: unreal64.net. Current members (as of Demozoo): Ray (Czech Republic), PCH / Petr Chlud (Czech Republic), Sillicon (Czech Republic). NOT a Polish group — research.md was incorrect. Ex-members include Polish sceners Elban and Gregfeel. PCH ("TFX Test", 1997) is an active Unreal musician.

**A Life in Hell** = Jaymz Julian, Australia / Warriors of the Wasteland. Starting from v2.98 (2005), contributed player code improvements, demo music on the release, and co-authored the manual. Contact: jaymz@unreal64.net. His SID file "TFX = Future Composer" (CSDb id 16222) is listed as a SID tune, not an editor.

**PseudoGrafx (Pseudografx / PG)** — Unreal member (Czech Republic, pg@pinknet.cz). Responsible for all graphical design, charset, and original TFX concept/design ("originally designed by PseudoGrafx").

---

## 2. Version history (complete from CSDb search)

| CSDb ID | Version | Year | Notes |
|---|---|---|---|
| 110111 | v1.0 | 1995 | First release. Code: Ray. Music/docs/design: Pseudografx. Two example songs: "Fire!" and "Fonttime" by Pseudografx. |
| 38900 | v1.2 | 1996 | Code: Ray. Graphics/design: Pseudografx. |
| 38901 | v1.3 | 1996 | Code: Ray. |
| 125997 | v2.4 | 1996 | Code: Ray. Also archived at archive.org (d64_TFX_v2.4_1996_Unreal). |
| 237763 | DMC-to-TFX v2.7 Convertor v1.4 | 1996 | Utility to convert DMC 7.x songs to TFX v2.7 format. Confirms TFX was usable from DMC workflows. |
| 38902 | v2.5 | 1997 | |
| 24717 | v2.6 | 1999 | Code: Ray. Graphics/design: Pseudografx. |
| 237765 | v2.7 | 1999 | Code: Ray. |
| (implied) | v2.8, v2.9 | ~2001–2002 | Mentioned in v2.98 changelog: "Import for TFX v2.7, v2.8 and v2.9 files". |
| 38903 | v2.92 | March 2003 | Code: Ray. Graphics/design: Pseudografx. |
| 126000 | v2.97 | 2004 | Manual copyright states 1995–2004. |
| 16473 | v2.98 | Jan 2005 | Code: Ray + A Life in Hell. Music: A Life in Hell. Docs: A Life in Hell. Major rewrite of player. |
| 18562 | v2.99 | Jul 2005 | Code: Ray + A Life in Hell. Final known release. A Life in Hell: "The player is much improved from the older (pre v2.9) player." |
| (Demozoo) | v2.98 | Jan 2005 | Demozoo lists this as the most recent in the "Unreal" group productions. |

**Note on Demozoo:** Lists TFX v2.98 as a production, but the CSDb search returned a v2.99 as well (Jul 2005, id 18562). The unreal64.net/downloads/c64/ directory (last modified 2007) contains both Tfx_2_98.zip and Tfx_2_99.zip.

The sidid.nfo (cadaver/sidid) records only: `TFX / AUTHOR: Ray / RELEASED: 1995 Unreal / REFERENCE: csdb.dk/release/?id=110111` — no hex player signatures published there.

---

## 3. Available source files (from Tfx_2_99.zip)

All files saved to `docs/src/`:

| file | description |
|---|---|
| `tfx-manual-v2.99.txt` | Full user manual (v2.97 title, covers 2.98+2.99 changes) — 1608 lines |
| `tfx-news-v2.99.txt` | Changelog for 2.97–2.99 |
| `tfx-keys-v2.99.txt` | Quick-reference keyboard shortcuts |
| `Player-v2.99.ass` | 6502 assembler source of the TFX player (for the hyperpacker). `(c) Ray/Unreal 1995-2002`. Last revision noted: 20/11/96 and 28/06/97, but file is from 2005. Includes note-frequency table (tnote1/tnote2), full playback engine. |
| `config-v2.99.ass` | Feature-flag config for assembling minimal player (which optional features to include) |
| `hyperPacker-v2.99.c` | PC-side C tool: reads a packed TFX SID binary, extracts the internal data structures, and repackages with a smaller player build. Reveals the on-disk data layout. |

The zip also includes `final/tfx.d64` (the actual editor disk image, 174 KB) and `hyperpacker/Src/Commy.ass` (C64 hardware constants, signed by Ray/Orcave inc.).

---

## 4. Feature model (from the manual)

### Overall structure

TFX is a **sector-based** C64 music editor using a 3-voice SID sequencer. Terminology:
- **Track** = ordered list of sector numbers + commands (LOOP, END, TRANSPOSE) per voice
- **Sector** = variable-length pattern of up to 255 bytes; one sector per voice active at a time
- **Instrument** = ADSR envelope + pointers into Wave/Pulse/Filter tables + flags + vibrato params
- **Tables** = shared pools: Wave Table, Pulse Table, Filter Table

Up to 80 sectors ($50) per song. Up to 5 independent subsongs in one file. Memory range: $1000–$2FFF (8 KB). Player loads at $1000 (init at $1000, play at $1003, and optionally a "table-only" player at $1006 for multispeed).

### Instrument parameters

```
ADSR | WT | PT | FT | FLAGS | VDL | VDP | VS
```

- **ADSR**: Attack/Decay/Sustain/Release — standard SID envelope.
- **WT**: Initial wave table pointer (entry point into the shared wave table).
- **PT**: Initial pulse table pointer.
- **FT**: Initial filter table pointer.
- **FLAGS** (8 bits):
  - `No Pulse Reset` — do not reset pulse table on new note trigger.
  - `rnote pos hl` — changes relative note commands in wave table from frequency-relative to note-index-relative (right-shifted 4).
  - `no flt set` — do not reset filter table on note trigger (for slave channels).
  - `Filter` — enable filtering for this instrument.
  - `Hold manual` — hold gate on until explicit GATE command.
  - `pulse off` — do not run pulse table at all.
  - `hold off` — do not hold note at all.
  - `hold gate` — hold until GATE command.
- **VDL**: Vibrato Delay (frames before vibrato starts).
- **VDP**: Vibrato Depth.
- **VS**: Vibrato Speed.

### Wave Table

Two-byte entries: `[waveform+control] [mode/value]`.

Left byte encodes: `wave(4 bits) | gate(1) | ringmod(1) | osc_sync(1) | test(1)`.

Right byte interpretation depends on the current **wave table mode** (changed by commands embedded in the table):

| Mode | Command | Right-byte meaning |
|---|---|---|
| **Normal** (default) | `NRM` | Semitone offset (like JCH/DMC/SDI) |
| **Hard Frequency Hi** | `SHI $xx` | Sets SID freq high byte to $xx00 |
| **Hard Frequency Lo+Hi** | `SHL $xy` | Sets SID freq to $0x / low = $y0 |
| **Relative Freq Hi** | `RHI` | Add value to current note freq (hi byte) |
| **Relative Freq Lo** | `RHL` | Add value to current note freq (lo byte) |
| **Hard Note** | `HRD` | Direct note index ($30 = middle C, $31 = C#, etc.) |

Other wave table commands:
- `AD $xx` — Set Attack/Decay register.
- `SR $xx` — Set Sustain/Release register ($00 restores original).
- `DEL $xx` — Delay X frames.
- `JMP $xx` — Jump to line X (editor updates target on insert/delete).
- `JWG $xx` — Jump if note is currently held (gate set).
- `USE $xx` — Use table variable N (actually variable N+1).
- `SPD` — Set wave table execution speed.

### Pulse Table

One-byte entries (value or command+parameter):

The 12-bit SID pulse width is stored as 8 bits only; a direct value $xx sets pulse to $xx0. Full 12-bit precision available only via ADD/SUB accumulation.

Commands:
- `SET $xx` — Set pulse width to $xx0.
- `SAC $xx $yy` — Set pulse width to $xxyy (16-bit accurate, added in v2.99).
- `ADD $xx` to `$yy` — Increment pulse by $xx until it reaches $yy (Note: can infinite-loop if target not reachable).
- `SUB $xx` to `$yy` — Decrement similarly.
- `DEL $xx` — Delay X frames.
- `JMP $xx` — Jump.
- `JWG $xx` — Jump if gated.
- `SPL $xx` — Start split/second pulse program at position $xx. v2.97+. Two pulse programs run simultaneously; finalPulse = pulse1 + (pulse2 − $0800).
- `HRD` — Hard note mode in pulse context.
- `USE $xx` — Table variable.

### Filter Table

Same structure as Pulse Table but for the SID filter:
- `SET $ab $cc` — Set filter type (a), resonance (b), cutoff ($cc).
- `SAC $xx $yy $zz` — 16-bit-accurate filter set (v2.99).
- `ADD`/`SUB`/`DEL`/`JMP`/`JWG`/`SPL`/`USE` — same semantics.
- Filter type $00 = filter off (v2.98).
- All 11 bits of cutoff frequency controllable (v2.98+).

### Sector (pattern) commands

Each row in a sector has: `[note] [instrument] [effect(s)]`. Multiple effects per note supported (up to 64 per row).

Note format: Symbolic (e.g. C-4, C#3) + instrument number. Special note values: `END` (end of sector), `GATE` (gate off / note off), `---` (pause/empty row).

Sector effects:

| Key | Command | Description |
|---|---|---|
| `C=` `-` | `---` | Pause / empty row |
| `C=` `+` | `END` | End this sector |
| `C=` `↑` | `GATE` | Gate off / note off |
| `C=` `a` | `AD $xx` | Set Attack/Decay for current note |
| `C=` `s` | `SR $xx` | Set Sustain/Release for current note |
| `C=` `q` | `ADN $xx` | Set Attack/Decay for next note |
| `C=` `w` | `SRN $xx` | Set Sustain/Release for next note |
| `C=` `x` | `SWITCH` | Toggle switch — new notes only adjust freq, don't retrigger tables |
| `C=` `d` | `DUR $xx` | Set duration in ticks per row ($00–$3F) |
| `C=` `g` | `GLIDE $xx` | Glide from this note to the next note |
| `C=` `h` | `SLIDE $xx` | Slide from current playing note to this note |
| `C=` `v` | `VOL $x` | Set volume (sustain level) of this note ($0–$F) |
| `C=` `b` | `FVOL $x` | Set global volume |
| `C=` `7` | `SETFF $xx` | Set filter frequency |
| `C=` `8` | `SETFT $xx` | Set filter type |
| `C=` `p` | `SETPF $xx` | Set pulse width |
| `C=` `y` | `A GATE $xx` | Auto-gate: gate off X ticks before end of row |
| `C=` `j` | `FADE+ $x` | Fade global volume from 0 to X |
| `C=` `k` | `FADE- $x` | Fade global volume from X to 0 |
| `C=` `1`–`6` | `SETVAR1`–`SETVAR6 $xx` | Set one of 6 table variables ($00–$FE) |
| `C=` `c` | `CTRL $xx` | Control override — OR with waveform control byte (Ring Mod, OSC Sync, Test, Gate, waveform) |
| `C=` `r` | `RLEN $xx` | Set hard-restart length for this channel (frames) |
| `C=` `t` | `SPED $xx` | Set global speed |
| `C=` `i` | `VSPD $xx` | Set vibrato speed |
| `C=` `o` | `VDEP $xx` | Set vibrato depth |
| `C=` `n` | `NOPL` | Toggle "no pulse reset" |
| `C=` `f` | `NOFL` | Toggle "no filter reset" |

### Track (orderlist) commands

The track editor has 3 columns (one per SID voice), each a list of sector numbers and commands:

| Key | Command | Description |
|---|---|---|
| `C=` `e` | `END` | Stop playing song |
| `C=` `l` | `LOOP $xx` | Loop back to given line |
| `C=` `+` | `TRANSPOSE +$xx` | Transpose up X semitones (additive, not offset) |
| `C=` `-` | `TRANSPOSE -$xx` | Transpose down X semitones |

**Important TRANSPOSE note:** Uses additive model (not offset). To undo TRANSPOSE +02, use TRANSPOSE ±00, not TRANSPOSE -02. Must be followed by a valid sector.

### Multispeed / Multiframe

TFX supports 1x to 12x music for all channels simultaneously (up to 72x for a single channel). Two multiframe modes:

1. **Simple mode**: Player called N times per frame at $1003 each call.
2. **$1003/$1006 split mode** (recommended): $1003 called once per frame (full note/instrument advance); $1006 called up to 11 more times (updates only selected parameters — wave, filter, pulse, etc. — as configured by `defplay`). Saves raster time significantly.

Per-channel speeds: channels 1/2/3 can each be assigned independent $1006 update counts. e.g. one channel at 1x, others at 4x.

ADC table: manual raster-line spacing table for high-speed modes (>10x) to avoid player overrun.

### Hard restart mechanism

Variable hard-restart length (0–255 frames, added v2.98). The first row of the wave table is used as the hard-restart row (sets SR register while the trigger pulse is suppressed). Hard restart synchronised across channels for the same hard-restart-finish time. Hard-restart length controllable per-channel via `RLEN` sector effect.

### Vibrato

Vibrato: per-instrument parameters (Delay, Depth, Speed) + per-note overrides via `VSPD`/`VDEP` sector effects. Vibrato starts after VDL frames. Implemented in the player as a sinusoidal frequency modulation added to the note frequency.

---

## 5. Data model (from hyperPacker.c)

The C unpacker reveals the on-disk structure at $1000+:

```c
int sectors[128][255];   // up to 128 sectors, each up to 255 bytes
int waveTab1[255];       // wave table (control byte per entry)
int waveTab2[255];       // wave table (mode/value byte per entry)
int pulseTab[255];       // pulse table
int filterTab[255];      // filter table
int sounds[32][8];       // up to 32 instruments, 8 bytes each
int orders[3][255];      // 3 voices × 255 track positions
int numOrders[3];        // track length per voice
int psetup[16];          // player setup block
int gvol;                // global volume
int spd;                 // global speed
```

Instrument size = 8 bytes (ADSR[2] + WT[1] + PT[1] + FT[1] + FLAGS[1] + VDL[1] + VDP+VS[1]). Up to 32 instruments. The `psound` field in the player is stored as a 5-bit index (0–31) packed into the sector byte: `and #$1f`.

Sector encoding uses special byte values:
- `$ff` = end-of-sector marker.
- `$fe` = GATE command.
- `$fd` = pause (---).
- `$80`–`$BF` = set instrument ($xx and $1f → instrument 0–31).
- `$C0`–`$CF` = set duration ($xx and $3f → DUR 0–63).
- `$D0`–`$DF` = set volume ($xx → VOL with shift).
- `$00`–$5F` = note values (with transpose applied).
- Effects follow the note byte via a pointer mechanism.

Track encoding:
- `$ff` = LOOP (next byte = target line).
- `$fe` = END.
- `$a0`–`$bf` = TRANSPOSE UP (value − $a0 = semitones up after processing).
- `$80`–`$9f` = TRANSPOSE DOWN.
- Other values = sector index.

Player base address: $1000 (init at $1000/$1003, play at $1003, table-only at $1006). Better on $xx00-aligned addresses.

---

## 6. Player source (Player.ass key facts)

From `docs/src/Player-v2.99.ass` (Ray/Unreal 1995–2002, last noted revision 28/06/97):

- Configurable via `config.ass` feature flags (`useVibrato`, `useGlideSlide`, `useComplexPulse`, `useComplexFilter`, `useNopulse`, `useNoflt`, `useSwitch`, `useSetrlen`, `useVariables`, etc.).
- Full 16-bit note frequency table: tnote1 (low byte) + tnote2 (high byte), 96 entries covering ~8 octaves.
- SID register writes via `syd` macro (can be redirected to a debug buffer with `useBufferedWrites=1`).
- Fade implemented as a per-frame volume modulation.
- Complex filter mode: two filter programs summed (fltfrqlo + fltfrqlo2, etc.).
- Game player mode (`gamePlayer=1`): `playFX` entry at init+9; takes note in A, channel×7 in X, instrument in Y, min-play-time in init-1, hard-restart-time in init-2. SFX mode prevents the main player from generating new notes over the effect for the specified time.
- Zero-page usage: $b1 (`zpl`), $b2 (`zph` / `fta`).
- Subtune selection: init called with subtune×8 in A (asl×3 at entry).

---

## 7. Relation to DMC

A DMC-to-TFX converter (v1.4, 1996, CSDb id 237763) was released by Unreal, suggesting TFX was designed to be at least partially import-compatible with DMC data. The sidid.nfo entry records both DMC (Graffity/Unreal family) and TFX as separate player identities. TFX v1.x/2.x have different player structures from DMC v7.x.

---

## 8. SID compatibility notes (from manual)

The manual explicitly warns that **reSID / sidplay2 are not TFX-friendly** — particularly for advanced filter effects and some ADSR timing details. Real C64 hardware recommended. reSID was noted as requiring an extra frame for certain ADSR things.

---

## 9. Known users

- **Pseudografx / PG** (Unreal) — demo songs bundled with v1.0 ("Fire!", "Fonttime").
- **A Life in Hell / Jaymz Julian** (Warriors of the Wasteland, Australia) — demo music on v2.98/v2.99 releases; player code contributions.
- **PCH** (Petr Chlud, Unreal) — "TFX Test" SID (1997, CSDb id 23201).
- The HVSC contains ~269 SIDs identified as using TFX player. The sidid scanner detects TFX but no published hex byte signatures in sidid.nfo.

Regarding **Factor6** and **Henne**: no documentary evidence found connecting these specific composers to TFX. Factor6 (CSDb) appears to be a Czech chiptune composer (Hexadragon, 2015) but no direct TFX association surfaced. Neither appeared in TFX credits, Demozoo records, or CSDb TFX search results.

---

## Leads to follow

1. **Disk image content**: The `final/tfx.d64` (174 KB) from v2.99.zip contains the actual editor. Mount with VICE and read: (a) any HELP or DOC files on the disk; (b) example songs that could reveal typical instrument programming style; (c) the embedded version string ("!tfx2.99" appears in Player.ass depackTables).

2. **Older manual**: The tfx-manual-html.zip also contains tfx-manual.html — identical content but as HTML. No v1.x / v2.4 manual found; the archived d64 images (Tfx_2_4.d64, Tfx_2_6.d64 at unreal64.net) may contain earlier in-program help text. Worth extracting those .d64 images with d64extract.

3. **Player hex signatures for sidid**: The player source is now available. The "!tfx2.99" / "tfx2.99" text at the depackTables block in Player.ass is a likely signature anchor. Can derive sidid-style hex patterns by assembling the player.

4. **Factor6 and Henne**: Check CSDb musician profiles directly for their listed tool/player (e.g. csdb.dk/scener/ with known handles) — CSDb 503-ed during this session. Also check HVSC `MUSICIANS/` subdirectory for "Factor6" or "Henne" SID file headers which carry the player title.

5. **v2.4 d64**: The Archive.org item `d64_TFX_v2.4_1996_Unreal` (screenshotted 20 times) may have readable screenshot content showing the editor UI circa 1996 — check the screenshot_*.png files on archive.org for UI/format clues predating v2.98 changes.

6. **unreal64.net tfx main page**: The http://www.unreal64.net/tfx URL (referenced in CSDb for v2.98/v2.99) was not archived during this session. It may contain feature overview text, a changelog, or a link to older docs. Try Wayback Machine: https://web.archive.org/web/*/unreal64.net/tfx.

7. **Tfx_2_98.zip content**: The unreal64.net download for 2.98 was not unpacked. It may contain an intermediate version of the player source.

8. **No source for v1.x**: The 1995/1996 versions were distributed as .prg files (Tfx_1_2_(pg).prg, Tfx_1_3_(pch).prg) — single executable files without a companion zip. These must be analysed via disassembly to understand the original format, which differs from v2.8+ (the v2.98 changelog notes "import for TFX v2.7, v2.8 and v2.9" implying a format break before v2.7).
