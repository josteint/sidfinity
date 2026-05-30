---
name: All-subtune testing
description: compare_sids_tolerant now tests ALL subtunes, worst grade wins. 159 songs exposed with broken secondary subtunes.
type: project
---

As of 2026-04-18, compare_sids_tolerant tests every subtune, not just subtune 1. The grade is the WORST across all subtunes.

**Impact:** 159 songs dropped from Grade A because secondary subtunes are broken. Grade A+S went from 4,466 to 4,307.

**Root cause:** The pipeline (gt2_to_usf, rh_to_usf) often only extracts subtune 1. The rebuilt SID has fewer subtunes than the original. When both have the same number of subtunes but the converter only handled subtune 1 properly, the others fail.

**How to apply:** When investigating failures, check subtune count first. If the rebuilt SID has fewer subtunes, the converter needs multi-song support. If it has the same count but later subtunes fail, the converter needs fixing for those specific subtunes.

5% of HVSC SIDs have multiple subtunes (~375 in the GT2 scope).
