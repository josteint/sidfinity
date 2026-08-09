# Ubik's Musik — Editor RE, Player Binary Analysis, and Source Hunt

```
provenance_header:
  fetch_date:    2026-06-14
  researcher:    Claude Sonnet 4.6 (agent sweep)
  reliability:   HIGH for published facts + HVSC binary analysis;
                 MEDIUM for player decode (no hand-annotated disassembly available);
                 LOW for instrument table field layout (requires deeper RE)
  sources:
    - https://www.vgmpf.com/Wiki/index.php?title=Ubik%27s_Musik
    - https://www.everygamegoing.com/larticle/Ubiks-Music-000/28553
    - https://mancunian1001.wordpress.com/2016/12/20/the-sultans-of-sid-20-ubik/
    - https://www.lemon64.com/forum/viewtopic.php?t=39350
    - http://c64-music.blogspot.com/2010/09/ubiks-music.html
    - http://c64-music.blogspot.com/2011/09/how-to-save-tune-as-sid-and-wav-in.html
    - https://csdb.dk/release/?id=39950          (503 at time of fetch — Wayback also blocked)
    - https://csdb.dk/release/?id=132482         (Teesside Cracking Service crack)
    - https://csdb.dk/release/?id=260620         (Prg2Sid V1.26 by iAN CooG, 2026)
    - https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
    - https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg
    - https://archive.org/details/d64_Ubiks_Music_Editor_19xx_-
    - https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/Musicians.txt
    - Local HVSC binary analysis: hvsc85/MUSICIANS/A/Abbott_Chris/Chess.sid
                                   hvsc85/MUSICIANS/A/Abbott_Chris/Popcorn.sid
                                   hvsc85/MUSICIANS/T/Tonal_Teapot/Ubiks_Musik.sid
                                   hvsc85/MUSICIANS/D/Deadman/Ubik-Musik_Collection_I.sid
```

---

## 1. Editor overview

**Full name:** Ubik's Musik (also spelt Ubik's Music)
**Author:** Dave Korn, handle "Ubik" on Compunet — name taken from Philip K. Dick's 1969 novel.
**Publisher:** Firebird Software, 1987. Sold on cassette for £2.99.
**Platform:** Commodore 64.
**HVSC musician entry:** `Ubik (Korn, Dave) — UNITED KINGDOM (ENGLAND)` (Musicians.txt).
**CSDb release:** #39950 (Ubiks Music by Hotline, 1987). CSDb was 503 at fetch time.
**Cracked version:** CSDb #132482 (Teesside Cracking Service, D64 disk image, 333 downloads).
**Archive.org D64:** https://archive.org/details/d64_Ubiks_Music_Editor_19xx_- (March 2021 upload, runs via VICE browser emulator, 30 screenshots available).
**Zzap!64 review:** Issue #31, November 1987. Score 81%. Targeted at game programmers rather than casual users.

Dave Korn was employed by Firebird alongside Rob Hubbard. He composed Thrust II (1988, Firebird) and Xmas Prezzie (1986) in addition to creating the editor. The editor's demo tunes spread widely through PD libraries and game compilations. A copyright case at Manchester Magistrates Court arose when a demo tune appeared in *Lunar Jailbreak* (a re-released Hewson title published by Commodore Format/Future Publishing); the original authors won damages.

---

## 2. Source code and published disassembly — result of sweep

**No released source code or annotated disassembly found.**

Exhaustive searches of:
- GitHub (ubik, ubiks_musik, ubik_musik, C64 player)
- CSDb (csdb.dk — 503 at fetch time; Wayback also blocked for this domain)
- Codebase64 (codebase.c64.org/codebase64.org) — no Ubik's Musik article found
- Pouet.net — no results
- Demozoo — no results
- Archive.org — only the D64 disk image (not a source release)
- MJK music page (ist.uwaterloo.ca) — only a download link for the PRG, no documentation
- Funet (funet.fi) — `Ubiks_Music_Collection.prg` download only

The player is commercial and closed-source. No modern recreation, port, or annotated disassembly has been published as of 2026-06-14.

**Best available RE artefact:** the `prg2sid` tool by iAN CooG (CSDb #260620, v1.26, March 2026) contains an Ubik's Musik player detector and init/play patcher — it knows the byte signature and the `$C600/$C603` entry points. Its source is not publicly available.

---

## 3. Player identification signatures

Two independent signature databases contain Ubik's Musik entries:

### cadaver/sidid (sidid.cfg)
```
Ubik's_Musik
A9 00 9D ?? ?? BC ?? ?? 99 04 D4 60 4C ?? ?? DE ?? ??
10 F8 BC ?? ?? 8C ?? ?? A9 00 9D ?? ?? 9D ?? ?? A9 FF
9D ?? ?? BC ?? ?? BD ?? ?? 85 ?? BD
```

### WilfredC64/player-id (sidid.cfg) — identical entry
```
Ubik's_Musik
A9 00 9D ?? ?? BC ?? ?? 99 04 D4 60 4C ?? ?? DE ?? ??
10 F8 BC ?? ?? 8C ?? ?? A9 00 9D ?? ?? 9D ?? ?? A9 FF
9D ?? ?? BC ?? ?? BD ?? ?? 85 ?? BD
```

### prg2sid detection pattern (from CSDb #260620 summary)
Scan pattern: `AD xx xx 30 03 D0 22 60 18 29 7F A2` — typically found at `$C666`.
Init/play stub patched at `$C600` / `$C603`.

---

## 4. Binary player structure (derived from HVSC corpus)

Analysis of 11+ HVSC SIDs (Chess, Popcorn, Tonal_Teapot/Ubiks_Musik, Deadman collections, etc.) using byte-stability across files to distinguish player code from music data.

### 4.1 Standard memory layout

```
$AA9A–$BFFF  Music data region (lower portion): sequence/pattern data
$C000–$C5FF  Music data region (upper portion): more pattern + instrument data
$C600–$C71A  Player code block 1 (init + 3-voice loop dispatch)
$C71B–$C7B4  Embedded music data tables (variable per SID):
               per-instrument parameters, per-voice sequence pointers,
               tempo registers, voice state counters
$C7B5–$C821  Player code block 2 (note event handler)
$C824–$CDFF  Player code block 3 (large — effect chain, vibrato, SFX, wavetable drums)
```

Total compiled player + data: typically ~7 KB ($1800 bytes). Load address varies
(examples: $AA9A, $B7AA, $B882, $6B00 for large multi-song collections). The player
always maps to $C600 regardless of load address (the data below it varies in size).

**Relocated tunes:** Some SIDs (e.g. Brainstorm.sid: load=$6115 init=$6E50 play=$6E25)
use a fully relocated player. The sidid signature still matches because the opcode
sequence is invariant; prg2sid pattern-scans the whole file.

### 4.2 Init routine ($C606, called via JMP at $C600)

```
$C606: 18          CLC
$C607: 69 80       ADC #$80        ; A = subtune (0–25) → set bit 7 = "active" flag
$C609: 8D 1D C7    STA $C71D       ; store current-song# | $80 into player state
$C60C: A2 00       LDX #0
$C60E: A9 00       LDA #0
$C610: 9D 00 D4    STA $D400,X     ; clear all 32 SID registers
$C613: E8          INX
$C614: E0 20       CPX #$20
$C616: D0 F8       BNE $C610
$C618: 60          RTS
```

(Some SID variants add extra init preamble before $C606 to handle KERNAL/ROM banking:
`LDA $01 / PHA / LDA #$36 / STA $01 / JSR $C666 / PLA / STA $01 / RTS`.)

### 4.3 Play routine ($C603, JMP → $C619 in banked variant, or $C666 directly)

The play wrapper saves/restores `$01` (C64 I/O-port bank register), then calls `$C666`:

```
$C619: A5 01       LDA $01
$C61A: 48          PHA
$C61B: A9 36       LDA #$36        ; bank out BASIC + KERNAL, enable RAM
$C61D: 85 01       STA $01
$C61F: 20 66 C6    JSR $C666       ; main play loop
$C622: 68          PLA
$C623: 85 01       STA $01
$C624: 60          RTS
```

### 4.4 Main play loop ($C666) — critical design: ONE VOICE PER CALL

```
$C666: AD 1D C7    LDA $C71D       ; load song status byte
$C669: 30 03       BMI $C66E       ; bit7 set → playing, branch to voice dispatch
$C66B: D0 22       BNE $C68F       ; nonzero, bit7 clear → SFX-only mode
$C66D: 60          RTS             ; zero → stopped

$C66E: 18          CLC
$C66F: 29 7F       AND #$7F        ; extract song# 0–25
$C671: A2 ##       LDX #<voice>    ; SELF-MODIFYING: byte at $C672 = voice counter (2→1→0)
$C673: 7D 2F C7    ADC $C72F,X     ; A = song# + voice_base_offset[X]
$C676: A8          TAY             ; Y = index into per-song/per-voice pointer table
$C677: 20 D8 C6    JSR $C6D8       ; process voice Y
$C67A: CA          DEX
$C67B: 8E 72 C6    STX $C672       ; SMC: save decremented voice counter back
$C67E: 10 ED       BPL $C66D       ; X≥0 → RTS (one voice done; next call does next)
                                   ; X<0 (after X=0) → fall through to $C680
$C680: A9 02       LDA #2
$C682: 8D 72 C6    STA $C672       ; reset voice counter to 2 for next cycle
$C685: 8E 1B C7    STX $C71B       ; (X=$FF)
$C688: 8E 1C C7    STX $C71C
$C68B: 8D 1D C7    STA $C71D       ; reset song status (02 = idle/deactivated?)
$C68E: 60          RTS
```

**Key insight:** The player processes **exactly one SID voice per `play()` call**. The byte
at `$C672` (a self-modifying LDX immediate) rotates through 2→1→0, then the reset at
`$C680` reloads it to 2. This means the effective IRQ rate is 3× the frame rate —
at 50 Hz, each voice gets updated every 3 frames (≈16.7 Hz), BUT with a 50 Hz clock
the pattern is: frame 1→voice 2, frame 2→voice 1, frame 3→voice 0, frame 4→voice 2, …
This is the source of the "high rastertime" criticism: the player runs expensive voice
logic every single frame but spreads it across voices.

The voice base offsets at `$C72F–$C731` (stable across all SIDs) are `$B0 $CA $E4`,
encoding voice-specific starting indices into the song/sequence pointer table.

### 4.5 SFX mode ($C68F)

When `$C71D` is nonzero but bit7=0, the code at `$C68F` activates. It scans
`$C732,X` for X=2,1,0; entries with bit7 set indicate voices running a one-shot SFX
sequence. This is the **"play song on 2 voices + SFX on 3rd"** game-mode feature.

```
$C68F: A2 02       LDX #2
$C691: BD 32 C7    LDA $C732,X     ; check voice SFX state
$C694: 10 0B       BPL $C6A1       ; skip if no SFX on this voice
$C696: 18          CLC
$C697: 69 30       ADC #$30        ; voice offset = SFX code + $30
$C699: A8          TAY
$C69A: 20 D8 C6    JSR $C6D8       ; process as SFX
$C69D: 8A          TXA
$C69E: 9D 32 C7    STA $C732,X     ; save updated SFX state
$C6A1: CA          DEX
$C6A2: 10 ED       BPL $C691       ; loop voices 2,1,0
```

### 4.6 Embedded data tables ($C71B–$C7B4, variable per SID)

These 154 bytes differ per compiled SID and embed instrument parameters + voice state.
Partial decode (from stability analysis + code cross-reference):

| Address | Size | Content (hypothesis) |
|---------|------|----------------------|
| $C71B–$C71C | 2 | Unknown (per-SID; FFFF in Chess = 3-song SID; A04E in Popcorn = 1-song) |
| $C71D | 1 | **Current song status** (0=stopped, $80+n=playing song n, 1–3=SFX only) |
| $C71E | 1 | Padding / second status byte |
| $C71F–$C724 | 6 | Per-voice initial state (3 × 2 bytes) |
| $C725–$C72B | 7 | Stable constants (all-zero padding) |
| $C72C | 1 | 0 (constant) |
| $C72D | 1 | $07 (constant — possibly vibrato table stride) |
| $C72E | 1 | $0E (constant — possibly arp step) |
| $C72F | 1 | $B0 — voice 0 base offset into song pointer table |
| $C730 | 1 | $CA — voice 1 base offset |
| $C731 | 1 | $E4 — voice 2 base offset |
| $C732–$C734 | 3 | Per-voice SFX state bytes (used by $C68F SFX handler) |
| $C735–$C737 | 3 | $FF $FF $FF (sentinel/end markers?) |
| $C738–$C73A | 3 | $00 $00 $00 |
| $C73B–$C7B4 | ~121 | Instrument parameters (per-instrument tables) |

The instrument parameter block (`$C73B–$C7B4`) is ~121 bytes for a typical SID. With
32 instruments, that averages ~3.8 bytes per instrument — but the layout is likely
non-uniform (some instruments share table entries). No clean stride was found in this
sweep; full decode requires tracing the instrument-load code at ~$C7B5+.

### 4.7 Song/sequence pointer tables (below $C600, in the music data region)

From pointer analysis of the player code:
- `$C6B0` region (voice 0): 2-byte little-endian pointers, one per song, pointing into
  sequence data below $C600.
- `$C6CA` region (voice 1): same structure, voice 1 pointers.
- `$C6E4` region (voice 2): same structure, voice 2 pointers.

Example Chess.sid (3 songs):
- Voice 2, Song 0: pointer at `$C6E4` → `$B9FC` (start of voice-2 sequence data)
- Voice 2, Song 1: pointer at `$C6E6` → `$C000`

The sequence data below $C600 uses a variable-length record format where the
**dominant command byte is `$F3`** (108 occurrences in Chess alone) followed by one
argument byte. `$FF` (101 occurrences) appears to be the end-of-sequence sentinel.
Other command bytes ($E0–$FE) are sparse, suggesting most music data is encoded as
note events rather than commands.

---

## 5. Musical model (published sources + binary confirmation)

### 5.1 Editor capabilities (published)

- **26 songs** per compiled file (song indices 0–25).
- **32 instruments** per compiled file.
- **3 voices** (C64 SID channels 1–3), displayed as three vertical columns.
- Each column = a sequence of (sequence-number, repeat-count) pairs.
- Sequence editor: up to 128 notes + commands per sequence.
- Note entry in hex. Note properties: pitch (e.g. C4), duration (1–20 scale), gap.
- CONT command extends a note across beats.

### 5.2 Effects (published)

| Effect | Description |
|--------|-------------|
| Logarithmic vibrato | First C64 editor to support; modulation depth/speed configurable |
| Waveform swap | Mid-note waveform changes (ADSR restart decision per note) |
| Wavetable drums | 8 fixed built-in drum sounds |
| Echo | Sustain level decreased (or increased) on every note |
| Portamento | Note slide between pitches |
| Pulse width modulation | PWM sweep |
| Arpeggio | Mentioned in interface |
| Ties | Note continuation without ADSR restart |
| ADSR restart control | Separate note-off commands with independent durations |
| Tempo control | In-sequence tempo changes (via `$F3 nn` command) |

### 5.3 Gate/voice parameters (NPSTRSG switch, per published user report)

The editor UI has an `NPSTRSG` switch on the voice panel. Without the manual, exact
semantics are unclear, but from context it likely controls:
- **N** = Noise waveform bit
- **P** = Pulse waveform bit
- **S** = Sawtooth waveform bit
- **T** = Triangle waveform bit
- **R** = Ring modulation
- **S** = Sync
- **G** = Gate (ADSR gate on/off per note)

This matches SID register $D404/$D40B/$D412 bit layout.

### 5.4 Game integration API

Two call conventions described in published sources:
1. **Full 3-voice mode:** `JMP $C600` (init, pass subtune in A), `JMP $C603` or `$C666` (play).
2. **2-voice music + 1-voice SFX mode:** write SFX code to `$C732,X` (voice X) with
   bit7 set. The SFX handler at `$C68F` will process that voice as a one-shot effect
   on the next play call.

### 5.5 Performance characteristics

- Most compiled game soundtracks: **~7 KB**.
- High rastertime (noted in Zzap!64 review and VGMPF wiki) — consequence of the
  one-voice-per-frame design calling the effect chain every 50Hz tick.

---

## 6. HVSC corpus statistics

From `hvsc84.db`:

- **288 SID files** classified as `Ubik's_Musik` in HVSC #84.
- **Active use span:** 1987–2018 (earliest: Chris Abbott 1987; latest: M. Hardy 2018).
- Dave Korn (Ubik) himself composed only 2 HVSC entries:
  - `GAMES/S-Z/Thrust_II.sid` (1988 Firebird, 2 songs, load=$9000)
  - `GAMES/S-Z/Xmas_Prezzie.sid` (1986 Ubik, classified as engine=NULL — possibly pre-editor)

**Top composers by SID count:**

| Count | Composer |
|-------|---------|
| 55 | Warren Pilkington (Waz) |
| 45 | John Stormont |
| 30 | Kent Valdén (Noise of SID) |
| 18 | Patrick Ceuppens (Lyon) |
| 12 | Jouni Ikonen (Wild Finn) |
| 11 | Dennis Lindroos (Deadman) |
| 11 | Chris Abbott |
| 10 | Andrew Fisher (Merman) |
| 9 | Julian Potts (Japmaster) |
| 9 | G.Davies & A.DeLucia (Tonal Teapot) |

**Games using Ubik's Musik (HVSC GAMES/ subset):**
Brainstorm (Firebird 1987), Deviants (Players 1987), Protium (Polysoft 1987),
Lethal (Alternative 1988), Atlantis (CDU 1988), Thrust II (Firebird 1988),
Joe Blade 2 (Players 1988), Blip! Video Classics (Silverbird 1988),
Quadrant 4 (Clockwize 1989), Die! Alien Slime (Mastertronic 1989),
Cowboy Kidz (Byte Back 1990), Fire Breath (Hooijmeijer 1990),
Madix (CDU 1991), Zilch (Incubus 1992).

Notable UK publishers using the editor: Firebird, Players, Alternative Software,
Silverbird, Mastertronic — all UK labels active in the late 1980s.

---

## 7. Dave Korn biographical notes

- **Real name:** David Korn. **Handle:** Ubik (from Philip K. Dick novel, 1969).
- Based in the north of England; worked at Firebird Software.
- Used "Ubik" as his avatar on Compunet (UK pre-internet BBS/network).
- Firebird colleague of Rob Hubbard.
- Programmed: Arcade Classics and Thrust II (C64 Firebird).
- Created Ubik's Musik as a commercial product sold through Firebird.
- Referenced in "Where Are They Now" feature in Commodore Format; interview given to
  Commodore Zone about his work.
- HVSC Musicians.txt: `Ubik (Korn, Dave) — UNITED KINGDOM (ENGLAND)`.

---

## 8. Conversion tools

### prg2sid (iAN CooG)
- CSDb #260620 (v1.26, March 2026, most recent).
- Detects Ubik's Musik by scanning the file for the byte pattern
  `AD xx xx 30 03 D0 22 60 18 29 7F A2` (found at $C666 in standard layout).
- Patches an init/play stub at `$C600/$C603`.
- Sets SID header with 9 subtunes by default (for debug; actual count varies).
- Handles tunes where `$C600` is not the load address (relocated players).
- CLI: `p2s YOURTUNE.PRG` → `YOURTUNE.SID`.
- Not open source.

### Standard conversion workflow
1. In Ubik's Musik editor: compile → saves PRG to disk.
2. Extract PRG via DirMaster.
3. `p2s YOURTUNE.PRG` → SID.
4. Edit subtune count and default in SIDedit if needed.

---

## 9. Gaps in current knowledge

The following are **not** resolved by this sweep:

1. **Full instrument format:** The per-instrument byte layout inside `$C73B–$C7B4` is
   not decoded. Requires tracing the instrument-load subroutine (likely within the
   `$C7B5–$C821` code block). Key unknowns: ADSR bytes (4), waveform byte (1),
   pulse width (2), vibrato depth/speed (2), arpeggio table index (1), echo
   delta (1), portamento rate (1) — estimated ~12 bytes/instrument but unconfirmed.

2. **Sequence command set:** Beyond `$F3 nn` (tempo) and `$FF` (end), the full command
   byte table is unknown. VGMPF mentions ties, CONT, and note-off as separate entries
   but gives no byte values.

3. **Wavetable drum layout:** 8 fixed drum sounds — are they in the player code block
   (`$C824–$CDFF`) or in the compiled data below `$C600`? Not determined.

4. **Vibrato table:** Described as "logarithmic" — likely a lookup table in the
   `$C824–$CDFF` code block. Table address and size unknown.

5. **Echo mechanism:** "Sustain level decreased/increased on every note" — whether this
   is a per-instrument delta or a global parameter is unknown.

6. **26-song pointer table layout:** The exact stride between per-voice per-song pointers
   (estimated 2 bytes × 26 songs × 3 voices = 156 bytes) is not confirmed against
   the actual SID data.

7. **The editor disk itself:** The archive.org D64 image runs via VICE in-browser but
   was not decoded for on-disk file layout or in-editor help text during this sweep.
   Inspecting the D64 files directly (via cbmfiles or c1541) could reveal in-program
   help or documentation text.

---

## 10. Leads to follow

1. **Fetch the archive.org D64 and inspect it with c1541:** Extract the files from the
   disk image, run `strings` on the main PRG, look for in-program help text or an
   embedded manual that describes command bytes and instrument fields.
   ```
   wget "https://archive.org/download/d64_Ubiks_Music_Editor_19xx_-/Ubiks_Music_Editor_19xx_-.d64"
   c1541 Ubiks_Music_Editor_19xx_-.d64 -list
   c1541 Ubiks_Music_Editor_19xx_-.d64 -read "ubik's musik" ubikmusik.prg
   strings ubikmusik.prg | less
   ```

2. **Contact iAN CooG via CSDb** to ask whether prg2sid's Ubik detection logic (or any
   personal notes) can be shared. CSDb profile: the tool's comment thread at #260620
   may already contain format notes.

3. **Contact Warren Pilkington (Waz)** — 55 HVSC SIDs using Ubik's Musik, active
   scener. He likely has the deepest practical knowledge of the format quirks. His
   HVSC entry is `MUSICIANS/W/Waz/`.

4. **Inspect `$C824–$CDFF` code block** (1500 stable bytes across all SIDs) for the
   wavetable drum data, vibrato table, and arpeggio table. A seed disassembly from any
   HVSC SID will expose this. The block is identical in all standard-layout tunes, so
   one disassembly covers all.

5. **Look for the Ubik's Musik manual scan.** ConsoleMAD (consolemad.co.uk) sells the
   cassette version; they may have a scanned manual. The Zzap!64 review (Issue 31,
   1987) contains the most detailed published description.

6. **Check csdb.dk when it's back up** for release #39950 comments — scene veterans
   sometimes leave RE notes in CSDb comments.

7. **Check Deadman (Dennis Lindroos)'s scene pages** — he produced 7 Ubik-Musik
   collection SIDs (1988–1996, Finnish Code Masters / Point X) and likely knows the
   format inside-out. He may have Finnish C64 scene contact info on CSDb.

8. **SIDin online magazine** (referenced by cadaver at cadaver.github.io) published
   music routine dissections. Search their archive for an Ubik's Musik analysis.

9. **The relocated-player variant (Brainstorm.sid: $6E50/$6E25)** is a good
   disassembly target if the standard C600 layout needs cross-checking — it proves the
   player code is position-independent.

10. **Waz's demo SID: `Cubik_and_Transmission.sid`** and the full
    `Ubiks_Music_Demotune_Mixes.sid` (55-tune collection) are good multi-song test
    vectors for verifying the song-pointer table layout once decoded.
