# EMS/Odie — Per-Frame Write Model & Version Binary Differences

## Provenance

```
provenance:
  sources:
    - url: "file:hvsc85/MUSICIANS/C/Connolly_Sean/Coup_De_Grace.sid"
      fetched_via: "Python read-only byte inspection"
      fetch_date: 2026-06-14
      content_date: "1996 Cosine Systems"
      reliability: authoritative (HVSC binary, canonical $1000 V7.03 player)
    - url: "file:hvsc85/MUSICIANS/C/Connolly_Sean/Cosine_Intro.sid"
      fetched_via: "Python read-only byte inspection"
      fetch_date: 2026-06-14
      content_date: "1996 Cosine Systems"
      reliability: authoritative (HVSC binary, earlier variant)
    - url: "file:hvsc85/MUSICIANS/C/Connolly_Sean/Rescued_Pixels_3.sid"
      fetched_via: "Python read-only byte inspection"
      fetch_date: 2026-06-14
      content_date: "2025 Arkanix Labs"
      reliability: authoritative (HVSC binary, only V10.x representative)
    - url: "file:hvsc85/MUSICIANS/T/TMR/Big_Bus.sid"
      fetched_via: "Python read-only byte inspection"
      fetch_date: 2026-06-14
      content_date: "~2000 Cosine"
      reliability: authoritative (HVSC binary, V9.x-like dispatch structure)
    - url: "file:hvsc85/MUSICIANS/C/Connolly_Sean/Wild_One.sid"
      fetched_via: "Python read-only byte inspection"
      fetch_date: 2026-06-14
      reliability: authoritative (HVSC binary, Odie_tiny variant)
    - url: "file:hvsc85/MUSICIANS/C/Connolly_Sean/CDU_Magazine_loadertune.sid"
      fetched_via: "Python read-only byte inspection"
      fetch_date: 2026-06-14
      reliability: authoritative (HVSC binary, Odie/Cosine variant)
    - url: "https://github.com/cadaver/sidid/blob/master/sidid.cfg"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: high (authoritative sidid fingerprint DB)
    - url: "https://www.lemon64.com/forum/viewtopic.php?t=10753"
      fetched_via: WebFetch
      fetch_date: 2026-06-14
      reliability: medium (scene forum; direct quote from TMR/Cosine)
    - url: "file:hvsc84.db"
      fetched_via: "sqlite3 read-only Python query"
      fetch_date: 2026-06-14
      reliability: authoritative (local HVSC #84 mirror)
  author: write-model-agent
  content_date: 2026-06-14
```

Cross-reference: `cluster_editor_and_cosine.md` (editor feature model from V7.03 help files)
and `cluster_corpus_and_scene.md` (corpus statistics, sidid signatures).

---

## 1. Binary Layout Overview

The compiled EMS player is a relocatable binary. Its load address varies (see
corpus stats in `cluster_corpus_and_scene.md`), but the structure at the load
base is always the same five-entry JMP table:

```
load+$0000: JMP init_routine        ; tune init (A = subtune, 0-based)
load+$0003: JMP play_routine        ; one frame of music
load+$0006: JMP sound_engine        ; multispeed call (filter NOT updated here)
load+$0009: JMP clear_routine       ; silence SID, clear state
load+$000C: JMP fade_routine        ; fade out (A = fade speed, duration = A×16 frames)
load+$000F: [per-tune data / engine state block]
```

PSID init() = JMP[0]; PSID play() = JMP[1] (i.e. init addr = load, play addr = load+3).

This is confirmed across all 196 EMS/Odie SIDs: `play_addr = init_addr + 3` holds
in 186/196 cases. The 10 exceptions use non-standard game-integration layouts.

**State block at load+$000F onwards**: 5-byte interleaved voice state (3 voices,
stride varies by version — see §3). After zeroing by init, this is populated during
the first several frames as the sequence decoder advances.

---

## 2. Dominant (V7.03) Play-Frame Write Sequence

Based on read-only disassembly of Coup_De_Grace.sid (canonical $1000-base V7.03
player, representative of 118/196 EMS/Odie SIDs sharing the exact same 5-JMP
preamble `4C B9 10 4C 2F 11 4C 21 11 4C F5 10 4C 0B 11`).

The play() entry at load+$0003 JMPs to the main play dispatcher. Disassembly
at `$112F` (Coup_De_Grace; address adjusts proportionally for other load addresses):

### 2.1 Per-Frame Dispatch Order

```
$112F  LDX #$02              ; X = voice index, counts 2→1→0
       JSR voice_update      ; process voice X=2
       DEX
       JSR voice_update      ; process voice X=1
       DEX
       JSR $18BD             ; filter/freq sweep update (global)
       JSR $188F             ; fade counter (if fade active)
       LDA $10AC             ; master_vol / filter state byte
       STA $D418             ; write master vol + filter routing
       LDA $109D             ; filter frequency lo
       STA $D415
       LDA $109E             ; filter frequency hi
       STA $D416
       LDA $10A3
       [ORA/AND into filter mode]
       STA $D417             ; filter routing / resonance
       ; (DEX already = 0, so last voice_update X=0 is at $1139)
```

**Actual call order inside the play dispatcher:**
```
voice X=2 → voice X=1 → [separate $18BD call] → [X=0 merged into $18BD path]
→ then voice X=0 inside $18BD/JSR path
→ then global: $D418, $D415, $D416, $D417
```

Wait — the actual structure (from the disassembly) is:

```
JMP $112F (play):
  LDX #$02
  JSR $115A     ; voice_update(X=2)
  DEX
  JSR $115A     ; voice_update(X=1)
  DEX
  JSR $18BD     ; voice X=0 + filter update (combined)
  JSR $188F     ; fade step
  STA $D418     ; master volume + filter routing
  LDA $109D; STA $D415
  LDA $109E; STA $D416
  [filter mode]; STA $D417
  RTS
```

The filter/envelope global block at $18BD handles voice X=0 inline (not through
$115A). The two main subroutine passes (X=2, X=1) write via $1816 (the SID
write stub); voice X=0 writes happen inside $18BD.

### 2.2 SID Write Order Per Voice (Inside voice_update → $1816)

The SID write stub at $1816 (using Y = voice base register offset):

```
STA $D400,Y    ; frequency lo  (Y = voice base: $00/$07/$0E for V1/V2/V3)
STA $D401,Y    ; frequency hi
STA $D402,Y    ; pulse width lo
STA $D403,Y    ; pulse width hi
; (if hard-restart enabled via state flag AND $10)
  STA $D404,Y  ; gate-off (test-bit or waveform write for hard restart)
  STA $D405,Y  ; AD register (from instrument table)
  STA $D406,Y  ; SR register (from instrument table)
; else
  STA $D404,Y  ; control register (gate-on, waveform, test)
```

**Gate sequencing per voice**: on note trigger, a gate-off frame is inserted
(bit 0 cleared in $D404,Y), then on subsequent frame gate-on fires. The player
tracks a "hard restart" flag per voice (state byte $109A,X bit 4). When set:
writes gate-off + primes ADSR before firing gate-on.

**Filter (global, written once per frame, after all voices):**
```
$D418  — master volume (lo nibble) + filter routing (hi nibble)
$D415  — filter frequency lo
$D416  — filter frequency hi  
$D417  — resonance (hi nibble) + voice filter routing (lo nibble)
```

### 2.3 Voice Addressing

Each voice N (N=0,1,2) maps to SID register block starting at:
- Voice 0: $D400 (Y=$00)
- Voice 1: $D407 (Y=$07)
- Voice 2: $D40E (Y=$0E)

The Y offset is loaded from a per-voice base table at `load+$1015,X`
(at $1000 base: $D415[0]=$00, $D415[1]=$07, $D415[2]=$0E). These values
are fixed constants — not song data.

### 2.4 Sequence Decoder — Indirect ZP Walk

The core of the per-voice update is a byte-stream decoder using ZP indirect:

```
LDA load+$100F,X   ; lo-byte of sequence pointer → ZP $F8
STA $F8
LDA load+$1012,X   ; hi-byte → ZP $F9
STA $F9
LDY load+$102B,X   ; current offset within sequence → Y
LDA ($F8),Y        ; load next byte from sequence stream
```

Confirmed by disassembly: B9/$B1 pairs referencing $F8/$F9 appear at $11B4,
$11BB, $11D3, $11F1, $11FA, $1239, etc. in Coup_De_Grace.

**Command byte dispatch** (from sequence stream byte in A):

| Range      | Meaning |
|------------|---------|
| `$FF`      | Song loop / subtune boundary: read next byte as new Y → re-fetch |
| `$FE`      | Voice silence: clear active flag, zero gate |
| `$FD`      | Fade trigger: set fade flag + read 2 more bytes (speed, count) |
| `$F0–$FF`  | Speed / duration override: low nibble → per-voice tempo counter |
| `$E0–$EF`  | Transpose set: low 5 bits → transpose (EOR $FF = store inverted) |
| `$C0–$DF`  | Transpose set (alt encoding): low 5 bits → transpose |
| `$A0–$BF`  | Arpeggio type select: low 5 bits → arp index |
| `$60–$9F`  | Glide: SBC #$5E → per-voice glide increment, then load next byte |
| `$00–$5F`  | Note: raw note number; triggers freq lookup, instrument apply, gate |

When a note byte is decoded:
1. Note index → frequency lookup (freq table at `$1A12` offset in Coup_De_Grace = `load+$0A12`)
2. Store freq hi/lo in per-voice state ($10B3,X / $10B6,X)
3. Run instrument apply: set waveform (via instrument soundtype), pulse width, vibrato
4. Trigger gate: write $D404 (control) sequence = gate-off → gate-on on next frame

### 2.5 Instrument Apply on Note Trigger

At note-on ($124F in Coup_De_Grace), the instrument record is indexed by
voice's current instrument index. Fields read (in order):

```
vibrato_delay       → $1070,X  (vibrato start delay counter)
soundtype (bits 0-2)→ $104C,X  (effect mode: 0=vib, 1=arp, 2=osc_dn, 3=osc_up, 5=hf_arp)
pulse_rate nibble   → $1091,X  (pulse cycle speed)
pulse_lo            → $107C,X  (PW lo, from freq_lo table at $1952)
pulse_hi            → $107F,X  (PW hi, from freq_hi table at $19B2)
```

After instrument load, per-voice active flag bit 5 ($109A,X bit 5) is cleared
("note trigger done"), and bit 7 is checked for gate-restart mode.

### 2.6 Vibrato

Vibrato is applied every frame when the per-voice vibrato counter $1049,X > 0:
```
LDY $1049,X               ; vibrato position
LDA $1B26,Y               ; vibrato table read
LSR x5 → check            ; extract vibrato amount
if non-zero:
  ADC/SBC to freq state    ; modulate current freq
STA $D400/01,Y            ; update freq via SID write
```

The "constant amplitude regardless of frequency" property (mentioned in
HELP.GENERAL) is achieved by the table lookup rather than a fixed add —
the table is pre-scaled. Vibrato is controlled by:
- `vibdelay` (instrument field $109): N frames before start
- `vibspeed` (instrument field $11): cycles every 3× value frames
- `oscdelay_vibdepth` (field $10): right nibble = depth (0=heavy, 7=light)

### 2.7 Pulse Width Cycling

PW cycling per voice: if `pwrate` (instrument $06) != 0, each frame:
```
LDA $1058,X               ; PW accumulator lo
CLC; ADC rate             ; add pwrate
STA $1058,X
if overflow carry:
  INC $105B,X             ; PW hi
  check hi-byte bounds ($1BAA table):
    if above max: reverse direction (EOR #$80 on direction flag $109A bit 7)
    if below min: reverse direction
```

Direction-flip comparison is against per-instrument bounds from `$1BAA,Y`.

### 2.8 Filter Sweep

The global filter sweep (called from $18BD every frame) uses a second indirect
ZP walk through a filter table. The filter table pointer pair lives at
`$10A6`/$10A7 (table index) → indexed into a filter-ptr table at `$1AA2`.
The filter walk produces `$D415` (lo) and `$D416` (hi) per-frame values,
with a sweep rate and a loop-or-terminate sentinel (`$FFFE`/`$FFFF`).

---

## 3. Version Binary Differences

### 3.1 Corpus Classification by Pattern

Full-corpus search over all 211 EMS-family SIDs (196 EMS/Odie + 9 Odie/Cosine
+ 3 Odie_tiny + 2 Odie/Pulse + 1 EMS_V10.x):

| Pattern | Count | Significance |
|---------|------:|--------------|
| V7.03 init (LDY #$16 D400-clear + gate-off) | 137 | Canonical V7.03 init |
| V9.x-like dispatch (A2 02 A0 0E 20 ...) | 28 | Restructured play dispatcher |
| V10.x expand loop (A0 00 B9 … 0A … 2A … C0 53) | 11 | New data preprocess step |
| Neither (older/non-standard) | 35 | Pre-V7, Odie/Cosine, Odie/Pulse, Odie_tiny |

Note: V7.03 and V9.x patterns are mutually exclusive in the corpus (0 overlap),
confirming they identify distinct codebase lineages, not overlapping features.
V10.x overlap with V7.03 is 0 at the init level, but 11 SIDs have the V10.x
data-expansion loop — these include Rescued_Pixels_3 plus 10 EMS/Odie SIDs that
sidid still classifies generically (the V10.x sidid sub-signature fires on Rescued
Pixels_3 only because sidid sub-sigs are independent of the main family match).

### 3.2 Variant A: EMS_V7.03 (Dominant Form, n≈137 at $1000 base)

**Representative SID**: Coup_De_Grace.sid (1996, Cosine), Fluff.sid,
Target_X.sid (1999, Mirage), Bayliss Richard corpus, Merman corpus.

**5-JMP table targets** (at $1000 base):
```
$1000: JMP $10B9    ; init_full (clear state + load subtune params)
$1003: JMP $112F    ; play_main
$1006: JMP $1121    ; sound_engine
$1009: JMP $10F5    ; clear_SID (the V7.03 sidid-matched routine)
$100C: JMP $110B    ; fade
```

**Init structure** (`$10B9`):
1. `AND #$07` → mask subtune number
2. Clear state block $1018–$10B8 to $00 (`LDX #$00; STA $100F,X; INX; CPX #$A1; BNE`)
3. Set per-voice defaults: tempo counter at $101C,X=5, duration at $1019,X=2,
   instrument at $109A,X=$11 (voice active + default flags)
4. Multiply subtune index × 3 + 2 → Y index into subtune pointer table
5. Load 3 subtune sequence pointers (pairs at $1C5A): write to $102B,X for X=2,1,0
6. Set master vol: STA $10AC
7. `JMP $10F5` → the D400-clear routine

**The V7.03 D400-clear** (sidid signature) at `$10F5`:
```
$10F5: A0 16         LDY #$22 (decimal 22 = $16 + 0)
$10F7: A9 00         LDA #$00
$10F9: 99 00 D4      STA $D400,Y    ; clear $D416 first, count down
$10FC: 88            DEY
$10FD: 10 FA         BPL $10F9      ; loop until Y underflows ($FF < 0 in BPL)
$10FF: A9 08         LDA #$08       ; waveform=noise, gate=0 (hard-restart prime)
$1101: 8D 04 D4      STA $D404      ; V1 ctrl = $08 (test bit set)
$1104: 8D 0B D4      STA $D40B      ; V2 ctrl = $08
$1107: 8D 12 D4      STA $D412      ; V3 ctrl = $08
$110A: 60            RTS
```

This clears all 23 SID registers ($D400–$D416, LDY counts $16=$22 down to 0 = 23
writes) then primes all three voice control registers to $08 (noise waveform +
test bit = hard restart state). Master volume ($D418) is written during play() in
the first frame, not during init.

**Play dispatcher** (`$112F`):
```
JSR voice_update(X=2)
DEX
JSR voice_update(X=1)
DEX
JSR filter_and_v0()   ; handles X=0 + global filter
JSR fade_step()
STA $D418             ; master vol
STA $D415/$D416/$D417 ; filter
```

Voice processing order: **V3 → V2 → V1** (X=2 first). Voice X=0 is handled
inside the combined filter routine rather than through the main JSR.

### 3.3 Variant B: Earlier form (n=2 at $1000 base)

**Representative SID**: Cosine_Intro.sid (1996, Cosine) — only 2 SIDs confirmed.

**5-JMP table** (at $1000 base):
```
$1000: JMP $10BA    ; init
$1003: JMP $1138    ; play
$1006: JMP $112A    ; sound_engine
$1009: JMP $1109    ; clear
$100C: JMP $1114    ; fade
```

**Init** (`$10BA`): clears state block $100F–$10B6 to $00 (CPX #$A8 → 168 bytes
vs. V7.03's #$A1 = 161 bytes). The subtune multiplier is **7× + 2** (not 3× + 2)
→ subtune ptr table stride differs. D400 clear uses
`LDY #$19; STA $D418,Y` (counts down from $D418, clearing $D400–$D418 = 25 registers
including $D418 itself).

**Key difference from V7.03**:
- State block zero-fill size: 168 bytes (B) vs. 161 bytes (A)
- Subtune-pointer table stride: 7 (B) vs. 3 (A)
- Init clears $D418 as well (B) vs. leaving it to play() (A)
- `$D404` prime value: `A9 08` same in both (noise+test)
- No `STA $D404` during init in B (D400-clear loop includes it already)
- Voice active flag byte is at $108E,X (B) vs. $109A,X (A)

**State offsets differ**: in Variant B the active/voice-flag byte is $108E (vs.
$109A in V7.03), tempo at $1013 (vs. $101C), current-note at $1016 (vs. $101F),
etc. — the state block is a different layout.

These two SIDs (Cosine_Intro and Cyberwing, both 1996) predate the V7.03
public release (Jan 1997) and represent an intermediate engine version. The
V7.03 tool release reorganised the state block.

### 3.4 EMS_V9.x (n=28 EMS/Odie SIDs with this dispatch pattern)

**sidid signature**:
```
A2 02 A0 0E 20 && A0 07 20 && A0 ?? 86 ?? 84 ?? BD
```

`&&` = address matching (self-referential, i.e. the two JSR targets are the
same subroutine). Decoded: `LDX #$02; LDY #$0E; JSR sub; DEX; LDY #$07; JSR sub;
DEX; LDY #$00; STX zp; STY zp; LDA abs,X …`

**Confirmed in corpus** (28 SIDs, all classified generic EMS/Odie by sidid):
- Bellringer_III.sid (Connolly, 2022), Cyberwing.sid, Futureshock_Remix.sid,
  Get_em_DX.sid, Guy_Spy.sid, Mollusk.sid, Noisy_Pillars.sid, Outer_Space.sid,
  Tropical_Islands.sid, Turbocharge.sid, Vallation.sid, Wonderland.sid,
  TMR/Big_Bus.sid, Dozey.sid, Echoing.sid, Flower_Power_loader.sid,
  Goldrunner.sid, Hymn_to_Yezz.sid, Last_Ninja_3.sid, Microtune.sid,
  Nukenin_and_the_Ronin.sid, Sanxion_loader.sid, Shoot_em_Up_Destruction_Set_Menu.sid,
  Sometimes.sid, Wizardry_Remix.sid, and 3 others.

**What the pattern means**: the play dispatcher restructures the 3-voice call loop.
Instead of JSR × 2 then a special combined call, it does:

```
LDX #$02; LDY #$0E; JSR voice_sub    ; voice X=2, base register = Y=$0E
DEX     ; LDY #$07; JSR voice_sub    ; voice X=1, base register = Y=$07
DEX     ; LDY #$00                   ; voice X=0
STX zp; STY zp                       ; store X/Y for voice sub
...
```

Y=$0E/$07/$00 are the SID base register offsets (voice 3/2/1 = $D40E/$D407/$D400).
The V9.x variant passes the SID base register as a Y parameter to a shared voice
sub, rather than the V7.03 approach of loading Y from a per-voice table inside
the sub. Both produce identical SID writes; the architectural difference is internal.

**No distinct V9.x init** confirmed in binary: all 28 V9.x-dispatch SIDs also
carry the V7.03 D400-clear init (LDY #$16). So the "V9.x" sub-signature in sidid
specifically marks the restructured dispatch, not a different init or data format.

Confirmed by disassembly of Big_Bus.sid at $115A:
```
$115A: A2 02       LDX #$02
$115C: A0 0E       LDY #$0E        ; base = $D40E (voice 3)
$115E: 20 6A 11    JSR $116A
$1161: CA          DEX
$1162: A0 07       LDY #$07        ; base = $D407 (voice 2)
$1164: 20 6A 11    JSR $116A
$1167: CA          DEX
$1168: A0 00       LDY #$00        ; base = $D400 (voice 1)
$116A: 8E A9 10    STX $10A9       ; store voice idx
$116D: 8C AA 10    STY $10AA       ; store SID base
```

**Relationship to V8**: TMR stated (Lemon64 ~2003) that "EMS V8 driver exists and
was used in 'In_My_Life_My_Mind' and 'Combo_Racer'". Both of those SIDs are in
the 28-SID V9.x-dispatch group (`In_My_Life_My_Mind.sid` and `Combo_Racer.sid`
have this pattern). The V9.x sidid sub-signature likely captures what was
internally named "V8" or "V9" at Cosine — sidid uses external version numbering
that may not match Odie's internal labels.

### 3.5 EMS_V10.x (n=11 SIDs with expand loop, 1 officially tagged)

**sidid signature**:
```
A0 00 B9 ?? ?? 0A 99 ?? ?? B9 ?? ?? 2A 99 ?? ?? C8 C0 53 D0
```

Decoded:
```
LDY #$00
loop:
  LDA table_A,Y    ; B9 ?? ??
  ASL              ; 0A — shift left
  STA table_B,Y    ; 99 ?? ??
  LDA table_C,Y    ; B9 ?? ??
  ROL              ; 2A — rotate left (catches carry from ASL)
  STA table_D,Y    ; 99 ?? ??
  INY              ; C8
  CPY #$53         ; C0 53 — compare to 83
  BNE loop         ; D0 ED
```

**Meaning**: This is an init-time data expansion loop. On first run, it expands 83
packed frequency-table entries from two packed-byte tables (table_A at $1B37 and
table_C at $1B98 in Rescued_Pixels_3) into two full-byte tables (table_B at $1B43
and table_D at $1BA4). The ASL/ROL pair performs a 16-bit left-shift: the carry
from ASL(lo) feeds into ROL(hi), producing a 16-bit value from two packed 7-bit
fields. This allows storing 83 frequency values in half the space by packing
two 8-bit bytes per entry rather than two 7-bit values.

**Only `Rescued_Pixels_3.sid` (2025) is sidid-tagged `(EMS_V10.x)`**. The other
10 SIDs with the V10.x expand loop are sidid-classified as generic `EMS/Odie` —
either the V10.x sub-signature was not in sidid at time of HVSC #84 processing,
or those SIDs also have other EMS/Odie patterns that fire first.

**The 11 SIDs with the V10.x expand loop**:
- Rescued_Pixels_3.sid (2025, Arkanix Labs) — sidid: `(EMS_V10.x)`
- Brilliant_Maze.sid (2014, Cosine) — sidid: `EMS/Odie`
- Carl_Lewis_Challenge.sid (2021, Cosine)
- Dice_Skater.sid (2019, Cosine)
- End_of_the_World.sid (2009, Cosine)
- Firepower.sid (2020, Cosine)
- Hammer_Down.sid (2022, Cosine/Psytronik)
- Lovefunk_2SID.sid (2020, Cosine)
- Salty_Lemon.sid (~2012, Cosine)
- Star_Trooper.sid (~2012, Cosine)
- That_Old_Magic.sid (~2020, Cosine)

This suggests V10 was Cosine's active production version from ~2009–2025.

**V10.x init structure** (Rescued_Pixels_3, $1113):
```
$1113: PHA                           ; save subtune
$1114: LDA $1B43                     ; check if expand done (non-zero = already run)
$1117: BNE $112E                     ; skip expand on 2nd+ call
$1119: [V10.x expand loop $1119–$112D]
$112E: JSR $119C                     ; clear RAM block ($100F for #$FA bytes → 0)
$1131: PLA                           ; restore subtune A
$1132: AND #$1F                      ; mask subtune
$1134: STA $70                       ; temp
$1136: ASL; ADC $70; ...             ; subtune × 3 → offset
$113A: LDY #$EA (SMC target)         ; SMC: patch play dispatcher
...
$115A–$1166: JSR per-voice setup ×3
$1167: JSR clear_SID
$116A: patch SMC slots for current subtune
$116F: LDA #$0F; STA $101C           ; master vol target
$1174: STA $1013; RTS
```

V10 init: uses SMC (self-modifying code) to patch the subtune-specific call
addresses into the play dispatcher (at $11F2 in Rescued_Pixels_3). This is
one-time: if `$1B43 != 0`, the expand loop is skipped (idempotent after first call).

**V10.x clear routine** (`$11A7`):
```
LDX #$00
LDA #$00
loop: STA $D400,X; INX; CPX #$19; BNE loop
```
Uses X (not Y) index; count = $19 = 25 (registers $D400–$D418). Then:
```
LDA #$08; STA $D404; STA $D40B; STA $D412
```
Same gate-prime as V7.03 but with a count of 25 (includes $D418) vs. 23 (excludes
$D418).

**V10.x play dispatcher** (`$11F1`):
```
$11F1: LDA #$00
$11F3: BEQ $124D       ; if A=0 always skip → RTS (SMC placeholder = $00 initially)
```
The `A9 00 / F0 58` block is a SMC slot: init patches `$11F2` to the actual
subtune-specific flag value (`01`). This is how multi-subtune is implemented —
init patches the play dispatcher to select the right subtune context.

### 3.6 Odie/Cosine (n=9 SIDs — Distinct Engine)

**sidid signature**:
```
60 BD ?? ?? 38 FD ?? ?? 9D && 38 DE && 18 7D ?? ?? 9D && FE ?? ?? BD ?? ?? C9 ?? F0
```

These 9 SIDs span 1987–1991 and include both Connolly's early Cosine works
(CDU_Magazine_loadertune, 1990) and two Marc François (Skywave/Francois_Marc)
pieces (Hektic, Warflame). They are classified as `Odie/Cosine` not `EMS/Odie`.

**Load address**: completely variable ($E900, $C000, $65C0, $E9B9, $0BF7, $BA00,
$7DB0, $E000, $A000) — not the canonical EMS $1000 layout.

**Play structure** (CDU_Magazine_loadertune, play=$E99E):
```
LDA $E904         ; check global state byte
BEQ $E9D2         ; zero = normal play
CMP #$01          ; 1 = init/reset pending
BNE $E9D1         ; else RTS immediately
; init path: clear state, set up voice start positions
LDX #$02
LDA #$FF; STA $E90B,X   ; mark voice position = FF (not started)
LDA #$01; STA $E908,X   ; tempo counter
DEX; BPL
; --- normal play path at $E9D2: ---
LDX #$02
LDY $E999,X       ; per-voice instrument index
JSR $E9E1         ; process voice
LDX $E99C; DEX; BNE loop
```

**Sequence command bytes** (from $E9FD onwards, indirect ZP $F8/$F9):
```
LDA ($F8),Y
CMP #$80          ; <$80 = note (raw byte)
CMP #$FF          ; $FF = end of sequence (stop + trigger init)
CMP #$FE          ; $FE = stop (no restart)
CMP #$FD          ; $FD = next-sub increment (advance instrument program)
CMP #$80          ; $80–$FE = control command (AND #$7F → instrument index)
```

This is a substantially different byte-stream format than the main EMS/Odie engine.
It uses a flat sequence-pointer walk without the multi-level track/sequence
hierarchy of V7+. These are Odie's pre-EMS or very early EMS works.

**SID write** (from $E9D7):
- Indirect ZP table-walk
- Per-voice: writes $D400/$D401 (freq) indirectly
- $D418 written at $EB47 (from filter table lookup)
- No standardised jump table at start

Conclusion: **Odie/Cosine is NOT EMS**. It is a distinct pre-EMS player from
Sonix Systems / early Cosine era (1987–1991). It shares the ZP-indirect
walk mechanism but has an entirely different song format and state model.

### 3.7 Odie_tiny (n=3 SIDs — Compact Variant)

**sidid signature**:
```
18 7D ?? ?? 29 7F A8 B9 ?? ?? 48 B9 ?? ?? BC ?? ?? 99 01 D4 68 99 00 D4 FE
```

Three SIDs: 4k_Digi_Competition_Entry.sid, 4k_Party_2.sid, Wild_One.sid —
all by Sean Connolly, 1998–1999, Cosine.

**Structure** (Wild_One.sid, play=$10A8):
Init at $107A:
```
LDA #$00; TAX
loop: STA $100A,X; INX; CPX #$38; BNE loop   ; clear 56 bytes from $100A
LDA #$0F; STA $D418                           ; master vol = 15
LDA #$00; TAY
loop: STA $D400,Y; INY; CPY #$18; BNE loop   ; clear $D400–$D417
```

Play at $10A8:
```
LDA $103F; CMP $1040,X; [filter sweep]; STA $D416
DEC $100A; BMI [restart]
LDX #$02; JSR per_voice
DEX; JSR per_voice
DEX; [inline last voice]
```

The tiny player is radically simplified:
- Flat tempo counter at $100A (single counter, not per-voice)
- Per-voice state stride is different (instrument fields directly indexed)
- Sequence walk is bare note-byte with duration packed into nibble
- No multi-track tempo, no filter table structure
- Total player code ~$57A–$107A = ~$1000 bytes (1K), fitting the 4k constraint

**SID writes** (confirmed at $D400/$D401/$D403/$D402/$D404,Y — same per-voice
block structure as V7.03 but written in different order): freq lo/hi, PW hi/lo,
ctrl register. Note that $D402 and $D403 (PW lo/hi) writes are present but
in a simpler fixed sequence.

Conclusion: **Odie_tiny is a stripped EMS player**: same author, same general
SID write block structure, but a minimal ~1K player intended for size-constrained
(4K) productions. Incompatible data format with full EMS.

### 3.8 Odie/Pulse (n=2 SIDs — Oldest Known)

**sidid signature**:
```
9D 00 D4 E8 E0 20 D0 F5 A9 ?? 8D 18 D4 A9
```

Two SIDs: Crazy_Mirrors.sid (1988, Pulse Productions), Merry_Christmas_87.sid
(1988, Pulse Productions).

Load addresses: $8FA2 and $5000. Play at $8FAE and $C046. No standard jump table.

**Init** (Crazy_Mirrors, $8FA2):
```
A2 35; STX $01       ; set CPU banking register (!)
JSR $8FBA            ; sub
A2 37; STX $01       ; restore
RTS
```

The explicit `STX $01` writes to the C64 banking register — this is a very early
player that manipulates CPU bank switching directly, consistent with the
1987–1988 era when KERNAL access patterns were common.

**Play** (Crazy_Mirrors, $8FAE):
```
JSR $8FBD
JSR $2090
JSR $20A0
JSR $00C0
[full indirect-dispatch via JMP ($FE03)]
```

Uses a completely different calling convention with JSR to $0000 range and KERNAL
addresses. The `E0 20 D0 F5` in the sidid signature (`CPX #$20; BNE -$0B`) = a
loop that clears $20 = 32 SID register slots.

Conclusion: **Odie/Pulse is a completely different pre-Cosine player**. 1987–1988
Pulse Productions era. Shares only the author. No data format compatibility with EMS.

---

## 4. Comparison Table: Version Characteristics

| Feature | Odie/Pulse | Odie/Cosine | V7.03 (EMS) | V9.x dispatch | V10.x |
|---------|:---------:|:-----------:|:-----------:|:-------------:|:------:|
| Era | 1987–88 | 1987–91 | 1996–2007 | ~2000–2010 | ~2009–2025 |
| 5-JMP table | No | No | Yes | Yes | Yes |
| Init entry = load | N/A | No | Yes | Yes | Yes |
| D400-clear via LDY#$16 | No | No | Yes | Yes | No |
| D400-clear via LDX loop | No | No | No | No | Yes (CPX #$19) |
| Voice dispatch: X=2,1,0 JSR | No | No | JSR+special | Uniform JSR | JSR |
| Y=SID offset passed in | No | No | No (table) | Yes (explicit) | Yes |
| ZP $F8/$F9 indirect | Yes | Yes | Yes | Yes | Yes |
| $FF sentinel = song loop | Yes | Yes | Yes | Yes | Yes |
| $FE = silence voice | No | Yes | Yes | Yes | Yes |
| V10 data-expand loop | No | No | No | No | Yes |
| SMC subtune dispatch | No | No | No | No | Yes |
| CPU bank switch | Yes | No | No | No | No |
| KERNAL calls | Possible | No | No | No | No |
| Compact (tiny) | No | No | No | No | No |

Odie_tiny is omitted from the table as it is a special 1K stripped variant.

---

## 5. State Block Map (V7.03 at $1000 base)

From read-only disassembly of Coup_De_Grace.sid. Per-voice state is
X-indexed (X=0/1/2 → voice 1/2/3). State at load+offset:

| load offset | per-voice (idx+X) | content | notes |
|------------|-------------------|---------|-------|
| $000F + X | $100F,X | seq ptr lo | lo-byte of ZP $F8 |
| $0012 + X | $1012,X | seq ptr hi | hi-byte of ZP $F9 |
| $0015 + X | $1015,X | SID base Y | 0/$07/$0E for V1/V2/V3 |
| $0019 + X | $1019,X | duration counter | counts down from tempo |
| $001C + X | $101C,X | tempo reload value | loaded from subtune track data |
| $001F + X | $101F,X | note counter | another down-counter |
| $0025 + X | $1025,X | instrument program step | position in waveform program |
| $002B + X | $102B,X | sequence position Y | current offset in ZP-walk |
| $0034 + X | $1034,X | glide counter | frames remaining for glide |
| $003A + X | $103A,X | transpose | current semi-tone transpose |
| $003D + X | $103D,X | instrument index | current inst idx |
| $0040 + X | $1040,X | soundtype bits | effect mode (vib/arp/osc) |
| $0043 + X | $1043,X | arp position | offset into arp table |
| $0049 + X | $1049,X | vibrato accumulator | vibrato phase counter |
| $004C + X | $104C,X | soundtype cache | copy of soundtype field bits 0-2 |
| $004F + X | $104F,X | freq lo | current freq low byte |
| $0052 + X | $1052,X | freq hi | current freq high byte |
| $0055 + X | $1055,X | glide note | portamento target note |
| $0058 + X | $1058,X | pulse lo | pulse width accumulator lo |
| $005B + X | $105B,X | pulse hi | pulse width accumulator hi |
| $005E + X | $105E,X | pulse target | from instrument table |
| $0061 + X | $1061,X | hard-restart gate | gate-off frame state |
| $0064 + X | $1064,X | instrument step 2 | waveform program 2nd counter |
| $0067 + X | $1067,X | vibrato step | position in vibrato table |
| $006D + X | $106D,X | osc-glide phase | oscillating glide direction |
| $0070 + X | $1070,X | vibrato delay ctr | counts from vibdelay down to 0 |
| $0073 + X | $1073,X | PW sub-table idx | for pulse width min/max check |
| $0079 + X | $1079,X | waveform program ptr | offset into waveform table |
| $007C + X | $107C,X | pulse lo init | PW lo from instrument |
| $007F + X | $107F,X | pulse hi init | PW hi from instrument |
| $0091 + X | $1091,X | subtune note ptr | instrument index override for subtune |
| $009A + X | $109A,X | voice flags | bit 0=active, bit 4=hard-restart, bit 5=note-trigger, bit 7=PW direction |
| $00B3 + X | $10B3,X | waveform prog ptr lo | lo of ZP $F8 for waveform |
| $00B6 + X | $10B6,X | waveform prog ptr hi | hi of ZP $F9 for waveform |

**Global (single):**

| load offset | address | content |
|------------|---------|---------|
| $00A3 | $10A3 | filter mode byte (ORA/AND $D417) |
| $00A6 | $10A6 | filter table index |
| $00A7 | $10A7 | filter table step |
| $00A8 | $10A8 | fade active flag |
| $00A9 | $10A9 | fade speed |
| $00AA | $10AA | fade counter |
| $00AB | $10AB | subtune-change flag |
| $00AC | $10AC | master volume / filter state ($D418 shadow) |
| $009D | $109D | filter freq lo shadow ($D415) |
| $009E | $109E | filter freq hi shadow ($D416) |

This map is for V7.03 at $1000; all offsets scale with load address.

---

## 6. Data Section Layout (V7.03 at $1000 base)

Approximate layout extracted from Coup_De_Grace.sid ($1000–$2337):

| address range | content |
|--------------|---------|
| $1000–$100E | 5-JMP table (15 bytes) |
| $100F–$10B7 | Per-voice state block (165 bytes, per §5 map) |
| $10B8–$1128 | Init routine + sub-routines (fade, clear) |
| $1129–$15FF | Play routine + subroutines (sequence decoder, SID write, vibrato, etc.) |
| $1600–$187F | Effect chain: oscillating glide, portamento, arpeggio |
| $1880–$194F | Filter sweep + fade step + waveform program walker |
| $1950–$19B1 | Pulse-width lo lookup table (96 entries) |
| $19B2–$1A11 | Pulse-width hi lookup table (96 entries) |
| $1A12–$1A75 | Frequency lo lookup table (96 entries × 2 = 48 per direction?) |
| $1A76–$1AA1 | Filter pointer table (32-entry: 2-byte ptrs to filter tables) |
| $1AA2–$1AA5 | Arpeggio pointer table fragment |
| $1AA6–$1B25 | Instrument records (32 instruments × 3 bytes = 96 — check) |
| $1B26–$1B3B | Vibrato table or waveform loop targets |
| $1B3C–$1B51 | ADSR attack/decay table per instrument |
| $1B52–$1B67 | ADSR sustain/release table per instrument |
| $1B68–$1B9F | Waveform tables (up to $18 tables, variable length) |
| $1BA0–$1BBF | Arpeggio tables |
| $1BC0–$1C3F | Instrument data (soundtype, vibrato, pulse parameters) |
| $1C40–$1C5F | Subtune sequence pointer table (3 × n_subtunes entries) |
| $1C60–$2337 | Sequence data (compressed stream) |

NOTE: The above is approximate, derived from pointer references in the disassembly.
The exact boundaries differ per SID (song data size varies). The engine code
($1000–$194F approx.) is identical across all same-variant SIDs; only the tables
and sequence data from ~$1950 onwards differ.

---

## 7. Filter Model

From HELP.FILTER (in `cluster_editor_and_cosine.md`) and binary inspection:

- $D415/$D416: filter frequency (16-bit, lo/hi), driven by filter table sweep
- $D417: resonance (hi nibble) + voice routing (lo nibble 0-7, voice 1=bit0,
  voice 2=bit1, voice 3=bit2, external=bit3)
- $D418: master volume (lo nibble $0–$F) + filter mode (hi nibble):
  $10 = lowpass, $20 = bandpass, $40 = highpass, $70 = all (lowpass+bandpass+highpass)

Filter is **written once per play() frame** after all three voice updates. It is
**NOT sped up by multispeed** (stated in HELP.GENERAL). The sound engine (JMP[2])
handles voices at multispeed rate but skips the filter update.

---

## 8. SID Write-Log Model Summary

For **frame-by-frame verification** purposes (Mode 1):

Per play() call, writes are emitted in this logical order:

1. **Voice X=2** (SID voice 3, $D40E base):
   - $D40E freq lo, $D40F freq hi
   - $D410 PW lo, $D411 PW hi
   - $D412 ctrl (or $D412 gate-off + $D413 AD + $D414 SR on hard-restart)

2. **Voice X=1** (SID voice 2, $D407 base):
   - $D407 freq lo, $D408 freq hi
   - $D409 PW lo, $D40A PW hi
   - $D40B ctrl

3. **Voice X=0** (SID voice 1, $D400 base) — handled inside global update:
   - $D400 freq lo, $D401 freq hi
   - $D402 PW lo, $D403 PW hi
   - $D404 ctrl

4. **Global filter** (after all voices):
   - $D418 master volume + filter routing
   - $D415 filter freq lo
   - $D416 filter freq hi
   - $D417 resonance / voice routing

**Notes**:
- Vibrato, portamento, and PW cycling modify the freq/PW values computed in steps
  1–3 before they are written. The final written values are the post-effect values.
- Hard restart inserts an extra gate-off write ($D404/$D40B/$D412 = 0) one frame
  before the gate-on write, then the following frame writes gate-on with ADSR primed.
- The exact sub-order within each voice block (whether PW is written before or after
  freq) may vary by frame state and effect path; the above is the dominant order from
  disassembly of the primary SID write stub ($1816).
- For V9.x tunes the voice block sequence is functionally identical; only the dispatch
  mechanism changed. For V10.x: same SID write structure; the data-expand loop only
  runs once at init.

---

## 9. Tool Handling

### libsidplayfp / VICE

EMS/Odie SIDs are standard PSID. libsidplayfp runs them correctly via the standard
PSID emulation path (CPU 6510, SID 6581/8580 selected by PSID header). The jump-table
calling convention (init() = load+$0000, play() = load+$0003) is fully PSID-compliant.
No special-case handling required. `siddump --writelog` captures the write stream
normally.

One exception: Brian_the_Lion.sid has `speed = 1` (CIA-timed, bit 0 of PSID speed
field set). This is the sole CIA-timed EMS SID in the corpus. libsidplayfp handles
it correctly; siddump `--writelog-per-irq` should be used for per-play() verification
if needed.

### DeepSID

No EMS-specific handling found in the DeepSID GitHub repository. EMS SIDs play via
the standard WebSid / jsSID JS emulators. DeepSID may display the sidid-detected
engine name in its metadata panel (EMS/Odie, EMS_V7.03, etc.) but this comes from
the HVSC sidid classification file, not any DeepSID-internal logic.

### sidid

Three EMS-family label groups in sidid.cfg (as of cadaver/sidid master):

**Family label `EMS/Odie`** — 5 alternative patterns (OR-combined), matches all
V7.03, V8/V9.x, and most V10.x SIDs:
```
B9 ?? ?? 85 F8 B9 ?? ?? 85 F9 BC ?? ?? B1 F8 C9 FF D0 ?? C8 B1 F8
BD ?? ?? 85 F8 BD ?? ?? 85 F9 BC ?? ?? B1 F8 C9 40 90 ?? C9 FE D0
B9 ?? ?? AC ?? ?? 99 06 D4 AD ?? ?? 99 05 D4 AD ?? ?? 29 FE 99 04 D4
BC ?? ?? B9 ?? ?? 85 ?? 0A 85 ?? 18 65 ?? 85 ?? ... BD ?? ?? 29 ?? F0 ?? BC ?? ?? 4C
85 ?? 06 ?? 26 ?? 26 ?? 26 ?? 38 A5 ?? E5 ?? AA A5 ?? E5 ?? 90
```

**Sub-variant labels** (additional narrowing — each fires separately, not modifying the
family label): `(EMS_V7.03)`, `(EMS_V9.x)`, `(EMS_V10.x)`.

**Related labels** (different sidid entries): `Odie/Cosine`, `Odie/Pulse`, `Odie_tiny`.

---

## 10. Leads to Follow

1. **Exact V7.03 instrument binary record layout**: the 15-field instrument model
   (from HELP files, documented in `cluster_editor_and_cosine.md` §6.3) needs
   byte-offset confirmation. The binary record read by the play dispatcher at $1A76
   (freq ptr table) and $1BC0 (instrument table) regions needs a full mapping.
   Reverse one compiled module with known instruments (Coup_De_Grace is ideal —
   simple tune with few instruments).

2. **V8 vs V7.03 differences**: sidid has no V8 sub-signature. The "V8" driver (used
   in In_My_Life_My_Mind.sid and Combo_Racer.sid, per TMR) is one of the 28 V9.x-
   dispatch SIDs — but are those two specifically V8 or V9? The dispatch restructure
   (V9.x pattern) is the only confirmed code change visible. Does V8 also change any
   data format fields?

3. **Subtune pointer table format**: at $1C5A (Coup_De_Grace), the subtune-start
   table. The init multiplies subtune × 3 + 2 → table index. But each subtune gets
   3 pointers (one per voice start position in the sequence data). Need to confirm
   whether multi-subtune SIDs (Cyberwing, 25 subtunes) actually use this scheme or
   a different approach.

4. **Waveform table terminal format**: from HELP.WAVES: `$FF, loop_line_number`.
   What is `loop_line_number` — an absolute sequence byte index, or a table-row count?
   Also: how is the firstwf byte (instrument field 01) connected to the waveform table?
   Does it replace row 0 of the table, or is it separate?

5. **Filter table wire format**: from HELP.FILTER: each entry = dest + rate, up to
   7 destinations, terminate with $FFFE, loop with $FFFF. What is the binary layout?
   2 bytes (dest-hi, rate) or 4 bytes (dest-lo, dest-hi, rate-lo, rate-hi)?
   Needs binary confirmation from the filter table region of a compiled module.

6. **V10.x SMC patch targets**: in Rescued_Pixels_3, the init patches the play
   dispatcher at $11F2. For multi-subtune SIDs (Hammer_Down has 12 subtunes,
   Brilliant_Maze has 8), what does the SMC patch mechanism look like when n_subtunes
   > 1? Does init patch different addresses for different subtunes, or is there a
   lookup table?

7. **Odie_tiny sequence format**: Wild_One uses a much simpler byte stream. The
   sidid signature ends with `FE` (a possible sequence terminator). Fully decode one
   Odie_tiny sequence to confirm the format (note byte, duration, commands).

8. **Odie/Cosine data format**: the CDU_Magazine player uses $FF = stop + trigger
   init, $FE = stop, $FD = increment sub-sequence. Fully decode one Odie/Cosine
   sequence to map the full command set. The player from 1990 uses a per-voice
   instrument table at $E914,X — map those fields.

9. **PSID `speed` bit in Brian_the_Lion**: only CIA-timed SID in corpus. What EMS
   feature triggers CIA mode? Is it a player flag, a PSID header setting added
   by the HVSC archivist, or does the EMS player itself write CIA registers?

10. **EMS V10 disk image**: the YouTube videos "EMS V10.0 teaser" and "Happy Birthday
    EMS V10.01" confirm the tool exists. No CSDb ID > 4649 found for EMS V10. Search
    Wayback Machine / scene.org / Pouet for the V10 download.
