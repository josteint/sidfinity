"""Run `python -m pipelines.monty.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
