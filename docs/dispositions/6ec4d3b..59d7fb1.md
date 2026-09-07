# Disposition Record — `6ec4d3b..59d7fb1`

**Source**: `docs/reviews/6ec4d3b..59d7fb1.md`, 2 findings, FAIL at Gate 6 + CONTRACT-VIOLATED
**Scope**: `6ec4d3b..59d7fb1`, derived with `git diff --name-only` — the record shape check and its
tests, the paired-optional owner and its five adopters, and the records and registry this range
repaired
**Prior round**: `docs/dispositions/6ec4d3b..a7c40d1.md`

An input from another producer, reviewing a range this repository had already reviewed and settled
once, and correctly declining to re-report what that round repaired.

## Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | FAIL at Gate 6 + CONTRACT-VIOLATED | Gate 6 is recorded `fail` and the verdict names it; two Against-Contract rows are `VIOLATED`, which raises the one flag the verdict carries | pass |
| Calibration / Gate Index | Gates 1-8 | eight gates are accounted for, given as `1–5 pass`, `6 fail`, `7–8 blocked`. Collapsing five gates into one row leaves per-gate status unstated, which the contract's index asks for a row at a time; recorded as a pass because the aggregate is unambiguous and the ladder is coherent — 6 failing is what blocks 7 and 8 | pass |
| Finding count | 2 | two finding rows, and the two Against-Contract rows key to them one for one. The input says so in its Structural Cause, which declares both as one root | pass |
| Coverage | partial, four sets | all four present, and `gate-reviewed` names units rather than paths — "record_shape, outcome, paired consumers and focused tests". The paired consumers resolve against this range's own delta, so the set is decidable | pass |
| Non-finding sections | not declared | the Gate 5 Ledger carries six rows and the Verification section four claims, and neither states its finding status. This is the concession's case: a record from another producer has nothing to reconcile here | not claimed |

One note on the Ledger, recorded here rather than as a finding: it lists the row reader as reaching
nothing directly, which is right, and `record_shape.table` as reaching that reader and a separator
pattern — both of which this round's repair deletes, so neither is citable as a symbol any more. The
Ledger was accurate when written, which is the property an archived record has and a live one does
not.

## Prior scope resolution

| Prior finding | Scope evidence stated by this round's input | Membership | This round's slot |
|---|---|---|---|
| RESULT-READ-BY-POSITION | finding 2 reports the same unit and refutes the premise that round's repair rested on | re-reported | current finding → Dispositions, carried, recurring |
| ESCAPE-TESTED-NOT-CONSUMED | finding 1 reports the same unit and a case that round's repair did not reach | re-reported | current finding → Dispositions, carried, recurring |
| DECLARED-GUARDS-ONE-PAYLOAD, INVARIANT-SPELLED-TWO-WAYS, EMPTY-SCOPE-READS-AS-CLEAN, TABLE-BODY-HAS-NO-NAME, TEST-ROOT-BY-CWD, PROSE-WIDTH-UNENFORCED, NO-OP-COMPREHENSION, SORT-TO-COUNT | the input states each is repaired at HEAD and declines to re-report; `record_shape` and `outcome` are `gate-reviewed` | inside | Closed |
| ABSENT-CLAIM-AS-MISMATCH | not re-reported; `record_shape` is `gate-reviewed` and the input opens Gate 6 over it | inside | Carried forward — condition 2 not established |
| SELFCHECK-FOLDED-INTO-THE-INPUT-AUDIT | same | inside | Carried forward — condition 2 not established |
| TRAILING-WHITESPACE-UNSEEN | the input ran `git diff --check` and reports it passing | inside | Carried forward — condition 2 not established |
| TRIGGER-KEYS-ON-THE-WEAKEST-AXIS, LEDGER-TABLE-ROUNDS, LIFECYCLE-OMITS-THE-NAMED-PRIOR, REVIEW-COVERAGE-AS-FINDING | their units are in records and governance the input lists `triage-only` | inside | Carried forward — condition 1 not established |
| REVIEW-FILED-A-VIOLATION-AS-A-VERIFIED-CLAIM, PARAGRAPH-SPLIT-NOT-REFLOWED, FIXTURE-READ-AS-PRODUCT, COVERAGE-ENUMERATION-ABSENT, RAWSCORES-PROVISIONAL, F-11, F-12 | none of their units is among the input's locations | outside | Out of scope this round |

**Eight closures, and the input earns them by declining to re-report rather than by silence.** It
states that the previous round's ten findings "都有對應修復", names the range those repairs sit in,
and `gate-reviewed` the two modules that carry them. Two of the ten are re-reported and are this
round's findings; the other eight close.

**The two re-reported ones are Recurring in the sharpest form this range has produced.** Both
repairs landed over their full recorded Reach and both findings came back — which under this skill's
own test means the stated cause was wrong. It was: the previous round read "a row missing its
trailing pipe loses a cell" as a **premise** and repaired only which cell got blamed. The cell was
never supposed to be lost. And it read the escape defect as a lookbehind to be replaced by a
hand-written scan, when the escape rule itself belongs to a parser this repository declares an owner
for.

## Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach (every location it touches) | Route |
|---|---|---|---|---|---|---|
| 1 | The table row reader was written beside its caller on the assumption that reading to a delimiter needs no parser, so the two parts of the grammar that are not a delimiter — which characters a backslash escapes, and that the outer pipes are optional — were guessed | ESCAPE-EATS-A-NON-PUNCTUATION-PAIR, TRAILING-PIPE-ASSUMED-MANDATORY | 1a consume only ASCII punctuation after a backslash, and drop the final segment only when the row ends with an unescaped pipe | `guard` | the deleted row reader in `record_shape` | **not taken** — it patches two guesses and leaves the third, which is that anything here guesses at all |
| 1 | " | " | 1b enable the parser's table rule and read rows through the owner, deleting the reader | `converge` | `markdown_links.PARSER`, `markdown_links.table_rows`, `record_shape.table`, `record_shape.Table.column`, and the reader this deletes | **taken** |
| 2 | A Record integrity section that holds no table this can read answered the same as a record carrying no such section, so a malformed table passed | MALFORMED-TABLE-READS-CLEAN | 2a report a section that is present and holds no readable table | `distinguish` | `record_shape.record_defects` | **taken** |
| 3 | The two registry conditions this range measured lived only in a module docstring and in commit prose | — | 3a record both where development judgment reads them | `declare` | `development-knowns.yaml`, the new `record-shape-cannot-read-a-row-subject` and `lifecycle-partition-unreadable-in-prose` entries | **taken**, with the authorization `AGENTS.md` requires |

### Why `1b` rather than either correction the input proposed

The input offers two: parse through the repository's CommonMark owner, or restrict the escape to
punctuation. The first as written is not available and the second is not enough.

**Not available as written**: `markdown_links.PARSER` was `MarkdownIt("commonmark")`, and a table is
GFM rather than CommonMark — measured, the preset emits no table token at all. So the owner could
not parse a table until its table rule was enabled, and that is why a reader had been written beside
the caller in the first place.

**Enabling it was the unmeasured part, and measuring retired the objection.** An earlier round in
this range declined exactly this on the ground that turning the rule on changes tokenization for the
four operations that share the parser. That was never measured. It was measured now, over every
Markdown file this repository tracks: every answer all four operations give is identical with the
rule on and off. The concern was real and false.

**And the owner is right about a third case neither the input nor this repository had considered**: a
row with no outer pipes at all. GFM permits it, the hand-written reader dropped a cell from it, and
`1a` would not have fixed that because nobody thought to test it. That is the argument for an owner
over a patch, stated as a case rather than as a principle.

## Pattern

**Three times in this range an unmeasured concern produced a worse decision, and this is the third.**
A component design called the paired-optional owner marginal because the invariant had never been
violated at the sites implementing it — refuted when the next site violated it twice. A planning
round put a table reader outside `markdown_links` because "the operation needs no parser" — refuted
here, where the operation needed the parser for exactly the two things it got wrong. And a round
declined to enable the table rule because it "changes tokenization for five existing operations" —
refuted by measuring 121 files and finding no change.

Each concern was plausible, each was cheap to measure, and none was measured before it decided
something. The shape is not carelessness about facts; it is treating a cost as known because it is
easy to state. What ends it is not a rule about parsers: it is that a stated cost with no
measurement beside it is a hypothesis, and this range has now spent three rounds paying for
hypotheses.

**The second shape, and the input found it: a repair can rest on the defect's own premise.** The
previous round read "a row missing its trailing pipe loses a cell" as the situation and repaired
which cell got blamed for the loss. It wrote a test asserting the loss was correct. A review that
went to the grammar rather than to the code found that the loss was itself the defect, and the test
had frozen it. A finding whose repair encodes the finding's premise is the hardest kind to see from
inside the round that made it, and the only thing that caught it was a producer reading the spec
instead of the diff.

## Coupling

- `1a` is **voided by** `1b`, and would have left the no-outer-pipes case standing.
- `2a` is independent, and was found by a test written for `1b` rather than reported by the input.
- `3a` is independent of both.

## Dispositions

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| ESCAPE-EATS-A-NON-PUNCTUATION-PAIR — a row reader consumed any character after a backslash, so a legal cell lost its backslash and two distinct finding ids collided under one | 1 | carried | accept | — |
| TRAILING-PIPE-ASSUMED-MANDATORY — a row reader dropped its final segment unconditionally, so a legal complete row written without GFM's optional trailing pipe was reported as missing the column it carried | 1 | carried | accept | — |
| MALFORMED-TABLE-READS-CLEAN — a Record integrity section present but holding no readable table answered as a record carrying no such section | 2 | new | accept | — |

Three findings against the input's two. The third is not a defect the input missed in the tree it
reviewed — it is one this round's own repair produced and a test written for that repair caught, in
the same turn. Recorded as a finding rather than folded into `1b` silently, because a reader
comparing the input's count to this record's is owed the reason they differ.

**Where this round disagrees with its input, and it changed the repair rather than the verdict.**
Both findings hold exactly as reported, and both corrections the input proposes are the wrong ones:
the first is unavailable without a change the input does not name, and the second patches two guesses
while leaving the third. The reasoning is above. The input's Structural Cause is right and is what
picked `1b` — that both findings come from implementing table grammar independently of the declared
owner.

## Carried forward

| Finding | Prior disposition | Original reason, unchanged | Closure condition not established |
|---|---|---|---|
| ABSENT-CLAIM-AS-MISMATCH | accept | a Record integrity row can convict on a claim the input never made, because nothing ties the row's Result to whether its `Input claim` cell names a claim at all | 2 — unchanged by this range, and now registered as `record-shape-cannot-read-a-row-subject` so the boundary is read by development judgment rather than by a docstring alone |
| SELFCHECK-FOLDED-INTO-THE-INPUT-AUDIT | accept | a fact about the record being written can be filed in the table that audits the input, because the two tables' subjects are stated in prose and enforced by nothing | 2 — narrowed by key-set closure and not removed, which the same registry entry records |
| TRAILING-WHITESPACE-UNSEEN | accept | nothing in this repository sees a trailing space, in any file | 2 — the input confirms the instances are gone; the recorded cause is the absence of a check, weighed and not bought |
| TRIGGER-KEYS-ON-THE-WEAKEST-AXIS | accept | the condition for building the derived check tests a row's Result where the defect is in its subject | 1 — its units are `triage-only` |
| LEDGER-TABLE-ROUNDS | out of scope in earlier rounds | unchanged | 1 — its unit is `triage-only` |
| LIFECYCLE-OMITS-THE-NAMED-PRIOR | accept | a lifecycle self-check answered `pass` by counting the ids the record had placed rather than by enumerating the prior record's open dispositions | 1 — `triage-only`, and now registered as `lifecycle-partition-unreadable-in-prose` for the reason no check can reach it |
| REVIEW-COVERAGE-AS-FINDING | decline | a review's coverage claim is not a defect of the registry it is recorded in | — declined; no new evidence |

## Closed

| Finding | Prior disposition | Code evidence the cause no longer holds | Input evidence |
|---|---|---|---|
| DECLARED-GUARDS-ONE-PAYLOAD | accept | `record_shape.Declared` holds one payload through `record_shape.Shape`, and `outcome.paired` guards it, so no unread state carries a missing reason | `record_shape` and `outcome` both `gate-reviewed` at Gates 1-5; the input re-reports neither and its Ledger records `outcome.paired` as enforcing the state |
| INVARIANT-SPELLED-TWO-WAYS | accept | no hand-written form of the predicate remains; `outcome.paired` is the only one and all five types call it | same |
| EMPTY-SCOPE-READS-AS-CLEAN | accept | `record_shape.check` reports a missing directory and an empty corpus as distinct diagnostics | same |
| TABLE-BODY-HAS-NO-NAME | accept | `record_shape.Table` names the header and the body apart | same, and the input's Ledger lists `table` as separating them |
| TEST-ROOT-BY-CWD | accept | the suite resolves the repository from `record_shape.ROOT` | `focused tests` are `gate-reviewed` and the input reports the suite passing |
| PROSE-WIDTH-UNENFORCED | accept | no non-table prose line in either record exceeds the stated width | the input ran `git diff --check` and reports it passing |
| NO-OP-COMPREHENSION | accept | the expression is gone, and the reader holding it has been deleted entirely | `record_shape` `gate-reviewed` |
| SORT-TO-COUNT | accept | `record_shape.main` counts without sorting | same |

## Out of scope this round

**REVIEW-FILED-A-VIOLATION-AS-A-VERIFIED-CLAIM, PARAGRAPH-SPLIT-NOT-REFLOWED,
FIXTURE-READ-AS-PRODUCT, COVERAGE-ENUMERATION-ABSENT, RAWSCORES-PROVISIONAL, F-11, F-12.** None of
their units is among the input's locations. The three declined ones keep their dispositions.

## Undetermined

`none`. The input enumerates four coverage sets, which is what empties this section.

## Recurring

**ESCAPE-TESTED-NOT-CONSUMED and RESULT-READ-BY-POSITION**, both returning under the new ids above
after their recorded repairs landed over their full Reach — which under this skill's test means the
stated cause was wrong rather than the Reach short.

It was wrong in the same way twice. The escape finding was recorded as a lookbehind to replace, and
the replacement was another hand-written scan; the cause was that the grammar had no owner here at
all. The trailing-pipe finding was recorded as a wrongly-blamed cell, taking the cell's loss as the
situation; the cause was that the loss should never have happened. Both re-derive to cause 1, and
the repair taken deletes the reader rather than correcting it — which is the first repair for either
that removes the thing admitting the next instance.

## Ungrouped

`none`.

## Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass — counted from the previous record's own tables, which left seventeen ids open: its ten Dispositions rows and its seven Carried forward rows. Two of the ten are re-reported here and sit in Dispositions, eight are Closed. Of the seven carried, all seven remain Carried forward. Two plus eight plus seven is seventeen, and Out of scope this round holds the seven the round before had already placed there. Undetermined is empty |
| Every accepted cause carries at least one repair with an enumerated Reach | pass — cause 1 carries `1b`, taken, whose Reach names `markdown_links.PARSER`, `markdown_links.table_rows`, `record_shape.table` and `record_shape.Table.column`; cause 2 names `record_shape.record_defects`; cause 3 names the two registry entries by id |
