"""Run `python -m pipelines.master_of_magic.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
