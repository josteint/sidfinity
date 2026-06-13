# Provenance log — Music Assembler research sweep (2026-06-13)

Every URL/source attempted during the six-cluster research-player sweep, so a
future wave doesn't re-fetch. Per-file provenance headers carry the exact URL
for each saved doc; this is the roll-up.

## Fetched successfully

| Source | Via | Yielded |
|---|---|---|
| CSDb release #94388 (`csdb.dk/release/?id=94388`) | curl (Firefox UA, `--compressed`; plain WebFetch 503'd) | metadata, download links, comments, dating, name-collision caveat |
| Manual PDF `csdb.dk/getinternalfile.php/137191/masm_manual_0_01b.pdf` | curl | vendored `csdb_manual_0_01b.pdf` + `pdftotext` → `.txt` |
| Archive.org `d64_Music_Assembler_1990_Markt_Technik` | direct + Python D64 walker (no VICE) | editor disk → `masm_editor_1990_OMUSICASSEMBLER.prg` |
| `github.com/ice00/jc64` (JC64dis, GPL-2) | clone/raw | hand-annotated `MusicAssembler.dis` → `jc64dis_*` + `spec_player_jc64dis.md` |
| `github.com/cadaver/sidid`, `github.com/WilfredC64/player-id` | raw | sidid signatures + variant family |
| HVSC binaries (`OPM/Sid_Slam`, `Ozone/Power_Wars`, `Kalle_Kloakk_part_8`, etc.) | local disasm + `siddump --writelog` | the two grounded RE traces + write model |
| Local `tmp/dmc_hunt/` sidid configs + DeepSID checkout | local read (read-only) | signature population counts across all 6351 tunes |
| DeepSID (`deepsid.chordian.net`) | direct | player-name string, STIL, re-tag notes |

## Attempted but blocked / empty

| Source | Status | Note |
|---|---|---|
| `forum64.de` (German) | 403 to WebFetch | needs a browser; likely home of any German player analysis |
| Lemon64 threads (relocation; VoiceTracker `t=2029`, JITT64-dev `t=26109`) | 503 to WebFetch | retry via `curl web.archive.org/.../id_/<url>` |
| Codebase64 wiki/forum | no MASM article | negative result |
| comp.sys.cbm (Google Groups) | no format discussion | negative result |
| Pouet.net | no technical MASM content | negative result |
| JITT64 SourceForge SVN (`svn.code.sf.net/p/jitt64/code/trunk/`) | no `svn`/network in sandbox | top lead; needs networked host |
| GitHub authenticated code search (`"Music Assembler"`, `Swagerman`) | blocked unauthenticated | worth a pass with credentials |

## Unfetched leads (see README "Top leads" + `forum_leads.md`)

CSDb #27470/#27471/#27472 (Triad V1.1/1.3/1.4), #10756 (VoiceTracker V1.0);
archive.org `d64_Voicetracker_v5_1990_Pawel_Soltysinski`; zimmers.net
VoiceTracker/MusicMixer PRGs; `paula8364.com` (claimed MASM engine versions,
unverified); Marco Swagerman direct (amiga.cafe `MC-DusaT`, YouTube).
