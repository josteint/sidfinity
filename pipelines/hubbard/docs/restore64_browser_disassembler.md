---
source_url: "https://restore64.dev/"
fetched_via: "direct"
fetch_date: 2026-04-11
author: "local: tool documentation notes"
content_date: "2026-04-11"
reliability: "secondary"
---
# Restore 64 — Browser-Based C64 Disassembler

**URL:** https://restore64.dev/
**Alt URL:** https://restore.datucker.nl/
**Type:** Client-side JavaScript (no server upload, runs entirely in browser)

## Capabilities

### Auto-Depacking
Supports 370+ packer formats (ByteBoozer, Exomizer, PuCrunch, etc.). Automatically
detects and decompresses packed PRG files before disassembly.

### SID Player Detection
Uses 787 SIDID signatures to identify SID player engines. Should detect Rob Hubbard's
engine variants. Detection works via IRQ vector analysis, register write patterns,
and call graph tracing.

### Multi-Pass Analysis
1. Control flow tracing with register and flag state tracking
2. IRQ/NMI handler discovery
3. Self-modifying code detection
4. Jump table and RTS trick identification
5. Inline data recognition
6. PETSCII string detection

### Hardware Register Annotation
Names 250+ VIC-II, SID, CIA, and zero-page registers. Decodes bitfields in comments
showing exactly what each hardware write does. Example: `STA $D404` would be annotated
with the control register bit meanings (gate, sync, ring, test, waveform select).

### Output Formats
- KickAssembler (v5.25+) — primary format
- ACME
- 64tass

All dialects get correct syntax, directives, and addressing mode notation.

## Using with Hubbard SIDs

### Preparation
PSID files may need header stripping before dropping into Restore 64. The tool expects
PRG format (2-byte load address + raw binary). Steps:
1. Strip the $7C-byte PSID header from the SID file
2. Prepend the 2-byte little-endian load address
3. Or use a SID-to-PRG conversion tool

### What to look for
- Init routine: Follow from the init address to see how song number indexes into song table
- Play routine: The main loop shows voice processing order, register write sequence
- Data regions: Should appear as `.byte` directives after code analysis completes
- Self-modifying code: Hubbard's driver modifies pulse width values in instrument data
  (stored in player memory, not in SID registers) — Restore 64 should detect this

### Limitations for our use case
- No Hubbard-specific data structure labeling (unlike SIDdecompiler which names
  instruments, sequences, songs, etc.)
- Browser-only: cannot be scripted for batch processing
- Output is generic disassembly, not structured data extraction
- No API or CLI interface

## Value Assessment

**Best for:** Quick interactive exploration of specific problematic Hubbard SIDs during
decompiler development. When our parser fails on a particular SID, drop it into Restore 64
to visually inspect the code structure and identify where data regions begin/end.

**Not suitable for:** Batch processing, automated data extraction, or production pipeline use.
