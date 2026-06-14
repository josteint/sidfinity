# EMS (Electronic Music System) — Editor, Cosine, and Feature Model

## Provenance

| field | value |
|---|---|
| source_urls | https://csdb.dk/release/?id=4649 · https://www.cosine.org.uk/ · https://csdb.dk/scener/?id=1181 · https://demozoo.org/sceners/50015/ · https://www.lemon64.com/forum/viewtopic.php?t=5725 · https://www.lemon64.com/forum/viewtopic.php?t=10753 · https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg |
| fetched_via | WebFetch + WebSearch (Claude agent) |
| fetch_date | 2026-06-14 |
| primary_author | Sean Connolly (handle: Odie) |
| content_date | 1997 (V7.03 release); V10.x circa 2015+ |
| reliability | HIGH for V7.03 (full disk image extracted, all help files read verbatim); MEDIUM for V9/V10 (no disk image found; features inferred from sidid.cfg fingerprints + YouTube titles) |

**Primary source:** `ems_v703.d64` — the official Cosine release disk image downloaded from
`http://csdb.dk/getinternalfile.php/65199/ems_v703.zip` (CSDb release #4649).
All `HELP.*` and `SND*.*` files extracted verbatim; text is PETSCII-decoded.
Full extracts under `docs/src/`.

---

## 1. Author and Provenance

**Sean Connolly** (handle: **Odie**, CNET ID SC21) of **Cosine** / **Sonix Systems**, United Kingdom.
Active from 1989 onwards. Handle origin: "the dog from the Garfield cartoons."
CSDb profile: https://csdb.dk/scener/?id=1181
Demozoo profile: https://demozoo.org/sceners/50015/
Contact (1997): seanc@draught.demon.co.uk

Odie wears all hats: coder, musician, organiser, webmaster.
EMS credits (V7.03): Code/design/music = Odie; Music = Skywave (Cosine); Graphics/charset = The Magic Roundabout (Cosine).

**TMR (Jason Kelk)** — also of Cosine, passed away 2021. He was an EMS user (appears in the EMS user list, and is one of the 196-SID HVSC corpus composers using EMS/Odie engine). He pointed new users to EMS via the Cosine website and offered a tutorial at some point.

**Sonix Systems** — Odie's alternative group name; appears in CSDb credits alongside Cosine.

The release disk `ems_v703.d64` was downloaded from `cosine.org.uk` (logo in `file_id.diz` reads "A Cosine Systems Production / http://www.cosine.org.uk/").

---

## 2. Version History

| Version | Notes |
|---|---|
| Pre-V4.3 | Player-only, no graphical editor. Odie "normally works in source code rather than an editor." |
| V4.3 | First version with a graphical editor (per TMR on Lemon64). |
| V7.03 | Released 18 January 1997 (CSDb #4649). Full editor + player. This is the only publicly available disk image found. |
| V8 | In development as of ~2003 (per TMR on Lemon64); had an updated driver but no graphical editor. |
| V9.x | Distinct sidid fingerprint (see §7). No disk image found in this research sweep. |
| V10.x | Distinct sidid fingerprint (see §7). YouTube video "EMS V10.0 teaser - Commodore 64" exists (https://www.youtube.com/watch?v=ch8ntVgcH4k). "Happy Birthday played on the C64 using EMS V10.01 music editor" (https://www.youtube.com/watch?v=rYGhADLYOzk). Circa 2015+. |

From TMR (Lemon64 thread "I want to make music. What's a good program?", ~2003):
> "EMS only gained an editor at V4.3 (the latest is V8 and there isn't an editor for that either)."

From TMR (same thread):
> Odie was "presently writing a soft-synth version for the PC" (as of ~2003).

---

## 3. HVSC Corpus

196 HVSC #84 SIDs classified as `EMS/Odie` by sidid. Composers:

| composer dir | count |
|---|---|
| Merman | 99 |
| Connolly_Sean | 61 |
| TMR | 13 |
| Bayliss_Richard | 10 |
| Seabrain | 4 |
| Gillgrass_Dan | 3 |
| Fuzz | 2 |
| Francois_Marc | 2 |
| Julian_Jaymz | 1 |
| Jack | 1 |

Note: **Merman** (real name unknown; 99 tunes) is the single largest EMS/Odie user in HVSC. He commented favourably on EMS in the Lemon64 "I want to make music" thread. **TMR** (Jason Kelk, Cosine) appears with 13 tunes; passed away 2021. **Dan Gillgrass** (3 tunes) started composing with EMS on Cosine's recommendation. **Bayliss_Richard** is catalogued as EMS/Odie in HVSC (10 tunes) but his public interviews say he used DMC/Future Composer — possible sidid misclassification for some of his tunes.

Related engine strings (distinct sidid signatures, not EMS/Odie proper):
- `Odie/Cosine` (9 SIDs) — earlier Odie player pre-EMS
- `Odie_tiny` (3 SIDs) — 4k/compact variant
- `Odie/Pulse` (2 SIDs)

Load-address distribution of EMS/Odie tunes: **141/196 load at $1000** (init=$1000, play=$1003). The player is relocatable — 55 tunes use various other load addresses ($0900, $0F00, $1100, $E000, $8000, $9000, etc.). The 5-jump-vector layout (see §5) always places play = init + 3.

---

## 4. Editor Overview (V7.03)

Source: HELP.GENERAL extracted from `ems_v703.d64`.

- **Platforms**: C64, C128 (in C64 mode). Developed on C128 + Amiga A4000 (as65 assembler on Amiga).
- **Editor memory map during editing**: $9000–$D000 (includes music + sound data).
- **Up to 8 tunes per module** (multi-tune). Tune boundaries auto-detected from track data.
- **Multispeed**: single, double, triple, or quad speed. Two separate call entry points: main player (handles one full frame) and sound engine (for multispeed calls). Filter is NOT sped up by multispeed.
- **Zero-page usage**: top 8 locations $F8–$FF.
- **Compilation**: "final save" compiles module to a standalone binary. Must save the module first.
- **Sequence data stored in compressed format** — editing causes chunk moves.
- **Max 96 sequences**, each max $FF bytes.
- Editor restart after crash: `SYS 5596`.
- **Trace play** (single speed only): follows one track's sequences in real time.

---

## 5. Player API (V7.03)

From HELP.GENERAL, the compiled player has a 5-entry jump table at the start:

| offset | function |
|---|---|
| +$0000 | Init player. Tune number in A register. |
| +$0003 | Play 1 frame of music. |
| +$0006 | Play 1 frame of sound engine (multispeed call). |
| +$0009 | Clear the SID chip. |
| +$000C | Fade tune out. Speed in A. |

Fade: loops internally until complete; requires music running under IRQ. Duration = FadeSpd × 16 frames.

---

## 6. Musical Feature Model (V7.03)

All information extracted directly from the embedded help files on the V7.03 disk.

### 6.1 Song Structure

**Three-level hierarchy**: Tracks → Sequences → Notes+Commands.

- **Tracks**: 3 tracks (one per SID voice). Each track is a list of track commands + sequence references.
- **Sequences**: 96 sequences ($00–$5F), max $FF bytes each. Sequences are shared across tracks.
- **Track commands** (all in hex notation in the editor):
  - `rst??` — loop point at end of tune (restart)
  - `stop` — stop track playing
  - `fad??` — fade music out at speed ??
  - `tmp??` — set track tempo ($02–$0D)
  - `tr+??` — transpose upward ($00–$1F semitones)
  - `tr-??` — transpose downward ($01–$10 semitones)
  - `it??` — instrument transpose ($00–$1F); wraps modulo number of instruments (e.g. $1E+$06 = $04)
  - `rep??` — repeat next sequence ?? times ($03–$42); NOTE: rep $1C means play 28 times, not 29
  - `2a` (two hex digits) — sequence reference number ($00–$5F)

- **Per-track tempo**: multi-track tempo supported. Must use multiples of other tracks for correct timing (e.g. if all tracks at 6, use only 3 or 12 in changing track).

- **Track swapping**: ctrl+1/2/3 swaps voice assignments; disabled while player is on.

### 6.2 Sequence Commands (Note Data)

Notes range C-0 to B-7 (standard notation, not German H).

**Commands in sequence data:**

| command | description |
|---|---|
| `VOL?? ?0` | Volume, filter, resonance: high nibble = volume ($0–$F), next = filter type, next = resonance, last = fil command fills $0 |
| `^nnn0000` | Glide from source note: nnn=source note, next 2 digits = duration (frames to glide), next 2 = pre-glide delay. Must have destination note on next line. |
| `event` | Event flag: increments byte at player+$0018. Used for sync with screen effects. |
| `hdnon` | Oscillating glide DOWN on |
| `hupon` | Oscillating glide UP on |
| `arpon` | Arpeggio sound on |
| `vibon` | Vibrato sound on |
| `arp??` | Arpeggio table selection ($00–$17); used when instrument's fixed arp override = $FF |
| `sfx??` | Sound FX selection ($00–$1F) |
| `dur??` | Duration ($01–$40) |
| `filXXX` | Filter channel assignment (fills the $0 byte in `vol`); e.g. `fil011` = filter voices 2 and 3 |
| `slion` | Arpeggio slide DOWN on (downward arp sliding) |
| `slioff` | Arpeggio slide DOWN off |
| `cycon` | Pulse width cycle reset on (default: on) |
| `cycoff` | Pulse width cycle reset off (pulse no longer resets on new notes) |
| `porton` | Note portamento on (rapid slide between notes) |
| `portoff` | Note portamento off |
| `sus` | Sustain for previous duration (holds note) |
| `gat` | Same as sustain but gates waveform off for release (keyoff) |
| `nrep??` | Repeat next note ($03–$12) times; same sound and duration |

**Vol command example**: `vol1f f0` = vol=$1F (max), filter=lowpass, resonance=full, $0=fill for fil command.

**Glide example**: `^f-4320a` = source note F-4, duration=$32 frames, delay=$0A frames before glide starts.

**vibon/arpon/hdnon/hupon** allow overriding the sound type defined in the sound editor from within sequence data.

**arp?? command**: sequence-level arpeggio; used when instrument's fixed arp number is $FF (player reads arp number from sequence rather than instrument).

**sfx commands**: can be transposed to another sound via track `it??` command; must be reset or rest of tune may be silent.

**event command**: byte at player+$0018 increments; reset by programmer; used to trigger screen effects.

**sus vs gat**: if instrument is defined to gate off, `sus` cannot prevent gating off.

### 6.3 Instrument (Sound) Format

15 named parameters per instrument ("sound"), exposed via the sound editor help files:

| param | help file | description |
|---|---|---|
| firstwf | SND01 | First-frame waveform: direct waveform byte for frame 1 of note. Valid gate-on values: 01 09 11 13 15 17 21 23 25 27 31 33 35 37 41 43 45 47 51 53 55 57 61 63 65 67 81. Gate-off: 00 08 10 12 14 16 20 22 24 26 30 32 34 36 40 42 44 46 50 52 54 56 60 62 64 66 80. |
| wf+gateoff | SND02 | Low 5 bits = waveform table index ($00–$17). Bits 6–8 = gateoff period (frames before end of note when gate switches off): $20=1fr, $40=2fr, $60=3fr, $80=4fr, $A0=5fr, $C0=6fr, $E0=7fr. Combined: wftable + gateoff_period. Warning: don't set gateoff within 2 frames of tempo speed. |
| ADSR (AD) | SND03 | Attack (hi nibble) + Decay (lo nibble). Standard SID AD register. |
| ADSR (SR) | SND04 | Sustain (hi nibble) + Release (lo nibble). Standard SID SR register. |
| pulselohi | SND05 | Pulse width start level (14-bit). Format: $3A → pulse = $0A30 (the byte is interpreted as lo=lo-nibble×$100, hi=hi-nibble×$1000 of the 16-bit PW register). |
| pwrate | SND06 | Pulse cycle increment rate ($00=no cycling, $FF=fastest). |
| pwdelay | SND07 | Frames to delay before pulse cycling starts ($00–$FF; $FF ≈ 5.05 seconds). |
| pwminmax | SND08 | Pulse width high-byte min/max limits. $1E = min $0100, max $0E00; ping-pong between. $00 = max ignored, cycles endlessly. |
| vibdelay | SND09 | Vibrato start delay in frames ($00–$FF; $FF ≈ 5.05 sec). |
| oscdelay_vibdepth | SND10 | Dual-purpose: left digit = oscillating glide delay, right digit = vibrato depth (0=heavy, 7=almost none). |
| vibspeed | SND11 | Vibrato cycle speed ($00=off, $3F=longest cycle). Cycle = 3× value frames. "For sensible musical use, $00–$05 is OK." |
| soundtype | SND12 | Multi-purpose frequency modulator type, right nibble: 0=vibrato, 1=arpeggio, 2=osc glide down, 3=osc glide up, 5=high-frequency arp table output. Left nibble: for types 2/3 = glide increment rate ($0–$F, $0=none, $F=fastest; maxes out and defaults to vibrato); for types 1/5 = arpeggio frame delay ($0=fastest, $F=slowest). |
| filterhigh | SND13 | Filter highbyte start level ($C4 → filter source = $C400, 16-bit). Also the source for filter sweeps. |
| filtertable | SND14 | Which filter table to play ($00–$17). |
| arpovrride | SND15 | Fixed arpeggio override: $00–$17 = specific arp table; $FF = take arp from sequence `arp??` command. |

### 6.4 Waveform Tables

Source: HELP.WAVES + SND01/SND02.

- Up to $18 waveform tables (24 tables, indexed $00–$17).
- Each table = a sequence of SID waveform control bytes played 1 frame at a time.
- Terminated by `$FF, line_number_to_loop_to`.
- Do NOT loop to a loop command (may lock player).
- The `firstwf` parameter is a shortcut for the first frame; waveform table plays from frame 2 onward (or from frame 1 if no firstwf shortcut is used).

### 6.5 Arpeggio Tables

Source: HELP.ARPS.

Up to $18 arpeggio tables (24 tables, $00–$17). Each byte is:

| value | meaning |
|---|---|
| $00–$18 | Add offset to base note |
| $19–$5F | Absolute notes C#2–B-7 |
| $80–$DF | Absolute notes C-0–B-7 |
| $FE, $?? | Terminate arpeggio; $?? = sound type to play next ($00–$03, same as soundtype right nibble) |
| $FF, $?? | Loop arpeggio to line $?? |

**High-frequency output mode** (sound type 5): all bytes $00–$FD have 2 added to them and are output as high-byte frequency values. $FE/$FF behavior unchanged.

### 6.6 Filter Tables

Source: HELP.FILTER.

Up to $18 filter tables ($00–$17). Each entry has: `dest` (target filter level, 16-bit) and `rate` (increment rate). Can sweep to up to 7 destinations per table.

- Source level = filterhigh parameter of the instrument.
- Terminate: `dest = $FFFE`.
- Loop: `dest = $FFFF`, lo byte of rate = loop line number.

### 6.7 Vibrato

From HELP.GENERAL: "quite advanced" — uses a method that maintains constant vibrato amplitude regardless of frequency range (no de-tuning at low vs. high notes).

### 6.8 Glide (Note-to-Note)

From HELP.GENERAL: uses a division routine taking 9–12 scanlines per track, but ONLY on the first frame of the glide. Triggering glide on all 3 channels simultaneously risks a max raster jump of ~36 scanlines. Recommend staggering glide triggers by 1 frame per channel.

---

## 7. sidid.cfg Fingerprints

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg

```
[EMS/Odie]
B9 ?? ?? 85 F8 B9 ?? ?? 85 F9 BC ?? ?? B1 F8 C9 FF D0 ?? C8 B1 F8 END
BD ?? ?? 85 F8 BD ?? ?? 85 F9 BC ?? ?? B1 F8 C9 40 90 ?? C9 FE D0 END
B9 ?? ?? AC ?? ?? 99 06 D4 AD ?? ?? 99 05 D4 AD ?? ?? 29 FE 99 04 D4 END
BC ?? ?? B9 ?? ?? 85 ?? 0A 85 ?? 18 65 ?? 85 ?? BD ?? ?? C5 ?? 90 ?? C5 ?? 90 ?? C5 ?? 90 ?? BD ?? ?? 29 ?? F0 ?? BC ?? ?? 4C END
85 ?? 06 ?? 26 ?? 26 ?? 26 ?? 38 A5 ?? E5 ?? AA A5 ?? E5 ?? 90 END

[(EMS_V7.03)]
8D ?? ?? A0 16 A9 00 99 00 D4 88 10 FA A9 ?? 8D 04 D4 8D 0B D4 8D 12 D4 60 END

[(EMS_V9.x)]
A2 02 A0 0E 20 AND A0 07 20 AND A0 ?? 86 ?? 84 ?? BD END

[(EMS_V10.x)]
A0 00 B9 ?? ?? 0A 99 ?? ?? B9 ?? ?? 2A 99 ?? ?? C8 C0 53 D0 END
```

**Interpretation of sub-variant fingerprints:**

- **EMS_V7.03**: Init routine — clears 22 ($16) SID voice registers to zero (`A0 16; A9 00; 99 00 D4; 88; 10 FA`), then sets voice control registers ($D404, $D40B, $D412) to a priming value, then RTS.

- **EMS_V9.x**: Init loop structure — `A2 02` (X=2, loop over 3 voices); `A0 0E` / `A0 07` / `A0 ??` (Y-register addressing with different counts per pass); contains calls (`20 AND`). Significantly restructured vs. V7.

- **EMS_V10.x**: Data processing loop — `A0 00; B9 ?? ??; 0A; 99 ?? ??; B9 ?? ??; 2A; 99 ?? ??; C8; C0 53; D0` — processes $53 (83) consecutive values, doing bit-shift operations (ASL `0A` and ROL `2A`) and storing two result streams. Suggests a new data preprocessing or table-building step in the init routine (possibly related to a new encoding of the frequency table or instrument data).

The generic `EMS/Odie` patterns (5 alternatives joined by OR) match all versions. The sub-variants additionally narrow the version: a SID matching BOTH the generic patterns AND `(EMS_V7.03)` is V7.03; etc.

---

## 8. Structural/Format Notes for RE

- **Multi-tune**: player auto-detects tune boundaries from consecutive track data. Up to 8 tunes per compiled binary.
- **Sequence count**: max 96 sequences ($00–$5F).
- **Sequence length**: max $FF ($255) bytes.
- **Player memory during editing**: $9000–$D000.
- **Zero-page**: $F8–$FF (8 bytes).
- **Sound effects (sfx??)**: $00–$1F range — 32 SFX slots in parallel to instruments.
- **Waveform table count**: $18 (24) tables.
- **Arpeggio table count**: $18 (24) tables.
- **Filter table count**: $18 (24) tables.
- **Sequence line numbers are byte offsets** (index into compressed sequence data), not line counts.
- **Compiled binary**: starts with the 5-entry JMP table (init/play/engine/clear/fade). Relocatable.
- **Multispeed calls**: main player once per frame; sound engine additional N−1 times for N× speed. Filter routine NOT sped up.
- **Fade duration formula**: FadeSpd × 16 frames (value in A register at $+$000C).
- **Event counter**: byte at player_base + $0018.

---

## 9. Community Context

- EMS is described as "good, but advanced" (Richard/TND on Lemon64). Suitable for experienced users.
- TMR recommended EMS for those willing to invest the learning curve; newcomers often chose DMC (tutorials available from TND group).
- Dan Gillgrass: "EMS is what got me into composing on the sixty four."
- merman (Lemon64): EMS has easier sound creation + built-in player + compiler; DMC produces smaller compiled files and is "slightly more powerful."
- JCH and SYNC also recommended alongside EMS in contemporaneous discussions.
- Odie himself normally composed in source code (assembler), not the editor.
- The EMS demo modules on the disk (MOD.*) are: Brian the Lion, Coup De Grace, Cyberwing, Enigma, Extreme Force, Go West, Goatbeard, Noisy Pillars, Peanuts, Perception, Set Piece, The Fastlane, Tomb Raider, Yoda's Theme.

---

## 10. Leads to Follow

1. **EMS V9 and V10 disk images**: not found in this sweep. Search: csdb.dk search for "EMS" releases with IDs > 4649; pouet.net; scene.org; zimmers.net/anonftp/; GameBase64. The YouTube channel that posted the EMS V10.0 teaser and Happy Birthday demos may link to the disk image.

2. **Cosine website archived pages**: `https://www.cosine.org.uk/products.php?4mat=c64&prod=ems_v703` returned empty content — the page exists but WebFetch could not render it. Try Wayback Machine snapshots: `https://web.archive.org/web/2010*/https://cosine.org.uk/` — known unavailable via WebFetch in this session.

3. **V9.x/V10.x format differences**: the sidid fingerprints (§7) confirm distinct init routines. The V10.x loop over $53 values with bit-shifting suggests either a new frequency table format or a new instrument data encoding. Reversing one V10.x SID would clarify.

4. **Odie FM demo (2018)**: YouTube video "Odie FM - Commodore 64 FM-YAM music demo" exists (https://www.youtube.com/watch?v=_nJgvcA5td4) — may show Odie's work post-EMS.

5. **Sound editor UI details**: the V7.03 help files describe 15 instrument parameters but the editor UI screen layout (how parameters are laid out in memory and in the compiled binary per-instrument record) is not documented in the help text. Reversing a compiled EMS V7.03 module would give the exact binary instrument record layout.

6. **Binary instrument record format**: SND01–SND15 describe 15 named fields. Expected byte layout per instrument: `[firstwf][wf+gateoff][AD][SR][pulselohi][pwrate][pwdelay][pwminmax][vibdelay][oscdelay_vibdepth][vibspeed][soundtype][filterhigh][filtertable][arpovrride]` (15 bytes, but exact ordering needs confirmation from binary).

7. **TMR tutorial**: TMR mentioned pursuing a tutorial for EMS (Lemon64 thread ~2003). May exist on an archived cosine.org.uk page or in a diskmag (Driven, Commodore Zone).

8. **Cyberwing SID** (CSDb #5683, 25 subtunes, 1995): an early multi-tune EMS release; useful as a reference for the multi-tune format since the help files reference it by name ("See the CYBER WING demo to see this").

9. **EMS V8**: intermediate version mentioned by TMR as having an updated driver but no editor. Not in CSDb tools listing. May be a player-only release in a Cosine demo.

10. **Other EMS composers**: Richard Bayliss accounts for 99/196 HVSC EMS tunes (the "Berman" directory). Bayliss is a prolific Cosine-adjacent composer who may have written EMS tutorials or format notes.
