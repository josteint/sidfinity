---
name: project-jay-derrett
description: "Migration of Companion/Jay_Derrett (20 SIDs on disk in HVSC #84; earlier count of 25 included filenames not in the collection). 15/20 byte-exact in tools/regression.py: 6 Cluster A + 3 Cluster B PSID + 1 Cluster C (Discovery) + 3 RSID IRQ (Osmium, Thundercross, Trigger_Happy via py65 IRQ-vector capture) + 2 Type B B1 (Equalizer, Death_or_Glory). Remaining 5: Sqij (B4 dual dur counter), Dracula (B1 variant with external subroutines at $1FB9/$1FA6), Spindizzy_USA_Version, Road_Warrior (multi-engine), Traxxion (Cluster C variant — existing sidfinity is 137/4382 partial)."
metadata: 
  node_type: memory
  type: project
  originSessionId: ce060f8a-e40f-4b55-9551-2d4fc0bb3028
---

# Companion/Jay_Derrett migration

**IMPORTANT UPDATE (current session):** The earlier "aperiodic by design" exclusion of 15 Type A SIDs was **WRONG** and has been REVERTED. Investigation triggered by the user noticing that Soundwave_Tubular_Bells (one of the 10 not-yet-classified) audibly sounds like a standard orderlist+patterns engine.

Inspection of V1 pattern data at $0801 for Tubular_Bells revealed the classic Mike Oldfield motif in standard Jay_Derrett byte format:

```
TEMPO_6 / INST_0 / NOTE / SKIP / NOTE / SKIP / ... / SUBJUMP_0 / motif-repeat / SUBJUMP_3 / ...
```

This is a normal orderlist with SUBJUMP commands branching through the sub-jump table — exactly the kind of structure the existing companion-strain composers handle. Not aperiodic.

What had been measured: voice pointers don't simultaneously realign in HVSC songlength. What this actually means: the song progresses through MULTIPLE sub-jump-table entries before completing a full cycle. HVSC songlength is one cycle (or a fragment); voices don't realign within it because the song is genuinely longer than HVSC's chosen cutoff (similar to e.g. C64ME).

ALL 15 previously-excluded Jay_Derrett entries removed from `tools/excluded_sids.json` (current session). Total Jay_Derrett unmigrated: 25/25 again. Migration to be planned as a standard orderlist+patterns composer effort.

25 SIDs classified as Companion/Jay_Derrett in HVSC #84. The
canonical RE is on Ninja_Hamster.sid (smallest, cleanest layout).
Engine code shape varies by tune but all share the same pointer-
walking byte-stream interpreter (proc_note) + per-frame modulation
block. Full notes in `pipelines/companion/jay_derrett/README.md` and
annotated disassembly in `disassembly_ninja_hamster.s`.

## Current state — extract side done

**Scanner: 25/25.** `load_state_from_sid` peels through direct play,
static trampolines (3 layers), init-emulation-resolved indirect JMP,
KERNAL IRQ vector, and subtune dispatchers (Gun_Runner). Returns
per-voice ptr_addrs + initial_ptr + zp + structural addresses.

**Engine-data scanners** (all dataflow, no heuristics — see
[[feedback_dataflow_over_heuristics]]):
- `find_freq_tables` — 25/25
- `find_sub_jump_table` — 25/25
- `find_instrument_base_table` — 15/25 (the 10 that fail are Type B
  shape — inline instrument data instead of indexed table)

**Type A/B split:** 15 SIDs have the Ninja_Hamster-shape indexed
instrument table (Type A). 10 use a different (TBD) inline layout
(Type B). Migration focuses on Type A first.

**TYPE_A list:** Counterforce, Destruct, Discovery, Jetboys,
Lifeforce, Mandroid, Ninja_Hamster, Osmium, Road_Warrior, Stratton,
Thundercross, Traxxion, Trigger_Happy, Vengeance, ZIP.

## Built this session (2026-05-31)

1. **`extract/orderlist.py`** — decodes a jay_derrett byte stream
   into typed Rows. Vocabulary:
   - `$00..$7F` → Note(pitch_byte = octave<<4 | semitone)
   - `$80` → CmdGateOff
   - `$81` → CmdSkip (extends preceding row's duration in higher
     layers, à la clever_music)
   - `$82 N` → CmdSetDuration (2-byte; N is operand)
   - `$Bx` / `$Cx` / `$Dx` → CmdSetTempo / CmdSetVol /
     CmdSetInstrument (the engine INCs the $Dx value — index +1
     quirk)
   - `$E0..$E9` → CmdPatternJump — only fires when byte equals the
     engine's self-mod counter at proc_note+$18
   - Static `decode_voice_orderlist()` walks until first `$Ex`;
     covers "pat 0" only. Full coverage requires runtime simulation
     (the active `$Ex` boundary depends on runtime counter state).

2. **`extract/engine_model._run_play_capture()`** — runs the engine
   in py65 for N frames, tracks each voice's `ptr_addr` value per
   frame. Returns per-voice ptr trails + final memory + counter
   trail. KEY GOTCHAS:
   - Do NOT `_peel_irq_handler` for runtime entry. The peel follows
     the first JSR/JMP target, which for jay_derrett is the
     tempo-counter-non-zero "frame-skip" branch (skips proc_note,
     runs only per-frame block). Use the full IRQ entry at
     `play_real`.
   - IRQ-driven SIDs (Osmium, Thundercross, Trigger_Happy) end
     their handler with `JMP $EA81` (KERNAL exit) which pulls a
     6-byte IRQ stack frame our JSR doesn't provide. Patch
     `4C 81 EA` → `60 EA EA` (RTS + 2 NOPs) in the simulator's mem
     copy before running.
   - Halts early on counter-wrap (song-loop closure) when the byte
     at proc_note+$18 (the self-mod CMP operand) decreases past its
     observed max.

3. **`extract/dump_type_a.py`** + **`_extracted/<NAME>.json`** —
   15/15 Type A SIDs dumped to structured JSON. Each record carries:
   - PSID meta (title/author/flags/start_song/speed)
   - Engine structural addresses (load/init/play/proc_note/loop_entry)
   - Per-voice ptr_addr + initial_ptr + zp
   - Self-mod counter address + initial value
   - Freq table (lo + hi, 128 bytes each)
   - $E0 sub-jump table (20 bytes — 10 entries × 2)
   - Instrument programs (raw 24-byte each — 18..20 per SID)
   - Per-voice captured byte sequence (200..1041 bytes, the full
     span from min..max ptr the play-capture observed)
   - Play-capture stats (n_frames, counter_max, loop_detected)

   11/15 hit ✓loop closure cleanly. 4 ran to the 15k cap because
   the counter-address default (proc_note+$18) doesn't match their
   variant — but full per-voice byte coverage was captured anyway.

## What's done (this session, 2026-06-01)

**USF schema design** — solved by the principled-Instrument refactor
(see [[project_principled_instrument_refactor]]). FreqSlideConfig +
IncBy2Config + envelope.release_ctrl + PwmConfig.phase1_* fields
landed in the schema (Phase 1-3 of the refactor). jay_derrett's
24-byte instrument programs decompose cleanly into these typed fields.

**`extract/instrument.py`** — decode_instrument() decodes 24-byte
program into typed Instrument (waveform/adsr/pwm/freq_slide_config/
envelope.release_ctrl). Maps the 21 read bytes; drops 3 padding
bytes ($09, $0D, $13). Three freq-slide modes derived from bit-flags
(one_shot_halt / one_shot_swap / bidirectional).

**`extract/to_usf.py`** — build_usf() consumes _extracted/<NAME>.json
dumps, walks per-voice captured byte streams via the row vocabulary:
  - $00..$7F → Note(pitch, dur=1)
  - $80 → rest; $81 → fold +1 into prev
  - $82 N → rest(dur=1+N, set_dur=$NN fx flag)
  - $Bx/$Cx → tempo=N / vol=N flags
  - $Dx → instr=i{N+1} (engine INC quirk)
  - $Ex → section_end=N flag
Each voice = 1 Pattern looping (orderlist 1 loop@0). Freq table inlined.

**Grammar additions**: section_end=N + set_dur=$NN fx-flag tokens
(additive — Hubbard 71 + Companion 35 stay green).

**Result**: 15/15 Type A USFs written to hvsc84/MUSICIANS/D/Derrett_Jay/.
All parse + validate + round-trip cleanly.

**Soft-fallbacks in the instrument decoder**:
  - Counterforce's 31-byte programs are pad/truncated to 24 (extras
    not RE'd yet; might lose some modulation behavior).
  - USF inst id = engine table index directly (not +1) to match the
    $Dx-then-INC engine quirk.

## What's still pending

1. **Composer codegen for jay_derrett — design problem first.**

   The round-trip verifier (`extract/verify_extract.py`) confirms
   15/15 USFs reproduce the **memory-range bytes** captured by
   play-capture (`mem[min_ptr : max_ptr+2]`). BUT this is the
   linear-memory slice, not the **execution sequence** the engine
   actually plays.

   The engine's `$Ex` self-mod counter creates non-linear execution
   flow:
     - Most `$Ex` bytes are SKIPPED (counter doesn't match) → ptr
       advances linearly through them.
     - Some `$Ex` bytes MATCH and fire sub-jumps → ptr jumps to a
       new sub-pattern address in the same voice's stream.

   The captured byte stream includes ALL bytes in the visited range
   (including bytes the engine skipped past linearly), but the
   execution ORDER (which sub-pattern after which) lives in the
   sub-jump table — which we intentionally dropped from USF per Q1's
   principled design.

   For composer codegen to produce matching per-frame SID writes,
   the engine it emits must reproduce the SAME execution sequence
   the original played — not just the same memory bytes.

   Three approaches (decision needed for Phase 5):

   **A. Carry the sub-jump-target per `section_end` row.** Extend the
   `section_end=N` fx flag to `section_end=N target=N_rows_into_stream`
   or similar. Composer's engine uses this for explicit jumps.
   Trade-off: positional info in USF (engine-mechanism-leak shape).

   **B. Re-record per-frame trail + emit only the executed sequence.**
   Extend play-capture to dump the ORDERED byte sequence (one byte
   per frame the engine processed). USF's orderlist is then the
   played sequence; composer's engine plays linearly through it.
   Trade-off: USF becomes a runtime trace, not the source bytes.
   Loses round-trip with the original SID's memory layout.

   **C. Composer runs runtime simulation at codegen time.**
   Composer takes the USF + emits a 6502 engine + RUNS play-capture
   to figure out the right sub-jump table layout, iterates until SID
   writes match. Self-tuning composer. Trade-off: codegen becomes a
   solver, brittle, slow.

   Option B is cleanest principled (matches what the engine ACTUALLY
   plays, not what's in memory). Suggest re-extracting USFs with the
   ordered play sequence per voice.

   **Realistically, Phase 5 needs this design decision before any
   composer code goes in.** Ask user.

2. **Byte-exact verify** — Per-tune debug until all 15 pass
   `verify_all` (per-frame snapshot match). Roll into
   `tools/regression.py`.

3. **Counterforce 31-byte program RE** — disassemble the longer
   layout to map the extra 7 bytes' semantics.

4. **Type B SIDs (10 remaining)** — find_instrument_base_table
   doesn't work for these; they use inline instrument data instead
   of an indexed table. Out of scope for now.

5. **Instrument decoder byte-fidelity gaps** — 217/286 instruments
   don't byte-exact round-trip (mostly $0E PW direction value
   preserved as boolean; bit-flags on slide-inactive instruments).
   These don't affect SID writes per the per-frame-snapshot principle
   but are worth fixing for representation completeness.

2. **Byte-exact verify** — Per-tune debug until all 15 pass
   `verify_all` (per-frame snapshot match). Roll into
   `tools/regression.py`.

3. **Counterforce 31-byte program RE** — disassemble the longer
   layout to map the extra 7 bytes' semantics.

4. **Type B SIDs (10 remaining)** — find_instrument_base_table
   doesn't work for these; they use inline instrument data instead
   of an indexed table. Out of scope for now.

## Pending fix: counter-address detection

The hardcoded `counter_addr = proc_note + $18` is wrong for 4 of 15
Type A SIDs (Jetboys, Osmium, Thundercross, Traxxion). The correct
slot is the `CMP #imm` operand inside the `$Ex` dispatch path of
proc_note (after the `AND #$F0; CMP #$E0; BNE skip; LDA ($zp),y;
CMP #$E0` chain — the second CMP is the self-mod one). A proper
scanner would walk proc_note from its start, find the second
`CMP #imm` after the `AND #$F0` filter, return the operand byte's
address. Add to `find_*` family in `engine_model.py`.

(Not blocking — capture still works at the 15k cap; just doesn't
auto-stop on loop closure for those 4.)

## Engine RE summary — Ninja_Hamster canonical (2026-06-02)

The Ninja_Hamster engine occupies $C000-$CAFF (load = $C000,
init = $C57A, play = $C452, 2816 bytes — most of which is data).
Code regions:

| Range | Role |
|-------|------|
| $C452-$C5B5 | play + proc_note + init |
| $C6DD-$C86A | per-frame modulation (slide + PWM) |
| $C86E-$C8FC | instrument-program loader (sub_C86E) |
| All other bytes | data tables + per-voice runtime state |

### Engine state addresses (Ninja_Hamster, parametric for other instances)

| Addr | Role |
|------|------|
| $C5B6/B7/B8 | duration counter per voice (V1/V2/V3) |
| $C5B9 | tempo countdown |
| $C5BA | tempo reload |
| $C5BB-BD | current instrument per voice |
| $C5BE-C0 | CTRL byte per voice (modified by GATE_OFF $80) |
| $C5C1 | frame counter (INC'd every play call) |
| $C5C2/C3, C4/C5, C6/C7 | per-voice pattern ptr (lo+hi) |
| $C5CB-DA | sub-jump table (10 × 2-byte addrs) |
| $C5DD,X (X=inst×$10) | instrument freq-slide-lo table base |
| $C65D,X | instrument freq-slide-hi table base |
| $C4D3 | self-mod CMP counter operand ($E0..$E9, wraps) |
| $C92D-$C944,y (y=inst_y∈{$00,$1A,$34}) | per-voice runtime state copy of 24-byte program |
| $C941/C944,y | CTRL slots (write-then-restore on GATE_OFF) |
| $C945/C946,y | note-freq override (when bit-flag) |
| $CAFB,X | voice-to-SID-offset (0/7/14) |
| $CAFE,X | per-voice PWM sub-state |
| $CB01,X | per-voice PWM low-byte accumulator |
| $CB04 | modulation-loop voice index |

### Per-frame flow

```
play:                                    ($C452)
  INC frame_counter                      ($C5C1)
  DEC tempo_counter                      ($C5B9)
  BNE skip_proc_note                     → JMP modulation
  // tempo expired — process all 3 voices
  for v in (0, 1, 2):
    set zp = voice_ptr[v]                ($C5C2+v*2 → $F2/$F3)
    set $F4 = v*2                        (X stride: voice-to-state offset)
    set $F5 = v*$1A                      (Y stride: per-voice 24-byte slab in $C92D)
    JSR proc_note ($C4BB)
    save zp back to voice_ptr[v]
  reload tempo_counter from tempo_reload
modulation: ($C6DD)
  for v in (0, 1, 2):
    set $CB04 = v*2
    JSR sub_C6EE  (slide + PWM update for voice v)
```

`proc_note` reads the next pattern byte and dispatches by high
nibble / specific value:

| Byte | Action |
|------|--------|
| $00-$7F | NOTE: write CTRL ($C5BE,X → $D404,Y), then JSR instrument loader at $C86E with A=note, advance ptr |
| $80 | GATE OFF: write $C941,y CTRL to $C944,y (clears gate bit), advance ptr |
| $81 | SKIP: advance ptr, recurse |
| $82 N | SET DURATION: store N in $C5B6,X (duration counter), advance ptr twice |
| $Bx | SET TEMPO: store low nibble in tempo_reload ($C5BA), DEC it, advance ptr |
| $Cx | SET MASTER VOL: store low nibble in $D418, advance ptr |
| $Dx | SET INSTRUMENT: store low nibble in $C5BB,X then INC (so on-disk N → engine N+1), advance ptr |
| $E0-$EF (high nibble) | PATTERN_JUMP: check second CMP at proc_note+$18 (self-mod counter, starts $E0) — if byte matches, jump zp to sub-jump-table[low nibble], INC counter; else SKIP. After $E9 matches, reset counter to $E0 + clear two song-loop counters ($C975/$C978) |

### Instrument loader sub_C86E

```
A = note byte
Y = note * 2 → ptr to freq table entry at $C8FB,y  → $C92E,y (note freq)
                                                  → $C92F,y
X = inst * 2 → ptr to program at $C91D,x  → copies 24 bytes from
   [program_base] into $C92D,y (per-voice runtime state)
Y = $00..$17 ← reads bytes from ($C92D+y, runtime state)
Apply program: writes ADSR ($D405/$D406), set CTRL slot,
freq-slide deltas, PWM init, etc.
```

The 24-byte program layout (from inst[0]):
```
$00-$08  freq-slide lo/hi pairs (PWM phase 1/2 deltas, bounds)
$09       ?(usually 0/1)
$0A       AD value
$0B       SR value
$0C-$0D   ?
$0E-$0F   ?  (PW initial?)
$10-$11   ?
$12-$13   ?
$14       CTRL byte (waveform + gate)
$15-$17   ?
```

(Decoded by `extract/instrument.py` into typed Instrument; bytes
not fully accounted for — 217/286 don't byte-exact round-trip per
earlier notes.)

### Per-frame modulation (sub_C6EE)

Reads `$C92D,y` flag byte:
- bit 0: slide direction (BCS at $C73E)
- bit 1: slide swap mode
- bit 2: slide one-shot vs continuous

Two-stage PWM:
- `$CAFE,X` = phase (0 or 1)
- Phase 0: accumulate `$C939,y` into `$CB01,X` + carry into `$C937,y`; compare to `$C938,y`; if reached, advance phase
- Phase 1: subtract `$C93F,y` from `$CB01,X`; compare to `$C93D,y`; loop back to phase 0

### Engine variants (the 5 dispatch shapes)

Same proc_note core, different play-entry wrappers:

1. **Direct play** (Ninja_Hamster + 7 more) — play at $C452, simple loop
2. **Discovery 2-trampoline** (2 SIDs) — play_entry indirects through trampoline pairs
3. **Trampoline** (7 SIDs) — single trampoline relocation
4. **IRQ-driven** (3 SIDs: Osmium, Thundercross, Trigger_Happy) — play ends `JMP $EA81` (KERNAL exit). Capture needs patch `4C 81 EA → 60 EA EA`.
5. **Gun_Runner multi-subtune dispatcher** (Gun_Runner only) — dispatches by subtune index

## Multi-session principled migration plan

**Phase 1 (DONE 2026-06-02, commit 100eb22)** — Python step-by-step emulator
- `pipelines/companion/jay_derrett/emulator.py` — `JayDerrettEmulator` class
- Byte-exact vs `siddump --writelog` for Ninja_Hamster over 15,000+ frames
  (300s = full song + multiple loops, 222,810 SID writes)
- Test: `pipelines/companion/jay_derrett/tests/test_emulator.py`
- Engine semantics covered: tempo, all proc_note dispatch types (NOTE,
  GATE_OFF, SKIP, SET_DUR, SET_TEMPO, SET_VOL, SET_INST, PATTERN_JUMP),
  self-mod counter wrap, instrument loader (sub_C86E), per-frame
  modulation (freq slide + 2-phase PWM)
- Includes libsidplayfp powerup RAM pattern (00 00 FF FF FF FF 00 00
  per 8-byte block, alternating per 16K bank) — load-bearing because
  orig reads $CB01 (= $FF in powerup) as initial PWM lo accumulator
- Parametric via `EngineParams` dataclass — Ninja_Hamster instance
  hard-coded; other Type A instances add by varying addresses

**Phase 2 (DONE 2026-06-02, commit 6b5a4ed)** — clean xa65 composer
- `pipelines/companion/jay_derrett/build.py` — emit_asm() + build_ninja_hamster_sid()
- Engine logic rewritten cleanly (no verbatim engine bytes); data
  tables inlined from extracted SID body
- Two-pass assembly: pass 1 finds voice_pattern label addresses, then
  sub_jump_table entries get remapped to new locations, pass 2 produces
  final binary
- Test: `tests/test_build.py` — `is_full` match vs orig Ninja_Hamster
  at the regression-standard 6s window
- Default load = $1000 (relocated from orig $C000)
- Two non-obvious engine-mechanism leaks preserved as explicit init writes:
  1. V1 PWM lo accumulator init = $FF (orig relied on libsidplayfp
     powerup RAM at $CB01 = $FF)
  2. Self-mod counter wrap at $E9 clears voice 2 CTRL slots
     (voice_state+$14+$34 and +$17+$34); orig wrote to $C975 + $C978
     which happen to be those runtime state cells
  These should ideally lift into USF as explicit primings/effects in
  Phase 3.
- Bug along the way: `_assemble` label parser was whitespace-split
  but xa65 format is comma-separated ("name, 0xaddr, 0, 0xext"). Empty
  labels dict → bases [0,0,0] → bogus sub_jump_table with $00 hi bytes
  → $F3 zeroed when an $Ex dispatch fired. Spent half the session on
  this. Lesson: always inspect emitted asm + labels output when
  debugging assembler-emitted code.

**Phase 3 (IN PROGRESS — generic infra landed 2026-06-02)** — Parametrise for other Type A SIDs
- `build_sid(sid_path, params)` generic builder (works for any Type A)
- `params_from_extracted_json(json_path)` populates EngineParams from
  the scanner's JSON dumps
- `capture_init_state(sid_path, params)` runs orig init in py65 with
  libsidplayfp powerup RAM, captures key state cell values
- `try_all_type_a()` runs build + writelog-verify on all 15 Type A SIDs
- Status as of session 2026-06-02:
  - PASS: 1/15 (Ninja_Hamster)
  - FAIL match=1-2 writes: 10/15 — diverge at first play frame
    because orig init pre-populates voice_state slabs at
    engine-specific addresses; my reb starts voice_state = $00
  - BUILD-ERR (StopIteration): 4/15 (Mandroid, Osmium, Thundercross,
    Trigger_Happy) — voice ptrs non-contiguous so the
    "next-boundary > start" pattern slicer falls off the end

### Phase 3 status after 2026-06-02 (two sessions)

**Status across 15 Type A SIDs:**
- PASS: 1 (Ninja_Hamster)
- match_all 9-25 writes: 3 (Discovery, Jetboys, Vengeance)
- match_all 1-2 writes: 8 (Counterforce, Destruct, Lifeforce,
  Mandroid, Road_Warrior, Stratton, Traxxion, ZIP)
- empty siddump output: 3 (Osmium, Thundercross, Trigger_Happy —
  IRQ-driven, play=$0000, need dispatch handling)

**Generic infrastructure landed:**
- `detect_voice_state_base` (scan instrument-loader copy loop)
- `detect_pwm_lo_accum_base` (scan modulation PW-lo write)
- `capture_voice_state_slabs` + `capture_cells_after_init`
  (run orig init via py65 with libsidplayfp powerup RAM)
- `voice_byte_ranges` parameter for non-contiguous voice patterns
- build_sid auto-wires all of the above

**Architectural blocker discovered:** Counterforce (and most other
Type A SIDs) use INTERLEAVED voice_state layout — V0/V1/V2 freq lo
at consecutive addresses N/N+1/N+2 (3 voices indexed by X = voice
idx into a single cell row). Ninja_Hamster uses SLAB layout — V0
occupies a 26-byte slab, then V1 in another slab, then V2.

The composer's emit_asm hardcodes slab layout (`voice_state+$01,Y`
where Y is voice stride 0/$1A/$34). Supporting interleaved variants
needs a parametric emit pass (per-engine voice_state slot offsets +
stride). That's a substantial refactor — voice_state has ~22 slots
that all need their offset detected.

### Recommended Phase 3 path forward (next sessions)

**Option A — Per-engine emit_asm variants.** Detect voice_state
layout (slab vs interleaved + per-slot offsets) per engine, emit
matching modulation/inst-load code. 3-5 sessions.

**Option B — Generic engine via captured-write replay.** Don't try to
mirror engine semantics; just dump orig's writelog into a sample
buffer and emit a sample-player. Loses USF-ability (engine becomes a
write trace, not musical content). Not principled.

**Option C — Pause Type A; do Type B first** (10 SIDs that use inline
instrument data; might be simpler architecturally despite the
unfamiliar layout). Then return to Type A with fresh perspective.

Option A is the principled path. Pre-RE: identify each engine's
voice_state slot offsets by scanning the modulation block — each
LDA $XXXX,Y / STA $D40X,X writes from a specific voice_state offset.
Catalogue per engine, then emit_asm becomes parametric.

### Variant taxonomy (profiled 2026-06-02 — `profile_variants.py`)

After scanning all 25 SIDs' binaries (modulation block + copy loop +
strides + dispatch), the FAMILY breaks into 4 distinct engine
variants. ALL Type A engines use SLAB layout (not interleaved — my
earlier hypothesis was wrong); they differ in slot offsets, program
size, stride, and dispatch shape.

**Cluster A — Ninja_Hamster shape (6 SIDs)**
- Signature: 24-byte program, stride 26, direct dispatch
- Slot offsets from mod_base: freq_lo=+1, freq_hi=+2, pw_hi=-13,
  off_freq_lo=-22 (i.e. at $0A and $18 from copy_dst since
  mod_base = copy_dst + $17 for these)
- SIDs: Jetboys, Lifeforce, Mandroid, Ninja_Hamster, Vengeance, ZIP
- **Status**: only Ninja_Hamster PASSES; others fail because
  composer uses copy_dst as voice_state_base, but Lifeforce/Mandroid/
  ZIP have copy_dst ≠ mod_base (copy lands at V2's slab; engine reads
  from mod_base which is +1 stride away).

**Cluster B — 15-byte program shape (7 SIDs)**
- Signature: 15-byte program, stride 26, mixed dispatch shapes
- Slot offsets: freq_lo=+1, freq_hi=+2, pw_hi=-20, off_freq_lo=-1
- DIFFERENT slot layout from Cluster A (different positions for
  pw_hi and off_freq_lo)
- SIDs: Counterforce, Destruct (direct), Osmium, Thundercross,
  Trigger_Happy (IRQ-driven, play=$0000), Road_Warrior (trampoline),
  Stratton (trampoline_indirect)
- Needs separate emit variant for this slot layout

**Cluster C — stride-24 variant (2 SIDs)**
- Signature: 24-byte program, stride 24, direct_no_inc (DEC first,
  no INC frame_counter)
- Slot offsets: freq_lo=+1, freq_hi=+2, pw_hi=+10 (different from A!)
- SIDs: Discovery, Traxxion
- Needs another emit variant

**Cluster TypeB — different engine entirely (10 SIDs)**
- No copy loop detected (no `B9 ?? ?? 99 LL HH 88 10 F7` pattern)
- Different inst loading mechanism, probably inline programs per row
- SIDs: Blade_Runner, Death_or_Glory, Dracula, Equalizer, Gun_Runner,
  Shao-Lins_Road, Soundwave_Tubular_Bells, Space_Doubt,
  Spindizzy_USA_Version, Sqij
- Full RE needed (separate from Type A composer work)

### Most-actionable principled plan

| Phase | SIDs | Effort | Status |
|-------|------|--------|--------|
| 3a | Cluster A (5 remaining) | 1 session | DONE (commit 83b248d): 3/6 PASS via mod_base detection + voice_state slab capture + PWM phase capture |
| 3a' | Cluster A residuals (3) | 1 session | DONE (commit 0b250dd): 6/6 PASS via two more quirks: set_dur_clears_v3 detector (fixes Vengeance/Lifeforce) + initial_frame_counter capture (fixes ZIP — pre-INC'd $53 times during init) |
| 3b | Cluster B (2 direct + 1 trampoline_ind) | 1 session | DONE (commit cbfc639): Counterforce, Destruct, Stratton PASS. Stratton's trampoline_indirect works through PSID dispatch with no special handling. |
| 3b' | Cluster B IRQ (3) | 1 session | DONE (commit 2b93049): Osmium/Thundercross/Trigger_Happy PASS via py65 capture (follows IRQ vector at $0314/$0315 after init — see project_chimera.md). New `capture_writes_via_py65()` in build.py. Reb ships as PSID with normal play_addr, captured via siddump. Comparison drops reb's 2 init $D418 writes (py65 capture starts post-init). |
| 3b'' | Cluster B multi-engine (1) | 1 session | TODO — Road_Warrior bundles TWO mod engines in one binary (like C64ME). Needs subtune-aware dispatch or per-subtune emit. |
| 3c | Cluster C Discovery (1) | 1 session | DONE (commit 16a2e66): Parametrized emit_asm over stride, has_off_slide, inc_frame_counter. detect_dur_counters_base via DEC $ABS,X pattern (Discovery's dur cells at vp-$0B not vp-12). Conditional off-slide write in inst loader (was clobbering V1's flag in Cluster C stride-24 layout). |
| 3c' | Traxxion (1) | 1-2 sessions | TODO — Cluster C variant with SHARED single-byte tempo counter (DEC $7F66 / BEQ proceed; uses ZP $FB/$FC for ptr, $FD/$FE for voice idx/stride; proc_note has no per-voice dur counter — pattern bytes encode their own duration). Distinct engine architecture; needs new emit_asm variant. |
| 4 | Type B (10) | 3-5 sessions | IN PROGRESS — RE done on Equalizer (canonical). Sub-clusters identified. emit_asm_type_b not yet written. |

Total: 9-11 sessions for full 25-SID coverage. **6/15 Type A DONE** (entire Cluster A: Jetboys, Lifeforce, Mandroid, NH, Vengeance, ZIP).

### Phase 3a tooling landed (commits 83b248d + 0b250dd)

- `detect_mod_base` — slide-update pattern scan, universal across
  slab variants
- `detect_pwm_phase_base` — phase cell detector via
  `BD LL HH D0 ??` (LDA voice-idx-indexed / BNE phase1)
- `_run_init_for_extract` — py65 init run with libsidplayfp powerup
  RAM, returns full RAM image. Crucial for engines (Mandroid) that
  copy pattern data from body to RAM during init.
- `detect_set_dur_clears_v3` — scans for engines whose SET DUR
  handler ALSO clears V3 CTRL slots (Jetboys/Lifeforce/Vengeance/ZIP
  do this; NH/Mandroid don't)
- EngineQuirks now carries 9 captured init-state fields: cur_inst,
  cur_ctrl, tempo, dur_counters, smc, master_vol, pwm_lo, pwm_phase,
  frame_counter. All auto-captured via `capture_cells_after_init`.

### Cluster B RE findings (Counterforce — for Phase 3b)

Cluster B is structurally a different engine from Cluster A. The
15-byte program has a different byte-semantic layout, AND the engine
code reads/writes slab slots at different offsets.

**Counterforce slab layout (24 bytes, indexed from copy_dst $1ED1):**

| Offset | Slot semantic |
|--------|---------------|
| $00 | flag (bit 0 controls off-slide; NH uses bit 7) |
| $01 | PW hi (NH has freq lo here) |
| $02 | phase 0 limit (NH has freq hi) |
| $03 | phase 0 lo delta (NH has slide_max_lo) |
| $04 | (unused?) |
| $05 | phase 0 direction flag |
| $06 | phase 1 direction flag |
| $07 | phase 1 max |
| $08 | phase 1 min |
| $09 | phase 1 lo delta |
| $0A | (?) |
| $0B | CTRL byte (NH has phase0 limit) |
| $0C | AD |
| $0D | SR |
| $0E | gate-off CTRL |
| $0F-$13 | (unused?) |
| $14 | off-slide freq lo (computed by inst loader from note byte) |
| $15 | off-slide freq hi |
| $16 | normal freq lo (computed from note+$10 — different note!) |
| $17 | normal freq hi |

**Key differences vs Cluster A (NH):**
1. PW hi at $01 (NH: $0A)
2. CTRL at $0B (NH: $14)
3. Off-slide freq at $14/$15 (NH: $18/$19)
4. Normal freq at $16/$17 (NH: $01/$02)
5. Bit 0 of flag controls off-slide path (NH: bit 7)
6. Normal freq stores note+$10 freq (octave shift); off-slide stores
   actual note freq — OPPOSITE assignment from NH
7. 15-byte inst program (vs NH's 24-byte) — different byte semantics

**Why this needs separate emit_asm_cluster_b:**

My current emit_asm hardcodes slot offsets. Runtime writes (slide-
update writes to voice_state+$01, PWM-update writes to voice_state+
$0A) go to specific cells. For Cluster B those cells have DIFFERENT
semantic data — can't be fixed by remapping captured slab values.

The principled solution is a parametric SlotLayout dataclass + two
profiles (CLUSTER_A, CLUSTER_B), with emit_asm dispatching by
profile. ~500 lines of new code; 2-3 sessions estimated.

**Cluster B SIDs (7 total):**
- Direct dispatch (2): Counterforce, Destruct
- IRQ dispatch (3): Osmium, Thundercross, Trigger_Happy
- Trampoline (1): Road_Warrior
- Trampoline_indirect (1): Stratton

All 7 share the same engine code shape; just different play-entry
wrappers. Once Cluster B's direct-dispatch emit works, IRQ/trampoline
wrappers should be straightforward additions.

### Key tooling for next session

- `pipelines/companion/jay_derrett/profile_variants.py` — prints
  per-SID slot layout + clusters
- `detect_mod_base(sid_path, params)` in build.py — finds modulation
  base via freq_lo source - 1. NOTE: heuristic for picking normal
  vs off-slide path is engine-specific (some engines have normal at
  LARGER source addr, others at SMALLER — need different cue).

### Key tactical fix for Phase 3a

The "normal-vs-off-slide STA $D400,X" identification needs a
universal cue. The cleanest: scan for the slide-update pattern
`B9 LL HH 18 79 ?? ?? 99 LL HH` (LDA / CLC / ADC / STA at SAME
address). The slide accumulator slot is the freq lo cell; mod_base
= that addr - 1. This works for ALL slab variants regardless of
which path is "first" in code order.

### Type B engine RE (Equalizer canonical) — 2026-06-02

Type B is a DIFFERENT engine from Type A — not just different slot
offsets. Key differences:

| Feature | Type A (NH-shape) | Type B (Equalizer-shape) |
|---------|-------------------|--------------------------|
| Modulation | Y-indexed slabs (stride $1A) | Per-voice unrolled subroutines |
| Inst program size | 24 bytes (5-byte for CF) | 5 bytes |
| Inst lookup | inst_id * 2 → 16-bit ptr table | inst_id * 5 → direct offset |
| Inst loader | Separate sub_C86E with copy loop | Inline in $Dx handler; writes AD/SR direct to SID |
| State cells | Slab at mod_base + Y_stride | Per-voice individual cells |
| PWM logic | 2-phase with limits | Simple ADD-until-limit + signed-delta oscillation |
| $Ex wrap | $E9 (NH) / $E6 (CF) | $E3 (only 3 sub-jump entries) |

**Shared with Type A:**
- proc_note byte vocabulary IDENTICAL ($Ex/$Dx/$80/$81/$82/$Bx/$Cx + NOTE)
- Per-voice dur counter decrement at proc_note entry
- DEC abs,X / BEQ proceed pattern

**Equalizer structure (canonical):**
- Init at $C86E sets voice ptrs at $C8AC..$C8B1 (V0/V1/V2 lo+hi)
- Play at $C6B4:
  1. JSR V1 mod sub ($C9E1)
  2. JSR V2 mod sub ($CA2C)
  3. JSR V3 mod sub ($CA6C)
  4. DEC tempo ($C8AA); if zero, process voices; else RTS
  5. For each voice: copy ptr to $FB/$FC, set $FD=voice_idx, $FE=sid_off
     (0/7/$E), self-mod some constants, JSR proc_note ($C76D)
  6. Save ptr back; reload tempo
- proc_note at $C76D: DEC dur,X / BEQ proc; dispatch on byte
- $Dx instrument handler: inst_id * 5 → index into 5-byte program;
  writes AD/SR direct to SID $D405/$D406 (via STA,X with X=sid_off)

**Type B sub-clusters (from architecture probe):**

| Cluster | Count | SIDs | Signature |
|---------|-------|------|-----------|
| B1: Equalizer-shape | 3 | Equalizer, Death_or_Glory, Dracula | Per-voice PWM unrolled subs, prog *5 indexing, DEC dur,X (1x) |
| B2: extended | 2 | Gun_Runner, Shao-Lins_Road | More PWM writes (multi-subtune?), prog *5 |
| B3: minimal | 3 | Blade_Runner, Space_Doubt, Spindizzy_USA_Version | No per-voice PWM unrolled, prog *5 |
| B4: distinct | 2 | Sqij (2x DEC,X), Soundwave_Tubular_Bells (no prog *5) | Likely separate engine sub-variants |

**Phase 4 plan (Type B):**
- Phase 4a (1 session): Write emit_asm_type_b for B1 cluster (Equalizer canonical). Validate Equalizer byte-exact.
- Phase 4b (1 session): Extend to Death_or_Glory + Dracula (same B1 sub-cluster).
- Phase 4c (1-2 sessions): B3 cluster (Blade_Runner, Space_Doubt, Spindizzy) — likely simpler variant of Equalizer (no PWM mod?).
- Phase 4d (1-2 sessions): B2 cluster (Gun_Runner multi-subtune, Shao-Lins_Road).
- Phase 4e (1-2 sessions): B4 cluster (Sqij dual-dur-counter, Tubular_Bells different inst format).

Total Type B: 5-8 sessions.

**Next session entry point**: write `pipelines/companion/jay_derrett/type_b.py`
with `emit_asm_type_b()` mirroring Equalizer's structure. Use Equalizer
as test case. Once Equalizer passes, extend to Death_or_Glory + Dracula.

**Phase 4 (2-3 sessions)** — Type B (10 remaining SIDs)
- Re-RE find_instrument_base_table for inline-instrument variant
- Migrate Type B composer variant
- Verify byte-exact

**Phase 5 (1 session)** — Gun_Runner multi-subtune
- Multi-subtune dispatcher composer
- Likely shares Phase 3 dispatch shapes for inner engine

**Total: 8-9 sessions for full 25-SID principled migration.**

### Pre-existing assets to leverage

- `extract/engine_model.py` — scanner 25/25 (voice ptrs, freq tables, sub-jump table, instrument table for Type A)
- `_extracted/<NAME>.json` — 15 Type A JSONs with full structural data
- `extract/orderlist.py` — byte-stream decoder
- `extract/instrument.py` — 24-byte program decoder (partial — 217/286 round-trip)
- `extract/to_usf.py` — 15 USFs written (not yet verified byte-exact)
- `extract/verify_extract.py` — round-trip checker
- `disassembly_ninja_hamster.s` — canonical annotated disassembly
- `README.md` — engine RE notes

### Decision pending — pattern-jump representation in USF

Three approaches discussed earlier:
- **A.** Carry sub-jump-target per `section_end` row (positional info in USF — engine-mechanism leak shape)
- **B.** Re-record per-frame trail + emit only executed sequence (loses round-trip with source bytes)
- **C.** Composer runs runtime simulation at codegen time (self-tuning composer)

Option B leans cleanest principled. Phase 1 (Python emulator) should produce both:
- The executed byte sequence (for Option B)
- The visited byte sequence + sub-jump-table mapping (for Option A)
- Then decide.
