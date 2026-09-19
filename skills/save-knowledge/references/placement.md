# Placement Reference

Use this reference when deciding where durable knowledge should live.

## Placement Principles

- Put knowledge where future readers will naturally look before they need it.
- Prefer the narrowest scope that still reaches every future user.
- Update an existing source of truth instead of creating a new parallel document.
- Keep host-specific details in host packaging or host-specific docs.
- Keep portable skill behavior in `SKILL.md`; put long optional detail in `references/`.
- Keep personal learning artifacts out of durable project dependencies.

## Destination Guide

| Destination | Good For | Avoid When |
|---|---|---|
| `AGENTS.md` | Repository-wide agent governance and authoring rules | The rule applies only to one skill or host |
| Skill `SKILL.md` | Core reusable workflow instructions | The detail is long, optional, or host-specific |
| Skill `references/` | Detailed schemas, examples, style guides, placement rules | The content must always be loaded |
| Host packaging | Host activation, install notes, paths | The behavior is portable and belongs in core |
| Project context docs | Stable project background, architecture, constraints | The knowledge is personal reflection |
| Decision record | Decisions where alternatives and trade-offs matter | The decision is trivial or temporary |
| Runbook | Repeatable operational procedure | The process is one-off or not yet proven |
| Deployment/installer docs or deploy skill | Tool, deployment, or install mechanisms | The step is a one-off manual action |
| README | Human-facing overview or setup guidance | The detail is primarily for agents or internal workflow |

## Scope Test

Ask these questions before writing:

1. Who needs this knowledge later?
2. What task will fail or degrade if the knowledge is missing?
3. Is the proposed destination the first place that reader would check?
4. Is there already a maintained source that should be updated?
5. Does the content include unsupported conclusions or personal interpretation?

If the answer to question 2 is weak, do not persist yet.
