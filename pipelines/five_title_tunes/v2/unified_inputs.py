"""Unified 5 Title Tunes — ONE engine, 5 subtunes.

Builds a single `_Inputs` that the shared codegen turns into ONE PSID
with 5 music subtunes. Instruments from the 5 sub-engines are
concatenated and re-numbered (absolute IDs 1..56 across subs).
Per-subtune engine params (speed_ctr_init, incby2_step, late_gate)
and per-subtune ovseed go into runtime tables (see codegen.py's
Phase-2 path). Off-table arpeggio is only used by sub_1; the shared
freqtab carries sub_1's state region — the other subs never read
past pitch 95.
"""

from __future__ import annotations

from dataclasses import replace

from pipelines.hubbard.codegen import _Inputs, _inputs_from_config
from pipelines.five_title_tunes.v2.config import ALL_TUNES


# Per-Hubbard-'85 freq-table state offsets (where the engine's
# per-voice load-time state lives). Default = Commando's.
_SEED_OFS = {'v_ctrl': 208, 'pwm_period': 229, 'pwm_dir': 232,
             'v_instr': 214, 'v_durfield': 205, 'v_slide': 239}


def _ovseed_from_freq_bytes(freq_bytes: bytes, inst_offset: int = 0) -> bytes:
    """Extract the 18-byte ovseed from a sub's freq_bytes. `inst_offset`
    shifts the per-voice v_instr bytes by the sub's instrument-table
    offset — in the unified build each sub's instruments live at
    different positions in the global concatenated table, so the
    initial v_instr values (which are sub-local indices in the raw
    binary) must be re-numbered to point at the same instrument in
    the merged table."""
    out = []
    for field in ('v_ctrl', 'pwm_period', 'pwm_dir',
                  'v_instr', 'v_durfield', 'v_slide'):
        for i in range(3):
            b = freq_bytes[_SEED_OFS[field] + i]
            if field == 'v_instr':
                # Renumber: keep flag bits (high 2), shift inst idx.
                flags = b & 0xC0
                idx = b & 0x3F
                b = flags | ((idx + inst_offset) & 0x3F)
            out.append(b)
    return bytes(out)


def build_unified_inputs() -> _Inputs:
    """Build a unified 5-subtune `_Inputs` from the 5 per-sub configs."""
    sub_inputs = [_inputs_from_config(cfg) for cfg in ALL_TUNES]

    # Renumber instruments globally: sub_0's 0..7 → 0..7, sub_1's 0..11 →
    # 8..19, sub_2 → 20..31, sub_3 → 32..43, sub_4 → 44..55.
    all_models = []
    inst_offsets = []
    offset = 0
    for si in sub_inputs:
        inst_offsets.append(offset)
        for m in si.models:
            all_models.append(replace(m, inst=m.inst + offset))
        offset += len(si.models)

    # Re-index note instrument bytes AND pattern indices to be globally
    # unique. Different subs use overlapping pattern index ranges (each
    # has patterns 1, 2, 3, ...) so without renumbering the codegen's
    # pattern-pool dedup would collapse different subs' patterns onto
    # the first one seen. We shift each sub's pattern indices by a
    # per-sub offset to make them unique.
    all_scores = []
    pat_offsets = []
    pat_offset = 0
    for sub_idx, si in enumerate(sub_inputs):
        pat_offsets.append(pat_offset)
        max_pat = 0
        for score in si.scores:
            for v in score.voices:
                if v.orderlist:
                    max_pat = max(max_pat, max(v.orderlist, default=0))
                if v.patterns:
                    max_pat = max(max_pat, max(v.patterns.keys(), default=0))
        pat_offset += max_pat + 1

    for sub_idx, si in enumerate(sub_inputs):
        for score in si.scores:
            new_voices = []
            for v in score.voices:
                # Renumber pattern indices in the orderlist.
                new_orderlist = [oidx + pat_offsets[sub_idx]
                                 for oidx in v.orderlist]
                new_patterns = {}
                for pat_id, notes in v.patterns.items():
                    new_notes = []
                    for n in notes:
                        flags = n.instrument & 0xC0
                        local_inst = n.instrument & 0x3F
                        new_inst = local_inst + inst_offsets[sub_idx]
                        new_notes.append(
                            replace(n, instrument=flags | new_inst))
                    new_patterns[pat_id + pat_offsets[sub_idx]] = new_notes
                new_voices.append(replace(v, orderlist=new_orderlist,
                                          patterns=new_patterns))
            all_scores.append(replace(score, voices=new_voices))

    # Per-subtune tables. incby2_onset is globalized to $10 — subs 0/2/3
    # have no fx-bit-1 instruments and don't read it; subs 1 and 4 both
    # use $10.
    per_subtune_speed_ctr_init = [cfg.speed_ctr_init for cfg in ALL_TUNES]
    per_subtune_incby2_step = [cfg.incby2_step for cfg in ALL_TUNES]
    per_subtune_incby2_late_gate = [
        cfg.incby2_late_gate if cfg.incby2_late_gate is not None else 0xFF
        for cfg in ALL_TUNES]
    per_subtune_ovseed = [
        _ovseed_from_freq_bytes(si.freq_bytes, inst_offset=inst_offsets[i])
        for i, si in enumerate(sub_inputs)]

    # Concatenate per-sub resetspd and voice_starts (each sub has 1 sub).
    resetspds = [si.resetspds[0] for si in sub_inputs]
    voice_starts = [si.voice_starts[0] for si in sub_inputs]

    # Off-table arpeggio: only sub_1 has notes with arp pitch >= 96.
    # Use sub_1's freq_bytes as the unified freqtab — its state region
    # holds the bytes sub_1's off-table reads expect. The other subs
    # never read past pitch 95.
    freq_bytes = sub_inputs[1].freq_bytes

    # PSID header — copy from parent SID.
    parent_path = (
        'hvsc84/MUSICIANS/H/Hubbard_Rob/5_Title_Tunes.sid')
    with open(parent_path, 'rb') as f:
        parent_hdr = f.read(124)

    return _Inputs(
        title=parent_hdr[22:54],
        author=parent_hdr[54:86],
        released=parent_hdr[86:118],
        start_song=1,
        arp_interval=12,
        arp_period=2,
        linear_pw_or=0,
        # Scalar fallbacks (overridden by per_subtune_* tables).
        incby2_step=2,
        incby2_every_frame=False,
        incby2_onset=0x10,        # globalized — see comment above
        suppress_first_notestart=False,
        freeze_on_stop=False,
        speed_ctr_init=0,
        first_frame_gate_off=False,
        stop_fill=None,
        sfx_framectr_ofs=253,
        sfx_state_ofs=None,
        has_sfx=False,
        subtunes=(0, 1, 2, 3, 4),
        models=all_models,
        scores=all_scores,
        resetspds=resetspds,
        voice_starts=voice_starts,
        freq_bytes=freq_bytes,
        sfx_list=[],
        seed_overlap=True,
        psid_speed=0,
        per_subtune_speed_ctr_init=per_subtune_speed_ctr_init,
        per_subtune_incby2_step=per_subtune_incby2_step,
        per_subtune_incby2_late_gate=per_subtune_incby2_late_gate,
        per_subtune_ovseed=per_subtune_ovseed,
    )


def build_unified_sid(out_path: str) -> str:
    """Build the unified 5TT PSID directly via `_emit_sid`."""
    from pipelines.hubbard.codegen import _emit_sid
    from pipelines.hubbard.note_codec import BitPackCodec
    inputs = build_unified_inputs()
    _emit_sid(inputs, out_path, BitPackCodec())
    return out_path


if __name__ == '__main__':
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else '/tmp/5tt_unified.sid'
    p = build_unified_sid(out)
    import os
    print(f'wrote {p} ({os.path.getsize(p)} bytes)')
