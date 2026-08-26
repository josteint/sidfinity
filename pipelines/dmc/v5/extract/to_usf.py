"""DMC V5 model -> USF.

Maps the extracted V5Model onto the engine-neutral USF schema so the
pipeline runs SID -> USF -> SID (the project's "always through USF"
rule). The composer stays model-driven; `from_usf` rebuilds the model
from the parsed USF (the inverse of this module).

Representation choices (USF representation principle):

- WAVE program: each instrument's wave-table slice (followed through the
  engine's $90 jump-back marker) becomes the instrument's
  `waveform`/`wave_freq`/`loop` -- decoding away the engine's wave-table
  pointer. The idle walk (table index 0, the engine's cleared wave
  position before a voice's first note) is carried as `wave_programs[0]`.
  `wave_freq` bytes are kept RAW: each step's mode (melodic offset vs
  absolute freq-hi) is the step's own ctrl bit 3 ($08), visible in
  `waveform`.

- PULSE program: each restarting instrument's pulse-table slice becomes
  an inline `pulse_sweep` (start PW + (add, frames) segments + loop) --
  decoding away the pulse-table pointer. Non-restarting instruments
  (pointer 0) carry `pwm.keep_running` (the running oscillator continues;
  position-persistence is engine mechanism, not stored content).

- SECTORS -> per-voice `Pattern`s (note rows + `hold` gate rows; sticky
  dur/instrument stamped per row). ORDERLISTS -> `Orderlist`
  (sector entries + signed transposes + loop). FREQ table, speed->tempo,
  master vol + filter leftovers -> init.sid; meta -> psid.

FILTER sweeps (voice-3-only) are residue: Katusha uses no filter
program (the model's filter table is a single null entry, no instrument
points into it). A filter-using V5 member needs a `filter_sweep` field
of the same shape as `pulse_sweep`.
"""
from __future__ import annotations

import os

from src.usf.types import (
    Environment,
    UsfFile, PsidMeta, Params, InitState, InitSid, InitFilter, InitVoice,
    Instrument, PwmConfig, VibratoConfig, SweepEnvelope,
    MusicSubtune, VoiceBlock, Orderlist, Pattern, NoteRow, Pitch,
)

# A sweep program advances by `count` frames per segment; bound the
# reachable-phase capture so the engine's table-fusion (programs bleeding
# into one another) is dissolved — beyond this many frames no realistic
# note (or keep-running continuation over a song) reaches.
_PHASE_CAP = 48           # max distinct phases captured (program-size bound)
_WALK_CAP = 5000          # max table reads before declaring the bytes corrupt.
                          # A real sweep terminates (loop / hold / end) in <~50
                          # reads; only a malformed $90-chain (a $90 pointing at
                          # another $90 in a cycle, appending no phase) spins —
                          # this is the seatbelt that turns that into a clean
                          # `unsupported` instead of an infinite loop. NOT a
                          # frame/song bound (capture depth is set by the
                          # program's own loop/hold/end + _PHASE_CAP).
from src.usf.writer import write_file
from pipelines.dmc.v5.config import DMCV5Config
from pipelines.dmc.v5.extract.engine_model import (
    extract, V5Model, _slice_wave, measure_live_window_reads)

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def _pitch(note: int) -> Pitch:
    return Pitch(name=NOTE_NAMES[note % 12], octave=note // 12)


# --- wave program slicing: `_slice_wave` moved to engine_model so the extract's
#     off-table step indexing matches the wave_freq this module emits.


# --- sweep envelope capture (pulse OR filter) ----------------------------
# Walk the engine's (step, count) phase stream from `ptr`, capturing the
# REACHABLE phases (the table is a shared/fused resource; the bleeding past
# the reachable horizon is the packer's space-saving mechanism — Rule 1).
def _capture_env(table: list, ptr: int, has_start: bool = True,
                 start_val: int = 0, reach: int | None = None,
                 count8bit: bool = False,
                 truncate_on_cap: bool = False) -> SweepEnvelope:
    # has_start=True: table[ptr] is the loaded START value, phases begin at
    # ptr+1 (per-instrument pulse/filter — filter_init/pulse_init load the
    # start). has_start=False: ptr is already the first ADD pair, phases begin
    # at ptr, and start_val (the priming cutoff) is recorded for completeness
    # — the V3 idle filter, which has no start entry and continues from the
    # init.sid.filter cutoff.
    #
    # `reach` = the CAPTURE HORIZON in play-frames = the verify window
    # (songlength*1.1*playrate). Stop once the captured phases cover that many
    # frames: the rebuild only ever PLAYS `reach` frames, so capturing past it
    # is wasted AND can overflow the de-fused table (we un-share the packer's
    # overlapped programs, so a full capture can exceed the original's 256
    # entries — that's what truncating beyond the window prevents). A LOOP/hold
    # terminal hits first when it occurs before `reach`. None = no horizon
    # (capture to the natural terminal). This is the song-derived bound, NOT a
    # magic number; `_WALK_CAP` below is a SEPARATE seatbelt (reads, not frames).
    if has_start:
        start = (table[ptr][0] << 8) | table[ptr][1]
        pos = ptr + 1
    else:
        start = start_val
        pos = ptr
    phases = []
    loop = None
    cum = 0
    pos_phase = {}                # table position a phase started at -> index
    iters = 0
    while pos < len(table):
        iters += 1
        if iters > _WALK_CAP:     # malformed table (e.g. a $90->$90 cycle that
            raise RuntimeError(   # appends no phase) — bail clean, don't spin.
                f'unsupported:capture_loop @{ptr}')
        if len(phases) >= _PHASE_CAP:
            if truncate_on_cap:       # off-table one-shot ramp (no loop): keep the
                break                 # captured prefix — it covers far more frames
            raise RuntimeError(f'unsupported:sweep_too_long @{ptr}')  # than any note
        lo, hi = table[pos]
        if lo == 0x90:            # jump to the target byte position
            tgt = hi
            if tgt in pos_phase:  # revisiting a captured phase = a real cycle
                loop = pos_phase[tgt]
                break
            pos = tgt             # otherwise FOLLOW it (the target may be a
            # ⚠ THE ENGINE FOLLOWS EXACTLY ONE $90, then uses the target cell
            # AS A VALUE without re-testing it. Canon v5 filter_run_v3:
            #     $14A0  CMP #$90
            #     $14A2  BNE $14AE          ; not a marker -> use it
            #     $14A4  LDA $19C7,y        ; target
            #     $14A7  STA $17F9          ; new filterpos
            #     $14AA  TAY
            #     $14AB  LDA $19C6,y        ; re-read AT THE TARGET
            #     $14AE  STA $101F          ; ...and USE it. No second check.
            # family-4's pulse/filter handler ($14B4) has the same shape, and
            # the wave path is already documented as reading its start cell
            # with no $90 check. So a target that is ITSELF $90 is a literal
            # ADD value, not another jump.
            #
            # Chasing the chain instead (a bare `continue`) spun on members
            # whose $90s form a cycle that lands on no captured phase, and the
            # walk hit `_WALK_CAP` -> `unsupported:capture_loop`, refusing the
            # whole member: 47 of them, and 46 reach the offending program from
            # a played instrument, so they were not dead garbage slots.
            if pos < len(table) and table[pos][0] == 0x90:
                pos_phase[pos] = len(phases)
                rate = (0x90 << 8) | table[pos][1]
                if rate >= 0x8000:
                    rate -= 0x10000
                if pos + 1 >= len(table):
                    break
                clo, chi = table[pos + 1]
                frames = (chi if chi != 0 else 256) if count8bit else \
                    ((clo << 8) | chi) or 0x10000
                phases.append((rate, frames))
                cum += frames
                pos += 2
                if reach is not None and cum > reach:
                    break
                if frames >= 0x9000:
                    break
            continue
        if pos + 1 >= len(table):  # step without its count
            break
        pos_phase[pos] = len(phases)
        rate = (lo << 8) | hi
        if rate >= 0x8000:
            rate -= 0x10000
        clo, chi = table[pos + 1]
        if count8bit:
            # family-4 pulse: the count is the 8-bit pulsehi[pos+1] ($23BC) only;
            # pulselo[pos+1] ($23A3) is unused garbage that a 16-bit read would
            # fold into the count, inflating `cum` so `reach` truncates early and
            # the re-pack caps the program with a spurious $90 loop. count==0 wraps
            # at 256 (the 8-bit counter), not 65536.
            frames = chi if chi != 0 else 256
        else:
            frames = (clo << 8) | chi
            # count==0 means the engine's 16-bit phase counter wraps (65536
            # frames) before advancing — i.e. a terminal hold. This is also what
            # the off-table zero-region of a small (last-table) filter program
            # decodes to; without this the (0,0) entries spin forever -> PHASE_CAP.
            if frames == 0:
                frames = 0x10000
        phases.append((rate, frames))
        cum += frames
        pos += 2
        if reach is not None and cum > reach:   # past the verify window
            break
        if frames >= 0x9000:       # terminal hold — value stays put
            break
    return SweepEnvelope(start=start, phases=phases, loop=loop)


def _capture_env_f4(table: list, ptr: int, start_val: int = 0,
                    has_start: bool = False,
                    reach: int | None = None,
                    truncate_on_cap: bool = False) -> SweepEnvelope:
    """family-4 filter program: 8-bit (add, count) steps, walked 2 table
    positions per step. `add` = table[pos][0] (filterlo[pos], signed 8-bit);
    `count` = table[pos+1][1] (filterhi[pos+1]); a $90 at table[pos][0] loops
    to table[pos][1]. The 16-bit `_capture_env` misreads this (it fuses the two
    bytes of each pair into one 16-bit value), so family-4 needs its own walk.
    count==0 means the 8-bit counter wraps (256 frames).

    has_start=True (per-instrument filter, $1421): the engine loads
    $1019 = filterlo[ptr] as the START cutoff and begins the sweep at ptr+1
    (filterpos = byte4 then INC). has_start=False (V3 default/idle program,
    filterpos 0): no start entry — start_val is the priming cutoff (f4_fcinit),
    phases begin at ptr."""
    if has_start:
        start = table[ptr][0]          # filterlo[byte4] = the loaded cutoff
        pos = ptr + 1
    else:
        start = start_val
        pos = ptr
    phases: list = []
    loop = None
    pos_phase: dict = {}
    cum = 0
    iters = 0
    while pos < len(table):
        iters += 1
        if iters > _WALK_CAP:
            raise RuntimeError(f'unsupported:capture_loop @{ptr}')
        if len(phases) >= _PHASE_CAP:
            if truncate_on_cap:        # off-table one-shot filter ramp (no loop):
                break                  # keep the prefix (covers >> the re-init interval)
            raise RuntimeError(f'unsupported:sweep_too_long @{ptr}')
        lo, hi = table[pos]
        if lo == 0x90:                 # $90 -> loop to target position `hi`
            if hi in pos_phase:
                loop = pos_phase[hi]
                break
            pos = hi
            # ONE $90 ONLY — same engine rule as `_capture_env` above (family-4
            # pulse/filter handler at $14B4 falls through to use the target cell
            # as the ADD value without re-testing it). A target that is itself
            # $90 is a literal add, not another jump.
            if pos < len(table) and table[pos][0] == 0x90:
                if pos + 1 >= len(table):
                    break
                pos_phase[pos] = len(phases)
                cnt = table[pos + 1][1]
                phases.append((0x90 - 0x100, cnt if cnt != 0 else 256))
                cum += phases[-1][1]
                pos += 2
                if reach is not None and cum > reach:
                    break
            continue
        if pos + 1 >= len(table):
            break
        pos_phase[pos] = len(phases)
        add = lo if lo < 0x80 else lo - 0x100
        count = table[pos + 1][1]
        frames = count if count != 0 else 256
        phases.append((add, frames))
        cum += frames
        pos += 2
        if reach is not None and cum > reach:
            break
    return SweepEnvelope(start=start, phases=phases, loop=loop)


# --- sectors -> pattern rows ---------------------------------------------
# Each note/gate becomes a row; the leading parameter commands ($FD dur,
# $FC snd, $F3 vol, $F8 frq, $F7/$F6 fade, $F2/$F1 adr/srr, $F9 flt,
# $F5 gate_toggle) attach to the FOLLOWING row as ORDERED prefix flags.
# Their byte position is preserved verbatim because the engine's gate-off
# lookahead reads the raw next byte -- a command may not be reshuffled
# relative to the notes/gates around it. The note/gate main events:
# note (<$80), gate ($FE)=tie, gate_tie ($F4), glide ($FB)=note+glide,
# slide ($FA)=tie+glide.

# event name -> (prefix flag formatter): single-arg positioned commands
_PREFIX = {
    'dur': lambda v: f'set_dur=${v:02X}',
    'snd': lambda v: f'set_instr={v}',
    'vol': lambda v: f'vol={v}',
    'frq': lambda v: f'frq=${v:02X}',
    'fade_in': lambda v: f'fade_in=${v:02X}',
    'fade_out': lambda v: f'fade_out=${v:02X}',
    'adr': lambda v: f'adr=${v:02X}',
    'srr': lambda v: f'srr=${v:02X}',
    'flt': lambda v: f'filter=${v:02X}',
    # family-4-only prefix command (see engine_model._CMD). $F0 is handled
    # separately in _sector_rows (it decomposes into two fields).
    'freq_bias': lambda v: f'freq_bias=${v:02X}',
}


def _note_byte(n: int) -> Pitch:
    # A raw note/glide-target byte (0-255). Values >95 are OFF-TABLE indices —
    # the player reads past the 96-entry freq table, and (for glide/slide
    # targets) the player adds the running transpose first: the effective index
    # is (n + transpose) & $FF, which usually wraps back in-table (the target is
    # stored transpose-relative, e.g. raw $FE = "transpose-2"). The 2-digit-
    # octave NOTE_NAME (e.g. $FE -> "D-21") round-trips losslessly through
    # _pitch / _pitch_str_num, and from_usf re-emits `& $FF`, so the byte is
    # preserved. (The old >119 reject predated 2-digit-octave off-table pitches.)
    if not 0 <= n <= 255:
        raise RuntimeError(f'unsupported:note_out_of_range {n}')
    return _pitch(n)


def _sector_rows(events: list) -> list:
    rows = []
    dur = 1
    pending = []                         # leading commands, in order
    ended = False                        # saw the $FF lookahead terminator
    for e in events:
        cmd = e[0]
        if cmd in _PREFIX:
            if cmd == 'dur':
                dur = e[1]
            pending.append(_PREFIX[cmd](e[1]))
        elif cmd == 'f0':                # $F0: decompose the packed byte into
            pending.append(f'f0_vib_width={e[1] & 0x07}')   # vib width ($1856)
            pending.append(f'f0_wave_count={e[1] >> 4}')     # wave count ($1809)
        elif cmd == 'gate_toggle':       # $F5: flip gate flag (no duration)
            pending.append('gate_toggle')
        elif cmd == 'note':
            rows.append(NoteRow(pitch=_note_byte(e[1]), duration=dur,
                                fx_flags=tuple(pending)))
            pending = []
        elif cmd == 'gate':              # $FE: hold current note, no retrigger
            rows.append(NoteRow(pitch=Pitch.rest(), duration=dur,
                                fx_flags=tuple(pending) + ('tie',)))
            pending = []
        elif cmd == 'gate_tie':          # $F4: hold + toggle gate-mask bit
            rows.append(NoteRow(pitch=Pitch.rest(), duration=dur,
                                fx_flags=tuple(pending) + ('gate_tie',)))
            pending = []
        elif cmd == 'glide':             # $FB spd cur tgt: note + glide
            _, spd, cur, tgt = e
            rows.append(NoteRow(
                pitch=_note_byte(cur), duration=dur,
                fx_flags=tuple(pending)
                + (f'glide={spd}', f'glide_to={_note_byte(tgt)}')))
            pending = []
        elif cmd == 'slide':             # $FA spd tgt: hold + glide to target
            _, spd, tgt = e
            rows.append(NoteRow(
                pitch=Pitch.rest(), duration=dur,
                fx_flags=tuple(pending)
                + (f'glide={spd}', f'glide_to={_note_byte(tgt)}')))
            pending = []
        elif cmd == 'end':
            ended = True
            break
        else:
            raise RuntimeError(f'unsupported:sector_cmd {cmd}')
    if pending and ended:
        # Unreachable under the corrected decode: `$FF` only terminates a
        # sector as the lookahead peeked straight after a ROW ($118C/$1314), so
        # a terminated sector can never have commands left over. Kept as a
        # tripwire in case the walk's end model is ever loosened again.
        raise RuntimeError(f'unsupported:trailing_sector_cmds {pending}')
    # A sector that did NOT terminate CYCLES (its byte-wide position wrapped),
    # so these commands are not orphans — they are the lead-in of the next lap,
    # and the engine reaches them again with rows following. Our re-encoding
    # terminates every sector with $FF, so the lap boundary is already the
    # documented divergence point for this shape; dropping the commands here
    # loses nothing further and lets the member build instead of being refused.
    return rows


def _orderlist(events: list) -> Orderlist:
    entries, transposes = [], []
    transpose = 0
    loop_to = None
    loop_reestablish = False
    stop = False
    # Map raw byte offset -> (entry index, is_transpose_prefix). A loop target
    # is a byte offset that lands on ONE of two things (byte offsets are
    # unique): an entry's SECTOR byte, or an entry's leading $FD/$FC transpose
    # PREFIX. The distinction is the loop's transpose semantics:
    #   - target = PREFIX byte  -> the player re-dispatches the transpose each
    #     wrap (RE-ESTABLISH); loop_transpose carries the value.
    #   - target = SECTOR byte (past the prefix, or an unprefixed entry) -> the
    #     player CARRIES the running transpose over the wrap; loop_transpose
    #     stays None.
    # Recording only the prefix byte sent past-the-prefix targets to loop_to=0;
    # recording only the sector byte sent prefix targets there. Record both.
    byte_map = {}
    byte_pos = 0
    prefix_start = None       # byte where the pending entry's $FD/$FC prefix began
    for e in events:
        if e[0] == 'sector':
            i = len(entries)
            byte_map[byte_pos] = (i, False)           # sector byte = carry
            if prefix_start is not None:
                byte_map[prefix_start] = (i, True)    # prefix byte = re-establish
            prefix_start = None
            entries.append(e[1])
            transposes.append(transpose)
            byte_pos += 1
        elif e[0] == 'transpose':
            if prefix_start is None:
                prefix_start = byte_pos               # transpose prefix start
            t = e[1]
            transpose = t - 256 if t >= 128 else t   # signed
            byte_pos += 2
        elif e[0] in ('loop', 'wrap'):
            # 'wrap' = the track ran out of its 256-byte window and the player's
            # byte-wide position rolled onto an already-dispatched offset. Same
            # musical meaning as a stated $FF loop to that offset.
            tgt = e[1]                                # raw byte offset
            loop_to, loop_reestablish = byte_map.get(tgt, (0, False))
        elif e[0] == 'end':
            stop = True
    loop_transpose = (transposes[loop_to]
                      if (loop_reestablish and loop_to is not None
                          and loop_to < len(transposes)) else None)
    ol = Orderlist(entries=entries, loop_to=loop_to, stop=stop,
                   loop_transpose=loop_transpose,
                   transposes=transposes if any(transposes) else [])
    return ol


def _pulse_env_for(model, ptr, reach):
    """Per-instrument pulse env. family-4's pulse count is 8-bit; capture it that
    way so a multi-step PWM program isn't truncated early. An OFF-TABLE pulse pointer
    (program walks past the real table into adjacent STATIC bytes — proven static by
    the $23A3-$24BB taint check) is a one-shot ramp with no $90 loop, so under 8-bit
    counts the walk runs past _PHASE_CAP. The old fallback to the 16-bit capture was
    WRONG for family-4: it read the 8-bit count byte as the low half of a 16-bit count
    (e.g. E0 -> 0xFFE0 = 65504, a terminal hold), collapsing the whole program to a
    single +32 ramp and DISCARDING the off-table sweep (the flat-stream localized
    Jupiter41 blocker at write 56000). Instead, TRUNCATE the 8-bit walk at the phase
    cap: family-4 pulse programs re-init on every note-load, so the walk never runs
    longer than one note — and _PHASE_CAP phases already cover far more frames than any
    note holds, so the captured prefix (which keeps the +2048 sweep) is faithful."""
    if not ptr:
        return None
    if getattr(model, 'pulse_ctr_8bit', False):
        try:
            return _capture_env(model.pulse, ptr, reach=reach, count8bit=True)
        except RuntimeError:
            # off-table one-shot ramp overflowed the phase cap: keep the correct
            # 8-bit-count prefix rather than the family-4-incorrect 16-bit fallback.
            return _capture_env(model.pulse, ptr, reach=reach, count8bit=True,
                                truncate_on_cap=True)
    return _capture_env(model.pulse, ptr, reach=reach)


def _filter_env_for(model, ptr, reach):
    """Per-instrument filter env — same off-table one-shot-ramp handling as
    _pulse_env_for. A filter pointer that walks off-table (past its table into
    adjacent static bytes, no $90 loop) is a one-shot ramp that generates unbounded
    phases at the whole-song reach -> _PHASE_CAP -> sweep_too_long. The filter
    re-inits on every note-load (V3, $1421), so it never runs longer than one note;
    TRUNCATE the captured prefix (which covers >> the re-init interval) instead of
    raising. Only kicks in on RuntimeError, so a member whose filter already captures
    cleanly (all currently-FULL members) is untouched -> zero-regression by construction."""
    if not ptr:
        return None
    if getattr(model, 'filter_prog_8bit', False):
        try:
            return _capture_env_f4(model.filter, ptr, has_start=True, reach=reach)
        except RuntimeError:
            return _capture_env_f4(model.filter, ptr, has_start=True, reach=reach,
                                   truncate_on_cap=True)
    try:
        return _capture_env(model.filter, ptr, reach=reach)
    except RuntimeError:
        return _capture_env(model.filter, ptr, reach=reach, truncate_on_cap=True)


def _instrument_to_usf(ins, model: V5Model, reach: int | None = None):
    """Map a V5Instrument to a USF Instrument. The wave program is decoded
    inline (self-looping, separable); pulse/filter are entry indices into
    the tune's shared tables (carried whole by model_to_usf). `reach` = the
    per-song capture horizon (see _capture_env)."""
    wc, wf, wl = _slice_wave(model.wave, ins.wave_ptr)
    # pulse_ptr == 0 = no restart (the PW oscillator keeps running across
    # the note); a real entry index restarts the sweep there.
    return Instrument(
        id=ins.id,
        waveform=list(wc),
        loop=wl,
        wave_freq=[b & 0xFF for b in wf],
        adsr=(ins.ad, ins.sr),
        pwm=PwmConfig(keep_running=(ins.pulse_ptr == 0)),
        pulse_env=_pulse_env_for(model, ins.pulse_ptr, reach),
        filter_env=_filter_env_for(model, ins.filter_ptr, reach),
        vibrato=VibratoConfig(onset=ins.vib_delay, speed=ins.vib_speed,
                              amplitude=ins.vib_width),
        offtable_freq=list(ins.offtable_freq),
    )


def model_to_usf(m: V5Model, reach: int | None = None) -> UsfFile:
    # one Pattern per global sector (shared across voices); each voice
    # carries the Patterns its orderlist references.
    #
    # BUILD ONLY THE REFERENCED ONES. Every voice attaches `sector_pat[s]` for
    # the sectors ITS orderlist names (below), so a pattern no orderlist names
    # is built and then thrown away — but `_sector_rows` can REFUSE while
    # building it, and that refusal killed the whole member. 12 of the 15
    # `trailing_sector_cmds` members are exactly this: their trailing commands
    # sit on sectors no track ever plays, so the engine never executes them and
    # there is nothing musical to lose (C7). A sector pointer table routinely
    # carries unplayed junk — un-relocated compilation leftovers (C31), packer
    # padding — and none of it should be able to refuse a member.
    referenced = {s for st in (m.subtunes or [m]) for ol in st.orderlists
                  for e in ol if e[0] == 'sector' for s in [e[1]]}
    sector_pat = {i: Pattern(id=i, length=0, rows=_sector_rows(ev))
                  for i, ev in enumerate(m.sectors) if i in referenced}
    for p in sector_pat.values():
        p.length = sum(r.duration for r in p.rows)

    # one MusicSubtune per orderlist record. The data tables (sectors above,
    # instruments/freq/wave_programs below) are SHARED at the top level; each
    # subtune carries only its 3 voices (orderlists) + tempo + master vol.
    # The file-image leftovers (filter cutoff, $1013 speed-counter / $101C
    # fade-frac startup phases, $100F idle notes) are GLOBAL -> subtune 0.
    sub_data = m.subtunes or [m]
    usf_subs = []
    for si, st in enumerate(sub_data):
        voices = []
        for vi in range(3):
            ol = _orderlist(st.orderlists[vi])
            used = sorted(set(ol.entries))
            pats = [sector_pat[s] for s in used]
            voices.append(VoiceBlock(id=vi + 1, orderlist=ol, patterns=pats))
        sid = InitSid(
            master_vol=st.master_vol,
            filter=(InitFilter(cutoff_lo=m.lo_fclo, cutoff_hi=m.lo_fchi,
                               res_routing=m.lo_filtmode) if si == 0 else None))
        usf_subs.append(MusicSubtune(
            id=si + 1, tempo=st.speed, voices=voices,
            init=InitState(
                sid=sid,
                voices=([InitVoice(id=v + 1, note=m.lo_notes[v])
                         for v in range(3)] if si == 0 else []),
                # $1013 speed-counter + $101C fade-frac startup phases
                # (init clears neither) — engine-state priming (§4.5),
                # subtune-0 only. speed_ctr_init = the Hubbard/5TT key.
                speed_ctr_init=(m.lo_spdctr if si == 0 else 0),
                fade_frac_init=(m.lo_mvolfrac if si == 0 else 0))))

    instruments = [_instrument_to_usf(ins, m, reach=reach) for ins in m.instruments]
    # idle wave walk (cleared wave position 0 -> what a voice's effects
    # read before its first note).
    idle_c, idle_f, idle_l = _slice_wave(m.wave, 0)

    # idle (default) V3 filter sweep: filter-table position 0 is a default
    # cutoff program the engine runs from frame 0 (no instrument points at it;
    # filterpos starts at 0). PLAY-TIME content, not init priming — the start
    # cutoff STATE stays in init.sid.filter. Capture pos 0 FAITHFULLY: a leading
    # (0,0) is a valid zero-rate HOLD phase whose count is at pos 1 (e.g.
    # Cooksey: hold ~20 frames then ramp $1415/frame), NOT "no idle" — the old
    # `m.filter[0] != (0,0)` gate dropped exactly those swept-after-a-hold idle
    # programs (the FL_LO partial cluster), so the composer held the priming
    # cutoff forever where the orig sweeps. (Same fix the default_pulse twin
    # below already got in round-8.) The `any rate != 0` check below keeps a
    # PURE-hold idle (the cutoff genuinely holds at the priming value) as None.
    default_filter = None
    if m.filter:
        try:                       # best-effort: a malformed idle table -> no
            if getattr(m, 'filter_prog_8bit', False):  # 8-bit (add,count) walk
                idle = _capture_env_f4(m.filter, 0,
                                       start_val=m.lo_fchi, reach=reach)
            else:                   # default_filter (composer holds), not a
                idle = _capture_env(    # member-wide error.
                    m.filter, 0, has_start=False,
                    start_val=((m.lo_fchi << 8) | m.lo_fclo), reach=reach)
        except RuntimeError:
            idle = None
        if idle and any(rate != 0 for rate, _ in idle.phases):
            default_filter = idle

    # idle (default) per-voice PULSE-WIDTH sweep: pulse-table position 0, run by
    # a voice from pulsepos=0 (pulse_run is unconditional) before/between its
    # own pulse programs. Pulse twin of the idle filter; PW starts at 0 (cleared
    # at init). Capture pos 0 FAITHFULLY — a leading (0,0) is a valid zero-rate
    # phase whose count is at pos 1, NOT "no idle" (e.g. Symphony: +0 for 256
    # frames then +80 ramp; Digital_Rain: +0 for 2048). The old `pulse[0]!=(0,0)
    # + any-nonzero-rate` gate dropped both, so the composer's null pos-0 either
    # held where orig ramps (A) or bled into the adjacent instrument program
    # where orig holds (B). Emit None ONLY for a TRIVIAL terminal hold (a single
    # zero-rate phase with count >= 0x9000) — that's the genuine no-idle case,
    # kept as the single (0,0) null to preserve the 891-FULL layout (round-8: a
    # fabricated multi-entry hold there shifted the de-fused table + regressed).
    default_pulse = None
    if m.pulse:
        try:
            idle_p = _capture_env(m.pulse, 0, has_start=False,
                                  start_val=0, reach=reach,
                                  count8bit=getattr(m, 'pulse_ctr_8bit', False))
        except RuntimeError:
            idle_p = None
        if idle_p and idle_p.phases:
            ph = idle_p.phases
            trivial_hold = (len(ph) == 1 and ph[0][0] == 0
                            and ph[0][1] >= 0x9000)
            if not trivial_hold:
                default_pulse = idle_p

    return UsfFile(
        psid=PsidMeta(title=m.title, author=m.author, released=m.released,
                      clock=getattr(m, 'clock', 'PAL'),
                      sid=getattr(m, 'sid_model', 6581),
                      start_song=1),
        # C18 phase schedule is TEMPORAL DISPATCH — trichotomy §4.3, so it
        # belongs beside cia_period/play_repeat/init_plays rather than in the
        # params bag (ledger C33).
        environment=(Environment(cia_period=getattr(m, 'cia_period', 0),
                                 play_phases=getattr(m, 'play_phases', '') or '')
                     if (getattr(m, 'cia_period', 0)
                         or getattr(m, 'play_phases', '')) else None),
        params=Params(fields={
            # PLAYER-MECHANISM KNOBS (Principle §8): named behaviours, not
            # the originating player's name. Emitted only when they differ
            # from the default, so a canon member's USF is unchanged.
            **({'noteon_skip_freq_clear': 1} if getattr(m, 'noteon_skip_freq_clear', False) else {}),
            **({'wave_speed_from_instr': 1} if getattr(m, 'wave_speed_from_instr', False) else {}),
            **({'volovr_ad_zero': 1} if getattr(m, 'volovr_ad_zero', False) else {}),
            **({'pulse_ctr_8bit': 1} if getattr(m, 'pulse_ctr_8bit', False) else {}),
            **({'noteload_no_d418': 1} if getattr(m, 'noteload_no_d418', False) else {}),
            **({'filter_v3_only': 1} if getattr(m, 'filter_v3_only', False) else {}),
            **({'filter_needs_cmd': 1} if getattr(m, 'filter_needs_cmd', False) else {}),
            **({'filter_d416_only': 1} if getattr(m, 'filter_d416_only', False) else {}),
            **({'d418_skip_vib_reversal': 1} if getattr(m, 'd418_skip_vib_reversal', False) else {}),
            **({'wave_step_carry': 1} if getattr(m, 'wave_step_carry', False) else {}),
            **({'vib_from_instr_bytes': 1} if getattr(m, 'vib_from_instr_bytes', False) else {}),
            **({'filter_prog_8bit': 1} if getattr(m, 'filter_prog_8bit', False) else {}),
            **({'play_skip_init': int(getattr(m, 'play_skip_init', 2))}
               if int(getattr(m, 'play_skip_init', 2)) != 2 else {}),
            **({'dur_ctr_init': int(getattr(m, 'dur_ctr_init', 1))}
               if int(getattr(m, 'dur_ctr_init', 1)) != 1 else {}),
        }),
        init=InitState(),
        instruments=instruments,
        subtunes=usf_subs,
        # per-tune tuning: 96 lo + 96 hi
        freq_table=list(m.freq_lo) + list(m.freq_hi),
        wave_programs={0: {'ctrl': list(idle_c),
                           'freq': [b & 0xFF for b in idle_f],
                           'loop': idle_l}},
        default_filter=default_filter,
        default_pulse=default_pulse,
        # off-table reads ride per-instrument `offtable_freq` (ML-musical).
    )


_SL_DB = None       # cached Songlengths.md5 (loaded once per process)


def _verify_window_frames(cfg: DMCV5Config, hvsc_root: str) -> int:
    """The sweep CAPTURE HORIZON (= `reach`) in 50Hz play-frames: the verify
    window. verify plays each subtune for clamp(songlen*1.1, 5, 1500) s and the
    shared sweep tables must cover the LONGEST subtune. Verified V5 members are
    all vblank (CIA/multispeed are rejected upstream), so 50Hz is exact. Falls
    back to 30000 (~600s, the old fixed horizon) when the songlength is
    unknown."""
    global _SL_DB
    try:
        from src.songlengths import load_database, get_durations
        if _SL_DB is None:
            _SL_DB = load_database(
                os.path.join(hvsc_root, 'DOCUMENTS', 'Songlengths.md5'))
        durs = get_durations(os.path.join(hvsc_root, cfg.sid_path), _SL_DB)
    except Exception:
        durs = None
    if not durs:
        return 30000
    win_s = max(min(d * 1.1, 1500.0) for d in durs)
    return int(win_s * 50) + 200        # + small margin over the play window


def _emit_live_position_form(m, usf, seen: dict, over: list):
    """Rewrite `usf` into the live-position form (see the caller comment):
    live-window record slots become named `LiveSignal`s and every
    env-carrying instrument gains its original table start position. Raises
    the refusal when an observed read value falls outside every captured
    program region (the delta-serve validity condition)."""
    import dataclasses
    from src.usf.types import LiveSignal
    # (kind, idx) -> (signal name, 1-based voice | None)
    sig_of = {(k, i): (name, voice)
              for (k, i, name, voice) in m.offtable_live_reads}
    # captured program regions per table: [start, start + 1 + 2*phases]
    regions = {'pulse_position': [], 'filter_position': []}
    for um, mm in zip(usf.instruments, m.instruments):
        if um.pulse_env is not None and mm.pulse_ptr:
            regions['pulse_position'].append(
                (mm.pulse_ptr, mm.pulse_ptr + 1 + 2 * len(um.pulse_env.phases)))
        if um.filter_env is not None and mm.filter_ptr:
            regions['filter_position'].append(
                (mm.filter_ptr, mm.filter_ptr + 1 + 2 * len(um.filter_env.phases)))
    for key, vals in seen.items():
        name = sig_of.get(key, (None,))[0]
        bad = [v for v in vals
               if name and not any(lo <= v <= hi for lo, hi in regions[name])]
        if bad:
            raise RuntimeError(
                f'unsupported:offtable_live_pos ({"+".join(over)} pool '
                f'overflow; {name} read at idx {key[1]} observed '
                f'{sorted(bad)} outside every captured program region)')
    out = []
    for um, mm in zip(usf.instruments, m.instruments):
        recs = []
        for off, note, lo, hi in um.offtable_freq:
            idx = (off + note) & 0xFF
            s = sig_of.get(('lo', idx))
            if s:
                lo = LiveSignal(*s)
            s = sig_of.get(('hi', idx))
            if s:
                hi = LiveSignal(*s)
            recs.append((off, note, lo, hi))
        out.append(dataclasses.replace(
            um, offtable_freq=recs,
            pulse_table_pos=(mm.pulse_ptr
                             if um.pulse_env is not None and mm.pulse_ptr
                             else None),
            filter_table_pos=(mm.filter_ptr
                              if um.filter_env is not None and mm.filter_ptr
                              else None)))
    return dataclasses.replace(usf, instruments=out)


def write_v5_usf(cfg: DMCV5Config, out_dir: str,
                 hvsc_root: str = 'hvsc85') -> str:
    m = extract(cfg, hvsc_root=hvsc_root)
    usf = model_to_usf(m, reach=_verify_window_frames(cfg, hvsc_root))
    # offtable_live_pos handling AT THE EXTRACT BOUNDARY (ledger C8 sixth
    # widening + C11 / backlog item 19, live-position form owner-approved
    # 2026-08-26): this member's off-table freq read lands on the LIVE
    # pulsepos/filterpos block — the read SONIFIES a table position, so the
    # honest representation is a NAMED live signal (`pulse_position(vN)` /
    # `filter_position()`) plus each instrument's ORIGINAL table start
    # (`pulse_table_pos`/`filter_table_pos`, the wave_table_pos siblings).
    # The composer serves the read from its OWN live cursor + the
    # (original - own) start delta: the walks advance in lockstep (same
    # phases), so the delta is constant per instrument.
    #
    # VALIDITY GATE, measured (C11: measure at the read): the delta model
    # holds only while the original's cursor is inside the CAPTURED program
    # region (past _PHASE_CAP truncation our cursor parks while the
    # original walks on). `measure_live_window_reads` observes every read
    # over the full verify window; every observed value must lie inside
    # some captured region of its table, else REFUSE. (2026-08-26 census:
    # all 4 carriers pass — incl. the two whose values are inconstant, the
    # very case no static byte could serve.)
    #
    # This lives HERE because its facts are known here and nowhere
    # downstream: the live-window hit + read sites are extract-side (player
    # state-block addresses), and would-the-pool-overflow comes from
    # from_usf's size mirror (self-checked against its real packer).
    if getattr(m, 'offtable_live_pos', False):
        from pipelines.dmc.v5.from_usf import defused_pool_overflow
        over = defused_pool_overflow(usf)
        if over:
            seen = measure_live_window_reads(cfg, m, hvsc_root)
            if seen is None:
                raise RuntimeError(
                    f'unsupported:offtable_live_pos ({"+".join(over)} pool '
                    f'overflow; no read-site map for this player)')
            usf = _emit_live_position_form(m, usf, seen, over)
    base = os.path.splitext(os.path.basename(cfg.sid_path))[0]
    out = os.path.join(out_dir, base + '.usf')
    write_file(usf, out)
    return out
