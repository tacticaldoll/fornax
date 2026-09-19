---
name: scope-new-skill
description: Use when an agent needs to explore whether a vague workflow or knowledge process should become a skill; classifies skill type, outputs, resources, risks, and readiness rather than creating or editing skill files.
---

# Scope a new skill
Use this skill to explore a possible skill before creating or editing skill files. The goal is to
turn a vague intent into a clear implementation shape, or to decide that a skill is not warranted.

Mental model: **screen the intent**. Run the candidate through a fixed panel
of readiness dimensions (Phase 4) and report a verdict; only intents that survive the screen are
admitted as skills, and a failed screen is a valid, informative result.

Governing intuition: **decline is a first-class outcome** — explore to a clear implementation shape
or to a well-founded "do not create a skill"; never rubber-stamp a skill into existence.

**Input**: the proposed skill idea or workflow to evaluate — if the intent is too vague to classify safely, ask one clarifying question (Phase 1) before proceeding.

**Boundary**: explores and recommends a shape; does not create or edit skill files unless the user asks to implement after the exploration.

## Workflow

### Phase 1: Intent Capture

Identify the user's proposed capability in one sentence. Extract:

- The task or situation that would trigger the skill.
- The expected user-visible output or action.
- The agent hosts or environments the skill should support.
- Any known files, tools, APIs, policies, or project contexts involved.

Ask a clarifying question only when the intent cannot be safely classified from context.

### Phase 2: Type Classification

Read [references/skill-types.md](references/skill-types.md) when the type is unclear or when the
user asks about skill style. Choose one dominant type and any secondary types.

Use these first-pass signals:

| Signal | Likely Type |
|---|---|
| The hard part is judgment, classification, or when to decline | Workflow / cognition |
| The hard part is remembering schemas, domain notes, policies, or examples | Reference |
| The same deterministic code would be rewritten repeatedly | Script |
| The skill needs reusable templates, examples, starter projects, or media | Asset / template |
| The skill coordinates tools, services, retries, or side effects | Tool orchestrator |
| The skill repeatedly creates a document, deck, workbook, UI, or other artifact | Artifact builder |
| The skill establishes durable behavior constraints | Governance / rule |

### Phase 3: Resource Plan

Recommend the smallest useful resource set:

- `SKILL.md` only for concise workflow guidance.
- `references/` for detailed optional knowledge that should load lazily.
- `scripts/` for deterministic repeated operations.
- `assets/` for reusable source materials.
- Host-specific activation/install is not per-skill; it lives at the packaging layer (see
  `docs/host-packaging.md`).

Avoid adding scripts, assets, or orchestration until the intent has stable boundaries.

### Phase 4: Readiness Gate

Assess whether the idea is ready to implement.

| Dimension | Ready Signal | Concern Signal |
|---|---|---|
| Trigger clarity | Specific user requests are known | Could activate on broad brainstorming |
| Output clarity | Expected output shape is named | Output could be summary, plan, artifact, or action |
| Boundary clarity | Non-goals are explicit | Overlaps with existing skills |
| Resource clarity | Required resources are known | Resources are speculative |
| Portability | Core workflow is agent-neutral | Depends on one host's hidden conventions |
| Risk | Side effects and security concerns are constrained | Writes files, calls networks, or changes state without gates |

If the idea is not ready, produce an exploration result with open questions instead of an
implementation plan.

### Phase 5: Recommendation

Recommend one of:

- **Proceed**: The skill is ready to draft.
- **Prototype**: Create a narrow draft and expect iteration.
- **Defer**: More examples or boundaries are needed.
- **Do not create a skill**: The need is better handled by ordinary prompting, project docs, a
  one-off script, or an existing skill.

## Output Format

```markdown
# Skill Exploration

**Candidate name**: [lowercase-hyphen-name or "undecided"]
**Intent**: [one sentence]
**Recommendation**: [Proceed | Prototype | Defer | Do not create a skill]

| Dimension | Assessment |
|---|---|
| Dominant type | ... |
| Secondary types | ... |
| Trigger clarity | ... |
| Expected output | ... |
| Boundary / overlap | ... |
| Suggested resources | ... |
| Host packaging | ... |
| Portability concerns | ... |
| Security or side-effect concerns | ... |

## Proposed Skeleton

For **Proceed** or **Prototype**: a brief folder and workflow skeleton.
For **Defer** or **Do not create a skill**: omit the skeleton; give the blocking gap and what would
unblock it (Defer), or the better-fit alternative — ordinary prompting, project docs, a one-off
script, or an existing skill (Do not create a skill).

## Open Questions

[Only include questions that block safe implementation.]
```

## Rules

- Do not create or edit files unless the user explicitly asks to implement after exploration.
- Prefer the smallest skill shape that preserves the user's intent.
- Keep the dominant type singular even when secondary types exist.
- Treat host-specific paths, tools, and UI conventions as packaging concerns, not core workflow.
- Route mature conversation knowledge to a knowledge-output skill when appropriate:
  - Use `assess-knowledge` for assessing extractable conversation knowledge.
  - Use `write-learning-report` for personal internalization reports.
  - Use `save-knowledge` for durable project, agent, or team knowledge.
- Once a skill is drafted, harden its wording so it binds under use — point to `harden-skill`.
