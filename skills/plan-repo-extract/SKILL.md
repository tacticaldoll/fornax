---
name: plan-repo-extract
description: Use when an agent needs to assess whether a cohesive part of a repository should become an independent repository; evaluates extractability and plans dependency, API, history, and migration work rather than executing the split.
---

# Plan a repo extraction
Use this skill to **extract** a cohesive component out of its repository into an **independent
repository** — carefully lifting out the self-contained component while leaving the rest undisturbed. The
agent's default working scope is the repo; this skill operates at the **repo boundary**: it looks
inward to find cohesion, judges whether that cohesion is worth standing on its own, and — only then —
plans the carve.

Governing intuition: **most components should stay in-repo.** A separate repository buys independent
versioning and consumption at the cost of a cut dependency, a hardened API, split history, and its
own build/CI/release. The assessment must earn the split; "keep in-repo" is a common, correct
verdict.

**Input**: the repository component to assess for carve-out — if unnamed, discover the candidate in Phase 1; if the goal is only an internal module split, hand off to `plan-split`.

**Boundary**: evaluates and plans — produces a go/no-go assessment and, for a GO, a carve-out plan; does not run git surgery, create repos, publish, or move code.

## Workflow

### Phase 0: Anchor the scope

The working scope is this repository; the target is a **new, independent repository**. Confirm the
candidate component (named by the user, or to be discovered in Phase 1). If the intent is only a
cleaner internal module *within the same package*, this is the wrong skill — hand off to `plan-split`.

### Phase 1: Locate the cohesion

Find the candidate component's **true boundary** inside the repo — the members that cohere into one
responsibility, versus what is merely colocated. If the component is not yet a clean internal seam
(its members are scattered or entangled), hand off the internal decomposition to `plan-split` first; a
carve is only as clean as the seam beneath it.

### Phase 2: Assess extractability — the go/no-go

Judge whether the component *should* become its own repo (see
[references/extractability.md](references/extractability.md) for the criteria):

| Axis | Question | Weak signal (lean no) |
|---|---|---|
| **Cohesion** | Is it one responsibility with a nameable purpose? | It is a grab-bag or an arbitrary slice |
| **Coupling severability** | Can its outbound dependencies on the rest of the repo be severed or inverted? | It reaches deep into parent internals that cannot invert |
| **Independent value** | Does it stand alone — a real or likely second consumer, a distinct release cadence? | Only ever used by this one parent, in lockstep |
| **Cost** | Is the API surface, history, CI, publish, and consumer-migration cost worth it? | Cost dwarfs the benefit |

Emit a verdict: **GO** (worth an independent repo), **DEFER** (cohesive but no forcing function yet —
e.g. no second consumer), or **NO** (keep in-repo; optionally `plan-split` it internally instead).
For **DEFER** or **NO**, stop after the assessment and do not produce a carve-out plan.

### Phase 3: Plan the carve (only for GO)

- **Target blueprint (design forward, then reconcile)** — design what the component's boundary
  *should* be as if greenfield (`design-boundaries` is that pass), then reconcile it against the
  boundary recovered from the existing code: matches extract as-is; each gap becomes a fix-in-carve
  or accept-as-declared-debt entry (see [references/carve-mechanics.md](references/carve-mechanics.md)).
- **Dependency inversion** — the component must end up depending only outward/downward and on
  external packages, **never back on the parent**. For each outbound edge to the parent, decide:
  sever, invert (parent depends on the component), duplicate a small primitive, or pull it along.
  A residual back-edge means it is not independent — a cycle across the new repo boundary.
- **Public API** — the internal surface the parent used, reconciled against the blueprint, becomes a
  real, minimal, stable public API; everything else stays private. State the compatibility commitment.
- **History strategy** — preserve provenance (`git subtree split` / `git filter-repo` to carry the
  component's history) versus a fresh start; note the tradeoff.
- **New-repo scaffolding** — its own dependency manifest, build, CI, license, versioning.
- **Consumer migration** — how the parent (and any other consumer) switches from internal use to
  consuming the extracted repo as a dependency (path → published/pinned).

### Phase 4: Sequence the migration

Order into reversible, verifiable steps. A common progression:

1. `plan-split` internally so the component is a clean seam.
2. Introduce a package boundary in-repo (a workspace member) as an intermediate waypoint.
3. Invert/sever the cross-boundary dependencies until the component is acyclic-independent.
4. Split into the new repo (with history strategy).
5. Cut consumers over to depend on it.
6. Publish / pin as the release story requires.

### Phase 5: Adversarially verify the plan

- **Independence**: after the carve, is the component truly acyclic — zero dependency back on the
  parent?
- **API**: is the exposed surface minimal and stable, not a leak of former internals?
- **History**: is provenance preserved (or is a fresh start explicitly chosen)?
- **Consumers**: is behaviour preserved for every existing consumer across the cut-over?

### Phase 6: Produce the assessment and plan

```markdown
## Carve-out Assessment — [component]

**Verdict**: GO | DEFER (reason) | NO (keep in-repo; consider `plan-split`)
**Cohesion / Severability / Independent value / Cost**: [one line each]

## Carve-out Plan (only if GO)
- Boundary: [true members]
- Target blueprint vs current seam: [forward-designed boundary; gaps → fix-in-carve or accept as declared debt]
- Dependency inversion: [per outbound edge — sever/invert/duplicate/pull-along]
- Public API: [minimal surface + compatibility commitment]
- History: [subtree/filter-repo | fresh — why]
- New-repo scaffolding: [manifest/build/CI/license/versioning]
- Consumer migration: [path → published/pinned]
- Sequence: [ordered, reversible steps with per-step verification]
```

## Rules

- Evaluate before planning. A **NO / keep-in-repo** or **DEFER** is a valid, common outcome — do not
  carve for its own sake, and do not include a carve-out plan for those verdicts.
- Planning only. Do not run git surgery, create repos, publish, or move code — produce the
  assessment and plan; a human or follow-up step executes.
- Independence is the bar: the plan must leave the component with **no dependency back on the
  parent** (no cycle across the repo boundary), or the verdict is not GO.
- Preserve behaviour for existing consumers across the cut-over unless a break is explicitly declared
  and versioned.
- Address history/provenance explicitly — preserve it or consciously choose a fresh start.
- Extract toward a designed boundary, not the grown one. Reconcile the recovered seam against a
  forward blueprint; a pure reverse-read risks freezing an accidental boundary into a public API.
- Stay in lane; hand off at the boundary. For designing the target component boundary forward before
  reconciling it with the existing seam, point to `design-boundaries`. For finding/cleaning the internal
  seam beneath the carve, point to `plan-split`. The actual git surgery, repo creation, and
  publishing are execution — hand them off. Name the handoff rather than half-doing the other skill's
  job.
