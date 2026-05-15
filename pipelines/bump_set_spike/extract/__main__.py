"""Run `python -m pipelines.bump_set_spike.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
