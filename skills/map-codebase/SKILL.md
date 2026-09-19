---
name: map-codebase
description: Use when an agent needs to understand how an unfamiliar codebase or subsystem actually works before changing it; maps entry points, control and data flow, key abstractions, and external effects to the depth the task needs, and reports what was not traced rather than reviewing quality or editing code.
---

# Map the codebase
Use this skill to **separate** an unfamiliar codebase — pull an opaque whole apart into its
identifiable flows and structures so you can see how it actually works before you touch it. The
output is a **system map**: where execution enters, how control and data move along the paths that
matter, the load-bearing abstractions and invariants, the external effects, and — explicitly — what
was not traced.

Governing intuition: **comprehension has no natural end — the task you are about to do sets the
horizon.** Trace the paths the change will touch, not the whole system. And a map is only as
trustworthy as the `file:line` under each claim: what you observe in the code is fact, what you infer
is inference — mark the difference and never present a guess about behaviour as established.

**Input**: the codebase, subsystem, or feature to understand, plus the change or decision the map will serve (which sets the needed depth) — if the purpose is unstated, ask what the map is for.

**Boundary**: reads and maps only — produces a system map, not a change or a quality judgment; does not edit or run state-changing commands.

## Workflow

### Phase 0: Anchor scope and purpose

Confirm two things before tracing anything:

- **What** to map — a subsystem, one feature's path end to end, a module, a call graph.
- **Why** — the change, fix, or decision the map serves. The purpose is the stopping rule; without
  it, comprehension has no bottom. If it is unstated, ask.

Read-only throughout: read, grep, and follow references — do not edit, and do not run commands that
change state.

### Phase 1: Find entry points and boundaries

- Locate where execution enters the area: public APIs, route/request handlers, CLI commands, event
  or message handlers, `main`/init, scheduled jobs, or the test harness that drives it.
- Map the module/package boundaries and the external surface: which I/O, network, filesystem,
  database, or third-party calls cross the edge.

### Phase 2: Trace the task-relevant flow

- **Control flow** — follow the call chain along the path(s) the purpose implicates: key branches,
  early returns, error and edge handling. Do not trace every path; trace the ones the change touches.
- **Data flow** — alongside, track the state each step reads and writes, where that state lives, what
  transforms it, and which side effects fire.

### Phase 3: Identify load-bearing abstractions and invariants

- Name the key types, interfaces, and contracts the area is built on.
- Name the implicit **invariants** a change must not break — ordering guarantees, nullability, object
  lifecycle, concurrency assumptions, transactional boundaries.
- Note coupling hotspots: what is widely depended on, and what is tangled.

### Phase 4: Surface unknowns and change risks

State what remains opaque or unverified, where confidence is low, and the landmines a change in
service of the purpose would hit (hidden callers, global state, ordering, concurrency).

### Phase 5: Produce the system map

```markdown
## System Map — [area]

**Purpose**: [the change/decision this map serves — sets the depth]
**Scope**: [what is mapped | what is deliberately out of scope]

### Entry points
[where execution enters — `file:line`]

### Flow (control + data)
[the task-relevant path(s): call chain, key branches, state read/written, side effects — `file:line`]

### Key abstractions & invariants
[load-bearing types/contracts; invariants a change must preserve]

### External effects
[I/O, network, DB, filesystem, third-party edges]

### Unknowns & change risks
[what is not understood; low-confidence areas; landmines for the intended change]

### Not traced
[paths/areas deliberately left unmapped, and why — the map's boundary]
```

## Rules

- Read-only. Read, grep, and follow references; do not edit code or run commands that change state.
- Map to the depth the purpose needs. Comprehension is unbounded — trace the paths the change will
  touch, not the whole system, and state the horizon.
- Ground every claim in the code (`file:line`). Mark inference as inference; do not present a guess
  about behaviour as fact.
- State what was not traced. The **Not traced** section is required — an unmarked gap reads as
  "understood" when it is not.
- Do not judge or fix. This maps how the code works, not whether it is good; quality findings and
  bug fixes are a different job.
- Stay in lane; hand off at the boundary. To judge code quality, point to `static-review`. To trace a
  specific bug or stack trace to its root cause, point to `diagnose-issue`. To plan splitting
  a unit you now understand, point to `plan-split`; to design a target structure, point to `design-boundaries`.
  To orient to governance and conventions rather than code behaviour, point to `orient-repo`. Name
  the handoff rather than half-doing the other skill's job.
