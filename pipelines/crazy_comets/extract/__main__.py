"""Run `python -m pipelines.crazy_comets.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
