# SID-Wizard — Player internals, call vectors, multispeed, hard-restart, ghost regs (forum/wiki cluster)

> **Provenance**
> - **source_url (manuals):** SID-Wizard **1.4** User Manual §3.3 + §5 application-note
>   (`https://www.c64.cz/data2/download/x11/113614/SID-Wizard-1.4-UserManual.pdf`, complete 27 pp);
>   **1.5** User Manual application-note + driver section (`https://csdb.dk/getinternalfile.php/125509/SID-Wizard-1.5-UserManual.pdf`, fragment).
> - **source_url (forum):** `https://www.lemon64.com/forum/viewtopic.php?t=80378` (SID-Wizard/ML integration),
>   `https://www.lemon64.com/forum/viewtopic.php?t=86825` (playing from BASIC),
>   `https://chipmusic.org/forums/topic/7702/sidwizard-10/` (V1.0 discussion).
> - **source_url (wiki):** `https://chiptunesak.readthedocs.io/en/stable/sid.html` (multispeed/CIA model).
> - **empirical:** local parse of 1048 `Hermit/SidWizard_V1.x` PSID/RSID headers in `hvsc85/` (init→play delta).
> - **fetched_via:** PDFs → `pdftotext -layout` + Read; CSDb/ChiptuneSAK via WebFetch; Lemon64 + chipmusic
>   direct WebFetch were **HTTP 503 / 403**-blocked, so their content is from WebSearch result snippets.
> - **fetch_date:** 2026-06-13
> - **author/handle:** Hermit (manuals); forum content attributed inline.
> - **content_date:** 2012–2022.
> - **reliability:** secondary (author manuals + forum); init→play-delta section is **ground truth**.

---

## 1. Player call-vector layout (THE key fact for SIDfinity dispatch)

From the **1.4 manual §5** ("Application note to the player routine"), verbatim:

> "The initializer routine's caller address is the same as the base-address/load-address (e.g. $1000)
> which requires a subtune-number present in Accumulator (as usual with other routines too).
> The single-speed playing-address is the init-address plus 3 (e.g $1003). The multi-speed playing is
> done in the same way as XSID's/SDI's (not as Goattracker's), so the multi-speed routine's calls are to
> be performed at init-address plus 6 (e.g. $1006) beside the single-speed routine, on different
> rasterlines of course (and have much less rastertime-usage). To change volume of the tune externally,
> put the desired volume (0..F) into the Accumulator and call volume-setter routine at init-address plus
> 9 (e.g. $1009)."

So the **fixed jump-table at the load address**:

| Offset | Routine | Entry contract |
|--------|---------|----------------|
| `+0`  | **init** | subtune number in **A** |
| `+3`  | **single-speed play** | call once per frame (50 Hz PAL / 60 Hz NTSC) |
| `+6`  | **multispeed play** | call on the *extra* rasterlines (XSID/SDI convention) |
| `+9`  | **volume setter** | desired volume `0..F` in **A** (external volume control) |
| `+12` | (1.5 manual references a `LoadAddress+12` entry as well — purpose: see note) |

**The default load/init address is `$1000`** for PRG exports and **`$0F82`** for SID exports (1.4 manual
§3, SID-Maker). Both are relocatable by the exporter; the jump-table offsets `+3/+6/+9` are relative to
whatever load address was chosen, so SIDfinity reads `play = init + 3` (single-speed) from that contract.

**Empirical confirmation (1048 HVSC headers, `init→play` delta):**

```
delta = play_addr - init_addr   count
   3   (= the +3 single-speed vector)    968   ← dominant, matches the manual
  23                                      49    ← deferred-init exporter layout (play after a longer init stub)
  27                                       5
   7 / 16 / 18 / 25                      few    ← other exporter/relocation layouts
  negative (play < init)                 ~10    ← RSID / relocated tunes where init sits above play
```

Takeaway: for ~92% of HVSC SID-Wizard tunes the PSID `play` vector IS `init+3`, exactly the documented
single-speed entry. The exceptions are exporter layout variants (a longer init prologue) and the 7 RSID
files — they still honour the same *relative* `+3/+6/+9` table internally; the header `play` field just
points at a different absolute address.

---

## 2. Multispeed (MULPLY) timing — XSID/SDI model, NOT GoatTracker

SID-Wizard supports **up to 8× framespeed (≈400 Hz SID control)** without affecting speed/tempo values
(*"just like in X-SID / SDI"*, 1.4 manual §2.1). Critically:

- The multispeed engine is the **`init+6`** routine, called on the *extra* rasterlines **in addition to**
  the once-per-frame `init+3` call — it consumes much less rastertime than a full play().
- This is the **XSID/SDI split** (a light "between-frames" update), **explicitly not GoatTracker's** model
  (where the single play routine is simply called N times). So a 2×/4×/8× SID-Wizard tune is NOT just
  "play() ×N per frame" — it is one full `+3` play plus (N−1) lighter `+6` updates per frame.
- **Bare player has NO multispeed** (see `forum_versions_and_drivers.md` §2) — only Light/Medium/Normal/
  Extra do.

### How the exported PSID drives it (the CIA gotcha)

From **ChiptuneSAK** (readthedocs, secondary), verbatim:

> "Some SIDs are 'multispeed', meaning that the play routine is called more than once per frame. … For
> multispeed PSIDs to function correctly in low-fidelity emulators, the initialization routine must
> configure CIA #1 Timer A to reflect the shorter play interval relative to the frame duration."

> "VBI (Vertical Blank Interrupt): a raster interrupt will call the play routine once per frame. CIA Timer
> Interrupt: which can give easier control over how often the play routine is called per frame. … When CIA
> is used, the CIA 1 timer A cycle count defaults to its PAL or NTSC KERNAL bootup settings."

**Implication for SIDfinity's dispatch model:** a multispeed SID-Wizard PSID sets **CIA #1 Timer A** in
its init to fire the play interrupt at `framecycles / N`. This is the same situation CLAUDE.md flags as
the **CIA-timed-tune case** (PSID `speed != 0`): the per-50Hz-frame writelog bucket will straddle multiple
`+3`/`+6` invocations, so capture these tunes **per `play()` invocation** (`siddump --writelog-per-irq` /
`verify_all`'s CIA path), not per siddump frame. Single-speed SID-Wizard tunes are vblank-synced (V1.2+
*"normal vblank-sync-ed SID output for single-speed tunes"*) and use the flat per-frame path.

> ⚠ The `+6` multispeed update is a **partial** SID write (tables/slides/vibrato progression) — it does
> NOT re-emit the whole register set. Within one VBI you will see: one `+3` full update **then** the
> `+6` partial update(s). The order/grouping of writes within the frame is the signal (Mode-1 verdict);
> the cycle timestamps are not.

---

## 3. Ghost / shadow registers — what they change in the write stream

SID-Wizard buffers SID register values in RAM ("ghost"/"shadow" copies) and flushes them to `$D4xx`.
This is named in both manuals as an **Extra-only** feature for the mono builds, and as **always-on for
2SID/3SID** builds:

- 1.4 matrix row (Extra only): *"Filter/Pulsewidth/WF-program/slides **never skipped**, filt-ex.FX,
  **Ghost-reg.**"*
- 1.5 Extra prose: *"… FiltSwitch-Reso.FX, **Ghost registers**, fast tempo (0..2), vibrato is not lost
  after pitch-slide …"*
- 1.5 verbatim: *"**2SID version of SID-Wizard uses ghost-registers in all types of players.**"*

**What "ghost registers" means for the write-log:** without them, the player **skips** writing a register
on a frame where its program-table produced no change (saves rastertime). With them, every program-table /
slide value is **written unconditionally every frame** (so a held note still re-emits its PW/filter/WF
slide value each frame). Therefore:

- A mono **Normal/Light/Medium/Bare** tune emits writes only when a value *changes* (sparser stream).
- A mono **Extra** tune (or **any 2SID/3SID** tune) re-emits PW/filter/WF/slide every frame (denser
  stream — "never skipped").

This directly affects the expected per-frame write count and **must be modelled per-variant** (it is the
classic "missing/extra write" trap). The variant is recoverable from the author-info **N/M/L/E/B** tag
and the SID count (see `forum_versions_and_drivers.md`).

### SID register write ORDER (within a voice update)

The 1.4 manual register table lists the registers in the canonical SID order; the prior `research.md`
records the player's observed write order as **SR, AD, Freq, PW, Waveform** (i.e. envelope before pitch,
waveform/gate **last** so the gate edge lands after ADSR/freq are set — the standard hard-restart-safe
ordering). The gate bit transition in `$D404/$D40B/$D412` being written **after** AD/SR is the load-bearing
ordering fact for the Mode-1 (within-frame order) verdict. *(Confirm the exact per-frame order against
the source `player.asm` ghost-flush — the sibling GitHub-cluster `*_writemodel.md` covers the source.)*

---

## 4. Hard-restart (HR) — exact mechanism

From the **1.4 manual** (§3.2 + §III.1.1), verbatim:

> "There's a workaround to this that's called hard-restart. It can stabilize the SID's response to fast
> paced ADSR note-triggering sequences by resetting some registers 1-2 frames (20..40ms) before a
> sound/note actually starts ('gate-on' event)."

> "**ADHR** - The ADSR value for hard restart (get loaded to ADSR registers 1-2 frames before a new note
> is triggered)."
> "**Hard-restart timer** - 0..2 - the amount of frames for hard-restart before note-triggering."
> "**Hard-restart type** - Normal hard-restart or Staccato/aggregated mode. If Test-bit is also to be
> reset at hard-restart (Adds 1-2 frames of emphasized gap between consequent notes.)"

So HR is **per-instrument** and parametrised by:
1. **HR-ADSR (`ADHR`)** — a separate AD/SR pair written to `$D405/$D406` (etc.) during the HR window.
2. **HR timer (0..2 frames)** — how many frames *before* the note's gate-on the HR runs. `0` = no HR.
3. **HR type** — Normal, or **Staccato** with an extra **Test-bit reset** (`$08` set in the waveform
   register during the HR window → oscillator reset → emphasised inter-note gap of 1-2 frames).

Instrument control byte (per `research.md` offset 0): bit0–1 HR timer, bit2 gate-off HR, bit3 test-bit HR,
bit4–5 vibrato type, bit6 PW-reset-off, bit7 filter-reset-off.

**Write-log shape of HR (what SIDfinity must reproduce):** in the 1-2 frames before a new note's gate-on,
the player writes the instrument's HR-ADSR to `$D405/$D406`, may clear the gate (and set the test bit in
Staccato mode) in `$D404`, then on the gate-on frame writes the real ADSR + the frame-1 waveform (`$09`
default, or the settable value on V1.2+ Normal/Extra). **HR types are Normal/Extra-only** (1.4 matrix
row 3: *"Vibrato-types, Hard-restart types, Frame1 $09 waveform switch"* — Medium/Light/Bare lack them),
so a Light/Medium/Bare tune has only the simplest HR (or none).

---

## 5. Zeropage / rastertime / footprint (host-integration facts)

From 1.4 manual §5 + §2.1, verbatim:

> "The player saves and restores the 2 internally used zeropage bytes (by default **$fe and $ff**).
> Therefore inclusion is easy in any programs as virtually no zeropage is affected outside the routine
> (unless the exporter's 'PLAYERZP_VAR' in settings.cfg was set to nonzero value before compilation)."

> "The 'normal/full' player-routine's required maximal rastertime is around **$1A..$1C raster-rows**,
> slightly depending on the number of effects and table-commands used simultaneously (in 'light' version
> max. **$14..$19** rasterlines)… If less than 3 tracks are utilized in the music, rastertime of the
> player routine decreases significantly."

- Player code ≈ **2 kB** (Extra a bit more); editor+graphics ≈ 14 kB (not in exports).
- **Zeropage save/restore is Medium/Normal/Extra only** (1.4 matrix: *"Subtune-jump FX … Saving/Restoring
  zeropage"*) — Light/Bare do **not** preserve `$fe/$ff`. (Bare also drops subtune support entirely.)

---

## 6. Forum-sourced gotchas (real-world, secondary)

- **Play from BASIC / ML integration** (Lemon64 t=80378, t=86825 — content via search snippets, secondary):
  initialise at the base/load address with the subtune in A, then call `init+3` from an IRQ once per frame;
  multispeed tunes need the extra `init+6` call on additional rasterlines. (Matches the manual exactly.)
- **"Avoid FF jumps to itself"** (Hermit, V1.0 RC, CSDb id=109698) — a sequence `$FF` loop pointing at its
  own position can freeze; the editor later guards it: *"An Orderlist-effect shouldn't be right before a
  `$FF` loop-signal … the loop command will be ignored to prevent freezing"* (1.4 manual §III.3).
- **MIDI cartridges cause border flashing** (1.5 manual) — irrelevant to exports, but explains stray IRQ
  behaviour if anyone traces the *editor* rather than an exported tune.
- **Warm-reset launcher** is `SYS 2061` (BASIC) — editor recovery, not a player concern.
- **SID-type old/new (6581/8580)** export setting is auto-detected; it sets the PSID header model bits but
  does not change the `$D4xx` write stream.

---

## Cross-references
- Multi-SID write-address mapping + empirical HVSC header survey → `forum_multisid_writemap.md`
- Version timeline + driver-variant feature matrix (which effects each variant emits) → `forum_versions_and_drivers.md`
- SWM byte-stream musical semantics + source-level write model → sibling `csdb_hermit_site_manual.md` / `*_writemodel.md`
