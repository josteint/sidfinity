"""Run `python -m pipelines.one_man_and_his_droid.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
