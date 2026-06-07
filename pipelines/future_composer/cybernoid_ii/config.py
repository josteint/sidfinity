"""Cybernoid II FCConfig — second canary for the FC family.

Addresses derived from the ACME source `Tel_Jeroen_Cybernoid2.asm`
(Deenen 1988, mirrored at github.com/realdmx/c64_6581_sid_players).
The HVSC tune loads at $A600; the source's RELOC was $1000, so all
labels are offset by ($A600 - $1000) = $9600.

Key structural differences from Hawkeye:
  - Flat seq_table (no SMC indirection, no SFX page section)
  - 87 freq-table entries (Hawkeye has 96)
  - 19 instruments (Hawkeye has 16)
  - 33 patterns (Hawkeye has 64)
  - 2 subtunes, all music
  - Init/play/songout three-vector entry: init=$A600 play=$A606
    (PSID metadata reports play=$A603, which is the `jmp songout` slot;
    the +6 form `jmp playirq` is the actual play vector)

Run this module as a script to dump the decoded model:
    python3 -m pipelines.future_composer.cybernoid_ii.config
"""
from pipelines.future_composer.config import FCConfig


# Address verification (from disassembling Cybernoid_II.sid):
#   freq_lo signature found at $AE3F  (lonote)
#   freq_hi signature found at $AE96  (hinote = lonote + 87)
#   snelheid at $AEED (= hinote + 87)
#   seq_table at $AEEF (= snelheid + 2)
#   sequence (pat ptr table) at $AF01 (= seq_table + 12 + 6 runtime slots)
#   pulsetabel at $AFF4
#   instr_records (pulsehi) at $B014 (= pulsetabel + 32)
CYBERNOID_II = FCConfig(
    name='cybernoid_ii',
    sid_path='hvsc84/MUSICIANS/T/Tel_Jeroen/Cybernoid_II.sid',

    freq_lo_addr=0xAE3F,
    freq_hi_addr=0xAE96,
    pattern_ptr_addr=0xAF01,
    instr_records_addr=0xB014,
    per_subtune_speed_addr=0xAEED,

    subtune_layout='flat_seq_table',
    seq_table_addr=0xAEEF,
    emit_data_from_usf=True,

    # Cybernoid II's freq table is 87 entries (NOT a full 8-octave 96)
    # — the table truncates partway through the top octave. The source
    # ends lonote/hinote with `!by $8f,$f8,$2e` (3 bytes) after 7 full
    # rows of 12, giving 87.
    freq_table_entries=87,
    instr_count=19,
    max_patterns=34,   # sequences reference pattern 33 (dup of 29); 33 was
                       # one short and dropped it (only mattered once the
                       # composer emits patterns from USF, not verbatim).

    # Aux-table addresses (found by disassembling the engine's
    # `lda <addr>,X` references):
    #   $AD51: BD 45 AF       lda $AF45,X    ← drumtabel
    #   $AC7A: BD C4 AF       lda $AFC4,X    ← filterbytes
    #   $ADC9: D9 C0 B0       cmp $B0C0,Y    ← startlen
    #   $ADCE: B9 CC B0       lda $B0CC,Y    ← starttabel
    #   $A861: B9 7F AF       lda $AF7F,Y    ← arplo
    #   $A869: B9 87 AF       lda $AF87,Y    ← arphi
    #   $AB9B: B9 F4 AF       lda $AFF4,Y    ← pulsetabel
    #   $A9CD: BE AC B0       ldx $B0AC,Y    ← vibtabwait
    drumtabel_addr=0xAF45,
    filterbytes_addr=0xAFC4,
    startlen_addr=0xB0C0,
    starttabel_addr=0xB0CC,
    arplo_addr=0xAF7F,
    arphi_addr=0xAF87,
    pulsetabel_addr=0xAFF4,
    vibtabwait_addr=0xB0AC,

    # Cyb II's fx_pulse_run (fx3 bit $02) at $ACE4-$AD24 — verified
    # via siddump --pc-trace at frame 8400. Adds $63 to per-voice
    # accumulator each frame; pulsehisto shadow walks with overflow,
    # wrapping at $0F via `EOR #$08` → $07.
    pulse_run_style='cyb2',
    pulserunspeed=0x63,
)


if __name__ == '__main__':
    from pipelines.future_composer.engine_model import extract, print_song
    print_song(extract(CYBERNOID_II))
