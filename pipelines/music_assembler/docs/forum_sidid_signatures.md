# Music Assembler — SIDId player byte signatures & player family tree

> **source_url:** https://github.com/cadaver/sidid (files `sidid.cfg` + `sidid.nfo`,
>   fetched as raw.githubusercontent.com/cadaver/sidid/master/{sidid.cfg,sidid.nfo})
> **fetched_via:** WebFetch
> **fetch_date:** 2026-06-13
> **author/handle:** Lasse Öörni (cadaver / Covert Bitops) — maintainer of SIDId,
>   the canonical SID-player fingerprint database (the same tool HVSC uses to
>   classify engines).
> **content_date:** signatures accreted ~2007–present; entries reference the 1989 release.
> **reliability:** secondary (community-maintained fingerprint DB, but it IS the
>   de-facto authority for engine classification and is what HVSC/sidid use).

This is the single most useful version-distinction artifact found. SIDId works
by scanning the SID binary for a fixed opcode pattern from the player routine
(`??` = wildcard byte, `AND` = the following pattern must ALSO match anywhere,
`END` = end of pattern). A hit on one of these patterns is how HVSC labels a
tune as "Music_Assembler". **There are SIX distinct but related signatures** —
this is the version/packer-variant map the task asked for.

## The signatures (verbatim from sidid.cfg)

### `Music_Assembler` (the base / canonical player)
```
BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60 B9 ?? ?? 85 END
```
Decoded (operands wildcarded):
```
LDY abs,X        ; BC ?? ??     load some per-voice index byte
CPY #$FE         ; C0 FE        $FE sentinel test  (matches arpeggio $FE=stop!)
BNE +9           ; D0 09
LDA abs,X        ; BD ?? ??
AND #$FE         ; 29 FE        clear bit0 (the "29 FE" gate-clear idiom)
STA abs,X        ; 9D ?? ??
RTS              ; 60
LDA abs,Y        ; B9 ?? ??
STA zp           ; 85 ??
```
The `C0 FE / D0 09` ($FE-sentinel) and `29 FE` (clear gate bit) match the
manual's documented `$FE = stop` arpeggio terminator and the gate-bit handling.

### `Music_Assembler/MC` (Marco Swagerman variant)
```
EE 19 D0 20 ?? ?? 4C AND BD ?? ?? 85 ?? BC ?? ?? C8 C8 B1 FA C9 FF D0 02 A0 00 98 9D END
```
Decoded:
```
INC $D019        ; EE 19 D0     acknowledge the raster IRQ
JSR ?? ??        ; 20 ?? ??
JMP ...          ; 4C ...
  AND (second mandatory pattern):
LDA abs,X        ; BD ?? ??
STA zp           ; 85 ??
LDY abs,X        ; BC ?? ??
INY / INY        ; C8 C8       advance pointer by 2
LDA (zp),Y       ; B1 FA       read packed data stream via ZP ptr $FA/$FB
CMP #$FF         ; C9 FF       $FF sentinel  (track $FF=loop / seq $FF=loop)
BNE +2           ; D0 02
LDY #$00         ; A0 00       wrap pointer to 0 on $FF
TYA              ; 98
STA abs,X        ; 9D ...
```
**This is the most informative signature for the packed-stream model:** it shows
the player walks a packed byte stream through a zero-page pointer (`$FA/$FB`),
advancing by 2 bytes per step (`INY INY`), and treats `$FF` as the
loop/wrap terminator (`CMP #$FF`). Matches the manual's track entry format
(sequence#, transpose, repeat) and `$FF = loop`.

### `Dutch-USA_Team/ProDrum`
```
F0 14 C9 FE F0 4A AA CA A9 00 85 F7 BD END
```
`C9 FE / F0 4A` again is the `$FE` sentinel branch. A separate "ProDrum"
sub-engine — note CLAUDE.md's Commando memory warns about phantom drum
sub-engines; MA apparently has a real optional drum path.

### `Dutch-USA_Team/MC`
```
29 FE 99 04 D4 98 AA A5 END
```
`29 FE` (clear bit0) then `STA $D404,Y` (`99 04 D4`) — i.e. it masks the SID
**control register $D404 gate bit** before writing it. Direct evidence of the
per-frame $D404 write model: gate-off is done by `AND #$FE` then `STA $D4xx`.

### `Dutch-USA_Team/86` (a 1986-era earlier player by the same team)
```
B9 ?? ?? 9D ?? ?? AC ?? ?? B9 00 ?? 9D ?? ?? B9 ?? ?? 9D ?? ?? 60
AD 00 ?? 8D 00 D4   AD 01 ?? 8D 01 D4   AD 07 ?? 8D 07 D4   AD 08 ?? 8D 08 D4 END
```
This one is a literal SID register copy loop:
```
LDA $xx00 -> STA $D400   (V1 freq lo)
LDA $xx01 -> STA $D401   (V1 freq hi)
LDA $xx07 -> STA $D407   (V2 freq lo)
LDA $xx08 -> STA $D408   (V2 freq hi)
```
A different, older write-model (full register block copy). Likely NOT the same
packed format — flag as a separate engine if HVSC labels any tune with this.

### `Harald_Rosenfeldt` — "Music Assembler V3.1" (NAME COLLISION, different product)
```
E8 8A 4A A8 A9 01 99 ?? ?? E8 E0 0C D0 C1 END
```
**Critical disambiguation:** sidid.nfo lists a *second, unrelated* product also
called "Music Assembler" — **"Music Assembler V3.1" by Harald Rosenfeldt, 1989,
64'er/Markt & Technik.** This is NOT the Swagerman/Giesen Dutch USA-Team player.
Both are 1989 Markt & Technik magazine products, so the names collide. When
filtering HVSC by the string "Music Assembler", expect to catch Rosenfeldt's
tunes too — they have a completely different signature and write model
(`E8 8A 4A A8` = INX/TXA/LSR/TAY index math; a 12-entry loop `E0 0C`) and must
be excluded from any Dutch-USA-Team migration. Treat as a distinct engine.

## Player family tree (from sidid.nfo descriptive text)

The Music Assembler **player routine** was reused as the runtime for several
later editors. SIDId's notes:

- **VoiceTracker** (1991) — "Editor based on the Music Assembler player"
- **Music_Mixer** (1991) — "Editor based on the Music Assembler player"
- **DoubleTracker** (1993) — "Multispeed version of VoiceTracker. Editor based
  on the Music Assembler player"
- **Ten_Tracker** (1991) — "10x speed version of VoiceTracker. Editor based on
  the Music Assembler player"

**Implication for the migration:** the same packed-data format + player runtime
likely underlies VoiceTracker / Music Mixer / DoubleTracker / Ten Tracker tunes
too. DoubleTracker = multispeed, Ten Tracker = 10× speed — these are the
multispeed/dispatch-rate variants to expect (cf. CLAUDE.md Trap C / CIA-tune
handling). A single MA decoder may cover a much larger HVSC slice than the 6,351
"Music Assembler"-tagged tunes if these derivatives share the format.

## What this tells us about the packed format & write model

1. **ZP stream pointer:** packed data is walked via a zero-page pointer at
   **$FA/$FB** (`B1 FA` = `LDA ($FA),Y`), advanced `INY INY` (2 bytes/step) in
   the MC variant — consistent with the manual's 2/3-column track entries.
2. **Sentinels:** `$FE` = stop, `$FF` = loop/wrap, decoded inline (`C0 FE`,
   `C9 FF`, `C9 FE`) — matches the manual's documented track/seq/arp terminators.
3. **Gate handling:** gate-off is `AND #$FE` then `STA $D4xx` (`29 FE 99 04 D4`)
   — write-model detail for $D404/$D40B/$D412 control registers.
4. **IRQ ack:** `INC $D019` (`EE 19 D0`) confirms a raster-IRQ driven player.
