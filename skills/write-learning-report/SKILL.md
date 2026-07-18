---
name: write-learning-report
description: Use when an agent needs to turn mature conversation content into a self-contained learning report; selects a fitting report structure and preserves source fidelity for personal understanding rather than durable project knowledge.
---

# Write a learning report
Use this skill to transform mature conversation content into a structured report for personal
internalization. Learning reports are self-contained artifacts; knowledge that needs to
become durable project or team context belongs in an externalization workflow such as `save-knowledge`.

Governing intuition: **structure follows content** — the material's natural shape determines the
report's form rather than being forced into a fixed template.

**Input**: the conversation content to internalize — a named topic, provided notes or transcript, a prior report to revise, or a prior assess-knowledge result; if none is given, pick the most substantial internalization-ready topic. Resolution detail in Phase 1.

**Boundary**: produces a self-contained learning report for personal understanding — does not externalize durable knowledge (use `save-knowledge`), depend on or point to sibling reports, or write a file unless the user gives a destination.

## Workflow

### Phase 1: Input Resolution

Resolve the report source:

| Source | Resolution |
|---|---|
| User names a topic | Use that conversation topic |
| User provides notes, transcript, or existing report text | Use the provided material as source |
| User provides existing report path or asks to update a prior report | Treat as a report revision; apply the gate in [references/edge-cases.md](references/edge-cases.md) |
| Prior assess-knowledge result exists | Use its nature, maturity, attribution, and volume as guidance |
| No topic is specified | Identify the most substantial internalization-ready topic |

When prior assess-knowledge guidance exists:

| Attribution | Action |
|---|---|
| Internalize | Proceed if the topic passes the quality gate |
| Externalize | Tell the user the topic is better suited to durable knowledge externalization |
| Both | Proceed on the conceptual insight; note that project-specific aspects may need externalization |

Decline when the source is too thin or when the user's intent is only a plain summary.

### Phase 2: Source Fidelity Scan

Before choosing a structure, separate what the source supports from what the agent may infer.

| Claim Type | Treatment |
|---|---|
| Explicitly stated | May be written as source fact |
| Strongly implied | May be written as synthesis; do not present as direct source fact |
| Agent interpretation | Use only when it helps the user's understanding; mark as interpretation |
| Unsupported | Omit or frame as an open question |

Do not turn a plausible inference into a settled conclusion. If a key claim is unsupported, either
weaken the claim, keep it as an open question, or decline the report when the unsupported claim is
central.

### Phase 3: Structure Selection

Choose exactly one dominant structure using the first matching test:

| # | Test | Structure |
|---|---|---|
| 1 | Documents a multi-phase process with decisions made along the way | Experience Report |
| 2 | Develops an argument from observation through analysis to principle | Analytical Essay |
| 3 | Captures a specific technical finding with investigation process | Technical Note |
| - | None match, or content is too thin | Decline |

If assess-knowledge produced a nature classification, use this mapping as a hint:

| Nature | Likely Structure |
|---|---|
| Decision Record | Experience Report |
| Universal Principle | Analytical Essay |
| Problem Diagnosis | Technical Note |
| Operational Knowledge | Technical Note |
| Factual Record | Technical Note |

Do not mix structures in one report. If the content clearly contains multiple independent report
shapes, ask the user to choose the dominant angle or propose separate reports.

Before drafting, verify internally why the selected structure fits better than the other available
structures. Use that fit check to shape the report, but do not include the fit check in the final
report unless the user asks for process notes.

When one session yields two or more reports, coordinate them (scope, reading order, no overlap) per
[references/edge-cases.md](references/edge-cases.md).

### Phase 4: Structure Application

Read [references/readability.md](references/readability.md) before drafting when the report is long,
technical, multilingual, or likely to contain tables, diagrams, or decision callouts.

#### Experience Report

Use for content that documents what was done and why.

| Section | Role |
|---|---|
| Background | What existed before; what triggered the work |
| Discovery | Chronological phases, including trials, revisions, and turning points |
| Decisions | Summary table of major decisions, when there are at least 3 |
| Supplementary Knowledge | Optional related concepts that inform the decisions |
| Key Lessons | Transferable insights derived from the experience |

When the conversation contains alternatives, explicit trade-offs, failed attempts, or user
redirects, embed decision points in the Discovery section at the moment they occurred.

Use this callout format sparingly:

```markdown
> **Decision Point**: [one-line decision]
> Alternatives: [what else was considered and why it was rejected]
> Outcome: [consequence, success, failure, or follow-up]
```

#### Analytical Essay

Use for content that argues what should be true and why.

| Section | Role |
|---|---|
| Introduction | Concrete trigger and problem statement |
| Analysis | Framework or reasoning applied to the problem |
| Reflection | Broader implications, tensions, edge cases |
| Conclusion | Transferable principles |

#### Technical Note

Use for content that explains how something works or how a problem was solved.

| Section | Role |
|---|---|
| Problem | What was encountered |
| Investigation | What was tried and what was found |
| Finding | The core technical insight |
| Application | Optional guidance for applying the finding |

### Phase 5: Quality Gate

Before finalizing, check the draft:

| Check | Fail Action |
|---|---|
| Required section has no content | Re-evaluate structure selection |
| Section has fewer than 2 substantive points | Merge with an adjacent section |
| Section repeats another section | Deduplicate; keep content where it fits best |
| Overall report has fewer than 3 substantive sections | Decline instead of padding |
| Major conclusion exceeds source support | Weaken, qualify, or remove the claim |
| Tables, lists, or callouts outnumber prose lines | Add real narrative context or simplify structure |
| Report depends on or points to another report (self-containment rule) | Re-explain needed concepts inline and close this report's own causal chain |

For Experience Reports, re-read Background after drafting Discovery:

| Check | Fail Action |
|---|---|
| Background mentions history Discovery never uses | Remove it |
| Discovery assumes context Background did not establish | Add the missing starting condition |
| Background recaps process instead of starting state | Rewrite it as scene-setting |

This quality gate is a terminal pass — do not open an unbounded revision loop.

### Phase 6: Generalization

Generalization is opt-in. Activate it only when the user asks for a portable or shareable version.

When generalizing:

1. Replace project-specific names, paths, team names, and internal jargon with generic descriptions.
2. Preserve the reasoning, structure, and reusable principles.
3. Verify that no project-specific reference leaks through.

## Report Format

This section is the single source of truth for the learning report format. Hosts may choose
where the report is written, but they must not change the report schema unless the user explicitly
requests a different format.

Default to the user's conversation language unless the user asks otherwise. Use English for portable
generalized versions when requested.

Every report must use this header:

```markdown
# [Report Title]

**Structure**: [Experience Report | Analytical Essay | Technical Note]
**Date**: [YYYY-MM-DDTHH:MM]
**Source**: [conversation | notes | reconstruction]
**Model**: [model name, when available]
**Agent**: [agent surface and version, when available]

## [Section 1]
...
```

Include `Model` and `Agent` only when the host exposes them accurately. If the host does not expose
exact values, omit those lines rather than guessing.

Use `Source: conversation` when the report is grounded in accessible conversation context. Use
`Source: notes` when the user provides standalone notes or files. Use `Source: reconstruction` when
the agent must reconstruct from partial context; in that case, qualify claims more carefully.

Use the timestamp when the report is produced, to minute precision. If source coverage is partial,
the user requested a rough version, or the report has unresolved open questions, say so in the
introduction instead of adding a `Status` header.

If the host can create files and the user asks for a file artifact, choose a clear destination based
on host conventions or user-provided paths. Otherwise, produce the report in chat.

## Rules

- Structure follows content; never force thin content into a report.
- Do not pad. Merge thin sections or decline.
- Keep each report self-contained: it must not depend on or point to sibling reports, and other
  project rules, context, docs, or skills must not depend on it. If its insight must be referenced
  elsewhere, route that to an externalization workflow such as `save-knowledge`.
- Do not externalize durable knowledge while writing the report; route that work to a separate
  externalization skill.
- Preserve project-specific detail by default; generalize only when asked.
- Use one dominant report structure per report.
- Ask before writing a report to a file unless the user already provided a destination.
