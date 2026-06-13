---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-13
author: cadaver (fingerprint scanner), signatures by Ian Coog / Ice00 / Ninja / Yodelking / Wilfred/HVSC / Prof. Chaos
content_date: current (repo)
reliability: primary
---

# SID Factory II — SIDID Fingerprints

From cadaver's sidid.cfg (https://github.com/cadaver/sidid):

## SidFactory (original, pre-II)

```
SidFactory/Laxity
A9 ?? 4C ?? ?? A9 ?? 9D ?? ?? A9 ?? 9D ?? ?? BD ?? ?? A8 29 02 D0 ?? 4C ?? ?? 98 29 FD 9D END
```

## SidFactory II / Laxity

```
SidFactory_II/Laxity
C8 B1 ?? C9 FF D0 04 C8 B1 ?? A8 98 AND C9 7E F0 ?? 18 END
```

NOTE: `AND` here is the sidid wildcard/mask operator, not the 6502 AND instruction.
This signature matches the sequence scan loop in the SF2 driver that checks for
sequence end ($7F) and note-tie ($7E) markers.

## Laxity NewPlayer V21

```
Laxity_NewPlayer_V21
99 04 D4 BD ?? ?? C9 FF F0 ?? 4C ?? ?? DE ?? ?? BD ?? ?? D0 ?? 4C END
```

This is the NP20 (JCH NewPlayer) format as used in older Laxity/JCH tunes.

## Implications for SF2 identification

- HVSC tunes using SF2 driver 11-16 will be tagged as "SidFactory_II/Laxity"
- Tunes using the older SF2 (C64-only edition) will be tagged "SidFactory/Laxity"
- NP20 tunes get "Laxity_NewPlayer_V21" (separate from SF2 proper)
- The SF2_II signature is in the sequence reader loop, not the driver header
- For USF extraction: the self-describing header at load address (0x1337 magic) is
  the authoritative identifier, not the sidid byte pattern

## OPEN: Distinguish driver 11 variants by signature

The sidid database does NOT distinguish between driver versions 11.00 through 11.05.
To identify which specific driver version a SID uses, we need to:
1. Read the driver binary and parse the self-describing header (block 1 descriptor)
2. Check version_major (11) + version_minor (00..05) from the Descriptor block
3. OR check the HR table size (8 vs 16 rows) and presence of note-delay feature

This can be done programmatically by porting the `driver_info.cpp` parser to Python.
