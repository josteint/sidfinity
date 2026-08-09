---
source_url: local: /home/jtr/sidfinity/hvsc85/DOCUMENTS/STIL.txt
fetched_via: local read
fetch_date: 2026-06-15
author: HVSC STIL team + individual contributors
content_date: HVSC #84
reliability: primary
---

# Reflextracker — STIL Entries

Only the PVCF-authored tunes have technical STIL comments. All other Reflextracker corpus members have only title/artist credits (covers of commercial tracks) or no STIL entry.

## PVCF — Access Denied (intro) [init=$C000, the very first Reflextracker song]

```
/MUSICIANS/P/PVCF/Access_Denied_intro.sid
COMMENT: "This was done very quick & dirty, if I remember right I've had only
         3-4 hours time to compose this track in our new developed and
         finished Reflex-Tracker, a 2 channel sampletracker. Access Denied
         sample spoken by me. The bass-drumm split was make with an Amiga 500
         and converted to my C64. Later in version v1.1 of Reflex-Tracker the
         user could do this without directly in the trakker. Funny: most of
         the time in this song I use only one digichannel, after release I
         created a remix which prooves the ability of Reflex-Tracker a little
         bit better. After winning the C64 democompo at THE PARTY'94 in
         Denmark, most of the people thought our group name is 'Access Denied'"
```

**Key technical facts:**
- Reflextracker v1.0 had no built-in bass-drum splitting (had to do it on Amiga)
- v1.1 added bass-drum splitting directly in the tracker
- "2 channel sampletracker" confirmed
- Won democompo at THE PARTY'94 (Denmark, 1994)
- The song mostly uses only 1 of the 2 digi channels

## PVCF — Access Denied (remix) [init=$C006]

```
/MUSICIANS/P/PVCF/Access_Denied_remix.sid
COMMENT: "This is the remix of Access_Denied_intro.sid where I show some of the
         features of Reflex-Tracker: 2 channels of digi-sounds, faked third
         voice (drum and snare which are rendered in the bassvoice), volume,
         echoeffects and flanger. All samples by me, except the "ho ho" which
         I have sampled from the german rap song 'Edelweiß'." (PVCF)
```

**Key technical facts:**
- "2 channels of digi-sounds" confirmed
- "faked third voice (drum and snare which are rendered in the bassvoice)" = software mixing within the 2-channel DAC
- Effects demonstrated: volume control, echo, flanger
- Flanger = reverse sample playback with timing offset (likely the EOR #$01 direction toggle)
- Echo = delay between forward and reverse playback of same sample

## PVCF — Gubber [init=$C050]

```
/MUSICIANS/P/PVCF/Gubber.sid
COMMENT: "Reflex-Tracker demo song. It was only a joke :) Took about 4 hours.
         I think absolutely no one liked this song but me, I'm proud of it,
         hehe!" (PVCF)
```

## PVCF — Trance 202 [init=$C050]

```
/MUSICIANS/P/PVCF/Trance_202.sid
COMMENT: "The second Reflex-Tracker demosong, this song was released with
         Brainbeat 4 on SideB. It shows some volume effects and wave/drum
         splitting." (PVCF)
```

**Key technical facts:**
- "wave/drum splitting" = the 2-channel architecture separating melodic wave from drum
- Released on Brainbeat 4 Side B (Reflex musicdisk)

## PVCF — Originalzak [init=$C050]

```
/MUSICIANS/P/PVCF/Originalzak.sid
COMMENT: "This is the first music which was made in the finished Reflex-Tracker,
         it has no melodie or inspiration, it was more a test than a song.
         Altough it's not the first song which was made with our 2channel
         digiroutine: the first one was used as endpart in our trackmo
         'Cafe Odd'. The Cafe_Odd_end.sid digi music was composed in pure
         assembler." (PVCF)
```

**Key technical facts:**
- "2channel digiroutine" — pre-Reflextracker version existed and was hand-coded in assembler
- First FINISHED tracker song = Originalzak; first digi song at all = Cafe Odd endpart (pure asm)
- Confirms the 2-channel digi routine was developed for Cafe Odd trackmo BEFORE the Reflextracker UI was built

## PVCF — Brainbeat 3 Introrap [init=$C103]

```
/MUSICIANS/P/PVCF/Brainbeat_3_Introrap.sid
COMMENT: "Again a Reflex-Tracker song, the rap and the beats are realtime
         mixed. Rapped by myself ;) The string was ripped from Georg Brandt's
         Paranoia_Complex.sid, Tune #1, thanks to Georg! As I've made this tune
         I thought it would be a revolution, the first realtime rap on C64 and
         so... but no one, I repeat: no one! cared about ;) Later I composed
         a very long CBA&Nightshade hate hip-hop track, (they have stolen and
         cracked a game which we have made), but this song was never spread by
         our swapper Happymaker. Very sad." (PVCF)
```

**Key technical facts:**
- "Rap and beats are realtime mixed" = both digi channels active simultaneously (voice split: beats on one channel, speech on the other)
- Confirms realtime 2-channel mixing capability in the player
- First real-time speech/rap playback on C64 (PVCF's claim)

## Non-technical STIL entries for other Reflextracker corpus members

Most other STIL entries in the corpus are pure title/artist credits (covers of 90s dance/techno tracks). None contain technical information about Reflextracker's operation. Examples:

- Jonny/Dance_Now.sid: "Gonna Make You Sweat (Everybody Dance Now)" by C+C Music Factory
- Gregfeel/Be_My_Lover.sid: "Be My Lover" by La Bouche — "Sample from a CASIO CTK-670 keyboard"
- Leming/De_Prodigi.sid: "Everybody In The Place" by The Prodigy

The corpus is primarily Polish C64 scene covers of popular 90s electronic and dance music.

## STIL searches yielding zero results

Searches for the following found **nothing** in STIL.txt:
- "QuadSID" / "quad sid" / "multi-SID"
- "Reflextracker" (term not used in STIL)
- "Hinrichs" / "Kramm" / "Quiss"
- "Obsessed Maniacs"
- Gregorian/general "kb" hits
