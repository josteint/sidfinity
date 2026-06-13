;---------------------------------------
;SDI PLAYER V2.1 N50 (C)16/05/2014 SHAPE
;  GEIR TJELTA & GLENN RUNE GALLEFOSS
;---------------------------------------
SID      = $D400
MZERO    = $FE   ;PLAYER ZEROPAGE
;---------------------------------------
REM~a44CH  = 1  ;1 = IGNORE 4TH CHANNEL
REM~a4DET  = 0  ;1 = IGNORE DETUNE (Z8/Z9)
REM~a4GOUT = 0  ;1 = IGNORE GATE TIMEOUT
REM~a41WF  = 0  ;1 = IGNORE 1ST WFPRG BYTE
REM~a4WFD  = 1  ;1 = IGNORE FE WF HOLD CMD
REM~a4ADSR = 1  ;1 = IGNORE FD WF ADSR CMD
REM~a4MP   = 1  ;1 = IGNORE FB WF PULS CMD
REM~a4WFR  = 1  ;1 = IGNORE FA WFP REP CMD
REM~a4WF0  = 1  ;1 = IGNORE F0-F7 WF D415
REM~a4PUW  = 1  ;1 = IGNORE EB-EE WF PULSE
REM~a4PU   = 0  ;1 = IGNORE PULSE ROUTINE
REM~a4WE2  = 1  ;1 = IGNORE E2-E7 WF NOISE
REM~a4ARP  = 0  ;1 = IGNORE ARP ROUTINE
REM~a4FI   = 0  ;1 = IGNORE FILTER ROUTINE
REM~a4FSPD = 1  ;1 = IGNORE FILTER SPEED
REM~a4GLID = 0  ;1 = IGNORE GLIDE ROUTINE
REM~a4VIB  = 0  ;1 = IGNORE VIBRATO ROUT
REM~a4CC   = 1  ;1 = IGNORE CRAZY COM VIB
REM~a4FAD  = 1  ;1 = IGNORE FADEOUT ROUTIN
REM~a4GAT  = 1  ;1 = IGNORE SEQ GAT/FLGCMD
REM~a4F20  = 1  ;1 = IGNORE SEQ 20 FILTCMD
REM~a4WFO  = 1  ;1 = IGNORE SEQ WF ORA CMD
REM~a4VOFF = 1  ;1 = IGNORE VOICE ON/OFF
REM~a4TRKL = 1  ;1 = MAX $FF TRACK SIZE
REM~a4TP   = 0  ;1 = IGNORE TEMPO PROGRAMS
;NB!!^^ ENTER SONG'S TEMPO IN OFFSET "S"
;SAVE CYCLES IF ONLY SINGLE TEMPOS USED.
;---------------------------------------
FRQSUM   = REM~a4DET*REM~a4CC
GATSUM   = REM~a4GOUT*REM~a4ADSR
ADDSUM   = REM~a4GLID*REM~a4VIB

         *= $0C00

RAS1     = $02
RAS2     = $03
RASMAX   = $04
VZP      = $05

CLOCK    = $0568+6+$28
TUN      = $0590+6+$28
FCH      = $05B8+6+$28
CYCLER   = $05E0+6+$28
RASTER   = $0608+6+$28

VSCR     = $0798+$28

         SEI
         CLD
         JSR $FF84
         LDY #1
         LDA #$81
         BIT $D011
         BMI *-3
         BIT $D011
         BPL *-3
         LDX #$72
         DEX
         BPL *-1
         BIT $D011
         BMI PAL
         TYA
         DEY
PAL      STY $02A6
         STA $DC0E
         JSR TIMBOFF
         LDA #<INFO
         LDY #>INFO
         JSR $AB1E
         LDA #$2F
         STA TUN+2
         LDA #S-C-1
         JSR GETALL
         STX TUN+3
         STA TUN+4
         LDA #$16
         STA $D018
         SEI
         LDA #<INT
         STA $0314
         LDA #>INT
         STA $0315
         LDA #$7F
         STA $DC0D         
         LDX #1
         STX $D01A
         DEX
         STX ZZ+1
         LDA #$FF
         STA $D012
         LDA #$1B
         STA $D011
         BIT $DC0D
         CLI
         JMP START
         
FFE4     JSR $FFE4
         BEQ *-3

KFADE    CMP #$46
         BNE KSP
         LDA #$1F
         JSR FADEOUT
         JMP FFE4
         *= *-((*-KFADE)*REM~a4FAD)

KSP      LDX ZZ+1
         CMP #$20
         BNE KPL
         JMP START
KPL
         CMP #$2B
         BNE KMIN
         INX
         CPX #S-C
         BCC *+4
         LDX #0
         JMP START

KMIN     CMP #$2D
         BNE VOIC
         DEX
         BPL *+4
         LDX #S-C-1
         JMP START

VOIC     CMP #$31
         BCC VO1
         CMP #$34
         BCS VO1
         SEC
         SBC #$31
         TAX
         BEQ *+11
         CLC
         LDA #0
         ADC #7
         DEX
         BNE *-3
         TAX
         LDA SEQBYTE,X
         BMI VO1
         LDA VOFF+1
         EOR CHANON,X
         STA VOFF+1
         *= *-((*-VOIC)*REM~a4VOFF)
VO1      JMP FFE4
START    SEI
         STX ZZ+1
ZZ       LDX #0
         JSR INIT
         JSR SETOD
         CLI
         JMP FFE4

INT      INC $D019
SPOL     DEC $D020
         LDA $D011
         BPL NOR
         JSR PLAY
         JMP CONT
NOR      LDA $D012
         STA RAS1
         JSR IPLAY
         LDA $D012
         SEC
         SBC #1
         STA RAS2
CONT     LDA #0
         STA $D020
         LDA $DC01
         CMP #$FD
         BEQ SPOL
         CMP #$DF
         BEQ GOGG
         CMP #$FB
         BNE CLR
         LDA #0
         JSR CLEARMAX
CLR      JSR TOD
R~a4VOFFX  JSR VOICES
         *= *-((*-R~a4VOFFX)*REM~a4VOFF)
VO~a4FI2   JSR FCHAN
         *= *-((*-VO~a4FI2)*REM~a4FI)
         JSR RTIME
         JSR SONG
         JSR CYCLES
         JMP $EA31
GOGG     JSR $FDA3
         JSR $FD15
         JSR $E518
         SEI
         JMP $9000
RTIME    LDA RAS2
         SEC
         SBC RAS1

         CMP RASMAX
         BCC NEWMAX
         STA RASMAX
NEWMAX   LDA RASMAX
         JSR GETALL
         STX RASTER
         STA RASTER+1
         RTS

SONG     LDA ZZ+1
         JSR GETALL
         STX TUN
         STA TUN+1
         RTS
GETALL   PHA
         LSR A
         LSR A
         LSR A
         LSR A
         TAY
         LDA TALL,Y
         TAX
         PLA
         AND #$0F
         TAY
         LDA TALL,Y
         RTS
SETOD    LDA #0
         STA $DC0F
         STA $DC0B
         STA $DC0A
         STA $DC09
         STA $DC08
         STA $D020
         STA $D021
         BIT $DC08         
         STA RAS1
         STA RAS2
CLEARMAX STA RASMAX
         STA MAXLO
         STA MAXHI
         RTS
TOD      LDA #$3A
         STA CLOCK+2
         LDY #4
         LDA $DC09
         JSR GETOD
         LDY #1
         LDA $DC0A
GETOD    TAX
         AND #$0F
         ORA #$30
         STA CLOCK,Y
         TXA
         LSR A
         LSR A
         LSR A
         LSR A
         ORA #$30
         DEY
         STA CLOCK,Y
         RTS
VOICES   LDA #<VSCR+8+(4*(1-REM~a44CH))
         STA VZP
         LDA #>VSCR+8+(4*(1-REM~a44CH))
         STA VZP+1
         LDX #CHANNELS*7
VO4      LDY #2
         LDA VOFF+1
         AND CHANON,X
         BNE VO2
VO3      LDA OFF,Y
         STA (VZP),Y
         DEY
         BPL VO3
         BNE VO5

VO2      LDA ON,Y
         STA (VZP),Y
         DEY
         BPL VO2
VO5      LDA VZP
         SEC
         SBC #$04
         BCS *+4
         DEC VZP+1
         STA VZP
         TXA
         SEC
         SBC #7
         TAX
         BPL VO4
         RTS

FCHAN    LDA FILTCH+1
VO~a4FI    ORA FILTENA+1
         *= *-((*-VO~a4FI)*REM~a4F20)

         LDX #$30
         LSR A
         BCC *+4
         LDX #$31
         STX FCH

         LDX #$30
         LSR A
         BCC *+4
         LDX #$31
         STX FCH+2

         LDX #$30
         LSR A
         BCC *+4
         LDX #$31
         STX FCH+4
         RTS
         *= *-((*-FCHAN)*REM~a4FI)

TALL     .TEXT "0123456789"
         .BYTE 1,2,3,4,5,6
OFF      .BYTE $0F,$06,$06
ON       .BYTE $0F,$0E,$20
INFO     .BYTE $05,$93,$08,$1E
         .TEXT "SDI V2.1 PLAYER 2014"
         .BYTE $0D,$0D
         .BYTE $5F
         .TEXT "    :FFWD"
         .BYTE $0D
         .TEXT "SPACE:RESTART"
         .BYTE $0D
         .TEXT "+/-  :SUBTUNES"
         .BYTE $0D
         .TEXT "1-3  :VOICES"
         .BYTE $0D
         .TEXT "F    :FADE"
         .BYTE $0D
         .TEXT "CBM  :EXIT"
         .BYTE $0D,$0D,$0D
         .TEXT "CLOCK:"
         .BYTE $0D
         .TEXT "TUNE :"
         .BYTE $0D
         .TEXT "FCHAN:"
         .BYTE $0D
         .TEXT "CYCLE:"
         .BYTE $0D
         .TEXT "D012 :"         
         .BYTE 0


CYCLES   LDA $DD07
         EOR #$FF
         STA CURRHI
         LDA $DD06
         EOR #$FF
         SEC
         SBC #18
         STA CURRLO
         BCS *+5
         DEC CURRHI

         LDY CURRHI
         TYA
         LDX CURRLO
         CPX MAXLO
         SBC MAXHI
         BCC MX1
         STY MAXHI
         STX MAXLO

MX1      LDA MAXHI
         JSR GETALL
         STX CYCLER
         STA CYCLER+1
         LDA MAXLO
         JSR GETALL
         STX CYCLER+2
         STA CYCLER+3
         LDA CURRHI
         JSR GETALL
         STX CYCLER+5
         STA CYCLER+6
         LDA CURRLO
         JSR GETALL
         STX CYCLER+7
         STA CYCLER+8
         RTS

MAXLO    .BYTE 0
MAXHI    .BYTE 0
CURRLO   .BYTE 0
CURRHI   .BYTE 0

IPLAY    LDA #$FF
         STA $DD06
         STA $DD07
         LDA #%00001001
         STA $DD0F
         JSR PLAY
TIMBOFF  LDA #%00001000
         STA $DD0F
         RTS


;------------------START OF DRIVER/DATA-

         *= $1000

         JMP INIT    ;CALL WITH X
         JMP PLAY
R~a4FAD3   JMP FADEOUT ;NEGATIVE # =DOWN
         *= *-((*-R~a4FAD3)*REM~a4FAD)

         .TEXT "-PLAYER V2.1 "
         .TEXT "BY GT+GRG-"

CHANON   = *
CHANOFF  = *+1
TRKLO    = *+2
TRKHI    = *+3
TDELAY   = *+4
TRACKY   = *+5
TRACKHI  = *+6
         .BYTE $01,$FE,0,0,0,0,0
         .BYTE $02,$FD,0,0,0,0,0
         .BYTE $04,$FB,0,0,0,0,0
CHANX    .BYTE $80,$7F,0,0,0,0,0

TRANSP   = *+1
DUR      = *+2
DURATION = *+3
SEQP     = *+4
SOUND2   = *+5
NOTE2    = *+6
         .BYTE $00,0,0,0,0,0,0
         .BYTE $07,0,0,0,0,0,0
         .BYTE $0E,0,0,0,0,0,0
FADECO   .BYTE 0,0,0,0,0,0,0
RELEASE  = *
SEQSUST  = *+1
SEQBYTE  = *+2
FILTRE   = *+3
GLIDADD2 = *+4
WF~a4ORA   = *+5
WF~a4ORA2  = *+6
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
ARPNUM2  = *
ARPLE    = *+1
SRCO     = *+2
SOUND    = *+3
NOTE     = *+4
GATE     = *+5
GATEDEC  = *+6
         .BYTE $80,0,0,0,0,0,0
         .BYTE $80,0,0,0,0,0,0
         .BYTE $80,0,0,0,0,0,0
         .BYTE $00
ARPNUM   = *
ATTACK   = *+1
SUSTAIN  = *+2
GLIDADD  = *+3
GLIDTO   = *+4
ADDLO    = *+5
ADDHI    = *+6
         .BYTE $80,0,0,0,0,0,0
         .BYTE $80,0,0,0,0,0,0
         .BYTE $80,0,0,0,0,0,0
ARPDE    = *
ADDVAL~a4L = *+1
ADDVAL~a4H = *+2
VIBLE    = *+3
VIBWID   = *+4
VIBDIR   = *+5
VIBDEC   = *+6
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0

PULSCO   = *
PULSEOR  = *+1
PULSDEL  = *+2
PULSLE   = *+3
PULSLE2  = *+4
PULSDEC  = *+5
PULSDEC2 = *+6
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
PULSLO   = *
PULSLO2  = *+1
PULSHI   = *+2
PULSHI2  = *+3
PULSHLD  = *+4 ;USES 2 BUT NEEDS ONLY 1
         ;6 FREE
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0

WF       = *
WFP      = *+1
WF~a4DEL   = *+2
WF~a4REPET = *+3
DETUNLO  = *+4
DETUNHI  = *+5
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0
         .BYTE 0,0,0,0,0,0,0

FILTSPD  .BYTE 0
         *= *-((*-FILTSPD)*REM~a4FSPD)

CLEAR~a4WAV
         STA SID+$04
         STA SID+$0B
         STA SID+$12
         JMP FADE
         *= *-((*-CLEAR~a4WAV)*REM~a4VOFF)

CHANNELS = 3-REM~a44CH

PLAY     LDX #CHANNELS*7
VOFF     LDA #0
         BEQ CLEAR~a4WAV
         *= *-((*-VOFF)*REM~a4VOFF)
;-----------------------CONDUCTOR/TEMPO-
R~a44CH1
         BPL NOC2
         *= *-((*-R~a44CH1)*REM~a4VOFF)

         LDY DURATION+21
         BPL NO~a4CONDUCT
         LDA TEMPO+1
         BEQ COND~a4DUR
         CMP CUR~a4TEM+1
         BEQ COND~a4SEQ
NOC2     JMP NO~a4CONDUCT

COND~a4DUR LDA DUR+21
         STA DURATION+21

R~a4FI8    LDA RELEASE+21
         ASL A
         ASL A
         ASL A
         ASL A
         STA SETFI+1

         LDA GLIDADD2+21
         BMI NO~a4CONDUCT
         STY GLIDADD2+21
         BEQ RESTFI
         STY FILTSND+1
         LSR A
         LSR A
         STA FILTLE+1
         LDA #0
         STA FILTDEC+1
F~a4SPD3   STA FILTSPD
         *= *-((*-F~a4SPD3)*REM~a4FSPD)
         BEQ NO~a4CONDUCT
RESTFI   STA FILTRE
         STA FILTRE+7
         STA FILTRE+14
         *= *-((*-R~a4FI8)*REM~a4FI)
         BPL NO~a4CONDUCT

COND~a4SEQ STX X+1
         LDA #$7F
         STA ARPNUM2+21
         JMP SEQ~a4COND
COND~a4RET
R~a4VOFF1  LDA VOFF+1
         BMI COND~a4ON
         LDA #0
         STA TRK~a4TRAN+1
         BEQ NO~a4CONDUCT
         *= *-((*-R~a4VOFF1)*REM~a4VOFF)
COND~a4ON  LDA ARPNUM2+21
         BMI SET~a4TEM
         CMP #$7F
         BEQ NO~a4CONDUCT
         CMP #$40
         BCS SETBAND
         LSR A
SET~a4TEM  STA TEM~a4PRG+1
         LDA #0
         STA TEM~a4Y+1
R~a4FI9    BEQ NO~a4CONDUCT
         *= *-((*-R~a4FI9)*REM~a4FI)
SETBAND
R~a4FI10   ASL A
         ASL A
         ASL A
         STA BAND+1
         *= *-((*-R~a4FI10)*REM~a4FI)
NO~a4CONDUCT
         LDX #(CHANNELS-1)*7
         *= *-((*-R~a44CH1)*REM~a44CH)

;-----------------------PLAYER LOOP POS-
PART1    STX X+1
R~a4GOUT1  LDA GATEDEC,X
         BEQ BN71
         DEC GATEDEC,X
         BNE BN71
         LDA #$FE
         STA GATE,X
BN71
         *= *-((*-R~a4GOUT1)*GATSUM)
         LDA DURATION,X
         BPL BN33
TEMPO    LDA #0
         BEQ SETVAL

CUR~a4TEM  CMP #0
         BEQ *+5
BN33     JMP PART2
         JMP SEQU2

;-------------------SET TIE/GLIDE/NOTE--
SETVAL   LDA DUR,X
         STA DURATION,X

R~a4VOFF2  LDA VOFF+1
         AND CHANON,X
         BEQ BN33
         *= *-((*-R~a4VOFF2)*REM~a4VOFF)

         LDY NOTE2,X
R~a4GAT2   BMI R~a4GAT1
         *= *-((*-R~a4GAT2)*REM~a4GAT)
         CPY #$5F
         BEQ FORCEVIB

R~a4GLI1   LDA GLIDADD2,X
         STA GLIDADD,X
         BNE R~a4GLI2
         *= *-((*-R~a4GLI1)*REM~a4GLID)

FCODE4   LDA #0
         *= *-((*-FCODE4)*(1-REM~a4GLID))

         STA ADDLO,X
         STA ADDHI,X
         *= *-((*-FCODE4)*ADDSUM)

         TYA
         STA NOTE,X

BN27     LDA #0
         STA VIBDEC,X
         *= *-((*-BN27)*REM~a4VIB)

R~a4ARP1   LDA ARPNUM2,X
         STA ARPNUM,X
         BMI TIE~a4NOTE
         STA ARPDE,X
         TAY
         LDA AD,Y
         STA ARPLE,X
         *= *-((*-R~a4ARP1)*REM~a4ARP)

;--------------------SET INSTRUMENTS----
TIE~a4NOTE LDA SRCO,X
         BNE SET~a4SND
         JMP WFROUT

R~a4GAT1   TYA
         STA GATE,X
         JMP PART2
         *= *-((*-R~a4GAT1)*REM~a4GAT)

FORCEVIB LDA GLIDADD2,X
         BEQ BN33
R~a4VIB1   LSR A
         LSR A
         STA VIBLE,X
         LDA #0
         STA VIBDEC,X
         *= *-((*-R~a4VIB1)*REM~a4VIB)
         JMP GLIDE

R~a4GLI2   TYA
         STA GLIDTO,X
         BPL BN27
         *= *-((*-R~a4GLI2)*REM~a4GLID)

SET~a4SND  STA GATE,X
         LDY SOUND2,X
         LDA SEQSUST,X
         CMP #1
         LDA Z2,Y
         BCC BN21
         AND #$0F
         ORA SEQSUST,X
BN21     STA MZERO+1
         AND #$F0
         STA SUSTAIN,X
         ORA #$0F
         STA SID+6,X

         LDA WF,X
         ORA #1
         STA SID+4,X

R~a4DET1   LDA Z8,Y
         STA DETUNHI,X
         LDA Z9,Y
         STA DETUNLO,X
         *= *-((*-R~a4DET1)*REM~a4DET)

R~a4GOUT2  LDA Z3,Y
         AND #$1F
         ASL A
         STA GATEDEC,X
         *= *-((*-R~a4GOUT2)*GATSUM)

R~a4FI1    LDA FILTRE,X
         BMI BN37
         LDA Z6,Y
         STA FILTRE,X
         ASL A
         BNE BN45
         BCS BN37
         LDA FILTCH+1
         AND CHANOFF,X
         BCC BN37-3

BN45     LSR A
         STA FILTLE+1
         LDA #0
         STA FILTDEC+1
F~a4SPD4   STA FILTSPD
         *= *-((*-F~a4SPD4)*REM~a4FSPD)
         STY FILTSND+1
         LDA FILTCH+1
         ORA CHANON,X
         STA FILTCH+1
         *= *-((*-R~a4FI1)*REM~a4FI)

BN37     LDA Z4,Y
         STA VIBLE,X
         *= *-((*-BN37)*REM~a4VIB)

         LDA Z5,Y
         BEQ NO~a4PULS
R~a4PU1    BPL PULW~a4VAL
         *= *-((*-R~a4PU1)*REM~a4PU)

         AND #$7F
         STA SID+2,X
         STA SID+3,X
R~a4OP3    LDA #0
         STA PULSLE2,X
         *= *-((*-R~a4OP3)*REM~a4MP)
NO~a4PULS
R~a4PU2    LDA PULSLE,X
         ORA #$80
         BNE PULS~a4OFF
PULW~a4VAL ASL A
         ASL A
         TAY
         BCC PULS~a4ON
         LDA SOUND2,X
         CMP SOUND,X
         BEQ PULS~a4END

PULS~a4ON  LDA #0
R~a4MP4    STA PULSLE2,X
         *= *-((*-R~a4MP4)*REM~a4MP)
         STA PULSDEC,X
         LDA P-4,Y
         STA SID+2,X
         STA SID+3,X
         TYA
         LSR A
         LSR A
PULS~a4OFF STA PULSLE,X
PULS~a4END
         *= *-((*-R~a4PU2)*REM~a4PU)

         LDY SOUND2,X
         LDA Z1,Y
         LDY ATTACK,X
         BNE SETATT
         LDY SEQSUST,X
         BEQ NEWSUST
         LDA #0
         BEQ NEWSUST
SETATT   LDA #0
         STA ATTACK,X
         STA SEQSUST,X
R~a4GOUT3  STA GATEDEC,X
         *= *-((*-R~a4GOUT3)*GATSUM)
         TYA
NEWSUST  STA SID+5,X
         LDA MZERO+1
         STA SID+6,X

         LDA #0
         STA SRCO,X
R~a4WFD3   STA WF~a4DEL,X
         *= *-((*-R~a4WFD3)*REM~a4WFD)
R~a4WFR3   STA WF~a4REPET,X
         *= *-((*-R~a4WFR3)*REM~a4WFR)

R~a4PU3    LDA SOUND2,X
         STA SOUND,X
         TAY
         *= *-((*-R~a4PU3)*REM~a4PU)
R~a4PU4    LDY SOUND2,X
         *= *-((*-R~a4PU4)*(1-REM~a4PU))
         LDA Z0,Y

R~a41WF1   TAY
         INY
         TYA
         *= *-((*-R~a41WF1)*REM~a41WF)
R~a41WF2   CLC
         ADC #1
         *= *-((*-R~a41WF2)*(1-REM~a41WF))
         STA WFP,X

R~a41WF3   LDA W-1,Y
R~a4ARP2   CMP #$90
         BCC *+4
         AND #$7F
         *= *-((*-R~a4ARP2)*REM~a4ARP)
         STA SID+4,X

         LDA F-1,Y
         BMI FRQ~a4LOCK
         CLC
         ADC NOTE,X
FRQ~a4LOCK AND #$7F
         TAY
         LDA FREQLO,Y
R~a4DET2   CLC
         ADC DETUNLO,X
         *= *-((*-R~a4DET2)*REM~a4DET)
         STA SID+0,X
         LDA FREQHI,Y
R~a4DET3   ADC DETUNHI,X
         *= *-((*-R~a4DET3)*REM~a4DET)
         STA SID+1,X
         *= *-((*-R~a41WF3)*REM~a41WF)
         JMP SID~a4NEXT


;----------------SEQUENCER--------------
SEQU2    LDA #0
         STA GLIDADD2,X
SEQ~a4COND
         LDY SEQBYTE,X
R~a4VOFF3  BPL BN54
         LDA VOFF+1
         AND CHANOFF,X
         STA VOFF+1

R~a44CH5   CPX #21
         BNE SEQU2-3
         JMP COND~a4RET
         *= *-((*-R~a44CH5)*REM~a44CH)
R~a44CH6   JMP SID~a4NEXT
         *= *-((*-R~a44CH6)*(1-REM~a44CH))
         *= *-((*-R~a4VOFF3)*REM~a4VOFF)

BN54     LDA SL,Y
         STA MZERO
         LDA SH,Y
         STA MZERO+1

R~a4WFO1   LDA #$FF
         STA WF~a4ORA2,X
         *= *-((*-R~a4WFO1)*REM~a4WFO)

R201     LDA #BN32-FXJMP-2
         STA FXJMP+1
         *= *-((*-R201)*REM~a4F20)

         LDY SEQP,X
         LDA (MZERO),Y
         CMP #$5F
         BEQ BN6
         CMP #$F0
         BCC BN4
         AND #$0F
         STA RELEASE,X
         BPL BN6

BN4      CMP #$C0
         BCC BN13
         AND #$3F
         ASL A
         STA ARPNUM2,X
         TAX
         LDA AD+1,X
         AND #$3F
X        LDX #0
         BPL BN15

BN13     CMP #$A0
         BCC BN14
         AND #$1F
         ASL A
         ASL A
         STA GLIDADD2,X
R202     BPL BN6
         *= *-((*-R202)*(1-REM~a4F20))

COM20    BNE BN6
         LDA #COMFX-FXJMP-2
         STA FXJMP+1
         BNE BN6
         *= *-((*-COM20)*REM~a4F20)

BN14     CMP #$80
         BCC BN7
         STA ARPNUM2,X
         AND #$3F
R~a4WFO2   STA WF~a4ORA2,X
         *= *-((*-R~a4WFO2)*REM~a4WFO)

BN15     STA SOUND2,X
R~a4FI2    STA FILTRE,X
         *= *-((*-R~a4FI2)*REM~a4FI)

         LDA #0
R~a4WFO3   STA WF~a4ORA,X
         *= *-((*-R~a4WFO3)*REM~a4WFO)

         STA SEQSUST,X
BN6      INY
         LDA (MZERO),Y
         CMP #$DF
         BCC BN7
         BEQ DUR~a420
         AND #$3F
         BNE BN12
DUR~a420   INY
         LDA (MZERO),Y
         BNE BN12

R~a44CH7   CMP #$5F
         BEQ NOTE2CH4
         AND #$7F
         STA NOTE2CH4+1
NOTE2CH4 LDA #0
         CLC
         ADC TRANSP+21
         STA TRK~a4TRAN+1
         JMP TRACK~a4CONDUCT
         *= *-((*-R~a44CH7)*REM~a44CH)

BN7      CMP #$80
         BCS BN56
         CMP #$60
         BCC BN56
         AND #$1F
BN12     STA DUR,X
         INY
         LDA (MZERO),Y
         CMP #$F0
         BCC BN56
         AND #$0F
         STA RELEASE,X
         LDA #$5F
BN56
R~a44CH2   CPX #21
         BEQ R~a44CH7
         *= *-((*-R~a44CH2)*REM~a44CH)

         CMP #$5F
FXJMP    BNE BN32
         STA ACK+1
         STA NOTE2,X
         LDA RELEASE,X
         BMI TRACK~a4CONDUCT
         ORA SUSTAIN,X
         STA SID+6,X
         LDA #$FE
         STA GATE,X
         STA RELEASE,X
         BNE TRACK~a4CONDUCT

COMFX    LSR A
         LDA FILTENA+1
         BCS DISAFI
         ORA CHANON,X
         BNE DISAF2
DISAFI   AND CHANOFF,X
DISAF2   STA FILTENA+1
         LDA #$5F
         STA ACK+1
         BNE NOTE~a45F
         *= *-((*-COMFX)*REM~a4F20)

R~a4GAT4   ADC #0
         EOR #$FF
         STA NOTE2,X
         LDA #$5F
         STA ACK+1
         BNE TRACK~a4CONDUCT
         *= *-((*-R~a4GAT4)*REM~a4GAT)

BN32     STA ACK+1
         AND #$7F
R~a4GAT3   BEQ R~a4GAT4
         *= *-((*-R~a4GAT3)*REM~a4GAT)
         CLC
TRK~a4TRAN ADC #0
         CLC
         *= *-((*-TRK~a4TRAN)*REM~a44CH)
         ADC TRANSP,X
NOTE~a45F  STA NOTE2,X

TRACK~a4CONDUCT
         INY
         LDA (MZERO),Y
         BEQ *+3
         TYA
         STA SEQP,X
         BNE TRK~a4END

TRACK~a4INIT
         LDY TDELAY,X
         BEQ BN61
         DEC TDELAY,X
         BPL TRK~a4END

BN61     LDA TRACKY,X ;16-BIT
         STA MZERO
         LDA TRACKHI,X
         STA MZERO+1
         *= *-((*-BN61)*REM~a4TRKL)
R~a4TRKL1  LDA TRKLO,X  ;8-BIT
         STA MZERO
         LDA TRKHI,X
         STA MZERO+1
         LDY TRACKY,X
         *= *-((*-R~a4TRKL1)*(1-REM~a4TRKL))

         LDA (MZERO),Y
         BPL BN28
         CMP #$F7
         BCC T~a4DEL
R~a4STOP   BEQ BN28
         *= *-((*-R~a4STOP)*REM~a4VOFF)

R~a4TRKL2  AND #7
         STA BN36+1
         INY
         CLC
         LDA TRKLO,X
         ADC (MZERO),Y
         STA MZERO
         LDA TRKHI,X
BN36     ADC #0
         STA MZERO+1
         DEY
         *= *-((*-R~a4TRKL2)*REM~a4TRKL)
R~a4TRKL3  INY
         LDA (MZERO),Y
         TAY
         *= *-((*-R~a4TRKL3)*(1-REM~a4TRKL))
         LDA (MZERO),Y
T~a4DEL    CMP #$C0
         BCC BN62
         AND #$3F
         STA TDELAY,X
         INY
         LDA (MZERO),Y
         BPL BN28
BN62     SEC
         SBC #$A0
         STA TRANSP,X
         INY
         LDA (MZERO),Y
BN28     STA SEQBYTE,X
R~a4TRKL4  TYA
         SEC
         ADC MZERO
         STA TRACKY,X
         LDA #0
         ADC MZERO+1
         STA TRACKHI,X
         *= *-((*-R~a4TRKL4)*REM~a4TRKL)
R~a4TRKL5  INY
         TYA
         STA TRACKY,X
         *= *-((*-R~a4TRKL5)*(1-REM~a4TRKL))
TRK~a4END  CPX #21
         BEQ RRTS
         *= *-((*-TRK~a4END)*REM~a44CH)

ACK      LDA #0
         CMP #$5F
         BEQ BN66
         LDA RELEASE,X
         BCS TIE~a4ATT
         BMI NO~a4SUST
         ASL A
         ASL A
         ASL A
         ASL A
         STA SEQSUST,X
NO~a4SUST  LDA #$FF
         STA RELEASE,X
         STA SRCO,X

         LDY SOUND2,X
         LDA Z3,Y
         ASL A
         BMI NO~a4RLS
         AND #$40
         BEQ NO~a4HARD
         ADC #$E0
         STA SID+6,X
         LDA #$0F
         STA SID+5,X
NO~a4HARD  LDA #$FE
         STA GATE,X
         AND WF,X
R~a4WFO5   ORA WF~a4ORA,X
         *= *-((*-R~a4WFO5)*REM~a4WFO)
         STA SID+4,X
NO~a4RLS   JMP SID~a4NEXT
RRTS     JMP COND~a4RET
         *= *-((*-RRTS)*REM~a44CH)
TIE~a4ATT  BMI R~a4WFO4
         ASL A
         ASL A
         ASL A
         ASL A
         STA ATTACK,X
         LDA #$F0
         BNE NO~a4SUST-3

R~a4WFO4   LDA WF~a4ORA2,X
         BMI BN66
         STA WF~a4ORA,X
         *= *-((*-R~a4WFO4)*REM~a4WFO)
BN66     JMP WFROUT

PART2
PULSE
;----------------------MULTI PULSE ROUT-
R~a4MP1    LDA PULSLE2,X
         BEQ PULSE3
         DEC PULSCO,X
         BNE PULSE2
         LDA PULSDEL,X
         STA PULSCO,X
         LDA PULSEOR,X
         EOR #1
         STA PULSEOR,X
PULSE2   LDA PULSEOR,X
         BEQ PULSE3
         INX
         *= *-((*-R~a4MP1)*REM~a4MP)
;----------------------PULSE PROGRAM----
PULSE3   LDA PULSLE,X
         BMI NO~a4PULSE
         BNE GO~a4PULSE
NO~a4PULSE
R~a4MP7    LDX X+1
         *= *-((*-R~a4MP7)*REM~a4MP)
         JMP GLIDE
GO~a4PULSE ASL A
         ASL A
         TAY
         STX MZERO+1
         LDA PULSDEC,X
         BNE BN22
         STA PULSHLD,X
         LDA #2
         STA PULSDEC,X
         BCS BN22
         LDA P+1-4,Y
         BNE PH1
         LDA P+2-4,Y
         STA PULSHLD,X
PH1
         LDA P-4,Y
         AND #$F0
         STA PULSLO,X
         LDA P-4,Y
         AND #$0F
         STA PULSHI,X
         JMP SET~a4PULS

BN22     LDA PULSHLD,X
         BEQ PH2
         DEC PULSHLD,X
         BNE SET~a4PULS
         BEQ PH3

PH2
         LDA P+1-4,Y
         LSR A
         LSR A
         LSR A
         LSR A
         TAX
         STX UPPER2+1
         LDA P+1-4,Y
         AND #$0F
         CMP UPPER2+1
         BCC BN24+1
         STA UPPER2+1
BN24     LDA #$AA
         STX LOWER2+1
         LDX MZERO+1
         LDA #$90
         DEC PULSDEC,X
         BNE *+4
         LDA #$B0
         STA BRANCH2
         INC PULSDEC,X
         LDA PULSLO,X
BRANCH2  BCC BN26
         CLC
         ADC P+2-4,Y
         STA PULSLO,X
         LDA PULSHI,X
         ADC #0
         STA PULSHI,X
UPPER2   CMP #0
         BCS BN29
         BCC SET~a4PULS
BN26     SEC
         SBC P+2-4,Y
         STA PULSLO,X
         LDA PULSHI,X
         SBC #0
         STA PULSHI,X
         BCC *+6
LOWER2   CMP #0
         BCS SET~a4PULS
         INC PULSHI,X
BN29     LDA #0
         STA PULSLO,X
PH3      LDA P+3-4,Y
         BPL *+5
         DEC PULSDEC,X
         DEC PULSDEC,X
         BNE SET~a4PULS
         AND #$7F
         STA PULSLE,X
;----------------------SET PULSE VALUES-
SET~a4PULS
R~a4MP5    LDA PULSLO,X
         STA SID+2,X
         LDA PULSHI,X
         STA SID+3,X
         *= *-((*-R~a4MP5)*(1-REM~a4MP))

R~a4MP6    TXA
         TAY
         LDX X+1
         LDA PULSLO,Y
         STA SID+2,X
         LDA PULSHI,Y
         STA SID+3,X
         *= *-((*-R~a4MP6)*REM~a4MP)

         *= *-((*-PULSE)*REM~a4PU)

;----------------------GLIDE ROUTINE----
GLIDE    LDA GLIDADD,X
         BMI GLIDE~a4IT
         BNE *+5
         JMP VIBRATO
         ORA #$80
         STA GLIDADD,X
         JMP GETADD
GLIDE~a4IT LDY NOTE,X
         STY MZERO+1
         LDA ADDLO,X
         CLC
         ADC FREQLO,Y
         STA MZERO
         LDA ADDHI,X
         ADC FREQHI,Y
         PHA
         LDY GLIDTO,X
         LDA MZERO
         CMP FREQLO,Y
         PLA
         SBC FREQHI,Y

BN65     LDA ADDLO,X
         BCC BN11
         SBC ADDVAL~a4L,X
         STA ADDLO,X
         LDA #$B0
         STA ADDOR
         LDA ADDHI,X
         SBC ADDVAL~a4H,X
         JMP BN19

BN11     ADC ADDVAL~a4L,X
         STA ADDLO,X
         LDA #$90
         STA ADDOR
         LDA ADDHI,X
         ADC ADDVAL~a4H,X
BN19     STA ADDHI,X
         STA MZERO

         LDA ADDLO,X
         LDX MZERO+1
         CLC
         ADC FREQLO,X
         PHP
         CMP FREQLO,Y
         LDA MZERO
         ADC FREQHI,X
         PLP
         SBC FREQHI,Y
         LDX X+1
ADDOR    BCC BN60
         TYA
         STA NOTE,X
         LDA #0
         STA GLIDADD,X
         STA ADDLO,X
         STA ADDHI,X
BN60     JMP WFROUT

         *= *-((*-GLIDE)*REM~a4GLID)

;----------------------VIBRATO ROUTINE--

VIBRATO  LDA VIBLE,X
         BEQ BN63
         ASL A
         ADC VIBLE,X
         TAY
         LDA VIBDEC,X
         BNE BN16
         STA ADDLO,X
         STA ADDHI,X
         LDA V-3,Y
R~a4DET4   BEQ DETUN
         CMP #$FE
         BEQ DETUN2
         *= *-((*-R~a4DET4)*REM~a4DET)

         STA VIBDEC,X
         LDA V+1-3,Y
         CMP #$80
         AND #$7F
         STA VIBWID,X
         ROR A
         STA VIBDIR,X
         LDA V+2-3,Y
         *= *-((*-VIBRATO)*REM~a4VIB)

GETADD   AND #$7F
         STA MZERO
         LDA NOTE,X
         LSR A
         CLC
         ADC MZERO
         CMP #$60
         BCC *+6
         AND #$1F
         ORA #$60
         TAY
         LDA #0
         BCC BN17
         LDA FREQHI-$60,Y
BN17     STA ADDVAL~a4H,X
         LDA FREQHI,Y
         STA ADDVAL~a4L,X
BN63     JMP WFROUT
         *= *-((*-BN63)*REM~a4VIB)
         *= *-((*-GETADD)*ADDSUM)

DETUN    INC VIBLE,X
DETUN2   LDA V+1-3,Y
         STA DETUNLO,X
         LDA V+2-3,Y
         STA DETUNHI,X
         JMP WFROUT
         *= *-((*-DETUN)*REM~a4DET)

BN16     CMP #$FF
         BEQ BN53
         DEC VIBDEC,X
         BNE BN53
         INC VIBLE,X
BN53
;----------------------CRAZY COMET FX---
CC1      LDA V+2-3,Y
         BPL BN59
         AND #3
ANDCOUNT AND #0
         BNE BN59
         STA FRQ~a4L+1
         BEQ WFROUT2-3

         *= *-((*-CC1)*REM~a4CC)
;----------------------ADD/SUB FREQUENCY
BN59     LDA ADDLO,X
         LDY VIBDIR,X
         BMI BN1
         CLC
         ADC ADDVAL~a4L,X
         STA ADDLO,X
         LDA ADDHI,X
         ADC ADDVAL~a4H,X
         JMP BN2
BN1      SEC
         SBC ADDVAL~a4L,X
         STA ADDLO,X
         LDA ADDHI,X
         SBC ADDVAL~a4H,X
BN2      STA ADDHI,X
         DEY
         TYA
         STA MZERO
         BIT MZERO
         BVC BN3
         EOR #$7F
         ORA VIBWID,X
BN3      STA VIBDIR,X
         *= *-((*-DETUN)*REM~a4VIB)

;----------------------SET FREQUENCIES--
WFROUT
R~a4DET5   LDA ADDLO,X
R~a4DET6   CLC
         ADC DETUNLO,X
         *= *-((*-R~a4DET6)*REM~a4DET)
         STA FRQ~a4L+1
         LDA ADDHI,X
R~a4DET7   ADC DETUNHI,X
         *= *-((*-R~a4DET7)*REM~a4DET)
         STA FRQ~a4H+1
         *= *-((*-R~a4DET5)*FRQSUM)

;----------------------WAVEFORM PROGRAM-
WFROUT2  LDY WFP,X
         LDA W,Y
         CMP #$FF
         BNE WF~a4LOOP

R~a4WFR1   LDA WF~a4REPET,X
         BEQ NOREP
         DEC WF~a4REPET,X
         BNE NOREP
         INY
         BNE WFROUT2+3
         *= *-((*-R~a4WFR1)*REM~a4WFR)
NOREP
         LDA F,Y
         TAY
         LDA W,Y
WF~a4LOOP
;----------------------PROGRAM DELAY----
R~a4WFD1   CMP #$FE
         BNE WF~a4LOOP2
         LDA F,Y
         STA WF~a4DEL,X
         INY
         TYA
         STA WFP,X
         LDA W,Y
         *= *-((*-R~a4WFD1)*REM~a4WFD)
WF~a4LOOP2
;----------------------ADSR COMMAND-----
R~a4ADSR   CMP #$FD
         BNE WF~a4LOOP3
         INY
         LDA RELEASE,X
         LSR A
         BCC NO~a4ADSR
         LDA F-1,Y
         CMP #$80
         AND #$7F
         STA GATEDEC,X
         BCS *+7
         LDA #$FF
         STA GATE,X
         LDA W,Y
         STA SID+5,X
         LDA F,Y
         STA SID+6,X
NO~a4ADSR  INY
         LDA W,Y
         *= *-((*-R~a4ADSR)*REM~a4ADSR)
WF~a4LOOP3
;----------------------MULTI PULSE------
R~a4MP2    CMP #$FB
         BNE WF~a4LOOP5
         LDA F,Y
         STA PULSLE2,X
         LDA #1
         STA PULSCO,X
         LSR A
         STA PULSDEC2,X
         INY
         LDA W,Y
         STA PULSEOR,X
         LDA F,Y
         STA PULSDEL,X
         INY
         LDA W,Y
         *= *-((*-R~a4MP2)*REM~a4MP)

;----------------------WF REPEAT--------
WF~a4LOOP5
R~a4WFR2   CMP #$FA
         BNE WF~a4LOOP4
         LDA F,Y
         STA WF~a4REPET,X
         INY
         LDA W,Y
         *= *-((*-R~a4WFR2)*REM~a4WFR)

WF~a4LOOP4 CMP #$F0
         BCC WF~a4PULS
         STA SID+$15
         INY
         LDA W,Y
         *= *-((*-WF~a4LOOP4)*REM~a4WF0)

;----------------------GET WAVEFORM-----
WF~a4PULS  CMP #$EE
         BNE WF~a4PULS2
         LDA F,Y
         STA PULSLO,X
         STA SID+2,X
         AND #$0F
         STA PULSHI,X
         BPL WF~a4PULSHI

WF~a4PULS2 CMP #$ED
         BNE WF~a4PULS3
         LDA PULSLO,X
         SEC
         SBC F,Y
         STA PULSLO,X
         STA SID+2,X
         BCS WF~a4PULSHI+3
         DEC PULSHI,X
         BCC WF~a4PULSA

WF~a4PULS3 CMP #$EC
         BNE WF~a4PULS4
         LDA PULSLO,X
         CLC
         ADC F,Y
         STA PULSLO,X
         STA SID+2,X
         BCC WF~a4PULSHI+3
         INC PULSHI,X
WF~a4PULSA LDA PULSHI,X
         JMP WF~a4PULSHI

WF~a4PULS4 CMP #$EB
         BNE WF~a4LOOP6
         LDA F,Y
         STA SID+2,X
WF~a4PULSHI
         STA SID+3,X
         INY
         LDA W,Y
         *= *-((*-WF~a4PULS)*REM~a4PUW)
WF~a4LOOP6
R~a4ARP3
         CMP #$E2
         BCS WF~a4KIK
         *= *-((*-R~a4ARP3)*REM~a4WE2)
         CMP #$90
         BCC *+4
         AND #$7F
         *= *-((*-R~a4ARP3)*REM~a4ARP)
WF~a4KIK
         STA WF,X
         AND GATE,X
R~a4WFO6   ORA WF~a4ORA,X
         *= *-((*-R~a4WFO6)*REM~a4WFO)
         STA SID+4,X
         INY

;----------------------WF DELAY COUNTER-
R~a4WFD2   LDA WF~a4DEL,X
         BEQ BN57
         DEC WF~a4DEL,X
         JMP BN572
         *= *-((*-R~a4WFD2)*REM~a4WFD)
BN57     TYA
         STA WFP,X
BN572
R~a4ARP4   BCC WF~a4STAND
;----------------------ARPEGGIO PRG-----
         LDA ARPNUM,X
         BMI WF~a4STAND
         TAY
         SEC
         LDA ARPDE,X
         SBC #$40
         BCS *+5
         LDA AD+1,Y
         STA ARPDE,X
         LDY ARPLE,X
         BCS *+5
         INC ARPLE,X
         LDA A,Y
         BPL BN48
         BCS BN48
         PHA
         LDY ARPNUM,X
         LDA AD,Y
         STA ARPLE,X
         PLA
         BNE BN48
         *= *-((*-R~a4ARP4)*REM~a4ARP)

WF~a4STAND LDA F-1,Y
         BMI BN44
BN48     CLC
         ADC NOTE,X
BN44     AND #$7F
         TAY

         LDA FREQLO,Y
FCODE    CLC
FRQ~a4L    ADC #0
         STA SID+0,X
         LDA FREQHI,Y
FRQ~a4H    ADC #0
         *= *-((*-FCODE)*FRQSUM)

FCODE2   CLC
         ADC ADDLO,X
         *= *-((*-FCODE2)*ADDSUM)
         STA SID+0,X
         LDA FREQHI,Y
FCODE3   ADC ADDHI,X
         *= *-((*-FCODE3)*ADDSUM)
         *= *-((*-FCODE2)*(1-FRQSUM))
         STA SID+1,X

SID~a4NEXT LDA CHANX,X
         BMI CC2
         TAX
         JMP PART1

CC2      INC ANDCOUNT+1
         *= *-((*-CC2)*REM~a4CC)
R~a4FAD4
FADE     LDA #0
         BEQ NOFADE
         DEC FADECO
         BPL NOFADE
         CLC
         ADC #1
         LSR A
         STA FADECO
         LDY #0
         BCC FADEDWN
VOICEON
R~a4VOFF4  LDA #0
         STA VOFF+1
         *= *-((*-R~a4VOFF4)*REM~a4VOFF)
         LDA VOL+1
         CMP #$0F
         BCC FADEUP
         STY FADE+1
         BCS NOFADE
FADEDWN  DEC VOL+1
         BPL NOFADE
R~a4VOFF5  LDA VOFF+1
         STA VOICEON+1
         STY VOFF+1
         *= *-((*-R~a4VOFF5)*REM~a4VOFF)
         STY FADE+1
FADEUP   INC VOL+1

NOFADE
         *= *-((*-R~a4FAD4)*REM~a4FAD)

R~a4FI3
SETFI    LDA #0
         BEQ FILTOK
F~a4SPD6   LDX #0
         STX FILTSPD
         *= *-((*-F~a4SPD6)*REM~a4FSPD)
         JMP FIDIR
         *= *-((*-SETFI)*REM~a44CH)
FILTOK
F~a4SPD1   DEC FILTSPD
         BMI FSPEED
         JMP FILTCH
FSPEED   LDA #0
         STA FILTSPD
         *= *-((*-F~a4SPD1)*REM~a4FSPD)

FILTLE   LDA #0
         ASL A
         BNE *+5
         JMP FILTCH
         ASL A
         TAY
FILTDEC  LDA #0
         BNE BN38
         LDA #2
         STA FILTDEC+1
         LDA #$B0
         STA BRANCH
         BCS BN38

FILTSND  LDX #0
R~a44CH4   BMI FIVOICE4
         *= *-((*-R~a44CH4)*REM~a44CH)

         LDA FI+1-4,Y  ;FRAME V2.1
         BNE *+7       ;
         LDA FI+2-4,Y  ;
         BNE *+5       ;

         LDA Z7,X
         TAX
         ASL A
         ASL A
         ASL A
         ASL A
         STA RES+1
         TXA
         AND #$F0
         STA BAND+1
FIVOICE4 LDA FI-4,Y
         STA CUTOFF+1

BN38     LDA FI+1-4,Y
         BNE *+8       ;FRAME V2.1
         LDA CUTOFF+1  ;
         JMP BN42      ;

         ASL A
         ASL A
         ASL A
         ASL A
         TAX
         STX UPPER+1
         LDA FI+1-4,Y
         AND #$F0
         CMP UPPER+1
         BCC BN43+1
         STA UPPER+1
BN43     LDA #$AA
         STX LOWER+1

CUTOFF   LDA #0
BRANCH   BCC BN39
         CLC
         ADC FI+2-4,Y
UPPER    CMP #0
         BCC BN40
         BCS BN42

BN39     SEC
         SBC FI+2-4,Y
         BCC *+6        ;217
LOWER    CMP #0
         BCS BN40
         CLC            ;217
         ADC FI+2-4,Y   ;217
BN42     LDX FI+3-4,Y
         BPL *+5
         DEC FILTDEC+1
         DEC FILTDEC+1
         BNE BN41
         STX FILTLE+1
BN41     LDX #$90
         STX BRANCH
BN40     STA CUTOFF+1

FIDIR    STA SID+$16
FILTCH   LDA #0
FILTENA  ORA #0
         *= *-((*-FILTENA)*REM~a4F20)
RES      ORA #0
         STA SID+$17
         *= *-((*-R~a4FI3)*REM~a4FI)

VOL      LDA #$0F
R~a4FI4
BAND     ORA #0
         *= *-((*-R~a4FI4)*REM~a4FI)
         STA SID+$18

R~a4VOFF6  LDA VOFF+1
         BEQ BN8
         *= *-((*-R~a4VOFF6)*REM~a4VOFF)

         DEC TEMPO+1
         BPL BN8

         DEC DURATION
         DEC DURATION+7
         DEC DURATION+14
R~a44CH3   DEC DURATION+21
         *= *-((*-R~a44CH3)*REM~a44CH)

TEM~a4PRG  LDA #0

R~a4TP     BMI TEM~a4NUM
         TAY
         LDA TEM~a4P,Y
         CLC
TEM~a4Y    ADC #0
         TAY
         LDA TEM~a4D,Y
         BPL TPL
         LDY #$FF
         STY TEM~a4Y+1
TPL      INC TEM~a4Y+1
TEM~a4NUM  AND #$7F
         *= *-((*-R~a4TP)*REM~a4TP)

         STA TEMPO+1
         CMP #3
         BCC *+4
         LDA #2
         STA CUR~a4TEM+1
BN8      RTS

;PAL TUNED FREQTABLE:
;(NTSC FREQTABLE IS ON RELEASE DISK)

FREQHI   .BYTE $01,$01,$01,$01,$01,$01
         .BYTE $01,$01,$01,$01,$01,$02
         .BYTE $02,$02,$02,$02,$02,$02
         .BYTE $03,$03,$03,$03,$03,$04
         .BYTE $04,$04,$04,$05,$05,$05
         .BYTE $06,$06,$06,$07,$07,$08
         .BYTE $08,$09,$09,$0A,$0A,$0B
         .BYTE $0C,$0D,$0D,$0E,$0F,$10
         .BYTE $11,$12,$13,$14,$15,$17
         .BYTE $18,$1A,$1B,$1D,$1F,$20
         .BYTE $22,$24,$27,$29,$2B,$2E
         .BYTE $31,$34,$37,$3A,$3E,$41
         .BYTE $45,$49,$4E,$52,$57,$5C
         .BYTE $62,$68,$6E,$75,$7C,$83
         .BYTE $8B,$93,$9C,$A5,$AF,$B9
         .BYTE $C4,$D0,$DD,$EA,$F8,$FF
FREQLO   .BYTE $16,$27,$39,$4B,$5F,$74
         .BYTE $8A,$A1,$BA,$D4,$F0,$0E
         .BYTE $2D,$4E,$71,$96,$BE,$E7
         .BYTE $14,$42,$74,$A9,$E0,$1B
         .BYTE $5A,$9C,$E2,$2D,$7B,$CF
         .BYTE $27,$85,$E8,$51,$C1,$37
         .BYTE $B4,$38,$C4,$59,$F7,$9D
         .BYTE $4E,$0A,$D0,$A2,$81,$6D
         .BYTE $67,$70,$89,$B2,$ED,$3B
         .BYTE $9C,$13,$A0,$45,$02,$DA
         .BYTE $CE,$E0,$11,$64,$DA,$76
         .BYTE $39,$26,$40,$89,$04,$B4
         .BYTE $9C,$C0,$23,$C8,$B4,$EB
         .BYTE $72,$4C,$80,$12,$08,$68
         .BYTE $39,$80,$45,$90,$68,$D6
         .BYTE $E3,$99,$00,$24,$10,$FF


INIT
R~a4VOFF7
         LDA C,X
         STA VOFF+1
R~a4FAD5   STA VOICEON+1
         *= *-((*-R~a4FAD5)*REM~a4FAD)
         *= *-((*-R~a4VOFF7)*REM~a4VOFF)

         LDA S,X
         STA TEM~a4PRG+1
         LDA #1
         STA TEMPO+1
         STA CUR~a4TEM+1

R~a4FI5    LDA FS,X
F~a4SPD2   TAY
         AND #$0F
         STA FSPEED+1
         TYA
         *= *-((*-F~a4SPD2)*REM~a4FSPD)
         LSR A
         LSR A
         LSR A
         LSR A
         STA FILTENA+1
         *= *-((*-R~a4FI5)*REM~a4FI)

R~a4FAD2   LDA FV,X
         PHA
         AND #$0F
         STA VOL+1
         *= *-((*-R~a4FAD2)*REM~a4FAD)

         LDA #$60
TRIN1    STA TRK~a4END
         *= *-((*-TRIN1)*REM~a44CH)
TRIN2    STA ACK
         *= *-((*-TRIN2)*(1-REM~a44CH))

         LDY TP,X
         LDX #CHANNELS*7
BN52     LDA VOFF+1
         AND CHANON,X
         BEQ BN74
         *= *-((*-BN52)*REM~a4VOFF)
         LDA #0
         STA TDELAY,X
         STA DUR,X
         STA SEQP,X
         STA TRANSP,X
R~a4TRKL6  STA TRACKY,X
         *= *-((*-R~a4TRKL6)*(1-REM~a4TRKL))
T40      CPX #3*7
         BCS T44
         *= *-((*-T40)*REM~a44CH)
         STA PULSLE2,X
         STA SRCO,X
R~a4FI6    STA FILTRE,X   ;FI SUBTUNE FIX
         *= *-((*-R~a4FI6)*REM~a4FI)

R~a4WFR4   STA WF~a4REPET,X
         *= *-((*-R~a4WFR4)*REM~a4WFR)
         LDA #$FE       ;217
         STA GATE,X     ;217
T44      LDA #$FE
         STA NOTE2,X
         STA DURATION,X
         STA SOUND,X
         LDA TL,Y
         STA TRKLO,X
R~a4TRKL7  STA TRACKY,X
         *= *-((*-R~a4TRKL7)*REM~a4TRKL)
         LDA TH,Y
         STA TRKHI,X
R~a4TRKL8  STA TRACKHI,X
         *= *-((*-R~a4TRKL8)*REM~a4TRKL)

         TYA
         PHA
         JSR TRACK~a4INIT
         PLA
         TAY

T43      DEY
BN74     LDA CHANX,X
         TAX
         BPL BN52

         LDX #$14
         LDA #0
         STA SID+0,X
         DEX
         BPL *-4
CC3      STA ANDCOUNT+1
         *= *-((*-CC3)*REM~a4CC)
R~a4TP2    STA TEM~a4Y+1
         *= *-((*-R~a4TP2)*REM~a4TP)

R~a4FI7    STA SETFI+1
         *= *-((*-R~a4FI7)*REM~a44CH)
F~a4SPD5   STA FILTSPD
         *= *-((*-F~a4SPD5)*REM~a4FSPD)
         STA FILTCH+1
         LDY #$07
         STY SID+$15
         *= *-((*-R~a4FI7)*REM~a4FI)

TRIN3    STA TRK~a4TRAN+1
         STA NOTE2CH4+1
         LDA #$E0
         STA TRK~a4END
         *= *-((*-TRIN3)*REM~a44CH)

TRIN4    LDA #$A9
         STA ACK
         *= *-((*-TRIN4)*(1-REM~a44CH))

R~a4FAD1   PLA
         AND #$F0
FADEOUT  STA FADE+1
         STA FADECO
         *= *-((*-R~a4FAD1)*REM~a4FAD)
         RTS
