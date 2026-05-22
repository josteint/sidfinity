"""Run `python -m pipelines.last_v8_c128.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
