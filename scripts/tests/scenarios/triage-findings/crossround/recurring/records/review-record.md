# Review Record

**Source**: `code/baseline.rs`
**Calibration**: Gates 1-5
**Triage**: skipped (1 file)
**Coverage**: complete — gate-reviewed: [`code/baseline.rs`]; triage-only: []; unread: []
**Findings**: 1
**Verdict**: FAIL at Gate 5

## Gate Index

| Gate | Status |
|---:|---|
| 1 | pass |
| 2 | pass |
| 3 | pass |
| 4 | pass |
| 5 | fail |

## Findings

### P-identity

`code/baseline.rs`: baseline identity matching has more than one semantic definition. `identity_matches`
compares through the derived `PartialEq`, while `stale_matches` compares the fields itself and trims the
target, so the two disagree about whether a record whose target gained whitespace is the same record.
