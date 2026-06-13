<!--
provenance:
  topic: SID-Wizard per-version release/change history (player.asm / exporter.asm / SWM format)
  primary_source_url: https://sourceforge.net/p/sid-wizard/code/HEAD/tree/trunk/manuals/ChangeLog.txt
  secondary_source_urls:
    - https://sourceforge.net/p/sid-wizard/code/HEAD/tree/tags/   (SVN version tags + revisions + dates)
    - https://sourceforge.net/p/sid-wizard/code/HEAD/log/         (SVN commit log)
    - https://csdb.dk/release/?id=109698  (V1.0 RC)
    - https://csdb.dk/release/?id=110942  (V1.0)
    - https://csdb.dk/release/?id=112716  (V1.2)
    - https://csdb.dk/release/?id=131846  (V1.7)
    - https://csdb.dk/release/?id=165302  (V1.8)
    - https://csdb.dk/release/?id=220489  (V1.91)
    - https://csdb.dk/release/?id=221555  (V1.92)
    - https://csdb.dk/release/?id=255544  (V1.93)
    - https://demozoo.org/productions/99999/  (V1.5)
    - https://www.hvsc.c64.org/download/files/news/20221223.txt (HVSC #78 news)
    - https://www.generationamiga.com/2026/01/17/sid-wizard-v1-94-major-upgrade-for-c64-music-creators/
  fetched_via:
    - "direct" for the SourceForge ChangeLog.txt (raw via curl), SVN tags/log (WebFetch), Demozoo, GenerationAmiga, HVSC news
    - CSDb release pages NOT directly fetchable (HTTP 503 to both WebFetch and curl, 2026-06-13); dates/notes are from WebSearch result snippets, cross-checked against the SVN tag dates
  fetch_date: 2026-06-13
  author: Mihaly Horvath ("Hermit") — SID-Wizard author. ChangeLog text is Hermit's own. SVN tags by hermitsoft + soci (Soci/Singular = co-developer, esp. 64tass + IRQ/MIDI).
  content_date: 2012-07-08 (SVN r1) .. 2026-01-17 (V1.94); ChangeLog.txt covers V1.0..V1.8
  reliability: HIGH for V1.0..V1.8 (verbatim from the in-repo ChangeLog.txt + SVN tag revisions/dates). MEDIUM for V1.9..V1.94 (these post-date the SourceForge SVN, which froze at V1.8 / Jan-2021; later releases live on CSDb + the author's site, reconstructed here from news/search snippets — CSDb itself was unreachable this session).
-->

# SID-Wizard — version-to-version history

Companion docs: `archive_version_player_diffs.md` (per-version player CODE deltas =
basis of the per-version sidid signatures), `research.md` (current-format reference).

## TL;DR for SIDfinity

- **Two development eras.** (1) **C64-native tracker era, V1.0 (2012) .. V1.8 (2018/2021)** —
  developed in the SourceForge SVN; this is where `player.asm` / `exporter.asm` / the SWM
  format evolved, and where the **distinct per-version sidid signatures come from** (the
  exported player code changed shape per release). (2) **Cross-platform era, V1.9 (2022) .. V1.94 (2026)** —
  per HVSC #78 news, "since version v1.9 [SID-Wizard] also [runs] on Windows and Linux";
  most V1.9x work is the PC editor + the `cRSID` emulation engine, NOT the C64 player. The
  C64 player.asm / SWM format are essentially frozen from ~V1.8 onward (V1.92 added 4SID
  export via the WebSID `.sid` proposal — an exporter/header change, not a player-logic change).
- **The exported player embeds a version string.** `player.asm` has
  `TrackerID .text " SID-WIZARD ",SWversion," "` in its jump-table header — every exported
  `.sid`/`.prg` carries `" SID-WIZARD <ver> "`. Combined with the per-version code layout
  shifts, this is why sidid has separate `SidWizard_V1.0/V1.2/V1.4/V1.5` fingerprints.
- **The SWM module format magic never bumped past `SWM1`.** `SWM2` was a *planned* format
  (referenced repeatedly in the ChangeLog: "0 will mean 0 in SWM2 module format") that was
  never shipped. The 64-byte SWM header is frozen ("don't modify to keep compatibility
  throughout versions"); the format evolved by *deprecating* header fields in place, not by
  changing the magic. See `archive_version_player_diffs.md` §SWM.

## SVN version tags (authoritative dates + revisions)

From `sourceforge.net/p/sid-wizard/code/HEAD/tree/tags/`. The tag is the canonical "this is
release X" handle; note `1.0-rc` was committed by `soci`, the rest tagged by `hermitsoft`.

| Tag          | SVN rev | Tag date    | Tagger     | Notes |
|--------------|---------|-------------|------------|-------|
| `1.0-rc`     | r3      | 2012-07-08  | soci       | V1.0 RC / beta. CSDb release 2012-07-07 (id 109698). Hermit later marked it "rather obsolete". |
| `1.0-100%`   | r103    | 2012-09-09  | hermitsoft | V1.0 final. CSDb release 2012-08-31 (id 110942). (Repo layout reorganised around here — commit msg "deleted accidental 'trunk'".) |
| `1.2`        | r174    | 2012-11-12  | hermitsoft | CSDb release 2012-11-12 (id 112716). |
| `1.4`        | r214    | 2013-02-07  | hermitsoft | CSDb release 2013-02-07. (No public 1.3 release; ChangeLog lumps "1.0...1.2" then jumps to 1.4.) |
| `1.5`        | r312    | 2014-01-03  | hermitsoft | CSDb / Demozoo release 2013-12-30; SVN tag cut a few days later. Co-credited Hermit + Soci. |
| `1.6`        | r357    | 2014-02-14  | hermitsoft | |
| `1.7`        | r389    | 2014-07-14  | hermitsoft | CSDb release 2014-07-12 (id 131846). Last "classic" SourceForge ZIP release (`SID-Wizard-1.7.zip`, on the project's files page + hermit.sidrip.com). |
| `1.8`        | r394    | 2021-01-02  | soci       | **Big gap 2014→2021 in SVN.** CSDb release dated 2018-06-03 (id 165302) — i.e. V1.8 shipped publicly in 2018 but was only committed/tagged into SourceForge SVN in Jan-2021 (a batch import by soci: r393 "Add version 1.8", r394 "Tag 1.8", then build-fixes r395-r398). SVN HEAD = r398 (2021-01-02), the end of SourceForge activity. |

Post-1.8 (V1.9, V1.91, V1.92, V1.93, V1.94) have **no SourceForge SVN tags** — development moved
off SourceForge. Releases are on CSDb + the author's site; the `anarkiwi/sid-wizard` GitHub
mirror tracks SVN HEAD (≈1.8) on `master` (its "v1.0.1" GitHub release is a mirror-packaging
tag, unrelated to the C64 version numbering).

## CSDb / post-SVN release dates

| Version | Release date | CSDb id | Headline |
|---------|--------------|---------|----------|
| V1.0 RC | 2012-07-07   | 109698  | First public release. |
| V1.0    | 2012-08-31   | 110942  | First "100%" release. |
| V1.2    | 2012-11-12   | 112716  | |
| V1.4    | 2013-02-07   | (—)     | New GT-style filter FX; single-speed→plain SID export. |
| V1.5    | 2013-12-30   | 99999*  | SFX, 2SID, bare player, auto-reloc table, alt tunings. (*Demozoo id) |
| V1.6    | 2014-02-14   | (—)     | +2 instruments via memory rearrangement. |
| V1.7    | 2014-07-12   | 131846  | Full 3SID; SWP packed-data format + SWP player; slowdown FX. |
| V1.8    | 2018-06-03   | 165302  | Drean support; "DEMO" playertype; SR-AD reorder; orderlist-NOP. |
| V1.9    | 2022 (Q3?)   | (—)     | First cross-platform (Windows/Linux) build per HVSC #78. |
| V1.91   | 2022-08-08   | 220489  | (PC-side; predecessor to the -O2 speedup in 1.92.) |
| V1.92   | 2022-09-04   | 221555  | Full 4SID export (WebSID `.sid` proposal); 2× faster (GCC -O2); SID4 mute Shift+U/I/O; improved Ctrl+E pattern-finder; date stamped into SID. |
| V1.93   | 2025-08-22   | 255544  | Maintenance/feature update (PC editor). |
| V1.94   | 2026-01-17   | (—)     | sinc-resampler smoothing; **cRSID-1.56** engine; config-file save/load; oscilloscope + main-volume tweaks. (PC editor — no C64 player/format change reported.) |

> Note the **CSDb date vs SVN-tag date split for V1.8** (2018 public release, 2021 SVN
> import). If you fingerprint by player code, treat "V1.8 player" as a single artifact
> regardless of which of those two dates a given HVSC tune is stamped with.

## Per-version change summary (C64 player/exporter/format), from the in-repo ChangeLog.txt

Only items that touch the **player.asm / exporter.asm / SWM format** (i.e. things that change
the *exported* artifact or its register-write stream) are pulled out here; the ChangeLog also
has hundreds of editor-UX / SWMconvert / MIDI items that are irrelevant to SIDfinity. The
ChangeLog lists newest-first; this table is oldest-first.

### V1.0 → V1.2 (the founding feature set; ChangeLog header "1.0...1.2 additions")
Player / export-affecting items:
- **`$1F` "filt-external" big-FX added to the `extra` player variant** (toggles $D418 external-input bit; initialised to 0 at tune start). First example of a feature gated to one driver variant.
- **More ghost-registers added** "at least for HR and Waveform" for more precise sound (and "in extra version all registers are ghosted") — i.e. the ghost-register write model was strengthened here. Costs a little rastertime.
- **SID-register init changed: "now writing 0 instead of 8 into SID-registers"** (then setting waveform $08 afterwards) — changes the init write stream (and a noted side effect: a bigger $D418 click on subtune switch).
- **ADSR↔gate-bit write spacing rule established**: "KEEP ENOUGH DISTANCE (around 10 commands but not too much) BETWEEN ADSR AND GATE-BIT WRITING" — a deliberate write-ordering/timing constraint in the player (hard-restart correctness). Also restructured IRQ rasterbars so the single-speed `play()` is not under the sprites (was eating ~400 cycles).
- **$FF detune-NOP** added (a detune-table terminator/no-op).
- **First-frame waveform (instrument byte $0F) made user-configurable**, with the compat rule "in SW1.x 0 is converted to $09 ... but 0 will mean 0 in **SWM2** module format" (first SWM2 reference).
- **Subtune-jump can be handled independently per track** (parametrised `SETSEQA`).
- **Relocator `sec` fix** ("a 'sec' was missing" — broke since ~rev16) and instrument-0 dismissal so HVSC accepts exports (`instrument-0-pointer outside player`).
- NTSC auto-detection at startup; PAL/NTSC frequency-table selectable in SID-Maker.

### V1.4 (ChangeLog "1.4 additions")
- **New GT-compatible pattern effects** ("some effects slightly rearranged (e.g. wf-table pointer), new effects added which are in GT: simple cutoff-frequency setting, simple filter-control (switch&reso) setting"). Filter-switch setting in range `$80..$8F` (KT value). → **changes the effect-byte → register-write mapping** (relevant to the V1.4 sidid signature).
- **Exporter: single-speed SIDs now use the plain SID filetype (no CIA starter code).** Multi-speed still uses CIA timing. → changes the exported PSID header/init for single-speed tunes.
- **Exporter: tracker/author info now stored into the VARIABLES area** (overwritten by initer) — "~60 bytes freed up". → moves where the `SID-WIZARD <ver>` signature string sits relative to code.
- Extended relocation range (settings.cfg `min`/`max`, default $0200..$FF00).
- `exe.prg` export can switch subtunes (+/- keys); rastertime/player-size shown in startup-menu; auto-detected-but-selectable player-type (normal/light/medium/extra) + machine-type.
- Fix: vibrato-amplitude-change FX after portamento now precisely pitched; reset filter-shift at startup.

### V1.5 (ChangeLog "1.5 additions") — the big structural release
- **Auto-generated relocation table** — "player now has an automatically generated relocation-table - Soci made 64tass rev361 capable of achieving this in the preprocessor". → the player's relocation mechanism changed wholesale.
- **`bare` player variant introduced** ("'bare' player (no subtune-support, etc...)"). Adds a 5th driver variant alongside light/medium/normal/extra.
- **SFX support** — a distinct note/pattern playable on (e.g.) track 3 from outside the player (`SFXsub`/`SFXinit` entry in the jump table; uses HR for SFX sounds). Gated by `SFX_SUPPORT`. → new player entry-point + code.
- **2SID (stereo) support** — 2SID editor + 2SID exporter (user sets SID2 address in the export). → second set of SID register defs (`SID2BASE`) in player.asm; new `.sid` 2nd-chip address field.
- **Alternative tunings** — A=432 Hz Verdi + just-intonation/Pythagorean/Well freq tables, selectable in startup-menu; **loadable/calculated frequency tables**. → SWM header byte $14 (TUNINGTYPE_POS) becomes meaningful; the freq table the player ships with can differ.
- **SID-init loop reworked so `$d418` is left out of init** — "click/pop is eliminated or at least less noticeable this way". → changes the init write stream (no $D418 in the SID-clear loop).
- **Tempotable reduced to `$80`** ("that would be enough, we got some more place").
- Note-mode chords; SDI/GMC/JCH keyboard layouts (editor); config saved to `.cfg`; manual moved to txt.

### V1.6 (ChangeLog "1.6 additions")
- **Room made for two more instruments** via careful memory arrangement (raises the usable instrument count).
- `SYS2061` SafeRestart now also inits the NMI vector (RESTORE key).
- Bare-player 2SID export freeze fixed (`datzptr+0`/`datzptr+1` swapped in `exporter.asm endPset`).
- Exporter: mono SIDs now clear bits 6-7 at SID-header `$77` (Ian Coog) — a PSID-header fix.
- `$FE/$FF` end-signal handling: "if other tracks are zero or shorter than the currently edited, don't play them after $FE/$FF endsignal" (`dec SEQPOS,x` added in INITER branch).

### V1.7 (ChangeLog "1.7 additions")
- **Full 3SID support** (editor + exporter; `playadapter.asm` channel-division tables for 7+ channels). → third SID register set.
- **SWP format + SWP player** — "SWP is a separate packed music-data file with relative pointers; the special SWP-player adjusts its pointers to SWAP to it at init (SWP address in X and Y)". A *new player variant* that keeps instrument+SFX data separate and is relocatable independently of tune size. → distinct exported player.
- **Slowdown FX** (combined pitch-shift + tempo change, "bullet-time"). → new pattern effect.
- Fix: filtered→unfiltered instrument no longer leaves other channels filtered (point filter exec to `$ff`).

### V1.8 (ChangeLog "1.8 additions") — last C64-player-logic release
- **AD-SR write order changed to SR-AD** in `player.asm` "when non-ghostregister Hard-Restart and soundstart events happen. Probably causes a bit better, more stable sound". → **direct change to the SID write order** in the non-ghost path (see player-diffs doc; strong candidate for distinguishing a V1.8 fingerprint). (SVN r390, 2014-07-22, message: "AD-SR order changed to SR-AD in Hard Restart and soundstart in player.asm".)
- **"DEMO" playertype** — "size & runtime reduction but keep some important aspects". Adds a 6th driver variant (bare/light/medium/normal/extra/demo). SWM header $13 enumerates these.
- **Drean (C64) detection + support** — exporter now copies CIA-timer values for PAL/NTSC/**Drean** into the framespeed list. → adds a machine-type to the exported timing.
- **Orderlist Separator NOP** (orderlist-FX `$F0..$FD`, optional index) — new sequence-stream opcode.
- player.asm bug fixed: **1st-waveform pitch was indexed in `FREQTBH` by X instead of Y (typo)** — "not much audible difference btw." (a real but subtle write-value change between ≤1.7 and 1.8).
- SID-Maker-SWP slide/portamento > ~$F0 fixed: **`bpl`→`bcs` after label `SLOWDN3`** (a branch-condition change in the slowdown/slide path).
- `player.TUNE_HEADER` no longer pinned to fixed `$20`, so trackerinfo always fits before format/author info even if the jump-table grows. → the `SID-WIZARD <ver>` signature + header layout can shift in 1.8.
- Filter/PW-jump command `$0A/$0B` fix: reset `CWEPCNT`/`PWEEPCNT` so slide-repetition works after a long left-side wait.
- Final Cartridge 3 / KERNAL load-save export fixes; debug `sta $8000,x` removed from exporter (was harmlessly left in 1.7).
- SWMconvert: SWS↔SWM conversions.

### V1.9 .. V1.94 (post-SourceForge; reconstructed)
- **V1.9 (2022): the editor became cross-platform (Windows + Linux PC build)** in addition to the native C64 program (HVSC #78 news). This is the big architectural fork — a PC reimplementation of the editor/player using `cRSID` for emulation. The C64 player/format are unchanged in spirit.
- **V1.91 (2022-08-08):** PC-side iteration (immediate predecessor of the 1.92 -O2 build).
- **V1.92 (2022-09-04):** **Full 4SID support** for `.sid` generation "used the new WebSID SID-format proposal" (an *export-header* feature — multi-SID `.sid`, not new player music-logic); editor 2× faster than 1.91 ("added the -O2 flags for GCC"); SID4 channel mute Shift+U/I/O; improved Ctrl+E pattern-finder (scans all subtunes for the highest-numbered pattern); date inserted into the SID file.
- **V1.93 (2025-08-22):** maintenance/feature update (PC editor).
- **V1.94 (2026-01-17):** sinc-resampler smoothing; upgraded to **cRSID-1.56**; config-file save/load; enhanced oscilloscope + main-volume controls. All **PC-editor** improvements; no reported C64 player or SWM-format change.

## What this means for the SIDfinity pipeline

1. **For sidid fingerprinting:** the four DB signatures (V1.0/V1.2/V1.4/V1.5) correspond to real
   player-code shape changes (see the player-diffs doc). After V1.5 the code keeps drifting
   (1.6 instrument-count memory rearrange, 1.7 3SID/SWP, **1.8 SR-AD reorder + TUNE_HEADER
   un-pinning**), so expect additional implicit fingerprints for 1.6/1.7/1.8 even if the DB
   currently only names up to V1.5. The embedded `" SID-WIZARD <ver> "` string is an exact
   version tag inside the binary if you want a ground-truth version (when not stripped).
2. **For the SWM extractor:** target **SWM1 only** (no SWM2 exists in the wild). The 64-byte
   header is stable; just be aware that header bytes $06/$07/$11/$12 are **obsolete/garbage in
   modern files** and were live editor-state in ≤V1.2 — don't read them.
3. **For the write-model / verifier:** the per-version write-stream differences worth encoding
   as config knobs are: (a) **AD vs SR ordering** in the non-ghost HR/soundstart path (≤1.7 = AD-SR,
   1.8+ = SR-AD); (b) **`$D418` presence in the init clear-loop** (present ≤1.4, omitted from
   1.5 on); (c) **single-speed plain-SID vs CIA-starter** (CIA always ≤1.2-ish, plain-SID for
   single-speed from 1.4); (d) **ghost-register coverage** (more registers ghosted from 1.2,
   "all" in the `extra` variant). These are exactly the kind of per-engine config fields the
   project favours over `if version==X` branches.
