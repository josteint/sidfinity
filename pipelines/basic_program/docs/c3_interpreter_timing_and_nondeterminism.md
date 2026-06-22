---
source_url: multiple (pagetable.com/c64ref/c64disasm, c64-wiki.com, skoolkid.github.io/sk6502/c64rom, larsgregori.de, lemon64.com, emudev.de, sta.c64.org, bumbershootsoft.wordpress.com, scruss/bench64, zimmers.net)
fetched_via: WebFetch + WebSearch
fetch_date: 2026-06-22
author: SIDfinity LEAF research agent (cluster 3 — execution + timing + nondeterminism)
content_date: 2026-06-22
reliability: derived from primary C64 ROM disassembly + community technical documentation
---

# Cluster 3: C64 BASIC V2 Interpreter — Execution Model, Timing, and Nondeterminism

**Context:** The 486 `Basic_Program` SIDs in HVSC are all RSID v2 with `load=init=play=0` and the BASIC flag set. They run from $0801 via the C64 BASIC V2 interpreter; there is no `play()` vector. This document answers whether their $D400–$D418 write stream is deterministic, at what granularity (cycle-exact vs ordered-(reg,val)), and which tunes are inherently reproducible vs inherently random.

---

## 1. How RUN Executes: The BASIC Main Loop

### 1.1 CHRGET — the atomic fetch primitive ($0073–$008A, zero page)

CHRGET is the innermost routine of the BASIC interpreter. It is copied from ROM into **zero page ($0073–$008A)** at cold-start so every call uses zero-page addressing (3–4 cycles per instruction, critical for speed). The full listing:

```
0073: E6 7A    INC $7A        ; increment TXTPTR low byte (self-modifying text pointer)
0075: D0 02    BNE $0079      ; skip carry
0077: E6 7B    INC $7B        ; increment TXTPTR high byte
0079: AD 00 08 LDA $0800      ; self-modifying LDA abs — address bytes at $007A/$007B
                               ; (patched to current program text pointer)
007C: C9 3A    CMP #':'       ; colon or higher = end of statement
007E: B0 0A    BCS $008A      ; carry set = end-of-statement (zero flag = 1 iff exactly ':')
0080: C9 20    CMP #' '       ; space?
0082: F0 EF    BEQ $0073      ; skip spaces (loop back)
0084: 38       SEC
0085: E9 30    SBC #$30       ; subtract '0' — carry=0 if result < 0 (i.e. it's a digit)
0087: 38       SEC
0088: E9 D0    SBC #$D0
008A: 60       RTS
```

**Flags on exit:**
- Carry=0 → character was a decimal digit  
- Zero=1 → end of statement (colon) or null (EOL)
- Zero=0 → non-digit character fetched

**Key property:** CHRGET is self-modifying code — the `LDA $0800` operand bytes at $007A–$007B ARE TXTPTR. Incrementing $7A/$7B (before the LDA) and then reading through the LDA is how the interpreter walks the program text.

### 1.2 Statement dispatch: $A7AE–$A81A

The main interpreter inner loop lives at **$A7AE** (decimal 42926):

1. Check for CTRL-C (run/stop key) via the keyboard buffer flag.
2. Load the BASIC execution pointer ($7A–$7B = TXTPTR).
3. Fetch byte at current position. If **zero** (end-of-line), load the next line pointer and continue.
4. Transition to a new line: extract line number into $39–$3A (CURLIN), advance TXTPTR past the 4-byte line header (next-pointer + line-number).
5. **Token dispatch at $A7ED:** subtract $80 from the fetched token byte; use the result as an index into the statement dispatch table **STMDSP at $A00C**. Each entry is (address−1), exploiting the 6502 RTS convention. Invalid tokens (< $80) fall through to LET processing.
6. Colon (`:`) delimiter encountered → restart loop (next statement in same line).
7. `GO` token → GOTO/GOSUB handling.

The dispatch table STMDSP ($A00C) has 43 entries for all BASIC keywords:
- END ($A831), FOR ($A742), NEXT ($AD1E), DATA ($A8F8), INPUT# ($ABA5), INPUT ($ABBF), DIM, READ, LET, GOTO ($A8A0), RUN, IF, RESTORE ($A81D), GOSUB ($A883), RETURN ($A8D2), REM, STOP, ON, WAIT, LOAD, SAVE, VERIFY, DEF, POKE, PRINT#, PRINT, CONT, LIST, CLR, CMD, SYS, OPEN, CLOSE, GET ($AB7B), NEW ($A642).

### 1.3 FOR/NEXT stack mechanics

**FOR** at $A742 pushes an **18-byte frame** (FORSIZ=$12) onto the hardware stack:
- 2 bytes: variable pointer (points into the variable list at VARTAB)
- Step value (5-byte float)
- Limit value (5-byte float)  
- Current value (5-byte float)
- Return line number and TXTPTR offset for the body

**FNDFOR** ($A38A) searches the stack for a FOR frame: walks up by 18 bytes comparing the stored variable pointer. If NEXT specifies a variable name, it searches for matching frame. If no variable, uses the topmost FOR frame. Carry=1 on success, carry=0 on failure.

**NEXT** at $AD1E:
1. Calls FNDFOR to locate the matching FOR frame.
2. Retrieves step and limit values.
3. Adds step to the loop variable (floating-point add via FADD).
4. Compares new value to limit (floating-point compare).
5. If loop continues: restores TXTPTR to the saved body position (fast — direct address, no line scan).
6. If loop done: pops the 18-byte frame from the stack.

**Nesting limit:** Up to 9 simultaneous open FOR loops (hardware stack is 256 bytes; 9 × 18 = 162 bytes + other stack use).

### 1.4 Variable storage and lookup

Variables are stored in a **linear list** starting at **VARTAB** ($2D–$2E). Each numeric variable occupies **7 bytes** (2-byte name + 5-byte floating-point value). String variables have a 2-byte name + 5 bytes for a descriptor.

**Lookup** during expression evaluation: BASIC scans linearly from VARTAB, comparing 2-byte name prefixes until a match is found or ARYTAB ($2F–$30) is reached. **Cost is O(N) in the number of previously-declared variables.** This means:
- The Nth variable accessed takes ~7N cycles to find (each 7-byte step = ~4 LDA/CMP pairs = ~8 cycles → ~56N cycles per lookup).
- Variables declared first are found fastest.
- This O(N) cost is DETERMINISTIC for a given program run (the same variables appear in the same order every time the program runs from a clean state).

Arrays are stored at ARYTAB after simple variables. Accessing an array after declaring it also requires walking past all simple variables first.

### 1.5 READ/DATA/RESTORE

- **RESTORE** ($A81D) resets data pointer: DATLIN ($3F–$40) ← start of program, DATPTR ($41–$42) ← start of program.
- **READ** ($AC06) scans program for DATA tokens, then reads values advancing DATPTR.
- **DATA** statements are tokenized as $83 and skipped during normal execution; READ finds them by token.
- All of this is deterministic: same DATA, same READ sequence, same result every run.

---

## 2. Timing Model and Cycle Cost

### 2.1 The PAL C64 clock and frame budget

- **PAL CPU clock:** 985,248 Hz (0.985 MHz)
- **PAL frame rate:** 50 Hz (19,656 cycles per VBI frame; sidplayfp uses ~19,656)
- **NTSC CPU clock:** 1,022,727 Hz; NTSC 60 Hz → ~17,045 cycles per frame

### 2.2 FOR/NEXT iteration speed

From the bench64 benchmark (scruss/bench64, NTSC C64):
- **Null FOR/NEXT loop: ~674 iterations/second** (NTSC)
- PAL C64 is ~3% slower (index ~97 vs 100 for NTSC) → ~654 iterations/second

Working backwards: at 1,022,727 Hz / 674 = **~1,518 cycles per null FOR/NEXT iteration** (NTSC). Confirmed order-of-magnitude: a `FOR L=1 TO 145:NEXT` busy-wait takes ~145 × 1,518 ≈ 220,000 cycles ≈ 215 ms (NTSC) / 222 ms (PAL). Since PAL BASIC music tunes typically target 50 Hz, a 220,000-cycle delay corresponds to ~11 PAL frames — a plausible tempo for a slow melody.

**The actual cycle cost per FOR/NEXT iteration depends on:**
1. Number of variables already declared (linear-scan cost for the loop variable).
2. Whether the limit variable is a literal constant (faster) or a named variable (second scan).
3. The step size (default 1 = integer fast-path vs float step).

For a specific program with a fixed variable layout, the per-iteration cost is **perfectly deterministic** across runs — same program, same variable initialization order, same cost.

### 2.3 Floating-point cost

C64 BASIC V2 uses Microsoft floating-point: 5 bytes per number (1-byte exponent + 4-byte mantissa). FAC1 ($61–$66) and FAC2 ($69–$6E) are the accumulators. Every `POKES+1,PEEK(M)/28` requires:
1. Evaluate `M` (float lookup, ~56×N cycles)
2. PEEK($DFB8 or wherever M points) (fast, ~10 cycles)
3. Float division by 28 (~300 cycles for FP divide)
4. POKE to SID register (fast, ~15 cycles)

Total per SID write: hundreds of cycles. Exact count depends on variable count. This is why algorithmic tunes advance M by 0.2 (5 iterations per integer step) — the FP overhead is so high that each BASIC "note" takes many milliseconds.

### 2.4 VIC-II bad line cycle stealing

On every 8th raster line (when $D011 bit 3 is set), the VIC-II steals the bus from the CPU for character fetch. On a bad line, the CPU gets only **23 cycles** instead of 63. This happens 25 times per PAL frame.

**Effect on BASIC timing:** BASIC programs that happen to be executing during bad lines are slowed slightly (~40 cycles × 25 bad lines / frame = 1,000 cycles/frame stolen). This is ~5% of the frame budget.

**Critically: bad lines are tied to the raster and are therefore DETERMINISTIC** — they occur at the same raster positions every frame. Given a program running from a known state, the bad-line pattern relative to instruction execution is deterministic (same code, same timing).

---

## 3. The KERNAL IRQ and the Jiffy Clock

### 3.1 CIA #1 Timer A and the jiffy interrupt

The KERNAL initializes **CIA #1 Timer A** at startup to fire at **~60 Hz** (actually 1/60.05 s PAL, 1/59.86 s NTSC):
- **PAL reload value:** $4025 (hex) = 16,421 decimal cycles
- **NTSC reload value:** approximately $4295 cycles
- CIA timers count down 1 per CPU cycle; on underflow they reload and assert the IRQ line.

The KERNAL IRQ service routine at **$EA31** is entered at each timer underflow:

| Step | Routine | Purpose |
|------|---------|---------|
| $EA31 | JSR [$FFEA] → $F69B (UDTIM) | Increment jiffy clock at $A0–$A2 |
| $EA34–$EA5E | Cursor blink logic | Decrement counter, toggle cursor char |
| $EA61–$EA79 | Cassette motor control | Read I/O port, manage motor bit |
| $EA7B | JSR [$EA87] (SCNKEY) | Scan keyboard matrix; fill buffer $0277–$0280 |
| $EA7E–$EA86 | Cleanup | Restore registers, RTI |

**Total cycle cost:** The IRQ handler takes approximately **300–1,400 cycles** per invocation. The wide range is due to the keyboard scanner: when no key is pressed, SCNKEY terminates quickly (~200 cycles); when a key is being debounced, it takes much longer (~1,000+ cycles). This variability is the dominant source of jitter in BASIC program timing.

One forum measurement described "~21 full raster lines" for the IRQ handler (21 × 63 = 1,323 cycles), but this appears to be a worst-case (key-press) figure.

### 3.2 UDTIM — the jiffy clock increment ($F69B)

```
F69B  A2 00        LDX #$00
F69D  E6 A2        INC $A2           ; increment low byte of jiffy clock
F69F  D0 06        BNE $F6A7         ; no carry
F6A1  E6 A1        INC $A1           ; increment mid byte
F6A3  D0 02        BNE $F6A7         ; no carry
F6A5  E6 A0        INC $A0           ; increment high byte
F6A7  38           SEC
F6A8  A5 A2        LDA $A2
F6AA  E9 01        SBC #$01          ; compare to $4F1A01 (24 hrs in jiffies)
F6AC  A5 A1        LDA $A1
F6AE  E9 1A        SBC #$1A
F6B0  A5 A0        LDA $A0
F6B2  E9 4F        SBC #$4F
F6B4  90 06        BCC $F6BC         ; < 24 hrs, don't reset
F6B6  86 A0        STX $A0           ; reset all three bytes to 0
F6B8  86 A1        STX $A1
F6BA  86 A2        STX $A2
```

The jiffy clock at **$A0–$A2** is a 3-byte binary counter (NOT BCD), incremented once per IRQ (nominally once per 16,421 cycles on PAL). It rolls over after 24 hours (5,184,001 jiffies = $4F1A01).

**TI (BASIC variable):** Reads $A0–$A2 as a 3-byte integer value. `TI=0` after cold start or reset. `TI$="000000"` resets TI to 0.

**Initialization:** TI is set to **0 on power-on/reset**. It is NOT reset by RUN or CLR — only by cold start (hardware reset) or explicit `TI$="000000"`.

### 3.3 Is the jiffy clock deterministic for BASIC music?

**In an emulator with cycle-accurate CIA emulation:** YES — **deterministic**. CIA1 Timer A starts at its reload value ($4025 PAL) at cycle 0 after reset and counts down exactly 1 per CPU cycle. The first IRQ fires at cycle 16,421; subsequent IRQs at multiples thereof (plus RTI overhead). Since the C64 cold-start ROM initializes TI=0, and the CIA timer starts from a known value, TI advances in a completely deterministic way throughout program execution.

**On real hardware:** Also deterministic — same startup state, same CIA initial value, same jiffy increment timing. The KERNAL writes the CIA reload values at a specific boot ROM location that runs identically every cold start.

**BUT:** The keyboard scanner within the IRQ introduces **cycle-level jitter** — the IRQ handler takes more or fewer cycles depending on keyboard state. In sidplayfp emulation with no key pressed, the keyboard scanner always takes the same path (no key debounce), making the total IRQ duration **deterministic** in the emulator under the "no key pressed" assumption.

---

## 4. Nondeterminism Risk — Complete Catalogue

This section flags every source of potential nondeterminism in BASIC music programs. Each is classified as **DETERMINISTIC** (reproducible across runs), **EMULATOR-DETERMINISTIC** (reproducible under emulator's fixed-state assumption), or **TRULY NONDETERMINISTIC** (cannot be reproduced without the original hardware state).

### 4.1 RND function — the most important source

**RND(positive) — e.g. `RND(1)`, `RND(B)` where B > 0:**
- Uses a **PRNG with seed at $8B–$8F** (5-byte float).
- Algorithm: multiply previous result by constant 11,879,546 + add constant 3.927677739E-8.
- Seed is initialized from ROM during cold start ($E3A2–$E3BE → copied to $8B–$8F).
- **Initial seed after cold start:** $80, $4F, $C7, $52, $58 (documented; verified empirically — same five numbers 19, 5, 83, 56, 90 appear on every fresh boot).
- CLR/RUN do NOT reset the seed — the seed only resets on cold start (hardware reset/power-on).
- **BUT:** Under sidplayfp, the psiddrv.cpp initializes a known C64 state before each tune. The cold-start ROM initialization sequence runs (it copies CHRGET + the initial seed from ROM). So the seed is always $80,$4F,$C7,$52,$58 when the BASIC program starts.
- **Classification: EMULATOR-DETERMINISTIC.** The PRNG sequence is fully deterministic from a fixed seed. Since sidplayfp performs a cold-start-equivalent initialization, RND(1) always produces the same sequence.
- **Caveat:** If a tune calls `RND(1)` AFTER calling `RND(0)` or `RND(-TI)`, the seed has been mutated by the nondeterministic source and the subsequent PRNG sequence is also nondeterministic.

**RND(0):**
- Reads **CIA #1 Timer A registers $DC04 (low) and $DC05 (high)** plus Time-of-Day registers **$DC08 and $DC09** (10th of seconds, seconds).
- CIA Timer A is a free-running countdown counter — it counts down from $4025 at 985,248 Hz. The exact value when RND(0) is called depends on exactly how many CPU cycles have elapsed since the last timer reload.
- The TOD clock ($DC08/$DC09) is a real-time clock driven by 50/60 Hz AC power; on a real C64 it starts from 0 but advances in real time, not cycle time.
- **Under sidplayfp:** CIA Timer A IS cycle-accurately emulated. Its value at any given moment is a function of total cycles executed since reset, which is deterministic. TOD clock is also emulated.
- **BUT:** Even in the emulator, the CIA timer value at the moment `RND(0)` is called depends on the exact instruction count to reach that call, which in turn depends on the full execution path, variable count, prior BASIC computation, and KERNAL IRQ timing. This is effectively random from a music-replication standpoint.
- **Classification: TRULY NONDETERMINISTIC for practical purposes.** Even if technically deterministic inside one sidplayfp session, any change in execution path, variable ordering, or run environment changes the CIA timer value at the call site.
- **Tunes using `RND(0)` or `RND(-TI)` as seeds:** Not reproducible register-exactly across different recordings. Their write stream is a one-time event.

**RND(negative) — e.g. `RND(-1)`, `RND(-100)`, `RND(-TI)`:**
- `RND(-N)` with a fixed literal N (not TI): deterministic — always seeds to the same value. Subsequent `RND(1)` calls give the same sequence.
- `RND(-TI)`: Seeds with the current jiffy clock. Since TI depends on how long the program has been running before this call, and that depends on execution path... **TRULY NONDETERMINISTIC** in the same way as RND(0).
- **Classification:** `RND(-literal)` = EMULATOR-DETERMINISTIC. `RND(-TI)` = TRULY NONDETERMINISTIC.

### 4.2 TI — the jiffy clock variable

Used in tunes like `POKES+8,TI AND PEEK(M+64)` (Two Lines of Code by Alan Bond):
- TI advances by 1 per jiffy (~1/60 s).
- Under sidplayfp (cycle-accurate CIA emulation), TI starts at 0 after cold-start reset.
- The timing of when BASIC code reads TI relative to IRQ firing is deterministic given a fixed execution path.
- **Classification: EMULATOR-DETERMINISTIC** under the "no key pressed" assumption (no keyboard jitter in the IRQ handler).
- **Real hardware caveat:** If the user runs the program some jiffies after boot, TI is nonzero at program start → different music. This means two HVSC recordings made at different boot times would differ.

### 4.3 PEEK of time-varying hardware registers

Specific dangerous PEEK targets:
- **$D012 (VIC-II raster counter):** Returns the current raster line (0–311 PAL). This is CYCLE-DEPENDENT and effectively nondeterministic unless the read happens at a fixed raster position each iteration.
- **$DC04/$DC05 (CIA #1 Timer A):** Free-running countdown; its value at any given BASIC statement is cycle-dependent. TRULY NONDETERMINISTIC in practice.
- **$DC08–$DC09 (CIA #1 TOD clock):** Time-of-day BCD clock. Nondeterministic.
- **$DD04–$DD07 (CIA #2 timers):** Same as CIA #1.

**$DFB8 and above (I/O expansion area 2):** On a stock C64 with no cartridge, reads from $DE00–$DFFF (I/O expansion areas 1 and 2) return **open bus** — typically $FF, but can vary. Under sidplayfp, likely returns 0 or $FF consistently.

**ROM areas ($A000–$BFFF BASIC ROM, $E000–$FFFF KERNAL ROM):** PEEK returns fixed ROM bytes — **DETERMINISTIC** and invariant. The "Two Lines of Code" M=57272 trick eventually reads KERNAL ROM ($E000+) bytes as melody data, which is fully deterministic (same ROM, same bytes, same melody). The initial reads from $DFB8–$DFFF (I/O expansion area 2) return a fixed value under emulation.

**C64 color RAM ($D800–$DBFF):** Uninitialized at power-on; content is undefined. A PEEK into color RAM could return arbitrary values. Under sidplayfp's cold-start initialization, color RAM is likely zeroed or set to a fixed pattern (the psiddrv.cpp `fillRam` call clears $0000–$03FF; color RAM at $D800 is not in that range).

### 4.4 GET — keyboard reading

`GET A$` calls KERNAL GETIN ($FFE4 → actual keyboard reader), which:
1. Checks the keyboard buffer at $0277–$0280 (length in $C6).
2. If buffer is empty → returns immediately with `A$=""` (null string, 0 byte).
3. If buffer has a key → dequeues and returns it.

The KERNAL IRQ fills the keyboard buffer by scanning the matrix at $EA7B (SCNKEY) every jiffy.

**In sidplayfp emulation with no key injection:** The keyboard matrix always reads "no keys pressed" → buffer stays empty → every `GET A$` returns `""` immediately. This is **DETERMINISTIC**.

**Interactive tunes (like Ahoy_Magazine_BASIC):** The HVSC recording was made without interactive key presses (the HVSC maintainers record the "idle" path). Under emulation with no keys, the GET branch `IF A$="" THEN loop` always fires → music loops deterministically → **DETERMINISTIC** for the recorded path.

**Special case:** If a BASIC program explicitly polls for a specific key to stop, and the HVSC recording happened to stop at a specific point, the stopping condition won't fire in emulation (no key) → the tune loops indefinitely past the HVSC recording length. This is a capture-length issue, not a nondeterminism issue.

### 4.5 WAIT — waiting for I/O register bits

`WAIT 53265,128,0` (WAIT $D011, $80, 0) blocks until bit 7 of $D011 (raster bit 8) toggles. Since VIC-II raster timing is deterministic in a cycle-accurate emulator, WAIT also terminates deterministically. However, the exact cycle at which WAIT exits depends on raster timing, which interleaves with BASIC execution in a deterministic but complex way.

### 4.6 Variable lookup overhead — timing nondeterminism

As noted in section 1.4, variable lookup time scales O(N) with the number of declared variables. This means:
- A FOR/NEXT loop early in the program (few variables declared) runs FASTER than the same loop later (many variables declared).
- **This variation is DETERMINISTIC** for a given program: same variable count, same lookup cost, every run.
- But it means FOR/NEXT loops serving as delay timers are NOT constant-time across different parts of the same program.

**Implication for music:** The `FOR L=1 TO 145:NEXT` tempo delay is only as accurate as the variable count at that point. If declared after many other variables, L's lookup is slower → each iteration takes more cycles → the delay is longer. This is deterministic but program-state-dependent.

### 4.7 Summary nondeterminism table

| Source | Classification | Notes |
|--------|---------------|-------|
| `RND(1)` / `RND(positive)` | EMULATOR-DETERMINISTIC | Fixed seed from ROM at cold start; same sequence every emulated run |
| `RND(0)` | TRULY NONDETERMINISTIC | Reads running CIA timer — value changes per cycle |
| `RND(-TI)` | TRULY NONDETERMINISTIC | Seeds from jiffy clock at call time |
| `RND(-literal)` | EMULATOR-DETERMINISTIC | Fixed seed → same sequence |
| `TI` / jiffy clock | EMULATOR-DETERMINISTIC | Starts at 0, advances at fixed CIA rate in emulator |
| `TI$="000000"` reset | DETERMINISTIC | Explicit reset |
| `GET A$` (no key) | DETERMINISTIC | Returns "" immediately; buffer empty under emulation |
| `PEEK(ROM_addr)` | DETERMINISTIC | ROM bytes are fixed ($A000–$BFFF BASIC, $E000–$FFFF KERNAL) |
| `PEEK($D012)` raster | NONDETERMINISTIC | Cycle-dependent; varies per BASIC path |
| `PEEK($DC04)` CIA timer | TRULY NONDETERMINISTIC | Running counter, cycle-dependent |
| `PEEK($D800-$DBFF)` color RAM | POTENTIALLY NONDETERMINISTIC | Uninitialized RAM; emulator may zero it |
| FOR/NEXT delay loop | EMULATOR-DETERMINISTIC | Cycle count is fixed given fixed variable layout |
| DATA/READ sequences | DETERMINISTIC | Fully sequential, deterministic |
| Variable lookup cost | DETERMINISTIC (but program-state-dependent) | Same cost every run for same program |

---

## 5. Verification Mode Analysis

### 5.1 No play() vector — the fundamental difference

BASIC tunes have **no PSID play() vector**. sidplayfp handles them by:
- Setting init address to $BF55 (BASIC interpreter entry point) when BASIC flag is set.
- Installing a "basic trap" at $BF53.
- Clearing $0000–$03FF, setting PAL/NTSC flag at $02A6.
- Then letting the C64 run: BASIC executes GOTO loops indefinitely, poking SID via POKE statements.

The SID writes happen whenever BASIC executes a POKE to $D400–$D418. These writes occur at irregular CPU-cycle intervals: sometimes several writes per "frame" (for ADSR setup in the init section), sometimes one write per many frames (for note frequency during a FOR/NEXT delay). There is no 50-Hz periodicity to the writes.

### 5.2 Mode 1 (per-play() frame) — DOES NOT APPLY

Mode 1 buckets writes per play() invocation. BASIC has no play() vector → no bucket boundaries → Mode 1 is inapplicable.

### 5.3 Mode 2 (cycle-exact) — THEORETICALLY APPLICABLE, PRACTICALLY TOO STRICT

Mode 2 requires `(cycle, reg, val)` matching. In principle, if BASIC execution is fully cycle-deterministic (which it is under emulation), Mode 2 would be achievable. But:
- The cycle timestamps depend on every BASIC instruction, every variable lookup, every FP operation, and every KERNAL IRQ interrupt boundary.
- Any change in BASIC execution environment (variable count, KERNAL version, even the number of open files) changes cycle timestamps.
- For emulation purposes (comparing two emulator runs), cycle-exact IS achievable.
- For comparing emulator output to a recording from real hardware, cycles will differ due to PRG load time, keyboard scanner jitter, exact CIA timer phase at run-start, etc.

**Verdict: Cycle-exact is too strict for inter-machine comparison but achievable within one emulator.**

### 5.4 Recommended verification mode: continuous ordered (reg,val) stream

The appropriate mode is **a continuous, uninterrupted `(reg, val)` write stream** — the flat sequence of SID register writes in order, with cycle timestamps DROPPED. Concretely:
- Capture: `siddump --writelog` on the RSID file with ROM images supplied.
- Compare: flat `(reg, val)` sequence, no frame bucketing, no cycle matching.
- This is robust to: KERNAL IRQ jitter, variable-lookup cycle variation, bad-line phase variation.
- This is NOT robust to: RND(0) nondeterminism (different runs, different sequences).

**For the DATA/READ class (the majority):** The write stream is perfectly deterministic under emulation. Any two emulator runs produce identical (reg,val) sequences.

**For the TI-based algorithmic class:** The write stream is deterministic within one emulator session (TI starts at 0, advances at fixed CIA rate). Two recordings from the same emulator at the same "song start from clean state" will match.

**For the RND(0)/RND(-TI) class:** The write stream is inherently nondeterministic. No USF representation can be faithful to the original (different runs = different music). Options: (a) exclude from USF pipeline; (b) note as "inherently random, record one realization"; (c) detect the RND(0) usage and flag the tune in the DB.

### 5.5 Cycle-level precision: within-emulator vs cross-platform

| Scenario | (reg,val) ordered stream matches? | Cycle timestamps match? |
|----------|----------------------------------|------------------------|
| Two emulator runs, same ROM, no RND(0) | YES | YES |
| Two emulator runs, same ROM, uses TI | YES (TI is deterministic in emulator) | YES |
| Two emulator runs, same ROM, uses RND(0) | NO (different CIA timer value) | NO |
| Emulator vs real hardware | YES if same program, same ROM, same start state | NO (keyboard jitter, CIA phase) |
| Two real hardware runs | Depends on RND(0) usage; TI same if same start jiffies | NO |

---

## 6. sidplayfp's Handling of BASIC RSIDs

From the `psiddrv.cpp` analysis:

1. When the BASIC flag is set, the psiddrv overrides init to `$BF55` (BASIC interpreter warm-start entry).
2. It installs a "basic trap" at `$BF53` for subtune selection (writes subtune number for $030C).
3. Memory clear: `fillRam(0, 0, 0x3FF)` — clears zero page and the BASIC stack area.
4. Copies "power-on patterns from a pre-recorded kernel reset state" — this includes the CHRGET routine AND the RND seed ($80,$4F,$C7,$52,$58) being placed at $8B–$8F.
5. Sets $02A6 to PAL/NTSC flag.
6. CIA #1 Timer A is configured for 60 Hz by the KERNAL ROM startup code.

**Key conclusion:** sidplayfp provides a fully deterministic C64 cold-start environment. The BASIC program always starts from the same machine state. Given no RND(0) usage, the write stream is reproducible across emulator runs.

---

## 7. Recommended Sub-Classification for the 486-SID Corpus

For pipeline planning, the nondeterminism axis suggests:

**Class A — DATA/READ table-driven (deterministic):**  
Note tables in DATA statements; FOR/NEXT delay for tempo; no RND(0). These produce a deterministic write stream. Example: `Ahoy_Magazine_BASIC.sid`. Likely the MAJORITY of the 486 corpus. Can be decompiled to note events → principled USF representation.

**Class B — Algorithmic with TI or fixed-seed RND (emulator-deterministic):**  
Uses `TI` for rhythm or `RND(positive)` with power-on default seed. The write stream is deterministic in sidplayfp. Example: `Two_Lines_of_Code_1_BASIC.sid` (reads ROM bytes + TI). These can be captured by the emulator and the stream is reproducible. USF representation: "algorithmic emulation trace" — harder to make principled but capturable.

**Class C — Truly nondeterministic (RND(0), RND(-TI)):**  
These include `RND(0)` which reads a running CIA timer, or `RND(-TI)` which seeds from the jiffy clock at call time. Each run produces different music. These are fundamentally unreproducible register-exactly. Recommendation: flag in DB; candidate for exclusion (like Jay_Derrett).

**Detection:** To classify each of the 486 SIDs:
1. Detokenize the BASIC program (the recon transcript has a working detokenizer).
2. Search the text for `RND(0)` (token sequence: $88=RND, $28='(', $30='0', $29=')'  or numeric 0).
3. Search for `RND(-TI)` or `RND(-` pattern.
4. Search for `PEEK($DC04)` or `PEEK(56324)` or similar CIA timer PEEK patterns.
5. All others: deterministic or emulator-deterministic.

---

## 8. Sources

- pagetable.com C64 BASIC/KERNAL ROM disassembly: `https://www.pagetable.com/c64ref/c64disasm/`
- skoolkid sk6502 C64 ROM disassembly (individual routine pages): `https://skoolkid.github.io/sk6502/c64rom/`
- C64-Wiki: CHRGET, BASIC-ROM, FOR, RND, Jiffy Clock, CLR, GET, TIME, Zeropage, Interrupt, Variable: `https://www.c64-wiki.com/wiki/`
- Lars Gregori "C64 BASIC — How I fixed RND" (RND implementation + seed details): `https://www.larsgregori.de/2020/05/24/c64-basic-how-i-fixed-rnd/`
- emudev.de CIA timers article: `https://emudev.de/q00-c64/cias-timers-keyboard-and-more/`
- Commodore 64 memory map: `https://sta.c64.org/cbm64mem.html`
- scruss/bench64 (BASIC performance benchmark): `https://github.com/scruss/bench64`
- Bumbershoot Software C64 BASIC performance tuning: `https://bumbershootsoft.wordpress.com/2017/09/09/c64-basic-performance-tuning/`
- microheaven.com fast C64 BASIC tips: `https://www.microheaven.com/FastC64Basic/tips.html`
- libsidplayfp psiddrv.cpp (BASIC flag handling): `https://github.com/kode54/sidplay-residfp/blob/master/libsidplayfp/src/psiddrv.cpp`
- Lemon64 forum threads: system IRQ overhead, keyboard buffer mechanics, delay loop timing
- SID file format (RSID/BASIC flag): `https://ist.uwaterloo.ca/~schepers/formats/SIDPLAY.TXT`
- KERNAL IRQ handler ($EA31): `https://skoolkid.github.io/sk6502/c64rom/asm/EA31.html`
- RND function ($E097): `https://skoolkid.github.io/sk6502/c64rom/asm/E097.html`
- UDTIM/bump-clock ($F69B): `https://skoolkid.github.io/sk6502/c64rom/asm/F69B.html`

---

## Leads to Follow

1. **Corpus survey for RND(0) usage:** Detokenize all 486 SIDs and grep for `RND(0)` / `RND(-TI)` / `PEEK($DC04)` patterns to quantify Class A/B/C split. A detokenizer is already proven in the recon transcript — write a batch scanner.

2. **Verify sidplayfp cold-start state more carefully:** Confirm that psiddrv.cpp's "power-on pattern copy" includes the RND seed bytes at $8B–$8F. If psiddrv.cpp only copies $0000–$00FF or similar, the seed might not be reset → first run's residual RND state leaks into the emulated program. Inspect the source carefully at the `fillRam` + "power-on pattern" calls.

3. **Verify siddump --force-rsid + ROM path:** Once ROM images are available (Cluster 5 finding), test `siddump --writelog --force-rsid` on an Ahoy-style DATA/READ tune, capture its write stream, and confirm it is identical across two runs. This empirically validates the "deterministic Class A" hypothesis.

4. **Cycle count measurement:** Use `siddump --pc-trace` on a DATA/READ tune to measure the actual cycles between successive POKE writes. This gives the real tempo granularity and confirms the FOR/NEXT busy-wait model. The cycle trace also reveals if CIA IRQs are actually firing during BASIC execution (which they should be, updating TI).

5. **Keyboard buffer state during GET:** Confirm that sidplayfp never injects keyboard events during BASIC program emulation (keyboard buffer $0277–$0280 stays empty). This is the "no key pressed" assumption behind the GET determinism claim. Check the libsidplayfp source for any keyboard event injection.

6. **The $030C subtune mechanism:** Verify exactly how sidplayfp handles multi-subtune BASIC tunes — does it write the subtune number to $030C before BASIC starts, and does the BASIC program read $030C to select a melody? This affects corpus sizing (how many of the 486 are multi-subtune?).

7. **Color RAM / uninitialized RAM reads:** If any tunes do `PEEK($D800+N)` for melody, the "uninitialized" content matters. Confirm what sidplayfp's psiddrv.cpp sets for color RAM ($D800–$DBFF) at startup — if it's zeroed, the PEEK returns 0 deterministically.

8. **M=57272 pattern (ROM-reading tunes):** The Two Lines of Code tune reads from $DFB8 (I/O expansion area 2) initially, then sweeps into KERNAL ROM ($E000+). Confirm what sidplayfp returns for PEEK($DFB8) — likely $FF or 0. The KERNAL ROM bytes that form the actual melody are ROM-deterministic. Test empirically.

9. **FOR/NEXT empty loop cycle count verification:** Time `FOR I=1 TO 1000:NEXT` on sidplayfp by noting the cycle count between the BASIC init and a subsequent SID write. This gives the precise cycles-per-iteration for validation.
