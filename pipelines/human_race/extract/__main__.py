"""Run `python -m pipelines.human_race.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
