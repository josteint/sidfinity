---
source_url: multiple — see per-section citations below
fetched_via: WebFetch + WebSearch
fetch_date: 2026-06-13
author: synthesised from primary sources
content_date: 1988–2026
reliability: primary (interview + help-file quotes); secondary (synthesised context)
---

# Digitalizer — TASK 1: Ancestor research (Prosonix / SteinTronic + JCH)

## Summary of findings

Olav Mørkrid's admission that Digitalizer was "copied" from Stein Pedersen's editor
is documented in TWO independent primary sources — the V3.0 help file shipped with
the editor itself (June 1992) and the Recollection #2 interview (2006). Both are
already in this docs directory. The ancestor editor is confirmed as "SteinTronic"
(= "Prosonix Music Editor", CSDb id 179618). Three Prosonix player variants exist
in sidid.cfg. The JCH/Vibrants connection is JCH = Jens-Christian Huus, creator of
DeepSID (formerly "Chordian"), who added SteinTronic to DeepSID in July 2019.

---

## 1. The ancestor editor — Prosonix Music Editor (= SteinTronic)

### Identity

| Attribute | Value |
|-----------|-------|
| Name | Prosonix Music Editor |
| AKA | SteinTronic |
| Author | Stein Pedersen (Offence, Panoramic Designs, Prosonix) |
| Group | Prosonix (Norway, formed 1988) |
| CSDb release ID | 179618 |
| CSDb URL | https://csdb.dk/release/?id=179618 |
| Disk image | SteinTronic1.d64 |
| Download count | 187 (CSDb) |
| DeepSID entry | Added by JCH on 2019-07-16 (comment on CSDb release page) |

### Source: CSDb page (release id 179618)
> Release name: "Prosonix Music Editor"
> AKA: "SteinTronic"
> Credits: code and music by Stein Pedersen of Offence, Panoramic Designs, Prosonix
> Type: C64 Tool
> Download: SteinTronic1.d64 (D64 disk image)
> SID demo included: "Spaceship Cleopatra" by Stein Pedersen (in HVSC)
> Comment (JCH, 2019-07-16): "An entry for this editor has now been added in DeepSID."
Source: https://csdb.dk/release/?id=179618 (WebFetch 2026-06-13, reliability: primary)

### Stein Pedersen — profile

| Attribute | Value |
|-----------|-------|
| Real name | Stein Pedersen |
| Handles | Stone, The Idol, 1030 |
| Location | Oslo County, Oslo, Norway |
| Groups | Prosonix (1989–present), Panoramic Designs (1990–present), Offence (2009–present), The Troopers (prior), Fresh And In Charge (prior), Jazzcat Cracking Team, Newlook, The Megateam |
| Roles | Coder, Graphician, Musician |
| CSDb profile | https://csdb.dk/scener/?id=2272 |
| Demozoo profile | https://demozoo.org/sceners/1249/ |
| CSDb rating | 9.4/10 as coder (10 votes), 9.4/10 as musician (18 votes) |

**Stein Pedersen was a Panoramic Designs member simultaneously.** This is why the
V3.0 help file credits him alongside Olav Mørkrid under the Panoramic banner — they
were in overlapping groups (Prosonix + Panoramic Designs). CSDb notes: "the prosonix
team is now a part of panoramic."

Stein Pedersen's other notable tools:
- SIDBlaster USB driver BETA (2015) — hardware SID interface driver
- SIDdecompiler V0.5 and V0.8 (2017, 2019, with Prosonix) — 6502-tracing SID decompiler

---

## 2. Primary admission sources

### Source A: V3.0 Help File (June 1992) — verbatim

Already in this docs directory at `docs/src/digitalizer_v3.0_instructions.txt`.
Relevant passage (verbatim from the help file ASCII-converted by 6R6 in 2013):

> "I would like to thank prosonix for inspiration (vi kaller det herming!) and
> Geir/Mozicart for helpful discussions (I hope you got some help too!).
>
> The crew consists of:
> Lars Hoff            Prosonix
> Ole-Marius Pettersen Prosonix
> Stein Pedersen       Prosonix
> Geir Tjelta          Mozicart
> Trond Lindanger      Mozicart
> Henning Rokling      Panoramic
> Richard Nygaard      Panoramic
> Olav Morkrid         Panoramic"
>
> — OLAV M0RKRID, June 1992

**"vi kaller det herming"** = Norwegian: "we call it imitation/mimicry." A self-aware
admission that Digitalizer was modelled on the Prosonix Music Editor. The Norwegian
word "herming" has a nuance of imitating in jest / affectionate copying, not plagiarism.

Source: docs/src/digitalizer_v3.0_instructions.txt
(Extracted from CSDb zip http://csdb.dk/getinternalfile.php/118523/Digitalizer-2.9(ff)%20v3.0.zip)
Reliability: primary (original author's words, 1992)

### Source B: Recollection #2 Interview (2006) — verbatim

URL: https://www.atlantis-prophecy.org/recollection/?load=interviews&id_interview=129
(WebFetch 2026-06-13)

The interviewer asked Olav about a comment from Stein Pedersen that Olav had
"borrowed his music editor via a freeze backup." Olav's response:

> "Well, he is right. I admit to the crime. Stein deserves the true credit for
> making the first and best music editors."

The interview also describes Stein Pedersen (Troopers/Prosonix) as having "always
had a firm touch with everything he does" and being "too modest for his talents."

**Note:** The interview does NOT mention "SteinTronic" by name, nor does it discuss
JCH/Vibrants, specific format details, or Digitalizer version numbers. It focuses on
demo work and Funcom. The freeze-backup reference implies Olav obtained the editor
binary via a cartridge freeze (Action Replay / Final Cartridge) rather than source.

Reliability: primary (author's own words, 2006)

---

## 3. What the "herming" implies for the format

The V3.0 help file names Prosonix members as credits for "inspiration." The sidid.cfg
contains THREE Prosonix player variants, confirming the Prosonix player was a
significant, actively-evolved format:

```
Prosonix
29 7F 9D ?? ?? A9 ?? 99 01 D4 END
DE ?? ?? 10 ?? A9 80 19 ?? ?? 9D ?? ?? B9 ?? ?? 29 03 C9 01 D0 ?? 9D ?? ?? 4C END

Prosonix_new
B1 ?? 10 26 C9 C0 90 ?? C9 E0 END

Prosonix_tiny
B1 ?? 8D 00 D4 C8 B1 ?? 8D 01 D4 C8 84 ?? 60 B1 END
```

Source: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg (WebFetch 2026-06-13)

### Prosonix variant analysis (OPEN — no RE performed)

**Prosonix (original):**
- `29 7F` = AND #$7F → mask off bit 7 (7-bit value extraction)
- `9D ?? ?? A9 ?? 99 01 D4` → STA $????,X + LDA #imm + STA $D401,Y → SID pulse-hi write
- `DE ?? ?? 10 ??` = DEC indexed + BPL (counter loop)
- `A9 80 19 ?? ??` = LDA #$80 + ORA $????,Y (set bit 7 / flag)
- `9D ?? ??` = STA indexed
- `B9 ?? ?? 29 03 C9 01 D0 ?? 9D ?? ?? 4C` = LDA indexed-Y + AND #$03 + CMP #$01 + BNE + STA + JMP
  → a 2-bit field dispatch (waveform? gate? voice state?) with 4 states

**Prosonix_new:**
- `B1 ??` = LDA (zp),Y → indirect-indexed read (sequence/pattern data read)
- `10 26` = BPL +$26 (branch if positive — non-sentinel byte check)
- `C9 C0 90 ?? C9 E0` = CMP #$C0 + BCC + CMP #$E0 → 3-way range dispatch: <$C0 normal, $C0–$DF mid-range, ≥$E0 end-of-sequence
  OPEN: maps onto Digitalizer's Olav_Moerkrid Pattern C (`CMP #$7F / BMI`) — different sentinel range.

**Prosonix_tiny:**
- `B1 ?? 8D 00 D4 C8 B1 ?? 8D 01 D4 C8 84 ?? 60` = LDA (zp),Y / STA $D400 / INY / LDA (zp),Y / STA $D401 / STY zp / RTS
  → a MINIMAL player: 2-byte frequency write ($D400 freq lo + $D401 freq hi) per note, then return.
  This is a stripped-down player with no envelope, no waveform, no filter — frequency pairs only.

### Structural inference

The three Prosonix variants show an evolution from complex → new → tiny. Prosonix_tiny's
direct $D400/$D401 write with no SID voice register indexing suggests a single-voice
(or pre-configured voice) player. Prosonix_new's $C0/$E0 sentinel range would be a
format-level change from Prosonix's 7-bit masking.

OPEN: Does Digitalizer's sequence format (sentinel $7F in Olav_Moerkrid Pattern C,
sentinel $FF in Wilfred's variant) derive from Prosonix's sentinel scheme ($C0/$E0 in
Prosonix_new)? All use high-byte values as command dispatchers. This is the core
format lineage question.

---

## 4. The JCH/Vibrants connection

### Who is JCH

JCH = Jens-Christian Huus, Danish scener, member of Vibrants (C64 demo group).
He is "Chordian" — operator of:
- blog.chordian.net (SID blog)
- DeepSID (https://deepsid.chordian.net) — the main online SID player
- SID Factory II (https://github.com/Chordian/sidfactory2) — open-source C64 music editor

JCH wrote the "JCH Editor" (also: "JCH's Music Editor") for Vibrants, a C64 music
composition tool. CSDb: https://csdb.dk/release/?id=14037 (JCH Editor V3.04 20G4, 1991).

### The JCH/Vibrants connection to Digitalizer/Prosonix

**Direct evidence found:** NONE. The search found no interview, forum post, or CSDb
comment establishing a technical lineage from JCH to Digitalizer. The JCH editor is
listed separately in sidid.cfg with its own signatures, and the V3.0 help file does
not mention JCH.

**The connection through DeepSID:** JCH (CSDb 2019 comment) added SteinTronic to
DeepSID. He was aware of and engaged with the Prosonix editor. But this is fan/curator
engagement, not a development lineage.

**What the comparison table shows (chordian.net/c64editors.htm):** The JCH Editor 3.04
uses 32 instruments, 31 subtunes, 114 patterns (up to 96 rows each), single-channel
patterns with bytes in vertical order lists. This is a fundamentally different format
from Digitalizer's three-mode editor (Seq/Inst/Trk) with $00–$1F instrument / $20–$3F
arpeggio command bytes.

**Working hypothesis:** The JCH/Vibrants connection mentioned in the task description
as "another acknowledged influence" is not confirmed by documentary evidence found in
this session. It may refer to a different interview or diskmag article not yet found.

OPEN: Check World News #11 (1991 interview with Olav) and Hotshot #04 (1990 interview)
for JCH mentions. Also Internal #27 (2001 interview).

---

## 5. Prosonix group context

From Demozoo (https://demozoo.org/groups/1251/, WebFetch 2026-06-13):

Members:
- Stein Pedersen (Oslo, Norway) — coder, graphician, musician; 1989–present
- Lars Hoff (Norway) — musician
- Ole Marius Pettersen (Røyken, Buskerud, Norway) — graphician, musician
- Lynx (Farsund, Agder, Norway) — ex-member, joined ~December 1989 after leaving Shadows

Prosonix produced 65 total releases (1989–2026); still active as of 2026 ("Tunnel Vision").

The group overlapped strongly with Panoramic Designs:
- Stein Pedersen is a PD member AND Prosonix member
- Lars Hoff and Ole-Marius Pettersen are both credited in Olav's V3.0 help as part of the
  "crew" for Digitalizer
- Prosonix released under joint "PD + Prosonix" banners (e.g. "Destination II", 1991)

This overlap means the "herming" (imitation) was collegial and cross-group — Olav
borrowed from a co-group-member's work with the member's eventual tacit acceptance
(the Recollection interview treats it humorously rather than as a grievance).

---

## 6. Format comparison — SteinTronic vs Digitalizer V3.0

No public SteinTronic format documentation found. The disk image `SteinTronic1.d64`
is available at CSDb (187 downloads) but has not been disassembled in any public
source found during this research. The following comparison is based on sidid
signatures only.

| Aspect | Prosonix (SteinTronic) | Digitalizer V3.0 |
|--------|------------------------|------------------|
| Sequence data pointer | ZP indirect (pattern B1 ??) | ZP $FC indirect (B1 FC) |
| Sentinel byte | $C0–$E0 range (Prosonix_new) | $7F (Olav_Moerkrid cadaver) / $FF (Wilfred) |
| SID write method | STA $D401,Y (Y-indexed) | STA $D4??,X (X-indexed) |
| Gate bit handling | AND #$03 + CMP #$01 dispatch | EOR #$01 + AND #$01 (toggle) |
| Instrument count | OPEN | 32 (00–1F byte range in seq data) |
| Arpeggio count | OPEN | 32 (20–3F byte range in seq data) |
| Sub-programs per inst | OPEN | 4 (wave, pulse, filter, arpeggio) |

ALL OPEN — needs RE of SteinTronic1.d64 to confirm.

---

## Leads to follow

1. **SteinTronic1.d64** — download from CSDb id 179618. Disassemble or run in an
   emulator to document: instruments, sequence/pattern format, effect byte encoding.
   This is the highest-value RE target for understanding the ancestor format.

2. **World News #11 (1991)** and **Hotshot #04 (1990)** — diskmag interviews with Olav.
   These predate Recollection #2 (2006) and may contain technical discussion about
   Digitalizer's development and inspiration. Check c64mags.untergrund.net.

3. **Internal #27 (2001)** — another diskmag interview with Olav. May contain more
   detail than Recollection #2 about the music editor lineage.

4. **JCH Editor format** — the JCH/Vibrants influence is not confirmed by found
   sources. Check if the Recollection #2 full text mentions JCH (the WebFetch summary
   was incomplete). The chordian.net/c64editors.htm table excludes Digitalizer and
   SteinTronic, so no comparison was possible.

5. **Geir Tjelta / Mozicart** — Olav credits "Geir/Mozicart for helpful discussions"
   in V3.0 help. Geir Tjelta is also a sidid-detected player author ("SID Duzz'It",
   "Sid Systems" variants). His format may have influenced Digitalizer's tracker model.

6. **Prosonix player variants** — `Prosonix`, `Prosonix_new`, `Prosonix_tiny` are
   three distinct sidid entries. RE of SIDs tagged `Prosonix` in HVSC would reveal
   the sequence format that Olav imitated. The HVSC path is likely
   `MUSICIANS/P/Prosonix/Pedersen_Stein/`.

7. **"Spaceship Cleopatra"** — the demo SID included in SteinTronic1.d64. Load address
   $8F00, init $8F00, play $8F09 (from CSDb SID entry 22863). RE this SID to extract
   the Prosonix player code and sequence data format.
