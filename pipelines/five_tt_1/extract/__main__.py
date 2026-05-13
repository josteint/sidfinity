"""Run `python -m pipelines.five_tt_1.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
