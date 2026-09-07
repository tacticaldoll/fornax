# Disposition Record — `6ec4d3b..a7c40d1`

**Source**: `docs/reviews/6ec4d3b..a7c40d1.md`, 10 findings, FAIL at Gate 1 + CONTRACT-VIOLATED
**Scope**: `6ec4d3b..a7c40d1`, derived with `git diff --name-only` — a new check module and its
tests, one gate-step entry, two shipped skill files, and the records this range repaired
**Prior round**: `docs/dispositions/v0.4.1..6ec4d3b.md`

The first round in this range to review work this repository did at a user's direction rather than
in answer to another producer, and the first whose input is a review of a new gate step.

## Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | FAIL at Gate 1 + CONTRACT-VIOLATED | Gate 1 is recorded `fail` and is the lowest failing gate, and three Against-Contract rows are `VIOLATED`, which raises the one flag the verdict carries | pass |
| Calibration / Gate Index | Gates 1-8 | eight gates carry a status and none is `not inspected`, which matches the calibration. But six of them read `pass (vacuous)`, and the Gate Index's declared values are `pass`, `fail`, `blocked` and `not inspected` — no qualifier among them. The qualification is honest and its reasoning is sound; the place is wrong. `docs/dispositions/v0.4.1..61789c2.md` set the precedent for the same distinction and put it in the coverage line, not in the index cell. The Result column of this very table admits a qualifier because the contract's own template declares one there; the Gate Index declares none | mismatch |
| Finding count | 10 | four gate rows plus six Structural Causes rows that name findings. The record declares its keying: Against-Contract rows 1, 2 and 3 key to three of those findings and the one `REFUTED` claim keys to a fourth, and two Structural Causes rows declare no finding | pass |
| Coverage | partial, four sets, each partially-gate-reviewed unit naming its opened gates | all four present and enumerated by path; the partial units name Gate 1 or Gates 1-2, which is where the ladder stopped for each | pass |
| Non-finding sections | the `Findings` field excludes the Ledger rows | the Ledger states that its rows are not findings and carries one; the two Structural Causes rows without a finding say so in the cell | pass |

## Prior scope resolution

| Prior finding | Scope evidence stated by this round's input | Membership | This round's slot |
|---|---|---|---|
| INTEGRITY-ROW-DUPLICATES-A-DECLARED-CHECK | the input verifies the repair directly — Claims 7 re-runs the sweep and Against-Contract 8 confirms the key set is derived, and the check runs over every record | inside | Closed |
| ABSENT-CLAIM-AS-MISMATCH | the input reports the new check's boundary in its own module docstring and in Structural Causes | inside | Carried forward — condition 2 not established, and probed |
| SELFCHECK-FOLDED-INTO-THE-INPUT-AUDIT | same evidence; the cause is narrowed rather than removed | inside | Carried forward — condition 2 not established |
| TRAILING-WHITESPACE-UNSEEN | the input's Claims 5 confirms the instances are gone; the cause was the absence of a check, and `1b` was not taken | inside | Carried forward — condition 2 not established |
| TRIGGER-KEYS-ON-THE-WEAKEST-AXIS | its units are in `docs/guards.md` and `docs/dispositions/c60a6ba..af1185a.md`, which the input lists `triage-only` | inside | Carried forward — condition 1 not established |
| LEDGER-TABLE-ROUNDS | its unit is `docs/guards.md`, inside the delta and listed `triage-only` | inside | Carried forward — condition 1 not established |
| LIFECYCLE-OMITS-THE-NAMED-PRIOR | its units are lifecycle sections of `docs/dispositions/v0.4.1..61789c2.md`, listed `partially-gate-reviewed` at Gate 1, which is not the relevant gate | inside | Carried forward — condition 1 not established |
| REVIEW-COVERAGE-AS-FINDING | declined; its unit `development-knowns.yaml` is inside the delta and listed `triage-only` | inside | Carried forward, declined — no new evidence |
| REVIEW-FILED-A-VIOLATION-AS-A-VERIFIED-CLAIM | its unit is a Claims entry of `docs/reviews/v0.4.1..6ff702e.md`, which this delta does not touch | outside | Out of scope this round |
| PARAGRAPH-SPLIT-NOT-REFLOWED, FIXTURE-READ-AS-PRODUCT, COVERAGE-ENUMERATION-ABSENT, RAWSCORES-PROVISIONAL, F-11, F-12 | none of their units is among the delta's paths | outside | Out of scope this round |

**One closure, and the reason it is only one is the reading this round exists to record.** The check
built to settle the Record-integrity class closes `INTEGRITY-ROW-DUPLICATES-A-DECLARED-CHECK`
outright: an invented key is refused, verified against a live counter-example and over every record.
It does **not** close `ABSENT-CLAIM-AS-MISMATCH`. Probed: a row keyed `Coverage` — a key the contract
declares — whose `Input claim` reads "not stated" and whose Result reads `mismatch` passes the check
clean. That is the cause verbatim, and the check answers a different question.

So the repair was confined to the instances again, in a new form. The previous three rounds confined
it to a row, then to a table's row labels; this round built a check over row labels and the cause is
where it was. What has changed is that the boundary is now stated in the module rather than
discovered by the next round — the input reports it, and this record carries it as cause 8 below.

## Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach (every location it touches) | Route |
|---|---|---|---|---|---|---|
| 1 | The paired-optional shape is a convention copied by hand with no owner, so the fifth copy diverged in spelling and was incomplete for a type carrying two payload fields rather than one | DECLARED-GUARDS-ONE-PAYLOAD, INVARIANT-SPELLED-TWO-WAYS | 1a collapse `Declared` to one payload so the family's single guard is complete, and spell the guard as its four siblings do | `converge` | `record_shape.Declared`, `record_shape.declared` | `plan-implementation` |
| 1 | " | " | 1b give the family an owner — the `Read[T]` primitive whose component design this session already produced — and route all five copies plus the four `tuple[X, reason]` returns through it | `converge` | `record_shape.Declared`, `skill_yaml.Document`, `path_boundary.Boundary`, `check_citations.Symbols`, `evidence_currency.Fingerprint`, and the enumeration `AGENTS.md` requires of a new owner | `plan-implementation` — and see the Pattern, which is why this is no longer marginal |
| 2 | the table reader returns a flat list in which the header is indistinguishable from the body, so every caller skips it by index and reads the Result by `[-1]` rather than by its column | RESULT-READ-BY-POSITION, TABLE-BODY-HAS-NO-NAME | 2a return the header and the body apart, and read the Result by the column the header names | `distinguish` | `record_shape.table`, `record_shape.Table`, `record_shape.declared`, `record_shape.record_defects` | `plan-implementation` |
| 3 | A root holding no records returns an empty diagnostic list, and the entry point reports that as clean — the same result a run that inspected everything gives | EMPTY-SCOPE-READS-AS-CLEAN | 3a make an absent or empty corpus a failure, as `check_sources` does for a missing interpreter | `forbid` | `record_shape.check`, `record_shape.main` | `plan-implementation` |
| 4 | The cell escape is tested by a lookbehind rather than consumed, so a backslash that is itself escaped reads as escaping the delimiter after it | ESCAPE-TESTED-NOT-CONSUMED | 4a consume escapes left to right when splitting a row | `guard` | `markdown_links.table_rows` | `plan-implementation` |
| 4 | " | " | 4b register the gap instead, since `AGENTS.md` permits a delimiter-bounded read without an owning parser | `declare` | `development-knowns.yaml` | document — maintainer-owned; **weaker than 4a**, because the claim that is wrong is about the escape rather than about the delimiter |
| 5 | The new suite resolves the repository as the working directory where its sibling resolves it from the module's own location | TEST-ROOT-BY-CWD | 5a use `record_shape.ROOT`, as `test_check_citations` uses `check_citations.ROOT` | `converge` | `test_record_shape.DerivedShape`, `test_record_shape.RecordIntegrityRows` | `plan-implementation` |
| 6 | `ruff.toml` claims one width for "the Python and the markdown" and nothing enforces the second half | PROSE-WIDTH-UNENFORCED | 6a reflow the two paragraphs | `restate` | `docs/dispositions/v0.4.1..61789c2.md` and `docs/dispositions/v0.4.1..de72982.md`, each one's probe-disclosure paragraph | document — maintainer-owned |
| 6 | " | " | 6b register the unenforced half beside the entry that records the Python one | `declare` | `development-knowns.yaml`, the `e501-exempts-a-whitespace-free-line` entry | document — maintainer-owned |
| 7 | Two expressions do more than their purpose — a comprehension that copies a list unchanged, and a sort taken only for a length | NO-OP-COMPREHENSION, SORT-TO-COUNT | 7a write each as what it does | `restate` | `record_shape.main` | `plan-implementation` |
| 8 | Key-set closure answers whether a row's **key** is declared, and the carried cause is whether a row's **claim** exists — so the check refuses the instances that occurred and admits the cause | — carried, see `ABSENT-CLAIM-AS-MISMATCH` | 8a require `not claimed` wherever the `Input claim` cell holds a declared absence token, which means the contract declaring one | `guard` | a canonical absence token in `skills/triage-findings/SKILL.md`'s marked template, plus `record_shape.record_defects` | **not taken this round** — see the weighing |
| 8 | " | " | 8b leave the boundary stated and carry the finding | `declare` | `record_shape` module docstring, which already states it | taken as the interim, and it is what the Carried forward row records |

### Weighing repair 8a

`AGENTS.md` asks what a candidate check would have caught and what it costs. **What it would have
caught**: the `Range already settled` row, whose `Input claim` was "not stated" and whose Result was
`mismatch` — the one instance of this class that reached the shared branch inside a record that read
as settled. Key-set closure catches that row too, by its label; `8a` would catch it by its defect,
and would also catch the same defect under a declared label, which nothing does today.

**What it costs**: the contract has to declare a canonical spelling for an absent claim, because the
corpus writes it as "not stated" and "not declared" and a check comparing prose would be guessing.
That is a contract change reaching a producer's authoring step, and this round has already learned
what happens when a rule is written and applied in one turn. It is also the third consecutive round
in which a repair for this cause has been proposed; buying the check in the same turn that
discovered the previous check does not close it is the pattern rather than the exit.

**Not taken, and the trigger is decidable**: the next round that finds a Record integrity row
convicting under a **declared** key on an `Input claim` cell that names no claim. Key-set closure
cannot see that row, which is exactly what makes the trigger a test of this cause and not of the
last one.

## Pattern

**This round refutes a weighing I made earlier in the same session, and the refutation is measured.**
The component design for the `Read[T]` primitive called it marginal, on this reasoning: "the
invariant has NEVER been violated at the five sites that implement it. It was violated at the sites
that DIDN'T implement it." A fifth site was then written in this range and it violated the invariant
twice over — incomplete for its second payload field, and spelled differently from all four
siblings. So the argument that the copies are safe because they have held is an argument from a
sample that excluded the next copy, and the next copy is the one a new module always writes.

That makes `1b` the repair with the strongest earned case in this range, and it was the one ranked
lowest when it was designed. Cause 1's `1a` is the local fix and does not touch what admits the
sixth copy.

**The second shape is the one causes 3, 6 and 8 share: a claim whose enforcement is narrower than
its wording.** An entry point reporting `OK` over an empty corpus, a width claim covering markdown
that only Python is held to, and a key-set check standing in for a subject rule. Each is honest
about its boundary in exactly one place — a docstring, a comment, a module — and each is read as
wider by anything that only sees the green. This range has now produced three of them and repaired
two by writing the boundary down, which is not the same as closing it.

## Coupling

- `1a` is a **prerequisite of** `1b`, and this row first said it was voided by it. Corrected while
  the repairs were being planned: `outcome.paired` takes one payload and one reason, so a type
  carrying two payload fields that travel together cannot be handed to it at all. The collapse is
  what makes `Declared` able to call the owner. That is also the sharpest argument for the owner —
  it refuses the shape that broke rather than only deduplicating the shape that held — and the
  reading was available in this record's own cause 1 statement, which says the fifth copy "was
  incomplete for a type carrying two payload fields rather than one".
- `4b` is **voided by** `4a`; they are alternatives and `4a` is the stronger, because what the commit
  message got wrong is the escape rule rather than the delimiter.
- `8a` and `8b` are not alternatives: `8b` is what stands while `8a` is unbuilt.
- `2a`, `3a`, `5a`, `6a`, `7a` are independent of each other and of everything above.

## Dispositions

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| DECLARED-GUARDS-ONE-PAYLOAD — a two-payload paired optional guards one field, and the second accessor then raises with an empty message | 1 | new | accept | — |
| INVARIANT-SPELLED-TWO-WAYS — the fifth copy of one invariant is spelled unlike the four it names as its model | 1 | new | accept | — |
| RESULT-READ-BY-POSITION — a row missing its trailing pipe yields a diagnostic naming a non-Result cell as the verdict | 2 | new | accept | — |
| TABLE-BODY-HAS-NO-NAME — three sites skip a table's header by index, and the concept has no name | 2 | new | accept | — |
| EMPTY-SCOPE-READS-AS-CLEAN — a check that inspected nothing reports what a check that inspected everything reports | 3 | new | accept | — |
| ESCAPE-TESTED-NOT-CONSUMED — a lookbehind reads an escaped backslash as escaping the delimiter after it | 4 | new | accept | — |
| TEST-ROOT-BY-CWD — the suite resolves the repository from the working directory where its sibling resolves it from the module | 5 | new | accept | — |
| PROSE-WIDTH-UNENFORCED — two prose lines exceed the width the style config claims for markdown, which nothing checks | 6 | new | accept | — |
| NO-OP-COMPREHENSION — a comprehension copies a list unchanged | 7 | new | accept | — |
| SORT-TO-COUNT — a directory listing is sorted only to be counted, and re-globbed after the run that walked it | 7 | new | accept | — |

All ten accepted. Each was verified against the tree during triage and eight were probed by the
input; none reduced to a wrong cause. Two are one-line edits, and they are accepted because their
repairs cost a line and their causes hold rather than because a review produced them.

**Where this round disagrees with its own input.** The Review Record marks Gates 3-8 `pass
(vacuous)` in the Gate Index. The reasoning is right and the placement is not: the Gate Index has
four declared values and no qualifier, while the Result column of a Record integrity table admits
one because the template declares it there. Recorded as a Record integrity mismatch above rather
than as a finding, because it is the input's fitness and not a defect in the tree.

## Carried forward

| Finding | Prior disposition | Original reason, unchanged | Closure condition not established |
|---|---|---|---|
| ABSENT-CLAIM-AS-MISMATCH | accept | a Record integrity row can convict on a claim the input never made, because nothing ties the row's Result to whether its `Input claim` cell names a claim at all | 2 — probed: a declared key with an `Input claim` of "not stated" and a Result of `mismatch` passes the new check. The check answers about the key, the cause is about the claim |
| SELFCHECK-FOLDED-INTO-THE-INPUT-AUDIT | accept | a fact about the record being written can be filed in the table that audits the input, because the two tables' subjects are stated in prose and enforced by nothing | 2 — narrowed, not removed: an undeclared key is refused, and a subject-wrong row under a declared key is not. The input states this boundary in the module itself |
| TRAILING-WHITESPACE-UNSEEN | accept | nothing in this repository sees a trailing space, in any file | 2 — the instances are gone and the class swept, which the input verifies, but the recorded cause is the absence of a check and `1b` was weighed and not taken |
| TRIGGER-KEYS-ON-THE-WEAKEST-AXIS | accept | the condition for building the derived check tests a row's Result where the defect is in its subject | 1 — its units are listed `triage-only`, and this round did not re-read them |
| LEDGER-TABLE-ROUNDS | out of scope in earlier rounds | unchanged | 1 — its unit is inside the delta and listed `triage-only` |
| LIFECYCLE-OMITS-THE-NAMED-PRIOR | accept | a lifecycle self-check answered `pass` by counting the ids the record had placed rather than by enumerating the prior record's open dispositions | 1 — its units sit in a record opened at Gate 1 only, which is not the relevant gate |
| REVIEW-COVERAGE-AS-FINDING | decline | a review's coverage claim is not a defect of the registry it is recorded in | — declined; its unit is inside the delta but `triage-only`, and scope alone is not new evidence |

## Closed

| Finding | Prior disposition | Code evidence the cause no longer holds | Input evidence |
|---|---|---|---|
| INTEGRITY-ROW-DUPLICATES-A-DECLARED-CHECK | accept | `record_shape.record_defects` refuses a Record integrity row whose key is not among the five, and `record_shape.declared` takes those five from the contract's marked template rather than from a copy. An invented label has nowhere to sit | the input verifies the repair directly rather than by silence: Claims 7 re-runs the label sweep, Against-Contract 8 confirms the derivation by changing the template, and a live counter-example was reintroduced into a real record and refused |

## Out of scope this round

**REVIEW-FILED-A-VIOLATION-AS-A-VERIFIED-CLAIM, PARAGRAPH-SPLIT-NOT-REFLOWED,
FIXTURE-READ-AS-PRODUCT, COVERAGE-ENUMERATION-ABSENT, RAWSCORES-PROVISIONAL, F-11, F-12.** None of
their units is among this delta's paths. The three declined ones keep their dispositions and reasons.

Worth one line on the first, because this round could have re-reported it and did not need to: its
own input filed the measured escape defect as an Against-Contract violation **and** as a refuted
claim, keyed together. That is the conduct the finding asks for, observed rather than claimed — but
the finding's unit is a file this delta does not touch, so it stays outside rather than closing.

## Undetermined

`none`. The input enumerates its coverage, which is what empties this section for a `static-review`
record.

## Recurring

`none` among this round's ten findings — all are new identities.

The recurrence belongs to **ABSENT-CLAIM-AS-MISMATCH**, carried above, and it is now four rounds
deep with a fourth form. Its recorded repairs were: remove one row; compose the table from the
contract's list each round; build a check over the row labels. All three landed. The cause named in
the previous record — nothing ties a row's Result to whether its claim exists — is untouched by all
three, and this round is the first to demonstrate that with a probe rather than to infer it. Cause 8
above is the first repair addressed at the cause rather than at what the cause produced.

## Ungrouped

`none`.

## Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass — counted from the previous record's own tables, which left fifteen ids open: its six Dispositions rows and its nine Out of scope ids. This record places one in Closed, seven in Carried forward, and seven in Out of scope this round. One plus seven plus seven is fifteen. Dispositions holds this round's ten new ids and no prior one; Undetermined is empty and says why |
| Every accepted cause carries at least one repair with an enumerated Reach | pass — causes 1 through 7 each carry a repair whose Reach names a file plus a symbol. Cause 8 is carried rather than accepted as a finding of this round, and its `8a` names a template token and a symbol while `8b` names the docstring that already holds it |
