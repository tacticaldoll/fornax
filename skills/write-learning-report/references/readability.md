# Readability Reference

Use these guidelines when drafting learning reports, especially for long, technical,
multilingual, or highly structured reports.

## Terminology

- Introduce domain terms on first use with a short gloss or example.
- Limit each paragraph to at most two new domain terms.
- When several terms are needed, add a bridging sentence that uses already-established vocabulary
  before introducing the next term.
- In multilingual reports, introduce the local-language term and the English anchor together when
  the English term is useful for later search or technical grounding.

Example:

```markdown
The report treats durable project knowledge as a single source of truth: one maintained location
that later agents and maintainers can rely on instead of reconstructing the decision from chat.
```

## Sentence Complexity

- Avoid sentences that contain three or more independent concepts.
- Split nested parentheticals into separate sentences.
- Use short transition sentences when moving from observation to analysis or from analysis to
  principle.

## Narrative Continuity

- Open each major section with a sentence that connects it to the prior section's outcome.
- Use Background for starting conditions, not a compressed history of everything that happened.
- Keep Discovery chronological unless an analytical grouping is clearer and does not hide causality.
- Close the report's own causal chain; keep the report self-contained (see the self-containment rule
  in SKILL.md).

## Structural Elements

- Introduce every table, list, callout, or diagram with prose that explains why it matters.
- Follow every diagram with prose that interprets the key insight.
- Avoid consecutive decision callouts without an intervening narrative paragraph.
- If a report has many decisions, reserve full callouts for pivotal decisions and weave minor
  decisions into prose.

### Decision Density

Use decision callouts only when they improve comprehension. Preserve narrative flow over rigid
structure.

| Decision Points | Strategy |
|---|---|
| 2-4 | Use full callouts for each major decision |
| 5-7 | Use full callouts only for pivotal decisions; weave minor decisions into prose |
| 8 or more | Use narrative-first prose; reserve full callouts for the 2-3 most consequential decisions |

Never place more than two full decision callouts in sequence without at least one narrative
paragraph between them.

Use narrative-woven decisions when density is high:

```markdown
The team chose to keep the report as an internalization artifact rather than a project dependency.
The alternative was to place the conclusion into durable project context immediately, but that would
have turned a personal learning artifact into a source of future operational behavior before the
boundary was clear.
```

## Diagrams

Prefer Mermaid diagrams when the report explains:

- relationships among three or more entities,
- branching flows,
- decision trees,
- lifecycle movement from one state to another.

Use diagrams to show structure. Use surrounding prose to explain causation, trade-offs, and meaning.
