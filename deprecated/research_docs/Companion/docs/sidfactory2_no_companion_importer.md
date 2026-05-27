---
source_url: https://github.com/Chordian/sidfactory2/tree/master/SIDFactoryII/source/runtime/editor/converters
fetched_via: WebFetch
fetch_date: 2026-05-25
author: Chordian (Jens-Christian Huus)
content_date: ongoing (active project, open BETA)
reliability: primary (source tree listing)
---

# SIDFactory II has NO Companion importer

## Converter directories present

`SIDFactoryII/source/runtime/editor/converters/` contains:

- `cc/` — files: `converter_cc.cpp/.h`, `source_ct.cpp/.h`  (purpose unknown
  from listing alone; possibly CheeseCutter — see leads)
- `gt/` — files: `converter_gt.cpp/.h`, `source_sng.cpp/.h`  (GoatTracker
  .sng — search results confirm "imports Goattracker, CheeseCutter and MOD")
- `jch/` — JCH (Jens-Christian Huus's own old player / format), based on the
  initials matching the author
- `mod/` — Amiga ProTracker MOD
- `null/` — base/null converter
- `utils/` — shared utilities

Plus base files: `converterbase.cpp/.h`.

## Conclusion

**No "companion/", "hubbard/", or "murray/" subdirectory exists.** SIDFactory
II does NOT have a Companion importer. The official feature list (per
chordian.net SIDFactory page) lists support for "Goattracker, CheeseCutter and
MOD" only.

## Why this matters

- We cannot reuse Chordian's parsing — there's nothing to reuse.
- The Companion player is too primitive for SIDFactory II to be a natural
  target (no instruments-as-objects, no arp tables, no PWM — just notes +
  orderlist + freq lookup); converting Companion → SIDFactory II would
  lose nothing on the input side but require us to write the import code
  ourselves anyway.
