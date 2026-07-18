---
name: audit-governance
description: Use when an agent needs to test governance prose against what a project actually enforces; classifies claims as structural or judgment and recommends dissolve, convert, keep, or defer rather than editing documents or adding checks.
---

# Audit governance
Use this skill to challenge a project's **governance prose** against what the project **actually
enforces**, and decide what each claim should become. The test is enforcement: prose that a
mechanism already holds is redundant and can dissolve; prose that asserts a checkable property no
mechanism holds can convert into one; prose that carries a human judgment cannot, and stays.

It produces a per-claim disposition plan with reasoning; a human decides and acts on it.

Governing intuition: **governance prose is debt to be discharged into enforcement — but only where
the property is structural, and only when a real forcing function has arrived.** Most honest passes
conclude "leave it": a disciplined challenge protects load-bearing prose and resists premature rules
as often as it removes redundancy.

**Input**: the governance prose to interrogate (a charter, ADRs, `PROJECT.md`, README claims, style/lint rules, or a decision log) — if unspecified, ask which artifact; locate the enforcement surface before classifying any claim.

**Boundary**: plans only — produces a per-claim disposition plan; does not rewrite documents, delete prose, or add tests/checks.

## Workflow

### Phase 0: Scope the prose and locate the enforcement surface

- Identify the governance artifact(s) to interrogate (charter, ADRs, `PROJECT.md`, README claims,
  style/lint rules, a decision log).
- Identify what **enforces** claims in this project: tests, CI checks, the type system, linters,
  schema validation, runtime assertions, a self-governance/self-check suite, generated-and-pinned
  artifacts. This is where projects differ — every project enforces differently.
- **Read the governance's own decision log and exclusions first.** Many "consolidate / sink / DRY /
  retire" reframes are already-decided; do not re-litigate a standing rejection. Grep for the
  relevant decisions before endorsing any change.
- **Enumerate the discrete claims** to interrogate — the individual prose assertions in the
  artifact(s), each captured as a checkable proposition with its quote and location. These are the
  units Phase 1 classifies.

### Phase 1: Partition each claim — structural vs judgment

For every substantive/candidate prose claim, classify it (see
[references/disposition.md](references/disposition.md) for the full tests):

| Kind | Test | Consequence |
|---|---|---|
| **Structural** | Mechanically checkable against an artifact (code, config, the declared model) without reading intent | Candidate for enforcement; prose may be redundant |
| **Judgment** | Requires reading human intent / rationale / a value call | Must stay prose — a check here is a false-negative engine |

The partition is the load-bearing move. Getting it wrong in the structural direction manufactures a
gameable check that gives false assurance.

### Phase 2: Disposition each claim

| Disposition | When | Recommended action |
|---|---|---|
| **DISSOLVE** | Structural **and already enforced**, and the prose merely *indexes/restates* it (a coordinate, count, cross-reference, or verbatim copy that rots on edit) | Remove the redundant prose; point the reader to the enforced source or its generated projection |
| **CONVERT** | Structural but **not yet enforced** (or only partially — see the coverage trap) | Recommend a check; name the concrete observation source it would read |
| **KEEP** | Judgment, rationale, rejected alternatives, lineage, or a stable human-language invariant summary | Stays prose; it has no observation source, and readers benefit from seeing it inline |
| **DEFER** | Structural-and-convertible **but no forcing function yet** (it has not drifted; no second consumer) | Born-when-built; codifying now is infrastructure-ahead-of-need and builds a gaming target |

**The coverage trap:** before calling a claim enforced, confirm the mechanism covers the *whole*
claim, not just one direction of it (see
[references/disposition.md](references/disposition.md) Test 3).

### Phase 3: Adversarially verify the plan

Before finalizing, attack the plan from independent lenses (see
[references/disposition.md](references/disposition.md) for each lens's full mandate). Use separate
reviewers only when the host offers them; otherwise reason through each lens directly:

- **Loophole** — can a disguised violation pass a proposed CONVERT check?
- **Consistency** — does any disposition contradict a standing decision or silently narrow the charter?
- **Necessity** — is the forcing function real, or is this premature?

Record the honest bound: **green and plausible do not prove.** A standard gate may not exercise the
claim; state where confidence ends.

### Phase 4: Produce the disposition plan

Output a table and hand off — do not edit:

```markdown
## Governance Disposition Plan

**Artifact**: [what was interrogated]
**Enforcement surface**: [tests / CI / types / self-check / …]
**Standing decisions checked**: [yes — relevant entries | none found]

| Claim (quote + location) | Kind | Disposition | Reason | Observation source / What would be lost | Confidence |
|---|---|---|---|---|---|
| … | structural/judgment | dissolve/convert/keep/defer | … | … | high/med/low |

## Verdict
[e.g. "3 dissolve, 1 convert (deferred — no forcing function), rest keep. Net: the charter is
already well-migrated; recommend only the 3 pure prose removals."]
```

## Rules

- Analysis only. Do not edit governance docs, delete prose, or add checks — recommend; the human
  decides and acts.
- Convert a claim to a check **only if it is soundly checkable**; a judgment forced into a check is a
  false-negative engine — the one failure this skill must not cause.
- Never dissolve load-bearing prose (rationale, rejected alternatives, lineage, a stable invariant
  summary). Only *indexes/restatements that rot on edit* dissolve.
- Respect the forcing function: do not recommend codifying a rule ahead of a real need, and do not
  build a positive checklist that future contributors can game.
- Check the governance's own standing decisions and exclusions before endorsing any sink/consolidate/
  retire reframe.
- State partial-coverage gaps explicitly; do not treat "looks enforced" as "enforced".
- Stay in lane; hand off at the boundary. This skill plans governance disposition. When a
  "consolidate / DRY" reframe turns out to target duplicated **code** rather than prose, point to
  `plan-split` for the behaviour-preserving decomposition. When the audit surfaces an unresolved
  contradiction between requirements or parties rather than a prose-vs-enforcement mismatch, point to
  `resolve-deadlock`. For assessing extractable conversation knowledge, point to `assess-knowledge`;
  for persisting mature conversation knowledge, point to `save-knowledge`. Name the handoff rather
  than half-doing the other skill's job.
