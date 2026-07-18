---
name: explore-intent
description: Use when an agent needs to explore intent, requirements, and direction through dialogue before any building; holds a no-stakes, codebase-grounded thinking-partner stance that surfaces options and tradeoffs one question at a time and resists premature convergence, rather than implementing, designing component structure, or planning the work.
---

# Explore intent
Hold the problem **open** — keep the possibilities live and moving — until the intent
is clear enough to let a direction *settle*. This is a thinking-partner stance, not a procedure:
a no-stakes exploration of what to build and why, before anyone commits to how.

Governing intuition: **the failure this resists is solving the wrong problem well.** Keep the problem
open until you can actually see it; widen before you narrow; and — because this is a coding
context, not abstract ideation — ground every option in the codebase that would carry it, not in the
abstract.

**Input**: a vague idea, feature, change, or direction to explore, plus the codebase it would live in — if the code the options depend on is unfamiliar, map it first with `map-codebase`. There is no fixed output; exploration ends in a shared understanding you hand off.

**Boundary**: explores and clarifies through dialogue; does not implement, design component structure, plan the work, decide for the user, or produce a fixed artifact — it hands off at the edge.

## The stance

Hold these at once; there are no phases and no order to march through.

- **One question at a time.** Ask, listen, let the answer reshape the next question. Do not fire a
  batched questionnaire — a real dialogue follows the answers.
- **Widen before you narrow.** Surface alternatives, analogies, and counter-examples before
  converging. Name the tradeoffs of each, not just your front-runner.
- **Ground options in the code.** Weigh each option against what the codebase actually is — its
  constraints, existing patterns, and prior art — not against an idealized system. If you do not yet
  understand the relevant code, say so and map it first (`map-codebase`).
- **Surface the assumptions.** Put the unstated on the table: what is being assumed about users,
  scale, constraints, and what "success" means.
- **No stakes.** Nothing is being written or committed here, and saying so is what lets the
  exploration stay honest. Ideas are cheap while nothing is committed.
- **Resist premature convergence.** The pull toward a solution before the problem is understood is
  the thing to resist. When you feel it, name it and stay open until the intent is clear.

## Exit and hand-off

Exploration ends when the intent, the requirements, and a chosen direction are clear enough to act
on. At that point you may summarize the clarified intent in a few lines — a shared understanding, not
a spec — then hand off; do not carry the work further yourself:

- to design the component structure → `design-boundaries`
- to plan the implementation work → `plan-implementation`
- to understand code the direction depends on → `map-codebase`
- if the question is whether an idea should become a skill → `scope-new-skill`

Keep any exit summary light. The structured artifacts are the downstream skills' job, not this one's.

The stance above is the discipline; the doing happens outside it — do not decide for the user, only
help them see clearly and choose.
