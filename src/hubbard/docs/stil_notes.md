---
source_url: local: /home/jtr/sidfinity/data/C64Music/DOCUMENTS/STIL.txt
fetched_via: local read
fetch_date: 2026-04-11
author: Rob Hubbard (RH comments); STIL maintainers
content_date: unknown
reliability: primary
---
# Rob Hubbard STIL Notes (Technical Highlights)

Extracted from `/home/jtr/sidfinity/data/C64Music/DOCUMENTS/STIL.txt`.

General STIL note: "People have often stolen Hubbard's routine causing some
tunes to be falsely credited to him. Hubbard's own comments are denoted (RH)."

## Technical Comments from Hubbard (RH)

### Delta
"Delta was based on this minimalist composition technique inspired by Glass and
a bit of Pink Floyd. It was quite hard to do and required some custom code to
the driver to do it. The music was tedious to debug."

Delta's intro allowed the user to select the instruments for each voice while
the game loaded (Mix-E-Load).

### Kentilla
"The whole thing was originally intended to be 'interactive music', responding
to the different scenes in the game. I originally wrote it to work in this
fashion, but time ran out and they couldn't wait the extra three weeks."

According to Hubbard, Kentilla and Delta were the most complicated to compose,
took the longest time, and both drove him insane.

### Human Race
"I only used 2 SID voices for all these tunes because I used the other for
SFX. I used a machine code monitor to edit music data and sound patch data on
the file while the tune was playing. This allowed me to really fine tune the
SID parameters for the music."

### Last V8
"I purposely wrote the 2 melody lines to work off one voice to make it sound
like more than 1 voice." The original release had a 7-byte bug in the player
code causing tune #1 to fall out of sync at ~1 minute. Corrected in HVSC.

### Mr Meaner
"It is really, really, difficult to byte code the swing 16th feel. You have to
define long 16th and short 16th, and then when you get some syncopated phrases
it gets really messy. So, I opted for a straight version. It refreshes faster
than 50Hz to speed the wobble chords up, and I added a bit of filter code."

Note: This confirms some songs use faster-than-50Hz refresh rates.

### International Karate
"I started exploring pentatonic things in B flat minor over different bass
notes. The middle section went into F (I think) at double tempo to liven
things up." Written over a 3 week period.

### Monty on the Run
"The middle section was an excuse to use the new pitch bend code that I wrote
for this project." (Portamento feature added for this game.)

### I, Ball
"Some of what I was trying to do was pushing the driver too much."

### Thing on a Spring
"Thing On A Spring was actually something I wrote to test my first driver."

### Sanxion
"Inspired by Zoolook by Jarre. I think the synth solo is very melodic."

### Mega Apocalypse
First C64 game to have three channel music AND samples playing during gameplay.
Samples by Simon Nicol.

### BMX Kidz
The sampled voice saying "Go!" is actually Hubbard himself.

### Commando
"I went down to their office and started working on it late at night, and
worked on it through the night. I took one listen to the original arcade
version. I just did what I wanted to do. By the time everyone arrived at
8.00am in the morning, I had loaded the main tune on every C64 in the building!"

### Sun Never Shines (RobTracker conversion)
"A highlight of this is an extra bit of code to emulate the Sample & Hold that
was in the original."

### Dragons Lair Part II
"All the tunes for Dragons Lair 2 were written in 1 afternoon. I sat at the
keyboard and just recorded myself playing for 3 hours!!"

## Bug Notes

### Last V8
Seven bytes of player code were incorrect in the original release, causing
the main theme to fall out of sync at ~1 minute. Corrected in HVSC.

### Thrust
Review copies had a bugged loader that corrupted the instrument data, causing
"horrible screeching noise playing to drums" instead of the intended sounds.

### Thing on a Spring
Early driver bug: "The first time the driver runs, the note on voice 3 is
skipped."

### Skate or Die
Many cracked versions played at incorrect speed. HVSC version verified by
Hubbard and against the original.

## Pandora
"For quite a while it was suggested that someone used Rob's routine for this
game. However Rob has confirmed he did do it."

## Samantha Fox Strip Poker
Although credited to "John York", it was really done by Rob Hubbard. "John
York was the first name that I thought of and used as an alias."

## Auf Wiedersehen Monty
Tune #1 is a joint venture between Rob Hubbard and Ben Daglish. The other
sub-tunes were done by Rob Hubbard, some arranged on paper by Ben Daglish.
