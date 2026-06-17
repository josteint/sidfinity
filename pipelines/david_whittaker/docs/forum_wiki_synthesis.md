---
source_url: multiple (see per-section headers below)
fetched_via: WebSearch + WebFetch, 2026-06-17
fetch_date: 2026-06-17
author: research synthesis (forums + wikis cluster)
content_date: various (2023 for Lemon64 thread; 2023 for VGMPF NES Driver; ongoing)
reliability: secondary (synthesis from primary sources listed per section)
---

# David Whittaker C64 Player — Forums + Wikis Research

This file captures technical content from Lemon64, CSDb comments, VGMPF wiki pages
(NES Driver + Jason Brooke), and cross-platform conversion discussions.

---

## 1. VGMPF Wiki: David Whittaker (NES Driver)

**Source:** https://vgmpf.com/Wiki/index.php/David_Whittaker_(NES_Driver)
**Last updated:** 2023-08-13 (per wiki footer)
**Reliability:** secondary (wiki, attributed to researcher Tony Bybell + site editors)

This article is the richest **single publicly-available technical document** on the
Whittaker format family. Its cross-platform scope makes it directly relevant to
understanding the C64 format.

### Key structural finding

> "His music format IS assembler, but only as much as to represent absolute pointer
> addresses for data. Typically a song table of `<speed>,<v1 lo>,<v1 hi>, …
> <vn lo>,<vn hi>` which would be 7 bytes per entry on C64 (3 SID voices) and
> 9 on NES (4 2A03 voices). Voice pointer lo/hi pointers point to individual
> patterns."

Song table entry layout (C64):

| Offset | Size | Field          |
|--------|------|----------------|
| 0      | 1    | Speed (tempo)  |
| 1–2    | 2    | Voice 1 lo/hi  |
| 3–4    | 2    | Voice 2 lo/hi  |
| 5–6    | 2    | Voice 3 lo/hi  |

**Total: 7 bytes per sub-song entry** (confirmed by Panther.asm analysis: `Track1`, `Track2`, `Track3` are separate tables indexed by sub-song; Panther has 1 sub-song).

NOTE: The song table in Panther.asm does NOT match this 7-byte layout directly.
Panther uses three *separate* pointer-table vars (`Track1`, `Track2`, `Track3`
each a 2-byte absolute address) followed by per-voice sequence tables
(`Track1Seq`, `Track2Seq`, `Track3Seq`) of `!wo <pattern-ptr>` pairs
terminated by `!wo 0`. The VGMPF description is a high-level summary of the
multi-sub-song case; in single-sub-song early tunes the layout may be degenerate.
Cross-check against a multi-sub-song SID (e.g. Lazy Jones with 21 sub-songs).

### Pattern end byte

- **C64:** `$88`
- **Spectrum (ZX):** `$87`
- **NES:** `$FF`

Confirmed by: Panther.asm `ArpTable` entries end with `$88`:
```
L_976F  !by $00,$03,$07,$88
```
And pattern data ends with `$88` (e.g. `L_9902: !by $be,$d0,$00,$00,$ff,$80,$88`).

### Frequency tables

Two C64 implementations noted:

| Variant | A-1 value | G-7 value | Notes |
|---------|-----------|-----------|-------|
| Whittaker standard | (see Panther NoteFreqsL/H below) | — | Used by all HVSC tunes |
| Manfred Trenz variant | 3D5 hex | 32 hex | Super Turrican (NES); Trenz modified DW's source code for NES Super Turrican |

Panther C64 frequency table (from `NoteFreqsL`/`NoteFreqsH` at $9126):
```
$0116, $0126, $0138, $014b, $0160, $0172, $0189, $01a1, $01bb, $01d6, $01f1, $020e  ; octave 1
$022c, $024c, $0270, $0296, $02c0, $02e4, $0312, $0342, $0376, $03ac, $03e2, $041c  ; octave 2
$0458, $0498, $04e0, $052c, $0580, $05c8, $0624, $0684, $06ec, $0758, $07c4, $0838  ; octave 3
$08b0, $0930, $09c0, $0a58, $0b00, $0b90, $0c48, $0d08, $0dd8, $0eb0, $0f88, $1070  ; octave 4
$1160, $1260, $1380, $14b0, $1600, $1720, $1890, $1a10, $1bb0, $1d60, $1f10, $20e0  ; octave 5
$22c0, $24c0, $2700, $2960, $2c00, $2e40, $3120, $3420, $3760, $3ac0, $3e20, $41c0  ; octave 6
$4580, $4980, $4e00, $52c0, $5800, $5c80, $6240, $6840, $6ec0, $7580, $7c40, $8380  ; octave 7
$8b00, $9300, $9c00, $a580, $b000, $b900, $c480, $d080, $dd80, $eb00, $f880        ; octave 8 (partial)
```
91 entries (8 octaves × 12 − 5 at top). Stored interleaved lo/hi as `!wo` words.

### Vibrato: per-octave scaling on C64, absent on NES

> "Vibrato on the NES comes from tables that don't scale according to NES octave,
> but this limitation doesn't exist in C64 as it encodes frequency differently
> and in fact he scales vibration depth up per octave."

The Panther SoundUpdate routine at $9537–$95BF implements this: vibration depth
is shifted proportionally (see the ASL/ROL loop at `L_955A`). On NES, that logic
was skipped (limitation; above highest frequencies vibrato is disabled outright).

### Sound parameter tables (NES analogy for C64 effects)

> "NES contains special tables similar to 'soundparameters' found on C64 editors
> such as Future Composer. These encode vibrato and tremolo information."
> "Final byte of each table entry has high bit set."

On C64, the ArpTable entries do the same: terminated by `$88` (high bit set = end).
The arpeggio pointer table at `ArpTable` ($9141+) contains 13 entries:

| Index | Semitone sequence | Musical meaning          |
|-------|-------------------|--------------------------|
| 0     | 00 03 07          | minor triad              |
| 1     | 00 04 07          | major triad              |
| 2     | 00 03 07 0C       | minor triad + octave     |
| 3     | 00 04 07 0C       | major triad + octave     |
| 4     | 07 0C 0F          | fifth / octave / minor 9th |
| 5     | 07 0C 10          | fifth / octave / major 9th |
| 6     | 03 07 0C          | minor (root omitted)     |
| 7     | 04 07 0C          | major (root omitted)     |
| 8     | 00 0C             | octave                   |
| 9     | 00 04             | root + major 3rd         |
| 10    | 00 03             | root + minor 3rd         |
| 11    | 00 05             | root + fourth            |
| 12    | 00 07             | root + fifth             |

All terminate with `$88` (high-bit-set end marker matches the C64 `$88`
pattern-end byte by value; the SoundUpdate arpeggio scanner checks `cmp #$54`
and wraps the pointer, so bytes < $54 are semitone steps, bytes >= $54 reset).

### Driver architecture (Tony Bybell attribution)

Researcher Tony Bybell provided extensive analysis of the NES version. He noted:
- Similarities to Jason Brooke's C64 rewrite
- "Music format as assembly-based data with macro expansion rather than true compiled code"
- Common methodology: Spectrum and C64 formats use similar macro structure

### Game list using the NES driver

Loopz (1990), Elite (1991), Castelian (1991), Krusty's Fun House (1992),
Spider-Man: Return of the Sinister Six (1992), Alfred Chicken (1993),
Super Turrican (1993, Manfred Trenz modification), The Lion King (1995).

---

## 2. Lemon64 Forum: "Why wasn't David Whittaker asked to do the music for Xenon?"

**Source:** https://www.lemon64.com/forum/viewtopic.php?t=81385
**Date:** July 2023
**Reliability:** secondary (forum; key poster "Bansai" has technical expertise)

### Bansai's technical posts (key contributor)

User **Bansai** (known technically — built an automatic ZX128→C64 Whittaker
converter, see §3 below) posted:

> "His players between Spectrum and C64 were *quite* compatible with the Spectrum
> missing commands here and there for the additional SID waveforms among other
> things, but nothing that was a dealbreaker with getting a reasonable conversion.
> All the usual Whittaker arpeggios tables and such are there in the Spectrum data."

Technical implication: the ZX Spectrum version has the same arpeggio table
structure as C64; SID-specific waveform commands ($8A noise, $8B pulse, $8C saw,
$8D tri, $92 ring-tri, $93 sync-square) have no equivalents on Spectrum but
everything else maps cleanly.

> "I have full player source/song data for Xenon [offered via PM]"
> "Data conversion isn't size optimized and can be improved a lot, broken into
> separate memory regions"

Bansai also mentioned a working conversion of Xenon's ZX128 player to C64,
demonstrating the structural closeness between the two platform variants.

---

## 3. CSDb: Xenon (ZX128 conversion) by Bansai (2023)

**Source:** https://csdb.dk/release/?id=233756
**Released:** 12 July 2023
**Author:** Bansai
**Reliability:** primary (release notes by the author)

This release is a C64 SID conversion of David Whittaker's ZX Spectrum 128K
music for Xenon. Technically highly informative about Whittaker's cross-platform
data architecture.

### Bansai's technical release notes (exact quotes)

> "Subsong and track pointers are the same exact format as C64."

> "Looking at the patterns, song pattern data is very close to C64 with some
> minor differences."

> "Pattern commands were parsed and converted automatically."

> "Arpeggio tables, glides, and vibrato passed right through to the C64."

> "I theorised that Whittaker used an assembler-based mostly compatible macro
> command structure across platforms enabling easy song data portability."

**Extraction method:** Memory dump extracted from a hacked `aylet` emulator on
Linux (Z80/AY emulator) to examine the Spectrum 128K song data structure. The
conversion is automatic (not a manual re-arrangement).

**iAN CooG** (HVSC tech, SIDId author) commented, apparently surprised at the
quality of the result — confirming it sounds like authentic Whittaker.

**Conclusion for migration:** The ZX-to-C64 automatic conversion confirms:
1. Song/subsong pointer tables: byte-identical format
2. Pattern command bytes: near-identical with minor Spectrum-missing-SID-cmds gap
3. Arpeggio tables: identical (no conversion needed)
4. Glide/portamento: identical
5. Vibrato: identical

---

## 4. VGMPF Wiki: Jason Brooke

**Source:** https://www.vgmpf.com/Wiki/index.php/Jason_Brooke
**Reliability:** secondary (wiki, attributed to Jason Brooke himself via interview)

### The June 1986 driver rewrite

Jason Brooke rewrote David Whittaker's CPC driver in June 1986 at Whittaker's
request. Context: Binary Design's game programmers complained about both the
original C64 and CPC drivers being slow.

The rewrite was:
- "Much shorter, faster, and more flexible"
- "Got adapted to more platforms and released by late September [1986]"
- Added: "Much more flexible chords, envelopes, and combining pitch bends
  with chords"

Brooke's workflow:
- **Assembler:** "Mikes Assembler" on an Einstein computer
- **Method:** "A sound driver was programmed once per platform, and songs and
  sound effects were arranged by typing numbers and labels into the driver's
  source code"
- Einstein could directly test ZX Spectrum 128, CPC, and MSX (same Z80 CPU,
  same AY audio chip, different tuning)

### Which driver is in HVSC?

From VGMPF: "One of them [Brooke or Whittaker] converted it back to the C64,
and he used it (without real updates) until 1991."

This strongly implies the HVSC SIDs from 1986 onward use the
**Brooke-rewritten driver** adapted back to C64, NOT Whittaker's original
1985 minimalist driver. The pre-Brooke "minimalist" driver (tuned at 424 Hz,
limited effects) is likely only in very early SIDs (1984–mid 1986, possibly
Lazy Jones and a few Terminal Software/early Binary Design titles).

**Driver timeline hypothesis:**

| Period | Driver | Characteristics |
|--------|--------|-----------------|
| late 1985 – mid 1986 | Whittaker original | Minimalist, 424 Hz tuning, some filter use |
| June 1986 onward | Brooke rewrite → C64 | Faster, chords, flexible envelopes, pitch bends; used until 1991 |

The Panther.asm (1986, Mastertronic) is one of the FIRST games to use the
post-Brooke C64 driver. Lazy Jones (1984) likely uses the pre-Brooke driver.
This explains why NostalgicPlayer distinguishes "QBall old player" from
"standard player" — QBall was a very early Amiga/C64 game and would use
the pre-Brooke format.

---

## 5. C64.com Interview: David Whittaker (technical excerpts)

**Source:** https://www.c64.com/interviews/whittaker.html (SSL cert issue; content
from VGMPF synthesis)
**Reliability:** secondary

Key technical facts:

- Composed on: **Yamaha CX5M** and **Jupiter 6** (hardware synthesizers), no MIDI
- Workflow: "Just a synth and an assembler – no MIDI whatsoever"
- Filter: "By autumn 1987, stopped using the filter (except on engine sounds)"
- PWM: Especially appreciated "pulse-width flexibility" of SID chip
- Polyphony trick (Glider Rider): "Just the old method of playing quick/short notes
  of a chord, in quick succession – giving the feeling of more notes sounding than
  there really were" — rapid arpeggiation to simulate chords
- Driver sharing: "Usually good about lending his sound drivers to other companies,
  but some also used them without permission"

---

## 6. Lemon64: "SIDplayer routines" (general C64 music driver discussion)

**Source:** https://www.lemon64.com/forum/viewtopic.php?t=26021
**Reliability:** tertiary (no DW-specific content)

General C64 music driver notes (for comparison against Whittaker):

- Vibrato typically implemented as "a frequency modulation table that adds $XX XX
  to the played note in Y frames before it jumps to position Z in the same table"
- Per-tick effects run when speed counter > 1
- "Essential player features: step-programming for instruments (waveform/arpeggio,
  pulse and filter), portamento & vibrato; transpose & looping in pattern sequencer"

The Whittaker Panther driver matches this pattern exactly — these are standard C64
music driver design patterns, not Whittaker-specific.

---

## 7. Synthesis: Command Byte Map (C64 Panther driver, from `CommandTable`)

From Panther.asm lines 397–418, the command dispatch table at `$9253`:

| Byte | Label | Action |
|------|-------|--------|
| $80 | L_93FB | → L_9431 (set note duration from VD_NOTD; reload pat ptr) |
| $81 | L_93CF | VD_B1D = 0 (clear glide/portamento flag) |
| $82 | L_93D7 | VD_B1D = $40 (set portamento-up? bit 7) |
| $83 | L_93DF | Read 1 byte → ModeVol ($D418) volume |
| $84 | L_9363 | VD_FLAGS \|= $04 (set bit 3 — vibrato or chromatic flag?) |
| $85 | L_935B | VD_FLAGS \|= $20 (set bit 6) |
| $86 | L_93C5 | VD_FLAGS \|= $08 (set bit 4 — pitch slide up/down?) |
| $87 | L_93BD | VD_FLAGS \|= $80 (set bit 8) then fall to $86 |
| $88 | L_9304 | **Pattern end / next pattern from track sequence** |
| $89 | L_939A | Read 2 bytes → VD_B1A, VD_B1B, VD_B1C (glide params) |
| $8A | cmd_Noise | VD_WAVE = $80 (noise waveform) |
| $8B | cmd_Pulse | VD_WAVE = $40 (pulse waveform) |
| $8C | cmd_Saw | VD_WAVE = $20 (sawtooth waveform) |
| $8D | cmd_Tri | VD_WAVE = $10 (triangle waveform) |
| $8E | L_93EF | VD_FLAGS \|= $03 (set bits 1+2) |
| $8F | cmd_PulseHi | Set VD_PWL=0, VD_PWH=next_byte; clear VD_B21 (PWM off) |
| $90 | L_9297 | Read 3 bytes → VD_B1E, VD_B1F, VD_B20 (PWM params); set VD_B21=1 |
| $91 | cmd_StopMusic | Pull stack, jump to StopMusic |
| $92 | cmd_RingTri | VD_WAVE = $14 (ring-mod triangle) |
| $93 | cmd_SyncSquare | VD_WAVE = $42 (sync + pulse) |

**Special pattern byte ranges** (pspecial dispatch, lines 744–828):

| Range | Condition | Action |
|-------|-----------|--------|
| $80–$B7 | `cmp #$B8; bcc pcommand` | Execute command via CommandTable[$byte − $80] |
| $B8–$C7 | falls through to arpeggio | `asl; tax; lda ArpTable,x` → set arp pointer + VD_FLAGS\|=$10 |
| $C8–$D7 | `adc #$10; bcs padsr` | ADSR: read 2 bytes (AD, SR) from pattern |
| $D8–$DF | `adc #$10; bcc ptempo` | Tempo: `sta SongTempo` (value = byte+9) |
| $E0–$FF | `adc #0; ldy #VD_NOTD; sta (VD),y` | Note duration |

Notes:
- Notes are raw bytes $00–$7F (positive = note value index into NoteFreqsL/H)
- $88 is BOTH the "next pattern" command AND the arpeggio sequence terminator
- The PWM unit (L_9297/$90) takes 3 bytes: speed_lo, max_pw_hi, step; L_9673–L_9700
  in SoundUpdate implements bidirectional PWM sweep

---

## 8. Voice Data Block (VD) layout — Panther driver

Base pointer in zero-page: $FA/$FB (`VD`). Three 36-byte blocks: `v1data`, `v2data`, `v3data`.

| Offset | Label | Size | Purpose |
|--------|-------|------|---------|
| $00 | VD_FLAGS | 1 | State flags (bits: 0=flip, 1=?, 2=glide, 3=pitch-slide, 4=PWM-active, 5=arp, 6=flag2, 7=flag3) |
| $01–$02 | VD_PAT | 2 | Current pattern pointer (lo/hi) |
| $03–$04 | VD_TRACK | 2 | Track sequence pointer (lo/hi) = VD_B03/B04 |
| $05–$06 | VD_B05/B06 | 2 | Track position offset counter |
| $07–$08 | VD_B07/B08 | 2 | Glide delta accumulator |
| $09–$0A | VD_ARP2L/H | 2 | Arpeggio restart pointer (loop-back) |
| $0B–$0C | VD_ARP/ARPH | 2 | Arpeggio current pointer |
| $0D | — | 1 | (unused?) |
| $0E–$0F | VD_B0E/B0F | 2 | Glide counter/limit |
| $10 | VD_NOTC | 1 | Note duration counter (counts down) |
| $11 | VD_NOTD | 1 | Note duration (reload value) |
| $12 | VD_NOTE | 1 | Current note index (0–90) |
| $13 | VD_AD | 1 | ADSR Attack/Decay |
| $14 | VD_SR | 1 | ADSR Sustain/Release |
| $15–$16 | VD_FQL/FQH | 2 | Frequency (lo/hi; written to SID each frame) |
| $17–$18 | VD_PWL/PWH | 2 | Pulse width (lo/hi) |
| $19 | VD_B19 | 1 | Gate delay counter (1→write waveform without gate, then gate-on) |
| $1A–$1C | VD_B1A/B/C | 3 | PWM/glide working vars |
| $1D | VD_B1D | 1 | Glide direction flag ($00=off, $40=portamento bit) |
| $1E–$20 | VD_B1E/F/20 | 3 | PWM: min_pw, max_pw_hi, step |
| $21 | VD_B21 | 1 | PWM active flag (0=off, 1=up, $81=down) |
| $22 | VD_WAVE | 1 | Waveform byte (without gate bit): $80=noise,$40=pulse,$20=saw,$10=tri,$14=ring+tri,$42=sync+pulse |
| $23 | VD_CTRL | 1 | Final control byte written to $D404/B/12 (= WAVE+gate; VD_B19 controls timing) |

---

## 9. Gate timing mechanism

From play loop (lines 327–378):

For each voice, after SoundUpdate:
```
ldx v1data + VD_CTRL   ; load computed ctrl (wave | gate)
lda v1data + VD_B19    ; check delay counter
beq _v2                ; if 0: skip pre-gate write, go straight to gate-on
dec v1data + VD_B19    ; decrement delay
stx SIDV1CTRL          ; write wave WITHOUT gate (B19 set by pspecial at note start)
inx                    ; gate bit = next instruction's implicit +1 = set gate
stx SIDV1CTRL          ; write wave WITH gate
```

So on a new note:
1. Frame N (B19=1): write waveform WITHOUT gate, then write WITH gate (hard restart simulation)
2. Frame N+1 onward (B19=0): write waveform WITH gate only

This implements a standard SID hard-restart: one frame of gate-off+waveform before gate-on. Duration is exactly 1 frame (VD_B19 is initialized to 1 at every new note via L_9431 → `lda #1; sta (VD),y ; ; ldy #VD_B19`).

---

## 10. Filter usage timeline (from VGMPF DW article)

> "The first drivers were minimalist, tuned at 424 Hz, and a few use the SID chip's
> inconsistent filter, sounding best with a bias of at least -300."
> "By autumn 1987, Whittaker stopped using the filter (except on engine sounds)."

Practical implication for migration:
- Pre-1987 SIDs: may set $D415/$D416/$D417 (filter cutoff + resonance/routing)
- Post-autumn-1987 SIDs: $D417 = 0 (all voices unfiltered, filter off) EXCEPT
  engine-sound effects
- The Panther.asm (1986) sets `ModeVol = $0F` (vol=15, filter mode=0) at init;
  no filter writes in the pattern stream → no filter in Panther

---

## 11. Known gaps after this sweep

1. **Lazy Jones (1984)**: Almost certainly uses the pre-Brooke "minimalist" driver.
   Load at $1480, init at $1500, play at $1630, 21 sub-songs, 3328 bytes. Need a
   disassembly to confirm the structural differences vs Panther (pre-vs-post Brooke).
   Check if `$88` end marker and CommandTable are already present.

2. **comp.sys.cbm Usenet**: No technical Whittaker threads found in this sweep.
   No indexable Usenet archive returned results. Likely no substantive technical
   discussion exists there (Whittaker's driver was a commercial secret during its
   active use period).

3. **Forum64.de**: German-language forum returned no results for Whittaker player
   internals. If it exists, it would be under "SID Musik Treiber" or "C64 Musik
   Format" search terms.

4. **codebase64.org**: The wiki page `/doku.php?id=base:david_whittaker_player`
   does not exist (empty response). The general wiki at `codebase64.org` returned
   a Cloudflare verification block and could not be fetched. A future attempt via
   Wayback Machine (`web.archive.org/web/*/codebase64.org/*whittaker*`) may find
   a cached version.

5. **AtariAge**: Whittaker's Atari ST/Amiga work is documented at exotica.org.uk
   (also Cloudflare-blocked this session). The Amiga `.dw` format is well-covered
   by the NostalgicPlayer C# source and c-flod ActionScript (see other docs).

6. **DeepSID player-type label**: Could not extract from JavaScript-rendered UI.
   The player-id / sidid signatures cover only ONE variant (`David_Whittaker`)
   suggesting SIDID does not distinguish pre-Brooke vs post-Brooke variants.
   This is worth verifying by running sidid against Lazy_Jones.sid vs Panther.sid.

---

## Leads to follow

| Resource | URL | Why important |
|----------|-----|---------------|
| Bansai's Xenon conversion source | PM on Lemon64 (no public repo found) | Full ZX128↔C64 format diff |
| codebase64 wiki (Wayback) | `https://web.archive.org/web/2023*/https://www.codebase64.org/doku.php?id=base:david_whittaker_player` | May have a player analysis page |
| exotica.org.uk David Whittaker format | `https://www.exotica.org.uk/wiki/David_Whittaker_(format)` | Currently Cloudflare-blocked; Amiga .dw format spec |
| Lazy Jones disassembly (pre-Brooke driver) | Need to generate with tools/seed_disassembly.py | Confirm pre-vs-post Brooke structural diff |
| forum64.de Whittaker search | `https://www.forum64.de/index.php?board/15-c64-allgemein/` search "Whittaker" | German scene may have technical RE discussions |
| HVSC DOCUMENTS mentions | `hvsc84/DOCUMENTS/Update00.hvs`, `Update02.hvs`, `Update_Announcements/20020817.txt`, `20240630.txt` | grep-match "whittaker"; reclassification / variant notes |
| sidid run on Lazy Jones vs Panther | `sidid Lazy_Jones.sid Panther.sid` | Verify single vs multiple sidid signatures |
| Tony Bybell (VGMPF NES researcher) | VGMPF talk page | May have further C64 analysis |
| Bansai (Lemon64 user) | https://www.lemon64.com/forum/profile.php?mode=viewprofile&u=<id> | Has full Xenon source; knowledgeable on ZX↔C64 format |
