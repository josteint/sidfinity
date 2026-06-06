"""Shared plumbing for engine composers.

Mechanism-level helpers that every engine family uses identically:
xa65 invocation, PSID header construction, etc. These are deliberately
small and engine-blind — adding engine logic here is a smell.

The §8 "composer is engine-blind" principle (docs/usf_representation_principle.md)
binds individual emitters; this module is even further from engine
identity — it's pure mechanism shared across families.
"""
from src.composer_runtime.xa65 import assemble
from src.composer_runtime.psid import build_header

__all__ = ['assemble', 'build_header']
