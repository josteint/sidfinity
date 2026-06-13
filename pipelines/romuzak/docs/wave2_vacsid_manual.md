---
source_url: http://csdb.dk/getinternalfile.php/36832/vacsid.zip
fetched_via: curl (downloaded to tmp/romuzak_research/vacsid.zip, then unzip -l + unzip -p)
fetch_date: 2026-06-14
author: Oliver Blasnik (ROM / Vacuum)
content_date: 1996-03-31 (VacSID Mekka '96 Pre-Release)
reliability: primary
---

# VacSID Mekka Pre-Release — Zip Contents and ROMUZAK.DOC Discovery

## Zip file inventory

Downloaded: `http://csdb.dk/getinternalfile.php/36832/vacsid.zip`
Local: `tmp/romuzak_research/vacsid.zip` (416 KB)

```
   9619  1996-03-31 13:14   VACSID.DOC        ← VacSID player doc (Mekka build)
   3040  1996-03-31 13:14   VACUUM.NFO        ← Group NFO (extracted to docs/src/)
    851  1996-03-31 13:14   FILE_ID.DIZ       ← BBS summary
 120853  1996-03-31 13:14   RTM.EXE           ← DOS runtime (binary, not RE'd)
  15481  1996-03-31 13:14   VACSETUP.EXE      ← Setup (binary)
 186112  1996-03-31 13:14   VACSID.EXE        ← Main player (binary, C64 emulator)
 308278  1996-03-31 13:14   VACSID.IDX        ← Resource index (binary)
  58376  1996-03-31 13:14   DPMI16BI.OVL      ← DPMI overlay (DOS protected mode)
     23  1996-03-31 13:14   VACSID.RES        ← Resource file (binary)
  29906  1996-03-31 13:14   ROMUZAK.DOC  ***  ← RoMuzak editor manual (TEXT — KEY FIND)
      3  1996-06-07 18:36   VACSID.CFG        ← Config (3 bytes, stub)
```

**KEY FINDING: ROMUZAK.DOC** — a 29,906-byte text file, the COMPLETE RoMuzak
editor manual in German. This is the primary technical documentation for the
RoMuzak format. It was NOT previously known to exist as a text file inside
this zip. Saved to: `pipelines/romuzak/docs/src/romuzak_doc_vacsid_bundle.txt`

---

## VACSID.DOC (this zip vs. wave1 V1.59 version)

The VACSID.DOC in this zip is the **Mekka '96 pre-release** (V0.88), NOT
the V1.59 doc already saved from vsid159.zip. Key differences:

### This zip (Mekka pre-release VACSID.DOC):
- Explicitly lists: **"C64 RoMuzak Music Composer Software V7.96"** as a
  feature in the SOFTWARE FEATURES section
- States: "To exit from the included, free c64-sound-editor RoMuzak, choose
  RESET and OK to go back to VacSid."
- Has more direct description of RoMuzak integration

### V1.59 VACSID.DOC (from vsid159.zip, already in docs/src/):
- Does NOT list RoMuzak in the software features section
- Focuses on V1.59 features (Pseudo-Stereo, Compressor/Limiter, Playlists, etc.)
- RoMuzak may have been removed from the feature list by V1.59

Both docs are now saved. The Mekka build (this zip) is the version that
shipped with RoMuzak V7.96 bundled.

---

## ROMUZAK.DOC — Content Summary (full text in docs/src/)

The manual covers two versions: **RoMuzak V6.2** (main body) and
**RoMuzak V7.9x** (addendum: "Erlaeuterungen zum neuen RoMuzak V7.94 im
Vergleich zur alten V6.3").

### Confirmed: RoMuzak is the editor; this zip IS the editor

The VACSID.DOC confirms: "C64 RoMuzak Music Composer Software V7.96 emulation
with emulated 1541 File-System." The ROMUZAK.DOC is the documentation for
this bundled editor. VacSID ran the actual C64 RoMuzak V7.96 binary inside
its 6510 emulator, with emulated 1541 disk I/O for loading/saving songs.

### Authorship and copyright

```
ROMUZAK Version 6.2
ROMED   Version 2.0
(c)opyright by Lazer Cybernetics / Digital Marketing
(w)ritten   by Oliver Blasnik '89
(p)roduced  by Digital Marketing
```

The companion tool is "ROMED Version 2.0" (likely a ZeroPage/Memory Mover
utility bundled with later RoMuzak versions).

### Key format facts from ROMUZAK.DOC (all verbatim)

#### Player entry points (V6.2, default load at $8000)

```
LDA #nr        ; subtune number (0-7)
JSR $8000      ; init
               ; play via IRQ: JSR $8003
LDA #FF
JSR $8000      ; stop
```

- **Init:** `JSR $8000`, A = tune number (0-7)
- **Play:** `JSR $8003` (called every raster IRQ)
- **Stop:** `LDA #$FF : JSR $8000`
- **Play entry is init+3** (not +6 like FC; not +0 like some drivers)

This is a critical difference from FC (which uses +6).

#### Zero-page usage

```
Benutzt sind $f8-$fb.
```

Only 4 zero-page bytes used: `$F8, $F9, $FA, $FB`. ZEROPAGE MOVER can
relocate these to any $02-$FC range (avoiding $02-$05 and $50-$57 for
stability while in-editor).

#### Memory layout

- Default load address inferred as $8000 (from BASIC SYS32768 = $8000)
- `POKE56,128:CLR:SYS32774` = init at $8006? Or sets BASIC top-of-memory
  to $8000 ($8000/256=128 → POKE56,128) then calls $8006
- MEMORY MOVER: can relocate to $0400-$F000
- "Die Normallaenge schwankt zwischen 12 und 15 Bloecken" — normal music
  file size: 12-15 disk blocks = approx. 3-4 KB

#### Song structure

- **8 tunes (melodies) per music file**, global sector pool
- **3 tracks** (one per SID voice), shared across all 8 tunes
- **$40 (64) sectors** maximum
- Track window: 21 rows × 12 bytes = 252 bytes per display window
- Sound table terminated by "8 mal ff" ($FF × 8)

#### Track byte encoding (VERBATIM from doc)

```
$00-$3F  Sektor spielen (play sector N)
$40-$7F  Sektor wiederholen: next byte gives sector; played $40-xx+1 times
$80-$BF  Noten Transpose: following notes transposed up by $80-xx semitones
$C0-$FB  Sound Transpose: following sound numbers offset by $C0-xx
$FC xx   Goto: jump to byte xx in this track, continue from there
$FD      Restart ALL (alle neu starten)
$FE      Stop entire piece
$FF      Restart THIS track
```

Example (verbatim):
```
00: 80 c0 43 01 02 8c 43 01 02 ff
```
= reset both transposes ($80/$C0 = delta 0), play sector $01 four times
($43 = $40+3 → 4 repeats), play sector $02 once, set note-transpose to
12 semitones ($8C = $80+12), play $01 and $02 again, restart.

#### Sector (pattern) command set V6.2

| Command | Binary encoding | Notes |
|---------|-----------------|-------|
| Note c-0..b-7 | pitch byte | 8 octaves, C to B |
| DUR.xx | duration | 01-$20 |
| SND.xx | sound select | 00-$1F (32 instruments) |
| GLD.XYZ | glide | X=direction, Y=delay (0-7 in DUR/2 units), Z=speed (0-f) |
| APM.xx | autoportamento | 00=off, $1F=max; auto-calculates glide to target |
| CONT | continue/tie | extend previous note |
| PSE.xx | pause | 01-$20 |

Note: binary byte values for sector commands are NOT given in the doc.
Only the human-readable mnemonics are described. The actual byte encoding
requires RE of the sector-parse loop. OPEN.

#### Instrument (Sound) definition V6.2 — 8 bytes (B0..B7)

See `wave2_fc_inheritance.md` for full mapping. Summary:

| Byte | Field | Description |
|------|-------|-------------|
| B0 | PW lo×16 + hi / SEEK value | Pulse width or seek start |
| B1 | Waveform ($D404) | SID control register |
| B2 | Attack/Decay ($D405) | SID ADSR hi |
| B3 | Sustain/Release ($D406) | SID ADSR lo |
| B4 | Drum-type / Echo-value / SoundChange param | Multiplex per B7 flags |
| B5 | Freq vibrato (FC-mode or normal, selected by B7 bit3) | Pitch vibrato |
| B6 | PW-vibrato strength/speed OR CH80 freq OR FreqDrum freq | Multiplex per B7 |
| B7 | Effect control byte (8 bits) | Master effect selector |

**B7 flags (verbatim translation):**

| Bit | Hex | Effect |
|-----|-----|--------|
| 0 | $01 | Drum: plays drum 0-7 (in B4); +bit3 = fixed freq from B6; +bit6 = echo-drum |
| 1 | $02 | Arpeggio: pitch from next sound-table entries; $FF resets to first arp byte |
| 2 | $04 | Echo: cycles between two notes; speed = hi nibble B4, interval = lo nibble B4 |
| 3 | $08 | B5 vibrato mode: 0=FC-style (bits 6-3 speed, 2-0 depth), 1=Normal (hi=strength, lo=speed) |
| 4 | $10 | SEEK: PW sweeps from $0000 upward by B0 each DUR |
| 5 | $20 | Filter enable for this voice (global filter freq+add from SET FILTER menu) |
| 6 | $40 | After 2 DUR, waveform switches to $40 (rectangle) |
| 7 | $80 | First DUR plays waveform as noise with high freq |
| 6+7 | $C0 | Alternate waveform every half-DUR between B1 and CH80 noise (freq in B6) |
| 3+4 | $0C | SoundChange: after B4-hi DUR's, switch to sound B4-lo |

#### Converters (V6.2)

Three converters in EXTRAS/CONVERTER menu:
1. **CVN Soundmon**: Soundmonitor → RoMuzak. No arpeggio, no sound convert
   (Soundmonitor uses 24-byte instruments; RoMuzak uses 8 bytes).
2. **CVN Future Composer**: FC "0.18" → RoMuzak.
   - Tracks: 100% (byte-for-byte reinterpretation of track stream)
   - Sectors: 100%
   - Sounds: 90% (arpeggios converted to Echo effects; pulse-vibrato needs
     retuning; drums may need re-editing)
3. **CVN RoMuzak**: old RoMuzak (≥V3.2) → current V6.2 format.
   - Tracks: 100%, Sectors: 100%, Sounds: 95% (drums + arpeggios need editing)

---

## V7.9x addendum — new features beyond V6.3

The second half of ROMUZAK.DOC documents V7.94/V7.96 additions:

### New sector commands (XSCS — 21 new commands)

| Command | Description |
|---------|-------------|
| VDL.xx | VIBRATODELAY — delay vibrato start by xx cycles |
| ARP.xx | ARPEGGIO SELECT — xx<$20: pointer to arp row in sound table; xx>$1F: direct arp value (ARP.$37 → $00/$03/$07) |
| REL.xx | RELEASE — initiate release after xx cycles |
| ARL.xx | AUTORELEASE — not yet implemented in V7.96 |
| PNT.xx | PULLNOTES — like APM but explicit start+end notes (2 note bytes follow); speed $00-$1F |
| ECH.xx | ECHO — increase sustain by xx on each note (fast notes → echo effect; credited to M. Schneider / X-Ample Architectures) |
| ASS.xx | ARPEGGIOSPEED SELECT |
| HGD.xx | HIGLIDE — continuously increment freq hi-byte by xx; HGD.$00 to stop |
| PSW.xy | PULSESWEEP — glide pulse to x at speed y |
| FDR.xx | FADER — fade in (bit7=0) or out (bit7=1); speed in bits 0-6 |
| VOL.xy | VOLUME — set volume y + filter x (→ $D418) |
| FST.xx | FILTERSTART — set filter FX start value |
| FAD.xx | FILTERADD — set filter FX add value |
| FSW.xx | FILTERSWEEP — sweep filter from FST to xx at speed FAD; holds D416 non-zero while active |
| LCY.xx | LOOPCYCLES — if filter FX active: bit7=direction (0=down, 1=up); low bits = # direction changes |
| SPD.xx | SPEED — set music speed |
| RES.xx | RESET — reset all special-command parameters |
| :xx | LOOPSTART — begin repeat block (xx = count) |
| . | LOOPEND — end repeat block (ISR) |
| GOTOxx | GOTO SECTOR — jump to byte 00 of sector xx (ISG) |
| ->text | REMARK — comment in sector (IRS) |

### New V7.94+ instrument flags (sound editor)

| Code | Description |
|------|-------------|
| FX06 | 1-Line-Arpeggio: DX field holds the arpeggio |
| FX02 | DX holds arpeggio speed |
| FX41 / FX49 | Hi-nibble of DX = echo value; if 0 or > drum-byte count, drum plays once only |
| DRUM | Hi-nibble of PL can specify a sound number; if 1-F, that sound plays after the drum |

### New V7.94+ sector commands (SRV, OCT)

| Command | Description |
|---------|-------------|
| SRV.xx | Set sustain+release of current sound; SRV.$00 = use value from sound table. Enables echo/fade effects. |
| OCT.xy | Set note start offset: y=1-7 → note+y; y=9-F → note+8-y. X=0-7: switch after x DURs directly; X=8-F: glide at speed 8=slow, F=fast |

### Extended drum editor (XDSE) — drums 8-$F

Each drum consists of **2 rows × 16 bytes**:
- Row 1: waveform bytes (positions 0-$0F); $FF = drum end
- Row 2: frequency bytes (positions 0-$0F)
A drum plays from byte 00 through byte $0F (or until $FF).

### SIMPLEX mode

Voices can be played individually. High nibble of tune-number at init
= simplex value (bitmask of which voices to mute).

### V7.94 bug fixes

- Fixed: player re-init via $8003 sometimes ran incorrectly (V6.3 bug)
- LIVEPLAY in progress (not complete in V7.96)
- OUT OF MEMORY instead of crash on file save
- SID reset added to music init

---

## VACUUM.NFO — Group context

Saved to: `pipelines/romuzak/docs/src/vacuum_nfo_mekka_prerelease.txt`

Confirms Vacuum group membership as of March 1996:
- Scamp (founder, coder), R0M / ROM / Oliver Blasnik (coder, sysop WHQ
  TRIPLeBUG), SplatterSquad (gfx), Galactor, Cannibal (music), Matrix
  (coder), EduART (music), Portable Stoevchen (music)
- R0M is the author of both VacSID and RoMuzak

Contact at time of release:
- eMail: account DOWN (new soon)
- FidoNet: Simon Kissel (2:2455/61)
- Phone: +49-6721-14955

---

## Leads to follow

1. **Sector command binary encoding** — the ROMUZAK.DOC gives mnemonics
   only. The actual byte values for DUR/SND/GLD/APM/CONT/PSE etc. are
   unknown without RE. OPEN: disassemble the sector-parse dispatch loop.
   This is the single highest-value RE target for the extractor.

2. **Saved music file binary layout** — the doc describes the UI but not
   the file format. OPEN: save a test song from the editor (in VICE using
   the d64 from archive.org), extract the PRG, and map byte ranges against
   the doc's structure description. This is gather work (no disassembly needed
   for the outer layout).

3. **ROMED Version 2.0** — a companion tool mentioned in the header. Its
   function is unclear (ZP+Memory Mover?). The d64 disk images on archive.org
   may contain it. OPEN: check d64 directory for a file named ROMED or similar.

4. **V7.9x sector command byte values** — the 21 XSCS commands (VDL, ARP,
   REL, PNT, ECH, ASS, HGD, PSW, FDR, VOL, FST, FAD, FSW, LCY, SPD, RES,
   :xx, ., GOTOxx, ->) are now semantically documented. Their byte opcodes
   need RE. The LOOPSTART/LOOPEND (:xx / .) and GOTO syntax is particularly
   important as it creates structured repetition within sectors.

5. **d64 disk images (archive.org)** — two ACT 501 release disks are
   preserved. Screenshots of the Analyser disk show 9 UI screens. The .d64
   files themselves contain the actual editor + song binaries. Mounting with
   `c1541 -attach file.d64 -list` (no emulator) gives the directory.
   Candidates to extract: the music file binary (test any saved song),
   ROMED tool, any text/doc files on disk.
   URL: https://archive.org/details/d64_Romuzak_Music_Demo-Editor_1989_ACT_501

6. **Track window size vs. stored size** — "21 rows × 12 bytes = 252 bytes"
   is a UI display parameter. Whether tracks are stored as 252-byte fixed
   blocks or variable-length streams affects the file format. OPEN: extract
   a saved song and check if track data is padded to 252-byte boundaries.
