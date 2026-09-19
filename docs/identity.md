# Fornax — Identity

**Name**: Fornax — the brand name for the collection and the namespace its skills install under
(`/fornax:<skill>`).

**Tagline**: Skills that plan before they touch your code.
_(Portable, single-purpose skills for coding agents.)_

## Thesis

Fornax refines the **context an agent holds** — a codebase, a conversation, a set of governance
claims, or the toolkit itself — into context worth acting on, without touching the world. A skill
separates, characterizes, and reorganizes what is already there; it does not act on the code or ship
anything.

This is why the honesty discipline is a **law**, not an add-on: a skill works only with what the
context actually contains, and never fabricates what it does not. Fornax skills read, plan, and
report rather than edit — with no manufactured findings, no inflated confidence, no padding, and no
fabricated agreement. They mark inference apart from fact and name what they did not check.

## What it is

Fornax is a portable, multi-agent **skills registry**. Each skill is a small, single-purpose
operation an agent applies to a codebase or a conversation to produce **one well-defined result** — a
plan, a map, a review, a decision — or, for a stance skill, to hold a reasoning posture. Skills
**read, plan, report, or reason**; they hand off execution rather than editing behind the user's
back. What each type must (or must not) produce is its declared output contract — see
`skill-types.md`.

## Who it's for

Coding agents — Claude Code, Codex, Cursor, Antigravity, and generic LLM agents — and the people who
run them, who want disciplined, portable, reusable reasoning steps instead of ad-hoc prompts.

## Naming rules (for new skills)

- **Slug: lowercase-hyphen, task-descriptive** (verb-object) — it says what the skill does, because
  the slug is the name a human types at `/fornax:<slug>`. Keep it legible, not clever
  (`plan-implementation`, `map-codebase`, …).
- Triggering rides the `description`; the `/fornax:` prefix namespaces the slug — so descriptive
  slugs stay legible and never collide with built-ins.
- Full authoring, versioning, and review rules live in `../AGENTS.md`.

> **Why the slug is descriptive**: auto-triggering by `description` proved
> unreliable in practice, so manual `/fornax:<slug>` invocation is the load-bearing path — where an
> obscure slug is a real cost and a legible task name is not. Native per-skill aliases are unsupported
> across hosts, so the slug itself had to carry the task name.

## Voice

Precise, unhurried, honest about limits. Every skill states what it does **not** do; reports mark
inference apart from fact and name what was not checked. Fornax refines — it does not overclaim.
