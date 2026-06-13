# Music Assembler — Markt & Technik 1990 editor disk (Archive.org)

> **Provenance**
> - source_url: https://archive.org/details/d64_Music_Assembler_1990_Markt_Technik
> - disk image download: https://ia600608.us.archive.org/9/items/d64_Music_Assembler_1990_Markt_Technik/Music_Assembler_1990_Markt__Technik.d64
> - fetched_via: direct (archive.org metadata API + file download)
> - fetch_date: 2026-06-13
> - author / publisher: Marco Swagerman (MC) & Oscar Giesen (OPM); published by Markt & Technik (German edition, dated 1990)
> - content_date: 1989–1990
> - reliability: HIGH — primary artifact. The actual commercial editor binary, the
>   single most useful source for reverse-engineering the player + packer. D64
>   verified to parse and the embedded player matches the canonical HVSC fingerprint.

## What this item is

The **commercial Markt & Technik release of Music Assembler** as a 35-track D64
floppy image. This is the editor itself (the program a composer ran on a C64 to
create `s.`/`p.` files), saved locally as `masm_editor_1990.d64` in this dir.

- Uploader: "Sketch the Cow" (an Internet Archive bulk C64-software uploader),
  2021-03-10. Collections: *Software Library: C64 Applications*.
- Item size 4.6 MB (mostly emulator screenshots + a GIF); the only payload that
  matters is the D64.

## D64 contents (parsed directly, no c1541 needed)

```
Disk name : "DIGITAL DUNGEON "   ID: "98"   DOS: "2A"
Directory : 1 entry
  PRG  T19/S0   "O-MUSICASSEMBLER"   (chain length 14300 bytes)
BAM allocation: only tracks 18-21 used (1 dir + 1 BAM + 57 data sectors)
```

Notes:
- The disk header name ("DIGITAL DUNGEON") is from whatever disk the dumper
  re-used; it is **not** an MA artifact. Ignore it.
- The directory entry shows "0 blocks" — a cosmetic quirk of this dump's dir
  entry; the file's sector chain (starting T19/S0) is intact and yields a clean
  14300-byte program.
- The `O-` filename prefix is the MA convention for the editor program itself
  (composer song/preset files use the `s.`/`p.` prefixes documented in the
  manual). Only one file is on the disk: the editor.

## Extracted program

Saved here as `masm_editor_1990_OMUSICASSEMBLER.prg`.

- Load address **$0801** (BASIC program area). First payload bytes are a BASIC
  stub: `0B 08 4B 43 9E 32 30 35 39 00` = line that does `SYS 2059` (`$080B`),
  i.e. the editor cold-starts via a one-line BASIC loader.
- End address **$3FDB**. So the editor occupies roughly $0801–$3FDB (~14 KB).
- This blob contains **both** the editor UI/data-model code **and** the player
  routine template + the assembler/packer that turns the edited tables into the
  packed `s.` stream. That packer is the open RE target (see
  `archive_player_writemodel.md`).

### Why the player is not byte-identical to a saved SID

The player template inside the editor uses the editor's own working addresses;
on save, MA **relocates + assembles** the player to the user-chosen base. So a
verbatim byte-search for a saved SID's player code inside the editor PRG
**fails** (confirmed: the $3091 per-voice routine from a saved tune is not found
literally in the editor blob). To recover the template you must trace the
packer's relocation pass, OR (much easier) just disassemble the player out of an
already-saved HVSC SID, which IS the final relocated form. The latter is what
`archive_player_writemodel.md` does.

## How to re-extract from the D64 (Python, no external tools)

Standard 35-track 1541 geometry; follow the sector chain from the directory
entry's (track, sector). The repo has no `c1541`/VICE, so a ~20-line Python D64
walker (sectors-per-track table `21*17, 19*7, 18*6, 17*10`; each sector =
2 link bytes + 254 data) is sufficient. Disk name/ID live in the BAM at
track 18 sector 0 (offset $90 / $A2).

## Leads embedded in this item

- The editor binary is the authoritative source for the **packer/assembler**
  (the "intricate unreadable data" generator the manual brags about). RE the
  save path here to fully specify the packed `s.` format.
- The `p.` (presets-only) file format can likewise be recovered from the
  editor's disk-save code.
