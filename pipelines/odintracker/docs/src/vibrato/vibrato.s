; 1 table for each possible vibrato depth.
; Each table contains 1/4th of a 64 byte sine wave.
; Total 256 bytes.

; Table for vibrato amplitude $00.
        .byte   0,   0,   0,   0,   0,   0,   0,   0
        .byte   0,   0,   0,   0,   0,   0,   0,   0
; Table for vibrato amplitude $10. ($11, actually.)
        .byte   0,   2,   3,   5,   7,   8,   9,  11
        .byte  12,  13,  14,  15,  16,  16,  17,  17
; Table for vibrato amplitude $20. ($22, actually.)
        .byte   0,   3,   7,  10,  13,  16,  19,  22
        .byte  24,  26,  28,  30,  31,  33,  33,  34
; Table for vibrato amplitude $30. ($33, actually.)
        .byte   0,   5,  10,  15,  20,  24,  28,  32
        .byte  36,  39,  42,  45,  47,  49,  50,  51
; Table for vibrato amplitude $40. ($44, actually.)
        .byte   0,   7,  13,  20,  26,  32,  38,  43
        .byte  48,  53,  57,  60,  63,  65,  67,  68
; Table for vibrato amplitude $50. ($55, actually.)
        .byte   0,   8,  17,  25,  33,  40,  47,  54
        .byte  60,  66,  71,  75,  79,  81,  83,  85
; Table for vibrato amplitude $60. ($66, actually.)
        .byte   0,  10,  20,  30,  39,  48,  57,  65
        .byte  72,  79,  85,  90,  94,  98, 100, 102
; Table for vibrato amplitude $70. ($77, actually.)
        .byte   0,  12,  23,  35,  46,  56,  66,  75
        .byte  84,  92,  99, 105, 110, 114, 117, 118
; Table for vibrato amplitude $80. ($88, actually.)
        .byte   0,  13,  27,  39,  52,  64,  76,  86
        .byte  96, 105, 113, 120, 126, 130, 133, 135
; Table for vibrato amplitude $90. ($99, actually.)
        .byte   0,  15,  30,  44,  59,  72,  85,  97
        .byte 108, 118, 127, 135, 141, 146, 150, 152
; Table for vibrato amplitude $a0. ($aa, actually.)
        .byte   0,  17,  33,  49,  65,  80,  94, 108
        .byte 120, 131, 141, 150, 157, 163, 167, 169
; Table for vibrato amplitude $b0. ($bb, actually.)
        .byte   0,  18,  36,  54,  72,  88, 104, 119
        .byte 132, 145, 155, 165, 173, 179, 183, 186
; Table for vibrato amplitude $c0. ($cc, actually.)
        .byte   0,  20,  40,  59,  78,  96, 113, 129
        .byte 144, 158, 170, 180, 188, 195, 200, 203
; Table for vibrato amplitude $d0. ($dd, actually.)
        .byte   0,  22,  43,  64,  85, 104, 123, 140
        .byte 156, 171, 184, 195, 204, 211, 217, 220
; Table for vibrato amplitude $e0. ($ee, actually.)
        .byte   0,  23,  46,  69,  91, 112, 132, 151
        .byte 168, 184, 198, 210, 220, 228, 233, 237
; Table for vibrato amplitude $f0. ($ff, actually.)
        .byte   0,  25,  50,  74,  98, 120, 142, 162
        .byte 180, 197, 212, 225, 236, 244, 250, 254
