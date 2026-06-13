# Archive: namelessalgorithm Soundmonitor blog (via Wayback) + archive.org disk images + variants

```
source_url:    https://www.namelessalgorithm.com/computer_music/blog/soundmonitor/
fetched_via:   wayback 2026-06-13  (http://web.archive.org/web/2id_/<url> via curl;
                 the live page 404'd through WebFetch, Wayback served the full article)
fetch_date:    2026-06-13
author:        "nameless algorithm" (uncredited blog author; secondary RE write-up)
content_date:  ~2021 (the author runs Soundmonitor in VICE; references the 2021 archive.org upload)
reliability:   SECONDARY — a careful modern reverse-engineering walkthrough. Agrees with the
               primary 64'er manual on every format detail; adds the introspection/quirks angle
               and the v1.0 module memory ranges. Use as cross-check, not as the byte authority.
```

The blog is the technical write-up flagged in the task brief. Its format claims all **corroborate
the primary 64'er manual** (see `archive_64er_1986.md`); the parts that add value:

## Format details (corroborating + clarifying)

- **3 tracks = 3 SID voices.** Each track plays a "bar" at any time; a bar is a block of note data,
  each note having a pitch and an associated sound.
- **EDIT SOUND** = "a patch for a single oscillator on the SID chip": waveform, envelope, vibrato,
  portamento, filter cutoff/resonance/envelope. **"24 parameters in total."** (Matches the 24-reg
  table.)
- **TRACK/STEP-TABLE** row `SP TRKx TR ST`: "SP = step, TRKx = a direct 16-bit memory address to
  the bar data, **normally from $BE00 and up**, TR = transpose (two's complement), ST = sound
  transpose (offsets the instrument index, lets bars be reused with modified sounds)."
- **NOTE EDIT** grid example confirms the per-cell `note + (options<<4 | instrument)` layout and the
  left-to-right/top-to-bottom 8th + three-32nds reading order. Verbatim sound-options bit list:
  `bit1=portamento, bit2=transpose disable, bit3=arpeggio, bit4=soundtranspose` (1-based; identical
  to the manual's 0-based `bit0/1/2/3`). Worked example `C-2 61` = note C2, options `0110`=6
  (transpose-disable | arpeggio), instrument 1.
- **AR/S DATA** = "where you define tempo and arpeggios; it can change for each bar, allowing tempo
  and harmonic changes." Arpeggios = "rapid pitch changes emulating a chord using a single sound
  channel" (cf. Hubbard's *Monty on the Run*, 1985).
- **Two's complement everywhere:** "transposing two semitones down is `FE`." (`F8..FF` = -8..-1.)

## Memory layout (blog's v1.0 module ranges — agrees with Tabelle 1)

> "addresses `$3000–$9FFF` can be used for note data, as well as `$B000–$BDFF`, and … `$BE00` is
> an empty bar. … the Soundmonitor editor itself is located at `$1000`."

Quirk demonstrated: typing `$1000` into the track/step table makes the editor display its own code
as "note data"; editing it crashes the program ("editing Soundmonitor from within itself").

## Lineage / variants (from the blog + corroborating searches)

- **MusicMaster** = the standalone replayer Hülsbeck wrote *before* Soundmonitor; the editor was
  built around it. (The 64'er manual: "eine völlig unabhängige Abspielroutine … 'Musicmaster'".)
- **TFMX** = Hülsbeck's *next* C64 system after Soundmonitor — abstracted arpeggios into "sound
  macros" (per-frame pitch/waveform/amplitude manipulation). Re-implemented on Amiga 1989 (Turrican
  II). **TFMX is a different engine, not a Soundmonitor variant.**
- **"The Final Musicplayer"** — described elsewhere as an *optimized* replayer for the same data
  (the vanilla MusicMaster was slow & unrelocatable). Treat as a possible alternate replayer over
  the same module format (verify before assuming).
- **Rockmonitor (The Dutch USA-Team)** = Soundmonitor hacked to add **digi/sample playback** —
  "clearly still Soundmonitor with a few added features." Multiple versions (II/III/IV/V). This is
  the main version axis HVSC will contain beyond vanilla v1.x. **The sample feature is the key
  format delta to watch for** (vanilla Soundmonitor has NO samples).

---

## Disk images & binaries on archive.org / FTP (download leads — NOT fetched into repo by me)

### Soundmonitor v1.0 editor disk (.d64)
```
source_url:  https://archive.org/details/d64_Soundmonitor_v1.0_1986-10_Chris_Huelsbeck
fetched_via: direct (metadata only; binary not downloaded)
fetch_date:  2026-06-13
content_date:1986-10 ; uploaded by "Sketch the Cow" 2021-03-10
reliability: PRIMARY artifact (the actual editor disk)
```
- Item identifier: `d64_Soundmonitor_v1.0_1986-10_Chris_Huelsbeck`
- Disk image: `Soundmonitor_v1.0_1986-10_Chris_Huelsbeck.d64` (170.8 KB) — the standard 1541 D64.
  Direct download:
  `https://archive.org/download/d64_Soundmonitor_v1.0_1986-10_Chris_Huelsbeck/Soundmonitor_v1.0_1986-10_Chris_Huelsbeck.d64`
- **No bundled .txt/.nfo/.pdf docs** in the item — only the .d64, metadata XML/sqlite, and 12
  screenshots (`screenshot_00..11.png`, `00_coverscreenshot.png`). The screenshots show the
  TRACK/STEP-TABLE, EDIT SOUND, NOTE EDIT and ARP/S pages (useful for confirming the UI fields, not
  the binary layout).
- NOTE: a parallel research agent has already placed extracted binaries in
  `pipelines/soundmonitor/docs/vendor/` (`SOUND-MONITOR.prg` 12797 B ≈ the unpacked 51-block
  editor; `sound_monitor_v1.0.t64.gz`). Use those for binary cross-checks of the §1 memory map.

### zimmers.net FTP — editor binaries (incl. Rockmonitor)
```
source_url:  https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/
fetched_via: direct (index only)
fetch_date:  2026-06-13
reliability: MEDIUM (community archive; binaries dated 2009-08-18)
```
- `rockmonitor-2.prg` (26254 B) — "Successor of soundmonitor **with digiplayer**."
- `rockmonitor-3.prg` (17923 B), `rockmonitor-4.prg` (20062 B).
- `mastercomposer.prg` (23306 B) — "Editor for Huelsbeck's tunes like Katakis" (a *different*,
  later Hülsbeck editor — not Soundmonitor; flagged so it isn't conflated).
- (No file explicitly named "soundmonitor"/"musicmaster" in this dir; Rockmonitor-2 references its
  predecessor.)

### Rockmonitor disk images / releases
- archive.org: `https://archive.org/details/d64_Rockmonitor_II_1987_The_Dutch_USA_Team` (Rockmonitor
  II, 1987, The Dutch USA-Team).
- CSDb Rock Monitor V5: `https://csdb.dk/release/?id=10632` (Dutch USA-Team, 1988-05-14).
- CSDb Soundmonitor V1.0: `https://csdb.dk/release/?id=59929` (2160 downloads; ext. host
  Pokefinder.org). User comments confirm "Rockmonitor was a modified version of this."

---

## Version axis summary (for distinguishing HVSC members)

| Engine                         | Replayer signature | Samples? | Notes |
|--------------------------------|--------------------|----------|-------|
| Soundmonitor v1.0 (1986-10)    | init $C000 / play $C020 | no   | the 64'er type-in; the canonical target |
| Soundmonitor v1.1 / v1.3 (86–87)| (same family)     | no       | community/later revisions (c64-wiki lists v1.0/1.1/1.3) — likely same module + replayer, minor editor changes; **verify replayer addresses & write order before assuming identical** |
| Rockmonitor II/III/IV/V (87–88)| (Soundmonitor-derived) | **YES (digi)** | Dutch USA-Team hack; adds sample playback. The sample path is the format delta; treat as a distinct sub-engine for the per-frame/cycle write model (digi = cycle-exact, Mode 2). |
| MusicMaster                    | $C000/$C020 (the embedded replayer) | no | the standalone routine Soundmonitor is built around; what games/demos embed |
| "The Final Musicplayer"        | (unknown)          | ?        | reportedly an optimized replayer for the same data — unverified |
| TFMX (later)                   | n/a                | n/a      | **separate engine**, not a Soundmonitor variant — do not classify as Soundmonitor |

---

## Leads to follow

- **64'er 10/1986 full magazine scan (HOLY GRAIL — fetched & translated):**
  archive.org item `64er_1986_10` — details: `https://archive.org/details/64er_1986_10` ;
  OCR text: `https://archive.org/stream/64er_1986_10/64er_1986_10_djvu.txt`. Article+manual at OCR
  lines ~17743–18591; "Tabelle 1" memory map ~18640–18800; 24-register table ~18470–18591; the
  11 KB hex Listing 1 begins ~20195 (continuations ~36761, ~43173). Pages 53–64. **All translated
  into `archive_64er_1986.md`.**
- **Soundmonitor v1.0 editor disk:** archive.org item `d64_Soundmonitor_v1.0_1986-10_Chris_Huelsbeck`
  → `Soundmonitor_v1.0_1986-10_Chris_Huelsbeck.d64`. (Binaries already in `docs/vendor/`.)
- **Rockmonitor (digi variant) disks:** archive.org `d64_Rockmonitor_II_1987_The_Dutch_USA_Team`;
  CSDb V5 `id=10632`. zimmers FTP `rockmonitor-2/3/4.prg` at
  `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/`. Pull these when modelling the
  sample-playback delta.
- **CSDb release pages:** Soundmonitor V1.0 `https://csdb.dk/release/?id=59929` (links to
  Pokefinder.org external host + 2160-download internal file); scan its "used by"/notes for the
  v1.1/v1.3 revision releases.
- **namelessalgorithm blog (this source):** live URL 404'd via WebFetch; Wayback works ⇒
  `http://web.archive.org/web/2id_/https://www.namelessalgorithm.com/computer_music/blog/soundmonitor/`.
  Its References list also cites "huelsbeck.com: Credits" (checked — no Soundmonitor content there).
- **C64-Wiki (de):** `https://www.c64-wiki.de/wiki/Soundmonitor` — lists versions v1.0/v1.1/v1.3 +
  Rockmonitor, the `SYS 4096` (editor restart) / `SYS 49152` (play complete song) entry points, and
  the full key-command reference. (English `c64-wiki.com/wiki/Soundmonitor` 404'd.)
- **VGMPF wiki:** `https://www.vgmpf.com/Wiki/index.php?title=Soundmonitor` — names "The Final
  Musicplayer" as the optimized driver; otherwise high-level.
```
