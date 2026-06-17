---
source_url: https://github.com/realdmx/c64_6581_sid_players/blob/main/Whittaker_David/Whittaker_David_Panther.asm
fetched_via: direct
fetch_date: 2026-06-17
author: dmx87 (dmx, Drumtex, Lloyd, Flashman — CSDb scener ID 31068, group Megastyle Inc.)
content_date: unknown (repo active as of 2026)
reliability: primary
---

# David Whittaker C64 Player — Technical Documentation

Sources synthesised: realdmx/c64_6581_sid_players (Panther.asm), VGMPF, Lemon64 forum t=81385 (Bansai), c64.com interview, Wikipedia.

---

## dmx87 Reverse-Engineering Collection

**GitHub repository:** https://github.com/realdmx/c64_6581_sid_players

The repo contains original and reverse-engineered C64 SID music players, formatted for the ACME assembler. Every .asm file assembles to a playable .sid.

**Relevant directory:** `Whittaker_David/`
**Known files:**
- `Whittaker_David_Panther.asm` — Panther (1986 Mastertronic), reversed by dmx87
  - Size: 24,071 bytes
  - SHA: 4b74c5574b5b18507746abaa1af43a3879c1fef6
  - Raw download: https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/main/Whittaker_David/Whittaker_David_Panther.asm
  - This file is already present in this repo at `pipelines/david_whittaker/docs/src/Whittaker_David_Panther.asm`

The repo also holds: Audial_Arts, Bjerregaard_Johannes_MON, Bulka_Adam_FAME, Deenen_Charles_MON, Dunn_Jonathan, Galway_Martin, Gray_Fred, Gray_Matt, Hubbard_Rob, Kimmel_Jeroen, Ouwehand_Reyn_MON, Tel_Jeroen_MON.

**dmx87 scener identity:** CSDb scener ID 31068. Handles: dmx, Drumtex, dmx87, Lloyd, Flashman. Group: Megastyle Inc. Coder + musician. Active 1989–present (hiatus, returned 2016). Notable: Bruce Lee Duology, Trump Tower.

---

## Panther Driver — Detailed Structure

Source: `Whittaker_David_Panther.asm`, reversed by dmx87.
PSID v2, author David Whittaker, year 1986 Mastertronic.

### Memory Map

| Address | Label | Purpose |
|---------|-------|---------|
| $9000 | load/init | Module loads and inits at $9000 |
| $9010–$9037 | v1data | Voice 1 working state (40 bytes per voice) |
| $9038–$905F | v2data | Voice 2 working state |
| $9060–$9087 | v3data | Voice 3 working state |
| $9088 | PlayFlag | Global playback enable flag |
| $9151 | play | Main play vector (called each frame) |
| $9117–$9119 | L_9117/18/19 | Temporary variables |
| ~$93A8 | CommandTable | Jump table for $80–$93 pattern commands |

### Voice Data Block (40 bytes per voice, base = $FA + voice_offset)

All voice state is in a contiguous block. Offsets from voice base:

| Offset | Label | Meaning |
|--------|-------|---------|
| $00 | FLAGS | Voice status flags |
| $01–$02 | PAT/PATH | Current pattern pointer (lo/hi) |
| $03–$04 | TRACK/TRACKH | Track (orderlist) pointer |
| $05 | B05 | (purpose TBD from full disasm) |
| $07 | B07 | (purpose TBD) |
| $09–$0A | ARP2L/ARP2H | Secondary arp pointer |
| $0B–$0C | ARP/ARPH | Primary arp table pointer |
| $0E–$0F | B0E/B0F | (purpose TBD) |
| $10 | NOTC | Note counter (duration counter) |
| $11 | NOTD | Note duration value |
| $12 | NOTE | Last note number played |
| $13 | AD | Current ADSR Attack/Decay value |
| $14 | SR | Current ADSR Sustain/Release value |
| $15–$16 | FQL/FQH | Frequency lo/hi (current) |
| $17–$18 | PWL/PWH | Pulse width lo/hi |
| $19 | B19 | (purpose TBD) |
| $1A–$1C | B1A/B1B/B1C | (purpose TBD) |
| $1D–$21 | B1D/B1E/B1F/B20/B21 | (purpose TBD — 5 bytes, possible arp/effect state) |
| $22 | WAVE | Waveform register value (without gate bit) |
| $23 | CTRL | Control register value (with gate) |

### Routines

| Label | Purpose |
|-------|---------|
| init | SID chip reset + voice data initialisation |
| play | Main per-frame playback dispatcher |
| GetNote | Read next note from pattern stream |
| NextPatValue | Advance pattern pointer |
| SoundUpdate | Frequency and parameter recalculation |
| SIDreset | Hard reset all SID registers |
| StopMusic | Halt playback, gate off |
| pnotdone | Handle note still counting (duration not elapsed) |
| pspecial | Process effect/command bytes |
| pcommand | Dispatch $80–$93 command bytes via CommandTable |
| L_9297–L_93FB | Individual command handlers |
| L_935B, L_9363 | Flag set/clear operations |
| L_939A, L_93BD | Parameter setup handlers |

### Pattern Stream Command Bytes

Commands $80–$93 are dispatched via a jump table at ~$93A8:

| Byte | Handler | Effect |
|------|---------|--------|
| $80 | L_93FB | (TBD — possibly pattern end/loop) |
| $81–$8F | various | Waveform/parameter commands |
| $90 | L_93xx | Arpeggio |
| $91 | StopMusic | Stop music |
| $92 | L_93xx | Noise waveform |
| $93 | L_93xx | Pulse + saw + triangle + ring-mod + sync variants |

Note: Bytes $00–$7F are note data; $80–$93 are commands; bytes $81–$8F at minimum control waveform.

### Data Tables

| Label | Purpose |
|-------|---------|
| ArpTable | Arpeggio interval lookup (intervals in semitones or freq deltas) |
| NoteFreqsL / NoteFreqsH | Note number → SID frequency register lo/hi |
| CommandTable | $80–$93 command → handler address jump table |
| SongTempo | Tempo value (may be a dynamic offset) |
| TempoCnt | Tempo countdown counter |

### Architecture Summary

- **3-voice playback.** Standard SID chip voices 1–3.
- **Pattern-based sequencing.** Each voice has an independent pattern stream pointer + a track/orderlist pointer. The track selects which pattern to play in sequence.
- **Duration counter.** `NOTC` counts down; `NOTD` holds the loaded duration. `pnotdone` handles the count-still-running case.
- **Arp tables.** Two pointers per voice (ARP/ARPH for primary, ARP2L/ARP2H for secondary). ArpTable is a shared global table indexed by these pointers.
- **Note frequency encoding.** Note numbers index into NoteFreqsL/H for SID register values.
- **ADSR per voice.** AD and SR stored in voice block ($13/$14), written to $D405–$D406 on note trigger.
- **Waveform.** WAVE ($22) holds the waveform bits without gate; CTRL ($23) has gate set. Written to $D404 on gate-on and gate-off transitions.
- **Pulse width.** PWL/PWH ($17/$18) stored per voice, written to $D402–$D403.
- **Module size.** 3328 bytes ($0D00) for Panther. This includes both the player code and the music data.

---

## Driver Version History (Timeline)

Based on VGMPF + c64.com interview + Wikipedia:

| Period | Version | Key characteristics |
|--------|---------|---------------------|
| ≤1984 | "Early/Lazy Jones" | Load $1480, 21 subtunes, 3328 bytes; 424 Hz tuning; uses SID filter |
| ~1985 | "Whittaker original" | Whittaker's own driver, hand-assembled via Supersoft assembler + machine code monitor + Yamaha CX5M/Roland Jupiter-6. Slow per programmer complaints. |
| 1986 (pre-June) | "Binary Design era" | Panther ($9000), Storm ($9000), Red Max ($E000) — multiple load addresses, consistent structure |
| June 1986 | "Jason Brooke rewrite" | Brooke rewrote CPC driver to be "shorter, faster, more flexible chords, envelopes, combining pitch bends with chords." First game: Glider Rider ZXS (late September 1986). |
| 1986–1987 | "Post-Brooke" | Brooke's version back-ported to C64. Whittaker used it without major updates until 1991. Filter usage dropped (except engine sound effects). |
| 1987 onward | "Stable format" | The two 1987 rippers (Jack the Ripper, Whittex) demonstrate the format was stable enough to identify and extract automatically. Whittaker+Brooke drivers "distinguishable from each other" — Brooke made independent iterative refinements. |

**Tuning note:** Whittaker's drivers tuned at 424 Hz. ZX Spectrum version "tuned at 390 Hz (two semitones too low)." This means the frequency tables differ between C64 and Spectrum versions.

**Filter:** Early versions use SID filter (6581, bias ≥ −300 for optimal sound). Later versions (post-1987) do not use filter except for engine sound effects.

---

## Cross-Platform Compatibility (from Bansai / Lemon64)

The Whittaker C64 and ZX Spectrum 128 players share the same data format. Bansai confirmed:
- Automatic conversion from ZX128 player → C64 player works
- Spectrum version is "missing commands here and there for the additional SID waveforms"
- All arpeggio tables are present in Spectrum data (identical structure)
- NES player was derived from the C64 player

**NES driver specifics (from VGMPF NES Driver page):**
- Song table: `<speed>, <v1 lo>, <v1 hi>, ... <vN lo>, <vN hi>` — 9 bytes per entry (4 voices on NES)
- Pattern end byte: $FF on NES (vs. $88 on C64, $87 on Spectrum)
- Vibrato/tremolo tables: final byte always has high bit set (identical structure to C64 soundparameter tables)
- Loop command forces repetition from new voice pointer (skips intro material)
- Termination command: immediate song end
- DPCM channel used only once (Krusty's Fun House title screen)
- "His player does all the heavy lifting for effects, not the PSG in the 2A03"

NES games using Whittaker driver: Loopz, Elite, Castelian, Krusty's Fun House, Spider-Man: Return of the Sinister Six, Alfred Chicken, Super Turrican, The Lion King.

Unreleased NES: 007: Licence to Kill, Ferrari Grand Prix, Populous, Tip-Off.

---

## Data Format Notes (synthesised from multiple sources)

### Pattern end marker
- C64: $88
- NES: $FF
- ZX Spectrum: $87

### Song/track table
- `<speed>, <v1 lo>, <v1 hi>, <v2 lo>, <v2 hi>, <v3 lo>, <v3 hi>` for 3 voices on C64 (7 bytes/subtune entry)
- NES has 4-voice variant

### Instrument data
Whittaker did not use a separate tracker — music data was macro-expanded in an assembler. The whole module file = player code + music data. There is NO separate instrument file; instruments are embedded as tables within the module.

"The music data are embedded into an assembler player, so the whole module file contains both the player and music." (NostalgicPlayer)
"His players can recognize all the different versions of David Whittaker's player and extract the data and play them back." (NostalgicPlayer — implies multiple detectable versions)

### Known distinct driver versions detected by NostalgicPlayer
NostalgicPlayer lists 20 songs in "David Whittaker" format, file sizes 18 KB – 194 KB.

---

## NostalgicPlayer Format Page

URL: https://nostalgicplayer.dk/modules/format/davidwhittaker/4
Content fetched: lists 20 David Whittaker format modules, 18–194 KB.
Key quote: "The music data are embedded into an assembler player, so the whole module file contains both the player and music. The player can recognize all the different versions of David Whittakers player and extract the data and play them back."
**No byte-level format spec on this page** — likely in a linked documentation sub-page not yet fetched.

---

## Amiga .dw Format (ExoticA)

URL: https://www.exotica.org.uk/wiki/David_Whittaker_(format)
The page was blocked by browser verification (Cloudflare) during this research session.

From search-result snippets:
- `.dw` files are "exotic" (non-tracker custom) Amiga format used in Amiga games
- EP_DWhittaker.lha = Amiga EaglePlayers player (v1.0, 6721 bytes) — plays .dw files under DeliTracker 2.32
- Download URL (ExoticA EaglePlayers): http://wt.exotica.org.uk/players.html (SSL error during fetch)
- Aminet likely hosts EP_DWhittaker.lha

---

## Leads to Follow

1. **dmx87 full Whittaker_David directory** — the GitHub repo `realdmx/c64_6581_sid_players/tree/main/Whittaker_David/` may contain more .asm files beyond Panther. Fetch the raw directory listing at https://api.github.com/repos/realdmx/c64_6581_sid_players/contents/Whittaker_David to get the full file list.

2. **Bansai's Xenon ZX128→C64 conversion** — CSDb release (search scener 38332 or title "Xenon ZX128"). Has download + full player source/song data for Xenon in C64 format. Very likely to include a second Whittaker .asm disassembly.

3. **Whittex additional versions on "Debyshire RAM" disks** — Max (Whittex author) said V1.0 is here and "other versions on the Debyshire RAM various release disks." Those later versions may expose more driver variants.

4. **David Whittaker Ripper .zip (CSDb 33379)** — download `http://csdb.dk/getinternalfile.php/22425/David Whittaker Ripper.zip` and inspect the ripping code to understand how it identifies/extracts Whittaker music from memory.

5. **NostalgicPlayer documentation sub-page** — the format page at /modules/format/davidwhittaker/4 mentions recognising "all the different versions." There may be a linked /documentation or /format-spec sub-page.

6. **ExoticA EP_DWhittaker.lha** — Amiga player source. Try Aminet: `http://aminet.net/search?query=DWhittaker+player` or `http://aminet.net/mus/play/EP_DWhittaker.lha`.

7. **HVSC STIL/BUGlist entries for Whittaker** — HVSC's STIL.txt + BUGlist.txt contain per-SID notes from rippers; may have driver-version annotations.

8. **Jason Brooke VGMPF page** — https://vgmpf.com/Wiki/index.php/Jason_Brooke — already partially fetched; the full gameography (Brooke-credited vs Whittaker-credited C64 games) would identify which tunes use the post-June-1986 "Brooke" driver variant.

9. **DeepSID player identifier** — DeepSID uses player identification logic; the "Bansai xenon C64 conversion" on DeepSID (linked from Lemon64 thread) would show which driver tag it receives.

10. **Panther.asm full raw text** — file is already at `pipelines/david_whittaker/docs/src/Whittaker_David_Panther.asm` in this repo. Read it in full to extract the complete ArpTable, NoteFreqsL/H, and CommandTable byte contents.
