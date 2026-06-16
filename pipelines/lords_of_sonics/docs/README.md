# LordsOfSonics/MS player — research docs index

**Engine family:** `lords_of_sonics` (sidid label **LordsOfSonics/MS**) — the C64
music driver written by **Markus Schneider** ("MS"; early aliases Diflex / Synth-Man)
in 1988 as a Soundmonitor replacement for **Jens Blidon**; the two founded the
German group **Lords of Sonics (LOS)** in Cologne, 1988. The driver was shared
across many composers: **123 HVSC SIDs** spanning Blidon (32), Babyface/Kagan Demir
(17), Schneider (13+4), A-Man/Steven Diemer (8), Jesper Spang (7), Ice/Stefan
Toftevall (6), Mc Olly (6), SMC/Sanke Michael Choe (4), and game rips.

> **Naming:** the "MS" in `LordsOfSonics/MS` = **Markus Schneider**, NOT the composer
> SMC (Sanke Michael Choe), who merely bug-fixed the editor docs.

Research sweep: **2026-06-16** (research-player skill; 2 GitHub agents completed in
full, the other clusters wrote their files before a session-token cutoff — all six
clusters are covered). State → **OK** (sweep complete).

## Headline finding — the format IS recoverable (a public editor exists)

The driver was **publicly released as a tool**: **The Parsec Music Editor V5.1**
(1989, Mnemonic Designs — code by Markus Schneider/Diflex + Nic + ADT, docs by SMC,
demo music by Jeroen Tel). **CSDb #10744** has a `.d64` download (also #169438, a
1991 crack). Disassembling the player stub inside that D64 is the authoritative,
highest-ROI path to a complete format spec — we do **not** have to reverse-engineer
production SIDs blind (contrast `vibrants_jo`, whose player was never released).

**Lineage:** LOS/MS driver (1988) → *Parsec Music Editor* (1989) → Schneider joins
**X-Ample Architectures** (Mar 1989), merges his driver with theirs over ~7 weeks →
**Compotech V2.x** (1990; public V2.1 1995, CSDb #122614). **Compotech and X-Ample
are classified as a SEPARATE sidid family (`xample`, already OK)** — that branch has
a structurally different play routine (bit-7 masking, no Y-indexed SID writes). Keep
the families distinct; X-Ample material here is lineage context only.

## What we have

| file | content |
|---|---|
| **`hvsc_findings.md`** | **Richest doc.** Full PSID-header survey of all 123 SIDs: 5 dispatch-table variant clusters (V_PLAY_INIT 87, V_NOP3_INIT_PLAY 9, V_INIT_PLAY 11, …), engine-header byte map (payload+8…), load-address distribution, speed/CIA anomalies, per-composer breakdown, representative header table, STIL/Musicians excerpts, Remix64 interview digest, 10 RE leads. |
| **`src/sidid_signatures.txt`** | Verbatim `sidid.cfg` blocks: the LordsOfSonics/MS 2-line play signature + `(Parsec)` init sub-variant, plus the full X-Ample family blocks (Compotech_V2.x, Sonic/SDS, Thomas_Detert, XTracker 4.1x/4.2x, X-Ample_Digi) for lineage comparison. |
| `github_findings.md` | Hand-decoded play routine + Parsec init routine opcode-by-opcode (freq double-index lookup, Y=voice register stride 7, X=voice loop 2→0, bit-2 gate test, waveform mask). |
| `github_wilfred_deepsid.md`, `github_parsec_versions_and_interview.md` | sidid/player-id/DeepSID detection details; Parsec version history + Schneider interview notes. |
| `disasm_findings.md` | Disassembly/tech-article/German-magazine sweep. Confirms **no published RE exists**, but recovered an **embedded version-history block** (Move.sid: v2.0→2.2→2.3 [Geir Tjelta]→2.4→v4.1 [Lingo.sid]→v5.1 [Parsec]), a V5.1 binary sketch, and the **"Docs 2 Compotech"** documentation-disk lead. |
| `archive_web_research.md` | Wayback/web sweep (616 lines) — Remix64 interview, VGMPF, group/career history. |
| `forum_findings.md` | Forum/wiki/Usenet sweep (German scene). |
| `csdb_group_lords_of_sonics.md`, `csdb_group_x_ample.md`, `csdb_release_parsec_music_editor.md`, `csdb_release_compotech.md`, `csdb_scener_markus_schneider.md`, `csdb_scener_jens_blidon.md` | CSDb pages: group #757, scener Schneider #6003 / Blidon #2205, Parsec #10744, Compotech #122614. |
| `research.md` | Original 5-line stub (pre-existing; kept). |

## Engine shape (from sidid decode + header survey — confirm against the editor)

- **Embedded load address:** PSID `load=0x0000` for all 123 → real load is the first
  2 payload bytes (LE), immediately followed by a JMP dispatch stub.
- **Canonical layout (`V_PLAY_INIT`, 87/123):** `[lo hi] JMP play / JMP init`, so PSID
  play=base+0, init=base+3. Engine header fields begin ~payload+8 (byte+8 looks like a
  song-count/max-index; byte+11 tempo-ish; bytes+12..13 often `FF xx` = default note
  length/counter — **load-bearing, decode from the editor**).
- **Play routine:** per-voice loop with **X = voice index (2→0)** and **Y = SID
  register offset (0/7/14)**; freq via **double-indexed table lookup** (`ADC (zp),Y;
  ASL; TAY; LDA (zp),Y`) writing `$D400/$D401` (freq lo/hi) and `$D404` (ctrl, masked)
  all **Y-indexed**; bit-2 test (`AND #$04; CMP #$04`) gates the freq update.
- **`(Parsec)` init sub-variant:** three table-clear loops (`STA addr,X; DEX; BPL`),
  then full SID reset (`LDX #$18; LDA #$00; STA $D400,X; DEX; BPL`), set `$D418` master
  vol, init the 3-voice counter. A version/era discriminator, not a separate engine.
- All PAL/VBlank 50 Hz except a couple Schneider multi-subtune tunes with possible CIA
  (`Magic_Events`, `Timezone` — speed fields may also just be corrupted rip text).

## RE anchors & outliers for the migration

- **Cleanest first targets:** simple 1-subtune Blidon 1989 tunes in `V_PLAY_INIT`
  layout (e.g. `Its_Magic_end`, load/play $3000, init $3003); and the 5 game rips
  (`Arcade_Pilot`, `Peter_Pilot`, `Mean_Car`, `Shoot_Out`, `Xytris`).
- **Separate sub-engine / outliers:** `No_Mercy` (13 subtunes, play=$0000 — built-in
  IRQ), `Timezone` (13 subtunes, non-standard init/play offsets), `Blax` (14 subtunes),
  `SMC/Phaedra` (Parsec variant, play<init). The A-Man `V_NOP3_INIT_PLAY` cluster (9
  SIDs) may be an older engine revision.
- **Watch the family boundary:** verify Schneider's 1990+ tunes classify as
  `LordsOfSonics/MS` vs `xample`/`Geir_Tjelta/Comptech-X` (4 Schneider SIDs hit the
  latter) — Compotech-era output may land in a different family.

## Gap analysis

- **Fillable from released materials (→ migration phase, NOT this sweep):** the entire
  byte-level format. Ground-truth source to acquire: the **Parsec Music Editor V5.1 D64**
  (CSDb #10744) — disassemble its player + read its in-editor data layout. This makes a
  clean spec achievable without blind RE. (Version lineage v2.0→…→v5.1 is in
  `disasm_findings.md` — expect minor per-version format drift.)
  - **"Docs 2 Compotech" (CSDb #253740) — DOWNLOADED + CHECKED, dead end for a spec.**
    Both disk images are in `src/` (see `src/compotech_disks_NOTES.md`). The "docs" PRG
    is a scene greetings/credits scroller, NOT a format manual. The companion disk holds
    the actual **Compotech** editor/player — but Compotech is the separate **`xample`**
    family, not LordsOfSonics/MS, so it's relevant to a future *xample* migration, not
    this one.
- **Fillable from our binaries:** confirm the 5 dispatch-variant clusters and the
  payload+8 header field meanings against a `V_PLAY_INIT` disassembly.
- **Probably unfillable / low-value online:** no open-source parser/decompiler exists
  (checked SIDFactory II, libsidplayfp, CheeseCutter, realdmx, SIDdecompiler, DeepSID);
  no published annotated disassembly. The editor D64 supersedes the need for one.
