---
source_url: https://csdb.dk/release/?id={10604,10605,10607,7709,196273,11644,134469,47498,30048}
fetched_via: direct CSDb fetch 2026-06-03
fetch_date: 2026-06-03
author: various (FCS, Beastie Boys, Mnemonic Designs, Union, Dynamix, Warlords TMB)
content_date: 1988-1992 release notes; CSDb metadata current as of fetch
reliability: secondary (CSDb release entries — scene-curated, generally reliable)
---

# Future Composer C64 — full release timeline (CSDb)

Authoritative version-by-version credits for the C64 Future Composer
lineage, gathered from CSDb release entries. Use this to identify
which driver/format Hawkeye.sid (Jeroen Tel, 1988 Thalamus) is most
likely built against.

## V1.0 — Finnish Gold, 20 June 1988

**Title:** "FCS's Future Composer no: 00.18 v1.0"

**Code credits:**
- Charles Deenen (Maniacs of Noise, Scoop)
- Finland Cracking Service (Finnish Gold) — i.e. **Juha Granberg / FCS**

**Music:** Jeroen Tel (MoN), Rock (Finnish Gold)

**Idea:** Gallstone (Finnish Gold), Rock (Finnish Gold)

**Documentation:** Finland Cracking Service (Finnish Gold)

**Notes:**
- Finished 13 June 1988; officially released 20 June 1988 *with*
  instructions.
- "Although Future Composer V1.0 was finished on 13th of June 1988,
  FIG didn't officially release it until 20th of June 1988 together
  with the instructions." — CSDb user comment.
- The "Code: Charles Deenen" credit is the **smoking gun** — V1's
  player IS the MoN driver, contributed by Deenen directly. FCS built
  the editor frontend around it.
- Hawkeye is dated 1988 but the precise month is unclear; if Hawkeye
  was scored before Future Composer's June 1988 release, **Tel was
  using the MoN-Deenen driver directly (Cybernoid 2 family), and
  Hawkeye is NOT a "Future Composer" tune in the editor sense, but
  shares the same driver lineage**.

## V2.0 — Beastie Boys (and Mayhem release), 25 September 1988

**Code:** Axiom of Beastie Boys

**Import (distribution):** Stormbringer of Mayhem

**Notes:** Bug-fixes + editor improvements. Driver still MoN-derived.

## V2.1 — Beastie Boys, 1988 (CSDb id=134469)

Minor update. V2.1++ later released by Quartet (1988, id=30048) with
further enhancements.

## V3.0 — Mnemonic Designs, August 1989

**Code:** ADT, SMC (Pretzel Logic)

**Notes:** First V3 release. **Driver enhanced** — V3 is when wave/pulse/filter
tables get their richer command-based language. Mnemonic Designs is NOT
MoN-affiliated; they reverse-engineered V2 and improved it.

## V3.1 — Union, 1990

**Code credits:**
- Charles Deenen (MoN) — **driver code, re-credited**
- Finland Cracking Service (Finnish Gold) — FCS
- Headline (Union)
- Softmaster (Audial Arts, Hitmen, Ruthless, Union)

**Music:** EVS (20th Century Composers), Jeroen Tel (MoN)

**Graphics:** Headline (Union)

**Included SIDs:** "No Mercy" by van Santen Edwin, "Sample" by Jeroen Tel

**Notes:** This is the **most-distributed V3.x**. The Deenen/FCS
re-credit suggests Union folded V3.0's improvements back into the
canonical MoN-Deenen driver line.

## V4.0 — Dynamix, 1989 (CSDb id≈Demozoo 188668)

**Code:** "The Syndicate of Coococ Magazine Staff, Dynamix"

**Notes:** Sequence editor added. **Packed song format** introduced
(sidid `FC_V4_Packed` signature catches it). Filter/drum editors split out.

## V4.1+ 100% — Dynamix (with The Beat Machine), 22 March 1990

**Code:** "The Syndicate of Coococ Magazine Staff, Dynamix"

**Music:** Chris (Art of Sonix, Beat Machine, Dynamix), Jeroen Tel (MoN), Rock (Finnish Gold)

**Included SIDs (in editor package):**
- D.Y.S.P.I.D.C.E. (part 2)
- Forever Together (remix)
- Future Composer 1 (tune 3)
- Noisy Pillars (tune 1)
- Scout

**Notes:** This is **the canonical V4** — the funet `fc4.0.prg` file
(which we have at `/tmp/fc_research/fc4.0.prg`, 41 407 bytes) is this
package. Embedded instructions text inside the binary (extracted via
`strings`) confirms: "FUTURE COMPOSER V4.0 SEQUENCE EDITOR",
"FUTURE COMPOSER V4.0 FILTER EDITOR".

## V5.0 — Warlords TMB Group, 1992

**Music:** Chris (Art of Sonix, Beat Machine), HTD (Topaz Beerline)

**Text:** Warrior (Warlords TMB Group)

**User comment from CSDb:** *"Can't see much change from 4.1 version.
Still holds all the bugs and bad saving."*

**Notes:** Cosmetic. Driver unchanged from V4.

## Conclusion for Hawkeye (Jeroen Tel, 1988, Thalamus)

The CSDb sid entry (id=28158) shows:
- Composer: Jeroen Tel
- Year: 1988
- Load: $7AE0, Init: $7AE0, Play: $7AE3
- Data size: 8 768 bytes ($2240)
- 12 subtunes, default 1

The **+3 spacing** (init=$7AE0, play=$7AE3) implies a **2-vector
init/play, not the +6 3-vector** seen in the Cybernoid 2 source. That
means Hawkeye's PSID header writer simplified the entry table to just
init + play (or init/songout-stub + play). The body is still the
MoN-Deenen V3-ancestor driver — Hawkeye predates FC V3's release (Aug
1989) by ~12 months, so it's the **bare MoN-Deenen driver, V3-shape
dispatcher**, that FC V3 was modelled on later.

This means the order is:
1. **MoN-Deenen V01-07-1988 driver** (used for Cybernoid 2)
2. **Hawkeye** = same driver, 12-tune edition, used by Tel in 1988
3. **FC V3 dispatcher** = formalised version of the same driver
   (Mnemonic Designs RE'd it from MoN tunes ~1989)

## Demozoo: full FC-C64 tag list (productions)

- *Future Composer V1.0* (Jun 1988) – Finnish Gold
- *Future-Composer V2.0* (1988) – Beastie Boys
- *Future Composer V3.1* (1990) – Union
- *Future-Composer V4.0* (1989) – Dynamix
- *Future-Composer V4.1+ 100%* (Mar 1990) – Dynamix + The Beat Machine
- *Relocater for Future Composer* (no date) – Unic
- *Future Composer Re-Locator v1.3+* (1989) — Raze [Internet Archive]

Music tracks tagged FC-C64:
- *Disco Rap* (1988) – Thargon / EGA CS ^ The Dark Science
- *Enola Gay* (1988) – Markus Schneider / Level 99
- *I'll Have to Say Goodbye* (1991) – Harold Klink
- *Ten Years of No FC!* (Jun 2009) – Conrad
- *Valmis* (Oct 2014) – Apollyon / Contex
- *Biggles Remix* (Apr 2015) – Rock / Finnish Gold
- *When Tapes Talk* (Aug 2023) – FΛDE / Onslaught

The 2015 "Biggles Remix" by **Rock / Finnish Gold** is particularly
interesting — Rock was an FC1 co-author, so a 2015 FC-format tune by
the original co-author could be a useful **modern, fully-documented**
test case for the format.
