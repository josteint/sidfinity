# Commodore 64 Music Examples — RE notes

**File:** `hvsc84/MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid` (Rob Hubbard, 1985)
**PSID:** load `$086D`, init `$087C`, play `$086D`. 15 subtunes. Body covers `$086D-$422A` (14782 bytes).
**sidid classification:** `Companion` (base — same fingerprint as Up_up_and_Away and Bowden's 1984 driver).

## Architecture

**Two engine families**, not five (early agent draft incorrectly counted five — see "byte pattern collapse" below).

- **Family A** — 14 of 15 subtunes (subs 0, 2, 3, 4-14). The same engine logic is instantiated 4 times physically: at `$0903`, `$1D8B`, `$2A23`, and `$33DB`. Subs 0/2/3 each occupy one of the first three instances solo. Subs 4-14 share the fourth instance (`$33DB`) via per-subtune dataset dispatch.
- **Family B** — sub 1 only, at `$1119`. Different opcodes from the very first instruction. A distinct engine.

This is consistent with the SID's title: a *Music Examples* compilation. Hubbard bundled 14 example tunes through his canonical engine plus 1 example using a different player technique.

## PSID-level dispatch

`init` patches 9 fixed locations with `RTS` or `NOP` (constant across all subtunes — feature-disable points) then patches the play loop's JSR target via per-subtune lookup tables at `$08D8` (hi) and `$08EC` (lo):

```
$08CA: TAX               ; X = subtune-derived index (see derivation below)
$08CB: LDA $08EC,X       ; → STA $0878 (play's JSR low byte)
$08D1: LDA $08D8,X       ; → STA $0879 (play's JSR high byte)
```

The X-index is *not* the raw subtune number. Init derivation (verified by py65):
- Subtune 0..3: `X = subtune + $0F`, reading table entries 15..18.
- Subtune 4..14: a separate path computes `X = $13`, reading entry 19 (all 11 high-subtunes share this slot).

**Real per-subtune dispatch** (verified by running `_run_init` and reading `$0878-$0879` after init):

| Subtune | Handler | Family | Notes |
|---|---|---|---|
| 0 | `$0903` | A | Own state at `$0A6E-$0AB4` |
| 1 | `$1119` | B | Distinct engine — only Family B instance |
| 2 | `$1D8B` | A | Own state at `$1F00+` |
| 3 | `$2A23` | A | Own state at `$2B80+` |
| 4-14 | `$33DB` | A | Shared engine; per-subtune dataset selected via the 11 small stubs at `$38A0..$4224` |

The per-subtune `$D403` (V1 PW hi) value is also set during init for subs 4-14 (sourced from `$35C5` data table indexed by subtune).

## Byte pattern collapse (Family A confirmation)

Compare the first 21 bytes of each handler:

| Handler | Bytes |
|---|---|
| sub 0 `$0903` | `AD 7C 0A 30 10 EE 8C 0A CD 8C 0A D0 08 A2 0E 20 B6 0A 8D 8C 0A` |
| sub 2 `$1D8B` | `AD 00 1F 30 10 EE 10 1F CD 10 1F D0 08 A2 0E 20 D0 1E 8D 10 1F` |
| sub 3 `$2A23` | `AD 8D 2B 30 10 EE 97 2B CD 97 2B D0 08 A2 0E 20 A8 2B 8D 97 2B` |
| sub 4-14 `$33DB+5` | `AD D0 35 30 10 EE E0 35 CD E0 35 D0 08 A2 0E 20 49 35 8D E0 35` |

Identical opcodes; only operand addresses differ (and subs 4-14 have an extra 5-byte preamble before the same template starts). All four are literally the **same engine assembled at different addresses** with different state regions.

| Handler | Bytes |
|---|---|
| sub 1 `$1119` | `A2 02 CE 33 14 10 06 AD 34 14 8D 33 14 BD 08 14 8D 0B 14 A8 AD` |

Sub 1 has no matching opcode prefix — distinct engine.

## Play loop wrapper

```
$086D: LDX #$XX           ; operand at $086E — per-frame counter
$086F: INC $086E          ; ticks each play call
$0872: LDA $a2; PHA; STX $a2  ; swap X into KERNAL ZP $A2
$0877: JSR <handler>      ; operand patched by init
$087A: PLA; STA $a2; RTS
```

So `$A2` holds the *frame counter* throughout the handler call. Handlers read it to time pattern advancement.

## Family A engine shape

Common skeleton (sub 0's instance, others equivalent at relocated addresses):

```
$0903: LDA <state.v1_phase>   ; read voice-1 phase
       BMI <skip-v1>          ; phase bit 7 set → voice silent
       INC <state.v1_ctr>
       CMP <state.v1_ctr>
       BNE <skip-v1>
       LDX #$0E               ; V3 base (engine-internal odd voice ordering)
       JSR $0AB6              ; voice "tick" subroutine
       STA <state.v1_ctr>
<skip-v1>:
... same pattern for V2, V3 ...
INC <state.frame_ctr>
LDA <state.frame_ctr>
CMP <state.tempo>
BNE ...                       ; not yet → exit
JMP <song-loop-or-advance>
```

The engine has **per-voice phase counters + tempo counter + JSR-based note-step routines**, reading pattern data via zero-page pointers (`$1C/$1D`, `$1E/$1F`, `$20/$21` for sub 0 — relocatable per instance).

Voice data is dispatched by `JSR $0954` (sub 0's voice-event router at `$0954-$09CC`), which decodes pattern bytes:
- Note `<$09`: scale-of-12 note → write to SID via freq tables at `$0B5F` (lo) and `$0BDF` (hi), via offset to register 0x01,X (freq hi) then 0x00,X (freq lo) then update timbre.
- Note `$09`: rest / sustain
- Notes `$0C`/`$0D`/`$0E`: control events (envelope, slide)
- High-bit-set bytes: pattern-end / loop / song-end markers (handled by `$09C5`/`$09D6` paths)

State block (sub 0 example) at `$0A6E-$0AB4`:
- `$0A6E` — V1 phase
- `$0A71` — V2 phase
- `$0A72`+X — per-voice secondary state (4 bytes each)
- `$0A83` — tempo
- `$0A84` — alt-tempo (loop marker)
- `$0A85` — frame ctr
- `$0A86/87` — V1 pattern ptr base
- `$0A88/89` — V2 pattern ptr base
- `$0A8A/8B` — V3 pattern ptr base
- `$0A8C/8D` — running ctr (one per voice)

Init template for sub 0 starts at `$10C7` (32 bytes copied to `$0A6E-$0A8D` by `$0A8E`).

## Family B engine shape (sub 1)

Different. First instructions at `$1119`:
```
LDX #$02
DEC <ctr1>
BPL +6
LDA <ctr2>; STA <ctr1>
LDA <ptn_table>,X; STA <jsr-op>
...
```

This looks more like a *pattern-jump-driven* engine — needs separate RE before migration.

## Feature-disable patches

Init patches 9 locations with `RTS`/`NOP` *for every subtune*:
- `$0900` (RTS) — 3 bytes before sub 0's handler `$0903`
- `$1334` (RTS) — middle of sub 1's region
- `$1D88` (RTS) — 3 bytes before sub 2's handler `$1D8B`
- `$2A20` (RTS) — 3 bytes before sub 3's handler `$2A23`
- `$33D8` (RTS) — 3 bytes before subs 4-14 handler `$33DB`
- `$342B`, `$34B7`, `$360C` (RTS), `$35FB` (NOP) — internal to subs 4-14 region

The "3 bytes before each handler" pattern suggests these are alternate entry points or trampolines disabled at runtime.

## Music data layout

Each Family A instance has its own state block + pattern data, all bundled in the same SID body. Sub 0's pattern data lives in `$0B5F-$0BDF` (freq tables) + somewhere referenced by the zp ptrs initialized from `$0A86-$0A8B` (pattern start addresses).

Subs 4-14 each have a per-subtune entry stub (5-byte JSR + setup) at `$38A0..$4224` that the shared `$33DB` engine dispatches to via the frame counter.

## Migration plan

| Step | Scope | Sessions |
|---|---|---|
| 1 | Family A extract + composer for **one subtune** (sub 0 — simplest, isolated state) | 1-2 |
| 2 | Extend Family A composer to handle the multi-instance physical layout (subs 0, 2, 3) | 1 |
| 3 | Extend Family A to handle subs 4-14 (shared engine + per-subtune dataset dispatch) | 1-2 |
| 4 | Family B extract + composer for sub 1 | 1-2 |
| 5 | Multi-subtune composer for the unified 15-subtune SID | 1 |

Total realistic budget: **4-7 sessions**. Less than the original 5-10 estimate because the family collapse cut effective engines from 5 to 2.

## Open questions for the next session

1. Where do sub 0's V1/V2/V3 pattern pointers actually point? Need to read `$10C7-$10E6` (the init template) and follow.
2. The mysterious `JSR $10E5` in `$09E8` — likely the song-start setup for sub 0. Need to trace.
3. The 11 5-byte stubs `$38A0..$4224` — confirm they're per-subtune setup calls for subs 4-14.
4. CIA timer is set to `$2663` for subs 4-14 only. Implications for play rate?
5. Family B (sub 1) — full RE pass needed; agent's notes for `$1119` weren't verified by py65 trace.
