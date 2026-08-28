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
| CHECKER-ERROR-STATES | the reason branch in `check_citations.citations` | `test_check_citations.ModuleIdentity.test_a_module_that_cannot_be_parsed_is_reported_as_that` | 2 |
| CHECKER-STEM-COLLISION | the collisions `check_citations.check` reports | `test_check_citations.ModuleIdentity.test_a_stem_naming_more_than_one_module_is_reported_once` | 1 |
| EXTENSION-RULE-TOO-NARROW | `check_citations.LINE_CITATION`, capped back to six letters | `test_check_citations.LineCitations.test_a_long_extension_is_still_a_line_citation` | 2 |
| DIAGNOSTIC-COMPOSES-A-PATH | the module path in `check_citations.citations`, composed instead of taken from the map | `test_check_citations.ModuleIdentity.test_an_unparseable_module_is_named_where_it_actually_sits` | 1 |
| CITABLE-SET-ASKS-THE-ENVIRONMENT | `check_citations.citable`, given a name nothing here imports | `test_check_citations.SymbolCitations.test_a_third_party_module_nothing_here_imports_is_reported` | 1 |
| IMPORTS-OUTSIDE-THE-INVARIANT | the raising accessor on `check_citations.Symbols`, so `imports` answers a reason-carrying value | `test_check_citations.ModuleIdentity.test_a_symbols_holding_a_reason_answers_neither_question` | 1 |
| SNAPSHOT-NEEDS-A-WORKTREE | the filesystem fallback in `distribution_manifest.install_documents` | `test_validate_skills.ProjectedDescriptionTests.test_a_non_worktree_validates_from_the_filesystem`, `test_validate_skills.ProjectedDescriptionTests.test_a_non_worktree_still_reports_a_stale_pin` | 2 |
| FINGERPRINT-COLLAPSED-NONE | the reasons in `evidence_currency.fingerprint` | `test_evidence_currency.DriftTests.test_each_way_a_fingerprint_fails_says_which_one` | 1 |
| UNRESOLVABLE-SAYS-NOTHING | the `OUTSIDE` branch in `evidence_currency.fingerprint`, folded back together with the one below it | `test_evidence_currency.DriftTests.test_an_unresolvable_path_says_what_stopped_it` | 2 |

## Repairs with no guard, and why

| Finding | Why nothing goes red |
|---|---|
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
