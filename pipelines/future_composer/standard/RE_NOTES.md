# Standard FC player — RE notes + effect-format spec

Representative: `Carter/Jarre_2.sid` (load $1800). Dominant FC player =
3673/4024 (91%) of HVSC FC. Full disasm + address map in `disassembly.s`.
Config + working extract in `config.py` (FC_STANDARD). Status: extract OK;
play stream diverges because the standard effect formats aren't yet
implemented in the extract decoders + composer emitters. This file is the
implementation blueprint for those two effect engines.

## PULSE effect — table $1E95, routine $1B40-$1BE0
Format: N programs × 4 bytes = `[thr_a, step1, thr_b, step2]`.
Selected by an instrument byte `(n & 7)`; program index uses `(n-1)*4`.
Jarre_2 has 3 programs:
  prog1 `04 a0 08 60`   prog2 `04 80 0c 10`   prog3 `03 80 10 40`

Per frame, with voice frame-counter `ctr = $2142,x`:
  - `ctr >= thr_a`            → step = step1   (byte +1)
  - `thr_b <= ctr < thr_a`    → step = step2   (byte +3)
  - `ctr <  thr_b`            → step = default ($2154 & $FC)
Step drives a 16-bit PW accumulator (lo $2145,x / hi $2148,x), with a
per-voice direction flag $216F,x:
  - dir=0 (down): acc -= step; if hi underflows below $01 → dir=1 (up)
  - dir=1 (up):   acc += step; if hi reaches $0F → dir=0 (down)
Then `$D402 = acc_lo`, `$D403 = acc_hi` (per-voice via d4point $2156).
Bounds $01/$0F are HARDCODED (cf. [[reference_hubbard_pwm_bounds]] — same
pattern as Hubbard's hardcoded PWM bounds).

vs Tel variant (Cyb II `pulse_run_style='cyb2'`): constant `pulserunspeed`,
8-byte programs. The standard format is a ctr-keyed 2-threshold step schedule,
4-byte. → needs `pulse_run_style='standard'` (new asm) + a 4-byte decoder.

## FILTER effect — table $1E89 (ptr $f9/$fa = $1E89), routine $1C00-$1C7B
Format: 12 bytes = `[6 cutoff values][6 thresholds]`.
Jarre_2: cutoffs `c0 f0 f8 f4 f2 40`  thresholds `01 02 06 0c 10 30`.
Per frame, with `ctr = $2142,x`: scan thresholds (y=$0B..$06, descending);
the band ctr falls into selects a cutoff (y=$00..$05) → `$D416` (cutoff hi),
and res/routing computed from $2169,x + a value → `$D417`. Time-keyed cutoff
envelope. vs Tel `fx_filter_prog` (4 ptrs to 10-byte programs) — different
shape → needs a standard filter decoder + emitter.

## Implementation plan (the two effect engines)
1. Extract decoders (engine_model.py), gated by a cfg format knob:
   - pulse: read $1E95 as N×4 → USF pulse program {thr_a,step1,thr_b,step2}.
   - filter: read $1E89 as 6 (threshold,cutoff) pairs → USF filter program.
   Confirm against the raw bytes above.
2. USF representation: extend pulse_programs / filter_programs to carry the
   standard shape (or add a typed variant) — musical params, not raw bytes.
3. Composer emitters (composer_asm.py), GATED by cfg so the green canaries
   (Cyb II/Hawkeye/Adrenalin) are untouched:
   - `_emit_fx_pulse_run` → add `pulse_run_style='standard'` with the
     2-threshold step schedule + PW accumulator + $01/$0F flip above.
   - filter emitter → add a `standard` style with the 6-band cutoff envelope.
4. Iterate write-log on Jarre_2 via `verify_featuredriven` (trichotomy).
5. Relocation: family members load at $1800/$4800/... — derive addresses from
   the load/init so ONE config covers all 3673.

## Pulse EMITTER integration plan (turnkey — derived from the composer)
DONE: decoder (`_decode_pulse_programs`, gated by `cfg.pulse_prog_format=='standard'`)
parses $1E95 into `{std,thr_a,step1,thr_b,step2}` — VERIFIED on Jarre_2.

Remaining, minimal-wiring path (avoids USF grammar changes):
1. USF schema reuse: have the decoder emit the EXISTING Tel pulse-program shape
   so `_write_pulse_programs`/reader round-trip unchanged:
     `{lo:$01, hi:$0F, wrap:False,
       segs:[(thr_a,step1,False),(thr_b,step2,False),(0,0,False)]}`
   (the standard bounds $01/$0F are hardcoded; default step $2154&$FC handled in
   the emitter). The emitter reinterprets seg[0]/seg[1] as the 2-threshold
   schedule — it does NOT use the Tel sequential-crossing semantics.
2. Composer emitter: this is a PER-INSTRUMENT PW program → it belongs on the
   `pp_store`/`pulse_prog` path (pulsestolo/pulsehisto shadows), NOT
   `fx_pulse_run`. Add a gated `standard` variant that, per voice per frame:
     step = (ctr>=thr_a)?step1 : (ctr>=thr_b)?step2 : (default $2154&$FC)
            where ctr = the voice frame counter
     16-bit PW acc ±= step; dir flag flips at hi<$01 (→up) / hi>=$0F (→down)
     write shadow d402/d403 (respect cfg.voice_loop_layout: interleaved →
     inline SID write in pp_store; tight → nextvoice writes at chain end)
   Note-load resets the acc + dir + selects the program (find the standard
   selector field in the instrument record — disasm $1986/$19xx area).
3. Verify: set FC_STANDARD pulsetabel_addr=$1E95 + pulse_prog_format='standard';
   `verify_featuredriven`; localize the $D402/$D403 sub-stream divergence with
   tools/voice_writelog.py; iterate.
GATING: everything behind cfg knobs; default 'tel' → Cyb II/Hawkeye/Adrenalin
untouched. Hubbard/Companion are a different composer entirely (no risk).

## EMITTER PROGRESS + key finding (2026-06-09)
DONE: standard pulse emitter asm cut + integrated — `_standard_pulse_prog_body`
+ `_splice_standard_pulse_prog` (marker-based splice of fx_pulse_prog..pp_store,
gated by cfg.pulse_prog_format=='standard'). FC canaries stay 15/15 (gating is
clean — Tel engines never run the standard body). Config enables it
(pulsetabel_addr=$1E95, pulse_prog_format='standard').

**KEY FINDING — wrong order:** enabling the pulse emitter does NOT move the
Jarre_2 verdict, because the trichotomy aligner returns `shift=None` — the
play streams don't align AT ALL. That means the BASE playback (notes / freq /
ctrl / AD-SR / sequence timing) already diverges from the standard player
(rebuild ~10% more writes), so effects can't be isolated/verified on top of an
unaligned base. **Base playback alignment is the PREREQUISITE; pulse/filter
come after.** The pulse emitter is banked (gated, safe) but unverifiable until
the base aligns.

**NEXT (revised order):**
1. BASE first: get Jarre_2's play stream to ALIGN (shift becomes a small int,
   not None). Localize the first base divergence (note-load / sequence step /
   freq+ctrl write order / per-frame writes) — the composer's Tel-tuned base
   behavior vs the standard player. This is where the real iteration is.
2. THEN pulse: with the base aligned, verify the $D402/$D403 sub-stream
   (tools/voice_writelog.py) and fix the standard pulse selector/default/
   counter semantics.
3. THEN filter ($1E89), then relocation for family coverage.

## BASE-ALIGNMENT iteration — first divergence found (2026-06-09)
Compared per siddump frame (init = frame 0). The standard player writes each
voice's block ONCE per frame in this order (V3 note frame, from orig Jarre_2):
  $0F freqhi, $0E freqlo, $13 AD, $14 SR, $10 PWlo, $11 PWhi, $12 ctrl
(held frames omit AD/SR: freqhi, freqlo, PWlo, PWhi, ctrl). V1/V2 analogous at
their reg offsets, voice order V3,V2,V1.

The composer's DEFAULT layout (tight_nextvoice + nextvoice_write_order
(4,0,1,2,3)) instead emits, per voice:
  nolengset(note-load): freqhi, freqlo, AD, SR
  nextvoice(every frame): ctrl, freqlo, freqhi, PWlo, PWhi
→ FREQ WRITTEN TWICE (nolengset + nextvoice) and AD/SR land BEFORE freq, not
after. That is the +2-writes/frame and the `shift=None` (streams never align).

**FIX (next asm cut):** a gated `voice_loop_layout='standard'` that emits the
per-voice block freqhi, freqlo, [AD, SR on note], PWlo, PWhi, ctrl — ONCE, in
that order (freq written once per frame in the voice loop; AD/SR interleaved
after freq on note-load; no nextvoice freq duplication). Gate it so Cyb II/
Hawkeye/Adrenalin (interleaved/tight) are untouched. Then re-compare frame 1;
expect `shift` to become a small int (streams align), exposing the next
divergence (tempo / held-frame / sequence). THEN the pulse + filter emitters
(already cut/spec'd) become verifiable.

## BASE-ALIGNMENT progress (2026-06-09, cont.)
DONE: `voice_loop_layout='standard'` (gated) — nolengset's freq SID writes
suppressed so freq is written ONCE per frame by nextvoice. **Freq-duplication
divergence FIXED.** FC canaries 15/15 (gated). Config: voice_loop_layout=
'standard', nextvoice_write_order=(1,0,2,3,4).

Still `shift=None`. Two remaining base issues, found by per-frame compare:
1. **Held-frame write order** is `PWlo,PWhi,freqhi,freqlo,ctrl` = nextvoice
   order `(2,3,1,0,4)`, NOT (1,0,2,3,4). (Note-load frame 0 is freq-first,
   freqhi,freqlo,AD,SR,PWlo,PWhi,ctrl — note vs held orders differ; the
   composer's nolengset(AD,SR)+nextvoice split may not produce both exactly.)
2. **NOTE-TIMING divergence (the alignment blocker):** orig V3 freq advances
   $25a2(f0)→$4800(f1)→… (new notes), but the rebuild HOLDS $25a2 — it isn't
   advancing notes at the original's cadence. Likely a speed/tempo or
   note-length mismatch (per_subtune_speed_addr=$211D may be wrong, or the
   standard player's note-length/speed-counter semantics differ from the
   composer's). Until note timing matches, no 64-write window aligns → shift
   stays None.

**NEXT:** (a) set nextvoice_write_order=(2,3,1,0,4); (b) fix note timing —
trace the standard player's speed/note-length ($2173 ctr vs $211D, the
nootleng/nootcount path) vs the composer's, get V3 to advance to $4800 at f1.
Then shift→int (aligned), then the held/note order + effects (pulse/filter).

## ROOT CAUSE of the "note-timing" divergence (2026-06-09) — it's the INSTRUMENT LAYOUT
Tempo is CORRECT: $211D=$01, extracted speedbyte=$01; the tick mechanism is
per-voice $2142-$2144 incremented every frame, $2173 counts down + reloads from
$211D, tick when $2173==$211D (DEC $2127,x note-length). So note advance is fine.

The real divergence is EFFECTS driven by a wrong instrument decode:
- reb V3 freq oscillates $25a2 ±4 ($25a6/$259e) = SPURIOUS VIBRATO; orig V3 holds
  $25a2 (with brief $4800 transients = some other effect).
- The composer's fx_vibrato runs iff the instrument's fx1 byte != 0
  (composer_asm.py ~1930/1957). The extract decodes the standard instrument's
  effect bytes at the TEL offsets (fx1/fx2/fx3 = record +5/+6/+7), but the
  STANDARD 8-byte record has a different layout, so it reads the wrong bytes as
  fx1 → spurious vibrato (and wrong pulse/filter selectors). AD ($+2) / SR
  ($+3) happen to line up (confirmed via disasm note-load), but the effect bytes
  do NOT.

**NEXT (the actual base prerequisite):** map the STANDARD instrument record's
8-byte layout from disassembly.s (note-load $1986-$19C9 + $1A11-$1A1D reads
$2188+0..7): which byte = waveform/ctrl, pulse-hi, AD, SR, and which drive
vibrato / pulse-program / filter / wave selectors. Then a standard instrument
DECODER (gated by a cfg knob, like the pulse decoder) so the composer applies
the RIGHT effects. Until then the base can't align (spurious vibrato corrupts
every held frame). Held-frame write order is now set: nextvoice (2,3,1,0,4).
THEN the $4800 transient effect, then pulse/filter emitters (already cut).

## Standard instrument decoder DONE — vibrato fixed; frame-1 divergences remain (2026-06-09)
`instr_format='standard'` decoder cut (gated): decodes the real 8-byte layout,
zeros Tel fx1/2/3 → **spurious vibrato GONE** (V3 freq steady $25a2, matches
orig). FC canaries 15/15. But still `shift=None` — frame-1 compare shows the
standard player is STRUCTURALLY different from the Tel composer in several ways:

1. **$D418 (vol) placement** — orig writes $18=$1F FIRST each frame (top of the
   play loop $1833); composer writes it mid-frame. → need a vol-first knob.
2. **Conditional freq writes** — orig does NOT rewrite a voice's freq when
   unchanged (frame1 V2 = PW+ctrl only, no freq); the composer's nextvoice
   writes freq EVERY frame. → the standard player writes freq only when it
   changes (note/effect). This is a different per-frame write model.
3. **ctrl/waveform from the WAVE PROGRAM** — orig V3 ctrl $81 at frame1 (from
   wave table $1E76 = 81,41,40,40,...); composer uses the static raw[1]=$41.
   → need the standard wave-program emitter ($1E66/$1E76) driving $D404.
4. **PW** — orig sweeps (standard pulse, currently off because fx2=0); needs the
   standard pulse selector wired (selector byte TBD, NOT fx2=$2154 which is the
   default-step) + the cut pulse emitter.
5. **Filter $D416/$D417** — orig $16=$FF; needs the standard filter emitter ($1E89).
6. **$4800 freq transient** (orig V3 frame1) — another per-frame effect TBD.

So the standard player is a structurally-different engine (conditional freq
writes, wave-program ctrl, vol-first, standard effect formats), not a knob
variant of the Tel composer. Each item above is a gated composer piece +
write-log iteration. Recommended next order: (1) vol-first, (2) conditional
freq writes, (3) wave-program ctrl — these are the base; then pulse/filter.

## WAVE-PROGRAM emitter — full RE + decoded data (2026-06-09) — the engine's core envelope
Routine $1C7B-$1CE2. The biggest base/effect piece: a per-frame envelope that
drives BOTH ctrl ($D404) and freq ($D400/$D401).
- ENABLE: instrument +7 ($2155) bit4 ($10). If clear → skip (go to $1CE3,
  another effect: $2155 bit7).
- SELECTOR: instrument +5 ($2153) low nibble → index into 4 pointer tables
  $1E3E(ctrl-lo)/$1E40(ctrl-hi)/$1E42(freq-lo)/$1E44(freq-hi); SMC'd into the
  LDA operands at $1CAE/$1CB6. (Jarre_2: only sel 0,1 valid; ptr tables end at
  the first data table $1E46.)
- CLOCK: $2142,x = frames since note-load (the effect-envelope clock, INC every
  frame, reset on note-load), capped at 15 ($1CA5 CMP #$0F BCS skip→holds last).
  Index = clk-1 ($1CAC TAX; DEX).
- CTRL: ctrltable[clk-1] → $2179 → $D404.
- FREQ: freqtable[clk-1] → $2168; then mode on +5 ($2153) bit4 ($10):
    set ($1CC5) → freq = $2130,x + $2168 (relative)
    clear ($1CCF) → freq hi = $2168 + $0D, freq lo = $00 (absolute)
- Decoded Jarre_2 programs (15 entries each):
    sel0 ctrl@1e56 [81 41 40 80 80 80 80 80 10 10 10 10 10 10 10]
         freq@1e46 [13 01 ff 23 08 13 03 23 00 00 00 00 00 00 00]
    sel1 ctrl@1e76 [81 41 40 40 40 40 40 40 40 40 40 40 40 40 40]
         freq@1e66 [24 fd fb f9 f8 f7 f6 f6 f5 f5 f4 f4 f5 f6 f5]

This is what makes V3's ctrl ($81) and freq ($4800) — the largest remaining
divergence. The conditional-freq logic already in place will emit the freq once
the wave program updates the freq shadow.

EMITTER PLAN (gated standard wave style):
1. Decoder: per selector, read ptr from $1E3E/$40/$42/$44; decode ctrl[15] +
   freq[15] tables. Number of selectors = (first-table-addr - $1E3E)//... bound
   by the ptr region; for Jarre_2 = 2. USF: carry per-selector ctrl+freq tables.
2. Composer emitter (gated): each frame, if instrument wave-enabled, clk =
   min(counter2,x, 15); ctrl_shadow = ctrl[clk-1]; freq from freq[clk-1] per
   mode (+$0D absolute / +base relative). counter2,x must = frames-since-note
   capped 15 (verify it resets on note-load like $2142,x).
3. Wire selector (instrument +5 low nibble) + enable (+7 bit4) + mode (+5 bit4).
4. Verify ctrl + freq sub-streams (tools/voice_writelog.py); iterate.
This is a large dual-register envelope engine — implement carefully + iterate.

## ✅ PATTERN DECODER DONE + finding CORRECTED (2026-06-10)
The standard pattern decoder is implemented and committed (1af4a15):
`_parse_pattern_standard` in engine_model.py, gated by `cfg.pattern_format=
'standard'` (default 'tel' → canaries untouched, 15/15). Full $18DD-$1957 trace:
  $FF        end ($19CC / sub_19ED peek)
  $F0..$FE   tie/no-retrigger prefix; low nibble ignored; NEXT byte is the note,
             played WITHOUT instrument reload ($2180,x=1 skips $1986 note-load).
             → PatNoGlide (carries the 'noretrig' flag in to_usf) + PatNote.
  $E0..$EF   3-byte glide [$Ex][param][note]; param low nibble = dir(b0)+
             speed(b1-3>>1); 3rd byte = note. → PatGlide + PatNote.
  $C0..$DF   INSTRUMENT-select, low 5 bits (0-31). → PatInstrumentChange.
  $80..$BF   note-length, low 6 bits. → PatSetLength.
  $00..$7F   note. → PatNote.
Reuses the existing PatEvent vocabulary; to_usf/composer consume it unchanged.

**The 2026-06-09 "wrong notes / stuck on 2" finding below was a MIS-DIAGNOSIS**
(from an incomplete parser trace that hadn't yet resolved $1930=$Cx-instrument
and $1942=$8x-length). Empirically the note PITCHES are IDENTICAL between Tel and
standard decode for Jarre_2 (verified: pat9 both give 43,43,43,45,46,...). The
REAL foundational bug is INSTRUMENT SELECTION: Jarre_2's patterns have ZERO
$70-$7F bytes — they select the instrument via $Cx, which Tel decode misread as
a wave-position nudge (PatWaveAdjust), so NO instrument was ever selected and the
WRONG (default) instrument's effects ran. Fixed now: pat5→i4, pat6→i1,
pat7/8/9→i7. Frame 0 matches; first divergence moved to frame 1 (the effect chain).

## ✅ $40 EFFECT (wave-arp) DONE + instrument-select fix (2026-06-10, commit 3fdf1e9)
The $40 effect ($1BE0: ctrl=$1E32[counter&3] when counter>=3) = the SAME musical
concept as the already-shipped `wave_arp` (types.py: "cycles $D404 waveform
indexed counter2&3"). REUSED it — no new schema: wavearp_addr=$1E32 +
wavearpwait=3 (onset = a player constant = engine mechanism, correctly a cfg
knob not USF content) + a gated interpreter block in std_wave_chain (the Tel
fx_wave_arp is bypassed by gwo2->std_wave_chain). Decoder/data/allocator/equate
paths all pre-existed.

PREREQUISITE FIX (same commit): the instrument-select encoding. The composer's
pattern parser sets wavecount (its instrument mechanism) ONLY from $C0-$DF;
$70-$7F is arp-select. But encode_pattern emitted NoteRow.instr as $70|n — so the
standard $Cx instrument round-tripped into the ARP path and never set the
instrument: every standard voice played inst0 (all-zero) → ctrl $00. New
`instr_as_wavecount` flag (gated on pattern_format=='standard') emits the
instrument as $C0|n. NOW: V2 loads inst1, ctrl $41 gate-on; the $40 effect
cycles ctrl $40. **V1 (inst4, WAVE PROGRAM) ctrl matches orig EXACTLY** (incl.
timing: $11,$81,$41,$40,... — confirms counter2's phase is right for V1).

### Residual on the $40 effect — a per-voice counter INIT-PHASE difference
The $40 effect onset is 1 tick late: orig writes ctrl=$41 for 2 frames then $40;
reb writes $41 for 3 frames then $40 (a real write-COUNT diff, not Trap-C). Yet
V1's wave program (same counter2) matches exactly. So counter2 is NOT globally
off — orig has a 1-frame phase DIFFERENCE BETWEEN VOICES: V1's counter is 0 at
its note-load (wave entry[0] at note-load+1), but V2's $40 effect fires as if its
counter is +1 (2 ticks not 3 to reach the CMP #$03 threshold). orig establishes
this inter-voice phase during INIT/pre-roll (some voices' counters advanced
before the first play). The reb resets all voices' counter2 at f0 (in phase), so
V2 is 1 tick behind orig. ALSO a separate note-DURATION discrepancy (reb V2 note2
~2 frames early). Both are base counter/tempo init-phasing — broader than the $40
effect, shared across effects — NOT yet fixed. The $40 VALUES are correct.

## ✅ $80 EFFECT DONE (2026-06-10, commit 13beae3) — V3 attack+restore EXACT
= noise_tick reuse (same fx3 bit as Hawkeye's; 0x80→'noise_tick' mapping
pre-existed): new `noise_tick_style='standard'`, body in std_wave_chain (after
the wave program, matching orig chain order $1C7B→$1CE3). Semantics: counter<2
→ freq=$4800 (written HI,LO via the conditional-freq path) + ctrl=$81; counter
>=2 → BASE note freq rewritten EVERY frame LO,HI (orig $1D0A) + ctrl=
waveform&$FE. The order asymmetry is handled by a per-voice `nt_flag` armed by
the chain each restore frame and consumed by nextvoice's freq slot
(unconditional lo,hi write; self-clearing so note-load frames — which skip the
chain — use the normal conditional path). Verified exact on Jarre_2 V3 f1-f4
(values AND order). Rebuild writes 11544→13494 (orig 17189).

## ✅ PULSE SWEEP DONE (2026-06-10, commit 23c9f22) — corrected semantics
$1B41-$1BDD, body at the TOP of std_wave_chain (orig chain order pulse→$40→
wave→$80), gated pulse_prog_format=='standard'. CORRECTED step schedule (the
older notes above had the bands backwards): ctr<=thr_a → step1; thr_a<ctr<=
thr_b → step2; ctr>thr_b → DEFAULT step = fx2&$FC. Program selector = fx2&7
(OVERLAPS the default-step field). **fx2&7==0 quirk:** the orig indexes the
table at -4 and compares OUT-OF-TABLE bytes; for real tunes these resolve
below ctr → default band (proof: V2 +$40/frame and V3 +$C0/frame = each
inst's own fx2&$FC — one shared garbage step couldn't make both). Composer
emits an explicit fx2&7==0→default branch (tenet: no OOB-read mechanism).
Acc = d402/d403 shadows + dir = pulsetest,x — both already note-load-init'd
(lo=0/hi=pw&$0F, dir=1) and tie-skipped; NO new state. Flips at hi<$01/>=$0F.
fx2==0 → no acc update (shadows still hit SID via nextvoice). Data: gated
4-byte [thr_a,step1,thr_b,step2] emission at (n-1)*4 (Tel keeps 8-byte).
DELETED the inert splice (_standard_pulse_prog_body/_splice_…) — it patched
the Tel chain which the standard layout bypasses; it never ran. NOT emitted:
+$B0 write-time jitter (inst raw[0] bit7, odd frames; acc unaffected) — no
Jarre_2 inst uses it; implement when a family SID exercises it.
Verified: V2 exact; V3 exact until the known ~2-frame-early note advance.

## ✅ WAVE-FREQ + $D416 + TICK GATE-OFF DONE (2026-06-10, commits 4c0a355 +
## e18bda0) — FRAMES 1-3 EXACT (match prefix 46)
1. **Wave-program FREQ part** (orig $1CB6-$1CE0): val=freqtab[sel][clk-1];
   mode = inst +5 bit4: SET = RELATIVE — a semitone ARPEGGIO (note index +
   val → freq-table lookup, written LO,HI direct, $1D42), NOT a raw freq
   add; CLEAR = ABSOLUTE (hi = val+$0D w/ 8-bit wrap, lo=0, written HI,LO,
   $1CD8/$1CDD). Both unconditional clk 1..14. TWO corrections: clk>=15
   SKIPS the whole ctrl+freq update (shadows hold; idx range is 0..13, NOT
   "capped at 15"); wave-enabled insts NEVER reach the $80 effect (all
   paths exit before $1CE3). nt_flag generalized → fw_mode (0=cond hi,lo /
   1=uncond lo,hi: $80-restore+wave-relative / 2=uncond hi,lo: wave-abs).
2. **$D416=$FF filter-off default** (orig $1C6A-$1C78): +7 bit0 CLEAR insts
   write $D416=$FF iff voice == filtvoice latch ($2175, 0 until a filter
   inst runs → V1/X=0 wins). Chain arms filt_pend; nextvoice writes it
   between PW and freq ($1C78 position). Bit-SET path ($1E89 6-band
   envelope + $D417 res/routing $1C32-$1C67) still unemitted (unexercised).
3. **Standard tick GATE-OFF** (orig $19FA) + RE-DIAGNOSIS: the earlier
   "counter init-phase / $40-onset-late" residual was NEITHER — orig V2's
   $40 at f2 is $19FA: on tick frames with counter2!=0 the ctrl shadow
   defaults to waveform&$FE BEFORE the chain (the wave-arp value $40 merely
   coincides). New h10 body for voice_loop_layout='standard'. The
   init-phase theory is DEAD; ignore it in older sections below.

## ✅✅ JARRE_2 SUB 0 FULL (2026-06-10) — play 17164/17164, trichotomy audio✓
The first fully-verified standard-player tune. The last three pieces:

### VIBRATO done ($1A36-$1AE8) — full RE
Runs iff fx3 bit2 CLEAR, bit4 CLEAR (wave insts skip it via the $2030 path,
which makes NO SID writes) and fx1 != 0. fx1 = depth(bits 3-6) + speed(bits
0-2) — NOTE: different bit layout from Tel's fx1 vibrato. Per-voice triangle
counter ($215E pos / $215B dir = svib_pos/svib_dir) — NOT reset on note-load,
continuous across notes. Step = the note's SEMITONE DELTA (freq[note+1] -
freq[note]) shifted right per speed, replicated 1:1 INCLUDING two quirks that
are audible semantics: `hi += counter2 + carry` ($1A7C) and a lone initial
A-only LSR ($1A7F). freq = base - step*(depth/2) + step*pos, written
$D400/$D401 (lo,hi) DIRECTLY when counter2 >= 4 — lands before nextvoice's
PW block (the orig position). Shadows/lastfreq untouched (vibrato is
invisible to the shadow system; $80-restore voices rewrite base after, as in
orig). $1AEB-$1B40 is the $Ex GLIDE (shadow-modifying, lo,hi direct) — NOT
yet emitted, no Jarre_2 sub-0 pattern uses $Ex.

### Note-duration semantics fixed (the "~2-frames-early" residual)
The standard player plays (raw&$3F)+1 ticks per $8x length byte ($2127=raw,
DEC/BMI counts raw+1 underflows); the composer plays exactly `duration`
ticks (nootleng=duration-1). Fix in the EXTRACT (principled — USF carries
the ACTUAL tick count): _parse_pattern_standard emits PatSetLength(raw+1).
CAVEAT: consecutive $8x bytes OVERWRITE in the standard player but to_usf
CHAINS them (Tel) — no Jarre_2 pattern has adjacent $8x; gate if a family
SID does.

### Init = pure trichotomy (init_style='universal_reset')
Orig Jarre_2 init is a CLEAN ZEROING ($00-$17 ascending; the $D418=$0F is
the host stub) with NO priming → USF init{} stays empty, cfg defaults
(init_master_vol=$0F, no filter) match the end-of-init state exactly. The
Tel-style default init (which writes $16=$FF/$17=$00/$18=$1F — Cyb II's
signature) was leaking in before the knob was set. Verdict: shift=7,
init=(25,32), state ✓, audio✓ (canonical boundary).

### Still unimplemented (will surface via write-log on family SIDs)
- filter bit-SET path ($1E89 6-band envelope + $D417 res/routing $1C32-$1C67)
- $Ex glide ($1AEB-$1B40)
- pulse +$B0 write-jitter (inst raw[0] bit7, odd frames)
- the fx3-bit2 / $2030 effect (writes $1E87/$1E88 globals — glide speed?)
- wave+$80 both-bits insts (orig: wave path skips $80 — composer matches)
- adjacent-$8x setlen chaining (see caveat above)

## FAMILY ROLLOUT phase 1 (2026-06-10) — relocation + 2nd member FULL
**Relocation confirmed + shipped**: the load image has a FIXED internal
layout — 2760/4024 HVSC FC SIDs carry the canonical freq table at exactly
load+$564; 2639 share Jarre_2's full shape (init=load, play=load+6, vblank).
`fc_standard_config(sid_path)` (standard/config.py) shifts all 9 address
fields by (load-$1800) + probes the variant byte (below). Sample list:
/tmp/fc_std_members.json (regenerable via the freq-table probe).

**PRATO (Luca) = 2nd verified member** — play 181601/181601, audio✓.
Three family findings shipped on the way:
1. **Pulse programs decoded BY REFERENCE**: n = fx2&7 for every inst; the
   player indexes blindly so n>=4 reads PAST the nominal 3-prog table into
   following data (Prato prog 7 lands in the pattern-ptr region). The 4
   bytes are still the inst's effective schedule — captured by VALUE.
2. **STALE-TAIL player variant** — a single static code byte at orig $2046
   (the vibrato-skip JMP operand): $EB (Jarre_2) = skip writes nothing;
   $DC (Prato) = jump into the vibrato WRITE TAIL ($1ADC) → vibrato-skipped
   insts (fx1==0 / wave bit4 / bit2) write the STALE global work regs
   ($217C/$217D — last vibrato computation, possibly another voice's!) to
   their freq lo,hi EVERY frame. cfg.std_vibrato_stale_tail, factory-probed.
   This single fix took Prato 1.57% → 92.87%.
3. **Instrument table growth**: patterns select ids 0-31 ($Cx, 5 bits);
   Prato references inst 10 (beyond Jarre's 10). Extract grows the decode to
   max referenced id; the composer sizes every instr-table emission from
   the USF (instr_count is a floor, not the truth).
Plus verify fixes: Songlengths fractional seconds ('0:19.813'); trichotomy
Check-A default state now includes the HOST's pre-init $D418=$0F (psiddrv
writes it BEFORE init) — deferred-init members (Prato: init makes ZERO SID
writes, the $210E=$2C variant) verify correctly.

### NEXT: the $Ex GLIDE (the biggest remaining effect; blocks Entrail +
### likely several of the 9 remaining sample failures)
Full RE (from $18FC + $1AEB-$1B40):
- Pattern cmd [$Ex][param][note]: cmd bit0 → dir flag $213F,x=(b&1)+1
  (1=up, 2=down); cmd bits1-3 >>1 → $2165 (speed HI). Param byte: hi
  nibble → $2164 (speed LO, hi-nibble-only value); lo nibble → the GATE
  THRESHOLD, stored via SMC into the CMP operand at $1AF8. NB $2164/$2165/
  $1AF8 are GLOBALS — last-parsed $Ex wins across voices.
- Per frame ($1AEB): if (noteleng - count) < threshold → skip (glide
  starts mid-note); if $213F,x==0 → skip (flag cleared per note at $18CD).
  dir==1 → shadows $213C/$2136 (lonotesto/hinotesto!) += $2164/$2165,
  written lo,hi DIRECT; else -= , same writes. Position: between vibrato
  and pulse. NOTE: it MUTATES the base-freq shadows → the $80-restore and
  vibrato base then see the glided freq (orig behavior).
- **MY PARSER BUG**: _parse_pattern_standard currently DISCARDS the $Ex
  param byte (only keeps cmd&$0F as PatGlide.delay + the note). Needs: carry
  (dir, speed_hi, speed_lo, threshold); to_usf encode; encode_pattern emit
  the standard 3-byte form (gated — the Tel $E0,d,p semantics differ); the
  composer's $Ex parse handler + the chain glide block.
Then re-batch /tmp/fc_std_sample.json (9 tunes still shift=None) +
widen to the full member list.

## ✅ $Ex GLIDE DONE (2026-06-10) + the MIRROR-WRITE variant
Implemented across all layers: USF grammar/parser grew `glide_up=$RRRR` /
`glide_down=$RRRR` / `glide_onset=N` (directional-rate portamento — a new
point shape in the same parameter space as Tel's `glide=N` slide-to-target);
PatGlide carries (direction, speed, onset); standard 3-byte encode; gated
composer $Ex parse handler (sgl_dir,x per voice + sgl_spd_lo/hi + sgl_thresh
GLOBALS, last-$Ex-wins, threshold as a variable not the orig's SMC); chain
block between vibrato and pulse — MUTATES lonotesto/hinotesto (so $80-restore
sees the glided freq), writes lo,hi direct, d400/d401+lastfreq track intent.

**MIRROR-WRITE variant** (one static operand byte at orig $1B3F, the glide-UP
hi write): $01 = 2739/2760 members (normal freq hi); $55 = 20 members (e.g.
Entrail_Ranx) — STA $D455,Y lands on SID-MIRRORED registers (($55+d4point) &
$1F: V1→$15 cutoff-lo, V2→$1C, V3→$03). cfg.std_glide_hi_reg (low 5 bits,
factory-probed); the composer emits sta $D400+reg,y (mirror-equivalent), and
the freq shadows/lastfreq still track the engine's INTENT (the chip's freq-hi
stays stale exactly as in orig). Verified on Entrail: prefix 17376 → 18948.

## VARIANT CENSUS (2760 members, the factory's probe bytes)
- $2046 (vibrato-skip JMP): $EB ×2694, $DC ×34 (stale-tail), ~19 oddballs
  (likely different builds — triage when batched).
- $1B3F (glide-up hi): $01 ×2739, $55 ×20 (mirror-write).
- $1B20 (glide-down hi): $01 ×2759 — no variant.
- init JMP target: $2108 ×1245, $2000 ×972, + tail — IRRELEVANT under
  universal_reset except where end-of-init STATE differs (trichotomy
  Check-A catches per tune; the host default now includes $D418=$0F).

## ✅ FILTER bit-SET path DONE (2026-06-10) — Entrail prefix 18948 → 49752
Representation: the standard filter maps into the EXISTING Tel
filter_programs envelope shape (same musical concept: init cutoff + ramp
segments + final hold) grown along the musical axis: the grammar's fp_seg
count is now variable (Tel 3 / standard 4) + an optional `onset=` threshold
(band-0 entry; Tel programs omit it = 0). Decoder: filter_prog_format=
'standard' reads the 12 bytes at filterbytes_addr ($1E89 reloc'd, now in
_RELOC_FIELDS) → progs[0] {init=cut[0], onset=thr[0], segs=(thr[k],cut[k])
k=1..4, end=thr[5], final=cut[5]} — only when some inst has +7 bit0.
Emitter: gated 12-byte [6 cutoffs][6 thresholds] section + std_filter
equate. Chain block (the stdw_waveprog slot): descending threshold scan;
band 5 absolute; bands 4..1 cutoff-shadow += add (flt_sto,x = orig $2169);
band 0 absolute + the $D417 write ($D417 = filt_ctr + mask when (filt_ctr
& mask)==0; mask = voice0?1:voice<<1); below onset = no write; bit-CLEAR =
the latched-voice $FF default (kept). filt_ctr = orig $2172: seeded $B0
after ok2 in the universal_reset song-init (engine bookkeeping init),
reset 0 at any sequence-$FF wrap. $D417/$D416 are chain-armed pendings
(filt_pend17/filt_pend) consumed by nextvoice between PW and freq —
$D417 FIRST (orig $1C4B before $1C78).

## ENTRAIL TRIAGE (2026-06-10) — one fixed, one open
✅ FIXED — the GLIDE EMISSION ORDER bug (prefix 49752 → 53174): the
composer's parser, after a $Cx instrument, checks only $8x-or-note (the
orig's structure); my encode emitted [len][instr][$Ex...] so the $Ex
straight after the instrument was misread as a LENGTH and the glide's
PARAM byte became the NOTE (V2 played $30=48 instead of $32=50; reb noho
probe confirmed). The orig editor always emits [instr][len][$Ex] — a
length byte re-dispatches fully, making $Ex reachable. encode_pattern's
standard glide branch now emits instr first + the length UNCONDITIONALLY
(idempotent nootleng re-set) before the $Ex triple.

✅ RESOLVED (2026-06-10) — ENTRAIL FULL: play 127162/127162, audio✓. The
$70C7 mystery = the **fx3-bit2 +$04 ARPEGGIO** ($1D1E-$1D51), the last
unimplemented chain effect. Found via the NEW EVENT-ALIGNED STATE DIFFER
(below), which proved NO semantic-state divergence across all 3676 play
events — meaning the missing write was stateless-looking → an unemitted
effect. Semantics:
- fx3 bit2: per-note counter (orig $2161,x, set to 3 at note FETCH
  $18D8) cycles 2→1→0→2; freq = freqtab[noho + arp3[counter]] written
  lo,hi DIRECT every frame ($1D42; position after the $80 restore,
  before ctrl). $70C7 = freq[74+7] ✓.
- arp3 = the 3 bytes at orig $1E86-$1E88: slot 0 STATIC image data;
  slots 1-2 REWRITTEN by every vibrato-skipped instrument's $2030 path
  (fx1 hi/lo nibbles, or $0C/$18 when fx1==0 — last runner wins). THIS
  is what the $2030 routine is for.
- Reached by every non-wave inst (bit7-clear via $1CE8→$1D1E; the $80
  restore falls through; the $80 ATTACK and wave insts skip to $1D52).
- $80+bit2 insts write BOTH pairs per frame (restore then arp) →
  composer fw_mode=3 (double-pair dispatch in nextvoice).
- Composer: arp3_ctr per-voice (3 at note fetch in h3f_pattern),
  arp3_tab seeded from the baked image bytes at song-init
  (cfg.std_arp3_init, factory-probed; both Jarre/Entrail = 00 00 01),
  slot rewrites in the chain's stdvib_skip path.
Two red herrings en route: the "one frame longer note" (memwatch
sampling skew) and the $70C7-vs-trajectories puzzle (it's a third
effect's write). Also benign-by-construction: counter2 snapshot offset
(orig INCs all 3 at frame top BEFORE the $D418 write; the composer now
matches for the standard layout — RAM-only, stream-neutral) and the
baked $1AF8 glide threshold (editor leftover, dead until the first $Ex).

## SAMPLE TRIAGE round 2 (2026-06-11) — 7/12 FULL
Three new family findings (each unlocked multiple tunes):
1. **$D416-write variant** (the opcode at orig $1C78, the filter chain's
   final SID write — the $2169,x shadow before it is never patched):
   $8D normal ×2748 / $EA NOPed-out ×8 / $20 JSR-hook ×2 (FBI: LDA #$10;
   STA $D416; RTS = a CONSTANT override; one unrecognized hook:
   JBs_Freak-Out). cfg.std_d416_mode ('normal'/'none'/'const') +
   std_d416_const, factory-probed. FBI 0.03% → 95.45% on this alone.
2. **Loop-pickup transpose** (USF `loop@N+T`, schema growth on
   Orderlist.loop_transpose): the engine's transpose CARRIES OVER the
   $FF wrap. An inherited loop head (no $80 byte — FBI) plays passes 2+
   under the end-of-list transpose; an explicit head (Prato) re-
   establishes. Resolved per-entry transposes can't express the
   difference — the new terminator carries it. Extract: explicit-head
   detection; encode: omit the head byte iff loop_transpose set (an
   inherited head always resolved to 0 on pass 1). NB the analogous
   PERSISTED-LENGTH carry-over across the wrap (nootleng) is NOT yet
   modeled — pass-2 head patterns entered with a different persisted
   length would need a (fc_id, init_len) pattern the extract never
   created. Surface when a tune exhibits it.
3. state_map_gen's label build now mirrors the composer's contiguous
   base-float (FBI's layout needed the widen-retry).
REMAINING sample fails (5): Intense_Intro (1/84040), Exquisite_2
(0/80760), Obelisk_1 (1/130975), Eurodance_Remix (99712/265150),
Deneb (3 subtunes, all ~1). Triage next, write-log-first.

## SAMPLE TRIAGE round 3 (2026-06-11) — 10/12 FULL
Three more findings (Intense, Exquisite_2, Eurodance_Remix + Deneb[2]):
1. **filt_pend $00 limitation**: $D416=$00 is a real cutoff (Intense's
   envelope hits 0); the pending VALUE can't double as the flag → new
   filt_pend_f armed/consumed alongside it.
2. **freq_overrun** (USF block, content-by-reference): the wave-RELATIVE
   mode / +$04 arp index `freqtab[note+offset]` with an 8-BIT index —
   off-table indices (96..255) read the orig's bytes AFTER the freq
   tables (e.g. Intense: hinote[110] = the $1E32 wavearp byte $40). The
   extract captures the 160 image bytes after hinote; the composer emits
   them right after its hinote so off-table lookups resolve to the same
   values (lonote's overrun is covered by lo/hi adjacency). The same
   argument as pulse-prog-by-reference, scaled up: the player indexes
   blindly; what it reads IS what plays.
3. **Wrapper inits / multi-song** (runtime_slot): some members' init
   installs the active subtune's 6-byte seq record into the $1EA1 slot
   from a side table (Intense: copy-loop at image+$800 with $2174=1;
   Deneb: songs=3). The factory detects via py65 ground truth (run the
   PSID init once, compare the post-init slot vs the static record;
   songs>1 ⇒ wrapper by construction) → subtune_layout='runtime_slot'
   (extract reads post-init memory per subtune; engine_model now
   supports runtime_slot on single-engine SIDs).
REMAINING: Obelisk_1 (1/130975), Deneb subs 0/1 (1/162616, 1/35927).

## SAMPLE TRIAGE round 4 (2026-06-11) — 12/12 FULL ✅✅
The last two findings:
1. **Pulse prog "0"** (Obelisk): my fx2&7==0 → default-step shortcut was
   Jarre-specific. The orig indexes pulsetabel+$FC (8-bit (0-1)*4) and
   the 4 bytes THERE form the instrument's effective program — Obelisk's
   are [11 12 13 10] → step1=$12 (Jarre's are zeros → default, which is
   why the shortcut ever worked; Prato's fx2&7==0 insts have fx2==0 =
   no pulse at all). Captured by value as prog 0; emitted in slot
   kmax+1; the chain remaps n==0 via the pulse_prog0_slot equate.
2. **Tel h11 ADSR-release suppressed for the standard layout** (Deneb
   subs 0/1): the shared h11 path force-writes SR=h11_release_sr_value
   when pulsehitemp bit 4 is set at note-end — a TEL feature. Standard
   instruments freely use raw[0] bit 4 (it's just the PW-hi nibble
   range), so Deneb emitted a spurious SR=$02. The block is Tel-only
   now ({h11_release} template var).
Both diagnosed in minutes with the established loop: manual aligned
flat-compare (insertion/value shape) → event-aligned state differ →
inst/program probe.

### THE TOOL (built for this): event-aligned state diff
`tools/state_diff.py --on-write D418 --align-value 1F` — snapshots at
every write to the trigger register and compares by GLOBAL EVENT INDEX
(one event per play() for the standard player) — NO frame bucketing, NO
Trap C. Map via `tools/state_map_gen.py --engine standard --sid SID.sid`
(NEW --sid: per-member rebuild layout + orig reloc shift; annotation in
standard/state_map.py — stream CURSORS tabcount/begcount intentionally
unmapped, the composer re-encodes streams). "NO STATE DIVERGENCE +
write divergence" = a missing/extra EFFECT EMISSION — exactly how this
case cracked.

⚠ LATENT (found while triaging, unexercised by the sample): the orig
parser, after an $Ex's param, FALLS INTO the $Cx/$8x dispatch ($192E →
L_1930) — the glide's 3rd byte can be a command, not a note. My
_parse_pattern_standard assumes 3rd-byte-is-note. All Entrail/sample
glides have note 3rd-bytes; fix when a family SID hits it (the decoder
should re-dispatch $Cx/$8x after the param like the orig).

## (RE preserved below for reference)
### the FILTER bit-SET path — COMPLETE RE (incl. $2172)
Routine $1BFE-$1C78, table $1E89 = 12 bytes [6 cutoffs][6 thresholds],
ctr = counter2 (frames since note):
- inst +7 bit0 SET: latch filtvoice=this voice ($2175). Scan thresholds
  DESCENDING: ctr >= thr[5] → cutoff[5] ABSOLUTE → $D416 (+$2169,x shadow);
  thr[k] (k=4..1) → cutoff = $2169,x + table[k] INCREMENTAL → $D416;
  ctr >= thr[0] (band 0) → $D417 RES/ROUTING FIRST: mask = voice==0 ? 1 :
  voice<<1; if ($2172 & mask)==0 → $D417 = $2172 + mask; then cutoff[0]
  ABSOLUTE → $D416. ctr < thr[0] → NO write this frame.
- $2172: INIT CONSTANT $B0 (sub_20D9 — engine bookkeeping init, the
  composer's song-init must seed it for the standard layout); RESET to 0
  at any voice's sequence-$FF wrap ($1886). So $D417 = $B1/$B2/$B4 before
  the first wrap (resonance 11 + routing bit), mask-only after.
- bit0 CLEAR: the already-implemented filtvoice==voice → $D416=$FF default.
REPRESENTATION QUESTION (do the schema-discipline checklist first): the
standard filter is ONE 12-byte 6-band envelope; Tel filter_programs is a
ptr table → 10-byte programs (3 segs + init/final/d418/end). Either extend
filter_programs to a variable seg count (musical-axis growth) or carry the
6 (threshold, cutoff, absolute|incremental) bands; the $2172/$D417
mechanism is ENGINE (emitter), only the bands are content.
Blocks Entrail @18948/127140; likely other sample tunes too.
First divergence (find_first_divergence Jarre_2 vs reb, frame 1, SID V3):
  orig: V3 PW=$01C0 (pulse sweep), freq=$4800, ctrl=$81 ; V2 PW=$0240, ctrl=$41
  reb : V3 PW=$0000, ctrl=$00, NO freq ; (effects not emitting)
Jarre_2's opening exercises THREE effects at once (instrument +7 = effect-flags):
  - inst4 (V0/pat5): wave program, bit4 $10. fx1($2153)=$01 → sel1, absolute mode.
  - inst1 (V1/pat6): the $40 effect, bit6 $40.
  - inst7 (V2/pat7-9): the $80 effect, bit7 $80. (inst9: + filter bit0 $01.)
Effect-flag map (fx3=+7): $40→inst 1,6,8 · $10(wave)→inst 2,3,4 · $80→inst 5,7,9
· $01(filter)→inst 9.

**$40 effect** ($1BE0-$1BFA, decoded 2026-06-10): gated by +7 bit6. Reads voice
frame-counter $2142,x; if <3 → SKIP (silent first 3 frames); else selector =
counter&3 → ctrl = $1E32[selector] → $2179,x → $D404. A 4-entry ctrl/waveform
CYCLE (writes ONLY ctrl, no freq/PW). $1E32 = 4-byte table.

To align Jarre_2 the chain needs (in some order): wave-program ctrl (gated/done)
+ FREQ part + modes; the $40 effect ($1E32); the $80 effect ($1CE3 region); the
standard pulse sweep ($1E95, emitter cut/unverified); filter ($1E89, inst9).

------------------------------------------------------------------------------
## (SUPERSEDED — see above) ⚠ FOUNDATIONAL FINDING (2026-06-09) — the PATTERN FORMAT differs from Tel
While verifying the wave effect (stage 2b), found the reb plays only ~2 notes
(stuck) while orig plays a melody. Root cause: the extract decodes PATTERNS with
TEL semantics, but the standard pattern format is DIFFERENT.

Evidence: pattern 5 (V1) bytes `c4 8b 00 ff`. Tel decode → WaveAdjust($C4),
SetLength($8b), Note(0), End($ff) = 1 note. But the standard parser
($18DD-$1957): a byte is a COMMAND only if `(b & $f0) == $f0` ($Fx); everything
else is a note/range-command. $Ex = 3-byte glide ($18FC), $Cx ($c0-$df) =
command ($1930), lower = note. So `c4`,`8b`,`00` are notes/commands and `ff`
is the lone $Fx command — the pattern is LONGER than the Tel decode sees.

So the SEQUENCE decode is right (standard: $8x=transpose, $00-$7f=pattern,
$fe/$ff markers — matches), but the PATTERN decode is Tel-format and WRONG. The
reb plays the wrong note stream, and NOTHING downstream (base alignment,
wave/pulse/filter) can be verified until this is fixed. (Frame 0 V1 freq
coincidentally matched — the first note — masking it.)

## REVISED SCOPE — the standard player is a DIFFERENT ENGINE, not a config variant
Every layer differs from the Tel composer the FC pipeline grew around:
- PATTERN format ($18DD parser: $Fx commands, $Ex glide triples, $Cx range,
  note+length encoding) — DIFFERENT, extract decodes it wrong. ← foundational
- INSTRUMENT format (+5/+6/+7 = wave-sel/pulse-default/effect-flags) — DONE.
- EFFECT chain: wave ($10), the $40 effect (inst1 — drives Jarre_2's opening!),
  $80 effect, filter ($01), pulse — multiple per-frame effects by +7 bit.
- WRITE model (conditional freq, vol-first, per-frame wave-program ctrl) — base
  pieces DONE. Order was backwards: built base+effects on a wrong note stream.

## NEXT (corrected priority order):
1. **Standard PATTERN decoder** (extract) — parse $18DD-$1957 semantics
   ($Fx commands incl length/end, $Ex glide triple, $Cx range, note encoding)
   so the reb plays the RIGHT notes. THE foundational fix; re-verify base +
   conditional-freq against a correct note stream after.
2. Instrument EFFECT dispatch: Jarre_2's opening uses inst1 ($40 effect), NOT
   the wave program — implement the $40 effect (~$1BE0) to align the opening;
   the wave effect (done, gated) covers inst2/3/4.
3. Then pulse / filter / $80 effect, then relocation for the family.

## Filter EMITTER: same pattern — gated `standard` filter style emitting the
6-band cutoff envelope ($1E89) → $D416/$D417. Spec above (after base aligns).

## Other tables still to spec when needed
$1E66/$1E76 (per-frame wave/arp), $1E3E/$40/$42/$44 (program-ptr table sel
$2153&$0F), $1E32 (4-byte effect). Map these the same way if Jarre_2 (or
other family members) exercise them.

## ✅ UREADY ROUND A (2026-06-11) — freq_overrun minimization + batch hygiene
1. **freq_overrun reachable-window capture** (engine_model._std_freq_overrun):
   replaced the unconditional 160-byte tail with the set of hinote indices
   the tune can actually REACH. Per-voice orderlist walk (transpose + current
   instrument carried through patterns AND across the $FF wrap, two passes =
   the loop-pickup fixpoint); per-instrument deltas: 0 (note-load), +1
   (vibrato's semitone-delta read, only for vibrato-capable insts), the
   wave-relative freq-program values (entries 0..13), the global arp3
   candidate set (init slots + vibrato-skipped insts' fx1 nibbles + $0C/$18).
   The PAIRING matters: relative-mode programs are full of negative vals
   ($F4..$FD) that only wrap off-table under LOW notes — a naive notes×deltas
   cross product recaptures ~160 for nearly every wave-relative tune; the
   paired walk gives Jarre 0, Intense 11, Exquisite 13, FBI 12, most 0.
   Sample 12/12 FULL + canaries 16/16 after regeneration. Under-capture is
   fail-visible (the next data section sits right after the window).
2. **Factory hygiene** (FCStandardUnsupported, bucketable .reason): the
   factory now detects-and-flags instead of building wrong-shape noise —
   image too short; freq-table probe (SHA1 of the 96 LO bytes at load+$564
   ONLY: the table is per-tune image data — Tyranny carries an edited
   hi[90]=$00; LO-only reproduces the documented membership); entry shape
   (init ∈ {0, load, $2108+delta} — ~50 members point init straight at the
   stock routine — play = load+6); CIA speed bits; oddball $2046 operands
   ($00 ×6, $C9 ×3, $18 ×2); unrecognized/oddball $1C78 ($D416) hooks
   (JBs_Freak-Out JSR $2080). Probe over all 4024 FC SIDs: 2672 members /
   1352 flagged (82 too-short, 11 play=load+3, 5 play=load+$2A, singles).
