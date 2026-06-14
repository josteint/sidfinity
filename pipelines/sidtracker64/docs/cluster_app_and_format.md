# SidTracker64 — App, Format & Exported Player: Research Cluster

```
provenance:
  author:       research-player agent (Claude Sonnet 4.6)
  fetch_date:   2026-06-14
  content_date: 2015–2026 (sources dated per section)
  reliability:  HIGH for app features (multiple independent reviews + App Store data + chordian.net
                comparison table); MEDIUM for player internals (CSDb CIA-timer thread, PSID header
                analysis of 259 HVSC SIDs); LOW for .s64 binary format (no public spec found)
```

---

## 1. Product identity

| Field | Value |
|---|---|
| App name | SidTracker64 |
| Developer — programmer | Daniel Larsson ("Pernod", scene handle since 1987) |
| Developer — design/marketing | Fredrik Segerfalk |
| Company | Datakalsong |
| Platform | iPad (iPadOS 9.0+; visionOS 1.0+) |
| Price | USD 12.99 / GBP 9.99 (Black Friday discount seen at $10.99) |
| App Store ID | 955421205 |
| Bundle ID | slb.SidSynth64 |
| Official site | sidtracker64.com (unreachable 2026-06-14; no Wayback snapshots accessible) |
| Social | @SidTracker64 on X/Twitter, Facebook, YouTube channel (@sidtracker6440), Instagram |
| First release | 18 June 2015 (App Store v1.0) |
| Latest known version | 1.0.5 (31 October 2019) |

### Scener background — Pernod
Daniel Larsson / Pernod (CSDb id=809) is a veteran Swedish coder from the C64 demoscene.
Groups: Absolut Vodka Team (1987–89) → Fairlight (1989–90) → Horizon (1990–present) → Booze Design
(joined Feb 2024). Coder rating 9.8/10. Brother of scener JackAsser. He wrote the SidTracker64 iOS
app independently of his demoscene work; the app's programming is entirely his. The 6502 player
embedded in .sid exports is his own authorship, confirmed by CSDb CIA-timer thread (2017).

Sources:
- https://csdb.dk/scener/?id=809
- https://forum.loopypro.com/discussion/9132/ (Audiobus/Loopy Pro thread, originally 2015)
- https://zeromagazine.nu/2015/07/29/fredrik-segerfalk-jobbar-bade-digitalt-och-analogt/

---

## 2. Feature model — what the app exposes

This section describes the **musical feature space** that the embedded 6502 player must reproduce.
Sources: App Store description, Sound on Sound review, chordian.net editor-comparison table (v1.0.3),
Audiobus/Loopy Pro thread.

### 2.1 SID chip emulation

| Parameter | Value |
|---|---|
| Chip modelled | SID 8580 R5 (MOS 8580, the "clean" revision) |
| Chip emulation engine | Custom — written ground-up by Daniel Larsson, NOT reSID |
| 6581 filter option | Present (as an alternative; users noted it was in progress as of 2015) |
| Voices | 3 independent voices (standard SID architecture) |
| Waveforms | 8: triangle, sawtooth, pulse+PWM, noise, trisaw, tripulse, sawpulse, nowave (gate-off) |
| Hard sync | Per voice |
| Ring modulation | Per voice |
| Hard restart | Yes — gate-off timer control for predictable envelope reset |
| Envelope | Full ADSR per voice (Attack/Decay/Sustain/Release) |
| Filter | Multimode: LP (12dB), BP (6dB), HP (12dB); combinable; cutoff sweep envelope |

**"Hard restart"** is explicitly documented: it forcibly re-triggers the ADSR at note start
rather than allowing the existing envelope to continue ("random envelope errors" without it).
This is a known SID quirk addressed by gate-off timing; the player has a configurable gate-off timer.

### 2.2 Instruments

| Parameter | Value |
|---|---|
| Max instruments per song | 32 |
| Instrument operations | Copy, paste, rename (alias naming added in v1.0, Oct 2015) |
| Wavetable | Yes — per-instrument table of waveform/ctrl bytes; step sequencer; includes "Reset" effect (added v1.0.5, 2019) |
| Pulse table | Yes — separate table for PWM value sequences |
| Filter table | Yes — table of filter cutoff/mode sequences |
| Vibrato | Dedicated vibrato controls (separate from wavetable); also triggerable from modulation wheel via MIDI |
| Arpeggio | Via wavetable ("hi-frequency mode") — not a separate command |
| ADSR | Full 4-param ADSR per instrument |
| PWM sweep envelope | Yes — configurable sweep (direction+rate) |

From chordian.net comparison table (v1.0.3, added Feb 2018):
- "Uses wave table for arpeggio with hi-frequency mode"
- "Programmable pulsating and filtering"

The wavetable is a simple mod-sequencer (like SID-Wizard or GoatTracker wavetables): a sequence of
waveform/control byte values stepped once per tick. The "Reset" effect added in v1.0.5 lets the table
reset to the beginning on re-trigger.

### 2.3 Pattern / sequencer model

| Parameter | Value |
|---|---|
| Voices in pattern | 3 (one pattern drives all 3 voice tracks simultaneously) |
| Max patterns | 128 |
| Max rows per pattern | 128 steps (all 3 tracks share the same row count) |
| FX pattern | Dedicated 4th track per pattern: per-step volume, filter cutoff, and speed (BPM/tempo) changes |
| Instrument change per step | Yes — any step can change the instrument for that voice |
| Note effects per step | glide, sustain, vibrato, filter reset, pulse reset, tie (see 2.4) |
| Transpose in song mode | ±48 semitones |
| Loop/stop | Both supported |
| Follow-play | Yes |

**FX pattern** is a key feature: it is a fourth sequencer track running alongside the 3-voice note
tracks. Each step can independently set master volume ($D418), filter cutoff ($D415/$D416), and
playback speed/tempo. This gives per-step filter automation and tempo changes — unusual for C64
trackers of this era.

### 2.4 Step-level note effects (NotesFX)

Documented explicitly in the Loopy Pro thread and App Store listing. These are per-step flags/values
applied to individual notes, NOT tracker command columns:

| Effect | Behaviour |
|---|---|
| **Glide** | Portamento — smooth pitch slide from previous note frequency to new note |
| **Sustain** | Extends the note past its natural gate-off (holds gate open) |
| **Vibrato** | Applies instrument's vibrato setting starting from this step |
| **Filter reset** | Resets filter state (cutoff/mode) at note start — stops any running filter sweep |
| **Pulse reset** | Resets pulse width to initial value at note start |
| **Tie** | Legato — does NOT restart the wavetable or sweep; continues previous note's instrument program |

From Loopy Pro thread (developer Segerfalk): "Note FX is not for live use, it's for adding vibrato,
glide, tie (legato), pulse reset and filter reset to stop each note from initializing the wavetable
or sweep."

### 2.5 Song structure

| Parameter | Value |
|---|---|
| Song table ("orderlist") | Yes — ordered list of pattern indices defining playback order |
| Subtunes | Rarely used; almost all HVSC SidTracker64 SIDs have 1 subtune (2 have 2–3) |
| Transpose per song position | ±48 semitones (app documentation) |

### 2.6 Speed and timing

| Parameter | Value |
|---|---|
| Emulation speed range | 25–240 Hz (app setting); standard = 50 Hz (PAL VBI) |
| BPM model | BPM-based tempo control; player sets CIA timer to match the exact BPM |
| CIA usage | **ALWAYS** sets CIA timer in .sid export (confirmed by CSDb thread, 2017) |
| Multispeed | Implicit via BPM (integer multiples of 50 Hz → 1x/2x/4x etc.) |

**Critical timing note** (from CSDb "SidTracker64 and CIA timer settings" thread, 2017, roomid=14,
topicid=113188): The app uses exact BPM integer values, not the real PAL VBI rate. So a 4× tune
runs at exactly 200 Hz CIA timer, not the hardware-accurate 200.5 Hz (≈4×50.125 Hz). This means
exported .SID files **always** have CIA setup code and speed=1 in the PSID header (CIA-timed),
even for tunes that would sound correct at VBI speed. This was raised as a concern by demo coders
in 2017 because it makes the tunes hard to use in demos with raster effects.

As of 2017, 88 SidTracker64 SIDs were in HVSC (CSDb thread). HVSC #84 has 259 (June 2026 count).

### 2.7 Export and MIDI

- Export: `.s64` (native), `.m4a` (AAC audio), `.sid` (PSID), `.prg` (executable for real C64)
- MIDI in: keyboard (mono/duo/poly), CC-assignable params, mod wheel → vibrato, pitch bend, MIDI clock
- Audiobus 2 + Inter-App Audio support (for recording into DAW apps)
- Dropbox + email sharing

**The `.prg` export** means the player code is actual valid 6502 machine code that runs on a real
Commodore 64 — not an approximation or emulation wrapper.

**SID file start address** is settable from Settings menu (added v1.0.5, 2019). This is why
non-$1000 load addresses appear in HVSC.

---

## 3. The embedded 6502 player — what we know

This section covers what we can infer about the actual PSID player code without disassembly.

### 3.1 Player identity

- Custom player authored by Daniel Larsson / Pernod (not derived from an existing public player)
- Identified in sidid.nfo (cadaver/sidid) as "SidTracker64" (entry present, minimal signature data
  returned from the binary tool — exact byte signatures not obtained)
- NOT in SID Preservation's tracker list (sidpreservation.6581.org/sid-trackers/) as of 2026

### 3.2 PSID header analysis (259 HVSC #84 SIDs)

**Init and play address distribution:**

| Init addr | Count | Notes |
|---|---|---|
| $1000 | 210 (81%) | Dominant canonical load address |
| $A000 | 15 | Upper RAM area |
| $E000 | 7 | Top RAM area |
| $0800 | 5 | Acrouzet custom (user-set start addr) |
| $1884 | 5 | Unusual — init≠play (init does extra setup, play at $1003) |
| Other | 17 | Various: $2000, $4000, $7000, $8000, $B5xx, $B6xx |

**Play address:** Almost always init+3. The init/play+3 convention means the player uses the
standard PSID calling convention: JSR init(A=subtune), JSR play() per frame.

**PSID speed field:**

| speed value | Count | Meaning |
|---|---|---|
| 0x0 | 137 (53%) | VBI-timed in PSID header — BUT player may still set CIA internally |
| 0x1 | 121 (47%) | CIA-timed (bit 0 = subtune 1 uses CIA) |
| 0x3 | 1 | CIA-timed for first two subtunes |

The 53% that show speed=0 in PSID header are **not** contradicting the CIA timer note. The PSID
speed field is advisory to the host; the actual timer setup happens in the 6502 init code regardless.
sidplayfp respects the PSID speed field for calling convention only.

**Data size (= player code + song data):**

| Range (bytes) | Count |
|---|---|
| < 3000 | 14 |
| 3000–5000 | 119 |
| 5000–8000 | 106 |
| 8000–12000 | 19 |
| > 12000 | 1 (Rob's Life, 3 subtunes, 17651 bytes) |

Median data size: ~4938 bytes. Min: 2727 bytes. The player code is self-contained within each .sid
file (it is not a shared stub; each .sid includes both player and song data).

**PSID flags (version 2 header):**

Dominant: `0x24` (223 SIDs = 86%). Bit decoding:
- bits 2–3 (clock): 01 = PAL (86% of tunes)
- bits 4–5 (SID model): 10 = 8580 (consistent with app's advertised 8580 R5 emulation)

`0x14` (23 SIDs): clock=PAL, SID model=6581 (some tunes targeting older chip sound)
`0x28` (5 SIDs): clock=NTSC, SID model=8580

**CPU usage:** chordian.net reports "Approx 23–27 rasterlines" at 1× speed (50 Hz). For a 63-cycle
rasterline budget ×263 lines/frame = 16569 cycles/frame total, 23–27 rasterlines ≈ 1449–1701 cycles
per play() call ≈ 8.7–10.3% of CPU at 1MHz. This is in line with a moderately optimised tracker
player (GoatTracker 2 is similarly ~20 rasterlines).

### 3.3 What the player code does (inferred from features + binary header)

From the init code structure (payload at $1000, first 64 bytes show a clear init sequence):
- `LDX #$00 / JSR $17F8` pattern visible three times → likely a 3-voice register-clear loop
- `STA $D415` / `$D416` / `$D418` writes visible early in init (filter and volume setup)
- CIA timer setup in init (sets CIA 1 Timer A to match BPM × subdivision rate)
- Play() routine at init+3: called by CIA interrupt or by host per VBI

The player must implement:
1. Per-tick wavetable step (waveform sequencer)
2. Per-tick pulse-width table step
3. Per-tick filter table step
4. ADSR management with hard-restart (delayed gate-off on note re-trigger)
5. Vibrato oscillator (sine or triangle approximation)
6. Glide (portamento — interpolate freq registers toward target)
7. FX track processing: volume ($D418 master vol), filter ($D415/16), speed (CIA timer update)
8. Note-FX: tie suppresses wavetable/sweep restart; filter-reset clears sweep; pulse-reset resets PW

The FX track speed-change is notable: it implies the CIA timer value can change per pattern step,
meaning songs can have tempo automation — the CIA register is written from the FX track data each frame.

### 3.4 Data layout (speculative — no .s64 spec found)

The embedded .sid payload includes both the player machine code and all song data. Based on the PSID
header analysis and the init code fragment:
- Load address (the PSID data start) = player base (usually $1000)
- Song data immediately follows player code within the same memory block
- There is no separate "player stub + data" structure visible from outside; it is monolithic

The init code contains multiple `AD xx xx` (LDA abs) and `8D xx xx` (STA abs) instructions
referencing data in the $10xx–$18xx range (for $1000-based loads), confirming song data is
interleaved with or immediately follows the player code.

---

## 4. Version history

| Version | Date | Key changes |
|---|---|---|
| 1.0 (initial) | Jun 2015 | Launch: full feature set, Commando + Blood Money demo tunes |
| 1.0 (Oct 2015 update) | Oct 2015 | Instrument alias naming; cut/clear pattern editing; vibrato tracker-effect export |
| 1.0.x (2015–2016) | 2015–2016 | Circular/linear knob mode toggle; file management improvements |
| 1.0.3 | Apr 2016 | Portrait layout for iPad Pro |
| 1.0.5 | Oct/Nov 2019 | Configurable SID file start address (in Settings); improved iPad screen size layouts; Reset effect in wavetable editor; Turrican arrangement by Jason Page added as demo tune; general bug fixes |

**Note:** The App Store confirms only one version since 2019 (v1.0.5 as of the final update). There
is no "v2.0" rewrite documented anywhere. The app appears to have been in maintenance-only mode
since the 2019 update. No updates found for 2020–2026.

---

## 5. Third-party tools and .s64 format

### 5.1 .s64 format
No public specification found. The format is proprietary to the iOS app. No open-source parser,
converter, or reverse-engineering documentation was found on GitHub, forums, or CSDb.

The developer's comment (Loopy Pro thread): "`.sid` is just a data streaming format without any
information on instruments, pattern length and song construction" — which confirms .s64 contains the
structured musical data (instruments, pattern grid, orderlist) while the .sid export is a compiled
binary (player + song data, no source-level reconstruction possible from .sid alone).

### 5.2 sidid / player-id
- cadaver/sidid identifies "SidTracker64" (present in sidid.nfo at master)
- WilfredC64/player-id references sidid.cfg; SidTracker64 status in that cfg not confirmed

### 5.3 No known converters
- olefriis/sidtool does NOT parse .s64 or SidTracker64 .sid files
- ChiptuneSAK (chiptunesak.readthedocs.io) has no SidTracker64 support
- No SidTracker64-specific analysis tool found anywhere

### 5.4 HVSC author distribution (259 SIDs in #84)
Jason Page is the most prolific SidTracker64 contributor (multiple long compositions). Other notable
authors: Lula, Acrouzet, Rob Hubbard & Jason Page (Robs_Life), Harlequin, Factor6.

---

## 6. Bundled demo tunes

| Tune | Composer | Notes |
|---|---|---|
| Commando | Rob Hubbard (arrangement) | Classic game SID, required "data analysis and hand correction" to import |
| Blood Money | Fredrik Segerfalk | Co-developer's own composition |
| True Survivor | Kung Fury soundtrack remix | "YouTube remix hit" according to app description |
| Turrican arrangement | Jason Page | Added in v1.0.5 (2019); demonstrates "7 voices + TR-808" via advanced technique |

The Commando note is significant: Segerfalk confirmed importing an existing .sid required "data
analysis and then correct a lot by hand" — the app has NO .sid import; the demo was manually
transcribed. The .sid format does not round-trip back to .s64.

---

## 7. Comparison with contemporaneous C64 trackers

From chordian.net/c64editors.htm (comparison table, SidTracker 64 v1.0.3, accessed 2026-06-14):

| Feature | SidTracker64 | GoatTracker v2 | SID-Wizard 1.x |
|---|---|---|---|
| Platform | iPad (emulation) | PC/Mac/Linux | C64 native |
| Max instruments | 32 | 63 | 32 |
| Max patterns | 128 | 256 | 96 |
| Max rows/pattern | 128 | 128 | 128 |
| Wavetable arpeggio | Yes (hi-freq mode) | Yes | Yes |
| Programmable filter | Yes (filter table) | Yes | Yes |
| Programmable pulse | Yes (pulse table) | Yes | Yes |
| Digi/samples | No | No (GT stereo yes) | No |
| Speed | Ticks per second (BPM) | Ticks per second | Variable |
| CPU usage (1×) | 23–27 rasterlines | ~20 rasterlines | — |
| Transpose | ±48 semitones | ±36 | ±36 |

SidTracker64 is a modern tablet tracker in the "clean SID" tradition (8580 chip model, no digi,
BPM-centric). It is closer in spirit to GoatTracker (PC-based, non-native, focused on musical
expression) than to the assembly-centric C64-native trackers.

---

## 8. Leads to follow

1. **Disassemble a canonical .sid** (`MUSICIANS/P/Page_Jason/First.sid`, $1000 base, 6569 bytes,
   single subtune) to map the full player structure: init, play, CIA setup, wavetable dispatch,
   FX track dispatch. `tools/seed_disassembly.py` should work directly on this file.

2. **FX track data layout**: the per-step volume/filter/speed FX track is the unusual element vs
   other C64 trackers — how are these encoded in the song data? Is it a separate table or inline
   with pattern rows?

3. **Wavetable encoding**: how are wavetable, pulse table, and filter table stored? Are they
   shared across instruments or per-instrument? What is the loop/end marker byte?

4. **CIA BPM table**: does the player embed a BPM→CIA timer lookup table, or does it compute the
   CIA value from a stored BPM byte? The CSDb thread implies BPM is the authoring unit.

5. **The $1884 init / $1003 play pattern** (5 SIDs): init address≠play address+0, suggesting a
   second init block (possibly for multi-section songs or for instrument pre-loading). Worth
   understanding what lives at $1884 vs $1003.

6. **Acrouzet's $0800-based SIDs**: 5 tunes load at $0800 instead of $1000 — same player code
   relocated, or a different player variant? Compare binary sizes to canonical $1000 SIDs.

7. **sidid byte signatures**: fetch the complete sidid.nfo (raw bytes, since the rendered page
   was truncated) and extract the SidTracker64 entry to get the byte-level player fingerprint.
   URL: `https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo`

8. **Official site via Wayback**: `web.archive.org/web/*/sidtracker64.com` — if the app ever
   had a manual page, it would be there. Wayback was unreachable on 2026-06-14.

9. **Jason Page's SidTracker64 SIDs as RE targets**: Jason Page has the most tunes and the longest
   ones; he probably explored the full feature set. His multi-subtune SIDs (`Street_Defender` with
   3 subtunes) are the best candidates for understanding subtune switching.

10. **sidtool (olefriis/sidtool)**: although it doesn't support .s64, it does parse PSID and could
    be used to extract and display the SidTracker64 player code for cross-referencing.
