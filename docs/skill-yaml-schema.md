# skill.yaml Schema

The pinned `agent-skill-builder` is the standard baseline for skill packages. This document keeps
only the Fornax-specific profile decisions; the profile is selected by `agent-skill-builder.yaml`
and is the executable source for the baseline check.

## Fornax profile

`profiles/fornax.yaml` requires:

- a `skill.yaml` in every skill directory;
- a `**Input**:` line in every `SKILL.md`;
- descriptions beginning with `Use when an agent needs to `.

The workspace gate runs the builder through `scripts/check_agent_skills.py`, then runs the
collection checks in `scripts/validate_skills.py`. Do not duplicate builder rules in a collection
script or in this reference.

## Collection fields

`scripts/skill_model.py` owns the values that Fornax-specific checks consume:

| Field | Fornax rule |
| --- | --- |
| `name` | Lowercase letters, digits, and hyphens; it matches the skill directory. |
| `family` | One of `implementation`, `knowledge`, `decisions`, or `meta`. |
| `description` | One sentence beginning `Use when an agent needs to …`; the boundary is negative. |
| `triggers` | A list of concrete user requests or contexts. |
| `entrypoint` | A relative path to the skill's primary instruction file, normally `SKILL.md`. |
| `status` | Optional; `draft`, `stable`, or `deprecated`. |
| `resources` | Optional; only `scripts`, `references`, and `assets` are collection resource keys. |
| `version` | Forbidden; collection releases are declared by `distribution.json`. |

The collection validator also checks local Markdown links, handoff targets, and record-interface
claims. Those are Fornax checks, not part of the portable baseline.

Portable optional metadata such as `compatibility`, `replaces`, `replaced_by`, and `maintainers`
remains builder-owned; use the pinned builder schema rather than copying its field definitions here.

## Portability

Keep paths relative to the skill directory and keep core fields vendor-neutral. Host-specific
discovery, activation, and installation belong in the packaging layer; see
[`host-packaging.md`](host-packaging.md). Add a `skill-interface.yaml` only when another skill
consumes the output, and keep its identity aligned with the matching producer.

Create or update manifests from [`templates/skill`](../templates/skill), then run:

```sh
.venv/bin/python scripts/check_workspace.py
```
