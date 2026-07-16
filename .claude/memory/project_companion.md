---
name: project_companion
description: "Companion engine pipeline — pipelines/companion/. Instruction-sequence exact for Up_up_and_Away.sid (5/5 subtunes). First non-Hubbard-'85 engine in our pipeline. Engine origin documented (Keith Bowden 1984 type-in book) via research-player skill."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Pipeline for Rob Hubbard's earliest SID — `Up_up_and_Away.sid`
(1984 Starcade). Uses the **Companion engine** (Keith Bowden, 1984
type-in driver from *The Companion to the Commodore 64*, Pan Books).
Hubbard extended Bowden's base driver before later writing his own
1985 player (the Commando-era engine).

**Status (2026-05-25): FULLY instruction-sequence exact, 5/5 subtunes.**
```
unified sub_0: 2860/2860 (100.0%) — 52 sec
unified sub_1:  660/ 660 (100.0%) — 12 sec
unified sub_2:  440/ 440 (100.0%) —  8 sec
unified sub_3:  220/ 220 (100.0%) —  4 sec
unified sub_4:  715/ 715 (100.0%) — 13 sec
```

## Engine model

3-voice flat-note sequencer, ~334 bytes of code. Per-voice:
locked timbre (pw_lo, pw_hi, ctrl, AD, SR). Per-subtune: 32-byte
init template at distinct binary offsets + per-voice orderlists.

Hubbard's extension on top of Bowden:
- Two tempo dividers per subtune (gate_off_tick + note_load_tick)
  for staccato/legato — instead of Bowden's single tempo.
- Global V3 PW_LO sweep: `pw_lo += 4 + carry` every other frame.
  The carry comes from the `CMP #$01` set when triggering — so
  the effective step is +5 per frame (NOT +4). Easy to miss.
- Extended note sentinels: `$8C` rest, `$8D` end-tune (on V3),
  plus `$80 + pitch` = play pitch AND schedule early release at
  next gate-off tick. Bowden's base only had `$80`=rest,`$FF`=restart.
- 5-subtune dispatch via self-modifying JMP at `$C913/$C914`.

The original engine **does NOT check `song_alive`** in its play
loop — `$8D` on V3 writes vol=0 but the engine keeps advancing
orderlist positions, reading garbage bytes adjacent in memory.
The pipeline reproduces this by extending each extracted orderlist
with 32 bytes past `$8D` (the bytes the orig engine would read).

## Pipeline layout

- `pipelines/companion/config.py` — `CompanionConfig`: per-subtune
  binary addresses (templates, orderlists, dispatch).
- `pipelines/companion/extract/` — reads SID binary, parses 5
  subtunes' state templates + orderlists + freq tables.
- `pipelines/composer.py` (shared composer; the earlier per-family
  `pipelines/companion/codegen.py` is gone) — emits a 6502 engine at $1000
  that reproduces the original frame-by-frame writes; assembles
  via xa65 and wraps as PSID.

## USF representation

`hvsc84/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.usf` is the source of truth — the
shipped `.sid` is built from it alone (no binary access at build
time, per the [[feedback_always_through_usf]] principle).

USF schema unchanged; Companion's music fits cleanly:
- 5 music subtunes, each with its own `params { ... }` + `init { ... }`
- 15 instruments (5 subs × 3 voices, locked timbres with ctrl/pw/ad/sr)
- Each voice: orderlist=[1] stop + 1 pattern (the song-proper rows)

The Companion engine reads past its $8D terminator (the play loop
doesn't check song_alive). The bytes it reads are the original
binary's per-voice slot-padding — a uniform fill byte between
each voice's $8D and the next adjacent chunk. We capture this as
**(count, byte) parameters per voice** in the subtune's existing
`params { }` bag (`v1_pad_count`, `v1_pad_byte`, …, `v3_pad_byte`).
Mechanism stays parametric, not opaque bytes. Schema clean.

Companion's binary layout per subtune block:
```
ord_s<i>_v1  (orderlist + v1 padding)
ord_s<i>_v2  (orderlist + v2 padding)
ord_s<i>_v3  (orderlist + v3 padding)
tmpl_s<i>    (32-byte init template, derived from `init { }`)
```
This mirrors the original adjacency so reads past each $8D fall
into the next chunk's bytes — same as the original.

## Engine code bugs caught during build

Three quirks of the original engine had to be matched exactly:

1. **PW sweep step is +5, not +4**: The original `ADC #$04` runs
   after a `CMP #$01` that always sets C=1, so the effective add
   is 5. No `CLC` to clear. Easy to miss reading the source.
2. **V3 pw_lo is NOT written during note-load**: Hubbard's
   `proc_normal` calls `sub_C8C9` first which checks `CPX #$0E`
   and SKIPS the pw_lo store for V3. V3's PW is governed solely
   by the global sweep.
3. **The engine never checks song_alive**: `$C7A1` is set/cleared
   but never branched on in the play loop. The engine keeps
   running past `$8D`, reading garbage bytes. Our rebuild must
   emit enough post-`$8D` bytes (32 extra per orderlist suffices
   for all 5 subs at 1.1x HVSC length).

## Research dossier

Full research notes at `pipelines/companion/docs/` (25+ files with
provenance headers). Includes Bowden's complete commented
disassembly extracted from JC64dis. Engine lineage tree:
Bowden 1984 → Hubbard (Up,up&Away), Chris Murray (Henry's House,
A4=423Hz), Graham Jarvis (Clever Music) → Jay Derrett (~22 CRL
games). Plus Vic Berry's 1988-89 tools.

## Related

- `_deprecated/project_usf_refactor.md` — overall pipeline status
- docs/the_principle.md — when (if) to extend
  USF to cleanly represent Companion-shape engines.
