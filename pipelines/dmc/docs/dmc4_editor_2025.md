---
source_url: https://csdb.dk/release/?id=251057 (1.1), https://csdb.dk/release/?id=250645 (1.0), https://csdb.dk/getinternalfile.php/267129/dmc4editor11_win64.zip (ReadMe), https://www.lemon64.com/forum/viewtopic.php?t=86611 (via Wayback 20250823134612)
fetched_via: direct
fetch_date: 2026-06-12
author: Logan/Slackers (editor); compiled by research agent
content_date: 2025-03
reliability: secondary (NO source code or written format spec found; closed-source Windows binary. Primary artifacts captured: official ReadMe.txt 1.0+1.1 verbatim, binary string analysis of dmc4editor.exe 1.1, CSDb release pages, Lemon64 thread)
---

# DMC 4 Editor 1.0 / 1.1 by Logan/Slackers (March 2025)

Modern Windows (wxWidgets + PortAudio + embedded libsidplayfp/ReSIDfp) editor
for the C64 **DMC (Demo Music Creator)** format. "Editor by Logan, DMC Player
by Brian/Graffity" (from the exe's About box). Internal project name:
**dmcproxy** (PDB path `E:\Projects\VS2022\dmcproxy\x64\Release\dmc4editor.pdb`).

## Verdict on the research goal

- **No public source code.** No GitHub/GitLab/Codeberg repo for "dmc4editor"
  or "dmcproxy" exists as of 2026-06-12. The zips ship only the exe + DLLs +
  ReadMe.txt. The CSDb pages, comments, and the Lemon64 thread contain no
  source/spec link. The editor is the work of Logan (Slackers) with player
  code credited to Brian (Graffity, The Imperium Arts) — i.e. it embeds the
  ORIGINAL 6502 DMC player (Brian credited as co-coder), almost certainly
  driving it through emulation ("proxy" = GUI proxied onto the real player).
- **No written format documentation ships with it.** The ReadMe points to
  Richard/TND's tutorial for format/usage details:
  https://tnd64.unikat.sk/music_scene.html (already a reference in
  `research.md`).
- Still format-gold indirectly: the binary's UI strings confirm the V4
  track/sector/sound/filter data model (below), and the editor itself is a
  reference implementation we can diff against (import → export PRG round
  trips through the real format).

## Releases

| Version | CSDb id | Date | Downloads |
|---|---|---|---|
| DMC 4 Editor 1.0 | 250645 | 2025-03-03 | win64: getinternalfile.php/266649, win32: 266648, winxp: 266662 |
| DMC 4 Editor 1.1 | 251057 | 2025-03-15 | win64: getinternalfile.php/267129, win32(xp): 267130 |

Mirror: http://ftp.pokefinder.org/index.php?s=DMC%204%20Editor
Zip contents (1.1 win64): `dmc4editor.exe`, `portaudio_x64.dll`,
`wxbase32u_vc14x_x64.dll`, `wxmsw32u_core_vc14x_x64.dll`, `config.ini`
(window geometry only), `ReadMe.txt`. Local copies of both zips + extracted
ReadMes in `tmp/dmc_research/` (gitignored).

## Format-relevant facts from the binary (strings analysis, exe 1.1 x64)

### Supported player versions / import

- Two player classes compiled in: **`PlayerDmc4`** and **`PlayerDmc7`**
  (RTTI: `.?AVPlayerDmc4@@`, `.?AVPlayerDmc7@@`); UI strings
  `DMC Player 4.0`, `DMC Player 7.0`, `Undefined`. Richard/TND (Lemon64):
  import works for tunes composed with **DMC V4.0, V7.0A, V7.0B** — i.e. the
  V7 branch is data-compatible with V4 (V7 reused V4's player code; matches
  research.md's lineage note).
- Import accepts **.prg and .sid** (`c64 prg / sid music (*.prg;*.sid)`).
  Embeds a full SidTune loader (libsidplayfp strings: PSID driver,
  MUS/MUS+STR, "Bad reloc data", etc.) and ReSIDfp 6581/8580 emulation for
  playback — playback is real-player-under-emulation, not a reimplementation.
- Export: **PRG with music relocator** ("Choose music load address") and
  editable **music word message/credits** (the text block embedded in DMC
  modules). Native project format **`.dmcProj`**; sound-bank exchange format
  **`.dmcSnd`** ("Import/Export DMC sounds...", select sounds to export,
  "Auto place req. filter in unused filter slot" — i.e. a sound references a
  filter program by number, and bank import remaps/auto-places the required
  filter).
- **DMC Tune Seeker**: scans a directory (e.g. HVSC) of .sid/.prg files and
  detects DMC 4.x tunes ("DMC 4.x Tune Seeker"); results cached to a text
  file. Confirms DMC 4/7 modules are reliably fingerprintable inside SID
  wrappers (useful precedent for our own DB classification).
- Playback speeds: Normal / Double / Tripple / Quatro / Quintuple
  (1x–5x multispeed support; Jammer's CSDb comment claims 6x also works).

### Track (orderlist) entry vocabulary (display format strings)

```
%.2X: ...%.2X    sector number
%.2X: TR-%.2X    transpose down
%.2X: TR+%.2X    transpose up
%.2X: -END-      end of track
%.2X: STOP!      stop
```
Keyboard: `-` inserts TR-00, `=` inserts TR+00.

### Sector (pattern) entry vocabulary

```
%.2X:  %s%d      note name + octave (octaves 0-7)
%.2X: SND.%.2X   instrument ("sound") select
%.2X: DUR.%.2X   duration set
%.2X: GLD.%.2X   glide/portamento
%.2X: VOL.%.2X   volume
%.2X: SWITCH     switch command
%.2X: -GATE-     gate control
%.2X: ------     empty/rest row
%.2X: -END!-     end of sector
```
Matches the duration-based (not tick-based) model: sectors are arbitrary
length, voices unsynchronised (confirmed by Tobias in the Lemon64 thread:
"DMC uses duration based patterns, they can be any length, no syncing is
done at all... you are not limited to one or two commands per tick and
triplets can be done way easier"). 1.1 added a per-sector **Duration**
display specifically to help manual cross-voice sync.

### Sound (instrument) editor flag names

Per-sound attribute strings (these name the bits/fields of the 11-byte V4
instrument record documented in `research.md`):

```
DRUM EFFECT   NO GATE FX    HOLDING FX   NO FILT RES
NO PULS RES   CYMBAL FX     FILTER FX    DUAL EFFECT
Req Filter    FILTER FX
```

Each sound has: a name (editor-side, 1.1 feature — NOT in the C64 format),
a **wave table** (own editor screen, entered at the sound's `##` position
→ table position is a sound field), and an optional **filter program**
reference ("Req Filter", filter editor with numbered filters,
"No more free filters!" on bank import).

### Editors present

Track Editor, Sector Editor, Sound Editor (+ wave table sub-editor),
Filter Editor, Tune Seeker. Status bar: `F1 = Play | F3 = Stop | F5 =
Pause | Space = Play from track cursor position`. Also "Music message:"
(the credits text stored in the module).

## Official ReadMe.txt (1.1) — changelog section, verbatim

```
Changelog for 1.1
- Import Music -> read and display the music word message/credits
- Export PRG -> added music relocator/ you can change/save music words message/credits
- Sector Editor -> added Octave Up/Down (for selection or from cursor position) and Voice on/off in popup menu
- Sector Editor -> Display Sector Duration useful for sync between tracks
- Sound Editor -> you can put/change names of sounds
- Added View menu where you can select larger fonts for track/sector/sound editors
- Added Sound menu where you can import/export sounds banks
- Track Editor -> added ability to play from any selected track position by pressing "space"
- Track Editor -> Display music time and current playing pos of tracks/sectors
- Fixed many minor bugs
```

(Full ReadMe key-binding reference preserved at
`tmp/dmc_research/win64/ReadMe.txt`; 1.0's ReadMe is identical minus the
changelog. Both end with: "The more details about using the 'Real' DMC4 can
be found here: https://tnd64.unikat.sk/music_scene.html".)

## Community discussion (no format details beyond the above)

- CSDb 1.0 comments: Richard ("My favourite music composer DMC V4 springing
  back to life"), Jammer ("And 6x speed! At least!"), psych ("go and make a
  full DMC version with all these nice/new and very much needed features"),
  Comos (XP build request — granted in 1.1's win32 build). Video links:
  https://www.youtube.com/watch?v=uPdxCpUFnSc and
  https://www.youtube.com/watch?v=a-BgREkkjcg
- CSDb 1.1 comments: only praise (Yogibear, Apprentix) + Logan's changelog.
- Lemon64 thread "DMC V4 is back in 2025" (t=86611, 5 posts, fetched via
  Wayback — Lemon64 itself is in maintenance mode 2026-06): Richard/TND
  announcement (feature list, V4.0/V7.0A/V7.0B import), Jeanluc asking how
  patterns sync, Tobias explaining the duration-based no-sync model. Logan
  did not post; no source-code mention anywhere.
