<!--
provenance:
  topic: SID-Wizard per-version player.asm / exporter.asm CODE differences (basis of the per-version sidid signatures)
  primary_source_urls:
    - https://sourceforge.net/p/sid-wizard/code/214/tree/trunk/sources/include/player.asm   (player.asm at SVN r214 = tag 1.4)
    - https://sourceforge.net/p/sid-wizard/code/312/tree/trunk/sources/include/player.asm   (player.asm at SVN r312 = tag 1.5)
    - https://sourceforge.net/p/sid-wizard/code/214/tree/trunk/sources/exporter.asm          (exporter.asm at r214)
    - https://sourceforge.net/p/sid-wizard/code/312/tree/trunk/sources/exporter.asm          (exporter.asm at r312)
    - https://sourceforge.net/p/sid-wizard/code/HEAD/tree/trunk/manuals/ChangeLog.txt        (Hermit's verbatim changelog, V1.0..V1.8)
    - https://sourceforge.net/p/sid-wizard/code/HEAD/log/                                    (SVN commit log; r390 = the SR-AD reorder)
  fetched_via: "direct" — raw player.asm/exporter.asm pulled per-revision via curl (?format=raw) and diffed locally; line numbers below are from these fetched files (CRLF stripped). ChangeLog raw via curl.
  fetch_date: 2026-06-13
  author: Mihaly Horvath ("Hermit"); player.asm $Id keyword shows last-touched r182 (2012-11-25) for the 1.4/1.5-era file; Soci co-authored 64tass/reloc/IRQ.
  content_date: player.asm/exporter.asm as of r214 (2013-02-07, v1.4) and r312 (2014-01-03, v1.5)
  reliability: HIGH for the V1.4 vs V1.5 deltas (diffed from the actual fetched source) and for the V1.8 SR-AD reorder (ChangeLog + SVN r390 message). MEDIUM-LOW for V1.0/V1.2 byte-level specifics: the source at r103/r174 was NOT directly fetchable this session (the pre-1.4 repo layout differs — player.asm not under sources/include/ then, and the SourceForge raw endpoint 404'd), so V1.0/V1.2 deltas below are from the ChangeLog prose, not a byte diff.
-->

# SID-Wizard — per-version player code differences (sidid-signature basis)

Why this doc: the SIDfinity sidid DB carries **distinct signatures for SidWizard_V1.0 / V1.2 /
V1.4 / V1.5** — i.e. the *exported player machine code* changes shape across these releases, so
a single fingerprint doesn't cover them. This doc pins down *what* changes, with source-line
evidence where I could fetch the source. See `archive_version_history.md` for the dated
release table; `research.md` for the current (HEAD) format/player reference.

## The two things that move the fingerprint

1. **The embedded version string.** `player.asm` jump-table header has, verbatim:
   `TrackerID .text " SID-WIZARD ",SWversion," "` (r214 player.asm line 52). Every exported
   `.sid`/`.prg` therefore contains the ASCII `" SID-WIZARD <ver> "`. `SWversion` is a build
   constant substituted per release, so even with identical code the bytes differ per version.
   *(If present and not stripped, this is a ground-truth version stamp — grep the SID body.)*
2. **Code layout + write-order drift.** Each release adds features, reorders SID writes, and
   (in 1.5) refactors the register symbols — shifting both byte positions and the actual
   `$D4xx` write sequence. The concrete shifts I verified:

## The SID write model (shared across all versions) — context for the diffs

SID-Wizard is a **ghost-register (shadow) player**: per-channel state is computed into RAM
shadow bytes, then flushed to `$D400+` once per frame. The **per-frame main flush** writes a
channel's registers in this fixed order (from r214 player.asm lines 246-258, offsets relative
to that channel's `SIDBASE+7*chn`):

```
sta SIDBASE+6,x   ; SR  (Sustain/Release)     <- line 246  (SR written FIRST)
sta SIDBASE+5,x   ; AD  (Attack/Decay)        <- line 248
sta SIDBASE+0,x   ; FREQ lo                   <- line 250
sta SIDBASE+1,x   ; FREQ hi
sta SIDBASE+2,x   ; PW lo
sta SIDBASE+3,x   ; PW hi
sta SIDBASE+4,x   ; WAVE / control            <- line 258
```

So the *steady-state* order is **SR, AD, FREQ, PW, WAVE** in every version (matches the
research.md note). The version-sensitive part is the **hard-restart / note-start (soundstart)
path**, which is a separate code block and historically wrote AD before SR — see V1.8 below.

## V1.0 → V1.2 (ChangeLog "1.0...1.2"; byte-diff not available — see provenance)

Player-code-affecting changes (from Hermit's ChangeLog; these are the deltas that first
differentiate a V1.0 vs V1.2 fingerprint):
- **Ghost-register coverage increased.** "put some more ghost-registers, at least for HR and
  Waveform ... in extra version all registers are ghosted." → more shadow stores in the play
  loop; different write timing. This is the single biggest V1.0→V1.2 player-shape change.
- **Init write changed: "now writing 0 instead of 8 into SID-registers"** (then waveform $08
  afterwards). → the init clear-loop stores `#0` not `#8` (a different init write stream;
  side effect noted: a bigger `$D418` click on subtune switch).
- **ADSR↔gate spacing enforced** ("KEEP ENOUGH DISTANCE ~10 commands BETWEEN ADSR AND GATE-BIT
  WRITING") and **IRQ rasterbars restructured** so the single-speed `play()` is not under the
  sprites (recovered ~400 cycles / +8 rasterlines). → different code placement, different
  cycle profile of the writes.
- **`$1F` filt-external big-FX** added to the `extra` variant (toggles the $D418 external bit).
- **$FF detune-NOP**, **per-track independent subtune-jump** (`SETSEQA`), relocator **`sec` fix**,
  instrument-0 dismissal (so HVSC accepts the export).
> Net: a V1.0 fingerprint vs V1.2 fingerprint differ mainly by ghost-register count, the
> `#0`-vs-`#8` init store, and IRQ/raster code rearrangement.

## V1.2 → V1.4 (ChangeLog "1.4"; player.asm at r214 fetched & inspected)

- **New GT-style pattern effects → new effect-byte→register mappings.** ChangeLog: "some effects
  slightly rearranged (e.g. wf-table pointer), new effects added which are in GT: simple
  cutoff-frequency setting, simple filter-control (switch & reso) setting" with the filter-switch
  encoded for KT values `$80..$8F`. → the big-FX dispatch table and the `$D415/$D416/$D417`
  (cutoff/resonance/filter-control) write paths change. **This is the most fingerprint-relevant
  V1.4 change** (a tune using the new cutoff/filter-control FX simply cannot be a V1.2 player).
- **Exporter: single-speed tunes now export as a *plain* PSID (no CIA starter).** ChangeLog: "for
  single-speed SIDs use normal SID-filetype without CIA starter code." → for single-speed
  tunes the V1.4 export has a different init/play vector arrangement than the always-CIA earlier
  exporters. Multi-speed still CIA.
- **Exporter: tracker/author info relocated into the VARIABLES area** (overwritten by initer,
  "~60 bytes freed"). → the `" SID-WIZARD <ver> "` signature + author bytes sit at a different
  offset relative to code in V1.4 exports than in V1.2.
- Relocation range extended (settings.cfg min/max, default $0200..$FF00); reset filter-shift at
  startup; vibrato-amplitude-after-portamento pitch fix.

## V1.4 → V1.5 (player.asm r214 vs r312 — DIFFED FROM SOURCE)

This is a **structural rewrite**, not an incremental patch. The two files differ by ~4000
changed/added lines (r214 = 2162 lines, r312 = 2419 lines). Verified concrete changes:

- **Register symbols refactored + a `SIDG.` ghost-shadow namespace introduced.** r312 adds
  named defs (lines 25-29):
  ```
  FREQ = SIDBASE+0 ; PLSW = SIDBASE+2 ; WAVE = SIDBASE+4 ; AD = SIDBASE+5 ; SR = SIDBASE+6
  ```
  and HR/flush stores now target `SIDG.AD,x` / `SIDG.SR,x` / `WFGHOST,x` rather than raw
  `SIDBASE+n,x`. Purely a code-readability refactor in intent, but it **re-emits the whole
  player with shifted byte layout** → a V1.5 binary does not pattern-match a V1.4 binary even
  where behaviour is identical. (This alone justifies a separate V1.5 sidid signature.)
- **`$D418` removed from the SID init clear-loop.** r312 line 228:
  `ldy #$17  ;$d418 is left out from init, so pop/clip might be less noticeable`, then the
  `sta SIDBASE,y` clear-loop (line 229) only covers `$00..$17` (not `$18`). In r214 the init
  loop wrote the full range and `$D418` was set explicitly afterwards (r214 lines 158, 268-271).
  → **the init write stream differs**: V1.5+ never writes `$D418` during the register-clear.
- **Second SID register block added (`SID2BASE+0/+2/+4/...`)** for the new **2SID** export (r312
  lines 37-42). → V1.5 player can carry a 2nd `$D4xx` base / stereo write path.
- **SFX entry point added to the jump table** (`SFXsub jmp SFXinit`, gated by `SFX_SUPPORT`):
  "INITIALIZE A SOUND-EFFECT ON CHANNEL 3: X=note/pitch, Y=SFX-instrument number, A=length".
  → a new public player vector + SFX code (changes jump-table size → shifts everything after).
- **`bare` driver variant introduced** (no subtune support) — a new size/feature point alongside
  light/medium/normal/extra (5 variants in V1.5).
- **Auto-generated relocation table** (Soci's 64tass rev361 preprocessor feature) — the player's
  relocation mechanism is entirely different from V1.4's.
- **Alternative tuning tables** (432 Hz Verdi / just-intonation) selectable → the freq table the
  player ships with may differ; SWM header byte $14 (TUNINGTYPE_POS) becomes meaningful.
- **HR ADSR order in V1.5 is still AD-then-SR** (verified, r312 lines 736-741):
  `GET HR-AD → sta SIDG.AD,x` then `GET HR-SR → sta SIDG.SR,x`. (Same as V1.4 — see below.)

## V1.5 → V1.6 → V1.7 (ChangeLog; not byte-diffed this session)

- **V1.6:** "made space for two more instruments with careful memory-arrangement" → instrument
  table base/limits move (layout shift). Exporter PSID-header fix: mono SIDs clear bits 6-7 at
  header `$77`. Bare-player 2SID export freeze fix (`datzptr` byte-order in `exporter.asm endPset`).
- **V1.7:** **full 3SID** (third SID register set; `playadapter.asm` channel-division tables).
  **SWP format + SWP player** (separate relocatable packed-data file; a *distinct exported
  player variant*). **Slowdown FX** (combined pitch+tempo) → new pattern-effect dispatch.

## V1.7 → V1.8 (ChangeLog "1.8" + SVN r390 — the cleanest per-version write-order change)

- **★ AD-SR → SR-AD reorder in the non-ghost hard-restart / soundstart path.** ChangeLog:
  "AD-SR order changed to SR-AD in player.asm when non-ghostregister Hard-Restart and soundstart
  events happen. Probably causes a bit better, more stable sound." SVN r390 (2014-07-22),
  message: *"AD-SR order changed to SR-AD in Hard Restart and soundstart in player.asm"*.

  Verified the *pre*-change order in the fetched source: both V1.4 (r214 lines 493-502) and V1.5
  (r312 lines 736-741) write **AD first then SR** in the HR block:
  ```
  ; V1.4 (r214):  lda (PLAYERZP),y ;GET HR-AD  / sta SIDBASE+5,x   (AD)
  ;               lda (PLAYERZP),y ;GET HR-SR  / sta SIDBASE+6,x   (SR)
  ; V1.5 (r312):  GET HR-AD -> sta SIDG.AD,x   (AD)
  ;               GET HR-SR -> sta SIDG.SR,x   (SR)
  ```
  So **≤V1.7 = AD-then-SR**, **V1.8+ = SR-then-AD** in the *non-ghost* HR/soundstart path. This
  is a real `(reg,val)` write-order difference at note-start and is the **highest-value config
  knob for telling a V1.8 player from earlier ones** in the write-log. (The steady-state main
  flush was already SR-then-AD in all versions; this change makes the HR path agree with it.)
- **`1st-waveform pitch indexed by X instead of Y` bug fixed** (r214/r312 had the typo; fixed in
  1.8) — "not much audible difference btw." but it *is* a different freq write value for the
  first frame, so ≤1.7 vs 1.8 can differ on frame-0 pitch of a note.
- **`SLOWDN3` branch `bpl`→`bcs`** in the SWP slowdown/slide path (slides > ~$F0 were broken).
- **`TUNE_HEADER` no longer pinned to `$20`** → the header/signature layout (incl. `SWversion`
  string position) can shift in 1.8 even relative to 1.7.
- **"DEMO" driver variant added** (6th variant). **Drean** machine-type added to exporter CIA
  timing. **Orderlist Separator NOP** opcodes `$F0..$FD` added to the sequence stream.
- Filter/PW-jump `$0A/$0B` fix: reset `CWEPCNT`/`PWEEPCNT`.

## V1.8 → V1.9+ (no player-logic change expected)

Post-V1.8 development moved to the cross-platform PC editor (`cRSID` engine). The C64
player.asm is essentially frozen. The one export-side change of note is **V1.92's 4SID `.sid`
generation** using the WebSID multi-SID `.sid` proposal — that affects the PSID/WebSID *header*
and multi-chip addressing, not the per-channel music write logic. No SWM-format magic bump.

## SWM module format version history (priority item)

- **The format ID is `"SWM1"`** (mono) at SWM bytes 0-3 (stereo variant `"SWMS"` per research.md).
  Source: `sources/SWM-spec.src` line 34 (`00..03: 'SWM1' identifier`).
- **The 64-byte header is frozen across all versions** — `SWM-spec.src` line 32:
  `tuneheadersize=64 ;//don't modify (to keep compatibillity throughout versions)`.
- **`SWM2` never shipped.** It is referenced only as a *planned future* format in the ChangeLog
  (e.g. "convert zeroes to default $09 value till SWM2 standard"; "0 will mean 0 in SWM2 module
  format"). All HVSC SID-Wizard tunes are **SWM1**. → the extractor only needs SWM1.
- **The format evolved by deprecating header fields in place, not by bumping the magic.**
  `SWM-spec.src` marks four header bytes as **"now it's obsolete, don't use this anymore in
  SWM1!"**:
  | Byte | Field | Status |
  |------|-------|--------|
  | $06 | `SWM_AUTO_POS` (auto-advance amount) | obsolete (was editor state in ≤V1.2) |
  | $07 | `SWM_CBIT_POS` (on/off config bits: track-binding, rasterbar, follow-play, auto-typing) | obsolete |
  | $11 | `COLORTHEMEPOS` (colour-theme number) | obsolete |
  | $12 | `KEYBOARDTYPE_POS` (keyboard-type number) | obsolete |
  These were **live editor-state fields baked into early-version SWM files** and orphaned later.
  **Do not read them** in the extractor — they're stale/garbage in modern files.
- **Two header fields that *gained* meaning over time:**
  - **$13 `DRIVERTYPE_POS`** — player/driver-musicroutine type (light/medium/full/extra/bare/demo).
    The set of valid values grew with the variants: bare added in V1.5, demo added in V1.8.
    `SWM-spec.src` line 53 stresses it's "just an information, no restriction caused" — the SWM
    doesn't *force* a driver, the editor/exporter picks one. (For SIDfinity: this byte tells you
    which driver variant the author intended, but the exported `.sid` is what actually matters.)
  - **$14 `TUNINGTYPE_POS`** — 0 = 440 Hz, 1 = 432 Hz Verdi, 2 = just-intonation (key of C).
    Meaningful from **V1.5** (when alt tunings were added); 0 in older files.
- Stable opcode constants (unchanged across versions, "HARDWIRED ... POSSIBLY UNCHANGEABLE"):
  note max `$5F`, vibrato-FX `$60`, packed-NOPs `$70..$77`, portamento `$78`, sync-on/off
  `$79/$7A`, ring-on/off `$7B/$7C`, gate-on/off `$7D/$7E`; legato small-FX `$3F`. (Full table in
  research.md / SWM-spec.src lines 110-132.) The only sequence-stream *addition* across versions
  is the **orderlist-FX `$F0..$FD` separator-NOP in V1.8**.

## Recommended config knobs for the SIDfinity write-model / verifier

Encode these as per-version `EngineConfig`-style fields (not `if version==X`):
1. `hr_adsr_order`: `AD_SR` for ≤V1.7, `SR_AD` for V1.8+ (non-ghost HR/soundstart path).
2. `init_writes_d418`: `True` for ≤V1.4, `False` for V1.5+ (the `$D418`-omitted init clear-loop).
3. `singlespeed_export`: `CIA` for ≤V1.2-era, `plain_psid` for single-speed from V1.4+.
4. `ghost_register_coverage`: minimal (V1.0) → HR+WF added (V1.2) → "all" in the `extra` variant.
5. `first_waveform_pitch_index_bug`: present ≤V1.7 (indexed by X), fixed V1.8 (indexed by Y) —
   affects the first-frame freq write value.
6. `driver_variant`: bare/light/medium/normal/extra/demo (+ SWP packed-player from V1.7) — from
   SWM header $13, but verify against the exported player's actual code size/features.
