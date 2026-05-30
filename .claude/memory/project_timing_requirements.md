---
name: SID timing requirements (frame-accurate vs cycle-accurate)
description: When frame-accurate timing is sufficient and when cycle-precise timing is required. Affects USF design and player architecture.
type: project
originSessionId: bd8c5590-7fdb-4eda-ac35-63db9d55f189
---
**For tracker music (Commando, Monty on the Run, ~95% of HVSC):**
Frame-accurate (1/50 sec, 19656 PAL cycles) is sufficient. Cycle ordering within a frame doesn't matter for audio. Per-instruction timing within play() call is irrelevant — only per-frame state matters.

**Why:** SID's analog filter is sluggish, 24-bit phase accumulator tolerates brief glitches, ADSR rate counter operates at frame scale. PW/freq writes can happen any cycle within a frame.

**The two things that DO need precision even for tracker music:**
1. Hard-restart sequence: gate-off + ADSR-zero must precede new gate-on by ≥2 frames (Dag Lem's 33ms minimum). Off by 1 frame in wrong direction = audible ADSR malfunction.
2. Multispeed (CIA timer) songs (tempo>=12 in GT2, ~9.6%): need correct CIA phase, but still tens-of-cycles tolerant.

**For digi SIDs (FUTURE SCOPE — out of scope for Commando but planned):**
Cycle-precise. Mahoney needs $D418 writes at exactly 21 cycles ±0. Off by 1-2 cycles = audible noise. Requires CIA/NMI timer support, not regular VBI.

**For demo SIDs (FUTURE SCOPE):**
Cycle-precise. Test-bit waveform tricks ramp the phase accumulator at specific cycles. Raster-synced effects. Multispeed at 16x or higher.

**Implication for USF design:**
- Current USF (frame-quantized note events) is fine for Commando-class tracker music
- For digi: USF needs to carry sample streams with cycle timestamps
- For demos: USF needs cycle-level event timing
- The codegen and player should be designed so cycle precision can be ADDED later without restructuring (e.g., player should be CIA-timer-aware)

**Implication for verification:**
- For Commando: per-frame state comparison (bisimulation) is sufficient. Don't waste effort on cycle-perfect matching.
- For digi/demo (later): need cycle-accurate Lean 6510 model (currently shelved) with CIA timer simulation.

**Source:** Research at https://sourceforge.net/p/sidplay-residfp/wiki, Cadaver's music.html, CSDb forums, Mahoney's writeups, libsidplayfp source. Confirmed by sid_compare.py jitter classification rules.
