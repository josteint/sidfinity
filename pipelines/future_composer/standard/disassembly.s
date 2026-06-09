; ============================================================================
; STANDARD ("vanilla") FUTURE COMPOSER PLAYER
; ============================================================================
; Representative: hvsc84/MUSICIANS/C/Carter/Jarre_2.sid (load/init $1800)
;
; THIS IS THE DOMINANT FC PLAYER: fingerprinting (tools/fc_fingerprint.py)
; shows 3673 / 4024 HVSC FutureComposer SIDs (≈91%) share this exact player
; (relocation-invariant opcode skeleton). Migrating this one player covers the
; bulk of the FC catalogue. (Cyb II / Hawkeye / Adrenalin engine A are larger
; CUSTOM demoscene variants — outliers, not this family.)
;
; Per the CORE TENET we do NOT reproduce this code — the existing FC composer
; emits our own engine. This disasm exists to give the EXTRACT the data-table
; addresses (below); semantics are then verified via the write-log.
;
; Load $1800   Init $1800 (JMP $2108: JSR $20D9 setup + silence-clear $D400-17)
;              Play $1806
; Auto-traced 1449 reachable code bytes.
;
; DATA-TABLE ADDRESS MAP (at load $1800; relocates with load for other members):
;   freq table         lo $1D64  hi $1DC4   (96 entries — canonical FC table)
;   instrument records $2188     (8 bytes/rec, id<<3; +2=AD +3=SR +4=.. PW etc.)
;   pattern pointers   $1EA7     (2-byte interleaved lo/hi, indexed pattern*2)
;   sequence/orderlist ptrs lo $1EA1 / hi $1EA4   (3 entries, per voice)
;   d4point (voice→SID off)  $211E   (0/7/14)   stored live at $2156
;   speed ctr $2173   speed cmp $211D   play-state $2174 (0=run,1=?,2=halt)
;
; SEQUENCE STREAM (read via ($fb),y, ptr from $1EA1/$1EA4):
;   $FE end · $FF loop · bit7 set → transpose (&$1F → $214F,x)
;   bit6 set → soundtranspose (&$3F → $2176,x) · else pattern id → $1EA7 ptr
; PATTERN STREAM (read via ($fd),y, ptr from $1EA7): note + cmd bytes; note +
;   transpose ($214F,x) indexes the freq table $1D64/$1DC4. Instrument # from a
;   pattern cmd → $2133,x → <<3 → instrument record at $2188.
;
; EFFECT TABLES (the $1E** data region, standard FC effect layout):
;   $1E32  4-byte effect (sel $2142&3; gated by $2155&$40) → $2179
;   $1E3E/$40/$42/$44  program-ptr pairs (sel $2153&$0F; SMC'd at $1CAF..$1CB8)
;   $1E66 / $1E76  per-frame wave/arp tables (sel by frame ctr $2142,x)
;   $1E89  FILTER program, 12 bytes, read ($f9),y y=$06-$0B → $D416/$D417
;   $1E95  PULSE program, 4 bytes/prog (sel (n&7)<<2) → PW accum → $D402/$D403
;
; SCOPE FINDING (2026-06-09): these are the STANDARD FC effect formats and they
; differ STRUCTURALLY from the Tel variants (Cyb II/Hawkeye) the current
; extract/composer were built for — e.g. pulse is 4-byte here vs 8-byte there;
; filter is a 12-byte ($f9),y program. So migrating this player is NOT
; config-only: it needs standard-FC-format decoders (extract) + emitters
; (composer). First build (config addresses only, aux=0) verified: extract OK,
; play stream diverges because the instruments use fx1/2/3 but the standard
; effect formats aren't yet implemented. This reorients the FC composer around
; the DOMINANT format (91% of HVSC FC) rather than the custom outliers.
;
; STATUS: disassembled + FULLY address-mapped incl. effect tables (2026-06-09).
; NEXT: implement standard-FC effect decoders/emitters (pulse $1E95 4-byte,
; filter $1E89 12-byte, wave/arp $1E66/$1E76, $1E3E-$44 program ptrs), iterate
; write-log on Jarre_2, then relocation so one config covers the 3673 family.
; ============================================================================

; ======= init: =======
init:
    $1800: 4C 08 21   JMP $2108        ; → L_2108
; ----- data gap $1803-$1805 (3 bytes) -----

; ======= play: =======
play:
    $1806: AD 74 21   LDA $2174     
    $1809: C9 02      CMP #$02      
    $180B: F0 07      BEQ $1814        ; → L_1814
    $180D: C9 01      CMP #$01      
    $180F: D0 19      BNE $182a        ; → L_182A
    $1811: 4C E8 20   JMP $20e8        ; → L_20E8
L_1814:
    $1814: 60         RTS           
; ----- data gap $1815-$1829 (21 bytes) -----

L_182A:
    $182A: EE 42 21   INC $2142     
    $182D: EE 43 21   INC $2143     
    $1830: EE 44 21   INC $2144     
    $1833: A9 1F      LDA #$1f      
    $1835: 8D 18 D4   STA $d418      ;VOL
    $1838: A2 02      LDX #$02      
    $183A: CE 73 21   DEC $2173     
    $183D: 10 06      BPL $1845        ; → L_1845
    $183F: AD 1D 21   LDA $211d     
    $1842: 8D 73 21   STA $2173     
L_1845:
    $1845: 2C 20 D0   BIT $d020     
    $1848: 86 FF      STX $ff       
    $184A: BD 1E 21   LDA $211e,x   
    $184D: 8D 56 21   STA $2156     
    $1850: A8         TAY           
    $1851: AD 73 21   LDA $2173     
    $1854: CD 1D 21   CMP $211d     
    $1857: D0 12      BNE $186b        ; → L_186B
    $1859: BD A1 1E   LDA $1ea1,x   
    $185C: 85 FB      STA $fb       
    $185E: BD A4 1E   LDA $1ea4,x   
    $1861: 85 FC      STA $fc       
    $1863: DE 27 21   DEC $2127,x   
    $1866: 30 06      BMI $186e        ; → L_186E
    $1868: 4C FA 19   JMP $19fa        ; → L_19FA
L_186B:
    $186B: 4C 0A 1A   JMP $1a0a        ; → L_1A0A
L_186E:
    $186E: BC 21 21   LDY $2121,x   
    $1871: B1 FB      LDA ($fb),y   
    $1873: C9 FE      CMP #$fe      
    $1875: F0 15      BEQ $188c        ; → L_188C
    $1877: C9 FF      CMP #$ff      
    $1879: D0 19      BNE $1894        ; → L_1894
    $187B: A9 00      LDA #$00      
    $187D: 9D 27 21   STA $2127,x   
    $1880: 9D 21 21   STA $2121,x   
    $1883: 9D 24 21   STA $2124,x   
    $1886: 8D 72 21   STA $2172     
    $1889: 4C 6E 18   JMP $186e        ; → L_186E
L_188C:
    $188C: A9 02      LDA #$02      
    $188E: 8D 74 21   STA $2174     
    $1891: 4C 0B 21   JMP $210b        ; → L_210B
L_1894:
    $1894: 8D 67 21   STA $2167     
    $1897: 29 80      AND #$80      
    $1899: F0 0E      BEQ $18a9        ; → L_18A9
    $189B: AD 67 21   LDA $2167     
    $189E: 29 1F      AND #$1f      
    $18A0: 9D 4F 21   STA $214f,x   
    $18A3: FE 21 21   INC $2121,x   
    $18A6: 4C 6E 18   JMP $186e        ; → L_186E
L_18A9:
    $18A9: AD 67 21   LDA $2167     
    $18AC: 29 40      AND #$40      
    $18AE: F0 0E      BEQ $18be        ; → L_18BE
    $18B0: AD 67 21   LDA $2167     
    $18B3: 29 3F      AND #$3f      
    $18B5: 9D 76 21   STA $2176,x   
    $18B8: FE 21 21   INC $2121,x   
    $18BB: 4C 6E 18   JMP $186e        ; → L_186E
L_18BE:
    $18BE: AD 67 21   LDA $2167     
    $18C1: 0A         ASL a         
    $18C2: A8         TAY           
    $18C3: B9 A7 1E   LDA $1ea7,y   
    $18C6: 85 FD      STA $fd       
    $18C8: B9 A8 1E   LDA $1ea8,y   
    $18CB: 85 FE      STA $fe       
    $18CD: A9 00      LDA #$00      
    $18CF: 9D 3F 21   STA $213f,x   
    $18D2: BC 24 21   LDY $2124,x   
    $18D5: 9D 42 21   STA $2142,x   
    $18D8: A9 03      LDA #$03      
    $18DA: 9D 61 21   STA $2161,x   
L_18DD:
    $18DD: B1 FD      LDA ($fd),y   
    $18DF: 85 F8      STA $f8       
    $18E1: 29 F0      AND #$f0      
    $18E3: C9 F0      CMP #$f0      
    $18E5: D0 10      BNE $18f7        ; → L_18F7
    $18E7: A9 01      LDA #$01      
    $18E9: 9D 80 21   STA $2180,x   
    $18EC: FE 24 21   INC $2124,x   
    $18EF: C8         INY           
    $18F0: B1 FD      LDA ($fd),y   
    $18F2: 85 F8      STA $f8       
    $18F4: 4C 57 19   JMP $1957        ; → L_1957
L_18F7:
    $18F7: A9 00      LDA #$00      
    $18F9: 9D 80 21   STA $2180,x   
    $18FC: A5 F8      LDA $f8       
    $18FE: 29 F0      AND #$f0      
    $1900: C9 E0      CMP #$e0      
    $1902: D0 2C      BNE $1930        ; → L_1930
    $1904: A5 F8      LDA $f8       
    $1906: 29 01      AND #$01      
    $1908: 18         CLC           
    $1909: 69 01      ADC #$01      
    $190B: 9D 3F 21   STA $213f,x   
    $190E: A5 F8      LDA $f8       
    $1910: 29 0E      AND #$0e      
    $1912: 4A         LSR a         
    $1913: 8D 65 21   STA $2165     
    $1916: FE 24 21   INC $2124,x   
    $1919: C8         INY           
    $191A: B1 FD      LDA ($fd),y   
    $191C: 48         PHA           
    $191D: 29 F0      AND #$f0      
    $191F: 8D 64 21   STA $2164     
    $1922: 68         PLA           
    $1923: 29 0F      AND #$0f      
    $1925: 8D F8 1A   STA $1af8     
    $1928: FE 24 21   INC $2124,x   
    $192B: C8         INY           
    $192C: B1 FD      LDA ($fd),y   
    $192E: 85 F8      STA $f8       
L_1930:
    $1930: A5 F8      LDA $f8       
    $1932: 29 E0      AND #$e0      
    $1934: C9 C0      CMP #$c0      
    $1936: D0 0A      BNE $1942        ; → L_1942
    $1938: A5 F8      LDA $f8       
    $193A: 29 1F      AND #$1f      
    $193C: 9D 33 21   STA $2133,x   
    $193F: 20 ED 19   JSR $19ed        ; → sub_19ED
L_1942:
    $1942: A5 F8      LDA $f8       
    $1944: 29 C0      AND #$c0      
    $1946: C9 80      CMP #$80      
    $1948: D0 0D      BNE $1957        ; → L_1957
    $194A: A5 F8      LDA $f8       
    $194C: 29 3F      AND #$3f      
    $194E: 9D 2A 21   STA $212a,x   
    $1951: 20 ED 19   JSR $19ed        ; → sub_19ED
    $1954: 4C DD 18   JMP $18dd        ; → L_18DD
L_1957:
    $1957: BD 2A 21   LDA $212a,x   
    $195A: 9D 27 21   STA $2127,x   
    $195D: A5 F8      LDA $f8       
    $195F: 18         CLC           
    $1960: 7D 4F 21   ADC $214f,x   
    $1963: 9D 30 21   STA $2130,x   
    $1966: A8         TAY           
    $1967: B9 64 1D   LDA $1d64,y   
    $196A: 48         PHA           
    $196B: B9 C4 1D   LDA $1dc4,y   
    $196E: AC 56 21   LDY $2156     
    $1971: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1974: 9D 36 21   STA $2136,x   
    $1977: 9D 39 21   STA $2139,x   
    $197A: 68         PLA           
    $197B: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $197E: 9D 3C 21   STA $213c,x   
    $1981: BD 80 21   LDA $2180,x   
    $1984: D0 46      BNE $19cc        ; → L_19CC
    $1986: BD 33 21   LDA $2133,x   
    $1989: 0A         ASL a         
    $198A: 0A         ASL a         
    $198B: 0A         ASL a         
    $198C: AA         TAX           
    $198D: 8E 52 21   STX $2152     
    $1990: BD 8A 21   LDA $218a,x   
    $1993: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1996: BD 8B 21   LDA $218b,x   
    $1999: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $199C: BD 8C 21   LDA $218c,x   
    $199F: 48         PHA           
    $19A0: BD 88 21   LDA $2188,x   
    $19A3: 48         PHA           
    $19A4: BD 89 21   LDA $2189,x   
    $19A7: A6 FF      LDX $ff       
    $19A9: 9D 2D 21   STA $212d,x   
    $19AC: 9D 79 21   STA $2179,x   
    $19AF: A9 00      LDA #$00      
    $19B1: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $19B4: 9D 45 21   STA $2145,x   
    $19B7: 68         PLA           
    $19B8: 9D 4B 21   STA $214b,x   
    $19BB: 29 0F      AND #$0f      
    $19BD: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $19C0: 9D 48 21   STA $2148,x   
    $19C3: A9 01      LDA #$01      
    $19C5: 9D 6F 21   STA $216f,x   
    $19C8: 68         PLA           
    $19C9: 9D 6C 21   STA $216c,x   
L_19CC:
    $19CC: FE 24 21   INC $2124,x   
    $19CF: BC 24 21   LDY $2124,x   
    $19D2: B1 FD      LDA ($fd),y   
    $19D4: C9 FF      CMP #$ff      
    $19D6: D0 12      BNE $19ea        ; → L_19EA
L_19D8:
    $19D8: A9 00      LDA #$00      
    $19DA: 9D 24 21   STA $2124,x   
    $19DD: BD 76 21   LDA $2176,x   
    $19E0: F0 05      BEQ $19e7        ; → L_19E7
    $19E2: DE 76 21   DEC $2176,x   
    $19E5: 10 03      BPL $19ea        ; → L_19EA
L_19E7:
    $19E7: FE 21 21   INC $2121,x   
L_19EA:
    $19EA: 4C 52 1D   JMP $1d52        ; → L_1D52
sub_19ED:
    $19ED: FE 24 21   INC $2124,x   
    $19F0: C8         INY           
    $19F1: B1 FD      LDA ($fd),y   
    $19F3: C9 FF      CMP #$ff      
    $19F5: F0 E1      BEQ $19d8        ; → L_19D8
    $19F7: 85 F8      STA $f8       
    $19F9: 60         RTS           
L_19FA:
    $19FA: AC 56 21   LDY $2156     
    $19FD: BD 42 21   LDA $2142,x   
    $1A00: F0 08      BEQ $1a0a        ; → L_1A0A
    $1A02: BD 2D 21   LDA $212d,x   
    $1A05: 29 FE      AND #$fe      
    $1A07: 9D 79 21   STA $2179,x   
L_1A0A:
    $1A0A: BD 33 21   LDA $2133,x   
    $1A0D: 0A         ASL a         
    $1A0E: 0A         ASL a         
    $1A0F: 0A         ASL a         
    $1A10: A8         TAY           
    $1A11: B9 8D 21   LDA $218d,y   
    $1A14: 8D 53 21   STA $2153     
    $1A17: B9 8E 21   LDA $218e,y   
    $1A1A: 8D 54 21   STA $2154     
    $1A1D: B9 8F 21   LDA $218f,y   
    $1A20: 8D 55 21   STA $2155     
    $1A23: 29 04      AND #$04      
    $1A25: D0 0C      BNE $1a33        ; → L_1A33
    $1A27: AD 55 21   LDA $2155     
    $1A2A: 29 10      AND #$10      
    $1A2C: D0 05      BNE $1a33        ; → L_1A33
    $1A2E: AD 53 21   LDA $2153     
    $1A31: D0 03      BNE $1a36        ; → L_1A36
L_1A33:
    $1A33: 4C 30 20   JMP $2030        ; → L_2030
L_1A36:
    $1A36: 48         PHA           
    $1A37: 29 78      AND #$78      
    $1A39: 4A         LSR a         
    $1A3A: 4A         LSR a         
    $1A3B: 4A         LSR a         
    $1A3C: 9D 58 21   STA $2158,x   
    $1A3F: 68         PLA           
    $1A40: 29 07      AND #$07      
    $1A42: 8D 57 21   STA $2157     
    $1A45: BD 5B 21   LDA $215b,x   
    $1A48: F0 0A      BEQ $1a54        ; → L_1A54
    $1A4A: DE 5E 21   DEC $215e,x   
    $1A4D: D0 19      BNE $1a68        ; → L_1A68
    $1A4F: FE 5B 21   INC $215b,x   
    $1A52: 10 14      BPL $1a68        ; → L_1A68
L_1A54:
    $1A54: FE 5E 21   INC $215e,x   
    $1A57: BD 58 21   LDA $2158,x   
    $1A5A: DD 5E 21   CMP $215e,x   
    $1A5D: B0 09      BCS $1a68        ; → L_1A68
    $1A5F: 9D 5E 21   STA $215e,x   
    $1A62: DE 5B 21   DEC $215b,x   
    $1A65: DE 5E 21   DEC $215e,x   
L_1A68:
    $1A68: BD 30 21   LDA $2130,x   
    $1A6B: A8         TAY           
    $1A6C: B9 65 1D   LDA $1d65,y   
    $1A6F: 38         SEC           
    $1A70: F9 64 1D   SBC $1d64,y   
    $1A73: 8D 7F 21   STA $217f     
    $1A76: B9 C5 1D   LDA $1dc5,y   
    $1A79: F9 C4 1D   SBC $1dc4,y   
    $1A7C: 7D 42 21   ADC $2142,x   
    $1A7F: 4A         LSR a         
L_1A80:
    $1A80: CE 57 21   DEC $2157     
    $1A83: 30 07      BMI $1a8c        ; → L_1A8C
    $1A85: 4A         LSR a         
    $1A86: 6E 7F 21   ROR $217f     
    $1A89: 4C 80 1A   JMP $1a80        ; → L_1A80
L_1A8C:
    $1A8C: 8D 7E 21   STA $217e     
    $1A8F: B9 64 1D   LDA $1d64,y   
    $1A92: 8D 7C 21   STA $217c     
    $1A95: B9 C4 1D   LDA $1dc4,y   
    $1A98: 8D 7D 21   STA $217d     
    $1A9B: BD 58 21   LDA $2158,x   
    $1A9E: 4A         LSR a         
    $1A9F: A8         TAY           
L_1AA0:
    $1AA0: 88         DEY           
    $1AA1: 30 16      BMI $1ab9        ; → L_1AB9
    $1AA3: 38         SEC           
    $1AA4: AD 7C 21   LDA $217c     
    $1AA7: ED 7F 21   SBC $217f     
    $1AAA: 8D 7C 21   STA $217c     
    $1AAD: AD 7D 21   LDA $217d     
    $1AB0: ED 7E 21   SBC $217e     
    $1AB3: 8D 7D 21   STA $217d     
    $1AB6: 4C A0 1A   JMP $1aa0        ; → L_1AA0
L_1AB9:
    $1AB9: BD 42 21   LDA $2142,x   
    $1ABC: C9 04      CMP #$04      
    $1ABE: 90 2B      BCC $1aeb        ; → L_1AEB
    $1AC0: BC 5E 21   LDY $215e,x   
L_1AC3:
    $1AC3: 88         DEY           
    $1AC4: 30 16      BMI $1adc        ; → L_1ADC
    $1AC6: 18         CLC           
    $1AC7: AD 7C 21   LDA $217c     
    $1ACA: 6D 7F 21   ADC $217f     
    $1ACD: 8D 7C 21   STA $217c     
    $1AD0: AD 7D 21   LDA $217d     
    $1AD3: 6D 7E 21   ADC $217e     
    $1AD6: 8D 7D 21   STA $217d     
    $1AD9: 4C C3 1A   JMP $1ac3        ; → L_1AC3
L_1ADC:
    $1ADC: AC 56 21   LDY $2156     
    $1ADF: AD 7C 21   LDA $217c     
    $1AE2: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1AE5: AD 7D 21   LDA $217d     
    $1AE8: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1AEB:
    $1AEB: A6 FF      LDX $ff       
    $1AED: AC 56 21   LDY $2156     
    $1AF0: BD 2A 21   LDA $212a,x   
    $1AF3: 38         SEC           
    $1AF4: FD 27 21   SBC $2127,x   
    $1AF7: C9 01      CMP #$01      
    $1AF9: 90 46      BCC $1b41        ; → L_1B41
    $1AFB: BD 3F 21   LDA $213f,x   
    $1AFE: F0 41      BEQ $1b41        ; → L_1B41
    $1B00: 29 03      AND #$03      
    $1B02: C9 01      CMP #$01      
    $1B04: F0 1F      BEQ $1b25        ; → L_1B25
    $1B06: AD 64 21   LDA $2164     
    $1B09: 38         SEC           
    $1B0A: BD 3C 21   LDA $213c,x   
    $1B0D: ED 64 21   SBC $2164     
    $1B10: 9D 3C 21   STA $213c,x   
    $1B13: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1B16: BD 36 21   LDA $2136,x   
    $1B19: ED 65 21   SBC $2165     
    $1B1C: 9D 36 21   STA $2136,x   
    $1B1F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1B22: 4C 41 1B   JMP $1b41        ; → L_1B41
L_1B25:
    $1B25: AD 64 21   LDA $2164     
    $1B28: 18         CLC           
    $1B29: BD 3C 21   LDA $213c,x   
    $1B2C: 6D 64 21   ADC $2164     
    $1B2F: 9D 3C 21   STA $213c,x   
    $1B32: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1B35: BD 36 21   LDA $2136,x   
    $1B38: 6D 65 21   ADC $2165     
    $1B3B: 9D 36 21   STA $2136,x   
    $1B3E: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1B41:
    $1B41: AD 54 21   LDA $2154     
    $1B44: F0 6C      BEQ $1bb2        ; → L_1BB2
    $1B46: 29 07      AND #$07      
    $1B48: A8         TAY           
    $1B49: 88         DEY           
    $1B4A: 98         TYA           
    $1B4B: 0A         ASL a         
    $1B4C: 0A         ASL a         
    $1B4D: A8         TAY           
    $1B4E: B9 95 1E   LDA $1e95,y   
    $1B51: DD 42 21   CMP $2142,x   
    $1B54: 90 03      BCC $1b59        ; → L_1B59
    $1B56: 4C 63 1B   JMP $1b63        ; → L_1B63
L_1B59:
    $1B59: C8         INY           
    $1B5A: C8         INY           
    $1B5B: B9 95 1E   LDA $1e95,y   
    $1B5E: DD 42 21   CMP $2142,x   
    $1B61: 90 0A      BCC $1b6d        ; → L_1B6D
L_1B63:
    $1B63: C8         INY           
    $1B64: B9 95 1E   LDA $1e95,y   
    $1B67: 8D 4E 21   STA $214e     
    $1B6A: 4C 75 1B   JMP $1b75        ; → L_1B75
L_1B6D:
    $1B6D: AD 54 21   LDA $2154     
    $1B70: 29 FC      AND #$fc      
    $1B72: 8D 4E 21   STA $214e     
L_1B75:
    $1B75: BD 6F 21   LDA $216f,x   
    $1B78: D0 1D      BNE $1b97        ; → L_1B97
    $1B7A: BD 45 21   LDA $2145,x   
    $1B7D: 38         SEC           
    $1B7E: ED 4E 21   SBC $214e     
    $1B81: 9D 45 21   STA $2145,x   
    $1B84: BD 48 21   LDA $2148,x   
    $1B87: E9 00      SBC #$00      
    $1B89: 9D 48 21   STA $2148,x   
    $1B8C: C9 01      CMP #$01      
    $1B8E: B0 22      BCS $1bb2        ; → L_1BB2
    $1B90: A9 01      LDA #$01      
    $1B92: 9D 6F 21   STA $216f,x   
    $1B95: D0 1B      BNE $1bb2        ; → L_1BB2
L_1B97:
    $1B97: BD 45 21   LDA $2145,x   
    $1B9A: 18         CLC           
    $1B9B: 6D 4E 21   ADC $214e     
    $1B9E: 9D 45 21   STA $2145,x   
    $1BA1: BD 48 21   LDA $2148,x   
    $1BA4: 69 00      ADC #$00      
    $1BA6: 9D 48 21   STA $2148,x   
    $1BA9: C9 0F      CMP #$0f      
    $1BAB: 90 05      BCC $1bb2        ; → L_1BB2
    $1BAD: A9 00      LDA #$00      
    $1BAF: 9D 6F 21   STA $216f,x   
L_1BB2:
    $1BB2: A9 00      LDA #$00      
    $1BB4: 8D D4 1B   STA $1bd4     
    $1BB7: BD 4B 21   LDA $214b,x   
    $1BBA: 29 80      AND #$80      
    $1BBC: F0 0C      BEQ $1bca        ; → L_1BCA
    $1BBE: BD 42 21   LDA $2142,x   
    $1BC1: 29 01      AND #$01      
    $1BC3: F0 05      BEQ $1bca        ; → L_1BCA
    $1BC5: A9 B0      LDA #$b0      
    $1BC7: 8D D4 1B   STA $1bd4     
L_1BCA:
    $1BCA: A6 FF      LDX $ff       
    $1BCC: AC 56 21   LDY $2156     
    $1BCF: BD 45 21   LDA $2145,x   
    $1BD2: 18         CLC           
    $1BD3: 69 00      ADC #$00      
    $1BD5: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $1BD8: BD 48 21   LDA $2148,x   
    $1BDB: 69 00      ADC #$00      
    $1BDD: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $1BE0: AD 55 21   LDA $2155     
    $1BE3: 29 40      AND #$40      
    $1BE5: F0 14      BEQ $1bfb        ; → L_1BFB
    $1BE7: A6 FF      LDX $ff       
    $1BE9: BD 42 21   LDA $2142,x   
    $1BEC: C9 03      CMP #$03      
    $1BEE: 90 0B      BCC $1bfb        ; → L_1BFB
    $1BF0: 29 03      AND #$03      
    $1BF2: AA         TAX           
    $1BF3: BD 32 1E   LDA $1e32,x   
    $1BF6: A6 FF      LDX $ff       
    $1BF8: 9D 79 21   STA $2179,x   
L_1BFB:
    $1BFB: 8C 67 21   STY $2167     
    $1BFE: AD 55 21   LDA $2155     
    $1C01: 29 01      AND #$01      
    $1C03: F0 2A      BEQ $1c2f        ; → L_1C2F
    $1C05: A6 FF      LDX $ff       
    $1C07: 8E 75 21   STX $2175     
    $1C0A: A9 89      LDA #$89      
    $1C0C: 85 F9      STA $f9       
    $1C0E: A9 1E      LDA #$1e      
    $1C10: 85 FA      STA $fa       
    $1C12: A6 FF      LDX $ff       
    $1C14: BD 42 21   LDA $2142,x   
    $1C17: A0 0B      LDY #$0b      
    $1C19: D1 F9      CMP ($f9),y   
    $1C1B: B0 33      BCS $1c50        ; → L_1C50
    $1C1D: A0 0A      LDY #$0a      
L_1C1F:
    $1C1F: D1 F9      CMP ($f9),y   
    $1C21: B0 38      BCS $1c5b        ; → L_1C5B
    $1C23: 88         DEY           
    $1C24: C0 06      CPY #$06      
    $1C26: D0 F7      BNE $1c1f        ; → L_1C1F
    $1C28: D1 F9      CMP ($f9),y   
    $1C2A: B0 06      BCS $1c32        ; → L_1C32
    $1C2C: 4C 7B 1C   JMP $1c7b        ; → L_1C7B
L_1C2F:
    $1C2F: 4C 6A 1C   JMP $1c6a        ; → L_1C6A
L_1C32:
    $1C32: A5 FF      LDA $ff       
    $1C34: 0A         ASL a         
    $1C35: D0 03      BNE $1c3a        ; → L_1C3A
    $1C37: 18         CLC           
    $1C38: 69 01      ADC #$01      
L_1C3A:
    $1C3A: 8D 68 21   STA $2168     
    $1C3D: AE 72 21   LDX $2172     
    $1C40: 8A         TXA           
    $1C41: 2D 68 21   AND $2168     
    $1C44: D0 08      BNE $1c4e        ; → L_1C4E
    $1C46: 8A         TXA           
    $1C47: 18         CLC           
    $1C48: 6D 68 21   ADC $2168     
    $1C4B: 8D 17 D4   STA $d417      ;RES_FILT
L_1C4E:
    $1C4E: A0 06      LDY #$06      
L_1C50:
    $1C50: 88         DEY           
    $1C51: 88         DEY           
    $1C52: 88         DEY           
    $1C53: 88         DEY           
    $1C54: 88         DEY           
    $1C55: 88         DEY           
    $1C56: B1 F9      LDA ($f9),y   
    $1C58: 4C 73 1C   JMP $1c73        ; → L_1C73
L_1C5B:
    $1C5B: 88         DEY           
    $1C5C: 88         DEY           
    $1C5D: 88         DEY           
    $1C5E: 88         DEY           
    $1C5F: 88         DEY           
    $1C60: 88         DEY           
    $1C61: BD 69 21   LDA $2169,x   
    $1C64: 18         CLC           
    $1C65: 71 F9      ADC ($f9),y   
    $1C67: 4C 73 1C   JMP $1c73        ; → L_1C73
L_1C6A:
    $1C6A: A5 FF      LDA $ff       
    $1C6C: CD 75 21   CMP $2175     
    $1C6F: D0 0A      BNE $1c7b        ; → L_1C7B
    $1C71: A9 FF      LDA #$ff      
L_1C73:
    $1C73: A6 FF      LDX $ff       
    $1C75: 9D 69 21   STA $2169,x   
    $1C78: 8D 16 D4   STA $d416      ;FC_HI
L_1C7B:
    $1C7B: AC 67 21   LDY $2167     
    $1C7E: AD 55 21   LDA $2155     
    $1C81: 29 10      AND #$10      
    $1C83: F0 5E      BEQ $1ce3        ; → L_1CE3
    $1C85: AD 53 21   LDA $2153     
    $1C88: 29 0F      AND #$0f      
    $1C8A: AA         TAX           
    $1C8B: BD 3E 1E   LDA $1e3e,x   
    $1C8E: 8D AF 1C   STA $1caf     
    $1C91: BD 40 1E   LDA $1e40,x   
    $1C94: 8D B0 1C   STA $1cb0     
    $1C97: BD 42 1E   LDA $1e42,x   
    $1C9A: 8D B7 1C   STA $1cb7     
    $1C9D: BD 44 1E   LDA $1e44,x   
    $1CA0: 8D B8 1C   STA $1cb8     
    $1CA3: A6 FF      LDX $ff       
    $1CA5: BD 42 21   LDA $2142,x   
    $1CA8: C9 0F      CMP #$0f      
    $1CAA: B0 34      BCS $1ce0        ; → L_1CE0
    $1CAC: AA         TAX           
    $1CAD: CA         DEX           
    $1CAE: BD 76 1E   LDA $1e76,x   
    $1CB1: A4 FF      LDY $ff       
    $1CB3: 99 79 21   STA $2179,y   
    $1CB6: BD 66 1E   LDA $1e66,x   
    $1CB9: 8D 68 21   STA $2168     
    $1CBC: AD 53 21   LDA $2153     
    $1CBF: 29 10      AND #$10      
    $1CC1: F0 0C      BEQ $1ccf        ; → L_1CCF
    $1CC3: A6 FF      LDX $ff       
    $1CC5: BD 30 21   LDA $2130,x   
    $1CC8: 18         CLC           
    $1CC9: 6D 68 21   ADC $2168     
    $1CCC: 4C 42 1D   JMP $1d42        ; → L_1D42
L_1CCF:
    $1CCF: AC 56 21   LDY $2156     
    $1CD2: AD 68 21   LDA $2168     
    $1CD5: 18         CLC           
    $1CD6: 69 0D      ADC #$0d      
    $1CD8: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1CDB: A9 00      LDA #$00      
    $1CDD: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
L_1CE0:
    $1CE0: 4C 52 1D   JMP $1d52        ; → L_1D52
L_1CE3:
    $1CE3: AD 55 21   LDA $2155     
    $1CE6: 29 80      AND #$80      
    $1CE8: F0 34      BEQ $1d1e        ; → L_1D1E
    $1CEA: A6 FF      LDX $ff       
    $1CEC: AC 56 21   LDY $2156     
    $1CEF: BD 42 21   LDA $2142,x   
    $1CF2: C9 02      CMP #$02      
    $1CF4: B0 14      BCS $1d0a        ; → L_1D0A
    $1CF6: A9 48      LDA #$48      
    $1CF8: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1CFB: A9 00      LDA #$00      
    $1CFD: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1D00: A6 FF      LDX $ff       
    $1D02: A9 81      LDA #$81      
    $1D04: 9D 79 21   STA $2179,x   
    $1D07: 4C 52 1D   JMP $1d52        ; → L_1D52
L_1D0A:
    $1D0A: BD 3C 21   LDA $213c,x   
    $1D0D: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1D10: BD 36 21   LDA $2136,x   
    $1D13: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1D16: BD 2D 21   LDA $212d,x   
    $1D19: 29 FE      AND #$fe      
    $1D1B: 9D 79 21   STA $2179,x   
L_1D1E:
    $1D1E: AD 55 21   LDA $2155     
    $1D21: 29 04      AND #$04      
    $1D23: F0 2D      BEQ $1d52        ; → L_1D52
    $1D25: DE 61 21   DEC $2161,x   
    $1D28: 10 05      BPL $1d2f        ; → L_1D2F
    $1D2A: A9 02      LDA #$02      
    $1D2C: 9D 61 21   STA $2161,x   
L_1D2F:
    $1D2F: A6 FF      LDX $ff       
    $1D31: BD 61 21   LDA $2161,x   
    $1D34: AA         TAX           
    $1D35: BD 86 1E   LDA $1e86,x   
    $1D38: 85 41      STA $41       
    $1D3A: A6 FF      LDX $ff       
    $1D3C: BD 30 21   LDA $2130,x   
    $1D3F: 18         CLC           
    $1D40: 65 41      ADC $41       
L_1D42:
    $1D42: AA         TAX           
    $1D43: AC 56 21   LDY $2156     
    $1D46: BD 64 1D   LDA $1d64,x   
    $1D49: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1D4C: BD C4 1D   LDA $1dc4,x   
    $1D4F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1D52:
    $1D52: A6 FF      LDX $ff       
    $1D54: AC 56 21   LDY $2156     
    $1D57: BD 79 21   LDA $2179,x   
    $1D5A: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1D5D: CA         DEX           
    $1D5E: 30 03      BMI $1d63        ; → L_1D63
    $1D60: 4C 45 18   JMP $1845        ; → L_1845
L_1D63:
    $1D63: 60         RTS           
; ----- data gap $1D64-$202F (716 bytes) -----

L_2030:
    $2030: AD 53 21   LDA $2153     
    $2033: F0 13      BEQ $2048        ; → L_2048
    $2035: 4A         LSR a         
    $2036: 4A         LSR a         
    $2037: 4A         LSR a         
    $2038: 4A         LSR a         
    $2039: AA         TAX           
    $203A: AD 53 21   LDA $2153     
    $203D: 29 0F      AND #$0f      
L_203F:
    $203F: 8D 88 1E   STA $1e88     
    $2042: 8E 87 1E   STX $1e87     
    $2045: 4C EB 1A   JMP $1aeb        ; → L_1AEB
L_2048:
    $2048: A9 18      LDA #$18      
    $204A: A2 0C      LDX #$0c      
    $204C: D0 F1      BNE $203f        ; → L_203F
    $204E: 00         BRK           
; ----- data gap $204F-$20D8 (138 bytes) -----

sub_20D9:
    $20D9: A9 00      LDA #$00      
    $20DB: A2 62      LDX #$62      
L_20DD:
    $20DD: 9D 21 21   STA $2121,x   
    $20E0: CA         DEX           
    $20E1: 10 FA      BPL $20dd        ; → L_20DD
    $20E3: A9 B0      LDA #$b0      
    $20E5: 8D 72 21   STA $2172     
L_20E8:
    $20E8: A9 00      LDA #$00      
    $20EA: 8D 42 21   STA $2142     
    $20ED: 8D 43 21   STA $2143     
    $20F0: 8D 44 21   STA $2144     
    $20F3: A2 02      LDX #$02      
L_20F5:
    $20F5: 9D 21 21   STA $2121,x   
    $20F8: 9D 24 21   STA $2124,x   
    $20FB: 9D 27 21   STA $2127,x   
    $20FE: 9D 30 21   STA $2130,x   
    $2101: CA         DEX           
    $2102: 10 F1      BPL $20f5        ; → L_20F5
    $2104: 8D 74 21   STA $2174     
    $2107: 60         RTS           
L_2108:
    $2108: 20 D9 20   JSR $20d9        ; → sub_20D9
L_210B:
    $210B: A2 00      LDX #$00      
    $210D: 8A         TXA           
L_210E:
    $210E: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $2111: E8         INX           
    $2112: E0 18      CPX #$18      
    $2114: D0 F8      BNE $210e        ; → L_210E
    $2116: 60         RTS           
; ----- data gap $2117-$2289 (371 bytes) -----

