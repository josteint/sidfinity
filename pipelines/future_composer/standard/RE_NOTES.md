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

## Filter EMITTER: same pattern — gated `standard` filter style emitting the
6-band cutoff envelope ($1E89) → $D416/$D417. Spec above (after base aligns).

## Other tables still to spec when needed
$1E66/$1E76 (per-frame wave/arp), $1E3E/$40/$42/$44 (program-ptr table sel
$2153&$0F), $1E32 (4-byte effect). Map these the same way if Jarre_2 (or
other family members) exercise them.
