---
source_url: https://sidpreservation.6581.org/sid-trackers/
fetched_via: direct
fetch_date: 2026-06-15
author: sidpreservation.6581.org (community wiki)
content_date: unknown
reliability: secondary
---

# SID Preservation — Vibrants/Laxity Entry

## Key findings from the SID Preservation tracker catalogue

The page documents the "Laxity Editor V/32-3.34" as the canonical tool for the
`Vibrants/Laxity` HVSC engine family.

**Critical documentation note:**
> "Laxity himself did never write a full documentation, as it was never intended to go public."
> "The editor is very hard to get anything out of, unless you know how to work it out."

The editor is noted as "the biggest breakthrough" in SID music composition of its era — it
"really show what the SID chip was made of and it just didn't sound half done, it sounded brilliant!"

**Legacy:**
Laxity's work inspired JCH to develop his own editor (the JCH Editor / NewPlayer) after
Laxity suggested JCH stop using Laxity's editor due to JCH's musical prowess.

## Version identification

The CSDb lists two 1990 releases:
- `Laxity Editor v/32-3.34` (CSDb #122333)
- `Laxity Editor v/34-3.35` (same period)

Precursor: `TFA Editor V3.24` (CSDb #215790, 1989) — described as:
> "TFA Editor #3.24 is the precursor to Laxity Editor v/32-3.34, Laxity Editor v/33-3.35
> and Laxity Editor v/34-3.35"

The TFA Editor was released under "The Flexible Arts" (Laxity's earlier group before Vibrants).

## Documentation state

No public documentation exists for the Laxity Editor / Vibrants/Laxity player format.
The format must be reverse-engineered from:
1. The SIDId signatures (5 OR-lines — see `cluster_sidid_discrimination.md` in
   `pipelines/laxity_newplayer/docs/`)
2. HVSC binary SIDs tagged as `Vibrants/Laxity` (179 SIDs)
3. The D00/EdLib format (JCH's AdLib tracker) which shares lineage with the C64 Laxity
   editor — JCH explicitly states EdLib "used the same track editing system as my
   Commodore 64 editor"

## What the SIDId signatures reveal

From `pipelines/laxity_newplayer/docs/cluster_sidid_discrimination.md` (verbatim):

```
; LINE 1 — 16-bit freq write via table (ADC + TAY + STA $D401 + STA $D400)
18 7D ?? ?? 0A A8 B9 ?? ?? 48 B9 ?? ?? AC ?? ?? 99 01 D4 68 99 00 D4

; LINE 2 — voice ctrl write + sequence advance
FE ?? ?? BD ?? ?? 99 04 D4 4C ?? ?? BD ?? ?? 29 ?? F0 ?? A9 ?? 99 04 D4

; LINE 3 — timer/speed init (CE loop × 4 counters, then AD/8D)
A9 ?? 8D ?? ?? 60 A2 ?? CE ?? ?? 10 ?? CE ?? ?? CE ?? ?? CE ?? ?? AD ?? ?? 8D

; LINE 4 — command dispatch with nibble extraction
C9 ?? B0 ?? 29 ?? 48 A9 ?? 9D ?? ?? 68 0A 0A 9D ?? ?? 4C ?? ?? 29

; LINE 5 — filter write via add ($D416)
AD ?? ?? 18 79 ?? ?? 8D ?? ?? 8D 16 D4 2C ?? ?? 70 ?? D9 ?? ?? 90
```

Key architectural inferences from these signatures:

1. **16-bit frequency model (LINE 1):** `ADC abs,X; ASL; TAY; LDA tbl,Y; PHA; LDA tbl,Y;
   LDY abs; STA $D401; PLA; STA $D400` — a 16-bit frequency table lookup using a stack-separated
   hi/lo write that writes $D401 BEFORE $D400 (reversed from $D400-first models). The `ASL` after
   ADC suggests a 2-byte-per-note freq table (each note = 2 bytes, lo + hi).

2. **Voice control write (LINE 2):** `INC abs,X; LDA abs,X; STA $D404,Y; ...` — gate/ctrl
   register written via Y-indexed absolute addressing. The `29 ?? F0 ?? A9 ??` is a compare-
   and-branch with immediate load — suggests the waveform/gate byte is constructed from a
   table value (AND-masked, then possibly OR'd with immediate).

3. **Timer/speed (LINE 3):** Four `DEC abs; BPL` counters (one per CE-10 pair). Speed
   mechanism uses multiple decrementing counters with BPL branch-back — a multi-counter tempo
   system rather than a single speedcnt.

4. **Command dispatch (LINE 4):** `CMP #?; BCS; AND #?; PHA; LDA #?; STA abs,X; PLA; ASL;
   ASL; STA abs,X; JMP; AND` — nibble extraction via PHA/PLA + ASL×2 (left shift × 2 = ×4).
   This is a command byte split: hi nibble → one table, lo nibble×4 → another. The `BCS` on
   compare suggests command range splitting (< threshold = one type, ≥ = another).

5. **Filter ($D416) (LINE 5):** `LDA abs; ADC abs,Y; STA abs; STA $D416; BIT abs; BVS;
   CMP abs,Y; BCC` — filter cutoff is an accumulating register (ADC-based sweep), stored
   to $D416 every frame. The `BIT; BVS` after the store suggests an overflow/boundary check
   on the filter value. Note: this writes $D416 (filter cutoff HI), NOT $D417 or $D418.

## Play offset

Canonical: init=$1000, play=$1006 (note +$06, different from JCH_NewPlayer/NP21 which use +$03).
This implies a 6-byte dispatch table: {init_jmp, play_jmp, mplay_jmp} as 3×2-byte entries.

HVSC corpus (179 SIDs): 81% at the canonical +$06 offset. Much more multi-subtune variation
than NP21 (10 multi-subtune entries vs NP21's 6).
