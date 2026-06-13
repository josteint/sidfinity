# X-Ample / Compotech — X-Ample_Digi / CIA Sample Mode

**source_url:** https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
                https://gist.github.com/munshkr/30f35e39905e63876ff7
                https://bumbershootsoft.wordpress.com/2022/12/30/digital-sound-playback-on-the-c64/
                https://c64.xentax.com/index.php/16-sid-digi-play-routines
**fetched_via:** WebFetch + WebSearch
**fetch_date:** 2026-06-13
**reliability:** secondary (sidid pattern is primary; CIA technique is general knowledge)

---

## What is X-Ample_Digi?

`X-Ample_Digi` is the sidid name for a CIA-timer-driven sample playback
module that is part of (or attached to) the X-Ample / Compotech player.
It is identified by the following fingerprint in sidid.cfg (verbatim):

```
(X-Ample_Digi)
29 1F 8D ?? ?? C8 B1 ?? C9 80 90 ?? 29 3F 8D ?? ?? C8 B1 ?? AA BD ?? ?? 8D 04 DD BD ?? ?? 8D 05 DD AE ?? ?? BD ?? ?? 8D ?? ?? BD ?? ?? 8D ?? ?? A9 ?? 8D 0E DD END
```

---

## Disassembled pattern

Decoding the fingerprint (each `??` is a wildcard byte — any value):

```asm
; --- sample byte decode (5-bit extraction) ---
29 1F           AND #$1F        ; mask lower 5 bits → 32 amplitude levels
8D ?? ??        STA <var1>      ; store processed sample nibble
C8              INY             ; advance stream pointer (Y = offset in (zp),Y)
B1 ??           LDA (<zp>),Y   ; load next byte from sample stream via indirect-Y
C9 80           CMP #$80        ; is this the end-of-sample sentinel ($80)?
90 ??           BCC <not-end>   ; branch if byte < $80 (not end)

; --- secondary nibble / CIA reload value lookup ---
29 3F           AND #$3F        ; mask lower 6 bits
8D ?? ??        STA <var2>      ; store secondary field
C8              INY             ; advance again
B1 ??           LDA (<zp>),Y   ; load next byte (possibly the timer index)
AA              TAX             ; X = timer table index

; --- CIA Timer A programming ---
BD ?? ??        LDA <table1>,X  ; load timer low byte from lookup table
8D 04 DD        STA $DD04       ; *** CIA2 Timer A Low (or CIA1 — see note)
BD ?? ??        LDA <table2>,X  ; load timer high byte
8D 05 DD        STA $DD05       ; *** CIA2 Timer A High

; --- SID voice register writes ---
AE ?? ??        LDX <voice_base>; load current voice register offset
BD ?? ??        LDA <cache>,X   ; load SID register value from cache
8D ?? ??        STA <target>    ; store to SID (indirect)
BD ?? ??        LDA <cache>,X   ; another SID register
8D ?? ??        STA <target>

; --- Start timer ---
A9 ??           LDA #<ctrl>     ; CIA control register value (start, continuous mode)
8D 0E DD        STA $DD0E       ; *** CIA2 Control Register A → start timer
```

**Note on $DDxx vs $DCxx:** $DD04/$DD05/$DD0E are CIA **#2** registers
(CIA2 is at $DD00; CIA1 is at $DC00/$DC04). CIA2 Timer A generates **NMI**
interrupts on the C64; CIA1 Timer A generates **IRQ** interrupts. Using CIA2
for sample playback is the NMI approach — NMIs are non-maskable and
higher priority, giving tighter timing. This is the standard digi approach
for cycle-accurate playback (per the C64 Hacking article gist.github.com/
munshkr/30f35e39905e63876ff7).

---

## CIA timing mechanism (general C64 background)

From https://gist.github.com/munshkr/30f35e39905e63876ff7 (verbatim extracts):

> "The basic approach to interrupt-based playback is to set CIA #2 Timer A
> to generate an NMI every 123 (PAL) or 128 (NTSC) cycles and then vector
> NMI to our playback routine."

> "Frequency value = CPU cycles between samples (approximately 1,000,000 Hz
> ÷ desired sample rate). Example: 141 cycles produces ~7100 Hz playback."

> "It is often important that each sample of a digi is played back at regular
> intervals. If the samples aren't played at a steady speed, extra distortion
> is audible."

> "ROMs switched out to direct NMI vector at $FFFA/$FFFB to custom handler.
> Screen blanked to eliminate VIC cycle-stealing jitter."

**Application to X-Ample_Digi:**
The `BD ?? ?? / 8D 04 DD / BD ?? ?? / 8D 05 DD` sequence writes NEW timer
reload values from a lookup table (indexed by sample data byte X). This is
not a fixed-rate timer — it's a **variable-rate** timer where each sample
byte encodes its own playback duration. This is more sophisticated than
fixed-interval NMI digi; it allows tempo-varying sample playback or
encodes musical pitch.

---

## Sample data format

From the fingerprint pattern:
- `29 1F` extracts bits [4:0] (5 bits → 32 values) as the primary field
- `C9 80` tests bit 7 as an end-of-sample sentinel
- `29 3F` extracts bits [5:0] (6 bits → 64 values) as a secondary field
- Each sample byte encodes: [7]=end flag, [5:0]=some nibble/index
- The alternation between `29 1F` and `29 3F` suggests pairs of fields
  per byte or a two-pass decode

**Likely interpretation:** the sample stream is packed with:
- High bit ($80) = end-of-sample terminator
- Bits [4:0] = one 5-bit sample amplitude (32 levels, not the usual 16)
  OR an index into the CIA timer table
- Bits [5:0] in the second pass = another value (perhaps pitch index)

This is NOT the standard 4-bit $D418 digi — it uses CIA timer programming
(variable rate) and possibly writes to SID voice registers (not just $D418),
making it a more sophisticated hybrid player.

---

## Output target

The fingerprint does NOT show a `STA $D418` write. Instead it writes to
CIA registers ($DD04/$DD05/$DD0E) and SID registers via:
```
AE ?? ??  LDX <voice_base>
BD ?? ??  LDA <cache>,X
8D ?? ??  STA <anywhere>
```
The STA target is wildcard — could be $D418 (master vol) or a voice
register ($D4xx with X offset). This suggests the digi mode may write
amplitude to $D418 AND program CIA timing simultaneously.

---

## Migration scope assessment

**X-Ample_Digi is OUT OF SCOPE for Mode 1 (frame-by-frame) migration:**

1. It programs CIA2 registers ($DDxx), not just $D400-$D418.
2. The CIA timer controls sample playback rate (NMI-based) — the write-log
   stream from siddump will include $DDxx writes which Mode 1 ignores.
3. The correct verification mode is Mode 2 (cycle-exact) as used for
   Chimera digi, or explicit exclusion.
4. No HVSC tunes are confirmed to use X-Ample_Digi in hvsc84.db (0 tunes
   tagged with this variant). If any exist, they are tagged under the
   parent `X-Ample` label.

**What needs investigation before exclusion:**
- The 11 CIA-timed SoNiC tunes (PSID speed-bit set) should be checked
  individually. CIA-timed = VIA tempo control; it does NOT necessarily
  mean they use the X-Ample_Digi sample extension. SoNiC's CIA tunes
  likely use CIA1 for tempo (IRQ-based music) while X-Ample_Digi uses
  CIA2 for sample NMI. These are two distinct CIA uses.
- The RSID `Hawkeye_II.sid` by Markus Schneider (play=$0000, 18,873 bytes)
  is the most likely candidate for X-Ample_Digi usage (self-playing, large
  file, by the engine author). Should be inspected for $DDxx writes.

---

## Comparison to other CIA-digi engines in HVSC

For reference — other HVSC engines using CIA-based digi:

| Engine | CIA registers used | HVSC count |
|---|---|---|
| X-Ample_Digi | $DD04, $DD05, $DD0E | 0 confirmed |
| Comer/NMI_Sample_5 | CIA NMI based | 36 |
| Comer/Sample_Studio | CIA based | 18 |
| Ghost/SampleMon | CIA based | 18 |
| Chimera (Hubbard) | $D401 toggle (1-bit) | 1 |

X-Ample_Digi appears to be a more complex CIA digi than the simple $D418
nibble approaches, using variable CIA reload values (pitch/rate control).

---

## 8580 SID compatibility note

From https://bumbershootsoft.wordpress.com/2022/12/30/digital-sound-playback-on-the-c64/:

> "Standard $D418 digis fail on 8580 chips (lacking DC offset). Workaround
> involves generating sustain voltage via pulse waveforms before volume
> modulation."

X-Ample_Digi does NOT write only to $D418 (it programs CIA and SID voices
via the cache). If it writes to $D400-$D407 (voice 1 frequency/control)
as part of the digi, the 8580 compatibility situation may be different from
standard $D418-only digi. This is unresolved.
