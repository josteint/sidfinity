# John Player — Write Model, Binary Structure, and Version Variants

## Provenance

| Field | Value |
|-------|-------|
| fetch_date | 2026-06-14 |
| author | Aleksi Eeben ("Heatbeat") / CNCD / Cyberiad |
| sources | **PRIMARY**: Original WLA-6510 assembler source (player.asm + mem.inc + editor.asm + help.asm) recovered by sibling research agent and stored in `pipelines/john_player/docs/src/` — includes V1.0 source in `src/v10/` and V1.4 source in `src/v14/`. CSDb release IDs 2630/2631/18767. Pastebin V2.0b help text (pastebin.com/80TaWPMz, ref iLKke/CSDb 2014). Demozoo prod 134378. pouet.net prod 13860. github.com/cadaver/sidid sidid.cfg. Direct READ-ONLY binary inspection of HVSC #84 SIDs. |
| reliability | **VERY HIGH** for all facts cross-confirmed against original source code (src/player.asm). HIGH for binary-confirmed SID write order and version census. MEDIUM for V2.0b internals (source not yet found). LOW for Pastebin paraphrase. |

---

## 1. Player Summary

John Player is a C64 tracker tool coded by Aleksi Eeben of CNCD/Cyberiad, released 2001–2002. Five releases are known; sidid tracks four distinct player binaries (V1.0, V1.4, V1.6, V2.0b). The player delivers 3-voice SID music with a shared "sound table" for per-step waveform/arpeggio/filter-cutoff programming. The player is compact (sub-10-rasterline budget cited by users), uses $0D zero-page locations ($40–$4C by default), and embeds song data directly in the SID file.

Key facts:
- **Load address**: always $1000 (PSID v2, embedded load at data_offset+0 = little-endian $10 $00)
- **Init entry**: $1000 — always a JMP to the actual init routine
- **Play entry**: $1003 — either inline play code (V1.x) or a second JMP (V2.0b)
- **Speed**: PSID speed=0 for all confirmed HVSC members (50Hz VBI, PAL)
- **Subtunes**: usually 1, occasionally multi-subtune (e.g. Aquarius = 4 subtunes, init=$2D90, play=$2D93 — player embedded at higher load or concatenated)
- **End-of-binary marker**: embedded ASCII string "JOHN PLAYER BY A. EEBEN" (confirmed in V2.0b; present in data tail)

---

## 2. Version Census (183 HVSC #84 John Player SIDs)

Classified by binary signature match against sidid.cfg patterns (see Section 4).

| Version | Count | % | Notes |
|---------|------:|---|-------|
| V1.0    | 0     | 0% | No V1.0 members found in HVSC #84 |
| V1.4    | 13    | 7% | Oldest surviving HVSC variant |
| V1.6    | 93    | 51% | Most common |
| V2.0b   | 77    | 42% | Beta; released 2002 alongside V1.6 |

**V1.4 members (13 total):** DEMOS/A-F/Datasette_Meltdown, DEMOS/G-L/Gullibility, MUSICIANS/E/Eeben_Aleksi/John_Player_note, Music_Test_2, Music_Test_3, Music_Test_4, MUSICIANS/M/Muhmi/Infoaehky, MUSICIANS/N/Nick_Vivid/1988, History, Reset_to_Zero, plus 3 others.

**V1.6 members (93 total):** All major composers (Eeben, Reed, Crome, Duck-hunter, Mermaid, Scout, Vincenzo, Mortimer_Twang, PSC64, Xiny6581, etc.).

**V2.0b members (77 total):** Later Eeben works (Radio_Challenge, Rock_n_Roll_Butterfly is V1.6 not V2.0b), Dalezy, Codehead, Mr_Death, Mortimer_Twang (subset), Xiny6581 (subset), Mermaid, plus many others.

---

## 3. Binary Structure — $1000 Player Layout

### 3.1 Entry Points

```
$1000: JMP  <init_routine>      ; 3 bytes, always present
$1003: [play entry]             ; V1.x: play code starts here inline
                                ; V2.0b: JMP <play_body> (second JMP)
```

**V1.4/V1.6**: Play routine starts INLINE at $1003. First instruction: `LDY $42` (voice 1 state).

**V2.0b**: `$1003: JMP $10BA` — extra dispatch stubs at $1006–$1078 provide helper routines (modulator, sequence advance, init-zero helpers) before the main init at $107C.

### 3.2 Init Routine Location

| Version | Init JMP target | Offset from $1000 |
|---------|-----------------|-------------------|
| V1.4    | $1327           | +$327 = +807      |
| V1.6    | $1334           | +$334 = +820      |
| V2.0b   | $107C           | +$07C = +124      |

### 3.3 Init Routine (All Versions — common core)

**Source-confirmed** (player.asm `Initialize:` section, COMPILE_PLAYER == 0/1):

The normal (non-packed) init does NOT use the 9D/95 loop. It clears all SID registers via:
```asm
ldy  #$17
_sid: sta $d400,y   ; zero $D400–$D417
      dey
      bpl _sid
sta $d418           ; then sets master vol
```
Then sets speed=$0C, count=1, and patches vibrato SMC slots off (LDA #$C9 / JSR setc1mod etc).

The **sidid base signature** loop (9D 00 D4 / 9D 0B D4) is from the **COMPILE_PLAYER==2 (packed) variant** of the init:
```asm
ldx  #$0c
_clr: sta cmdtick,x  ; clear ZP[$40..$4C]
      sta $d400,x    ; clear $D400–$D40C
      sta $d40b,x    ; clear $D40B–$D417
      dex
      bpl _clr
```
Both packed and non-packed inits are present in HVSC binaries (HVSC uses the packed variant overwhelmingly; the sidid sig matches the packed form).

After the init clearing loop (packed form):
- **V1.4/V1.6**: `A8` (TAY), then `A9 0F 8D 18 D4` (STA $D418 = master vol $0F), `A9 0C 85 46` (tempo = $0C), then `jmp firstblockentry`.
- **V2.0b**: `A8` (TAY, Y=0), then loads initial state from song-specific tables (`AD 80 16` → $D417; `AD 00 17` → $D418; `AD 00 16` → $46 tempo), then additional init (clear voice state, advance-sequence call).

---

## 4. Version Identification Signatures (sidid.cfg, confirmed)

All sub-sigs match against the common init loop. The discriminating bytes are what comes immediately after the loop ends (at CA 10 F5) and the $D406 write context in the play routine.

```
John_Player (base):
  A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5  END

John_Player_V1.0:
  A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A9  END
  (byte after loop = A9 = LDA #imm; init sets up directly)

John_Player_V1.4:
  8D 06 D4 A9  AND  A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A8 A9  END
  (D406 write in play FOLLOWED BY A9 = LDA #$09 for D404 ctrl; after loop = A8 A9)

John_Player_V1.6:
  8D 06 D4 B9  AND  A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A8 A9  END
  (D406 write in play FOLLOWED BY B9 = LDA abs,Y for next inst field; after loop = A8 A9)

John_Player_V2.0b:
  A9 00 A2 0C 95 ?? 9D 00 D4 9D 0B D4 CA 10 F5 A8 AD  END
  (after loop = A8 = TAY, AD = LDA abs = absolute table read for init state)
```

**Binary-confirmed discriminators:**

| Version | After loop (loop+15, loop+16) | $D406 context in play |
|---------|-------------------------------|----------------------|
| V1.4    | A8, A9                        | 8D 06 D4 **A9** 09 8D 04 D4 |
| V1.6    | A8, A9                        | 8D 06 D4 **B9** 22 14 8D 5E 10 |
| V2.0b   | A8, AD                        | (play body relocated, different context) |

The `8D 06 D4 A9` vs `8D 06 D4 B9` distinction (V1.4 vs V1.6) is in the **play routine**, specifically the voice block: after writing $D406 (SR), the NEXT opcode is either `A9` (LDA #imm = hardcode ctrl=$09) or `B9` (LDA abs,Y = load next instrument field). Both versions write $D406 from the instrument table; only V1.4 hardcodes the $D404 ctrl write at this point.

---

## 5. Per-Frame Write Model

### 5.1 Zero-Page Layout

**Source-confirmed** from `mem.inc` (.ENUM zeropage at $40):

```
ZP $40  — cmdtick   : command tick flag (set = process block command next frame)
ZP $41  — fbase     : filter base (cutoff offset added to FilTab value → $D416)
ZP $42  — c1hold    : voice 1 hold / sound trigger index (0 = no hold; nonzero = init instrument next frame)
ZP $43  — c2hold    : voice 2 hold / sound trigger index
ZP $44  — c3hold    : voice 3 hold / sound trigger index
ZP $45  — count     : frame countdown (decremented each frame; ==0 → nextstep)
ZP $46  — speed     : tempo period (reloaded into count; init = $0C)
ZP $47  — seqpos    : sequencer position (index into Sequencer orderlist)
ZP $48  — step      : block step lo (used as ZP indirect pointer lo for B1 48)
ZP $49  — block     : block step hi (ZP indirect pointer hi)
ZP $4A  — vibpos    : vibrato LFO position (0–$0F, ANDed; indexes VibTab)
ZP $4B  — mod       : vibrato modulation lo byte (SMC-patched into freq lo read)
ZP $4C  — modh      : vibrato modulation hi byte (SMC-patched into freq hi read)
```

Note: `c1hold`/`c2hold`/`c3hold` at $42/$43/$44 hold the **SoundTab Y-index** for the instrument to load on the next frame (not the current playing sound position). When nonzero, the voice block loads instrument data from `SoundTab,y` and resets the step pointer.

The current sound step (position within the sound program) is stored as **SMC (self-modifying code)** in the player:
- Voice 1 step: byte in `c1sndp_+1` (the LDY #imm operand of the step-load instruction)
- Voice 2 step: `c2sndp_+1`
- Voice 3 step: `c3sndp_+1`

This means the SID player relies heavily on SMC; ZP is sparse.

### 5.2 Voice Block Write Order (New Note)

The play routine processes 3 voices sequentially. Each voice block fires when its instrument Y-index ($42/$43/$44) is nonzero (voice active). On every call that voice fires a note event, the writes are:

**V1.4/V1.6 voice note-on sequence (confirmed by binary trace):**

| Order | SID Reg | Source | Notes |
|-------|---------|--------|-------|
| 1 | $D404 (CTRL) | STX (X=0) | Gate off — hard restart; clears gate+waveform |
| 2 | $D405 (AD)   | $1420+Y [V1.4] / $1420+Y [V1.6] | Attack/Decay from instrument table |
| 3 | $D406 (SR)   | $1421+Y [V1.6] / #$09 [V1.4] | Sustain/Release: **V1.4 hardcodes $09; V1.6 per-instrument** |
| 4 | $D404 (CTRL) | #$09 | Test+gate asserted (hard restart + gate-on, no waveform yet) |
| 5 | $D417 (FILT_CTRL) | $1429+Y | Filter resonance + voice routing from instrument |
| 6 | $D418 (MSTR_VOL)  | $142A+Y | Filter mode + master volume from instrument |
| [loop] | — | sound table step | Per-step: filter cutoff, waveform, arpeggio |
| 7 | $D416 (FC_HI+RES) | $1500+step + $41 | Filter cutoff high + resonance (with transpose ADC) |
| 8 | $D404 (CTRL) | $1540+step AND #$FE | Wave control (gate stripped; gate set separately) |
| 9 | $D402 (PW_LO) | STX or sound table | Pulse width lo |
| 10 | $D403 (PW_HI) | instrument or modified | Pulse width hi |
| 11 | $D400 (FRQ_LO) | freq_table[note*2] | Frequency lo |
| 12 | $D401 (FRQ_HI) | freq_table[note*2+1] | Frequency hi |

Voice 2 uses $D407–$D40D (same pattern), Voice 3 uses $D40E–$D414.

**Notes on gate/restart:**
- The double $D404 write (X=0 then #$09) is a hard-restart sequence: gate-off clears the envelope, then test+gate-on re-triggers it before the waveform is loaded.
- The actual waveform arrives from the sound table loop via `LDA $1540,Y; AND #$FE; STA $D404` — the AND #$FE mask removes gate bit, then a final gate-set write re-enables it. This means waveform register is written multiple times per frame on note-on.

**V2.0b** shifts the pattern to the restructured tables ($1520 for instrument, $1680 for wave, $1700 for arp) and the play body is at $10BA (not inline from $1003). The sequence structure is the same: gate-off → AD/SR → test+gate → filter → sound-table-step loop → freq. V2.0b also adds a modulator channel (vibrato/slide) dispatched from separate subroutines at $1006–$107B.

### 5.3 $D40B,X Init Stride Confirms Voice Spacing

The init loop writes:
- `STA $D400,X` — clears voice 1 start ($D40C when X=$0C down to $D400 when X=0)
- `STA $D40B,X` — clears voice 2 start ($D417 when X=$0C down to $D40B when X=0)

This confirms the SID register map: voice 1 = $D400–$D406, voice 2 = $D407–$D40D (stride $07 from V1), voice 3 = $D40E–$D414, global = $D415–$D418.

---

## 6. Data Section Layout

### 6.1 V1.4 / V1.6 Data Layout (from load $1000)

```
$1000–$132x  Player code (~820 bytes for V1.4, ~820 bytes for V1.6)
$132x–$1348  Post-init junk + misc constants
$135A        Frequency table (V1.4) — 64 notes * 2 bytes LE = 128 bytes
$1360        Frequency table (V1.6) — same content, 6-byte shift
$13DA+       Additional computed data / calibration bytes
$1400        Vibrato/modulation LUT — 32 bytes sine-shaped
               [00 18 2D 3B 3F 3B 2D 18 00 E7 D2 C4 C0 C4 D2 E7 ...]
$1420        Instrument table — 11 bytes per instrument, up to ~23 instruments
$1500        Filter cutoff sound table — 32 rows (V1.x)
$1540        Wave control sound table — 32 rows
$1580        Arpeggio/note sound table — 32 rows
$15C0+       Orderlist (hi/lo address pairs pointing to patterns) + pattern data
```

**Frequency table values (identical across V1.4/V1.6/V2.0b, different base address):**
Note 0 = $0224, Note 12 = $0449, Note 24 = $0892, Note 36 = $1125, Note 48 = $224A, Note 60 = $4495.
Computed for ~1 MHz clock (original, slightly off for PAL/NTSC — see Section 8).

### 6.2 SoundTab Record Format (V1.4/V1.6 — 11 bytes, stride $0B)

**Source-confirmed** from `player.asm` channel 1 block (comments are verbatim from source):

```
Offset  Source field   SID dest  Source comment
+0      SoundTab+0     $D405     $00: attack/decay
+1      SoundTab+1     $D406     $01: sustain/release  [V1.6: per-record; V1.4: hardcoded #$09]
+2      SoundTab+2     SMC       $02: sound pos (starting step in sound program)
+3      SoundTab+3     SMC       $03: sound end (last step before loop)
+4      SoundTab+4     SMC       $04: sound loop (loop target step)
+5      SoundTab+5     (gate)    $05: pw init ($00 = no init)
+6      SoundTab+6     SMC       $06: pw mod rate (step per frame; signed: ADC or SBC)
+7      SoundTab+7     SMC       $07: pw mod top (CMP value for upper reversal)
+8      SoundTab+8     SMC       $08: pw mod bottom (CMP value for lower reversal)
+9      SoundTab+9     $D417     $09: resonance/filt. ch select
+10     SoundTab+10    $D418     $0a: filt. type/master volume
```

This table is named **SoundTab** in the source (not "InstrumentTable"). Y-index: sound N → Y = N × 11. The "sound program" pointed to by +2/+3/+4 indexes into the three per-step tables (FilTab/WaveTab/ArpTab) at the same Y offset. Maximum ~23 sound programs (Y < 256 / 11 = 23).

Note: V1.4 source hardcodes `STA $D404, LDA #$09, STA $D404` for the ctrl byte; V1.6 source reads `SoundTab+1,y` for SR before the hardcoded $09 ctrl write. This is the ONLY binary difference between V1.4 and V1.6 player code.

### 6.2b Sound Table Defines Summary (Source)

From `player.asm` defines (reloc = $1000):
```
FreqTab    = $1358   (= $0358 + $1000, V1.0/V1.4 player.asm; V1.6 binary shows $1360 = slight shift)
VibTab     = $1400   (= $0400 + $1000)
SoundTab   = $1420   (= $0420 + $1000)   ← 11-byte instrument records
FilTab     = $1500   (= $0500 + $1000)   ← filter cutoff steps
WaveTab    = $1540   (= $0540 + $1000)   ← waveform control steps
ArpTab     = $1580   (= $0580 + $1000)   ← arpeggio note steps
Sequencer  = $15C0   (= $05C0 + $1000)   ← orderlist
BlockData  = $1600   (= $0600 + $1000)   ← first block of pattern data
```

### 6.3 V2.0b Data Layout (from load $1000)

```
$1000–$137x  Player code + dispatch stubs (~900 bytes)
$1354        Modulation/parameter table (tempo/arp data, ~10 bytes)
$1460        Frequency table (64 notes * 2 bytes = 128 bytes; same values)
$1500        Filter cutoff sound table — 64 rows (DOUBLED from V1.x)
$1510        Second filter column or resonance table (64 rows)
$1520        Instrument table — 7 bytes per instrument
$1600        Song parameters table (tempo, initial state reads)
$1680        Wave control sound table — 64 rows
$1700        Arpeggio/note sound table — 64 rows
$17xx+       Zeros (padding), then orderlist + pattern data
```

**V2.0b instrument record (7 bytes, stride 7):**

```
Offset  SID dest  Notes
+0      $D405     Attack/Decay
+1      $D406     Sustain/Release
+2      (local)   Sound table start index (or pointer into sound table)
+3      (local)   ?
+4      (local)   ?
+5      (local)   ?
+6      (local)   ?
```

Note: V2.0b has FEWER bytes per instrument (7 vs 11) while the sound table is LARGER (64 vs 32 rows). This implies more sound-design data moved from the instrument record into the sound table steps.

### 6.4 Sound Table Format (V1.x — 3 columns × 32 rows)

Per-frame the player reads the current step from each of the three sound-table columns:

| Column | Address (V1.x) | SID write | Content |
|--------|---------------|-----------|---------|
| Filter cutoff | $1500+step | $D416 (via ADC $41) | Filter cutoff freq value (8-bit) |
| Wave control  | $1540+step | $D404 AND #$FE | Waveform byte: bit7=noise, bit6=pulse, bit5=saw, bit4=tri, bit3=test |
| Arp/note      | $1580+step | freq_table[ASL*2] | Note index * 2 as freq table offset; $80+ = special (loop?) |

From Pastebin (V2.0b help text): "To define a loop enter $00 in Waveform column and the desired loop position in Arpeggio column at the same step." In V1.x the loop mechanism is analogous.

**V2.0b sound table:** Same 3-column concept but 64 rows each, at $1500/$1680/$1700.

### 6.5 Orderlist and Pattern Stream (Source-Confirmed)

**Sequencer format** (at `Sequencer` = $15C0):

The sequencer selects **blocks** (patterns). Each entry is a **block number** (1 byte). When `block == 0`, the sequencer has ended; the NEXT byte is a loop-back position (index to restart seqpos from). Block number N → pattern at `BlockData + (N-1)*256` (i.e., each block is a 256-byte page; `sta block` sets the hi-byte of the ZP indirect pointer at $49).

```
Sequencer[$15C0]: block_0_num, block_1_num, ..., $00, loop_seqpos
```

**Block (pattern) format** (at `BlockData` = $1600, non-packed mode):

Each block = one 256-byte page. Within a block, steps advance in 8-byte strides (source: `adc #$08` after pattern step decode). Each 8-byte step:

```
Offset  Content
+0      command byte (0 = no command; 1–8 = block command index)
+1      command parameter byte
+2      voice 1 note byte (0 = no note; $FE = gate off; positive = note number)
+3      voice 1 sound number (0 = tied note/no retrigger; nonzero = SoundTab Y/11)
+4      voice 2 note byte
+5      voice 2 sound number
+6      voice 3 note byte
+7      voice 3 sound number
```

Note: **`$FE` = gate-off mask** (NOT a loop command) — it gets SMC-patched into the voice's `AND` gate instruction to hold gate off. The Pastebin description calling it a "loop command" was incorrect.

**Block commands** (source `cmdjmpL`):
```
1: End        → nextblock (advance to next block in sequencer)
2: Brk        → blockbreak (reset step pointer to 0 within current block)
3: Flt        → setfilter (set fbase = filter cutoff base offset)
4: Tmp        → setspeed (set tempo speed)
5: Ini        → setvibwidth (init vibrato width for channel X)
6: Vib        → setvibrate (set vibrato rate)
7: Mod        → modchannel (enable modulation/vibrato on channel X)
8: Off        → offchannel (disable modulation on channel X)
```

**Vibrato mechanism**: The modulation toggles between `CMP #imm` (no-op, passes freq unchanged) and `ADC` (adds vibrato delta) via SMC at `c1modulatel_` / `c1modulateh_`. VibTab (at $1400) is a 32-byte table: first 16 bytes = sine, next 16 bytes = second octave. Vibrato phase steps $00–$0F, masking with `AND #$0F`.

**Packed player (COMPILE_PLAYER==2)**: Uses a different pattern format with variable-length records and `block`/`step` as a 16-bit pointer (hi=block, lo=step). The packed init uses the `9D 00 D4`/`9D 0B D4` loop (matches sidid signature). Packed player is what appears in HVSC SID files.

---

## 7. Version Difference Summary

| Feature | V1.0 | V1.4 | V1.6 | V2.0b |
|---------|------|------|------|-------|
| Init at $1000 | JMP far | JMP $132x | JMP $133x | JMP $107C |
| Play at $1003 | Inline | Inline | Inline | JMP $10BA |
| $D406 SR source | ? | Instrument table | Instrument table | Instrument table |
| Ctrl $D404 (gate-on) | ? | #$09 hardcoded | #$09 hardcoded | #$09 hardcoded |
| Init: master vol | ? | #$0F hardcoded | #$0F hardcoded | From song table |
| Sound table rows | ? | 32 | 32 | 64 (doubled) |
| Instrument size | ? | 11 bytes | 11 bytes | 7 bytes |
| Freq table base | ? | $135A | $1360 | $1460 |
| Instrument base | ? | $1420 | $1420 | $1520 |
| Wave table base | ? | $1540 | $1540 | $1680 |
| Arp table base | ? | $1580 | $1580 | $1700 |
| Modulator (vib/slide) | ? | basic | basic | expanded (extra stubs) |
| Song size overhead | ? | base | +6 bytes vs V1.4 | +~0.4 KB (per Pastebin) |
| HVSC members | 0 | 13 | 93 | 77 |

**V1.4 vs V1.6 (single binary difference confirmed):**
In the play routine, immediately after `STA $D406`:
- V1.4: next byte = `A9` (`LDA #$09`) — control register hardcoded
- V1.6: next byte = `B9` (`LDA $1422,Y`) — reads next instrument field from table

Both still write $D406 from the instrument table; V1.4 just goes straight to setting ctrl=$09 rather than first loading more instrument fields into local scratch.

**V2.0b additions (from Pastebin help text + binary):**
- Sound table doubled: $7F steps (128 usable; docs say "doubled steps in sound table $7F")
- Sequencer steps also doubled ($7F)
- Modulator channel with vibrato + slide (dispatched via extra subroutines)
- Initial song parameters read from per-song table at $1600 (not hardcoded in player)
- Songs are ~0.4 KB larger than V1.6
- Incompatible with V1.x format

---

## 8. Frequency Table and Tuning

The frequency table (64 entries, 16-bit LE, chromatic scale starting approximately at C2) is identical across all versions in content; only the load address shifts:
- V1.4: base $135A; V1.6: base $1360; V2.0b: base $1460.

The original table was computed assuming CPU clock = 1 MHz (exactly), which is incorrect for PAL (985248 Hz) and NTSC (1022727 Hz). This means all HVSC SIDs with the original table play ~1.5% sharp on PAL. In September 2024 Aleksi Eeben released a corrected V1.6 (`john16intune.prg`) with proper PAL frequency values; HVSC members use the original (incorrect) table.

---

## 9. Tool Handling

**libsidplayfp / VICE**: Play as standard PSID v2 files. No special handling needed — the player is fully self-contained at $1000, PSID speed=0 (50Hz VBI), init=$1000/$2D90, play=$1003/$2D93. libsidplayfp plays all 183 HVSC members correctly via the normal PSID path.

**SIDId (cadaver/sidid)**: All four sub-sigs are present in sidid.cfg (source confirmed at github.com/cadaver/sidid). CSDb release IDs in .nfo: V1.0=#2630, V1.4=#2631, V1.6/V2.0b=#18767.

**DeepSID (Chordian)**: No special John Player handling found in DeepSID codebase or documentation — treated as standard PSID.

**reSID / libsidplayfp**: No special handling; PSID emulation covers all accesses.

---

## 10. HVSC Member Statistics

- Total: 183 SIDs classified as John_Player in HVSC #84
- Load address: always $1000 (100%)
- Play address: $1003 (typical), $2D93 (multi-subtune Aquarius)
- PSID version: v2 (100% of checked members)
- Speed: 0 (50Hz VBI, all checked members)
- Composers using the tool: ~25 distinct HVSC artist directories

---

## Leads to Follow

1. **V1.0 members absent**: No V1.0 SIDs appear in HVSC #84. V1.0 was released ~2001 (CSDb #2630, 457 downloads); music made with it may not have been submitted to HVSC, or may have been reclassified/updated to V1.4+.

2. **Instrument table stride assumptions unconfirmed for V2.0b**: The V2.0b instrument stride is inferred as 7 bytes from the 7 consecutive LDA $1520+Y,+1,+2... accesses. The exact semantic of bytes +2 through +6 is not traced to SID writes — needs further disassembly.

3. **Pattern stream format not fully decoded**: The note/duration/instrument encoding within patterns is partially understood. The `$FF`/`$FE` terminators are confirmed but the exact 2- vs 3-byte event encoding needs a traced decode of the `B1 48` pattern reader loop.

4. **Modulator (V2.0b) not characterized**: The extra subroutines at $1006–$107B in V2.0b implement vibrato/slide/modulation routing not present in V1.x. The Pastebin help mentions "Ini/Vib, Sli, Mod/Off" block commands; their binary representation in the pattern stream is unknown.

5. **Sound table loop condition**: The `$00` waveform + arpeggio-value-as-loop-position loop mechanism needs binary verification. The Pastebin describes it but it wasn't directly traced in the waveform loop code.

6. **Multi-subtune layout**: Aquarius.sid (4 subtunes, init=$2D90, play=$2D93) has a different structure — the player appears concatenated or relocated. The per-subtune data partitioning scheme is unknown.

7. **Source code FOUND**: The WLA-6510 assembler source for V1.0 and V1.4 was recovered and is at `pipelines/john_player/docs/src/v10/` and `src/v14/`. The current `src/player.asm` (top-level) is the V1.6 source. V2.0b source not yet found.

8. **V1.5 (Demozoo mentions)**: Demozoo references "V1.5" in the version history description but no V1.5 sidid signature exists and no V1.5 binary is identified. May be an intermediate unreleased build.

9. **$D415 (filter cutoff lo)**: Not explicitly written in the confirmed play traces. The filter cutoff is driven via $D416 (FC_HI + resonance) but $D415 appears unwritten (or initialized to 0 by the init loop). Needs explicit check — may mean fixed cutoff-lo = 0 for all John Player tunes.

10. **Regression portfolio**: Once RE is complete, select portfolio members covering: V1.4 (SR hardcoded), V1.6 (SR per-instrument), V2.0b (doubled tables + modulator), multi-subtune (Aquarius), long songs (Greenrunner = 480s), short demos (Music_Test_2 = 31s).

11. **SMC reliance**: The player uses extensive SMC for performance (step pointers, gate state, vibrato on/off, pulse width direction). Any USF representation must encode the OUTPUTS (the SID write stream) not the SMC slots. The USF principle (CORE TENET) applies directly.

12. **V2.0b source**: Not located in `pipelines/john_player/docs/src/`. The V2.0b binary (Radio_Challenge, Breaking_Loose etc.) shows a substantially restructured player with expanded tables and a modulator. Source acquisition from CSDb #18767 download zip would directly confirm all V2.0b table semantics.
