## Disposition Record

**Source**: `docs/reviews/ebf16c7..48ce457.md`, 21 reported findings, FAIL at Gate 1 + SECURITY-ALERT + CONTRACT-VIOLATED + CLAIM-REFUTED. Run in fresh context because the author of the range could not supply one; it reached this triage inside a message and is archived there as received
**Scope**: `ebf16c7..48ce457`, derived with `git diff --name-only` — six files, seven commits
**Prior round**: `docs/dispositions/8a45707..2c1b448.md`

### Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | FAIL at Gate 1 + SECURITY-ALERT + CONTRACT-VIOLATED + CLAIM-REFUTED | the index records Gate 1 `fail` and it is the lowest failing gate; a Security Triage Alert, six VIOLATED rows and five REFUTED rows answer for the three suffixes | pass |
| Calibration / Gate Index | Gates 1–8 | the index records Gates 1 to 6 opened and 7 and 8 blocked, and says which units each aggregate cell belongs to and which ladder closed each. It also states plainly that no unit reached all eight, so `gate-reviewed` is empty rather than overclaimed — which the two previous inputs did not do | pass |
| Finding count | 21 | the itemisation is not given as a sum this time, and the rows counted cannot be recovered exactly from the record: six VIOLATED rows plus five REFUTED plus four partial plus two Gate 1 plus one Gate 2 plus seven Gate 6 exceeds 21, so some tracks of one defect are being counted once. The defects are traceable and the total is not | mismatch |
| Coverage | partial, four sets enumerated, `unread` empty, all six paths accounted | the accounting is complete, gates opened are named per unit, and the reason a YAML prose field offers no subject for five gates is stated | pass |
| Non-finding sections | the Ledger rows are marked not findings; every Structural Causes row names a finding | the Ledger is marked. Structural Causes rows 3 to 7 name their findings by description rather than by row number, which is looser than the previous input but still resolvable; none names none | pass, qualified |

### Prior scope resolution

The prior record left thirty-six open ids — fourteen in its Dispositions, two in its Carried forward
and twenty in its Out of scope this round. All fourteen Dispositions were repaired in this range and
the input verifies each against the repair its disposition named.

| Prior finding | Scope evidence stated by this round's input | Membership | This round's slot |
|---|---|---|---|
| QUOTED-HASH-CUT-BEFORE-THE-LEXER, SHELL-WORDS-CLAIMS-A-REFUSAL-IT-DOES-NOT-MAKE, PROSPECTIVE-SECTION-SPLICED | `read_whole.shell_words` and `docs/guards.md` reviewed, and the input reports each repair as partial with a named falsifier | inside | re-reported → Dispositions |
| OPERATOR-BRANCH-UNCONTROLLED, MATCHER-ENUMERATION-BLIND-TO-NON-REGEX, GUARD-DIED-WITH-ITS-ONLY-CALLER, REVERT-INSTRUCTION-AMBIGUOUS, ENTRY-POINT-CHECK-READS-ONE-SPELLING, ENTRY-POINT-CHECK-BOUND-UNDECLARED, CONTROL-MISLABELLED, COMMENTRULE-CITES-A-REMOVED-WORDING, MESSAGE-NUMBERS-IN-A-DOCSTRING, WORD-SPELLED-TREE-TOTAL, ENTRY-POINT-CLASS-OVERCLAIMS | the input verifies each repair explicitly | inside | closure candidate → Closed |
| UNIQUENESS-CONTROL-MISSING, LEDGER-TABLE-ROUNDS | inside a changed file, the carrying unit not among those reviewed | inside | closure candidate → Carried forward |
| the remaining twenty | the four enumerated sets contain no unit that carries them | outside | Out of scope this round |

### Causes and candidate repairs

| # | Cause (the thing to change) | Findings | Repair | Kind | Reach (every location it touches) | Route |
|---|---|---|---|---|---|---|
| 1 | **The seam, one level up from the last round's remit.** Nothing owns what "a command" is. `runtime_contract.run_commands` joins a continued line into one text, applying the shell's continuation rule to a line bash reads as a comment — bash ends a comment at the newline whatever the last character is — and `read_whole.shell_words` then answers for that whole text with a rule true only of a line. A leading comment therefore swallows a real install, and the caller reports no pin and nothing unreadable. This is the same shape the previous round named at the unit: a question with no owner, answered anyway | PIN-HIDDEN-BEHIND-A-JOINED-COMMENT, WHOLE-LINE-ANSWER-APPLIED-TO-A-TEXT, WHOLE-LINE-PREDICATE-UNCONTROLLED | 1a stop the join where bash stops the comment: `runtime_contract.run_commands` ends a command at a newline when the line it is continuing is a comment | `guard` | `scripts/runtime_contract.py` + `runtime_contract.run_commands`, `scripts/tests/test_runtime_contract.py` | `plan-implementation` |
| 1 | " | " | 1b make `read_whole.shell_words` refuse text holding a newline, its one-command premise having failed, so the callee stops answering a question about a text it was told is a line | `forbid` | `scripts/read_whole.py` + `read_whole.shell_words`, `scripts/tests/test_read_whole.py` + `test_read_whole.ShellWordTests` | " |
| 1 | " | " | 1c give the seam an owner rather than patching either side: one unit decides what a command is and hands single commands on, so neither the join nor the word reading can disagree about it | `distinguish` | `scripts/runtime_contract.py` + `runtime_contract.run_commands`, `scripts/read_whole.py` + `read_whole.shell_words` | `design-boundaries` |
| 2 | Durable prose in this repository asserts a prohibition `AGENTS.md` does not carry. A hand-written matcher for an uninstallable grammar is permitted where the grammar and its absent owner are registered, which this very entry does; what is forbidden is inventing a terminator list with neither. The false prohibition is stated as the ground for declining, so the decision reads as compelled where it was chosen on evidence | GOVERNANCE-MISSTATED-AS-A-PROHIBITION | 2a restate both places as the measured history — each hand-written reading of this rule proved wrong one character further out — rather than as a rule | `restate` | `scripts/read_whole.py` + `read_whole.shell_words`, `development-knowns.yaml` "shell-command-structure-read-by-hand" | none — document repair |
| 2 | " | " | 2b add the prohibition to `AGENTS.md` if it is meant, so the prose and the governance agree | `declare` | `AGENTS.md` "A matcher that reads a token" | `audit-governance` |
| 3 | A text edit made by slicing between two anchors, without asserting what the slice contains, deletes content nobody intended to touch. It removed the evidence item registering that `distribution_manifest.install_refs` bounds a git-ref and pip-URL grammar by hand, unmentioned in the message, leaving the grammar unregistered and two references arguing from an item that is gone | REGISTERED-GRAMMAR-SILENTLY-DELETED, ORPHANED-REFERENCES-INTO-THE-ENTRY | 3a restore the item and re-point both references | `restate` | `development-knowns.yaml` "shell-command-structure-read-by-hand", `docs/guards.md` "MATCHER-ENUMERATION-BLIND-TO-NON-REGEX" | none — document repair |
| 3 | " | " | 3b give the ref grammar its own entry, the shell entry having grown to carry several | `declare` | `development-knowns.yaml` | " |
| 4 | The stated cost of declining is short by a form, and the diagnostic's advice does not fit it. A word whose hash is quoted is refused too, because the predicate runs on posix-lexed words after quote removal, so an ordinary workflow line fails the gate and is told to move a comment it does not have | COST-ENUMERATION-SHORT-BY-A-FORM, DIAGNOSTIC-ADVICE-MISFITS | 4a name the quoted form in the docstring and the ledger, and give the diagnostic advice that fits both | `restate` | `scripts/read_whole.py` + `read_whole.shell_words`, `docs/guards.md` "declining the question" | none — document repair |
| 4 | " | " | 4b narrow the refusal so a word whose hash was quoted is read, which needs the quoting state the predicate discarded and is therefore the question with no owner again | `guard` | `scripts/read_whole.py` + `read_whole.shell_words` | `plan-implementation` |
| 5 | A settling turn deletes the prospective section of an earlier round and leaves its own standing, so a section claiming nothing is repaired survives inside the commits that repaired everything it named | PROSPECTIVE-SECTION-SPLICED | 5a delete or re-date the section in the turn that repairs its findings, and reflow the prose spliced in this range | `restate` | `docs/guards.md` "prospective — the 2c1b448 round" | none — document repair |
| 6 | Two rewritten cases assert only that a refusal happened, where the cases they replaced asserted an exact reading and every sibling pins the refused text. One of them passes for an unrelated reason and stays green when the rule it names is deleted | REFUSAL-CASES-ASSERT-ONLY-A-TYPE | 6a pin the refused text in both, and the reason in the one that can refuse two ways | `guard` | `scripts/tests/test_read_whole.py` + `test_read_whole.ShellWordTests` | `plan-implementation` |
| 7 | A module-level helper carries the `test_` prefix it inherited from the constant it replaced, so it is named as a test case and is not one — the only such callable in the tree, collected and errored by any runner that looks for the prefix | HELPER-NAMED-AS-A-TEST-CASE | 7a rename it to what it returns, and follow the name through the ledger row and the record cell that cite it | `restate` | `scripts/tests/test_module_claims.py` + `test_module_claims.test_modules`, `docs/guards.md` "the entry-point check", `docs/dispositions/8a45707..2c1b448.md` | `plan-implementation` |
| 8 | A pointer and a claim name a record that does not hold the measurement they cite, and the comment over `read_whole.COMMENT` states two rules for one pattern, the older of which this range's own control refutes | MEASUREMENT-POINTER-WRONG, COMMENT-STATES-TWO-RULES | 8a point at the record that holds the reading, and cut the superseded sentence over the pattern and in `runtime_contract.pins` | `restate` | `scripts/tests/test_module_claims.py` + `test_module_claims.entry_point_out_of_place`, `docs/guards.md` "the entry-point check", `scripts/read_whole.py` + `read_whole.COMMENT`, `scripts/runtime_contract.py` + `runtime_contract.pins` | none — document repair |
| 9 | A measurement of the tree was written into a commit message, which the hygiene rule names as the path by which a message's number becomes the tree's, and the non-stale form was already available in the ledger | TREE-MEASUREMENT-IN-A-MESSAGE | none listed — commit prose is history and is not editable. What the cause admits is the next message not carrying one | `restate` | none — the finding is closed by not repeating it | none |

### Pattern

**A question with no owner, answered anyway — now at the seam rather than inside the unit.**

The previous round found this at `read_whole.shell_words` and the repair declined the question. Cause
1 is the identical shape one level out: `run_commands` decides what a command is, `shell_words`
assumes it is one line, and neither owns the boundary, so a leading comment joined across a newline
hides a real install. The repair that fixed the unit did not look at what the unit is handed, which
is why the security alert the previous round raised survives its own repair.

Cause 3 is a different shape and is mine as an operator rather than as an author: a text edit made
by slicing between two anchors without asserting what lies between them. It has now done two things
in this session — inserted a paragraph at the top of a file when the anchors were reversed, and
deleted a registry item nobody mentioned. Both were caught by a check or a review rather than by the
edit, and the repair is a habit rather than a rule: assert the slice's contents before replacing it.

Cause 2 is worth separating from both. Three durable places now assert that this repository forbids
a hand-written matcher for an uninstallable grammar. It does not — it requires the grammar and its
absent owner to be registered, which is what the entry carrying the misstatement does. The decision
to decline was right on evidence and was written down as compelled by a rule, which is how a
judgement stops being re-examinable. `audit-governance` is the route for whether the rule should say
what the prose claims.

### Coupling

`1a` and `1b` are both worth having — one stops the join, the other stops the callee answering for
a text — and `1c` voids both by giving the boundary an owner. `2a` and `2b` are alternatives: state
the history, or make the rule true. `3a` and `3b` are alternatives. `4b` voids `4a`'s first half and
reopens the question with no owner, which is the argument against it. `8a`'s two halves are
independent.

### Dispositions

| Finding | Cause | Carried | Disposition | Reason (REQUIRED for decline and defer) |
|---|---|---|---|---|
| PIN-HIDDEN-BEHIND-A-JOINED-COMMENT — a joined comment line swallows a real install and no pin is reported | 1 | new | accept | — |
| WHOLE-LINE-ANSWER-APPLIED-TO-A-TEXT — a rule true of a line answers for a text spanning newlines | 1 | carried | accept | — |
| WHOLE-LINE-PREDICATE-UNCONTROLLED — no control on the axis where the surviving answer fails | 1 | new | accept | — |
| GOVERNANCE-MISSTATED-AS-A-PROHIBITION — durable prose asserts a rule the governance does not carry | 2 | new | accept | — |
| REGISTERED-GRAMMAR-SILENTLY-DELETED — an evidence item registering a hand-read grammar was removed unmentioned | 3 | new | accept | — |
| ORPHANED-REFERENCES-INTO-THE-ENTRY — two places argue from evidence the entry no longer holds | 3 | new | accept | — |
| COST-ENUMERATION-SHORT-BY-A-FORM — a quoted hash is refused and the stated cost omits it | 4 | new | accept | — |
| DIAGNOSTIC-ADVICE-MISFITS — the advice tells a reader to move a comment that is not there | 4 | new | accept | — |
| PROSPECTIVE-SECTION-SPLICED — a section claiming nothing is repaired survives the commits that repaired it | 5 | carried | accept | — |
| REFUSAL-CASES-ASSERT-ONLY-A-TYPE — two cases pass for any refusal, one for an unrelated one | 6 | new | accept | — |
| HELPER-NAMED-AS-A-TEST-CASE — a module-level helper carries the test prefix | 7 | new | accept | — |
| MEASUREMENT-POINTER-WRONG — a pointer names a record that does not hold the reading | 8 | new | accept | — |
| COMMENT-STATES-TWO-RULES — one pattern, two stated rules, the older refuted by this range's own control | 8 | new | accept | — |
| TREE-MEASUREMENT-IN-A-MESSAGE — a reading of the tree written into commit prose | 9 | new | accept | — |
| SHELL-WORDS-CLAIMS-A-REFUSAL-IT-DOES-NOT-MAKE | 1 | carried | decline | the overclaim it named is gone: the code now makes the refusal the docstring promised. The new overclaim in the same docstring is a different statement about a different case and is WHOLE-LINE-ANSWER-APPLIED-TO-A-TEXT, not this finding returning. Declining rather than carrying keeps the two from being settled as one |

Fourteen accepted, one declined, none deferred. Three are prior findings returning.

### Carried forward

| Finding | Prior disposition | Original reason, unchanged | Closure condition not established |
|---|---|---|---|
| UNIQUENESS-CONTROL-MISSING | accept | no alternate-spelling control for the separator | 1 — the carrying unit is in no reviewed set |
| LEDGER-TABLE-ROUNDS | out of scope in earlier rounds | unchanged | 1 — `docs/guards.md` opened Gate 1 alone |

### Closed

Eleven, each verified explicitly by the input against the repair its disposition named:
OPERATOR-BRANCH-UNCONTROLLED, whose branch no longer exists;
MATCHER-ENUMERATION-BLIND-TO-NON-REGEX, the field now offering a search rather than claiming an
enumeration and naming the forms it cannot reach; GUARD-DIED-WITH-ITS-ONLY-CALLER, the unrunnable
row now saying so where it is; REVERT-INSTRUCTION-AMBIGUOUS, both readings reproduced and the
recorded one named; ENTRY-POINT-CHECK-READS-ONE-SPELLING and ENTRY-POINT-CHECK-BOUND-UNDECLARED,
matched on the tree and over every test module git lists; CONTROL-MISLABELLED, the accepted side
controlled by a tab; COMMENTRULE-CITES-A-REMOVED-WORDING, the citation gone;
MESSAGE-NUMBERS-IN-A-DOCSTRING and WORD-SPELLED-TREE-TOTAL, both gone from the docstrings; and
ENTRY-POINT-CLASS-OVERCLAIMS, the class now stating the shape its check decides.

### Out of scope this round

Twenty prior dispositions, decidably excluded by the input's enumerated coverage: the units that
carry them are not in this range. DISPOSITION-DOMAIN-UNCHECKED,
MISSING-RESULT-COLUMN-YIELDS-A-DOMAIN, ABSENT-CLAIM-AS-MISMATCH,
SELFCHECK-FOLDED-INTO-THE-INPUT-AUDIT, READ-FAILURE-SPELLED-THREE-WAYS,
SHIPPED-SKILL-CITATION-UNVERIFIED, AGENTS-POINTS-AT-THE-WRONG-SYMBOL,
SHIPPED-SKILL-NAMES-A-PRIVATE-SYMBOL, NOQA-CLAIM-REFUTED, TRAILING-WHITESPACE-UNSEEN,
TRIGGER-KEYS-ON-THE-WEAKEST-AXIS, LIFECYCLE-OMITS-THE-NAMED-PRIOR, REVIEW-COVERAGE-AS-FINDING,
REVIEW-FILED-A-VIOLATION-AS-A-VERIFIED-CLAIM, PARAGRAPH-SPLIT-NOT-REFLOWED, FIXTURE-READ-AS-PRODUCT,
COVERAGE-ENUMERATION-ABSENT, RAWSCORES-PROVISIONAL, F-11 and F-12.

### Undetermined

`none`. The input enumerates four coverage sets and accounts for every changed path.

### Recurring

WHOLE-LINE-ANSWER-APPLIED-TO-A-TEXT and PROSPECTIVE-SECTION-SPLICED. Each had every location in its
recorded Reach changed, so each repair landed in full and a finding of the same identity survived
it. For the first the identity is the clause — a reader hands back the whole reading or an `Unread`
— and the unit, and this is its third return under three different causes: a matcher ahead of the
lexer, a proxy for a word boundary, and now a line rule applied to a text. Cause 1 is stated at the
seam rather than in the unit for that reason.

### Ungrouped

`none`.

### Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass — the prior record left thirty-six ids open, fourteen in its Dispositions, two in its Carried forward and twenty in its Out of scope. Three return here as current findings, eleven are in Closed, two in Carried forward and twenty in Out of scope; none in two homes and none dropped |
| Every accepted cause carries at least one repair with an enumerated Reach | pass for causes 1 to 8. Cause 9 has **none listed** and says why: its unit is commit prose, which is history and not editable, so what the cause admits is the next message not carrying a measurement rather than a repair to this one |
| Every commit this record names is reachable from HEAD | pass — `ebf16c7`, `48ce457`, `923c60a`, `e930f0c`, `40ff422` and `d0f61da` all resolve and are ancestors of HEAD |
| Every reconciliation row above was read from the file this record's Source names | mismatch — the input arrived inside a message and is archived as received; the archive is not independent of it and its table prose is condensed |
| Every claim this record makes about the tree was measured rather than taken from the input | pass for the load-bearing ones, re-run before acceptance: the joined-comment command through `run_commands` and `workflow_pins` with `bash -x` beside it, the quoted-hash refusals, and the deleted evidence item with both orphaned references counted |
| The finding declined above was declined on its own terms | pass — the overclaim it named is repaired and measured; what replaced it is a different statement about a different case, filed as its own finding so neither is settled by the other |
| This record was written in the turn that repaired | mismatch — no repair landed in this turn. All fourteen accepted findings are open |

