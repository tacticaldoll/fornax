# `static-review` Gate 5 ledger — micro-test

Maintainer-only behavioral evidence for the Gate 5 wording. Not part of the installed skill package.
Protocol: `skills/harden-skill/references/hardening.md`.

## What was measured

Whether the Gate 5 wording shipped in 0.4.1 makes a reviewer answer **per unit** rather than give one
gate-level verdict. Control is the wording immediately before that change; treatment is the shipped
wording plus the Ledger section of `skills/static-review/SKILL.md`.

- **Control** — `git show ab76ac4:skills/static-review/references/gates.md`
- **Treatment** — `gates.md` at the fingerprint the registry records, plus the Ledger section
- **Fixture** — `fixture/billing.py`, `fixture/reporting.py` (five units; one holds four jobs and
  reaches a global pool, an environment variable, and an inline HTTP client; four are clean)

## Prompt

Identical for both arms except which gate file is read.

```text
You are performing a static code review.

1. Read the gate definitions at <variant>/gates.md
2. Read the code under review: <fixture>/billing.py and <fixture>/reporting.py
   [treatment only] Read the Gate 5 report section spec at <variant>/ledger-section.md

Review this code at **Gate 5 only**. Do not review other gates.

Produce your Gate 5 result. Your final message IS the review output — return only that, no preamble.
```

## Results

Every sample read by hand, fresh context each, 5 reps per arm. The control is the wording
immediately before the change; arms B and C both carry the corrected wording, and differ only in
whether the Ledger table spec was supplied.

| Measure | control (prior wording) | B (corrected + table) | C (corrected, no table) |
|---|---|---|---|
| Every unit answered (job clause + dependency origin) | 0 / 5 | 5 / 5 | 5 / 5 |
| Says layering was `inferred` when none is declared | 0 / 5 | 5 / 5 | 5 / 5 |
| Judges interface minimality against in-scope call sites only | 0 / 5 | 5 / 5 | 5 / 5 |

**The rubric widened between rounds, and the control's zero is unaffected.** Round 1 scored the
control and the treatment against four units; round 2 scored arms B and C against five, adding
`InvoiceFormatter.__init__`. The fixture never changed — `scoring-round2.md` says it reused round
1's metrics, and it reused the fixture while widening the unit list. The control column above is
round 1's, beside arms scored at five, which the table does not otherwise say. It changes nothing
here: `raw-scores.md` records every control rep as producing no per-unit answer at all — "無任何
unit 有 job clause" — so no unit count could turn that into anything but a zero.

**The wording binds on its own.** Arm C had no table to fill and answered per unit anyway, naming
each unit's job in one clause and separating handed-in dependencies from reached-directly ones.
Several arm C reps volunteered a completeness statement — "no unit in scope is unopened" — without
ever seeing the spec that asks for one.

**The table supplies format, not substance.** Arm B's five reps are all tables; arm C's five are
per-unit prose sections in five slightly different shapes. Their *content* converges completely:
the same five units, the same job judgments, the same origin classifications, the same three units
passing. Convergence on substance is the protocol's signal that wording has landed; the table adds
convergence on shape.

**The correction did not cost anything.** Arm B matches the pre-correction treatment on all three
measures. Where it differs it is finer: three reps used `not determinable from the reviewed scope`
for a parameter type defined outside the scope, and one counted inline constants as reached
directly.

## On the no-guidance control

`harden-skill` requires one, and the control here is the prior wording rather than no text at all.
That is the same thing for this subject. A gate definition cannot be withheld and still leave a
Gate 5 to review at — an arm with no `gates.md` measures an invented gate, not this one. For a
behavior added to an existing document, the document without the addition is the no-guidance
condition, and the prior Gate 5 carried no per-unit requirement of any kind.

## The correction this evidence produced

The first round measured a `gates.md` sentence calling the failure one that "reads as passed while
no unit was opened". No control arm read as passed: all five failed the gate and analysed both files
substantively. What reproduces is weaker and more specific — clean units are never opened as units,
so their status goes unstated, and the gate reports the defects it found rather than the units it
examined.

The sentence was left standing in the first round because editing it drifts this record's
fingerprint by design. It was corrected in the second round together with the re-run that re-earns
the fingerprint, which is the order the currency guard is built to force.
