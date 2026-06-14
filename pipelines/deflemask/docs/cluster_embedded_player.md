# DefleMask C64 SID Embedded Player — Architecture & Song-Data Layout

## Provenance

| Field | Value |
|---|---|
| fetch_date | 2026-06-14 |
| author | Multiple (see per-section sources) |
| reliability | HIGH for player code (derived from HVSC binary analysis); MEDIUM for effect semantics (official docs + forum) |

### Sources consulted
- HVSC #84 binary analysis (direct): `MUSICIANS/G/Garvalf/Lully_Marche_Ceremonie_Turcs_Wip.sid`, `DEMOS/G-L/Lovely_Little_Egg.sid`, `DEMOS/A-F/Cind-i-rell-i.sid`, `DEMOS/G-L/Green_Tea.sid`
- sidid.cfg: https://github.com/cadaver/sidid/blob/master/sidid.cfg (player signatures)
- deflestream64 source: https://github.com/chiptunecafe/deflestream64 (VGM streaming player, NOT the embedded player)
- DefleMask changelog: https://www.deflemask.com/changelog.txt
- DefleMask DMF spec: https://www.deflemask.com/DMF_SPECS.txt
- BotB effect list: https://battleofthebits.com/lyceum/View/DefleMask+Tracker+Effects+Commands
- DefleMask bug tracker: https://www.deflemask.com/bugs/view.php?id=353 (SID init/play address fix)
- VICE Hall of Shame: https://vice-emu.pokefinder.org/wiki/Hall_of_Shame (GPL context)

---

## 1. Player Variants (sidid classification)

Three variants are in HVSC #84 (310 total SIDs):

| sidid name | HVSC count | sidid signature | Notes |
|---|---|---|---|
| `DefleMask_v1` | 1 | `E6 02 D0 02 E6 03 60 86 03 84 02 A9 00 85 04 20` | Earliest variant; one SID in HVSC |
| `DefleMask_v2` | 69 | `99 00 D4 CA D0 F4 86 03 A2 02 B5` | Intermediate; write-queue model |
| `DefleMask_v12` | 240 | `B5 ?? 9D 00 D4 CA 10 F8 C6 ?? 30` | The dominant variant; ZP shadow blit |

**Dominant address layout (v12, 112/240 SIDs):** load=$1006, init=$1103, play=$1006.
**Second layout (v12, 60/240):** load=$1006, init=$1000, play=$1006 (or init=$1106 play=$1000).
**All DefleMask SIDs:** load_addr=0 in PSID header (load addr embedded in first 2 bytes of data).
**All DefleMask SIDs:** single subtune only (n_subtunes=1).
**Speed flag:** typically `$00000001` (bit 0 set = subtune 1 is CIA-timed).

---

## 2. DefleMask_v12 — The Dominant Variant

### 2.1 Memory Map

```
$1006-$1102  Fixed player code (253 bytes, invariant across all v12 SIDs)
$1103-$1108  Init stub (6 bytes: LDY #$09 / LDX #$11 / JMP $10B2 / NOP / ...)
$1109        Unused alignment byte (skipped by stream reader on first access)
$110A-$110B  CIA timer value: lo byte, hi byte (e.g. $EA49 -> ~52Hz; $E54F -> ~48Hz)
$110C-$110D  Song data pointer: lo byte ($29), hi byte ($2A)  [= 16-bit addr of song stream]
$110E-$1126  Register reorder table: 25 bytes, PER-TUNE (maps stream field index -> D4xx offset)
$1127+       Song data stream (bit-compressed frame commands)
```

Observed song data pointer range: typically $1200-$12FF for small tunes; larger tunes place data later.

### 2.2 Zero-Page Layout

```
ZP $02        Frame tick counter (decremented each play(), command dispatched when it reaches 0)
ZP $03        Note sustain delay counter (used by delay commands $A1-$FF)
ZP $04-$1C    SID shadow register array: ZP[$04+i] mirrors $D400+i for i=0..24
              (direct 1:1 mapping: $04=D400 V1 freq lo, ..., $1C=D418 vol+mode)
ZP $1D-$1E    Loop-back pointer (16-bit): set by stream $FD command; restored by $FE
ZP $1F-$25    Zero-page read-byte subroutine (7 bytes, SMC, installed by init):
              INC $26 / BNE / INC $27 / LDA <ptr_lo><ptr_hi> / (RTS via ZP $28)
              The LDA instruction's address IS ZP $26/$27, making it self-patching.
ZP $26-$27    Primary song data read pointer (16-bit, lo/hi)
ZP $28        $60 = RTS opcode (tail of ZP read-byte routine; installed by init)
ZP $29-$2A    Backup/alternate pointer (swapped with $26/$27 by JSR $10A1)
```

### 2.3 PLAY Routine ($1006) — Detailed Flow

#### Phase 1: Shadow Blit to SID (always runs, every frame)

```asm
$1006: LDX #$18          ; X = 24 (= $D418 offset)
$1008: LDA $04,X         ; load ZP shadow for this reg
$100A: STA $D400,X       ; blit to SID
$100D: DEX
$100E: BPL $1008         ; loop X = 24..0 (descending order)
```

**Write order:** D418 first, then D417, D416, ..., D401, D400 (25 writes per frame, always).
All 25 SID registers ($D400–$D418) are written every frame from the ZP shadow array.
This is what the sidid signature `B5 ?? 9D 00 D4 CA 10 F8 C6 ?? 30` matches.

#### Phase 2: Tick Management

```asm
$1010: DEC $02            ; decrement tick counter
$1012: BMI $1015          ; if underflowed (was 0), proceed to command dispatch
$1014: RTS                ; still counting down, done for this frame
$1015: STX $02            ; X is now $FF, store as new tick count (= "wait 1 frame")
```

Note: `STX $02` sets tick to $FF when X=$FF, but normally tick is set by stream commands.

#### Phase 3: Command Dispatch

```
Read stream byte B (via JSR $001F = ZP read-byte subroutine):
  B = 0:         Read next byte B2:
                   B2 = $FD: LOOP SAVE  — save $26/$27 into $1D/$1E (loop point)
                   B2 = $FE: LOOP RESTORE — restore $1D/$1E into $26/$27, restart dispatch
                   B2 = $FF: SONG END — gate off all 3 voices (D404=$00, D40B=$00, D412=$00),
                              reset song ptr to $105E (song-end sentinel region)
                   B2 other: unclear (not observed in sample corpus)
  B < $A0 (and != 0): store B in ZP $02 (tick count), RTS
  B >= $A0:      Two-byte voice-jump command:
                   STA $2A (hi byte from B); read next byte -> STA $29 (lo byte)
                   JMP to voice-data decode loop ($1076)
```

#### Phase 4: Voice Data Decode Loop

Entered after a two-byte voice-jump command sets $29/$2A (new stream segment pointer).

```asm
$1076: JSR $10A1          ; swap ($26/$27) with ($29/$2A) — switch to new segment
$1079: LDA #$F8
$107B: CLC
$107C: ADC #$07           ; A = $FF
$107E: PHA                ; push $FF
$107F: TAX                ; X = $FF (field counter starting from $FF, wrapping to 0)
$1080: JSR $001F          ; read stream byte -> A (bit-field byte)
$1083: LSR                ; bit 0 -> C
$1084: PHP                ; save flags
$1085: INX                ; X++ (field index)
$1086: LSR                ; bit 1 (previous bit 2) -> C
$1087: BCS $1093          ; if set: this field has data
$1089: BNE $1085          ; if more bits: continue
$108B: PLP
$108C: PLA                ; restore $FF (or decrement for next byte?)
$108D: BCS $107B           ; loop for next byte in bit-field
$108F: JSR $10A1          ; swap back
$1092: RTS

; When BCS $1093 fires (field has data):
$1093: PHA
$1094: LDY $110E,X        ; THIS ADDRESS IS SMC-PATCHED at init to LDY <reorder_base>,X
                           ; Y = SID register offset for this field index
$1097: JSR $001F          ; read value byte from stream
$109A: STA $0004,Y        ; write to ZP shadow[$04 + reg_offset] = ZP[4 + D4xx_offset]
$109D: PLA
$109E: JMP $1085           ; continue with remaining bits
```

**Field decoding:** Each bit in the bit-field byte (LSR chain) indicates whether field[X] has an updated value. If bit is set, read 1 byte from stream = new value for that SID register. The register is identified by `reorder_table[X]` (patched into the LDY instruction at $1094).

### 2.4 INIT Routine ($1103)

```asm
$1103: LDY #$09            ; ptr lo = $09
$1105: LDX #$11            ; ptr hi = $11  -> initial read ptr = $1109
$1107: JMP $10B2

$10B2: STY $26             ; ZP $26 = $09 (ptr lo)
$10B4: STX $27             ; ZP $27 = $11 (ptr hi) -> ptr = $1109

; Install ZP read-byte subroutine from template at $10C6:
$10B6: LDX #$06
$10B8: LDA $10C6,X         ; source: INC $26 / BNE / INC $27 / LDA $FFFF (7 bytes)
$10BB: STA $1F,X           ; dest: ZP $1F-$25
$10BD: DEX; BPL $10B8
$10C0: LDA #$60; STA $28   ; ZP $28 = RTS opcode

$10D0: JSR $001F           ; read stream[0] = CIA timer lo -> STA $DC04
$10D3: JSR $001F           ; read stream[1] = CIA timer hi -> STA $DC05
       ; CIA timer = {hi,lo} cycles/frame; PAL C64 = 985248 Hz
       ; Observed: $49EA=18922->52.1Hz, $4FE5=20453->48.2Hz
$10D6: JSR $001F           ; read stream[2] = song ptr lo -> STA $29
$10D9: JSR $001F           ; read stream[3] = song ptr hi -> STA $2A

; Advance ptr by 1 (inline, not via JSR $001F):
$10E6: INC $26; BNE; INC $27   ; ptr now points to $110E (reorder table base)
; SMC-patch LDY instruction at $1094 with current ptr ($110E):
$10EC: LDA $26; STA $1095    ; patch lo byte
$10F1: LDA $27; STA $1096    ; patch hi byte

; Clear ZP $02-$1E:
$10F6: LDX #$1C; LDA #$00
$10F8: STA $02,X; DEX; BPL

; Swap pointers: $26/$27 (reorder table ptr $110E) <-> $29/$2A (song data ptr)
; After swap: $26/$27 = song data ptr, $29/$2A = reorder table ptr
$10FF: JSR $10A1
$1102: RTS
```

### 2.5 Register Reorder Table

The 25-byte table at $110E is **per-tune** (different for each SID). It maps:
- `field_index` (0–24, counted by INX loop in the bit-field decoder) → D4xx register offset

Two observed examples:
```
Example 1 (Lully): 16 12 13 0B 0E 0F 04 0C 05 07 00 01 08 15 03 06 09 0A 0D 10 11 14 17 18 02
Example 2 (Egg):   12 13 0F 04 0E 05 01 00 0B 0C 07 08 14 0D 06 16 18 17 03 10 15 09 11 02 0A
```

In both examples all 25 SID register offsets ($00–$18) appear exactly once — the table is a permutation. The ordering varies by song (probably reflecting which registers change most frequently, for compression efficiency).

### 2.6 Song Data Stream Format

The song stream (starting at the address stored at $110C/$110D) is a sequence of commands:

```
Tick commands (single byte, 1–$9F):
  $01-$9F  Set frame tick count = this value; RTS (wait N frames before next dispatch)

Voice-jump commands (two bytes):
  $A0-$FF, <lo>   Jump to voice-data segment at <hi=$byte, lo=next_byte>
                  Switches stream pointer to this segment and reads bit-field data for
                  per-frame register updates (see §2.3 Phase 4)

Zero-prefix commands (two bytes, first byte = $00):
  $00, $FD   LOOP SAVE: snapshot current read pointer as loop start
  $00, $FE   LOOP RESTORE: jump back to loop start (repeat section)
  $00, $FF   SONG END: gate off all voices, reset to sentinel/silence region
```

**Per-voice data segments** (reached via voice-jump commands):
A sequence of bit-field bytes. Each byte encodes which of the 25 SID fields is updated:
- Bits extracted via LSR chain; each '1' bit = "read next byte = new value for this field"
- Field N maps to SID register `reorder_table[N]` (from $110E)
- New values written to ZP shadow `$04 + reorder_table[N]` (will be blitted to SID next frame)

---

## 3. DefleMask_v2 — Write-Queue Model

### 3.1 Memory Map

```
$1006-$100B   V1/V2/V3 ctrl reg offsets: $04, $0B, $12 (used as lookup table)
$100C-$???    ZP read-byte subroutine (same pattern as v12)
$1006-$110E   Fixed player code
$110F         Init entry: LDX #$11, LDY #$1B -> JMP $1013  (ptr = $111B)
$1117         Play entry: JSR $103F
$111B+        Per-tune data: CIA timer, song ptr, reorder table?, song stream
```

### 3.2 Zero-Page Layout (v2)

```
ZP $02        Frame tick counter
ZP $03        Write-queue depth (number of pending SID writes)
ZP $04-$06    V1/V2/V3 ctrl register shadows (3 bytes; ctrl reg indices $04/$0B/$12)
ZP $07-$09    V1/V2/V3 gate-state flags (bit7=pending gate change, bit0=new gate value)
ZP $0A-$0B    Loop-back pointer (saved/restored by $81/$82 commands)
ZP $13-$14    Primary song data read pointer (16-bit)
ZP $15        Status byte
```

### 3.3 PLAY Routine ($1117 → $103F) — Write-Queue Model

**Phase 1: Flush write queue**
```
LDX $03 (queue depth)
Loop: LDY $CFD3,X (register index from queue)
      LDA $CFE9,X (value from queue)
      STA $D400,Y
      DEX; BNE loop
ZP $03 = 0 after flush
```

Write queue is in high RAM: register indices at $CFD3, values at $CFE9. Up to ~30 entries.

**Phase 2: Per-voice gate/ctrl update (hard restart)**
```
For each voice X = 2, 1, 0:
  LDA $07,X (gate flag; bit7 = pending update, bit0 = target gate)
  BPL -> skip (no pending change)
  LSR -> carry = target gate value
  LDA $04,X (ctrl shadow)
  LDY $1006,X (ctrl reg offset: $04/$0B/$12 for V1/V2/V3)
  If carry=0 (gate off): AND #$FE; STA $D400,Y (write ctrl with gate=0)
  Then: ORA #$01; STA $D400,Y (write ctrl with gate=1)
  → Two STA writes per triggered note: hard-restart sequence
```

**Phase 3–5:** Tick management + stream command dispatch (similar structure to v12).

**Stream commands (v2):**
```
$00           End-of-frame separator; read next command
$01-$7F       Tick count
$81           Loop restore (goto saved ptr)
$82-$FF       Gate off all voices (song end/reset)
<other>       Voice/register update data (bit-compressed, using write queue)
```

**Key difference from v12:** v2 uses a write queue for all SID writes rather than the full ZP shadow blit. This means only changed registers are written per frame (potentially fewer SID writes), but the write order depends on queue insertion order rather than a fixed D400-D418 sweep.

---

## 4. DefleMask_v1 — Direct Stream Model

### 4.1 Memory Map

```
$0FF0-$1004   Read-byte subroutine with C64 banking toggle (ZP $01 manipulation)
$1006         Advance-ptr subroutine (INC ZP$02/$03)
$100F-$1025   Init/setup helpers
$102D         Play entry
$1061         Init entry: LDX #$10, LDY #$6D -> call JSR $1011 (ptr = $106D)
$106D+        Song data stream (direct (reg, val) pairs with $80 frame separator)
```

### 4.2 Zero-Page Layout (v1)

```
ZP $01        C64 memory banking control (toggled to $38 during reads, restored after)
ZP $02/$03    Song data read pointer (lo/hi) 
ZP $04        Status flag (cleared at init)
ZP $05/$06    Saved loop pointer (lo/hi)
```

### 4.3 Song Data Stream Format (v1)

The v1 stream is the simplest: direct `(register, value)` byte pairs.

```
$00-$7F, <val>:  Write val to $D400+reg  (direct SID register write)
$80:             End-of-frame marker (RTS — frame complete)
$81:             Loop save: snapshot current ptr to ZP $05/$06, restart
Other $82-$FF:   Frame tick/delay management (swap ptr pairs ZP $02/$03 and $05/$06)
```

Example stream excerpt (from Green_Tea.sid, $106D):
```
reg=$00 val=$00   (V1 freq lo = 0)
reg=$18 val=$0F   (vol = 15, filter off)
reg=$02 val=$FC   (V1 pw lo)
...
reg=$04 val=$40   (V1 ctrl = saw, gate off)
reg=$04 val=$41   (V1 ctrl = saw, gate ON — two consecutive D404 writes!)
$80               (end of frame)
```

The double D404 write (gate off then gate on in same stream segment) implements hard restart within a single frame.

### 4.4 Special: Banking Toggle

v1 uses a banking-aware read at $0FF0:
```asm
LDY $01          ; save current banking state
STY $0FFE        ; (save to RAM)
LDY #$38         ; enable all-RAM ($38 = all RAM, no ROMs)
STY $01
LDY #$00
LDA ($02),Y      ; read byte from song data pointer
LDY #$00
STY $01          ; restore ZP $01 to 0 (or $00)
RTS
```

This allows the song data to span regions that would normally hit ROM under the default banking. The init/play addresses $1061/$102D sit in the writable $1000-$1FFF region regardless.

---

## 5. C64 SID Effect Codes (DefleMask tracker-level)

These are the tracker effects the composer uses; they map to player behavior in the export stream. Source: Battle of the Bits Lyceum + BotB effect reference.

| Code | Description |
|---|---|
| `10xx` | Set waveform: 00=none, 01=tri, 02=saw, 03=saw+tri, 04=pulse, 05=pulse+tri, 06=pulse+saw, 07=all three, 08=noise |
| `11xx` | Set filter cutoff (xx = $00–$3F) |
| `12xx` | Set pulse width (xx = $00–$3F) |
| `13xx` | Set filter resonance (xx = $00–$0F) |
| `14xx` | Set filter mode: 00=off, 01=LP, 02=BP, 03=BP+LP, 04=HP, 05=HP+LP, 06=HP+BP, 07=HP+BP+LP |
| `15xx` | ADSR hard reset time (xx = number of frames to wait before gate-on; 00 = reset every note) |
| `1Axx` | Reset ADSR on new notes: 00=do reset, 01=do NOT reset (continue envelope) |
| `1Bxy` | Reset filter cutoff: x=per-note reset, y=instant apply |
| `1Cxy` | Reset pulse width: x=per-note reset, y=instant apply |
| `1Exy` | Set ADSR: x=0 attack, x=1 decay, x=2 sustain, x=3 release, x=4 ring mod, x=5 sync, x=6 CH2OFF |

Standard tracker effects (also apply to C64): `00xx` arpeggio, `01xx` portamento up, `02xx` portamento down, `03xx` portamento to note, `04xy` vibrato (x=speed, y=depth), `08xx` set panning (unused on SID), `0Bxx` position jump, `0Dxx` pattern break, `0Fxx` set speed/tempo.

---

## 6. Write Model Summary

| Variant | SID write mechanism | Writes per frame | Order |
|---|---|---|---|
| v1 | Direct `(reg, val)` pairs, `$80` = frame end | Variable (only changed regs) | Stream order (composer-determined) |
| v2 | Writes accumulate in queue ($CFD3/$CFE9), flushed by play() | Variable (only changed regs, queue size) | Queue fill order; plus explicit ctrl writes for gate transitions |
| v12 | Full ZP shadow blit every frame + bit-compressed stream to update shadow | Always 25 (D418..D400 descending) | Fixed: D418 first, D400 last |

**v12 gate/hard-restart model:** The ctrl register (D404/D40B/D412) is in the ZP shadow like all other registers. A note-on sequence writes D4x4 with gate=0 (in one frame's stream segment) then D4x4 with gate=1 (in the next or same segment). The blit always fires before command dispatch, so the gate is updated atomically.

**v12 write-log signature:** Every frame emits exactly 25 writes to D418, D417, ..., D401, D400. The ORDER is descending. This is visible in siddump writelog output: each play() invocation starts with a D418 write and ends with a D400 write, all 25 present (even if unchanged).

---

## 7. deflestream64 (Third-Party VGM Streaming Player)

This is a **different product** from the embedded SID player. It takes a `.vgm` file (DefleMask's VGM export, not `.sid`) and converts it to a C64 streaming binary.

- Source: https://github.com/chiptunecafe/deflestream64
- Author: rytone (chiptunecafe)
- Language: Rust (builder) + 6502 assembly (C64 runtime) + cc65
- Uses: Krill's Loader for disk streaming, Bitnax LZ compression

The C64-side IRQ handler reads a simple two-byte command stream:
```
($reg, $val)   : SID register write
($FF, $00)     : end of frame
($FF, $FF)     : end of song
```

This is derived from the VGM `0xB6` SID write command, not the DefleMask `.sid` embedded player format.

---

## 8. Known Issues / Bug History

- **SID export hardware crash (bug #216, #353):** Exported SIDs crashed on real C64 hardware. Root cause: zero-page usage conflicting with KERNAL/game code. The player uses `$DC04/$DC05` (CIA timer A) for playback rate. Fixed around 2025 to match sidplay2's init/play address convention.
- **Relocation failures:** `sidreloc` reported "Write out of bounds at $0001" and "$DC04-$DC05" — confirming CIA timer writes and ZP $01 banking writes in v1. v12 avoids the banking issue.
- **GPL violation (resolved 2020):** v0.12.0 used reSID from VICE statically without attribution. Resolved in v0.12.1 with a new SID emulator. HVSC SIDs were exported with v0.12.0's embedded player before the fix.

---

## 9. Leads to Follow

1. **Bit-field decode algorithm (v12) — exact semantics unclear.** The `LSR / PHP / INX / LSR / BCS` loop at $1080–$108E is partially understood. Confirm exactly how field indices map to the reorder table (off-by-one? X starts at $FF/$00?). Build a test decoder in Python to confirm against a known tune.

2. **Song data $A0-$FF voice-jump command — semantics.** The two-byte command `$Axx $yy` sets $29/$2A to a new ptr, jumps to voice data decode. Does each "voice jump" correspond to one SID voice, or to any arbitrary register group? Is there always exactly one voice-jump per frame, or multiple? Trace a simple 3-voice tune.

3. **Reorder table construction rule.** What determines the permutation? Likely: registers that change most often get lower field indices for compression efficiency. Verify by correlating field frequency with ordering.

4. **v12 tick/delay command $A1-$FF.** The code at $102E: `SEC; SBC #$9F; STA $03; DEC $03; JMP $1076` handles bytes $A0-$FF. But $A0 goes to the two-byte path. Bytes $A1-$FF set ZP $03 (the sustain delay counter) to (B - $9F - 1). Clarify interaction with ZP $02 (frame tick counter).

5. **CIA timer interpretation.** Two observed values: $49EA (52.1Hz) and $4FE5 (48.2Hz). Neither is the exact PAL 50Hz value. Does DefleMask compute the CIA value for the song's authored BPM rather than always targeting 50Hz?

6. **v2 player — full bit-field stream format.** Not fully decoded. The write queue at $CFD3/$CFE9 collects per-frame updates; the exact encoding from stream bytes to queue entries is only partially traced.

7. **DefleMask source code.** Not publicly available. Delek (Leonardo Demartino) has not open-sourced the tracker. The 6502 player code is the only authoritative artifact.

8. **NTSC vs PAL SIDs.** deflestream64 roadmap mentions "NTSC compatibility" as a TODO. HVSC contains both PAL and NTSC DefleMask SIDs. The CIA timer value would differ. Check whether HVSC v12 SIDs cluster into PAL/NTSC groups by CIA value.

9. **Effect-to-stream mapping.** How do tracker effects `10xx`-`1Exx` translate to ZP shadow updates in the v12 player? The shadow array is updated via the bit-field stream; the pre-computed shadow values are the final register state per frame. DefleMask's C host code computes all effects and serialises only the resulting register deltas into the stream.

10. **Largest v12 SID.** Several v12 SIDs load at unusual addresses ($B435, $3000, $0800). Check if the player code is relocated or if those are different sub-variants.
