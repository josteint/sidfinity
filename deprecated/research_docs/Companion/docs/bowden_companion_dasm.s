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
exitIrq:
      jmp  $EA31                        ; Default hardware interrupt (IRQ)
;================
; Play sound irq
;================
playSound:
      ldx  currentTick                  
      inx                               ; Increment current tick
      stx  currentTick                  
      cpx  tuneSpeed                    ; Tune speed check (period)
      bne  exitIrq                      
      lda  #$00                         
      sta  currentTick                  
      jmp  processSound                 
;===================
; Sid registers:
; 0 Pulse Wave low
; 1 Pulse wave high
; 2 Ctrl
; 3 Attack/Decay
; 4 Sustain/Release
;===================
currentIndexV1:
      .byte $20, $00                    
sidRegV1:
      .byte $00, $00, $20, $09, $00     
currentIndexV2:
      .byte $20, $00, $00, $00, $20, $09, $00 
currentIndexV3:
      .byte $01, $00, $00, $00, $00, $00, $00 
;===================
; Set Irq for music
;===================
setMusicIrq:
      sei                               
      lda  #<playSound                  
      sta  $0314                        ; Vector: Hardware Interrupt (IRQ)
      lda  #>playSound                  
      sta  $0315                        ; Vector: Hardware Interrupt (IRQ)
      cli                               
      rts                               
restoreKernalIrq:
      sei                               
      lda  #$31                         
      sta  $0314                        ; Vector: Hardware Interrupt (IRQ)
      lda  $EA                          
      sta  $0315                        ; Vector: Hardware Interrupt (IRQ)
      cli                               
      nop                               
      lda  #$00                         
      ldx  #$00                         
loopClear:
      sta  $D400,x                      ; Voice 1: Frequency control (lo byte)
      inx                               
      cpx  #$19                         
      bne  loopClear                    
      rts                               
;====================
; Init sound routine
;====================
initSound:
      lda  #$00                         
      ldx  #$00                         
loopClear2:
      sta  $D400,x                      ; Voice 1: Frequency control (lo byte)
      inx                               
      cpx  #$19                         
      bne  loopClear2                   
      lda  #$0F                         
      sta  $D418                        ; Select volume and filter mode
      lda  #$09                         
      sta  $D405                        ; Generator 1: Attack/Decay
      lda  #$00                         
      sta  $D406                        ; Generator 1: Sustain/Release
      lda  #$09                         
      sta  $D40C                        ; Generator 2: Attack/Decay
      lda  #$00                         
      sta  $D40D                        ; Generator 2: Sustain/Release
      jmp  setMusicIrq                  
tuneSpeed:
      .byte $10
currentTick:
      .byte $03, $1B, $1B               
regLinit:
      .byte $13
processSound:
      ldx  currentIndexV1               ; Current index in music flow voice 1
      inc  currentIndexV1               
      ldy  musicV1,x                    
      ldx  #$00                         ; Voice 1 offset
      jsr  processData                  
      ldx  currentIndexV2               ; Current index in music flow voice 2
      inc  currentIndexV2               
      ldy  musicV2,x                    
      ldx  #$07                         ; Voice 2 offset
      jsr  processData                  
      ldx  currentIndexV3               ; Current index in music flow voice 3
      inc  currentIndexV3               
      ldy  musicV3,x                    
      ldx  #$0E                         ; Voice 3 offset
      jsr  processData                  
      jmp  $EA31                        ; Default hardware interrupt (IRQ)
processData:
      tya                               ; A=music data
      and  #$80                         
      bne  notNote                      
      lda  frequencyHi,y                
      sta  $D401,x                      ; Voice 1: Frequency control (hi byte)
      lda  frequencyLo,y                
      sta  $D400,x                      ; Voice 1: Frequency control (lo byte)
      nop                               
      nop                               
      txa                               ; A=sid offset
      tay                               
      adc  #$04                         ; A=sid offset+4
      sta  regLinit                     
loopReg:
      lda  sidRegV1,y                   
      sta  $D402,y                      ; Voice 1: Wave form pulsation amplitude (lo byte)
      iny                               
      cpy  regLinit                     
      bne  loopReg                      
      ldy  sidRegV1+2,x                 
      iny                               ; Switch gate
      tya                               
      sta  $D404,x                      ; Voice 1: Control registers
      rts                               
notNote:
      cpy  #$80                         ; Rest (enter release cycle)?
      bne  checkRestart                 
      lda  sidRegV1+2,x                 
      sta  $D404,x                      ; Voice 1: Control registers
      rts                               
checkRestart:
      cpy  #$FF                         ; Restart tune?
      bne  exitRoutine                  
      lda  #$01                         
      sta  currentIndexV1,x             ; Set index for second position
      cpx  #$00                         ; Voice 1?
      bne  testVoice2                   
      ldy  musicV1                      ; Process first positon V1
testVoice2:
      cpx  #$07                         ; Voice 2?
      bne  testVoice3                   
      ldy  musicV2                      ; Process first positon V2
testVoice3:
      cpx  #$0E                         ; Voice 3?
      bne  goProcessData                
      ldy  musicV3                      ; Process first positon V3
goProcessData:
      jmp  processData                  
exitRoutine:
      rts                               
      .org $CA00
frequencyHi:                            ; A4=424 HZ (PAL) | A4=440 HZ (NTSC)
      .byte $01, $01, $01, $01, $01, $01, $01, $01 
      .byte $01, $01, $01, $01, $00, $00, $00, $00 
      .byte $02, $02, $02, $02, $02, $02, $02, $03 
      .byte $03, $03, $03, $03, $00, $00, $00, $00 
      .byte $04, $04, $04, $04, $05, $05, $05, $06 
      .byte $06, $07, $07, $07, $00, $00, $00, $00 
      .byte $08, $08, $09, $09, $0A, $0B, $0B, $0C 
      .byte $0D, $0E, $0E, $0F, $00, $00, $00, $00 
      .byte $10, $11, $12, $13, $15, $16, $17, $19 
      .byte $1A, $1C, $1D, $1F, $00, $00, $00, $00 
      .byte $21, $23, $25, $27, $2A, $2C, $2F, $32 
      .byte $35, $38, $3B, $3F, $00, $00, $00, $00 
      .byte $43, $47, $4B, $4F, $54, $59, $5E, $64 
      .byte $6A, $70, $77, $7E, $00, $00, $00, $00 
      .byte $86, $8E, $96, $9F, $A8, $B3, $BD, $C8 
      .byte $D4, $E1, $EE, $FD, $00, $00, $00, $00 
frequencyLo:                            ; A4=424 HZ (PAL) | A4=440 HZ (NTSC)
      .byte $0C, $1C, $2D, $40, $51, $66, $7B, $91 
      .byte $A9, $C3, $DD, $FA, $00, $00, $00, $00 
      .byte $18, $38, $5A, $7D, $A3, $CC, $F6, $23 
      .byte $53, $86, $BB, $F4, $00, $00, $00, $00 
      .byte $30, $70, $B4, $FB, $47, $98, $ED, $47 
      .byte $A7, $0C, $77, $E9, $00, $00, $00, $00 
      .byte $61, $E1, $68, $F7, $8F, $30, $DA, $8F 
      .byte $4E, $18, $EF, $D2, $00, $00, $00, $00 
      .byte $C3, $C3, $D1, $EF, $1F, $60, $B5, $1E 
      .byte $9C, $31, $DF, $A5, $00, $00, $00, $00 
      .byte $87, $86, $A2, $DF, $3E, $C1, $6B, $3C 
      .byte $39, $63, $BE, $4B, $00, $00, $00, $00 
      .byte $0F, $0C, $45, $BF, $7D, $83, $D6, $79 
      .byte $73, $C7, $7C, $97, $00, $00, $00, $00 
      .byte $1E, $18, $8B, $7E, $FA, $06, $AC, $F3 
      .byte $E6, $8F, $F8, $2E, $00, $00, $00, $00 
;============================
; Music data
; 00..7F notes (octave/note)
; 80     ctrl off (release)
; FF     restart tune
;=============================
musicV1:
      .byte $32, $37, $32, $37, $32, $37, $32, $37 
      .byte $34, $37, $34, $37, $34, $37, $34, $37 
      .byte $35, $39, $35, $39, $35, $39, $35, $39 
      .byte $32, $39, $32, $39, $32, $39, $32, $39 
      .byte $FF, $40, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
musicV2:
      .byte $47, $80, $47, $47, $42, $80, $42, $80 
      .byte $44, $44, $44, $44, $40, $80, $40, $40 
      .byte $45, $80, $45, $45, $40, $40, $40, $40 
      .byte $46, $46, $46, $46, $42, $80, $42, $42 
      .byte $FF, $40, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
      .byte $00, $00, $00, $00, $00, $00, $00, $00 
musicV3:
      .byte $00, $FF, $00, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
      .byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF 
