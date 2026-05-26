#!/bin/bash
# Source this to set up the sidfinity environment
export SIDFINITY_ROOT=/home/jtr/sidfinity
export PYTHONPATH="$SIDFINITY_ROOT/.pylocal/lib/python3.12/site-packages:$SIDFINITY_ROOT/src:$PYTHONPATH"
export PATH="$SIDFINITY_ROOT/.pylocal/bin:$SIDFINITY_ROOT/tools/xa65/xa:$SIDFINITY_ROOT/local/bin:$PATH"
export LD_LIBRARY_PATH="$SIDFINITY_ROOT/local/lib:$LD_LIBRARY_PATH"
