"""
adapters.usf_text — Human-readable text formatting for USF token lists.

to_text(tokens) -> formatted string with indentation and line breaks.
"""


def to_text(tokens):
    """Convert token list to readable text with line breaks."""
    lines = []
    indent = 0
    line = []

    for t in tokens:
        if t.startswith('/'):
            if line:
                lines.append('  ' * indent + ' '.join(line))
                line = []
            indent = max(0, indent - 1)
            lines.append('  ' * indent + t)
        elif t in ('SONG', 'INST', 'ORD') or t.startswith('PAT') or (t.startswith('V') and len(t) == 2):
            if line:
                lines.append('  ' * indent + ' '.join(line))
                line = []
            lines.append('  ' * indent + t)
            indent += 1
        else:
            line.append(t)

    if line:
        lines.append('  ' * indent + ' '.join(line))

    return '\n'.join(lines)
