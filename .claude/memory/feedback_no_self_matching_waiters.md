---
name: feedback_no_self_matching_waiters
description: "Never poll with `while pgrep -f 'PATTERN'; do sleep N; done` — the pattern self-matches the waiter's own command line and loops forever; rely on harness task notifications instead"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 31df618e-1d05-4346-8dfa-a60476d0a5cc
  modified: 2026-07-22T14:50:20.426Z
---

**TRIPWIRE — do NOT write `while pgrep -f 'PATTERN' >/dev/null; do sleep N; done`
waiter loops to block on a background job.** The waiter's OWN command line
contains `PATTERN` (e.g. `pgrep -f 'family_batch.py'`, `pgrep -f 'verify_usf'`),
so `pgrep -f` matches the waiter itself → the condition is always true → the
loop never exits → it spawns `sleep` forever. This leaked ~15 stuck waiters in
one session (2026-06-27), each respawning a `sleep`, and needed a manual
PID-by-PID kill to clean up (while carefully sparing the PARALLEL DMC session's
real `dmc_family_batch.py` workers + its own poller).

**THIRD OCCURRENCE, 2026-09-02 — and the new part is that it was a SCRIPT
waiting on the pattern, not just a one-liner.** A serial overnight chain

```bash
while pgrep -f "tools/regression.py" >/dev/null 2>&1; do sleep 60; done
```

never advanced past step one, because by then SIX earlier harness waiters —
each itself a `bash -c ... pgrep -f "tools/regression.py" ...` — were sitting
in the process table with the pattern in their argv. They matched each other
and the chain matched all of them, so the whole set waited on itself while the
job they were watching had already finished with exit 0. The chain's two
remaining steps (a re-batch and a corpus sweep) simply never ran.

⚠ THE MULTIPLIER IS THE NEW LESSON: every waiter you spawn becomes a decoy for
the NEXT one. One is a bug; several make the pattern permanently true, and the
symptom is indistinguishable from "the job is still running".

**Cures, in order of preference:** (1) rely on the harness task notification —
it is exact and it already told us; (2) if a script genuinely must poll, use a
pattern that cannot match a shell wrapper (`pgrep -f "[t]ools/regression.py"`,
or `pgrep -x python3` plus a check on the child's own output file); (3) have
the long job WRITE A SENTINEL on completion and poll for the file, which no
argv can imitate.

**Why:** a foreground `sleep` is blocked by the harness, so the instinct is to
background a poll loop — but `pgrep -f` over a self-describing command is the
classic self-match. Escaping the dot (`family_batch\.py`) avoids matching the
literal-dot form but is fragile and easy to forget.

**SECOND FAILURE MODE, same class — the waiter never exits because its TEST is
broken, not because the pattern self-matches (2026-07-22).** Escaping the dot
did avoid the self-match, but:

```bash
until [ "$(pgrep -c -f 'dmc_family_batch\.py' 2>/dev/null || echo 0)" -eq 0 ]; do sleep 20; done
```

`pgrep -c` PRINTS `0` *and* EXITS NON-ZERO when nothing matches, so `|| echo 0`
fires as well: the substitution is `"0\n0"`, `[` errors with `integer
expression expected`, a failed test means "condition false" — and `until`
loops forever. It spun ~40 min until killed by hand. **The batch it was
"waiting for" had already notified through the harness.**

The self-inflicted trap here was in the VERIFICATION: the doubled `0` was
printed in plain sight while checking the pattern for self-matching, and got
read as two separate check lines. When testing a waiter, assert on the LOOP
TERMINATING (run it and watch it exit), never on the predicate's output
looking plausible.

Guard for any future poll: `c=$(pgrep -c -f PAT); [ "${c:-0}" -eq 0 ]` — no
`|| echo`, since `pgrep -c` already prints 0.

**THIRD OCCURRENCE (2026-07-22, same session as the second) — the plain
self-match again, invited by the harness's own error text.** Trying to block
on a foreground `sleep`, the harness refuses and suggests: *"use Monitor with
an until-loop (e.g. `until <check>; do sleep 2; done`)"*. Taking that shape
literally produced

```bash
until ! pgrep -f masm_family_batch >/dev/null; do sleep 20; done
```

— failure mode 1 verbatim, with this memory already in context. It spun 22 min
and was only noticed because the task's output file was 0 bytes long after the
job it "waited for" had already reported DONE. **The suggested LOOP FORM is
fine; the predicate is what kills you** — and `pgrep -f <name-of-the-thing-in-
this-very-command>` can never be a valid predicate. TELL that you are in it: a
`run_in_background` task whose output file stays EMPTY while the thing it
waited on has finished, plus a lone `sleep N` in `ps` that keeps reappearing
with a fresh elapsed time.

The durable fix is behavioural, not syntactic: when the harness blocks a
`sleep`, that is a signal to **stop waiting entirely** and go do other work —
the `<task-notification>` will arrive. Three occurrences have now all come from
trying to synchronously wait for something the harness was already tracking.

**How to apply:**
- The harness already RE-INVOKES you with a `<task-notification>` when a
  `run_in_background: true` Bash task finishes. WAIT for that notification —
  don't build your own waiter. Read the output file when it fires.
- If you truly must poll external state the harness can't track, match a string
  that CANNOT appear in the poller's own argv (e.g. `pgrep -x sleep` then filter
  by parent, or grep the OUTPUT FILE growing, or check a pidfile), never
  `pgrep -f '<the script name in this very command>'`.
- Shared-host hygiene: when killing strays, a parallel session's processes use a
  DIFFERENT bash snapshot id; identify yours vs theirs by snapshot before any
  kill, and never `pkill -f` a broad pattern that could hit the other session.

Related: [[feedback_background_jobs_harness]] (long batches use the harness
background, not `nohup&`), [[feedback_subagents_no_git]] (don't disrupt shared
state another session relies on).
