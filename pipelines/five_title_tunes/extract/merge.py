"""Merge 5 ExtractedSong sub-songs into one idiomatic merged ExtractedSong.

5 Title Tunes is the only multi-binary Hubbard SID — its parent PSID
dispatches to 5 separate Hubbard player binaries. To present it as
ONE USFSong with 5 USFSubtune records (matching how Commando + Monty
look in USF), we walk each sub's ExtractedSong and merge their
instrument + pattern lists into one, rewriting orderlist indices and
per-note instrument refs accordingly.

The hard constraint is the pattern-data bit-packing: the runtime inst
byte stores the instrument index in 5 bits (max 32) plus 3 flag bits.
5 Title Tunes' subs together have 38 instruments → won't fit naively.
Dedup strategy:

  1. Drop any instrument never referenced by a pattern note (saves 2:
     sub 0 inst 3 and sub 4 inst 3 are extracted but never used).
  2. Fold strict byte-for-byte duplicates across subs (e.g. two subs'
     drum instruments with identical waveform / envelope / arp).
  3. Fold "vibrato twins" — instruments identical in every musical
     parameter except vibrato_scale. The fidelity loss is one vibrato
     variant collapsed into another; instruments meant to sound the
     same become the same instrument.

If these three rules don't get us to ≤32, we fall back to PWM-speed
folding: instruments identical except for pwm.init_pw OR pwm.speed get
collapsed. This is a more meaningful audible compromise.
"""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO))

from pipelines.commando.extract.types import (
    Envelope, ExtractedSong, Instrument, Note, PWMConfig, Score, Voice,
    Waveform,
)

MAX_INSTRUMENTS_PER_USF = 32  # 5-bit field in pattern data inst byte


def _strict_key(i: Instrument) -> tuple:
    """Byte-for-byte instrument equivalence."""
    return (
        tuple(i.waveform.steps), i.waveform.loop,
        i.pwm.speed, i.pwm.mode, i.pwm.min_hi, i.pwm.max_hi, i.pwm.init_pw,
        i.envelope.ad, i.envelope.sr,
        i.arp_offset, i.vibrato_scale, i.has_bit0,
    )


def _no_vib_key(i: Instrument) -> tuple:
    """Equivalence ignoring vibrato_scale."""
    return (
        tuple(i.waveform.steps), i.waveform.loop,
        i.pwm.speed, i.pwm.mode, i.pwm.min_hi, i.pwm.max_hi, i.pwm.init_pw,
        i.envelope.ad, i.envelope.sr,
        i.arp_offset, i.has_bit0,
    )


def _no_pw_init_key(i: Instrument) -> tuple:
    """Equivalence ignoring pwm.init_pw + pwm.speed too."""
    return (
        tuple(i.waveform.steps), i.waveform.loop,
        i.pwm.mode,
        i.envelope.ad, i.envelope.sr,
        i.arp_offset, i.has_bit0,
    )


def _coarse_key(i: Instrument) -> tuple:
    """Coarsest equivalence: same waveform + envelope + arp/drum role.
    Ignores all PWM details and vibrato. Used as last-resort fold."""
    return (
        i.waveform.steps[0], i.waveform.loop,
        i.envelope.ad, i.envelope.sr,
        i.arp_offset, i.has_bit0,
    )


def _count_usage(song: ExtractedSong) -> dict[int, int]:
    """Return {inst_id: number of notes referencing it} for one sub."""
    counts: dict[int, int] = {}
    for v in song.score.voices:
        for pat_idx, notes in v.patterns.items():
            for n in notes:
                inst_idx = n.instrument & 0x1F   # 5-bit field
                counts[inst_idx] = counts.get(inst_idx, 0) + 1
    return counts


def merge(subs: list[ExtractedSong]) -> ExtractedSong:
    """Merge N sub-songs into one. Returns an ExtractedSong with one
    `voices` list of (sum(3) per sub) entries. The caller (emit_usf)
    wraps each group of 3 in a USFSubtune."""
    n_subs = len(subs)

    # ── Step 1: dedup ────────────────────────────────────────────────────
    # Walk sub-by-sub. For each instrument, look up its dedup key. If
    # we've already seen an equivalent one, map this (sub, idx) to that
    # canonical merged-index. Otherwise add as new.
    #
    # Tier 1: drop instruments that have 0 usages in THEIR sub's patterns.
    # Tier 2: strict-key dedup.
    # Tier 3 (if still > 32): no-vib dedup.
    # Tier 4 (if still > 32): no-pw-init dedup.

    usages = [_count_usage(s) for s in subs]
    merged_instruments: list[Instrument] = []
    keys_seen: dict[tuple, int] = {}
    remap: dict[tuple[int, int], int] = {}  # (sub_idx, sub_local_inst_idx) -> merged_idx

    for tier, keyfn in [
        ('strict', _strict_key),
        ('no_vib', _no_vib_key),
        ('no_pw_init', _no_pw_init_key),
        ('coarse', _coarse_key),
    ]:
        # Reset and retry from scratch with looser key if we overshoot.
        merged_instruments.clear()
        keys_seen.clear()
        remap.clear()
        for sub_idx, sub in enumerate(subs):
            for local_idx, inst in enumerate(sub.instruments):
                # Skip unused (Tier 1)
                if usages[sub_idx].get(local_idx, 0) == 0:
                    # Map unused inst to a stable canonical (instrument 0)
                    # — won't be referenced anyway. Pick merged index 0
                    # arbitrarily; nothing references it.
                    remap[(sub_idx, local_idx)] = 0 if merged_instruments else None
                    continue
                k = keyfn(inst)
                if k in keys_seen:
                    remap[(sub_idx, local_idx)] = keys_seen[k]
                    continue
                keys_seen[k] = len(merged_instruments)
                remap[(sub_idx, local_idx)] = len(merged_instruments)
                merged_instruments.append(inst)
        if len(merged_instruments) <= MAX_INSTRUMENTS_PER_USF:
            print(f'[merge] dedup tier={tier!r} → {len(merged_instruments)} unique instruments',
                  file=sys.stderr)
            break
    else:
        raise ValueError(
            f'After all dedup tiers, still {len(merged_instruments)} '
            f'instruments — > {MAX_INSTRUMENTS_PER_USF} cap'
        )

    # Replace stub unused remappings (None) with 0 (won't be referenced)
    for k, v in list(remap.items()):
        if v is None:
            remap[k] = 0

    # ── Step 2: merge patterns ──────────────────────────────────────────
    # Each sub has its own (pat_idx → notes) dict, possibly shared across
    # its voices. We rewrite each note's instrument byte to use the merged
    # inst index. Pattern indices get renumbered globally.
    merged_pat_dict: dict[int, list[Note]] = {}
    pat_remap: dict[tuple[int, int], int] = {}  # (sub_idx, sub_local_pat_idx) -> merged_pat_idx

    for sub_idx, sub in enumerate(subs):
        seen_pat_idxs: set[int] = set()
        for v in sub.score.voices:
            for pat_idx, notes in v.patterns.items():
                if (sub_idx, pat_idx) in pat_remap:
                    continue
                if pat_idx in seen_pat_idxs:
                    continue
                seen_pat_idxs.add(pat_idx)
                # Rewrite notes
                new_notes: list[Note] = []
                for n in notes:
                    inst_idx = n.instrument & 0x1F
                    flags    = n.instrument & 0xE0
                    new_merged_idx = remap[(sub_idx, inst_idx)]
                    if new_merged_idx >= 0x20:
                        raise ValueError(
                            f'merged inst idx {new_merged_idx} ≥ 32 — '
                            f'sub {sub_idx} note refs inst {inst_idx}'
                        )
                    new_n = replace(n, instrument=new_merged_idx | flags)
                    new_notes.append(new_n)
                merged_idx = len(merged_pat_dict)
                merged_pat_dict[merged_idx] = new_notes
                pat_remap[(sub_idx, pat_idx)] = merged_idx

    # ── Step 3: merge voices into one list (5 subs × 3 voices = 15) ─────
    merged_voices: list[Voice] = []
    subtune_tempos: list[int] = []
    for sub_idx, sub in enumerate(subs):
        subtune_tempos.append(sub.score.tempo)
        for v in sub.score.voices:
            new_orderlist = [pat_remap[(sub_idx, pi)] for pi in v.orderlist]
            # patterns dict for this voice = the patterns it actually uses,
            # but renumbered. emit_usf assembles the global pattern list
            # from merged_pat_dict directly; voices' patterns dict is just
            # a per-voice copy.
            new_patterns = {
                pat_remap[(sub_idx, pi)]: merged_pat_dict[pat_remap[(sub_idx, pi)]]
                for pi in v.patterns.keys()
            }
            merged_voices.append(Voice(
                orderlist=new_orderlist,
                patterns=new_patterns,
                loop=v.loop,
            ))

    # ── Step 4: pick a freq table ───────────────────────────────────────
    # Standard PAL (pitches 0-95) is identical across all 5 subs (and is
    # the standard freq table). Extended pitches (96+) are unused in 5TT
    # (verified empirically) so sub 0's freq table is fine.
    merged_freq_table = subs[0].freq_table

    # Combine all tempos into a single Score. The caller (emit_usf)
    # interprets the voices in groups of 3 as subtunes with the
    # corresponding tempo from `subtune_tempos`.
    merged_score = Score(
        tempo=subtune_tempos[0],  # primary tempo; per-subtune tempos via attr
        voices=merged_voices,
    )
    # Stash subtune_tempos on the score for the caller (mutable dataclass)
    merged_score.subtune_tempos = subtune_tempos  # type: ignore[attr-defined]

    return ExtractedSong(
        freq_table=merged_freq_table,
        instruments=merged_instruments,
        score=merged_score,
    )
