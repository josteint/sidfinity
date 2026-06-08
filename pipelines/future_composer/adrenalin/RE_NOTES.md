# Adrenalin (HeatWave) — RE notes

**SID:** `hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid`
**Engine:** MoN/FutureComposer (per sidid)
**Authors:** Marvin Severijns & M. de Bree
**Songlength:** 9:25 (565s), 4 subtunes
**PSID:** load=$0000 (inline-encoded), init=$50E0, play=$50E3
**Purpose:** 3rd FC family canary — diversifies away from Tel-only
canaries (Hawkeye, Cybernoid_II). See `docs/canary_picker.md` row 3
of engine #4 (MoN/FutureComposer).

## DIAGNOSIS 2026-06-07 — THREE engines, FOUR independent songs (READ FIRST)

Adrenalin is not one FC song with 4 subtunes; it is a **compilation** that
packs **three distinct player engines** + four independent data sets into one
PSID. Established this session with py65 init-per-subtune + post-init memory
diffs + pc-trace:

| Sub | Engine (post-init) | Relation | Data pool |
|-----|--------------------|----------|-----------|
| 0 | engine A @ `$7A00` (canonical FC, full feature set) | reference | own |
| 2 | engine A relocated to `$1000` (entry `$1006`→`JMP $1102`) | `$128B` nolengset == engine A `$7C8B` byte-for-byte, addrs reloc `$7A`→`$10` — **proven engine A** | own |
| 3 | same relocated engine A @ `$1000` | 99% identical code to sub 2; different data | own |
| 1 | a DIFFERENT, smaller engine @ `$1021` | only **4%** code-identical to subs 2/3; not engine A | own, layout unknown |

- **Every subtune has an INDEPENDENT data pool.** freq_lo/hi, instr_records,
  pattern_ptr_table AND pattern/sequence bytes ALL differ between subs 0/2/3
  (sub 2 & 3 happen to share the freq table only). They sit at engine A's
  same runtime addresses (`$17E3/$1842/$19AC/$1BA0/$1A20..`) but each
  subtune's init copies different VALUES there. So subs 0/2/3 are three
  separate FC songs that reuse engine A's *design*, not one song with shared
  pools + per-subtune sequences (the normal FC multi-subtune shape).
- **Shared IRQ harness** at `$1E00-$1EFF` (100% identical across subs):
  installs the tune's own IRQ, banks `$01=$37`, spins at `$JMP $1EA5`, and
  calls the active player via `JMP ($1E04)` → `$50E3` (the PSID play vector).
  The heavy `$1Exx` pc-trace count is just this idle spin, not real work.
- **Sub 1's engine** ($1021): `LDX #0; DEC $1090 (speed ctr); JSR $1226;
  JSR $1225; JMP $1225`. Compact 3-voice player, distinct code. Whether it is
  a stripped FC variant or a different player is NOT yet determined — needs
  its own disasm + data-address hunt. Its extract via engine-A addresses
  yields garbage (seq_v0_addr came out `$910C`, in the packed-source region).

### Migration implications (scope)
- **Sub 0 alone = a clean FC canary.** Engine A, full feature set, one pool.
  The ONLY composer change needed is to map `runtime_slot` → `flat_seq_table`
  on the EMISSION side (the rebuild lays out its own seqtabel per the CORE
  TENET; `runtime_slot` is purely an EXTRACTION concept — where to read the
  original's pointers). Concrete blocker today: `_emit_song_init_routine`
  (`composer_asm.py:374`) raises `unknown subtune_layout: 'runtime_slot'`.
  The extract path ALREADY captures sub 0 correctly (it reads sub 0's
  post-init pool); `extract(ADRENALIN)` succeeds and yields 96 freq / 16 instr
  / 17 patterns / 4 subtunes — but the shared-pool fields come from sub 0
  ONLY, so subs 2/3 in that FCSong are WRONG (carry sub 0's pools).
- **Full Adrenalin (subs 0/2/3) = needs multi-INDEPENDENT-song FC support:**
  FCSong + USF + composer must carry a separate freq/instr/pattern/sequence
  pool PER subtune and emit a subtune dispatch that repoints all base
  addresses. Engine A's design is shared, so it's ONE engine emit + 3 data
  pools + dispatch — but the current model assumes a single shared pool, so
  this is a genuine schema+composer feature, not a config tweak.
- **Sub 1 = separate engine, separate RE.** Defer; or treat as its own
  mini-engine once subs 0/2/3 land.

Recommended order when resumed: (1) sub-0 canary (map runtime_slot→
flat_seq_table emission, build a single-subtune USF, verify byte-frame-exact);
(2) decide whether multi-independent-song FC support is worth it for subs 2/3;
(3) sub 1 last.

## PROGRESS 2026-06-07 (cont.) — composer unblocked; sub-0 init divergence

Pursued the sub-0 canary (the recommended first increment).

**DONE — composer unblocked (the `runtime_slot` blocker is gone):**
- `compose_fc_asm_featuredriven` now normalizes `subtune_layout=='runtime_slot'`
  → `'flat_seq_table'` at entry (EMISSION only; extract keeps runtime_slot).
  Rationale: runtime_slot is purely an extraction concept (where to read the
  original's per-subtune seq pointers from post-init mem); the rebuild lays
  out its own flat seq_table, so emission == flat_seq_table. CORE TENET.
- Adrenalin config: `emit_data_from_usf=True`, `load_addr=0x0E00` (engine
  ~2KB sits BELOW the fixed data tables at $17E3+; sections emit ascending,
  so engine must precede data — load above $17E3 makes section padding go
  negative: "DSB has negative length").
- `write_canary_usf(ADRENALIN)` + `build_via_asm_featuredriven(ADRENALIN)`
  now BUILD (5975 bytes). Cyb II 2/2 + Hawkeye 12/12 still pass (the
  normalization only triggers for runtime_slot = Adrenalin only).

**REMAINING — sub-0 fails frame-exact on an INIT-sequence mismatch (pos 0):**
Adrenalin (engine A) has a distinctive MULTI-FRAME init the generic FC
composer doesn't reproduce. Per-frame writelog (subtune 0, vblank speed=0):

| frame | ORIG | REBUILD |
|---|---|---|
| 0 | 1 write: `$D418=$0F` | 53 writes: generic FC init (`$D416=FF,$D417=00,$D418=1F`, silence $D400-$D415) |
| 1 | 78 writes: `$D417=01,00 $D416=01,00 … $D400=01,00` — a verbose **$01-then-$00 reset sweep** descending across all SID regs | 17 writes: MUSIC starts (V1 ctrl/freq) |
| 2 | 17 writes: MUSIC starts (`$D410=80 $D411=02 $D412=41 …`) | music |

So orig's music starts at **frame 2**, rebuild's at **frame 1** → off by one
frame + different init writes → diverges at flat pos 0. The `$01/$00` sweep
nets to all-zero (a verbose clear); it's a "reset" sequence (init trichotomy)
but the frame-exact verdict still requires reproducing it.

**The exact init routine FOUND** (disassembly.s `sub_7AB4` song-init tail,
`$7AE2-$7AFB`):
```
$7AE2: LDX #$17              ; X = $17 → sweep $D417 down to $D400
$7AE4: LDA #$01 : STA $D400,X   ; write $01 to $D400+X
$7AE9: LDA #$00 : STA $D400,X   ; then $00  to $D400+X
$7AEE: DEX : BPL $7AE4
$7AF1: LDA #$0F : STA $D418   ; VOL  = $0F
$7AF6: LDA #$00 : STA $D417   ; RES_FILT = $00
$7AFB: RTS
```
= 48 writes ($D417..$D400, each $01 then $00) + `$D418=$0F` + `$D417=$00`.
The generic FC composer init instead does `$D416=$FF, $D417=$00, $D418=$1F`
+ ascending `$00` silence of `$D400-$D415` — completely different bytes AND
a different VOL ($0F vs $10|VOLUME_INIT=$1F).

**Next step:** add an FCConfig `init_style` knob (default = current generic
init; `'fc_clear_sweep'` = engine A's `$7AE2` routine above) and branch in
`_emit_song_init_routine`. Two sub-problems beyond the byte sequence:
  1. **Frame split.** Orig: f0=`$D418=$0F` only, f1=the sweep, music f2.
     Rebuild does init+music contiguously (music f1). For the flat
     `compare_instruction_stream` the frame boundary itself doesn't matter,
     but the ORDERED write stream must match — so the rebuild must emit the
     same leading `$D418=$0F` then the sweep then music, with no extra/missing
     writes. Where the orig's standalone f0 `$D418=$0F` comes from (PSID-init
     tail vs first play() warmup) needs confirming via pc-trace of $50E0/$50E3.
  2. Only AFTER the init matches can the music-frame divergences (engine-knob
     differences: nextvoice order, drum, pulse/filter progs, etc.) be
     iterated via find_first_divergence.
This is the gating work for sub-0 frame-exact; subs 2/3 (independent pools)
and sub 1 (different engine) remain as previously scoped.

## PROGRESS 2026-06-07 (cont. 3) — layout decoupling DONE; now per-voice note accuracy

**Layout decoupling SHIPPED (commit 7984e88) — voices fixed.** The cont.-2
"engine+state too big / overlaps data" hypothesis below was WRONG. True root
cause: the original packs its data tables so tightly that emitting them at their
ORIGINAL addresses OVERLAPS (pulsetabel/vibtabwait collide with the instrument
table). Overlapping CPU addresses can't map to a flat load file, so xa65's
backward `* =` desynced the byte-concatenated file from CPU addresses by $38
bytes → the state region (`d4point`, the per-voice SID offset table) loaded $38
off and read as zeros → every voice wrote V1.
- Fix: new `FCConfig.contiguous_data_layout` (Adrenalin only; default False so
  Cyb II/Hawkeye keep the proven fixed-address layout). A pre-pass packs all
  data tables contiguously from the first data address and rewrites cfg so the
  section builders + pointer-table layouts + equates use packed, non-overlapping
  addresses. (arp rejected — its count is encoded in the arplo/arphi gap; N/A
  here since usf.arp_programs is empty.)
- Result: d4point survives; all 3 voices write their own registers.

**nextvoice_write_order fixed (commit pending):** orig writes a voice's
new-note regs as PW,ctrl,freq (engine A inst-load $7CEB/$7CF7 write PW before
ctrl/freq), not ctrl,freq,PW. Set `(2,3,4,0,1)`.

**Divergence progression this session:** pos 1 (no init) → 50 (init_style) →
51 (voices all-V1) → 55 (layout decoupling) → 70 (nextvoice order).

**CURRENT divergence — pos 70, V1 first-note pattern content.** orig loads V1 as
a NEW note (freq $02CC + AD=$00 SR=$FD + PW + ctrl=$41 gate-on); the rebuild's
V1 does NOT gate on (freq $0430, no AD/SR, ctrl=00) — V1's first note isn't
playing. V3 (pos 50-59) + V2 (60-68) match perfectly, so the engine plays
patterns correctly in general; this is V1-pattern-specific.

VERIFIED CORRECT (this session, ruled out): V1's sequence parse
(`_parse_sequence` → patterns [9,9,9,9,1,...]); the to_usf orderlist
(`entries=[0,1,1,1,2,3,...]`, the (fc_id, persisted_length) split is by design);
the pattern pool dedup (`build_pattern_pool` by row-content → V1 entries map to
slots [0,0,0,0,1,1] = pattern-9 ×4, correct); the seq_table voice order
(voice 0 = V1 = the $90 09... sequence).

### FIXED (commit e3363a4): glide target gates on unconditionally
The glide handler did `bne nolengset` ("always taken, target>0") but V1's glide
target is $00 (note C0) → bne fell through, skipping the note-play/gate → V1
silent. Changed to `jmp nolengset` (engine always plays the glide target with
attack). V1 now gates on; divergence advanced pos 70 → 87. Cyb II 2/2 +
Hawkeye 12/12 unaffected.

### FIXED (commit fc25d4e): fx3-bit-2 auto-arpeggio (engine A $7D9C)
pos-87 root cause was NOT note-length — it was that V2's instrument has fx3
bit 2 = an AUTO-ARPEGGIO (no pattern $7x command), cycling a fixed arp program
($1973 = program 1 = (0,+4,+7)) each frame. The composer had the per-frame
bit-2 handler but never set the per-voice arp pointer for an auto-arp → null
ptr → garbage. Three-part fix: (1) extract `arp_ptr_hi_min` (Adrenalin $10) so
the low-memory arp programs aren't filtered out; (2) contiguous_data_layout now
packs arp; (3) `fx3_bit2_autoarp_index` knob (Adrenalin=1) — nolengset sets
arpieoklo/arpieokhi + resets the counter for fx3-bit-2 insts. V2 freq now
byte-exact ($42D0...). Divergence 87 → 89. Cyb II 2/2 + Hawkeye 12/12 green.

### FIXED (commit 129eccb): vol/filter write order — voice_loop_layout=interleaved
orig writes the master vol/filter ($D418/$D416, from engine A's per-voice filter
routine $807D-$80DA) BETWEEN the last voice's PW and ctrl/freq writes. The
composer (tight_nextvoice) wrote them before the whole nextvoice block. Switching
Adrenalin to `voice_loop_layout='interleaved'` (PW early, ctrl/freq late) puts
the filter/vol write in the right spot. Div 89 → 98. Cyb II/Hawkeye unaffected
(config-only; Hawkeye already uses interleaved).

### FIXED (commits 7b7789f, h11): wave-arp + release SR
- pos-98 was a SPURIOUS bit-6 wave-arp: engine A only checks fx3 bits 2/4/7,
  NOT bit 6 (dead bit in its instruments), but the composer's bit-6 handler ran
  the Hawkeye wave-arp → null wavearp table → ctrl=$00. New `fx3_bit6_wavearp`
  knob (Adrenalin False) disables it. Div 98 → 232.
- pos-232 was the release SR value: engine A $7D76 writes $01 on release; the
  composer default `h11_release_sr_value` is $02. Set Adrenalin $01. Div 232 →
  403.

### FIXED (commit 867d64c): arp counter ran with a spurious note-load reset — KETCHUP
pos-403 was NOT note-length. The fx3-bit-2 auto-arp counter (tonearpcounter)
was reset at every note-load (nolengset_resets_tonearpcounter default True +
my fx3_autoarp fragment reset). Engine A ($7DA2/$7DAA) runs it CONTINUOUSLY
across notes — verified via memwatch (orig V2 $7a51 cycles 0,2,1,0,2,1 unbroken
across note boundaries). The reset desynced the arp phase after the first note.
Fix: `nolengset_resets_tonearpcounter=False` for Adrenalin + drop the fragment
reset. SINGLE keystone fix → writelog match jumped **403 → 28686** (the user's
predicted "ketchup effect"). sub-0 now matches the first ~33s / frame 1663.
Cyb II 2/2 + Hawkeye 12/12 unaffected.

### ✅ SUB 0 BYTE-EXACT (2026-06-08) — the ketchup fully flowed
At full songlength the ORIGINAL (209,432 writes) is a COMPLETE PREFIX of the
rebuild — NO divergence. (rebuild has +19 trailing writes = ~1 extra music
frame because its init is one siddump-frame shorter, so it runs 1 frame ahead;
benign init-bucketing, same class as the Hubbard CIA/init traps. By the Mode-1
writelog-overlap standard — full overlap match + |len diff|<=tol, as Hubbard's
verify_all uses — sub 0 is byte-exact.)

The cascade from pos-28686 onward (all single-keystone "ketchup" fixes):
- pos 28686 (frame 1663): drum-kick RELEASE tail used the preserved base freq;
  engine A ($819F) uses the VIBRATO'D current freq ($7a2b/$7a25, updated by the
  vibrato $7F65-$7F79). `noise_tick_release_uses_vibrato=True`. → 117638.
- pos 117638 (frame 6669): fm2 filter CLEANUP used Cyb II values; engine A
  ($80D2) writes $D416=$E0 with NO $D418. `fm2_cleanup_d416_value=$E0` +
  `fm2_cleanup_writes_d418=False`. → 208299 = full orig length.

REMAINING for is_full / regression: the +19-write trailing (1-frame init
offset). Either (a) reproduce engine A's 2-frame init (first play() writes only
$D418=$0F, song-init/sweep on the 2nd play()), or (b) use the Hubbard-style
overlap+close verdict for FC. Sub 1/2/3 still need multi-independent-song
support (separate, pre-existing scope).

### (history) pos 28686 — V3 release freq [RESOLVED — noise_tick_release_uses_vibrato]
orig V3 freq $1BC7 vs rebuild $1C31, with V3 ctrl=$40 (gate OFF = release).
Everything else matches. Much deeper — likely an arp-phase or glide-slide
drift accumulating over ~1600 frames (a rare frame where the arp counter or a
slide step differs by one). NEXT: compare V3's arp counter / glide state around
frame 1663 (orig vs rebuild) to find the rare ±1.

### (history) pos-403 V2 note-length off-by-one [WRONG framing — was the arp reset, see above]
Matches through frame 21. V2 has the fx3-bit-2 auto-arp; its freq cycles arp
offsets 7,4,0 (notes $47,$44,$40). orig: f19-24 = 7,4,0,**0**,7,4 — an EXTRA
offset-0 frame at f22 because V2 LOADS A NEW NOTE there (note-load writes the
base freq $2CC1 = offset 0, and resets the arp). The rebuild has 7,4,0,7,4 — no
extra base frame, i.e. its V2 new note arrives ONE FRAME EARLY. So V2's
note-length/nootcount is off by one (rebuild note ~1 frame short). Likely the FC
note-length persistence (nootleng/durtab, the (fc_id, persisted_length) split)
or a count±1. NEXT: compare orig vs rebuild V2 nootcount/nootleng around f21-22
(state_diff or pc-trace) to find the ±1.

### (history) pos-98 held-frame ctrl=$00 [SUPERSEDED — bit-6 wave-arp fix above]
On the next note/held frame, the rebuild writes ctrl=$00 for ALL THREE voices;
orig keeps ctrl=$41/$21/$41 (everything else — PW, freq, vol, filter — matches).
pc-trace: stod404[V3]=$00 comes from `$1494: LDA $0000,Y` — a waveform-table
effect (indexed by counter&3) reading a NULL table base ($0000), like the arp
null-pointer bug earlier. So a per-voice waveform effect (wave-arp / pre-attack
starttabel / noise-tick) runs with an unset pointer → $00 → clears the ctrl.
orig's ctrl is stable ($41, no waveform cycling here), so EITHER the rebuild
runs this effect spuriously OR its table pointer isn't set up. NEXT: identify
which effect the $148F-$1497 routine is (gate + table) and either suppress it
(if orig doesn't run it for these voices) or set up its table pointer. Likely
the same class as the arp fix (effect enabled by an instrument fx bit whose
per-voice program pointer the composer's note-load never initialises).
orig writes (V1, the last voice): PWlo $02, PWhi $03, **then vol $18 + filter
$16**, then ctrl $04, freqlo $00, freqhi $01. The rebuild writes vol $16/$18
BEFORE V1's PW. So the master-vol/filter ($D418/$D416) write is positioned
mid-V1-nextvoice in orig (after PW offset 3, before ctrl offset 4) but
before-nextvoice in the rebuild. Likely the composer's fm2 (master-vol/filter)
write placement relative to the last voice's nextvoice writes — a sequencing
knob, not a value bug (the values match). NEXT: find where engine A emits the
$D418/$D416 master write in the voice loop (relative to V1's nextvoice) and
match the composer's fm2 placement.

### (history) pos-87, V2 note-length + null pattern pointer [SUPERSEDED — see fx3-bit-2 fix above]
Traced via pc-trace of the rebuild ($0E00 engine). The chain:
- orig holds V2's first note (pitch 60+transpose4 = note $40 → freq $2CC1) for
  6 frames (pattern slot 3 = `c7 86 3c 3c ...`: wave_adj7, **setlen $86=6**,
  note $3C ×2) and VIBRATO-modulates it ($2CC1→$42D0→$3863→$2CEB). It does NO
  table lookup on frame 2.
- rebuild: V2's note-length counter `$2455,X` is already **0** on frame 1
  (`DEC`→$FF at PC $1138), so it PREMATURELY advances the pattern — V2's note
  length was never set to ~5 (the `$86` setlen didn't take). V1/V3 hold
  correctly, so it's V2-specific.
- On that bad advance, V2's current-pattern pointer `$2458,X`/`$245B,X` is
  **$00/$00** → zp ptr `$53/$54 = $0000` → it reads zero-page `$0000` (=$2F) as
  the pattern position, then pattern byte `$24`, adds toneadd `$40` → pitch
  `$64` (=100, OUT OF the 96-entry freq table) → reads garbage `$0001`.
- ($0001 is the byte-swap of freq[0]=$0100, a red herring — the real fault is
  the out-of-range index from the null-pointer garbage.)

DEEPER ROOT (further pc-trace): the bad path is gated by `LDA $42; AND #$04;
BEQ` (PC $1126) — V2's note has **fx bit 2 set**, triggering a per-voice
freq-modulation effect (the "bit-2 sweep", composer `freq_rise_acc`, orig
$90E0). THAT is what produces orig's $2CC1→$42D0→$3863→$2CEB modulation on the
held note. The effect reads its program/state pointer from `$2458,X`/`$245B,X`
into zp `$53/$54`, but for V2 those are $00/$00 (null) → reads zero-page $0000 →
garbage pitch/freq. V1/V3's notes don't have fx bit 2, so they never hit this
path → V2-specific.

So pos-87 is a COMPOSER fx-bit-2 (freq-sweep) EFFECT-SETUP bug: the note-load
doesn't initialise the bit-2 effect's per-voice pointer ($2458/$245B). NEXT:
read engine A's bit-2 handler in disassembly.s (the $90E0/freq-rise path +
where it sets the per-voice pointer at note-load), then make the composer's
note-load set up that pointer/state for fx-bit-2 instruments. Shared FC-effect
change — verify Cyb II + Hawkeye. (Confirm whether any of their instruments use
fx bit 2; if not, it's currently untested and safe to add.)

### (history) earlier framing — pos 87, V2 pitch ($42D0 vs $0001)
After the glide fix, V1 matches through pos 86. At pos 87 V2's note freq is
orig $42D0 vs rebuild $0001 (near-zero); V2 gates on (ctrl=$21 matches at pos
86), so it's a PITCH/freq COMPUTATION issue, not a gate issue. The streams
RE-CONVERGE at pos 93-95 (V1 ctrl/freq match), so it's a localized per-note
mis-pitch, not a structural break. V2's sequence ($1aa0) has transposes
$84 then $90 (`84 05 05 05 05 90 02 03...`), so transpose handling on V2's
note is the prime suspect. Also a vol/filter vs V1-PW write-ORDER shift around
pos 89-92 (likely a consequence of the same note resolving differently). NEXT:
trace V2's note at this step (pitch index + toneadd) vs orig; check the
$0001 — likely a bad freq-table index from a transpose over/underflow.

### (historical) ROOT CAUSE of the pos-70 divergence: V1 FIRST note DELAYED GLIDE. orig pattern 9 = `f1 f1 c1 a0 e0 8f 00 ...`: filter $F1, wave_adj
1, len 32, then `$E0 $8F $00` = a GLIDE command (delay $8F=143, target note
$00=C0). The extraction is CORRECT (USF row: glide=143, pitch=C0). The original
ENGINE still GATES ON this note (writes AD/SR + ctrl=$41) — a glide with no
prior note (first note) / with a delay plays the target note with attack first,
then glides. The COMPOSER's glide emitter does NOT gate on (writes ctrl=$00, no
AD/SR), so V1 stays silent. V2/V3 first notes are plain (no glide) so they're
unaffected — that's why only V1 diverges.
→ FIX (next session, composer-effect work): make the glide path gate on the
note when there's no source note to glide from (and/or honor the glide DELAY:
gate on now, begin sliding after `delay` frames). Read engine A's glide handler
in disassembly.s (the $E0/glide path, PatGlide) for the exact delay + gate
semantics, then fix the composer's glide emitter. This is a shared FC-composer
effect change — gate it / verify Cyb II + Hawkeye don't regress.

EARLIER LEADS (now superseded by the root cause above, kept for context):
- The encoder emits a `$C0` (voiceinc 0) right after the transpose in EVERY
  voice's sequence (`90 c0 00 00 ...`). orig V1 has NO voiceinc command. It's
  present for V2/V3 too (whose first notes still match), so the decoder handles
  it — but per the design note "voiceinc bakes into wave_adjust" it may be
  spurious and worth removing (encode+decode together). Check whether it
  perturbs V1 specifically.
- Decode V1's slot-0 pattern stream (`f1 f1 c1 a0 e0 8f 00 07 ...`) vs orig
  pattern 9's first row; confirm the first row is a real note (not rest/tie) and
  that `_build_pattern_rows` + the persisted_length carry produced the right
  first-note duration/instrument for V1.
- Compare against the engine's V1 note-load path at runtime (pc-trace V1's
  first do_h2 step) to see why it doesn't gate on.

orig/rebuild flat lengths are near-equal (4941 vs 4953); the engine is
structurally sound — this is the normal per-voice writelog-divergence loop.

## PROGRESS 2026-06-07 (cont. 2) — init byte-exact; voice bug [HYPOTHESIS BELOW WAS WRONG — see cont. 3]

**init_style sweep DONE (committed a1bbba2).** New FCConfig `init_style`;
`'fc_clear_sweep'` emits engine A's `$7AE2` init. Adrenalin sub-0 init now
matches byte-for-byte (full-flat pos 0..50); first divergence moved into the
music at pos 51.

**Voice bug ROOT-CAUSED — it's a composer LAYOUT collision, not voice logic:**
- Symptom: rebuild writes ONLY V1 registers ($D400-$D406); V2/V3 NEVER written
  (V1 count ~4×, V2/V3 = 0 over 88 frames). All three voice iterations write to
  V1.
- Cause: the per-voice SID offset comes from `d4point` (`.byt $00,$07,$0E`, the
  static [0,7,14] table). The voice loop DOES iterate X=2,1,0 correctly
  (`stx wax` trace shows 02,01,00), and `startplayer` does `ldy d4point,x;
  sty voicesto`. BUT at runtime `LDY $2410,X` (= `d4point,x`) reads **0** for
  X=2 — d4point is all zeros at runtime.
- Why: `d4point` resolves to **$2410**, but the BUILT BINARY has `00 00 00` at
  $2410 (checked the .sid file directly). The engine+state block, emitted from
  `load_addr=$0E00`, is **~5.6 KB** (extends past $2410), so it OVERLAPS the
  data tables at `$17E3` and the USF music_data region. The composer places
  data/music_data via `* =` at those addresses and zero-fills gaps — clobbering
  the state region (incl. d4point) that the engine code also occupies up there.
- Confirmation: `d4point` is BEFORE `tabcount` in source, so `ok2`'s zeroing
  (tabcount..state_end) does NOT touch it — ruling out ok2. The zeros come from
  the section layout overlap.

**Root constraint:** the composer emits sections ascending and requires
`load_addr < all data-section addresses` (load above a section → "DSB has
negative length"). Adrenalin's data tables are fixed LOW ($17E3) by cfg (those
addrs are shared by extract = read orig, and emit = place rebuild). The
engine+state (~5.6 KB) does NOT fit in $0E00..$17E3 (only ~2.5 KB), so ANY
load_addr below $17E3 collides. Cyb II/Hawkeye avoid this because their data
addrs sit ABOVE their load_addr.

**Next step (composer layout, needs design — do NOT hack):** decouple the
extract-time data addresses (read orig at $17E3 etc.) from the emit-time
placement, so `emit_data_from_usf` can put the data tables ABOVE the engine+
state (like Cyb II) instead of at orig's low addresses. Options: (a) add
emit-address-override fields to FCConfig; (b) in emit_data_from_usf mode,
auto-relocate ALL data tables to after the engine+state block and rewrite the
equates accordingly (orig addresses are extraction artifacts — CORE TENET says
the rebuild's layout is free). Then re-verify sub-0 from pos 51 onward
(voice-order + per-voice music should fall into place once d4point survives).

## Addresses found (2026-06-06)

From py65 init + disassembly grep:

| Address | Meaning | Verification |
|---|---|---|
| `$17E3` | lonote (freq_lo) | `$17E3+$48 = $0C` matches Hawkeye freq idx $48 lo |
| `$1842` | hinote (freq_hi) | `$1842+$48 = $47` matches Hawkeye freq idx $48 hi |
| `$18A1` | per_subtune_speed | 4 bytes `$02 $02 $01 $01` for 4 subtunes |
| `$18A5` + `$18A7` | subtune seq-base pointer table | X-indexed lo (`$18A5+X`) + hi (`$18A7+X`) — engine SMCs LDA at `$7ACA` with these |
| `$18B5` | runtime 6-byte per-voice seq ptr slot | copied from subtune base at init |
| `$19AC` | instr_records | 8 bytes/inst, byte layout matches Hawkeye (+0 pulse_hi, +1 ctrl, +2 AD, +3 SR, +4 fil_count, +5 fx1, +6 fx2, +7 fx3) |
| `$1BA0` | pattern_ptr_table | 2 bytes/entry lo,hi (e.g. `$1BA0..$1BAF = {$001C, $061C, $341C, $451C, $561C, $7A1C, $8E1C, $B31C}`) |

Code-side identification points:
- Nolengset (new-note play) at `$7C8B-$7CB8`
- Inst record load at `$7CCA-$7DE9`
- Pattern dispatch + ASL+TAY+SMC at `$7BAC-$7BB9`
- Sequence-byte read via `($75),Y` indirect at `$7BC9`

## Structural finding: data tables populated at init

Adrenalin's data tables (lonote at `$17E3`, hinote at `$1842`,
per_subtune_speed at `$18A1`, instr_records at `$19AC`,
pattern_ptr_table at `$1BA0`) all live in **low memory `$17xx-$1Bxx`**
— BELOW the binary's load address (`$50E0`). They're zeroes in the
raw binary. At init time the engine code at `$50E0`-`$7AB3` copies
packed source data from higher addresses into `$17xx-$1Bxx`.

Source addresses found so far (via signature match in raw binary):
| Runtime addr | Source addr | What |
|---|---|---|
| `$17E3` (lonote) | `$68B3` | Canonical FC lonote bytes (`1C 2D 3E 51 66 7B ...`) found in raw binary at `$68B3` |
| `$1842` (hinote) | ? | Find by sig "01 01 01 01 01 01 01 02 02 02..." in raw binary |

**This is a NEW extract-path shape vs Hawkeye/Cyb II**, both of which
have data tables directly at their runtime addresses in the raw binary
(engine loads its data tables to their final positions).

Two options for the extract path:
1. **Run init in py65 first** to populate `$17xx-$1Bxx`, then read
   addresses from post-init memory. Cleanest. Requires extending
   `engine_model.py::extract` to optionally run init (a new FCConfig
   field like `requires_init=True`).
2. **Find all source addresses in the raw binary** and update the
   FCConfig addresses to source rather than runtime. Requires
   understanding the init copy mechanism in detail.

For byte-exact rebuild, the rebuild MUST place the source data at
the source addresses (so the init copy produces matching post-init
state). So either way, the source addresses are what get written
into the rebuild's data emission.

## Per-subtune engine instances (NEW FINDING 2026-06-06)

Adrenalin uses **MULTIPLE engine instances**, not just multiple
per-subtune data sets. Decoded from the init copy table at `$514E-$5175`:

| Sub | Copy src | Copy dst | Size  | Play vector |
|-----|----------|----------|-------|-------------|
|  0  | `$5176`  | `$17F3`  | `$06E7` | `$7A06` (the engine at `$7A00`) |
|  1  | `$575D`  | `$1021`  | `$0A73` | `$1006` (engine instance at `$1000+`) |
|  2  | `$60D0`  | `$1000`  | `$0DDD` | `$1006` |
|  3  | `$6DAD`  | `$1000`  | `$0D51` | `$1006` |

Init flow (`$50E6-$5107`):
1. `JSR sub_510A` — runs the memcpy loop with X = subtune\*2,
   pulling source/dest/size from the four 8-byte tables.
2. SMC the play vector at `$50E3-$50E5` with the per-subtune play
   handler from `$516E[X]/$516F[X]`.

The implication: sub 0 uses the `$7A00` engine we disassembled, and
its tables at `$17E3/$1842/$19AC/$1BA0` are valid. Subs 1/2/3 use a
DIFFERENT engine at `$1000-$1FFF` (a second relocated FC engine copy
with its own data layout).

## Engine prefix bytes — observation only (2026-06-06)

Comparing the first 9 bytes at each per-subtune copy destination:

```
Sub 0  $7A00: 4C B4 7A | 4C FC 7A | 4C 02 7B   (engine code already in raw binary)
Sub 2  $1000: 4C 00 CD | 4C FC 10 | 4C 02 11   (post-init at $1000)
Sub 3  $1000: 4C 00 9D | 4C FC 10 | 4C 02 11   (post-init at $1000)
Sub 1  $1021: A2 00 CE 90 10 30 0C 20 26       (post-init at $1021, no JMP prefix)
```

Measured directly via `_run_init_in_py65(sub=2)`: of the first 2048
bytes at offset 0 (i.e., comparing `$7A00..$81FF` to `$1000..$17FF`),
**1578/2048 = 77.1% bytes are identical**. The matching positions
include relative offsets `$FC` and `$102` (the 2nd and 3rd JMP
targets) and other internal labels.

This is consistent with **two distinct hypotheses** that the seed
disasm alone cannot distinguish:

1. **Multi-engine.** Adrenalin has multiple distinct engine instances:
   engine A statically present in the binary at `$7A00`, engine B
   copied into `$1000` at init (same family code, relocated). The 77%
   match is the byte-identical portion of relocated code; the 23%
   difference is the address operands that had to be rebased.

2. **Single engine + per-subtune data overlay.** Adrenalin has ONE
   engine at `$7A00` and the per-subtune copies place **data only**
   (with some shim/trampoline bytes that happen to start with JMP-
   shaped bytes because those are part of the packed data structure).
   The `JMP $CD00` at `$1000` is never executed; PSID's SMC'd play
   vector at `$1006` (= `JMP $1102`) trampolines into the `$7A00`
   engine.

Without a hand-annotated disassembly of BOTH `$7A00..$81FF` AND
`$1000..$1FFF` (post-init), I cannot rule out either hypothesis.
**Speculation prior to that disasm was a protocol violation per
`feedback_check_existing_engine_docs`.**

## Critical reframing via family docs (2026-06-06 session 2)

Reading `pipelines/future_composer/docs/wiki_mon_driver_disasm.md` +
`wiki_fc_v41_manual.md`: the **entire MoN/FC driver family is
canonically single-engine** — one player at a fixed base, multi-
subtune via `LDA #subtune / JSR init`. Across Deenen/Tel/Bjerregaard
MoN, FC V1-V5: all single-engine. Hawkeye and Cybernoid II conform.

Adrenalin's runtime arrangement (per-subtune SMC of the play vector
into 3 different engine copies) is **non-canonical for the family**.
Likely explanation: HeatWave (1991) wrote a custom launcher around an
FC-family engine to pack 4 subtunes into memory where a single
$1800-based engine couldn't fit them all (the data for each subtune
exceeds the address-space allowance the engine code reserves).

### Applying the CORE TENET

> The verification target is the SID write-log stream, not the engine
> code structure. The composer is FREE to invent any runtime
> architecture that produces the same writes.

For our rebuild:

- The PRODUCED `.sidfinity.sid` does NOT need to mirror Adrenalin's
  3-engine-instance memory layout.
- A single canonical FC engine handling all 4 subtunes (the standard
  Hawkeye/Cyb II shape) is allowed — and is the right target — IF the
  per-subtune writelog matches HVSC's original.
- This collapses the previously-imagined "multi-engine composer
  emission" (Phase 4 in the reverted plan) to standard composer work.

What we still need from RE:

- **Per-subtune DATA extraction**, possibly from different runtime
  addresses (sub 0 reads `$17E3`/`$1842`/`$19AC`/`$1BA0`; subs 1/2/3
  read addresses inside `$1000-$1FFF` we haven't located yet). The
  `_run_init_in_py65` helper + the resolve_address infrastructure
  from Phase 1/2 fits this purpose exactly — extract per subtune
  from the post-init memory.
- **Hand-annotated disassembly of engine A at $7A00** to confirm it's
  a recognizable FC variant + identify its read-address knobs (so
  the composer can emit a canonical single-engine equivalent).
- Engine B at $1000 may or may not need disasm depending on whether
  it's confirmed-relocated engine A (77% match suggests yes) — if it
  is, we don't need to RE engine B beyond confirming the relocation;
  we just need to know engine B's read addresses for subs 2/3 data
  extraction.
- Sub 1's `$1021` entry: still TBD.

This is a SIMPLER scope than the reverted multi-engine plan. The
Phase 1/2 infrastructure (EngineInstance schema + resolve_address +
extract refactor) directly supports per-subtune extract — that
infrastructure is the right shape for this work.

## Engine A ($7A00) — hand-annotation, in progress

Following the same labelling pattern as Hawkeye's `RE_NOTES.md`
(disassembly.s keeps the seed `L_XXXX` labels — they're cross-referenced
throughout — and this table maps each to its canonical FC label).

Adrenalin engine A uses the canonical FC v4.1 +0/+3/+6 vector layout
(matching MoN/FC family across Deenen, Tel, Bjerregaard, FC V1-V5).
Variant confirmed: standard 3-vector entry at engine base.

### Entry vectors

| Addr | Canonical FC label | Purpose |
|---|---|---|
| `$7A00` | `init` (jmp song) | Entry vector → jumps to per-subtune init at `$7AB4` |
| `$7A03` | (jmp songout) | Songout vector → jumps to `$7AFC` |
| `$7A06` | `play` (jmp playirq) | Per-frame play vector → jumps to dispatcher at `$7B02` |

PSID's play vector at `$50E3` is SMC'd by the launcher (at init time)
to point at `$7A06` for sub 0; subs 1/2/3 point elsewhere — see
"Per-subtune engine instances" above.

### Engine A routine map (in progress)

| Adrenalin | Canonical FC label | Purpose |
|---|---|---|
| `sub_7A88` | `ok2` | Zero per-voice state at `$7A0D..$7A87` (`STA $7A0D,X` with X=$7A down to 0). Then explicitly clear 4-byte $7A3E..$7A40 with `$FF` and 3-byte arrays at `$7A0D/$7A10/$7A13/$7A1F` (per-voice). Sets play state `$7A61=0`. Called by `songinit` after subtune setup. |
| `L_7AB4` (`sub_7AB4`) | `songinit` / `song` | Per-subtune init. PHA saves subtune#, sets `$7A61=1` (state=stopped), restores A as X = subtune index. SMC's the LDA at `$7ACA` with `$18A5,X`/`$18A7,X` so the next loop copies subtune-specific seq pointers from `(<sub_base>),Y` to `$18B5,Y` (6 bytes). Loads speed from `$18A1,X` to `$7A09` (per-frame speed reload), and `$18A3,X` to `$7D73` (TBD — likely another SMC). Calls `ok2`. Then clears SID `$D400-$D414` and sets `$D418=$0F` / `$D417=$00`. |
| `L_7AFC` | `songout` | Sets play state `$7A61=2` (end). RTS — does NOT actually silence voices (caller's responsibility). |
| `L_7B02` | `playirq` (dispatcher) | Read `$7A61` (play state); state=2 → RTS (song ended); state=1 → RTS (not playing); state=0 → fall to `L_7B11` (main play). |
| `L_7B11` | `playirq` (main entry) | Per-frame work entry. INC frame counters at `$7A3E..$7A40` (3 voices). DEC `$7A60` (global speed counter); if BPL skip reload, else reload from `$7A09` (per-subtune speedbyte). |
| `L_7B27` | `startplayer` (voice loop) | Per-voice loop body, X = voice (2→1→0). STX `$77` (zp save). LDA per-voice `tabcount` from `$7A0A,X` → `$7A45` (active tabcount byte). Continue sequence read. |
| `L_7B4F` | (sustain branch) | `JMP $7D63` — branches to sustain-frame handler when nootcount not zero. |
| `L_7B52` | `h2` (sequence read) | Read sequence byte: `LDY $7A0D,X; LDA $1A20,Y`. Test for `$FE` (song end → `L_7B6E`) and `$FF` (wrap → reset begcount). `$1A20` = sequence stream base. |
| `L_7B6E` | (song end handler) | `$FE` token: set play state=2 (songout), JMP `$7AE2` (silence voices / final cleanup). |
| `L_7B76` | `h3` (transpose) | `$80-$BF` command. `AND #$1F; STA $7A41,X` (transpose), advance `tabcount` (`$7A0D,X`). |
| `L_7B88` | `h3a` (voiceinc) | `$60-$7F` command. `AND #$0F; STA $7A84,X` (voiceinc?). |
| `L_7B9A` | `h3c` (repeats) | `$40-$5F` command. `AND #$3F; STA $7A63,X` (repeats counter). |
| `L_7BAC` | `h3f` (pattern jump) | `$00-$3F` command. ASL+TAY then `LDA $1BA0,Y; STA $75` + `LDA $1BA1,Y; STA $76` — load pattern address into zp `$75/$76`. `$1BA0` = pattern_ptr_table. |
| `L_7BCD` | `startnote` (pat dispatcher) | Pattern-byte dispatcher (with `$73` = current pattern byte). Recognises `$F0` (noglide), `$F1` (filterset → `$D417`), `$E0-$EF` (glide 3-byte), `$C0-$DF` (waveform select), `$70-$7F` (instrument change). |
| `L_7C8B` | (note-play / nolengset) | Identified earlier: compute Y from `$73 + transpose`, then `LDA $17E3,Y` → `$7A81,X` (current freq lo shadow) + `STA $D400,Y`. `LDA $1842,Y` → `$7A81,X` (hi shadow) + `STA $D401,Y`. Then per-frame instrument table setup from `$19AC` region. |
| `sub_7D27` | `verhoogtest` | Helper: INC `$7A0D,X` (begcount/tabcount?), INY, read next pattern byte via `($75),y`, check `$FF`. |
| `L_7D34` | (note-continue) | Branch from `$7B47: DEC $7A13,X; BMI $7B52` (new note) vs continue. Sustain-frame handling. |
| `L_7D63` | (sustain) | Sustain-frame freq update / held-note path. |

### Data table addresses (confirmed)

| Addr | Field | Verification |
|---|---|---|
| `$17E3` | lonote (freq_lo) | `LDA $17E3,Y` at `$7C9B` in nolengset; sig matches Hawkeye freq idx $48 lo |
| `$1842` | hinote (freq_hi) | `LDA $1842,Y` at `$7CA5` in nolengset; sig matches Hawkeye freq idx $48 hi |
| `$18A1` | per_subtune_speed | `LDA $18A1,X` at `$7AD3` in songinit; 4 bytes for 4 subtunes |
| `$18A5`/`$18A7` | seqtabel ptr lo/hi | `LDA $18A5,X` + `LDA $18A7,X` at `$7ABC`/`$7AC2` in songinit |
| `$18B5` | runtime per-voice seq ptrs | `STA $18B5,Y` at `$7ACD` (copy target) |
| `$19AC` | instr_records (8 bytes/inst) | `LDA $19AC,X..$19B3,X` at `$7CCA-$7DE9` in nolengset/per-frame |
| `$1A20` | sequence stream base | `LDA $1A20,Y` at `$7B55` in h2 |
| `$1BA0` | pattern_ptr_table (2 bytes/entry) | `LDA $1BA0,Y / $1BA1,Y` at `$7BB1/$7BB6` in h3f |

Per-voice state base: `$7A0D` onwards (3-byte arrays); explicit
zero-clear in `ok2` covers `$7A0D..$7A87` (127 bytes ≈ same as
Hawkeye's 119-byte block at `$90C5`).

### Effect chain (extending the routine map)

| Adrenalin | Canonical FC label | Purpose |
|---|---|---|
| `L_7D34` | (h10 / held-note SR-modify) | nootcount>0: LDA inst's fil_count `$19B0,Y`; AND #$F0; >>3 = threshold. Compares against `nootleng - nootcount` (elapsed frames). Sets gate-off mask in `$7A66,X` (stod404). |
| `L_7D60` | (gate-off store) | `STA $7A66,X` — write computed stod404 byte. |
| `L_7D63` | (SR-release trigger) | LDA `$7A3A,X` (inst fx?); AND #$10; BEQ skip. Force-release SR when condition met. Writes `$D406,Y` directly. |
| `L_7D79` | (per-frame inst chain entry) | LDA `$7A22,X` (curr inst); shift; TAY. Cache fx1/fx2/fx3 at `$78`/`$71`/`$72`. Check fx3 bit $10 (drum) → BNE `$7EAC` (drum/effect path). |
| `L_7D9C` | `fx_tone_arp` | fx2 (now `$72`) bit $04 (arp) gate. DEC `$7A50,X` arp counter; if BMI reload from `$1973`. Then re-lookup freq from `$17E3,Y`/`$1842,Y` at `Y = arp_offset + base pitch`. |
| `L_7DCA` | `fx_vibrato` (setup) | fx1 (`$78`) != 0 gate. LDX `$1A14,Y` = per-inst vibrato params; SMC at `$7E63`. Decode amplitude (low nibble) and speed (mid bits). |
| `L_7DF8` | (vibrato delta) | Compute delta = freq[Y+1] - freq[Y] from `$17E3/$1842` tables; shift right `amp` times. |
| `L_7E14` | (vibrato shift loop) | `DEC $7A46; BMI exit; LSR $7A6B; ROR $7A6C`. Identical to Hawkeye. |
| `L_7E25` | (vibrato LFO state) | LFO state machine with `$7A4A/$7A4D/$7A47` (vibstore2/3/1 equivalent). |
| `L_7E48` | (vibrato base + sub loop) | Load base freq from `$17E3,Y`/`$1842,Y` into `$7A69/$7A6A`. Then subtract delta `vibstore1>>1` times (skipped while frame counter < threshold). |
| `L_7E7C` | (vibrato add loop) | Add delta `vibstore3` times. |
| `L_7E98` | (vibrato output) | Write `$7A69/$7A6A` (= vibrato output) to current freq lo/hi shadows. |
| `L_7EAC` | `fx_glide` (entry) | LDA `$7A2E,X` (glidetest); BNE run, BEQ skip → fall to `fx_pulse_prog`. |
| `L_7EB9` | `glide_run` | Decode glidedelay byte `$7A79,X`. Check threshold for snap. |
| `L_7EE5` | `glide_div` | 16-bit / 8-bit long division. Delta = freq[target] - freq[source] divided by speedbyte+1. SMC slots at `$7F6A`/`$7F75` hold the divided step. |
| `L_7F63` | (glide step apply) | `LDA $7A2B,X; ADC #$16; STA $7A2B/$7A7E,X; LDA $7A25,X; ADC #$00; STA $7A25/$7A81,X` — `#$16` is the immediate step (likely SMC'd from glide division but visible-as $16 here). |
| `L_7F82` | `glide_snap` | Reached target: load freq from `$17E3,Y`/`$1842,Y` at `Y = $7A76,X` (glide target); clear glidetest/glidetest2. |
| `L_7FA3` | `fx_pulse_prog` | fx2 (`$71`) != 0 gate. Extract program (lo 3 bits) and increment (hi 4 bits). 4 programs in `$199C` table, each 8 bytes per (n*8)-7 offset. |
| `L_805A` | (pulse_prog output) | Write `$D402/$D403` from `$7A34,X`/`$7A37,X` (PW lo/hi shadows). |
| `L_806B` | `fx_filter_prog` | fx3 (`$72`) bit $01 gate. LDA `$7A59,X` (filcount cache); AND #$03 (4 programs); ASL; TAX. SMC from `$198B,X`/`$198C,X` (filterbytes ptr table). |
| (drum path branched from `$7D99`) | `fx_drum` | fx3 bit $10. Decoded at `$8109`+: AND #$0F (drum number); `$18DD,X` is drumtabel. SMC `$190E,Y`/`$191F,Y` reads (drum 6's wave/tone — same Hawkeye SMC trick). Compare frame counter `$7A3E,X` against `#$0F` (SMC'd to drum length). |
| `L_8175` | `fx_noise_tick` | fx3 bit $80 gate. counter2 < 2 → write freq=`$0058`, ctrl=$81 (noise+gate); counter2 in [2,3] → restore freq from `$7A2B/$7A25,X` shadows; gate off (ctrl & $FE). Same as Hawkeye's `noise_tick_style='hawkeye_constants'`. |
| `L_81B3` | `nextvoice` | Write `$D404` from `$7A66,X` (stod404), `$D400` from `$7A7E,X`, `$D401` from `$7A81,X`. DEX; loop or RTS. |

### `$7D73` SMC target — identified

`songinit` writes `$18A3,X / STA $7D73`. `$7D73` is the IMMEDIATE byte
of `CMP #$01` at the held-note `D406` SR-release trigger (line `$7D72`).
The SMC writes a PER-SUBTUNE threshold into that CMP. So `$18A3` is a
4-byte per-subtune table of SR-release thresholds (one byte per
subtune).

### All data table addresses for engine A — final

| Addr | Field | Size |
|---|---|---|
| `$17E3` | lonote (freq_lo) | 96 entries |
| `$1842` | hinote (freq_hi) | 96 entries |
| `$18A1` | per_subtune_speed | 4 bytes (4 subtunes) |
| `$18A3` | per_subtune_sr_threshold | 4 bytes (SMC into `$7D73` per subtune) |
| `$18A5` | seqtabel ptr lo (X-indexed) | 4 bytes |
| `$18A7` | seqtabel ptr hi (X-indexed) | 4 bytes |
| `$18B5` | runtime per-voice seq ptrs slot | 6 bytes |
| `$18DD` | drumtabel | 4 bytes/drum |
| `$190E` | drum 6 wave (SMC source) | (fixed reference) |
| `$191F` | drum 6 tone (SMC source) | (fixed reference) |
| `$1961` | arplo (arp ptr lo per inst) | 8 bytes (overlaps with arphi at last) |
| `$1968` | arphi (arp ptr hi per inst) | 8 bytes |
| `$1973` | arp offset table | constants used by `fx_tone_arp` |
| `$198B` | filterbytes (ptr lo+hi to 10-byte progs) | 4 progs × 2 bytes |
| `$199C` | pulsetabel | 4 progs × 8 bytes (per offset (n*8)-7) |
| `$19AC` | instr_records | 16 × 8 bytes |
| `$1A14` | vibtabwait | 8 bytes (per-inst vibrato delay) |
| `$1A20` | sequence stream base | variable (multiple voices share) |
| `$1BA0` | pattern_ptr_table | 2 bytes/entry (lo+hi interleaved) |

### Engine A — engine variant + knob mapping for FCConfig

Comparing to existing FCConfig knob choices:

| FCConfig field | Adrenalin engine A | Reasoning |
|---|---|---|
| `subtune_layout` | NEW VARIANT NEEDED — call it `'lo_hi_pair_with_smc_copy'` | `$18A5`/`$18A7` X-indexed lo+hi tables + 6-byte copy from `($18A5,X:$18A7,X)+0..5` to `$18B5`. Doesn't match Cyb II's `flat_seqtabel` (which is contiguous 6-byte blocks) or Hawkeye's `smc_template_with_sfx`. |
| `voice_loop_layout` | `tight_nextvoice` | nextvoice at `$81B3` writes all 5 voice regs together; no inline writes in effect chain. |
| `noise_tick_style` | `'hawkeye_constants'` | `$8175+` uses `LDA #$58 / LDA #$81` — same as Hawkeye. No startlen/starttabel. |
| `nextvoice_write_order` | `(4, 0, 1, 2, 3)` (ctrl, freq lo, freq hi, ...) | At `$81B3-$81C7`: D404 (`+4`) then D400 (`+0`) then D401 (`+1`) — Cyb II order. |
| `fx_drum_d401_offset` | `$0D` | At `$8167-$816A`: `LDA $7A55; CLC; ADC #$0D; STA $7A81,X` — same Hawkeye offset. |
| `held_note_clears_stod404_gate` | True (Hawkeye-style) | `$7D34-$7D60` directly clears gate via `AND #$FE / STA $7A66,X` — no byteand. |
| `filter_prog_mask` | `$03` (4 programs) | `$8079: AND #$03` at filter_prog entry. |
| `pulse_run_style` | `'disabled'` | No fx3 bit $02 handling visible; Adrenalin doesn't use pulse_run. |
| `pulserunspeed` | n/a | n/a |
| `fm2_cleanup_d416_value` | TBD via experimentation | Need to find fm2 branch. |
| `wavearpwait` / `pulsearpwait` | TBD | Need to find wave_arp / pulse_arp branches (might not exist for Adrenalin). |
| `instr_count` | 16 | inst_records = 8 bytes/inst at `$19AC`, max inst id is fx1/fx2/fx3 low nibble = 4 bits. |
| `max_patterns` | TBD | Limited by pattern_ptr_table size. Need to inspect `$1BA0..$1Bxx`. |

The `$18A3` SR-release threshold is per-subtune but doesn't currently
have a FCConfig field — would be a new field `per_subtune_sr_thresh_addr`
or handled by the new `lo_hi_pair_with_smc_copy` subtune_layout's
config. Defer until extract-path implementation reveals the cleanest
API.

### Subtune-to-engine mapping — VERIFIED

Tested directly via `_run_init_in_py65` + post-init memory inspection:

| Sub | PSID $50E3 play vec | Engine used | Data tables at |
|---|---|---|---|
|  0  | JMP `$7A06` | engine A at `$7A00` | `$17E3`/`$1842`/`$19AC`/`$1BA0` |
|  1  | JMP `$1021` | unknown (entry shim?) | unknown — TBD |
|  2  | JMP `$1006` | **engine A relocated at `$1000`** | `$17E3`/`$1842`/`$19AC`/`$1BA0` (SAME as sub 0) |
|  3  | JMP `$1006` | **engine A relocated at `$1000`** | `$17E3`/`$1842`/`$19AC`/`$1BA0` (SAME as sub 0) |

The `$1000` engine is engine A with PER-VOICE STATE addresses rebased
(`$7Axx → $10xx`) but **DATA TABLE references unchanged** (still
read from `$17E3`/`$1842`/etc.). Verified by disassembling the
relocated nolengset at `$128B`:

```
Engine A nolengset $7C8B+:              Relocated $128B+:
  LDA $7A16,X    STA $7A13,X              LDA $1016,X    STA $1013,X
  LDA $73        CLC  ADC $7A41,X         LDA $73        CLC  ADC $1041,X
  STA $7A1F,X    TAY                      STA $101F,X    TAY
  LDA $17E3,Y    STA $7A7E,X              LDA $17E3,Y    STA $107E,X   ← lonote ADDR UNCHANGED
  PHA  STA $7A2B,X                        PHA  STA $102B,X
  LDA $1842,Y                             LDA $1842,Y                  ← hinote ADDR UNCHANGED
```

So:

- **Both engines share the data table addresses at `$17E3`/`$1842`/
  `$19AC`/`$1BA0`/etc.** The PER-SUBTUNE state (`$7Axx` for sub 0's
  engine, `$10xx` for sub 2/3's engine) is separate.
- For subs 0, 2, 3: the DATA at the engine A addresses differs per
  subtune (each subtune's init copies its own patterns / per_subtune_speed
  / etc. into the shared addresses). E.g., sub 0's per_subtune_speed
  is `02 02 01 01`, sub 2's is `03 02 01 01`, sub 3's is `03 02 01 01`.
- The reason for the two engine copies: each engine instance has its
  own per-voice state (so subs 2/3 don't stomp on sub 0's state).
  That's irrelevant to our rebuild — we emit one engine.

### Empirical: subs 0/2/3 may share most data (TBD)

After running init per subtune and dumping the runtime state:

- Subs 0, 2, 3 ALL show identical:
  - per-subtune ptr lookup table at `$18A5..$18AB` (`A9 AF 18 18 20 A0 20`)
  - runtime slot at `$18B5..$18BA` (`20 A0 20 1A 1A 1B` → V0=`$1A20`,
    V1=`$1AA0`, V2=`$1B20`)
  - active speedbyte at `$7A09` (`$02`)
- Subs 2, 3 ALL show identical:
  - per_subtune_speed table at `$18A1` (`03 02 01 01`)

So the extracted USF for subs 0/2/3 has identical V0/V1/V2 sequence
pointers + identical speed. Yet HVSC's Songlengths reports 4 distinct
durations: `3:36 3:47 1:21 0:41`. So the actual music DIFFERS somehow.

Two possibilities:
1. **The sequence bytes at `$1A20`/`$1AA0`/`$1B20` differ between
   subs 0/2/3's post-init memory** — i.e., the per-subtune copy
   populates the same pointer addresses but with different data at
   the pointed-to locations. Likely.
2. **Subs 0/2/3 share the same music**, with the launcher exposing
   different STARTING POSITIONS or different SECTIONS via some
   non-FC mechanism. Less likely.

Need to verify by inspecting sequence/pattern bytes per subtune.

### Composer build is BLOCKED on the new `runtime_slot` variant

`compose_fc_asm_featuredriven` doesn't know `runtime_slot` — it
expects `flat_seqtabel` or `smc_template_with_sfx`. To get a rebuild
SID, one of two paths:

1. **Teach the composer about runtime_slot.** Emit a standard FC
   songinit that copies per-subtune data into the runtime slot from
   a synthesized flat seqtabel table. Per the CORE TENET the rebuilt
   SID doesn't have to mirror Adrenalin's binary layout — it just has
   to produce the same writelog.

2. **Change Adrenalin's subtune_layout to 'flat_seqtabel'**, and have
   the extract path synthesize a 4-subtune flat seqtabel by reading
   each subtune's runtime slot from its own post-init memory.

Option 2 is simpler. The extract code already runs init per subtune.
Just collect the runtime slot values + speedbyte values into a
synthetic 4-record table, expose as `cfg.seqtabel_addr` /
`cfg.per_subtune_speed_addr` for the composer.

But before either path: confirm whether subs 0/2/3 really differ at
the sequence/pattern byte level. If they share data, the single-
subtune Adrenalin canary (sub 0 only) is the realistic deliverable
and we should mark subs 1/2/3 as deferred.

### Sub 1 — TBD

PSID play vec for sub 1 is `$1021` — neither engine A (`$7A06`) nor
the relocated engine (`$1006`). Post-init data at engine A's addresses
(`$17E3` etc.) doesn't look like valid FC data for sub 1
(lonote[$48]=`$90` instead of `$0C`; pattern_ptr_table all zeros;
per_subtune_speed `$21 $02 $00 $21`).

Sub 1 likely uses a third engine variant at `$1021` (e.g., a
trampoline / shim) OR sub 1 is an SFX-style subtune that uses
different machinery. Needs disasm of `$1021+` post-init.

For now: sub 0, 2, 3 are the "music subtunes" with confirmed engine A
data layout. Sub 1 is the outlier. Can land subs 0/2/3 first
(3-subtune canary) then return for sub 1 separately.

### Implications for `EngineInstance` schema

The Phase 1 schema with per-EngineInstance address overrides was
designed assuming per-subtune address overrides for `freq_lo_addr`
etc. The actual situation: **for subs 0, 2, 3 the data addresses are
the same** — no per-EngineInstance overrides needed for them. Sub 1
likely DOES need overrides.

EngineInstance is still useful for tracking:
- Which subtunes go through which engine instance
- The init copy params (src/dst/size) per subtune
- The PSID play vector per subtune

But for data extraction across subs 0/2/3, the existing top-level
FCConfig address fields suffice. Sub 1 is the one case that needs
per-subtune address overrides.

## Required next session — full decompile (protocol Step 0)

Before any FCConfig / composer / USF schema work, do the following
in order:

1. **Read the family-wide docs** at `pipelines/future_composer/docs/`
   (FC v4.1 manual, `csdb_fc_v4_player_disasm.md`, lineage notes) —
   already exist; haven't been fully consulted yet for this RE.

2. **Hand-annotate engine A** at `$7A00..$81D0` from the existing
   seed `disassembly.s` (967 lines, auto-traced). Identify structural
   labels: playirq, songinit, nolengset, arpset, the per-frame voice
   loop, etc. Use Hawkeye's `disassembly.s` as a model for annotation
   style.

3. **Generate and hand-annotate engine B** at `$1000..$1FFF`
   post-init. Use `_run_init_in_py65(sub=2)` to capture the post-init
   memory, write it as a synthetic SID, seed-disassemble with
   `tools/seed_disassembly.py --entry 0x1003 --entry 0x1006`, then
   hand-annotate.

4. **Compare engine A vs engine B routine-by-routine.** Determine
   from evidence whether engine B is:
   - engine A relocated (multi-engine hypothesis), or
   - a small trampoline that JSRs into engine A (single-engine
     hypothesis with shim).

5. **Generate and hand-annotate the sub 1 source** at `$575D..$61CF`
   (copies to `$1021`). This one has no JMP prefix — its structural
   purpose is genuinely unknown from current evidence.

6. **Determine FC v4 / FC v4.1 player layout.** Some FC variants
   support per-subtune player code as an explicit feature. If
   Adrenalin uses that mechanism, the existing FC docs may describe
   it.

7. **Only THEN** decide multi-engine vs single-engine architecture
   and write the FCConfig.

## What's already in place for either outcome

Phase 1 schema + Phase 2 extract refactor commits (`55c1f98`,
`5c5a4c3`, `6b60f4c`) added general infrastructure:

- `EngineInstance` dataclass + `instance_for_subtune` /
  `resolve_address` helpers on `FCConfig`.
- `_run_init_in_py65` to capture post-init memory.
- `extract()` is multi-engine aware via `engine=None` fallback for
  single-engine SIDs — no behavior change for Hawkeye/Cyb II.

These are general-purpose. If Adrenalin turns out single-engine,
`FCConfig.engines = None` and the new infrastructure simply isn't
used for this canary; it remains available for genuinely multi-engine
SIDs if one is encountered later.

If Adrenalin IS multi-engine, the infrastructure is ready and the
FCConfig only needs the EngineInstance tuple filled in based on the
hand-annotated disasm.

## Decision NOT YET MADE — pending full decompile

Three options for what canary #3 actually covers (DO NOT pick one
before the hand-annotated disasm work above is complete):

1. **Adrenalin sub 0 only** as a single-subtune canary. The engine
   at `$7A00` matches Hawkeye/Cyb II's shape (we already found the
   addresses). Works under the existing FCConfig if we treat the
   "songs" field as 1 instead of 4. Loses 3 of the 4 subtunes from
   coverage but DOES land a non-Tel FC canary cleanly.

2. **Full Adrenalin (all 4 subs)** — requires multi-engine-instance
   support in FCConfig + the composer. Significantly larger scope:
   the per-subtune copy table becomes a new schema element, and the
   composer needs to emit two engine instances. Realistically a
   multi-session refactor.

3. **Switch to a different non-Tel FC canary.** Eliminator (row 2,
   Tel) and Tomcat (row 4, Tel) don't help diversify. Adrenalin is
   the only non-Tel row. Without Adrenalin (in some form), the FC
   canary set stays Tel-only.

Recommendation: option (1) — extract sub 0 only, mark Adrenalin as
"partial canary" in `canary_picker.md`, and revisit multi-instance
support once it's the bottleneck. This gets us a non-Tel canary into
the regression in one more focused session without committing to a
schema-level refactor.

## Unknown — TODO next session

- `subtune_layout`: new shape (X-indexed lo+hi pointer table + 6-byte
  runtime slot at `$18B5`). Provisional `'flat_seqtabel'` in config;
  may need a new SubtuneLayout variant if extractor fails.
- `instr_count`: count from `$19AC` records area.
- `max_patterns`: count from `$1BA0..` table extent.
- Aux tables (`drumtabel`, `filterbytes`, `arplo`, `arphi`, `pulsetabel`,
  `vibtabwait`, `startlen`, `starttabel`, `wavearp`, `pulsearp`):
  not yet located.
- `voice_loop_layout`, `noise_tick_style`, `nextvoice_write_order`, all
  other Cyb II/Hawkeye discriminator knobs: provisionally Cyb II
  defaults; verify by examining the per-voice loop tail + drum effect
  in the disasm.

## Status (2026-06-06)

**Stalled at structural discovery.** The runtime layout differs
fundamentally from Hawkeye/Cyb II:

1. **Inline-load PSID.** Header load=$0000 means the first 2 bytes of
   code body hold the actual load address (=$50E0). Hawkeye/Cyb II
   are non-inline (header load=actual load).

2. **Self-decompressing engine.** PC trace at subtune 1, 0.5s shows
   execution flows from $50E0..$5100 area → $7A00-$8100 area. The
   binary occupies $50E0..$81D0 (~12.5kB), but the engine itself isn't
   visible at the load address — it gets *unpacked* into the
   $7Axx-$81xx range at init. Adrenalin's $50xx region is a
   decompressor + packed engine data.

3. **`tools/seed_disassembly.py` only traced 76 lines** because it
   follows reachable code from init+play+subtune-entries and the
   unpack stage SMC-installs further entry points it can't see ahead
   of time.

## To continue

The pre-decompression binary is opaque. To get a useful disassembly:

1. **Run init in py65 to completion** (the decompressor exits to RTS
   or the IRQ handler).
2. **Snapshot RAM after init**: `mem_post_init = py65.memory[$7A00:$8200]`
   (or wider — the actual range needs discovery).
3. **Write the snapshot as a synthetic PSID** with load=$7A00 and the
   actual play address from the IRQ vector.
4. **Re-run `tools/seed_disassembly.py`** on the synthetic PSID. Now
   the disasm sees the real engine code with proper entry points.
5. **Cross-reference with `pipelines/future_composer/docs/wiki_fc_v41_manual.md`**
   and `csdb_fc_v4_player_disasm.md` for FC instruction semantics.
6. **Hand-annotate** structural labels (per-frame routine, nolengset,
   tone_arp, vibrato, drum, etc.) following Hawkeye's
   `disassembly.s` as a model.

## Then the standard canary-extract path

Once a clean disassembly exists:

1. Find the ~12 address knobs (freq_lo/hi, pattern_ptr, instr_records,
   per_subtune_speed, drumtabel, filterbytes, arplo/hi, pulsetabel,
   vibtabwait, startlen, starttabel) via `lda <addr>,X` greps.
2. Choose FCConfig knobs (subtune_layout, pulse_run_style,
   noise_tick_style, voice_loop_layout, ...).
3. Address the inline-load PSID shape — may require a new FCConfig
   field or a small extension to `composer.py::_load_sid_psid` to
   handle inline at SID-write time.
4. Build canary: `pipelines/future_composer/adrenalin/config.py` →
   `ADRENALIN = FCConfig(...)`.
5. Extract: `from pipelines.future_composer.engine_model import
   extract; extract(ADRENALIN)`.
6. Verify byte-exact: `verify_featuredriven(ADRENALIN)`.
7. Add to `tools/regression.py::regress_future_composer` canaries
   list once 4/4 subtunes go FULL.

## Why we're adding Adrenalin

Hawkeye + Cybernoid_II are both Jeroen Tel tunes; their feature mix
overlaps heavily and doesn't exercise everything the FC engine can do.
HeatWave's Adrenalin is the only non-Tel candidate in `canary_picker`
row 3 of engine #4, and adds (at minimum):

- Different composer style → different per-instrument fx_bytes patterns
- Self-decompressing engine load shape
- Inline-encoded PSID header
- 4 subtunes (multi-sub regression coverage)
- Potentially: feature combinations no Tel tune uses (subtune SFX
  handling, different fil_count bits, different drum tables, etc.)

The composer's current feature coverage is honest only when at least
one canary structurally distinct from the existing two demonstrates
that the feature-driven composition path generalises beyond Tel's
subset.

## Tools to use (per [[feedback_writelog_divergence_recipe]])

- `tools/seed_disassembly.py` — generate skeleton (already done at
  76 lines; redo against post-init snapshot)
- `tools/find_first_divergence.py` — once a rebuild exists
- `siddump --memwatch-on-write` + `--memwatch` — state inspection
- The hand-annotated disassembly is the input to everything else.

## Related

- [[project_hawkeye]] — worked example of FC canary migration end-to-end
- [[feedback_check_existing_engine_docs]] — Step 0 protocol
- `pipelines/future_composer/docs/wiki_fc_v41_manual.md` — FC v4.1
  instruction format
- `pipelines/future_composer/docs/csdb_fc_v4_player_disasm.md` —
  player disasm reference
