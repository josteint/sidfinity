---
source_url: multiple (see per-entry provenance)
fetched_via: WebFetch / WebSearch
fetch_date: 2026-06-15
author: various
content_date: 2026-06-15
reliability: secondary (summarized from web fetches)
---

# External Sources — Vibrants/Laxity / JCH NewPlayer Research

## 1. JCH Computer Timeline (primary lineage source)

**URL:** https://blog.chordian.net/computer-timeline/
**Reliability:** Primary (JCH's own account)

Key facts extracted:
- Jun 1988: JCH reverse-engineered Laxity's C64 music player, started composing with it
- Jul 1987: First NewPlayer code (pre-editor)
- Nov 1988: Editor V1 (no sequences)
- Dec 1988: Editor V2 (sequences introduced)
- Apr 1989: NewPlayer V5.02, V6.01 (with music editor)
- May 1990: NewPlayer V14.G0, V15.G0
- Jul 1990: NewPlayer V12.G3, V15.G6
- Oct 1990: NewPlayer V17.G1
- Jan 1991: NewPlayer V17.Q? (quick player)
- Feb 1991: NewPlayer V18.G0
- Mar 1991: NewPlayer V19.G1
- May 1991: NewPlayer V20.G4 ("my last standard player on C64")
- Aug 1989: JCH and Link established "Vibrants"
- Sep 1990: Laxity joined Vibrants
- Aug 1991: Final editor ED3.04/D15/20.G4

## 2. CSDb: Vibrants/Laxity editor release

**URL:** https://csdb.dk/release/?id=122333
**Reliability:** Primary (CSDb is the authoritative C64 scene database)

- Released 1990 by Laxity
- 5 demo tunes included: DXYCP Scroll, Fast Stuff 1, In the Mood Mix, Lethal C., Spacemilk
- Credited to Laxity (Maniacs of Noise, Starion, The Flexible Arts, Vibrants) + Scortia
- Available in T64 and D64 format via CSDb downloads

## 3. CSDb: SidFactory/Laxity (2006)

**URL:** https://csdb.dk/release/?id=39519
**Reliability:** Primary

SID Factory 0.5 Alpha 1 (Sep 2, 2006):
- Dynamic multispeed switching
- Tempo table
- Portamento (Driver 5.02, Sep 9, 2006)
- Parallel instrument + slide
- Pointer configuration to various tables from voices
- Pattern editing 8 steps at a time
- Driver versions: 5.02 (portamento), 6.03 (bug fix)

## 4. CSDb: Laxity_NewPlayer_V21 (2006)

**URL:** https://csdb.dk/release/?id=26563
**Reliability:** Primary

NP21.g4 final (Jan 16, 2006, Maniacs of Noise + Vibrants):
- Authored by Laxity
- Includes 3 demo tunes
- Companion to JCH Editor V3.04 20G4

## 5. CSDb: SidFactory_II/Laxity (2020)

**URL:** https://csdb.dk/release/?id=210571
**Reliability:** Primary

SID Factory II build 20200716:
- JCH + Laxity (Bonzai, Maniacs of Noise, Vibrants)
- 17 SID files, driver tests (drivers 11–16)
- Ongoing development at https://github.com/Chordian/sidfactory2

## 6. GitHub: Chordian/sidfactory2

**URL:** https://github.com/Chordian/sidfactory2
**Reliability:** Primary (source code)

Key facts:
- Primary dev: Thomas Egeskov Petersen (Laxity)
- Contributors: JCH, Michel de Bree, Thomas Jansson
- Uses reSID emulator (resid-fp)
- Interface: JCH's "contiguous sequence stacking system" + Protracker note input
- Import: Goattracker, CheeseCutter, 4-channel MOD
- Latest driver: 11.05 (build 20260314)
- Driver changelog: 11.02 (pulse index/tempo/main vol commands), 11.03 (filter enable flag),
  11.04 (note delay), 11.05 (pulse reset flag)
- Built-in packer with ZP address relocation
- ASID protocol for real hardware (TherapSID, USBSID-Pico)

## 7. SF2 User Manual (2020 build)

**URL:** http://files.chordian.net/sf2/SIDFactoryII_20200604_User_Manual.pdf
**Latest URL:** https://files.chordian.net/sf2/SIDFactoryII_20260314_User_Manual.pdf
**Reliability:** Primary (official documentation)

Note: WebFetch returned the PDF but could not extract technical format specs from it
(the AI model reading it reported Danish-language introductory content). The manual
is confirmed to exist and covers driver documentation.

## 8. SF2 tutorial series

**URL:** https://blog.chordian.net/2022/08/27/composing-in-sid-factory-ii-part-2-sequences/
**Reliability:** Primary (author's tutorials)

Sequence format confirmed:
- Order list: 2-byte words = [transpose_byte][sequence_number]
- Transpose byte: range $80–$BF; $A0 = no transpose
- Sequence number: 0–127 (128 max sequences)
- Sequence rows: up to 1000+ via real-time packing
- Each row: note column (letter notation), instrument column (0–255)

## 9. cadaver/sidid repository

**URL:** https://github.com/cadaver/sidid
**nfo URL:** https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo
**Reliability:** Primary

Key facts from nfo:
- Vibrants/Laxity → Thomas Egeskov Petersen (Laxity), CSDb #122333
- SidFactory/Laxity → Thomas Egeskov Petersen (Laxity), CSDb #39519, released 2006
- SidFactory_II/Laxity → Thomas Egeskov Petersen (Laxity), CSDb #210571, released 2020
- Laxity_NewPlayer_V21 → Thomas Egeskov Petersen (Laxity), CSDb #26563, released 2006
- JCH_NewPlayer → Jens-Christian Huus (JCH), CSDb #14037
- Vibrants/JO → Poul-Jesper Olsen (JO) [no CSDb ref in nfo]
- Dane_NewPlayer → Stellan Andersson (Dane), CSDb #100406, released 2011

## 10. JCH-Editor 3.1 + NP22-25 (CSDb #100406)

**URL:** https://csdb.dk/release/?id=100406
**Reliability:** Primary

Key facts:
- Released Jun 6, 2011 by Dane of Booze Design
- Includes: wave/pulse/filter tables, tracks/sequences vertical layout
- Documentation: "NP22-25 docs.doc" (2173 downloads), disk image "JCH 3.1+NP22-25.d64"
- References "Frantic's docs to the JCH-system" as excellent newcomer guide
- Requires JCH-packer for operation

## Unresolved sources (URLs found but not yet fetched)

- CSDb JCH Editor V3.04 20G4 (#14037): https://csdb.dk/release/?id=14037
  → The primary JCH editor release; may have format docs in the download
- CSDb JCH Music-Editor V2.53 (#10754): https://csdb.dk/release/?id=10754
  → Earliest well-known version with docs; mentioned in Lemon64 thread
- CSDb forum "From jch newplayer file to SID" (#5698): conversion procedure
  → Standard init=$1000, play=$1003; JCH-packer; MusicMixerV6 alternative
- CSDb forum "JCH editor guide" (#29168): references "Frantic's PDF guide"
  → Frantic's guide = "an excellent guide to newcomers or musicians"
  → "A Beginner's Guide to the JCH Editor V2.53, NewPlayer V14.G0" mentioned
- DisC=overy issue #1: beginner's guide by Sean M. Pappalardo
- Demozoo jch-player tag: https://demozoo.org/productions/tagged/jch-player/
  → 16–17 productions listed; no version details exposed
