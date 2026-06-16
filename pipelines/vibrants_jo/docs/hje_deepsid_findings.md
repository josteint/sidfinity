---
source_url: multiple — see sections below
fetched_via: direct
fetch_date: 2026-06-16
author: research agent
content_date: 2026-06-16
reliability: secondary
---

# Vibrants/JO — HJE, DeepSID, Wayback, and Supplementary Research

This document extends and cross-checks findings in `hvsc_online_research.md`,
`github_findings.md`, and `csdb_findings.md`. It focuses on HJE (Hans Jürgen
Ehrentraut) who used JO's player, DeepSID's player detection, archived web
content, and sidid.nfo metadata.

---

## 1. HJE (Hans Jürgen Ehrentraut) — Full Profile

### Identity

- **Handle:** HJE (also written H-JE)
- **Earlier alias:** Esonix (used ~1989, see Xenon.sid)
- **Real name:** Hans Jürgen Ehrentraut
- **Nationality:** German
- **CSDb ID:** 2273 — https://csdb.dk/scener/?id=2273

### Groups

| Period | Group |
|--------|-------|
| ~1989 | Event (as Esonix) |
| 1990–1991 | Amok |
| 1991–2013 | Genesis Project |
| 2016–present | Genesis Project (rejoined) |
| ongoing | Masters' Design Group |

### How HJE Likely Got JO's Player

JO was in Amok from ~1989 through 1991. HJE joined Amok in 1990 and left in 1991.
They were in the same group for at least one year. JO's CSDb bio explicitly confirms
he created "his own players on C64 and for the AdLib sound card" and had "unique
knowledge about coding players." The most parsimonious explanation: JO shared a copy
of his player (or a binary + brief usage notes) with HJE during their Amok overlap.

Supporting evidence:
- `Stormlord_2_Demo.sid` (in the HVSC, per `disasm_findings.md`) contains an embedded
  string: `"NEW PLAYER V22.6-7 BY JESPER OLSEN. MUSIC BY HJE/JO."` — This is the single
  strongest documentary proof: JO's player credited by name, music jointly attributed
  to HJE and JO.
- All 23 (per some counts, up to 36 per the HJE HVSC directory including Esonix/) HJE
  SIDs in HVSC match the Vibrants/JO sidid fingerprint.
- The HVSC has 23 files in MUSICIANS/H/HJE/ (plus an Esonix/ subdirectory).
- HJE used the player across commercial game work and demo music well into the 1990s.

### HJE's Commercial Game Work (Using JO's Player)

All five confirmed commercial titles (Lemon64 database):

| Year | Title | Publisher | Platform |
|------|-------|-----------|----------|
| 1991 | Woody the Worm | Golden Disk 64 | C64 |
| 1991 | Pot Panic | Kingsoft | C64 |
| 1991 | Solix | 64'er | C64 |
| 1992 | Solitax | Amok | C64 |
| 2020 | Survival Messenger Adventure | Public Domain | C64 |
| 2022 | Careers | Public Domain | C128 |

**Woody the Worm.sid** (HVSC: MUSICIANS/H/HJE/Woody_the_Worm.sid) is 19 KB —
unusually large for a Vibrants/JO SID (typical: 2–4 KB). Likely multiple subtunes.
**Vicious_SID_2-Turn_Disk.sid** is 45.5 KB and **Vicious_SID_2-Greets.sid** is 42.3 KB
— these are multi-tune or digi-embedded SIDs.

### HJE Technical SID Addresses

Selected SIDs from CSDb (all confirmed using Vibrants/JO player by sidid):

| Title | Year | Load | Init | Play | Songs | Size |
|-------|------|------|------|------|-------|------|
| Genesis_Project_crack_intro | 1991 | $0DC8 | $0DC8 | $0DCB | 1 | 2014 B |
| Propaganda_Music | 1991 | $762D | $7634 | $769F | 2 | 3350 B |
| Solitax_end_sequence | 1992 | $1162 | $1162 | $1168 | 2 | 2872 B |
| Tech_2 | 1997 | $1000 | $1000 | $1006 | 1 | 2712 B |

Observations:
- Play address offset from init varies: +3, +7, +6, +6. Not a fixed ABI.
- Load addresses span a wide range ($0DC8 to $762D), consistent with a relocatable engine.
- Play = Load in all but Propaganda_Music (where Load+7 = Init, Init+$6B = Play).
  Propaganda is anomalous — the $7634 init is 7 bytes past load, and play at $769F is
  another $6B = 107 bytes into the code. May have a multi-tune trampoline.
- All sizes in the 2–3.5 KB typical range except the multi-tune SIDs.

### HJE's Scene Activity

- Active 1990–2022 (36+ years in the scene).
- Attended X'2016 (Silicon Limited Summer Party mentioned in CSDb).
- Composed "Hangover@X16" in 2017 — a new C64 chiptune released on YouTube.
- As of 2022 still composing (Careers, a C128 game).
- His Propaganda diskmag credits span issues #1–15 and #28–29.

---

## 2. DeepSID — Player Detection and Label

**Source:** https://deepsid.chordian.net/, https://github.com/Chordian/deepsid

DeepSID is written by Jens-Christian Huus (JCH of Vibrants) — a different Vibrants
member from JO, but both in the same group. DeepSID uses the sidid classification
database for player detection.

- Player label shown in DeepSID: **"Vibrants/JO"** (derived from sidid.cfg).
- DeepSID cannot be scraped for per-file player labels (JS-rendered; the fetch returns
  the generic player documentation page regardless of the `?file=` parameter).
- The sidid.nfo entry for Vibrants/JO is minimal (only `AUTHOR` field populated):

```
Vibrants/JO
   AUTHOR: Poul-Jesper Olsen (JO)
```

No `NAME`, `RELEASED`, or `REFERENCE` fields — the player was never formally released
as a named product, consistent with it being hand-assembled and not publicly distributed.
Compare with the richer Vibrants/Laxity entry which has `NAME: LAXITY editor` and a
CSDb release reference.

DeepSID todo.txt (620+ lines) contains no specific notes about the Vibrants/JO player
format, detection, or any Vibrants/JO-specific implementation details. The DeepSID
codebase uses sidid as a black-box classifier.

---

## 3. Archived www.vibrants.dk Content

web.archive.org cannot be fetched by the tool used in this research session (blocked).
Attempts to fetch `https://web.archive.org/web/*/www.vibrants.dk` all failed.

**What is known from other sources:**
- JO had a personal website at www.vibrants.dk (listed on his Demozoo profile).
- The website is confirmed defunct.
- JCH of Vibrants maintains chordian.net and blog.chordian.net (separate from JO's site).
- The later AdLib music by Vibrants was documented on chordian.net's blog
  (https://blog.chordian.net/2017/12/03/the-later-adlib-music-by-vibrants/), which
  confirms JO "composed tunes in an assembler listing" for his own AdLib player — same
  methodology as his C64 player.
- No archived technical documentation from vibrants.dk was recoverable in this session.

**Wayback status:** Should be investigated via https://web.archive.org/web/*/vibrants.dk
when that URL becomes accessible (the `www.` subdomain may differ from the bare domain).

---

## 4. Lemon64 — No New Technical Details Found

Lemon64 threads about "Vibrants JO" and general C64 music trackers did not yield
technical player format details. The most relevant thread (C64 Music Tracker Software,
https://www.lemon64.com/forum/viewtopic.php?t=71942) only mentions DeepSID and JCH
in passing, with no discussion of JO's player specifically.

HJE's Lemon64 game database page lists his commercial titles (see section 1 above).

---

## 5. sidid.cfg Signatures — Full Block (Confirmed)

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
(See also: /home/jtr/sidfinity/tmp/vibrants_jo_research/sidid_cfg_vibrants_jo.txt)

All 10 signatures confirmed. Three were provided in the task brief; the other 7
(confirmed from the raw file):

```
Vibrants/JO
C9 80 D0 ?? BC ?? ?? C8 B1 END                                                  [sig 1]
29 7F DD ?? ?? D0 ?? A9 ?? 9D ?? ?? FE ?? ?? FE END                              [sig 2]
BC ?? ?? B1 ?? C9 F0 D0 ?? C8 B1 ?? 18 7D ?? ?? 9D ?? ?? C8 B1 ?? 9D ?? ?? FE ?? ?? FE ?? ?? FE END  [sig 3]
BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? DE ?? ?? D0 ?? A9 01 9D ?? ?? FE END  [sig 4]
BC ?? ?? B1 ?? C9 60 90 ?? 38 E9 60 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? D0 ?? 9D ?? ?? FE END  [sig 5]
B9 ?? ?? 85 ?? DE ?? ?? ?? ?? BC ?? ?? B1 ?? C9 END                             [sig 6]
A2 ?? CE ?? ?? 10 ?? AD ?? ?? 8D ?? ?? EE ?? ?? EE ?? ?? EE END                 [sig 7]
C9 D0 90 ?? E9 D0 0A 0A 0A 9D END                                               [sig 8: task-provided]
A2 02 BC ?? ?? A9 00 99 05 D4 99 06 D4 A9 08 99 04 D4 CA 10 ?? 60 END          [sig 9: task-provided]
30 03 4C ?? ?? A9 00 9D ?? ?? A9 08 99 04 D4 98 48 A0 00 BD END                 [sig 10]
```

**Decoding notes on previously-undocumented signatures:**

- **Sig 2** (`29 7F / DD ?? ?? / D0 / A9 ?? / 9D`): `AND #$7F` followed by `CMP abs,X`
  then branch. Likely a bitmask operation on note/waveform flags (clearing bit 7 of a
  data byte before comparing against a table entry).

- **Sig 3** (`C9 F0`): Compare to $F0 — likely a pattern command value. The long
  sequence (`18 7D ?? ??` = ADC abs,X; `9D ?? ??` = STA abs,X repeated) suggests this
  is the note-load / frequency-apply loop. The `$F0` sentinel may be an instrument
  trigger or rest command embedded in the pattern stream.

- **Sig 4** (`C9 FF`): $FF = end-of-pattern / loop marker (universal in 6502 music
  players). On hit: `A9 00 / 9D` clears a counter; `DE ?? ??` decrements another table;
  `D0` branches; `A9 01 / 9D` sets a flag to 1. This is the pattern-exhausted / order-list
  advance logic.

- **Sig 5** (`C9 60 / 90 ?? / 38 E9 60`): Note bytes are in range $60+. Values < $60 go
  to an alternate path. Values >= $60 have $60 subtracted (SEC + SBC $60 = `38 E9 60`)
  to get the 0-based note index, then stored. The second half (`BC ?? ?? / B1 ?? / D0 ??
  / 9D`) reads a second byte from the stream — likely a duration or effect byte.

- **Sig 6** (`B9 ?? ?? / 85 ?? / DE ?? ??`): Load from abs,Y into A, store to ZP
  (85 = STA zp), then decrement abs,X. Classic per-voice state update.

- **Sig 7** (`A2 ?? / CE ?? ?? / 10 ?? / AD ?? ?? / 8D ?? ?? / EE EE EE`): Speed
  counter via LDX #n, DEC abs, BPL (don't advance yet), else: LDA/STA a register
  and INC three more counters. This is the nested timer / multi-speed counter structure.

- **Sig 10** (`30 03 4C ?? ?? / A9 00 9D ?? ?? / A9 08 99 04 D4`): BMI = gate off
  condition; JMP to rest handler. LDA #0 STA X-indexed (clear register); LDA #$08
  STA $D404,Y (ADSR: attack=0, decay=0, sustain=0, release=0, gate=0, output $08?
  Actually $08 to $D404 = test bit set, waveform = none). This looks like the
  per-note hard-restart: set test bit ($08) before re-gating.

---

## 6. Zimmers.net — Confirmed: No JO Tools

The zimmers.net Vibrants archive (https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/)
contains ONLY JCH editor music and utilities (Deluxe Drivers 2.0–5.0, JCH Editor v1.4G,
relocators, etc.). No JO subfolder, no JO player binary, no JO source code.

The `README` prefix codes (`acc`, `dek`, `drx`, `hj`, `jch`, `lnk`, `mtl`, `sco`) all
refer to JCH-editor composers. The `hj` prefix (versions 11, 13) is likely HJE's
JCH-editor work, not his JO-player work — HJE appears to have used BOTH JCH's editor
(early) and JO's player (from ~1990 onward), or the `hj` refers to a different composer.

---

## 7. JO vs. JCH — Disambiguation

Multiple web searches conflate JCH (Jens-Christian Huus) and JO (Poul-Jesper Olsen)
because both are associated with Vibrants and with C64 music player creation. Key
distinctions:

| | JO (our engine) | JCH (different engine) |
|--|--|--|
| Real name | Poul-Jesper Olsen | Jens-Christian Huus |
| Nationality | Danish | Danish |
| CSDb ID | 1926 | 626 |
| sidid label | `Vibrants/JO` | `Vibrants/JCH` or `JCH` |
| Player | Hand-assembled, no editor | JCH Music-Editor (public) |
| Editor public? | No | Yes (v1.11 through v3.04) |
| Zimmers archive | Not present | Full archive |
| Current activity | Not active since ~90s | Still active (DeepSID, SID Factory II) |

---

## 8. Summary of New Confirmed Facts (This Session)

1. **HJE's CSDb ID is 2273** — https://csdb.dk/scener/?id=2273 (previous sessions had
   been unable to resolve this; the search found `HJE/Genesis Project/Masters' Design Group`).

2. **HJE used the alias "Esonix" in his earliest releases (~1989)** — confirmed via the
   Esonix/ subdirectory in MUSICIANS/H/HJE/ and the CSDb SID entry for Xenon (1989, by
   Esonix). He predates his HJE handle.

3. **HJE is German** (not Danish) — confirmed from CSDb scener page.

4. **HJE's active career spans 1990–2022**, including new work in 2017 (Hangover@X16
   YouTube chiptune) and 2022 (Careers, C128 game).

5. **HJE's commercial game titles confirmed**: Woody the Worm (Golden Disk 64, 1991),
   Pot Panic (Kingsoft, 1991), Solix (64'er, 1991), Solitax (Amok game, 1992).

6. **sidid.nfo Vibrants/JO entry is minimal** — no `NAME`, `RELEASED`, or `REFERENCE`
   fields. The player was never given an official name or a formal CSDb release.

7. **All 10 sidid signatures confirmed** from the raw sidid.cfg file (task-brief listed 3;
   this session confirms all 10 and provides decoding analysis for the 7 previously
   undocumented ones).

8. **DeepSID cannot be scraped for per-file metadata** — the player detects Vibrants/JO
   via sidid but the JS-rendered interface is not scrapable.

9. **Wayback Machine blocked** — web.archive.org not accessible via the fetch tool.

---

## Leads to Follow

The following are specific, actionable next steps ordered by likely yield:

1. **HJE's CSDb page (ID 2273)** — now confirmed accessible. Check his full release list
   for any "player" or "music tool" release. He may have re-released or documented JO's
   player separately.
   URL: https://csdb.dk/scener/?id=2273

2. **Stormlord_2_Demo.sid embedded string** — `disasm_findings.md` documents the string
   `"NEW PLAYER V22.6-7 BY JESPER OLSEN. MUSIC BY HJE/JO."` This "V22.6-7" is a version
   number. Are there earlier player versions visible in other SID embedded strings? A grep
   of all 130 Vibrants/JO SIDs for embedded ASCII strings may reveal version labels, dates,
   or feature descriptions.
   Tool: `strings hvsc84/MUSICIANS/J/JO/*.sid | grep -i "player\|jesper\|jo\|version"`

3. **Wayback Machine for vibrants.dk** — try accessing via a different fetch path:
   URL: https://web.archive.org/web/20020101000000*/vibrants.dk
   (bare domain, not www.) — JO's personal site may have had player docs or download.
   Also try: https://webcache.googleusercontent.com/search?q=cache:vibrants.dk

4. **HJE email / contact** — HJE was active at X'2016 and composing in 2022. He can
   potentially be contacted via CSDb message or Lemon64 forum. He likely knows the
   player format from having used it for years. A direct question about instrument
   structure and pattern encoding could yield definitive documentation.
   CSDb contact: https://csdb.dk/scener/?id=2273

5. **DRAX worktune file** — MUSICIANS/D/DRAX/Worktunes/Worktune_in_JOs_player.sid
   is confirmed in HVSC. Disassemble alongside a JO tune to cross-validate the engine
   version DRAX used. Does DRAX's worktune use a different player version from JO's main
   corpus?

6. **Esonix subdirectory** — MUSICIANS/H/HJE/Esonix/ contains HJE's pre-1990 releases
   under his earlier alias. These may use a DIFFERENT player (predating JO's). Verify
   whether Esonix/ SIDs also match Vibrants/JO or match a different engine.
   Tool: `sidid hvsc84/MUSICIANS/H/HJE/Esonix/*.sid`

7. **`hj` prefix files in Zimmers Vibrants archive** — `hj` versions 11 and 13 exist in
   the JCH-editor music collection. Determine if these are HJE using JCH's editor (separate
   from his JO-player work) or a different HJ composer.
   URL: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/JCH+HJ/

8. **Comparison of HJE's large SIDs** — Woody_the_Worm.sid (19 KB),
   Vicious_SID_2-Turn_Disk.sid (45.5 KB), Vicious_SID_2-Greets.sid (42.3 KB),
   Megademo_part_2.sid (11.7 KB) are 3–15× larger than typical. These are the richest
   sources for multi-subtune and possibly digi-sample analysis.
   Disassemble with: `tools/seed_disassembly.py hvsc84/MUSICIANS/H/HJE/Woody_the_Worm.sid`

9. **Sig 10 decoding** — `30 03 4C ?? ?? / A9 08 99 04 D4` writes $08 to $D404,Y. In
   the SID chip, writing $08 to the voice control register (VCREG) sets the TEST bit
   while clearing the gate. This is the hard-restart sequence. Cross-reference with the
   disassembly at the labels identified in `disasm_findings.md` to confirm this is
   the per-voice hard-restart subroutine entry point.

10. **CSDb Vibrants group page** — find the correct Vibrants group ID to see all official
    Vibrants tool and music releases. May list JO's player as a credited resource in
    group productions.
    Search: https://csdb.dk/search/?seinsel=group&search=vibrants&Go=Go
