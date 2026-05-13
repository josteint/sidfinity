"""Run `python -m pipelines.five_title_tunes.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
