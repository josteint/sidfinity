# X-Ample / Compotech — XTracker by Tufan Uysal (SoNiC)

**source_url:** https://csdb.dk/release/?id=17708
                https://csdb.dk/release/?id=82320
                https://csdb.dk/scener/?id=1312 (Thomas Detert)
                https://www.vgmpf.com/Wiki/index.php?title=Tufan_Uysal
                sidid.nfo (GitHub cadaver/sidid)
**fetched_via:** WebFetch + WebSearch
**fetch_date:** 2026-06-13
**reliability:** secondary (CSDb + sidid.nfo); VGMPF secondary

---

## Key fact: XTracker is NOT by X-Ample Architectures

Despite the name and heritage, XTracker V3.1 and V4.x were written entirely
by Tufan Uysal (SoNiC), an external composer who became the largest user of
the X-Ample player format. X-Ample Architectures (the company) had disbanded
by 1997; SoNiC released XTracker V3.1 in April 1996.

**Authorship (sidid.nfo, verbatim):**
```
(XTracker_V4.1x)
     NAME: The Ultimate X-Tracker
   AUTHOR: Tufan Uysal (SoNiC)
 RELEASED: 1996 The Art Project Studios
REFERENCE: https://csdb.dk/release/?id=82320
```

---

## The Ultimate X-Tracker V3.1 (April 1996)

**CSDb #17708** (https://csdb.dk/release/?id=17708)

- Groups: Smash Designs, The Art Project Studios
- Author: SoNiC (code, idea, concept — all roles)
- Downloads: 1,132

**User comments (verbatim, complete):**

> **Fred, October 12, 2013:**
> "The player of this editor is 100% identical to Compotech V2.1"

> **Richard, April 9, 2005:**
> "Kind of reminds me of the good old DMC player, but this one is even cooler :)"

**Technical interpretation of Fred's comment:**
- The PLAY ROUTINE binary in XTracker V3.1 matches Compotech V2.1 byte-for-byte.
- Therefore XTracker V3.1 is a new EDITOR SHELL around the existing Compotech
  V2.1 PLAYER. The data format that the player reads is identical to Compotech.
- SoNiC obtained or reverse-engineered the Compotech V2.1 player binary and
  embedded it in his new editor.

**Technical interpretation of Richard's DMC comparison:**
DMC (Digital Music Creator by Drax/Vibrants) is a well-known C64 tracker
with a similar 3-voice note/instrument model. The comparison is about FEEL
and editing workflow, not format identity. DMC and X-Ample are different
engines (separate sidid signatures). This comment suggests XTracker V3.1's
editing workflow (step sequencer, instrument editor, pattern navigation) was
similar to DMC's.

---

## The Ultimate X-Tracker V4.13 (1996)

**CSDb #82320** (https://csdb.dk/release/?id=82320)

- Groups: The Art Project Studios, Smash Designs, The Obsessed Maniacs
- Author: SoNiC (all roles)
- Downloads: 510

**Included demo tracks (9 SIDs by SoNiC):**
1. APS-Mag (mag extended)
2. Audio Wave (blue system mix)
3. Double Dragon (the dragon mix)
4. Experimental
5. Hit Dance
6. Shorty (short cut)
7. Totally Freaked Up
8. Tufan Uysal's Mahogany Dub
9. Twingo (red colour mix)

**User comments:** None on the CSDb page.

**Version progression:**
- V3.1 (April 1996, CSDb #17708) — player = Compotech V2.1 (confirmed)
- V4.00 Beta (1996) — Thomas Detert credited for music; player changed
  (sidid fingerprint shifts to XTracker_V4.1x pattern)
- V4.13 (1996, CSDb #82320) — V4.1x player confirmed by sidid

The V3.1→V4.00 transition is when SoNiC rewrote the player (changing from
the Compotech bitmask-loop to the unrolled 3-call dispatch). The data
format MAY have changed in this transition.

---

## Tufan Uysal (SoNiC) biography

**Handles:** SoNiC, UnPro 7
**Real name:** Tufan Uysal
**Groups:** Smash Designs, The Art Project Studios, The Obsessed Maniacs
**Active:** ~1994-2002+ (HVSC credits through 2001 game work)

From HVSC db: 123 X-Ample SIDs + 1 (XTracker_V4.2x) = 124 total X-Ample
format SIDs, making SoNiC the single largest X-Ample corpus author.

**Notable compositions:**
- Turrican 3 (24 subtunes, 42,565 bytes — largest X-Ample SID in HVSC)
- Katakis 3D (2001, multiple parts)
- In_Da_Mix, Situations, Concussion_in_the_brain — CIA-timed tunes
- Falk-Ohr-Filter_Model_50 — the only (XTracker_V4.2x)-tagged tune in HVSC

**Non-X-Ample work:**
3 SIDs in AMP engine, 2 in DMC, 2 in GoatTracker V2.x, 1 each in
Hermit/SidWizard_V1.x, JCH_NewPlayer, Music_Assembler, MoN/FutureComposer
(×8), Neil_Crossley, Sonic_Graffiti (×12), Soundmonitor (×4), System6581 (×3).
SoNiC was prolific across multiple trackers.

---

## XTracker vs Compotech — structural differences inferred

From sidid.cfg fingerprint analysis (see sidid_variant_taxonomy.md):

| Feature | Compotech_V2.x | XTracker_V4.1x |
|---|---|---|
| Voice dispatch | Bitmask loop (LSR/BCC) | Unrolled (3× A2 xx / JSR) |
| Voice loop back | CMP #$15 / BCC | None (3 explicit calls) |
| Master vol write | ORA + STA $D418 | ORA + STA $D418 (same) |
| Filter write | STA $D416 | STA $D416 (same) |
| Frame counter | DEC / BPL / reload | DEC / BPL / reload (same) |

The dispatch change (bitmask loop → unrolled) affects performance and code
size but NOT the data format the player reads. The frame counter, voice
stride (ADC #7), and SID register write pattern are identical.

**Assessment:** XTracker V4.1x almost certainly reads the same data format
as Compotech V2.1. The player routine was rewritten for efficiency; the
data tables (notes, instruments, sequences, orderlists) were preserved.

---

## XTracker V4.2x — the rarest variant

**HVSC corpus:** 1 tune only:
- `MUSICIANS/S/Sonic/Falk-Ohr-Filter_Model_50.sid` by Tufan Uysal (SoNiC)
- init=$8000, play=$8003

From sidid fingerprint: adds `A0 00 / F0 01 / 60` entry trick, restores
bitmask loop (from V4.1x's unrolled approach), flips bitmask polarity
(BCS instead of BCC), and includes a hardcoded `9D 04 D4 / STA $D404,X`
gate write identical to the `(Sonic/SDS)` pattern.

This suggests V4.2x was a brief experimental revision, possibly a private
build by SoNiC. The single HVSC instance and the "Falk-Ohr-Filter (Model 50)"
name (a filter effect test) suggest it was an R&D tune.

---

## The "DMC player" comparison context

Richard's 2005 comment ("Kind of reminds me of the good old DMC player")
warrants documentation. DMC was developed by Drax (Thomas Mogensen) of
Vibrants, a Danish demo group. DMC uses:
- 3 voices with separate sequence/orderlist per voice
- Pattern-based composition with note + instrument + effect columns
- A compact player with bitmask-gated voice updates

This workflow resemblance to X-Ample/XTracker suggests that the X-Ample
data format follows a similar TRACKER pattern:
- Per-voice sequence/orderlist (pattern list)
- Pattern data: note + instrument + effect per row
- Instrument programs with ADSR + waveform sequences

**This is unconfirmed** — no public documentation of the X-Ample data format
exists — but the DMC comparison and the sidid dispatch loop analysis both
point toward a standard 3-voice tracker model.
