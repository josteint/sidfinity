"""Run `python -m pipelines.rasputin.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
