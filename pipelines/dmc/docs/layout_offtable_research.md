---
source_url: (multiple — see per-section citations)
fetched_via: local file read + web search + WebFetch
fetch_date: 2026-06-20
author: Claude (sidfinity leaf research agent)
content_date: 1993-2026
reliability: Q1 = ANSWERED by our own annotated disassembly (primary, high confidence); Q2 = ANSWERED by disassembly + project RE notes (primary, confirmed by running code). External web/doc sources found NO additional detail beyond what local docs already contain.
---

# DMC V5 packed-module layout + off-table freq lookup — research findings

## Q1 — What is stored IMMEDIATELY AFTER the 96-entry freq table?

### Answer: WORK RAM / PER-VOICE STATE — not a second music table

**Sources consulted (in priority order):**

1. `/home/jtr/sidfinity/pipelines/dmc/v5/disassembly.s` — annotated disassembly of
   Katusha.sid (family-3/5, the dominant DMC V5 player; 1495 SIDs). Hand-annotated
   variable map + code with every address.  **PRIMARY.**
2. `/home/jtr/sidfinity/pipelines/dmc/v5/RE_NOTES.md` — RE session notes with
   address tables and data-layout findings. **PRIMARY.**
3. `/home/jtr/sidfinity/pipelines/dmc/docs/dmc_v5_docs_original.txt` — The Syndrom's
   first-party V5.0 instruction text (1993-94). Editor-level, no memory-map detail.
4. `/home/jtr/sidfinity/pipelines/dmc/docs/tnd_dmc_tutorial.txt` — Richard Bayliss/TND
   tutorial §3. User-level, no memory-map detail.
5. Web: HVMEC page, CSDb releases #2594 / #22938 / #36658, Lemon64, Pouet — **none
   contain any byte-level format documentation.** External sources are silent on this
   question.

### Evidence

From `disassembly.s` header (lines 63-70):

```
;   $170F  freq table LO (96 notes)        $176F  freq table HI (96 notes)
;   $1878  track-pointer record: 3x(lo,hi) orderlist ptrs, then speed, $101B
;   $196E  sector pointer table LO         $1972  sector pointer table HI
;   $1976  INSTRUMENT table (8 bytes each, ids $00-$1F)
;   $199E  wave-table CTRL array           $19AB  wave-table FREQ/offset array
;   $19B8  pulse-table ADD-LO / arg array  $19BF  pulse-table ADD-HI / arg array
;   $19C6  filter-table arg-LO array       $19C7  filter-table arg-HI array
;   (the 2-byte tables are addressed by ENTRY index; one entry per frame.)
```

`freqlo` = $170F (96 bytes) → ends at $176E.
`freqhi` = $176F (96 bytes) → ends at $17CE.

What follows immediately at $17CF is the **per-voice work RAM state block**:

```
;   $17CF,x/$17D2,x  track pointer lo/hi (orderlist);  $17D5,x track position
;   $17D8,x  sector position (byte index within current sector)
;   $17DB,x  duration counter (ticks; reload from $17DE,x);  $17DE,x dur reload
;   $17E1,x  current instrument (SND);  $17E4,x transpose (signed, TR+/TR-)
;   $17E7,x  VOL override (sustain; 0=instrument's own SR)
;   $17EA,x  gate-off flag (GATE cmd; note plays w/o retrigger)
;   $17ED,x  glide/slide speed (0=off);  $17F0,x glide/slide target note
;   $17F3,x  wave-table position;  $17F6,x pulse-table position
;   $17F9    filter-table position (GLOBAL — V3 only)
;   $17FC,x  vibrato delay counter;  $17FF,x vibrato speed (period)
```

Then at $1802-$1843: more per-voice scratch state (vib step, note counters, freq
accumulators, pulse accumulators, filter counters, flags).

Then at $1878: the **track-pointer record** (packer-placed music data — 3×2 orderlist
addresses + speed + $101B master-vol init).

### Interpretation

The byte region $17CF-$1877 (104 bytes) is **CPU work RAM that overlaps the packed
data section** — it is the per-voice runtime state block, initialised by `init_clear`
($1040-$107F) from the orderlist record at $1878, then live-updated during play.

This region is NOT a second frequency table, NOT a tuning table, NOT a pointer table —
it is the engine's per-voice registers: track pointers, sector position, duration
counters, transpose, instrument #, wave/pulse/filter table positions, vibrato state,
etc. The packer places it WITHIN the packer-output data region so it survives
relocation (the whole $1006-$1845 block is code+state, per the factory relocation
notes in RE_NOTES.md).

**There is no second music-data table between the 96-entry freqhi and the orderlist
record. The gap is all work-RAM.**

### Katusha layout (per RE_NOTES.md data table at lines 32-41)

| Table | Katusha address | Read site(s) in code |
|-------|-----------------|----------------------|
| freq lo/hi | $170F / $176F | $13A5/$13AB, $168C/$1692, $153B/$1541 |
| orderlist (init copies to $17CF/$17D2) | $1878 | $1046-$1057 |
| sector ptr lo/hi | $196E / $1972 | $114E / $1153 |
| instrument table | $1976 | $129D (8-byte × instrument-id) |
| wave ctrl/freq | $199E / $19AB | $1385/$165E, $19AB alongside |
| pulse lo/hi | $19B8 / $19BF | $13C0/$13C3, etc. |
| filter lo/hi | $19C6 / $19C7 | $13EF/$13F5, etc. |

Note: these addresses are Katusha-specific; the packer patches all data-table
addresses into the player's operands per-song. The layout ORDER (freq→state→orderlist
rec→sector ptrs→instr→wave→pulse→filter) appears consistent but the absolute
addresses vary by module.

---

## Q2 — Off-table wave lookup: what happens when (wave_freq + note) > 95?

### Answer: CONFIRMED BUG/FEATURE — reads past the 96-entry freq table into whatever bytes follow

**Sources consulted:**

1. `disassembly.s` lines 620-640 (wave_init melodic path). **PRIMARY.**
2. `RE_NOTES.md` §"PARTIAL LONG TAIL round 11 — off-table FREQ lookup" (lines 621-645).
3. `pipelines/dmc/v5/extract/engine_model.py` function `_freq_overrun` (lines 261-298).
4. External docs / web — **SILENT**: no external source (V5.0 docs, TND tutorial, CSDB
   comments, Lemon64, HVMEC) mentions this behaviour at all.

### Evidence from the disassembly

The melodic wave path in `wave_init` ($139D-$13AE):

```asm
L_139D:
    $139D: B9 AB 19   LDA $19ab,y   ; wave_freq[wavepos] (arp semitone offset)
    $13A0: 18         CLC           
    $13A1: 7D 0F 10   ADC $100f,x   ; + curnote (current note#, unsigned)
    $13A4: A8         TAY           ; Y = (wave_freq + note) & $FF  (8-bit, NO bounds check)
    $13A5: B9 0F 17   LDA $170f,y   ; freqlo[Y]  ← Y can be > 95
    $13A8: 9D 0E 18   STA $180e,x   ; → freq-lo work reg
    $13AB: B9 6F 17   LDA $176f,y   ; freqhi[Y]  ← Y can be > 95
    $13AE: 9D 11 18   STA $1811,x   ; → freq-hi work reg
```

There is **NO bounds check on Y**. The ADC is 8-bit (no CLC carry overflow check — the
& $FF wrapping is implicit in the 6502's single-byte Y register). If `(wave_freq[step]
+ curnote) > 95`, Y indexes past the 96-entry `freqlo` / `freqhi` arrays into whatever
bytes follow in the packed image — which is the per-voice **work RAM state block**
described in Q1.

The same pattern occurs in `wave_step` at $168C/$1692.

### Musical / structural interpretation

From RE_NOTES.md (session findings on round 11, confirmed by running verification):

> "the melodic wave path computes `(wave_freq[step] + curnote) & $FF` and reads
> freqlo/freqhi there; index 64+60=124 falls past the 96-entry tables. orig's
> off-table byte is real content (freq_hi[124]=0); we emitted only 96 entries, so
> the read hit garbage."

So the off-table read is **NOT a deliberate design feature** — it is an **unchecked
8-bit add** whose result falls into whatever the packer placed after the freq table
(the work-RAM block). The bytes there happen to have concrete values (mostly small
integers from per-voice state), and the engine reads them as freq-hi bytes.

**Concrete example (Elysium, confirmed):**
- Instrument 8/9 has `wave_freq[step] = 64` (a $40 melodic arp offset).
- Playing note 60 → Y = (64 + 60) & $FF = 124.
- `freqhi[124]` = byte at $176F + 124 = $17EB. In Katusha's layout that is
  `$17EA,x` = the gate-off flag — happens to be 0.
- Result: freq-hi = 0 = a very low frequency. This is the actual audible output
  from that arp step.

The content is therefore **content-by-reference**: the original HVSC tune's
off-table bytes are part of the musical output even though the composer (Brian) almost
certainly never intended them as "extra frequency table entries". The 96-entry limit
was just the standard PAL table (8 octaves × 12 notes), and the arp add was left
unchecked.

**Documented arpeggio offsets from first-party docs (minor chord example):**

From `dmc_v5_docs_original.txt`:
```
00 21-00
01 21-03
02 21-07
03 90-00   (loop)
```

The arp byte is `00, 03, 07` — small positive semitone offsets. These are safe for
typical note ranges (note 0-88 + offset 0-7 stays well within 96). But NOTHING in the
docs says the offset must be small, or that there is any clamp. Larger offsets (e.g.
$40 = 64) were used by some composers, producing the off-table read as a side effect.

**There is no documented notion of:**
- The freq table being longer than 96 entries
- Signed offsets
- A "deliberate read past the table" design
- Any extension or alias region

The off-table bytes are an accidental read of whatever the packer placed there; their
values are musically significant only because those specific SIDs were authored with
wave_freq offsets that produce indices > 95, and the HVSC binary's off-table bytes
happen to be part of the authentic sound.

### Fix in this codebase

`_freq_overrun` in `engine_model.py` captures the reachable off-table freq-hi bytes
(indices 96 to max reachable = max over all melodic wave values × all notes ×
transposes), stored in `V5Model.freq_overrun`. The composer emits this window
contiguously after `freqhi` so off-table indices resolve to the same bytes as in the
original. This recovered **+44 FULL** members (RE_NOTES.md round 11).

---

## Relevant quotes about freq table, arp offsets, drum/test-bit mode

**From `dmc_v5_docs_original.txt` (The Syndrom, 1993-94):**

> "WV IS THE POINTER TO THE ARPEGGIO-TABLE. MORE ABOUT IT LATER..."
>
> "IN THE VERY LEFT ROW THE POSITIONS ARE DISPLAYED, THE LEFT ROW OF THE REAL TABLE
> IS RESERVED FOR THE WAVEFORMS ... BIT 3 ? WELL, THIS IS THE TESTBIT, AND NOT NEEDED
> NORMALLY. BUT CLEVER AS BRIAN IS, HE USED THIS BIT FOR THE DRUM-MODE (OR
> HIFREQ-MODE (HI JENS!)), REMEMBER, IN THIS MODE, ALL THE NOTE-VALUES WILL BE PUT
> DIRECTLY INTO $D401 (OR $D408 OR $D40F), WHICH IS THE HIBYTE OF THE FREQUENCY, SO
> THAT THE SOUND ALWAYS IS THE SAME, EQUAL WHICH NOTE YOU PLAY IT WITH..."
>
> "FOR A NORMAL MINOR-CHORD, USE LIKE THIS:
>   00 21-00
>   01 21-03
>   02 21-07
>   03 90-00   RIGHT !?!"
>
> "VALUES ABOVE $87 ARE CRAP!" (referring to waveform control byte — NOT the arp offset)

The original docs say NOTHING about:
- The freq table having 96 entries or any count limit
- What happens if the arp offset + note exceeds the table bound
- Off-table reads or any notion of wrapping

**From `disassembly.s` header:**

```
;   $170F  freq table LO (96 notes)        $176F  freq table HI (96 notes)
;   WAVE  ($199E ctrl, $19AB freq): ctrl byte -> $D404 (AND gate mask).
;     bit3 ($08) test bit = DRUM/hi-freq mode: the FREQ byte goes straight
;     to freq-hi ($D401), freq-lo=0. Else MELODIC: FREQ byte = signed
;     semitone arp offset added to the note -> freq-table lookup.
;     ctrl == $90 -> loop: next FREQ byte = absolute entry to jump to.
```

Note: the disassembly header says "signed semitone arp offset" — but the code itself
does an unsigned `ADC` (CLC + ADC = unsigned addition; no sign-extension). Large
positive values such as $40=64 simply produce a large Y, running off-table. The word
"signed" was an earlier annotation assumption; the actual hardware behaviour for large
offsets is the unchecked overrun described above.

---

## Leads to follow

1. **Confirm Q1 with a second representative SID** — pick a family-3 member whose
   packed layout differs (different instrument count, etc.) and trace the data table
   addresses to verify the order is always: freqlo→freqhi→(state block)→orderlist rec
   →sector ptrs→instr→wave→pulse→filter.

2. **Confirm whether wave_freq byte is truly unsigned or sign-extended.** The ADC at
   $13A1 is unsigned. But if wave_freq can hold $FF = 255, the result wraps to
   $FF+note mod 256. Small negatives would land in the upper range (indices 224-255),
   reading deep into the work-RAM. No evidence any composer exploited this
   intentionally. The original docs imply positive semitone offsets (0, 3, 7 = minor
   chord) but don't exclude larger values.

3. **Enumerate which HVSC DMC V5 tunes actively produce off-table reads and survive
   as FULL.** The freq_overrun window after the +44 fix handles them; running
   `dmc_v5_family_batch` and grepping for members with `freq_overrun` non-empty would
   give the count.

4. **Check family-4 (Jupiter41, 686 SIDs, play+$95).** Does it share the same freq
   table size (96) and the same unchecked arp-add path? The Jaccard distance (0.31 to
   family-3) suggests it may diverge here.

5. **No external documentation found on either question.** The sidid.cfg signature for
   DMC V5.x (`BC ?? ?? B9 ?? ?? C9 90 D0 AND ...`) confirms the $90-loop-check but
   yields no layout information. CSDb release pages, HVMEC, TND tutorial, and Lemon64
   forum threads are silent on both questions. The authoritative source is the
   annotated disassembly.
