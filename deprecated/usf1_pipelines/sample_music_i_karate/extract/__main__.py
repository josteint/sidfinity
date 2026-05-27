"""Run `python -m pipelines.sample_music_i_karate.extract` → dispatch to cli."""
from .cli import main
import sys

sys.exit(main())
