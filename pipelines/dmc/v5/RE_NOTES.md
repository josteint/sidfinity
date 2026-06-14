# DMC V5 — RE notes (Phase A complete)

Rep: `DEMOS/G-L/Katusha.sid` (family-3, 1461 + family-5 sibling 34 = the
dominant V5 player). Phase A (full disassembly + annotation) DONE
2026-06-14 → `pipelines/dmc/v5/disassembly.s`. Scope + plan in
`pipelines/dmc/v5/SCOPE.md`; format research in
`pipelines/dmc/docs/dmc_v5_{format_notes,docs_original}.md` +
`dmc_sector_commands.md`.

## ✅ Resolved in Phase A (all in disassembly.s header)

- **Sector command byte map** (the flagged unknown): notes `<$80`;
  commands `$F1-$FE` (SRR/ADR/VOL/gate×2/FD-/FD+/FRQ/FLT/SLD/GLD/SND/DUR/
  GATE) + `$FF` END. Track (orderlist): `$FC/$FD` transpose, `$FE`
  voice-end, `$FF pp` loop.
- **8-byte instrument** order confirmed from runtime: AD, SR, WV, PU, FL,
  vib-delay, vib-speed, vib-width(&$07).
- **3 programmable 2-byte tables** (wave/pulse/filter), `$90`=loop;
  filter is **voice-3 only** (`CPX #$02` @ $1496). Vib step = base-note
  freq << width. Full 11-bit filter cutoff ($D415 lo + $D416 hi).
- **Per-voice write order** (sid_write $16E6): freq lo/hi, PW lo/hi, ctrl
  (AND gate mask). Global $D415/$D416 once per play; $D418 in fade;
  $D417 at FLT cmd. Hard restart via gate-mask $F6 + SR=0 (gate_logic).

## Phase B (extract) — operand sites for dataflow

The packer places the data tables per song (like V4 — these addresses
are operand-patched; Katusha's values are the disassembly's). The extract
reads the base of each table by dataflow from these CODE sites (operand
lo-byte address = the listed PC + 1):

| table | Katusha addr | read sites (PC) |
|---|---|---|
| orderlist ptr | $1878 | $1046, $1059 (init) |
| sector ptr lo/hi | $196E / $1972 | $114E / $1153 |
| instrument | $1976 | $12CB/$12CF (note_on), $134F.. (note_init2) |
| freq lo/hi | $170F / $176F | $13A5/$13AB, $168C/$1692, $153B/$1541 |
| wave ctrl/freq | $199E / $19AB | $1385/$165E, $19AB reads alongside |
| pulse lo/hi | $19B8 / $19BF | $13C0/$13C9, $143C/$1450 |
| filter lo/hi | $19C6 / $19C7 | $13EF/$13F5, $149D/$14B1 |

NB confirm whether WV/PU/FL instrument pointers are entry indices or
need ×2 — the player uses them as ENTRY indices into the 2-byte tables
(reads `$199E,y` / `$19AB,y` with y = the pointer, not ×2). So pointers
are entry indices; the table arrays are split lo/hi (parallel), not
interleaved 2-byte records.

## Phase B/C open items

1. Packed memory map for ARBITRARY members (Katusha's table addresses are
   operand-patched — generalize via the dataflow sites above; build a
   `dmc_v5_config` factory like V4/family-2).
2. USF schema: the 3 programmable tables (content-by-reference), fade
   (FD+/-), ADR/SRR live register-sets, full filter cutoff, vib-step=
   freq<<width. Reuse `_offtable_check` pattern.
3. NEW V5 composer (the V4 composer does NOT apply). Write-log-first on
   Katusha. Verdict: `verify_dmc` (engine-neutral, reuse as-is).
4. **family-4 branch (686, Jupiter41, play +$95):** distinct (~0.31
   Jaccard) — diff its disasm against family-3's once family-3 is FULL.

## Next concrete step

Phase B: seed the V5 extract (`pipelines/dmc/v5/extract/`) + `config.py`
+ `factory.py` off the operand sites above; lift Katusha to a V5 model
and start the write-log loop on a new composer.
