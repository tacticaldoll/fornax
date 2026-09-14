## Disposition Record

**Source**: `docs/reviews/ba81ab1..1a84428.md`, 15 reported findings, FAIL at Gate 1 + CONTRACT-VIOLATED + CLAIM-REFUTED. Run in fresh context by a reviewer that did not author the range; persisted from the text as received
**Scope**: `ba81ab1..1a84428`, derived with `git diff --name-only` — 45 files, eleven commits
**Prior round**: `docs/dispositions/8dc34ca..ba81ab1.md`

### Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | FAIL at Gate 1 + CONTRACT-VIOLATED + CLAIM-REFUTED | the index records Gate 1 `fail` and it is the lowest failing gate; four VIOLATED rows and the refuted claims answer for the two suffixes | pass |
| Calibration / Gate Index | Gates 1–7 | the index records every gate's status, says which file closed each ladder, and names why Gate 8 was not opened. `gate-reviewed` is populated rather than empty, which no prior input here has managed | pass |
| Finding count | 15, itemised as Gate 1 two, Gate 2 three, Gate 5 one, Gate 7 one, Against-Contract five VIOLATED, Claims Verified one REFUTED, Structural Causes two | the itemisation is wrong in two places that nearly cancel. Against-Contract carries five VIOLATED rows but the same field excludes one of them as settled remainder, so four count. Claims Verified carries two REFUTED rows not counted elsewhere, not one. Structural Causes carries three rows naming no finding, not two. Sixteen findings are triaged below | mismatch |
| Coverage | partial, with four unit sets enumerated | `gate-reviewed` enumerated with the ladder stated per file; `partially-gate-reviewed` enumerated with the gate that closed each; `triage-only` enumerated as the import-rewrite files; `unread` empty. The enumerated units account for every unit the findings name | pass |
| Non-finding sections | the `Findings` field excludes the settled-remainder contract row, the duplicate REFUTED rows, the Ledger rows, and the `holds`/`verified` rows | every excluded class is named and each row carries the axis it duplicates. The Ledger states its own rows are not findings. One row is excluded on a ground the field does not name — the Gate 1 section's unlisted import-grouping observation, excluded against `development-knowns.yaml` rather than against a duplicate axis — and naming that ground in the row is what keeps it from reading as an omission | pass |

### Prior scope resolution

| Prior finding | Scope evidence stated by this round's input | Membership | This round's slot |
|---|---|---|---|
| the eight ids of `8dc34ca..ba81ab1` | four enumerated unit sets, covering `validate_skills`, `skill_model`, the new package and the suite | inside | closure candidates → Closed |

### Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach | Route |
|---|---|---|---|---|---|---|
| 1 | The package's boundary is a sentence with no mechanism, and the grep that checked it was anchored where the evidence is not: the edge out is an indented `TYPE_CHECKING` import | PACKAGE-EDGE-OUT-AND-BACK | 1a move `shell_script` into the package | `converge` | `scripts/shell_script.py`, `scripts/runtime_contract.py` at its `shell_script` import | `plan-implementation` |
| 1 | " | " | 1b give `read_whole.shell_words` a package-defined parameter type, converted at the call site | `distinguish` | `agent_skill_format.read_whole.shell_words`, `scripts/shell_script.py`, `scripts/runtime_contract.py` | `plan-implementation` |
| 1 | " | " | 1c move `shell_words` out of the package, beside `shell_script` | `converge` | `agent_skill_format.read_whole.shell_words`, `scripts/shell_script.py` | `plan-implementation` |
| 1 | " | " | 1d assert in the suite that no package module imports outside the package | `guard` | `test_module_claims.imports`, `test_module_claims.ModuleClaimTests` | `plan-implementation`. Additive: it is what keeps 1a–1c true, and voids none of them |
| 2 | The proxy is a property of one value rather than of the type, so the type's docstring describes something the type does not guarantee | SCHEMA-DOCSTRING-DESCRIBES-A-VALUE, MAPPING-NOT-PROXIED-BY-TYPE | 2a wrap the mapping in `FormatSchema.__post_init__`, making the docstring true of every instance | `forbid` | `agent_skill_format.schema.FormatSchema` | `plan-implementation` |
| 2 | " | " | 2b move the three value-describing sentences back to the filling and leave the type saying only what freezing covers | `restate` | `agent_skill_format.schema.FormatSchema` docstring, `skill_model.FORNAX_FORMAT` | document is the two modules' own prose; no code handoff |
| 3 | `main` regained a default while the module prose still says it holds the only one | ONLY-DEFAULT-CLAIM-FALSE | 3a state that the entry point and the per-skill check each hold one | `restate` | `scripts/validate_skills.py` module docstring, at "It carries the only default" | document is that module's own docstring |
| 3 | " | " | 3b remove `validate_skill`'s default so the sentence becomes true | `forbid` | `validate_skills.validate_skill`, `test_validate_skills.check` | `plan-implementation` |
| 4 | `SchemaSeamTests` accumulated cases that are not seam cases, and its contract sentence still describes only the seam ones | SEAMTESTS-CONTRACT-OVERREACHES | 4a split the non-seam cases into classes named for what they hold | `converge` | `test_validate_skills.SchemaSeamTests` | `plan-implementation` |
| 4 | " | " | 4b keep one class and rewrite the contract to cover both kinds | `restate` | `test_validate_skills.SchemaSeamTests` docstring | document is that class's own docstring |
| 5 | A module with a `__main__` moved and its own invocation did not | SKILL-INTERFACE-USAGE-STALE | 5a rewrite the Usage block to the module form and name the path condition | `restate` | `agent_skill_format.skill_interface` module docstring, at "Usage:" | document is that module's own docstring |
| 5 | " | " | 5b keep a thin entry point in `scripts/` so the documented command stays true | `converge` | `agent_skill_format.skill_interface`, a new module under `scripts/` | `plan-implementation` |
| 6 | Guard rows were updated to measurements while the section heading that governs them still says nothing was measured, and names no tree | GUARDS-HEADING-CONTRADICTS-ITS-ROWS | 6a rewrite the heading to the measured form and name the commit each measurement was taken at | `restate` | `docs/guards.md`, at "Written 2026-09-14, prospective" and its lead paragraph | document is `docs/guards.md`; maintained by this round |
| 6 | " | " | 6b move the measured rows into their own dated-and-committed section, leaving the prospective one to the rows that are still prospective | `restate` | `docs/guards.md`, at "Written 2026-09-14, prospective" | document is `docs/guards.md` |
| 7 | A trailing-whitespace line that no gate reads | TRAILING-WHITESPACE-IN-GUARDS | 7a delete the whitespace | `restate` | `docs/guards.md`, at the `SCHEMA-STOPS-SHORT-OF-THE-MAP` row | document is `docs/guards.md`. The registered known `e501-exempts-a-whitespace-free-line` already records that no gate measures Markdown width; this is the same absence, one property over |
| 8 | A blanket substitution rewrote the disclosure sentence along with what it disclosed, so the sentence now says a name was replaced by itself | DISCLOSURE-ATE-ITS-SUBJECT | 8a restore the superseded name inside the disclosure | `restate` | `docs/dispositions/8dc34ca..ba81ab1.md`, at "now name it as" | document is the prior round's record; a disclosure that cannot be read is not one |
| 9 | The Reach note names "the triage template" without saying which, and the Self-check answer describes a form the table does not use | REACH-NOTE-UNVERSIONED, SELF-CHECK-CONTRADICTS-THE-NOTE | 9a version the note — the installed 0.4.1 asks for `file:line`, the repository's own skill asks for a file plus the unit, and the record follows the latter — and correct the Self-check answer to the form the table uses | `restate` | `docs/dispositions/8dc34ca..ba81ab1.md`, at "The triage template asks for" and at its Self-check row | document is the prior round's record |
| 10 | "Which Python files are this repository's modules" is answered in three places and owned in one, and the answer added this round is the shape its owner already records as silently lossy | MODULE-MAP-ANSWERED-A-THIRD-TIME, SWEEP-MISSED-THE-OTHER-GLOB | 10a route both test-side answers through `check_citations.modules` | `converge` | `test_module_claims.MODULES`, `test_check_workspace.WorkspaceChecks` at its generator glob | `plan-implementation` |
| 10 | " | " | 10b keep the local maps but carry the owner's collision field and assert it empty | `guard` | `test_module_claims.MODULES`, `test_check_workspace.WorkspaceChecks` | `plan-implementation` |
| 11 | A dated measurement of another collection was transcribed into a docstring with its date and version dropped | TREE-MEASUREMENT-IN-A-DOCSTRING | 11a move the measurement into a dated record and leave the docstring saying what the check refuses | `restate` | `validate_skills.undeclared_directories` docstring, `docs/guards.md` | document is that function's docstring plus this round's ledger |
| 12 | A recorded red count includes a second red produced by state one case leaves for the next | GUARD-COUNT-IS-POLLUTION | 12a restore `FORNAX_FORMAT` in the case's cleanup so the count reflects its own guard | `guard` | `test_validate_skills.SchemaSeamTests` at the mapping case | `plan-implementation` |
| 12 | " | " | 12b annotate the row that the second red is a pollution effect | `restate` | `docs/guards.md`, at the `FROZEN-CLAIM-OVER-A-MUTABLE-DICT` row | document is `docs/guards.md` |
| 13 | The citation exemption names one column of a record whose coordinates sit in four | REVIEW-EXEMPTION-NARROWER-THAN-ITS-OBJECT | 13a widen the exemption to a Review Record's coordinates into the tree as reviewed | `restate` | `AGENTS.md`, at "a Review Record's own evidence column" | document is `AGENTS.md`; governance prose, needs the owner's assent |
| 13 | " | " | 13b state in the citation check's own prose why `docs/reviews` is outside `RECORDS` | `restate` | `check_citations.SUBJECTS`, `check_citations.RECORDS` | document is that module's docstring |

### Pattern

Causes 3, 5, 6, 8, 9 and 11 share the shape the prior round already named and this round did not apply: **a sentence written for a state that then changed, left where it was.** What is new is the mechanism in two of them — a blanket textual substitution rewrote its own disclosure (cause 8), and a transcription dropped the version that made a measurement quotable (cause 11). Both are edits made by a tool over a whole file rather than by a reader over a sentence. The pattern-level repair is not another round of corrections: it is that a substitution across a record or a docstring is read back before it is committed, which is the one step neither of those two had.

Cause 1 is a different shape and the more serious one: a boundary asserted in prose, verified by a grep anchored at line start, and refuted by an indented import. The claim was made twice and checked once, wrongly.

### Coupling

`2b` voided by `2a` — a type that guarantees the proxy needs no sentence moved away from it. `3a` voided by `3b`. `4b` voided by `4a`. `6b` and `6a` are alternatives, not a sequence. `12b` voided by `12a`. `1d` voids none of `1a`–`1c` and is what keeps whichever lands from silently reverting.

### Dispositions

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| PACKAGE-EDGE-OUT-AND-BACK | 1 | new | accept | — |
| SCHEMA-DOCSTRING-DESCRIBES-A-VALUE | 2 | new | accept | — |
| MAPPING-NOT-PROXIED-BY-TYPE | 2 | new | accept | — |
| ONLY-DEFAULT-CLAIM-FALSE | 3 | new | accept | — |
| SEAMTESTS-CONTRACT-OVERREACHES | 4 | new | accept | — |
| SKILL-INTERFACE-USAGE-STALE | 5 | new | accept | — |
| GUARDS-HEADING-CONTRADICTS-ITS-ROWS | 6 | new | accept | — |
| TRAILING-WHITESPACE-IN-GUARDS | 7 | new | accept | — |
| DISCLOSURE-ATE-ITS-SUBJECT | 8 | new | accept | — |
| REACH-NOTE-UNVERSIONED | 9 | new | accept | The finding holds; the reviewer's stated cause does not. It read the repository's own skill, which asks for a file plus the unit, and concluded the note describes a requirement that does not exist. The note describes the installed `0.4.1` plugin, which asks for `file:line` and is the text the round actually ran under. What is wrong is that the note names neither version |
| SELF-CHECK-CONTRADICTS-THE-NOTE | 9 | new | accept | — |
| MODULE-MAP-ANSWERED-A-THIRD-TIME | 10 | new | accept | — |
| SWEEP-MISSED-THE-OTHER-GLOB | 10 | new | accept | — |
| TREE-MEASUREMENT-IN-A-DOCSTRING | 11 | new | accept | — |
| GUARD-COUNT-IS-POLLUTION | 12 | new | accept | — |
| REVIEW-EXEMPTION-NARROWER-THAN-ITS-OBJECT | 13 | new | defer | Real, and the repair edits `AGENTS.md`'s governance prose rather than code. It has no effect while `check_citations.RECORDS` names only `docs/dispositions`. Now when a round proposes adding `docs/reviews` to that constant — that proposal is what makes the wording load-bearing |

### Carried forward

none — every prior finding closed.

### Closed

| Finding | Prior disposition | Code evidence the cause no longer holds | Input evidence |
|---|---|---|---|
| DEFINITION-NAMED-ON-THE-BINDING | accept | `skill_model`'s prose names the schema's fields as the definitions and the module names as bindings onto them | Gates 1–7 opened over the module; the round re-reports no claim of definition on a binding |
| ALIAS-REASON-OVERREACHES | accept | each binding names the reader that keeps it, and the one with none was removed | Gates 1–7 opened; Claims Verified confirms `NAME_PATTERN` has no code reader and says which reader keeps it |
| NAME-GRAMMAR-ENUMERATION-SHORT | accept | the enumeration names the record-input producer group and the handoff capture group | Against-Contract row 1 swept the whole tree for a further spelling and found none |
| MAIN-SEAM-HAS-NO-READER | accept | the parameter returned with a case that reads it | Structural Appendix confirms the sole reader and that the CLI remains unable to pass one |
| SCHEMA-STOPS-SHORT-OF-THE-MAP | accept | the filling reaches the distribution check; the map generator is pinned by a decision the prose now states | Against-Contract row 6 re-ran the falsifier, found the same result, and recorded it as settled remainder rather than as a finding |
| DEFAULTS-ON-THE-INNER-CHECKS | accept | the three inner checks require a filling | Gates 1–7 opened over `validate_skills`; the round's finding about defaults concerns the module's prose, not the checks |
| FROZEN-CLAIM-OVER-A-MUTABLE-DICT | accept | `FORNAX_FORMAT.families` is a mapping proxy | Claims Verified confirms the repair; the residue — that the guarantee is the value's and not the type's — is this round's `MAPPING-NOT-PROXIED-BY-TYPE`, a new finding rather than a survival of the old one |
| TWO-SPELLINGS-IN-THE-SUITE | accept | the suite's reads go to the schema's fields but for two sites whose reasons are stated | Claims Verified confirms both retained sites and their reasons |

### Out of scope this round

none.

### Undetermined

none — the input enumerates its coverage.

### Recurring

none. `MAPPING-NOT-PROXIED-BY-TYPE` is adjacent to a closed finding rather than a return of it: the prior repair's whole Reach changed and the prior cause no longer holds, while the new finding names a different one — the guarantee's owner rather than its presence.

### Ungrouped

none.

### Sent back for review

The input did not report it and it is not this record's to add. The repository's `skills/triage-findings/SKILL.md` and the installed `0.4.1` plugin state the Reach form differently, and the installed text is what an agent running the collection reads. That is a divergence between a shipped skill and the tree, reached while verifying cause 9's stated cause, and it wants a review of its own — it bears on the release, not on this range.

### Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass — all eight in Closed, none elsewhere |
| Every accepted cause carries at least one repair with an enumerated Reach | pass — causes 1 through 12 each carry at least one, and every Reach cell names a file plus the unit inside it, or a quoted phrase where no unit owns the text, which is the form the repository's own skill asks for |
