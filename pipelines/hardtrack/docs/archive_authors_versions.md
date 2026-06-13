# HardTrack Composer — authors, scene provenance, and version history

```
source_url:   https://csdb.dk/release/?id=74928   (V1.0)
              https://csdb.dk/release/?id=36647   (V1.0+ [6 speed])
              https://csdb.dk/scener/?id=370      (Brush)
              https://csdb.dk/scener/?id=3539     (Longhair)
              https://csdb.dk/sid/?id=13597       (Glover SID, North Party 1997)
              https://csdb.dk/forums/?roomid=14&topicid=65313  (format help thread)
              https://www.c64scene.pl/viewtopic.php?t=584      (original + printed PL manual)
local:        tmp/hardtrack/OUT_PRZECZYTAJ_MNIE.prg (decoded read-me — see archive_elysium_contents.md §4)
              tmp/hardtrack/Hardtrack_Composer_v1_-6speed-.inf0
              pipelines/hardtrack/docs/_artifacts/sdk/extracted/PLAYER_V1.0.bin / PLAYER_V1.1.bin
fetched_via:  WebFetch + WebSearch (CSDb, c64scene.pl, c64power.com); Wayback CDX API;
              local read of pre-fetched read-me/inf0/SDK binaries
fetch_date:   2026-06-13
author:       composite — CSDb editors (Fred et al.), the authors' own read-me, the BHG .inf0
content_date: 1991-12 (build) .. 1992 (V1.0 release) .. ~1997 (6 speed) .. 2013 (CSDb forum)
reliability:  HIGH for authors (cross-confirmed by first-party read-me + CSDb);
              MEDIUM for exact dates (CSDb gives year-only; 6-speed date inferred from Glover/Samar 1997 activity);
              LOW for the rumoured "V2.0" (single forum mention, unverified).
```

## 1. Authors & roles (first-party, from the decoded read-me + CSDb)

| Role | Handle | Real name | Group(s) | Source |
|---|---|---|---|---|
| **Editor code** | **Brush** | **Krzysiek (Krzysztof) Dąbrowski** | Elysium (founder, 1/1992); ex-Parados (1991–92), ex-Sex Instructors (1989–91), later Success | read-me §4 + CSDb scener #370 |
| **Player / replay code** | **Longhair** (lhr) | **Miłosz Ignatowski** | Elysium (1/1992); ex-Parados; founder of Jazzers | read-me §4 + CSDb scener #3539 + YouTube "Music Collection intro – Miłosz Ignatowski (Longhair) 1992" |
| Intro code | Zephyr | Krzysiek Augustyn | Elysium | read-me |
| Title picture | Cruise | Wojtek Niemczyk | Elysium (CSDb lists Cruise/Padua) | read-me / CSDb |
| Intro music | The Syndrom | Matthias Hartung | TIA / Crest | read-me / CSDb |
| Example-tune driver* | KSB | Sławek Abramczyk | Datacrime | read-me |
| Disk fastloader | K.M. | Krzysiek Matula | Taboo | read-me; loader stamp `K.M.91-12-12` |
| Turbo ROM saver | MMS | Marek Matula | Taboo | read-me |
| Example tunes | Longhair; Touldie (Bartosz Tabaka); Shogoon (Wojtek Radziejewski) | — | Elysium / Taboo | read-me |
| Beta testers | Longhair, Touldie, Shogoon | — | — | read-me |

\* The "grajek do muzyczek" (KSB/Datacrime) is the *driver used for the bundled example
tunes*, NOT the HardTrack replay routine. The engine HVSC identifies as `HardTrack_Composer`
is **Longhair's player**. Do not conflate.

CSDb's V1.0 release page (#74928) credits **Code: Brush + Longhair** (both Elysium/Parados),
Music: The Syndrom, Graphics: Cruise/Padua, packaged tune "Frozen Energy" by The Syndrom.
A 2013 CSDb edit by *Fred* notes "I've added Longhair to the credits since he made the code
of the player" — i.e. the player authorship was historically under-credited and later fixed,
matching the read-me.

### Scene provenance chain
- **Elysium** (Poland, founded 1/1992 by Brush) is the home group; many members (Brush,
  Longhair, Zephyr, Cruise, Touldie, Hain) came over from **Parados** (1991–92).
- The editor was commercially distributed in Poland by **Tim Soft** (disk label `(C) TIM SOFT`,
  Timsoft 1994 disk). The original boxed copy shipped with a **printed Polish manual**
  ("instrukcja PL"); a sealed unit was auctioned on Allegro.pl (c64scene.pl thread t=584).
- Source was later open-released by Brush himself under the "GNU Generation" Polish
  source-sharing banner (`/gnu-generation/Brush/hardtrack_sdk.zip`) and re-released at
  **North Party 6** (2010). Mirror upkeep by CenTraX/Agony.
- Canonical FTP per the BHG `.inf0`: `ftp://ftp.elysium.pl/`.

## 2. Format reference (verbatim, from CSDb forum #65313, Asterion 2013-12-27)

The most complete public format spec is Asterion's forum post. Reproduced verbatim
(this is the authority the per-engine format notes should cite; it agrees with the
prior `research.md` but corrects two points marked ⚠).

**Keybindings (editor):**
> F1 play / F2 stop / F3 continue / F5 slow play / F7 fast play / arrow disk menu /
> +- change song / CTRL+1 2 3 move between track tables / CBM+1 2 3 mute channels 1-3 /
> `,` `.` macro/pulse/filter tables / SHFT+RETURN move to pattern editor / S sound editor /
> K L change tempo / CBM+CLR delete track / CBM+P kill patterns / CBM+K kill tracks /
> CBM+M kill macros/pulse/filter data

**Track (orderlist) window data:**
> `$00-$7F` pattern numbers / `$80-$FC` change transposition / `$FD xx` jump to track
> position / `$FE` end of track / `$FF` jump to beginning

**Pattern data:**
> notes / `END` (CBM+E) end / `GLU yy` (CBM+U) glissando up / `GLD yy` (CBM+S) glissando
> down / `DEL` (CBM+D) trigger release / `CUT` (CBM+C) release / instrument = its number
> increased by `$80` / `$6F` plays legato / X V change octave

**Sound (instrument) editor parameters:**
> pulse/filter start = initial cutoff/pulse / pulse/waveform/filter number = macro-table
> references / vibrato width/add/end = depth control / `fx byte` = `xy` format /
> `$d017/$d018` = `xy` resonance & filter type

**FX byte `xy`:**
> x: `0`=normal ins, `8`=drum instrument / y: `0`-`2` hard-restart settings (frames)

**Macro (waveform) command data — pairs `xx yy`:**
> ⚠ `xx` → written to `$d404` waveform register, **nybbles reversed** /
> `yy`: `$00-$5C` relative transposition, `$80-$DF` absolute transposition /
> `$FE` stop macro / `$FF yy` loop to position
> (⚠ research.md said "xx = waveform register value" plainly — the forum spec says the
>  nybbles are stored reversed, a real codec detail for extraction.)

**Pulse macro — pairs `xx yy`:**
> `xx` add/subtract from pulse (even/odd encodes direction) / `yy` = how many frames /
> `$FF yy` loop

**Filter macro — pairs `xx yy`:**
> `xx` add to `$D416` / `yy` how many frames / `$80 yy` loop

**Drums:** drum instruments use absolute pitch via `$d401` (per Asterion + research.md).

## 3. Version table

| Version | Date | Released as | Author(s) | What it is / differences |
|---|---|---|---|---|
| **V1.0** | **1992** (loader stamped 1991-12-12) | "Hardtrack Composer V1.0" by Elysium (CSDb #74928); commercial disk via **Tim Soft** (1994 redistribution); SDK source later open-released | Editor: **Brush**; Player: **Longhair** | The baseline release. Full editor (`MAIN`) + standalone `HDT PLAYER` (V1.0) + `HDT DEPACKER` + `HDT RELOCATOR` + 10 example tunes + Polish read-me. Player load addr varies per build; SDK source listing is `PLAYER_V1.0.bin` (`PLAYER V1.0 BY LONGHAIR/ELYSIUM`). |
| **V1.1** | post-1992 (undated) | player binary inside the SDK only — **no standalone disk on the mirror** | Player: **Longhair** | A **player-only** revision. SDK source listing `PLAYER_V1.1.bin` is ~337 B (~6%) larger than V1.0's listing. V1.1-unique source fragments: an `IRQ LDA $FB` handler line, extra `QWERT` (tune-control) state rows, and a `>TR` label — i.e. a reworked IRQ entry + extra per-tune control state. Editor-side this is still the same V1.0 editor; V1.1 designates the replay. Both V1.0 and V1.1 players appear across HVSC's 1,170 HardTrack tunes. |
| **V1.0+ "6 speed"** | **~1997** | "Hardtrack Composer V1.0+ [6 speed]" by **Beverly Hills Group** (CSDb #36647); single packed file `HARDTRACK V1.0+6` on disk `[CENTRAX/AGONY!]` | code adds **Glover** (Samar Productions), ex-handle **Shatter/BHG** — real name **Łukasz Baran** — atop Brush + Longhair | A third-party patch of V1.0 raising the IRQ multispeed to **6×** (so up to 6 player calls per frame for finer timing/digi-ish effects). Per the bundled `.inf0`: "Done by Shatter/Beverly Hills Group (now Glover/Samar.)", uploaded by CenTraX/Agony. Glover (Łukasz Baran) was active in Samar in 1997 (CSDb SID #13597 "For North Party / 1997"), dating this ~1996-97. |
| **Tape version** | (undated; mirror entry 2005) | single packed file `HARDTRACK TAPE` on disk `]CENTRAX/AGONY![` | (repack of V1.0) | A tape-loadable build of the editor for cassette-based setups. No engine difference established; it is a loader/packaging variant of V1.0. |
| **"V2.0"** | — | **UNVERIFIED** | — | A single 2002 c64power.com forum poster (`Slay_`) referred to "v2.0" being tested. No CSDb release, no binary, no other corroboration. Treat as rumour / possible confusion until a binary surfaces. |

### Multispeed note
The base engine is CIA-timer driven. Stock V1.0/V1.1 run at the standard multispeed range
(research.md: up to ~6×); the BHG "6 speed" build hard-sets/extends the multispeed to 6×.
Init `$1000` / play `$1003` per the engine convention (research.md). Confirm exact per-tune
speed via `siddump`/PSID `speed` bit at extraction time — do not assume from the version name.

## 4. HVSC footprint
- `hvsc84.db`: **1,170** SIDs classified `HardTrack_Composer` (matches the brief).
- Glover's own HardTrack tunes are in HVSC (`MUSICIANS/G/Glover/Hardtrack.sid`,
  `Hardtrack_final.sid`) — the 6-speed author dogfooding his own variant.
- Other HardTrack files: `MUSICIANS/K/Kosa/Hardtrack.sid`, `MUSICIANS/D/Decoy/Hardtrack.sid`
  (the latter already has a `.usf` + `.sidfinity.sid` from a prior session).
- No HVSC `DOCUMENTS/` player doc exists for HardTrack — the CSDb forum spec (§2) and the
  SDK source are the only format references.

## Leads to follow
- **Date V1.1 precisely:** disassemble `PLAYER_V1.1.bin` vs `PLAYER_V1.0.bin` and look for an embedded build date, or grep HVSC HardTrack SIDs for the V1.1 player signature to bound the date by earliest V1.1-using tune.
- **Confirm/refute "V2.0":** search CSDb release list under Elysium/Brush and Pokefinder for any Hardtrack 2.0; if none, mark the c64power mention as confusion in the version table.
- **6-speed exact date + Glover identity:** fetch CSDb scener page for Glover/Shatter (Samar) and the BHG group page (#…) to pin the 6-speed year; cross-check `Hardtrack_Composer_v1_-6speed-.d64` directory date (mirror lists 2005-12-12, which is the *upload* date, not authoring).
- **Printed manual:** the only first-party prose spec is the boxed Tim Soft Polish manual (auctioned, c64scene.pl t=584). Watch for a scan on c64scene.pl / archive.org.
- **Glover's player mod scope:** disassemble `HARDTRACK V1.0+6` to see whether the 6× change is replay-only (affects the `$1003` dispatch rate) or also alters the data format — relevant to whether 6-speed tunes need a distinct extraction path.
