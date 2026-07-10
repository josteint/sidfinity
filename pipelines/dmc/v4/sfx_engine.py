"""dmc_sfx — extract + reference interpreter for the embedded SFX sub-player.

Some DMC compilations pack, alongside their DMC music players, a tiny (~257
byte) custom SFX sequencer (Canyon_Tank_Duel @ $3000, Empire_Strikes_Back @
$3D00). It is NOT DMC — its own note/instrument/waveform format. This module
decodes one such player at a forced base into a typed `SfxEngine` (the USF
musical content) and provides a pure-Python reference interpreter that
reproduces the exact per-play() SID write stream reading ONLY the SfxEngine
(proving the representation is complete). See pipelines/dmc/v4/RE_NOTES.md
section 'dmc_sfx' for the full engine model.

Scored by the CORE TENET: only the $D400-$D418 write stream matters.
"""

from __future__ import annotations

from src.usf.types import (SfxEngine, SfxInstrument, SfxSong, SfxVoiceInit)

# base-relative offsets of the player's tables (invariant across the known
# instances — the whole player relocates as a unit; see RE_NOTES.md).
_FILTER = 0x1D          # filter cutoff LFO table (8 bytes)
_FREQLO = 0x25          # 96-entry freq_lo tuning table
_FREQHI = 0x85          # 96-entry freq_hi tuning table
_STATE = 0x0C           # dur[3] pitch[3] incr[3] wavestep[3] instr[3]
_COUNTER = 0xF1         # play-counter SMC byte (LDX operand at play entry)
_SONG = 0x200           # song records (8 bytes: voice,dur,ws,incr,ad,sr,pwl,pwh)
_INSTR = 0x280          # instr records (8 bytes: ctrl[4], freqbase[4])
_WAVE = 0x300           # arp / pitch-program table
_SIDOFF = (0, 7, 14)    # per-voice SID register offset (V1/V2/V3)

# the off-table freq_hi read at fidx = (_COUNTER - _FREQHI) sonifies the LIVE
# play counter (state-as-data); everything else past the 96-entry table is a
# static byte the engine reads as an extended-tuning frequency.
_LIVE_FIDX = _COUNTER - _FREQHI      # = 0x6C = 108


def is_sfx_player(mem, base: int) -> bool:
    """True iff `base` holds the dmc_sfx player: the play-entry signature
    LDX #imm / LDA base+$1D,X / STA $D416 / LDA #$01 / STA $D415."""
    p = base + 0xF0                       # play entry (base+3 -> JMP here)
    play = mem[base + 4] | (mem[base + 5] << 8)   # base+3 = JMP play
    if play != p:
        return False
    return (mem[p] == 0xA2 and mem[p + 2] == 0xBD
            and (mem[p + 3] | (mem[p + 4] << 8)) == base + _FILTER
            and mem[p + 5] == 0x8D and (mem[p + 6] | (mem[p + 7] << 8)) == 0xD416
            and mem[p + 8] == 0xA9 and mem[p + 9] == 0x01
            and mem[p + 10] == 0x8D and (mem[p + 11] | (mem[p + 12] << 8)) == 0xD415)


def _reach(mem, base: int, n_songs: int):
    """Simulate every song to gate-off; return (max freq index, max wave index)
    actually read, so the captured tuning + wave tables cover exactly what the
    engine reads (the verify gate catches any shortfall)."""
    max_f = 95
    max_w = 15
    for song in range(n_songs):
        dur = [mem[base + _STATE + i] for i in range(3)]
        pitch = [mem[base + _STATE + 3 + i] for i in range(3)]
        incr = [mem[base + _STATE + 6 + i] for i in range(3)]
        ws = [mem[base + _STATE + 9 + i] for i in range(3)]
        X = song * 8
        v = mem[base + _SONG + X]
        dur[v] = mem[base + _SONG + X + 1]
        ws[v] = mem[base + _SONG + X + 2]
        incr[v] = mem[base + _SONG + X + 3]
        pitch[v] = 0
        instr = [mem[base + _STATE + 12 + i] for i in range(3)]
        instr[v] = X
        for _ in range(2048):
            if not any(dur):
                break
            for X2 in (2, 1, 0):
                if not dur[X2]:
                    continue
                if ws[X2] & 0x80:
                    pitch[X2] = (pitch[X2] + incr[X2]) & 0xFF
                else:
                    y = (ws[X2] | incr[X2]) & 0xFF
                    max_w = max(max_w, y)
                    pitch[X2] = mem[base + _WAVE + y]
                    ws[X2] = (y + 1) & 0x0F
                fb = mem[base + _INSTR + 4 + instr[X2]]   # rotation 0 lower bound
                for r in range(4):
                    fbr = mem[base + _INSTR + 4 + r + instr[X2]]
                    max_f = max(max_f, (fbr + pitch[X2]) & 0xFF)
                dur[X2] = (dur[X2] - 1) & 0xFF
    return max_f, max_w


def extract_sfx_engine(mem, base: int, n_songs: int = 8) -> SfxEngine:
    """Decode the dmc_sfx player at `base` into a typed SfxEngine."""
    if not is_sfx_player(mem, base):
        raise ValueError(f'no dmc_sfx player at {base:#06x}')
    max_f, max_w = _reach(mem, base, n_songs)
    freq_lo = tuple(mem[base + _FREQLO + i] for i in range(max_f + 1))
    freq_hi = tuple(mem[base + _FREQHI + i] for i in range(max_f + 1))
    wave = tuple(mem[base + _WAVE + i] for i in range(max_w + 1))
    filt = tuple(mem[base + _FILTER + i] for i in range(8))

    instruments = []
    songs = []
    for n in range(n_songs):
        s = base + _SONG + n * 8
        i = base + _INSTR + n * 8
        instruments.append(SfxInstrument(
            ctrl=tuple(mem[i + k] for k in range(4)),
            freqbase=tuple(mem[i + 4 + k] for k in range(4)),
            ad=mem[s + 4], sr=mem[s + 5], pw_lo=mem[s + 6], pw_hi=mem[s + 7]))
        songs.append(SfxSong(
            voice=mem[s], duration=mem[s + 1], wavestep=mem[s + 2],
            increment=mem[s + 3], instrument=n))

    vinit = []
    for v in range(3):
        ib = mem[base + _STATE + 12 + v]
        if ib % 8 or ib // 8 >= n_songs:
            raise ValueError(f'dmc_sfx leftover instr {ib:#x} not a song slot')
        vinit.append(SfxVoiceInit(
            duration=mem[base + _STATE + v], pitch=mem[base + _STATE + 3 + v],
            increment=mem[base + _STATE + 6 + v],
            wavestep=mem[base + _STATE + 9 + v], instrument=ib // 8))

    return SfxEngine(
        filter_lfo=filt, wave_table=wave, freq_lo=freq_lo, freq_hi=freq_hi,
        instruments=instruments, songs=songs, voice_init=tuple(vinit),
        init_counter=mem[base + _COUNTER],
        live_counter_fidx=_LIVE_FIDX if max_f >= _LIVE_FIDX else -1)


def simulate_sfx(e: SfxEngine, song_idx: int, nframes: int) -> list:
    """Reference interpreter — reproduce the per-play() write stream reading
    ONLY the SfxEngine. Returns a flat [(reg, val), ...] list. Proves the
    typed representation is complete (matches the ground-truth writelog)."""
    dur = [vi.duration for vi in e.voice_init]
    pitch = [vi.pitch for vi in e.voice_init]
    incr = [vi.increment for vi in e.voice_init]
    ws = [vi.wavestep for vi in e.voice_init]
    inst = [vi.instrument for vi in e.voice_init]     # 0..len(instruments)-1
    sg = e.songs[song_idx]
    dur[sg.voice] = sg.duration
    ws[sg.voice] = sg.wavestep
    incr[sg.voice] = sg.increment
    pitch[sg.voice] = 0
    inst[sg.voice] = sg.instrument
    pc = e.init_counter
    out = []

    def wave_at(y):
        return e.wave_table[y] if y < len(e.wave_table) else 0

    for _ in range(nframes):
        ex = pc
        out += [(0x16, e.filter_lfo[ex & 7]), (0x15, 0x01), (0x17, 0x23)]
        r = (ex + 1) & 3
        pc = (ex + 1) & 7
        for X in (2, 1, 0):
            if not dur[X]:
                continue
            out.append((0x18, 0x1F))
            off = _SIDOFF[X]
            if ws[X] & 0x80:
                pitch[X] = (pitch[X] + incr[X]) & 0xFF
            else:
                y = (ws[X] | incr[X]) & 0xFF
                pitch[X] = wave_at(y)
                ws[X] = (y + 1) & 0x0F
            ins = e.instruments[inst[X]]
            out += [(0x04 + off, ins.ctrl[r]),
                    (0x05 + off, ins.ad), (0x06 + off, ins.sr),
                    (0x02 + off, ins.pw_lo), (0x03 + off, ins.pw_hi)]
            fidx = (ins.freqbase[r] + pitch[X]) & 0xFF
            lo = e.freq_lo[fidx] if fidx < len(e.freq_lo) else 0
            if fidx == e.live_counter_fidx:
                hi = pc                              # LIVE play counter
            else:
                hi = e.freq_hi[fidx] if fidx < len(e.freq_hi) else 0
            out += [(0x00 + off, lo), (0x01 + off, hi)]
            dur[X] = (dur[X] - 1) & 0xFF
            if dur[X] == 0:
                out += [(0x04 + off, 0x08), (0x06 + off, 0x00), (0x05 + off, 0x00)]
    return out
