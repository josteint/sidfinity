# Vibrants/JO player — research docs index

**Engine family:** `vibrants_jo` (sidid label **Vibrants/JO**) — the bespoke
6502 SID player of **Poul-Jesper Olsen** (handles JO / Rock / Technic), Danish,
groups Genesis Project → Amok → Vibrants. **130 SIDs in HVSC** (~106 by JO under
`MUSICIANS/J/JO/`, ~23 by **HJE** = Hans Jürgen Ehrentraut who got the player
from JO during their Amok overlap 1990–91, 1 DRAX worktune).

**Distinct from `jch_newplayer`** (Jens-Christian Huus, also Vibrants) and from
`vibrants_laxity` (Laxity's NewPlayer). All three are separate engines; do not
conflate. *(A first research burst spawned agents that drifted onto JCH NewPlayer;
those 4 wrong-engine files were deleted 2026-06-16.)*

Research sweep: **2026-06-16** (research-player skill). State → **OK** (sweep
complete). The remaining gaps are reverse-engineering, not gatherable online.

## Headline finding

**The JO player was never publicly released — no source, no editor, no format
spec, no annotated disassembly exists anywhere.** Independently confirmed across
CSDb, Demozoo, GitHub, Archive.org/Wayback, Codebase64, Lemon64/forums, Usenet,
and scene magazines. JO "never really got around to finishing an editor" — he
composed directly in an assembler listing (same as his later AdLib work). The
`sidid.nfo` entry is a bare stub: `AUTHOR: Poul-Jesper Olsen (JO)`, no NAME, no
REFERENCE. The player was internally versioned to **V22+** (`Stormlord_2_Demo.sid`
embeds `"NEW PLAYER V22.6-7 BY JESPER OLSEN. MUSIC BY HJE/JO."`).

**Consequence for migration:** the format must be reverse-engineered from our own
binaries (migration phase). This sweep's job — collect what already exists — is
done; the binary analysis below is the head-start.

## What we *do* have (the useful artifacts)

| file | content |
|---|---|
| **`usf_and_binary_analysis.md`** | **The most valuable doc.** Full Multi_Move.sid binary layout map ($1800–$2289), engine state-var table ($211D–$2189), instrument-stream byte encoding, freq/wave/pulse/filter table locations, USF analysis of the existing `Multi_Move.usf`, cross-SID header table, and 10 RE leads. |
| `src/sidid_vibrants_jo_signatures.txt` | All 10 sidid OR-patterns, hand-decoded (gate-off routine, indexed data walk, `$D0`/`$60`/`$80`/`$F0`/`$FF` sentinels). The machine-readable format knowledge. |
| `github_binary_survey.md` | Binary header/size survey across the corpus (relocation spread, code-size band). |
| `hvsc_findings.md` | Local corpus analysis + PSID-header variant table + STIL/Musicians excerpts. |
| `csdb_findings.md`, `csdb_wave2_findings.md` | CSDb/Demozoo scener facts; JO's single coder credit (Music Demo #001, 1989); no tool release. |
| `archive_findings.md` | Wayback/Archive sweep; the V22 version string; hard-restart provenance (JO credited as inventor). |
| `forum_findings.md` | Codebase64/Lemon64/Usenet; assembler-only workflow; best RE anchor clusters. |
| `disasm_findings.md` | Confirms no published RE; binary clustering; names cleanest RE-start clusters. |
| `github_findings.md` | GitHub/tool sweep; sidid is the only open-source format knowledge. |
| `hje_deepsid_findings.md` | HJE identity (CSDb 2273, ex-Esonix), the JO→HJE transfer, HJE's commercial game uses. |
| `hvsc_online_research.md` | Online STIL/player-detection cross-checks. |
| `research.md` | Original 5-line stub (pre-existing; kept). |

## Engine shape (inferred — to be confirmed by RE)

- **Fully relocatable**, load $0800–$F000; ~2300 bytes of player code + per-tune
  data in one binary. All tunes **PAL/VBI, 50 Hz** (no CIA). `sidid` keys on
  opcode patterns with wildcarded operands → one engine relocated, not N versions.
- 3-voice `LDX #2 … DEX/BPL` loop; per-voice ZP state ~$40; `LDY abs,x` / `LDA (zp),y`
  indexed data walk; 8-byte instrument records selected via `(byte−$D0)×8`.
- Sentinels: `$80` note boundary, `$60` note/command threshold (`SBC #$60`),
  `$F0` command marker, `$FF` end-of-sequence, `$FE` song-end (→ mode $02).
- **Test-bit hard-restart** (`AD=0,SR=0,$D404,y=$08`) — JO is credited as its
  inventor (JCH learned it from him ~1988).
- Split freq table (separate 96-byte LO/HI blocks, standard PAL tuning).
  `$D418=$1F` written at top of each play call. 3-state song machine
  (00=playing / 01=loop-at-end / 02=silent). Two init JMPs (full-init / song-change)
  for multi-subtune.
- **Best RE anchors:** `Gamlere`/`Gamlest`/`Rob_Lam_Fejl` (shared play $425C),
  `Cool_Intro_Music`/`Creep_Mix`/`My_Best_Tune` cluster (84–97% code match), and
  the 5 SIDs sharing the `A9 1F 8D 18 D4` play head.
- **Outliers to handle separately:** `Grid.sid` (635 B — a different game engine,
  not JO's player; candidate exclusion) and `First_Digi.sid` (6705 B, play=$0000 —
  possible digi / init-only).

## Prior work in-repo

An earlier partial migration exists: `Multi_Move.usf` + `Multi_Move.sidfinity.sid`
(Hubbard-style USF schema). `usf_and_binary_analysis.md` maps it in full — start there.

## Gap analysis (what's left, and where it lives)

- **Fillable only by RE of our binaries** (→ migration phase, NOT this sweep):
  exact wave/pulse/filter table binary layouts + dispatcher indexing; orderlist
  index mapping (USF 0-based vs binary offset); multi-subtune song-change mechanism;
  instrument-stream command-set evolution 1988→1992; relocation-normalized
  fingerprint to count true player revisions; `First_Digi`/`Grid` disposition.
- **Fillable online but low-value / dead:** `vibrants.dk` Wayback (timed out;
  hosted JO's *AdLib* players, unlikely C64 source); HJE is reachable (active 2022)
  and could be asked directly — a last resort, not needed to start RE.
- **Unfillable online:** everything format-level — the player was never released.
  This is the expected state for a hand-assembled private engine.
