---
source_url: https://csdb.dk/release/?id=59929 (+ CSDb search, Pouet, VGMPF) + local player disasm of HVSC tunes
fetched_via: curl (csdb direct, Firefox UA) + WebFetch (search/pouet/vgmpf) + local siddump/disasm
fetch_date: 2026-06-13
author: CSDb community / Chris Hülsbeck (code); player-RE section is original SIDfinity analysis
content_date: 1986–2024 (CSDb comments); player disasm = HVSC #84 tunes
reliability: primary for the vendored binary + the disasm-derived write model; secondary for CSDb metadata/comments
---

# Soundmonitor — CSDb releases, downloads, versions, + player RE

## Vendored binary (in this repo)

- `docs/vendor/sound_monitor_v1.0.t64.gz` — the **original Soundmonitor V1.0 editor**, downloaded
  from CSDb release #59929 (`getinternalfile.php/51762/sound_monitor_v1.0.t64.gz`).
- `docs/vendor/SOUND-MONITOR.prg` — extracted from the .t64. T64 dir entry:
  `name="SOUND-MONITOR" load=$0801 end=$39FC` (PRG = $0801–$39FB, 12795 data bytes + 2-byte header).
  BASIC stub: `9e 32 31 36 37` = `SYS 2167` = `$0877` → editor entry.
- NOTE: this PRG is **only the editor body $0801–$39FC**. The MusicMaster *replayer* lives at
  `$C01F–$CC00` at runtime (per the 64'er memory map); the editor copies/relocates it there (or
  HVSC rips capture the assembled $C000 image). The replayer code to decompile is therefore best
  read from an **HVSC `init=$C000 play=$C020` rip**, not from this editor PRG.

## CSDb release #59929 — Soundmonitor V1.0 (the canonical original)

- Type: **C64 Tool**, by **Chris Huelsbeck**, **October 1986**. AKA "Sound Monitor 1.0".
- Download: `http://csdb.dk/getinternalfile.php/51762/sound_monitor_v1.0.t64.gz` (2160 downloads).
- Notable comments: Steppe (2007) confirms "released in issue 10/86 of … 64'er as a type-in
  listing … massive impact on the scene"; Six asks "I take it Rockmonitor was a modified version
  of this?" → tlr: "yes." (confirms Rockmonitor = modified Soundmonitor.)

## Version / variant map (the priority-3 answer)

| CSDb id | Title | By | Date | What it is / engine signature impact |
|---------|-------|----|------|--------------------------------------|
| 59929 | **Soundmonitor V1.0** | Chris Hülsbeck | Oct 1986 | the original. Replayer init=$C000, **play=$C020** (CIA-timer driven). |
| 10198 | **Soundmonitor V1.1** | Computer Cracking Team (CCT) | 28 Dec 1986 | **the "raster speed" fix**: play called once per frame from the **raster IRQ** instead of the CIA timer; **routine entry $C475** (Steppe: "MUSIC IS PLAYED AT RASTER SPEED … ROUTINE ENTRY POINT $C475"). SIDWAVE calls it an "anti-fix" — disabling the CIA timer in the editor "the tempo capabilities go to hell." → explains the HVSC `play=$C475` cluster. Download: `getinternalfile.php/255/cct_-_soundmonitor_1_1.d64.gz`. |
| 24108 | **Soundmonitor Relocator V1.2** | MC / Dutch USA-Team (DUSAT) | 1987 | relocates the player+song to an arbitrary base. → explains the enormous load/init/play address spread in HVSC. Download: `getinternalfile.php/11895/The_Soundmonitor_Relocator_V1.2.t64`. |
| 196380 | **Soundmonitor V3.0** | Dutch USA-Team (crack) | 1987 | DUSAT's evolved branch (becomes the Rockmonitor line). |
| 33026 | **Soundmonitor on Raster Interrupt** | Super Swap Sweden | 24 Apr 1988 | another raster-IRQ install variant. |
| 151615 | **Second Soundmonitor** | — | 1991 | later variant. |
| 252163 | **OSS Soundmonitor** | — (crack) | 1987 | variant. |
| 196739 | **Soundmonitor User's Manual [hungarian]** | Cement Crew | 1988 | manual (lead). |
| 7456 / 7459 | **Soundmonitor Projekt 1 / 2** | Welle:Erdball | 2002 | music made with it (not tools). |
| — many — | **Soundmonitor V1.0** cracks | TW, RIC, TBG, 5211, … | 1986–87 | the type-in repackaged. |

### Rockmonitor lineage (= Soundmonitor + samples, by Dutch USA-Team & others)
Confirmed (namelessalgorithm + CSDb): **The Dutch USA-Team** modified Soundmonitor to support
**samples** and shipped it as **Rock Monitor** (first ~April 1987). It then forked widely. CSDb
shows a long version ladder — relevant tool releases:
- Rockmonitor II/III (DUSAT, 33038), **IV** (DUSAT 20676, also "4+" 10630 w/ Beastie Boys),
  **5 / V5.3** (RSP, HIC, TFC, FIS), **6/VI** (RSP 119091, URD 31223, TTC 237028, Rezz),
  **VIII** (CFL 59923), **V7** (System Six 1989), Rockmonitor.K, Rockmonitor Hacker.
- HVSC engine classification lumps Rockmonitor tunes under "Soundmonitor". The samples support is
  the key format delta (V1.0 has **no sample playback**; Rockmonitor adds it). Expect extra
  sound-patch bytes / a sample table in Rockmonitor rips — verify against a Rockmonitor SID before
  treating the 24-byte sound bank as universal.

### "MusicMaster" is NOT a separate release
The brief listed MusicMaster as a sibling tool. Per the 64'er memory map, **»Musicmaster« is the
name of the in-editor replayer routine itself** ($C01F–$CC00). The CSDb "MusicMaster" hits
(ids 242663/260093/103653 etc.) are unrelated games/tools. There is no standalone "MusicMaster"
Soundmonitor product — the replayer = MusicMaster.
(VGMPF also notes a separate optimized driver **"The Final Musicplayer" (1987)** given to some
composers — that's a different, later replayer, a lead worth checking if a tune won't classify.)

## HVSC engine-signature census (`hvsc84.db`, engine='Soundmonitor', 3625 tunes)

Distinct (init,play) signatures, most common first — this is what a reloc-aware decompiler must
handle:

| init   | play   | count | interpretation |
|--------|--------|-------|----------------|
| $C000  | $C020  | 1182  | **canonical V1.0 in place** (CIA-timer, MusicMaster at $C000). |
| $C000  | $0000  | 507   | V1.0 image but play installed via IRQ vector (play hooked, header play=0). |
| $C000  | $C475  | 349   | **V1.1 raster-speed entry $C475** with player still based at $C000. |
| $9FD0  | $0000  | 236   | relocated player just below $A000, IRQ-installed (DUSAT relocator pattern). |
| $CBD4  | $C020  | 207   | relocated init, canonical play. |
| $BFF0  | $C020  | 141   | relocated init below $C000. |
| $80F8  | $0000  | 99    | relocated to $8000-ish, IRQ. |
| …      | …      | …     | a long tail of unique reloc bases ($5xxx–$Fxxx) — the relocator output. |

Takeaways:
- **The data window $A000–$BFFF and player $C000 are the "home" layout** but everything is
  routinely relocated. The decompiler must find the player base (e.g. from init/play addrs +
  fingerprint the $C000 code) and read the 4-table-per-voice + sound-bank + arp tables at the
  base-relative offsets from the memory map.
- `play=$C475` ⇒ V1.1 raster build; `play=$0000` ⇒ IRQ-installed (find the install code to get
  the real play vector). `play=$C020`/`$C01F` ⇒ V1.0 MusicMaster.

## Player RE — disassembly of an HVSC V1.0 rip (PRIMARY; original analysis)

Target: `hvsc85/MUSICIANS/H/Huelsbeck_Chris/Dance_at_Night.sid` (PSID v2, real load $7000–$CBD3,
**init=$C000 play=$C020**, 1 subtune) — a Hülsbeck original at the canonical signature.
(Disassembled with an inline 6502 disassembler over the loaded 64K image.)

### Entry vectors ($C000–$C00E "Musikroutine Einsprung")
```
C000: A9 01 8D 0F C0 60     init: LDA #$01; STA $C00F; RTS   ; $C00F = "play song" flag/var
C006: 4C 67 C6              JMP $C667                         ; (C006 = alt entry)
C009: 4C C1 C7              JMP $C7C1
C00C: 4C 17 CA              JMP $CA17
C00F: ...                   variables ($C00F play-flag, $C010/$C011)
C020: 4C 67 C6              play: JMP $C667                    ; ← PSID play vector
```
So **play = $C667** (the per-frame routine). $C475 (V1.1) is the raster-IRQ wrapper that calls
the same core.

### The $C667 per-frame routine (structure)
- Reads play-state in **zero page $02C7/$02C8** (status/flags), **$02D3** (global transpose add),
  **$02CD** etc., and the song work-state in **$CC00–$CExx** (the MusicMaster variables region).
- Uses bar-address tables **`$C3B7,x` (hi) / `$C416,x` (lo)** inside the player as the *resolved*
  current-bar pointers, and indexes the per-voice step tables at **$A000/$A100/$A200/$A300**
  (voice 1), **$A400…/$A800…** (voices 2/3) and arp tables at **$AC00/$AD00** — i.e. it reads
  EXACTLY the absolute bases from the 64'er memory map. **This empirically confirms the memory
  map is the live data layout.**
- Per-sound work bytes are unpacked into a contiguous work area around **$CBFA–$CC08** and the
  $CDxx mirror, then fed to the SID.

### Note-trigger SID write sequence (gate edges — Mode-1 critical)
On a **new note** ($C590 region) the engine, per voice:
```
PW lo  -> $D402     (sound byte, <<4)
PW hi  -> $D403     (sound byte, >>4)
CTRL   -> $D404  with gate bit CLEARED (LDA $CDD6; AND #$FE)   ; gate low first
AD     -> $D405     (sound #1 attack/decay,  from $CBFB)
SR     -> $D406     (sound #2 sustain/release, from $CBFC)
FREQ lo-> $D400
FREQ hi-> $D401
(optional portamento init via JSR $C2EB if note's $CC49 bit0 set)
CTRL   -> $D404  with gate bit SET (LDA $CBFA = "waveform(keyon)")  ; gate high
```
This is the canonical **set-ADSR/PW/freq while gate low, then raise the gate** edge — the
composer must reproduce this two-write-to-$D404 ordering within the frame.

### Note-OFF / silence-all block ($C48A)
```
LDA #$00
STA $D404 ; STA $D40B ; STA $D412   (gate off on all 3 voices = control regs cleared)
STA $D417                            (clear resonance/filter routing)
LDA #$0F ; STA $D418                 (master volume = $0F, full)
```
(A universal-reset-shaped tail; useful as the composer's init/clear.)

### Per-frame steady-state write ORDER (empirical, `siddump --writelog`)
Captured from Dance_at_Night, a representative non-trigger frame
(`|W:` chunk decoded; format `cycle:reg:val`):
```
$D415,$D416   filter cutoff lo, hi            (one filter, written first)
$D402,$D403   V1 pulse width lo, hi
$D409,$D40A   V2 pulse width lo, hi
$D410,$D411   V3 pulse width lo, hi
$D400,$D401   V1 freq lo, hi
$D407,$D408   V2 freq lo, hi
$D40E,$D40F   V3 freq lo, hi
$D418         master vol / filter mode
```
**Write model = register-major, not voice-major:** each parameter (cutoff → PW → freq) is swept
across all three voices before the next parameter, and $D418 is written last. Control/$D404-style
gate writes appear only on note edges (above). Frame 0 is the classic SID reset: `$D418=$0F` then
a descending `$D417..$D400 = $00` clear, then test-bit pulses on $D404/$D40B/$D412.

This `(reg,val)`-ordered stream is the project's verification target (Mode 1, frame-by-frame
instruction sequence). For digi-bearing Rockmonitor variants, expect intra-frame sample writes
(Mode 2 territory) — out of scope for V1.0.

## Other download leads (not vendored)
- V1.1: `getinternalfile.php/255/cct_-_soundmonitor_1_1.d64.gz`
- Relocator V1.2: `getinternalfile.php/11895/The_Soundmonitor_Relocator_V1.2.t64`
- DUSAT V3.0 (id 196380), Rockmonitor IV (id 20676/10630), Rockmonitor V5 (multiple) — for the
  sample-extension format.

## Leads to follow
- **archive.org/details/64er_1986_10/** — the original magazine text (SP step-param byte layout,
  AR/S byte format, song-header first/last/loop-step fields). Best remaining primary source.
- Vendor **Rockmonitor IV/V5** (e.g. CSDb 20676 / FIS 175027) + the **DUSAT V3.0** disk to RE the
  **sample table** format delta vs V1.0 (the 24-byte sound bank likely gains sample-pointer bytes).
- Vendor **Soundmonitor Relocator V1.2** to read its relocation table (tells us exactly which
  absolute pointers get fixed up → the authoritative list of reloc-sensitive offsets).
- Disassemble a **`play=$C475`** rip to confirm the V1.1 raster wrapper is a pure call-shim around
  $C667 (vs a re-laid-out player).
- Lemon64 thread t=15402 ("Looking for Sound-Monitor … manual") may point to an English manual.
- **github.com/arnaud-neny/rePlayer** — multi-format player; check whether it carries a
  Soundmonitor/Rockmonitor reader (CSDb's "Soundmonitor" sidid is the most likely existing
  detection logic — see the sidid lead in the parsers doc).
