---
source_url: https://www.lemon64.com/forum/viewtopic.php?t=31273
fetched_via: direct
fetch_date: 2026-06-15
author: iAN CooG (listing); multiple Lemon64 users
content_date: circa 2010-2015 (thread date not captured)
reliability: secondary
---

# Lemon64 Thread: "Trackers Supporting Digital Samples" (Thread #31273)

## Relevant Excerpt

User **iAN CooG** lists trackers that support digital samples on C64:

> "Pollytracker, Rockmonitor (aka Soundmonitor aka MusicMaster), Reflextracker, Digiorganizer..."

## Interpretation

This confirms **Reflextracker's defining feature in the C64 landscape**: it is classified as a
**digi-sample tracker**, not a synthesis/waveform tracker. This matches:

- PVCF's description: "2voiced digitracker"
- tomaes on pouet.net: "2 channel digi tracker"
- The sidid.cfg signature: 16-bit fractional sample position arithmetic (D0/D1 accumulator)
- The large file sizes (10–51 KB): sample data dominates the binary

## Comparison to Listed Peers

| Tracker | Type | Notes |
|---------|------|-------|
| Pollytracker | Digi | C64-native, older |
| Rockmonitor / Soundmonitor / MusicMaster | Digi | Multiple names, C64-native |
| **Reflextracker** | **Digi** | **PC-cross; 2-voice** |
| Digiorganizer | Digi | C64-native |

Reflextracker is notable in this list as the **only PC cross-tracker** (runs on PC, exports to
C64). All others are C64-native editors.

## Classification Implication for USF

Reflextracker is **not a synthesis tracker** — there are no SID waveform, ADSR, or pulse-width
parameters to extract. The instrument data is **PCM samples** (digitised audio). The "2-voice"
architecture means: two simultaneous sample channels. The player mixes/interleaves the two
sample streams into the SID's internal digi mechanism (test-bit flip or volume-register trick).
