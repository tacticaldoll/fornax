---
name: design-boundaries
description: Use when an agent needs to design component boundaries for a feature or system before the code exists; partitions responsibilities into single-purpose components with minimal interfaces and an acyclic dependency direction, then pressure-tests the boundaries rather than editing code, splitting an existing tangled unit, or extracting a separate repository.
---

# Design component boundaries
Use this skill to **separate** a feature or system, at design time, into
components with distinct responsibilities and clean interfaces, partitioned by what changes
independently. The output is a **component design**: what components exist,
what each is responsible for, the interface each exposes, and which way the dependencies point —
before any code commits the structure.

Governing intuition: **draw boundaries along what changes independently, not along the nouns.** A
component earns its existence by having one reason to change and hiding it behind a narrow interface;
responsibilities that always change together belong in one component. Fewer cohesive components beat
many anemic ones — resist the decomposition you have not earned.

**Input**: the feature or system to structure — a requirements description, a spec, or a capability being added to an existing system (existing code is context, not the thing being split); if the target is an existing tangled code unit, hand off to `plan-split`. If no scope is given, ask what is being designed.

**Boundary**: designs and plans — produces a target component structure; writes no code, scaffolds nothing, and picks no concrete framework.

## Workflow

### Phase 0: Frame the system and its forces

Capture, before drawing any boundary:

- **Purpose** — what the feature/system must do, in one or two sentences.
- **Forces** — what is expected to **vary** independently (formats, providers, policies, UIs) versus
  what is **stable**. Boundaries fall along the axes of variation.
- **Consumers** — who calls this, and across what surface (in-process, network, CLI, other teams).
- **Constraints** — hard requirements: performance, security boundaries, deployment units, tech the
  team already owns.

If the real task is to untangle an *existing* code unit, this is the wrong skill — hand off to
`plan-split`. This skill designs a target structure; it does not read a tangle and plan its extraction.

### Phase 1: Enumerate responsibilities

List the distinct jobs the system does — each a **reason to change**, one line each. Stay at the
responsibility level (what work exists), not the noun level (what data objects exist). Two jobs that
always change for the same reason are one responsibility.

### Phase 2: Draw component boundaries

Group responsibilities into components. For each component record:

- **Single responsibility** — the one reason it changes.
- **Public interface (contract)** — the narrowest surface it exposes; everything else stays internal.
- **Dependency direction** — what it depends on. Depend inward/downward on stable abstractions;
  never let two components point at each other.

Record **shared primitives** (helpers/types several components need — decide where they live) and
what is **kept together** (responsibilities deliberately not split because they change as one).

### Phase 3: Pressure-test the boundaries

Load [references/boundaries.md](references/boundaries.md) and challenge the partition:

- **Earned?** Does each component have a real, distinct reason to change, or is it decomposition for
  its own sake? Collapse components that only ever change together.
- **Cohesion** — does what changes together live together, or is one change smeared across many
  components?
- **Interface minimalism** — is each surface the narrowest that still serves its consumers, or does
  it leak internals?
- **Cross-cutting concerns** — are logging/auth/config threaded as explicit seams, not scattered?

### Phase 4: Adversarially verify

Attack the design before finalizing. Use separate passes/reviewers only when the host offers them;
otherwise reason through each lens directly:

- **Cycle** — does any dependency edge form a loop? Invert or merge to break it.
- **God-component** — does one component carry several reasons to change? Split it.

(Over-decomposition and interface leaks are already caught by Phase 3's *Earned?* and *Interface
minimalism* lenses; re-check them here only if the design shifted.)

### Phase 5: Produce the component design

```markdown
## Component Design — [feature/system]

**Scope**: [what is being structured]
**Forces**: [what varies independently | what is stable | consumers]
**Non-goals**: design only — no code, no interface for out-of-scope needs, no premature generality.

### Components
| Component | Single responsibility | Public interface (contract) | Depends on (→, acyclic) | Visibility |
|---|---|---|---|---|
| … | one reason to change | narrowest surface | [components/abstractions] | public / internal |

### Shared primitives
[helpers or types used by several components, and where they live.]

### Kept together (and why)
[responsibilities deliberately not split — they change as one / cohesive core.]

### Boundary risks
[cycles avoided, god-component watch, interface-leak watch, over/under-decomposition calls.]
```

## Rules

- Design only. Do not write code, scaffold files, or pick a concrete framework — produce the
  component design; an implementer builds against it.
- Draw boundaries along reasons to change (axes of variation), not along domain nouns or default
  layers.
- Earn every component. Responsibilities that always change together stay in one component; fewer
  cohesive components beat many anemic ones.
- Keep the dependency graph acyclic. A back-edge between components is a design smell — invert the
  dependency or merge them.
- Keep each interface minimal — expose the narrowest surface that serves consumers; keep the rest
  internal.
- Stay in lane; hand off at the boundary. To split an existing tangled code unit into that structure,
  point to `plan-split`. To plan the implementation work that builds the design, point to `plan-implementation`. To
  extract a cohesive component into its own repository, point to `plan-repo-extract`. To
  decide whether to adopt an external dependency instead of building a component, point to
  `assess-dependency`. Name the handoff rather than half-doing the other skill's job.
