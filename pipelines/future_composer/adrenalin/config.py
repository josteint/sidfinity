"""Adrenalin (HeatWave) FCConfig — third FC family canary.

Status: DRAFT. Addresses identified via disassembly + post-init py65
memory inspection (see RE_NOTES.md "Addresses found"). Several knobs
default to Cybernoid II values pending verification.

Run this module to dump the decoded model (will likely error until
all addresses + knob choices are validated):
    python3 -m pipelines.future_composer.adrenalin.config
"""
from pipelines.future_composer.config import FCConfig, EngineInstance


# Address verification (from py65 init + disassembly grep):
#   $17E3 lonote   — freq_lo[0..95], $17E3+$48=$0C matches Hawkeye idx $48
#   $1842 hinote   — freq_hi[0..95], $1842+$48=$47 matches Hawkeye idx $48
#   $18A1 per_subtune_speed — 4 bytes: $02 $02 $01 $01 (4 subtunes)
#   $18A5/$18A7    — per-subtune sequence-base pointer table (X-indexed
#                    lo at $18A5+X, hi at $18A7+X; the engine SMCs the
#                    LDA at $7ACA with these to load the 6-byte per-voice
#                    seq pointers from <subtune_base>+0..5 → $18B5)
#   $19AC instr_records — 8-byte records, identified via $7CCA-$7DE9
#                  (matches Hawkeye byte layout: +0 pulse_hi, +1 ctrl,
#                  +2 AD, +3 SR, +4 fil_count, +5 fx1, +6 fx2, +7 fx3)
#   $1BA0 pattern_ptr_table — 2 bytes/entry lo,hi (e.g.
#                  $1BA0..$1BAF = pat 0..7 ptrs ${001C, 061C, ...} which
#                  matches the SMC pattern at $7BB1: LDA $1BA0,Y / $1BA1,Y)
#
# UNKNOWNS (TODOs — find via further disasm):
#   - subtune_layout: probably 'flat_seqtabel' (no SFX evident in
#     PSID's 4 music subtunes) but the X-indexed ptr table at
#     $18A5/$18A7 is a NEW shape — Cyb II's flat_seqtabel is a
#     contiguous 6-byte block per subtune, Hawkeye's
#     smc_template_with_sfx uses a different SMC template scheme.
#     May need a new SubtuneLayout variant.
#   - instr_count: count from instrument records data
#   - max_patterns: count from $1BA0..$1BFF range
#   - drumtabel_addr, filterbytes_addr, arplo/hi, pulsetabel,
#     vibtabwait, startlen, starttabel: not yet located
#   - voice_loop_layout: probably 'tight_nextvoice' but verify by
#     examining the per-voice loop tail
#   - noise_tick_style: 'cyb2_table' default; may need new style
#   - All other Hawkeye-vs-Cyb II discriminator knobs


ADRENALIN = FCConfig(
    name='adrenalin',
    sid_path='hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid',

    # ---- verified addresses ----
    freq_lo_addr=0x17E3,
    freq_hi_addr=0x1842,
    pattern_ptr_addr=0x1BA0,
    instr_records_addr=0x19AC,
    per_subtune_speed_addr=0x18A1,

    # ---- TODO: verify subtune layout shape ----
    # Adrenalin uses X-indexed lo + hi pointer tables at $18A5/$18A7
    # plus a 6-byte runtime slot at $18B5. This is a new shape vs Cyb II
    # and Hawkeye. Provisionally pick 'flat_seqtabel' — if the
    # extractor doesn't decode the seq stream cleanly, this needs a new
    # SubtuneLayout variant added to config.py.
    subtune_layout='flat_seqtabel',
    seqtabel_addr=0x18A5,           # PROVISIONAL

    # ---- table sizes (TODO: verify from instr_records + pattern_ptr extent) ----
    freq_table_entries=96,           # confirmed via Hawkeye signature match
    instr_count=16,                  # PROVISIONAL — count from $19AC area
    max_patterns=64,                 # PROVISIONAL

    # ---- aux tables (TODO: locate via further disasm) ----
    # drumtabel_addr=0,
    # filterbytes_addr=0,
    # arplo_addr=0, arphi_addr=0,
    # pulsetabel_addr=0,
    # vibtabwait_addr=0,
    # startlen_addr=0, starttabel_addr=0,
    # wavearp_addr=0, pulsearp_addr=0,

    # ---- Cyb II-style defaults until proven otherwise ----
    # noise_tick_style='cyb2_table',
    # voice_loop_layout='tight_nextvoice',
    # nextvoice_write_order=(4, 0, 1, 2, 3),

    # ---- Multi-engine instances (from init copy table $514E-$5175) ----
    # Sub 0 uses engine A at $7A00 (the one we disassembled). Subs 2/3
    # use engine B at $1000 (same FC code, relocated; same +$FC and
    # +$102 relative-offset structure). Sub 1 uses entry C at $1021
    # (no JMP prefix — likely a shim into engine B). The top-level
    # address fields above reflect engine A (sub 0); the EngineInstance
    # overrides for subs 1/2/3 carry their distinct addresses.
    engines=(
        EngineInstance(
            name='engine_a_7A00',
            subtune_indices=(0,),
            copy_src_addr=0x5176,
            copy_dst_addr=0x17F3,
            copy_size=0x06E7,
            play_vector=0x7A06,
            # Top-level field defaults apply (engine A IS the top-level).
        ),
        EngineInstance(
            name='engine_b_1000_sub1',
            subtune_indices=(1,),
            copy_src_addr=0x575D,
            copy_dst_addr=0x1021,
            copy_size=0x0A73,
            play_vector=0x1021,
            # TODO: per-engine runtime address overrides — engine B has
            # its own freq_lo/hi, instr_records, etc. at offsets within
            # the $1000-$1FFF block. Find via disasm.
        ),
        EngineInstance(
            name='engine_b_1000_sub2',
            subtune_indices=(2,),
            copy_src_addr=0x60D0,
            copy_dst_addr=0x1000,
            copy_size=0x0DDD,
            play_vector=0x1006,
            # TODO: per-engine runtime address overrides
        ),
        EngineInstance(
            name='engine_b_1000_sub3',
            subtune_indices=(3,),
            copy_src_addr=0x6DAD,
            copy_dst_addr=0x1000,
            copy_size=0x0D51,
            play_vector=0x1006,
            # TODO: per-engine runtime address overrides
        ),
    ),
)


if __name__ == '__main__':
    from pipelines.future_composer.engine_model import extract, print_song
    print_song(extract(ADRENALIN))
