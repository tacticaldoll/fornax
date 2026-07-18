# skill.yaml Schema

`skill.yaml` is the portable discovery manifest for each skill. Keep it vendor-neutral and easy for
different agents, registries, and installers to parse.

Host-specific discovery, activation, and install live at the packaging layer, not in top-level
`skill.yaml`. See [host-packaging.md](host-packaging.md) for how host-specifics are packaged.

## Location

Every production skill must include:

```text
skills/<skill-name>/skill.yaml
```

The manifest `name` must match `<skill-name>`.

## Required Fields

### `name`

Type: string

The canonical skill identifier. Use lowercase letters, digits, and hyphens only.

```yaml
name: summarize-meeting
```

### `version`

Type: string

The skill version in semantic version format.

```yaml
version: 0.1.0
```

Versioning rules:

- Patch: wording fixes, metadata corrections, and non-behavioral clarifications.
- Minor: new supported workflows, scripts, references, or assets.
- Major: trigger changes, removed behavior, renamed resources, or incompatible script interfaces.

### `family`

Type: string

The skill's domain, used for README grouping and for generating the skill maps. Exactly one of:

- `implementation` — codebase work: explore, orient, understand, design, plan, refactor, review.
- `knowledge` — capturing and shaping conversation knowledge.
- `decisions` — project-level judgment calls (dependencies, governance prose).
- `meta` — skills that operate on the skill toolkit itself.

```yaml
family: implementation
```

### `description`

Type: string

A concise description of what the skill does and when an agent should consider using it. This field
must be understandable without reading `SKILL.md`.

```yaml
description: Use when an agent needs to summarize meeting notes into decisions, action items, and risks.
```

### `triggers`

Type: list of strings

Concrete user request patterns or task contexts that should activate the skill.

```yaml
triggers:
  - user asks to summarize meeting notes
  - user asks to extract decisions and action items from a transcript
```

Prefer trigger descriptions that are specific enough to avoid activating unrelated skills.

### `entrypoint`

Type: string

Relative path to the primary instruction file.

```yaml
entrypoint: SKILL.md
```

The target file must exist.

## Recommended Fields

### `resources`

Type: mapping

Relative paths to bundled resources.

```yaml
resources:
  scripts: scripts/
  references: references/
  assets: assets/
```

Only include directories that exist or are expected to exist in the skill package.

### `compatibility`

Type: list of strings

Agent hosts, runtimes, or installer targets that the skill is intended to support.

```yaml
compatibility:
  - openai-codex
  - claude
  - cursor
  - generic-llm-agent
```

Use stable lowercase identifiers. Document host-specifics at the packaging layer (see `host-packaging.md`).

## Optional Fields

### `status`

Type: string

Lifecycle status.

Allowed values:

- `draft`
- `stable`
- `deprecated`

```yaml
status: stable
```

### `replaces`

Type: list of strings

Skill names this skill supersedes.

```yaml
replaces:
  - old-meeting-summary
```

### `replaced_by`

Type: string

Replacement skill for deprecated skills.

```yaml
replaced_by: summarize-meeting
```

### `maintainers`

Type: list of strings

People or team handles responsible for the skill.

```yaml
maintainers:
  - fornax-maintainers
```

## Full Example

```yaml
name: summarize-meeting
version: 0.1.0
status: stable
description: Use when an agent needs to summarize meeting notes into decisions, action items, and risks.
triggers:
  - user asks to summarize meeting notes
  - user asks to extract decisions and action items from a transcript
entrypoint: SKILL.md
resources:
  scripts: scripts/
  references: references/
  assets: assets/
compatibility:
  - openai-codex
  - claude
  - cursor
  - generic-llm-agent
maintainers:
  - fornax-maintainers
```

## Portability Rules

- Keep all paths relative to the skill folder.
- Keep core fields in English.
- Do not put vendor-specific metadata in top-level fields unless clearly namespaced and documented.
- Keep host-specific packaging at the packaging layer, not in `skill.yaml`.
- Keep trigger metadata stable and specific; changing triggers may require a major version bump.
