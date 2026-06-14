## TFX Corpus Characterisation & Version Cohorts

```
provenance:
  sources:
    - url: "file:hvsc84.db"
      fetched_via: "sqlite3.connect(uri=True, mode=ro)"
      content_date: "HVSC #84"
      reliability: authoritative (HVSC canonical)
    - url: "https://csdb.dk/release/?id=110111"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "1995 (TFX V1.0 release page)"
      reliability: high (primary scene database)
    - url: "https://csdb.dk/release/?id=38900"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "1996 (TFX V1.2 release page)"
      reliability: high
    - url: "https://csdb.dk/release/?id=2629"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "1995 (DMC V7.0 release page, Ray's comment)"
      reliability: high (first-person from author)
    - url: "https://csdb.dk/scener/?id=1594"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "Ray's CSDb profile"
      reliability: high
    - url: "https://csdb.dk/group/?id=124"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "Unreal group page"
      reliability: high
    - url: "https://csdb.dk/scener/?id=257"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "Factor6 CSDb profile"
      reliability: high
    - url: "https://oldschoolgameblog.com/2018/02/01/summer-memories-a-c64-scene-sid-music-album/"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "2018-02-01"
      reliability: medium (blog, cites liner notes)
    - url: "https://archive.org/details/d64_TFX_v2.4_1996_Unreal"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      content_date: "uploaded 2021-03-10 (software 1996)"
      reliability: medium (metadata only; binary not inspected)
  author: corpus-research agent (Claude Sonnet 4.6)
  fetch_date: 2026-06-14
```

---

## 1. Tool genealogy & author

TFX is a C64 music editor/tracker written by **Ray** (CSDb scener ID 1594), real-name
possibly "Raymond Paskvyl" (a playful self-assigned handle-story name; true name not
publicly listed). Ray co-founded **Area Team** circa 1992 and then co-founded
**Unreal** (Czech Republic) in March 1995, where he has remained.

**TFX evolved directly from DMC.** In Ray's own 2005 comment on the DMC V7.0 CSDb page:

> "we decided to improve old V4 ... added code grows up to 50% of original Brian's size.
> ... we decided to make TFX. Early versions of TFX looks like DMC, before PG
> completely changes it."

"PG" = Pseudografx (Zdenek Eisenhammer, also of Unreal), who designed the
graphics and UI and fundamentally reshaped TFX's look/feel from its DMC ancestor.

**Confirmed version timeline (from Ray's CSDb discography):**

| Version | Year | CSDb ID | Notes |
|---------|------|---------|-------|
| V1.0    | 1995 | 110111  | First release; ships on .d64; credits Ray (code), Pseudografx (gfx/docs/music). Bundled tunes: "Fire!" and "Fonttime" by Pseudografx. |
| V1.2    | 1996 | 38900   | Ships as .prg; credits Ray (code), Pseudografx (gfx/design/charset). |
| V1.3    | 1996 | —       | Listed in Ray's discography; no separate CSDb fetch done. |
| V2.4    | 1996 | —       | On Internet Archive: `d64_TFX_v2.4_1996_Unreal`. |
| V2.5    | 1997 | —       | Ray's discography. |
| V2.6    | 1999 | —       | Ray's discography. |
| V2.7    | 1999 | —       | Ray's discography. Also: "DMC 7.x To TFX V2.7 Convertor V1.4" (1996) — shows DMC→TFX migration tool. |
| V2.8    | ~2002–2006? | — | Used by Factor6 (Akio Tenshi) per 2018 liner notes ("Summer Memories" album). NOT yet listed in CSDb discography fetch — may be an intermediate build. |
| V2.92   | 2003 | —       | Ray's discography. |
| V2.97   | 2004 | —       | Ray's discography. |
| V2.98   | 2005 | —       | Ray's discography. |
| V2.99   | 2005 | —       | Ray's discography; likely final public release. |

**Key finding:** The version cited in prior `research.md` as "2.4" is only the
first of a long V2.x series that ran 1996–2005. "TFX 2.4" is NOT the final
version; V2.99 appears to be. The "2.8" used by Factor6 for SID work (confirmed
from 2018 album notes) is not in CSDb separately — may be a semi-private build.

**Unreal is Czech, not Polish.** The group's CSDb page and PCH's profile both
confirm Czech Republic. PCH (Petr Chlud, born March 2, 1973 per CSDb) is Czech.
David Cwik (Sad) is Czech/Slovak (released through Czech and Slovak groups:
Anubis, Padua, Warriors of the Wasteland). Jaymz Julian (A Life in Hell) is
Australian. Factor6 (now Akio Tenshi) is Czech.

The "Polish scene" characterisation in `research.md` is **incorrect**. TFX is a
**Czech Republic** tracker. The scene around it (Unreal, Anubis, Padua) is
predominantly Central European (Czech/Slovak), with one Australian contributor
(Jaymz Julian).

---

## 2. HVSC corpus shape (269 tunes, all PSID v2)

All 269 SIDs are PSID version 2. No `speed` flag column is available in the DB
schema, but the vblank-timed PAL standard is the expected mode for a tracker of
this type.

### 2.1 Subtune distribution

| n_subtunes | count |
|-----------|-------|
| 1         | 263   |
| 2         | 3     |
| 3         | 1     |
| 6         | 1     |
| 7         | 1     |

Multi-subtune tunes (all have init=play-3, standard or custom layout):
- `Walking_Death.sid` — 7 subtunes, init=$2040, play=$2043 (2018, Akio Tenshi & Petr Chlud)
- `Schlimeisch_Mania_II.sid` — 6 subtunes, init=$82A0, play=$82A3 (2018, Akio Tenshi)
- `Marblelogic.sid` — 3 subtunes, init=$1000, play=$1003 (2005, Factor6)
- `Kikstart_2012.sid` — 2 subtunes, init=$BF00, play=$BF03 (2012, Factor6)
- `Fishmagic.sid` — 2 subtunes, init=$1000, play=$1003 (2002, Jaymz Julian)
- `Forever.sid` — 2 subtunes, init=$1000, play=$1003 (2018, David Cwik/Sad)

### 2.2 Songlength distribution

| Range    | Count | Min  | Max  | Avg  |
|----------|-------|------|------|------|
| < 30 s   |   1   |  27s |  27s |  27s |
| 30–60 s  |  24   |  31s |  59s |  46s |
| 1–2 min  |  72   |  61s | 119s |  92s |
| 2–5 min  | 156   | 121s | 298s | 178s |
| 5–10 min |  15   | 304s | 561s | 384s |
| > 10 min |   1   | 626s | 626s | 626s |

The corpus is dominated by 2–5 min pieces. The longest tune is
`Dream.sid` / David Cwik (Sad), 626 s (~10.4 min), init=$2402, play=$2415
— a non-canonical layout (pre-V2.x export style).

---

## 3. Author concentration

| Author (HVSC field)              | Count | Activity |
|----------------------------------|-------|----------|
| David Cwik (Sad)                 | 108   | 1998–2025 |
| Petr Chlud (PCH)                 |  52   | 1993–2009 |
| Jaymz Julian (A Life in Hell)    |  45   | 2001–2022 |
| Factor6 (→ Akio Tenshi)          |  42   | 2002–2016 |
| Zdenek Eisenhammer (PseudoGrafx) |   7   | 1995–1997 |
| Jaymz Julian (various credits)   |   5   | 2001–2007 |
| Aki (= Factor6/Akio Tenshi)      |   3   | 2020–2021 |
| Petr Kratky (Manex)              |   1   | 2000      |
| Hendrik Söhnholz (Henne)         |   1   | 2005      |
| Edward R. Jones (Loscha)         |   1   | 2004      |
| collaborations                   |   4   | various   |

Top 4 authors account for 247/269 (92%) of the corpus. Note that
"Aki" and "Akio Tenshi" are the same person as "Factor6" (handle evolution
per CSDb profile: Koko&Keke → Factor6 → Akio Tenshi → Aki).

David Cwik (Sad) alone contributes 40% of the corpus. He spans the longest
timeframe (1998–2025) and his SIDs appear in five different address layouts
(see §4).

---

## 4. Address-cluster table and version cohorts

### Structural groups

There are five meaningfully distinct structural groups, identifiable purely
from (init_addr, play_addr):

```
Group  init                play        Count  Authors / Era          Likely TFX version
-----  ----                ----        -----  -----------------      ------------------
A      $1000               $1003        154   All major authors,     V2.x canonical
                                              1994–2022              (standard export)
B      $1100               $1100         10   PCH only, 1993–1996    V1.0 / V1.2 era
       (init=$1106)                           + PseudoGrafx 1995     (pre-V2 player)
C1     $0FF0               $1003         30   Sad only, 1999–2003    V2.6 / V2.7 Sad-variant
C2     $0FF4               $1003         11   Sad only, 2008–2025    V2.9x Sad-variant
C3     $0FF6               $1003          2   Henne 2005 + Sad       V2.9x variant
D      $1000 < init ≤ $1003 (data ptr)  $1003  23   Various, 2002–2018   V2.x (init points into
       (init >> $1100, non-standard)           Factor6/Sad/PCH/JJ     song data area)
E1     init = play − 3     NOT $1003/    9   Factor6/Sad/JJ/PCH,    V2.x relocated
       (standard offset)   $1100              1996–2018
E2     init near play      NOT $1003/   25   Sad/PCH/PseudoGrafx,   pre-V2 OR early V2
       (diff=18 or 19)     $1100              1995–2007              (older export layout)
F      entirely non-std     various       5   1 each (misc)          anomalous / wrapper
```

**Notes on each group:**

**Group A (154 tunes) — canonical TFX V2.x layout.**
Player at `$1000`; init entry = `$1000` (player init); play entry = `$1003`
(player tick). This is the standard TFX export from V2.4 onward, used by
every author from ~1996 PCH first sightings through to Factor6 2016 and
Aki 2021. The PCH tunes in this group starting 1994 suggest V1.x → V2.x
transition happened by 1996 at the latest.

**Group B (10+1 tunes) — PCH V1.x export, play=$1100.**
All 10 "clean" members have init=$1106, play=$1100, confined to PCH (1993–1996)
and one PseudoGrafx (1995). The one outlier (`Fire!` by PseudoGrafx, 1995,
init=$2038, play=$1100) is the first-ever TFX tune included on the
V1.0 disk — its higher init suggests a version with song-data separated above
the player. This group corresponds to TFX V1.0 / V1.2 player layout. PCH
has 9 Group-B tunes (all 1993–1996) and 43 Group-A tunes — confirming he
switched to the V2.x layout around 1996.

**Group C (43 tunes) — Sad's priming-block variant at $FF0/$FF4/$FF6.**
All authored by David Cwik (Sad) except one Henne tune (2005, $FF6).
Three sub-variants:
- C1 ($FF0, 30 tunes, 1999–2003): Sad's early-2000s output. Player still
  at $1000/$1003; the $FF0 region holds 16 bytes of pre-player initialization
  that run before the player init. Consistent with TFX V2.6/V2.7 (1999).
- C2 ($FF4, 11 tunes, 2008–2025): Sad's later long-term output. Shifted
  priming block by 4 bytes, consistent with a V2.9x change.
- C3 ($FF6, 2 tunes, 2005): Two-byte further shift.

These groups are structurally the same player ($1000/$1003) with a short
pre-init stub; they represent a Sad-specific TFX configuration (or version)
rather than a separate player.

**Group D (23 tunes) — high init pointing into tune data, play=$1003.**
Player at $1003; init address points well beyond the player into tune data
(range $1C52–$28E0). This is the PSID init address being set to the tune's
song-data start rather than the player's own init routine. This pattern
appears in various authors (Sad, PCH, PseudoGrafx, Factor6, Jaymz Julian)
and spans 2002–2018. It may be a quirk of how TFX exported SIDs — a PSID
tool set the init header field to song-data start rather than player init.
Verification implication: init call behaviour differs from the canonical
group; the player may self-init ignoring the PSID init addr, or the init
call triggers a song-select.

**Group E1 (9 tunes) — init=play-3, player NOT at $1003.**
Standard TFX layout relocated: same init=play-3 offset but player loaded
at $C00, $E00, $1AE0, $2040, $82A0, $A000, $BF00. Factor6 multi-subtune
tunes at $BF00 (Kikstart 2012, 2012), $A000 (Bytefest, 2013), $82A0
(Schlimeisch Mania II, 2018). These are late productions where the
musician placed the TFX player at an unusual base address (possibly to
avoid BASIC RAM conflicts or fit inside a demo).

**Group E2 (25 tunes) — diff=18 or diff=19 between init and play.**
Init is 18 or 19 bytes before the play routine. Player is NOT at $1003 — it
sits in the $1D00–$2700 range. Most are from 1995–2002, authored by
PCH/PseudoGrafx/Sad/Jaymz Julian. This appears to be the V1.x (or early V2.x)
export where the player was NOT pre-positioned at $1000 — it loaded wherever
data ended, with a fixed-size init stub at init_addr = play_addr - 18 or -19.
PseudoGrafx's "Fonttime" (1995, included on the TFX V1.0 disk) has
play=$1E12, init=$1E00 (diff=18). This is likely the V1.0 native export
format. PCH's 1996 Group-E2 tunes confirm V1.x was still producing this
layout mid-1996.

**Group F (5 tunes) — anomalous.**
- `Chachachaoseum Short Mix` (PCH, 1996): init=$FF26, play=$EF03 — scrambled
  or corrupt PSID headers; play not near $1000 family at all.
- `Still a Failure` (Jaymz Julian, 2015): play=None — PSID header malformed.
- Three others with high non-standard bases (see §4 table).

---

## 5. MUSICIANS folder distribution

| Folder          | Count | Author                        |
|-----------------|-------|-------------------------------|
| Sad             |  108  | David Cwik (Sad)              |
| Julian_Jaymz    |   52  | Jaymz Julian (+ variants)     |
| PCH             |   52  | Petr Chlud (PCH)              |
| Factor6         |   47  | Factor6 / Akio Tenshi / Aki   |
| PseudoGrafx     |    7  | Zdenek Eisenhammer            |
| Henne           |    1  | Hendrik Söhnholz              |
| Manex           |    1  | Petr Kratky                   |
| DEMOS/S-Z       |    1  | Edward R. Jones (Silly Synth) |

Note: Factor6's folder at `MUSICIANS/F/Factor6/` contains 47 entries even
though the author field splits across "Factor6", "Akio Tenshi", and "Aki"
— all the same person.

---

## 6. Year / release-group distribution (summary)

| Era       | Count | Primary release groups |
|-----------|-------|------------------------|
| 1993–1996 |  54   | Unreal (Czech)         |
| 1997–2000 |  32   | Unreal, Anubis         |
| 2001–2005 | 104   | Anubis, WotW, Padua, ROLE, Unreal |
| 2006–2010 |  25   | Padua, Anubis, WotW    |
| 2011–2016 |  38   | Padua, Tropyx, Factor6/HVSC |
| 2017–2025 |  16   | Unreal, Padua, Tropyx, Onslaught, A Life in Hell |

Peak year: 2001 (24 tunes, Anubis-era Sad productivity).
Longest quiet: 1997 (3 tunes); 1998 (2 tunes).
Modern revival: Tropyx-affiliated Factor6 active 2012–2016; Aki 2020–2021.
Still active as of 2025: David Cwik (Sad) — `Halvbøj.sid`, 2025 Padua.

---

## 7. Cohort summary for migration planning

From a migration standpoint, the corpus resolves into **three player layouts**:

| Layout | Groups | Count | init offset | Play base | Implication |
|--------|--------|-------|-------------|-----------|-------------|
| V2.x canonical | A + D | 177 | $1000 | $1003 | Main target; single player binary at $1000–$1002 (init) + $1003 (tick) |
| V1.x / early | B + E2 | 35 | play−18/−19 or $1106 | $1100 or $1D00–$2200 | Older player; separate init stub; song data starts right after; confirm player binary differs from V2.x |
| Sad-priming | C | 43 | $FF0/$FF4/$FF6 | $1003 | Same V2.x player at $1003 but with a short pre-init wrapper at page $FF; priming bytes differ by sub-variant |
| Relocated V2.x | E1 | 9 | play−3 | various | V2.x player binary loaded at non-standard base; otherwise canonical |
| Anomalous | F | 5 | various | various | Need individual inspection; may be corrupt or wrapped |

---

## 8. Key factual corrections vs prior research.md

1. **"Polish scene"** → incorrect. Unreal is **Czech Republic**. Core authors
   (Ray, PCH, Pseudografx, Sad/Cwik) are Czech/Slovak. Jaymz Julian is Australian.
   Tropyx is Polish (Factor6's later group), but TFX itself is Czech.
2. **"Author: Ray of Area Team/Unreal"** → Ray founded Area Team (1992–1995)
   then co-founded Unreal (1995–present). Both credits are accurate but Area
   Team is the predecessor group, not a co-affiliation.
3. **"Multiple versions (1.0, 1.2, 2.4)"** → the version series is longer:
   V1.0, V1.2, V1.3, V2.4, V2.5, V2.6, V2.7, [V2.8 unconfirmed on CSDb],
   V2.92, V2.97, V2.98, V2.99. "2.4" is one of many V2.x builds.
4. **"Very little public documentation"** → confirmed; no known format spec,
   disassembly, or player source in the public domain.

---

## Leads to follow

1. **Binary inspection of TFX V1.0 .d64 and V2.4 .d64 (Internet Archive)**:
   Compare player binary bytes to determine if V1.x (Group B, init=$1100) and
   V2.x (Group A, init=$1000) are distinct player binaries or the same with a
   relocation. Key question: does the V2.x player have a 3-byte dispatch stub
   at $1000–$1002 (JMP abs to actual init)?

2. **Sad's $FF0 init block**: 16 bytes at $FF0–$FFF that execute before the
   player init at $1000. What do they write? If it's pure SID priming
   (register initialisation), this is a USF `init.sid` block candidate.
   Sample binary: any of the 30 Group-C1 tunes (e.g. `Zero.sid`).

3. **Group E2 diff=18/19 pattern**: The 18-byte or 19-byte init stub before
   the play routine in the V1.x layout. Disassemble "Fonttime" (1995, on TFX
   V1.0 disk) to understand what those 18 bytes do.

4. **Group D high-init**: Verify whether PSID init call at e.g. $1C52 is ignored
   by the player (which self-inits) or selects a song. Test with siddump to see
   if subtune-1 vs subtune-2 call produces different initial state.

5. **TFX V2.8 confirmation**: Not on CSDb's V-series list. The Summer Memories
   liner notes (2018) credit it explicitly. Could be a private build given to
   Factor6, or a publicly released intermediate build not separately catalogued.
   Worth checking unreal64.net directly (site was mostly empty on fetch).

6. **Factor6's `Bytefest.sid` at $A000 and `Kikstart_2012.sid` at $BF00**:
   These relocated TFX players sit in the upper RAM. On C64, $A000–$BFFF is
   normally BASIC ROM. If Factor6 disabled BASIC before loading, the player
   at $A000 works in RAM. The banking concern from CLAUDE.md applies here —
   worth checking if the SID plays correctly and if there's a `sta $01` in
   the player.

7. **`TFX_Equals_Future_Composer.sid`** (Jaymz Julian, 2002): The title
   asserts TFX equals (sounds like / was derived from) Future Composer. The
   DMC lineage already shows TFX → DMC → ? → Future Composer-like. Worth
   loading and comparing write-model to verify Julian's claim. It uses the
   canonical layout (init=$1000, play=$1003).

8. **Player identification in sidid**: Confirm sidid uses what fingerprint to
   tag 269 tunes as TFX. If it's bytewise, which bytes / offsets distinguish
   V1.x from V2.x from V2.9x?
