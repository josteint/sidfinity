---
source_url: https://github.com/WilfredC64/player-id (config/sidid.cfg + sidid.nfo), https://github.com/cadaver/sidid (config/sidid.cfg + sidid.nfo)
fetched_via: direct
fetch_date: 2026-06-13
author: WilfredC64 (player-id), cadaver/Lasse Öörni (sidid)
content_date: master/main as of 2026-06-13
reliability: primary=source code (the canonical detection signatures shipped with the two reference SID-ID tools)
---

# Music Assembler — player-ID signature database (sidid.cfg)

The canonical player-detection signatures used by **SIDId** (cadaver/Lasse
Öörni) and **player-id** (WilfredC64, the modern multi-core re-implementation,
sidid.cfg-compatible). These are the patterns HVSC's `Documents/` tooling and
deepsid use to label tunes as "Music Assembler".

## Signature file format (player-id V2.0 spec, doc/Signature_File_Format.txt)

- Signatures are space-separated **2-hex-digit** byte values matched against the
  SID **load image** (the relocated player code in memory).
- `??` = wildcard for ONE byte. There is no nibble wildcard.
- `AND` / `&&` (the `&&` form added in V2.0) = "skip multiple bytes until the
  next occurrence of the following pattern is found" — i.e. a gap-allowing
  concatenation of two sub-patterns.
- `END` = end of a (possibly multi-line) signature; optional in V2.0, required
  in V1.0. Without END a signature terminates at end-of-line.
- A player name line introduces one or more signature lines; a parenthesised
  name `(Name)` is a sub-variant under the preceding player heading.
- Authoring guidance: avoid absolute addresses (players are relocated — match on
  opcodes + SID I/O regs like `$D4xx` which are fixed; wildcard zero-page and
  relocatable operands).

## Music_Assembler family signatures (verbatim)

```
Music_Assembler
BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60 B9 ?? ?? 85

(Music_Assembler/MC)
EE 19 D0 20 ?? ?? 4C && BD ?? ?? 85 ?? BC ?? ?? C8 C8 B1 FA C9 FF D0 02 A0 00 98 9D

(VoiceTracker)
BC ?? ?? C8 20 ?? ?? C9 FF D0 02 A0 00 98 9D && C8 B1 FA C9 FD F0 01 60 C8 B1 FA

(Music_Mixer)
A9 F0 8D 17 D4 29 0F 8D A6
```

### The multispeed editor variants (same MA player core)

```
(Ten_Tracker)
CE ?? ?? A2 00 D0 ?? A2 0A

(DoubleTracker)
AD ?? ?? F0 05 A2 00 20 ?? ?? AD ?? ?? F0 05 A2 01 20 ?? ?? AD ?? ?? F0 05 A2 02
```

Note Ten_Tracker's `CE ?? ?? A2 00` = `DEC abs; LDX #$00` — the SAME speed-counter
+ `LDX #$00` voice-loop opener seen at the MA play entry ($c021: `DEC $c090; ...
LDX #$00`), but with the multispeed twist (`A2 0A` = `LDX #$0A` later = the "10x"
in Ten_Tracker). DoubleTracker's signature is its 2-up multispeed dispatch
(`AD abs; F0 05; LDX #$00; JSR ...; ... LDX #$01 ...; LDX #$02`) — three voices
driven twice per frame. All six signatures live under ONE `Music_Assembler`
heading in sidid.cfg, confirming a single player core with editor-front-end and
dispatch-rate variations.

(cadaver/sidid lists the first four; the `&&` appears as `AND` in older configs.
Ten_Tracker / DoubleTracker are in the WilfredC64 player-id `config/sidid.cfg`.)

### Dutch-USA_Team auxiliary signatures (same author group)

```
Dutch-USA_Team/ProDrum
F0 14 C9 FE F0 4A AA CA A9 00 85 F7 BD

Dutch-USA_Team/MC
29 FE 99 04 D4 98 AA A5

Dutch-USA_Team/86
B9 ?? ?? 9D ?? ?? AC ?? ?? B9 00 ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? 60
```

## Decoding the primary Music_Assembler signature (6502 disassembly)

This is the most useful piece for the decompiler: the canonical signature IS a
verbatim fragment of the player's per-frame inner loop. Disassembled
(operands that are `??` are relocatable absolute/zero-page addresses):

```
BC ?? ??     LDY  abs,X        ; index a per-voice byte (Y = work value), X = voice
C0 FE        CPY  #$FE         ; compare to $FE  ($FE = "stop" sentinel in MA tables)
D0 09        BNE  +9           ; if not $FE, branch past the masking step
BD ?? ??     LDA  abs,X        ; load voice byte
29 FE        AND  #$FE         ; mask off bit0
9D ?? ??     STA  abs,X        ; store back
60           RTS
B9 ?? ??     LDA  abs,Y         ; (start of next routine) table-indexed load
85 ..        STA  zp           ; stash into zero page
```

Key takeaways for RE:
- `$FE` is a live sentinel in the running tables (matches the manual's
  "$FE = stop" / "$FF = loop" for arpeggios and tracks). The player tests for
  `#$FE` and `#$FF` (`C9 FF` appears in the VoiceTracker variant) inline while
  walking packed streams.
- `AND #$FE` / `ORA`-style bit0 toggling on a per-voice byte = the classic
  "gate / new-note flag in bit0" pattern. Bit0 is used as a control flag the
  player clears after consuming it.
- `B1 FA` (`LDA ($FA),Y`) in the MC + VoiceTracker variants: the packed
  sequence stream is walked through a **zero-page pointer at $FA/$FB**
  indexed by Y. `C9 FF D0 02 A0 00` = "if byte==$FF, reset Y to 0" (the loop
  wrap), `C9 FD F0 01 60` = "if byte==$FD, return" (another sentinel — $FD).
  So the packed stream uses at least THREE in-band sentinels: **$FD, $FE, $FF**.

## Player entry points (from manual / research.md, cross-checked vs. Tape Master Pro note)

- IRQ setup: `base + $0000`
- play:      `base + $0021`
- init:      `base + $0048`

Tape Master Pro's loader-music guide independently documents
"Init $1048 play $1021 (Voice Tracker or Dutch USA Team's Music Assembler)"
— i.e. for a player relocated to base $1000, confirming play=base+$21,
init=base+$48. VoiceTracker shares the SAME entry layout (it is the same
player core with a different editor front-end).

## Variant family (from sidid.nfo — all share the Music Assembler PLAYER CORE)

| Variant            | Author                     | Year | Group       | Notes |
|--------------------|----------------------------|------|-------------|-------|
| Music_Assembler    | Marco Swagerman (MC) & Oscar Giesen (OPM) | 1989 | Dutch USA-Team | original |
| Music_Assembler/MC | (MC's own front-end)       | 1989 | Dutch USA-Team | distinct init/play fingerprint |
| VoiceTracker       | Pawel Soltysinski (Polonus)| 1991 | Science 451 | editor on the MA player |
| Music_Mixer        | Pawel Soltysinski (Polonus)| 1991 | Padua       | editor on the MA player |
| DoubleTracker      | Pawel Soltysinski (Polonus)| 1993 | Padua       | **multispeed** version of VoiceTracker |
| Ten_Tracker        | Moog                       | 1991 | Keen Acid   | **10x speed** version of VoiceTracker |

CSDb refs: Music_Assembler #94388, VoiceTracker #77308, Music_Mixer #82618,
DoubleTracker #8430, Ten_Tracker #63135.

IMPLICATION for SIDfinity: there is NOT one MA player but a family of at least
6 binaries sharing a packed-data core. DoubleTracker (multispeed) and
Ten_Tracker (10x) imply per-tune dispatch-rate variation — the PSID `speed`
bit / CIA handling will differ across the family (cf. CLAUDE.md Trap C /
CIA-timed verdict). Expect a version-group split in HVSC analogous to GT2 A/B/C/D.
