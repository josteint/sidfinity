"""5 Title Tunes (1985) — multi-binary wrapper.

This pipeline is structurally different from a normal Hubbard rebuild:
the original SID is a dispatcher (init $0B10, play $0B40) that forwards
to one of 5 separate Hubbard sub-binaries. We rebuild each sub via its
own sub-pipeline (`pipelines/five_tt_0` ... `pipelines/five_tt_4`),
then `combine.py` overlays the 5 V3 binaries into the parent's address
space and patches the dispatcher's 10 JSR targets to point at our V3
init/play addresses.
"""
