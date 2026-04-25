        * = $1000
        jmp init
        jmp play

init
        lda #$0F
        sta $D418
        lda #<v0pat
        sta $81
        lda #>v0pat
        sta $82
        lda #1
        sta $80
        lda #0
        sta $85
        sta $88
        sta $89
        sta $87
        sta $8A
        sta $B0
        lda #$FF
        sta $8B
        sta $8C
        sta $8F
        lda #<v1pat
        sta $91
        lda #>v1pat
        sta $92
        lda #1
        sta $90
        lda #0
        sta $95
        sta $98
        sta $99
        sta $97
        sta $9A
        sta $B1
        lda #$FF
        sta $9B
        sta $9C
        sta $9F
        lda #<v2pat
        sta $A1
        lda #>v2pat
        sta $A2
        lda #1
        sta $A0
        lda #0
        sta $A5
        sta $A8
        sta $A9
        sta $A7
        sta $AA
        sta $B2
        lda #$FF
        sta $AB
        sta $AC
        sta $AF
        rts

play
; --- Voice 1 ---
        dec $80
        beq v0new
        lda $80
        cmp #3
        bne v0nohr
        lda #0
        sta $D405
        sta $D406
v0nohr
        jmp v0wave

v0new
        ldy #0
        lda ($81),y
        cmp #$FF
        bne v0note
        jmp v0done
v0note
        sta $86
        iny
        lda ($81),y
        tax
        lda #0
v0m    clc
        adc #$06
        dex
        bne v0m
        sta $80
        iny
        lda ($81),y
        tax
        lda iad,x
        sta $D405
        lda isr,x
        sta $D406
        cpx $8F
        beq v0nopw
        lda $8F
        cmp #$FF
        beq v0pwini
        lda inoise,x
        bne v0tons
        lda $B0
        bne v0frns
        lda ipwslo,x
        ora ipwshi,x
        bne v0nopw
        beq v0pwini
v0frns
        lda $8D
        sta $85
        sta $D402
        lda $8E
        sta $88
        sta $D403
        lda ipwslo,x
        sta $87
        lda ipwshi,x
        sta $8A
        lda ipwmin,x
        sta $8B
        lda ipwmax,x
        sta $8C
        lda #0
        sta $B0
        jmp v0pwdone
v0tons
        lda $85
        sta $8D
        lda $88
        sta $8E
v0pwini
        lda inoise,x
        sta $B0
        lda ipwl,x
        sta $85
        sta $D402
        lda ipwh,x
        sta $88
        sta $D403
        lda #0
        sta $89
        lda ipwslo,x
        sta $87
        lda ipwshi,x
        sta $8A
        lda ipwmin,x
        sta $8B
        lda ipwmax,x
        sta $8C
        jmp v0pwdone
v0nopw
        lda ipwslo,x
        sta $87
        lda ipwshi,x
        sta $8A
        lda ipwmin,x
        sta $8B
        lda ipwmax,x
        sta $8C
v0pwdone
        stx $8F
        lda iwl,x
        sta $83
        lda iwh,x
        sta $84
        clc
        lda $81
        adc #3
        sta $81
        bcc v0wave
        inc $82

v0wave
        ldy #0
        lda ($83),y
        cmp #$FF
        bne v0wok
        iny
        lda ($83),y
        tax
        iny
        lda ($83),y
        sta $84
        stx $83
        ldy #0
        lda ($83),y
v0wok
        sta $D404
        iny
        lda ($83),y
        clc
        adc $86
        tax
        lda ftlo,x
        sta $D400
        lda fthi,x
        sta $D401
        clc
        lda $83
        adc #2
        sta $83
        bcc v0pw
        inc $84
v0pw
        lda $85
        sta $D402
        lda $88
        sta $D403
        lda $87
        ora $8A
        beq v0done
        lda $8C
        cmp #$FF
        bne v0pwbidi
        clc
        lda $85
        adc $87
        sta $85
        jmp v0done
v0pwbidi
        lda $89
        bne v0pwdn
        clc
        lda $85
        adc $87
        sta $85
        lda $88
        adc $8A
        sta $88
        cmp $8C
        bcc v0done
        ldx $8C
        stx $88
        lda #1
        sta $89
        jmp v0done
v0pwdn
        sec
        lda $85
        sbc $87
        sta $85
        lda $88
        sbc $8A
        sta $88
        cmp $8B
        beq v0pflp
        bcs v0done
v0pflp
        ldx $8B
        stx $88
        lda #0
        sta $89
v0done

; --- Voice 2 ---
        dec $90
        beq v1new
        lda $90
        cmp #3
        bne v1nohr
        lda #0
        sta $D40C
        sta $D40D
v1nohr
        jmp v1wave

v1new
        ldy #0
        lda ($91),y
        cmp #$FF
        bne v1note
        jmp v1done
v1note
        sta $96
        iny
        lda ($91),y
        tax
        lda #0
v1m    clc
        adc #$06
        dex
        bne v1m
        sta $90
        iny
        lda ($91),y
        tax
        lda iad,x
        sta $D40C
        lda isr,x
        sta $D40D
        cpx $9F
        beq v1nopw
        lda $9F
        cmp #$FF
        beq v1pwini
        lda inoise,x
        bne v1tons
        lda $B1
        bne v1frns
        lda ipwslo,x
        ora ipwshi,x
        bne v1nopw
        beq v1pwini
v1frns
        lda $9D
        sta $95
        sta $D409
        lda $9E
        sta $98
        sta $D40A
        lda ipwslo,x
        sta $97
        lda ipwshi,x
        sta $9A
        lda ipwmin,x
        sta $9B
        lda ipwmax,x
        sta $9C
        lda #0
        sta $B1
        jmp v1pwdone
v1tons
        lda $95
        sta $9D
        lda $98
        sta $9E
v1pwini
        lda inoise,x
        sta $B1
        lda ipwl,x
        sta $95
        sta $D409
        lda ipwh,x
        sta $98
        sta $D40A
        lda #0
        sta $99
        lda ipwslo,x
        sta $97
        lda ipwshi,x
        sta $9A
        lda ipwmin,x
        sta $9B
        lda ipwmax,x
        sta $9C
        jmp v1pwdone
v1nopw
        lda ipwslo,x
        sta $97
        lda ipwshi,x
        sta $9A
        lda ipwmin,x
        sta $9B
        lda ipwmax,x
        sta $9C
v1pwdone
        stx $9F
        lda iwl,x
        sta $93
        lda iwh,x
        sta $94
        clc
        lda $91
        adc #3
        sta $91
        bcc v1wave
        inc $92

v1wave
        ldy #0
        lda ($93),y
        cmp #$FF
        bne v1wok
        iny
        lda ($93),y
        tax
        iny
        lda ($93),y
        sta $94
        stx $93
        ldy #0
        lda ($93),y
v1wok
        sta $D40B
        iny
        lda ($93),y
        clc
        adc $96
        tax
        lda ftlo,x
        sta $D407
        lda fthi,x
        sta $D408
        clc
        lda $93
        adc #2
        sta $93
        bcc v1pw
        inc $94
v1pw
        lda $95
        sta $D409
        lda $98
        sta $D40A
        lda $97
        ora $9A
        beq v1done
        lda $9C
        cmp #$FF
        bne v1pwbidi
        clc
        lda $95
        adc $97
        sta $95
        jmp v1done
v1pwbidi
        lda $99
        bne v1pwdn
        clc
        lda $95
        adc $97
        sta $95
        lda $98
        adc $9A
        sta $98
        cmp $9C
        bcc v1done
        ldx $9C
        stx $98
        lda #1
        sta $99
        jmp v1done
v1pwdn
        sec
        lda $95
        sbc $97
        sta $95
        lda $98
        sbc $9A
        sta $98
        cmp $9B
        beq v1pflp
        bcs v1done
v1pflp
        ldx $9B
        stx $98
        lda #0
        sta $99
v1done

; --- Voice 3 ---
        dec $A0
        beq v2new
        lda $A0
        cmp #3
        bne v2nohr
        lda #0
        sta $D413
        sta $D414
v2nohr
        jmp v2wave

v2new
        ldy #0
        lda ($A1),y
        cmp #$FF
        bne v2note
        jmp v2done
v2note
        sta $A6
        iny
        lda ($A1),y
        tax
        lda #0
v2m    clc
        adc #$06
        dex
        bne v2m
        sta $A0
        iny
        lda ($A1),y
        tax
        lda iad,x
        sta $D413
        lda isr,x
        sta $D414
        cpx $AF
        beq v2nopw
        lda $AF
        cmp #$FF
        beq v2pwini
        lda inoise,x
        bne v2tons
        lda $B2
        bne v2frns
        lda ipwslo,x
        ora ipwshi,x
        bne v2nopw
        beq v2pwini
v2frns
        lda $AD
        sta $A5
        sta $D410
        lda $AE
        sta $A8
        sta $D411
        lda ipwslo,x
        sta $A7
        lda ipwshi,x
        sta $AA
        lda ipwmin,x
        sta $AB
        lda ipwmax,x
        sta $AC
        lda #0
        sta $B2
        jmp v2pwdone
v2tons
        lda $A5
        sta $AD
        lda $A8
        sta $AE
v2pwini
        lda inoise,x
        sta $B2
        lda ipwl,x
        sta $A5
        sta $D410
        lda ipwh,x
        sta $A8
        sta $D411
        lda #0
        sta $A9
        lda ipwslo,x
        sta $A7
        lda ipwshi,x
        sta $AA
        lda ipwmin,x
        sta $AB
        lda ipwmax,x
        sta $AC
        jmp v2pwdone
v2nopw
        lda ipwslo,x
        sta $A7
        lda ipwshi,x
        sta $AA
        lda ipwmin,x
        sta $AB
        lda ipwmax,x
        sta $AC
v2pwdone
        stx $AF
        lda iwl,x
        sta $A3
        lda iwh,x
        sta $A4
        clc
        lda $A1
        adc #3
        sta $A1
        bcc v2wave
        inc $A2

v2wave
        ldy #0
        lda ($A3),y
        cmp #$FF
        bne v2wok
        iny
        lda ($A3),y
        tax
        iny
        lda ($A3),y
        sta $A4
        stx $A3
        ldy #0
        lda ($A3),y
v2wok
        sta $D412
        iny
        lda ($A3),y
        clc
        adc $A6
        tax
        lda ftlo,x
        sta $D40E
        lda fthi,x
        sta $D40F
        clc
        lda $A3
        adc #2
        sta $A3
        bcc v2pw
        inc $A4
v2pw
        lda $A5
        sta $D410
        lda $A8
        sta $D411
        lda $A7
        ora $AA
        beq v2done
        lda $AC
        cmp #$FF
        bne v2pwbidi
        clc
        lda $A5
        adc $A7
        sta $A5
        jmp v2done
v2pwbidi
        lda $A9
        bne v2pwdn
        clc
        lda $A5
        adc $A7
        sta $A5
        lda $A8
        adc $AA
        sta $A8
        cmp $AC
        bcc v2done
        ldx $AC
        stx $A8
        lda #1
        sta $A9
        jmp v2done
v2pwdn
        sec
        lda $A5
        sbc $A7
        sta $A5
        lda $A8
        sbc $AA
        sta $A8
        cmp $AB
        beq v2pflp
        bcs v2done
v2pflp
        ldx $AB
        stx $A8
        lda #0
        sta $A9
v2done

        rts

ftlo
        .byte $00,$D0,$BD,$D0,$03,$05,$13,$28,$2A,$42,$A9,$D0,$E0,$5A,$9B,$D0
        .byte $E2,$05,$7B,$D0,$27,$85,$D0,$06,$0C,$0E,$51,$C1,$D0,$37,$B4,$D0
        .byte $37,$C4,$D0,$57,$D0,$6E,$D0,$6E,$D0,$6E,$D0,$6E,$0F,$6E,$82,$00
        .byte $10,$21,$25,$6E,$11,$68,$6E,$00,$88,$AF,$EB,$2C,$7C,$CC,$1C,$39
        .byte $6C,$BC,$0C,$5C,$AC,$FC,$4C,$9C,$EC,$13,$3C,$8C,$DC,$2C,$7C,$A1
        .byte $CC,$D5,$09,$1C,$3D,$6C,$BC,$0C,$46,$5C,$7D,$AC,$B4,$EB,$FC,$32
        .byte $4C,$70,$9C,$AE,$EC,$04,$2A,$3C,$68,$8C,$A6,$DC,$E4,$22,$2C,$60
        .byte $7C,$9E,$CC,$DC,$04,$1A,$1C,$2C,$54,$58,$6C,$7C,$96,$A4,$BC,$CC
        .byte $F4,$0C,$1C,$44,$5C,$6C,$94,$AC,$D0,$F8,$FC,$11,$20,$48,$4C,$52
        .byte $70,$93,$98,$9C,$C0,$E8,$EC,$10,$38,$3C,$60,$88,$8C,$DC,$22,$68
        .byte $AE,$10,$38,$59,$60,$88,$A2,$B0,$D8,$EB,$00,$28,$50,$78,$A0,$C8
        .byte $5E,$D6,$29,$7C,$CF,$DE,$2C,$72,$7A,$C8,$CA,$16,$22,$64,$7A,$81
        .byte $B2,$00,$4E,$9C,$EA,$38,$95,$F2,$4F,$26,$89,$EC,$4F,$42,$AB,$14
        .byte $7D,$8C,$08,$41,$15,$41,$B8,$15,$41,$81,$A0,$20,$BC,$AC,$E4,$70
        .byte $4C,$84,$18,$10,$70,$40,$58,$E0,$30,$2E
fthi
        .byte $00,$01,$02,$02,$03,$03,$03,$03,$03,$03,$03,$03,$03,$04,$04,$04
        .byte $04,$05,$05,$05,$06,$06,$06,$07,$07,$07,$07,$07,$07,$08,$08,$08
        .byte $09,$09,$09,$0A,$0A,$0B,$0B,$0C,$0C,$0D,$0D,$0E,$0F,$0F,$0F,$10
        .byte $10,$10,$10,$10,$11,$11,$12,$13,$13,$14,$15,$16,$16,$16,$17,$17
        .byte $17,$17,$18,$18,$18,$18,$19,$19,$19,$1A,$1A,$1A,$1A,$1B,$1B,$1B
        .byte $1B,$1B,$1C,$1C,$1C,$1C,$1C,$1D,$1D,$1D,$1D,$1D,$1D,$1D,$1D,$1E
        .byte $1E,$1E,$1E,$1E,$1E,$1F,$1F,$1F,$1F,$1F,$1F,$1F,$1F,$20,$20,$20
        .byte $20,$20,$20,$20,$21,$21,$21,$21,$21,$21,$21,$21,$21,$21,$21,$21
        .byte $21,$22,$22,$22,$22,$22,$22,$22,$22,$22,$22,$23,$23,$23,$23,$23
        .byte $23,$23,$23,$23,$23,$23,$23,$24,$24,$24,$24,$24,$24,$24,$25,$25
        .byte $25,$27,$27,$27,$27,$27,$27,$27,$27,$27,$28,$28,$28,$28,$28,$28
        .byte $29,$2B,$2C,$2C,$2C,$2D,$2E,$2E,$2E,$2E,$2E,$2F,$2F,$2F,$2F,$2F
        .byte $2F,$30,$30,$30,$30,$31,$31,$31,$32,$34,$34,$34,$35,$37,$37,$38
        .byte $38,$3A,$3E,$3E,$41,$41,$41,$43,$43,$43,$45,$4E,$52,$57,$5C,$62
        .byte $68,$6E,$75,$7C,$93,$9C,$AF,$C4,$EA,$FD

iad
        .byte $0D,$0D,$06,$06,$06,$06,$0D,$0D,$0D,$0A,$29,$29,$29,$29,$29,$29,$29,$09,$29,$29,$29,$29,$29,$29,$29,$09,$09,$09,$29,$29,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$05,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$38,$09,$38,$38,$38,$05,$05,$05,$05,$05,$38,$38,$05,$0F,$0F,$06,$06,$06,$06,$06,$06,$06,$06,$06,$0D,$0D,$0D,$0D,$06,$06,$06,$06,$0D,$0D,$06,$06,$06,$0D,$0D,$0D,$0D,$0D,$0D,$05,$05,$05,$05,$05,$0D,$05,$05,$09,$09,$0A,$09,$09,$05,$05,$0A,$05
isr
        .byte $FB,$FB,$4B,$4B,$4B,$4B,$FB,$FB,$FB,$09,$5F,$5F,$5F,$5F,$5F,$5F,$5F,$0A,$5F,$5F,$5F,$5F,$5F,$5F,$5F,$0A,$0A,$0A,$5F,$5F,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$A9,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$7A,$0A,$7A,$7A,$7A,$A9,$A9,$A9,$A9,$A9,$7A,$7A,$A9,$C4,$C4,$4B,$4B,$4B,$4B,$4B,$4B,$4B,$4B,$4B,$FB,$FB,$FB,$FB,$4B,$4B,$4B,$4B,$FB,$FB,$4B,$4B,$4B,$FB,$FB,$FB,$FB,$FB,$FB,$A9,$A9,$A9,$A9,$A9,$FB,$A9,$A9,$9F,$9F,$09,$9F,$9F,$A9,$A9,$09,$A9
ipwl
        .byte $80,$80,$80,$80,$80,$80,$80,$80,$80,$00,$00,$60,$C0,$60,$80,$60,$E0,$00,$C0,$A0,$A0,$00,$60,$C0,$60,$00,$00,$00,$C0,$C0,$80,$8A,$A0,$AA,$A0,$AA,$C0,$D6,$F6,$00,$82,$8C,$AC,$02,$00,$A0,$00,$E0,$20,$C0,$A0,$80,$C0,$E0,$E0,$C0,$00,$80,$80,$A0,$00,$40,$E0,$40,$DC,$54,$7C,$F6,$5E,$20,$E0,$86,$00,$00,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$80,$DC,$54,$7C,$F6,$5E,$80,$2C,$86,$80,$F6,$00,$64,$56,$DC,$9A,$00,$86
ipwh
        .byte $01,$01,$01,$01,$01,$01,$01,$01,$01,$02,$09,$0D,$0A,$0D,$0C,$0D,$09,$08,$0A,$0B,$0B,$09,$0D,$0A,$0D,$08,$08,$08,$0A,$0A,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08,$08,$03,$0A,$0A,$09,$0B,$0C,$0D,$0B,$0A,$0A,$0B,$0A,$0D,$0D,$0C,$08,$08,$0A,$08,$08,$08,$08,$08,$08,$09,$0A,$08,$02,$02,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$01,$08,$08,$08,$08,$08,$01,$08,$08,$01,$01,$02,$01,$01,$08,$08,$02,$08
inoise
        .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$01,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$01,$00,$00,$00,$00,$01,$00
ipwslo
        .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$E0,$E0,$E0,$E0,$E0,$E0,$00,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$00,$00,$00,$E0,$E0,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$02,$00,$20,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$E0,$00,$E0,$E0,$E0,$06,$04,$06,$06,$04,$E0,$E0,$06,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$06,$04,$06,$06,$04,$00,$04,$06,$16,$16,$00,$16,$16,$06,$06,$22,$06
ipwshi
        .byte $00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$0F,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$00,$07,$00
ipwmin
        .byte $FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$08,$08,$08,$08,$0A,$08,$FF,$08,$08,$08,$09,$08,$08,$08,$FF,$FF,$FF,$08,$08,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$00,$08,$08,$09,$0B,$08,$0A,$08,$08,$08,$08,$08,$08,$08,$08,$FF,$08,$08,$08,$FF,$FF,$FF,$FF,$FF,$08,$08,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$01,$FF
ipwmax
        .byte $FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$0E,$0E,$0E,$0D,$0E,$0E,$FF,$0E,$0E,$0B,$0E,$0E,$0E,$0E,$FF,$FF,$FF,$0A,$0E,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$0F,$0A,$0E,$0E,$0E,$0D,$0E,$0E,$0E,$0E,$0E,$0E,$0E,$0E,$0E,$FF,$0E,$0E,$0E,$FF,$FF,$FF,$FF,$FF,$0B,$0A,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$FF,$08,$FF
iwl
        .byte <wt0,<wt1,<wt2,<wt3,<wt4,<wt5,<wt6,<wt7,<wt8,<wt9,<wt10,<wt11,<wt12,<wt13,<wt14,<wt15,<wt16,<wt17,<wt18,<wt19,<wt20,<wt21,<wt22,<wt23,<wt24,<wt25,<wt26,<wt27,<wt28,<wt29,<wt30,<wt31,<wt32,<wt33,<wt34,<wt35,<wt36,<wt37,<wt38,<wt39,<wt40,<wt41,<wt42,<wt43,<wt44,<wt45,<wt46,<wt47,<wt48,<wt49,<wt50,<wt51,<wt52,<wt53,<wt54,<wt55,<wt56,<wt57,<wt58,<wt59,<wt60,<wt61,<wt62,<wt63,<wt64,<wt65,<wt66,<wt67,<wt68,<wt69,<wt70,<wt71,<wt72,<wt73,<wt74,<wt75,<wt76,<wt77,<wt78,<wt79,<wt80,<wt81,<wt82,<wt83,<wt84,<wt85,<wt86,<wt87,<wt88,<wt89,<wt90,<wt91,<wt92,<wt93,<wt94,<wt95,<wt96,<wt97,<wt98,<wt99,<wt100,<wt101,<wt102,<wt103,<wt104,<wt105,<wt106,<wt107,<wt108,<wt109,<wt110,<wt111,<wt112,<wt113,<wt114,<wt115,<wt116,<wt117,<wt118
iwh
        .byte >wt0,>wt1,>wt2,>wt3,>wt4,>wt5,>wt6,>wt7,>wt8,>wt9,>wt10,>wt11,>wt12,>wt13,>wt14,>wt15,>wt16,>wt17,>wt18,>wt19,>wt20,>wt21,>wt22,>wt23,>wt24,>wt25,>wt26,>wt27,>wt28,>wt29,>wt30,>wt31,>wt32,>wt33,>wt34,>wt35,>wt36,>wt37,>wt38,>wt39,>wt40,>wt41,>wt42,>wt43,>wt44,>wt45,>wt46,>wt47,>wt48,>wt49,>wt50,>wt51,>wt52,>wt53,>wt54,>wt55,>wt56,>wt57,>wt58,>wt59,>wt60,>wt61,>wt62,>wt63,>wt64,>wt65,>wt66,>wt67,>wt68,>wt69,>wt70,>wt71,>wt72,>wt73,>wt74,>wt75,>wt76,>wt77,>wt78,>wt79,>wt80,>wt81,>wt82,>wt83,>wt84,>wt85,>wt86,>wt87,>wt88,>wt89,>wt90,>wt91,>wt92,>wt93,>wt94,>wt95,>wt96,>wt97,>wt98,>wt99,>wt100,>wt101,>wt102,>wt103,>wt104,>wt105,>wt106,>wt107,>wt108,>wt109,>wt110,>wt111,>wt112,>wt113,>wt114,>wt115,>wt116,>wt117,>wt118

wt0
wt0b0
        .byte $15,$00
wt0b2
        .byte $80,$1E
wt0b4
        .byte $80,$00
wt0b6
        .byte $14,$1E
wt0b8
        .byte $14,$00
wt0b10
        .byte $14,$1E
wt0b12
        .byte $14,$00
wt0b14
        .byte $14,$1F
        .byte $FF,<wt0b12,>wt0b12
wt1
wt1b0
        .byte $15,$00
wt1b2
        .byte $80,$06
wt1b4
        .byte $80,$00
wt1b6
        .byte $14,$06
wt1b8
        .byte $14,$00
        .byte $FF,<wt1b6,>wt1b6
wt2
wt2b0
        .byte $41,$00
wt2b2
        .byte $80,$79
wt2b4
        .byte $80,$00
wt2b6
        .byte $40,$79
wt2b8
        .byte $40,$00
        .byte $FF,<wt2b6,>wt2b6
wt3
wt3b0
        .byte $41,$00
wt3b2
        .byte $80,$80
wt3b4
        .byte $80,$00
wt3b6
        .byte $40,$80
wt3b8
        .byte $40,$00
        .byte $FF,<wt3b6,>wt3b6
wt4
wt4b0
        .byte $41,$00
wt4b2
        .byte $80,$79
wt4b4
        .byte $80,$00
wt4b6
        .byte $40,$79
wt4b8
        .byte $40,$00
wt4b10
        .byte $40,$79
        .byte $FF,<wt4b10,>wt4b10
wt5
wt5b0
        .byte $41,$00
wt5b2
        .byte $80,$80
wt5b4
        .byte $80,$00
wt5b6
        .byte $40,$80
wt5b8
        .byte $40,$00
wt5b10
        .byte $40,$80
        .byte $FF,<wt5b10,>wt5b10
wt6
wt6b0
        .byte $15,$00
wt6b2
        .byte $80,$4C
wt6b4
        .byte $80,$00
wt6b6
        .byte $14,$4C
wt6b8
        .byte $14,$00
        .byte $FF,<wt6b6,>wt6b6
wt7
wt7b0
        .byte $15,$00
wt7b2
        .byte $80,$21
wt7b4
        .byte $80,$00
wt7b6
        .byte $14,$21
wt7b8
        .byte $14,$00
wt7b10
        .byte $14,$21
wt7b12
        .byte $14,$00
wt7b14
        .byte $14,$22
        .byte $FF,<wt7b12,>wt7b12
wt8
wt8b0
        .byte $15,$00
wt8b2
        .byte $80,$49
wt8b4
        .byte $80,$00
wt8b6
        .byte $14,$49
wt8b8
        .byte $14,$00
        .byte $FF,<wt8b6,>wt8b6
wt9
wt9b0
        .byte $81,$00
wt9b2
        .byte $80,$69
wt9b4
        .byte $80,$00
wt9b6
        .byte $80,$69
        .byte $FF,<wt9b4,>wt9b4
wt10
wt10b0
        .byte $41,$00
wt10b2
        .byte $41,$00
wt10b4
        .byte $41,$00
wt10b6
        .byte $40,$00
        .byte $FF,<wt10b6,>wt10b6
wt11
wt11b0
        .byte $41,$00
wt11b2
        .byte $41,$00
wt11b4
        .byte $41,$00
wt11b6
        .byte $41,$00
wt11b8
        .byte $41,$00
wt11b10
        .byte $41,$00
wt11b12
        .byte $41,$00
wt11b14
        .byte $41,$00
wt11b16
        .byte $41,$00
wt11b18
        .byte $40,$00
wt11b20
        .byte $40,$00
wt11b22
        .byte $40,$00
        .byte $FF,<wt11b22,>wt11b22
wt12
wt12b0
        .byte $41,$00
wt12b2
        .byte $41,$02
wt12b4
        .byte $41,$04
wt12b6
        .byte $41,$05
wt12b8
        .byte $41,$05
wt12b10
        .byte $41,$04
wt12b12
        .byte $41,$02
wt12b14
        .byte $41,$00
wt12b16
        .byte $41,$00
wt12b18
        .byte $41,$02
wt12b20
        .byte $41,$04
wt12b22
        .byte $41,$05
wt12b24
        .byte $41,$05
wt12b26
        .byte $41,$04
wt12b28
        .byte $41,$02
wt12b30
        .byte $41,$00
wt12b32
        .byte $41,$00
wt12b34
        .byte $41,$02
wt12b36
        .byte $41,$04
wt12b38
        .byte $41,$05
wt12b40
        .byte $41,$05
wt12b42
        .byte $40,$04
wt12b44
        .byte $40,$02
wt12b46
        .byte $40,$00
        .byte $FF,<wt12b46,>wt12b46
wt13
wt13b0
        .byte $41,$00
wt13b2
        .byte $41,$00
wt13b4
        .byte $41,$00
wt13b6
        .byte $41,$00
wt13b8
        .byte $41,$00
wt13b10
        .byte $41,$00
wt13b12
        .byte $41,$00
wt13b14
        .byte $41,$00
wt13b16
        .byte $41,$00
wt13b18
        .byte $41,$00
wt13b20
        .byte $41,$00
wt13b22
        .byte $41,$00
wt13b24
        .byte $41,$00
wt13b26
        .byte $41,$00
wt13b28
        .byte $41,$00
wt13b30
        .byte $40,$00
wt13b32
        .byte $40,$00
wt13b34
        .byte $40,$00
        .byte $FF,<wt13b34,>wt13b34
wt14
wt14b0
        .byte $41,$00
wt14b2
        .byte $41,$00
wt14b4
        .byte $41,$00
wt14b6
        .byte $41,$00
wt14b8
        .byte $41,$00
wt14b10
        .byte $41,$00
wt14b12
        .byte $41,$00
wt14b14
        .byte $41,$00
wt14b16
        .byte $41,$00
wt14b18
        .byte $40,$00
wt14b20
        .byte $40,$00
wt14b22
        .byte $40,$00
        .byte $FF,<wt14b22,>wt14b22
wt15
wt15b0
        .byte $41,$00
wt15b2
        .byte $41,$00
wt15b4
        .byte $41,$00
wt15b6
        .byte $40,$00
        .byte $FF,<wt15b6,>wt15b6
wt16
wt16b0
        .byte $41,$00
wt16b2
        .byte $41,$01
wt16b4
        .byte $41,$02
wt16b6
        .byte $41,$03
wt16b8
        .byte $41,$03
wt16b10
        .byte $41,$02
wt16b12
        .byte $41,$01
wt16b14
        .byte $41,$00
wt16b16
        .byte $41,$00
wt16b18
        .byte $41,$01
wt16b20
        .byte $41,$02
wt16b22
        .byte $41,$03
wt16b24
        .byte $41,$03
wt16b26
        .byte $41,$02
wt16b28
        .byte $41,$01
wt16b30
        .byte $41,$00
wt16b32
        .byte $41,$00
wt16b34
        .byte $41,$01
wt16b36
        .byte $41,$02
wt16b38
        .byte $41,$03
wt16b40
        .byte $41,$03
wt16b42
        .byte $40,$02
wt16b44
        .byte $40,$01
wt16b46
        .byte $40,$00
        .byte $FF,<wt16b46,>wt16b46
wt17
wt17b0
        .byte $41,$00
wt17b2
        .byte $80,$00
wt17b4
        .byte $80,$00
wt17b6
        .byte $40,$00
wt17b8
        .byte $40,$FE
wt17b10
        .byte $40,$FC
wt17b12
        .byte $40,$FA
wt17b14
        .byte $40,$F8
wt17b16
        .byte $40,$F5
wt17b18
        .byte $40,$F2
wt17b20
        .byte $40,$EC
wt17b22
        .byte $40,$E9
wt17b24
        .byte $40,$E5
wt17b26
        .byte $40,$E1
wt17b28
        .byte $40,$D9
wt17b30
        .byte $40,$D7
wt17b32
        .byte $40,$D7
wt17b34
        .byte $40,$D7
wt17b36
        .byte $40,$D7
wt17b38
        .byte $40,$D7
wt17b40
        .byte $40,$D7
wt17b42
        .byte $40,$D7
wt17b44
        .byte $40,$D7
wt17b46
        .byte $40,$D7
        .byte $FF,<wt17b46,>wt17b46
wt18
wt18b0
        .byte $41,$00
wt18b2
        .byte $41,$03
wt18b4
        .byte $41,$05
wt18b6
        .byte $41,$07
wt18b8
        .byte $41,$07
wt18b10
        .byte $41,$05
wt18b12
        .byte $41,$03
wt18b14
        .byte $41,$00
wt18b16
        .byte $41,$00
wt18b18
        .byte $41,$03
wt18b20
        .byte $41,$05
wt18b22
        .byte $41,$07
wt18b24
        .byte $41,$07
wt18b26
        .byte $41,$05
wt18b28
        .byte $41,$03
wt18b30
        .byte $41,$00
wt18b32
        .byte $41,$00
wt18b34
        .byte $41,$03
wt18b36
        .byte $41,$05
wt18b38
        .byte $41,$07
wt18b40
        .byte $41,$07
wt18b42
        .byte $40,$05
wt18b44
        .byte $40,$03
wt18b46
        .byte $40,$00
        .byte $FF,<wt18b46,>wt18b46
wt19
wt19b0
        .byte $41,$00
wt19b2
        .byte $41,$01
wt19b4
        .byte $41,$02
wt19b6
        .byte $41,$03
wt19b8
        .byte $41,$03
wt19b10
        .byte $41,$02
wt19b12
        .byte $41,$01
wt19b14
        .byte $41,$00
wt19b16
        .byte $41,$00
wt19b18
        .byte $41,$01
wt19b20
        .byte $41,$02
wt19b22
        .byte $41,$03
wt19b24
        .byte $41,$03
wt19b26
        .byte $41,$02
wt19b28
        .byte $41,$01
wt19b30
        .byte $41,$00
wt19b32
        .byte $41,$00
wt19b34
        .byte $41,$01
wt19b36
        .byte $41,$02
wt19b38
        .byte $41,$03
wt19b40
        .byte $41,$03
wt19b42
        .byte $40,$02
wt19b44
        .byte $40,$01
wt19b46
        .byte $40,$00
wt19b48
        .byte $40,$00
wt19b50
        .byte $40,$00
wt19b52
        .byte $40,$00
wt19b54
        .byte $40,$00
wt19b56
        .byte $40,$00
wt19b58
        .byte $40,$00
        .byte $FF,<wt19b58,>wt19b58
wt20
wt20b0
        .byte $41,$00
wt20b2
        .byte $41,$00
wt20b4
        .byte $41,$00
wt20b6
        .byte $40,$00
        .byte $FF,<wt20b6,>wt20b6
wt21
wt21b0
        .byte $41,$00
wt21b2
        .byte $41,$00
wt21b4
        .byte $41,$00
wt21b6
        .byte $41,$00
wt21b8
        .byte $41,$00
wt21b10
        .byte $41,$00
wt21b12
        .byte $41,$00
wt21b14
        .byte $41,$00
wt21b16
        .byte $41,$00
wt21b18
        .byte $40,$00
wt21b20
        .byte $40,$00
wt21b22
        .byte $40,$00
        .byte $FF,<wt21b22,>wt21b22
wt22
wt22b0
        .byte $41,$00
wt22b2
        .byte $41,$02
wt22b4
        .byte $41,$06
wt22b6
        .byte $41,$09
wt22b8
        .byte $41,$09
wt22b10
        .byte $41,$06
wt22b12
        .byte $41,$02
wt22b14
        .byte $41,$00
wt22b16
        .byte $41,$00
wt22b18
        .byte $41,$02
wt22b20
        .byte $41,$06
wt22b22
        .byte $41,$09
wt22b24
        .byte $41,$09
wt22b26
        .byte $41,$06
wt22b28
        .byte $41,$02
wt22b30
        .byte $41,$00
wt22b32
        .byte $41,$00
wt22b34
        .byte $41,$02
wt22b36
        .byte $41,$06
wt22b38
        .byte $41,$09
wt22b40
        .byte $41,$09
wt22b42
        .byte $40,$06
wt22b44
        .byte $40,$02
wt22b46
        .byte $40,$00
        .byte $FF,<wt22b46,>wt22b46
wt23
wt23b0
        .byte $41,$00
wt23b2
        .byte $41,$03
wt23b4
        .byte $41,$07
wt23b6
        .byte $41,$09
wt23b8
        .byte $41,$09
wt23b10
        .byte $41,$07
wt23b12
        .byte $41,$03
wt23b14
        .byte $41,$00
wt23b16
        .byte $41,$00
wt23b18
        .byte $41,$03
wt23b20
        .byte $41,$07
wt23b22
        .byte $41,$09
wt23b24
        .byte $41,$09
wt23b26
        .byte $41,$07
wt23b28
        .byte $41,$03
wt23b30
        .byte $41,$00
wt23b32
        .byte $41,$00
wt23b34
        .byte $41,$03
wt23b36
        .byte $41,$07
wt23b38
        .byte $41,$09
wt23b40
        .byte $41,$09
wt23b42
        .byte $40,$07
wt23b44
        .byte $40,$03
wt23b46
        .byte $40,$00
        .byte $FF,<wt23b46,>wt23b46
wt24
wt24b0
        .byte $41,$00
wt24b2
        .byte $41,$02
wt24b4
        .byte $41,$05
wt24b6
        .byte $41,$08
wt24b8
        .byte $41,$08
wt24b10
        .byte $41,$05
wt24b12
        .byte $41,$02
wt24b14
        .byte $41,$00
wt24b16
        .byte $41,$00
wt24b18
        .byte $41,$02
wt24b20
        .byte $41,$05
wt24b22
        .byte $41,$08
wt24b24
        .byte $41,$08
wt24b26
        .byte $41,$05
wt24b28
        .byte $41,$02
wt24b30
        .byte $41,$00
wt24b32
        .byte $41,$00
wt24b34
        .byte $41,$02
wt24b36
        .byte $41,$05
wt24b38
        .byte $41,$08
wt24b40
        .byte $41,$08
wt24b42
        .byte $40,$05
wt24b44
        .byte $40,$02
wt24b46
        .byte $40,$00
        .byte $FF,<wt24b46,>wt24b46
wt25
wt25b0
        .byte $41,$00
wt25b2
        .byte $80,$00
wt25b4
        .byte $80,$00
wt25b6
        .byte $40,$00
wt25b8
        .byte $40,$FA
wt25b10
        .byte $40,$F8
wt25b12
        .byte $40,$F6
wt25b14
        .byte $40,$F4
wt25b16
        .byte $40,$F2
wt25b18
        .byte $40,$F2
wt25b20
        .byte $40,$F2
wt25b22
        .byte $40,$F2
        .byte $FF,<wt25b22,>wt25b22
wt26
wt26b0
        .byte $41,$00
wt26b2
        .byte $80,$00
wt26b4
        .byte $80,$00
wt26b6
        .byte $40,$00
        .byte $FF,<wt26b6,>wt26b6
wt27
wt27b0
        .byte $41,$00
wt27b2
        .byte $80,$00
wt27b4
        .byte $80,$00
wt27b6
        .byte $40,$00
wt27b8
        .byte $40,$FE
wt27b10
        .byte $40,$FC
wt27b12
        .byte $40,$FA
wt27b14
        .byte $40,$F8
wt27b16
        .byte $40,$F5
wt27b18
        .byte $40,$F5
wt27b20
        .byte $40,$F5
wt27b22
        .byte $40,$F5
        .byte $FF,<wt27b22,>wt27b22
wt28
wt28b0
        .byte $41,$00
wt28b2
        .byte $41,$00
wt28b4
        .byte $41,$00
wt28b6
        .byte $40,$00
        .byte $FF,<wt28b6,>wt28b6
wt29
wt29b0
        .byte $41,$00
wt29b2
        .byte $41,$02
wt29b4
        .byte $41,$03
wt29b6
        .byte $41,$05
wt29b8
        .byte $41,$05
wt29b10
        .byte $41,$03
wt29b12
        .byte $41,$02
wt29b14
        .byte $41,$00
wt29b16
        .byte $41,$00
wt29b18
        .byte $41,$02
wt29b20
        .byte $41,$03
wt29b22
        .byte $41,$05
wt29b24
        .byte $41,$05
wt29b26
        .byte $41,$03
wt29b28
        .byte $41,$02
wt29b30
        .byte $41,$00
wt29b32
        .byte $41,$00
wt29b34
        .byte $41,$02
wt29b36
        .byte $41,$03
wt29b38
        .byte $41,$05
wt29b40
        .byte $41,$05
wt29b42
        .byte $40,$03
wt29b44
        .byte $40,$02
wt29b46
        .byte $40,$00
        .byte $FF,<wt29b46,>wt29b46
wt30
wt30b0
        .byte $41,$00
wt30b2
        .byte $80,$52
wt30b4
        .byte $80,$00
wt30b6
        .byte $40,$52
wt30b8
        .byte $40,$00
wt30b10
        .byte $40,$52
        .byte $FF,<wt30b10,>wt30b10
wt31
wt31b0
        .byte $41,$00
wt31b2
        .byte $80,$63
wt31b4
        .byte $80,$00
wt31b6
        .byte $40,$63
wt31b8
        .byte $40,$00
        .byte $FF,<wt31b6,>wt31b6
wt32
wt32b0
        .byte $41,$00
wt32b2
        .byte $80,$6D
wt32b4
        .byte $80,$00
wt32b6
        .byte $40,$6D
wt32b8
        .byte $40,$00
wt32b10
        .byte $40,$6D
        .byte $FF,<wt32b10,>wt32b10
wt33
wt33b0
        .byte $41,$00
wt33b2
        .byte $80,$79
wt33b4
        .byte $80,$00
wt33b6
        .byte $40,$79
wt33b8
        .byte $40,$00
        .byte $FF,<wt33b6,>wt33b6
wt34
wt34b0
        .byte $41,$00
wt34b2
        .byte $80,$79
wt34b4
        .byte $80,$00
wt34b6
        .byte $40,$79
wt34b8
        .byte $40,$00
wt34b10
        .byte $40,$79
        .byte $FF,<wt34b10,>wt34b10
wt35
wt35b0
        .byte $41,$00
wt35b2
        .byte $80,$27
wt35b4
        .byte $80,$00
wt35b6
        .byte $40,$27
wt35b8
        .byte $40,$00
        .byte $FF,<wt35b6,>wt35b6
wt36
wt36b0
        .byte $41,$00
wt36b2
        .byte $80,$2C
wt36b4
        .byte $80,$00
wt36b6
        .byte $40,$2C
wt36b8
        .byte $40,$00
        .byte $FF,<wt36b6,>wt36b6
wt37
wt37b0
        .byte $41,$00
wt37b2
        .byte $80,$27
wt37b4
        .byte $80,$00
wt37b6
        .byte $40,$27
wt37b8
        .byte $40,$00
wt37b10
        .byte $40,$27
        .byte $FF,<wt37b10,>wt37b10
wt38
wt38b0
        .byte $41,$00
wt38b2
        .byte $80,$2C
wt38b4
        .byte $80,$00
wt38b6
        .byte $40,$2C
wt38b8
        .byte $40,$00
wt38b10
        .byte $40,$2C
        .byte $FF,<wt38b10,>wt38b10
wt39
wt39b0
        .byte $41,$00
wt39b2
        .byte $80,$3A
wt39b4
        .byte $80,$00
wt39b6
        .byte $40,$3A
wt39b8
        .byte $40,$00
        .byte $FF,<wt39b6,>wt39b6
wt40
wt40b0
        .byte $41,$00
wt40b2
        .byte $80,$63
wt40b4
        .byte $80,$00
wt40b6
        .byte $40,$63
wt40b8
        .byte $40,$00
wt40b10
        .byte $40,$63
        .byte $FF,<wt40b10,>wt40b10
wt41
wt41b0
        .byte $41,$00
wt41b2
        .byte $80,$6D
wt41b4
        .byte $80,$00
wt41b6
        .byte $40,$6D
wt41b8
        .byte $40,$00
        .byte $FF,<wt41b6,>wt41b6
wt42
wt42b0
        .byte $41,$00
wt42b2
        .byte $80,$7E
wt42b4
        .byte $80,$00
wt42b6
        .byte $40,$7E
wt42b8
        .byte $40,$00
        .byte $FF,<wt42b6,>wt42b6
wt43
wt43b0
        .byte $41,$00
wt43b2
        .byte $80,$52
wt43b4
        .byte $80,$00
wt43b6
        .byte $40,$52
wt43b8
        .byte $40,$00
        .byte $FF,<wt43b6,>wt43b6
wt44
wt44b0
        .byte $41,$00
wt44b2
        .byte $41,$00
wt44b4
        .byte $41,$00
wt44b6
        .byte $40,$00
        .byte $FF,<wt44b6,>wt44b6
wt45
wt45b0
        .byte $41,$00
wt45b2
        .byte $41,$00
wt45b4
        .byte $41,$00
wt45b6
        .byte $41,$00
wt45b8
        .byte $41,$00
wt45b10
        .byte $41,$00
wt45b12
        .byte $41,$00
wt45b14
        .byte $41,$00
wt45b16
        .byte $41,$00
wt45b18
        .byte $40,$00
wt45b20
        .byte $40,$00
wt45b22
        .byte $40,$00
        .byte $FF,<wt45b22,>wt45b22
wt46
wt46b0
        .byte $41,$00
wt46b2
        .byte $41,$00
wt46b4
        .byte $41,$00
wt46b6
        .byte $40,$00
        .byte $FF,<wt46b6,>wt46b6
wt47
wt47b0
        .byte $41,$00
wt47b2
        .byte $41,$00
wt47b4
        .byte $41,$00
wt47b6
        .byte $41,$00
wt47b8
        .byte $41,$00
wt47b10
        .byte $41,$00
wt47b12
        .byte $41,$00
wt47b14
        .byte $41,$00
wt47b16
        .byte $41,$00
wt47b18
        .byte $40,$00
wt47b20
        .byte $40,$00
wt47b22
        .byte $40,$00
        .byte $FF,<wt47b22,>wt47b22
wt48
wt48b0
        .byte $41,$00
wt48b2
        .byte $41,$00
wt48b4
        .byte $41,$00
wt48b6
        .byte $41,$00
wt48b8
        .byte $41,$00
wt48b10
        .byte $41,$00
wt48b12
        .byte $41,$00
wt48b14
        .byte $41,$00
wt48b16
        .byte $41,$00
wt48b18
        .byte $40,$00
wt48b20
        .byte $40,$00
wt48b22
        .byte $40,$00
        .byte $FF,<wt48b22,>wt48b22
wt49
wt49b0
        .byte $41,$00
wt49b2
        .byte $41,$00
wt49b4
        .byte $41,$00
wt49b6
        .byte $40,$00
        .byte $FF,<wt49b6,>wt49b6
wt50
wt50b0
        .byte $41,$00
wt50b2
        .byte $41,$00
wt50b4
        .byte $41,$00
wt50b6
        .byte $41,$00
wt50b8
        .byte $41,$00
wt50b10
        .byte $41,$00
wt50b12
        .byte $41,$00
wt50b14
        .byte $41,$00
wt50b16
        .byte $41,$00
wt50b18
        .byte $40,$00
wt50b20
        .byte $40,$00
wt50b22
        .byte $40,$00
        .byte $FF,<wt50b22,>wt50b22
wt51
wt51b0
        .byte $41,$00
wt51b2
        .byte $41,$00
wt51b4
        .byte $41,$00
wt51b6
        .byte $40,$00
        .byte $FF,<wt51b6,>wt51b6
wt52
wt52b0
        .byte $41,$00
wt52b2
        .byte $41,$01
wt52b4
        .byte $41,$02
wt52b6
        .byte $41,$03
wt52b8
        .byte $41,$03
wt52b10
        .byte $41,$02
wt52b12
        .byte $41,$01
wt52b14
        .byte $41,$00
wt52b16
        .byte $41,$00
wt52b18
        .byte $41,$01
wt52b20
        .byte $41,$02
wt52b22
        .byte $41,$03
wt52b24
        .byte $41,$03
wt52b26
        .byte $41,$02
wt52b28
        .byte $41,$01
wt52b30
        .byte $41,$00
wt52b32
        .byte $41,$00
wt52b34
        .byte $41,$01
wt52b36
        .byte $41,$02
wt52b38
        .byte $41,$03
wt52b40
        .byte $41,$03
wt52b42
        .byte $41,$02
wt52b44
        .byte $41,$01
wt52b46
        .byte $41,$00
wt52b48
        .byte $41,$00
wt52b50
        .byte $41,$01
wt52b52
        .byte $41,$02
wt52b54
        .byte $41,$03
wt52b56
        .byte $41,$03
wt52b58
        .byte $41,$02
wt52b60
        .byte $41,$01
wt52b62
        .byte $41,$00
wt52b64
        .byte $41,$00
wt52b66
        .byte $40,$01
wt52b68
        .byte $40,$02
wt52b70
        .byte $40,$03
        .byte $FF,<wt52b70,>wt52b70
wt53
wt53b0
        .byte $41,$00
wt53b2
        .byte $41,$FF
wt53b4
        .byte $41,$FE
wt53b6
        .byte $41,$FD
wt53b8
        .byte $41,$FC
wt53b10
        .byte $41,$FB
wt53b12
        .byte $41,$F8
wt53b14
        .byte $41,$F6
wt53b16
        .byte $41,$F4
wt53b18
        .byte $41,$F3
wt53b20
        .byte $41,$F1
wt53b22
        .byte $41,$F0
wt53b24
        .byte $41,$EC
wt53b26
        .byte $41,$ED
wt53b28
        .byte $41,$EE
wt53b30
        .byte $41,$EF
wt53b32
        .byte $41,$EF
wt53b34
        .byte $41,$EE
wt53b36
        .byte $41,$ED
wt53b38
        .byte $41,$EC
wt53b40
        .byte $41,$EC
wt53b42
        .byte $41,$ED
wt53b44
        .byte $41,$EE
wt53b46
        .byte $41,$EF
wt53b48
        .byte $41,$EF
wt53b50
        .byte $41,$EE
wt53b52
        .byte $41,$ED
wt53b54
        .byte $41,$EC
wt53b56
        .byte $41,$EC
wt53b58
        .byte $41,$ED
wt53b60
        .byte $41,$EE
wt53b62
        .byte $41,$EF
wt53b64
        .byte $41,$EF
wt53b66
        .byte $40,$EE
wt53b68
        .byte $40,$ED
wt53b70
        .byte $40,$EC
        .byte $FF,<wt53b70,>wt53b70
wt54
wt54b0
        .byte $41,$00
wt54b2
        .byte $41,$FE
wt54b4
        .byte $41,$FC
wt54b6
        .byte $41,$FA
wt54b8
        .byte $41,$F9
wt54b10
        .byte $41,$F7
wt54b12
        .byte $41,$F5
wt54b14
        .byte $41,$F3
wt54b16
        .byte $41,$F1
wt54b18
        .byte $41,$F0
wt54b20
        .byte $41,$EE
wt54b22
        .byte $41,$EC
wt54b24
        .byte $41,$F2
wt54b26
        .byte $41,$F2
wt54b28
        .byte $41,$F2
wt54b30
        .byte $41,$F2
wt54b32
        .byte $41,$F2
wt54b34
        .byte $41,$F2
wt54b36
        .byte $41,$F2
wt54b38
        .byte $41,$F2
wt54b40
        .byte $41,$F2
wt54b42
        .byte $40,$F2
wt54b44
        .byte $40,$F2
wt54b46
        .byte $40,$F2
        .byte $FF,<wt54b46,>wt54b46
wt55
wt55b0
        .byte $41,$00
wt55b2
        .byte $41,$00
wt55b4
        .byte $41,$00
wt55b6
        .byte $41,$00
wt55b8
        .byte $41,$00
wt55b10
        .byte $41,$00
wt55b12
        .byte $41,$00
wt55b14
        .byte $41,$00
wt55b16
        .byte $41,$00
wt55b18
        .byte $41,$00
wt55b20
        .byte $41,$00
wt55b22
        .byte $41,$00
wt55b24
        .byte $41,$00
wt55b26
        .byte $41,$00
wt55b28
        .byte $41,$00
wt55b30
        .byte $40,$00
wt55b32
        .byte $40,$00
wt55b34
        .byte $40,$00
        .byte $FF,<wt55b34,>wt55b34
wt56
wt56b0
        .byte $41,$00
wt56b2
        .byte $41,$01
wt56b4
        .byte $41,$04
wt56b6
        .byte $41,$05
wt56b8
        .byte $41,$08
wt56b10
        .byte $41,$0A
wt56b12
        .byte $41,$0C
wt56b14
        .byte $41,$0D
wt56b16
        .byte $41,$0F
wt56b18
        .byte $41,$10
wt56b20
        .byte $41,$12
wt56b22
        .byte $41,$13
wt56b24
        .byte $41,$2A
wt56b26
        .byte $41,$2B
wt56b28
        .byte $41,$2C
wt56b30
        .byte $41,$2D
wt56b32
        .byte $41,$2D
wt56b34
        .byte $41,$2C
wt56b36
        .byte $41,$2B
wt56b38
        .byte $41,$2A
wt56b40
        .byte $41,$2A
wt56b42
        .byte $41,$2B
wt56b44
        .byte $41,$2C
wt56b46
        .byte $41,$2D
wt56b48
        .byte $41,$2D
wt56b50
        .byte $41,$2C
wt56b52
        .byte $41,$2B
wt56b54
        .byte $41,$2A
wt56b56
        .byte $41,$2A
wt56b58
        .byte $41,$2B
wt56b60
        .byte $41,$2C
wt56b62
        .byte $41,$2D
wt56b64
        .byte $41,$2D
wt56b66
        .byte $40,$2C
wt56b68
        .byte $40,$2B
wt56b70
        .byte $40,$2A
        .byte $FF,<wt56b70,>wt56b70
wt57
wt57b0
        .byte $41,$00
wt57b2
        .byte $41,$FF
wt57b4
        .byte $41,$FC
wt57b6
        .byte $41,$F9
wt57b8
        .byte $41,$F6
wt57b10
        .byte $41,$F1
wt57b12
        .byte $41,$ED
wt57b14
        .byte $41,$EA
wt57b16
        .byte $41,$E7
wt57b18
        .byte $41,$E4
wt57b20
        .byte $41,$E1
wt57b22
        .byte $41,$DD
wt57b24
        .byte $41,$D9
wt57b26
        .byte $41,$D5
wt57b28
        .byte $41,$D3
wt57b30
        .byte $41,$D1
wt57b32
        .byte $41,$CE
wt57b34
        .byte $41,$CC
wt57b36
        .byte $41,$CA
wt57b38
        .byte $41,$C7
wt57b40
        .byte $41,$C5
wt57b42
        .byte $41,$C3
wt57b44
        .byte $41,$C1
wt57b46
        .byte $41,$BE
wt57b48
        .byte $41,$BC
wt57b50
        .byte $41,$BA
wt57b52
        .byte $41,$B9
wt57b54
        .byte $41,$B8
wt57b56
        .byte $41,$B6
wt57b58
        .byte $41,$B3
wt57b60
        .byte $41,$B1
wt57b62
        .byte $41,$B0
wt57b64
        .byte $41,$AF
wt57b66
        .byte $41,$AE
wt57b68
        .byte $41,$AD
wt57b70
        .byte $41,$AB
wt57b72
        .byte $41,$AA
wt57b74
        .byte $41,$A9
wt57b76
        .byte $41,$A8
wt57b78
        .byte $41,$A7
wt57b80
        .byte $41,$A6
wt57b82
        .byte $41,$A5
wt57b84
        .byte $41,$A4
wt57b86
        .byte $41,$A3
wt57b88
        .byte $41,$A1
wt57b90
        .byte $40,$A0
wt57b92
        .byte $40,$9F
wt57b94
        .byte $40,$9E
        .byte $FF,<wt57b94,>wt57b94
wt58
wt58b0
        .byte $41,$00
wt58b2
        .byte $41,$02
wt58b4
        .byte $41,$05
wt58b6
        .byte $41,$08
wt58b8
        .byte $41,$08
wt58b10
        .byte $41,$05
wt58b12
        .byte $41,$02
wt58b14
        .byte $41,$00
wt58b16
        .byte $41,$00
wt58b18
        .byte $41,$02
wt58b20
        .byte $41,$05
wt58b22
        .byte $41,$08
wt58b24
        .byte $41,$08
wt58b26
        .byte $41,$05
wt58b28
        .byte $41,$02
wt58b30
        .byte $41,$00
wt58b32
        .byte $41,$00
wt58b34
        .byte $41,$02
wt58b36
        .byte $41,$05
wt58b38
        .byte $41,$08
wt58b40
        .byte $41,$08
wt58b42
        .byte $40,$05
wt58b44
        .byte $40,$02
wt58b46
        .byte $40,$00
        .byte $FF,<wt58b46,>wt58b46
wt59
wt59b0
        .byte $41,$00
wt59b2
        .byte $41,$01
wt59b4
        .byte $41,$04
wt59b6
        .byte $41,$05
wt59b8
        .byte $41,$08
wt59b10
        .byte $41,$0A
wt59b12
        .byte $41,$0C
wt59b14
        .byte $41,$0D
wt59b16
        .byte $41,$0F
wt59b18
        .byte $41,$10
wt59b20
        .byte $41,$12
wt59b22
        .byte $41,$13
wt59b24
        .byte $41,$19
wt59b26
        .byte $41,$1B
wt59b28
        .byte $41,$1E
wt59b30
        .byte $41,$21
wt59b32
        .byte $41,$21
wt59b34
        .byte $41,$1E
wt59b36
        .byte $41,$1B
wt59b38
        .byte $41,$19
wt59b40
        .byte $41,$19
wt59b42
        .byte $41,$1B
wt59b44
        .byte $41,$1E
wt59b46
        .byte $41,$21
wt59b48
        .byte $41,$21
wt59b50
        .byte $41,$1E
wt59b52
        .byte $41,$1B
wt59b54
        .byte $41,$19
wt59b56
        .byte $41,$19
wt59b58
        .byte $41,$1B
wt59b60
        .byte $41,$1E
wt59b62
        .byte $41,$21
wt59b64
        .byte $41,$21
wt59b66
        .byte $40,$1E
wt59b68
        .byte $40,$1B
wt59b70
        .byte $40,$19
        .byte $FF,<wt59b70,>wt59b70
wt60
wt60b0
        .byte $41,$00
wt60b2
        .byte $80,$00
wt60b4
        .byte $80,$00
wt60b6
        .byte $40,$00
wt60b8
        .byte $40,$FE
wt60b10
        .byte $40,$FC
wt60b12
        .byte $40,$FA
wt60b14
        .byte $40,$F8
wt60b16
        .byte $40,$F5
wt60b18
        .byte $40,$F2
wt60b20
        .byte $40,$EC
wt60b22
        .byte $40,$E9
wt60b24
        .byte $40,$E5
wt60b26
        .byte $40,$E1
wt60b28
        .byte $40,$D9
wt60b30
        .byte $40,$D7
wt60b32
        .byte $40,$D7
wt60b34
        .byte $40,$D7
wt60b36
        .byte $40,$D7
wt60b38
        .byte $40,$D7
wt60b40
        .byte $40,$D7
wt60b42
        .byte $40,$D7
wt60b44
        .byte $40,$D7
wt60b46
        .byte $40,$D7
wt60b48
        .byte $40,$D7
wt60b50
        .byte $40,$D7
wt60b52
        .byte $40,$D7
wt60b54
        .byte $40,$D7
wt60b56
        .byte $40,$D7
wt60b58
        .byte $40,$D7
wt60b60
        .byte $40,$D7
wt60b62
        .byte $40,$D7
wt60b64
        .byte $40,$D7
wt60b66
        .byte $40,$D7
wt60b68
        .byte $40,$D7
wt60b70
        .byte $40,$D7
        .byte $FF,<wt60b70,>wt60b70
wt61
wt61b0
        .byte $41,$00
wt61b2
        .byte $41,$01
wt61b4
        .byte $41,$02
wt61b6
        .byte $41,$03
wt61b8
        .byte $41,$03
wt61b10
        .byte $41,$02
wt61b12
        .byte $41,$01
wt61b14
        .byte $41,$00
wt61b16
        .byte $41,$00
wt61b18
        .byte $41,$01
wt61b20
        .byte $41,$02
wt61b22
        .byte $41,$03
wt61b24
        .byte $41,$03
wt61b26
        .byte $41,$02
wt61b28
        .byte $41,$01
wt61b30
        .byte $41,$00
wt61b32
        .byte $41,$00
wt61b34
        .byte $41,$01
wt61b36
        .byte $41,$02
wt61b38
        .byte $41,$03
wt61b40
        .byte $41,$03
wt61b42
        .byte $40,$02
wt61b44
        .byte $40,$01
wt61b46
        .byte $40,$00
        .byte $FF,<wt61b46,>wt61b46
wt62
wt62b0
        .byte $41,$00
wt62b2
        .byte $41,$01
wt62b4
        .byte $41,$03
wt62b6
        .byte $41,$04
wt62b8
        .byte $41,$06
wt62b10
        .byte $41,$07
wt62b12
        .byte $41,$09
wt62b14
        .byte $41,$0A
wt62b16
        .byte $41,$0B
wt62b18
        .byte $41,$0C
wt62b20
        .byte $41,$0D
wt62b22
        .byte $41,$0E
wt62b24
        .byte $41,$10
wt62b26
        .byte $41,$11
wt62b28
        .byte $41,$12
wt62b30
        .byte $41,$13
wt62b32
        .byte $41,$13
wt62b34
        .byte $41,$12
wt62b36
        .byte $41,$11
wt62b38
        .byte $41,$10
wt62b40
        .byte $41,$10
wt62b42
        .byte $41,$11
wt62b44
        .byte $41,$12
wt62b46
        .byte $41,$13
wt62b48
        .byte $41,$13
wt62b50
        .byte $41,$12
wt62b52
        .byte $41,$11
wt62b54
        .byte $41,$10
wt62b56
        .byte $41,$10
wt62b58
        .byte $41,$11
wt62b60
        .byte $41,$12
wt62b62
        .byte $41,$13
wt62b64
        .byte $41,$13
wt62b66
        .byte $40,$12
wt62b68
        .byte $40,$11
wt62b70
        .byte $40,$10
        .byte $FF,<wt62b70,>wt62b70
wt63
wt63b0
        .byte $41,$00
wt63b2
        .byte $41,$01
wt63b4
        .byte $41,$03
wt63b6
        .byte $41,$04
wt63b8
        .byte $41,$06
wt63b10
        .byte $41,$07
wt63b12
        .byte $41,$09
wt63b14
        .byte $41,$0A
wt63b16
        .byte $41,$0B
wt63b18
        .byte $41,$0C
wt63b20
        .byte $41,$0D
wt63b22
        .byte $41,$0E
wt63b24
        .byte $41,$10
wt63b26
        .byte $41,$10
wt63b28
        .byte $41,$10
wt63b30
        .byte $41,$10
wt63b32
        .byte $41,$10
wt63b34
        .byte $41,$10
wt63b36
        .byte $41,$10
wt63b38
        .byte $41,$10
wt63b40
        .byte $41,$10
wt63b42
        .byte $41,$10
wt63b44
        .byte $41,$10
wt63b46
        .byte $41,$10
wt63b48
        .byte $41,$10
wt63b50
        .byte $41,$10
wt63b52
        .byte $41,$10
wt63b54
        .byte $40,$10
wt63b56
        .byte $40,$10
wt63b58
        .byte $40,$10
        .byte $FF,<wt63b58,>wt63b58
wt64
wt64b0
        .byte $41,$00
wt64b2
        .byte $80,$11
wt64b4
        .byte $80,$00
wt64b6
        .byte $40,$11
wt64b8
        .byte $40,$00
wt64b10
        .byte $40,$11
        .byte $FF,<wt64b10,>wt64b10
wt65
wt65b0
        .byte $41,$00
wt65b2
        .byte $80,$11
wt65b4
        .byte $80,$00
wt65b6
        .byte $40,$11
wt65b8
        .byte $40,$00
wt65b10
        .byte $40,$11
        .byte $FF,<wt65b10,>wt65b10
wt66
wt66b0
        .byte $41,$00
wt66b2
        .byte $80,$14
wt66b4
        .byte $80,$00
wt66b6
        .byte $40,$14
wt66b8
        .byte $40,$00
wt66b10
        .byte $40,$14
        .byte $FF,<wt66b10,>wt66b10
wt67
wt67b0
        .byte $41,$00
wt67b2
        .byte $80,$11
wt67b4
        .byte $80,$00
wt67b6
        .byte $40,$11
wt67b8
        .byte $40,$00
        .byte $FF,<wt67b6,>wt67b6
wt68
wt68b0
        .byte $41,$00
wt68b2
        .byte $80,$14
wt68b4
        .byte $80,$00
wt68b6
        .byte $40,$14
wt68b8
        .byte $40,$00
wt68b10
        .byte $40,$14
        .byte $FF,<wt68b10,>wt68b10
wt69
wt69b0
        .byte $41,$00
wt69b2
        .byte $41,$00
wt69b4
        .byte $41,$00
wt69b6
        .byte $40,$00
        .byte $FF,<wt69b6,>wt69b6
wt70
wt70b0
        .byte $41,$00
wt70b2
        .byte $41,$19
wt70b4
        .byte $41,$19
wt70b6
        .byte $41,$4A
wt70b8
        .byte $80,$5B
wt70b10
        .byte $40,$5B
wt70b12
        .byte $40,$4A
        .byte $FF,<wt70b12,>wt70b12
wt71
wt71b0
        .byte $41,$00
wt71b2
        .byte $40,$11
wt71b4
        .byte $40,$00
wt71b6
        .byte $40,$11
        .byte $FF,<wt71b6,>wt71b6
wt72
wt72b0
        .byte $43,$00
wt72b2
        .byte $43,$00
wt72b4
        .byte $43,$00
wt72b6
        .byte $42,$00
        .byte $FF,<wt72b6,>wt72b6
wt73
wt73b0
        .byte $43,$00
wt73b2
        .byte $80,$00
wt73b4
        .byte $80,$00
wt73b6
        .byte $42,$00
        .byte $FF,<wt73b6,>wt73b6
wt74
wt74b0
        .byte $41,$00
wt74b2
        .byte $80,$77
wt74b4
        .byte $80,$00
wt74b6
        .byte $40,$77
wt74b8
        .byte $40,$00
        .byte $FF,<wt74b6,>wt74b6
wt75
wt75b0
        .byte $41,$00
wt75b2
        .byte $80,$78
wt75b4
        .byte $80,$00
wt75b6
        .byte $40,$78
wt75b8
        .byte $40,$00
        .byte $FF,<wt75b6,>wt75b6
wt76
wt76b0
        .byte $41,$00
wt76b2
        .byte $80,$69
wt76b4
        .byte $80,$00
wt76b6
        .byte $40,$69
wt76b8
        .byte $40,$00
        .byte $FF,<wt76b6,>wt76b6
wt77
wt77b0
        .byte $41,$00
wt77b2
        .byte $80,$77
wt77b4
        .byte $80,$00
wt77b6
        .byte $40,$77
wt77b8
        .byte $40,$00
wt77b10
        .byte $40,$77
wt77b12
        .byte $40,$00
wt77b14
        .byte $40,$77
wt77b16
        .byte $40,$00
wt77b18
        .byte $40,$77
wt77b20
        .byte $40,$00
wt77b22
        .byte $40,$77
wt77b24
        .byte $40,$00
wt77b26
        .byte $40,$77
wt77b28
        .byte $40,$00
wt77b30
        .byte $40,$77
wt77b32
        .byte $40,$00
wt77b34
        .byte $40,$77
wt77b36
        .byte $40,$00
wt77b38
        .byte $40,$77
wt77b40
        .byte $40,$00
wt77b42
        .byte $40,$77
wt77b44
        .byte $40,$00
wt77b46
        .byte $40,$77
wt77b48
        .byte $40,$77
wt77b50
        .byte $80,$77
wt77b52
        .byte $80,$00
wt77b54
        .byte $40,$77
wt77b56
        .byte $40,$00
wt77b58
        .byte $40,$77
wt77b60
        .byte $40,$00
wt77b62
        .byte $40,$77
wt77b64
        .byte $40,$00
wt77b66
        .byte $40,$77
wt77b68
        .byte $40,$00
wt77b70
        .byte $40,$77
wt77b72
        .byte $40,$00
wt77b74
        .byte $40,$77
wt77b76
        .byte $40,$00
wt77b78
        .byte $40,$77
wt77b80
        .byte $40,$00
wt77b82
        .byte $40,$77
wt77b84
        .byte $40,$00
wt77b86
        .byte $40,$77
wt77b88
        .byte $40,$00
wt77b90
        .byte $40,$77
wt77b92
        .byte $40,$00
wt77b94
        .byte $40,$77
        .byte $FF,<wt77b94,>wt77b94
wt78
wt78b0
        .byte $41,$00
wt78b2
        .byte $80,$69
wt78b4
        .byte $80,$00
wt78b6
        .byte $40,$69
wt78b8
        .byte $40,$00
wt78b10
        .byte $40,$69
wt78b12
        .byte $40,$00
wt78b14
        .byte $40,$69
wt78b16
        .byte $40,$00
wt78b18
        .byte $40,$69
wt78b20
        .byte $40,$00
wt78b22
        .byte $40,$69
wt78b24
        .byte $40,$69
wt78b26
        .byte $80,$69
wt78b28
        .byte $80,$00
wt78b30
        .byte $40,$69
wt78b32
        .byte $40,$00
wt78b34
        .byte $40,$69
        .byte $FF,<wt78b34,>wt78b34
wt79
wt79b0
        .byte $41,$00
wt79b2
        .byte $80,$77
wt79b4
        .byte $80,$00
wt79b6
        .byte $40,$77
wt79b8
        .byte $40,$00
wt79b10
        .byte $40,$77
        .byte $FF,<wt79b10,>wt79b10
wt80
wt80b0
        .byte $41,$00
wt80b2
        .byte $80,$7E
wt80b4
        .byte $80,$00
wt80b6
        .byte $40,$7E
wt80b8
        .byte $40,$00
        .byte $FF,<wt80b6,>wt80b6
wt81
wt81b0
        .byte $41,$00
wt81b2
        .byte $80,$80
wt81b4
        .byte $80,$00
wt81b6
        .byte $40,$80
wt81b8
        .byte $40,$00
wt81b10
        .byte $40,$80
wt81b12
        .byte $40,$00
wt81b14
        .byte $40,$80
wt81b16
        .byte $40,$00
wt81b18
        .byte $40,$80
wt81b20
        .byte $40,$00
wt81b22
        .byte $40,$80
wt81b24
        .byte $40,$00
wt81b26
        .byte $40,$80
wt81b28
        .byte $40,$00
wt81b30
        .byte $40,$80
wt81b32
        .byte $40,$00
wt81b34
        .byte $40,$80
wt81b36
        .byte $40,$00
wt81b38
        .byte $40,$80
wt81b40
        .byte $40,$00
wt81b42
        .byte $40,$80
wt81b44
        .byte $40,$00
wt81b46
        .byte $40,$80
wt81b48
        .byte $40,$80
wt81b50
        .byte $80,$80
wt81b52
        .byte $80,$00
wt81b54
        .byte $40,$80
wt81b56
        .byte $40,$00
wt81b58
        .byte $40,$80
wt81b60
        .byte $40,$00
wt81b62
        .byte $40,$80
wt81b64
        .byte $40,$00
wt81b66
        .byte $40,$80
wt81b68
        .byte $40,$00
wt81b70
        .byte $40,$80
wt81b72
        .byte $40,$00
wt81b74
        .byte $40,$80
wt81b76
        .byte $40,$00
wt81b78
        .byte $40,$80
wt81b80
        .byte $40,$00
wt81b82
        .byte $40,$80
wt81b84
        .byte $40,$00
wt81b86
        .byte $40,$80
wt81b88
        .byte $40,$00
wt81b90
        .byte $40,$80
wt81b92
        .byte $40,$00
wt81b94
        .byte $40,$80
        .byte $FF,<wt81b94,>wt81b94
wt82
wt82b0
        .byte $41,$00
wt82b2
        .byte $80,$78
wt82b4
        .byte $80,$00
wt82b6
        .byte $40,$78
wt82b8
        .byte $40,$00
wt82b10
        .byte $40,$78
wt82b12
        .byte $40,$00
wt82b14
        .byte $40,$78
wt82b16
        .byte $40,$00
wt82b18
        .byte $40,$78
wt82b20
        .byte $40,$00
wt82b22
        .byte $40,$78
wt82b24
        .byte $40,$78
wt82b26
        .byte $80,$78
wt82b28
        .byte $80,$00
wt82b30
        .byte $40,$78
wt82b32
        .byte $40,$00
wt82b34
        .byte $40,$78
        .byte $FF,<wt82b34,>wt82b34
wt83
wt83b0
        .byte $15,$00
wt83b2
        .byte $80,$1E
wt83b4
        .byte $80,$00
wt83b6
        .byte $14,$1E
wt83b8
        .byte $14,$00
        .byte $FF,<wt83b6,>wt83b6
wt84
wt84b0
        .byte $15,$00
wt84b2
        .byte $80,$4B
wt84b4
        .byte $80,$00
wt84b6
        .byte $14,$4B
wt84b8
        .byte $14,$00
        .byte $FF,<wt84b6,>wt84b6
wt85
wt85b0
        .byte $15,$00
wt85b2
        .byte $80,$35
wt85b4
        .byte $80,$00
wt85b6
        .byte $14,$35
wt85b8
        .byte $14,$00
        .byte $FF,<wt85b6,>wt85b6
wt86
wt86b0
        .byte $15,$00
wt86b2
        .byte $80,$08
wt86b4
        .byte $80,$00
wt86b6
        .byte $14,$08
wt86b8
        .byte $14,$00
        .byte $FF,<wt86b6,>wt86b6
wt87
wt87b0
        .byte $41,$00
wt87b2
        .byte $80,$67
wt87b4
        .byte $80,$00
wt87b6
        .byte $40,$67
wt87b8
        .byte $40,$00
        .byte $FF,<wt87b6,>wt87b6
wt88
wt88b0
        .byte $41,$00
wt88b2
        .byte $80,$40
wt88b4
        .byte $80,$00
wt88b6
        .byte $40,$40
wt88b8
        .byte $40,$00
        .byte $FF,<wt88b6,>wt88b6
wt89
wt89b0
        .byte $41,$00
wt89b2
        .byte $80,$67
wt89b4
        .byte $80,$00
wt89b6
        .byte $40,$67
wt89b8
        .byte $40,$00
wt89b10
        .byte $40,$67
        .byte $FF,<wt89b10,>wt89b10
wt90
wt90b0
        .byte $41,$00
wt90b2
        .byte $80,$40
wt90b4
        .byte $80,$00
wt90b6
        .byte $40,$40
wt90b8
        .byte $40,$00
wt90b10
        .byte $40,$40
        .byte $FF,<wt90b10,>wt90b10
wt91
wt91b0
        .byte $15,$00
wt91b2
        .byte $80,$EB
wt91b4
        .byte $80,$00
wt91b6
        .byte $14,$EB
wt91b8
        .byte $14,$00
        .byte $FF,<wt91b6,>wt91b6
wt92
wt92b0
        .byte $15,$00
wt92b2
        .byte $80,$47
wt92b4
        .byte $80,$00
wt92b6
        .byte $14,$47
wt92b8
        .byte $14,$00
        .byte $FF,<wt92b6,>wt92b6
wt93
wt93b0
        .byte $41,$00
wt93b2
        .byte $80,$53
wt93b4
        .byte $80,$00
wt93b6
        .byte $40,$53
wt93b8
        .byte $40,$00
        .byte $FF,<wt93b6,>wt93b6
wt94
wt94b0
        .byte $41,$00
wt94b2
        .byte $80,$69
wt94b4
        .byte $80,$00
wt94b6
        .byte $40,$69
wt94b8
        .byte $40,$00
wt94b10
        .byte $40,$69
        .byte $FF,<wt94b10,>wt94b10
wt95
wt95b0
        .byte $41,$00
wt95b2
        .byte $80,$53
wt95b4
        .byte $80,$00
wt95b6
        .byte $40,$53
wt95b8
        .byte $40,$00
wt95b10
        .byte $40,$53
        .byte $FF,<wt95b10,>wt95b10
wt96
wt96b0
        .byte $15,$00
wt96b2
        .byte $80,$D7
wt96b4
        .byte $80,$00
wt96b6
        .byte $14,$D7
wt96b8
        .byte $14,$00
        .byte $FF,<wt96b6,>wt96b6
wt97
wt97b0
        .byte $15,$00
wt97b2
        .byte $80,$4F
wt97b4
        .byte $80,$00
wt97b6
        .byte $14,$4F
wt97b8
        .byte $14,$00
        .byte $FF,<wt97b6,>wt97b6
wt98
wt98b0
        .byte $15,$00
wt98b2
        .byte $80,$2E
wt98b4
        .byte $80,$00
wt98b6
        .byte $14,$2E
wt98b8
        .byte $14,$00
        .byte $FF,<wt98b6,>wt98b6
wt99
wt99b0
        .byte $15,$00
wt99b2
        .byte $80,$1F
wt99b4
        .byte $80,$00
wt99b6
        .byte $14,$1F
wt99b8
        .byte $14,$00
wt99b10
        .byte $14,$1F
wt99b12
        .byte $14,$00
wt99b14
        .byte $14,$2B
        .byte $FF,<wt99b12,>wt99b12
wt100
wt100b0
        .byte $15,$00
wt100b2
        .byte $80,$2F
wt100b4
        .byte $80,$00
wt100b6
        .byte $14,$2F
wt100b8
        .byte $14,$00
        .byte $FF,<wt100b6,>wt100b6
wt101
wt101b0
        .byte $15,$00
wt101b2
        .byte $80,$51
wt101b4
        .byte $80,$00
wt101b6
        .byte $14,$51
wt101b8
        .byte $14,$00
wt101b10
        .byte $14,$51
wt101b12
        .byte $14,$00
wt101b14
        .byte $14,$1A
        .byte $FF,<wt101b12,>wt101b12
wt102
wt102b0
        .byte $41,$00
wt102b2
        .byte $80,$17
wt102b4
        .byte $80,$00
wt102b6
        .byte $40,$17
wt102b8
        .byte $40,$00
wt102b10
        .byte $40,$17
        .byte $FF,<wt102b10,>wt102b10
wt103
wt103b0
        .byte $41,$00
wt103b2
        .byte $80,$17
wt103b4
        .byte $80,$00
wt103b6
        .byte $40,$17
wt103b8
        .byte $40,$00
wt103b10
        .byte $40,$17
        .byte $FF,<wt103b10,>wt103b10
wt104
wt104b0
        .byte $41,$00
wt104b2
        .byte $80,$27
wt104b4
        .byte $80,$00
wt104b6
        .byte $40,$27
wt104b8
        .byte $40,$00
wt104b10
        .byte $40,$27
        .byte $FF,<wt104b10,>wt104b10
wt105
wt105b0
        .byte $41,$00
wt105b2
        .byte $80,$17
wt105b4
        .byte $80,$00
wt105b6
        .byte $40,$17
wt105b8
        .byte $40,$00
        .byte $FF,<wt105b6,>wt105b6
wt106
wt106b0
        .byte $41,$00
wt106b2
        .byte $80,$27
wt106b4
        .byte $80,$00
wt106b6
        .byte $40,$27
wt106b8
        .byte $40,$00
wt106b10
        .byte $40,$27
        .byte $FF,<wt106b10,>wt106b10
wt107
wt107b0
        .byte $15,$00
wt107b2
        .byte $15,$FC
wt107b4
        .byte $80,$02
        .byte $FF,<wt107b4,>wt107b4
wt108
wt108b0
        .byte $41,$00
wt108b2
        .byte $80,$17
wt108b4
        .byte $40,$17
wt108b6
        .byte $40,$00
        .byte $FF,<wt108b6,>wt108b6
wt109
wt109b0
        .byte $41,$00
wt109b2
        .byte $40,$17
wt109b4
        .byte $40,$00
wt109b6
        .byte $40,$17
        .byte $FF,<wt109b6,>wt109b6
wt110
wt110b0
        .byte $41,$00
wt110b2
        .byte $41,$00
wt110b4
        .byte $41,$00
wt110b6
        .byte $41,$00
wt110b8
        .byte $41,$00
wt110b10
        .byte $41,$00
wt110b12
        .byte $41,$00
wt110b14
        .byte $41,$00
wt110b16
        .byte $41,$00
wt110b18
        .byte $41,$00
wt110b20
        .byte $41,$00
wt110b22
        .byte $41,$00
wt110b24
        .byte $41,$00
wt110b26
        .byte $41,$00
wt110b28
        .byte $41,$00
wt110b30
        .byte $40,$00
wt110b32
        .byte $40,$00
wt110b34
        .byte $40,$00
        .byte $FF,<wt110b34,>wt110b34
wt111
wt111b0
        .byte $41,$00
wt111b2
        .byte $41,$00
wt111b4
        .byte $41,$00
wt111b6
        .byte $40,$00
        .byte $FF,<wt111b6,>wt111b6
wt112
wt112b0
        .byte $81,$00
wt112b2
        .byte $80,$37
wt112b4
        .byte $80,$00
wt112b6
        .byte $80,$37
        .byte $FF,<wt112b4,>wt112b4
wt113
wt113b0
        .byte $41,$00
wt113b2
        .byte $41,$00
wt113b4
        .byte $41,$00
wt113b6
        .byte $41,$00
wt113b8
        .byte $41,$00
wt113b10
        .byte $41,$00
wt113b12
        .byte $41,$00
wt113b14
        .byte $41,$00
wt113b16
        .byte $41,$00
wt113b18
        .byte $40,$00
wt113b20
        .byte $40,$00
wt113b22
        .byte $40,$00
        .byte $FF,<wt113b22,>wt113b22
wt114
wt114b0
        .byte $41,$00
wt114b2
        .byte $41,$00
wt114b4
        .byte $41,$00
wt114b6
        .byte $41,$00
wt114b8
        .byte $41,$00
wt114b10
        .byte $41,$00
wt114b12
        .byte $41,$00
wt114b14
        .byte $41,$00
wt114b16
        .byte $41,$00
wt114b18
        .byte $41,$00
wt114b20
        .byte $41,$00
wt114b22
        .byte $41,$00
wt114b24
        .byte $41,$00
wt114b26
        .byte $41,$00
wt114b28
        .byte $41,$00
wt114b30
        .byte $41,$00
wt114b32
        .byte $41,$00
wt114b34
        .byte $41,$00
wt114b36
        .byte $41,$00
wt114b38
        .byte $41,$00
wt114b40
        .byte $41,$00
wt114b42
        .byte $40,$00
wt114b44
        .byte $40,$00
wt114b46
        .byte $40,$00
        .byte $FF,<wt114b46,>wt114b46
wt115
wt115b0
        .byte $41,$00
wt115b2
        .byte $80,$16
wt115b4
        .byte $80,$00
wt115b6
        .byte $40,$16
wt115b8
        .byte $40,$00
wt115b10
        .byte $40,$16
        .byte $FF,<wt115b10,>wt115b10
wt116
wt116b0
        .byte $41,$00
wt116b2
        .byte $80,$16
wt116b4
        .byte $80,$00
wt116b6
        .byte $40,$16
wt116b8
        .byte $40,$00
        .byte $FF,<wt116b6,>wt116b6
wt117
wt117b0
        .byte $81,$00
wt117b2
        .byte $41,$F0
wt117b4
        .byte $41,$F0
wt117b6
        .byte $41,$F5
wt117b8
        .byte $80,$0B
wt117b10
        .byte $40,$0B
wt117b12
        .byte $40,$F5
        .byte $FF,<wt117b12,>wt117b12
wt118
wt118b0
        .byte $41,$00
wt118b2
        .byte $40,$16
wt118b4
        .byte $40,$00
wt118b6
        .byte $40,$16
        .byte $FF,<wt118b6,>wt118b6

v0pat
        .byte $E6,$02,$00
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$02,$06
        .byte $E2,$02,$01
        .byte $E6,$02,$07
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$02,$08
        .byte $E2,$02,$01
        .byte $E6,$02,$00
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$02,$06
        .byte $E2,$02,$01
        .byte $E6,$02,$07
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$02,$08
        .byte $E2,$02,$01
        .byte $38,$01,$09
        .byte $58,$01,$0A
        .byte $58,$02,$0B
        .byte $58,$02,$0B
        .byte $58,$02,$0B
        .byte $58,$04,$0C
        .byte $58,$03,$0D
        .byte $58,$02,$0E
        .byte $B1,$01,$0F
        .byte $B1,$02,$0B
        .byte $B1,$02,$0E
        .byte $B1,$02,$0B
        .byte $B1,$04,$10
        .byte $2A,$04,$11
        .byte $B7,$04,$12
        .byte $B1,$04,$10
        .byte $B7,$04,$12
        .byte $B1,$05,$13
        .byte $73,$01,$14
        .byte $73,$02,$15
        .byte $73,$02,$0B
        .byte $73,$02,$0E
        .byte $73,$04,$16
        .byte $2A,$04,$11
        .byte $38,$01,$09
        .byte $88,$01,$0A
        .byte $88,$02,$0B
        .byte $88,$02,$0B
        .byte $88,$02,$0B
        .byte $88,$04,$17
        .byte $88,$03,$0D
        .byte $88,$02,$0E
        .byte $C9,$01,$0F
        .byte $C9,$02,$0B
        .byte $C9,$02,$0E
        .byte $C9,$02,$0B
        .byte $C9,$04,$10
        .byte $2A,$04,$11
        .byte $CD,$04,$10
        .byte $C9,$04,$10
        .byte $CD,$04,$10
        .byte $C9,$05,$13
        .byte $A1,$01,$14
        .byte $A1,$02,$15
        .byte $A1,$02,$0B
        .byte $A1,$02,$0E
        .byte $A1,$04,$18
        .byte $33,$02,$19
        .byte $2A,$01,$1A
        .byte $2A,$01,$1A
        .byte $38,$01,$09
        .byte $58,$01,$0A
        .byte $58,$02,$0B
        .byte $58,$02,$0B
        .byte $58,$02,$0B
        .byte $58,$04,$0C
        .byte $58,$03,$0D
        .byte $58,$02,$0E
        .byte $B1,$01,$0F
        .byte $B1,$02,$0B
        .byte $B1,$02,$0E
        .byte $B1,$02,$0B
        .byte $B1,$04,$10
        .byte $2A,$04,$11
        .byte $B7,$04,$12
        .byte $B1,$04,$10
        .byte $B7,$04,$12
        .byte $B1,$05,$13
        .byte $73,$01,$14
        .byte $73,$02,$15
        .byte $73,$02,$0B
        .byte $73,$02,$0E
        .byte $73,$04,$16
        .byte $2A,$04,$11
        .byte $38,$01,$09
        .byte $88,$01,$0A
        .byte $88,$02,$0B
        .byte $88,$02,$0B
        .byte $88,$02,$0B
        .byte $88,$04,$17
        .byte $88,$03,$0D
        .byte $88,$02,$0E
        .byte $C9,$01,$0F
        .byte $C9,$02,$0B
        .byte $C9,$02,$0E
        .byte $C9,$02,$0B
        .byte $C9,$04,$10
        .byte $2A,$04,$11
        .byte $CD,$04,$10
        .byte $C9,$04,$10
        .byte $CD,$04,$10
        .byte $C9,$05,$13
        .byte $A1,$01,$14
        .byte $A1,$02,$15
        .byte $A1,$02,$0B
        .byte $A1,$02,$0E
        .byte $A1,$04,$18
        .byte $33,$02,$19
        .byte $2A,$01,$1A
        .byte $2A,$01,$1A
        .byte $38,$02,$09
        .byte $38,$02,$09
        .byte $58,$02,$15
        .byte $58,$02,$0B
        .byte $58,$01,$0A
        .byte $58,$01,$0A
        .byte $58,$02,$0B
        .byte $73,$02,$15
        .byte $88,$02,$0B
        .byte $A1,$01,$14
        .byte $A1,$01,$0A
        .byte $A1,$02,$0B
        .byte $A1,$02,$0B
        .byte $A1,$02,$0B
        .byte $A1,$04,$18
        .byte $2A,$02,$1B
        .byte $A1,$01,$0F
        .byte $B1,$01,$1C
        .byte $B7,$01,$0A
        .byte $B7,$01,$0A
        .byte $B1,$02,$0B
        .byte $A1,$02,$0E
        .byte $88,$02,$0B
        .byte $73,$02,$0B
        .byte $58,$02,$0B
        .byte $4F,$04,$1D
        .byte $38,$01,$09
        .byte $58,$01,$0F
        .byte $58,$02,$0B
        .byte $58,$02,$0E
        .byte $73,$02,$0B
        .byte $58,$04,$0C
        .byte $2A,$04,$11
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $58,$01,$22
        .byte $B7,$02,$23
        .byte $B1,$02,$24
        .byte $B7,$01,$25
        .byte $B1,$02,$24
        .byte $B0,$01,$26
        .byte $A1,$02,$27
        .byte $B7,$01,$25
        .byte $B1,$02,$24
        .byte $B0,$01,$26
        .byte $A1,$02,$27
        .byte $B7,$02,$23
        .byte $B1,$02,$24
        .byte $73,$01,$28
        .byte $65,$02,$29
        .byte $58,$01,$22
        .byte $4F,$02,$2A
        .byte $73,$01,$28
        .byte $65,$02,$29
        .byte $58,$01,$22
        .byte $4F,$02,$2A
        .byte $88,$02,$2B
        .byte $73,$02,$1F
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $65,$01,$20
        .byte $58,$02,$21
        .byte $88,$01,$1E
        .byte $73,$02,$1F
        .byte $58,$01,$22
        .byte $B7,$02,$23
        .byte $B1,$02,$24
        .byte $B7,$01,$25
        .byte $B1,$02,$24
        .byte $B0,$01,$26
        .byte $A1,$02,$27
        .byte $B7,$01,$25
        .byte $B1,$02,$24
        .byte $B0,$01,$26
        .byte $A1,$02,$27
        .byte $B7,$02,$23
        .byte $B1,$02,$24
        .byte $73,$01,$28
        .byte $65,$02,$29
        .byte $58,$01,$22
        .byte $4F,$02,$2A
        .byte $73,$01,$28
        .byte $65,$02,$29
        .byte $58,$01,$22
        .byte $4F,$02,$2A
        .byte $88,$02,$2B
        .byte $73,$02,$1F
        .byte $88,$01,$2C
        .byte $73,$02,$2D
        .byte $65,$01,$2E
        .byte $58,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$02,$2F
        .byte $A1,$02,$30
        .byte $88,$01,$2E
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$31
        .byte $58,$02,$32
        .byte $88,$02,$2F
        .byte $A1,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$01,$31
        .byte $73,$02,$32
        .byte $65,$01,$33
        .byte $58,$02,$2F
        .byte $88,$02,$32
        .byte $A1,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$31
        .byte $58,$02,$32
        .byte $88,$01,$33
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$02,$2F
        .byte $A1,$02,$2F
        .byte $C5,$06,$34
        .byte $C5,$06,$35
        .byte $9D,$02,$2F
        .byte $73,$02,$2F
        .byte $73,$04,$36
        .byte $65,$02,$2F
        .byte $2A,$02,$1B
        .byte $2A,$02,$1B
        .byte $65,$01,$2C
        .byte $65,$01,$2C
        .byte $73,$02,$2F
        .byte $9D,$02,$32
        .byte $9D,$06,$34
        .byte $9D,$02,$2F
        .byte $B1,$03,$37
        .byte $9D,$03,$37
        .byte $73,$06,$38
        .byte $9D,$08,$39
        .byte $2A,$02,$1B
        .byte $2A,$02,$1B
        .byte $C5,$06,$34
        .byte $C5,$06,$35
        .byte $9D,$02,$2F
        .byte $73,$02,$32
        .byte $73,$04,$36
        .byte $65,$02,$2F
        .byte $2A,$02,$1B
        .byte $2A,$02,$1B
        .byte $65,$01,$2E
        .byte $65,$01,$2C
        .byte $73,$02,$2F
        .byte $9D,$02,$2F
        .byte $9D,$06,$34
        .byte $9D,$02,$32
        .byte $B1,$03,$37
        .byte $9D,$03,$37
        .byte $73,$06,$38
        .byte $9D,$08,$39
        .byte $2A,$02,$1B
        .byte $2A,$02,$1B
        .byte $A1,$04,$3A
        .byte $2A,$02,$1B
        .byte $A1,$01,$33
        .byte $A1,$01,$2C
        .byte $B1,$03,$37
        .byte $A1,$03,$37
        .byte $88,$06,$3B
        .byte $33,$02,$19
        .byte $2A,$06,$3C
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $A1,$04,$3A
        .byte $2A,$02,$1B
        .byte $A1,$01,$33
        .byte $A1,$01,$2E
        .byte $B1,$03,$37
        .byte $A1,$03,$37
        .byte $88,$06,$3B
        .byte $33,$02,$19
        .byte $2A,$06,$3C
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $B1,$04,$3D
        .byte $2A,$02,$1B
        .byte $B1,$01,$2C
        .byte $B1,$01,$2C
        .byte $C5,$03,$37
        .byte $B1,$03,$37
        .byte $A1,$06,$3E
        .byte $33,$02,$19
        .byte $2A,$06,$3C
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $B1,$04,$3D
        .byte $2A,$02,$1B
        .byte $B1,$01,$2E
        .byte $B1,$01,$33
        .byte $C5,$03,$37
        .byte $B1,$03,$37
        .byte $A1,$05,$3F
        .byte $C5,$03,$37
        .byte $CD,$02,$2F
        .byte $C5,$03,$37
        .byte $CD,$03,$37
        .byte $D1,$02,$2F
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$42
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $CD,$01,$42
        .byte $D2,$02,$43
        .byte $D2,$01,$41
        .byte $D2,$01,$41
        .byte $CD,$01,$44
        .byte $CD,$01,$44
        .byte $88,$01,$33
        .byte $73,$02,$32
        .byte $65,$01,$31
        .byte $58,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$02,$2F
        .byte $A1,$02,$32
        .byte $88,$01,$31
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$2E
        .byte $58,$02,$30
        .byte $88,$02,$2F
        .byte $A1,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$01,$2E
        .byte $73,$02,$30
        .byte $65,$01,$45
        .byte $58,$02,$2F
        .byte $88,$02,$30
        .byte $A1,$02,$2F
        .byte $88,$01,$2C
        .byte $73,$02,$2F
        .byte $65,$01,$2E
        .byte $58,$02,$30
        .byte $88,$01,$45
        .byte $73,$02,$2F
        .byte $65,$01,$2C
        .byte $58,$02,$2F
        .byte $88,$01,$46
        .byte $D2,$01,$40
        .byte $D2,$01,$40
        .byte $D2,$01,$47
        .byte $FF
v1pat
        .byte $00,$01,$48
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$02,$4C
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D4,$01,$49
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$03,$4E
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D4,$01,$49
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$02,$4C
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D4,$01,$49
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $D7,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$03,$4E
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D4,$01,$49
        .byte $D9,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$02,$4C
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$03,$4E
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D9,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $4F,$03,$50
        .byte $49,$03,$03
        .byte $3F,$02,$4B
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $49,$08,$51
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $4F,$03,$50
        .byte $49,$03,$03
        .byte $3F,$03,$52
        .byte $49,$01,$05
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $49,$08,$51
        .byte $D5,$01,$49
        .byte $D9,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$02,$4C
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$03,$4E
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D9,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $4F,$03,$50
        .byte $49,$03,$03
        .byte $3F,$02,$4B
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $49,$08,$51
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $4F,$03,$50
        .byte $49,$03,$03
        .byte $3F,$03,$52
        .byte $49,$01,$05
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $49,$02,$03
        .byte $49,$08,$51
        .byte $D5,$01,$49
        .byte $D9,$01,$49
        .byte $D9,$01,$49
        .byte $D9,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$02,$4C
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$03,$4E
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$02,$4C
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$03,$4E
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$02,$4C
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $D5,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $D8,$01,$49
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3F,$03,$4B
        .byte $3A,$03,$4A
        .byte $38,$03,$4E
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$08,$4D
        .byte $E6,$02,$53
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$02,$54
        .byte $E2,$02,$01
        .byte $E6,$02,$53
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$02,$54
        .byte $E2,$02,$01
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $36,$03,$57
        .byte $36,$03,$57
        .byte $33,$03,$58
        .byte $36,$01,$59
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $33,$02,$58
        .byte $36,$01,$59
        .byte $33,$01,$5A
        .byte $36,$02,$57
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $36,$03,$57
        .byte $36,$03,$57
        .byte $33,$03,$58
        .byte $36,$01,$59
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $33,$02,$58
        .byte $36,$01,$59
        .byte $33,$01,$5A
        .byte $36,$02,$57
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $36,$03,$57
        .byte $36,$03,$57
        .byte $33,$03,$58
        .byte $36,$01,$59
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $33,$02,$58
        .byte $36,$01,$59
        .byte $33,$01,$5A
        .byte $36,$02,$57
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $36,$03,$57
        .byte $36,$03,$57
        .byte $33,$03,$58
        .byte $36,$01,$59
        .byte $36,$02,$57
        .byte $36,$02,$57
        .byte $33,$02,$58
        .byte $36,$01,$59
        .byte $33,$01,$5A
        .byte $36,$02,$57
        .byte $E4,$02,$55
        .byte $DF,$02,$56
        .byte $E8,$02,$5B
        .byte $E5,$02,$5C
        .byte $38,$02,$4C
        .byte $38,$02,$4C
        .byte $38,$03,$4C
        .byte $38,$03,$4C
        .byte $35,$03,$5D
        .byte $38,$01,$5E
        .byte $38,$02,$4C
        .byte $38,$02,$4C
        .byte $35,$02,$5D
        .byte $38,$01,$5E
        .byte $35,$01,$5F
        .byte $38,$02,$4C
        .byte $E8,$02,$60
        .byte $E5,$02,$54
        .byte $E8,$02,$5B
        .byte $E5,$02,$54
        .byte $38,$02,$4C
        .byte $38,$02,$4C
        .byte $38,$03,$4C
        .byte $38,$03,$4C
        .byte $35,$03,$5D
        .byte $38,$01,$5E
        .byte $38,$02,$4C
        .byte $38,$02,$4C
        .byte $35,$02,$5D
        .byte $38,$01,$5E
        .byte $35,$01,$5F
        .byte $38,$02,$4C
        .byte $E8,$02,$60
        .byte $E5,$02,$61
        .byte $E9,$02,$62
        .byte $E6,$02,$63
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$03,$4A
        .byte $3A,$03,$4A
        .byte $38,$03,$4C
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $38,$02,$4C
        .byte $3A,$01,$4F
        .byte $38,$01,$5E
        .byte $3A,$02,$4A
        .byte $E9,$02,$64
        .byte $E6,$02,$65
        .byte $E9,$02,$62
        .byte $E6,$02,$63
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $3A,$03,$4A
        .byte $3A,$03,$4A
        .byte $38,$03,$4C
        .byte $3A,$01,$4F
        .byte $3A,$02,$4A
        .byte $3A,$02,$4A
        .byte $38,$02,$4C
        .byte $3A,$01,$4F
        .byte $38,$01,$5E
        .byte $3A,$02,$4A
        .byte $E9,$02,$62
        .byte $E6,$02,$65
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$68
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $B7,$01,$68
        .byte $C9,$02,$69
        .byte $C9,$01,$67
        .byte $C9,$01,$67
        .byte $B7,$01,$6A
        .byte $B7,$01,$6A
        .byte $E6,$02,$53
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$02,$54
        .byte $E2,$02,$01
        .byte $E6,$02,$53
        .byte $E2,$02,$01
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $58,$03,$02
        .byte $58,$03,$02
        .byte $49,$03,$03
        .byte $58,$01,$04
        .byte $58,$02,$02
        .byte $58,$02,$02
        .byte $49,$02,$03
        .byte $58,$01,$04
        .byte $49,$01,$05
        .byte $58,$02,$02
        .byte $E6,$01,$6B
        .byte $C9,$01,$6C
        .byte $C9,$01,$66
        .byte $C9,$01,$66
        .byte $C9,$01,$6D
        .byte $FF
v2pat
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0C,$03,$6E
        .byte $1B,$01,$6F
        .byte $2E,$02,$70
        .byte $0C,$02,$71
        .byte $0C,$04,$72
        .byte $2E,$02,$70
        .byte $1A,$01,$6F
        .byte $1B,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0C,$03,$6E
        .byte $1B,$01,$6F
        .byte $2E,$02,$70
        .byte $0C,$02,$71
        .byte $0C,$04,$72
        .byte $2E,$02,$70
        .byte $1A,$01,$6F
        .byte $1B,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0C,$03,$6E
        .byte $1B,$01,$6F
        .byte $2E,$02,$70
        .byte $0C,$02,$71
        .byte $0C,$04,$72
        .byte $2E,$02,$70
        .byte $1A,$01,$6F
        .byte $1B,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $0D,$03,$6E
        .byte $1E,$01,$6F
        .byte $2E,$02,$70
        .byte $0D,$02,$71
        .byte $0D,$04,$72
        .byte $2E,$02,$70
        .byte $1B,$01,$6F
        .byte $1E,$01,$6F
        .byte $0D,$03,$6E
        .byte $1E,$01,$6F
        .byte $2E,$02,$70
        .byte $0D,$02,$71
        .byte $0D,$04,$72
        .byte $2E,$02,$70
        .byte $1B,$01,$6F
        .byte $1E,$01,$6F
        .byte $0E,$03,$6E
        .byte $20,$01,$6F
        .byte $2E,$02,$70
        .byte $0E,$02,$71
        .byte $0E,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $20,$01,$6F
        .byte $09,$03,$6E
        .byte $15,$01,$6F
        .byte $2E,$02,$70
        .byte $09,$02,$71
        .byte $09,$04,$72
        .byte $2E,$02,$70
        .byte $12,$01,$6F
        .byte $12,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0C,$03,$6E
        .byte $1B,$01,$6F
        .byte $2E,$02,$70
        .byte $0C,$02,$71
        .byte $0C,$04,$72
        .byte $2E,$02,$70
        .byte $1A,$01,$6F
        .byte $1B,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $0D,$03,$6E
        .byte $1E,$01,$6F
        .byte $2E,$02,$70
        .byte $0D,$02,$71
        .byte $0D,$04,$72
        .byte $2E,$02,$70
        .byte $1B,$01,$6F
        .byte $1E,$01,$6F
        .byte $0D,$03,$6E
        .byte $1E,$01,$6F
        .byte $2E,$02,$70
        .byte $0D,$02,$71
        .byte $0D,$04,$72
        .byte $2E,$02,$70
        .byte $1B,$01,$6F
        .byte $1E,$01,$6F
        .byte $0E,$03,$6E
        .byte $20,$01,$6F
        .byte $2E,$02,$70
        .byte $0E,$02,$71
        .byte $0E,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $20,$01,$6F
        .byte $09,$03,$6E
        .byte $15,$01,$6F
        .byte $2E,$02,$70
        .byte $09,$02,$71
        .byte $09,$04,$72
        .byte $2E,$02,$70
        .byte $12,$01,$6F
        .byte $12,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0C,$03,$6E
        .byte $1B,$01,$6F
        .byte $2E,$02,$70
        .byte $0C,$02,$71
        .byte $0C,$04,$72
        .byte $2E,$02,$70
        .byte $1A,$01,$6F
        .byte $1B,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0C,$03,$6E
        .byte $1B,$01,$6F
        .byte $2E,$02,$70
        .byte $0C,$02,$71
        .byte $0C,$04,$72
        .byte $2E,$02,$70
        .byte $1A,$01,$6F
        .byte $1B,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $06,$03,$6E
        .byte $14,$01,$6F
        .byte $2E,$02,$70
        .byte $06,$02,$71
        .byte $06,$04,$72
        .byte $2E,$02,$70
        .byte $12,$01,$6F
        .byte $14,$01,$6F
        .byte $06,$03,$6E
        .byte $14,$01,$6F
        .byte $2E,$02,$70
        .byte $06,$02,$71
        .byte $06,$04,$72
        .byte $2E,$02,$70
        .byte $12,$01,$6F
        .byte $14,$01,$6F
        .byte $0E,$03,$6E
        .byte $20,$01,$6F
        .byte $2E,$02,$70
        .byte $0E,$02,$71
        .byte $0E,$04,$72
        .byte $2E,$02,$70
        .byte $1D,$01,$6F
        .byte $20,$01,$6F
        .byte $0E,$03,$6E
        .byte $20,$01,$6F
        .byte $2E,$02,$70
        .byte $0E,$02,$71
        .byte $0E,$04,$72
        .byte $2E,$02,$70
        .byte $1D,$01,$6F
        .byte $20,$01,$6F
        .byte $06,$03,$6E
        .byte $14,$01,$6F
        .byte $2E,$02,$70
        .byte $06,$02,$71
        .byte $06,$04,$72
        .byte $2E,$02,$70
        .byte $12,$01,$6F
        .byte $14,$01,$6F
        .byte $06,$03,$6E
        .byte $14,$01,$6F
        .byte $2E,$02,$70
        .byte $06,$02,$71
        .byte $06,$04,$72
        .byte $2E,$02,$70
        .byte $12,$01,$6F
        .byte $14,$01,$6F
        .byte $0E,$03,$6E
        .byte $20,$01,$6F
        .byte $2E,$02,$70
        .byte $0E,$02,$71
        .byte $0E,$04,$72
        .byte $2E,$02,$70
        .byte $1D,$01,$6F
        .byte $20,$01,$6F
        .byte $0E,$03,$6E
        .byte $20,$01,$6F
        .byte $2E,$02,$70
        .byte $0E,$02,$71
        .byte $0E,$04,$72
        .byte $2E,$02,$70
        .byte $1D,$01,$6F
        .byte $20,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $02,$03,$6E
        .byte $12,$01,$6F
        .byte $2E,$02,$70
        .byte $02,$02,$71
        .byte $02,$04,$72
        .byte $2E,$02,$70
        .byte $10,$01,$6F
        .byte $12,$01,$6F
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $2A,$02,$1B
        .byte $20,$01,$73
        .byte $23,$02,$74
        .byte $20,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $33,$02,$19
        .byte $2A,$02,$1B
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $0A,$03,$6E
        .byte $1A,$01,$6F
        .byte $2E,$02,$70
        .byte $0A,$02,$71
        .byte $0A,$04,$72
        .byte $2E,$02,$70
        .byte $15,$01,$6F
        .byte $1A,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$02,$70
        .byte $1E,$01,$6F
        .byte $21,$01,$6F
        .byte $10,$03,$6E
        .byte $21,$01,$6F
        .byte $2E,$02,$70
        .byte $10,$02,$71
        .byte $10,$04,$72
        .byte $2E,$01,$75
        .byte $23,$01,$73
        .byte $23,$01,$73
        .byte $23,$01,$76
        .byte $FF
