---
source_url: derived from JC64dis disassembly (see jc64dis_companion_disassembly.md)
fetched_via: synthesized
fetch_date: 2026-05-25
author: this research session, distilled from primary disassembly
content_date: 1984 (original)
reliability: tertiary (derived from primary)
---

# Companion player — format specification (Bowden 1984 baseline)

This is the **canonical** Companion format from Bowden's type-in. The
Hubbard-extended variant at $C900 in our local engine builds on top of this.

## Memory layout (Bowden $C000-based original)

```
$C000   exitIrq       JMP $EA31
$C003   playSound     IRQ entry, tick counter
$C012+  per-voice state records (interleaved):
        currentIndexV1  cursor       (2 bytes: idx + pad)
        sidRegV1        instrument   (5 bytes: pulse-lo, pulse-hi,
                                      ctrl-no-gate, AD, SR)
        currentIndexV2  cursor + sidRegV2
        currentIndexV3  cursor + sidRegV3
$C031+  setMusicIrq / restoreKernalIrq
$C04C+  processSound  (dispatcher)
$C06D+  processData   (per-voice byte handler)
$CA00   frequencyHi[128]
$CA80   frequencyLo[128]
$CB00+  musicV1[…]   note stream
        musicV2[…]
        musicV3[…]
```

## Note byte encoding (verbatim from disassembly comment)

```
00..7F   note (octave high nibble, semitone low nibble within 0..11)
80       rest — write current ctrl byte with gate=0
FF       restart tune for this voice — reset cursor to 1, re-execute slot 0
```

A4 (concert A) at index $46 (octave 4, semitone 6 — 1-based or shifted?
actually octave-row $40, semitone $06 = "A4" by Bowden's mapping). Frequency
table is calibrated to **A4 = 424 Hz (PAL)** / 440 Hz (NTSC). Within each
octave row of 16, only first 12 slots are real notes; last 4 are $00.

## Tempo

Single global byte at `tuneSpeed` (default $10 = 16 IRQ ticks per song
step). The IRQ runs at the C64's screen-rate VBI (~50 Hz PAL), so default
tempo is `50 Hz / 16 = 3.125` song steps per second.

## Per-voice algorithm (each IRQ tick that hits the speed boundary)

```
for voice V in {V1, V2, V3}:
    byte = musicV[V][cursor[V]]
    cursor[V] += 1
    if byte < $80:
        # play note
        SID.freq_hi = freqHi[byte]
        SID.freq_lo = freqLo[byte]
        SID.pulse_lo, pulse_hi, ctrl(gate=0), AD, SR = state[V]
        SID.ctrl = state[V].ctrl | 1   # gate on (literally INY trick)
    elif byte == $80:
        SID.ctrl = state[V].ctrl       # gate off (release)
    elif byte == $FF:
        cursor[V] = 1                  # restart, replay slot 0 immediately
        byte = musicV[V][0]
        goto play-note
    else:
        # bytes $81..$FE are ignored (early-out RTS)
        rts
```

Note three quirks:
1. There is no instrument index — every note for a voice plays the SAME
   instrument (the single 5-byte state record). Instrument changes require
   patching the state bytes from outside the player.
2. The gate-on trick is `LDY ctrl ; INY ; STY $D404`. This means the
   stored ctrl byte must have gate=0 and any non-gate bits set. Setting gate
   via INY only works correctly if bit 0 of ctrl is 0; otherwise carry into
   bit 1 corrupts the SYNC bit. This is a known footgun.
3. The restart sentinel ($FF) re-executes slot 0 immediately on the same
   tick. Slot 0 is therefore typically a "first note", not metadata.

## What Hubbard's extension at $C900 (our local file) adds

Comparing the published Bowden code to our local disassembly:

| Feature                | Bowden $C000          | Hubbard $C900 extension    |
|------------------------|-----------------------|----------------------------|
| Layout                 | flat notes per voice  | orderlist → note table    |
| Per-voice cursor       | inline with state     | $C6C0+ block               |
| Tempo                  | 1 divider             | 2 dividers ($C6D5/$C6D6)   |
| PWM                    | none                  | global PW sweep on V3      |
| Effects                | none                  | none other than PWM        |
| Note sentinels         | $80 rest, $FF restart | likely same                |

The extra orderlist layer indicates Hubbard added a pattern-style two-tier
sequencer on top of Bowden's flat note stream. Validate this against the
local $C900 disassembly:

- Freq tables at $C000+y / $C080+y → exactly Bowden's freqHi/freqLo
  positions, just relocated 256 bytes earlier (Bowden's are at $CA00/$CA80;
  Hubbard's are at $C000/$C080). The 128-entry size and PAL 424 Hz tuning
  almost certainly survive — verify the FF E6 8F F8 2E tail still matches.
- Per-voice state at $C6C0+ → Bowden's state was inline at $C012+; Hubbard
  moved it to a dedicated block.
- Orderlists at $C5B0/$C5F8/$C640 → not in Bowden, fully new.

## Open questions about Hubbard's extension

1. What is the orderlist sentinel? In Bowden's note layer it's $FF =
   restart; the orderlist layer presumably also has a restart marker, but
   could be $FF, $80, or something else.
2. How are pattern lengths encoded? Implicit by next-pattern address? Bytes
   inline? A length byte at the head?
3. What does the second tempo divider ($C6D6) do? Bowden has only one
   (`tuneSpeed`). A second one might be a "PW sweep speed" counter or a
   "sub-tick" counter for swing.
4. How is the V3 PW sweep parametrised? Start, end, direction, step?
5. Is there instrument-change support, or is per-voice timbre still locked
   for the whole tune?

These are the questions the local Companion engine work should answer next.
