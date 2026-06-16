# Provenance log — MoN/Deenen research sweep (2026-06-15)

Every URL attempted during the sweep, with status. Future waves: skip the
already-fetched, retry the failed-but-promising.

## Fetched OK (content saved)

| URL | Yielded |
|-----|---------|
| https://github.com/realdmx/c64_6581_sid_players | **Primary source** — RE'd player .asm for all 4 variant authors → `src/*.asm` |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.cfg | **Full MoN sidid signatures** → `src/sidid_cfg_cadaver.txt` |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo | Author/reference NFO notes (merged into cadaver txt) |
| https://vgmpf.com/Wiki/index.php/Maniacs_of_Noise | Driver = "Musicfile", Turbo Ass; .mon/.jt format names |
| https://vgmpf.com/Wiki/index.php/Charles_Deenen | Games list; used Tel's driver version |
| https://en.wikipedia.org/wiki/Charles_Deenen | 1987 MoN founding; bio |
| https://www.c64-wiki.com/wiki/Maniacs_of_Noise | History (no format) |
| https://csdb.dk/group/?id=448 | MON SFX Editor/Relocator/Crash Saver tool IDs |
| https://csdb.dk/release/?id=10759 | MON SFX Editor V1.00 (1990); Monase_1.0.zip / Music Mania.zip |
| https://csdb.dk/release/?id=10760 | MON SFX Relocator V1.0 |
| https://csdb.dk/release/?id=10761 | MON SFX Crash Saver V1.0 |
| https://csdb.dk/scener/?id=1040 | Deenen releases (incl. Future Composer V3.1 contribution) |
| https://hugi.scene.org/.../jeroen%20tel.htm | Tel interview (learned on Hubbard's routine) |
| https://archive.org/details/Cybernoid_Music_1988_Maniacs_Of_Noise | .d64 (binary only, no source) |
| https://archive.org/details/Maniacs_of_Noise_Music_1_19xx_FCC | .d64 (no source) |

## Attempted — FAILED or no content

| URL | Status |
|-----|--------|
| https://charlesdeenen.com / https://www.jeroentel.com | ECONNREFUSED (domains down) |
| https://codebase64.org/doku.php?id=base:maniacs_of_noise | Empty / page absent |
| https://www.c64-wiki.com/wiki/Charles_Deenen | 404 |
| https://www.exotica.org.uk/wiki/Jeroen_Tel_(format) , /Maniacs_of_Noise | Browser verification wall |
| https://www.c64.com/gt_display_interview.php?interview=8 | SSL cert error |
| https://web.archive.org/... (charlesdeenen / jeroentel) | Blocked in this environment |
| https://raw.githubusercontent.com/WilfredC64/player-id/.../config/sidid.cfg | 404 raw (web view truncated; content == cadaver) |
| https://raw.githubusercontent.com/libsidplayfp/.../sidid.cfg | 404 (dropped from libsidplayfp?) |
| https://raw.githubusercontent.com/hvsc-org/HVSC-SIDID/main/sidid.cfg | 404 (repo path wrong/private) |
| https://raw.githubusercontent.com/Chordian/deepsid/master/php/sidid.cfg | 404 (path/branch differs) |
| https://www.hvsc.c64.org/.../DOCUMENTS/SID_PLAYERS.txt | 404 |
| http://justsolve.archiveteam.org/wiki/Maniacs_of_Noise | ECONNREFUSED (site down) |
| https://csdb.dk/release/?id=10604 (FCS editor for MoN/FC player) | 503 — retry |
| https://www.file-extensions.org/mon-file-extension-... | 403 |

## Wave 2 — 2026-06-16 (follow-up, non-recursive Explore-style agents)

| URL | Status / yield |
|-----|----------------|
| https://api.github.com/repos/realdmx/c64_6581_sid_players (tree) | OK — full inventory; confirmed we have all MoN files |
| https://raw.githubusercontent.com/realdmx/c64_6581_sid_players/HEAD/Bjerregaard_Johannes_MON/Bjerregaard_J_James_Bond_3.asm | OK → `src/Bjerregaard_J_James_Bond_3.asm` (full Bjerregaard RE, instrument/sequence decode) |
| realdmx repo root README | OK → `src/realdmx_README.md` |
| https://github.com/realdmx (profile/gists) | OK — no separate MoN RE notes |
| https://csdb.dk/release/?id=10604 | OK — actually Future Composer V1.0, not MoN docs |
| https://csdb.dk/release/?id=10759/10760/10761 | OK — Monase/Music-Mania zip contents pinned (see followup_csdb_findings.md) |
| https://csdb.dk/scener/?id=8051 / ?id=1040 | OK — no player source |
| https://raw.githubusercontent.com/cadaver/sidid/master/sidid.nfo (full) | OK — sub-ID names decoded (Cyb2/TTWII/JTS/RWE/Bantam) |
| DeepSID tune-info (Cybernoid_II / Rubicon / Mantalos) | OK — reports parent tags only; sub-IDs never surface |
| http://justsolve.archiveteam.org/wiki/Maniacs_of_Noise | ECONNREFUSED (still down) |
| https://www.exotica.org.uk/wiki/Maniacs_of_Noise , Jeroen_Tel_(format) | Cloudflare bot-check (blocked) |
| ZX Spectrum 128K port source | Not found (no public source) |

## Still unfetched (not needed for OK; nice-to-have)

- Actual binary download of `Monase_1.0.zip` (contents already identified)
- Modland Reyn Ouwehand module dir
