---
source_url: local: tmp/dmc_hunt/DeepSID/ (local DeepSID source tree); https://deepsid.chordian.net (live site)
fetched_via: local read (DeepSID source tree in tmp/dmc_hunt/DeepSID/); direct (live site, limited response)
fetch_date: 2026-06-17
author: DeepSID (Chordian / Bo Zimmermann); jsSID modifications noted inline
content_date: local tree: pre-2026 snapshot; live site: ongoing
reliability: primary (local source analysis); secondary (live site inference)
---

# DeepSID — David Whittaker Player Notes

## Player label in DeepSID

From `tmp/dmc_hunt/DeepSID/php/pretty_player_names.php`:

```php
'David_Whittaker' => 'David Whittaker\'s player',
```

DeepSID displays "David Whittaker's player" as the human-readable engine name
when sidid identifies a SID as `David_Whittaker`. This is a **single label** —
no sub-variant names or separate entries (consistent with the sidid database
having one block for all Whittaker variants).

## Whittaker player workaround in jsSID

DeepSID's JavaScript SID emulator (`js/handlers/jsSID-modified.js`) contains
an explicit workaround for the Whittaker player. This is one of only ~4
player-specific workarounds in the entire jsSID codebase (alongside Galway/Rubicon
CIA timer fix and CJ in the USA memory-mirror fix).

### The workaround (line 709)

```javascript
if(addr==0xD404 && !(memory[0xD404]&1)) ADSRstate[0]&=0x3E;
if(addr==0xD40B && !(memory[0xD40B]&1)) ADSRstate[1]&=0x3E;
if(addr==0xD412 && !(memory[0xD412]&1)) ADSRstate[2]&=0x3E;
//Whittaker player workaround
```

This fires on **every write to any voice control register** when the gate bit
is written LOW (gate-off). For all three voices ($D404 V1, $D40B V2, $D412 V3):

- `!(memory[0xD404]&1)` — true when the newly-written control value has gate=0
- `ADSRstate[0]&=0x3E` — clear the ATTACK_BITMASK and DECAYSUSTAIN_BITMASK bits
  (keeping only bits 0, 6, 7 = gate-current, hold-zero, and one other)

### Consequence (line 922)

```javascript
if (prevgate) {
    ADSRstate[channel] &= 0xFF-(GATE_BITMASK|ATTACK_BITMASK|DECAYSUSTAIN_BITMASK);
}
//falling edge (with Whittaker workaround this never happens, but should be here)
```

With the workaround active, the ADSR state is pre-cleared before the normal
"falling edge" handler can fire — so the ADSR state machine effectively **skips
the release phase** when Whittaker writes gate=0. The comment acknowledges this
suppresses normal release behaviour.

### What this tells us about Whittaker's note-trigger model

Whittaker's driver issues a rapid gate-off / gate-on pair in consecutive writes:
```
STA $D404, value = $2x   ; gate=0, waveform=pulse (0x40) or saw (0x20)
STA $D404, value = $2x+1 ; gate=1, same waveform
```
(Or via `STX; INX; STX` where X holds the waveform byte and X+1 = waveform|gate.)

The intended effect is a **hard note re-trigger**: clear the SID chip state and
start the envelope from Attack. Without the workaround, jsSID would enter a
Release phase between the two writes, producing an audible click or decay before
the new note starts. The workaround short-circuits Release so the new Attack
starts immediately.

**USF representation implication:** The gate-off write is a **reset token**, not
a "release note" event. It should NOT be modelled as a separate note-off event
in the USF instrument model — it is part of the note-on mechanism (the driver
always pairs gate-off + gate-on as an atomic note trigger).

## Changes log mention (changes.htm)

From `tmp/dmc_hunt/DeepSID/changes.htm` (November 14, 2021):

```html
Fixed a bug that stopped autoplaying if the subtune was shorter than one second.
...Try Jason Brooke's Out Run... or David Whittaker's Paddle_Mania as examples.
```

DeepSID specifically calls out **Paddle_Mania** (41 subtunes, many very short)
as a test case for short-subtune handling. This implies Paddle_Mania is a
well-known stress-test for Whittaker player compatibility — its 41 subtunes
include many that are only a second or two long.

The mention alongside Jason Brooke's Out Run confirms DeepSID treats both
composers as using related engines (consistent with `MUSICIANS/B/Brooke_Jason/Tiger_Road.sid`
being classified as `David_Whittaker` by sidid — see `sidid_signature.md`).

## SQL note — Infection.sid copyright year

From `tmp/dmc_hunt/DeepSID/php/_update/special_updating.sql`:

```sql
UPDATE files SET copyright = "1989"
WHERE fullname LIKE "%/MUSICIANS/W/Whittaker_David/Infection.sid"
```

This is a one-off data fix setting the copyright year for `Infection.sid` to 1989.
Not technically significant, but confirms DeepSID tracks per-SID metadata beyond
what HVSC provides.

## sidid tool bundled with DeepSID

DeepSID ships an older sidid binary at `utility/sidid_100/`:

```
sidid_100/sidid.cfg       (config — 2335 lines)
sidid_100/sidid.nfo       (player documentation)
sidid_100/sidid.exe       (Windows binary)
sidid_100/sidid.c         (source)
sidid_100/sidid_old_but_works.cfg
sidid_100/sidid_newer_but_does_not_work.cfg
```

The bundled `sidid.cfg` contains the **identical 5 Whittaker patterns** as
cadaver/sidid v1.09+ and WilfredC64/player-id. The `sidid.nfo` documentation
does NOT have an entry for `David_Whittaker` (no AUTHOR/COMMENT block) — this
is consistent with both upstream nfo files also having no Whittaker entry.

The two alternate configs (`_old_but_works` / `_newer_but_does_not_work`) differ
only in formatting (`END` terminator vs no terminator + blank lines); the
**Whittaker patterns are identical in both**. The "does not work" refers to
a different parsing bug in the DeepSID tool that reads the cfg, not to any issue
with the Whittaker patterns themselves.

## Variant count — DeepSID's view

DeepSID does not document sub-variants. The `pretty_player_names.php` has one
entry; the jsSID workaround is unconditional (fires for all Whittaker-tagged SIDs,
not just specific variants). From DeepSID's perspective, Whittaker is a **single
player class** with one set of identification patterns.

## Known issue — "Paddle Mania" subtune test case

Paddle_Mania (41 subtunes, load $0B00, 13364 bytes) was used as a test case for
DeepSID's autoplay bug fix. The HVSC `songlengths` for many of its subtunes are
very short (~1 second). This is a multi-subtune edge case to keep in mind during
USF extraction.

## Summary for USF migration

| Finding | Impact |
|---------|--------|
| Single `David_Whittaker` label; no sub-variants in detection tools | All 110 detected SIDs are one migration target family |
| jsSID gate-off workaround (line 709) | Gate-off is atomic reset, not release; model as note-trigger preamble |
| Paddle_Mania 41-subtune short-subtune stress test | Verify extraction handles very short subtunes correctly |
| No STIL entries for Whittaker's own tunes | No per-tune composer notes available from HVSC |

## Leads to follow

- **DeepSID live player page** for Panther — visit
  `https://deepsid.chordian.net/?file=/MUSICIANS/W/Whittaker_David/Panther.sid`
  to see what player/engine info the live UI reports
- **DeepSID live player page** for Paddle_Mania — subtune 18 specifically was
  called out in changes.htm:
  `https://deepsid.chordian.net/?file=/MUSICIANS/W/Whittaker_David/Paddle_Mania.sid&subtune=18`
- **jsSID workaround history** — the workaround (line 709) may have a git-blame
  commit message explaining when/why it was added; check the jsSID GitHub
  (jsSID by Hermit): https://github.com/Shizmob/sidfactory2/... (or the
  original jsSID repo) for context
- **DeepSID changelog** (`changes.htm`) — search for earlier mentions of Whittaker
  to trace when the workaround was added; the current file goes back to ~2019
