# SID-Wizard — CSDb / release history + version-delta digest (V1.0 → V1.92)

> **Provenance**
> - **source_urls:**
>   - CSDb V1.92: `https://csdb.dk/release/?id=221555` (Hermit, 2022)
>   - CSDb V1.8: `https://csdb.dk/release/?id=165302` (Hermit, 2018) — *page itself 503'd repeatedly; data from search index + the 1.8 manual*
>   - SourceForge files dir: `https://sourceforge.net/projects/sid-wizard/files/release/`
>   - SourceForge project page: `https://sourceforge.net/projects/sid-wizard/`
>   - Demozoo V1.5: `https://demozoo.org/productions/99999/`
>   - vitno.org (Vintage is the New Old) V1.4/V1.7 posts + HerMIDI post:
>     `https://vitno.org/2014/07/21/sid-wizard-1-7/`, `https://vitno.org/2013/02/10/sid-wizard-1-4/`,
>     `https://www.vintageisthenewold.com/hermidi-sid-wizard`
>   - **1.8 plaintext manual** (in the M64GitHub fork):
>     `https://raw.githubusercontent.com/M64GitHub/sid-wizard/m64/sid-wizard-vessel/manuals/SID-Wizard-1.8-UserManual.txt`
> - **fetched_via:** WebFetch (AI-fetch path; it solved CSDb's Cloudflare challenge where raw `curl` got
>   LEN-0 / 503). WebSearch used to triangulate dates CSDb wouldn't serve.
> - **fetch_date:** 2026-06-13
> - **author / content_date:** releases by **Hermit (Mihály Horváth)**, 2012-2022 (V1.93 = 2025, out of brief
>   scope but noted). CSDb comment dates inline below.
> - **reliability:** MIXED. SourceForge file dates + the two manuals = HIGH (primary). CSDb comment
>   thread = HIGH (author's own words). Version-delta attributions for 1.5/1.6/1.7 below are reconstructed
>   from SourceForge feature-list + vitno.org + the 1.8 manual's "new features" wording, NOT from each
>   release's own CSDb note (those pages mostly 503'd) — flagged MEDIUM where so.

---

## 1. Authoritative release timeline

From the **SourceForge `/files/release/` listing** (file timestamps — HIGH reliability up to 1.7):

| Version | Filename | Date |
|---|---|---|
| **1.0 RC** | SID-Wizard-1.0-rc.zip | **2012-07-08** |
| **1.0 stable** | SID-Wizard-1.0-stable.zip | **2012-09-01** |
| **1.2** | SID-Wizard-1.2-full-pack.zip | **2012-11-12** |
| **1.4** | SID-Wizard-1.4.zip | **2013-02-07** |
| **1.5** | SID-Wizard-1.5.zip | **2013-12-30** (Demozoo: "Hermit + Soci") |
| **1.6** | SID-Wizard-1.6.zip | **2014-02-14** |
| **1.7** | SID-Wizard-1.7.zip | **2014-07-13** |

Beyond SourceForge (project moved off SF ~2016-03; later releases on CSDb / GitHub):

| Version | Date | Source |
|---|---|---|
| **1.8** | **2018-06-03** | CSDb id 165302 (the fork is tagged "1.8.7") |
| **1.9 / 1.91** | ~2018-2022 | referenced by 1.92's "twice as fast than 1.91" note |
| **1.92** | **2022-09-04** | CSDb id 221555 |
| *(1.93)* | *2025-08-22* | *Hermit comment on the 1.92 page — outside this brief's V1.92 ceiling* |

---

## 2. V1.92 (2022-09-04) — CSDb id 221555 — release notes + comment thread

**Credits:** Code + Music = **Hermit** (Samar Productions / SIDRIP Alliance / Singular). **Rating 9.8/10**
(14 votes). Downloads on the page: `SID-Wizard-1.92-disk1.d64`, `SID-Wizard-1.92-win.zip`,
`SID-Wizard-1.92-C64-source.zip`, `sidwizard-1.92.deb`.

**Release notes (Hermit, 2022-09-04):**
- **Full 4SID support** — uses the **WebSID format proposal** (a multi-SID PSID/SID flavour) with custom
  modifications **allowing individual SIDs to play on middle / both channels** (i.e. per-SID stereo
  panning routing).
- **Twice as fast as 1.91** — PC build compiled with **GCC `-O2`**; CPU usage nearly halved.
- **SID4 channels mute/unmute** via **Shift+U / I / O**.
- **Ctrl+E (`C=+E`) pattern-finder in orderlist** improved.
- **Date field** added to SID-file generation in the PC version.

**Technically-relevant comments (verbatim-ish, dated):**
- **Hermit, 2022-09-04** — 4SID **channel-routing strategy**: WebSID format + custom mods; discussion of
  stereo routing and possible hardware-panning solutions; stereo achievable by assigning SIDs to L / R / both.
- **Frantic, 2022-09-04** — argued **mono routing is the better *default*** for multiple SIDs (vs hard L/R).
- **Hermit, 2022-12-23** — clarified **4SID PRG availability** + **NTSC auto-detection**.
- **uneksija (2022-10-26 / 2023-02-15)** — asked for **4SID native-C64 version** + hardware-mod path.
- **Collcroc123, 2022-11-05** — requested NTSC-version support (display issues).
- **apprentix, 2023-01-04** — "Thanks for Linux support." (the `.deb` PC build).
- **Hermit, 2025-03-14** — caveat about the `@`-overwrite save feature being unreliable on some
  disk-emulation systems → **`SAVING ERROR 4`** reports (El Stocko 2023-08-11) on the PC version.
- **Hermit, 2025-08-22** — "Just released SID-Wizard 1.93."
- Praise from JCH ("Very nice."), spider-j ("Awesome!"), PCH ("Genious!").

> **SIDfinity takeaway:** 4SID tunes in HVSC built with ≥v1.92 carry the **WebSID multi-SID SID-header
> flavour** with custom per-SID L/R/both routing — the SID2/3/4 base-address + channel routing matters for
> multi-chip capture, and "play on both channels" means the same SID may be addressed at two mirror windows.

---

## 3. Per-version feature DELTAS (what each release added to the format / player)

### V1.0 (2012-07/09) — first stable
Baseline: 50 instruments, 100 patterns (250-byte), 16 ($0..$F) subtunes, the SWM1 module format, normal +
light/medium players. Grammar cleanup by Dóra Kőrösi. (Manual §2.1.)

### V1.2 (2012-11-12) — format-affecting
*(Full list in `csdb_hermit_site_manual.md` §9.)* Highlights that touch the format/player:
- **NTSC machine auto-detect** → sets graphics **and the frequency-table**.
- **1st-frame waveform register now configurable** (was hardwired **$09** in SWM1; 0 still reserved).
- **Startup menu with selectable players: normal / light / medium / extra.**
- SID-Maker: **extended relocation range $0200..$FFFF**; exe.prg can switch subtunes; **normal
  vblank-synced SID output for single-speed tunes**.

### V1.4 (2013-02-07)
`sng2swm` converter; F2 playback processes preceding effects; more pattern-effects; player-info
(size/rastertime) shown in startup menu; author-info in row 26; `C=`+/- octave-select.
**(The 1.4 User Manual is the most detailed format spec — see `csdb_hermit_site_manual.md`.)**

### V1.5 (2013-12-30, "Hermit + Soci") — the big multi-SID + extras drop  *(MEDIUM: attributed via vitno + SF)*
Per the vintageisthenewold post and SourceForge feature list, this wave introduced:
- **MIDI-in** (HerMIDI hardware) + MIDI sync output (start/stop/clock).
- **2SID (stereo) version.**
- **324 new example instruments.**
- **New 'Bare' player** (the smallest driver variant — see §4).
- **Sound-FX (SFX) support.**
- Config saved to **`@SWCONFIG.PRG`** (loaded at startup).

### V1.6 (2014-02-14)  *(MEDIUM)*
- **Verdi tuning (A4=432 Hz)** + **Just-intonation** tuning options.
- **Janko keyboard layout** (chromatic; notes also on F/4/K/8 keys).
- Calculated vibrato/slide refinements.

### V1.7 (2014-07-13) — confirmed by vitno.org
Five headline features (verbatim from vitno.org):
- **"Support for 3 SID chips"** (3SID version).
- **"Independent order list-marks"** (per-track playstart markers; `C=+SPACE`).
- **"Insert entire order list column"** (`C=+DEL`).
- **"SWP – re-locatable music data / player"** (the relocatable export format — see §4/§5).
- **"Tape slow-down effect support in player."**

### V1.8 (2018-06-03) — confirmed by the 1.8 manual
Consolidation + the **"Demo" player variant**, plus the orderlist **`$F0..$FD` section-separator NOPs**
(see §4 / §6). The 1.8 manual is in plaintext (M64 fork `manuals/`) and supersedes 1.4 for multi-SID limits.

### V1.92 (2022-09-04)
**Full 4SID** (WebSID) + per-SID L/R/both routing; `-O2` 2× speed; Shift+U/I/O SID4 mute; improved
orderlist pattern-finder; SID-header Date field. (§2.)

---

## 4. Driver / player variants — the **1.8** view (supersedes 1.4's 4-column table)

The 1.8 manual lists **SIX** startup player-routine types (1.4 had 4 in its matrix). Feature presence
("lacks …" = absent in that variant):

| Variant | Size | Notable feature set |
|---|---|---|
| **Normal** | standard | calc.vibrato, detune, chord, transpose, keyboard-tracking, 11-bit filter, tempo-programs, vibrato-types, HR-types |
| **Medium** | smaller | as Normal **minus** vibrato-type, hard-restart type, frame1-waveform, PW keyboard-track, note-off table-index, subtune-jump FX |
| **Light** | smaller still | **minus** calc.vibrato/slide, detune, chord, transpose, instrument-octave, WF-arp speed, PW/filter-reset, keyboard-track, 11-bit filter |
| **Extra** | larger (Normal+) | program-tables never skipped, **FiltSwitch+Reso FX ($1F)**, **ghost-registers**, fast-tempo, vibrato preserved after pitch-slide, **note/track delay FX ($1D/$1E)** |
| **Bare** | minimal | **minus** subtune, multispeed, external-volume, filter-shift, orderlist-FX, portamento, WF-arp NOP $80, vibrato-rate FX |
| **Demo** | demo/intro | most demo features; **minus** subtune, filtershift, portamento, vibrato-frequency-FX, the small filter/detune/WF/ring/sync effects |

**Load-bearing for SIDfinity capture:**
- **"The 2SID version of SID-Wizard uses ghost-registers in ALL player types."** (Not just Extra — so any
  stereo SWM rebuild buffers writes through the RAM shadow before hitting $D4xx.) For 1SID, ghost-reg is
  Extra-only.
- `$1D`/`$1E` note/track-delay and `$1F` external-filter FX remain **Extra-only**.
- **Bare** drops portamento, multispeed, subtunes, orderlist-FX entirely — a Bare-driver tune has a much
  smaller write/feature surface.

---

## 5. Multi-SID resource limits + export ABI (from the 1.8 manual) — load-bearing

**Per-config module limits (1.8):**
| Config | Instruments | Subtunes | Patterns |
|---|---|---|---|
| **1SID (standard)** | 36 | 8 | 100 (×250 bytes) |
| **2SID (stereo)** | 30 | 2 | 105 — uses ghost-registers; independent SID2 base-address |
| **3SID** | 26 | 1 | 105 — independent SID3 base-address |
| **4SID** (v1.92) | — | — | WebSID format; per-SID L/R/both channel routing |

Player base-addresses are menu-selectable; **a clash with cartridges can happen at $DE00..$DFE0.**

**Exported-tune call convention (1.8 — the embedded-player ABI):**
```
LoadAddress       Init   (subtune number in A)
LoadAddress + 3   Play   (call once per frame, single-speed)
LoadAddress + 6   Multispeed play call   (X-SID/SDI convention — on the extra rasterlines)
LoadAddress + 9   External volume set    (volume 0..F in A)
LoadAddress + 12  SFX trigger            (only if exported with SID-Maker-SFX; X=Note, Y=Instrument, A=Length-frames)
LoadAddress + 15  Tape-slowdown effect   (only SWP-FX variant; 0..24 halftone-steps in A)
```
- **SFX:** "All FXes are essentially instruments; they override channel-3 notes during execution."
  (SFX always plays on **voice 3**.)
- **SWP relocatable export:** init takes **load-address lo-byte in X, hi-byte in Y, subtune in A**, then
  call init then play. (This is how relocatable music+player data is embedded.)
- Player still uses **2 zeropage bytes (default $fe/$ff)**, saved/restored.

---

## 6. Orderlist `$F0..$FF` — the 1.8 reading (DIFFERS from the 1.4 manual)

The 1.4 manual described `$80-$FD` as transpose/volume/track-tempo and only `$FE/$FF` as control. The **1.8**
manual documents an additional/overlapping high-byte meaning:
- `$F0..$FD` — **Separator "NOP" with a section-ID** (shown in the editor as `'-'` … `'-D'`). Cosmetic
  section markers in the orderlist; **do not** consume a pattern.
- `$FE` — **End of tune** (stop playback). **"Orderlist must not begin with $FE/$FF!"**
- `$FF` — **Jump** to the following position; if that position **≥ $80**, it's a **jump to subtune
  (pos − $80)**.

> NOTE the tension: in 1.4, `$B0..$FD` = set-track-tempo and `$80..$9F` = transpose/volume. In 1.8 the
> `$F0..$FD` band is documented as section-separator NOPs. **For the rebuild, resolve the exact high-byte
> dispatch from the SVN/Git player source (`player.asm`) per target version** — this is a known
> version-divergent area. (Flagged for the sibling source-mining agent's `*_swm_format.md`.)

---

## 7. Forks & mirrors (reference, not authoritative)

- **anarkiwi/sid-wizard** (GitHub) — the fork named in CLAUDE-context; mirrors upstream.
- **M64GitHub/sid-wizard** (branch `m64/sid-wizard-vessel`) — fork of **1.8.7** adding VESSEL-MIDI + NMI
  sync. **Contains `manuals/SID-Wizard-1.8-UserManual.txt` (plaintext)** + `sources/` + `application/`
  (d64s). Build: 64tass + exomizer + c1541 + gcc. **Best plaintext-manual mirror for 1.8.**
- **hermitsoft/sid-wizard** — SourceForge says the project relocated to `github.com/hermitsoft/`, but that
  repo path returns 404 as of fetch (may be private/renamed). Lead, not confirmed.
- Commodore.software mirror of 1.8: `https://commodore.software/downloads/.../12194-sid-wizard-1-8`.
