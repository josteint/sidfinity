; ======================================
; Part of Odin Tracker 1.13 for C64 by Zed on 17 Apr 2001.
;
; Global constants.
; ======================================

BASIC           = $0801

EDITOR          = $0810
FONT            = $3800
RWDATA          = $3a00         ; Editor's read/write and uninitialized data.
SPRITEHILIGHT   = $3f80         ; Track row highlight sprite.
SPRITECURSOR    = $3fc0         ; Cursor sprite.

; Locations of music data.
ORDERLIST       = $4000         ; 256 bytes for orderlist.
SONGTITLE       = $4100         ; 32 bytes for song title.
PATTERNS        = $4200         ; 256 pattern, 3 track numbers + transpose per pattern, total $600 bytes.
INSTRUMENTS     = $4800         ; 32 instruments, each 16 bytes.
INSTRUMENTNAMES = $4a00         ; 32 instrument names, each 16 bytes.
WAVETABLE       = $4c00         ; 256 bytes for wave table.
ARPEGGIOTABLE   = $4d00         ; 256 bytes for arpeggio table.
FILTERTABLE     = $4e00         ; 256 bytes for filter table.
SONGSTARTTABLE  = $4f00         ; Song start positions.
TRACKS_BASE     = $5000         ; 128 tracks, each 64*3 bytes.
VPLAYER         = $b000         ; Relocatable player.
OPCODELIST      = $bf00         ; Number of bytes for each 6510 instruction.
PLAYER          = $c000         ; Editor's player.
INSTRUMENTBUFFER = $ce00        ; Used when converting instruments from old format.
HELPTEXT        = $d000         ; $3000 bytes for help text.

; Pattern and orderlist are decompiled into these lists for packed tunes.
; These numbers are pretty unimportant, they just have to uniquely identify
; pages for the relocator.
TRACKTRANSPOSES0 = $f000
TRACKPOINTERSLO0 = $f100
TRACKPOINTERSHI0 = $f200
TRACKTRANSPOSES1 = $f300
TRACKPOINTERSLO1 = $f400
TRACKPOINTERSHI1 = $f500
TRACKTRANSPOSES2 = $f600
TRACKPOINTERSLO2 = $f700
TRACKPOINTERSHI2 = $f800

; ======================================
; Defines for editor and player.
; ======================================

MAX_ORDERS      = 256
MAX_PATTERS     = 256
MAX_TRACKS      = 128
MAX_INSTRUMENTS = 32
SONGTITLELEN    = 32
INSTRUMENTLEN   = 16
INSTRUMENTNAMELEN = 16

; Offsets in instrument structure.
INST_AD                 = $00  ; Attack/Decay.
INST_SR                 = $01  ; Sustain/Release.
INST_WAVETABLESTART     = $02  ; Wave table start index .
INST_WAVETABLEEND       = $03  ; Wave table end index.
INST_WAVETABLELOOP      = $04  ; Wave table loop index.
INST_ARPTABLESTART      = $05  ; Arpeggio table start index.
INST_ARPTABLEEND        = $06  ; Arpeggio table end index.
INST_ARPTABLELOOP       = $07  ; Arpeggio table loop index.
INST_VIBDELAY           = $08  ; Number of ticks before starting vibrato.
INST_VIBDEPTH_SPEED     = $09  ; Vibrato speed*$10 + vibrato depth
INST_PULSEWIDTH         = $0a  ; Pulse low/high ratio bits 11..4
INST_PULSESPEED         = $0b  ; Pulse variation speed bits 7..0.
INST_PULSELIMITS        = $0c  ; Pulse variation limit.
                               ;   Low nybble is lower limit's bits 11.8,
                               ;   high nybble is high limit's bits 11.8.
INST_FILTERTABLESTART   = $0d  ; Filter table start index.
INST_FILTERTABLEEND     = $0e  ; Filter table end index.
INST_FILTERTABLELOOP    = $0f  ; Filter table loop index.

INSTRUMENTS_AD                  = 0*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_SR                  = 1*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_WAVETABLESTART      = 2*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_WAVETABLEEND        = 3*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_WAVETABLELOOP       = 4*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_ARPTABLESTART       = 5*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_ARPTABLEEND         = 6*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_ARPTABLELOOP        = 7*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_VIBDELAY            = 8*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_VIBDEPTH_SPEED      = 9*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_PULSEWIDTH          = 10*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_PULSESPEED          = 11*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_PULSELIMITS         = 12*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_FILTERTABLESTART    = 13*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_FILTERTABLEEND      = 14*MAX_INSTRUMENTS+INSTRUMENTS
INSTRUMENTS_FILTERTABLELOOP     = 15*MAX_INSTRUMENTS+INSTRUMENTS


; ======================================
; Player's zeropage.
; ======================================

; Temporary pointers for track, instruments and patterns.
; The player destroys these.
player_trackptr = $fb           ; Temp 16 bit pointer to track.
player_patternptr = $fd         ; Temp 16 bit pointer to pattern.
; Temp 16 bit vibrato and slide adder.
; Never used at the same time as player_patternptr.
player_vibratotemp = player_patternptr
