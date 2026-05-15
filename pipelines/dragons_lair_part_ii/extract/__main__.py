"""Run `python -m pipelines.dragons_lair_part_ii.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
