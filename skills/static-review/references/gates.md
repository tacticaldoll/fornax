# Review Gates

Use these gates for local, gate-based code review. Gates open in order. A failed lower gate blocks
higher gates.

## Gate 1: Formatting & Syntax Hygiene

Check:

- Formatting follows project convention.
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
- Abbreviations are domain-standard.

Failure meaning: the code cannot be understood without author narration.

## Gate 3: Error Handling & Observability

Check:

- No silent swallowing of errors.
- Error messages are actionable.
- Boundary inputs are handled.
- Invalid state fails fast.
- Resources are cleaned up.
- Critical paths have enough structured observability.

Failure meaning: the code may work only on the happy path.

## Gate 4: Control Flow & Structural Clarity

Check:

- Nesting is justified.
- Functions are not doing multiple jobs.
- Loops have explicit termination.
- Complex control flow can be understood by reading.

Failure meaning: the code may work, but readers cannot prove it.

## Gate 5: Responsibility & Boundaries

Check:

- Domain layers are not mixed without justification.
- Dependency direction is correct.
- Public interfaces are minimal.

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
- Existing patterns are followed.
- API or state transitions have migration paths when needed.

Failure meaning: the code is clean and structured but wrong.

## Gate 7: Deduplication & Composition

Check:

- Repeated logic is extracted when the shared concept is real.
- New patterns converge with existing patterns.
- Composition is preferred over brittle inheritance or copy-paste.
- Future duplication risk is considered.

Failure meaning: the code is correct but creates another copy of the same idea.

## Gate 8: Security & Parameter Integrity

Check:

- User-controlled parameters are classified by risk.
- Authentication and authorization are both enforced where relevant.
- Sensitive data is not exposed in logs, errors, URLs, or responses.
- Injection surfaces are parameterized or isolated.
- No custom crypto, hardcoded secrets, weak randomness, or unjustified unsafe code.

Failure meaning: the code may pass all earlier gates but is still unsafe.
