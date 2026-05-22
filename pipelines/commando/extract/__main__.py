"""Run `python -m pipelines.commando.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
