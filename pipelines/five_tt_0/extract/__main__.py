"""Run `python -m pipelines.five_tt_0.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
