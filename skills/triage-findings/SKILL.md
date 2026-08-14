---
name: triage-findings
description: Use when an agent needs to decide what to do with a static review's findings before any fix is planned; groups findings into shared causes, lists the repairs each cause admits and enumerates what each one touches, and records a per-finding disposition that carries into the next review round, rather than sequencing the fixes, editing code, or re-reviewing it.
---

# Triage review findings
Use this skill to turn a list of review findings into decisions: what the causes are, which repairs
each cause admits, and which findings are accepted, declined, or deferred.

Governing intuition: **a finding names a place; a cause names the thing to change.** A review reports
locations, so a repair that touches only the location leaves the cause standing and the same findings
come back next round. Name the cause, then list the repairs it admits and **enumerate** what each one
touches — a repair confined to the finding's own place is then visible as exactly that, with nothing
to classify and no bucket to mis-assign.

**Input**: a review findings list — a `static-review` Review Record, findings pasted inline, or a path to either — plus the prior round's Disposition Record when one exists, and the codebase the findings concern; if none is given, ask which findings to triage.

**Boundary**: decides causes, repairs, and dispositions — produces a Disposition Record; does not sequence or apply the repairs, review the code or add findings of its own, or persist the record itself.

## Workflow

### Phase 0: Resolve the findings and the prior round

Normalize the input into one flat list of findings, whatever shape it arrived in — a Review Record's
gate tables, its non-gated tracks, a pasted list, or a file holding either.

Audit the Review Record before reading the code: reconcile its Verdict with the Gate Index, its
stated finding count with the finding rows it actually contains, and its Coverage claim with the
units and gates it enumerates. Preserve each mismatch for Record integrity; do not silently repair
the input by reinterpreting a count, scope, or status.

Then load the prior round:

- When a prior Disposition Record exists, every finding it declined or deferred **keeps that
  disposition and its recorded reason**. Reopen one only on new evidence, and name the evidence.
- Record **this round's scope** — the files, diff, or component the input covers — and compare each
  prior disposition against it. One that lies **inside** this scope and that the input did not
  re-report is a closure candidate, not automatically carried or closed. One that lies **outside** it
  is `out of scope this round`: this round looked elsewhere and says nothing about it. These slots
  are in the record (Phase 5); a scope change is not a closure.
- Membership is decidable only when the input **enumerates** what it covered. When the input states a
  scope without enumerating it, a prior disposition's membership is `undetermined` — record it as
  that rather than deciding it. Undetermined is neither carried nor closed. Re-evaluate it from the
  next round's input: a matching re-report enters the ordinary finding flow; newly enumerated scope
  decides inside versus outside; another unenumerated scope leaves it undetermined.
- When none exists, record `first round`. Do not infer a prior decision from the code.

### Phase 1: Give each finding a stable identity

Key each finding by **what it violates plus the unit that carries it** — not by `file:line`. The unit
is the smallest named code or document element that owns the violated contract (function, type,
module, manifest, section); use the file only when no smaller stable owner exists. Preserve the
logical unit when code moves or is renamed and the same contract remains. A line number drifts with
the next edit, so a line-keyed finding cannot be matched across rounds, and a finding that cannot be
matched cannot be closed.

One defect often arrives more than once: as a gate finding, again as a contract row, again as a
refuted claim. Findings that key alike are **one** finding — record every source id against it rather
than triaging the same defect several times.

Match every finding against the prior record before treating it as new. Findings in the same unit
that violate different contracts remain different identities. When one reappears, compare the
recorded repair and its Reach with what actually changed:

- **No recorded Reach changed** — the accepted repair never landed; a repair nobody attempted is no evidence about
  anything. Keep the **disposition and its reason**, and re-derive the repairs in Phase 3. A
  disposition is a decision, so freezing it is what stops re-litigation; a repair is a reading of the
  cause, so freezing it would preserve a misreading the code never justified.
- **Only part of the recorded Reach changed** — the repair did not fully land. Keep the disposition
  and reason, record the changed and untouched locations, and do not call it recurring.
- **The complete recorded Reach changed** — the repair landed and the finding survived. Record it as
  recurring, verify whether the original cause still holds, and re-derive the repairs in Phase 3;
  either the Reach was incomplete or the stated cause was wrong.

For each closure candidate — a prior finding inside an enumerated scope that the input did not
re-report — verify all of the following before closing it:

1. The input gate-reviewed the unit and relevant gate, or explicitly verifies the repair. A
  `triage-only` or uninspected unit cannot close a finding by silence.
2. The code at the recorded cause shows that the cause no longer holds.
3. The input does not contradict the closure elsewhere in its record.

When all three hold, record the finding as `closed` with the code and input evidence. When the cause
still holds, or any closure evidence is unavailable, carry the prior disposition and original reason
forward; say which closure condition was not established. Review silence alone is never closure.

### Phase 2: Group findings into causes

For each finding ask: **what one change would remove it?** Findings that answer the same way share a
cause.

- A cause is not a category. "Naming" is a gate; "the module exposes two responsibilities under one
  name" is a cause.
- A cause is stated as the thing to change, not as the symptom that revealed it.
- **Verify the cause against the code.** A review states a cause as well as a location, and the stated
  cause can be wrong while the finding is real — a wrong cause points at a wrong repair. Check it, and
  when it does not hold, record the cause the code supports and say what the review claimed.
- A finding whose cause cannot be named from the code, or from the documents the code answers to,
  stays **ungrouped**. Do not invent a cause to make the table tidy — an invented cause produces a
  repair that fixes nothing.

### Phase 3: List the repairs each cause admits

A cause may admit more than one repair, and they are not interchangeable — one may correct prose where
another changes behaviour. **List every repair the cause admits**, not the one you would pick: a cause
recorded with a single repair hides the choice from whoever plans the work.

Each repair carries two things.

**Reach** — every location the repair touches, enumerated as `file:line`. Enumerate; do not classify.
Whether a repair is confined to the finding's own place, spans several, or dissolves them is then read
off the list itself.

**Kind** — what the repair does:

| Kind | The repair |
|---|---|
| `guard` | add the missing check where it is missing |
| `derive` | replace a written-down set with one computed from the source it must cover |
| `index` | replace a hand-written scan or matcher with lookup through an existing key or ordering capability |
| `converge` | delete one complete implementation of an operation and call the other implementation that already performs it |
| `restate` | correct prose, a spec, or a document |
| `declare` | record a limit or a count as governed policy |
| `forbid` | refuse an input that was admitted |

These seven are the values this skill's own use has produced, from one repository. The list is **not
closed**: a repair none of them fits is named in its own words and reported as a gap, never forced
into the nearest value. A cause whose repair is a decomposition of a unit, or a re-drawn seam between
units, is outside this vocabulary — do not invent a Kind for it; hand the cause on (Rules).

A cause whose repairs cannot be named from what the review reached has **none listed** — say so, and
say what would produce one. A cause the review reached through a blocked or unopened gate is the
common case.

When one repair's reason disappears once another lands, note which voids which. A repair that a
sibling makes pointless is not a second task.

### Phase 4: Disposition each finding

Decide per finding, not per gate, and never accept a batch because a review produced it.

- `accept` — the cause is real and at least one of its repairs is worth doing.
- `decline` — the finding does not hold for this codebase, or every repair costs more than the defect.
- `defer` — real, but not now; name what would make it now.

Every `decline` and `defer` carries a reason. The reason is the only thing that stops the finding
returning next round, so a disposition without one has not actually been made.

### Phase 5: Produce the Disposition Record

```markdown
## Disposition Record

**Source**: [the review record or list triaged]
**Scope**: [the files, diff, or component this round's input covers]
**Prior round**: [the record carried forward | first round]

### Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach (every location it touches) | Route |
|---|---|---|---|---|---|---|
| 1 | stated as the change, not the symptom | every source id | 1a | listed Kind \| `<action> (gap)` | `file:line`, … | where it goes |
| 1 | " | " | 1b | the alternative, when the cause admits one | `file:line`, … | " |

### Pattern

[Two or more causes sharing one shape: the shape, which causes hold it, and a pattern-level repair
that catches the next instance — repairing the instances does not remove the shape. `none` when no
shape recurs.]

### Coupling

[Repairs whose reason disappears once another lands, as `1b voided by 3a`. `none` when independent.]

### Dispositions

[Every finding reported by this round, including a stable id matched to prior history. A prior
finding not re-reported belongs in exactly one lifecycle section below — Carried forward, Closed, or
Out of scope this round — and is not duplicated here. A finding re-reported after it was Closed
returns here as `carried`; reappearance alone does not make it Recurring.]

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| id | # \| ungrouped | new \| carried | accept \| decline \| defer | why — not "as reviewed" |

### Carried forward

[Prior dispositions lying inside this round's scope that the input did not re-report: id,
disposition, the original reason unchanged, and which closure condition was not established. A
disposition leaves this section only when the closure test in Phase 1 proves its cause no longer
holds, never because the review stopped reporting it. `first round` when there is no prior record.]

### Closed

[Prior dispositions whose closure test passed: id, prior disposition, code evidence that the cause
no longer holds, and the input evidence that the relevant unit was reviewed without re-reporting the
finding. Preserve the stable finding id so a later re-report can match the closed history. `none`
when no closure is established.]

### Out of scope this round

[Prior dispositions this round's input did not cover, each marked `out of scope` when the input
enumerates what it covered, or `undetermined` when the input states a scope without enumerating it.
Neither carried nor closed either way. Their ids and count.]

### Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | what each says | whether they agree | pass \| mismatch |
| Finding count | stated count | current Review Record finding rows | pass \| mismatch |
| Coverage | stated scope and coverage | enumerated units and inspected gates | pass \| mismatch |
| Prior continuity | prior ids | each id's one lifecycle slot | pass \| mismatch |

[Code defects the review missed do not belong here — send those back for review.]

### Recurring

[Findings that came back after every location in a recorded repair's Reach changed: the stable id,
the prior repair and Reach, whether its cause still holds, and the newly derived repairs. This is
additional analysis for a current Dispositions row, not a mutually exclusive lifecycle slot. A
finding that was previously Closed is not Recurring merely because it appears in a later round.]

### Ungrouped

[findings whose cause could not be named, and what would settle each]
```

## Rules

- Decide only. Do not edit code, sequence the work, or put the record anywhere but your reply — no
  file, no published page, no external destination, however durable the caller needs it to be. When
  the prior record arrived as a path, that file is read-only input. Losing the record is a real cost
  and not yours to solve: say where it should be kept, and let the caller keep it.
- Triage only what the input reports. A defect in the code that the review missed is not yours to add
  — say so plainly and send the code back for review. A defect in the **record** is different: it is
  the input's own fitness, and you are its consumer, so it goes in Record integrity (Phase 5).
- List every repair a cause admits. Recording one where the cause admits two makes a choice that
  belongs to whoever plans the work, and hides it as if there were nothing to choose.
- Stay in lane; hand off at the boundary. Route each accepted repair by its Kind: a `restate` has no
  code handoff — name the document and who owns it, and stop there; for every other Kind,
  hand off to `plan-implementation`. Most repairs go there, and saying so is more honest than a
  routing table that reads richer than the work. Route a named Kind gap by the action it actually
  performs: a code repair goes to `plan-implementation` unless one of the structural cases below
  applies. When a cause's repair decomposes one unit,
  hand off to `plan-split`; when it redraws the seam between units, hand off to `design-boundaries`.
  When a cause cannot be named without tracing the fault, hand off to `diagnose-issue`; when settling
  it needs runtime evidence rather than static reading, hand off to `plan-testing`. For a fresh review
  of the code itself, route to `static-review`. Name the handoff rather than half-doing the other
  workflow's job.
