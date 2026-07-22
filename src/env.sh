#!/bin/bash
# Source this to set up the sidfinity environment
export SIDFINITY_ROOT=/home/jtr/sidfinity
export PYTHONPATH="$SIDFINITY_ROOT/.pylocal/lib/python3.12/site-packages:$SIDFINITY_ROOT/src:$PYTHONPATH"
# `tools` is on PATH so `siddump` resolves by name — CLAUDE.md has always said
# sourcing this puts it there, but until 2026-07-23 only xa65 was added and
# every ad-hoc `siddump ...` died with "No such file or directory".
export PATH="$SIDFINITY_ROOT/.pylocal/bin:$SIDFINITY_ROOT/tools:$SIDFINITY_ROOT/tools/xa65/xa:$SIDFINITY_ROOT/local/bin:$PATH"
export LD_LIBRARY_PATH="$SIDFINITY_ROOT/local/lib:$LD_LIBRARY_PATH"

# C64 ROMs, read straight from the repo. siddump needs kernal/basic/chargen
# to execute RSID + C64-BASIC tunes; without them the BASIC interpreter never
# runs, every Basic_Program member reports `unsupported:too_few_steps`, and
# regression prints "22 regressed" for reasons unrelated to the code.
#
# It used to look only in ~/.local/share/sidplayfp, which is not stable on
# every host (wiped twice on 2026-07-21, each time taking the ROMs with it).
# siddump now prefers $SIDFINITY_ROMS_DIR, so the repo carries its own copy
# and nothing outside the tree is load-bearing. The ROMs themselves stay
# gitignored — copyrighted Commodore binaries.
export SIDFINITY_ROMS_DIR="$SIDFINITY_ROOT/tools/c64roms"
