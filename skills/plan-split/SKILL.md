---
name: plan-split
description: Use when an agent needs to plan splitting a large or tangled code unit inside the same codebase; finds natural responsibility boundaries, dependency risks, and reviewable extraction steps rather than editing code or executing the refactor.
---

# Plan a code split
Use this skill to plan how to **split** a large or tangled code unit along its natural
single-responsibility seams — the natural boundaries where cohesive clusters separate cleanly. The
output is a decomposition **plan**: what moves where, in what order, preserving behavior and the
public contract, with the verification each step must pass.

Governing intuition: **a good split follows the code's own structure.** Do not impose a split where
the code is genuinely cohesive; the cohesive core that *is* the unit's purpose should stay whole. The
win is analysis cost and single responsibility, not module count.

**Input**: the code unit to split (a file, module, class, or function) — if unnamed, ask which unit, and pin the public surface that must not change before planning.

**Boundary**: plans only — produces a decomposition plan; does not move code, create files, run the build, or open changes.

## Workflow

### Phase 0: Read the unit and pin its contract

- Read the target unit in full and map the **public/observable surface that must not change**:
  exported names, signatures, re-export paths, and observable behavior.
- Map the **dependency edges**: what the unit imports, and what imports *it* (inbound references
  decide repointing cost and cycle risk).

### Phase 1: Find the seams

Identify cohesive single-responsibility clusters (see
[references/seams.md](references/seams.md) for patterns). For each candidate cluster record:

- What it is (a coherent responsibility, not an arbitrary line range).
- Whether it is **contiguous** or **scattered** through the unit.
- Its **shared primitives** — helpers used by several clusters (these decide where the seam falls).

### Phase 2: Analyze each candidate extraction

| Dimension | What to determine | Risk signal |
|---|---|---|
| **Dependency direction** | Does the extracted piece depend only *downward*, or would the parent also depend back on it? | A back-edge = an import **cycle** (a design smell even where the language permits it) |
| **Inbound edges** | Who else references the moved items? | Each external reference is a repoint; high count = churn and review surface |
| **Contract impact** | Must a public path stay reachable? | If yes, plan a re-export facade so the path is preserved; never a silent rename |
| **Minimal visibility** | The narrowest visibility each moved item can take and still be reached | Widening visibility "just in case" leaks surface |
| **Artificiality** | Is this a real responsibility, or splitting for its own sake? | A cohesive core, or tests/logic that only make sense together, should stay |

Flag **cycle risk** and **artificial splits** explicitly — they are the two decisions most often
gotten wrong.

### Phase 3: Sequence the extractions

- Order **leaf-first / lowest-coupling-first**: extract pieces with zero or few inbound edges before
  pieces others depend on.
- Note **interlocks**: extractions that must land together (e.g. a code split that a test move
  depends on), and call out any that are better deferred.
- Scope each extraction as an **independently verifiable step** (one reason to exist), not one large
  move.

### Phase 4: Adversarially verify the plan

Attack the plan before finalizing. Use separate passes or reviewers only when the host offers them;
otherwise reason through each lens directly:

- **Cycle**: does any proposed extraction create a back-edge / import cycle?
- **Contract**: does any step change a public path, signature, or behavior? (It must not.)
- **Artificiality**: is any split imposed against the code's structure — would it scatter one responsibility or
  force a shared primitive to duplicate?
- **Sequence**: is the order dependency-correct, and is each step verifiable on its own?

### Phase 5: Produce the decomposition plan

Output the plan and hand off — do not edit:

```markdown
## Decomposition Plan

**Unit**: [file/module/class/component]
**Contract to preserve**: [public surface + behavior]
**Non-goals**: behavior-preserving only — no API change, no new feature, no logic change.

### Ordered extractions
| # | Cluster (what moves) | Target | Dependency direction | Inbound repoints | Contract-preservation | Visibility | Verification |
|---|---|---|---|---|---|---|---|
| 1 | … | new module/file | one-way ↓ | [callers to repoint] | re-export facade / none | narrowest that still reaches its callers (flag any widening) | [tests/build/lint that must stay green] |

### Interlocks & deferred
[Extractions that must land together (and why); any deliberately deferred and why.]

### Kept whole (and why)
[Clusters deliberately not split — cohesive core, artificial-to-separate, cycle-risk deferred.]
```

Each extraction's **Verification** column names the checks an implementer must run to confirm the
step is behavior-preserving (existing test suite parity, type/build check, linter, formatter, and a
diff-fidelity review). The specific commands are project-specific — name the *criteria*, and defer
the exact invocation to the project's own conventions.

## Rules

- Analysis only. Do not move code, create files, run builds, or open changes — produce the plan; an
  implementer executes it.
- Behaviour-preserving only. If a genuinely better design requires changing behavior or the public
  contract, say so and mark it out of scope — that is a design change, not a split.
- Preserve public paths via re-export facades; never plan a silent rename of a reachable symbol.
- Do not split for its own sake; keep a cohesive core whole.
- Prefer the narrowest visibility each moved item can take; flag any that must widen and why.
- Flag cycle risk and interlocks explicitly; sequence leaf-first so each step is independently
  verifiable.
- Stay in lane; hand off at the boundary. This skill plans an internal code split. If the extracted
  cluster is cohesive enough to live as its own repository, point to `plan-repo-extract`; and when the
  target structure does not yet exist as code, point to `design-boundaries`. For reviewing the
  resulting diff once implemented, point to `static-review` or another available code-review workflow. Name
  the handoff rather than half-doing the other skill's job.
