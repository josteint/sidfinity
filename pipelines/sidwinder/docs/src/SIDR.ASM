
#define LO(x) (x&$ff)
#define HI(x) (x>>8)

;If you're using the compiled binary version on the Plus/4 and you want to
;include it to your program, you must replace _all occurences of 'oldbase',
;'newbase', 'start' and 'end' in the code, respectively.
;(Or take this file, modify to your particular datas and re-compile it with
;Table Driven Assembler on PC).


#define oldbase $d400                   ;Old SID base address
#define newbase $fd40                   ;New SID base address
#define start $1100                     ;Player code start in memory
#define end $1605                       ;End in memory


        *= $2ffe                        ;Let's quickly generate a load
        .word *+2                       ;address

        lda #LO(start)
        sta $d0
        lda #HI(start)
        sta $d1

loop    ldx #4                          ;5 checked instructions
        ldy #0
        lda ($d0),y
loo2    cmp codes,x                     ;Is it an appropriate code?
        beq found1                      ;Yes!
        dex
        bpl loo2
        bmi notf
found1  ldy #2                          ;Check the address high byte
        lda ($d0),y
        cmp #HI(oldbase)                ;old SID base high
        bne notf                        ;...didn't win.
        dey
        lda ($d0),y
        cmp #LO(oldbase)                ;low byte
        bcc notf                        ;below, not found
        cmp #LO((oldbase+$20))
        bcs notf                        ;Above, get out...
        and #$1f                        ;Found, strip unneeded bits
        ora #LO(newbase)                ;and add new base address low bits
        sta ($d0),y                     ;Store!
        iny
        lda #HI(newbase)                ;Base address high
        sta ($d0),y

notf    inc $d0                         ;check next...
        bne j1
        inc $d1
j1      lda $d0
        cmp #LO(end)
        bne loop
        lda $d1
        cmp #HI(end)
        bne loop
        rts


codes   .byte $8e,$8c,$8d,$9e,$9d       ;stx, sty, sta absolute and
                                        ;sta absolute,x/y

.end
