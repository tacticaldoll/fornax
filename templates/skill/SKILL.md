---
name: replace-me
description: Use when an agent needs to perform a specific workflow. Replace this with clear trigger contexts and the capability this skill provides.
---

# Replace Me

Follow this skill when the user asks for the workflow described in the frontmatter or `skill.yaml`.

**Input**: <what this skill consumes> — <how to resolve when ambiguous, or "ask the user">.

**Boundary**: <what this skill does NOT do — e.g. plans and reports but does not edit, run, or execute> — hand off at the edge.

## Workflow

1. Inspect the task context and relevant files.
2. Load only the bundled resources needed for the request.
3. Execute the workflow using the host agent's available tools and the repo's existing patterns.
4. Validate the result before reporting completion.

## Bundled Resources

- Read files in `references/` only when their topic is directly relevant.
- Run scripts in `scripts/` when deterministic behavior is preferred.
- Use files in `assets/` as templates or source materials for outputs.

## Portability

- Use relative paths from this skill folder.
- Treat host-specific tools as optional; describe a fallback when the workflow depends on them.
- Keep platform-specific activation, install, or UI metadata at the packaging layer (root plugin
  manifests), not in the core workflow.

## Stance-type variant

If this is a **stance / thinking-partner** skill (see `docs/skill-types.md`), delete `## Workflow`
and its phases: a stance skill states its posture, its boundaries, and its exit / hand-off — not
steps — and imposes no fixed output artifact. It also needs no separate `## Rules` — the stance
bullets are the discipline and the hand-off lives in the exit. Keep the `**Input**:` and
`**Boundary**:` lines, then delete this note.
