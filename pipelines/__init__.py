"""SIDfinity pipelines: per-engine end-to-end SID rebuild paths.

Each pipeline lives in its own subpackage (commando, monty, ...) and is
fully self-contained: extraction (Python, reads original SID → emits USF
data as Lean source) plus codegen (Lean, USF → rebuilt SID).
"""
