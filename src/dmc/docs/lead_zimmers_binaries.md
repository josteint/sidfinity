---
source_url: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/
fetched_via: direct
fetch_date: 2026-04-11
author: unknown (archive maintained by Zimmers.net; original binaries by Brian/Graffity)
content_date: 2009-08-18 (archival migration date; original software 1991–1993)
reliability: primary
---
# DMC Editor Binaries on zimmers.net

**Source URL:** https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/

All DMC files are in the single directory `/pub/cbm/c64/audio/editors/` and nowhere else
on zimmers.net (confirmed via ALLFILES index search). No README or documentation files
accompany the DMC entries. There are no DMC files in the players/, utilities/, samples/,
or Vibrants/ subdirectories.

---

## Files Available

All files listed with date 2009-08-18 (when the archive was migrated to zimmers from
ftp.funet.fi). The date reflects the archival upload, not the original release date.

| Filename | Size (bytes) | MD5 | Notes |
|---|---|---|---|
| `demo_music_creator_v2.1db.prg` | 15,175 | f6464f7bd6e1a34fe50ee304061b0551 | v2.1, packer variant "db" |
| `demo_music_creator_v2.1qd.prg` | 15,143 | aac3558ad0dfe54d4a2afa469536a520 | v2.1, packer variant "qd" |
| `demo_music_creator_v4.0qu.prg` | 14,039 | c4c1d36f8c19b6784a606df263d4d5ff | v4.0, packer variant "qu" |
| `demo_music_creator_v4.0sx.prg` | 13,878 | 734e517c1d144bb00a5511c80e0fda67 | v4.0, packer variant "sx" |
| `DMC-v4.0.prg` | 13,878 | 734e517c1d144bb00a5511c80e0fda67 | IDENTICAL to v4.0sx above |
| `dmc4.0.prg` | 12,357 | 09bdc1eb028879b5a76fedc189129e30 | v4.0, different structure |

zimmers directory description for `dmc4.0.prg`: "DemoMusicComposer Version 4.0. Great thing."
`DMC-v4.0.prg` has no directory description. The v2 and other v4 files have no descriptions.

All downloaded to: `/home/jtr/sidfinity/src/dmc/binaries/`

---

## File Identity and Deduplication

- `DMC-v4.0.prg` and `demo_music_creator_v4.0sx.prg` are **byte-for-byte identical**
  (same MD5). Two names for the same file.
- `demo_music_creator_v2.1db.prg` and `demo_music_creator_v2.1qd.prg` are different
  compressions of the same program (32-byte size difference, 14,817 differing bytes out
  of 15,143 compared — typical of same source packed with two packer variants). Both share
  identical first 25 bytes and last 59 bytes (packer header/footer signature).
- `demo_music_creator_v4.0qu.prg` and `demo_music_creator_v4.0sx.prg` are also different
  compressions of the same v4.0 source (161-byte size difference, nearly all bytes differ).

So there are **three distinct program binaries**:
1. DMC v2.1 (represented by the two "db" and "qd" packed variants)
2. DMC v4.0 as packed editor (represented by the "qu" and "sx" packed variants, the "sx"
   also being called "DMC-v4.0.prg")
3. `dmc4.0.prg` — a separate v4.0 build with a different structure (see below)

---

## Binary Structure Analysis

All files load at `$0801` (standard C64 BASIC program start address).

### v2 and v4 "packed" variants (5 files excluding dmc4.0.prg)

BASIC stub at `$0801`:
```
$0801: 0C 08   ; ptr to next BASIC line = $080C
$0803: C9 07   ; line number 1993
$0805: 9E      ; SYS token
$0806: FF      ; pi character (non-standard — packer trick)
$0807: AC      ; PEEK token in C64 BASIC v2
$0808: 36 35 36 ; ASCII "656" ($0290 = C64 auto-start vector)
$080B: 00      ; end of BASIC line
$080C: A0 00   ; start of machine-code decompressor (LDY #$00)
```

The `SYS pi PEEK(656)` BASIC line is a known cruncher/packer trick — the BASIC
tokenizer evaluates this as a numeric expression but the actual execution jumps
into `$080C` (the decompressor) via the packer's own mechanism. This is NOT a
valid SYS call; the packer overwrites BASIC's execution path.

The "db", "qd", "qu", "sx" suffixes in the filenames are conventional abbreviations
for the C64 packer/cruncher used (e.g., "db" = DataBanker, "sx" = some other
compressor). The compressed content is identical source code packed differently.

### dmc4.0.prg — different structure

Has a clean BASIC stub:
```
$0801: 0B 08   ; ptr to next BASIC line = $080B
$0803: C5 07   ; line number 1989
$0805: 9E 32 30 36 31 00  ; SYS 2061 (= $080D) — clean SYS call
$080B: 00 00   ; end of BASIC program
$080D:          ; machine code entry point
```

This is likely the **unpacked/original** version of the editor — it is 12,357 bytes
versus 13,878–15,175 bytes for the packed variants. The packed variants are larger
because they include a decompressor stub and compress to a smaller runtime footprint,
but the on-disk .prg is larger.

Entry code at `$080D`:
```
A9 8C A0 08   ; LDA #$8C / LDY #$08  -> set IRQ vector to $088C
20 1E AB      ; JSR $AB1E  (KERNAL: output message)
A9 00         ; LDA #$00
8D 20 D0      ; STA $D020  (border color = black)
8D 21 D0      ; STA $D021  (background color = black)
...
```

The IRQ handler at `$088C` is the main editor/player interrupt. A `CODE:` string is
visible at `$088F` in this build, suggesting the editor has a keyboard input mode.

Load range for `dmc4.0.prg`: `$0801`–`$3844` (14,656 addresses, 12,355 bytes of content).

---

## Player String Evidence

In `demo_music_creator_v4.0sx.prg` (and its identical copy `DMC-v4.0.prg`), after
decompression the binary contains the player identifier string:

```
$3987: "DMC'S PLAYER1"
```

This matches SIDId's signature for DMC v4 players in HVSC SID files. The `1` suffix
likely indicates player variant 1 (there may be variant 2 for the relocated standalone
player).

---

## Comparison with HVSC DMC SIDs

The HVSC collection contains ~10,738 DMC SIDs. The player code embedded in those SID
files comes from the DMC editor's player routine — the standalone relocatable player
extracted from the editor and relocated to a SID-compatible load address.

The `dmc4.0.prg` file (unpacked, load `$0801`) contains the editor + embedded player.
The player routine starting at `$088C` is the IRQ handler that drives the music engine.
When SID files are created from DMC, this player is extracted and relocated.

The player in HVSC SIDs identified as "v4" corresponds to `DMC'S PLAYER1` at `$3987`
in the sx/v4.0 packed variant. The `dmc_parser.py` v4 detection signature
(`FE ?? ?? BD ?? ?? 18 7D ?? ?? 9D`) should be findable in the unpacked dmc4.0.prg
binary.

---

## What Is NOT Available on zimmers.net

- No DMC v3.x files
- No DMC v5.x or v6.x files (those are later, possibly never archived here)
- No source code for DMC
- No documentation or manual for DMC
- No disk image (.d64) containing DMC with demo songs
- No standalone player files (only the editor, which contains the player internally)
- No "v2.0" or earlier versions — only v2.1 and v4.0

For v5/v6 documentation and later versions, see the other leads files in this directory.
