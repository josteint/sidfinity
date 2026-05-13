"""Run `python -m pipelines.five_tt_4.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
