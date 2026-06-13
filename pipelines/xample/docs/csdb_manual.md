# X-Ample Architectures Sound Player — Technical Documentation

<!-- provenance:
  source_url: D64 disk images from CSDb:
    https://csdb.dk/getinternalfile.php/121250/Comptech_2.1.d64
    https://csdb.dk/getinternalfile.php/129662/Compotech-X-Ample.d64
  fetched_via: direct download, D64 parsed in Python
  fetch_date: 2026-06-13
  author: Markus Schneider, Helge Kozielek (original player source annotation)
  content_date: 1992 (player version 3.2), 1995 (V2.1 release)
  reliability: HIGH — extracted verbatim from original annotated TurboAss source in D64
  translation: German → English by Claude (research assistant), 2026-06-13
-->

## Overview

This file documents the X-Ample Architectures Sound Player as recoverable from the original
annotated TurboAss 6502 source embedded in the `.player-routine` SEQ file in `Comptech_2.1.d64`
and the `compotech   /xap` SEQ file in `Compotech-X-Ample.d64`.

The `.player-routine` file (16,475 bytes) is a TurboAss assembly source file with embedded
documentation strings delimited by `$80` bytes in PETSCII. It is the **verbatim annotated
player source code** distributed with Compotech V2.1 so that game developers could integrate
the player into their own products.

The header of the player reads (verbatim German, then translation):

```
X-AMPLE ARCHITECTURES SOUND PLAYER
VERSION 3.2
MUSIKROUTINE + SFX-ROUTINE
PROGRAMMIERT VON:
MARKUS SCHNEIDER
HELGE KOZIELEK &
ORGINAL TURBOASS-FILE/DOKUMENTIERT
```

Translation: "X-AMPLE ARCHITECTURES SOUND PLAYER / VERSION 3.2 / MUSIC ROUTINE + SFX-ROUTINE /
PROGRAMMED BY: / MARKUS SCHNEIDER / HELGE KOZIELEK & / ORIGINAL TURBOASS FILE / DOCUMENTED"

---

## Player Architecture

### Main Entry Point

```
HAUPTEINSPRUNG                  ; "Main entry point"
-MUSS EIN MAL PRO FRAME ANGESTEUERT  ; "Must be called once per frame"
-STEUERT DIE DREI STIMMEN TUNE+SFX   ; "Controls the three SID voices (tune + SFX)"
```

The player is called **once per VBI frame** (50 Hz PAL / 60 Hz NTSC). It iterates over three
SID voices plus the SFX (sound effects) system.

### Voice Layout

```
STIMMEN DES SID'S
SIND IN 7'ER BLOECKEN ANGELEGT WIE DIE  ; "SID voices are laid out in 7-byte blocks"
WERDEN SELBSTSTAENDIG INITIALISIERT       ; "Are initialized independently"
```

The three SID voices are arranged as 7-byte blocks at `$D400`, `$D407`, `$D40E` (standard SID
layout). Each voice block covers the standard SID registers:

```
SID REGISTER ADDRESS LAYOUT (from player source):
LO BYTE FREQUENZ         ; $D400 / $D407 / $D40E
HI BYTE FREQUENZ         ; $D401 / $D408 / $D40F
PULS WERT LO-BYTE        ; $D402 / $D409 / $D410
PULS WERT HI-BYTE        ; $D403 / $D40A / $D411 (upper nibble)
WAVEFORM STIMME          ; $D404 / $D40B / $D412 (control register)
ATTACK DECAY             ; $D405 / $D40C / $D413
SUSTAIN RELEASE          ; $D406 / $D40D / $D414
FILTER WERT              ; $D416 (shared)
FILTER/ LAUTSTAERKE      ; $D417 / $D418
OSZILATOR 1 / 2          ; $D41B / $D41C (read-only oscillator)
```

### Zero-Page Variables

The player uses zero-page RAM extensively. Per-voice state is organized in parallel arrays
(one slot per voice). The following annotated variables were identified from the player source:

**Per-voice data path pointers:**
- `-ADDRESSE WO DER DATEN-PFAD FEUR STIMME LIEGT` — address where the data path for this voice lies
- `-POSITION IM DATENPFAD` — position in the data path
- `-AKTUELLER BLOCK` — current block number
- `-ANZAHL DER BLOCK-WIEDERHOLUNGEN` — number of block repetitions remaining

**Per-voice note state:**
- `-NOTENLAENGE` — note length (duration counter)
- `-SOUND-NUMMER` — sound/instrument number
- `-SFX-PARAMETER` — SFX parameters
- `-AKTUELLER GLIDE-WERT` — current glide value
- `-GLIDE-SPEED` — glide speed
- `-NOTENENDE FUER GLIDE` — note end value for glide
- `-NOTE LO-BYTE` / `-NOTE HI-BYTE` — current frequency (lo/hi byte)
- `-PULSWERT LO-BYTE` — pulse width low byte
- `-VIBRATO EINSATZ` — vibrato onset
- `-DURRATION VERGLEICH` — duration comparison
- `-VARIABLER ZAEHLER` — variable counter
- `-WAVEFORM-STATUS` — waveform status
- `-FILTERSTATUS` — filter status
- `-NOTENHOEHE FUER KOM-PLETTEN BLOCK` — note pitch for complete block

**Global state:**
- `TUNE-SPEED` / `MUSIK-SPEED` — tune speed
- `AUSBLEND-SPEED` — fade-out speed
- `ANZAHL DER SID-STIMMEN` — number of active SID voices (1, 2, or 3)
- `CONTROL-BYTE` — control byte
- `FADESTATUS` — fade status
- `FADECOUN` — fade counter
- `FRAMEFXBYTE` — per-frame FX byte
- `SOUNDCUR` — current sound
- `ANZAHL SFX-STIMMEN` — number of SFX voices

---

## Data Format (Song/Music Data)

The player reads "data paths" (Datenpfad) organized as **blocks**. Internal label names from
the data tail of the player file confirm the following table types:

```
BLK1 .. BLK8    ; Music blocks (pattern data)
ARP0            ; Arpeggio table
DRUM0           ; Drum table
TRACK3 / TRACK4 / TRACK5  ; Voice tracks (order lists?)
```

### SFX Block Format

From the annotated source (verbatim):

```
SFX BLOCKE MUESSEN MIT         ; "SFX blocks must end with"
$FE, (NULLSOUND Z.B.),$01,$00  ; "$FE (null sound, e.g.),$01,$00"
ENDEN                          ; "end"
BLOCKE DIE SIE NICHT BENUTZEN  ; "Blocks you don't use"
MUESSEN NACHHER ENTFERNT WERDEN ! ; "must be removed afterwards!"

BYTE 0 = IN WELCHER STIMME 01 02 04   ; "In which voice: 01=V1, 02=V2, 04=V3"
         ODER KOMBIS Z.B   03 06 07 05  ; "or combinations e.g. 03 06 07 05"
BYTE 1 = WELCHER BLOCK WIRD GESPIELT ? ; "Which block is played?"
BYTE 2 = WELCHER BLOCK WIRD GESPIELT ? ; "Which block is played?"
BYTE 3 = WELCHER BLOCK WIRD GESPIELT ? ; "Which block is played?"
```

Translation: SFX entries are 4 bytes: `[voice_bitmask][block1][block2][block3]`.
The voice bitmask is `01`=voice 1, `02`=voice 2, `04`=voice 3, combinable (e.g. `03`=voices 1+2).
Bytes 1–3 specify which pattern blocks to play for each SFX slot. Unused blocks must be
terminated with `$FE` and removed from the data after composition.

The editor also embeds a note:

```
AN DIESE STELLE MUSS DAS DURCH DEN  ; "At this position the SEQ file"
EDITOR ABGESPEICHERTE SEQ. FILE EIN- ; "saved by the editor must be"
GELADEN WERDEN !!!!                   ; "loaded!"
```

This confirms the player template has a placeholder for the editor-exported SEQ data.

### Frequency Tables

The player contains two frequency tables (lo and hi byte):
```
FREQUENZTABELLE LO    ; Low-byte frequency table
FREQUENZTABELLE HI    ; High-byte frequency table
```

The lo-byte table entries (extracted from player data) begin:
`$03, $03, $03, $04, $04, $04, $05, $05, $06, $06, $07, $07, $08, $08, $09, $0A, ...`

This is a standard C64 chromatic frequency table for the SID chip.

Also referenced:
```
UND DEN ARPEGGIO TABS   ; "And the arpeggio tables"
EBENSO VERFAHREN SIE BEI DEN DRUMTABS ; "Proceed similarly for the drum tables"
```

---

## Effect Routines

The player contains the following named effect routines (extracted from $80-delimited
documentation strings):

### VIBRATO-ROUTINE
- Trigger: `VIBRATO AN ?` / `KEIN VIBRATO` (vibrato on/off check)
- Parameter: `VIBRATO-WERT` (vibrato depth), `VIBRATO EINSATZ` (vibrato onset)
- Algorithm: Complex calculation (`KOMPLIZIERTE BERECHNUNG`) oscillating the frequency
  within a given range (`INNERHALB GEWISSEN SPEKTRUMS`) around the base pitch.
  Speed set by `VIBRATO SPEED`. Produces frequency LO/HI writes.

### PORTAMENTO FX-ROUTINE
- Trigger: `PORTAMENTO EIN?` / `KEIN PORTAMENTO` (portamento on/off)
- Computes the entire frequency spectrum (`BRECHNET DAS GESAMMTE SPEKTRUM`)
  and calculates the portamento end value (`ENDWERT FUER PORTAMENTO`).
- Sets start and end values, then adds/subtracts the glide speed.

### GLIDE ROUTINE
- Trigger: `GLIDEROUTINE AN?` / `KEIN GLIDE`
- `GLIDE HOCH` / `GLIDE RUNTER` — glide up or down
- Adds/subtracts the glide speed value from frequency until target reached.
- `EXTRA LANGE NOTE?` — allows note to be held until the next note arrives.

### ARPEGGIO ROUTINE
- Trigger: `ARPEGGIO AN?` / `KEIN ARPEGGIO`
- Reads from arpeggio table (`ARPEG.TABELLE`)
- `TABLAENGE` — table length; walks to table start (`ZUM TAB-ANFANG`)
- Computes pseudo-value (`PSEUDO WERT BERECHNEN`) relative to the base note

### DRUM-ROUTINE
- `DRUM-TAB LESEN` — reads drum table
- Separate drum table (`DRUM-TABELLE`)
- Includes `KEIN HI-HAT` / `HI-HAT SETZEN` (hi-hat on/off)
- Sets frequency and waveform

### ECHO (ECHTES ECHO — "true echo")
- `ECHTES ECHO` vs `PSEUDO ECHO (TREMOLO)` — two echo modes
- True echo: note repeats at faster rate (`SCHNELLER FOLGE`, `VON NOTEN - ECHO`)
  with similar ADSR values (`AEHNL. EFFEKTE`). Counter incremented (`ZAEHLER HOCH!`).
- Pseudo echo (tremolo): waveform swapping (`WERT SWAPPEN?`) to create tremolo effect.
  (`DAUER RUNTER` / `DAUER HOCH` — duration down/up cycling.)

### PULS ROUTINE (Pulse Width Modulation)
- `PULSESWEEP` — standard pulse sweep
- `NORMALE PULSEROUTINE` / `PULSE-SWEEP` — normal vs sweep mode
- `PULS WERT LO/HI` — pulse value low/high bytes sent to SID `$D402/$D403`
- Direction logic: subtract (`PULSWERTE SUBTRAHIEREN`) / increment pulse width

### FILTER ROUTINE
- `FILTER AN ?` / `KEINE FILTER` — filter on/off check
- `FILTERSWEEP ?` — filter sweep enable
- `FILTERSEEK` — filter seek (chase target frequency)
- `HILFSZAEHLER` — auxiliary counter
- `ERLAUBT EIN WEITERSCHWINGEN DES FILTERS OHNE INIT BEI NEUER NOTE` —
  "allows filter to continue oscillating without re-init on new note"
- `SETZEN IN NEUER NOTE!!!` — set filter on new note
- `FILTER ZU ENDE!` — filter finished

### RELEASE CONTROL
- `RELEASECONTROL` — release control
- `BEENDET FRUEHZEITIG DAS RELEASE` — terminates release early
- `NOTENABBRUCH?` — note abort?
- Sets second waveform (`ZWEITE WAVEFORM`) for release

### ANSCHLAGSDYNAMIK (Note attack dynamics)
- `ANSCHLAGSDYNAMIK?` — "attack dynamics?" (velocity-like parameter)
- Applied on new note load

---

## Song Structure (from demo data)

The `ed>demo song` (1992) and `2.MUSIC DEMO` files are raw song data as exported by the
Compotech editor. Based on the editor's SEQ format and the player internals:

- Data contains **pattern blocks** referenced by track/order list
- The pattern stream includes note data, duration, waveform changes, and effect commands
- Block markers: `$FF` = repeat, `$FE` = end of block (null sound)
- Voice bitmask confirms per-voice assignment

From the demo song binary (2668 bytes), pattern data visible includes:
- Note bytes (pitch values)
- Duration values
- Commands for waveform select
- Arpeggio/vibrato enable bytes

---

## Player Integration Notes (from source documentation)

```
TUNE NUMMER              ; tune number to select
ANZAHL DER STIMMEN       ; number of voices (1-3)
SONG SPEED               ; song speed (timer value)
AUSBLEND SPEED           ; fade-out speed
STIMMENZAHL              ; voice count parameter
LAUTSTAERKE              ; master volume ($D418 low nibble)
FILTER AUF               ; filter on
INITIALISIERUNG ALLER WERTE  ; "initialization of all values"
EIN SAUBERES EINSETZEN VON MUSIK ODER ; "clean entry of music or"
ZEN VON MUSIK ODER       ; "..."
KEIN FADEN !!            ; "no fade!!"
KEIN AUSBLENDEN          ; "no fade-out"
WENN MUSIK               ; "when music"
KEIN NACHKLINGEN !!!     ; "no reverb!!!" (clear important SID registers at end)
DAMIT KEIN NACHKLINGEN   ; "so no reverb" (end-of-music register clear)
FADESTATUS SETZEN        ; "set fade status"
(KANN KOMPLETT ENTFERNT WERDEN) ; "(can be completely removed)" — refers to TEST-IRQ
```

The SFX system runs **independently** of the music:
```
SFX-VERZWEIGUNG          ; SFX branch point
EINSPRUNG ZU DEN SOUNDEFFEKETEN ; "entry to sound effects"
EINSPRUNG ZUM PLAYER     ; "entry to player"
ZEIGT DIE RASTERZEIT AN  ; "shows the raster time"
```

The SFX routine can be called separately (`FUER SFX ROUTINE`) with its own voice count
(`ANZAHL SFX-STIMMEN`) and parameters.

---

## On Absent Manual

No formal printed or text-mode manual for Compotech or the X-Ample player was found
in any of the fetched D64 images. The "Docs 2 Compotech" release (CSDb #253740) is a
**runtime C64 viewer program** (crunched binary, not extractable as plain text without
emulation). The Mister Giga docs are embedded in the viewer and require runtime execution
to read.

The V2.1 distribution included the full annotated TurboAss source of the player
(`.player-routine` SEQ) as the primary technical reference for integrators.

---

## OPEN: Items Requiring Disassembly

The following aspects of the format are **not determinable from this text research alone**
and require actual disassembly (siddump/py65/RE):

1. **Exact note/pitch byte encoding** — the frequency table byte order and pitch-to-table-index
   mapping. Are notes stored as index into freq table, or as absolute SID freq values?

2. **Block/pattern stream byte format** — exact command byte semantics in the pattern stream.
   What is the duration encoding? Are effects triggered by flag bytes or command bytes?

3. **SFX vs. music voice arbitration** — how the player decides which voice to steal for SFX.

4. **XTracker V4.1x vs V4.2x** — these SIDId variants are not in CSDb and have no known
   separate release. They may be later revisions of the same player with a different editor.
   Differences vs Compotech: unknown without disassembly comparison.

5. **Parsec Music Editor V4 format** — the T64 info file is compressed (Parsec_4_info.t64);
   the actual format diff between V4 and V5.1 is not reconstructible from text alone.

6. **Thomas_Detert SIDId variant** — Thomas Detert used a customised version; differences
   from the standard Compotech_V2.x player are not documented in any released source.

7. **X-Ample_Digi SIDId variant** — no documentation found; likely a digi-sample extension.
