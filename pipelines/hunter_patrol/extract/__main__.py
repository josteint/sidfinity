"""Run `python -m pipelines.hunter_patrol.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
