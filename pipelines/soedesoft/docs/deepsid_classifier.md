# DeepSID Sub-Classifier: SoedeSoft / Soundmaster

**Provenance:** Derived by reading
`tmp/dmc_hunt/DeepSID/utility/python/specific/soedesoft.py` (read-only)
and the surrounding DeepSID utility harness.
Date: 2026-06-13.

---

## What the classifier does (source: soedesoft.py)

The script is one of many in the DeepSID `specific/` batch pipeline.
It reads a pre-built `_specific.csv` file (generated externally by running
`sidid` over the full HVSC tree — that CSV is NOT stored in the repo)
and filters it to emit a `soedesoft.csv` containing only SoedeSoft
sub-variant labels.

**Full logic of soedesoft.py (verbatim):**

```python
with open('_specific.csv', 'r', encoding='utf-8') as f:
    content = f.readlines()

with open('soedesoft.csv', 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    prev_line = ''
    for line in content:
        if '(Soundmaster_' in line:
            writer.writerow([
                '_High Voltage SID Collection/' + prev_line[0:prev_line.find('.sid') + 4],
                'SoedeSoft/' + line[line.find('(') + 1 : line.find(')')]
            ])
        prev_line = line
```

**Key observations:**

1. **Filter token:** `(Soundmaster_` — only sidid sub-variant lines
   containing that exact prefix are captured.  The parent engine name
   `SoedeSoft` (the line that names the engine) is NOT itself written
   into the CSV; only the sub-variant parenthetical lines are.

2. **Two-line sliding window:** `prev_line` holds the SID path
   (the `*.sid` filename emitted by sidid on the line *before* the
   variant label), and `line` holds the variant label.  This mirrors
   sidid's output convention: the SID path comes first, then the
   matched signature label follows on the next line.

3. **Output columns:**
   - Column 0: `_High Voltage SID Collection/<path>.sid`
   - Column 1: `SoedeSoft/<variant>` — e.g. `SoedeSoft/Soundmaster_V1.0`,
     `SoedeSoft/Soundmaster_V3.1`, `SoedeSoft/Soundmaster_V3.2`.

4. **What is NOT captured:**  Any SoedeSoft SID matched by sidid at the
   engine level ONLY (no matching sub-variant — i.e. no `(Soundmaster_…)`
   line follows) will appear in the DB as plain `SoedeSoft` without a
   sub-version label.  That is the majority of the 929 tunes.

5. **The classification signal is entirely sidid's byte-pattern match**
   (see `sidid_signature_analysis.md`).  The Python script just reformats
   the output — there is no independent byte-reading, no embedded-ASCII-
   sig scan, and no init/play address heuristic inside this script.

---

## Sub-variant label space (from sidid.cfg)

The only sub-variant tokens the filter will ever emit are the three
parenthetical sub-signatures defined in sidid.cfg:

| Label emitted            | sidid token         |
|--------------------------|---------------------|
| `SoedeSoft/Soundmaster_V1.0` | `(Soundmaster_V1.0)` |
| `SoedeSoft/Soundmaster_V3.1` | `(Soundmaster_V3.1)` |
| `SoedeSoft/Soundmaster_V3.2` | `(Soundmaster_V3.2)` |

---

## Notes on the _specific.csv pipeline

`_process.bat` runs all specific-classifiers in sequence.  The combined
CSVs feed DeepSID's database import (`_import.csv`).  This pipeline is
Windows-only and requires a live sidid run over HVSC; the intermediate
`_specific.csv` is ephemeral and is not committed to the repo.
