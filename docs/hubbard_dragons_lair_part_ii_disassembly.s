; ============================================================================
; Rob Hubbard - Dragon's Lair Part II (1986 Software Projects)
; ANNOTATED DISASSEMBLY (auto-seeded; hand-annotated)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/H/Hubbard_Rob/Dragons_Lair_Part_II.sid
; Load:   $AF00   Init: $AF00   Play: $C015
; PSID:   10 subtunes, default subtune 1 (1-indexed; A=0 passed to init)
; Binary: $AF00-$CDFF (7936 bytes)
;
; Auto-traced 1149 reachable code bytes from init+play. Layout commentary
; below was hand-derived from static analysis (operand-based data probing,
; per-voice loop trace). The engine is a more advanced cousin of Commando:
; same per-voice instrument record / pattern indirection idea, but with
; an explicit "first-frame" state bit, end-of-song handling via a state
; flag, and an interleaved 3-voice orderlist scheme.
;
; ============================================================================
;
; HIGH-LEVEL FLOW
; ----------------
;
; init ($AF00): subtune permutation + (optional) RAM copy + first-frame setup.
;   The PSID subtune index A is remapped to an INTERNAL index via a
;   chained CMP/BNE dispatcher and the tables at $AF80/$AF88. The remap
;   table (PSID subtune number 1..10 → internal A passed to $CC17):
;       PSID    1   2   3   4   5   6   7   8   9   10
;       A       9   7   1   6   4   2   3   0   5   8
;   For PSID #1 (default) → A=9 (the long main tune).
;   For PSID #2..#9 (A=2..8 path) the init *also* runs a 256-iteration
;   copy from $A6XX/$A7XX (uninitialised RAM in PSID context = zero)
;   into $BEXX/$BFXX, with the dest low byte patched by self-modify
;   from $AF80[A-2]. This was a hook for the game-resident loader to
;   stream pattern data in; in PSID context the source is zero and
;   the copy lands on bytes that happen to be unused by the selected
;   subtune (each subtune's $AF80 entry points at a different sub-region
;   of $BE/$BF that the *other* subtunes don't touch).
;
; play ($C015): every frame.
;   1. STA #$1F → $D418 (master volume = $F, low-pass off, bit 4 set).
;   2. BIT $C505 - the global state byte:
;        bit 7 (N): MUTE (kill ctrl, eventually RTS quickly).
;        bit 6 (V): FIRST-FRAME. On true, zero per-voice state, clear ctrl,
;                  set default instrument = $1B, then drop bit 6 and bail.
;        00: normal play.
;        bit 7 set + bit 6 set: muted but first-frame pending - clears all
;                  ctrl, then leaves $C505 = $80 (mute, no re-init).
;   3. Normal path: tick $C502 (phase counter, 3-step modulo for arpeggio),
;      tick $C4EC (beat counter), loop X = 2..0 over voices.
;   4. Per-voice ($C07C..$C3F6):
;        a. Decrement $C4CE,X (note-duration). When negative, fetch next
;           pattern row at $C0A5; orderlist marker $FF = wrap (restart at
;           orderlist[0]); $FE = end-of-song (JSR $C012 → $CC50 sets $C505
;           bit 7+6). Otherwise the orderlist byte is a pattern index into
;           the $C732 (LO) / $C7B4 (HI) pointer tables.
;        b. Pattern-row decode (1, 2, 3 or 4 bytes per row - see "Pattern
;           Format" below). On NEW NOTE we look up freq via $C402,note*2
;           into $C509/$C506 (target freq cache).
;        c. Apply instrument (from $C530+8*instr first-table and $C610+8*instr
;           second-table): pulse PW, ctrl waveform, AD/SR.
;        d. Effects loop: pulse-width sweep, alt waveforms,
;           pitch-bend (portamento), arpeggio (3-step using $C522), vibrato,
;           filter-cutoff sweep, "release" alt waveform. Most effects are
;           gated by bits in $C50C (= instrument byte 7 from second table).
;        e. Final SID writes: ctrl ← $C4D4,X & $C4DD,X (AND-mask used to
;           clear gate on TIE rows), freq_hi ← $C506,X, freq_lo ← $C509,X.
;   5. After all voices: tick $C522 (arp phase, 0..2 wrap).
;
; sub_C00F: JMP $CC17  - first-frame setup (alias).
; sub_C012: JMP $CC50  - end-of-song trigger (sets $C505 bit 7+6).
;
; ============================================================================
;
; PATTERN FORMAT
; ----------------
;
; Pattern rows are 1..4 bytes. First byte (the "duration" byte) controls
; what follows via bits 7 and 6.
;
;   duration.bit5..0 = number of frames this row holds (after AND #$1F).
;   duration.bit6 (V): "tie" - keep playing previous note, do NOT load
;       a new note. Causes ctrl AND-mask = $FE on next ctrl write (clears
;       gate bit; effectively a key-off / release trigger).
;   duration.bit7 (N): a SECONDARY byte follows. The secondary byte's
;       bit 7 distinguishes the two sub-formats:
;         secondary.bit7 = 0: secondary IS a new instrument index;
;                             then a NOTE byte follows. (3 bytes total.)
;         secondary.bit7 = 1: secondary is a "command" marker; a third
;                             byte is consumed (loaded into A but its
;                             value is discarded by this engine - likely
;                             a vestigial slot for an engine variant); a
;                             NOTE byte follows. (4 bytes total.)
;   note.bit7 (raw): saved to $C50E. If set on a TIE row at $C147 ($BMI),
;       skips PW + AD/SR re-init - lets the instrument re-trigger pitch
;       only. Otherwise the AND #$7F masked value indexes into the freq
;       table via $C402,note*2 / $C403,note*2.
;
; In-pattern marker $FF: end of this pattern row sequence. The play
; advances orderlist index (INC $C4C8,X) and resets row index to 0.
;
; Pattern data lives at addresses pointed to by $C732+pat (lo) and
; $C7B4+pat (hi); the player has 128 pattern slots. Most patterns live in
; $BE/$BF for subtunes A=0..6 and in $C8/$C9/$CA/$CB for subtunes A=7..9.
;
; ============================================================================
;
; KEY ZERO-PAGE AND DATA-AREA SYMBOLS
; ---------------------------------------
;   $F8/$F9       orderlist pointer (per voice, loaded fresh per fetch).
;   $FA/$FB       pattern-data pointer (per voice).
;
;   $C000-$C002   per-voice pulse-PW counter (3 bytes, byte0=03 in binary
;                 - probably stale init; gets overwritten via $C003-relay).
;   $C003-$C005   per-voice pulse-PW max (set from instr1.byte5 hi nibble
;                 via PHA / AND #$78 / 3xLSR at $C1D6).
;   $C006-$C008   per-voice pulse direction flag (sign bit drives up/down).
;   $C009-$C00E   "JMP $CC56; JMP $CD7C; JMP ..." - dispatch trampolines
;                 to optional routines (one per "command" sub-variant).
;                 Reachable only from instrument byte 5 hi-nibble routing.
;   $C00F         JMP $CC17 (first-frame setup trampoline).
;   $C012         JMP $CC50 (end-of-song trampoline).
;
;   $C400-$C401   freq table sentinel pair (so that "previous note" lookup
;                 at $C20B / $C213 has a valid entry below note 0).
;   $C402..$C4xx  freq table: 2 bytes per semitone (LO,HI), little-endian.
;
;   $C4C4-$C4C6   D400-offset for V1,V2,V3 = $00, $07, $0E (indexed by X).
;   $C4C7         saved Y = current voice's D400-offset.
;   $C4C8,X       orderlist index (per voice).
;   $C4CB,X       row index within current pattern (per voice).
;   $C4CE,X       remaining-frames counter for current note/row.
;   $C4D1,X       saved raw duration byte (used for tie-bit replay).
;   $C4D4,X       ctrl waveform shadow (instrument waveform + altered by fx).
;   $C4D7,X       current note number (0..127, 7-bit).
;   $C4DA,X       current instrument index.
;   $C4DD,X       ctrl AND-mask. $FF normal, $FE clears gate on TIE.
;   $C4E0         scratch (raw duration byte for BIT test).
;   $C4E2         saved X across instrument-byte computation.
;   $C4E3         saved instr1.byte2 (default ctrl waveform).
;   $C4E4         pulse-shift count for portamento approximation (3-bit).
;   $C4E5         current arp note-offset (from $C536,Y at $C1C2).
;   $C4E6,X       (init 0) reserved; addressed but writes only.
;   $C4E9,X       per-voice PW-direction sub-flag (toggled via INC/DEC).
;   $C4EC         beat counter (within current "step"); reload from $C501.
;   $C4ED+A       per-subtune speed reload (A is internal subtune 0..9).
;                 Values: 01 01 01 04 01 02 01 02 01 01
;   $C4F7+A       per-subtune phase reload (A is internal subtune 0..9).
;                 Values: 04 6E 08 08 7E 03 02 01 08 03
;                 - written to $C501 and patched into the $C06A operand.
;   $C500         ?
;   $C501         beat-counter reload (= $C4ED+A after first-frame init).
;   $C502         phase counter (3..0 looping, drives arpeggio step).
;   $C503         nvoices-1 = 2 (constant; always 3 voices).
;   $C504         instr*8 saved across the per-voice block (for Y reuse).
;   $C505         GLOBAL STATE byte. bit7=mute, bit6=first-frame.
;   $C506,X       cached target FREQ HI (3 bytes).
;   $C509,X       cached target FREQ LO (3 bytes).
;   $C50C         current instrument byte 7 (effect flags) - see "Flag Bits".
;   $C50E         saved RAW note byte (preserves bit 7 for replay test).
;   $C510,X       cached PW LO (target).
;   $C513,X       cached PW HI (target).
;   $C516,X       attack-decay frame counter (alt waveform timer).
;   $C519,X       per-voice frame counter (incremented each frame).
;   $C51C,X       (init 0).
;   $C51F,X       filter cutoff accumulator.
;   $C522         master arp-phase counter (0..2 wrap, ticked at $C3F7).
;   $C523+Y       arp note-offset table (3 entries per pattern). Indexed
;                 by ($C522 + something), value added to note to produce
;                 arpeggio.
;   $C526+2*y     2-byte arp pattern source - copied into $C524/$C525.
;   $C530..$C5xx  INSTRUMENT TABLE 1, 8 bytes per instrument:
;                   +0  pulse PW LO (initial)
;                   +1  pulse PW HI (initial)
;                   +2  ctrl waveform (initial $D404)
;                   +3  AD  ($D405)
;                   +4  SR  ($D406)
;                   +5  config: bits 6..3 = pulse max,
;                               bits 2..0 = pulse-shift count.
;                               If byte5 == 0 the whole instrument-apply
;                               block is skipped (only freq write happens).
;                   +6  arp-offset value applied each frame ($C4E5).
;                   +7  effect flag byte → $C50C. See "Flag Bits".
;   $C610..$C6xx  INSTRUMENT TABLE 2, 8 bytes per instrument:
;                   +0  alt waveform (PW-sweep extreme).
;                   +1  vibrato source waveform.
;                   +2  noise-mode waveform (effect $C338+).
;                   +3  unused/reserved (read but stored only briefly).
;                   +4  release-alt-waveform.
;                   +5  pulse-mod params (lo nibble: pulse delta;
;                               hi nibble (>>4): pulse phase max).
;                               Patched into operands of CMPs at $C2B7/$C29D.
;                   +6  filter resonance / route to $D417.
;                   +7  filter cutoff delta ($D416).
;
;   $C6F0..$C6F2  current orderlist LO (3 bytes, copied from song-head).
;   $C6F3..$C6F5  current orderlist HI (3 bytes, copied from song-head).
;   $C6F6..$C725  10×6-byte song heads (one per internal subtune A=0..9):
;       (V1_LO, V2_LO, V3_LO, V1_HI, V2_HI, V3_HI).
;
;   $C732+pat     pattern LO[pat] (128 entries).
;   $C7B4+pat     pattern HI[pat] (128 entries).
;
;   $BE00..$BFFF  pattern data (subtunes A=0..6).
;   $C835..$C8FF  pattern data (subtune A=7).
;   $C903..$CDFF  pattern data + orderlists (subtunes A=8..9).
;
; ============================================================================
;
; FLAG BITS (instrument byte 7 → $C50C)
; ---------------------------------------
;   bit 0 (mask $01): "pulse-direction trigger" - if freq_hi !=0 and
;                     duration counter ($C4CE,X) !=0, and current note
;                     near top of pattern (CMP $C4CE,X with note&$1F-1),
;                     either decrement pulse-counter and force ctrl=$FE
;                     (release) or set ctrl=$80 (noise).
;   bit 1 (mask $02): "alt waveform A": if $C519,X (frame counter) bit 0
;                     is set, ctrl ← $C532,Y (instr1.byte2); else
;                     ctrl ← $C612,Y (instr2.byte2 = noise mode).
;   bit 2 (mask $04): "attack-decay counter": $C516,X counts down; while
;                     nonzero use instr2.byte0 ($C610,Y) as ctrl; when
;                     zero use $C532,Y.
;   bit 3 (mask $08): "secondary freq trigger" - on $C519,X.bit0 set, use
;                     $C4D7,X as freq index; else use $C614,Y (release
;                     alt freq). Multiplied by 2 to index freq table.
;   bit 4 (mask $10): "arpeggio" - 3-step pattern from $C522/$C523. Uses
;                     $C610,Y as an inner pattern selector.
;   bit 5 (mask $20): "filter sweep" - $C51F,X += $C617,Y; result written
;                     to $D416 (FC_HI); $C616,Y → $D417 (RES_FILT).
;   bit 6 (mask $40, BIT/V): "release alt-waveform" - when triggered
;                     (gate just dropped), use $C516,X / $C535,Y to pick
;                     waveform for release tail.
;   bit 7 (mask $80, BIT/N): unused (BIT directly tests bits 7/6 of $C50C).
;
; ============================================================================
;
; CONSEQUENCE FOR CODEGEN
; --------------------------
;
;   This is a 1986-era Hubbard engine, considerably richer than Commando
;   (1985). Key extras vs. Commando:
;     - 8-byte SECONDARY instrument table at $C610 (Commando has only one
;       8-byte table).
;     - Explicit $C505 state byte with mute + first-frame bits, rather
;       than the implicit reset-on-init style of Commando.
;     - Per-subtune phase-reload patched into a play-loop operand via
;       self-modify (the $C06A poke from $CC28). The Lean codegen will
;       need to support this self-modify or fold it into a per-subtune
;       lookup table.
;     - Pulse-width modulation runs as a per-voice counter ($C000-$C008)
;       with sign-bit-driven direction switching - distinct from Commando's
;       single pulse-direction byte.
;     - The orderlist marker semantics differ from Commando: $FE here is
;       "end of song" (sets mute), and $FF is "wrap".
;
;   For a byte-perfect rebuild, the Lean codegen should treat the song
;   data as opaque (verbatim) and rebuild only the player skeleton, OR
;   structurally model patterns + instruments + orderlists per voice.
;   Recommendation: opaque (verbatim) first to lock the md5, then
;   structural extraction on top.
;
; ============================================================================

; ======= init: =======
; A = PSID subtune index minus 1 (0..9). Remap to internal subtune index
; via the chained CMP/BNE dispatcher, then call $C00F (= $CC17 first-frame
; setup). For internal indices 2..8, an additional self-modifying RAM
; copy runs ($A6/$A7 → $BE/$BF, dest patched from $AF80[A-2]).
init:
    $AF00: C9 00      CMP #$00          ; PSID #1 (A=0)?
    $AF02: D0 05      BNE $af09         ; no, try next
L_AF04:
    ; PSID #1 entry-point (and BCC/BCS fallthroughs for out-of-range).
    $AF04: A9 09      LDA #$09          ; internal A = 9 (main tune)
    $AF06: 4C 0F C0   JMP $c00f         ; → CC17
L_AF09:
    $AF09: C9 09      CMP #$09          ; PSID #10 (A=9)?
    $AF0B: D0 05      BNE $af12
    $AF0D: A9 08      LDA #$08          ; internal A = 8
    $AF0F: 4C 0F C0   JMP $c00f         ; → CC17
L_AF12:
    $AF12: C9 01      CMP #$01          ; PSID #2 (A=1)?
    $AF14: D0 05      BNE $af1b
    $AF16: A9 07      LDA #$07          ; internal A = 7
    $AF18: 4C 0F C0   JMP $c00f         ; → CC17
L_AF1B:
    ; A is 2..8. Validate range, then look up internal index + dest patch.
    $AF1B: C9 02      CMP #$02          ; A < 2 → fallback to PSID #1 entry
    $AF1D: 90 E5      BCC $af04
    $AF1F: C9 09      CMP #$09          ; A >= 9 → fallback to PSID #1 entry
    $AF21: B0 E1      BCS $af04
    $AF23: 38         SEC               ; A in [2..8]: X = A - 2 in [0..6]
    $AF24: E9 02      SBC #$02
    $AF26: AA         TAX
    $AF27: BD 80 AF   LDA $af80,x       ; dest low byte (B0,B2,B4,B6,B8,BA,BC)
    $AF2A: 8D 3D AF   STA $af3d         ; SELF-MODIFY: STA dst,X target low
    $AF2D: 18         CLC
    $AF2E: 69 01      ADC #$01
    $AF30: 8D 43 AF   STA $af43         ; SELF-MODIFY: STA dst,X target low (+1)
    $AF33: BD 88 AF   LDA $af88,x       ; internal A index for this subtune
    $AF36: 20 0F C0   JSR $c00f         ; → CC17 (first-frame setup)
    $AF39: A2 00      LDX #$00          ; 256-byte copy:
L_AF3B:
    $AF3B: BD 00 A6   LDA $a600,x       ;   src1 = $A6XX (uninit RAM in PSID = 0)
    $AF3E: 9D 00 BE   STA $be00,x       ;   dst1 = $BE??,X  (?? patched at $AF3D)
    $AF41: BD 00 A7   LDA $a700,x       ;   src2 = $A7XX (uninit RAM = 0)
    $AF44: 9D 00 BF   STA $bf00,x       ;   dst2 = $BF??,X  (?? patched at $AF43)
    $AF47: E8         INX
    $AF48: D0 F1      BNE $af3b
    $AF4A: 60         RTS

; ----- data $AF4B-$AF7F (53 bytes) -----
; Unused / zero-filled (binary has $00s here).

; ----- data $AF80-$AF8E (15 bytes) -----
; $AF80: dest-low-byte table for the init copy, indexed by (A-2).
;   $AF80: B0 B2 B4 B6 B8 BA BC
; $AF88: internal-A remap for PSID subtunes 2..8 (A=2 → 01, A=3 → 06, ...).
;   $AF88: 01 06 04 02 03 00 05
;   (Together with the early CMP branches, the full remap is:
;       PSID#1→A=9  PSID#2→A=7  PSID#3→A=1  PSID#4→A=6  PSID#5→A=4
;       PSID#6→A=2  PSID#7→A=3  PSID#8→A=0  PSID#9→A=5  PSID#10→A=8.)

; ----- data $AF8F-$BFFF (4209 bytes) -----
; Pattern data + uninitialised buffers used by subtunes A=0..6.
; The init's RAM-copy loop targets a 256-byte slice of $BEXX-$BFXX based
; on the subtune (dest LO from $AF80). For PSID-only playback this is
; effectively zero-fill of unused sub-regions.

; ----- code $C000-$C00E (15 bytes) -----
; $C000-$C002: per-voice pulse-counter scratch (in-binary init values
;   $03 $03 $03 - the per-voice "pulse-max" min reset).
; $C003-$C005: per-voice pulse-max ($04 $04 $04 - overwritten at runtime
;   from instr1.byte5 hi nibble).
; $C006-$C008: per-voice pulse-direction byte ($FF $FF $00 - signed; sign
;   bit drives up/down sweep).
; $C009-$C00E: dispatch trampolines (3 × "JMP $abcd") used by the engine's
;   command-byte routing. Not reachable from PSID-driven play in this
;   subtune mix.
sub_C00F:
    $C00F: 4C 17 CC   JMP $cc17         ; → CC17 (first-frame setup)
sub_C012:
    $C012: 4C 50 CC   JMP $cc50         ; → CC50 (end-of-song)

; ======= play: =======
; Called every frame. Routes by $C505 state, then runs per-voice loop.
play:
    ; Master volume / filter: bit 4 = high-pass disable (volume only $F).
    $C015: A9 1F      LDA #$1f
    $C017: 8D 18 D4   STA $d418      ;VOL
    ; State byte $C505:
    ;   bit 7 (BMI) = MUTE (silenced - just decay).
    ;   bit 6 (BVC=false → set) = FIRST-FRAME (clear voices and bail).
    ;   00 = normal play.
    $C01A: 2C 05 C5   BIT $c505
    $C01D: 30 2A      BMI $c049         ; bit 7 set → mute path
    $C01F: 50 40      BVC $c061         ; bit 6 clear → normal play
    ; FIRST-FRAME path: zero per-voice state and clear $D404/$D406.
    $C021: AE 03 C5   LDX $c503         ; X = nvoices-1 = 2
L_C024:
    $C024: A9 00      LDA #$00
    $C026: BC C4 C4   LDY $c4c4,x       ; Y = D400 offset for voice X
    $C029: 99 04 D4   STA $d404,y    ;V1_CTRL,Y    ; ctrl = 0 (silence)
    $C02C: 9D C8 C4   STA $c4c8,x       ; orderlist index = 0
    $C02F: 9D CB C4   STA $c4cb,x       ; row index = 0
    $C032: 9D CE C4   STA $c4ce,x       ; remaining frames = 0
    $C035: 9D D4 C4   STA $c4d4,x       ; ctrl shadow = 0
    $C038: 99 06 D4   STA $d406,y    ;V1_SR,Y      ; SR = 0
    $C03B: A9 1B      LDA #$1b
    $C03D: 9D DA C4   STA $c4da,x       ; default instrument = $1B
    $C040: CA         DEX
    $C041: 10 E1      BPL $c024         ; loop X=2,1,0
    $C043: 8D 05 C5   STA $c505         ; $C505 = $1B (clear bit 7+6)
    $C046: 4C F7 C3   JMP $c3f7         ; → cleanup (arp tick + RTS)
L_C049:
    ; MUTE path. If FIRST-FRAME bit also set ($C505 = $C0 - posted by
    ; sub_C012 / $CC50), clear all CTRL and downgrade to plain $80 (mute).
    $C049: 50 13      BVC $c05e         ; bit 6 clear → already-mute → RTS
    $C04B: A9 00      LDA #$00
    $C04D: AE 03 C5   LDX $c503
L_C050:
    $C050: BC C4 C4   LDY $c4c4,x
    $C053: 99 04 D4   STA $d404,y    ;V1_CTRL,Y    ; CTRL = 0
    $C056: CA         DEX
    $C057: 10 F7      BPL $c050
    $C059: A9 80      LDA #$80
    $C05B: 8D 05 C5   STA $c505         ; $C505 = $80 (mute only)
L_C05E:
    $C05E: 4C F7 C3   JMP $c3f7         ; → cleanup
L_C061:
    ; ======= normal-play entry =======
    ; X = nvoices-1 = 2 → loop will process V3, V2, V1 in that order.
    $C061: AE 03 C5   LDX $c503
    ; Phase counter $C502: 3-step modulo. When negative, reload from the
    ; SELF-MODIFIED operand at $C06A (poked by $CC28 = $C4F7+A for the
    ; selected subtune). Phase 0 means "advance pattern row this frame".
    $C064: CE 02 C5   DEC $c502
    $C067: 10 08      BPL $c071         ; not yet wrapped
    $C069: A9 03      LDA #$03          ; operand at $C06A: patched per-subtune
    $C06B: 8D 02 C5   STA $c502
    $C06E: 4C 7C C0   JMP $c07c         ; (skip beat-counter tick)
L_C071:
    ; Beat counter $C4EC: ticks while phase>0, reloads from $C501 (which
    ; was set to $C4ED+A by $CC1F).
    $C071: CE EC C4   DEC $c4ec
    $C074: 10 06      BPL $c07c
    $C076: AD 01 C5   LDA $c501
    $C079: 8D EC C4   STA $c4ec
L_C07C:
    ; --- per-voice block (entered with X = current voice 2/1/0) ---
    $C07C: BD C4 C4   LDA $c4c4,x       ; A = D400 offset (0/7/$E)
    $C07F: 8D C7 C4   STA $c4c7         ; save D400 base for this voice
    $C082: A8         TAY               ; Y = D400 offset
    $C083: AD 02 C5   LDA $c502
    $C086: F0 1A      BEQ $c0a2         ; phase==0 → skip note-load (fx only)
    $C088: AD EC C4   LDA $c4ec
    $C08B: CD 01 C5   CMP $c501
    $C08E: D0 12      BNE $c0a2         ; beat tick not at top → fx only
    ; "On beat" frame: maybe fetch next pattern row.
    $C090: BD F0 C6   LDA $c6f0,x       ; orderlist LO for voice X
    $C093: 85 F8      STA $f8
    $C095: BD F3 C6   LDA $c6f3,x       ; orderlist HI for voice X
    $C098: 85 F9      STA $f9
    $C09A: DE CE C4   DEC $c4ce,x       ; remaining-frames --
    $C09D: 30 06      BMI $c0a5         ; underflowed → load next row
    $C09F: 4C 9E C1   JMP $c19e         ; still in row → continue with fx
L_C0A2:
    $C0A2: 4C B2 C1   JMP $c1b2         ; → fx-only entry
L_C0A5:
    ; ===== Fetch next pattern row from orderlist =====
    $C0A5: BC C8 C4   LDY $c4c8,x       ; Y = orderlist index
    $C0A8: B1 F8      LDA ($f8),y       ; orderlist[Y]
    $C0AA: C9 FF      CMP #$ff
    $C0AC: F0 0A      BEQ $c0b8         ; $FF → wrap (restart orderlist+pattern)
    $C0AE: C9 FE      CMP #$fe
    $C0B0: D0 14      BNE $c0c6         ; not $FE → it's a pattern index
    $C0B2: 20 12 C0   JSR $c012         ; $FE → end-of-song (set $C505=$C0)
    $C0B5: 4C F7 C3   JMP $c3f7         ; → cleanup
L_C0B8:
    ; Orderlist wrap: clear remaining-frames + indices then re-enter.
    $C0B8: A9 00      LDA #$00
    $C0BA: 9D CE C4   STA $c4ce,x
    $C0BD: 9D C8 C4   STA $c4c8,x       ; orderlist index = 0
    $C0C0: 9D CB C4   STA $c4cb,x       ; row index = 0
    $C0C3: 4C A5 C0   JMP $c0a5         ; re-fetch orderlist[0]
L_C0C6:
    ; A = pattern index (0..$FD). Resolve pattern data pointer.
    $C0C6: A8         TAY
    $C0C7: B9 32 C7   LDA $c732,y       ; pattern LO[Y]
    $C0CA: 85 FA      STA $fa
    $C0CC: B9 B4 C7   LDA $c7b4,y       ; pattern HI[Y]
    $C0CF: 85 FB      STA $fb
    $C0D1: A9 00      LDA #$00
    $C0D3: 9D 19 C5   STA $c519,x       ; per-voice frame counter = 0
    $C0D6: 9D 1C C5   STA $c51c,x       ; reserved scratch = 0
    $C0D9: 9D 1F C5   STA $c51f,x       ; filter cutoff accumulator = 0
    $C0DC: BC CB C4   LDY $c4cb,x       ; Y = row index within pattern
    $C0DF: A9 FF      LDA #$ff
    $C0E1: 9D DD C4   STA $c4dd,x       ; ctrl AND-mask = $FF (full gate)
    ; --- duration byte ---
    $C0E4: B1 FA      LDA ($fa),y
    $C0E6: 9D D1 C4   STA $c4d1,x       ; save (for TIE replay)
    $C0E9: 8D E0 C4   STA $c4e0         ; scratch
    $C0EC: 29 1F      AND #$1f
    $C0EE: 9D CE C4   STA $c4ce,x       ; remaining-frames = duration low 5 bits
    $C0F1: 2C E0 C4   BIT $c4e0         ; test bits 7,6 of raw duration
    $C0F4: 70 38      BVS $c12e         ; bit 6 (V) set → TIE (no new note)
    $C0F6: FE CB C4   INC $c4cb,x       ; advance row past duration
    $C0F9: AD E0 C4   LDA $c4e0
    $C0FC: 10 14      BPL $c112         ; bit 7 clear → 2-byte row (just note)
    ; bit 7 set → 3- or 4-byte row.
    $C0FE: C8         INY
    $C0FF: B1 FA      LDA ($fa),y       ; secondary byte
    $C101: 10 09      BPL $c10c         ; bit 7 clear → it's an instrument index
    ; bit 7 of secondary set → "command" sub-format (4 bytes). The next
    ; byte is consumed but its value is discarded by this engine (likely
    ; a vestigial waveform-override slot left from an earlier engine
    ; variant - the LDA value is never stored before being overwritten
    ; at $C113).
    $C103: C8         INY
    $C104: B1 FA      LDA ($fa),y       ; load tertiary byte (DISCARDED)
    $C106: FE CB C4   INC $c4cb,x       ; row advance for secondary
    $C109: 4C 0F C1   JMP $c10f         ; → row advance for tertiary + note read
L_C10C:
    ; "Instrument-change" sub-format. A = new instrument index.
    $C10C: 9D DA C4   STA $c4da,x
L_C10F:
    $C10F: FE CB C4   INC $c4cb,x       ; row advance for secondary/tertiary
L_C112:
    ; --- NOTE byte ---
    $C112: C8         INY
    $C113: B1 FA      LDA ($fa),y
    $C115: 8D 0E C5   STA $c50e         ; save raw (bit 7 used at $C147)
    $C118: 29 7F      AND #$7f
    $C11A: 9D D7 C4   STA $c4d7,x       ; current note number (7-bit)
    $C11D: 0A         ASL a             ; *2 for 16-bit table stride
    $C11E: A8         TAY
    $C11F: B9 02 C4   LDA $c402,y       ; freq LO[note]
    $C122: 9D 09 C5   STA $c509,x       ; cache target freq LO
    $C125: B9 03 C4   LDA $c403,y       ; freq HI[note]
    $C128: 9D 06 C5   STA $c506,x       ; cache target freq HI
    $C12B: 4C 31 C1   JMP $c131         ; → instrument apply
L_C12E:
    ; TIE row (duration.bit6 set): clear gate on next ctrl write.
    $C12E: DE DD C4   DEC $c4dd,x       ; AND-mask: $FF → $FE
L_C131:
    ; ===== Apply instrument (from both 8-byte instr tables) =====
    $C131: AC C7 C4   LDY $c4c7         ; Y = D400 offset for voice
    $C134: BD DA C4   LDA $c4da,x       ; A = instrument index
    $C137: 8E E2 C4   STX $c4e2         ; save voice X (X about to be clobbered)
    $C13A: 0A         ASL a
    $C13B: 0A         ASL a
    $C13C: 0A         ASL a             ; A = instrument * 8
    $C13D: AA         TAX
    $C13E: BD 32 C5   LDA $c532,x       ; instr1.byte2 (default ctrl waveform)
    $C141: 8D E3 C4   STA $c4e3         ; save - used at $C17E final ctrl-shadow
    $C144: AD 0E C5   LDA $c50e         ; raw note byte
    $C147: 30 35      BMI $c17e         ; bit 7 of NOTE set → skip PW + AD/SR
    ; --- Pulse-width + AD + SR from instr1 ---
    $C149: BD 30 C5   LDA $c530,x       ; instr1.byte0 = PW LO
    $C14C: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $C14F: 48         PHA
    $C150: BD 31 C5   LDA $c531,x       ; instr1.byte1 = PW HI
    $C153: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $C156: 48         PHA
    $C157: BD 13 C6   LDA $c613,x       ; instr2.byte3 (reserved/unused)
    $C15A: 48         PHA
    $C15B: BD 33 C5   LDA $c533,x       ; instr1.byte3 = AD
    $C15E: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $C161: BD 34 C5   LDA $c534,x       ; instr1.byte4 = SR
    $C164: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $C167: AE E2 C4   LDX $c4e2         ; restore voice X
    $C16A: A9 00      LDA #$00
    $C16C: 9D E9 C4   STA $c4e9,x       ; reset PW-direction flag
    $C16F: 9D E6 C4   STA $c4e6,x       ; reset $C4E6,X
    $C172: 68         PLA
    $C173: 9D 16 C5   STA $c516,x       ; cache instr2.byte3 → $C516,X
    $C176: 68         PLA
    $C177: 9D 13 C5   STA $c513,x       ; cache PW HI target
    $C17A: 68         PLA
    $C17B: 9D 10 C5   STA $c510,x       ; cache PW LO target
L_C17E:
    ; ===== Final ctrl-shadow write (initial waveform) =====
    $C17E: AD E3 C4   LDA $c4e3         ; saved instr1.byte2
    $C181: AE E2 C4   LDX $c4e2         ; X = voice index (in case TIE skipped above)
    $C184: 9D D4 C4   STA $c4d4,x       ; ctrl shadow = waveform
    $C187: FE CB C4   INC $c4cb,x       ; advance row past note
    $C18A: BC CB C4   LDY $c4cb,x
    $C18D: B1 FA      LDA ($fa),y       ; peek next row byte
    $C18F: C9 FF      CMP #$ff
    $C191: D0 08      BNE $c19b         ; not $FF: stay in this pattern
    ; In-pattern $FF marker → end-of-pattern. Reset row + advance orderlist.
    $C193: A9 00      LDA #$00
    $C195: 9D CB C4   STA $c4cb,x
    $C198: FE C8 C4   INC $c4c8,x
L_C19B:
    $C19B: 4C D6 C3   JMP $c3d6         ; → SID-write block (apply this frame)
L_C19E:
    ; "Mid-note" fx tail: triggered when note-load was skipped. Test if
    ; the active note's duration is exhausted (bit5 of $C4D1 set + counter
    ; reached 0) to fire a release.
    $C19E: AC C7 C4   LDY $c4c7
    $C1A1: BD D1 C4   LDA $c4d1,x       ; saved duration byte
    $C1A4: 29 20      AND #$20
    $C1A6: D0 0A      BNE $c1b2         ; bit 5 set → skip release
    $C1A8: BD CE C4   LDA $c4ce,x
    $C1AB: D0 05      BNE $c1b2         ; counter !=0 → not yet release
    $C1AD: A9 FE      LDA #$fe
    $C1AF: 9D DD C4   STA $c4dd,x       ; AND-mask = $FE (clear gate now)
L_C1B2:
    ; ===== Effects block (runs every frame, even when no new note) =====
    ; Y = instr*8 from $C4DA,X (current instrument).
    $C1B2: BD DA C4   LDA $c4da,x
    $C1B5: 0A         ASL a
    $C1B6: 0A         ASL a
    $C1B7: 0A         ASL a
    $C1B8: A8         TAY
    $C1B9: 8C 04 C5   STY $c504         ; save instr*8 for reuse
    $C1BC: B9 37 C5   LDA $c537,y       ; instr1.byte7 = effect flag bits
    $C1BF: 8D 0C C5   STA $c50c
    $C1C2: B9 36 C5   LDA $c536,y       ; instr1.byte6 = arp note-offset
    $C1C5: 8D E5 C4   STA $c4e5
    $C1C8: B9 35 C5   LDA $c535,y       ; instr1.byte5 = pulse-mod config
    $C1CB: D0 03      BNE $c1d0
    $C1CD: 4C 6E C2   JMP $c26e         ; byte5==0: skip pulse-mod block
L_C1D0:
    ; Decode pulse-mod config: bits 6..3 = pulse max, bits 2..0 = shift.
    $C1D0: 48         PHA
    $C1D1: 29 78      AND #$78
    $C1D3: 4A         LSR a
    $C1D4: 4A         LSR a
    $C1D5: 4A         LSR a
    $C1D6: 9D 03 C0   STA $c003,x       ; per-voice pulse max
    $C1D9: 68         PLA
    $C1DA: 29 07      AND #$07
    $C1DC: 8D E4 C4   STA $c4e4         ; pulse shift count
    ; Pulse direction + counter advance.
    $C1DF: BD 06 C0   LDA $c006,x       ; pulse direction flag (sign)
    $C1E2: 10 0A      BPL $c1ee
    ; negative direction: decrement, flip sign on zero.
    $C1E4: DE 00 C0   DEC $c000,x
    $C1E7: D0 19      BNE $c202
    $C1E9: FE 06 C0   INC $c006,x       ; flip direction (toward positive)
    $C1EC: 10 14      BPL $c202
L_C1EE:
    ; positive direction: increment counter; cap at pulse-max.
    $C1EE: FE 00 C0   INC $c000,x
    $C1F1: BD 03 C0   LDA $c003,x
    $C1F4: DD 00 C0   CMP $c000,x
    $C1F7: B0 09      BCS $c202         ; counter <= max → keep
    $C1F9: 9D 00 C0   STA $c000,x       ; clamp counter = max
    $C1FC: DE 06 C0   DEC $c006,x       ; flip direction (toward negative)
    $C1FF: DE 00 C0   DEC $c000,x       ; back off counter by 1
L_C202:
    ; Build freq diff between adjacent semitones for portamento approx.
    ; ($C402,Y - $C400,Y) → ($F8/$F9), shifted right by $C4E4 bits.
    $C202: BD D7 C4   LDA $c4d7,x       ; current note
    $C205: 0A         ASL a
    $C206: A8         TAY
    $C207: 38         SEC
    $C208: B9 02 C4   LDA $c402,y       ; freq LO[note]
    $C20B: F9 00 C4   SBC $c400,y       ; - freq LO[note-1] (sentinel makes -1 safe)
    $C20E: 85 F9      STA $f9
    $C210: B9 03 C4   LDA $c403,y       ; freq HI[note]
    $C213: F9 01 C4   SBC $c401,y       ; - freq HI[note-1]
L_C216:
    $C216: CE E4 C4   DEC $c4e4
    $C219: 30 06      BMI $c221
    $C21B: 4A         LSR a             ; shift hi
    $C21C: 66 F9      ROR $f9           ; shift lo
    $C21E: 4C 16 C2   JMP $c216
L_C221:
    ; Save shifted diff to $F8/$F9; load base freq into $FA/$FB.
    $C221: 85 F8      STA $f8
    $C223: B9 02 C4   LDA $c402,y
    $C226: 85 FA      STA $fa
    $C228: B9 03 C4   LDA $c403,y
    $C22B: 85 FB      STA $fb
    ; Subtract pulse-counter * diff: y = pulse_counter / 2.
    $C22D: BD 03 C0   LDA $c003,x       ; pulse-max
    $C230: 4A         LSR a
    $C231: A8         TAY
L_C232:
    $C232: 88         DEY
    $C233: 30 10      BMI $c245
    $C235: 38         SEC
    $C236: A5 FA      LDA $fa
    $C238: E5 F9      SBC $f9
    $C23A: 85 FA      STA $fa
    $C23C: A5 FB      LDA $fb
    $C23E: E5 F8      SBC $f8
    $C240: 85 FB      STA $fb
    $C242: 4C 32 C2   JMP $c232
L_C245:
    ; Add pulse-counter * diff back, scaled by current $C000,X.
    $C245: BD D1 C4   LDA $c4d1,x       ; saved duration byte
    $C248: 29 1F      AND #$1f
    $C24A: C9 03      CMP #$03
    $C24C: 90 20      BCC $c26e         ; duration low5 < 3 → skip add
    $C24E: BC 00 C0   LDY $c000,x       ; Y = pulse counter
L_C251:
    $C251: 88         DEY
    $C252: 30 10      BMI $c264
    $C254: 18         CLC
    $C255: A5 FA      LDA $fa
    $C257: 65 F9      ADC $f9
    $C259: 85 FA      STA $fa
    $C25B: A5 FB      LDA $fb
    $C25D: 65 F8      ADC $f8
    $C25F: 85 FB      STA $fb
    $C261: 4C 51 C2   JMP $c251
L_C264:
    ; Write modulated freq back to caches.
    $C264: A5 FA      LDA $fa
    $C266: 9D 09 C5   STA $c509,x       ; freq LO ← modulated
    $C269: A5 FB      LDA $fb
    $C26B: 9D 06 C5   STA $c506,x       ; freq HI ← modulated
L_C26E:
    ; ===== Per-frame pulse-width sweep =====
    ; If $C4E5 (arp note-offset) == 0, skip the entire PW block.
    $C26E: AD E5 C4   LDA $c4e5
    $C271: F0 5C      BEQ $c2cf
    $C273: AC 04 C5   LDY $c504         ; Y = instr*8
    $C276: B9 15 C6   LDA $c615,y       ; instr2.byte5 lo nibble = pulse delta
    $C279: 29 0F      AND #$0f
    $C27B: 8D B8 C2   STA $c2b8         ; SELF-MODIFY operand at $C2B8
    $C27E: B9 15 C6   LDA $c615,y       ; instr2.byte5 hi nibble = pulse max
    $C281: 4A         LSR a
    $C282: 4A         LSR a
    $C283: 4A         LSR a
    $C284: 4A         LSR a
    $C285: 8D 9E C2   STA $c29e         ; SELF-MODIFY operand at $C29E
    $C288: BD E9 C4   LDA $c4e9,x
    $C28B: D0 1A      BNE $c2a7         ; direction bit set → reverse sweep
    ; --- forward sweep ---
    $C28D: AD E5 C4   LDA $c4e5
    $C290: 18         CLC
    $C291: 7D 10 C5   ADC $c510,x       ; PW LO target += arp offset
    $C294: 48         PHA
    $C295: BD 13 C5   LDA $c513,x
    $C298: 69 00      ADC #$00
    $C29A: 29 0F      AND #$0f
    $C29C: 48         PHA
    $C29D: C9 0F      CMP #$0f          ; operand patched by $C285
    $C29F: D0 1D      BNE $c2be
    $C2A1: FE E9 C4   INC $c4e9,x       ; reached max → flip to reverse
    $C2A4: 4C BE C2   JMP $c2be
L_C2A7:
    ; --- reverse sweep ---
    $C2A7: 38         SEC
    $C2A8: BD 10 C5   LDA $c510,x
    $C2AB: ED E5 C4   SBC $c4e5
    $C2AE: 48         PHA
    $C2AF: BD 13 C5   LDA $c513,x
    $C2B2: E9 00      SBC #$00
    $C2B4: 29 0F      AND #$0f
    $C2B6: 48         PHA
    $C2B7: C9 0D      CMP #$0d          ; operand patched by $C27B
    $C2B9: D0 03      BNE $c2be
    $C2BB: DE E9 C4   DEC $c4e9,x
L_C2BE:
    ; Write new PW back.
    $C2BE: AC C7 C4   LDY $c4c7
    $C2C1: 68         PLA
    $C2C2: 9D 13 C5   STA $c513,x       ; PW HI cache
    $C2C5: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $C2C8: 68         PLA
    $C2C9: 9D 10 C5   STA $c510,x       ; PW LO cache
    $C2CC: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
L_C2CF:
    ; ===== Flag-bit 0: pulse-direction trigger =====
    $C2CF: EA         NOP
    $C2D0: AC 04 C5   LDY $c504
    $C2D3: AD 0C C5   LDA $c50c
    $C2D6: 29 01      AND #$01
    $C2D8: F0 26      BEQ $c300
    $C2DA: BD 06 C5   LDA $c506,x       ; freq HI nonzero?
    $C2DD: F0 21      BEQ $c300
    $C2DF: BD CE C4   LDA $c4ce,x       ; remaining-frames nonzero?
    $C2E2: F0 1C      BEQ $c300
    $C2E4: BD D1 C4   LDA $c4d1,x       ; saved duration
    $C2E7: 29 1F      AND #$1f
    $C2E9: 38         SEC
    $C2EA: E9 01      SBC #$01
    $C2EC: DD CE C4   CMP $c4ce,x
    $C2EF: 90 0A      BCC $c2fb
    $C2F1: DE 06 C5   DEC $c506,x       ; near top of note: drop freq HI
    $C2F4: A9 FE      LDA #$fe
    $C2F6: 9D DD C4   STA $c4dd,x       ; AND-mask = $FE (gate clear)
    $C2F9: D0 05      BNE $c300
L_C2FB:
    $C2FB: A9 80      LDA #$80          ; near end: ctrl ← noise wave
    $C2FD: 9D D4 C4   STA $c4d4,x
L_C300:
    ; ===== Flag-bit 1: alt waveform A =====
    $C300: AD 0C C5   LDA $c50c
    $C303: 29 02      AND #$02
    $C305: F0 16      BEQ $c31d
    $C307: AC 04 C5   LDY $c504
    $C30A: BD 19 C5   LDA $c519,x
    $C30D: 29 01      AND #$01
    $C30F: F0 06      BEQ $c317
    $C311: B9 32 C5   LDA $c532,y       ; default waveform (instr1.byte2)
    $C314: 4C 1A C3   JMP $c31a
L_C317:
    $C317: B9 12 C6   LDA $c612,y       ; alt waveform (instr2.byte2)
L_C31A:
    $C31A: 9D D4 C4   STA $c4d4,x
L_C31D:
    ; ===== Flag-bit 2: attack-decay counter (alt waveform B) =====
    $C31D: AD 0C C5   LDA $c50c
    $C320: 29 04      AND #$04
    $C322: F0 14      BEQ $c338
    $C324: BD 16 C5   LDA $c516,x
    $C327: F0 09      BEQ $c332
    $C329: DE 16 C5   DEC $c516,x
    $C32C: B9 11 C6   LDA $c611,y       ; instr2.byte1
    $C32F: 4C 35 C3   JMP $c335
L_C332:
    $C332: B9 32 C5   LDA $c532,y       ; default waveform
L_C335:
    $C335: 9D D4 C4   STA $c4d4,x
L_C338:
    ; ===== Flag-bit 3: secondary freq trigger =====
    $C338: AD 0C C5   LDA $c50c
    $C33B: 29 08      AND #$08
    $C33D: F0 21      BEQ $c360
    $C33F: BD 19 C5   LDA $c519,x
    $C342: 29 01      AND #$01
    $C344: F0 06      BEQ $c34c
    $C346: BD D7 C4   LDA $c4d7,x       ; current note
    $C349: 4C 4F C3   JMP $c34f
L_C34C:
    $C34C: B9 14 C6   LDA $c614,y       ; instr2.byte4 = release alt freq
L_C34F:
    $C34F: 0A         ASL a
    $C350: A8         TAY
    $C351: B9 02 C4   LDA $c402,y
    $C354: 9D 09 C5   STA $c509,x
    $C357: B9 03 C4   LDA $c403,y
    $C35A: 9D 06 C5   STA $c506,x
    $C35D: AC 04 C5   LDY $c504
L_C360:
    ; ===== Flag-bit 4: arpeggio (3-step) =====
    $C360: AD 0C C5   LDA $c50c
    $C363: 29 10      AND #$10
    $C365: F0 2C      BEQ $c393
    $C367: B9 10 C6   LDA $c610,y       ; instr2.byte0 = arp pattern selector
    $C36A: 0A         ASL a
    $C36B: A8         TAY
    $C36C: B9 26 C5   LDA $c526,y       ; arp source LO[selector]
    $C36F: 8D 24 C5   STA $c524
    $C372: B9 27 C5   LDA $c527,y       ; arp source HI[selector]
    $C375: 8D 25 C5   STA $c525
    $C378: AC 22 C5   LDY $c522         ; Y = arp phase (0..2)
    $C37B: 18         CLC
    $C37C: BD D7 C4   LDA $c4d7,x       ; base note
    $C37F: 79 23 C5   ADC $c523,y       ; + arp offset at phase
    $C382: 0A         ASL a
    $C383: A8         TAY
    $C384: B9 02 C4   LDA $c402,y       ; freq LO
    $C387: 9D 09 C5   STA $c509,x
    $C38A: B9 03 C4   LDA $c403,y
    $C38D: 9D 06 C5   STA $c506,x       ; freq HI
    $C390: AC 04 C5   LDY $c504
L_C393:
    ; ===== Flag-bit 5: filter sweep =====
    $C393: AD 0C C5   LDA $c50c
    $C396: 29 20      AND #$20
    $C398: F0 13      BEQ $c3ad
    $C39A: BD 1F C5   LDA $c51f,x       ; per-voice filter accumulator
    $C39D: 18         CLC
    $C39E: 79 17 C6   ADC $c617,y       ; + instr2.byte7 = filter delta
    $C3A1: 9D 1F C5   STA $c51f,x
    $C3A4: 8D 16 D4   STA $d416      ;FC_HI
    $C3A7: B9 16 C6   LDA $c616,y       ; instr2.byte6 = res/filter route
    $C3AA: 8D 17 D4   STA $d417      ;RES_FILT
L_C3AD:
    ; ===== Flag-bit 6: release alt-waveform =====
    $C3AD: 2C 0C C5   BIT $c50c
    $C3B0: 50 24      BVC $c3d6
    $C3B2: BD 16 C5   LDA $c516,x
    $C3B5: F0 09      BEQ $c3c0
    $C3B7: DE 16 C5   DEC $c516,x
    $C3BA: B9 10 C6   LDA $c610,y
    $C3BD: 4C C8 C3   JMP $c3c8
L_C3C0:
    $C3C0: B9 35 C5   LDA $c535,y       ; instr1.byte5
    $C3C3: D0 11      BNE $c3d6
    $C3C5: BD D7 C4   LDA $c4d7,x
L_C3C8:
    $C3C8: 0A         ASL a
    $C3C9: A8         TAY
    $C3CA: B9 02 C4   LDA $c402,y
    $C3CD: 9D 09 C5   STA $c509,x
    $C3D0: B9 03 C4   LDA $c403,y
    $C3D3: 9D 06 C5   STA $c506,x
L_C3D6:
    ; ===== Final SID writes for this voice =====
    $C3D6: AC C7 C4   LDY $c4c7         ; Y = D400 offset
    $C3D9: BD D4 C4   LDA $c4d4,x       ; ctrl shadow
    $C3DC: 3D DD C4   AND $c4dd,x       ; AND with mask ($FE clears gate)
    $C3DF: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $C3E2: BD 06 C5   LDA $c506,x
    $C3E5: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $C3E8: BD 09 C5   LDA $c509,x
    $C3EB: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $C3EE: FE 19 C5   INC $c519,x       ; per-voice frame counter++
    $C3F1: CA         DEX
    $C3F2: 30 03      BMI $c3f7         ; X<0 → all voices done
    $C3F4: 4C 7C C0   JMP $c07c         ; → next voice
L_C3F7:
    ; ===== Cleanup: tick global arp-phase counter =====
    $C3F7: CE 22 C5   DEC $c522
    $C3FA: 10 05      BPL $c401
    $C3FC: A9 02      LDA #$02
    $C3FE: 8D 22 C5   STA $c522
L_C401:
    $C401: 60         RTS

; ----- data $C402-$CC16 (2069 bytes) -----
; Freq table ($C402..), instrument table 1 ($C530..$C5xx, 8 bytes/instr),
; pulse-mod sub-table ($C610..$C6xx, 8 bytes/instr), song-head table
; ($C6F6..$C725, 10×6 bytes), pattern pointer tables ($C732 LO, $C7B4 HI,
; 128 entries each), and pattern data at $C835.. (subtune 7) and $C903..
; (subtunes 8/9 + remaining patterns).

; ======= $CC17: first-frame setup (called from init via $C00F) =======
; A = internal subtune index (0..9). Configures the player for this tune.
L_CC17:
    $CC17: A0 00      LDY #$00
    $CC19: AA         TAX               ; X = A
    $CC1A: A9 02      LDA #$02
    $CC1C: 8D 03 C5   STA $c503         ; nvoices-1 = 2
    $CC1F: BD ED C4   LDA $c4ed,x       ; speed reload
    $CC22: 8D 01 C5   STA $c501
    $CC25: BD F7 C4   LDA $c4f7,x       ; phase reload
    $CC28: 8D 6A C0   STA $c06a         ; SELF-MODIFY play operand at $C06A
    $CC2B: 8D 02 C5   STA $c502         ; initial phase
    $CC2E: 8A         TXA
    $CC2F: 0A         ASL a             ; *2
    $CC30: 8D E2 C4   STA $c4e2         ; scratch
    $CC33: 0A         ASL a             ; *4
    $CC34: 18         CLC
    $CC35: 6D E2 C4   ADC $c4e2         ; *4 + *2 = *6
    $CC38: AA         TAX               ; X = subtune * 6
L_CC39:
    $CC39: BD F6 C6   LDA $c6f6,x       ; copy 6 bytes of song-head:
    $CC3C: 99 F0 C6   STA $c6f0,y       ;   $C6F0..$C6F5 ← $C6F6+A*6..+5
    $CC3F: E8         INX
    $CC40: C8         INY
    $CC41: C0 06      CPY #$06
    $CC43: D0 F4      BNE $cc39
    $CC45: A9 00      LDA #$00
    $CC47: 8D 17 D4   STA $d417      ;RES_FILT    ; filter off
    $CC4A: A9 40      LDA #$40
    $CC4C: 8D 05 C5   STA $c505         ; $C505 = $40 (first-frame, not mute)
    $CC4F: 60         RTS

; ======= $CC50: end-of-song (called from $C012) =======
; Sets $C505 = $C0 (mute + first-frame). Next play frame will go through
; the C049 mute path, zero all CTRLs, then downgrade $C505 to $80.
L_CC50:
    $CC50: A9 C0      LDA #$c0
    $CC52: 8D 05 C5   STA $c505
    $CC55: 60         RTS

; ----- data $CC56-$CDFF (426 bytes) -----
; Unreached code/data: some optional "command" handlers reachable only
; via the trampolines at $C009-$C00E (which are not used by any of the
; orderlists in this PSID). Last meaningful byte at $CDFF.
