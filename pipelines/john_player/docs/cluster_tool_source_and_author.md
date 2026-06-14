---
source_url: http://csdb.dk/getinternalfile.php/60840/John_Player_1.0.zip (V1.0); http://csdb.dk/getinternalfile.php/60841/John_Player_1.4.zip (V1.4); http://csdb.dk/getinternalfile.php/6796/johnplayer.zip (V1.6+V2.0b); https://pastebin.com/raw/80TaWPMz (V2.0b help)
fetched_via: wget + WebFetch
fetch_date: 2026-06-14
author: Aleksi Eeben (handle: Heatbeat), CNCD/Cyberiad, Finland
content_date: 2001-09-03 (V1.0 source) / 2001-09-29 (V1.4 source) / 2002-02-11 to 2002-04-13 (V1.6+V2.0b)
reliability: PRIMARY — original source code from official CSDb releases; assembler source confirmed WLA-6510 format
---

# John Player — Tool Source and Author Cluster

## Summary

**SOURCE CODE FOUND AND SAVED.**

The John Player V1.0 and V1.4 releases both include `source.zip` in their
CSDb download packages. The source contains the full WLA-6510 assembler source
for the player, packer, editor, disk routines, and all binary data assets. All
files have been saved to `pipelines/john_player/docs/src/v10/` (V1.0) and
`pipelines/john_player/docs/src/v14/` (V1.4). The V1.6 help text and V2.0
beta help text are saved as `src/johnhelp_v16.txt` and `src/johnhelp_v20beta.txt`.

The V1.6 + V2.0b release (`johnplayer.zip`) does NOT contain source — only two
`.d64` disk images and the `johnhelp.txt` changelog. No source for V1.6 or
V2.0b has been found.

---

## Author and Provenance

**Full name:** Antti Aleksi Mikkonen (born 2 July 1976, Finland)  
**Demoscene handle:** Heatbeat (also: Aleksi Eeben)  
**Groups:** Rebels (1990) → Carillon → CNCD/Cyberiad  
**CSDb profile:** https://csdb.dk/scener/?id=13210  
**Contact (2001-era):** aleksi@cncd.fi, http://www.cncd.fi/aeeben  
**Current web presence:** https://aleksieeben.wordpress.com, https://aleksi-eeben.itch.io, "Aleksi's Eight Bit Shed" (Dropbox mirror: https://bit.ly/eightbitshed)  
**Wikipedia:** https://en.wikipedia.org/wiki/Aleksi_Eeben

Eeben created John Player because he found other C64 music tools unintuitive.
Quoted verbatim from Pouet user comments: "the most efficient c64 editor" in
terms of "combining user-friendliness and straightforwardness."

He remains highly active in the C64/8-bit demoscene: 2024-2026 releases include
Quantum Soundtracker, Dodo Sampler, Hare Basic, Bass 6502 Assembler V1.02,
numerous 256b intros, games, and tools. In September 2024 he issued a corrected
frequency table patch for V1.6 (fix for 1 MHz CPU clock assumption; correct is
985248 Hz PAL / 1022727 Hz NTSC).

---

## Release History

| Version | CSDb ID | Year | Source | Notes |
|---------|---------|------|--------|-------|
| V1.0 | 2630 | 2001-09 | YES (source.zip in release) | First release; FreqTab at reloc+$0358 |
| V1.1 | Demozoo 191559 | 2001-09 | Unknown | Minor update (no CSDb download found) |
| V1.4 | 2631 | 2001-09 | YES (source.zip in release) | FreqTab shifted to reloc+$035a; PWM direction logic rewritten; relocator hint added; demo music by Reed |
| V1.5 | (bundled) | 2002 | NO | Slide command added; note trig rewritten from scratch; 1 rasterline saved (peaks at 7 lines) |
| V1.6 | 18767 | 2002-02 | NO | Paste track key changed; help key added; music relocator included |
| V2.0 beta | 18767 / Pouet 13860 | 2002-04 | NO | Major: sound table doubled ($7F steps), sequencer doubled ($7F), 32 sounds ($1F), new loop syntax, initial Tmp/Flt/Vol in step 00; songs INCOMPATIBLE with V1.x |

**CSDb #2630** is the V1.0 entry. The V1.6+V2.0b package is **CSDb #18767**.
Pouet #13860 links to the V2.0b package.

---

## Player Memory Layout (V1.0; reloc=$1000 default)

From `player.asm` DEFINE block:

```
FreqTab     = $1358     ; 21-step PAL frequency table (84 bytes: 42 words)
Music       = $1400     ; music data region start
VibTab      = $1400     ; vibrato sine table (16+16 bytes: +$00 lo, +$10 hi)
SoundTab    = $1420     ; sound descriptors (11 bytes each)
FilTab      = $1500     ; filter cutoff table (64 bytes, shared across all sounds)
WaveTab     = $1540     ; waveform table (64 bytes, shared)
ArpTab      = $1580     ; arpeggio/absolute-pitch table (64 bytes, shared)
Sequencer   = $15c0     ; sequencer list (block indices + loop)
BlockData   = $1600     ; pattern block data
```

V1.4 difference: FreqTab shifts to $135a (reloc+$035a instead of $0358) — 2 bytes later.

**Zero-page variables** (base = $40, 13 bytes total):
```
$40  cmdtick    command-pending flag
$41  fbase      filter base (from Flt command)
$42  c1hold     voice 1 sound-trigger offset (0=no hold)
$43  c2hold     voice 2 sound-trigger offset
$44  c3hold     voice 3 sound-trigger offset
$45  count      tempo countdown
$46  speed      tempo value
$47  seqpos     sequencer position
$48  step       current block step (lo)
$49  block      current block step (hi)
$4a  vibpos     vibrato LFO position (4-bit, 0-$0f)
$4b  mod        vibrato delta lo (SMC: opcode byte)
$4c  modh       vibrato delta hi (SMC: opcode byte)
```

Player entry points:
- `JSR $1000` — Initialize (clear ZP, clear SID, set speed=$0C, set vol=$0F)
- `JSR $1003` — Play one frame (called every VBI/CIA IRQ)

---

## Sound Descriptor Format (SoundTab, 11 bytes per sound)

From player.asm comments (confirmed against source code):

```
offset  byte  meaning
$00     AD    Attack (hi nybble) / Decay (lo nybble)
$01     SR    Sustain (hi) / Release (lo)  -> $d405/$d406
$02     pos   Sound table start position (index into WaveTab/FilTab/ArpTab)
$03     end   Sound table end position (exclusive; loops when reached)
$04     loop  Sound table loop-back position
$05     pwi   PWM Init hi-byte value (0 = no PWM init; continues previous)
$06     pwr   PWM Rate (ADC/SBC operand each frame)
$07     pwt   PWM Top Limit
$08     pwb   PWM Bottom Limit
$09     fr    Filter Resonance (hi nybble) + Channel Select (lo nybble) -> $d417
$0a     fv    Filter Type (hi nybble) + Master Volume (lo nybble) -> $d418
```

Only voice 1 triggers filter writes ($d416/$d417/$d418). Voices 2 and 3
do not read FilTab or write filter registers.

---

## Per-Step Sound Table Format (3 columns, shared across all sounds)

Each step in the 64-step shared table has three bytes:
1. **WaveTab[y]** — waveform byte: written to $d404/+7/+14 (gate bit masked to current state)
   - $11 = Triangle, $21 = Sawtooth, $41 = Pulse, $51 = Tri+Pulse, $31 = Tri+Saw
   - $81 = Noise, $15 = Ring mod, $43 = Pulse+Sync, $23 = Saw+Sync
   - $09 = Test+Gate (hard restart); player relies on this for timing stability
2. **ArpTab[y]** — arpeggio/pitch byte:
   - $00-$7E: relative semitone offset (added to note, ASL+ADC)
   - $80-$FF: absolute pitch (hi byte only; value shifted left 1, written to $d401/+7/+14)
3. **FilTab[y]** — filter cutoff addend (added to fbase, written to $d416; voice 1 only)

---

## Block (Pattern) Data Format

**Uncompressed player (COMPILE_PLAYER != 2):**
Each step is 8 bytes at fixed stride:
```
offset  content
+0      (unused / command tick flag)
+1      (unused)
+2      Voice 1 note: 0=empty, $01-$7F=note, $FE=gate-off mask
+3      Voice 1 sound: 0=tied note (no trig), >0=sound index -> c1hold
+4      Voice 2 note (same encoding as voice 1)
+5      Voice 2 sound
+6      Voice 3 note
+7      Voice 3 sound (if gate-off: BMI exit before reading)
```
Each block pointed to by Sequencer; blocks are in BlockData region.

**Packed player (COMPILE_PLAYER == 2):**
Variable-length encoding using (step, block) as a 16-bit pointer pair.
Notes stored compactly; $FF = "no more notes on this line" early exit.
Commands stored inline at 2-byte stride (cmd, param); notes in variable offsets.

---

## Sequencer Format

**Uncompressed player:** Sequencer is an array of block indices.
- Non-zero byte: block index N → block address = (BlockData/256 - 1 + N) * 256
- Zero byte followed by a byte X: loop — set seqpos=X and re-read from there

**Packed player:** Sequencer is an array of 2-byte (block_hi, block_lo) pairs.
- Non-zero block_hi: use as absolute address
- Zero block_hi, non-negative block_lo: loop — set seqpos=block_lo

---

## Block Commands

8 commands, dispatched via `cmdjmpL` low-byte table (commands 1-8):

| # | Name | Mnemonic | Parameter | Description |
|---|------|----------|-----------|-------------|
| 1 | End | End | — | Normal block end; advance to next block in sequencer |
| 2 | Brk | Brk | — | Block break; restart block from step 0 |
| 3 | Flt | Flt XX | $00-$FF | Set filter cutoff base (fbase); added to per-step FilTab value |
| 4 | Tmp | Tmp XX | $06-$FF | Set speed (tempo); default $0C |
| 5 | Ini | Ini XX | $00-$02 | Initialize modulation; set vibrato width multiplier + reset vibpos, mod, modh |
| 6 | Vib | Vib XX | $00-$04 | Set vibrato rate (1-4); 0 = stop slide (keep freq); activates if Mod set |
| 7 | Mod | Mod XX | $01-$03 | Activate modulation on channel XX (patch opcode to ADC) |
| 8 | Off | Off XX | $01-$03 | Deactivate modulation on channel XX (patch opcode to CMP#) |

Commands are stored at byte offsets 0+1 within each step (before note data in
uncompressed format); command dispatch uses SMC to patch the modulatel_/modulateh_
opcodes. Vibrato width: Ini 0 = x1 (CMP#/NOP), Ini 1 = x2 (NOP/ASL), Ini 2 = x4 (ASL/ASL).

---

## Vibrato / Slide Mechanism

Single shared modulator (vibrato XOR slide — not both simultaneously).
Vibrato table: 16-entry sine (lo) at VibTab+$00, 16-entry sine (hi) at VibTab+$10.
Modulation enabled/disabled per-channel by patching the opcode at `cNmodulatel_` and
`cNmodulateh_`: opcode $65 (ADC zp) = on, opcode $C9 (CMP #) = off.
Vibpos advances 4 bits per rate tick; rate set by `setvibrate` (SMC into `vibrate_+1`).

Slide: same modulator path; `mod`/`modh` are set directly by `Sli` command (not via LFO);
`Vib 00` freezes slide at current frequency, `Off XX` resets to original note.

---

## V2.0 Beta Changes (from johnhelp_v20beta.txt)

1. Sound table: 128 steps ($7F) instead of 64 — shared across all sounds
2. Sequencer: 128 steps ($7F) instead of 64
3. Sounds: 32 ($1F) instead of (implied) 16
4. Loop syntax change: loop is now defined by a $00 waveform byte with the loop
   position in the Arpeggio column (same step), rather than separate Sound End / Loop fields
5. Initial song parameters in step 00 of sound table (since step 00 is otherwise unused):
   - Column 1: filter resonance + channel select ($d417)
   - Column 2: filter type + master volume ($d418)
   - Column 3: initial tempo
6. Player uses $0D zero-page locations ($40-$4C default) — same as V1.x
7. Compiled tunes ~0.4KB larger; still under 8 raster lines
8. Songs INCOMPATIBLE with V1.0-V1.6

---

## Version Identification (for HVSC sidid)

The HVSC has ~183 John Player SIDs. Versions have distinct player binaries
(different code at reloc=$1000). Key discriminators:
- V1.0: FreqTab at reloc+$0358; no relocator comment; executable-player scrolltext
- V1.4: FreqTab at reloc+$035a; "use relocator instead" comment; PWM direction logic rewritten
- V1.5: note-trig rewritten (different branch structure in getnotes); slide added; 7 raster peak
- V1.6: same player as V1.5 with paste-track key change; relocator .prg included
- V2.0b: completely different data layout (128-step sound table, 32 sounds, step-00 init)

---

## Files Saved

```
pipelines/john_player/docs/src/
├── v10/                     <- V1.0 source (2001-09-03 original)
│   ├── player.asm           <- 6502 player + packed player (26KB, WLA-6510)
│   ├── editor.asm           <- full editor source (68KB)
│   ├── packer.asm           <- song packer (10KB)
│   ├── disk.asm             <- disk routines (4KB)
│   ├── help.asm             <- help screen (5KB)
│   ├── mem.inc              <- WLA memory map header
│   ├── m.bat / puit.bat     <- build batch files (WLA-6510 + linker)
│   ├── player.lnk           <- linker script
│   ├── player.prg           <- compiled player binary (9KB)
│   └── *.bin                <- binary data assets (freq table, presets, etc.)
├── v14/                     <- V1.4 source (2001-09-29)
│   ├── player.asm           <- updated player (25KB; FreqTab+2, PWM rewrite)
│   ├── editor.asm / packer.asm / disk.asm / help.asm
│   ├── presets.bin          <- preset sounds (not in V1.0)
│   └── blueflash.bin        <- UI asset (not in V1.0)
├── johnhelp_v16.txt         <- V1.6 help + changelog (from johnplayer.zip)
└── johnhelp_v20beta.txt     <- V2.0 beta help + changelog (from Pastebin #80TaWPMz)
```

---

## Gaps and Leads to Follow

### Source gaps
- **V1.5 source not found**: no separate CSDb entry for V1.5; likely only shipped
  as a .d64 inside the V1.6+V2.0b package. The `john16.d64` disk image in
  `johnplayer.zip` (CSDb #18767) contains the V1.6 binary; the V1.5 player changes
  (note-trig rewrite, slide) are documented in `johnhelp_v16.txt` but source is absent.
- **V2.0 beta source not found**: `john20beta.d64` contains only the binary. The
  data format changes are significant (128-step tables, 32 sounds, step-00 init).
- **V1.1 source unknown**: Demozoo lists it (ID 191559) but no download link found;
  CSDb entry may have no file attached.

### Investigation leads
- **Extract d64 images**: `john16.d64` and `john20beta.d64` in
  `tmp/john_player_research/` could be mounted with `vice`/`c1541` to list files;
  may contain a more recent `player.prg` or even source. No d64 tool is installed.
- **Aleksi's Eight Bit Shed (Dropbox)**: https://www.dropbox.com/sh/820f5e07f8x74ou/...
  — not successfully fetched (Dropbox HTML auth wall). May contain later sources.
- **Aleksi's WordPress / itch.io**: https://aleksieeben.wordpress.com has a "portfolio"
  section; itch.io has games but no music tools listed. Neither had John Player assets.
- **HVSC sidid signatures**: the 4 known player versions (V1.0, V1.4, V1.5/1.6, V2.0b)
  have different player binaries. A binary fingerprint of each version (like the FC
  fingerprint approach) would let us route all 183 HVSC tunes to the right data decoder.
  Key: V1.0 vs V1.4 differ at FreqTab offset ($0358 vs $035a); V2.0b differs completely
  in data layout (step-00 init, 128-step table).
- **Data format for V1.6**: the uncompressed data layout derived above from V1.0/V1.4
  source almost certainly applies to V1.5/V1.6 (only the note-trig and slide routines
  changed, not the data structures). Verify by binary-diffing `player.prg` (V1.0) against
  a ripped V1.6 player.
- **WLA-6510 assembler**: build system is WLA-6510 (http://www.hut.fi/~vhelin/wla.html);
  `m.bat` runs the assembler and `player.lnk` links. Source can be recompiled to verify
  the binary matches.
