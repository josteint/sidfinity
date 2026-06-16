---
source_url: multiple — see sections below
fetched_via: direct
fetch_date: 2026-06-16
author: research agent
content_date: 2026-06-16
reliability: secondary
---

# Vibrants / JO — Online Research Notes

## 1. Player Detection Name

**sidid engine name: `Vibrants/JO`**

Single entry in cadaver/sidid `sidid.cfg` — no V1/V2/V3 variants.
Also present in WilfredC64/player-id (same signature block, independently confirmed).

The canonical sidid signature block (10 independent patterns, OR logic):

```
[Vibrants/JO]
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

DeepSID (https://github.com/Chordian/deepsid) — written by JCH of Vibrants (a different member).
DeepSID uses sidid classification; the player label shown would be "Vibrants/JO".
DeepSID was not directly reachable during this session (fetch returned JS-rendered page).

## 2. CSDb Profile

- **Real name:** Poul-Jesper Olsen
- **Handle(s):** JO, Rock, Technic, Jesper Olsen
- **Nationality:** Danish
- **Groups (chronological):** Genesis Project → Amok / Amok Sound Dept. → BUDS/NATO →
  Maniacs of Noise → Vibrants (joined ~1992) + Tale Software/Kingsoft (game credits)
- **CSDb scener ID:** 1926 — https://csdb.dk/scener/?id=1926 (returned HTTP 503 on 2026-06-16)
- **Demozoo:** https://demozoo.org/sceners/6764/
- **MobyGames:** https://www.mobygames.com/person/53900/jesper-olsen/
- **Website (defunct):** www.vibrants.dk

**Active C64 years:** 1988–1994 (peak 1988–1991 as Amok/Genesis Project).

**Key biographical note (Demozoo/last.fm):**
> "He had unique knowledge about coding players for computer formats such as the Amiga
> home computer and the Roland MT-32 on the PC. He also made his own players on C64 and
> for the AdLib sound card."

**Composition method (blog.chordian.net, JCH writing about JO's AdLib work):**
> "Jesper Olsen also wrote his very own AdLib player and composed tunes for it in an
> assembler listing."

JO writes his players hand-in-assembler with no GUI editor — both AdLib and C64.
The data format is therefore encoded directly in the assembler source: no editor tool
to extract a format spec from. **No public release of the C64 player source or editor
has been found.**

**HVSC Musicians.txt entry:**
```
JO (Olsen, Jesper {Technic, Rock}) / Amok / Vibrants - DENMARK
```

**Demozoo production list (selected highlights):**

| Year | Title | Type | Alias |
|------|-------|------|-------|
| 1988 | Multi Move | 8K Intro (Code+Graphics+Music) | Rock |
| 1988 | Pice of Mind | Music | JO |
| 1988 | Behind the Wheel | Cracktro music | Rock |
| 1989 | The Batcave | Demo (Code+Music+Graphics) | JO |
| 1989 | Battle Pac | Music | JO |
| 1989 | Sex'n'Crime #1-#11 | Diskmag music | Jesper Olsen |
| 1990 | Various demos | Music | JO/Jesper Olsen |
| 1991 | Beermacht, Unreal, Spritemania | Demo music | JO |
| 1992 | Copper | MS-DOS: Code (player) + Music | JO |
| 1994 | Notes | C64 Demo music | JO |

The 1992 "Copper" entry explicitly credits "Code (player), Music" — JO wrote a custom
player for MS-DOS as well. His C64 player career peaked 1988–1991.

**Vibrants group context:**
Vibrants was founded October 1989 by JCH, DRAX, and Link. All members were musicians.
Members: DRAX, JCH/Chordian, Joss, Laxity, Link, Metal, MSK, JO (joined ~1992).
Each member used their **own** player engine:
- JCH: JCH Editor v1/v2.53/v3.04 (public, released on CSDb)
- Laxity: his own player (sidid: `Vibrants/Laxity`, CSDb id=122333)
- JO: his own player (sidid: `Vibrants/JO`, this engine)
- DRAX: used multiple players including JO's (see DRAX "Worktune in JO's player" in HVSC)

**Game audio credits:**
JO scored games for Interactivision, Brain Bug, FunSoft (Germany), Interactive Television
Entertainment, Tale Software/Kingsoft. The same JO player appears in game rips (sidid
fingerprint matches them).

## 3. Player Format Clues

All the following is inferred from the sidid opcode signatures plus binary inspection
of local HVSC files. **No documented format spec found online.**

### Architecture

- **3-voice loop, X = voice index (0–2):** Sig 9 (`A2 02 ... CA 10`) shows a canonical
  DEX loop structure. Voice 2 processed first, then 1, then 0.
- **Zero-page pointer + Y-walk (`BC`+`B1` pairs):** `LDY abs,x` loads a per-voice index
  into Y, then `LDA (zp),y` reads through a zero-page pointer. This is the standard
  6502 pattern for "pointer table in ZP, Y is the read cursor." Data tables (note lists,
  instrument programs) are accessed this way.
- **Per-voice counters in absolute arrays:** `FE ?? ??` (INC abs,x) and `DE ?? ??`
  (DEC abs,x) increment/decrement per-voice duration or speed counters using X as index.

### Sentinel command bytes in data streams

From sig comparisons (`CMP #imm` values seen in the signatures):

| Byte | Likely meaning |
|------|---------------|
| `$80` | Note boundary / high-note flag (Sig 1: `C9 80 D0`) |
| `$60` | Note threshold — values `< $60` are note indices, `>= $60` are commands (Sig 5) |
| `$F0` | Sequence command / block marker (Sig 3) |
| `$FF` | End-of-sequence / restart marker (Sig 4) |
| `$D0`+ | Instrument select: `(byte - $D0) * 8` = offset into 8-byte instrument table (Sig 8) |

### Instrument table stride

Sig 8: `CMP #$D0 / BCC / SBC #$D0 / ASL / ASL / ASL / STA abs,x`
→ three left-shifts = multiply by 8 → **8-byte instrument records**.

### Gate-off / voice reset

Sig 9 decodes exactly to:
```
LDX #2                  ; 3-voice loop
LDY abs,x              ; load voice Y-register offset (0/7/14 for D400/D407/D40E)
LDA #0
STA $D405,y            ; AD = 0
STA $D406,y            ; SR = 0
LDA #8
STA $D404,y            ; Ctrl = $08 (test bit set, gate off)
DEX
BPL ...
RTS
```
Standard test-bit gate-off (hard-restart capable).

### Frequency operations

`18 7D ?? ??` = `CLC / ADC abs,x` — frequency accumulation with per-voice absolute
table. Used for glide or vibrato (frequency delta added to current freq).

### Zero-page layout (from Grid.sid init)

Init loop `LDX #$3A / ... / STA $40,X / STA $D400,X / DEX / BPL` clears:
- ZP $40–$7A: 58 bytes of per-voice engine state (~19 bytes per voice × 3)
- SID $D400–$D43A: all voice registers
- ZP $75: confirmed as frame counter (DEC $75 in play loop)
- ZP base $40: voice 0 state block; $53: voice 1; $66: voice 2 (approx, ~19 bytes each)

### Dispatch table pattern

Most tunes start with:
```
$LOAD+0: 4C xx xx    JMP init_routine   ; or pad bytes
$LOAD+3: 4C xx xx    JMP play_routine
```
Play entry may precede init in address space for some tunes (Sex_n_Crime_10,
Turn_It have play before init).

## 4. Version Variants

**No version variants documented online.** sidid has exactly one `[Vibrants/JO]` block.
The address-space scatter ($1000–$F000 load addresses) is relocation, not versioning.

**Evidence for a single relocatable engine:**
- sidid fingerprint matches across all 103 JO/ SIDs — consistent byte patterns
  regardless of load address → the engine relocates (JO re-assembles for each tune's
  load address or uses a simple assembler-origin parameter)
- sidid.cfg signatures avoid absolute addresses (`??` wildcards on all operand bytes)
- HJE tunes (German composer, ~23 SIDs) also match — JO distributed the engine to
  at least one other composer

**Internal variation signals:**
- Init offset from load address varies: load+0, load+3, load+6, load+$16, etc.
- Some tunes have code before data (play routine near load); others have data first
  (Amok_Title: data at $1006–$17FF, code at $180A)
- Code sizes span 635–6705 bytes. The minimal 635-byte Grid.sid may be a stripped
  engine; typical size 2000–3500 bytes includes full effects

## 5. Leads to Follow

### High priority

1. **CSDb scener page for JO** (id=1926) — was returning HTTP 503.
   URL: https://csdb.dk/scener/?id=1926
   When accessible: full release list; look for "player" or "music system" releases.

2. **sidid.nfo full text for `[Vibrants/JO]` entry** — the NFO was too large to read fully.
   URL: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
   May have AUTHOR/RELEASED/CSDB fields linking to a player release.

3. **CSDb Vibrants group page** — uncertain ID (likely not 672; that was a different group).
   URL: https://csdb.dk/search/?seinsel=group&search=vibrants&Go=Go
   Find correct Vibrants group ID, then look for tool releases.

4. **vibrants.dk archive** — group website defunct but archived.
   URL: https://web.archive.org/web/*/vibrants.dk
   JO's AdLib MP3s were hosted there; C64 player source may also exist.

5. **"Copper" demo (1992, Surprise! Productions)** — Demozoo credits JO with
   "code player creation" on this MS-DOS demo. The demo binary may contain a clean
   or commented version of his player methodology.
   URL: https://csdb.dk/search/?search=Copper+1992

6. **HJE (Hans Jürgen Ehrentraut)** — used JO's player for ~23 SIDs. His CSDb page may
   have notes about obtaining the player or format documentation.
   URL: https://csdb.dk/search/?search=HJE

7. **`Gamlere`, `Gamlest`, `Rob_Lam_Fejl`** — all share play address $425C despite
   different init addresses. This sub-cluster is the best reference for a canonical
   engine layout (same code, different init trampolines). Ideal starting point for
   disassembly — one engine instance to label, three tunes to cross-validate.

### Medium priority

8. **zimmers.net Vibrants archive** — contains JCH tools (Deluxe Drivers, JCH Editor)
   but NOT JO tools (confirmed by this session).
   URL: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/

9. **archive.org: "Smack My SID Up — Best of Vibrants"** (mtk056)
   URL: https://archive.org/details/mtk056
   May contain player binaries alongside SID rips.

10. **pouet.net search for Vibrants/JO** — demoscene releases sometimes have inline
    format comments.

11. **realdmx/c64_6581_sid_players** — does NOT include JO (confirmed), but it shows
    the format for similar-era players. Useful reference for RE methodology.
    URL: https://github.com/realdmx/c64_6581_sid_players

## 6. Raw Findings by Source

| Source | Status | Key content |
|--------|--------|-------------|
| CSDb (all endpoints) | HTTP 503 during session | Unreachable 2026-06-16 |
| cadaver/sidid sidid.cfg (GitHub) | Fetched | Full signature block extracted; see `src/sidid_vibrants_jo_signatures.txt` |
| WilfredC64/player-id (GitHub) | Fetched | Confirms same signatures, no additions |
| Demozoo scener/6764 | Fetched | Production list, biography, group history |
| MobyGames person/53900 | Fetched | Game credits: Interactivision, Brain Bug, FunSoft, ITE |
| blog.chordian.net (JCH 2017) | Fetched | Confirms JO composes in assembler listing, no GUI |
| last.fm / Jesper Olsen | Fetched | Confirms custom C64 + AdLib + Amiga + MT-32 players |
| zimmers.net Vibrants archive | Fetched | JCH tools only; no JO tools |
| DeepSID (chordian.net) | Not fetched (JS-rendered) | Would show player tag in header |
| GitHub code search (vibrants JO) | Searched | No source code or disassembly found |
| archive.org | Searched | No JO C64 player source found |
| Local HVSC corpus | Analyzed | Full header table; binary inspection of Grid/Airwolf_Theme/Amok_Title |
| HVSC STIL.txt | Analyzed | No technical player notes; only musical attribution |
| HVSC Musicians.txt | Analyzed | Identity confirmed |

## 7. Searches That Came Up Empty

- "Vibrants JO player" C64 SID player — no format documentation
- "Poul-Jesper Olsen" C64 — only biography, no technical content
- "sidid Vibrants" SID player detection — returned sidid tool description, no JO-specific notes
- "JO SID player C64 vibrants" — scene biography pages only
- "Vibrants JO SID player format" — nothing on-topic
- site:csdb.dk vibrants JO music player — CSDb was down, search returned nothing
- "Vibrants" C64 demo group Denmark musicians — group history only
- HVSC JO Vibrants music player format — no results
- GitHub code search for "vibrants JO SID player" — no matching repos
- Archive.org search for JO C64 collection — JCH collection found, no JO equivalent
- Any existing disassembly, source code, or format documentation for the JO player — **NONE FOUND**

The JO player has not been publicly documented beyond the sidid fingerprint signatures.
All format knowledge must be derived by binary analysis of the HVSC corpus.
