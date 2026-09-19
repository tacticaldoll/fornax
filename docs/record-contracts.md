# Record contracts

What crosses a producer-to-consumer seam in this repository. `static-review` produces a **Review
Record**, which `handle-feedback` and `triage-findings` name as `**Input**:`; `assess-knowledge`
produces a **Knowledge Assessment Record**, which `save-knowledge` and `write-learning-report` name.
This file says what crosses each seam, so a change to a producer or a consumer is visible. The
Inventory below is generated, so a seam added later appears there without this sentence being
rewritten.

It describes these relationships as they stand; it is not a published interface. Nothing parses a
Review Record, no host reads this file, and **none of the skills link to it** — a skill folder is a
portable package boundary and must not depend on a path outside itself. Maintainers of these seams
are the audience.

The consumers use it at different depths. `handle-feedback` treats the complete record as technical
feedback to verify and routes it to `triage-findings`; it does not interpret individual fields or
produce a disposition. `triage-findings` audits the record, reads its fields, and returns a
session-local Disposition Record when the user asks for one. The field-level obligations below
therefore belong to the Review Record seam; the repository does not keep a disposition ledger.

**Status**: deterministic fixtures cover the current `static-review` → `triage-findings` record
shape. The fresh-context behavioral evidence recorded in
`scripts/tests/scenarios/triage-findings/README.md` predates the current wording; read its dated
results and release blockers separately from this current field inventory.

## What crosses the Review Record seam

| Field | Produced by | Read by | What the consumer does with it |
|---|---|---|---|
| `Source` | Phase 0 | Phase 0 | names what the round covers |
| `Calibration` | Phase 1 | Record integrity | reconciled against the gates the index records as opened |
| `Coverage` | Phase 3 inventory | Phase 0, Phase 1, Record integrity | decides prior-scope membership, and gates closure |
| `Verdict` | Phase 4b | Record integrity | reconciled against the gate the index shows |
| Gate Index | Phase 4 | Record integrity, Phase 1 | which gates opened, and at which one a finding sits |
| Gate finding rows | Phase 4 | Phase 0, Phase 1 | the findings themselves; each row is a `file:line` |
| `Findings` | Phase 5 header | Record integrity | reconciled against the rows the record contains; counts every finding row, not the `Triage` file counts and not the Ledger's rows |
| Structural Causes | Phase 4c | Phase 0, Phase 1, Phase 2 | a row naming a finding is that finding's stated cause and is verified like any other; a row naming none is itself a finding, keyed by what it states and the unit that carries it |
| Against-Contract, Claims Verified | Phase 4b | Phase 1 | the same defect can arrive here *and* as a gate finding |
| Responsibility & Dependency Ledger | Phase 5, when Gate 5 opened | Phase 0, Record integrity | required output the producer must show rather than a claim crossing the seam; its rows are not findings, so Phase 0 does not flatten them and the count does not include them |

## What crosses the Knowledge Assessment Record seam

`assess-knowledge` produces one table, and its columns are what cross. The generated Inventory below
cannot show them: the output template marker selects a template by record identity and the inventory
extracts its visible headings, so it reports the record's header fields and never sees a cell.

| Element | Produced by | Read by | What the consumer does with it |
|---|---|---|---|
| `Nature` column | Phase 2, Nature | `write-learning-report` Phase 3, `save-knowledge` Phase 1 | `write-learning-report` maps it to a report structure and its mapping must cover every value this column can take; `save-knowledge` reads it as input-resolution guidance and owes no per-value answer |
| `Maturity` column | Phase 2, Maturity | `save-knowledge` Phase 1, `write-learning-report` Phase 1 | guidance on whether the topic is settled enough to act on |
| `Attribution` column | Phase 2, Attribution | `save-knowledge` Phase 1, `write-learning-report` Phase 1 | routes the topic; each consumer answers every value, including the one that sends it nowhere |
| `Volume` column | Phase 2, Volume | `save-knowledge` Phase 1, `write-learning-report` Phase 1 | guidance on whether the topic sustains a standalone artifact |
| `Expansion Cues` column | Phase 2, Expansion Cues | nobody | diagnostic metadata for the reader; it crosses no seam and obliges no consumer |

Two obligations follow, and no check carries either:

- **A value added to `Nature` or `Attribution` obliges the consumers that answer per value.** The
  mapping in `write-learning-report` Phase 3 names a structure per `Nature` value, and each
  consumer's Phase 1 table answers per `Attribution` value; `save-knowledge` reads `Nature` without
  a per-value answer and is not obliged by a value added to it. A value with no row is a record the
  consumer reads and has no action for. This has happened: `Neither` was added to the producer and
  neither consumer answered it until the change that wrote this section.
- **Renaming a column is a change to the record's required output shape**, which the versioning
  rules place at minor inside an unchanged record identity. The major in the identity moves only
  when an existing consumer can no longer read the record at all.

## Inventory

Generated from the producer and consumers by `scripts/seam_contract.py`; `--check` fails when it no
longer matches them. The seam list is derived from matching optional `skill-interface.yaml`
declarations rather than prose, so another seam appears without an edit and zero seams is a clean
answer.

It is an inventory, not a reconciliation: it says what the producer's template declares, and says
nothing about which elements the consumer reads or whether the consumer names one that does not
exist. Both defects this file has recorded were found by reading the inventory against the table
above, which is a human act — the generation exists so the inventory cannot go stale while that
table does.

<!-- SEAM-INVENTORY:START (generated by scripts/seam_contract.py — do not edit by hand) -->

### `static-review` → `handle-feedback` — Review Record v1 (text/markdown)

| Element | Kind |
|---|---|
| `Source` | field |
| `Calibration` | field |
| `Triage` | field |
| `Coverage` | field |
| `Findings` | field |
| `Verdict` | field |
| `Not executed` | field |
| `Review Record` | section |
| `Gate Index` | section |
| `Security Triage Alert` | section |
| `Against-Contract` | section |
| `Claims Verified` | section |
| `Structural Causes` | section |
| `Responsibility & Dependency Ledger` | section |
| `Gate N: [name]` | section |
| `Structural Appendix` | section |

### `assess-knowledge` → `save-knowledge` — Knowledge Assessment Record v1 (text/markdown)

| Element | Kind |
|---|---|
| `Date` | field |
| `Topics identified` | field |

### `static-review` → `triage-findings` — Review Record v1 (text/markdown)

| Element | Kind |
|---|---|
| `Source` | field |
| `Calibration` | field |
| `Triage` | field |
| `Coverage` | field |
| `Findings` | field |
| `Verdict` | field |
| `Not executed` | field |
| `Review Record` | section |
| `Gate Index` | section |
| `Security Triage Alert` | section |
| `Against-Contract` | section |
| `Claims Verified` | section |
| `Structural Causes` | section |
| `Responsibility & Dependency Ledger` | section |
| `Gate N: [name]` | section |
| `Structural Appendix` | section |

### `assess-knowledge` → `write-learning-report` — Knowledge Assessment Record v1 (text/markdown)

| Element | Kind |
|---|---|
| `Date` | field |
| `Topics identified` | field |

<!-- SEAM-INVENTORY:END -->

## Rules that hold the Review Record seam together

These govern `static-review` → `triage-findings` and are not general to every seam here; the
Knowledge Assessment Record has its own obligations section.

- **Coverage is the only thing that licenses a closure.** A prior finding the review did not
  re-report is closed only if the unit was `gate-reviewed`, or was `partially-gate-reviewed` and the
  relevant gate is among those explicitly opened. A partial unit missing that gate, a `triage-only`
  unit, or an `unread` unit cannot close a finding by silence. This is why `Coverage` always
  enumerates each set and the gates opened for every partial unit.
- **Membership needs the enumeration.** `Coverage: complete` without an enumerated set does not let
  the consumer decide whether a prior disposition was in scope; that produces `undetermined`, which
  is a compatibility state for foreign records and should never arise in the
  `static-review` → `triage-findings` seam.
- **Identity is not a line number.** The producer emits `file:line`; the consumer keys findings by
  what they violate plus the unit that carries it, so a line that moves does not create a new
  finding. The producer does not need to emit an id, but it must name the unit clearly enough that
  one can be derived.
- **One defect can arrive more than once** — as a gate finding, an Against-Contract row, and a refuted
  claim. The consumer collapses them to one finding and records every source id. The producer should
  not deduplicate across its own tracks; each track answers a different question.
- **Vocabulary that must not collide across the seam.** `not inspected` names a *gate* the
  calibration never opened. `unread` names a *unit* never opened. `triage-only` names a unit that
  received Phase 2's rapid checks and no gates. `partially-gate-reviewed` names a unit and must list
  the gates it received. Both axes are reported in the same record, so one word for both makes
  the record unreadable by its own consumer.
- **A claim the producer does not emit is `not claimed`.** The consumer must not read a missing field
  as a passing one — see the Output Records section of `AGENTS.md`.

## Open seam defects

`none`. Both defects this file surfaced on the day it was written are settled:

- **Structural Causes had no reader.** Settled by naming what each row kind is. A row that names a
  finding is that finding's stated cause, which Phase 2 already knows how to verify. A row that names
  none is itself a finding: it states what is wrong and the unit that carries it, so Phase 1 can key
  it, and it was filed as a cause only because the gate that would have carried it never opened.
  Restricting Phase 4c to linked rows was the alternative and was declined — case 2 exists for a
  cause that belongs to no reported finding, which is the case that motivated the phase.
- **`Finding count` had no producer.** Settled by `static-review` emitting `Findings`, defined as
  every finding row rather than the `Triage` file counts. Dropping the check was the alternative and
  was declined: a declared count is what detects a record truncated in transit, and these records are
  transcribed between sessions by hand.

## When this file is wrong

The **Inventory** cannot go stale: `scripts/seam_contract.py --check` runs with the other gates and
fails the moment a declared record shape moves.

Everything else here can. The `What crosses` tables, the rules, and the settled defects are all
hand-written, and nothing compares them to the skills — the generated block sits above them so a
maintainer reading one reads the other, which is the whole mechanism. Treat a mismatch between this
file and a `SKILL.md` as a defect in this file until the skills are shown to disagree with each
other.
