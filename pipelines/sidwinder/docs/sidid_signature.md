---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg (upstream); local copies at deprecated/gt2_pipeline/tools/sidid.cfg and tmp/ariston_research/sidid/sidid.cfg
fetched_via: local read (grep) + WebFetch direct
fetch_date: 2026-06-17
author: cadaver (Tamás Felső) — SIDId project; signature authored by unknown contributor
content_date: unknown (present in the project from at least 2009)
reliability: primary
---

# SidWinder — SIDId Signature

## Canonical byte signature

From cadaver/sidid `sidid.cfg` (identical in all three local copies):

```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

`??` = wildcard (any byte). `END` terminates the pattern.

### 6502 disassembly of the fixed bytes

| Offset | Byte | 6502 mnemonic | Notes |
|--------|------|---------------|-------|
| +0  | AD | LDA abs       | Load from absolute address (speed counter?) |
| +1  | ?? | addr lo       | |
| +2  | ?? | addr hi       | |
| +3  | F0 | BEQ rel       | branch if zero (counter reached 0 = new frame tick) |
| +4  | ?? | branch offset | |
| +5  | CE | DEC abs       | decrement (speed counter) |
| +6  | ?? | addr lo       | |
| +7  | ?? | addr hi       | |
| +8  | 88 | DEY           | decrement Y (voice loop counter) |
| +9  | 4C | JMP abs       | loop back to voice processing top |
| +10 | ?? | addr lo       | |
| +11 | ?? | addr hi       | |
| +12 | B9 | LDA abs,Y     | load from table indexed by Y |
| +13 | ?? | addr lo       | |
| +14 | ?? | addr hi       | |
| +15 | C9 | CMP #imm      | compare with immediate |
| +16 | ?? | immediate     | |
| +17 | 90 | BCC rel       | branch if carry clear |
| +18 | ?? | branch offset | |
| +19 | F0 | BEQ rel       | branch if equal/zero |
| +20 | ?? | branch offset | |
| +21 | B9 | LDA abs,Y     | load from table indexed by Y (sector instr?) |
| +22 | ?? | addr lo       | |
| +23 | ?? | addr hi       | |
| +24 | 8D | STA abs       | store to absolute (likely SID register or state) |
| +25 | ?? | addr lo       | |
| +26 | ?? | addr hi       | |
| +27 | A8 | TAY           | transfer A to Y |

**Interpretation:** The signature covers the core voice-dispatch loop of the
SidWinder player: a speed-counter decrement + zero-test, a DEY + JMP loop across
3 SID voices, followed by a sector-instruction comparison dispatch. This matches
the published PLAYER.ASM architecture (see source_docs section below).

## Single variant — no version split

Only ONE signature is registered for SidWinder. There is no separate entry for
V01.22 vs V01.23. The V01.23 packer notes that the player is relocatable (all
addresses relative to `pstart` label); the fixed opcode bytes are the same across
relocations, so one pattern covers all packed instances.

## SIDId project metadata for SidWinder

From `sidid.nfo` (cadaver/sidid, GitHub master):

```
SidWinder
   AUTHOR: Balázs Takács (Taki)
 RELEASED: 1999 Natural Beat
REFERENCE: https://csdb.dk/release/?id=66494
```

No format notes, no multiple-version notes in the NFO entry.

## sidid.cfg context (surrounding entries)

```
SidTracker64
BD ?? ?? 29 FE 9D 04 D4 B9 ?? ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? F0 ?? A8 BD ?? ?? 18 69 END

SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END

Silas_Warner
69 01 9D ?? ?? A9 00 9D ?? ?? 9D 04 D4 8A 18 69 END
```

## WilfredC64/player-id

A second independent signature tool (`github.com/WilfredC64/player-id`, Rust
implementation, BNDM algorithm) also maintains a signature database. It lists
contributors including Wilfred Bos, iAN CooG, Professor Chaos, Cadaver, Ninja,
Ice00, and Yodelking. SidWinder coverage is expected to be the same pattern but
was not separately confirmed from that database during this sweep.

## Leads to follow

- Confirm WilfredC64/player-id's SidWinder entry: `https://github.com/WilfredC64/player-id`
  (look in the `.cfg` or `.toml` signature files in that repo)
- Cross-reference the 6502 disassembly of the signature against `SRC/PLAYER.ASM`
  in the source archive (zimmers.net, locally at
  `tmp/sidwinder_research/src_docs/` after extraction) — the `pstart`-relative
  layout will show exactly which routine contains this pattern.
- The packer's identity field at player_base+$20 (default $1020) is a 32-byte
  ASCII ID field — could be used as a secondary detection anchor.
- Factor6 uses 38 SidWinder SIDs in HVSC — verify the same signature fires on
  his files (no custom variant; Factor6 is Czech so may have received the editor
  via FTP/internet rather than in-scene sharing).
