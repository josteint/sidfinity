---
source_url: http://csdb.dk/getinternalfile.php/185033/Reflextracker_V1.1.zip (D64 extraction)
fetched_via: curl + python3 D64 reader
fetch_date: 2026-06-15
reliability: primary (direct binary analysis)
---

# Reflextracker V1.1 — Disk Contents and Format Analysis

## Disk Images Obtained

Two zips from CSDb, both containing two D64 (Commodore 1541 disk image) files:

- `Reflextracker V1.1 [Reflex + The Obsessed Maniacs] (side 1).d64` — main disk
- `Reflextracker V1.1 [Reflex + The Obsessed Maniacs] (side 2).d64` — sample library

Raw binaries saved to: `/home/jtr/sidfinity/tmp/reflextracker_research/`

---

## Side 1 — Main Disk Directory

```
   43  REFLEXTRACK.V1.1        PRG   (main editor, $0801 = C64 BASIC entry)
    9  RFXT PLAYER V1.1        PRG   (standalone SID player — SEE BELOW)
  112  BESCHREIBUNG            PRG   (documentation, 112 blocks)
    -  ----------------        DEL
    1  SDRV.UPRT 4BHI          PRG   (sampler driver: user port, 4-bit high)
    1  SDRV.UPRT 4BLO          PRG   (sampler driver: user port, 4-bit low)
    1  SDRV.UPRT 8BIT          PRG   (sampler driver: user port, 8-bit)
    1  SDRV.I/O1 4BHI          PRG   (sampler driver: I/O port 1, 4-bit high)
    1  SDRV.I/O1 4BLO          PRG   (sampler driver: I/O port 1, 4-bit low)
    1  SDRV.I/O1 8BIT          PRG   (sampler driver: I/O port 1, 8-bit)
    1  SDRV.I/O2 4BHI          PRG   (sampler driver: I/O port 2, 4-bit high)
    1  SDRV.I/O2 4BLO          PRG   (sampler driver: I/O port 2, 4-bit low)
    1  SDRV.I/O2 8BIT          PRG   (sampler driver: I/O port 2, 8-bit)
    1  SDRV.JOY1 2BHI          PRG   (sampler driver: joystick port 1, 2-bit high)
    1  SDRV.JOY1 4BIT          PRG   (sampler driver: joystick port 1, 4-bit)
    1  SDRV.JOY2 2BHI          PRG   (sampler driver: joystick port 2, 2-bit high)
    1  SDRV.JOY2 2BLO          PRG   (sampler driver: joystick port 2, 2-bit low)
    1  SDRV.JOY2 4BIT          PRG   (sampler driver: joystick port 2, 4-bit)
    1  SDRV.SIDWAVE            PRG   (SID waveform capture driver — special, see below)
    -  ----------------        DEL
    -  -BEISPIELSONGS!-        DEL   ("Example songs!")
  116  MOD.ACCESS2/B           PRG   (example song: Access Denied remix)
   40  MOD.ENDLOSCHOOR         PRG   (example song: Endloschoor)
  175  MOD.TRANCE202           PRG   (example song: Trance 202)
    -  ----------------        DEL
```

Note: The directory entry `^ START: $C006` in the version-1 zip (no block counts) is a comment entry, indicating the player starts at $C006. This aligns with HVSC init_addr for most Reflextracker SIDs ($C006 = 49158 decimal).

---

## Side 2 — Sample Library

A large collection of audio samples (all PRG files), each is a raw PCM sample stored as C64 memory:

```
ORGANIC BASS, SCHERBENKLIRREN, ONE !!, TWO !!, THREE!!, C-2 BASS, C-3 BASS,
DRUM1, SCRATCH, STRING OCT.HIGH, ACD.BASSWAVE, ACD.BASS, RFX. PR.T.Y.,
C64 DRUMM, PVCF /SAM/H, DRUMM MUELLTONNE, BOOTWAVE1, OL C3 VOICE,
BASS1 C2, PANFLOETE1 C2, CHOOR 2 C3, BOOTWAVE2, RAVE-BASS1, RAVE-DRUMM1,
NICHT NORMAL!, RAVE 3 LANG, RAVE4 LANG, SUPERDRUMMM, AUUUUHHHH!!!,
ALARM /SCHIFF, E-GITARRE, SCRATCH (2nd), SCRATCHHH!, FLESCH KORKEN, WUM.!!!,
HUST SCOTCH, WAAUUU!, SUPER HE.!!, HE.!!!, HAE.!!!, HEH!!!, OKAY!!,
ONE TWO, HIT IT!!!, PUMPKINS WAVE, PUMPKINS GITARRE, PUMPKINS SCHREI,
GOATHE !!!
```

Sample naming convention: `NAME OCTAVE` (e.g., `PANFLOETE1 C2` = pan flute sample, base note C2).

The sample disk contains rave/techno/hardcore-oriented sounds (Prodigy-era), bass samples, drums, scratches, and vocal snippets. These are the "PVCF/REF" samples referenced in the BESCHREIBUNG.

---

## RFXT PLAYER V1.1 — Binary Analysis

**File:** `rfxt_player_v1.1.prg` (extracted to `/home/jtr/sidfinity/tmp/reflextracker_research/rfxt_player_v1.1.prg`)

```
Load address:  $C000
Total size:    2050 bytes (2 load addr + 2048 code/data)
Code range:    $C000 – $C7FF (exactly 2048 bytes)
```

**First 32 bytes (after load addr):**
```
4C 2C C0  JMP $C02C         ; jump to init/play dispatch
4C 16 C0  JMP $C016         ; second jump (play routine entry?)
78        SEI
A9 36     LDA #$36          ; $01 = $36 (RAM + I/O, no BASIC)
85 01     STA $01
20 2C C0  JSR $C02C
8D 20 D0  STA $D020         ; border color
8D 11 D0  STA $D011         ; VIC control
D0 00     BNE $C020
...
```

The HVSC PSID header for standard Reflextracker SIDs:
- **init_addr = $C006** (= 49158 decimal) — the most common value (130 of 137 SIDs)
- **play_addr = $0000** — PAL VBI (the player installs its own IRQ)
- **load_addr** = varies per song (sample data + mod data loads at different addresses)

**Note from BESCHREIBUNG:** "AUF DISK SOLLTE EIN y BLOCK LANGER PLAYER SEIN" ("On disk there should be a Y-block-long player", where y ≈ 9 blocks = 2304 bytes max) — consistent with 9 blocks = 2048 bytes player size.

**Player start:** "DER START IST IN $C006 ODER SYS 49158" — confirmed in HVSC init addresses.

---

## SDRV.SIDWAVE — SID Waveform Capture Driver

A unique special driver listed in the documentation:
- Converts SID chip waveforms (triangle/sawtooth/pulse/noise) into PCM samples
- Parameters: WFORM+PULSE (waveform number 1-4, 12-bit pulse width for wave types 3-4), FREQUENCY (written directly to SID registers)
- The freq values mentioned in docs are: C0=$D411v, C1=$D422p, C2=$D4QtB, C3=$D4xBt, C4=$DqqvW, C5=$DrrCF, C6=$DtuyD, C7=$DxBsB (PETSCII hex notation — these are C64 SID freq registers)
- This driver bridges the PCM sampler into SID-synth territory

---

## Sample Drivers (SDRV.*)

15 sampler drivers for different hardware interfaces:
- **UPRT** = User Port (parallel) — 4-bit high nibble, 4-bit low nibble, 8-bit
- **I/O1, I/O2** = Expansion port cartridge samplers
- **JOY1, JOY2** = Joystick ports (2-bit or 4-bit)
- **SIDWAVE** = SID chip waveform → PCM (no external hardware needed)

Amiga transfer: SDRV.UPRT 8BIT used with a standard Amiga-to-C64 parallel cable; the Amiga (or Archimedes) saves the sample as a file named "(ARC: [filename])" and the driver receives it automatically.

---

## MOD File Format (Reflextracker module)

From the BESCHREIBUNG documentation and CSDb directory listing:
- Extension/prefix: `MOD.` (e.g., `MOD.TRANCE202`)
- Stored as PRG files on disk
- Contains: track table (voice 1 + voice 2 pattern indices), patterns (pattern data), and embedded sample references

The HVSC PSID files for Reflextracker tunes load the sample data + mod data into C64 RAM alongside the player. The SID file itself packages: player ($C000–$C7FF) + sample data + mod data.
