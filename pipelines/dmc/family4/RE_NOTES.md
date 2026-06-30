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

## C16 KNOBS APPLIED (commits f33dde5, 2acfbec) — match 60→86, all principled
The consult (C16) was right — it's emission-order KNOBS, not a rewrite. Traced
the exact per-frame order and landed 3 family-4-gated knobs (family-3 7/7 FULL):
1. **note-on FRQ-skip** — family-4's note-on writes ONLY SR/AD/CTRL (no FREQ=$0)
   on the TICK frame; family-3 writes FREQ=$0000 there. (60→73)
2. **pulse lo/hi SWAP** — family-4 adds $23BC→PW_lo / $23A3→PW_hi; the composer
   does PW_lo+=pulse_hi, so swap op_pulse_lo/hi in FAMILY4_SITES. (73→86)
3. **leadin durctr=2** — family-4 init seeds $17E5,x=2 (family-3 default 1); the
   2-phase ticks on even frames → first note-on at frame 2. durctr=2 + lo_spdctr=0
   = the principled combo (no magic number; was a magic lo_spdctr=4). (match 86)

### ✅ WAVE-SPEED counter — the steady-vs-sweep root cause (commit 5617d66, match 86→92)
write 86 was NOT a duration bug — the orig HOLDS each note 6 frames; the rebuild
SWEPT every frame. Root cause: the family-4 wave-step ($1654) has a per-instrument
wave-SPEED counter ($1845 reload / $1848 counter, gating the $17FD advance), seeded
from **instrument byte 6 ($2293) >> 4** (=5 for inst 8 → advance every 6 frames).
family-3 has no such counter. Three family-4-gated composer knobs (family-3 9/9 FULL):
1. **wave-speed counter** (wavespd/wavespc per-voice; ws_adv holds N frames/step;
   backward-compatible — speed 0 = advance every frame = family-3 unchanged).
2. **note-on no-pre-advance** (family-4 note-on does NO wave step, so the per-frame
   wave_step starts AT the wave_ptr — don't `inc wavepos` on note-on).
3. **vib-disable** (family-4 byte 6 = wave speed, NOT vib_speed; bytes 5/7 unused —
   vibrato is the $F0 sector cmd. Zero the per-instr vib setup, else $50 read as a
   huge vib_speed → +$21 freq jitter, was $2800 vs $27DF). **V1 now byte-exact.**

### ✅✅ NON-FILTER STREAM BYTE-EXACT (match 86 → 13793/13824, ~100%)
A chain of family-4-gated composer knobs took the non-filter stream from 86 writes
to byte-exact (commits 5617d66 → 6ed3ae2; family-3 FULL throughout):
- **speed-gated note-init advance** (1343366, 92→161): the note-init first-step
  must apply the SAME speed-gated advance as ws_adv (not a plain no-advance), else
  a speed-0 drum emits its first wave value twice. Fixed V2's DD00 drum transient.
- **melodic wave-step CARRY propagation** (35ae98d, 161→4651): the orig's $1688
  does `adc $1842` (bias) with NO clc, so the carry from clc/adc(wavefreq+curnote)
  lands in freqlo — +1 when wavefreq+curnote>=256 ($0431 vs $0430). Added
  `adc frqbias,x` (carry+bias) to ws_mel + ni_w_mel. MASSIVE: 161→4651.
- **8-bit pulse counter** (6c2bc31, 4651→5837): family-4 counts pulse steps with
  an 8-bit counter ($1830 vs $23BC[pos+1]), not the family-3 16-bit — V3's PWM
  sweep never advanced under the 16-bit check.
- **vol-override AD=$00** (6ed3ae2, 5837→13793): the vol-override note-on ($1352)
  forces AD=$00 (SR carries the vol level). Unlocked the ENTIRE rest of the stream.
The remaining 31 = capture-tail length. **The musical content is byte-exact.**

### FINAL PIECE — C-2 filter (Jupiter41 still `partial`): $D416-only sweep
Filter is a distinct family-4 subsystem (filtmode $D418=$30 done, cc8cb46):
- **$D416 = $1019(sweep) + $1853(base)** written every play() ($10AD). $1019 is the
  1-byte cutoff swept by the filter program $23D5(add)/$242C(count); $1853 = base.
- **$D415 = $00 ONCE** at init (family-3 writes fclo every frame — skip for fam-4).
- **$F9 <arg>** ($126F) sets BOTH resonance $D417=(arg<<4)|$04 (arg!=0; else 0) AND
  filtmode $1018=arg&$F0. So $D417=$54 ⇐ $F9 $05. ($F9 is 'flt' in the _CMD map.)
- **$F8 is the FILTER-BASE command** for family-4 ($129B sets $1853), NOT 'frq' —
  the V5 _CMD map decodes it as 'frq' (harmless to the freq — composer's frq is a
  no-op — but its value must route to filtbase). NB the filter cmds ($F8 base/$F9
  res+mode) are intertwined; the extract must capture their args for family-4.
DONE (commit 95b5ddc): filtbase var + $F8→filtbase + $D416=fchi+filtbase + 8-bit
filter_run + no per-frame $D415. filtbase works ($D0); MVOL matches; $D415 gone.

### ✅ FILTER FULLY UNDERSTOOD (memwatch of the orig's $1019/$1853/$1803/$184E)
For Jupiter41 the filter is **STATIC**, NOT swept — my sweep machinery was the wrong
model. Ground truth (orig memwatch):
- **$1019 = $5E CONSTANT** — it is the FILE-IMAGE byte at $1019 (mem[$1019]=$5E),
  never touched: V3 stays idle (inst 0) so its filter-program init/sweep never runs.
  $1803 (filterpos) = 0 constant; $184E counts but $242C[1]=0 so it never advances;
  $23D5[0]=0 so even the running add is 0 → $1019 frozen at the file-image $5E.
- **$1853 = $00 → $D0** (set by $F8 $D0, ~frame 3). $1857=$35 (from $F9, filter on).
- **$D416 = $1019 + $1853 = $5E (early) → $5E+$D0 = $2E** (matches orig 00 5E 5E 2E…).
So the orig $D416 seq is 2 distinct values, NOT a 20-value sweep — the ~20 distinct
$D416 values over the whole song are LATER (real filter notes on V3), out of the
first-divergence window.

THE REBUILD BUG: the composer's V3 runs a filter PROGRAM during idle (note-on
filter-init sets filterpos from inst byte4 ($01/$29…), then filter_run sweeps fchi
to $D0) — the orig's idle V3 does none of that ($1019 stays the file-image $5E).

### ✅ FILTER SWEEPS (commit 0a8fa72, full-stream match 85 → 5911 / 11.8%)
CORRECTED the "static filter" error — it was a 16-frame-window artifact (the SAME
short-window trap). Over 80s the orig's $1019 DOES sweep via the DEFAULT filter
program (filterpos walks 0,2,4,6… while V3 stays idle). Three fixes landed:
(1) fchi init = file-image $1019 (f4_fcinit=$5E); (2) force filtflag=0 → V3 stays on
the default program (note-on never resets filterpos from an instrument byte4);
(3) drop note_init2's $D418 (the note-LOAD writes only SR/AD/CTRL — C16). Counter
semantics confirmed: count=0 means 256 frames (the 8-bit counter wraps 255→0, then
0==0 advances) — my `inc filtctr_lo; cmp` handles that.

### ✅ USF FILTER ENCODING FIXED (commit 6e11d60, full-stream 5911 → 7203 / 14.3%)
to_usf `_capture_env_f4` (8-bit walk: add=filterlo[pos], count=filterhi[pos+1], $90
loop) + a matching 8-bit from_usf decode (add→filterlo[2k], count→filterhi[2k+1],
$90→2*lp), both family-4-gated. Roundtrip now FAITHFUL (walk-relevant bytes ==
extract). Plus `filtactive`: the orig's V3 sweep is gated by $1857 (set by $F9 ~frame
2-3), not frame 0 — set in sd_f9, gate filter_run on it (the sweep was ~2 frames
early). $D416 sweep now matches ~388 writes (was 318).

### ✅✅✅ FIRST ~67s OF JUPITER41 MATCH (match 7203 → 56000 / write-exact to ~67s)
This session, after the principle-check: principled per-instrument filter (→31994),
vibrato (→32043), then the vib-reversal $D418 skip (→56000/~67s). The $D418 detail:
the orig skips the per-voice $D418 ONLY on the vib UP-reversal frame ($158F→$1654);
every other oscillating frame WRITES it ($15B0 BNE $1612); the DOWN reversal writes
unless step-doubling ($1812=byte7>>4). So a per-voice `vibrev` flag set on the UP
reversal (the inc-vibdir path), cleared each frame at vib_on entry; write_vol skips
$D418 when vibspd!=0 && vibrev!=0 (commit 8a8e8b8).

### ⛔ V3 OFF-TABLE pulse — FULLY DIAGNOSED MECHANISM (write 56000, ~67s)
**The pulse PERSISTS across notes.** Init handler $13F4: `LDA $2290,y` (instr
byte3 = pulse_ptr) → `BEQ $1411` — the pulse re-inits (pulsepos=byte3, PW from
pulselo/hi[byte3], INC $1800) ONLY when byte3≠0. Instruments with byte3=0 do NOT
reset the pulse, so a single pulse program keeps running across MANY notes (each
note ~48 frames, but the sweep at $07 ran 256+ frames ≈ 5 notes). So the pulse
HORIZON is the inter-reinit interval (frames between byte3≠0 instrument loads),
NOT the note duration (my first note-duration hypothesis was REFUTED: max note
frames = 48, far short of the observed 256+).
**Off-table walk:** pulsepos advances by 2 (odd positions $07→$09→$0B…); the $90
loop markers sit at EVEN positions ($06,$0A) → the walk NEVER loops; it reads the
table's COUNT bytes ($23BC, odd offsets) as pulse adds, ramping PW (PW_hi +$08 for
256 frames at $07, +$00/8 at $09, +$02/240 at $0B…). Long counts → a long sweep.
**Why it doesn't de-fuse:** capturing the off-table sweep with accurate 8-bit
counts over the whole-song reach (16260) walks ~96 phases → de-fused pulse table
= 513 > 256 (`pulse_table_overflow`). A GLOBAL note-bounded reach REGRESSES (match
56000→7416) because (a) some overflowing instruments are off-table too and the
16-bit fallback's garbage-count truncation only ACCIDENTALLY matches their short
notes, and (b) the shared-table re-pack shifts other instruments' data.
**Correct fix (non-trivial, multi-part):** per-instrument re-init horizon from a
play simulation (frames between byte3≠0 loads on each voice) + DROP the 16-bit
fallback for family-4 (family-4 counts are ALWAYS 8-bit → 16-bit is wrong). With
the right horizon each off-table sweep is ~6–12 phases (fits). Multiple long
off-table sweeps may still need a larger/separate sweep representation. This is
the residue-triage "architectural-limit-last" class.
**Scope (80-member sample):** off-table sweep is the SINGLE biggest build-blocker
(pulse_table_overflow 8 + sweep_too_long 8 + filter_table_overflow 4 = 20/80).

### 🔧 PLAY-SIM HORIZON ATTEMPT (2026-06-30) — fixes V3, regresses V2; PARKED
Built the per-voice re-init horizon (max frames between byte3≠0 note-ons; sim walks
each orderlist's sector seq twice, tracking cur_inst via 'snd', cur_dur via 'dur',
reinit at 'note' when instruments[cur_inst].pulse_ptr≠0). **Jupiter41 horizon=618.**
Used as the pulse-capture reach (8-bit, no 16-bit fallback). RESULT (verdict
`compare_instruction_stream`): the horizon-8-bit capture is CORRECT for V3 (inst 17,
ptr 2): captures `(+32,224),(+32,2),(+2048,256),…` — the +$08 PW_hi phase that the
16-bit `+32-forever` collapse missed (= the 56000 divergence). BUT it REGRESSES V2
(inst 14/15, ptr 19) from 56000→7416: inst 14/15's 8-bit env is
`(+0,1),(-512,256),(+0,23),(+0,132),(+8192,256)`; its re-packed START is verified
CORRECT (pulselo[115]=$08), so the break is NOT the start. Hypothesis: inst 14/15's
play-interval is SHORT, so its 16-bit collapse (`-512 forever`, only the 1st phase
ever plays) was fine; the 8-bit's later phases only diverge if the COMPOSER's
pulse-reinit timing (byte3≠0 detection) differs from the orig, making inst 14/15's
program play past its 1st phase. NEXT: verify the composer's byte3≠0 reinit matches
the orig exactly (it may reinit on the wrong events), OR apply horizon-8-bit ONLY to
the instrument whose 16-bit diverges (inst 17), keeping 16-bit for short-interval
off-table insts (inst 14/15). Prototype code is in the session transcript; not
committed (would regress). Pulse re-pack uses `add_env` (16-bit layout) for family-4
even though counts are 8-bit — works because count_lo coincides with the 8-bit read
for counts ≤256; a dedicated `add_env_f4_pulse` (8-bit) may be cleaner.

### ⚠️ TOOLING CAVEAT: find_first_divergence vs the verdict
For Jupiter41, `find_first_divergence` reports "frame 2 / position 22" but the VERDICT
(`compare_instruction_stream`) gives match=56000. The 22 is its `match_post_init`
metric, MISLEADING when orig/rebuild INIT LENGTHS differ (drops a fixed init prefix →
mis-aligns the play streams). TRUST the flat `match` (56000) = the off-table pulse.
Lesson: for family-4 (different init length), use `compare_instruction_stream`'s flat
`match`/`is_full`, not find_first_divergence's post-init position.
**The regression IS localizable (self-correction):** the ad-hoc flat counter agrees
with the verdict (both 56000 committed / 7416 horizon), so flat position 7416 IS the
divergence: orig writes $D40A=$08 (V2 PW hi) where the rebuild writes $00 — the
rebuild MISSES a V2 PW-hi=$08 write. (A memwatch of $D40A shows $00 for 14s, but that
is TRAP A — the orig writes $08 then $00 within the SAME frame; the frame-boundary
snapshot only keeps the final $00. The write-log is right; don't trust register
snapshots for within-frame order.) **PRECISE ROOT (confirmed):** dumped inst 3/4/13/14/15 start bytes in BOTH committed
(ptab=119) and horizon (ptab=163) builds — pulselo[ptr]=$08 in ALL (start NOT
corrupted; de-fusion shift REFUTED). So the regression is MID-SWEEP, not the note-on.
The decisive logic: committed's inst 14/15 = 16-bit collapse `(+0,1),(-512,65536)` =
`-512 forever` and matches the orig to 56000; horizon's 8-bit = `(+0,1),(-512,256),
(+0,23),(+0,132),(+8192,256)` and matches only to 7416. The VERDICT prefers the
16-bit. THEREFORE the orig's inst 14/15 (ptr 19) actually ramps `-512` for a LONG
time, and **`_capture_env`'s 8-bit off-table walk MIS-MODELS ptr 19** (it claims the
walk leaves the -512 step after 256 frames into +0/+8192, but the orig stays on
-512). Contrast ptr 2 (inst 17), where the 8-bit walk is CORRECT (recovers the real
+$08 PW_hi sweep = the 56000 fix). So different off-table pointers walk differently
and `_capture_env` matches some (ptr 2) but not others (ptr 19) — the advance/count/
$90-loop/parity model is wrong for ptr 19. **THE blocker:** make `_capture_env`'s
off-table walk bit-exact to the orig's pulse engine ($14B4 advance + the
$23A3/$23BC count/loop semantics) for ALL pointers, verified against a memwatch of
the orig's PW per off-table pointer. The play-sim horizon is correct and necessary
(bounds the table) but insufficient alone — the capture's off-table WALK must match
first. Horizon prototype in the session transcript; NOT committed.

### 📊 FAMILY-4 WIDE-SAMPLE CENSUS (80/686 members, 2026-06-30) — 0 FULL
First batch through `dmc_v5_family_batch.py` after this session's gated knobs
(filter/vibrato/wave-speed/$D418-skip). Build path routes (`dmc_v5_config` →
`_family4_config`). **0/80 FULL** — family-4 is early-stage with 5 blocker classes:
| blocker | n | type | tier |
|---|---|---|---|
| off-table pulse/filter (pulse_table_overflow 8 + sweep_too_long 8 + filter_table_overflow 4) | 20 | build | unblock-builds |
| unknown sector cmd $F0 / $EF | 16 | build | unblock-builds (decode $F0/$EF) |
| partials (diverse: init-order $D400/$D406, $D418=$0F order, later) | 35 | write-stream | fix-effects |
| USF parse error (stray `}` token) | 3 | build | unblock-builds (USF-gen escape bug) |
| misc unsupported (player_code_mismatch 3, capture_loop 2, trailing 1) | 6 | build | — |
**Dependency-ordered plan (residue-triage):**
1. **unblock-builds**: (a) decode sector cmds $F0/$EF (16, likely a quick decoder
   addition — check disasm sector handler); (b) fix the USF-gen `}` escape bug (3);
   (c) off-table pulse/filter horizon (20, the hard one — see mechanism above).
2. **fix-effects**: the 35 partials — START with the 6× frame-0 init-order
   `(0,0)/(6,0)` ($D400 vs $D406 = freq-lo vs SR ordering at note-load) + the
   `$D418=$0F` ordering cluster (shared init-write-order knob, like family-1's
   nextvoice_write_order / master_vol_every_note). These are cheap shared levers.
3. Jupiter41 (the rep) is itself a partial blocked at ~67s by the off-table pulse;
   first ~67s write-exact. Its init+play matches (the session's knobs landed).

### (superseded) NEXT (write 56000, ~67s): V3 OFF-TABLE pulse program
V3 ramps PW_lo += $20 (matched), then the orig advances to PW_hi += $08 (→$2460→
$2C60→$3460, holds), but the rebuild's pulse loops $5C↔$5E (spurious re-packed $90).
ROOT: family-4's pulse COUNT is 8-bit ($23BC[pos+1]); _capture_env read it 16-bit
(folding garbage $23A3[pos+1] into the count), inflating cum so `reach` truncated the
program early → re-pack capped it with a $90 loop. Added count8bit (commit 6a840e3) —
correct for non-off-table family-4 PWM. BUT Jupiter41's V3 pulse pointer is OFF-TABLE
(no real $90 loop; program runs past its end into a terminal hold), so the 8-bit walk
runs past _PHASE_CAP=48 → falls back to the 16-bit bound → still the spurious loop.
The off-table pulse (C2/C11) needs the off-table playbook: capture the bytes the orig
plays past the nominal program end (the terminal hold), analogous to freq_overrun.
Then verify FULL SONG.

### (superseded) V3 pulse program advance
V3 ramps PW_lo += $20 (matched: 1C20→1C40→1C60), then the orig advances to a step
adding $08 to PW_hi (→$2460→$2C60→$3460, then holds for a new note), but the rebuild
stays on the $20 low-add step (1C80→1CA0→1CC0). The pulse program doesn't advance to
the high-byte-add step in the rebuild — a per-(note/instrument) pulse-program count or
extraction detail (NOT a lo/hi swap — the low-add applies correctly to both). Then the
tail + DOWN-reversal step-doubling generalization. VERIFY FULL SONG (run_member).

### (historical) PRINCIPLED FILTER + VIBRATO (match 7203 → 32043 / 63.7%)
PRINCIPLED filter fix (commit 2a457aa) — checked against USF §7 + ledger C1/C8 (the
"verbatim table + orig byte4 indices" idea I was about to write was the §7 LEAK;
rejected after re-reading the principle). Each family-4 instrument's filter program
is an 8-bit (add,count) SweepEnvelope (_capture_env_f4 has_start=True: start=
filterlo[byte4], phases from byte4+1), de-fused per instrument (C8), re-packed by
add_env_f4; filter_ptr is the composer's OWN re-packed index — NO raw table, NO engine
indices in USF. V3 re-init now fires. Composer: filter init is V3-ONLY (CPX #$02); the
cpx clobbered Z so `beq ni_nofilt` skipped `sta filterpos` — reload filtflag (THE
unlock: 7203→31994). VIBRATO (commit 49b2da5): family-4 HAS per-instrument vibrato
(note-on $138F, state machine $157C); same byte map as family-3 EXCEPT vibspd =
byte6 & $0F (high nibble = wave speed). vibdel=byte5 (onset), vibwidth=byte7&7.
31994→32043. NEXT (write 32043): the orig's oscillating-vib path ($158F) bypasses the
per-voice $D418 ($1651) — naive "skip when vibspd!=0 && vibdel==0" OVER-skips; needs
the exact $1612-vs-$1651 condition. Then vib step-doubling ($1812=byte7>>4) + tail.

### (historical) "sweep timing lag" (write 7203) = the missing per-instrument filter RE-INIT
NOT a timing bug. Traced via filterpos walk: the orig walks 0(intro)→02..18 (default
program), then a V3 note RE-INITS the filter — filterpos = byte4($01)+1 = $02,
$1019 = filterlo[$01] = $23D5[$01] = $84 (= the $54 = $84+$D0 jump). V3 plays inst-0
notes (byte4=$01) that re-init; "force filtflag=0" disabled this so the rebuild only
runs the default program (caps at 7203). Reverting force=0 makes it WORSE (→101):
the rebuild re-inits from the WRONG byte4 ($51 = inst 8, not $01 = inst 0).

ROOT CAUSE (deeper than timing): the USF roundtrip **re-packs the filter table and
re-assigns every instrument's `filter_ptr`** to a re-packed index. For family-4 ALL
instruments share the single $23D5/$242C program and index it at their ORIG byte4 —
the re-pack destroys those indices. My _capture_env_f4 made the default PROGRAM
faithful but not the instrument INDICES into it (extract inst-0 filter_ptr=$1F vs
orig byte4=$01; the rebuild plays inst 8 filter_ptr=$51). The non-filter stream MASKS
this (inst 8's ad/sr/wave/pulse == inst 0's, so the notes match; only the filter
byte4 differs).

FULL FIX (a USF-representation change, bigger than a knob): carry the family-4 filter
table as a SHARED verbatim resource at orig indices + preserve each instrument's orig
byte4 (`filter_ptr`), bypassing the from_usf re-pack. Then the per-instrument re-init
reads the right byte4 and the re-init path (write 7203+) matches. Also handle the
intro/idle (don't re-init during the 256-frame intro before V3's first real note).
Current stable state: force filtflag=0, match 7203 (default program only).

### (historical) "sweep timing lag" framing — superseded by the re-init finding above:
$1853 is constant ($D0); $1019 ACCUMULATES across the program's loop (pos 30 → pos 2,
no reset) — the orig sweeps $1019 UP to $84 by the first loop, but the rebuild LAGS
(still ~$36): the rebuild's sweep takes MORE frames to reach the $90 loop. Counts are
faithful (roundtrip-verified), so suspect: the count=0→256 intro vs the orig, the
filtactive start frame vs orig's $F9 frame, or a per-step count-application off-by-one
accumulating over ~350 frames. NOT the USF encoding (now faithful) — a residual
filter_run timing detail. Then verify FULL SONG (run_member).

### (historical) ROOT CAUSE that the above fixed: USF roundtrip corrupted the program
The EXTRACT is correct (m.filter == raw $23D5/$242C). But to_usf→from_usf
RE-SYNTHESIZES `filt` from `usf.default_filter` using the family-3 **16-bit
(rate, frames) phase encoding** (from_usf.py ~L197-207): each phase → an ADD pair
(rate.hi,rate.lo) + a count pair (frames.hi,frames.lo) + a $90 loop. Family-4's
program is **8-bit (add=$23D5[pos], count=$242C[pos+1])** — so the roundtrip shifts
it and inserts a spurious $90 (144). The composer then walks a corrupted program →
filterpos stuck / wrong sweep. **Diagnosis: EXTRACT m.filter[0..10] matches raw;
ROUNDTRIP m.filter differs (prepends (0,0), inserts (144,0)).**
FIX: carry the family-4 filter program FAITHFULLY through USF — either a typed
(add,count) default-filter encoding for family-4, or the raw program prefix as an
f4 field. Then the existing filter_run (8-bit counter, default program) sweeps
correctly. VERIFY FULL SONG (run_member), not a short window.

### EARLIER REMAINING (superseded by the above):
1. **fchi init = file-image $1019** (mem[base+$19]=$5E) for family-4, NOT lo_fchi($00).
   Capture as an f4 param (analogous to f4_filtmode). LEFT_FCHI := that for family-4.
2. **Don't run V3's filter program during idle** for family-4 (the note-on filter-init
   + filter_run sweep must be no-ops when V3 is idle) — so fchi stays the static $5E.
   Then $D416 = $5E + filtbase matches. NB later real V3 filter notes (the ~20-value
   sweep region) will then need the program to actually run — verify the full song,
   not just the first window, before declaring FULL.

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
