---
name: chimera-pipeline-state
description: "Chimera — MIGRATED to USF, all 4 subtunes (2 music + 2 digi) through USF; music frame-exact via py65, digi cycle-strict via writelog."
metadata: 
  node_type: memory
  type: project
  originSessionId: 0dddd211-01d5-48ea-b899-54adc79e22ae
---

Rob Hubbard's *Chimera* (1985 Firebird). USF demo SID:
`hvsc85/MUSICIANS/H/Hubbard_Rob/Chimera.sid` (12440 bytes; read
directly from HVSC — the old demo/hubbard copy is gone).

**USF status (2026-05-24): COMPLETE + on the USF-only pipeline.**
Chimera is `pipelines/hubbard/chimera/config.py` on the shared Hubbard '85
core + `pipelines/hubbard/chimera/extract/to_usf.py` adapter writing
`Chimera.usf` + `Chimera.sample{2,3}.flac` (see
[[reference_usf_format]]). All 4 subtunes pass verify_all:

- Music subtunes 0, 1: 6000/6000 frame-exact via py65.
- Digi subtunes 2, 3: 108/108 + 138/138 writelog cycle-strict (when
  verified via the original RSID); writeset-match flatten via the
  PSID rebuild's slightly different dispatcher cycle count.

Commits 18cce55, 9df7877 (music codegen) + 7a40627, 26115f8, 922f59c
(digi pipeline D1..D3c) + c931160, e3e9a0f, 8eac97b, 29bb548 (USF-only
build + PSID conversion + no verbatim engine bytes).

**Two players in one file.** Music engine at $C200/$C203/$C206 (the
standard '85 tracker — freq table $C567, instruments $C662, 8-byte
records, 19 of them, 2 music subtunes). A separate digi player at
$C000 drives the other 2 PSID subtunes — **now also through USF** via
the digi pipeline (extract → Sample/FLAC sidecar → pack_digi → combined
RSID build). Disassembly: `pipelines/hubbard/chimera/disassembly.s`.

**The digi pipeline** (engine-agnostic, see [[reference_digi_pipeline]]):
- `pipelines/hubbard/chimera/extract/digi.py` extracts the 1-bit waveform-
  toggle samples + per-block vol envelope. Sample bytes are 17-byte
  groups `[vol, audio×16]`; bits emitted MSB-first via V1 ctrl
  $41/$49; CIA2-paced. The $A10B "sample-table" is a bank-
  VALIDATION table, NOT the bank index — `$C045-$C049` reloads
  X = bank * 4 before reading $A000+X*4.
- `pipelines/build_from_usf.py` (thin wrapper over `pipelines/composer.py`) is the unified build for
  music + digi (the previous `build_with_digi.py` is gone). All
  pieces of the digi region are regenerated, NOT lifted verbatim:
  - PSID dispatcher at $9F80 — hand-written xa65 (no KERNAL deps,
    no IRQ install, proper play() entry).
  - Digi player at $C000 — hand-written xa65 in
    `pipelines/hubbard/engine_constants.py::CHIMERA_DIGI_PLAYER_ASM`,
    assembled verbatim — the same 305 bytes as the original.
  - Bank table at $A000, validation at $A10B (sorted bank-ascending
    for cycle-strict scan match), pace+bank tables in the
    dispatcher.
  - Sample bytes from `pack_digi(read_sample(flac))`.
  - Boundary-vol byte (engine reads one past `end` on the $F9 wrap
    before exit) preserved via Sample.extras['boundary_vol'].
  Combined file: PSID v2, ~45KB (sparse — music at $1000, big zero
  gap, digi region at $9F80-$C130).

**IRQ-driven — drove a shared-core capture fix.** Chimera's PSID play
address is 0; the music runs from a raster IRQ installed at the
KERNAL vector $0314/$0315. `inst_program.capture` now, when the PSID
play address is 0, follows $0314/$0315 after init (the handler JSRs
the real play routine and exits via JMP $EA31 into $00-filled memory,
which the BRK sentinel catches). The rebuilt SID is a normal
play-address SID, so only the original needs this.

Config deltas (all EngineConfig fields):
- `instr_base=0xC662, instr_count=19, freq_table_base=0xC567`.
- `speed_ctr_init=2` — the $C652/$C653 tick gate defers note-load 2
  frames; frames 0-1 are effects-only.
- `vib_onset=8` (CMP #$08 at $C3D3).
- `arp_period=8` — arp is `frame & 7`: base 1-of-8, +12 7-of-8. The
  ArpSpec now carries a period-length interval tuple; `_arp` indexes
  it mod len (Commando stays period 2).
- `linear_pw_or=0x40` — linear PW does `ORA #$40` on pw_lo ($C412).
- `incby2_step=1` — fx bit 1 does INC v_fhi (+1, $C526).
- `incby2_onset=0x11` — fx bit 1 needs dur field >= $11.

Chimera runs effects before the first note-load (and V1's first note
is a tie), so the shared core now seeds two more per-voice variables
from the freq-table overlap: `dur_field` (freq+205, the vibrato carry
path) and `slide_v` (freq+239, the drum's cached freq-hi). The drum
itself (fx bit 0) needed no new code — the shared `_skydive` already
IS it (onset writes freq_hi + ctrl=$80; decay does freq_hi-- +
gate-clear).

How to apply: Chimera is done — all 4 subtunes. The linear-PWM carry
the old memory flagged as "unmodelable" is fully handled by
`_vibrato`'s carry_out plus the dur_field seed — instruction-sequence exact, not
"inaudible drift". For digi work on a different engine, start from
the Chimera digi pipeline (the extract → Sample/FLAC → pack flow is
mostly engine-agnostic; only `extract_digi` and the dispatcher patch
addresses are engine-specific). See [[reference_digi_pipeline]].

**Player lives at $B093 — the banking-restore-anywhere-inside-cleanup
trap (2026-05-27).** The digi player's cleanup originally restored
banking ($37) in the middle of its instruction sequence. Banking $37
maps BASIC ROM over $A000-$BFFF, so if `player_base` lives in that
range, instructions fetched *after* the sta $01 read BASIC ROM bytes
instead of the RAM we wrote. The first attempt (commit 7c0abd7) moved
the restore to "just before RTS" — but the RTS itself still has to
be fetched from $A000-$BFFF AFTER the sta $01, so the fix was
incomplete: sub 4 played fully but a phantom ping fired at ~3.1s
because PC walked through BASIC ROM bytes into the driver data area
and re-entered the dispatcher init.

**The real fix (commit 1b68da3):** don't restore banking in the
player's cleanup AT ALL. psiddrv's setregs already does
`lda #$37 ; sta $01` itself after init returns (in the driver page at
$04xx, which is RAM regardless of $01). So cleanup just does
mute / restore VIC / pla×4 / cli / rts — all under banking $36, all
fetched from RAM. RTS pops into psiddrv's driver page; psiddrv
restores banking from RAM-safe ground.

**Why:** any sta $01 that flips banking $36→$37 from inside the
$A000-$BFFF region ruins all subsequent in-routine instruction
fetches. There is no "safe spot" to put the restore — it must be done
from a location outside the banked range (e.g. driver page or
$C000+), or not at all.

**How to apply:** when writing any RAM-resident routine in
$A000-$BFFF that manipulates $01, don't restore banking yourself.
Let the caller (whose code is outside the banked region) restore it.
Diagnosis was done with `tools/siddump --pc-trace FILE START END`
(added in commit 1b68da3 — useful for any future "where did the CPU
go" investigation).

Final state: `player_base=$B093` (auto-packed against samples ending
at $B092), file 9601 bytes (smaller than original 12440), all 4
subtunes instruction-sequence exact + 32s playback in sidplayfp.
