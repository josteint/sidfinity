; ============================================================================
; DMC V4 CANONICAL PLAYER ("player by brian of graffity 91")
; ============================================================================
; Representative: hvsc84/MUSICIANS/A/Amadeus_Slash_Design/Geometrical_Zaks.sid
;                 "Geometrical Zaks" — Björn Stockleben (Amadeus), 1994 Slash
;                 Design. 3 subtunes. Load $1000, Init $1000, Play $1003.
;                 Binary $1000-$21EC (4589 bytes). Auto-traced 1720 code bytes.
;
; THIS IS THE DOMINANT DMC PLAYER: the fingerprint census (2026-06-12,
; tools/engine_fingerprint.py over hvsc84.db, see
; pipelines/dmc/docs/fingerprint_census.md) shows family 1 = 5401 / 10676
; HVSC DMC SIDs (50.6%) share this player (reloc-invariant opcode skeleton;
; 0.973 Jaccard vs the V4 player binary carved from DMC 4 Editor 2025).
; This SID carries the dominant EXACT opcode hash (3002 members). Family 2
; (2889 SIDs, 0.732) is a V4-derived variant to be diffed against this later.
;
; Per the CORE TENET we do NOT reproduce this code — the composer emits our
; own engine. This disasm exists to give the EXTRACT the data formats and
; state semantics; correctness is then judged via the write-log.
;
; ============================================================================
; KEY FINDING — PACKER-PATCHED TABLE OPERANDS (probed across family 1):
; ============================================================================
; The DMC editor's packer lays the song data regions contiguously after the
; player and PATCHES the player's absolute operands per song. Verified by
; probing 7 operand sites across family-1 members: instr table is ALWAYS
; $18F0, but wavectrl/wavefreq/filterdef/tunetab/sectorptr addresses all
; differ per SID. Extraction must therefore recover table addresses by
; DATAFLOW (read the operands at the known code offsets), never by fixed
; layout. Operand sites (address of the abs,y operand = code addr + 1):
;     $1227 = instrument records      ($18F0 in all standard members)
;     $159C = wave ctrl table         (Zaks $19D7)
;     $15B9 = wave freq/offset table  (Zaks $1A27)   [2nd site $15FB]
;     $1296 = filter definition table (Zaks $1A77)   [+1 sites $12AC/B2/B8,
;                                                      steps $13E7/$13ED +4/+10]
;     $180E = tune pointer records    (Zaks $1C10)   [sites $1050/56, $1813]
;     $1103 = sector ptr lo           (Zaks $217B)
;     $1108 = sector ptr hi           (Zaks $21B4)
; Region sizes are implied by the address DELTAS (e.g. wave table length =
; wavefreq - wavectrl; instrument count = (wavectrl - $18F0) / 11).
; A few family-1 members have wrapper inits / shifted code (e.g.
; On_My_Way_to_X, Retro_Tech) — the extraction factory must probe, FC-style.
;
; ============================================================================
; MEMORY MAP (Geometrical_Zaks; starred regions move per song)
; ============================================================================
;   $1000-$100B  entry jump table (init / play / all-off / sfx-note)
;   $100C-$101C  global player vars (see VARIABLE MAP)
;   $101D-$101F  JMP $1807 (tune-select entry, also reached from init)
;   $1020-$104F  copyright string "MUSIC BY ..." ($1040 doubles as scratch!)
;   $1050-$1646  player code (init tail, play loop, voice engine)
;   $1647-$16A6  freq table LO, 96 entries  (FIXED addr — code-addressed)
;   $16A7-$1706  freq table HI, 96 entries  (FIXED addr)
;   $1707-$17BF  per-voice state + constants (see VARIABLE MAP)
;   $17C0-$188D  player code (sector dispatch, helpers, tune setup)
;   $1888-$18E7  per-note vibrato depth table (FIXED; OVERLAPS code $1888-8D:
;                notes 0-5 read code bytes — Hubbard-style space trick)
;   $18F0-$19D6* instrument records, 11 bytes each (count = delta/11; 21 here)
;   $19D7-$1A26* wave table CTRL bytes   (parallel array #1)
;   $1A27-$1A76* wave table FREQ bytes   (parallel array #2, same index)
;   $1A77-$1A86* filter definitions, 16 bytes each (1 here)
;   $1A87-$1C0F* track (orderlist) data, per subtune × voice
;   $1C10-$1C27* tune pointer records, 8 bytes per subtune:
;                [V1ptr lo,hi] [V2ptr lo,hi] [V3ptr lo,hi] [speed] [mastervol]
;                (research.md said "6 used + 2 pad" — WRONG, all 8 used)
;   $1C28-$217A* sector (pattern) data, variable length each
;   $217B-$21B3* sector pointer table LO (one byte per sector; 57 here)
;   $21B4-$21EC* sector pointer table HI (file ends with this — anchor)
;
; ZERO PAGE: $F8/$F9 only (track ptr, then reused as sector ptr within a
; fetch). research.md's "$FB-$FF (5 bytes)" is WRONG for this player.
;
; ============================================================================
; GLOBAL VARIABLE MAP
; ============================================================================
;   $100C-$100E  voice active flag (1=run, 0=stopped by track $FE)
;   $100F-$1011  gate mask, ANDed onto wave ctrl before $D404 write:
;                $FF=gate as wave table says, $FE=force gate off;
;                $7D SWITCH toggles bit0 (tie/legato)
;   $1012-$1014  current note (incl. transpose)
;   $1015-$1017  current instrument number
;   $1018        $D417 routing shadow (lo nibble: voice filter-route bits).
;                NOT cleared by init — ships with a leftover value in the
;                file image ($01 here) until instruments set/clear it.
;                (init.sid priming candidate for USF!)
;   $1019        dual-effect ($40) global frame parity (half-rate clock)
;   $101A        temp (slide subtract operand)
;   $1040        temp/scratch INSIDE the copyright string (SR override calc)
;
; PER-VOICE STATE (x = voice 0-2), all in $1707-$17BF:
;   $1707,x/$170A,x  track ptr lo/hi (set from tune record at init)
;   $170D,x  CONST: SID register offset 0/7/14
;   $1710,x  CONST: filter route bit  1/2/4
;   $1713,x  CONST: complement mask  $FE/$FD/$FB
;   $1716    speed (tick period - 1), from tune record byte 6
;   $1717    master volume (lo nibble of $D418), tune record byte 7
;   $1718    speed counter (DEC per frame; reload = tick)
;   $1719    filter: current step index 0-5
;   $171A    filter: frames spent in current step
;   $171B    filter: definition base index (def# << 4)
;   $171C    filter: current cutoff (written to $D416 every frame)
;   $171D    filter: repeat/loop step index (def byte 2)
;   $171E    filter: stop cutoff value (def byte 3)
;   $171F    temp (pulse step nibble / glide step / wave jump distance)
;   $1720    filter claimed-this-frame flag (first filter-voice wins)
;   $1721    filter: current step size cache
;   $1722    filter: current step duration cache
;   $1723    filter resonance (def byte 0 hi nibble) → $D417 hi
;   $1724/$1725  freq temp for the dual-effect path
;   $1726,x  track position
;   $1729,x  sector position
;   $172C,x  transpose (signed semitones, from track $8x/$Ax)
;   $172F,x/$1732,x  base freq lo/hi (from freq tables at note/wave step)
;   $1735,x/$1738,x  freq offset accumulator lo/hi (vibrato/glide)
;   $173B,x  duration counter (DEC per tick; 0 → fetch next event)
;   $173E,x  duration reload (sector $80-$BF & $3F)
;   $1741,x  glide speed nibble (0 = no glide active)
;   $1744,x/$1747,x  glide start note / target note
;   $174A,x  new-note pending flag ($FF on fetch frame → init next frame)
;   $174D,x  instrument offset (instrument# × 11)
;   $1750,x/$1753,x  pulse width accumulator lo/hi
;   $1756,x  PW bound A (instr byte 2 hi nibble)
;   $1759,x  PW bound B (= bound A EOR $0F)
;   $175C,x  PW current step (phase nibble + base)
;   $175F,x  PW step base (instr byte 6 hi nibble)
;   $1762,x  PW phase index 0-5 (selects nibble of instr bytes 3-5)
;   $1765,x  PW direction (0=up, 1=down)
;   $1768,x  vibrato direction (0=up, 1=down)
;   $176B,x  vibrato step counter (counts to width)
;   $176E,x  vibrato ramp counter (counts to instr byte 8)
;   $1771,x  vibrato delay counter (instr byte 7 hi nibble >> 1, ×8 frames)
;   $1774,x  vibrato width (instr byte 7 lo nibble; DOUBLES each half-cycle
;            while ramping — see L_1567)
;   $1777,x  vibrato ramp limit / dual-effect slide speed (instr byte 8)
;   $177A,x  wave table position
;   $177D,x  FX flags cache (instr byte 10)
;   $1780,x  current wave ctrl byte (masked → $D404 each frame)
;   $1783,x  current wave note (write-only in reachable code)
;   $1786,x  post-note guard: set 2 at note init; while >0 the end-of-note
;            gate logic (L_132D) is skipped → gate-on lasts 3 frames minimum
;   $1789,x  cleared at note init, never read in reachable code
;   $1792,x/$1795,x  vibrato step size lo/hi (lo = per-note from $1888 tbl)
;   $1798,x/$179B,x  dual-effect slide accumulator lo/hi
;   $17B0,x  soft-start toggle ($7C cmd): nonzero = skip hard-restart prep
;            on note load; RESET to 0 at each sector end ($7F)
;   $17B3,x  sustain override ($Fx cmd): 0 = use instrument SR as-is,
;            n = replace sustain nibble of SR with n
;
; ============================================================================
; SECTOR (PATTERN) BYTE DISPATCH — order as the code tests it
; ============================================================================
;   $F0-$FF  VOL.x: sustain-nibble override → $17B3,x  (prefix; loops)
;   $7C      toggle soft-start mode $17B0,x            (prefix; loops)
;   $7E      rest: duration ← reload, no state change (prev note releases
;            per its flags; NOTE: a HOLDING instrument gates off only when
;            the rest's counter hits 1 — verify via write-log)
;   $7D      SWITCH: gate mask EOR $01 (tie/legato) + duration ← reload
;   $C0-$DF  glide/slide: AND $1F → bit4 = mode, lo nibble = speed → $1741,x
;              mode 0 ($C0-$CF): [cmd][noteA][noteB] — plays A, glides to B
;              mode 1 ($D0-$DF): [cmd][noteB] — slides current note to B
;            ($E0-$EF alias mode 0; unused by the editor)
;   $80-$BF  duration: AND $3F → reload $173E,x        (prefix; loops)
;   $60-$7B  instrument select: AND $1F → $1015,x      (prefix; loops)
;   $00-$5F  note → note load (transpose added, freq looked up, hard
;            restart prep unless $17B0,x)
;   $7F      end of sector (tested AFTER a note loads, in sub_11E6:
;            advances track pos, resets sector pos + soft-start toggle)
;
; CORRECTIONS vs docs/research.md (web-sourced; the binary is the truth):
;   - instrument vs duration ranges were SWAPPED there ($60-$7C / $80-$9F)
;   - glide is $C0-$DF (not $A0-$BF); $F0-$FF is VOL (not unused)
;   - track transpose: $80-$9F = down 0-31, $A0-$BF = up 0-31 (5-bit, not 4)
;   - track sector range is $00-$7F (not $00-$3F)
;   - instrument bytes 2/6/9 were rotated there; truth below
;   - wave table: ANY byte >= $90 is jump-back (val-$90); no $FE/$FF specials
;   - hard-restart preset is AD=$0F SR=$0F (not $0000/$0F00/$F800)
;
; ============================================================================
; INSTRUMENT RECORD (11 bytes at $18F0 + n*11)
; ============================================================================
;   +0   AD → $D405 (written at note init, frame 2 of the note)
;   +1   SR → $D406 (sustain nibble replaceable by the $Fx VOL override)
;   +2   pulse: hi nibble = PW bound A (its EOR $0F = bound B);
;               lo nibble = PW hi-byte initial value
;   +3-5 pulse speed nibble sequence (6 phases: hi,lo,hi,lo,hi,lo as the
;        phase index $1762,x advances 0-5 and stops at 5)
;   +6   hi nibble = PW step base (added to every phase nibble);
;        lo nibble = filter definition index (used iff flag $20)
;   +7   hi nibble >> 1 = vibrato delay (frames = nibble × 8);
;        lo nibble = vibrato width
;   +8   vibrato ramp limit; for flag $40 instruments: per-note slide speed
;        (bit7 = slide up [subtract], else down [add to subtrahend])
;   +9   wave table start index
;   +10  FX flags:
;        $01 drum mode: wave FREQ byte is an absolute $D401 hi value
;            (lo forced 0) instead of a semitone offset added to the note
;        $02 no filter reset (keep running filter at note init)
;        $04 no pulse reset (keep PW state at note init)
;        $08 no gate-off (gate stays until next note's mask)
;        $10 holding: gate off only when duration counter == 1
;            (without $08/$10 the gate drops after 3 frames and the note
;             tail rides the SID release — the classic DMC envelope model)
;        $20 filter on (claims the global filter for this voice)
;        $40 dual effect: per-note slide at half frame rate (global parity
;            $1019), speed = byte 8
;        $80 cymbal: note-init writes freq $FFFF + ctrl $81 (gated noise)
;            and SKIPS the wave/pulse writes that frame
;
; ============================================================================
; FILTER DEFINITION (16 bytes at filterdef + def# * 16)
; ============================================================================
;   +0   hi nibble = resonance → $D417 hi; lo nibble = filter MODE bits
;        (LP/BP/HP) → $D418 hi nibble (ORed with master volume!)
;   +1   initial cutoff (→ $171C → $D416 every frame)
;   +2   repeat step index (loop point after step 5)
;   +3   stop cutoff (cutoff == this → freeze)
;   +4-9   step sizes 0-5 (signed 8-bit, added to cutoff per frame)
;   +10-15 step durations 0-5 (frames per step)
;   Only ONE voice owns the filter per frame ($1720 claim flag, first
;   filter-flagged voice in X order wins).
;
; ============================================================================
; WAVE TABLE (two parallel byte arrays, same index, length = delta)
; ============================================================================
;   CTRL array → $D404 (after AND gate mask): waveform + gate/sync/ring.
;     byte >= $90: jump back (byte - $90) positions and re-read
;     ($91 = hold previous entry forever; $9x = loop of x entries).
;   FREQ array, same index: semitone offset added to the current note
;     (arpeggio); drum-mode instruments ($01): absolute $D401 value.
;   Stepped EVERY FRAME (not per tick).
;
; ============================================================================
; PLAY FLOW (one frame)
; ============================================================================
;   play: DEC speed ctr (reload = "tick") → per voice: voice_tick →
;         $D416 = cutoff, $D417 = res | route
;   voice_tick: inactive/non-tick/duration>0 → frame_entry
;               duration hit 0 on a tick → track_fetch → sector bytes
;               (prefix cmds loop; a note ends the fetch)
;   note fetch frame  : TEST bit $08 → $D404, $0F0F → AD/SR (hard restart;
;                       skipped in soft-start mode), pending = $FF
;   note frame 2      : real AD/SR + pulse/filter/vibrato init + wave step
;                       + full freq/PW/ctrl writes ($1786 guard = 2)
;   frames 3-4        : effects run, gate logic skipped (guard 2→1→0)
;   frames 5+         : gate logic active (non-holding instruments get the
;                       gate-off mask), effects + wave step + writes
;   Per-frame SID writes per voice (steady state): freq lo,hi ($D400/01),
;   PW lo,hi ($D402/03), ctrl ($D404) — then globally $D416, $D417.
;   $D418 is written ONLY at init (master vol) and at filter note-init
;   (mode | vol). $D405/$D406 only at note boundaries. ORDER within a
;   frame: V1 freq,PW,ctrl, V2..., V3..., $D416, $D417.
;
; ============================================================================
; ENTRY POINTS
; ============================================================================
;   $1000 init       A = subtune → JMP $101D → JMP $1807
;   $1003 play       once per frame
;   $1006 all_off    deactivate all voices + clear gate masks (JMP $162F)
;   $1009 sfx_note   A = note, Y = instrument, X = voice → JMP $163E
;   $101D tune_select(A = subtune) — same as init
; ============================================================================

; ======= init: =======
init:
    $1000: 4C 1D 10   JMP $101d        ; → L_101D → $1807 tune setup
; ======= play: =======
play:
    $1003: 4C 85 10   JMP $1085        ; → L_1085 play body
sub_1006:                              ; ENTRY: all voices off
    $1006: 4C 2F 16   JMP $162f        ; → L_162F
sub_1009:                              ; ENTRY: sfx note (A=note Y=instr X=voice)
    $1009: 4C 3E 16   JMP $163e        ; → L_163E
; ----- $100C-$101C: global player vars (see map above) -----

L_101D:                                ; tune-select entry (A = subtune)
    $101D: 4C 07 18   JMP $1807        ; → L_1807 tune setup
; ----- $1020-$104F: copyright string "MUSIC BY B.STOCKLEBEN(ADS) 3/94!" -----
; ----- ($1040 inside it is reused as scratch by sub_184B) -----

; ---------------------------------------------------------------------------
; init tail — entered from L_1870 with Y = subtune*8 + 6 (after the three
; track-pointer pairs were copied). Reads speed + master volume from the
; tune record, wipes all state, silences the SID.
; ---------------------------------------------------------------------------
L_1050:
    $1050: B9 10 1C   LDA $1c10,y      ; tune record byte 6 = SPEED   [patched operand]
    $1053: 8D 16 17   STA $1716        ; speed (tick period - 1)
    $1056: B9 11 1C   LDA $1c11,y      ; tune record byte 7 = MASTER VOL [patched]
    $1059: 8D 17 17   STA $1717        ; volume shadow (lo nibble of $D418)
    $105C: 8D 18 D4   STA $d418        ; VOL — the only init-time SID value
    $105F: A2 00      LDX #$00
    $1061: 8A         TXA
L_1062:                                ; clear $1718-$179D ($86 bytes of state)
    $1062: 9D 18 17   STA $1718,x
    $1065: E8         INX
    $1066: E0 86      CPX #$86
    $1068: D0 F8      BNE $1062        ; → L_1062
    $106A: A2 00      LDX #$00
    $106C: A9 01      LDA #$01
L_106E:                                ; voice active = 1, duration ctr = 1
    $106E: 9D 0C 10   STA $100c,x      ; (duration 1 → first tick fetches)
    $1071: 9D 3B 17   STA $173b,x
    $1074: E8         INX
    $1075: E0 03      CPX #$03
    $1077: D0 F5      BNE $106e        ; → L_106E
    $1079: A2 00      LDX #$00
    $107B: 8A         TXA
L_107C:                                ; clear SID $D400-$D417 (NOT $D418)
    $107C: 9D 00 D4   STA $d400,x
    $107F: E8         INX
    $1080: E0 18      CPX #$18
    $1082: D0 F8      BNE $107c        ; → L_107C
    $1084: 60         RTS              ; NB: $1018 ($D417 shadow) NOT cleared —
                                       ; ships with a file-image leftover!

; ---------------------------------------------------------------------------
; play body — speed counter, three voice calls, global filter regs
; ---------------------------------------------------------------------------
L_1085:
    $1085: CE 18 17   DEC $1718        ; speed counter
    $1088: 10 06      BPL $1090        ; not expired → no tick
    $108A: AD 16 17   LDA $1716
    $108D: 8D 18 17   STA $1718        ; reload → $1716==$1718 marks the tick
L_1090:
    $1090: A2 00      LDX #$00
    $1092: 8E 20 17   STX $1720        ; filter claim flag = free
    $1095: 20 B0 10   JSR $10b0        ; voice 0
    $1098: E8         INX
    $1099: 20 B0 10   JSR $10b0        ; voice 1
    $109C: E8         INX
    $109D: 20 B0 10   JSR $10b0        ; voice 2
    $10A0: AD 1C 17   LDA $171c
    $10A3: 8D 16 D4   STA $d416        ; filter cutoff hi (every frame)
    $10A6: AD 18 10   LDA $1018        ; route shadow (lo nibble)
    $10A9: 0D 23 17   ORA $1723        ; | resonance (hi nibble)
    $10AC: 8D 17 D4   STA $d417        ; RES/FILT (every frame)
    $10AF: 60         RTS

; ---------------------------------------------------------------------------
; voice_tick — decide: fetch new event vs run effects
; ---------------------------------------------------------------------------
sub_10B0:
    $10B0: BD 0C 10   LDA $100c,x      ; voice active?
    $10B3: F0 10      BEQ $10c5        ; no → effects still run (state freewheels)
    $10B5: AD 16 17   LDA $1716
    $10B8: CD 18 17   CMP $1718        ; tick frame? (counter == reload)
    $10BB: D0 08      BNE $10c5        ; no → effects
    $10BD: DE 3B 17   DEC $173b,x      ; duration counter (ticks)
    $10C0: BD 3B 17   LDA $173b,x
    $10C3: F0 03      BEQ $10c8        ; expired → fetch next event
L_10C5:
    $10C5: 4C F9 11   JMP $11f9        ; → L_11F9 frame entry (note-init/effects)

; ---------------------------------------------------------------------------
; track_fetch — read the orderlist: transpose cmds, sector select, end/loop
; ---------------------------------------------------------------------------
L_10C8:
    $10C8: BD 07 17   LDA $1707,x      ; track ptr → ZP $F8/$F9
    $10CB: 85 F8      STA $f8
    $10CD: BD 0A 17   LDA $170a,x
    $10D0: 85 F9      STA $f9
L_10D2:
    $10D2: BC 26 17   LDY $1726,x      ; track position
    $10D5: B1 F8      LDA ($f8),y
    $10D7: 10 28      BPL $1101        ; $00-$7F = sector number
    $10D9: C9 FF      CMP #$ff
    $10DB: D0 08      BNE $10e5
    $10DD: A9 00      LDA #$00         ; $FF = loop track to start
    $10DF: 9D 26 17   STA $1726,x
    $10E2: 4C D2 10   JMP $10d2        ; → L_10D2 re-read
L_10E5:
    $10E5: C9 FE      CMP #$fe
    $10E7: D0 06      BNE $10ef
    $10E9: A9 00      LDA #$00         ; $FE = end of tune: voice off
    $10EB: 9D 0C 10   STA $100c,x      ; (state freewheels; no silence write)
    $10EE: 60         RTS
L_10EF:                                ; $80-$FD = transpose command
    $10EF: 38         SEC
    $10F0: E9 A0      SBC #$a0         ; $A0-$BF → +0..+31 (carry set)
    $10F2: B0 04      BCS $10f8
    $10F4: 49 1F      EOR #$1f         ; $80-$9F → -0..-31 (two's complement
    $10F6: 69 01      ADC #$01         ;  via EOR $1F, +1; carry is clear)
L_10F8:
    $10F8: 9D 2C 17   STA $172c,x      ; transpose (signed semitones)
    $10FB: FE 26 17   INC $1726,x
    $10FE: C8         INY
    $10FF: B1 F8      LDA ($f8),y      ; next byte = the sector number
L_1101:
    $1101: A8         TAY              ; Y = sector number
    $1102: B9 7B 21   LDA $217b,y      ; sector ptr lo  [patched operand]
    $1105: 85 F8      STA $f8          ; ZP $F8/$F9 now = sector ptr
    $1107: B9 B4 21   LDA $21b4,y      ; sector ptr hi  [patched operand]
    $110A: 85 F9      STA $f9
L_110C:
    $110C: 4C C0 17   JMP $17c0        ; → L_17C0 → L_1837 sector fetch
; ----- data gap $110F-$1112 (4 bytes) -----

; ---------------------------------------------------------------------------
; sector dispatch stage 3 (from L_17DA): instrument select vs note
; ---------------------------------------------------------------------------
L_1113:
    $1113: C9 60      CMP #$60
    $1115: 90 0B      BCC $1122        ; $00-$5F = note
    $1117: 29 1F      AND #$1f         ; $60-$7B = instrument select
    $1119: 9D 15 10   STA $1015,x      ; current instrument
    $111C: FE 29 17   INC $1729,x
    $111F: 4C 0C 11   JMP $110c        ; → refetch (prefix command)
L_1122:
    $1122: 4C A2 11   JMP $11a2        ; → L_11A2 note load

; ---------------------------------------------------------------------------
; sector dispatch stage 2 (from L_17C5): rest, switch, glide
; ---------------------------------------------------------------------------
L_1125:
    $1125: C9 7E      CMP #$7e
    $1127: F0 4B      BEQ $1174        ; $7E = rest
    $1129: C9 7D      CMP #$7d
    $112B: F0 56      BEQ $1183        ; $7D = SWITCH (tie/legato toggle)
    $112D: C9 C0      CMP #$c0
    $112F: 90 66      BCC $1197        ; < $C0 → stage 4 (duration / note)
    $1131: 29 1F      AND #$1f         ; $C0-$DF glide/slide
    $1133: 48         PHA
    $1134: 29 0F      AND #$0f
    $1136: 9D 41 17   STA $1741,x      ; glide speed nibble (activates glide)
    $1139: 68         PLA
    $113A: 29 10      AND #$10         ; bit4 = mode
    $113C: D0 20      BNE $115e        ; 1 → slide current note
    $113E: C8         INY              ; mode 0: glide [noteA][noteB]
    $113F: B1 F8      LDA ($f8),y
    $1141: 18         CLC
    $1142: 7D 2C 17   ADC $172c,x      ; + transpose
    $1145: 9D 44 17   STA $1744,x      ; glide start note A
    $1148: C8         INY
    $1149: B1 F8      LDA ($f8),y
    $114B: 18         CLC
    $114C: 7D 2C 17   ADC $172c,x
    $114F: 9D 47 17   STA $1747,x      ; glide target note B
    $1152: FE 29 17   INC $1729,x      ; (2 extra bytes consumed)
    $1155: FE 29 17   INC $1729,x
    $1158: BD 44 17   LDA $1744,x
    $115B: 4C A6 11   JMP $11a6        ; → play note A (full note load)
L_115E:
    $115E: C8         INY              ; mode 1: slide [noteB]
    $115F: B1 F8      LDA ($f8),y
    $1161: 18         CLC
    $1162: 7D 2C 17   ADC $172c,x
    $1165: 9D 47 17   STA $1747,x      ; target = noteB
    $1168: BD 12 10   LDA $1012,x
    $116B: 9D 44 17   STA $1744,x      ; start = current note
    $116E: FE 29 17   INC $1729,x
    $1171: 4C 74 11   JMP $1174        ; → consume a duration slot, no retrigger
L_1174:                                ; $7E rest (also slide tail)
    $1174: BD 3E 17   LDA $173e,x      ; duration ← reload
    $1177: 9D 3B 17   STA $173b,x
    $117A: FE 29 17   INC $1729,x
L_117D:
    $117D: 20 E6 11   JSR $11e6        ; → sub_11E6 end-of-sector check ($7F)
    $1180: 4C 22 13   JMP $1322        ; → effects (no note init)
L_1183:                                ; $7D SWITCH
    $1183: BD 3E 17   LDA $173e,x      ; duration ← reload
    $1186: 9D 3B 17   STA $173b,x
    $1189: BD 0F 10   LDA $100f,x
    $118C: 49 01      EOR #$01         ; gate mask bit0 toggle ($FF↔$FE)
    $118E: 9D 0F 10   STA $100f,x
    $1191: FE 29 17   INC $1729,x
    $1194: 4C 7D 11   JMP $117d        ; → L_117D
L_1197:
    $1197: 4C DA 17   JMP $17da        ; → L_17DA stage 4 (duration / note)
; ----- data gap $119A-$11A1 (8 bytes) -----

; ---------------------------------------------------------------------------
; note load — transpose, freq lookup, duration, hard-restart prep
; ---------------------------------------------------------------------------
L_11A2:
    $11A2: 18         CLC
    $11A3: 7D 2C 17   ADC $172c,x      ; note + transpose
L_11A6:                                ; (sfx entry $163E jumps here, no transpose)
    $11A6: 9D 12 10   STA $1012,x      ; current note
    $11A9: A8         TAY
    $11AA: B9 47 16   LDA $1647,y      ; freq lo  (FIXED table)
    $11AD: 9D 2F 17   STA $172f,x      ; base freq lo
    $11B0: B9 A7 16   LDA $16a7,y      ; freq hi  (FIXED table)
    $11B3: 9D 32 17   STA $1732,x      ; base freq hi
    $11B6: BD 3E 17   LDA $173e,x      ; duration ← reload
    $11B9: 9D 3B 17   STA $173b,x
    $11BC: FE 29 17   INC $1729,x
    $11BF: BD B0 17   LDA $17b0,x      ; soft-start mode ($7C)?
    $11C2: D0 B9      BNE $117d        ; yes → skip hard restart entirely
    $11C4: A9 00      LDA #$00         ; hard-restart prep:
    $11C6: 9D 35 17   STA $1735,x      ; clear freq offset accum
    $11C9: 9D 38 17   STA $1738,x
    $11CC: 18         CLC
    $11CD: 9D 68 17   STA $1768,x      ; clear vibrato dir
    $11D0: 9D 6B 17   STA $176b,x      ; clear vibrato step ctr
    $11D3: 20 23 18   JSR $1823        ; → sub_1823 clear ramp + slide accum
    $11D6: BC 0D 17   LDY $170d,x      ; Y = SID reg offset
    $11D9: A9 08      LDA #$08
    $11DB: 20 FB 17   JSR $17fb        ; → sub_17FB: $08→ctrl (TEST), $0F→AD+SR
    $11DE: A9 FF      LDA #$ff
    $11E0: 9D 0F 10   STA $100f,x      ; gate mask = pass-through
    $11E3: 9D 4A 17   STA $174a,x      ; new-note pending (init next frame)
                                       ; falls into sub_11E6, then RTS —
                                       ; the fetch frame writes ONLY test+ADSR
; ---------------------------------------------------------------------------
; end-of-sector check — called/fallen-into after every duration-consuming
; event; a trailing $7F advances the track NOW (so the next tick reads the
; next sector without an empty slot)
; ---------------------------------------------------------------------------
sub_11E6:
    $11E6: BC 29 17   LDY $1729,x
    $11E9: B1 F8      LDA ($f8),y      ; peek next sector byte
    $11EB: C9 7F      CMP #$7f
    $11ED: F0 01      BEQ $11f0
    $11EF: 60         RTS
L_11F0:
    $11F0: A9 00      LDA #$00
    $11F2: 9D 29 17   STA $1729,x      ; sector pos = 0
    $11F5: 20 2D 18   JSR $182d        ; → sub_182D: track pos++, soft-start off
    $11F8: 60         RTS

; ---------------------------------------------------------------------------
; frame entry — pending note → note init; else → running effects
; ---------------------------------------------------------------------------
L_11F9:
    $11F9: BD 4A 17   LDA $174a,x      ; new-note pending?
    $11FC: D0 03      BNE $1201
    $11FE: 4C 22 13   JMP $1322        ; → L_1322 running effects
L_1201:                                ; ===== NOTE INIT (frame 2 of a note) =====
    $1201: 18         CLC
    $1202: A9 00      LDA #$00
    $1204: 9D 4A 17   STA $174a,x      ; clear pending
    $1207: 9D 50 17   STA $1750,x      ; clear PW accum lo
    $120A: 9D 89 17   STA $1789,x      ; (cleared, never read)
    $120D: 9D 92 17   STA $1792,x      ; clear vib step size
    $1210: 9D 95 17   STA $1795,x
    $1213: BD 15 10   LDA $1015,x      ; instrument number × 11:
    $1216: 0A         ASL a
    $1217: 0A         ASL a
    $1218: 0A         ASL a            ; n*8
    $1219: 7D 15 10   ADC $1015,x      ; +n
    $121C: 7D 15 10   ADC $1015,x      ; +n
    $121F: 7D 15 10   ADC $1015,x      ; +n = n*11
    $1222: 9D 4D 17   STA $174d,x      ; instrument offset
    $1225: A8         TAY
    $1226: B9 F0 18   LDA $18f0,y      ; instr+0 = AD  [operand FIXED $18F0]
    $1229: 48         PHA
    $122A: B9 F1 18   LDA $18f1,y      ; instr+1 = SR
    $122D: BC 0D 17   LDY $170d,x      ; Y = SID reg offset
    $1230: 20 4B 18   JSR $184b        ; → sub_184B SR write (VOL override)
    $1233: 68         PLA
    $1234: 99 05 D4   STA $d405,y      ; AD (real envelope, after $0F0F prep)
    $1237: BC 4D 17   LDY $174d,x
    $123A: B9 FA 18   LDA $18fa,y      ; instr+10 = FX flags
    $123D: 29 04      AND #$04         ; $04 no-pulse-reset?
    $123F: D0 28      BNE $1269        ; set → keep PW state
    $1241: B9 F2 18   LDA $18f2,y      ; instr+2 = PW init/bounds
    $1244: 48         PHA
    $1245: 29 0F      AND #$0f
    $1247: 9D 53 17   STA $1753,x      ; PW hi initial (lo nibble)
    $124A: 68         PLA
    $124B: 4A         LSR a
    $124C: 4A         LSR a
    $124D: 4A         LSR a
    $124E: 4A         LSR a
    $124F: 9D 56 17   STA $1756,x      ; PW bound A (hi nibble)
    $1252: 49 0F      EOR #$0f
    $1254: 9D 59 17   STA $1759,x      ; PW bound B = A EOR $0F
    $1257: B9 F6 18   LDA $18f6,y      ; instr+6
    $125A: 4A         LSR a
    $125B: 4A         LSR a
    $125C: 4A         LSR a
    $125D: 4A         LSR a
    $125E: 9D 5F 17   STA $175f,x      ; PW step base (hi nibble)
    $1261: A9 00      LDA #$00
    $1263: 9D 62 17   STA $1762,x      ; PW phase = 0
    $1266: 9D 65 17   STA $1765,x      ; PW direction = up
L_1269:
    $1269: B9 FA 18   LDA $18fa,y      ; FX flags again
    $126C: 29 20      AND #$20         ; $20 filter on?
    $126E: F0 50      BEQ $12c0        ; no → clear this voice's route bit
    $1270: AD 18 10   LDA $1018
    $1273: 1D 10 17   ORA $1710,x      ; route bit 1/2/4 into $D417 shadow
    $1276: 8D 18 10   STA $1018
    $1279: B9 FA 18   LDA $18fa,y
    $127C: 29 02      AND #$02         ; $02 no-filter-reset?
    $127E: D0 49      BNE $12c9        ; set → keep running filter
    $1280: A9 00      LDA #$00
    $1282: 8D 19 17   STA $1719        ; filter step = 0
    $1285: 8D 1A 17   STA $171a        ; step frame ctr = 0
    $1288: B9 F6 18   LDA $18f6,y      ; instr+6 lo nibble = filter def index
    $128B: 29 0F      AND #$0f
    $128D: 0A         ASL a
    $128E: 0A         ASL a
    $128F: 0A         ASL a
    $1290: 0A         ASL a            ; def# * 16
    $1291: 8D 1B 17   STA $171b        ; filter def base
    $1294: A8         TAY
    $1295: B9 77 1A   LDA $1a77,y      ; def+0  [patched operand]
    $1298: 48         PHA
    $1299: 29 F0      AND #$f0
    $129B: 8D 23 17   STA $1723        ; resonance (hi nibble) → $D417 hi
    $129E: 68         PLA
    $129F: 29 0F      AND #$0f
    $12A1: 0A         ASL a
    $12A2: 0A         ASL a
    $12A3: 0A         ASL a
    $12A4: 0A         ASL a            ; mode bits (LP/BP/HP) to hi nibble
    $12A5: 0D 17 17   ORA $1717        ; | master volume
    $12A8: 8D 18 D4   STA $d418        ; VOL+mode (only non-init $D418 write!)
    $12AB: B9 78 1A   LDA $1a78,y      ; def+1 = initial cutoff
    $12AE: 8D 1C 17   STA $171c
    $12B1: B9 79 1A   LDA $1a79,y      ; def+2 = repeat step
    $12B4: 8D 1D 17   STA $171d
    $12B7: B9 7A 1A   LDA $1a7a,y      ; def+3 = stop cutoff
    $12BA: 8D 1E 17   STA $171e
    $12BD: 4C C9 12   JMP $12c9
L_12C0:                                ; non-filter instrument:
    $12C0: AD 18 10   LDA $1018
    $12C3: 3D 13 17   AND $1713,x      ; clear this voice's route bit
    $12C6: 8D 18 10   STA $1018
L_12C9:
    $12C9: BC 4D 17   LDY $174d,x
    $12CC: B9 F7 18   LDA $18f7,y      ; instr+7 = vibrato delay/width
    $12CF: 48         PHA
    $12D0: 29 F0      AND #$f0
    $12D2: 4A         LSR a            ; hi nibble << 4 >> 1 = nibble*8
    $12D3: 9D 71 17   STA $1771,x      ; vibrato delay (frames)
    $12D6: 68         PLA
    $12D7: 29 0F      AND #$0f
    $12D9: 9D 74 17   STA $1774,x      ; vibrato width
    $12DC: B9 F8 18   LDA $18f8,y      ; instr+8 = ramp limit / slide speed
    $12DF: 9D 77 17   STA $1777,x
    $12E2: B9 F9 18   LDA $18f9,y      ; instr+9 = wave table start
    $12E5: 9D 7A 17   STA $177a,x      ; wave position
    $12E8: B9 FA 18   LDA $18fa,y      ; instr+10 = FX flags
    $12EB: 9D 7D 17   STA $177d,x      ; cached
    $12EE: BC 12 10   LDY $1012,x      ; Y = current NOTE:
    $12F1: B9 88 18   LDA $1888,y      ; per-note vibrato depth (FIXED table,
    $12F4: 18         CLC              ;  overlaps code for notes 0-5!)
    $12F5: 9D 92 17   STA $1792,x      ; vib step size lo
    $12F8: A9 02      LDA #$02
    $12FA: 9D 86 17   STA $1786,x      ; post-note guard = 2 frames
    $12FD: 20 85 18   JSR $1885        ; → sub_1885: width 0 → step size 0
    $1300: BD 7D 17   LDA $177d,x
    $1303: 29 80      AND #$80         ; $80 cymbal?
    $1305: F0 11      BEQ $1318
    $1307: BC 0D 17   LDY $170d,x      ; cymbal: freq $FFFF, gated noise,
    $130A: A9 FF      LDA #$ff         ;         skip wave/pulse this frame
    $130C: 99 00 D4   STA $d400,y      ; V1_FREQ_LO,Y
    $130F: 99 01 D4   STA $d401,y      ; V1_FREQ_HI,Y
    $1312: A9 81      LDA #$81
    $1314: 99 04 D4   STA $d404,y      ; CTRL = noise + gate
    $1317: 60         RTS
L_1318:
    $1318: 4C 91 15   JMP $1591        ; → wave step + full SID writes
; ----- data gap $131B-$1321 (7 bytes) -----

; ---------------------------------------------------------------------------
; running effects — every frame after note init
; ---------------------------------------------------------------------------
L_1322:
    $1322: BD 86 17   LDA $1786,x      ; post-note guard active?
    $1325: F0 06      BEQ $132d
    $1327: DE 86 17   DEC $1786,x      ; 2→1→0: skip gate logic 2 frames
    $132A: 4C 4E 13   JMP $134e        ; → pulse etc.
L_132D:                                ; ===== end-of-note gate logic =====
    $132D: BD 7D 17   LDA $177d,x
    $1330: 29 10      AND #$10         ; $10 holding?
    $1332: F0 0E      BEQ $1342
    $1334: BD 3B 17   LDA $173b,x      ; holding: gate off only when the
    $1337: C9 01      CMP #$01         ; duration counter is at 1 (one tick
    $1339: D0 13      BNE $134e        ; before the next event)
    $133B: A9 FE      LDA #$fe
    $133D: 20 EC 17   JSR $17ec        ; → sub_17EC: mask=$FE + AD/SR=$00
    $1340: D0 0C      BNE $134e        ; (always taken)
L_1342:
    $1342: BD 7D 17   LDA $177d,x
    $1345: 29 08      AND #$08         ; $08 no-gate-off?
    $1347: D0 05      BNE $134e        ; set → gate stays up
    $1349: A9 FE      LDA #$fe         ; default: gate mask = off from frame 5
    $134B: 9D 0F 10   STA $100f,x      ; (3 gate-on frames; tail = release)
L_134E:                                ; ===== pulse program =====
    $134E: BD 62 17   LDA $1762,x      ; phase index 0-5
    $1351: 4A         LSR a            ; /2 = which of bytes 3-5
    $1352: 18         CLC
    $1353: 7D 4D 17   ADC $174d,x
    $1356: A8         TAY
    $1357: B9 F3 18   LDA $18f3,y      ; instr+3/+4/+5 = speed nibbles
    $135A: 8D 1F 17   STA $171f
    $135D: BD 62 17   LDA $1762,x
    $1360: 29 01      AND #$01         ; odd phase → lo nibble, even → hi
    $1362: F0 0C      BEQ $1370
    $1364: AD 1F 17   LDA $171f
    $1367: 29 0F      AND #$0f
    $1369: 0A         ASL a
    $136A: 0A         ASL a
    $136B: 0A         ASL a
    $136C: 0A         ASL a
    $136D: 4C 75 13   JMP $1375
L_1370:
    $1370: AD 1F 17   LDA $171f
    $1373: 29 F0      AND #$f0
L_1375:
    $1375: 18         CLC
    $1376: 7D 5F 17   ADC $175f,x      ; + step base (instr+6 hi)
    $1379: 9D 5C 17   STA $175c,x      ; current PW step
    $137C: BD 65 17   LDA $1765,x      ; direction
    $137F: D0 1E      BNE $139f
    $1381: BD 50 17   LDA $1750,x      ; up: PW accum += step
    $1384: 18         CLC
    $1385: 7D 5C 17   ADC $175c,x
    $1388: 9D 50 17   STA $1750,x
    $138B: BD 53 17   LDA $1753,x
    $138E: 69 00      ADC #$00
    $1390: 9D 53 17   STA $1753,x
    $1393: DD 59 17   CMP $1759,x      ; hi == bound B → turn down
    $1396: D0 2D      BNE $13c5
    $1398: A9 01      LDA #$01
    $139A: 9D 65 17   STA $1765,x
    $139D: D0 1C      BNE $13bb        ; (always)
L_139F:
    $139F: BD 50 17   LDA $1750,x      ; down: PW accum -= step
    $13A2: 38         SEC
    $13A3: FD 5C 17   SBC $175c,x
    $13A6: 9D 50 17   STA $1750,x
    $13A9: BD 53 17   LDA $1753,x
    $13AC: E9 00      SBC #$00
    $13AE: 9D 53 17   STA $1753,x
    $13B1: DD 56 17   CMP $1756,x      ; hi == bound A → turn up
    $13B4: D0 0F      BNE $13c5
    $13B6: A9 00      LDA #$00
    $13B8: 9D 65 17   STA $1765,x
L_13BB:
    $13BB: BD 62 17   LDA $1762,x      ; phase advances on each direction
    $13BE: C9 05      CMP #$05         ; flip, saturating at 5 (so speed
    $13C0: F0 03      BEQ $13c5        ; nibbles run hi,lo,hi,lo,hi,lo once,
    $13C2: FE 62 17   INC $1762,x      ; then the last nibble repeats)
L_13C5:                                ; ===== filter program =====
    $13C5: BD 7D 17   LDA $177d,x
    $13C8: 29 20      AND #$20         ; filter instrument?
    $13CA: F0 50      BEQ $141c
    $13CC: AD 20 17   LDA $1720        ; filter free this frame?
    $13CF: D0 4B      BNE $141c        ; (first filter voice in X order wins)
    $13D1: E8         INX
    $13D2: 8E 20 17   STX $1720        ; claim (X+1, nonzero)
    $13D5: CA         DEX
    $13D6: AD 1C 17   LDA $171c
    $13D9: CD 1E 17   CMP $171e        ; cutoff == stop value → frozen
    $13DC: F0 3E      BEQ $141c
    $13DE: AD 1B 17   LDA $171b        ; def base + step index
    $13E1: 18         CLC
    $13E2: 6D 19 17   ADC $1719
    $13E5: A8         TAY
    $13E6: B9 7B 1A   LDA $1a7b,y      ; def+4..9 = step size  [patched]
    $13E9: 8D 21 17   STA $1721
    $13EC: B9 81 1A   LDA $1a81,y      ; def+10..15 = step duration [patched]
    $13EF: 8D 22 17   STA $1722
    $13F2: AD 1C 17   LDA $171c
    $13F5: 18         CLC
    $13F6: 6D 21 17   ADC $1721        ; cutoff += step size (signed wrap)
    $13F9: 8D 1C 17   STA $171c
    $13FC: EE 1A 17   INC $171a        ; frames in step
    $13FF: AD 1A 17   LDA $171a
    $1402: CD 22 17   CMP $1722
    $1405: D0 15      BNE $141c
    $1407: A9 00      LDA #$00         ; step done → next step
    $1409: 8D 1A 17   STA $171a
    $140C: EE 19 17   INC $1719
    $140F: AD 19 17   LDA $1719
    $1412: C9 06      CMP #$06
    $1414: D0 06      BNE $141c
    $1416: AD 1D 17   LDA $171d        ; after step 5 → repeat step (def+2)
    $1419: 8D 19 17   STA $1719
L_141C:                                ; ===== glide/slide ($Cx) =====
    $141C: BD 41 17   LDA $1741,x      ; glide speed (0 = inactive)
    $141F: F0 7E      BEQ $149f
    $1421: 0A         ASL a
    $1422: 0A         ASL a
    $1423: 0A         ASL a
    $1424: 0A         ASL a            ; speed nibble << 4 = step/frame
    $1425: 8D 1F 17   STA $171f
    $1428: BD 44 17   LDA $1744,x
    $142B: DD 47 17   CMP $1747,x      ; start >= target → glide down
    $142E: B0 2A      BCS $145a
    $1430: BC 47 17   LDY $1747,x      ; --- gliding up ---
    $1433: BD 35 17   LDA $1735,x      ; freq offset accum += step
    $1436: 18         CLC
    $1437: 6D 1F 17   ADC $171f
    $143A: 9D 35 17   STA $1735,x
    $143D: BD 38 17   LDA $1738,x
    $1440: 69 00      ADC #$00
    $1442: 9D 38 17   STA $1738,x
    $1445: BD 35 17   LDA $1735,x      ; (base + accum) hi byte
    $1448: 18         CLC
    $1449: 7D 2F 17   ADC $172f,x
    $144C: BD 38 17   LDA $1738,x
    $144F: 7D 32 17   ADC $1732,x
    $1452: D9 A7 16   CMP $16a7,y      ; == target's freq HI → arrived
    $1455: D0 45      BNE $149c        ; (HI-byte equality only!)
    $1457: 4C 81 14   JMP $1481
L_145A:
    $145A: BC 47 17   LDY $1747,x      ; --- gliding down ---
    $145D: BD 35 17   LDA $1735,x      ; accum -= step
    $1460: 38         SEC
    $1461: ED 1F 17   SBC $171f
    $1464: 9D 35 17   STA $1735,x
    $1467: BD 38 17   LDA $1738,x
    $146A: E9 00      SBC #$00
    $146C: 9D 38 17   STA $1738,x
    $146F: BD 35 17   LDA $1735,x
    $1472: 18         CLC
    $1473: 7D 2F 17   ADC $172f,x
    $1476: BD 38 17   LDA $1738,x
    $1479: 7D 32 17   ADC $1732,x
    $147C: D9 A7 16   CMP $16a7,y
    $147F: D0 1B      BNE $149c
L_1481:                                ; glide arrived:
    $1481: 98         TYA
    $1482: 9D 12 10   STA $1012,x      ; current note = target
    $1485: B9 47 16   LDA $1647,y      ; rebase freq from tables
    $1488: 9D 2F 17   STA $172f,x
    $148B: B9 A7 16   LDA $16a7,y
    $148E: 9D 32 17   STA $1732,x
    $1491: A9 00      LDA #$00
    $1493: 9D 41 17   STA $1741,x      ; glide off
    $1496: 9D 35 17   STA $1735,x      ; accum = 0
    $1499: 9D 38 17   STA $1738,x
L_149C:
    $149C: 4C 91 15   JMP $1591        ; glide active → NO vibrato this frame
L_149F:                                ; ===== vibrato delay =====
    $149F: BD 71 17   LDA $1771,x
    $14A2: F0 06      BEQ $14aa
    $14A4: DE 71 17   DEC $1771,x      ; still delaying → no vib yet
    $14A7: 4C 91 15   JMP $1591
L_14AA:                                ; ===== dual effect ($40) check =====
    $14AA: BD 7D 17   LDA $177d,x
    $14AD: 29 40      AND #$40
    $14AF: F0 6F      BEQ $1520        ; off → triangle vibrato
    $14B1: EE 19 10   INC $1019        ; GLOBAL half-rate parity (shared by
    $14B4: AD 19 10   LDA $1019        ;  all $40 voices — they interleave!)
    $14B7: 29 01      AND #$01
    $14B9: 8D 19 10   STA $1019
    $14BC: D0 03      BNE $14c1
    $14BE: 4C 91 15   JMP $1591        ; even frame → skip
L_14C1:                                ; ===== per-note slide ($40) =====
    $14C1: BC 0D 17   LDY $170d,x
    $14C4: BD 2F 17   LDA $172f,x      ; freq = base + accum - slide accum
    $14C7: 18         CLC
    $14C8: 7D 35 17   ADC $1735,x
    $14CB: 8D 24 17   STA $1724
    $14CE: BD 32 17   LDA $1732,x
    $14D1: 69 00      ADC #$00         ; NB: accum HI ($1738) NOT added here
    $14D3: 8D 25 17   STA $1725
    $14D6: AD 24 17   LDA $1724
    $14D9: 38         SEC
    $14DA: FD 98 17   SBC $1798,x
    $14DD: 99 00 D4   STA $d400,y      ; V1_FREQ_LO,Y — direct write,
    $14E0: AD 25 17   LDA $1725        ;  bypasses the common tail
    $14E3: FD 9B 17   SBC $179b,x
    $14E6: 99 01 D4   STA $d401,y      ; V1_FREQ_HI,Y
    $14E9: BD 77 17   LDA $1777,x      ; slide speed (instr+8)
    $14EC: 30 15      BMI $1503        ; bit7 → slide up
    $14EE: BD 98 17   LDA $1798,x      ; slide accum += speed (pitch falls)
    $14F1: 18         CLC
    $14F2: 7D 77 17   ADC $1777,x
    $14F5: 9D 98 17   STA $1798,x
    $14F8: BD 9B 17   LDA $179b,x
    $14FB: 69 00      ADC #$00
    $14FD: 9D 9B 17   STA $179b,x
    $1500: 4C 19 16   JMP $1619        ; → PW + ctrl writes (skip wave step)
L_1503:
    $1503: BD 77 17   LDA $1777,x      ; bit7 set: accum -= (speed & $7F)
    $1506: 29 7F      AND #$7f         ; (pitch rises)
    $1508: 8D 1A 10   STA $101a
    $150B: BD 98 17   LDA $1798,x
    $150E: 38         SEC
    $150F: ED 1A 10   SBC $101a
    $1512: 9D 98 17   STA $1798,x
    $1515: BD 9B 17   LDA $179b,x
    $1518: E9 00      SBC #$00
    $151A: 9D 9B 17   STA $179b,x
    $151D: 4C 19 16   JMP $1619
L_1520:                                ; ===== triangle vibrato =====
    $1520: BD 68 17   LDA $1768,x      ; direction
    $1523: D0 21      BNE $1546
    $1525: BD 35 17   LDA $1735,x      ; up: accum += step size
    $1528: 18         CLC
    $1529: 7D 92 17   ADC $1792,x      ; (per-note depth from $1888 table)
    $152C: 9D 35 17   STA $1735,x
    $152F: BD 38 17   LDA $1738,x
    $1532: 7D 95 17   ADC $1795,x
    $1535: 9D 38 17   STA $1738,x
    $1538: FE 6B 17   INC $176b,x
    $153B: BD 6B 17   LDA $176b,x
    $153E: DD 74 17   CMP $1774,x      ; counted to width → half-cycle done
    $1541: F0 24      BEQ $1567
    $1543: 4C 91 15   JMP $1591
L_1546:
    $1546: BD 35 17   LDA $1735,x      ; down: accum -= step size
    $1549: 38         SEC
    $154A: FD 92 17   SBC $1792,x
    $154D: 9D 35 17   STA $1735,x
    $1550: BD 38 17   LDA $1738,x
    $1553: FD 95 17   SBC $1795,x
    $1556: 9D 38 17   STA $1738,x
    $1559: FE 6B 17   INC $176b,x
    $155C: BD 6B 17   LDA $176b,x
    $155F: DD 74 17   CMP $1774,x
    $1562: F0 03      BEQ $1567
    $1564: 4C 91 15   JMP $1591
L_1567:                                ; half-cycle boundary:
    $1567: A9 00      LDA #$00
    $1569: 9D 6B 17   STA $176b,x      ; step ctr = 0
    $156C: BD 68 17   LDA $1768,x
    $156F: 49 01      EOR #$01         ; flip direction
    $1571: 9D 68 17   STA $1768,x
    $1574: BD 6E 17   LDA $176e,x      ; ramp: until ramp ctr == instr+8,
    $1577: DD 77 17   CMP $1777,x      ; the width DOUBLES each half-cycle
    $157A: F0 15      BEQ $1591        ; (vibrato swells in)
    $157C: FE 6E 17   INC $176e,x
    $157F: BD 74 17   LDA $1774,x
    $1582: 18         CLC
    $1583: 7D 74 17   ADC $1774,x      ; width += width
    $1586: 9D 74 17   STA $1774,x
    $1589: BD 95 17   LDA $1795,x      ; DEAD CODE: ADC computed, result
    $158C: 69 00      ADC #$00         ; discarded via BIT (original player
    $158E: 2C 95 17   BIT $1795        ; bug/leftover — $1795 never grows)
L_1591:                                ; ===== wave table step =====
    $1591: BD 7D 17   LDA $177d,x
    $1594: 29 01      AND #$01         ; $01 drum mode?
    $1596: D0 3D      BNE $15d5
L_1598:                                ; --- melodic: freq = note + offset ---
    $1598: BC 7A 17   LDY $177a,x      ; wave position
    $159B: B9 D7 19   LDA $19d7,y      ; CTRL byte  [patched operand]
    $159E: C9 90      CMP #$90
    $15A0: 90 13      BCC $15b5
    $15A2: 38         SEC              ; >= $90: jump back (val - $90)
    $15A3: E9 90      SBC #$90
    $15A5: 8D 1F 17   STA $171f
    $15A8: BD 7A 17   LDA $177a,x
    $15AB: 38         SEC
    $15AC: ED 1F 17   SBC $171f
    $15AF: 9D 7A 17   STA $177a,x
    $15B2: 4C 98 15   JMP $1598        ; re-read at the new position
L_15B5:
    $15B5: 9D 80 17   STA $1780,x      ; current wave ctrl
    $15B8: B9 27 1A   LDA $1a27,y      ; FREQ byte = semitone offset [patched]
    $15BB: 18         CLC
    $15BC: 7D 12 10   ADC $1012,x      ; + current note
    $15BF: 9D 83 17   STA $1783,x      ; (stored; never read back)
    $15C2: A8         TAY
    $15C3: B9 47 16   LDA $1647,y      ; freq lookup for the offset note
    $15C6: 9D 2F 17   STA $172f,x      ; REBASES the voice's base freq —
    $15C9: B9 A7 16   LDA $16a7,y      ; arpeggio steps move the base!
    $15CC: 9D 32 17   STA $1732,x
    $15CF: FE 7A 17   INC $177a,x      ; wave position++
    $15D2: 4C 03 16   JMP $1603
L_15D5:                                ; --- drum: freq hi = raw table byte ---
    $15D5: BC 7A 17   LDY $177a,x
    $15D8: B9 D7 19   LDA $19d7,y      ; CTRL byte, same jump-back logic
    $15DB: C9 90      CMP #$90
    $15DD: 90 13      BCC $15f2
    $15DF: 38         SEC
    $15E0: E9 90      SBC #$90
    $15E2: 8D 1F 17   STA $171f
    $15E5: BD 7A 17   LDA $177a,x
    $15E8: 38         SEC
    $15E9: ED 1F 17   SBC $171f
    $15EC: 9D 7A 17   STA $177a,x
    $15EF: 4C D5 15   JMP $15d5
L_15F2:
    $15F2: 9D 80 17   STA $1780,x
    $15F5: A9 00      LDA #$00
    $15F7: 9D 2F 17   STA $172f,x      ; base lo = 0
    $15FA: B9 27 1A   LDA $1a27,y      ; FREQ byte = absolute $D401 value
    $15FD: 9D 32 17   STA $1732,x      ; base hi = raw byte
    $1600: FE 7A 17   INC $177a,x
L_1603:                                ; ===== common SID write tail =====
    $1603: BC 0D 17   LDY $170d,x
    $1606: BD 2F 17   LDA $172f,x      ; freq = base + vib/glide accum
    $1609: 18         CLC
    $160A: 7D 35 17   ADC $1735,x
    $160D: 99 00 D4   STA $d400,y      ; V1_FREQ_LO,Y
    $1610: BD 32 17   LDA $1732,x
    $1613: 7D 38 17   ADC $1738,x
    $1616: 99 01 D4   STA $d401,y      ; V1_FREQ_HI,Y
L_1619:                                ; (dual-effect path joins here)
    $1619: BD 50 17   LDA $1750,x
    $161C: 99 02 D4   STA $d402,y      ; V1_PW_LO,Y
    $161F: BD 53 17   LDA $1753,x
    $1622: 99 03 D4   STA $d403,y      ; V1_PW_HI,Y
    $1625: BD 80 17   LDA $1780,x
    $1628: 3D 0F 10   AND $100f,x      ; wave ctrl AND gate mask
    $162B: 99 04 D4   STA $d404,y      ; V1_CTRL,Y
    $162E: 60         RTS

; ---------------------------------------------------------------------------
; ENTRY $1006: stop all voices (active=0, gate masks=0 → ctrl writes $00)
; ---------------------------------------------------------------------------
L_162F:
    $162F: A2 00      LDX #$00
    $1631: 8A         TXA
L_1632:
    $1632: 9D 0C 10   STA $100c,x
    $1635: 9D 0F 10   STA $100f,x
    $1638: E8         INX
    $1639: E0 03      CPX #$03
    $163B: D0 F5      BNE $1632
    $163D: 60         RTS

; ---------------------------------------------------------------------------
; ENTRY $1009: trigger a note directly (game sfx/jingle hook)
;   A = note, Y = instrument, X = voice 0-2. No transpose applied.
; ---------------------------------------------------------------------------
L_163E:
    $163E: 48         PHA
    $163F: 98         TYA
    $1640: 9D 15 10   STA $1015,x      ; instrument
    $1643: 68         PLA
    $1644: 4C A6 11   JMP $11a6        ; → note load (hard restart etc.)

; ----- $1647-$16A6: FREQ TABLE LO (96 entries, PAL) — FIXED address -----
; ----- $16A7-$1706: FREQ TABLE HI (96 entries)      — FIXED address -----
; ----- $1707-$17BF: per-voice state + constants (see VARIABLE MAP);    -----
; -----   $170D: 00 07 0E (SID offsets)  $1710: 01 02 04 (route bits)   -----
; -----   $1713: FE FD FB (complement masks)                            -----

; ---------------------------------------------------------------------------
; sector fetch + dispatch stage 1
; ---------------------------------------------------------------------------
L_17C0:
    $17C0: 4C 37 18   JMP $1837        ; → L_1837 (trampoline)
; ----- data gap $17C3-$17C4 (2 bytes) -----

L_17C5:                                ; dispatch stage 2: < $F0 arrives here
    $17C5: C9 7C      CMP #$7c
    $17C7: F0 03      BEQ $17cc        ; $7C = soft-start toggle
    $17C9: 4C 25 11   JMP $1125        ; → L_1125 stage 3
L_17CC:
    $17CC: BD B0 17   LDA $17b0,x
    $17CF: 49 01      EOR #$01         ; toggle: skip hard restart on notes
    $17D1: 9D B0 17   STA $17b0,x
    $17D4: FE 29 17   INC $1729,x
    $17D7: 4C C0 17   JMP $17c0        ; → refetch (prefix command)
L_17DA:                                ; dispatch stage 4 (from L_1197)
    $17DA: C9 80      CMP #$80
    $17DC: 90 0B      BCC $17e9        ; < $80 → instrument/note
    $17DE: 29 3F      AND #$3f         ; $80-$BF = duration (6-bit)
    $17E0: 9D 3E 17   STA $173e,x      ; duration reload
    $17E3: FE 29 17   INC $1729,x
    $17E6: 4C 0C 11   JMP $110c        ; → refetch (prefix command)
L_17E9:
    $17E9: 4C 13 11   JMP $1113        ; → L_1113 stage 5

; ---------------------------------------------------------------------------
; gate off + envelope kill (holding instruments, 1 tick before note end)
; ---------------------------------------------------------------------------
sub_17EC:
    $17EC: 9D 0F 10   STA $100f,x      ; gate mask = A ($FE)
    $17EF: BC 0D 17   LDY $170d,x
    $17F2: A9 00      LDA #$00
    $17F4: 99 05 D4   STA $d405,y      ; AD = 0
    $17F7: 99 06 D4   STA $d406,y      ; SR = 0 (hard-restart precondition)
    $17FA: 60         RTS

; ---------------------------------------------------------------------------
; hard-restart prime: ctrl = A ($08 TEST), AD = SR = $0F
; ---------------------------------------------------------------------------
sub_17FB:
    $17FB: 99 04 D4   STA $d404,y      ; TEST bit on, gate off
    $17FE: A9 0F      LDA #$0f
    $1800: 99 05 D4   STA $d405,y      ; AD = $0F
    $1803: 99 06 D4   STA $d406,y      ; SR = $0F
    $1806: 60         RTS

; ---------------------------------------------------------------------------
; tune setup (init / tune-select, A = subtune)
; ---------------------------------------------------------------------------
L_1807:
    $1807: 0A         ASL a
    $1808: 0A         ASL a
    $1809: 0A         ASL a            ; subtune * 8
    $180A: A8         TAY
    $180B: A2 00      LDX #$00
L_180D:
    $180D: B9 10 1C   LDA $1c10,y      ; tune record: 3 × (track ptr lo,hi)
    $1810: 9D 07 17   STA $1707,x      ;   [patched operand]
    $1813: B9 11 1C   LDA $1c11,y
    $1816: 9D 0A 17   STA $170a,x
    $1819: C8         INY
    $181A: C8         INY
    $181B: E8         INX
    $181C: E0 03      CPX #$03
    $181E: D0 ED      BNE $180d
    $1820: 4C 70 18   JMP $1870        ; → clear toggles, then L_1050
                                       ;   (Y = subtune*8+6 → speed/vol)

; ---------------------------------------------------------------------------
; clear vibrato ramp + dual-effect slide accum (note load)
; ---------------------------------------------------------------------------
sub_1823:
    $1823: 9D 6E 17   STA $176e,x      ; ramp ctr = 0
    $1826: 9D 98 17   STA $1798,x      ; slide accum = 0
    $1829: 9D 9B 17   STA $179b,x
    $182C: 60         RTS

; ---------------------------------------------------------------------------
; sector end ($7F): advance track, re-arm hard restart
; ---------------------------------------------------------------------------
sub_182D:
    $182D: FE 26 17   INC $1726,x      ; track position++
    $1830: 9D B0 17   STA $17b0,x      ; soft-start toggle = 0 (A is 0 here)
    $1833: 2C B3 17   BIT $17b3        ; (no-op: flags only, result unused)
    $1836: 60         RTS

; ---------------------------------------------------------------------------
; sector fetch / dispatch stage 1: the $Fx VOL prefix
; ---------------------------------------------------------------------------
L_1837:
    $1837: BC 29 17   LDY $1729,x      ; sector position
    $183A: B1 F8      LDA ($f8),y
    $183C: C9 F0      CMP #$f0
    $183E: 90 85      BCC $17c5        ; < $F0 → stage 2
    $1840: 29 0F      AND #$0f         ; $F0-$FF: VOL.x
    $1842: 9D B3 17   STA $17b3,x      ; sustain override nibble (0 = off)
    $1845: FE 29 17   INC $1729,x
    $1848: 4C 37 18   JMP $1837        ; → refetch (prefix command)

; ---------------------------------------------------------------------------
; SR write with sustain override (note init)
; ---------------------------------------------------------------------------
sub_184B:
    $184B: 8D 40 10   STA $1040        ; scratch INSIDE the copyright string!
    $184E: BD B3 17   LDA $17b3,x
    $1851: D0 07      BNE $185a
    $1853: AD 40 10   LDA $1040        ; no override → SR as-is
    $1856: 99 06 D4   STA $d406,y      ; V1_SR,Y
    $1859: 60         RTS
L_185A:
    $185A: AD 40 10   LDA $1040
    $185D: 29 0F      AND #$0f         ; keep release nibble
    $185F: 8D 40 10   STA $1040
    $1862: BD B3 17   LDA $17b3,x
    $1865: 0A         ASL a
    $1866: 0A         ASL a
    $1867: 0A         ASL a
    $1868: 0A         ASL a            ; override → sustain nibble
    $1869: 0D 40 10   ORA $1040
    $186C: 99 06 D4   STA $d406,y      ; V1_SR,Y
    $186F: 60         RTS

; ---------------------------------------------------------------------------
; init: clear the 8 toggle/override bytes $17B0-$17B7, then state wipe
; ---------------------------------------------------------------------------
L_1870:
    $1870: A2 00      LDX #$00
    $1872: 8A         TXA
L_1873:
    $1873: 9D B0 17   STA $17b0,x      ; $17B0-2 soft-start, $17B3-5 VOL ovr
    $1876: E8         INX
    $1877: E0 08      CPX #$08         ; (+2 spare)
    $1879: D0 F8      BNE $1873
    $187B: 4C 50 10   JMP $1050        ; → L_1050 (Y still = subtune*8+6)
; ----- data gap $187E-$1884 (7 bytes) -----

; ---------------------------------------------------------------------------
; vibrato width 0 → force step size 0 (note init helper)
; ---------------------------------------------------------------------------
sub_1885:
    $1885: BD 74 17   LDA $1774,x
    $1888: D0 03      BNE $188d
    $188A: 9D 92 17   STA $1792,x
L_188D:
    $188D: 60         RTS
; ----- $1888-$18E7: PER-NOTE VIBRATO DEPTH TABLE (read as $1888,note at
; -----   $12F1!). Entries for notes 0-5 are the code bytes above (D0 03 9D
; -----   92 17 60) — deliberate overlap; real data starts at note 6:
; -----   02 02 04 04 04 ... 08 ... 0C ... (depth grows with pitch so
; -----   vibrato depth tracks the freq-table slope). FIXED engine table.
; ----- $18E8-$18EF: gap (8 bytes) -----
; ----- $18F0-:      instrument records (11 bytes each) — song data; count
; -----              = (wavectrl_addr - $18F0) / 11 (21 instruments here)
; ----- then (all packer-placed, addresses from the patched operands):
; -----   wave ctrl tbl / wave freq tbl / filter defs / track data /
; -----   tune records / sector data / sector ptr lo / sector ptr hi = EOF
