"""The Devils Galop EngineConfig — Devils Galop as a config on the
shared Hubbard '85 core (pipelines/hubbard/).

Devils Galop (Rob Hubbard, 1985) is the same engine family as
Commando, with these deltas: instruments at $183B (placed there by
the self-modifying init), freq table at $1694, arpeggio interval 24
semitones, one music subtune, no sound-effect sub-engine.
"""

import os

from pipelines.hubbard.devils_galop.extract.engine_model import extract
from pipelines.hubbard.config import EngineConfig

# config.py -> devils_galop -> pipelines -> repo root  (3 dirnames)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))


def _resetspd(subtune, binary, load):
    """Tick divider — one less than the score's frames-per-tick."""
    return extract(subtune=subtune).score.tempo - 1


DEVILS_GALOP = EngineConfig(
    name='devils_galop',
    sid_path=os.path.join(ROOT, 'hvsc85', 'MUSICIANS', 'H', 'Hubbard_Rob', 'Devils_Galop.sid'),
    instr_base=0x183B,
    instr_count=13,
    freq_table_base=0x1694,
    extract=extract,
    resetspd=_resetspd,
    subtunes=(0,),
    arp_interval=24,
    vib_onset=8,                # vibrato gate CMP #$08 (Commando uses 6)
    has_sfx=False,
    incby2_step=-1,             # init patches INC $1783,X -> DEC
    incby2_every_frame=True,    # the slide runs every frame, not odd-only
    suppress_first_notestart=True,   # the $178B gate drops V3's f0 note
    master_vol_every_note=0x0F,      # $13B7 writes $D418=$0F on every
                                     # note-load (clamp NOP'd at runtime)
)
