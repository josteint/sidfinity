"""
Detect GT2 compilation flags from USF song data.
Port of greloc.c's optimization logic.
"""


def detect_gt2_flags(song, r):
    """Detect compilation flags from USF Song and parse_gt2_direct result.

    Returns dict of flag_name → 0 (enabled) or 1 (disabled).
    """
    ni = len(song.instruments)

    # All flags start as 1 (disabled/optimized out)
    F = {}
    for k in ['NOEFFECTS','NOGATE','NOFILTER','NOFILTERMOD','NOPULSE','NOPULSEMOD',
              'NOWAVEDELAY','NOWAVECMD','NOREPEAT','NOTRANS','NOPORTAMENTO','NOTONEPORTA',
              'NOVIB','NOINSTRVIB','NOSETAD','NOSETSR','NOSETWAVE','NOSETWAVEPTR',
              'NOSETPULSEPTR','NOSETFILTPTR','NOSETFILTCUTOFF','NOSETFILTCTRL',
              'NOSETMASTERVOL','NOFUNKTEMPO','NOGLOBALTEMPO','NOCHANNELTEMPO',
              'NOFIRSTWAVECMD','NOCALCULATEDSPEED','NONORMALSPEED','NOZEROSPEED']:
        F[k] = 1

    speed_left = []

    def calcspeedtest(pos):
        if pos == 0:
            F['NOZEROSPEED'] = 0
            return
        if pos - 1 < len(speed_left):
            if speed_left[pos - 1] >= 0x80:
                F['NOCALCULATEDSPEED'] = 0
            else:
                F['NONORMALSPEED'] = 0
        else:
            F['NOCALCULATEDSPEED'] = 0
            F['NONORMALSPEED'] = 0

    # --- Scan orderlists ---
    if hasattr(song, '_raw_gt2') and song._raw_gt2 and 'col_data' in song._raw_gt2:
        for vi in range(3):
            entries = song.orderlists[vi]
            for i in range(len(entries) - 2):
                if (entries[i] == entries[i+1] == entries[i+2]):
                    F['NOREPEAT'] = 0
                    break
            for _, t in entries:
                if t != 0:
                    F['NOTRANS'] = 0

    # --- Scan patterns ---
    for patt in song.patterns:
        for ev in patt.events:
            if ev.type in ('off', 'on'):
                F['NOGATE'] = 0
            cmd = ev.command
            if cmd is not None and cmd != 0:
                F['NOEFFECTS'] = 0
                if cmd == 5: F['NOSETAD'] = 0
                if cmd == 6: F['NOSETSR'] = 0
                if cmd == 7: F['NOSETWAVE'] = 0
                if cmd == 8: F['NOSETWAVEPTR'] = 0
                if cmd == 9: F['NOSETPULSEPTR'] = 0
                if cmd == 10: F['NOSETFILTPTR'] = 0
                if cmd == 11: F['NOSETFILTCTRL'] = 0
                if cmd == 12: F['NOSETFILTCUTOFF'] = 0
                if cmd == 13: F['NOSETMASTERVOL'] = 0
                if cmd in (1, 2, 3, 4):
                    calcspeedtest(ev.command_val)
                if cmd == 14:
                    F['NOFUNKTEMPO'] = 0
                    F['NOGLOBALTEMPO'] = 0
                if cmd == 15:
                    val = ev.command_val
                    if (val & 0x7F) < 3:
                        F['NOFUNKTEMPO'] = 0
                    if val & 0x80:
                        F['NOCHANNELTEMPO'] = 0
                    else:
                        F['NOGLOBALTEMPO'] = 0
            elif cmd == 0:
                F['NOEFFECTS'] = 0

    # --- Scan instruments ---
    for inst in song.instruments:
        if inst.vib_speed_idx > 0:
            F['NOINSTRVIB'] = 0
            F['NOVIB'] = 0
            calcspeedtest(inst.vib_speed_idx)
        if getattr(inst, 'pulse_ptr', 0) > 0:
            F['NOPULSE'] = 0
        if getattr(inst, 'filter_ptr', 0) > 0:
            F['NOFILTER'] = 0
        if inst.first_wave in (0, 0xFE, 0xFF):
            F['NOFIRSTWAVECMD'] = 0

    # --- Scan wave table ---
    for l, rv in song.shared_wave_table:
        if l == 0xFF:
            continue
        if 0 < l < 0x10:
            F['NOWAVEDELAY'] = 0
        if 0xE0 <= l <= 0xEF:
            F['NOWAVECMD'] = 0
            wave_cmd = l - 0xE0
            if wave_cmd in (1, 2, 3, 4):
                calcspeedtest(rv)
            if wave_cmd == 9:
                F['NOPULSE'] = 0
            if wave_cmd == 10:
                F['NOFILTER'] = 0

    # --- Scan pulse table ---
    for l, rv in song.shared_pulse_table:
        if l == 0xFF:
            continue
        if 0 < l < 0x80:
            F['NOPULSEMOD'] = 0

    # --- Scan filter table ---
    for l, rv in song.shared_filter_table:
        if l == 0xFF:
            continue
        if 0 < l < 0x80:
            F['NOFILTERMOD'] = 0

    # --- FIXEDPARAMS ---
    FIXEDPARAMS = 1
    gt_vals = r.get('col_data', {}).get('gate_timer', [])
    fw_vals = r.get('col_data', {}).get('first_wave', [])
    if gt_vals and len(set(gt_vals)) > 1:
        FIXEDPARAMS = 0
    if fw_vals and len(set(fw_vals)) > 1:
        FIXEDPARAMS = 0

    # --- SIMPLEPULSE ---
    SIMPLEPULSE = 1
    for l, _ in song.shared_pulse_table:
        if l >= 0x80 and l < 0xFF:
            SIMPLEPULSE = 0
            break

    F['FIXEDPARAMS'] = FIXEDPARAMS
    F['SIMPLEPULSE'] = SIMPLEPULSE

    # --- Flag dependencies ---
    if F['NOFILTER']:
        F['NOFILTERMOD'] = 1
    if F['NOPULSE']:
        F['NOPULSEMOD'] = 1
    if F['NOVIB']:
        F['NOINSTRVIB'] = 1
    if F['NOEFFECTS']:
        for k in ['NOSETAD','NOSETSR','NOSETWAVE','NOSETWAVEPTR','NOSETPULSEPTR',
                   'NOSETFILTPTR','NOSETFILTCTRL','NOSETFILTCUTOFF','NOSETMASTERVOL']:
            F[k] = 1

    return F
