## Disposition Record

**Source**: `docs/reviews/8dc34ca..ba81ab1.md`, 7 reported findings, FAIL at Gate 2 + CONTRACT-VIOLATED. Run in fresh context by a reviewer that did not author the range; persisted from the text as received
**Scope**: `8dc34ca..ba81ab1`, derived with `git diff --name-only` — `scripts/skill_model.py`, `scripts/validate_skills.py`, `scripts/tests/test_validate_skills.py`, one commit
**Prior round**: `docs/dispositions/ebf16c7..48ce457.md`

The prior record's range does not abut this one; commits lie between them with no record of their own, which is the condition already registered as `review-rounds-settled-without-a-record` and is not re-reported here as a finding.

### Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | FAIL at Gate 2 + CONTRACT-VIOLATED | the index records Gate 2 `fail` and it is the lowest failing gate; three VIOLATED rows in Against-Contract answer for the suffix | pass |
| Calibration / Gate Index | Gates 1–7 | the index records Gate 1 opened, Gate 2 opened and failed, Gates 3–7 blocked by the ladder, Gate 8 not inspected with its reason stated. `gate-reviewed` is empty rather than overclaimed | pass |
| Finding count | 7, itemised as Gate 2 two rows, Against-Contract three VIOLATED rows, Structural Causes two rows | the record carries Gate 2 two rows and Against-Contract three VIOLATED rows as stated, but **three** Structural Causes rows name no finding, not two. Eight findings are triaged below | mismatch |
| Coverage | partial, with four unit sets enumerated | `gate-reviewed` empty; `partially-gate-reviewed` enumerated with the gates opened for each (1–2); `triage-only` empty; `unread` empty. The enumerated units account for every unit the findings name | pass |
| Non-finding sections | the `Findings` field excludes the Claims Verified REFUTED row and the Ledger rows | the Ledger states its own rows are not findings and is empty with its reason; the REFUTED row is Claims Verified #6. But Claims Verified #2 carries `partial`, which the field neither counts nor excludes — its content keys alike with Gate 2 #2 and is triaged there rather than twice | mismatch |

Claims Verified #6 is REFUTED for absence of evidence inside a static scope, not for being false. Runtime evidence exists outside that scope and is recorded here rather than in the input: `.venv/bin/python scripts/check_workspace.py` passed at `ba81ab1`, and the pre-commit hook ran it before the commit was accepted. This settles the input's stated limit; it does not convert a static reading into a runtime one anywhere else in the record.

### Prior scope resolution

| Prior finding | Scope evidence stated by this round's input | Membership | This round's slot |
|---|---|---|---|
| all fifteen ids of `ebf16c7..48ce457` | four enumerated unit sets, none naming a unit of `shell_script`, `read_whole`, `runtime_contract`, `development_knowns` or their records | outside | Out of scope this round |

### Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach (every location it touches) | Route |
|---|---|---|---|---|---|---|
| 1 | The module docstring still describes the constants as definitions, which they stopped being when the aliases were bound to the schema's fields | DEFINITION-NAMED-ON-THE-BINDING, ALIAS-REASON-OVERREACHES | 1a restate the ownership paragraphs in binding voice, and give each alias its own reader | `restate` | `scripts/skill_model.py` module docstring, at "is the single definition" (twice), "stay module names because sibling scripts", and the `HANDOFF` paragraph | document is `scripts/skill_model.py`'s own docstring; no code handoff |
| 1 | " | " | 1b delete the `STATUSES` alias, which no sibling script or prose reads, and point its one test read at the field | `converge` | the `STATUSES` binding, `test_validate_skills.ValidateSkillTests.test_unknown_status_fails`, and 1a's reach for the sentence that named it | `plan-implementation` |
| 2 | `FormatSchema` took ownership of the skill-name grammar without the enumeration growing to match; two further spellings sit in the same two files | NAME-GRAMMAR-ENUMERATION-SHORT | 2a extend the enumeration sentence to name the `producer` group and the handoff pattern's own group | `restate` | `scripts/skill_model.py` module docstring, at "in development_knowns.py, and the same inline in" | document is `scripts/skill_model.py`'s own docstring; no code handoff |
| 2 | " | " | 2b route the `producer` group through `schema.FormatSchema`'s name pattern | `converge` | `validate_skills.RECORD_INPUT_PATTERN`, and 2a's reach | `plan-implementation`. Changes what validates — the docstring already says unifying the spellings is a decision, not a cleanup |
| 3 | The seam reaches `validate_skill` and stops, while the docstrings claim a filling the whole collection reads | MAIN-SEAM-HAS-NO-READER, SCHEMA-STOPS-SHORT-OF-THE-MAP | 3a narrow both claims to the seam that exists, and say `skill_graph` and `distribution_manifest` are pinned to `FORNAX_FORMAT` | `restate` | `scripts/skill_model.py` module docstring, at "lets a collection state a different filling"; `scripts/validate_skills.py` module docstring, at "Where the values come from" | documents are the two module docstrings; no code handoff |
| 3 | " | " | 3b remove `main`'s `schema` parameter, which has no caller, no flag and no test | `converge` | `validate_skills.main` | `plan-implementation` |
| 3 | " | " | 3c extend the seam to `skill_graph.load` and `distribution_manifest`, so one filling governs every reader | `converge` | `skill_graph.load`, `skill_graph.render`, `distribution_manifest.validate_distribution`, `validate_skills.main` | `plan-implementation` |
| 4 | The default sits on the inner checks, where it is unreachable and where the next caller can take `FORNAX_FORMAT` back in silence | DEFAULTS-ON-THE-INNER-CHECKS | 4a make `schema` required on the three inner checks, leaving the default on `validate_skill` and `main` | `forbid` | `validate_skills.validate_handoffs`, `validate_skills.validate_skill_manifest`, `validate_skills.validate_skill_document` | `plan-implementation` |
| 5 | The frozen rationale claims more than `dataclass(frozen=True)` delivers: the `families` mapping is mutable in place and shared with the alias | FROZEN-CLAIM-OVER-A-MUTABLE-DICT | 5a type the field as a mapping and fill it through `types.MappingProxyType` | `forbid` | `schema.FormatSchema`, `skill_model.FORNAX_FORMAT` | `plan-implementation` |
| 5 | " | " | 5b weaken the rationale to what freezing covers, leaving the mapping as it is | `restate` | `schema.FormatSchema` docstring, at "Frozen because a check that reads a value" | document is `scripts/skill_model.py`'s own docstring; no code handoff |
| 6 | The suite asks the owner two ways: migrated reads take the schema field, unmigrated reads take the alias | TWO-SPELLINGS-IN-THE-SUITE | 6a point the remaining alias reads at `FORNAX_FORMAT`'s fields | `converge` | `test_validate_skills.ValidateSkillTests.test_unknown_family_fails`, `test_validate_skills.ValidateSkillTests.test_unknown_status_fails`, `test_validate_skills.SkillModelTests.test_families_carry_a_title_each` | `plan-implementation` |

The Reach column cites a symbol or a quoted phrase rather than `file:line`. Which template asks for
which has to be said, because the two disagree: the installed `fornax` plugin at `0.4.1` — the text
this round actually ran under — asks for `file:line`, while `skills/triage-findings/SKILL.md` in this
tree asks for a file plus the unit inside it, or a quoted phrase where no unit owns the text. This
record follows the tree's, which is also what the citation rule requires of a record: a coordinate
that survives an edit. The exemption AGENTS.md grants a Review Record's evidence column does not
extend here.

The first wording of this paragraph named neither version and said only that "the triage template"
asks for `file:line`. A later round read the tree's copy, found the opposite, and reported the
paragraph as describing a requirement that does not exist. Both readings were of a real text; what
was missing was the word saying which.

Repair 1b removes the `STATUSES` binding, so this record cannot name it as a live symbol and the
Reach cell names it as text instead. The citation gate step refused the removal until it did, which
is the signal the guard row for this finding predicted. What changed is the citation's form; the
repair it names and the disposition that accepted it are untouched.

Later, the carve-out moved the schema type into the package being extracted, and the three cells
that named it under its old module now name it under `schema`, where it went. The superseded
spelling is not written here: this record is a subject of the citation gate, and naming a symbol
that no module defines is the thing the gate refuses, so the disclosure says which module it left
rather than reproducing the coordinate it left behind.

Two further edits, disclosed here because they were not disclosed where they were made. The
Self-check answer about the Reach form was corrected in the same commit as the Reach note above; it
described a form this record's table does not use, and the correction says what the table does. That
cell reconciles this record against its contract, which is nearer to a reading than a coordinate is,
so it is named here rather than left to a commit message. And the three guard rows in
`docs/guards.md` that cite this round's cases by class had their class names updated when the cases
were regrouped — coordinates, forced by the citation gate, with the readings beside them untouched. Same treatment and
same reason: a Reach cell names where a repair touches, which is a coordinate and not a reading, and
the gate refused the move until the coordinate was current. Disclosed here rather than left for a
reader to discover that this record's coordinates were edited after it was settled.

### Pattern

Causes 1, 3 and 5 share one shape: **a sentence written for the structure that existed before the value moved, left standing after it moved.** Each states an ownership — definition, filling, immutability — that the code stopped supporting in the same commit that wrote or kept the sentence. Repairing the three instances does not remove the shape, because nothing reads a docstring's ownership claim. The pattern-level repair is the rule the round already has and did not apply: when a module takes ownership of a behaviour, the prose that named the previous owner is part of the reach. Cause 2 is the same rule missed on its enumeration half, which is why it is a separate cause and the same lesson.

### Coupling

`1a` partially voided by `1b` — deleting the alias removes the sentence that misdescribes it, but the `FAMILIES` and `HANDOFF` sentences still need `1a`. `2a` voided by `2b` — routing the group through the owner removes the spelling the sentence would have had to enumerate. `5b` voided by `5a` — a mapping that cannot be mutated needs no weakened claim about it. `3a` narrowed by `3c` — extending the seam makes part of the narrowed claim false again, in the good direction.

### Dispositions

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| DEFINITION-NAMED-ON-THE-BINDING | 1 | new | accept | — |
| ALIAS-REASON-OVERREACHES | 1 | new | accept | — |
| NAME-GRAMMAR-ENUMERATION-SHORT | 2 | new | accept | — |
| MAIN-SEAM-HAS-NO-READER | 3 | new | accept | — |
| SCHEMA-STOPS-SHORT-OF-THE-MAP | 3 | new | accept | — |
| DEFAULTS-ON-THE-INNER-CHECKS | 4 | new | accept | — |
| FROZEN-CLAIM-OVER-A-MUTABLE-DICT | 5 | new | accept | — |
| TWO-SPELLINGS-IN-THE-SUITE | 6 | new | accept | — |

### Carried forward

none — every prior disposition lies outside this round's enumerated coverage.

### Closed

none — this round's scope contains no prior finding to close.

### Out of scope this round

The fifteen ids of `docs/dispositions/ebf16c7..48ce457.md`: PIN-HIDDEN-BEHIND-A-JOINED-COMMENT, WHOLE-LINE-ANSWER-APPLIED-TO-A-TEXT, WHOLE-LINE-PREDICATE-UNCONTROLLED, GOVERNANCE-MISSTATED-AS-A-PROHIBITION, REGISTERED-GRAMMAR-SILENTLY-DELETED, ORPHANED-REFERENCES-INTO-THE-ENTRY, COST-ENUMERATION-SHORT-BY-A-FORM, DIAGNOSTIC-ADVICE-MISFITS, PROSPECTIVE-SECTION-SPLICED, REFUSAL-CASES-ASSERT-ONLY-A-TYPE, HELPER-NAMED-AS-A-TEST-CASE, MEASUREMENT-POINTER-WRONG, COMMENT-STATES-TWO-RULES, TREE-MEASUREMENT-IN-A-MESSAGE, SHELL-WORDS-CLAIMS-A-REFUSAL-IT-DOES-NOT-MAKE. This round looked at three files under `scripts/` and says nothing about any of them.

### Undetermined

none — the input enumerates its coverage, which is what `static-review` requires of its own producer.

### Recurring

none.

### Ungrouped

none — every finding's cause is nameable from the code and from the clauses the code answers to.

### Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass — all fifteen in Out of scope this round, none elsewhere |
| Every accepted cause carries at least one repair with an enumerated Reach | pass — causes 1 through 6 each carry at least one, and every Reach cell names a file plus the unit inside it, or a quoted phrase where no unit owns the text, rather than describing a span |
