# Jeff SID Player — Write Model, Binary Structure, and Variant Analysis

## Provenance

| Field | Value |
|---|---|
| source_url (sidid.cfg) | https://github.com/cadaver/sidid/blob/master/sidid.cfg |
| source_url (sidid.nfo) | https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo |
| source_url (interview) | https://remix64.com/interviews/interview-soren-jeff-lund.html |
| source_url (CSDb scener) | https://csdb.dk/scener/?id=8059 |
| source_url (CSDb music editor) | https://csdb.dk/release/?id=122334 |
| source_url (CSDb X-SID) | https://csdb.dk/release/?id=47985 |
| source_url (CSDb FLT demo) | https://csdb.dk/release/?id=17292 |
| fetched_via | WebFetch + WebSearch + READ-ONLY hvsc85/ binary inspection |
| fetch_date | 2026-06-14 |
| author | Søren Lund (Jeff), born 1974, Denmark, d. 2013-12-01 |
| reliability | HIGH (binary inspection of canonical SIDs: Action_Hunter.sid V9.6, Birdie_Pip.sid V7, Cool_Fool.sid V4, 6581_Doped_Cows.sid X-SID, plus group variants); sidid.nfo confirmed attributions |

---

## 1. Author and Version History

Søren "Jeff" Lund (1974–2013) was a Danish C64 composer who developed his own SID player from scratch, writing approximately 30 versions across his scene career (stated in the Remix64 interview). He composed the vast majority (≥178/192) of the tunes in his HVSC directory himself.

**Group timeline (from CSDb scener #8059):**

| Period | Group | Handle used in credits |
|---|---|---|
| 1991–1992 | X-Factor (XF) | Joss / Jeff |
| 1992 | Daniax | Jeff |
| 1992–1993 | Imagination Developments | Jeff |
| 1992–2013 | Camelot (CML) | Jeff |
| 1993–2003 | Cyberzound Productions (CZP) | Jeff |
| 1999–2013 | Crest | Jeff |
| 1999–2013 | Bonzai | Jeff |
| 2003–2013 | Viruz (VRZ, founded by Jeff) | Soren |
| 2006–2013 | Cosine | Jeff / Soren |

**Player version strings found in HVSC binaries** (from READ-ONLY byte scan, `hvsc85/MUSICIANS/J/Jeff/*.sid`):

| String | Example SID | ~Year |
|---|---|---|
| `PLAYER (C) 1992 S0REN LUND/XF` | Profitless.sid | 1992 |
| `PLAYER & MUSIC BY JEFF OF X-FACTOR (S0REN LUND) IN1992.` | House.sid | 1992 |
| `PLAYER & MUSIC BY JOSS OF X-FACTOR (S0REN LUND) IN1992.` | Acid.sid, Colic.sid | 1992 |
| `PLAYER V4 (C) S0REN LUND.` | Cool_Fool.sid, Music_001.sid | ~1992 |
| `PLAYER V7 (C) 1992 S0REN LUND.` | Birdie_Pip.sid (and 16 others) | 1992 |
| `PLAYER V7 (C) S0REN LUND OF ID` | Beginning.sid | 1992 |
| `PLAYER V8 +MUSIC (C) 1992 JEFF` | Soft-Ice_2.sid | 1992 |
| `PLAYER V9 (C) JEFF OF CAMELOT!` | Fiskeaande.sid | 1993 |
| `PLAYER V9.1+ & MUS BY JEFF/CML` | Cave_of_Rave.sid | 1993 |
| `PLAYER V9.2 & MUSIC BY JEFF'93` | Pat_Kasser.sid | 1993 |
| `PLAYER V9.4 & ZAK BY JEFF/CML!` | Castle_Camelot.sid | 1993 |
| `PLAYER V9.6 (C) JEFF / CAMELOT` | Action_Hunter.sid | 1993 |
| `PLAYER V9.7 & ZAK BY JEFF/CML!` | Plasmatic_Puke.sid | 1993 |
| `PLAYER V9.9A BY S0REN LUND...` | Complex_Menu.sid | ~1993 |
| `PLAYER BY JEFF/CZP!!` | Reflex_Tune.sid | 1993–2003 |
| `PLAYER BY JEFF/CREST` | Paradise.sid | ~1999+ |
| `PLAYER BY JEFF/CML!!` | Reflex_Tune_2.sid | ~2002 |
| (no string — X-SID era) | 6581_Doped_Cows.sid | 2007+ |

**Tool releases:**
- **CZP Music Editor V2.0** (1996, CSDb #122334) — the "canonical" release of his editor/player. Never properly released; circulated informally. Rastertime: max $1C rasterlines vs JCH v20's $26 (Jeff wins). Includes 4 SIDs: Martin_Walker_Tribute, MSI, Raabik, Zarathus.
- **X-SID** (2007, CSDb #47985, Viruz) — redesigned editor, rated 9.4/10.

---

## 2. Binary Layout (V9.x Canonical — `$1000` base)

Analysed from `Action_Hunter.sid` (Player V9.6, init=$1000, play=$1003, load $1000–$1C8C, 3212 bytes, 1 subtune).

### 2.1 Header / Vectors

```
$1000–$1002  JMP <init_target>   ; e.g. JMP $11A4
$1003–$1005  JMP <play_target>   ; e.g. JMP $12F0
$1006–$100B  padding / flags     ; subtune count in $100B (byte 0x0B from load)
$100C–$101F  petscii credits or padding
$1020–$103F  Version string, null-terminated
             Example: '-PLAYER V9.6 (C) JEFF / CAMELOT-'
```

PSID `init` points to $1000 (JMP trampoline). PSID `play` points to $1003 (JMP trampoline). The real init and play routines are deeper in the binary.

### 2.2 Per-Voice State Table

Three voice state "slots" occupy a 7-byte-stride region within the code page:

```
Slot 0 (X=0x00):  $1040 – $1046   (and beyond to ~$1060)
Slot 1 (X=0x07):  $1047 – $104D   (+$07 from slot 0)
Slot 2 (X=0x0E):  $104E – $1054   (+$0E from slot 0)
```

All indexed accesses use `STA/LDA addr,X` where X ∈ {$00, $07, $0E} selects the voice. The base addresses (e.g. `$1040`, `$106A`, etc.) are absolute but the 7-byte stride is the invariant. This is the sidid main signature:

```
A5 ?? 48 A5 ?? 48    ; PHA $FB / PHA $FC (save ZP song-data ptr)
AND A2 ?? 20          ; LDX #$00 / JSR dispatch_voice
AND A2 07 20          ; LDX #$07 / JSR dispatch_voice
AND A2 ?? 20 ?? ??   ; LDX #$0E / JSR dispatch_voice
68 85 ?? 68 85 ?? 60 ; PLA / STA $FC / PLA / STA $FB / RTS
```

State bytes (per voice, at `base+X`):

| Offset from base | Role |
|---|---|
| `$1041,X` | Note-length down-counter |
| `$1044,X` | Voice mode / phase |
| `$106A,X` | Orderlist ptr lo |
| `$106B,X` | Orderlist length counter |
| `$106C,X` | Gate flag |
| `$106D,X` | Voice active / tick flag |
| `$106E,X` | Pattern position (Y-index) |
| `$106F,X` | Current waveform value |
| `$1070,X` | Vibrato depth / arp counter |
| `$1081,X` | Pattern ptr lo |
| `$1082,X` | Pattern ptr hi |

ZP $FB/$FC = current pattern read pointer (16-bit); saved to stack on play entry, restored on exit.

### 2.3 Tables

```
$10C4–$1123  Frequency lo-byte table  (96 entries = 8 octaves × 12 semitones)
$1124–$1183  Frequency hi-byte table  (96 entries)
$1184–$11A3  Arp/vibrato semitone-offset table (multiples of 3: 0,3,6,9...90)
```

Freq table indexing: note byte from pattern → `(note & $1F) × 8` → base index into freq table. Each octave spans 12 entries; 8 octaves × 12 = 96. The table starts near C-0 at ~$0108 (lo=$08, hi=$01).

### 2.4 Code Regions

```
$11A4–$12EF  INIT routine
             - Y = subtune number (passed in A, TAY)
             - Per-subtune data indexed from address table at $17C8
             - Copies orderlist ptrs (voice 1/2/3) into per-voice slots
             - Sets $D417 (filter mode) once
             - Calls per-voice setup sub (LDX#0/JSR, LDX#7/JSR, LDX#E/JSR)
             - Primes ADSR and initial waveform per voice

$12F0–$134C  PLAY main entry
             - On first call: clear $D400–$D418 all zeros, set active flags, RTS
             - Writes $D418 (master vol | filter LPF bit) every frame
             - 3-voice dispatch: LDX#0/JSR $1408, LDX#7/JSR $1408, LDX#0E/JSR $1408
             - ZP $FB/$FC saved (PHA) before dispatch, restored (PLA) after

$134D–$13E7  PLAY second path (used for different state / song-done detection)
             - 3-voice dispatch to JSR $13E8 (alternate effect chain)

$13E8–$1407  Alternate effect chain (secondary voice routine)

$1408–$154F  Main per-voice dispatch:
             - DEC $1041,X (note length counter)
             - If non-zero: go to effect chain (glide/vibrato/PW continue)
             - If zero: read new byte from ($FB),Y
               Pattern byte decode:
                 $00:       rest (silent)
                 $01–$7B:   note (semitone)
                 $7C:       (unclear, treated as note-like)
                 $7D:       rest (silence gate)
                 $7E:       note range boundary
                 $7F:       tie/hold (sustain; no gate toggle)
                 $80:       rest / silent (alternate rest)
                 $FE:       pattern loop (wrap to start)
                 $FC:       loop-target marker
                 $FF:       pattern end / orderlist advance

$1550–$17B7  Effect emitters:
             - Filter update ($D415, $D416)
             - Glide / portamento (additive freq: CLC / ADC abs,X pattern)
             - Vibrato (oscillating freq delta from vibrato table)
             - Pulse-width sweep ($D402/$D403 update)
             - Freq write-out ($D400/$D401)
             - Instrument program executor ($D404 waveform/gate)
             - ADSR write-out ($D405/$D406)
```

### 2.5 Data Regions

```
$17C8–$17FF  Address table (16-bit little-endian pointers, 30 entries in V9.6)
             Indexed by subtune: LDA $17C8,Y / LDA $17C9,Y (lo/hi)
             Layout: [V1_orderlist_ptr, V2_orderlist_ptr, V3_orderlist_ptr,
                      inst0_ptr, inst1_ptr, ..., pat0_ptr, pat1_ptr, ...]

$1800–$18A3  Instrument ADSR init table (per-instrument AD/SR priming values)

$18A4–$196E  Instrument programs (waveform sequences)
             Format: ((duration:u8, wave_byte:u8)* FE FF?)
               wave_byte values:
                 $41 = pulse + gate (triangle bit 6 | gate)
                 $21 = sawtooth + gate
                 $81 = noise + gate
                 $11 = triangle + gate
                 $01 = gate-only (no waveform change)
                 $40 = pulse (gate OFF)
               FE = loop-back (instrument loops)
               FF = end

$196F–$19CF  Effect/arp programs (pulse modulation, filter sweep, arp sequences)

$19D0–$1C8B  Pattern data (note sequences)
             Format: (duration:u8, note:u8)* FF
               duration: 1–255 frames per note step
               note:    $01–$7B = semitone (1-indexed)
                        $7F = tie/hold
                        $7D = rest
               FF = end of pattern (advance orderlist)
```

### 2.6 Multi-Subtune Structure

For multi-subtune SIDs, each subtune is indexed at init time:

```
$1025[subtune] = song-set index (0-based)
$1706[index*2] = lo byte of pointer to voice-1 orderlist for this song-set
$1706[index*2+1] = hi byte
$1029[subtune] = additional per-subtune parameter (transpose/speed)
```

The address table at $17C8 grows per-SID; the first 3 entries are always the 3 voice orderlists for subtune 0, then instruments, then patterns.

Orderlists are duration-only streams (1 byte per step). Each orderlist entry says how many frames the next pattern step lasts. When the duration counter expires, advance to next pattern byte.

---

## 3. Per-Frame Write Model

### 3.1 Frame Write Order

Every PLAY() call (once per VBI, ~50 Hz PAL):

```
1. STA $D418  ← master vol | filter-LPF-bit, EVERY frame (unconditional)

[Voice 1, X=$00]
2. STA $D415  ← filter resonance + voice routing  (conditional: filter effect active)
3. STA $D416  ← filter cutoff lo                  (conditional: filter effect active)
4. STA $D402,X ← pulse width lo                   (conditional: PW changed)
5. STA $D403,X ← pulse width hi                   (conditional: PW changed)
6. STA $D404,X ← control reg (gate=0, old wave)   (conditional: new note only — hard-restart gate-off)
7. STA $D405,X ← ADSR attack/decay                (conditional: new note only)
8. STA $D406,X ← ADSR sustain/release             (conditional: new note only)
9. STA $D400,X ← freq lo                          (conditional: freq changed)
10. STA $D401,X ← freq hi                         (conditional: freq changed)
11. STA $D404,X ← control reg (gate=1, new wave)  (conditional: new note only — gate-on)

[Voice 2, X=$07]  — same as voice 1
[Voice 3, X=$0E] — same as voice 1
```

### 3.2 Key Write-Model Observations

- **$D418 written unconditionally** on every frame. The master-vol field carries the LPF bit (bit 4) permanently OR'd in. The 4-bit volume field is the tune's global volume.
- **$D417 (filter mode) is init-only.** Written once during subtune init. Not in the play loop.
- **Hard-restart gate model:** On each new note, $D404 is written TWICE: first with gate=0 (resetting the ADSR envelope), then with gate=1 and the new waveform. This is the standard C64 hard-restart pattern.
- **Tie ($7F):** No gate toggle, no ADSR write. Only freq and PW continue to be updated by active effects.
- **Rest ($7D):** $D404 gate=0 written. No freq write. ADSR not rewritten (voice just releases).
- **Freq writes are conditional:** Freq is written when: (a) new note with non-zero freq, OR (b) glide/portamento effect is running, OR (c) vibrato effect is running. Silent when held at same pitch.
- **Filter regs ($D415/$D416) written only on filter-effect steps.** Filter cutoff ($D416) is the primary swept value; resonance ($D415) is updated together.
- **Voices processed strictly in order:** V1 (X=0) fully processed, then V2 (X=7), then V3 (X=$0E). Within-voice, effects accumulate left-to-right through the emitter chain.
- **PSID `speed` field:** The canonical Jeff player is VBI-driven (speed=0). CIA timing not used in the main player; X-SID (2007) uses CIA for multi-song scheduling.

### 3.3 Additive Freq-Table Lookups

The sidid main signature second line captures the additive freq pattern:

```
9D ?? ?? BD ?? ?? 18 7D ?? ?? 7D ?? ?? A8 B9
```

This decodes as:
- `9D xx xx` = STA abs,X (store computed freq component)
- `BD xx xx` = LDA abs,X (load voice-freq accumulator)
- `18` = CLC
- `7D xx xx` = ADC abs,X (add vibrato/glide delta)
- `7D xx xx` = ADC abs,X (add second component, e.g. global transpose)
- `A8` = TAY (result → Y for freq-table index)
- `B9 xx xx` = LDA abs,Y (look up in freq table)

The additive combination of per-voice base note + vibrato delta + arp offset → Y → freq table → $D400/$D401 write. The `& $1F × 8` noted in dispatch constrains the arp/vibrato counter to a 32-slot cycle.

---

## 4. Group-Specific Variants

All variants are by Søren Lund. The sidid sub-sigs distinguish init or structural micro-differences in otherwise-compatible engines.

### 4.1 Jeff (main, V4–V9.9, X-SID)

The canonical player family. Four sidid signatures:

```
Sig 1: A5 ?? 48 A5 ?? 48 AND A2 ?? 20 AND A2 07 20 AND A2 ?? 20 ?? ?? 68 85 ?? 68 85 ?? 60
        → ZP push / 3-voice JSR dispatch with X=$00/$07/$0E / ZP pop
        → Core structural identity: present in ALL V7+ engines
Sig 2: 9D ?? ?? BD ?? ?? 18 7D ?? ?? 7D ?? ?? A8 B9
        → Additive freq lookup (vibrato/glide/arp accumulate into freq)
Sig 3: BD ?? ?? 9D 00 D4 BD ?? ?? 18 7D ?? ?? 9D 01 D4
        → Final freq write-out: load computed freq / STA $D400 / additive / STA $D401
(X-SID) 88 10 F7 A5 ?? 48 A5 ?? 48 A2
        → X-SID variant (2007): DEY / BPL (3-voice init loop) then ZP push; each voice
          gets TWO JSRs per dispatch (dispatch + write-out separate)
```

**V4** (Jeff/Airwalk): Predates the sidid main sig. Uses ZP $F9/$FA/$FB (three pointers). Voice dispatch uses 3 hardcoded absolute JSR targets (no X-register indexing). Instrument executor identified by `C9 FF B0 0E 8D 04 D4 C8`.

**V7**: Introduces X=$00/$07/$0E dispatch, but voice 0 has a different JSR target from voices 1–2. Per-voice pattern ptrs injected as literal addresses between JSRs (not from a table). ZP = $FB/$FC.

**V9.x**: All three voices use the same JSR target. Pattern ptrs from an address table (enables multi-subtune without code changes). ZP = $FB/$FC. This is the dominant variant (≥130 SIDs).

**X-SID** (2007): Restructured play loop — a 3-iteration loop (LDY#2/LDX table,Y/JSR init; DEY/BPL) initializes voices. Each voice gets two JSRs in play. Writes ALL SID regs ($D418/$D417/$D416/$D401,X/$D400,X/$D406,X/$D405,X/$D404,X/$D402,X/$D403,X) unconditionally every frame (no conditional writes). CIA timer scheduling for multi-song. Only 1 SID in HVSC matches (`6581_Doped_Cows.sid`, load $1000–$2D7A, 7546 bytes including CIA stub at $2D55/$2D68).

### 4.2 Jeff/Airwalk (sidid: `C9 FF B0 0E 8D 04 D4 C8`)

**3 SIDs:** Cool_Fool.sid, Music_001.sid, Old_Tune.sid. All `init=$1000 play=$1003`.

This sub-sig fires inside the **instrument-program executor** of the V4 player. The byte sequence is:

```
C9 FF = CMP #$FF  ; is this the end marker?
B0 0E = BCS +$0E  ; if >=FF branch past write
8D 04 D4 = STA $D404  ; else write waveform to voice-control reg
C8 = INY          ; advance instrument position
```

The V4 player differs structurally from V7+: it uses ZP $F9/$FA/$FB (3 ZP pointers), and the per-voice routines are at fixed absolute addresses (no X-register dispatch). Play JMP in Cool_Fool.sid goes to $1B60 (well within $1000–$1DEA).

"Airwalk" in the sidid name most likely refers to a very small C64 group Jeff produced music for circa 1992 (earliest active period); Airwalk Cracking Crew (CSDb #8420, Germany) and Airwalk Codeworks (CSDb #11777) both predate or are unrelated. No CSDb release specifically tagged "Jeff/Airwalk" was found — the name appears only in sidid.

### 4.3 Jeff/BullSID (sidid: `10 D7 A9 00 85 FC A9 00 85 FB 60 A9`)

**2 SIDs:** Evolver_6581.sid (18.2 KB, compilation), Rectumor_8580.sid. All `init=$1000 play=$1003`.

Sub-sig fires at the **song-done / ZP-clear exit path**:

```
10 D7 = BPL -$29    ; (conditional branch, target of the song-length countdown)
A9 00 85 FC = LDA #0 / STA $FC   ; zero ZP pointer hi (song done)
A9 00 85 FB = LDA #0 / STA $FB   ; zero ZP pointer lo
60 = RTS
A9 = next byte (LDA #... begins new path)
```

Core structural difference from V9.x: **ZP $FB/$FC is saved to RAM** (via `STA abs`) rather than to stack (PHA/PLA). This means the 3-voice dispatch in Evolver uses `LDA $FB / STA $1373` save pattern rather than `PHA`. Otherwise the 3-voice JSR dispatch is identical (X=$00/$07/$0E, same JSR target $161E in Evolver). BullSID likely a small group name for a collaboration.

Evolver_6581.sid is a large compilation (18.2 KB loaded, probably 16+ songs) using an internal song-selector with this ZP-clear-on-done pattern.

### 4.4 Jeff/FLT (sidid: `60 A9 00 8D 02 D4 A9 08 8D 03 D4 4C`)

**2 SIDs:** Deep_Shit.sid, Martin_Walker_Tribute.sid. All `init=$1000 play=$1003`.

Per sidid.nfo: "Custom player made for One Million Lightyears from Earth/FairLight" (CSDb release #17292, Floppy 2005 demo, Jeff did the music). The sub-sig fires in the **init tail**:

```
60 = RTS            ; end of one init sub
A9 00 8D 02 D4 = LDA #$00 / STA $D402   ; V1 PW lo = 0
A9 08 8D 03 D4 = LDA #$08 / STA $D403   ; V1 PW hi = 8 → PW = $0800 = 50% pulse
4C F4 11 = JMP $11F4  ; continue init
```

This is a **pulse-width priming step** in the init routine that sets PW to $0800 (50% duty cycle) for voice 1 at startup, before the main 3-voice dispatch init. The core play engine is otherwise the same as V9.x (same 3-voice JSR dispatch, $D418-first write order, ZP PHA/PLA save).

The FLT init also writes $D409 / $D40A / $D40C (voice 2 ADSR) directly at init from the subsig scan of Martin_Walker_Tribute, which confirms it's an init-tweak variant, not a fundamentally different engine.

Play entry at $1003: `A9 0F 09 00 8D 18 D4` = `LDA #$0F / ORA #$00 / STA $D418` (master vol $0F on every play call). Structurally identical to V9.x play loop.

### 4.5 Jeff/XLarge (sidid: `60 A9 D7 8D 06 D4 A9 ?? 8D 0D D4 A9 ?? 8D 14 D4 A9 00 8D 05 D4 8D 0C D4`)

**3 SIDs (confirmed), 2 unclassified (X-Large_5/6):** X-Large.sid (765 bytes), X-Large_2.sid (1008 bytes), X-Large_4.sid. All `init=$1000 play=$1003`.

This is a **completely different engine** from all other Jeff variants. X-Large.sid is 765 bytes total — far too small for a general tracker engine. It is a **direct table-driven SID player** for a specific piece, not a general-purpose tracker.

The sub-sig is the **init routine itself**:

```
60 = RTS (end of previous stub)
A9 D7 / 8D 06 D4 = LDA #$D7 / STA $D406   ; V1 sustain/release
A9 ?? / 8D 0D D4 = LDA #?? / STA $D40D    ; V2 sustain/release
A9 ?? / 8D 14 D4 = LDA #?? / STA $D414    ; V3 sustain/release
A9 00 / 8D 05 D4 / 8D 0C D4 = LDA #0 / STA $D405 / STA $D40C  ; V1,V2 AD = 0
```

This directly primes all three voices' ADSR-SR and AD registers in the init. The play loop at $103E is a minimal: reads pre-computed freq table entries indexed by a note counter, writes $D400/$D401/$D407/$D408/$D40E/$D40F (freq for 3 voices), and updates a simple arp/wave cycling table. No pattern format, no orderlist, no instrument programs. Just a hardcoded looping melody with 3-voice freq cycling.

### 4.6 Jeff/BullSID3 (sidid: `A0 16 A9 00 99 00 D4 88 10 FA 8D ?? ?? A0 ?? 99`)

**2 SIDs:** Touching_Cloth.sid (`init=$1000 play=$1003`), Drax_8580_Years_Old.sid (`init=$8000 play=$8003`).

Credits string in binary: `JEFF/VRZ 2009-` (Viruz, 2009 era).

Sub-sig is the **complete SID-clear init loop**:

```
A0 16 = LDY #$16       ; Y = $16 = 22 (SID has regs $D400–$D416 = 23 regs)
A9 00 = LDA #$00       ; A = 0
99 00 D4 = STA $D400,Y ; clear $D400+Y
88 = DEY               ; Y--
10 FA = BPL $-4        ; loop until Y < 0 (clears $D400–$D416)
8D ?? ?? = STA abs     ; store zero somewhere else
A0 ?? = LDY #??        ; start further init
99 = STA abs,Y         ; more writes
```

This is the "BullSID3" init that explicitly clears ALL 23 SID registers ($D400–$D416) before setup — a more thorough chip reset than standard Jeff V9 (which relies on first-call RTS-on-zero-A to clear regs). The core 3-voice JSR dispatch and play loop are V9.x-compatible (confirmed in Touching_Cloth.sid: play at $1310 with `A9 0F 09 10 8D 18 D4 A2 00 20 23 13 A2 07 20 23 13 A2 0E ...`).

"BullSID" and "BullSID3" likely denote Jeff's collaboration with a group named BullSID (no separate CSDb group found for this name; Jeff/VRZ credits suggest these are Viruz-era commissions for BullSID group members).

---

## 5. Variant Relationship Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    Søren Lund "Jeff" player lineage             │
├────────────────┬──────────┬────────────┬────────────────────────┤
│  Name          │  ~Year   │  Variant?  │  Key structural diff   │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff/Airwalk   │  ~1992   │  V4 engine │  ZP=$F9/$FA/$FB; 3 fixed│
│ (sidid sub-sig)│          │  (diff)    │  absolute JSR targets  │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff V7        │  1992    │  core V7   │  X-dispatch; but voice0│
│                │          │            │  different JSR target  │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff V8        │  1992    │  core V8   │  between V7 and V9     │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff V9.x      │ 1993+    │  canonical │  Unified JSR target;   │
│ (main sidid)   │          │  majority  │  address table; PHA ZP │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff/BullSID   │ V9 era   │  init var  │  ZP→RAM save not PHA   │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff/FLT       │ ~2005    │  init var  │  PW priming in init    │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff/BullSID3  │ ~2009    │  init var  │  Full SID clear (Y#16) │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff/XLarge    │ varied   │  UNRELATED │  Completely different: │
│                │          │  engine    │  direct table player   │
├────────────────┼──────────┼────────────┼────────────────────────┤
│ Jeff X-SID     │  2007    │  redesign  │  Y-loop init; 2-JSR/v; │
│ (sidid sub)    │          │            │  all-regs each frame   │
└────────────────┴──────────┴────────────┴────────────────────────┘
```

**Conclusion:** Airwalk/BullSID/FLT/BullSID3 are ALL the same core engine with different **init priming** (init sub-sig = group commission customisation). None has a fundamentally different play-model from V9.x. XLarge is an outlier (different engine). X-SID is a genuine 2007 redesign.

The sidid sub-sigs for Airwalk/BullSID/FLT/BullSID3 fire in **init-only or exit-path code**, confirming they are init-routine variants, not play-engine variants.

---

## 6. Engine Distribution in HVSC

From `hvsc84.db` (READ-ONLY query, 181 Jeff SIDs total):

| sidid classification | Count | Notes |
|---|---|---|
| Jeff | 166 | Main engine (V4 through V9.x) |
| Jeff/Airwalk | 3 | Cool_Fool, Music_001, Old_Tune (V4 era) |
| Jeff/FLT | 2 | Deep_Shit, Martin_Walker_Tribute (~2005) |
| Jeff/BullSID3 | 2 | Touching_Cloth, Drax_8580_Years_Old (2009) |
| Jeff/BullSID | 2 | Evolver_6581, Rectumor_8580 |
| Jeff/XLarge | 3 | X-Large, X-Large_2, X-Large_4 |
| Power_Music | 1 | Feeling_Alone (different engine entirely) |
| None (unclassified) | 2 | X-Large_5, X-Large_6 |

Init/play address distribution:
- `init=$1000 play=$1003`: 143 SIDs (canonical base)
- `init=$0FD0 play=$0FE3`: 10 SIDs (alternate base, same engine)
- `init=$0FD0 play=$0FE2`: 7 SIDs
- `init=$0B00 play=$0B03`: 3 SIDs
- `init=$E000 play=$E003`: 3 SIDs
- `init=$8000 play=$8003`: 2 SIDs (Drax/BullSID3)
- Miscellaneous other bases: ~13 SIDs

The player loads at many addresses ($0FD0, $0B00, $8000, $8D0, $E000 etc.) — Jeff clearly recompiled for each base address. The $17C8 address table, ZP $FB/$FC, and all hardcoded addresses shift with each relocation.

---

## 7. Tool Handling

- **libsidplayfp / VICE:** Plays all Jeff variants correctly. The engine is straightforward VBI-driven (50 Hz PAL); no non-standard PSID requirements.
- **DeepSID (Chordian):** Online player; identifies engine via sidid.cfg. No Jeff-specific rendering special-cases found in DeepSID source.
- **SIDId (cadaver/sidid):** Six entries: `Jeff`, `Jeff/Airwalk`, `Jeff/BullSID`, `Jeff/FLT`, `Jeff/XLarge`, `Jeff/BullSID3`. Sourced from Wilfred/HVSC and collaborators per sidid.nfo.
- **player-id (WilfredC64):** Uses same signatures.
- **Rastertime:** Jeff's player claimed max $1C rasterlines (vs JCH v20 $26) per the 2002 Remix64 interview. This is fast enough for reliable 50 Hz VBI operation.

---

## 8. Gaps and Unknowns

1. **V4 full structure** not fully traced: the Cool_Fool V4 instrument executor and orderlist format may differ from V9.x in ways not yet documented. The three ZP pointers ($F9/$FA/$FB) vs two ($FB/$FC) in V9 suggest a different inner loop.

2. **V8 intermediate version** (Dejskraber_v2.sid, Soft-Ice_2.sid): not inspected. May bridge V7→V9 structurally.

3. **Pattern byte $7C / $FD**: their exact semantics in the dispatch were not confirmed (limited to `CMP #$7C / 30 E5` seen in code; $FD compared but branch target not traced).

4. **Orderlist format details**: orderlists look like duration-only streams, but the relationship between the duration bytes and the pattern data is not fully confirmed. Does the orderlist control WHICH pattern is played next, or just HOW LONG each pattern step lasts?

5. **Filter cutoff hi ($D417 in-play)**: only one write found (in init). Need to confirm whether any tune uses runtime $D417 updates.

6. **BullSID group identity**: no CSDb group found. May be an informal name for a small collaboration circle.

7. **X-Large_5 / X-Large_6**: unclassified in hvsc84.db. Not inspected; may be XLarge variant or something else.

8. **Unclassified SIDs at non-$1000 bases**: 38 SIDs load at non-$1000 addresses. All are likely the same engine, just recompiled. The sidid main sig is address-invariant (bytes-only match) so these should still fire — but worth confirming a few samples.

9. **X-SID full format**: only one HVSC SID (6581_Doped_Cows.sid) matched the X-SID sub-sig. X-SID's data format (instrument programs, pattern encoding) likely differs from V9.x and is not documented here.

10. **CZP Music Editor V2.0 disk image**: the CSDb release #122334 is a .d64 disk image containing the actual editor + 4 SIDs. Inspecting the editor binary would reveal the canonical data format documentation and any comments Jeff left in the code.

---

## Leads to Follow

- **Inspect the CZP Music Editor V2.0 .d64** (CSDb #122334, ~130 KB) — it contains the editor source or binary + 4 SIDs. The editor's save format is the canonical documentation.
- **Disassemble the init routine more fully** for a V4 SID (Cool_Fool.sid at $1189) to document the V4 orderlist/instrument format differences from V9.
- **Trace pattern byte decode for $7C, $FD, $FC** — exactly 3 unexplained branches in the dispatch.
- **Inspect V8** (Soft-Ice_2.sid) to find the V7→V9 transition point.
- **Check X-Large_5.sid / X-Large_6.sid** (currently unclassified) — are they XLarge variants or something else?
- **Search CSDb for "BullSID" group** — may have a profile under a different spelling or be attached to scener profiles.
- **Run sidid on non-$1000 base SIDs** (e.g. $0FD0, $8D0, $B00) to confirm the main sig fires for all relocations.
- **Find any source code or disassembly archives** from Jeff's X-SID release (CSDb #47985) — comments in the X-SID binary may document the updated format.
- **Inspect Martin_Walker_Tribute / Deep_Shit** more deeply to confirm the FLT init tweak's effect on the play model (does it change the PW handling in play, or only prime PW at init?).
