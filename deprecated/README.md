# Deprecated Code

Files moved here are from earlier development phases. They worked at
the time but have been superseded by the current USF pipeline. The
production build path now lives at:

  `pipelines/<family>/<engine>/extract/to_usf.py` (binary → USF)
  → `pipelines/build_from_usf.py` (USF → SID via `pipelines/composer.py`)

See `CLAUDE.md` for the full architecture. Each subdirectory below
has its own README explaining what the code did and why it was
deprecated.
