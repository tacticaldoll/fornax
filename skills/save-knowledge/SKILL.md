---
name: save-knowledge
description: Use when an agent needs to persist mature conversation knowledge into durable project, agent, or team sources; chooses the narrowest destination and drafts the edit for downstream execution rather than internalizing it for personal understanding.
---

# Save durable knowledge
Use this skill to convert mature conversation knowledge into durable knowledge that future agents,
maintainers, or team members can rely on. If the user wants a learning report for internalization,
route to `write-learning-report`; if the content is not mature enough to persist, decline or ask for more
source context.

Governing intuition: **placement discipline** — put the smallest accurate knowledge unit in the
narrowest durable home. Persist durable knowledge into a stable home only once it is genuinely
settled (mature and supported). This is why later phases say "do not persist" knowledge that has not
settled.

**Input**: the mature conversation knowledge to persist — a named insight, a prior assess-knowledge result, or a target path to validate; if the source is unclear, ask for the excerpt or intended future use. Resolution detail in Phase 1.

**Boundary**: plans placement and drafts the edit for downstream execution when the user asks to externalize into a durable source; does not edit files or run validation itself, and does not handle personal reflection — route those to `write-learning-report`.

## Workflow

### Phase 1: Input Resolution

Resolve the knowledge source:

| Source | Resolution |
|---|---|
| User names a conversation insight | Extract the specific claim, decision, rule, or workflow |
| Prior assess-knowledge result exists | Use its nature, maturity, attribution, and volume as guidance |
| User provides a target path | Validate that the target is the correct durable home |
| User asks where knowledge should live | Run placement selection before proposing any change |
| Source is unclear | Ask for the conversation excerpt or intended future use |

When prior assess-knowledge guidance exists:

| Attribution | Action |
|---|---|
| Externalize | Proceed if maturity and placement gates pass |
| Both | Split conceptual insight from project-specific durable knowledge |
| Internalize | Tell the user this is better suited for a learning report — route to `write-learning-report` — unless they identify a durable use |

### Phase 2: Knowledge Claim Extraction

State the candidate knowledge as one or more precise claims. For each claim, identify:

- What future reader or agent needs to know.
- Why the knowledge must persist beyond the conversation.
- What source evidence supports it.
- What should not be generalized from it.

Read [references/durability.md](references/durability.md) to judge whether each claim is durable
enough to persist. Do not persist vibes, tentative preferences, or personal reflections as project
knowledge.

### Phase 3: Placement Selection

Choose the narrowest durable home. Read [references/placement.md](references/placement.md) for the
destination guide, its avoid-when conditions, and the scope test.

If two destinations seem plausible, choose the one with the fewest future readers who still need
the knowledge. If the content is personal understanding only, do not persist it; route to
`write-learning-report`.

Phase 3 fixes *where* — the destination surface and its scope. The *form* the knowledge takes is
chosen next in Phase 4; where the destination guide and Phase 4 name the same shape (decision record,
runbook, README), Phase 4's table is the authority on that form.

### Phase 4: Artifact Type Selection

Given the destination fixed in Phase 3, choose the form the knowledge takes:

| Artifact | Use When |
|---|---|
| Rule | Future agents must always follow a constraint |
| Context note | Future tasks need stable background |
| Skill update | The knowledge changes how a reusable skill should behave |
| Reference update | The knowledge is detailed, optional, or loaded lazily |
| Decision record | The alternatives and reasoning matter later |
| Runbook | The user or agent will repeat operational steps |
| README/doc update | Human maintainers need discoverable project guidance |

Keep the artifact minimal. Preserve reasoning only when future users need it to apply the knowledge
correctly.

### Phase 5: Governance Gate

Run this gate before proposing a write to broad or mandatory destinations such as `AGENTS.md`,
always-on rules, policy docs, repository-wide conventions, or host-specific rule systems.

| Check | Pass Condition | Fail Action |
|---|---|---|
| Authority | The user explicitly asked to create or update durable governance | Ask before policy-level writing |
| Scope | The rule applies to every future reader governed by the destination | Move to a narrower destination |
| Obligation | The wording states required behavior only when compliance is genuinely mandatory | Reword as guidance, context, or rationale |
| Maintenance | The destination has a clear owner or update path | Prefer a less authoritative artifact |
| Reversibility | Future maintainers can identify when the rule should change or be removed | Add conditions or avoid governance placement |

Governance writing is the strongest form of persistence. Prefer context, references, or skill-local
instructions when the knowledge does not need always-on force.

### Phase 6: Pollution Gate

Before drafting the edit, run these checks in addition to the Governance Gate above:

| Check | Fail Action |
|---|---|
| Knowledge is not mature or supported | Decline or ask for more source context |
| Content is personal reflection | Route to `write-learning-report` |
| Update duplicates existing knowledge | Update the existing source instead of adding a parallel copy |
| Host-specific convention would enter portable core docs | Move it to host-specific packaging or docs |
| Edit would touch unrelated content | Narrow the patch |

### Phase 7: Draft The Edit For Handoff

When the user has asked to externalize and the gates pass, produce the concrete change for downstream
execution. Do not edit the file or run validation yourself — that is handed off.

1. Read the target file and nearby context.
2. Locate the smallest relevant section to change.
3. Draft the edit as a diff that preserves the document's tone, scope, and structure.
4. Name the repository or project checks that should validate the change once it is applied.
5. Report the placement, the drafted diff, and the validation to run.

If no project check applies to the destination, say so.

If the user only asks where knowledge should live, or asks for a placement recommendation, stop at
the placement plan without drafting a diff.

## Output

When planning only:

```markdown
# Knowledge Persistence Plan

**Candidate knowledge**: ...
**Recommended destination**: ...
**Artifact type**: ...
**Reason**: ...
**Pollution risks**: ...
**Action**: [draft edit | ask | decline | route to write-learning-report]
```

When a specific edit is drafted (Action was `draft edit`):

```markdown
**Placement**: [file:section]
**Drafted diff**: [the proposed change as a fenced diff, for downstream execution to apply]
**Validation to run after applying**: [command(s), or why none apply]
```

## Rules

- Externalize only mature, supported knowledge with a clear future use.
- Plan and draft the edit only when the user has asked to externalize into a durable source; hand the actual file change and validation to execution.
- Prefer one maintained source over parallel copies.
- Choose the narrowest durable home.
- Do not turn personal insight into project policy.
- Do not write host-specific assumptions into portable core instructions.
- Do not create rules, governance, or mandatory behavior without clear user intent.
- Keep `write-learning-report` learning reports non-referable; if their insight must be referenced,
  persist the insight into an appropriate durable home instead.
