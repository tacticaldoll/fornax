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

**Input**: the conversation content to internalize — a named topic, provided notes or transcript, a prior report to revise, or a prior `assess-knowledge` Knowledge Assessment Record; if none is given, pick the most substantial internalization-ready topic. Resolution detail in Phase 1.

**Boundary**: produces a self-contained learning report for personal understanding — does not externalize durable knowledge (use `save-knowledge`), depend on or point to sibling reports, or write a file unless the user gives a destination.

## Workflow

### Phase 1: Input Resolution

Resolve the report source:

| Source | Resolution |
|---|---|
| User names a topic | Use that conversation topic |
| User provides notes, transcript, or existing report text | Use the provided material as source |
| User provides existing report path or asks to update a prior report | Treat as a report revision; apply the gate in [references/edge-cases.md](references/edge-cases.md) |
| A prior Knowledge Assessment Record exists | Use its nature, maturity, attribution, and volume as guidance |
| No topic is specified | Identify the most substantial internalization-ready topic |

When a prior Knowledge Assessment Record exists:

| Attribution | Action |
|---|---|
| Internalize | Proceed if the topic passes the quality gate |
| Externalize | Tell the user the topic is better suited to durable knowledge externalization |
| Both | Proceed on the conceptual insight; note that project-specific aspects may need externalization |
| Neither | The assessment found the topic has conversation value but no clear artifact value. Decline rather than writing a report the source cannot support |

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

#### What the source already holds

The table above judges what may be *claimed*. Before drafting, list separately what the source
already *contains*, because that is what the report owes and what a clean draft quietly drops:

- **Genesis** — how the problem actually arose: the triggering incident, the symptom, the wrong turn
  taken and reversed. This is not why a conclusion holds; that is the argument's own job, and it is
  the half that survives abstraction on its own.
- **Concrete cases** — the specific events, failures, numbers, and details the claims grew out of.
- **Undeveloped depth** — what the source opened and left in a sentence: a sub-problem raised and
  dropped, a premise used as given, a topic carrying more than one core question.

The list stays in working context. It is not a section, is not written to a file, and does not reach
the reader. The conversation remains readable throughout, so the list is not there to preserve
access — it is a commitment made before the drafting that would otherwise drop these without anyone
noticing.

### Phase 3: Structure Selection

Choose exactly one dominant structure using the first matching test:

| # | Test | Structure |
|---|---|---|
| 1 | Documents a multi-phase process with decisions made along the way | Experience Report |
| 2 | Develops an argument from observation through analysis to principle | Analytical Essay |
| 3 | Captures a specific technical finding with investigation process | Technical Note |
| - | None match, or content is too thin | Decline |

If the Knowledge Assessment Record carries a nature classification, use this mapping as a hint:

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

#### Claim-to-form selection

Before drafting, extend the Phase 2 working list with each core claim, its source support or
explicitly hypothetical premises, and the question a reader needs to check. Evaluate each form
in Phase 4 against that question:

| Decision | Evidence to record | Action |
|---|---|---|
| Applicable | the relationship, case, deciding rule, or boundary the form makes inspectable | Draft the form from those premises |
| Not applicable | why the form does not address a question this claim raises | Continue the substantive report without that form |
| Insufficient support | the missing premise, definition, or deciding rule needed for a relevant form | Narrow or qualify the claim, keep the gap open, or decline when it is central |

Missing support is not evidence of non-applicability. Evaluate applicability again after narrowing
a claim. Neither a qualitative subject nor an absence of numbers rules out a logical statement or
a model of explicitly specified rules. A form is selected for the work it does, not its appearance.
Keep this selection in working context; hand unresolved support gaps to the user beside the report.

### Phase 4: Structure Application

Read [references/readability.md](references/readability.md) before drafting; it governs how every
structured element below is introduced, paced, and interpreted.

#### Structured expression

Use Phase 3's claim-to-form selection to decide which forms the report carries. An applicable
form is required; its presence does not discharge its purpose. A report with no applicable forms
can still carry a substantive argument. Do not introduce a mechanism solely to obtain a form.

| Form | Applicable when | What it must carry | Degenerate when |
|---|---|---|---|
| Diagram | a claim turns on connected causal steps, state movement, or responsibility boundaries | those relationships | it redraws section headings or leaves the relationships unexplained |
| Table | a claim requires tracing a case through a deciding condition or comparing handling of the same case | the input, condition, and outcome, or the competing readings and their consequences | it only lists terms |
| Executable model | explicitly specified rules admit concrete inputs, expected outcomes, and a violating case | a runnable, dependency-free model whose assertions reject that case | it checks unrelated rules invented to fill the form, asserts nothing, or claims to verify an unspecified judgment |
| Formal statement | a claim rests on a defined invariant, type relation, set boundary, or quantitative relationship | the relation and the premises from which it follows | undefined symbols dress a sentence or operations have no defined meaning |

For each formal statement, introduce the claim in ordinary language, define its symbols and
relations, identify its source support or explicitly hypothetical premises, then show a case that
satisfies it and a case that would violate it. Cases can be hypothetical and must be labeled as
such; a violating case illustrates what the statement excludes, not an observed refutation.

For arithmetic, define each quantity's domain, unit or scale, and what each operation means.
For logical or structural statements, define predicates, membership rules, or permitted transitions.
An abstract noun assigned a symbol is not thereby a quantity. A qualitative argument can use a
logical boundary without inventing numerical magnitudes.
Follow [references/readability.md](references/readability.md) for presentation and a worked example.

Distinguish a model's stipulated assumptions from source facts. Say which rule the model can check
and which real-world judgment it cannot establish. An assertion over a hypothetical model does not
validate the assumptions or establish a measured effect.

This skill runs nothing. An executable model is written so that the *reader* can run it and so its
assertions fail loudly when the claim is wrong; that property belongs to the code, not to anyone
having executed it. So the report must not say a model was run, present output as observed, or quote
a number only an execution could produce. Hand what went unverified to the user instead.

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
| A genesis step or concrete case from Phase 2 is absent, or survives only as "for various reasons" | Restore it in specific form, or report which was dropped and why when handing the report over |
| Nothing on the Phase 2 undeveloped-depth list was developed; the report stops where the source stopped | Develop what this report's subject can carry, or report which was left and why |
| An added argument traces back to neither the report's subject nor a premise it must restate to stay self-contained | Cut it; an expansion floor is not licence to widen the subject |
| An applicable structured form is missing or degenerate by its Phase 4 test | Restore it from the supported claim; when support is insufficient, narrow or qualify the claim and re-evaluate applicability |
| A form was marked not applicable because a needed premise or deciding rule is absent | Reclassify as insufficient support and handle the gap through Phase 3 |
| A formal statement has undefined symbols or operations, or a hypothetical model is presented as source fact | Define the relation and premises, qualify the claim, or remove the unsupported expression |
| The report states that a model was run, or quotes output as observed | Remove the claim; this skill executes nothing |
| Tables, lists, or callouts outnumber prose lines | Add the missing narrative context; reassess a form that carries no claim |
| Report depends on or points to another report (self-containment rule) | Re-explain needed concepts inline and close this report's own causal chain |

For Experience Reports, re-read Background after drafting Discovery:

| Check | Fail Action |
|---|---|
| Background mentions history Discovery never uses | Remove it |
| Discovery assumes context Background did not establish | Add the missing starting condition |
| Background recaps process instead of starting state | Rewrite it as scene-setting |

This quality gate is a terminal pass — do not open an unbounded revision loop.

### Phase 6: Attack the report

Attack the draft before handing it over. Use separate passes or reviewers only when the host offers
them; otherwise reason through each lens directly. The lenses are this skill's own claims about its
output, which is where it is least able to notice it is wrong:

- **Swallowed genesis** — take the Phase 2 list and locate each entry in the draft. An entry you can
  only find "in spirit" is not there.
- **Filled, not earned** — trace each included form to its Phase 3 claim and apply its Phase 4
  degeneracy test. Try to break the relation with the stated violating case; check that symbols and
  operations have definitions. For each omitted form, distinguish non-applicability from missing
  support. A model checking its own stipulated rules cannot prove those rules describe the world.
- **Unrun claims** — find every sentence that would be true only if something had been executed,
  measured, or looked up. This skill did none of those.
- **Depth ceiling** — set the draft against what the source already said. A draft that only
  reorganizes it has not been written yet.

Run the attack once. Repair what can be repaired; what cannot is reported rather than hidden.
Neither this phase nor Phase 5 opens a revision loop — the user is the last judge, and an unrepaired
weakness reaches them faster as a sentence than as another pass.

#### What to hand over

The attack's findings stay out of the report. A learning report is a self-contained artifact about
its subject, and a section recounting how it was made is the generation trace the self-containment
rule exists to keep out. Give them to the user beside the report instead:

- which lenses were attacked, and what survived;
- what was dropped from the Phase 2 list, and why;
- which structured forms went unverified, and what the user would have to run to verify them;
- which relevant forms lacked support, and which premise or deciding rule remains missing.

State these plainly. Do not soften them into a summary of what the report does well.

### Phase 7: Generalization

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

The report is produced in the conversation. Write it to a file only when the user asks for a file
**and names where it goes** — never derive a destination from host conventions, a scratch directory,
or the report's own title. A request to save it without a path is a request for the path, not
permission to choose one.

## Rules

- Structure follows content; select structured forms through Phase 3's claim-to-form selection.
- Do not pad. Merge thin sections or decline; a substantive report does not need an inapplicable form.
- Keep each report self-contained: it must not depend on or point to sibling reports, and other
  project rules, context, docs, or skills must not depend on it. If its insight must be referenced
  elsewhere, route that to an externalization workflow such as `save-knowledge`.
- Do not externalize durable knowledge while writing the report; route that work to a separate
  externalization skill.
- Preserve project-specific detail by default; generalize only when asked.
- Use one dominant report structure per report.
- Produce the report in the conversation; write a file only on a request that names the destination.
