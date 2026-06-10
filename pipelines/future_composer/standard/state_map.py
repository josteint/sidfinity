"""Standard ("vanilla") FC player orig→rebuild state mapping for state_diff.

Per-engine annotation: maps logical state names to the orig's runtime
addresses (base $1800 image — pass --sid to state_map_gen so BOTH the
orig addresses (reloc shift) and the rebuild labels (per-SID layout)
resolve for an arbitrary family member). Addresses from disassembly.s
+ standard/RE_NOTES.md.

NB the orig keeps several per-frame temps PER-VOICE that the composer
holds as scalars (e.g. vib depth $2158,x) — those are same-frame
equivalent and intentionally unmapped to avoid false diffs.
"""

# Per-voice state arrays (3 bytes each, X = 0/1/2).
# NB: stream CURSORS (tabcount $2121, begcount $2124) are intentionally
# absent — the composer re-encodes the sequence/pattern byte streams, so
# byte positions are incomparable with the orig's by design.
PER_VOICE_STATE = {
    'nootcount':  0x2127,   # note-length countdown
    'nootleng':   0x212A,   # note length (raw $8x & $3F)
    'wavesto':    0x212D,   # instrument waveform cache (inst raw[1])
    'noho':       0x2130,   # note index (note + transpose)
    'wavecount':  0x2133,   # current instrument (from $C0+ pattern byte)
    'hinotesto':  0x2136,   # stored note freq hi (glide-mutated)
    'lonotesto':  0x213C,   # stored note freq lo (glide-mutated)
    'sgl_dir':    0x213F,   # $Ex glide flag (0 none / 1 up / 2 down)
    'counter2':   0x2142,   # frames-since-note (the effect clock)
    'pulse_lo':   0x2145,   # pulse acc lo  (composer: the d402 shadow)
    'pulse_hi':   0x2148,   # pulse acc hi  (composer: the d403 shadow)
    'pulsehitemp': 0x214B,  # inst raw[0] cache
    'toneadd':    0x214F,   # transpose (from $80+ seq byte)
    'svib_dir':   0x215B,   # vibrato triangle direction (0 up / $FF down)
    'svib_pos':   0x215E,   # vibrato triangle position
    'flt_sto':    0x2169,   # filter cutoff shadow
    'filtercount': 0x216C,  # inst raw[4] cache
    'pulsetest':  0x216F,   # pulse direction (1 up / 0 down)
    'repeatsto':  0x2176,   # pattern repeat counter
    'stod404':    0x2179,   # ctrl shadow
    'newnote':    0x2180,   # tie flag (set by $Fx)
}

# Shared scalar state (single bytes).
SCALAR_STATE = {
    'sgl_spd_lo':  0x2164,  # glide rate lo (last-$Ex-wins global)
    'sgl_spd_hi':  0x2165,  # glide rate hi
    'sgl_thresh':  0x1AF8,  # glide onset threshold (orig: SMC CMP operand!)
    'filt_ctr':    0x2172,  # $D417 res/routing counter ($B0 seed)
    'filtvoice':   0x2175,  # filter-voice latch
    'speedsto':    0x2173,  # tempo counter
    'speedbyte':   0x211D,  # tempo reload
    'svib_wlo':    0x217C,  # vibrato work freq lo (global temps)
    'svib_whi':    0x217D,  # vibrato work freq hi
    'svib_shi':    0x217E,  # vibrato step hi
    'svib_slo':    0x217F,  # vibrato step lo
}

# orig logical name → composer xa65 label (identical unless noted).
COMPOSER_LABEL_MAP = {
    'pulse_lo': 'd402',
    'pulse_hi': 'd403',
    # everything else shares its name with the composer label
}
