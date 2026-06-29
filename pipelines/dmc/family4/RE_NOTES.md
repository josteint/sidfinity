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

## Effect chain ($147B steady → $1654 wave-step) — standard V5, relocated
Per voice, every frame (the MAIN routine $1373 note-init falls through to, and
$147B runs for, the steady path), in ORDER:
1. **FILTER program** (V3 only, x==2, if $1857 active): pos $1803; add table
   **`$23D5`**, count **`$242C`**, `$90` loop. `$1019 += $23D5[pos]` (cutoff acc).
2. **PULSE program** (all voices): pos $1800,x; lo-add **`$23BC`**, hi-add
   **`$23A3`**, count, `$90` loop. PW accum `$182A,x`(lo)/`$182D,x`(hi).
3. **GLIDE/SLIDE**: speed `$17F7,x`, target `$17FA,x`; ramp freq accum
   `$183C,x`/`$183F,x` toward `$1779[target]`; arrival snaps. → `$1654`.
4. **WAVE step `$1654`**: pos `$17FD,x`; ctrl table **`$2325`**, arg table
   **`$2364`**, `$90` loop ($2325[p]==$90 → p=$2364[p]). Drum (ctrl & $08):
   freq-hi direct = `$2364[p]`. Melodic: arp = `$2364[p] + curnote`; freq lo =
   `$1719[arp] + $1842,x` ($EF offset), freq hi = `$1779[arp]`. wave-step
   duration `$1848`/$1845`. Then GATE/hard-restart ($17E5==1 → SR=0).

## SID WRITE ORDER (the writelog-exact target — $16F0, per voice y=$100C,x)
```
$D400,y = $1818,x + $183C,x   ; FREQ LO  (table freq + glide accum lo)
$D401,y = $181B,x + $183F,x   ; FREQ HI
$D402,y = $182A,x             ; PW LO    (pulse accum lo)
$D403,y = $182D,x             ; PW HI
$D404,y = $181E,x AND $1821,x ; CTRL     (wave ctrl AND gate mask $1821)
```
Voices V1→V2→V3 each emit that 5-write block (via $1654); then play() writes
`$D416` once (cutoff hi). Plus: AD/SR ($D405/$D406) at note-on + $F1/$F2 cmds;
$D417 (res) at $F9. Freq tables: **lo `$1719`, hi `$1779`** (96-entry, V5).
$EF = a per-voice freq-lo BIAS ($1842,x, added in the wave-step).

## Timing ($1016): 2-frame note tempo, NOT multispeed
$1016 resets to 1 (fixed) and DECs each play(): MAIN/TICK alternate every frame,
so the NOTE-ADVANCE (tick) runs every OTHER frame — a fixed 2-frame tempo tick;
note durations ($17E8/$17E5) carry the rhythm. **SID writes happen EVERY frame**
(both paths call $1654), so it is a normal 50 Hz VBLANK tune — `verify_dmc`'s
standard per-frame writelog applies (no CIA / no per-IRQ). [confirm by writelog.]

## CENSUS of the 686 (fingerprint bucket)
`_detect_v5` over all 686: **635 = `family4`** (ALL with play offset +$95 —
uniform), 36 = `v5` (the family-3 layout — borderline fingerprints that already
build via the family-3 path), 15 = rejected (None). Load addrs: 577 @ `$1000`,
~58 relocated (`$E000`/`$A000`/`$5000`/`$0FD0`/...). So family-4 is UNIFORM (one
play variant) with a modest relocation spread → the family-2 relocation+knobs
playbook fits cleanly. Migration target ≈ 635.

## Phase-A status: ✅ COMPLETE
Fully mapped (init, play+2-phase timing, tick/track, sector command map,
note/note-on, 8-byte instrument record, the FULL effect chain [filter/pulse/
glide/wave], the SID write ORDER, freq tables, $EF/$F0). Timing CONFIRMED
VBLANK (PSID speed bit 0; SID writes every frame; verify_dmc applies). Census
done (635 uniform). Verdict: family-3's V5 format relocated + a different
player — the family-2 relocation+knobs playbook. Ready for Phase B.

## Phase B — ✅ DONE (commit 88f18bc): factory dispatch + extract
- `DMCV5Config.family4` flag + `FAMILY4_SITES` (the 12 operand-site PCs,
  verified 12/12 against Jupiter41). `_family4_config` builds the config
  (base=load; sites + delta). The V5 extract reuses the shared data decode —
  **Jupiter41 extracts cleanly** (1 subtune, 19 instr, 96 freq, pulse/filter/
  wave tables) and the **FULL pipeline runs end-to-end** (extract→USF→compose→
  build→verify). family-3 V5 unaffected (6/6 FULL sanity). 32/34 sample build.

## Phase C — STARTED (diagnostics done; work list below)
Building Jupiter41 with the family-3 composer: data is right, player write
stream differs. Three concrete issues found (in divergence order):

**C-1. LEADIN curnote leftover (the first divergence).** orig V1 freq `$0C8F`
(= freq_table[43]) vs rebuild `$011C` (= freq_table[1]) at frame 1 — BEFORE the
first note gates. `$1012` (curnote) is NOT in the init-cleared range ($17DF..),
so the engine reads the FILE-IMAGE leftover ($1012=43 for Jupiter41) as the idle
freq during the leadin; the composer's idle curnote differs. The first GATED
note (60) decodes correctly. → capture the family-4 curnote leftover ($1012,x,
3 bytes) like the V5 `lo_notes` idle handling; composer primes them.

**C-2. FILTER** (the ~27k extra writes + $D418): family-4 writes **only $D416**
(8-bit cutoff = running `$1019` + base `$1853`); composer writes both $D415 &
$D416 (11-bit). And `$D418 = $101A (mvol fade) | $1018 (filter MODE from $F9 &
$F0)` — orig $3F (mode $30), rebuild $0F. → composer knob: $D416-only 8-bit
cutoff path + the $D418 mode bits + the $101A master-vol-fade.

**C-3. TIMING** ($1016 2-phase note tempo): note-advance every other frame vs the
family-3 speed counter. PROGRESS:
- ✅ speed=1 extracts correctly → the family-3 composer ticks every 2 frames
  (= the 2-phase rate). No timing knob needed for the RATE.
- ✅ `lo_spdctr` was read from `$1013` = family-4's V2 CURNOTE ($24=36), not a
  speed counter → a bogus 36-frame startup delay. ZEROED for family-4 (correct;
  member-independent). [`lo_fchi/fclo/filtmode` stay — C-2's filter domain.]
- ⏳ REMAINING: the LEADIN LENGTH. orig's first note gates ~frame 2 (write ~60);
  with lo_spdctr=0 the rebuild gates at write ~24 (too early). The family-4 init
  seeds the per-voice DURATION counter `$17E5,x = 2`; the composer seeds
  `durctr=1`. → composer knob: seed durctr=2 for family-4 (test; the leadin is
  sensitive — verify it lands the first note at the orig's frame, not over/under).

### C-1 STATUS: ✅ done (commit cc63144) — non-filter match 25→60 on Jupiter41.

## ⚠️ C-3 REAL BLOCKER (found 2026-06-29): the 2-phase splits the WRITE ORDER
Sweeping lo_spdctr (0..4) maxes the non-filter match at ~63 then forks — and the
fork is a WRITE-ORDER difference, not values/leadin. At the first-note frame
(orig writes, one frame): **V1 note-on (SR/AD/CTRL), V2 note-on, THEN the
wave-steps (freq/PW/ctrl) for the voices** — i.e. family-4 BATCHES the note-on
pass separately from the wave-step pass (the 2-phase: the TICK path does
note-on+RTS without wave-stepping; the wave-step/$1654 happens in a separate
pass). The family-3 composer does **per-voice INTERLEAVED** (V1 note-init+
wave-step, V2 …). Writes 56-62 match (V1 note-on identical) then the order
diverges at write 63 (orig=V2 note-on $D40D, rebuild=V1 freq $D400).
**→ This is ledger [[C16]] (per-frame WRITE-ORDER differs). CONSULT 2026-06-29
REFRAMED it: NOT a wholesale composer rewrite — PARAMETRIZE the composer's
EMISSION order (precedent: FC `nextvoice_write_order`, a config tuple of the
register-write order). The CORE TENET licenses "re-arranged effect-chain
emitters". The family-4 analogue = a composer knob (gated on m.family4) that
splits the per-voice emit into a NOTE-ON pass (SR/AD/CTRL for fetching voices)
then a WAVE-STEP pass (FREQ/PW/CTRL).**
PREREQ (C16 methodology — TRACE FIRST, don't guess scope): finish tracing the
exact $1095/$10E1/$1373/$147B/$1654/$10D3 call graph and write the LITERAL
register sequence for 2-3 frames (which voices note-on vs wave-step on the MAIN
vs the TICK/$1016 frame; the role of the 3rd JT entry $10D3=$1654×3). Then the
emission-order knob is bounded. C-2 (filter) is easy once the order is right
(Jupiter41 filter near-static: skip $D415, $D418 mode $30, $D416=$2E).

### Reference (the original first-divergence dump for posterity)
Building Jupiter41 with the family-3 V5 composer gives the right DATA but the
family-3 PLAYER write stream. First divergence + the deltas to fix:
1. **Filter**: orig `$D418=$3F` (filter MODE bits $30 set) vs rebuild `$0F`;
   and the rebuild emits ~27k EXTRA writes = the family-3 `$D415` (cutoff lo)
   it writes every frame that family-4 NEVER writes. → composer knob:
   `$D416`-only filter + the family-4 `$D418` filter-mode derivation (`$1018`
   from `$F9`).
2. **Timing**: the 2-phase `$1016` note tempo (advance every other frame) vs
   the family-3 speed counter → the note stream re-times. → composer timing knob.
3. Confirm the note/freq decode once filter+timing align (the frame-1 freq
   diff $0C8F vs $011C is likely the timing offset, not a decode bug).
4. **Verdict**: `verify_dmc`. Carve a Jupiter41 reference for masked dispatch.
5. Wide batch over the ~635.
