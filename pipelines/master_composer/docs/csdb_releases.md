# Master Composer — CSDb releases & technical comments

> **Provenance**
> - **source_url:** https://csdb.dk/release/?id=128699, https://csdb.dk/release/?id=31047,
>   https://csdb.dk/release/?id=215363, https://csdb.dk/release/?id=184807,
>   https://csdb.dk/release/?id=4298, https://csdb.dk/scener/?id=19061,
>   https://csdb.dk/search/?seinsel=releases&search=Master+Composer,
>   https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg,
>   https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
> - **fetched_via:** curl (Firefox/128 UA) for CSDb pages (WebFetch hit HTTP 503 / anti-bot);
>   WebFetch for the GitHub raw + scener page
> - **fetch_date:** 2026-06-13
> - **author (of the engine):** Paul Kleimeyer / Access Software Inc.
> - **content_date:** release pages dated 1983–1985; CSDb comments 2010–2022; sidid current
> - **reliability:** HIGH for the release facts + the verbatim user comments (primary CSDb
>   records). HIGH for the sidid signature (cadaver's reverse-engineered fingerprint, the
>   canonical HVSC engine classifier). MEDIUM for community-comment inference about usage.

---

## sidid engine signature (the load-bearing RE artifact)

`cadaver/sidid` — the canonical C64 SID-player fingerprint catalogue used by HVSC.
Its `sidid.nfo` attribution entry:

```
Master_Composer
     NAME: Master Composer
   AUTHOR: Paul Kleimeyer
 RELEASED: 1983 Access Software Inc.
REFERENCE: https://csdb.dk/release/?id=128699
```

Its `sidid.cfg` byte-pattern (`??` = wildcard byte; `END` terminates an alternative):

```
Master_Composer
F0 ?? C9 64 D0 0E ?? ?? ?? ?? ?? ?? 29 FE 8D 0B D4 4C ?? ?? A8 END
(Patrick_Payne)
29 FE 8D 04 D4 4C ?? ?? A8 B9 ?? ?? 8D 00 D4 B9 ?? ?? 8D 01 D4 AE ?? ?? BD ?? ?? 29 FE 8D 04 D4 09 01 8D 04 D4 END
(Lope_Pulse_Sweep)
F0 04 90 02 B0 37 A9 01 8D END
```

Reading of the opcodes (confirms the engine model in `research.md`):
- `C9 64` = `CMP #$64` → the 100-entry note range (`$00` rest, `$01..$63` note index) is
  bounds-checked.
- `29 FE 8D 0B D4` = `AND #$FE : STA $D40B` → voice-3 control gate-clear (LSB cleared = gate
  off). The `(Patrick_Payne)` variant does the same on `$D404` (voice 1) and also re-writes
  freq lo/hi (`8D 00 D4`, `8D 01 D4` = `STA $D400/$D401`) then `09 01 8D 04 D4`
  (`ORA #$01 : STA $D404`, gate on). This is the per-voice "write full SID register set per
  block" behaviour — there is no effect engine, just direct register stores + a gate edge.
- `4C ?? ?? A8` = `JMP $A8??` into the play loop (the `A8` high byte is why HVSC files tend to
  sit with the player near `$7580`/relocated — absolute jump target patched at relocate).
- The `(Patrick_Payne)` tag = a named **variant fingerprint** (a second alternative the
  classifier recognises as the same engine family). The `(Lope_Pulse_Sweep)` tag = a
  sub-pattern for the **manually-added pulse-width sweep** some arrangers bolted on (the engine
  itself has no PWM — see `csdb_manual.md`).

> **Note for the migration:** the task brief's "Patrick Payne" is **not a second author of the
> editor** — it is a sidid variant label for an alternate code shape of the same Kleimeyer
> player. No CSDb scener or release credits a "Patrick Payne" for Master Composer.

---

## Full CSDb release census (search: "Master Composer", releases)

CSDb returns 12 release matches. Disambiguated below — **the first group is Access
Software's Master Composer; the second group ("Mastercomposer V1.0/V1.1") is an UNRELATED
1989–1990 scene tool and must not be conflated.**

### Access Software's Master Composer (the target engine)

| CSDb id | Title | Type | By | Year | Notes |
|---|---|---|---|---|---|
| **184807** | Master Composer | C64 **Tool** | **(ASI)** = Access Software Inc. | **1983** | The original publisher release. d64: `Master Composer (1983)(ASI).d64` (106 dl). No credits field. **Most authoritative original.** |
| 31047 | Master Composer | C64 Crack | International Cracking Group (ICG) | 1985 | Richest comment thread (9 comments). d64 `Mastercomposer-ICG.d64` (430 dl). Replaced with the *complete* release bundling **Musictranslator V1.2**. |
| 215363 | Master Composer | C64 Crack | Eagle Soft Incorporated (ESI) | 1985 | d64 `MasterComposer_ESI.d64` (116 dl). Comment confirms docs scarcity (below). |
| **128699** | Master Composer | C64 Crack | MST | (n/a) | The CSDb id cited by sidid + the task brief. d64 `Master_Composer-MST.d64` (187 dl). "only crack… that has a working Dealer Demo" (Fred, 2014). |

Music collections of tunes *made with* the tool (output, not the editor):
| id | Title | Type | By | Year |
|---|---|---|---|---|
| 221711 | Master Composer Hits | C64 Music Collection | The Axeman | — |
| 229233 / 229252 | Master Composer Melodies | C64 Music Collection | Ninja Music Inc. | — |
| 88788 / 103739 | Master Composer Melodies | C64 Music Collection | PMK | 1985 |

### UNRELATED — a different "Mastercomposer" scene tool (do NOT use for this engine)

| id | Title | Type | By | Year | Why unrelated |
|---|---|---|---|---|---|
| 4298 / 250846 | Mastercomposer V1.0 | C64 Tool | Bierfront / Twins (TWS) | 1990 | Code by Playboy / Sir Tippitt; music by "MC of Dutch USA-Team"; graphics Powell. A scene music tool, **not** Access Software. AKA "Master Composer V1.0". |
| 244828 | Mastercomposer V1.1 | C64 Crack | Duel (D) | 1989 | Same V1.x scene lineage as 4298. |

The "V1.0 / V1.1" version numbers therefore belong to the **Bierfront** tool, **not** to
Access Software's Master Composer. Access Software's product carries no public version number
on CSDb (the original is just "Master Composer (1983)").

---

## Verbatim user comments (technical / provenance value)

**Release 31047 (ICG, 1985) — 9 comments:**

- *4mat (2010-10-13):* "For the time an absolute godsend having the player code built-in.
  **(SYS 30120, remember?)** A lot of early famous c64 tracks were written with it."
  → `SYS 30120` = `$75A8`-ish decimal entry to the built-in player; corroborates the
  init≈`$7580` / play≈`$7587` layout (30120 = `$75A8`).
- *bepp (2010-11-27):* "**Press H for Help screen** :)" → the in-program help is the only
  shipped 'documentation' most users saw.
- *Fred (2014-10-19):* "Replaced release with the complete release that includes the
  **Musictranslator V1.2** tool which were spread together." → a companion conversion/export
  tool shipped alongside the cracked editor.
- *JackAsser (2013-11-27):* "How awesome is `MUSICIANS/K/Kleimeyer_Paul/Maniac.sid`?!?
  Perfect rendition using **plain and simple waveforms without any fuss**." → reinforces
  "no effects, direct register writes".
- *Inge (2010-10-13):* HVSC pointers — `MUSICIANS/K/Kleimeyer_Paul/` (Flashdance.sid,
  Maniac.sid) and `/DEMOS/Unknown/Master_Composer`.
- *McMeatLoaf (2010-10-13):* tunes are largely uncredited → HVSC keeps a dedicated
  `/DEMOS/UNKNOWN/` folder for them (exception: The Mighty Bogg).
- *4mat (2010-10-14):* "The Mighty Bogg used it for a lot of his releases."

**Release 215363 (ESI, 1985) — 1 comment:**

- *Paladin (2022-03-15):* "Nice find! I remember this program from back in the day. **I never
  could quite figure out how to use this one though. I wonder is [if] ESI did any docs for
  this?**" → independent confirmation that documentation is hard to find.

**Release 128699 (MST) — 1 comment:**

- *Fred (2014-02-05):* "This is the only Master Composer crack I can find that has a working
  Dealer Demo."

---

## Download artifacts (CSDb-hosted d64 disk images)

These are the editor disk images linked from the release pages (not fetched here — for a
disasm/parser lead they are the primary binaries):

- `https://csdb.dk/getinternalfile.php/192017/Master%20Composer%20(1983)(ASI).d64` (id 184807, original)
- `http://csdb.dk/getinternalfile.php/133270/Mastercomposer-ICG.d64` (id 31047, + Musictranslator V1.2)
- `https://csdb.dk/getinternalfile.php/226192/MasterComposer_ESI.d64` (id 215363)
- `http://csdb.dk/getinternalfile.php/127473/Master_Composer-MST.d64` (id 128699, Dealer Demo)

All also mirrored on Pokefinder.org.
