from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import fixtures
import skill_interface

PUBLISHER = fixtures.PUBLISHER_ID
RECORD = f"{PUBLISHER}/review-record@1 text/markdown"


def declaration(kind: str, record: str = RECORD, publisher: str = PUBLISHER) -> str:
    return f"publisher: {publisher}\n{kind}:\n  - {record}\n"


class InterfaceParsing(unittest.TestCase):
    def test_invalid_utf8_is_an_interface_error(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / skill_interface.INTERFACE_FILE
            path.write_bytes(b"publisher: \xff\n")

            with self.assertRaisesRegex(skill_interface.InterfaceError, "must use UTF-8"):
                skill_interface.load(path)

    def test_record_identities_are_not_ordered(self) -> None:
        # Nothing sorts, compares or takes a min of an identity. Matching a producer
        # to a consumer intersects two sets, which needs hashing — frozen=True gives
        # that, so an ordering capability would be six methods nobody calls.
        first = skill_interface.RecordIdentity.parse(RECORD)
        second = skill_interface.RecordIdentity.parse(
            f"{PUBLISHER}/other-record@1 text/markdown"
        )

        self.assertEqual(len({first, second}), 2)
        with self.assertRaises(TypeError):
            sorted([first, second])

    def test_a_producer_round_trips_its_record_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / skill_interface.INTERFACE_FILE
            path.write_text(declaration("produces"), encoding="utf-8")

            interface = skill_interface.load(path, "producer")

        self.assertEqual(str(interface.produces[0]), RECORD)

    def test_an_absent_sidecar_is_an_opt_out(self) -> None:
        with TemporaryDirectory() as tmp:
            fixtures.write_skill(Path(tmp), "plain-skill")

            interfaces, errors = skill_interface.discover(Path(tmp))

        self.assertEqual(interfaces, [])
        self.assertEqual(errors, [])

    def test_invalid_or_foreign_output_declarations_fail_closed(self) -> None:
        cases = {
            "missing publisher": "produces:\n  - " + RECORD + "\n",
            "bad uuid": declaration("produces", publisher="not-a-uuid"),
            "zero major": declaration(
                "produces", record=f"{PUBLISHER}/review-record@0 text/markdown"
            ),
            "foreign output": declaration(
                "produces",
                record="c52ebc66-c01e-49af-9ed6-818ee4bc49f1/review-record@1 text/markdown",
            ),
            "unknown yaml": declaration("produces") + "nested:\n  value: no\n",
        }
        for label, text in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                path = Path(tmp) / skill_interface.INTERFACE_FILE
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(skill_interface.InterfaceError):
                    skill_interface.load(path)

    def test_every_parser_rule_rejects_its_own_shape(self) -> None:
        # A mutation sweep found each of these guards passing the suite when it was
        # neutered: the record grammar was fenced, the document grammar was not.
        cases = {
            "list item with no list field": (
                f"publisher: {PUBLISHER}\n  - {RECORD}\n",
                "list item has no list field",
            ),
            "duplicate field": (
                f"publisher: {PUBLISHER}\npublisher: {PUBLISHER}\nproduces:\n  - {RECORD}\n",
                "duplicate publisher",
            ),
            "list field with a value": (
                f"publisher: {PUBLISHER}\nproduces: {RECORD}\n",
                "produces must be a block list",
            ),
            "empty publisher": (
                f"publisher:\nproduces:\n  - {RECORD}\n",
                "publisher must not be empty",
            ),
            "no record at all": (f"publisher: {PUBLISHER}\n", "declare at least one"),
            "duplicate record": (
                f"publisher: {PUBLISHER}\nproduces:\n  - {RECORD}\n  - {RECORD}\n",
                "must not contain duplicates",
            ),
        }
        for label, (text, message) in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                path = Path(tmp) / skill_interface.INTERFACE_FILE
                path.write_text(text, encoding="utf-8")

                with self.assertRaisesRegex(skill_interface.InterfaceError, message):
                    skill_interface.load(path)

    def test_comments_and_blank_lines_are_skipped(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / skill_interface.INTERFACE_FILE
            path.write_text(
                f"# a note\n\npublisher: {PUBLISHER}\nproduces:\n  # another\n  - {RECORD}\n",
                encoding="utf-8",
            )

            interface = skill_interface.load(path, "producer")

        self.assertEqual(str(interface.produces[0]), RECORD)

    def test_noncanonical_record_and_publisher_values_fail(self) -> None:
        cases = (
            declaration("produces", publisher=PUBLISHER.upper()),
            declaration("produces", record=f"{PUBLISHER}/Review-Record@1 text/markdown"),
            declaration("produces", record=f"{PUBLISHER}/review-record@1 TEXT/MARKDOWN"),
        )
        for text in cases:
            with self.subTest(text=text), TemporaryDirectory() as tmp:
                path = Path(tmp) / skill_interface.INTERFACE_FILE
                path.write_text(text, encoding="utf-8")
                with self.assertRaises(skill_interface.InterfaceError):
                    skill_interface.load(path)

    def test_unsupported_scalar_syntax_fails_closed(self) -> None:
        cases = {
            "quoted publisher": declaration("produces", publisher=f"'{PUBLISHER}'"),
            "flow publisher": declaration("produces", publisher=f"[{PUBLISHER}]"),
            "anchored publisher": declaration("produces", publisher=f"&publisher {PUBLISHER}"),
            "quoted record": declaration("produces", record=f"'{RECORD}'"),
            "aliased record": declaration("produces", record="*record"),
            "tagged record": declaration("produces", record=f"!record {RECORD}"),
        }
        for label, text in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                path = Path(tmp) / skill_interface.INTERFACE_FILE
                path.write_text(text, encoding="utf-8")
                with self.assertRaisesRegex(skill_interface.InterfaceError, "unsupported"):
                    skill_interface.load(path)


class Recommendation(unittest.TestCase):
    def interface(self, skill: str) -> skill_interface.SkillInterface:
        record = skill_interface.RecordIdentity.parse(RECORD)
        return skill_interface.SkillInterface(
            skill, PUBLISHER, (), (record,), f"/installed/{skill}"
        )

    def test_one_match_is_recommended(self) -> None:
        record = skill_interface.RecordIdentity.parse(RECORD)
        self.assertEqual(
            [item.skill for item in skill_interface.recommend(record, [self.interface("beta")])],
            ["beta"],
        )

    def test_ties_are_listed_until_a_preference_selects_one(self) -> None:
        record = skill_interface.RecordIdentity.parse(RECORD)
        interfaces = [self.interface("beta"), self.interface("alpha")]
        self.assertEqual(
            [item.skill for item in skill_interface.recommend(record, interfaces)],
            ["alpha", "beta"],
        )
        self.assertEqual(
            [item.skill for item in skill_interface.recommend(record, interfaces, ("beta",))],
            ["beta"],
        )

    def test_duplicate_install_sources_remain_tied(self) -> None:
        record = skill_interface.RecordIdentity.parse(RECORD)
        first = self.interface("beta")
        second = skill_interface.SkillInterface(
            first.skill, first.publisher, first.produces, first.consumes, "/other/beta"
        )

        matches = skill_interface.recommend(record, [first, second], ("beta",))

        self.assertEqual(len(matches), 2)

    def test_a_present_preference_excludes_other_skills_when_its_sources_tie(self) -> None:
        record = skill_interface.RecordIdentity.parse(RECORD)
        first = self.interface("beta")
        second = skill_interface.SkillInterface(
            first.skill, first.publisher, first.produces, first.consumes, "/other/beta"
        )

        matches = skill_interface.recommend(
            record,
            [first, second, self.interface("alpha")],
            ("beta",),
        )

        self.assertEqual([(item.skill, item.source) for item in matches], [
            ("beta", "/installed/beta"),
            ("beta", "/other/beta"),
        ])

    def test_a_lower_ranked_preference_cannot_outrank_a_present_tied_preference(self) -> None:
        record = skill_interface.RecordIdentity.parse(RECORD)
        first = self.interface("beta")
        second = skill_interface.SkillInterface(
            first.skill, first.publisher, first.produces, first.consumes, "/other/beta"
        )

        matches = skill_interface.recommend(
            record,
            [first, second, self.interface("alpha")],
            ("beta", "alpha"),
        )

        self.assertEqual({item.skill for item in matches}, {"beta"})

    def test_cli_reports_no_match_without_invoking_anything(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(root, "plain-skill")
            stdout = StringIO()
            stderr = StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                code = skill_interface.main(
                    ["--skills-path", str(root), "--recommend", RECORD]
                )

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "")

    def test_list_exposes_capabilities_and_deduplicates_a_repeated_root(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(
                root,
                "producer",
                interface_text=declaration("produces"),
            )
            stdout = StringIO()
            with redirect_stdout(stdout):
                code = skill_interface.main(
                    ["--skills-path", str(root), "--skills-path", str(root), "--list"]
                )

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().count("producer ("), 1)
        self.assertIn(f"produces: {RECORD}", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
