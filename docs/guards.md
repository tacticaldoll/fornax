# Repair guards

What must go red when a repair in the `v0.4.1` range is reverted, so a later round can retire the
finding by running something rather than by re-deriving the story from commit messages.

This file exists because findings sat in `Carried forward` round after round with no path out. Their
repairs were measured when they landed — a revert, a red test, a count in a commit message — and none
of that is re-runnable by a reader. What a round needed in order to close one was the evidence, and
the evidence was in prose nobody could execute.

Each entry names the unit to revert and the test that must fail, both as symbols. Nothing here names
a line: `scripts/check_citations.py` resolves every symbol below, so an entry whose unit or guard is
renamed away is loud rather than quietly wrong.

**A finding closes on this ledger the way it closes on an input's explicit verification** — the
closure test in `skills/triage-findings/SKILL.md` accepts a verified repair in place of a
gate-reviewed unit, and a probe a round can re-run is a stronger verification than a reading of one.
What that does not claim is a gate: no gate has opened over most of these units, and this ledger says
what was measured rather than what was inspected.

## Measured 2026-08-27

Each revert applied to the tree at `1abbb01`, the named test file run, the tree restored, and the
whole suite confirmed green afterwards. Every revert's edit was confirmed to have landed before its
result was read — an earlier probe in this range reported no failures because its edit had not
applied, and the number was nearly recorded.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| REF-FRAGMENT-CLOSES-QUOTE | the closing-quote check in `distribution_manifest.install_refs` | `test_validate_skills.ProjectedDescriptionTests.test_an_opening_quote_nothing_closes_leaves_the_ref_unread`, `test_validate_skills.ProjectedDescriptionTests.test_a_quoted_ref_ends_at_its_quote_and_nowhere_else` | 4 |
| VERDICT-SEAM | the publisher comparison folded into `validate_skills.validate_skill`, by printing its `OK` line before the sidecar block | `test_validate_skills.EntryPointTests.test_a_mismatched_sidecar_publisher_fails_the_entry_point` | 1 |
| VERDICT-CONTROL | the same fold; this finding is the assertion that the `OK` line is absent | the `assertNotIn` inside the test above | 1 |
| FENCE-HANDREAD | `seam_contract.elements`' use of `markdown_links.marked_code_blocks`, replaced by a hand-written fence pattern | `test_seam_contract.TemplateHeadingTests.test_a_four_backtick_template_keeps_a_three_backtick_example_inside_it`, `test_seam_contract.TemplateHeadingTests.test_a_tilde_fenced_template_is_the_output_template`, `test_seam_contract.TemplateHeadingTests.test_a_template_fenced_as_another_language_is_reported` | 3 |
| BINARY-AS-TEXT | the suffix narrowing removed from `check_text._hygiene`, restored | `test_check_text.TextHygiene.test_any_tracked_file_holding_a_nul_is_reported_not_skipped` | 4 |

## Repairs with no guard, and why

| Finding | Why nothing goes red |
|---|---|
| INPUT-PATTERN-SPLIT | An equivalence refactor: two patterns for one Markdown line became one, and the answers were measured identical over the label alone, a padded label, a full contract line and a line without one. Reverting it leaves the suite green by construction, which is what an equivalence claim means. What settles it is `validate_skills.INPUT_LINE` being one pattern where there were two |
| CLOSURE-NAMES-WRONG-SYMBOL | Its guard is not a test but a gate step: `scripts/check_citations.py` refuses a citation whose symbol no module defines, which is the defect itself. It is verified by the gate being green over the records |
| ORDINAL-IN-NEW-MODULE, REGISTRY-UNDERREPORT, LEDGER-TABLE-ROUNDS, RAWSCORES-PROVISIONAL | The unit is prose. No test can hold a docstring's wording, and no gate opens over one. These close on the recorded reading that settled them, which is in each round's Disposition Record |
| REGISTRY-NOT-DERIVED | Declined, with the weighing in `development-knowns.yaml`. A declined finding has no repair to guard |

## What was declined

**Running these reverts as a gate step.** It would catch a repair losing its guard — which has
happened here: a seam test stayed green under a full revert of the change it claimed to cover,
because it drove the helper instead of the consumer. Against that: each entry would need a textual
mutation spec anchored in source that moves, so the specs would break on unrelated edits and be
maintained by hand. That is the property this range spent a round removing from citations, and
reintroducing it in a more brittle form to guard the same claims is a worse trade than running the
reverts when a round wants to close something.

**Reconsider when** a repair is found to have lost its guard, or a mutation runner arrives that
addresses a unit rather than a span of text.
