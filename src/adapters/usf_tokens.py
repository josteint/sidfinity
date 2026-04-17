"""
adapters.usf_tokens — ML tokenization for USF Song objects.

tokenize(song) -> list of string tokens
detokenize(tokens) -> Song
"""

from usf.format import (
    Song, Instrument, Sample, WaveTableStep, PulseTableStep, FilterTableStep,
    SpeedTableEntry, Pattern, NoteEvent,
    NOTE_NAMES, WAVEFORM_NAMES, WAVEFORM_TOKENS, TOKEN_TO_WAVEFORM,
    note_name, note_from_name,
)


def tokenize(song):
    """Convert a Song to a list of string tokens.

    This is the format used for ML training.
    """
    tokens = []

    # Song header
    tokens.append('SONG')
    if song.title:
        tokens.append(f'TITLE:{song.title}')
    if song.author:
        tokens.append(f'AUTHOR:{song.author}')
    tokens.append(f'SID_{song.sid_model}')
    tokens.append(song.clock)
    tokens.append(f'T{song.tempo}')
    if song.gt2_player_group:
        tokens.append(f'GROUP_{song.gt2_player_group}')
    # Player behavior — all fields needed for lossless SID rebuild
    if song.first_note != 0:
        tokens.append(f'FN{song.first_note}')
    if not song.nowavedelay:
        tokens.append('WAVEDELAY')
    if song.ad_param != 0x0F:
        tokens.append(f'ADPARAM{song.ad_param:02X}')
    if song.sr_param != 0x00:
        tokens.append(f'SRPARAM{song.sr_param:02X}')
    if song.adsr_write_order != 'sr_first':
        tokens.append(f'ADSRORD_{song.adsr_write_order.upper()}')
    if song.loadregs_adsr_order != 'sr_first':
        tokens.append(f'LRORD_{song.loadregs_adsr_order.upper()}')
    if song.newnote_reg_scope != 'all_regs':
        tokens.append(f'NNSCOPE_{song.newnote_reg_scope.upper()}')
    if song.ghost_regs != 'none':
        tokens.append(f'GHOST_{song.ghost_regs.upper()}')
    if song.vibrato_param_fix:
        tokens.append('VIBFIX')
    if song.nocalculatedspeed:
        tokens.append('NOCALCSPD')
    if song.pulse_speed_asl:
        tokens.append('PULSEASL')
    if song.filter_cutoff_low != 0:
        tokens.append(f'FCLW{song.filter_cutoff_low}')
    if song.multiplier > 0:
        tokens.append(f'MULTI{song.multiplier}')
    if song.psid_flags != 0x0014:
        tokens.append(f'PSID{song.psid_flags:04X}')
    if song.freq_lo is not None:
        tokens.append('FREQLO:' + ''.join(f'{b:02X}' for b in song.freq_lo))
    if song.freq_hi is not None:
        tokens.append('FREQHI:' + ''.join(f'{b:02X}' for b in song.freq_hi))
    if song.orderlist_restart != [0, 0, 0]:
        tokens.append(f'OLRST:{song.orderlist_restart[0]},{song.orderlist_restart[1]},{song.orderlist_restart[2]}')
    if song.songs != 1:
        tokens.append(f'SONGS{song.songs}')

    # Samples (4-bit digi)
    for samp in song.samples:
        tokens.append('SAMP')
        if samp.name:
            tokens.append(f'SNAME:{samp.name}')
        tokens.append(f'SRATE{samp.rate}')
        if samp.loop_start >= 0:
            tokens.append(f'SLOOP{samp.loop_start},{samp.loop_end}')
        # Sample data as hex pairs (each byte = 2 packed 4-bit samples)
        tokens.append('SDATA[')
        for byte_i in range(0, len(samp.data), 16):
            chunk = samp.data[byte_i:byte_i + 16]
            tokens.append(''.join(f'{b:02X}' for b in chunk))
        tokens.append(']SDATA')
        tokens.append('/SAMP')

    # Instruments
    for inst in song.instruments:
        tokens.append('INST')
        tokens.append(f'AD{inst.ad:02X}')
        tokens.append(f'SR{inst.sr:02X}')
        # Map waveform name to token (e.g. 'pulse' -> 'PUL', 'tri_ring' -> 'TRR')
        _wf_to_tok = {
            'tri': 'TRI', 'saw': 'SAW', 'pulse': 'PUL', 'noise': 'NOI',
            'tri_ring': 'TRR', 'saw_ring': 'SAR', 'pulse_ring': 'PUR',
            'tri_sync': 'TRS', 'saw_sync': 'SAS', 'pulse_sync': 'PUS',
            'tri_ring_sync': 'TXS', 'saw_ring_sync': 'SXS', 'pulse_ring_sync': 'PXS',
        }
        tokens.append(_wf_to_tok.get(inst.waveform, inst.waveform.upper()[:3]))
        tokens.append(f'HR_{inst.hr_method.upper()}')
        tokens.append(f'GT{inst.gate_timer:X}')
        if inst.legato:
            tokens.append('LEG')
        if inst.vib_speed_idx > 0:
            tokens.append('VLOG' if inst.vib_logarithmic else 'VLIN')
            tokens.append(f'VIB{inst.vib_speed_idx:X}')
        if inst.vib_delay > 0:
            tokens.append(f'VD{inst.vib_delay:X}')
        if inst.first_wave >= 0:
            tokens.append(f'FW{inst.first_wave:02X}')
        if inst.pulse_width != 0x0808:
            tokens.append(f'PW{inst.pulse_width:04X}')
        if inst.wave_ptr > 0:
            tokens.append(f'WP{inst.wave_ptr}')
        if inst.pulse_ptr > 0:
            tokens.append(f'PP{inst.pulse_ptr}')
        if inst.filter_ptr > 0:
            tokens.append(f'FP{inst.filter_ptr}')

        # Wave table
        if inst.wave_table:
            tokens.append('WT[')
            for step in inst.wave_table:
                slide_suffix = f'/s{step.freq_slide:+d}' if step.freq_slide else ''
                # Always use raw hex for waveform to preserve gate/ring/sync bits
                wt = f'${step.waveform:02X}'
                if step.is_loop:
                    tokens.append(f'L{step.loop_target}')
                elif step.delay > 0:
                    # Delay steps can carry waveform, note_offset, absolute_note, keep_freq
                    extras = ''
                    if step.waveform != 0x41:
                        extras += f':{step.waveform:02X}'
                    if step.keep_freq:
                        extras += '~'
                    elif step.note_offset != 0:
                        sign = '+' if step.note_offset >= 0 else ''
                        extras += f'n{sign}{step.note_offset}'
                    elif step.absolute_note >= 0:
                        if step.absolute_note <= 95:
                            extras += f'a{note_name(step.absolute_note)}'
                        else:
                            extras += f'aN{step.absolute_note}'
                    tokens.append(f'W{step.delay}{extras}')
                elif step.keep_freq:
                    tokens.append(f'{wt}~{slide_suffix}')
                elif step.absolute_note >= 0:
                    if step.absolute_note <= 95:
                        tokens.append(f'{wt}={note_name(step.absolute_note)}{slide_suffix}')
                    else:
                        # Notes > 95 can't be expressed as note names
                        tokens.append(f'{wt}=N{step.absolute_note}{slide_suffix}')
                else:
                    off = step.note_offset
                    sign = '+' if off >= 0 else ''
                    tokens.append(f'{wt}{sign}{off}{slide_suffix}')
            tokens.append(']WT')

        # Pulse table
        if inst.pulse_table:
            tokens.append('PT[')
            for step in inst.pulse_table:
                if step.is_loop:
                    tokens.append(f'L{step.loop_target}')
                elif step.is_set:
                    tokens.append(f'={step.value:02X}{step.low_byte:02X}')
                else:
                    tokens.append(f'm{step.value:+d}x{step.duration}')
            tokens.append(']PT')

        # Filter table
        if inst.filter_table:
            tokens.append('FT[')
            for step in inst.filter_table:
                if step.is_loop:
                    tokens.append(f'L{step.loop_target}')
                elif step.type == 'cutoff':
                    if step.cutoff_low:
                        tokens.append(f'C{step.value:02X}L{step.cutoff_low}')
                    else:
                        tokens.append(f'C{step.value:02X}')
                elif step.type == 'modulate':
                    tokens.append(f'm{step.value:+d}x{step.duration}')
                elif step.type == 'params':
                    tokens.append(f'R{step.value:02X}')
            tokens.append(']FT')

        tokens.append('/INST')

    # Speed table
    if song.speed_table:
        tokens.append('SPD[')
        for entry in song.speed_table:
            tokens.append(f'{entry.left:02X}{entry.right:02X}')
        tokens.append(']SPD')

    # Shared tables (raw byte pairs — lossless roundtrip)
    if song.shared_wave_table:
        tokens.append('SWT[')
        for l, r in song.shared_wave_table:
            tokens.append(f'{l:02X}{r:02X}')
        tokens.append(']SWT')
    if song.shared_pulse_table:
        tokens.append('SPT[')
        for l, r in song.shared_pulse_table:
            tokens.append(f'{l:02X}{r:02X}')
        tokens.append(']SPT')
    if song.shared_filter_table:
        tokens.append('SFT[')
        for l, r in song.shared_filter_table:
            tokens.append(f'{l:02X}{r:02X}')
        tokens.append(']SFT')

    # Patterns
    for patt in song.patterns:
        tokens.append(f'PAT{patt.id}')

        current_inst = -1
        for event in patt.events:
            if event.instrument >= 0:
                tokens.append(f'I{event.instrument}')

            if event.type == 'note':
                tokens.append(note_name(event.note))
            elif event.type == 'rest':
                tokens.append('.')
            elif event.type == 'off':
                tokens.append('OFF')
            elif event.type == 'on':
                tokens.append('ON')
            elif event.type == 'tie':
                tokens.append('TIE')
            elif event.type == 'digi':
                # DIGI<sample_id> with optional rate override in command_val
                if event.command_val > 0:
                    tokens.append(f'DIGI{event.note}R{event.command_val}')
                else:
                    tokens.append(f'DIGI{event.note}')

            if event.command is not None:
                tokens.append(f'x{event.command:X}{event.command_val:02X}')

            if event.duration > 1:
                tokens.append(f'd{event.duration}')

        tokens.append('/PAT')

    # Orderlists
    tokens.append('ORD')
    for vi in range(3):
        tokens.append(f'V{vi + 1}')
        for patt_id, transpose in song.orderlists[vi]:
            if transpose != 0:
                tokens.append(f'T{"+" if transpose > 0 else ""}{transpose}')
            tokens.append(f'P{patt_id}')
        tokens.append(f'/V{vi + 1}')
    tokens.append('/ORD')

    # Extra orderlists for multi-song SIDs
    if song.extra_orderlists:
        tokens.append('XORD')
        for idx, entries in enumerate(song.extra_orderlists):
            tokens.append(f'XV{idx}')
            restart = song.extra_orderlist_restart[idx] if idx < len(song.extra_orderlist_restart) else 0
            if restart != 0:
                tokens.append(f'XRST{restart}')
            for patt_id, transpose in entries:
                if transpose != 0:
                    tokens.append(f'T{"+" if transpose > 0 else ""}{transpose}')
                tokens.append(f'P{patt_id}')
            tokens.append(f'/XV{idx}')
        tokens.append('/XORD')

    tokens.append('/SONG')
    return tokens


def detokenize(tokens):
    """Convert a list of tokens back to a Song.

    Inverse of tokenize().
    """
    song = Song()
    i = 0

    while i < len(tokens):
        t = tokens[i]

        if t == 'SONG':
            pass
        elif t.startswith('TITLE:'):
            song.title = t[6:]
        elif t.startswith('AUTHOR:'):
            song.author = t[7:]
        elif t.startswith('GROUP_'):
            song.gt2_player_group = t[6:]
        elif t.startswith('SID_'):
            song.sid_model = t[4:]
        elif t in ('PAL', 'NTSC'):
            song.clock = t
        elif t.startswith('T') and t[1:].isdigit():
            song.tempo = int(t[1:])
        elif t.startswith('FN') and t[2:].isdigit():
            song.first_note = int(t[2:])
        elif t == 'WAVEDELAY':
            song.nowavedelay = False
        elif t.startswith('ADPARAM'):
            song.ad_param = int(t[7:], 16)
        elif t.startswith('SRPARAM'):
            song.sr_param = int(t[7:], 16)
        elif t.startswith('ADSRORD_'):
            song.adsr_write_order = t[8:].lower()
        elif t.startswith('LRORD_'):
            song.loadregs_adsr_order = t[6:].lower()
        elif t.startswith('NNSCOPE_'):
            song.newnote_reg_scope = t[8:].lower()
        elif t.startswith('GHOST_'):
            song.ghost_regs = t[6:].lower()
        elif t == 'VIBFIX':
            song.vibrato_param_fix = True
        elif t == 'NOCALCSPD':
            song.nocalculatedspeed = True
        elif t == 'PULSEASL':
            song.pulse_speed_asl = True
        elif t.startswith('FCLW') and t[4:].isdigit():
            song.filter_cutoff_low = int(t[4:])
        elif t.startswith('MULTI') and t[5:].isdigit():
            song.multiplier = int(t[5:])
        elif t.startswith('PSID') and len(t) == 8:
            song.psid_flags = int(t[4:], 16)
        elif t.startswith('FREQLO:'):
            song.freq_lo = bytes(int(t[7+j*2:9+j*2], 16) for j in range(len(t[7:])//2))
        elif t.startswith('FREQHI:'):
            song.freq_hi = bytes(int(t[7+j*2:9+j*2], 16) for j in range(len(t[7:])//2))
        elif t.startswith('OLRST:'):
            parts = t[6:].split(',')
            song.orderlist_restart = [int(p) for p in parts]
        elif t.startswith('SONGS') and t[5:].isdigit():
            song.songs = int(t[5:])
        elif t == 'SAMP':
            samp = Sample(id=len(song.samples))
            i += 1
            while i < len(tokens) and tokens[i] != '/SAMP':
                t2 = tokens[i]
                if t2.startswith('SNAME:'):
                    samp.name = t2[6:]
                elif t2.startswith('SRATE') and t2[5:].isdigit():
                    samp.rate = int(t2[5:])
                elif t2.startswith('SLOOP'):
                    parts = t2[5:].split(',')
                    samp.loop_start = int(parts[0])
                    samp.loop_end = int(parts[1]) if len(parts) > 1 else -1
                elif t2 == 'SDATA[':
                    data_bytes = bytearray()
                    i += 1
                    while i < len(tokens) and tokens[i] != ']SDATA':
                        hex_str = tokens[i]
                        for j in range(0, len(hex_str), 2):
                            data_bytes.append(int(hex_str[j:j+2], 16))
                        i += 1
                    samp.data = bytes(data_bytes)
                i += 1
            song.samples.append(samp)

        elif t == 'INST':
            inst = Instrument(id=len(song.instruments))
            i += 1
            while i < len(tokens) and tokens[i] != '/INST':
                t2 = tokens[i]
                if t2.startswith('AD'):
                    inst.ad = int(t2[2:], 16)
                elif t2.startswith('SR'):
                    inst.sr = int(t2[2:], 16)
                elif t2 in TOKEN_TO_WAVEFORM:
                    inst.waveform = TOKEN_TO_WAVEFORM[t2]
                elif t2.startswith('HR_'):
                    inst.hr_method = t2[3:].lower()
                elif t2.startswith('GT') and len(t2) <= 4:
                    inst.gate_timer = int(t2[2:], 16)
                elif t2 == 'LEG':
                    inst.legato = True
                elif t2 == 'VLOG':
                    inst.vib_logarithmic = True
                elif t2 == 'VLIN':
                    inst.vib_logarithmic = False
                elif t2.startswith('VIB') and t2 != 'VIBRATO':
                    inst.vib_speed_idx = int(t2[3:], 16)
                elif t2.startswith('VD'):
                    inst.vib_delay = int(t2[2:], 16)
                elif t2.startswith('FW'):
                    inst.first_wave = int(t2[2:], 16)
                elif t2.startswith('PW') and len(t2) == 6:
                    inst.pulse_width = int(t2[2:], 16)
                elif t2.startswith('WP') and t2[2:].isdigit():
                    inst.wave_ptr = int(t2[2:])
                elif t2.startswith('PP') and t2[2:].isdigit():
                    inst.pulse_ptr = int(t2[2:])
                elif t2.startswith('FP') and t2[2:].isdigit():
                    inst.filter_ptr = int(t2[2:])
                elif t2 == 'PT[':
                    i += 1
                    while i < len(tokens) and tokens[i] != ']PT':
                        pt = tokens[i]
                        step = PulseTableStep()
                        if pt.startswith('L'):
                            step.is_loop = True
                            step.loop_target = int(pt[1:])
                        elif pt.startswith('='):
                            step.is_set = True
                            step.value = int(pt[1:3], 16)
                            step.low_byte = int(pt[3:5], 16)
                        elif pt.startswith('m'):
                            # m+3x5 = modulate speed +3 for 5 frames
                            parts = pt[1:].split('x')
                            step.value = int(parts[0])
                            step.duration = int(parts[1]) if len(parts) > 1 else 1
                        inst.pulse_table.append(step)
                        i += 1
                elif t2 == 'FT[':
                    i += 1
                    while i < len(tokens) and tokens[i] != ']FT':
                        ft = tokens[i]
                        step = FilterTableStep()
                        if ft.startswith('L') and ft[1:].isdigit():
                            step.is_loop = True
                            step.loop_target = int(ft[1:])
                        elif ft.startswith('C'):
                            step.type = 'cutoff'
                            # C<HH> or C<HH>L<n> (with cutoff_low)
                            if 'L' in ft[1:]:
                                li = ft.index('L', 1)
                                step.value = int(ft[1:li], 16)
                                step.cutoff_low = int(ft[li+1:])
                            else:
                                step.value = int(ft[1:], 16)
                        elif ft.startswith('R'):
                            step.type = 'params'
                            step.value = int(ft[1:], 16)
                        elif ft.startswith('m'):
                            step.type = 'modulate'
                            parts = ft[1:].split('x')
                            step.value = int(parts[0])
                            step.duration = int(parts[1]) if len(parts) > 1 else 1
                        inst.filter_table.append(step)
                        i += 1
                elif t2 == 'WT[':
                    i += 1
                    while i < len(tokens) and tokens[i] != ']WT':
                        wt = tokens[i]
                        step = WaveTableStep()
                        # Extract /sN freq_slide suffix if present
                        if '/s' in wt:
                            slide_idx = wt.index('/s')
                            step.freq_slide = int(wt[slide_idx + 2:])
                            wt = wt[:slide_idx]  # strip suffix for normal parsing
                        if wt.startswith('L'):
                            step.is_loop = True
                            step.loop_target = int(wt[1:])
                        elif wt.startswith('W') and len(wt) > 1 and wt[1].isdigit():
                            # Delay: W3, W3:0F, W3:0Fn+7, W3:01~, W3:08aC4, W3:08aN96
                            rest = wt[1:]
                            d_end = 0
                            while d_end < len(rest) and rest[d_end].isdigit():
                                d_end += 1
                            step.delay = int(rest[:d_end])
                            rest = rest[d_end:]
                            if rest.startswith(':'):
                                step.waveform = int(rest[1:3], 16)
                                rest = rest[3:]
                            if rest.endswith('~') or '~' in rest:
                                step.keep_freq = True
                                rest = rest.replace('~', '')
                            if 'n' in rest:
                                ni = rest.index('n')
                                step.note_offset = int(rest[ni+1:])
                            elif rest.startswith('aN'):
                                step.absolute_note = int(rest[2:])
                            elif rest.startswith('a'):
                                step.absolute_note = note_from_name(rest[1:])
                        elif wt.endswith('~'):
                            # Keep freq: $41~ or PUL~
                            wn = wt[:-1]
                            if wn.startswith('$'):
                                step.waveform = int(wn[1:], 16)
                            else:
                                step.waveform = WAVEFORM_NAMES.get(wn.lower() + '_gate', 0x41)
                            step.keep_freq = True
                        elif '=' in wt:
                            # Absolute note: $81=C4 or $81=N96 (numeric > 95)
                            parts = wt.split('=')
                            if parts[0].startswith('$'):
                                step.waveform = int(parts[0][1:], 16)
                            else:
                                step.waveform = WAVEFORM_NAMES.get(parts[0].lower() + '_gate', 0x41)
                            if parts[1].startswith('N') and parts[1][1:].isdigit():
                                step.absolute_note = int(parts[1][1:])
                            else:
                                step.absolute_note = note_from_name(parts[1])
                        elif wt.startswith('$'):
                            # Raw hex waveform: $30+0 or $30-2
                            rest = wt[1:]
                            for sep in ('+', '-'):
                                if sep in rest:
                                    parts = rest.split(sep, 1)
                                    step.waveform = int(parts[0], 16)
                                    step.note_offset = int(sep + parts[1])
                                    break
                        else:
                            # Named waveform: PUL+4 or NOI-2
                            for wn, wv in [('PUL', 0x41), ('SAW', 0x21), ('TRI', 0x11), ('NOI', 0x81)]:
                                if wt.startswith(wn):
                                    step.waveform = wv
                                    step.note_offset = int(wt[len(wn):])
                                    break
                        inst.wave_table.append(step)
                        i += 1
                i += 1
            song.instruments.append(inst)

        elif t.startswith('PAT'):
            patt_id = int(t[3:])
            patt = Pattern(id=patt_id)
            i += 1
            current_inst = -1
            while i < len(tokens) and tokens[i] != '/PAT':
                t2 = tokens[i]
                if t2.startswith('I') and t2[1:].isdigit():
                    current_inst = int(t2[1:])
                elif t2 == '.':
                    patt.events.append(NoteEvent(type='rest', instrument=current_inst))
                    current_inst = -1  # only set once
                elif t2 == 'OFF':
                    patt.events.append(NoteEvent(type='off'))
                elif t2 == 'ON':
                    patt.events.append(NoteEvent(type='on'))
                elif t2 == 'TIE':
                    patt.events.append(NoteEvent(type='tie'))
                elif t2.startswith('DIGI'):
                    # DIGI<sample_id> or DIGI<sample_id>R<rate>
                    rest = t2[4:]
                    rate_override = 0
                    if 'R' in rest:
                        parts = rest.split('R')
                        sample_id = int(parts[0])
                        rate_override = int(parts[1])
                    else:
                        sample_id = int(rest)
                    patt.events.append(NoteEvent(type='digi', note=sample_id,
                                                  command_val=rate_override))
                elif t2.startswith('x') and len(t2) >= 4:
                    # Command: x1FF = command 1, param $FF
                    if patt.events:
                        patt.events[-1].command = int(t2[1], 16)
                        patt.events[-1].command_val = int(t2[2:4], 16)
                elif t2.startswith('d') and t2[1:].isdigit():
                    # Duration modifier for previous event
                    if patt.events:
                        patt.events[-1].duration = int(t2[1:])
                else:
                    # Try as note name
                    n = note_from_name(t2)
                    if n >= 0:
                        patt.events.append(NoteEvent(type='note', note=n,
                                                      instrument=current_inst))
                        current_inst = -1
                i += 1
            song.patterns.append(patt)

        elif t == 'ORD':
            pass
        elif t.startswith('V') and len(t) == 2 and t[1].isdigit():
            vi = int(t[1]) - 1
            i += 1
            current_trans = 0
            while i < len(tokens) and not tokens[i].startswith('/V'):
                t2 = tokens[i]
                if t2.startswith('T') and (t2[1] == '+' or t2[1] == '-' or t2[1:].lstrip('+-').isdigit()):
                    current_trans = int(t2[1:])
                elif t2.startswith('P') and t2[1:].isdigit():
                    patt_id = int(t2[1:])
                    song.orderlists[vi].append((patt_id, current_trans))
                    current_trans = 0
                i += 1

        elif t == 'XORD':
            # Extra orderlists for multi-song SIDs
            i += 1
            while i < len(tokens) and tokens[i] != '/XORD':
                t2 = tokens[i]
                if t2.startswith('XV') and t2[2:].isdigit():
                    # Start of an extra orderlist voice
                    current_entries = []
                    current_restart = 0
                    current_trans = 0
                    i += 1
                    xv_idx = t2  # e.g. 'XV0'
                    while i < len(tokens) and not tokens[i].startswith('/XV'):
                        t3 = tokens[i]
                        if t3.startswith('XRST') and t3[4:].isdigit():
                            current_restart = int(t3[4:])
                        elif t3.startswith('T') and len(t3) > 1 and (t3[1] == '+' or t3[1] == '-' or t3[1:].lstrip('+-').isdigit()):
                            current_trans = int(t3[1:])
                        elif t3.startswith('P') and t3[1:].isdigit():
                            patt_id = int(t3[1:])
                            current_entries.append((patt_id, current_trans))
                            current_trans = 0
                        i += 1
                    song.extra_orderlists.append(current_entries)
                    song.extra_orderlist_restart.append(current_restart)
                i += 1

        elif t == 'SPD[':
            i += 1
            while i < len(tokens) and tokens[i] != ']SPD':
                s = tokens[i]
                if len(s) == 4:
                    song.speed_table.append(SpeedTableEntry(
                        left=int(s[:2], 16), right=int(s[2:], 16)))
                i += 1

        elif t == 'SWT[':
            i += 1
            while i < len(tokens) and tokens[i] != ']SWT':
                s = tokens[i]
                if len(s) == 4:
                    song.shared_wave_table.append((int(s[:2], 16), int(s[2:], 16)))
                i += 1
        elif t == 'SPT[':
            i += 1
            while i < len(tokens) and tokens[i] != ']SPT':
                s = tokens[i]
                if len(s) == 4:
                    song.shared_pulse_table.append((int(s[:2], 16), int(s[2:], 16)))
                i += 1
        elif t == 'SFT[':
            i += 1
            while i < len(tokens) and tokens[i] != ']SFT':
                s = tokens[i]
                if len(s) == 4:
                    song.shared_filter_table.append((int(s[:2], 16), int(s[2:], 16)))
                i += 1

        elif t == '/SONG':
            break

        i += 1

    return song
