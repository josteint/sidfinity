# GoatTracker V1.x — Forums, Wikis, and Primary-Source Technical Notes

## Provenance

All findings below come from PRIMARY SOURCES retrieved during the 2026-06-29 research session:

| Source | Location | Type |
|--------|----------|------|
| GoatTracker V1.25 readme | `pipelines/goattracker/docs/src/v1_readme_125.txt` | Primary (official doc, Cadaver) |
| GoatTracker V1.53 readme | `pipelines/goattracker/docs/src/v1_readme_153.txt` | Primary (official doc, Cadaver) |
| GoatTracker V1.25 player1.s | `pipelines/goattracker/docs/src/v1_player1_125.s` | Primary (DASM assembly source) |
| GoatTracker V1.53 player1.s | `pipelines/goattracker/docs/src/v1_player1_v153.s` | Primary (DASM assembly source) |
| GoatTracker V1.53 gmusic.s | `pipelines/goattracker/docs/src/v1_gmusic_v153.s` | Primary (gamemusic player source) |
| GoatTracker V2 readme | https://github.com/leafo/goattracker2/blob/master/readme.txt | Primary (V2 format spec + V1 diffs) |
| GoatTracker V2 morphos guide | https://github.com/leafo/goattracker2/blob/master/morphos/goattracker.guide | Primary (V2 reference) |
| CSDb GoatTracker V2.0 beta thread | https://csdb.dk/forums/?roomid=14&topicid=16345&showallposts=1 | Forum (V1→V2 migration discussion) |
| Cadaver music routine blog | https://cadaver.github.io/rants/music.html | Author's blog (player arch) |
| Lemon64 Sadotracker thread | https://www.lemon64.com/forum/viewtopic.php?t=1595 | Forum (Lasse/Cadaver quotes on wavetable design) |

FOCUS: V1.x only. V2 data appears only as CONTRAST. Statements labeled **[V2-CONTRAST]** describe V2 behaviour for comparison; they are NOT V1 descriptions.

---

## 1. File Format Identifier

**V1 song format identifier: `GTS!`** (4 bytes, at .SNG offset +0).
**V1 instrument format identifier: `GTI!`** (4 bytes, at .INS offset +0).

Source: both readmes, §6.1.1 and §6.2.

**[V2-CONTRAST]** V2 introduced: `GTS3` → `GTS4` (v2.4, pulse modulation 1-bit accuracy added) → `GTS5` (v2.59+, gateoff bitflag parameters added). The V2 chain `GTS3/4/5` is entirely separate from V1's `GTS!`. None of the GTS3/4/5 identifiers appear in any V1 binary.

---

## 2. Song (.SNG) File Format — V1.53

Header layout (101 bytes total):

```
Offset  Size   Description
+0      4      Identification string "GTS!"
+4      32     Song name, zero-padded
+36     32     Author name, zero-padded
+68     32     Copyright string, zero-padded
+100    1      Number of subtunes (0 = 1 subtune, since data always present)
```

### 2.1 Orderlist (§6.1.2)

Repeats for channels 1, 2, 3 of subtune 1, then channels 1, 2, 3 of subtune 2, etc.

```
+0      1      Length of orderlist n - 1
+1      n      Orderlist data:
               Values 0-207: pattern numbers
               Values 208-223 ($D0-$DF): REPEAT commands (repeat 1-16 times)
               Values 224-254 ($E0-$FE): TRANSPOSE commands
               Value 255 ($FF): RST (restart) endmark, followed by restart-position byte
```

Note: the REPEAT and TRANSPOSE commands were **added in V1.3** (not present in V1.25).
In V1.25 the orderlist only contained pattern numbers 0-254 plus $FF=restart endmark.

### 2.2 Instruments (§6.1.3)

Repeats 31 times (instruments 1-31; instrument 0 is the empty instrument and is NOT stored).

```
Offset  Size   Description
+0      1      Attack/Decay
+1      1      Sustain/Release
+2      1      Initial pulse width (bit 0 = hard-restart indicator: 0=use HR, 1=no HR)
+3      1      Pulse speed
+4      1      Pulse limit low
+5      1      Pulse limit high
+6      1      Filter freq/type (V1.25) — or filter step number (V1.53, from V1.4)
+7      1      Size of wavetable in bytes n (always even)
+8      16     Instrument name, zero-padded
+24     n      Wavetable: waveform/note byte pairs (see §3 below)
```

**Maximum 31 instruments** in V1 (instrument 0 reserved = empty). **[V2-CONTRAST]** V2 expanded to 63.

Instrument 0 bytes (packed binary virtual address layout, player1_v153.s):
```
mt_instad       = $4000   ; Attack/Decay   (inst 1 at $4000, stride 8)
mt_instsr       = $4001   ; Sustain/Release
mt_instpulse    = $4002   ; Pulse init
mt_instpulsespd = $4003   ; Pulse speed (bit 0 = hardrestart inhibit)
mt_instpulselow = $4004   ; Pulse limit low
mt_instpulsehigh = $4005  ; Pulse limit high
mt_instfilter   = $4006   ; Filter reference
mt_instwave     = $4007   ; Wavetable start index (into mt_wavetbl/mt_notetbl)
```
Stride = 8 bytes per instrument in the packed binary. Pulse/speed/limit bytes have nybbles reversed vs. the editor display (confirmed by both readmes).

**[V2-CONTRAST]** V2 instrument is 9 bytes: adds "HR/Gate Timer" + "1stFrame Wave" fields. V1 hardrestart is a global parameter set at pack/relocate time (ADSR and length), not per-instrument. V1 also has no speedtable pointer in the instrument.

### 2.3 Patterns (§6.1.4-6.1.5)

```
+0      1      Number of patterns n
Then for each pattern:
  +0    1      Size of pattern in bytes m
  +1    m      Groups of 3 bytes per row:
               Byte 0: Note number
                 0-93 ($00-$5D): notes C-0 to A-7
                 94 ($5E):       KEYOFF (clear gatebit)
                 95 ($5F):       REST
                 96-191 ($60-$BF): notes without cmd+data bytes (compact encoding)
                 192-254 ($C0-$FE): long rest (packed rest)
                 255 ($FF):      ENDPATT
               Byte 1: Bits 7-3 = instrument number (0-31); bits 2-0 = command (0-7)
               Byte 2: Command databyte
```

Pattern row is **3 bytes** (vs 4 bytes in V2). Maximum 80 rows per pattern (V1 readme §3.3); max 208 patterns.

The note range is C-0 to A-7 (notes $00-$5D = 94 notes). **[V2-CONTRAST]** V2 uses $60-$BC = C-0 to G#7 (note encoding different), and patterns are 4 bytes.

### 2.4 Filter Table (§6.1.6)

Added in V1.4. Flat 256-byte block (64 × 4 bytes). Each filter step:
```
Byte 0: Resonance/channels (nonzero = set new filter; zero = cutoff modulation)
Byte 1: Filter type/volume  (if ctrl≠0: type bits + SID master vol nybble;
                              if ctrl=0: modulation duration in frames)
Byte 2: Filter freq/speed   (if ctrl≠0: new cutoff frequency; if ctrl=0: speed)
Byte 3: Next filter step    (loop pointer; step 00 = stop; filter 0 next-step disabled for funktempo hack)
```

**OPEN**: In V1.25, the filter byte in the instrument (offset +6) is described as "Filter Freq/Type" — a single byte encoding cutoff (high nibble) and filter type (bits 0-2). This is the simpler pre-step-programming model. V1.4 replaced this with step-programming. Confirm how the V1.25 player applies the filter byte (does it set $D416/$D417 directly?).

---

## 3. Wavetable / Arpeggio Table — THE BIG V1-SPECIFIC ITEM

This is the central V1 vs V2 difference.

### 3.1 Structure

In V1 the wave/arpeggio/note table is **a single unified table per instrument**, stored as byte pairs in the .SNG file:

```
Pair format (index 0, 2, 4, ...):
  Byte [2i]:   waveform byte (left)
  Byte [2i+1]: note byte (right)
```

The table ends when the waveform byte is $FF:
- `$FF / $00`: stop wavetable execution
- `$FF / n` (n > 0): loop to absolute index n (1-based)

**Source**: V1.25 readme §3.4; V1.53 readme §3.5.

### 3.2 Waveform Byte Semantics (left column)

```
$00         Do not change the waveform (useful during keyoff in wavetable)
$01-$08     Delay wavetable execution 1-8 frames (waveform unchanged)  [ADDED IN V1.5]
$09-$BF     Waveform register value (bit combinations):
              bit 0 ($01) = Gate bit
              bit 1 ($02) = Synchronize
              bit 2 ($04) = Ring modulation
              bit 3 ($08) = Test bit (silence + LFSR reset)
              bit 4 ($10) = Triangle
              bit 5 ($20) = Sawtooth
              bit 6 ($40) = Pulse
              bit 7 ($80) = Noise (cannot combine with other waveforms)
$FF         End/loop marker (see above)
```

Note: In V1.25 the delay feature ($01-$08) did NOT exist. V1.5 added delayed wavetable execution. Before V1.5, $01-$07 were just waveform values (gate bit only, test bit combos).

**[V2-CONTRAST]** V2 wavetable left side: $00 = waveform unchanged; $01-$0F = delay 1-15 frames; $10-$DF = waveform; $E0-$EF = inaudible waveforms ($00-$0F mapped here from v2.18+); $F0-$FE = execute pattern command inline; $FF = jump. V2 has no combined waveform+delay range; delays map to $01-$0F cleanly.

### 3.3 Note Byte Semantics (right column)

```
$00-$5F: Relative note — added to current channel note to get pitch
$80-$DF: Absolute note — direct frequency table index (C-0=$80 to B-7=$DF)
$60-$7F: Outside valid range → produces incorrect pitch (not used by Cadaver)
```

**Source**: both readmes.

**[V2-CONTRAST]** V2 right side: $00-$5F relative, $60-$7F negative relative, $80 = keep frequency unchanged, $81-$DF absolute notes C#0-B7.

### 3.4 In-Memory Split (Packed Binary)

In the **SNG file** waveform and note bytes are INTERLEAVED (pairs). In the **packed/relocated SID binary**, the packer SPLITS them into two separate regions:

```
V1.25 player1_125.s:
  mt_wavetbl = $5000  ; waveform bytes only
  mt_notetbl = $5100  ; note bytes only

V1.53 player1_v153.s:
  mt_wavetbl = $4100  ; waveform bytes only
  mt_notetbl = $4200  ; note bytes only
```

Both use the SAME index register Y to address both tables simultaneously:
```asm
mt_waveexec:  lda mt_wavetbl,y   ; fetch waveform byte
              ...
              lda mt_notetbl,y   ; fetch note byte at same index
```

This means the packed binary wavetable layout is NOT the paired-byte layout of the .SNG — the packer de-interleaves them. The virtual addresses above are symbolic stubs; the relocator patches in the actual runtime addresses.

---

## 4. Pattern Command Set — V1 (Commands 0-7)

V1 has **8 commands** (3 bits, packed with instrument number in one byte). V2 has 16 commands (4 bits, separate byte). The command is encoded in bits 2-0 of pattern row byte 1.

### V1.25 Command Set (8 commands)

| Cmd | V1.25 Name | V1.25 Semantics |
|-----|------------|-----------------|
| 0 | Arpeggio | 3-note arpeggio: root → root+X → root+Y; X≥8 = half-speed |
| 1 | Portamento | Raises (dir bit=0) or lowers (dir bit=1) pitch; speed = (XY & $7F)*2 per tick |
| 2 | Set Filter Cutoff Speed | Adds XY to cutoff each tick (XY≥$80 subtracts); stop with 200 cmd |
| 3 | Toneportamento | Slides to target note; dir in high bit; speed = (XY & $7F)*2; $00 = tie |
| 4 | Vibrato | Speed = X (direction-change interval); depth = Y*16+X per tick |
| 5 | Set Filter Parameters | X = resonance, Y = channel bitmask (bits 0-2 = ch1/2/3) |
| 6 | Set Sustain/Release | Sets $D406,x to XY |
| 7 | Set Tempo | Global if bit7=0 ($03-$7F); per-channel if bit7=1 ($83-$FF); $C0-$FF = timing marks (playroutines 3/4) |

Source: V1.25 readme §3.3.

### V1.53 Command Set (8 commands — different from V1.25!)

| Cmd | V1.53 Name | V1.53 Semantics |
|-----|------------|-----------------|
| 0 | Arpeggio | 3-note arpeggio: root → root+X → root+Y; X≥8 = half-speed (unchanged from V1.25) |
| 1 | Portamento Up | Raises pitch by XY*4 each tick |
| 2 | Portamento Down | Lowers pitch by XY*4 each tick **(NEW — was "set filter cutoff speed" in V1.25)** |
| 3 | Toneportamento | Direction now auto-determined; speed = XY*4; $00 = tie note **(changed in V1.3)** |
| 4 | Vibrato | X = direction-change speed; Y*16+X = pitch change per tick (unchanged formula) |
| 5 | Set Filter Parameters | Now a FILTER STEP NUMBER (00-3F) since V1.4 step-programming **(changed)** |
| 6 | Set Sustain/Release | Sets $D406,x to XY (unchanged) |
| 7 | Set Tempo | $03-$7F all channels; $80-$FE per-channel; $EF = timing mark; $F0-$FF = master volume fader **($EF/$Fxx added in V1.5)** |

**KEY DIFFERENCES from V2**: V2 has 16 commands where V1's 8 were split/renamed:
- V1 cmd 0 (Arpeggio) → REMOVED in V2 (replaced by wavetable arpeggio with wave steps)
- V1 cmds 1-4 → V2 cmds 1-4 (semantically similar but speed encoding changed; V2 uses speedtable index)
- V1 cmd 5 (Filter) → V2 cmd A (Filtertable pointer) + V2 cmd B (Filter control) + V2 cmd C (Cutoff)
- V1 cmd 6 (SR) → V2 cmd 6 (SR) unchanged
- V1 cmd 7 (Tempo) → V2 cmd F (Tempo) + V2 cmd E (Funktempo) + V2 cmd D (Master vol)
- V2 adds: cmd 7 (Set waveform register), cmd 8 (Wavetable pointer), cmd 9 (Pulsetable pointer)

Source: V1.25 readme §3.3, V1.53 readme §3.3.

### Tick Execution Model

Commands divide into tick-0 (on new note row) vs. tick-n (continuous) in **both V1.25 and V1.53**:

**V1.25** (from player code, `CMD_*` constants):
- Tick-0 commands (execute on row boundary): `CMD_SETCUTOFFADD` (2), `CMD_SETFILTER` (5), `CMD_SETSUSTAIN` (6), `CMD_SETTEMPO` (7)
- Tick-n commands (execute on ticks 1..N-1): `CMD_ARPEGGIO` (0), `CMD_PORTAMENTO` (1), `CMD_TONEPORTA` (3), `CMD_VIBRATO` (4)

**V1.53** (from readme §3.3):
- Tick-0 only: 5 (filter), 6 (sustain/release), 7 (tempo)
- Tick-n only: 1 (portamento up), 2 (portamento down), 3 (toneportamento), 4 (vibrato)
- Every tick: **0 (arpeggio)** — documented explicitly: "Command 0 (arpeggio) executes on every tick"

In V1.25 the readme says: "The 'continuous' commands 0, 1, 3 and 4, are executed only on ticks 1-N" — i.e., arpeggio was NOT executed on tick 0 in V1.25. V1.3 changelog says "No wavetable/arpeggio skip on tick 0 anymore." The V1.53 player code confirms arpeggio runs on both tick 0 (via `mt_tick0arp`) and tick-n (via `mt_ticknarp`).

**Source**: V1.25 readme §3.3; V1.53 readme §3.3; player1_125.s constants; player1_v153.s jump tables.

---

## 5. Arpeggio Command — Complete Semantics (V1)

The arpeggio command is **the defining V1 feature removed in V2**. It is a 3-note pattern arpeggio executed as a pattern effect command, not via wavetable.

### 5.1 Parameter Encoding

Pattern command 0, databyte = XY:
- X (bits 4-7 of databyte, after the player extracts them with `and #$70; lsr; lsr; lsr; lsr`): halftones above root for note 2
- Y (bits 0-3 of databyte): halftones above root for note 3
- Special: if X ≥ 8 (bit 3 of X is set), arpeggio runs at **half speed** and 8 is subtracted from X to get the actual interval

### 5.2 Execution (from player1_v153.s `mt_arpeggio` routine)

The arpeggio counter `mt_chnarpcount` cycles through 6 states (0-5). After LSR, this gives 3 states (0,0 → 1,1 → 2,2):
- States 0,1 (count 0,1): Play root note + X halftones
- States 2,3 (count 2,3): Play root note (no offset)  
- States 4,5 (count 4,5): Play root note + Y halftones

So the sequence is: **X, root, Y, X, root, Y...** at 2 ticks per step.

For half-speed (X ≥ 8): the `asl` at `mt_arpeggio` shifts the databyte left so bit 7 is the half-speed flag. **OPEN**: Trace exactly how half-speed is implemented in the counter logic — the `asl` before counter check needs careful reading.

The counter is shared with the **vibrato** direction counter. V1.53 warning (readme §2): "From version 1.3 onwards arpeggio & vibrato use the same internal register for calculations. Mixing arpeggio & vibrato in the same note may cause unexpected results."

### 5.3 Tick 0 vs. Tick N (V1.53)

From player1_v153.s:
```asm
mt_tick0arp:  beq mt_tick0idle     ; param=0 → idle
              lda mt_chnnewnote,x  ; if new note pending → idle (wavetable will run)
              bpl mt_tick0idle
              ldy mt_chnwaveptr,x  ; if wavetable active → skip arpeggio
              beq mt_arpeggio      ; no wave → run arpeggio
mt_tick0idle: jmp mt_tick0done

mt_ticknarp:  beq mt_arpzero       ; param=0 → zero freq (no arpeggio)
              jmp mt_arpeggio
```

So on tick 0: arpeggio only runs if there is no new note AND no active wavetable. On tick N: arpeggio runs on every non-zero arpeggio parameter.

**[V2-CONTRAST]** V2 removed the arpeggio command entirely. V2's wavetable right column uses relative notes (same as V1 relative notes) to achieve the same effect. V2's import converts V1 arpeggio commands to wavetable programs. Cadaver's V2 readme: "The only major feature removal is that of the arpeggio command in v2. Everything that this command does can also be done with wavetables, and the import feature converts all arpeggio commands to corresponding wavetable programs."

---

## 6. Instrument Pulse Modulation — V1

V1 uses a **bounds/limit based** pulse modulation model (not time-based like V2).

Parameters (all per-instrument, stored in instrument data):
- **Initial pulse width**: starting PW value ($00 = leave current PW unchanged; bit 0 = hardrestart inhibit)
- **Pulse speed**: added to PW each tick; the player stores PW as two nybbles reversed (V1.25: 4-bit speed $0-$F; V1.53: finer resolution)
- **Pulse limit low**: PW direction reverses when PW goes below this threshold
- **Pulse limit high**: PW direction reverses when PW exceeds this threshold
- If both limits = 0: PW always decreases (no reversal)

The direction flip uses the carry/borrow from the comparison, storing the direction flag in `mt_chnpulsedir`.

Player note: "Lowest bit of pulse width is the hard restart indicator (0 = use hard restart, 1 = don't use)." Source: V1.53 readme §6.1.3.

**[V2-CONTRAST]** V2 replaces per-instrument pulse parameters with a global **pulsetable** (step-programmed, time-based). V2 pulsetable: $01-$7F = modulation step (left = frame time, right = speed); $8X-$FX = set pulse width directly; $FF = jump. V2 added 1-bit precision to pulse speed in v2.4 ("pulse modulation speed has 1 bit added accuracy, so you need to double pulsespeeds"). V2 CSDb beta: "pulsetable seemed to have changed quite a bit" across V1 versions — Cadaver confirmed nybbles were swapped at one point.

---

## 7. Filter Model — V1.25 vs V1.53

### V1.25 Filter (pre-step-programming)

Per-instrument byte at offset +6: "Filter Freq/Type"
- High bits = cutoff frequency (8-bit)
- Low bits = filter type bitmask: bit 0=lowpass, bit 1=bandpass, bit 2=highpass

Applied on new note. Pattern command 2 = "Set filter cutoff speed" (adds signed XY to cutoff each tick). Pattern command 5 = set resonance and channel bitmask.

The player applies the filter byte directly to $D416 (cutoff) and $D417 (resonance/routing):
```asm
mt_filtcutoff:  lda #$00      ; SMC: actual cutoff value
mt_filtcutoffadd: adc #$00    ; SMC: speed (signed)
                sta mt_filtcutoff+1
                sta $d416
mt_filtctrl:    lda #$00      ; SMC: resonance+channels
                sta $d417
mt_filttype:    lda #$00      ; SMC: type+volume
mt_volume:      ora #$0f
                sta $d418
```
Source: player1_125.s.

### V1.53 Filter (step-programmed, from V1.4)

The filter table is a flat 256-byte block (64 × 4-byte steps). Each step:
```
Byte 0: resonance/channels (nonzero = set; zero = modulate)
Byte 1: type/volume (if nonzero ctrl) OR duration in frames (if ctrl=0)
Byte 2: cutoff (if nonzero ctrl) OR speed (if ctrl=0)
Byte 3: next step (loop pointer; step 0 = stop)
```

The instrument now stores a **filter step number** (0-63) rather than inline filter parameters. Step 0 has a special role: it stores the funktempo values in bytes 2 and 3, so its "next step" function is disabled.

Pattern command 5XY: sets filter step XY (range 00-3F).

Source: V1.53 readme §3.6.

---

## 8. Player Loop Structure

### V1.25 Player Loop (player1_125.s, "Musicroutine 11.1")

```
play():
  1. Filter cutoff update (slide: add mt_filtcutoffadd to mt_filtcutoff)
  2. Write $D416 (cutoff), $D417 (ctrl), $D418 (type+vol)
  3. For each channel (X=0, then channel offset +7, +14):
     a. Decrement tick counter
     b. If tick=0: read new pattern row (note, instrument, cmd, databyte)
        - Hard restart on new note: zero $D405, $D406
        - Set waveform $D404 = gate=0 (keyoff for prev note)
        - Run tick-0 command
     c. If tick>0: run effects (portamento/toneporta/vibrato)
     d. Wavetable step: update mt_chnwave, fetch note from mt_notetbl
     e. Pulse modulation: update PW, write $D402/$D403
     f. Write freq: $D400/$D401
     g. Write waveform: $D404 (wave AND gate-mask)
```

Note: `mt_wavetbl` and `mt_notetbl` are **separate arrays** at packed virtual addresses $5000 and $5100. The SNG format stores pairs; the packer splits them.

### V1.53 Player Loop (player1_v153.s)

```
play():
  1. ZP save (mt_temp1, mt_temp2 pushed to stack)
  2. Filter execution (same 4-step table as V1.25 but uses setfiltersub now)
  3. Write $D416, $D417, $D418 (with master-volume AND via mt_volume)
  4. Check mt_chnloop+1: if MSB set, do channel init (reset all sequencer state)
  5. For each channel (X = 0, 7, 14):
     a. Decrement tick counter
     b. If tick ≠ 0 and wavetable active: go to waveexec instead of effects
     c. If tick ≠ 0: run tick-n effect (portamento/toneporta/vibrato/arpeggio)
     d. Wavetable execution (mt_waveexec):
        - Fetch waveform byte from mt_wavetbl,y
        - Values 0-7: delay (skip, increment arpcount-as-delay)  [V1.5+]
        - Values 8+: write to mt_chnwave, fetch note from mt_notetbl,y
        - $FF: end or loop
     e. If tick = 0 (new row): read note+cmd from pattern data
        - Handle instrument change (update ADSR, PW, wave pointer)
        - Hard restart (testbit: write $09 to $D404)
     f. Gate-time check: write freq+wave+gate to SID
     g. Pulse modulation
     h. Write $D400-$D404 (freq lo/hi, wave AND gate)
  6. ZP restore
```

Source: player1_v153.s full reading.

**Key behavioural changes V1.25 → V1.53:**
- Hard restart changed completely in V1.5 (testbit method: write $09 to $D404 = test+gate; the testbit silences and resets the oscillator for a sharp attack)
- Delayed wavetable ($01-$08 = delay 1-8 frames) added in V1.5
- Filter now uses the step-programmed setfiltersub subroutine (from V1.4)
- ADSR load order: V1 always writes $D405 (AD) before $D406 (SR), then $D404 (wave). From Cadaver's blog: "the registers should be written to in this order: Waveform – Attack/Decay – Sustain/Release."

---

## 9. V1 Instrument Data in the Packed SID Binary (Packed Binary Layout)

From player1_125.s §5.6 ("Tweaking instrument data") the PACKED binary lays instruments as flat 8-byte structs starting at `startaddress + sizeof(player)`:

```
Instr. 1 AD              instrument_base + $0
Instr. 1 SR              instrument_base + $1
Instr. 1 Pulse           instrument_base + $2  (nybbles reversed)
Instr. 1 Pulsespeed      instrument_base + $3  (nybbles reversed)
Instr. 1 Pulselimit Low  instrument_base + $4  (nybbles reversed)
Instr. 1 Pulselimit High instrument_base + $5  (nybbles reversed)
Instr. 1 Filt. Freq/Type instrument_base + $6
Instr. 1 Wavetbl. Index  instrument_base + $7
Instr. 2 AD              instrument_base + $8   etc.
```

The wavetable index (`mt_instwave`) is a byte-offset into the separate mt_wavetbl/mt_notetbl regions (i.e., the waveform sequence number, not a byte-pair address).

---

## 10. Sound Effect Format — V1 (§6.3)

The SFX format is completely different from the instrument format. In the packed binary, sound effects are used via a separate SFX table:

```
+0      1      Attack/Decay
+1      1      Sustain/Release
+2      1      Pulse width (nybbles reversed: $80 PW → stored as $08)
+3      ?      Wavetable (note/waveform interleaved, different order than instrument!):
               Value 0: end sound effect
               Values 1-129: waveform values
               Values 130-223: absolute notes D-0 to B-7
               (V1.25 only) Values 254/255: repeat same note+wave 2/1 times
```

SFX wavetable: note comes BEFORE waveform (opposite of instrument wavetable). Absolute notes start at D-0 ($82 in V1.25). V1.53 removed the repeat values 254/255 from SFX.

---

## 11. V1.x Version Landmarks (from readme §8 / §9)

| Version | Key change relevant to format/player |
|---------|--------------------------------------|
| 0.9-0.93 | Beta; wavetable end was byte $00 (changed to $FF in 0.94) |
| 0.94 | Wavetable loops; pulse during wavetable; cmd 6 no longer overridden |
| 1.0 | First stable release |
| 1.3 | Hard restart toggle per-instrument; TRANSPOSE/REPEAT in orderlist; step-programmed filter foundation; no wavetable/arpeggio skip on tick 0 (arpeggio now executes on tick 0 too); separate portamento down; finer pulse speed |
| 1.4 | Filter is step-programmable (64 steps); filter command 5 changes meaning |
| 1.5 | Playroutine rewritten: testbit hard restart; delayed wavetable ($01-$08); proper keyoff (gateoff); master fader command 7F0-7FF |
| 1.52 | Frequency table tuning fix |
| 1.53 | Packer fixes for no-hardrestart / no-pulseinit instruments |

**[V2-CONTRAST]** V2.0 introduced: arpeggio command removed; 63 instruments; speedtable; uniform step-programming for wavetable (separate from pulse/filter). V2 → V2.4: GTS4 format (pulse speed 1-bit accuracy). V2 → V2.18: wavetable $00-$0F mapped to $E0-$EF; delay = $00-$0F only. V2 → V2.59+: GTS5 format (gateoff timer bitflags $80/$40).

---

## 12. Forum and Community Sources — Summary of Findings

**CSDb GoatTracker v2.0 beta thread** (https://csdb.dk/forums/?roomid=14&topicid=16345&showallposts=1):
- Confirmed format is binary-incompatible V1 → V2; BETACONV utility provided for intermediate V2 beta songs.
- Cadaver confirmed V1 had "swapped the pulsenybbles" at some point and "pattern commands also totally changed meaning" around V1.2-1.4 transition.
- Forum user Hein noted that the arpeggio removal in V2 "required pre-composing chord sequences into instrument wavetables, eliminating on-the-fly transitional chord creation."
- Cadaver restored vibrato depth to V1 behaviour for the initial V2 release ("halve all vibratodepths").

**Lemon64 Sadotracker thread** (https://www.lemon64.com/forum/viewtopic.php?t=1595):
- Cadaver (as Lasse): "the idea of arpeggio/waveformtable is to change the note pitch (the hex-numbers mean halftones, so a minor arpeggio would be $00 $03 $07) and the waveform each frame for all kinds of effects (drumsounds, chords etc.)"
- On register write order: "dumping all SID values from ghost registers at the end of the playroutine" and "loading the registers as close to each other as possible, and each voice in the order they appear in memory (waveform before ADSR, for example) gives the best soundquality."

**Cadaver's "Building a music routine" blog** (https://cadaver.github.io/rants/music.html):
- "The waveform/arpeggio-table usually contains byte pairs; the other byte is what to put in the waveform register and the other is the note number; either relative (arpeggios) or absolute (drumsounds)."
- Confirms V1 design: waveform 0 = no waveform change; special values for delay and loop.
- Player sequence: three voices, then filter, per frame.

**ChiptuneSAK source** (https://chiptunesak.readthedocs.io/en/latest/_modules/chiptunesak/goat_tracker.html):
- Only implements GTS5. No V1 format handling. Useful as V2 reference only.

**Battle of the Bits Lyceum** (https://battleofthebits.com/lyceum/View/GoatTracker+Effects+Commands):
- Documents V2 command set (0XY = nop in V2). V1 arpeggio (0XY) not present.

**Codebase64.org**: Site appears compromised (domain shows unrelated content). No GoatTracker V1 technical content retrieved.

**Pouet.net GoatTracker entry** (https://www.pouet.net/prod.php?which=13367): User testimonials only, no technical content.

---

## 13. Open Questions (BINARY RE NEEDED TO CONFIRM)

1. **Half-speed arpeggio exact counter logic**: How does the `asl` at `mt_arpeggio` in player1_v153.s exactly gate the half-speed behaviour? The player doubles A (the databyte) before the counter comparison. Needs careful cycle-tracing to confirm the 6-state vs 3-state cycle under half-speed.

2. **V1.25 arpeggio counter**: The V1.25 player (`mt_chnarpcount` usage) may differ from V1.53. Need to read the arpeggio execution in player1_125.s to confirm the 3-note cycle matches V1.53.

3. **Filter byte in V1.25 packed binary**: The instrument's `mt_instfilter` byte ($4006) — how does the V1.25 player apply it? Does it write directly to $D417+$D416+$D418, or does it set ghost regs differently? (See `mt_newnoteinit` in player1_125.s.)

4. **Wavetable index encoding**: Is `mt_instwave` a BYTE index into the flat waveform/note arrays (i.e., index into mt_wavetbl = index into mt_notetbl), or a PAIR index? The player uses it as `lda mt_wavetbl,y` with y = mt_instwave, so it appears to be a direct byte index into the waveform array. Confirm from packer output.

5. **GTS3 identifier**: Cadaver's V2 transition from "GTS!" (V1) — was V2.0 immediately GTS3, or did it use GTS2 briefly? The V2 beta thread implies GTS3 existed before GTS4 (v2.4), but no V2.0 source doc was found to confirm the exact transition point.

6. **HVSC V1 SNG data format**: HVSC stores `.sid` files (packed+relocated). A V1 SID unpacked to .SNG would use "GTS!" header. But does any HVSC V1 SID have the .SNG preserved? The packed binary format has a different layout than the .SNG.

## Leads to Follow

- Read `pipelines/goattracker/docs/src/v1_player1_125.s` lines 340+ (the arpeggio + filter execution) to answer OPENs 2 and 3.
- Check `pipelines/goattracker/docs/src/v1_player2_v153.s` (gamemusic playroutine) for SFX integration differences.
- The packer/relocator source `goattrk.c` (inside the V1.53 ZIP: `cadaver.github.io/tools/goattrk.zip`) splits the SNG interleaved wavetable into separate mt_wavetbl/mt_notetbl regions. Reading the packer would confirm the exact byte ordering + instrument index computation → needed for extraction.
- Search CSDb for V1-era songs and inspect their packed `.sid` binaries to find the GTS! header offset and confirm instrument layout.
- Check `pipelines/goattracker/docs/gt2_data_layout.md` for V2 packed layout; compare structurally with V1 to identify extraction differences.
- The `v1_gmusic_v153.s` (gamemusic player) has the same wavetable system but also adds RELOCATEMUSIC — reading it would clarify how the packer computes section offsets (mt_wavetbl, mt_notetbl, etc. are `= mt_musicdata+4` placeholders pre-relocation).
