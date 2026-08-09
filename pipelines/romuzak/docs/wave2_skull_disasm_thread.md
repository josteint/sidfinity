---
source_url: https://c64scene.pl/viewtopic.php?t=112
fetched_via: direct (WebFetch HTML-to-markdown)
fetch_date: 2026-06-14
author: "skull" (c64scene.pl scener) + others
content_date: 2009-03 (forum post date)
reliability: secondary (WebFetch AI-summarised; thread text not verbatim-captured)
---

# Polish RE Thread — skull disassembles RoMuzak V6.3 (c64scene.pl #112)

## Status of fetch

c64scene.pl/viewtopic.php?t=112 was reachable via WebFetch.
The content was AI-summarised rather than returned verbatim (the page
rendered as markdown). Wayback Machine fetches of this URL were blocked
by the fetcher.  Web search for the thread returned no cached copies
or mirrors.

The thread content below is the **complete technical substance** that the
WebFetch model extracted. Direct addresses and quoted player strings ARE
verbatim where provided; the narrative is a paraphrase.

OPEN: Re-fetch the raw HTML via `curl -A "Mozilla/5.0" "https://c64scene.pl/viewtopic.php?t=112"`
from a live shell to capture every post verbatim.

---

## Thread Summary (English translation of Polish content)

**Forum:** c64scene.pl (Polish C64 scene forum)
**Thread ID:** 112
**Date:** March 2009
**Key participant:** "skull"

### Topic: Using RoMuzak V6.3 inside an interrupt handler

The thread was sparked by a practical problem: "skull" wanted to use the
RoMuzak V6.3 player inside a C64 interrupt handler that also ran sprite
multiplexing. The player was consuming too many raster cycles — measured
by skull as **"twenty-some raster lines per iteration"** when processing a
single channel while sprites were displayed. This made it incompatible
with skull's interrupt-driven architecture.

---

## Concrete technical claims (verbatim where quoted)

### Player identity string

The ROM player contains the literal text:

```
ROMUZAK V6.3 <W> BY OLIVER BLASNIK, <C> DIGITAL MARKETING!! 02435-1295!!
```

where `<W>` likely encodes the write date/version and `<C>` encodes the
copyright marker. The phone number `02435-1295` appears verbatim.

### Raster cost (performance measurement)

- "twenty-some raster lines" per per-channel invocation (skull's measurement,
  no cycle count given, approximate)
- Skull measured this with sprites active; the overhead was enough to cause
  sprite flicker / timing conflicts
- No exact cycle count or memory address of the timing measurement code
  is given in the recovered text

### Disassembly tool: 64COPY monitor

Skull used **64COPY** (a C64 disk-management and monitor tool for PC) to
disassemble the player binary. 64COPY includes a 6502 disassembler/monitor
mode. No specific 64COPY version or session log was captured.

### Per-channel routine structure

The thread describes "per-channel modules" that skull identified by finding
**repeated jump patterns** in the disassembly:

- The monolithic play() routine dispatches to three separate per-voice
  subroutines
- Each subroutine handles one SID voice independently
- The `JSR`/jump structure was recognizable as a repeated pattern —
  each channel handler was structurally identical

**Concrete technique:** skull separated these three channel handlers and
called them individually from his interrupt handler, one per IRQ, rather
than calling the full play() entry point that processed all three at once.
This distributed the raster cost across three interrupt slots.

### Data-swapping optimization

Skull reported that restructuring the channel calls required "data-swapping
for tracks/instruments/patterns" — implying that the per-channel routines
shared some global state (current track position, current sector pointer,
current sound/instrument number) that had to be managed per-call when
channels were split out.

This is consistent with the ROMUZAK.DOC description of the zero-page
usage: `$f8-$fb` are the used zero-page addresses (per the ZEROPAGE MOVER
documentation). The per-channel state likely occupies additional zero-page
or fixed-address locations not explicitly listed in the manual.

### Copyright / validation routine

The player includes a validation routine that:
- Checks the author text ("OLIVER BLASNIK") and metadata embedded in the
  player binary
- The validation consumed measurable cycles — skull describes it as
  "unnecessary validation overhead"
- Skull **eliminated** this routine from his modified version

**Location:** NOT given verbatim. The thread says skull identified and
removed it but gives no hex address for the validation routine.

OPEN: Disassemble V6.3 player binary to find the validation routine.
Likely pattern: LDY #$xx / LDA player_base,Y / CMP #"O" (first byte of
"OLIVER") / BNE fail_branch, looping through the string. Will appear
near the init or near a first-call-only block. Run:
`siddump --pc-trace` on a V6.3 SID and look for a block that only
fires on first invocation.

### Resolution

After extracting the per-channel handlers and removing the validation
routine, skull's modified player:
- Fit within the raster budget for sprite+music simultaneous operation
- Ran cleanly in his interrupt-driven architecture

---

## What was NOT captured

The WebFetch model did not return:
- Exact hex addresses for any routine (play entry, voice handlers,
  validation routine, zero-page slots beyond $f8-$fb)
- The exact raster-line count (only "twenty-some")
- Whether skull noted instrument-format or sector-format offsets
- The number of posts or other participants
- Any reply from Oliver Blasnik (ROM) or other knowledgeable parties

---

## Leads to follow

1. **Raw page fetch** — `curl` the page directly to get verbatim post text,
   which may contain hex addresses and disassembly fragments.
   Command: `curl -s "https://c64scene.pl/viewtopic.php?t=112" > tmp/romuzak_research/skull_thread.html`

2. **Validation routine location** — OPEN. Run `siddump --pc-trace` on a
   RoMuzak V6.3 SID (e.g. from hvsc85/MUSICIANS/D/Detert_Thomas/),
   identify the init-only block (executed once, never during play()), and
   look for a string-compare loop against the ROMUZAK V6.3 copyright string.
   This is RE work.

3. **Per-channel routine split points** — OPEN. After getting the V6.3 player
   disassembly, find the three JSR targets for voice 1/2/3. These are the
   "per-channel modules" skull found. Their X-register indexing convention
   (0 / 7 / 14 like FC, or a different stride) would tell us the voice-state
   layout immediately.
