---
source_url: (synthesized index — no single URL)
fetched_via: direct
fetch_date: 2026-06-17
author: research session 2026-06-17
content_date: 2026-06-17
reliability: secondary (synthesis)
---

# David Whittaker C64 SID Player — GitHub / Open-Source Tool Research Index

Research session: 2026-06-17. Scope: GitHub repos, open-source tools that
parse/detect the Whittaker player. Excludes: CSDb releases, HVSC docs,
Spectrum/MSX ports (deferred).

## Summary of findings

### 1. Player detection tools

| Tool | Repo | Whittaker coverage |
|---|---|---|
| SIDID (cadaver) | https://github.com/cadaver/sidid | `David_Whittaker` entry: 5 signatures |
| Player-ID (WilfredC64) | https://github.com/WilfredC64/player-id | Same 5 signatures in sidid.cfg |

Both tools use the same .cfg format; the Whittaker entry is NOT split by
variant (all known C64 variants identified by one of 5 byte-sequences).
See `github_sidid_signatures.md` for the exact bytes + RE interpretation.

### 2. C64 disassemblies in public repos

| Tune | Repo | Author | Date | Notes |
|---|---|---|---|---|
| Panther (1986) | https://github.com/realdmx/c64_6581_sid_players | dmx87 (realdmx) | 2023-04-23 | Only Whittaker file in repo; ACME asm |

**Verdict**: Only ONE C64 Whittaker disassembly exists in any public GitHub
repo as of 2026-06-17. No disassemblies of Lazy Jones, Glider Rider, Red Max,
Feud, Menace, or any other tune. The Panther disassembly is already in
`pipelines/david_whittaker/docs/src/Whittaker_David_Panther.asm` (confirm
identical to realdmx raw file).

### 3. Cross-platform player implementations (Amiga .dw format)

These implement the Amiga sibling of the C64 engine. Very useful for
variant detection and data structure layout — NOT C64 SID register drivers.

| Tool | Language | Repo | Notes |
|---|---|---|---|
| c-flod (Flod 4.1) | C | https://github.com/rofl0r/c-flod | DWPlayer.c/DWSong/DWVoice; original by Christian Corti |
| NostalgicPlayer | C# | https://github.com/neumatho/NostalgicPlayer | Most complete; detects QBall-old vs new player; 3 period tables |

See `github_cflod_amiga_player.md` and `github_nostalgicplayer_csharp.md`.

### 4. libsidplayfp / VICE / sidplayfp

No Whittaker-specific handling found. libsidplayfp emulates the full C64 at
hardware level; all player detection / SID-write attribution goes through
SIDID's signature tool, not through the emulator itself.

### 5. DeepSID / webSID

DeepSID (https://github.com/Chordian/deepsid) uses Jürgen Wothke's JavaScript
emulator for low-level SID emulation. No Whittaker-specific code found.
webSID (https://github.com/wothke/websid) is a generic C64 emulator.

## Key facts for RE

1. **Engine architecture**: music data embedded in a single binary alongside
   the player. Not a separate-data format. Each SID file = player + data.

2. **Song table**: `<speed>, <v1lo>, <v1hi>, <v2lo>, <v2hi>, <v3lo>, <v3hi>`
   = 7 bytes per sub-song on C64. Each pointer → voice track sequence.

3. **Track sequence**: fixed-size arrays of pattern pointers (Panther: 56
   entries per voice). Voiced independently.

4. **Pattern encoding**: bytes < $80 = notes; bytes $80–$93 = effects/commands
   (20 commands total in Panther). Command $91 = stop.

5. **Effects in Panther**: arpeggio (13-pattern table), freq-mod/vibrato,
   PWM sweep, portamento/glide, ADSR control, waveform select, ring mod, sync.

6. **The INX / STX $D404 double-write** is the most discriminating fingerprint
   (sidid sig 1). Appears in the gate-toggle sequence of every Whittaker tune.

7. **Frequency table**: 96 entries (8 octaves × 12 notes) — lo/hi byte tables.

8. **No variant split in sidid**: one `David_Whittaker` entry covers all
   known C64 variants. Implies same core play loop across 1984–1991 engine.

9. **Amiga variant index 0–41** (c-flod): the Amiga binary has 42 detectable
   variants; C64 likely has fewer (different hardware constraints). Correlating
   C64 subtune fingerprints to Amiga variant IDs = open research.

10. **No relocatable data**: absolute pointer addresses throughout (confirmed
    by VGMPF NES driver notes; "not relocatable unlike Tony Crowther's player").
    Each SID file is loaded at a fixed address.

## Gaps (unresolved)

- No disassemblies of early-era tunes (Lazy Jones 1984, Red Max 1986).
  These likely have a shorter command table and smaller frequency range.
- Amiga variant index 0–41 not mapped to C64 tunes.
- No confirmation whether the C64 engine has multi-sub-song support in
  any HVSC tune (Panther = 1 song; other HVSC tunes may have N songs).
- UADE eagleplayer `EP_DWhittaker.lha` — binary only, source unknown.
- exotica.org.uk Whittaker format page — Cloudflare-gated.
- fileformats.archiveteam.org Whittaker page — connection refused.

## File map (this docs session)

```
docs/github_sidid_signatures.md       — sidid/player-id byte signatures + RE interpretation
docs/github_realdmx_panther_disassembly.md  — realdmx repo: only known C64 disassembly
docs/github_cflod_amiga_player.md     — c-flod Amiga player (C, command encoding)
docs/github_nostalgicplayer_csharp.md — NostalgicPlayer C# (most complete parser)
docs/github_format_cross_platform.md  — C64/NES/Amiga/ZX format deltas + timeline
docs/src/cflod_dwplayer_notes.md      — c-flod DWPlayer.c key facts + raw URLs
docs/src/Whittaker_David_Panther.asm  — (pre-existing) dmx87 ACME disassembly
```

## Leads to follow (priority order)

1. **More C64 disassemblies**: contact dmx87 (realdmx) to request Lazy Jones
   and Glider Rider. Submit PR to c64_6581_sid_players. These are the highest-
   value artifacts for variant-diffing.
   Profile: https://github.com/realdmx

2. **sidid.nfo hex-dump**: the cadaver sidid.nfo is 45 kB binary; running
   `strings` on it might yield Whittaker-specific notes. Command:
   `curl https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo | strings | grep -i whittaker`

3. **c-flod raw source download**: fetch all 8 DWPlayer*.c/.h files (URLs in
   `src/cflod_dwplayer_notes.md`) for the complete 68000 opcode scan logic.

4. **NostalgicPlayer Effect.cs**: fetch
   https://raw.githubusercontent.com/neumatho/NostalgicPlayer/master/Source/Agents/Players/DavidWhittaker/Containers/Effect.cs
   for the effect parameter record.

5. **Amiga format archive**: locate UADE source with EP_DWhittaker; check
   aminet.net or wayback for EP_DWhittaker.lha source.

6. **exotica.org.uk**: retry from outside Cloudflare region, or use wayback:
   https://web.archive.org/web/*/https://www.exotica.org.uk/wiki/David_Whittaker_(format)

7. **CSDb Whittaker SID pages**: check Lazy Jones ($30405) and Red Max ($30428)
   CSDb pages for load/init/play addresses to compare against Panther.
   https://csdb.dk/sid/?id=30405  (Lazy Jones)
   https://csdb.dk/sid/?id=30428  (Red Max)

8. **HVSC players page**: https://hvsc.de/players — check if Whittaker appears
   in the HVSC-curated player list with any technical notes.
