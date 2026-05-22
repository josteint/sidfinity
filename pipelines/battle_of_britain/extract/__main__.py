"""Run `python -m pipelines.battle_of_britain.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
