# SID-Wizard — SID-export binary layout (`exporter.asm`)

> **Provenance**
> - source_url: https://github.com/anarkiwi/sid-wizard (mirror of https://sourceforge.net/p/sid-wizard/code)
> - raw files: `https://raw.githubusercontent.com/anarkiwi/sid-wizard/master/sources/exporter.asm`, `.../sources/settings.cfg`, `.../sources/include/player.asm`, `.../sources/SWM-spec.src`
> - fetched_via: curl (raw.githubusercontent.com)
> - fetch_date: 2026-06-13
> - author: Hermit (Mihály Horváth); relocation/reloc-table macros by Soci/Singular
> - content_date: `$Id: exporter.asm 387 2014-07-09` / `settings.cfg` / `player.asm` rev ~382 (SID-Wizard 1.x line; these sources are the V1.x editor/exporter, 64tass syntax)
> - reliability: **primary** (the actual exporter that produced the HVSC `SidWizard_V1.x` SID files)

This is the SIDfinity **extraction target**: the layout of the C64 binary that
SID-Wizard's `exporter.asm` writes into an exported `.sid`. Our decompiler must
parse this layout in reverse. **NB:** this is *not* the SWM workfile layout
(that is `github_swm_format.md`); the exporter transforms the SWM workfile into
this compacted, name-stripped, pointer-table form.

---

## 0. The two layouts — do not confuse them

| | SWM workfile (`.swm`) | Exported SID data section |
|---|---|---|
| Header | 64-byte SWM header present | **dropped** (copied into player's `TUNE_HEADER` ZP/var area, then cropped) |
| Instrument names | 8-byte name per instrument | **stripped** during compaction |
| Pattern end | `$FF` end-signal | replaced by a **size byte**, then length-info |
| Pointers | implicit (editor max-size tables) | explicit **lo/hi pointer tables** for patterns + instruments, computed at export |
| Tempo `$FF` | filter-table `$FF` end | turned into size info |

The exporter (`preparetunedata`, exporter.asm:1144) does the transform.

---

## 1. Top-level memory map of the exported file

From `settings.cfg` and exporter.asm `SIDHEADER` / `CIAINIT` / `LOADADDR`:

```
settings.cfg:31   PLAYERADDR = $1000        ; player code base (default; user-relocatable on export)
exporter.asm:998  SIDHEADERSIZE = $7c        ; PSID v2 header size (124 bytes)
exporter.asm:1037 *= CIAINIT-2  CIAADDR      ; 2-byte CIA load address (relocator leaves alone)
exporter.asm:1040 *= PLAYERADDR-$48  CIAINIT ; CIA-starter code sits in the $48 bytes BELOW PLAYERADDR
exporter.asm:1078 *= PLAYERADDR-2  LOADADDR  ; .byte <PLAYERADDR,>PLAYERADDR (safety load addr)
exporter.asm:1082 *= PLAYERADDR              ; player.asm code
exporter.asm:1091 *= PLAYERADDR+MAX_PLAYERSIZE  MUSICDATA  ; music data immediately after player
```

So on disk the SID file is:

```
[ PSID v2 header, $7C bytes ]
[ 2-byte load address = PLAYERADDR (lo) , relocaddr (hi) ]
[ CIA-starter code  ($48 bytes, at PLAYERADDR-$48)  — ONLY for multispeed tunes ]
[ player code        (at PLAYERADDR = $1000 by default) ]
[ MUSICDATA          (immediately after the player code) ]
```

`MUSICDATA` begins exactly at `PLAYERADDR + MAX_PLAYERSIZE`, where
`MAX_PLAYERSIZE = size(extraPlayer.player)` (exporter.asm:1084) — i.e. the
data start depends on **which driver variant** was selected (bare/light/
medium/normal/extra differ in size). The per-driver end addresses live in
`altplayers.inc` as `PlrEnds[drivertype*2]` (used at exporter.asm:1180).

### Single-speed special case (framespeed == 1)
For a 1× (vblank) tune the CIA-starter code is **left out of the saved range**
and the header init/play vectors point straight into the player:

```
exporter.asm:402  ldy player.FRAME_SPD ; cpy #1 ; bne SaveDat  -> if framespeed!=1 save normally (incl. CIA code)
exporter.asm:415  lda #<PLAYERADDR     ; write load-address $1000 (skip CIA-starter)
exporter.asm:419  lda #<PLAYERADDR     ; start address = PLAYERADDR
```

---

## 2. PSID v2 header — verbatim (`SIDHEADER`, exporter.asm:1000)

`SIDHEADERSIZE = $7c`. Big-endian word fields. (Line numbers in comments.)

```asm
SIDHEADER
 .text "psid"            ;+00 magicID  ('PSID'/'RSID'; SW writes lowercase "psid")
 .byte $00,(SID_AMOUNT==1)?$02:$03 ;+04 version  (2 for mono, 3 for 2/3/4-SID)
 .byte $00,$7C           ;+06 dataOffset  ($007C, v2)
 .byte $00,$00           ;+08 loadAddress (0 => load addr is in the binary)
SIDinitadd .byte >CIAINIT,<CIAINIT  ;+0A initAddress (patched by SetSIDply)
SIDplayadd .byte >CIAPLAY,<CIAPLAY  ;+0C playAddress (patched by SetSIDply)
SIDstamount .byte $00,$01           ;+0E songs    (subtune count, set at export)
SIDdefasubt .byte $00,$01           ;+10 startSong (default subtune)
SIDtimerTyp .byte $FF,$FF,$FF,$FF   ;+12 speed (32-bit; per-tune VBI(0)/CIA(1) bits)
SIDtitletx .fill $20,0  ;+16 <title>    (32 bytes, set from author/title text)
SIDauthrtx .fill $20,0  ;+36 <author>
SIDreleatx .fill $20,0  ;+56 <released>
;--- v2 extensions ---
SIDflags .byte %00000000            ;+76 flags (hi byte)
         .byte (SID_AMOUNT==1)?%00100100:%10100100 ;+77 flags (lo)
                ; bit0 builtin player, bit1 C64-compat, bit2..3 video(01=PAL),
                ; bit4..5 SID model(00=?,01=6581,10=8580,11=both), bit6..7 SID2 model
 .byte $00              ;+78 startPage (relocStartPage)
 .byte $00              ;+79 pageLength (relocPages)
 ; (+7A reserved word, or SID2/SID3 sidAdd bytes for multi-SID builds)
;+7C => start of C64 binary data
```

Header **patch sites** (filled at export, not assembled-in):
- `SIDinitadd` / `SIDplayadd` — set by `SetSIDply` (exporter.asm:2163), see §4.
- `SIDstamount` (+0E songs) and `SIDdefasubt` (+10) — set from subtune count.
- `SIDtimerTyp` (+12 speed) — set by `SetSIDply` (all bytes 0 or all $FF), see §4.
- `SIDtitletx`/`SIDauthrtx`/`SIDreleatx` — set by `SetSIDt` (exporter.asm:2121),
  parsed from the SWM author string around a `:` separator.

> For 2/3/4-SID builds, version is **3** and the +77 flags byte sets bit7
> (`%10100100`) plus per-chip model nibbles + the `SID2sidAdd`/`SID3sidAdd`
> bytes at +7A (`(defaultSID2BASE-$d000)/16`). Mono builds use the +7A word as
> the reserved `$00,$00`.

---

## 3. CIA-starter code (multispeed only) — verbatim (exporter.asm:1036)

Lives in the $48 bytes below PLAYERADDR. Only saved when framespeed != 1.

```asm
        *= CIAINIT-2
CIAADDR .byte <CIAINIT,>CIAINIT     ; load address word (relocator leaves alone)
        *= PLAYERADDR-$48
CIAINIT ldy player.FRAME_SPD        ; A holds subtune number on entry (untouched)
p_SIDa1 ldx CiaFrameHi,y            ; CIA timer hi for this framespeed
        stx $dc05
p_SIDa2 ldx CiaFrameLo,y            ; CIA timer lo
        stx $dc04
        ldx #$00
p_SIDa3 stx frCount+1
p_SIDa4 jmp player.inisub           ; init the song (A = subtune)
CIAPLAY inc frCount+1               ; CIA IRQ entry
frCount lda #selfmod
p_SIDa5 cmp player.FRAME_SPD
        beq +
p_SIDa6 jmp player.mulpsub          ; intermediate (multispeed) tick: tables only, no new row
+       lda #0
p_SIDa7 sta frCount+1
p_SIDa8 jmp player.playsub          ; the "main" frame: full play()

CiaFrameHi .byte $99, $4c,$26,$19,$13, $0f,$0c,$0a,$09  ;[framespeed] index; [0]=half-speed
CiaFrameLo .byte $8f, $c7,$63,$97,$31, $5a,$cb,$f7,$98
```

The exporter overwrites `CiaFrameHi/Lo` (the live copy) with the PAL/NTSC/Drean
table picked by the user (exporter.asm:1066-1071):
```
CiaFrameHiPAL  .byte $99, $4c,$26,$19,$13, $0f,$0c,$0a,$09   ; framespd 1 PAL  = 312*63-1 = $4CC7
CiaFrameLoPAL  .byte $8f, $c7,$63,$97,$31, $5a,$cb,$f7,$98
CiaFrameHiNTSC .byte $85, $42,$21,$16,$10, $0d,$0b,$09,$08   ; framespd 1 NTSC = 263*65-1 = $42C6
CiaFrameLoNTSC .byte $8d, $c6,$62,$41,$b0, $5a,$20,$89,$57
CiaFrameHiDrean .byte $9e, $4f,$27,$1a,$13, $0f,$0d,$0b,$09  ; framespd 1 Drean = 312*65-1 = $4F37
CiaFrameLoDrean .byte $6f, $37,$9b,$67,$cd, $d7,$33,$50,$e6
```

Index 0 ("framespeed 0") is treated as half-speed (25/30 Hz). The formula
(per Ian Coog, comment line 1061): `((screen lines)*(cycles per line)/speed) - 1`.

**Multispeed semantics for extraction:** the CIA fires `framespeed` times per
frame. Of those, `framespeed-1` calls go to `mulpsub` (advance vibrato/PW/
filter/arp tables only, no new pattern row) and the 1 wrap call goes to
`playsub` (the real play()). So one *musical* frame == `framespeed` IRQs.
This matches the project's existing CIA-tune handling
(`siddump --writelog-per-irq`).

---

## 4. Vector & speed-flag selection — `SetSIDply` (exporter.asm:2163)

```
framespeed == 1 (single/vblank):
  SIDinitadd = player.inisub ,  SIDplayadd = player.playsub
  SIDtimerTyp[0..3] = $00            ; all subtunes = VBI timing

framespeed  > 1 (multispeed):
  SIDinitadd = CIAINIT ,  SIDplayadd = CIAPLAY
  SIDtimerTyp[0..3] = $FF            ; all subtunes = CIA timing
```

Note the speed flag is **uniform across all 32 tune bits** — SW does not mix
per-subtune timing. Detect multispeed via `speed != 0` (consistent with
CLAUDE.md's CIA-tune verdict path).

---

## 5. The data section: how `preparetunedata` builds it (exporter.asm:1144)

Order of operations (the in-source comment at 1212 says **"!!order of these
upcoming calls is important!! don't modify!"**):

1. **Copy SWM 64-byte header** into the player's `TUNE_HEADER` variable area
   (`normalPlayer.player.TUNE_HEADER`), and stash `FRAME_SPD` from
   `TUNEHEADER+FSPEEDPOS` into `player.FRAME_SPD` (exporter.asm:1147-1161).
   The header itself is then **cropped** out of the data.
2. **Move music data down** to sit right after the selected player code
   (target = `altplayers.PlrEnds[drivertype]`, exporter.asm:1180), overwriting
   the now-redundant header (exporter.asm:1170-1209).
3. `depktempo` (exporter.asm:1214) — depack/init **subtune-tempos + tempotable**,
   and set the tempo-pointer table. Tempo-program 0 is missing by convention
   (the `-1` compensation at 1216). Tempotable is shifted forward by 8 bytes
   (14 for 2SID) to make room for the subtune funktempos (`RESTEMP-TEMPOTBL`,
   1234-1248).
4. `depkinsch` (exporter.asm:1251) — depack/init **chords + instruments**.
5. **Strip instrument names + compact**: the data above the first "unnamed"
   instrument is moved up to crop the space freed by name omission; all table
   base pointers and the instrument lo/hi pointer-table entries are then
   adjusted by `relocamount` (= compzptr-decozptr) (exporter.asm:1264-1316).
6. `depkptseq` (exporter.asm:1328) — depack **patterns** and write the
   **sequence pointers** into the generated subtune section.
7. Compute `expoendadd` = end of data (exporter.asm:1330-1339). The saved range
   is `[decozptr=PLAYERADDR .. expoendadd)`.

### 5.1 Section order in the finished data (low → high address)
Driven by the ZP base pointers (next section), the compacted data section is:

```
subtuneadd  -> Subtune table  : per-subtune sequence-pointer triples (+ tempo-ptr)
                                 (sequences themselves are pointed at from here)
                Sequences      : the orderlist bytes for each track
tempotbadd  -> Tempo table     : tempo-programs (shifted +8 / +14)
tempoptadd  -> Tempo-pointer table
chordtbadd  -> Chord table
chordptadd  -> Chord-pointer table
insptloadd  -> Instrument pointer table, LO bytes  (per instrument)
inspthiadd  -> Instrument pointer table, HI bytes
                Instruments    : 16-byte base + variable wave/pulse/filter tables
                                 (names stripped)
ptnptloadd  -> Pattern pointer table, LO bytes  (per pattern)
ptnpthiadd  -> Pattern pointer table, HI bytes
                Patterns       : depacked row data
```

(Exact adjacency/ordering is set by `depktempo`/`depkinsch`/`depkptseq` +
the pointer arithmetic in `preparetunedata`; the *editor's* max-size layout in
settings.cfg §6 is a different, looser arrangement and should not be used to
parse the exported file — use the pointer tables.)

---

## 6. Zero-page pointer map (the parse handles) — `settings.cfg`

These ZP pointers are how the **player** reaches each data region, and how the
**exporter** lays them out. They are the canonical "where is each section":

```
settings.cfg:392  decozptr   = $d6  ; unpacked-data pointer (also export SAVE cursor)
settings.cfg:393  compzptr   = $d8  ; packed-data pointer (depacker cursor)
settings.cfg:396  datzptr    = $de  ; universal data pointer
settings.cfg:399  expoendadd = $e0  ; END address of data to export
settings.cfg:400  subtuneadd = $e2  ; subtune-table base
settings.cfg:401  ptnptloadd = $e4  ; pattern-pointer table, LO base
settings.cfg:402  ptnpthiadd = $e6  ; pattern-pointer table, HI base
settings.cfg:403  insptloadd = $e8  ; instrument-pointer table, LO base
settings.cfg:404  inspthiadd = $ea  ; instrument-pointer table, HI base
settings.cfg:405  chordptadd = $ec  ; chord-pointer table base
settings.cfg:406  chordtbadd = $ee  ; chord table base
settings.cfg:407  tempoptadd = $f0  ; tempo-pointer table base
settings.cfg:408  tempotbadd = $f2  ; tempo table base
settings.cfg:409  relocamount= $f4  ; 16-bit reloc delta
                  ($fe reserved for player.asm)
```

### 6.1 Editor in-memory (max-size) layout — `settings.cfg:418`
This is the *editor's* layout (constant offsets, before compaction). Useful for
upper-bound sanity, NOT for parsing the exported file:

```asm
SUBTUNES = MUSICDATA+0
PPTRLO   = SUBTUNES + (maxsubtuneamount+1)*(8*SID_AMOUNT)   ; (or *32 for 3SID)
PPTRHI   = PPTRLO  + (maxptnamount+1)
INSPTLO  = PPTRHI  + (maxptnamount+1)
INSPTHI  = INSPTLO + (maxinstamount+1)
CHDPTRLO = INSPTHI + (maxinstamount+1)
TEMPTRLO = CHDPTRLO+ (MAXCHORDAMOUNT+1)
; ... ptnlength, ptnsize caches ...
SEQUENCES   = TUNEHEADER + tuneheadersize
PATTERNS    = SEQUENCES + (maxsubtuneamount+1)*(CHN_AMOUNT)*seqbound
INSTRUMENTS = align$100( RESTPTN + (maxptnamount-1)*PTNBOUND )
CHORDS      = INSTRUMENTS + (maxinstamount-1)*maxinstsize
TEMPOTBL    = CHORDS + ChordTableLen
RESTEMP     = TEMPOTBL + (2+2*CHN_AMOUNT)          ; subtune funktempos
```
with constants from `SWM-spec.src`: `maxsubtuneamount=7`, `maxptnamount=100`,
`maxinstamount=37`, `seqbound=128`, `PTNBOUND=256`, `maxinstsize=128`,
`MAXCHORDAMOUNT=64`, `ChordTableLen=256`, `MAXTEMPOPRAMOUNT=64`,
`TempoTableLen=128`, `tuneheadersize=64`, `CHN_AMOUNT=3` per SID chip.

---

## 7. How the player's absolute addresses get patched — `setplayer` + reloc tables

The player code has absolute-addressing instructions whose operands must be
filled with the runtime data-section addresses. The mechanism (player.asm
relocm segment + exporter `setplayer`, exporter.asm:1401):

- **`DataPtr` table** (player.asm:2939) — the list of player code *operand
  addresses* (`p_subt1`, `p_ptnl1`, `p_insl3`, `p_tmpt1`, `p_chdp1`, …) that
  point at music data.
- **`PtrValu` table** (player.asm:2884) — parallel table: for each `DataPtr`
  entry, `[zp_pointer_base, signed_offset]`. `$FF` offset = "subtract 1".
  Example: `p_ptnl1 -> ptnptloadd,0`; `p_insl3 -> insptloadd,0`;
  `p_tmpt5 -> tempotbadd,1`; `p_chdp1 -> chordptadd,0`.
- `setplayer` walks both via `PlrDatP[drivertype]`/`PlrValP[drivertype]`
  (driver-specific copies in `altplayers.inc`) and writes
  `operand = zp_pointer_value + offset` into the player's instruction operands
  (exporter.asm:1417-1445).
- When **subtune-support is off**, the `p_seqtX` operands are first turned from
  "pointer-to-pointer" into direct sequence pointers (exporter.asm:1447-1471).

**Extraction implication:** to find each data region in an exported SID without
the SWM header, disassemble the player and read the operands at the
`p_*` sites, *or* (more robustly) reconstruct the ZP pointer values — they
satisfy the §6 relationships and the §5.1 section order. The `DataPtr`/`PtrValu`
pairing is the ground-truth "operand ↔ section" map.

---

## 8. Relocation — `relocator` (exporter.asm:2207)

Only runs when the user picks a relocation address != `PLAYERADDR` and the
output is not the standalone EXE:
- `relocdiff = relocaddr - >PLAYERADDR` (page delta).
- Adjusts the pattern/instrument/chord/tempo pointer **tables**, the subtune
  sequence pointers, and the player's own internal absolute addresses (via the
  `reloctable` generated by Soci's twice-compile diff macro, player.asm:2993).
- `CIAADDR`/`LOADADDR` words are deliberately **not** relocated.
- `unrelocate` (exporter.asm:2414) reverses it after save (each export gets a
  fresh player copy).

HVSC `SidWizard_V1.x` tunes are overwhelmingly at `$1000`; expect occasional
relocated bases. The data-section internal pointer tables are absolute, so a
relocated tune just shifts every `p_*` operand and every pointer-table entry by
`relocdiff` pages.

---

## 9. Export-type matrix (`setexport1`/`outputformat`)

`outputformat` selects the container (exporter.asm:269+):
- `0` C64 PRG (load-address prepended)
- `1` C64 RAW/BIN (no load address)
- `2` EXEcutable standalone (BASIC `$0801` SYS stub; no relocation needed)
- `3` SID file (PSID header + data) ← **the HVSC form we extract**

Driver variant (bare/light/medium/normal/extra) is `TUNE_HEADER+DRIVERTYPE_POS`
(SWM header offset $13); it selects `MAX_PLAYERSIZE`, `PlrEnds`, `PlrDatP`,
`PlrValP` from `altplayers.inc`. SID_AMOUNT (1/2/3/4) is a compile-time build of
the whole exporter (`SID-Wizard`, `-2SID`, `-3SID` apps), not a per-tune flag.

---

## 10. Quick reference — offsets the extractor needs

| Thing | Where | Value |
|---|---|---|
| PSID header size | exporter.asm:998 | `$7C` (124) |
| Player load base | settings.cfg:31 | `$1000` (relocatable) |
| Data start | exporter.asm:1091 | `PLAYERADDR + MAX_PLAYERSIZE` (driver-dependent) |
| CIA starter base | exporter.asm:1040 | `PLAYERADDR-$48` (multispeed only) |
| init vector | header +0A | `inisub` (1×) or `CIAINIT` (multi) |
| play vector | header +0C | `playsub` (1×) or `CIAPLAY` (multi) |
| speed bits | header +12 | all `$00` (VBI) or all `$FF` (CIA) |
| Subtune base ptr | ZP `$E2` | subtuneadd |
| Pattern ptr tables | ZP `$E4`/`$E6` | ptnptlo/hi add |
| Instrument ptr tables | ZP `$E8`/`$EA` | insptlo/hi add |
| Chord ptr / table | ZP `$EC`/`$EE` | chordpt/chordtb add |
| Tempo ptr / table | ZP `$F0`/`$F2` | tempopt/tempotb add |
