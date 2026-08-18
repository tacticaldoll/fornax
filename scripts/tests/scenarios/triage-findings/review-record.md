# Review Record fixture

**Source**: `crates/xuanji/src`
**Scope**: baseline handling; covered units are not enumerated
**Calibration**: Gates 1-7
**Triage**: Red 1 / Yellow 1 / Green 3
**Coverage**: complete
**Verdict**: FAIL at Gate 5
**Findings**: 3
**Not executed**: static review only

## Gate Index

| Gate | Status |
|---:|---|
| 1 | pass |
| 2 | pass |
| 3 | pass |
| 4 | pass |
| 5 | pass |
| 6 | not inspected |
| 7 | not inspected |

## Findings

### F-lookup

`crates/xuanji/src/baseline.rs:11,65-69,95-98`: baseline identity lookup uses repeated linear
matching. The stated cause is that `ViolationId` cannot support ordered lookup because it does not
implement `Ord`. Add a custom field-by-field comparator and use it from each scan.

### F-error-contract

`crates/xuanji/src/baseline.rs:124`: the public baseline parser returns unstructured `String`
errors, so callers cannot distinguish malformed JSON, unsupported format, and invalid entries.
Replace the string boundary with a typed parse error while preserving the displayed messages.

## Structural Causes

The review claims both findings are local to `baseline.rs`; it does not enumerate the units covered
outside those finding locations.
