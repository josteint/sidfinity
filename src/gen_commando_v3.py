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


def gen_note(note, tempo):
    pitch = note['pitch']
    dur = note['duration']
    inst_raw = note['instrument']
    # das_model: bits 6 AND 7 are flags. Preserve them - they're needed at
    # runtime for hub_off counter (+1 for bit6 legato, +2 for bit7 tie, +3
    # for full new note). The actual instrument index is bits 0-5.
    # Pattern byte stores the RAW value; codegen masks for table indexing.
    # no_release is encoded in bit 7 of drum_trig (das_model_gen.py:197).
    # Hubbard's no_release flag suppresses HR at the end of THIS note; the
    # next note inherits the still-on gate so the SID envelope doesn't
    # retrigger across the boundary. We piggyback the flag on bit 5 of the
    # raw instrument byte (bits 0-3 are the index, 6/7 are the legato/tie
    # flags). Codegen masks it out for table lookup and uses it to skip HR.
    no_release = bool(note.get('drum_trig', 0) & 0x80)
    inst = (inst_raw & 0xFF) | (0x20 if no_release else 0)
    tie = note.get('tie', False)
    # Frame count = dur * tempo (frames per tick). Tempo varies per subtune
    # in Hubbard games — comes from speed_table[subtune]+1.
    frames = dur * tempo
    # Portamento byte: drum_trig has porta speed << 1 in bits 1-6 and
    # direction in bit 0; bit 7 was the no_release flag (extracted above).
    # Strip bit 7, leave the porta payload.
    porta = note.get('drum_trig', 0) & 0x7F
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
    return f"{{ kind := {kind}, durationFrames := {frames}, instrument := {inst}, porta := {porta} }}"


def gen_pattern(idx, notes, tempo):
    note_strs = [gen_note(n, tempo) for n in notes]
    return f"def cv3P{idx} : USFPattern := {{ notes := [{', '.join(note_strs)}] }}"


def main():
    # Subtune list. Default = 3 music subtunes (game, title, intro). Pass
    # comma-separated indices to override, e.g. `gen_commando_v3.py 0,1,2`.
    subtune_indices = [0, 1, 2]
    if len(sys.argv) > 1:
        subtune_indices = [int(x) for x in sys.argv[1].split(',')]

    # Extract per subtune. The first subtune supplies the shared freq table
    # and instruments (which are the same across all Hubbard subtunes that
    # share his player engine).
    extracts = [extract(subtune=s) for s in subtune_indices]
    T, instruments, _ = extracts[0]

    out = ["-- Auto-generated USF v3 Commando data",
           f"-- Subtunes: {subtune_indices} (0-indexed; PSID subtunes "
           f"{[s+1 for s in subtune_indices]})",
           "import USFv3", ""]

    out.append(f"def commandoV3FreqTable : USFFreqTable := {{ entries := {gen_freq_table(T)} }}")
    out.append("")

    for i, inst in enumerate(instruments):
        out.append(gen_instrument(i, inst))
        out.append("")

    # Collect patterns across all subtunes. Each pattern's durationFrames is
    # pre-multiplied by ITS subtune's tempo, so a pattern shared between two
    # subtunes at different tempos would need different durations — we
    # error if that happens. For Commando subtunes 0/1/2 there's no overlap
    # (they each use disjoint pattern ranges).
    all_pats = {}                # pat_idx -> (notes, tempo)
    for (_, _, score) in extracts:
        tempo = score['tempo']
        for v in score['voices']:
            for pat_idx, pat_notes in v['patterns'].items():
                if pat_idx in all_pats:
                    existing_notes, existing_tempo = all_pats[pat_idx]
                    if existing_tempo != tempo:
                        raise SystemExit(
                            f"pattern {pat_idx} shared between subtunes with "
                            f"different tempos ({existing_tempo} vs {tempo}); "
                            f"need tick-based durations to handle this"
                        )
                else:
                    all_pats[pat_idx] = (pat_notes, tempo)

    for idx in sorted(all_pats.keys()):
        notes, tempo = all_pats[idx]
        out.append(gen_pattern(idx, notes, tempo))
        out.append("")

    # Per-subtune voices (orderlists). Each subtune contributes 3 voices.
    voice_defs = []
    voice_global_idx = 0
    subtune_voices = []  # list of (start_idx, count) per subtune
    for si, (_, _, score) in enumerate(extracts):
        start = voice_global_idx
        for v in score['voices']:
            ol = '[' + ', '.join(str(p) for p in v['orderlist']) + ']'
            loop_pt = v.get('loop')
            # rh_decompile uses -1 to mean "no loop / song stops"; USF schema
            # represents that as `none`.
            loop_str = (
                f'some {loop_pt}' if loop_pt is not None and loop_pt >= 0
                else 'none'
            )
            voice_defs.append(
                f"def cv3V{voice_global_idx} : USFVoice := {{ orderlist := {ol}, loopPoint := {loop_str} }}"
            )
            voice_global_idx += 1
        subtune_voices.append((start, voice_global_idx - start))
    out.extend(voice_defs)
    out.append("")

    # Subtune defs: each USFSubtune wraps 3 voices + tempo.
    subtune_defs = []
    for si, ((start, count), (_, _, score)) in enumerate(zip(subtune_voices, extracts)):
        v_refs = ', '.join(f'cv3V{i}' for i in range(start, start + count))
        subtune_defs.append(
            f"def cv3S{si} : USFSubtune := {{ voices := [{v_refs}], tempo := {score['tempo']} }}"
        )
    out.extend(subtune_defs)
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
    subtune_refs = ', '.join(f'cv3S{i}' for i in range(len(extracts)))
    pat_list = ', '.join(pat_refs)

    # Engine quirks for Commando (Hubbard player). Encoded as DATA so the
    # universal codegen can emit code mechanically. See docs/usf_v3_engine_quirks.md.
    quirks = """{
    preserveNoteFlags := true
    voiceScratch := [
      { name := "hub_off", initial := ⟨0, by omega⟩ },   -- slot 0
      { name := "seq_idx", initial := ⟨0, by omega⟩ }    -- slot 1
    ]
    noteLoadOps := [
      -- hub_off (slot 0): bit 6 -> +1, bit 7 -> +2, neither -> +3
      .addByFlag 0 [
        (⟨0x40, by omega⟩, ⟨0x40, by omega⟩, ⟨1, by omega⟩),
        (⟨0x80, by omega⟩, ⟨0x80, by omega⟩, ⟨2, by omega⟩),
        (⟨0x00, by omega⟩, ⟨0x00, by omega⟩, ⟨3, by omega⟩)
      ],
      -- Eager pattern-end behaviors (das_model v2nd1):
      -- when next byte is the EOP marker, reset hub_off and inc seq_idx
      .resetIfNextEnds 0,
      .incIfNextEnds   1 ⟨1, by omega⟩
    ]
    patternEndOps := [
      -- Also (redundantly) on next note's advance_order
      .reset 0,
      .increment 1 ⟨1, by omega⟩
    ]
    dynamicFreqEntries := [
      -- ===== Frame-start updates =====
      -- T[100]: V2.hub_off (lo), V3.hub_off (hi)
      { freqSlot := 100,
        loSource := .scratch ⟨1, by omega⟩ 0,
        hiSource := .scratch ⟨2, by omega⟩ 0,
        phase    := .atFrameStart },
      -- T[104]: V1.ctrl (lo), V2.ctrl (hi). Hubbard percussion noise feed.
      { freqSlot := 104,
        loSource := .voiceCtrl ⟨0, by omega⟩,
        hiSource := .voiceCtrl ⟨1, by omega⟩,
        phase    := .atFrameStart },

      -- ===== Between V3 and V2 (= beforeVoice 1) =====
      -- T[98]: V1.seq_idx (lo), V2.seq_idx (hi)
      { freqSlot := 98,
        loSource := .scratch ⟨0, by omega⟩ 1,
        hiSource := .scratch ⟨1, by omega⟩ 1,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[99]: V3.seq_idx (lo), V1.hub_off (hi)
      { freqSlot := 99,
        loSource := .scratch ⟨2, by omega⟩ 1,
        hiSource := .scratch ⟨0, by omega⟩ 0,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[105]: V3.ctrl (lo), V1.pitch (hi)
      { freqSlot := 105,
        loSource := .voiceCtrl ⟨2, by omega⟩,
        hiSource := .voicePitch ⟨0, by omega⟩,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[106]: V2.pitch (lo), V3.pitch (hi)
      { freqSlot := 106,
        loSource := .voicePitch ⟨1, by omega⟩,
        hiSource := .voicePitch ⟨2, by omega⟩,
        phase    := .beforeVoice ⟨1, by omega⟩ },
      -- T[107]: V1.inst (lo), V2.inst (hi)
      --   At this phase V1 hasn't loaded yet so v_inst[V1] is "prev_inst";
      --   V2 may or may not have loaded depending on its own scheduling.
      { freqSlot := 107,
        loSource := .voiceInst ⟨0, by omega⟩,
        hiSource := .voiceInst ⟨1, by omega⟩,
        phase    := .beforeVoice ⟨1, by omega⟩ },

      -- ===== Between V2 and V1 (= beforeVoice 0) =====
      -- T[100]: re-update so V1 sees latest V2.hub_off this frame
      { freqSlot := 100,
        loSource := .scratch ⟨1, by omega⟩ 0,
        hiSource := .scratch ⟨2, by omega⟩ 0,
        phase    := .beforeVoice ⟨0, by omega⟩ },
      -- T[104]: re-update similarly
      { freqSlot := 104,
        loSource := .voiceCtrl ⟨0, by omega⟩,
        hiSource := .voiceCtrl ⟨1, by omega⟩,
        phase    := .beforeVoice ⟨0, by omega⟩ }
    ]
  }"""

    out.append(f"""def commandoV3 : USFSong := {{
  freqTable := commandoV3FreqTable
  instruments := [{inst_refs}]
  patterns := [{pat_list}]
  subtunes := [{subtune_refs}]
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
