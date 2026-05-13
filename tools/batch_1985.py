"""Build pipelines for all 1985 classic-engine Hubbard SIDs.

For each remaining 1985 SID (Commando + Monty already done):
  1. Clone the Monty pipeline with auto-discovered ft_base + pulse init.
  2. Add lakefile.lean entries for the new pipeline.
  3. Run extract, lake build, run the exe, grade.
  4. Report a per-SID summary line.

Music vs sound-effect detection: the per-SID list of music subtunes is
hardcoded below from HVSC Songlengths (any subtune ≥ 30 sec is music).

Skips any pipeline that already exists.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SIDS_DIR = REPO / 'data/C64Music/MUSICIANS/H/Hubbard_Rob'

# (sid_basename, pipeline_name, music_subtunes_csv) — derived from the
# 1985 classic-engine survey + Songlengths-based ≥30s music detection.
TARGETS = [
    ('5_Title_Tunes.sid',                'five_title_tunes',     '0,1,2,3,4'),
    ('Action_Biker.sid',                 'action_biker',      '0,1'),
    ('Battle_of_Britain.sid',            'battle_of_britain', '0'),
    ('Chimera.sid',                      'chimera',           '0,1'),
    ('Confuzion.sid',                    'confuzion',         '0'),
    ('Crazy_Comets.sid',                 'crazy_comets',      '0,1'),
    ('Devils_Galop.sid',                 'devils_galop',      '0'),
    ('Gremlins.sid',                     'gremlins',          '0,1,2,3,4,5,6'),
    ('Hunter_Patrol.sid',                'hunter_patrol',     '0'),
    ('One_Man_and_his_Droid.sid',        'one_man_and_his_droid', '0'),
    ('Rasputin.sid',                     'rasputin',          '0'),
    ('Sample_Music_from_I_Karate.sid',   'sample_music_i_karate', '0'),
    ('Human_Race.sid',                   'human_race',        '0,1,2,3,4'),
    ('Last_V8.sid',                      'last_v8',           '0'),
    ('Last_V8_C128_version.sid',         'last_v8_c128',      '0'),
    ('Master_of_Magic.sid',              'master_of_magic',   '0'),
    ('Thing_on_a_Spring.sid',            'thing_on_a_spring', '0'),
]


def cap(name: str) -> str:
    return ''.join(p.capitalize() for p in name.split('_'))


def run(cmd: list[str], cwd: Path = REPO, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def add_lakefile_entries(pnames: list[str]) -> None:
    """Append lakefile entries for each new pipeline if not already present."""
    lf = REPO / 'lakefile.lean'
    text = lf.read_text(encoding='utf-8')
    for pname in pnames:
        cap_n = cap(pname)
        marker = f'lean_exe sidgen_{pname} where'
        if marker in text:
            continue
        entry = (
            f"\n\nlean_lib {cap_n} where\n"
            f'  srcDir := "pipelines/{pname}/codegen"\n'
            f"  roots  := #[`{cap_n}.SID, `{cap_n}.Asm6502, `{cap_n}.PSIDFile,\n"
            f"              `{cap_n}.USF, `{cap_n}.Constants, `{cap_n}.SongData,\n"
            f"              `{cap_n}.Codegen, `{cap_n}.Properties]\n\n"
            f"lean_exe sidgen_{pname} where\n"
            f'  srcDir := "pipelines/{pname}/codegen"\n'
            f"  root   := `{cap_n}.Main\n"
        )
        text += entry
    lf.write_text(text, encoding='utf-8')


def grade(orig: Path, rebuild: Path) -> str:
    """Return one-line grade string from writelog_grade.py."""
    proc = run(['python3', 'src/writelog_grade.py', str(orig), str(rebuild)], check=False)
    line = proc.stdout.splitlines()[0] if proc.stdout else proc.stderr.splitlines()[0]
    return line


def main() -> int:
    # Phase 1: clone all + add lakefile entries
    clone_log: list[tuple[str, str]] = []
    pnames_to_register: list[str] = []
    for sid, pname, subtunes in TARGETS:
        pipeline_dir = REPO / 'pipelines' / pname
        if pipeline_dir.exists():
            print(f'[skip] {pname}: pipeline already exists')
        else:
            sid_path = SIDS_DIR / sid
            proc = run(['python3', 'tools/clone_hubbard_pipeline.py',
                        str(sid_path.relative_to(REPO)), pname, subtunes],
                       check=False)
            if proc.returncode != 0:
                print(f'[FAIL clone] {pname}: {proc.stderr.strip()[:200]}')
                clone_log.append((pname, 'clone-failed'))
                continue
            print(f'[clone OK] {pname}')
        pnames_to_register.append(pname)

    add_lakefile_entries(pnames_to_register)
    print(f'\n--- lakefile updated with {len(pnames_to_register)} entries ---\n')

    # Phase 2: extract → build → grade each
    results: list[tuple[str, str]] = []
    for sid, pname, subtunes in TARGETS:
        sid_path = SIDS_DIR / sid
        # extract
        proc = run(['python3', '-m', f'pipelines.{pname}.extract', subtunes], check=False)
        if proc.returncode != 0:
            results.append((pname, f'extract failed: {proc.stderr.strip()[:120]}'))
            continue
        # build
        proc = run(['lake', 'build', f'sidgen_{pname}'], check=False)
        if proc.returncode != 0:
            results.append((pname, f'lake build failed: {proc.stderr.strip()[:120]}'))
            continue
        # run exe
        exe = REPO / f'.lake/build/bin/sidgen_{pname}'
        if not exe.exists():
            results.append((pname, 'exe missing after build'))
            continue
        proc = run([str(exe)], check=False)
        rebuild = REPO / f'{pname}.sid'
        if proc.returncode != 0 or not rebuild.exists():
            results.append((pname, f'exe failed: {proc.stderr.strip()[:120]}'))
            continue
        # grade
        grade_line = grade(sid_path, rebuild)
        results.append((pname, grade_line))
        print(f'  {pname:<28} {grade_line}')

    print('\n=== FINAL ===')
    for pname, line in results:
        print(f'  {pname:<28} {line}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
