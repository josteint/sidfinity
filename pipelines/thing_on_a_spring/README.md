# Thing on a Spring pipeline

End-to-end rebuild of Rob Hubbard's *Thing on a Spring* (1985 Gremlin Graphics).
Same shape as the Commando / Monty pipelines.

## Status (2026-05-15)

| Metric | Value |
|---|---|
| Subtunes extracted | 1 (the title music — PSID #1, 0-indexed 0) |
| Lean build | green (`lake build sidgen_thing_on_a_spring`) |
| Codegen runs | yes, produces `build/thing_on_a_spring.sid` |
| Grade vs original | **F — 4.8% snapshots (72/1500)** |

**The scaffold is in place, but the codegen does NOT yet match this
engine.** The extract + codegen were cloned from Monty's pipeline (which
graded A) with the SID path + freq-table base swapped to Thing on a Spring's
values, but Thing on a Spring's player has structural differences from
Monty's that haven't been ported across. The README in this repo's
history claimed Grade A 98.8%; that claim is stale.

Reference disassembly: `docs/hubbard_thing_on_a_spring_disassembly.s`.

## Layout

Identical to Commando — see `pipelines/commando/README.md` for the layout
explanation. The Thing-on-a-Spring-specific differences (vs Monty) currently
live as:

| File | Thing-on-a-Spring-only change |
|---|---|
| `extract/emit_usf.py` | `THING_ON_A_SPRING_SID` path; `THING_ON_A_SPRING_FT_BASE = $C3A9` |
| `extract/engine_model.py` | Path swap only |
| `codegen/ThingOnASpring/Codegen.lean` | ≈73 lines of cosmetic diff vs Monty |
| `codegen/ThingOnASpring/USF.lean` | identical to Monty (incl. `skydive` field) |

## How to run

```bash
source src/env.sh
python -m pipelines.thing_on_a_spring.extract.emit_usf      # → SongData.lean (subtune 0)
lake build sidgen_thing_on_a_spring
./.lake/build/bin/sidgen_thing_on_a_spring                  # → build/thing_on_a_spring.sid

python3 src/writelog_grade.py \
    data/C64Music/MUSICIANS/H/Hubbard_Rob/Thing_on_a_Spring.sid \
    pipelines/thing_on_a_spring/build/thing_on_a_spring.sid
```

## Engine differences from Monty / Commando (from the disassembly)

These are the load-bearing reasons the Monty-clone codegen doesn't byte-match.
Numbers/labels are from `docs/hubbard_thing_on_a_spring_disassembly.s`.

1. **SFX overlay player at `$C326`**. Subtune 0 plays the main song;
   subtunes 1..16 are sound effects that run a *separate* 2-voice engine
   over V1+V2 while the main player skips its SID writes (via the
   `$C4A0` gate at `$C310`). The current codegen has no concept of this
   overlay — it emits Monty's 3-voice song player only. Subtune 0 alone
   is enough for the title music, but the main player's per-voice loop
   itself still checks `$C4A0` BMI/BPL on every freq/ctrl/PW write,
   which Monty's main player does not.

2. **Freq table is 96 semitones × 2 bytes at `$C3A9`**, not Monty's
   layout. The discovery base is correct in `emit_usf.py`, but downstream
   code expects Monty's semantics.

3. **fx flags semantics (`$CD31,Y`)**:
   - bit 0 → freq-hi DOWN-sweep with test-bit ($80) ctrl retrigger near
     mid-note (drum sound).
   - bit 1 → freq-hi UP-sweep (no ctrl retrigger).
   - bit 2 → +24-semitone arpeggio on odd-numbered `$C49D` frames (two
     octaves up — *not* Commando's +12).

4. **Self-modifying code at `$C35F`**. `sub_C4A9` patches the opcode
   byte to `$EE` (INC) or `$CE` (DEC) based on SFX flags bits 4-5,
   choosing whether the SFX walks step UP or DOWN per tick. Only matters
   for SFX subtunes; can be left as a doc note for now.

5. **Instrument layout (8-byte stride at `$CD2A`, 15 records)**:
   `+0 PW_LO  +1 PW_HI  +2 CTRL  +3 AD  +4 SR  +5 vib_divider
    +6 pulse_delta_packed  +7 fx_flags`. The pulse-delta byte packs
   amount (high 3 bits) + pwcnt-reload (low 5 bits) — see `$C22F`.

6. **PWM bounds**. Standard Hubbard `$08` / `$0E` direction flip on
   PW_HI (see `reference_hubbard_pwm_bounds.md`). Mutation is IN-PLACE
   on `$CD2A` / `$CD2B` per-instrument bytes — same as Commando.

7. **Hard-restart threshold**. The release path at `$C173` fires when
   `v_notelen == 0` *and* note byte bit 5 (no_release) clear. The
   README's old claim of "HR threshold = 1" doesn't match — it's "= 0".

## Next steps

To get this to Grade A on subtune 0:

1. Diff `Codegen.lean` against Monty's and find which assumptions (HR
   threshold, fx-flag bit semantics, freq-table size, voice state
   addresses) no longer hold for this engine.
2. Verify the `$C4A0` SFX-active gate is *always* true on subtune 0
   (since no SFX is active) — if so, the gate writes can be omitted in
   the rebuilt player, but the address layout still has to match.
3. Compare frame 0 register writes against `siddump --writelog` output
   from the original to identify which extracted instrument values are
   wrong. (Currently frame 0 emits 21 SID writes — the original emits
   only `$D418 = $0F` and a freq pair at frame ≈9800 cycles.)

## Why a separate pipeline from Monty

Two Hubbard SIDs from the same player era still differ in load-bearing
ways. Cloning the pipeline rather than parameterising it keeps the Monty
byte-perfect invariant safe while this one is being adapted. The two
can be merged once a third Hubbard SID validates the abstraction.

See also: the engine notes in
`docs/hubbard_thing_on_a_spring_disassembly.s` and the memories
`reference_hubbard_pwm_bounds.md`,
`project_hubbard_notenum_overlap.md`.
