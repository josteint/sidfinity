---
source_url: https://github.com/Chordian/sidfactory2 + https://github.com/Chordian/DeepSID + https://github.com/WilfredC64/player-id + https://github.com/cadaver/sidid + https://github.com/libsidplayfp/libsidplayfp + https://github.com/theyamo/CheeseCutter + https://github.com/realdmx/c64_6581_sid_players
fetched_via: direct (shallow git clones, grepped 2026-06-12)
fetch_date: 2026-06-12
author: various
content_date: repo heads as of 2026-06-12
reliability: primary (negative results verified by grep over full source trees)
---

# GitHub parser survey for DMC — verified negatives

Every plausible open-source C64 music tool was shallow-cloned and grepped
for `dmc` / `graffity` / `demo music creator` (case-insensitive). Result:
**no open-source project parses or disassembles the DMC player format.**

| Repo | DMC content found | Notes |
|---|---|---|
| `Chordian/sidfactory2` | none | Only converter is `source/runtime/editor/converters/jch/converter_jch.{h,cpp}` (JCH .dat) + GT/MOD. **SF2 does NOT import DMC.** The JCH converter is still the closest cross-format relative (JCH's editor lineage is the same Danish tradition); `converter_jch.cpp` is a worked example of lifting an editor-native binary into SF2's model. |
| `Chordian/DeepSID` | signature names only | `utility/sidid_100/sidid.cfg` carries `DMC`, `(DMC_V4.x)`, `(DMC_V5.x)`, `DMC_V6.x` sigs; `js/browser.js` exposes them as search types; `php/annex_help.php` lists DMC v4.x/v5.x as player-search examples. No parser, no player internals. |
| `WilfredC64/player-id` | signatures only | `config/sidid.cfg` — same signature set as cadaver/sidid. |
| `cadaver/sidid` | signatures only | `sidid.cfg` DMC / V4.x / V5.x / V6.x patterns (already transcribed in research.md §SIDId Signature Patterns). |
| `libsidplayfp/libsidplayfp` | none | Player-agnostic emulator; no per-player handling. |
| `theyamo/CheeseCutter` | none | CheeseCutter is the JCH-NewPlayer lineage (its `player/` is a NewPlayer derivative); zero DMC references. |
| `realdmx/c64_6581_sid_players` | none | "Original and reverse-engineered music players" — has annotated ASM for Galway, Gray, Tel, Dunn, Deenen, Bjerregaard, Whittaker, Ouwehand, Hubbard, FAME/Bulka, Audial Arts — **but no DMC/Graffity**. Best-in-class example of the artifact we want for DMC; worth watching for additions. |

GitHub repo-search API queries `demo+music+creator+c64`, `dmc+sid+c64`,
`demo+music+creator` returned no relevant repos (only false positives).
grep.app blocked by Vercel challenge; unauthenticated GitHub code search
unavailable (no `gh` on this host).
