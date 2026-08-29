; ============================================================================
; Rob Hubbard - Heavy-Beat (1993 Collision/Electric Boyz)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc85/MUSICIANS/0-9/2NY/Heavy-Beat.sid
; Load:   $9000   Init: $9340   Play: $0000
; PSID:   1 subtune(s), default subtune 1
; Binary: $9000-$B3FF (9216 bytes)
;
; Auto-traced 485 reachable code bytes from init+play.
;
; ============================================================================

sub_9000:
    $9000: 4C 40 90   JMP $9040        ; → L_9040
sub_9003:
    $9003: 4C 87 90   JMP $9087        ; → L_9087
; ----- data gap $9006-$903F (58 bytes) -----

L_9040:
    $9040: A9 70      LDA #$70      
    $9042: A0 00      LDY #$00      
    $9044: 8D 04 DD   STA $dd04     
    $9047: 8C 05 DD   STY $dd05     
    $904A: 8C 06 DD   STY $dd06     
    $904D: 8C 07 DD   STY $dd07     
    $9050: A9 11      LDA #$11      
    $9052: 8D 0E DD   STA $dd0e     
    $9055: A9 51      LDA #$51      
    $9057: 8D 0F DD   STA $dd0f     
    $905A: AD 0D DD   LDA $dd0d     
    $905D: A9 82      LDA #$82      
    $905F: 8D 0D DD   STA $dd0d     
    $9062: A9 18      LDA #$18      
    $9064: 8D 18 D4   STA $d418      ;VOL
    $9067: A0 91      LDY #$91      
    $9069: 8C FB FF   STY $fffb     
    $906C: A9 57      LDA #$57      
    $906E: 8D FA FF   STA $fffa     
    $9071: A9 00      LDA #$00      
    $9073: 8C 86 90   STY $9086     
    $9076: 8D 82 90   STA $9082     
    $9079: 8D 83 90   STA $9083     
    $907C: 20 BD 91   JSR $91bd        ; → sub_91BD
    $907F: 60         RTS           
; ----- data gap $9080-$9086 (7 bytes) -----

L_9087:
    $9087: CE 81 90   DEC $9081     
    $908A: 30 01      BMI $908d        ; → L_908D
    $908C: 60         RTS           
L_908D:
    $908D: A9 06      LDA #$06      
    $908F: 8D 81 90   STA $9081     
    $9092: AD 83 90   LDA $9083     
    $9095: D0 61      BNE $90f8        ; → L_90F8
L_9097:
    $9097: AD 82 90   LDA $9082     
    $909A: 0A         ASL a         
    $909B: AA         TAX           
L_909C:
    $909C: BD 00 92   LDA $9200,x   
    $909F: AA         TAX           
    $90A0: E0 FE      CPX #$fe      
    $90A2: D0 06      BNE $90aa        ; → L_90AA
    $90A4: A9 57      LDA #$57      
    $90A6: 8D FA FF   STA $fffa     
    $90A9: 60         RTS           
L_90AA:
    $90AA: E0 FF      CPX #$ff      
    $90AC: D0 07      BNE $90b5        ; → L_90B5
    $90AE: E8         INX           
    $90AF: 8E 82 90   STX $9082     
    $90B2: 4C E6 91   JMP $91e6        ; → L_91E6
L_90B5:
    $90B5: AD 82 90   LDA $9082     
    $90B8: 0A         ASL a         
    $90B9: A8         TAY           
    $90BA: B9 01 92   LDA $9201,y   
    $90BD: 29 7F      AND #$7f      
    $90BF: 20 C7 91   JSR $91c7        ; → sub_91C7
    $90C2: A9 00      LDA #$00      
    $90C4: 8D 85 90   STA $9085     
    $90C7: 8A         TXA           
    $90C8: 0A         ASL a         
    $90C9: 2E 85 90   ROL $9085     
    $90CC: 0A         ASL a         
    $90CD: 2E 85 90   ROL $9085     
    $90D0: 0A         ASL a         
    $90D1: 2E 85 90   ROL $9085     
    $90D4: 0A         ASL a         
    $90D5: 2E 85 90   ROL $9085     
    $90D8: 0A         ASL a         
    $90D9: 2E 85 90   ROL $9085     
    $90DC: EA         NOP           
    $90DD: EA         NOP           
    $90DE: EA         NOP           
    $90DF: EA         NOP           
    $90E0: 8D 84 90   STA $9084     
    $90E3: AD 85 90   LDA $9085     
    $90E6: 18         CLC           
    $90E7: 69 95      ADC #$95      
    $90E9: 8D 85 90   STA $9085     
    $90EC: 8D FB 90   STA $90fb     
    $90EF: AD 84 90   LDA $9084     
    $90F2: 8D FA 90   STA $90fa     
    $90F5: AD 83 90   LDA $9083     
L_90F8:
    $90F8: AA         TAX           
    $90F9: BD 60 95   LDA $9560,x   
    $90FC: D0 21      BNE $911f        ; → L_911F
L_90FE:
    $90FE: EE 83 90   INC $9083     
    $9101: AD 83 90   LDA $9083     
    $9104: C9 20      CMP #$20      
    $9106: B0 01      BCS $9109        ; → sub_9109
    $9108: 60         RTS           
sub_9109:
    $9109: A9 00      LDA #$00      
    $910B: 8D 83 90   STA $9083     
    $910E: CE 86 90   DEC $9086     
    $9111: 10 0B      BPL $911e        ; → L_911E
    $9113: AD 82 90   LDA $9082     
    $9116: 18         CLC           
    $9117: 69 01      ADC #$01      
    $9119: 29 7F      AND #$7f      
    $911B: 8D 82 90   STA $9082     
L_911E:
    $911E: 60         RTS           
L_911F:
    $911F: A0 57      LDY #$57      
    $9121: 20 D7 91   JSR $91d7        ; → sub_91D7
    $9124: 0A         ASL a         
    $9125: 0A         ASL a         
    $9126: A8         TAY           
    $9127: B9 FC 92   LDA $92fc,y   
    $912A: 8D 64 91   STA $9164     
    $912D: 8D 85 91   STA $9185     
    $9130: D9 FD 92   CMP $92fd,y   
    $9133: 90 06      BCC $913b        ; → L_913B
    $9135: 18         CLC           
    $9136: 69 01      ADC #$01      
    $9138: 4C 3E 91   JMP $913e        ; → L_913E
L_913B:
    $913B: B9 FD 92   LDA $92fd,y   
L_913E:
    $913E: 8D A4 91   STA $91a4     
    $9141: B9 FE 92   LDA $92fe,y   
    $9144: 8D 04 DD   STA $dd04     
    $9147: A9 00      LDA #$00      
    $9149: 8D 63 91   STA $9163     
    $914C: 8D 84 91   STA $9184     
    $914F: A9 60      LDA #$60      
    $9151: 8D FA FF   STA $fffa     
    $9154: 4C FE 90   JMP $90fe        ; → L_90FE
sub_9157:
    $9157: 8D 5E 91   STA $915e     
    $915A: AD 0D DD   LDA $dd0d     
    $915D: A9 02      LDA #$02      
    $915F: 40         RTI           
; ----- data gap $9160-$9166 (7 bytes) -----

sub_9167:
    $9167: 4A         LSR a         
    $9168: 4A         LSR a         
    $9169: 09 10      ORA #$10      
    $916B: 8D 18 D4   STA $d418      ;VOL
    $916E: A9 81      LDA #$81      
    $9170: EE 63 91   INC $9163     
    $9173: D0 03      BNE $9178        ; → L_9178
    $9175: EE 64 91   INC $9164     
L_9178:
    $9178: 8D FA FF   STA $fffa     
    $917B: AD 0D DD   LDA $dd0d     
    $917E: A5 F8      LDA $f8       
    $9180: 40         RTI           
; ----- data gap $9181-$9187 (7 bytes) -----

sub_9188:
    $9188: 09 10      ORA #$10      
    $918A: 8D 18 D4   STA $d418      ;VOL
    $918D: EE 84 91   INC $9184     
    $9190: F0 0B      BEQ $919d        ; → L_919D
    $9192: A9 60      LDA #$60      
    $9194: 8D FA FF   STA $fffa     
    $9197: AD 0D DD   LDA $dd0d     
    $919A: A5 F8      LDA $f8       
    $919C: 40         RTI           
L_919D:
    $919D: EE 85 91   INC $9185     
    $91A0: AD 85 91   LDA $9185     
    $91A3: C9 A9      CMP #$a9      
    $91A5: B0 0B      BCS $91b2        ; → L_91B2
    $91A7: A9 60      LDA #$60      
    $91A9: 8D FA FF   STA $fffa     
    $91AC: AD 0D DD   LDA $dd0d     
    $91AF: A5 F8      LDA $f8       
    $91B1: 40         RTI           
L_91B2:
    $91B2: A9 57      LDA #$57      
    $91B4: 8D FA FF   STA $fffa     
    $91B7: AD 0D DD   LDA $dd0d     
    $91BA: A5 F8      LDA $f8       
    $91BC: 40         RTI           
sub_91BD:
    $91BD: 2C 86 90   BIT $9086     
    $91C0: AD 8E 90   LDA $908e     
    $91C3: 8D 81 90   STA $9081     
L_91C6:
    $91C6: 60         RTS           
sub_91C7:
    $91C7: 8D D2 91   STA $91d2     
    $91CA: AD 86 90   LDA $9086     
    $91CD: EA         NOP           
    $91CE: EA         NOP           
    $91CF: 10 F5      BPL $91c6        ; → L_91C6
    $91D1: A9 02      LDA #$02      
    $91D3: 8D 86 90   STA $9086     
L_91D6:
    $91D6: 60         RTS           
sub_91D7:
    $91D7: 8C FA FF   STY $fffa     
    $91DA: C9 FF      CMP #$ff      
    $91DC: D0 F8      BNE $91d6        ; → L_91D6
    $91DE: 68         PLA           
    $91DF: 68         PLA           
    $91E0: 20 09 91   JSR $9109        ; → sub_9109
    $91E3: 4C 97 90   JMP $9097        ; → L_9097
L_91E6:
    $91E6: 8E 83 90   STX $9083     
    $91E9: 4C 9C 90   JMP $909c        ; → L_909C
; ----- data gap $91EC-$933F (340 bytes) -----

; ======= init: =======
init:
    $9340: 78         SEI           
    $9341: A9 35      LDA #$35      
    $9343: 85 01      STA $01       
    $9345: A9 74      LDA #$74      
    $9347: 8D FE FF   STA $fffe     
    $934A: A9 93      LDA #$93      
    $934C: 8D FF FF   STA $ffff     
    $934F: A9 81      LDA #$81      
    $9351: 8D 0D DC   STA $dc0d     
    $9354: AD 0D DC   LDA $dc0d     
    $9357: A9 81      LDA #$81      
    $9359: 8D 12 D0   STA $d012     
    $935C: A9 1B      LDA #$1b      
    $935E: 8D 11 D0   STA $d011     
    $9361: A2 00      LDX #$00      
    $9363: 8E 0E DC   STX $dc0e     
    $9366: E8         INX           
    $9367: 8E 1A D0   STX $d01a     
    $936A: 8E 19 D0   STX $d019     
    $936D: A9 00      LDA #$00      
    $936F: 20 00 90   JSR $9000        ; → sub_9000
    $9372: 58         CLI           
    $9373: 60         RTS           
sub_9374:
    $9374: 48         PHA           
    $9375: 8A         TXA           
    $9376: 48         PHA           
    $9377: 98         TYA           
    $9378: 48         PHA           
    $9379: 0E 19 D0   ASL $d019     
    $937C: 20 03 90   JSR $9003        ; → sub_9003
    $937F: AD 0D DC   LDA $dc0d     
    $9382: 68         PLA           
    $9383: A8         TAY           
    $9384: 68         PLA           
    $9385: AA         TAX           
    $9386: 68         PLA           
    $9387: 40         RTI           
; ----- data gap $9388-$B3FF (8312 bytes) -----

