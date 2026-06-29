# DMC V5 family-4 — reverse-engineering notes (Phase A, in progress)

**Rep:** `DEMOS/G-L/Jupiter41.sid` (Victory/Tempest 1997). **686 SIDs**
(fingerprint `68901f5d7f01f574f73d57aea07f7c2d3cae5b93`, member list in
`tmp/v5_family4_members.json`). The V5 factory already DETECTS this family
(`_detect_v5` → `layout='family4'`) and rejects it with `family4_branch`.

**Verdict (revised after mapping the note handler):** family-4 is family-3's V5
DATA FORMAT, RELOCATED, driven by a DIFFERENT PLAYER. It shares the track
format, the sector-command map (nearly 1:1 — see table), AND the 8-byte
instrument record format. The ~0.31 Jaccard is the PLAYER code (different
timing, filter, per-voice dispatch, zero-page), NOT the data model. So this is
closer to the **family-2-vs-V4 relocation+knobs** playbook than to a from-scratch
engine: the family-3 EXTRACT is largely reusable with relocated addresses; the
real work is (a) factory dispatch + dataflow the relocated table bases, (b) two
extra sector commands ($EF, $F0), (c) the composer player mechanics (the $1016
2-phase timing + $D416-only filter). Much more tractable than the initial scope.

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

## SECTOR commands ($1150 dispatch; `< $80` = note → `$1314`) — NEARLY == family-3
| byte | family-4 | family-3 | match |
|---|---|---|---|
| `$EF nn` | ⚠ `$1842,x = nn` (per-voice param; TBD) | (none) | NEW |
| `$F0 [n]` | ⚠ wave/vib note setup (`n&$07`=vib width→`$1856`; freq`<<`width; hi nib→`$1809,x`) | (none) | NEW |
| `$F1 nn` | `$D406,y = nn` (SR, y=$100C,x voice base) | srr | ✅ |
| `$F2 nn` | `$D405,y = nn` (AD) | adr | ✅ |
| `$F3 nn` | `$17F1,x = nn` (vol override) | vol | ✅ |
| `$F4` | toggle `$1821,x` bit0 (gate_tie) | gate_tie | ✅ |
| `$F5` | toggle `$17F4,x` (gate_toggle) | gate_toggle | ✅ |
| `$F6 nn` | `$1855 = nn` (fade_out) | fade_out | ✅ |
| `$F7 nn` | `$1854 = nn` (fade_in) | fade_in | ✅ |
| `$F8 nn` | `$1853 = nn` (filter cutoff add → `$D416`) | frq | ✅ |
| `$F9 nn` | nn`<<4`\|`$04`→`$D417` (res); nn`&$F0`→`$1018` | flt | ✅ |
| `$FA s,t` | slide: spd `$17F7,x`, target `$17FA,x = t+tr` | slide | ✅ |
| `$FB s,a,b` | glide: spd `$17F7,x`, A→`$1012,x`, B→`$17FA,x` (+tr) | glide | ✅ |
| `$FC nn` | **snd**: `$17EB,x = nn` (inst#; ×8 → `$184B,x` instr index) | snd | ✅ |
| `$FD nn` | dur `$17E8,x = nn` | dur | ✅ |
| `$FE [note][$FF?]` | gate: reload dur, note → `$1827,x`; trailing `$FF` = sector end (reset pos, INC track) → `JMP $1654` | gate | ✅ |
| (else) | INC sector pos, skip | — | |

## note handler ($1314) + note-on ($1323)
- `$1314`: `note + transpose($17EE,x) → $1012,x` (curnote). If `$17F4,x` (gate-
  toggle flag) set → `JMP $11D0` (skip note-on, just gate); else `$1323`.
- `$1323` note-on: 2nd byte → `$1827,x`; inst index `$17EB,x ×8 → $184B,x`; if
  no vol-override (`$17F1,x`==0): load AD `$228D[i*8]` → `$D405,y`, SR
  `$228E[i*8]` → `$D406,y`; `$D404,y = $09` (gate+test); `$1815,x = $09`
  (note-start flag for `$1373`).

## Instruments — 8-byte records at $228D (SAME format as family-3, relocated)
`$17EB,x` (the `$FC` inst#) `×8` = the record index `$184B,x`. Fields (base+i*8):
- `$228D` +0 = **AD** ; `$228E` +1 = **SR** ; +2,3,4 = TBD
- `$2292` +5 = **WV ptr** ; `$2293` +6 = **PU ptr** (low nibble in `$1373`) ;
  `$2294` +7 = **FL ptr / vib** (`&$F0>>3`, `&$07`=vib width)
So NOT parallel arrays — it's the standard V5 8-byte instrument record at base
`$228D`. (My first read mistook base+offset[i*8] for parallel arrays.)

## Instrument 8-byte record ($228D base) — full field map (from $1373 note-init)
| off | addr | field | use |
|---|---|---|---|
| +0 | `$228D` | AD | → `$D405` at note-on |
| +1 | `$228E` | SR | → `$D406` (low nibble OR'd with vol-override hi when `$F3` set) |
| +2 | `$228F` | → `$17FD,x` | (param; vib/pw?) |
| +3 | `$2290` | program ptr | if ≠0: indexes `$23A3`/`$23BC` tables → `$182D,x`/`$182A,x` |
| +4 | `$2291` | V3-only | (filter ptr; read only when `x==2`) |
| +5 | `$2292` | wave ptr | → `$1806,x` |
| +6 | `$2293` | low nib = wave count → `$1809,x`; hi nib → `$1845/$1848,x` (pulse) |
| +7 | `$2294` | hi nib `>>3` → `$1812,x` (pulse ptr); low 3 bits → vib width `$1856` |

## KEY TABLE ADDRESSES (Jupiter41; dataflow these per-member)
- song/orderlist record table: **`$1A40`** (+song*8)
- sector pointer table: lo **`$2209`**, hi **`$224B`**
- instrument records: **`$228D`** (8 bytes each)
- freq table: **`$1779`** (curnote → freq, `$180C`)
- wave/pulse program tables: **`$23A3`**, **`$23BC`** (indexed by instr +3 byte)
- filter cutoff: running `$1019` + add `$1853` (`$F8` cmd) → `$D416`

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

## Phase-A status: SUBSTANTIALLY COMPLETE
Mapped: jump table, init, play (2-phase timing + filter), tick/track walk,
the full sector command map (≈1:1 with family-3 + `$EF`/`$F0`), note handler,
note-on, the 8-byte instrument record, and the key table addresses. Verdict
corrected to "family-3 format relocated + different player" (tractable).

### Remaining Phase-A detail (smaller; the standard V5 effect chain, relocated)
- [ ] steady effects `$147B` (per-frame vib/glide/pulse/wave accumulation)
- [ ] `$1654` per-voice SID write (freq `$1812`+vib `$180C`/`$180F` → `$D400/1`,
      PW `$1827` → `$D402/3`, ctrl `$1815`/wave → `$D404`) — confirm the write
      ORDER (the writelog-exact target)
- [ ] `$EF`/`$F0` semantics (the two family-4-only sector commands)
- [ ] `$1016` 2-phase: measure vs writelog — is it multispeed-2 (play() runs the
      tick path every other frame) or a tempo halving? Affects the verify path.
- [ ] census the 686 for sub-variants (uniform play+$95? table-base spread?)

## Phase B/C plan (the family-2 playbook)
1. **Factory**: stop rejecting `layout='family4'`; build a `family4` config
   (base=load; dataflow the table operand sites above).
2. **Extract**: reuse the family-3 V5 extract with relocated bases + the
   `$EF`/`$F0` commands; same track/sector/instrument decode.
3. **Composer**: a family-4 variant of the V5 engine — the 2-phase `$1016`
   timing, `$D416`-only filter, `$FA/$FB` zero-page. Reuse the rest.
4. **Verdict**: `verify_dmc` (engine-neutral). Carve a Jupiter41 reference for
   the masked-identity dispatch (like `dmc4_family2_player_1000.bin`).
5. Wide batch over the 686.
