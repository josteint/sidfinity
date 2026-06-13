---
source_url: https://www.namelessalgorithm.com/computer_music/blog/soundmonitor/
fetched_via: wayback 2026-02-14 (raw id_ snapshot 20260214165125; live site 404s/blocks curl; images from 2021-04-21 capture)
fetch_date: 2026-06-13
author: Jakob Schmid (namelessalgorithm.com)
content_date: 2021 (article) / images same
reliability: secondary (popular RE writeup) — image artefacts (edit-sound screen + 64'er memory map) are PRIMARY; corroborated against the actual $C000 player disasm of an HVSC tune (see csdb_release_and_downloads.md §"player RE")
---

# Soundmonitor — namelessalgorithm.com RE writeup (full)

Jakob Schmid's article. It is a *popular* (narrative) reverse-engineering writeup, strong on
the editor's data model and the original 64'er memory map. It does NOT contain a byte-level
sound-patch table nor the per-frame SID write order — those come from the embedded
screenshots (transcribed below) and from disassembling an actual HVSC player
(see `csdb_release_and_downloads.md`). Treat the prose as orientation; treat the two image
transcriptions in this file as load-bearing.

## Identity / provenance (corroborated everywhere)

- Author: **Chris Hülsbeck** (b. 1968), age 18 at release. Later wrote **TFMX** (C64 then Amiga;
  Turrican II). Soundmonitor is his earlier, simpler engine.
- Published: **64'er** magazine **issue 10/1986** (Markt & Technik, German), as the "Listing des
  Monats" — a **5-page hex dump** the reader typed in by hand. (Pouet commenters say 8 pages;
  VGMPF says first published Sep 19 1986. The 64'er issue is dated 10/1986.)
- It is a **type-in**, not a scene release; the CSDb entry exists for its historical impact.
- "Musik wie noch nie." Called a 'Mammut-Programmbeschreibung'.

### The hex dump (useful for any "is this the original V1.0 image?" check)
- **11591 two-digit hex bytes**, **1448 lines**, 8 bytes per line.
- First line (verbatim): `0f 08 0a 00 9e 20 32 30` — this is a BASIC autostart stub at $0801:
  `0f 08` = link to next BASIC line, `0a 00` = line number 10, `9e` = token `SYS`, then
  ASCII ` 20` … (the SYS target). i.e. `10 SYS <addr>`. (The HVSC/vendored editor PRG's stub
  differs slightly — `9e 32 31 36 37` = `SYS 2167` = `$0877` — because the vendored V1.0 .t64
  is a self-contained editor build; same family.)

## Editor structure (the 4 screens — the data model)

Soundmonitor has **3 tracks**, one per SID voice. At any instant each track is playing a **bar**.
A bar is a block of note data; each note has a pitch + an associated **sound** (instrument/patch).
The 4 editor screens map 1:1 to the 4 on-disk data structures:

1. **EDIT SOUND** — a *sound* is a patch for one SID oscillator: waveform, envelope, vibrato,
   portamento, filter cutoff/resonance/envelope. **24 parameters total.** (Byte table below.)
2. **TRACK/STEP TABLE** — the master sequence: 3 tracks side by side. (Row format below.)
3. **NOTE EDIT** — edits one bar; notes/pauses laid out left→right, top→bottom on a 32nd grid.
4. **AR/S DATA** — tempo + arpeggios; can change per bar (tempo/harmonic changes).

All four are stored together in a **SONG**.

### TRACK/STEP TABLE — row format (per track)
```
  SP TRKx TR ST
  00 0000 00 00 -- (the trailing "00" column = sound transpose)
  |  |    |  |
  |  |    |  sound-base offset (ST): offsets the instrument index of every note in the bar,
  |  |    |                          so a bar can be reused with different sounds
  |  |    transpose (TR): two's-complement semitone transpose of the whole bar
  |  bar address (TRKx): a *direct 16-bit RAM pointer* to the bar's note data, normally $BE00+
  step parameters (SP)
```
- **TRKx is a literal 16-bit memory address** to the bar data (verifiable in an emulator memory
  dump). Reusing one bar at different `TR`/`ST` is the engine's only "pattern compression" on a
  32 KB machine.
- Two's complement is used for negatives in TR (e.g. transpose **down 2 semitones = `FE`**).
  Reference table the article gives:
  `... -8 -7 -6 -5 -4 -3 -2 -1 0 1 2 ...` ↔ `... F8 F9 FA FB FC FD FE FF 0 1 2 ...`
- (The article's prose only labels TRKx/TR/ST + "sound transpose"; the byte size of SP and the
  exact field packing of a track/step *record* come from the German 64'er memory map +
  player disasm — see below. The editor screenshot shows columns `SP TRK1 TR ST  TRK2 TR ST
  TRK3 TR ST  AR/S`, i.e. one shared SP + per-track {TRK,TR,ST} + a shared AR/S pointer per row.)

### NOTE EDIT — bar / note encoding (load-bearing)
Example dump straight from the article (addresses are literal RAM):
```
be00 C-2 61 --- 00 C-3 02 --- 00
be08 --- 00 --- 00 --- 00 --- 00
be10 C-2 61 --- 00 --- 00 --- 00
be18 --- 00 --- 00 --- 00 --- 00
be20 C-2 61 --- 00 --- 00 --- 00
be28 --- 00 --- 00 --- 00 --- 00
be30 C-2 61 --- 00 --- 00 --- 00
be38 --- 00 --- 00 --- 00 --- 00
```
- A bar shown = **8 rows × 4 note-cells**, each cell = **2 bytes** ⇒ **32 cells = 64 bytes/bar**.
  This is the **32nd-note grid**: the leftmost column = even 8th notes, each followed by 3
  successive 32nds (so column tells on-/off-beat at a glance). `$BE00`-row addresses advance by
  $08 per displayed row of 4 cells ⇒ 8 bytes/row, consistent with 2-byte cells.
- **Each note = 2 bytes:**
  - byte 0 = **note value** (pitch; `---` = no note / continuation. C-2 etc.)
  - byte 1 = **`(sound-options-nibble << 4) | instrument-index`** (high nibble = options,
    low nibble = instrument). The article's worked example:
    ```
    C-2 61
    |   ||
    +------- note: C2
        |+-- instrument: 1
        +--- sound options: 6  (= transpose-disable | arpeggio)
    ```
  - **Sound-options nibble** (bit numbering as the article writes it, bit1 = LSB):
    ```
     bit  option
      1   portamento        (LSB, value 1)
      2   transpose disable (value 2)
      3   arpeggio          (value 4)
      4   soundtranspose    (MSB, value 8)
    ```
    So `6 = 0110b = transpose-disable | arpeggio`. (Confirmed by inception2 screenshot which
    shows the same "sound options" legend with portamento/transpose/arpeggio/soundtranspose.)

### AR/S DATA
- Defines **tempo and arpeggios**, **per bar** (a row in the track/step table references an AR/S
  entry). Arpeggios = rapid pitch changes emulating a chord on one channel. Article namechecks
  Hubbard's *Monty on the Run* (1985) as the arp precedent. (Byte layout of the arp tables: see
  64'er memory map below — Arpeggio low/high pointer tables at $AC00/$AD00, arp data at $BF00.)

## Memory map — 64'er "Tabelle 1" (PRIMARY; transcribed from `memory_map.jpg`)

This German table is the authoritative editor/player memory layout. **This is the canonical
data layout the MusicMaster replayer reads** (verified: the $C000 player in an HVSC tune indexes
exactly these absolute bases — see `csdb_release_and_downloads.md` §player RE).

| Range        | German label                                                  | Meaning |
|--------------|---------------------------------------------------------------|---------|
| `02C0–02E0`  | Variablen der Musikroutine                                    | music-routine zero-page-ish vars (actually $02Cx page) |
| `1000–2FFF`  | Editorprogramm                                                | editor code |
| `3000–9FFF`  | Frei für Takte                                                | free for **bars** (note data) |
| `A000–A0FF`  | Low-Bytes der Takte für Stimme 1                              | **voice 1**: bar-address LOW table (the TRKx lo per step) |
| `A100–A1FF`  | High-Bytes der Takte für Stimme 1                             | voice 1: bar-address HIGH table |
| `A200–A2FF`  | Transpose-Speicher für Stimme 1                               | voice 1: transpose (TR) table |
| `A300–A3FF`  | Sound-Basisnummer für Stimme 1                                | voice 1: sound-base (ST) table |
| `A400–A7FF`  | Abspielfolge für Stimme 2 (wie für Stimme 1)                  | **voice 2**: same 4 tables (lo/hi/transpose/sound-base), $A400/$A500/$A600/$A700 |
| `A800–ABFF`  | Abspielfolge für Stimme 3 (wie für Stimme 1)                  | **voice 3**: same 4 tables, $A800/$A900/$AA00/$AB00 |
| `AC00–ACFF`  | Low-Bytes des Arpeggiospeichers                               | arpeggio pointer LOW table |
| `AD00–ADFF`  | High-Bytes des Arpeggiospeichers                              | arpeggio pointer HIGH table |
| `AE00–B1FF`  | Soundspeicher (20 Soundeinstellungen, jeweils 24 Bytes) (32 Sounds ergeben 768 Bytes) | **sound bank**: 24 bytes/sound; reads "20 sounds" but "32 sounds = 768 bytes" (32×24=768) ⇒ the bank holds **32 sound slots × 24 bytes = 768 bytes** ($AE00–$B0FF), and $B100–$B1FF spare |
| `B000–BDFF`  | Taktspeicher                                                  | **bar storage** (the actual note data, where TRKx points; overlaps the spare end of the sound region by convention) |
| `BE00–BEFF`  | Leertakt                                                      | **empty bar** (the default/blank bar) |
| `BF00–BFFF`  | Arpeggiospeicher                                              | **arpeggio data** |
|              | "Insgesamt von A000–BFFF (32 Blöcke)"                         | the whole song-data window $A000–$BFFF = 32 × 256-byte blocks |
| `C000–C00E`  | Musikroutine Einsprung                                        | **music-routine entry vectors** (init $C000, play $C020, …) |
| `C00F–C011`  | Variablen                                                     | vars (play flag etc.) |
| `C01F–CC00`  | »Musicmaster«-Programm                                        | **the MusicMaster replayer code** |
| `CC01–CFFF`  | Variablen der Musikroutine und des Editors                   | replayer + editor work variables |

Key consequences for a decompiler:
- The "module" is conceptually the **$A000–$BFFF window** (32 blocks). Per voice there are 4
  parallel 256-byte step tables (bar-addr lo, bar-addr hi, transpose, sound-base) → up to 256
  steps/voice. Sounds are a flat **32×24-byte** bank. Bars are 64-byte 32nd grids of 2-byte
  note cells, anywhere in $3000–$BDFF.
- This window is **relocatable in practice** (DUSAT relocator, many HVSC load addresses) but the
  *internal structure and relative offsets are fixed*; the player just has a different base.

## "Quirks" section (editor introspection)
- The note editor literally interprets whatever is at the TRKx address as notes — entering
  `$1000` (the editor's own code) shows the editor as garbage "notes"; editing it crashes the
  machine. Confirms: bars are raw RAM, no validation.
- Article confirms $3000–$9FFF + $B000–$BDFF usable for note data, and **$BE00 is an empty bar**.

## EDIT SOUND screen — the 24 sound-patch parameters (PRIMARY; transcribed verbatim
## from `edit_sound.png`, header "SOUNDMONITOR V1.0  EDIT SOUND NUMBER 01")

The screen lists the 24 bytes of a sound patch **in storage order**, each with the SID register
it feeds. This is the single most important artefact for the binary sound-bank layout. Left
column = the (example) hex value shown; right = the on-screen label (verbatim):

| # (offset) | label (verbatim)                          | SID target / meaning |
|------------|-------------------------------------------|----------------------|
| 0  | `waveform (keyon)`                                | control byte $D404 written **with gate ON** (the attack waveform+gate) |
| 1  | `attack/decay`                                    | $D405 (AD) |
| 2  | `sustain/release`                                 | $D406 (SR) |
| 3  | `portamento effectbyte`                           | portamento mode/effect selector |
| 4  | `pulserate`                                       | pulse-width sweep rate |
| 5  | `pulse EG count up time`                          | pulse "envelope-gen" up duration |
| 6  | `pulse EG count down time`                        | pulse EG down duration |
| 7  | `pulse EG count level`                            | pulse EG level/threshold |
| 8  | `waveform (waveoff)`                              | control byte used **with gate OFF / second waveform** |
| 9  | `pulse EG mode/portamento effect`                 | pulse-EG mode bits + portamento effect flags |
| 10 | `portamento level low`                            | portamento target/step LO |
| 11 | `portamento level high`                           | portamento target/step HI |
| 12 | `vibrato speed`                                   | vibrato rate |
| 13 | `vibrato level`                                   | vibrato depth |
| 14 | `vibrato delay`                                   | frames before vibrato starts |
| 15 | `fine detune`                                     | per-sound fine pitch offset |
| 16 | `filter (high nibble of sid reg24)`               | $D418 high nibble (filter mode bits 4-7) |
| 17 | `resonance/filter to voice (reg23)`               | $D417 (resonance hi nibble + filter-enable per voice lo nibble) |
| 18 | `filter cut off frequency`                        | filter cutoff (feeds $D415/$D416) |
| 19 | `filter EG count up time`                         | filter-cutoff "envelope" up duration |
| 20 | `filter EG count down time`                       | filter EG down duration |
| 21 | `f. EG count level low (up/down)`                 | filter EG level LO |
| 22 | `f. EG count level high`                          | filter EG level HI |
| 23 | `f. EG mode/trigger voice`                        | filter EG mode + which voice triggers/owns the (single) filter |

Notes / interpretation (cross-checked against the $C000 player disasm):
- There are **two waveform/control bytes** per sound (#0 "keyon" and #8 "waveoff"): the engine
  raises the gate with #0's value and uses #8 for the held/gate-off phase (a 2-state
  waveform/gate machine — explains the per-note gate-low-then-gate-high write pair seen in the
  writelog).
- The "pulse EG" (#4–#9) and "filter EG" (#18–#23) are **software ramp generators** the replayer
  runs each frame (up/down time + level + mode), not hardware envelopes — they drive $D402/03 PW
  and $D415/16 cutoff respectively. This is the engine's PWM + filter-sweep mechanism.
- Only ONE hardware filter exists; sound #17/#23 decide which voice owns it and the routing.

## References listed on the page (chase list mirrored to "Leads to follow")
- CSDb release 59929 (Soundmonitor V1.0)
- huelsbeck.com/credits/
- archive.org/details/64er_1986_10/  (the original magazine scan — the actual listing + German
  text incl. the memory-map table)
- VGMPF: Chris Hülsbeck / Soundmonitor
- C64-Wiki: 64'er, SID
- MOS 6581 datasheet / SID block diagram

## Sub-pages / assets on this page
- Images (all saved to `tmp/sm_research/img/`, transcribed above where load-bearing):
  `edit_sound.png` (24-param screen — transcribed), `track_step_table.png` (track/step screen —
  shows column layout + "sound options 4" legend + octave/keytranspose/arpeggio/begin-stop +
  "Typ: complete song / Load/Save"), `memory_map.jpg` (64'er Tabelle 1 — transcribed),
  `inception1/2.png` (editor-as-notes introspection), `soundmonitor.png`, `rockmon.png`
  (Rockmonitor V5 screen), `chris.jpg`, `64er.jpg`, `listing_page1.jpg` (page 1 of the hex dump),
  `c64.jpg`, `sid.png`, `crash.png`.
- No deeper sub-articles; it is a single long article. The article links to the references above.

## Leads to follow
- **archive.org/details/64er_1986_10/** — the actual magazine: get the *prose* around Tabelle 1
  (it almost certainly documents the SP step-parameter byte layout + AR/S byte format that the
  screenshots don't spell out). Highest-value remaining primary source.
- The TRACK/STEP screen image shows extra fields not in the prose: `quantize`, `record track`,
  `play: voice 1 2 3`, `octave`, `keytranspose`, `arpeggio on/off`, `begin/stop`,
  `first/last/loop step` + `steps:` — these are *editor* state but `first/last/loop step` and the
  per-row AR/S pointer imply the song header stores **first-step / last-step / loop-step** and a
  global tempo — confirm byte positions from the magazine + player init code.
