---
source_url: local: /home/jtr/sidfinity/tmp/reflextracker_research/ (D64 images from CSDb download 160214)
fetched_via: local read (D64 directory parsed with Python)
fetch_date: 2026-06-15
author: Reflex / The Obsessed Maniacs
content_date: 1995 (disk timestamps: 1996-03-29 original, 1998-12-07 ripped D64)
reliability: primary
---

# Reflextracker — D64 Disk Contents

## Downloaded archives

- `Reflextracker v1.1-Reflex-.zip` (CSDb file #160214, 286 downloads): contains two D64s labelled "MHD/<F>/M8" (a rip label)
- `Reflextracker_V1.1.zip` (CSDb file #185033, 82 downloads): contains two D64s labelled "REFLEXTRACKER" / "SAMPLES" (original labels)

## Side 1 — Tracker disk

Disk label: **"REFLEXTRACKER"** (ID: AA)  
All relevant files also extracted as standalone PRGs.

```
REFLEXTRACK.V1.1   PRG  (the tracker editor, BASIC load at $0801)
RFXT PLAYER V1.1   PRG  (standalone player, load at $C000, 2048 bytes)
BESCHREIBUNG       PRG  (German manual, 28 KB PETSCII)
```

Sample input drivers (for recording samples FROM hardware):
```
SDRV.UPRT 4BHI     4-bit high nibble, Userport
SDRV.UPRT 4BLO     4-bit low nibble, Userport
SDRV.UPRT 8BIT     8-bit, Userport
SDRV.UPRT AMIGA    Amiga parallel cable (sample transfer)
SDRV.I/O1 4BHI     4-bit high nibble, I/O port 1 (expansion)
SDRV.I/O1 4BLO     4-bit low nibble, I/O port 1
SDRV.I/O1 8BIT     8-bit, I/O port 1
SDRV.I/O2 4BHI     4-bit high nibble, I/O port 2
SDRV.I/O2 4BLO     4-bit low nibble, I/O port 2
SDRV.I/O2 8BIT     8-bit, I/O port 2
SDRV.JOY1 2BHI     2-bit high nibble, Joystick port 1
SDRV.JOY1 2BLO     2-bit low nibble, Joystick port 1
SDRV.JOY1 4BIT     4-bit, Joystick port 1
SDRV.JOY2 2BHI     2-bit high nibble, Joystick port 2
SDRV.JOY2 2BLO     2-bit low nibble, Joystick port 2
SDRV.JOY2 4BIT     4-bit, Joystick port 2
SDRV.SIDWAVE       SID chip waveform → sample converter
```

Example songs (the "Beispielsongs"):
```
MOD.ACCESS2/B      Access Denied (remix) — load=$4A1C, 29,414 bytes
MOD.ENDLOSCHOOR    Endlos Choor — load=$95FC, 9,990 bytes
MOD.TRANCE202      Trance 202 — load=$1009, 44,281 bytes
```

**IMPORTANT note on disk:** The directory in the ripped D64 includes a fake entry `"^ START: $C006"` — this is NOT a file but a DEL entry used as a label by the ripper to document the player start address.

## Side 2 — Samples disk

Disk label: **"SAMPLES"** (ID: BB)  
54 sample PRG files — raw sample data for use as instruments in the tracker.

```
ORGANIC BASS         C-2 BASS             DRUMM MUELLTONNE
SCHERBENKLIRREN      C-3 BASS             BOOTWAVE1
ONE !!               SUMBA-EH!            OL C3   VOICE
TWO !!               DRUM1                BASS1  C2
THREE!!              SCRATCH              PANFLOETE1 C2
ACD.BASSWAVE         STRING OCT.HIGH      CHOOR 2  C3
ACD.BASS             RFX. PR.T.Y.         ODYSSE CHOOR/H
C64 DRUMM            ROCK                 BOOTWAVE2
PVCF /SAM/H          RAVE-BASS1           RAVE-DRUMM1
NICHT NORMAL!        RAVE 3 LANG          RAVE4 LANG
SUPERDRUMMM          AU!-SCHREI           AUUUUHHHH!!!
ALARM /SCHIFF        E-GITARRE            SCRATCH (2nd)
SCRATCHHH!           FLESCH KORKEN        WUM.!!!
EFFECT/OUTRUN        HUST     SCOTCH      WAAUUU!
SUPER HE.!!          HE.!!!               HAE.!!!
HEH!!!               OKAY!!               WELCOME!MIESS
ONE TWO              HIT IT!!!            PUMPKINS WAVE
PUMPKINS GITARRE     PUMPKINS SCHREI      GOATHE !!!
```

Sample types visible: bass (organic, acid, C-2, C-3), drums (drum1, rave-drumm1, superdrummm), chords/strings (choor, panfloete, odysse choor), SFX (scherbenklirren=glass breaking, alarm, scratch, WUM=boom), vocals (he/hae/okay/one two/hit it — speech samples), Smashing Pumpkins samples.

All samples were collected and recorded by PVCF (documented in BESCHREIBUNG).

## MOD file magic

All three example MOD files begin with: `52 46 58 31` = **"RFX1"** (ASCII)

```
MOD.ACCESS2/B:  52 46 58 31 54 42 10 00  ("RFX1TB..")
MOD.TRANCE202:  52 46 58 31 87 77 77 77  ("RFX1" + sample data)
MOD.ENDLOSCHOOR:52 46 58 31 BB A8 66 79  ("RFX1" + sample data)
```

The 4-byte magic is followed immediately by song/sample data. No version byte or header length field is visible in the first 8 bytes.

## Extracted files location

`/home/jtr/sidfinity/tmp/reflextracker_research/`:
- `RFXT_PLAYER_V1.1_extracted.prg` — standalone player binary (2050 bytes incl. PRG header)
- `REFLEXTRACK_V1.1_extracted.prg` — tracker application (10,867 bytes)
- `BESCHREIBUNG_extracted.bin` — German documentation (28,301 bytes)
- `MOD_ACCESS2B_extracted.prg` — example song (29,414 bytes)
- `MOD_TRANCE202_extracted.prg` — example song (44,281 bytes)
- `MOD_ENDLOSCHOOR_extracted.prg` — example song (9,990 bytes)
- `Reflextracker V1.1 [Reflex + The Obsessed Maniacs] (side 1).d64`
- `Reflextracker V1.1 [Reflex + The Obsessed Maniacs] (side 2).d64`
