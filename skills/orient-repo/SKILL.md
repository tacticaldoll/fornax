---
name: orient-repo
description: Use when an agent needs to orient itself in an unfamiliar repository before acting; discovers governance, conventions, enforcement, and non-goals into a compact working brief rather than editing files or relying on one host's auto-loaded context.
---

# Orient in a repo
Use this skill to **align with a project's conventions before acting** — so the first
change an agent makes already fits how the project wants work done. Read and internalize the
project's governance before reacting to it, rather than discovering the conventions by violating
them.

It is deliberately **agent-agnostic**: it does not assume the host auto-loaded any particular file,
and it hunts the surfaces a given host would otherwise miss (a Claude agent may see `CLAUDE.md` but
not `AGENTS.md`; a Cursor agent may see neither).

Governing intuition: **state what the project actually declares and enforces, and state what it does
not.** Do not invent a convention the repo never set; an unstated rule is a gap to report, not a
default to assume.

**Input**: the repository to orient in — by default the current working directory; if pointed at a subdirectory (e.g. a monorepo subpackage), sweep upward to the repository root as well, since host-neutral governance often lives above the target. Sweep the host-neutral governance surfaces regardless of what the host auto-loaded.

**Boundary**: reads and reports — produces a working brief, not code changes; does not edit, commit, or change state.

## Workflow

### Phase 0: Discover the governance and convention surface

Sweep the host-neutral locations — agent/assistant guides, project documentation, ownership and
process, any memory/notes directory, and the enforcement config — using
[references/discovery-surfaces.md](references/discovery-surfaces.md) for the concrete file checklist.

Read what is present. **Record what is absent** — a missing convention is a finding, not license to
assume one.

### Phase 1: Extract the operational contract

From what you read, extract how this project wants work done:

- **Commit** — message style/format, granularity, scope conventions, attribution policy.
- **Branch / integration** — branch model, whether the default branch is protected, PR/merge ritual
  (squash vs merge, subject rules).
- **Review** — required gates, who/what must approve, review-before-merge expectations.
- **Style / language** — formatter, lint rules, naming conventions, doc requirements, language policy.

### Phase 2: Map the enforcement surface

Separate what is **enforced** (a mechanism fails if you violate it) from what is **merely
documented** (a human must remember it). Identify the concrete checks: CI jobs, test suites,
linters, formatters, type checks, git hooks, a self-check/self-governance suite, schema validation.
Note the command(s) that run them when discoverable. This enforced-vs-documented split is the
highest-value part of the brief: it tells the agent what will *catch* a mistake versus what it must
self-police.

### Phase 3: Surface standing decisions and non-goals

Find the project's decision log, exclusions, and explicit "do not do X" statements (in `PROJECT.md`
decisions, a `BACKLOG`, ADRs, or governance prose). These prevent re-litigating settled calls and
violating deliberate non-goals — the mistakes that waste the most trust early.

### Phase 4: Produce the working brief

Emit a compact brief using the template in
[references/working-brief.md](references/working-brief.md), then stop — do not act on it beyond the
current task's needs. Flag every gap explicitly (`not found`), so the agent knows where it is
operating on assumption rather than declaration. Close the brief with the 2-4 **first-action
guardrails** — the few rules that most shape the very next change; this is the brief's payoff, not an
optional footer.

## Rules

- Read-only. Do not edit files, commit, or change state — produce the brief; the agent then works
  within it.
- Do not assume unstated conventions. State what the project declares, and mark what it does not
  (`not found`) rather than filling in a default.
- Be agent-agnostic. Do not rely on the host having auto-loaded any single file; sweep all the
  host-neutral surfaces and supplement whatever the host already injected.
- Separate enforced from documented. Name the concrete check that fails on violation, not just the
  rule a human must remember.
- Keep the brief compact and operational — the contract, the enforcement surface, the standing
  decisions/non-goals — not a summary of the whole repository.
- The brief is **transient** working context, not durable knowledge. Stay in lane; hand off at the
  boundary: to capture durable project/team knowledge, point to `save-knowledge`; to challenge whether
  governance prose should become enforcement, point to `audit-governance`; to understand how the code itself
  works, point to `map-codebase`; to plan a code decomposition, point to `plan-split`. Name the handoff
  rather than half-doing the other skill's job.
