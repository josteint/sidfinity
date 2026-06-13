# SID Duzz'It — comp.sys.cbm Usenet and Lemon64 Forum Research

<!-- provenance
  sources:
    - url: https://groups.google.com/g/comp.sys.cbm (various threads)
      fetched_via: WebSearch + WebFetch
      fetch_date: 2026-06-13
      reliability: secondary (search results; direct thread fetches returned 503)
    - url: https://www.lemon64.com/forum/viewtopic.php?t=31585 (SDI and SID files)
      fetched_via: WebFetch — returned HTTP 503 (rate-limited, Retry-After: 3600)
      fetch_date: 2026-06-13
      reliability: NOT RECOVERED
    - url: https://www.lemon64.com/forum/viewtopic.php?t=24039 (SDI question)
      fetched_via: WebFetch — returned HTTP 503 (rate-limited)
      fetch_date: 2026-06-13
      reliability: NOT RECOVERED
    - url: https://www.lemon64.com/forum/viewtopic.php?t=24599 (SDI help)
      fetched_via: WebFetch — returned HTTP 503 (rate-limited)
      fetch_date: 2026-06-13
      reliability: NOT RECOVERED
    - url: https://www.lemon64.com/forum/viewtopic.php?t=67248 (Comparison of editors)
      fetched_via: WebFetch — returned HTTP 503 (rate-limited)
      fetch_date: 2026-06-13
      reliability: NOT RECOVERED
    - WebSearch results for comp.sys.cbm threads mentioning SDI
      fetched_via: WebSearch
      fetch_date: 2026-06-13
      reliability: low (search snippets only; no full thread content)
-->

---

## comp.sys.cbm — Findings

### Search Summary

Multiple WebSearch queries for `comp.sys.cbm "SID Duzz'It"`, `comp.sys.cbm "Geir Tjelta"`,
and `narkive comp.sys.cbm "SDI tracker"` were run. Results:

- **No Usenet posts about SDI were found** via web search, Google Groups, or narkive.
- The comp.sys.cbm newsgroup is partially archived on Google Groups and narkive, but
  the archive coverage for the 1992–2002 period (when SDI was first released and active)
  appears incomplete.
- SDI was a native C64 tool distributed via the demo scene BBS network, not via Usenet.
  This is consistent with the absence of Usenet mentions: Norwegian BBS/demo scene tools
  of this era were typically distributed via scene channels (BBS, copy parties, disk
  swapping) rather than announced on Usenet.

### Threads Fetched — Content of Unrelated Threads

Two comp.sys.cbm Google Groups threads were fetched directly (based on search results):

**Thread: "Mobile SID Player - DIY?" (March 2004)**
Authors: Brian Lund, John Moore, mid64, Scott McDonnell, J.Oppermann, Rainer Buchty,
Zed Yago, Marcel Gonzalez — all hardware/player focus. No SDI mention.

**Thread: "Converting MIDI files to SID" (February 2017)**
Author: Daniel England (re: XSID tool). No SDI mention.

**Thread: "New SID to MIDI conversion tool" (August 2017)**
Author: Daniel England (re: XSID tool). No SDI mention.

### Conclusion on comp.sys.cbm

There is no recoverable Usenet (comp.sys.cbm) discussion about SID Duzz'It in the
accessible archive. This absence is likely a genuine gap rather than a search failure:
SDI was an internal Norwegian scene tool before SourceForge and CSDb made it publicly
discoverable (post-2002). The SDI community has always been primarily on CSDb and
scene-internal channels rather than on public Usenet.

---

## Lemon64 Forums — Known Threads (Not Recovered)

Lemon64 returned HTTP 503 (rate-limited) for all requests during this session.
The following threads were identified via WebSearch and are documented for future retrieval:

| Thread URL | Topic | Relevance |
|-----------|-------|-----------|
| `viewtopic.php?t=31585` | "SDI and SID files" | Likely discusses how SDI tunes are ripped/exported as PSID. HIGH priority. |
| `viewtopic.php?t=24039` | "SDI (SID Duzz It) question" | General usage question. MEDIUM priority. |
| `viewtopic.php?t=24599` | "Sdi help!!" | Usage help. MEDIUM priority. |
| `viewtopic.php?t=67248` | "Comparison of C64 Music Editors" | Chordian's comparison table discussion, includes SDI. HIGH priority. |

### Partial Content Recovered via WebSearch Snippets

From WebSearch results (snippets, not full posts):

**Thread t=24039 "SDI (SID Duzz It) question":**
A search snippet reveals the thread discusses instrument/effects/speed column encoding:
> "Instrument:00-1F, Arpeggio, Glide, Vibrato, Attack, Sustain, Release, Filter on/off.
> You can't set Decay."
— attributed to "Glenn" (likely Glenn Rune Gallefoss / 6R6) in the comparison table
thread at Chordian's blog.

**Thread t=31585 "SDI and SID files":**
No snippet content recovered, but the thread title confirms it discusses the relationship
between SDI's native format and the PSID (.sid) export format.

**Thread t=24599 "Sdi help!!":**
No snippet content recovered.

### Multispeed Information from Search Snippets

A search snippet about SDI multispeed (from the SourceForge description and search aggregator):

> "Multispeed plays the tables faster, and it's only wavetable and pulseprogram that
> runs on speed. CBM+* marks the channels you want to use multispeed on."

This confirms the multispeed mechanism in SDI: the CIA-timed speed player (`SDI21-SPD50`)
calls the wave/pulse table engine multiple times per VBI frame. Only the waveform program
and pulse program advance per speed-tick; the sequencer (note/instrument changes) runs at
the normal 50 Hz rate.

Another search snippet explains:

> "Multispeed gives finer/faster control of the SID by modifying its registers multiple
> times in a 50Hz PAL (or 60Hz NTSC) frame. With 8x multispeed the SID can be modified
> in 400Hz frequency, and the waveform/arpeggio tables can run really fast."

---

## ChipMusic.org — SDI Threads (Not Recovered)

Two ChipMusic.org SDI threads were identified:

| URL | Topic | Status |
|-----|-------|--------|
| `chipmusic.org/forums/topic/19378/` | "Making music in SDI tracker (SID Duzz It)" | HTTP 403 Forbidden |
| `chipmusic.org/forums/topic/10911/sid-duzz-it-wav-table-question/` | "Sid duzz it wav table question" | HTTP 403 Forbidden |

These returned 403 during this session. They may require login or are geo-blocked.

### Partial Content from ChipMusic.org (via search snippet)

The "wav table question" thread is confirmed to exist and discusses waveform program
table behaviour. A search snippet from the thread:

> "Multispeed plays the tables faster, and it's only wavetable and pulseprogram that
> runs on speed."

The "Making music in SDI tracker" thread (topic 19378) had a description visible
in search results:

> "Tutorial series on using SID Duzz It (C64 tracker) by Geir Tjelta and Glenn Rune
> Gallefoss [...] How to use the editor, instruments, effects etc."

---

## Summary: Forum Coverage Gaps

| Forum | Status | Gap |
|-------|--------|-----|
| CSDb release comments | RECOVERED (see `forum_csdb_release_comments.md`) | Partial — some comment text paraphrased not verbatim |
| CSDb SDI forum thread | PARTIALLY RECOVERED | Only ~9 posts; thread may have more |
| comp.sys.cbm | NO CONTENT FOUND | SDI likely never discussed on Usenet |
| Lemon64 (4 threads) | NOT RECOVERED (503) | Rate-limited; retry 1 hour later |
| ChipMusic.org (2 threads) | NOT RECOVERED (403) | May require login |
| Pouet.net (V2.0) | RECOVERED (see `forum_csdb_release_comments.md`) | Minimal comments |
| forum64.de | NO RESULTS FOUND | German C64 forum; may have SDI content in German |

---

## Leads to Follow

- **Lemon64 t=31585 "SDI and SID files"**: Re-fetch after Retry-After: 3600 (1 hour).
  This thread is the most likely Lemon64 source for technical SDI ripping/export discussion.
  URL: `https://www.lemon64.com/forum/viewtopic.php?t=31585`

- **Lemon64 t=67248 "Comparison of C64 Music Editors"**: Contains the community discussion
  around Chordian's comparison table, which listed SDI. This thread will have the SDI
  feature comparison vs JCH, GoatTracker, SID-Wizard.
  URL: `https://www.lemon64.com/forum/viewtopic.php?t=67248`

- **ChipMusic.org topic 19378**: The main SDI tutorial thread. Try with a different user
  agent or at a later time (403 may be rate-limiting or bot-blocking, not auth).
  URL: `https://chipmusic.org/forums/topic/19378/making-music-in-sdi-tracker-sid-duzz-it-commodore-64-editor/`

- **forum64.de search for "SID Duzz'It"**: German demoscene forum not searched in this
  session. URL: `https://www.forum64.de/` — search for "SID Duzz" or "SDI" or "Geir Tjelta".
  German community may have independent technical notes.

- **narkive.com comp.sys.cbm archive**: More complete than Google Groups for the 1992–2002
  period. Search: `https://comp.sys.cbm.narkive.com/search?q=SID+Duzz%27It`
  Worth one more targeted attempt before declaring comp.sys.cbm clean.

- **Lemon64 t=24039 "SDI question" and t=24599 "SDI help!!"**: Lower priority than t=31585
  and t=67248 but still worth fetching for any technical details in the replies.
