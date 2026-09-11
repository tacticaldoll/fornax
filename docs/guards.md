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

Every finding a round accepted **from the round this file began in onward** has a row, closed ones
included, and a finding whose repair nothing can guard has a row saying so rather than no row at
all. Rounds settled before that are not covered and are not being backfilled: a row's content is an
instruction to revert a unit and expect a count, and for those repairs no count was ever recorded,
so a row written now would be a reconstruction presented as a measurement. That is the same reason
this file does not edit its own past numbers. The claim used to be unbounded and the file has never
met it — an accepted finding in an earlier round would show up as a hole with nothing marking it,
which is worse than a stated boundary. The first version held only
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

**A row state this ledger's schema did not anticipate.** Every round before `6ec4d3b..a7c40d1`
landed its repairs in the turn that wrote its record, so every row could name a revert. That round
accepted ten findings and routed their repairs onward instead, which leaves rows whose repair has
not landed: there is no unit to revert and no test to redden, and the reason is neither "the unit is
prose" nor "the repair is an equivalence". It is that the repair is planned and unbuilt. Such a row
says so, and a later round reads it as work outstanding rather than as a finding nothing can guard.

## Measured 2026-09-07, at the commit carrying this section

Each revert applied to the tree, confirmed to have landed by reading the changed line back, the
named test run, the tree restored, and the whole suite confirmed green afterwards at 448 tests. The
tree is named as the commit carrying this section for the reason the section above gives.

Every unit below was created by the `6ec4d3b..a7c40d1` round's repairs and exists at no earlier
tree, which is why this section is its own.

**One of these numbers was wrong on its first run, and the way it was wrong is the one this file's
preamble warns about.** `ESCAPE-TESTED-NOT-CONSUMED` first measured 10, from a revert that removed
escape handling altogether — which is not what the code was. The pre-repair code read escapes with
a lookbehind, which handles the common `\|` correctly and fails only where a backslash is itself
escaped. Reverting to *that* reddens 1. The instruction below names the lookbehind, not its absence.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| DECLARED-GUARDS-ONE-PAYLOAD | the reason an unread `record_shape.Declared` carries, so its accessor raises with nothing to say — which is what the two-field version did by construction | `test_record_shape.DeclaredInvariant.test_an_unread_contract_never_raises_without_saying_why` | 3 |
| RESULT-READ-BY-POSITION | `record_shape.record_defects`' use of `record_shape.Table.column`, back to reading the last cell of the row | `test_record_shape.RecordIntegrityRows.test_a_short_row_is_padded_by_the_parser_and_read_as_empty` | 1 |
| EMPTY-SCOPE-READS-AS-CLEAN | the empty-corpus diagnostic in `record_shape.check` | `test_record_shape.EmptyScope.test_a_root_with_no_records_is_a_failure_not_a_clean_answer` | 1 |
| ESCAPE-TESTED-NOT-CONSUMED | the routing of `record_shape.table` through `markdown_links.table_rows`, back to a row reader written beside its caller — **superseded**: the repair this row first named was a hand-written escape scan, which a later review refuted for eating a non-punctuation escape. The unit to revert is now the routing, and the reader it replaced is gone | `test_record_shape.RecordIntegrityRows.test_a_non_punctuation_escape_keeps_its_backslash` | 1 |

## Measured 2026-09-07, at the commit carrying this section, second round of the day

The `6ec4d3b..59d7fb1` round's repairs. Each revert applied, confirmed landed by reading the changed
line back, the named test run, the tree restored, and the whole suite confirmed green afterwards at
452 tests.

Two of these reverts are **broad**, and the ledger says so rather than letting a reader take the
number for a narrow guarantee. Both findings share one repair — routing table rows through the
parser that owns the grammar — so both share one revert, and undoing it removes several correct
readings at once because the reader it replaced was wrong in more than one way. The number is what
the instruction produces, not a measure of the finding's size.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| SELFCHECK-FLOOR-UNENFORCED | `record_shape.RequiredKeys` from what `record_shape.rules_for` returns for `THIS_RECORD` | `test_record_shape.Seats.test_a_record_omitting_a_declared_self_check_is_reported` | 2 |
| SUBJECT-DOES-NOT-PICK-THE-RULE | the `THE_INPUT` branch of `record_shape.rules_for`, so every seat falls through to one discipline | `test_record_shape.Seats.test_a_seat_judging_the_input_closes_its_key_set`, and twelve others | 13 |
| VERDICT-READ-BY-PREFIX | the `whole()` read in `record_shape.record_defects`, back to the `startswith` test it replaced | `test_record_shape.RecordIntegrityRows.test_a_value_merely_sharing_a_prefix_with_a_verdict_is_not_one`, and five others | 6 |
| ESCAPE-EATS-A-NON-PUNCTUATION-PAIR | the `table` rule on `markdown_links.PARSER` | `test_record_shape.RecordIntegrityRows.test_a_non_punctuation_escape_keeps_its_backslash`, and 18 others — the revert is broad, see above | 19 |
| TRAILING-PIPE-ASSUMED-MANDATORY | `record_shape.table`'s use of `markdown_links.table_rows`, replaced by a row reader written beside it | `test_record_shape.RecordIntegrityRows.test_a_row_with_no_trailing_pipe_keeps_every_cell`, and 13 others — broad for the same reason | 14 |
| MALFORMED-TABLE-READS-CLEAN | the no-readable-table diagnostic in `record_shape.record_defects` | `test_record_shape.RecordIntegrityRows.test_a_section_that_holds_no_readable_table_is_not_a_record_without_one` | 1 |

## Measured 2026-09-07, at the commit carrying this section, the repair round

Settled by `docs/dispositions/v0.4.1..d75d484.md` and
`docs/dispositions/7b98106..d75d484.second-reading.md`. This replaces the two prospective
sections those records were written with: every number below is one run against this tree
after all of the repairs landed, not a number carried forward from the turn that wrote the
row. Three commit messages in this round first stated a count measured at an intermediate
tree and were corrected, which is why the whole set was re-run at the end rather than
collected as it went.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| SECTION-ABSENCE-SKIPS-ITS-RULES | `record_shape.RequiredSections` from `record_shape.RECORD_RULES` | `test_record_shape.RecordCardinality` | 4 |
| DUPLICATE-SECTION-READ-AS-ONE | `record_shape.OneSectionEach` from `record_shape.RECORD_RULES` | `test_record_shape.RecordCardinality` | 1 |
| MALFORMED-TABLE-READS-CLEAN | `record_shape.ReadableTable` from `record_shape.RECORD_RULES` | `test_record_shape.RecordCardinality` | 2 |
| ARCHIVE-BOUND-TO-CURRENT-CONTRACT | the history argument in `record_shape.audit`, so every record reads the working tree | `test_record_shape.SettledContract` | 3 |
| SNAPSHOT-READS-AS-HISTORY | the historyless branch in `contract_revision.settled` | `test_record_shape.SettledContract` | 35 |
| UNJUDGED-READS-AS-CLEAN | the `unjudged` append in `record_shape.audit` | `test_record_shape.SettledContract` | 1 |
| SUBJECT-ABSENCE-READS-AS-CLEAN | the missing-subject report in `check_citations.check` | `test_check_citations.SubjectCorpus` | 1 |
| CITATION-CORPUS-EMPTY-READS-AS-CLEAN | the empty-corpus failure in `check_citations.check` | `test_check_citations.SubjectCorpus` | 1 |
| KEY-READ-BY-PREFIX | the whole read in `record_shape.UniqueFirstColumn`, restoring the prefix split | `test_record_shape.FindingKeyReadWhole` | 3 |
| DISPOSITION-DOMAIN-UNCHECKED | `record_shape.ValueReadWhole` from the findings seat in `record_shape.rules_for` | `test_record_shape.FindingsDomain` | 3 |
| DOMAIN-SHARED-ACROSS-SEATS | the per-column derivation in `record_shape._domains` | `test_record_shape.FindingsDomain` | 30 |
| MISSING-RESULT-COLUMN-YIELDS-A-DOMAIN | the unread-contract branch in `record_shape.shape_of` | `test_record_shape.ContractWithoutAVerdictColumn` | 1 |
| RULE-ANNOTATED-SHAPE-GETS-DECLARED | `record_shape.Declared.shape` at the call in `record_shape.record_defects`, handing over the outer type | `test_record_shape.FindingsDomain` | 39 |
| ROW-SKIP-NOT-ASKED-OF-THE-WIRING | the `closed` condition in `record_shape.ValueReadWhole` | `test_record_shape.FindingsDomain` | 3 |
| SHELL-COMMENT-RULE-NARROWER-THAN-CLAIMED | the operator lookbehind in `read_whole.COMMENT` | `test_read_whole.CommentRule` | 3 |

**This row cannot be run any more, and the finding it guarded is closed.** Its revert names an
operator lookbehind that no longer exists: `read_whole.COMMENT` was narrowed when the shell stopped
sharing it, and its guard `test_read_whole.CommentRule` stopped reaching the pattern at all when
that call was severed — both symbols staying in place, so the citation gate had nothing to refuse.
The reading of 3 stands as written, being true of the tree this heading names. What replaces it is
the row under "the severed-guard repair", where the subject is reached directly and the revert is
to put the retired form back.

The row went quiet for two rounds before anyone ran it, which is the finding
GUARD-DIED-WITH-ITS-ONLY-CALLER. A rename is refused by a check; a guard that stops reaching its
subject is refused by nothing, and re-measuring the rows a repair's Reach touches is the discipline
that catches it. That discipline missed this row twice, because the repairs that killed it named
`read_whole.shell_words` while the row names `read_whole.COMMENT` — which is why the repair routed
for it keys rows by the symbols their instructions name rather than by what an author recalls.

Five findings this round accepted have no revert, and each is a row below rather than an
omission: the prose ones, and the two the round chose to register rather than repair.

## Measured 2026-09-11, at the commit carrying this section

The rows the round settled in `docs/dispositions/v0.4.1..e144212.md` wrote prospectively, now
measured. Each revert was applied to the tree, the whole suite run, the tree restored, and the
suite confirmed green again afterwards. The tree is named as the commit carrying this section
rather than by hash, for the reason the earlier sections give: the measurements were taken in the
turn that made them, so the hash did not exist while they were being written.

Two corrections to what those rows said, disclosed here rather than left to be discovered. The
prospective row called the escaped-hash control an existing case in `test_read_whole.CommentRule`.
No such case existed; it is written in this round, in `test_read_whole.ShellWordTests`, alongside a
second control for adjacent quoting. Correcting where a guard lives is correcting the row's label
rather than one of its readings, which `AGENTS.md` admits — the readings below were taken after the
correction and report what actually ran. The row also offered a choice of repairs, and 1a is the
one taken, so the revert names it alone.

The two counts are not the same kind of two. The shell revert reddens one named test that carries a
subtest per quote character; the record revert reddens two named tests.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| QUOTED-HASH-CUT-BEFORE-THE-LEXER | the quote-preserving scan in `read_whole.shell_words`, restoring the pre-lexer split on `read_whole.COMMENT` that `a1e8c11` left | `test_read_whole.ShellWordTests.test_a_hash_inside_quotes_is_not_a_comment` | 2 |
| RECORD-RULES-IGNORE-THE-DECLARED-SHAPE | the declared-seat gate in `record_shape.record_defects`, so every rule is handed every seat again | `test_record_shape.UndeclaredSeatIsNotJudged.test_a_duplicated_undeclared_section_is_not_reported`, `test_record_shape.UndeclaredSeatIsNotJudged.test_an_unreadable_table_under_an_undeclared_section_is_not_reported` | 2 |

The design of the shell repair is held by two further controls, which are not guards for a finding
and so are not rows here. Each is reddened by a wrong repair rather than by reverting the right
one, and each was measured the same way:
`test_read_whole.ShellWordTests.test_an_escaped_hash_is_declined_rather_than_guessed` reddens when the
cut is made on the lexer's output, because posix `shlex` unescapes and an escaped hash arrives as
the token a comment would; and
`test_read_whole.ShellWordTests.test_adjacent_quotes_are_one_word` reddens when the words are
rebuilt by rejoining the scan's tokens instead of slicing the text.

## Measured 2026-09-11, at the commit carrying this section, the recurrence repair

`QUOTED-HASH-CUT-BEFORE-THE-LEXER` returned after its first repair landed in full, so this is the
same finding measured a second time against a second repair. Both halves were reverted separately
and each reddens only its own case, which is what makes them two repairs rather than one.

This section also exists because of how its rows were checked. Before writing them, every row
elsewhere in this file whose named unit or named guard lay inside this repair's Reach was re-run
against the tree — the discipline `docs/dispositions/e144212..05025bc.md` proposes as repair 2c,
performed by hand here rather than asserted, so that proposing it as a rule rests on having paid
its cost once. It found drift immediately, disclosed below, and it found it in the same turn that
caused it rather than a round later.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| QUOTED-HASH-CUT-BEFORE-THE-LEXER | the `start == 0 or gap or operator` condition in `read_whole.shell_words` and nothing else, leaving the `startswith` test it guarded | `test_read_whole.ShellWordTests.test_a_hash_after_a_closing_quote_stays_in_its_word` | 1 |
| QUOTED-HASH-CUT-BEFORE-THE-LEXER | the escaped-separator refusal in `read_whole.shell_words`, so a token ending in a backslash no longer stops the reading | `test_read_whole.ShellWordTests.test_a_hash_after_an_escaped_separator_keeps_its_word` | 1 |

**Which revert was measured.** The instruction above named "the begins-a-word test", which two
readers undo differently: removing the condition alone reddens one case, and removing the whole
block back to what the tree held before reddens two. The reading measured was the first, and the
cell now names the condition rather than the test, so one reading is available. A row is an
instruction a later round runs, and an instruction with two answers is not one.

**Superseded by the round below.** The two reverts these rows name no longer exist: the
begins-a-word test and the escaped-separator refusal were both deleted when the question they
answered was declined instead. The readings stand as written, each true of the tree named in the
heading, and the guards they name have been re-pointed to the cases that now carry the same
subjects — a label correction, the readings themselves untouched. One of those subjects inverted
with the repair: an escaped separator before a hash is now read rather than refused, so the case
asserting the refusal became a case asserting the word survives.

**What the re-run found.** The row for this same finding under the earlier heading records 2 red for
reverting the quote-preserving scan. Against this tree that revert reddens 3, because the
escaped-separator case added here is reddened by it too. The earlier reading is left as written: it
reports what was true at the tree it names, and editing it would falsify a measurement rather than
correct a label. What is recorded is that the number no longer describes the current tree, which is
the thing a later round needed and would not otherwise have been told.

The re-run also confirmed that `SHELL-COMMENT-RULE-NARROWER-THAN-CLAIMED` still reddens nothing —
`GUARD-DIED-WITH-ITS-ONLY-CALLER` is open and unrepaired, and this repair does not touch it.

## Measured 2026-09-11, at the commit carrying this section, the test-collection repair

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| DIRECT-RUN-SKIPS-A-CLASS | the moved entry-point block in `scripts/tests/test_read_whole.py`, put back above the last class | `test_module_claims.EntryPointPlacement.test_every_test_module_places_its_entry_point_last` | 1 |

The revert reproduces the defect as well as reddening the guard: with the block back above the
last class, a direct run of that module collects fifteen tests where discovery collects eighteen.
Three modules had the shape and all three are moved; the other seventeen already placed the block
last, so the repair follows a convention the tree already held rather than introducing one.

The guard is scoped to test modules because theirs is the silent case — a script whose entry point
calls something defined below it raises where anyone can see. It carries the third answer as well:
a module with no entry point at all is not misplaced, which is most of this tree.

Re-run under the same discipline as the section above, across the rows whose named unit or guard
this repair's Reach touched. Both rows for `QUOTED-HASH-CUT-BEFORE-THE-LEXER` still redden 1 each,
so moving the block changed no count. Recording a re-run that found nothing, because a discipline
only reported when it fires reads as though it always fires.

The other two findings settled in the same round and repaired alongside this one —
`LEDGER-NAMES-A-SELECTION-THE-CONFIG-DOES-NOT-HOLD` and `STATEMENT-OVERRUN-BY-ITS-EVIDENCE` — can
have no guard and keep their rows in the section below.

## Measured 2026-09-11, at the commit carrying this section, the severed-guard repair

`read_whole.COMMENT` had no coverage of its own. `test_read_whole.CommentRule` reached it only
through `shell_words`, and when that call went the coverage went with it while both symbols stayed
in place, so the citation check saw nothing and the row below kept instructing a later round to run
a revert that reddened nothing.

The repair gives the pattern its own class and retires the operator form the shell needed. Nothing
here exercised that form; pip owns the requirements-file comment and is not installed, so its
correctness cannot be settled, and an unexercised rule that cannot be checked was removed rather
than guarded. `development-knowns.yaml` records the absent owner.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| GUARD-DIED-WITH-ITS-ONLY-CALLER | the operator form's removal from `read_whole.COMMENT`, putting the lookbehind back | `test_read_whole.RequirementsComment.test_a_hash_after_a_marker_separator_is_not_a_comment` | 1 |

**Re-pointing the row this finding is about.** `SHELL-COMMENT-RULE-NARROWER-THAN-CLAIMED` recorded 3
red for reverting the operator lookbehind. Re-run across the three trees it has seen: 3 at the tree
it was measured on, 0 once `shell_words` stopped calling the pattern, and 1 now. The instruction has
also inverted — the operator form is retired, so the revert is to put it back rather than to take it
away — and the test it reddens is the new alternate-spelling control rather than the old class. Its
earlier readings stand as written, each true of the tree it names; this row is where the current
one lives.

Re-run under the same discipline as the sections above. Both rows for
`QUOTED-HASH-CUT-BEFORE-THE-LEXER` still redden 1, and `DIRECT-RUN-SKIPS-A-CLASS` still reddens 1,
so this repair moved no count but its own.

## Measured 2026-09-11, at the commit carrying this section, declining the question

The repair the three rounds before did not make. `read_whole.shell_words` no longer locates where
the shell's comment begins; it declines the question, which has no owner installable here. Two
answers survive because neither needs a grammar: a hash at the first non-blank character is a
comment whole, nothing before it being able to quote it, and a hash inside a word is not a comment.
Everything between leaves the command unread.

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| QUOTED-HASH-CUT-BEFORE-THE-LEXER | the hash-word refusal in `read_whole.shell_words` | `test_read_whole.CommentRule.test_a_hash_that_could_open_a_word_leaves_the_command_unread`, `test_read_whole.ShellWordTests.test_a_comment_is_declined_rather_than_located`, `test_read_whole.ShellWordTests.test_an_escaped_hash_is_declined_rather_than_guessed` | 7 |
| QUOTED-HASH-CUT-BEFORE-THE-LEXER | the whole-line-comment answer in `read_whole.shell_words` | `test_read_whole.CommentRule.test_a_command_opening_with_a_hash_is_refused_and_never_arrives`, `test_read_whole.ShellWordTests.test_a_comment_is_declined_rather_than_located` | 2 |

SHELL-WORDS-CLAIMS-A-REFUSAL-IT-DOES-NOT-MAKE and OPERATOR-BRANCH-UNCONTROLLED are closed by this
repair rather than guarded: the first was a docstring promising a refusal the code did not make and
the code now makes it, the second named a branch that no longer exists. Neither has a row, because a
revert would have to restore the branch to have anything to redden.

**What it costs, in the forms it actually takes.** Three commands this could read before are now
refused: an inline comment; an escaped hash, which posix `shlex` unescapes into the token a comment
would produce; and a hash the author quoted, because the predicate reads words after quote removal,
where the quoting that would settle it is already gone. The third was omitted when this section was
written and is the one whose advice did not follow — `echo "### building"` is refused and has no
comment to move — so the diagnostic now names both ways out. Nothing in this repository carries any
of the three, and the workflow this actually reads still yields its commands with none refused.

**What it buys, measured.** Against bash over the same constructed set the previous rounds used, the
shortfall class is empty: no command is read as a shorter well-formed word list. The residual
divergences are substitution constructs where this returns *more* words than bash, which cannot
hide a pin and fail loudly at `packaging` instead.

## Measured 2026-09-11, at the commit carrying this section, the entry-point check

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| ENTRY-POINT-CHECK-READS-ONE-SPELLING | the structural match in `test_module_claims.main_guard`, restoring the comparison of unparsed text against one literal | `test_module_claims.EntryPointPlacement.test_the_check_sees_the_guard_written_the_other_way_round` | 1 |
| ENTRY-POINT-CHECK-BOUND-UNDECLARED | the workspace-wide set in `test_module_claims.test_modules`, restoring a glob on one directory | `test_module_claims.EntryPointPlacement.test_the_set_reaches_every_tests_directory_the_workspace_holds` | 1 |

The set comes from `workspace_files` now rather than from a glob, so the bound is git's and not a
directory named here; the suite it used to miss is the CLI one, which is the suite `AGENTS.md`
already treats specially and therefore exactly the exclusion that would have needed stating.

MESSAGE-NUMBERS-IN-A-DOCSTRING, WORD-SPELLED-TREE-TOTAL and ENTRY-POINT-CLASS-OVERCLAIMS are
repaired in the same docstrings and have no guard: nothing reads a docstring's figures against the
tree, counts what a comment says "most" of, or tests a class docstring against what its check
decides. Their rows are in the no-guard table, and the measurement the figures reported now lives
under its own dated heading here, where it is quotable with the tree it names.

## Measured 2026-09-11, at the commit carrying this section, the mislabelled control

| Finding | Revert this | Guard | Red on revert |
|---|---|---|---|
| CONTROL-MISLABELLED | the whitespace class in `read_whole.COMMENT`, narrowed to a literal space | `test_read_whole.RequirementsComment.test_a_hash_after_a_tab_begins_a_comment` | 1 |

The finding was a label — a second near-miss called an alternate spelling — and the label was
load-bearing, because calling it that left the accepted side of the rule with no control at all.
The pattern admits any whitespace and only a space was ever exercised, so narrowing the class to a
space passed the whole suite. It reddens now.

## Written 2026-09-11, prospective — the 48ce457 round, nothing measured

The round settled in `docs/dispositions/ebf16c7..48ce457.md` accepted fourteen findings and
repaired none. Four can carry a guard once their repair lands; the rest are prose, a commit message
that cannot be edited, or a rename whose only signal is the citation gate.

| Finding | Revert this, once its repair lands | Guard | Red on revert |
|---|---|---|---|
| PIN-HIDDEN-BEHIND-A-JOINED-COMMENT | for 1a, the comment test in `runtime_contract.run_commands` that stops a join at the newline | a case handing the joined comment-and-install block to `runtime_contract.workflow_pins` and asserting the pin is reported or the text refused, never both absent | not measured — no repair has landed |
| WHOLE-LINE-ANSWER-APPLIED-TO-A-TEXT | for 1b, the newline refusal in `read_whole.shell_words` | a case asserting that a leading comment followed by a command on the next line is not answered as an empty word list | not measured |
| WHOLE-LINE-PREDICATE-UNCONTROLLED | the same, this being the control the predicate never had on the axis where it fails | the same case | not measured |
| REFUSAL-CASES-ASSERT-ONLY-A-TYPE | the pinned text and reason added to the two cases | the cases themselves — one currently stays green when the rule it names is deleted, which is what pinning the reason fixes | not measured |
| HELPER-NAMED-AS-A-TEST-CASE | the rename in `scripts/tests/test_module_claims.py` | none by test; `scripts/check_citations.py` refuses the old name wherever a record or a row still cites it, which is the only signal a rename has here | not measured |

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
| SELFCHECK-FOLDED-INTO-THE-INPUT-AUDIT | none by test — the units are rows of two records. The re-runnable reading is the one that found the class: take the checks `skills/triage-findings/SKILL.md` declares and compare them to the row labels of every Record integrity table under `docs/dispositions/`. It was run after the repair and reports no extra row anywhere in the tree, which is the first time that reading has come back empty |
| TRIGGER-KEYS-ON-THE-WEAKEST-AXIS | none — the unit is a condition written in prose, in this file and in `docs/dispositions/c60a6ba..af1185a.md`. No test holds a trigger. What replaces a guard is that the condition is now decidable from a row's own cells rather than from its verdict, so a later round can apply it by reading rather than by judging |
| REVIEW-FILED-A-VIOLATION-AS-A-VERIFIED-CLAIM | none — the unit is a Claims Verified entry of `docs/reviews/v0.4.1..6ff702e.md`, and an archived Review Record is kept as received, so the repair is recorded in the settling record rather than written into the input. Nothing can hold where a review files a measurement it has already taken |
| INVARIANT-SPELLED-TWO-WAYS | none, by construction — an equivalence. Reverting only the spelling of `record_shape.Declared`'s guard leaves the suite green, measured, which is what an equivalence claim means. What settles it is that no hand-written form of the predicate remains anywhere: `outcome.paired` is the only one, and reverting *it* to a no-op turns 8 red |
| TABLE-BODY-HAS-NO-NAME | none — the repair is that `record_shape.Table` names the header and the body apart, and no test holds whether a concept has a name. Its consequence is guarded under `RESULT-READ-BY-POSITION`, which is the defect the missing name produced |
| TEST-ROOT-BY-CWD | none — the unit is the suite's own root resolution, and reverting a test's resolution reddens nothing when the run starts at the repository root, which is where the gate starts it. The re-runnable measurement is to run `test_record_shape` from another working directory: it failed before and passes now |
| NO-OP-COMPREHENSION | none — the unit is an expression computing the value a shorter one computes. Its line moved into the table reader's rewrite and then out of the tree with it, when the reader was replaced by `markdown_links.table_rows` |
| SORT-TO-COUNT | none — the unit is a sort taken for a length in `record_shape.main`. No test holds how a count is obtained |
| PROSE-WIDTH-UNENFORCED | none, and the absence is half the finding. Nothing measures a Markdown line's width, so no revert of the reflow can redden anything — the same shape as `WIDTH-EXEMPT-SINGLE-TOKEN`, one language over, and now registered with it under `e501-exempts-a-whitespace-free-line`. The reading is to measure the non-table lines of the two records cause 6 names |
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
| ABSENT-CLAIM-AS-MISMATCH | none — the units are rows of a Record integrity table, and no test holds a table cell. Its second instance is why this row says more than that: the repair recorded for the first instance was the removal of one row, which landed and did not stop the next, so what a later round can re-run is not a revert but a reading — take the checks `skills/triage-findings/SKILL.md` declares and compare them to the row labels of each record under `docs/dispositions/`. A record carrying a sixth is the defect. That reading is repair `1b` in `docs/dispositions/c60a6ba..af1185a.md`, and running it is what found that the class was larger than the input showed — a sixth row in records no review had opened, some of them scoring an input `mismatch`. The condition for building the check that would do this automatically is stated there, and the `v0.4.1..6ec4d3b` round restated it because it keyed on a row's Result where the defect keys on its subject: a row whose `Input claim` cell does not name a claim the input actually made about itself |
| TREE-COUNT-IN-NEW-PROSE | none by test — the units are sentences in `record_shape`'s docstrings and in this file, and no check decides which numbers the count rule reaches. The reading is to grep the modules this range added for a number standing beside a noun naming a tree artifact, then check each against the derived source it transcribes. It was run and the docstring's own tally was one high |
| UNDECLARED-LABEL-TALLY-WRONG | none by test — the unit is one sentence of `record_shape.Subject`, now carrying no number. The reading that found it: collect the first-column labels of every Self-check table under `docs/dispositions/`, subtract what the contract declares, and compare the remainder against the sentence. The number was measured before the same commit's own label edit removed one, so it was false by the end of the commit that wrote it |
| COMMENT-OUTLIVED-ITS-CODE | none — the unit was a comment. Reverting its deletion leaves every gate green, because nothing reads a comment's relevance to the code beneath it. The reading is to grep `scripts/record_shape.py` for the phrase and confirm the module performs no such split |
| NOQA-CLAIM-REFUTED | none — the unit is a comment in `ruff.toml`, and the two directives it denied are well formed, so neither suppression rule fires on them. The reading is to grep the linted tree for the directive and compare what is there against what the comment claims |
| AGENTS-POINTS-AT-THE-WRONG-SYMBOL | none — the unit is one sentence of `AGENTS.md`, and the citation gate cannot reach it because the constant it named does exist and merely held something else. The reading is to compare that sentence against `check_citations.SUBJECTS` and `check_citations.RECORDS` |
| SHIPPED-SKILL-NAMES-A-PRIVATE-SYMBOL | none — the unit is prose in a shipped skill. The reading is to grep `skills/` for a dotted name resolving into `scripts/`; it returned one, naming `evidence_currency.resolved_inside`, and returns none now |
| SHIPPED-SKILL-CITATION-UNVERIFIED | none, and not repaired — registered as `shipped-skill-prose-not-citation-checked`. Adding `skills/` to the subject set was measured and reports two findings, both false, so buying the check costs the exemptions `AGENTS.md` refuses. What closed the real instance was the row above |
| LABEL-EDIT-RULE-UNWRITTEN | none — the unit is a clause that was absent from `AGENTS.md`, and no check decides which record edits are permitted. The reading is to grep `AGENTS.md` for the label-versus-answer distinction; it returned nothing before this round and the reasoning sat inside the record it authorised editing |
| REVERT-CLAIM-NAMES-A-SHAPE | none by test, and the absence is half the finding — the unit is commit prose, which is history and not editable. What replaces a guard is this row: delete the two subject branches of `record_shape.rules_for`, so every seat falls through to the findings rules, and the suite reports 31 red. Stated as the deletion rather than as "the branch that lets the subject pick", because writing this row is where that difference stopped being theoretical — the first draft of it said 3, which is what a different mutation of the same function produces. The claim it corrects named "the branch that lets the subject pick at all", which two readers mutate differently — four sibling measurements in the same commit named a unit and each reproduced exactly, and this one did not |
| GUARDS-LEDGER-INCOMPLETE | none — the unit is this file's opening claim, which is bounded now rather than unbounded. The reading is to collect every accepted `Dispositions` id from the rounds this file covers and check each against the row keys here; earlier rounds are stated as out of scope rather than left as unmarked holes |
| UNJUDGED-LOCAL-ANNOTATION-WRONG | none, and the absence is the point of repair 3b. The unit is a local annotation in `record_shape.audit`, and no gate step reads an annotation — `requirements-maintenance.txt` pins no type checker, and `ruff` is selected to `E`, `F` and `W` plus rules about the suppression mechanism itself, none of which compares an annotation against what is assigned. The re-runnable reading is to compare that local against the field it fills on `record_shape.Audit`. The repair has landed and nothing went red for it, which is what this row said would happen. The same class was swept by comparing every local list annotation in the tree against what is appended to it; two other sites flag on the shape of the call and neither is one |
| MATCHER-ENUMERATION-BLIND-TO-NON-REGEX | none — the unit is the `verification` field of `development-knowns.yaml` `shell-command-structure-read-by-hand`, and no check reads a registry entry's prose for whether the command it offers finds what it claims. The re-runnable reading is to run that field's own command and compare what it returns against the grammar decisions the tree actually makes. Widening the spellings was tried and the finding returned, because the gap is not the list's width: the field now says there is no command that enumerates this subject, offers the search as a starting set, and names the forms it cannot reach — a membership test inside a character loop, a slice on a scanned position, a comparison on a token a lexer handed back. `distribution_manifest.install_refs` is named as the instance that proves it, bounding a ref with a character loop and appearing in the search's output only because an unrelated compiled pattern sits in the same function. Which hits bound a borrowed grammar rather than merely read a string stays a reader's judgement and nothing checks it. Repair 3b would make this a guard and was declined once already, inside the same entry |
| LEDGER-NAMES-A-SELECTION-THE-CONFIG-DOES-NOT-HOLD | none — the unit is a row in this file, and nothing compares a row's prose against the configuration it describes. The re-runnable reading is to read `select` in `ruff.toml` and compare it against what the row says is selected. It was short by the rules about the suppression mechanism; the repair, landed, takes `ruff.toml`'s own wording rather than a corrected count, so the row cannot go stale against a selection it no longer spells out |
| STATEMENT-OVERRUN-BY-ITS-EVIDENCE | none — the unit is the `statement` field of the same registry entry, and no check tests a statement against the evidence listed under it. The re-runnable reading is to read each evidence item and ask whether it names a hand-written bounding the statement omits; `distribution_manifest.install_refs` is one |
| SHELL-WORDS-CLAIMS-A-REFUSAL-IT-DOES-NOT-MAKE | none — the unit is a docstring sentence, and nothing tests prose against the code beneath it. The re-runnable reading is to take the sentence "Where that question cannot be answered the command is refused" and find an unanswerable case: an escaped separator two tokens back is one, and it is read short |
| PROSPECTIVE-SECTION-SPLICED | none — the unit is a paragraph in this file. The re-runnable reading is to measure every prose line here against the width the rest of the file holds, and to check that a section promising rows has them; this section has neither |
| MESSAGE-NUMBERS-IN-A-DOCSTRING | none, and the repair has landed — the unit is a docstring, and nothing compares its figures against the tree. The re-runnable reading is to collect every number in an undated docstring and measure it; the transcribed pair was true at the tree the message described and is not at this one |
| WORD-SPELLED-TREE-TOTAL | none, and the repair has landed — the hygiene rule that forbids this is a judgement and nothing checks it. The re-runnable reading is to count the test modules carrying an entry-point block and compare that against the comment, which says most have none |
| REVERT-INSTRUCTION-AMBIGUOUS | none — the unit is a row in this file, and nothing checks that a row admits one reading. The re-runnable reading is to perform each reading its wording allows and compare the answers; two readings give two numbers, neither of them the one recorded |
| ENTRY-POINT-CLASS-OVERCLAIMS | none, and the repair has landed — the unit is a class docstring. The re-runnable reading is to construct the shape the check reports and ask whether anything is uncollected: a block followed by a module-level constant is reported and loses nothing |
| COMMENTRULE-CITES-A-REMOVED-WORDING | none — the citation gate refuses a symbol that no longer resolves and does not read a quoted wording. The re-runnable reading is to search `development-knowns.yaml` for the phrase the docstring attributes to it; this range removed it |
| GOVERNANCE-MISSTATED-AS-A-PROHIBITION | none — nothing tests durable prose against `AGENTS.md`. The re-runnable reading is to take each sentence claiming this repository forbids something and find the clause; the clause here permits a hand-written matcher whose grammar and absent owner are registered, which is what the entry carrying the misstatement does |
| REGISTERED-GRAMMAR-SILENTLY-DELETED | none — no check notices an evidence item leaving a registry entry. The re-runnable reading is to list the hand-read grammars the tree holds and check each against the entries; `distribution_manifest.install_refs` bounds a git-ref and pip-URL grammar and no entry now registers it |
| ORPHANED-REFERENCES-INTO-THE-ENTRY | none — a reference into a registry entry names prose, not a symbol, so the citation gate cannot see it. The re-runnable reading is to follow every "this entry's own evidence" reference to the item it means; two reach nothing |
| COST-ENUMERATION-SHORT-BY-A-FORM | none — the unit is a docstring sentence. The re-runnable reading is to take each form the prose says is refused, and each it does not mention, and run them; a word whose hash is quoted is refused and unmentioned |
| DIAGNOSTIC-ADVICE-MISFITS | none — nothing tests whether advice fits the case that triggered it. The re-runnable reading is to trigger each refusal and ask whether the advice applies; moving a comment to its own line does nothing for `echo "### building"` |
| MEASUREMENT-POINTER-WRONG | none — the citation gate resolves a symbol, not a claim that a file holds a reading. The re-runnable reading is to open the file a pointer names and search for the measurement; it is in a Disposition Record instead |
| COMMENT-STATES-TWO-RULES | none — nothing compares two sentences about one pattern. The re-runnable reading is to take each stated rule and test the pattern against it; this range's own control refutes the older one |
| TREE-MEASUREMENT-IN-A-MESSAGE | none, and none possible — the unit is commit prose, which is history and not editable. What closes it is the next message not carrying a measurement of the tree. The re-runnable reading is to read the range's messages for a number that describes the tree rather than the commit |

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
