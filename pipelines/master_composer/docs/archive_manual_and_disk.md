# Master Composer — Archive.org disk image, editor screenshots & manual search

Provenance
- source_url (disk item): https://archive.org/details/d64_Master_Composer_v1.0_19xx_Playboy
- source_url (metadata API): https://archive.org/metadata/d64_Master_Composer_v1.0_19xx_Playboy
- source_url (Music Software Guide): https://archive.org/stream/commodore-64-and-128-music-software-guide/Commodore64And128MusicSoftwareGuide_djvu.txt
- source_url (manual question): https://www.lemon64.com/forum/viewtopic.php?t=55611
- fetched_via: "direct" (archive.org metadata API + file downloads via curl; Music Software Guide djvu via WebFetch);
  the Lemon64 thread via "wayback 2023-04-30" (lemon64.com was in site-wide maintenance mode on fetch day)
- fetch_date: 2026-06-13
- author/handle: disk image uploaded by "Sketch the Cow" (sketch@cow.net, Internet Archive staff); cracked release by group "Playboy" / intro "BIER FRONT"; Music Software Guide is a published reference book; Lemon64 posters Link6415 + Hidron
- content_date: disk item added 2021-03-10 (preserves an ~1983/84 program); Music Software Guide ~1985/86; Lemon64 thread 2015-03-15/16
- reliability: HIGH for the disk image + screenshots (a real, runnable D64 with emulator-captured UI) and the Music Software Guide vendor listing (published, contemporaneous); MEDIUM for the crack-intro screens (cosmetic, not the program). No scanned printed MANUAL was found anywhere in this cluster.

---

## A. The editor disk image (primary artefact)

**`d64_Master_Composer_v1.0_19xx_Playboy`** — a working Commodore 64 disk image of
**Master Composer v1.0**, cracked by group **Playboy** (crack intro screen reads "BIER FRONT
PRESENTS"). This is the only Master Composer EDITOR (as opposed to ripped tunes) found in the
archive.org software library.

- File: `Master_Composer_v1.0_19xx_Playboy.d64` — **174 848 bytes** = standard 35-track,
  single-sided .d64 (683 × 256). Matches preservation64's "5.25 DSDD, 1 disk, side 1 empty"
  (see `archive_provenance_preservation.md`): only side 0 carries the program.
- Emulator: `vice-resid` (reSID). Collections: `softwarelibrary_c64_applications`,
  `softwarelibrary_c64`, `emulation`. Added 2021-03-10.
- 29 emulator screenshots (`screenshot_00.png`…`screenshot_28.png`) — these are the de-facto
  visual documentation of the program (see §C). Screens 01–05 are the Playboy crack intro;
  06/10/20 (and the bulk of 07–28) are the live editor.
- **NOT downloaded into the repo** (binary, outside docs scope). To pull for analysis later:
  `curl -L https://archive.org/download/d64_Master_Composer_v1.0_19xx_Playboy/Master_Composer_v1.0_19xx_Playboy.d64`

A second editor disk image exists on **CSDb** (release #128699): `Master_Composer-MST.d64`,
cracked by group **MST**. A user comment there notes it is "the only Master Composer crack I can
find that has a working **Dealer Demo**" — i.e. the original retail disk shipped with a
dealer/showroom demo mode, and most cracks broke it. (CSDb getinternalfile URL recorded in
`archive_provenance_preservation.md`.)

## B. The printed manual — search result: NOT FOUND (negative result, documented)

- No scanned Master Composer manual/box/advertisement PDF exists on Internet Archive. The
  archive.org full-text (`mediatype:texts`) search for `"master composer"` returns only sheet-music
  indexes and jazz books — zero C64 hits. The `subject:"Access Software"` text search likewise
  yields nothing relevant. Access Software's own 1984 magazine ads (Compute!/Ahoy!/RUN) are not
  indexed under that phrase.
- The **Lemon64 thread "Master composer manual scan?"** (2015) confirms the same: the asker wanted
  a manual link; the only answer was *"I can't find a manual, but it looks like you can press the
  'H' key for the help screen."* So **the in-program `H` help screen is the closest thing to a
  manual that survives** — and it lives inside the D64 above (worth dumping the help-screen text
  from the disk if format detail is needed).
- **4am preservation crack notes — checked, none for this title.** 4am's documented cracks are
  almost entirely Apple II; there is no 4am Master Composer (or Access Software C64 editor) crack
  write-up. The surviving cracks are the C64-scene ones (Playboy above; MST on CSDb). So the
  detailed-protection-write-up route (4am-style) is a dead end; the protection detail instead
  comes from preservation64 (see §D / the provenance file): **"error 5 on track 18 sector 18"**.

## C. What the editor screenshots actually show (UI model, transcribed)

The main edit screen (screenshots 06/10/20 — same screen, cursor at different positions) is a
block/track editor. Transcribed verbatim:

**Title bar:** `MASTERCOMPOSER V1.0 by PLAYBOY` (the "by PLAYBOY" is the crack tag, not the original).

**Main grid** — header row `TR  V1 St Pm Tu   V2 St Pm Tu   V3 St Pm Tu`, rows numbered `00`–`08`(+scroll):
- Leftmost column **TR** (per-row value, e.g. `0f 0f 0f 0f 14 15 16 18 15` down the rows).
- Then a 4-column group **per voice** V1 / V2 / V3, each = `(value) St Pm Tu`. Sample row 00:
  `V1: 0f 00 00 16 | V2: 0f 1c 0e 11 | V3: ff 0c 0d 00`.
- Working interpretation (to be confirmed against the binary): the four per-voice columns are the
  per-block SID-register snapshot — almost certainly **St**=waveform/control (status), **Pm**=pulse
  (PWM/pulse-width), **Tu**=tuning/transpose, with the lead column the note/sound selector. This is
  consistent with `research.md`'s "each block defines ALL SID register values for 3 voices" and with
  VGMPF's refinement that a block sets registers **except combined waves** plus tempo and a
  bar/16th range (see `forum_vgmpf_wiki.md`). The grid here is the BLOCK table being edited.

**Lower-left status/command panel** (verbatim labels + sample values):
```
Track:00   Step:0b
Begin:00   Stop:40
Play:on    Speed:04
File:------------
Typ :Whole Music
Startadress:$2000
Init:        (Y/N)
Save:$0000-$0000
```
- `Speed:04` → the VBlank tempo divider (play routine runs every 4th frame here). Directly relevant
  to per-frame write reproduction: the play() vector emits writes only every `Speed` frames.
- `Begin/Stop` (00 / 40) → the block range played (Stop:40 = 64 = the documented 64-block max).
- `Startadress:$2000` → user-chosen relocation base for the exported driver (corroborates
  "relocatable, absolute addresses adjusted at load time"; HVSC rips commonly sit at $7580 instead).
- `Typ : Whole Music` → an export-type selector (i.e. there are other export types — likely a
  data-only vs whole-driver-plus-data choice; the "Dealer Demo" from §A is a separate mode).
- `Init:(Y/N)` and `Save:$xxxx-$xxxx` → the save-to-disk dialog (emits the relocated player+data
  between the two addresses).

**Lower-right panel** — two parts:
1. A **frequency-table view** with note names, e.g.
   `$3668:9a(D-2)  00 20` / `$366b:96(A#1)  00 10` / `$366e:90(C-2) …` / `$3671:95(A-1)↑ 00 20`
   / `$3674:96(A#1) 00 10`. These are (address : freq-byte (note-name) …) rows — i.e. the live
   freq table the player indexes, shown with C64 note names. Confirms the freq table is stored as
   per-note byte values with note-name labels (the `(D-2)`,`(A#1)` octave-tagged names) and the NTSC
   tuning baseline. `Voiceno.:$0f` heads this panel (the currently-selected voice/sound number).
2. A **base-pointer block**:
   `00:$3300 $3360 $3373` / `03:$33f1 $346f $34ea` / `06:$351a $3583 $35b3`.
   Three columns × rows indexed 00/03/06 — these look like the data-region base addresses the
   player uses (three per row → plausibly the three voices' stream pointers, or table bases such
   as freq-lo/freq-hi/page-table). Note `$3360`/`$3373` line up near the `$3668` freq rows above,
   consistent with `research.md`'s freq-table region. Treat as a CONCRETE anchor to validate the
   memory map against the actual D64 when the binary is disassembled.

> These addresses are from a song loaded at `Startadress:$2000`-class layout in THIS crack; they
> are not the canonical $7580 HVSC offsets, but the RELATIVE structure (freq table → pointer block →
> block grid) is the engine's and should match after relocation.

## D. Music Software Guide — Access Software vendor listing (contemporaneous, published)

From *Commodore 64 & 128 Music Software Guide* (archive.org), Master Composer is listed twice
(Composition/Transcription and Programming Utilities), verbatim:

> "This utility program allows users to produce all types of music. By experimenting with different
> arrangements and instrument sounds, one can create both simple melodies and intricate compositions.
> The program is **interrupt driven**, so music created with it **may be added to BASIC or machine
> language programs**. Music files may also be **linked or relocated**. **Hard copies can be obtained
> with graphics-capable dot matrix printers.** $39.95. Available from ACCESS SOFTWARE."

- Vendor address (as printed): **ACCESS SOFTWARE, 2561 South 1560 West, Woods Cross, UT 84087.**
- Corroborates: interrupt-driven player; relocatable/linkable driver (the `Startadress`/`Save`
  dialog in §C); price $39.95. Adds: a **score-printing** feature (dot-matrix hardcopy) — not
  relevant to SID writes but confirms it was a full notation editor, and the on-screen display
  (§C, the note-name column) is the editable score.
- No structural (page/block/bar) or tuning detail in the Guide, and no Paul Kleimeyer mention there
  (authorship attribution comes from preservation64 + VGMPF — see the other archive_* file).

## E. Implications for the SIDfinity migration

1. **`Speed` divider is a first-class field.** The play vector emits SID writes only every `Speed`
   frames (here 04). Per-frame write reproduction must model the speed divider, not assume 1×/frame.
2. **Block grid layout is `(lead, St, Pm, Tu) × 3 voices`** — when disassembling, expect the block
   table to be (at least) four parallel per-voice columns, matching the on-screen editor, NOT one
   flat $D400-snapshot per block. The "except combined waves" VGMPF note means the waveform/control
   column never holds a combined-waveform nibble.
3. **The freq table is byte-per-note with NTSC tuning** and is indexed by a note number; the
   on-screen `(D-2)`/`(A#1)` labels are the editor's, not stored. The pointer block ($3300/$3360/…)
   is the structural anchor to verify the memory map against a real D64.
4. **Two export modes at least** (`Typ: Whole Music`, plus the "Dealer Demo") + relocation → expect
   minor header/layout variation between rips that all share the same player core.
5. **The printed manual does not survive digitally** — the authoritative usage doc is the in-disk
   `H` help screen; dump it from the D64 if exact key/command semantics are ever needed.
