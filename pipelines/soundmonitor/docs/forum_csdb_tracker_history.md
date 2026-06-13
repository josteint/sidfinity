# Soundmonitor — CSDb forum + tracker-history lineage

Cluster: forums + wikis + Usenet (CSDb forum/comments + cmatsuoka tracker-history).
This file establishes the **version/variant lineage** (priority 3) and the
Soundmonitor↔Rockmonitor↔MusicMaster relationships.

---

## Source A — CSDb release #59929 (comments thread)

```
source_url:   https://csdb.dk/release/?id=59929
fetched_via:  WebFetch (Claude Code)
fetch_date:   2026-06-13
author:       multiple sceners (see below)
content_date: release dated 1986-10; comments later
reliability:  secondary
```

Release: **Soundmonitor V1.0 by Chris Huelsbeck (1986)**, type "C64 Tool",
released October 1986.

Substantive technical comments (verbatim, with handle):

- **Steppe:** "released in issue 10/86 of the german commercial magazine 64'er
  as a type-in listing"
- **Six:** "I take it Rockmonitor was a modified version of this?"
- **tlr:** "@six: yes." — i.e. **Rockmonitor is confirmed by sceners to be a
  modified Soundmonitor.**

No init/play addresses, byte layout, or ripping procedure are discussed in the
CSDb comments themselves. The comment value is the lineage confirmation.

---

## Source B — cmatsuoka "tracker-history" / soundmonitor.txt

```
source_url:   https://github.com/cmatsuoka/tracker-history/blob/master/soundmonitor.txt
fetched_via:  WebFetch (Claude Code); GitHub blob (403 on raw, content via render)
fetch_date:   2026-06-13
author:       Claudio Matsuoka (tracker-history project), citing C64-Wiki + HVMEC + CSDb
content_date: file curated ~2010s; events 1986-1987
reliability:  secondary (curated catalogue, cites CSDb + HVMEC + C64-Wiki)
```

This is the cleanest **canonical lineage** for the family. Full record, verbatim:

```
soundmonitor_10
Name: Soundmonitor V1.0
Author: Chris Hülsbeck
Comment: a.k.a. Music Master            <-- "Music Master" == the Soundmonitor replayer
Date: 1986-10           # csdb release 59929

soundmonitor_11
Name: Soundmonitor V1.1
Author: The Leader/Computer Cracking Team
Date: 1986-12-28        # csdb release 10198
Based on soundmonitor_10

musicmaster_13
Name: Music Master V1.3
Author: The Syndicate
Date: 1987
Based on soundmonitor_11

rockmonitor_2
Name: Rockmonitor II
Author: Marco Swagerman & Oscar Giesen
Date: 1987
Based on soundmonitor_10   [ Digital channel ]

digitronix
Name: Digitronix
Author: RAB/The Lightning Duo
Date: 1987
Based on rockmonitor_2     [ 2 sample channels ]
```

Plus a pouet.net quote captured in the file (re: Digitronix author):
> "in my c64 days I did a program called Digitronix which was basicly a
> Rockmonitor (1 digichannel) clone but by using 4bit samples instead of
> eight and 'mixing' them on the NMI you had 2 channels of samples and 3
> channels of SID."

### Lineage interpretation (load-bearing for the parser/variants)

1. **Soundmonitor V1.0** (Hülsbeck, 1986-10) is the root. The embedded
   replayer it bundles is called **"Music Master"** (a.k.a. MusicMaster). So
   inside the HVSC PSID population, a "MusicMaster"-driven tune and a
   "Soundmonitor V1.0"-driven tune use the **same replayer core** — they are
   NOT two different engines at the write-stream level. (Caveat: the wiki
   "MusicMaster" *editor* page is a DIFFERENT 1983 program — see the
   `forum_wikis_*` file; do not conflate.)
2. **V1.1** (The Leader/CCT, 1986-12) and **V1.3 "Music Master"** (The
   Syndicate, 1987) are cracker-modified descendants "Based on" the prior
   version. These are the in-the-wild variants HVSC will contain alongside
   pristine 1.0. Expect small replayer deltas (relocation, speed) rather than
   a new format.
3. **Rockmonitor II** (Swagerman & Giesen, 1987) is "Based on
   soundmonitor_10" **+ a Digital channel** — i.e. the SID-music core is the
   Soundmonitor core, with a 4th digi/sample channel bolted on. This matches
   the C64-Wiki/Usenet claim that Rockmonitor = Soundmonitor + samples.
   **→ Rockmonitor's SID (non-digi) part should be format-compatible with
   Soundmonitor; the digi channel is the additive difference.**
4. **Digitronix** is a further Rockmonitor derivative (2× 4-bit sample
   channels via NMI mixing). Mentioned for completeness; out of the
   Soundmonitor SID-core scope.

### Practical consequence for SIDfinity

- Treat **Soundmonitor 1.0 / 1.1 / MusicMaster 1.3** as one engine family with
  per-version replayer deltas (the variant axis = priority 3).
- **Rockmonitor** = same SID core + extra digi channel; if HVSC's Soundmonitor
  bucket includes Rockmonitor tunes, the SID-write model is shared but the digi
  channel needs separate (cycle-strict, Mode 2) treatment, analogous to Chimera.
- HVMEC (the "High Voltage Music Editor Collection") hosts per-version editor
  binaries at the `utenti.multimania.it/ice00/HVMEC/.../Soundmonitor/{1.0,1.1,1.3}/`
  paths cited in the file — a place to obtain each version's actual replayer for
  disassembly (see Leads).

## Leads to follow

- **HVMEC editor binaries per version** — the tracker-history file cites
  `utenti.multimania.it/ice00/HVMEC/CONTROL/Tracker/Soundmonitor/{1.0,1.1,1.3}/`
  and `.../Digitronix/V1/`. Multimania is long dead; look for the HVMEC mirror
  (it is distributed inside HVSC's `DOCUMENTS/` or on CSDb) to get each version's
  replayer for side-by-side disassembly of the variant deltas.
- **CSDb release #10198** (Soundmonitor V1.1, The Leader/CCT) and the Music
  Master V1.3 / Rockmonitor II releases — pull each release page for download +
  any scener comments naming the replayer entry points.
- **pouet.net topic which=1035** — the Digitronix/Rockmonitor NMI-mixing
  discussion thread (referenced by tracker-history) may have more digi detail.
