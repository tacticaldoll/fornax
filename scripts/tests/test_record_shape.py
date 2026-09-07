"""Cover each constraint, and the reading that derives them from the contract."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

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
| something | pass |
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
            shape.checks,
            (
                "Verdict / Gate Index",
                "Calibration / Gate Index",
                "Finding count",
                "Coverage",
                "Non-finding sections",
            ),
        )

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
                shape.checks

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
        held = record_shape.Declared(record_shape.Shape(("a",), ("pass",)), None)

        self.assertEqual(held.checks, ("a",))
        self.assertEqual(held.results, ("pass",))

    def test_neither_a_shape_nor_a_reason_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            record_shape.Declared(None, None)

    def test_both_a_shape_and_a_reason_is_refused(self) -> None:
        with self.assertRaises(ValueError):
            record_shape.Declared(record_shape.Shape((), ()), "why")

    def test_an_unread_contract_never_raises_without_saying_why(self) -> None:
        # The defect the collapse removes: an accessor that finds its own field empty
        # and raises a reason nobody set. Every unread state now carries one, because
        # the guard admits no other.
        unread = record_shape.Declared(None, "the template carries no marker")

        for accessor in ("shape", "checks", "results"):
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
            self.assertIn("begins with none of", problems[0].message)

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
            self.assertIn("begins with none of", problems[0].message)

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

            self.assertEqual(len(problems), 1, problems)
            self.assertIn("carries no table this can read", problems[0].message)

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
