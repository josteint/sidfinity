"""Run `python -m pipelines.thing_on_a_spring.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
