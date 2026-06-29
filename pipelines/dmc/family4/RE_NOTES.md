# DMC V5 family-4 — reverse-engineering notes (Phase A, in progress)

**Rep:** `DEMOS/G-L/Jupiter41.sid` (Victory/Tempest 1997). **686 SIDs**
(fingerprint `68901f5d7f01f574f73d57aea07f7c2d3cae5b93`, member list in
`tmp/v5_family4_members.json`). The V5 factory already DETECTS this family
(`_detect_v5` → `layout='family4'`) and rejects it with `family4_branch`.

**Verdict so far:** family-4 is a distinct V5 *version* — it SHARES the V5
track/sector data model with family-3 (Katusha) but has a DIFFERENT player
(timing, per-voice dispatch, filter) and a DIFFERENT instrument format. ~0.31
Jaccard to family-3. A real migration, but the family-3 extract/compose
infrastructure is largely reusable with parametrization + the new instrument
decode + the new player mechanics.

Seed disassembly: `pipelines/dmc/family4/disassembly.s` (auto-traced from the
3 jump-table entries; 1759 reachable bytes; awaiting full hand annotation).

## Jump table ($1000, 3 entries — family-3 has 2)
- `$1000: JMP $1040` — init
- `$1003: JMP $1095` — play
- `$1006: JMP $10D3` — **3rd entry** (per-voice `JSR $1654` ×3 — a SID-write /
  all-notes pass; family-3 has no 3rd entry). Not called by play(); purpose TBD
  (maybe a separate "silence/refresh" entry the demo calls).

## init ($1040)
- Copy the per-song record from **`$1A40` + song*8** (8 bytes/song): 3 voice
  track pointers → `$17D9,x`(lo)/`$17DC,x`(hi); then 2 trailing bytes → `$10BF`
  and **`$101A`** (the 4th = a speed/param; `$101A` is read in the effects).
- Clear work RAM `$17DF..$1857` to 0; per-voice `$17E5,x=2`, `$1009,x=2`
  (duration / active seeds).
- Clear `$D400-$D417`; set `$D404/$D40B/$D412 = $08` (test bit on all voices).

## play ($1095) — 2-PHASE TIMING (the big mechanical difference)
```
push $FA/$FB            ; family-4 uses zero-page $FA/$FB (family-3: $F8/$F9)
DEC $1016 ; BMI alt     ; $1016 = a 2-phase frame toggle
  normal:  JSR $1373 ×3 ; MAIN voice routine (effects, every frame)
  alt:     $1016=1 ; JSR $10E1 ×3  ; TICK voice routine (advance, on underflow)
filter:  $D416 = $1019 + $1853     ; ONLY $D416 (hi) — NO $D415 write
pull ; rts
```
- `$1016` toggles between MAIN (`$1373`) and TICK+MAIN (`$10E1`→falls into
  `$1373`). `$10E1` decrements the duration counter `$17E5,x` and fetches the
  next track/sector event when it expires; otherwise it just `JMP $1373`.
- **Filter: family-4 writes ONLY `$D416`** (cutoff hi = `$1019 + $1853`), never
  `$D415`. family-3 writes both. `$1853` is set by the `$F8` sector cmd;
  `$1019` is the running/base cutoff.

## TICK / track walk ($10E1) — track format SAME as family-3
Track = stream of **sector#** (`< $80`) + track markers:
- `$FF` → INY; loop target = next byte → `$17DF,x`; reload.
- `$FD nn` → track transpose `$17EE,x = nn`.
- `$FC nn` → track transpose `$17EE,x = -(nn)` (EOR $FF, +1).
- `$FE` → voice stop (`$1009,x = 0`; `JMP $1654`).
- sector# → `$FA/$FB = ($2209[sec], $224B[sec])` (**sector pointer table**:
  lo `$2209`, hi `$224B`), then walk the sector from pos `$17E2,x`.

## SECTOR commands ($1150 dispatch; `< $80` = note → `$1314`)
Mostly the SAME bytes as family-3 (✅), with family-4-specific ones (⚠):
| byte | family-4 | family-3 |
|---|---|---|
| `$F0` | ⚠ **wave/vib note setup** (`& $07` = vib width → `$1856`; freq`<<`width; hi nibble → `$1809,x` wave?) | (none) |
| `$F3 nn` | `$17F1,x = nn` (vol/param) | vol |
| `$F4` | toggle `$1821,x` bit0 (gate_tie) → gate path | gate_tie |
| `$F5` | toggle `$17F4,x` (EOR $FF) | gate_toggle |
| `$F8 nn` | `$1853 = nn` (filter cutoff add → `$D416`) | frq (filter base) |
| `$F9 nn` | nn`<<4`\|`$04`→`$D417` (res) ; nn`&$F0`→`$1018` | flt (type\|res) |
| `$FA s,t` | slide: spd `$17F7,x`, target `$17FA,x = t+transpose` | slide |
| `$FB s,a,b` | glide: spd `$17F7,x`, A `$1012,x = a+tr`, B `$17FA,x = b+tr` | glide |
| `$FC nn` | ⚠ `$17EB,x = nn` + sector-pos (NOT snd) | snd |
| `$FD nn` | dur `$17E8,x = nn` | dur |
| `$FE [note][$FF?]` | gate: reload dur, note → `$1827,x`; trailing `$FF`=sector end (reset pos, INC track) → `JMP $1654` | gate |
- TODO: confirm `$F1`/`$F2` (srr/adr) and `$F6`/`$F7` (fade) presence; map the
  note handler `$1314` and the `$1654` SID-write; whether `$FC`=instrument-select.

## Instruments — DIFFERENT layout (`$2292` parallel arrays)
The MAIN routine `$1373` reads instrument fields from **`$2292/$2293/$2294,Y`**
(Y = `$184B,x`, the per-voice instrument index — NOT scaled by 8):
- `$2293,Y & $0F` → `$1809,x` (a count/len; if 0 skip)
- `$2292,Y` → `$1806,x`
- `$2294,Y & $F0 >>3` → `$1812,x` ; `$2294,Y & $07` → `$1856` (vib width)
- so instruments are **parallel byte arrays** at `$2292`(+0), `$2293`(+1),
  `$2294`(+2) indexed by id, vs family-3's contiguous 8-byte records. Full
  field map TODO (more arrays likely at `$2295+`, `$2209` overlaps the sector
  ptr lo — need the operand-site reads in `$1373`/`$1314`).

## Migration delta vs family-3 (what the port needs)
1. **Factory dispatch**: accept `layout='family4'` (already detected); base = load.
2. **Relocated table addresses**: song `$1A40`, sector-ptr `$2209/$224B`,
   instruments `$2292`, freq table (`$1779` seen as note→? lookup), wave/pulse/
   filter tables — all at family-4 addresses (dataflow-extract the operand sites).
3. **New instrument decode** (parallel `$2292` arrays, nibble-packed).
4. **New player mechanics in the composer**: the `$1016` 2-phase timing, the
   single-`$D416` filter (`$1019+$1853`, no `$D415`), the `$F0` wave/vib cmd,
   `$FC` semantics, the 3rd JT entry.
5. **Sector decode**: reuse the family-3 walker; reparametrize the command map
   (most bytes match; override `$F0`/`$FC`).

## Remaining Phase-A work
- [ ] note handler `$1314` + effects `$1373` (vib/glide/pulse/wave/filter writes)
- [ ] `$1654` (the per-voice SID write — freq/PW/ctrl)
- [ ] full instrument field map (`$2292`+ arrays)
- [ ] freq table base + wave/pulse table bases + `$F0` semantics
- [ ] confirm the `$1016` 2-phase = multispeed-2 vs tempo (measure vs writelog)
- [ ] census the 686 for sub-variants (are play+$95 members uniform?)
