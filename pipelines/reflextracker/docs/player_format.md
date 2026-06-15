---
source_url: local: /home/jtr/sidfinity/tmp/reflextracker_research/Reflextracker V1.1 [Reflex + The Obsessed Maniacs] (side 1).d64
fetched_via: local read (D64 image extracted from CSDb download)
fetch_date: 2026-06-15
author: kb (Zorc/Quiss code), PVCF (docs/music)
content_date: 1995
reliability: primary (original disk image)
---

# Reflextracker — Player & MOD File Format

## Disk layout (Side 1 — REFLEXTRACKER disk)

```
REFLEXTRACK.V1.1     PRG  ~10.8 KB   The tracker application ($0801 load)
RFXT PLAYER V1.1     PRG    2.0 KB   Standalone player ($C000 load, 2048 bytes)
BESCHREIBUNG         PRG   28.3 KB   German documentation (PETSCII text, BASIC stub)
SDRV.UPRT 4BHI       PRG             Sample driver: Userport 4-bit high-nibble
SDRV.UPRT 4BLO       PRG             Sample driver: Userport 4-bit low-nibble
SDRV.UPRT 8BIT       PRG             Sample driver: Userport 8-bit
SDRV.UPRT AMIGA      PRG             Sample driver: Amiga parallel transfer
SDRV.I/O1 4BHI       PRG             Sample driver: I/O port 1 4-bit high
SDRV.I/O1 4BLO       PRG             Sample driver: I/O port 1 4-bit low
SDRV.I/O1 8BIT       PRG             Sample driver: I/O port 1 8-bit
SDRV.I/O2 4BHI       PRG             Sample driver: I/O port 2 4-bit high
SDRV.I/O2 4BLO       PRG             Sample driver: I/O port 2 4-bit low
SDRV.I/O2 8BIT       PRG             Sample driver: I/O port 2 8-bit
SDRV.JOY1 2BHI       PRG             Sample driver: Joystick port 1 2-bit high
SDRV.JOY1 2BLO       PRG             Sample driver: Joystick port 1 2-bit low
SDRV.JOY1 4BIT       PRG             Sample driver: Joystick port 1 4-bit
SDRV.JOY2 2BHI       PRG             Sample driver: Joystick port 2 2-bit high
SDRV.JOY2 2BLO       PRG             Sample driver: Joystick port 2 2-bit low
SDRV.JOY2 4BIT       PRG             Sample driver: Joystick port 2 4-bit
SDRV.SIDWAVE         PRG             Sample driver: SID waveform capture
MOD.ACCESS2/B        PRG   29.4 KB   Example song: Access Denied (remix), load=$4A1C
MOD.ENDLOSCHOOR      PRG    9.9 KB   Example song: Endloschoor, load=$95FC
MOD.TRANCE202        PRG   44.2 KB   Example song: Trance 202, load=$1009
```

Side 2 (SAMPLES disk) contains 54 raw sample files used as instruments.

## The standalone player (RFXT PLAYER V1.1)

- **Load address:** $C000
- **Size:** 2048 bytes exactly ($800)
- **Init entry (standard):** $C006
- **Play entry:** $0000 (player installs its own CIA2 IRQ)

The player occupies $C000–$C7FF. The song MOD file is loaded separately into a non-overlapping region. The documentation says: "DER PLAYER AUF DISK SOLLTE EIN 8 BLOCK LANGER PLAYER SEIN" (the player on disk should be 8 blocks = 2048 bytes) and "DER START IST IN $C006 ODER SYS 49158."

### Init routine structure ($C006)

From the binary (DERIVED — not full disassembly):

```
$C000: 4C 2C C0     JMP $C02C        ; entry 0: jump to play step?
$C003: 4C 16 C0     JMP $C016        ; entry 1: jump to init
$C006: (init entry point)
$C016: 78           SEI              ; disable interrupts
$C019: A9 36        LDA #$36         ; $36 = basic off, kernal on, char ROM in
$C01B: 85 01        STA $01          ; set C64 banking
$C01D: 20 2C C0     JSR $C02C        ; call some setup?
$C020: 8D 20 D0     STA $D020        ; border color
$C023: 8D 11 D0     STA $D011        ; VIC control
...
$C033: A9 00        LDA #$00
$C035: A2 18        LDX #$18
$C037: 9D 00 D4     STA $D400,X      ; clear all SID registers
$C03A: CA           DEX
$C03B: 10 FA        BPL loop
$C03D: A2 7F        LDX #$7F
$C03F: 8E 0D DD     STX $DD0D        ; CIA2 ICR: mask all interrupts
$C042: A2 93        LDX #$93         ; CIA2 timer A low byte ($93)
$C044: 8E 04 DD     STX $DD04        ; write timer low
$C047: 8D 05 DD     STA $DD05        ; timer high = $00 (from A=0 after LDA #0? DERIVED)
$C04A: A2 FF        LDX #$FF
$C04C: 8E 02 D4     STX $D402        ; voice 1 PW low = $FF
$C04F: 8E 03 D4     STX $D403        ; voice 1 PW high = $FF
$C052: 8E 06 D4     STX $D406        ; voice 2 PW low = $FF
$C055: A2 41        LDX #$41         ; gate on + noise waveform
$C057: 8E 04 D4     STX $D404        ; voice 1 control
$C05A: 8E 0E DD     STX $DD0E        ; CIA2 timer A: start + continuous
$C05D: 60           RTS
```

CIA2 timer A value = $0093 = 147 decimal. PAL clock = 985248 Hz. IRQ rate = 985248 / 147 ≈ **6,702 Hz**. This is the digi sample playback rate. (This is DERIVED from the binary bytes — needs verification.)

## MOD file format (RFX1)

All three example songs begin with the magic bytes `52 46 58 31` = **"RFX1"**.

```
Offset  Size  Description
$0000   4     Magic: "RFX1"
$0004   ...   Song data (packed sample data + track table + pattern data)
```

The detailed internal structure is NOT YET DECODED from these files. The song data contains:
- Packed 4-bit sample data (the dominant bulk of the file)
- Track table (orderlist for voices 1 and 2)
- Pattern data (note/speed/volume/direction grid)

The documentation describes the internal structure (translated from German):

### Track table

Two-voice orderlist. Each entry = pattern number or special command:
- `--` = this voice is silent (other voice continues until its pattern ends)
- `RP` = Repeat: jump back to position 00 (loop point)
- `ED` = End: stop player

Special constraint: both voices must NEVER both have `--` simultaneously — the player finds the pattern number to read the speed. If neither voice has a pattern number, the player may crash.

Pattern numbers are hex (0–$FF, so up to 256 patterns).

### Pattern structure

Each pattern is 16 rows long (hex $10). Each row has entries for **Voice 1** and **Voice 2**:

| Field | Bits | Description |
|-------|------|-------------|
| SND | note | Note to play (e.g., C-3). `--` = rest, `=` = stop sample |
| IS | 8-bit | Instrument (sample) number. `--` = continue previous sample at new pitch (switch effect) |
| D | 1 bit | Direction: `0` = forward, `1` = reverse |
| S | hex 0–F | Speed: 0=slowest, F=fastest. Recommended value = 7 for standard 4/4 at 16-row patterns |
| V | 2 bits | Volume: 0–3 (4 levels: 0=max, 3=min) |

Voice 1 has **priority** over Voice 2 for the play speed.

### Instruments / samples

Each sample has:
- Name (up to ~16 chars)
- Start address (RAM address of sample data)
- End address (RAM address + length)
- Sample data = signed 8-bit PCM or 4-bit nibble-packed (depending on driver)

Up to at least 16 sample slots (instrument numbers 0–$F mentioned; hex "0A" = 10th instrument).

### Speed (S field)

S=7 = normal 4/4 time at 16-row pattern length. The CIA timer rate is fixed; S controls how many CIA IRQs fire per pattern row advance. S=F is fastest, S=0 is slowest.

### Volume (V field)

Four levels only (0, 1, 2, 3 → 4 volumes). Written to the SID master volume register $D418 as 4-bit DAC for digi output.

## Sample drivers (SDRV.*)

The tracker can sample from hardware input (for composition). Drivers correspond to sampling hardware connected to different C64 ports:
- Userport (UPRT): 4-bit high nibble, 4-bit low nibble, 8-bit
- Expansion port I/O 1 and I/O 2: 4-bit and 8-bit
- Joystick ports 1 and 2: 2-bit and 4-bit
- SDRV.SIDWAVE: samples SID chip waveforms (triangle, sawtooth, pulse, noise) into RAM

## Playback mechanism (derived)

The player installs a CIA2 timer A interrupt at ~6702 Hz. On each interrupt:
1. Read next nibble from Voice 1 sample data (pointer at $D0/$D1)
2. Read next nibble from Voice 2 sample data (pointer at $D2/$D3)
3. Mix both nibbles (sum, clip to 4 bits)
4. Write to $D418 (SID master volume = 4-bit DAC)
5. Advance row counter; when row completes, read next note from pattern
6. On pattern end, advance track table position; on RP, loop

The SID's 3 synthesis voices are NOT used by the Reflextracker player for synthesis — all audio comes from $D418 DAC writes. Two digi channels are mixed in software.

The documentation mentions "faked third voice (drum and snare which are rendered in the bassvoice)" in PVCF's STIL comment — this is a software trick within the 2-channel digi mixer, not a third hardware DAC voice.

## Memory map (standard $C006 build)

```
$C000–$C7FF   Player code (2048 bytes = 8 disk blocks)
$C800+        (varies) — possibly player variables or end of song data
$????–$????   Song track table + pattern data
$????–$????   Sample data (4-bit packed or 8-bit raw)
```

The actual layout of song+sample data depends on how the .sid was packed. In HVSC SIDs, the entire binary (player + song + samples) is concatenated into one .sid data block. The PSID load_addr=0 means the PSID wrapper determines where data goes (sidplayfp loads data at the address encoded in the PRG header).

Most HVSC members load at $0000 with init at $C006 — sidplayfp reads the 16-bit load address from the first two bytes of PSID data, places code there, then calls init at $C006.

## Key documentation quotes (from BESCHREIBUNG, translated)

> "Der Reflex-Tracker ist ein Musikprogramm welches mit einer zweistimmigen Diggispur arbeitet."
> ("The Reflex-Tracker is a music program that works with a two-voice digi track.")

> "Der Editor ist mit für den C64 sehr grossem Comfort ausgestattet und erlaubt es binnen extrem kurzer Einarbeitungszeit qualitativ gute Lieder selbst für einen Anfänger herzustellen."
> ("The editor is equipped with very great comfort for the C64 and allows even a beginner to create qualitatively good songs within an extremely short learning time.")

> PVCF's STIL note on Access Denied (intro): "a 2 channel sampletracker. [...] Later in version v1.1 of Reflex-Tracker the user could do this [bass-drum split] without directly in the tracker."

> PVCF's STIL note on Access Denied (remix): "2 channels of digi-sounds, faked third voice (drum and snare which are rendered in the bassvoice), volume, echoeffects and flanger."

## Credits (from BESCHREIBUNG)

```
EDITORCODE:         ZORC/REFLEX
EDITORDESIGN:       PVCF/REFLEX  
DISK UND OPTIMIZESYSTEM: KB/TOM
CODE UND SAMPLEMENUDESIGN: KB/TOM
BESCHREIBUNG:       PVCF
BEISPIELLIEDER:     PVCF
SAMPLE-PACK CODE:   QUISS/REFLEX
SAMPLES:            PVCF/REFLEX
```

Matthias Kramm (Quiss) handled the **sample pack/compression code**. Zorc wrote the **editor code**. KB (Tammo Hinrichs) did the **disk system, optimization, and sample menu**. PVCF wrote the **documentation, example songs, and sampled all the instruments**.

Contact address in docs: Matthias Kramm, Moewestr. [?], [?] München, Germany.
