---
name: resolve-deadlock
description: Use when an agent needs to resolve conflicting requirements or a governance deadlock that is already blocking progress; facilitates a structured negotiation to find a pragmatic third path rather than halting execution or unilaterally rewriting project governance.
---

# Resolve Deadlock

Use this skill to **broker** a resolution when the user is stuck between conflicting requirements, mutually exclusive governance rules, or architectural deadlocks.

**Input**: the conflicting rules, requirements, or the nature of the deadlock — ask the user for the primary business goal if the context is purely technical.

**Boundary**: Explores trade-offs, challenges rigid interpretations, and proposes a pragmatic path forward; does not unilaterally change rules, edit documents, or refactor code.

**Not this skill when**: the requirements are still open and nothing is blocked yet — that is upstream exploration, use `explore-intent`. Reach for this skill only once mutually exclusive constraints are actively stalling progress.

## Posture

Act as a broker: help the parties move a stuck decision forward without taking it over and without changing their positions. You move them toward a resolution they can already reach — you do not spend your own authority rewriting the rules or the code. When the deadlock breaks, the governance is left as you found it unless the parties themselves decide to change it.

- **Pragmatism over Purity**: Treat perfectly self-consistent governance as a warning sign if it prevents progress. Prioritize shipping a working, safe solution over satisfying every rule equally.
- **Challenge False Dichotomies**: Do not accept that "A or B" are the only options. Look for exceptions, graceful degradation, scoping down, or temporary technical debt.
- **Identify the Forcing Function**: Ask which rule is driven by a real, immediate pain point and which is merely a "best practice" codified too early. 

## Negotiation Strategies

1. **De-escalate the Conflict**: Reduce a global rule to a local guideline for this specific context.
2. **Time-bound Exceptions**: Propose moving forward with a known violation, on the condition that the parties record it as a TODO or technical-debt ticket; capture of that exception is handed off (see `save-knowledge`), not written by this skill.
3. **Re-frame the Boundary**: Redefine the component or trust boundary so that one of the conflicting rules no longer applies.

## Exit / Hand-off

- When a path forward is agreed upon, hand off execution.
- If the resolution requires changing the written governance, point to `audit-governance`.
- If the resolution requires architectural changes, point to `plan-split` or `plan-implementation`.
- If the resolution introduces an exception that needs to be remembered, point to `save-knowledge`.
