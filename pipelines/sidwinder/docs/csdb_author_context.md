---
source_url: https://commodorefree.com/magazine/vol10/issue91.html
fetched_via: direct
fetch_date: 2026-06-17
author: Hermit (author of TEDzakker; Commodore Free magazine issue 91)
content_date: ~2016
reliability: secondary
---

# SIDwinder in Context — Third-Party References

## Commodore Free Magazine Issue 91 (TEDzakker article)

Hermit, discussing the music tool landscape for Plus/4 before TEDzakker's release:

> "There's a port of SIDwinder (C64 by Taki, ported by TLC), a new PC editor
> Knaecketraecker, that's all."

This positions SIDwinder as one of only two existing native C64/Plus/4 music editors at the time.

---
source_url: https://csdb.dk/release/?id=99574
fetched_via: direct
fetch_date: 2026-06-17
author: Luca (FIRE / Fantastic Italian Research Enterprise)
content_date: 2011-04-18
reliability: primary
---

## Luca (FIRE) — Technical Commentary on SIDwinder V01.23 Enhanced

Luca beta-tested both the original C64 SIDwinder and TLC's Plus/4 port. His CSDb comments
(2011) are the most technically informative third-party statements:

### On the license:
> "I got it's based on TLC/CNS' 'SIDwinder V01.23', released under GPL licence on C64
> and Plus/4+SIDcard."

### On the packer bug:
> "years ago, I spotted out a bug in that version's packer, and TLC coded and released
> a fixed SIDwinder V01.23 packer on Plus/4 which works ok."

### On the scope of the bug:
> "...and the longer the tune, the higher the probability to collect bugs in
> endpoints and/or glide/slide."

The "endpoints" refer to sector Finish markers and glide/slide table endpoints — the
packer was miscomputing offsets in complex songs, causing playback corruption in
glide (pitch transition) and slide (pitch shift) effects.

---
source_url: https://plus4world.powweb.com/software/SIDwinder_V01_23
fetched_via: direct
fetch_date: 2026-06-17
author: Plus/4 World documentation (TLC/Coroners)
content_date: 2000
reliability: primary
---

## Architectural Notes: Original C64 V01.22 vs V01.23 (TLC Port)

From the Plus/4 World description:
> "Original Author: Balázs Takács (Taki/Natural Beat) - V01.22 for C64 (1994)"
> "Plus/4 Conversion: Levente Hársfalvi (TLC/Coroners) - 2000"
> "The original C64 version was developed in 1994 but remained unreleased until later.
> TLC adapted it for Plus/4, improving the editor and developing a new packer from scratch."

Key architectural differences between C64 V01.22 and V01.23:
- TLC rewrote the packer from scratch (the C64 packer had the bug above)
- TLC added Plus/4 SID card support (clock-adjusted frequency table, ZP word change)
- V01.23 was the first GPL release
- The Plus/4 SID card base address is `$FD40` (not C64's `$D400`)

---
source_url: https://www.pouet.net
fetched_via: direct
fetch_date: 2026-06-17
author: pouet.net
content_date: 2026
reliability: primary
---

## Pouet.net — No Natural Beat Presence

Natural Beat group is **not listed on pouet.net**. The group search for "Natural Beat"
returned empty results. SIDwinder as a production is also not listed (only the unrelated
2025 Genesis Project visualizer tool).

Natural Beat was a pure music group active 1993–2000; their releases were music
collections and tools (not demos), which explains the absent Pouet listing
(Pouet is primarily demo-focused).

---
source_url: https://csdb.dk/release/?id=8708
fetched_via: direct
fetch_date: 2026-06-17
author: CSDb
content_date: 1998-09-15
reliability: primary
---

## Cubic Player (1998) — Natural Beat "Third Album"

CSDb release #8708. Taki's music player/disc release also known as "The Third Album."
Contains 13 tracks: Classical, Draxish, Drummer, Glorious, Impulse, Lost Love, Memories,
Precisely, Prince of Persia #1, Radiation, Realbeat, Southern, Uncertain.

These tracks also appear on SIDwinder V01.23 (released 2000), suggesting the SIDwinder
release was partly a showcase/demo disc for the editor, including music composed in it.

Download mirrors:
- ftp://ftp.padua.org/pub/c64/Demos/pal/natural_beat/cubicplayer_NB.zip
- ftp://c64.rulez.org/pub/c64/Demos/n/Natural_Beat/Cubic_Player.zip

---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-17
author: Cadaver (Covert Bitops) + contributors
content_date: 2021 (version 1.09)
reliability: primary
---

## SidWinder Player Fingerprint (cadaver/sidid)

The HVSC playroutine identity scanner `sidid` includes a signature for SidWinder:

```
SidWinder
AD ?? ?? F0 ?? CE ?? ?? 88 4C ?? ?? B9 ?? ?? C9 ?? 90 ?? F0 ?? B9 ?? ?? 8D ?? ?? A8 END
```

Decoded 6502 instruction sequence:
- `AD ?? ??`  — LDA $nnnn (absolute load, likely track table index)
- `F0 ??`     — BEQ (branch if zero, end/loop check)
- `CE ?? ??`  — DEC $nnnn (decrement counter)
- `88`        — DEY
- `4C ?? ??`  — JMP $nnnn (jump — dispatch loop)
- `B9 ?? ??`  — LDA $nnnn,Y (load from table, Y-indexed)
- `C9 ??`     — CMP #imm (compare with command marker)
- `90 ??`     — BCC (branch if carry clear)
- `F0 ??`     — BEQ (branch if equal)
- `B9 ?? ??`  — LDA $nnnn,Y (load next byte)
- `8D ?? ??`  — STA $nnnn (store — likely to SID or work register)
- `A8`        — TAY (transfer to Y — used for indexing)

This is characteristic of the sector command dispatch loop: reading a command byte,
comparing it to command thresholds, then loading and storing note/instrument data.

The `??` wildcards handle relocation — the same player works at different load addresses.
