# Review Record — `6ec4d3b..59d7fb1`

Archived as received. `AGENTS.md` allows a non-English record here: it is a copy of what a producer
wrote, and the Disposition Record that reconciles it is English.

```markdown
Review Record
Source: 6ec4d3b..59d7fb1, validating prior v0.4.1..6ec4d3b
Calibration: Gates 1–8
Triage: Red 1 / Green 7 implementation units
Coverage: partial — gate-reviewed: record_shape, outcome, paired consumers and focused tests;
triage-only: changed records/governance; unread: README.md, resolve-deadlock/SKILL.md
Findings: 2
Verdict: FAIL at Gate 6 + CONTRACT-VIOLATED
Not executed: CLI runtime/build

Findings
#  Location  Violation  Correction
1  record_shape.py:166  cells() consumes every \x pair. CommonMark preserves non-punctuation
escapes, so ONE\q is silently changed to ONEq, corrupting finding identity and potentially hiding
duplicates.  Parse tables through the repository's CommonMark owner, or consume only valid
escapable punctuation. Add a \q negative control.
2  record_shape.py:177  cells() always discards the final segment. A valid row without an optional
trailing pipe loses its Result value and is falsely rejected.  Discard the final segment only when
the source row ends with an unescaped pipe. Add a complete four-column no-trailing-pipe case.
Current tests encode the second behavior as though omitting the trailing pipe removes a cell at
test_record_shape.py:196; that premise is incorrect.

Against-Contract
Clause  Falsifier  Result
CommonMark readings go through markdown_links and markdown-it-py  Parse \q in a table cell
VIOLATED: validator removes the backslash; project parser preserves it
Table grammar permits an optional trailing pipe  Parse | Coverage | stated | enumerated | pass
without the final pipe  VIOLATED: validator reports a missing Result
Contract evidence: development-knowns.yaml:34.

Structural Cause
Both findings come from record_shape.cells implementing part of GFM table grammar independently of
the repository's declared parser owner. The existing tests cover escaped | and \\, but not
non-punctuation escapes or a complete row without a trailing pipe.

Gate Index
Gate  Status
1–5  pass
6  fail
7–8  blocked

Gate 5 Ledger
Unit  Job  Handed in  Reached directly
record_shape.cells  Parse one table row  line  none
record_shape.table  Separate table header and body  text  SEPARATOR, cells
record_shape.declared  Derive the contract shape  root  contract path, CommonMark helpers
record_shape.record_defects  Validate one disposition  path, shape  filesystem, table helpers
record_shape.check  Validate the disposition corpus  root  filesystem, declared shape
outcome.paired  Enforce payload-or-reason state  payload, reason, message  none

Verification
.venv/bin/python scripts/check_workspace.py: passed
Focused record_shape suite: 20 tests passed
Ruff and git diff --check: passed
Reproduction: ONE\q becomes ONEq; a complete row without trailing pipe is reported as missing Result
The preceding re-review's whitespace and four historical-row findings are repaired at current HEAD
and are superseded by this record.
```
