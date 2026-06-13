# Master Composer — DeepSID / web findings (player name + variant tags)

> **Provenance**
> - **Generated:** 2026-06-13 by the Master Composer research cluster (web leg).
> - **Web sources fetched:**
>   - DeepSID — https://deepsid.chordian.net/ (player/editor identification mechanism)
>   - VGMPF Wiki, *Master Composer* — https://www.vgmpf.com/Wiki/index.php?title=Master_Composer
>   - VGMPF Wiki, *DeepSID* — https://www.vgmpf.com/Wiki/index.php?title=DeepSID
>   - cadaver SIDId — https://github.com/cadaver/sidid (`readme.txt` = signature-format authority)
> - **Local corroboration:** `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg` is DeepSID's *bundled
>   copy* of the cadaver SIDId database — so DeepSID's player-ID for these tunes is produced by the same
>   `Master_Composer` signature analysed in `sidid_signature_analysis.md`.
> - Web search is US-only and surfaced no players.json dump; findings below are what the live pages and
>   the SIDId source actually state.

---

## 1. How DeepSID labels Master Composer tunes

- DeepSID has a **"Players / Editors" tab** showing "information about the editor/player that made the
  song." Player identification is driven by **SIDId** (cadaver's scanner); DeepSID ships the SIDId DB at
  `utility/sidid_100/sidid.cfg`. The player-name string DeepSID reports for these files is therefore the
  SIDId group name **`Master_Composer`** (displayed as **"Master Composer"**).
- DeepSID additionally assigns a **composer "focus" icon `M` = "Master Composer"** — applied to
  *"composers who only used Master Composer."* (Other focus icons: `D`=DefleMask, `L`=Loadstar
  Songsmith, `B`=BASIC.) This is a *composer-level* tag, distinct from the per-file player-ID.
- A canonical Master Composer collection path exists on DeepSID:
  `/DEMOS/UNKNOWN/Master_Composer/…` (e.g. `Happy_Trails.sid`, `Clair_de_Lune.sid`, `Sweet_Dreams.sid`).

**No separate DeepSID variant tags** for `Patrick_Payne` / `Lope_Pulse_Sweep` were found — those names
live only inside the SIDId cfg as sub-signatures (see §3); DeepSID surfaces the umbrella
`Master Composer` name + the `M` focus icon, not the sub-variant names.

---

## 2. VGMPF facts that corroborate the signature analysis

The VGMPF *Master Composer* page independently confirms two things the disassembly already showed:

1. **"Patrick Payne" is a COMPOSER, not an engine.** VGMPF lists six named composers who used Master
   Composer — explicitly including **Patrick Payne** (alongside Charles Callet, Graham Marsh, …). This
   is why the SIDId `(Patrick_Payne)` sub-signature exists: cadaver seeded an extra anchor from Payne's
   files. It is the same player (see `sidid_signature_analysis.md` §2b/§3 — `(Patrick_Payne)` never
   appears without the head signature in HVSC).

2. **"Some users added pulse width modulation externally."** The base player has **no built-in effects**
   (no vibrato/arp/PWM). This is the documentary explanation for the SIDId `(Lope_Pulse_Sweep)`
   sub-signature — an **external PWM/pulse-sweep add-on** bolted onto the stock player by a coder
   ("Lope"), found in ~20 HVSC files (BOGG et al.). It is the only sub-signature that changes the
   emitted SID write stream.

Other VGMPF facts (consistent with `research.md`): author **Paul Kleimeyer**, written **1983**, publisher
**Access Software**, ~1984 release; **relocatable driver**; format = **bars (≤127, ≤16 notes each) →
blocks (≤64, full SID-register config) → pages (≤23, non-sequential block playback)**; default tuning
**450 Hz NTSC / 433.5 Hz PAL**; known **decaying-hum** bug at song end; *"superseded by Sidplayer"* by
1986.

---

## 3. SIDId format authority (cadaver readme) — settles the parentheses + slash questions

From `github.com/cadaver/sidid` `readme.txt`:

- A signature is **hex bytes + `??` wildcards**; **`END`** terminates a signature; **"multiple
  signatures can exist for one player."**
- **A parenthesised name `(Foo)` is a sub-variant / additional signature of the SAME player** — *not* a
  separate engine. ⇒ `(Patrick_Payne)` and `(Lope_Pulse_Sweep)` belong to `Master_Composer`.
- A **`/` in a name is a family/sub-name path**, and is used to file a sub-driver of a different family.
  ⇒ **`TFMX/MasterComposer` is a TFMX-family driver, a *separate* engine** that merely shares the
  "MasterComposer" word (name collision). Confirmed structurally: it uses `LDA ($06),Y` zero-page
  indirect note fetch (TFMX style) vs Access's absolute-indexed tables; its anchor occurs 0× in the
  Access player; HVSC files it as a distinct engine (5 files). Full proof in
  `sidid_signature_analysis.md` §4.

---

## 4. What the web did NOT yield (gaps)

- **No public Master Composer player source / disassembly online** (VGMPF: "Source — Not public";
  `research.md` agrees). The reverse-engineering in `sidid_signature_analysis.md` is from the HVSC
  binaries directly.
- **No players.json mapping dump** retrieved (US-only search; the live page renders it dynamically).
  Immaterial: DeepSID's player-ID = the bundled SIDId DB we already have locally.
- **No version numbering** for the Access player surfaced anywhere (web or binaries) — the project's
  variant axis is the SIDId-level taxonomy (vanilla vs Lope-PWM), not a vendor version string.

## Leads to follow

1. **Player-ID = SIDId, already local.** Don't re-scrape DeepSID for engine labels — its verdict is the
   `Master_Composer` SIDId group in `tmp/dmc_hunt/DeepSID/utility/sidid_100/sidid.cfg`, identical to the
   other two cfg copies. Treat `sidid_signature_analysis.md` as the authority.
2. **Use DeepSID's `M`-focus composer list as a population sanity check.** Composers flagged `M` (only
   used Master Composer) on DeepSID should map 1:1 to HVSC author dirs in the 1,019 — a cheap way to
   spot mis-classified files. (Confirmed names so far: Patrick Payne, Charles Callet, Graham Marsh,
   plus the Ekaitis_Joe / Hawes_Chuck / Fern_Eric / Matt / BOGG dirs seen in the population query.)
3. **Confirm the Lope-PWM coder identity** (CSDb) only if the ~20-file variant is worth a dedicated
   sub-config — the effect itself (16-bit PW sweep) is already disassembled and is the real migration
   work, not the attribution.
4. **No upstream source means binary-only RE for the player.** The three-tier format (pages/blocks/bars)
   is well documented (VGMPF + `research.md` + the disassembled table offsets), so extraction can lean
   on dataflow tracing from the `STA $D4xx` sites rather than any vendor spec.

---

### Sources

- [DeepSID — Chordian](https://deepsid.chordian.net/)
- [VGMPF Wiki — Master Composer](https://www.vgmpf.com/Wiki/index.php?title=Master_Composer)
- [VGMPF Wiki — DeepSID](https://www.vgmpf.com/Wiki/index.php?title=DeepSID)
- [cadaver/sidid (signature-format readme)](https://github.com/cadaver/sidid)
- [Chordian/deepsid (player DB / SIDId bundling)](https://github.com/Chordian/deepsid)
