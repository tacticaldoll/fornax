---
name: plan-implementation
description: Use when an agent needs to turn a goal into an ordered, verifiable implementation plan before coding; slices the work into the smallest independently verifiable increments, sequences them by dependency and risk, and names each step's acceptance check rather than writing code, designing component structure, or planning a behavior-preserving split.
---

# Plan the implementation
Use this skill to **break** a goal into an implementation plan — add the work in small, controlled
increments toward the outcome, each one producing an observable signal that it landed. The output is
an **ordered task plan**: the increments, their dependencies and risk, and the acceptance check that
tells you each is done.

Governing intuition: **each increment must produce a signal you can see flip.** A task whose "done"
you cannot observe is not verifiable — reslice it until it has an acceptance check.
Prefer the smallest slice that proves something real and leaves the system working over a big step
you cannot verify midway; and order by what unblocks or de-risks the rest, not by what is easy.

**Input**: the goal to plan toward — a feature, fix, or change — plus its hard constraints; if none is given, ask what outcome the plan should reach.

**Boundary**: plans only — writes no code, scaffolds nothing, runs no build; produces the plan an implementer executes.

## Workflow

### Phase 0: Frame the goal and constraints

- State the goal as an **outcome** — what will be true when it is done — not as a task list.
- Capture hard constraints: behaviour that must not break, interfaces to honour, deadlines, and the
  tech the team already owns.
- Check the upstream boundary: unfamiliar code the plan touches → `map-codebase` first; an unsettled
  component structure → `design-boundaries` first; a behaviour-preserving decomposition → `plan-split`;
  a data migration or database schema change → `plan-migration`, whose phased backward-compatible model this skill does not carry.

### Phase 1: Slice into verifiable increments

Break the goal into increments, each one:

- **Independently verifiable** — produces an observable signal (a test, a check, a runnable
  behaviour), not just "code written".
- **The smallest slice that delivers a real signal** — thin, not trivial.
- **Leaving the system working** — no half-broken state committed between increments.

Prefer thin **vertical slices** (a little of each layer, end to end) over horizontal layers; each
vertical slice proves something works.

### Phase 2: Sequence by dependency, then risk

- Order so every task's prerequisites land first — the sequence must be dependency-correct.
- Among tasks free to reorder, pull the **riskiest or most uncertain** and the **most unblocking**
  work earlier: surface unknowns while there is time to react, and clear the widest downstream first.
  Do not front-load the easy work.
- Note **interlocks** — tasks that must land together — and any deliberately deferred.

### Phase 3: Define each step's acceptance check

For every task, name how you will know it is done: the test to write and pass, the behaviour to
observe, the check that flips green. A task without an acceptance check is not a task — it is a wish;
reslice it until it has one.

### Phase 4: Adversarially verify the plan

Attack the plan before finalizing:

- **Missing task** — is there a gap between increments (something assumed but never built)?
- **Unverifiable step** — any task whose "done" cannot be observed? Reslice it.
- **Hidden coupling** — do two "independent" tasks actually depend on each other?
- **Broken in the middle** — does any ordering leave the system unshippable between steps?

### Phase 5: Produce the implementation plan

```markdown
## Implementation Plan — [goal]

**Goal (outcome)**: [what is true when done]
**Constraints / non-goals**: [behaviour that must not break; out of scope; no design change here]

### Ordered tasks
| # | Task (increment) | Depends on | Risk | Acceptance check |
|---|---|---|---|---|
| 1 | thin vertical slice | — | low / med / high | the test or behaviour that proves it |

### Interlocks
[tasks that must land together, and why]

### Open risks / not planned
[unknowns to resolve first; work deliberately deferred or out of scope]
```

## Rules

- Plan only. Do not write code, scaffold, or run builds — produce the plan; an implementer executes
  it.
- Every task is independently verifiable. Name its acceptance check; a step whose "done" cannot be
  observed is not a task — reslice it.
- Smallest useful increments. Prefer thin vertical slices that each prove something and leave the
  system working over big steps you cannot verify midway.
- Order by dependency, then by risk and unblocking. Surface the riskiest unknowns early; do not
  front-load the easy work.
- Stay in lane; hand off at the boundary. To understand unfamiliar code the plan touches, point to
  `map-codebase`. To design the component structure the plan builds toward, point to `design-boundaries`.
  For a behaviour-preserving split of existing code, point to `plan-split`. To review the result once
  built, point to `static-review`. Name the handoff rather than half-doing the other skill's job.
