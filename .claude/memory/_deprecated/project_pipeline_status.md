---
name: Pipeline status
description: Lean V3 codegen on Commando subtune 1 round-trips audibly identical to original (user-confirmed). Engine quirks live in USF as data. Subtune 2 still Grade F (env-timing). Roadmap: docs/PLAN_dasmodel_v2.md.
type: project
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
**GT2 pipeline:** 4,968 Grade A songs (separate older path).

**Lean V3 / USF v3.x — Commando milestone (May 2026):**

Subtune 1 (game music) — **user-confirmed audibly indistinguishable from original**. First Hubbard subtune to round-trip cleanly through the Lean pipeline. sid_compare jitter-tolerant: Grade A, score 99.9, V1 ok=2965/3000.

Subtune 2 (title music): Grade F, score 80.5. 0 strong audible diffs (note_wrong=0, wave_wrong=0). env_wrong=1614 (17.93%) — gate-off ADSR-zero timing offset by ~1 frame on V1, weakly audible. Separate fix.

**Bugs fixed to reach subtune 1 round-trip (commit order):**
- `4d52d64` Vibrato → PWM carry leak. Hubbard's linear PWM at $5237 has no CLC before its ADC; the vibrato target_hi-overflow carry deliberately leaks into pwlo += pwm_speed, giving an occasional +1. Reproduced by removing CLC from our codegen + using BMI on a re-encoded pwmode (bit 7 = linear) that doesn't disturb C.
- `33fed80` Per-subtune speed table + correct FF orderlist semantics. Speed table at $5514 indexed by subtune (LDA $5514,X / STA $5517). find_speed previously rejected the table because byte 5 ($C0) > 15; relaxed to accept whatever valid prefix and pad. FF in orderlist: Hubbard driver at $5099 resets position to 0 (loop to start), the byte after FF is dead data — old code was treating it as a loop value.
- `3f5f77a` Drum waveform: 3 frames of $80 (not 2). das_model_gen `w_steps = [ctrl|0x01, 0x80, 0x80, 0x80, ctrl&0xFE]`, w_loop=4.
- `f8e39b3` Bidirectional PW direction is per-VOICE not per-instrument. Hubbard's $5510,X is voice-indexed; direction persists across instrument changes on the same voice. Renamed `i_pwdir` → `v_pwdir`, indexed by X (voice), 3 entries. Without this, a voice picking up a new bidirectional instrument starts with the wrong direction and PW lands in the audible middle range when orig was sweeping through the inaudible $00xx/$0Fxx extremes — heard as "extra notes".
- `bdbaba9` no_release skips HR. Hubbard's no_release flag (bit 5 of pattern dur byte; surfaces in das_model_gen via drum_trig bit 7) suppresses the HR (gate-off + ADSR-zero) at the END of the marked note; the next note inherits the still-on gate so the SID envelope doesn't retrigger. Encoded in bit 5 of the raw inst byte; codegen extracts it into a per-voice v_no_release[X], masks $FB to bits 0-4 for table lookup, checks v_no_release in the HR fire branch. (Don't confuse this with `.tie` — orig DOES fire gate-on at no_release notes, the flag only suppresses HR at their end.)
- `9ca8f2f` Portamento. Per-frame freq slide for porta-active notes. Hubbard porta byte: bits 1-6 = step size, bit 0 = direction. Threading: rh_decompile.note.portamento → das_model_gen drum_trig → gen_commando_v3 strips bit 7 (no_release), emits remainder as `porta` field on USFNoteEvent → CodegenV3 emits 4 bytes per note (pitch, dur, inst, porta), advance += 4. Note-load reads byte 4 into v_porta[X] and inits a 16-bit v_porta_lo/hi[X] accumulator from base freq. New "2a. PORTAMENTO" sustain stage runs BEFORE vibrato; when v_porta != 0 it slides the accumulator and writes straight to SID freq, JMPing past vibrato (orig disables vibrato modulation during a slide). Watch out: TAY in note-load porta-init clobbers Y (= sidoff for downstream STA absY); use scratch zp + restore Y from v_sidoff[X] at the end.

**Architecture (the important thing):**

Engine quirks live in `USFSong.engineQuirks` as DATA, not codegen branches. CodegenV3.lean is universal — it iterates the data and emits 6502 mechanically. Same codegen will work for any engine; only the decompiler-emitted quirks change.

`USFEngineQuirks` schema (USFv3.lean):
- `voiceScratch` — extra per-voice state bytes
- `noteLoadOps` — addConst/addByFlag/setConst/resetIfNextEnds/incIfNextEnds
- `patternEndOps` — reset/increment
- `dynamicFreqEntries` — slot fed from USFDynRef at USFUpdatePhase
- `preserveNoteFlags` — keep bits 6/7 in pattern data

For Commando, this encodes: hub_off + seq_idx counters, T[98], T[99], T[100], T[104], T[105], T[106], T[107] dynamic freq aliasing, +1/+2/+3 hub_off increment by inst-byte flag bits, eager pattern-end resets. ~80 lines of declarative data in `gen_commando_v3.py`.

Also fixed in CodegenV3 itself (universal player behaviors, not Hubbard quirks):
- Vibrato 16-bit subtraction order (lo first, then hi)
- Vibrato lo/hi swap in multiply loop
- Vibrato multiply step count off-by-one
- Tie notes (pitch=$FD) preserve v_inst, skip Fhi/Flo, write Ctrl/PW/ADSR with previous instrument's tables
- Per-voice (not per-instrument) PW direction
- Per-note no_release flag suppresses HR
- Per-note portamento: 4-byte note encoding, 16-bit per-voice freq accumulator

**Note encoding (current):**
4 bytes per note in pattern data: pitch, durationFrames, instrument, porta. Pattern terminator = pitch byte $00. Pattern advance += 4. Instrument byte: bits 0-4 = index, bit 5 = no_release, bits 6/7 = legato/no-inst-byte (hub_off advance flags).

**Ground truth (CRITICAL):**
- siddump --writelog = definitive instruction stream
- siddump --raw = per-frame register state (most useful for matching audio)
- py65 = proxy (may differ in cycle counting); never use as sole truth
- The user's ear is the final judge.

**Roadmap next:**
- Validate on Monty on the Run (same Hubbard engine, should "just work" via decompiler)
- JSON serialization of USFSong (task #30)
- Subtune 2 env_wrong fix (gate-off timing — likely tempo-related threshold)
- ML training on USF JSON

**Files of note:**
- src/formal/USFv3.lean — schema (incl. engineQuirks, USFNoteEvent.porta)
- src/formal/CodegenV3.lean — universal player codegen
- src/formal/CommandoV3.lean — generated from gen_commando_v3.py
- src/gen_commando_v3.py — Commando decompiler that populates engineQuirks
- src/das_model_gen.py — Hubbard-specific extract() that produces (T, instruments, score)
- src/rh_decompile.py — raw Hubbard SID parser; find_speed accepts partial valid speed tables
- demo/hubbard/Commando_v3pipe.sid — round-trip subtune 1 (game), Grade A audibly clean
- demo/hubbard/Commando_v3pipe_st2.sid — round-trip subtune 2 (title), Grade F (env timing)
- demo/hubbard/Commando_das_model.s — Hubbard reference asm (94.77% match)
- docs/usf_v3_engine_quirks.md — engineQuirks DSL design
