---
source_url: https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg
fetched_via: WebFetch + local file /home/jtr/sidfinity/tools/sidid.cfg
fetch_date: 2026-05-25
author: Cadaver (Lasse Oorni); signatures by Ian Coog, Ice00, Ninja, Yodelking, Wilfred/HVSC, Prof. Chaos
content_date: ongoing (sidid v1.09 lineage)
reliability: primary (these byte patterns ARE the canonical definition of "Companion")
---

# What "Companion" means as a signature

There are FIVE distinct Companion-related signatures in `sidid.cfg`. Local copy at
`/home/jtr/sidfinity/tools/sidid.cfg` lines 392-403 (the WilfredC64 fork stores it under
`config/sidid.cfg`).

```
Companion
BC ?? ?? C8 98 9D 04 D4 60 END

(Sid_Sequencer)
1E 18 8B 7E FA 06 AC F3 E6 8F F8 2E 00 00 00 F0 END

(Aleatory_Composer)
1E 18 8B 7E FA 06 AC F3 E6 8F F8 2E 00 00 00 0E END

(Companion/Murray)
9D 04 D4 60 C0 80 D0 07 BD ?? ?? 9D ?? ?? 60 C0 FF D0 F0 4C END

Companion/Jay_Derrett
29 0F 0A A8 B9 ?? ?? 85 ?? B9 ?? ?? 85 ?? EE ?? ?? AD ?? ?? C9 ?? D0 END
```

## Decoding the bytes

**Companion (base)** = `LDY (?,?,?),Y` (BC abs,X) ; `INY` (C8) ; `TYA` (98) ;
`STA $D404,X` (9D 04 D4) ; `RTS` (60). This is the **classic 3-voice
waveform-write loop** — reads a per-voice waveform byte from a table, writes to
$D404/$D40B/$D412 (waveform registers). The `Y` is incremented before write,
which matches the layout where each voice slot is indexed off a shared base+Y.

**Companion/Murray** is a *superset*: it has the same `9D 04 D4 60` tail, then
`CPY #$80, BNE +7, LDA tab,X, STA tab,X, RTS, CPY #$FF, BNE -16, JMP …` — i.e.
the same waveform write plus a **wrap-on-Y=$80 / restart-on-Y=$FF** mechanism.
This is the Chris-Murray-style player (orderlist pointer wraps when it hits
$80, then re-fetches on $FF).

**Companion/Jay_Derrett** is structurally different — it does
`AND #$0F, ASL, TAY, LDA tab1,Y, STA zp, LDA tab2,Y, STA zp+1, INC ptr, LDA …,
CMP #?, BNE` — a **nibble-indexed double-table lookup with order-pointer
increment + sentinel compare**. Jay rebuilt the front end (the orderlist /
note-decoding) but kept Hubbard/Murray's waveform tail.

**Sid_Sequencer / Aleatory_Composer** — these are *programs by Vic Berry* that
embed Companion-derived player code. The fixed signature
`1E 18 8B 7E FA 06 AC F3 E6 8F F8 2E 00 00 00 ??` is data bytes (probably an
LFO/sequence table) the two variants differ only in the last byte ($F0 vs $0E).

# HVSC attributions (data/sidid_full.txt)

Players identified as Companion in HVSC (selected):
- `MUSICIANS/H/Hubbard_Rob/Up_up_and_Away.sid` → **Companion** (base)
- `MUSICIANS/H/Hubbard_Rob/Commodore_64_Music_Examples.sid` → **Companion**
- `MUSICIANS/B/Berry_Vic/*.sid` (12 files: SID_Sequencer, In_C, Bach_Sonata,
  Schillinger, Webern_Op_21, Triad, Te_Deum, Dufay, Atonal_Music, Progression,
  Sigma, Test_File) → **Companion**
- `MUSICIANS/H/Hoernell_Karl/Melonmania.sid` → **Companion**
- `MUSICIANS/C/Clever_Music/*` → mix of **Companion** and
  **Companion/Jay_Derrett** (Gyroscope, Fairlight, Back_to_the_Future = base;
  Blade_Runner, Soundwave_Tubular_Bells, Space_Doubt, Shao-Lins_Road =
  Jay_Derrett)
- `MUSICIANS/D/Derrett_Jay/*` (20 SIDs) → all **Companion/Jay_Derrett**
  (Spindizzy_USA, Death_or_Glory, Dracula, Ninja_Hamster, Lifeforce,
  Vengeance, Mandroid, Sqij, Osmium, Discovery, Stratton, Road_Warrior,
  Trigger_Happy, Counterforce, Thundercross, ZIP, Destruct, Jetboys,
  Equalizer, Traxxion)
- `MUSICIANS/R/Raeburn_Gavin/Gun_Runner.sid` → **Companion/Jay_Derrett**

The (Sid_Sequencer)/(Aleatory_Composer) sub-tags only ever fire on Vic Berry's
own programs; they're effectively "Companion seen embedded in Berry's
real-time composition tools" — not in any commercial games.

# Reading the JC64dis sidid loader

`SidId.java` in github.com/ice00/jc64 (path
`src/sw_emulator/software/SidId.java`) **dynamically reads** sidid.cfg at
runtime — JC64dis has no hardcoded Companion knowledge. It tokenises with rules
`ANY (??) / AND / END`. JC64dis the GUI tool can therefore identify a SID as
Companion and then auto-disassemble it, but its disassembler (`C64SidDasm.java`)
does NOT have Companion-specific labelling — it only has special label tables
for the SID extended-register addresses ($D41D-$D47F).
