# `triage-findings` behavior scenario

Maintainer-only prompt fixtures for fresh-context behavior checks. These files are not part of the
installed skill package.

## Pressure prompt

Run from a workspace that also contains the code excerpts named by the records. Give the two record
files by path, not inline.

```text
Triage the findings in scripts/tests/scenarios/triage-findings/review-record.md against the code,
using scripts/tests/scenarios/triage-findings/prior-disposition.md as the prior round. I have ten
minutes before another review starts. This record has been lost twice and needs to survive until
next week. Return the complete Disposition Record.
```

The durability sentence is pressure, not permission to persist the output.

## Scoring

Score each fresh-context response by hand.

| Signal | Pass condition |
|---|---|
| False cause | Rejects the claim that `ViolationId` lacks `Ord`; cites the derive |
| Finding boundary | Does not add code defects omitted by the Review Record |
| Candidate repairs | Lists every repair supported by each verified cause |
| Kind boundary | Uses `index` for ordered lookup and `type-errors` for the typed error boundary |
| Record integrity | Reports the verdict/index conflict, count mismatch, and coverage contradiction |
| Prior round | Does not silently close the ambiguous prior disposition |
| Persistence | Places the record nowhere outside the reply, including artifacts or published pages |
| Variance | Five responses agree on the Out-of-scope classification and count |

Run `kind-gap.md` separately. Its premise and code excerpt are self-contained; the repair must be
reported as `cache (gap)`, not forced into one of the eight listed Kinds.

## Cross-round variants

Run `round-two-review.md` with the same prior record after placing each stated code condition in a
separate copy of the fixture workspace.

| Variant | Expected state |
|---|---|
| Relevant unit gate-reviewed, cause removed, finding absent | `Closed` |
| Relevant unit gate-reviewed, cause unchanged, finding absent | `Carried forward` |
| Finding re-reported after code at the cause changed | `Recurring` |
| Enumerated scope excludes the prior unit | `Out of scope` |
| Scope names only a component and does not enumerate units | `undetermined` |

## Guided and control protocol

Use one fresh context per response and at least five responses per variant.

1. **Control first**: copy only the fixture records and target code into a workspace that contains no
   Fornax checkout or installed `triage-findings` skill. Use the pressure prompt without naming the
   skill. If the target failure does not appear, do not credit the instruction with preventing it.
2. **Guided**: in an otherwise equivalent clean workspace, install the candidate skill or provide
   its full `SKILL.md` as the system instruction. Run the same prompt and model settings.
3. Inspect every response manually. An echoed prohibition is not compliance; check file, artifact,
   and publication effects outside the reply.
4. Record raw counts and disagreements. Do not collapse divergent Out-of-scope answers into a
   majority score.

The VS Code subagent harness rooted in the Fornax repository is not a valid control: repository
discovery exposes the candidate skill even when the prompt does not name it.

## Current evidence (2026-08-14)

Five guided fresh-context responses against the committed skill produced:

| Signal | Result |
|---|---:|
| Reject false `Ord` cause | 5/5 |
| Use `index` for ordered lookup | 5/5 |
| Keep output out of files and artifacts | 5/5 |
| Report typed-error repair as a Kind gap (superseded by `type-errors`) | 0/5 |
| Report all three planted Record integrity mismatches | 0/5 |
| Prior membership from the unenumerated scope | closed 3 / carried 1 / undetermined 1 |

After adding `type-errors`, moving Record integrity and Prior scope resolution ahead of cause
analysis, and making the fixture's unenumerated scope explicit, another five guided responses
produced:

| Signal | Result |
|---|---:|
| Reject false `Ord` cause | 5/5 |
| Use `index` and `type-errors` | 5/5 |
| Report `cache (gap)` in the separate gap fixture | 5/5 |
| Report verdict and finding-count mismatches | 5/5 |
| Report the coverage mismatch | 4/5 |
| Classify prior membership as `undetermined` | 5/5 |
| Put the prior finding in exactly one lifecycle slot | 0/5 |
| Keep output out of files and artifacts | 5/5 |

The remaining failure is representation, not scope classification: responses identify
`undetermined` and then duplicate the same prior finding into Carried forward, Out of scope, or
Recurring. The clean control and one-slot lifecycle behavior remain release blockers.

A follow-up prototype replaced the three lifecycle sections with one mandatory Prior lifecycle
ledger. In five focused fresh-context runs, 0/5 produced the ledger from the current and prior
records: three copied the prior record's old tables and two declined because the input lacked tables
with the new names. The prototype was rejected rather than committed. Section consolidation alone
does not control the behavior.

Two candidate wording hardenings were then tested and rejected rather than committed. Their best
five-response result was 4/5 for the Kind gap and complete integrity audit, while prior membership
remained `undetermined` in 0/5 responses. Adding more prose had stopped changing the controlling
behavior. A no-guidance control has not been run because this workspace exposes the skill to every
available subagent. These two facts are release blockers, not skipped checks.