"""Run `python -m pipelines.gremlins.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
