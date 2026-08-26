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
- Avoid hidden assumptions in core skill instructions — about the agent host, the programming
  language, the development workflow, or an externally installed tool (see the standing decisions in
  `PROJECT.md`).

## Skill Layout

Each production skill belongs under `skills/<skill-name>/`.

Recommended structure:

```text
skills/<skill-name>/
  skill.yaml
  SKILL.md
  skill-interface.yaml  # optional; only for a real record handoff
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

## Output Records

A skill whose type owes a defined output (`docs/skill-types.md`) states that output's shape in
`SKILL.md`. Rules about that shape, each earned where a record receives field-level audit:
`static-review` produces a Review Record and `triage-findings` audits it
(`docs/review-record-contract.md`). They are judgment, not structure: nothing validates them, and
they apply only where a record makes claims about itself.

A new skill needs no record contract of its own. When another skill reads its output, give both
skills matching optional `skill-interface.yaml` declarations and keep the human-readable record name
in their `**Input**:` and output prose. Use the standardized form
``a `<producer>` <Title Case Record Name>`` for that Input claim; validation checks it against both
sidecars. The sidecars make the seam discoverable without using prose as the inventory; a skill
whose output nobody reads is not missing a contract. See `docs/skill-interface.md` and the standing
decision in `PROJECT.md`.

- **Give a check three answers, not two.** "The input carries no such claim" is not "the claim does
  not hold". A two-valued cell forces a record predating a field, or one from another producer, into
  a false pass or a false contradiction. Name the third value, and say that a missing claim is not a
  passing one.
- **Keep facts about the input apart from facts about the record being written.** They read alike and
  answer to different owners: one is the input's fitness for the work, the other is your own. A
  self-check folded into an audit of the input hides which of the two failed.
- **Require an enumeration rather than inventing a value for what cannot be decided without one.** A
  record stating a scope without listing what it covered cannot support a decision about membership,
  and a state meaning "undecidable" spreads into every later round that reads it. Require the
  enumeration from producers in this repository; keep the undecidable state only as a concession to
  records this repository did not produce, and say in the skill which state is that concession — a
  reader cannot otherwise tell a compatibility path from a design choice.

## Authoring Workflow

When asked to create or update a skill:

1. Clarify the skill's concrete use cases only when the request is ambiguous.
2. Normalize the skill name to lowercase hyphen-case.
3. Create or update `skills/<skill-name>/skill.yaml`.
4. Create or update `skills/<skill-name>/SKILL.md`.
5. Add only the resource directories that are useful for the request.
6. Run repository validation before reporting completion.
7. Commit the change, then review and settle it as the Testing Strategy section requires — the
   review reads a range, so it cannot run before the commit exists.

Validation command:

```sh
.venv/bin/python scripts/check_workspace.py
```

The workspace command includes template validation. Its direct form remains available when debugging
template-only failures:

```sh
.venv/bin/python scripts/validate_skills.py --skills-path templates --allow-template-placeholders
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

- **Review what the tag will carry, not only the skills.** The Review stage above is scoped to a
  skill; the validation machinery, its test suite, and the generators go inside the release tag as
  well. A release has already shipped unreviewed script commits — the gate, Ruff, and CI were
  green, which is not the same as reviewed. The obligation is the one stated in Testing Strategy;
  what Release adds is the report line — state which commits in the release range received a review
  pass and which did not, so skipping one is a visible decision rather than an omission.
- If the change ships now, bump the collection version and the host manifests together (see
  Versioning).
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
- **Pin an external dependency by tag, and treat a released tag as immutable.** The engine is
  installed from `git+…@v<x.y.z>` in CI and in `tools/fornax-cli/pyproject.toml`, which is a mutable
  ref: moving that tag silently changes what every deployment installs. A commit SHA would remove
  that, and it is deliberately not used — a SHA makes an engine bump unreadable in a diff, and
  `PROJECT.md` already fixes Fornax's own release identity to a tag rather than a hash. The
  assumption that carries the risk is therefore stated rather than left implicit: a published tag is
  never moved or deleted, in this collection or in the engine. Re-pin to a SHA if a tag is ever
  observed to move.
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

### Versioning

The collection's release version lives in `distribution.json`; bump it on release and keep host
packaging manifest versions aligned. That alignment has teeth outside this repo: Claude Code gates
`plugin update` on the plugin manifest version, so shipping changed skills without a bump is a no-op
for installed users and the deployer must uninstall and reinstall to bust the version-pinned cache.

Skills do not carry a version of their own. Release versioning is the collection's, because a skill
has no distribution path of its own — hosts read `SKILL.md`, whose frontmatter has no version field,
and the `fornax` CLI pins one collection tag. Git carries per-skill change history. See
`PROJECT.md`.

Do not bump the version while developing or reviewing a feature or fix. First land and validate the
behavioral commits at the current version; after the release contents are confirmed, bump the
collection and every host projection together in a separate `build(deploy)` release commit.

Judge the increment by what changed for the people who install the collection:

- Patch for wording fixes, metadata corrections, and non-behavioral clarifications.
- Minor for new skills, new supported workflows, scripts, or references, for a change to a skill's
  required output shape inside an unchanged record identity, and for a field added to the shipped
  manifest schema.
- Major for removed or renamed skills, trigger changes, removed behavior, incompatible script
  interfaces, and for a field removed or renamed in the shipped manifest schema.

`skill.yaml`, the `SKILL.md` frontmatter, and the optional `skill-interface.yaml` travel to every
installed host, and `docs/skill-yaml-schema.md` calls the manifest something registries and
installers parse — so their schema is a published interface. `distribution.json` is one as well: it
carries the collection's identity and the version every host manifest projects. A field added,
removed, or renamed in any of them counts even when nothing in this repository reads it.

While the collection is pre-1.0, a major-class change takes the minor position instead; `1.0.0` is a
maturity decision, not an increment this rule can reach.

Contributor-facing changes — validation rules, generators, CI, the script test suite — do not drive
the increment on their own; they ride along with whatever release carries them.

### Final Report Notes

This repository commits directly to `main` and runs no pull-request workflow (`PROJECT.md`), so
these notes belong in the final report; a PR or MR, where one exists, carries the same content:

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
- `skill.yaml` has `name`, `family`, `description`, `triggers`, and `entrypoint`.
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
- A record that audits its own input follows the Output Records rules, and says which of its states
  is a concession to records this repository did not produce.
- Version changes match the scope of the behavior change.

## Testing Strategy

Prefer lightweight tests that match the risk of the change.

- Run repository validation for every change.
- Review every change with `static-review` before reporting completion — any change, not only a
  skill — after committing it, so the review reads a range rather than a working tree. Fresh
  context, and the full Against-Contract track. The gate is not that and neither is rereading the
  diff: a range that had been through three adversarial passes and a green gate returned eighteen
  findings on its first real review, one of them a regression whose own commit message called it a
  strengthening. This is the one step here no gate can enforce, because it needs a model rather
  than a fast deterministic check, so it is stated here and pointed at from the Authoring Workflow
  and from Release rather than restated in either.
- Settle what a review found with `triage-findings`, and keep the Disposition Record it produces
  under `docs/dispositions/<range>.md` so the next round can be handed the prior one. Requiring the
  review without requiring the disposition is how a cause returns: round after round repaired findings
  at their locations, and each round's repairs produced the next round's defects. One commit per
  cause, not one per round.
- Use `.venv/bin/python scripts/check_workspace.py` as the public local entry point; CI runs the
  same script in its pinned Python 3.10 environment, and the style and hook-syntax gates run inside
  it so a green local run and a green CI run mean the same thing. What stays CI-only does so because
  they need what the maintenance environment does not declare: the JavaScript plugin needs `node`,
  and the deployment CLI tests need the engine installed. That is the whole of the difference —
  state it here when it moves, because a local gate that quietly checks less is how a rejected push
  gets its first surprise. Keep component checks independently runnable for focused diagnostics.
- Run `.venv/bin/python scripts/development_knowns.py --check` through the workspace gate. Record only
  non-obvious current conditions that affect development judgment; external review language is
  evidence, not the project statement, and a treatment never authorizes work without an explicit
  `work` state. After review, triage, spike, test, or experiment verifies such a condition, suggest a
  project-centered registry update automatically, but do not write it or execute its repair without
  explicit user authorization. See `docs/development-knowns.md`.
- **Read a dated evidence log by its headings, never by grep alone.** An evidence file records what
  was true at a revision, so a count, a verdict, or a standing claim is quotable only together with
  the dated section it sits under. The last section in such a file is the oldest kept, not the
  current one. A sentence written in the present tense inside a superseded section is still
  superseded — the section heading governs, not the grammar. This is what "evidence, not the project
  statement" means in practice: a superseded blocker was quoted from
  `scripts/tests/scenarios/triage-findings/README.md` as live, and reached a review verdict, a
  triage cause, and a registry entry before anyone checked which heading it lived under. When you
  supersede a claim, mark it where it is written, not only in the heading above it.
- Regenerate the README skill maps with `.venv/bin/python scripts/skill_graph.py --write` after changing a
  skill's `family` or its handoff targets; `--check` fails when the committed block is stale.
- Regenerate the record inventory with `.venv/bin/python scripts/seam_contract.py --write` after changing the
  marked output template of a skill another skill reads, or either skill's interface sidecar; `--check`
  fails when `docs/review-record-contract.md` is stale. The seam list is derived, so a new one needs
  no edit to be counted and no seams at all is a clean answer.
- Cover a new or changed validation rule in `scripts/tests/`, run with
  `PYTHONPATH=scripts .venv/bin/python -m unittest discover -s scripts/tests`. Check the fixture actually
  fails when the rule is removed; a suite that passes either way proves nothing. Revert the unit
  the claim names, not something it calls: moving a heading grammar out of `seam_contract` into the
  shared parser was verified by breaking the shared parser, which of course went red, while putting
  the private regex back into `seam_contract` — the entire change — left the suite green, because
  the test called the parser directly and never ran the consumer whose ownership had moved. The
  `tools/fornax-cli` suite is among the CI-only steps named above.
- When a check is a hand-written matcher claiming an invariant over a grammar — a version, a
  dependency spec, a heading — cover it with two negative controls, not one: a **near-miss sharing
  the accepted prefix**, and a **valid alternate spelling of the same meaning**. Instance tests stay
  necessary; these are what make the claim about the grammar rather than about the examples. Both
  halves have failed here in one day: a tag boundary written as an excluded-character list let
  `+build.5` through, and a pin matcher rewritten to ignore the command prefix began reporting
  `# example: tool==1.0` as an install. Each was one control short, and the missing control was a
  different one each time.
- A matcher that reads a token must name the grammar's owner, and use it. CommonMark is owned by
  `markdown-it-py` and the shell by `shlex`, both installed and both used. Where the owner is not
  installed — PEP 440 by `packaging`, GitHub Actions YAML by `PyYAML`, a pyproject string by
  `tomllib`, which needs Python 3.11 — the matcher may be hand-written, but the grammar and its
  absent owner go in `development-knowns.yaml` with the reason. Stopping at the enclosing
  construct's own closing delimiter needs neither: `[^"]+` inside quotes, `[^*]+` inside `**`,
  `[^\n]+` on a line are reading to a delimiter the construct defines, not guessing where a token
  gives out. Inventing a terminator list is the thing that needs an owner or an entry — five
  rounds of this were each a repair freely inventing one, and it was the freedom rather than any
  particular list that kept reopening the hole.
- Read a token whole through `read_whole.whole`, never a prefix of it. Both ways of deciding where
  a token ends are guesses — listing what may follow it, or listing what it may contain — and the
  second fails worse, because ending too early yields a well-formed value that passes its next
  comparison while ending too late yields a malformed one that fails loudly. `ruff==0.16.1|x` read
  as `0.16.1|x` was caught by the comparison; rewritten to the version's own alphabet it read as
  `0.16.1`, matched the installed release and answered clean. `whole()` only calls `fullmatch` and
  is the only way to a `Whole`, so a grammar stated wrongly now yields an `Unread` the caller has
  to report. The guess stays a guess; what it can no longer do is pass.
- After repairing a defect, sweep the repository for the same class before calling it fixed. Not by
  rereading the change — by enumerating the mechanism: every `re.compile`, every hand-written
  grammar, every place the same question is answered, then checking each against the property the
  repair established. Reviews report what they were pointed at. The install-ref boundary was
  rewritten form after form, and when the class was finally swept, more matchers of the same shape
  were sitting in files no round had opened: a hand-written heading grammar in `seam_contract`, and
  a terminator list for a declared version in `runtime_contract`. Both were found by asking "what
  else is like this", which no review had been asked. Sweeping is not the end of it either — one of
  those repairs replaced a terminator list with an alphabet, which is the same mistake in the other
  direction, and the sweep that found the site did not stop the repair from being wrong. What ends
  a round is the reading being total, not the examples being covered: once a wrong guess yields an
  `Unread` the caller reports, a further input the matcher misreads is a known to register, not a
  repair to make. Round after round ran past that point, each closing one more example of a hole
  the type now closes.
- The OpenCode plugin is syntax-checked in CI with
  `node --input-type=module --check < .opencode/plugins/fornax.js`, install-free on the runner; the
  hook is parsed by `scripts/check_sources.py` inside the workspace gate. Feed the plugin through
  stdin as a module — plain `node --check` on a `.js` file parses it as CommonJS and silently passes
  anything containing `import`, so the check would do nothing. The plugin is the one that fails
  silently in use: nothing else reads it, so a syntax error would only surface for an OpenCode user.
- Python style is checked by `ruff check .` against `ruff.toml` — width 100, rules `E`/`F`/`W`
  with `preview` on, pinned to one ruff version so a release cannot fail an unrelated push. It is
  run by the workspace gate, so the pre-commit hook and CI reach the same answer. Never auto-apply
  a fix as part of another change, and treat a ruff version bump as its own commit — preview rules move
  between releases.
- `.python-version` is the single source for the minimum maintenance runtime. CI consumes it
  directly, and `scripts/runtime_contract.py` keeps Ruff's syntax target aligned. The pre-commit
  hook uses the same pinned environment from `.venv`; it never installs or upgrades dependencies
  during a commit. The independently packaged Fornax CLI keeps its declared Python 3.10 minimum.
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
- Use the Python standard library by default. A maintenance dependency is allowed only when it
  materially reduces complexity; pin it and every transitive dependency in
  `requirements-maintenance.txt`, and keep CI and the local hook on that same environment.
- **When a module takes ownership of a behaviour, enumerate every existing implementation of it.**
  Extracting a shared owner is only half the change; the other half is finding the copies it now
  answers for and either routing them through it or recording why one stays outside. `skill_model.py`
  does this for `NAME_PATTERN` — it names the spellings the repository uses and says that
  unifying them changes what validates, so the divergence is a decision rather than a cleanup. Every
  participant left outside a new owner without that record has been a defect: a private manifest
  reader in `skill_graph.py`, an unguarded directory listing in `validate_skills.py`, and two return
  polarities under one `validate_` prefix.
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
- **Do not write a count of what the repository contains.** Not how many skills, families, seams,
  consumers, generated blocks, gate steps, registry entries, modules or tests there are, and not
  how many commits or forms a past repair took. A number beside such a noun is a claim about the
  tree that nothing reads, and every one of these nouns has carried a stale one: README named fewer
  gate steps than the gate ran, `generated_block` named fewer consumers than dispatched blocks,
  `PROJECT.md` kept seam counts by hand, and had already had some removed for this very reason.
  Derive the number into a generated block, or say the thing without it — "form after form", "more
  than one check", "the consumers of one record identity".

  **The rule is a judgment; the check is not the rule.** `scripts/check_text.py` reports a cardinal
  number standing immediately before a noun from a closed list — the nouns that have gone stale.
  That is one syntax a count can take, and counts take others: an adjective between the number and
  the noun slips past it, and so does any noun not on the list. Both were verified, and a count
  phrased that way sat in `development-knowns.yaml` while the commit that added the check claimed
  counts had stopped. Widening the syntax was measured and abandoned: allowing modifiers before
  the noun and any plural after the number matched mostly prose — "one is", "72 characters", "PEP
  508 is" — so it caught nothing new and would have buried what it did catch. Extending the noun
  list narrows the gap; nothing closes it, because deciding whether a number counts the tree needs
  the sentence's meaning. `development-knowns.yaml` records that.

  The classification below is what decides whether a number is a count at all, and it is for the
  author to apply — the check only catches the plainest form. Each row names where the suite shows
  the check agreeing with it, because a category stated here that the check does not implement is
  the same defect this rule is about.

  | A number that... | Is it a count? |
  |---|---|
  | says how much of something the tree holds | **yes — remove it** |
  | a rule prescribes, or states as a threshold | no |
  | records the conditions a measured result was taken under | no, and rewording it falsifies it |
  | configures a tool, or names a version | no |
  | a check computes while it runs | no, it cannot go stale |

  In `scripts/tests/test_check_text.py`, in that order:
  `..._a_count_of_what_the_repository_contains_is_reported`,
  `..._a_skill_states_thresholds_and_a_scenario_states_its_parameters` for the next two,
  `..._a_configured_value_is_not_a_count`, and
  `..._a_derived_number_in_output_is_not_written_down`.

  Skills and scenario records sit outside the check because their numbers are the prescribed and
  almost everywhere. That exemption is by directory, which is coarse; a count of tree state inside
  one would pass. Nothing better is available without reading intent, and this file is where that
  limit is recorded rather than left to be rediscovered.

  This check's own rule text and fixtures have to contain the pattern. They compose their numbers
  from parts instead of earning an exemption: a check its own suite is exempt from is a check
  nothing holds to its own rule.
