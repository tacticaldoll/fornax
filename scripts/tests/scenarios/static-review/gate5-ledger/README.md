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

## Results — 2026-08-25, 5 reps per arm, fresh context each, every sample read by hand

| Measure | control | treatment |
|---|---|---|
| Every unit answered (job clause + dependency origin) | 0 / 5 | 5 / 5 |
| Says layering was `inferred` when none is declared | 0 / 5 | 5 / 5 |
| Judges interface minimality against in-scope call sites only | 0 / 5 | 5 / 5 |
| Emits `Rows in this section are not findings.` | 0 / 5 | 4 / 5 |

Control output is finding-shaped: a numbered defect list in which units appear only as the subject of
a defect. Treatment output is ledger-shaped: one row per unit first, findings after. Control varied
(6/6/6/7/7 findings, three arms volunteering a positive section and two not); treatment converged so
far that one job clause — `format one invoice as a locale-tagged display string` — is word-identical
across four independent reps. Convergence is the protocol's own signal that wording has landed.

## What this does not show

The treatment arm received the new wording **and** the Ledger table spec, because that is what 0.4.1
ships together. It therefore cannot separate "the wording binds" from "a table was supplied to fill".
Two of the four measures are partially separable: `inferred` layering and the call-sites minimality
rule appear only in `gates.md`, never in the table spec, and the treatment arm applied both 5/5.

Isolating the wording alone needs a third arm — new `gates.md`, no table spec — which was not run.

## A correction this produced

`gates.md` described the failure as a gate "answered by the cheapest evidence in reach, an
import-direction scan across modules, **which reads as passed while no unit was opened**". No control
arm read as passed: all five failed the gate and analysed both files substantively. What reproduced is
weaker — clean units are never opened as units, so their status goes unstated. The wording works; that
sentence overstates what it was fixing.

The sentence is **left standing on purpose**. Editing it changes the text this result measured, so the
currency guard would drift the entry the moment the edit landed — correctly, because the evidence
would no longer describe what ships. The repair costs a re-run, and that price should be paid
deliberately rather than absorbed by quietly re-recording a fingerprint against prose nobody measured.
