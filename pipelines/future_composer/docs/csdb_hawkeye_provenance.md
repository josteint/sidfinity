---
source_url: https://csdb.dk/sid/?id=28158
fetched_via: direct
fetch_date: 2026-06-03
author: Jeroen Tel (Maniacs of Noise)
content_date: 1988 (Thalamus release)
reliability: primary
---

# Hawkeye (Jeroen Tel, 1988) — engine provenance

## Verified header facts (CSDb)

| Field            | Value     |
|------------------|-----------|
| Load address     | `$7AE0`   |
| Init address     | `$7AE0`   |
| **Play address** | `$7AE3`   |
| Number of songs  | 12        |
| Default song     | 1         |
| SID model        | 6581      |
| Clock            | PAL       |
| Data size        | 8,768 bytes (`$2240`) |

Sources:
- CSDb SID page: https://csdb.dk/sid/?id=28158
- HVSC path: `MUSICIANS/T/Tel_Jeroen/Hawkeye.sid`
- DeepSID listing: https://deepsid.chordian.net/?file=MUSICIANS/T/Tel_Jeroen/Hawkeye.sid

## Critical correction to `research.md`

The existing 95-line summary states FC V3.x uses **play = init+6**,
and groups Hawkeye under "V3.x (Hawkeye)". But the Hawkeye SID
header shows **play = init+3** (`$7AE0` init, `$7AE3` play).

**Disassembly of the Hawkeye SID entry prologue (verified
2026-06-03 by py65 against the actual SID body):**

```
$7AE0  JMP $918F      ; init entry — jumps to init code at $918F
$7AE3  JMP $7B98      ; play entry — jumps to play code at $7B98
$7AE6  BRK            ; ...
```

So Hawkeye uses a **two-JMP dispatch table** at the load
address. The "real" init is at `$918F` and the "real" play is
at `$7B98`. The +3 offset gives room for `JMP abs` (3 bytes).
This is **functionally equivalent** to the FC V4 standalone
player's `JSR $1800` / `JSR $1806` pattern — the V4 wrapper
just calls into the +0/+6 entries directly, while Hawkeye uses
a 3-byte JMP trampoline at +0/+3.

The original `research.md` claim of "**+6 distinctive offset**"
applies specifically to **FC V4 editor output** (the standalone
`PLAYER $4000 [D]` wrapper code, see `csdb_fc_v4_player_disasm.md`).
**FC V3.x output, including Hawkeye, uses +3** (init JMP +
play JMP, 3 bytes each).

And **the FC_V3.x sidid signature has been confirmed to match
Hawkeye.sid directly** — see prior session's `hawkeye_sid_layout.md`
plus this session's grep at byte offset 321 of the PSID body
(memory address $7C1F). So **Hawkeye IS an FC V3.x driver** —
research.md's family classification is correct, only the +6
specific is wrong.

The reality:

1. **Hawkeye's driver is the MoN 1988 game driver** — the original
   code Jeroen Tel and Charles Deenen wrote into Thalamus's game.
2. **FC V1.0 (FIG, June 1988)** ripped this driver almost verbatim.
3. **FC V3.0/V3.1 (1989-1990)** added new features on top —
   wave/pulse/filter tables, multi-voice editor improvements —
   AND shifted the internal layout, hence the new `+6` play
   offset.
4. The "better driver from Hawkeye" mentioned in VGMPF refers
   to the FC team **back-porting** Hawkeye improvements into the
   FC editor, not to Hawkeye-the-game shipping FC V3 inside it.

For our pipeline this means:

- A "Hawkeye-engine" pipeline must target the **MoN 1988 driver
  variant**, not the FC V3 editor's emitted bytes.
- HVSC's sidid classification (per `csdb_sidid_signatures.md`):
  Hawkeye.sid will most likely match the `MoN/FutureComposer`
  *generic* signature (the filter-table-fetch / 6-DEY-rewind
  block — that code IS in the Hawkeye driver) but **may not match
  `FC_V3.x`** (the wave-table threshold dispatcher).
- HVSC's 4,085-tune count under "MoN/FutureComposer" mixes
  Hawkeye-lineage game music with FC-editor-emitted SIDs. A
  byte-exact rebuild needs both code paths.

## Companion SID — Hawkeye loader music

- https://csdb.dk/release/?id=20130 → "Hawkeye Mix'em Loader Music"
- HVSC path: `MUSICIANS/T/Tel_Jeroen/Hawkeye_loader.sid`
- Same engine family, smaller song. Useful as a **paired test
  case** alongside the 8.7 KB main Hawkeye SID — if our rebuild
  byte-matches both, we have the driver-and-data path right.

## DeepSID — useful complementary tool

`https://deepsid.chordian.net/` plays SIDs in-browser with
register-level visualizers. Useful when ear-testing rebuilds.
Also exposes its sidid classification for each SID; cross-check
ours against theirs.

## Open question (LEAD)

Is there a CSDb release page or PRG for the "Hawkeye driver"
specifically (i.e. an isolated ripped/decompiled version)?
The search results to date show only the Hawkeye SID itself
and the "loader music" companion — no rip of the driver as a
standalone artifact. Worth checking
`https://csdb.dk/scener/?id=` for Jeroen Tel / Charles Deenen
productions in the 1988–1989 window, and the various MoN
demo releases (some carry the driver as a music routine, with
or without sources).
