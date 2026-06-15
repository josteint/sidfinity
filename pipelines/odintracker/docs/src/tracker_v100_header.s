; ======================================
; Odin Tracker 1.00 for C64 by Zed on 15 Feb 2000.
;
; This is the complete source including all data (font, etc) as well.
; Use DASM to compile.
;
; Hacks, unfinished portions are marked with !!!.
;
; Wotan mit uns.
; ======================================

; ======================================
; Memory layout
;
; $0810-$3800     editor code and data
; $3800-$3a00     font
; $3a00-$3fc0       [unused, maybe for some editor hack]
; $3fc0-$4000     sprite cursor
; $4000-$4100     orderlist
; $4100-$4120     song title
; $4120-$4200       [unused, maybe for song info]
; $4200-$4800     patterns
; $4800-$4a00     instruments
; $4a00-$4c00     instrument names
; $4c00-$4d00     wave table
; $4d00-$4e00     arpeggio table
; $4e00-$5000       [unused, maybe for some filter table]
; $5000-$b000     tracks
; $b000-$d000     help text
; ======================================

BASIC           = $0801

EDITOR          = $0810
PLAYER          = $2e00
FONT            = $3800
SPRITE          = $3fc0

; Locations of music data.
ORDERLIST       = $4000         ; 256 bytes for orderlist.
SONGTITLE       = $4100         ; 32 bytes for song title.
PATTERNS        = $4200         ; 256 pattern, 3 track numbers + transpose per pattern, total $600 bytes.
INSTRUMENTS     = $4800         ; 32 instruments, each 16 bytes.
INSTRUMENTNAMES = $4a00         ; 32 instrument names, each 16 bytes.
WAVETABLE       = $4c00         ; 256 bytes for wave table.
ARPEGGIOTABLE   = $4d00         ; 256 bytes for arpeggio table.
TRACKS_BASE     = $5000         ; 128 tracks, each 64*3 bytes.
HELPTEXT        = $b000         ; $2000 bytes for help text.

MAX_ORDERS      = 256
MAX_PATTERS     = 256
MAX_TRACKS      = 128
MAX_INSTRUMENTS = 32
SONGTITLELEN    = 32
INSTRUMENTNAMELEN = 16

; ======================================
; Defines for editor only.
; ======================================

; Kernal data.
status          = $90
shiftflags      = $028d
caseswitch      = $0291

;Kernal routines.
scnkey          = $ff9f
getin           = $ffe4
setnam          = $ffbd
setlfs          = $ffba
load            = $ffd5
save            = $ffd8
chrin           = $ffcf
open            = $ffc0
close           = $ffc3
chkin           = $ffc6
chkout          = $ffc9
ciout           = $ffa8
acptr           = $ffa5
clrchn          = $ffcc
chrout          = $ffd2
plot            = $fff0

; Keycodes returned by getin.
;KEY_                   = $00
;KEY_                   = $01
;KEY_                   = $02
KEY_RUNSTOP             = $03
;KEY_                   = $04
KEY_CTRL_2              = $05
KEY_CTRL_LEFTARROW      = $06
;KEY_                   = $07
;KEY_                   = $08
;KEY_                   = $09
;KEY_                   = $0A
;KEY_                   = $0B
;KEY_                   = $0C
KEY_RETURN              = $0D
;KEY_                   = $0E
;KEY_                   = $0F
;KEY_                   = $10
KEY_DOWN                = $11
KEY_CTRL_9              = $12
KEY_HOME                = $13
KEY_DELETE              = $14
;KEY_                   = $15
;KEY_                   = $16
;KEY_                   = $17
;KEY_                   = $18
;KEY_                   = $19
;KEY_                   = $1A
;KEY_                   = $1B
KEY_CTRL_3              = $1C
KEY_RIGHT               = $1D
KEY_CTRL_6              = $1E
KEY_CTRL_7              = $1F
KEY_SPACE               = $20
KEY_EXCL                = $21
KEY_DOUBLEQUOT          = $22
KEY_HASHMARK            = $23
KEY_DOLLAR              = $24
KEY_PERCENT             = $25
KEY_AMP                 = $26
KEY_QUOT                = $27
KEY_LBRACKET            = $28
KEY_RBRACKET            = $29
KEY_ASTERISK            = $2A
KEY_PLUS                = $2B
KEY_COMMA               = $2C
KEY_MINUS               = $2D
KEY_PERIOD              = $2E
KEY_SLASH               = $2F
KEY_0                   = $30
KEY_1                   = $31
KEY_2                   = $32
KEY_3                   = $33
KEY_4                   = $34
KEY_5                   = $35
KEY_6                   = $36
KEY_7                   = $37
KEY_8                   = $38
KEY_9                   = $39
KEY_COLON               = $3A
KEY_SEMICOLON           = $3B
KEY_LESS                = $3C
KEY_EQUALS              = $3D
KEY_GREATER             = $3E
KEY_QUEST               = $3F
KEY_AT                  = $40                   ; @
KEY_A                   = $41
KEY_B                   = $42
KEY_C                   = $43
KEY_D                   = $44
KEY_E                   = $45
KEY_F                   = $46
KEY_G                   = $47
KEY_H                   = $48
KEY_I                   = $49
KEY_J                   = $4A
KEY_K                   = $4B
KEY_L                   = $4C
KEY_M                   = $4D
KEY_N                   = $4E
KEY_O                   = $4F
KEY_P                   = $50
KEY_Q                   = $51
KEY_R                   = $52
KEY_S                   = $53
KEY_T                   = $54
KEY_U                   = $55
KEY_V                   = $56
KEY_W                   = $57
KEY_X                   = $58
KEY_Y                   = $59
KEY_Z                   = $5A
KEY_LSQRBRACKET         = $5B
KEY_POUND               = $5C
KEY_RSQRBRACKET         = $5D
KEY_UPARROW             = $5E
KEY_LEFTARROW           = $5F
;KEY_                   = $60
;KEY_                   = $61
;KEY_                   = $62
;KEY_                   = $63
;KEY_                   = $64
;KEY_                   = $65
;KEY_                   = $66
;KEY_                   = $67
;KEY_                   = $68
;KEY_                   = $69
;KEY_                   = $6A
;KEY_                   = $6B
;KEY_                   = $6C
;KEY_                   = $6D
;KEY_                   = $6E
;KEY_                   = $6F
;KEY_                   = $70
;KEY_                   = $71
;KEY_                   = $72
;KEY_                   = $73
