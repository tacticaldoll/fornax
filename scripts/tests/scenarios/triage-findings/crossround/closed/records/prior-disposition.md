# Disposition Record

**Source**: first review of the baseline identity path
**Scope**: `code/baseline.rs` — gate-reviewed: [`code/baseline.rs`]
**Prior round**: first round

## Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach (every location it touches) | Route |
|---|---|---|---|---|---|---|
| 1 | baseline identity matching has more than one semantic definition, so two callers can disagree about whether two records are the same | P-identity | 1a | converge | `code/baseline.rs` — the hand-written `PartialEq for ViolationId`, and `identity_matches` | plan-implementation |

## Dispositions

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| P-identity | 1 | new | accept | — |

## Carried forward

first round

## Out of scope this round

none
