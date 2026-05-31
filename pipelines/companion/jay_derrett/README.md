# Companion / Jay_Derrett engine

The "Companion/Jay_Derrett" engine is a sibling of `bowden_canonical`
in HVSC's sidid classification but shares no byte-level layout with
it. Where bowden uses a fixed orderlist + indexed pattern lookup, this
engine uses a **pointer-walking instruction stream** with embedded
control commands (`$Bx`/`$Cx`/`$Dx`/`$Ex`).

20 SIDs in HVSC #84 carry this classification (HVSC `engine ==
'Companion/Jay_Derrett'`):

```
DEMOS:                  -
GAMES:                  -
MUSICIANS/C/Clever_Music: Blade_Runner, Shao-Lins_Road,
                          Soundwave_Tubular_Bells, Space_Doubt
MUSICIANS/D/Derrett_Jay:  Counterforce, Death_or_Glory, Destruct,
                          Discovery, Dracula, Equalizer, Jetboys,
                          Lifeforce, Mandroid, Ninja_Hamster, Osmium,
                          Road_Warrior, Spindizzy_USA_Version, Sqij,
                          Stratton, Thundercross, Traxxion,
                          Trigger_Happy, Vengeance, ZIP
MUSICIANS/R/Raeburn_Gavin: Gun_Runner
```

(plus a 26th, `Counterforce.sid` — 2 subtunes — listed under
Derrett_Jay/.)

The canonical RE was done on **Ninja_Hamster.sid** (load $C000,
init $C57A, play $C452, 2.7 KB, 1 subtune — smallest + cleanest layout
in the family). The annotated disassembly lives at
`pipelines/companion/jay_derrett/disassembly_ninja_hamster.s`.

## Dispatch shapes across the 20 SIDs

Scanning the first 6 bytes at `play_addr`:

| shape | count | first 6 bytes | example |
|---|---|---|---|
| **Ninja_Hamster** | 8 | `INC abs / DEC abs / BEQ +3 / JMP abs` | Ninja_Hamster, Jetboys, Mandroid, Vengeance, ZIP, Counterforce, Destruct, Lifeforce |
| **Discovery** | 2 | `DEC abs / BEQ +3 / JMP abs` (no frame-ctr INC at top) | Discovery, Traxxion |
| **trampoline / wrapper** | 7 | first bytes are bank-switch (`$01` write) or `JSR` to a helper | Dracula, Equalizer, Death_or_Glory, Spindizzy, Sqij, Stratton, Trigger_Happy |
| **IRQ-driven** (play=$0000) | 3 | n/a — PSID stub follows the $0314/$0315 vector | Osmium, Road_Warrior, Thundercross |

The trampoline and IRQ shapes are dispatch shells — the actual engine
body is reached after following the wrapper / IRQ vector. The
downstream engine body in all 20 is the same shape as
Ninja_Hamster's, so an extract scanner that walks through the wrappers
should classify all 20 uniformly.

## Engine structure (Ninja_Hamster)

### Init ($C57A)

Sets up three orderlist pointers + per-voice duration counters + a
self-modifying register, then writes master VOL:

```
(V1 ptr) $C5C2/C5C3 ← $C000       ; voice 1 orderlist
(V2 ptr) $C5C4/C5C5 ← $C169       ; voice 2 orderlist
(V3 ptr) $C5C6/C5C7 ← $C342       ; voice 3 orderlist
self-mod $C4D3      ← $E0         ; $E0-range sub-jump base
tempo    $C5B9      ← $0A         ; current tempo counter
tempo    $C5BA      ← $0A         ; tempo reload value
$D418               ← $0F         ; master volume = full
v_durctr $C5B6/B7/B8 ← $01         ; per-voice ticks remaining
```

Three independent orderlist pointers, one per voice — distinct from
bowden's shared-orderlist + per-voice cursor.

### Play ($C452)

```
inc $C5C1                ; frame counter (vibrato/PWM phase source)
dec $C5B9                ; tempo counter
beq tick                 ; on underflow, run a "tick"
jmp $C6DD                ; else just run the per-frame effect block

tick:
  ; --- voice 1 ---
  lda $C5C2/C5C3 → $F2/$F3   ; load V1 pointer into zp
  ldx #0; stx $F4; stx $F5   ; voice idx=0, voice offset=0
  jsr proc_note ($C4BB)      ; advance V1 by one note/command
  sta $C5C2/C5C3 ← $F2/$F3   ; save updated V1 pointer

  ; --- voice 2 ---
  lda $C5C4/C5C5 → $F2/$F3
  inc $F4 (=1); lda #$18; sta $F5  ; voice 2 offset
  jsr proc_note
  sta $C5C4/C5C5

  ; --- voice 3 ---
  lda $C5C6/C5C7 → $F2/$F3
  inc $F4 (=2); asl $F5 (=$30)
  jsr proc_note
  sta $C5C6/C5C7

  lda $C5BA; sta $C5B9       ; reload tempo
  jmp $C6DD                  ; per-frame effects
```

The zp `$F2/$F3` is a transient orderlist pointer that gets loaded
per-voice from the engine-state copy, mutated by `proc_note` as it
consumes bytes, then written back. `$F4` is voice index (0/1/2);
`$F5` is a per-voice offset (0/$18/$30) into voice-state tables.

### proc_note ($C4BB)

The orderlist byte-stream interpreter. Each byte triggers a different
control-flow path:

```
$00..$7F  → NOTE byte. Look up freq + PWM + envelope for this pitch
            from instrument tables, write to V_FREQ_LO/HI/PW_LO/HI/
            CTRL/AD/SR. Advance pointer +1.

$80       → GATE OFF. Write a non-gate ctrl byte to V_CTRL. Advance.

$81       → SKIP. Just advance pointer +1. (Used for inter-note
            timing.)

$82 N     → SET DURATION. Reads next byte N and writes it to
            $C5B6+voice_idx (so this voice will idle N ticks before
            its next call).

$Bx       → TEMPO. Low nibble x sets new tempo: $C5BA ← x, then
            DEC. Advance pointer, recurse into proc_note.

$Cx       → MASTER VOL. Writes $D418 ← x. Advance, recurse.

$Dx       → INSTRUMENT CHANGE. Writes lo nibble to $C5BB+voice_idx,
            INCs it (the +1 is part of the engine quirk).
            Advance, recurse.

$E0..$EF  → SUB-JUMP / END. Reads from a table at $C5CB+y*2 (where
            y = lo nibble) to get a new orderlist pointer. Self-
            modifying counter at $C4D3 increments; resets to $E0
            at $E9. Used for pattern jumps and song-end.

other bit-7 → fall-through, treated as data.
```

### note-start ($C86E)

Triggered by a real note byte. Sets up the voice's modulation state
(freq slide, PWM, envelope) for the new note:

1. Note byte indexes into a 96-entry **freq table** at `$C5DD` (lo)
   and `$C65D` (hi).
2. Voice base offset (0/7/14) read from `$CAFB+voice_idx`. Determines
   `STA $D400+off` target.
3. **24-byte instrument program copy** — `LDY #$17; copy from
   instr_table[note] to voice_state[$C92D+offset]` via two pairs of
   self-modifying addresses (`$C88E/C88F` for source, `$C891/C892`
   for dest, set by indexing `$C8FB` and `$C91D` tables).
4. Initial freq written to V_FREQ_LO/HI.
5. CTRL byte built from `$C941+y` | `$C944+y` (waveform + control
   flags); written to V_CTRL. Cached at `$C5BE+voice_idx`.
6. AD / SR written to V_AD / V_SR.

The per-voice state at `$C92D+voice_off*24` carries fields for:
- bit-flags ($C92D+y bit 0=slide direction, bit 1=PWM mode, bit 2=PWM
  bound mode)
- current freq lo/hi ($C92E, $C92F)
- freq slide bounds ($C930-$C933)
- freq slide step ($C934, $C935)
- PWM current ($C937), bound ($C938)
- PWM step ($C939)
- PWM mode flag ($C93B)
- bidirectional PWM state ($C93C)
- ctrl byte ($C941)
- AD ($C942), SR ($C943)
- gate-off ctrl ($C944)
- high-octave freq lo/hi ($C945, $C946) — for arpeggio?

(Field assignments inferred from per-frame block; not all confirmed.)

### Per-frame block ($C6DD)

Runs on every play() call (whether tick or not). For each voice
(0,1,2):
1. Pick voice base addr from `$CAFB+voice_idx` (Y).
2. Pick voice-state base offset from `$C86B+voice_idx` (the offset
   into the $C92D table — different from voice index).
3. Apply per-voice modulation:
   - **Freq slide**: ADC/SBC the step into current freq, compare
     against bound; if bound crossed, either swap to other-direction
     bound (bidirectional) or zero the step (one-shot).
   - **PWM**: similar add/sub against bound; bidirectional flips a
     state byte.
   - **Bound-crossing arp**: when first bound crossed, swaps to
     the "high" freq variant (`$C945/$C946`).

Writes the updated V_FREQ_LO/HI/PW_LO/HI and CTRL back to SID.

## Open / unverified

- **Freq table contents** — the `$C5DD` / `$C65D` byte tables are not
  yet dumped. Expected to be PAL-ish but possibly hand-tuned (Hubbard
  '85 tradition).
- **Instrument programs** — the 24-byte blocks have ~20 fields; only
  ~10 are interpreted by the per-frame block in the current
  disassembly. The remaining fields need a finer trace.
- **`$E0` sub-jump table** at `$C5CB` — used for pattern jumps and
  song-end. The self-modifying `$C4D3` counter says "after the 9th
  $Ex call, reset and zero some flags." Needs end-of-song RE.
- **CTRL byte semantics** — `$C941` and `$C944` likely store
  "gate-on ctrl" and "gate-off ctrl" but the precise composition with
  the engine's frame-counter-driven gate cycle isn't fully traced.
- **Trampoline / IRQ shells** — 10 of 20 SIDs use a dispatch wrapper
  (bank-switch / JSR-helper / `play_addr=$0000` IRQ install). The
  scanner has to peel these layers off before pattern-matching the
  canonical play loop.

## Differences from `bowden_canonical`

| aspect | bowden_canonical | jay_derrett |
|---|---|---|
| orderlist | shared, indexed by `v_pos` | per-voice independent pointers |
| voice scan | `LDX abs / INC abs / LDY abs,X / LDX # / JSR` | `LDA abs / STA zp / LDA abs / STA zp / JSR / STA abs / STA abs` |
| pattern bytes | pitch byte only (5-byte timbre lookup is global) | pitch byte + embedded `$Bx`/`$Cx`/`$Dx`/`$Ex` commands |
| instrument | locked 5-byte timbre per voice | 24-byte instrument program per voice |
| modulation | none (locked timbre) | freq slide + PWM (uni/bi-directional) + bound-crossing arp |
| song-end | `$FF` orderlist terminator | `$E0..$EF` sub-jump with end-counter |
| voice disable | JSR → BIT patching (per Melonmania sub 1) | unknown — needs RE |

Significantly more complex than bowden. Closer in scope to a
Hubbard-'85-class engine.

## Recommended migration plan

1. **Scanner** (`extract/engine_model.py`): ✓ DONE.
   `load_state_from_sid` finds the play loop entry, peels a few
   trampoline shapes (bare JMP, bank-switch + JSR, conditional JMP),
   pattern-matches the 3 per-voice setup blocks (`LDA abs / STA zp`
   ptr-load bookend + `JSR proc_note` + `LDA zp / STA abs` write-back
   bookend), enforces shared proc_note across voices, and returns the
   engine's structural addresses. Walks by 6502 instruction length
   (not by byte) so STX/LDA operand bytes can't be mistaken for $20
   JSR opcodes. Coverage:

   | shape | count | scanner |
   |---|---:|:---:|
   | direct play (Ninja_Hamster + Discovery + inline-extra-LDA Equalizer) | 11 | ✓ |
   | trampoline-wrapped (Dracula bank-switch + Sqij conditional + Blade_Runner + Death_or_Glory + Spindizzy + Soundwave_Tubular_Bells + Space_Doubt) | 7 | ✓ |
   | KERNAL-IRQ (`play_addr=$0000`) | 3 | ✗ |
   | runtime-installed indirect JMP (Road_Warrior / Stratton / Shao-Lins_Road / Gun_Runner) | 4 | ✗ |

   Net: **18/25** classify with the static scanner. The 7 remaining
   all need init code to run (in py65 or sidplayfp) before we can
   read the dispatch state — KERNAL IRQ vector at $0314/$0315 or
   runtime-patched JMP targets in zero page / data ROM.

2. **Init emulator** (next session): run init through py65, capture
   the resolved play vector for the IRQ + indirect-JMP cases. Should
   recover the remaining 7.

3. **Engine data extraction**: instrument programs (24 bytes × N
   instruments), freq tables, $E0 sub-jump targets.

4. **USF representation**: per-voice orderlist as a sequence of
   command-byte rows. Note rows carry pitch + instrument ref; control
   rows carry `tempo=N`/`vol=N`/`instr=N`/`pattern_jump=N`/`song_end`.
   Likely needs a new pattern_encoding mode in the composer ("cmd-stream"
   variant — clever_music has a similar shape with `$Bx`/`$Cx`/`$Dx`/`$Ex`
   commands today, may be reusable as a starting point).

5. **Codegen**: new `_emit_jay_derrett_*` family in `composer.py`, or
   parameterize the existing `_emit_companion_*` further.

6. **Verification**: cycle-strict `compare_instruction_stream`, same
   as bowden_canonical.

Hardest piece: the instrument program format. Worth a separate phase
of RE before starting the extract.

## Skill reuse

This is the second-engine-family migration done as a "research +
docs first, then build" split. Same pattern as `migrate-hubbard-engine`
but for Companion-style strains. After two more such migrations a
sibling skill `migrate-companion-strain` might be worth distilling.
