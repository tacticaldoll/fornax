# Repair guards

What must go red when a repair in the `v0.4.1` range is reverted, so a later round can retire the
finding by running something rather than by re-deriving the story from commit messages.

This file exists because findings sat in `Carried forward` round after round with no path out. Their
repairs were measured when they landed — a revert, a red test, a count in a commit message — and
none of that is re-runnable by a reader. What a round needed in order to close one was the evidence,
and the evidence was in prose nobody could execute.

Each **guarded** entry names the unit to revert and the test that must fail, both as symbols;
an entry with no guard names the finding and says why nothing can turn red, which is a row of its
own kind and not a half-filled one. Nothing here names a line: `scripts/check_citations.py` resolves
every symbol below, so an entry whose unit or guard is renamed away is loud rather than quietly
wrong.

Every finding a round accepted in this range has a row, closed ones included, and a finding whose
repair nothing can guard has a row saying so rather than no row at all. The first version held only
the findings still carried, which read the ledger as a way out rather than as what it is — the
record of what must break if a repair is undone, and a closed finding's repair can be undone like
any other. The second version was written in the turn that repaired, before the round's own findings
list existed, so it could not hold what that list would say; the ledger is completed in the settling
turn now, which `AGENTS.md` states.

**A finding closes on this ledger the way it closes on an input's explicit verification** — the
closure test in `skills/triage-findings/SKILL.md` accepts a verified repair in place of a
gate-reviewed unit, and a probe a round can re-run is a stronger verification than a reading of one.
What that does not claim is a gate: no gate has opened over most of these units, and this ledger
says what was measured rather than what was inspected.

A dated section is quotable only with the tree it names, so each one names its own.

**What a row is, and is not.** A row is an instruction a later round runs: revert that unit, run
that test, expect that many red. The number beside it is the result of one run on the date its
section names, and nothing in the tree re-verifies it — a static reading can check that the unit
and the test exist, which the citation gate step does, and no further. Treating the number as
verified state is the mistake; re-running the instruction is the point.

Two ways a run has produced a wrong number here, both recorded because a third will look like them:
the edit did not apply and the suite stayed green, which is why every edit is now confirmed to have
landed before its result is read; and the edit applied but was not the pre-repair code — a revert
that read `Path("scripts")` relative to the working directory rather than the fixture's root
changed behaviour for an unrelated reason and reddened cases the repair had nothing to do with. **A
revert has to be what the code was, not merely a change to the line the repair touched.**

## Measured 2026-08-27, at `1abbb01`

Each revert applied to that tree, the named test file run, the tree restored, and the whole suite
confirmed green afterwards.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| REF-FRAGMENT-CLOSES-QUOTE | the closing-quote check in `distribution_manifest.install_refs` | `test_validate_skills.ProjectedDescriptionTests.test_an_opening_quote_nothing_closes_leaves_the_ref_unread`, `test_validate_skills.ProjectedDescriptionTests.test_a_quoted_ref_ends_at_its_quote_and_nowhere_else` | 4 |
| VERDICT-SEAM | the publisher comparison folded into `validate_skills.validate_skill`, by printing its `OK` line before the sidecar block | `test_validate_skills.EntryPointTests.test_a_mismatched_sidecar_publisher_fails_the_entry_point` | 1 |
| VERDICT-CONTROL | the publisher comparison in `validate_skills.validate_skill`, by printing its `OK` line before the sidecar block — the same revert VERDICT-SEAM names, because this finding is the assertion that the `OK` line is absent | `test_validate_skills.EntryPointTests.test_a_mismatched_sidecar_publisher_fails_the_entry_point` | 1 |
| FENCE-HANDREAD | `seam_contract.elements`' use of `markdown_links.marked_code_blocks`, replaced by a hand-written fence pattern | `test_seam_contract.TemplateHeadingTests.test_a_four_backtick_template_keeps_a_three_backtick_example_inside_it`, `test_seam_contract.TemplateHeadingTests.test_a_tilde_fenced_template_is_the_output_template`, `test_seam_contract.TemplateHeadingTests.test_a_template_fenced_as_another_language_is_reported` | 3 |
| BINARY-AS-TEXT | the suffix narrowing removed from `check_text._hygiene`, restored | `test_check_text.TextHygiene.test_any_tracked_file_holding_a_nul_is_reported_not_skipped` | 4 |

## Measured 2026-08-28, at `aecf03d`

The rows below were added after the tree above. Two of their units — `install_documents` and the
reasons in `fingerprint` — were created at `aecf03d` and do not exist at `1abbb01`, so a later round
reproducing these reverts against the earlier tree would be sent to units that are not there. That
is why the sections are separate rather than one heading with two dates.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| NETWORK-PATH-AUTHORITY | `check_citations.URL_AUTHORITY`, narrowed back to the scheme form | `test_check_citations.LineCitations.test_a_url_authority_is_not_a_line_citation` | 1 |
| CHECKER-ERROR-STATES | the reason branch in `check_citations._symbol_citations` | `test_check_citations.ModuleIdentity.test_a_module_that_cannot_be_parsed_is_reported_as_that` | 2 |
| CHECKER-STEM-COLLISION | the collisions `check_citations.check` reports | `test_check_citations.ModuleIdentity.test_a_stem_naming_more_than_one_module_is_reported_once` | 1 |
| EXTENSION-RULE-TOO-NARROW | `check_citations.LINE_CITATION`, capped back to six letters | `test_check_citations.LineCitations.test_a_long_extension_is_still_a_line_citation` | 2 |
| DIAGNOSTIC-COMPOSES-A-PATH | the module path in `check_citations._symbol_citations`, composed instead of taken from the map | `test_check_citations.ModuleIdentity.test_an_unparseable_module_is_named_where_it_actually_sits` | 1 |
| CITABLE-SET-ASKS-THE-ENVIRONMENT | `check_citations.citable`, given a name nothing here imports | `test_check_citations.SymbolCitations.test_a_third_party_module_nothing_here_imports_is_reported` | 1 |
| IMPORTS-OUTSIDE-THE-INVARIANT | the raising accessor on `check_citations.Symbols`, so `imports` answers a reason-carrying value | `test_check_citations.ModuleIdentity.test_a_symbols_holding_a_reason_answers_neither_question` | 1 |
| SNAPSHOT-NEEDS-A-WORKTREE | the filesystem fallback in `distribution_manifest.install_documents` | `test_validate_skills.ProjectedDescriptionTests.test_a_non_worktree_validates_from_the_filesystem`, `test_validate_skills.ProjectedDescriptionTests.test_a_non_worktree_still_reports_a_stale_pin` | 2 |
| FINGERPRINT-COLLAPSED-NONE | the reasons in `evidence_currency.fingerprint` | `test_evidence_currency.DriftTests.test_each_way_a_fingerprint_fails_says_which_one` | 1 |
| UNRESOLVABLE-SAYS-NOTHING | the `OUTSIDE` branch in `evidence_currency.fingerprint`, folded back together with the one below it | `test_evidence_currency.DriftTests.test_an_unresolvable_path_says_what_stopped_it` | 2 |

## Measured 2026-09-03, at `5327d53`

Each revert applied to that tree, the named test run, the tree restored, and the whole suite
confirmed green afterwards at 424 tests. The three units below were created at `5327d53` and do not
exist at `aecf03d`, which is why this section is its own rather than rows under the heading above.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| CHECKER-CANNOT-DECODE | the `UnicodeError` branch in `check_citations.module_symbols` | `test_check_citations.ModuleIdentity.test_a_module_that_cannot_be_decoded_is_reported_as_that` | 1 |
| QUOTE-CLOSER-BY-EXISTENCE | the closer search in `distribution_manifest.install_refs`, back to asking whether the opening quote appears anywhere after the ref | `test_validate_skills.ProjectedDescriptionTests.test_a_later_unrelated_quote_does_not_close_the_word` | 3 |
| EVIDENCE-SECTION-UNBOUNDED | both section checks in `evidence_currency.load` | `test_evidence_currency.ModelTests.test_the_evidence_section_must_appear_exactly_once` | 2 |

`QUOTE-CLOSER-BY-EXISTENCE` carries a second row of a kind this ledger has not held before: a
control that must stay **green** under the same revert.
`test_validate_skills.ProjectedDescriptionTests.test_every_quoting_of_a_closed_word_reads_the_same_ref`
was run under that revert and passed, which is what distinguishes a check that reads the quote's
position from one that refuses every quoted ref. Recorded because the matcher rule in `AGENTS.md`
asks for both controls and only the red one is a guard in the usual sense. The pre-existing
`test_an_opening_quote_nothing_closes_leaves_the_ref_unread` also stayed green under the revert —
that is the measurement showing why one control was not enough to catch this defect.

## Measured 2026-09-07, at the commit carrying this section

Each revert applied to the tree, confirmed to have landed by reading the changed line back, the
named test run, the tree restored, and the whole suite confirmed green afterwards at 428 tests.

The tree is named as the commit carrying this section rather than by hash, for the reason the
`v0.4.1..6ff702e` Disposition Record gives about its own settlement: the measurements were taken in
the turn that made the repairs, so the hash did not exist while they were being written. A later
round resolves it from this file's own history.

Six of the units below were created by that round and exist at no earlier tree —
`distribution_manifest.fail`, `check_text.Content`, `check_text.Bytes`, `check_citations.prose`,
`check_citations._line_citations` and `check_citations._symbol_citations` — which is why this
section is its own rather than rows under the heading above.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| PIN-DIAGNOSTIC-UNSANITIZED | the `printable` call in `distribution_manifest.fail`, leaving the bare interpolation the module's sites used to carry | `test_validate_skills.DiagnosticExitTests.test_an_override_in_a_ref_cannot_rewrite_its_own_failure_line`, `test_validate_skills.DiagnosticExitTests.test_a_surrogate_in_a_path_is_a_diagnostic_and_not_a_traceback`, `test_validate_skills.DiagnosticExitTests.test_every_diagnostic_leaves_through_the_one_exit` | 3 |
| BYTES-THIRD-OUTCOME | the `EMPTY` branch in `check_text._bytes`, folded back into the state beside it so a file with no bytes answers as one that could not be read | `test_check_text.TextHygiene.test_a_file_with_no_bytes_is_told_apart_from_one_that_could_not_be_read` | 1 |
| TAUTOLOGICAL-SIBLING-ASSERTION | the transitive path itself, by giving `seam_contract` a direct `markdown_it` import — see the note below, because reverting the assertion reddens nothing and that is the finding | `test_module_claims.ModuleClaimTests.test_the_check_sees_a_package_reached_through_a_sibling` | 1 |

`TAUTOLOGICAL-SIBLING-ASSERTION` needs the note this ledger has carried once before, for
`QUOTE-CLOSER-BY-EXISTENCE`: a **green** control under the same condition is part of the
measurement. Reverting the repaired assertion to the expression that stood there —
`"seam_contract"` against a set the subtraction removes it from — and giving `seam_contract` a
direct `markdown_it` import leaves the suite **green**, which is what the finding says: the old
assertion could not see the condition its own test name claims to test. Both results were run. The
red one is the guard in the usual sense; the green one is why the row exists, and it is the reason
this entry names a change to the product rather than to the test. Reverting a weakened assertion
reddens nothing by construction, so a test's own strength is a thing no revert of that test can
guard.

## Repairs with no guard, and why

| Finding | Why nothing goes red |
|---|---|
| WIDTH-EXEMPT-SINGLE-TOKEN | none, and the absence is the finding. Reverting the line split leaves `ruff` green, because `E501` does not report a line whose content after the indentation holds no whitespace — which is what let the line stand. The re-runnable reading is to measure every line under `scripts/` and `tools/` and test whether the content after its indentation holds whitespace; it reports none. `2b` would have made this a guard and was weighed and not taken, with the reasoning in `docs/dispositions/v0.4.1..6ff702e.md` and the limit registered as `e501-exempts-a-whitespace-free-line` |
| CITATIONS-READS-AND-JUDGES | none, by construction — an equivalence refactor, like `INPUT-PATTERN-SPLIT` above. One body became `check_citations.prose` plus `check_citations._line_citations` and `check_citations._symbol_citations`, and the whole suite passed unchanged with no test edited, which is what a behaviour-preserving split means. What settles it is that `check_citations.citations` now hands its lines to policies rather than holding them, and that the two ledger rows naming branches which moved were re-pointed in the same change |
| FOUND-REBOUND-IN-COMPREHENSION | none — the unit is a local variable's name. No test holds one, and `ruff` holds neither shadowing of this kind nor a comprehension's choice of binding |
| GUARD-ROW-DUPLICATED | none by test — the unit is a row of this file. What a later round can re-run is a reading: grep this file for every finding id and expect exactly one row per id. It was run and reports one for each. The check that would do this without a reader is `7b` in `docs/dispositions/v0.4.1..6ff702e.md`, not taken, and a registry keyed by id is what would make a second row inexpressible rather than caught |
| CARRIED-TALLY-DISAGREES | none — the unit is a Self-check cell of `docs/dispositions/c60a6ba..af1185a.md`. The re-runnable reading is to count the ids its Carried forward table holds and compare them to the number that cell states; the cell now names both the id count and the row count, and says which the check is about |
| COUNT-OVER-RECORDS-IN-GUARDS | none — the unit is a clause in the surviving `ABSENT-CLAIM-AS-MISMATCH` row of this file, and no check decides which numbers the count rule reaches. `AGENTS.md` says so where the rule is written |
| GUARD-SWEEP-RESULT-NOT-REPRODUCIBLE | none by test, and not for want of a check but for want of one worth its cost — `8b` in `docs/dispositions/v0.4.1..6ff702e.md`, not taken. The reading is the row's own instruction, and it now states the result it produces: one non-ancestor, `9354d75`, and no other. Run again after the correction and it matches |
| TRAILING-WHITESPACE-UNSEEN | none, and the absence is the finding. `check_text._hygiene` reads every tracked file and asks whether it holds a NUL and whether it ends with a newline; neither is this, and `ruff` holds a Python line's width and not its end. So no revert can redden anything, because nothing here reads the class. The re-runnable reading is `git diff --check` over a range, or `git ls-files -z \| xargs -0 grep -lIE " +$"` over the tree, which reports none. A check was weighed and not taken, in `docs/dispositions/v0.4.1..6ec4d3b.md` |
| INTEGRITY-ROW-DUPLICATES-A-DECLARED-CHECK | none — the unit is a row of `docs/dispositions/v0.4.1..e693b19.md`, and its repair was a merge rather than a removal, so what a reading can check is that the reconciliation survived: `Coverage` there now states the Triage figure and why it is reconciled on that row. Deleting the row instead would have destroyed a correct reading, which is the part a row-count rule gives no reason to preserve |
| SELFCHECK-FOLDED-INTO-THE-INPUT-AUDIT | none by test — the units are rows of two records. The re-runnable reading is the one that found the class: take the five checks `skills/triage-findings/SKILL.md` declares and compare them to the row labels of every Record integrity table under `docs/dispositions/`. It was run after the repair and reports no extra row anywhere in the tree, which is the first time that reading has come back empty |
| TRIGGER-KEYS-ON-THE-WEAKEST-AXIS | none — the unit is a condition written in prose, in this file and in `docs/dispositions/c60a6ba..af1185a.md`. No test holds a trigger. What replaces a guard is that the condition is now decidable from a row's own cells rather than from its verdict, so a later round can apply it by reading rather than by judging |
| REVIEW-FILED-A-VIOLATION-AS-A-VERIFIED-CLAIM | none — the unit is a Claims Verified entry of `docs/reviews/v0.4.1..6ff702e.md`, and an archived Review Record is kept as received, so the repair is recorded in the settling record rather than written into the input. Nothing can hold where a review files a measurement it has already taken |
| INPUT-PATTERN-SPLIT | An equivalence refactor: two patterns for one Markdown line became one, and the answers were measured identical over the label alone, a padded label, a full contract line and a line without one. Reverting it leaves the suite green by construction, which is what an equivalence claim means. What settles it is `validate_skills.INPUT_LINE` being one pattern where there were two |
| CLOSURE-NAMES-WRONG-SYMBOL | Its guard is not a test but a gate step: `scripts/check_citations.py` refuses a citation whose symbol no module defines, which is the defect itself. It is verified by the gate being green over the records |
| ORDINAL-IN-NEW-MODULE, REGISTRY-UNDERREPORT, LEDGER-TABLE-ROUNDS, RAWSCORES-PROVISIONAL, COUNTS-IN-THE-NEW-PROSE, ROUND-ENDS-WHEN-ASKED, RECONCILED-AGAINST-A-PARTIAL-COPY | The unit is prose. No test can hold a docstring's wording, and no gate opens over one. These close on the recorded reading that settled them, which is in each round's Disposition Record |
| MODULE-MAP-REBUILT | none — the repair changed how often the tree is read, not what it answers. Its measurement is in `docs/dispositions/v0.4.1..1609403.md`: 165 parses to 66, 0.77s to 0.26s. The later 66 to 48 belongs to DOUBLE-PARSE-DISAGREES, in its own record, and this row said 48 and a wall time no record holds |
| FORMATTING-DRIFT | none — the units are an import block and two prose lines, which no test holds |
| SUBJECTS-STATED-TWICE, GUARDS-INCOMPLETE, ROUND-CLAUSE-TOO-WIDE, GUARD-NOT-A-SYMBOL | none — every unit is prose, and `GUARD-NOT-A-SYMBOL`'s repair is verified by the citation gate step reading this file |
| DOUBLE-PARSE-DISAGREES | none, and this row claimed one. It said reverting `check_citations.citable` to a second walk turns `test_check_citations.ModuleIdentity.test_an_unparseable_module_is_absent_and_reported_by_one_answer` red, measured at 2. Re-measured: both implementations answer identically on that fixture, because the walk swallowed an unparseable module exactly as the one-pass form does. The convergence's effect is the parse count and one decision point for an unreadable module, neither of which an output can show. The case is kept — it asserts that one answer covers absence and defect — but it is not this repair's guard |
| GUARD-CLAIM-UNFAITHFUL-REVERT | — the finding is that a guard row promised a red that does not happen, and its repair is that row's correction. A ledger row cannot guard a ledger row |
| LEDGER-QUOTES-WRONG-FIGURES | — the unit is a table cell |
| PARAGRAPH-NOT-REWRAPPED | — the unit is a paragraph's line breaks |
| ROW-NOT-SELF-CONTAINED | — the unit is a table cell |
| GUARDS-CLAUSE-SELF-CONTRADICTS | — the unit is a clause in `AGENTS.md` |
| REGISTRY-NOT-DERIVED | Declined, with the weighing in `development-knowns.yaml`. A declined finding has no repair to guard |
| SETTLEMENT-NAMES-AN-ORPHAN | none — the unit is a hash in a record's `Settled by` and Scope cells. What replaces a guard is the check itself, re-runnable by any round: `git cat-file -e` on every hash a record names, then `git merge-base --is-ancestor` against HEAD. Run over every record in `docs/dispositions/`, it reports **one** non-ancestor, and that hit is expected rather than a remainder: `9354d75` is named only as the pre-amend object, and the three records naming it each state its non-ancestry as the defect being reported. So the result to expect is that hash and no other, and what the row claims is that no record names an unreachable *settlement*. Stated because the row first said "none remaining", which the run does not produce — a re-runnable instruction whose expected result its own run contradicts sends the next round to judge a hit the row should have accounted for |
| LEDGER-ROW-IN-THE-WRONG-TABLE | none — the units are a schema sentence in this file and the table a row sits in. No test holds either, and no gate opens over a table's membership |
| DECLINE-NOT-RE-WEIGHED | none — the unit is the "What was declined" section below, and the repair is that the weighing is written there rather than left to a reader. Nothing can hold the presence of reasoning |
| REACH-STOPS-AT-THE-FILE | none by test, but not unguarded: `scripts/check_citations.py` reads every record under `docs/dispositions/`, so a Reach cell naming a symbol that no module defines is refused. What stays unheld is a cell naming a quoted phrase, which the check cannot resolve |
| PARAGRAPH-SPLIT-NOT-REFLOWED | none — the unit is a paragraph's line breaks in `AGENTS.md`. `ruff` holds a Python line's width and nothing holds a Markdown paragraph's |
| GUARDS-LEDGER-MISSES-THE-SETTLING-ROUND | none — the unit is which findings a settling turn reads as current, which is a turn's own conduct and not a place in the tree. The nearest re-runnable check is the one its round's Disposition Record now carries as a self-check row: grep this file for every id that record accepts, and expect each to be found. Reverting the rows below turns that reading red, which is the closest a prose unit comes to a guard |
| LIFECYCLE-OMITS-THE-NAMED-PRIOR | none — the units are the "Out of scope this round" sections and the lifecycle self-check rows of the two `v0.4.1..61789c2` records. The repair is that the self-check answers from the prior record's own tables rather than from what the record placed; no test holds where a self-check gets its list |
| ANCESTRY-STATEMENT-UNBOUND | none — the unit is a `Verified how` cell's sentence. The ancestry facts it states are re-runnable, and are the same two commands `SETTLEMENT-NAMES-AN-ORPHAN` names above; what no check holds is whether the sentence attaches each result to the right hash |
| COVERAGE-ENUMERATION-ABSENT | Declined, with the weighing in `docs/dispositions/74cd7e3..85d0569.md`. A declined finding has no repair to guard |
| FIXTURE-READ-AS-PRODUCT | Declined, with the weighing in `docs/dispositions/v0.4.1..c60a6ba.md`. The reviewed units are the deliberate defects of a micro-test fixture, and a guard against repairing them is the registry entry the fixture already has: `evidence_currency.py --check` ties the `static-review-gate5-ledger` scenario to the wording it measured, and `unaccounted_files` reports a scenario file no entry accounts for |
| REVIEW-COVERAGE-AS-FINDING | Declined, with the weighing in `docs/dispositions/v0.4.1..c60a6ba.md`. A declined finding has no repair to guard |
| ABSENT-CLAIM-AS-MISMATCH | none — the units are rows of a Record integrity table, and no test holds a table cell. Its second instance is why this row says more than that: the repair recorded for the first instance was the removal of one row, which landed and did not stop the next, so what a later round can re-run is not a revert but a reading — take the five checks `skills/triage-findings/SKILL.md` declares and compare them to the row labels of each record under `docs/dispositions/`. A record carrying a sixth is the defect. That reading is repair `1b` in `docs/dispositions/c60a6ba..af1185a.md`, and running it is what found that the class was larger than the input showed — a sixth row in records no review had opened, some of them scoring an input `mismatch`. The condition for building the check that would do this automatically is stated there, and the `v0.4.1..6ec4d3b` round restated it because it keyed on a row's Result where the defect keys on its subject: a row whose `Input claim` cell does not name a claim the input actually made about itself |

## What was declined

**Running these reverts as a gate step.** It would catch a repair losing its guard — which has
happened here: a seam test stayed green under a full revert of the change it claimed to cover,
because it drove the helper instead of the consumer. Against that: each entry would need a textual
mutation spec anchored in source that moves, so the specs would break on unrelated edits and be
maintained by hand. That is the property this range spent a round removing from citations, and
reintroducing it in a more brittle form to guard the same claims is a worse trade than running the
reverts when a round wants to close something.

**Re-weighed after the trigger fired, and the decline stands.** The evidence above was one
occurrence when it was written, and this file has since recorded three more ways a guard result went
wrong: an edit that did not apply, an edit that applied but was not the pre-repair code, and a row
whose guard never guarded at all. The trigger below names a repair *losing* its guard, and only the
first of those three is that; the other two are a claim that never held, which a gate step would not
have caught either — it would have run the same unfaithful revert and recorded the same number.
What the three do say is that the failures are in *how a revert is performed*, not in whether one is
performed on a schedule, and the preamble above is where that repair went. A reader meeting this
decline should see it was reconsidered rather than left standing.

**Reconsider when** a repair is found to have lost a guard it demonstrably had, or a mutation runner
arrives that addresses a unit rather than a span of text.
