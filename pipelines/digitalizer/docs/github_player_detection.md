---
source_url: multiple (cadaver/sidid, WilfredC64/player-id, Chordian/deepsid, hvsc.de, csdb.dk)
fetched_via: direct
fetch_date: 2026-06-13
author: various
content_date: 2006–2026
reliability: primary (sidid sources); secondary (CSDb metadata)
---

# Digitalizer — Player Detection Survey

## 1. cadaver/sidid (https://github.com/cadaver/sidid)

**Status: DETECTS Digitalizer — two entries confirmed.**

- `Digitalizer_V3.0` — 32-byte exact match, no wildcards
- `Digitalizer_V2.x` — 7-byte loose match, 2 wildcard pairs
- `Olav_Moerkrid` — 3-chained-pattern match (the runtime player, not just the tool binary)
- `Panorama` — single pattern, likely the Panoramic Designs release player

See `github_sidid_signature.md` for full byte sequences and analysis.

Scanner behavior: linear scan of entire file, no fixed offset. Multi-pattern entries
use sequential forward scan (match A then continue from that position for B, etc.).

---

## 2. WilfredC64/player-id (https://github.com/WilfredC64/player-id)

**Status: DETECTS Digitalizer — same entries as cadaver, PLUS a different Olav_Moerkrid pattern.**

Rust-based rewrite, V2 signature format. Digitalizer entries identical to cadaver's.
The Olav_Moerkrid entry differs — see `github_sidid_signature.md` for both versions.

Additional player: `Oeyvind_Jergan` — a different Norwegian scener's player, present
in both cadaver and WilfredC64.

---

## 3. DeepSID (https://github.com/Chordian/deepsid)

**Status: INDIRECT detection only via sidid lookup.**

`php/pretty_player_names.php` contains:
```php
'Olav_Moerkrid' => "Olav Mørkrid's player"
```

No `Digitalizer_V3.0`, no `Digitalizer_V2.x`, no `Panorama` entries in the
pretty_player_names.php mapping. This means:
- HVSC SIDs tagged as `Olav_Moerkrid` by sidid will display as "Olav Mørkrid's player" in DeepSID
- HVSC SIDs tagged as `Digitalizer_V3.0` or `Digitalizer_V2.x` will display with the raw sidid key
- The `Panorama` entry has no pretty-name mapping

**Relevant PHP files for player detection in DeepSID:**
- `php/sid_id.php` — SID identification
- `php/player.php` — core player functionality
- `php/player_list.php` — player list
- `php/pretty_player_names.php` — display name mapping (~200 entries)

DeepSID does NOT have special-case Digitalizer handling beyond the sidid-based name lookup.

---

## 4. libsidplayfp / VICE

**Status: NO Digitalizer-specific handling found.**

libsidplayfp is a generic PSID/RSID emulator. It plays any PSID file by running the
embedded 6502 code. There is no player-specific code path for Digitalizer.
VICE similarly: no Digitalizer-specific handling. Both play Digitalizer SID files
generically via the PSID init/play interface.

---

## 5. SIDdecompiler (https://github.com/Galfodo/SIDdecompiler)

**Status: NO Digitalizer support.**

Only has enhanced label names for Rob Hubbard compositions. Does not support
Digitalizer or other tracker-specific decompilation.

---

## 6. JSIDPlay2 (https://github.com/umjammer/JSIDPlay2)

**Status: Unknown — likely inherits sidid.cfg detection but no Digitalizer-specific code.**

Uses libsidplayfp core. No Digitalizer-specific source found in top-level directory scan.
Would need deeper src/ exploration to confirm.
OPEN: Does JSIDPlay2's Java layer have any Digitalizer-specific handling?

---

## 7. HVSC Player Database (https://hvsc.de/players)

**Status: Page not fully loaded during fetch — content blocked.**

The HVSC maintains a list of known players at hvsc.de/players. The Digitalizer entry
(if any) would give canonical counts of how many SIDs in HVSC use this player.
OPEN: Fetch this page with a JavaScript-capable browser or find a cached version.

---

## 8. Archive.org / Zimmers FTP

**Status: Binary available, not parsed.**

Zimmers FTP (https://c64.rulez.org/pub/c64/Tools/Music/Editor/) has:
- `Olav_M0rkrids_Digitalizer_v2,8[Panoramic].zip` — 8.3K (1999-06-25)
- `Olav_M0rkrids_Digitalizer_v2_8.zip` — 8.3K (1999-06-25)

Both are V2.8. The `[Panoramic]` suffix = the Panoramic Designs release version.
CSDb has official downloads for V2.2, V2.5, V2.7, V2.8, V3.0, V3.5.

---

## 9. sidid.cfg Format Reference (from sidid.c source)

The sidid.cfg config file format, as confirmed by reading sidid.c:

```
TOKEN = player_name | hex_pair | ?? | AND | END

player_name  ::= any token that is NOT a 2-hex-char, not "??", not "AND", not "END"
hex_pair     ::= two hex digits (00..FF) — matches exact byte
??           ::= wildcard, matches any single byte
AND          ::= "skip forward in file until next byte of pattern matches"
END          ::= signature match success
```

Multi-pattern entries: player name → pattern1 END → pattern2 END → ... (all must match
in forward order from each preceding match position).

The scanner does NOT use fixed offsets. It scans the raw binary starting from position 0.
This means signatures can appear ANYWHERE in the SID file (load address region).

---

## Leads to follow

- OPEN: Fetch DeepSID's `php/sid_id.php` to confirm how it calls sidid and which entries
  it remaps. URL: https://raw.githubusercontent.com/Chordian/deepsid/master/php/sid_id.php
- OPEN: Fetch HVSC player page with working JS: https://hvsc.de/players — may list
  Digitalizer SID count in HVSC.
- OPEN: JSIDPlay2 src/ subtree — search for "sidid" or "Digitalizer" in Java source.
  URL: https://github.com/umjammer/JSIDPlay2/tree/master/jsidplay2/src
- OPEN: Blues Muz' player (coded by same V3.5 contributors 6R6/Kjell Nordbo) — does
  sidid.cfg have a "Blues_Muz" entry that might cover V3.5-era Digitalizer SIDs?
  The Blues Muz Player V1.0 was released Jun 1994 (Demozoo) by Olav Mørkrid himself.
