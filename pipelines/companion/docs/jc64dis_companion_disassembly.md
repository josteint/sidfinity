---
source_url: https://github.com/ice00/jc64/blob/master/doc/example/KeithBowden_Companion.dis
fetched_via: direct (git clone)
fetch_date: 2026-05-25
author: Ice Team (disassembly comments) over Keith G. Bowden (original code)
content_date: 1984 (code) / disassembled circa 2018-2020
reliability: primary
---

# Bowden Companion player — JC64dis commented disassembly

JC64dis (an iterative C64 disassembler by Ice Team) ships a fully commented
disassembly of Keith Bowden's original `companion.prg` (the type-in from *The
Companion to the Commodore 64*, Pan Books 1984) bundled as an example project
in `doc/example/KeithBowden_Companion.dis` (gzipped JC64dis project file).

Extracted Dasm-format source below. The local file
`/tmp/companion_dasm_final.txt` has the complete listing.

## Header

```
;****************************
;  JC64dis version 1.9
;  Source in Dasm format
;****************************
      processor 6502
      .org $C000
;==========================
; Keith Bowden player
; by Keith G. Bowden
; (c) 1984 Pan Books
;==========================
; tune "Music Roundabout"
;==========================
```

The shipped tune is "Music Roundabout" — Bowden's example/demo tune from the
book. Load address $C000.

## Code structure (Bowden original, $C000-base)

```
exitIrq:                              ; jmp $EA31 (kernal IRQ continue)
playSound:                            ; tick-counter IRQ handler
    ldx currentTick                   ;   tick++
    inx
    stx currentTick
    cpx tuneSpeed                     ;   if (tick == tuneSpeed) {
    bne exitIrq                       ;     tick=0; processSound() }
    lda #$00
    sta currentTick
    jmp processSound

; --- per-voice state (interleaved 7-byte records) ---
currentIndexV1: .byte $20, $00        ; [0]=cursor [1]=padding
sidRegV1:       .byte $00, $00, $20, $09, $00
                                       ;  [2..6] = pulse-lo, pulse-hi,
                                       ;          ctrl(no-gate), AD, SR
currentIndexV2: .byte $20, $00, $00, $00, $20, $09, $00
currentIndexV3: .byte $01, $00, $00, $00, $00, $00, $00

setMusicIrq:                          ; install playSound at $0314/$0315
restoreKernalIrq:                     ; restore + clear SID regs

processSound:
    ldx currentIndexV1                ; per-voice driver
    inc currentIndexV1
    ldy musicV1,x
    ldx #$00                          ; SID base offset for voice 1 ($D400)
    jsr processData
    ldx currentIndexV2
    inc currentIndexV2
    ldy musicV2,x
    ldx #$07                          ; SID base offset for voice 2 ($D407)
    jsr processData
    ldx currentIndexV3
    inc currentIndexV3
    ldy musicV3,x
    ldx #$0E                          ; SID base offset for voice 3 ($D40E)
    jsr processData
    jmp $EA31

processData:                          ; Y=note byte, X=SID offset (0/7/14)
    tya
    and #$80                          ; is bit7 set?
    bne notNote                       ;   yes -> sentinel handler
    ; --- 0..7F: regular note ---
    lda frequencyHi,y
    sta $D401,x                       ; FREQ HI
    lda frequencyLo,y
    sta $D400,x                       ; FREQ LO
    nop
    nop
    txa                               ; build copy range = X..X+4
    tay
    adc #$04
    sta regLinit
loopReg:
    lda sidRegV1,y                    ; copy pulse-lo, pulse-hi, ctrl, AD, SR
    sta $D402,y                       ; into D402,X .. D406,X
    iny
    cpy regLinit
    bne loopReg
    ldy sidRegV1+2,x                  ; ctrl byte (with gate off)
    iny                               ; flip gate bit → gate on
    tya
    sta $D404,x                       ; CTRL
    rts

notNote:
    cpy #$80                          ; $80 = REST (gate-off only)
    bne checkRestart
    lda sidRegV1+2,x                  ; load gate-off ctrl
    sta $D404,x
    rts

checkRestart:
    cpy #$FF                          ; $FF = RESTART tune (this voice)
    bne exitRoutine
    lda #$01
    sta currentIndexV1,x              ; reset cursor to 1 (skip slot 0)
    cpx #$00
    bne testVoice2
    ldy musicV1                       ; … and replay slot 0 immediately
testVoice2:
    cpx #$07
    bne testVoice3
    ldy musicV2
testVoice3:
    cpx #$0E
    bne goProcessData
    ldy musicV3
goProcessData:
    jmp processData                   ; (tail-recurse with slot-0 byte)
exitRoutine:
    rts
```

## Data layout

```
$CA00  frequencyHi[128]   ; PAL A4=424 Hz, NTSC A4=440 Hz
$CA80  frequencyLo[128]   ; (same indexing)
       musicV1[…]
       musicV2[…]
       musicV3[…]
```

Each frequency table is 128 bytes long indexed by the 7-bit note value.
Within an octave (16 entries), only the first 12 are real notes; the last 4
slots are zeros. This makes the note byte effectively `(octave<<4)|note` with
notes 0..11 in each octave (the example tune uses values $32, $37, $34, $39,
$40, … i.e. octave-3 note 2, etc.).

## "Music Roundabout" data sample (musicV1 head)

```
.byte $32, $37, $32, $37, $32, $37, $32, $37
.byte $34, $37, $34, $37, $34, $37, $34, $37
.byte $35, $39, $35, $39, $35, $39, $35, $39
.byte $32, $39, $32, $39, $32, $39, $32, $39
.byte $FF, $40, $FF, …                          ; restart sentinel
```

## Music data format (verbatim comment from disassembly)

```
;============================
; Music data
; 00..7F notes (octave/note)
; 80     ctrl off (release)
; FF     restart tune
;=============================
```

That is the **complete** Bowden-format spec. No tempo bytes, no instrument
table, no effects — every note's instrument settings come from the per-voice
state record (`pulse-lo, pulse-hi, ctrl, AD, SR`) which the program patches
directly at startup. Tempo is a global divider (`tuneSpeed`, default $10 = 16
IRQs per step).

## What this means for our /home/jtr/sidfinity/src/Companion/ engine

The local sidfinity disassembly at $C900/$C703 with state at $C6C0,
orderlists at $C5B0/$C5F8/$C640 and tempo dividers at $C6D5/$C6D6 is **NOT
Bowden's original $C000-based code** — it is an extension. Compared to base
Bowden:

| Feature                | Bowden $C000          | Local Companion $C900   |
|------------------------|-----------------------|-------------------------|
| Layout                 | single layer (notes)  | orderlist → notes      |
| Tempo                  | 1 divider             | 2 dividers ($C6D5/D6)  |
| State                  | inline 7-byte records | $C6C0+ block            |
| PWM                    | none                  | global PW sweep on V3   |
| Sentinels (note layer) | $80 rest, $FF restart | likely same             |

The extra orderlist layer plus the dual tempo divider plus voice-3 PW sweep
is consistent with what sidid calls the **Hubbard-extended** Companion
(two-earliest-Hubbard-SIDs branch) — distinct from the
**Jay-Derrett/Clever-Music** extension which has a 4+4-nibble note byte.

## Bowden's own bibliography (for cross-reference)

The disassembly was extracted from `/home/ice/SRC/lst/Companion/companion.prg`
on Ice's machine, indicating the source PRG is something Ice Team obtained
directly. The header comment names the author as "Keith G. Bowden" (full
middle initial — useful for further searches).
