"""Hawkeye FCConfig — addresses verified by RE_NOTES.md + disassembly.s.

Run this module as a script to dump the decoded model:
    python3 pipelines/future_composer/hawkeye/config.py
"""
from pipelines.future_composer.config import FCConfig


HAWKEYE = FCConfig(
    name='hawkeye',
    sid_path='hvsc84/MUSICIANS/T/Tel_Jeroen/Hawkeye.sid',

    # Verified by `python3 pipelines/future_composer/hawkeye/data_dump.py`
    freq_lo_addr=0x8337,
    freq_hi_addr=0x8396,
    pattern_ptr_addr=0x8409,
    instr_records_addr=0x860C,
    per_subtune_speed_addr=0x83F5,

    subtune_layout='smc_template_with_sfx',
    per_subtune_smc_addr=0x83FC,
    per_subtune_mode_addr=0x7AFF,
    template_base_hi=0x7B,

    # Hawkeye: 6 music subtunes + 6 SFX; SFX records at pages
    # $92, $94, $96, $98, $9A, $9C (stride = 2 pages)
    music_subtune_count=6,
    sfx_page_base=0x92,
    sfx_page_stride=2,

    # Table sizes
    freq_table_entries=96,
    instr_count=16,
    max_patterns=64,

    # Aux-table addresses found by disassembling Hawkeye's engine:
    #   $7CDD: BD 80 85  lda $8580,X       ← arplo  (NOT $AF7F like CYII)
    #   $7CE6: BD 89 85  lda $8589,X       ← arphi
    #   $810D: B9 8C 84  lda $848C,Y       ← wavearp
    #   $8126: B9 97 84  lda $8497,Y       ← pulsearp
    #   $8279: B9 9F 84  lda $849F,Y       ← drumtabel
    #   $814D: B9 B7 85  lda $85B7,Y       ← filterbytes
    #   pulsetabel at $85EC (signature match)
    #   vibtabwait at $8704 (signature match)
    # NOT FOUND: startlen, starttabel — Hawkeye doesn't use noise_tick
    # (no instrument has fx3 bit $80 set), so the engine probably
    # doesn't include the noti routine. Defaults to $0000 placeholders.
    drumtabel_addr=0x849F,
    filterbytes_addr=0x85B7,
    arplo_addr=0x8580,
    arphi_addr=0x8589,
    pulsetabel_addr=0x85EC,
    vibtabwait_addr=0x8704,
    wavearp_addr=0x848C,           # $810D: LDA $848C,Y
    pulsearp_addr=0x8497,          # $8126: LDA $8497,Y
    # startlen_addr/starttabel_addr left at default 0 (unused).

    # Hawkeye uses wavearpwait=3 ($8106: CMP #$03), pulsearpwait=1
    # ($811C: CMP #$01). Cyb II uses (2, 1).
    wavearpwait=3,
    pulsearpwait=1,

    # Hawkeye's nextvoice writes in this order per voice (verified by
    # diffing HVSC's writelog): pw lo, pw hi, ctrl, freq lo, freq hi.
    nextvoice_write_order=(2, 3, 4, 0, 1),

    # fm2 cleanup is structurally different from Cyb II in Hawkeye —
    # see disassembly.s $8199-$81A5:
    #   $81A0: lda #$e0
    #   $81A5: sta $d416     ; only $D416, no $D418
    # And no strange-filter check before the cleanup. Verified in RE_NOTES.
    fm2_cleanup_d416_value=0xE0,
    fm2_cleanup_writes_d418=False,
    fm2_cleanup_checks_strange_filter=False,

    # Hawkeye's per-voice loop is interleaved (not tight nextvoice):
    # PW writes happen early ($80F4/$80FA), CTRL+FREQ writes happen
    # late ($8311/$8317/$831D), and the filter handler interleaves its
    # $D416/$D418 writes between them. See RE_NOTES.md "Per-voice loop
    # structure" for the full disassembly walk.
    voice_loop_layout='interleaved',
)


if __name__ == '__main__':
    from pipelines.future_composer.engine_model import extract, print_song
    print_song(extract(HAWKEYE))
