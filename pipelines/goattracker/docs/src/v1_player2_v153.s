;-------------------------------------------------------------------------------
; Relocation info for the gamemusic-mode playroutine.
;
; NOTE: This playroutine source code does not fall under the GPL license!
; Use it freely for any purpose, commercial or noncommercial.
;-------------------------------------------------------------------------------

                processor 6502
                org $1000

                dc.b 0                  ;Instrument data size in bytes
                dc.b 0                  ;Wavetable length in bytes / 2
                dc.b 0                  ;Songtable size in bytes / 2
                dc.b 0                  ;Patterntable size in bytes / 2
