<!--
source_url: (multiple — per-section attribution)
  - https://cadaver.github.io/rants/music.html  (Cadaver, "Building a musicroutine")
  - https://blog.chordian.net/2022/08/27/composing-in-sid-factory-ii-part-4-instruments/  (JCH/Chordian, SF2 successor)
  - https://codebase64.pokefinder.org/doku.php?id=base:a_sid_player_routine  (codebase64, via search)
  - https://www.lemon64.com/forum/viewtopic.php?t=49977 , t=26968  (Lemon64, via search)
  - https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/utils/  (Vibrants tool listing)
fetched_via: WebFetch + WebSearch (small-model summarization; some lines via search snippets)
fetch_date: 2026-06-13
author/handle: Cadaver (Lasse Öörni); JCH/Chordian; codebase64 contributors
content_date: cadaver page ~2000s; SF2 article 2022; codebase64 ongoing
reliability: secondary
note: Cadaver and the SF2 article are written by SID-player authors and are the
      most authoritative *technical* (write-model) secondary sources found.
      The four HR *types* ($0x/$4x/$8x/$Ax) are JCH-NewPlayer-specific; the
      *frame-by-frame register sequence* below is the shared C64 idiom JCH/DMC
      both implement.
-->

# JCH NewPlayer — hard-restart timing & per-frame SID write model

This is the codec-critical doc: it pins down the exact `$D404/$D405/$D406`
write sequence around a note change, which SIDfinity must reproduce
frame-accurately. The four HR *types* are JCH-specific selectors; the underlying
register dance is the standard "testbit hard restart" idiom.

## 1. The write-order law (Cadaver — "Building a musicroutine") — verbatim

> "In this method it's important that Attack/Decay and Sustain/Release are always
> written before Waveform. There might also be a necessity for some delays
> between them for maximum reliability."

> "Works reliably on PAL machines only, but gives a nice sharp sound."

Per-frame breakdown (Cadaver, as summarized):

- **2+ frames before the note ends (the hard-restart frames):** clear the gate
  bit and set ADSR to a preset value (e.g. `$0000`, `$0F00`, or `$F800`).
- **Frame 1 of the new note:** write Attack/Decay (`$D405`) and Sustain/Release
  (`$D406`) **first**, then write `$09` to the waveform register `$D404`
  (testbit + gate, no waveform yet).
- **Frame 2 of the new note:** load the instrument's actual waveform value into
  `$D404`; the note becomes audible.

**Register-order invariant for the composer:** within a note-start frame the
order MUST be `$D405,$D406` (ADSR) **before** `$D404` (waveform). This is exactly
the kind of within-frame write ORDER the project's Mode-1 verdict cares about
(gate edges / ADSR delay) — getting it backwards will diverge the write-log even
if the values are right.

## 2. The `$09` first-frame value (codebase64 / Lemon64) — verbatim

> "Modern C64 editors like DMC/JCH write nonzero values to ADSR (for example
> $0f00), and have $09 (testbit+gate) in the waveform register for first frame
> of the note." — (codebase64 / Lemon64, via search)

So for a JCH-family note start you should expect to see, at `$D404`:
`...$09 (test+gate, frame 1) → <instrument waveform> (frame 2)...`, with `$D405/6`
loaded to the HR-ADSR (commonly `$0F00`) during the preceding HR frames and to
the instrument's real ADSR on the start frame.

## 3. The 2-frame gate-off rule (codebase64) — verbatim

> "You need to keep the gatebit 0 for a certain time (usually at least 2 frames,
> 40ms on PAL) so that starting of new attack succeeds most of the time. The
> testbit doesn't affect the envelope generator at all, and you need the minimum
> 2 frame period with gatebit off to be safe." — (codebase64, via search)

This is why three of the four JCH HR types drop the gate **2 frames** before the
next note (`$4x`, `$8x`, `$Ax`); the `$0x` type goes 3 frames (gate off 3 frames
before, waveform cleared 1 frame before — see research.md / the NP21 format doc).

## 4. SID Factory II (JCH's successor) on the same mechanism — verbatim

These confirm the "two ticks before" timing and the `$0F 00` HR-ADSR default,
and show how the successor exposes the same idea JCH's NewPlayer encodes in the
instrument's byte C/D:

> "The hard restart prevention works by gating off and resetting the ADSR values
> a few ticks before the next note triggers. How to design hard restart in a
> player varies a lot depending on the creator, but in SID Factory II, most
> drivers that use it triggers the effect exactly two ticks before."

> Example: "if a note is held gated on for 15 ticks total, the hard restart
> activates after 13 ticks have elapsed, leaving 2 ticks before the subsequent
> note triggers."

> "The second nibble points to the HR table. The value pair here defines the
> ADSR value used for the last two ticks. I recommend you leave that at the
> default `0F 00`."

> "You can enable hard restart for an instrument by setting the most significant
> bit of the third byte. In other words, add `80` to whatever else is used in
> this byte."

Cross-mapping to JCH NewPlayer's instrument byte C (high nibble = HR type):
- The SF2 "set MSB of byte 3 to enable HR" maps to JCH's `$8x` HR-type bit on
  instrument byte C — the same high-bit-of-the-HR-byte convention.
- "ADSR value for the last two ticks read from the HR table, default `0F 00`"
  matches the NP convention "hard-restart ADSR read from command-table row 0,
  bytes B,C, default `0F 00`" (see `forum_cheesecutter_np21_format.md`).

## 5. The four JCH HR types — consolidated (for the write-model)

From research.md + the NP21 format doc, restated in write-log terms:

| Type (byte C hi nibble) | Gate-off lead | HR-ADSR write? | Waveform-clear | AD preserved? |
|---|---|---|---|---|
| `$0x` | 3 frames before | (gate-off only) | waveform cleared 1 frame before | — |
| `$4x` "soft" | 2 frames before | no (soft) | — | — |
| `$8x` "hard" | 2 frames before | yes — write HR-ADSR (`0F00`) | — | no (AD overwritten) |
| `$Ax` "Laxity" | 2 frames before | yes, but **AD untouched** | — | **yes (AD preserved)** |

The `$Ax` "Laxity restart" is the distinguishing Laxity/NP21 behavior: it does
the hard restart **without clobbering the Attack/Decay nibbles**, so the next
attack inherits the instrument's AD instead of the HR-ADSR's AD. For the codec
this means: on an `$Ax` instrument, the HR frames write `$D406` (SR) to the
HR value but leave `$D405` (AD) at the instrument's AD.

## 6. Tooling corroboration of the JCH↔Laxity player split

The Vibrants utility set ships **separate relocators** —
`Relocate JCH.prg` *and* `Relocate Laxity.prg` — plus `VibRip50.00.prg` (the
"VibRip" ripper) and `JCH Split v1.1.prg`. Two distinct relocators is direct
evidence that the JCH player and the Laxity player, while one *format family*,
have different enough code/layout to need different relocation logic — reinforcing
the §1 lineage note in `forum_version_lineage_and_comparison.md` (NP21 = Laxity's
continuation). For SIDfinity ripping/identification, `VibRip` is the period tool;
the modern path is SIDId signatures (research.md lists Dane_NewPlayer among ~21
variants).

## 7. Open verification items (flag before trusting in the codec)

- Exact `$0x` waveform-clear value (is it `$08` noise-off / `$00` / instrument's
  HR waveform byte D?) — research.md says "waveform cleared 1 frame before"; the
  *value* written is the instrument's byte-D HR-waveform per the NP21 instrument
  table. Confirm against a real `$0x` rip's write-log.
- Whether `$8x`/`$Ax` write `$D404=$09` (test+gate) or just gate-off during the
  HR frames in the *classic NP20* player specifically (Cadaver's `$09`-on-frame-1
  is the general idiom; NP20 may differ in whether testbit is set). This is the
  single most likely source of a within-frame write-log divergence.
