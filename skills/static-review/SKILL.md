---
name: static-review
description: Use when an agent needs to review local or pasted code with sequential quality gates; resolves files, diffs, commits, branches, or snippets into a static review scope and reports findings without modifying code or calling remote services.
---

# Static code review
Use this skill to perform a local, gate-based static code review.

Governing intuition: **run the review as ordered gates — open each quality gate in order and let a
failure at a lower gate block the higher ones**. A review's deeper judgments are not useful when
basic hygiene, naming, or error handling is already broken, so the deeper gates give no meaningful
reading until the earlier ones clear. The gates in
[references/gates.md](references/gates.md) are the ordered stages.

It reviews local or pasted input and produces a structured report.

**Input**: pasted code or a diff, local file path(s), a local git diff, a commit hash or range, or a branch name — if none is given, ask for one; never fetch remote PR/MR data. Resolution detail in Phase 0.

**Boundary**: reviews local or pasted input only — produces a report; does not modify code, call remote PR/MR APIs, post comments, or approve.

## Workflow

### Phase 0: Resolve Local Input

Normalize the user's input into a review scope:

| Input | Resolution |
|---|---|
| Pasted code or diff | Review the provided content directly |
| Local file path(s) | Read full file content; no diff context unless available |
| Local git diff | Review changed files and hunks |
| Commit hash or range | Use local git diff when available |
| Branch name | Use local merge-base diff when available |
| Ambiguous request | Ask for files, diff, commit/range, branch, or pasted code |

Do not fetch MR/PR data, call remote APIs, or require authentication. If remote context is needed,
ask the user to provide a local diff or pasted content.

### Phase 1: Calibrate Review Depth

Choose how many gates to open. Default to Gates 1-5 for ordinary local changes.

| Context | Gate Range |
|---|---|
| Draft, WIP, exploratory code | Gates 1-3 |
| Ordinary feature or internal tool | Gates 1-5 |
| Shared library, production path, or public API | Gates 1-7 |
| Security-sensitive code, auth, crypto, command execution, or user input boundary | Gates 1-8 |

When ambiguous, ask what destination or risk level the code has.

### Phase 2: Triage Large Scopes

When the review scope contains more than 5 files, run a rapid triage before deep inspection.
For 5 or fewer files, skip triage and proceed to structural extraction.

Triage checks:

| # | Check | → Gate | Fail Signal |
|---|---|---|---|
| 1 | Dead code | Gate 1 | Commented-out code, unused imports, debug output |
| 2 | Naming clarity | Gate 2 | Public names are vague or misleading |
| 3 | Nesting depth | Gate 4 | Nesting deeper than 3 levels |
| 4 | Function length | Gate 4 | Functions are long enough that their flow cannot be followed by reading |
| 5 | Error swallowing | Gate 3 | Empty catch/except or ignored failure |
| 6 | Domain mixing | Gate 5 | I/O and business logic mixed in one unit |
| 7 | Raw field assembly | Gate 6 | Complex conditions lack semantic helpers |
| 8 | Duplication scent | Gate 7 | Similar logic appears repeatedly |
| 9 | Security smell | Gate 8 | Secrets, unsafe interpolation, sensitive logs, unchecked dangerous input |

The **→ Gate** column names the gate a failed check targets.

Classify files:

| Class | Criteria | Next Action |
|---|---|---|
| Red | 3 or more checks fail | Full gate inspection |
| Yellow | 1-2 checks fail | Inspect each failed check's targeted gate (→ Gate column) and all lower gates |
| Green | 0 checks fail | Record as `triage-only`; do not claim its gates passed |

Security smell is dual-track: report it as a triage alert even if Gate 8 is blocked by a lower gate,
and append `+ SECURITY-ALERT` to the verdict (see Verdict composition in Phase 4b).

### Phase 3: Structural Extraction

Before opening gates, extract structure for each reviewed function, class, module, or relevant code
unit. Use extraction to guide the gate review; do not rely only on raw diff text.

Record:

- Closures, callbacks, or nested functions.
- Inline objects or local entities with behavior.
- I/O operations and external side effects.
- Deepest nesting and the reason for it.
- Domain distribution: infrastructure, business, presentation, or mixed.
- Lifecycle: one-shot, persistent, or mixed.
- Captured variables and hidden dependencies.
- Obvious anomalies discovered during extraction.
- Source of truth for Gate 6: locate the spec/governance doc to judge logic against, or note that
  none was found (gates.md Gate 6 lists where to look).
- Responsibility and dependency origin, per unit: the unit's job in one clause, and for each
  dependency whether it arrives as a parameter or an injected abstraction or is reached directly (a
  global singleton, an environment variable, a concrete implementation constructed inline). Gate 5
  judges from these rather than scanning import direction; the Ledger in Phase 5 is where they land.
- Coverage inventory: place every in-scope unit in exactly one set — `gate-reviewed` when every
  calibrated gate was opened for it, `partially-gate-reviewed` when only a stated prefix of those
  gates was opened, `triage-only` when it received only Phase 2's rapid checks, or `unread` when it
  was declared in scope but never opened. For every partially-gate-reviewed unit, state the gates
  actually opened. Coverage is `complete` only when every in-scope unit is `gate-reviewed`;
  otherwise it is `partial`. Always enumerate all four sets, including for complete coverage. Never
  call a partial, triage-only, or unread remainder passed. These four name *units*; the Gate Index's
  `not inspected` names a *gate* the calibration never opened — different axes.
- Contract inventory (when the change has a contract — a spec, acceptance scenarios, a task/change
  checklist, or stated project invariants): list each clause as its own review target. One row per
  requirement, per acceptance scenario, and per invariant the change touches, plus one row per
  claimed-complete item (checked-off task, acceptance marked done). If no contract exists, record
  "no contract found" — do not skip silently. This inventory feeds the Against-Contract Review
  (Phase 4b), which is distinct from Gate 6: Gate 6 asks whether the logic *quality* holds up; the
  Against-Contract Review adversarially tries to *break* each clause and verifies each claim.

### Phase 4: Sequential Gate Review

Read [references/gates.md](references/gates.md) for gate definitions.

Open gates in order. If a gate fails, stop opening higher gates for that file or review scope. Do
not manufacture findings. Silence means compliance for detail sections; the gate index still records
which gates opened, passed, failed, or were blocked.

For a multi-file scope, the Gate Index and Verdict aggregate **worst-case** across fully and
partially gate-reviewed files for each gate they actually opened: a gate is `fail` if any reviewed
file fails it and `blocked` if a lower gate failed for the reviewed file that would have carried it;
per-file detail lives in the finding rows (each row is a `file:line`). The Coverage field, not the
Gate Index, says which gates each unit actually received and whether the whole declared scope was
inspected deeply enough to support a complete-review claim.

### Phase 4b: Against-Contract Review (dual-track)

Run whenever a contract inventory exists (Phase 3). This track is **not gated** — report it even
when a lower gate failed, exactly as the Security Triage Alert does. A contract violation or a
refuted claim can fail the verdict independently of the gate ladder.

**Verdict composition (all non-gated tracks apply):** the Verdict is the gate result followed by
every non-gated flag that fired — `gate-result [+ SECURITY-ALERT] [+ CONTRACT-VIOLATED]
[+ CLAIM-REFUTED]` on one line, not a single worst-case label. A gate failing at Gate 3 with a
refuted claim is `FAIL at Gate 3 + CLAIM-REFUTED`; a clean gate ladder with a refuted claim is
`PASS + CLAIM-REFUTED`. Keep the gate result (`PASS` / `FAIL at Gate N`) in the Verdict even when a
flag fires — do not drop it in favor of the flag alone.

For **each contract clause** (requirement, acceptance scenario, invariant), output one row:

1. The clause.
2. A concrete falsifier — a specific input, state, or sequence that *would* violate it.
3. Whether the change admits that falsifier: `holds` / `VIOLATED` / `unprovable statically`.
4. `file:line` evidence.

Try to break the clause; do not confirm that it reads correctly. A clause you cannot attempt to
falsify is `unprovable statically`, not `holds`.

For **each claimed-complete item** (checked-off task, acceptance scenario marked done), output one
row — list every such item, not only the doubtful ones. Each row: the claim, the `file:line` that
evidences it, and one of `verified` / `partial` / `REFUTED`. A claim with no locatable evidence in
the reviewed scope is `REFUTED` — never `partial`, never "cannot verify", never omitted. Use
`partial` only when evidence exists but is incomplete; "not in this diff" means `REFUTED`, because
the item was marked complete.

### Phase 4c: Structural Causes (dual-track)

Run for every finding reported above. This track is **not gated**: a finding's cause is reported even
when the gate that would have carried it is `blocked`.

The ladder blocks a gate because a *review* at that depth gives no reading while hygiene is broken.
It does not follow that a cause already in hand goes unsaid. Reporting a symptom while withholding
its cause is what produces a repair in the wrong place — and the finding then returns next round,
which is the failure this track exists to stop.

Each row carries: the finding it explains (or `—`), the cause stated as the thing to change rather
than the symptom that revealed it, where the cause lives (`file:line`), and the gate that would have
carried it with that gate's status.

Output a row in each of two cases:

1. **A reported finding whose cause lives elsewhere.** Ask what one change would remove the finding;
   when that change is not the finding's own location, the change is the cause.
2. **A structural observation the Phase 3 extraction already reached that a `blocked` or
   `not inspected` gate would have carried.** The extraction is not gated — it runs before any gate
   opens — so a cause it reached is already in hand, and the ladder withholding the gate does not make
   the cause unknown. A lower gate can fail on something as small as an inconsistent error message,
   and that is no reason to lose a structural reading already taken.

Name only what the extraction reached. Anything that would need the gate review this scope did not
perform is `not established` — say so rather than guessing at a depth the ladder declined. This track
carries **no verdict flag** and claims no gate coverage: every row names its gate's status, so the
Gate Index stays the honest statement of what was reviewed.

### Phase 5: Report

Produce a report using this format:

<!-- OUTPUT-TEMPLATE: review-record@1 text/markdown -->
```markdown
## Review Record

**Source**: [input reference]
**Calibration**: Gates 1-[N] ([reason])
**Triage**: [skipped | Red M / Yellow N / Green K]
**Coverage**: [complete | partial] — gate-reviewed: [...]; partially-gate-reviewed: [unit (Gates 1-N), ...]; triage-only: [...]; unread: [...]
**Findings**: [one number: every finding row below, gate sections and non-gated tracks alike — not the file counts in Triage, and not the Ledger rows]
**Verdict**: [PASS | FAIL at Gate N] [+ SECURITY-ALERT] [+ CONTRACT-VIOLATED] [+ CLAIM-REFUTED]
**Not executed**: [static review only — tests / build / runtime not run]

### Gate Index

| Gate | Focus | Status |
|---:|---|---|
| 1 | Formatting & Syntax Hygiene | [pass | fail | blocked | not inspected] |
| 2 | Naming & Readability | [pass | fail | blocked | not inspected] |
| 3 | Error Handling & Observability | [pass | fail | blocked | not inspected] |
| 4 | Control Flow & Structural Clarity | [pass | fail | blocked | not inspected] |
| 5 | Responsibility & Boundaries | [pass | fail | blocked | not inspected] |
| 6 | Business Logic Integrity | [pass | fail | blocked | not inspected] |
| 7 | Deduplication & Composition | [pass | fail | blocked | not inspected] |
| 8 | Security & Parameter Integrity | [pass | fail | blocked | not inspected] |

### Security Triage Alert

[Include only when triage check 9 fails. Report regardless of gate status; also append
`+ SECURITY-ALERT` to the Verdict.]

### Against-Contract

[Include when a contract inventory exists (Phase 4b). Report regardless of gate status.]

| # | Clause | Falsifier attempted | Result | Evidence |
|---|---|---|---|---|
| 1 | [requirement / acceptance / invariant] | [concrete input, state, or sequence] | [holds \| VIOLATED \| unprovable statically] | `file:line` |

### Claims Verified

[Include when the contract inventory has claimed-complete items.]

| # | Claim | Evidence | Result |
|---|---|---|---|
| 1 | [checked-off task or acceptance marked done] | `file:line` | [verified \| partial \| REFUTED] |

### Structural Causes

[Include when either Phase 4c case produces a row: a reported finding's cause lies outside its own
location, or Phase 3 already reached a structural observation that a blocked or `not inspected` gate
would have carried. Report regardless of gate status.]

| # | Finding | Cause (the thing to change) | Cause location | Gate that would carry it |
|---|---|---|---|---|
| 1 | the finding it explains \| — | stated as the change | `file:line` | Gate N (pass \| fail \| blocked \| not inspected) |

### Responsibility & Dependency Ledger

[REQUIRED whenever Gate 5 opened: one row per unit that gate opened, findings or not. An empty table
claims Gate 5 opened no unit; state that rather than omitting the table. Name the in-scope units this
gate did not open and why — blocked by a lower gate, or outside the calibration — so an omission the
ladder caused is distinguishable from one the gate simply did not answer. Name each dependency, not
only its category — a row answering `parameter` for a unit holding two dependencies of different
origin has lost which is which. `none` is an answer in either column, and so is `not determinable
from the reviewed scope` — when a unit's signature or construction site lies outside the reviewed
input, record that rather than assigning an origin it cannot read. Rows are not findings — a
violation also gets a Gate 5 row below.]

| # | Unit | Its job (one clause) | Handed in | Reached directly |
|---|---|---|---|---|
| 1 | `file:unit` | one clause; needing "and" / "then" is a finding | `repository (parameter)`, `clock (injected abstraction)` \| none \| not determinable from the reviewed scope | `TOKEN (environment variable)`, `Registry (global)`, `PgPool (constructed inline)` \| none \| not determinable from the reviewed scope |

### Gate N: [name]

| # | Location | Violation | Correction |
|---|---|---|---|
| 1 | `file:line` | Gate N: specific standard violated | Concrete correction |

### Structural Appendix

[Include summaries for code units related to findings.]
```

### Phase 6: Optional Fix Plan

Produce a fix plan only when the user asks for one.

The rules below assume each finding's disposition and repair are already settled. When
findings recur across review rounds, or when several findings look like one cause, settle that first
— hand off to `triage-findings` rather than planning a fix per finding.

Fix-plan rules:

- One violation per fix.
- Fix order follows gate order.
- Within the same gate, order by file and line unless logical dependencies require otherwise.
- No opportunistic fixes.
- Each fix includes verification criteria.

## Rules

- Review only; do not modify code.
- Use local or pasted inputs only; do not call remote PR/MR APIs.
- Open gates sequentially and stop at the first failed gate.
- Non-gated tracks (Security Triage Alert, Against-Contract, Structural Causes) are reported even when
  a lower gate failed. Phase 4b is the single source for how the Verdict composes, the
  falsify-every-clause rule, and the claimed-complete rule — follow it there; do not restate it here.
  Phase 4c adds no verdict flag: a reported finding whose cause sits at a blocked gate still names the
  cause, because a symptom reported without its cause is repaired in the wrong place.
- Give concrete corrections; avoid vague suggestions such as "consider improving".
- If all opened gates pass, the Gate Index is the report; do not invent findings.
- Report coverage independently from correctness. `PASS` means the opened gates passed for the
  fully and partially gate-reviewed units; only `Coverage: complete` extends every calibrated gate
  to the full declared scope. Every review enumerates all four coverage sets, and each
  partially-gate-reviewed unit names its opened gates rather than describing a remainder as passed.
- Stay in lane; hand off at the boundary. This skill is static, local review only. It reports
  findings and does not decide their disposition; to settle which findings are accepted and what each
  cause's repair would touch, hand off to `triage-findings`. For runtime or
  behavioral correctness, hand off to `plan-testing` (design the test strategy) or a runtime
  verification pass that exercises the change end-to-end; for deep security analysis beyond Gate 8's
  surface checks, hand off to `assess-threats`; to trace a reported bug to its root cause, hand off to
  `diagnose-issue`. Name the handoff rather than half-doing the other workflow's job.
