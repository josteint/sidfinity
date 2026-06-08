"""Adrenalin (HeatWave) FCConfig — third FC family canary.

All address knobs derived from hand-annotated disassembly of engine A
at `$7A00-$81D0` (see `disassembly.s` + `RE_NOTES.md` "Engine A —
hand-annotation" section). Engine variant: canonical FC family,
+0/+3/+6 vector layout, structurally identical to Hawkeye and Cyb II
just at different addresses.

Verified subtune-to-engine mapping (via `_run_init_in_py65`):
  sub 0: engine A at `$7A00` directly
  sub 1: outlier — engine at `$1021`, data layout TBD
  sub 2: engine A relocated to `$1000` (state at `$10xx`, data still
         at `$17E3` etc. — verified by disasm of relocated nolengset
         at `$128B`)
  sub 3: same as sub 2

Subs 0, 2, 3 all read from the SAME data tables at engine A's
addresses; only the data VALUES differ per subtune (each subtune's
init copies its own patterns/per_subtune_speed/sequence pointers
into the runtime slot). Per the CORE TENET, our rebuild emits ONE
canonical FC engine handling 3 subtunes via standard FC subtune
dispatch — Adrenalin's binary uses 2 engine copies for memory
packing, irrelevant to our rebuild.

Sub 1 is deferred — handled as a separate task once subs 0/2/3
verify byte-exact.

Run this module to dump the decoded model:
    python3 -m pipelines.future_composer.adrenalin.config
"""
from pipelines.future_composer.config import FCConfig, EngineInstance


ADRENALIN = FCConfig(
    name='adrenalin',
    sid_path='hvsc84/MUSICIANS/H/HeatWave/Adrenalin.sid',

    # ---- rebuild layout (CORE TENET: own layout, match the writelog) ----
    # The original is a self-decompressing inline-load PSID; the rebuild is a
    # plain FC engine emitted from USF. Data tables stay at engine A's runtime
    # addresses ($17E3-$1Bxx); the engine code (~2KB) sits BELOW them at
    # load_addr, with USF-derived music_data (patterns/sequences/seq_table)
    # placed after the data sections (~$1Exx). Engine $0E00..~$15F5, data
    # $17E3+ — the composer emits sections in ascending address order, so the
    # engine must precede the data tables.
    emit_data_from_usf=True,
    load_addr=0x0E00,
    init_style='fc_clear_sweep',     # engine A $7AE2 descending $01/$00 clear
    contiguous_data_layout=True,     # orig packs tables tightly → emit packed

    # ---- mandatory data table addresses (verified by disasm reads) ----
    freq_lo_addr=0x17E3,            # lonote, LDA $17E3,Y at $7C9B
    freq_hi_addr=0x1842,            # hinote, LDA $1842,Y at $7CA5
    per_subtune_speed_addr=0x18A1,  # LDA $18A1,X at $7AD3 (4 bytes for 4 subs)
    instr_records_addr=0x19AC,      # LDA $19AC,X..$19B3,X at $7CCA-$7DE9
    pattern_ptr_addr=0x1BA0,        # LDA $1BA0,Y / $1BA1,Y at $7BB1/$7BB6

    # ---- subtune layout: runtime_slot variant ----
    # Songinit ($7AB4) SMC-copies 6 bytes from per-subtune source
    # ($18A5+X:$18A7+X)+0..5 to $18B5..$18BA. We extract from $18B5
    # directly after running init per subtune in py65.
    subtune_layout='runtime_slot',
    runtime_seq_ptrs_addr=0x18B5,   # 6-byte slot (3 lo + 3 hi)
    runtime_speed_addr=0x7A09,      # active speed byte (loaded by songinit)

    # ---- table sizes ----
    freq_table_entries=96,          # canonical FC 96-entry table
    instr_count=16,                 # 16 × 8-byte records at $19AC
    max_patterns=64,                # provisional; revisit if extract complains

    # ---- aux table addresses (all confirmed via disasm reads) ----
    drumtabel_addr=0x18DD,          # LDA $18DD,X / $18DE,X at $8112/$811B
    filterbytes_addr=0x198B,        # LDA $198B,X / $198C,X at $807D/$8083
    arplo_addr=0x1961,              # LDA $1961,X at $7C46
    arphi_addr=0x1968,              # LDA $1968,X at $7C4F
    arp_ptr_hi_min=0x10,            # arp programs live at $19xx (hi $19), not
                                    # high memory — don't filter them as garbage
    fx3_bit2_autoarp_index=1,       # fx3 bit 2 → auto-arp using program 1
                                    # ($1973 = (0,+4,+7)); engine A $7DA7
    pulsetabel_addr=0x199C,         # LDA $199C,Y at $7FAF
    vibtabwait_addr=0x1A14,         # LDX $1A14,Y at $7DD6

    # ---- engine knobs (from disasm) ----
    noise_tick_style='hawkeye_constants',  # $8175+: LDA #$58, LDA #$81
    voice_loop_layout='tight_nextvoice',   # nextvoice at $81B3 all-in-one
    nextvoice_write_order=(2, 3, 4, 0, 1),  # PWlo PWhi ctrl freqlo freqhi
                                            # (engine A inst-load $7CEB/$7CF7
                                            # write PW before ctrl/freq)
    fx_drum_d401_offset=0x0D,              # $8168: ADC #$0D
    held_note_clears_stod404_gate=True,    # $7D5B: AND #$FE / STA stod404
    filter_prog_mask=0x03,                 # $8079: AND #$03 (4 progs)
    pulse_run_style='disabled',            # no fx3 bit $02 path in engine A

    # ---- multi-engine: which subtune uses which engine instance ----
    # Setting `engines` triggers the init-per-subtune extract path
    # (each subtune's post-init memory has its own data). All 4 subs
    # listed; no per-subtune ADDRESS overrides needed for subs 0/2/3
    # (they all read engine A's standard data tables — verified by
    # disasm of relocated nolengset at $128B).
    #
    # Sub 1 IS the outlier (different engine at $1021); extract will
    # produce garbage data for it. Accepting that until sub 1's own
    # disasm work lands.
    engines=(
        EngineInstance(
            name='engine_a_at_7A00',
            subtune_indices=(0,),
            copy_src_addr=0x5176, copy_dst_addr=0x17F3, copy_size=0x06E7,
            play_vector=0x7A06,
        ),
        EngineInstance(
            name='engine_at_1021_sub1_DEFERRED',
            subtune_indices=(1,),
            copy_src_addr=0x575D, copy_dst_addr=0x1021, copy_size=0x0A73,
            play_vector=0x1021,
            # Sub 1 deferred — extract output for this sub will be
            # garbage until its data layout is identified.
        ),
        EngineInstance(
            name='engine_a_relocated_to_1000_sub2',
            subtune_indices=(2,),
            copy_src_addr=0x60D0, copy_dst_addr=0x1000, copy_size=0x0DDD,
            play_vector=0x1006,
        ),
        EngineInstance(
            name='engine_a_relocated_to_1000_sub3',
            subtune_indices=(3,),
            copy_src_addr=0x6DAD, copy_dst_addr=0x1000, copy_size=0x0D51,
            play_vector=0x1006,
        ),
    ),
)


if __name__ == '__main__':
    from pipelines.future_composer.engine_model import extract, print_song
    print_song(extract(ADRENALIN))
