"""
Generate USF v3 Commando data as a Lean file.
"""
import sys
sys.path.insert(0, 'src')
from das_model_gen import extract


def hex_byte(n):
    return f"⟨{n & 0xFF}, by omega⟩"


def gen_freq_table(T):
    """Emit 128 entries: standard PAL 0-95, plus engine-extracted 96-127.
    Pitch 104 is special-cased in player (dynamic ctrl byte alias).
    """
    pairs = []
    for i in range(128):
        if i < len(T):
            flo = T[i] & 0xFF
            fhi = (T[i] >> 8) & 0xFF
        else:
            flo = 0
            fhi = 0
        # Zero out pitch 104 (decompiler marks it as percussion .dynamicCtrl)
        if i == 104:
            flo = 0
            fhi = 0
        pairs.append(f"({hex_byte(flo)}, {hex_byte(fhi)})")
    return "[" + ", ".join(pairs) + "]"


def gen_instrument(idx, inst):
    pw = inst['P']
    bit0 = inst.get('has_bit0', False)
    arp_off = inst.get('arp_offset', 0)
    vib = inst.get('vibrato_scale', 0)
    w = inst['W']
    waveform = w['steps']
    loop = w['loop']
    init_pw = pw['init_pw']
    init_lo = init_pw & 0xFF
    init_hi = (init_pw >> 8) & 0x0F

    if pw['speed'] == 0:
        pwmod = 'none'
    elif pw['mode'] == 'linear':
        pwmod = (
            f"some {{ mode := .linear {hex_byte(pw['speed'])}, "
            f"stepEvery := 1, startDelay := 0 }}"
        )
    else:
        pwmod = (
            f"some {{ mode := .bidirectional {hex_byte(pw['speed'])} "
            f"{hex_byte(pw.get('min_hi', 8))} {hex_byte(pw.get('max_hi', 14))}, "
            f"stepEvery := 1, startDelay := 0 }}"
        )

    if vib == 0:
        vibspec = 'none'
    else:
        vibspec = (
            f"some {{ shape := .triangle, periodFrames := 8, "
            f"semitoneShift := {vib + 1}, onsetFrames := 6, "
            f"rampUpFrames := 0, unipolar := true }}"
        )

    if bit0:
        slidespec = (
            "some { kind := .monotonic (-1), stepEvery := 1, "
            "startDelay := 9, stopAtZero := true }"
        )
    else:
        slidespec = 'none'

    if arp_off > 0:
        arpspec = (
            f"some {{ intervals := [0, {arp_off}], stepEvery := 1, "
            f"phaseSource := .global, startDelay := 0 }}"
        )
    else:
        arpspec = 'none'

    eff_parts = []
    if vib > 0:
        eff_parts.append('.vibrato')
    eff_parts.append('.pwMod')
    if bit0:
        eff_parts.append('.freqSlide')
    if arp_off > 0:
        eff_parts.append('.arpeggio')
    eff_parts.append('.gateCheck')
    eff_order = '[' + ', '.join(eff_parts) + ']'

    waveform_lit = '[' + ', '.join(hex_byte(b) for b in waveform) + ']'

    return f"""def cv3I{idx} : USFInstrument := {{
  initCtrl := {hex_byte(waveform[0])}
  initPwLo := {hex_byte(init_lo)}
  initPwHi := {hex_byte(init_hi)}
  ad := {hex_byte(inst['E']['ad'])}
  sr := {hex_byte(inst['E']['sr'])}
  initFreqMod := .normal
  waveformProgram := {waveform_lit}
  waveLoop := {loop}
  waveStepEvery := 1
  pwMod := {pwmod}
  vibrato := {vibspec}
  freqSlide := {slidespec}
  arpeggio := {arpspec}
  effectOrder := {eff_order}
  release := {{ framesBeforeEnd := 3, zeroAdsr := true, noRelease := false }}
  filterEnabled := false
}}"""


def gen_note(note):
    pitch = note['pitch']
    dur = note['duration']
    inst_raw = note['instrument']
    # das_model: bits 6 AND 7 are flags. Preserve them - they're needed at
    # runtime for hub_off counter (+1 for bit6 legato, +2 for bit7 tie, +3
    # for full new note). The actual instrument index is bits 0-5.
    # Pattern byte stores the RAW value; codegen masks for table indexing.
    inst = inst_raw & 0xFF
    tie = note.get('tie', False)
    # Frame count = dur * 3 (Commando tempo), -1 for our DEC-first model
    # Actually, USF should NOT have engine-specific adjustments. Just use frames.
    # The codegen will handle the DEC-first model internally.
    frames = dur * 3
    if tie:
        kind = '.tie'
    elif pitch == 104:
        kind = '.percussion .dynamicCtrl'
    elif pitch < 96:
        kind = f'.pitched {hex_byte(pitch)}'
    else:
        # Other extended pitches — for now treat as dynamicCtrl too
        # (Hubbard's pitch 100, 116 etc.)
        kind = '.percussion .dynamicCtrl'
    return f"{{ kind := {kind}, durationFrames := {frames}, instrument := {inst} }}"


def gen_pattern(idx, notes):
    note_strs = [gen_note(n) for n in notes]
    return f"def cv3P{idx} : USFPattern := {{ notes := [{', '.join(note_strs)}] }}"


def main():
    T, instruments, score = extract()

    out = ["-- Auto-generated USF v3 Commando data",
           "import USFv3", ""]

    out.append(f"def commandoV3FreqTable : USFFreqTable := {{ entries := {gen_freq_table(T)} }}")
    out.append("")

    for i, inst in enumerate(instruments):
        out.append(gen_instrument(i, inst))
        out.append("")

    # Collect all patterns from all voices (deduped)
    all_pats = {}
    for v in score['voices']:
        for pat_idx, pat_notes in v['patterns'].items():
            if pat_idx not in all_pats:
                all_pats[pat_idx] = pat_notes

    for idx in sorted(all_pats.keys()):
        out.append(gen_pattern(idx, all_pats[idx]))
        out.append("")

    # Voices (orderlist)
    voice_defs = []
    for vi, v in enumerate(score['voices']):
        ol = '[' + ', '.join(str(p) for p in v['orderlist']) + ']'
        loop_pt = v.get('loop')
        loop_str = f'some {loop_pt}' if loop_pt is not None else 'none'
        voice_defs.append(
            f"def cv3V{vi} : USFVoice := {{ orderlist := {ol}, loopPoint := {loop_str} }}"
        )
    out.extend(voice_defs)
    out.append("")

    # Pattern list (ordered by index, with empty placeholders for missing indices)
    max_pat = max(all_pats.keys()) + 1
    pat_refs = []
    for i in range(max_pat):
        if i in all_pats:
            pat_refs.append(f'cv3P{i}')
        else:
            pat_refs.append('{ notes := [] }')

    # Final song
    inst_refs = ', '.join(f'cv3I{i}' for i in range(len(instruments)))
    voice_refs = ', '.join(f'cv3V{i}' for i in range(len(score['voices'])))
    pat_list = ', '.join(pat_refs)

    # Engine quirks for Commando (Hubbard player). Encoded as DATA so the
    # universal codegen can emit code mechanically. See docs/usf_v3_engine_quirks.md.
    quirks = """{
    preserveNoteFlags := true
    voiceScratch := [
      { name := "hub_off", initial := ⟨0, by omega⟩ }
    ]
    noteLoadOps := [
      -- Hubbard hub_off: bit 6 -> +1, bit 7 -> +2, neither -> +3
      .addByFlag 0 [
        (⟨0x40, by omega⟩, ⟨0x40, by omega⟩, ⟨1, by omega⟩),
        (⟨0x80, by omega⟩, ⟨0x80, by omega⟩, ⟨2, by omega⟩),
        (⟨0x00, by omega⟩, ⟨0x00, by omega⟩, ⟨3, by omega⟩)
      ]
    ]
    patternEndOps := [
      .reset 0
    ]
    dynamicFreqEntries := [
      -- T[100]: V2.hub_off (lo), V3.hub_off (hi). Updated right before V1
      -- runs so V1 sees the latest values.
      { freqSlot := 100,
        loSource := .scratch ⟨1, by omega⟩ 0,
        hiSource := .scratch ⟨2, by omega⟩ 0,
        phase    := .beforeVoice ⟨0, by omega⟩ }
    ]
  }"""

    out.append(f"""def commandoV3 : USFSong := {{
  freqTable := commandoV3FreqTable
  instruments := [{inst_refs}]
  voices := [{voice_refs}]
  patterns := [{pat_list}]
  voiceOrder := [⟨2, by omega⟩, ⟨1, by omega⟩, ⟨0, by omega⟩]
  filter := none
  playRate := .vbi
  engineQuirks := {quirks}
  title := "Commando"
  author := "Rob Hubbard"
  released := "1985 Elite"
}}""")

    with open('src/formal/CommandoV3.lean', 'w') as f:
        f.write('\n'.join(out) + '\n')

    print(f"Wrote {len(instruments)} instruments, {len(all_pats)} patterns, "
          f"{len(score['voices'])} voices to CommandoV3.lean", file=sys.stderr)


if __name__ == '__main__':
    main()
