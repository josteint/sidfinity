# Archive: 64'er Magazin 10/1986 — Soundmonitor type-in (the holy grail)

```
source_url:    https://archive.org/details/64er_1986_10
                 (OCR full text: https://archive.org/stream/64er_1986_10/64er_1986_10_djvu.txt)
fetched_via:   direct (archive.org djvu OCR text, curl)
fetch_date:    2026-06-13
author:        Chris Hülsbeck (article + program), translated/edited "tr" (64'er staff)
content_date:  1986-10
publication:   64'er (Markt & Technik), issue 10/October 1986, "Listing des Monats", pp. 53–64
reliability:   PRIMARY SOURCE — the original author's own manual + the type-in machine-code
               dump. Highest authority for the v1.0 format and the per-frame SID write model.
               Caveat: text is magazine OCR; a few tokens are garbled (flagged inline). The
               24-register parameter table and the worked byte examples are clean and verbatim.
```

This is the original publication: a 5-page **HEX DUMP of 11 KB of machine code** (11591 two-digit
hex bytes, 1448 lines, entered via the "MSE" machine-code editor, see issue p.76) plus a full
German manual ("Bedienungsanleitung") written by Hülsbeck himself. NOT assembly source — the
listing is opaque machine code; the *format knowledge* lives in the manual prose + worked
examples + the 24-register table, all reproduced/translated below.

The distributed file is `SM.PACKED` (loads at $0801, BASIC start). `RUN` unpacks it (border turns
dark blue during unpack); the result is the working editor, which occupies **51 disk blocks** and
starts with `RUN` (BASIC stub at $0801 does `SYS` into $1000). Checksum of the packed file:
`FOR I=2049 TO 13635: A=A+PEEK(I): NEXT: PRINT A` must print **1487068** ($0801=2049, end 13635).

---

## 1. Memory layout — "Tabelle 1. Speicheraufteilung des Soundmonitors"

This is the authoritative map. The replayer's song-data tables are the $A000–$BFFF block (the
"module"). **Critically, the TRACK/STEP-TABLE is NOT stored as interleaved rows — it is stored as
parallel 256-byte columns, one set per voice** (this refines the earlier `research.md` guess).

| Range        | Contents (translated)                                                     |
|--------------|----------------------------------------------------------------------------|
| `$02C0–$02E0`| Variables of the music routine                                             |
| `$1000–$2FFF`| **Editor program** (the GUI; not needed by the replayer)                   |
| `$3000–$9FFF`| Free for bars (bar/pattern note data may live here too)                    |
| `$A000–$A0FF`| **Low-bytes of the bar addresses for voice 1** (indexed by step $00..$FF)   |
| `$A100–$A1FF`| **High-bytes of the bar addresses for voice 1**                            |
| `$A200–$A2FF`| **Transpose store for voice 1** (per step, two's-complement)               |
| `$A300–$A3FF`| **Sound base number (soundtranspose ST) for voice 1** (per step)           |
| `$A400–$A7FF`| Playback sequence for voice 2 (same 4×256 structure as voice 1)            |
| `$A800–$ABFF`| Playback sequence for voice 3 (same 4×256 structure as voice 1)            |
| `$AC00–$ACFF`| Low-bytes of the arpeggio store                                            |
| `$AD00–$ADFF`| High-bytes of the arpeggio store                                           |
| `$AE00–$B1FF`| **Sound store** (sound patches). OCR: "20 Soundeinstellungen, jeweils 24 Bytes … 32 Sounds ergeben 768 Bytes" → **32 sound patches × 24 bytes = 768 bytes** = $300 ($AE00..$B0FF), overlapping the next region's start. (See note.) |
| `$B000–$BDFF`| **Bar/pattern store** ("Taktspeicher")                                      |
| `$BE00–$BEFF`| Empty bars ("Leertakte"); `$BE00` = the empty bar used as the default pause |
| `$BF00–$BFFF`| Arpeggio store ("Arpeggiospeicher")                                         |
| `$C000–$C00E`| **Music routine entry ("Musicmaster Einsprung") = init**                   |
| `$C00F–$C011`| Variables                                                                  |
| `$C01F–$CC00`| **"Musicmaster" program** (the standalone replayer code)                    |
| `$CC01–$CFFF`| Variables of the music routine and of the editor                           |

"Insgesamt von $A000–$BFFF (32 Blöcke)" — the whole module is the 32-page $A000–$BFFF block.

Note on overlaps: the OCR garbles the sound-store start (printed "AEOO"/"BOOO" and "B1FF"). The
clean reading is: 32 patches × 24 bytes = 768 ($300) bytes; bars from $B000; empty bars $BE00;
arps $BF00. The exact sound-store base is best confirmed against the binary (vendor/SOUND-MONITOR.prg)
— the manual's intent is "32 sounds, 24 bytes each", placed below $B000.

### Replayer entry points (matches the standard HVSC signature init=$C000, play=$C020)
- **`$C000` = init** (the "Einsprung", entry block $C000–$C00E). A complete song saved as
  "Complete Song" plays "as if you had loaded it absolutely and started it with `SYS 49152`".
- **`$C020` = play** (per-frame). The block $C00F–$C011 holds variables; play sits just past it.
  (`$C000`=49152, `$C020`=49184.) The replayer "runs completely independently in the interrupt"
  — i.e. it is hooked into a raster/CIA IRQ so the song plays even while editing.
- `SYS 4096` ($1000) restarts the **editor** (after pressing `X` to exit to BASIC).

---

## 2. TRACK/STEP-TABLE (master sequencing) — verbatim format

Per-track row layout shown to the user (decoded from the 4 parallel columns above):

```
SP  TRKx  TR  ST
00  0000  00  00
|   |     |   |
|   |     |   sound transpose (ST) — added to every sound number used in the bar
|   |     transpose (TR) — two's complement, added to every note in the bar
|   bar address (TRKx) — direct 16-bit RAM pointer to bar/pattern data
step number ($00..$FF), like a BASIC line number
```

- **SP (Step):** fixed column $00..$FF. There is a **FIRST STEP** and **LAST STEP** (set with `F3`
  / `F5`); the song plays steps FIRST..LAST then loops/ends. "CURRENT STEP" shows the playing step.
- **TRKx:** "TRK1/TRK2/TRK3" = the bar-playback sequence for SID voices 1/2/3. Direct 16-bit
  address of the bar in RAM (low byte in $Ax00 page, high byte in $Ax01 page). After Initialize,
  every step points at `$BE00` (the empty bar = whole-bar pause).
- **TR (Transpose):** value added to each note in the bar. `$00..$7F` = positive, `$FF..$80` =
  negative (two's complement). Worked example: a C-2 with transpose `$01`→C#2, `$03`→D#2,
  `$0C`→C-3, `$FF`→H-1 (B-1), `$FB`→G-1. (German note "H" = English B.)
- **ST (Soundtranspose):** value added to **every sound number** referenced inside the bar. A bar
  can only address sounds $0..$F directly (low nibble of the note byte); ST lets the same bar use
  sounds > $0F and lets one bar be replayed with different instruments.

---

## 3. NOTE EDIT — bar/pattern format (verbatim)

A bar is a grid; notes are read **left-to-right, then top-to-bottom**. The display shows 4 columns
× N rows; **the leftmost column = the on-beat eighths, the following 3 columns = the 3 successive
32nd-notes after each eighth.** Example bar at $BE00 (two notes then rests):

```
be00 C-2 61   --- 00   --- 00   --- 00
be08 --- 00   --- 00   --- 00   --- 00
...
```

The left hex (`be00`, `be08`, …) are **direct RAM addresses of the note data** (verifiable in an
emulator memory dump). Each grid cell is **2 bytes**: a note byte + a "sound/options" byte.

### Note byte
- Note value = note letter (C..H, where H=B) + sharp marker (`#` or `—`) + octave (0..7).
- `---` (three dashes) = **pause / note-off** ("release the key" on playback). Entered as `—` on
  the note position.
- `+++` (three plus signs) = **tie / hold** the previous tone (only if the sound permits holding).
- Notes shown **inverse** = struck (gate-on / new attack). Notes shown **normal** (entered with
  SHIFT held) = **not struck** (legato — continues without re-triggering the envelope).

### Second byte = sound number (low nibble) + sound-options (high nibble)
```
C-2 61
    ||
    |+--- low nibble  = sound number (0..F) → which of the 32 patches (after +ST)
    +---- high nibble = sound options (4 bits)
```

**Sound-options bits (high nibble of the per-note byte):**

| bit | option            | meaning                                                       |
|-----|-------------------|---------------------------------------------------------------|
| 0   | portamento        | enable portamento (slide) toward this note                    |
| 1   | transpose disable | this note ignores the bar's TR transpose                      |
| 2   | arpeggio          | play an arpeggio rooted on this note                           |
| 3   | soundtranspose    | (1=enable / use ST?) — "soundtranspose"                        |

Worked example: `C-2 61` → note C-2, instrument 1, options nibble `6` = binary `0110` = bit1
(transpose disable) + bit2 (arpeggio). The `*`/£ key (`<*>` in the manual) toggles/inverts the
option bits and shows the resulting digit, available in both the track table and the note display.

### Arpeggio selection inside a bar
- An arpeggio is rooted at a struck note that has the arpeggio bit (bit 2) set → nibble must be
  `4` (plus any other option bits).
- **WHICH arpeggio runs is encoded in the *second byte after the last note* (the trailing byte of
  the bar), because with arpeggios you rarely play two notes back-to-back.** "Since there is no
  'last note' at the start of a bar, the byte after the bar's last note is used." Values:
  `$08`=arpeggio 1, `$10`=arpeggio 2, `$18`=arp 3, `$20`=arp 4, … (i.e. arp index×8).

---

## 4. ARP/S DATA — per-bar base parameters (tempo / length / volume / fade) + arpeggios

Reached via RETURN under the ARP/S column. Each bar's ARP/S row begins with an address, then
**8 hex bytes**. The first row (the one whose address is shown in the track/step table) holds the
**base parameters ("Grundparameter"):**

| pos | name (translated)                                    | meaning                                                                                   |
|-----|------------------------------------------------------|--------------------------------------------------------------------------------------------|
| 0   | CIA-timer speed **low** (fine tempo)                 | fine tempo trim, e.g. for syncing to a turntable                                           |
| 1   | CIA-timer speed **high**                             | "ideally 35..50"; smaller = faster                                                         |
| 2   | coarse tempo                                         | between 0 and 4; smaller = faster                                                          |
| 3   | bar length ("Taktlänge")                             | default `$20` (32 notes). See below.                                                       |
| 4   | **fade-out** at song end                             | `$FF` = no fade. To use: at song end, point ARP/S at another address with identical base+arps but a *different* byte-4 (`$10`=fast fade … `$30`=slow). |
| 5   | **volume** `$00..$0F`                                | ≈ SID register 24 (`$D418`) low nibble, **without** filter. (The filter high-nibble of $D418 comes from sound register 16; when filter is set there, that sound's low nibble of reg-16 is unused.) |
| 6   | unused                                               |                                                                                            |
| 7   | unused                                               |                                                                                            |

**Bar length (byte 3):** default `$20` = 32 notes/bar. Because each note carries a sound byte too,
the *next free bar address* is `length × 2` higher. `$20`→step $40 ($B000,$B040,$B080,$B0C0,…).
Other values: `$30` = 6/8 bar (step $30: $B000,$B030,$B060,…); `$40` = like $20 but double length
(step $80: $B000,$B080,$B100,…).

### Arpeggios (the row under the base params)
- An arpeggio is **always 8 note-steps** called in sequence; each step works exactly like
  Transpose (added to the root note). Example A-minor arpeggio:
  ```
  0c 07 03 00  0c 07 03 00
  ```
  "Like playing a chord with four fingers": A' (`0C`), E' (`07`), C' (`03`), A (`00`).
- The same DELETE-bar key combo (`SHIFT + @`) in ARP/S sets the base params plus two arpeggios.

---

## 5. The 24 sound registers (the per-frame SID write model) — VERBATIM, translated

This is the EDIT SOUND patch: **24 bytes per sound, 32 sounds.** This table is the heart of the
replayer's per-frame SID writes. Worked demo-sound byte rows are in §6.

| Reg | Name                              | Meaning / SID mapping (translated verbatim)                                                                                                                                                                                                                       |
|-----|-----------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| 0   | **Waveform (keyon)**              | Written to SID waveform regs 4/11/18 ($D404/$D40B/$D412) **when a note is struck** (the inverse notes). High digit = waveform: `0`=silent, `1`=triangle, `2`=saw, `4`=pulse (regs 4,5,6,7 and 9 affect pulse), `8`=noise. Low digit (4 bits): bit0=**gate** (start envelope), bit1=sync, bit2=ring-mod, bit3=test. So struck values are `11/21/41/81` (gate set). `15` is useful for effects. |
| 1   | **Attack/Decay**                  | SID A/D regs 5/12/19 ($D405/$D40C/$D413).                                                                                                                                                                                                                          |
| 2   | **Sustain/Release**               | SID S/R regs 6/13/20 ($D406/$D40D/$D414).                                                                                                                                                                                                                          |
| 3   | **Portamento effect byte**        | Affects the effect produced when portamento "over-shoots" (used together with reg 9; the upper/lower bound the tone is dragged toward). [OCR garbled on this line; semantics: it is the target/limit byte for the slide.]                                          |
| 4   | **Pulse rate**                    | Pulse-width / duty of the pulse waveform ($00–$FF). (→ $D402/3, $D409/A, $D410/1.)                                                                                                                                                                                 |
| 5   | **Pulse EG count up**             | When PW is modulated → "floating"/sweeping sound. How long reg-7's value is **added** to the pulse width.                                                                                                                                                          |
| 6   | **Pulse EG count down**           | Like reg 5 but reg-7's value is **subtracted**.                                                                                                                                                                                                                   |
| 7   | **Pulse EG count byte**           | Magnitude of the value added/subtracted (above ~`$30` the tone gets "dirty").                                                                                                                                                                                     |
| 8   | **Waveform (keyoff)**             | Like reg 0 but **gate bit must be 0** (values `10/20/40/80`). Written when the note is released. You *can* change waveform between keyon/keyoff (not always good). Normal case = same waveform as reg 0 (e.g. 0=21 / 8=20; 11/10, 41/40, 81/80).                     |
| 9   | **Pulse EG mode / Portamento eff**| Left digit `1` → pulse-EG continuously restarted. Right digit = portamento control: bit0=slide tone **up**, bit1=slide tone **down**; the bounds are the struck note and reg 3; bit2=slide only **once** (not continuously) — audible in the BASEDRUM sound. Bits 3,6,7 unused. For normal portamento the right digit = 0. |
| 10  | **Portamento low**                | Slide speed (low byte). `$00` = no portamento. The slid note must also have the portamento sound-option bit set.                                                                                                                                                   |
| 11  | **Portamento high**               | Slide speed (high byte). High value + reg-9 bit0 set → interesting effect.                                                                                                                                                                                         |
| 12  | **Vibrato level**                 | Vibrato intensity (depth).                                                                                                                                                                                                                                         |
| 13  | **Vibrato speed**                 | `$00`=very fast … `$7F`=very slow. **Bit 7** decides whether vibrato begins downward or upward.                                                                                                                                                                    |
| 14  | **Vibrato delay**                 | Delay after a note is struck before vibrato starts.                                                                                                                                                                                                               |
| 15  | **Fine detune**                   | Fine pitch trim (normally `$00`); used for turntable/tape sync.                                                                                                                                                                                                   |
| 16  | **High nibble of SID reg 24**     | Right digit = unused. Left digit = filter type (`0`=no filter; bit0=low-pass, bit1=band-pass, bit3=high-pass) → high nibble of `$D418`. **If a sound needs no filter, set this byte to `$FF`** — then it does NOT disturb other sounds currently using the filter (suppresses SID filter on/off "click"). If filter was set for a voice and the next sound on that voice has reg16=`$FF`, the filter stays as-is (must program a sound that clears regs 16..23 = `$00` to actually clear it). |
| 17  | **Resonance / Filter-to-voice**   | Exactly SID reg 23 ($D417). Left digit = resonance; right digit = which voices are routed through the filter (bit0..2 = voice 1..3).                                                                                                                               |
| 18  | **Cutoff frequency**              | Filter cutoff `$00..$FF` → SID cutoff ($D415/$D416).                                                                                                                                                                                                              |
| 19  | **Filter EG count up**            | Same principle as the pulse-EG (regs 5,6,7) but modulating the **filter** cutoff (count-up time).                                                                                                                                                                 |
| 20  | **Filter EG count down**          | Time the filter is counted **down**.                                                                                                                                                                                                                             |
| 21  | **Filter EG count level lo (up/down)** | Left digit = how much (0..F) to count **up**; right digit = how much to count **down** (only for filter effects with reg 23).                                                                                                                                  |
| 22  | **Filter EG count level hi**      | Magnitude counted up/down (`$00..$FF`; `$02..$20` recommended).                                                                                                                                                                                                   |
| 23  | **Filter EG mode / Trigger voice**| Left digit: bit0 = restart filter-EG continuously; bit1 = start at "count up" vs "count down". Right digit = which voice starts the EG (normally the filtered voice): bit0=voice1, bit1=voice2, bit2=voice3.                                                       |

**Key takeaways for the per-frame write model:**
- regs 0 & 8 are the **keyon vs keyoff waveform/control** bytes ($D404-style). Gate edges are
  produced by writing reg 0 (gate=1) on a struck note and reg 8 (gate=0) on release.
- The **pulse-EG (regs 4–7,9)** and **filter-EG (regs 18–23)** are identical software ramp
  generators run *per frame* on the chip's PW and cutoff respectively (add reg7/reg22 for N frames
  counting up, subtract for M frames counting down, optionally restart). This is the engine's
  per-frame PWM and filter-sweep — modelled as an add/subtract counter, not a table.
- **Vibrato** (regs 12–14): depth, speed (bit7 = initial direction), delay-after-attack.
- **Portamento** (regs 3, 9, 10, 11 + the per-note portamento option bit): a 16-bit-speed slide
  between the struck note and reg-3 bound; reg-9 right nibble picks up/down/once.
- **Filter byte $FF convention** (reg 16): the engine writes the $D418 high-nibble only when reg16
  ≠ $FF; $FF = "leave global filter alone" (anti-click). Important for matching $D418 writes.
- **Volume**: ARP/S byte 5 → $D418 low nibble; filter type (reg 16 high digit) → $D418 high nibble.

---

## 6. Demo sounds (literal 24-byte patches — ground-truth parse fixtures)

From the manual. Each is a full 24-byte sound patch (reg 0 .. reg 23, left→right). Excellent
unit-test fixtures for the extractor + composer.

```
Bass (tutorial sound 01):
  41 09 99 00 20 10 10 10 40 10 00 00 00 00 00 00 FF 00 00 00 00 00 00 00

Melody (tutorial sound 02):
  41 08 7C 00 60 10 10 10 40 10 00 00 10 07 1A 00 FF 00 00 00 00 00 00 00

Flute:
  11 09 99 00 00 00 00 00 10 00 00 00 10 06 10 00 FF 00 00 00 00 00 00 00

Basedrum:
  11 09 09 01 00 00 00 00 10 01 FF 00 00 00 00 00 FF 00 00 00 00 00 00 00

Snaredrum:
  81 09 09 01 00 00 00 00 80 01 10 30 00 00 00 00 FF 00 00 00 00 00 00 00

Rambo theme sound:
  41 08 7D 00 00 20 10 10 40 10 00 00 10 08 1D 00 FF 00 00 00 00 00 00 00

Ringmodulation effect:
  15 08 7A 10 00 00 00 00 14 01 20 23 00 00 00 00 FF 00 00 00 00 00 00 00

Portamento sound (play with the portamento sound-option bit set):
  11 09 99 00 00 00 00 00 10 00 70 00 00 00 00 00 FF 00 00 00 00 00 00 00
```

(Reg 0 = `41` → pulse + gate; `11` → triangle + gate; `81` → noise + gate; `15` → triangle +
sync + gate, for ring/sync effects. Reg 8 mirrors reg 0 with gate cleared: `40`/`10`/`80`. Reg 16
= `FF` in all → these sounds touch no filter.)

---

## 7. Other manual facts relevant to parsing / playback

- **Metronome:** after Initialize, bar `$BE80` holds a metronome bar; sound number `00` is reserved
  for a metronome-simulating bar. For the metronome bar TR and ST must be `00`.
- **`+++` (hold)** only sustains if the sound permits holding (i.e. keyoff waveform/gate handling).
- **Realtime record / Quantize:** `Q` sets quantize (1=16th, 2=8th, 3=4th, 0=off). Not a
  playback-format concern (editor-only), but explains how bars get filled.
- **Save filetypes** (`T` key): *Soundnumber* (one/several sound patches), *Complete Song* (song +
  music routine — this is the playable PSID-equivalent, plays via `SYS 49152`), *Steps only* (song
  WITHOUT the music routine — fewer blocks; for continuing work). For loading a song you must NOT
  set the "Soundnr" filetype.
- **Independent IRQ replayer:** "Der Hauptteil des Programms, die Abspielroutine, läuft völlig
  selbständig im Interrupt" — the play routine is IRQ-driven (CIA-timed, see ARP/S bytes 0–1), so
  HVSC PSIDs from this engine are CIA-timed (relevant to the per-IRQ verification path).

---

## Provenance trail

- Article + manual: 64'er 10/1986, pp. 53–64, "Listing des Monats", author Chris Hülsbeck (German;
  translated here). OCR lines ~17743–18591 of `64er_1986_10_djvu.txt`.
- "Tabelle 1. Speicheraufteilung des Soundmonitors": OCR lines ~18640–18800.
- 24-register "Soundparameter" table: OCR lines ~18470–18591.
- Demo sounds + metronome + synchronisation: OCR lines ~18560–18600.
- Listing 1 (the 11 KB hex dump) begins OCR line ~20195 (`Listing 1. Soundmonitor`, file
  `sm.packed`, load $0801, packed-checksum 1487068). Listing continuations at ~36761 and ~43173.
```
