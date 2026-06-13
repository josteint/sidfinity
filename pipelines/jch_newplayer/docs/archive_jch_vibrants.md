# JCH / Vibrants — author pages, released source, FTP archives

> Provenance
> - source_url: (multiple — see per-section headers)
> - fetched_via: mix of "direct" (curl / WebFetch) and "wayback 2026-06-13"
> - fetch_date: 2026-06-13
> - author of underlying material: Jens-Christian Huus (JCH) of Vibrants; CheeseCutter player by Abaddon/Triad (based on Laxity's NP21)
> - content_date: 1987–2011 (player history); pages 2009–2025
> - reliability: HIGH for chordian.net (JCH's own site) + CheeseCutter source (released asm) + funet/zimmers FTP (canonical mirror) + CSDb (scene DB). MEDIUM for secondary summaries.

This file collects the **author pages, released source archives, and FTP file
listings**. The per-version *changelog table* lives in
`archive_version_history.md`. The byte-level table/instrument format already
lives in `research.md` (do not duplicate) — this file adds the *released asm
source* that confirms it.

---

## 1. Who: Jens-Christian Huus (JCH) of Vibrants

> source_url: https://csdb.dk/scener/?id=626 + https://blog.chordian.net/computer-timeline/
> fetched_via: direct (WebFetch), 2026-06-13 | reliability: HIGH (chordian = his own site)

- Danish scener, active C64 1986–1992. Roles: Coder, Cracker, Musician,
  Webmaster. **Co-founded Vibrants** (Aug 1989, with Link; later Laxity joined).
- Runs **chordian.net** today and authored **DeepSID** (the online HVSC player,
  2018) — so chordian.net is a *primary* source for player-version facts.
- Lineage origin (per chordian timeline + sidpreservation): JCH **reverse-
  engineered Laxity's C64 player in Jun 1988** and started composing in it; later
  built his own NewPlayer + sequenced editor. This matters for parsing: the
  **JCH NewPlayer and the Laxity player are sibling engines**, and the 21+
  series was continued *by Laxity*, not JCH (see §2 + version-history doc).

Key claim (chordian timeline, verbatim): NP **v20.G4 (May 1991) = "my last
standard player on C64."** Everything numbered 21+ is by others (Laxity, Dane).

---

## 2. Released player SOURCE — the load-bearing artifacts

JCH **released the source to his players** ("JCH was kind enough to release the
source code for his players… many coders/composers wrote/improved their own
NewPlayers" — sidpreservation.6581.org/sid-trackers). The two reachable,
machine-readable asm sources today are the **CheeseCutter** players, which carry
explicit NP-lineage headers and the full data-format definition.

### 2a. CheeseCutter `player_v4.acme` — "Based on JCH NP 21.G4 by Laxity/VIB"

> source_url: https://raw.githubusercontent.com/theyamo/CheeseCutter/master/src/c64/player_v4.acme
> fetched_via: direct (curl raw.githubusercontent.com), 2026-06-13 | reliability: HIGH (released ACME asm)
> repo: https://github.com/theyamo/CheeseCutter (canonical, by theyamo/Abaddon) ; mirror https://github.com/localhost/CheeseCutter

Header verbatim:
```
;;; CCUTTER 2.x musicplayer by abad
;;; Based on JCH NP 21.G4 by Laxity/VIB
```

This file is the **single best parsing oracle we have for the NP21/CheeseCutter
data layout** — it defines the format symbolically. Captured highlights (the
exact bytes/strides the binary parser must replicate):

**Assembly-time config knobs (top of file):**
```
INSNO       = 48        ; number of instruments  (NP20.G4 = 32; NP21/CC = 48)
MULTISPEED  = TRUE      ; CIA multispeed supported
CIA_VALUE   = $4cc7     ; default CIA timer for multispeed  (== the $dc04/$dc05 value)
MULTIPLIER  = 1
BASEADDRESS = $1000     ; init=$1000, play=$1003, mplay=$1006
```

**Instrument table = 8 columns, COLUMN-MAJOR, stride = INSNO (NOT 8-byte rows):**
```
INS_AD    = 0          ; Attack/Decay
INS_SR    = 1*INSNO    ; Sustain/Release
INS_HR    = 2*INSNO    ; $x0 = HR type, $0x = arp delay count
INS_4     = 3*INSNO    ; Hard-Restart waveform
INS_FLTP  = 4*INSNO    ; Filter-table pointer
INS_PULSP = 5*INSNO    ; Pulse-table pointer ($00-$3F)
INS_7     = 6*INSNO    ; Hard-restart SR envelope value
INS_ARP   = 7*INSNO    ; Wave-table pointer
```
> PARSING NOTE: research.md describes the instrument record as "8 bytes/inst".
> The released NP21/CheeseCutter layout is **column-major**: all AD bytes, then
> all SR bytes, etc., each column INSNO entries wide. Verify per-version whether
> the on-disk binary is row-major (NP20.G4) or column-major (NP21/CC) before
> indexing. Also note the editor's field semantics differ slightly from
> research.md: byte index 6 (INS_7) = **hard-restart SR value**, index 7
> (INS_ARP) = **wave-table pointer** (research.md had G/H swapped).

**Effect command set (Super Table commands $00–$08), verbatim:**
```
$0 Slide up         $1 Slide down      $2 Hi-fi Vibrato
$3 Detune note      $4 Set ADSR        $5 Lo-fi vibrato
$6 Set wave         $7 Portamento(tie) $8 Stop portamento/slide
```
Vibrato params (from editor help text): byte1 lonibble = vibrato "feel";
byte2 hinibble = speed, lonibble = depth divider (bigger = narrower). Slide/
detune = signed 16-bit. Portamento runs until a `8-00 00` command.

**Pulse table = 4 bytes/row (the NP21/CC width), verbatim field help:**
```
byte0  Duration+direction: $00-$7F add n frames, $80-$FF subtract n frames
byte1  Add value
byte2  Initial pulse value  (NIBBLES REVERSED: $48 = $8400) ; $FF = skip/retain
byte3  Pointer to next set ($00-$3F) or $7F = stop pulse program
```

**Filter table = 4 bytes/row (NP21/CC width), verbatim field help:**
```
byte0  $00-$7F duration / $90-$F0 select filter type
byte1  add value  OR  resonance + channel mask
byte2  initial filter value  OR  $FF = skip
byte3  pointer to next set ($00-$3F)  OR  $7F = stop filter program
```

**Wave table = 2 columns, verbatim field help:**
```
col0 (transpose/loop): $00-$5F relative transpose up; $80-$DF absolute tuning
                       (unaffected by note/transpose); $7E loop-to-previous-row;
                       $7F loop-to-row (col1 = target row)
col1 (waveform/delay): $00 nothing; $01-$0F override inst wave-delay this row;
                       $10-$DF waveform = SID control reg value;
                       $E0-$EF = SID control reg $00-$0F; (loop ptr if col0=$7F)
```

**Hard-restart types (inst byte INS_HR high nibble), verbatim:**
`$00 = 3-frame restart; $40 = soft restart; $80 = hard restart; low nibble $0-$F = arpeggio delay.`

**Editor-export pointer block** (left out of finalized tunes; `EXPORT=FALSE`
region at `$0e00`/`$0fa0`/`$f000`): exposes the runtime symbol → address map
(`filttab, pulstab, inst, track1/2/3, seqlo, seqhi, cmd1, speed, …`) — useful
when locating tables in a CheeseCutter-exported SID. `version !pet "cc4.07"`.

### 2b. CheeseCutter `custplay.acme` — the CIA multispeed wrapper (Q-series mechanism)

> source_url: https://raw.githubusercontent.com/localhost/CheeseCutter/master/src/c64/custplay.acme
> fetched_via: direct (curl), 2026-06-13 | reliability: HIGH (released asm)

This is the **exact multispeed dispatch** the Q-series ("quattro") uses — a
4-byte header `[timerlo, timerhi, pplay, pinit]` then a CIA-timer-driven
sub-frame divider. Captured verbatim (this is what `verify_all`'s CIA per-IRQ
path will see for Q-series tunes):
```
play   dec ZP
       bpl $1006-2
       lda #1
       sta ZP
       jmp $1003
init   ldx #0
       stx ZP
       ldx #<$4cc7      ; CIA timer lo  -> $dc04
       ldy #>$4cc7      ; CIA timer hi  -> $dc05
       sty $dc05
       stx $dc04
       jmp $1000
```
The commented reference form shows `timer = $4cc7 / 2`, `div = 1`, i.e.
sub-frames driven by a CIA underflow with a software divider `counter`. The
G-series ("standard") has no such wrapper — single 50 Hz `play()` at $1003.

---

## 3. FTP archives — funet / zimmers (canonical Vibrants mirror)

> source_url root: http://ftp.funet.fi/pub/cbm/c64/audio/Vibrants/  (301-redirects to http://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/)
> fetched_via: direct (curl), 2026-06-13 | reliability: HIGH (canonical CBM FTP mirror)
> NOTE: the commodore.ca mirror of this tree returns HTTP 403 — use ftp.funet.fi or zimmers.net directly.

Vibrants tree top-level dirs (verbatim):
```
3x-player/  Accept/  Deek/  Drax/  JCH+HJ/  "Jens Christian Huus"/
Link/  Metal/  Scortia/  utils/   READ-ME  README
```

`Vibrants/utils/` (player relocators + rippers — the JCH/Laxity tool family):
```
Deluxe Driver-2.0.prg   Deluxe Driver-3.0.prg   Deluxe Driver-4.0.prg
Deluxe Driver-5.0.prg   "JCH Coder v1.prg"      "JCH Split v1.1.prg"
"Relocate JCH.prg"      "Relocate Laxity.prg"   VibRip50.00.prg
```
> "Relocate JCH" vs "Relocate Laxity" being separate tools is more evidence the
> JCH and Laxity players are distinct (relocation-incompatible) engines.

`Vibrants/utils/editor/` — **the JCH Editor itself + its docs**:
```
"Example Tune.prg"
"JCH Editor-1.4G.prg"
"JCH Editor-docs.prg"     (14,269 bytes, Last-Modified 2009-08-18)
```
Direct file URL (confirmed 200 OK): 
`http://www.zimmers.net/anonftp/pub/cbm/c64/audio/Vibrants/utils/editor/JCH%20Editor-docs.prg`

`Vibrants/"Jens Christian Huus"/` — only `.prg` *tunes* (06*, 09*, 10*, …, named
by player-version prefix e.g. `12jch01j.prg` = NP v12). No source here; the
source/editor live under `utils/` and `editors/` (the `editors/` index was
empty via HTTP — fetch the `.d64`/`.prg` under `utils/editor/` instead).

---

## 4. JCH's own site (chordian.net) — primary timeline + DeepSID

> source_url: https://blog.chordian.net/computer-timeline/ ; https://deepsid.chordian.net/?file=/MUSICIANS/J/JCH
> fetched_via: direct (WebFetch), 2026-06-13 | reliability: HIGH (JCH's own pages)

- **Computer Timeline** = JCH's dated personal log of every NewPlayer version he
  wrote (1987 → v20.G4 May 1991). Full extraction → `archive_version_history.md`.
- **DeepSID** (deepsid.chordian.net) classifies HVSC tunes by player; its JCH
  folder is tagged "JCH NewPlayer v3". DeepSID's player-ID strings are a useful
  cross-check for SIDId fingerprint buckets.
- Per chordian/DeepSID notes: JCH "mostly uses NP20.g4"; the most common
  NewPlayers in HVSC are **17.G0, 20.G4, 20.Q0**. ("Q-series stands for
  *quattro* = multispeed.")

---

## 5. The NP22-25 resurrection — Dane / Booze Design (2011)

> source_url: https://csdb.dk/release/?id=100406  (Wayback snapshot 20250617141300)
> fetched_via: wayback 2026-06-13 | reliability: HIGH (CSDb release record)

- **"JCH-Editor 3.1 + NP22-25"**, released by **Booze Design**, **Release Date
  6 June 2011**. Code/Music/Idea/Docs all **Dane of Booze Design**.
- Ships **NP22, NP23, NP24, NP25** ("several players" trading raster-time vs
  flexibility) + a comprehensive **English manual**.
- Downloadable artifacts (host csdb.dk):
  - `http://csdb.dk/getinternalfile.php/97829/NP22-25 docs.doc`  ← **the manual; top doc lead**
  - `http://csdb.dk/getinternalfile.php/97828/JCH 3.1+NP22-25.d64` ← editor+players disk
- So the **22–25 versions are Dane's**, not JCH's and not Laxity's — a third
  branch of the lineage (see version-history doc).

---

## 6. Reachability notes (for the next session)

| Resource | Status 2026-06-13 | How to fetch |
|---|---|---|
| chordian.net/computer-timeline | OK | WebFetch direct |
| github theyamo/CheeseCutter raw .acme | OK | curl raw.githubusercontent.com |
| ftp.funet.fi / zimmers.net Vibrants tree | OK | curl direct (funet 301→zimmers) |
| commodore.ca funet mirror | **403** | avoid; use funet/zimmers |
| theyamo.kapsi.fi/ccutter/about.html | 401 direct | **Wayback** `web/20190811215852/` |
| csdb.dk/release/?id=100406 | 503 intermittent direct | **Wayback** `web/20250617141300/` |
| docsnyderspage JCH | OK but no tech detail | (bio only — skip for format) |
