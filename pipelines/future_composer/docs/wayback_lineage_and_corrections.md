---
source_url: aggregated (CSDb sids + akaobi.wordpress.com + interview + Wikipedia + sidid)
fetched_via: cross-source synthesis 2026-06-03
fetch_date: 2026-06-03
author: synthesis
content_date: 1985-1992
reliability: secondary (synthesis of multiple primary/secondary sources)
---

# Future Composer / MoN driver lineage — corrected timeline and Hawkeye placement

## Corrections to `research.md`

The 95-line summary in `research.md` has **two errors** worth flagging
before further work:

1. **`research.md` says: "play = init + 6 (distinctive +6 offset)"**
   — TRUE for the **canonical** MoN driver (Noisy Pillars: init=$1800,
   play=$1806; Cybernoid 2: init=$xxxx, songout=$xxxx+3, play=$xxxx+6
   per the disassembly).

   **Hawkeye does NOT use +6** — CSDb confirms init=$7AE0, **play=$7AE3**
   (a **+3 offset**). So either (a) Hawkeye uses a 2-vector entry (init
   / play with no songout slot), or (b) the PSID header points to the
   songout slot as "init" and to the actual init as "play+something".
   Most likely (a): Hawkeye is an end-product PSID where the player
   was edited to drop the songout vector (since PSID has no "stop"
   call), giving a 2-vector init+play layout. **The existing claim
   "play offset = +6" should be qualified: "+6 for the MoN editor
   source; some PSID-exports compact to +3."**

2. **`research.md` says: "Origin: Finnish Gold (1988)"**
   — TRUE for the editor (Future Composer V1.0, FCS / FIG, June 1988).
   **FALSE for the driver** — the driver is **Charles Deenen's 1987
   MoN routine**, first heard in *Noisy Pillars* (1987 Scoop Designs).
   FCS only wrapped an editor around it, and Deenen+Tel sent
   cease-and-desist letters trying to halt FC's spread.

   So the driver lineage is:

   ```
   Charles Deenen 1987 MoN routine (Noisy Pillars, Scoop Designs)
     │
     ├── 1987-1988: used directly by Tel / Deenen in MoN game tunes
     │             (Cybernoid, Cybernoid 2, Hawkeye, Robocop, etc.)
     │
     └── 1988-06: FCS (Juha Granberg / Finnish Gold) reverse-engineered
                  it & released FC V1.0 (Code-credit to Deenen on CSDb
                  is honest re-attribution after the dust-up)
        │
        ├── 1988-09: V2.0/V2.1 (Beastie Boys) — bug fixes
        ├── 1989-08: V3.0 (Mnemonic Designs) — wave/pulse/filter
        │           tables formalised; this is the "FC V3.x" sidid
        │           signature shape
        ├── 1990:    V3.1 (Union) — folds V3.0 changes back into the
        │           canonical Deenen line (credits Deenen again)
        ├── 1989-90: V4.0/V4.1 (Dynamix) — sequence editor, packed
        │           data, relocation support
        └── 1992:    V5.0 (Warlords TMB) — cosmetic
   ```

   **Hawkeye lives on the LEFT branch**, not the FC branch. Calling it
   a "Future Composer tune" is technically inaccurate — it's a direct
   MoN-Deenen-driver tune. But the player byte-patterns are sidid-FC-V3.x,
   because FC V3.x's distinctive `CMP #$60 / CMP #$40` dispatcher *was
   reverse-engineered out of* the same driver Hawkeye uses.

## Frequency-table = exact Cybernoid 2 PAL table

The Cybernoid 2 source contains the explicit 96-entry PAL freq table:

```
lonote: $C3,$DD,$FA,$18,$38,$5A,$7D,$A3,$CC,$F6,$23,$53,
        $86,$BB,$E0,$30,$70,$B4,$FB,$47,$98,$ED,$47,$A7,
        $0C,$77,$E9,$61,$E1,$68,$F7,$8F,$30,$DA,$8F,$4E,
        $18,$EF,$D2,$C3,$C3,$D1,$EF,$1F,$60,$B5,$1E,$9C,
        $31,$DF,$A5,$87,$86,$A2,$DF,$3E,$C1,$6B,$3C,$39,
        $63,$BE,$4B,$0F,$0C,$45,$BF,$7D,$83,$D6,$79,$73,
        $C7,$7C,$97,$1E,$18,$8B,$7E,$FA,$06,$AC,$F3,$E6,
        $8F,$F8,$2E
hinote: $01,$01,$01,$02,$02,$02,$02,$02,$02,$02,$03,$03,
        $03,$03,$03,$04,$04,$04,$04,$05,$05,$05,$06,$06,
        $07,$07,$07,$08,$08,$09,$09,$0A,$0B,$0B,$0C,$0D,
        $0E,$0E,$0F,$10,$11,$12,$13,$15,$16,$17,$19,$1A,
        $1C,$1D,$1F,$21,$23,$25,$27,$2A,$2C,$2F,$32,$35,
        $38,$3B,$3F,$43,$47,$4B,$4F,$54,$59,$5E,$64,$6A,
        $70,$77,$7E,$86,$8E,$96,$9F,$A8,$B3,$BD,$C8,$D4,
        $E1,$EE,$FD
```

83 visible entries; entries 84-95 are off-screen in the truncated
view but exist (96 total).

**Check: $01C3 (C-0) → 451 → freq 451 * (985248/16777216) ≈ 26.5 Hz.**
That's well below C-0 = 16.35 Hz — confirms the table uses a **non-equal-tempered**
or **shifted** mapping where index 0 ≠ MIDI 0. Need to verify against
sidplayfp ear-test.

**Note**: the labels `lonote2 = * + 1` / `hinote2 = * + 1` are aliases
for `lonote+1` / `hinote+1`. The vibrato code:

```
ldy noothoogt,x           ; pitch index
lda lonote2,y             ; = lonote[index+1]   (next semitone)
sec
sbc lonote,y              ; - current semitone
sta templono              ; = freq delta between adjacent semitones
lda hinote2,y
sbc hinote,y
sta temphino
```

Computes the **delta between current and next semitone** — that's the
musical-vibrato width. The vibrato is then scaled by `vibrasto` (0..15)
and added/subtracted from the current freq via the `subval/addval`
loops. This is the **"linear in cents, not in Hz"** vibrato that gives
MoN its characteristic sound.

## Master-volume initialisation (init.sid candidate)

From the Cybernoid 2 `song` routine, the SID-init sequence is:

```
sty $d416         ; cutoff hi = 0 (filter off initially)
iny               ; y=1
sty $d417         ; resfilt = $01 — voice 1 routed to filter
lda #$10 + volume ; = $10 + $0F = $1F
sta $d418         ; volume=$F + filter low-pass on
jsr ok2           ; clears all per-voice state RAM
```

Followed by `uitzet` which zeros $D400-$D415 (all voices muted).

So **init.sid.master_vol** for Hawkeye should be `$1F` (= $10 + 15) =
volume 15 with low-pass enabled. **init.sid.resfilt** = $01 (V1 routed
to filter). **No PW priming** — PW is taken from the instrument when a
note starts.

This matches the "init trichotomy" pattern: a small set of typed
priming writes, then per-voice state is cleared, then the play loop
takes over.

## Knob values that distinguish songs sharing this driver

The Cybernoid 2 source has these tune-specific constants near the top:

```
volume          = $0f
vibtotzover     = $30      ; vibrato envelope max
pulserunspeed   = $63      ; PWM-sweep step
dubvoice        = $0c      ; double-voice detune
noisehitone     = $fa      ; noise pitch-hi
pulsearpwait    = $01
gitarwait       = $0f      ; (unused — vestigial)
spacelength     = $00
spacewait       = $60
wavearpwait     = 2
```

**For Hawkeye, these will be different values.** The extraction step
should recover them by scanning the immediate-mode operand bytes
inside the standard play routine.

These nine constants are the **per-tune "EngineConfig knobs"** that
make Cybernoid 2's driver into Hawkeye's driver. This matches the
SIDfinity USF-representation principle: same engine, parametric knobs,
no engine-specific dispatch.

## Pattern command-byte semantics (V3 dispatcher table)

Reconstructed from Cybernoid 2 source `h2 / skip / noglideset /
novoiceset / arpset / nolengset`:

### Sequence-byte (the outer loop, `h2`)

| Byte value | Meaning |
|---|---|
| `$FE` | song-end (call `songout` → mute all voices) |
| `$FF` | pattern-loop / sequence-restart |
| `$E0..$FD` | (passes to inner `h3f`: pitch index for off-pattern note?) |
| `$80..$DF` | reserved (handled in `h3a` chain) |
| `$60..$7F` | **set voiceinc** = byte AND $0F (voice's instrument-bank offset) |
| `$40..$5F` | **set repeatsto** = byte AND $3F (pattern repeat counter) |
| `$00..$3F` | **set toneadd** = byte AND $1F (transpose, in semitones) |

When a byte is < $40, it's also treated as a **pattern number** (after
shift): `lda st2; asl; tay; lda sequence,y; sta zp3; ...`. So the
`$00..$3F` "transpose" interpretation only fires when a previous step
already set the transpose flag — otherwise the byte is a pattern
number. This is a **stateful dispatch** with mode bits.

### Pattern-byte (inner per-note, via `(zp3),y`)

| First byte | Meaning |
|---|---|
| `$FF` | pattern end |
| `$F1..$FF` (odd) | filter resfilt-set: next byte → $D417 |
| `$F0` | new-note flag: next byte = real note byte |
| `$E0..$EF` | glide-set: next byte = glidedelay, then byte = tempglide (target pitch) |
| `$C0..$DF` | instrument-set: byte AND $1F + voiceinc → wavecount |
| `$80..$BF` | note-length set: byte AND $3F − 1 → nootleng (then next byte may extend) |
| `$70..$7F` | arpeggio program select: byte AND $0F → arp index |
| `$00..$6F` | **pitch byte** — index into lonote/hinote (after adding toneadd) |

(The exact ranges around $80/$C0/$E0 need careful disassembly — there
are nested checks; see `wayback_cybernoid2_driver.md` for the chain.)

This is a **prefix-style variable-length encoding** very similar to
Hubbard's pattern format but with **byte-range dispatch** rather than
nibble-flags. The "+6 / +3 dispatcher" we built for Hubbard '85 will
need significant adaptation for the FC family.

## Hawkeye-specific predictions

Given the driver is fundamentally identical to Cybernoid 2:

1. Frequency table at offset N, **96 bytes lo + 96 bytes hi** (192 bytes
   total), values starting with `$C3 $DD $FA $18` (lo) / `$01 $01 $01 $02`
   (hi).
2. **9-byte tune-config table** near the top of the player (volume,
   vibtotzover, pulserunspeed, dubvoice, noisehitone, pulsearpwait,
   gitarwait, spacelength, spacewait, wavearpwait).
3. **Instrument table**: 8 bytes per instrument, indexed × 8.
   Likely 16-32 instruments. Field order: `pulsehi, waveform, attdec,
   susrel, filcount, fx1, fx2, fx3`.
4. **`snelheid`**: 12-byte table (one byte per subtune, speed multiplier).
5. **`seqtabel`**: 12 × 6 bytes = 72 bytes of sequence pointers (3 voices × 2 bytes per subtune).
6. **`sequence`**: word array, ≤256 patterns × 2 bytes = ≤512 bytes.
7. **`pulsetabel`**: 4 × 8-byte PWM programs = 32 bytes.
8. **`filterbytes`**: 4 × 10-byte filter programs (likely larger in V3+).
9. **`drumtabel`**: word pointers + variable-length drum programs.
10. **`arplo/arphi`**: 8 × 2-byte pointers + variable arp programs.

## Open questions

1. **Subtune format**: is Hawkeye's 12-tune setup using `snelheid[12]`
   + `seqtabel[12 × 6]`, or are some subtunes SFX/jingles with different
   layout? Cybernoid 2 has 2 tunes; 12 in Hawkeye is unusually many for
   this driver — could be game music + SFX.
2. **PSID +3 offset**: does Hawkeye's PSID header just point at `songout`
   (the middle vector) as init, with init via a different mechanism?
   Or has the entry triple been compacted to 2 vectors?
3. **V3 wave-table vs V2 instrument**: Hawkeye is 1988, FC V3 is 1989.
   So Hawkeye should be the **V2-shape** instrument (8 bytes, no
   wave-table program) — but the `0123456789ABCDEF` PWM byte runs in
   the V4 instructions suggest wave-tables are part of the driver
   from earlier than V3's "official" release. The shape may be
   **continuous** rather than discrete-versioned.

## Provenance log entry

Synthesis of:
- `https://csdb.dk/sid/?id=28190` (Noisy Pillars metadata)
- `https://csdb.dk/sid/?id=28158` (Hawkeye metadata)
- `https://akaobi.wordpress.com/2014/11/09/sid-compilation-enhanced-jeroen-tel-style/` (Deenen 1987, FC controversy)
- `https://www.c64-hof.com/groups/f/fig/intfcs.htm` (FCS interview — "ripping Jeroen Tell's code")
- `https://en.wikipedia.org/wiki/Charles_Deenen` (background)
- Cybernoid 2 driver source `/tmp/fc_research/c64_6581_sid_players/Tel_Jeroen_MON/Tel_Jeroen_Cybernoid2.asm`
- sidid signature config (`MoN/FutureComposer`, `FC_V3.x`)
