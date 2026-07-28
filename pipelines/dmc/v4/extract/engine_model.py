"""DMC V4 binary → semantic model.

Decodes the dominant DMC V4 player's song data (see
pipelines/dmc/v4/disassembly.s for the authoritative format reference)
into engine-neutral musical structures ready for USF emission.

Design notes (all grounded in the disassembly):

- Table addresses are read from the player's PACKER-PATCHED operands
  (dataflow), never from fixed offsets.

- Sector (pattern) decoding replicates the player's exact 5-stage
  dispatch order — including the ghost path where a `$7F` byte reached
  through dispatch (i.e. NOT via the post-event peek) reads as
  "instrument 31". A sector only ENDS at the `$7F` peek that follows a
  duration-consuming event (note / rest / switch / slide).

- Sticky state (duration reload, instrument, VOL override, transpose)
  crosses sector and even track-loop boundaries. Patterns are therefore
  PATH-RESOLVED: each track entry yields a pattern instance with every
  row stamped with its effective duration/instrument/vol, and instances
  dedup by content. Track loops are unrolled until the sticky state at
  the wrap point repeats (cycle detection) — the FC loop-pickup lesson.

- The soft-start toggle ($7C) is reset at every sector end by the
  player, so it never crosses sectors; rows carry it as `noretrig`.
"""
from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field, replace as _dc_replace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tools'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'tools', 'py65_lib'))

from pipelines.dmc.v4.config import DMCV4Config
from pipelines.dmc.engine_constants import VIBDEPTH

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


# ---------------------------------------------------------------------------
# Decoded structures
# ---------------------------------------------------------------------------

@dataclass
class DmcInstrument:
    """Semantic fields of an 11-byte V4 instrument record."""
    id: int
    ad: int
    sr: int
    pw_init_hi: int          # PW hi initial (byte2 lo nibble)
    pw_bound_a: int          # byte2 >> pulse-bound shift (canon 4 = hi nibble)
    pw_bound_b: int          # = bound_a EOR $0F
    pw_steps: list           # 6 effective per-phase step bytes
    pw_keep_running: bool    # flag $04
    filter_def: int          # byte6 lo nibble (meaningful iff filter_on)
    filter_on: bool          # flag $20
    filter_keep_running: bool  # flag $02
    vib_delay: int           # frames (byte7 hi nibble * 8)
    vib_width: int           # byte7 lo nibble
    vib_ramp: int            # byte8 (when not dual)
    dual: bool               # flag $40 — half-rate per-note slide
    slide_step: int          # byte8 & $7F (when dual)
    slide_dir: str           # 'up' (byte8 bit7 set) | 'down'
    gate_mode: str           # 'release_early' | 'hold' ($10) | 'open' ($08)
    gate_open: bool          # $10 AND $08 both set — independent editor
                             # flags; hold wins in the engine ($132D tests
                             # $10 first), but the raw flags byte is
                             # observable via the off-table fxf read
    drum: bool               # flag $01 — wave freq bytes are absolute
    noise_attack: bool       # flag $80 — cymbal
    wave_start: int          # byte9 (raw index into the shared wave table)
    wave_pool_pos: int | None = None  # table position of the program's first
                                      # step (== wave_start unless byte9 sits
                                      # on the own-end marker); set only when
                                      # DmcModel.wavepos_layout fires
    wave_ctrl: list = field(default_factory=list)   # sliced program
    wave_freq: list = field(default_factory=list)   # parallel
    wave_loop: int = 0
    # off-table arpeggio frequencies (the v5 `offtable_freq` form, ported to
    # v4): per (wave-program offset, played note) the explicit (lo, hi) the freq
    # read produces when `(note + offset) & $FF` runs past the 96-entry table.
    # idx = (offset + note) & $FF; entry = (offset, note, lo, hi). Replaces the
    # conservative `offtable_live` rejection for the STABLE-when-read reads.
    offtable_freq: list = field(default_factory=list)
    # The editor placed wave byte9 ON this program's own loop marker
    # ($90+n, loop 0): the engine chases it back n on the first read every
    # note-init, writing the shared $171F scratch (= n). Set only for members
    # whose off-table freq reads sonify $171F (the wjmp window); the composer
    # then re-asserts wjmp=n at note-init. See extract() + composer wchase.
    wave_start_on_marker: bool = False


@dataclass
class DmcRow:
    """One path-resolved pattern event."""
    note: int | None         # raw 0-95, or None for rest/switch rows
    duration: int            # ticks
    instr: int               # effective instrument (stamped)
    vol: int = 0             # sustain override (0 = instrument default)
    soft: bool = False       # no hard restart ($7C mode)
    gate_toggle: bool = False  # $7D SWITCH event
    glide_speed: int = 0     # 0 = no glide
    glide_to: int | None = None   # raw target note (mode 0)
    glide_slide: bool = False     # mode 1: slide current note to `note`
    # STATED-command flags: this editor row physically carries a duration /
    # instrument / volume command (or N soft-start toggles) in the sector
    # bytes — the composer's command PLACEMENT (arrangement, §8), incl. the
    # redundant re-statements that a value-change derivation cannot see.
    # Consumed by the sectpos shadow ($1729,x = per-byte sector position,
    # read off-table): per-row byte width = base(kind) + stated commands.
    dcmd: bool = False       # $80-$BF duration command on this row
    icmd: bool = False       # $60-$7B instrument command on this row
    vcmd: bool = False       # $Fx volume/sustain command on this row
    # RUN-ON row: the source stream ran into the next track fetch with NO $7F
    # end-marker after this row (a post-transpose one-row garbage sector, or
    # any unterminated tail) — the engine's sector position ($1729,x) is NOT
    # reset here and keeps accumulating into the next entry. Consumed by the
    # composer's sectpos shadow (per-entry base threading); USF flag 'runon'.
    runon: bool = False
    softcmd: int = 0         # count of $7C soft-start toggles on this row
    tempo: int | None = None  # speed reload set AT this row (the Doxx tempo
                             # mailbox: an instr command >= $10 on the third
                             # voice doubles as a tempo command — see the
                             # factory `v3_instr_tempo` probe). None = no
                             # tempo change; rendered as fx `tempo=N`.


@dataclass
class DmcSong:
    """One subtune, fully path-resolved."""
    id: int
    speed: int
    master_vol: int
    voices: list = field(default_factory=list)   # 3 × DmcVoice
    # Per-subtune idle priming (trichotomy §4.5 voice_state). None = the
    # model-level value serves every subtune, which is the case for every
    # single-player member (one player, one set of work-file leftovers). A
    # COMPILATION packs N players, each with its OWN uncleared leftovers, and
    # each subtune runs exactly one of them — so the priming becomes a
    # per-subtune fact and rides `MusicSubtune.init.voices` instead of the
    # file-level `init` block (same split the schema already documents for
    # speed_ctr_init: file-level for single engines, per-subtune for compound).
    idle_notes: tuple | None = None
    idle_masks: tuple | None = None
    durrel_init: tuple | None = None
    # Per-subtune $D417 routing shadow (trichotomy §4.2 SID-chip priming —
    # `init.sid.filter.res_routing`, already per-subtune in the schema). Same
    # rule as the voice_state priming above: None = the model-level value
    # serves every subtune. It is the SAME uncleared-leftover fact, so a
    # COMPILATION makes it per-subtune too — the merge used to keep only the
    # START player's shadow, which handed Pour_le_merite's sub 0 the other
    # player's $01 where its own player primes $02.
    d417_shadow: int | None = None
    # Per-subtune half-rate slide-clock phase (trichotomy §4.5, the
    # file-level `init.slide_phase`). Same per-player-fact split: each packed
    # player's $1019 leftover seeds ITS subtunes' dual-effect interleave
    # (Chwat: player 1 leftover 1, player 2 leftover 0 — the merge used to
    # hand every subtune the start player's phase, flipping player 2's
    # wavestep/slide alternation). None = the file-level value serves.
    dual_phase: int | None = None
    # Per-subtune composer-param overrides (MusicSubtune.params). Same
    # per-player-fact split as the priming above: a COMPILATION's packed
    # players can disagree on a factory-probed wedge knob (Super_Seven:
    # player 0 is family-2 `rest_effects='skip'`, player 1 canon 'run'),
    # and the merge used to keep only the START player's extra_params —
    # a one-frame modulator stall (or its absence) on every event boundary
    # of the other player's subtunes. None = file-level params serve.
    params: dict | None = None


@dataclass
class DmcVoice:
    patterns: list = field(default_factory=list)     # list[list[DmcRow]]
    entries: list = field(default_factory=list)      # indices into patterns
    transposes: list = field(default_factory=list)   # signed, per entry
    entry_offsets: list = field(default_factory=list)  # orig track byte offset
                                                     # of each entry's sector
                                                     # byte (walk-time ground
                                                     # truth for otrk_pad)
    loop_to: int | None = None
    stop: bool = False
    # Initial sticky-instrument seed the walk ran with: the engine's per-voice
    # current-instrument number ($1015,x) is a work-file LEFTOVER the canon
    # init never clears — a note reached before any $6x command note-inits
    # with it (same leftover family as idle_notes/durrel_init/slide_phase).
    # 0 = the pre-fix assumption (and the common case: most voices state an
    # instrument before their first note, so the seed is dead).
    instr_seed: int = 0


@dataclass
class DmcModel:
    instruments: dict = field(default_factory=dict)  # id -> DmcInstrument
    filter_defs: dict = field(default_factory=dict)  # def# -> dict
    songs: list = field(default_factory=list)        # list[DmcSong]
    freq_lo: list = field(default_factory=list)
    freq_hi: list = field(default_factory=list)
    vibdepth: list = field(default_factory=list)     # 96 bytes incl. overlap
    # off-table vibrato-depth reads (note > 95): {note: depth} — the value the
    # engine reads past the 96-entry vibdepth table (lands on static instr
    # records). The vibdepth analog of offtable_freq.
    offtable_vibdepth: dict = field(default_factory=dict)
    d417_shadow: int = 0
    dual_phase: int = 0              # $1019 leftover & 1 — initial phase
                                     # of the half-rate slide clock
    cia_period: int = 0              # CIA1 timer A latch (multispeed); 0=VBI
    play_repeat: int = 1             # INTERNAL multispeed: the play wrapper
                                     # JSRs the inner play N x per VBI with NO
                                     # PSID speed bit (vblank-dispatched). 1=once.
    family2: bool = False            # the V4-derived family-2 build
    extra_params: dict = field(default_factory=dict)  # factory-probed knobs
    offtable_canon: bool = True      # original state block at the canon offset
                                     # from the freq tables (extract geometry
                                     # probe). to_usf uses it to stamp per-read
                                     # `live` flags; NOT serialized as a bit.
    # Wave-table NORMAL FORM (live_signal_modulation_draft §4, C32 stated
    # notation): the sparse position-indexed cell dict to emit as the USF
    # `wave_table` block, with instruments as `wave_start` pointers. Set
    # ONLY when the shared resolver provably reproduces every resolved
    # program (idle walk included) from the stated cells — else None and
    # the member keeps the resolved-copy form (fallback wholesale).
    wave_table_norm: 'dict | None' = None
    wavepos_layout: bool = False     # an off-table freq read sonifies a live
                                     # wave position ($177A-$177C) AND every
                                     # wave program is a verbatim contiguous
                                     # slice of the orig table: carry each
                                     # instrument's editor wave-table position
                                     # so the composer packs its pool at the
                                     # orig positions (wavepos == orig $177A)
    idle_wave: tuple = ((), (), 0)   # wave walk from table index 0 (the
                                     # cleared-cache idle path): ctrl,
                                     # freq, loop
    idle_notes: tuple = (0, 0, 0)    # $1012-$1014 work-file leftovers
    idle_masks: tuple = (0, 0, 0)    # $100F-$1011 gate-mask leftovers
    idle_guards: tuple = (0, 0, 0)   # $1786-$1788 post-note-guard leftovers
    durrel_init: tuple = (0, 0, 0)   # $173E-$1740 duration-reload leftovers
                                     # (init never writes $173E; the leftover
                                     # is read via off-table freq idx 247-249
                                     # lo / 151-153 hi until the voice's first
                                     # event stores its row duration)
                                     # (uncleared until the voice's first
                                     # note-init; sonified by off-table reads)
    title: str = ''
    author: str = ''
    released: str = ''
    clock: str = 'PAL'               # PSID header clock flag (audio metadata)
    sid_model: int = 6581            # PSID header SID model — the write-log
                                     # verdict is BLIND to this; a 6581 build
                                     # of an 8580 tune sounds wrong (filters)
    n_subtunes: int = 1
    start_song: int = 1


# ---------------------------------------------------------------------------
# Binary loading
# ---------------------------------------------------------------------------

def _hdr_flags(sid_path: str) -> int:
    """PSID v2+ header flags word (0 for v1/RSID-without-flags)."""
    with open(sid_path, 'rb') as f:
        b = f.read(0x78)
    if len(b) < 0x78 or int.from_bytes(b[4:6], 'big') < 2:
        return 0
    return int.from_bytes(b[0x76:0x78], 'big')


def _hdr_clock(sid_path: str) -> str:
    return {0: 'unknown', 1: 'PAL', 2: 'NTSC', 3: 'both'}[
        (_hdr_flags(sid_path) >> 2) & 3]


def _hdr_sid_model(sid_path: str):
    # int 6581/8580, or the strings the USF psid block also admits —
    # lossless round-trip of the orig header flag
    return {0: 0, 1: 6581, 2: 8580, 3: 'both'}[
        (_hdr_flags(sid_path) >> 4) & 3]


def _load_image(sid_path: str):
    from seed_disassembly import parse_psid
    s = parse_psid(sid_path)
    mem = bytearray(0x10000)
    load = s['load']
    for i, b in enumerate(s['payload']):
        if load + i < 0x10000:
            mem[load + i] = b
    return mem, s


def _rd16(mem, addr):
    return mem[addr] | (mem[addr + 1] << 8)


_PLAYER_WIN = 0x1000


def _is_player_head(mem, a: int) -> bool:
    """The RELOCATION- and REASSEMBLY-invariant player-base signature (no load
    floor): a page-aligned address whose init (+0) and play (+3) vectors are
    both `JMP abs` into the player's own [base, base+$1000) window.

    THE one implementation — compilation.py re-exports it (it imports this
    module, so the definition lives here to avoid a cycle). A stale
    three-JMP copy lived here until 2026-07-23: round 90 generalised the
    compilation-side predicate to the two essential vectors (re-assembled
    players carry data at +6) but missed this duplicate, so
    `_postinit_window(stop_at_player=True)` never recognised a two-JMP head
    and ran to the 1M-step cap, returning None."""
    if a & 0xFF or not (0 < a and a + 6 < 0x10000):
        return False
    if mem[a] != 0x4C or mem[a + 3] != 0x4C:
        return False
    for off in (1, 4):
        tgt = mem[a + off] | (mem[a + off + 1] << 8)
        if not (a <= tgt < a + _PLAYER_WIN):
            return False
    return True


class _TaintMemory:
    """A py65 memory that flags reads of bytes only the EMULATOR ENVIRONMENT
    set — the power-on fill / psiddrv zero — never the file image or the
    running player.

    Such a byte is emulator-dependent: py65's fill can DIFFER from
    libsidplayfp's, and once a null-pointer / off-image player reads one the two
    emulators' whole playback states diverge — so a py65-EXTRACTED value that
    reads it is NOT ground truth (feedback_ground_truth, third failure mode; DMC
    Roots read $0031 = $00 under py65 where libsidplayfp had $87). This is the
    tripwire for that class: build it, `seed()` the environment (NOT tracked),
    then load the file image and run with tracking ON so the load + every CPU
    write mark bytes DEFINED. Read extracted values through `read_trusted()`;
    any address in `.tainted` afterward was environment-only in py65 and its
    value must be re-measured from siddump (`--memwatch-on-write` / `--writelog`)
    rather than trusted.

    Drop-in for `mpu.memory` (int/slice get/set, `len`); the plain `[]` path the
    CPU uses does NOT taint (only the explicit `read_trusted` value reads do)."""

    __slots__ = ('_m', '_defined', '_track', 'tainted')

    def __init__(self):
        self._m = bytearray(0x10000)
        self._defined = bytearray(0x10000)
        self._track = True
        self.tainted = set()

    def __len__(self):
        return 0x10000

    def __getitem__(self, k):
        return self._m[k]

    def __setitem__(self, k, v):
        self._m[k] = v
        if self._track:
            if isinstance(k, slice):
                for i in range(*k.indices(0x10000)):
                    self._defined[i] = 1
            else:
                self._defined[k] = 1

    def seed(self, data):
        """Install the emulator environment (64K power-on + psiddrv zero)
        WITHOUT marking any byte defined."""
        self._track = False
        try:
            self._m[:] = bytes(data)
        finally:
            self._track = True

    def read_trusted(self, addr):
        """Read `addr`, recording it in `.tainted` if only the environment (not
        the file image or a CPU write) ever set it — i.e. a value py65 cannot be
        trusted for; verify it against siddump."""
        if not self._defined[addr & 0xFFFF]:
            self.tainted.add(addr & 0xFFFF)
        return self._m[addr & 0xFFFF]


def _poweron_fill(memory):
    """libsidplayfp's power-on RAM pattern (SystemRAMBank::reset()): 16K
    blocks with alternating base byte $00/$FF, and offsets 2-5 of every
    8 bytes holding the flipped byte. Verified against a live memwatch
    ($4700 = $FF on the running emulator)."""
    byte = 0x00
    for j in range(0, 0x10000, 0x4000):
        memory[j:j + 0x4000] = [byte] * 0x4000
        byte ^= 0xFF
        for i in range(j + 0x02, j + 0x4000, 0x08):
            memory[i:i + 4] = [byte] * 4


def _postinit_window(s, lo: int, n: int, sub: 'int | None' = None,
                     stop_at_player: bool = False):
    """Bytes [lo, lo+n) AFTER running the member's init under py65 (subtune =
    start song, or `sub` when given). Some inits REWRITE static data the
    extract reads from the file image (e.g. the 'Ed' members' init stamps
    res/mode + initial cutoff over every filter def record) — the engine then
    reads the rewritten bytes, so the file-image capture is wrong. Returns
    None when py65 can't complete the init (C9 territory; caller keeps the
    file image).

    `sub` (0-based) selects WHICH subtune's init runs. A RELOCATING
    compilation wrapper (ledger C31 + C26) copies a different player into RAM
    per subtune, so the player at a given base only exists after the init of a
    subtune that selects it — the caller passes that subtune.

    `stop_at_player` stops the run the moment control reaches a player base
    (page-aligned three-JMP head) instead of running init to completion — the
    RELOCATED player's image AS LOADED, post-copy but before the player's own
    init has touched it. That is the exact analogue of the file image an
    ordinary in-image member is extracted from, and it matters: the leftover
    state the extract reads as PRIMING (the $D417 routing shadow, idle notes /
    gate masks) is precisely what a player's init overwrites, so running to
    completion silently substitutes post-init values for the leftovers
    (Pour_le_merite sub 0 then wrote $D417=$01 for the orig's $02).

    ⚠ DO NOT migrate this to siddump (attempted + reverted 2026-07-25,
    native-capture Phase 2): this function is NOT an observation of the real
    machine — it is an IDEALIZED SIMULATION (image + init's own writes +
    power-on pattern, WITHOUT the PSID driver), and the real machine cannot
    produce that counterfactual: psiddrv is always resident somewhere (it sat
    at $48xx on Super_Seven, so a libsidplayfp RAM snapshot fed DRIVER BYTES
    into the extraction's base memory and sub 1 went partial), its location
    differs between orig and rebuild, and real zp/vector/stack state rides
    along. The pipeline is calibrated on the idealized view; GENUINE
    environment reads are served separately by the C29 `--peek-post-init`
    machinery. py65 is the right tool here per feedback_ground_truth's own
    rule — it reads image-loaded / init-written bytes."""
    try:
        from py65.devices.mpu6502 import MPU
        mpu = MPU()
        # Seed the libsidplayfp power-on RAM pattern (SystemRAMBank::reset():
        # 16K blocks alternating base $00/$FF, offsets 2-5 of every 8 bytes
        # flipped) so a byte the image/init never writes reads what the ENGINE
        # reads — py65's zero-fill is a different machine. Bit hard on
        # Super_Seven: the wrapper's copy loop truncates the player's data at
        # $46FF, so secp_hi[9] at $4700 is power-on RAM = $FF at runtime
        # ($00 under zero-fill), sending sector 9 to $FFEF (KERNAL tail),
        # not $00EF (zeros).
        _poweron_fill(mpu.memory)
        # psiddrv::install zeroes $0000-$03FF before init on every PSID —
        # mirror it, or unwritten low RAM reads pattern where the engine
        # reads $00.
        for _a in range(0x400):
            mpu.memory[_a] = 0
        load = s['load']
        for i, b in enumerate(s['payload']):
            if load + i < 0x10000:
                mpu.memory[load + i] = b
        mpu.stPush(0x00)
        mpu.stPush(0x00)             # RTS sentinel -> PC = $0001
        mpu.pc = s['init']
        start_pc = mpu.pc
        mpu.a = (s.get('start', 1) or 1) - 1 if sub is None else sub
        for _ in range(1_000_000):
            if (mpu.pc == 0x0001 if not stop_at_player else
                    (mpu.pc != start_pc and _is_player_head(mpu.memory, mpu.pc))):
                return [mpu.memory[(lo + k) & 0xFFFF] for k in range(n)]
            mpu.step()
    except Exception:
        pass
    return None


# ---------------------------------------------------------------------------
# Sector (pattern) simulation
# ---------------------------------------------------------------------------

class _Sticky:
    """The state that crosses sector / loop boundaries.

    The duration reload defaults to 0, NOT 1: the note-load reads the duration
    reload from $173E,x, and the engine's INIT clears $1718-$179D (which spans
    $173E-$1740) to 0 — so a first note reached before any sector $80-$BF
    duration command plays for reload 0 (the counter DECs 0->$FF, i.e. a held
    256-tick note), not 1. The old default 1 gave such notes a too-short life,
    hitting the track terminator one play early and dropping a frame (e.g.
    Klepkomania's single-note decorative subtunes)."""
    __slots__ = ('dur', 'instr', 'vol')

    def __init__(self, dur=0, instr=0, vol=0):
        self.dur, self.instr, self.vol = dur, instr, vol

    def key(self):
        return (self.dur, self.instr, self.vol)

    def copy(self):
        return _Sticky(self.dur, self.instr, self.vol)


@dataclass
class _SecFmt:
    """Sector-command byte map. canon V4 and the family-2 V4-derived
    build share the engine but remap the command bytes (family 2 moves
    the terminator to $FF, drops VOL + soft-start, extends the
    instrument range to $7F). The terminator is only checked in the
    post-event PEEK — a terminator reached via DISPATCH is the ghost
    path (canon $7F → instr 31; family2 $FF → glide), preserved by
    letting it fall through to its range."""
    term: int = 0x7F                 # sector terminator (peeked)
    rest: int = 0x7E
    switch: int = 0x7D
    soft: 'int | None' = 0x7C        # soft-start toggle ($7C); None = none
    vol_min: 'int | None' = 0xF0     # VOL prefix range start; None = none
    instr_lo: int = 0x60
    glide_min: int = 0xC0
    dur_min: int = 0x80
    glide_dead: bool = False         # C19 glide_neutered wedge: the player's
                                     # glsp store is re-pointed into dead data,
                                     # so no glide/slide ever moves — decode
                                     # every $Cx/$Dx speed nibble as 0 (the
                                     # engine's glide-cancel semantics); byte
                                     # consumption and note/target unchanged


_SECFMT = {
    'v4': _SecFmt(),
    'family2': _SecFmt(term=0xFF, rest=0xFE, switch=0xFD, soft=None,
                       vol_min=None),
}


def _simulate_sector(mem, sec_addr: int, st: _Sticky,
                     fmt: _SecFmt = _SECFMT['v4'],
                     retrig: 'dict | None' = None,
                     transpose: int = 0) -> list:
    """Walk one sector with the player's dispatch; mutate `st`; return
    the row list. Parametric over `fmt` (the command byte map).

    The player's sector position is ONE byte (`LDY $1729,x / LDA ($f8),y`),
    so a sector with no terminator wraps mod 256 and plays forever — the
    voice never fetches another track entry (ledger C11: mirror the 8-bit
    wrap). Seen on header-overstated subtunes whose garbage track selects a
    sector number past the real pointer table (address $0000, zero fill).
    For that case the walk detects the wrapped cycle by (pos, sticky, soft,
    pending-prefix) state repeat and returns `('endless', lead, period)` —
    the rows before the first repeated state, and one full period. A
    terminated sector never revisits a loop-top state (pos is strictly
    increasing until the terminator), so the terminated path is untouched.

    `retrig` (the $7D-retrig wedge, cfg.switch_retrig / ledger C19): a
    mutable {'abs': .., 'cur': ..} shadow of the engine's stored glide-start
    note base+$744,x ('abs', absolute = transpose already folded in at store
    time) and curnote base+$12,x ('cur'). When set, a $7D byte is a FULL
    NOTE-INIT of 'abs' entering the note path at base+$1A6 — the transpose
    add is skipped — so it decodes as a plain note row with note byte
    `(abs - transpose) & $FF` (the composer's playback re-adds `transpose`,
    reproducing the same table index) and NO switch/gate toggle. Only glide
    rows write the register: mode 0 stores start+transpose, mode 1 copies
    curnote. None = canon semantics, byte-for-byte the old path."""
    rows = []
    pos = 0
    soft = False
    guard = 0
    seen = {}               # loop-top (pos, sticky, soft, pending) -> len(rows)
    # pending STATED-command flags: prefix bytes consumed since the last row
    # event belong to the NEXT row's fetch (each INCs $1729,x). Recorded as
    # byte FACTS of the sector (not change-vs-sticky), so the same sector
    # always yields the same flags regardless of entry context.
    p_d = p_i = p_v = False
    p_s = 0

    def _take():
        nonlocal p_d, p_i, p_v, p_s
        d, i, v, s = p_d, p_i, p_v, p_s
        p_d = p_i = p_v = False
        p_s = 0
        return {'dcmd': d, 'icmd': i, 'vcmd': v, 'softcmd': s}

    def rd(off):
        # 8-bit sectpos wrap (as the player, C11) + 16-bit address wrap: the
        # 6502's (zp),y crosses $FFFF into zeropage (a sector based in the
        # KERNAL tail — Super_Seven's truncated-copy $FFEF window).
        a = (sec_addr + (off & 0xFF)) & 0xFFFF
        # The sector pointer $F8/$F9 holds THIS sector's base during the
        # read — a SELF-REFERENTIAL window byte (C29). Its live value is
        # per-window, so no single mem[] byte can represent two overlapping
        # low windows; serve it here instead of poking mem.
        if a == 0x00F8:
            return sec_addr & 0xFF
        if a == 0x00F9:
            return (sec_addr >> 8) & 0xFF
        return mem[a]

    def peek_end():
        return rd(pos) == fmt.term

    while True:
        guard += 1
        if guard > 4096:
            # no terminator within bounds: the secp table / track points
            # at non-sector data (a corrupt or differently-laid-out
            # member). Refuse cleanly rather than crash.
            raise RuntimeError(
                f'unsupported:sector_decode no end at ${sec_addr:04X}')
        pos &= 0xFF
        key = (pos, st.key(), soft, p_d, p_i, p_v, p_s) + \
            ((retrig['abs'], retrig['cur']) if retrig is not None else ())
        if key in seen:
            i = seen[key]
            return ('endless', rows[:i], rows[i:])
        seen[key] = len(rows)
        b = rd(pos)
        # VOL prefix (canon $F0+; family 2 has none)
        if fmt.vol_min is not None and b >= fmt.vol_min:
            st.vol = b & 0x0F
            p_v = True
            pos += 1
            continue
        # soft-start toggle (canon $7C; family 2 has none)
        if fmt.soft is not None and b == fmt.soft:
            soft = not soft
            p_s += 1
            pos += 1
            continue
        # rest / switch (exact bytes, checked before the glide range so
        # family 2's $FE/$FD are caught above $C0)
        if b == fmt.rest:
            rows.append(DmcRow(note=None, duration=st.dur, instr=st.instr,
                               vol=st.vol, **_take()))
            pos += 1
            if peek_end():
                return rows
            continue
        if b == fmt.switch:
            if retrig is not None:
                # $7D-retrig wedge: replay the stored glide-start note as a
                # full note-init (transpose add skipped — subtract it here so
                # playback's re-add lands the same index). A shadow value the
                # note byte space can't express is a refusal, not a guess.
                nb = (retrig['abs'] - transpose) & 0xFF
                if nb >= fmt.instr_lo:
                    raise RuntimeError(
                        'unsupported:switch_retrig note $%02X' % nb)
                retrig['cur'] = retrig['abs']
                rows.append(DmcRow(note=nb, duration=st.dur, instr=st.instr,
                                   vol=st.vol, soft=soft, **_take()))
                pos += 1
                if peek_end():
                    return rows
                continue
            rows.append(DmcRow(note=None, duration=st.dur, instr=st.instr,
                               vol=st.vol, gate_toggle=True, **_take()))
            pos += 1
            if peek_end():
                return rows
            continue
        # glide / slide
        if b >= fmt.glide_min:
            speed = 0 if fmt.glide_dead else (b & 0x0F)
            if b & 0x10:             # mode 1: slide current note to target
                target = rd(pos + 1)
                pos += 2
                if retrig is not None:      # base+$744,x <- curnote ($1168)
                    retrig['abs'] = retrig['cur']
                rows.append(DmcRow(note=target, duration=st.dur,
                                   instr=st.instr, vol=st.vol,
                                   glide_speed=speed, glide_slide=True,
                                   **_take()))
                if peek_end():
                    return rows
                continue
            else:                    # mode 0: play A, glide to B
                a = rd(pos + 1)
                t = rd(pos + 2)
                pos += 3
                if retrig is not None:      # base+$744,x <- A+transp ($1145)
                    retrig['abs'] = retrig['cur'] = (a + transpose) & 0xFF
                rows.append(DmcRow(note=a, duration=st.dur, instr=st.instr,
                                   vol=st.vol, soft=soft,
                                   glide_speed=speed, glide_to=t,
                                   **_take()))
                if peek_end():
                    return rows
                continue
        # duration prefix
        if b >= fmt.dur_min:
            st.dur = b & 0x3F
            p_d = True
            pos += 1
            continue
        # instrument prefix (a dispatched terminator falls here for
        # canon = instr 31, the ghost path) / note
        if b >= fmt.instr_lo:
            st.instr = b & 0x1F
            p_i = True
            pos += 1
            continue
        # note
        if retrig is not None:              # curnote <- b+transp ($11A6)
            retrig['cur'] = (b + transpose) & 0xFF
        rows.append(DmcRow(note=b, duration=st.dur, instr=st.instr,
                           vol=st.vol, soft=soft, **_take()))
        pos += 1
        if peek_end():
            return rows


def _glide_poke_overlay(mem, rec, secp_lo: int, secp_hi: int,
                        fmt: _SecFmt, target: int) -> dict:
    """glide_neutered wedge (C19), second effect: the re-pointed speed store
    is `STA target,X` and `target` can sit INSIDE THE SONG DATA — every
    glide/slide command voice X executes pokes its speed nibble over the
    byte at target+X, i.e. runtime-generated musical content (Ice_on_Fire:
    V1's $C4 rows poke $04 over sector 20's pos-37 note byte; V3 later
    audibly plays note 4 there). When a voice uses exactly ONE speed nibble
    the effective byte is static — return {addr: value} so the walk reads
    what the engine reads. A voice with no glides pokes nothing; a
    multi-speed voice has no static effective byte, so its slot is left at
    the file value (the verify verdict judges). Byte-POSITION scan only —
    consumption widths match _simulate_sector's dispatch and need no sticky
    state."""
    pokes = {}
    for vi in range(3):
        tp = _rd16(mem, rec + vi * 2)
        secs = set()
        for i in range(256):
            b = mem[(tp + i) & 0xFFFF]
            if b in (0xFE, 0xFF):
                break
            if b < 0x80:
                secs.add(b)
        speeds = set()
        for sn in secs:
            base = mem[(secp_lo + sn) & 0xFFFF] | \
                (mem[(secp_hi + sn) & 0xFFFF] << 8)
            pos = 0
            for _ in range(300):
                b = mem[(base + (pos & 0xFF)) & 0xFFFF]
                if b == fmt.term:
                    break
                if fmt.vol_min is not None and b >= fmt.vol_min:
                    pos += 1
                    continue
                if b in (fmt.rest, fmt.switch) or \
                        (fmt.soft is not None and b == fmt.soft):
                    pos += 1
                    continue
                if b >= fmt.glide_min:
                    speeds.add(b & 0x0F)
                    pos += 2 if (b & 0x10) else 3
                    continue
                pos += 1
        if len(speeds) == 1:
            pokes[(target + vi) & 0xFFFF] = speeds.pop()
    return pokes


def _walk_track(mem, track_addr: int, secp_lo: int, secp_hi: int,
                loop_target: bool = False,
                loop_reset_pos: int | None = None,
                fmt: _SecFmt = _SECFMT['v4'],
                instr_seed: int = 0,
                switch_retrig: bool = False,
                loop_note_inject: bool = False) -> DmcVoice:
    """Walk one voice's track (orderlist), path-resolving every sector
    instance. Unrolls $FF loops until (wrap position, sticky state)
    repeats. `loop_target`: the JSR-$1042 player variant reads the byte
    after $FF as the loop position (canonical loops to 0).
    `loop_reset_pos`: the RESET-ALL-to-N SYNC hook (dataflow-probed, ledger
    C13) writes a fixed position to all three voices' track pos at $FF — the
    $FF loops to that fixed position (overrides both `loop_target` and the
    loop-to-0 default). Round-53 handled N==0 via loop_target=False; N>0 lands
    here (Action_G loops to pos 5). A DISTINCT loop position per voice is
    passed here as the per-voice scalar (round-63: Attacker V1/V2/V3 = 3/30/3);
    the caller (extract) indexes the config tuple before this call.

    The engine's track position is ONE byte (`LDY $1726,x` / `INC $1726,x`),
    so a track with no $FF/$FE terminator wraps mod 256 in hardware and the
    walk becomes a 256-byte loop (ledger C11: mirror the 8-bit index wrap in
    the extractor). Seen on header-overstated subtunes (Bayliss: PSID says 6
    songs, the tune table has 1 real record; subtunes 1-5 point at zero-fill
    and march sector 0 forever). The wrap is a NO-OP for every track that
    terminates before pos 256 — a real track walking past 255 unwrapped
    could never have verified — and the mod-256 cycle detection engages only
    after an actual wrap, so terminated tracks take the exact old path."""
    v = DmcVoice()
    pat_key_to_id = {}
    st = _Sticky(instr=instr_seed)
    v.instr_seed = instr_seed
    # $7D-retrig wedge shadow (cfg.switch_retrig, ledger C19). Seed 0/0: the
    # canon init clears the whole base+$718..$79D state block (glide-start
    # base+$744,x included) and the note-init cache to 0.
    retrig = {'abs': 0, 'cur': 0} if switch_retrig else None
    _rkey = (lambda: (retrig['abs'], retrig['cur'])) if switch_retrig \
        else (lambda: ())
    transpose = 0
    pos = 0
    wrap_states = {}        # (tgt, sticky, pending) at wrap -> entry index
    mod_states = {}         # (pos, sticky, transpose) after a mod-256 wrap
    wrapped = False
    pending_off = 0         # sector position INHERITED across a $FF loop:
                            # the $7F end handler zeros $1729,x but the $FF
                            # LOOP handler does NOT — a loop taken mid-sector
                            # (the post-transpose $FF quirk below) resumes
                            # the target sector at the leftover position.
    guard = 0
    while True:
        guard += 1
        if guard > 8192:
            raise RuntimeError(f'track at ${track_addr:04X} never settles')
        if pos > 0xFF:                 # 8-bit otrk: wrap like the hardware
            pos &= 0xFF
            wrapped = True
        if wrapped:
            key = (pos, st.key(), transpose) + _rkey()
            if key in mod_states:
                v.loop_to = mod_states[key]
                return v
            mod_states[key] = len(v.entries)
        b = mem[(track_addr + pos) & 0xFFFF]
        if b == 0xFE:
            v.stop = True
            return v
        if b == 0xFF:
            if loop_note_inject:
                # $FF text-fallthrough note-inject (cfg.loop_note_inject, a
                # C13 third form — see config.py): the wrap plays ONE
                # spurious note-0 row (sticky dur/instr, CURRENT transpose)
                # and INCs sectpos before resuming at track position 0. The
                # walk materialises the row as a one-row pattern entry;
                # the wrap key carries transpose (it pitches the fake row)
                # so unrolling converges on the right entry.
                key = ('inject', st.key(), pending_off, transpose) + _rkey()
                if key in wrap_states:
                    v.loop_to = wrap_states[key]
                    return v
                wrap_states[key] = len(v.entries)
                r0 = DmcRow(note=0, duration=st.dur, instr=st.instr,
                            vol=st.vol)
                pkey = (('inject', r0.note, r0.duration, r0.instr, r0.vol),)
                pid = pat_key_to_id.get(pkey)
                if pid is None:
                    pid = len(v.patterns)
                    v.patterns.append([r0])
                    pat_key_to_id[pkey] = pid
                v.entry_offsets.append(pos)
                v.entries.append(pid)
                v.transposes.append(transpose)
                pos = 0
                pending_off += 1        # the note path's INC $1729,x
                continue
            if loop_reset_pos is not None:
                tgt = loop_reset_pos    # reset-all-to-N SYNC hook (ledger C13)
            else:
                tgt = mem[(track_addr + ((pos + 1) & 0xFF)) & 0xFFFF] if loop_target else 0
            key = (tgt, st.key(), pending_off) + _rkey()
            if key in wrap_states:
                v.loop_to = wrap_states[key]
                return v
            wrap_states[key] = len(v.entries)
            pos = tgt
            continue
        if b >= 0x80:
            # mirror the 6502: SEC SBC #$A0; on borrow EOR #$1F, ADC #$01
            if b >= 0xA0:
                transpose = b - 0xA0
            else:
                t8 = ((((b - 0xA0) & 0xFF) ^ 0x1F) + 1) & 0xFF
                transpose = t8 - 256 if t8 >= 128 else t8
            pos += 1
            if pos > 0xFF:
                pos &= 0xFF
                wrapped = True
            b = mem[(track_addr + pos) & 0xFFFF]
            if b >= 0x80:
                # THE ENGINE DOES NOT RE-DISPATCH the post-transpose byte in
                # the fetch that consumed the transpose: `INY / LDA ($f8),y /
                # TAY` takes it as a SECTOR NUMBER unconditionally ($10FE-
                # $1101), so ANY >= $80 byte after a transpose plays ONE ROW
                # of its (usually garbage) sector; the NEXT row-fetch re-reads
                # this position as a TRACK byte and the byte MUTATES ROLES:
                #   $FF -> loop (Rock_Tec_Tec `a0 ff`: secp[$FF] = $0000 live
                #        zp outro; Creo/Dance aim secp[$FF] at a real phrase),
                #   $FE -> stop,
                #   $80-$FD -> ANOTHER TRANSPOSE (Memomania `$F3 $A5 $BA $D0
                #        $03`: each garbage byte plays one row of its sector
                #        — secp[$A5]=$0000 port/zp, secp[$BA]=$FFFF wrap,
                #        secp[$D0]=$00FF stack-page — then becomes tr +5/+26/
                #        +48, finally landing the REAL sector #$03 at tr $30;
                #        proven by the live pc-watch sector-ptr run-length
                #        [$C2E2×76, $C8D0×3, $C8C8×7, $0000, $FFFF, $00FF,
                #        $C37C×73, $0000×183] + the otrk/transp memwatch).
                # The row's consumed bytes accumulate in the persistent sector
                # position ($1729 is zeroed ONLY by $7F, never by loop/select),
                # so chained one-row sectors each start where the previous
                # left off — and the engine's post-row $7F peek (sub_11E6) can
                # advance the track past the byte before it ever re-dispatches.
                ga = ((mem[(secp_lo + b) & 0xFFFF] |
                       (mem[(secp_hi + b) & 0xFFFF] << 8))
                      + pending_off) & 0xFFFF
                probe = _simulate_sector(
                    mem, ga, st.copy(), fmt,
                    retrig=dict(retrig) if retrig is not None else None,
                    transpose=transpose)
                if isinstance(probe, tuple) and probe[0] == 'endless':
                    # A garbage pseudo-sector has no $7F terminator, so the
                    # simulation reports 'endless' — but the engine only ever
                    # plays ROW 0 before the next fetch re-dispatches the
                    # track byte, so the first simulated row is all that
                    # matters.
                    _rows = (probe[1] or []) + probe[2]
                    probe = _rows[:1]
                if isinstance(probe, list) and probe:
                    r0 = probe[0]
                    consumed = (3 if r0.glide_to is not None else
                                2 if r0.glide_slide else 1)
                    consumed += (int(r0.dcmd) + int(r0.icmd) + int(r0.vcmd)
                                 + r0.softcmd)
                    if r0.dcmd:
                        st.dur = r0.duration
                    if r0.icmd:
                        st.instr = r0.instr
                    if r0.vcmd:
                        st.vol = r0.vol
                    if retrig is not None:
                        # only r0 was consumed — apply ITS shadow effect alone
                        # (the simulate copy above may have walked further)
                        if r0.glide_to is not None:
                            retrig['abs'] = retrig['cur'] = \
                                (r0.note + transpose) & 0xFF
                        elif r0.glide_slide:
                            retrig['abs'] = retrig['cur']
                        elif r0.note is not None:
                            retrig['cur'] = (r0.note + transpose) & 0xFF
                    # sub_11E6 end-of-sector peek: after the row, a $7F at the
                    # new sector position advances the track NOW (pos++ +
                    # sectpos reset) — the byte then never re-dispatches. A
                    # non-$7F peek = a RUN-ON row: sectpos keeps accumulating
                    # (pending_off) into the next entry, and the composer's
                    # sectpos shadow must mirror that (the 'runon' USF flag).
                    peek = ((mem[(secp_lo + b) & 0xFFFF] |
                             (mem[(secp_hi + b) & 0xFFFF] << 8))
                            + pending_off + consumed) & 0xFFFF
                    r0.runon = mem[peek] != 0x7F
                    key = tuple((r.note, r.duration, r.instr, r.vol, r.soft,
                                 r.gate_toggle, r.glide_speed, r.glide_to,
                                 r.glide_slide, r.dcmd, r.icmd, r.vcmd,
                                 r.softcmd, r.runon) for r in [r0])
                    pid = pat_key_to_id.get(key)
                    if pid is None:
                        pid = len(v.patterns)
                        v.patterns.append([r0])
                        pat_key_to_id[key] = pid
                    v.entry_offsets.append(pos)
                    v.entries.append(pid)
                    v.transposes.append(transpose)
                    pending_off += consumed
                    if not r0.runon:
                        pending_off = 0
                        pos += 1
                        if pos > 0xFF:
                            pos &= 0xFF
                            wrapped = True
                # (unsimulatable pseudo-sector: fall through, the next
                # iteration's dispatch handles the byte as before — old
                # behavior)
                continue
        sec = b
        v.entry_offsets.append(pos)
        sec_addr = (mem[(secp_lo + sec) & 0xFFFF] |
                    (mem[(secp_hi + sec) & 0xFFFF] << 8)) + pending_off
        pending_off = 0
        rows = _simulate_sector(mem, sec_addr, st, fmt,
                                retrig=retrig, transpose=transpose)
        if isinstance(rows, tuple) and rows[0] == 'endless':
            # unterminated sector (8-bit sectpos wrap): the voice never
            # leaves it — encode lead rows (once) + one period, self-loop.
            _, lead, period = rows
            for chunk in ([lead] if lead else []) + [period]:
                v.patterns.append(chunk)
                v.entries.append(len(v.patterns) - 1)
                v.transposes.append(transpose)
            v.loop_to = len(v.entries) - 1
            return v
        key = tuple((r.note, r.duration, r.instr, r.vol, r.soft,
                     r.gate_toggle, r.glide_speed, r.glide_to,
                     r.glide_slide, r.dcmd, r.icmd, r.vcmd, r.softcmd)
                    for r in rows)
        pid = pat_key_to_id.get(key)
        if pid is None:
            pid = len(v.patterns)
            v.patterns.append(rows)
            pat_key_to_id[key] = pid
        v.entries.append(pid)
        v.transposes.append(transpose)
        pos += 1


def _seed_consumed(v: DmcVoice) -> bool:
    """Does this walked voice note-init BEFORE any $6x instrument command?

    If yes, the engine's first note reads the per-voice current-instrument
    LEFTOVER at $1015,x (canon init never clears it) — the walk must be
    re-run seeded with it. Scan rows in play order (pass-0 entry order):
    the first icmd row kills the seed; a note/glide row before one consumes
    it. Rest/switch rows neither read nor state the instrument."""
    for pi in v.entries:
        for r in v.patterns[pi]:
            if r.icmd:
                return False
            if r.note is not None:
                return True
    return False


def _offimage_sectors(mem, secp_lo: int, secp_hi: int, tunetab: int,
                      n_sub: int, load: int, loop_target: bool,
                      forced: int | None = None) -> list:
    """Base addresses of PLAYED sectors whose 256-byte read window leaves the
    RAM the image/init defines — the engine then sonifies ENVIRONMENT bytes:

    - base BELOW the load address (the C29 '$0000' class: a $FF loop into a
      garbage sector number → live zeropage as note data — 6510 port $2F/$37
      at offset 0/1, then static zp);
    - window overlapping banked-in ROM ($A000-$BFFF / $E000-$FFFF under the
      PSID default $01=$37) or WRAPPING past $FFFF into zeropage — the
      truncated-copy class (Super_Seven: the wrapper copies the player's data
      only to $46FF, secp_hi[9] reads power-on RAM $FF → sector 9 at $FFEF =
      KERNAL tail bytes + zp).

    The file image / py65 view is wrong there, so the extract overlays what
    the engine reads (runtime zp capture + ROM bytes). Walks every track
    (mirrors _walk_track, $FF followed once); an all-in-image member returns
    [] (byte-identical build)."""
    out = set()
    for sub in range(n_sub):
        rec = tunetab + (sub if forced is None else forced) * 8
        for vi in range(3):
            tp = _rd16(mem, rec + vi * 2)
            pos = 0
            guard = 0
            seen_loop = set()
            while guard < 1024:
                guard += 1
                pos &= 0xFF
                b = mem[(tp + pos) & 0xFFFF]
                if b == 0xFE:
                    break
                if b == 0xFF:
                    tgt = mem[(tp + ((pos + 1) & 0xFF)) & 0xFFFF] if loop_target \
                        else 0
                    if tgt in seen_loop:
                        break
                    seen_loop.add(tgt)
                    pos = tgt
                    continue
                if b >= 0x80:              # transpose command
                    # The transpose handler ($10FE-$1101) takes the NEXT byte
                    # as a sector number UNCONDITIONALLY (INY / LDA($f8),y /
                    # TAY — no re-dispatch), EVEN when it is itself >= $80
                    # (Memomania: `$F3 $A5` plays one row of sector $A5).
                    # _walk_track mirrors this (one row, then the byte
                    # re-dispatches by track rules on the next invocation:
                    # $FF loop / $FE stop / $80-$FD another transpose), so
                    # this gate must record the sector's window too — else a
                    # post-transpose off-image sector is never overlaid and
                    # _walk_track reads image zeros. pos += 1 only: the loop
                    # then re-dispatches the byte exactly like the engine
                    # (a < $80 byte re-records its window — set-deduped).
                    nb = mem[(tp + ((pos + 1) & 0xFF)) & 0xFFFF]
                    sec_addr = mem[(secp_lo + nb) & 0xFFFF] | \
                        (mem[(secp_hi + nb) & 0xFFFF] << 8)
                    if (sec_addr < load or sec_addr + 0xFF > 0xFFFF
                            or (0xA000 <= sec_addr + 0xFF
                                and sec_addr <= 0xBFFF)
                            or sec_addr + 0xFF >= 0xE000):
                        out.add(sec_addr)
                    pos += 1
                    continue
                sec_addr = mem[(secp_lo + b) & 0xFFFF] | \
                    (mem[(secp_hi + b) & 0xFFFF] << 8)
                if (sec_addr < load or sec_addr + 0xFF > 0xFFFF
                        or (0xA000 <= sec_addr + 0xFF and sec_addr <= 0xBFFF)
                        or sec_addr + 0xFF >= 0xE000):
                    out.add(sec_addr)
                pos += 1
    return sorted(out)


def _undefined_secp_reads(mem, secp_lo: int, secp_hi: int, tunetab: int,
                          n_sub: int, load: int, img_end: int,
                          loop_target: bool, forced: int | None = None) -> list:
    """Sector-POINTER table reads (`secp_lo/hi + sector#`) that land OUTSIDE
    the loaded image — a track byte can select a sector number past the
    pointer tables, pushing the pointer fetch itself off the image end. The
    engine reads the emulator ENVIRONMENT there (power-on RAM pattern /
    relocated psiddrv), so the image's zero MISLOCATES the sector base
    entirely (C29 3rd occurrence, Trailways_A: track byte $11 indexes 10-entry
    tables; secp_hi[$11] sits past EOF and reads power-on $FF -> the sector is
    at $FFCA = KERNAL tail, not $00CA). These bytes must be served the CPU-eye
    value BEFORE _offimage_sectors resolves sector windows. Mirrors the
    _offimage_sectors track walk."""
    out = set()
    for sub in range(n_sub):
        rec = tunetab + (sub if forced is None else forced) * 8
        for vi in range(3):
            tp = _rd16(mem, rec + vi * 2)
            pos = 0
            guard = 0
            seen_loop = set()
            while guard < 1024:
                guard += 1
                pos &= 0xFF
                b = mem[(tp + pos) & 0xFFFF]
                if b == 0xFE:
                    break
                if b == 0xFF:
                    tgt = mem[(tp + ((pos + 1) & 0xFF)) & 0xFFFF] if loop_target \
                        else 0
                    if tgt in seen_loop:
                        break
                    seen_loop.add(tgt)
                    pos = tgt
                    continue
                if b >= 0x80:              # transpose command
                    # The next byte is a sector number UNCONDITIONALLY (orig
                    # $10FE-$1101; mirrors _offimage_sectors / _walk_track) —
                    # its POINTER fetch can leave the image whatever the
                    # byte's value. pos += 1 only: the loop then re-dispatches
                    # the byte exactly like the engine (loop / stop / another
                    # transpose / plain sector re-select).
                    nb = mem[(tp + ((pos + 1) & 0xFF)) & 0xFFFF]
                    for a in ((secp_lo + nb) & 0xFFFF,
                              (secp_hi + nb) & 0xFFFF):
                        if not (load <= a < img_end):
                            out.add(a)
                    pos += 1
                    continue
                for a in ((secp_lo + b) & 0xFFFF, (secp_hi + b) & 0xFFFF):
                    if not (load <= a < img_end):
                        out.add(a)
                pos += 1
    return sorted(out)


def _offimage_track_ptrs(mem, tunetab: int, n_sub: int,
                         forced: int | None = None) -> list:
    """Track (orderlist) POINTERS from the tune table whose 256-byte read
    window overlaps BANKED-IN ROM — the engine reads the ORDERLIST ITSELF from
    static ROM, so the file-image zero-fill mis-decodes the whole voice
    (Memomania sub 3: V1 ptr $F256 = KERNAL ROM, `01 F7 20 ...` -> sector 1 +
    transpose walk; the zero-fill decodes sector 0 forever). The CPU-eye peek
    reproduces ROM byte-for-byte.

    STATIC ROM ONLY, deliberately: a pointer into the ROM regions ($A000-$BFFF
    BASIC, $E000-$FFFF KERNAL under the PSID default $01=$37) is reproducible;
    a below-load / zeropage pointer reads DYNAMIC RAM the stability filter
    can only serve as 0 (= the old zero-fill), so overlaying it can only move
    a divergence around, not fix it (it slightly worsened Flash/Kan-Kan when
    the gate included < load). C29's static-vs-dynamic boundary.

    Regression-safe by construction: a FULL member has every track pointer IN
    image (else its orderlist read the zero-fill and it was already non-FULL),
    so this returns [] for it and the build stays byte-identical. The 8-bit
    track position bounds the window to [tp, tp+$FF]."""
    out = set()
    for sub in range(n_sub):
        rec = tunetab + (sub if forced is None else forced) * 8
        for vi in range(3):
            tp = _rd16(mem, rec + vi * 2)
            if ((0xA000 <= tp + 0xFF and tp <= 0xBFFF)
                    or tp + 0xFF >= 0xE000):
                out.add(tp)
    return sorted(out)


def _psid_play_iomap(play_addr: int) -> int:
    """The 6510 port value psiddrv sets BEFORE each play() call — the bank
    config the ENGINE's environment reads see at play time (libsidplayfp
    psiddrv iomap(), keyed on the play address): a player under BASIC ROM
    ($A000+) runs with BASIC banked OUT, so a $0001 read sonifies $36, not
    the idle-time $37 that `--peek-post-init` snapshots (Memomania at $B800:
    the $0000-sector row at offset 1 plays note $36, not $37 — the peek's
    value decoded one semitone high). Deterministic per member; $37 for the
    common below-$A000 player, so every prior C29 carrier is unchanged."""
    if play_addr < 0xA000:
        return 0x37          # BASIC + KERNAL banked in
    if play_addr < 0xD000:
        return 0x36          # KERNAL only
    if play_addr < 0xE000:
        return 0x34          # no ROMs
    return 0x35              # IO only


def _overlay_offimage_windows(mem, path: str, bases, post_sub, s,
                              data_post_init: bool) -> None:
    """Overlay CPU-eye bytes (siddump --peek-post-init = libsidplayfp ground
    truth) over the 256-byte read windows at `bases`, touching ONLY UNDEFINED
    bytes (C29). Shared by the off-image SECTOR overlay and the out-of-image
    TRACK-POINTER pre-pass — both read the environment (banked-in ROM incl.
    psiddrv's patched vectors, the 6510 port, env zeropage, power-on RAM).

    Defined = image span ∪ bytes the (wrapper) init changed vs the same seed;
    a garbage window can overlap real player data and the peek is a full
    init+play snapshot, so writing over defined bytes clobbers the landing
    view (Pour_le_merite / Abyssal_Karma). Per-byte source (C29 boundary,
    static env vs dynamic residue): the port + banked ROM are STATIC -> the
    peek value is truth; a RAM byte gets the peek snapshot only if CONSTANT
    during play (memwatch stability), else 0 (the verdict-proven default;
    without the filter a stack-page window wrote a live snapshot where 0 was
    right — Remix_1995)."""
    if not bases:
        return
    wranges = []
    for base in bases:
        if base + 0xFF > 0xFFFF:                 # 16-bit pointer wrap
            wranges.append((base, 0xFFFF))
            wranges.append((0x0000, (base + 0xFF) & 0xFFFF))
        else:
            wranges.append((base, base + 0xFF))
    ref = bytearray(0x10000)
    if data_post_init or post_sub is not None:
        _poweron_fill(ref)
        for _a in range(0x400):
            ref[_a] = 0
    _ld = s['load']
    for _i, _b in enumerate(s['payload']):
        if _ld + _i < 0x10000:
            ref[_ld + _i] = _b
    _imgspan = range(_ld, min(0x10000, _ld + len(s['payload'])))
    _rom = ((0xA000, 0xBFFF), (0xE000, 0xFFFF))
    peek = _cpu_peek(path, wranges, subtune=post_sub)
    _ram = [a for a in peek if a >= 2
            and not any(lo <= a <= hi for lo, hi in _rom)]
    stable = _postinit_values(path, _ram, subtune=post_sub)
    for a, v in peek.items():
        if a in _imgspan or mem[a] != ref[a]:
            continue                     # defined — never clobber
        if a == 1:
            # 6510 port: serve the PLAY-TIME bank value (psiddrv sets $01 =
            # iomap(play) before each play call), not the peek's idle-time
            # snapshot — they differ for players above $A000.
            mem[a] = _psid_play_iomap(s.get('play', 0) or 0)
        elif a < 2 or any(lo <= a <= hi for lo, hi in _rom):
            mem[a] = v
        else:
            mem[a] = stable.get(a, 0)


# ---------------------------------------------------------------------------
# Instruments / wave / filter
# ---------------------------------------------------------------------------

def _signed8(b):
    return b - 256 if b >= 128 else b


def _slice_wave(ctrl_tab: list, freq_tab: list, start: int, n_inbound=None):
    """Follow the wave table from `start` to its first jump-back byte
    (>= $90); return (ctrl, freq, loop) with the cyclic region
    normalized into the slice (see disassembly: >= $90 jumps back
    (val - $90) positions and re-reads).

    `ctrl_tab`/`freq_tab` may be EXTENDED past the wave table (covering the
    bytes the original reads when an instrument's wave_start sits past the
    table — an off-table WAVE read, the wave analogue of off-table freq).
    `n_inbound` is the real wave-table size: an IN-TABLE start (< n_inbound)
    is sliced bounded to n_inbound, byte-identical to the unextended call (so
    no built member regresses); an OFF-TABLE start (>= n_inbound) is sliced
    over the full extended length, capturing the off-table program. Defaults
    to len(ctrl_tab) (the unextended single-table behaviour)."""
    if n_inbound is None:
        n_inbound = len(ctrl_tab)
    # In-table slices stay bounded to the real table (today's behaviour);
    # off-table slices use the extended window.
    n = n_inbound if start < n_inbound else len(ctrl_tab)
    # OFF-table starts are resolved by simulating the engine's wave-position
    # walk (markers hop back and re-read, possibly multi-hop) until the walk
    # SETTLES into a loop — recovering the flat program even when the chain
    # re-enters a marker (Jim inst 10: off-table bytes then a 1-step ping-pong
    # = a sustained byte). The in-table path below is the proven, byte-identical
    # slice (no built member regresses).
    if start >= n_inbound:
        return _resolve_wave_chain(ctrl_tab, freq_tab, start)
    # a start sitting on a marker re-dispatches immediately (the
    # original checks the marker before reading) — follow the chain
    guard = 0
    while start < n and ctrl_tab[start] >= 0x90:
        back = ctrl_tab[start] - 0x90
        if back == 0:
            raise RuntimeError(f'unsupported:wave_marker_chain @{start}')
        if start - back < 0:
            # the engine's SBC is 8-bit: the hop UNDERFLOWS and wraps to a
            # high position in the 256-byte read window (Cool_Compo_Tune:
            # marker $FF at pos $26 -> $B7). Resolve by simulating the
            # mod-256 walk over the extended window.
            return _resolve_wave_chain(ctrl_tab, freq_tab, start)
        start -= back
        guard += 1
        if guard > 64:
            raise RuntimeError('unsupported:wave_marker_chain loop')
    pos = start
    end = None
    while pos < n:
        if ctrl_tab[pos] >= 0x90:
            end = pos
            break
        pos += 1
    if end is None:                      # runaway — cap at table end, hold
        ctrl = ctrl_tab[start:n]
        freq = freq_tab[start:n]
        return ctrl, freq, max(0, len(ctrl) - 1)
    back = ctrl_tab[end] - 0x90
    loop_pos = end - back
    if loop_pos < 0:
        # 8-bit underflow: the engine wraps to a high window position and
        # keeps playing from there (NOT a Python negative slice — that read
        # the extended table's TAIL, garbage far past the real window).
        # Simulate the mod-256 walk instead (family-1 deep-tail round 18).
        return _resolve_wave_chain(ctrl_tab, freq_tab, start)
    if loop_pos >= start:
        return (ctrl_tab[start:end], freq_tab[start:end], loop_pos - start)
    # loop target before the start: cycle = [loop_pos..end-1]; the
    # heard sequence is [start..end-1] then the cycle repeating, which
    # equals list [start..end-1]+[loop_pos..start-1] with loop=0.
    if any(b >= 0x90 for b in ctrl_tab[loop_pos:start]):
        # the pre-start region holds ANOTHER marker (chained hop, e.g.
        # $94 -> $91 -> settle) — the flat concatenation would emit the
        # marker byte as a step; simulate the engine's walk instead
        # (Tichelmann_03 inst 12: [$14,$14,$14,$94] settles on $41/hold).
        return _resolve_wave_chain(ctrl_tab, freq_tab, start)
    return (ctrl_tab[start:end] + ctrl_tab[loop_pos:start],
            freq_tab[start:end] + freq_tab[loop_pos:start], 0)


def _resolve_wave_chain(ctrl_tab: list, freq_tab: list, start: int):
    """Flatten an OFF-table wave read by SIMULATING the engine's wave-position
    walk: each step resolves markers (>= $90 hops back val-$90 and re-reads,
    possibly several times), then emits (ctrl, freq) at the settled position
    and advances +1. The walk SETTLES into a loop once it revisits a position
    already emitted — that revisit is the loop point. Returns (ctrl, freq, loop)
    or raises wave_marker_chain for a degenerate chain (hops out of range, or
    no settle within the guard). This recovers chains the flat slicer can't —
    e.g. Jim inst 10: [$0D,$08,$06,$04,$02,$00] then a $FF->$91 hop pair that
    ping-pongs index 4<->5 = a sustained $11 (program loops on the final byte).
    """
    n = len(ctrl_tab)
    ctrl, freq = [], []
    seen = {}                       # settled position -> emit index (loop pt)
    # The engine's wave position is an 8-BIT byte (INC $177A,x wraps
    # $FF -> $00; the marker hop SBC wraps too) — so the walk is mod 256
    # (ledger C11: 8-bit index wrap, the wave-walk instance). Attah_2 inst 22:
    # wave_start $FF reads (ctrl $03, +17) then WRAPS to $00 for the real
    # program [(41,+0)] loop; the old linear walk read past index 255 into
    # the extended window and produced a bogus program. Positions are
    # wrapped; reads stay within the first 256 bytes of the window.
    pos = start & 0xFF
    for _ in range(512):
        hops = 0
        while pos < min(n, 256) and ctrl_tab[pos] >= 0x90:
            pos = (pos - (ctrl_tab[pos] - 0x90)) & 0xFF
            hops += 1
            if hops > 128:
                raise RuntimeError(f'unsupported:wave_marker_chain @{start}')
        if pos >= min(n, 256):       # beyond the readable window -> hold
            break
        if pos in seen:
            return ctrl, freq, seen[pos]
        seen[pos] = len(ctrl)
        ctrl.append(ctrl_tab[pos])
        freq.append(freq_tab[pos])
        pos = (pos + 1) & 0xFF
    if not ctrl:
        raise RuntimeError(f'unsupported:wave_marker_chain @{start}')
    return ctrl, freq, max(0, len(ctrl) - 1)


def _decode_instrument(mem, base: int, iid: int,
                       ctrl_tab, freq_tab, n_inbound=None,
                       pw_bound_shift: int = 4) -> DmcInstrument:
    # the player computes the record offset in the 8-bit accumulator
    # ($1213-$121F: CLC / ASL x3 / ADC #n x3), so it WRAPS mod 256 — but NOT
    # as a clean (iid*11) & 0xFF: the CLC runs only once, so a carry out of
    # an INTERMEDIATE ADC feeds the NEXT one (+1). E.g. iid=26: $D0+$1A=$EA,
    # $EA+$1A=$104 -> A=$04 c=1, $04+$1A+1 = $1F (31), where (26*11)&$FF
    # gives 30 (Techno's V1 first-note class, family-1 round 16). And a
    # final ASL carry-out feeds the FIRST ADC (iid >= 32). Emulate the exact
    # 6502 chain. iid 0-23 (offset < 256, no wraps) are unaffected.
    off = iid
    c = 0
    for _ in range(3):
        c = (off >> 7) & 1
        off = (off << 1) & 0xFF
    for _ in range(3):
        off = off + iid + c
        c = 1 if off > 0xFF else 0
        off &= 0xFF
    b = [mem[base + off + k] for k in range(11)]
    fx = b[10]
    pw_base = b[6] >> 4
    nibs = [b[3] & 0xF0, (b[3] & 0x0F) << 4,
            b[4] & 0xF0, (b[4] & 0x0F) << 4,
            b[5] & 0xF0, (b[5] & 0x0F) << 4]
    if fx & 0x10:
        gate = 'hold'
    elif fx & 0x08:
        gate = 'open'
    else:
        gate = 'release_early'
    wc, wf, wl = _slice_wave(ctrl_tab, freq_tab, b[9], n_inbound)
    return DmcInstrument(
        id=iid, ad=b[0], sr=b[1],
        pw_init_hi=b[2] & 0x0F, pw_bound_a=b[2] >> pw_bound_shift,
        pw_bound_b=(b[2] >> pw_bound_shift) ^ 0x0F,
        pw_steps=[(x + pw_base) & 0xFF for x in nibs],
        pw_keep_running=bool(fx & 0x04),
        filter_def=b[6] & 0x0F, filter_on=bool(fx & 0x20),
        filter_keep_running=bool(fx & 0x02),
        vib_delay=(b[7] >> 4) * 8, vib_width=b[7] & 0x0F,
        vib_ramp=b[8], dual=bool(fx & 0x40),
        slide_step=b[8] & 0x7F, slide_dir='up' if b[8] & 0x80 else 'down',
        gate_mode=gate, gate_open=(fx & 0x18) == 0x18, drum=bool(fx & 0x01),
        noise_attack=bool(fx & 0x80), wave_start=b[9],
        wave_ctrl=wc, wave_freq=wf, wave_loop=wl)


def _decode_filter_def(mem, base: int, n: int) -> dict:
    r = [mem[base + n * 16 + k] for k in range(16)]
    return {'res': r[0] >> 4, 'mode': r[0] & 0x0F, 'init': r[1],
            'repeat': r[2], 'stop': r[3],
            'steps': [(_signed8(r[4 + k]), r[10 + k]) for k in range(6)]}


# ---------------------------------------------------------------------------
# Top-level extraction
# ---------------------------------------------------------------------------

def extract(cfg: DMCV4Config, hvsc_root: str = 'hvsc84') -> DmcModel:
    path = os.path.join(hvsc_root, cfg.sid_path)
    mem, s = _load_image(path)
    # INIT-UNPACKER member (factory-detected): every data table lives
    # OUTSIDE the loaded image, generated by init in high RAM. The bytes
    # the engine reads are the post-init RAM, so extract from that — the
    # file image has nothing at the table addresses. (Priming reads —
    # d417 shadow, idle notes/masks — likewise come out post-init, which
    # is exactly the state the play loop starts from.)
    # RELOCATED compilation player (ledger C31 + C26): the dispatch wrapper
    # COPIES this player into RAM during init, so it is absent from the file
    # image at `cfg.base` entirely. Extract from the RAM left by the init of a
    # subtune that selects it (`post_init_sub`) — that is the memory the
    # engine itself reads.
    post_sub = getattr(cfg, 'post_init_sub', None)
    if getattr(cfg, 'data_post_init', False) or post_sub is not None:
        post = _postinit_window(s, 0, 0x10000, sub=post_sub,
                                stop_at_player=post_sub is not None)
        assert post is not None, \
            'init-unpacker member: py65 could not complete init'
        mem = bytearray(post)

    # dataflow: the packer-patched table addresses
    instr_base = _rd16(mem, cfg.op_instr)
    wavectrl = _rd16(mem, cfg.op_wavectrl)
    wavefreq = _rd16(mem, cfg.op_wavefreq)
    filtdef = _rd16(mem, cfg.op_filtdef)
    tunetab = _rd16(mem, cfg.op_tunetab)
    secp_lo = _rd16(mem, cfg.op_secp_lo)
    secp_hi = _rd16(mem, cfg.op_secp_hi)
    # canon/2-entry put the instrument table at base+$8F0; family 2
    # relocates it ($17B0). Trust the operand read, bounded to the
    # LOADED IMAGE as a sanity floor (the factory validates the player
    # identity separately; the verify gates a mislocation). Members with a
    # data prefix below the player put the table there (Mothafucka_2SID:
    # load $0900, instruments at $0A00 — a genuine record array). A RELOCATED
    # compilation player is exempt from the floor: the wrapper can copy it
    # BELOW the load address (Pour_le_merite $9409 -> $1000), so its tables
    # legitimately sit there — the floor guards image reads, not RAM reads.
    _floor = 0 if post_sub is not None else s['load']
    assert _floor <= instr_base < 0x10000, \
        f'non-standard instrument base ${instr_base:04X}'

    n_wave = wavefreq - wavectrl
    # Extend the read window past the wave table so an instrument whose
    # wave_start sits past it (an off-table WAVE read — the wave analogue of
    # off-table freq) is sliced from the bytes the original actually reads
    # (the freq table + following data region). _slice_wave bounds IN-table
    # starts to n_wave (byte-identical to the unextended slice), so the
    # extension only affects the previously-refused off-table instruments.
    ext = min(0x10000 - max(wavectrl, wavefreq), max(n_wave, 0) + 0x180)
    ctrl_tab = [mem[wavectrl + i] for i in range(ext)]
    freq_tab = [mem[wavefreq + i] for i in range(ext)]

    b = cfg.base
    # idle note / gate-mask = the file-image initial values of the per-voice
    # curnote / gatemask STATE blocks. Canon: base+0x12 / base+0x0F; a
    # re-assembled variant lays them out differently and the dataflow extractor
    # LOCATES them (cfg.curnote_addr / cfg.gatemask_addr) — fall back to canon.
    cn = cfg.curnote_addr if cfg.curnote_addr is not None else b + 0x12
    gm = cfg.gatemask_addr if cfg.gatemask_addr is not None else b + 0x0F
    dp = (getattr(cfg, 'dual_parity_addr', None)
          if getattr(cfg, 'dual_parity_addr', None) is not None
          else b + 0x19)
    # Leftover priming: prefer the factory's POST-INIT capture (dataflow /
    # re-assembled members whose init may clear these bytes — canon init
    # provably never touches them, so canon has no post_init_state and
    # keeps reading the file image).
    pis = getattr(cfg, 'post_init_state', None) or {}
    m = DmcModel(
        freq_lo=[mem[cfg.freq_lo_addr + i] for i in range(96)],
        freq_hi=[mem[cfg.freq_hi_addr + i] for i in range(96)],
        vibdepth=[mem[cfg.vibdepth_addr + i] for i in range(96)],
        d417_shadow=pis.get('d417_shadow', mem[cfg.d417_shadow_addr]),
        idle_notes=tuple(pis.get('idle_notes',
                                 (mem[cn], mem[cn + 1], mem[cn + 2]))),
        idle_masks=tuple(pis.get('idle_masks',
                                 (mem[gm], mem[gm + 1], mem[gm + 2]))),
        idle_guards=tuple(pis.get('idle_guards',
                                  (mem[b + 0x786], mem[b + 0x787],
                                   mem[b + 0x788]))),
        durrel_init=tuple(pis.get('durrel_init',
                                  (mem[b + 0x73E], mem[b + 0x73F],
                                   mem[b + 0x740]))),
        dual_phase=pis.get('dual_phase', mem[dp] & 1),
        cia_period=cfg.cia_period,
        play_repeat=cfg.play_repeat,
        title=s.get('name', ''), author=s.get('author', ''),
        released=s.get('released', ''),
        clock=_hdr_clock(path), sid_model=_hdr_sid_model(path),
        n_subtunes=s.get('songs', 1), start_song=s.get('start', 1),
    )

    m.idle_wave = _slice_wave(ctrl_tab, freq_tab, 0, n_wave)

    # OUT-OF-IMAGE loop sector ($0000 bucket): a $FF track loop lands on a
    # garbage sector number past the pointer table whose pointer is $0000, so
    # the sector reads live ZEROPAGE as note data. The file image is all-zero
    # below the load address, so the naive decode is note-0-forever; the engine
    # actually plays the 6510 I/O port ($00=$2F DDR, $01=$37 port under the PSID
    # environment) then static zp bytes. Capture that low RAM from libsidplayfp
    # (py65 can't reproduce the environment's zeropage — ledger C9) and overlay
    # it so _walk_track / _simulate_sector read what the engine reads (C26: read
    # the runtime RAM, not the image). Gated on an out-of-image loop, so every
    # in-image track is byte-identical (the overlay only touches $00-$FF, which
    # nothing else reads). Regression-safe by construction: a played out-of-image
    # sector was always mis-decoded (image zeros != runtime), so any member this
    # changes was already non-FULL; an unplayed sector's decode never reaches the
    # write-log.
    # A hand-crafted init wrapper can HARD-FORCE the played record (cfg.
    # forced_subtune, factory C19 probe: Sans_intro's `LDA #$01` prefix forces
    # record 1 — record 0 is a $FE-stop dummy). Walk the played record then.
    forced = getattr(cfg, 'forced_subtune', None)
    # C29 track-pointer class: a tune-table TRACK POINTER can itself leave the
    # image into banked ROM (Memomania sub 3: V1 ptr $F256 = KERNAL ROM). The
    # orderlist is then read from ROM, so overlay its CPU-eye window BEFORE the
    # secp-read + sector walks below (both read `mem[tp+pos]`) — else they walk
    # the zero-fill and mislocate everything. SKIPPED for post-init memory
    # (same gate as _undefined_secp_reads below): there `mem` is the runtime
    # RAM the engine reads, and a $A000-$BFFF/$E000+ orderlist address is
    # GENERATED RAM, not banked ROM — peeking the CPU-eye there would clobber
    # the generated orderlist with ROM bytes (Kan-Kan: init-unpacked orderlist
    # at $A3A1 is RAM, not BASIC ROM).
    _dpi = getattr(cfg, 'data_post_init', False)
    if not (_dpi or post_sub is not None):
        _oob_tracks = _offimage_track_ptrs(mem, tunetab, s.get('songs', 1),
                                           forced=forced)
        _overlay_offimage_windows(mem, path, _oob_tracks, None, s, False)
    # C29 pointer-byte class: a sector-POINTER fetch itself can leave the
    # image (track byte selects a sector # past the pointer tables). Serve
    # those bytes the CPU-eye value FIRST, or the zero-filled image view
    # mislocates the sector base and the window overlay below peeks the
    # wrong address ($00CA instead of $FFCA — Trailways_A). Skipped for
    # post-init memory: _postinit_window already seeds the power-on pattern.
    if not (getattr(cfg, 'data_post_init', False) or post_sub is not None):
        _updef = _undefined_secp_reads(
            mem, secp_lo, secp_hi, tunetab, s.get('songs', 1), s['load'],
            s['load'] + len(s['payload']), cfg.track_loop_target,
            forced=forced)
        for _a, _v in _cpu_peek(path, [(a, a) for a in _updef],
                                subtune=post_sub).items():
            mem[_a] = _v
    oob = _offimage_sectors(mem, secp_lo, secp_hi, tunetab, s.get('songs', 1),
                            s['load'], cfg.track_loop_target, forced=forced)
    # CPU-EYE overlay of every off-image sector window (the shared helper —
    # see its docstring for the undefined-only + static/dynamic rules and the
    # Pour_le_merite / Abyssal_Karma / Remix_1995 incidents behind them). The
    # sonified environment is banked-in ROM (incl. psiddrv's PATCHED KERNAL
    # vectors — Super_Seven's window byte 14 = $FFFD, the relocated driver
    # entry hi), the 6510 port, env zeropage and the power-on RAM pattern.
    _overlay_offimage_windows(mem, path, oob, post_sub, s, _dpi)
    # ($F8/$F9 — the live sector pointer — is served per-window inside
    # _simulate_sector's rd(); overlapping low windows each see their OWN
    # base, which one shared mem[] byte cannot express.)

    # decode subtunes; collect referenced instruments + filter defs as
    # they surface
    used_instr = set()
    for sub in range(m.n_subtunes):
        rec = tunetab + (sub if forced is None else forced) * 8
        # glide_neutered wedge: simulate the re-pointed store's data poke on
        # a per-song copy so the walk reads the engine's EFFECTIVE bytes
        # (each subtune plays standalone — no cross-song poke leakage).
        smem = mem
        _gn = cfg.extra_params.get('glide_neutered')
        if _gn:
            _pokes = _glide_poke_overlay(mem, rec, secp_lo, secp_hi,
                                         _SECFMT[cfg.sector_format],
                                         int(_gn, 16))
            _pokes = {a: v for a, v in _pokes.items() if mem[a] != v}
            if _pokes:
                smem = list(mem)
                for _a, _v in _pokes.items():
                    smem[_a] = _v
        voices = []
        for vi in range(3):
            tp = _rd16(mem, rec + vi * 2)
            # loop_reset_pos is either a scalar N (reset-all-to-N, every voice
            # loops to the same position) or a per-voice tuple (reset-all with
            # a distinct loop position per voice — ledger C13 refinement).
            lrp = cfg.loop_reset_pos
            if isinstance(lrp, tuple):
                lrp = lrp[vi]
            fmt = _SECFMT[cfg.sector_format]
            if cfg.extra_params.get('glide_neutered'):
                fmt = _dc_replace(fmt, glide_dead=True)
            _sr = getattr(cfg, 'switch_retrig', False)
            _lni = getattr(cfg, 'loop_note_inject', False)
            v = _walk_track(smem, tp, secp_lo, secp_hi,
                            loop_target=cfg.track_loop_target,
                            loop_reset_pos=lrp,
                            fmt=fmt, switch_retrig=_sr,
                            loop_note_inject=_lni)
            # Initial sticky-instrument LEFTOVER ($1015,x — canon init never
            # clears it): a voice that note-inits before any $6x command
            # plays the leftover instrument, not 0. Re-walk seeded ONLY when
            # consumed (zero churn otherwise) and plausibly an instrument
            # number (the $6x command domain is &$1F; a wilder leftover would
            # need the note-init's exact ADC-chain wrap emulated — refuse by
            # keeping today's decode, the member stays partial as before).
            _seedl = smem[(_eventdriven_addrs(cfg)[2][vi]) & 0xFFFF]
            if _seedl and _seedl < 0x20 and _seed_consumed(v):
                v = _walk_track(smem, tp, secp_lo, secp_hi,
                                loop_target=cfg.track_loop_target,
                                loop_reset_pos=lrp,
                                fmt=fmt, instr_seed=_seedl,
                                switch_retrig=_sr,
                                loop_note_inject=_lni)
            voices.append(v)
        song = DmcSong(id=sub + 1, speed=mem[rec + 6],
                       master_vol=mem[rec + 7], voices=voices)
        m.songs.append(song)
        for v in voices:
            for rows in v.patterns:
                for r in rows:
                    used_instr.add(r.instr)

    # The engine's note-init cache is cleared to 0 by init, so a voice
    # idling before its first note runs record 0's pulse/wave mechanism.
    # Record 0 must therefore always ship (and sit first in the list).
    used_instr.add(0)
    # PWM bound-A extraction shift: canon note-init does LSR x4 (bound A =
    # byte+2 hi nibble); a wedge variant (factory._pw_bound_shift_probe) drops
    # one LSR to >>2, widening the PWM sweep band. Extract-only knob — the
    # resulting bound VALUES ride in USF min_hi/max_hi, so it never enters USF.
    pw_shift = int(getattr(cfg, 'extra_params', {}).get('pw_bound_shift', 4))
    for iid in sorted(used_instr):
        inst = _decode_instrument(mem, instr_base, iid, ctrl_tab, freq_tab,
                                  n_wave, pw_bound_shift=pw_shift)
        m.instruments[iid] = inst
    # Filter defs: capture the ENTIRE 8-bit walk window, not just the defs
    # instruments reference. The engine's repeat reload ($1719 = def+2) can be
    # > 5; the step index then walks UPWARD forever (INC + CMP #6 exact-match
    # never fires again), reading size/duration bytes at def-table offsets that
    # cross into ADJACENT records (and, via the +10 durations view, up to
    # def-table+265). Emitting the composer's table in the orig's 16-byte
    # record layout (composer fdrec) makes every walked read byte-exact — so
    # ship all 16 records (typed, byte-lossless) + the 10-byte tail. C2 class.
    # 17 records = 272 bytes >= the 266-byte window (16*16 + the 10 bytes the
    # +10 durations view reaches at walk index 250..255); the 17th record's
    # last 6 bytes are unreachable padding, kept typed for uniformity.
    # POST-INIT ground truth: some inits rewrite the def records (the 'Ed'
    # members stamp res/mode + initial cutoff over every def) — decode what
    # the engine reads, not the file image; py65-fail keeps the file image.
    if any(m.instruments[i].filter_on for i in m.instruments):
        # Same memory view as the rest of this player's extraction: for a
        # RELOCATED compilation player that means ITS subtune's run, stopped at
        # the landing. Re-reading with the default (start-song, run-to-RTS)
        # would run a subtune whose wrapper never copies this player into
        # place, so the window comes back all zeros and every filter def
        # decodes empty (Pour_le_merite sub 0 lost its whole filter window).
        post = _postinit_window(s, filtdef, 272, sub=post_sub,
                                stop_at_player=post_sub is not None)
        fmem = mem
        if post is not None and list(mem[filtdef:filtdef + 272]) != post:
            fmem = bytearray(mem)
            fmem[filtdef:filtdef + 272] = bytes(post)
        for d in range(17):
            if filtdef + d * 16 + 16 <= 0x10000:
                m.filter_defs[d] = _decode_filter_def(fmem, filtdef, d)
    # family 2: cymbal fires one frame later (frame 2, params.cymbal_onset),
    # and the vibrato swells differently — note-init stores freq_hi(note)>>1
    # to $178C and RAMPS the 16-bit step ($1792/$1795) by it each half-cycle
    # (canon instead loads a fixed step from the $1888 VIBDEPTH table and
    # doubles the WIDTH). The composer derives the increment from the freq
    # table; the swell mechanism is the build-level params.vib_ramp flag.
    m.family2 = (cfg.sector_format == 'family2')
    # pw_bound_shift is consumed above (extract-only); keep it out of USF so
    # the params block carries only musical content, never the derivation knob.
    m.extra_params = {k: v for k, v in getattr(cfg, 'extra_params', {}).items()
                      if k != 'pw_bound_shift'}
    if m.extra_params.get('dual_freq_generator'):
        # Dual-generator members (factory._dual_freq_gen_probe) force pwphase to
        # P0/P0+1 on every dual frame (P0 = $19 + ph_add), so the pulse
        # machine's speed fetch reads instr_base + ioff + 3 + (P>>1) — past
        # the instrument's own record. Those are STATIC table bytes; capture
        # them per dual instrument so the composer can extend its stride-8
        # isteps/irawsp tables at the reachable indices (P0..P0+3 — at most
        # two direction-flip INCs before the next dual-frame reset).
        from pipelines.dmc.composer_asm import _inst_offset
        ph_add = int(m.extra_params['dual_freq_generator'].split(',')[1])
        p0 = (0x19 + ph_add) & 0xFF
        ents = []
        for iid, ins in sorted(m.instruments.items()):
            if not ins.dual:
                continue
            ioff = _inst_offset(iid)
            raws = [mem[instr_base + ioff + 3 + (p0 >> 1) + k]
                    for k in range(3)]
            ents.append(':'.join([str(iid + 1)] + [str(r) for r in raws]))
        if ents:
            m.extra_params['dual_generator_steps'] = ','.join(ents)
    _assign_offtable_freq(m, mem, cfg.freq_lo_addr, cfg.freq_hi_addr,
                          cfg.vibdepth_addr)
    # off-table source bytes are in the engine's work RAM; init writes them, so
    # the runtime value differs from the file image. Correct to what the engine
    # actually reads (post-init, ground truth) — recovers the constant reads the
    # file-image capture mis-valued (the "dynamic residue" that wasn't).
    varying = _correct_offtable_postinit(m, path, cfg.freq_lo_addr,
                                         cfg.freq_hi_addr, cfg.vibdepth_addr,
                                         getattr(cfg, 'song_subtunes', None))
    # State-geometry probe: the composer's off-table redirect map
    # (DMC_OFFTABLE_STATE) + the sectpos shadow identify window idx with the
    # canon live state vars via the CANON table→state geometry (state block at
    # canon offsets from the freq tables — invariant under whole-image
    # relocation). Variant builds move the state elsewhere (the page-3 builds:
    # Viiskyt_vuotta_humppaa keeps per-voice state at $03xx) — their window
    # bytes are unrelated STATIC code/data, exactly what the post-init capture
    # above serves, and every live redirect there would shadow a correct
    # static value (idx 130 "sectpos" = an opcode byte; idx 208 "cvram" = an
    # INY). Probe statically (C19: read the member's instructions): the canon
    # player DECs its per-voice duration counter at freq_hi + ($173B-$16A7);
    # no `DEC <that addr>,x` in the image ⇒ non-canon geometry ⇒ redirect map
    # + sectpos shadow off, event-driven correction unrestricted.
    canon_geom = _canon_state_geometry(mem, cfg)
    # If any off-table byte varied over the post-init time-sample, some read may
    # land on a globally-varying byte that is nonetheless STABLE at the moment a
    # given note reads it (sector-position, a settled track pointer). Recover
    # those with an event-driven capture (the value read AT the access). Gated so
    # members whose off-table reads are all init-constant skip the extra siddump.
    # Canon geometry only: the capture memwatches the member's (relocated) state
    # addresses derived from cfg; on a non-canon member the canon offsets are
    # unrelated bytes — it would fabricate constant bogus keys that can poison
    # correct records. Non-canon members keep the post-init static values (their
    # window bytes are static code/data; a varying one stays honest residue).
    # COMPILATION (ledger C31): a packed player's event-driven capture must run
    # the file subtune(s) that SELECT it (song_subtunes.values()), else it reads
    # the START player's off-table results and overwrites correct records
    # (Rogue_Ninja player-1 idx 97 = $B7 clobbered by player-0's $1708 = $D6).
    # GLIDE-ARRIVAL reach (r116, Psycho_One): a slow glide's ARRIVAL reloads
    # curnote = target ($1481 TYA/STA $1012,x) — and the arrival can land
    # frames later, under a LATER instrument's still-running wave (glsp
    # survives the intervening rows). A low target (the glide-to-0 dive
    # idiom) then sends that wave's negative offsets off-table (idx 255..)
    # — reads the static row walk cannot enumerate (the target note never
    # appears on the reading instrument's rows). Gate: any glide target
    # that, combined with any shipped instrument's wave offset, indexes
    # past the table; the event-driven capture then observes the actual
    # reads and CREATES the missing records (keyed to glide-target notes
    # only — surgical).
    glide_notes = set()
    for song in m.songs:
        for v in song.voices:
            for ei, e in enumerate(v.entries):
                tr = v.transposes[ei] if v.transposes else 0
                for r in v.patterns[e]:
                    if r.glide_to is not None:
                        glide_notes.add((r.glide_to + tr) & 0xFF)
                    elif r.glide_slide and r.note is not None:
                        glide_notes.add((r.note + tr) & 0xFF)
    _all_offs = {o & 0xFF for ins in m.instruments.values()
                 for o in ins.wave_freq} | {0}
    glide_risk = any(((t + o) & 0xFF) > 95
                     for t in glide_notes for o in _all_offs)
    if (varying or glide_risk) and canon_geom:
        _ss = getattr(cfg, 'song_subtunes', None)
        _fsubs = sorted(set(_ss.values())) if _ss else None
        _correct_offtable_eventdriven(m, path, cfg=cfg, file_subtunes=_fsubs,
                                      create_notes=glide_notes)
    # sectpos shadow gating: an off-table freq read landing on $1729-$172B
    # (per-voice sector position — INC per consumed sector byte, reset at the
    # $7F end check) cannot be served statically (the value cycles) nor by the
    # event-driven capture (varies per key). The composer maintains a live
    # sectpos,x shadow instead, its per-row values derived from row kind +
    # the stated-command flags (dur_cmd/instr_cmd/vol_cmd/soft_cmd) — enable it when any
    # captured read hits those bytes (flo idx 226-228 / fhi idx 130-132),
    # canon geometry only (see the probe above).
    # Canon state geometry is stored on the model (NOT serialized as a geometry
    # bit). to_usf stamps a per-read `live` flag from it (canon AND idx hits a
    # live-served window position) and derives the sectpos row-command gate; the
    # composer re-derives its member-global redirect/sectpos booleans from those
    # per-read flags. Replaces the old ML-visible offtable_redirect/sectpos_shadow
    # params (which described HVSC memory geometry — Core Tenet corollary).
    m.offtable_canon = canon_geom
    # wavepos live serving: an off-table freq read on $177A-$177C (fhi idx
    # 211-213) sonifies a voice's LIVE wave position — it varies at the read
    # (neither the static capture nor the event-driven one can serve it), and
    # the composer's own wavepos runs on ITS re-packed pool offsets. When
    # every wave program (idle walk included) is a verbatim contiguous slice
    # of the orig table, carry each instrument's editor wave-table position
    # (arrangement, §8) so the composer packs its pool at the orig positions —
    # then its wavepos state EQUALS orig $177A,x and the DMC_WAVEPOS_ROW
    # redirect serves the read live. Canon geometry only (ledger C6 note).
    _WAVEPOS_IDX = {(0x177A + k) - 0x16A7 for k in range(3)}
    if canon_geom and any((off + note) & 0xFF in _WAVEPOS_IDX
                          for ins in m.instruments.values()
                          for off, note, _lo, _hi in ins.offtable_freq):
        pos = _wave_layout_verbatim(m, ctrl_tab, freq_tab, n_wave)
        if pos is not None:
            for iid, c in pos.items():
                m.instruments[iid].wave_pool_pos = c
            m.wavepos_layout = True
    # d417_tail_anim (Ed/Go_Funk, C19): the stub animates two WAVEFREQ-table
    # bytes, targetable in our build only when the wave pool is emitted
    # layout-preserving (positions == the orig table's). Force that layout
    # for carriers; if it cannot be proven verbatim, drop the param — the
    # member stays honestly partial rather than poking the wrong pool bytes.
    if 'd417_tail_anim' in m.extra_params and not m.wavepos_layout:
        pos = _wave_layout_verbatim(m, ctrl_tab, freq_tab, n_wave) \
            if canon_geom else None
        if pos is not None:
            for iid, c in pos.items():
                m.instruments[iid].wave_pool_pos = c
            m.wavepos_layout = True
        else:
            del m.extra_params['d417_tail_anim']
    # Wave-table NORMAL FORM (§4): state the shared table + prove the
    # resolver round-trip; None = keep the resolved-copy form wholesale.
    m.wave_table_norm = _wave_table_normal_form(m, ctrl_tab, freq_tab,
                                                n_wave)
    # wjmp chase shadow: an off-table freq read on $171F (fhi idx 120 / flo
    # idx 216) sonifies the shared effect scratch — the LAST value written to
    # it that frame. One writer is a chasing instrument's first-read hop: an
    # instrument whose wave byte9 sits ON its own loop marker ($90+n, loop 0)
    # chases back n every note-init, storing $171F=n. The composer packs the
    # SETTLED program (skips the transient chase), so it misses that one write
    # — mark such instruments so the composer re-asserts wjmp=n at note-init
    # (the hop repeats every settled frame anyway; only note-init is missed).
    # Canon geometry only; layout-independent (the value is the distance n,
    # not a pool position), so unaffected by / orthogonal to wavepos_layout.
    _WJMP_IDX = {(0x171F - 0x16A7) & 0xFF, (0x171F - 0x1647) & 0xFF}
    if canon_geom and any((off + note) & 0xFF in _WJMP_IDX
                          for ins in m.instruments.values()
                          for off, note, _lo, _hi in ins.offtable_freq):
        _wlim = min(n_wave, 256)
        for ins in m.instruments.values():
            ws, n = ins.wave_start, len(ins.wave_ctrl)
            if (ins.wave_loop == 0 and n and ws < _wlim
                    and ctrl_tab[ws] == 0x90 + n):
                ins.wave_start_on_marker = True
    _split_offtable_by_subtune(m)
    # v3_instr_tempo (custom Doxx build, factory-probed): the play tail reads
    # the THIRD voice's current-instrument slot as a TEMPO MAILBOX — an
    # instrument command with number >= $10 doubles as "speed reload = n &
    # $0F" (the row still sets the sticky instrument to the phantom record,
    # which the pool carries faithfully). Attach the musical tempo event to
    # the row (fx `tempo=N`, ledger C14); the composer emits a gated tempo
    # prefix at the row fetch.
    if cfg.extra_params.get('v3_instr_tempo'):
        for song in m.songs:
            for rows in song.voices[2].patterns:
                for r in rows:
                    if r.icmd and r.instr >= 16:
                        r.tempo = r.instr & 0x0F
    return m


def _split_offtable_by_subtune(m: DmcModel) -> None:
    """Serve a per-SUBTUNE off-table byte through a SHARED instrument (ledger
    C31's "no file-level idx-keyed table can hold a per-player fact", in its
    single-player form). A record's source byte can be per-subtune init state
    (track-ptr slots): the reaching subtunes each read a DIFFERENT constant,
    so one instrument record — and one static window byte — cannot serve
    both (Assassins: inst 21 idx 98 = $1709, sub 0 $80 / sub 1 $CE; the
    start-song fallback made every non-start subtune read the wrong pitch).

    Fix with ZERO composer/schema change: clone the instrument per
    VALUE-CLASS (subtunes grouped by their sampled record values) and remap
    the non-start classes' rows to the clone — each subtune then USES an
    instrument carrying its own values, which is exactly the disagreement
    the composer's per-subtune window patch (`ovr_sub`) detects and serves
    by re-writing the conflicting window positions at every init. The two
    subtunes genuinely hear different pitches at that read, so two
    instrument points is honest musical content, not duplication for
    mechanism's sake. Gated: no disagreement (the corpus-dominant case) ->
    no clone -> byte-identical."""
    sv = getattr(m, 'offtable_song_values', None)
    if not sv:
        return
    from collections import defaultdict
    from dataclasses import replace
    import copy
    by_inst = defaultdict(dict)
    for (iid, off, note), vals in sv.items():
        by_inst[iid][(off, note)] = vals
    next_id = max(m.instruments) + 1
    start_si = max(0, (getattr(m, 'start_song', 1) or 1) - 1)
    for iid, recs in sorted(by_inst.items()):
        ins = m.instruments.get(iid)
        if ins is None:
            continue
        songs = sorted({si for vals in recs.values() for si in vals})
        # value-class: the tuple of this subtune's sampled record values
        cls = {}
        for si in songs:
            key = tuple(sorted((k, vals[si]) for k, vals in recs.items()
                               if si in vals))
            cls.setdefault(key, []).append(si)
        if len(cls) < 2:
            continue
        # the class holding the start song keeps the original instrument
        # (whose records already carry the start-song fallback values)
        keep = next((k for k, ss in cls.items() if start_si in ss),
                    next(iter(cls)))
        for key, ss in sorted(cls.items()):
            if key == keep:
                tgt, t = iid, ins
            else:
                t = copy.deepcopy(ins)
                tgt = t.id = next_id
                next_id += 1
                m.instruments[tgt] = t
            vals = dict(key)
            t.offtable_freq = sorted(
                (off, note) + vals.get((off, note), (lo, hi))
                for off, note, lo, hi in t.offtable_freq)
            if tgt == iid:
                continue
            for si in ss:
                for v in m.songs[si].voices:
                    v.patterns = [
                        [replace(r, instr=tgt) if r.instr == iid else r
                         for r in pat] for pat in v.patterns]


def _wave_table_normal_form(m: DmcModel, ctrl_tab, freq_tab, n_wave):
    """Build the sparse STATED wave table (normal form §4) and prove, via
    the SHARED resolver, that it reproduces every resolved program —
    the C32 re-derivation assert. Returns the cell dict or None (member
    keeps the resolved-copy form wholesale).

    Cell collection mirrors the slicer's two bounding regimes: an
    in-table walk is bounded to the real wave table (`n_wave`), the
    mod-256 chain regime to the 256-byte read window — tried in that
    order per program, accepting whichever reproduces the extract's
    (ctrl, freq, loop) exactly. The FINAL assert re-runs the resolver
    over the merged union (another program may state cells past a
    bound that would change this program's absent-cell hold — the
    union-pollution case), refusing wholesale on any mismatch.

    Phase 4 lifted the former wavepos_layout / start-on-marker
    exclusions: wavepos_layout members carry BOTH forms during the
    transition (the composer prefers place_prog when wave_table_pos is
    present — byte-identical to the pre-norm build); a start-on-marker
    instrument's `wave_start` is the raw marker cell, which the walk
    chases exactly as the engine does (a non-positional build still
    materializes the settled span and keeps the iwchase re-assert via
    the wave_start_on_marker flag)."""
    from src.usf.resolve import resolve_wave_table, walk_wave_table

    def view(bound):
        b = min(bound, 256, len(ctrl_tab))
        return {i: (('jump', ctrl_tab[i] - 0x90) if ctrl_tab[i] >= 0x90
                    else ('step', ctrl_tab[i], freq_tab[i]))
                for i in range(b)}
    views = (view(n_wave), view(256))
    progs = [(0, (list(m.idle_wave[0]), list(m.idle_wave[1]),
                  m.idle_wave[2]))]
    progs += [(ins.wave_start, (list(ins.wave_ctrl), list(ins.wave_freq),
                                ins.wave_loop))
              for ins in m.instruments.values()]
    union = {}
    for start, want in progs:
        got = None
        for v in views:
            r = walk_wave_table(v, start)
            if r is not None and (r[0], r[1], r[2]) == want:
                got = r
                break
        if got is None:
            return None
        for p in got[3]:
            union[p] = views[1].get(p, views[0].get(p))
    for start, want in progs:
        r = resolve_wave_table(union, start)
        if r is None or (list(r[0]), list(r[1]), r[2]) != want:
            return None
    return union


def _wave_layout_verbatim(m: DmcModel, ctrl_tab, freq_tab, n_wave):
    """Layout-preserving-pool precondition. Returns `{iid: table position of
    the program's first step}` when the idle walk AND every instrument's wave
    program are verbatim contiguous slices of the original wave table, ending
    on an orig marker byte equal to the composer's synthesized `$90+(n-loop)`
    — then a pool placed at these positions makes the runtime wavepos equal
    orig $177A at every SETTLED (observable) moment, marker hops included.
    None -> the member stays honest residue.

    A wave_start may sit ON the program's own end marker (the editor idiom
    "start at the loop marker": the engine chases it back n positions on the
    first read, settling on the same step span — inst byte9 = slice start + n,
    loop 0). That's admitted; the composer skips the transient chase (iwst =
    first-step position), which is unobservable EXCEPT through the chase's
    $171F wjmp write — so a member that ALSO reads the wjmp window (flo idx
    216 / fhi idx 120) with any chasing instrument is rejected.

    A NON-verbatim program (chain-resolved / off-table / runaway) does not
    reject the member outright: its positions matter only while a wavepos
    read can OBSERVE them. When every recorded wavepos read (fhi idx
    211-213) is SELF-REFERENTIAL — voice j reading its own $177A+j during
    its own wave step of a verbatim-placed instrument (reader voices ==
    {j}, per _assign_offtable_freq's attribution) — a read can only occur
    while voice j plays that instrument, so a non-verbatim program is never
    observed and gets a FREE position past every verbatim placement
    (Object_of_Art: inst 2's $9F marker chain, played by V1 only, while
    the sole read is V3's own inst-5 step). Any cross-voice / unattributed
    (idle-path) wavepos read falls back to the strict all-verbatim rule."""
    progs = [(None, 0, list(m.idle_wave[0]), list(m.idle_wave[1]),
              m.idle_wave[2])]
    progs += [(iid, ins.wave_start, list(ins.wave_ctrl),
               list(ins.wave_freq), ins.wave_loop)
              for iid, ins in m.instruments.items()]
    lim = min(n_wave, 256)
    out, chased, nonverb, max_end = {}, False, [], 0
    for iid, start, ctrl, freq, loop in progs:
        n = len(ctrl)
        if n == 0 or not 0 <= loop < n or n - loop > 0x6F:
            return None                  # composer-shape limit: hard reject
        ok, chase = True, False
        if start < lim and ctrl_tab[start] >= 0x90:
            # start on a marker: admit ONLY the own-end-marker form
            # (back distance n, i.e. loop 0 with the slice right before it)
            if loop != 0 or ctrl_tab[start] != 0x90 + n or start < n:
                ok = False
            else:
                start -= n
                chase = True
        if ok and (start + n >= lim      # marker must sit inside the table
                   or any(b >= 0x90 for b in ctrl)   # resolved chain
                   or ctrl != ctrl_tab[start:start + n]
                   or (freq if freq else [0] * n)
                   != freq_tab[start:start + n]
                   or ctrl_tab[start + n] != 0x90 + (n - loop)):
            ok = False
        if not ok:
            if iid is None:
                return None      # the composer pins the idle program at 0
            nonverb.append((iid, n))
            continue
        chased = chased or chase
        if iid is not None:
            out[iid] = start
        max_end = max(max_end, start + n + 1)
    if nonverb:
        # relaxation gate: a wavepos read at fhi idx 211+j sonifies VOICE
        # j's wave position, so the observability condition is on the
        # READ-TARGET voice's programs — every instrument voice j plays
        # must be verbatim-placed (its labels are what the read shows).
        # The READER instrument's own placement is irrelevant: it only
        # causes the read, and its program CONTENT (hence the read
        # timing) is identical under repacking. (The pre-2026-07-28 gate
        # keyed on the reader instrument + self-referential attribution —
        # sound but wrongly-motivated; a cross-voice read of a clean
        # voice was rejected for the reader's sins.) Sticky-instrument
        # inheritance can play record 0 without stating it (C31 idle
        # semantics), so record 0 is always included.
        played_by = [set(), set(), set()]
        for song in m.songs:
            for vi, v in enumerate(song.voices):
                for rows in v.patterns:
                    for r in rows:
                        if r.instr is not None:
                            played_by[vi].add(r.instr)
        for iid, ins in m.instruments.items():
            for off, note, *_rest in ins.offtable_freq:
                idx = (off + note) & 0xFF
                if not 211 <= idx <= 213:
                    continue
                need = played_by[idx - 211] | ({0} if 0 in m.instruments
                                               else set())
                if any(k in m.instruments and k not in out for k in need):
                    return None
        seen = {}
        for iid, n in nonverb:
            ins = m.instruments[iid]
            key = (tuple(ins.wave_ctrl), tuple(ins.wave_freq), ins.wave_loop)
            if key in seen:
                out[iid] = seen[key]
                continue
            if max_end + n > 255:        # place_prog bound (marker at pos+n)
                return None
            out[iid] = seen[key] = max_end
            max_end += n + 1
    if chased:
        _WJMP_IDX = {(0x171F - 0x16A7) & 0xFF, (0x171F - 0x1647) & 0xFF}
        if any((off + note) & 0xFF in _WJMP_IDX
               for ins in m.instruments.values()
               for off, note, _lo, _hi in ins.offtable_freq):
            return None
    return out


def _assign_offtable_freq(m: DmcModel, mem, flo_addr: int,
                          fhi_addr: int, vibdepth_addr: int) -> None:
    """Capture each reachable off-table freq read as a per-instrument
    `(offset, note, lo, hi)` record — the v5 `offtable_freq` form, ported to v4.

    The original reads past its 96-entry freq tables into the engine state
    block; v4's old `_offtable_check` mirrored only the STABLE prefix (k=6..16:
    constants + speed + master vol) via the composer's co-located window and
    REJECTED any read on the track-ptr slots (k<=5) or live state (k>=17). This
    instead records the EXPLICIT (lo, hi) the read produces (read from the file
    image), so the composer can place those exact values at the matching window
    positions — recovering the STABLE-when-read reads (the value the original
    reads early, before the state evolves; the v5 read-before-evolution result).
    Genuinely per-frame-dynamic reads (a track pointer that has advanced) stay a
    verify residue, not a build error.

    The k=6..16 records are still emitted but the composer keeps those positions
    co-located (live spd/mvol/constants) — so members that only read there are
    byte-identical to before (no regression).

    Note-load reads past the table (note > 95, via transpose) make TWO off-table
    reads: the note's own freq (captured here as an offset-0 offtable_freq
    record) AND the separate vibdepth table (the vibrato step) — captured into
    `m.offtable_vibdepth` ({note: depth}), which `to_usf` emits as
    `UsfFile.offtable_vibdepth` for the composer's vibdepth overrun window. Both
    land on STATIC bytes (freq tail / instrument records), so the captured values
    are exact. No more `offtable_vibdepth` rejection."""
    from collections import defaultdict
    recs = defaultdict(set)            # inst id -> {(off, note, lo, hi)}
    vibovr = {}                        # note>95 -> off-table vibdepth byte
    # Song attribution: which subtunes REACH each record. The off-table bytes
    # can be per-subtune init-written engine state (the $1707-$170C track-ptr
    # slots are set from the tune record at init), so the post-init correction
    # must sample the subtune that actually makes the read — the default
    # start-song sample serves the wrong subtune's init state (Cool_Musax
    # sub 1: idx 96 = V1 track-ptr lo, start-song $F8 vs reading-song $17).
    songmap = defaultdict(set)         # (inst id, off, note) -> {song idx}
    vibsongs = defaultdict(set)        # note -> {song idx}
    # Reader-VOICE attribution: which voice performs each record's read (the
    # wave step / note reload runs on the reading row's own voice). Consumed
    # by _wave_layout_verbatim to prove a wavepos read ($177A+j, fhi idx
    # 211-213) is SELF-REFERENTIAL (readers == {j}) — idle-path records get
    # no entry (attribution imprecise), which reads as "unattributed" there.
    voicemap = defaultdict(set)        # (inst id, off, note) -> {voice idx}

    def add_note(n, inst_id, si, vi=None):
        inst = m.instruments.get(inst_id)
        # curnote is an 8-bit value: note-init adds the transpose with an 8-bit
        # ADC ($11A3), so a NEGATIVE transpose wraps a low note PAST the 96-entry
        # freq/vibdepth tables (ledger C11 — index mirrors the 8-bit Y register).
        # The off-table read uses Y=(note+tr)&$FF, so classify + capture on the
        # WRAPPED value; the raw signed sum misses every negative-transpose read
        # (Journey note 0 + tr -4 -> curnote $FC -> vibdepth[$FC]=$23, the drum
        # vibrato step). Notes already in 0..255 are unchanged -> regression-safe.
        wrapped = n != (n & 0xFF)          # note+transpose underflowed/overflowed
        n &= 0xFF
        if n > 95:
            # the note's off-table VIBDEPTH read (vibdepth[note], note>95) —
            # lands on STATIC instr-record bytes (representable) -> always capture;
            # this is the drum vibrato step Journey needs.
            vibovr[n] = mem[(vibdepth_addr + n) & 0xFFFF]
            vibsongs[n].add(si)
            # the note's OWN off-table FREQ (offset-0 base read): only for a
            # GENUINE off-table note (real high pitch via positive transpose). A
            # NEGATIVE-transpose WRAP (note 0 - k -> 250..255, the DMC drum/silent
            # idiom) reads freq-table-adjacent ENGINE STATE that is PER-SUBTUNE /
            # dynamic (not statically representable) AND its base freq is either
            # overridden by the drum wave-step (Journey) or $0000 (silent) -> a
            # static capture there places a WRONG value (Other_Side: subtune-0
            # flo+254 = $00 but inst-6's reaching subtune = $5E -> last-writer
            # regression). The pre-fix default (no capture) is correct for wraps.
            if not wrapped:
                recs[inst_id].add((0, n, mem[(flo_addr + n) & 0xFFFF],
                                   mem[(fhi_addr + n) & 0xFFFF]))
                songmap[(inst_id, 0, n)].add(si)
                if vi is not None:
                    voicemap[(inst_id, 0, n)].add(vi)
        elif n < 96 and mem[(vibdepth_addr + n) & 0xFFFF] != VIBDEPTH[n]:
            # PER-MEMBER VIBDEPTH DEVIATION (in-table, note 0-95): the composer
            # ships the CANONICAL 96-byte VIBDEPTH ramp, but a member can carry a
            # non-canonical byte at a note it reaches -> the vibrato step for that
            # note (vstep = vibdepth[curnote]) is wrong. Two sub-classes, same fix:
            #   * CODE-OVERLAP HEAD (idx 0-5): the table base overlaps the note-init
            #     routine; indices 3,4 are the vstep-store operand encoding the
            #     STATE-BLOCK address -> RELOCATES for page-3 builds (vibdepth[3,4]
            #     = $03BC vs canonical $1792). (Journey: note 4 -> $03 vs $17.)
            #   * IN-TABLE MUSICAL DEVIATION (idx 6-95): an authored/patched
            #     per-note vibrato depth (Enter: note 44 -> $10 vs canonical $20,
            #     that note vibrates half as deep = C6/C7-(b) state-as-data).
            # Capture the member's actual byte ONLY where it differs from canonical
            # AND the note is reachable -> canonical-layout members deviate nowhere
            # they play, so capture NOTHING (byte-identical, regression-safe by
            # construction: a FULL with an active-vibrato deviation couldn't exist,
            # an inactive one is inert). The composer overrides vibdepth[n] in place.
            vibovr[n] = mem[(vibdepth_addr + n) & 0xFFFF]
            vibsongs[n].add(si)
        if inst is None or inst.drum:
            return
        for off in inst.wave_freq:
            y = (n + off) & 0xFF
            if y > 95:
                recs[inst_id].add((off & 0xFF, n,
                                   mem[(flo_addr + y) & 0xFFFF],
                                   mem[(fhi_addr + y) & 0xFFFF]))
                songmap[(inst_id, off & 0xFF, n)].add(si)
                if vi is not None:
                    voicemap[(inst_id, off & 0xFF, n)].add(vi)

    for si, song in enumerate(m.songs):
        for vi, v in enumerate(song.voices):
            # `running` = the instrument whose wave program is LIVE before a
            # row's note-init runs. Notes are FETCHED on a P call (curnote +
            # base update at $11A3-$11B3) but note-init (wave restart) is
            # DEFERRED to the pending frame — an intervening wave-step call
            # ($1591 F entry) steps the OLD program with the NEW curnote. And
            # a SOFT ($7C) row skips note-init entirely, so the old program
            # runs for its whole duration. Both make off-table reads at
            # (old-program offset + new note) — enumerate them too, else the
            # window byte for that idx stays the file-image leftover
            # (Bladeswede: inst-13 noise-arp off 52 + soft note 47 = idx 99
            # reads $170A = V1 track-ptr hi, runtime $1B vs file $00).
            running = None
            for ei, e in enumerate(v.entries):
                tr = v.transposes[ei] if v.transposes else 0
                for r in v.patterns[e]:
                    if r.note is not None:
                        add_note(r.note + tr, r.instr, si, vi)
                        if running is not None and running != r.instr:
                            add_note(r.note + tr, running, si, vi)
                        if not r.soft:
                            running = r.instr
                    if r.glide_to is not None:
                        add_note(r.glide_to + tr, r.instr, si, vi)
    # IDLE-WAVE off-table reads: a voice that starts on rests freewheels the
    # idle wave (m.idle_wave, the cleared-cache path) with curnote = its idle
    # note — and the idle-wave freq offsets + idle note can overshoot the
    # 96-entry table (e.g. Funky_Witch idle_note 50 + offset 51 = idx 101). The
    # per-instrument note loop above never covers the idle path, so capture it
    # here (curnote = each voice's idle note). Records go to instr 0 (always
    # shipped) — the off-table window is instrument-agnostic (idx -> value).
    idle_freq = list(m.idle_wave[1]) if m.idle_wave and m.idle_wave[1] else []
    for cn in set(m.idle_notes):
        for off in idle_freq:
            y = (cn + off) & 0xFF
            if y > 95:
                recs[0].add((off & 0xFF, cn & 0xFF,
                             mem[(flo_addr + y) & 0xFFFF],
                             mem[(fhi_addr + y) & 0xFFFF]))
    for iid, s in recs.items():
        if iid in m.instruments:
            m.instruments[iid].offtable_freq = sorted(s)
    m.offtable_vibdepth = vibovr
    # idle-wave records deliberately get NO songmap entry (their song
    # attribution is imprecise) -> the correction falls back to the
    # start-song sample, exactly the pre-song-aware behavior.
    m.offtable_songs = dict(songmap)
    m.offtable_vib_songs = dict(vibsongs)
    m.offtable_read_voices = dict(voicemap)


def _postinit_values(sid_path: str, addrs, subtune: int | None = None) -> dict:
    """Post-init values of work-RAM bytes via siddump --memwatch (libsidplayfp
    = ground truth). The off-table source bytes live in the engine's work RAM
    AFTER the freq tables; the engine's INIT writes them, so the value the
    original actually READS at runtime is NOT the file-image byte. Capture what
    the engine reads (Core Tenet: observe the writes, don't mirror the
    mechanism). Returns {addr: value} only for bytes CONSTANT across the sample
    (init-written-then-stable -> reproducible); bytes that VARY frame-to-frame
    are genuinely dynamic and omitted (caller keeps the file image; they remain
    honest residue)."""
    if not addrs:
        return {}
    import subprocess
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                      'tools', 'siddump')
    al = sorted(set(a & 0xFFFF for a in addrs))
    st = [] if subtune is None else ['--subtune', str(subtune + 1)]
    try:
        out = subprocess.run(
            [sd, sid_path, '--duration', '6', '--raw', *st,
             '--memwatch', ','.join(f'{a:04X}' for a in al)],
            capture_output=True, text=True, timeout=90).stdout
    except Exception:
        return {}
    seen = {}
    for line in out.splitlines():
        if 'M:' not in line:
            continue
        for tok in line.split('M:')[1].split('|')[0].split(':'):
            if '=' in tok:
                a, v = tok.split('=')
                seen.setdefault(int(a, 16), set()).add(int(v, 16))
    return {a: next(iter(vs)) for a, vs in seen.items() if len(vs) == 1}


def _cpu_peek(sid_path: str, ranges, subtune: int | None = None) -> dict:
    """CPU-EYE post-init bytes via `siddump --peek-post-init` (libsidplayfp =
    ground truth, read THROUGH the MMU): banked-in ROM — including psiddrv's
    PATCHED KERNAL vectors ($FFFC/$FFFD -> the relocated driver entry) — the
    6510 port ($00/$01 = $2F/$37), and the power-on RAM pattern for bytes
    nothing ever wrote. This is exactly what the engine's `LDA ($F8),y`
    returns, which a RAM-only memwatch capture cannot see (it reads the RAM
    under the ROM). `ranges` = [(lo, hi)] inclusive; returns {addr: val}."""
    if not ranges:
        return {}
    import subprocess
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                      'tools', 'siddump')
    st = [] if subtune is None else ['--subtune', str(subtune + 1)]
    spec = ','.join(f'{lo & 0xFFFF:04X}-{hi & 0xFFFF:04X}' for lo, hi in ranges)
    try:
        out = subprocess.run(
            [sd, sid_path, '--raw', *st, '--peek-post-init', spec],
            capture_output=True, text=True, timeout=90).stdout
    except Exception:
        return {}
    vals = {}
    for line in out.splitlines():
        if line.startswith('PEEK:'):
            for tok in line[5:].split(','):
                if '=' in tok:
                    a, v = tok.split('=')
                    vals[int(a, 16)] = int(v, 16)
    return vals


def _correct_offtable_postinit(m: DmcModel, sid_path: str, flo_addr: int,
                               fhi_addr: int, vibdepth_addr: int,
                               song_subtunes: dict | None = None) -> None:
    """Replace the file-image off-table values with the original's POST-INIT
    values (the bytes the engine actually reads). Recovers the
    init-written-then-constant reads that the file-image capture got wrong.

    SUBTUNE-AWARE: the off-table bytes can be per-subtune init state (track-ptr
    slots $1707-$170C, set from the tune record at init — constant within a
    subtune, different across subtunes). Sample post-init values on every
    subtune that REACHES a record (m.offtable_songs) and use that value only
    when all reaching subtunes were sampled and agree; otherwise fall back to
    the START-SONG sample — exactly the pre-song-aware behavior, so records
    reached from the start song (and idle records, which carry no attribution)
    are byte-identical to before.

    COMPILATION-AWARE: `song_subtunes` maps this player's OWN song index to the
    PSID subtune that plays it (ledger C31). A compilation's per-player extract
    numbers songs locally, so sampling file subtune `si` selects a DIFFERENT
    player whose init leaves this player's work RAM at the file-image leftover.
    None (the single-player case) = song index IS the subtune, unchanged."""
    addrs = set()
    for ins in m.instruments.values():
        for off, note, lo, hi in ins.offtable_freq:
            idx = (off + note) & 0xFF
            if idx > 95:
                addrs.add(flo_addr + idx)
                addrs.add(fhi_addr + idx)
    for note in m.offtable_vibdepth:
        addrs.add(vibdepth_addr + note)
    if not addrs:
        return set()
    songmap = getattr(m, 'offtable_songs', {})
    vibsongs = getattr(m, 'offtable_vib_songs', {})
    start_si = max(0, (getattr(m, 'start_song', 1) or 1) - 1)
    need = {start_si}
    for songs in songmap.values():
        need |= songs
    for songs in vibsongs.values():
        need |= songs
    n_songs = max(1, len(m.songs))
    need = {si for si in need if 0 <= si < n_songs}
    def _file_sub(si):
        """This player's song `si` -> the PSID subtune to sample it in."""
        if song_subtunes is None:
            return si
        return song_subtunes.get(si)      # None -> siddump's start song

    post_by_song = {si: _postinit_values(sid_path, addrs, subtune=_file_sub(si))
                    for si in sorted(need)}
    post = post_by_song.get(start_si, {})
    if not any(post_by_song.values()):
        return {a & 0xFFFF for a in addrs}  # siddump failed → all unresolved
    resolved = set()

    def pick(addr, songs):
        a = addr & 0xFFFF
        if songs:
            vals = [post_by_song.get(si, {}).get(a) for si in songs]
            if all(v is not None for v in vals) and len(set(vals)) == 1:
                resolved.add(a)
                return vals[0]
        v = post.get(a)
        if v is not None:
            resolved.add(a)
        return v

    # Per-subtune DISAGREEMENT map: a record whose reaching subtunes were all
    # sampled (byte constant within each) but with DIFFERENT values — one
    # file-level window byte cannot serve them (the track-ptr slots are
    # per-subtune init state: Assassins sub 0 $1709=$80 vs sub 1 $CE). The
    # `pick` fallback keeps the start-song value (sub 0 stays byte-identical);
    # _split_offtable_by_subtune clones the instrument per value-class so the
    # composer's existing per-subtune window patch (ledger C31, `ovr_sub`)
    # serves each subtune its own byte.  {(iid, off, note): {si: (lo, hi)}}
    song_values = {}
    for iid, ins in m.instruments.items():
        new = []
        for off, note, lo, hi in ins.offtable_freq:
            idx = (off + note) & 0xFF
            songs = songmap.get((iid, off, note), ())
            plo = pick(flo_addr + idx, songs)
            phi = pick(fhi_addr + idx, songs)
            if songs and len(songs) > 1:
                la = {si: post_by_song.get(si, {}).get((flo_addr + idx)
                                                       & 0xFFFF)
                      for si in songs}
                ha = {si: post_by_song.get(si, {}).get((fhi_addr + idx)
                                                       & 0xFFFF)
                      for si in songs}
                if (all(v is not None for v in la.values())
                        and all(v is not None for v in ha.values())
                        and (len(set(la.values())) > 1
                             or len(set(ha.values())) > 1)):
                    song_values[(iid, off, note)] = {
                        si: (la[si], ha[si]) for si in sorted(songs)}
            new.append((off, note, lo if plo is None else plo,
                        hi if phi is None else phi))
        ins.offtable_freq = sorted(set(new))
    m.offtable_song_values = song_values
    vd = {}
    for n, d in m.offtable_vibdepth.items():
        v = pick(vibdepth_addr + n, vibsongs.get(n, ()))
        vd[n] = d if v is None else v
    m.offtable_vibdepth = vd
    # addrs whose byte VARIED over the post-init time-sample (unresolved,
    # keeping the file image). These are the candidates for the event-driven
    # correction below: a globally-varying byte can still be STABLE at the moment
    # a given note reads it (e.g. sector-position $1729).
    return {a & 0xFFFF for a in addrs} - resolved


_SL_DB: dict = {}


def _verify_window(sid_path: str) -> float:
    """songlength × 1.1 (the verify window) for the longest subtune, used as the
    event-driven capture duration so every read the verdict checks is observed.
    Falls back to 150s if the Songlengths DB can't be located."""
    root = sid_path
    db_path = None
    for _ in range(8):
        root = os.path.dirname(root)
        cand = os.path.join(root, 'DOCUMENTS', 'Songlengths.md5')
        if os.path.exists(cand):
            db_path = cand
            break
    if db_path is None:
        return 150.0
    if db_path not in _SL_DB:
        from src.songlengths import load_database
        _SL_DB[db_path] = load_database(db_path)
    from src.songlengths import get_durations
    durs = get_durations(sid_path, _SL_DB[db_path])
    return min((max(durs) if durs else 130) * 1.1, 300.0)


def _eventdriven_addrs(cfg) -> tuple:
    """The five 3-voice state-address tuples (Y, CN, INS, BLO, BHI) the
    event-driven capture watches, RELOCATED for `cfg`'s member layout. CN/INS
    are base-relative (canon $1012/$1015 = base+$12/+$15; a located
    `cfg.curnote_addr` overrides the base fallback); Y/BLO/BHI are
    freq-table-relative state-block bytes (canon $1783/$172F/$1732 = freq_hi +
    $DC/$88/$8B — invariant under whole-image relocation, per
    `_canon_state_geometry`). A canon member (base $1000, freq_hi $16A7)
    reproduces the hardcoded canon addresses exactly -> byte-identical. cfg=None
    -> canon (kept for callers without a config)."""
    if cfg is None:
        return ((0x1783, 0x1784, 0x1785), (0x1012, 0x1013, 0x1014),
                (0x1015, 0x1016, 0x1017), (0x172F, 0x1730, 0x1731),
                (0x1732, 0x1733, 0x1734))
    cn = cfg.curnote_addr if getattr(cfg, 'curnote_addr', None) is not None \
        else cfg.base + 0x12
    fh = cfg.freq_hi_addr
    return (tuple((fh + 0xDC + x) & 0xFFFF for x in range(3)),   # Y
            tuple((cn + x) & 0xFFFF for x in range(3)),          # CN
            tuple((cn + 3 + x) & 0xFFFF for x in range(3)),      # INS
            tuple((fh + 0x88 + x) & 0xFFFF for x in range(3)),   # BLO
            tuple((fh + 0x8B + x) & 0xFFFF for x in range(3)))   # BHI


def _offtable_eventdriven(sid_path: str, duration: float, cfg=None,
                          subtune: int | None = None) -> dict:
    """EVENT-DRIVEN off-table capture: record the value each off-table freq read
    produces AT THE ACCESS, keyed by `(inst, off, note)`. Recovers reads on a
    byte that varies GLOBALLY but is STABLE when this note reads it (the
    file-image / post-init-constant captures both miss these).

    The engine computes each voice's freq base into `$172F/$1732,x` from the
    (possibly off-table) index `$1783,x = curnote + wave_offset`. Snapshot all
    three voices' `(y, curnote, inst, base_lo, base_hi)` at every `$D416` write
    (once per play() — CIA-safe, per-play() not per-frame). Returns
    `{(inst, off, note): (lo, hi)}` for keys whose value is the SAME across every
    occurrence; keys that vary are omitted (they stay honest residue).

    RELOCATION/COMPILATION-AWARE (ledger C31): the watched addresses are derived
    from `cfg` (see `_eventdriven_addrs`) and the capture runs `subtune` — a
    packed player's per-player extract MUST run the file subtune that SELECTS it,
    else the capture reads the START player's off-table results (its own state
    block sits at the file-image leftover) and overwrites correct records."""
    import subprocess
    import re
    from collections import defaultdict
    sd = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..',
                      'tools', 'siddump')
    Y, CN, INS, BLO, BHI = _eventdriven_addrs(cfg)
    addrs = Y + CN + INS + BLO + BHI
    st = [] if subtune is None else ['--subtune', str(subtune + 1)]
    try:
        out = subprocess.run(
            [sd, sid_path, '--duration', str(int(duration)), *st,
             '--memwatch-on-write', 'D416',
             ','.join(f'{a:04X}' for a in addrs)],
            capture_output=True, text=True, timeout=int(duration) + 120).stdout
    except Exception:
        return {}
    pat = re.compile(r'([0-9A-F]{4})=([0-9A-F]+)')
    vals = defaultdict(set)
    for line in out.splitlines():
        if '|E' not in line:
            continue
        for ev in line.split('|'):
            if not ev.startswith('E'):
                continue
            d = {a: int(v, 16) for a, v in pat.findall(ev)}
            for x in range(3):
                y = d.get(f'{Y[x]:04X}')
                if y is None or y < 96:            # in-table read: not off-table
                    continue
                cn = d.get(f'{CN[x]:04X}', 0)
                blo = d.get(f'{BLO[x]:04X}')
                bhi = d.get(f'{BHI[x]:04X}')
                if blo is None or bhi is None:
                    continue
                key = (d.get(f'{INS[x]:04X}', 0), (y - cn) & 0xFF, cn & 0xFF)
                vals[key].add((blo, bhi))
    return {k: next(iter(vs)) for k, vs in vals.items() if len(vs) == 1}


def _canon_state_geometry(mem, cfg) -> bool:
    """True iff the member keeps its per-voice state block at the CANON offset
    from its freq tables (the premise of the composer's off-table redirect map
    + the sectpos shadow: window idx N = the canon state var at fhi+N).
    Static opcode probe (C19): the canon player DECs its per-voice duration
    counter every tick via `DEC $173B,x` ($10BD) — expect `DE lo hi` with
    addr = freq_hi + ($173B − $16A7) somewhere in the player image. Variant
    builds that moved the state (e.g. to $03xx) DEC a different address.
    Fail-open: a stray data match keeps today's behavior (redirect on)."""
    dur = (cfg.freq_hi_addr + (0x173B - 0x16A7)) & 0xFFFF
    pat = bytes((0xDE, dur & 0xFF, dur >> 8))
    lo = max(0, cfg.base)
    return pat in bytes(mem[lo:min(0x10000, lo + 0x4000)])


def _redirect_mapped_idx() -> set:
    """The off-table freq idx positions the composer serves from a LIVE redirect
    var (DMC_OFFTABLE_STATE), not the static window. A read landing there reads
    the tracked var, and its static window value is used only to SEED that var at
    init (round-25 gla/glb) — which must be the file-image LEFTOVER, never the
    deep runtime value. So the event-driven correction must skip these idx (a
    runtime override there breaks the seed — the Calimero regression)."""
    from pipelines.dmc.composer_asm import (DMC_OFFTABLE_STATE,
                                            DMC_SECTPOS_ROW, ORIG_FHI)
    return {(addr + k - ORIG_FHI) & 0xFF
            for addr, _label, n in DMC_OFFTABLE_STATE + [DMC_SECTPOS_ROW]
            for k in range(n)}


def _correct_offtable_eventdriven(m: DmcModel, sid_path: str, cfg=None,
                                  file_subtunes=None,
                                  create_notes=frozenset()) -> None:
    """Override off-table records with the event-driven read-moment value where
    it is STABLE per `(inst, off, note)`, EXCEPT positions the composer serves
    from a live redirect var (those are live-tracked + seeded from the leftover,
    so the static value must stay the file image — see `_redirect_mapped_idx`).
    Canon-geometry members only (the caller gates on `_canon_state_geometry`;
    the capture memwatches the member's (relocated) state addresses).
    On the remaining (window-served) positions this is regression-safe: a FULL
    member's reads already match, so the read-moment value equals the record → no
    change; only currently-wrong reads move. A key that VARIES is not in `ev`.

    COMPILATION-AWARE (ledger C31): `file_subtunes` are the PSID subtunes that
    select THIS packed player (one per song it plays); the capture runs each and
    keeps a key only where every run that saw it agrees. None -> the start song
    (single-player: the player IS the start song)."""
    dur = _verify_window(sid_path)
    subs = list(file_subtunes) if file_subtunes else [None]
    ev, conflict = {}, set()
    for su in subs:
        cap = _offtable_eventdriven(sid_path, dur, cfg=cfg, subtune=su)
        for k, v in cap.items():
            if k in ev and ev[k] != v:
                conflict.add(k)
            else:
                ev[k] = v
    for k in conflict:
        ev.pop(k, None)
    if not ev:
        return
    mapped = _redirect_mapped_idx()
    for iid, ins in m.instruments.items():
        changed = False
        new = []
        for off, note, lo, hi in ins.offtable_freq:
            rv = ev.get((iid, off & 0xFF, note & 0xFF))
            if (off + note) & 0xFF not in mapped and rv is not None \
                    and rv != (lo, hi):
                new.append((off, note, rv[0], rv[1])); changed = True
            else:
                new.append((off, note, lo, hi))
        # CREATION (r116, glide-arrival reach — see the extract() gate): a
        # stable observed key the static model missed becomes a record,
        # restricted to glide-target notes and to offsets this instrument
        # actually steps (its wave_freq offsets, or 0 = the base read) —
        # snapshot-skew keys (y/cn sampled across a reload) fail the offset
        # test. Wavepos reads (idx 211-213) stay with the layout machinery.
        if create_notes:
            offs = {o & 0xFF for o in ins.wave_freq} | {0}
            have = {(o & 0xFF, n & 0xFF) for o, n, *_r in ins.offtable_freq}
            for (ki, ko, kn), (lo, hi) in ev.items():
                idx = (ko + kn) & 0xFF
                if (ki != iid or kn not in create_notes or ko not in offs
                        or (ko, kn) in have or idx < 96
                        or 211 <= idx <= 213):
                    continue
                new.append((ko, kn, lo, hi)); changed = True
        if changed:
            ins.offtable_freq = sorted(set(new))
