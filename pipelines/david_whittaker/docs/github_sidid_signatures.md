---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-17
author: Cadaver (Lasse Öörni) + contributors (Wilfred Bos, iAN CooG, Professor Chaos, Ninja, Ice00, Yodelking)
content_date: 2024-10-28 (latest update per search metadata)
reliability: primary
---

# SIDID / Player-ID — David Whittaker Signatures

## Source repositories

- **cadaver/sidid** (original C tool): https://github.com/cadaver/sidid
  - Config: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
  - NFO:   https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
- **WilfredC64/player-id** (Rust re-implementation, same .cfg format):
  https://github.com/WilfredC64/player-id
  - Config: https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg

## Signature entry — `David_Whittaker`

Both cadaver/sidid and WilfredC64/player-id carry identical signatures (five
alternative patterns; any single match identifies the file as Whittaker):

```
David_Whittaker
CE ?? ?? 8E 04 D4 E8 8E 04 D4
8D 06 D4 AE ?? ?? 8E 04 D4 E8 8E 04 D4
AD ?? ?? 85 ?? AD ?? ?? 85 ?? A0 00 B1 ?? 8D ?? ?? C8 B1 ?? 8D ?? ?? 60
B1 ?? F0 && C8 B1 && A9 ?? 8D 04 D4 A9 ?? 8D 04 D4 && 69 02 85
8D 08 D4 B9 ?? ?? 8D 0E D4 B9 ?? ?? 8D 0F D4 A9 ?? 8D 04 D4
```

Format notes:
- `??` = wildcard (any byte)
- `&&` = logical AND mask (WilfredC64 uses `&&`; cadaver uses `AND`)
- Each line is an independent alternative (OR logic — any line matching = identified)

## Signature interpretation

**Sig 1** (`CE ?? ?? 8E 04 D4 E8 8E 04 D4`):
- `CE ?? ??` = `DEC abs` at some address (decrementing a counter, likely a voice
  duration/tempo counter)
- `8E 04 D4` = `STX $D404` (SID voice 1 control register)
- `E8` = `INX`
- `8E 04 D4` = `STX $D404` again — appears to be a gate-off + gate-on pair with X
  register stepping, characteristic of Whittaker's note trigger sequence

**Sig 2** (`8D 06 D4 AE ?? ?? 8E 04 D4 E8 8E 04 D4`):
- `8D 06 D4` = `STA $D406` (voice 1 sustain/release)
- `AE ?? ??` = `LDX abs`
- `8E 04 D4` = `STX $D404` (control reg)
- `E8` + `8E 04 D4` = INX + STX $D404 again (the INX-double-write pattern)
  This is the waveform/gate sequence in the sound-update loop.

**Sig 3** (`AD ?? ?? 85 ?? AD ?? ?? 85 ?? A0 00 B1 ?? 8D ?? ?? C8 B1 ?? 8D ?? ?? 60`):
- Two `LDA abs / STA zp` pairs — loading voice data pointers into zero page
- `A0 00` = `LDY #$00`
- `B1 ??` = `LDA (zp),Y` — indirect read of pattern/instrument data
- `8D ?? ??` = `STA abs` — storing to voice state
- `C8` = `INY`
- `B1 ??` = `LDA (zp),Y` — second byte read
- `8D ?? ??` = `STA abs`
- `60` = `RTS` — end of a short sub; likely the voice-pointer-load helper

**Sig 4** (`B1 ?? F0 && C8 B1 && A9 ?? 8D 04 D4 A9 ?? 8D 04 D4 && 69 02 85`):
- `B1 ??` = `LDA (zp),Y` — reading from pattern data
- `F0 (AND mask)` = branch/check
- `C8 B1 (AND mask)` = INY + LDA indirect
- `A9 ?? 8D 04 D4` = `LDA #imm / STA $D404` (load waveform byte, write to SID ctrl)
- `A9 ?? 8D 04 D4` = second write to $D404 (gate toggle)
- `69 02 85` = `ADC #$02 / STA zp` — likely advancing a pointer or arpeggio counter

**Sig 5** (`8D 08 D4 B9 ?? ?? 8D 0E D4 B9 ?? ?? 8D 0F D4 A9 ?? 8D 04 D4`):
- `8D 08 D4` = `STA $D408` (voice 2 freq lo)
- `B9 ?? ??` = `LDA abs,Y` (freq table lookup)
- `8D 0E D4` = `STA $D40E` (voice 3 freq lo)
- `B9 ?? ??` = `LDA abs,Y`
- `8D 0F D4` = `STA $D40F` (voice 3 freq hi)
- `A9 ?? 8D 04 D4` = load+write to $D404 (voice 1 ctrl)
  This is the 3-voice frequency-update loop, the central play() hot path.

## The companion `Chris_Walsh` entry

Not a Whittaker variant, but appears adjacent in the cfg:

```
Chris_Walsh
E9 00 8D ?? ?? AD ?? ?? 8D 0E D4 AD ?? ?? 8D 0F D4 CE ?? ?? AD ?? ?? C9 00
F0 1A AD ?? ?? 18 6D ?? ?? 8D ?? ?? 8D 10 D4 AD ?? ?? 6D ?? ?? 8D ?? ??
8D 11 D4 60 A0 00 A9 10 8D 12 D4 B1 ?? C9 FF
```

## Notes for RE

- Five alternative signatures cover the known C64 variant space. The
  `E8 / 8E 04 D4` (INX + STX $D404) double-write sequence is the most
  discriminating fingerprint — it is Whittaker's gate-toggle idiom.
- No separate "Whittaker_v2" / "Whittaker_v3" entries exist in either
  tool's config — all known variants are folded into one set of signatures.
- The absence of a split entry means sidid cannot distinguish early (Lazy
  Jones era) from late (Panther era) variants — treat all Whittaker SIDs as
  one engine family until disassembly shows otherwise.

## Leads to follow

- Raw sidid.cfg (cadaver): https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
- Raw sidid.cfg (WilfredC64): https://raw.githubusercontent.com/WilfredC64/player-id/master/config/sidid.cfg
- cadaver's sidid.nfo (appears binary-encoded, needs hex dump): https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
- WilfredC64 player-id Rust source (BNDM search): https://github.com/WilfredC64/player-id/tree/master/src
- CSDb: Player Identifier V1.00 by Wilfred Bos (2012): https://csdb.dk/release/?id=112812
