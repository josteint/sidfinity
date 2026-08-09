<!--
source_url: local: tmp/dmc_hunt/sidid/sidid.cfg ; tmp/dmc_hunt/player-id/config/sidid.cfg ;
            tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg (+ sidid_old_but_works.cfg, sidid_newer_but_does_not_work.cfg)
            cross-checked against real HVSC #84 binaries.
fetched_via: local read + local disassembly of HVSC #84 SID binaries
fetch_date: 2026-06-13
author: SIDId signature DB (Cadaver / HVSC / DeepSID maintainers); disasm by SIDfinity session
content_date: signatures undated (HVSC-era); manual is 2019-ish (Swagerman "20 years" note)
reliability: HIGH for the signature strings (verbatim from three local cfg copies) and the
             6502 decode (disassembled directly from HVSC binaries — ground truth, not inferred);
             MEDIUM for the variant-population counts (derived by masked byte-search over the
             6351 HVSC tunes the DB classifies as Music_Assembler, not by running sidid itself).
-->

# Music Assembler — sidid signature analysis

## The signatures (verbatim from the local sidid.cfg copies)

sidid syntax (authoritative, from `tmp/dmc_hunt/DeepSID/utility/sidid_100/readme.txt`
and `tmp/dmc_hunt/player-id/doc/Signature_File_Format.txt`):
- `??` = wildcard for one byte (nibble wildcards are not possible).
- `AND` and `&&` are the **SAME token** (`&&` is the v2-format spelling of `AND`):
  "skip any number of bytes, then continue matching when the next run is found."
  It is a **gap/skip operator WITHIN a single signature** — NOT a logical AND
  of two independent signatures.
- `END` terminates a signature (optional in v2; a signature otherwise ends at
  end-of-line — useful to spread one signature over multiple lines).
- **Multiple signature LINES under one player name are OR'd** — if ANY one
  matches, the player is reported.
- `(Name/Variant)` parenthesised form = a sub-signature for a particular
  version/variant; it is OR'd in alongside the base.

So `(Music_Assembler/MC)`'s `EE 19 D0 20 ?? ?? 4C  AND  BD..9D` is ONE signature:
"find the IRQ-ack stub, then (skipping bytes) find the data-decode loop after it."

```
Music_Assembler
  BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60 B9 ?? ?? 85          END

(Music_Assembler/MC)            # variant attributed to MC (Marco Swagerman)
  # --- "old_but_works" form (DeepSID): the data-decode loop alone ---
  BD ?? ?? 85 ?? BC ?? ?? C8 C8 B1 FA C9 FF D0 02 A0 00 98 9D          END
  # --- "newer / does_not_work" form: IRQ-ack stub  &&  data loop ---
  EE 19 D0 20 ?? ?? 4C  &&  BD ?? ?? 85 ?? BC ?? ?? C8 C8 B1 FA C9 FF D0 02 A0 00 98 9D
```

All copies carry the SAME base signature (and it is identical to the upstream
`github.com/cadaver/sidid/sidid.cfg`, verified by direct fetch 2026-06-13).
They differ only in the `/MC` sub-signature:

| cfg copy | `/MC` form |
|---|---|
| `sidid/sidid.cfg`, `DeepSID/.../sidid.cfg`, upstream cadaver/sidid | `EE 19 D0 20 ?? ?? 4C  AND  BD..9D` |
| `player-id/config/sidid.cfg` | `EE 19 D0 20 ?? ?? 4C  &&  BD..9D` (same meaning, v2 spelling) |
| `DeepSID/.../sidid_old_but_works.cfg` | `BD..9D` only (data loop, NO IRQ-ack prefix) |
| `DeepSID/.../sidid_newer_but_does_not_work.cfg` | `EE 19 D0 20 ?? ?? 4C  &&  BD..9D` (author flags broken) |

`AND`/`&&` here is the within-signature byte-skip, so all the "current" copies'
`/MC` form is identical in meaning: "IRQ-ack stub, then the data loop." The
DeepSID maintainer's own filenames are the lead: the form REQUIRING the IRQ-ack
prefix is labelled **"does_not_work"**, while the **data-loop-alone form is
"old_but_works"**. The IRQ-ack stub `EE 19 D0 20 ?? ?? 4C` (`INC $D019` /
`JSR ??` / `JMP`) is NOT present in every MA tune — packers that relocate the
player out of an inline raster-IRQ wrapper (or ack the IRQ differently) drop it.
Prepending it shrinks the `/MC` hit rate from ~71% to ~30% (counts below).

## What the matched bytes DO (disassembled from a real HVSC tune)

Disassembled from `hvsc85/MUSICIANS/W/Waz/Quadraped_Tearaways_3.sid`
(load $1000), first base-sig hit at $1091. X = voice index (0/1/2, a
stride into the per-voice state byte-tables). This is the **per-voice
sequence-step advance / end-of-pattern handler** — the heart of the player's
"self-disassembling data" loop:

### Base signature `BC ?? ?? C0 FE D0 09 BD ?? ?? 29 FE 9D ?? ?? 60 B9 ?? ?? 85`
```
$1091  BC 8D 10   LDY $108D,X    ; Y = per-voice current step-control byte
$1094  C0 FE      CPY #$FE       ; is it the $FE STOP sentinel?
$1096  D0 09      BNE $10A1      ; no -> go process the step
$1098  BD 84 10   LDA $1084,X    ; yes (STOP): load the per-voice flag byte
$109B  29 FE      AND #$FE       ; <-- the "masked store": clear bit 0
$109D  9D 84 10   STA $1084,X    ;     (gate/active flag off for this voice)
$10A0  60         RTS            ; done
$10A1  B9 4F 1D   LDA $1D4F,Y    ; (continue) pointer-table LO, indexed by Y
$10A4  85 FA      STA $FA        ; -> $FA  (set up ($FA) indirect data ptr)
       B9 21 1D   LDA $1D21,Y    ; pointer-table HI
       85 FB      STA $FB        ; -> $FB
       BC 81 10   LDY $1081,X    ; Y = per-voice data-stream cursor
```

Reading register/offset implications:
- **X = voice (0/1/2)**; the per-voice state lives in parallel byte-tables at
  fixed offsets from the player base: `$1081` (cursor), `$1084` (flags),
  `$108D` (step-control), `$10E6` (another per-voice byte set in the MC loop).
- **`$FE` = STOP sentinel** for a voice's step-control byte; hitting it does a
  `AND #$FE` masked clear of bit 0 of the voice flag (turn the voice's gate/active
  bit off) and `RTS`.
- **`($FA)` is the indirect data-stream pointer**, rebuilt every step from a
  pair of pointer tables: LO at `$1D4F`, HI at `$1D21` (these absolute addresses
  are the wildcarded bytes — they relocate with the player). The Y index selects
  which sequence/segment pointer to load.

### `/MC` data-loop `BD ?? ?? 85 ?? BC ?? ?? C8 C8 B1 FA C9 FF D0 02 A0 00 98 9D`
Same tune, hit at $1198 — this is the **fetch-next-stream-byte with wrap**:
```
$1198  BD BC 14   LDA $14BC,X    ; per-voice ptr-hi -> $FB (rebuild ($FA) ptr)
$119B  85 FB      STA $FB
$119D  BC 87 10   LDY $1087,X    ; Y = per-voice byte-index into the stream
$11A0  C8         INY            ; advance...
$11A1  C8         INY            ; ...by 2 (steps are >1 byte wide)
$11A2  B1 FA      LDA ($FA),Y    ; peek next stream byte
$11A4  C9 FF      CMP #$FF       ; $FF = LOOP-WRAP sentinel
$11A6  D0 02      BNE $11AA
$11A8  A0 00      LDY #$00       ; wrap index back to 0
$11AA  98         TYA
$11AB  9D 87 10   STA $1087,X    ; store advanced index
$11AE  B1 FA      LDA ($FA),Y    ; read step byte 0 -> step-control ($108D,X)
       9D 8D 10   STA $108D,X
       C8         INY
       B1 FA      LDA ($FA),Y    ; read step byte 1 -> $10E6,X
       9D E6 10   STA $10E6,X
```
So in the stream: **`$FF` = loop-to-start sentinel**, **`$FE` = stop sentinel**
(checked by the base sig). Steps are read 2 bytes at a time via `($FA),Y` with
Y as the per-voice cursor. This is the packed "self-disassembled" data the
manual describes.

The IRQ-ack stub gating the newer `/MC` form is `EE 19 D0  / 20 ?? ??  / 4C`
= `INC $D019` (ack VIC raster IRQ) / `JSR play` / `JMP` (back to the IRQ tail) —
present only when the saved file ships its own raster IRQ wrapper.

Confirmed concretely in `hvsc85/MUSICIANS/O/OPM/Sid_Slam.sid` (OPM = co-author
Oscar Giesen), load $C000, stub at $C018:
```
$C018  EE 19 D0   INC $D019      ; ack VIC raster IRQ
$C01B  20 21 C0   JSR $C021      ; <-- play = base($C000) + $21  (matches the doc!)
$C01E  4C ?? ??   JMP ...        ; tail
```
This is the direct verification that **play = base+$21**: the JSR target is
exactly base+$21. The PSID-header play address points at this wrapper, not at
$C021 itself.

## Population: base vs /MC across HVSC #84 (6351 Music_Assembler tunes)

Skip-join byte-search (correct `AND`/`&&` = skip-and-continue semantics) over
every HVSC tune the DB classifies `Music_Assembler`:

| signature | matches | share |
|---|---|---|
| **base** `BC..85` | **6351 / 6351** | **100%** — universal MA fingerprint |
| `/MC` "old_but_works" (data-loop `BD..9D` alone) | **4495 / 6351** | 70.8% |
| `/MC` "newer/does_not_work" (`EE 19 D0 20 ?? ?? 4C` AND data-loop) | **1929 / 6351** | 30.4% |
| matched by NEITHER base nor MC-loop | 0 / 6351 | 0% |

Confirms the DeepSID maintainer's filenames empirically: requiring the inline
`INC $D019 / JSR / JMP` raster-IRQ stub before the data loop only fires on ~30%
of MA tunes, whereas the data-loop-alone form catches ~71%. **The base signature
is the one to key on for classification — present in 100% of MA tunes.** The
`/MC` sub-signatures are version sub-classifiers (presence of an inline raster
wrapper), NOT the primary detector. ~29% of MA tunes match the base but neither
`/MC` form (no inline raster wrapper AND a data loop that differs enough from
`BD..9D` to miss) — a third structural family worth noting.

## Wrapper / packer-layout variants (PSID init/play offset signature)

The PSID-header init/play addresses do NOT point at the documented internal
player entry (init = base+$48, play = base+$21). They point at the SAVED-FILE
wrapper (relocator + IRQ installer). Histogram of (init_off, play_off) relative
to `min(init,play)` over the 6351 tunes:

| init offset | play offset | count | reading |
|---|---|---|---|
| +$00 | +$03 | 3338 | wrapper-A: init at block start, play 3 bytes in |
| +$27 | +$00 | 2747 | wrapper-B: play at block start, init at +$27 |
| +$2C | +$00 | 43 | wrapper-B variant |
| +$00 | +$12 / +$13 / +$21 / +$39 | ~75 | misc relocated wrappers |
| +$8F00 / +$8FC0 | +$00 | ~23 | high-memory ($Bxxx-ish) relocations |

The internal $48/$21 player entry the docs cite is reachable only after the
wrapper relocates the block; it is not the PSID-visible address. Treat the
two dominant layouts (A: init+$00/play+$03 = 3338; B: init+$27/play+$00 = 2747)
as the two principal packer families for a future migration — expect a
GT2-style A/B version-group split here.

## Cross-engine collision (important for classification)

DeepSID's `php/_update/special_updating.sql` (local) manually RE-tags two
Nebula tunes that sidid mis-identifies:
```
/* Replace 'Music Assembler' with 'Padua's Music Mixer' which used the same player */
UPDATE files SET player = "Padua's Music Mixer" WHERE id = 32528  -- MUSICIANS/N/Nebula/Catman.sid
UPDATE files SET player = "Padua's Music Mixer" WHERE id = 32543  -- MUSICIANS/N/Nebula/Flodder.sid
```
"Padua's Music Mixer" reuses the MA player, so the base signature matches it
too. Any MA migration's verification set should be aware that a small number of
"MA" hits are actually Padua's Music Mixer derivatives.

## Leads to follow

- **Base signature = the per-voice sequence-step handler, NOT init.** The
  matched code at $1091 (+ the MC loop at $1198) is the live play-time data
  decoder. It directly exposes the runtime write-model state layout: per-voice
  byte-tables (cursor/flags/step-control/extra) at fixed offsets from the player
  base, an indirect `($FA)/($FB)` stream pointer rebuilt each step from LO/HI
  pointer tables, `$FE` = voice-stop sentinel (does `AND #$FE` gate-off), `$FF`
  = stream loop-wrap. This is the highest-value lead for the per-frame SID
  write-model — seed `disassembly.s` from one of the canary tunes starting at
  the base-sig hit and walk outward to the $D4xx stores.
- **Two principal packer/wrapper families** by PSID init/play offset:
  (A) init+$00 / play+$03 = 3338 tunes; (B) init+$27 / play+$00 = 2747 tunes.
  Plus ~23 high-memory ($8F00-ish offset) relocations and a long tail. Expect a
  GT2-style A/B/C version-group split; classify these before designing extract.
- **`/MC` sub-signature ≠ a different player — it's a wrapper marker.** Its
  distinguishing prefix `EE 19 D0 20 ?? ?? 4C` is an inline raster-IRQ ack
  (`INC $D019 / JSR play / JMP`). ~30% of MA tunes carry it inline; ~71% match
  the data-loop alone. The `/MC` split likely tracks "shipped with inline IRQ
  wrapper" vs "relocated/CIA-driven/PSID-driver-supplied IRQ." Worth correlating
  `/MC`-match against the (A)/(B) packer-layout families.
- **The ~29% that match base but NEITHER `/MC` form** (no inline raster wrapper
  AND a data loop differing from `BD..9D`) are a third structural family —
  isolate and disassemble one to see whether the data loop is genuinely a
  variant or just relocated past the wildcards.
- **Cross-engine collisions to carve out of any MA verification set:**
  (1) Padua's Music Mixer (Nebula/Catman, Nebula/Flodder per DeepSID's manual
  re-tag); (2) the `sidid.nfo` "Harald Rosenfeldt / Music Assembler V3.1"
  NAME — a different 1989 product; do not trust the nfo attribution (see
  `deepsid_and_web_findings.md`).
- **Confirm play=base+$21 / init=base+$48 internally**, not from PSID headers:
  the headers point at the saved-file wrapper. `OPM/Sid_Slam.sid` already shows
  `JSR base+$21` as the play call inside the raster IRQ. Verify the +$48 init
  entry the same way on a canary before coding extraction.
