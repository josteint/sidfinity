<!--
provenance:
  source_url: "local: tmp/dmc_hunt/DeepSID/{php/pretty_player_names.php, utility/python/specific/*.py, utility/howto_update_hvsc.txt, php/_update/special_updating.sql, tags.htm} + web: deepsid.chordian.net, csdb.dk/release/?id=59929, vgmpf.com/Wiki/Soundmonitor, en.wikipedia.org/wiki/Chris_Huelsbeck"
  fetched_via: "local read + direct web fetch/search"
  fetch_date: 2026-06-13
  author: "DeepSID by Jens-Christian Huus (Chordian); SoundMonitor by Chris Hülsbeck; Rockmonitor by Dutch USA Team"
  content_date: "DeepSID checkout ~2023-2024; CSDb/Wikipedia/VGMPF contemporary"
  reliability: "HIGH for the DeepSID naming pipeline (read directly from DeepSID's own source scripts); HIGH for version/provenance history (multiple independent web sources agree); MEDIUM for exact per-variant HVSC counts (not enumerable locally — see notes)."
-->

# Soundmonitor — DeepSID player-name taxonomy & version history

This documents (a) what player string DeepSID shows for Soundmonitor-family
tunes and how it is derived, and (b) the version/variant history from the
authoritative web sources. The raw sidid byte-signatures are in
`sidid_signatures.md`.

## 1. How DeepSID derives the player name (the actual pipeline)

DeepSID does NOT hand-tag players. Its `files.player` column is generated from
`sidid`, in two passes (verbatim from `DeepSID/utility/howto_update_hvsc.txt`):

1. **General pass** — `sidid > sidid_100_simple.csv` over the whole HVSC. This
   emits the COARSE primary player name. Soundmonitor-family tunes get
   `Soundmonitor` here. (Lines 111-156 of the howto: parse CSV → import into a
   `files_import` table → `UPDATE files SET files.player = files_import.player`.)

2. **Specific pass** — `sidid -m > _specific.csv` (the `-m` flag makes sidid
   report ALL matches, including the parenthesised `(Variant)` sub-labels).
   Then `python/specific/_process.bat` runs a per-family Python script that
   slices the `(Variant)` out and rewrites the player name to the FINE-grained
   value (lines 158-198). These fine names OVERRIDE the coarse ones.

The `_process.bat` driver runs these family scripts that touch the
Soundmonitor block:
`beatbox.py, digimonitor.py, digitronix.py, drummaker.py, dusat_rockmon.py,
karl_xii.py, musicmaster.py, red_packed.py, syndicate_bb.py`.

### Naming convention produced by each script
Each script reads `_specific.csv`, finds lines containing its tag, and writes
`collection_path,player` rows. Two conventions emerge (THIS is the taxonomy
nuance):

| Script | Match tag | Player name written |
|---|---|---|
| `musicmaster.py` | `(MusicMaster_` | `SoundMonitor/<MusicMaster_1\|_2\|_TMM>` |
| `beatbox.py` | `(BeatBox` | `SoundMonitor/BeatBox…` |
| `karl_xii.py` | `(Karl_XII` | `SoundMonitor/Karl_XII…` |
| `digitronix.py` | `(Digitronix` | `SoundMonitor/Digitronix` |
| `drummaker.py` | `(DrumMaker` | `SoundMonitor/DrumMaker2` |
| `red_packed.py` | `(ReD_Packed` | `SoundMonitor/ReD_Packed` |
| `syndicate_bb.py` | `(Syndicate` | `SoundMonitor/Syndicate…` |
| `dusat_rockmon.py` | `(DUSAT` | **`DUSAT/RockMon…`** (NO `SoundMonitor/` prefix) |
| `digimonitor.py` | `(DigiMonitor` | **`DigiMonitor`** (NO `SoundMonitor/` prefix) |

So in DeepSID's player tree:
- **Most variants are shown nested as `SoundMonitor/<Variant>`** (e.g. a tune
  detected as MusicMaster_1 shows player `SoundMonitor/MusicMaster_1`).
- **Rockmonitor is shown as a SIBLING `DUSAT/RockMon2..5.1`** (the
  `dusat_rockmon.py` script deliberately omits the `SoundMonitor/` prefix), and
  **DigiMonitor as bare `DigiMonitor`**. This is purely a display choice in the
  post-processor; sidid still groups them in the one `Soundmonitor` cfg block.

The exact per-row logic (from `musicmaster.py`, representative):
```python
if '(MusicMaster_' in line:
    writer.writerow([
        '_High Voltage SID Collection/' + prev_line[0:prev_line.find('.sid')+4],
        'SoundMonitor/' + line[line.find('(')+1 : line.find(')')]
    ])
```
(`prev_line` = the SID path line, `line` = the `(Variant)` line that sidid
prints right after it under `-m`.)

### The coarse base name → pretty string
`DeepSID/php/pretty_player_names.php:46`:
```php
'Chris_Huelsbeck' => 'Chris Hülsbeck\'s player',
```
There is NO pretty-name entry for `Soundmonitor` itself, so DeepSID shows the
raw `SoundMonitor/<Variant>` string in the player factoid. The only pretty
rewrite in this family is `Chris_Huelsbeck` → "Chris Hülsbeck's player".

### Live site confirmation
`deepsid.chordian.net` renders the player name client-side (browser.js,
factoid system), so it is not in the static HTML; the canonical example tune
is `MUSICIANS/H/Huelsbeck_Chris/Shades.sid`. The DeepSID `browser.js:538`
hard-routes a "Chris Hülsbeck" link to `MUSICIANS/H/Huelsbeck_Chris`.
`special_updating.sql` carries manual copyright fixes for Huelsbeck_Chris tunes
(Bugbomber→1991, Metro_Dance→1988). `tags.htm:250` warns curators not to slap a
"Digi" tag on "a SoundMonitor spin-off with digi tracks added" — confirming the
many `*_Digi` / sample-capable spin-offs in the cfg are a known DeepSID concern.

## 2. Version / variant history (web-sourced, cross-checked)

### SoundMonitor (the editor) — Chris Hülsbeck
- **MusicMaster** is the *driver*, written FIRST (1985, in Profi-Ass 64;
  Hülsbeck composed in raw hex). **SoundMonitor is the EDITOR** he wrote in
  summer 1986 on top of MusicMaster because hand-hexing was tedious. (Wikipedia
  "Soundmonitor"/"Chris Huelsbeck"; VGMPF.) → In sidid terms: the `MusicMaster_*`
  sub-names ARE the replay driver; the bare `Soundmonitor` name is the
  editor-embedded replay.
- Released as a **type-in hex listing in 64'er magazine 10/1986** (Markt &
  Technik). VGMPF dates the release **September 19, 1986**; CSDb release
  **#59929 "Soundmonitor V1.0"** dates it **October 1986**. ("Sound Monitor 1.0".)
- Known editor versions (Wikipedia/c64-wiki): **V1.0 (1986)**, **V1.1 (1986)**,
  **V1.3 (1987)**. Effects supported (a first for an editor): transpose,
  detune, portamento, vibrato, PWM, filter modulation, arpeggio.
- **"The (Final) Musicplayer"** — an optimised driver variant Hülsbeck made
  throughout 1987, per VGMPF "given only to Georg Brandt". This is the
  `MusicMaster_TMM` sidid sub-name (TMM = The MusicPlayer).
- Canonical HVSC tune: `Huelsbeck_Chris/Shades.sid` — "Shades (filter
  corrected)" © 1986 Markt & Technik (jc64 List.txt).

### Rockmonitor — Dutch USA Team (DUSAT)
- The best-known **unofficial** derivative; same keyboard operation, **adds
  sample (digi) playback** — to Hülsbeck's annoyance at the time. First
  appeared **April 1987**. (Wikipedia/c64-wiki.)
- sidid distinguishes **RockMon2, 3, 3h, 4, 5.0, 5.1** (the "h" = a hacked/alt
  build of v3; 5.0 vs 5.1 differ only in the init shadow-table page byte
  `$AE`→`$B0`). jc64 List.txt cites:
  - "Rockmonitor 2" by **Marco Swagerman & Oscar Giesen** © 1987 Dutch USA Team
  - "Rockmonitor 5 Demosong" by **Oscar Giesen (OPM)** © 1988 Dutch USA Team
- RockMon5.x has a distinct init (clears `$D404/$D40B/$D412` voice-control regs
  explicitly before the bulk `99 00 D4` clear) — see `sidid_signatures.md` §6.

### Other family members (scene derivatives, all in the same cfg block)
- **Karl_XII / BeatBox** — Karl XII (scene musician) Rockmonitor-derived player + a BeatBox build.
- **DrumMaker2** — MusicMaster_2 base with an added `JSR $CC60` drum routine.
- **JamMasterV1**, **Digitronix**, **Syndicate/BB** (CIA2 `$DD04/$DD05`
  table-driven), **Novotrade**, **ReD_Packed** (a packer wrapper).
- **Digi spin-offs**: `DigiMonitor`, `Cavi_Digi`, `Mahoney_Digi`,
  `Huelsbeck_Digi_V1`, `Huelsbeck_Digi_V2` — sample/4-bit-volume `$D418`
  playback bolted onto the SoundMonitor core.

## 3. Population & relocation (from `hvsc84.db`, read-only)

| Engine label | HVSC #84 count |
|---|---|
| `Soundmonitor` (coarse, all variants combined) | **3,625** |
| `Chris_Huelsbeck` (separate hand driver) | **11** |

- All 3,625 are PSID **v2**; `load_addr=$0000` (PSID-embedded PRG load).
- Dominant entry config `init=$C000 play=$C020` (1,182) = the textbook
  MusicMaster replayer (`SYS 49152`). 1,301 have `play=$0000`. `play=$C475`
  (478) is a second common build. init origins are spread across
  `$C000/$9FD0/$CBD4/$BFF0/$80F8/$9FFA/$CE3x/$7FF8/$9E00/…` → relocated per
  release (the reason sidid wildcards every absolute address).
- **The per-variant (RockMon vs MusicMaster vs …) breakdown is NOT in
  `hvsc84.db`** — the DB stores only the coarse sidid name. The split exists
  only in DeepSID's `sidid -m` `_specific.csv` post-pass, and no built
  `_specific.csv`/`*.csv` is present in the local DeepSID checkout (the
  `python/specific/*.py` scripts are present but their input/output CSVs are
  not). Reproducing it needs a `sidid -m` run over HVSC.

## Leads to follow
- To get RockMon/MusicMaster/Karl_XII/etc. per-variant HVSC counts: build the
  `sidid` 100-char tool, run `sidid -m` over `hvsc84/`, then apply the
  `DeepSID/utility/python/specific/*.py` slicing (or just `grep` the
  `(Variant)` tags). This is the only path to the fine taxonomy population —
  the DB can't give it.
- Confirm live DeepSID strings by loading `Huelsbeck_Chris/Shades.sid` and a
  known Rockmonitor tune in a JS-capable fetch; the static fetch only returns
  the generic site description (player factoid is client-rendered).
- The "MusicMaster vs SoundMonitor" distinction matters for the USF migration:
  MusicMaster_* = the standalone game driver (init `$C000`/play `$C020`),
  the bare Soundmonitor = editor-embedded replay. They likely share the play
  routine but differ in init/data layout — verify against a member of each.
- Georg Brandt's "The Final Musicplayer" (= MusicMaster_TMM) and the digi
  spin-offs (RockMon, DigiMonitor, *_Digi) add `$D418` sample playback → those
  subtunes are Mode-2 (cycle-exact digi) candidates, not pure Mode-1 tracker.
