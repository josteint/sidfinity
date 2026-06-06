"""Cybernoid II orig→rebuild state address mapping for state_diff.

Per-voice arrays (3 bytes each, X = 0/1/2 for V1/V2/V3) — addresses
from the ACME source `Tel_Jeroen_Cybernoid2.asm` (Deenen 1988)
relocated by ($A600 - $1000) = $9600.
"""

PER_VOICE_STATE = {
    'pulsestolo': 0xA654,   # PW lo state (pulse_prog)
    'pulsesto_hi': 0xA657,  # PW hi state (pulse_prog)
    'pulsecount': 0xA65E,   # pulse_prog tick counter
    'pulsetest':  0xA67E,   # pulse_prog direction flag
    'pulserun_acc': 0xA6A2, # pulse_run accumulator
    'pulserun_hi':  0xA6A5, # pulse_run hi shadow
    'pulserun_flag': 0xA69F, # pulse_run first-frame init flag
    'wavecount':  0xA63F,   # current instrument
    'nootcount':  0xA651,   # setlength countdown
    'tabcount':   0xA63C,   # seq position
    'begcount':   0xA642,   # pattern position
}

SCALAR_STATE = {
    'tempo_counter': 0xA6E7,   # speedsto
    'tempo_reload':  0xAEED,   # speedbyte (from snelheid_addr)
    'testbyte':      0xA6E0,
}

COMPOSER_LABEL_MAP = {
    'pulsestolo':     'pulsestolo',
    'pulsesto_hi':    'pulsehisto',
    'pulsecount':     'counter2',
    'pulsetest':      'pulsetest',
    'pulserun_acc':   'pulserun_acc',
    'pulserun_hi':    'pulserun_hi',
    'pulserun_flag':  'pulserun_flag',
    'wavecount':      'wavecount',
    'nootcount':      'nootcount',
    'tabcount':       'tabcount',
    'begcount':       'begcount',
    'tempo_counter':  'speedsto',
    'tempo_reload':   'speedbyte',
    'testbyte':       'testbyte',
}
