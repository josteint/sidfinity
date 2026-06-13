---
source_url: multiple — see per-section headers
fetched_via: direct (WebFetch/WebSearch)
fetch_date: 2026-06-13
author: various
content_date: various
reliability: secondary (aggregated from public sources; no primary source code found)
---

# GitHub parser notes — RoMuzak

## Summary: No public RoMuzak parser found

A systematic search of GitHub (cadaver/sidid, WilfredC64/player-id, Chordian/deepsid,
OpenMPT/openmpt, neumatho/NostalgicPlayer, libsidplayfp, VICE) found **no open-source
parser, decompiler, or format converter specifically for RoMuzak**.

The player is identified by byte signature only. No format specification document exists
in any of the searched repositories.

---

## Tools that DETECT RoMuzak (but do not parse the format)

### cadaver/sidid
- URL: https://github.com/cadaver/sidid
- Status: detects V6.x and V7.x by byte pattern (see `github_sidid_signature.md`)
- Parser: none — identification only

### WilfredC64/player-id
- URL: https://github.com/WilfredC64/player-id
- Status: Rust rewrite of sidid; same signatures; no parser
- Config: `config/` directory (contains sidid.cfg); `doc/Signature_File_Format.txt` for format spec

### DeepSID (Chordian/deepsid)
- URL: https://github.com/Chordian/deepsid
- Status: uses sidplayfp/JSIDPlay2/WebSid WebAssembly backends; no player-specific code for RoMuzak
- Player.js, player_list.php, pretty_player_names.php: **no RoMuzak entries found**
- Speed handling: generic from PSID header `speed` field; no RoMuzak-specific override

### libsidplayfp / VICE
- URL: https://github.com/libsidplayfp/libsidplayfp
- Status: plays RoMuzak SIDs as generic PSID (via the 6502 emulator); no player-specific handling
- Confirmed: no RoMuzak-specific code found in libsidplayfp codebase

---

## Player performance characteristics (from community sources)

Source: Polish C64 scene forum (https://www.c64scene.pl/viewtopic.php?t=112)

- RoMuzak V6.3 is known to consume "an enormous amount of raster time"
- One developer reported it took "twenty-some raster lines" per call — enough to break
  between interrupt calls in a demo context
- The player has a **per-channel call structure** — individual channel routines can be called
  separately (a developer in that thread successfully decomposed it this way)
- The player code contains **author/metadata validation routines** that can be stripped to save CPU
- The in-binary string is: `** ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!!`
  (this appears to be a banner/credit string, distinct from the compact "ROMUZAK89" tag at +$09)

---

## Memory layout (from research.md — prior project work)

Already confirmed from existing project research (not duplicated fully here):

```
+$0000  JMP init
+$0003  JMP play
+$0006  JMP stop/reset
+$0009  "ROMUZAK89" (9-byte ASCII tag)
+$0012  Three 2-byte pointers to per-voice pattern data
+$0018  Instrument parameter block (~136 bytes): ADSR, waveform, PW, filter, vibrato/portamento
+$00A2  Standard frequency table (96 entries, consistent across V6.x tunes)
+$0202  Player code (~2636 bytes)
```

Total binary size: 2747–4041 bytes.

---

## DeepSID player DB entry (indirect)

DeepSID's online interface for `MUSICIANS/D/Detert_Thomas/RoMuzak_V6_3_intro.sid`
(https://deepsid.chordian.net/?file=MUSICIANS%2FD%2FDetert_Thomas%2FRoMuzak_V6_3_intro.sid)
shows player info including load address, init address, play address, and speed — but
this is read from the PSID header, not from RoMuzak-specific parsing.

---

## Leads to follow

- **OPEN:** No parser found — the full USF decompiler must be written from scratch via RE.
- **OPEN:** WilfredC64/player-id has a `doc/Signature_File_Format.txt` — fetch this to understand
  how future signatures could be structured/extended for RoMuzak subvariants.
- **OPEN:** DeepSID's player DB (PHP backend, `players_info` table) may have additional metadata
  not exposed via API. The `speeds` field in player.php is worth querying for RoMuzak entries
  (would confirm CIA vs VBlank timing per version).
- **OPEN:** libsidplayfp issue tracker — search for "RoMuzak" to see if any correctness bugs
  have been filed that reveal format edge cases.
- **OPEN (community):** The developer on c64scene.pl who decomposed the player into per-channel
  calls may have documented their work elsewhere (CSDb, Pouet, or personal site). Username "skull"
  (Polish scene) worth tracking down.
