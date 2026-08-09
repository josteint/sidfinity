# HardTrack Composer — SIDId signature analysis

**Provenance**
- Author: SIDfinity research session (sidid signature cluster), 2026-06-13.
- Engine: HardTrack Composer (Brush + Longhair / Milosz Ignatowski, Elysium/Parados, Poland, 1992).
- Local sidid configs inspected (READ-ONLY):
  - `tmp/dmc_hunt/sidid/sidid.cfg` (line 833)
  - `tmp/dmc_hunt/player-id/config/sidid.cfg` (line 855)
  - `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` (line 808)
- Player image disassembled (READ-ONLY): `pipelines/hardtrack/docs/src/sdk/extracted/RELEASE_NOTES.bin`
  — despite the filename this is the compiled **V1.0 player image** ($1000 load,
  embedded string `PLAYER 1.0 BY LONGHAIR/ELYSIUM`; JMP table `4C 60 10 / 4C D8 10`
  at the top = init $1060 / play $10D8).
- Real HVSC SIDs cross-checked: `hvsc85/MUSICIANS/B/Bzyk/Good_World.sid` (V1.0),
  `hvsc85/MUSICIANS/S/Shogoon/Tribute_to_Laxity.sid` (V1.1 / V1.0+).
- HVSC population: `hvsc84.db` opened READ-ONLY (`file:...?mode=ro`).

---

## 1. The signature

All three local sidid.cfg copies carry **exactly one** HardTrack_Composer signature,
byte-identical across copies:

```
0A 0A 8D ?? ?? 68 29 F0 85 FB AD ?? ?? 29 0F 05 FB 1D ?? ?? 8D ?? ?? 8D 17 D4
```

`?? ` = single-byte wildcard (low/high byte of a relocation-dependent absolute address).
The signature ends on `8D 17 D4` = **STA $D417** (the SID filter-resonance / filter-routing
register), which is the anchor.

Provenance of the signature itself: cadaver's `sidid.nfo` lists
`HardTrack_Composer  AUTHOR: Milosz Ignatowski (Longhair)
REFERENCE: https://csdb.dk/release/?id=74928`. No signature count is documented there
(the .nfo is author/reference metadata only), but the .cfg has a single entry.

## 2. Where it matches in the player

In the V1.0 player image (`RELEASE_NOTES.bin`, $1000-based) the signature matches
inside the per-voice **note-on filter-routing setter**. The four consecutive `0A` (ASL A)
in the player mean the signature regex anchors on the **last two** ASLs; here is the
full routine, hand-disassembled:

```
; ---- PATH A: note-on / instrument selects filter routing ($135D) ----
$135D  48        PHA              ; save the instrument's filter byte
$135E  29 0F     AND #$0F         ; low nibble  = resonance level (0..F)
$1360  0A        ASL A            ; shift it...
$1361  0A        ASL A
$1362  0A        ASL A            ; <-- sig: 0A 0A
$1363  0A        ASL A            ; ...into the HIGH nibble (×16)
$1364  8D 7A 15  STA $157A        ; <-- sig: 8D ?? ??   (temp / SMC operand)
$1367  68        PLA              ; <-- sig: 68         restore filter byte
$1368  29 F0     AND #$F0         ; <-- sig: 29 F0      keep its HIGH nibble...
$136A  85 FB     STA $FB          ; <-- sig: 85 FB      ...the filter MODE bits (LP/BP/HP + V3OFF)
$136C  AD 1F 10  LDA $101F        ; <-- sig: AD ?? ??   current $D417 shadow ($101F V1.0)
$136F  29 0F     AND #$0F         ; <-- sig: 29 0F      keep the LOW nibble = filter-ENABLE bits (FILT1/2/3 + EXT)
$1371  05 FB     ORA $FB          ; <-- sig: 05 FB      merge in this inst's mode bits
$1373  1D 91 16  ORA $1691,X      ; <-- sig: 1D ?? ??   merge per-VOICE filter-enable bit (X = voice index)
$1376  8D 1F 10  STA $101F        ; <-- sig: 8D ?? ??   write back the shadow
$1379  8D 17 D4  STA $D417        ; <-- sig: 8D 17 D4   commit to SID
```

(The `STA $157A` at $1364 is the temp the shifted resonance nibble is stored to; it is
read a few instructions later by the resonance-write path — note `$157A` is not actually
re-read by the snippet shown, it is the SMC/temp operand the editor's resonance code uses.
The signature's structural meaning does not depend on it.)

There is a **second** STA $D417 a few bytes later — the note-off / clear-routing path
(NOT part of the signature, shown for completeness):

```
; ---- PATH B: note-off / clear this voice's filter routing ($1394) ----
$1394  AD 1F 10  LDA $101F        ; shadow
$1397  3D 94 16  AND $1694,X      ; AND with per-voice CLEAR mask (X = voice) -> drop this voice's FILTn bit
$139A  8D 1F 10  STA $101F        ; write back
$139D  8D 17 D4  STA $D417        ; commit
```

## 3. What the signature computes (the write model it reveals)

It builds the single byte written to **$D417** (`RES/FILT`: bits 7-4 = resonance,
bits 3-0 = FILT1/FILT2/FILT3/FILTEX routing) from three independent sources, with a
persistent software shadow:

1. **Resonance** comes from the instrument's filter byte LOW nibble, shifted to the high
   nibble (the `AND #$0F` + 4× ASL). i.e. the editor stores resonance 0..F in a nibble and
   the player promotes it to $D417 bits 7-4.
2. **Filter MODE** is NOT in $D417 at all — `AND #$F0` keeps the high nibble of the
   filter byte and stashes it in $FB; that high nibble actually holds the **filter-enable
   contribution for THIS instrument** that gets OR-ed into the low nibble of the shadow
   (see step 3). (The LP/BP/HP mode + V3-off bits live in $D418, set elsewhere; $D417's
   low nibble is pure routing.)
3. **Per-voice routing** — the shadow `$101F` (V1.0) keeps the accumulated $D417 byte
   across all three voices. The routine takes the shadow's current LOW nibble (the other
   voices' enable bits), OR-s in this instrument's bits ($FB) and the per-voice enable bit
   from table `$1691,X` (X = voice 0/1/2), then writes the merged byte back to both the
   shadow and $D417.

**Key takeaway for the USF write model:** $D417 is a *shared, accumulated* register —
HardTrack maintains a software shadow ($101F in V1.0 / $101E in V1.1) and each voice's
note-on OR-s its filter-enable bit in; each voice's note-off AND-s its bit out via a
per-voice mask table (`$1691,X` to set, `$1694,X` to clear). Resonance is whole-chip
(written from whichever voice last triggered a filtered instrument). A faithful USF
rebuild must therefore model $D417 as the running OR/AND of per-voice routing bits plus
the last-set resonance nibble, NOT as a per-voice register snapshot. The two tables
`$1691,X` (set-mask) and `$1694,X` (clear-mask) are the routing-bit-per-voice constants.

## 4. Version taxonomy — does the single signature cover V1.0 AND V1.1?

**Yes.** The single signature matches **1170/1170** HVSC HardTrack_Composer SIDs (full
sweep, regex over the SID data image). It covers both versions because every byte that
*differs* between versions falls on a `??` wildcard (an absolute address operand). Direct
comparison of the signature region in real SIDs:

| field | V1.0 (`Good_World.sid`) | V1.1 / V1.0+ (`Tribute_to_Laxity.sid`) |
|---|---|---|
| sig CPU address | `$1362` | `$1387` (routine shifted ~$25 later) |
| `STA $157A` resonance temp | `$157A` | `$15A4` |
| `LDA/STA $D417 shadow` | **`$101F`** | **`$101E`** |
| `ORA $xxxx,X` set-mask table | `$1691,X` | `$16C4,X` |
| matched bytes (with wildcards) | `0a 0a 8d 7a 15 68 29 f0 85 fb ad 1f 10 29 0f 05 fb 1d 91 16 8d 1f 10 8d 17 d4` | `0a 0a 8d a4 15 68 29 f0 85 fb ad 1e 10 29 0f 05 fb 1d c4 16 8d 1e 10 8d 17 d4` |

So the signature is version-agnostic AND relocation-agnostic by construction. Its three
fixed anchors — `0A 0A` (resonance promotion), `29 F0 85 FB ... 29 0F 05 FB` (the
nibble split/merge), and `8D 17 D4` (the $D417 commit) — are stable opcode runs; everything
else is wildcarded.

**Consequence: the signature cannot distinguish V1.0 from V1.1.** Version splitting in
HVSC must use other evidence (e.g. the shadow address $101F vs $101E, the routine offset,
or the rare embedded `PLAYER V1.x` string — present in only 4/1170 SIDs). See
`deepsid_population_and_versions.md`.

## 5. Cross-check: the source artifacts do NOT contain the signature

`PLAYER_V1.0.bin` (5309 B) and `PLAYER_V1.1.bin` (5646 B) report bogus load addresses
($A909, $1309) and contain **no `STA $D417` byte sequence at all** — they are not
executable images. They are the editor's relocatable/source-object form (interleaved
`09 ?? 83 ??` link structure, embedded strings `PLAYER V1.0 BY LONGHAIR` / `PLAYER V1.1
BY LONGHAIR`). The directly-disassemblable V1.0 image is `RELEASE_NOTES.bin`; V1.1 was
confirmed from a real HVSC SID (above). The 337-byte size growth V1.0→V1.1 in the source
form matches the routine-offset shift ($1362→$1387) seen in the compiled players —
V1.1/V1.0+ adds the multispeed (4×/6×) machinery.

## Leads to follow

- Confirm $D417 shadow address as the cheap V1.0/V1.1 discriminator across all 1170
  (V1.0 → `AD 1F 10`, V1.1 → `AD 1E 10` in the sig region) — gives a clean per-SID version
  tag without needing the embedded version string.
- Disassemble PATH B fully + the resonance-write path that consumes `$157A`/`$15A4` to
  nail down exactly how resonance reaches $D417 bits 7-4 (the `STA $157A` is an SMC/temp
  operand whose reader wasn't in the captured window).
- Extract the `$1691,X` set-mask and `$1694,X` clear-mask tables (3 bytes each) from a
  representative SID — these are the per-voice FILTn routing-bit constants needed for the
  USF $D417 write model.
- The SDK `PLAYER_V*.bin` are relocatable-object format; if a clean executable V1.1 player
  image is wanted for side-by-side disasm, relocate one out of a $1000 HVSC V1.1 SID.
- Web/DeepSID player-name string for HardTrack tunes is not exposed via the public page;
  DeepSID derives its player label from sidid, so the displayed name == `HardTrack
  Composer` (sidid id `HardTrack_Composer`). Confirm against a live DeepSID query if the
  exact display casing matters.
