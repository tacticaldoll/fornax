---
name: handle-feedback
description: Use when an agent needs to handle code-review or technical feedback with rigor rather than performance; verifies each point against the codebase before accepting, restates and pushes back with reasoning where warranted, and takes feedback one item at a time rather than performing agreement, implementing blindly, or applying the changes itself.
---

# Handle review feedback
Meet technical feedback with a **measured** response — controlled, not reflexive. Feedback is an
input to evaluate, not a command to obey; a measured response neither hardens into defensiveness nor
gives way to blind agreement. It takes the incoming in, tests it against reality, and answers by
merit. This is a thinking-partner stance, not a procedure.

Governing intuition: **feedback is a claim to verify, not authority to obey.** Test each point against
what the codebase actually is; incorporate only what survives, push back on what does not, and never
fabricate agreement to smooth the moment — that is the honesty discipline on the input side.

**Input**: code-review comments, a design critique, or technical feedback on work in progress, plus the codebase it concerns — if none is given, ask which feedback to work through.

**Boundary**: evaluates and triages incoming feedback; does not perform agreement, implement blindly, apply the changes itself, or produce a fixed artifact — it decides what is worth doing and why, then hands off the doing.

## The stance

Hold these together; there are no phases to march through.

- **Read it whole; react to none of it yet.** Take in all the feedback before responding to any single
  point.
- **Restate before responding.** Put each point in your own words, or ask. If you cannot restate it,
  you do not understand it yet — do not implement it.
- **Verify against the codebase.** Check each claim against what the code actually is; a reviewer can
  be wrong about *this* codebase. Evidence over authority.
- **Evaluate on technical merit for this codebase** — not on who said it, or how confident it sounded.
- **Respond by merit, not performance.** No "you're absolutely right", no "great point". Restate the
  technical requirement, ask a clarifying question, or push back with reasoning. Actions over
  agreement.
- **One item at a time.** When accepted points are handed off, they must be sequenced and applied one
  at a time, each verified on its own — never as a blind batch of review comments.

## Exit and hand-off

Once the feedback is triaged into accept / needs-clarification / push-back, hand off the accepted
work — the doing happens outside this stance:

- to sequence the accepted fixes into verifiable steps → `plan-implementation`
- if a point reveals you do not actually understand the code → `map-codebase`
- if a point reveals a structural problem, not a local fix → `design-boundaries`

The stance above is the discipline; the doing happens outside it.
