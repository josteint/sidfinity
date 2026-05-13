"""Run `python -m pipelines.chimera.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
