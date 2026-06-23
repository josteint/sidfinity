#!/usr/bin/env python3
"""Capture survey for the Basic_Program family (486 RSID-BASIC tunes).

For each tune: run `siddump --writelog` TWICE (ROM-enabled build) at
min(songlength*1.1, CAP) seconds, then record:
  - n_writes / distinct regs / freq-writes / gate-writes  (richness)
  - deterministic: run1 (reg,val) stream == run2's            (correctness)
  - classification: music / no_voice / silent

Purpose (research, not the verdict): prove run-to-run determinism across the
whole family and find the curatorial "no music without keypress" set (a subset
of the 81 GET play-along tunes). Output -> tmp/basic_program_research/survey.jsonl
"""
import json, os, re, subprocess, sys
from concurrent.futures import ProcessPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SIDDUMP = os.path.join(ROOT, "tools", "siddump")
OUT = os.path.join(ROOT, "tmp", "basic_program_research", "survey.jsonl")
CAP = 30.0          # seconds cap for the survey (triage, not the verdict)
FREQ_REGS = {0x00, 0x01, 0x07, 0x08, 0x0e, 0x0f}
GATE_REGS = {0x04, 0x0b, 0x12}   # voice ctrl regs (carry the gate bit)

def capture(path, dur):
    """Return the ordered list of (reg,val) pairs from one writelog run."""
    try:
        r = subprocess.run([SIDDUMP, path, "--writelog", "--duration", f"{dur:.1f}"],
                           capture_output=True, text=True, timeout=max(60, dur*6))
    except subprocess.TimeoutExpired:
        return None
    pairs = []
    for tok in re.findall(r'\|W:([0-9a-f:]+)', r.stdout):
        f = tok.split(":")
        # repeating triples cycle:reg:val
        for i in range(0, len(f) - 2, 3):
            try:
                reg = int(f[i+1], 16); val = int(f[i+2], 16)
            except ValueError:
                continue
            pairs.append((reg, val))
    return pairs

def survey_one(args):
    relpath, songlen = args
    abspath = os.path.join(ROOT, "hvsc84", relpath)
    dur = min((songlen or 10.0) * 1.1, CAP)
    a = capture(abspath, dur)
    b = capture(abspath, dur)
    if a is None or b is None:
        return {"path": relpath, "error": "timeout"}
    regs = {r for r, _ in a}
    freq_w = sum(1 for r, _ in a if r in FREQ_REGS)
    gate_w = sum(1 for r, _ in a if r in GATE_REGS)
    deterministic = (a == b)
    if freq_w > 0 and gate_w > 0 and len(a) >= 8:
        cls = "music"
    elif len(a) <= 2:
        cls = "silent"
    else:
        cls = "no_voice"
    return {"path": relpath, "dur": round(dur, 1), "n_writes": len(a),
            "n_regs": len(regs), "freq_writes": freq_w, "gate_writes": gate_w,
            "deterministic": deterministic, "cls": cls}

def main():
    rows = subprocess.run(
        ["duckdb", "-noheader", "-list", "-c",
         "SELECT path, COALESCE(songlength_s,10) FROM read_csv('%s/hvsc84.csv',"
         "header=true,nullstr='',escape='\"') WHERE engine='Basic_Program' ORDER BY path"
         % ROOT],
        capture_output=True, text=True).stdout.strip().split("\n")
    work = []
    for r in rows:
        if not r:
            continue
        p, sl = r.rsplit("|", 1)
        work.append((p, float(sl)))
    print(f"surveying {len(work)} tunes (cap {CAP}s, x2 for determinism)", flush=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    done = 0
    with open(OUT, "w") as fo, ProcessPoolExecutor(max_workers=8) as ex:
        for res in ex.map(survey_one, work):
            fo.write(json.dumps(res) + "\n"); fo.flush()
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(work)}", flush=True)
    print(f"done -> {OUT}", flush=True)

if __name__ == "__main__":
    main()
