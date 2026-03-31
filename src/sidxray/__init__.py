"""
sidxray — Reverse-engineer any SID player by observing it run.

Uses siddump --memtrace to capture every memory read the player makes,
then analyzes the access patterns to identify data structures:
instrument tables, wave/pulse/filter tables, pattern data, orderlists,
frequency tables, and more.

Works for ANY player — GoatTracker, DMC, JCH, Hubbard, all 642 engines.
"""
