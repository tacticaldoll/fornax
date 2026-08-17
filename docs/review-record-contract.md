# Review Record contract

The one place in this repository where a skill's output is another skill's input: `static-review`
produces a **Review Record**, and `triage-findings` reads it as its `**Input**:`. This file names
what crosses that seam, so a change to either half is visible as a change to both.

It describes the pair as it stands; it is not a published interface. Nothing parses a Review Record,
no host reads this file, and **neither skill links to it** — a skill folder is a portable package
boundary and must not depend on a path outside itself. Maintainers of the pair are the audience.

**Status**: neither half's current wording has been exercised by a fresh-context run since the last
several revisions; `scripts/tests/scenarios/triage-findings/README.md` records what has been run and
what remains a release blocker. Read the field list as current, not as settled.

## What crosses

| Field | Produced by | Read by | What the consumer does with it |
|---|---|---|---|
| `Source` | Phase 0 | Phase 0 | names what the round covers |
| `Calibration` | Phase 1 | Record integrity | reconciled against the gates the index records as opened |
| `Coverage` | Phase 3 inventory | Phase 0, Phase 1, Record integrity | decides prior-scope membership, and gates closure |
| `Verdict` | Phase 4b | Record integrity | reconciled against the gate the index shows |
| Gate Index | Phase 4 | Record integrity, Phase 1 | which gates opened, and at which one a finding sits |
| Gate finding rows | Phase 4 | Phase 0, Phase 1 | the findings themselves; each row is a `file:line` |
| Structural Causes | Phase 4c | Phase 2 | a cause the review already reached, so triage does not re-derive it |
| Against-Contract, Claims Verified | Phase 4b | Phase 1 | the same defect can arrive here *and* as a gate finding |

## Rules that hold the two halves together

- **Coverage is the only thing that licenses a closure.** A prior finding the review did not
  re-report is closed only if the unit was `gate-reviewed`; a `triage-only` or `unread` unit cannot
  close a finding by silence. This is why `Coverage` enumerates its three sets rather than stating a
  verdict-shaped summary.
- **Membership needs the enumeration.** `Coverage: complete` without an enumerated set does not let
  the consumer decide whether a prior disposition was in scope; that produces `undetermined`, which
  is a compatibility state for foreign records and should never arise from this pair.
- **Identity is not a line number.** The producer emits `file:line`; the consumer keys findings by
  what they violate plus the unit that carries it, so a line that moves does not create a new
  finding. The producer does not need to emit an id, but it must name the unit clearly enough that
  one can be derived.
- **One defect can arrive three times** — as a gate finding, an Against-Contract row, and a refuted
  claim. The consumer collapses them to one finding and records every source id. The producer should
  not deduplicate across its own tracks; each track answers a different question.
- **Vocabulary that must not collide across the seam.** `not inspected` names a *gate* the
  calibration never opened. `unread` names a *unit* never opened. `triage-only` names a unit that
  received Phase 2's rapid checks and no gates. The two axes are reported in the same record, so one
  word for both makes the record unreadable by its own consumer.
- **A claim the producer does not emit is `not claimed`.** The consumer must not read a missing field
  as a passing one — see the Output Records section of `AGENTS.md`.

## Open seam defects

- **`Finding count` has no producer.** `triage-findings`' Record integrity table reconciles a stated
  finding count against the rows the record contains, but `static-review`'s report format emits no
  such field — its `Triage` line counts *files* (Red/Yellow/Green), not findings. Against a real
  Review Record this check is `not claimed` every time, which makes it decoration rather than an
  integrity anchor. The scenario fixture supplies a `Finding count` line that the producer never
  writes. Either `static-review` states the count, or the check row goes.

## When this file is wrong

It has no test and no validator. It is stale the moment either half changes without it, and the only
thing that catches that is a maintainer reading both. Treat a mismatch between this file and either
`SKILL.md` as a defect in this file until the skills are shown to disagree with each other.
