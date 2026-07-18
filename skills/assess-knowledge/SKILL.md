---
name: assess-knowledge
description: Use when an agent needs to assess a conversation for knowledge worth extracting; identifies topics, maturity, and internalize/externalize tendency without creating artifacts or recommending next steps.
---

# Assess conversation knowledge
Use this skill to scan conversation content and identify topics with extractable knowledge value — a
structured assessment for the user's decision-making.

Governing intuition: **name what is worth extracting; do not prescribe what to do with it.** Include
even thin topics — omission is itself a prescription — and never inflate maturity or volume to
justify extraction.

**Input**: the conversation to assess — by default the current one; if the user names a span or topic, scope to that.

**Boundary**: assesses and reports only — does not create artifacts, modify files, invoke other skills, or recommend next steps.

## Workflow

### Phase 1: Thread Identification

Scan the conversation chronologically. Identify distinct discussion topics by semantic shift: a new
subject, question, problem, or decision path starts a new thread.

Use this granularity rule:

- Split compound topics only when they reach independent conclusions.
- Keep topics merged when they share one conclusion chain.
- Include low-value or thin topics; omission is a form of prescription.

### Phase 2: Per-Topic Assessment

Assess each topic independently across nature, maturity, attribution, volume, and expansion
cues.

#### Nature

Classify with the first matching test:

| # | Test | Nature |
|---|---|---|
| 1 | Records a decision process with alternatives evaluated | Decision Record |
| 2 | Derives principles applicable beyond the current project | Universal Principle |
| 3 | Solves a specific problem with root cause analysis | Problem Diagnosis |
| 4 | Documents a procedure or how-to | Operational Knowledge |
| 5 | Describes what exists or what was observed | Factual Record |

#### Maturity

| Rating | Criteria |
|---|---|
| Nascent | Initial observation; no iteration or conclusion |
| Developing | Has structure, some iteration, or partial conclusion |
| Mature | Multiple iterations, refined conclusion, and clear formulation |

Raise maturity when the conversation includes trial-and-error cycles, challenge-and-revision
exchanges, explicit trade-off comparison, or convergence on a principle.

#### Attribution

| Tendency | Signal |
|---|---|
| Internalize | Universal principle, methodology, or thinking pattern; value is in understanding |
| Externalize | Project-specific decision, configuration, architecture constraint, or durable rule; value is in persistence |
| Both | Core insight should be understood personally, while the specific application should be documented |
| Neither | Topic has conversation value but no clear artifact value |

#### Volume

| Estimate | Criteria |
|---|---|
| Sufficient | At least 3 refined points, clear structure, and enough depth for a standalone artifact |
| Marginal | Has substance but fits better as a section within a larger artifact |
| Insufficient | Brief mention, no depth, or not worth extracting |

#### Expansion Cues

Expansion cues describe latent structure and evidence gaps for later use. They are not next steps.

Include short cues such as:

- Narrative arc: how the topic developed over time.
- Decision tension: alternatives, trade-offs, or redirects.
- Evidence gap: what is missing or unsupported.
- Conceptual insight: the transferable understanding embedded in the topic.
- Durable claim: the specific decision, rule, or constraint the topic asserts.
- Boundary warning: what should not be generalized.

## Output Format

```markdown
# Conversation Knowledge Assessment

**Date**: [YYYY-MM-DD]
**Topics identified**: [N]

| # | Topic | Nature | Maturity | Attribution | Volume | Expansion Cues | Notes |
|---|---|---|---|---|---|---|---|
| 1 | ... | Decision Record | Mature | Externalize | Sufficient | Decision tension: ... | ... |
| 2 | ... | Universal Principle | Developing | Internalize | Marginal | Conceptual insight: ... | ... |
```

The table is the complete output. Do not add a recommendations section, action list, or next-step
suggestions.

## Rules

- Keep zero project coupling: do not reference a project's directory structure, governance
  framework, skill inventory, or toolchain unless it is the topic being assessed.
- Treat expansion cues as diagnostic metadata, not recommendations.
- Assess honestly: do not inflate maturity or volume to justify extraction.
- Preserve completeness: every identified topic must appear in the table.
- Distinguish value assessment from content recall. A request to "summarize our discussion" is
  content recall; a request for "what is worth extracting" is value assessment.
