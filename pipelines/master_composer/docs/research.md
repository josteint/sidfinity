## Master Composer (1,075 tunes)

> **⚠ 2026-06-13 — see [`README.md`](README.md) + `spec_extraction_plan.md`/`spec_write_model.md`** (decoded from the local JC64dis disasm + ground-truthed against real binaries via `siddump`). Corrections to this overview: it's **CIA-timed, NOT VBlank** (PSID speed=$1 for 996/1019 → the **per-IRQ** `--writelog-per-irq` verdict); the data-table bases are **dataflow-derived per file** (≥2 player relocations/variants — the fixed offset map below is one member's, not universal); note byte = `$00` rest / `$01-$63` freq index / **`$64` gate-off**; a block applies a **16-register full SID snapshot** (`outTimbre` +$0AA), waveform/gate per-note (gate retrigger). The `(Patrick_Payne)` sidid tag is the **same player** (an adjacent voice-slice anchor, not a fork); `(Lope_Pulse_Sweep)` (~20 files) is a real external PW-sweep add-on needing its own config; `TFMX/MasterComposer` (5 files) is a separate engine — exclude.

- **Author:** Paul Kleimeyer
- **Publisher:** Access Software, Inc.
- **Year:** 1983-1984
- **Price:** $39.95
- **Source:** Not public
- **CSDb:** #128699
- **Historical significance:** First popular C64 music editor

### Entry Points (typical load $7580)
- $7580: Init (7 bytes)
- $7587: Play (init + 7)
- VBlank-timed, interrupt-driven
- Relocatable (absolute addresses adjusted at load time)

### Three-Tier Hierarchy

**1. Pages (up to 23):** Played sequentially, each specifies start/end block.

**2. Blocks (up to 64):** Each defines ALL SID register values for 3 voices:
- Waveform, ADSR, pulse width, filter cutoff, resonance/routing, volume/mode
- When a new block starts, all SID parameters change (like switching instruments)

**3. Bars (up to 127):** Each bar = up to 16 notes (16th-note resolution):
- $00 = rest
- $01-$63 = note frequency index
- Bar durations stored in separate table

### Memory Layout

| Offset | Purpose |
|--------|---------|
| +$000 | Init routine |
| +$007 | Play routine entry |
| +$0AA | Block register write routine |
| +$300 | Frequency table lo (96 entries) |
| +$360 | Frequency table hi (96 entries) |
| +$3C0 | Player variables (page/block/bar indices, flags) |
| +$3D0 | Bar duration table (127 entries) |
| +$450 | Block parameter tables (64 entries each, 16 tables for all SID regs) |
| +$A68 | Page table (23 entries) |
| +$A80 | Note/music data |

Player code: ~768 bytes. Total: 3600-7800 bytes.

### Characteristics
- No built-in effects (no vibrato, arpeggio, PWM)
- Direct SID register manipulation per block
- Default tuning: 450 Hz (NTSC) / 433.5 Hz (PAL)
- Identical player code across all files (only addresses differ for relocation)
- Known bug: decaying hum after final page completes
- Page duplication allows songs up to ~20 minutes
