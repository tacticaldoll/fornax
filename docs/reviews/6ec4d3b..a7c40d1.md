# Review Record — `6ec4d3b..a7c40d1`

Archived as received, so the reconciliation in `docs/dispositions/6ec4d3b..a7c40d1.md` can be
checked by a later round against the text it was handed.

```markdown
## Review Record

**Source**: local `git diff 6ec4d3b..HEAD` — five commits, 15 files, +712/-16
**Calibration**: Gates 1-8 (a new gate step that later rounds will trust; it reads untrusted record
content into printed diagnostics)
**Triage**: Red 1 / Yellow 3 / Green 11
**Coverage**: partial — gate-reviewed: scripts/check_workspace.py (Gates 3-8 vacuously);
partially-gate-reviewed: scripts/record_shape.py (Gate 1 only — its Gate 1 failed),
scripts/tests/test_record_shape.py (Gates 1-2), docs/dispositions/v0.4.1..de72982.md (Gate 1),
docs/dispositions/v0.4.1..61789c2.md (Gate 1); triage-only: docs/guards.md,
docs/dispositions/c60a6ba..af1185a.md, docs/dispositions/v0.4.1..6ec4d3b.md,
docs/dispositions/v0.4.1..1609403.second-reading.md, docs/dispositions/v0.4.1..e693b19.md,
skills/triage-findings/SKILL.md, skills/resolve-deadlock/SKILL.md, README.md,
development-knowns.yaml; unread: docs/reviews/v0.4.1..6ec4d3b.md — an archived input kept as
received, opened for nothing but its own presence
**Findings**: 10
**Verdict**: FAIL at Gate 1 + CONTRACT-VIOLATED
**Not executed**: static review only. Gate ran green at 440 tests; eight probes measured the claims
below. No runtime exercise of the CLI, no build.

### Gate Index

| Gate | Focus | Status |
|---:|---|---|
| 1 | Formatting & Syntax Hygiene | fail |
| 2 | Naming & Readability | fail |
| 3 | Error Handling & Observability | pass (vacuous) |
| 4 | Control Flow & Structural Clarity | pass (vacuous) |
| 5 | Responsibility & Boundaries | pass (vacuous) |
| 6 | Business Logic Integrity | pass (vacuous) |
| 7 | Deduplication & Composition | pass (vacuous) |
| 8 | Security & Parameter Integrity | pass (vacuous) |

Gates 3-8 are marked vacuous and that is the honest reading, not a hedge. Gate 1 failed for
record_shape.py, so Gates 2-8 are blocked for the only substantial new module in the range; Gate 2
failed for test_record_shape.py, blocking 3-8 for it. The single file that carried Gates 3-8 is
check_workspace.py, whose change is a five-line Step entry — a subject those gates cannot
meaningfully judge. Reading 3-8 as a real pass here would be the "cheapest evidence in reach" that
gates.md warns about. The precedent is docs/dispositions/v0.4.1..61789c2.md, which drew this
distinction for four prose documents.

Five of the ten findings sit at gates the ladder blocked. They are in Structural Causes, per Phase
4c — the extraction reached them before any gate opened, and withholding a cause already in hand is
what makes a repair land in the wrong place.

### Against-Contract

| # | Clause | Falsifier attempted | Result | Evidence |
|---|---|---|---|---|
| 1 | a7c40d1: "Reading a row's cells needs no owning parser: a cell is bounded by the pipe the table defines and GFM's own escape" | an escaped backslash before a delimiter, which GFM reads as two cells | VIOLATED — read as one cell. The lookbehind treats any backslash before a pipe as escaping it, one level short of the escape it claims | scripts/record_shape.py:60 |
| 2 | workspace_files: "A check that silently found nothing to inspect would report the same clean result as one that inspected everything"; check_sources: "A missing interpreter is a failure, not a skip" | point the check at a root holding a contract and no records | VIOLATED — prints OK and exits 0. Probed | scripts/record_shape.py:232 |
| 3 | ruff.toml: "100 is the width the Python and the markdown already use" | measure the non-table prose lines this range added | VIOLATED — two added prose lines are 101 characters, and nothing checks Markdown width | docs/dispositions/v0.4.1..61789c2.md, docs/dispositions/v0.4.1..de72982.md |
| 4 | AGENTS.md: "When a module takes ownership of a behaviour, enumerate every existing implementation of it" | is the fifth paired-optional named against the four it joins? | holds — the docstring names all four | scripts/record_shape.py:70 |
| 5 | a7c40d1: "the check needs no exemptions at all" | look for any path list, suffix carve-out or skip set | holds — none; the one record with no such table is covered by a predicate | scripts/record_shape.py |
| 6 | 43c7964: an unmatched OUTPUT-TEMPLATE marker "contributes nothing to the seam inventory" | render the inventory before and after | holds — byte-identical, --check green | scripts/seam_contract.py:155 |
| 7 | AGENTS.md: a diagnostic must not carry untrusted text unwrapped | a record cell holding a right-to-left override | holds — one printable call, and cells reach it through repr as well | scripts/record_shape.py:225 |
| 8 | The contract's five keys must be derived, never copied | change the template's fifth key and see whether the check follows | holds — keys come from marked_code_blocks; no literal key in the module | scripts/record_shape.py:139 |

### Claims Verified

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | a7c40d1: "key-set closure 2 red, Result domain 1, Dispositions uniqueness 1" | each rule disabled in turn, revert confirmed landed, suite run | verified |
| 2 | a7c40d1: "Gate step and README's generated block land together" | --check failed before the rewrite and passed after, both in one commit | verified |
| 3 | a7c40d1: "Workspace gate green at 440 tests" | ran it | verified |
| 4 | 43c7964: "verified byte-identical before and after" | diffed the rendered inventory | verified |
| 5 | 0dc1076: "The class is two lines" | the tree reports none remaining | verified |
| 6 | a7c40d1: "a cell is bounded by the pipe the table defines and GFM's own escape" | the escaped-backslash probe | REFUTED |
| 7 | 0e0b2c1: "the five declared checks against every Record integrity table reports no extra row anywhere" | re-ran the sweep; the new check agrees over 24 records | verified |

### Structural Causes

| # | Finding | Cause (the thing to change) | Cause location | Gate that would carry it |
|---|---|---|---|---|
| 1 | DECLARED-INVARIANT-COVERS-ONE-FIELD | the guard ranges over one of two payload fields, and both accessors gate on the first. Make the invariant range over every payload, or collapse to one | scripts/record_shape.py:86, :100 | Gate 3 (blocked) |
| 2 | INVARIANT-SPELLED-TWO-WAYS | the four siblings spell it one way and this spells it another; one concept in two spellings | scripts/record_shape.py:86 | Gate 2 (blocked) |
| 3 | EMPTY-SCOPE-READS-AS-CLEAN | an absent corpus returns an empty diagnostic list and the entry point reports clean | scripts/record_shape.py:210, :232 | Gate 3 (blocked) |
| 4 | ESCAPED-BACKSLASH-MISREAD | the escape is read by lookbehind rather than consumed left to right | scripts/record_shape.py:60 | Gate 6 (blocked) |
| 5 | WRONG-CELL-BLAMED | the Result is read as the last cell rather than by the column the header names | scripts/record_shape.py:117, :185 | Gate 3 (blocked) |
| 6 | HEADER-SKIP-BY-POSITION | three sites skip the header by index; "a table's body" has no name | scripts/record_shape.py:146, :180, :196 | Gate 7 (blocked) |
| 7 | — (extraction reached it; no finding) | declared recovers the Result domain by splitting on a pipe that rows already unescaped; undocumented coupling | scripts/record_shape.py:151 | Gate 6 (blocked) |
| 8 | — (extraction reached it; no finding) | record_defects opens the file and applies two policies in one body — the read/judge split check_text established | scripts/record_shape.py:170 | Gate 5 (blocked) |

### Responsibility & Dependency Ledger

Rows in this section are not findings.

| # | Unit | Its job (one clause) | Handed in | Reached directly |
|---|---|---|---|---|
| 1 | check_workspace.STEPS | name every gate step in the order the gate runs them | none | Step (constructed inline, module-level constant) |

Gate 5 opened over one unit, and that is the ladder's doing rather than an omission.
record_shape.py's Gate 1 failed, so Gates 2-8 are blocked for every unit in it — rows, declared,
record_defects, check, main and Declared all went unopened at this gate. test_record_shape.py's Gate
2 failed, blocking 5 for its units. Everything else is triage-only or unread by the Phase 3 coverage
sets. The one Gate 5 reading the extraction did reach is Structural Causes row 8.

### Gate 1: Formatting & Syntax Hygiene

| # | Location | Violation | Correction |
|---|---|---|---|
| 1 | scripts/record_shape.py:118 | Gate 1: a comprehension that copies a list unchanged — dead code | found.append(cells[1:-1] if len(cells) > 2 else []) |
| 2 | scripts/record_shape.py:232 | Gate 1: a directory listing sorted to take its length, re-globbed after check already walked it | have check return the count, or len(list(...)); the sort has no purpose |
| 3 | docs/dispositions/v0.4.1..61789c2.md, docs/dispositions/v0.4.1..de72982.md | Gate 1: two prose lines added at 101 characters against the convention ruff.toml states for the Python and the markdown; nothing checks Markdown width | reflow both paragraphs to 100 |

### Gate 2: Naming & Readability

| # | Location | Violation | Correction |
|---|---|---|---|
| 4 | scripts/tests/test_record_shape.py:78, :99, :112, :121 | Gate 2: the suite resolves the repository as the working directory while its sibling asserts against the module's own ROOT; the same test means something different depending on where the suite starts | use record_shape.ROOT |

### Structural Appendix

Declared — a frozen dataclass with two payload fields and one reason, the only paired-optional in
this family carrying more than one payload. That is finding 1's cause: the four siblings hold one
payload each, so their single guard is complete, and copying their shape to a two-payload type left
half the invariant unstated.

rows — pure, no I/O, deepest nesting 1. Reads to the delimiter the table defines, which AGENTS.md
blesses without an owner; the escape handling falls one level short. A malformed row yields an empty
cell list which every caller skips, so a malformed row is dropped rather than reported — not raised,
because no record contains one and Gate 3 is blocked for this file.

record_defects — opens the file, then applies the key/Result policy to one section and the
uniqueness policy to another. Its elif means a row with an undeclared key never has its Result
judged, which is deliberate and correct.
```
