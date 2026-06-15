---
source_url: https://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/laxity_orig/-README-.TXT
fetched_via: direct (file downloaded to /home/jtr/sidfinity/tmp/vibrants_laxity_research/laxity_orig/)
fetch_date: 2026-06-15
author: Jens-Christian Huus (JCH)
content_date: c.1995 (from "The Complete C64 Music Collection")
reliability: primary (first-hand account by JCH)
---

# JCH's First-Hand Account of the Laxity Player

This README accompanies JCH's own tunes made in Laxity's player (~1988), found in
the zimmers.net Vibrants archive at:
`pub/cbm/c64/audio/Vibrants/laxity_orig/`

## Full Text (verbatim)

```
The complete C64 music collection                            Jens-Christian Huus

The music done in Laxity's player, 1988.

After doing "Darkness IV" in my own old player system Laxity appeared in the
scene in 1988 doing a couple of wonderful tunes in quite a different style than
I did myself. I was impressed when I heard that he did the music directly in a
machinecode monitor - I was dead tired of my own cumbersome players and his
player took very little rastertime. Somehow I managed to get my hands on a
version of his player in Turbo Assembler (this was something entirely different
on the C64, do not confuse with Borland Turbo Assembler), and I tried composing
something for fun in the assembler listing. This tune, called "L.l.l." was in
fact only 90% me as I used fragments of Laxity's original bassline. A democoder
from "2000 AD" encouraged me by telling me that it sounded surprisingly good
and quite different from what I used to do, so I continued doing tunes in
Laxity's player for a while. From the second tune, "Can't Stop", I made all
the music and instruments myself and this introtune was widely used in american
intro's. However, at Dexion's copy-party in 1988, Laxity finally approached me
and told me that he didn't want me to make music in his player - go make your
own player or get lost, he said. At that time we were competetors. I made the
final touch to the last tune, "Last One" and then went coding on my own player
system - to be called "NewPlayer" - what else! :)  To conclude the story
between Laxity and I we later gained a greater respect for each other and he
even joined Vibrants - which he is still a member of today.

The compositions became better, but are still of a very low quality.

BIRTHDAY.DAT    Birthday
                A birthday song made for the Jewels demogroup - or was it the
                group living close to Jewels? Never mind. They were celebrating
                their group and wanted such a tune. However, I am not sure if
                the birthday tune in the beginning is a danish song.

CANTSTOP.DAT    Can't Stop
                An introtune which became very popular in the United States.

GUNFIGHT.DAT    Gunfight
                I managed to code a complete Gunfight game in 1987-1988 - you
                know, the stuff with two gunfighters in each side of the screen
                shooting each other until one of them enters "BOOT HILL". This
                tune was made in "Aegis Sonix" - the only tune to be converted
                using the old method into Laxity's player.

LAST_ONE.DAT    Last One
                The last tune I made in Laxity's player until Laxity told me
                to beat it.

L_L_L.DAT       L.l.l.
                The first tune made in Laxity's. Not 100% my own composition
                since I left parts of the instruments and bassline intact.
                The name was to be short of "Laxity..." something. I can't
                remember the rest anymore! ;)

NO_BIRTH.DAT    No Birthday
                Shorter version of "Birthday" without the silly birthday song
                in the beginning.
```

---

## Key Technical Facts Extracted

1. **Laxity appeared in the scene in 1988** doing music in his own player
2. **JCH obtained a copy of the player in Turbo Assembler (C64 TA) source form**
   → The player SOURCE was in Turbo Assembler format on C64
3. **Composition method:** "did the music directly in a machinecode monitor"
   → Music data entered as raw hex bytes in a machine code monitor
4. **Player efficiency:** "his player took very little rastertime"
   → Efficient player, important for demos
5. **Music data extension is `.DAT`** (not .prg, not .sid)
   → Separate player + .DAT music data format (not a single binary)
6. **Incident:** Dexion's copy-party 1988 → Laxity banned JCH from his player
7. **JCH then coded "NewPlayer"** — which evolved into JCH NewPlayer V1, V2...V21

## Files in `laxity_orig/` (zimmers.net)

| File | Description |
|------|-------------|
| -README-.TXT | JCH's account (this document) |
| BIRTHDAY.DAT | Music data for "Birthday" (Laxity player format) |
| BIRTHDAY.SID | PSID wrapper of same tune |
| CANTSTOP.DAT | Music data for "Can't Stop" |
| CANTSTOP.SID | PSID wrapper |
| GUNFIGHT.DAT | Music data (originally Aegis Sonix, converted) |
| GUNFIGHT.SID | PSID wrapper |
| LAST_ONE.DAT | Last tune JCH made in Laxity's player |
| LAST_ONE.SID | PSID wrapper |
| L_L_L.DAT | First tune JCH made in Laxity's player |
| L_L_L.SID | PSID wrapper |
| NO_BIRTH.DAT | Shorter version of Birthday |
| NO_BIRTH.SID | PSID wrapper |

The `.DAT` files are the RAW MUSIC DATA in the Laxity format.
The `.SID` files are PSID-wrapped versions with the player embedded.

**These .DAT files are PRIMARY reverse-engineering material** — they contain pure
Laxity music data without a player, making the format easier to decode by comparing
with the .SID versions (where player code precedes the data).

---

## Implication for Decompiler

The fact that music data is in `.DAT` files separate from the player binary confirms
the Laxity format has a CLEAN SEPARATION between:
- **Player code** (separate binary, relocatable)
- **Music data** (`.DAT` file, loaded separately)

This is analogous to how the Rob Hubbard engine separates player code from tune data.
The `.DAT` files in laxity_orig/ directly show the binary music data format for
6 JCH-composed tunes from 1988.
