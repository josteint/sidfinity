#!/bin/bash
# Source this to set up the sidfinity environment
export SIDFINITY_ROOT=/home/jtr/sidfinity
export PYTHONPATH="$SIDFINITY_ROOT/.pylocal/lib/python3.12/site-packages:$SIDFINITY_ROOT/src:$PYTHONPATH"
export PATH="$SIDFINITY_ROOT/.pylocal/bin:$SIDFINITY_ROOT/tools/xa65/xa:$SIDFINITY_ROOT/local/bin:$PATH"
export LD_LIBRARY_PATH="$SIDFINITY_ROOT/local/lib:$LD_LIBRARY_PATH"

# C64 ROM self-heal. siddump needs kernal/basic/chargen in
# ~/.local/share/sidplayfp to execute RSID + C64-BASIC tunes; without them the
# BASIC interpreter never runs, every Basic_Program member reports
# `unsupported:too_few_steps`, and regression reports "22 regressed" for
# reasons that have nothing to do with the code.
#
# ~/.local/share is NOT stable on this host — it was wiped twice on
# 2026-07-21 (19:41 and 21:31), each time taking the ROMs with it. So restore
# from the in-repo copy whenever it has gone missing. Cheap: one stat when the
# ROMs are present, which is the normal case.
if [ ! -f "$HOME/.local/share/sidplayfp/kernal" ] \
   && [ -f "$SIDFINITY_ROOT/tools/c64roms/kernal" ]; then
    mkdir -p "$HOME/.local/share/sidplayfp"
    cp "$SIDFINITY_ROOT/tools/c64roms/kernal" \
       "$SIDFINITY_ROOT/tools/c64roms/basic" \
       "$SIDFINITY_ROOT/tools/c64roms/chargen" \
       "$HOME/.local/share/sidplayfp/" 2>/dev/null \
      && echo "env.sh: restored C64 ROMs to ~/.local/share/sidplayfp" >&2
fi
