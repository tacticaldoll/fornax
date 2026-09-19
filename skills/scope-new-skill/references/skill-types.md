# Skill Type Reference

Use this reference to classify the dominant type of a proposed skill. A skill may combine types,
but one type should lead the implementation.

The signals for *which* type an intent matches live in SKILL.md Phase 2; this
reference maps each type to its primary value and the resources it typically implies.

## Types

| Type | Primary Value | Typical Resources |
|---|---|---|
| Workflow / cognition | Guides agent reasoning, judgment, and output shape | `SKILL.md`, optional `references/` |
| Reference | Provides domain knowledge loaded on demand | `references/` |
| Script | Performs deterministic or repeated operations | `scripts/` |
| Asset / template | Supplies reusable source material for outputs | `assets/` |
| Tool orchestrator | Coordinates multiple tools, services, or external systems | `SKILL.md`, `scripts/`, `references/` |
| Artifact builder | Produces a structured user artifact such as a document, deck, workbook, or UI | `assets/`, `scripts/`, optional `references/` |
| Governance / rule | Establishes durable behavior constraints for agents or projects | `SKILL.md`, project docs |
