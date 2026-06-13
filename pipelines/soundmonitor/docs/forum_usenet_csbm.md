# Soundmonitor — Usenet (comp.sys.cbm) + funet/zimmers FTP archive

Cluster: forums + wikis + Usenet (the **Usenet** + canonical-archive leg).
Carries: (a) period (1992-2017) Usenet mentions confirming the
Soundmonitor↔Rockmonitor↔Future-Composer relationships and the
"SID-only vs digi" distinction; (b) the actual archived ripper/relocator/
editor binaries that let you obtain & relocate Soundmonitor data.

---

## Source A — comp.sys.cbm (Usenet, via Google Groups archive)

```
source_url:   https://groups.google.com/g/comp.sys.cbm  (search: "Soundmonitor")
fetched_via:  WebFetch (Claude Code) over the Google Groups archive index
fetch_date:   2026-06-13
author:       various posters (named per item)
content_date: 1992-2017 (per post)
reliability:  secondary (period primary-discussion, but no byte-level format)
```

NOTE on extraction limits: Google Groups' archive renders post BODIES via
JavaScript, so WebFetch could only recover thread **subjects + authors + dates
+ a one-line snippet** per item, not full message text. The bodies were not
machine-extractable through the available tools. The value below is the
catalogue of WHO discussed it and WHAT relationship each post asserts.

Historical Soundmonitor / Rockmonitor mentions found (subject — author — date —
snippet):

1. **"Using samples in demos?"** — Lars Forsberg — 2000-03-19 —
   "**ROCKMONITOR is based upon** the **SOUNDMONITOR** documentation"
   (snippet around samples taking priority over editor ease-of-use).
   → Independent Usenet confirmation that Rockmonitor derives from
   Soundmonitor (matches CSDb tlr + tracker-history "Based on soundmonitor_10").
2. **"Soundtracker for C64 / music of Netherworld?"** — Lasse Öörni
   (Cadaver) — 2002-11-26 — "**Soundmonitor**, which can only do the SID-part"
   (vs tools combining digitized + SID sound).
   → Confirms vanilla Soundmonitor = **SID-only, no digi**; the digi channel is
   the Rockmonitor addition. Lasse Öörni = author of GoatTracker, a credible
   C64-audio authority.
3. **"Which music editor do you prefer?"** — Anders Carlsson — 2000-12-01 —
   "extremely old **Soundmonitor** and some Future Composer '88".
4. **"SID Editor"** — ChillyWin — 1999-04-15 — "**Soundmonitor**, published in
   64'er mag issue Oct.86", effective but **producing large files**.
   → Corroborates 64'er 10/86 origin + the >10 KB song-size constraint.
5. **"JCH musix"** — Crimson Knight — 1993-07-20 — asks whether "**soundmonitor**
   files" play on **Rockmonitor** and can be edited through **Future Composer**.
   → Period evidence that users treated Soundmonitor files as (at least
   partly) loadable by Rockmonitor — consistent with a shared SID core.
6. **"STEREO PROGRAMS"** — William Jhun — 1993-03-03 — describes a program as an
   "**enhancement of Soundmonitor/Rockmonitor**" with **6-voice stereo SID**
   (dual-SID) capability.
   → A further Soundmonitor/Rockmonitor derivative exists targeting 2× SID.
7. **"SYS30120 songs..."** — Gene Buckle — 1995-08-02 — "**SoundMonitor** or Sid
   music" conversion. (SYS30120 = $75A8, a different player's entry — context
   is format conversion, not Soundmonitor's own entry.)
8. **"SOUND/JAMmonitor files wanted..."** — Louis@bota.unine.ch — 1992-09-21 —
   seeks FTP sites hosting "**JAMmonitor or SOUNDmonitor files**".
9. Also-mentioned-in-passing (no technical content): "C64 jukebox software?"
   (Harry Potter, 2017-02-16); "Looking for music editors" (boompjes,
   1998-12-09); "C64 Music software?" (Samuel Lindeman, 1997-04-17).

### Usenet net findings (relationship axis)
- **Soundmonitor = SID-only**; **Rockmonitor = Soundmonitor + digi/samples**
  (Öörni #2, Forsberg #1). Cross-confirms the wikis + tracker-history.
- **Rockmonitor "is based upon the Soundmonitor documentation"** (Forsberg #1) —
  i.e. format-derived, not a from-scratch rewrite → SID-core compatibility is a
  reasonable working assumption (still must be disasm-verified).
- A **6-voice stereo** Soundmonitor/Rockmonitor enhancement existed (Jhun #6) —
  flag for dual-SID outliers in the HVSC bucket.
- No comp.sys.cbm post in the archive gives byte offsets, init/play addresses,
  or a ripping recipe. Usenet adds RELATIONSHIP + CONSTRAINT corroboration, not
  the binary spec.

---

## Source B — funet/zimmers FTP: c64/audio/editors/

```
source_url:   https://www.zimmers.net/anonftp/pub/cbm/c64/audio/editors/index.html
              (mirror: https://www.commodore.ca/manuals/funet/cbm/c64/audio/editors/)
fetched_via:  WebFetch (Claude Code)
fetch_date:   2026-06-13
author:       funet.fi CBM archive maintainers (descriptions are archive captions)
content_date: archive captions; binaries 1986-1987
reliability:  secondary (canonical binary archive + one-line captions)
```

Relevant archived **binaries** (filename — bytes — caption):

- **rockmonitor-2.prg** — 26254 — "Successor of soundmonitor with digiplayer"
- **rockmonitor-3.prg** — 17923 — (Rockmonitor v3)
- **rockmonitor-4.prg** — 20062 — (Rockmonitor v4)
- **mastercomposer.prg** — 23306 — "**Editor for Huelsbeck's tunes like Katakis**"

Notes:
- The funet caption "rockmonitor-2 = Successor of soundmonitor with digiplayer"
  is a THIRD independent statement of the Rockmonitor=Soundmonitor+digi fact.
- **mastercomposer.prg** ("Editor for Huelsbeck's tunes like Katakis") is a
  separate, later Hülsbeck-ecosystem editor — note it for lineage, but it is
  NOT the Soundmonitor replayer (Katakis used a later Hülsbeck driver). Don't
  fold MasterComposer tunes into the Soundmonitor bucket.
- The directory does **not** carry a bare "soundmonitor.prg" or a format `.doc`;
  the V1.0 editor lives in the 64'er listing / CSDb / HVMEC, not here.

---

## Source C — funet/zimmers FTP: c64/audio/utilities/

```
source_url:   http://www.zimmers.net/anonftp/pub/cbm/c64/audio/utilities/index.html
fetched_via:  WebFetch (Claude Code)
fetch_date:   2026-06-13
author:       funet.fi CBM archive maintainers
content_date: archive captions
reliability:  secondary
```

Relevant **tools** (filename — bytes — caption):

- **SM-Relocator.prg** — 3899 — "**Soundmonitor soundrelocator**"
  → A dedicated tool to RELOCATE Soundmonitor data — direct confirmation that
  the native replayer is fixed at $C000/$C020 and tunes had to be relocated by
  hand/tool to embed elsewhere. Useful: this tool's logic shows exactly which
  pointers in the data are position-dependent (the bar-address table / TRK
  pointers) — worth disassembling when modelling relocation.
- **MusicRipper.prg** — 1408 — "Assists in ripping music from other programs"
- **Digiripper-1.0.prg** — 2607 — "Assists in ripping digitized effects"
- **MusicAnalyzer3.sfx** — 10018 — "Version 3.0, allows play of IRQ musics + more"
- **Musicwizard.prg** — 17247 — "Tool to examine sounds"
- **Advanced Music Search v5.0.lnx** — 16403 — "Searches for music in other
  programs"

(These are generic period rip tools, not Soundmonitor-format-specific, except
SM-Relocator which IS Soundmonitor-specific.)

---

## Consolidated relationship map (this cluster's verdict on priority 4)

```
MusicMaster (Hülsbeck replayer core, written FIRST)
   └─ Soundmonitor V1.0  (Hülsbeck, 64'er 10/1986)         SID-only, $C000/$C020, not relocatable
        ├─ Soundmonitor V1.1     (The Leader/CCT, 1986-12)   cracker-mod
        ├─ Music Master V1.3     (The Syndicate, 1987)       cracker-mod  (NB: "Music Master"==replayer name)
        └─ Rockmonitor II        (Swagerman/Giesen, 1987)    + digi channel ("based upon SM documentation")
              ├─ Rockmonitor 3 / 4                            further digi versions
              └─ Digitronix       (RAB, 1987)                 2× 4-bit sample channels, NMI mix
   (… 6-voice stereo SM/Rockmonitor enhancement — Jhun 1993 — separate outlier)

SEPARATE (do NOT bucket as Soundmonitor):
   The Final Musicplayer (TFMP)   Hülsbeck optimized successor, 1987 → leads to TFMX
   MasterComposer                 later Hülsbeck-ecosystem editor (Katakis-era)
   "MusicMaster" (Compute! 1983)  unrelated Metcalf/Sugiyama keyboard sim
```

- **Is Soundmonitor an ancestor of later editors?** Yes — directly spawned the
  Rockmonitor series + Digitronix; and the wikis call it a conceptual basis for
  later Amiga/PC trackers. Hülsbeck's own optimized line (TFMP → TFMX) is a
  separate, non-compatible engine.
- **Is Rockmonitor format-compatible?** Per three independent sources
  (CSDb tlr, Usenet Forsberg/Öörni, funet caption) it is a Soundmonitor
  derivative whose SID part shares the Soundmonitor core, plus an additive digi
  channel. SID-core compatibility is the working hypothesis — verify by
  disassembly before relying on it.
- **Does MusicMaster == the Soundmonitor replayer exactly?** Yes — "Music
  Master" is the bundled Soundmonitor replayer (Hülsbeck wrote it before the
  editor; tracker-history lists it as "a.k.a. Music Master" and as the V1.3
  family name). It is NOT the 1983 Compute! "MusicMaster".

## Leads to follow

- **Disassemble SM-Relocator.prg** (funet `audio/utilities/`, 3899 bytes) — it
  enumerates exactly which Soundmonitor pointers are position-dependent (TRK bar
  pointers + the $BE00 bar-address table). Fastest route to a correct relocation
  / pointer model for the parser.
- **Disassemble rockmonitor-2.prg** (funet `audio/editors/`, "with digiplayer")
  to isolate the additive digi channel vs the shared Soundmonitor SID core, and
  confirm SID-core format compatibility.
- **Recover full comp.sys.cbm post bodies** for the technical threads (Forsberg
  2000-03-19; Öörni 2002-11-26; Jhun 1993-03-03; Crimson Knight 1993-07-20) via
  an NNTP archive that serves raw text (e.g. archive.org Usenet dumps,
  novabbs/eternal-september mirrors) — Google Groups only exposed subjects+
  snippets here.
- **forum64.de threads BLOCKED** this session (HTTP 403 to the scraper for both
  thread/60587 "Soundmonitor V1.0" and thread/145999 "Alte Sound-Formate"; the
  latter's search snippet asserts the Soundmonitor playroutine is at **$c000**
  and that the thread contains 6502 code examples for playing
  Soundmonitor/Future-Composer/Romuzak data). Retry via an authenticated/
  browser fetch or a Wayback snapshot (web.archive.org was also unreachable from
  this environment) — `thread/145999-alte-sound-formate` is the top remaining
  forum target for embed/play code.
- **Lemon64 thread t=15402** ("Looking for Sound-Monitor … download + manual?")
  returned HTTP 503 (rate-limited, Retry-After 3600 s) — retry later; may carry
  the English manual scan + ripping chatter.
