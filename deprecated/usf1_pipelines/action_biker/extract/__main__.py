"""Run `python -m pipelines.action_biker.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
