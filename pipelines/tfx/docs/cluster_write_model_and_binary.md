# TFX SID Player — Write Model and Binary Structure

<!-- provenance-header
  source_url:     https://csdb.dk/release/?id=110111  (TFX v1.0, 1995)
                  https://csdb.dk/release/?id=38900   (TFX v1.2, 1996)
                  https://archive.org/details/d64_TFX_v2.4_1996_Unreal
                  https://github.com/cadaver/sidid    (sidid.nfo/sidid.cfg)
                  https://github.com/WilfredC64/player-id (sidid.cfg)
                  hvsc84/MUSICIANS/F/Factor6/*.sid     (binary inspection)
                  hvsc84/MUSICIANS/S/Sad/*.sid         (binary inspection)
                  hvsc84/MUSICIANS/P/PCH/*.sid         (binary inspection)
  fetched_via:    WebFetch + local binary READ-ONLY inspection
  fetch_date:     2026-06-14
  author:         Ray (Łada Loštàk), member of Area Team and Unreal groups
  content_date:   1995–~2000 (player versions); HVSC tunes through 2016
  reliability:    HIGH for binary structure (direct byte inspection of 269 SIDs);
                  MEDIUM for effect semantics (6502 disasm, no runtime verification);
                  LOW for version feature deltas beyond 1.0/1.3/2.8 (limited samples)
-->

## 1. Player Overview

**TFX** ("The Tracker" or "TFX") is a Commodore 64 SID music tracker created by
**Ray** (Łada Loštàk), member of **Area Team** and **Unreal** groups, released
in 1995 (v1.0) through approximately 1997–2000 (v2.94–2.99). It is a Polish-scene
tracker with most composers being Polish or Czech C64 musicians.

HVSC #84 contains **269 TFX SIDs** — the authors are:

| Author                         | SIDs |
|-------------------------------|------|
| David Cwik (Sad)              | 108  |
| Petr Chlud (PCH)              |  52  |
| Jaymz Julian (A Life in Hell) |  45  |
| Factor6                       |  42  |
| Others (Aki, Henne, etc.)     |  22  |

CSDb releases: v1.0 (1995, id=110111), v1.2 (1996, id=38900), v2.4 (1996, archive.org).
Versions seen in HVSC: 1.0, 1.3, 2.7, 2.8, 2.93, 2.94, 2.95, 2.97, 2.98, 2.99.

---

## 2. SIDId Signature

From `sidid.cfg` (cadaver/sidid, WilfredC64/player-id, DeepSID):

```
TFX
9D ?? ?? 9D ?? ?? A9 00 9D 05 D4 9D 06 D4 A9 ?? 9D 04 D4
```

Decoded (X = 0, 7, or 14 for voices 1–3):

```asm
STA  $????,X       ; 9D ?? ?? — store to per-voice state (e.g. $18DA,X)
STA  $????,X       ; 9D ?? ?? — store to per-voice state (e.g. $1904,X)
LDA  #$00          ; A9 00
STA  $D405,X       ; 9D 05 D4 — clear Attack/Decay
STA  $D406,X       ; 9D 06 D4 — clear Sustain/Release
LDA  #$??          ; A9 ?? — control byte (typically $08 = TEST bit)
STA  $D404,X       ; 9D 04 D4 — set ctrl (hard-restart with TEST bit)
```

This is the **per-voice hard-restart sequence** in the voice-initialisation
subroutine, matching the known fact from the task description. It fires once per
voice during init, with X iterating over 0, 7, 14.

Location in TFX 2.8: `$1132–$1144` (init at `$10FA`, voice-init sub at `$111F`).

**One signature covers all versions** — the byte sequence appears in TFX 1.0 through
2.99. No sub-signatures for version discrimination are present in sidid.cfg.

---

## 3. Player Binary Structure

### 3.1 Memory Layout — TFX 2.x (main family)

All TFX 2.x SIDs load at **$1000** (standard) or a relocation address (e.g. $A000,
$8240, $0C00). The structure relative to the load base `BASE` is:

```
BASE+$0000:  4C xx xx   JMP BASE+$FA  ; init entry ($1000 in standard)
BASE+$0003:  4C xx xx   JMP BASE+$72  ; play entry ($1003 in standard)
BASE+$0006:  4C xx xx   JMP BASE+$14  ; 3rd entry (instrument/event table)
BASE+$0009:  27         '             ; apostrophe — string delimiter
BASE+$000A:  [VERSION STRING]         ; "TFX 2.8 BY RAY/UNREAL" etc. (R=$D2, U=$D5 in PETSCII)
             27                       ; '
             [SONG TITLE]             ; e.g. "ATARIADA BY FACTOR6 2016!!"
             27                       ; '  — marks end of title / start of data
BASE+$003A:  [FREQ TABLE LO]         ; 96 bytes — lo-bytes for notes C0–B7
BASE+$009A:  [FREQ TABLE HI]         ; 96 bytes — hi-bytes for notes C0–B7
BASE+$00FA:  [INIT ROUTINE]          ; player init code
BASE+$0172:  [PLAY DISPATCHER]       ; per-frame play: processes all 3 voices
             ...
BASE+$0xxx:  [ENGINE CODE]           ; voice-process, pattern decoder, SID write sink
             ...
BASE+$1BCF:  [INIT TABLE]            ; 8-byte subtune descriptors
BASE+$1BEF+: [PATTERN / SONG DATA]  ; pattern streams for all voices
```

The version string between the first two apostrophes identifies the engine; the
song title between the 2nd and 3rd apostrophes is the composition name. The `!!`
at the end of the song title is a visual convention (not a sentinel); the closing
`'` (0x27) is the actual delimiter.

### 3.2 Memory Layout — TFX 1.0

TFX 1.0 has a different layout — the **freq table occupies $1000–$10BF**; the
player body starts at $1100:

```
$1000–$105F:  FREQ TABLE LO  (96 bytes, notes C0–B7)
$1060–$10BF:  FREQ TABLE HI  (96 bytes)
$10C0–$10FF:  PETSCII border + version string "TFX 1.0 BY RAY /UNREAL" + song title
$1100:  JMP $117E    ; play entry
$1103:  JMP $1995    ; 3rd entry
$1106:  [INIT ROUTINE]
```

PSID header: `init=$1106`, `play=$1100`. The freq-table lo-bytes are
**identical** between v1.0 and v2.8. Hi-bytes differ only at note 95 (B7):
`$FC` (v1.0) vs `$96` (v2.8) — a tuning micro-correction.

### 3.3 Frequency Table

96 entries, C0 to B7. Split into separate lo/hi tables:

| Version | lo-table address | hi-table address |
|---------|-----------------|-----------------|
| 1.0     | `BASE+$0000`    | `BASE+$0060`    |
| 2.x     | `BASE+$003A`    | `BASE+$009A`    |
| 2.94    | `BASE+$00A0`    | `BASE+$00C1`    |

TFX 2.94 uses a **shorter lo-table (32 entries)** covering only the upper
pitch range (matching notes 64–95 of 2.8), with a hi-table of 95 entries
starting at `BASE+$00C1`. The engine references $10C1,Y for hi-byte lookups in 2.94.
This means 2.94 has a narrower playable pitch range or uses a different note-index
mapping vs 2.8. The exact 2.94 note-mapping semantics are not fully resolved
(see §9 Leads).

The frequency values are **TFX-proprietary** — they do not match standard PAL
C64 pitch tables. Example: C4 (note 48) = $C310 = 49936 = ~2932 Hz SID register
value (versus standard PAL ~4452). The engine applies these values directly to
$D400–$D401 per voice.

---

## 4. PSID Entry Points

| Version | init      | play      | Notes                                          |
|---------|-----------|-----------|------------------------------------------------|
| 1.0     | `$1106`   | `$1100`   | Play at different address; freq table at $1000 |
| 1.3     | `$1000`   | `$1003`   | Standard; OR init > $1FFF (multi-speed wrapper)|
| 2.7     | `$1000`   | `$1003`   | Standard; OR init=$0FF0 (pre-body wrapper)     |
| 2.8     | `$1000`   | `$1003`   | Standard (most common)                         |
| 2.93+   | `$1000`   | `$1003`   | Standard                                       |

**Subtune-select init variants** — when a SID has `init != $1000` (e.g. `$1FF5`,
`$24E0`, `$0FF0`), the PSID's init vector points to a **multi-speed / subtune
wrapper** that:
1. Sets CIA1 Timer A for a specific firing rate.
2. Optionally patches an SMC location with the subtune index.
3. Jumps to `$1000` (the standard engine init) or `$1003` (direct play entry).

Similarly when `play != $1003`, the PSID's play vector points to a wrapper that
may DEC a counter and call the real `$1003` every N frames.

**Relocation**: At least three HVSC TFX 2.8 SIDs run the engine at non-$1000
addresses (`$A000`, `$8240`, `$0C00`). These are full address-fixup relocations —
the engine structure is identical.

---

## 5. Init Sequence

The init routine at `BASE+$FA` (v2.8) / `$1106` (v1.0):

```
A = subtune_number (passed in .A register from PSID caller)
A <<= 3             ; multiply by 8 (subtune descriptor index)
SMC-patch LDY in voice-init sub (patches the Y offset)
Y ← A

Load song config from init-table[Y+6] → SMC $1183 (default D418 value)
Load song config from init-table[Y+7] → SMC $11BF (filter/vol default)

Loop for X = 0, 7, 14  (voices 1, 2, 3):
  Load pattern-ptr lo from init-table[Y+0] → $1901,X
  Load pattern-ptr hi from init-table[Y+1] → $1902,X
  Set $18D5,X = $18DA,X = $1904,X = $01  (speed counter, active flag)
  Write $D405,X = $00  (clear AD)   ← SIDId signature begins here
  Write $D406,X = $00  (clear SR)
  Write $D404,X = $08  (TEST bit = hard restart)  ← SIDId ends
  Set $18D6,X = $FF  (note duration sentinel)
  Clear 7 per-voice state slots in $186C–$1896 region
  X += 7 (advance to next voice)
```

**Hard-restart**: AD=0, SR=0, ctrl=TEST clears the voice oscillator without an
audible gate-on click. The gate-on happens on the first note-on in play().

**No explicit `$D418` write** in the standard init body — the default vol/filter
values are stored in SMC slots and written each frame by the play tail.

---

## 6. Play Sequence (Per-Frame)

Called at `play=$1003` (JMP $1172 in v2.8) once per VBL (50 Hz) or at CIA rate.

```
1. Save ZP $B1/$B2 on stack.
2. For X = 0, 7, 14 (each voice):
   a. Check $18DA,X (active flag). If 0: skip to SID-write sink.
   b. DEC $18D5,X (speed counter). If non-zero: skip to SID-write sink.
   c. Speed counter hit 0 → decode next pattern byte(s).
   d. Pattern byte dispatch (see §7).
   e. Update per-voice state.
3. SID-write sink ($13EB / $14CD region) per voice:
   STA $D406,X  (SR — sustain/release)
   STA $D405,X  (AD — attack/decay)
   STA $D404,X  (ctrl — gate / waveform / ring / sync / test)
   STA $D403,X  (PW hi)
   STA $D402,X  (PW lo)
   STA $D401,X  (freq hi)
   STA $D400,X  (freq lo)
4. Restore $B1/$B2.
5. Play tail — write global regs:
   STA $D418    (master vol | filter mode)   ← SMC value from $11BF / CMD_F9
   STA $D416    (filter cutoff fc)           ← SMC value from $11C6 / CMD_F8
   STA $D417    (filter resonance + routing) ← ORA-computed from SMC slots
```

**Voice stride = 7**: all per-voice state arrays use stride 7 (X=0,7,14) matching
the 7-register-per-voice SID layout. This means `STA $D400,X` with X=0/7/14
directly addresses the SID voice 1/2/3 frequency-lo registers.

**Write order within the voice sink**: SR before AD before ctrl. This matters for
ADSR timing: SR is set before the gate edge (ctrl). The envelope starts from the
gate-on in ctrl.

---

## 7. Pattern Byte Encoding

The pattern stream is read byte-by-byte with ZP indirect `LDA ($B1),Y`. Each
byte is a one-byte opcode (some commands read 1–3 additional argument bytes):

| Range        | Meaning                                                                    |
|-------------|----------------------------------------------------------------------------|
| `$00–$5F`   | **Note** index 0–95 (direct freq-table lookup → $D400/$D401 via $18D7,X) |
| `$60–$7F`   | **Arp/secondary speed**: `(b & $1F)` → `$18D9,X`                         |
| `$80–$BF`   | **Primary duration**: `(b & $3F)` → `$18D8,X` + `$18D5,X` (speed counter)|
| `$C0–$CF`   | **ADSR nibble**: `(b & $0F) << 4` → `$1883,X` (used for $D405 AD byte)  |
| `$D0–$ED`   | **Instrument/event select**: reads 1 arg byte; sets SMC loop-point        |
| `$EE`       | **Vibrato-start** (3-arg): speed, note/spd, base_note                     |
| `$EF`       | **Glide** (2-arg): glide_speed, note_offset → `$1872,X/$1871,X`; `$1870,X`=current|
| `$F1`       | **Set loop-back** (1-arg): position; sets `$119B=$FF` (filter-off mode)   |
| `$F2`       | **Set AD** (1-arg): arg → `$D405,X` immediately                           |
| `$F3`       | **Set SR** (1-arg): arg → `$D406,X` immediately                           |
| `$F4`       | **Set vibrato depth** (1-arg): arg → `$1897,X`                            |
| `$F5`       | **Gate-off mode** (1-arg): arg → `$1896,X`                                |
| `$F6`       | **Set note counter** (1-arg): arg → `$1904,X`                             |
| `$F8`       | **Global filter cutoff** (1-arg): arg → SMC `$11C6` + `$16B3`             |
| `$F9`       | **Filter mode + master vol** (1-arg): nibbles → SMC `$11CD` + `$11C1`     |
| `$FA`       | **Pulse width** (1-arg): nibbles → `$18DB,X`, `$189A,X`, `$189B,X`        |
| `$FB`       | **Filter cutoff/mode** (1-arg): arg → SMC `$11BF`                         |
| `$FC`       | **Toggle gate**: `$1882,X ^= 1` (flip gate bit), then re-read next byte   |
| `$FD`       | **Loop / jump**: reads loop-target Y offset; loops back in pattern         |
| `$FE`       | **Voice-off**: sets `$18DA,X = $00` (mutes voice)                         |
| `$FF`       | **Pattern end / next-segment**: transitions to next pattern or loops       |

**Duration mechanics**: Two counters coexist:
- `$18D5,X` = primary speed counter (decremented each frame; set by `$80–$BF`)
- `$18D9,X` = secondary/arp counter (set by `$60–$7F`)

A note in the pattern is followed by one or more duration bytes before the
next note. Both counters can be set per note-group; the engine appears to use
both for arpeggio-style effects vs held-note durations (exact interaction
between the two counters is not fully verified).

---

## 8. Effects Model

### 8.1 Vibrato

Commands `$EE` (in-pattern) and `$F4` (depth). State:
- `$1872,X` = vibrato speed
- `$1871,X` = vibrato target note-offset (+ transpose)
- `$1870,X` = vibrato current freq accumulator lo
- `$1897,X` = vibrato depth

The vibrato is applied in the freq-write region (`$1500–$1561` area) as a
bi-directional accumulator: each frame, the speed is added or subtracted from the
accumulator (`$18AD,X`), and the result is used to look up the freq hi/lo bytes
(`$103A,Y` and `$109A,Y`). When the accumulator crosses the target boundary the
direction reverses (`$1870 vs $1871` comparison at `$1507`). This is a
**register-relative vibrato** driven by speed and target-offset, not a sine-wave LFO.

### 8.2 Glide / Portamento

Command `$EF` (2-arg). Sets:
- `$1872,X` = glide speed
- `$1871,X` = target note offset (relative to current note + transpose)
- `$1870,X` ← set to current note in freq units

On each frame the glide accumulator is incremented by speed until the target is
reached; the freq write uses the accumulated value. Same accumulator/direction-flip
mechanism as vibrato.

### 8.3 Pulse Width

Command `$FA`. Stores the arg byte into `$18DB,X`; upper nibble × 16 → PW lo
(`$189A,X`), lower nibble → PW hi (`$189B,X`). The PW is written via
`$D402,X` / `$D403,X` in the SID-write sink. Whether the PW sweeps each frame
or is a static value needs further verification.

### 8.4 ADSR

- `$C0–$CF` commands: set the AD nibble inline in the pattern stream (attack/decay
  stored in `$1883,X`, later written to `$D405,X`).
- `$F2` command: directly writes arg to `$D405,X` (immediate AD set).
- `$F3` command: directly writes arg to `$D406,X` (immediate SR set).
- The instrument-select path (`$13EB` region) also reads AD/SR from a per-voice
  instrument table and can condition the write on `$18D5,X` countdown matching
  `$1904,X`.

### 8.5 Filter

Filter is **global** (not per-voice):
- `$D418` (master vol + filter mode): written each frame from SMC `$11BF` (or the
  play-tail computed value). Commands `$F9` and `$FB` update the SMC slots.
- `$D416` (filter cutoff): written each frame from SMC `$11C6`. Command `$F8`
  updates it globally for all voices.
- `$D417` (filter routing + resonance): written with an ORA-composed constant
  pattern in the play tail (`LDA #$01 / ORA #$A0 / STA $D417`).

The filter registers are written **after all three voices** in the play tail.

### 8.6 Waveform / Control

Waveform selection is via the `ctrl` byte written to `$D404,X`. The
instrument-select path (commands `$D0–$ED` region) reads instrument parameters
from a table at `$1914+` and sets the ctrl byte including the waveform bits. Gate
toggling is also possible via command `$FC` (`$1882,X ^= 1`).

---

## 9. Version Differences

| Version | HVSC count | Play addr  | Freq table base | Key differences                                    |
|---------|-----------|------------|----------------|---------------------------------------------------|
| 1.0     | 10        | `$1100`    | `BASE+$0000`    | Freq table at $1000; strings at $10C0; JMP at $1100|
| 1.3     | ~22+      | `$1003`    | `BASE+$003A`    | Multi-speed via play-wrapper DEC counter; CIA init |
| 2.7     | ~61       | `$1003`    | `BASE+$003A`    | Some init=$0FF0 (pre-body subtune wrapper)         |
| 2.8     | ~80       | `$1003`    | `BASE+$003A`    | Most common; CIA-timed multispeed via init wrappers|
| 2.93    | 7         | `$1003`    | `BASE+$003A`    | Minor engine updates; mostly structural like 2.8   |
| 2.94    | 7         | `$1003`    | `BASE+$00A0`    | Shorter lo-table (32 bytes); hi-table at $10C1     |
| 2.95    | 4         | `$1003`    | unknown         | Not inspected                                      |
| 2.97–99 | ~9        | `$1003`    | unknown         | Some have play_addr=0 (Sad's experiments)          |

The engine code between v2.7 and v2.8 shows only **~16 byte differences** in the
first $200 bytes of the init entry — most are address fixups for the different
song-data placement. The core play/decode engine is essentially the same.

Between v1.0 and v2.x the layout is more different (freq table moved, JMP vectors
moved) but the frequency content is nearly identical.

**SIDId has a single signature** covering all versions.

---

## 10. Multi-Speed / CIA Timing

Two mechanisms found in the corpus:

**CIA timer init wrapper** (v2.7/2.8, e.g. Bloedzuster, Anubis 1.3):
- PSID init vector → wrapper code that sets CIA1 Timer A to `$2663` = 9827 cycles
  → **100.3 Hz** (exactly 2× PAL 50 Hz).
- Then JMP `$1000` to do normal engine init.
- PSID `play` remains at `$1003`; PSID speed field = 0 (VBL-driven at 50 Hz in
  the player, but the CIA fires an independent IRQ at 100 Hz calling $1003).

**Play-wrapper counter** (v1.3 multi-speed):
- PSID play vector → wrapper at `$2008+` that DEC-s a counter SMC'd by init.
  Every other call (counter = 0): call real `$1003`. Otherwise: do nothing.
  Effective song rate = 2× if counter reset = 2, N× if reset = N.

**63× speed example** (Julian_Jaymz `63_speed_music_1.sid`, TFX 2.7):
- CIA Timer A = `$0888` = 2184 cycles → **451 Hz = 9× speed!**
- Init wrapper at `$1D8C`: patches subtune index via STX `$1D9F` (SMC).
- Then JMP `$1000`.

---

## 11. Tool / Player Handling

### SIDId / sidid.cfg

Single TFX signature in all known `sidid.cfg` variants (cadaver, WilfredC64,
DeepSID). No version sub-detection.

### DeepSID

No TFX-specific JavaScript handling found in the DeepSID source tree at
`/home/jtr/sidfinity/tmp/dmc_hunt/DeepSID/`. TFX is identified purely by
sidid.cfg signature lookup. No STIL annotations observed for the TFX engine type.

### libsidplayfp / VICE

No TFX-specific handling discovered. TFX uses standard PSID format; libsidplayfp
plays it as a normal PSID with the PSID metadata (init/play) fields set by the
tool that created the SID file. The CIA-timed variants will sound at the correct
speed if the PSID `speed` bit is set correctly (speed=0 = VBL; CIA-timed tunes
often rely on IRQ emulation).

### prg2sid / converters

Not investigated. TFX appears to produce self-contained PSID files with the
engine baked in; no external prg2sid conversion pipeline is known.

---

## 12. Binary Stability / Fingerprinting

The stable bytes in TFX 2.8 at `$1000–$10F9` (before song data):

- `$1000–$1008`: JMP vectors (3 × 3 bytes) — **stable opcode, variable addresses**
  (vary by relocation; standard = `4C FA 10 4C 72 11 4C 14 19`)
- `$1009–$1037`: version string — **stable delimiter structure**, version/title vary
- `$1038`: `21 21` = "!!" — **stable across all standard 2.8 instances**
  (this byte CANNOT serve as a signature since 0x27 appears in the freq table)
- `$103A–$10F9`: freq table — **stable content** across all v2.8 instances;
  exactly matches known PAL TFX2.8 freq table
- Engine code `$10FA–$1BCC`: stable in 2.8; ~16 byte address-fixups in 2.7 vs 2.8;
  structural differences in 2.94+

For **fingerprinting** (relocation-invariant): the freq-table LO bytes
(`$103A–$1099` in standard layout, stride=1) are stable and unique to TFX.
A hash of those 96 bytes would distinguish TFX from other engines.

---

## 13. Init Table Format

Located after the engine code, typically around `$1BCF+` in v2.8. Structure:
**8-byte records**, one per subtune, indexed by `Y = subtune_number × 8`:

```
[0]  V1 pattern ptr lo    → stored to $1901,X (voice 1)
[1]  V2 pattern ptr lo    → stored via 2nd init-sub call (voice 2)
[2]  V3 pattern ptr lo    → stored via 3rd init-sub call (voice 3)
[3]  ptr2 lo              (secondary orderlists or same voice)
[4]  ptr2 hi
[5]  ?
[6]  $D418 init lo        → SMC $1183 (filter/vol default)
[7]  $11BF init val       → SMC $11BF (per-frame filter/vol value)
```

The pattern pointers are 16-bit LE addresses within the SID binary's song-data region.

---

## 14. Gaps and Caveats

1. **Freq table tuning**: TFX uses a non-standard freq table (differs from standard
   PAL C64 values). The musical pitch accuracy vs hardware has not been ear-tested.

2. **TFX 2.94 note-index mapping**: The 32-byte lo-table means note-byte `$00` in
   the pattern maps to a different musical pitch than in v2.8. The exact mapping
   between note byte and pitch in 2.94 is not resolved.

3. **$60–$7F dual-counter interaction**: The relationship between the `$18D9,X`
   secondary counter and `$18D5,X` primary counter is not fully traced. Arpeggio
   vs. tempo semantics unclear.

4. **$D0–$ED instrument select**: The 30-byte command range points to a loop-point
   SMC mechanism. Whether these select waveforms, instruments, or sub-patterns is
   not verified from the disasm alone.

5. **Pulse width sweep**: `$FA` sets PW registers; whether TFX sweeps PW each frame
   is unclear from static analysis.

6. **Multi-subtune SIDs**: Walking_Death (7 songs, play=`$2043`), Schlimeisch_Mania_II
   (6 songs, play=`$82A3`), Kikstart_2012 (2 songs, play=`$BF03`) use unusual
   play addresses and likely have per-subtune wrappers not yet decoded.

7. **TFX 2.97–2.99 struct**: Only 1–3 SIDs per sub-version; some have
   `Still_a_Failure.sid` with `play=0` (broken). Not inspected at binary level.

---

## Leads to Follow

1. **Inspect TFX 1.0 pattern encoder** — the v1.0 play entry at `$1100`/`$117E`
   may have slightly different pattern-byte semantics; compare the dispatch table
   at the equivalent of `$124B` in Africa.sid.

2. **TFX 2.94 note-index resolution** — check Silly_Synth_Song.sid with libsidplayfp
   vs siddump to verify which actual pitches note indices map to; compare freq
   values in the 2.94 shorter table against the 2.8 table.

3. **Multi-subtune walking wrappers** — disassemble Walking_Death.sid play=`$2043`
   to understand how TFX 2.8 implements multi-song playback.

4. **Arpeggio / `$18D9,X` counter** — trace what consumes the secondary speed
   counter in the SID-write sink to understand if TFX supports arpeggio sequences.

5. **CSDb TFX v1.2 / v2.4 disk images** — these contain the actual tracker UI
   and may include a bundled `DOCS` or instruction screen that documents the
   pattern byte commands from the composer perspective. Archive.org has the d64.

6. **`$0FF0` pre-body wrapper** — 30 TFX 2.7 SIDs have `init=$0FF0` (before
   player body). Decode those 16 bytes to see if it's always CIA setup + subtune
   selection or something else.

7. **Full CSDb scener page for Ray** — CSDb id for Ray/Unreal was not found
   directly; search `https://csdb.dk/scener/?handle=Ray&group=Unreal` or browse
   the Unreal group page to find all tool releases and any documentation files.

8. **Woolyss chiptrackers page** — `https://woolyss.com/chipmusic-chiptrackers.php`
   may have a TFX entry with a short feature description from the tracker UI
   screenshots (not yet fetched).
