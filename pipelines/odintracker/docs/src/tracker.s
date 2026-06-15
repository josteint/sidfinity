; ======================================
; Odin Tracker 1.13 for C64 by Zed on 17 Apr 2001.
;
; Main module.
;
; http://www.inf.bme.hu/~zed/tracker
; mailto:zed@kempelen.inf.bme.hu
;
; Wotan mit uns.
; ======================================

; ======================================
; Memory layout
;
; $0810-$3800     editor code and initialized and readonly data
; $3800-$3a00     font
; $3a00-$3f80     key mapping + read/write and uninitialized editor data
; $3f80-$3fc0     sprite that is used to highlight current patternrow
; $3fc0-$4000     sprite cursor
; $4000-$4100     orderlist
; $4100-$4120     song title
; $4120-$4200       [unused, maybe for song info]
; $4200-$4800     patterns
; $4800-$4a00     instruments
; $4a00-$4c00     instrument names
; $4c00-$4d00     wave table
; $4d00-$4e00     arpeggio table
; $4e00-$4f00     filter table
; $4f00-$5000     song start positions
; $5000-$b000     tracks
; $b000-$bf00     relocatable player
; $bf00-$c000     opcode list for all 6510 instructions, used by the packer
; $c000-$ce00     editor's player
; $ce00-$d000     used when converting instrument data from old format
; $d000-$xxxx     help text
;
; Yes, it finally happened: I'm running low on memory.
; Nothing serious yet, just the nice, logical structure is
; beginning to drift away... :(
; ======================================

        include vplayeri.s              ; Update VPLAYER_CODE_END !!!

        include kernal.s
        include defines.s

; ======================================
; Defines for editor only.
; ======================================

; Escape byte in RLE packer.
RLE_ESCAPE_BYTE         = $ff

; Screen identifiers for editor.
EDITOR_ORDER_ID         = 0
EDITOR_PATTERN_ID       = 1
EDITOR_INSTRUMENT_ID    = 2
EDITOR_CONFIGMENU_ID    = 3
EDITOR_SPECMENU_ID      = 4
EDITOR_DISKMENU_ID      = 5

; Block status flags.
BLOCK_BEGINSET          = $01
BLOCK_ENDSET            = $02

; Logical file number for practically all disk I/O.
FILENUMBER              = 8

; MSB of sprite X coordinates ($d010) hardwired.
SPRITEXMSB              = $c0

; Color masks for list display.
DISPLAY_INDEXCOLORMASK  = $40
DISPLAY_DATACOLORMASK   = $80
DISPLAY_SELCOLORMASK    = $c0

; ======================================
; Editor's zeropage.
; ======================================

editor_trackptr         = $40   ; Temp 16 bit pointer to track.
editor_temptrackptr     = $42   ; Used when inserting/deleting in track.
editor_instptr          = $44   ; Temp 16 bit pointer to instrument.
editor_patternptr       = $46   ; Pointer to pattern.
stringptr               = $48   ; for console_writestring.
display_datasrc         = $4a   ; For write_list

timer_hundreds          = $4c   ; Timer that measures playing time.
timer_seconds           = $4d   ; Timer that measures playing time.
timer_minutes           = $4e   ; Timer that measures playing time.

div16_dividend          = $50
div16_divisor           = $52
div16_quotient          = $54

io_pointer              = $ac   ; Pointer used while load/save.
io_saveend              = $ae   ; Pointer to first byte _not_ to save.
io_blockcounter         = $56   ; 4 digit BCD block number while load/save.
io_bytecounter          = $58   ; 8 bit byte counter for disk blocks.

        processor 6502

; ======================================
; Start of editor.
; ======================================

        org EDITOR

        jsr editor_init

; Main editor loop.
editor_loop:
        jsr getin
        sta editor_currentkey
        ldx editor_whichscreen
        lda editorloop_entrieslo,x
        ldy editorloop_entrieshi,x
        jsr jsrya

; Process global keys.
; If the key was processed by some handler before, editor_currentkey==0
el_processglobalkeys:
        lda editor_currentkey
        beq el_keyprocessed
; Try to find action for this key.
        ldx #0
el_findkey:
        cmp global_keys,x
        beq el_keyfound
        inx
        inx
        inx
        cpx #GLOBAL_KEYS_NUM
        bne el_findkey
        beq el_keyprocessed

; Call event handler for the key found.
el_keyfound:
        lda global_keys+1,x
        ldy global_keys+2,x
        jsr jsrya

el_keyprocessed:
        jsr editor_updatescreen
        jmp editor_loop

; ======================================
; Clear editor_currentkey to indicate it is processed.
; ======================================
editor_clearkey:
        lda #0
        sta editor_currentkey
        rts

; ======================================
; Events for global keys.
; ======================================

; Stop player and shut up SID.
editor_stopplayer:
        lda #$00
        sta editor_playmode
        jmp player_stop

; Start/stop playing.
eg_playonoff:
        lda editor_playmode
        cmp #1
        beq editor_stopplayer

; Start playing from current pattern. (SPACE)
        jsr eg_initplayer
        ldx #0
        ldy #0
        beq eg_startplaying             ; Jump always.

; Start playing a single pattern. (SHIFT+SPACE)
eg_playpattern:
        jsr eg_initplayer
        ldx #0
        beq eg_playsinglepatter         ; Jump always.

; Start playing a single pattern from current row. (RETURN)
eg_playpatterncurrent:
        ldx trackrow
eg_playsinglepatter:
        ldy #1

;  Input: X: first pattern row
;         Y: if nonzero, play single pattern only.
eg_startplaying:
        lda ordernumber
        jsr player_start
        jsr eg_zerorastertimes
        lda #$01
        sta editor_playmode
        rts

; Show context help.
eg_writecontexthelp:
        ldx editor_whichscreen
        lda editor_contexthelppages,x
        .byte $2c                       ; BIT $ffff
; Show all help.
eg_writehelp:
        lda #0
eg_writecontexthelp1:
        ldx #$00
        stx $d020
        stx $d021
        ldx #$1b
        stx $d011                       ; Disable ECM.
        ldx #$16
        stx $d018                       ; Set ROM font.
        ldx #$00
        stx $d015                       ; Disable all sprites.
        jsr write_help
        jmp editor_reinit

; Go to order editor.
eg_gotoordereditor:
        lda #EDITOR_ORDER_ID
eg_gotoscreen:
        sta editor_whichscreen
        jmp editor_initscreen

; Go to pattern editor.
eg_gotopatterneditor:
        lda #EDITOR_PATTERN_ID
        bne eg_gotoscreen

; Go to instrument editor.
eg_gotoinsteditor:
        lda #EDITOR_INSTRUMENT_ID
        bne eg_gotoscreen

; Go to config menu.
eg_configmenu:
        jsr cm_getcolors
        lda #EDITOR_CONFIGMENU_ID
        bne eg_gotoscreen

; Go to disk menu.
eg_specmenu:
        lda #EDITOR_SPECMENU_ID
        bne eg_gotoscreen

; Go to disk menu.
eg_diskmenu:
        lda #EDITOR_DISKMENU_ID
        bne eg_gotoscreen

; Dec current instrument.
eg_instdec:
        ldx editor_currentinst
        dex
        jmp eg_instinc1

; Inc current instrument.
eg_instinc:
        ldx editor_currentinst
        inx
eg_instinc1:
        txa
        and #MAX_INSTRUMENTS-1
        sta editor_currentinst
        rts

; Dec pattern for current order position.
eg_keypatterndec:
        ldx ordernumber
        dec ORDERLIST,x
        rts

; Inc pattern for current order position.
eg_keypatterninc:
        ldx ordernumber
        inc ORDERLIST,x
        rts

; Move backward in orderlist.
eg_keyorderdec:
        dec ordernumber
        jmp eg_keyorderinc0

; Move forward in orderlist.
eg_keyorderinc:
        inc ordernumber
eg_keyorderinc0:
        ldy editor_playmode
        lda #0                          ; Avoid calling player inbetween!
        sta editor_playmode
        lda ordernumber
        sta nextordernumber
        lda #$80
        sta forcenewpattern
        sty editor_playmode
        rts

; Mute/unmute all channels.
eg_muteall:
        ldx editor_patternchannel
        lda chn_muted,x
        eor #$80
        sta chn_muted+0
        sta chn_muted+1
        sta chn_muted+2
        jmp editor_updatepatterncolors

; Mute/unmute channel 1.
eg_mutechannel1:
        ldx #0
        beq eg_domute
; Mute/unmute channel 2.
eg_mutechannel2:
        ldx #1
        bne eg_domute
; Mute/unmute channel 3.
eg_mutechannel3:
        ldx #2
eg_domute:
        lda chn_muted,x
        eor #$80
        sta chn_muted,x
        jmp editor_updatepatterncolors

; Select octaves.
eg_octave1:
        ldx #1
        lda #0
eg_octavedone:
        stx editor_currentoctave
        sta editor_currentoctavenote
        rts
eg_octave2:
        ldx #2
        lda #12
        bne eg_octavedone               ; short jump
eg_octave3:
        ldx #3
        lda #24
        bne eg_octavedone               ; short jump
eg_octave4:
        ldx #4
        lda #36
        bne eg_octavedone               ; short jump
eg_octave5:
        ldx #5
        lda #48
        bne eg_octavedone               ; short jump
eg_octave6:
        ldx #6
        lda #60
        bne eg_octavedone               ; short jump
eg_octave7:
        ldx #7
        lda #72
        bne eg_octavedone               ; short jump

; Clear rastertime counters.
eg_zerorastertimes:
        lda #$00
        sta editor_currentraster        ; Clear current rastertime.
        sta editor_maxraster            ; Clear max rastertime.
; Zero timer.
        sta timer_hundreds
        sta timer_seconds
        sta timer_minutes
        rts

; Init player. This completely resets everything, including speed.
eg_initplayer:
        jsr editor_stopplayer
        jmp player_init

; Keyjazz (test instrument) in pattern and istrument editor.
eg_keyjazz:
; Do nothing when instrument 0 is selected.
        lda editor_currentinst
        beq egkj_done
; Test SHIFT.
        lda shiftflags
        lsr
        bcc egkj_keyoff
; See if a note key is pressed.
        lda $c5
        cmp #$40
        beq egkj_keyoff
; Try to identify a note key.
        ldx #KEYJAZZNOTEKEYS_NUM-1
egkj_findnotekeys:
        cmp keyjazznotekeys,x
        beq egkj_notekey
        dex
        bpl egkj_findnotekeys
        rts
; We have a note key pressed.
egkj_notekey:
        inx
        txa
        clc
        adc editor_currentoctavenote
        cmp #97                         ; Do not allow anything above B-7.
        bcc egkj_notekeyok
        lda #96
egkj_notekeyok:
        sta editor_currentkeyjazznote
; Check if we are already in keyjazz mode.
        lda editor_playmode
        cmp #2
        beq egkj_inkeyjazz
; Stop player and shut up SID if we are not yet in keyjazz mode.
        jsr editor_stopplayer
egkj_inkeyjazz:
; Init for this instrument
        jsr editor_clearkey
        lda #$02
        sta editor_playmode
        rts
egkj_keyoff:
        lda #$00
        sta editor_currentkeyjazznote
egkj_done:
        rts

; ======================================
editor_editorder:
; Edit orders.
; ======================================
;  Input: editor_currentkey: key from getin.
; ======================================
        lda editor_currentkey
        beq eo_done
; Try to find action for this key.
        ldx #0
eo_findkey:
        cmp editorder_keys,x
        beq eo_keyfound
        inx
        inx
        inx
        cpx #EDITORDER_KEYS_NUM
        bne eo_findkey

        lda editor_currentkey
        jsr ascii2hexdigit
        bmi eo_done
        ldx editor_ordercol
        php
        ldy ordernumber
        ldx ORDERLIST,y
        plp
        beq eo_highnybble
        jsr replacelownybble
        jmp eo_replaced
eo_highnybble:
        jsr replacehighnybble
eo_replaced:
        sta ORDERLIST,y
        jmp eo_keyprocessed

; Call event handler for the key found.
eo_keyfound:
        jsr editor_clearkey             ; Indicate that key is processed.
        lda editorder_keys+1,x
        ldy editorder_keys+2,x
        jmp jsrya

eo_keyprocessed:
        jsr editor_clearkey             ; Indicate that key is processed.
        lda editor_ordercol
        eor #$01
        sta editor_ordercol
        bne eo_done
        jsr eg_keyorderinc
eo_done:
        rts

; ======================================
; Events for keys in orderlist editor.
; ======================================

eo_keyleft:
        lda #0
eo_keyleft1:
        sta editor_ordercol
        rts

eo_keyright:
        lda #1
        bne eo_keyleft1

; Page up/down in orderlist.
eo_keypgupdn:
        lda shiftflags
        lsr
        bcc eo_keypgdn

; Move up 16 lines in orders.
eo_keypgup:
        lda #$f8
eo_keypgup1:
        clc
        adc ordernumber
        jmp eo_keygotolinea

; Move down 16 lines in orders.
eo_keypgdn:
        lda #$08
        bne eo_keypgup1

; Goto row 0.
eo_keygotoline00:
        lda #$00
eo_keygotolinea:
        sta ordernumber
        jmp eg_keyorderinc0
; Goto row $40.
eo_keygotoline40:
        lda #$40
        bne eo_keygotolinea
; Goto row $80.
eo_keygotoline80:
        lda #$80
        bne eo_keygotolinea
; Goto row $c0.
eo_keygotolinec0:
        lda #$c0
        bne eo_keygotolinea

; Insert into order list.
eo_insert:
        lda #MAX_ORDERS-1
        sta list_length
        lda ordernumber
        ldx #<ORDERLIST
        ldy #>ORDERLIST
        jsr list_insert
        jmp eg_keyorderinc0

; Delete from orderlist.
eo_delete:
        lda ordernumber
        beq eo_deletedone
        jsr eg_keyorderdec
        lda #MAX_ORDERS-1
        sta list_length
        lda #$00
        sta list_defaultelement
        lda ordernumber
        ldx #<ORDERLIST
        ldy #>ORDERLIST
        jsr list_delete
        jmp eg_keyorderinc0
eo_deletedone:
        rts

; ======================================
ep_storeundobuffer:
; Store current track into undo buffer.
; ======================================
;  Input: editor_patternchannel
;         editor_tracks[]
; Output: editor_trackundochannel: = editor_patternchannel
;         editor_trackundobuffer[]
; ======================================
        ldx editor_patternchannel
        stx editor_trackundochannel
        lda editor_tracks,x
        jsr editor_maketrackpointer
        ldy #0
epsub_loop:
        lda (editor_trackptr),y
        sta editor_trackundobuffer,y
        iny
        cpy #192
        bne epsub_loop
        rts

; ======================================
ep_restoreundobuffer:
; Restore track from undo buffer.
; ======================================
;  Input: editor_trackundochannel
;         editor_tracks[]
; Output: editor_trackundochannel: always $80
; ======================================
        ldx editor_trackundochannel
        bmi eprub_done
        lda editor_tracks,x
        jsr editor_maketrackpointer
        ldy #0
eprub_loop:
        lda editor_trackundobuffer,y
        sta (editor_trackptr),y
        iny
        cpy #192
        bne eprub_loop
        lda #$80
        sta editor_trackundochannel
eprub_done:
        rts

; ======================================
editor_editpattern:
; Edit pattern.
; ======================================
;  Input: editor_currentkey: key from getin.
; ======================================
; Do our fancy keyjazz.
        jsr eg_keyjazz
; Buffer tracks
        jsr editor_gettracks
        lda trackrow
        sta editor_getputtrackrow
        jsr editor_gettrackrow
        lda editor_currentkey
        beq ep_done
; Try to find action for this key.
        ldx #0
ep_findkey:
        cmp editpattern_keys,x
        beq ep_keyfound
        inx
        inx
        inx
        cpx #EDITPATTERN_KEYS_NUM
        bne ep_findkey

        lda editor_currentkey
        ldy editor_patternfield
        beq ep_note
        jsr ascii2hexdigit
        bmi ep_done                     ; Not a hex digit.
        dey
        beq ep_insthi
        dey
        beq ep_instlo
        dey
        beq ep_effect
        dey
        beq ep_effectparhi
        dey
        beq ep_effectparlo
        brk                       ; !!!!! impossible

; Try to identify a note key.
ep_note:
        ldx #NOTEKEYS_NUM-1
ep_findnotekeys:
        cmp notekeys,x
        beq ep_notekey
        dex
        bpl ep_findnotekeys
ep_done:
        rts

; Edit various hex fields in pattern editor. A is a hex digit. [$00-$0f]
ep_insthi:
        ldx editor_trackinst
        jsr replacehighnybble
        jmp ep_instmodified
ep_instlo:
        ldx editor_trackinst
        jsr replacelownybble
ep_instmodified:
        cmp #MAX_INSTRUMENTS            ; Do not accept instrument>=$20
        bcs ep_done
        sta editor_trackinst
        jmp ep_patternrowmodified

ep_effect:
        sta editor_trackeffect
        jmp ep_patternrowmodified

ep_effectparhi:
        ldx editor_trackeffectpar
        jsr replacehighnybble
        jmp ep_effectmodified
ep_effectparlo:
        ldx editor_trackeffectpar
        jsr replacelownybble
ep_effectmodified:
        sta editor_trackeffectpar
        jmp ep_patternrowmodified

; Call event handler for the key found.
ep_keyfound:
        jsr editor_clearkey             ; Indicate that key is processed.
        lda editpattern_keys+1,x
        ldy editpattern_keys+2,x
        jmp jsrya

ep_notekey:
        inx
        txa
        clc
        adc editor_currentoctavenote
        cmp #96                         ; Do not allow anything above B-7.
        bcc ep_notekeyok
        lda #96
ep_notekeyok:
        sta editor_tracknote
        lda editor_currentinst          ; Do not enter instrument 0.
        beq ep_patternrowmodified
        sta editor_trackinst
ep_patternrowmodified:
        lda trackrow
        sta editor_getputtrackrow
        jsr editor_puttrackrow
        jsr ep_advancecursor
        jmp editor_clearkey             ; Indicate that key is processed.

; ======================================
ep_advancecursor:
; Advance cursor by number of rows in editor_editstep.
; ======================================
        lda trackrow
        clc
        adc editor_editstep
        and #$3f
        sta trackrow
        rts

; ======================================
; Events for keys in pattern editor.
; ======================================

ep_keyup:
        ldx trackrow
        dex
ep_keyup1:
        txa
        and #$3f
        sta trackrow
        rts

ep_keydown:
        ldx trackrow
        inx
        jmp ep_keyup1

ep_keyleft:
        ldx editor_patternfield
        ldy editor_patternchannel
        dex
        bpl ep_keyleft1
        ldx #5
ep_keyleft2:
        dey
        bpl ep_keyleft1
        ldy #2
ep_keyleft1:
        sty editor_patternchannel
ep_keyleft3:
        stx editor_patternfield
        rts

ep_keyright:
        ldx editor_patternfield
        ldy editor_patternchannel
        inx
        cpx #6
        bmi ep_keyleft1
ep_keyright2:
        ldx #0
        iny
        cpy #3
        bmi ep_keyleft1
        ldy #0
        beq ep_keyleft1                 ; short jump

; Move to note field in next channel.
ep_keynextchannel:
        ldy editor_patternchannel
        bpl ep_keyright2                ; short jump

; Move to note field in previous channel.
ep_keyprevchannel:
        ldx #0
        ldy editor_patternchannel
        lda editor_patternfield
        beq ep_keyleft2                 ; short jump
        bne ep_keyleft3

; Page up/down in pattern.
ep_keypgupdn:
        lda shiftflags
        lsr
        lda #$08
        bcc ep_keypgupdndo
        lda #$f8
ep_keypgupdndo:
        clc
        adc trackrow
        and #$3f
        .byte $2c                       ; BIT $ffff

; Goto row 0.
ep_keyhome:
        lda #0
        sta trackrow
        rts

; Inc track for current pattern.
ep_keytrackdec:
; Get pointer to pattern.
        ldy ordernumber
        lda ORDERLIST,y                 ; Get current pattern.
        jsr editor_makepatternpointer
        lda editor_patternchannel
        asl
        tay
        lda (editor_patternptr),y
        sec
        sbc #$01
        and #MAX_TRACKS-1
        sta (editor_patternptr),y
        rts

; Dec track for current pattern.
ep_keytrackinc:
; Get pointer to pattern.
        ldy ordernumber
        lda ORDERLIST,y                 ; Get current pattern.
        jsr editor_makepatternpointer
        lda editor_patternchannel
        asl
        tay
        lda (editor_patternptr),y
        clc
        adc #$01
        and #MAX_TRACKS-1
        sta (editor_patternptr),y
        rts

; Enter track number.
ep_edittracknum:
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask
        ldy editor_patternchannel
        lda editor_channelxpositions,y
        clc
        adc #3
        tax
        lda editor_tracks,y
        ldy #6
        jsr console_gethexatxy
        cmp #MAX_TRACKS
        bcc ep_edittracknumvalid
        rts
ep_edittracknumvalid:
        ldx editor_patternchannel
        sta editor_tracks,x
        jmp editor_puttracks

; Clear note or effect.
ep_keyclearnote:
        lda #0
        ldx editor_patternfield
        cpx #3
        bmi ep_keyclearnote1
        sta editor_trackeffect
        sta editor_trackeffectpar
        jmp ep_patternrowmodified
ep_keyclearnote1:
        sta editor_tracknote
ep_keyclearnote2:
        sta editor_trackinst
        jmp ep_patternrowmodified

ep_keyoff:
        lda #97                         ; B-7 + 1
        sta editor_tracknote
        lda #0
        beq ep_keyclearnote2

; Insert trackrow in current track.
ep_insert:
        jsr ep_storeundobuffer
        ldx editor_patternchannel
        lda editor_tracks,x             ; Get track index from current channel.
; Insert a line in track A at row trackrow. (Entry point).
ep_insertrow:
        jsr editor_maketrackpointer
        lda trackrow
        asl
        adc trackrow
        sta trackrow3
        cmp #63*3
        beq ep_insert1                  ; Nothing to move on last row.
; editor_temptrackptr=editor_trackptr+3
        lda editor_trackptr
        clc
        adc #3
        sta editor_temptrackptr
        lda editor_trackptr+1
        adc #0
        sta editor_temptrackptr+1
        ldy #63*3
ep_insertloop:
        dey
        lda (editor_trackptr),y
        sta (editor_temptrackptr),y
        dey
        lda (editor_trackptr),y
        sta (editor_temptrackptr),y
        dey
        lda (editor_trackptr),y
        sta (editor_temptrackptr),y
        cpy trackrow3
        bne ep_insertloop
ep_insert1:
        ldy trackrow3
        jmp ep_insdelclear

; Backspace trackrow in current track.
ep_delete:
        lda trackrow
        beq ep_delete1                  ; Nothing to do on first row.
        jsr ep_storeundobuffer
        dec trackrow
        ldx editor_patternchannel
        lda editor_tracks,x             ; Get track index from current channel.
; Delete a line in track A at row trackrow. (Entry point).
ep_deleterow:
        jsr editor_maketrackpointer
        lda trackrow
        asl
        adc trackrow
        tay
; editor_temptrackptr=editor_trackptr+3
        lda editor_trackptr
        clc
        adc #3
        sta editor_temptrackptr
        lda editor_trackptr+1
        adc #0
        sta editor_temptrackptr+1
ep_deleteloop:
        lda (editor_temptrackptr),y
        sta (editor_trackptr),y
        iny
        lda (editor_temptrackptr),y
        sta (editor_trackptr),y
        iny
        lda (editor_temptrackptr),y
        sta (editor_trackptr),y
        iny
        cpy #64*3                       ; Do move until last row.
        bne ep_deleteloop
        dey
        dey
        dey
; Clear row pointed by Y.
ep_insdelclear:
        lda #$00
        sta (editor_trackptr),y
        iny
        sta (editor_trackptr),y
        iny
        sta (editor_trackptr),y
ep_delete1:
        rts

; Insert in all tracks visible in editor.
ep_insertall:
; Insert in channel 1.
        lda editor_tracks+0
        jsr ep_insertrow
; Insert in channel 2 only of the track is different from channel 1's.
        lda editor_tracks+1
        cmp editor_tracks+0
        beq epia_skip2
        jsr ep_insertrow
epia_skip2:
; Insert in channel 3 only of the track is different from channel 1's and 2's.
        lda editor_tracks+2
        cmp editor_tracks+0
        beq epia_skip3
        cmp editor_tracks+1
        beq epia_skip3
        jsr ep_insertrow
epia_skip3:
        rts

; Delete in all tracks visible in editor.
ep_deleteall:
        lda trackrow
        beq epda_skip3                  ; Nothing to do on first row.
        dec trackrow
; Delete in channel 1.
        lda editor_tracks+0
        jsr ep_deleterow
; Delete in channel 2 only of the track is different from channel 1's.
        lda editor_tracks+1
        cmp editor_tracks+0
        beq epda_skip2
        jsr ep_deleterow
epda_skip2:
; Delete in channel 3 only of the track is different from channel 1's and 2's.
        lda editor_tracks+2
        cmp editor_tracks+0
        beq epda_skip3
        cmp editor_tracks+1
        beq epda_skip3
        jsr ep_deleterow
epda_skip3:
        rts

; Grab effect under cursor to effect buffer.
ep_grabeffect:
        lda editor_trackeffect
        sta editor_trackeffectbuf
        lda editor_trackeffectpar
        sta editor_trackeffectparbuf
        rts

; Enter effect from effect buffer to cursor.
ep_dropeffect:
        jsr ep_storeundobuffer
        lda editor_trackeffectbuf
        sta editor_trackeffect
        lda editor_trackeffectparbuf
        sta editor_trackeffectpar
        jmp ep_patternrowmodified

; Set block begin.
ep_setblockbeg:
        lda trackrow
        sta editor_trackblockbeg
        lda editor_trackblockflags
        ora #BLOCK_BEGINSET
        ldx editor_patternchannel
        cpx editor_blockchannel
        beq ep_checkblocklimits
        lda #BLOCK_BEGINSET
        bne ep_checkblocklimits         ; short jump

; Set block end.
ep_setblockend:
        lda trackrow
        sta editor_trackblockend
        lda editor_trackblockflags
        ora #BLOCK_ENDSET
        ldx editor_patternchannel
        cpx editor_blockchannel
        beq ep_checkblocklimits
        lda #BLOCK_ENDSET
; Force blockbeg<=blockend.
ep_checkblocklimits:
        sta editor_trackblockflags
        stx editor_blockchannel
        lda editor_trackblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        bne ep_checkblocklimits1        ; Begin or end unset -> nothing to do.
        lda editor_trackblockbeg
        cmp editor_trackblockend
        bcc ep_checkblocklimits1        ; beg<end -> nothing to do.
        ldy editor_trackblockend
        sta editor_trackblockend
        sty editor_trackblockbeg
ep_checkblocklimits1:
        rts

; Select the whole track.
ep_selecttrack:
        lda editor_patternchannel
        sta editor_blockchannel
        lda #0
        sta editor_trackblockbeg
        lda #63
        sta editor_trackblockend
        lda #BLOCK_BEGINSET+BLOCK_ENDSET
        sta editor_trackblockflags
        rts

; Unselect block.
ep_unselectblock:
        lda #$00
        sta editor_trackblockflags
        rts

; Cut block.
ep_cutblock:
; Proceed only if block start and end are defined.
        lda editor_trackblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        beq ep_cutblockvalid
        rts
ep_cutblockvalid:
        jsr ep_storeundobuffer
        lda #$00
        sta editor_trackcopybufferpos
        sta editor_trackcopybufferlen
        lda editor_trackblockbeg
        sta ep_execblockbeg
        lda editor_trackblockend
        sta ep_execblockend
        lda editor_blockchannel
        ldx #<ep_cutblockcb
        ldy #>ep_cutblockcb
        jmp ep_execblockop

; Cut block callback for each row.
ep_cutblockcb:
        jsr ep_copyblockcb
        lda #0
        sta editor_tracknote
        sta editor_trackinst
        sta editor_trackeffect
        sta editor_trackeffectpar
        rts

; Copy block.
ep_copyblock:
; Proceed only if block start and end are defined.
        lda editor_trackblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        beq ep_copyblockvalid
        rts
ep_copyblockvalid:
        lda #$00
        sta editor_trackcopybufferpos
        sta editor_trackcopybufferlen
        lda editor_trackblockbeg
        sta ep_execblockbeg
        lda editor_trackblockend
        sta ep_execblockend
        lda editor_blockchannel
        ldx #<ep_copyblockcb
        ldy #>ep_copyblockcb
        jmp ep_execblockop

; Copy block callback for each row.
ep_copyblockcb:
        lda editor_trackcopybufferlen
        asl
        asl
        tax
        lda editor_tracknote
        sta editor_trackcopybuffer,x
        inx
        lda editor_trackinst
        sta editor_trackcopybuffer,x
        inx
        lda editor_trackeffect
        sta editor_trackcopybuffer,x
        inx
        lda editor_trackeffectpar
        sta editor_trackcopybuffer,x
        inc editor_trackcopybufferlen
        rts

; Paste block.
ep_pasteblock:
        jsr ep_storeundobuffer
        lda #$00
        sta editor_trackcopybufferpos
        lda trackrow
        sta ep_execblockbeg
        lda #63
        sta ep_execblockend
        lda editor_patternchannel
        ldx #<ep_pasteblockcb
        ldy #>ep_pasteblockcb
        jmp ep_execblockop

; Paste block callback for each row.
ep_pasteblockcb:
        lda editor_trackcopybufferpos
        cmp editor_trackcopybufferlen   ; Do we still have block data?
        bcs ep_pasteblockcb1
        asl
        asl
        tax
        lda editor_trackcopybuffer,x
        sta editor_tracknote
        inx
        lda editor_trackcopybuffer,x
        sta editor_trackinst
        inx
        lda editor_trackcopybuffer,x
        sta editor_trackeffect
        inx
        lda editor_trackcopybuffer,x
        sta editor_trackeffectpar
        inc editor_trackcopybufferpos
ep_pasteblockcb1:
        rts

; Mix block.
ep_mixblock:
        jsr ep_storeundobuffer
        lda #$00
        sta editor_trackcopybufferpos
        lda trackrow
        sta ep_execblockbeg
        lda #63
        sta ep_execblockend
        lda editor_patternchannel
        ldx #<ep_mixblockcb
        ldy #>ep_mixblockcb
        jmp ep_execblockop

; Mix block callback for each row.
ep_mixblockcb:
        lda editor_trackcopybufferpos
        cmp editor_trackcopybufferlen   ; Do we still have block data?
        bcs ep_mixblockcb1
        asl
        asl
        tax
        lda editor_tracknote
        bne ep_mixblockcbkeepnote
        lda editor_trackcopybuffer,x
        sta editor_tracknote
ep_mixblockcbkeepnote:
        inx
        lda editor_trackinst
        bne ep_mixblockcbkeepinst
        lda editor_trackcopybuffer,x
        sta editor_trackinst
ep_mixblockcbkeepinst:
        inx
        lda editor_trackeffect
        bne ep_mixblockcbkeepeff
        lda editor_trackcopybuffer,x
        sta editor_trackeffect
ep_mixblockcbkeepeff:
        inx
        lda editor_trackeffectpar
        bne ep_mixblockcbkeeppar
        lda editor_trackcopybuffer,x
        sta editor_trackeffectpar
ep_mixblockcbkeeppar:
        inc editor_trackcopybufferpos
ep_mixblockcb1:
        rts

; Transpose block up.
ep_transposeup:
; Proceed only if block start and end are defined.
        lda editor_trackblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        beq ep_transposeupvalid
        rts
ep_transposeupvalid:
        jsr ep_storeundobuffer
        lda editor_trackblockbeg
        sta ep_execblockbeg
        lda editor_trackblockend
        sta ep_execblockend
        lda editor_blockchannel
        ldx #<ep_transposeupcb
        ldy #>ep_transposeupcb
        jmp ep_execblockop

; Transpose block up callback for each row.
ep_transposeupcb:
        lda editor_tracknote
        beq ep_transposeupcb0           ; Do not slide "no note".
        cmp #96                         ; Do not slide above B-7.
        bcs ep_transposeupcb0
        inc editor_tracknote
ep_transposeupcb0:
        rts

; Transpose block down.
ep_transposedown:
; Proceed only if block start and end are defined.
        lda editor_trackblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        beq ep_transposedownvalid
        rts
ep_transposedownvalid:
        jsr ep_storeundobuffer
        lda editor_trackblockbeg
        sta ep_execblockbeg
        lda editor_trackblockend
        sta ep_execblockend
        lda editor_blockchannel
        ldx #<ep_transposedowncb
        ldy #>ep_transposedowncb
        jmp ep_execblockop

; Transpose block down callback for each row.
ep_transposedowncb:
        lda editor_tracknote
        cmp #2                          ; Do not slide below C-0.
        bcc ep_transposedowncb0
        cmp #97                         ; Do not slide note off.
        beq ep_transposedowncb0
        dec editor_tracknote
ep_transposedowncb0:
        rts

; Transpose block up. (Only current instrument.)
ep_transposecurrentup:
; Proceed only if block start and end are defined.
        lda editor_trackblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        beq ep_transposecurrentupvalid
        rts
ep_transposecurrentupvalid:
        jsr ep_storeundobuffer
        lda editor_trackblockbeg
        sta ep_execblockbeg
        lda editor_trackblockend
        sta ep_execblockend
        lda editor_blockchannel
        ldx #<ep_transposecurrentupcb
        ldy #>ep_transposecurrentupcb
        jmp ep_execblockop

; Transpose block up callback for each row. (Only current instrument.)
ep_transposecurrentupcb:
        lda editor_tracknote
        cmp #2                          ; Do not slide below C-0.
        bcc ep_transposecurrentupcb0
        cmp #96                         ; Do not slide above B-7.
        bcs ep_transposecurrentupcb0
        lda editor_trackinst
        cmp editor_currentinst
        bne ep_transposecurrentupcb0
        inc editor_tracknote
ep_transposecurrentupcb0:
        rts

; Transpose block down. (Only current instrument.)
ep_transposecurrentdown:
; Proceed only if block start and end are defined.
        lda editor_trackblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        beq ep_transposecurrentdownvalid
        rts
ep_transposecurrentdownvalid:
        jsr ep_storeundobuffer
        lda editor_trackblockbeg
        sta ep_execblockbeg
        lda editor_trackblockend
        sta ep_execblockend
        lda editor_blockchannel
        ldx #<ep_transposecurrentdowncb
        ldy #>ep_transposecurrentdowncb
        jmp ep_execblockop

; Transpose block down callback for each row. (Only current instrument.)
ep_transposecurrentdowncb:
        lda editor_tracknote
        cmp #2                          ; Do not slide below C-0.
        bcc ep_transposecurrentdowncb0
        cmp #97                         ; Do not slide note off.
        beq ep_transposecurrentdowncb0
        lda editor_trackinst
        cmp editor_currentinst
        bne ep_transposecurrentdowncb0
        dec editor_tracknote
ep_transposecurrentdowncb0:
        rts

; Inc/dec edit step.
ep_editstepincdec:
        ldx editor_editstep
        inx
        lda shiftflags
        lsr
        bcc ep_editstep1
        dex
        dex
ep_editstep1:
        txa
        and #$3f
        sta editor_editstep
        rts

; Increment track transpose.
ep_transposeinc:
        ldx editor_patternchannel
        inc editor_tracktransposes,x
        jmp editor_puttracks

; Decrement track transpose.
ep_transposedec:
        ldx editor_patternchannel
        dec editor_tracktransposes,x
        jmp editor_puttracks

; Edit track transpose.
ep_edittranspose:
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask
        ldy editor_patternchannel
        lda editor_channelxpositions,y
        clc
        adc #8
        tax
        lda editor_tracktransposes,y    ; Convert transpose from 2's
        bpl ep_edittransposeup1         ; complement to sign bit binary.
        eor #$7f
        clc
        adc #$01
ep_edittransposeup1:
        ldy #6
        jsr console_gethexatxy
        tax                             ; Convert transpose from sign bit
        bpl ep_edittransposeup2         ; binary to 2's complement.
        sec
        sbc #$01
        eor #$7f
ep_edittransposeup2:
        ldx editor_patternchannel
        sta editor_tracktransposes,x
        jmp editor_puttracks

; ======================================
ep_execblockop:
; Execute block operation.
; The address of the callback function executed for each row is in Y:X.
; The callback function gets note, instrument and effect data in
; editor_tracknote, editor_trackinst, editor_trackeffect,
; editor_trackeffectpar and should update them if necessary.
; ======================================
;  Input: A: channel where operation is done
;         Y:X: callback function address
;         ep_execblockbeg: first row to touch
;         ep_execblockend: last row to touch
; ======================================
        sta ep_execblockchannel
        stx ep_execblockop0+1
        sty ep_execblockop0+2
epebo_loop:
        lda ep_execblockbeg
        sta editor_getputtrackrow
        ldx ep_execblockchannel
        jsr editor_gettrackrowanychannel
ep_execblockop0:
        jsr $ffff                       ; Self modifying code.
        ldx ep_execblockchannel
        jsr editor_puttrackrowanychannel
        inc ep_execblockbeg
        lda ep_execblockbeg
        cmp ep_execblockend
        bcc epebo_loop
        beq epebo_loop
        rts

; ======================================
editor_editinstrument:
; Edit instrument.
; ======================================
;  Input: editor_currentkey: key from getin.
; ======================================
; Do nothing when instrument 0 is selected.
        lda editor_currentinst
        beq ei_done1

; Do our fancy keyjazz.
        jsr eg_keyjazz

        lda editor_currentkey
; Try to find action for this key.
        ldx #0
ei_findkey:
        cmp editinstrument_keys,x
        bne ei_keyfoundnot
        jmp ei_keyfound
ei_keyfoundnot:
        inx
        inx
        inx
        cpx #EDITINSTRUMENT_KEYS_NUM
        bne ei_findkey

        lda editor_currentkey
        jsr ascii2hexdigit
        bpl ei_validdigit
ei_done1:
        jmp ei_done                     ; Not a hex digit
ei_validdigit:
        ldx editor_instfield
        beq ei_instparams
        dex
        beq ei_wavetable
        dex
        beq ei_arptable
        dex
        beq ei_filtertable
        brk                             ; impossible

ei_instparams:
        ldx editor_instcol
        php
        pha
        lda editor_instrow
        jsr editor_makeinstptr
        ldy editor_currentinst
        lda (editor_instptr),y
        tax
        pla
        plp
        beq ei_instparamshigh
        jsr replacelownybble
        jmp ei_instparams0
ei_instparamshigh:
        jsr replacehighnybble
ei_instparams0:
        sta (editor_instptr),y
        jmp ei_keyprocessed

ei_wavetable:
        ldy editor_waveindex
        ldx editor_instcol
        php
        ldx WAVETABLE,y
        plp
        beq ei_wavetablehigh
        jsr replacelownybble
        jmp ei_wavetable0
ei_wavetablehigh:
        jsr replacehighnybble
ei_wavetable0:
        sta WAVETABLE,y
        jmp ei_keyprocessed

ei_arptable:
        ldy editor_arpindex
        ldx editor_instcol
        php
        ldx ARPEGGIOTABLE,y
        plp
        beq ei_arptablehigh
        jsr replacelownybble
        jmp ei_arptable0
ei_arptablehigh:
        jsr replacehighnybble
ei_arptable0:
        sta ARPEGGIOTABLE,y
        jmp ei_keyprocessed

ei_filtertable:
        ldy editor_filterindex
        ldx editor_instcol
        php
        ldx FILTERTABLE,y
        plp
        beq ei_filtertablehigh
        jsr replacelownybble
        jmp ei_filtertable0
ei_filtertablehigh:
        jsr replacehighnybble
ei_filtertable0:
        sta FILTERTABLE,y
        jmp ei_keyprocessed

; Call event handler for the key found.
ei_keyfound:
        jsr editor_clearkey             ; Indicate that key is processed.
        lda editinstrument_keys+1,x
        ldy editinstrument_keys+2,x
        jmp jsrya

ei_keyprocessed:
        jsr editor_clearkey             ; Indicate that key is processed.
        lda editor_instcol
        eor #$01
        sta editor_instcol
        bne ei_done
        jsr ei_keydown
ei_done:
        rts

; ======================================
; Events for keys in instrument editor.
; ======================================

ei_keyup:
        lda #$ff
        clc
        ldx editor_instfield
        dex
        beq ei_keyupdownwave
        dex
        beq ei_keyupdownarp
        dex
        beq ei_keyupdownfilter
        ldx editor_instrow
        dex
ei_keyup1:
        txa
        and #$0f
        sta editor_instrow
        rts

ei_keydown:
        lda #$01
        clc
        ldx editor_instfield
        dex
        beq ei_keyupdownwave
        dex
        beq ei_keyupdownarp
        dex
        beq ei_keyupdownfilter
        ldx editor_instrow
        inx
        jmp ei_keyup1

ei_keyupdownwave:
        adc editor_waveindex
        sta editor_waveindex
        rts
ei_keyupdownarp:
        adc editor_arpindex
        sta editor_arpindex
        rts
ei_keyupdownfilter:
        adc editor_filterindex
        sta editor_filterindex
        rts

ei_keyleft:
        lda #0
ei_keyleft1:
        sta editor_instcol
        rts

ei_keyright:
        lda #1
        bne ei_keyleft1

; Move to next field.
ei_keynextfield:
        ldx editor_instfield
        inx
        cpx #4
        bmi ei_keynextfield1
        ldx #0
ei_keynextfield1:
        stx editor_instfield
        rts

; Move to previous field.
ei_keyprevfield:
        ldx editor_instfield
        dex
        bpl ei_keyprevfield1
        ldx #3
ei_keyprevfield1:
        stx editor_instfield
        rts

; Move up 16 lines up/down in tables.
ei_keypgupdn:
        lda shiftflags
        lsr
        lda #$08
        bcc ei_keypgupdndo
        lda #$f8
ei_keypgupdndo:
        clc
        ldx editor_instfield
        dex
        beq ei_keypgupdnwave
        dex
        beq ei_keypgupdnarp
        dex
        beq ei_keypgupdnfilter
        rts
ei_keypgupdnwave:
        adc editor_waveindex
        sta editor_waveindex
        rts
ei_keypgupdnarp:
        adc editor_arpindex
        sta editor_arpindex
        rts
ei_keypgupdnfilter:
        adc editor_filterindex
        sta editor_filterindex
        rts

; Go to wave or instrument table to position under cursor.
ei_keygototable:
        ldx #0
        lda editor_instfield            ; If not in inst params, go there.
        bne ei_keygototable1
        ldy editor_currentinst
        inx
        lda editor_instrow
        cmp #INST_WAVETABLESTART
        beq ei_keygototablewavestart
        cmp #INST_WAVETABLEEND
        beq ei_keygototablewaveend
        cmp #INST_WAVETABLELOOP
        beq ei_keygototablewaveloop
        inx
        cmp #INST_ARPTABLESTART
        beq ei_keygototablearpstart
        cmp #INST_ARPTABLEEND
        beq ei_keygototablearpend
        cmp #INST_ARPTABLELOOP
        beq ei_keygototablearploop
        inx
        cmp #INST_FILTERTABLESTART
        beq ei_keygototablefilterstart
        cmp #INST_FILTERTABLEEND
        beq ei_keygototablefilterend
        cmp #INST_FILTERTABLELOOP
        beq ei_keygototablefilterloop
        rts

ei_keygototablewavestart:
        lda INSTRUMENTS_WAVETABLESTART,y
        bcs ei_keygototablewave
ei_keygototablewaveend:
        lda INSTRUMENTS_WAVETABLEEND,y
        bcs ei_keygototablewave
ei_keygototablewaveloop:
        lda INSTRUMENTS_WAVETABLELOOP,y
        bcs ei_keygototablewave

ei_keygototablearpstart:
        lda INSTRUMENTS_ARPTABLESTART,y
        bcs ei_keygototablearp
ei_keygototablearpend:
        lda INSTRUMENTS_ARPTABLEEND,y
        bcs ei_keygototablearp
ei_keygototablearploop:
        lda INSTRUMENTS_ARPTABLELOOP,y
        bcs ei_keygototablearp

ei_keygototablefilterstart:
        lda INSTRUMENTS_FILTERTABLESTART,y
        bcs ei_keygototablefilter
ei_keygototablefilterend:
        lda INSTRUMENTS_FILTERTABLEEND,y
        bcs ei_keygototablefilter
ei_keygototablefilterloop:
        lda INSTRUMENTS_FILTERTABLELOOP,y
        bcs ei_keygototablefilter

ei_keygototablewave:
        sta editor_waveindex
        bcs ei_keygototable1
ei_keygototablearp:
        sta editor_arpindex
        bcs ei_keygototable1
ei_keygototablefilter:
        sta editor_filterindex
ei_keygototable1:
        stx editor_instfield
        lda #0
        sta editor_instcol
        rts

; Insert into wave or arpeggio table.
ei_insert:
        ldx editor_instfield
        dex
        beq ei_insertwave
        dex
        beq ei_insertarp
        dex
        beq ei_insertfilter
        rts
ei_insertwave:
        lda #$ff
        sta list_length
        lda editor_waveindex
        ldx #<WAVETABLE
        ldy #>WAVETABLE
        jsr list_insert
; Update all indices that affected by the insertion.
        lda editor_waveindex
        ldx #<INSTRUMENTS_WAVETABLESTART
        ldy #>INSTRUMENTS_WAVETABLESTART
        jsr ei_insertfix
        lda editor_waveindex
        ldx #<INSTRUMENTS_WAVETABLEEND
        ldy #>INSTRUMENTS_WAVETABLEEND
        jsr ei_insertfix
        lda editor_waveindex
        ldx #<INSTRUMENTS_WAVETABLELOOP
        ldy #>INSTRUMENTS_WAVETABLELOOP
        jmp ei_insertfix
ei_insertarp:
        lda #$ff
        sta list_length
        lda editor_arpindex
        ldx #<ARPEGGIOTABLE
        ldy #>ARPEGGIOTABLE
        jsr list_insert
; Update all indices that affected by the insertion.
        lda editor_arpindex
        ldx #<INSTRUMENTS_ARPTABLESTART
        ldy #>INSTRUMENTS_ARPTABLESTART
        jsr ei_insertfix
        lda editor_arpindex
        ldx #<INSTRUMENTS_ARPTABLEEND
        ldy #>INSTRUMENTS_ARPTABLEEND
        jsr ei_insertfix
        lda editor_arpindex
        ldx #<INSTRUMENTS_ARPTABLELOOP
        ldy #>INSTRUMENTS_ARPTABLELOOP
        jmp ei_insertfix
ei_insertfilter:
        lda #$ff
        sta list_length
        lda editor_filterindex
        ldx #<FILTERTABLE
        ldy #>FILTERTABLE
        jsr list_insert
; Update all indices that affected by the insertion.
        lda editor_filterindex
        ldx #<INSTRUMENTS_FILTERTABLESTART
        ldy #>INSTRUMENTS_FILTERTABLESTART
        jsr ei_insertfix
        lda editor_filterindex
        ldx #<INSTRUMENTS_FILTERTABLEEND
        ldy #>INSTRUMENTS_FILTERTABLEEND
        jsr ei_insertfix
        lda editor_filterindex
        ldx #<INSTRUMENTS_FILTERTABLELOOP
        ldy #>INSTRUMENTS_FILTERTABLELOOP
        jmp ei_insertfix

; Update wave and arpeggio table indices that have been affected by insertion.
; A: editor_waveindex or editor_arpindex
; Y:X: pointer to field that gets updated
ei_insertfix:
        sta ei_insertfixindex+1
        stx editor_instptr
        sty editor_instptr+1
        ldy #MAX_INSTRUMENTS-1
ei_insertfixloop:
        lda (editor_instptr),y
        cmp #$ff                        ; If index was $ff, never increment.
        beq ei_insertfix1
ei_insertfixindex:
        cmp #$ff
        beq ei_insertfix1
        bcc ei_insertfix1
        clc
        adc #1
        sta (editor_instptr),y
ei_insertfix1:
        dey
        bne ei_insertfixloop
        rts

; Delete from wave or arpeggio table.
ei_delete:
        ldx editor_instfield
        dex
        beq ei_deletewave
        dex
        beq ei_deletearp
        dex
        beq ei_deletefilter
ei_deletedone:
        rts
ei_deletewave:
        ldx editor_waveindex
        beq ei_deletedone
        dex
        stx editor_waveindex
        lda #$ff
        sta list_length
        lda #$00
        sta list_defaultelement
        txa
        ldx #<WAVETABLE
        ldy #>WAVETABLE
        jsr list_delete
; Update all indices that affected by the deletion.
        lda editor_waveindex
        ldx #<INSTRUMENTS_WAVETABLESTART
        ldy #>INSTRUMENTS_WAVETABLESTART
        jsr ei_deletefix
        lda editor_waveindex
        ldx #<INSTRUMENTS_WAVETABLEEND
        ldy #>INSTRUMENTS_WAVETABLEEND
        jsr ei_deletefix
        lda editor_waveindex
        ldx #<INSTRUMENTS_WAVETABLELOOP
        ldy #>INSTRUMENTS_WAVETABLELOOP
        jmp ei_deletefix
ei_deletearp:
        ldx editor_arpindex
        beq ei_deletedone
        dex
        stx editor_arpindex
        lda #$ff
        sta list_length
        lda #$00
        sta list_defaultelement
        txa
        ldx #<ARPEGGIOTABLE
        ldy #>ARPEGGIOTABLE
        jsr list_delete
; Update all indices that affected by the deletion.
        lda editor_arpindex
        ldx #<INSTRUMENTS_ARPTABLESTART
        ldy #>INSTRUMENTS_ARPTABLESTART
        jsr ei_deletefix
        lda editor_arpindex
        ldx #<INSTRUMENTS_ARPTABLEEND
        ldy #>INSTRUMENTS_ARPTABLEEND
        jsr ei_deletefix
        lda editor_arpindex
        ldx #<INSTRUMENTS_ARPTABLELOOP
        ldy #>INSTRUMENTS_ARPTABLELOOP
        jmp ei_deletefix
ei_deletefilter:
        ldx editor_filterindex
        beq ei_deletedone
        dex
        stx editor_filterindex
        lda #$ff
        sta list_length
        lda #$00
        sta list_defaultelement
        txa
        ldx #<FILTERTABLE
        ldy #>FILTERTABLE
        jsr list_delete
; Update all indices that affected by the deletion.
        lda editor_filterindex
        ldx #<INSTRUMENTS_FILTERTABLESTART
        ldy #>INSTRUMENTS_FILTERTABLESTART
        jsr ei_deletefix
        lda editor_filterindex
        ldx #<INSTRUMENTS_FILTERTABLEEND
        ldy #>INSTRUMENTS_FILTERTABLEEND
        jsr ei_deletefix
        lda editor_filterindex
        ldx #<INSTRUMENTS_FILTERTABLELOOP
        ldy #>INSTRUMENTS_FILTERTABLELOOP
        jmp ei_deletefix

; Update wave and arpeggio table indices that have been affected by deletion.
; A: editor_waveindex or editor_arpindex
; Y:X: pointer to field that gets updated
ei_deletefix:
        sta ei_deletefixindex+1
        stx editor_instptr
        sty editor_instptr+1
        ldy #MAX_INSTRUMENTS-1
ei_deletefixloop:
        lda (editor_instptr),y
ei_deletefixindex:
        cmp #$00                        ; Self modifying code.
        beq ei_deletefix1
        bcc ei_deletefix1
        sec
        sbc #1
        sta (editor_instptr),y
ei_deletefix1:
        dey
        bne ei_deletefixloop
        rts

; Jump to top of a table in intrument editor.
ei_keyhome:
        lda #0
        ldx editor_instfield
        dex
        beq ei_keyhomewave
        dex
        beq ei_keyhomearp
        dex
        beq ei_keyhomefilter
        sta editor_instrow
        rts
ei_keyhomewave:
        sta editor_waveindex
        rts
ei_keyhomearp:
        sta editor_arpindex
        rts
ei_keyhomefilter:
        sta editor_filterindex
        rts

; Edit instrument name.
ei_editname:
        lda editor_currentinst
        jsr editor_makeinstnameptr
        lda #INSTRUMENTNAMELEN
        ldx #5
        ldy #6
        jmp console_getstringatxy

; Cut instrument to buffer.
ei_cutinst:
; First copy to buffer.
        jsr ei_copyinst
; Delete name.
        ldy #INSTRUMENTNAMELEN-1
        lda #$20
ei_cutinstnameloop:
        sta (stringptr),y
        dey
        bpl ei_cutinstnameloop
; Delete parameters.
        lda #<INSTRUMENTS
        sta editor_instptr
        lda #>INSTRUMENTS
        sta editor_instptr+1
        ldy editor_currentinst
        ldx #INSTRUMENTLEN-1
ei_cutinstdataloop:
        lda #0
        sta (editor_instptr),y
        lda editor_instptr
        clc
        adc #MAX_INSTRUMENTS
        sta editor_instptr
        lda editor_instptr+1
        adc #0
        sta editor_instptr+1
        dex
        bpl ei_cutinstdataloop
        rts

; Copy instrument to buffer.
ei_copyinst:
; Copy name.
        lda editor_currentinst
        jsr editor_makeinstnameptr
        ldy #INSTRUMENTNAMELEN-1
ei_copyinstnameloop:
        lda (stringptr),y
        sta editor_instnamecopybuffer,y
        dey
        bpl ei_copyinstnameloop
; Copy parameters.
        lda #<INSTRUMENTS
        sta editor_instptr
        lda #>INSTRUMENTS
        sta editor_instptr+1
        ldx #INSTRUMENTLEN-1
ei_copyinstdataloop:
        ldy editor_currentinst
        lda (editor_instptr),y
        ldy #0
        sta (editor_instptr),y
        lda editor_instptr
        clc
        adc #MAX_INSTRUMENTS
        sta editor_instptr
        lda editor_instptr+1
        adc #0
        sta editor_instptr+1
        dex
        bpl ei_copyinstdataloop
; Indicate valid data in instrument copy boffer.
        lda #1
        sta editor_instcopybuffervalid
        rts

; Paste instrument from buffer.
ei_pasteinst:
; If there is no valid data in instrument copy boffer, do nothing.
        lda editor_instcopybuffervalid
        beq ei_pasteinstdone
; Paste name.
        lda editor_currentinst
        jsr editor_makeinstnameptr
        ldy #INSTRUMENTNAMELEN-1
ei_pasteinstnameloop:
        lda editor_instnamecopybuffer,y
        sta (stringptr),y
        dey
        bpl ei_pasteinstnameloop
; Paste parameters.
        lda #<INSTRUMENTS
        sta editor_instptr
        lda #>INSTRUMENTS
        sta editor_instptr+1
        ldx #INSTRUMENTLEN-1
ei_pasteinstdataloop:
        ldy #0
        lda (editor_instptr),y
        ldy editor_currentinst
        sta (editor_instptr),y
        lda editor_instptr
        clc
        adc #MAX_INSTRUMENTS
        sta editor_instptr
        lda editor_instptr+1
        adc #0
        sta editor_instptr+1
        dex
        bpl ei_pasteinstdataloop
ei_pasteinstdone:
        rts

; Set filter block begin.
ei_setblockbeg:
        ldx editor_instfield
        cpx #3
        bne ei_checkblocklimits1        ; If not in filter table, do nothing.
        lda editor_filterindex
        sta editor_filterblockbeg
        lda editor_filterblockflags
        ora #BLOCK_BEGINSET
        bne ei_checkblocklimits         ; short jump

; Set filter block end.
ei_setblockend:
        ldx editor_instfield
        cpx #3
        bne ei_checkblocklimits1        ; If not in filter table, do nothing.
        lda editor_filterindex
        sta editor_filterblockend
        lda editor_filterblockflags
        ora #BLOCK_ENDSET
; Force blockbeg<=blockend.
ei_checkblocklimits:
        sta editor_filterblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        bne ei_checkblocklimits1        ; Begin or end unset -> nothing to do.
        lda editor_filterblockbeg
        cmp editor_filterblockend
        bcc ei_checkblocklimits1        ; beg<end -> nothing to do.
        ldy editor_filterblockend
        sta editor_filterblockend
        sty editor_filterblockbeg
ei_checkblocklimits1:
        rts

; Unselect filter block.
ei_unselectblock:
        ldx editor_instfield
        cpx #3
        bne ei_unselectblockdone        ; If not in filter table, do nothing.
        lda #$00
        sta editor_filterblockflags
ei_unselectblockdone:
        rts

; Increment values in filter block. Wraparound is _not_ handled.
ei_incblock:
        lda #$fe                        ; opcode for INC $FFFF,X
        .byte $2c                       ; BIT $FFFF

; Increment values in filter block. Wraparound is _not_ handled.
ei_decblock:
        lda #$de                        ; opcode for DEC $FFFF,X
; Increment or decrement a block of filter values.
;  Input: A: opcode ($fe for inc, $de for dec)
        ldx editor_instfield
        cpx #3
        bne ei_incdecblockdone          ; If not in filter table, do nothing.
        ldx editor_filterblockflags
        cpx #BLOCK_BEGINSET+BLOCK_ENDSET
        bne ei_incdecblockdone
        sta ei_incdecblockdo
        ldx editor_filterblockbeg
ei_incdecblockloop:
        cpx editor_filterblockend
        bcc ei_incdecblockdo
        bne ei_incdecblockdone
ei_incdecblockdo:
        inc FILTERTABLE,x
        inx
        bne ei_incdecblockloop
ei_incdecblockdone:
        rts

; Fill filter block with linearly interpolated values.
ei_fillblock:
        ldx editor_instfield
        cpx #3
        bne ei_fillblockdone            ; If not in filter table, do nothing.
        ldx #0
        stx div16_divisor+1
        dex
        stx div16_dividend
        lda editor_filterblockend
        sec
        sbc editor_filterblockbeg
        sta div16_divisor
        ldx editor_filterblockend
        lda FILTERTABLE,x
        sec
        ldx editor_filterblockbeg
        sbc FILTERTABLE,x
        sta div16_dividend+1
        bcc ei_fillblockdown

; Fill block where FILTERTABLE[blockbeg] < FILTERTABLE[blockend]
        jsr div16
        lda #$00                        ; fractional part of first element
        ldx #$65                        ; opcode for ADC
        ldy #$18                        ; opcode for CLC
        bne ei_fillblockgo

; Fill block where FILTERTABLE[blockbeg] > FILTERTABLE[blockend]
ei_fillblockdown:
; Negate difference.
        sec
        sbc #$01
        eor #$ff
        sta div16_dividend+1
        jsr div16
        lda #$ff                        ; fractional part of first element
        ldx #$e5                        ; opcode for SBC
        ldy #$38                        ; opcode for SEC

; Fill block.
;  Input: when FILTERTABLE[blockbeg] < FILTERTABLE[blockend]
;           div16_quotient.w is added to div16_dividend.w
;           A: 0   (fractional part of first element)
;           X: $65 (opcode for ADC)
;           Y: $18 (opcode for CLC)
;  Input: when FILTERTABLE[blockbeg] > FILTERTABLE[blockend]
;           div16_quotient.w is subtracted from div16_dividend.w
;           A: $ff (fractional part of first element)
;           X: $e5 (opcode for SBC)
;           Y: $38 (opcode for SEC)
ei_fillblockgo:
        sta div16_dividend
        sty ei_fillblockdo1
        stx ei_fillblockdo2
        stx ei_fillblockdo3
        ldx editor_filterblockbeg
        lda FILTERTABLE,x
        sta div16_dividend+1
ei_fillblockloop:
        cpx editor_filterblockend
        bcc ei_fillblockdo
        bne ei_fillblockdone
ei_fillblockdo:
        lda div16_dividend
ei_fillblockdo1:
        clc
ei_fillblockdo2:
        adc div16_quotient
        sta div16_dividend
        lda div16_dividend+1
        sta FILTERTABLE,x
ei_fillblockdo3:
        adc div16_quotient+1
        sta div16_dividend+1
        inx
        bne ei_fillblockloop
ei_fillblockdone:
        rts

; ======================================
editor_configmenu:
; ======================================
;  Input: editor_currentkey: key from getin.
; ======================================
        lda editor_currentkey
        beq cm_done
; Try to find action for this key.
        ldx #0
cm_findkey:
        cmp configmenu_keys,x
        beq cm_keyfound
        inx
        inx
        inx
        cpx #CONFIGMENU_KEYS_NUM
        bne cm_findkey

        lda editor_currentkey
        jsr ascii2hexdigit
        bmi cm_done                     ; Not a hex digit
        ldy editor_configrow
        ldx editor_configcolors,y
        jsr replacelownybble
        sta editor_configcolors,y
        jmp cm_done

; Call event handler for the key found.
cm_keyfound:
        jsr editor_clearkey             ; Indicate that key is processed.
        lda configmenu_keys+1,x
        ldy configmenu_keys+2,x
        jmp jsrya

cm_done:
        rts

; ======================================
; Events for keys in config menu.
; ======================================

cm_keyup:
        ldx editor_configrow
        dex
        bpl cm_keyup1
        ldx #EDITOR_COLORSNUM-1
cm_keyup1:
        stx editor_configrow
        rts

cm_keydown:
        ldx editor_configrow
        inx
        cpx #EDITOR_COLORSNUM
        bmi cm_keydown1
        ldx #0
cm_keydown1:
        stx editor_configrow
        rts

; Copy colors to edit buffer.
cm_getcolors:
        ldx #EDITOR_COLORSNUM-1
cm_getcolorsloop:
        lda editor_colors,x
        sta editor_configcolors,x
        dex
        bpl cm_getcolorsloop
        rts

; Copy colors to real colors and reinit screen to take effect.
cm_putcolors:
        ldx #EDITOR_COLORSNUM-1
cm_putcolorsloop:
        lda editor_configcolors,x
        sta editor_colors,x
        dex
        bpl cm_putcolorsloop
        jmp editor_reinit

; Get default color sets .
cm_colorset1:
        ldx #EDITOR_COLORSNUM-1
        .byte $2c                       ; BIT $ffff
cm_colorset2:
        ldx #EDITOR_COLORSNUM+EDITOR_COLORSNUM-1
        .byte $2c                       ; BIT $ffff
cm_colorset3:
        ldx #2*EDITOR_COLORSNUM+EDITOR_COLORSNUM-1
        .byte $2c                       ; BIT $ffff
cm_colorset4:
        ldx #3*EDITOR_COLORSNUM+EDITOR_COLORSNUM-1
        ldy #EDITOR_COLORSNUM-1
cm_colorsetxloop:
        lda editor_colorsets,x
        sta editor_configcolors,y
        dex
        dey
        bpl cm_colorsetxloop
        bmi cm_putcolors                ; Re-init editor to update colors.

; ======================================
editor_specmenu:
; ======================================
;  Input: editor_currentkey: key from getin.
; ======================================
        lda editor_currentkey
        beq sm_done
; Try to find action for this key.
        ldx #0
sm_findkey:
        cmp specmenu_keys,x
        beq sm_keyfound
        inx
        inx
        inx
        cpx #SPECMENU_KEYS_NUM
        bne sm_findkey
        beq sm_done

; Call event handler for the key found.
sm_keyfound:
        jsr editor_clearkey             ; Indicate that key is processed.
        lda specmenu_keys+1,x
        ldy specmenu_keys+2,x
        jmp jsrya

sm_done:
        rts

; ======================================
; Events for keys in specials menu.
; ======================================

; Edit song title.
sm_edittitle:
        lda #<SONGTITLE
        sta stringptr
        lda #>SONGTITLE
        sta stringptr+1
        lda #SONGTITLELEN
        ldx #6
        ldy #6
        jmp console_getstringatxy

; Clear order list, patterns, tracks.
sm_clearsong:
        ldx #<clearsongtext
        ldy #>clearsongtext
        jsr sm_getconfirmation
        tax
        beq sm_clearsongdone
; Stop player.
        jsr editor_stopplayer
        jsr clear_song
sm_clearsongdone:
        jmp editor_initscreen

; Clear instruments.
sm_clearinstruments:
        ldx #<clearinsttext
        ldy #>clearinsttext
        jsr sm_getconfirmation
        tax
        beq sm_clearinstruments0
; Stop player.
        jsr editor_stopplayer
        jsr clear_instruments
sm_clearinstruments0:
        jmp editor_initscreen

; Replace instrument in tracks.
sm_replaceinsttrack:
; Get instrument numbers.
        jsr sm_getreplaceinstnum
        bcs smrit_done                  ; RUN/STOP hit.
        cmp #MAX_INSTRUMENTS
        bcs smrit_done
        jsr sm_getreplacewithinstnum
        bcs smrit_done
        cmp #MAX_INSTRUMENTS
        bcs smrit_done
; Get first and last track number.
        jsr sm_getfirsttrack
        bcs smrit_done                  ; RUN/STOP hit.
        cmp #MAX_TRACKS
        bcs smrit_done
        jsr sm_getlasttrack
        bcs smrit_done
        cmp #MAX_TRACKS
        bcs smrit_done
; If last<first, do nothing.
        lda sm_lasttrack
        cmp sm_firsttrack
        bcc smrit_done
; Get confirmation.
        ldx #<areyousuretext
        ldy #>areyousuretext
        jsr sm_getconfirmation
        tax
        beq smrit_done
; Stop player.
        jsr editor_stopplayer
; Do for all tracks between sm_firsttrack and sm_lasttrack.
smrit_trackloop:
        lda sm_firsttrack
        jsr sm_replaceinst
; Advance to next track.
        lda sm_firsttrack
        cmp sm_lasttrack
        beq smrit_done
        inc sm_firsttrack
        bne smrit_trackloop
smrit_done:
        jmp editor_initscreen

; Replace instrument in patterns.
; sm_firsttrack and sm_lasttrack are pattern numbers here!
sm_replaceinstpattern:
; Get instrument numbers.
        jsr sm_getreplaceinstnum
        bcs smrip_done                  ; RUN/STOP hit.
        cmp #MAX_INSTRUMENTS
        bcs smrip_done
        jsr sm_getreplacewithinstnum
        bcs smrip_done
        cmp #MAX_INSTRUMENTS
        bcs smrip_done
; Get first and last pattern number.
        jsr sm_getfirstpattern
        bcs smrip_done                  ; RUN/STOP hit.
        jsr sm_getlastpattern
        bcs smrip_done
; If last<first, do nothing.
        lda sm_lasttrack
        cmp sm_firsttrack
        bcc smrip_done
; Get confirmation.
        ldx #<areyousuretext
        ldy #>areyousuretext
        jsr sm_getconfirmation
        tax
        beq smrip_done
; Stop player.
        jsr editor_stopplayer
; Do for all patterns between sm_firsttrack and sm_lasttrack.
smrip_patternloop:
        lda sm_firsttrack
        jsr editor_makepatternpointer
        ldy #0
        lda (editor_patternptr),y
        jsr sm_replaceinst
        ldy #2
        lda (editor_patternptr),y
        jsr sm_replaceinst
        ldy #4
        lda (editor_patternptr),y
        jsr sm_replaceinst
; Advance to next pattern.
        lda sm_firsttrack
        cmp sm_lasttrack
        beq smrip_done
        inc sm_firsttrack
        bne smrip_patternloop
smrip_done:
        jmp editor_initscreen

; Replace instruments in track number A.
sm_replaceinst:
        jsr editor_maketrackpointer
; Do for rows 0..63 in each track.
        lda #0
        sta editor_getputtrackrow
smri_rowloop:
        lda editor_getputtrackrow
        cmp #64
        beq smri_done
        jsr editor_gettrackrowany
        lda editor_trackinst
        cmp sm_replaceinstnum
        bne smri_cont
        lda sm_replacewithinstnum
        sta editor_trackinst
        jsr editor_puttrackrowany
smri_cont:
        inc editor_getputtrackrow
        bne smri_rowloop
smri_done:
        rts

; Swap tracks 1-2 in patterns.
; sm_firsttrack and sm_lasttrack are pattern numbers here!
sm_swap12:
; Get first and last pattern number.
        jsr sm_getfirstpattern
        bcs sm_swap12done               ; RUN/STOP hit.
        jsr sm_getlastpattern
        bcs sm_swap12done
; If last<first, do nothing.
        lda sm_lasttrack
        cmp sm_firsttrack
        bcc sm_swap12done
; Get confirmation.
        ldx #<areyousuretext
        ldy #>areyousuretext
        jsr sm_getconfirmation
        tax
        beq sm_swap12done
; Stop player.
        jsr editor_stopplayer
sm_swap12loop:
        lda sm_firsttrack
        jsr editor_makepatternpointer
        ldy #0
        lda (editor_patternptr),y
        pha
        iny
        lda (editor_patternptr),y
        pha
        ldy #2
        lda (editor_patternptr),y
        ldy #0
        sta (editor_patternptr),y
        ldy #3
        lda (editor_patternptr),y
        ldy #1
        sta (editor_patternptr),y
        pla
        ldy #3
        sta (editor_patternptr),y
        pla
        dey
        sta (editor_patternptr),y
; Advance to next pattern.
        lda sm_firsttrack
        cmp sm_lasttrack
        beq sm_swap12done
        inc sm_firsttrack
        bne sm_swap12loop
sm_swap12done:
        jmp editor_initscreen

; Swap tracks 2-3 in patterns.
; sm_firsttrack and sm_lasttrack are pattern numbers here!
sm_swap23:
; Get first and last pattern number.
        jsr sm_getfirstpattern
        bcs sm_swap23done               ; RUN/STOP hit.
        jsr sm_getlastpattern
        bcs sm_swap23done
; If last<first, do nothing.
        lda sm_lasttrack
        cmp sm_firsttrack
        bcc sm_swap23done
; Get confirmation.
        ldx #<areyousuretext
        ldy #>areyousuretext
        jsr sm_getconfirmation
        tax
        beq sm_swap23done
; Stop player.
        jsr editor_stopplayer
sm_swap23loop:
        lda sm_firsttrack
        jsr editor_makepatternpointer
        ldy #2
        lda (editor_patternptr),y
        pha
        iny
        lda (editor_patternptr),y
        pha
        ldy #4
        lda (editor_patternptr),y
        ldy #2
        sta (editor_patternptr),y
        ldy #5
        lda (editor_patternptr),y
        ldy #3
        sta (editor_patternptr),y
        pla
        ldy #5
        sta (editor_patternptr),y
        pla
        dey
        sta (editor_patternptr),y
; Advance to next pattern.
        lda sm_firsttrack
        cmp sm_lasttrack
        beq sm_swap23done
        inc sm_firsttrack
        bne sm_swap23loop
sm_swap23done:
        jmp editor_initscreen

; Swap tracks 3-1 in patterns.
; sm_firsttrack and sm_lasttrack are pattern numbers here!
sm_swap31:
; Get first and last pattern number.
        jsr sm_getfirstpattern
        bcs sm_swap31done               ; RUN/STOP hit.
        jsr sm_getlastpattern
        bcs sm_swap31done
; If last<first, do nothing.
        lda sm_lasttrack
        cmp sm_firsttrack
        bcc sm_swap31done
; Get confirmation.
        ldx #<areyousuretext
        ldy #>areyousuretext
        jsr sm_getconfirmation
        tax
        beq sm_swap31done
; Stop player.
        jsr editor_stopplayer
sm_swap31loop:
        lda sm_firsttrack
        jsr editor_makepatternpointer
        ldy #4
        lda (editor_patternptr),y
        pha
        iny
        lda (editor_patternptr),y
        pha
        ldy #0
        lda (editor_patternptr),y
        ldy #4
        sta (editor_patternptr),y
        ldy #1
        lda (editor_patternptr),y
        ldy #5
        sta (editor_patternptr),y
        pla
        ldy #1
        sta (editor_patternptr),y
        pla
        dey
        sta (editor_patternptr),y
; Advance to next pattern.
        lda sm_firsttrack
        cmp sm_lasttrack
        beq sm_swap31done
        inc sm_firsttrack
        bne sm_swap31loop
sm_swap31done:
        jmp editor_initscreen

smess_index:    .byte 0
smess_col:      .byte 0

; Edit song start positions.
sm_editsongstarts:
        lda #$00
        sta smess_index
        sta smess_col
smess_loop:
        jsr getin
        cmp #KEY_RETURN
        bne smess_notexit
        jmp editor_initscreen
smess_notexit:
        cmp #KEY_LEFT
        bne smess_notleft
        ldx #0
        stx smess_col
        bcs smess_cont
smess_notleft:
        cmp #KEY_RIGHT
        bne smess_notright
        ldx #1
        stx smess_col
        bcs smess_cont
smess_notright:
        cmp #KEY_UP
        bne smess_notup
        dec smess_index
        bcs smess_cont
smess_notup:
        cmp #KEY_DOWN
        bne smess_notdown
        inc smess_index
        bcs smess_cont
smess_notdown:
        jsr ascii2hexdigit
        bmi smess_cont
        ldy smess_index
        ldx smess_col
        php
        ldx SONGSTARTTABLE,y
        plp
        beq smess_replacehigh
        jsr replacelownybble
        jmp smess_replaced
smess_replacehigh:
        jsr replacehighnybble
smess_replaced:
        sta SONGSTARTTABLE,y
        lda smess_col
        eor #1
        sta smess_col
        bne smess_cont
        inc smess_index
smess_cont:
; Display table.
        lda #34
        sta display_x
        lda #8
        sta display_y
        lda #17
        sta display_height
        lda smess_index
        sta display_index
        lda #8
        sta display_line
        lda #<SONGSTARTTABLE
        sta display_datasrc
        lda #>SONGSTARTTABLE
        sta display_datasrc+1
        lda #$00
        sta display_indexhighlight
        sta display_datahighlight
        jsr write_list
; Set cursor position.
        ldy #16
        lda #37
        clc
        adc smess_col
        tax
        jsr console_setspritecursor
        jmp smess_loop

; ======================================
sm_getconfirmation:
; Ask for confirmation for destructive operation.
; ======================================
;  Input: Y:X: pointer to prompt
; Output: A: 0: no
;            1: yes
; ======================================
        stx stringptr
        sty stringptr+1
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #0
        ldy #24
        jsr console_setcursorpos
        jsr console_writestring
        ldx #<confirmationtext
        ldy #>confirmationtext
        jsr console_writestringxy
        jsr console_hidespritecursor
        jsr console_waitkey
        tax
        lda #$01
        cpx #KEY_Y
        beq smgc_done
        lda #$00
smgc_done:
        rts

; ======================================
sm_getfirsttrack:
; Get first track number for read/write tracks and replace instrument ops.
; ======================================
; Output: sm_firsttrack
;         A: =sm_firsttrack
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit.
; ======================================
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #2
        ldy #23
        jsr console_setcursorpos
        ldx #<firsttracktext
        ldy #>firsttracktext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$00
        ldx #14
        ldy #23
        jsr console_gethexatxy
        sta sm_firsttrack
        rts

; ======================================
sm_getlasttrack:
; Get last track number for write tracks and replace instrument ops.
; ======================================
; Output: sm_lasttrack
;         A: =sm_lasttrack
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit.
; ======================================
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #25
        ldy #23
        jsr console_setcursorpos
        ldx #<lasttracktext
        ldy #>lasttracktext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$00
        ldx #36
        ldy #23
        jsr console_gethexatxy
        sta sm_lasttrack
        rts

; ======================================
sm_getfirstpattern:
; Get first pattern number for read/write patterns and replace instrument ops.
; ======================================
; Output: sm_firsttrack
;         A: =sm_firsttrack
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit.
; ======================================
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #0
        ldy #23
        jsr console_setcursorpos
        ldx #<firstpatterntext
        ldy #>firstpatterntext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$00
        ldx #14
        ldy #23
        jsr console_gethexatxy
        sta sm_firsttrack
        rts

; ======================================
sm_getlastpattern:
; Get last pattern number for write patterns and replace instrument ops.
; ======================================
; Output: sm_lasttrack
;         A: =sm_lasttrack
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit.
; ======================================
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #23
        ldy #23
        jsr console_setcursorpos
        ldx #<lastpatterntext
        ldy #>lastpatterntext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$00
        ldx #36
        ldy #23
        jsr console_gethexatxy
        sta sm_lasttrack
        rts

; ======================================
sm_getreplaceinstnum:
; Get instrument number that will be replaced.
; ======================================
; Output: sm_replaceinstnum
;         A: =sm_replaceinstnum
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit.
; ======================================
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #3
        ldy #22
        jsr console_setcursorpos
        ldx #<replaceinsttext
        ldy #>replaceinsttext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$00
        ldx #14
        ldy #22
        jsr console_gethexatxy
        sta sm_replaceinstnum
        rts

; ======================================
sm_getreplacewithinstnum:
; Get instrument number that replaces.
; ======================================
; Output: sm_replacewithinstnum
;         A: =sm_replacewithinstnum
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit.
; ======================================
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #20
        ldy #22
        jsr console_setcursorpos
        ldx #<replacewithinsttext
        ldy #>replacewithinsttext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$00
        ldx #36
        ldy #22
        jsr console_gethexatxy
        sta sm_replacewithinstnum
        rts

; ======================================
editor_diskmenu:
; ======================================
;  Input: editor_currentkey: key from getin.
; ======================================
        lda editor_currentkey
        beq dm_done
; Try to find action for this key.
        ldx #0
dm_findkey:
        cmp diskmenu_keys,x
        beq dm_keyfound
        inx
        inx
        inx
        cpx #DISKMENU_KEYS_NUM
        bne dm_findkey
        beq dm_done

; Call event handler for the key found.
dm_keyfound:
        jsr dm_clearstatusline
        jsr editor_clearkey             ; Indicate that key is processed.
        lda diskmenu_keys+1,x
        ldy diskmenu_keys+2,x
        jmp jsrya

dm_done:
        rts

; ======================================
dm_clearstatusline:
; Clear status line in disk menu.
; ======================================
        lda #$a0
        ldy #32
dmcsl_loop:
        sta $0400+6*40+7,y
        dey
        bpl dmcsl_loop
        rts

; ======================================
dm_displaydrivestatus:
; Display drive status from buffer.
; ======================================
        jsr dm_clearstatusline
        ldx #7
        ldy #6
        jsr console_setcursorpos
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask
        ldx #<io_drivestatus
        ldy #>io_drivestatus
        jmp console_writestringxy

; ======================================
; Events for keys in diskmenu.
; ======================================

; Cycle through device numbers 8-31.
dm_incdiskdevice:
        ldx io_diskdevice
        inx
        cpx #32
        bmi dm_decdiskdevice0
        ldx #8
        bne dm_decdiskdevice0

; Cycle through device numbers 8-31.
dm_decdiskdevice:
        ldx io_diskdevice
        dex
        cpx #8
        bpl dm_decdiskdevice0
        ldx #31
dm_decdiskdevice0:
        stx io_diskdevice
        rts

; ======================================
; Directory listing,
; ======================================
dm_directory:
; Stop playing.
        jsr editor_stopplayer
        lda #$37
        sta $01                         ; We need BASIC ROM now.
; Set colors, ROM font, sprite off.
        ldx #$00
        stx $d020
        stx $d021
        stx $0291                       ; Enable case-switching.
        ldx #$1b
        stx $d011                       ; Disable ECM.
        ldx #$14
        stx $d018                       ; Set ROM font.
        ldx #$00
        stx $d015                       ; Disable all sprites.
; Clear screen.
        lda #155                        ; Light grey characters.
        jsr chrout
        lda #147                        ; Clear screen.
        jsr chrout
; Open directory file.
        lda #$24                        ; $ - filename for dir.
        sta io_filename
        lda #1
        sta io_filenamelen
        ldy #0
        jsr io_openforread
        bcs dmd_end                     ; Disk error.
        jsr chrin
        jsr chrin
dmd_loop:
        lda shiftflags                  ; Pause while SHIFT is pressed.
        lsr
        bcs dmd_loop
        jsr udtim                       ; Exit when RUN/STOP is pressed.
        jsr stop
        beq dmd_end
        lda status
        bne dmd_end
        jsr chrin
;        cmp #$01
;        bne dmd_loop
        jsr chrin
        lda status
        bne dmd_end
        jsr chrin
        tax
        jsr chrin
        jsr $bdcd                       ; Print X:A.
        lda #32
        jsr chrout
dmd_nameloop:
        jsr chrin
        cmp #$00
        beq dmd_nameend
        jsr chrout
        lda status
        bne dmd_end
        beq dmd_nameloop
dmd_nameend:
        lda #13
        jsr chrout
        jmp dmd_loop
dmd_end:
        jsr io_close
; Print "press eny key."
        lda #<dm_pressanykeytext
        ldy #>dm_pressanykeytext
        jsr $ab1e
        lda #0                          ; Clear keyboard buffer.
        sta $c6
        jsr console_waitkey
        lda #$36                        ; Hide BASIC ROM.
        sta $01
        jmp editor_reinit

; ======================================
dm_loadsong:
; Load song. (raw data only)
; ======================================
; Read filename, if non-empty, clear current song and load.
        jsr dm_getloadfilename
        bcs dmls_quit                   ; RUN/STOP hit.
        lda io_filenamelen
        beq dmls_quit                   ; No filename entered.
; Stop player.
        jsr editor_stopplayer
; Open input file and check load address.
        jsr io_openforreadwithstatusline
        bcs dmls_done                   ; Disk error.
; Check load address (first two bytes). It must be either:
; $4000 for unpacked songs.
; $4c52 for RLE packed songs. (That reads "RL" in the file.)
        jsr io_getchar                  ; Low byte of load address.
        pha
        jsr io_getchar                  ; High byte of load address.
        tax
        pla
        beq dmls_unpacked
        cmp #$52
        bne dmls_done                   ; Not $00 or $52 -> error.
        cpx #$4c
        bne dmls_done                   ; Load address != $4c52 -> error.
        stx io_rlefile                  ; Load address says it is RLE.
        beq dmls_startload
dmls_unpacked:
        cpx #$40
        bne dmls_done                   ; Load address != $4000 -> error.
dmls_startload:
; Clear everything from the current song.
        jsr clear_all
; Start loading.
        ldx #<ORDERLIST
        ldy #>ORDERLIST
        jsr io_readxy
; Jump to order 0.
        lda #0
        sta ordernumber
dmls_done:
        jsr io_close
; Redraw screen to clear the 'enter filename'.
dmls_quit:
        jmp editor_initscreen

; ======================================
dm_savesong:
; Save song. (raw data only)
; ======================================
; Read filename, if non-empty, find last track and save unpacked memory.
        jsr dm_getsavefilename
        bcs dmss_quit                   ; RUN/STOP hit.
        lda io_filenamelen
        beq dmss_quit                   ; No filename entered.
; Stop player.
        jsr editor_stopplayer
; Find out last track used.
        lda #$00
        sta dm_savesongpattern
        sta dm_savesonglasttrack
dmss_findlasttrack:
        lda dm_savesongpattern
        jsr editor_makepatternpointer
        ldy #0
        lda (editor_patternptr),y
        cmp dm_savesonglasttrack
        bcc dmss_findlasttrack1
        sta dm_savesonglasttrack
dmss_findlasttrack1:
        iny
        iny
        lda (editor_patternptr),y
        cmp dm_savesonglasttrack
        bcc dmss_findlasttrack2
        sta dm_savesonglasttrack
dmss_findlasttrack2:
        iny
        iny
        lda (editor_patternptr),y
        cmp dm_savesonglasttrack
        bcc dmss_findlasttrack3
        sta dm_savesonglasttrack
dmss_findlasttrack3:
        inc dm_savesongpattern
        bne dmss_findlasttrack
; Save everything from $4000 to the address of the last track.
        lda dm_savesonglasttrack
        jsr editor_maketrackpointer
; Add last track's length to actually save it.
        lda editor_trackptr
        clc
        adc #192
        sta io_saveend
        lda editor_trackptr+1
        adc #0
        sta io_saveend+1
        lda #$01                        ; Save song in RLE file.
        ldx #<ORDERLIST
        ldy #>ORDERLIST
        jsr io_save
; Redraw screen to clear the 'enter filename' and other input.
dmss_quit:
        jmp editor_initscreen

; ======================================
dm_import10song:
; Import song from Odin Tracker 1.0x.
; ======================================
        jsr dm_getloadfilename
        bcs dmss_quit                   ; RUN/STOP hit.
        lda io_filenamelen
        beq dmss_quit                   ; No filename entered.
; Stop player.
        jsr editor_stopplayer
; Open input file and check load address.
        jsr io_openforreadwithstatusline
        bcs dmi10s_done                 ; Disk error.
; Check load address (first two bytes). It must be $4000.
        jsr io_getchar                  ; Low byte of load address.
        pha
        jsr io_getchar                  ; High byte of load address.
        tax
        pla
        bne dmi10s_done                 ; Fail if load address != $4000.
        cpx #$40
        bne dmi10s_done                 ; Fail if load address != $4000.
; Clear everything from the current song.
        jsr clear_all
; Load into $4000.
        ldx #<ORDERLIST
        ldy #>ORDERLIST
        jsr io_readxy
; Reorganize instruments for the new format. Damn ugly work.
; Copy data in old format to temp buffer.
        lda #2                          ; <(MAX_INSTRUMENTS*INSTRUMENTLEN)
        ldx #>INSTRUMENTS
        ldy #>INSTRUMENTBUFFER
        sty dm_import10songinstloop+2
        jsr memcpypages
; Clear instruments.
        ldx #>INSTRUMENTS
        ldy #2                          ; <(MAX_INSTRUMENTS*INSTRUMENTLEN)
        jsr memclearpages
; Walk linearly on old instruments.
        ldy #$01
        sty dm_import10songinst
        dey
        sty dm_import10songinstloop+1
dm_import10songnextinst:
        lda dm_import10songinst
        sta editor_instptr
        lda #>INSTRUMENTS
        sta editor_instptr+1
; Do not copy the filter parameters, since they are incompatible.
        ldx #0
dm_import10songinstloop:
        lda $ffff,x                     ; Self modifying code.
        sta (editor_instptr),y
        lda editor_instptr
        clc
        adc #MAX_INSTRUMENTS
        sta editor_instptr
        lda editor_instptr+1
        adc #0
        sta editor_instptr+1
        inx
        cpx #INST_FILTERTABLESTART
        bne dm_import10songinstloop
; Advance to next old instrument.
        lda dm_import10songinstloop+1
        clc
        adc #INSTRUMENTLEN
        sta dm_import10songinstloop+1
        lda dm_import10songinstloop+2
        adc #0
        sta dm_import10songinstloop+2
        inc dm_import10songinst
        lda dm_import10songinst
        cmp #MAX_INSTRUMENTS
        bne dm_import10songnextinst
; Jump to order 0.
        lda #0
        sta ordernumber
dmi10s_done:
        jsr io_close
; Redraw screen to clear the 'enter filename'.
dmi10s_quit:
        jmp editor_initscreen

; ======================================
dm_readtracks:
; Read tracks.
; ======================================
        jsr dm_getloadfilename
        bcs dmrt_quit                   ; RUN/STOP hit.
        lda io_filenamelen
        beq dmrt_quit                   ; No filename entered.
; Get the number of track it will be loaded to.
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #0
        ldy #23
        jsr console_setcursorpos
        ldx #<loadattracktext
        ldy #>loadattracktext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$00
        ldx #14
        ldy #23
        jsr console_gethexatxy
        bcs dmrt_quit                   ; RUN/STOP hit.
        cmp #MAX_TRACKS
        bcs dmrt_quit                   ; Invalid track number.
        sta sm_firsttrack
; Stop player.
        jsr editor_stopplayer
; Calculate load address.
        lda sm_firsttrack
        jsr editor_maketrackpointer
; And load.
        ldx editor_trackptr
        ldy editor_trackptr+1
        jsr io_load
; Redraw screen to clear the 'enter filename' and 'load to track' line.
dmrt_quit:
        jmp editor_initscreen

; ======================================
dm_writetracks:
; Write tracks.
; ======================================
        jsr dm_getsavefilename
        bcs dmwt_quit                   ; RUN/STOP hit.
        lda io_filenamelen
        beq dmwt_quit                   ; No filename entered.
; Get first and last track number.
        jsr sm_getfirsttrack
        bcs dmwt_quit                   ; RUN/STOP hit.
        cmp #MAX_TRACKS
        bcs dmwt_quit                   ; Invalid track number.
        jsr sm_getlasttrack
        bcs dmwt_quit                   ; RUN/STOP hit.
        cmp #MAX_TRACKS
        bcs dmwt_quit                   ; Invalid track number.
; If last<first, do nothing.
        lda sm_lasttrack
        cmp sm_firsttrack
        bcc dmwt_quit                   ; sm_firsttrack > sm_lasttrack.
; Stop player.
        jsr editor_stopplayer
; Save all tracks between sm_firsttrack and sm_lasttrack.
; Make pointer to end of last track.
        lda sm_lasttrack
        jsr editor_maketrackpointer
        lda editor_trackptr
        clc
        adc #192
        sta io_saveend
        lda editor_trackptr+1
        adc #0
        sta io_saveend+1
; Make pointer to first track.
        lda sm_firsttrack
        jsr editor_maketrackpointer
        lda #$00                        ; Save plain, not RLE.
        ldx editor_trackptr
        ldy editor_trackptr+1
        jsr io_save
dmwt_quit:
        jmp editor_initscreen

; ======================================
; Pack, relocate and save song.
; ======================================
dm_packandsavesong:
; Stop player.
        jsr editor_stopplayer
        jsr packer_findused
; Find size of player and instrument tables by relocating it to $0000.
        lda #$00
        jsr packer_setrelocdestinations
; Write the size of player code and instrument tables.
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #0
        ldy #17
        jsr console_setcursorpos
        ldx #<playerandinsttext
        ldy #>playerandinsttext
        jsr console_writestringxy
; We have the size of the player and tables in packer_tracksbase??
        lda packer_tracksbase+1
        jsr console_writehex
        lda packer_tracksbase
        jsr console_writehex
        ldx #<bytestext
        ldy #>bytestext
        jsr console_writestringxy
; Write the number of tracks.
        lda #"$"
        ldx #12
        ldy #18
        jsr console_writecharatxy
        lda packer_usedtracksnum
        jsr console_writehex
        ldx #<trackstext
        ldy #>trackstext
        jsr console_writestringxy
; Calculate the size of the tracks.
        lda packer_usedtracksnum
        jsr editor_maketrackpointer
        lda editor_trackptr+1
        sec
        sbc #>TRACKS_BASE
        jsr console_writehex
        lda editor_trackptr
        jsr console_writehex
        ldx #<bytestext
        ldy #>bytestext
        jsr console_writestringxy
; Get relocation address for player.
        ldx #4
        ldy #19
        jsr console_setcursorpos
        ldx #<relocateplayertext
        ldy #>relocateplayertext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #$10
        ldx #25
        ldy #19
        jsr console_gethexatxy
        bcs dmpass_quit0                ; RUN/STOP hit.
; Now we can calculate the relocation addresses.
        jsr packer_setrelocdestinations
; Ask the user if he wants to save the player and the tracks
; in two separete files.
        lda #$00
        jsr console_setcolormask
        ldx #0
        ldy #20
        jsr console_setcursorpos
        ldx #<saveseparatelytext
        ldy #>saveseparatelytext
        jsr console_writestringxy
        jsr console_hidespritecursor
        jsr console_waitkey
        cmp #KEY_N
        beq dmpass_singlefile
        cmp #KEY_Y
        beq dmpass_separately
dmpass_quit0:
        jmp dmpass_quit
; Save everything in one file.
dmpass_singlefile:
        jsr dm_getsavefilename
        bcs dmpass_quit0                ; RUN/STOP hit.
        lda io_filenamelen
        beq dmpass_quit0                ; No filename entered.
; Open output file.
        jsr io_openforwritewithstatuslinenotrle
        bcs dmpass_done0                ; Disk error.
        lda #$00                        ; Write load address.
        jsr io_putchar
        lda packer_playerdestpage
        jsr io_putchar
        jsr packer_relocplayer
        jsr packer_savetables
        jmp dmpass_writetracks
; Save player and instruments in a file and tracks in an other.
dmpass_separately:
; Ask address of tracks.
        ldx #4
        ldy #21
        jsr console_setcursorpos
        ldx #<relocatetrackstext
        ldy #>relocatetrackstext
        jsr console_writestringxy
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda packer_tracksbase+1
        jsr console_writehex
        lda packer_tracksbase
        jsr console_writehex
        lda packer_tracksbase+1
        ldx #25
        ldy #21
        jsr console_gethexatxy
        bcs dmpass_quit0                ; RUN/STOP hit.
        sta packer_tracksbase+1
        lda packer_tracksbase
        ldx #27
        ldy #21
        jsr console_gethexatxy
        bcs dmpass_quit0                ; RUN/STOP hit.
        sta packer_tracksbase
; Prompt for filename of player and instruments and save it.
        lda #$00
        jsr console_setcolormask
        ldx #<saveplayertext
        ldy #>saveplayertext
        lda #22
        jsr dm_getfilename
        bcs dmpass_quit                 ; RUN/STOP hit.
        lda io_filenamelen
        beq dmpass_quit                 ; No filename entered.
; Open output file.
        jsr io_openforwritewithstatuslinenotrle
dmpass_done0:
        bcs dmpass_done                 ; Disk error.
        lda #$00                        ; Write load address.
        jsr io_putchar
        lda packer_playerdestpage
        jsr io_putchar
        jsr packer_relocplayer
        jsr packer_savetables
        jsr io_close
        jsr dm_displaydrivestatus
; Prompt for filename of tracks and save it.
        ldx #<savetrackstext
        ldy #>savetrackstext
        lda #23
        jsr dm_getfilename
        bcs dmpass_quit                 ; RUN/STOP hit.
        lda io_filenamelen
        beq dmpass_quit                 ; No filename entered.
; Open output file.
        jsr io_openforwritewithstatuslinenotrle
        bcs dmpass_done                 ; Disk error.
        lda packer_tracksbase           ; Write load address.
        jsr io_putchar
        lda packer_tracksbase+1
        jsr io_putchar
dmpass_writetracks:
        jsr packer_savetracks
dmpass_done:
        jsr io_close
dmpass_quit:
        jmp editor_initscreen

; ======================================
; Get filename when loading. Prompts: "load filename:"
dm_getloadfilename:
; ======================================
        ldx #<loadfilenametext
        ldy #>loadfilenametext
        lda #22
        bne dm_getfilename

; ======================================
; Get filename when saving. Prompts: "save filename:"
dm_getsavefilename:
; ======================================
        ldx #<savefilenametext
        ldy #>savefilenametext
        lda #22

; ======================================
dm_getfilename:
; Read file name from keyboard.
; ======================================
;  Input: Y:X: -> prompt (must be 14 characters long)
;         A: input on this screenline
; Output: io_filename[]
;         io_filenamelen: number of valid characters in io_filename
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit.
; ======================================
        pha
        pha
        stx stringptr
        sty stringptr+1
; Clear old filename.
        lda #$20
        ldx #15
dmgfn_clear:
        sta io_filename,x
        dex
        bpl dmgfn_clear
; Write prompt.
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        pla
        tay
        ldx #0
        jsr console_setcursorpos
        jsr console_writestring
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda #<io_filename
        sta stringptr
        lda #>io_filename
        sta stringptr+1
        pla
        tay
        lda #$10
        ldx #14
        jsr console_getstringatxy
        bcs dmgfn_quit                  ; RUN/STOP hit.
; Convert from screen codes to ASCII.
        ldx #15
dmgfn_convloop:
        lda io_filename,x
        cmp #$20
        bcs dmgfn_noconv
        ora #$40
        sta io_filename,x
dmgfn_noconv:
        dex
        bpl dmgfn_convloop
; Find out name length.
        ldx #15
        lda #$20
dmgfn_len:
        cmp io_filename,x
        bne dmgfn_lenfound
        dex
        bpl dmgfn_len
dmgfn_lenfound:
        inx
        stx io_filenamelen
        clc
dmgfn_quit:
        rts

; ======================================
io_blockcounterinit:
; Init block counter while load/save. Call after each byte.
;  Input: Y:X -> RLE coded text to display in status line.
; Output: io_blockcounter: 0
;         io_bytecounter: 0
; ======================================
; Update block counter in status line.
        stx stringptr
        sty stringptr+1
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask
        ldx #7
        ldy #6
        jsr console_setcursorpos
        jsr console_writepackedstring
        jsr console_hidespritecursor
; Init block counter.
        lda #0
        sta io_blockcounter
        sta io_blockcounter+1
; Each block has 254 bytes payload.
; (First 2 byte are next track/sector.)
        lda #254
        sta io_bytecounter
        rts

; ======================================
io_blockcounterupdate:
; Update block counter while load/save. Call after each byte.
; A, X, Y are preserved, flags are not.
; ======================================
        dec io_bytecounter
        bne iobcu_done
        pha
        txa
        pha
        tya
        pha
        clc
        lda io_blockcounter
        sed
        adc #1
        sta io_blockcounter
        lda io_blockcounter+1
        adc #0
        cld
        sta io_blockcounter+1
; Display block counter.
        ldx #15
        ldy #6
        jsr console_setcursorpos
        ldx io_blockcounter+1
        lda hexdigitsscreen,x
        jsr console_writechar
        lda io_blockcounter
        jsr console_writehex
; Each block has 254 bytes payload.
; (First 2 byte are next track/sector.)
        lda #254
        sta io_bytecounter
        pla
        tay
        pla
        tax
        pla
iobcu_done:
        rts

; ======================================
io_setdeviceandfilename:
; Set device number and filename.
; ======================================
;  Input: Y: secondary address (0 when loading, 1 when saving, 15 for disk status)
;         io_filename
;         io_filenamelen
; ======================================
; Set device number.
        lda #FILENUMBER
        ldx io_diskdevice
        jsr setlfs
; Set name.
        lda io_filenamelen
        ldx #<io_filename
        ldy #>io_filename
        jmp setnam

; ======================================
io_openforreadwithstatusline:
; Open file for reading and display "loading" in the status line.
; ======================================
;  Input: io_filename
;         io_filenamelen
;         io_rlefile: 0.
; Output: C: set if error.
; ======================================
        ldx #<io_loadingtext
        ldy #>io_loadingtext
        jsr io_blockcounterinit
        ldy #0
        sty io_rlefile

; ======================================
io_openforread:
; Open file for reading.
; ======================================
;  Input: Y: secondary address (0 when loading, 15 for disk status)
;         io_filename
;         io_filenamelen
; Output: C: set if error.
; ======================================
        jsr io_setdeviceandfilename
        jsr open
        bcs ioofr_quit                  ; Probably "device not present".
; Set input file.
        ldx #FILENUMBER
        jsr chkin
ioofr_quit:
        rts

; ======================================
io_openforwritewithstatuslinenotrle:
; Open file for writing and display "saving" in the status line.
; File is always open for non-RLE write.
; ======================================
;  Input: io_filename
;         io_filenamelen
; Output: C: set if error.
; ======================================
        lda #$00

; ======================================
io_openforwritewithstatusline:
; Open file for writing and display "saving" in the status line.
; ======================================
;  Input: A: if non-zero, open for writing RLE packed file.
;         io_filename
;         io_filenamelen
; Output: C: set if error.
; ======================================
        sta io_rlefile
        ldx #<io_savingtext
        ldy #>io_savingtext
        jsr io_blockcounterinit
        ldy #1

; ======================================
io_openforwrite:
; Open file for writing.
; ======================================
;  Input: Y: secondary address (1 when saving, 15 for disk commands)
;         io_filename
;         io_filenamelen
; Output: C: set if error.
; ======================================
        jsr io_setdeviceandfilename
        jsr open
        bcs ioofw_quit                  ; Probably "device not present".
; Set output file.
        ldx #FILENUMBER
        jsr chkout
ioofw_quit:
        rts

; ======================================
io_devicenotpresent:
; Set drive status to "device not present"
; ======================================
        ldy #IO_DEVICENOTPRESENTTEXTLENGTH-1
iodnp_loop:
        lda io_devicenotpresenttext,y
        sta io_drivestatus,y
        dey
        bpl iodnp_loop
        rts

; ======================================
io_close:
; Close file opened with io_openforread or io_openforwrite.
; Then read drive status.
; ======================================
; Quite ugly jumping around to close file.
        jsr iogds_quit

; ======================================
io_getdrivestatus:
; Read drive status into io_drivestatus[].
; ======================================
; Default to "device not present" error.
        jsr io_devicenotpresent
        lda io_diskdevice
        jsr listen
        jsr unlsn
        lda status
        bmi iogds_quit
; Open status channel.
        lda #0
        sta io_filenamelen
        ldy #15
        jsr io_openforread
        bcs iogds_quit                  ; Probably "device not present".
        ldy #0
iogds_loop:
        lda status
        bne io_devicenotpresent
        jsr chrin
        cmp #13
        beq iogds_done
        and #$3f
        sta io_drivestatus,y
        iny
        bne iogds_loop
iogds_done:
        lda #$ff
        sta io_drivestatus,y
iogds_quit:
        lda #FILENUMBER
        jsr close
        jmp clrchn

; ======================================
io_getchar:
; Read byte from file, similar to C getchar().
; Updates block counter in the status line.
; ======================================
; Output: A: byte
;         C: 0 -> success, 1 -> error
;         $90: kernal status
; ======================================
        jsr io_blockcounterupdate
        jmp chrin

; ======================================
io_putchar:
; Write byte to file, similar to C putchar().
; Updates block counter in the status line.
; ======================================
;  Input: A: byte
; Output: C: 0 -> success, 1 -> error
;         $90: kernal status
; ======================================
        jsr io_blockcounterupdate
        jmp chrout

; ======================================
io_readxy:
; Read bytes from file, similar to C read().
; ======================================
;  Input: Y:X -> buffer
; Output: C: 0 -> success, 1 -> error
; ======================================
        stx io_pointer
        sty io_pointer+1

; ======================================
io_read:
; Read bytes from file, similar to C read().
; ======================================
;  Input: io_pointer: -> buffer
;         io_rlefile: if non-zero, read form RLE packed file.
; Output: C: 0 -> success, 1 -> error
; ======================================
        lda io_rlefile
        bne io_readrle
ior_loop:
        ldy status
        bne ior_done                    ; Probably end of file.
        jsr io_getchar
        jsr io_storebyte
        bne ior_loop
ior_done:
        rts

; ======================================
io_readrle:
; Read RLE packed file. Escape byte is $ff, then length, then byte.
; ======================================
;  Input: io_pointer: -> buffer
; Output: C: 0 -> success, 1 -> error
; ======================================
iorr_loop:
        ldy status
        bne iorr_done                   ; Probably end of file.
        jsr io_getchar
        cmp #RLE_ESCAPE_BYTE
        bne iorr_singlebyte
; RLE escape byte found.
        jsr io_getchar                  ; Read RLE length.
        cmp #$00
        beq iorr_done                   ; Length == 0 means end of file.
        sta iorr_rlelength+1
        jsr io_getchar                  ; Read the byte to repeat.
iorr_rlelength:
        ldx #$00                        ; Self modifying code.
iorr_rleloop:
        jsr io_storebyte
        dex
        bne iorr_rleloop
        beq iorr_loop
iorr_singlebyte:
        jsr io_storebyte
        bne iorr_loop
iorr_done:
        rts

; ======================================
io_storebyte:
;  Input: A: byte
;         io_pointer: -> buffer
; Output: Y: always 0, ZF always clear.
; ======================================
        ldy #0
        sta (io_pointer),y
        jmp $fcdb                       ; Increment $AC/$AD.

; ======================================
io_writexy:
; Write bytes to file, similar to C write().
; ======================================
;  Input: Y:X: -> buffer to save from.
;         io_saveend: -> first byte _not_ to save.
;         io_rlefile: if non-zero, write to RLE packed file.
; Output: C: 0 -> success, 1 -> error
; ======================================
        stx io_pointer
        sty io_pointer+1

; ======================================
io_write:
; Write bytes to file, similar to C write().
; ======================================
;  Input: io_pointer: -> buffer to save from.
;         io_saveend: -> first byte _not_ to save.
;         io_rlefile: if non-zero, write to RLE packed file.
; Output: C: 0 -> success, 1 -> error
; ======================================
        lda io_rlefile
        bne io_writerle
iow_loop:
        jsr $fcd1                       ; Compare $AC/$AD with $AE/$AF.
        beq iow_done
        ldy #0
        lda (io_pointer),y
        jsr io_putchar
        ldy status
        bne iow_done                    ; Probably disk full.
        jsr $fcdb                       ; Increment $AC/$AD.
        bne iow_loop                    ; Jump always.
iow_done:
        rts

; ======================================
io_writerle:
; Write RLE packed file. Escape byte is $ff, then length, then byte.
; ======================================
;  Input: io_pointer: -> buffer to save from.
;         io_saveend: -> first byte _not_ to save.
; Output: C: 0 -> success, 1 -> error
; ======================================
iowr_loop:
        jsr $fcd1                       ; Compare $AC/$AD with $AE/$AF.
        beq iowr_finish
; Get maximum run length.
; Limit maximum possible run length if end of file is near.
;   if (io_saveend-io_pointer <= $ff) max_length = io_saveend-io_pointer;
;   else max_length = $ff;
        sec
        lda io_saveend
        sbc io_pointer
        tay
        lda io_saveend+1
        sbc io_pointer+1
        bne iowr_getrlelengthmaxlength
        .byte $2c                       ; BIT $ffff
iowr_getrlelengthmaxlength:
        ldy #$ff
        sty iowr_getrlelengthend+1
; Now find actual run length.
        ldy #$00
        lda (io_pointer),y
iowr_getrlelengthloop:
        iny
        cmp (io_pointer),y
        bne iowr_getrlelengthbreak
iowr_getrlelengthend:
        cpy #$00                        ; Self modifying code.
        bne iowr_getrlelengthloop
; RLE length is in Y.
iowr_getrlelengthbreak:
; If the byte to save is the RLE escape byte, then always write RLE block.
        cmp #RLE_ESCAPE_BYTE
        beq iowr_rleblock
; Else write RLE block if it is at least 4 bytes long.
        cpy #4
        bcs iowr_rleblock
; ELse save single byte.
        jsr io_putchar
        ldy status
        bne iowr_done                   ; Probably disk full.
        jsr $fcdb                       ; Increment $AC/$AD.
        bne iowr_loop                   ; Jump always.
; Save RLE block. Character is in A, length is in Y.
iowr_rleblock:
        pha
        tya
        pha
; Advance io_pointer by Y bytes.
iowr_rleblockadvance:
        jsr $fcdb                       ; Increment $AC/$AD.
        dey
        bne iowr_rleblockadvance
; First write escape byte, then length, then byte.
        lda #RLE_ESCAPE_BYTE
        jsr io_putchar
        pla
        jsr io_putchar
        pla
        jsr io_putchar
        bcc iowr_loop
; Write an RLE block with length 0 to indicate end of file.
iowr_finish:
        lda #RLE_ESCAPE_BYTE
        jsr io_putchar
        lda #0
        jsr io_putchar
        lda #0
        jsr io_putchar
iowr_done:
        rts

; ======================================
io_load:
; Load a complete file. RLE files are not loaded.
; ======================================
;  Input: Y:X: -> buffer
;         io_filename
;         io_filenamelen
; ======================================
        stx io_pointer
        sty io_pointer+1
        jsr io_openforreadwithstatusline
        bcs iol_done                    ; Disk error.
        jsr io_getchar                  ; Skip low byte of load address.
        jsr io_getchar                  ; Skip high byte of load address.
        jsr io_read
iol_done:
        jsr io_close
        jmp io_getdrivestatus

; ======================================
io_save:
; Save a complete file.
; ======================================
;  Input: A: if non-zero, save RLE packed file.
;         Y:X: -> buffer to save from.
;         io_saveend: -> first byte _not_ to save.
;         io_filename
;         io_filenamelen
; ======================================
        stx io_pointer
        sty io_pointer+1
        pha
        jsr io_openforwritewithstatusline
        pla
        bcs ios_done                    ; Disk error.
        bne ios_rlefile
; Write load address for plain files.
        lda io_pointer
        jsr io_putchar
        lda io_pointer+1
        bne ios_startwrite              ; Jump always.
; Write $52, $4c for RLE files.
ios_rlefile:
        lda #$52
        jsr io_putchar
        lda #$4c
ios_startwrite:
        jsr io_putchar
; Write bytes, then send unlisten to write the last one!
        jsr io_write
        jsr unlsn
ios_done:
        jsr io_close
        jmp io_getdrivestatus

; ======================================
editor_initscreen:
; Draw static stuff in editor screen.
; Draws patterns and orders or instrument depending on editor_whichscreen.
; ======================================
; Clear everything on screen except for the panel.
        ldx #$00
eis_clearscreen:
        lda #$20
        sta $04f0,x
        sta $04f0+190,x
        sta $04f0+380,x
        sta $04f0+570,x
        lda color_pattern
        sta $d8f0,x
        sta $d8f0+190,x
        sta $d8f0+380,x
        sta $d8f0+570,x
        inx
        cpx #190
        bne eis_clearscreen

; Init colors to a known state.
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
; Move cursor directly below panel.
        ldx #0
        ldy #6
        jsr console_setcursorpos

; See what sort of screen we have to draw.
        ldx editor_whichscreen
        beq eis_pattern
        dex
        beq eis_pattern
        dex
        beq eis_instrument
        dex
        beq eis_configmenu
        dex
        beq eis_specmenu
        dex
        beq eis_diskmenu
        brk                      ; !!!! This is impossible

eis_pattern:
        ldx #<patterntext
        ldy #>patterntext
        jsr console_writepackedstringxy
        jmp editor_updatepatterncolors

eis_instrument:
        ldx #<instrumenttext
        ldy #>instrumenttext
eis_instrument0:
        jmp console_writepackedstringxy

eis_configmenu:
        ldx #<configmenutext
        ldy #>configmenutext
        bne eis_instrument0             ; Jump always.

eis_specmenu:
        ldx #<specmenutext
        ldy #>specmenutext
        bne eis_instrument0             ; Jump always.

eis_diskmenu:
        ldx #<diskmenutext
        ldy #>diskmenutext
        jsr console_writepackedstringxy
        jmp dm_displaydrivestatus

; ======================================
editor_updatepatterncolors:
; Update pattern colors to reflect channel mute status.
; ======================================
        lda editor_whichscreen          ; If not in order or pattern editor,
        cmp #EDITOR_INSTRUMENT_ID       ; don't set pattern muted/unmuted
        bcs eupc_done                   ; colors.
; Set color for channel 0.
        ldx #5
        ldy #8
        jsr console_setcursorpos
        lda color_pattern
        ldy chn_muted+0
        beq wtr_chn0active
        lda color_muted
wtr_chn0active:
        ldx #10
        ldy #17
        jsr console_fillcolorramblock
; Set color for channel 1.
        ldx #17
        ldy #8
        jsr console_setcursorpos
        lda color_pattern
        ldy chn_muted+1
        beq wtr_chn1active
        lda color_muted
wtr_chn1active:
        ldx #10
        ldy #17
        jsr console_fillcolorramblock
; Set color for channel 2.
        ldx #29
        ldy #8
        jsr console_setcursorpos
        lda color_pattern
        ldy chn_muted+2
        beq wtr_chn2active
        lda color_muted
wtr_chn2active:
        ldx #10
        ldy #17
        jmp console_fillcolorramblock
eupc_done:
        rts

; ======================================
editor_updatescreen:
; Update changing stuff in editor screen.
; Draws patterns and orders or instrument depending on editor_whichscreen.
; ======================================
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask

; Write current rastertime.
        lda editor_currentraster
        ldx #15
        ldy #3
        jsr console_writehexatxy
; Write max rastertime.
        jsr console_cursorright
        lda editor_maxraster
        jsr console_writehex

; Print editor step.
        lda editor_editstep
        ldx #18
        ldy #1
        jsr console_writehexatxy

; Print speed.
        lda speed
        ldx #18
        ldy #2
        jsr console_writehexatxy

; Draw timer.
        lda timer_minutes
        ldx #12
        ldy #4
        jsr console_writehexatxy
        jsr console_cursorright
        lda timer_seconds
        jsr console_writehex
        jsr console_cursorright
        lda timer_hundreds
        jsr console_writehex

; Display orderlist.
        lda #0
        sta display_x
        lda #0
        sta display_y
        lda #5
        sta display_height
        lda ordernumber
        sta display_index
        lda #2
        sta display_line
        lda #<ORDERLIST
        sta display_datasrc
        lda #>ORDERLIST
        sta display_datasrc+1
        lda #$00
        sta display_indexhighlight
        sta display_datahighlight
        jsr write_list

; Write instrument names.
        jsr write_instrumentnames

; See what sort of screen we have to draw.
        ldx editor_whichscreen
        beq eus_order
        dex
        beq eus_pattern
        lda #$01
        sta $d015                       ; Enable cursor only.
        dex
        beq eus_instrument
        dex
        beq eus_configmenu
        dex
        beq eus_specmenu
        dex
        beq eus_diskmenu
        brk                      ; !!!! This is impossible

eus_order:
        jsr write_pattern
; Set sprite cursor.
; X=3+editor_ordercol
        ldx editor_ordercol
        inx
        inx
        inx
        ldy #2
        jmp console_setspritecursor

eus_pattern:
        jsr write_pattern
; Set sprite cursor.
; X=5+editor_patternchannel*12+patterncursorpositions[editor_patternfield]
        lda editor_patternchannel
        asl
        adc editor_patternchannel
        asl
        asl
        adc #5
        ldy editor_patternfield
        adc editor_patternfieldxpositions,y
        tax
        ldy #16
        jmp console_setspritecursor

eus_instrument:
        jsr write_instrument
        ldx #41                         ; Move cursor out of screen.
        ldy #0
        lda editor_currentinst
        beq eus_instrument0
; Set cursor position into middle of table or into instrument parameters.
        ldy #16
        lda editor_instfield
        bne eusdi_intable
        lda #8
        clc
        adc editor_instrow
        tay
eusdi_intable:
        ldx editor_instfield
        lda editor_instfieldxpositions,x
        clc
        adc editor_instcol
        tax
eus_instrument0:
        jmp console_setspritecursor

eus_configmenu:
        jsr write_config
        ldx #24
        lda #8
        clc
        adc editor_configrow
        tay
        jmp console_setspritecursor

eus_specmenu:
; Display song title.
        jsr console_hidespritecursor
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        ldx #6
        ldy #6
        jsr console_setcursorpos
        lda #<SONGTITLE
        sta stringptr
        lda #>SONGTITLE
        sta stringptr+1
        ldx #SONGTITLELEN
        jmp console_writestringlen

eus_diskmenu:
        jsr console_hidespritecursor
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
; Quick hack to display a decimal-looking device number.
        ldx #0
        lda io_diskdevice
eusdm_devnumloop:
        cmp #10
        bmi eusdm_devnumdone
        sec
        sbc #10
        inx
        bne eusdm_devnumloop            ; Jumps always.
eusdm_devnumdone:
        sta eusdm_devnumtmp+1
        txa
        asl
        asl
        asl
        asl
eusdm_devnumtmp:
        ora #$00                        ; Self modifying code.
        ldx #18
        ldy #9
        jsr console_writehexatxy
        rts

; ======================================
editor_makeinstptr:
; editor_instptr=32*A+INSTRUMENTS
; ======================================
;  Input: A: instrument field number
; Output: editor_instptr, editor_instptr+1
; ======================================
        tay
        asl
        asl
        asl
        asl
        asl
        clc
        adc #<INSTRUMENTS
        php
        sta editor_instptr
        tya
        lsr
        lsr
        lsr
        plp
        adc #>INSTRUMENTS
        sta editor_instptr+1
        rts

; ======================================
editor_makeinstnameptr:
; stringptr=16*stringptr+INSTRUMENTNAMES
; ======================================
;  Input: A: instrument number
; Output: stringptr, stringptr+1
; ======================================
        sec
        sbc #$01
        ldy #$00
        asl
        asl
        asl
        asl
        bcc eminp_noof
        iny
eminp_noof:
        clc
        adc #<INSTRUMENTNAMES
        sta stringptr
        tya
        adc #>INSTRUMENTNAMES
        sta stringptr+1
        rts

; ======================================
editor_init:
; Initialize editor. Set up screen, colors, sprites, etc.
; ======================================
; Call routines that RESET does to init stuff.
        jsr $ff84                       ; initalise I/O devices
        jsr $ff8a                       ; restore I/O vectors
        jsr $ff81                       ; initalise screen and keyboard

        lda #$36
        sta $01                         ; Hide BASIC ROM.
        lda #$80
        sta $028a                       ; Enable keyrepeat.
        lda #$00                        ; Hide kernal messages.
        jsr setmsg

; Init editor state.
        lda $ba                         ; Device number in kernal zeropage.
        cmp #8                          ; Figure out the drive the program
        bmi ei_fixdevice1               ; was loaded from.
        cmp #12
        bmi ei_fixdevice2
ei_fixdevice1:
        lda #8
ei_fixdevice2:
        sta io_diskdevice
        lda #$ff
        sta io_drivestatus
        lda #EDITOR_PATTERN_ID
        sta editor_whichscreen
        lda #$00
        sta editor_playmode             ; Stop playing.
        sta editor_ordercol             ; Cursor on high nybble in orderlist.
        sta editor_patternchannel       ; Go to channel 1
        sta editor_patternfield         ; Go to note field.
        sta editor_instfield            ; Cursor on instrument parameters.
        sta editor_instrow              ; Cursor on first row in inst editor.
        sta editor_instcol              ; Cursor on high nybble.
        sta editor_waveindex
        sta editor_arpindex
        sta editor_filterindex
        sta editor_configrow            ; Cursor on first row in config menu.
        sta editor_trackeffectbuf       ; Clear effect copy buffer.
        sta editor_trackeffectparbuf    ; Clear effect parameter copy buffer.
        sta editor_trackblockflags      ; No track block.
        sta editor_filterblockflags     ; No filter table block.
        ldy #1
        sty editor_currentinst          ; Set current instrument.
        sty editor_editstep             ; Initialize edit step to 1.
        ldy #3
        sty editor_currentoctave        ; Default to octave 3.
        ldy #3*12
        sty editor_currentoctavenote    ; Default to octave 3.
; Invalidate undo buffer.
        ldy #$80
        sty editor_trackundochannel
; Clear track copy buffer.
        sta editor_trackcopybufferpos
        sta editor_trackcopybufferlen
; Clear instrument copy buffer.
        sta editor_instcopybuffervalid

; Load default color set 1.
        jsr cm_colorset1

; Init interrupts.
        jsr initirq
        jsr eg_zerorastertimes          ; Clear rastertime counters.
        jsr player_init

editor_reinit:
        lda #$80
        sta $0291                       ; Disable case-switching.
        lda #$5b
        sta $d011                       ; Enable ECM.

; Init colors.
        lda color_d021
        sta $d020
        sta $d021
        lda color_d022
        sta $d022
        lda color_d023
        sta $d023
        lda color_d024
        sta $d024

; Create static things in the panel.
        lda color_static
        ldx #$00
        jsr console_setcolorandmask
        ldx #0
        ldy #0
        jsr console_setcursorpos
        ldx #<paneltext
        ldy #>paneltext
        jsr console_writepackedstringxy

; Init static stuff on screen.
        jsr editor_initscreen

; Init sprites.
; Init track row highlight sprites.
        lda #$18                        ; Start of window in sprite coords.
        ldx #1
        ldy #2
ei_spritepointers:
        sta $d000,y                     ; Set sprite X position.
        clc
        adc #48
        pha
        lda #SPRITEHILIGHT/64
        sta $07f8,x                     ; Set sprite pointer.
        lda color_currentrow
        sta $d027,x                     ; Set sprite color.
        lda #$b2
        sta $d001,y                     ; Set sprite Y position.
        pla
        iny
        iny
        inx
        cpx #8
        bne ei_spritepointers
        lda #SPRITEXMSB
        sta $d010
; Init cursor sprite.
        lda #SPRITECURSOR/64
        sta $07f8                       ; Set sprite pointer.
        lda color_cursor
        sta $d027                       ; Sprite color.
        ldx #$fe
        stx $d01b                       ; Sprite to background priority.
        inx
        stx $d01d                       ; Double horizontal all sprites.

; Init font.
        lda #$10+FONT/1024
        sta $d018
        rts

; ======================================
editor_gettracks:
; Get track numbers and transposes into
; editor_tracks[], editor_tracktransposes[].
; ======================================
;  Input: ordernumber, orderlist[], patterns[]
; Output: editor_tracks+0, editor_tracks+1, editor_tracks+2
;         editor_tracktransposes+0, editor_tracktransposes+1, editor_tracktransposes+2
; ======================================
; Get pointer to pattern.
        ldy ordernumber
        lda ORDERLIST,y                 ; Get current pattern.
        jsr editor_makepatternpointer
        ldx #0
        ldy #0
egt_loop:
        lda (editor_patternptr),y
        sta editor_tracks,x
        iny
        lda (editor_patternptr),y
        sta editor_tracktransposes,x
        iny
        inx
        cpx #3
        bne egt_loop
        rts

; ======================================
editor_puttracks:
; Put track numbers and transposes from
; editor_tracks[], editor_tracktransposes[] to pattern.
; ======================================
;  Input: ordernumber, editor_tracks[], editor_tracktransposes[], orderlist[]
; Output: patterns[]
; ======================================
; Get pointer to pattern.
        ldy ordernumber
        lda ORDERLIST,y                 ; Get current pattern.
        jsr editor_makepatternpointer
        ldx #0
        ldy #0
ept_loop:
        lda editor_tracks,x
        sta (editor_patternptr),y
        iny
        lda editor_tracktransposes,x
        sta (editor_patternptr),y
        iny
        inx
        cpx #3
        bne ept_loop
        rts

; ======================================
editor_makepatternpointer:
; Calculate 6*A+PATTERNS.
; ======================================
;  Input: A: pattern number
; Output: patternptr: -> pattern
; ======================================
        sta emtp_noof1+1
        ldx #0
        asl
        bcc emtp_noof1
        inx
        clc
emtp_noof1:
        adc #$00                        ; Self modifying code.
        bcc emtp_noof2
        inx
emtp_noof2:
        stx editor_patternptr+1
        asl
        rol editor_patternptr+1
        adc #<PATTERNS
        sta editor_patternptr
        lda editor_patternptr+1
        adc #>PATTERNS
        sta editor_patternptr+1
        rts

; ======================================
editor_maketrackpointer:
; Calculate 192*track_number+tracks_base
; ======================================
;  Input: A: track number
; Output: editor_trackptr: -> track
; ======================================
        sta editor_maketrackpointer0+1
        asl
editor_maketrackpointer0:
        adc #$00                        ; Self modifying code.
        sta editor_trackptr+1
        lda #$00
        ror editor_trackptr+1
        ror
        lsr editor_trackptr+1
        ror
        adc #<TRACKS_BASE
        sta editor_trackptr
        lda editor_trackptr+1
        adc #>TRACKS_BASE
        sta editor_trackptr+1
        rts

; ======================================
editor_gettrackrow:
; Read note, instrument, effect and parameter from track visible in editor.
; ======================================
;  Input: editor_tracks+0, editor_tracks+1, editor_tracks+2
;         editor_getputtrackrow: row number to read from
; Output: editor_tracknote
;         editor_trackinst
;         editor_trackeffect
;         editor_trackeffectpar
; ======================================
        ldx editor_patternchannel

; Get from track visible in channel X in editor.
editor_gettrackrowanychannel:
        lda editor_tracks,x
        jsr editor_maketrackpointer

; Entry point to read any track.
editor_gettrackrowany:
        lda editor_getputtrackrow
        asl
        adc editor_getputtrackrow
        tay
; Read note.
        lda (editor_trackptr),y
        and #$7f
        sta editor_tracknote
; Read effect and instrument.
        lda (editor_trackptr),y
        lsr
        lsr
        lsr
        lsr
        and #$08
        sta editor_trackeffect
        iny
        lda (editor_trackptr),y
        and #$1f
        sta editor_trackinst
        lda (editor_trackptr),y
        lsr
        lsr
        lsr
        lsr
        lsr
        ora editor_trackeffect
        sta editor_trackeffect
; Read effect parameter.
        iny
        lda (editor_trackptr),y
        sta editor_trackeffectpar
        rts

; ======================================
editor_puttrackrow:
; Write note, instrument, effect and parameter to track visible in editor.
; ======================================
;  Input: editor_tracks+0, editor_tracks+1, editor_tracks+2
;         editor_getputtrackrow: row number to read from
;         editor_tracknote
;         editor_trackinst
;         editor_trackeffect
;         editor_trackeffectpar
; ======================================
        ldx editor_patternchannel

; Put to track visible in channel X in editor.
editor_puttrackrowanychannel:
        lda editor_tracks,x
        jsr editor_maketrackpointer

; Entry point to write any track.
editor_puttrackrowany:
        lda editor_getputtrackrow
        asl
        adc editor_getputtrackrow
        tay
; Put note and bit 3 of effect.
        lda editor_trackeffect
        and #$08
        asl
        asl
        asl
        asl
        ora editor_tracknote
        sta (editor_trackptr),y
; Put bit 0-2 of effect and instrument.
        lda editor_trackeffect
        asl
        asl
        asl
        asl
        asl
        ora editor_trackinst
        iny
        sta (editor_trackptr),y
; Put effect parameter.
        lda editor_trackeffectpar
        iny
        sta (editor_trackptr),y
        rts

; ======================================
write_instrumentnames:
; Display instrument name list
; ======================================
        lda #0
        sta display_y
        lda #5
        sta display_height
        lda editor_currentinst
        sec
        sbc #2
        sta display_index
        lda #0
        sbc #0
        sta display_index+1

win_next:
; Move cursor to current line.
        lda color_static
        ldy display_y
        cpy #2
        bne win_nohighligth
        lda color_highlight
win_nohighligth:
        jsr console_setcolor
        ldx #21
        jsr console_setcursorpos
; Display empty line if display_index<0 or display_index>=$20
        lda display_index+1
        bne win_emptyline
        lda display_index
        cmp #MAX_INSTRUMENTS
        bpl win_emptyline
; Display valid line in instrument names list.
        lda #DISPLAY_INDEXCOLORMASK
        jsr console_setcolormask
        lda display_index
        jsr console_writehex
        lda #":"
        jsr console_writechar
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        lda display_index
        beq win_instrument0
        jsr editor_makeinstnameptr
        ldx #INSTRUMENTNAMELEN
        jsr console_writestringlen
        jmp win_cont
win_instrument0:
        ldx #<instrument0name
        ldy #>instrument0name
        jsr console_writestringxy
        jmp win_cont
; Disply empty line in instrument name list.
win_emptyline:
        lda #DISPLAY_INDEXCOLORMASK
        jsr console_setcolormask
        ldy #3
        jsr console_writespaces
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        ldy #INSTRUMENTNAMELEN
        jsr console_writespaces
win_cont:
        inc display_index
        bne win_nohi
        inc display_index+1
win_nohi:
        inc display_y
        dec display_height
        bne win_next
        rts

; ======================================
write_instrument:
; Display instrument parameters.
; ======================================
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask
        lda editor_currentinst
        bne wi_validinstrument

; When displaying instrument 0 clear everything and
; write default instrument name.
        ldx #5
        ldy #6
        jsr console_setcursorpos
        ldx #<instrument0name
        ldy #>instrument0name
        jsr console_writestringxy
; Clear instrument parameters.
        ldx #19
        ldy #8
        jsr console_setcursorpos
        lda #$20
        ldx #2
        ldy #16
        jsr console_fillblock
; Clear wave table display.
        ldx #22
        ldy #8
        jsr console_setcursorpos
        lda #$20
        ldx #5
        ldy #17
        jsr console_fillblock
; Clear arpeggio table display.
        ldx #28
        ldy #8
        jsr console_setcursorpos
        lda #$20
        ldx #5
        ldy #17
        jsr console_fillblock
; Clear filter table display.
        ldx #34
        ldy #8
        jsr console_setcursorpos
        lda #$20
        ldx #5
        ldy #17
        jmp console_fillblock

; Write a valid (non-zero) instrument's data.
wi_validinstrument:
; Write instrument name.
        lda editor_currentinst
        jsr editor_makeinstnameptr
        ldx #5
        ldy #6
        jsr console_setcursorpos
        ldx #INSTRUMENTNAMELEN
        jsr console_writestringlen

; Write normal instrument parameters.
        lda #0
        sta display_index
        lda #8
        sta display_y
        lda #<INSTRUMENTS
        sta editor_instptr
        lda #>INSTRUMENTS
        sta editor_instptr+1
wi_loop:
        ldy editor_currentinst
        lda (editor_instptr),y
        ldx #19
        ldy display_y
        jsr console_writehexatxy
        lda editor_instptr
        clc
        adc #MAX_INSTRUMENTS
        sta editor_instptr
        lda editor_instptr+1
        adc #0
        sta editor_instptr+1
        inc display_index
        inc display_y
        lda display_index
        cmp #16
        bne wi_loop

; Display wave table.
        lda #22
        sta display_x
        lda #8
        sta display_y
        lda #17
        sta display_height
        lda editor_waveindex
        sta display_index
        lda #8
        sta display_line
        lda #<WAVETABLE
        sta display_datasrc
        lda #>WAVETABLE
        sta display_datasrc+1
        lda #$80
        sta display_indexhighlight
        ldy editor_currentinst
        lda INSTRUMENTS_WAVETABLESTART,y
        sta display_indexhighlightfirst
        lda INSTRUMENTS_WAVETABLEEND,y
        sta display_indexhighlightlast
        lda #$00
        sta display_datahighlight
        jsr write_list
; Display arpeggio table.
        lda #28
        sta display_x
        lda #8
        sta display_y
        lda #17
        sta display_height
        lda editor_arpindex
        sta display_index
        lda #8
        sta display_line
        lda #<ARPEGGIOTABLE
        sta display_datasrc
        lda #>ARPEGGIOTABLE
        sta display_datasrc+1
        ldy editor_currentinst
        lda INSTRUMENTS_ARPTABLESTART,y
        sta display_indexhighlightfirst
        lda INSTRUMENTS_ARPTABLEEND,y
        sta display_indexhighlightlast
        jsr write_list
; Display filter table.
        lda #34
        sta display_x
        lda #8
        sta display_y
        lda #17
        sta display_height
        lda editor_filterindex
        sta display_index
        lda #8
        sta display_line
        lda #<FILTERTABLE
        sta display_datasrc
        lda #>FILTERTABLE
        sta display_datasrc+1
        ldy editor_currentinst
        lda INSTRUMENTS_FILTERTABLESTART,y
        sta display_indexhighlightfirst
        lda INSTRUMENTS_FILTERTABLEEND,y
        sta display_indexhighlightlast
        ldy #$00
        lda editor_filterblockflags
        cmp #BLOCK_BEGINSET+BLOCK_ENDSET
        bne wi_nofilterblock            ; Begin or end unset -> nothing to do.
        lda editor_filterblockbeg
        sta display_datahighlightfirst
        lda editor_filterblockend
        sta display_datahighlightlast
        ldy #$80
wi_nofilterblock:
        sty display_datahighlight
        jmp write_list

; ======================================
write_pattern:
; ======================================
        lda #$ff
        sta $d015                       ; Enable all sprites.
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask

; Write current octave.
        lda editor_currentoctave
        clc
        adc #$30
        ldx #3
        ldy #6
        jsr console_writecharatxy

; Write track headers.
        jsr editor_gettracks
; Write track number for channel 1.
        lda editor_tracks+0
        ldx #8
        ldy #6
        jsr console_writehexatxy
; Write track transpose for channel 1.
        lda editor_tracktransposes+0    ; Convert transpose from 2's
        bpl wp_transposeup1             ; complement to sign bit binary.
        eor #$7f
        clc
        adc #$01
wp_transposeup1:
        ldx #13
        ldy #6
        jsr console_writehexatxy
; Write track number for channel 2.
        lda editor_tracks+1
        ldx #20
        ldy #6
        jsr console_writehexatxy
; Write track transpose for channel 2.
        lda editor_tracktransposes+1    ; Convert transpose from 2's
        bpl wp_transposeup2             ; complement to sign bit binary.
        eor #$7f
        clc
        adc #$01
wp_transposeup2:
        ldx #25
        ldy #6
        jsr console_writehexatxy
; Write track number for channel 3.
        lda editor_tracks+2
        ldx #32
        ldy #6
        jsr console_writehexatxy
; Write track transpose for channel 3.
        lda editor_tracktransposes+2    ; Convert transpose from 2's
        bpl wp_transposeup3             ; complement to sign bit binary.
        eor #$7f
        clc
        adc #$01
wp_transposeup3:
        ldx #37
        ldy #6
        jsr console_writehexatxy

; Write row numbers and 3 tracks for the pattern.
        ldx #1
        ldy #8
        stx display_x
        sty display_y
        lda trackrow
        sec
        sbc #8
        sta display_row

; Repeat this for each row on screen.
wp_nextrow:
; Write row numbers on the left.
        ldx display_x
        ldy display_y
        jsr console_setcursorpos
        lda display_row
        cmp #64
        bcc wp_validline
        lda #$00
        jsr console_setcolormask
        ldy #38
        jsr consolenc_writespaces
        jmp wp_cont
; Write non-empty line.
wp_validline:
; First write row number.
        lda #$00
        jsr console_setcolormask
        lda display_row
        jsr consolenc_writehex
; Create index into track.
        lda display_row
        asl
        adc display_row
        sta display_row3
        lda #0
        sta display_chn
; Repeat this for each track.
wp_nexttrack:
        jsr write_trackrow
        inc display_chn
        lda display_chn
        cmp #3
        bne wp_nexttrack
wp_cont:
        inc display_row
        inc display_y
        lda display_y
        cmp #25
        bmi wp_nextrow
        rts

; ======================================
write_trackrow:
; Write 1 row of a track.
; ======================================
;  Input: display_chn: channel number
;         display_x: screen x position
;         display_y: screen y position
;         display_row3: track row counter*3
;         editor_tracks[]
;         ... and more ...
; ======================================
        jsr consolenc_cursorright
        jsr consolenc_cursorright
        ldx display_chn
        lda editor_tracks,x
        jsr editor_maketrackpointer
; Find out if we are in a block. If so, highlight it.
        lda #$00
        ldy display_chn
        cpy editor_blockchannel
        bne wtr_colorok                 ; Block is in an other channel.
        ldy editor_trackblockflags
        cpy #BLOCK_BEGINSET+BLOCK_ENDSET
        bne wtr_colorok                 ; Begin or end unset -> no block.
        ldy editor_trackblockbeg
        cpy display_row
        beq wtr_colorok1
        bpl wtr_colorok
        ldy editor_trackblockend
        cpy display_row
        bmi wtr_colorok
wtr_colorok1:
        lda #DISPLAY_SELCOLORMASK
wtr_colorok:
        jsr console_setcolormask
        ldy display_row3
; Write note.
        lda (editor_trackptr),y
        and #$7f
        beq wtr_nonote                  ; No note -> write dots.
        cmp #97
        beq wtr_noteoff                 ; Note off -> write ===
        tay
        dey
        lda notestrings,y
        lsr
        lsr
        lsr
        lsr
        and #$07
        jsr consolenc_writechar
        ldx #$2d                        ; - minus
        lda notestrings,y
        bpl wtr_notsharp
        ldx #$23                        ; # hashmark
wtr_notsharp:
        txa
        jsr consolenc_writechar
        lda notestrings,y               ; Now write octave.
        and #$07
        clc
        adc #$30
        jsr consolenc_writechar
        jmp wtr_notewritten
wtr_noteoff:
        lda #$3d                        ; = equals
        .byte $2c                       ; BIT $ffff
wtr_nonote:
        lda #$2e                        ; . dot
wtr_noteoff_nonote:
        ldy #3
        jsr consolenc_writechars
wtr_notewritten:
        jsr consolenc_writespace
; Write instrument.
        ldy display_row3
        iny
        lda (editor_trackptr),y
        and #$1f
        bne wtr_validinst
        lda #$2e
        ldy #2
        jsr consolenc_writechars
        jmp wtr_instdone
wtr_validinst:
        jsr consolenc_writehex
wtr_instdone:
        jsr consolenc_writespace
; Write effect.
        ldy display_row3
        lda (editor_trackptr),y
        lsr
        lsr
        lsr
        lsr
        and #$08
        sta wtr_eff+1
        iny
        lda (editor_trackptr),y
        lsr
        lsr
        lsr
        lsr
        lsr
wtr_eff:
        ora #$00
        tay
        lda hexdigitsscreen,y
        jsr consolenc_writechar
; Write effect parameter.
        ldy display_row3
        iny
        iny
        lda (editor_trackptr),y
        jmp consolenc_writehex

; ======================================
write_config:
; Display config parameters.
; ======================================
        lda color_static
        ldx #DISPLAY_DATACOLORMASK
        jsr console_setcolorandmask

        lda #0
        sta display_index
        lda #8
        sta display_y
wc_loop:
        ldy display_index
        lda editor_configcolors,y
        ldx #23
        ldy display_y
        jsr console_writehexatxy
        inc display_index
        inc display_y
        lda display_index
        cmp #EDITOR_COLORSNUM
        bne wc_loop
        rts

; ======================================
write_list:
; Display orderlist, wave or arpeggio table.
; ======================================
;  Input: display_x: screen X position
;         display_y: screen Y position
;         display_height: number of lines to display
;         display_index: index of selected element
;         display_line: line where selected element appears
;         display_datasrc: 16 bit ptr to data
;         display_indexhighlight:
;         display_indexhighlightfirst:
;         display_indexhighlightlast:
;         display_datahighlight:
;         display_datahighlightfirst:
;         display_datahighlightlast:
; ======================================
        lda display_index
        sec
        sbc display_line
        sta display_index
        lda #0
        sbc #0
        sta display_index+1
; Calculate highlighted line Y position in screen coordinates.
        lda display_y
        clc
        adc display_line
        sta display_highlightline

wl_next:
; Set color to indicate highlight if necessary.
        lda color_static
        ldy display_y
        cpy display_highlightline
        bne wl_nohighligth
        lda color_highlight
wl_nohighligth:
        jsr console_setcolor
        ldx display_x
        jsr console_setcursorpos
; Move cursor to current line.
        ldx display_x
        ldy display_y
        jsr console_setcursorpos
; Display empty line if display_index<0 or display_index>=$100
        lda display_index+1
        bne wl_emptyline
; Display valid line in orderlist.
; Highlight index if required.
        lda #DISPLAY_INDEXCOLORMASK
        ldy display_index
        ldx display_indexhighlight
        beq wl_indexhighlightok
        cpy display_indexhighlightfirst
        bcc wl_indexhighlightok
        cpy display_indexhighlightlast
        beq wl_indexhighlight1
        bcs wl_indexhighlightok
wl_indexhighlight1:
        lda #DISPLAY_SELCOLORMASK
wl_indexhighlightok:
        jsr console_setcolormask
; And write index.
        tya
        jsr console_writehex
        lda #":"
        jsr console_writechar
; Highlight data if required.
        lda #DISPLAY_DATACOLORMASK
        ldy display_index
        ldx display_datahighlight
        beq wl_datahighlightok
        cpy display_datahighlightfirst
        bcc wl_datahighlightok
        cpy display_datahighlightlast
        beq wl_datahighlight1
        bcs wl_datahighlightok
wl_datahighlight1:
        lda #DISPLAY_SELCOLORMASK
wl_datahighlightok:
        jsr console_setcolormask
; And write data.
        lda (display_datasrc),y
        jsr console_writehex
        jmp wl_cont
; Disply empty line in list.
wl_emptyline:
        lda #DISPLAY_INDEXCOLORMASK
        jsr console_setcolormask
        ldy #3
        jsr console_writespaces
        lda #DISPLAY_DATACOLORMASK
        jsr console_setcolormask
        ldy #2
        jsr console_writespaces
wl_cont:
        inc display_index
        bne wl_nohi
        inc display_index+1
wl_nohi:
        inc display_y
        dec display_height
        beq wl_done
        jmp wl_next
wl_done:
        rts

; ======================================
initirq:
; Init IRQs.
; ======================================
        sei
        lda #$7f
        sta $dc0d
        lda #$81
        sta $d01a
        lda #$5b
        sta $d011
        lda #$32
        ldx #<irqhandler1
        ldy #>irqhandler1
        jsr setirq
        lda $dc0d
        cli
        rts

irqhandler1:
        lda $d019
        sta $d019
        ldx editor_playmode
        beq ih1_noplay
        dex
        bne ih1_keyjazz
        dec $d020
        jsr player_play
        inc $d020
        jsr timer_update                ; Update timer once a frame.
        jmp ih1_noplay
ih1_keyjazz:
        dec $d020
        lda editor_currentkeyjazznote
        ldy editor_currentinst
        jsr player_istrument_play
        inc $d020
ih1_noplay:
        lda $d012
        sec
        sbc #$32
        sta editor_currentraster
        cmp editor_maxraster
        bcc ih1_notmax
        sta editor_maxraster
ih1_notmax:
        jsr scnkey                      ; Scan keyboard once a frame.
        jmp $ea81

; ======================================
timer_update:
; Update the system timer. Call in every frame.
; ======================================
;  Input: timer_hundreds: 1/100th seconds, 0.02s precision
;         timer_seconds:  seconds
;         timer_minutes:  minutes
; Output: timer_hundreds: 1/100th seconds, 0.02s precision
;         timer_seconds:  seconds
;         timer_minutes:  minutes
; ======================================
        sed
        lda timer_hundreds
        clc
        adc #2
        sta timer_hundreds
        lda timer_seconds
        adc #0
        cmp #$60
        bcc tu_nominitupdate
        lda #0
        sta timer_seconds
        lda timer_minutes
        clc
        adc #1
        sta timer_minutes
        cld
        rts
tu_nominitupdate:
        sta timer_seconds
        cld
        rts

; ======================================
setirq:
; Set IRQ handler and rasterline.
; ======================================
;  Input: A: rasterline
;         X: handler low
;         Y: handler high
; ======================================
        sta $d012
        stx $0314
        sty $0315
        rts

; ======================================
write_help:
; Help reader.
; ======================================
;  Input: A: number of page to start at.
; ======================================
        tax
        jmp wh_displaypage
wh_loop:
        jsr console_waitkey
        cmp #KEY_DOWN
        beq wh_nextpage
        cmp #KEY_UP
        beq wh_prevpage
        cmp #KEY_LEFT
        beq wh_prevpage
        cmp #KEY_RIGHT
        beq wh_nextpage
; Exit help reader.
        rts

; Go to next page.
wh_nextpage:
        ldx editor_currenthelppage
        inx
        cpx #EDITOR_HELPPAGESNUM
        bcc wh_displaypage
        bcs wh_cont

; Go to previous page.
wh_prevpage:
        ldx editor_currenthelppage
        dex
        bpl wh_displaypage
        bmi wh_cont

; Write page in X.
wh_displaypage:
        stx editor_currenthelppage
        lda #155                        ; Light grey characters.
        jsr chrout
        lda #147                        ; Clear screen.
        jsr chrout
        lda editor_currenthelppage
        jsr write_helppage

wh_cont:
        jmp wh_loop

; ======================================
write_helppage:
; Display help page number A.
; Page end is marked with $00.
; ======================================
;  Input: A: help page number
; ======================================
        asl
        tax
        lda helppagepointers,x
        sta whp_getchar+1
        lda helppagepointers+1,x
        sta whp_getchar+2
whp_loop:
; It could be possible to miss an IRQ during this SEI/CLI section
; and thus miss a tick in the player.
; This shouldn't cause much trouble, though.
        ldx #$34
        ldy #$36
        sei
        stx $01                         ; Access RAM in $D000-$FFFF
whp_getchar:
        lda $ffff                       ; Self modifying code.
        sty $01                         ; Back to Kernal ROM.
        cli
        beq whp_done
        jsr chrout
        inc whp_getchar+1
        bne whp_loop
        inc whp_getchar+2
        bne whp_loop
whp_done:
        rts

; ======================================
packer_findused:
; Collect the instruments used in tracks,
; find lengths of orderlist, song start positions list,
; wave, arpeggio and wave table.
; ======================================
; Find first $ff element in orderlist. Its index is the length of orderlist-1.
        ldx #0
pfu_findorderend:
        lda ORDERLIST,x
        cmp #$ff
        beq pfu_orderend
        inx
        bne pfu_findorderend
        dex                             ; Shit happened, no $ff in orderlist.
pfu_orderend:
        stx packer_orderlistlength

; Find first $ff element in song start list. This is the number of songs-1.
        ldx #0
pfu_findsongstartlistend:
        lda SONGSTARTTABLE,x
        cmp #$ff
        beq pfu_songstartlistend
        inx
        bne pfu_findsongstartlistend
        dex                             ; Shit happened, no $ff in list.
pfu_songstartlistend:
        stx packer_songstartlistlength

; Find the largest instruments number used in the tracks.
        ldx #0
        stx packer_usedtracksnum
        stx packer_lastusedinstrument
        stx packer_currentorder
; For each orderlist position get the tracks for that pattern.
; Check the instruments for each of the 3 tracks.
pfu_orderloop:
        ldy packer_currentorder
        lda ORDERLIST,y
        jsr editor_makepatternpointer
        ldy #0
        lda (editor_patternptr),y
        jsr packer_addtracksinstruments
        ldy #2
        lda (editor_patternptr),y
        jsr packer_addtracksinstruments
        ldy #4
        lda (editor_patternptr),y
        jsr packer_addtracksinstruments
; Advance to next order.
        inc packer_currentorder
        lda packer_currentorder
        cmp packer_orderlistlength
        bne pfu_orderloop

; Find last element in wave table that is used by an instrument.
        ldx #<INSTRUMENTS_WAVETABLEEND
        ldy #>INSTRUMENTS_WAVETABLEEND
        jsr packer_findlargesttableindex
        sta packer_wavetablelength

; Find last element in arpeggio table that is used by an instrument.
        ldx #<INSTRUMENTS_ARPTABLEEND
        ldy #>INSTRUMENTS_ARPTABLEEND
        jsr packer_findlargesttableindex
        sta packer_arptablelength

; Find last element in filter table that is used by an instrument.
        ldx #<INSTRUMENTS_FILTERTABLEEND
        ldy #>INSTRUMENTS_FILTERTABLEEND
        jsr packer_findlargesttableindex
        sta packer_filtertablelength
        rts

; ======================================
packer_findlargesttableindex:
; Find largest index in a table used in instruments.
; ======================================
;  Input: Y:X: parameter pointer (INSTRUMENT_AD, INSTRUMENT_SR, etc.)
;         packer_lastusedinstrument: last instrument used in saved tracks.
; Output: A: last index encountered in instruments.
; ======================================
        stx stringptr
        sty stringptr+1
        ldy packer_lastusedinstrument
        lda #$00
pfle_loop:
        cmp (stringptr),y
        bcs pfle_cont
        lda (stringptr),y
pfle_cont:
        dey
        bne pfle_loop
        rts

; ======================================
packer_addtracksinstruments:
; Find the largest instrument number in a track.
; ======================================
;  Input: A: track number
;         packer_lastusedinstrument: previous largest
; Output: packer_lastusedinstrument
; ======================================
; Check if we have already processed this track.
        ldx #0
pati_seenexttrack:
        cpx packer_usedtracksnum
        beq pati_newtrack
        cmp packer_usedtracks,x
        beq pati_done                   ; We've already seen this track.
        inx
        bne pati_seenexttrack
; It is new track, add it to the list of used tracks and
; add every intrument in it to the list of used instruments.
pati_newtrack:
        sta packer_usedtracks,x
        inx
        stx packer_usedtracksnum
        jsr editor_maketrackpointer
; Do for rows 0..63 in each track.
        lda #0
        sta editor_getputtrackrow
pati_rowloop:
        lda editor_getputtrackrow
        cmp #64
        beq pati_done
        jsr editor_gettrackrowany
        lda editor_trackinst
        cmp packer_lastusedinstrument
        bcc pati_cont
        sta packer_lastusedinstrument
pati_cont:
        inc editor_getputtrackrow
        bne pati_rowloop
pati_done:
        rts

; ======================================
packer_setrelocdestinations:
; Calculate pointers for each table so that they follow each other immediately.
; ======================================
;  Input: A: destination page where player will sit.
; ======================================
        sta packer_playerdestpage
        clc
        adc #>VPLAYERSIZE
        sta stringptr+1
        lda #<VPLAYERSIZE
        sta stringptr

        ldx #0
; Set song start table pointer.
        clc
        lda packer_songstartlistlength
        jsr packer_setrelocdestination
; Decompile orderlist into track pointers and transpose values.
        ldy #9                  ; 3 bytes per pattern for each channel.
psrd_orderlistloop:
        clc
        lda packer_orderlistlength
        jsr packer_setrelocdestination
        dey
        bne psrd_orderlistloop
; Set instrument parameter pointers. (AD, SR, wave start, ... filter loop)
        ldy #INSTRUMENTLEN
psrd_instrumentloop:
        sec
        lda packer_lastusedinstrument   ; Set instrument AD pointer.
        jsr packer_setrelocdestination
        dey
        bne psrd_instrumentloop
; Set wave table pointer. Add carry, since this elements has to be saved.
        sec
        lda packer_wavetablelength
        jsr packer_setrelocdestination
; Set arp table pointer. Add carry, since this elements has to be saved.
        sec
        lda packer_arptablelength
        jsr packer_setrelocdestination
; Set filter table pointer. Add carry, since this elements has to be saved.
        sec
        lda packer_filtertablelength
        jsr packer_setrelocdestination

; Tracks can follow immediately.
        lda stringptr
        sta packer_tracksbase
        lda stringptr+1
        sta packer_tracksbase+1
        rts

; ======================================
packer_setrelocdestination:
; ======================================
;  Input: A+C: size of table.
;         X: index into packer_relocdestinations
;         stringptr+1:stringptr: current pointer.
; ======================================
        sta psrd_tablesize+1
        inx                             ; Skip the original address.
        inx
        lda stringptr
        sta packer_relocdestinations,x
psrd_tablesize:
        adc #$00                        ; Self modifying code.
        sta stringptr
        inx
        lda stringptr+1
        sta packer_relocdestinations,x
        adc #0
        sta stringptr+1
        inx
        rts

; ======================================
packer_relocplayerpiece:
; Relocate and save a portion of player code.
; ======================================
;  Input: stringptr: pointer to first player code byte to relocate
;         display_datasrc: pointer to last player code byte to relocate + 1
; ======================================
; Relocate player code and table pointers in player.
prp_loop:
        lda stringptr+1
        cmp #>VPLAYER_CODE_END
        bcc prp_playercode
        lda stringptr
        cmp #<VPLAYER_CODE_END
        bcc prp_playercode
        bcs prp_playerdata

; Relocate player code.
prp_playercode:
        jsr prp_getbyte
        pha
        jsr io_putchar
        pla
        tax
        ldy packer_instructionlist,x
        dey
        beq prp_loop
        dey
        beq prp_2byte
        bne prp_3byte
prp_2byte:
        jsr prp_getbyte
        jsr io_putchar
        jmp prp_loop
prp_3byte:
        jsr prp_getbyte
        sta packer_reloccurrentlobyte
        jsr prp_getbyte
        sta packer_reloccurrenthibyte
; See if this instructions accesses a page that holds some table.
        ldx #0
prp_intableloop:
        lda packer_reloccurrenthibyte
        cmp packer_relocdestinations+1,x
        bne prp_intablecont
        lda packer_reloccurrentlobyte
        cmp packer_relocdestinations,x
        beq prp_table
prp_intablecont:
        inx
        inx
        inx
        inx
        cpx #RELOCATETABLELENGTH
        bne prp_intableloop
; Absolute addresses outside the players address space must be kept unchanged.
        cmp #>VPLAYER
        bcc prp_putword
        cmp #>VPLAYEREND+1
        bcs prp_putword
; If we are here, this is an internal absolute address in the player.
        sec
        sbc #>VPLAYER
        clc
        adc packer_playerdestpage
        sta packer_reloccurrenthibyte
        bcc prp_putword
; Relocate some table.
prp_table:
        lda packer_relocdestinations+2,x
        sta packer_reloccurrentlobyte
        lda packer_relocdestinations+3,x
        sta packer_reloccurrenthibyte
prp_putword:
        lda packer_reloccurrentlobyte
        jsr io_putchar
        lda packer_reloccurrenthibyte
        jsr io_putchar
        jmp prp_loop

; Relocate player data.
prp_playerdata:
; Relocate effect pointer high bytes.
        ldx #16
prp_effectptrloop:
        jsr prp_getbyte
        sec
        sbc #>VPLAYER
        clc
        adc packer_playerdestpage
        jsr io_putchar
        dex
        bne prp_effectptrloop
; And now copy all the rest unchanged.
prp_copyloop:
        jsr prp_getbyte
        jsr io_putchar
        jmp prp_copyloop

; ======================================
prp_getbyte:
; Read next byte from player.
; If there are no more bytes, exits caller
; by popping the callers return address. Ugly hacking.
; ======================================
; Output: A: byte
; ======================================
        ldy #$00
        lda (stringptr),y
        inc stringptr
        bne prp_getbyte0
        inc stringptr+1
prp_getbyte0:
        ldy stringptr+1
        cpy display_datasrc+1
        bcc prp_getbyte1
        ldy stringptr
        cpy display_datasrc
        bcc prp_getbyte1
        beq prp_getbyte1
        pla
        pla
prp_getbyte1:
        rts

; ======================================
packer_relocplayer:
; Relocate and save player code.
; ======================================
; Save first 32 bytes.
        ldx #<VPLAYER
        ldy #>VPLAYER
        stx stringptr
        sty stringptr+1
        ldx #<VPLAYER+$20
        stx display_datasrc
        sty display_datasrc+1
        jsr packer_relocplayerpiece

; Now save song title. Convert from screen codes to ASCII.
        ldx #0
prp_playersavetitle:
        lda SONGTITLE,x
        cmp #$20
        bcs prp_playersavetitle0
        ora #$40
prp_playersavetitle0:
        jsr io_putchar
        inx
        cpx #SONGTITLELEN
        bne prp_playersavetitle

; Save rest of player code and data.
        ldx #<VPLAYER+$40
        ldy #>VPLAYER
        stx stringptr
        sty stringptr+1
        ldx #<VPLAYEREND
        ldy #>VPLAYEREND
        stx display_datasrc
        sty display_datasrc+1
        jmp packer_relocplayerpiece

; ======================================
packer_savetables:
; Save song start positions list, decompiled orderlist,
; instrument tables, wave, arpeggio and wave table.
; ======================================
; Save song start table.
        lda packer_songstartlistlength
        ldx #<SONGSTARTTABLE
        ldy #>SONGSTARTTABLE
        jsr packer_savetable

; Save transpose table for channel 1.
        ldy #1
        jsr packer_savetracktranspose
; Save track pointer low byte for channel 1.
        ldy #0
        jsr packer_savetrackpointerslo
; Save track pointer high byte for channel 1.
        ldy #0
        jsr packer_savetrackpointershi
; Save transpose table for channel 2.
        ldy #3
        jsr packer_savetracktranspose
; Save track pointer low byte for channel 2.
        ldy #2
        jsr packer_savetrackpointerslo
; Save track pointer high byte for channel 2.
        ldy #2
        jsr packer_savetrackpointershi
; Save transpose table for channel 3.
        ldy #5
        jsr packer_savetracktranspose
; Save track pointer low byte for channel 3.
        ldy #4
        jsr packer_savetrackpointerslo
; Save track pointer high byte for channel 3.
        ldy #4
        jsr packer_savetrackpointershi

; Save instrument tables. Do not save the first byte. (Instrument 0.)
        ldx #<INSTRUMENTS_AD
        ldy #>INSTRUMENTS_AD
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_SR
        ldy #>INSTRUMENTS_SR
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_WAVETABLESTART
        ldy #>INSTRUMENTS_WAVETABLESTART
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_WAVETABLEEND
        ldy #>INSTRUMENTS_WAVETABLEEND
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_WAVETABLELOOP
        ldy #>INSTRUMENTS_WAVETABLELOOP
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_ARPTABLESTART
        ldy #>INSTRUMENTS_ARPTABLESTART
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_ARPTABLEEND
        ldy #>INSTRUMENTS_ARPTABLEEND
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_ARPTABLELOOP
        ldy #>INSTRUMENTS_ARPTABLELOOP
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_VIBDELAY
        ldy #>INSTRUMENTS_VIBDELAY
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_VIBDEPTH_SPEED
        ldy #>INSTRUMENTS_VIBDEPTH_SPEED
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_PULSEWIDTH
        ldy #>INSTRUMENTS_PULSEWIDTH
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_PULSESPEED
        ldy #>INSTRUMENTS_PULSESPEED
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_PULSELIMITS
        ldy #>INSTRUMENTS_PULSELIMITS
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_FILTERTABLESTART
        ldy #>INSTRUMENTS_FILTERTABLESTART
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_FILTERTABLEEND
        ldy #>INSTRUMENTS_FILTERTABLEEND
        jsr packer_saveinstrumenttable
        ldx #<INSTRUMENTS_FILTERTABLELOOP
        ldy #>INSTRUMENTS_FILTERTABLELOOP
        jsr packer_saveinstrumenttable

; Save wave table.
        lda WAVETABLE
        jsr io_putchar
        lda packer_wavetablelength
        ldx #<WAVETABLE+1
        ldy #>WAVETABLE
        jsr packer_savetable
; Save arpeggio table.
        lda ARPEGGIOTABLE
        jsr io_putchar
        lda packer_arptablelength
        ldx #<ARPEGGIOTABLE+1
        ldy #>ARPEGGIOTABLE
        jsr packer_savetable
; Save filter table.
        lda FILTERTABLE
        jsr io_putchar
        lda packer_filtertablelength
        ldx #<FILTERTABLE+1
        ldy #>FILTERTABLE
        jmp packer_savetable

; ======================================
packer_savetracks:
; ======================================
        ldx #0
pst_nexttrack:
        txa
        pha
        lda packer_usedtracks,x
        jsr editor_maketrackpointer
        lda #192
        ldx editor_trackptr
        ldy editor_trackptr+1
        jsr packer_savetable
        pla
        tax
        inx
        cpx packer_usedtracksnum
        bne pst_nexttrack
        rts

; ======================================
packer_savetracktranspose:
; ======================================
;  Input: Y: 1: save track transpose of channel 1 for all orders
;            3: save track transpose of channel 2 for all orders
;            5: save track transpose of channel 3 for all orders
; ======================================
        sty pstt_whichchannel+1
        ldx #0
        stx packer_currentorder
pstt_orderloop:
        ldy packer_currentorder
        lda ORDERLIST,y
        jsr editor_makepatternpointer
pstt_whichchannel:
        ldy #$00                        ; Self modifying code.
        lda (editor_patternptr),y
        jsr io_putchar
; Advance to next order.
        inc packer_currentorder
        lda packer_currentorder
        cmp packer_orderlistlength
        bne pstt_orderloop
        rts

; ======================================
packer_savetrackpointerslo:
; ======================================
;  Input: Y: 0: save track transpose of channel 1 for all orders
;            2: save track transpose of channel 2 for all orders
;            4: save track transpose of channel 3 for all orders
; ======================================
        sty pstpl_whichchannel+1
        ldx #0
        stx packer_currentorder
pstpl_orderloop:
        ldy packer_currentorder
        lda ORDERLIST,y
        jsr editor_makepatternpointer
pstpl_whichchannel:
        ldy #$00                        ; Self modifying code.
        lda (editor_patternptr),y
        jsr packer_lookuptrack
        jsr editor_maketrackpointer
; Adjust track pointer.
        lda editor_trackptr
        clc
        adc packer_tracksbase
        jsr io_putchar
; Advance to next order.
        inc packer_currentorder
        lda packer_currentorder
        cmp packer_orderlistlength
        bne pstpl_orderloop
        rts

; ======================================
packer_savetrackpointershi:
; ======================================
;  Input: Y: 0: save track transpose of channel 1 for all orders
;            2: save track transpose of channel 2 for all orders
;            4: save track transpose of channel 3 for all orders
; ======================================
        sty pstph_whichchannel+1
        ldx #0
        stx packer_currentorder
pstph_orderloop:
        ldy packer_currentorder
        lda ORDERLIST,y
        jsr editor_makepatternpointer
pstph_whichchannel:
        ldy #$00                        ; Self modifying code.
        lda (editor_patternptr),y
        jsr packer_lookuptrack
        jsr editor_maketrackpointer
; Adjust track pointer.
        lda editor_trackptr+1
        sec
        sbc #>TRACKS_BASE
        sta editor_trackptr+1
        lda editor_trackptr
        clc
        adc packer_tracksbase
        sta editor_trackptr
        lda editor_trackptr+1
        adc packer_tracksbase+1
        jsr io_putchar
; Advance to next order.
        inc packer_currentorder
        lda packer_currentorder
        cmp packer_orderlistlength
        bne pstph_orderloop
        rts

; ======================================
packer_lookuptrack:
; Remap the track number.
; ======================================
;  Input: A: track number from the editor.
; Output: A: track number remaped according to the used tracks.
; ======================================
        ldx #$00
plut_seenexttrack:
        cmp packer_usedtracks,x
        beq plut_trackfound
        inx
        cpx packer_usedtracksnum
        bne plut_seenexttrack
plut_trackfound:
        txa
        rts

; ======================================
packer_saveinstrumenttable:
; Save some instrument parameter. (AD, SR, etc.)
; ======================================
;  Input: Y:X: table
; ======================================
        lda packer_lastusedinstrument
        clc
        adc #1

; ======================================
packer_savetable:
; ======================================
;  Input: Y:X: table
;         A: number of elements to save
; ======================================
        stx pst_source+1
        sty pst_source+2
        sta pst_loop+1
        ldx #0
pst_loop:
        cpx #$00                        ; Self modifying code.
        beq pst_done
pst_source:
        lda $ffff,x                     ; Self modifying code.
        jsr io_putchar
        inx
        bne pst_loop
pst_done:
        rts

; ======================================
console_waitkey:
; ======================================
;  Output: A: keycode (always non-zero)
; ======================================
        jsr getin
        cmp #0
        beq console_waitkey
        rts

; ======================================
console_hidespritecursor:
; Hide sprite cursor by moving it out of screen.
; ======================================
        ldx #41
        ldy #0

; ======================================
console_setspritecursor:
;  Input: X: X position
;         Y: Y position
; ======================================
; Set Y*8+$31
        tya
        asl
        asl
        asl
        adc #$31
        sta $d001
; Set X*8+$16
        txa
        ldx #SPRITEXMSB
        asl
        asl
        asl
        bcc css_nooverflow1
        inx
css_nooverflow1:
        clc
        adc #$16
        bcc css_nooverflow2
        inx
css_nooverflow2:
        sta $d000
        stx $d010
        rts

; ======================================
console_setcolor:
;  Input: A: color
; Output: console_color+1
; ======================================
        sta console_color+1
        rts

; ======================================
console_setcolormask:
;  Input: A: color mask
; Output: console_colormask+1
; ======================================
        sta console_colormask+1
        sta consolenc_colormask+1
        rts

; ======================================
console_setcolorandmask:
;  Input: A: color
;         X: color mask
; Output: console_color+1
;         console_colormask+1
; ======================================
        sta console_color+1
        stx console_colormask+1
        stx consolenc_colormask+1
        rts

; ======================================
console_setcursorpos:
;  Input: X: X position
;         Y: Y position
; Output: console_screenptr+1, console_screenptr+2
; ======================================
        stx csc_x+1
        tya
        asl
        tay
        lda screenptrs,y
csc_x:
        adc #$00
        sta console_screenptr+1
        sta consolenc_screenptr+1
        sta console_colramptr+1
        lda screenptrs+1,y
        adc #$00
        sta console_screenptr+2
        sta consolenc_screenptr+2
        adc #$d4                        ; !!!! Bloody hack. $d400=$d800-$0400
        sta console_colramptr+2
        rts

; ======================================
console_writespace:
; Print a space.
; ======================================
        lda #$20

; ======================================
console_writechar:
; Print a character.
; ======================================
;  Input: A: byte
; ======================================
console_colormask:
        ora #$00                        ; Self modifying code.
console_screenptr:
        sta $ffff                       ; Self modifying code.
console_color:
        lda #$00                        ; Self modifying code.
console_colramptr:
        sta $ffff                       ; Self modifying code.

; ======================================
console_cursorright:
; Move cursor right.
; ======================================
        inc console_screenptr+1
        bne ccr_noof1
        inc console_screenptr+2
ccr_noof1:
        inc console_colramptr+1
        bne ccr_noof2
        inc console_colramptr+2
ccr_noof2:
        rts

; ======================================
console_writespaces:
; Print Y spaces.
; ======================================
;  Input: Y: number of spaces
; ======================================
        lda #$20

; ======================================
console_writechars:
; Print the same character several times character.
; ======================================
;  Input: A: byte
;         Y: repeat count
; ======================================
        pha
        jsr console_writechar
        pla
        dey
        bne console_writechars
        rts

; ======================================
consolenc_writespace:
; Print a space.
; Special version that does not write to color RAM.
; ======================================
        lda #$20

; ======================================
consolenc_writechar:
; Print a character.
; Special version that does not write to color RAM.
; ======================================
;  Input: A: byte
; ======================================
consolenc_colormask:
        ora #$00                        ; Self modifying code.
consolenc_screenptr:
        sta $ffff                       ; Self modifying code.

; ======================================
consolenc_cursorright:
; Move cursor right.
; Special version that does not write to color RAM.
; ======================================
        inc consolenc_screenptr+1
        bne ccrnc_noof1
        inc consolenc_screenptr+2
ccrnc_noof1:
        rts

; ======================================
consolenc_writespaces:
; Print Y spaces.
; Special version that does not write to color RAM.
; ======================================
;  Input: Y: number of spaces
; ======================================
        lda #$20

; ======================================
consolenc_writechars:
; Print the same character several times character.
; Special version that does not write to color RAM.
; ======================================
;  Input: A: byte
;         Y: repeat count
; ======================================
        pha
        jsr consolenc_writechar
        pla
        dey
        bne consolenc_writechars
        rts

; ======================================
console_writestringxy:
; Print a string terminated by $ff.
; ======================================
;  Input: X: string pointer low byte
;         Y: string pointer high byte
; ======================================
        stx stringptr
        sty stringptr+1

; ======================================
console_writestring:
; Print a string terminated by $ff.
; ======================================
;  Input: stringptr: String pointer (16 bit)
; ======================================
        ldy #$00
cws_next:
        lda (stringptr),y
        cmp #$ff
        beq cws_done
        jsr console_writechar
        inc stringptr
        bne cws_nohi
        inc stringptr+1
cws_nohi:
        jmp cws_next
cws_done:
        rts

; ======================================
console_writestringlen:
; Print a string whose length is given in X.
; ======================================
;  Input: stringptr: String pointer (16 bit)
;         X: length of string
; ======================================
        ldy #$00
cwsl_next:
        lda (stringptr),y
        jsr console_writechar
        iny
        dex
        bne cwsl_next
        rts

; ======================================
console_writepackedstringxy:
; Print an RLE coded string terminated by $ff.
; $fe is RLE escape byte followed by count and char.
; ======================================
;  Input: X: string pointer low byte
;         Y: string pointer high byte
; ======================================
        stx stringptr
        sty stringptr+1

; ======================================
console_writepackedstring:
; Print an RLE coded string terminated by $ff.
; $fe is RLE escape byte followed by count and char.
; ======================================
;  Input: stringptr: -> string pointer
; ======================================
        ldy #0
cwps_loop:
        jsr cwps_getchar                ; Get character into A.
        cmp #$ff
        beq cwps_done                   ; End marker found.
        cmp #$fe
        beq cwps_depack                 ; RLE escape byte found.
        jsr console_writechar           ; Write simple character.
        jmp cwps_cont
; Depack RLE.
cwps_depack:
        jsr cwps_getchar                ; Get repeat count.
        tax
        jsr cwps_getchar                ; Get character into A.
cwps_depackloop:
        pha
        jsr console_writechar
        pla
        dex
        bne cwps_depackloop
cwps_cont:
        jmp cwps_loop
; Advance string pointer.
cwps_getchar:
        lda (stringptr),y
cwps_advance:
        inc stringptr
        bne cwps_nohi
        inc stringptr+1
cwps_nohi:
cwps_done:
        rts

; ======================================
console_writehex:
; Print a byte in hex.
; ======================================
;  Input: A: byte
; ======================================
        pha
        lsr
        lsr
        lsr
        lsr
        tax
        lda hexdigitsscreen,x
        jsr console_writechar
        pla
        and #$0f
        tax
        lda hexdigitsscreen,x
        jsr console_writechar
        rts

; ======================================
consolenc_writehex:
; Print a byte in hex.
; Special version that does not write to color RAM.
; ======================================
;  Input: A: byte
; ======================================
        pha
        lsr
        lsr
        lsr
        lsr
        tax
        lda hexdigitsscreen,x
        jsr consolenc_writechar
        pla
        and #$0f
        tax
        lda hexdigitsscreen,x
        jsr consolenc_writechar
        rts

; ======================================
console_writecharatxy:
; Print a character in hex at X,Y.
; ======================================
;  Input: A: character
;         X: X position
;         Y: Y position
; ======================================
        pha
        jsr console_setcursorpos
        pla
        jmp console_writechar

; ======================================
console_writehexatxy:
; Print a byte in hex at X,Y.
; ======================================
;  Input: A: byte
;         X: X position
;         Y: Y position
; ======================================
        pha
        jsr console_setcursorpos
        pla
        jmp console_writehex

; ======================================
console_fillblock:
; Fill a rectangular block with character in A at current cursor position.
; ======================================
;  Input: A: character
;         X: width
;         Y: height
; ======================================
        sta cfb_char+1
        dex
        stx cfb_width+1
        lda console_screenptr+1
        sta cfb_screenptr+1
        lda console_screenptr+2
        sta cfb_screenptr+2
cfb_char:
        lda #$00                        ; Self modifying code.
cfb_width:
        ldx #$00                        ; Self modifying code.
cfb_screenptr:
        sta $ffff,x                     ; Self modifying code.
        dex
        bpl cfb_screenptr
        lda cfb_screenptr+1
        clc
        adc #40
        sta cfb_screenptr+1
        lda cfb_screenptr+2
        adc #$00
        sta cfb_screenptr+2
        dey
        bne cfb_char
        rts

; ======================================
console_fillcolorramblock:
; Fill a rectangular block in the color RAM with color in A
; at current cursor position.
; ======================================
;  Input: A: character
;         X: width
;         Y: height
; ======================================
        sta cfcb_color+1
        dex
        stx cfcb_width+1
        lda console_colramptr+1
        sta cfcb_screenptr+1
        lda console_colramptr+2
        sta cfcb_screenptr+2
cfcb_color:
        lda #$00                        ; Self modifying code.
cfcb_width:
        ldx #$00                        ; Self modifying code.
cfcb_screenptr:
        sta $ffff,x                     ; Self modifying code.
        dex
        bpl cfcb_screenptr
        lda cfcb_screenptr+1
        clc
        adc #40
        sta cfcb_screenptr+1
        lda cfcb_screenptr+2
        adc #$00
        sta cfcb_screenptr+2
        dey
        bne cfcb_color
        rts

; ======================================
console_gethexatxy:
; Get a hex byte at X,Y.
; ======================================
;  Input: A: old byte
;         X: X position
;         Y: Y position
; Output: A: entered byte
;         C: If clear, byte was entered.
;         C: If set, RUN/STOP was hit, A = old byte.
; ======================================
        sta cgh_quit+1
        sta cgh_done+1
        stx display_x
        sty display_y
        jsr console_writehexatxy
        ldx display_x
        ldy display_y
        jsr console_setspritecursor
cgh_loop1:
        jsr getin
        cmp #KEY_RUNSTOP
        beq cgh_quit
        cmp #KEY_RETURN
        beq cgh_done
        jsr ascii2hexdigit
        bmi cgh_loop1
        ldx cgh_done+1
        jsr replacehighnybble
        sta cgh_done+1
        ldx display_x
        ldy display_y
        jsr console_writehexatxy
        ldx display_x
        inx
        ldy display_y
        jsr console_setspritecursor
cgh_loop2:
        jsr getin
        cmp #KEY_RUNSTOP
        beq cgh_quit
        cmp #KEY_RETURN
        beq cgh_done
        jsr ascii2hexdigit
        bmi cgh_loop2
        ldx cgh_done+1
        jsr replacelownybble
        sta cgh_done+1
        ldx display_x
        ldy display_y
        jsr console_writehexatxy

cgh_done:
        lda #$00                        ; Self modifying code.
        clc
        rts
cgh_quit:
        lda #$00                        ; Self modifying code.
        sec
        rts

; ======================================
console_getstringatxy:
; Read a string at X,Y.
; ======================================
;  Input: A: string length
;         X: X position
;         Y: Y position
;         stringptr: String pointer (16 bit)
; ======================================
        stx display_x
        sty display_y
        sta cgs_length+1
        tax
        dex
        stx list_length
        lda #0
        sta cgs_cursorpos+1
        lda #$20                        ; Add space when deleting.
        sta list_defaultelement
cgs_loop:
        ldx display_x
        ldy display_y
        jsr console_setcursorpos
cgs_length:
        ldx #$00                        ; Self modifying code.
        jsr console_writestringlen
        lda display_x
        clc
        adc cgs_cursorpos+1
        tax
        ldy display_y
        jsr console_setspritecursor
        jsr console_waitkey
        cmp #KEY_RUNSTOP
        beq cgs_quit
        cmp #KEY_RETURN
        beq cgs_done
        cmp #KEY_LEFT
        beq cgs_left
        cmp #KEY_RIGHT
        beq cgs_right
        cmp #KEY_DELETE
        beq cgs_delete
; Insert character into string.
        pha
        lda cgs_cursorpos+1
        ldx stringptr
        ldy stringptr+1
        jsr list_insert
cgs_cursorpos:
        ldy #$00                        ; Self modifying code.
        pla
        and #$3f
        sta (stringptr),y
; Move cursor right.
cgs_right:
        ldy cgs_cursorpos+1
        iny
        cpy cgs_length+1
        bcs cgs_right0
cgs_right1:
        sty cgs_cursorpos+1
cgs_right0:
        jmp cgs_loop
; Move cursor left.
cgs_left:
        ldy cgs_cursorpos+1
        dey
        bpl cgs_right1
        bmi cgs_loop
; Backspace.
cgs_delete:
        ldy cgs_cursorpos+1
        dey
        bmi cgs_loop
        sty cgs_cursorpos+1
        tya
        ldx stringptr
        ldy stringptr+1
        jsr list_delete
        jmp cgs_loop

cgs_done:
        clc
        rts
cgs_quit:
        sec
        rts

; ======================================
ascii2hexdigit:
; Convert ASCII charactor code to hex digit, like this:
; '0'->$00, ... 'A'->$0a, ... 'F'->$0f
; ======================================
;  Input: A: character representing a hex digit
; Output: A: hex digit value or $ff if input was in [0-9] or [A-Z]
; ======================================
        ldx #$0f
a2h_loop:
        cmp hexdigitsascii,x
        beq a2h_break
        dex
        bpl a2h_loop
a2h_break:
        txa
        rts

; ======================================
replacelownybble:
; Replace low nybble of X by A and return result in A.
; ======================================
        sta replacelownybble1+1
        txa
        and #$f0
replacelownybble1:
        ora #$00
        rts

; ======================================
replacehighnybble:
; Replace high nybble of X by A and return result in A.
; ======================================
        asl
        asl
        asl
        asl
        sta replacehighnybble1+1
        txa
        and #$0f
replacehighnybble1:
        ora #$00
        rts

; Data for list insert/delete.
list_length:            .byte 0
list_defaultelement:    .byte 0

; ======================================
list_insert:
; Insert into orderlist, wave or arpeggio table.
; ======================================
;  Input: A: index in list where insertion happens
;         X: pointer to list low byte
;         Y: pointer to list high byte
;         list_length: last valid element in list ($ff means 256 elements)
; ======================================
; Does not make much sense to insert at last element, so avoid that.
        cmp list_length
        beq li_last
        sta li_index+1
        stx editor_temptrackptr
        sty editor_temptrackptr+1
        ldy list_length
li_loop:
        dey
        lda (editor_temptrackptr),y
        iny
        sta (editor_temptrackptr),y
        dey
li_index:
        cpy #$00                        ; Self modifying code.
        bne li_loop
li_last:
        rts

; ======================================
list_delete:
; Delete from orderlist, wave or arpeggio table.
; ======================================
;  Input: A: index in list where deletion happens
;         X: pointer to list low byte
;         Y: pointer to list high byte
;         list_length: last valid element in list ($ff means 256 elements)
;         list_defaultelement: byte that is inserted at list end
; ======================================
; When deleting from last element, nothing has to be moved.
        stx editor_temptrackptr
        sty editor_temptrackptr+1
        tay
        cpy list_length
        beq ld_last
ld_loop:
        iny
        lda (editor_temptrackptr),y
        dey
        sta (editor_temptrackptr),y
        iny
        cpy list_length
        bne ld_loop
ld_last:
        lda list_defaultelement
        sta (editor_temptrackptr),y
ld_first:
        rts

; ======================================
clear_song:
; Clear orderlist, patterns, track.
; ======================================
; Nuke orderlist.
        ldx #>ORDERLIST
        ldy #$01
        jsr memclearpages
; Nuke patterns.
        ldx #>PATTERNS
        ldy #$06
        jsr memclearpages
; Nuke tracks.
        ldx #>TRACKS_BASE
        ldy #$60
        jsr memclearpages
; Nuke title.
        lda #$20
        ldx #SONGTITLELEN-1
csct_loop:
        sta SONGTITLE,x
        dex
        bpl csct_loop
        rts

; ======================================
clear_instruments:
; Clear all instrument data.
; ======================================
; Nuke instruments.
        ldx #>INSTRUMENTS
        ldy #$02
        jsr memclearpages
; Nuke wave table.
        ldx #>WAVETABLE
        ldy #$01
        jsr memclearpages
; Nuke arpeggio table.
        ldx #>ARPEGGIOTABLE
        ldy #$01
        jsr memclearpages
; Nuke filter table.
        ldx #>FILTERTABLE
        ldy #$01
        jsr memclearpages
; Nuke instrument names.
        lda #$20
        ldx #>INSTRUMENTNAMES
        ldy #$02
        jmp memsetpages

; ======================================
clear_all:
; Clear song, instruments, reset player.
; ======================================
        jsr clear_song
        jsr clear_instruments
        jmp player_init

; ======================================
memclearpages:
; Fill memory with 0.
; ======================================
;  Input: X: page number
;         Y: number of pages
; ======================================
        lda #$00

; ======================================
memsetpages:
; Fill memory with a given byte.
; ======================================
;  Input: A: fill byte
;         X: page number
;         Y: number of pages
; ======================================
        stx msp_fillpage+2
        ldx #0
msp_fillpage:
        sta $ff00,x                     ; Self modifying code.
        inx
        bne msp_fillpage
        inc msp_fillpage+2
        dey
        bne msp_fillpage
        rts

; ======================================
memcpypages:
; Copy memory pages. Overlapping areas are not guaranteed to copy correctly.
; ======================================
;  Input: A: number of pages to copy
;         X: source page number
;         Y: destination page number
; ======================================
        stx mcp_src+2
        sty mcp_dest+2
        tay
        ldx #$00
mcp_src:
        lda $ff00,x                     ; Self modifying code.
mcp_dest:
        sta $ff00,x                     ; Self modifying code.
        inx
        bne mcp_src
        inc mcp_src+2
        inc mcp_dest+2
        dey
        bne mcp_src
        rts

; ======================================
div16:
; Divide 16 bit by 16 bit, result is 16 bit. Horrible coding. :(
; ======================================
;  Input: div16_dividend: numerator
;         div16_divisor:  denominator
; Output: div16_quotient: result
; ======================================
        lda #0
        sta div16_quotient
        sta div16_quotient+1
div16_next:
        lda div16_dividend
        sec
        sbc div16_divisor
        sta div16_dividend
        lda div16_dividend+1
        sbc div16_divisor+1
        sta div16_dividend+1
        bcc div16_done
        inc div16_quotient
        bne div16_next
        inc div16_quotient+1
        bne div16_next
div16_done:
        rts

; ======================================
jsrya:
; Call subroutine in Y:A.
; ======================================
;  Input: Y:A: address of routine,
; ======================================
        sta jsrya0+1
        sty jsrya0+2
jsrya0:
        jmp $ffff                       ; Self modifying code.

; ======================================
; Editor's readonly data.
; ======================================

screenptrs:     .word $0400,$0428,$0450,$0478,$04a0,$04c8,$04f0,$0518
                .word $0540,$0568,$0590,$05b8,$05e0,$0608,$0630,$0658
                .word $0680,$06a8,$06d0,$06f8,$0720,$0748,$0770,$0798
                .word $07c0

; Hex digits in screen codes and in ASCII codes.
hexdigitsscreen:.byte $30, $31, $32, $33, $34, $35, $36, $37, $38, $39, $01, $02, $03, $04, $05, $06
hexdigitsascii: .byte KEY_0, KEY_1, KEY_2, KEY_3, KEY_4, KEY_5, KEY_6, KEY_7
                .byte KEY_8, KEY_9, KEY_A, KEY_B, KEY_C, KEY_D, KEY_E, KEY_F

; Call table for functions processing events in all 6 editor screens.
editorloop_entrieslo:   .byte <editor_editorder
                        .byte <editor_editpattern
                        .byte <editor_editinstrument
                        .byte <editor_configmenu
                        .byte <editor_specmenu
                        .byte <editor_diskmenu
editorloop_entrieshi:   .byte >editor_editorder
                        .byte >editor_editpattern
                        .byte >editor_editinstrument
                        .byte >editor_configmenu
                        .byte >editor_specmenu
                        .byte >editor_diskmenu

; Starting help pages for all 6 editor screens.
editor_contexthelppages:        .byte 15, 8, 3, 16, 17, 18

; X positions for channels in pattern display.
editor_channelxpositions:       .byte 5,17,29

; Cursor X positions in pattern editor.
editor_patternfieldxpositions:  .byte 0, 4, 5, 7, 8, 9
; Cursor X positions in instrument editor.
editor_instfieldxpositions:     .byte 19, 25, 31, 37

; Instrument 0 really means no instrument. This is the default name for that.
instrument0name .byte $1b,$0e,$0f,$20,$20,$09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$1d,$ff ; [no  instrument]

; "Device not present" text.
io_devicenotpresenttext:        .byte $04,$05,$16,$09,$03,$05,$20,$0e,$0f,$14,$20,$10,$12,$05,$13,$05,$0e,$14,$ff   ; device not present
IO_DEVICENOTPRESENTTEXTLENGTH   = *-io_devicenotpresenttext

; RLE coded "loading                          " text.
io_loadingtext:                 .byte $0c,$0f,$01,$04,$09,$0e,$07,$fe,$1a,$20,$ff       ; loading
; RLE coded "saving                           " text.
io_savingtext:                  .byte $13,$01,$16,$09,$0e,$07,$fe,$1b,$20,$ff           ; saving

; "press any key." text.
dm_pressanykeytext:             .byte $0d,$50,$52,$45,$53,$53,$20,$41,$4e,$59,$20,$4b,$45,$59,$2e,$00       ; press any key.

; RLE coded static panel text.
paneltext:      .byte $fe,$08,$60
                .byte $46,$71,$60,$46,$4f,$52,$60,$48,$45,$4c,$50       ; f1 for help
                .byte $fe,$1d,$60
                .byte $45,$44,$49,$54,$60,$53,$54,$45,$50,$7a           ; edit step:
                .byte $fe,$22,$60
                .byte $53,$50,$45,$45,$44,$7a                           ; speed:
                .byte $fe,$1e,$60
                .byte $52,$41,$53,$54,$45,$52,$7a,$a0,$a0,$6f           ; raster:  /
                .byte $fe,$1d,$60
                .byte $54,$49,$4d,$45,$7a,$a0,$a0,$ba,$a0,$a0,$ae       ; time:
                .byte $fe,$3e,$60
                .byte $ff

; RLE coded static pattern editor text. (Only the channel headers.)
patterntext:    .byte $4f,$43,$54,$60,$60                               ; oct.
                .byte $54,$52,$4b,$60,$60,$60,$54,$52,$fe,$04,$60       ; trk.. tr..
                .byte $54,$52,$4b,$60,$60,$60,$54,$52,$fe,$04,$60       ; trk.. tr..
                .byte $54,$52,$4b,$60,$60,$60,$54,$52,$60,$60,$60       ; trk.. tr..
                .byte $ff

; RLE coded static instrument editor text.
instrumenttext: .byte $4e,$41,$4d,$45,$7a,$fe,$10,$a0   ; name:
                .byte $60
                .byte $57,$41,$56,$45                   ; wave
                .byte $60,$60
                .byte $41,$52,$50                       ; arp
                .byte $60,$60,$60
                .byte $46,$49,$4c,$54                   ; filt
                .byte $60,$60
                .byte $fe,$2e,$20
                .byte $01,$14,$14,$01,$03,$0b,$2f,$04,$05,$03,$01,$19,$3a                               ; attack/decay:
                .byte $fe,$18,$20
                .byte $13,$15,$13,$14,$01,$09,$0e,$2f,$12,$05,$0c,$05,$01,$13,$05,$3a                   ; sustain/release:
                .byte $fe,$17,$20
                .byte $17,$01,$16,$05,$20,$14,$01,$02,$0c,$05,$20,$13,$14,$01,$12,$14,$3a               ; wave table start:
                .byte $fe,$19,$20
                .byte $17,$01,$16,$05,$20,$14,$01,$02,$0c,$05,$20,$05,$0e,$04,$3a                       ; wave table end:
                .byte $fe,$18,$20
                .byte $17,$01,$16,$05,$20,$14,$01,$02,$0c,$05,$20,$0c,$0f,$0f,$10,$3a                   ; wave table loop:
                .byte $fe,$18,$20
                .byte $01,$12,$10,$20,$14,$01,$02,$0c,$05,$20,$13,$14,$01,$12,$14,$3a                   ; arp table start:
                .byte $fe,$1a,$20
                .byte $01,$12,$10,$20,$14,$01,$02,$0c,$05,$20,$05,$0e,$04,$3a                           ; arp table end:
                .byte $fe,$19,$20
                .byte $01,$12,$10,$20,$14,$01,$02,$0c,$05,$20,$0c,$0f,$0f,$10,$3a                       ; arp table loop:
                .byte $fe,$1a,$20
                .byte $16,$09,$02,$12,$01,$14,$0f,$20,$04,$05,$0c,$01,$19,$3a                           ; vibrato delay:
                .byte $fe,$17,$20
                .byte $16,$09,$02,$12,$20,$04,$05,$10,$14,$08,$2f,$13,$10,$05,$05,$04,$3a               ; vibr depth/speed:
                .byte $fe,$1c,$20
                .byte $10,$15,$0c,$13,$05,$20,$17,$09,$04,$14,$08,$3a                                   ; pulse width:
                .byte $fe,$1c,$20
                .byte $10,$15,$0c,$13,$05,$20,$13,$10,$05,$05,$04,$3a                                   ; pulse speed:
                .byte $fe,$1b,$20
                .byte $10,$15,$0c,$13,$05,$20,$0c,$09,$0d,$09,$14,$13,$3a                               ; pulse limits:
                .byte $fe,$15,$20
                .byte $06,$09,$0c,$14,$05,$12,$20,$14,$01,$02,$0c,$05,$20,$13,$14,$01,$12,$14,$3a       ; filter table start:
                .byte $fe,$17,$20
                .byte $06,$09,$0c,$14,$05,$12,$20,$14,$01,$02,$0c,$05,$20,$05,$0e,$04,$3a               ; filter table end:
                .byte $fe,$16,$20
                .byte $06,$09,$0c,$14,$05,$12,$20,$14,$01,$02,$0c,$05,$20,$0c,$0f,$0f,$10,$3a           ; filter table loop:
                .byte $ff

; RLE coded static config menu text.
configmenutext:
                .byte $50,$52,$45,$53,$53,$60,$52,$45,$54,$55,$52,$4e,$60,$54,$4f,$60,$55,$50,$44,$41,$54,$45,$60,$43,$4f,$4c,$4f,$52,$53,$6e ; press return to update colors.
                .byte $fe,$0a,$60
                .byte $fe,$2e,$20
                .byte $10,$01,$0e,$05,$0c,$20,$02,$01,$03,$0b,$07,$12,$0f,$15,$0e,$04,$3a       ; panel background:
                .byte $fe,$13,$20
                .byte $16,$01,$12,$09,$01,$02,$0c,$05,$13,$20,$02,$01,$03,$0b,$07,$12,$0f,$15,$0e,$04,$3a ; variables background:
                .byte $fe,$1c,$20
                .byte $13,$14,$01,$14,$09,$03,$20,$14,$05,$18,$14,$3a                           ; static text:
                .byte $fe,$17,$20
                .byte $08,$09,$07,$08,$0c,$09,$07,$08,$14,$05,$04,$20,$14,$05,$18,$14,$3a       ; highlighted text:
                .byte $fe,$15,$20
                .byte $10,$01,$14,$14,$05,$12,$0e,$20,$02,$01,$03,$0b,$07,$12,$0f,$15,$0e,$04,$3a ; pattern background:
                .byte $fe,$11,$20
                .byte $03,$15,$12,$12,$05,$0e,$14,$20,$12,$0f,$17,$20,$02,$01,$03,$0b,$07,$12,$0f,$15,$0e,$04,$3a ; current row background:
                .byte $fe,$1b,$20
                .byte $10,$01,$14,$14,$05,$12,$0e,$20,$14,$05,$18,$14,$3a ; pattern text:
                .byte $fe,$1a,$20
                .byte $0d,$15,$14,$05,$04,$20,$03,$08,$01,$0e,$0e,$05,$0c,$3a ; muted channel:
                .byte $fe,$19,$20
                .byte $13,$05,$0c,$05,$03,$14,$05,$04,$20,$02,$0c,$0f,$03,$0b,$3a ; selected block:
                .byte $fe,$21,$20
                .byte $03,$15,$12,$13,$0f,$12,$3a ; cursor:
                .byte $ff

; RLE coded static specials menu text.
specmenutext:   .byte $54,$49,$54,$4c,$45,$7a,$fe,$20,$a0,$60,$60       ; title:
                .byte $fe,$28,$20
                .byte $05,$20,$20,$20,$05,$04,$09,$14,$20,$13,$0f,$0e,$07,$20,$14,$09,$14,$0c,$05   ; e   edit song title
                .byte $fe,$15,$20
                .byte $03,$20,$20,$20,$03,$0c,$05,$01,$12,$20,$13,$0f,$0e,$07   ; c   clear song
                .byte $fe,$1a,$20
                .byte $09,$20,$20,$20,$03,$0c,$05,$01,$12,$20,$09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$13       ; i   clear instruments
                .byte $fe,$13,$20
                .byte $14,$20,$20,$20,$12,$05,$10,$0c,$01,$03,$05,$20,$09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$20,$09,$0e,$20,$14,$12,$01,$03,$0b,$13 ; t   replace instrument in tracks
                .byte $fe,$08,$20
                .byte $10,$20,$20,$20,$12,$05,$10,$0c,$01,$03,$05,$20,$09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$20,$09,$0e,$20,$10,$01,$14,$14,$05,$12,$0e,$13 ; p   replace instrument in patterns
                .byte $fe,$06,$20
                .byte $31,$20,$20,$20,$13,$17,$01,$10,$20,$14,$12,$01,$03,$0b,$13,$20,$31,$2d,$32               ; 1   swap tracks 1-2
                .byte $fe,$15,$20
                .byte $32,$20,$20,$20,$13,$17,$01,$10,$20,$14,$12,$01,$03,$0b,$13,$20,$32,$2d,$33               ; 2   swap tracks 2-3
                .byte $fe,$15,$20
                .byte $33,$20,$20,$20,$13,$17,$01,$10,$20,$14,$12,$01,$03,$0b,$13,$20,$33,$2d,$31               ; 3   swap tracks 3-2
                .byte $fe,$15,$20
                .byte $13,$20,$20,$20,$05,$04,$09,$14,$20,$13,$0f,$0e,$07,$20,$13,$14,$01,$12,$14,$20,$10,$0f,$13,$09,$14,$09,$0f,$0e,$13 ; s   edit song start positions
                .byte $ff

; RLE coded static disk menu text.
diskmenutext:   .byte $53,$54,$41,$54,$55,$53,$7a,$fe,$21,$a0
                .byte $fe,$28,$20
                .byte $24,$20,$20,$20,$04,$09,$12,$05,$03,$14,$0f,$12,$19,$20   ; $   directory
                .byte $28,$13,$08,$09,$06,$14,$3d,$10,$01,$15,$13,$05,$29       ; (shift=pause)
                .byte $fe,$0d,$20
                .byte $04,$20,$20,$20,$03,$08,$01,$0E,$07,$05,$20,$04,$05,$16,$09,$03,$05,$3a   ; D   change device
                .byte $fe,$16,$20
                .byte $0c,$20,$20,$20,$0c,$0f,$01,$04,$20,$13,$0f,$0e,$07       ; L   load song
                .byte $fe,$1b,$20
                .byte $13,$20,$20,$20,$13,$01,$16,$05,$20,$13,$0f,$0e,$07       ; S   save song
                .byte $fe,$1b,$20
                .byte $09,$20,$20,$20,$09,$0d,$10,$0f,$12,$14,$20,$31,$2e,$30,$18,$20,$13,$0f,$0e,$07       ; I   import 1.0x song
                .byte $fe,$14,$20
                .byte $12,$20,$20,$20,$12,$05,$01,$04,$20,$14,$12,$01,$03,$0b,$13       ; R   read tracks
                .byte $fe,$19,$20
                .byte $17,$20,$20,$20,$17,$12,$09,$14,$05,$20,$14,$12,$01,$03,$0b,$13   ; W   write tracks
                .byte $fe,$18,$20
                .byte $10,$20,$20,$20,$10,$01,$03,$0b,$20,$01,$0e,$04,$20,$13,$01,$16,$05       ; P   pack and save
                .byte $ff

; load filename:
loadfilenametext:       .byte $0c,$0f,$01,$04,$20,$06,$09,$0c,$05,$0e,$01,$0d,$05,$3a
                        .byte $ff

; save filename:
savefilenametext:       .byte $13,$01,$16,$05,$20,$06,$09,$0c,$05,$0e,$01,$0d,$05,$3a
                        .byte $ff

; save player:
saveplayertext:         .byte $20,$20,$13,$01,$16,$05,$20,$10,$0c,$01,$19,$05,$12,$3a
                        .byte $ff

; save tracks:
savetrackstext:         .byte $20,$20,$13,$01,$16,$05,$20,$14,$12,$01,$03,$0b,$13,$3a
                        .byte $ff

; clear song?
clearsongtext:  .byte $03,$0c,$05,$01,$12,$20,$13,$0f,$0e,$07,$3f
                .byte $ff

; clear instruments?
clearinsttext:  .byte $03,$0c,$05,$01,$12,$20,$09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$13,$3f
                .byte $ff

; are you sure?
areyousuretext: .byte $01,$12,$05,$20,$19,$0f,$15,$20,$13,$15,$12,$05,$3f
                .byte $ff

; press 'y' to confirm.
confirmationtext:       .byte $20,$10,$12,$05,$13,$13,$20,$27,$19,$27,$20,$14,$0f,$20,$03,$0f,$0e,$06,$09,$12,$0d,$2e
                        .byte $ff

; first track:
firsttracktext: .byte $06,$09,$12,$13,$14,$20,$14,$12,$01,$03,$0b,$3a
                .byte $ff

; last track:
lasttracktext:  .byte $0c,$01,$13,$14,$20,$14,$12,$01,$03,$0b,$3a
                .byte $ff

; first pattern:
firstpatterntext:       .byte $06,$09,$12,$13,$14,$20,$10,$01,$14,$14,$05,$12,$0e,$3a
                        .byte $ff

; last pattern:
lastpatterntext:        .byte $0c,$01,$13,$14,$20,$10,$01,$14,$14,$05,$12,$0e,$3a
                        .byte $ff

; load at track:
loadattracktext:        .byte $0c,$0f,$01,$04,$20,$01,$14,$20,$14,$12,$01,$03,$0b,$3a
                        .byte $ff

; replace instrument:
replaceinsttext:        .byte $09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$3a
                        .byte $ff

; replace instrument:
replacewithinsttext:    .byte $17,$09,$14,$08,$20,$09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$3a
                        .byte $ff

; player and instruments: $
playerandinsttext:      .byte $10,$0c,$01,$19,$05,$12,$20,$01,$0e,$04,$20,$09,$0e,$13,$14,$12,$15,$0d,$05,$0e,$14,$13,$3a,$20,$24
                        .byte $ff

; tracks: $
trackstext:             .byte $20,$14,$12,$01,$03,$0b,$13,$3a,$20,$24
                        .byte $ff

; bytes
bytestext:              .byte $20,$02,$19,$14,$05,$13
                        .byte $ff

; relocate player to: $0000
relocateplayertext:     .byte $12,$05,$0c,$0f,$03,$01,$14,$05,$20,$10,$0c,$01,$19,$05,$12,$20,$14,$0f,$3a,$20,$24,$30,$30,$30,$30
                        .byte $ff

; relocate tracks to:
relocatetrackstext:     .byte $12,$05,$0c,$0f,$03,$01,$14,$05,$20,$14,$12,$01,$03,$0b,$13,$20,$14,$0f,$3a,$20,$24
                        .byte $ff

; save player and tracks separately? y/n
saveseparatelytext:     .byte $13,$01,$16,$05,$20,$10,$0c,$01,$19,$05,$12,$20,$01,$0e,$04,$20,$14,$12,$01,$03,$0b,$13,$20,$13,$05,$10,$01,$12,$01,$14,$05,$0c,$19,$3f,$20,$19,$2f,$0e
                        .byte $ff

; Table for relocation.
; Each element is two words: original address and relocated.
packer_relocdestinations:
        .word SONGSTARTTABLE,                   0
        .word TRACKTRANSPOSES0,                 0
        .word TRACKPOINTERSLO0,                 0
        .word TRACKPOINTERSHI0,                 0
        .word TRACKTRANSPOSES1,                 0
        .word TRACKPOINTERSLO1,                 0
        .word TRACKPOINTERSHI1,                 0
        .word TRACKTRANSPOSES2,                 0
        .word TRACKPOINTERSLO2,                 0
        .word TRACKPOINTERSHI2,                 0
        .word INSTRUMENTS_AD,                   0
        .word INSTRUMENTS_SR,                   0
        .word INSTRUMENTS_WAVETABLESTART,       0
        .word INSTRUMENTS_WAVETABLEEND,         0
        .word INSTRUMENTS_WAVETABLELOOP,        0
        .word INSTRUMENTS_ARPTABLESTART,        0
        .word INSTRUMENTS_ARPTABLEEND,          0
        .word INSTRUMENTS_ARPTABLELOOP,         0
        .word INSTRUMENTS_VIBDELAY,             0
        .word INSTRUMENTS_VIBDEPTH_SPEED,       0
        .word INSTRUMENTS_PULSEWIDTH,           0
        .word INSTRUMENTS_PULSESPEED,           0
        .word INSTRUMENTS_PULSELIMITS,          0
        .word INSTRUMENTS_FILTERTABLESTART,     0
        .word INSTRUMENTS_FILTERTABLEEND,       0
        .word INSTRUMENTS_FILTERTABLELOOP,      0
        .word WAVETABLE,                        0
        .word ARPEGGIOTABLE,                    0
        .word FILTERTABLE,                      0
RELOCATETABLELENGTH = *-packer_relocdestinations

; ======================================
; End of editor code.
; ======================================

; ======================================
; Font.
; ======================================

        org FONT

        incbin font/font.bin

; ======================================
; Editor's uninitialized and read/write data.
; ======================================

        org RWDATA

; I had to stuff the key mapping, note strings and some more
; in here because memory under $3800 was running low. :-/

; Used in the help reader.
editor_currenthelppage  .byte 0
helppagepointers:
                        .word helppage00, helppage01, helppage02, helppage03
                        .word helppage04, helppage05, helppage06, helppage07
                        .word helppage08, helppage09, helppage10, helppage11
                        .word helppage12, helppage13, helppage14, helppage15
                        .word helppage16, helppage17, helppage18, helppage19
                        .word helppage20, helppage21
EDITOR_HELPPAGESNUM     = (*-helppagepointers)/2

; Default color sets.
editor_colorsets:
                        .byte 6         ; Panel background.
                        .byte 11        ; Variables background.
                        .byte 15        ; Static text.
                        .byte 1         ; Highlighted text.
                        .byte 0         ; Pattern background.
                        .byte 11        ; Current row highlight.
                        .byte 15        ; Pattern text.
                        .byte 12        ; Pattern text for muted channels.
                        .byte 2         ; Selected block background.
                        .byte 1         ; Sprite cursor color.
EDITOR_COLORSNUM        = *-editor_colorsets

                        .byte 9         ; Panel background.
                        .byte 8         ; Variables background.
                        .byte 15        ; Static text.
                        .byte 1         ; Highlighted text.
                        .byte 0         ; Pattern background.
                        .byte 9         ; Current row highlight.
                        .byte 15        ; Pattern text.
                        .byte 12        ; Pattern text for muted channels.
                        .byte 6         ; Selected block background.
                        .byte 1         ; Sprite cursor color.

                        .byte 6         ; Panel background.
                        .byte 14        ; Variables background.
                        .byte 7         ; Static text.
                        .byte 1         ; Highlighted text.
                        .byte 12        ; Pattern background.
                        .byte 15        ; Current row highlight.
                        .byte 1         ; Pattern text.
                        .byte 0         ; Pattern text for muted channels.
                        .byte 10        ; Selected block background.
                        .byte 1         ; Sprite cursor color.

                        .byte 11        ; Panel background.
                        .byte 11        ; Variables background.
                        .byte 5         ; Static text.
                        .byte 13        ; Highlighted text.
                        .byte 0         ; Pattern background.
                        .byte 11        ; Current row highlight.
                        .byte 5         ; Pattern text.
                        .byte 12        ; Pattern text for muted channels.
                        .byte 11        ; Selected block background.
                        .byte 3         ; Sprite cursor color.

; Very clever packing method here :) Each byte's bits are interpreted as:
; snnn0ooo
; nnn: character identifying note (1 for A, 2 for B, etc.)
; ooo: octave (0-7 range)
;   s: if set, note is sharp (like C#4 instead of C-4)
;
;                      C   C#  D   D#  E   F   F#  G   G#  A   A#  B
notestrings:    .byte $30,$b0,$40,$c0,$50,$60,$e0,$70,$f0,$10,$90,$20   ; Octave 0.
                .byte $31,$b1,$41,$c1,$51,$61,$e1,$71,$f1,$11,$91,$21   ; Octave 1.
                .byte $32,$b2,$42,$c2,$52,$62,$e2,$72,$f2,$12,$92,$22   ; Octave 2.
                .byte $33,$b3,$43,$c3,$53,$63,$e3,$73,$f3,$13,$93,$23   ; Octave 3.
                .byte $34,$b4,$44,$c4,$54,$64,$e4,$74,$f4,$14,$94,$24   ; Octave 4.
                .byte $35,$b5,$45,$c5,$55,$65,$e5,$75,$f5,$15,$95,$25   ; Octave 5.
                .byte $36,$b6,$46,$c6,$56,$66,$e6,$76,$f6,$16,$96,$26   ; Octave 6.
                .byte $37,$b7,$47,$c7,$57,$67,$e7,$77,$f7,$17,$97,$27   ; Octave 7.

; Keys that are used to enter notes.
; This key set is practically Protracker compatible.
notekeys:       .byte KEY_Z, KEY_S, KEY_X, KEY_D, KEY_C, KEY_V, KEY_G, KEY_B, KEY_H, KEY_N, KEY_J, KEY_M
                .byte KEY_Q, KEY_2, KEY_W, KEY_3, KEY_E, KEY_R, KEY_5, KEY_T, KEY_6, KEY_Y, KEY_7, KEY_U, KEY_I, KEY_9, KEY_O, KEY_0, KEY_P
NOTEKEYS_NUM    = *-notekeys

; Keys used in the instrument editor keyjazz.
; These are matrix values read from $c5.
keyjazznotekeys:        .byte $0c,$0d,$17,$12,$14,$1f,$1a,$1c,$1d,$27,$22,$24
                        .byte $3e,$3b,$09,$08,$0e,$11,$10,$16,$13,$19,$18,$1e,$21,$20,$26,$23,$29
KEYJAZZNOTEKEYS_NUM     = *-keyjazznotekeys

; Default global keys.
global_keys:            .byte KEY_SPACE
                        .word eg_playonoff
                        .byte KEY_SH_SPACE
                        .word eg_playpattern
                        .byte KEY_F1
                        .word eg_writehelp
                        .byte KEY_F2
                        .word eg_writecontexthelp
                        .byte KEY_F3
                        .word eg_gotoordereditor
                        .byte KEY_F5
                        .word eg_gotopatterneditor
                        .byte KEY_F7
                        .word eg_gotoinsteditor
                        .byte KEY_F4
                        .word eg_configmenu
                        .byte KEY_F6
                        .word eg_specmenu
                        .byte KEY_F8
                        .word eg_diskmenu
                        .byte KEY_COMMA
                        .word eg_instdec
                        .byte KEY_PERIOD
                        .word eg_instinc
                        .byte KEY_AT
                        .word eg_keypatterndec
                        .byte KEY_ASTERISK
                        .word eg_keypatterninc
                        .byte KEY_PLUS
                        .word eg_keyorderdec
                        .byte KEY_MINUS
                        .word eg_keyorderinc
                        .byte KEY_COMM_1
                        .word eg_mutechannel1
                        .byte KEY_COMM_2
                        .word eg_mutechannel2
                        .byte KEY_COMM_3
                        .word eg_mutechannel3
                        .byte KEY_COMM_4
                        .word eg_muteall
                        .byte KEY_CTRL_1
                        .word eg_octave1
                        .byte KEY_CTRL_2
                        .word eg_octave2
                        .byte KEY_CTRL_3
                        .word eg_octave3
                        .byte KEY_CTRL_4
                        .word eg_octave4
                        .byte KEY_CTRL_5
                        .word eg_octave5
                        .byte KEY_CTRL_6
                        .word eg_octave6
                        .byte KEY_CTRL_7
                        .word eg_octave7
                        .byte KEY_SH_HOME
                        .word eg_zerorastertimes
                        .byte KEY_COMM_I
                        .word eg_initplayer
GLOBAL_KEYS_NUM         = *-global_keys

; Default keys specific for orderlist editor.
editorder_keys:         .byte KEY_UP
                        .word eg_keyorderdec
                        .byte KEY_DOWN
                        .word eg_keyorderinc
                        .byte KEY_LEFT
                        .word eo_keyleft
                        .byte KEY_RIGHT
                        .word eo_keyright
                        .byte KEY_EQUALS                ; Handles SHIFT.
                        .word eo_keypgupdn
                        .byte KEY_SH_A
                        .word eo_keypgup
                        .byte KEY_SH_Z
                        .word eo_keypgdn
                        .byte KEY_HOME
                        .word eo_keygotoline00
                        .byte KEY_SH_Q
                        .word eo_keygotoline00
                        .byte KEY_SH_W
                        .word eo_keygotoline40
                        .byte KEY_SH_E
                        .word eo_keygotoline80
                        .byte KEY_SH_R
                        .word eo_keygotolinec0
                        .byte KEY_INSERT
                        .word eo_insert
                        .byte KEY_DELETE
                        .word eo_delete
                        .byte KEY_RETURN
                        .word eg_gotopatterneditor
EDITORDER_KEYS_NUM      = *-editorder_keys

; Default keys specific for pattern editor.
editpattern_keys:       .byte KEY_UP
                        .word ep_keyup
                        .byte KEY_DOWN
                        .word ep_keydown
                        .byte KEY_LEFT
                        .word ep_keyleft
                        .byte KEY_RIGHT
                        .word ep_keyright
                        .byte KEY_RUNSTOP
                        .word ep_keynextchannel
                        .byte KEY_SH_RUNSTOP
                        .word ep_keyprevchannel
                        .byte KEY_EQUALS                ; Handles SHIFT.
                        .word ep_keypgupdn
                        .byte KEY_HOME
                        .word ep_keyhome
                        .byte KEY_COLON
                        .word ep_keytrackdec
                        .byte KEY_SEMICOLON
                        .word ep_keytrackinc
                        .byte KEY_COMM_Y
                        .word ep_edittracknum
                        .byte KEY_UPARROW
                        .word ep_keyclearnote
                        .byte KEY_SLASH
                        .word ep_keyoff
                        .byte KEY_INSERT
                        .word ep_insert
                        .byte KEY_DELETE
                        .word ep_delete
                        .byte KEY_POUND
                        .word ep_deleteall
                        .byte KEY_SH_POUND
                        .word ep_insertall
                        .byte KEY_COMM_G
                        .word ep_grabeffect
                        .byte KEY_COMM_F
                        .word ep_dropeffect
                        .byte KEY_COMM_B
                        .word ep_setblockbeg
                        .byte KEY_COMM_E
                        .word ep_setblockend
                        .byte KEY_COMM_T
                        .word ep_selecttrack
                        .byte KEY_COMM_R
                        .word ep_unselectblock
                        .byte KEY_COMM_X
                        .word ep_cutblock
                        .byte KEY_COMM_C
                        .word ep_copyblock
                        .byte KEY_COMM_V
                        .word ep_pasteblock
                        .byte KEY_COMM_M
                        .word ep_mixblock
                        .byte KEY_COMM_Q
                        .word ep_transposeup
                        .byte KEY_COMM_A
                        .word ep_transposedown
                        .byte KEY_COMM_P
                        .word ep_transposecurrentup
                        .byte KEY_COMM_L
                        .word ep_transposecurrentdown
                        .byte KEY_LEFTARROW
                        .word ep_editstepincdec         ; Handles SHIFT.
                        .byte KEY_COMM_W
                        .word ep_transposeinc
                        .byte KEY_COMM_S
                        .word ep_transposedec
                        .byte KEY_COMM_D
                        .word ep_edittranspose
                        .byte KEY_COMM_Z
                        .word ep_restoreundobuffer
                        .byte KEY_RETURN
                        .word eg_playpatterncurrent
EDITPATTERN_KEYS_NUM    = *-editpattern_keys

; Default keys specific for instrument editor.
editinstrument_keys:    .byte KEY_UP
                        .word ei_keyup
                        .byte KEY_DOWN
                        .word ei_keydown
                        .byte KEY_LEFT
                        .word ei_keyleft
                        .byte KEY_RIGHT
                        .word ei_keyright
                        .byte KEY_RUNSTOP
                        .word ei_keynextfield
                        .byte KEY_SH_RUNSTOP
                        .word ei_keyprevfield
                        .byte KEY_EQUALS                ; Handles SHIFT.
                        .word ei_keypgupdn
                        .byte KEY_RETURN
                        .word ei_keygototable
                        .byte KEY_INSERT
                        .word ei_insert
                        .byte KEY_DELETE
                        .word ei_delete
                        .byte KEY_HOME
                        .word ei_keyhome
                        .byte KEY_COMM_N
                        .word ei_editname
                        .byte KEY_COMM_X
                        .word ei_cutinst
                        .byte KEY_COMM_C
                        .word ei_copyinst
                        .byte KEY_COMM_V
                        .word ei_pasteinst
                        .byte KEY_COMM_B
                        .word ei_setblockbeg
                        .byte KEY_COMM_E
                        .word ei_setblockend
                        .byte KEY_COMM_R
                        .word ei_unselectblock
                        .byte KEY_COMM_Q
                        .word ei_incblock
                        .byte KEY_COMM_A
                        .word ei_decblock
                        .byte KEY_COMM_F
                        .word ei_fillblock
EDITINSTRUMENT_KEYS_NUM = *-editinstrument_keys

; Keys for specials menu.
specmenu_keys:          .byte KEY_E
                        .word sm_edittitle
                        .byte KEY_C
                        .word sm_clearsong
                        .byte KEY_I
                        .word sm_clearinstruments
                        .byte KEY_T
                        .word sm_replaceinsttrack
                        .byte KEY_P
                        .word sm_replaceinstpattern
                        .byte KEY_1
                        .word sm_swap12
                        .byte KEY_2
                        .word sm_swap23
                        .byte KEY_3
                        .word sm_swap31
                        .byte KEY_S
                        .word sm_editsongstarts
SPECMENU_KEYS_NUM       = *-specmenu_keys

; Keys for config menu.
configmenu_keys:        .byte KEY_UP
                        .word cm_keyup
                        .byte KEY_DOWN
                        .word cm_keydown
                        .byte KEY_RETURN
                        .word cm_putcolors
                        .byte KEY_EXCL
                        .word cm_colorset1
                        .byte KEY_DOUBLEQUOT
                        .word cm_colorset2
                        .byte KEY_HASHMARK
                        .word cm_colorset3
                        .byte KEY_DOLLAR
                        .word cm_colorset4
CONFIGMENU_KEYS_NUM       = *-configmenu_keys

; Keys for disk menu.
diskmenu_keys:          .byte KEY_DOLLAR
                        .word dm_directory
                        .byte KEY_D
                        .word dm_incdiskdevice
                        .byte KEY_SH_D
                        .word dm_decdiskdevice
                        .byte KEY_L
                        .word dm_loadsong
                        .byte KEY_S
                        .word dm_savesong
                        .byte KEY_I
                        .word dm_import10song
                        .byte KEY_R
                        .word dm_readtracks
                        .byte KEY_W
                        .word dm_writetracks
                        .byte KEY_P
                        .word dm_packandsavesong
DISKMENU_KEYS_NUM       = *-diskmenu_keys

; Current colors.
editor_colors:
color_d022:             .byte 0         ; Panel background.
color_d023:             .byte 0         ; Variables background.
color_static:           .byte 0         ; Static text.
color_highlight:        .byte 0         ; Highlighted text.
color_d021:             .byte 0         ; Pattern background.
color_currentrow:       .byte 0         ; Current row highlight.
color_pattern:          .byte 0         ; Pattern text.
color_muted:            .byte 0         ; Pattern text for muted channels.
color_d024:             .byte 0         ; Selected block background.
color_cursor:           .byte 0         ; Sprite cursor color.

editor_playmode:        .byte 0         ; 0: not running, 1: play song, 2: keyjazz
editor_whichscreen:     .byte 0         ; Editor screens. See constants EDITOR_*
editor_currentkey:      .byte 0         ; Key returned by getin.
editor_currentraster:   .byte 0         ; Current rastertime used in player.
editor_maxraster:       .byte 0         ; Max rastertime used in player.
editor_currentkeyjazznote: .byte 0      ; Current note when testing in instrument editor.

; Track numbers currently visible in the pattern editor.
editor_tracks:          .byte 0, 0, 0
editor_tracktransposes: .byte 0, 0, 0

; Block begin/end set flags and begin/end rows in the pattern editor.
editor_blockchannel:    .byte 0         ; Which channel is the block in?
editor_trackblockflags: .byte 0
editor_trackblockbeg:   .byte 0
editor_trackblockend:   .byte 0

; Temporary channel number and first and last rows touched in block operations.
ep_execblockchannel:    .byte 0
ep_execblockbeg:        .byte 0
ep_execblockend:        .byte 0

; Cursor location in orderlist editor.
editor_ordercol:        .byte 0         ; valid: $00..$01

; Cursor location in pattern editor.
editor_patternchannel:  .byte 0
; Never change these, since they index into editor_patternfieldxpositions[]
; 0: note
; 1: instrument high nybble
; 2: instrument low nybble
; 3: effect
; 4: effect parameter high nybble
; 5: effect parameter low nybble
editor_patternfield:    .byte 0

; Cursor locations in instrument editor.
editor_instfield:       .byte 0         ; 0: instrument params, 1: wave table, 2: arpeggio table, 3: filter table
editor_instrow:         .byte 0         ; valid: $00..$0f
editor_instcol:         .byte 0         ; valid: $00..$01
editor_waveindex:       .byte 0
editor_arpindex:        .byte 0
editor_filterindex:     .byte 0
editor_filterblockflags: .byte 0
editor_filterblockbeg:  .byte 0
editor_filterblockend:  .byte 0

; Cursor location in config menu.
editor_configrow:       .byte 0         ; valid: $00..EDITOR_COLORSNUM-1
editor_configcolors:                    ; Buffer for editing colors.
        REPEAT EDITOR_COLORSNUM
        .byte 0
        REPEND

; Current octave for entering notes.
editor_currentoctave:   .byte 0
editor_currentoctavenote: .byte 0       ; =octave*12

; Current instrument when entering notes/using instrument editor.
editor_currentinst:     .byte 0

; This is added to the row position when something is entered into a pattern.
editor_editstep:        .byte 0

; Row that editor_gettrackrow and editor_puttrackrow work on.
editor_getputtrackrow:  .byte 0

; Buffer for current row data.
editor_tracknote:       .byte 0
editor_trackinst:       .byte 0
editor_trackeffect:     .byte 0
editor_trackeffectpar:  .byte 0

; Buffer for grab/drop effect.
editor_trackeffectbuf:          .byte 0
editor_trackeffectparbuf:       .byte 0

; Buffer for track undo.
editor_trackundochannel:        .byte 0 ; = channel last modified or $80.
editor_trackundobuffer:
        REPEAT 192
        .byte 0
        REPEND

; Buffer for track cut/copy/paste.
editor_trackcopybufferpos:      .byte 0
editor_trackcopybufferlen:      .byte 0
editor_trackcopybuffer:
        REPEAT 256
        .byte 0
        REPEND

; Buffer for instrument copy/paste.
editor_instcopybuffervalid:     .byte 0
editor_instnamecopybuffer:      .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0

; Temp variables for displaying orderlist and pattern.

display_chn:                    .byte 0
display_row:                    .byte 0
display_row3:                   .byte 0
display_x:                      .byte 0
display_y:                      .byte 0
display_height:                 .byte 0
display_index:                  .byte 0, 0
display_line:                   .byte 0
display_highlightline:          .byte 0
display_indexcolormask:         .byte 0
display_datacolormask:          .byte 0
display_selcolormask:           .byte 0
display_indexhighlight:         .byte 0 ; Highlight index in list?
display_indexhighlightfirst:    .byte 0
display_indexhighlightlast:     .byte 0
display_datahighlight:          .byte 0 ; Highlight data in list?
display_datahighlightfirst:     .byte 0
display_datahighlightlast:      .byte 0

; Used in replace instruments in tracks/patterns.
sm_replaceinstnum:      .byte 0
sm_replacewithinstnum:  .byte 0

; First and last track number used when reading/writing tracks
; and replacing instruments.
; Also first/last pattern numbers when replacing instruments
; and swapping track.
sm_firsttrack:  .byte 0
sm_lasttrack:   .byte 0

; Temporary variables used when finding out last track to save.
dm_savesongpattern:     .byte 0
dm_savesonglasttrack:   .byte 0

; Instrument number just being converted when importing 1.0x song.
dm_import10songinst:    .byte 0

; ======================================
; Data for the packer/relocator.
; ======================================

; Buffers during relocation.
packer_reloccurrentlobyte:      .byte 0
packer_reloccurrenthibyte:      .byte 0

packer_currentorder:            .byte 0

; List of used tracks.
packer_usedtracksnum:           .byte 0
packer_usedtracks:
        REPEAT MAX_TRACKS
        .byte $00
        REPEND

; Largest instrument number found in tracks.
packer_lastusedinstrument:      .byte 0

; Song start and orderlist lengths.
packer_songstartlistlength:     .byte 0
packer_orderlistlength:         .byte 0

; Lengths of instrument tables. These are the last elements that get saved.
packer_wavetablelength:         .byte 0
packer_arptablelength:          .byte 0
packer_filtertablelength:       .byte 0

; Relocate player to this page.
packer_playerdestpage:          .byte 0

; Relocate tracks to this address.
packer_tracksbase:              .word 0

; I/O data.
io_diskdevice:          .byte 0         ; Disk device number (8-31)
io_filenamelen:         .byte 0
io_filename:            .byte 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0
io_rlefile:             .byte 0

; Buffer for drive status.
io_drivestatus:
        REPEAT 40
        .byte $00
        REPEND

; ======================================
; Track row highlight sprite.
; ======================================

        org SPRITEHILIGHT
        .byte $ff,$ff,$ff       ; row  0        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $ff,$ff,$ff       ; row  1        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $ff,$ff,$ff       ; row  2        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $ff,$ff,$ff       ; row  3        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $ff,$ff,$ff       ; row  4        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $ff,$ff,$ff       ; row  5        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $ff,$ff,$ff       ; row  6        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $ff,$ff,$ff       ; row  7        xxxxxxxxxxxxxxxxxxxxxxxx
        .byte $00,$00,$00       ; row  8        ........................
        .byte $00,$00,$00       ; row  9        ........................
        .byte $00,$00,$00       ; row 10        ........................
        .byte $00,$00,$00       ; row 11        ........................
        .byte $00,$00,$00       ; row 12        ........................
        .byte $00,$00,$00       ; row 13        ........................
        .byte $00,$00,$00       ; row 14        ........................
        .byte $00,$00,$00       ; row 15        ........................
        .byte $00,$00,$00       ; row 16        ........................
        .byte $00,$00,$00       ; row 17        ........................
        .byte $00,$00,$00       ; row 18        ........................
        .byte $00,$00,$00       ; row 19        ........................
        .byte $00,$00,$00       ; row 20        ........................

; ======================================
; Cursor sprite.
; ======================================

        org SPRITECURSOR
        .byte $fc,$00,$00       ; row  0        xxxxxx..................
        .byte $84,$00,$00       ; row  1        x....x..................
        .byte $84,$00,$00       ; row  2        x....x..................
        .byte $84,$00,$00       ; row  3        x....x..................
        .byte $84,$00,$00       ; row  4        x....x..................
        .byte $84,$00,$00       ; row  5        x....x..................
        .byte $84,$00,$00       ; row  6        x....x..................
        .byte $84,$00,$00       ; row  7        x....x..................
        .byte $84,$00,$00       ; row  8        x....x..................
        .byte $fc,$00,$00       ; row  9        xxxxxx..................
        .byte $00,$00,$00       ; row 10        ........................
        .byte $00,$00,$00       ; row 11        ........................
        .byte $00,$00,$00       ; row 12        ........................
        .byte $00,$00,$00       ; row 13        ........................
        .byte $00,$00,$00       ; row 14        ........................
        .byte $00,$00,$00       ; row 15        ........................
        .byte $00,$00,$00       ; row 16        ........................
        .byte $00,$00,$00       ; row 17        ........................
        .byte $00,$00,$00       ; row 18        ........................
        .byte $00,$00,$00       ; row 19        ........................
        .byte $00,$00,$00       ; row 20        ........................

; ======================================
; Tune data.
; ======================================

        org ORDERLIST

        org SONGTITLE
        REPEAT SONGTITLELEN
        .byte $20
        REPEND

        org PATTERNS

        org INSTRUMENTS

        org INSTRUMENTNAMES
        REPEAT MAX_INSTRUMENTS*INSTRUMENTNAMELEN
        .byte $20
        REPEND

        org WAVETABLE

        org ARPEGGIOTABLE

        org TRACKS_BASE


; ======================================
; Relocatable player.
; This is compiled separately so that we can avoid
; creating tons of new unique names to avoid symbol conflicts
; with the editor's player.
; However, one label is needed: the end of the player's code.
; This label is VPLAYER_CODE_END and is read from vplayeri.s
; ======================================

        org VPLAYER

        incbin vplayer.bin

VPLAYEREND = *
VPLAYERSIZE = VPLAYEREND-VPLAYER

; ======================================
; List the number of bytes each 6510 instructions takes.
; All 3 byte long instructions contain absolute addresses,
; inside the player code & data area will have to be relocated.
; (Note: absolute indirect addressing is not used in the player.)
; ======================================

        org OPCODELIST

packer_instructionlist:
        include 6510.s

; ======================================
; Start of editor's player.
; ======================================

        org PLAYER

        include eplayer.s

; ======================================
; Buffer used when importing 1.0x songs.
; ======================================

        org INSTRUMENTBUFFER

; ======================================
; Help text (PETSCII codes).
; ======================================

        org HELPTEXT

        include help/help.s
