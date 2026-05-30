---
name: Trust the binary, not the disassembly's !by directives
description: ACME/source disassembly comments for data sections can disagree with the actual binary — always read the bytes
type: feedback
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
**Rule:** When reverse-engineering a SID player, NEVER trust the
data-section initial values shown in the disassembly source's `!by`
directives. Read the actual bytes from the binary at the runtime
address instead.

**Why:** During the Monty PWM investigation (2026-05), the ACME
disassembly source `hubbard_monty_disassembly_acme.asm:696` says

    pulsedelay !by $00,$00,$00
    pulsedir   !by $00,$00,$00

but the actual binary at $84E5 / $84E8 has

    pulsedelay = $00, $01, $1D
    pulsedir   = $01, $00, $00

The disassembly was correct about *code* (instruction bytes match) but
out-of-date / sloppy about *data section initial values*. Trusting
the source comment cost hours of "why does first PWM step fire at the
wrong frame?" debugging when the answer was already there in the
binary.

**How to apply:** For any state-bearing variable in a Hubbard-class
player (pulsedelay, pulsedir, savefreq*, voicectrl, instrnr, lengthleft,
etc.), find its actual address by pattern-matching the relevant
instruction (e.g., `DEC abs,X` for pulsedelay), then read the raw
bytes at that address from the SID payload before init runs. If init
doesn't subsequently overwrite those bytes, that's the actual initial
state your codegen must reproduce.

A quick-and-dirty pattern search example for finding pulsedelay:

```python
for i in range(len(payload) - 5):
    if payload[i] == 0xDE and payload[i+3] == 0x10:  # DEC abs,X ; BPL +
        addr = payload[i+1] | (payload[i+2] << 8)
        print(f'DEC ${addr:04X},X at ${load+i:04X}')
```
