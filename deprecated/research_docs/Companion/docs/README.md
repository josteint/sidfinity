# Companion Player — Research

Research dossier on the **Companion** C64 SID player engine, gathered for
the SIDfinity pipeline migration of `Up_up_and_Away.sid` (1984) and
`Commodore_64_Music_Examples.sid` (1985).

## Phase 1 — local findings

- **sidid identifies three signature variants**:
  - `Companion` (base)
  - `Companion/Murray`
  - `Companion/Jay_Derrett`
  - All three are in `tools/sidid.cfg` (search for `Companion`).
  - Our `hvsc84/MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.sid`
    matches the base `Companion` signature (verified by inspecting
    `docs/hubbard_up_up_and_away_disassembly.s` against the pattern
    `BC ?? ?? C8 98 9D 04 D4 60`).
- **Hubbard catalog**: 2 SIDs by Hubbard use this engine —
  `Up_up_and_Away.sid` (1984 Starcade) and
  `Commodore_64_Music_Examples.sid` (1985 Companion).
- **HVSC docs / STIL.txt**: no specific notes on the Companion engine
  itself (only general STIL comments about the tunes).
- **No prior research notes** in `docs/players/` or anywhere else in
  the codebase.

## Local disassembly (already done before research)

`docs/hubbard_up_up_and_away_disassembly.s` — 197 lines, 334 reachable
code bytes. Engine summary from that:

- **Entry points**: load $C000, init $C900, play $C703.
- **3 voices**, each processed by `sub_C75A` with X = {0, 7, 14}.
- **Freq tables**: lo at `$C080+y`, hi at `$C000+y` (note byte = pitch
  index 0..127 directly).
- **Orderlists**: V1 at `$C5B0`, V2 at `$C5F8`, V3 at `$C640`
  (single bytes per step; bit 7 set = sentinel: $0C tempo, $0D loop,
  $0E end-of-song).
- **Per-voice state** at `$C6C0..$C6D?`, 7 bytes per voice:
  orderlist position, gate-off flag, pw_lo, pw_hi, ctrl, ad, sr.
- **Tempo dividers**: `$C6D5` (gate-off tick), `$C6D6` (next-note tick).
- **5 subtunes** dispatched via self-modifying JMP at `$C913/C914`,
  with per-subtune tables at `$C915/$C91D`.
- **No effects**: no arpeggio, no vibrato, no per-instrument PWM,
  no skydive, no SFX sub-engine. One global PW sweep on V3
  (`$C8BD`: V3.pw_lo += 4 every other frame).

## Open questions for online research (Phase 2)

1. What is "Companion" historically? A music construction tool?
   A driver shipped with a magazine? Published source code?
2. Who is "Murray" — Tony Murray? An author or distributor name?
3. Who is "Jay Derrett" — UK game-music composer; what is his
   variant of Companion, and what differs from the base?
4. Did Companion have an editor/tracker? Are screenshots / manuals
   archived anywhere (CSDb release page, Archive.org)?
5. What is the format of the orderlist sentinels (`$0C`/`$0D`/`$0E`)?
   We've inferred from disassembly, but is there a canonical doc?
6. Are there other Companion SIDs in HVSC outside Hubbard? They'd
   exercise more of the engine's feature surface.

## HVSC corpus inventory (Phase 1 extension)

A full `sidid` scan of HVSC identifies **53 SIDs** as `Companion` /
`Companion/Murray` / `Companion/Jay_Derrett`. Full list at
`/tmp/companion_sids.txt`; breakdown:

| Composer / Folder | Count | Notes |
|---|---:|---|
| Hubbard_Rob | 2 | Up, up & Away! (1984); Commodore 64 Music Examples (1985) |
| Derrett_Jay | 20 | Spindizzy, Trigger Happy, Mandroid, Ninja Hamster, Dracula, Lifeforce, ZIP, Equalizer, Sqij, Counterforce, Vengeance, Road Warrior, Traxxion, Death or Glory, Destruct, Discovery, Stratton, Osmium, Jetboys, Thundercross |
| Berry_Vic | 11 | Academic classical: Bach Sonata, Webern Op 21, In C, Schillinger, Triad, Atonal Music, Progression, Sigma, Te Deum, Dufay, plus `SID_Sequencer.sid` and `Test_File.sid` |
| Hoernell_Karl | 1 | Melonmania |
| Clever_Music | 6 | Fairlight, Shao-Lin's Road, Blade Runner, Soundwave Tubular Bells, Space Doubt, Gyroscope, Back to the Future |
| Raeburn_Gavin | 1 | Gun Runner |
| /DEMOS/ | 2 | Yes Tune, Roundabout |
| /GAMES/ | 6 | Hyper Blast, Henry's House, Memory 1991, Soldier of Fortune, Surfchamp |

Notable: `MUSICIANS/B/Berry_Vic/SID_Sequencer.sid` is the file whose
name suggests it IS the engine/editor source — worth disassembling.
"Jay Derrett" composed many UK budget games' music — his variant of
Companion is the most-used (~20 SIDs).

## Two structurally-different Hubbard Companion SIDs

Disassembling both Hubbard Companion SIDs reveals they are NOT the same
implementation:

| | Up, up & Away! | C64 Music Examples |
|---|---|---|
| Year | 1984 | 1985 |
| Size | 2.4 KB | 14.8 KB |
| Load / Init / Play | $C000 / $C900 / $C703 | $086D / $087C / $086D |
| Subtunes | 5 | 15 |
| Self-modifying init sites | 1 (subtune dispatch) | 8 (`$0900, $1334, $1D88, $2A20, $33D8, $342B, $34B7, $360C`) |
| CIA timer use | No (VBI) | **Yes** (writes `$DC04`/`$DC05`) |
| Disassembly | `docs/hubbard_up_up_and_away_disassembly.s` | `docs/hubbard_c64_music_examples_disassembly.s` |

The 1985 Music Examples appears to be either a multi-tune wrapper that
patches several embedded engines or a substantially-extended Companion
variant. Both match the `sidid` `Companion` base signature, but they're
not byte-equivalent. **Implication for the pipeline**: a single
`pipelines/companion/` may need to support multiple sub-variants, or the
1985 SID may turn out to be a different engine that sidid misidentifies.

## Phase 2 — online research (consolidated)

### Origin and lineage

The "Companion" engine descends from **Keith Bowden's *The Companion to
the Commodore 64*** (Pan Books, April 1984, ISBN 9780330284790) — a UK
type-in programming book. The book's music chapter contained a 3-voice
SID driver as a listing readers entered by hand. There was **no
commercial editor or tool** — the driver was distributed as printed
6502 source.

From that root, three independent forks emerged:

| sidid signature | Author | Distinguishing feature | Used by |
|---|---|---|---|
| `Companion` (base) | Keith Bowden, 1984 | Bowden's published driver, A4 = 440 Hz | Hubbard's Up, up & Away! (1984); Vic Berry's 11 academic-music SIDs (Bach, Webern, Cage's "In C", etc.); Hoernell's Melonmania; some Clever Music titles |
| `Companion/Murray` | Chris Murray, English Software, 1984 | wraps-on-$80 / restarts-on-$FF sentinel; **A4 = 423 Hz** | Henry's House (1984); subtune 1 of Hubbard's C64 Music Examples |
| `Companion/Jay_Derrett` | Jay Derrett, CRL Group, 1984+ (hired aged ~17) | nibble-indexed double-LUT front end (`AND #$0F; ASL; TAY; B9..B9..`); kept the waveform-write tail | ~22 CRL games: Spindizzy, Trigger Happy, Mandroid, Ninja Hamster, Dracula, Lifeforce, Sqij, Equalizer, etc. |

Plus two sub-signatures for **Vic Berry's tools** (SID Sequencer 1988-89,
Aleatory Composer) that embed Companion-derived player code.

Per VGMPF Clever Music page: **Graham Jarvis** of Clever Music wrote
the first Clever-Music fork; Jay Derrett later rewrote it. **Steven
Chapman** and **John McPhee** also reprogrammed it but their forks
match the base `Companion` signature (no separate sidid tag).

### Hubbard scope clarification (important)

Earlier I assumed both Hubbard Companion SIDs use the same engine. The
**`Commodore_64_Music_Examples.sid` is a mixed-driver PSID**:
- **subtune 1** = `Companion/Murray` variant (A4 = 423 Hz) — the only
  Murray-tuned tune in HVSC outside of Henry's House.
- **subtunes 2-15** = Hubbard's own 1985 engine (not Companion at all).

So the actual Companion migration scope is:
- All 5 subtunes of `Up_up_and_Away.sid` (base Companion variant).
- Subtune 1 of `Commodore_64_Music_Examples.sid` (Murray variant).
- The remaining 14 subtunes of Music Examples belong to the Hubbard '85
  pipeline (which is already done — but they may have been excluded
  from migration because sidid identified the whole file as "Companion"
  and we skipped it. Worth re-checking with subtune-level identification.)

### Critical engine facts established

1. **A4 tuning varies by variant**: base = 440 Hz, Murray = 423 Hz,
   Raeburn = 433.5 Hz (separate engine entirely; not actually
   Companion-family). The freq table is engine-specific data we must
   carry verbatim — there is no canonical "Companion freq table".
2. **No off-the-shelf parser exists** — SIDFactory II, libsidplayfp,
   JC64dis, SIDdecompiler, and Galway's archives all lack any
   Companion-format-specific code. JC64dis can *identify* Companion
   via sidid but its disassembler has no Companion-specific label
   tables. We'd be the first to programmatically parse this format.
3. **Engine is tiny**: 334 reachable code bytes in the Up,up&Away
   binary (97 lines of meaningful asm after stripping data gaps).
4. **JC64dis author (ice00)** has done the deepest engine archaeology
   of any single individual — interactive YouTube walkthrough exists.

### Source documents saved in this directory

- `sidid_source_companion_signature.md` — 5 sidid variants with byte
  patterns and what each pattern actually disassembles to
- `keith_bowden_book.md` — bibliographic root: ISBN 9780330284790,
  Pan Books April 1984, 208pp
- `csdb_commodore_64_music_examples.md` — ice00's identification of
  the mixed-driver Music Examples; the 423 Hz Murray fingerprint
- `csdb_csm_commodore_music_examples_driver.md` — alternative CSDb
  reference for the same finding
- `archive_org_companion_book.md` — Computing History museum
  catalogue entry for the book (no scan found)
- `vgmpf_clever_music_and_jay_derrett.md` — author/lineage data for
  the Clever Music + Derrett strand
- `c64_wiki_hubbard.md` — negative finding (Hubbard's wiki page
  skips his 1984 work)
- `gtw64_up_up_and_away.md` — commercial context of Hubbard's
  first game
- `jc64dis_companion_support.md` — confirms JC64dis identifies
  Companion via sidid but has no special disassembly logic
- `sidfactory2_no_companion_importer.md` — confirmed negative
- `libsidplayfp_no_companion.md` — confirmed negative

### Bowden disassembly obtained

The Archive.org agent retrieved JC64dis's commented disassembly of
**Bowden's original `companion.prg`** — see
`jc64dis_companion_disassembly.md`. The full Dasm listing is included.
Bowden's format is canonical and minimal:

- **Note byte encoding**: `00..7F` = `(octave<<4)|semitone`, low nibble
  0..11 valid (12-15 unused). `80` = rest / gate-off. `FF` = restart
  this voice's track from slot 0.
- **No instrument table** — each voice has a 5-byte locked timbre
  (pulse-lo, pulse-hi, ctrl-no-gate, AD, SR) patched once at startup.
- **Single tempo divider** (`tuneSpeed`, default $10 = 16 IRQs/step).
- **No effects**, no PWM, no arpeggio, no orderlist layer.
- **Per-voice 7-byte interleaved record** (cursor + 5-byte state).
- **Freq tables**: 128-entry `freqHi[]` + 128-entry `freqLo[]`. PAL
  tuning A4 = 424 Hz (not 440!), NTSC = 440 Hz.

### How Hubbard extended Bowden's format (in Up, up & Away!)

Compared against Bowden's vanilla code, our local disassembly of
Up,up&Away shows Hubbard added:

| Feature | Bowden $C000 | Hubbard $C900 |
|---|---|---|
| Note stream | 1 flat per voice | flat per voice (Bowden-compat) |
| Per-voice state | inline 7-byte records | block at `$C6C0+` |
| Tempo dividers | 1 (`tuneSpeed`) | 2 (`$C6D5` gate-off tick + `$C6D6` note-load tick) → encodes duty cycle / staccato |
| PWM | none | global V3 PW_LO += 4 every other frame (hardcoded) |
| Note sentinels | `$80` rest, `$FF` restart | `$8C` rest, `$8D` end-tune (on V3), plus `$80 + pitch` = "play pitch AND schedule early release" |
| Subtune dispatch | none | 5 subtunes via self-modifying JMP at `$C913/$C914` indexing tables `$C915/$C91D` |
| Voice ordering | V1, V2, V3 | same (X = 0, 7, 14) |
| Freq tables | at `$CA00/$CA80` | at `$C000/$C080` (same shape, relocated) |

The structural model is identical to Bowden's — Hubbard didn't rewrite
the engine, he layered features (dual-tick tempo, PWM sweep, subtune
dispatch, extended note sentinels) on top.

### Phase 4 — gap analysis

**Closed (we have what we need):**
- Engine identity, origin, lineage ✓
- Bowden's canonical disassembly (jc64dis source) ✓
- Hubbard's variant: full local disassembly + decoded engine model ✓
- Note byte encoding (rest / restart / early-release / sentinels) ✓
- Memory layout (freq tables, state, orderlists, subtune dispatch) ✓
- Frequency table tuning per variant (440/423/433.5 Hz A4) ✓
- HVSC corpus of Companion SIDs (53 total) ✓
- Migration scope per Hubbard SID (5 subtunes + 1 subtune) ✓

**Still open (but won't block migration of Up, up & Away):**
- Bowden book scan — useful for confirming the book's text describes
  what we see in the binary; not strictly required.
- Murray variant exact behaviour — needs disassembly of Henry's House
  or Music Examples subtune 1; blocks ONLY Music Examples subtune 1.
- Jay Derrett variant — separate engine, separate future pipeline.
- Vic Berry's editor tools (SID Sequencer / Aleatory Composer) —
  binary dumps in HVSC; interesting but orthogonal to migration.

### Phase 3 — leads to follow (high-value)

1. **Locate the book scan** — Centre for Computing History has a
   physical copy (catalogue ID CH60534). Internet Archive search for
   "Companion to the Commodore 64 Bowden" — book did not surface
   easily; needs deeper search / interlibrary loan if it really
   exists online.
2. **Henry's House SID** — canonical Murray variant. HVSC path
   `MUSICIANS/M/Murray_Chris/Henrys_House.sid` (if present) or check
   `GAMES/G-L/Henrys_House.sid` (which our scan found, identified as
   `Companion` not `Companion/Murray` — verify).
3. **JC64dis YouTube demo** "get Chris Murray player"
   (https://www.youtube.com/watch?v=_rEFdiC8LFM) — walks through
   reverse-engineering Henry's House interactively; may show data
   layout we need.
4. **Vic Berry's `SID_Sequencer.sid` and `Aleatory_Composer.sid`** —
   12 SIDs under `MUSICIANS/B/Berry_Vic/`. Some are likely
   editor-binary dumps (i.e., the program code, not just music).
   Disassembling these may reveal the data format Berry's tools
   use — which is a direct descendant of the Companion player.
5. **Forum threads (HTTP 403'd during research, retry needed):**
   - `chipmusic.org/forums/topic/1488` — Hubbard driver thread.
   - `hvmec.altervista.org/blog/?p=1689` & `?p=1695` — Vic Berry's
     SID Sequencer / Aleatory Composer technical posts.
   - `codebase64.org/doku.php?id=base:sid_players_table`.
6. **Subtune-level identification of Music Examples** — re-run sidid
   per-subtune to verify the mixed-driver claim before migration.
7. **CSDb commenter `ice00` profile and recent work** — has done the
   most engine-specific archaeology; possibly more on his itch.io
   page (iceteam.itch.io/jc64dis).
