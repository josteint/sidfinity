; ============================================================================
; Rob Hubbard - Up, up & Away! (1984 Starcade)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: demo/hubbard/Up_up_and_Away_original.sid
; Load:   $C000   Init: $C900   Play: $C703
; PSID:   5 subtune(s), default subtune 1
; Binary: $C000-$C921 (2338 bytes)
;
; Auto-traced 334 reachable code bytes from init+play.
;
; ============================================================================

; ----- data gap $C000-$C6FF (1792 bytes) -----

L_C700:
    $C700: 60         RTS           
; ----- data gap $C701-$C702 (2 bytes) -----

; ======= play: =======
play:
    $C703: EE DE C6   INC $c6de     
    $C706: AD DE C6   LDA $c6de     
    $C709: C9 01      CMP #$01      
    $C70B: D0 08      BNE $c715        ; → L_C715
    $C70D: A9 00      LDA #$00      
    $C70F: 8D DE C6   STA $c6de     
    $C712: 20 BD C8   JSR $c8bd        ; → sub_C8BD
L_C715:
    $C715: EE D7 C6   INC $c6d7     
    $C718: AD D7 C6   LDA $c6d7     
    $C71B: CD D5 C6   CMP $c6d5     
    $C71E: D0 03      BNE $c723        ; → L_C723
    $C720: 4C B5 C7   JMP $c7b5        ; → L_C7B5
L_C723:
    $C723: CD D6 C6   CMP $c6d6     
    $C726: D0 D8      BNE $c700        ; → L_C700
    $C728: A9 00      LDA #$00      
    $C72A: 8D D7 C6   STA $c6d7     
    $C72D: AE C0 C6   LDX $c6c0     
    $C730: EE C0 C6   INC $c6c0     
    $C733: BC B0 C5   LDY $c5b0,x   
    $C736: A2 00      LDX #$00      
    $C738: 20 5A C7   JSR $c75a        ; → sub_C75A
    $C73B: AE C7 C6   LDX $c6c7     
    $C73E: EE C7 C6   INC $c6c7     
    $C741: BC F8 C5   LDY $c5f8,x   
    $C744: A2 07      LDX #$07      
    $C746: 20 5A C7   JSR $c75a        ; → sub_C75A
    $C749: AE CE C6   LDX $c6ce     
    $C74C: EE CE C6   INC $c6ce     
    $C74F: BC 40 C6   LDY $c640,x   
    $C752: A2 0E      LDX #$0e      
    $C754: 20 5A C7   JSR $c75a        ; → sub_C75A
    $C757: 60         RTS           
; ----- data gap $C758-$C759 (2 bytes) -----

sub_C75A:
    $C75A: 98         TYA           
    $C75B: 29 80      AND #$80      
    $C75D: F0 0A      BEQ $c769        ; → L_C769
    $C75F: 9D C1 C6   STA $c6c1,x   
    $C762: 98         TYA           
    $C763: 29 7F      AND #$7f      
    $C765: A8         TAY           
    $C766: 4C 81 C7   JMP $c781        ; → L_C781
L_C769:
    $C769: B9 00 C0   LDA $c000,y   
    $C76C: 9D 01 D4   STA $d401,x    ;V1_FREQ_HI,X
    $C76F: B9 80 C0   LDA $c080,y   
    $C772: 9D 00 D4   STA $d400,x    ;V1_FREQ_LO,X
    $C775: 20 C7 C7   JSR $c7c7        ; → sub_C7C7
    $C778: BC C4 C6   LDY $c6c4,x   
    $C77B: C8         INY           
    $C77C: 98         TYA           
    $C77D: 9D 04 D4   STA $d404,x    ;V1_CTRL,X
    $C780: 60         RTS           
L_C781:
    $C781: C0 0C      CPY #$0c      
    $C783: D0 07      BNE $c78c        ; → L_C78C
sub_C785:
    $C785: BD C4 C6   LDA $c6c4,x   
    $C788: 9D 04 D4   STA $d404,x    ;V1_CTRL,X
    $C78B: 60         RTS           
L_C78C:
    $C78C: C0 0D      CPY #$0d      
    $C78E: D0 D9      BNE $c769        ; → L_C769
    $C790: 20 85 C7   JSR $c785        ; → sub_C785
    $C793: E0 0E      CPX #$0e      
    $C795: F0 01      BEQ $c798        ; → L_C798
    $C797: 60         RTS           
L_C798:
    $C798: A9 00      LDA #$00      
    $C79A: 8D A1 C7   STA $c7a1     
    $C79D: 8D 18 D4   STA $d418      ;VOL
    $C7A0: 60         RTS           
; ----- data gap $C7A1-$C7A5 (5 bytes) -----

sub_C7A6:
    $C7A6: BD C1 C6   LDA $c6c1,x   
    $C7A9: 30 01      BMI $c7ac        ; → L_C7AC
    $C7AB: 60         RTS           
L_C7AC:
    $C7AC: 20 85 C7   JSR $c785        ; → sub_C785
    $C7AF: A9 00      LDA #$00      
    $C7B1: 9D C1 C6   STA $c6c1,x   
    $C7B4: 60         RTS           
L_C7B5:
    $C7B5: A2 00      LDX #$00      
    $C7B7: 20 A6 C7   JSR $c7a6        ; → sub_C7A6
    $C7BA: A2 07      LDX #$07      
    $C7BC: 20 A6 C7   JSR $c7a6        ; → sub_C7A6
    $C7BF: A2 0E      LDX #$0e      
    $C7C1: 20 A6 C7   JSR $c7a6        ; → sub_C7A6
    $C7C4: 60         RTS           
; ----- data gap $C7C5-$C7C6 (2 bytes) -----

sub_C7C7:
    $C7C7: 20 C9 C8   JSR $c8c9        ; → sub_C8C9
    $C7CA: EA         NOP           
    $C7CB: EA         NOP           
    $C7CC: EA         NOP           
    $C7CD: BD C3 C6   LDA $c6c3,x   
    $C7D0: 9D 03 D4   STA $d403,x    ;V1_PW_HI,X
    $C7D3: BD C5 C6   LDA $c6c5,x   
    $C7D6: 9D 05 D4   STA $d405,x    ;V1_AD,X
    $C7D9: BD C6 C6   LDA $c6c6,x   
    $C7DC: 9D 06 D4   STA $d406,x    ;V1_SR,X
    $C7DF: 60         RTS           
L_C7E0:
    $C7E0: A9 01      LDA #$01      
    $C7E2: 8D A1 C7   STA $c7a1     
    $C7E5: 60         RTS           
; ----- data gap $C7E6-$C830 (75 bytes) -----

L_C831:
    $C831: A2 00      LDX #$00      
L_C833:
    $C833: BD F0 C4   LDA $c4f0,x   
    $C836: 9D C0 C6   STA $c6c0,x   
    $C839: E8         INX           
    $C83A: E0 20      CPX #$20      
    $C83C: D0 F5      BNE $c833        ; → L_C833
    $C83E: 20 97 C8   JSR $c897        ; → sub_C897
    $C841: A9 00      LDA #$00      
    $C843: 8D 16 D4   STA $d416      ;FC_HI
    $C846: A9 00      LDA #$00      
    $C848: 8D 17 D4   STA $d417      ;RES_FILT
    $C84B: A9 0F      LDA #$0f      
    $C84D: 8D 18 D4   STA $d418      ;VOL
    $C850: 4C E0 C7   JMP $c7e0        ; → L_C7E0
; ----- data gap $C853-$C896 (68 bytes) -----

sub_C897:
    $C897: AD D8 C6   LDA $c6d8     
    $C89A: 8D 34 C7   STA $c734     
    $C89D: AD D9 C6   LDA $c6d9     
    $C8A0: 8D 35 C7   STA $c735     
    $C8A3: AD DA C6   LDA $c6da     
    $C8A6: 8D 42 C7   STA $c742     
    $C8A9: AD DB C6   LDA $c6db     
    $C8AC: 8D 43 C7   STA $c743     
    $C8AF: AD DC C6   LDA $c6dc     
    $C8B2: 8D 50 C7   STA $c750     
    $C8B5: AD DD C6   LDA $c6dd     
    $C8B8: 8D 51 C7   STA $c751     
    $C8BB: 60         RTS           
; ----- data gap $C8BC-$C8BC (1 bytes) -----

sub_C8BD:
    $C8BD: AD D0 C6   LDA $c6d0     
    $C8C0: 69 04      ADC #$04      
    $C8C2: 8D 10 D4   STA $d410      ;V3_PW_LO
    $C8C5: 8D D0 C6   STA $c6d0     
    $C8C8: 60         RTS           
sub_C8C9:
    $C8C9: E0 0E      CPX #$0e      
    $C8CB: F0 06      BEQ $c8d3        ; → L_C8D3
    $C8CD: BD C2 C6   LDA $c6c2,x   
    $C8D0: 9D 02 D4   STA $d402,x    ;V1_PW_LO,X
L_C8D3:
    $C8D3: 60         RTS           
; ----- data gap $C8D4-$C8FF (44 bytes) -----

; ======= init: =======
init:
    $C900: AA         TAX           
    $C901: BD 15 C9   LDA $c915,x   
    $C904: 8D 13 C9   STA $c913     
    $C907: BD 1D C9   LDA $c91d,x   
    $C90A: 8D 14 C9   STA $c914     
    $C90D: A9 0F      LDA #$0f      
    $C90F: 8D 18 D4   STA $d418      ;VOL
    $C912: 4C 31 C8   JMP $c831        ; → L_C831
; ----- data gap $C915-$C921 (13 bytes) -----

