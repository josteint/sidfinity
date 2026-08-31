; ============================================================================
; Rob Hubbard - Boot Zak v2 (1998 Alpha Flight/Breeze)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc85/MUSICIANS/R/Rayden/Boot_Zak_v2.sid
; Load:   $0812   Init: $0812   Play: $0000
; PSID:   1 subtune(s), default subtune 1
; Binary: $0812-$6A77 (25190 bytes)
;
; Auto-traced 2850 reachable code bytes from init+play.
;
; ============================================================================

; ======= init: =======
init:
    $0812: 78         SEI           
    $0813: A9 01      LDA #$01      
    $0815: 8D 1A D0   STA $d01a     
    $0818: A9 7F      LDA #$7f      
    $081A: 8D 0D DC   STA $dc0d     
    $081D: AD 0D DC   LDA $dc0d     
    $0820: A9 81      LDA #$81      
    $0822: 8D 0D DD   STA $dd0d     
    $0825: AD 0D DD   LDA $dd0d     
    $0828: A9 00      LDA #$00      
    $082A: 8D 0E DD   STA $dd0e     
    $082D: A9 1B      LDA #$1b      
    $082F: 8D 11 D0   STA $d011     
    $0832: A9 32      LDA #$32      
    $0834: A2 00      LDX #$00      
    $0836: A0 0F      LDY #$0f      
    $0838: 8D 12 D0   STA $d012     
    $083B: 8E FA FF   STX $fffa     
    $083E: 8C FB FF   STY $fffb     
    $0841: A9 EE      LDA #$ee      
    $0843: A2 15      LDX #$15      
    $0845: A0 00      LDY #$00      
    $0847: 85 00      STA $00       
    $0849: 86 01      STX $01       
    $084B: 84 02      STY $02       
    $084D: 8C FE FF   STY $fffe     
    $0850: 8C FF FF   STY $ffff     
    $0853: A9 4C      LDA #$4c      
    $0855: A2 00      LDX #$00      
    $0857: A0 20      LDY #$20      
    $0859: 85 03      STA $03       
    $085B: 86 04      STX $04       
    $085D: 84 05      STY $05       
    $085F: EA         NOP           
    $0860: EA         NOP           
    $0861: EA         NOP           
    $0862: EA         NOP           
    $0863: EA         NOP           
    $0864: EA         NOP           
    $0865: EA         NOP           
    $0866: EA         NOP           
    $0867: EA         NOP           
    $0868: EA         NOP           
    $0869: EA         NOP           
    $086A: EA         NOP           
    $086B: EA         NOP           
    $086C: EA         NOP           
    $086D: EA         NOP           
    $086E: EA         NOP           
    $086F: EA         NOP           
    $0870: EA         NOP           
    $0871: EA         NOP           
    $0872: EA         NOP           
    $0873: EA         NOP           
    $0874: EA         NOP           
    $0875: EA         NOP           
    $0876: EA         NOP           
    $0877: EA         NOP           
    $0878: EA         NOP           
    $0879: EA         NOP           
    $087A: EA         NOP           
    $087B: EA         NOP           
    $087C: EA         NOP           
    $087D: EA         NOP           
    $087E: EA         NOP           
    $087F: EA         NOP           
    $0880: EA         NOP           
    $0881: EA         NOP           
    $0882: EA         NOP           
    $0883: EA         NOP           
    $0884: EA         NOP           
    $0885: EA         NOP           
    $0886: EA         NOP           
    $0887: EA         NOP           
    $0888: EA         NOP           
    $0889: EA         NOP           
    $088A: EA         NOP           
    $088B: 86 1B      STX $1b       
    $088D: A9 18      LDA #$18      
    $088F: 85 1C      STA $1c       
    $0891: A9 01      LDA #$01      
    $0893: 85 1A      STA $1a       
    $0895: 85 2A      STA $2a       
    $0897: 8A         TXA           
    $0898: 20 00 10   JSR $1000        ; → sub_1000
    $089B: 20 00 0C   JSR $0c00        ; → sub_0C00
    $089E: A2 00      LDX #$00      
    $08A0: A0 28      LDY #$28      
    $08A2: EA         NOP           
    $08A3: EA         NOP           
    $08A4: EA         NOP           
    $08A5: EA         NOP           
    $08A6: EA         NOP           
    $08A7: EA         NOP           
    $08A8: A2 00      LDX #$00      
    $08AA: A0 2F      LDY #$2f      
    $08AC: EA         NOP           
    $08AD: EA         NOP           
    $08AE: EA         NOP           
    $08AF: EA         NOP           
    $08B0: EA         NOP           
    $08B1: EA         NOP           
    $08B2: EA         NOP           
    $08B3: EA         NOP           
    $08B4: EA         NOP           
    $08B5: EA         NOP           
    $08B6: EA         NOP           
    $08B7: EA         NOP           
    $08B8: EA         NOP           
    $08B9: EA         NOP           
    $08BA: EA         NOP           
    $08BB: EA         NOP           
    $08BC: EA         NOP           
    $08BD: EA         NOP           
    $08BE: EA         NOP           
    $08BF: A9 00      LDA #$00      
    $08C1: 8D A7 02   STA $02a7     
    $08C4: A9 04      LDA #$04      
    $08C6: A2 22      LDX #$22      
    $08C8: A0 00      LDY #$00      
    $08CA: A9 01      LDA #$01      
    $08CC: EA         NOP           
    $08CD: D0 06      BNE $08d5        ; → L_08D5
    $08CF: A9 18      LDA #$18      
    $08D1: A2 25      LDX #$25      
    $08D3: A0 02      LDY #$02      
L_08D5:
    $08D5: 8D 72 20   STA $2072     
    $08D8: 8E 3D 20   STX $203d     
    $08DB: 8C 9B 0C   STY $0c9b     
    $08DE: 58         CLI           
L_08DF:
    $08DF: A9 32      LDA #$32      
L_08E1:
    $08E1: CD 12 D0   CMP $d012     
    $08E4: D0 FB      BNE $08e1        ; → L_08E1
    $08E6: EA         NOP           
    $08E7: EA         NOP           
    $08E8: EA         NOP           
    $08E9: A9 01      LDA #$01      
    $08EB: EA         NOP           
    $08EC: D0 0A      BNE $08f8        ; → L_08F8
    $08EE: EE A7 02   INC $02a7     
    $08F1: AD A7 02   LDA $02a7     
    $08F4: C9 07      CMP #$07      
    $08F6: F0 06      BEQ $08fe        ; → L_08FE
L_08F8:
    $08F8: 20 03 10   JSR $1003        ; → sub_1003
    $08FB: 20 03 0C   JSR $0c03        ; → sub_0C03
L_08FE:
    $08FE: A9 D2      LDA #$d2      
L_0900:
    $0900: CD 12 D0   CMP $d012     
    $0903: B0 FB      BCS $0900        ; → L_0900
    $0905: AD A7 02   LDA $02a7     
    $0908: C9 07      CMP #$07      
    $090A: D0 07      BNE $0913        ; → L_0913
    $090C: A9 00      LDA #$00      
    $090E: 8D A7 02   STA $02a7     
    $0911: F0 0D      BEQ $0920        ; → L_0920
L_0913:
    $0913: A2 00      LDX #$00      
    $0915: 20 91 15   JSR $1591        ; → sub_1591
    $0918: E8         INX           
    $0919: 20 91 15   JSR $1591        ; → sub_1591
    $091C: E8         INX           
    $091D: 20 91 15   JSR $1591        ; → sub_1591
L_0920:
    $0920: EA         NOP           
    $0921: EA         NOP           
    $0922: EA         NOP           
    $0923: A9 00      LDA #$00      
    $0925: F0 B8      BEQ $08df        ; → L_08DF
    $0927: EA         NOP           
    $0928: EA         NOP           
    $0929: EA         NOP           
    $092A: EA         NOP           
    $092B: EA         NOP           
    $092C: EA         NOP           
    $092D: EA         NOP           
    $092E: EA         NOP           
    $092F: EA         NOP           
    $0930: EA         NOP           
    $0931: EA         NOP           
    $0932: EA         NOP           
    $0933: EA         NOP           
    $0934: EA         NOP           
    $0935: EA         NOP           
    $0936: EA         NOP           
    $0937: EA         NOP           
    $0938: EA         NOP           
    $0939: EA         NOP           
    $093A: EA         NOP           
    $093B: EA         NOP           
    $093C: EA         NOP           
    $093D: EA         NOP           
    $093E: EA         NOP           
    $093F: EA         NOP           
    $0940: EA         NOP           
    $0941: EA         NOP           
    $0942: EA         NOP           
    $0943: EA         NOP           
    $0944: EA         NOP           
    $0945: EA         NOP           
    $0946: EA         NOP           
    $0947: EA         NOP           
    $0948: EA         NOP           
    $0949: EA         NOP           
    $094A: EA         NOP           
    $094B: EA         NOP           
    $094C: EA         NOP           
    $094D: EA         NOP           
    $094E: EA         NOP           
    $094F: EA         NOP           
    $0950: EA         NOP           
    $0951: EA         NOP           
    $0952: EA         NOP           
    $0953: EA         NOP           
    $0954: EA         NOP           
    $0955: EA         NOP           
    $0956: EA         NOP           
    $0957: EA         NOP           
    $0958: EA         NOP           
    $0959: EA         NOP           
    $095A: EA         NOP           
    $095B: EA         NOP           
    $095C: EA         NOP           
    $095D: EA         NOP           
    $095E: EA         NOP           
    $095F: EA         NOP           
    $0960: EA         NOP           
    $0961: EA         NOP           
    $0962: EA         NOP           
    $0963: EA         NOP           
    $0964: EA         NOP           
    $0965: EA         NOP           
    $0966: EA         NOP           
    $0967: EA         NOP           
    $0968: EA         NOP           
    $0969: EA         NOP           
    $096A: EA         NOP           
    $096B: EA         NOP           
    $096C: EA         NOP           
    $096D: EA         NOP           
    $096E: EA         NOP           
    $096F: EA         NOP           
    $0970: EA         NOP           
    $0971: EA         NOP           
    $0972: EA         NOP           
    $0973: EA         NOP           
    $0974: EA         NOP           
    $0975: EA         NOP           
    $0976: EA         NOP           
    $0977: EA         NOP           
    $0978: EA         NOP           
    $0979: EA         NOP           
    $097A: EA         NOP           
    $097B: EA         NOP           
    $097C: EA         NOP           
    $097D: EA         NOP           
    $097E: EA         NOP           
    $097F: EA         NOP           
    $0980: EA         NOP           
    $0981: EA         NOP           
    $0982: EA         NOP           
    $0983: EA         NOP           
    $0984: EA         NOP           
    $0985: EA         NOP           
    $0986: EA         NOP           
    $0987: EA         NOP           
    $0988: EA         NOP           
    $0989: EA         NOP           
    $098A: EA         NOP           
    $098B: EA         NOP           
    $098C: EA         NOP           
    $098D: EA         NOP           
    $098E: EA         NOP           
    $098F: EA         NOP           
    $0990: EA         NOP           
    $0991: EA         NOP           
    $0992: EA         NOP           
    $0993: EA         NOP           
    $0994: EA         NOP           
    $0995: EA         NOP           
    $0996: EA         NOP           
    $0997: EA         NOP           
    $0998: EA         NOP           
    $0999: EA         NOP           
    $099A: EA         NOP           
    $099B: EA         NOP           
    $099C: EA         NOP           
    $099D: EA         NOP           
    $099E: EA         NOP           
    $099F: EA         NOP           
    $09A0: EA         NOP           
    $09A1: EA         NOP           
    $09A2: EA         NOP           
    $09A3: EA         NOP           
    $09A4: EA         NOP           
    $09A5: EA         NOP           
    $09A6: EA         NOP           
    $09A7: EA         NOP           
    $09A8: EA         NOP           
    $09A9: EA         NOP           
    $09AA: EA         NOP           
    $09AB: EA         NOP           
    $09AC: EA         NOP           
    $09AD: EA         NOP           
    $09AE: EA         NOP           
    $09AF: EA         NOP           
    $09B0: EA         NOP           
    $09B1: EA         NOP           
    $09B2: EA         NOP           
    $09B3: EA         NOP           
    $09B4: EA         NOP           
    $09B5: EA         NOP           
    $09B6: EA         NOP           
    $09B7: EA         NOP           
    $09B8: EA         NOP           
    $09B9: EA         NOP           
    $09BA: EA         NOP           
    $09BB: EA         NOP           
    $09BC: EA         NOP           
    $09BD: EA         NOP           
    $09BE: EA         NOP           
    $09BF: EA         NOP           
    $09C0: EA         NOP           
    $09C1: EA         NOP           
    $09C2: EA         NOP           
    $09C3: EA         NOP           
    $09C4: EA         NOP           
    $09C5: EA         NOP           
    $09C6: EA         NOP           
    $09C7: EA         NOP           
    $09C8: EA         NOP           
    $09C9: EA         NOP           
    $09CA: EA         NOP           
    $09CB: EA         NOP           
    $09CC: EA         NOP           
    $09CD: EA         NOP           
    $09CE: EA         NOP           
    $09CF: EA         NOP           
    $09D0: EA         NOP           
    $09D1: EA         NOP           
    $09D2: EA         NOP           
    $09D3: EA         NOP           
    $09D4: EA         NOP           
    $09D5: EA         NOP           
    $09D6: EA         NOP           
    $09D7: EA         NOP           
    $09D8: EA         NOP           
    $09D9: EA         NOP           
    $09DA: EA         NOP           
    $09DB: EA         NOP           
    $09DC: EA         NOP           
    $09DD: EA         NOP           
    $09DE: EA         NOP           
    $09DF: EA         NOP           
    $09E0: EA         NOP           
    $09E1: EA         NOP           
    $09E2: EA         NOP           
    $09E3: EA         NOP           
    $09E4: EA         NOP           
    $09E5: EA         NOP           
    $09E6: EA         NOP           
    $09E7: EA         NOP           
    $09E8: EA         NOP           
    $09E9: EA         NOP           
    $09EA: EA         NOP           
    $09EB: EA         NOP           
    $09EC: EA         NOP           
    $09ED: EA         NOP           
    $09EE: EA         NOP           
    $09EF: EA         NOP           
    $09F0: EA         NOP           
    $09F1: EA         NOP           
    $09F2: EA         NOP           
    $09F3: EA         NOP           
    $09F4: EA         NOP           
    $09F5: EA         NOP           
    $09F6: EA         NOP           
    $09F7: EA         NOP           
    $09F8: EA         NOP           
    $09F9: EA         NOP           
    $09FA: EA         NOP           
    $09FB: EA         NOP           
    $09FC: EA         NOP           
    $09FD: EA         NOP           
    $09FE: EA         NOP           
    $09FF: EA         NOP           
    $0A00: EA         NOP           
    $0A01: EA         NOP           
    $0A02: EA         NOP           
    $0A03: EA         NOP           
    $0A04: EA         NOP           
    $0A05: EA         NOP           
    $0A06: EA         NOP           
    $0A07: EA         NOP           
    $0A08: EA         NOP           
    $0A09: EA         NOP           
    $0A0A: EA         NOP           
    $0A0B: EA         NOP           
    $0A0C: EA         NOP           
    $0A0D: EA         NOP           
    $0A0E: EA         NOP           
    $0A0F: EA         NOP           
    $0A10: EA         NOP           
    $0A11: EA         NOP           
    $0A12: EA         NOP           
    $0A13: EA         NOP           
    $0A14: EA         NOP           
    $0A15: EA         NOP           
    $0A16: EA         NOP           
    $0A17: EA         NOP           
    $0A18: EA         NOP           
    $0A19: EA         NOP           
    $0A1A: EA         NOP           
    $0A1B: EA         NOP           
    $0A1C: EA         NOP           
    $0A1D: EA         NOP           
    $0A1E: EA         NOP           
    $0A1F: EA         NOP           
    $0A20: EA         NOP           
    $0A21: EA         NOP           
    $0A22: EA         NOP           
    $0A23: EA         NOP           
    $0A24: EA         NOP           
    $0A25: EA         NOP           
    $0A26: EA         NOP           
    $0A27: EA         NOP           
    $0A28: EA         NOP           
    $0A29: EA         NOP           
    $0A2A: EA         NOP           
    $0A2B: EA         NOP           
    $0A2C: EA         NOP           
    $0A2D: EA         NOP           
    $0A2E: EA         NOP           
    $0A2F: EA         NOP           
    $0A30: EA         NOP           
    $0A31: EA         NOP           
    $0A32: EA         NOP           
    $0A33: EA         NOP           
    $0A34: EA         NOP           
    $0A35: EA         NOP           
    $0A36: EA         NOP           
    $0A37: EA         NOP           
    $0A38: EA         NOP           
    $0A39: EA         NOP           
    $0A3A: EA         NOP           
    $0A3B: EA         NOP           
    $0A3C: EA         NOP           
    $0A3D: EA         NOP           
    $0A3E: EA         NOP           
    $0A3F: EA         NOP           
    $0A40: EA         NOP           
    $0A41: EA         NOP           
    $0A42: EA         NOP           
    $0A43: EA         NOP           
    $0A44: EA         NOP           
    $0A45: EA         NOP           
    $0A46: EA         NOP           
    $0A47: EA         NOP           
    $0A48: EA         NOP           
    $0A49: EA         NOP           
    $0A4A: EA         NOP           
    $0A4B: EA         NOP           
    $0A4C: EA         NOP           
    $0A4D: EA         NOP           
    $0A4E: EA         NOP           
    $0A4F: EA         NOP           
    $0A50: EA         NOP           
    $0A51: EA         NOP           
    $0A52: EA         NOP           
    $0A53: EA         NOP           
    $0A54: EA         NOP           
    $0A55: EA         NOP           
    $0A56: EA         NOP           
    $0A57: EA         NOP           
    $0A58: EA         NOP           
    $0A59: EA         NOP           
    $0A5A: EA         NOP           
    $0A5B: EA         NOP           
    $0A5C: EA         NOP           
    $0A5D: EA         NOP           
    $0A5E: EA         NOP           
    $0A5F: EA         NOP           
    $0A60: EA         NOP           
    $0A61: EA         NOP           
    $0A62: EA         NOP           
    $0A63: EA         NOP           
    $0A64: EA         NOP           
    $0A65: EA         NOP           
    $0A66: EA         NOP           
    $0A67: EA         NOP           
    $0A68: EA         NOP           
    $0A69: EA         NOP           
    $0A6A: EA         NOP           
    $0A6B: EA         NOP           
    $0A6C: EA         NOP           
    $0A6D: EA         NOP           
    $0A6E: EA         NOP           
    $0A6F: EA         NOP           
    $0A70: EA         NOP           
    $0A71: EA         NOP           
    $0A72: EA         NOP           
    $0A73: EA         NOP           
    $0A74: EA         NOP           
    $0A75: EA         NOP           
    $0A76: EA         NOP           
    $0A77: EA         NOP           
    $0A78: EA         NOP           
    $0A79: EA         NOP           
    $0A7A: EA         NOP           
    $0A7B: EA         NOP           
    $0A7C: EA         NOP           
    $0A7D: EA         NOP           
    $0A7E: EA         NOP           
    $0A7F: EA         NOP           
    $0A80: EA         NOP           
    $0A81: EA         NOP           
    $0A82: EA         NOP           
    $0A83: EA         NOP           
    $0A84: EA         NOP           
    $0A85: EA         NOP           
    $0A86: EA         NOP           
    $0A87: EA         NOP           
    $0A88: EA         NOP           
    $0A89: EA         NOP           
    $0A8A: EA         NOP           
    $0A8B: EA         NOP           
    $0A8C: EA         NOP           
    $0A8D: EA         NOP           
    $0A8E: EA         NOP           
    $0A8F: EA         NOP           
    $0A90: EA         NOP           
    $0A91: EA         NOP           
    $0A92: EA         NOP           
    $0A93: EA         NOP           
    $0A94: EA         NOP           
    $0A95: EA         NOP           
    $0A96: EA         NOP           
    $0A97: EA         NOP           
    $0A98: EA         NOP           
    $0A99: EA         NOP           
    $0A9A: EA         NOP           
    $0A9B: EA         NOP           
    $0A9C: EA         NOP           
    $0A9D: EA         NOP           
    $0A9E: EA         NOP           
    $0A9F: EA         NOP           
    $0AA0: EA         NOP           
    $0AA1: EA         NOP           
    $0AA2: EA         NOP           
    $0AA3: EA         NOP           
    $0AA4: EA         NOP           
    $0AA5: EA         NOP           
    $0AA6: EA         NOP           
    $0AA7: EA         NOP           
    $0AA8: EA         NOP           
    $0AA9: EA         NOP           
    $0AAA: EA         NOP           
    $0AAB: EA         NOP           
    $0AAC: EA         NOP           
    $0AAD: EA         NOP           
    $0AAE: EA         NOP           
    $0AAF: EA         NOP           
    $0AB0: EA         NOP           
    $0AB1: EA         NOP           
    $0AB2: EA         NOP           
    $0AB3: EA         NOP           
    $0AB4: EA         NOP           
    $0AB5: EA         NOP           
    $0AB6: EA         NOP           
    $0AB7: EA         NOP           
    $0AB8: EA         NOP           
    $0AB9: EA         NOP           
    $0ABA: EA         NOP           
    $0ABB: EA         NOP           
    $0ABC: EA         NOP           
    $0ABD: EA         NOP           
    $0ABE: EA         NOP           
    $0ABF: EA         NOP           
    $0AC0: EA         NOP           
    $0AC1: EA         NOP           
    $0AC2: EA         NOP           
    $0AC3: EA         NOP           
    $0AC4: EA         NOP           
    $0AC5: EA         NOP           
    $0AC6: EA         NOP           
    $0AC7: EA         NOP           
    $0AC8: EA         NOP           
    $0AC9: EA         NOP           
    $0ACA: EA         NOP           
    $0ACB: EA         NOP           
    $0ACC: EA         NOP           
    $0ACD: EA         NOP           
    $0ACE: EA         NOP           
    $0ACF: EA         NOP           
    $0AD0: EA         NOP           
    $0AD1: EA         NOP           
    $0AD2: EA         NOP           
    $0AD3: EA         NOP           
    $0AD4: EA         NOP           
    $0AD5: EA         NOP           
    $0AD6: EA         NOP           
    $0AD7: EA         NOP           
    $0AD8: EA         NOP           
    $0AD9: EA         NOP           
    $0ADA: EA         NOP           
    $0ADB: EA         NOP           
    $0ADC: EA         NOP           
    $0ADD: EA         NOP           
    $0ADE: EA         NOP           
    $0ADF: EA         NOP           
    $0AE0: EA         NOP           
    $0AE1: EA         NOP           
    $0AE2: EA         NOP           
    $0AE3: EA         NOP           
    $0AE4: EA         NOP           
    $0AE5: EA         NOP           
    $0AE6: EA         NOP           
    $0AE7: EA         NOP           
    $0AE8: EA         NOP           
    $0AE9: EA         NOP           
    $0AEA: EA         NOP           
    $0AEB: EA         NOP           
    $0AEC: EA         NOP           
    $0AED: EA         NOP           
    $0AEE: EA         NOP           
    $0AEF: EA         NOP           
    $0AF0: EA         NOP           
    $0AF1: EA         NOP           
    $0AF2: EA         NOP           
    $0AF3: EA         NOP           
    $0AF4: EA         NOP           
    $0AF5: EA         NOP           
    $0AF6: EA         NOP           
    $0AF7: EA         NOP           
    $0AF8: EA         NOP           
    $0AF9: EA         NOP           
    $0AFA: EA         NOP           
    $0AFB: EA         NOP           
    $0AFC: EA         NOP           
    $0AFD: EA         NOP           
    $0AFE: EA         NOP           
    $0AFF: EA         NOP           
    $0B00: EA         NOP           
    $0B01: EA         NOP           
    $0B02: EA         NOP           
    $0B03: EA         NOP           
    $0B04: EA         NOP           
    $0B05: EA         NOP           
    $0B06: EA         NOP           
    $0B07: EA         NOP           
    $0B08: EA         NOP           
    $0B09: EA         NOP           
    $0B0A: EA         NOP           
    $0B0B: EA         NOP           
    $0B0C: EA         NOP           
    $0B0D: EA         NOP           
    $0B0E: EA         NOP           
    $0B0F: EA         NOP           
    $0B10: EA         NOP           
    $0B11: EA         NOP           
    $0B12: EA         NOP           
    $0B13: EA         NOP           
    $0B14: EA         NOP           
    $0B15: EA         NOP           
    $0B16: EA         NOP           
    $0B17: EA         NOP           
    $0B18: EA         NOP           
    $0B19: EA         NOP           
    $0B1A: EA         NOP           
    $0B1B: EA         NOP           
    $0B1C: EA         NOP           
    $0B1D: EA         NOP           
    $0B1E: EA         NOP           
    $0B1F: EA         NOP           
    $0B20: EA         NOP           
    $0B21: EA         NOP           
    $0B22: EA         NOP           
    $0B23: EA         NOP           
    $0B24: EA         NOP           
    $0B25: EA         NOP           
    $0B26: EA         NOP           
    $0B27: EA         NOP           
    $0B28: EA         NOP           
    $0B29: EA         NOP           
    $0B2A: EA         NOP           
    $0B2B: EA         NOP           
    $0B2C: EA         NOP           
    $0B2D: EA         NOP           
    $0B2E: EA         NOP           
    $0B2F: EA         NOP           
    $0B30: EA         NOP           
    $0B31: EA         NOP           
    $0B32: EA         NOP           
    $0B33: EA         NOP           
    $0B34: EA         NOP           
    $0B35: EA         NOP           
    $0B36: EA         NOP           
    $0B37: EA         NOP           
    $0B38: EA         NOP           
    $0B39: EA         NOP           
    $0B3A: EA         NOP           
    $0B3B: EA         NOP           
    $0B3C: EA         NOP           
    $0B3D: EA         NOP           
    $0B3E: EA         NOP           
    $0B3F: EA         NOP           
    $0B40: EA         NOP           
    $0B41: EA         NOP           
    $0B42: EA         NOP           
    $0B43: EA         NOP           
    $0B44: EA         NOP           
    $0B45: EA         NOP           
    $0B46: EA         NOP           
    $0B47: EA         NOP           
    $0B48: EA         NOP           
    $0B49: EA         NOP           
    $0B4A: EA         NOP           
    $0B4B: EA         NOP           
    $0B4C: EA         NOP           
    $0B4D: EA         NOP           
    $0B4E: EA         NOP           
    $0B4F: EA         NOP           
    $0B50: EA         NOP           
    $0B51: EA         NOP           
    $0B52: EA         NOP           
    $0B53: EA         NOP           
    $0B54: EA         NOP           
    $0B55: EA         NOP           
    $0B56: EA         NOP           
    $0B57: EA         NOP           
    $0B58: EA         NOP           
    $0B59: EA         NOP           
    $0B5A: EA         NOP           
    $0B5B: EA         NOP           
    $0B5C: EA         NOP           
    $0B5D: EA         NOP           
    $0B5E: EA         NOP           
    $0B5F: EA         NOP           
    $0B60: EA         NOP           
    $0B61: EA         NOP           
    $0B62: EA         NOP           
    $0B63: EA         NOP           
    $0B64: EA         NOP           
    $0B65: EA         NOP           
    $0B66: EA         NOP           
    $0B67: EA         NOP           
    $0B68: EA         NOP           
    $0B69: EA         NOP           
    $0B6A: EA         NOP           
    $0B6B: EA         NOP           
    $0B6C: EA         NOP           
    $0B6D: EA         NOP           
    $0B6E: EA         NOP           
    $0B6F: EA         NOP           
    $0B70: EA         NOP           
    $0B71: EA         NOP           
    $0B72: EA         NOP           
    $0B73: EA         NOP           
    $0B74: EA         NOP           
    $0B75: EA         NOP           
    $0B76: EA         NOP           
    $0B77: EA         NOP           
    $0B78: EA         NOP           
    $0B79: EA         NOP           
    $0B7A: EA         NOP           
    $0B7B: EA         NOP           
    $0B7C: EA         NOP           
    $0B7D: EA         NOP           
    $0B7E: EA         NOP           
    $0B7F: EA         NOP           
    $0B80: EA         NOP           
    $0B81: EA         NOP           
    $0B82: EA         NOP           
    $0B83: EA         NOP           
    $0B84: EA         NOP           
    $0B85: EA         NOP           
    $0B86: EA         NOP           
    $0B87: EA         NOP           
    $0B88: EA         NOP           
    $0B89: EA         NOP           
    $0B8A: EA         NOP           
    $0B8B: EA         NOP           
    $0B8C: EA         NOP           
    $0B8D: EA         NOP           
    $0B8E: EA         NOP           
    $0B8F: EA         NOP           
    $0B90: EA         NOP           
    $0B91: EA         NOP           
    $0B92: EA         NOP           
    $0B93: EA         NOP           
    $0B94: EA         NOP           
    $0B95: EA         NOP           
    $0B96: EA         NOP           
    $0B97: EA         NOP           
    $0B98: EA         NOP           
    $0B99: EA         NOP           
    $0B9A: EA         NOP           
    $0B9B: EA         NOP           
    $0B9C: EA         NOP           
    $0B9D: EA         NOP           
    $0B9E: EA         NOP           
    $0B9F: EA         NOP           
    $0BA0: EA         NOP           
    $0BA1: EA         NOP           
    $0BA2: EA         NOP           
    $0BA3: EA         NOP           
    $0BA4: EA         NOP           
    $0BA5: EA         NOP           
    $0BA6: EA         NOP           
    $0BA7: EA         NOP           
    $0BA8: EA         NOP           
    $0BA9: EA         NOP           
    $0BAA: EA         NOP           
    $0BAB: EA         NOP           
    $0BAC: EA         NOP           
    $0BAD: EA         NOP           
    $0BAE: EA         NOP           
    $0BAF: EA         NOP           
    $0BB0: EA         NOP           
    $0BB1: EA         NOP           
    $0BB2: EA         NOP           
    $0BB3: EA         NOP           
    $0BB4: EA         NOP           
    $0BB5: EA         NOP           
    $0BB6: EA         NOP           
    $0BB7: EA         NOP           
    $0BB8: EA         NOP           
    $0BB9: EA         NOP           
    $0BBA: EA         NOP           
    $0BBB: EA         NOP           
    $0BBC: EA         NOP           
    $0BBD: EA         NOP           
    $0BBE: EA         NOP           
    $0BBF: EA         NOP           
    $0BC0: EA         NOP           
    $0BC1: EA         NOP           
    $0BC2: EA         NOP           
    $0BC3: EA         NOP           
    $0BC4: EA         NOP           
    $0BC5: EA         NOP           
    $0BC6: EA         NOP           
    $0BC7: EA         NOP           
    $0BC8: EA         NOP           
    $0BC9: EA         NOP           
    $0BCA: EA         NOP           
    $0BCB: EA         NOP           
    $0BCC: EA         NOP           
    $0BCD: EA         NOP           
    $0BCE: EA         NOP           
    $0BCF: EA         NOP           
    $0BD0: EA         NOP           
    $0BD1: EA         NOP           
    $0BD2: EA         NOP           
    $0BD3: EA         NOP           
    $0BD4: EA         NOP           
    $0BD5: EA         NOP           
    $0BD6: EA         NOP           
    $0BD7: EA         NOP           
    $0BD8: EA         NOP           
    $0BD9: EA         NOP           
    $0BDA: EA         NOP           
    $0BDB: EA         NOP           
    $0BDC: EA         NOP           
    $0BDD: EA         NOP           
    $0BDE: EA         NOP           
    $0BDF: EA         NOP           
    $0BE0: EA         NOP           
    $0BE1: EA         NOP           
    $0BE2: EA         NOP           
    $0BE3: EA         NOP           
    $0BE4: EA         NOP           
    $0BE5: EA         NOP           
    $0BE6: EA         NOP           
    $0BE7: EA         NOP           
    $0BE8: EA         NOP           
    $0BE9: EA         NOP           
    $0BEA: EA         NOP           
    $0BEB: EA         NOP           
    $0BEC: EA         NOP           
    $0BED: EA         NOP           
    $0BEE: EA         NOP           
    $0BEF: EA         NOP           
    $0BF0: EA         NOP           
    $0BF1: EA         NOP           
    $0BF2: EA         NOP           
    $0BF3: EA         NOP           
    $0BF4: EA         NOP           
    $0BF5: EA         NOP           
    $0BF6: EA         NOP           
    $0BF7: EA         NOP           
    $0BF8: EA         NOP           
    $0BF9: EA         NOP           
    $0BFA: EA         NOP           
    $0BFB: EA         NOP           
    $0BFC: EA         NOP           
    $0BFD: EA         NOP           
    $0BFE: EA         NOP           
    $0BFF: EA         NOP           
sub_0C00:
    $0C00: 4C 00 0D   JMP $0d00        ; → L_0D00
sub_0C03:
    $0C03: 4C 40 0C   JMP $0c40        ; → L_0C40
; ----- data gap $0C06-$0C3F (58 bytes) -----

L_0C40:
    $0C40: CE 3F 0C   DEC $0c3f     
    $0C43: 30 01      BMI $0c46        ; → L_0C46
    $0C45: 60         RTS           
L_0C46:
    $0C46: C6 0B      DEC $0b       
    $0C48: F0 01      BEQ $0c4b        ; → L_0C4B
    $0C4A: 60         RTS           
L_0C4B:
    $0C4B: AD 16 17   LDA $1716     
    $0C4E: 8D 3F 0C   STA $0c3f     
L_0C51:
    $0C51: A0 00      LDY #$00      
    $0C53: B1 F0      LDA ($f0),y   
    $0C55: C9 FF      CMP #$ff      
    $0C57: D0 0C      BNE $0c65        ; → L_0C65
    $0C59: AE 08 0C   LDX $0c08     
    $0C5C: AC 09 0C   LDY $0c09     
    $0C5F: 86 F0      STX $f0       
    $0C61: 84 F1      STY $f1       
    $0C63: D0 EC      BNE $0c51        ; → L_0C51
L_0C65:
    $0C65: 10 08      BPL $0c6f        ; → L_0C6F
    $0C67: 29 0F      AND #$0f      
    $0C69: 0A         ASL a         
    $0C6A: 85 F2      STA $f2       
    $0C6C: C8         INY           
    $0C6D: B1 F0      LDA ($f0),y   
L_0C6F:
    $0C6F: 0A         ASL a         
    $0C70: 85 F3      STA $f3       
    $0C72: C8         INY           
    $0C73: B1 F0      LDA ($f0),y   
    $0C75: AA         TAX           
    $0C76: E8         INX           
    $0C77: 86 0B      STX $0b       
    $0C79: C8         INY           
    $0C7A: 98         TYA           
    $0C7B: 18         CLC           
    $0C7C: 65 F0      ADC $f0       
    $0C7E: 85 F0      STA $f0       
    $0C80: 90 02      BCC $0c84        ; → L_0C84
    $0C82: E6 F1      INC $f1       
L_0C84:
    $0C84: A9 00      LDA #$00      
    $0C86: 8D 0E DD   STA $dd0e     
    $0C89: A4 F2      LDY $f2       
    $0C8B: B9 80 1E   LDA $1e80,y   
    $0C8E: 8D 03 0F   STA $0f03     
    $0C91: B9 81 1E   LDA $1e81,y   
    $0C94: 8D 04 0F   STA $0f04     
    $0C97: A5 F3      LDA $f3       
    $0C99: 18         CLC           
    $0C9A: 69 00      ADC #$00      
    $0C9C: A8         TAY           
    $0C9D: B9 82 1E   LDA $1e82,y   
    $0CA0: 8D 04 DD   STA $dd04     
    $0CA3: B9 83 1E   LDA $1e83,y   
    $0CA6: 8D 05 DD   STA $dd05     
    $0CA9: A9 81      LDA #$81      
    $0CAB: 8D 0E DD   STA $dd0e     
    $0CAE: 2C 0E DD   BIT $dd0e     
    $0CB1: 60         RTS           
; ----- data gap $0CB2-$0CFF (78 bytes) -----

L_0D00:
    $0D00: A9 00      LDA #$00      
    $0D02: 85 F2      STA $f2       
    $0D04: 85 F3      STA $f3       
    $0D06: AE 06 0C   LDX $0c06     
    $0D09: AC 07 0C   LDY $0c07     
    $0D0C: 86 F0      STX $f0       
    $0D0E: 84 F1      STY $f1       
    $0D10: A9 01      LDA #$01      
    $0D12: 85 0B      STA $0b       
    $0D14: AD 16 17   LDA $1716     
    $0D17: 8D 3F 0C   STA $0c3f     
    $0D1A: 60         RTS           
; ----- data gap $0D1B-$0FFF (741 bytes) -----

sub_1000:
    $1000: 4C 1D 10   JMP $101d        ; → L_101D
sub_1003:
    $1003: 4C 85 10   JMP $1085        ; → L_1085
; ----- data gap $1006-$101C (23 bytes) -----

L_101D:
    $101D: 4C 07 18   JMP $1807        ; → L_1807
; ----- data gap $1020-$1041 (34 bytes) -----

sub_1042:
    $1042: C8         INY           
    $1043: B1 F8      LDA ($f8),y   
    $1045: 9D 26 17   STA $1726,x   
    $1048: 60         RTS           
; ----- data gap $1049-$104F (7 bytes) -----

L_1050:
    $1050: B9 6E 1B   LDA $1b6e,y   
    $1053: 8D 16 17   STA $1716     
    $1056: B9 6F 1B   LDA $1b6f,y   
    $1059: 8D 17 17   STA $1717     
    $105C: EA         NOP           
    $105D: EA         NOP           
    $105E: EA         NOP           
    $105F: A2 00      LDX #$00      
    $1061: 8A         TXA           
L_1062:
    $1062: 9D 18 17   STA $1718,x   
    $1065: E8         INX           
    $1066: E0 86      CPX #$86      
    $1068: D0 F8      BNE $1062        ; → L_1062
    $106A: A2 00      LDX #$00      
    $106C: A9 01      LDA #$01      
L_106E:
    $106E: 9D 0C 10   STA $100c,x   
    $1071: 9D 3B 17   STA $173b,x   
    $1074: E8         INX           
    $1075: E0 03      CPX #$03      
    $1077: D0 F5      BNE $106e        ; → L_106E
    $1079: A2 00      LDX #$00      
    $107B: 8A         TXA           
L_107C:
    $107C: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $107F: E8         INX           
    $1080: E0 18      CPX #$18      
    $1082: D0 F8      BNE $107c        ; → L_107C
    $1084: 60         RTS           
L_1085:
    $1085: CE 18 17   DEC $1718     
    $1088: 10 06      BPL $1090        ; → L_1090
    $108A: AD 16 17   LDA $1716     
    $108D: 8D 18 17   STA $1718     
L_1090:
    $1090: A2 00      LDX #$00      
    $1092: 8E 20 17   STX $1720     
    $1095: 20 B0 10   JSR $10b0        ; → sub_10B0
    $1098: E8         INX           
    $1099: 20 B0 10   JSR $10b0        ; → sub_10B0
    $109C: E8         INX           
    $109D: 20 B0 10   JSR $10b0        ; → sub_10B0
    $10A0: AD 1C 17   LDA $171c     
    $10A3: 8D 16 D4   STA $d416      ;FC_HI
    $10A6: AD 18 10   LDA $1018     
    $10A9: 0D 23 17   ORA $1723     
    $10AC: 8D 17 D4   STA $d417      ;RES_FILT
    $10AF: 60         RTS           
sub_10B0:
    $10B0: BD 0C 10   LDA $100c,x   
    $10B3: F0 10      BEQ $10c5        ; → L_10C5
    $10B5: AD 16 17   LDA $1716     
    $10B8: CD 18 17   CMP $1718     
    $10BB: D0 08      BNE $10c5        ; → L_10C5
    $10BD: DE 3B 17   DEC $173b,x   
    $10C0: BD 3B 17   LDA $173b,x   
    $10C3: F0 03      BEQ $10c8        ; → L_10C8
L_10C5:
    $10C5: 4C F9 11   JMP $11f9        ; → L_11F9
L_10C8:
    $10C8: BD 07 17   LDA $1707,x   
    $10CB: 85 F8      STA $f8       
    $10CD: BD 0A 17   LDA $170a,x   
    $10D0: 85 F9      STA $f9       
L_10D2:
    $10D2: BC 26 17   LDY $1726,x   
    $10D5: B1 F8      LDA ($f8),y   
    $10D7: 10 28      BPL $1101        ; → L_1101
    $10D9: C9 FF      CMP #$ff      
    $10DB: D0 08      BNE $10e5        ; → L_10E5
    $10DD: A9 00      LDA #$00      
    $10DF: 20 42 10   JSR $1042        ; → sub_1042
    $10E2: 4C D2 10   JMP $10d2        ; → L_10D2
L_10E5:
    $10E5: C9 FE      CMP #$fe      
    $10E7: D0 06      BNE $10ef        ; → L_10EF
    $10E9: A9 00      LDA #$00      
    $10EB: 9D 0C 10   STA $100c,x   
    $10EE: 60         RTS           
L_10EF:
    $10EF: 38         SEC           
    $10F0: E9 A0      SBC #$a0      
    $10F2: B0 04      BCS $10f8        ; → L_10F8
    $10F4: 49 1F      EOR #$1f      
    $10F6: 69 01      ADC #$01      
L_10F8:
    $10F8: 9D 2C 17   STA $172c,x   
    $10FB: FE 26 17   INC $1726,x   
    $10FE: C8         INY           
    $10FF: B1 F8      LDA ($f8),y   
L_1101:
    $1101: A8         TAY           
    $1102: B9 5F 1E   LDA $1e5f,y   
    $1105: 85 F8      STA $f8       
    $1107: B9 6B 1E   LDA $1e6b,y   
    $110A: 85 F9      STA $f9       
L_110C:
    $110C: 4C C0 17   JMP $17c0        ; → L_17C0
; ----- data gap $110F-$1112 (4 bytes) -----

L_1113:
    $1113: C9 60      CMP #$60      
    $1115: 90 0B      BCC $1122        ; → L_1122
    $1117: 29 1F      AND #$1f      
    $1119: 9D 15 10   STA $1015,x   
    $111C: FE 29 17   INC $1729,x   
    $111F: 4C 0C 11   JMP $110c        ; → L_110C
L_1122:
    $1122: 4C A2 11   JMP $11a2        ; → L_11A2
L_1125:
    $1125: C9 7E      CMP #$7e      
    $1127: F0 4B      BEQ $1174        ; → L_1174
    $1129: C9 7D      CMP #$7d      
    $112B: F0 56      BEQ $1183        ; → L_1183
    $112D: C9 C0      CMP #$c0      
    $112F: 90 66      BCC $1197        ; → L_1197
    $1131: 29 1F      AND #$1f      
    $1133: 48         PHA           
    $1134: 29 0F      AND #$0f      
    $1136: 9D 41 17   STA $1741,x   
    $1139: 68         PLA           
    $113A: 29 10      AND #$10      
    $113C: D0 20      BNE $115e        ; → L_115E
    $113E: C8         INY           
    $113F: B1 F8      LDA ($f8),y   
    $1141: 18         CLC           
    $1142: 7D 2C 17   ADC $172c,x   
    $1145: 9D 44 17   STA $1744,x   
    $1148: C8         INY           
    $1149: B1 F8      LDA ($f8),y   
    $114B: 18         CLC           
    $114C: 7D 2C 17   ADC $172c,x   
    $114F: 9D 47 17   STA $1747,x   
    $1152: FE 29 17   INC $1729,x   
    $1155: FE 29 17   INC $1729,x   
    $1158: BD 44 17   LDA $1744,x   
    $115B: 4C A6 11   JMP $11a6        ; → L_11A6
L_115E:
    $115E: C8         INY           
    $115F: B1 F8      LDA ($f8),y   
    $1161: 18         CLC           
    $1162: 7D 2C 17   ADC $172c,x   
    $1165: 9D 47 17   STA $1747,x   
    $1168: BD 12 10   LDA $1012,x   
    $116B: 9D 44 17   STA $1744,x   
    $116E: FE 29 17   INC $1729,x   
    $1171: 4C 74 11   JMP $1174        ; → L_1174
L_1174:
    $1174: BD 3E 17   LDA $173e,x   
    $1177: 9D 3B 17   STA $173b,x   
    $117A: FE 29 17   INC $1729,x   
L_117D:
    $117D: 20 E6 11   JSR $11e6        ; → sub_11E6
    $1180: 4C 22 13   JMP $1322        ; → L_1322
L_1183:
    $1183: BD 3E 17   LDA $173e,x   
    $1186: 9D 3B 17   STA $173b,x   
    $1189: BD 0F 10   LDA $100f,x   
    $118C: 49 01      EOR #$01      
    $118E: 9D 0F 10   STA $100f,x   
    $1191: FE 29 17   INC $1729,x   
    $1194: 4C 7D 11   JMP $117d        ; → L_117D
L_1197:
    $1197: 4C DA 17   JMP $17da        ; → L_17DA
; ----- data gap $119A-$11A1 (8 bytes) -----

L_11A2:
    $11A2: 18         CLC           
    $11A3: 7D 2C 17   ADC $172c,x   
L_11A6:
    $11A6: 9D 12 10   STA $1012,x   
    $11A9: A8         TAY           
    $11AA: B9 47 16   LDA $1647,y   
    $11AD: 9D 2F 17   STA $172f,x   
    $11B0: B9 A7 16   LDA $16a7,y   
    $11B3: 9D 32 17   STA $1732,x   
    $11B6: BD 3E 17   LDA $173e,x   
    $11B9: 9D 3B 17   STA $173b,x   
    $11BC: FE 29 17   INC $1729,x   
    $11BF: BD B0 17   LDA $17b0,x   
    $11C2: D0 B9      BNE $117d        ; → L_117D
    $11C4: A9 00      LDA #$00      
    $11C6: 9D 35 17   STA $1735,x   
    $11C9: 9D 38 17   STA $1738,x   
    $11CC: 18         CLC           
    $11CD: 9D 68 17   STA $1768,x   
    $11D0: 9D 6B 17   STA $176b,x   
    $11D3: 20 23 18   JSR $1823        ; → sub_1823
    $11D6: BC 0D 17   LDY $170d,x   
    $11D9: A9 08      LDA #$08      
    $11DB: 20 FB 17   JSR $17fb        ; → sub_17FB
    $11DE: A9 FF      LDA #$ff      
    $11E0: 9D 0F 10   STA $100f,x   
    $11E3: 9D 4A 17   STA $174a,x   
sub_11E6:
    $11E6: BC 29 17   LDY $1729,x   
    $11E9: B1 F8      LDA ($f8),y   
    $11EB: C9 7F      CMP #$7f      
    $11ED: F0 01      BEQ $11f0        ; → L_11F0
    $11EF: 60         RTS           
L_11F0:
    $11F0: A9 00      LDA #$00      
    $11F2: 9D 29 17   STA $1729,x   
    $11F5: 20 2D 18   JSR $182d        ; → sub_182D
    $11F8: 60         RTS           
L_11F9:
    $11F9: BD 4A 17   LDA $174a,x   
    $11FC: D0 03      BNE $1201        ; → L_1201
    $11FE: 4C 22 13   JMP $1322        ; → L_1322
L_1201:
    $1201: 18         CLC           
    $1202: A9 00      LDA #$00      
    $1204: 9D 4A 17   STA $174a,x   
    $1207: 9D 50 17   STA $1750,x   
    $120A: 9D 89 17   STA $1789,x   
    $120D: 9D 92 17   STA $1792,x   
    $1210: 9D 95 17   STA $1795,x   
    $1213: BD 15 10   LDA $1015,x   
    $1216: 0A         ASL a         
    $1217: 0A         ASL a         
    $1218: 0A         ASL a         
    $1219: 7D 15 10   ADC $1015,x   
    $121C: 7D 15 10   ADC $1015,x   
    $121F: 7D 15 10   ADC $1015,x   
    $1222: 9D 4D 17   STA $174d,x   
    $1225: A8         TAY           
    $1226: B9 F0 18   LDA $18f0,y   
    $1229: 48         PHA           
    $122A: B9 F1 18   LDA $18f1,y   
    $122D: BC 0D 17   LDY $170d,x   
    $1230: 20 4B 18   JSR $184b        ; → sub_184B
    $1233: 68         PLA           
    $1234: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1237: BC 4D 17   LDY $174d,x   
    $123A: B9 FA 18   LDA $18fa,y   
    $123D: 29 04      AND #$04      
    $123F: D0 28      BNE $1269        ; → L_1269
    $1241: B9 F2 18   LDA $18f2,y   
    $1244: 48         PHA           
    $1245: 29 0F      AND #$0f      
    $1247: 9D 53 17   STA $1753,x   
    $124A: 68         PLA           
    $124B: 4A         LSR a         
    $124C: 4A         LSR a         
    $124D: 4A         LSR a         
    $124E: 4A         LSR a         
    $124F: 9D 56 17   STA $1756,x   
    $1252: 49 0F      EOR #$0f      
    $1254: 9D 59 17   STA $1759,x   
    $1257: B9 F6 18   LDA $18f6,y   
    $125A: 4A         LSR a         
    $125B: 4A         LSR a         
    $125C: 4A         LSR a         
    $125D: 4A         LSR a         
    $125E: 9D 5F 17   STA $175f,x   
    $1261: A9 00      LDA #$00      
    $1263: 9D 62 17   STA $1762,x   
    $1266: 9D 65 17   STA $1765,x   
L_1269:
    $1269: B9 FA 18   LDA $18fa,y   
    $126C: 29 20      AND #$20      
    $126E: F0 50      BEQ $12c0        ; → L_12C0
    $1270: AD 18 10   LDA $1018     
    $1273: 1D 10 17   ORA $1710,x   
    $1276: 8D 18 10   STA $1018     
    $1279: B9 FA 18   LDA $18fa,y   
    $127C: 29 02      AND #$02      
    $127E: D0 49      BNE $12c9        ; → L_12C9
    $1280: A9 00      LDA #$00      
    $1282: 8D 19 17   STA $1719     
    $1285: 8D 1A 17   STA $171a     
    $1288: B9 F6 18   LDA $18f6,y   
    $128B: 29 0F      AND #$0f      
    $128D: 0A         ASL a         
    $128E: 0A         ASL a         
    $128F: 0A         ASL a         
    $1290: 0A         ASL a         
    $1291: 8D 1B 17   STA $171b     
    $1294: A8         TAY           
    $1295: B9 17 1B   LDA $1b17,y   
    $1298: 48         PHA           
    $1299: 29 F0      AND #$f0      
    $129B: 8D 23 17   STA $1723     
    $129E: 68         PLA           
    $129F: 29 0F      AND #$0f      
    $12A1: 0A         ASL a         
    $12A2: 0A         ASL a         
    $12A3: 0A         ASL a         
    $12A4: 0A         ASL a         
    $12A5: 0D 17 17   ORA $1717     
    $12A8: EA         NOP           
    $12A9: EA         NOP           
    $12AA: EA         NOP           
    $12AB: B9 18 1B   LDA $1b18,y   
    $12AE: 8D 1C 17   STA $171c     
    $12B1: B9 19 1B   LDA $1b19,y   
    $12B4: 8D 1D 17   STA $171d     
    $12B7: B9 1A 1B   LDA $1b1a,y   
    $12BA: 8D 1E 17   STA $171e     
    $12BD: 4C C9 12   JMP $12c9        ; → L_12C9
L_12C0:
    $12C0: AD 18 10   LDA $1018     
    $12C3: 3D 13 17   AND $1713,x   
    $12C6: 8D 18 10   STA $1018     
L_12C9:
    $12C9: BC 4D 17   LDY $174d,x   
    $12CC: B9 F7 18   LDA $18f7,y   
    $12CF: 48         PHA           
    $12D0: 29 F0      AND #$f0      
    $12D2: 4A         LSR a         
    $12D3: 9D 71 17   STA $1771,x   
    $12D6: 68         PLA           
    $12D7: 29 0F      AND #$0f      
    $12D9: 9D 74 17   STA $1774,x   
    $12DC: B9 F8 18   LDA $18f8,y   
    $12DF: 9D 77 17   STA $1777,x   
    $12E2: B9 F9 18   LDA $18f9,y   
    $12E5: 9D 7A 17   STA $177a,x   
    $12E8: B9 FA 18   LDA $18fa,y   
    $12EB: 9D 7D 17   STA $177d,x   
    $12EE: BC 12 10   LDY $1012,x   
    $12F1: B9 88 18   LDA $1888,y   
    $12F4: 18         CLC           
    $12F5: 9D 92 17   STA $1792,x   
    $12F8: A9 02      LDA #$02      
    $12FA: 9D 86 17   STA $1786,x   
    $12FD: 20 85 18   JSR $1885        ; → sub_1885
    $1300: BD 7D 17   LDA $177d,x   
    $1303: 29 80      AND #$80      
    $1305: F0 11      BEQ $1318        ; → L_1318
    $1307: BC 0D 17   LDY $170d,x   
    $130A: A9 FF      LDA #$ff      
    $130C: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $130F: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $1312: A9 81      LDA #$81      
    $1314: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $1317: 60         RTS           
L_1318:
    $1318: 4C 91 15   JMP $1591        ; → sub_1591
; ----- data gap $131B-$1321 (7 bytes) -----

L_1322:
    $1322: BD 86 17   LDA $1786,x   
    $1325: F0 06      BEQ $132d        ; → L_132D
    $1327: DE 86 17   DEC $1786,x   
    $132A: 4C 4E 13   JMP $134e        ; → L_134E
L_132D:
    $132D: BD 7D 17   LDA $177d,x   
    $1330: 29 10      AND #$10      
    $1332: F0 0E      BEQ $1342        ; → L_1342
    $1334: BD 3B 17   LDA $173b,x   
    $1337: C9 01      CMP #$01      
    $1339: D0 13      BNE $134e        ; → L_134E
    $133B: A9 FE      LDA #$fe      
    $133D: 20 EC 17   JSR $17ec        ; → sub_17EC
    $1340: D0 0C      BNE $134e        ; → L_134E
L_1342:
    $1342: BD 7D 17   LDA $177d,x   
    $1345: 29 08      AND #$08      
    $1347: D0 05      BNE $134e        ; → L_134E
    $1349: A9 FE      LDA #$fe      
    $134B: 9D 0F 10   STA $100f,x   
L_134E:
    $134E: BD 62 17   LDA $1762,x   
    $1351: 4A         LSR a         
    $1352: 18         CLC           
    $1353: 7D 4D 17   ADC $174d,x   
    $1356: A8         TAY           
    $1357: B9 F3 18   LDA $18f3,y   
    $135A: 8D 1F 17   STA $171f     
    $135D: BD 62 17   LDA $1762,x   
    $1360: 29 01      AND #$01      
    $1362: F0 0C      BEQ $1370        ; → L_1370
    $1364: AD 1F 17   LDA $171f     
    $1367: 29 0F      AND #$0f      
    $1369: 0A         ASL a         
    $136A: 0A         ASL a         
    $136B: 0A         ASL a         
    $136C: 0A         ASL a         
    $136D: 4C 75 13   JMP $1375        ; → L_1375
L_1370:
    $1370: AD 1F 17   LDA $171f     
    $1373: 29 F0      AND #$f0      
L_1375:
    $1375: 18         CLC           
    $1376: 7D 5F 17   ADC $175f,x   
    $1379: 9D 5C 17   STA $175c,x   
    $137C: BD 65 17   LDA $1765,x   
    $137F: D0 1E      BNE $139f        ; → L_139F
    $1381: BD 50 17   LDA $1750,x   
    $1384: 18         CLC           
    $1385: 7D 5C 17   ADC $175c,x   
    $1388: 9D 50 17   STA $1750,x   
    $138B: BD 53 17   LDA $1753,x   
    $138E: 69 00      ADC #$00      
    $1390: 9D 53 17   STA $1753,x   
    $1393: DD 59 17   CMP $1759,x   
    $1396: D0 2D      BNE $13c5        ; → L_13C5
    $1398: A9 01      LDA #$01      
    $139A: 9D 65 17   STA $1765,x   
    $139D: D0 1C      BNE $13bb        ; → L_13BB
L_139F:
    $139F: BD 50 17   LDA $1750,x   
    $13A2: 38         SEC           
    $13A3: FD 5C 17   SBC $175c,x   
    $13A6: 9D 50 17   STA $1750,x   
    $13A9: BD 53 17   LDA $1753,x   
    $13AC: E9 00      SBC #$00      
    $13AE: 9D 53 17   STA $1753,x   
    $13B1: DD 56 17   CMP $1756,x   
    $13B4: D0 0F      BNE $13c5        ; → L_13C5
    $13B6: A9 00      LDA #$00      
    $13B8: 9D 65 17   STA $1765,x   
L_13BB:
    $13BB: BD 62 17   LDA $1762,x   
    $13BE: C9 05      CMP #$05      
    $13C0: F0 03      BEQ $13c5        ; → L_13C5
    $13C2: FE 62 17   INC $1762,x   
L_13C5:
    $13C5: BD 7D 17   LDA $177d,x   
    $13C8: 29 20      AND #$20      
    $13CA: F0 50      BEQ $141c        ; → L_141C
    $13CC: AD 20 17   LDA $1720     
    $13CF: D0 4B      BNE $141c        ; → L_141C
    $13D1: E8         INX           
    $13D2: 8E 20 17   STX $1720     
    $13D5: CA         DEX           
    $13D6: AD 1C 17   LDA $171c     
    $13D9: CD 1E 17   CMP $171e     
    $13DC: F0 3E      BEQ $141c        ; → L_141C
    $13DE: AD 1B 17   LDA $171b     
    $13E1: 18         CLC           
    $13E2: 6D 19 17   ADC $1719     
    $13E5: A8         TAY           
    $13E6: B9 1B 1B   LDA $1b1b,y   
    $13E9: 8D 21 17   STA $1721     
    $13EC: B9 21 1B   LDA $1b21,y   
    $13EF: 8D 22 17   STA $1722     
    $13F2: AD 1C 17   LDA $171c     
    $13F5: 18         CLC           
    $13F6: 6D 21 17   ADC $1721     
    $13F9: 8D 1C 17   STA $171c     
    $13FC: EE 1A 17   INC $171a     
    $13FF: AD 1A 17   LDA $171a     
    $1402: CD 22 17   CMP $1722     
    $1405: D0 15      BNE $141c        ; → L_141C
    $1407: A9 00      LDA #$00      
    $1409: 8D 1A 17   STA $171a     
    $140C: EE 19 17   INC $1719     
    $140F: B4 19      LDY $19,x     
    $1411: 17         ???           
    $1414: D0 06      BNE $141c        ; → L_141C
    $1416: AD 1D 17   LDA $171d     
    $1419: 8D 19 17   STA $1719     
L_141C:
    $141C: BD 41 17   LDA $1741,x   
    $141F: F0 7E      BEQ $149f        ; → L_149F
    $1421: 0A         ASL a         
    $1422: 0A         ASL a         
    $1423: 0A         ASL a         
    $1424: 0A         ASL a         
    $1425: 8D 1F 17   STA $171f     
    $1428: BD 44 17   LDA $1744,x   
    $142B: DD 47 17   CMP $1747,x   
    $142E: B0 2A      BCS $145a        ; → L_145A
    $1430: BC 47 17   LDY $1747,x   
    $1433: BD 35 17   LDA $1735,x   
    $1436: 18         CLC           
    $1437: 6D 1F 17   ADC $171f     
    $143A: 9D 35 17   STA $1735,x   
    $143D: BD 38 17   LDA $1738,x   
    $1440: 69 00      ADC #$00      
    $1442: 9D 38 17   STA $1738,x   
    $1445: BD 35 17   LDA $1735,x   
    $1448: 18         CLC           
    $1449: 7D 2F 17   ADC $172f,x   
    $144C: BD 38 17   LDA $1738,x   
    $144F: 7D 32 17   ADC $1732,x   
    $1452: D9 A7 16   CMP $16a7,y   
    $1455: D0 45      BNE $149c        ; → L_149C
    $1457: 4C 81 14   JMP $1481        ; → L_1481
L_145A:
    $145A: BC 47 17   LDY $1747,x   
    $145D: BD 35 17   LDA $1735,x   
    $1460: 38         SEC           
    $1461: ED 1F 17   SBC $171f     
    $1464: 9D 35 17   STA $1735,x   
    $1467: BD 38 17   LDA $1738,x   
    $146A: E9 00      SBC #$00      
    $146C: 9D 38 17   STA $1738,x   
    $146F: BD 35 17   LDA $1735,x   
    $1472: 18         CLC           
    $1473: 7D 2F 17   ADC $172f,x   
    $1476: BD 38 17   LDA $1738,x   
    $1479: 7D 32 17   ADC $1732,x   
    $147C: D9 A7 16   CMP $16a7,y   
    $147F: D0 1B      BNE $149c        ; → L_149C
L_1481:
    $1481: 98         TYA           
    $1482: 9D 12 10   STA $1012,x   
    $1485: B9 47 16   LDA $1647,y   
    $1488: 9D 2F 17   STA $172f,x   
    $148B: B9 A7 16   LDA $16a7,y   
    $148E: 9D 32 17   STA $1732,x   
    $1491: A9 00      LDA #$00      
    $1493: 9D 41 17   STA $1741,x   
    $1496: 9D 35 17   STA $1735,x   
    $1499: 9D 38 17   STA $1738,x   
L_149C:
    $149C: 4C 91 15   JMP $1591        ; → sub_1591
L_149F:
    $149F: BD 71 17   LDA $1771,x   
    $14A2: F0 06      BEQ $14aa        ; → L_14AA
    $14A4: DE 71 17   DEC $1771,x   
    $14A7: 4C 91 15   JMP $1591        ; → sub_1591
L_14AA:
    $14AA: BD 7D 17   LDA $177d,x   
    $14AD: 29 40      AND #$40      
    $14AF: F0 6F      BEQ $1520        ; → L_1520
    $14B1: EE 19 10   INC $1019     
    $14B4: AD 19 10   LDA $1019     
    $14B7: 29 01      AND #$01      
    $14B9: 8D 19 10   STA $1019     
    $14BC: D0 03      BNE $14c1        ; → L_14C1
    $14BE: 4C 91 15   JMP $1591        ; → sub_1591
L_14C1:
    $14C1: BC 0D 17   LDY $170d,x   
    $14C4: BD 2F 17   LDA $172f,x   
    $14C7: 18         CLC           
    $14C8: 7D 35 17   ADC $1735,x   
    $14CB: 8D 24 17   STA $1724     
    $14CE: BD 32 17   LDA $1732,x   
    $14D1: 69 00      ADC #$00      
    $14D3: 8D 25 17   STA $1725     
    $14D6: AD 24 17   LDA $1724     
    $14D9: 38         SEC           
    $14DA: FD 98 17   SBC $1798,x   
    $14DD: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $14E0: AD 25 17   LDA $1725     
    $14E3: FD 9B 17   SBC $179b,x   
    $14E6: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
    $14E9: BD 77 17   LDA $1777,x   
    $14EC: 30 15      BMI $1503        ; → L_1503
    $14EE: BD 98 17   LDA $1798,x   
    $14F1: 18         CLC           
    $14F2: 7D 77 17   ADC $1777,x   
    $14F5: 9D 98 17   STA $1798,x   
    $14F8: BD 9B 17   LDA $179b,x   
    $14FB: 69 00      ADC #$00      
    $14FD: 9D 9B 17   STA $179b,x   
    $1500: 4C 19 16   JMP $1619        ; → L_1619
L_1503:
    $1503: BD 77 17   LDA $1777,x   
    $1506: 29 7F      AND #$7f      
    $1508: 8D 1A 10   STA $101a     
    $150B: BD 98 17   LDA $1798,x   
    $150E: 38         SEC           
    $150F: ED 1A 10   SBC $101a     
    $1512: 9D 98 17   STA $1798,x   
    $1515: BD 9B 17   LDA $179b,x   
    $1518: E9 00      SBC #$00      
    $151A: 9D 9B 17   STA $179b,x   
    $151D: 4C 19 16   JMP $1619        ; → L_1619
L_1520:
    $1520: BD 68 17   LDA $1768,x   
    $1523: D0 21      BNE $1546        ; → L_1546
    $1525: BD 35 17   LDA $1735,x   
    $1528: 18         CLC           
    $1529: 7D 92 17   ADC $1792,x   
    $152C: 9D 35 17   STA $1735,x   
    $152F: BD 38 17   LDA $1738,x   
    $1532: 7D 95 17   ADC $1795,x   
    $1535: 9D 38 17   STA $1738,x   
    $1538: FE 6B 17   INC $176b,x   
    $153B: BD 6B 17   LDA $176b,x   
    $153E: DD 74 17   CMP $1774,x   
    $1541: F0 24      BEQ $1567        ; → L_1567
    $1543: 4C 91 15   JMP $1591        ; → sub_1591
L_1546:
    $1546: BD 35 17   LDA $1735,x   
    $1549: 38         SEC           
    $154A: FD 92 17   SBC $1792,x   
    $154D: 9D 35 17   STA $1735,x   
    $1550: BD 38 17   LDA $1738,x   
    $1553: FD 95 17   SBC $1795,x   
    $1556: 9D 38 17   STA $1738,x   
    $1559: FE 6B 17   INC $176b,x   
    $155C: BD 6B 17   LDA $176b,x   
    $155F: DD 74 17   CMP $1774,x   
    $1562: F0 03      BEQ $1567        ; → L_1567
    $1564: 4C 91 15   JMP $1591        ; → sub_1591
L_1567:
    $1567: A9 00      LDA #$00      
    $1569: 9D 6B 17   STA $176b,x   
    $156C: BD 68 17   LDA $1768,x   
    $156F: 49 01      EOR #$01      
    $1571: 9D 68 17   STA $1768,x   
    $1574: BD 6E 17   LDA $176e,x   
    $1577: DD 77 17   CMP $1777,x   
    $157A: F0 15      BEQ $1591        ; → sub_1591
    $157C: FE 6E 17   INC $176e,x   
    $157F: BD 74 17   LDA $1774,x   
    $1582: 18         CLC           
    $1583: 7D 74 17   ADC $1774,x   
    $1586: 9D 74 17   STA $1774,x   
    $1589: BD 95 17   LDA $1795,x   
    $158C: 69 00      ADC #$00      
    $158E: 2C 95 17   BIT $1795     
sub_1591:
    $1591: BD 7D 17   LDA $177d,x   
    $1594: 29 01      AND #$01      
    $1596: D0 3D      BNE $15d5        ; → L_15D5
L_1598:
    $1598: BC 7A 17   LDY $177a,x   
    $159B: B9 ED 19   LDA $19ed,y   
    $159E: C9 90      CMP #$90      
    $15A0: 90 13      BCC $15b5        ; → L_15B5
    $15A2: 38         SEC           
    $15A3: E9 90      SBC #$90      
    $15A5: 8D 1F 17   STA $171f     
    $15A8: BD 7A 17   LDA $177a,x   
    $15AB: 38         SEC           
    $15AC: ED 1F 17   SBC $171f     
    $15AF: 9D 7A 17   STA $177a,x   
    $15B2: 4C 98 15   JMP $1598        ; → L_1598
L_15B5:
    $15B5: 9D 80 17   STA $1780,x   
    $15B8: B9 82 1A   LDA $1a82,y   
    $15BB: 18         CLC           
    $15BC: 7D 12 10   ADC $1012,x   
    $15BF: 9D 83 17   STA $1783,x   
    $15C2: A8         TAY           
    $15C3: B9 47 16   LDA $1647,y   
    $15C6: 9D 2F 17   STA $172f,x   
    $15C9: B9 A7 16   LDA $16a7,y   
    $15CC: 9D 32 17   STA $1732,x   
    $15CF: FE 7A 17   INC $177a,x   
    $15D2: 4C 03 16   JMP $1603        ; → L_1603
L_15D5:
    $15D5: BC 7A 17   LDY $177a,x   
    $15D8: B9 ED 19   LDA $19ed,y   
    $15DB: C9 90      CMP #$90      
    $15DD: 90 13      BCC $15f2        ; → L_15F2
    $15DF: 38         SEC           
    $15E0: E9 90      SBC #$90      
    $15E2: 8D 1F 17   STA $171f     
    $15E5: BD 7A 17   LDA $177a,x   
    $15E8: 38         SEC           
    $15E9: ED 1F 17   SBC $171f     
    $15EC: 9D 7A 17   STA $177a,x   
    $15EF: 4C D5 15   JMP $15d5        ; → L_15D5
L_15F2:
    $15F2: 9D 80 17   STA $1780,x   
    $15F5: A9 00      LDA #$00      
    $15F7: 9D 2F 17   STA $172f,x   
    $15FA: B9 82 1A   LDA $1a82,y   
    $15FD: 9D 32 17   STA $1732,x   
    $1600: FE 7A 17   INC $177a,x   
L_1603:
    $1603: BC 0D 17   LDY $170d,x   
    $1606: BD 2F 17   LDA $172f,x   
    $1609: 18         CLC           
    $160A: 7D 35 17   ADC $1735,x   
    $160D: 99 00 D4   STA $d400,y    ;V1_FREQ_LO,Y
    $1610: BD 32 17   LDA $1732,x   
    $1613: 7D 38 17   ADC $1738,x   
    $1616: 99 01 D4   STA $d401,y    ;V1_FREQ_HI,Y
L_1619:
    $1619: BD 50 17   LDA $1750,x   
    $161C: 99 02 D4   STA $d402,y    ;V1_PW_LO,Y
    $161F: BD 53 17   LDA $1753,x   
    $1622: 99 03 D4   STA $d403,y    ;V1_PW_HI,Y
    $1625: BD 80 17   LDA $1780,x   
    $1628: 3D 0F 10   AND $100f,x   
    $162B: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $162E: 60         RTS           
; ----- data gap $162F-$17BF (401 bytes) -----

L_17C0:
    $17C0: 4C 37 18   JMP $1837        ; → L_1837
; ----- data gap $17C3-$17C4 (2 bytes) -----

L_17C5:
    $17C5: C9 7C      CMP #$7c      
    $17C7: F0 03      BEQ $17cc        ; → L_17CC
    $17C9: 4C 25 11   JMP $1125        ; → L_1125
L_17CC:
    $17CC: BD B0 17   LDA $17b0,x   
    $17CF: 49 01      EOR #$01      
    $17D1: 9D B0 17   STA $17b0,x   
    $17D4: FE 29 17   INC $1729,x   
    $17D7: 4C C0 17   JMP $17c0        ; → L_17C0
L_17DA:
    $17DA: C9 80      CMP #$80      
    $17DC: 90 0B      BCC $17e9        ; → L_17E9
    $17DE: 29 3F      AND #$3f      
    $17E0: 9D 3E 17   STA $173e,x   
    $17E3: FE 29 17   INC $1729,x   
    $17E6: 4C 0C 11   JMP $110c        ; → L_110C
L_17E9:
    $17E9: 4C 13 11   JMP $1113        ; → L_1113
sub_17EC:
    $17EC: 9D 0F 10   STA $100f,x   
    $17EF: BC 0D 17   LDY $170d,x   
    $17F2: A9 00      LDA #$00      
    $17F4: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $17F7: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $17FA: 60         RTS           
sub_17FB:
    $17FB: 99 04 D4   STA $d404,y    ;V1_CTRL,Y
    $17FE: A9 0F      LDA #$0f      
    $1800: 99 05 D4   STA $d405,y    ;V1_AD,Y
    $1803: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $1806: 60         RTS           
L_1807:
    $1807: 0A         ASL a         
    $1808: 0A         ASL a         
    $1809: 0A         ASL a         
    $180A: A8         TAY           
    $180B: A2 00      LDX #$00      
L_180D:
    $180D: B9 6E 1B   LDA $1b6e,y   
    $1810: 9D 07 17   STA $1707,x   
    $1813: B9 6F 1B   LDA $1b6f,y   
    $1816: 9D 0A 17   STA $170a,x   
    $1819: C8         INY           
    $181A: C8         INY           
    $181B: E8         INX           
    $181C: E0 03      CPX #$03      
    $181E: D0 ED      BNE $180d        ; → L_180D
    $1820: 4C 70 18   JMP $1870        ; → L_1870
sub_1823:
    $1823: 9D 6E 17   STA $176e,x   
    $1826: 9D 98 17   STA $1798,x   
    $1829: 9D 9B 17   STA $179b,x   
    $182C: 60         RTS           
sub_182D:
    $182D: FE 26 17   INC $1726,x   
    $1830: 9D B0 17   STA $17b0,x   
    $1833: 2C B3 17   BIT $17b3     
    $1836: 60         RTS           
L_1837:
    $1837: BC 29 17   LDY $1729,x   
    $183A: B1 F8      LDA ($f8),y   
    $183C: C9 F0      CMP #$f0      
    $183E: 90 85      BCC $17c5        ; → L_17C5
    $1840: 29 0F      AND #$0f      
    $1842: 9D B3 17   STA $17b3,x   
    $1845: FE 29 17   INC $1729,x   
    $1848: 4C 37 18   JMP $1837        ; → L_1837
sub_184B:
    $184B: 8D 40 10   STA $1040     
    $184E: BD B3 17   LDA $17b3,x   
    $1851: D0 07      BNE $185a        ; → L_185A
    $1853: AD 40 10   LDA $1040     
    $1856: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $1859: 60         RTS           
L_185A:
    $185A: AD 40 10   LDA $1040     
    $185D: 29 0F      AND #$0f      
    $185F: 8D 40 10   STA $1040     
    $1862: BD B3 17   LDA $17b3,x   
    $1865: 0A         ASL a         
    $1866: 0A         ASL a         
    $1867: 0A         ASL a         
    $1868: 0A         ASL a         
    $1869: 0D 40 10   ORA $1040     
    $186C: 99 06 D4   STA $d406,y    ;V1_SR,Y
    $186F: 60         RTS           
L_1870:
    $1870: A2 00      LDX #$00      
    $1872: 8A         TXA           
L_1873:
    $1873: 9D B0 17   STA $17b0,x   
    $1876: E8         INX           
    $1877: E0 08      CPX #$08      
    $1879: D0 F8      BNE $1873        ; → L_1873
    $187B: 4C 50 10   JMP $1050        ; → L_1050
; ----- data gap $187E-$1884 (7 bytes) -----

sub_1885:
    $1885: BD 74 17   LDA $1774,x   
    $1888: D0 03      BNE $188d        ; → L_188D
    $188A: 9D 92 17   STA $1792,x   
L_188D:
    $188D: 60         RTS           
; ----- data gap $188E-$6A77 (20970 bytes) -----

