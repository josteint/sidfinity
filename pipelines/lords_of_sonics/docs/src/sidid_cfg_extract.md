---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: direct
fetch_date: 2026-06-16
author: Cadaver (Lasse Öörni); sigs by Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos
content_date: unknown (ongoing)
reliability: primary
---

# sidid.cfg — LordsOfSonics/MS related signatures

Extracted from the cadaver/sidid repository. The following entries are
relevant to the LordsOfSonics/MS engine family.

## LordsOfSonics/MS (base signatures)

```
LordsOfSonics/MS
79 ?? ?? 48 D0 06 A4 ?? C0 04 90 02 END
AC ?? ?? AD ?? ?? 29 04 C9 04 F0 ?? BD ?? ?? 99 01 D4 BD ?? ?? 99 00 D4 BD ?? ?? 3D ?? ?? 99 04 D4 END
```

### Sub-variant: (Parsec)
Matches The Parsec Music Editor V5.1 (Mnemonic Designs, 1989).

```
(Parsec)
9D ?? ?? 9D ?? ?? 9D ?? ?? CA 10 E5 A9 ?? 8D ?? ?? A9 01 8D ?? ?? A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 ?? 8D 18 D4 A2 02 8E ?? ?? CE ?? ?? 10 06 END
```

**Binary confirmation** (from Babyface/Babes_Boogie.sid at load=$1000, offset $0132):
```
9D 21 10 9D 83 10 9D 24 10 CA 10 E5 A9 1F 8D 54 11 A9 01 8D 06 10
A2 18 A9 00 9D 00 D4 CA 10 FA 60 A9 1F 8D 18 D4 A2 02 ...
```

**Disassembly of Parsec init sequence** (load=$1000 example):
```asm
; Zero 3 voice state pairs (STA voice+0, +3, +6, +9 per voice) × 3 voices
STA $1021,X  ; 9D 21 10
STA $1083,X  ; 9D 83 10
STA $1024,X  ; 9D 24 10
DEX          ; CA
BPL *-$1B   ; 10 E5
; Set master volume
LDA #$1F     ; A9 1F
STA $1154    ; 8D 54 11
; Set song init flag
LDA #$01     ; A9 01
STA $1006    ; 8D 06 10  (byte at +6 = song counter/init flag)
; Zero SID registers
LDX #$18     ; A2 18
LDA #$00     ; A9 00
STA $D400,X  ; 9D 00 D4
DEX          ; CA
BPL *-3      ; 10 FA
RTS          ; 60
; Set filter/master vol
LDA #$1F     ; A9 1F
STA $D418    ; 8D 18 D4
LDX #$02     ; A2 02
STX $100C    ; 8E 0C 10  (voice count = 3? = X+1)
DEC $1042    ; CE 42 10
BPL $10xx   ; 10 06     (branch if not first time)
```

## X-Ample group signatures (later evolution)

```
X-Ample
9D ?? ?? BD ?? ?? 29 7F 9D ?? ?? C8 98 9D ?? ?? BD ?? ?? 29 80 9D ?? ?? BC ?? ?? B9 ?? ?? 29 0F 9D ?? ?? 9D END

(Compotech_V2.x)
A9 ?? 8D ?? ?? CE ?? ?? 10 ?? A9 ?? 8D ?? ?? A2 ?? 8A 4E ?? ?? 90 ?? 20 ?? ?? ?? ?? 69 07 AA ?? 15 90 ?? A9 ?? 09 ?? 8D END

(Sonic/SDS)
BD ?? ?? D0 1B 9D 04 D4 F0 19 A9 00 8D ?? ?? A2 00 CE ?? ?? 10 05 A9 02 8D ?? ?? 4E ?? ?? 90 B3 20 ?? ?? 8A 18 69 07 AA C9 15 90 EF A9 00 09 ?? 8D 18 D4 A9 00 8D 16 D4 A9 00 F0 12 CE ?? ?? 10 END
```

## sidid.nfo entry (tool documentation)

```
LordsOfSonics/MS
AUTHOR: Markus Schneider

(Compotech_V2.x)
NAME: Compotech
AUTHOR: Markus Schneider & Helge Kozielek
RELEASED: 1990 X-Ample Architectures
REFERENCE: https://csdb.dk/release/?id=122614

(Parsec)
NAME: The Parsec Music Editor
AUTHOR: Markus Schneider (SMC), Nic & ADT
RELEASED: 1989 Mnemonic Designs
REFERENCE: https://csdb.dk/release/?id=10744

(XTracker_V4.1x)
NAME: The Ultimate X-Tracker
AUTHOR: Tufan Uysal (SoNiC)
RELEASED: 1996 The Art Project Studios
REFERENCE: https://csdb.dk/release/?id=82320
```

Notes:
- XTracker_V4.1x appears in the same sidid.nfo section but is by a different author
  (Tufan Uysal); it likely shares some LOS-derived code or inherits from Compotech.
- sidid.nfo credits Compotech release year as 1990, but CSDb #130599 shows 1992;
  the discrepancy may indicate an earlier unreleased or private version existed in 1990.
