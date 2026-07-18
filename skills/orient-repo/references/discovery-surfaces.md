# Discovery Surfaces

The host-neutral checklist of where a project declares how it wants work done. Sweep these; the value
of an agent-agnostic warm-up is finding the surfaces a given host did not auto-load. Absence is a
finding — record `not found` rather than assuming a default.

## Agent / assistant guides (host-specific, but read them all)

| File | Typically read by |
|---|---|
| `AGENTS.md` | Codex and agent-generic tooling |
| `CLAUDE.md`, `.claude/` | Claude Code |
| `.cursorrules`, `.cursor/rules/` | Cursor |
| `GEMINI.md` | Gemini |
| `.github/copilot-instructions.md` | GitHub Copilot |
| `.windsurfrules`, other `*rules*` dotfiles | misc hosts |

A given host usually injects only its own file. Read every one present — they often diverge, and the
divergence itself is worth flagging.

## Project documentation

- `README` — orientation, build/run, high-level intent.
- `CONTRIBUTING(.md)` — contribution process, commit/PR expectations, style.
- `PROJECT.md`, `ARCHITECTURE.md`, `docs/` — design intent and decisions.
- ADRs (`doc/adr/`, `docs/decisions/`, `*.adr.md`) — recorded decisions with rationale.
- `BACKLOG`, `ROADMAP`, `TODO` — planned and explicitly-deferred work (non-goals live here too).

## Ownership and process

- `.github/CODEOWNERS` (or `docs/CODEOWNERS`) — who owns what; steward-gated paths.
- `.github/PULL_REQUEST_TEMPLATE*`, `ISSUE_TEMPLATE/` — required PR/issue shape.
- `CHANGELOG`, release notes, version files — release cadence and versioning scheme.
- `LICENSE`, `NOTICE` — licensing and attribution constraints.

## Memory / notes

- A memory or notes directory the host maintains (e.g. an assistant memory index, `.notes/`,
  `decisions/`). Prior working agreements and corrections often live here.

## Enforcement surface (what actually fails on violation)

Separates enforced rules from merely-documented ones.

- **CI**: `.github/workflows/`, `.gitlab-ci.yml`, `azure-pipelines.yml`, `Jenkinsfile`, CircleCI, etc.
- **Tests**: the test runner and how it is invoked (framework config, test dirs, a self-check suite).
- **Lint / format / type**: linter and formatter configs, type-checker config, and their commands.
- **Git hooks**: `.pre-commit-config.yaml`, `.husky/`, `.githooks/`, `core.hooksPath`.
- **Build / package**: the build manifest and scripts (what "green" means locally).

For each, capture the **command** when discoverable, so the brief names what will catch a mistake.

## Reading discipline

- Prefer the project's *own* governance over generic assumptions; when two sources conflict, note the
  conflict rather than silently picking one.
- Skim for the operational contract and enforcement surface first; do not attempt to summarize the
  entire repository.
- Time-box: read enough to fill the working brief, then stop.
