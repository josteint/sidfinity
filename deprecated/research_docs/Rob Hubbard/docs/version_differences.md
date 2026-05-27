---
source_url: multiple
fetched_via: direct + search results
fetch_date: 2026-04-21
author: various (compiled from multiple sources)
content_date: various
reliability: secondary
---

# Rob Hubbard Driver Version Differences

---

## SIDId Detected Variants

From `sidid.cfg` (Cadaver's SIDId tool):

| Variant Name | SIDId Pattern | Notes |
|-------------|---------------|-------|
| `Rob_Hubbard` | 6 multi-line patterns | Core driver, most songs |
| `Rob_Hubbard_Digi` | 1 pattern | Late driver with PCM playback |
| `Paradroid/HubbardEd` | 1 short pattern | ZP $FC pointer, different flag layout |
| `Giulio_Zicchi` | 1 pattern | Italian composer variant, same 3-channel loop |
| `Bjerregaard` | 1 pattern | Stack-based register write, Johannes Bjerregaard |

These are sub-variants detected within the Rob_Hubbard family.

---

## Feature Timeline (by first appearance)

### Phase 1: Core driver (1984-1985)
Songs: Confuzion, Thing on a Spring, Monty on the Run, Action Biker, Crazy Comets

- 3 channels
- Single global speed counter (`resetspd` = fixed value at load time)
- Note format: 2-4 bytes (length byte + optional instrument byte + pitch byte)
- 8-byte instruments: PW, waveform, ADSR, vibrato depth, PWM speed, effects flags
- Effects: drum (bit 0), skydive (bit 1), octave arpeggio (bit 2)
- Vibrato: triangle LFO via 3-bit counter → 01233210 pattern
- PWM: sweeps between $0800 and $0E00
- Hard restart: clear gate + zero ADSR before new note

### Phase 2: Expansion (1985-1986)
Songs: Commando, International Karate, Lightforce

- Frequency table trick (out-of-range pitches index player variables)
  - First appeared in Commando (late 1985)
- Pattern transposition: notes can be transposed at track level to save memory
  - First appeared in International Karate (1986)
- In-song tempo changes: IK has a "double tempo" section
  - Mechanism: either fourth channel speed table or pattern-embedded speed changes
  - NOT CIA multispeed — these are data-driven tempo shifts within the driver

### Phase 3: Advanced features (1986-1987)
Songs: Delta, Last V8, Sanxion, Zoolook

- Filter control: SID filter register writes added
- Fourth channel: effects/filter/tempo/speed table control track
  - Documented in forum as "controlling the filter, tempo, speed table stuff"
  - Mechanism: a 4th data channel that the driver reads for meta-commands
- Arpeggio tables: data-driven arpeggio (replaced the simple octave-up bit)
  - Appeared March 1987 based on HVSC timeline
- Table-driven drums: drum effects from tables, not hardcoded
  - Appeared March 1987
- Table-driven PWM: PWM parameters from tables
  - Appeared July 1987

### Phase 4: Digi + Obfuscation (1987+)
Songs: Arcade Classics, various EA games

- 4-bit PCM via volume register ($D418)
  - Detected separately as `Rob_Hubbard_Digi`
  - Uses volume nibble writes timed to the interrupt
  - `LSR/LSR/LSR/LSR` to extract high nibble, `AND #$0F` for low nibble
- Code scrambling: routine obfuscated to prevent unauthorized copying
  - Triggered by other composers (Bjerregaard, Zicchi, Kimmel) copying the driver
- CIA multispeed: some songs run at 200Hz (4x) or 100Hz (2x)
  - Wizball confirmed 200Hz
  - Routine is called 4× per frame by the interrupt handler

---

## Specific Per-Song Speed Variations

### Fixed global speed (early driver)
`resetspd` is a constant set at player load time. All 3 channels run at the same speed.
E.g., Monty on the Run: resetspd=1 (2 frames/tick)

### Per-song speed table (multi-subtune SIDs)
When a SID has multiple subtunes, some variants use a speed table indexed by song number:
```assembly
LDA songtempos,X    ; BD lo hi
STA resetspd        ; 8D lo hi
```
Our `find_speed()` in rh_decompile.py detects this pattern.

### Nested double-counter (some variants)
Outer counter wraps the inner counter:
```assembly
DEC outer_ctr
BPL inner_counter_addr    ; skip inner when outer hasn't fired
LDA #imm
STA outer_ctr
JMP past_inner

inner_counter_addr:
DEC inner_ctr
BPL post
LDA tempo_var
STA inner_ctr
; ... music fires here
```
Effect: music fires approximately every (inner_speed + outer_imm) / 2 frames.
Our rh_decompile.py Pass 3 detects this.

### CIA multispeed (Wizball and late games)
Interrupt fires 2x or 4x per frame via CIA timer configuration.
The SID header `speed` bits indicate this (bit N = 1 means CIA timer for subtune N).
Cannot be detected from static analysis of the player binary alone — must read SID header.

---

## Paradroid/HubbardEd Variant Details

SIDId signature: `B1 FC 10 1B C9 FF F0 12 C9 FE F0 0A`

Differences from main Rob_Hubbard:
- Pattern pointer at ZP $FC (instead of $04/$05)
- `LDA ($FC),Y` for pattern fetch
- Same $FF/$FE terminators
- Unknown: whether speed counter is in same location or different ZP address

This variant appears in songs composed with a modified editor tool ("HubbardEd"),
possibly the "Robb Hubbard Music Editor V1.5" by BHT (csdb id 66495).

---

## Composer Variants

### Johannes Bjerregaard
SIDId signature: `99 03 D4 AE ?? ?? 9D ?? ?? 68 9D ?? ?? A9 01 9D`
- Stack-based register write (PHA/PLA around freq writes)
- Composing: Myth, Sanxion in-game (modified from Hubbard), his own compositions

### Giulio Zicchi
SIDId signature: `CA 30 03 4C ?? ?? 60 A2 00 8E ?? ?? E8 8E ?? ?? 60 A0 00`
- Same 3-channel loop structure (DEX/BMI/JMP)
- Minor structural differences in channel loop bookkeeping

### Jeroen Kimmel (Red/Judges)
- Converted Crazy Comets driver to editable source
- Used it for his own compositions
- No separate SIDId signature found — probably matched by main Rob_Hubbard pattern

---

## What "Phase 2, Phase 3, Phase 4" Actually Means

The web search found this terminology used for a DIFFERENT composer's drivers
(appears to be Laxity's drivers, NOT Rob Hubbard's):
> "Driver 1: 1987, annoying raster spikes"
> "Driver 2: late 1987/early 1988, fixed raster spikes"
> "Driver 3: 1989, hard restart with filter/pulse programs"
> "Driver 4: never released"

**Rob Hubbard himself did not use Phase 2/3/4 terminology.**
Our internal naming convention (if used) should be:
- "Classic/early" = Confuzion through Commando era (1985-1986)
- "Advanced" = Delta/Sanxion/Zoolook era (1986-1987)
- "Digi" = Arcade Classics / EA era (1987+)
