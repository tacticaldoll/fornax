# Skill Types

Use this taxonomy to choose the right shape for a skill before adding scripts, references,
assets, or host packaging. A skill may combine types, but one type should be dominant.

Use `skills/scope-new-skill/` when the intent is still ambiguous and needs a structured exploration pass
before implementation.

## Type Taxonomy

| Type | Primary Value | Typical Resources | Use When |
|---|---|---|---|
| Workflow / cognition | Guides agent reasoning, judgment, and output shape | `SKILL.md`, optional `references/` | The fragile part is deciding what to do, how to classify context, or when to decline |
| Reference | Provides domain knowledge loaded on demand | `references/` | The agent needs schemas, policies, domain notes, examples, or detailed background |
| Script | Performs deterministic or repeated operations | `scripts/` | The same code would otherwise be rewritten often, or exact behavior matters |
| Asset / template | Supplies reusable source material for outputs | `assets/` | The skill needs templates, boilerplate, images, fonts, examples, or starter projects |
| Tool orchestrator | Coordinates multiple tools, services, or external systems | `SKILL.md`, `scripts/`, `references/` | The task requires sequenced tool calls, API data collection, retries, or side-effect control |
| Artifact builder | Produces a structured user artifact such as a document, deck, workbook, or UI | `assets/`, `scripts/`, optional `references/` | The skill repeatedly creates a concrete artifact format with quality checks |
| Governance / rule | Establishes durable behavior constraints for agents or projects | `SKILL.md`, project docs | The output should influence future behavior, not just complete one task |
| Stance / thinking-partner | Holds a reasoning posture instead of executing fixed steps | `SKILL.md` only | The value is *how* the agent thinks (curious, unhurried, visual, non-committal), not a sequence of phases or a required output |

## Selection Heuristics

- Start with a workflow / cognition skill when the main risk is judgment, boundary-setting, or
  output structure.
- Add references only when detail should be loaded lazily instead of living in `SKILL.md`.
- Add scripts only when deterministic execution is materially better than natural-language
  instructions.
- Add assets only when the skill needs reusable source material.
- Add orchestration only after the workflow has stable tool boundaries and failure modes.
- Keep governance content separate from ordinary task skills unless the user explicitly wants an
  always-on behavior constraint.
- Choose a stance / thinking-partner skill only when a fixed workflow would *harm* the task — when the
  fragile part is sustaining an open-ended posture (exploration, ideation, requirement discovery)
  rather than reaching a defined output. Such a skill states its stance and boundaries, not phases,
  and should still declare what it will not do (e.g. never implement).

## Output Contract by Type

The dominant type determines what a skill must produce:

- **Workflow / cognition, artifact builder, tool orchestrator** — must produce a defined output (a
  plan, report, table, or artifact) in a stated shape.
- **Reference** — provides knowledge on demand; no standalone artifact.
- **Governance / rule** — produces durable constraints or dispositions, not a one-off artifact.
- **Stance / thinking-partner** — **imposes no fixed artifact.** Its value is the reasoning posture;
  it may end with an optional light summary (e.g. the clarified intent) but must not force one.

A stance skill producing "no artifact" is therefore not an exception to Fornax's read / plan / report
identity — it is the declared output contract of its type.

## Knowledge Output Skills

The `assess-knowledge`, `write-learning-report`, and `save-knowledge` skills are workflow / cognition skills.
Their purpose is to transform conversation context into the right knowledge output:

| Skill | Direction | Output Role |
|---|---|---|
| `assess-knowledge` | Assess | Identify extractable conversation knowledge and its maturity |
| `write-learning-report` | Internalize | Turn mature conversation content into self-contained reports for personal understanding |
| `save-knowledge` | Externalize | Turn mature conversation content into durable project, agent, or team knowledge |

These skills should prefer concise `SKILL.md` workflows with lazily loaded references. They should
not start as script or orchestrator skills, because their main value is classification, placement,
and quality gating.
