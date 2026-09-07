"""Cover each constraint, and the reading that derives them from the contract."""

from __future__ import annotations

import subprocess
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import record_shape
from markdown_links import heading_section, marked_code_blocks, table_rows

TEMPLATE = """# Triage

### Phase 5: Produce the Disposition Record

<!-- OUTPUT-TEMPLATE: disposition-record@1 text/markdown -->
```markdown
## Disposition Record

### Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | the gate named | its status | pass \\| mismatch \\| not claimed |
| Coverage | stated scope | four enumerated sets | pass \\| mismatch \\| not claimed |

### Dispositions

| Finding | Cause | Disposition |
|---|---|---|
| id | # | accept |

### Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass |
| Every accepted cause carries at least one repair with an enumerated Reach | pass |
```
"""

RECORD = """# Disposition Record — `a..b`

## Record integrity

| Check | Input claim | Reconciled evidence | Result |
|---|---|---|---|
| Verdict / Gate Index | PASS | the gate index agrees | pass |
{extra}
## Dispositions

| Finding | Cause | Carried | Disposition | Reason |
|---|---|---|---|---|
{rows}
## Self-check

| Check | This record's answer |
|---|---|
| Every prior id sits in exactly one exclusive lifecycle home | pass |
| Every accepted cause carries at least one repair with an enumerated Reach | pass |
"""


ONE_ROW = "| ONE — a thing | 1 | new | accept | — |"


def tree(extra: str = "", rows: str = ONE_ROW) -> TemporaryDirectory:
    holder = TemporaryDirectory()
    root = Path(holder.name)
    (root / "skills" / "triage-findings").mkdir(parents=True)
    (root / "skills" / "triage-findings" / "SKILL.md").write_text(TEMPLATE, encoding="utf-8")
    (root / "docs" / "dispositions").mkdir(parents=True)
    (root / "docs" / "dispositions" / "a..b.md").write_text(
        RECORD.format(extra=extra, rows=rows), encoding="utf-8"
    )
    return holder


class DerivedShape(unittest.TestCase):
    """The contract is read from the module's own root, not from the working directory.

    test_check_citations asserts against check_citations.ROOT for the same reason: a
    suite that resolves the repository as the process's cwd means something different
    depending on where it was started, and the module already resolves it from its own
    location.
    """

    def test_the_five_checks_come_from_the_contract_and_not_from_here(self) -> None:
        shape = record_shape.declared(record_shape.ROOT)

        self.assertIsNone(shape.reason)
        self.assertEqual(
            shape.keys[record_shape.INTEGRITY],
            (
                "Verdict / Gate Index",
                "Calibration / Gate Index",
                "Finding count",
                "Coverage",
                "Non-finding sections",
            ),
        )
        # And every other seat the template declares labels for, which is what lets a
        # seat judging its own record be held to a floor.
        self.assertEqual(len(shape.keys[record_shape.SELF_CHECK]), 2)

    def test_the_result_domain_comes_from_the_contract_too(self) -> None:
        # The template writes the domain with escaped pipes inside a cell, so a naive
        # split on the delimiter reads three broken values instead of three values.
        self.assertEqual(
            record_shape.declared(record_shape.ROOT).results, ("pass", "mismatch", "not claimed")
        )

    def test_a_contract_with_no_marked_template_is_reported_as_that(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "triage-findings").mkdir(parents=True)
            (root / "skills" / "triage-findings" / "SKILL.md").write_text("# x\n", encoding="utf-8")

            shape = record_shape.declared(root)

            self.assertIsNotNone(shape.reason)
            self.assertIn("carries no", shape.reason or "")
            with self.assertRaises(ValueError):
                shape.keys

    def test_the_derivation_reads_the_fence_content_and_not_the_raw_document(self) -> None:
        # The reason it goes through `marked_code_blocks`. Splitting on the marker string
        # leaves the template's own `###` inside a fence, where the parser correctly does
        # not see a heading — which is the same property that keeps an archived record's
        # quoted headings from being read as a document's own, and it is why the first
        # version of this derivation found no table at all.
        text = (record_shape.ROOT / record_shape.CONTRACT).read_text(encoding="utf-8")

        raw = text.split(record_shape.MARKER, 1)[1]
        self.assertIsNone(heading_section(raw, "Record integrity"))

        marked = [b for b in marked_code_blocks(text) if b.marker == record_shape.MARKER]
        content = marked[0].content
        self.assertIsNotNone(heading_section(content, "Record integrity"))


class DeclaredInvariant(unittest.TestCase):
    """One payload, so the single guard covers everything the type carries.

    The first version held the checks and the Result domain as two fields and guarded
    the first alone, so a value with a payload, no second payload and no reason was
    constructible. Reading `.results` there raised the reason, and the reason was None
    because the guard that would have required one had not run.
    """

    def test_a_shape_alone_is_the_read_state(self) -> None:
        held = record_shape.Declared(record_shape.Shape({"S": ("a",)}, ("pass",)), None)

        self.assertEqual(held.keys, {"S": ("a",)})
        self.assertEqual(held.results, ("pass",))

    def test_neither_a_shape_nor_a_reason_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            record_shape.Declared(None, None)

    def test_both_a_shape_and_a_reason_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            record_shape.Declared(record_shape.Shape({}, ()), "why")

    def test_an_unread_contract_never_raises_without_saying_why(self) -> None:
        # The defect the collapse removes: an accessor that finds its own field empty
        # and raises a reason nobody set. Every unread state now carries one, because
        # the guard admits no other.
        unread = record_shape.Declared(None, "the template carries no marker")

        for accessor in ("shape", "keys", "results"):
            with self.subTest(accessor=accessor):
                with self.assertRaises(ValueError) as raised:
                    getattr(unread, accessor)
                self.assertEqual(str(raised.exception), "the template carries no marker")


class RecordIntegrityRows(unittest.TestCase):
    def test_the_real_repository_passes_its_own_check(self) -> None:
        self.assertEqual(record_shape.check(record_shape.ROOT), [])

    def test_a_row_the_contract_does_not_declare_is_refused(self) -> None:
        row = "| Probe disclosure | one scratch probe | makes it checkable | pass |\n"
        with tree(extra=row) as t:
            problems = record_shape.check(Path(t))

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("Probe disclosure", problems[0].message)
            self.assertIn("does not declare", problems[0].message)

    def test_a_row_scoring_pass_is_refused_too_because_the_rule_is_the_subject(self) -> None:
        # Two rounds read a `pass`-scoring extra row as the lighter kind. The key set
        # does not consult the verdict, which is what makes it a proxy for the subject.
        with tree(extra="| Probe disclosure | x | y | pass |\n") as t:
            self.assertEqual(len(record_shape.check(Path(t))), 1)
        settled = "| Range already settled | not stated | nothing asks this | mismatch |\n"
        with tree(extra=settled) as t:
            self.assertEqual(len(record_shape.check(Path(t))), 1)

    def test_a_verdict_outside_the_declared_domain_is_refused(self) -> None:
        with tree(extra="| Coverage | stated | enumerated | probably |\n") as t:
            problems = record_shape.check(Path(t))

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("is not one of", problems[0].message)

    def test_a_row_with_no_trailing_pipe_keeps_every_cell(self) -> None:
        # GFM makes the pipes on either end of a row optional. The reader this replaced
        # dropped the last segment of every row unconditionally, so a legal complete row
        # written without its trailing pipe lost its Result and was reported as missing
        # the column it in fact carried. This test previously asserted that rejection as
        # correct, which is the premise a review refuted.
        legal = "| Coverage | stated | enumerated | pass\n"
        with tree(extra=legal) as holder:
            self.assertEqual(record_shape.check(Path(holder)), [])

    def test_a_short_row_is_padded_by_the_parser_and_read_as_empty(self) -> None:
        # GFM inserts empty cells for a row with fewer than the header declares, and the
        # parser does that before the check sees it. So a short row's Result exists and
        # is empty, which the domain rule reports — the row cannot lose a cell, which is
        # what the reader that dropped its last segment got wrong.
        rows = table_rows("| A | B | C |\n|---|---|---|\n| x | y |\n")
        self.assertEqual(rows[1], ["x", "y", ""])

        with tree(extra="| Coverage | stated |\n") as holder:
            problems = record_shape.check(Path(holder))

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("is not one of", problems[0].message)

    def test_a_header_with_no_result_column_is_reported_as_that(self) -> None:
        # The one way a column reads as absent now: the header never declared it. The
        # delimiter row has to match the header's width or GFM recognises no table.
        record = RECORD.replace(
            "| Check | Input claim | Reconciled evidence | Result |\n|---|---|---|---|",
            "| Check | Input claim | Reconciled evidence |\n|---|---|---|",
        )
        with tree() as holder:
            path = Path(holder) / "docs" / "dispositions" / "a..b.md"
            path.write_text(record.format(extra="", rows=ONE_ROW), encoding="utf-8")

            problems = record_shape.check(Path(holder))

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("declares no Result column", problems[0].message)

    def test_a_section_that_holds_no_readable_table_is_not_a_record_without_one(self) -> None:
        # A malformed table would otherwise pass the way an unopened corpus once did:
        # table() answers None both for "no table here" and "nothing recognisable", and
        # one record legitimately carries no Record integrity section at all.
        record = RECORD.replace("|---|---|---|---|", "not a delimiter row")
        with tree() as holder:
            path = Path(holder) / "docs" / "dispositions" / "a..b.md"
            path.write_text(record.format(extra="", rows=ONE_ROW), encoding="utf-8")

            problems = record_shape.check(Path(holder))

            # The fixture's delimiter row serves every table in it, so every seat
            # reports; what matters is that a section present with no readable table is
            # not silence.
            self.assertTrue(problems)
            self.assertIn("Record integrity carries no table this can read",
                          [problem.message for problem in problems])

    def test_a_non_punctuation_escape_keeps_its_backslash(self) -> None:
        # CommonMark escapes ASCII punctuation and nothing else, so a backslash before
        # `q` is a backslash and a q. A hand-written reader consumed any character after
        # a backslash, silently rewriting legal cell content. This is the negative
        # control the suite lacked: an escape that is not escapable.
        rows = table_rows("| H | I |\n|---|---|\n| ONE\\q | x |\n")

        self.assertEqual(rows[1][0], "ONE\\q")

    def test_two_ids_differing_only_by_an_escape_are_not_one(self) -> None:
        pair = "| ONEq — one | 1 | new | accept | — |\n| ONE\\q — another | 2 | new | accept | — |"
        with tree(rows=pair) as holder:
            self.assertEqual(record_shape.check(Path(holder)), [])

    def test_a_qualified_verdict_passes_because_the_rule_is_a_prefix(self) -> None:
        # The corpus carries `mismatch, stated by the input` and two more like it. A
        # membership test would need an exemption for each; a prefix test needs none,
        # and the qualifier says why rather than declaring a fourth verdict.
        qualified_verdicts = ("mismatch, stated by the input", "mismatch, narrowed", "pass, why")
        for qualified in qualified_verdicts:
            with self.subTest(qualified=qualified), tree(
                extra=f"| Coverage | stated | enumerated | {qualified} |\n"
            ) as t:
                self.assertEqual(record_shape.check(Path(t)), [])

    def test_a_value_merely_sharing_a_prefix_with_a_verdict_is_not_one(self) -> None:
        # The controls this suite lacked. `startswith` accepted every one of these: a
        # well-formed value passing its next comparison, which is the failure AGENTS.md
        # names where it says to read a token whole and never a prefix of it.
        for near in ("passenger", "mismatchable", "not claimedly", "passable", "mismatchXYZ"):
            with self.subTest(near=near), tree(
                extra=f"| Coverage | stated | enumerated | {near} |\n"
            ) as holder:
                problems = record_shape.check(Path(holder))

                self.assertEqual(len(problems), 1, problems)
                self.assertIn("is not one of", problems[0].message)

    def test_a_qualifier_needs_the_delimiter_the_contract_declares(self) -> None:
        # The contract declares a comma and a space. A qualifier run onto the value
        # without it is a different token, not a qualified verdict.
        with tree(extra="| Coverage | stated | enumerated | mismatch,narrowed |\n") as holder:
            self.assertEqual(len(record_shape.check(Path(holder))), 1)

    def test_the_verdict_grammar_is_built_from_what_the_contract_declares(self) -> None:
        # Not a fixed pattern: a fourth value cannot be accepted here without appearing
        # in the template, which is the same reason the keys are derived rather than copied.
        grammar = record_shape.verdict_grammar(("yes", "no"))

        self.assertIsNotNone(grammar.fullmatch("yes"))
        self.assertIsNotNone(grammar.fullmatch("no, with a reason"))
        self.assertIsNone(grammar.fullmatch("pass"))
        self.assertIsNone(grammar.fullmatch("yesterday"))

    def test_a_record_carrying_no_such_table_is_not_a_defect(self) -> None:
        # One record has none, and its round is registered debt. A predicate covers it
        # where a list of files it does not apply to would be the thing AGENTS.md refuses.
        with tree() as t:
            path = Path(t) / "docs" / "dispositions" / "a..b.md"
            path.write_text(
                "# Disposition Record — `a..b`\n\n## Causes\n\nnone\n", encoding="utf-8"
            )

            self.assertEqual(record_shape.check(Path(t)), [])


class EmptyScope(unittest.TestCase):
    def test_a_root_with_no_records_is_a_failure_not_a_clean_answer(self) -> None:
        # check_sources says a missing interpreter is a failure and not a skip;
        # workspace_files says an unlistable workspace must not read as an empty one.
        # This reported OK over a corpus it never opened.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "triage-findings").mkdir(parents=True)
            skill = root / "skills" / "triage-findings" / "SKILL.md"
            skill.write_text(TEMPLATE, encoding="utf-8")
            (root / "docs" / "dispositions").mkdir(parents=True)

            problems = record_shape.check(root)

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("no record to check", problems[0].message)

    def test_a_missing_records_directory_is_a_failure_too(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "skills" / "triage-findings").mkdir(parents=True)
            skill = root / "skills" / "triage-findings" / "SKILL.md"
            skill.write_text(TEMPLATE, encoding="utf-8")

            problems = record_shape.check(root)

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("not a directory", problems[0].message)


class Seats(unittest.TestCase):
    """The subject decides the discipline, and a seat cannot be given the wrong one."""

    def test_a_seat_judging_the_input_closes_its_key_set(self) -> None:
        rules = record_shape.rules_for(record_shape.Subject.THE_INPUT)

        self.assertTrue(any(isinstance(rule, record_shape.ClosedKeys) for rule in rules))
        self.assertFalse(any(isinstance(rule, record_shape.RequiredKeys) for rule in rules))

    def test_a_seat_judging_this_record_gets_a_floor_and_no_ceiling(self) -> None:
        # Measured across the corpus: eight distinct undeclared Self-check labels, all of
        # them a record holding itself to more than the template asks. A closed key set
        # there would refuse commit reachability, guards-row presence and citation
        # existence — checks worth having.
        rules = record_shape.rules_for(record_shape.Subject.THIS_RECORD)

        self.assertTrue(any(isinstance(rule, record_shape.RequiredKeys) for rule in rules))
        self.assertFalse(any(isinstance(rule, record_shape.ClosedKeys) for rule in rules))

    def test_a_record_omitting_a_declared_self_check_is_reported(self) -> None:
        # The check the subject asymmetry buys, and it found a real one on its first run:
        # a record whose second Self-check label read "with enumerated Reach", a word
        # short of the contract's.
        thin = RECORD.replace(
            "| Every accepted cause carries at least one repair with an enumerated Reach"
            " | pass |\n", "",
        )
        with tree() as holder:
            path = Path(holder) / "docs" / "dispositions" / "a..b.md"
            path.write_text(thin.format(extra="", rows=ONE_ROW), encoding="utf-8")

            problems = record_shape.check(Path(holder))

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("answers none of", problems[0].message)

    def test_an_extra_self_check_row_is_not_a_defect(self) -> None:
        rich = RECORD.replace(
            "| Every accepted cause carries at least one repair with an enumerated Reach"
            " | pass |",
            "| Every accepted cause carries at least one repair with an enumerated Reach"
            " | pass |\n| Every commit this record names is reachable from HEAD | pass |",
        )
        with tree() as holder:
            path = Path(holder) / "docs" / "dispositions" / "a..b.md"
            path.write_text(rich.format(extra="", rows=ONE_ROW), encoding="utf-8")

            self.assertEqual(record_shape.check(Path(holder)), [])

    def test_a_seat_added_to_the_tuple_needs_no_edit_to_the_loop(self) -> None:
        # What the declaration buys: the loop does not name a section, so a seat is added
        # by declaring it. Here one is declared for a heading the fixture carries.
        extra_seat = record_shape.Seat("Dispositions", record_shape.Subject.THE_FINDINGS)
        with patch.object(record_shape, "SEATS", (extra_seat,)):
            pair = f"{ONE_ROW}\n| ONE — again | 2 | new | accept | — |"
            with tree(rows=pair) as holder:
                problems = record_shape.check(Path(holder))

                self.assertEqual(len(problems), 1, problems)
                self.assertIn("keys 'ONE' more than once", problems[0].message)


class DispositionKeys(unittest.TestCase):
    def test_one_finding_keyed_twice_is_refused(self) -> None:
        with tree(
            rows=f"{ONE_ROW}\n| ONE — the same thing | 2 | new | accept | — |"
        ) as t:
            problems = record_shape.check(Path(t))

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("more than once", problems[0].message)

    def test_two_findings_sharing_a_prefix_are_not_one(self) -> None:
        # The near-miss control: the id is bounded by the em-dash the row uses, so two
        # ids where one is a prefix of the other stay distinct.
        with tree(
            rows=f"{ONE_ROW}\n| ONE-MORE — another | 2 | new | accept | — |"
        ) as t:
            self.assertEqual(record_shape.check(Path(t)), [])


if __name__ == "__main__":
    unittest.main()


VALID = RECORD.format(extra="", rows="| F1 | 1 | new | accept | — |")
# A record missing one label the contract declares for a seat judging its own work.
INCOMPLETE = VALID.replace(
    "| Every accepted cause carries at least one repair with an enumerated Reach | pass |\n", ""
)


def _repo(root: Path) -> None:
    """A worktree with an identity, so a commit needs nothing from the ambient config."""
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    for key, value in (("user.email", "t@example.com"), ("user.name", "t")):
        subprocess.run(["git", "-C", str(root), "config", key, value], check=True)


def _commit(root: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "commit", "-q", "-m", message], check=True)


def _lay_out(root: Path, template: str) -> Path:
    (root / "skills" / "triage-findings").mkdir(parents=True, exist_ok=True)
    contract = root / "skills" / "triage-findings" / "SKILL.md"
    contract.write_text(template, encoding="utf-8")
    (root / "docs" / "dispositions").mkdir(parents=True, exist_ok=True)
    return contract


class SettledContract(unittest.TestCase):
    """A record is judged against the contract revision it was settled under.

    Holding every archived record to the working tree's contract was the defect: rewording
    one declared label reported the whole corpus rather than the change, and the exits were
    editing history, an exemption list `AGENTS.md` refuses, or an unstated freeze on the
    wording. These drive `record_shape.audit` rather than `contract_revision` alone — a test
    that exercises the helper and never the caller is what let an ownership move pass here
    once while the consumer stayed broken.
    """

    def test_a_committed_record_is_not_convicted_by_a_later_contract_edit(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _repo(root)
            contract = _lay_out(root, TEMPLATE)
            (root / "docs" / "dispositions" / "a..b.md").write_text(VALID, encoding="utf-8")
            _commit(root, "settle a..b")

            # The contract now asks for a label no settled record could have carried.
            contract.write_text(
                TEMPLATE.replace(
                    "Every prior id sits in exactly one exclusive lifecycle home",
                    "Every prior id sits in exactly one lifecycle home",
                ),
                encoding="utf-8",
            )

            self.assertEqual(record_shape.check(root), [])

    def test_the_record_being_written_is_held_to_the_current_contract(self) -> None:
        # The half that keeps the check useful: a record git has never seen is the one this
        # round is producing, so it answers to the wording in the working tree in full.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _repo(root)
            _lay_out(root, TEMPLATE)
            (root / "docs" / "dispositions" / "a..b.md").write_text(VALID, encoding="utf-8")
            _commit(root, "settle a..b")
            (root / "docs" / "dispositions" / "c..d.md").write_text(
                INCOMPLETE, encoding="utf-8"
            )

            problems = record_shape.check(root)

            self.assertTrue(problems, "an uncommitted record must still be judged")
            self.assertTrue(
                all(problem.path.name == "c..d.md" for problem in problems), problems
            )

    def test_a_root_with_no_history_judges_everything_against_its_own_snapshot(self) -> None:
        # A release tarball or a `git archive` export carries its contract and its records
        # as one snapshot, so holding them to that snapshot is the strict answer. What must
        # not happen is answering as though a reading of history had taken place.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _lay_out(root, TEMPLATE)
            (root / "docs" / "dispositions" / "a..b.md").write_text(VALID, encoding="utf-8")

            result = record_shape.audit(root)

            self.assertEqual(result.problems, [])
            self.assertFalse(result.history.available)
            self.assertIn("not a git worktree", result.history.why or "")
            self.assertEqual(len(result.judged), 1)

    def test_a_record_older_than_the_marker_is_unjudged_and_counted(self) -> None:
        # Neither clean nor defective. The count is the point: a record this cannot judge
        # must not be reported as one it found clean.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            _repo(root)
            contract = _lay_out(root, TEMPLATE.replace(record_shape.MARKER, ""))
            (root / "docs" / "dispositions" / "old.md").write_text(VALID, encoding="utf-8")
            _commit(root, "a round settled before the template was marked")
            contract.write_text(TEMPLATE, encoding="utf-8")

            result = record_shape.audit(root)

            self.assertEqual(result.problems, [])
            self.assertEqual(result.judged, [])
            self.assertEqual(len(result.unjudged), 1, result.unjudged)
            self.assertEqual(result.unjudged[0][0], "old.md")
            self.assertEqual(result.read, 1)
