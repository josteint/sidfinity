; ============================================================================
; Rob Hubbard - Maniac (1983 Access Software Inc.)
; ANNOTATED DISASSEMBLY (auto-generated seed; awaiting hand annotation)
; ============================================================================
;
; Binary: hvsc84/MUSICIANS/K/Kleimeyer_Paul/Maniac.sid
; Load:   $7580   Init: $7580   Play: $7587
; PSID:   1 subtune(s), default subtune 1
; Binary: $7580-$943F (7872 bytes)
;
; Auto-traced 741 reachable code bytes from init+play.
;
; ============================================================================

; ======= init: =======
init:
    $7580: A9 01      LDA #$01      
    $7582: 8D 88 75   STA $7588     
    $7585: D0 21      BNE $75a8        ; → L_75A8
; ======= play: =======
play:
    $7587: A9 00      LDA #$00      
    $7589: D0 31      BNE $75bc        ; → L_75BC
    $758B: 60         RTS           
; ----- data gap $758C-$758C (1 bytes) -----

L_758D:
    $758D: AD 04 D4   LDA $d404      ;V1_CTRL
    $7590: 29 FE      AND #$fe      
    $7592: 8D 04 D4   STA $d404      ;V1_CTRL
    $7595: AD 0B D4   LDA $d40b      ;V2_CTRL
    $7598: 29 FE      AND #$fe      
    $759A: 8D 0B D4   STA $d40b      ;V2_CTRL
    $759D: AD 12 D4   LDA $d412      ;V3_CTRL
    $75A0: 29 FE      AND #$fe      
    $75A2: 8D 04 D4   STA $d404      ;V1_CTRL
    $75A5: 60         RTS           
; ----- data gap $75A6-$75A7 (2 bytes) -----

L_75A8:
    $75A8: A9 00      LDA #$00      
    $75AA: 8D 44 79   STA $7944     
    $75AD: 8D 46 79   STA $7946     
    $75B0: 4C E5 77   JMP $77e5        ; → L_77E5
sub_75B3:
    $75B3: B9 50 79   LDA $7950,y   
    $75B6: 8D 45 79   STA $7945     
    $75B9: 4C 2A 76   JMP $762a        ; → L_762A
L_75BC:
    $75BC: CE 45 79   DEC $7945     
    $75BF: F0 03      BEQ $75c4        ; → L_75C4
    $75C1: 60         RTS           
; ----- data gap $75C2-$75C3 (2 bytes) -----

L_75C4:
    $75C4: AC 41 79   LDY $7941     
    $75C7: B9 50 79   LDA $7950,y   
    $75CA: 8D 45 79   STA $7945     
    $75CD: EE 43 79   INC $7943     
    $75D0: B9 90 7E   LDA $7e90,y   
    $75D3: CD 42 79   CMP $7942     
    $75D6: D0 0B      BNE $75e3        ; → L_75E3
    $75D8: B9 10 7F   LDA $7f10,y   
    $75DB: CD 43 79   CMP $7943     
    $75DE: 90 11      BCC $75f1        ; → L_75F1
    $75E0: 4C D9 76   JMP $76d9        ; → L_76D9
L_75E3:
    $75E3: AD 49 79   LDA $7949     
    $75E6: CD 43 79   CMP $7943     
    $75E9: 90 03      BCC $75ee        ; → L_75EE
    $75EB: 4C D9 76   JMP $76d9        ; → L_76D9
L_75EE:
    $75EE: 4C DA 77   JMP $77da        ; → L_77DA
L_75F1:
    $75F1: EE 41 79   INC $7941     
    $75F4: AC 40 79   LDY $7940     
    $75F7: B9 E8 7F   LDA $7fe8,y   
    $75FA: CD 41 79   CMP $7941     
    $75FD: 90 03      BCC $7602        ; → L_7602
    $75FF: 4C 99 76   JMP $7699        ; → L_7699
L_7602:
    $7602: EE 40 79   INC $7940     
    $7605: AD 4A 79   LDA $794a     
    $7608: CD 40 79   CMP $7940     
    $760B: 90 03      BCC $7610        ; → L_7610
    $760D: 4C 90 76   JMP $7690        ; → L_7690
L_7610:
    $7610: EA         NOP           
    $7611: A9 1B      LDA #$1b      
    $7613: 8D 04 DC   STA $dc04     
    $7616: A9 41      LDA #$41      
    $7618: 8D 05 DC   STA $dc05     
    $761B: A9 00      LDA #$00      
    $761D: 8D 88 75   STA $7588     
    $7620: EA         NOP           
    $7621: EA         NOP           
    $7622: EA         NOP           
    $7623: EA         NOP           
    $7624: EA         NOP           
    $7625: EA         NOP           
    $7626: 4C 8D 75   JMP $758d        ; → L_758D
; ----- data gap $7629-$7629 (1 bytes) -----

L_762A:
    $762A: AE 41 79   LDX $7941     
    $762D: BD 50 7A   LDA $7a50,x   
    $7630: 8D 05 D4   STA $d405      ;V1_AD
    $7633: BD 90 7A   LDA $7a90,x   
    $7636: 8D 0C D4   STA $d40c      ;V2_AD
    $7639: BD D0 7A   LDA $7ad0,x   
    $763C: 8D 13 D4   STA $d413      ;V3_AD
    $763F: BD 10 7B   LDA $7b10,x   
    $7642: 8D 06 D4   STA $d406      ;V1_SR
    $7645: BD 50 7B   LDA $7b50,x   
    $7648: 8D 0D D4   STA $d40d      ;V2_SR
    $764B: BD 90 7B   LDA $7b90,x   
    $764E: 8D 14 D4   STA $d414      ;V3_SR
    $7651: BD D0 7B   LDA $7bd0,x   
    $7654: 8D 02 D4   STA $d402      ;V1_PW_LO
    $7657: BD 10 7C   LDA $7c10,x   
    $765A: 8D 09 D4   STA $d409      ;V2_PW_LO
    $765D: BD 50 7C   LDA $7c50,x   
    $7660: 8D 10 D4   STA $d410      ;V3_PW_LO
    $7663: BD 90 7C   LDA $7c90,x   
    $7666: 8D 03 D4   STA $d403      ;V1_PW_HI
    $7669: BD D0 7C   LDA $7cd0,x   
    $766C: 8D 0A D4   STA $d40a      ;V2_PW_HI
    $766F: BD 10 7D   LDA $7d10,x   
    $7672: 8D 11 D4   STA $d411      ;V3_PW_HI
    $7675: BD 50 7D   LDA $7d50,x   
    $7678: 8D 17 D4   STA $d417      ;RES_FILT
    $767B: BD 90 7D   LDA $7d90,x   
    $767E: EA         NOP           
    $767F: EA         NOP           
    $7680: 8D 18 D4   STA $d418      ;VOL
    $7683: BD D0 7D   LDA $7dd0,x   
    $7686: 8D 15 D4   STA $d415      ;FC_LO
    $7689: BD 10 7E   LDA $7e10,x   
    $768C: 8D 16 D4   STA $d416      ;FC_HI
    $768F: 60         RTS           
L_7690:
    $7690: AC 40 79   LDY $7940     
    $7693: B9 D0 7F   LDA $7fd0,y   
    $7696: 8D 41 79   STA $7941     
L_7699:
    $7699: AC 41 79   LDY $7941     
    $769C: B9 50 7F   LDA $7f50,y   
    $769F: 8D 04 DC   STA $dc04     
    $76A2: B9 90 7F   LDA $7f90,y   
    $76A5: 8D 05 DC   STA $dc05     
    $76A8: AD 0E DC   LDA $dc0e     
    $76AB: 09 10      ORA #$10      
    $76AD: 8D 0E DC   STA $dc0e     
    $76B0: 20 B3 75   JSR $75b3        ; → sub_75B3
    $76B3: B9 50 7E   LDA $7e50,y   
    $76B6: 8D 42 79   STA $7942     
    $76B9: B9 D0 7E   LDA $7ed0,y   
    $76BC: 8D 43 79   STA $7943     
L_76BF:
    $76BF: 20 28 78   JSR $7828        ; → sub_7828
    $76C2: A2 06      LDX #$06      
L_76C4:
    $76C4: 0A         ASL a         
    $76C5: 2E 48 79   ROL $7948     
    $76C8: CA         DEX           
    $76C9: D0 F9      BNE $76c4        ; → L_76C4
    $76CB: 18         CLC           
    $76CC: 69 FF      ADC #$ff      
    $76CE: 8D 47 79   STA $7947     
    $76D1: AD 48 79   LDA $7948     
    $76D4: 69 7F      ADC #$7f      
    $76D6: 8D 48 79   STA $7948     
L_76D9:
    $76D9: 4C 64 78   JMP $7864        ; → L_7864
L_76DC:
    $76DC: C9 40      CMP #$40      
    $76DE: F0 26      BEQ $7706        ; → L_7706
    $76E0: C9 03      CMP #$03      
    $76E2: D0 04      BNE $76e8        ; → L_76E8
    $76E4: A9 00      LDA #$00      
    $76E6: F0 1A      BEQ $7702        ; → L_7702
L_76E8:
    $76E8: C9 08      CMP #$08      
    $76EA: D0 04      BNE $76f0        ; → L_76F0
    $76EC: A9 03      LDA #$03      
    $76EE: D0 12      BNE $7702        ; → L_7702
L_76F0:
    $76F0: C9 3B      CMP #$3b      
    $76F2: D0 04      BNE $76f8        ; → L_76F8
    $76F4: A9 02      LDA #$02      
    $76F6: D0 0A      BNE $7702        ; → L_7702
L_76F8:
    $76F8: C9 38      CMP #$38      
    $76FA: D0 04      BNE $7700        ; → L_7700
    $76FC: A9 01      LDA #$01      
    $76FE: D0 02      BNE $7702        ; → L_7702
L_7700:
    $7700: A9 04      LDA #$04      
L_7702:
    $7702: 8D 44 79   STA $7944     
    $7705: EA         NOP           
L_7706:
    $7706: 4C 71 78   JMP $7871        ; → L_7871
L_7709:
    $7709: F0 04      BEQ $770f        ; → L_770F
    $770B: C9 01      CMP #$01      
    $770D: D0 1A      BNE $7729        ; → L_7729
L_770F:
    $770F: 18         CLC           
    $7710: AD 47 79   LDA $7947     
    $7713: 69 10      ADC #$10      
    $7715: 85 FB      STA $fb       
    $7717: AD 48 79   LDA $7948     
    $771A: 69 00      ADC #$00      
    $771C: 85 FC      STA $fc       
    $771E: AC 43 79   LDY $7943     
    $7721: B1 FB      LDA ($fb),y   
    $7723: F0 22      BEQ $7747        ; → L_7747
    $7725: C9 64      CMP #$64      
    $7727: D0 0E      BNE $7737        ; → L_7737
L_7729:
    $7729: AE 41 79   LDX $7941     
    $772C: BD 90 79   LDA $7990,x   
    $772F: 29 FE      AND #$fe      
    $7731: 8D 04 D4   STA $d404      ;V1_CTRL
    $7734: 4C 47 77   JMP $7747        ; → L_7747
L_7737:
    $7737: A8         TAY           
    $7738: B9 81 78   LDA $7881,y   
    $773B: 8D 00 D4   STA $d400      ;V1_FREQ_LO
    $773E: B9 E0 78   LDA $78e0,y   
    $7741: 8D 01 D4   STA $d401      ;V1_FREQ_HI
    $7744: 20 31 78   JSR $7831        ; → sub_7831
L_7747:
    $7747: AD 44 79   LDA $7944     
    $774A: F0 04      BEQ $7750        ; → L_7750
    $774C: C9 02      CMP #$02      
    $774E: D0 1A      BNE $776a        ; → L_776A
L_7750:
    $7750: 18         CLC           
    $7751: AD 47 79   LDA $7947     
    $7754: 69 20      ADC #$20      
    $7756: 85 FB      STA $fb       
    $7758: AD 48 79   LDA $7948     
    $775B: 69 00      ADC #$00      
    $775D: 85 FC      STA $fc       
    $775F: AC 43 79   LDY $7943     
    $7762: B1 FB      LDA ($fb),y   
    $7764: F0 25      BEQ $778b        ; → L_778B
    $7766: C9 64      CMP #$64      
    $7768: D0 0E      BNE $7778        ; → L_7778
L_776A:
    $776A: AE 41 79   LDX $7941     
    $776D: BD D0 79   LDA $79d0,x   
    $7770: 29 FE      AND #$fe      
    $7772: 8D 0B D4   STA $d40b      ;V2_CTRL
    $7775: 4C 8B 77   JMP $778b        ; → L_778B
L_7778:
    $7778: A8         TAY           
    $7779: B9 81 78   LDA $7881,y   
    $777C: 8D 07 D4   STA $d407      ;V2_FREQ_LO
    $777F: B9 E0 78   LDA $78e0,y   
    $7782: 8D 08 D4   STA $d408      ;V2_FREQ_HI
    $7785: 20 42 78   JSR $7842        ; → sub_7842
    $7788: EA         NOP           
    $7789: EA         NOP           
    $778A: EA         NOP           
L_778B:
    $778B: AD 44 79   LDA $7944     
    $778E: F0 04      BEQ $7794        ; → L_7794
    $7790: C9 03      CMP #$03      
    $7792: D0 1A      BNE $77ae        ; → L_77AE
L_7794:
    $7794: 18         CLC           
    $7795: AD 47 79   LDA $7947     
    $7798: 69 30      ADC #$30      
    $779A: 85 FB      STA $fb       
    $779C: AD 48 79   LDA $7948     
    $779F: 69 00      ADC #$00      
    $77A1: 85 FC      STA $fc       
    $77A3: AC 43 79   LDY $7943     
    $77A6: B1 FB      LDA ($fb),y   
    $77A8: F0 25      BEQ $77cf        ; → L_77CF
    $77AA: C9 64      CMP #$64      
    $77AC: D0 0E      BNE $77bc        ; → L_77BC
L_77AE:
    $77AE: AE 41 79   LDX $7941     
    $77B1: BD 10 7A   LDA $7a10,x   
    $77B4: 29 FE      AND #$fe      
    $77B6: 8D 12 D4   STA $d412      ;V3_CTRL
    $77B9: 4C CF 77   JMP $77cf        ; → L_77CF
L_77BC:
    $77BC: A8         TAY           
    $77BD: B9 81 78   LDA $7881,y   
    $77C0: 8D 0E D4   STA $d40e      ;V3_FREQ_LO
    $77C3: B9 E0 78   LDA $78e0,y   
    $77C6: 8D 0F D4   STA $d40f      ;V3_FREQ_HI
    $77C9: 20 53 78   JSR $7853        ; → sub_7853
    $77CC: EA         NOP           
    $77CD: EA         NOP           
    $77CE: EA         NOP           
L_77CF:
    $77CF: AD 46 79   LDA $7946     
    $77D2: F0 03      BEQ $77d7        ; → L_77D7
    $77D4: 20 51 CB   JSR $cb51     
L_77D7:
    $77D7: 60         RTS           
; ----- data gap $77D8-$77D9 (2 bytes) -----

L_77DA:
    $77DA: EE 42 79   INC $7942     
    $77DD: A9 01      LDA #$01      
    $77DF: 8D 43 79   STA $7943     
    $77E2: 4C BF 76   JMP $76bf        ; → L_76BF
L_77E5:
    $77E5: EA         NOP           
    $77E6: 4C F8 77   JMP $77f8        ; → L_77F8
; ----- data gap $77E9-$77F7 (15 bytes) -----

L_77F8:
    $77F8: AC D1 7F   LDY $7fd1     
    $77FB: B9 50 79   LDA $7950,y   
    $77FE: 8D 45 79   STA $7945     
    $7801: A9 00      LDA #$00      
    $7803: 8D 0B DC   STA $dc0b     
    $7806: 8D 0A DC   STA $dc0a     
    $7809: 8D 09 DC   STA $dc09     
    $780C: 8D 08 DC   STA $dc08     
    $780F: A9 01      LDA #$01      
    $7811: 8D 40 79   STA $7940     
    $7814: EA         NOP           
    $7815: EA         NOP           
    $7816: EA         NOP           
    $7817: EA         NOP           
    $7818: EA         NOP           
    $7819: EA         NOP           
    $781A: EA         NOP           
    $781B: EA         NOP           
    $781C: EA         NOP           
    $781D: EA         NOP           
    $781E: EA         NOP           
    $781F: EA         NOP           
    $7820: 4C 90 76   JMP $7690        ; → L_7690
; ----- data gap $7823-$7827 (5 bytes) -----

sub_7828:
    $7828: A9 00      LDA #$00      
    $782A: 8D 48 79   STA $7948     
    $782D: AD 42 79   LDA $7942     
    $7830: 60         RTS           
sub_7831:
    $7831: AE 41 79   LDX $7941     
    $7834: BD 90 79   LDA $7990,x   
    $7837: 29 FE      AND #$fe      
    $7839: 8D 04 D4   STA $d404      ;V1_CTRL
    $783C: 09 01      ORA #$01      
    $783E: 8D 04 D4   STA $d404      ;V1_CTRL
    $7841: 60         RTS           
sub_7842:
    $7842: AE 41 79   LDX $7941     
    $7845: BD D0 79   LDA $79d0,x   
    $7848: 29 FE      AND #$fe      
    $784A: 8D 0B D4   STA $d40b      ;V2_CTRL
    $784D: 09 01      ORA #$01      
    $784F: 8D 0B D4   STA $d40b      ;V2_CTRL
    $7852: 60         RTS           
sub_7853:
    $7853: AE 41 79   LDX $7941     
    $7856: BD 10 7A   LDA $7a10,x   
    $7859: 29 FE      AND #$fe      
    $785B: 8D 12 D4   STA $d412      ;V3_CTRL
    $785E: 09 01      ORA #$01      
    $7860: 8D 12 D4   STA $d412      ;V3_CTRL
    $7863: 60         RTS           
L_7864:
    $7864: AD 46 79   LDA $7946     
    $7867: D0 03      BNE $786c        ; → L_786C
    $7869: 4C 06 77   JMP $7706        ; → L_7706
L_786C:
    $786C: A5 C5      LDA $c5       
    $786E: 4C DC 76   JMP $76dc        ; → L_76DC
L_7871:
    $7871: AD 44 79   LDA $7944     
    $7874: C9 04      CMP #$04      
    $7876: F0 06      BEQ $787e        ; → L_787E
    $7878: AD 44 79   LDA $7944     
    $787B: 4C 09 77   JMP $7709        ; → L_7709
L_787E:
    $787E: 4C 10 76   JMP $7610        ; → L_7610
; ----- data gap $7881-$943F (7103 bytes) -----

