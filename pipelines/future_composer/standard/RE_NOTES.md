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

## ⚠ FOUNDATIONAL FINDING (2026-06-09) — the PATTERN FORMAT differs from Tel
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
