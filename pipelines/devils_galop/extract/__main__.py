"""Run `python -m pipelines.devils_galop.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
