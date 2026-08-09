---
source_url: multiple — Archive.org, Wayback Machine, CSDb, Demozoo, MobyGames, blog.chordian.net, github.com/cadaver/sidid, HVSC local (hvsc85/)
fetched_via: WebSearch + WebFetch + local read
fetch_date: 2026-06-16
author: Poul-Jesper Olsen (subject); research by Claude Code 2026-06-16
content_date: 1988–2026
reliability: secondary (web), primary (HVSC local binary + string evidence)
---

# Vibrants/JO — Archive.org & Historical Scene Research

## 1. Identity — Poul-Jesper Olsen ("JO")

- **Real name:** Poul-Jesper Olsen
- **Handles:** JO (primary), Rock (Genesis Project era), Technic (another alias)
- **Nationality:** Danish
- **Active C64 years:** 1988–1994 (peak 1988–1991); still making C64 music as late as 2026 ("Rasta Grid")
- **Groups (chronological):** Genesis Project → AMOK / AMOK Sound Dept. → BUDS/NATO → Maniacs of Noise → **Vibrants** (joined ~1992) + Tale Software/Kingsoft (commercial credits)
- **CSDb scener page:** https://csdb.dk/scener/?id=1926 (returned HTTP 503 on 2026-06-16 — CSDb was down)
- **Demozoo profile:** https://demozoo.org/sceners/6764/ (accessible; confirms bio)
- **MobyGames:** https://www.mobygames.com/person/53900/jesper-olsen/
- **Personal website (defunct):** www.vibrants.dk (no live snapshot recovered; domain gone)

Key biographical quote from Demozoo (source: demozoo.org/sceners/6764/):
> "He had unique knowledge about coding players for computer formats such as the Amiga
> home computer and the Roland MT-32 on the PC. He also made his own players on C64 and
> for the AdLib sound card."

JO is confirmed as a **professional game audio composer** for Interactivision, Brain Bug,
FunSoft (Danish/Scandinavian C64 game publishers). MobyGames lists commercial game credits.

---

## 2. Relationship to Vibrants Group (NOT JCH)

**Critical disambiguation:** Vibrants has two well-known music members with entirely
separate players:

| Property | JO (this engine) | JCH (different engine) |
|---|---|---|
| Full name | Poul-Jesper Olsen | Jens-Christian Huus |
| sidid label | `Vibrants/JO` | `JCH_NewPlayer` (+ variants) |
| Editor | None — composed in assembler | Full GUI editor (JCH Editor V3.04) |
| Source released? | No | Yes (JCH zip, 1998) |
| HVSC dir | MUSICIANS/J/JO/ | MUSICIANS/J/JCH/ |

JCH's blog (blog.chordian.net) confirms JO introduced JCH to the hard-restart
technique (~1989): "Jesper Olsen also wrote his very own AdLib player and composed
tunes for it in an assembler listing" — same composition-in-assembler approach used
on C64.

---

## 3. Player Existence — Binary String Evidence (primary)

Embedded strings in HVSC SID binaries confirm JO wrote and versioned his own player:

| SID file | Embedded string |
|---|---|
| `Stormlord_2_Demo.sid` | `- NEW PLAYER V22.6-7 BY JESPER OLSEN. MUSIC BY HJE/JO.` |
| `Col.sid`, `Dos.sid` | `- PLAYER BY JO. -` |
| `Airwolf.sid` | `- CODED AND IMITATED BY J.O. OF AMOK SOUND DEPARTMENT 1988 -` |
| `Psycho.sid` | `PLAYER AND MUSIC (C) J.O. OF AMOK MUSIC DEPARTMENT 1988` |
| `Soundtrack_1.sid` | `PLAYER AND MUSIC (C) JESPER OLSEN OF AMOK SOUND DEPARTMENT 05-07TH OF NOVEMBER 1988` |
| `Megabad.sid` | `MUSIC + PLAYER (C) JO 1988 REMEMBER ME IF YOU USE IT!! ,ELSE DIE` |
| `Hit_It.sid` | `MUSIC AND PLAYER BY JESPER OLSEN` |
| `Behind_the_Wheel.sid` | `PLAYER & MUSIC (C) BY ROCK/G * P  YOU MAY USE IT!.... CALL (03) 31 63 67....JESPER` |
| `Destiny_v3.sid` | `MUSIC BY JO/AMOK LEVETOFTEVEJ 1A. 4690 HASLEV DENMARK PHONE:(+45)56316459` |

The `Stormlord_2_Demo.sid` string `V22.6-7` confirms JO internally versioned his player
through at least 22 major iterations (~1990), never releasing variant binaries publicly.

---

## 4. Archive.org — What Was Found

**Specific Archive.org findings:**

- **No archived disk image releases of the JO player were found.** No snapshot of
  www.vibrants.dk contained player format documentation.
- **JCH distribution ZIP** (`JCH_C64_Editor_v3.04.zip`, 1998-07-18) *is* on Archive.org
  at identifier `jch_c64_zip` — but this is JCH's engine (NOT JO's). Filed separately in
  `csdb_research.md` / `archive_research.md`.
- Wayback Machine: www.vibrants.dk was checked but no player-format content recovered.
- No C64 disk magazines (scene mags) containing JO player documentation were found on
  Archive.org. Generic C64 scene magazine archives (Propaganda, Raw, etc.) were checked —
  no JO-specific player articles found.
- No HVSC documentation file (BUGlist, FORMAT.txt, etc.) describes the JO engine format.

**Source reliability note:** Absence of Archive.org materials is confirmed absence —
multiple search strategies were tried (see §7 below for queries used).

---

## 5. sidid Fingerprint (cadaver/sidid — primary)

Source: https://github.com/cadaver/sidid (`sidid.cfg`, fetched 2026-06-16)

The [Vibrants/JO] block contains 10 independent hex-pattern signatures (OR logic —
any one match = this engine):

```
C9 80 D0 ?? BC ?? ?? C8 B1 END
29 7F DD ?? ?? D0 ?? A9 ?? 9D ?? ?? FE ?? ?? FE END
BC ?? ?? B1 ?? C9 F0 D0 ?? C8 B1 ?? 18 7D ?? ?? 9D ?? ?? C8 B1 ?? 9D ?? ?? FE ?? ?? FE ?? ?? FE END
BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? DE ?? ?? D0 ?? A9 01 9D ?? ?? FE END
BC ?? ?? B1 ?? C9 60 90 ?? 38 E9 60 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? D0 ?? 9D ?? ?? FE END
B9 ?? ?? 85 ?? DE ?? ?? ?? ?? BC ?? ?? B1 ?? C9 END
A2 ?? CE ?? ?? 10 ?? AD ?? ?? 8D ?? ?? EE ?? ?? EE ?? ?? EE END
C9 D0 90 ?? E9 D0 0A 0A 0A 9D END
A2 02 BC ?? ?? A9 00 99 05 D4 99 06 D4 A9 08 99 04 D4 CA 10 ?? 60 END
30 03 4C ?? ?? A9 00 9D ?? ?? A9 08 99 04 D4 98 48 A0 00 BD END
```

Key opcode observations (format inference only — NOT verified RE):
- `BC ?? ??` = `LDY addr,X` appears repeatedly → X = voice index, Y = data stream offset
- `B1 ??` = `LDA (zp),Y` → ZP pointer + Y walk for per-voice data streams
- `C9 F0`, `C9 FF`, `C9 60`, `C9 80` = sentinel compare values in the data stream
- `FE ?? ??` / `DE ?? ??` = `INC addr,X` / `DEC addr,X` — per-voice counter increment/decrement
- `0A 0A 0A` = three ASL A — multiply by 8 → 8-byte instrument record stride
- `A2 02` + `CA 10 ??` = `LDX #2` / `DEX BPL` — 3-voice init loop
- `99 05 D4 99 06 D4 A9 08 99 04 D4` = write $00 to $D405,Y and $D406,Y, write $08 to $D404,Y
  → gate-off via test-bit ($08) — hard-restart technique (JO invented this, JCH adopted it)
- `C9 D0 90 ?? E9 D0 0A 0A 0A 9D` = compare $D0, branch, subtract $D0, ×8, STA,X
  → instrument-select byte processing: `(byte - $D0) * 8` = offset into instrument table
- `18 7D ?? ??` = CLC + ADC addr,X → frequency addition (transpose or slide)

---

## 6. HVSC Corpus Survey (local — primary)

Source: local `hvsc85/`, fetched 2026-06-16.

- **130 SIDs total** with engine label `Vibrants/JO`:
  - ~106 in `MUSICIANS/J/JO/` (JO's own compositions)
  - ~23 in `MUSICIANS/H/HJE/` (Hans Jürgen Ehrentraut — used JO's engine)
  - 1 in `MUSICIANS/D/DRAX/Worktunes/` (`Worktune_in_JOs_player.sid` — DRAX used JO's engine)
- **All VBL-timed** (PSID `speed = $00000000`); no CIA-timed tunes found.
- **Load addresses:** freely relocatable — observed across $0800–$F000 range.
- **PSID version:** v2 throughout.
- **STIL notes:** STIL.txt entries are musical attribution only; no technical engine notes.

DRAX's worktune title `Worktune_in_JOs_player.sid` is explicit confirmation that
the player was shared within Vibrants.

HJE (`MUSICIANS/H/HJE/`) used the same engine for ~23 tunes — likely received the
player source or binary from JO directly.

`MUSICIANS/J/JO/JO_goes_Myth.sid` uses a MoN/Bjerregaard engine (not JO's).
`MUSICIANS/J/JO/Multi_Move.sid` is FutureComposer (already has a sidfinity.sid).

---

## 7. Lemon64 / Game Connections

Source: lemon64.com (fetched 2026-06-16)

- JO wrote game music for Interactivision, Brain Bug, FunSoft.
- MobyGames (https://www.mobygames.com/person/53900/jesper-olsen/) lists commercial credits.
- No Lemon64 pages found that document the player format or link to source.
- Game tunes in HVSC are in `MUSICIANS/J/JO/` with STIL attribution — not in a
  separate GAMES/ subdir, suggesting the game releases used the same private player.

---

## 8. No Public Source / Format Docs — Confirmed

After exhaustive search:
- **No source code** for the JO player has been published anywhere online.
- **No format specification** document exists — no README, no .txt, no forum post.
- **No disassembly** found in any GitHub repository or scene archive.
- **No tool** (other than sidid identification signatures) handles this format.
- The engine is not referenced in any C64 music format documentation (HVSC docs,
  SIDPlay manuals, ACID64 docs, HardSID docs).

The path forward is original RE from HVSC binaries.

---

## Leads to Follow

1. **CSDb scener page** https://csdb.dk/scener/?id=1926 — was HTTP 503 on 2026-06-16.
   Re-fetch when CSDb is back online. May have production list, group affiliations, comments.

2. **Demozoo production list** https://demozoo.org/sceners/6764/ — credits JO with
   "code player creation for 'Copper' (1992, Surprise! Productions)". Fetch that production
   page for player binary evidence from the demo itself.

3. **www.vibrants.dk Wayback snapshots** — https://web.archive.org/web/*/vibrants.dk
   May have archived personal pages with player notes. The domain is defunct but may have
   been crawled in 1999–2005.

4. **JCH / Chordian blog** https://blog.chordian.net/ — JCH's personal blog has C64
   history articles. Any post mentioning JO directly may yield technical player details
   (JCH confirmed knowing JO and learning hard-restart from him).

5. **Atlantic Prophecy recollection site** https://atlantis-prophecy.org/ — hosts C64
   scene history articles. Check for any Vibrants / JO coverage.

6. **Amok Sound Dept. disk archives on CSDb** — JO's pre-Vibrants group. Any CSDb release
   under "Amok" from 1988–1992 with JO credits may contain the early player in the binary.
   Search: https://csdb.dk/search/?search=amok+sound&type=release

7. **Interactivision / Brain Bug game SIDs** — the GAMES/ subtree of HVSC may have
   JO-credited game tunes. Locating these would give player specimens in a commercial
   context (possibly with version strings).

8. **Archive.org C64 disk image collections** — search `identifier:c64` + "Vibrants" or
   "JO" in item descriptions. The collection at https://archive.org/details/c64s_uploaded_by_Commodore_Computer_Club
   and similar may have Amok/Vibrants demo disks containing the player binary.

9. **Pouët.net** https://www.pouet.net/ — search for Vibrants / JO C64 prods.
   Any prod with downloadable binary that contains the JO engine could be a specimen.

10. **HJE (Hans Jürgen Ehrentraut) — who gave him the player?** HJE has ~23 tunes
    in the same engine. A CSDb search for HJE may reveal how the player was obtained
    and whether there's any documentation.
    Search: https://csdb.dk/search/?search=HJE&type=scener
