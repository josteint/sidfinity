;       Compile with WLA-6510 (http://www.hut.fi/~vhelin/wla.html)


;*****  EDITOR DEFINES  ****************************************************

.DEFINE DEBUG           0

.DEFINE Editor          $4000

.DEFINE SCNKEY          $ff9f

.DEFINE tmpreg          $02             ; temporary register storage

.DEFINE Line            $f7             ; screen output line
.DEFINE LineH           $f8
.DEFINE edBlock         $f9             ; current block/line/note address
.DEFINE edBlockH        $fa
.DEFINE Keymap          $fb             ; current keymap (screen)
.DEFINE KeymapH         $fc
.DEFINE edSound         $fd             ; current sound address
.DEFINE edSoundH        $fe
.DEFINE Key             $ff


;*****  JOHN PLAYER EDITOR MAIN  *******************************************

.ORG    Editor
.SECTION "editor" FORCE
        sei

        lda     #$80
        sta     $028a                   ; repeat all keys
        sta     $0291                   ; disable case switching

        lda     #$80                    ; direct mode on
        sta     $9d
        lda     #$80                    ; no cursor
        sta     $cc

        lda     #$08
        cmp     $ba
        bcc     _drive
        sta     $ba
_drive:

        jsr     StopMusic
        jmp     BlockEditScreen


;*****  SOUND EDIT SCREEN  *************************************************

SoundEditScreen:
        lda     #$03
        sta.w   Screen

        jsr     InitScreen
        jsr     ShowSoundText

        lda     #SoundEditKeys&255
        sta     Keymap
        lda     #SoundEditKeys/256
        sta     KeymapH

SoundEditLoop:
        jsr     SetSndCursor
        jsr     DrawSound

        jsr     WaitKey
        sta     Key

        cmp     #$85
        beq     _nblockedit
        cmp     #$87
        beq     _nsequencer
        cmp     #$88
        beq     _nmenu

        jsr     CheckCommandKey
        jsr     CheckSoundHex
        jsr     SoundEditNoteCheck

        jmp     SoundEditLoop

_nblockedit:
        jmp     BlockEditScreen
_nsequencer:
        jmp     SequencerScreen
_nmenu:
        jmp     MenuScreen


;-----  sound preview gate off (left arrow)

SoundNoteOff:
        lda     #$fe
        sta.w   c1gate_+1
        rts


;-----  sound preview (shift + note key)

SoundEditNoteCheck:
        lda     Key
        ldy     #(Keyboard1-Keyboard0)-1

_seeksoundkey:
        cmp.w   Keyboard1,y
        beq     _soundeditnoteprev

        dey
        bpl     _seeksoundkey

_novalidsndkey:
        rts

_soundeditnoteprev:
        jsr     keytonote
        cmp     #$7c
        bcs     _novalidsndkey
        pha                                     ; note to stack

        ldy.w   CurrentSound
        lda.w   SoundLoc,y
        pha                                     ; sound to stack

        lda.w   MusicFlag
        beq     _sndprevinit
        and     #$01
        beq     _sndnoteprev
        pla
        pla
        rts                                     ; music playing, silent keys
_sndprevinit:
        ldy     #$02
        sty.w   MusicFlag
        dey
        sty.w   RasterPeak

        jsr     $1000
_sndnoteprev:
        pla
        sta.w   c1hold

        lda     #$00
        sta     $d404                           ; reset channel

        pla
        sta.w   c1note_+1
        rts


;-----  check sound hex edit

CheckSoundHex:
        lda     Key
        jsr     CheckHexKey
        beq     _sndhexedit

        rts

_sndhexedit:
        sty     $ff
        ldx.w   sndcurs

        lda.w   SndX
        lsr
        beq     seWaveform
        cmp     #$01
        beq     seArpeggio
        cmp     #$02
        beq     seFilter

seSoundParam:
        lda.w   SndY                    ; parameter under cursor
        ror
        ror
        ror
        and     #$1f
        sec
        sbc     #$02

        tay

        lda     (edSound),y
        jsr     seEdit
        sta     (edSound),y
        bcs     seDown
        rts

seWaveform:
        lda.w   WaveTab,x
        jsr     seEdit
        sta.w   WaveTab,x
        bcs     seDown
        rts

seArpeggio:
        lda.w   ArpTab,x
        jsr     seEdit
        sta.w   ArpTab,x
        bcs     seDown
        rts

seFilter:
        lda.w   FilTab,x
        jsr     seEdit
        sta.w   FilTab,x
        bcs     seDown
        rts
seDown:
        jmp     SndCursorDown


;-----  change sound parameter or sound table nybble

seEdit:
        pha

        lda.w   SndX
        ror
        bcs     _seLonybble

        lda     $ff
        rol
        rol
        rol
        rol
        and     #$f0
        sta     $ff

        pla
        and     #$0f
        ora     $ff

        inc.w   SndX
        clc
        rts

_seLonybble:
        lda     $ff
        and     #$0f
        sta     $ff

        pla
        and     #$f0

        ora     $ff

        dec.w   SndX
        sec
        rts


;-----  update sound edit screen

DrawSound:

        ldx     #$03                    ; write sound parameters
_sndplp:
        txa
        pha
        sta     $ff
        jsr     Locate

        lda     #$fd
        clc
        adc     $ff
        tay

        lda     (edSound),y

        ldy     #$23
        jsr     HexOut

        pla
        tax
        inx
        cpx     #$0e
        bne     _sndplp

        ldy     #$02
        lda     (edSound),y             ; get sound trig pos. and
        sta     $0100
        iny
        lda     (edSound),y             ; sound end
        sta     $0101

;-----  draw sound list

        ldx     #$01
_soundlines:
        txa
        pha
        jsr     Locate

        clc
        adc.w   SndScroll
        clc
        adc     #$ff

        sta     $ff

        cmp     $0100                   ; sound trig pos?
        bcc     _notsnd
        cmp     $0101                   ; check sound end then
        bcs     _notsnd

        ldx     #$0f                    ; text color: step is part of sound
        jmp     _sndcolor

_notsnd:
        ldx     #$0b                    ; text color: step not part of sound
_sndcolor:
        lda     LineH
        pha

        clc
        adc     #$d4                    ; to color ram
        sta     LineH

        txa
        ldy     #$0b
_scolorize:
        sta     (Line),y                ; colorize line
        dey
        bpl     _scolorize

        pla
        sta     LineH

        lda     $ff
        ldy     #$00
        jsr     HexOut                  ; output step number

        ldx     $ff
        lda.w   WaveTab,x
        ldy     #$04
        jsr     HexOut                  ; wave column

        ldx     $ff
        lda.w   ArpTab,x
        ldy     #$07
        jsr     HexOut                  ; arpeggio column

        ldx     $ff
        lda.w   FilTab,x
        ldy     #$0A
        jsr     HexOut                  ; filter column

        pla
        tax
        inx
        cpx     #$19
        bne     _soundlines

        rts


;-----  set sound cursor

SetSndCursor:
        lda     #$ff
        sta     $07ff

        ldx.w   SndX
        lda.w   soundeditcurs,x
        sta     $d00e
        lda.w   soundeditcurs9,x
        sta     $d010

        lda.w   SndY
        clc
        adc     #$2d
        sta     $d00f

        lda.w   SndY                    ; byte under cursor
        ror
        ror
        ror
        and     #$1f
        clc
        adc.w   SndScroll
        sta.w   sndcurs
        rts


soundeditcurs:
        .DB     $38,$40,$50,$58,$68,$70,$30,$38

soundeditcurs9:
        .DB     $60,$60,$60,$60,$60,$60,$e0,$e0


;-----  sound edit screen cursor movement

SndCursorDown:
        lda.w   SndY
        cmp     #$b8
        beq     _sndscrollup

        clc
        adc     #$08
        sta.w   SndY

        jmp     sndparamwin

_sndscrollup:
        lda.w   SndScroll
        cmp     #$28
        beq     _sndbot

        inc.w   SndScroll
_sndbot:
        rts

SndCursorUp:
        lda.w   SndY
        cmp     #$00
        beq     _sndscrolldown

        sec
        sbc     #$08
        sta.w   SndY

        jmp     sndparamwin

_sndscrolldown:
        lda.w   SndScroll
        cmp     #$00
        beq     _sndtop

        dec.w   SndScroll
_sndtop:
        rts

SndCursorLeft:
        lda.w   SndX
        beq     _sndls

        dec.w   SndX
_sndls:
        rts

SndCursorRight:
        lda.w   SndX
        cmp     #$07
        beq     _sndrs

        inc.w   SndX

sndparamwin:
        lda.w   SndX
        cmp     #$06
        bcc     _sndrs

        lda.w   SndY
        cmp     #$10
        bcs     _sndrstop

        lda     #$10
_sndrstop:
        cmp     #$60
        bcc     _sndrsbot

        lda     #$60
_sndrsbot:
        sta.w   SndY

_sndrs:
        rts


;-----  write sound edit text

ShowSoundText:
        ldy     #$00
_sndtxt:
        lda     SoundText,y
        sta     $0478,y
        lda     SoundText+$100,y
        sta     $0578,y
        iny
        bne     _sndtxt

        rts


SoundEditKeys:
        .DB     $03                     ; run/stop
        .DW     StopMusic
        .DB     $20                     ; space
        .DW     PlayBlock
        .DB     $a0                     ; shift+space
        .DW     PlayMusic

        .DB     $2b                     ; +
        .DW     NextBlock
        .DB     $2d                     ; -
        .DW     PrevBlock
        .DB     $3a                     ; ;
        .DW     PrevSound
        .DB     $3b                     ; :
        .DW     NextSound
        .DB     $2c                     ; ,
        .DW     OctaveDown
        .DB     $2e                     ; .
        .DW     OctaveUp

        .DB     $1d                     ; cursor keys
        .DW     SndCursorRight
        .DB     $9d
        .DW     SndCursorLeft
        .DB     $11
        .DW     SndCursorDown
        .DB     $91
        .DW     SndCursorUp

        .DB     $4e                     ; N
        .DW     CopySound
        .DB     $aa                     ; c= + N
        .DW     PasteSound

        .DB     $5f                     ; left arrow
        .DW     SoundNoteOff

        .DB     $ff


SndScroll:
        .DB     0
SndX:
        .DB     0
SndY:
        .DB     0
sndcurs:
        .DB     0


;*****  SEQUENCER SCREEN  **************************************************

SequencerScreen:
        lda     #$05
        sta.w   Screen

        jsr     InitScreen

        lda     #SequencerKeys&255
        sta     Keymap
        lda     #SequencerKeys/256
        sta     KeymapH

        jsr     ShowTag

SequencerLoop:
        jsr     SetSeqCursor
        jsr     DrawSequencer

        jsr     WaitKey
        sta     Key

        cmp     #$85
        beq     _sblockedit
        cmp     #$86
        beq     _ssoundedit
        cmp     #$88
        beq     _smenu

        jsr     CheckCommandKey
        jsr     CheckSeqEditKey

        jmp     SequencerLoop

_sblockedit:
        jmp     BlockEditScreen
_ssoundedit:
        jmp     SoundEditScreen
_smenu:
        jmp     MenuScreen


;-----  sequencer hex edit keys

CheckSeqEditKey:
        lda     Key
        jsr     CheckHexKey
        beq     _shexfound

        rts

_shexfound:
        ldx.w   SeqX
        beq     _shinybble

        sty     tmpreg                  ; write to seq byte low nybble
        ldx.w   seqcurs
        lda.w   Sequencer,x
        and     #$f0
        ora     tmpreg
        sta.w   Sequencer,x

        lda     #$00
        sta.w   SeqX
        lda.w   SeqY
        cmp     #$3f
        beq     _noshadv

        jmp     SeqCursorDown
_noshadv:
        rts

_shinybble:
        cpy     #$04
        bcs     _noshadv
        tya                             ; write to seq byte hi nybble
        rol
        rol
        rol
        rol
        and     #$f0
        sta     tmpreg
        ldx.w   seqcurs
        lda.w   Sequencer,x
        and     #$0f
        ora     tmpreg
        sta.w   Sequencer,x

        inc.w   SeqX
        rts


;-----  insert block

SeqInsert:
        ldy     #$3f
        cpy.w   seqcurs
        beq     _noins

        dey

_sins:
        lda.w   Sequencer,y
        sta.w   Sequencer+1,y
        dey
        cpy.w   seqcurs
        bpl     _sins

        iny
_noins:
        lda.w   CurrentBlock
        sta.w   Sequencer,y

        lda     #$00
        sta.w   SeqX
        rts


;-----  delete block

SeqDelete:
        ldy.w   seqcurs
_sdel:      
        lda.w   Sequencer+1,y
        sta.w   Sequencer,y
        iny
        cpy     #$40
        bne     _sdel

        lda     #$00
        sta.w   Sequencer+$3f

        rts



;-----  update sequencer screen

DrawSequencer:
        ldx     #$01
_seqlins:
        txa
        pha
        jsr     Locate


        clc
        adc.w   SeqScroll
        clc
        adc     #$ff

        pha
        ldy     #$00
        jsr     HexOut                  ; output step number
        pla
        tax
        lda.w   Sequencer,x
        ldy     #$04
        jsr     HexOut                  ; output sequence

        pla
        tax
        inx
        cpx     #$19
        bne     _seqlins

        rts


SetSeqCursor:
        lda     #$ff
        sta     $07ff

        lda.w   SeqX
        rol
        rol
        rol
        and     #$f8
        clc
        adc     #$38
        sta     $d00e

        lda.w   SeqY
        clc
        adc     #$2d
        sta     $d00f

        lda.w   SeqY                    ; byte under cursor
        ror
        ror
        ror
        and     #$1f
        clc
        adc.w   SeqScroll
        sta.w   seqcurs
        rts


;-----  show tag and info

ShowTag:
        ldy     #$04
_tlabl:
        lda.w   taglabel,y
        sta     $0485,y
        lda.w   nfolabel,y
        sta     $04fd,y
        dey
        bpl     _tlabl

        ldy     #$17
_twri:
        lda     $3500,y
        sta     $04ad,y
        lda     $3500+1*24,y
        sta     $04fd+1*40,y
        lda     $3500+2*24,y
        sta     $04fd+2*40,y
        lda     $3500+3*24,y
        sta     $04fd+3*40,y
        lda     $3500+4*24,y
        sta     $04fd+4*40,y
        dey
        bpl     _twri

        rts


taglabel:
        .DB     $54,$01,$07,$3a,$20     ; "Tag: "
nfolabel:
        .DB     $49,$0e,$06,$0f,$3a     ; "Info:"


;-----  edit info

EditInf:
        lda     #$5d
        sta     $d00f

        ldy     #$00
_infolines:
        tya
        pha

        lda.w   nfolins,y
        sta     $f9
        lda     #$35
        sta     $fa

        lda.w   nfolinn,y
        jsr     Locate
        ldx     #$0d

        lda     #$18
        sta     $fd
        lda     #$80
        sta     $fe

        lda     #$80                    ; cursor position
        sta     $d00e

        jsr     InputLine
        bcs     _break

        lda     $d00f                   ; cursor to next line
        clc
        adc     #$08
        sta     $d00f

        pla
        tay
        iny
        cpy     #$04
        bne     _infolines

        rts

_break:
        pla
        rts


nfolins:
        .DB     $18,$30,$48,$60
nfolinn:
        .DB     $07,$08,$09,$0a


;-----  sequencer screen cursor movement

SeqCursorDown:
        lda.w   SeqY
        cmp     #$b8
        beq     _seqscrollup

        clc
        adc     #$08
        sta.w   SeqY

        rts

_seqscrollup:
        lda.w   SeqScroll
        cmp     #$28
        beq     _seqbot

        inc.w   SeqScroll
_seqbot:
        rts

SeqCursorUp:
        lda.w   SeqY
        cmp     #$00
        beq     _seqscrolldown

        sec
        sbc     #$08
        sta.w   SeqY

        rts

_seqscrolldown:
        lda.w   SeqScroll
        cmp     #$00
        beq     _seqtop

        dec.w   SeqScroll
_seqtop:
        rts


SeqCursorLeft:
        lda     #$00
        sta.w   SeqX

        rts
SeqCursorRight:
        lda     #$01
        sta.w   SeqX

        rts



SeqScroll:
        .DB     0
SeqX:
        .DB     0
SeqY:
        .DB     0
seqcurs:
        .DB     0


SequencerKeys:
        .DB     $03                     ; run/stop
        .DW     StopMusic
        .DB     $20                     ; space
        .DW     PlayMusic
        .DB     $a0                     ; shift+space
        .DW     PlayFromHere

        .DB     $2b                     ; +
        .DW     NextBlock
        .DB     $2d                     ; -
        .DW     PrevBlock
        .DB     $3a                     ; ;
        .DW     PrevSound
        .DB     $3b                     ; :
        .DW     NextSound
        .DB     $2c                     ; ,
        .DW     OctaveDown
        .DB     $2e                     ; .
        .DW     OctaveUp

        .DB     $1d                     ; cursor keys
        .DW     SeqCursorRight
        .DB     $9d
        .DW     SeqCursorLeft
        .DB     $11
        .DW     SeqCursorDown
        .DB     $91
        .DW     SeqCursorUp

        .DB     $0d                     ; return
        .DW     SeqInsert
        .DB     $14                     ; inst/del
        .DW     SeqDelete

        .DB     $54                     ; T
        .DW     EditTag

        .DB     $49                     ; I
        .DW     EditInf

        .DB     $ff


;*****  MENU SCREEN  *******************************************************

MenuScreen:
        lda     #$07
        sta.w   Screen

        jsr     InitScreen
        jsr     ShowMenuText

        lda     #MenuKeys&255
        sta     Keymap
        lda     #MenuKeys/256
        sta     KeymapH

MenuLoop:
        jsr     WaitKey
        sta     Key

        cmp     #$85
        beq     _mblockedit
        cmp     #$86
        beq     _msoundedit
        cmp     #$87
        beq     _msequencer

        jsr     CheckCommandKey
        jmp     MenuLoop


_mblockedit:
        jmp     BlockEditScreen
_msoundedit:
        jmp     SoundEditScreen
_msequencer:
        jmp     SequencerScreen


;-----  menu screen cursor

SetMenuCursor:
        lda     #$30                    ; menu screen cursor
        sta     $d00e
        lda     #$c5
        sta     $d00f
        ;
;-----  write drive number

MenuDriveNumber:
        lda     #$10                    ; write drive number
        jsr     Locate

        ldy     #$0e
        lda     $ba
        jsr     HexOut

        rts


;-----  copy track

CopyTrack1:
        lda     #$01
        bne     CopyTrack
CopyTrack2:
        lda     #$02
        bne     CopyTrack
CopyTrack3:
        lda     #$03
        ;
CopyTrack:
        pha

        jsr     StopMusic

        lda     #copytrackmsg-menumsg
        jsr     WriteMenuMsg

        pla
        tax

        clc
        adc     #$30
        sta     $0729

        txa
        asl
        sta     edBlock

        ldx     #$00
_copyt:
        ldy     #$00
        lda     (edBlock),y
        sta.w   TrackBuffer,x

        iny
        lda     (edBlock),y
        sta.w   TrackBuffer+1,x

        lda     edBlock
        clc
        adc     #$08
        sta     edBlock

        inx
        inx
        cpx     #$40
        bne     _copyt
        
        rts


;-----  paste track

PasteTrack1:
        lda     #$01
        bne     PasteTrack
PasteTrack2:
        lda     #$02
        bne     PasteTrack
PasteTrack3:
        lda     #$03
        ;
PasteTrack:
        ldx.w   Screen
        cpx     #$07
        bne     _notrackmsg

        pha

        lda     #pastetrackmsg-menumsg
        jsr     WriteMenuMsg

        pla
        tax

        clc
        adc     #$30
        sta     $0733

        txa

_notrackmsg:
        asl
        sta     edBlock

        jsr     StopMusic


        ldx     #$00
_pastet:
        ldy     #$00
        lda.w   TrackBuffer,x
        sta     (edBlock),y

        iny
        lda.w   TrackBuffer+1,x
        sta     (edBlock),y

        lda     edBlock
        clc
        adc     #$08
        sta     edBlock

        inx
        inx
        cpx     #$40
        bne     _pastet
        
        lda.w   Screen
        cmp     #$01
        beq     _trackupdate

        rts

_trackupdate:
        jmp     InitNewBlock


;-----  copy sound

CopySound:
        jsr     StopMusic

        lda.w   Screen
        cmp     #$07
        bne     _nosndcmsg

        lda     #copysoundmsg-menumsg
        jsr     WriteMenuMsg

_nosndcmsg:
        ldy     #$00
_copys:
        lda     (edSound),y
        sta.w   SoundBuffer,y
        iny
        cpy     #$0b
        bne     _copys

        rts


;-----  paste sound

PasteSound:
        jsr     StopMusic

        lda.w   Screen
        cmp     #$07
        bne     _nosndpmsg

        lda     #pastesoundmsg-menumsg
        jsr     WriteMenuMsg

        ldy     #19
        lda.w   CurrentSound
        jsr     HexOut

_nosndpmsg:
        ldy     #$00
_pastes:
        lda.w   SoundBuffer,y
        sta     (edSound),y
        iny
        cpy     #$0b
        bne     _pastes

        rts


;-----  transpose block up

TransposeUp:
        jsr     StopMusic

        lda.w   Screen
        cmp     #$07
        bne     _skiptumsg

        lda     #transupmsg-menumsg
        jsr     WriteMenuMsg

_skiptumsg:
        lda     #$00
        sta     edBlock
        tay

_transupbl:
        tya
        and     #$07
        beq     _uskipc                 ; don't transpose commands

        lda     (edBlock),y
        beq     _uskipc                 ; don't transpose empties
        bmi     _uskipc                 ; don't transpose note offs etc.
        cmp     #$7a
        beq     _uskipc                 ; don't wrap to badsie note

        clc
        adc     #$02

        sta     (edBlock),y
_uskipc:
        iny
        iny
        bne     _transupbl

        lda.w   Screen
        cmp     #$01
        beq     _transupdate

        rts

_transupdate:
        jmp     InitNewBlock


;-----  transpose block down

TransposeDown:
        jsr     StopMusic

        lda.w   Screen
        cmp     #$07
        bne     _skiptdmsg

        lda     #transdownmsg-menumsg
        jsr     WriteMenuMsg

_skiptdmsg:
        lda     #$00
        sta     edBlock
        tay

_transdownbl:
        tya
        and     #$07
        beq     _dskipc                 ; don't transpose commands

        lda     (edBlock),y
        beq     _dskipc                 ; don't transpose empties
        bmi     _dskipc                 ; don't transpose note offs etc.
        cmp     #$02
        beq     _dskipc                 ; don't wrap to badsie note

        clc
        adc     #$fe

        sta     (edBlock),y
_dskipc:
        iny
        iny
        bne     _transdownbl

        lda.w   Screen
        cmp     #$01
        beq     _transupdate

        rts


;-----  copy block

CopyBlock:
        jsr     StopMusic

        lda     #copyblockmsg-menumsg
        jsr     WriteMenuMsg

        lda     #$00
        sta     edBlock
        tay

_copybl:
        lda     (edBlock),y
        sta.w   BlockBuffer,y
        iny
        bne     _copybl

        rts


;-----  paste block

PasteBlock:
        jsr     StopMusic

        lda.w   Screen
        cmp     #$07
        bne     _nopastemsg

        lda     #pasteblockmsg-menumsg
        jsr     WriteMenuMsg

        ldy     #19
        lda.w   CurrentBlock
        jsr     HexOut

_nopastemsg:
        lda     #$00
        sta     edBlock
        tay

_pastebl:
        lda.w   BlockBuffer,y
        sta     (edBlock),y
        iny
        bne     _pastebl

        lda.w   Screen
        cmp     #$01
        beq     _pasteupdate

        rts

_pasteupdate:
        jmp     InitNewBlock


menumsg:
copysoundmsg:
        .DB     "sOUND cOPIED",0
pastesoundmsg:
        .DB     "pASTED TO sOUND",0
copyblockmsg:
        .DB     "bLOCK cOPIED",0
pasteblockmsg:
        .DB     "pASTED TO bLOCK",0
copytrackmsg:
        .DB     "tRACK   cOPIED",0
pastetrackmsg:
        .DB     "pASTED TO tRACK",0
savemusicmsg:
        .DB     "sAVE mUSIC dATA ($0000 BYTES)",0
loadmusicmsg:
        .DB     "lOAD mUSIC dATA",0
savefinalmsg:
        .DB     "sAVE pACKED ($0000 INCL. PLAYER)",0
transupmsg:
        .DB     "bLOCK tRANSPOSED uP",0
transdownmsg:
        .DB     "bLOCK tRANSPOSED dOWN",0
filenamemsg:
        .DB     "fILENAME:",0
saveexemsg:
        .DB     "sAVE eXECUTABLE",0


;-----  write out message in menu screen

WriteMenuMsg:
        pha

        jsr     WipeMsg
        lda     #$14
        jsr     Locate

        pla
writeotherentry:
        tax
        ldy     #$03
_msgout:
        lda.w   menumsg,x
        beq     _msgend

        cmp     #$60
        bcc     _noupcase

        sec
        sbc     #$20
        jmp     _upcase
_noupcase:
        and     #$3f
_upcase:
        sta     (Line),y
        iny
        inx
        jmp     _msgout

_msgend:
        lda     #$cd
        sta     $d00f
        rts


;-----  wipe message lines

WipeMsg:
        lda     #$14
        jsr     Locate
        ldy     #$4f
        lda     #$20

_wipemsg:
        sta     (Line),y
        dey
        bne     _wipemsg

        jmp     SetMenuCursor


;----   pack music

PackMusic:
        jsr     BlockPack               ; pack block data

        ldy     #$00
_pcopysnd:
        lda     $1400,y                 ; copy sounds from unpacked music
        sta     $6400,y
        lda     $14c0,y
        sta     $64c0,y
        lda.w   PackPlayer,y
        sta     $6000,y
        lda.w   PackPlayer+$0100,y
        sta     $6100,y
        lda.w   PackPlayer+$0200,y
        sta     $6200,y
        lda.w   PackPlayer+$0300,y
        sta     $6300,y
        iny
        bne     _pcopysnd

        rts


;-----  swap memory ($1000-$37ff with $6000-$97ff)

SwapMemory:
        lda     #$60
        sta     sourceh
        lda     #$10
        sta     desth

        ldy     #$00
        sty     dest
        sty     source

_swaplp:
        lda     (source),y
        tax
        lda     (dest),y
        sta     (source),y
        txa
        sta     (dest),y

        iny
        bne     _swaplp

        inc     sourceh
        inc     desth
        lda     desth
        cmp     #$38
        bne     _swaplp

        rts


;-----  save executable

SaveExecutable:
        jsr     StopMusic
        jsr     PackMusic

        lda     #saveexemsg-menumsg
        jsr     WriteMenuMsg

        jsr     GetFilename
        beq     _nonameexe

        pha

        ldy     #$5f
_copyscroll:
        lda     $3518,y
        sta.w   xpscroller,y
        dey
        bpl     _copyscroll

        ldy     #$17
_copytag:
        lda     $3500,y
        sta.w   xptoptext,y
        dey
        bpl     _copytag

        lda     #$00
        tay
_clrbuff:
        sta     $0c00,y                 ; clear the other screen buffer
        sta     $0d00,y                 ; used by help browser
        sta     $0e00,y
        sta     $0f00,y
        iny
        bne     _clrbuff

        jsr     SwapMemory

        lda     #$01
        sta     source
        lda     #$08
        sta     sourceh

        lda     #$ad                    ; opcode for lda $nnnn
        sta     $080d

        jsr     PrepareTextMode
        pla

        jsr     SaveFile

        lda     #13
        jsr     CHROUT

        jsr     DiskStatus
        jsr     SwapMemory
        jsr     TextWaitKey

        lda     #$4c                    ; jmp back
        sta     $080d

        jsr     RestoreMenuText
        jmp     UpdateTop

_nonameexe:
        jsr     WipeMsg
        jmp     UpdateTop


;-----  save packed final

SavePacked:
        jsr     StopMusic
        jsr     PackMusic

        lda     #savefinalmsg-menumsg
        jsr     WriteMenuMsg

        ldy     #$11
        lda.w   dataendh
        sec
        sbc     #$10
        jsr     HexOut

        ldy     #$13
        lda.w   dataend
        jsr     HexOut

        jsr     GetFilename
        beq     _nonamefin

        pha
        jsr     SwapMemory

        lda     #$00
        sta     source
        lda     #$10
        sta     sourceh

        jsr     PrepareTextMode
        pla

        jsr     SaveFile

        lda     #13
        jsr     CHROUT

        jsr     DiskStatus
        jsr     SwapMemory
        jsr     TextWaitKey

        jsr     RestoreMenuText
        jmp     UpdateTop

_nonamefin:
        jsr     WipeMsg
        jmp     UpdateTop


;-----  save music

SaveMusic:
        jsr     StopMusic
        jsr     MusicPack

        lda     #savemusicmsg-menumsg
        jsr     WriteMenuMsg

        ldy     #$15
        lda.w   dataendh
        sec
        sbc     #$60
        jsr     HexOut

        ldy     #$17
        lda.w   dataend
        jsr     HexOut

        jsr     GetFilename
        beq     _nonamesav

        pha
        lda     #$00
        sta     source
        lda     #$60
        sta     sourceh

        jsr     PrepareTextMode
        pla

        jsr     SaveFile

        lda     #13
        jsr     CHROUT

        jsr     DiskStatus
        jsr     TextWaitKey

        jsr     RestoreMenuText
        jmp     UpdateTop

_nonamesav:
        jsr     WipeMsg
        jmp     UpdateTop

        rts


;-----  load music

LoadMusic:
        jsr     StopMusic

        lda     #loadmusicmsg-menumsg
        jsr     WriteMenuMsg

        jsr     GetFilename
        beq     _nonameload

        pha
        jsr     PrepareTextMode
        pla

        jsr     LoadFile

        lda     #13
        jsr     CHROUT

        jsr     DiskStatus
        jsr     MusicUnpack
        ; file format check here?
        jsr     TextWaitKey

        jsr     RestoreMenuText
        jmp     UpdateTop

_nonameload:
        jsr     WipeMsg
        jmp     UpdateTop


;-----  show disk status

ShowStatus:
        jsr     PrepareTextMode
        jsr     DiskStatus

        jsr     TextWaitKey
        jsr     RestoreMenuText

        rts


;-----  show dir

ShowDir:
        jsr     PrepareTextMode
        jsr     DiskDir
        jsr     DiskStatus

        jsr     TextWaitKey
        jsr     RestoreMenuText

        rts


HelpScreen:
        jsr     StopMusic
        lda     #$00

        sta     $d015
        jsr     ClearScreenAll

        lda     #$10
        sta     $d011

        jsr     Help

        jsr     RestoreMenuText
        rts


PrepareTextMode:
        jsr     StopMusic

        lda     #$00
        sta     $d015
        sta     $d020

        jsr     ClearScreenAll


        lda     #147
        jsr     CHROUT
        lda     #155
        jsr     CHROUT

        cli
        rts


TextWaitKey:
_waitkey:
        lda     $c6
        beq     _waitkey

        lda     #$00
        sta     $c6
        rts


RestoreMenuText:
        sei

        lda     #$0b
        sta     $d020

        jsr     InitScreen
        jsr     ShowMenuText

        rts


;-----  change drive

ChangeDrive:
        jsr     StopMusic

        inc     $ba
        lda     $ba
        and     #$03                    ; change to $07, $0f, $1f
        clc                             ; for more devices
        adc     #$08
        sta     $ba

        jmp     MenuDriveNumber


;-----  get filename

GetFilename:
        lda     #$15
        jsr     Locate

        lda     #filenamemsg-menumsg
        jsr     writeotherentry

        lda     #$04                    ; same as edBlock $f9-$fa
        sta     $f9
        lda     #$01
        sta     $fa

        lda     #$10
        sta     $fd
        lda     #$00                    ; no cursor keys
        sta     $fe

        lda     #$15
        jsr     Locate
        ldx     #$0c                    ; first column

        lda     #$78                    ; cursor position
        sta     $d00e

        jmp     InputLine


;-----  edit tag

EditTag:
        lda     #$00
        sta     $f9
        lda     #$35
        sta     $fa

        lda     #$18
        sta     $fd
        lda     #$80
        sta     $fe

        lda     #$04
        jsr     Locate
        ldx     #$0d

        lda     #$80                    ; cursor position
        sta     $d00e
        lda     #$45
        sta     $d00f

        jmp     InputLine


;-----  general input line routine (16 characters max)
;       first screen location in (Line)
;       memory write address in ($f9)
;       max length in $fd
;       cursor left/right flag $fe ($80 = enabled)

InputLine:
        txa
        clc
        adc     Line
        sta     Line
        lda     LineH
        adc     #$00
        sta     LineH

        lda     #$00                    ; character
        sta     tmpreg

_waitnamekey:
        jsr     WaitKey
        ldy     tmpreg

        cmp     #3                      ; run/stop
        beq     _nameexit

        cmp     #13                     ; return
        beq     _nameenter

        cmp     #20                     ; del
        beq     _namedel

        ldx     $fe                     ; check cursor key flag
        beq     _nocursors

        cmp     #$1d                    ; cursor keys (and badsies) enabled
        beq     _crmoveright
        cmp     #$9d
        bne     _writechar

_crmoveleft:
        cpy     #$00
        beq     _namenext
        jsr     _cursorleft
        jmp     _namenext

_nocursors:
        cmp     #42                     ; no cursor keys and no characters
        beq     _waitnamekey            ; that might confuse cbm dos
        cmp     #58
        beq     _waitnamekey
        cmp     #63
        beq     _waitnamekey
        cmp     #64
        beq     _waitnamekey

_writechar:
        cmp     #32                     ; character range
        bcc     _waitnamekey
        cmp     #91
        bcs     _waitnamekey
        
        cpy     $fd                     ; maximum file name length
        beq     _waitnamekey

        sta     (Line),y
        sta     ($f9),y

        jsr     _cursorright

_namenext:
        sty     tmpreg
        jmp     _waitnamekey

_namedel:
        cpy     #$00
        beq     _waitnamekey

        jsr     _cursorleft

        lda     #$20
        sta     (Line),y
        sta     ($f9),y

        jmp     _namenext

_crmoveright:
        cpy     $fd
        beq     _namenext
        jsr     _cursorright
        jmp     _namenext

_nameenter:
        lda     #$60
        sta     $d010
        clc                             ; no break
        tya
        rts
_nameexit:
        lda     #$60
        sta     $d010
        sec                             ; break flag
        lda     #$00
        rts


_cursorright:
        iny

        lda     $d00e
        clc
        adc     #$08
        sta     $d00e
        bcc     _cursnoca
        lda     #$e0
        sta     $d010
_cursnoca:
        rts


_cursorleft:
        dey

        lda     $d00e
        sec
        sbc     #$08
        sta     $d00e
        bcs     _cursnocb
        lda     #$60
        sta     $d010
_cursnocb:
        rts


MenuKeys:
        .DB     $03                     ; run/stop
        .DW     StopMusic
        .DB     $20                     ; space
        .DW     PlayMusic
        .DB     $a0                     ; shift+space
        .DW     PlayBlock

        .DB     $2b                     ; +
        .DW     NextBlock
        .DB     $2d                     ; -
        .DW     PrevBlock
        .DB     $3a                     ; ;
        .DW     PrevSound
        .DB     $3b                     ; :
        .DW     NextSound
        .DB     $2c                     ; ,
        .DW     OctaveDown
        .DB     $2e                     ; .
        .DW     OctaveUp

        .DB     $50                     ; P
        .DW     SavePacked

        .DB     $53                     ; S
        .DW     SaveMusic

        .DB     $4C                     ; L
        .DW     LoadMusic

        .DB     $24                     ; $
        .DW     ShowDir

        .DB     $40                     ; @
        .DW     ShowStatus

        .DB     $4e                     ; N
        .DW     CopySound
        .DB     $aa                     ; c= + N
        .DW     PasteSound

        .DB     $42                     ; B
        .DW     CopyBlock
        .DB     $bf                     ; c= + B
        .DW     PasteBlock

        .DB     $31                     ; 1
        .DW     CopyTrack1
        .DB     $81                     ; c= + 1
        .DW     PasteTrack1

        .DB     $32                     ; 2
        .DW     CopyTrack2
        .DB     $95                     ; c= + 2
        .DW     PasteTrack2

        .DB     $33                     ; 3
        .DW     CopyTrack3
        .DB     $96                     ; c= + 3
        .DW     PasteTrack3

        .DB     $48                     ; H
        .DW     HelpScreen

        .DB     $56                     ; V
        .DW     ChangeDrive

        .DB     $55                     ; U
        .DW     TransposeUp

        .DB     $44                     ; D
        .DW     TransposeDown

        .DB     $58                     ; X
        .DW     SaveExecutable

        .DB     $ff


;*****  BLOCK EDIT SCREEN  *************************************************

BlockEditScreen:
        lda     #$01
        sta.w   Screen

        jsr     InitScreen

        lda     #BlockEditKeys&255
        sta     Keymap
        lda     #BlockEditKeys/256
        sta     KeymapH

        jsr     InitNewBlock


BlockEditLoop:
        jsr     SetBlockCursor
        jsr     WaitKey
        sta     Key

.IF DEBUG == 1
        sta     $0400
.ENDIF

        cmp     #$86
        beq     _bsoundedit
        cmp     #$87
        beq     _bsequencer
        cmp     #$88
        beq     _bmenu

        jsr     CheckNoteKey
        jsr     CheckCommandKey

.IF DEBUG == 1
        lda     #$06
        sta     $d020
.ENDIF
        jmp     BlockEditLoop


_bsoundedit:
        jmp     SoundEditScreen
_bsequencer:
        jmp     SequencerScreen
_bmenu:
        jmp     MenuScreen


BlockEditKeys:
        .DB     $03                     ; run/stop
        .DW     StopMusic
        .DB     $20                     ; space
        .DW     PlayBlock

        .DB     $2b                     ; +
        .DW     NextBlock
        .DB     $2d                     ; -
        .DW     PrevBlock
        .DB     $3a                     ; ;
        .DW     PrevSound
        .DB     $3b                     ; :
        .DW     NextSound
        .DB     $2c                     ; ,
        .DW     OctaveDown
        .DB     $2e                     ; .
        .DW     OctaveUp

        .DB     $1d                     ; cursor keys
        .DW     BlockCursorRight
        .DB     $9d
        .DW     BlockCursorLeft
        .DB     $11
        .DW     BlockCursorDown
        .DB     $91
        .DW     BlockCursorUp

        .DB     $14                     ; inst/del
        .DW     BlockDeleteKey
        .DB     $5f                     ; left arrow
        .DW     BlockNoteOff

        .DB     $13                     ; home
        .DW     GotoBlockTop

        .DB     $81                     ; c= + 1
        .DW     PasteTrack1
        .DB     $95                     ; c= + 2
        .DW     PasteTrack2
        .DB     $96                     ; c= + 3
        .DW     PasteTrack3
        .DB     $bf                     ; c= + B
        .DW     PasteBlock
        .DB     $ac                     ; c= + D
        .DW     TransposeDown
        .DB     $b8                     ; c= + U
        .DW     TransposeUp

        .DB     $ff


;-----  go to top of block

GotoBlockTop:
        lda     #$00
        sta.w   BlockY
        sta.w   BlockX
        sta.w   BlockScroll
        jsr     InitNewBlock
        rts


;-----  delete note

BlockDeleteKey:
        lda     edBlock
        cmp     #$f8
        beq     _baddel                 ; don't delete end mark

        lda     #$00
        tay
        sta     (edBlock),y
        iny
        sta     (edBlock),y
        jmp     UpdateNoteAdvance

_baddel:
        rts


;-----  note off

BlockNoteOff:
        lda.w   BlockX
        cmp     #$03
        beq     _badnoteoff             ; channels only

        lda     #$fe
        ldy     #$00
        sta     (edBlock),y
        tya
        iny
        sta     (edBlock),y
        jsr     NotePlay

        jmp     UpdateNoteAdvance

_badnoteoff:
        rts


;-----  check command column key

CheckCmdEdit:
        lda     edBlock
        cmp     #$f8
        beq     _badcmdentry            ; don't overwrite block end mark

        ldy     #$08
        lda     Key
_seekcmdkey:
        cmp.w   _cmdkeymap-2,y          ; starting from cmd 2: Brk
        beq     _cmdentry               ; cmd entered
        dey
        bpl     _seekcmdkey

        ldy     #$00                    ; does current cmd have a param?
        lda     (edBlock),y
        cmp     #$03
        bcc     _badcmdentry

_hexparam:
        lda     Key
        jsr     CheckHexKey
        beq     _hexfound
_badcmdentry:
        rts

_cmdkeymap:
        .DB     $c2,$c6,$d4,$c9,$d6,$cd,$cf

_cmdentry:
        tya
        ldy     #$00
        sta     (edBlock),y             ; write cmd to block
        sty     Key

        jmp     UpdateNoteAdvance

_hexfound:
        tya
        rol
        rol
        rol
        rol
        and     #$f0
        sta     tmpreg

        ldy     #$01                    ; write parameter high nybble
        lda     (edBlock),y
        and     #$0f
        ora     tmpreg
        sta     (edBlock),y

        lda     #$04
        sta.w   BlockX                  ; cursor to low nybble

        jmp     UpdateNote              ; update but don't move

CheckLowNybble:
        dex
        stx.w   BlockX

        jsr     CheckHexKey
        beq     _hexlonybble

        rts

_hexlonybble:
        sty     tmpreg

        ldy     #$01
        lda     (edBlock),y
        and     #$f0
        ora     tmpreg
        sta     (edBlock),y

        jmp     UpdateNoteAdvance


;-----  check note edit key

CheckNoteKey:
        ldx.w   BlockX
        cpx     #$03
        beq     CheckCmdEdit
        cpx     #$04
        beq     CheckLowNybble

        ldy     #(Keyboard1-Keyboard0)-1

_seeknotekey:
        cmp.w   Keyboard0,y
        beq     _notekeydown
        cmp.w   Keyboard1,y
        beq     _shiftednotekeydown

        dey
        bpl     _seeknotekey

_novalidkey:
        rts

_shiftednotekeydown:
        jsr     keytonote
        cmp     #$7c
        bcs     _novalidkey
        ldy     #$00
        sta     (edBlock),y                     ; write note
        tya                                     ; sound $00 (tied note)
        jmp     _notekeyedit

_notekeydown:
        jsr     keytonote
        cmp     #$7c
        bcs     _novalidkey
        ldy     #$00
        sta     (edBlock),y                     ; write note

        ldy.w   CurrentSound
        lda.w   SoundLoc,y

_notekeyedit:
        ldy     #$01
        sta     (edBlock),y                     ; write sound number

        lda     #$00
        sta     Key

        jsr     NotePlay
        jmp     UpdateNoteAdvance


;-----  convert note key index to actual note in current octave

keytonote:
        tya
        asl
        ldy.w   CurrentOctave
        clc
        adc.w   OctaveBase-1,y

        rts
        

;-----  update note and advance cursor

UpdateNoteAdvance:
        jsr     UpdateNote
        jmp     BlockCursorDown


;-----  update note

UpdateNote:
        lda.w   BlockY                          ; cursor screen line
        ror
        ror
        ror
        clc
        adc     #$01
        and     #$1f

        jsr     WriteLine                       ; update line
        rts


;-----  play note during edit

NotePlay:
        lda.w   MusicFlag
        beq     _noteplayinit
        and     #$01
        beq     _notepreview
        rts                                     ; music playing, silent edit

_noteplayinit:
        ldy     #$02
        sty.w   MusicFlag                       ; first note play
        dey
        sty.w   RasterPeak

        jsr     $1000

_notepreview:
        lda.w   BlockX                          ; use current channel
        cmp     #$02
        beq     _notec3
        cmp     #$01
        beq     _notec2

_notec1:
        ldy     #$00
        lda     (edBlock),y
        bpl     _prevnotie1

        sta.w   c1gate_+1                       ; must be $fe (gate off mask)
        rts

_prevnotie1:
        sta.w   c1note_+1
        iny
        lda     (edBlock),y
        beq     _prevdone1

        sta     c1hold
        lda     #$00
        sta     $d404                           ; reset channel
_prevdone1:
        rts

_notec2:
        ldy     #$00
        lda     (edBlock),y
        bpl     _prevnotie2

        sta.w   c2gate_+1                       ; must be $fe (gate off mask)
        rts

_prevnotie2:
        sta.w   c2note_+1
        iny
        lda     (edBlock),y
        beq     _prevdone2

        sta     c2hold
        lda     #$00
        sta     $d404+7                         ; reset channel
_prevdone2:
        rts

_notec3:
        ldy     #$00
        lda     (edBlock),y
        bpl     _prevnotie3

        sta.w   c3gate_+1                       ; must be $fe (gate off mask)
        rts

_prevnotie3:
        sta.w   c3note_+1
        iny
        lda     (edBlock),y
        beq     _prevdone3

        sta     c3hold
        lda     #$00
        sta     $d404+14                        ; reset channel
_prevdone3:
        rts


;-----  draw new block on screen

InitNewBlock:
        jsr     StopMusic

        ldx     #$01

_blines:
        txa
        pha
        jsr     WriteLine
        pla
        tax
        inx
        cpx     #$19
        bne     _blines

        rts


;-----  write block edit screen line a

WriteLine:
        jsr     Locate                  ; screen line

        clc
        adc.w   BlockScroll             ; scroll position
        clc
        adc     #$ff

        pha
        rol                             ; calculate block line address
        rol
        rol
        and     #$f8
        sta     edBlock
        pla

        ldy     #$00                    ; output step number
        jsr     HexOut


        ldy     #$02
        lda     (edBlock),y             ; get c1 note

        ldy     #$06
        jsr     NoteOut                 ; output c1 note

        ldy     #$03
        lda     (edBlock),y             ; get c1 sound
        tay
        lda     SoundConv,y
        bne     _c1sound

        lda     #$20
        ldy     #$06+4
        sta     (Line),y                ; no sound, output spaces
        iny
        sta     (Line),y

        jmp     _c1outok

_c1sound:
        ldy     #$06+4
        jsr     HexOut                  ; output c1 sound
_c1outok:


        ldy     #$04
        lda     (edBlock),y             ; get c2 note

        ldy     #$0f
        jsr     NoteOut                 ; output c2 note

        ldy     #$05
        lda     (edBlock),y             ; get c2 sound
        tay
        lda     SoundConv,y
        bne     _c2sound

        lda     #$20
        ldy     #$0f+4
        sta     (Line),y                ; no sound, output spaces
        iny
        sta     (Line),y

        jmp     _c2outok

_c2sound:
        ldy     #$0f+4
        jsr     HexOut                  ; output c2 sound
_c2outok:


        ldy     #$06
        lda     (edBlock),y             ; get c3 note

        ldy     #$18
        jsr     NoteOut                 ; output c3 note

        ldy     #$07
        lda     (edBlock),y             ; get c3 sound
        tay
        lda     SoundConv,y
        bne     _c3sound

        lda     #$20
        ldy     #$18+4
        sta     (Line),y                ; no sound, output spaces
        iny
        sta     (Line),y

        jmp     _c3outok

_c3sound:
        ldy     #$18+4
        jsr     HexOut                  ; output c1 sound
_c3outok:


        ldy     #$00
        lda     (edBlock),y             ; get cmd
        pha

        ldy     #$21
        jsr     CmdOut
        iny

        pla
        cmp     #$03                    ; 0-2: have no parameter
        bcc     _cmdnopar

_cmdpar:
        ldy     #$01
        lda     (edBlock),y             ; get cmd parameter

        ldy     #$21+4
        jsr     HexOut

        jmp     _cmdoutok

_cmdnopar:
        lda     #$20
        ldy     #$21+4
        sta     (Line),y                ; no parameter
        iny
        sta     (Line),y

_cmdoutok:

        rts


;-----  block cursor movement

BlockCursorUp:
        lda.w   BlockY
        beq     _blockscrollup
        clc
        adc     #$f8
        sta.w   BlockY
        rts

BlockCursorDown:
        lda.w   BlockY
        clc
        adc     #$08
        cmp     #$08*24
        beq     _blockscrolldown
        sta.w   BlockY
        rts

BlockCursorLeft:
        ldx.w   BlockX
        dex
        cpx     #$ff
        bne     _blockxset
        rts

_blockxset:
        stx.w   BlockX
        rts

BlockCursorRight:
        ldx.w   BlockX
        inx
        cpx     #$04
        bne     _blockxset
        rts

_blockscrollup:
        lda.w   BlockScroll
        beq     _bnoscroll
        dec.w   BlockScroll

        ldx     #$00
        jsr     ScrollDown

        lda     #$01
        jmp     WriteLine

_bnoscroll:
        rts

_blockscrolldown:
        lda.w   BlockScroll
        cmp     #$08
        beq     _bnoscroll
        inc.w   BlockScroll

        ldx     #$00
        jsr     ScrollUp

        lda     #$18
        jmp     WriteLine


;-----  set block cursor sprite in place

SetBlockCursor:
        lda.w   BlockY
        clc
        adc     #$2d
        sta     $d00f

        ldy.w   BlockX
        lda.w   _blockcursorx,y
        sta     $d00e
        lda.w   _blockcursor9,y
        sta     $d010
        lda.w   _blockcursorsh,y
        sta     $07ff

        lda.w   BlockScroll                     ; calculate note address
        rol
        rol
        rol
        and     #$f8
        clc
        adc.w   BlockY

        ldy.w   BlockX
        clc
        adc.w   _findnotecol,y
        sta     edBlock                         ; low byte

.IF DEBUG == 1
        ldy     #$00
        lda     (edBlock),y
        sta     $0401
.ENDIF

        rts


_blockcursorx:
        .DB     $48,$90,$d8,$20,$48             ; $d00e
_blockcursor9:
        .DB     $60,$60,$60,$e0,$e0             ; $d010
_blockcursorsh:
        .DB     $fe,$fe,$fe,$fe,$ff             ; $07ff

_findnotecol:
        .DB     $02,$04,$06,$00,$00             ; c1, c2, c3, cmd



;-----  check key and execute command

CheckCommandKey:
        ldy     #$00

_seekkey:
        lda     (Keymap),y              ; check keymap end mark
        cmp     #$ff
        beq     _nokeyfound

        cmp     Key                     ; compare with key
        beq     _keyfound

        iny
        iny
        iny
        jmp     _seekkey

_keyfound:
        iny
        lda     (Keymap),y
        sta.w   _keyjump+1
        iny
        lda     (Keymap),y
        sta.w   _keyjump+2

_keyjump:
        jmp     $0000                   ; rts there

_nokeyfound:
        rts


;-----  stop music

StopMusic:
        lda.w   MusicFlag               ; already stopped?
        beq     _stopped
        jsr     $1000                   ; shut up sid
        lda     #$00
        sta.w   MusicFlag
_stopped:
        rts


;-----  play block

PlayBlock:
        lda.w   MusicFlag
        and     #$01
        bne     _playing
        lda     #$03
_initblockplay:
        jmp     _initplay


;       MusicFlag(s)
;       %00     silence
;       %01     music playing, don't retrig
;       %10     sound preview, can start music playing if requested
;       %11     block playing, don't retrig

;-----  play music

PlayMusic:
        lda.w   MusicFlag               ; already playing?
        and     #$01
        bne     _playing
        lda     #$01
_initplay:                              
        sta.w   MusicFlag
        lda     #$00
        sta.w   RasterPeak
        jsr     $1000                   ; shut up sid & init music
_playing:
        rts


;-----  play starting at current sequencer position

PlayFromHere:
        lda.w   MusicFlag
        and     #$01
        bne     _playing

        lda     #$01
        jsr     _initplay

        ldy.w   seqcurs
        lda.w   Sequencer,y             ; check requested starting pos
        beq     _badsiepos        

        sty     seqpos

        clc
        adc     #(BlockData/256)-1
        sta     block

_badsiepos:
        rts


;-----  next block

NextBlock:
        lda.w   MusicFlag
        cmp     #$03
        bne     _notbpa
        jsr     StopMusic

_notbpa:
        ldx.w   CurrentBlock
        inx
        cpx     #$20
        bne     _blockchange
        rts

_blockchange:
        stx.w   CurrentBlock
        jsr     UpdateTop

        lda.w   Screen
        cmp     #$01
        bne     _noblockdraw

        jmp     InitNewBlock            ; rts there

_noblockdraw:
        rts


;-----  previous block

PrevBlock:
        lda.w   MusicFlag
        cmp     #$03
        bne     _notbpb
        jsr     StopMusic

_notbpb:
        ldx.w   CurrentBlock
        dex
        cpx     #$00
        bne     _blockchange
        rts


;-----  next sound

NextSound:
        ldx.w   CurrentSound
        inx
        cpx     #$15
        bne     _soundchange
        rts

_soundchange:
        stx.w   CurrentSound
        jsr     UpdateTop
        rts


;-----  previous sound

PrevSound:
        ldx.w   CurrentSound
        dex
        cpx     #$00
        bne     _soundchange
        rts


;-----  octave up

OctaveUp:
        ldx.w   CurrentOctave
        inx
        cpx     #$05
        bne     _octavechange
        rts

_octavechange:
        stx.w   CurrentOctave
        jsr     UpdateTop
        rts


;-----  octave down

OctaveDown:
        ldx.w   CurrentOctave
        dex
        cpx     #$00
        bne     _octavechange
        rts


;*****  MISC SUBROUTINES  **************************************************

;-----  wait for any key, return key code in a

WaitKey:
        jsr     FrameDuty
        jsr     ReadKeyboard

.IF DEBUG == 1
        ldx     #$0b
        stx     $d020
        cmp     #$00
.ENDIF
        beq     WaitKey
       
        rts


;-----  output note name a, cursor in y

NoteOut:
        stx     tmpreg                  ; store x

        asl
        tax

        lda.w   NoteNames,x             ; 'C'
        sta     (Line),y
        iny
        lda.w   NoteNames+1,x           ; '#'
        sta     (Line),y
        iny
        lda.w   NoteNames+2,x           ; '3'
        sta     (Line),y

        ldx     tmpreg                  ; restore x
        rts


;-----  output command name, cursor in y

CmdOut:
        stx     tmpreg                  ; store x

        asl
        asl
        tax

        lda.w   CmdNames,x             ; 'C'
        sta     (Line),y
        iny
        lda.w   CmdNames+1,x           ; '#'
        sta     (Line),y
        iny
        lda.w   CmdNames+2,x           ; '3'
        sta     (Line),y

        ldx     tmpreg                  ; restore x
        rts


;-----  output a as hex, cursor in y

HexOut:
        stx     tmpreg                  ; store x

        pha
        ror
        ror
        ror
        ror
        and     #$0f                    ; output high nybble
        tax
        lda.w   Hex,x
        sta     (Line),y
        iny

        pla
        and     #$0f                    ; output low nybble
        tax
        lda.w   Hex,x
        sta     (Line),y

        ldx     tmpreg                  ; restore x
        rts


;-----  go to screen line a

Locate:
        sty     tmpreg                  ; store y
        pha

        tay
        lda     RowsL,y                 ; get line address from table
        sta     Line
        lda     RowsH,y
        sta     LineH

        pla
        ldy     tmpreg                  ; restore y
        rts


;-----  read keyboard

ReadKeyboard:
        jsr     SCNKEY                  ; keyboard scan

        lda     #$01                    ; speed up key repeat
        sta     $028b

        lda     $c6                     ; check buffer
        beq     _nokey

        ldy     $0277                   ; get key
        ldx     #$00
_movebuf:
        lda     $0278,x                 ; scroll keyboard buffer
        sta     $0277,x
        inx
        cpx     $c6
        bne     _movebuf

        dec     $c6
        tya                             ; return key code in a
_nokey:
        rts


;-----  frame duties: play music, flash cursor, timing

FrameDuty:
        ldx     #$fa
_wait0:
        cpx     $d012
        bne     _wait0

        ldx     #$00                    ; raster time zero if sound off
        ldy.w   MusicFlag
        beq     _noplay

        cpy     #$03                    ; check play mode
        beq     _blockplaymode
        cpy     #$02
        bne     _playmodeok

_noteplaymode:
        ldx     #$ff                    ; note play mode (sequencer off)
        stx     count
        jmp     _playmodeok

_blockplaymode:
        lda.w   CurrentBlock            ; block play mode
        clc
        adc     #(BlockData/256)-1
        sta     block

_playmodeok:
        lda     #$0c
        ldx     #$fc
_wait1:
        cpx     $d012
        bne     _wait1

        sta     $d020

        jsr     $1003
        lda     $d012

.IF DEBUG == 1
        ldx     #$02
.ELSE
        ldx     #$0b
.ENDIF
        stx     $d020

        clc
        adc     #$05                    ; raster time (full lines + 1)
        tax

_noplay:
        lda.w   Hex,x                   ; write raster use
        sta     $0425

        cpx.w   RasterPeak
        bcc     _nopeak
        stx.w   RasterPeak

        sta     $0427                   ; write raster peak
_nopeak:

        lda.w   Flash                   ; flash cursor
        clc
        adc     #$01
        and     #$1f
        sta.w   Flash
        tay

        lda.w   CursorFlash,y
        sta     $d02e

        rts


;-----  write/update top line

WriteTop:
        ldx     #$27
_wrtop:
        lda.w   toplinetext,x
        sta     $0400,x
        dex
        bpl     _wrtop

UpdateTop:
        lda.w   CurrentBlock

        clc                             ; calculate block address
        adc     #(BlockData/256)-1
        sta     edBlockH

        lda     #$00
        sta     edBlock                 ; address low byte

        ldy     #$f9                    ; each block must have an end mark
        sta     (edBlock),y             ; end mark parameter
        lda     #$01
        dey
        sta     (edBlock),y             ; end mark cmd


        lda     #$00
        jsr     Locate                  ; move to top line

        lda.w   CurrentBlock
        ldy     #$06
        jsr     HexOut                  ; output block number

        ldy.w   CurrentSound            ; calculate sound address
        lda.w   SoundLoc,y
        clc
        adc     #$20
        sta     edSound

        lda     #(SoundTab/256)
        sta     edSoundH

        tya
        ldy     #$10
        jsr     HexOut                  ; output sound number

        ldx.w   CurrentOctave
        lda.w   Hex,x
        sta     $041b                   ; output octave number

        rts


;-----  initialize screen when switching modes

InitScreen:
        jsr     StopMusic

        ldy     #$2e
_vic:
        lda     VICIISetup,y            ; set up VIC II
        sta     $d000,y
        dey
        bpl     _vic

        ldy     #$07
        lda     #$fe                    ; sprites at $3f80
_spr:
        sta     $07f8,y
        dey
        bpl     _spr

        jsr     ClearScreen

        jmp     WriteTop                ; rts there




;-----  clear screen including top row

ClearScreenAll:
        ldy     #$27
        lda     #$20
_scrall:
        sta     $0400,y
        dey
        bne     _scrall
        ;
        
;-----  clear screen

ClearScreen:
        ldy     #$00
_color:
        lda     #$0f
        sta     $d800,y
        sta     $d900,y
        sta     $da00,y
        sta     $db00,y
        lda     #$20
        sta     $0428,y
        sta     $0500,y
        sta     $0600,y
        sta     $06f8,y

        iny
        bne     _color

        rts


;-----  convert keypress in a to nybble $0-$f, $ff if key not hex

CheckHexKey:
        ldy     #$0f
_chexseek:
        cmp.w   Hex,y
        beq     _chex
        dey
        bpl     _chexseek
_chex:
        rts

        

;-----  scroll up, scrollmap start index in x

ScrollUp:

_scru:
        lda.w   scrollmap,x
        bne     _scrumore

        rts

_scrumore:
        tay

        .DEFINE scroll $0427
        .REPT 23

        lda.w   scroll+$28,y
        sta.w   scroll,y

        .REDEFINE scroll scroll+$28
        .ENDR

        inx
        jmp     _scru


;-----  scroll down, scrollmap start index in x

ScrollDown:

_scrd:
        lda.w   scrollmap,x
        bne     _scrdmore

        rts

_scrdmore:
        tay

        .REDEFINE scroll $03ff+23*$28
        .REPT 23

        lda.w   scroll,y
        sta.w   scroll+$28,y

        .REDEFINE scroll scroll-$28
        .ENDR

        inx
        jmp     _scrd


;-----  copy menu text to screen

ShowMenuText:
        ldy     #$00
_menulp:
        lda     MenuScreenText,y
        sta     $0428,y
        lda     MenuScreenText+$0100,y
        sta     $0528,y
        lda     MenuScreenText+$0200,y
        sta     $0628,y
        lda     MenuScreenText+$02c0,y
        sta     $06e8,y
        iny
        bne     _menulp

        lda     #$ff
        sta     $07ff

        jmp     SetMenuCursor


;-----  other routines

        .INCLUDE "packer.asm"
        .INCLUDE "disk.asm"
        .INCLUDE "help.asm"

PackPlayer:
        .INCBIN "packplayer.bin"        ; $1000-$13ff packed data player


;-----  some workspace etc

BlockBuffer:
        .DSB    $0100 $00
TrackBuffer:
        .DSB    $0040 $00
SoundBuffer:
        .DSB    $0010 $00


;-----  whatever

SoundText:
        .INCBIN "soundscreen.bin"

.ENDS


;*****  MISC TABLES/VARIABLES  *********************************************

.ORG $3800
.SECTION "misc" FORCE

Hex:
        .DB     $30,$31,$32,$33,$34,$35,$36,$37
        .DB     $38,$39,$41,$42,$43,$44,$45,$46
        .DB     $2a,$2a,$2a,$2a,$2a,$2a,$2a,$2a

Keyboard0:
        .INCBIN "keyboard0.bin"                         ; unshifted

Keyboard1:
        .INCBIN "keyboard1.bin"                         ; shifted

SoundLoc:
        .DB     $00,$01,$0c,$17,$22,$2d,$38,$43         ; $00-$07
        .DB     $4e,$59,$64,$6f,$7a,$85,$90,$9b         ; $08-$0f
        .DB     $a6,$b1,$bc,$c7,$d2                     ; $10-$14

OctaveBase:
        .DB     $02,$1a,$32,$4a,$62

VICIISetup:
        .DB     $18,$25,$48,$25,$78,$25,$a8,$25         ; $d000-
        .DB     $d8,$25,$08,$25,$38,$25,$00,$25
        .DB     $60,$1b,$00,$00,$00,$ff,$08,$00         ; $d010-
        .DB     $17,$00,$00,$ff,$7f,$ff,$00,$00
        .DB     $0b,$00,$00,$00,$00,$00,$0b,$00         ; $d020-
        .DB     $00,$00,$00,$00,$00,$00,$01

RowsL:
        .DEFINE raddr $0400
        .REPT 25
        .DB raddr&255
        .REDEFINE raddr raddr+$28
        .ENDR
RowsH:
        .REDEFINE raddr $0400
        .REPT 25
        .DB raddr/256
        .REDEFINE raddr raddr+$28
        .ENDR

scrollmap:
        .DB     $01,$02                         ; block editor scroll map
        .DB     $07,$08,$09,$0b,$0c
        .DB     $10,$11,$12,$14,$15
        .DB     $19,$1a,$1b,$1d,$1e
        .DB     $22,$23,$24,$26,$27
        .DB     $00


toplinetext:
        .INCBIN "topline.bin"


Screen:
        .DB     1

CurrentBlock:
        .DB     1
CurrentSound:
        .DB     1
CurrentOctave:
        .DB     1
RasterPeak:
        .DB     0

MusicFlag:
        .DB     0
Flash:
        .DB     0

BlockScroll:
        .DB     0
BlockX:
        .DB     0
BlockY:
        .DB     0


NoteNames:
        .INCBIN "notenames.bin"

SoundConv:
        .INCBIN "soundconv.bin"                 ; sound offset conversion

CmdNames:
        .INCBIN "cmdnames.bin"

CursorFlash:
        .INCBIN "cursorflash.bin"

MenuScreenText:
        .INCBIN "menuscreen.bin"
.ENDS


;*****  CURSOR/TOP SPRITES  ************************************************

.ORG    $3f80
.SECTION "sprite" FORCE

        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00
        .DB     $ff,$ff,$ff,$ff,$ff,$ff         ; cursor/top sprite
        .DB     $ff,$ff,$ff,$ff,$ff,$ff
        .DB     $ff,$ff,$ff,$ff,$ff,$ff
        .DB     $ff,$ff,$ff,$ff,$ff,$ff

        .DB     $00

        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00,$00,$00,$00
        .DB     $00,$00,$00

        .DB     $f0,$00,$00,$f0,$00,$00         ; small cursor
        .DB     $f0,$00,$00,$f0,$00,$00
        .DB     $f0,$00,$00,$f0,$00,$00
        .DB     $f0,$00,$00,$f0,$00,$00

        .DB     $00
.ENDS


;*****  HELP TEXT  *********************************************************

.ORG    $9800
.SECTION "help" FORCE
        .INCBIN "johnhelp.bin"

.ENDS
