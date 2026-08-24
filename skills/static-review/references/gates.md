# Review Gates

Use these gates for local, gate-based code review. Gates open in order. A failed lower gate blocks
higher gates.

A check that defers to a source outside itself — a project convention, a declared structure, the
call sites of an interface — names where that source is found. When that source lies outside the
review scope, or the project declares none, say so in the report and judge only what the scope
shows; a check states its own fallback only where it differs from that.

A check that names no source is answered by whatever evidence is cheapest to reach, and the gate
then reads as passed on the strength of the one sub-check that was easy. Gate 6 states this at
length; every gate owes it.

## Gate 1: Formatting & Syntax Hygiene

Check:

- Formatting follows project convention — locate the convention (a formatter or lint config, a style
  section in the project's own guide) and judge against it; when none is found, say so in the report
  and judge only what the code contradicts internally.
- No dead code, commented-out code, unused imports, or unreachable branches.
- No debug residue such as print statements or temporary logs.
- Imports and file organization are coherent.

Failure meaning: the code was not prepared for review.

## Gate 2: Naming & Readability

Check:

- Variables describe their content.
- Functions describe their action.
- Boolean names read as assertions.
- One concept uses one word consistently.
- Abbreviations are domain-standard — against the vocabulary the project's own docs, types, or
  glossary use; when none is declared, say so and judge only consistency within the scope.

Failure meaning: the code cannot be understood without author narration.

## Gate 3: Error Handling & Observability

Check:

- No silent swallowing of errors.
- Error messages are actionable.
- Boundary inputs are handled.
- Invalid state fails fast.
- Resources are cleaned up.
- Critical paths have enough structured observability — enough against the level the project's
  existing critical paths set; when the scope shows no comparable path, say so and judge only whether
  a failure here would be diagnosable from what is emitted.

Failure meaning: the code may work only on the happy path.

## Gate 4: Control Flow & Structural Clarity

Check:

- Nesting is justified.
- Sequential phases inside one function read as one flow. Whether the function owns more than one
  job is Gate 5's question, answered there per unit.
- Loops have explicit termination.
- Complex control flow can be understood by reading.

Failure meaning: the code may work, but readers cannot prove it.

## Gate 5: Responsibility & Boundaries

Check:

- Domain layers are not mixed without justification — against the layering the project declares (its
  module or package structure, a layering doc or ADR); when none is declared, read the layering the
  structure implies and say in the report that it was inferred.
- Dependency direction is correct — against the direction the project declares in an ADR, a layering
  doc, or the dependency edges its manifests already carry; when none is declared, judge that stable
  code is not made to depend on volatile code, and say the direction was inferred rather than
  declared.
- Public interfaces are minimal — against the call sites the review scope contains; an unused member
  is not unnecessary on scope alone.

One function has one job, and core logic is not unnecessarily hardwired to concrete infrastructure:
these two are answered **per unit, from the structural extraction**, not by one verdict for the gate.
The extraction already records each unit's I/O and external side effects, its captured variables and
hidden dependencies, and its domain distribution — that is the material this gate judges. A gate that
does not read it is answered by the cheapest evidence in reach, an import-direction scan across
modules, which reads as passed while no unit was opened.

For every unit this gate opened, its answer is two clauses:

- **The unit's job**, in one clause. A clause that needs "and" or "then" to hold is the finding — name
  the split.
- **Where each dependency comes from**: what the unit reaches directly — a global singleton, an
  environment variable, a concrete implementation it constructs inline — apart from what arrives as a
  parameter or an injected abstraction it was handed. A unit that both decides business behavior and
  reaches concrete infrastructure in the same body is the finding.

Both clauses are this gate's required output for every unit it opened, findings or not.

Failure meaning: the code is in the wrong place or owns the wrong responsibility.

## Gate 6: Business Logic Integrity

Ground this gate in a real source of truth, not assumption. If the repo carries a
spec or governance doc (`openspec/`, `PROJECT.md`, `AGENTS.md`, ADRs, a linked
issue), read it and judge "matches the requirement" against it. If none is
available, judge against the code's own stated intent and **say in the report that
no external spec was found** — do not invent a requirement to grade against.

Check:

- Business rules are encapsulated in semantic helpers.
- Logic matches the stated requirement or spec (read it; see above).
- Domain edge cases are considered.
- Existing patterns are followed — against the patterns the review scope contains, plus any the
  project declares (a style guide, the module this change parallels).
- API or state transitions have migration paths when needed.

Failure meaning: the code is clean and structured but wrong.

## Gate 7: Deduplication & Composition

Check:

- Repeated logic is extracted when the shared concept is real — against the other sites the review
  scope contains, plus any the project's style guide or ADRs name; one site alone is not a concept.
- New patterns converge with existing patterns — against the other copies the review scope
  contains, plus any convention the project's style guide or ADRs declare.
- Composition is preferred over brittle inheritance or copy-paste.
- Future duplication risk is considered.

Failure meaning: the code is correct but creates another copy of the same idea.

## Gate 8: Security & Parameter Integrity

Check:

- User-controlled parameters are classified by risk — by the sinks the scope shows each parameter
  reaching (a query, a shell, a path, a template), not by a taxonomy outside it.
- Authentication and authorization are both enforced where relevant — relevant against the policy
  the project declares (an authz matrix, a middleware convention, a documented public surface).
- Sensitive data is not exposed in logs, errors, URLs, or responses.
- Injection surfaces are parameterized or isolated.
- No custom crypto, hardcoded secrets, weak randomness, or unjustified unsafe code — justified
  against the convention the project declares for it (a required safety comment, an allowlist).

Failure meaning: the code may pass all earlier gates but is still unsafe.
