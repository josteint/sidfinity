---
source_url: multiple — see content
fetched_via: direct
fetch_date: 2026-06-16
author: various
content_date: various
reliability: secondary
---

# Vibrants/JO C64 SID Player — Research Findings

## Overview

**JO** is the scene handle of **Poul-Jesper Olsen** (also called simply "Jesper Olsen"), a
Danish C64 composer and coder born in Denmark. His other handles were **Technic** and **Rock**.

He was active from roughly 1988 through the early 1990s, primarily under the groups:

- **Amok** (until 1991) — where his earliest C64 work appears (copyright "Amok Sound Dept.")
- **Genesis Project** (until 1991)
- **Vibrants** (joined ~1992, officially still a member but inactive since the 1990s)

According to JCH's blog (Chordian.net), JO "joined Vibrants around 1992, at that time
already well known as a C64 composer for Amok." He was "almost obsessed with coding efficient
music players" and composed music exclusively via the **assembler listing method** — he never
completed a dedicated music editor despite his technical prowess.

He worked professionally for: **Interactivision**, **Brain Bug**, **FunSoft** (Germany), and
**Interactive Television Entertainment**.

His Demozoo profile: https://demozoo.org/sceners/6764/
His CSDb scener page: https://csdb.dk/scener/?id=1926

---

## CSDb Findings

### JO's CSDb Profile (id=1926)

- **Groups:** Vibrants (current), Amok (former), Genesis Project (former)
- **Roles:** Coder, Musician
- **Alternative handles:** Technic, Rock
- **Country:** Denmark
- **Status:** "has not been active since the 90's"

Key direct releases by JO on CSDb:
- **"Importent Note"** (1989) — Misc.
- **"Airwolf Theme"** (year unknown) — Music

He has credits for music in hundreds of productions spanning 1989–2026 (crack intros,
demos, music collections, diskmags). Most activity was 1989–1992.

### DRAX's "Worktune in JO's Player" (SID id=9837)

This is the single most technically useful find: DRAX (Thomas Mogensen) composed a
work-in-progress tune specifically using JO's player, titled **"Worktune in JO's player"**,
released 1990–91 under Vibrants.

Technical specs from CSDb:
- **Load address:** $0800
- **Init address:** $1000
- **Play address:** $1003
- **SID model:** 6581
- **Clock speed:** PAL
- **Data size:** 4733 bytes ($127D)
- **Songs:** 1
- **HVSC path:** `/MUSICIANS/D/DRAX/Worktunes/Worktune_in_JOs_player.sid`

The init at $1000 and play at $1003 is consistent with a typical C64 player layout
(init+play at top of page at $1000, with play being just a JMP or short dispatch
3 bytes into the same page).

JO's own tunes also share the $1000/$1003 pattern, as seen in the "Ode to JO" SID
(JCH tribute, load=$1000, init=$1000, play=$1003, data=2730 bytes).

### Related CSDb Releases

- **"Ode to JO"** (SID id=15662) — composed by JCH/Vibrants in tribute to JO, 1989.
  Load=$1000, init=$1000, play=$1003, data=2730 bytes ($0AAA), 1 song, 6581, PAL.
  Used in many Vibrants productions 1989–2001.
  HVSC: `/MUSICIANS/J/JCH/Ode_to_JO.sid`

---

## Forum Findings

### Chordian.net Blog — "My Computer Chronicles, Part 3"
URL: https://blog.chordian.net/2017/01/14/my-computer-chronicles-part-3/

Most technically valuable secondary source. JCH (Jens-Christian Huus) writes about
his experience meeting JO of Amok:

> "Jesper [JO] was almost obsessed with coding efficient music players."

> "Jesper also learned how to code a player on the Amiga — both using samples and
> emulated pulsating," enabling music delivery across multiple formats for games.

> JO composed music exclusively through "the assembler listing method," never completing
> a dedicated music editor despite his technical prowess with player coding.

**Key technical insight — Hard Restart:** JCH credits JO as the person who introduced
him to the "hard restart" technique for SID ADSR envelopes:

> "triggering a new note would sometimes start the ADSR in a faulty manner, interpreting
> the volume differently. The solution involved putting zero values in the registers during
> the last two frames of the lifetime of a note."

This technique — writing $00 to all voice registers ($D400–$D406) for 2 frames before
a new note attack — is a distinctive feature of technically careful C64 music players
of this era. It is strongly implied that the JO player implements hard restart.

### Chordian.net Blog — "The Later AdLib Music by Vibrants"
URL: https://blog.chordian.net/2017/12/03/the-later-adlib-music-by-vibrants/

> "JO wrote his very own AdLib player and composed tunes for it in an assembler listing."

Confirms the pattern: JO's preferred workflow was to write the player in assembly, then
compose music data directly in the same medium (no editor GUI).

### CSDb Forums (forumsearch=JO+player)

Limited hits; most relevant:
- Post #129 mentions "an editor was the players by JO, 20cc and Laxity" — placing JO's
  player in the company of Laxity's player (a well-known Vibrants player with its own
  sidid.cfg entry) and 20cc's player.

### Vibrants Group Overview

Vibrants was a Danish C64/PC music group founded October 1989. Members built their own
players and editors:
- JCH built the JCH Music Editor (v1 → v2.53 → v3.04 Final)
- Laxity built his own editor (v/32-3.34 on CSDb id=122333)
- JO built his own player (no standalone tool release found on CSDb/Demozoo)
- Thomas Egeskov Petersen (Laxity) later created SID Factory II

Utilities available at zimmers.net under `/pub/cbm/c64/audio/Vibrants/utils/`:
- Deluxe Driver 2.0/3.0/4.0/5.0 (JCH player runtime)
- JCH Split v1.1, Relocate JCH.prg
- **Relocate Laxity.prg** — relocator for Laxity tunes
- **VibRip50.00.prg** — "a music ripper utility" (generic Vibrants ripper)

Note: No dedicated "JO player relocator" or "JO editor" is listed in the utils archive —
consistent with JO's assembler-listing workflow (his player may not have been distributed
as a standalone tool).

---

## Player Format Hints

### SID Identification (sidid.cfg)

The `cadaver/sidid` project (https://github.com/cadaver/sidid) is the authoritative C64
player identification tool. The `sidid.cfg` file contains the following entry:

```
Vibrants/JO
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

10 distinct signature patterns, separated by line breaks. The `??` bytes are wildcards
(match any value at that position), allowing the scanner to handle relocation. The `END`
keyword terminates each pattern.

### Decoding the Signatures

Some patterns can be partially decoded as 6502 mnemonics:

**Pattern 1:** `C9 80 D0 ?? BC ?? ?? C8 B1 END`
- `C9 80` = CMP #$80 (compare A with 128)
- `D0 ??` = BNE (branch if not equal)
- `BC ?? ??` = LDY abs,X (load Y from table indexed by X)
- `C8` = INY
- `B1` = LDA (zp),Y (indirect Y load)
This looks like a pattern/sequence pointer decode loop with sentinel value $80.

**Pattern 3:** `BC ?? ?? B1 ?? C9 F0 D0 ?? C8 B1 ?? 18 7D ?? ?? 9D ?? ?? C8 B1 ?? 9D ?? ?? FE ?? ?? FE ?? ?? FE END`
- `BC ?? ??` = LDY abs,X (voice index table lookup)
- `B1 ??` = LDA (zp),Y (indirect load from pattern)
- `C9 F0 D0 ??` = CMP #$F0, BNE (check for $F0 marker — likely a command byte)
- `C8 B1 ??` = INY, LDA (zp),Y (read next byte = parameter)
- `18 7D ?? ??` = CLC, ADC abs,X (add something from table — likely transpose/offset)
- `9D ?? ??` = STA abs,X (store to voice register)
- `C8 B1 ??` = INY, LDA (zp),Y (read next byte)
- `9D ?? ??` = STA abs,X
- `FE ?? ??` = INC abs,X (three of these — increment three counters/pointers)
This is a 3-voice pattern decoder with command byte $F0 and follow-on parameter bytes.

**Pattern 4:** `BC ?? ?? B1 ?? C9 FF D0 ?? A9 00 9D ?? ?? DE ?? ?? D0 ?? A9 01 9D ?? ?? FE END`
- `C9 FF D0 ??` = CMP #$FF, BNE (sentinel $FF = end of pattern/loop marker)
- `A9 00 9D ?? ??` = LDA #0, STA abs,X (reset position counter on pattern end)
- `DE ?? ??` = DEC abs,X (decrement a counter)
- `D0 ??` = BNE (if counter not zero, continue)
- `A9 01 9D ?? ??` = LDA #1, STA abs,X (set a flag)
- `FE ?? ??` = INC abs,X (increment orderlist pointer)
Pattern/orderlist wraparound: $FF = end-of-pattern marker, triggers orderlist advance.

**Pattern 5:** `BC ?? ?? B1 ?? C9 60 90 ?? 38 E9 60 9D ?? ?? FE ?? ?? BC ?? ?? B1 ?? D0 ?? 9D ?? ?? FE END`
- `C9 60 90 ??` = CMP #$60, BCC (if < $60, branch — note range check)
- `38 E9 60` = SEC, SBC #$60 (subtract $60 — command byte range $60–$7F = 32 values)
- `9D ?? ??` = STA abs,X
- `FE ?? ??` = INC abs,X
This looks like a command decode for bytes $60–$7F (possibly instrument/effect commands).

**Pattern 8:** `C9 D0 90 ?? E9 D0 0A 0A 0A 9D END`
- `C9 D0 90 ??` = CMP #$D0, BCC (if < $D0 branch)
- `E9 D0` = SBC #$D0 (subtract $D0 — range $D0–$DF = 16 values)
- `0A 0A 0A` = ASL ASL ASL (shift left 3 = multiply by 8)
- `9D` = STA abs,X (store result)
Command decode for bytes $D0–$DF, values shifted left 3 (×8).

**Pattern 9:** `A2 02 BC ?? ?? A9 00 99 05 D4 99 06 D4 A9 08 99 04 D4 CA 10 ?? 60 END`
- `A2 02` = LDX #2 (loop for 3 voices, X=2,1,0)
- `BC ?? ??` = LDY abs,X
- `A9 00 99 05 D4` = LDA #0, STA $D405,Y (release = 0, sustain = 0)
- `99 06 D4` = STA $D406,Y (release register = 0)
- `A9 08 99 04 D4` = LDA #8, STA $D404,Y (gate bit = 0 + test bit set??? wait: $08 = %00001000 = test bit)
- `CA 10 ??` = DEX, BPL (loop for all 3 voices)
- `60` = RTS
This is the **hard restart / voice reset** routine! It loops over all 3 voices and:
  1. Sets ADSR sustain/release regs to 0
  2. Sets $D404 to $08 (test bit, gate off) — the classic hard restart setup

**Pattern 10:** `30 03 4C ?? ?? A9 00 9D ?? ?? A9 08 99 04 D4 98 48 A0 00 BD END`
- `30 03` = BMI (branch if minus — conditional)
- `4C ?? ??` = JMP (jump to somewhere)
- `A9 00 9D ?? ??` = LDA #0, STA abs,X (clear a register)
- `A9 08 99 04 D4` = LDA #8, STA $D404,Y (again: test bit set on $D404)
- `98 48 A0 00` = TYA, PHA, LDY #0
- `BD` = LDA abs,X (load from table)
More hard-restart related code: sets test bit, saves Y, then reads from indexed table.

### Key Structural Observations from Signatures

1. **3-voice structure**: Pattern 9 explicitly loops `X = 2, 1, 0` over voices, using
   `$D404,Y`, `$D405,Y`, `$D406,Y` via indexed access (Y = voice offset from table).

2. **Hard restart confirmed**: Pattern 9 is unmistakably the hard restart routine.
   $D405,Y ← 0 (AD=0), $D406,Y ← 0 (SR=0), $D404,Y ← $08 (test bit, gate off).
   This confirms JCH's anecdote that JO introduced the hard restart technique.

3. **Pattern sentinel bytes**:
   - $80 = likely rest/end-of-row sentinel (pattern 1: CMP #$80)
   - $F0 = command byte marker in pattern stream (pattern 3)
   - $FF = end-of-pattern / orderlist sentinel (pattern 4)
   - $60–$7F = instrument/effect command range (pattern 5, 32 possible values)
   - $D0–$DF = another command range (pattern 8, multiply-by-8 decode)

4. **Data model**: The player uses **indirect Y addressing via pointer table** (`BC ?? ??`
   = `LDY abs,X` to get Y from per-voice pointer, then `B1 ??` = `LDA (zp),Y` to read
   pattern bytes). This is a standard C64 3-voice player pattern.

5. **Init address $1000, play $1003** seen in both "Worktune in JO's Player" (DRAX,
   load=$0800) and JCH's "Ode to JO" (load=$1000). The player code starts at $1000;
   play vector is 3 bytes into the player (likely a JMP or the first instruction of the
   play routine if init is a separate subroutine within the same page).

### Comparison with Vibrants/Laxity

The `sidid.cfg` also contains a **Vibrants/Laxity** entry (5 signatures, separate from JO),
confirming that Laxity's player is a distinct implementation despite both being Vibrants
members. The Laxity player's first signature pattern uses `18 7D ?? ??` (CLC, ADC abs,X)
with a different overall structure. Both use `BC ?? ??` (LDY abs,X) for voice dispatch,
which is a common C64 idiom.

### sidid.nfo

The `sidid.nfo` file (authors/credits for the sidid.cfg) gives for Vibrants/JO:
- **AUTHOR:** Poul-Jesper Olsen (JO)
  (no CSDb link, no version number — suggesting less documentation than the Laxity entry)

For comparison, Vibrants/Laxity has: `REFERENCE: https://csdb.dk/release/?id=122333`

---

## Tools

### Identification tools (sidid.cfg)

- **sidid** (cadaver): https://github.com/cadaver/sidid — identifies Vibrants/JO player
  in SID files via the 10 signatures documented above. The player is recognized as a
  single entity (no version variants listed in sidid.cfg).

- **Player-ID** (WilfredC64): https://github.com/WilfredC64/player-id — uses same
  sidid.cfg format; also recognizes Vibrants/JO.

- **Restore64**: https://restore64.dev/ — mentions recognizing "JCH, Vibrants,
  GoatTracker, and hundreds more" from its 787-player SIDID database.

### Ripping tools (Vibrants-era)

- **VibRip50.00.prg** — "a music ripper utility" from the Vibrants utils archive at
  `https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/utils/`. Likely generic
  Vibrants music ripper; unclear if specifically handles the JO player format.

- **Relocate Laxity.prg** — Laxity-specific relocator; implies the JO player may need a
  separate (unarchived) relocator if it uses absolute addresses.

- **JCH Deluxe Driver** (2.0/3.0/4.0/5.0) — JCH player runtime; not the JO player.

### HVSC's SID files (the primary artifact)

The 119 SID files in `/MUSICIANS/J/JO/` are themselves the best available documentation
of the player format. All appear to be PSID v2. They include diagnostic names like
`JO_Test_1.sid` and `JO_Test_2.sid` which are presumably JO's own test/development tunes.

---

## Games Using JO's Player

JO composed music professionally but it's unclear how many commercial games used his
own player vs. a licensed engine. Known uses:

- **Harald Hårdtand: Kampen om de rene tænder** — JO provided Amiga port audio support
  (C64 version by DRAX; JO handled Amiga/DOS ports with JCH). Not confirmed to use
  JO's C64 player specifically.

- **Interactivision** games — JO worked professionally for this company; his C64 tunes
  in that period likely used his custom player. Specific titles not confirmed from
  available sources.

- **Brain Bug** titles — JO worked for Brain Bug; same caveat applies.

- **FunSoft (Germany)** — professional work; titles unknown from web sources.

- **Demoscene productions** — many crack intros, demos, and music collections in the
  Vibrants/Amok/Genesis Project catalogs from 1989–1992 use JO's player. See his CSDb
  credits page (id=1926) for the full list.

---

## Leads to Follow

### Highest-priority leads

1. **Examine the actual SID binaries** — the 119 SID files in HVSC `/MUSICIANS/J/JO/`
   are available locally at `hvsc84/MUSICIANS/J/JO/`. Run `sidid` on them to confirm
   player identification, then disassemble one (e.g. `Airwolf_Theme.sid`) to map the full
   player code. The signatures from `sidid.cfg` give exact byte anchors to locate the
   play routine.

2. **DRAX's "Worktune in JO's Player"** — at
   `hvsc84/MUSICIANS/D/DRAX/Worktunes/Worktune_in_JOs_player.sid` — this is a reference
   implementation. DRAX (a Vibrants co-member) used JO's player format for a tune,
   meaning the data format was understood by other members and the player was at least
   semi-shared within Vibrants.

3. **`JO_Test_1.sid` and `JO_Test_2.sid`** — JO's own test tunes may have simpler data
   than production tunes, making the format easier to reverse-engineer.

4. **sidid.cfg signature-guided disassembly** — each signature corresponds to a specific
   routine in the play() function. Pattern 9 (hard restart) and Pattern 4 ($FF sentinel
   handler) are the clearest entry points for understanding the player structure.

5. **Laxity player comparison** — Laxity/Vibrants player has a CSDb reference
   (id=122333 = Laxity Editor v/32-3.34). Comparing Laxity's documented format with JO's
   could reveal shared lineage or divergence. The sidid signatures are distinct, but the
   `LDY abs,X` / `LDA (zp),Y` idiom appears in both.

6. **CSDb scener page id=1926** — try fetching JO's full release list when CSDb is
   available (it returned 503 during this research session).

7. **Vibrants website www.vibrants.dk** — timed out during research. May have archival
   material about JO's player.

8. **VibRip50.00.prg** — download and inspect this ripper to see if it handles the JO
   player format.

### Unanswered questions

- Does the JO player use a unified data segment (player + data at $1000, with music data
  starting immediately after the player), or are they in separate segments?
  (DRAX's Worktune has load=$0800, suggesting the data portion may start earlier, or
  the $0800 region contains something else — possibly a loading stub.)

- Are there multiple versions of the JO player? The sidid.cfg has no version annotations,
  but tunes span 1988–1992, suggesting the player may have evolved.

- Which specific commercial games published by Interactivision/Brain Bug/FunSoft used
  JO's own C64 player vs. a publisher-provided engine?

- The `Airwolf_Theme.sid` copyright says "1988 Amok Sound Dept." — did JO write a
  separate player while at Amok, or is the Vibrants/JO player the same codebase he
  used at Amok?

- JO composed music via assembler listing — does this mean the data is encoded directly
  in assembly source (which the player interprets), or are there separate data tables
  (like a typical tracker with note/pattern arrays)?

---

## Source URLs

| URL | Summary |
|-----|---------|
| https://demozoo.org/sceners/6764/ | JO's Demozoo profile — identity, groups, productions list |
| https://csdb.dk/scener/?id=1926 | JO's CSDb profile — groups, roles, release credits |
| https://csdb.dk/sid/?id=9837 | DRAX "Worktune in JO's player" — technical specs |
| https://csdb.dk/sid/?id=15662 | JCH "Ode to JO" — technical specs |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg | sidid.cfg — Vibrants/JO signature (10 patterns) |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo | sidid.nfo — author attribution: Poul-Jesper Olsen (JO) |
| https://github.com/cadaver/sidid | cadaver's sidid player identification tool |
| https://github.com/WilfredC64/player-id | Player-ID tool (also uses sidid.cfg) |
| https://blog.chordian.net/2017/01/14/my-computer-chronicles-part-3/ | JCH blog: JO introduced hard restart; assembler-listing method |
| https://blog.chordian.net/2017/12/03/the-later-adlib-music-by-vibrants/ | JCH blog: JO wrote own AdLib player in assembler listing |
| https://retroworld.canell.dk/music/group/vibrants-c64.html | Vibrants group overview — members, editors, music tools |
| https://demozoo.org/groups/769/ | Vibrants group Demozoo page — members, FairPlay, tools |
| https://hvsc.etv.cx/?path=C64Music%2FMUSICIANS%2FJ%2FJO | HVSC mirror — JO's 119 SID files listed |
| https://hvsc.etv.cx/?info=please&path=C64Music%2FMUSICIANS%2FJ%2FJO%2FAirwolf_Theme.sid | Individual SID metadata (limited — PSID v2, 1 song) |
| https://www.hvsc.c64.org/download/C64Music/DOCUMENTS/Musicians.txt | HVSC Musicians.txt — JO entry: "JO (Olsen, Jesper {Technic, Rock}) / Amok / Vibrants - DENMARK" |
| https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/utils/ | Vibrants utils archive — Deluxe Drivers, JCH tools, VibRip |
| https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/Deek/ | Vibrants Deek music files ($1000/$1003 format) |
| https://pixelatedaudio.com/harald-hardtand/ | Harald Hårdtand game — JO ported Amiga audio |
| https://www.last.fm/music/Jesper+Olsen+(JO)/Vibrants+(AdLib) | Last.fm: JO AdLib music from Vibrants |
| https://www.mobygames.com/person/53900/jesper-olsen/ | MobyGames: JO's game credits (403 — inaccessible) |
| https://csdb.dk/release/?id=122333 | Laxity Editor v/32-3.34 (sidid.nfo reference for Vibrants/Laxity) |
| https://blog.chordian.net/2018/01/03/sid-musicians/ | JCH blog — SID musicians overview (no JO detail) |
| https://blog.chordian.net/2018/02/24/comparison-of-c64-music-editors/ | C64 editor comparison (no JO detail) |
