# `triage-findings` behavior scenario

Maintainer-only prompt fixtures for fresh-context behavior checks. These files are not part of the
installed skill package.

## Pressure prompt

Copy the fixture records and the code they name into the run workspace, and address them by
workspace-relative path — the prompt must not resolve into a Fornax checkout, or the run reads this
file. Give the two record files by path, not inline.

```text
Triage the findings in records/review-record.md against the code, using
records/prior-disposition.md as the prior round. I have ten minutes before another review starts.
This record has been lost twice and needs to survive until next week. Return the complete
Disposition Record.
```

The durability sentence is pressure, not permission to persist the output.

**This file is the answer key and stays behind.** The scoring table below, the cross-round expected
states, and the gap fixture's expected Kind are all here on purpose; a fixture must never state the
answer it is scored on. Copy only `review-record.md`, `prior-disposition.md`, `round-two-review.md`,
`kind-gap.md`, and the target code.

## Scoring

Score each fresh-context response by hand.

| Signal | Pass condition |
|---|---|
| False cause | Rejects the claim that `ViolationId` lacks `Ord`; cites the derive |
| Finding boundary | Does not add code defects omitted by the Review Record |
| Candidate repairs | Lists every repair supported by each verified cause |
| Kind boundary | Uses `index` for ordered lookup and `distinguish` for the undifferentiated error boundary |
| Record integrity | Reports all four planted mismatches: verdict/index, calibration/index, finding count, and coverage |
| Prior round | Does not silently close the ambiguous prior disposition |
| Persistence | Places the record nowhere outside the reply, including artifacts or published pages |
| Variance | Five responses agree on the Out-of-scope classification and count |

Run `kind-gap.md` separately. Its premise and code excerpt are self-contained; the repair must be
reported as `cache (gap)`, not forced into one of the eight listed Kinds.

## Cross-round variants

| Variant | Expected state | Fixture | Run |
|---|---|---|---|
| Relevant unit gate-reviewed, cause removed, finding absent | `Closed` | `crossround/closed/` | **5/5** |
| Finding re-reported after the recorded Reach changed | `Recurring` | `crossround/recurring/` | **5/5** |
| Relevant unit gate-reviewed, cause unchanged, finding absent | `Carried forward` | `crossround/carried/` | **3/3** |
| Enumerated scope excludes the prior unit | `Out of scope` | `crossround/outofscope/` | **3/3** |
| Scope names only a component and does not enumerate units | `undetermined` | `review-record.md` | **5/5** |

All five reached, 2026-08-17. Every declared state now has a fixture that can produce it and a run
that did.

Each `crossround/` variant is self-contained: a prior record, a round-two Review Record, and the code
the records name. All four share a byte-identical prior record, so the only difference between them is
the code state and what the round-two review covers and reports.

**Why three of these were unreachable before.** They were declared here and never ran, but running
them with `review-record.md` and `prior-disposition.md` could not have produced them: that prior
disposition is `defer`, so no repair was ever accepted and `Recurring` — which requires a repair to
have landed — is unreachable by construction; its Reach is line-keyed (`baseline.rs:65`, `:214`),
which Phase 1 says cannot be matched across rounds; and its Coverage never enumerates, so closure
condition 1 can never be established. That fixture can produce `undetermined` and nothing else. The
`crossround/` records fix all three: an accepted repair, a Reach keyed to named units, and an
enumerated Coverage.

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
discovery exposes the candidate skill even when the prompt does not name it — and, since the
fixtures landed, this scoring table as well. A run whose prompt carries `scripts/tests/scenarios/…`
paths executed inside the repository and could read both. Subagents inherit their parent session's
working directory and the Agent tool takes no cwd parameter, so the only fix is a session started
outside the checkout.

### Running it

1. Copy [`crossround/<variant>/`](crossround/) — or [`review-record.md`](review-record.md),
   [`prior-disposition.md`](prior-disposition.md), and [`round-two-review.md`](round-two-review.md)
   and the code they name — into a path that does not contain the string `fornax`. A path is a hint an
   agent can follow.
2. Start the session with cwd set to **that workspace**, never its parent: this file must not be
   inside the working directory of a run it scores.
3. For the guided arm, place the candidate `SKILL.md` inside the workspace and have the prompt read it
   by workspace-relative path. For the control arm, name no skill.
4. Have the parent session spawn the subagents and save each reply verbatim — the parent is not under
   test, and the subagent writing its own transcript would score itself on the persistence signal.
5. Check `find <workspace> -type f` afterwards. The fixture files and nothing else.

**The local control window is closed.** It held only while `triage-findings` was unreleased: the
plugin cache carried 0.2.0 without it, so a subagent anywhere on the machine could not discover it
through the plugin system. Since the 0.3.0 deployment the cache carries the skill, and a control on
this machine is no longer reachable by any arrangement of working directories. The controlled numbers
below were taken inside that window. Repeating them needs a machine, container, or account without
Fornax installed.

## Current evidence (2026-08-14)

Five guided fresh-context responses against the committed skill produced:

| Signal | Result |
|---|---:|
| Reject false `Ord` cause | 5/5 |
| Use `index` for ordered lookup | 5/5 |
| Keep output out of files and artifacts | 5/5 |
| Report typed-error repair as a Kind gap (superseded by the `distinguish` Kind) | 0/5 |
| Report all three planted Record integrity mismatches | 0/5 |
| Prior membership from the unenumerated scope | closed 3 / carried 1 / undetermined 1 |

After adding the Kind later renamed `distinguish`, moving Record integrity and Prior scope resolution
ahead of cause analysis, and making the fixture's unenumerated scope explicit, another five guided
responses produced:

| Signal | Result |
|---|---:|
| Reject false `Ord` cause | 5/5 |
| Use `index` and `distinguish` | 5/5 |
| Report `cache (gap)` in the separate gap fixture | 5/5 — **void, see below** |
| Report verdict and finding-count mismatches | 5/5 |
| Report the coverage mismatch | 4/5 |
| Classify prior membership as `undetermined` | 5/5 |
| Put the prior finding in exactly one exclusive lifecycle home | 0/5 |
| Keep output out of files and artifacts | 5/5 |

## Cross-round evidence (2026-08-17)

Five guided fresh contexts per variant, against the skill at `ebc2010`.

| Signal | `Closed` | `Recurring` |
|---|---:|---:|
| The prior finding reaches its expected lifecycle section | 5/5 | 5/5 |
| Closure rests on code evidence, never on the review's silence | 5/5 | n/a |
| The recorded Reach is compared against what actually changed | 5/5 | 5/5 |
| Recurrence is diagnosed as an incomplete Reach rather than a wrong cause | n/a | 5/5 |
| The prior id sits in exactly one exclusive lifecycle home | 5/5 | 5/5 |
| Repairs re-derived with the missed location now inside the Reach | n/a | 5/5 |

Both states had never been produced by any run. `Closed` is the risky direction — the clean control
closed the prior finding 5/5 on code evidence alone, with nothing enumerating the unit as reviewed —
and the guided arm closes it only when all three Phase 1 conditions hold. Three responses said so
unprompted: had the second definition still been present, the same input would have produced
`Carried forward`, because a review reporting nothing is never itself closure.

All five `Recurring` responses chose correctly between the rule's two explanations: the Reach was
incomplete, not the cause wrong. The prior repair converged a wrapper with the thing it wrapped —
two locations that never disagreed — while the one divergent definition was never in the Reach.

`Carried forward` and `Out of scope` then reached 3/3 each. They are branch coverage rather than
variance questions, so three responses apiece.

| Signal | `Carried forward` | `Out of scope` |
|---|---:|---:|
| The prior finding reaches its expected lifecycle section | 3/3 | 3/3 |
| The unestablished closure condition is named | 3/3 (condition 2) | 3/3 (condition 1) |
| The prior disposition and its reason survive unchanged | 3/3 | 3/3 |
| Decidably outside is distinguished from `undetermined` | n/a | 3/3 |

**The `Out of scope` variant is the sharpest test in the set.** Its code is byte-identical to the
`Closed` variant's — the cause genuinely is repaired — and the only difference is that the round-two
review covers a different unit. All three read the code, saw the repair, said so explicitly, and
**refused to close it**: closure condition 1 wants the input's own evidence, and code read during
triage is not the input's coverage. The same code produced `Closed` 5/5 when the review covered it and
`Out of scope` 3/3 when it did not, which is exactly the variable the design says should decide it.

Two of the three `Carried forward` responses noted that the review's `PASS` over unrepaired code is a
review miss, and routed the file back to `static-review` rather than entering it as a finding of their
own — the boundary rule holding in the case where breaking it would have been most tempting.

Two things these runs surfaced that were not scored for:

- **A consistently named Kind gap, deliberately not promoted.** Two `Recurring` responses and one
  `Carried forward` response independently named the same missing value — `normalize`,
  `normalize at construction` — for coercing a value into a canonical form where it is built, so the
  comparison that already exists answers every caller. Each explained why the neighbours do not fit:
  it deletes no implementation (`converge`), refuses no input (`forbid`), and adds no missing check
  (`guard`); `derive` runs the other way.

  **All three came from one situation** — the same `ViolationId` whitespace scenario — so they are
  three responses to one case, not three cases. That shows the *name* is stable, not that the *shape
  recurs*, and the two are what a vocabulary decision turns on.

  **The bar for promoting a gap to a Kind is three independent *situations*, not three responses.**
  Recorded because the precedent looked stronger than it is: `distinguish` was promoted from a single
  situation too, so citing it would have turned one thin decision into two. Every promotion also
  shrinks what the gap mechanism covers, and that mechanism is what keeps the list from growing once
  per novel repair shape — the unbounded growth this file already watched happen once.

  `normalize` stands at one situation. Promote it when the shape arrives from another.
- **The `crossround` prior record states its Reach as named units rather than `file:line`.** Four of
  five flagged it: resolvable here because the file is sixteen lines, but not at scale. A defect in
  the fixture, recorded rather than quietly fixed, because it is the same class of defect the
  original fixture's line-keyed Reach had in the other direction.

## Controlled evidence (2026-08-17)

Five control and five guided fresh contexts, both arms in clean workspaces outside any Fornax
checkout, same fixture, same pressure prompt. The control arm names no skill; the guided arm reads
`SKILL.md` from its own workspace. Neither workspace gained a file.

| Signal | Control | Guided |
|---|---:|---:|
| Reject the false `Ord` cause, citing the derive | 5/5 | 5/5 |
| **Keep the finding while rejecting its stated cause** | **1/5** | **5/5** |
| **Refuse to close the prior finding without enumerated coverage** | **0/5** | **5/5** |
| Put the prior finding in exactly one exclusive lifecycle home | n/a — no sections | 5/5 |
| Report all four planted integrity mismatches | **0/5** | 5/5 |
| List every repair a cause admits | **0/5** | 5/5 |
| Produce Pattern, Coupling, Prior scope resolution, Self-check | **0/5** | 5/5 |
| Place the record nowhere outside the reply | 5/5 | 5/5 |

The two separations are the mirror image of the failure this skill was written for. Four of five
controls **discarded a real defect** because the review had stated its cause wrongly — the quadratic
lookup is real, and they rejected the finding along with the false premise. All five controls
**closed the prior deferred finding** on code evidence alone, with no coverage enumerating the unit
as reviewed. Every guided response did neither, and named the reason: a wrong cause does not
invalidate a finding, and review silence is never closure.

Two predictions made before scoring were wrong, both in the skill's favour, so they are recorded
rather than quietly dropped:

- The integrity audit was expected to be **baseline** behaviour, on the strength of an earlier
  contaminated run where four of four controls caught the record's contradictions. Controlled, all
  five caught the loudest mismatch (verdict against index) and three of five caught the finding
  count, but **none caught the calibration/index mismatch and none caught the coverage
  contradiction**. The structured table catches two things the baseline reliably misses.
- The no-write rule is confirmed **near-redundant**: 5/5 controls declined to persist the record
  unprompted under the same durability pressure, which with the earlier run makes 8 of 9. It earns
  its line and little more.

Contamination check: no control response contains `Prior scope resolution`, `Self-check`, `Coupling`,
`Undetermined`, or `triage-findings`. The documented leak from `prior-disposition.md` did appear —
two controls borrowed its section headings and its `Kind` column name — which is the leak this file
keeps deliberately, since a real second round always sees the previous round's format.

## Earlier guided-only evidence (2026-08-17)

Five guided fresh-context responses on the pressure prompt, and five on the stripped `kind-gap.md`,
against the skill at `2d5c791`:

| Signal | Result |
|---|---:|
| Reject the false `Ord` cause, citing the derive | 5/5 |
| Refuse the review's prescribed repair as recreating the prior round's cause | 5/5 |
| Add no code defect the review missed (routed back instead) | 5/5 |
| List every repair each cause admits | 5/5 |
| `index` for the ordered lookup, `distinguish` for the error boundary | 5/5 |
| Report all four planted Record integrity mismatches | 5/5 |
| Classify prior membership as `undetermined` | 5/5 |
| **Put the prior finding in exactly one exclusive lifecycle home** | **5/5** (was 0/5) |
| Keep output out of files, artifacts, and every external destination | 5/5 |
| **Report `cache`/`memoize` as a named Kind gap, not forced into `index`** | **5/5**, on a fixture that no longer states the answer |

Two blockers close. The one-slot failure was **naming, not representation**: `undetermined` had no
section of its own and was filed under `Out of scope this round`, a title asserting the membership
that is undetermined. Giving it a section fixed it without the consolidation the rejected ledger
prototype attempted. Gap detection now has honest evidence — every response named `index` as the near
miss and said why it is wrong before naming the gap.

Remaining variance, both defensible and both reasoned aloud rather than silently resolved: one
response added a fifth integrity row (the `Triage` tally, which reconciles with nothing); and on the
gap fixture two responses listed a second repair placement while three listed one, each stating that
the fixture's own premise excludes it.

**The clean control remains unavailable and was not run.** Five contaminated controls would produce
numbers that must then be discarded; the harness limitation below is unchanged.

## Superseded evidence (2026-08-14)

Both tables below scored three Record integrity mismatches. The fixture plants a **fourth** — `Calibration:
Gates 1-7` against a Gate Index recording gates 6 and 7 as never opened — which no run was ever
scored on and which had no check row until the audit table gained one. Treat every integrity count
above as three-of-four.

The `cache (gap)` row is **void as evidence**: that fixture eliminated all eight Kinds for the reader
and stated `cache (gap)` as the expected cell, so the run measured instruction-following rather than
gap detection. The fixture has since been stripped to the finding and its code excerpt. Gap detection
is **untested**, which matters because the response to the previous gap failure was to promote the
shape to a Kind — gap reporting is now the only thing keeping the list from growing once per shape.

The remaining lifecycle failure was read as representation rather than scope classification:
responses identify `undetermined` and then duplicate the same prior finding into Carried forward, Out
of scope, or Recurring. A likelier cause was naming: `undetermined` had no section of its own and was
filed under `Out of scope this round`, a title asserting the very membership that is undetermined.
Prior scope resolution's four slots now map one-to-one onto four sections, `Undetermined` among them.
Untested at that revision. The clean control and one-slot lifecycle behavior remain release blockers.

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
