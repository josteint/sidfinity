# Session Status — 2026-04-25 (updated)

## Das Model

Spec at `docs/das_model.md`. SID = (T, I, S).

## Current Codegen: `src/das_model_gen.py`

**Output:** `demo/hubbard/Commando_das_model.sid` — 3,806 bytes (original 4,165)

**Register Match (30-second siddump comparison):**
```
Overall: 89.9% (28,330 / 31,500 register-frames)
  Freq:  90.3%  (V1: 82.5%, V2: 93.3%, V3: 99.9%)
  PW:    77.5%  (V1: 68%, V2: 100%, V3: 27.6% lo/100% hi)
  Ctrl:  96.2%
  ADSR:  98.8%

sid_compare: Grade A, 97.7%
  Zero note_wrong, zero wave_wrong across all voices
Audio PCM correlation: 0.29
```

## Key Findings This Session

### 1. Arp Phase = Global Frame Counter (FIXED)
The Hubbard arp uses `$5525 AND #$01` — the global frame counter's LSB. NOT a per-voice step counter. All voices share the same phase.

Code at $5365:
```
LDA $5525      ; global frame counter
AND #$01       ; bit 0
BEQ base_pitch ; even → base note
; odd → base_note + 12
```

$5525 increments every play() call ($5012). After init, it's reset to 0 via $5519 bit6 check.

Fix: separated W and F programs. W = 1 byte/step wave-only. F replaced by per-instrument `arp_offset` (0 or 12) evaluated via global `frame_ctr`.

### 2. Tie Notes (FIXED)
rh_decompile reports `pitch=None` for TIE notes. These extend the previous note's duration without retriggering. Our extract() was creating new notes with pitch=0.

Fix: merge ties into previous note's duration: `notes[-1]['duration'] += dur + 1`.

Trade-off: merged notes have a single hard restart at the combined end, while the original fires hard restart at each segment boundary (note/tie). This drops ADSR from 99.6% to 98.8%.

### 3. PW Note-Start Skip (INVESTIGATED, NOT APPLIED)
The original Hubbard player skips PW accumulation on the frame when a new note loads. Confirmed via py65 trace: delta=0 on note-start frames.

However, applying this fix in our engine makes siddump comparison worse (76.2% vs 77.5%) because the additional code bytes shift siddump frame boundaries. Audio correlation unchanged (0.29). Reverted.

The correct implementation would be:
- Skip PW write AND accumulate on note-start frames
- EXCEPT for the very first note (detected by frame_ctr==0)

### 4. Instrument Table Layout (confirmed)
$5591 base, 8 bytes per instrument:
- +0: pw_lo, +1: pw_hi, +2: ctrl, +3: AD, +4: SR
- +5: pw_sweep_lo, +6: pw_sweep_hi, +7: fx_flags

fx_flags bits: 0=drum, 1=skydive, 2=arpeggio, 3=table_arp

$5523 holds fx_flags for the currently processing voice (shared location).

## Remaining Issues

### Extended Table (V1 freq gap, unfixable)
T[96+] overlaps Hubbard player runtime state. T[100] at $54F8 changes every frame. Our static capture produces slightly wrong values for drum pitches (pitch=104) and arp notes using T[100].

### PW Accumulation (V3 27.6% pw_lo)
Linear PW for V3 diverges by exactly 1 PW step at note boundaries. The original skips PW on note-start frames. Our engine accumulates on every frame. Each melody section accumulates 1 extra step, then resyncs when a drum note resets PW.

### Audio Correlation Ceiling
0.29 PCM correlation dominated by V1 arp phase from extended table values. Each wrong arp phase frame has a 58:1 frequency ratio difference, which strongly anti-correlates the PCM.

## ZP Layout (per voice, 15 bytes)
```
+0:  tick_ctr
+1/2: ol_ptr (orderlist pointer)
+3/4: pat_ptr (pattern note pointer)
+5/6: w_ptr (wave program pointer, 1 byte/step)
+7:  pw_lo
+8:  base_note
+9:  note_len
+10: pw_speed
+11: pw_hi
+12: pw_max ($00=none, $FF=linear, else=bidir max)
+13: pw_dir (0=up, 1=down)
+14: prev_inst ($FF=first note)
$AD: global frame_ctr (shared)
```
V1: $80-$8E, V2: $8F-$9D, V3: $9E-$AC
