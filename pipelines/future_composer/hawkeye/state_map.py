"""Hawkeye orig→rebuild state address mapping for state_diff.

Per-engine annotation: maps logical state names to HVSC's runtime
addresses. The composer label of the same name resolves to the
rebuild's address (xa65 -l dump). state_map_gen.py joins these two
to produce a state_diff map file.

Addresses derived from disassembly.s header + investigative sessions.
"""

# Per-voice state arrays (3 bytes each, X = 0/1/2 for V1/V2/V3).
# Format: {label: orig_base_addr}
PER_VOICE_STATE = {
    'tabcount':  0x90C5,   # seq position (disasm header)
    'begcount':  0x90C8,   # pattern position within current pattern
    'nootcount': 0x90CB,   # setlength countdown
    'wavecount': 0x90DA,   # current instrument (from $C0+ pattern byte)
    'repeatsto': 0x9118,   # pattern repeat counter (disasm header)
    'newnote':   0x9127,   # noglide marker flag (set by $F0 byte)
    'toneadd':   0x90F9,   # transpose (from $80+ seq byte)
    'voiceinc':  0x9139,   # voice inc (from $60+ seq byte)
}

# Shared scalar state (NOT per-voice — single byte).
SCALAR_STATE = {
    'tempo_counter': 0x9116,   # global tempo counter (= speedsto in composer)
    'tempo_reload':  0x7AFE,   # tempo reload value (= speedbyte)
    'testbyte':      0x7B99,   # halt flag (set by songout)
}

# Map orig addresses → composer label names (for state_map_gen).
# Composer's xa65 labels resolve to rebuild's runtime addresses.
COMPOSER_LABEL_MAP = {
    # Per-voice arrays — the orig address is the base; composer also
    # has a 3-byte array under the same name.
    'tabcount':       'tabcount',
    'begcount':       'begcount',
    'nootcount':      'nootcount',
    'wavecount':      'wavecount',
    'repeatsto':      'repeatsto',
    'newnote':        'newnote',
    'toneadd':        'toneadd',
    'voiceinc':       'voiceinc',
    # Scalars
    'tempo_counter':  'speedsto',
    'tempo_reload':   'speedbyte',
    'testbyte':       'testbyte',
}
