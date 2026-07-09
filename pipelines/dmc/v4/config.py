"""DMC V4 per-SID extract config.

The DMC editor's packer patches the player's absolute data-table
operands per song (see pipelines/dmc/v4/disassembly.s — KEY FINDING).
The config therefore carries the CODE OFFSETS of the operand sites,
and the extract reads the actual table addresses from the binary by
dataflow. Only the freq tables, the instrument base and the per-note
vibrato-depth table are fixed (code-addressed).

All offsets are relative to the load address (= $1000 for the
standard family-1 layout; the operand sites are code positions and
move only if the player code itself is shifted, which the factory
must detect).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DMCV4Config:
    sid_path: str                     # HVSC-relative path
    name: str = ''
    # player base address. Canonical = $1000; relocated members carry
    # the same engine at a different base (operand sites + fixed tables
    # all shift by base - $1000). Extract reads from the relocated
    # addresses; the composer always emits OUR engine at $1000, so the
    # rebuild + verdict are base-independent (relocation is extract-only).
    base: int = 0x1000
    # operand sites (address of the abs,y operand low byte)
    op_instr: int = 0x1227            # instrument records (always $18F0)
    op_wavectrl: int = 0x159C         # wave table CTRL array
    op_wavefreq: int = 0x15B9         # wave table FREQ array
    op_filtdef: int = 0x1296          # filter definition table
    op_tunetab: int = 0x180E          # tune pointer records
    op_secp_lo: int = 0x1103          # sector pointer table LO
    op_secp_hi: int = 0x1108          # sector pointer table HI
    # fixed (code-addressed) tables
    freq_lo_addr: int = 0x1647
    freq_hi_addr: int = 0x16A7
    vibdepth_addr: int = 0x1888       # per-note vibrato depth (96 bytes,
                                      # first 6 overlap player code)
    d417_shadow_addr: int = 0x1018    # routing shadow — NOT cleared by
                                      # init; file-image leftover primes
                                      # the play stream's $D417 writes
    # Per-voice STATE blocks whose file-image initial values are the idle note
    # / idle gate-mask a resting (gate-off, freewheeling) voice uses. Canon:
    # curnote $1012, gatemask $100F (= base+0x12 / base+0x0F). A re-assembled
    # variant lays them out differently; the dataflow extractor LOCATES them
    # (None => fall back to the canon base offset in extract).
    curnote_addr: int = None
    gatemask_addr: int = None
    # The $40 dual-effect GLOBAL half-rate parity byte (canon $1019). Its
    # file-image leftover seeds slide_phase; a shifted body moves it
    # (Staring_at_the_Ceiling: $101A). None => canon base+0x19.
    dual_parity_addr: int = None
    # Track-loop variant (factory-probed): the canonical player's $FF
    # loops to track position 0; the JSR-$1042 hook variant reads the
    # NEXT track byte as the loop position ($FF nn).
    track_loop_target: bool = False
    # RESET-ALL-to-N hook (dataflow-probed, ledger C13): a $FF handler that
    # writes the SAME immediate N to all three voices' track-pos ($1726/7/8) =
    # a synchronized loop to track position N. None = not this form (use
    # track_loop_target). N==0 is left as None and handled by the loop-to-0
    # path (track_loop_target=False) for byte-identity with the round-53
    # reset-all-to-0 carriers; only N>0 sets this field.
    loop_reset_pos: int = None
    # Sector-command byte map (factory-probed). 'v4' = canonical
    # (terminator $7F, VOL $F0+, soft-start $7C); 'family2' = the
    # V4-derived variant (terminator $FF, no VOL/soft-start, instr range
    # extended to $7F). See pipelines/dmc/v4/extract/engine_model._SECFMT.
    sector_format: str = 'v4'
    # CIA multispeed (factory-probed): when the PSID play() is driven by
    # a CIA1 timer A (a multispeed wrapper at 2-6x), this is the timer
    # latch the original programs ($DC04/$DC05, read by running init in
    # py65). The composer sets the PSID speed bit + programs the SAME
    # latch so libsidplayfp drives our play() at the identical rate.
    # 0 = single-speed VBI.
    cia_period: int = 0
    # INTERNAL multispeed (vblank, NO PSID speed bit): the PSID play vector
    # points to a wrapper that does N x `JSR <play>` then RTS, so one VBI runs
    # the engine N times. The composer emits the same N-fold play. 1 = once.
    play_repeat: int = 1
    # Factory-probed engine write-stream params merged into USF params
    # (the family-2 build knobs: cymbal_onset / vib_ramp / hold_gateoff /
    # hard_restart / rest_effects). Family-2 sub-builds differ in some of
    # these (e.g. the holding gate-off: mask-only vs an AD/SR-clearing
    # helper), so the factory probes each from the member's code rather
    # than hardcoding. Empty for canonical V4 (canon defaults apply).
    extra_params: dict = field(default_factory=dict)
    # INIT-UNPACKER member (factory-detected): every data-table operand
    # points outside the loaded image — init GENERATES the song data in
    # high RAM. The extract must read its tables from post-init RAM
    # (py65 init run), not the file image. Extract-only (never USF).
    data_post_init: bool = False
    # Hand-crafted init WRAPPER that HARD-FORCES the played tune record
    # (factory-probed `LDA #imm` prefix, ledger C19). Sans_intro: init $0FFE =
    # `A9 01` falling through to base $1000 (JMP $101D = tune-select), so every
    # play forces record 1 regardless of the PSID song number — but record 0 is
    # a dummy (V1/V2 tracks = $FE stop). None = the PSID subtune indexes the
    # record normally (walk record = sub index). Extract-only: the composer
    # plays the walked content; the forced index is an engine artifact, not USF.
    forced_subtune: int = None
    # POST-INIT leftover values (dataflow/re-assembled members only; None =
    # read the file image). Canon's leftover priming (d417 shadow, idle
    # notes/masks, dual phase) reads the FILE IMAGE because canon init never
    # touches those bytes — but a re-assembled init MAY clear/rewrite them
    # (Scalework's init clears its $1017 route shadow), so the factory runs
    # the member's init in py65 and captures the values the play loop
    # actually starts from. Keys: 'd417_shadow', 'idle_notes', 'idle_masks',
    # 'dual_phase'. Extract-only (never USF).
    post_init_state: dict = None


ZAKS = DMCV4Config(
    sid_path='MUSICIANS/A/Amadeus_Slash_Design/Geometrical_Zaks.sid',
    name='geometrical_zaks',
)
