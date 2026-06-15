---
source_url: various (GitHub search, web search 2026-06-15)
fetched_via: WebSearch + WebFetch
fetch_date: 2026-06-15
author: N/A
content_date: 2026-06-15
reliability: secondary
---

# OdinTracker — Third-Party Tool Support Survey

## libsidplayfp / sidplayfp
No OdinTracker-specific handling found in any libsidplayfp source.
OdinTracker SIDs play as generic PSID (the packed player is self-contained 6502 code;
sidplayfp executes it natively without any engine-specific knowledge).

## VICE
No OdinTracker-specific handling found. Same as libsidplayfp — generic PSID execution.

## SID Factory II (github.com/Chordian/sidfactory2)
No OdinTracker import capability. SID Factory II imports GoatTracker, CheeseCutter, MOD.
No search result mentions OdinTracker support.

## GoatTracker / GoatTracker 2
No OdinTracker import capability. Separate engine/format entirely.

## CheeseCutter
No OdinTracker import capability found.

## SidWizard
No OdinTracker import capability found.

## DeepSID (github.com/Chordian/deepsid)
DeepSID uses sidid.cfg for player identification and plays via JSIDPlay2/jsSID.
No OdinTracker-specific player code found in PHP (info.php) or JS (sidplayer.js).
OdinTracker SIDs are identified via the sidid.cfg signature and displayed as
engine="OdinTracker" in the HVSC metadata.

## cadaver/sidid
Canonical engine-identification source. Contains OdinTracker signature + attribution.
See github_sidid_signature.md for full details.

## Conclusion

**No third-party C64 tool imports, converts, or has special handling for OdinTracker files.**
The only external tool that mentions OdinTracker at all is cadaver/sidid (for detection only).
This means:
1. No format documentation exists beyond the OdinTracker source code itself.
2. Our decompiler must work purely from the primary source (vplayer.s + defines.s + tracker.s).
3. SID playback via libsidplayfp is standard PSID — no emulation issues expected.
