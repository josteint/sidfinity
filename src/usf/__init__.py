"""
usf — Universal Symbolic Format for SID music.

Re-exports all public names from usf.format, plus tokenize/detokenize/to_text
from the adapters package, so existing code like `from usf import Song` keeps working.
"""

# Data structures and helpers (no circular dependency risk)
from usf.format import (
    Song, Instrument, WaveTableStep, PulseTableStep, FilterTableStep,
    SpeedTableEntry, Pattern, NoteEvent,
    CMD_NONE, CMD_PORTA_UP, CMD_PORTA_DOWN, CMD_TONE_PORTA, CMD_VIBRATO,
    CMD_SET_AD, CMD_SET_SR, CMD_SET_WAVE, CMD_SET_WAVEPTR, CMD_SET_PULPTR,
    CMD_SET_FILTPTR, CMD_SET_FILTCTL, CMD_SET_FILTCUT, CMD_SET_MASTERVOL,
    CMD_FUNKTEMPO, CMD_SET_TEMPO,
    NOTE_NAMES, WAVEFORM_NAMES, WAVEFORM_TOKENS,
    note_name, note_from_name, usf_to_json,
)


def __getattr__(name):
    """Lazy import for adapter functions to avoid circular imports."""
    if name == 'tokenize':
        from adapters.usf_tokens import tokenize
        return tokenize
    if name == 'detokenize':
        from adapters.usf_tokens import detokenize
        return detokenize
    if name == 'to_text':
        from adapters.usf_text import to_text
        return to_text
    raise AttributeError(f"module 'usf' has no attribute {name!r}")
