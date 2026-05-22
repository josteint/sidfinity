"""Run `python -m pipelines.confuzion.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
