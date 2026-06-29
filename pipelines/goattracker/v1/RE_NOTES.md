# GoatTracker V1 — reverse-engineering notes

Engine: original GoatTracker 1.x (Cadaver / Covert Bitops). HVSC engine
`GoatTracker_V1.x`, 1,359 SIDs (1,347 single-SID + 12 dual-SID to exclude).
**Dominant player = V1.5** (delayed-wave `cmp #$08`, testbit hard restart).

**Ground truth: `pipelines/goattracker/docs/src/v1_player1_v153.s`** (the full
free-licensed V1.5 playroutine). This file maps that source to the packed-SID
data layout, the write stream, and the USF representation. Read the source
alongside; do NOT re-derive. V2 docs (`player_algorithm.md` etc.) are a Rosetta
stone, not authoritative.

---

## 1. Player skeleton (from v1_player1_v153.s)

```
$base+0  jmp init
$base+3  jmp play
init:    sta init_adc+1 ; asl ; adc init_adc+1 ; sta mt_chnloop+1 ; rts
         ; → mt_chnloop init operand = subtune*3 (deferred; real init on 1st play)
play:    save $fc/$fd; FILTER exec (global); write $D416/$D417/$D418;
         then for X in 0,7,14: channel exec; restore $fc/$fd; rts
```

Per-channel exec (X = 0/7/14 = SID voice offset AND channel-var stride):
- **First play after init** (`mt_chnloop+1` >= 0): clear sequencer vars, set
  songnum = subtune*3 + channel, tempo=$05, tick=gatetimer+2, force
  pattptr=ENDPATT + newnote, → loadregs. (This is the deferred song init.)
- **`mt_noinit`**: `dec mt_chntick`; ==0 → tick0; <0 → reload tempo (funktempo
  if tempo<2) then tickN; else tickN.
- **tickN**: if waveptr!=0 run wave-table exec; else run the active continuous
  fx (arp/portaup/portadown/toneporta/vibrato via `mt_tickntbl`).
- **tick0**: decode newfx byte (= inst*8 | cmd); set instrument (if inst!=0)
  + active fx; run the tick-0 cmd (`mt_tick0tbl`); then if newnote pending →
  new-note init (load instrument: pulse, wave ptr, AD, SR, testbit ctrl $09,
  filter); else continue to wave/pulse exec.
- **pulse exec** → **gate-timer check** (`cmp #GATETIMER`; if tick==gatetimer →
  fetch new note from pattern) → **loadregs** ($D400/$D401 freq, $D404 wave&gate).

### Write stream per channel per frame (the verification target)
Filter (once/frame, global): `$D416` cutoff, `$D417` ctrl, `$D418` type|vol.
Per voice: `$D402/$D403` pulse (on new-note + during pulse modulation),
`$D405/$D406` AD/SR (on new-note + hard restart), `$D404` ctrl ($09 testbit on
new-note frame, then waveform&gate), `$D400/$D401` freq (every frame via
loadregs). Order matters within frame (gate edges, testbit).

---

## 2. Packed-SID data layout (virtual → relocated)

Player source virtual bases (greloc relocates each independently):

| Virtual | Label | Content |
|---|---|---|
| `$4000` | `mt_instXX` | Instruments, **8 bytes/record, stride 8** (record N at $4000+N*8). |
| `$4100` | `mt_wavetbl` | Wave-program left column (waveform $08-$FF / delay $00-$07). |
| `$4200` | `mt_notetbl` | Wave-program right column (note: rel if bit7 clear → +chnnote; abs if bit7 set). |
| `$4300/$4400` | `mt_songtbllo/hi` | Orderlist pointer table, indexed by songnum = subtune*3+channel. |
| `$4500/$4600` | `mt_patttbllo/hi` | Pattern pointer table, indexed by pattnum. |
| `$4700` | `mt_filttbl` | Filter table, **4 bytes/entry** (entry at +ptr; ptr is a byte offset, multiple of 4). Step 0 reserved (funktempo reuses bytes 2-3). |
| (in player) | `mt_freqtbllo/hi` | **96-entry freq table — PLAYER CONSTANT** (baked in, identical every tune). Not per-tune. |

**Instrument record (8 bytes):**
| Off | Field | Meaning |
|---|---|---|
| 0 | AD | → $D405 on new-note |
| 1 | SR | → $D406 on new-note (unless cmd 6 sustain-override active) |
| 2 | pulse | new-note PW: `(byte&$F0)`→$D402, `(byte&$0F)`→$D403 (hi nibble) + sets dir |
| 3 | pulsespd | bit0 = **0→do hard restart / 1→no HR**; `&$FE` = pulse modulation speed (0 = no pulse mod) |
| 4 | pulselow | pulse-$D403 low bounce limit |
| 5 | pulsehigh | pulse-$D403 high bounce limit |
| 6 | filter | filter-table ptr (0 = don't change filter on new-note) |
| 7 | wave | wave-program start ptr (1-based into wavetbl/notetbl; 0 = no wave) |

**Wave program** (per-instrument slice of the shared wavetbl/notetbl, starting
at `inst.wave`): each step = (left=wavetbl[y], right=notetbl[y]).
- left `$00-$07`: **delay** (compare to arpcount; hold the step N frames, no wave change).
- left `$08-$FF`: **waveform control byte** → chnwave (ANDed with gate at $D404).
- right: note. bit7 set → absolute note `&$7F`; clear → relative `+chnnote &$7F`.
- **loop/end**: when `wavetbl[y+1] == $FF`: if `notetbl[y+1]==0` → loop stays
  (target 0); else new ptr = `notetbl[y+1] + inst.wave - 2` (loop target is
  RELATIVE to the instrument's wave start). Else advance by 1.
- A frequency load resets arpcount (`mt_arpfreqresetvib`).

**Filter table entry (4 bytes at filttbl+ptr):**
| Off | Static-mode (byte0 != 0) | Mod-mode (byte0 == 0) |
|---|---|---|
| 0 | $D417 ctrl (res+routing) | 0 = modulation marker |
| 1 | $D418 type|vol (passband) | filttime (mod duration) |
| 2 | $D416 cutoff (0 = skip cutoff) | filtcutoffadd (signed cutoff step/frame) |
| 3 | next-step ptr (0 at entry 0 = stop) | next-step ptr |

---

## 3. Orderlist (song) format — `mt_sequencer`
Bytes at songtbl[songnum]:
- `$00-$CF`: pattern number → set pattnum, play it.
- `$D0-$DF` REPEAT: repeat the next pattern `byte-$CF` extra times.
- `$E0-$EF` TRANSDOWN / `$F0-$FE` TRANSUP: set channel transpose = `byte-$EF`
  (signed: $E0=-16 … $FE=+15), applied to subsequent notes.
- `$FF` LOOPSONG: next byte = restart position index; jump there.

## 4. Pattern format — `mt_getnewnotes`
Bytes at patttbl[pattnum]:
- `$00-$5F`: note **with command** (3-byte row): note (0-$5D, $5E=KEYOFF,
  $5F=REST) + fx byte (inst*8|cmd) + fxparam byte.
- `$60-$BF`: note **without command** (1-byte row): note = `byte-$5F`.
- `$C0-$FE`: **packed rest** (rest for `256-byte` frames; counter incs to wrap).
- `$FF` ENDPATT: end → forces sequencer to fetch next orderlist entry.

Note→newnote: `note + chntrans`. KEYOFF clears gate ($FE). Toneporta (cmd 3)
suppresses hard restart + gate-off (legato). Hard restart (if inst pulsespd
bit0==0): write HR-AD→$D405, HR-SR→$D406, gate off.

## 5. The 8 commands (low 3 bits of the fx byte)
| # | tick0 | tickN | Param meaning |
|---|---|---|---|
| 0 | arp setup | arpeggio | `$XY`: X(bits4-6)=2nd offset, Y(bits0-3)=3rd offset; cycles root→+X→+Y, 2 frames each. Suppressed while wave-program runs. |
| 1 | idle | portaup | speed (16-bit via `mt_makespeed`: param<<2) |
| 2 | idle | portadown | speed |
| 3 | toneporta (set target, legato) | toneporta | speed ($00 = tie/instant) |
| 4 | idle | vibrato | `$XY`: X(&$F0)=speed/half-cycle, Y(&$0F)=depth |
| 5 | set filter ptr | idle | filter-table ptr |
| 6 | set SR ($D406) | idle | SR value (also sets sustain-override so new-note won't reload SR) |
| 7 | tempo/fader/timing | idle | global tempo; `$80-$EE`→channel tempo `&$7F`; `$EF`→timing mark; `$F0-$FF`→master fader (`mt_volume`) |

## 6. Song globals — patched into the player (`dc.b $ff,$00` slots)
greloc patches these immediates from the .sng; extract from the binary:
- **gatetimer** (cmp at `mt_pulseexec`+3; and `+2` as initial tick `lda #gatetimer+2`).
- **hard-restart AD** (`lda #ADPARAM` before `sta $d405`).
- **hard-restart SR** (`lda #SRPARAM` before `sta $d406`).
Constants: default tempo `$05`; master vol init `$0F`; testbit new-note ctrl `$09`.

---

## 7. USF representation (decided; follows FC precedent — NO schema change)

Per-row commands → **`NoteRow.fx_flags` strings** (exactly as FC encodes
glide/filter/wave_adjust — `pipelines/future_composer/to_usf.py`). Musical,
parametric, no new schema. Proposed flag vocabulary:
`arp=X,Y` · `portaup=N` · `portadown=N` · `toneporta=N` · `vibrato=X,Y` ·
`filter=N` · `sr=$XX` · `tempo=N`/`chtempo=N`/`fader=$XX`/`timingmark`.

Mapping to existing schema:
- **Instruments** → `Instrument.adsr` (AD,SR); pulse 4-scalar → `PwmConfig`
  (bidirectional: init from byte2, min_hi=pulselow, max_hi=pulsehigh,
  speed=pulsespd&$FE, plus a HR flag → `freq?`/envelope); wave program →
  `Instrument.waveform` (ctrl bytes + delays) + `Instrument.wave_freq` (note
  rel/abs) + `Instrument.loop`; filter ptr → `FilterProgConfig.program`.
- **Filter table** → `filter_programs` library (cutoff/res/route/mod), keyed by ptr.
- **Patterns** → `Pattern`/`NoteRow` (pitch, duration, instr, fx_flags).
- **Orderlists** → `Orderlist` (entries + `transposes` + `repeats` + `loop_to`).
- **Freq table** = engine constant (composer emits the baked 96-entry table;
  USF need not carry it — verify, revisit only if a tune diverges).
- **Song globals** → `Params` / init: gatetimer, HR AD/SR, default tempo.
- **Arp**: per-row `arp=X,Y`. (Cluster-by-behaviour: same musical concept as
  ArpConfig but row-scoped — kept as a row fx like FC's per-row effects.)

Convergence-ledger consult: pulse 4-scalar bounce = C1 SweepEnvelope family
(bidirectional special case); filter table = C1/C10; off-table reads not yet
seen for V1 (freq table is a constant, fixed 96 entries — watch for arp/porta
running off the 96-entry table → C6).

---

## 8. Extraction plan (dataflow, per feedback_dataflow_over_heuristics)
1. Locate player at load addr; confirm V1.5 via markers (delayed-wave `c9 08`,
   testbit `a9 09`).
2. Read the relocated table base addresses from the player's instruction
   operands (the `lda <tbl>,y` sites — virtual $4000/$4100/.../$4700) — gives
   instbase, wavetbl, notetbl, songtbllo/hi, patttbllo/hi, filttbl.
3. Read song globals (gatetimer, HR AD/SR) from the patched immediates.
4. Parse instruments (8B records), wave/note programs (per-inst slices via
   inst.wave + loop resolution), filter table, song table → orderlists,
   pattern table → patterns.
5. Emit USF; build via the V1 composer; verify writelog (instruction-sequence
   exact, [[feedback_verification_modes]]).

## 9. Open questions to settle during extract/compose (from research)
- Exact half-speed arp counter behaviour (param X>=8 path) vs the cycling above.
- Filter static/mod chaining + funktempo's filttbl[0] bytes 2-3 reuse.
- Packed wave-program loop-target arithmetic (`notetbl[y+1]+inst.wave-2`) edge cases.
- Note-without-command off-by-one ($60→note 1; how C0 nocmd is encoded).
Settle each against the writelog during canary bring-up, not by guessing.

## 10. Composer principle — CLEAN REIMPLEMENTATION, not transliteration
The composer must NOT transliterate `v1_player1_v153.s` into xa65. That source
is dense with the exact MECHANISMS the CORE TENET says to drop:
- self-modifying code (`mt_chnloop+1`, `mt_volume+1`, jump-target patching),
- `dc.b $ff,$00` patched-immediate slots (gatetimer, HR AD/SR baked into operands),
- greloc's overlapping/packed virtual-address layout,
- the funktempo-reuses-filttbl-slot-0 hack.
Treat the source as **authoritative DOCUMENTATION of the write-stream semantics**
(like the V2 docs), then write a CLEAN engine from the USF musical model: real
RAM variables (no SMC), our own data layout, gatetimer/HR-AD/SR as plain
constants, funktempo as a clean construct. Reproduce the write OUTPUTS (incl. the
`$D404=$09` testbit-on-new-note write — a real output, not a trick), NOT the
original's structure. The algorithm we reproduce (wave-program stepping, arp
cycling, pulse bounce, gate timing) is the musical MACHINERY and legitimately
lives in the composer (USF principle §4/§6); the MODEL learns from USF, not the
composer. Guardrails (the three filters): regenerate every table from USF (no
HVSC bytes leapfrogged), keep USF parametric/musical (no engine-positional or
opaque bytes), engine-blind within the one composer (no USF-content sniffing to
dispatch). See [[feedback_deconstruct_not_reproduce]] + the CORE TENET.

## 11. The OPTIMIZED-LAYOUT variant (dominant non-V1.5 sub-version) — RE notes
Rep: `DEMOS/A-F/Alive.sid` (load $1000). This is `player_variables.md`'s
"Optimized Variable Layout" — a substantially RESTRUCTURED player, NOT just
"no delayed-wave". Decoded play body ($1040-$120D):
- **init flag**: SMC at `$1043` operand (`lda #flag; bmi noinit; inc $1043`),
  flag = subtune-derived, → $FF after init. Init path ($1046-$1079) clears vars,
  sets `chntempo=$1422` AND `chntick=$1423` both to TEMPO (`$05`) — **init-tick =
  tempo, NOT gt+2** (changes first-row write-stream timing vs V1.5).
- **tick mechanism** ($107C): `ldy chntick; bne; <chntick==0 → tick0 $1250>;
  bpl; <neg → reload chntempo>; dey; tya; sta chntick` — decrement via LDY/DEY/STA
  (V1.5 uses `dec chntick; beq`). Same net effect; NO `cmp #gatetimer` in the
  pulse path.
- **sequencer** ($1095-$10C6): orderlist walk (cmp #$D0 REPEAT / #$E0 TRANS /
  #$FF LOOPSONG), triggered by `chnpattptr($1420)==$FF`.
- **wave-exec** ($116A): no-delay (`lda wctrl,y; beq; sta chnwave,x`).
- **arp** ($119E): SAME structure as V1.5 (asl/arpcount/cmp #$06/...).
- **loadregs** ($11E0): `$D400/$D401` freq, `$D404` wave. New-note AD/SR
  ($11F2): `lda $13f7,x; bne skip` — **`$13f7` is the HR/gate-state flag** gating
  the AD/SR write (the optimized variant's hard-restart mechanism, restructured).
- Channel vars (optimized layout): chntick $1422, chntempo $1423, chnpattptr
  $1420, chnsongptr $141E, chnrepeat $140F, chntrans $1424, chnpattnum $1421,
  chnwave $1409, chnwaveptr $140A, chnarpcount $140D, instnum $13FA, chnnote
  $13F4, chnfreqlo/hi $13F5/$13F6, chnfxparam $13F9, HR-flag $13F7, ?$13F8.

**Framing (corrected — re-run the CORE TENET): this is a VARIANT EXTRACTION PATH
+ shared composer + knobs, NOT a separate engine.** The composer reproduces the
WRITE STREAM with its own clean, layout-agnostic engine, so the original's
internal differences (channel layout, init structure, pattern/instrument
ENCODING) only affect READING the binary into the (engine-neutral) USF musical
model — i.e. the EXTRACTOR. It's the SAME tracker (GoatTracker V1, compiled with
NOWAVEDELAY + the optimized layout), so the musical content is identical → one
USF model, one composer (per the USF principle's one-family-one-composer rule;
cf. DMC family-1/family-2 = variant extraction + knobs, not two engines). The
only WRITE-STREAM-relevant differences are behavioral KNOBS: `inittick=tempo`
(added) + the `$13f7`/no-`hr_sr` hard restart (verify if a knob is needed).
**Extraction differences to handle:** song/patt pair assignment (code order is
REVERSED vs V1.5 → use the diff rule: song table hi-lo == 3*nsubtunes); +
re-derive instrument-table extent + pattern/instrument decode for the optimized
layout (my V1.5 decode yielded instrument#s past the real table → wave runaway).
OPEN: once the optimized extractor reads correctly, build with the shared engine
+ `inittick=tempo` and DIFF — the first-divergence says whether an HR knob is the
only remaining behavioral difference. Cross-ref `docs/src/v1_player1_125.s`.

## 12. PLAYER2 — the "gamemusic-mode" routine (the BIGGEST non-V1.5 bucket, ~374)

**Identity (CONFIRMED, full source available):** the 413-tune "filttbl-fail" bucket
is **player2 = Cadaver's gamemusic-mode playroutine** (`docs/src/v1_player2_125.s`,
"Musicroutine 11.2 by Lasse Öörni, with sound effect support"). 374/413 match the
detector below (the other 39 are 2SID/other). This is a DISTINCT player from
player1 (V1.5 tracker) — different filter model + SFX + entry points — NOT just a
layout variant. Rep: `DEMOS/A-F/Eighties_Megahit.sid`.

**Detector:** the GLOBAL self-modifying filter sweep in `mt_play`:
`clc; lda #imm; adc #imm; sta self; sta $D416` → anchor `A9 ?? 69 ?? 8D ?? ?? 8D 16 D4`
(+ wave-exec writes `$D404` directly — the wavetbl variant-3 anchor already added).

**SHARED with player1 (same byte format → reuse the extractors):** instrument
8-byte record (instad, instsr, instpulse, instpulsespd, instpulselow, instpulsehigh,
**instfilter**, instwave), wavetbl, notetbl, songtbllo/hi, patttbllo/hi, the pattern
format (NOCMD / FIRSTPACKEDREST / 3-byte cmd rows), orderlist (`$FF`=LOOPSONG +
restart byte).

**DIFFERS from player1 — the migration work:**
- **NO filttbl.** The filter is GLOBAL + self-modifying: `mt_filtcutoff`(SMC accum)
  `+= mt_filtcutoffadd` each frame → `$D416`; `mt_filtctrl` → `$D417`;
  `mt_filttype|mt_volume` → `$D418`. Per-instrument **`instfilter`** byte (newnoteinit
  l.341): if non-zero, sets cutoff=`instfilter`, type=`instfilter<<4`. → represent
  as a per-instrument filter param (cutoff+type, MUSICAL) + the global cutoff sweep =
  **ledger C10** (chip-global `$D415-$D418` automation).
- **Command semantics differ:** 0=arp, 1=PORTAMENTO, **2=SETCUTOFFADD** (filter sweep
  rate — NOT porta-down), 3=toneporta, 4=vibrato, 5=SETFILTER, **6=SETSUSTAIN** (NOT
  set-SR), 7=settempo. The extractor's `_row_fx` needs a player2 command map.
- **Wave-exec writes `$D404` directly** (l.207/379) — no-delay style.
- **4 entry points:** init / play / **setvolume** / **playsfx**. setvolume + SFX are
  GAME-only → NOT called in PSID playback → **IGNORE for music extraction** (the
  "sound effect playing?" check at l.314 is inert when no SFX is active).
- **Init** (l.192-221): per-channel clear + tempo=tick=5, pattptr=ENDPATT; then global
  filter cleared (`$D415`=0, filtctrl=0, filtcutoffadd=0).

**MIGRATION PLAN (proposed):** variant extraction branch in the V1 extractor (detect
player2 → skip filttbl; read `instfilter` per instrument; the global filter is a C10
automation track; player2 command map) + a **player2 composer body** (direct `$D404`,
global SMC filter sweep, player2 command semantics) selected by a `player='gamemusic'`
knob. USF model SHARED (one GoatTracker-family model, per the one-family-one-composer
rule). SFX ignorable for PSID. This is the single biggest V1 lever (~374 tunes) and a
multi-step sub-project (extractor branch is modest — most tables are shared; the
composer body is the lift).

### 12b. player2 COMPOSER BODY — adaptation spec (engine `_engine_v2`, TODO)

Read path DONE (extract + to_usf + the `player='gamemusic'` pattern-encoder). The
remaining piece is the engine asm `_engine_v2(t)` in composer.py, selected by
`t.player=='gamemusic'`. Write it by ADAPTING the working V1.5 `_engine` (which
already reads our data layout: songlo/songhi orderlists, pattlo/patthi+voicebase
patterns, instXXX, wctrl/wnote, freqlo/hi) — REUSE these as-is, CHANGE only the
player2 behaviors. Canary: a small player2 tune (e.g. `DEMOS/A-F/Faderik.sid`, 4
insts; or `Improper_C0nnections`). Routine-by-routine (vs v1_player2_125.s):

REUSE verbatim from `_engine`: the `sequencer` (orderlist walk — our format),
`getnewnotes` pattern fetch + note decode, `arpeggio`, `makespeed`, `freqadd`/
`freqsub`/`tp_*` toneporta, `pulseexec` pulse modulation (player2's is the SAME
add/sub-with-bounds logic), `packedrest`.

CHANGE for player2:
1. **Note-fetch timing.** player2 fetches the row AT tick0 (`ldy chntick; beq
   newnotes`), NOT at chntick==GATETIMER. So there is NO gatetimer-ahead getnewnotes
   in pulseexec — drop the `cmp #GATETIMER; beq getnewnotes` and fetch+process the
   row directly in the tick0 path. (No GATETIMER constant; no HR window.)
2. **Filter exec** (frame start, before channels): SIMPLER than V1.5 — no filttbl
   step. Just `lda filtcut; clc; adc filtcutadd; sta filtcut; sta $D416; lda filtctrl;
   sta $D417; lda filttype; ora #$0f (volume); sta $D418`. (player2 $D418 = filttype
   OR volume-nibble, where volume defaults $0f; NOT V1.5's `and volmask`.)
3. **Commands** (the `_fx_to_cmd` numbers are already player2-correct): cmd1 =
   SIGNED porta (`asl param; bcc freqadd; bcs freqsub` — reuse freqadd/freqsub);
   cmd2 = SETCUTOFFADD tick0 set (`sta filtcutadd`); cmd5 = SETFILTER tick0 set
   (`sta filtctrl` → global $D417); cmd6 = SETSUSTAIN (`sta $D406,x` — same as V1.5
   cmd6); cmd0/3/4/7 (arp/toneporta/vibrato/tempo) reuse V1.5.
4. **Wave-exec writes $D404 DIRECTLY** (`lda wctrl,y; beq skip; sta chnwave,x; sta
   $D404,x`); player2's freq is written in arpfreq (`sta $D400/$D401`), pulse in
   loadpulse (`sta $D402/$D403`). So there is NO combined V1.5 `loadregs` — split
   the writes: ctrl in wave-exec, freq in arpfreq, pulse in a loadpulse tail. Match
   player2's per-voice write ORDER exactly (the convergence crux).
5. **Hard restart is immediate** on a new normal note: `lda #$00; sta $D405,x; sta
   $D406,x` (no HR_AD/HR_SR constants, no gatetimer window). New-note then loads
   instad/instsr, sets pulse from instpulse, and **instfilter → global filter**:
   `lda instfilter,y; beq +; sta filtcutoff; asl×4; sta filttype` (sets the GLOBAL
   cutoff+type on trigger — NOT a per-voice filter).
6. **init**: per-channel chntick=chntempo=chnnewnote=5, pattptr=ENDPATT; clear the
   global filter (filtcutoff=filtcutoffadd=filtctrl=filttype=0, $D415=0). Keep the
   deferred-init structure (first play = orig frame 0, dropped by the verdict).

BSS additions player2 needs (add to `_BSS_VARS`, harmless for player1): chncommand,
chncmddata, chnvibcount, chnwavetbl (player2's wave pointer ≈ V1.5 chnwaveptr — can
reuse chnwaveptr). Globals filtcut/filtcutadd/filtctrl/filttype already exist.
SFX (playsfx) is game-only → never emit (PSID never calls it).

Then build the canary → `tools/find_first_divergence.py` → fix the first per-voice
write-order/value diff → iterate (the standard bring-up loop). ~26% of V1 (~374
tunes) ride on this.

## Canary
`hvsc84/MUSICIANS/T/Topaz/Joker.sid` — V1.5, single-subtune, load $1000, compact.
