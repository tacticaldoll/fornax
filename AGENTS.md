# Fornax — Repository Guide

This repository is **Fornax**, the portable source of truth for reusable agent skills. Manage it as
a multi-agent skills registry, not as a Codex-only collection. See `docs/identity.md` for the brand
and naming rationale, and `PROJECT.md` for standing decisions and non-goals.

## Core Principles

- Keep every skill portable across mainstream agents unless a user explicitly asks for a
  single-agent skill.
- Treat `SKILL.md` as the primary workflow instruction file.
- Treat `skill.yaml` as the portable discovery and compatibility manifest.
- Keep skills host-neutral; host-specific packaging lives at the packaging layer, not per skill (see `docs/host-packaging.md`).
- Keep scripts, references, and assets relative to the skill folder.
- Avoid platform-specific hidden assumptions in core skill instructions.

## Skill Layout

Each production skill belongs under `skills/<skill-name>/`.

Recommended structure:

```text
skills/<skill-name>/
  skill.yaml
  SKILL.md
  scripts/
  references/
  assets/
```

Skill folder names must use lowercase letters, digits, and hyphens only.

## Authoring Rules

- Start from `templates/skill` when creating a new skill.
- Follow `docs/skill-yaml-schema.md` when creating or updating `skill.yaml`.
- Use `docs/skill-types.md` to identify the skill's dominant type before choosing resources,
  scripts, assets, or orchestration.
- Keep `SKILL.md` concise and procedural. Put detailed schemas, long examples, or large
  domain notes in `references/`.
- Put deterministic or frequently repeated operations in `scripts/`.
- Put reusable source materials in `assets/`.
- Make `skill.yaml` vendor-neutral. Do not put Codex-only, Claude-only, or Cursor-only fields
  there unless they are namespaced clearly.
- Keep host-specific discovery, activation, and install at the packaging layer (root plugin
  manifests), not per skill — see `docs/host-packaging.md`.

## Language Policy

Use English as the default language for repository governance and skill authoring.

Write these files in English:

- `skill.yaml`
- `SKILL.md`
- scripts, validation messages, commit messages, PR summaries, and release notes

Chinese is allowed when it is task data, source material, domain reference content, localized
examples, or required by a specific NLP workflow. Keep executable instructions and trigger metadata
in English whenever possible.

## Naming Convention

Beyond lowercase hyphen-case: name a skill with a **task-descriptive, verb-object slug that says what
it does** (e.g. `assess-knowledge`, `save-knowledge`, `map-codebase`, `harden-skill`,
`handle-feedback`). The slug is the name a human types at `/fornax:<slug>`, so legibility wins over
cleverness. Rationale: manual invocation is the load-bearing path (auto-triggering by `description`
is unreliable, and per-skill aliases are unsupported across hosts), so the slug must carry the task
name; the `/fornax:` prefix namespaces it against built-ins like `review` / `verify` (see
`PROJECT.md`).

- If the SKILL.md body frames the work with a **mental model**, that framing must be
  **load-bearing** — developed into the actual mental model the workflow reasons with — not a
  decorative label; a bolded verb that is never developed adds jargon without coherence.
- Keep slugs **legible and honest**: no internal-mechanism words (e.g. `progressive`), no relative
  qualifiers that have no sibling variant (e.g. a bare `local`). Mechanism/scope words the user would
  actually say are fine (see Description Shape).
- Record a rename in the new skill's `replaces` field.

## Description Shape

The `description` carries triggering, so keep all skills to one shape: a **single
sentence** opening `Use when an agent needs to …`, then a semicolon and a
comma-separated list of what the skill does, closing with a boundary clause that
states what it does *not* do (e.g. `… without modifying code`, `… rather than
planning the implementation`). The closing clause must be a **negative boundary** —
what the skill does not do — never a temporal caveat (`before creating files`) or a
failure-mode aside (`while avoiding pollution`); those do not fence the skill from its
siblings. Use plain, user-legible action verbs: the description text is the match
surface. Keep the same `description` text in `skill.yaml` and
in the `SKILL.md` front matter. Mechanism or scope words the user would actually say
(`gate-based`, `local`) belong here, and may also appear in the slug when they aid legibility
(e.g. `static-review`).

## Input Contract

Every `SKILL.md` states, up front, what the skill consumes and how it resolves ambiguity. Place a
single bold `**Input**:` line after the intent paragraph and before the first workflow heading:

```markdown
**Input**: <what the skill consumes> — <how to resolve when ambiguous, or "ask the user">.
```

- Keep it to one line; it is a contract, not a workflow step. When the skill already has an
  input-resolution phase, the line summarizes it and the phase carries the detail.
- Name the accepted input forms (a path, a diff, a conversation topic, a dependency name, a repo)
  and the fallback when none is given — never assume and proceed silently.
- Stance / thinking-partner skills may state the entry points they handle instead of a single input.

`scripts/validate_skills.py` enforces that this line is present; it does not check the line's content.

## Authoring Workflow

When asked to create or update a skill:

1. Clarify the skill's concrete use cases only when the request is ambiguous.
2. Normalize the skill name to lowercase hyphen-case.
3. Create or update `skills/<skill-name>/skill.yaml`.
4. Create or update `skills/<skill-name>/SKILL.md`.
5. Add only the resource directories that are useful for the request.
6. Run repository validation before reporting completion.

Validation command:

```sh
python scripts/validate_skills.py
```

Also validate the template after changing `templates/skill`:

```sh
python scripts/validate_skills.py --skills-path templates --allow-template-placeholders
```

## Skill Lifecycle

Move skills through clear lifecycle stages.

### Propose

Before creating a non-trivial skill, identify:

- The concrete user requests that should trigger it.
- The expected outputs or actions.
- The target agent hosts.
- Whether it needs scripts, references, or assets.
- Any security-sensitive operations.

### Draft

Create the initial files from `templates/skill`.

- Write `skill.yaml` first so discovery metadata is explicit.
- Write `SKILL.md` as the portable workflow.
- Keep references and scripts minimal until the skill needs them.
- Declare supported hosts in `compatibility`; host packaging is added at the packaging layer.

### Review

Review the skill as executable agent guidance.

- Check whether triggers are specific enough.
- Check whether instructions are portable across supported agents.
- Check whether scripts and assets are necessary.
- Check whether the skill can be understood without hidden context.

### Validate

Run repository validation and any script-specific checks. If scripts are added or changed, run at
least one representative command or document why it could not be run.

### Release

Before release:

- Update `skill.yaml` `version` according to the versioning rules.
- Use the required commit style and scope.
- Include validation commands in the PR or final report.
- Mention compatibility or migration notes when behavior changes.

### Deprecate

Deprecate instead of silently deleting when installed users may depend on a skill.

- Mark the skill as deprecated in `skill.yaml` if the manifest supports that field.
- Add replacement guidance in `SKILL.md`.
- Keep compatibility aliases or migration notes when practical.
- Remove only after the user explicitly approves or after a documented migration window.

## Deployment Tooling

Prefer compatibility with existing open tooling before creating custom installers.

Useful tools and intended roles:

- `agent-skills-distribution-template`: The neutral empty distribution contract and starting point
  for a new domain-specific skills repository; do not copy Fornax identity or governance into it.
- `agent-skill-deployer`: The independently versioned multi-host inventory and deployment engine;
  the in-tree `fornax` command must remain a thin workspace-versioned policy adapter fixed to the
  matching canonical release tag, with no local source or config interface.
- `gh skill`: GitHub-first install, update, preview, and publish flow for Agent Skills.
- `npx skills`: Cross-agent skill installer for local paths, GitHub, GitLab, and git URLs.
- Codex `$skill-installer`: Codex-specific install flow from catalogs or GitHub skill paths.
- `shskills`: Lightweight Git-based installer for Claude, Codex, Antigravity, OpenCode, or custom
  targets.
- MCP: Runtime tool/service exposure layer. Use MCP for skill registry search/read APIs or
  executable tools, not as the primary folder-format replacement.
- Antigravity Native: Copy or symlink the skill folder directly to `~/.gemini/config/skills/` (global) or `.agents/skills/` (workspace).

When adding custom deployment scripts, keep them thin:

- Validate first.
- Support dry-run when possible.
- Support project and user scopes.
- Avoid destructive cleanup unless explicitly requested.
- Preserve provenance such as source repo, ref, and installed path when practical.
- Assign exactly one authoritative Fornax deployment channel per host and scope. A fallback channel
  must be explicit, not installed alongside the default.
- Inventory all discovery surfaces before mutation. Never remove a skill solely because its name
  starts with `fornax-`; require Fornax provenance or explicit legacy adoption.

## Maintenance Guidelines

### Commit Style

Use Conventional Commits with a concise, imperative subject:

```text
<type>(<scope>): <subject>
```

Examples:

```text
feat(skill/summarize-meeting): add initial portable skill
fix(skill/entity-linking): clarify trigger description
docs(repo): document deployment tools
chore(template): update placeholder metadata
test(validate): cover missing skill manifest
```

Allowed types:

- `feat`: Add a new skill, script, or user-visible capability.
- `fix`: Correct broken behavior, invalid metadata, unsafe instructions, or compatibility issues.
- `docs`: Update repository guidance, skill instructions, references, or examples.
- `test`: Add or update validation, fixtures, or compatibility checks.
- `chore`: Maintain templates, formatting, metadata, or repository housekeeping.
- `refactor`: Restructure existing skill content without changing intended behavior.
- `build`: Change packaging, installer, CI, release, or dependency setup.
- `revert`: Revert a previous commit.

Preferred scopes:

- `skill/<skill-name>` for one skill.
- `skills` for changes spanning multiple skills.
- `template` for `templates/skill`.
- `validate` for validation scripts and checks.
- `deploy` for installer, publishing, or registry tooling.
- `repo` for top-level maintenance files.
- `docs` for broad documentation-only updates.

Keep subjects under 72 characters when practical. Do not end the subject with a period.

Use the commit body when the reason matters more than the file diff:

- Explain compatibility tradeoffs.
- Mention agent-specific behavior.
- Note migration steps for installed skills.
- Link issues or external specs when relevant.

### Commit Granularity

Prefer small, reviewable commits with one reason to exist.

Good commit boundaries:

- One new skill and its required manifest, core instructions, scripts, references, and assets.
- One behavioral update to one existing skill.
- One repository-wide policy or guideline update.
- One validation rule and its fixtures or examples.
- One deployment or installer capability.
- One mechanical formatting or metadata cleanup.

Split commits when a change contains multiple independent reasons:

- Separate skill content changes from validation script changes.
- Separate template changes from production skill changes.
- Separate deployment tooling from documentation updates unless the docs explain that exact tool
  change.
- Separate unrelated skills, even when the edits are similar.
- Separate mechanical rewrites from semantic changes.

Keep changes together when splitting would make the history misleading:

- Update `skill.yaml` and `SKILL.md` together when they describe the same skill behavior.
- Include script updates with the skill change that requires them.
- Include reference updates with the instruction change that depends on them.
- Include validation tests or fixtures with the new validation rule.

Avoid commits that only say "update files", "misc changes", or "fix stuff". If the scope cannot be
named clearly, split the change further.

### Commit Classification

Choose the commit type by the user-visible intent, not by the file extension.

- Use `feat` when adding a new skill, new workflow, new installer behavior, or a new reusable script
  capability.
- Use `fix` when correcting wrong triggers, invalid manifests, broken scripts, unsafe guidance, or
  compatibility regressions.
- Use `docs` when changing explanatory text without changing expected skill behavior.
- Use `test` when adding validation coverage, fixtures, smoke prompts, or compatibility checks.
- Use `chore` for repository housekeeping, metadata cleanup, placeholder maintenance, or
  non-behavioral template upkeep.
- Use `refactor` when reorganizing skill content without changing triggers, outputs, or supported
  workflows.
- Use `build` for packaging, installer, dependency, CI, release, or registry configuration.

When multiple types seem possible, prefer this order:

```text
fix > feat > build > test > refactor > docs > chore
```

Examples:

- Editing `SKILL.md` to correct a harmful instruction is `fix`, not `docs`.
- Adding a new script used by an existing skill is `feat`, unless it only fixes broken behavior.
- Updating `README.md` for a new installer in the same change is part of `build(deploy)`.
- Rewording a trigger so the skill activates in new situations is `feat` or `fix`, not `docs`.
- Moving long examples from `SKILL.md` to `references/` without behavior change is `refactor`.

### Change Grouping

- Keep unrelated skills in separate commits.
- Keep mechanical template or validation updates separate from skill content changes when possible.
- Update `skill.yaml` and `SKILL.md` in the same commit when they describe the same behavioral change.
- Include validation changes with the rule they enforce.

### Versioning

The collection's release version lives in `distribution.json`; bump it on release and keep host
packaging manifest versions aligned. Each `skill.yaml` `version` is the skill's own release version
— do **not** bump it on every edit. While
skills are `status: draft` (pre-1.0), leave them at `0.1.0` and let git carry the change history.

Bump a skill's `version` only for a release-level change to that skill:

- Patch for wording fixes, metadata corrections, and non-behavioral clarifications.
- Minor for new supported workflows, scripts, or references.
- Major for trigger changes, removed behavior, renamed resources, or incompatible script interfaces.

### Pull Request Notes

When preparing a PR summary, include:

- What changed.
- Which skills or tooling are affected.
- Compatibility impact across Codex, Claude, Cursor, Antigravity, and generic agents.
- Validation commands run.
- Any security-sensitive scripts, external calls, or environment variables.

Do not include AI signatures, AI-generated-by notices, or AI co-author trailers in commit
messages, PR, or MR descriptions.

## Compatibility Checks

Before considering a skill ready:

- `SKILL.md` has `name` and `description` frontmatter.
- `skill.yaml` has `name`, `version`, `description`, `triggers`, and `entrypoint`.
- Trigger descriptions are understandable without reading the body.
- Core instructions do not require a single agent vendor.
- Any host-specific requirement is documented at the packaging layer (`docs/host-packaging.md`).
- Scripts can run from relative paths or explain their expected working directory.
- References are discoverable from `SKILL.md` or `skill.yaml`.

## Review Checklist

Use this checklist for new skills and meaningful updates:

- The folder name, `skill.yaml` `name`, and `SKILL.md` frontmatter name match.
- `skill.yaml` includes clear `description`, `triggers`, `entrypoint`, and relative resource paths.
- `SKILL.md` describes what to do, when to load resources, and how to validate results.
- Host packaging carries host-specifics only, never a second copy of the core workflow.
- Instructions are written in English unless an exception from the language policy applies.
- Security-sensitive behavior is explicit and constrained.
- Scripts have clear inputs, outputs, dependencies, and expected working directory.
- The skill has at least one realistic prompt or scenario that can be used for smoke testing.
- Version changes match the scope of the behavior change.

## Testing Strategy

Prefer lightweight tests that match the risk of the change.

- Run repository validation for every change.
- Enforcement: CI (`.github/workflows/validate.yml`) runs the validator on every push; enable the
  local pre-commit hook once per clone with `git config core.hooksPath .githooks`.
- Validate `templates/skill` after template changes.
- For a new skill, test with at least one realistic user prompt and inspect whether the skill's
  instructions are sufficient.
- For trigger or metadata changes, test at least one positive prompt and one nearby non-trigger
  prompt when practical.
- For scripts, run representative commands and verify output, exit code, and file effects.
- For packaging changes, smoke-check that a skill still resolves and activates under the target host.
- For deployment tooling, prefer dry-run checks before install, update, publish, or cleanup.

Document any skipped test and the reason in the final report or PR notes.

## Script And Dependency Policy

Keep scripts deterministic, portable, and easy to audit.

- Use Python 3 for repository maintenance scripts and skill scripts by default.
- Use only the Python standard library unless dependencies materially reduce complexity.
- Use another scripting language only when the host toolchain requires it or the user explicitly
  asks for it.
- Document script dependencies near the script or in the skill's `SKILL.md`.
- Do not download dependencies, call external services, or modify user files unless the skill
  explicitly requires it.
- Support dry-run for scripts that install, publish, delete, move, or overwrite files.
- Keep secrets out of scripts, examples, fixtures, and command output.
- Use relative paths from the skill folder or document the expected working directory.
- Avoid global machine changes unless the user explicitly approves them.

## Security

- Inspect third-party skills before vendoring or installing them.
- Treat skill instructions as executable influence over an agent.
- Avoid embedding secrets, tokens, internal credentials, or private endpoints.
- Document required environment variables without including values.
- Be cautious with scripts that modify files, call networks, or run shell commands.

## Repository Hygiene

- Keep README user-facing and concise.
- Keep this file as the operating guide for agents working in this repository.
- Do not add generated caches, local installs, or copied third-party skills unless the user asks
  to vendor them.
- Run `git status --short` before final reporting so the user sees the actual change surface.
