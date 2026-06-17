---
source_url: https://cadaver.github.io/tools/gt2nt2.zip (readme.txt)
fetched_via: curl
fetch_date: 2026-06-17
author: Lasse Oeorni (Cadaver)
content_date: 2013-06
reliability: primary
---
GT2NT2 V1.03 - GoatTracker 2 to NinjaTracker 2 song converter
Written by Cadaver (loorni@gmail.com)

Usage: gt2nt2 <infile> <outfile> [maxdur]
       gt2nt2src <infile> <outfile> [maxdur]

Input file should be a GoatTracker1 or 2 song file. gt2nt2 outputs a Ninja-
Tracker V2.03+ compatible song which can be written to a diskimage and loaded
into the editor for further editing or packing/relocating. gt2nt2src produces
a gamemusic mode module in source format, ready to be assembled into a binary
music module.

Max.duration parameter allows to control how pattern steps are combined. The
default is to use the maximum supported (65.)

Unsupported features:
- More than 127 patterns
- More than 16 subtunes
- Too long subtune orderlists, must not exceed 256 bytes with all channels
  combined
- Too complex patterns, that become more than 192 bytes when converted
- Octave 0
- Wavetable commands
- "Leave frequency unchanged" in wavetable
- Changing filter mode without changing cutoff, or vice versa
- Filter resonance control. Instead the passband value + 8 (for example 9 for
  lowpass filter) gets copied to resonance
- Pattern commands 7, C, D, E
- Vibrato (command 4) in conjunction with a new note
- Fine pulse modulations. NinjaTracker uses only the high 4 bits of the pulse
  speed values used by GoatTracker.
- Calculated (note independent) slide and vibrato speed

NinjaTracker supports only toneportamentos. Commands 1 & 2 (portamento up/down
without destination note) will be emulated by using a high or low toneportamento
target, but may not be exact in all cases.
