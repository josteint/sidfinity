# HardTrack Composer — Release Notes & Player Versions (V1.0 vs V1.1)

> **Provenance**
> - source: `local: pipelines/hardtrack/docs/_artifacts/sdk/extracted/RELEASE_NOTES.bin`,
>   `PLAYER_V1.0.bin`, `PLAYER_V1.1.bin` (Elysium SDK, already extracted).
> - fetched_via: local artifacts + byte/string decode + structural diff of the two
>   tokenised assembler sources.
> - fetch_date: 2026-06-13
> - author: Longhair / Milosz Ignatowski (player), Brush (editor), Elysium / Parados.
> - content_date: 1992 (V1.0); V1.1 shortly after.
> - reliability: **primary** for the binary facts (sizes, strings, code delta);
>   **inferred** where a behaviour change is deduced from the source diff rather than
>   from prose release notes (the textual readme on disk is crunched — see §4).

---

## 1. What `RELEASE_NOTES.bin` actually is

Despite the filename, `RELEASE_NOTES.bin` is **not** a text file — it is the
**assembled V1.0 player ($1000) plus a demo tune** (a SID-shaped blob). Confirmed:

- First bytes `00 10` = load address **$1000**; then `4C 60 10` (`JMP $1060` = init)
  and `4C D8 10` (`JMP $10D8` = play). Identical vector layout to every HVSC
  HardTrack tune.
- Embedded title string at **$1020**:
  ```
  PLAYER 1.0 BY LONGHAIR/ELYSIUM! - MUSIC DONE BY LONGHAIR/ELYSIUM
  ```
- $1588/$15E8 hold the note→frequency tables; $16xx the runtime state; $18xx the
  subtune-dispatch tables — exactly the player documented in
  `csdb_player_source.md`.
- Its first 1024 bytes match `HT_7_1.sid`'s player 941/1024 (the differences are the
  song-specific config/data, not code), proving the player code is shared HVSC-wide.

So the "release notes" content is the **byline** ("PLAYER 1.0 BY LONGHAIR/ELYSIUM")
and the version stamp. The narrative Polish manual is a separate, crunched file
(`tmp/hardtrack/OUT_PRZECZYTAJ_MNIE.prg`, "Przeczytaj mnie" = "Read me") that cannot
be string-extracted without unpacking (BASIC stub `SYS 2059` → crunched payload).

---

## 2. The two player versions in the SDK

`PLAYER_V1.0.bin` and `PLAYER_V1.1.bin` are tokenised **Elysium turbo-assembler
SOURCE** files (header byte `09`, `.TEXT`/`.BYTE` directives, a PETSCII symbol table
with high-bit terminators). They are the source of Longhair's player routine, one per
version.

| Fact | V1.0 | V1.1 |
|------|------|------|
| Source file size | 5,309 B | 5,646 B (+337 B source) |
| **Assembled code length** (hdr word @ +6) | `$29B` (667 B) | `$2D5` (725 B) → **+58 bytes of code** |
| Title string | `PLAYER V1.0 BY LONGHAIR/ELYSIUM!` | `PLAYER V1.1 BY LONGHAIR/ELYSIUM` |
| Music byline | `MUSIC … BY LONGHAIR/ELYSIUM` (in RELEASE_NOTES build) / `MUSIC BY YOU` placeholder (SDK src) | `MUSIC BY YOU` placeholder |
| Distinctive label | — | **`QWERT`** ×2 (at src $1421/$1427, near `SPEEED`/`START`), absent in V1.0 |
| `IRQ LDA $FB` line | inside body | **hoisted** to the early region (visible at src $00B8) |

Both versions share the same symbol table prefix
(`INIT IRQ NRTUNE TR TRS PT PTS TRPOS PTPOS NRTUNEQ D418 …`), i.e. the same overall
architecture: 8-subtune dispatch, 3-voice loop, track/pattern streams, instrument
macros (wave/pulse/filter), arp, glissando, multispeed divider.

### What changed V1.0 → V1.1 (inferred from the diff)

The +58 assembled bytes plus the new `QWERT` label clustered around the
`SPEEED`/`START` symbols, and the hoisted `IRQ` entry, indicate the V1.1 change is in
the **play-entry / speed-setup path** — most consistent with a **multispeed / IRQ
dispatch refinement** (e.g. additional per-subtune speed handling or a guarded
re-entry). This is an *inference from the source structure*; the prose changelog is
in the crunched Polish readme and was not recoverable here. It is NOT a change to the
musical data format (the pattern/track/instrument symbol set is byte-identical
between the two), so the **USF extraction model is version-independent**.

---

## 3. Which player ships in HVSC

Fingerprinting all 1,170 HVSC `HardTrack_Composer` tunes on init/play vectors found
two dominant assembled layouts (same engine, relocated):

| Layout | init / play vectors | Tables | Example | Count (approx) |
|--------|--------------------|--------|---------|---------------|
| **A — original ($1000)** | init `JMP $1060`, play `JMP $10D8` | $18xx subtune, $194A pattern, $1588/$15E8 freq | `Wodnik/HT_7_1.sid`, `RELEASE_NOTES.bin` | majority |
| **B — Bzyk/Samar relocated** | init `JMP $1080`, **play `JMP $1061`** | $16xx/$17xx | `Bzyk/Schallow.sid`, `Bzyk/Introway.sid` | ~118 |
| (relocated off $1000) | various | — | — | ~117 |

Layout B (play directly after init) is the later Polish-scene repack used heavily by
Bzyk (262 tunes) and others around 1998 (Samar/Oxygen). It is the same player logic
with a different memory map — likely V1.1 and/or the BHG 6-speed reassembly. The
extractor must therefore locate tables via the init-copied live pointers
(`$100A–$100F`), never by fixed address.

---

## 4. The crunched Polish manual

`tmp/hardtrack/OUT_PRZECZYTAJ_MNIE.prg` ("PRZECZYTAJ MNIE!" = "READ ME!") is the
official editor documentation, but it is a crunched executable (BASIC `SYS 2059`
launcher → packed payload), so its prose is not directly extractable. The d64
directory entry confirms it (`23 blk PRG 'PRZECZYTAJ MNIE!'` on
`Hardtrack_Composer_1_0_Timsoft_1994.d64`). To recover the manual text, the payload
would need to be run/depacked in an emulator (out of scope here). Polish comment
fragments inside `EDYTOR.SRC.bin` give the editor's UI vocabulary (e.g.
"PROCEDURA DO PORUSZANIA SIE W PATERNIE" = "procedure for moving within a pattern",
"PROGRAM KASUJACY PATERNY" = "pattern-clearing routine",
"PROCEDURA DO WYLACZANIA KANALOW" = "channel-mute routine").

---

## 5. Summary

- `RELEASE_NOTES.bin` = the assembled **V1.0 player + demo tune**, byline
  "PLAYER 1.0 BY LONGHAIR/ELYSIUM".
- **V1.0 → V1.1**: +58 bytes of player code, a new `QWERT` label near the speed/start
  logic, a hoisted `IRQ` entry, and a bumped title string. Inferred to be a
  multispeed/IRQ-dispatch refinement; the **musical data format is unchanged**.
- Two assembled layouts ship in HVSC (original $1000 and a Bzyk/Samar relocation);
  both decode through the same USF model.
