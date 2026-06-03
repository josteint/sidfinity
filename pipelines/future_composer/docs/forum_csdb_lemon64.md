---
source_url: multiple (see provenance log)
fetched_via: direct
fetch_date: 2026-06-03
author: various forum participants
content_date: 2004-2018
reliability: secondary
---

# CSDb / Lemon64 forum findings

## Hawkeye.sid metadata (CSDb release #28158)

Crucial — disagrees with what the existing research doc assumes:
- Composer: Jeroen Tel
- Released: 1988 by Thalamus
- **Load address: $7AE0**
- **Init address: $7AE0**
- **Play address: $7AE3 (+3, not +6)**
- Data size: 8768 bytes ($2240)
- SID model: 6581, PAL
- 12 songs (subtune count = 12, default=1)

**Hawkeye does NOT use the FC +6 offset convention.** It uses the
standard +3 offset, meaning it's likely Tel's own MoN-family driver
(not the FC editor's wrapped variant).

## Noisy_Pillars_tune_1.sid — the FC parent

- Composer: Jeroen Tel
- Released: 1987 by Scoop Designs
- Load address: **$1800**
- Init address: $1800
- **Play address: $1806 (+6)**
- Data size: 2437 bytes
- This is the *exact* player binary that Finnish Gold (Granberg, FCS)
  ripped from a TLI intro and wrapped Future Composer V1.0 around in
  June 1988.

The +6 offset is the **FC fingerprint**; Hawkeye lacks it.

## Recollection magazine — historical context

From "The Brief History of SID" article
(atlantis-prophecy.org/recollection):

> "TMC sits down and thinks, and very fast after his first music
> demo, he codes the first MON (Maniacs of Noise) player. It's a
> clone of Rob Hubbard's players."

> "Let's make it clear, most later used players are. It's no direct
> rip, but they all have the same structure. Whatever you do, if you
> try to code the most efficient way and the player will be able to
> do all effects of the SID, what you end up with is more or less the
> same as the Hubbard/MON way to do things."

> "Also, 1988... Another player cracked: Future Composer! It's
> released by Finnish Gold. It's the first TMC/MON player, but
> Finnish Gold had made an editor for it."

This confirms the **Hubbard → MoN → FC lineage** and that all three
share architectural invariants (8-byte instruments, 96-note freq
tables, command-tagged pattern bytes, per-voice parallel state).

## CSDb release #10604 (FC V1.0 by Finnish Gold)

- Released 20 June 1988 (finished 13 June, released with manual 20
  June)
- Code: Charles Deenen (player) + FCS/Granberg (editor)
- Music: Jeroen Tel + Rock
- Documentation: FCS
- "Futurecomposer Instructions.txt" — bundled with FC 4.1 release,
  **173 downloads**; haven't fetched yet (see leads).

## CSDb release #7709 (FC V3.1 by Union, 1990)

- Code credits: **Charles Deenen, FCS, Headline (Union), Softmaster**
- Music: EVS, Jeroen Tel
- 1072 downloads of the zip ("futurecomposer + acid demo.zip")
- **No technical specs on the page**; would need to inspect the
  binary directly to confirm what V3.1 added over V1/V2.
- The credits list shows the V3.1 driver had **multiple coders
  iterate on it** after Deenen's original — likely where the FC V3.x
  features (wave/pulse/filter tables) were added.

## Lemon64 forum thread t=58578 (Nov 2015) — conversion workflow

User-confirmed workflow for converting FC binaries → SID:
1. Load .PRG into a hex editor; first 2 bytes are little-endian load
   address. `00 18` → $1800; `00 10` → $1000.
2. Rename .PRG → .DAT.
3. Write a text SIDPLAY header (init/play addresses), save as .SID.
4. Open in sidplay2/w → exports PSID.

**Quoted from the thread**: *"Future Composer files typically load at
$1800. The play address is at $1806, which is +6 from init —
unusual compared to most music software that uses +3."*

This is empirical confirmation of the +6 convention from active C64
musicians, dated 2015.

> "Some Future Composer songs convert poorly depending on how blocks
> together in the tracks are assembled."

— suggests **packed/unpacked variants** behave differently (relates
to FC_V4_Packed sidid signature).

## Lemon64 forum thread t=67248 (Feb 2018) — chordian editor comparison

Chordian (SID Factory II author) on FC:
> "I don't really think antiquated editors like Future Composer or
> Sound Monitor belongs on that page."

Not technical, but confirms FC is **out-of-living-tool-knowledge**;
documentation must come from RE / disassembly, not active users.

## Lemon64 forum thread t=11700 (Feb 2004) — earliest FC mention

Just learning-strategy advice; no technical content about FC's
internals. Mentions Richard of TND and Dan Gillgrass — both active
SID musicians who might have published FC-related docs. Lead to
follow.

## Aminet FutureComposer.lha

Returned by search but is the **Amiga** Future Composer by Jochen
Hippel — a completely different format despite the same name. Do not
conflate.

## Plus/4 World "Future Composer V4.4"

A Plus/4 port of FC V4.4 exists — different platform (TED chip not
SID), but might contain a documentation file salvageable for format
specs. Lead to follow.
