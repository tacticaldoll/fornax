from __future__ import annotations

import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import fixtures
import skill_interface

PUBLISHER = "9d0f3c1a-7b2e-4e61-8d45-2a6f90c3b817"
RECORD = f"{PUBLISHER}/review-record@1 text/markdown"


def declaration(kind: str, record: str = RECORD, publisher: str = PUBLISHER) -> str:
    return f"publisher: {publisher}\n{kind}:\n  - {record}\n"


class InterfaceParsing(unittest.TestCase):
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
