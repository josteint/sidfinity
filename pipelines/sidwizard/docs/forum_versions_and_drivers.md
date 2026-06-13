# SID-Wizard — Version timeline (V1.0→V1.92) + driver-variant matrix (forum/wiki cluster)

> **Provenance**
> - **source_url (releases):** CSDb release pages —
>   V1.0 RC `https://csdb.dk/release/?id=109698`, V1.4 `…?id=115599`, V1.7 `…?id=131846`,
>   V1.91 `…?id=220489`, V1.92 `…?id=221555` (and the later 1.93 `…?id=255544`, 1.94 `…?id=258573`).
> - **source_url (manuals):** SID-Wizard **1.4** User Manual (`https://www.c64.cz/data2/download/x11/113614/SID-Wizard-1.4-UserManual.pdf`, 27 pp, complete)
>   and **1.5** User Manual (`https://csdb.dk/getinternalfile.php/125509/SID-Wizard-1.5-UserManual.pdf`, fetched fragment, 5 pp).
> - **fetched_via:** WebFetch for CSDb release pages; PDFs downloaded to the tool-results cache then
>   read with `pdftotext -layout` + the Read tool (WebFetch could not decode the FlateDecode streams).
> - **fetch_date:** 2026-06-13
> - **author/handle:** Hermit (Mihály Horváth); release dates per CSDb.
> - **content_date:** 2012 (V1.0) → 2022 (V1.92).
> - **reliability:** secondary (author-written manuals + author release notes on CSDb).
>
> *(This file deliberately carries the **1.5-manual delta** — Bare player, tunings, 2SID 'sws' —
> which the sibling `csdb_hermit_site_manual.md` does not, since that doc is built on the 1.4 manual.)*

---

## 1. Release timeline (what each version added — load-bearing for version-discrimination)

| Version | Date (CSDb) | Key additions relevant to parsing / write-model |
|---------|-------------|--------------------------------------------------|
| **V1.0 RC** | 2012-07-07 | First release. `.SWM` workfile; SID/XM/MID conversion. Hermit: *"no time for thorough tests … chance to spread SID-Wizard in box at Arok Party."* Known issue: *"Avoid FF jumps to itself"*, exporter relocation could be skipped. |
| **V1.2** | 2012 | NTSC support (auto freq-table); **1st-frame waveform now settable** (was hardwired `$09`; `0` reserved for compat in SWM1); **startup-menu player select: normal/light/medium/extra**; SID-Maker author-info moved to reused memory; extended relocation range `$0200…$FFFF`; vblank-synced output for single-speed tunes. |
| **V1.4** | 2012-08-31 (mft.) / 2013 (manual) | `sng2swm` (GoatTracker `.sng` importer); F2 playback processes preceding effects; **player size/rastertime shown in startup menu**; author-info in row 26. Manual finalised. |
| **V1.5** | 2013 (manual) | **2SID (stereo) version — workfile format `.sws`**; **new smaller "Bare" player type**; **Tunings: Verdi (A4=432 Hz, equal-tempered) + Just-intonation**; SDI & Janko keyboard layouts; **Sound-FX (SFX) support**; MIDI-in (HerMIDI + many cartridges); config-file for editor settings; one-step Undo; *"Less audible player-initialization pop."* |
| **V1.7** | 2014-07-12 | **3SID version (3 SID chips)**; **SWP — relocatable music-data + player** (relative addresses only); **tape-slowdown effect in player**; independent orderlist-marks (`C=+SPACE`); insert entire orderlist column (`C=+DEL`); fixes to filelister/player/2SID. |
| **V1.91** | 2022-08-08 | Bug fixes (pattern-length corruption after Ctrl+X; emulator freeze on F3; Alt+F9 restart). **No 4SID yet.** Hermit: *"I don't know a way to store SID4 address in SID-header…"* |
| **V1.92** | 2022-09-04 | **Full 4SID support** via *"the new WebSID SID-format proposal"* (NON-standard header — see `forum_multisid_writemap.md` §3); `-O2` GCC build (*"CPU-usage nearly halved"* on the PC emulator side); pattern-finder across all subtunes (`C=+E`); native 4SID PRG for C64 + Mega65; NTSC auto-detect + border positioning. |
| (V1.93 2025-08-22 / V1.94 2026-01-09) | later | sinc-resampler + cRSID-1.56 engine improvements (PC-side emulator quality; not C64 player-format changes). |

**Format-version rule (Hermit, manuals):** the `.SWM` carries a *"'SWM1' filetype&version string"*; the
module-version **must match** the editor's / SID-Maker's software-version — *"SWM module-version needs to
match SID-Maker software-version."* So a version mismatch is a hard error, not a soft-parse.

**Discriminators for SIDfinity:**
- A tune using a settable 1st-frame waveform ≠ `$09` ⇒ ≥ V1.2 module.
- 2SID (`.sws` / PSID v3) ⇒ ≥ V1.5; 3SID (PSID v4) ⇒ ≥ V1.7; 4SID (WebSID header) ⇒ ≥ V1.92.
- Verdi/Just tuning frequency tables ⇒ ≥ V1.5 (see §4 of this file).

---

## 2. Driver/player-variant feature matrix — the size/feature ladder

All variants share the **same `.SWM` module format** but a **slightly different player/driver routine**.
The startup menu (and SID-Maker exporter) picks which to compile/embed. The variant abbreviation
(**N / M / L / E / B** = Normal / Medium / Light / Extra / Bare) is stored in the **author-info** field
and shown in the orderlist position-row after load (1.5 manual). For SIDfinity this means the variant is
**recoverable from the author string** of the SID header, and it tells you which effects can appear.

### 2a. The 1.4-manual matrix (Light / Medium / Full / Extra), verbatim header row + rows:

```
Feature (in 'source/settings.cfg')                                        Light Medium Full Extra
Calc.vibrato, Detune, Chord-table, Transpose, instr.Octave, WF-arp. speed         X     X     X
PW/filtertable-reset off, filter keyboard-track, 11bit filter, tempo-program      X     X     X
Vibrato-types, Hard-restart types, Frame1 $09 waveform switch                           X     X
Pulsewidth keyboard-tracking, Note-off table-pointers                                   X     X
Subtune-jump FX (now independent on tracks), Saving/Restoring zeropage                  X     X
Filter/Pulsewidth/WF-program/slides never skipped, filt-ex.FX, Ghost-reg.                     X
Tempo (0..2) full support, vibrato returns after portamento, delay note/track                 X
```

### 2b. The 1.5-manual prose breakdown (adds **Bare**), verbatim:

- **Normal:** *"It probably has everything you will need: Calculated vibratos, Detune, Chord, Transpose,
  instrument octave, WF-ARP speed, Pulse/Filt.reset OFF, keyboard-track, 11bit filter, tempo-programs."*
- **Extra:** *"Based on 'Normal', adds extras (takes more memory & rastertime): program-tables never
  skipped, FiltSwitch-Reso.FX, **Ghost registers**, fast tempo (0..2), vibrato is not lost after
  pitch-slide, note/track Delay pattern-FX."*
- **Medium:** *"Smaller player-size but lacks: vibrato-type, hard-restart type, frame1 setting, PW
  keybrd-track, note-off index, subtune-jump FX and zeropage save/restore."*
- **Light:** *"Even smaller & consumes less rastertime, but lacks also: Calculated vibrato & slide,
  Detune, Chord-table, Transpose FX, Instrument-octave, WF-arp.speed, PW/Filt.reset OFF, keyboard-trk,
  11bit filter, tempo-programs."*
- **Bare:** *"Very restricted, significantly smaller size, less than 'Light'. Lacks: subtune-support,
  multispeed support, external volume-setting, filter-shift FX, orderlist-FX, portamento in note-column,
  WF-arpeggio NOP $80, vibrato-rate FX, filter/detune/WF small effects."*

### 2c. Cumulative capability ladder (derived from 2a+2b — what each variant CAN emit)

```
                        Bare   Light  Medium  Normal  Extra
calc. vibrato/slide      –      –       Y       Y      Y
detune / chord / transp  –      –       Y       Y      Y
instr.octave, WF-arp spd –      –       Y       Y      Y
PW/filt-reset-off, 11bit –      –       Y       Y      Y
filter keyboard-track    –      –       Y       Y      Y
tempo-programs           –      –       Y       Y      Y
vibrato-TYPES            –      –       –       Y      Y
hard-restart TYPES       –      –       –       Y      Y
settable frame-1 wf      –      –       –       Y      Y
PW keyboard-track        –      –       –       Y      Y
note-off table-pointers  –      –       –       Y      Y
subtune-jump FX          –      –       –       Y      Y
zeropage save/restore    –      –       –       Y      Y
multispeed               –      Y       Y       Y      Y
orderlist-FX             –      Y       Y       Y      Y
external volume-set      –      Y       Y       Y      Y
program-tables NEVER skipped / filt-ex.FX / GHOST-REG / fast tempo 0..2 / delay-FX:  Extra only
```

(*Note: Light/Medium DO have multispeed; only **Bare** drops it. The "Light lacks calc.vibrato" row of
the 1.4 matrix and the 1.5 prose agree. The 1.5 prose is authoritative for Bare, which 1.4 predates.*)

### 2d. Gotchas the ladder implies for the write-log verdict

- **Bare** has **no multispeed** → its `play()` is single-speed only; do not look for an `init+6` call.
- **Ghost/shadow registers** ("never skip program-table/slide writes") are an **Extra-only** behaviour
  per both manuals — **EXCEPT in the 2SID/3SID build**, where *"2SID version of SID-Wizard uses
  ghost-registers in all types of players"* (1.5 manual, verbatim). So a stereo Bare/Light tune still
  flushes via ghost registers. This changes whether per-frame writes are unconditional vs skipped —
  see `forum_player_internals_gotchas.md` §3.
- **Frame-1 waveform** is `$09` (hardwired) in Light/Medium and on any pre-V1.2 module; settable only in
  Normal/Extra (V1.2+). A `$09` first-frame waveform write is therefore the *default*, not a quirk.

---

## 3. Module limits per build (affects how much data the parser expects)

From the manuals:

| Limit | Mono (`.swm`) | 2SID (`.sws`, 1.5) |
|-------|---------------|--------------------|
| Instruments | 44 (also quoted as 50 / 37 in different versions) | **31** |
| Subtunes | 6 (also "16 = $0..$F" in 1.4) | **2** |
| Patterns (≤250-byte / 249-byte) | 100 | **105** |
| Max framespeed | 8× (400 Hz) | 8× |
| Chords | 64 | — |
| Tempo programs | 64 | — |

(The instrument/subtune counts drift between manual editions — 1.4 says "50 instruments, 100 patterns,
16 subtunes"; 1.5 says "44 instruments, 6 subtunes, 100 patterns". The mono **patterns=100** and the
**8× multispeed** are stable. Treat the exact instrument cap as version-dependent — read it from the
SWM header's instrument-count byte, don't hardcode.)

---

## 4. Tunings (V1.5+) — three frequency tables

From the **1.5 manual**, verbatim:

> "For PAL machines you can select an alternative pitch-tuning system in Start-up menu: Verdi tuning is
> equal-tempered but uses A4=432Hz as base-note, while Just-intonation even has note-intervals based on
> integer ratios to produce pure intervals in key of C. (not other keys)"

So three frequency tables exist:
1. **Standard** — A4=440 Hz equal-tempered (default; the built-in PAL/NTSC table).
2. **Verdi** — A4=432 Hz, still equal-tempered (whole table scaled by 432/440).
3. **Just-intonation** — non-equal-tempered, integer-ratio intervals in **key of C only**.

NTSC has its **own** standard table (auto-set since V1.2). The tuning is a *property of the rendered
frequency words*, not a separate write — but two SID-Wizard tunes with identical note data and different
tunings produce **different `$D400/$D401` frequency values**, so the comparator must compare against the
*same* tuning the original used. (Verdi/Just are PAL-only per the manual.)

---

## Cross-references
- Multi-SID write-address mapping + empirical HVSC header survey → `forum_multisid_writemap.md`
- Player call vectors, multispeed timing, hard-restart, ghost-register flush order → `forum_player_internals_gotchas.md`
- SWM byte-stream musical semantics (effects/instrument tables) → sibling `csdb_hermit_site_manual.md`
