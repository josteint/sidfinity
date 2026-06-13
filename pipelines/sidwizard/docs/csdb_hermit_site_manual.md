# SID-Wizard — Hermit's site + Official User Manual (format-relevant digest)

> **Provenance**
> - **source_url (primary):** `https://www.c64.cz/data2/download/x11/113614/SID-Wizard-1.4-UserManual.pdf`
>   (full 27-page *SID-Wizard 1.4 User Manual* PDF, author-written; identical text to the
>   `SID-Wizard User Manual.pdf` hosted at `https://www.retrotime.hu/wp-content/uploads/2012/07/`)
> - **source_url (site):** `http://hermit.sidrip.com` (Hermit's homepage; older URL `http://hermit.netne.net`)
> - **source_url (project, for feature list):** `https://sourceforge.net/projects/sid-wizard/`
> - **fetched_via:** WebFetch (PDF downloaded to local tool-results cache, then read page-by-page
>   with the Read tool — WebFetch could not decode the FlateDecode streams); SourceForge via WebFetch.
>   `http://hermit.sidrip.com` itself returned **HTTP 522** (Cloudflare origin down) at fetch time and
>   could not be read directly — its content is reconstructed from the manual, SourceForge and CSDb.
> - **fetch_date:** 2026-06-13
> - **author:** Mihály Horváth (alias **Hermit**), Hungary — SIDRIP Alliance / Samar / Singular.
> - **content_date:** Manual = 2013 (covers up to v1.4; v1.2 "new features" section embedded).
>   SourceForge feature list last-updated 2021-01-02.
> - **reliability:** HIGH — author-written primary documentation. The manual is the authoritative prose
>   spec for the SWM format's musical semantics. (Binary byte-offsets live in the sibling source-mined
>   `research.md` / `*_swm_format.md`; this doc covers the **semantics** of those bytes.)

---

## 0. Identity & where things live

- **SID-Wizard** = native C64 tracker / SID-music editor by Hermit. Open-source from the 1st release
  (WTF license). Goal: "a comprehensive native C64 tool for SID music creation" with the features other
  editors lacked (per-instrument table save/load, multi-speed, detuning, jamming, keyboard-tracking).
- Inspirations Hermit names: **Goattracker, SDI, X-SID, SID-Factory, JCH Editor, DMC, Hardtrack Composer.**
  Pattern-FX numbers $01/$02/$03 (slide up / slide down / tone-portamento) are **deliberately identical to
  Goattracker's** FX numbers; multi-speed call convention copies **X-SID/SDI** (NOT Goattracker — see §8).
- Hermit's homepage at time of manual: `http://hermit.netne.net`; now `http://hermit.sidrip.com`.
  Email in manual: `hermit@upcmail.hu`. CSDb scener id 18806; GitHub moved to `github.com/hermitsoft/`.
- **Third-party docs (LEADS):**
  - Mikael Norrgård, *"Creating Chip Tunes with SID-Wizard"* (e-book) —
    `http://www.witchmastercreations.com/e-book-creating-chip-tunes-with-sid-wizard/`
    (this is the "Manualzz / Creating Chip Tunes" hit from search).
  - Akaobi (Takashi Kawano) — Japanese User Manual.
  - Ant1 newbie tutorial — `http://chipmusic.org/forums/topic/8104/c64-music-for-dummies-c64-tutorial/`

---

## 1. Driver / player variants — the size/feature tradeoff table (CORE for SIDfinity)

All variants use the **same SWM1 module format** but a **slightly different SID sound-engine
(player/driver routine)**. The startup menu (and SID-Maker exporter) selects which one to compile/embed.
Purpose of light/medium is to **reduce player-code size and rastertime consumption**; **extra** is the
biggest but best-quality, "well suited for standalone music releases". (Manual §2.2, the feature matrix.)

Editor+graphics ≈ 14 kB together; **player-code ≈ 2 kB (or a little more)**. "Virtually no zeropage usage"
— the player saves/restores 2 zeropage bytes (default **$fe and $ff**), so it doesn't interfere with a host
program.

**Feature → variant matrix** (X = present). Manual labels the columns **Light / Medium / Full / Extra**
(the "Full" column = the "normal" driver):

| Feature | Light | Medium | Full | Extra |
|---|---|---|---|---|
| Calc.vibrato, Detune, Chord-table, Transpose, instr.Octave, WF-arp. speed | | X | X | X |
| PW/filtertable-reset off, filter keyboard-track, **11-bit filter**, tempo-program | | X | X | X |
| Vibrato-types, Hard-restart types, **Frame1 $09 waveform switch** | | | X | X |
| Pulsewidth keyboard-tracking, Note-off table-pointers | | | X | X |
| Subtune-jump FX (now independent on tracks), Saving/Restoring zeropage | | | X | X |
| Filter/Pulsewidth/WF-program slides never skipped, **filt-ex.FX, Ghost-reg.** | | | | X |
| **Tempo (0..2) full support**, vibrato returns after portamento, **delay note/track** | | | | X |

Notes that fall out of this table (load-bearing for the rebuild):
- **"Ghost-reg."** (the RAM shadow/ghost-register write buffering described in `research.md`) is an
  **EXTRA-only** feature. Light/Medium/Full may write SID more directly.
- **`$1D` delay-track / `$1E` delay-note** BIG-FX (§5 below) are **EXTRA-only** ("delays are only present
  in 'extra' version").
- **Tempo values 0..2** (the very fastest tempos) are **fully supported only in Extra**.
- **filter-external-switch FX (`$1F`) + the external filter ($D417 channel-filter bits)** are EXTRA-tier.
- **Frame-1 $09 waveform switch** (the configurable 1st-frame waveform; until v1.2 hardwired to $09 = the
  test+gate combo) requires Full or Extra.
- v1.0/v1.1 light/medium players consume **max $14..$19 rasterlines**; full/normal player needs
  **~$1A..$1C rasterlines** (see §8).

SourceForge calls the driver set: **bare / light / medium / normal / extra** (5 variants — "bare" is the
smallest below "light"; the manual's matrix shows the upper 4).

---

## 2. SID register model the engine targets (manual §3.3)

Plain restatement of the $D400 write targets the engine drives (no built-in freq table — **pitches are
computed in code**, manual stresses this twice):

| Reg | Meaning | SID-Wizard remark |
|---|---|---|
| $D400/$D407/$D40E | Voice 1/2/3 freq LO | no freq-table in SID; computed by player code |
| $D401/$D408/$D40F | Voice 1/2/3 freq HI | |
| $D402/$D409/$D410 | Voice 1/2/3 pulse-width LO | |
| $D403/$D40A/$D411 | Voice 1/2/3 pulse-width HI (nibble) | |
| $D404/$D40B/$D412 | Voice 1/2/3 waveform+control | gate=1, sync=2, ring=4, test=8; $11 tri / $21 saw / $41 pulse / $81 noise |
| $D405/$D40C/$D413 | Voice 1/2/3 Attack/Decay | |
| $D406/$D40D/$D414 | Voice 1/2/3 Sustain/Release | |
| $D415 | Filter cutoff LO (3 bits) | |
| $D416 | Filter cutoff HI (8 bits) | **common to all channels** |
| $D417 | Resonance + per-channel filter-switch nibbles | resonance common; filter-switch per channel |
| $D418 | Filter band-mode + main volume | HP $40 / BP $20 / LP $10 (combinable $30/$50/$60/$70) |
| $D41B/$D41C | (read) V3 osc / V3 env output | read for the oscilloscope display |

**Filter is handled automatically per-track**: only tracks whose current instrument has a non-empty
filter-table get filtered; an instrument with **$00 in its filter-table 1st row is *filtered* but does NOT
control the filter**; a non-zero 1st row means that instrument *controls* band/resonance/cutoff. "Always the
latest note (with a filtered instrument) takes over control" (polyphonic-jam style, like JCH editor).

---

## 3. Instrument parameters (manual §III.1) — semantics of every field

**Main instrument-settings:**
- **ADSR** — the normal envelope Attack/Decay/Sustain/Release.
- **ADHR** — the **hard-restart ADSR** value; loaded into the ADSR registers **1–2 frames before** a new
  note triggers.
- **1st-frame waveform** — settable only if switched on (toggle via Return). **Until v1.2 this was
  hardwired to $09**; from v1.2 it can be any value (except 0 in SWM1). [→ this is the `Frame1 $09 waveform
  switch` Full/Extra row.]
- **Hard-restart timer** — 0..2 = number of frames of hard-restart before note-trigger.
- **Hard-restart type** — Normal, or **Staccato/aggregated** (also resets the Test-bit at hard-restart,
  adding 1–2 frames of emphasized gap between consecutive notes).
- **Vibrato amplitude, frequency**, and **delay / increment-speed** (the latter when using an *increasing*
  vibrato type).
- **Vibrato-type** — one of: **incremental ('violin' style)**, delayed **up-down**, delayed **upwards**,
  delayed **downwards**. (Selectable BIG-FX `$16` values: **$00 / $10 / $20 / $30**.)
- **Instrument-table & chord-table execution speed** — the arp/chord speed. **Multispeed gating thresholds
  (HARDCODED, load-bearing):**
  - value **> $40** → the **pulsewidth-table** runs at multispeed for this instrument;
  - value **> $80** → the **filter-table** also runs at multispeed.
  (i.e. bit6 = multispeed PW, bit7 = multispeed filter — matches `research.md` offset-7 note.)
- **Default Chord** — linked to the instrument by default; a pattern-FX can override it.
- **Octave shift** — 2's-complement transpose so bass/lead share one instrument.

**Waveform-arpeggio-detune table (3 columns: WF / ARP / DETUNE):**
- **WF column:**
  - `$00..$0F` — **Repeat** current arp+detune row for **1..16 frames** (no waveform change).
  - `$10..$FD` — **set the WAVEFORM/CONTROL register** ($D404-style value) directly.
  - `$FE` — **Jump** to a table-position (target in the ARP/2nd column; **if target ≥ $40 it jumps to
    itself** = a hold/loop-in-place).
  - `$FF` — **End** of table (table execution stops here).
- **ARP column** (the 2nd column; doubles as jump-target operand for `$FE`):
  - `$00` — zero pitch-shift (prime); regain the original note-pitch.
  - `$01..$5F` — relative pitch-shift **upwards** in halftones.
  - `$7F` — **Jump to the default chord, or the pattern-FX-set chord.**
  - `$80` — **No process** (leave pitch & detune untouched; just do the waveform).
  - `$81..$DF` — **set ABSOLUTE pitch** (frequencies identical to notes C-1..A-8).
  - `$E0..$FF` — relative pitch-shift **downwards** (negative interval).
- **DETUNE column:**
  - `$00..$FE` — set fine-detuning amount.
  - `$FF` — **No process** (retain previously set detune value).

**Pulsewidth-program table (3 columns; PW-cmd / value / KT):**
- `$8x..$Fx xx` — **set square-wave pulsewidth** directly (hi-nibble in col1 `8..F`, low-byte = `xx`).
- `$00..$7F xx` — **add/subtract the signed `xx` value `0..127` times** (sweep). (`xx` $00..$7F positive,
  $80..$FF negative.)
- `$FE` — Jump (target in 2nd column; can jump to itself).
- `$FF` — End.
- **3rd column = Keyboard-tracking (KT)** — makes pulsewidth note-pitch-dependent (Korg MS20/707 style).

**Filter-program table (3 columns; filt-cmd / value / KT):**
- `$8r..$Fr XX` — **Case 1: set filter parameters.**
  - 1st nibble `8..F`: filter band — `9`=lowpass, `A`=band-pass, `B`=hi-pass, `C`(? manual lists)…
    manual's explicit list: **`9`=lowpass, `A`=band-pass, `B`=hi-pass** (LP/BP/HP), plus combinations;
    note `D`=notch (lo+hi) per the band combos. *(Exact nibble→band map: the manual example "9F 38" =
    low-pass with $F resonance, cutoff hi-byte $38.)*
  - 2nd nibble `r`: **resonance** strength.
  - `XX`: **cutoff frequency hi-byte.** **If `XX` is in $80..$8F range, the second nibble of XX sets the
    per-channel filter-switches instead.**
- `$00..$7F XX` — **Case 2: add/subtract signed `XX` to the filter-cutoff register every frame, 0..127
  times** (sweep; uses the **full 11-bit** filter cutoff).
- `$FE` — Jump; `$FF` — End.
- **3rd column = Keyboard-tracking** of cutoff frequency (cutoff becomes pitch-dependent).

**Gate-off table-pointers** (Full/Extra): separate pointers (WF / PW / filter) for the **release phase** —
when a note's gate goes off, table execution can jump to a release-section of each table. (Maps to
`research.md` offsets $0C/$0D/$0E "Gate-off WF/PW/filter ptr".)

---

## 4. Pattern format — note-column + instrument-column effects (manual §III.2.1-2.2)

A pattern row has up to **4 columns**: (1) Note/note-FX, (2) Instrument/Small-FX, (3) Big-FX type,
(4) Big-FX value. Empty rows are run-length-compressed on save ("packed rest / packed NOP").

**Note-column** holds pitch + simple gating switches (placed via keyboard combos, shown graphically):
note-on/off, **Sync ON/OFF, Ring-mod ON/OFF, tone-portamento ON**, and **vibrato** (the only one with a
1-nibble 0..F amplitude value).

**Instrument-column** holds either an instrument-select or a **Small-FX** (1st nibble = type, 2nd = value).
These numbers are deliberately the same as the effect-column Small/Big numbers:
- `$01..$3E` — **Select instrument** (stays selected until a new one comes).
- `$3F` — **Tied note** (true legato: instrument does NOT restart, only the note-pitch changes).
- `$40..$4F` — **Waveform (reg.4) nibble** adjust (a later WF-table change overrides it).
- `$50..$5F` — **Sustain** nibble adjust (ADSR).
- `$60..$6F` — **Release** nibble adjust (SID reg.6 / ADSR).
- `$70..$7F` — **Select Chord** (override default; pair with `$7F` in the ARP-table to call it).

---

## 5. Effect-column — SMALL effects ($x with value-nibble) and BIG effects ($xx + value byte)

**SMALL effects (effect-column; 1st nibble type, 2nd nibble value).** $4..$7 are identical to BIG $04..$07:
- `$20..$2F` — **Attack** nibble adjust (ADSR).
- `$30..$3F` — **Decay** nibble adjust (ADSR).
- `$40..$4F` — **Waveform (reg.4)** nibble adjust (later WF-table change overrides).
- `$50..$5F` — **Sustain** nibble adjust.
- `$60..$6F` — **Release** nibble adjust.
- `$70..$7F` — **Select Chord** (override default).
- `$80..$8F` — **Vibrato Amplitude** adjust (frequency unchanged).
- `$90..$9F` — **Vibrato Frequency** adjust (amplitude unchanged).
- `$A0..$AF` — **Main volume** (low nibble of $D418).
- `$B0..$BF` — **filter Band-nibble** of $D418 (LOW/MID/HI/3OFF).
- `$C0..$CF` — **Chord-speed** adjust (arpeggio speed when explicit arp).
- `$D0..$DF` — **Detune** the actual note by the given amount.
- `$E0..$EF` — **Enable/disable Test/Ring/Sync/Gate bit** (a WF-table command can override).
- `$F0..$FF` — **Filter Resonance** (strength) nibble (a later filter-table command can override).

**BIG effects (effect-column type byte + 1-byte value $00..$FF, or signed -$7F..+$80 in the 4th column).**
$04..$07 == Small versions of same range:
- `$01` — **Pitch Slide UP** (same FX-number as Goattracker).
- `$02` — **Pitch Slide DOWN** (same FX-number as Goattracker).
- `$03` — **Tone-portamento** with given speed (same FX-number as Goattracker).
- `$04` — Simple **Waveform-control ($D404 etc.)** setting.
- `$05` — **Attack/Decay** ($D405) byte adjustment.
- `$06` — **Sustain/Release** ($D406) byte adjustment.
- `$07` — **Select Chord** (override default).
- `$08` — **Vibrato amplitude+frequency** (overrides instrument default vibrato).
- `$09` — **Go to Waveform-arpeggio table-index** for the current instrument.
- `$0A` — **Adjust Pulsewidth-program table-index** (jump to a table position).
- `$0B` — **Branch to Filter-program table-index** for the current instrument.
- `$0C` — **Chord-speed** adjustment.
- `$0D` — **Detune** actual note by given amount.
- `$0E` — Simple **pulsewidth** setting (instr.PW-table changes can override).
- `$0F` — Simple **filter cutoff-frequency** setting (takes keyboard-track into account).
- `$10` — Set **Main (subtune) basic single-tempo.**
- `$11` — Set **Main (subtune) funktempo** (1st/even-rows tempo in one nibble, 2nd/odd-rows in the other).
- `$12` — Set **Main tempo-program** for the whole subtune (arbitrary per-row speeds).
- `$13` — Set **Track's individual single-tempo.**
- `$14` — Set **Track's funktempo** (even/odd rows in left/right nibbles).
- `$15` — Set **Track's individual tempo-program.**
- `$16` — Select **vibrato-type** (values **$00 / $10 / $20 / $30**).
- `$17..$1B` — reserved for later expansions.
- `$1C` — **Filter-cutoff hi-byte SHIFT** (added to filter-freq). **Only a tune-init resets it!** (durable
  global offset — important for rebuild state.)
- `$1D` — **Delay track** by $00..$FF (20 ms) frames. **EXTRA version only.**
- `$1E` — **Delay only the actual note** by given frames (max value should be tempo − 3). **EXTRA only.**
- `$1F` — **Filter-switches (incl. external filter) + resonance** direct setting (register **$D417**).

---

## 6. Sequence / Orderlist format & effects (manual §III.3)

Per-track orderlist (3 independent tracks). Bytes:
- `$00..$7F` — normal **pattern numbers** (pattern $00 reserved = "no process"; lowest usable = $01).
- `$80..$8F` — **Transpose key DOWN** (`$8F` = −1 half-note … `$8E` = −2 … i.e. down by 16−lownibble).
- `$90` — **Switch off transposing** (back to original key).
- `$91..$9F` — **Transpose key UP** (`$91` = +1 half-note, `$92` = +2 …).
- `$A0..$AF` — **Set main volume** ($0..$F).
- `$B0..$FD` — **Set track-tempo** on this track (range equivalent to tempo $00..$5D).
- `$FE` — **End** of playback for this track.
- `$FF` — **Loop/jump.** The position number **following** `$FF` controls it:
  - a number **< $80** after `$FF` ⇒ **loop to that position** in the current subtune;
  - a number **≥ $80** after `$FF` ⇒ **jump to subtune `(number − $80)`'s** corresponding track/sequence
    (the "jump to other subtune" feature, for composing in small chunks / demo-parts).
- **Subtune-jump is per-track** — to jump a whole subtune you write the command on **all 3 tracks**.
  At a subtune-jump the **current tempo is retained** unless the target subtune applies a tempo-change FX.
  (Default subtune-tempo only takes effect on a fresh tune-start.)
- **Caveat:** an Orderlist-FX immediately before a `$FF` loop-signal is **ignored** (anti-freeze guard).

---

## 7. Chord-table & Tempo-program table (manual §1.5, §1.6)

- **Chord-table** = shared arpeggios (pitch-lists in halftones, 2's-complement). Any instrument can call a
  chord (avoids making a new instrument per chord). Per-chord terminators:
  - `$7F` — **loop the chord** over;
  - `$7E` — **return** to the WF-arpeggio table (resume the calling table at its next row).
  - Called from the WF-ARP table via the `$7F` ARP-column code, or set by pattern-FX `$70-$7F` / `$07`.
- **Tempo-program table** = per-row timing list (funktempo/swing/complex rhythm). **No value > $7F allowed.**
  Auto-loops after the last row (no jump command needed). Selected via pattern-FX `$12`/`$15`.

---

## 8. SID export / player application note (manual §IV.3, §V.5) — DIRECTLY load-bearing for SIDfinity

**SID-Maker** is a **separate C64 executable** (relocation can't be done in the editor's own memory). It
packs/relocates/exports. Outputs **4 formats**: `.C64.PRG` (normal C64 PRG), `.BIN.SEQ` (raw data),
runnable `.EXE.PRG`, and `.SID.SEQ` (**PSID/SID file**). Options on the SID-Maker screen:
- **Player-type via cursor LEFT/RIGHT** (normal / light / medium / extra — chooses the driver variant).
- **Machine-type via cursor UP/DOWN** (PAL/NTSC).
- **Relocation address via +/- keys** (e.g. $4C00; **extended relocation range $0200..$FFFF** since v1.2).
- **SID-model via cursor** (6581 / 8580).
- Author-info containing a **`:`** is split → text **before `:`** = author-name, **after `:`** = song-title
  in the SID header. (v1.92 PC build also adds a Date field.)
- Module **SWM version must match SID-Maker software version.**
- On `SAVE ERROR` (no 1541), export as plain `.C64.PRG` instead (skips SEQ). If a relocation address is set
  for PRG/SID and the exporter falls back, the **load-address is forced to default $1000 (or $0F82 for SID)**
  while the code itself is relocated — must then be patched by hand.

**Player call convention (manual §V.5 — the embedded-player ABI):**
- Player **init/caller address == the base/load-address** (e.g. `$1000`); **subtune number in the
  Accumulator** (as usual for PSID).
- **Single-speed play = init-address + 3** (e.g. `$1003`).
- **Multi-speed play = init-address + 6** (e.g. `$1006`). The multi-speed call convention is done the
  **X-SID/SDI way, NOT Goattracker's** — multi-speed routine calls happen at base+6 on the extra
  rasterlines (and use much less rastertime than the single-speed call). [CIA-timed multispeed; matches
  `research.md`.]
- **External volume change = init-address + 9** (e.g. `$1009`): put desired volume 0..F in A and call.
- Player uses **2 zeropage bytes (default $fe, $ff)**, saved+restored, so it's safe inside a host program.
  (Restoring zeropage is a Full/Extra feature — see §1.) Zeropage location configurable via `PLAYERZP_VAR`
  in `settings.cfg`.
- **Rastertime:** normal/full player ≈ **$1A..$1C rasterlines**, varying with #effects & #table-commands
  used per frame; **light** player max **$14..$19**. Drops significantly if <3 tracks are used.

**File formats around the editor:**
- **`.SWM`** = native optimized/compressed workfile (12-char filename limit; editor auto-appends `.SWM`).
  Contains the `SWM1` filetype+version string so the editor detects version mismatches. NOT compatible
  with other editors.
- **`.SWI`** = a single exported instrument (one instrument minus empty/unused space).
- **SWMconvert** (PC Win/Linux CLI, "SID-Wizard SWM module v1.0 converter") converts **SWM ↔ XM / MID**,
  `.swm.prg ↔ swm.P00`, and **`.S00` (VICE) → `.sid`**. Limits: XM↔SWM only carries **tracks 1..3** and
  they should be monophonic for clean conversion; XM lacks tempo-programs / variable pattern-lengths; SWM
  chords expand to more XM/MIDI tracks. MIDI→SWM reads the time-signature (default 4/4) and reuses repeated
  patterns; tempo-changes (incl. from orderlist) are handled.
- **`sng2swm`** — converts Goattracker `.sng` → SID-Wizard `.swm` "with good precision" (co-dev Conrad/Samar).

---

## 9. Version-relevant feature deltas captured in the manual

- **v1.0** — first release (open-source from day 1). Grammar cleanup by Dóra Kőrösi.
- **v1.2 — significant format-affecting changes:**
  - NTSC machine auto-detect (sets graphics + **frequency-table** for the machine).
  - **1st-frame waveform register now configurable** (was hardwired $09 in SWM1).
  - DMC/GT note-keyboard modes; configurable colour-themes; rasterbars hideable; instrument-autotyping.
  - **Copy/Paste in Orderlist-sequences**; **Ctrl+E find-empty-pattern**.
  - Negate values with `=` key in tables (`$40` → `$C0`).
  - SID-Maker: author-info moved to reused memory; faster relocation; **exe.prg can switch subtunes**;
    **extended relocation range $0200..$FFFF**; **normal vblank-synced SID output for single-speed tunes**.
  - **Startup menu with selectable players** (normal/light/medium/extra) — see §1 matrix.
- **v1.4** — `sng2swm` converter; F2 playback processes preceding effects; more pattern-effects;
  player-info (size, rastertime) shown in startup menu; author-info shown in row 26; `C=` + +/- octave-select.
- **HerMIDI** (MIDI-input hardware over the C64 serial port, device 15) was planned for **v1.5** — kept out
  of v1.4 so the v1.4 player is clean of it.

*(V1.7 → V1.92 → V1.93 release-level notes are in `csdb_releases.md`.)*
