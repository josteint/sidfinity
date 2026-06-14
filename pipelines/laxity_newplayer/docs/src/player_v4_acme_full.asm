;;; ----------------------------------------
;;; SOURCE: CheeseCutter player_v4.acme
;;; Obtained from: local read-only checkout at
;;;   /home/jtr/sidfinity/tmp/dmc_hunt/CheeseCutter/src/c64/player_v4.acme
;;; Repository: https://github.com/theyamo/CheeseCutter (GPL)
;;; Version: CheeseCutter 2.10  ("cc4.07")
;;; Author: "CCUTTER 2.x musicplayer by abad / Based on JCH NP 21.G4 by Laxity/VIB"
;;; fetch_date: 2026-06-14
;;; reliability: PRIMARY (verbatim copy of real 6502 source, 1764 lines)
;;; ----------------------------------------
;;; This file is a verbatim copy stored here for reference.
;;; See cluster_np21_effect_routines.md for the annotated analysis.
;;; ----------------------------------------

;;; CCUTTER 2.x musicplayer by abad
;;; Based on JCH NP 21.G4 by Laxity/VIB
;;; ----------------------------------------
!ifdef ZREG {
} else {
ZREG		= $fb
}
FALSE		= 0
TRUE		= 1
EXPORT		= FALSE				; if TRUE, editor specific code will be left out
MULTISPEED	= TRUE				; support for multispeed playback
INSNO		= 48				; number of instruments used
CIA_VALUE	= $4cc7				; for multispeed
MULTIPLIER	= 1				; for multispeed
BASEADDRESS	= $1000
;;; ----------------------------------------
;;; instr table enums
;;; ----------------------------------------
INS_AD		= 0				;
INS_SR		= 1 * INSNO
INS_HR		= 2 * INSNO			; $x0 = HR type, $0x arp delay count
INS_4		= 3 * INSNO			; HR waveform
INS_FLTP	= 4 * INSNO			;
INS_PULSP	= 5 * INSNO			;
INS_7		= 6 * INSNO			;
INS_ARP		= 7 * INSNO
;;; ----------------------------------------
;;; assembly conditionals
;;; ----------------------------------------
INCLUDE_CMD_SLUP	= TRUE
INCLUDE_CMD_SLDOWN	= TRUE
INCLUDE_CMD_VIBR	= TRUE
INCLUDE_CMD_PORTA	= TRUE
INCLUDE_CMD_SET_ADSR	= TRUE
INCLUDE_CMD_SET_OFFSET	= TRUE
INCLUDE_CMD_SET_LOVIB	= TRUE
INCLUDE_CMD_SET_WAVE	= FALSE
INCLUDE_SEQ_SET_PULSE	= TRUE
INCLUDE_SEQ_SET_CHORD	= TRUE
INCLUDE_SEQ_SET_ATT	= TRUE
INCLUDE_SEQ_SET_DEC	= TRUE
INCLUDE_SEQ_SET_SUS	= TRUE
INCLUDE_SEQ_SET_REL	= TRUE
INCLUDE_SEQ_SET_SPEED	= TRUE
INCLUDE_SEQ_SET_VOL	= TRUE
INCLUDE_DIRECT_PULSE    = TRUE
INCLUDE_VIBRAFEEL	= TRUE
INCLUDE_BREAKSPEED	= TRUE
INCLUDE_CHORD		= TRUE
INCLUDE_FILTER		= TRUE
INCLUDE_SYNC		= TRUE
USE_MDRIVER		= FALSE
;;; ----------------------------------------
;;; new effect commands
;;; ----------------------------------------
CMD_SLIDE_UP	= $00
CMD_SLIDE_DOWN	= $01
CMD_VIBRATO	= $02
CMD_SET_OFFSET	= $03
CMD_SET_ADSR	= $04
CMD_SET_LOVIB	= $05
CMD_SET_WAVE	= $06
CMD_PORTAMENTO	= $07
CMD_STOP	= $08				;stop portamento/slide
;;; ----------------------------------------
SUPERHIGH = CMD_SET_OFFSET

;;; [... editor-only regions $e00, $f000, $f800 omitted for brevity ...]
;;; See full source at tmp/dmc_hunt/CheeseCutter/src/c64/player_v4.acme

;;; ----------------------------------------
;;; MAIN PLAYER BODY -- all lines present
;;; ----------------------------------------

		 *= BASEADDRESS		; $1000

init		jmp subinit
play		jmp subplay
mplay		jmp submplay
sync		!8 0

;---------------------------------------
subinit		asl
		asl
		asl
		tay
		ldx #0
		stx speedsub
		stx sync
subinit0	lda songsets,y
		sta twraplo,x
		iny
		lda songsets,y
		sta twraphi,x
		iny
		inx
		cpx #3
		bne subinit0
		lda songsets,y			;set song speed
		sta speed
		ldx #2
subinit1	lda songsets+1,y
		and bits,x
		sta voicon,x
		lda twraplo,x
		sta tracklo,x
		lda twraphi,x
		sta trackhi,x
		lda #1
		sta newseq,x
		dex
		bpl subinit1
subinit3	lda #1
		sta state
		rts

;;; ----------------------------------------
;;; multispeed extra play
;;; ----------------------------------------
submplay	lda #$40
		sta state
		ldx #2
		jmp syncskip

;;; ----------------------------------------
;;; regular play call
;;; ----------------------------------------
subplay
		lda state
		beq run

		lda #2
		sta speedcnt

		ldx #(clrlast-clrfirst)
		lda #0
subinit4	dex
		sta clrfirst,x
		bne subinit4

		;; reset synchronization

		ldx #2
subinit5	lda #2
		sta synccnt,x			; HR allowed
		lda #$fe
		sta tsync,x 			; sync done
		dex
		bpl subinit5
		lda #$0f
		sta volume
		lda #0
		sta filter
		sta bandpass
		lda #$f0
		sta $d417
		lda #0
		sta state
		rts

run		dec speedcnt
		bpl speeddone
		lda speed
		cmp #2
		bpl speedok
speedalt	ldy speedsub
		lda chord,y
                bpl nowrap
                ldy #0
                sty speedsub
                lda chord,y
nowrap          inc speedsub
		sta playspeed
		cmp #2
		bpl speedok
		lda #2
speedok		sta speedcnt
speeddone
;---------------------------------------
		ldx #2
main0		lda voicon,x
		bne trackon
		jmp next
trackon		inc synccnt,x
		lda speedcnt
		beq jupdseq
		cmp #1
		beq updtrack
		jmp updsound
jupdseq		jmp updseq
;---------------------------------------
updtrack	lda newseq,x
		beq skiptrack
		sec
		sbc #1
		sta seqcnt,x
		lda #0
		sta newseq,x
		tay
		lda tracklo,x
		sta ZREG
		lda trackhi,x
		sta ZREG+1
		lda (ZREG),y
		bpl trk02

		cmp #$80			; get transpose value
		beq skiptrans
		sbc #$a0
		sta shtrans2,x
skiptrans	inc tracklo,x
		bne trk01
		inc trackhi,x
trk01		iny
		lda (ZREG),y
trk02		sta curseq,x
		iny
		lda (ZREG),y
		cmp #$f0
		bcc trk03

		pha
		iny
		lda (ZREG),y
		clc
		adc twraplo,x
		sta tracklo,x

		pla
		and #$07
		adc twraphi,x			; song wrap
		sta trackhi,x
		jmp updsound

trk03		inc tracklo,x
		bne skiptrack
		inc trackhi,x
skiptrack	jmp updsound
;---------------------------------------
updseq		dec durcnt,x
		bmi nextnote
		jmp updsound
nextnote	ldy curseq,x
		lda seqlo,y
		sta ZREG
		lda seqhi,y
		sta ZREG+1
		lda #2
		sta tsync,x
getseq		ldy seqcnt,x
seqnext		lda (ZREG),y
		cmp #$c0
		bcs command
		cmp #$60-1			; command coming up?
		bcc nocmdbyt
		sbc #$60
		bpl nottie
		inc tienote,x			; $5f = flag tienote
		iny
		jmp seqnext

nottie		pha				; store note value
		iny
		lda (ZREG),y			; fetch sequence command
		beq skipcmd
		sta shsuper,x
		inc newcmdflag,x
skipcmd		pla

nocmdbyt	sta shnote,x			; check for rest & gate flags
		cmp #3
		bcs sequpdtrans
settie		inc tienote,x
		jmp seqdone

command		cmp #$f0
		bmi notdur
setdur		and #$0f
		sta duration,x
		iny
		jmp seqnext

notdur		sbc #$c0-1
		sta shinst,x
		inc newinsflag,x
		iny
		jmp seqnext

sequpdtrans	lda shtrans2,x
		sta shtrans,x
seqdone		iny
		beq seqsetflag
		tya
		sta seqcnt,x
		lda (ZREG),y
		cmp #$bf			;seq end mark
		bne noteos
seqsetflag	inc newseq,x
noteos
		lda duration,x
		sta durcnt,x
		lda newcmdflag,x
		beq snotporta

		;; Check for super commands that should be parsed immediately

		ldy shsuper,x
		cpy #$40
		bpl updsound

		lda cmd1,y
		cmp #CMD_PORTAMENTO
		bne snotporta

		lda cmd2,y
		and #$0f
		sta portahi,x
		lda cmd3,y
		sta portalo,x

		lda #$81
		sta effstate,x
		lda #0
		sta newcmdflag,x
		jmp updsound
snotporta

;;; ----------------------------------------
;;; sound work
;;; ----------------------------------------
updsound	lda #0
		sta hardon,x
		lda tsync,x
		bpl dosync
		jmp syncskip

dosync		dec tsync,x

		lda tienote,x
		beq syncnottied
		jmp syncskip

syncnottied	lda tsync,x
		cmp #1
		bne syncgate

		lda synccnt,x			; hard restart possible?
		cmp #2
		bmi syncnohr

		ldy shinst,x			; use hard restart?
		lda inst+INS_HR,y
		bpl syncnohr
		and #$20
		bne laxhr

		;; Hard restart: set AD from global cmd2 row0

		lda cmd2			;Set adsr for HR -- cmd2 row 0 = HR-AD
		sta ad,x
laxhr		lda inst+INS_7,y		; HR-SR from inst byte6
		sta sr,x
syncnohr	lda #$fe
		sta gate,x
		jmp dowave			;only update wavetable

syncgate	cmp #$ff
		beq syncgateon
		jmp syncskip

syncgateon	lda newinsflag,x
		beq checknote

		ldy shinst,x
		lda inst,y			;Store AD of instrument in shadow
		sta shad,x
		lda inst+INS_SR,y
		sta shsr,x

		lda effstate,x			;don't reset porta
		bmi checknote

		lda #0
		sta effstate,x

checknote	lda shtrans,x			;set transpose to current
		sta trans,x

		lda shnote,x
		clc				;get real (transposed) value of the note
		adc trans,x
		sta notereal,x

		ldy effstate,x			;skip if portamento
		bmi skipsetfrq
		tay
		lda freqtable_lo,y
		sta plo,x
		lda freqtable_hi,y
		sta phi,x

		txa
		sta shfreqlo,x
		lda #0
		sta shfreqhi,x
skipsetfrq	ldy shinst,x
		lda inst+INS_ARP,y		;set wave pos
		sta wavepos,x
		lda shad,x			;set ADSR
		sta ad,x
		lda shsr,x
		sta sr,x

		lda inst+INS_PULSP,y		;set the pulse
		beq setflt
		bpl skippdirect
		and #$0f
		sta pulsehi,x
                lda #0
		sta pulselo,x
		jmp pulsdirset
skippdirect	asl
		asl
pulsdirset	sta pulsenxt,x			;pointer
		lda #0
		sta pulsecnt,x

setflt
		lda inst+INS_FLTP,y
		beq filterdone			;no filter reset
skipcutdirect	asl
		asl
                sta filtnxt
		lda #0
		sta filtcnt
filterdone

scmddone	lda #0
		sta newinsflag,x
		sta chordvalue,x
		lda #$80
		sta chordtpos,x

		lda inst+INS_HR,y		;set wave timer
		and #$0f
		sta wavetime,x
		lda #0
		sta wavecnt,x

		lda inst+INS_HR,y
		and #$c0			;Check for soft restart
		cmp #$40
		beq wavenotoff

		lda inst+INS_4,y
		ora #1
		sta waveform,x
		inc hardon,x
wavenotoff	lda #$ff			;Gate on
		sta gate,x

		lda #$00			;Reset sync
		sta synccnt,x
		ldy effstate,x
		bmi noeffreset
		sta effstate,x
noeffreset	jmp checksuper

syncskip
;;; ----------------------------------------
;;; pulsework
;;; ----------------------------------------
updatepulse	ldy pulsecur,x
		dec pulsecnt,x
		bpl pulsenotnew

		lda pulsenxt,x
		sta pulsecur,x
		tay
		lda pulstab+2,y
		cmp #$ff
		beq pulseskipset

		sta ZREG
		and #$f0
		sta pulselo,x
		lda ZREG
		and #$0f
		sta pulsehi,x

pulseskipset	lda pulstab+0,y
		and #$7f
		sta pulsecnt,x

		lda pulstab+3,y
		bne pulsenotnxt
		lda pulsenxt,x
		clc
		adc #4
		jmp pulsesetnxt
pulsenotnxt	cmp #$7f
		bne pulsenotstop
		lda #0
		jmp pulsesetnxt
pulsenotstop	asl
		asl
pulsesetnxt	sta pulsenxt,x

pulsenotnew	lda pulstab,y
		bmi pulsesub

		lda pulselo,x
		clc
		adc pulstab+1,y
		sta pulselo,x
		bcc pulsedone
		inc pulsehi,x
		jmp pulsedone

pulsesub	lda pulselo,x
		sec
		sbc pulstab+1,y
		sta pulselo,x
		bcs pulsedone
		dec pulsehi,x
pulsedone

;;; ----------------------------------------
;;; sfx effects dispatch
;;; ----------------------------------------
		lda effstate,x
		bne effdo1
		jmp effdone
effdo1
		cmp #$01
		bne effdo2
effslideup	lda shfreqlo,x
		clc
		adc slidelo,x
		sta shfreqlo,x
		lda shfreqhi,x
		adc slidehi,x
		sta shfreqhi,x
		jmp effdone
effdo2
		cmp #$02
		bne effdo3
effslidedown	lda shfreqlo,x
		sec
		sbc slidelo,x
		sta shfreqlo,x
		lda shfreqhi,x
		sbc slidehi,x
		sta shfreqhi,x
		jmp effdone
effdo3
		cmp #$04
		bne effdo3a
		lda vibraamp,x
		sta ZREG
		lda #0
		asl ZREG
		rol
		asl ZREG
		rol
		sta ZREG+1
		jmp vibrealadd
effdo3a
		cmp #$03
		beq effvibrato
		jmp effdo4

effvibrato	ldy notereal,x
		sec
		lda freqtable_lo+1,y
		sbc freqtable_lo,y
		sta ZREG
		lda freqtable_hi+1,y
		sbc freqtable_hi+0,y
		sta ZREG+1

		lda vibracor,x
		clc
		adc vibraamp,x
		tay
		lda #0
		sta vibracor,x
viblessamp	dey
		bmi vibadd
		lsr ZREG+1
		ror ZREG
		jmp viblessamp

vibadd
		lda ZREG
		clc
		adc vibrafl,x
		sta ZREG
		lda ZREG+1
		adc vibrafh,x
		sta ZREG+1

		lda vibrafl,x
		clc
		adc vibraflv,x
		sta vibrafl,x
		lda vibrafh,x
		adc #0
		sta vibrafh,x

vibrealadd	lda vibradir,x
		and #1
		bne vibradown

		lda shfreqlo,x
		clc
		adc ZREG
		sta shfreqlo,x
		lda shfreqhi,x
		adc ZREG+1
		sta shfreqhi,x
		jmp vibrapost

vibradown	lda shfreqlo,x
		sec
		sbc ZREG
		sta shfreqlo,x
		lda shfreqhi,x
		sbc ZREG+1
		sta shfreqhi,x

vibrapost	clc
		lda vibracnt,x
		adc #1
		cmp vibrafrq,x
		bcc vibradirok
		inc vibradir,x
		lda #0
vibradirok	sta vibracnt,x
vibradone

effdo4
		cmp #$81			; Portamento
		beq effporta
		jmp effdone

effporta
		ldy notereal,x
		lda freqtable_lo,y
		sta ZREG
		lda freqtable_hi,y
		sta ZREG+1

		lda plo,x
		sec
		sbc ZREG
		sta plo,x

		lda phi,x
		sbc ZREG+1
		sta phi,x

		bmi portaup

		lda plo,x
		sec
		sbc portalo,x
		sta plo,x
		lda phi,x
		sbc portahi,x
		sta phi,x

		bpl portaclc

		jmp portaset

portaup		lda plo,x
		clc
		adc portalo,x
		sta plo,x
		lda phi,x
		adc portahi,x
		sta phi,x

		bmi portaclc

portaset	lda ZREG
		sta plo,x
		lda ZREG+1
		sta phi,x
		jmp portadone
portaclc	lda plo,x
		clc
		adc ZREG
		sta plo,x
		lda phi,x
		adc ZREG+1
		sta phi,x

portadone	ldy notereal,x
		lda plo,x
		sec
		sbc freqtable_lo,y
		sta shfreqlo,x
		lda phi,x
		sbc freqtable_hi,y
		sta shfreqhi,x

effdone
;;; ----------------------------------------
;;; update wavetable
;;; ----------------------------------------
dowave		lda hardon,x
		beq waveok
		jmp wavedone

waveok		dec wavecnt,x
		bpl waveprocess

		lda wavetime,x
		sta wavecnt,x

		ldy wavepos,x
		lda arp1,y
		sta wavetrans,x
		lda arp2,y
		cmp #$10
		bcc waveskip
		cmp #$e0
		bcc wavereg
		and #$0f
wavereg		sta waveform,x
waveskip	lda arp1+1,y
		cmp #$7e
		beq wavestore
		iny
wavenotend	cmp #$7f
		bne wavenotend2
		lda arp2,y
		tay
wavenotend2	lda arp2,y
		beq wavestore
		cmp #$10
		bcs wavestore
		sta wavecnt,x
wavestore	tya
		sta wavepos,x

		ldy chordtpos,x
		bmi chorddone
chordinit	lda chord,y
		cmp #$40
		bcc chordnotneg
		ora #$80
chordnotneg	sta chordvalue,x
		inc chordtpos,x
		lda chord+1,y
		bpl chorddone
		and #$7f
		sta chordtpos,x
chorddone

waveprocess	lda wavetrans,x
		bpl wavenotabs
waveabs		and #$7f
		tay
		lda freqtable_lo,y
		sta freqlo,x
		lda freqtable_hi,y
		sta freqhi,x
		jmp wavedone
wavenotabs	clc
		adc notereal,x
		adc chordvalue,x
		tay
		lda freqtable_lo,y
		clc
		adc shfreqlo,x
		sta freqlo,x
		lda freqtable_hi,y
		adc shfreqhi,x
		sta freqhi,x

wavedone
;;; ----------------------------------------
checksuper	lda tsync,x
		cmp #$ff
		beq supersync
		jmp superdone
supersync	lda newcmdflag,x
		bne superparse
		jmp superdone

superparse	lda #0
		sta newcmdflag,x

superparse2	ldy shsuper,x
		cpy #$40
		bcs *+5
		jmp iscmd
		tya
		cmp #$60
		bcs notpulse

		and #$1f
		asl
		asl
		sta pulsenxt,x
		lda #0
		sta pulsecnt,x
		jmp superdone

notpulse
		cmp #$80
		bcs notfilt

		and #$1f
		asl
		asl
		sta filtnxt
		lda #0
		sta filtcnt
		jmp superdone

notfilt
		cmp #$a0
		bcs notchord
		and #$1f
		tay
		lda chordindex,y
		sta chordtpos,x
		jmp superdone

notchord
		cmp #$b0
		bcs notatt

		asl
		asl
		asl
		asl
		sta ZREG
		lda ad,x
		and #$0f
		ora ZREG
		sta ad,x
		jmp superdone

notatt
		cmp #$c0
		bcs notdec

		and #$0f
		sta ZREG
		lda ad,x
		and #$f0
		ora ZREG
		sta ad,x
		jmp superdone

notdec
		cmp #$d0
		bcs notsus

		asl
		asl
		asl
		asl
		sta ZREG
		lda sr,x
		and #$0f
		ora ZREG
		sta sr,x
		jmp superdone

notsus
		cmp #$e0
		bcs notrel

		and #$0f
		sta ZREG
		lda sr,x
		and #$f0
		ora ZREG
		sta sr,x
		jmp superdone

notrel
		cmp #$f0
		bcs notvol

		and #$0f
		sta volume
		jmp superdone

notvol
		and #$0f
		bne notsync
		inc sync
		jmp superdone
notsync
		sta speed
		cmp #2
		bcs notvol2
                lda #1
                sta speedsub
		lda chord
notvol2		sta playspeed
		sta speedcnt
		dec speedcnt
		jmp superdone

;;; ----------------------------------------
;;; process a command table entry
;;; ----------------------------------------
iscmd		lda cmd2,y
		sta ZREG
		lda cmd1,y
		sta ZREG+1
		cmp #SUPERHIGH
		bcc superlow
		jmp superhigh

superlow
		cmp #0
		bne snotslide1
		lda ZREG
		sta slidehi,x
		lda cmd3,y
		sta slidelo,x
		lda #1
		sta effstate,x
		jmp superdone

snotslide1
		cmp #CMD_SLIDE_DOWN
		bne snotslide2
		lda ZREG
		sta slidehi,x
		lda cmd3,y
		sta slidelo,x
		lda #2
		sta effstate,x
		jmp superdone

snotslide2
		cmp #CMD_VIBRATO
		bne snotvibrato

		lda #3
		sta effstate,x

		lda ZREG
		and #$0f
		sta vibraflv,x
		lda cmd3,y
		and #$0f
		sta vibraamp,x
		lda cmd3,y
		lsr
		lsr
		lsr
		lsr
		clc
		adc #1
		sta vibrafrq,x
		lsr
		bcc novibcor
		inc vibracor,x			;Correction
novibcor	sta vibracnt,x
		lda #0
		sta vibradir,x
		sta vibrafl,x
		sta vibrafh,x

snotvibrato	jmp superdone

superhigh
		cmp #CMD_SET_OFFSET
		bne snotoffset

		lda cmd2,y
		sta shfreqhi,x
		lda cmd3,y
		sta shfreqlo,x
		jmp superdone

snotoffset
		cmp #CMD_SET_ADSR
		bne snotattdec

		lda cmd2,y
		sta ad,x
		lda cmd3,y
		sta sr,x
		jmp superdone

snotattdec
		cmp #CMD_SET_LOVIB
		bne snotlovib
		lda #4
		sta effstate,x
		lda cmd2,y
		sta vibrafrq,x
		lsr
		sta vibracnt,x
		lda cmd3,y
		sta vibraamp,x
		lda #0
		sta vibradir,x

snotlovib
		; CMD_SET_WAVE = $06 disabled (INCLUDE_CMD_SET_WAVE=FALSE)

		cmp #CMD_STOP
		bne snotstop
		lda #0
		sta effstate,x
snotstop

superdone
;;; ----------------------------------------
setsid		ldy voice,x
		lda freqlo,x
		sta $d400,y
		lda freqhi,x
		sta $d401,y
		lda sr,x
		sta $d406,y
		lda ad,x
		sta $d405,y
		lda pulselo,x
		sta $d402,y
		lda pulsehi,x
		sta $d403,y
		lda waveform,x
		and gate,x
		sta $d404,y
;;; ----------------------------------------
		bit state
		bvc *+5
		jmp next

		;; check tie & super
		lda tsync,x
		cmp #$ff
		beq postsync
		jmp skippostsync
postsync	dec tsync,x

		lda tienote,x
		bne tiednote
		jmp next

tiednote	lda shtrans,x
		sta trans,x

		lda shnote,x
		beq tiestore
		cmp #3
		bcc setgatestat

		clc
		adc trans,x
		sta notereal,x

		ldy effstate,x
		bmi tieclear

		lda #0
		sta shfreqlo,x
		sta shfreqhi,x
		sta effstate,x
skiptiefrq	jmp tiestore

setgatestat	tay
		lda gatestat-1,y
		sta gate,x
tieclear	lda #0
tiestore	sta tienote,x

skippostsync

;---------------------------------------
next		dex
		bmi maindone
		bit state
                bpl *+5
		jmp updsound
                bvs *+5
		jmp main0
		jmp syncskip

maindone
                lda #0
		sta state
;;; ----------------------------------------
;;; filter routine  (feb '12: sweeps now 10-bit)
;;; ----------------------------------------
		dec filtcnt
		bpl filtnotnew
		lda filtnxt
filtstart	sta filtcur
		tay
		lda filttab,y		;byte A = duration or bandpass
		bpl filtsetcnt
		and #$70
		sta bandpass
		lda filttab+1,y
		sta $d417
		lda #0
filtsetcnt	sta filtcnt

		lda filttab+1,y
		and #3
		asl
		sta filtadd+1
		lda filttab+1,y
		cmp #$80
		ror
		cmp #$80
		ror
		sta filtadd

filtjump	lda filttab+3,y			; check jump value
		bne filtnotnxt
		lda filtnxt
		clc
		adc #4
		jmp filtsetnxt
filtnotnxt	cmp #$7f
		bne filtnotstop
		lda #0
		jmp filtsetnxt
filtnotstop	asl
		asl
filtsetnxt	sta filtnxt

 		lda filttab+2,y
 		cmp #$ff
 		beq filtnotset
 		sta filter
 		lda #0
 		sta filtlo

filtnotset
		jmp filterskip

filtnotnew	lda filtadd+1
		clc
		adc filtlo
		cmp #8
		and #7
		sta filtlo
		lda filter
		adc filtadd
		sta filter

filterskip	lda filtlo
		sta $d415
		lda filter
		sta $d416

		lda volume
		ora bandpass
		sta $d418

		rts

;---------------------------------------
freqtable_lo
		!8 $16,$27,$38,$4b,$5f,$73
		!8 $8a,$a1,$ba,$d4,$f0,$0e
		; [... 96 entries total, 8 octaves x 12 semitones ...]
freqtable_hi
		!8 $01,$01,$01,$01,$01,$01
		; [... 96 entries total ...]

;---------------------------------------
; State variable layout (relative to clrfirst)
voicon		!8 1,1,1
state		!8 0
bits		!8 %00000001,%00000010,%00000100
gatestat	!8 $fe,$ff
voice		!8 0,7,14

tracklo/hi	; track pointers
twraplo/hi	; track wrap pointers
speed		; current song speed
speedcnt	; speed countdown
playspeed	; displayed speed
speedsub	; breakspeed index
newseq		; per-voice new-sequence flags
volume		; master volume -> $d418

clrfirst:
newinsflag	; per-voice instrument-changed flag
newcmdflag	; per-voice command-pending flag
hardon		; per-voice: 1 = new note hard gate-on this frame
duration	; per-voice row duration (from $fX seq bytes)
durcnt		; per-voice duration countdown
tsync		; per-voice sync state machine ($fe=done, $ff=new, countdown 2..0)
synccnt		; per-voice frames-since-note (HR guard)
tienote		; per-voice tie-note flag
notereal	; per-voice transposed note value
effstate	; per-voice effect: 0=none,1=slup,2=sldown,3=hifivibr,4=lovibr,$81=porta
shtrans/shnote/shinst/shsuper/shad/shsr
shfreqlo/hi	; per-voice frequency offset accumulator
freqlo/hi	; per-voice final frequency -> $d400/$d401
trans		; per-voice current transpose
gate		; per-voice gate mask ($ff=on, $fe=off)
curseq		; per-voice current sequence number
seqcnt		; per-voice sequence byte position
bandpass/filter/filtcnt/filtcur/filtnxt/filtadd/filtlo
vibracnt/vibradir/vibraamp/vibrafrq  ; vibrato (both types)
vibracor/vibrafl/vibrafh/vibraflv    ; hi-fi vibrato only
slidelo/slidehi                      ; slide
pulsecur/pulsenxt/pulsecnt/pulselo/pulsehi
ad/sr/waveform
wavetrans/wavecnt/wavepos/wavetime
chordtpos/chordvalue
portahi/portalo/plo/phi
clrlast:
