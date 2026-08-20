from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import development_knowns


ENTRY = """schema: 1
knowns:
  - id: example-constraint
    statement: Runtime compatibility requires the older spelling.
    kind: constraint
    treatment: accept
    rationale: The supported runtime rejects the proposed replacement.
    evidence:
      - python3.8 rejects list aliases in an assignment context.
    declined-changes:
      - Replace typing.List with list.
    updated: 2026-08-18
"""


def load_text(text: str):
    with TemporaryDirectory() as tmp:
        path = Path(tmp) / "development-knowns.yaml"
        path.write_text(text, encoding="utf-8")
        return development_knowns.load(path)


class ParserTests(unittest.TestCase):
    def test_minimal_accepted_entry_loads(self) -> None:
        knowns = load_text(ENTRY)

        self.assertEqual(len(knowns), 1)
        self.assertEqual(knowns[0].scalar("id"), "example-constraint")

    def test_unknown_field_fails(self) -> None:
        with self.assertRaisesRegex(development_knowns.KnownError, "unknown field surprise"):
            load_text(ENTRY.replace("    statement:", "    surprise: value\n    statement:"))

    def test_duplicate_ids_fail(self) -> None:
        duplicate = ENTRY + ENTRY.split("knowns:\n", 1)[1]

        with self.assertRaisesRegex(development_knowns.KnownError, "duplicate id"):
            load_text(duplicate)

    def test_wrong_indentation_fails(self) -> None:
        with self.assertRaisesRegex(development_knowns.KnownError, "unsupported YAML shape"):
            load_text(ENTRY.replace("    statement:", "   statement:"))

    def test_schema_must_precede_knowns(self) -> None:
        with self.assertRaisesRegex(development_knowns.KnownError, "knowns must follow schema"):
            load_text(ENTRY.replace("schema: 1\n", ""))

    def test_non_utf8_registry_fails_with_a_known_error(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "development-knowns.yaml"
            path.write_bytes(b"schema: 1\nknowns:\n\xff")

            with self.assertRaises(development_knowns.KnownError):
                development_knowns.load(path)

    def test_yaml_features_outside_the_subset_fail(self) -> None:
        variants = {
            "anchor": "&shared Runtime compatibility requires the older spelling.",
            "alias": "*shared",
            "tag": "!custom value",
            "multiline": "|",
            "flow": "[one, two]",
            "quoted": "'quoted value'",
        }
        for label, value in variants.items():
            with self.subTest(label=label), self.assertRaises(development_knowns.KnownError):
                load_text(
                    ENTRY.replace(
                        "Runtime compatibility requires the older spelling.", value, 1
                    )
                )


class InvariantTests(unittest.TestCase):
    def test_updated_must_be_a_real_calendar_date(self) -> None:
        text = ENTRY.replace("updated: 2026-08-18", "updated: 2026-99-99")

        with self.assertRaisesRegex(development_knowns.KnownError, "calendar date"):
            load_text(text)

    def test_comments_and_blank_lines_are_skipped(self) -> None:
        text = ENTRY.replace("schema: 1\n", "# a note\n\nschema: 1\n")
        self.assertNotEqual(text, ENTRY, "the fixture must actually change")

        self.assertEqual(len(load_text(text)), 1)

    def test_every_document_ordering_rule_is_enforced(self) -> None:
        # Written out rather than edited from ENTRY: these are rules about where a
        # line may appear, so the shape of the document is the fixture.
        body = ENTRY.split("knowns:\n", 1)[1]
        cases = {
            "schema after knowns": (
                f"schema: 1\nknowns:\n{body}schema: 1\n",
                "schema must precede knowns",
            ),
            "knowns before schema": (f"knowns:\n{body}", "knowns must follow schema"),
            "duplicate schema": (f"schema: 1\nschema: 1\nknowns:\n{body}", "duplicate schema"),
            "duplicate knowns": (f"schema: 1\nknowns:\n{body}knowns:\n", "duplicate knowns"),
            "knowns with a value": ("schema: 1\nknowns: one\n", "knowns must be a block list"),
            "entry before knowns": (f"schema: 1\n{body}", "known entry appears before knowns"),
            "field with no entry": (
                "schema: 1\nknowns:\n    kind: constraint\n",
                "known field has no entry",
            ),
            "missing knowns": ("schema: 1\n", "missing knowns"),
        }
        for label, (text, message) in cases.items():
            with self.subTest(label=label):
                with self.assertRaisesRegex(development_knowns.KnownError, message):
                    load_text(text)

    def test_a_list_field_given_a_same_line_value_is_refused(self) -> None:
        text = ENTRY.replace("    evidence:\n", "    evidence: one thing\n")
        self.assertNotEqual(text, ENTRY, "the fixture must actually change")

        with self.assertRaisesRegex(development_knowns.KnownError, "must be a block list"):
            load_text(text)

    def test_every_treatment_refuses_the_work_states_it_cannot_carry(self) -> None:
        cases = {
            "remediate cannot be done": (
                "treatment: remediate\n    repair: do the thing\n    work: done",
                "remediate work cannot be done",
            ),
            "monitor authorizes nothing": (
                "treatment: monitor\n    reconsider-when: the floor moves\n    work: backlog",
                "monitor must not authorize work",
            ),
            "resolved work must be done": (
                "treatment: resolved\n    verification: the gate fails without it\n"
                "    work: backlog",
                "resolved work must be done",
            ),
            "accept authorizes nothing": (
                "treatment: accept\n    work: backlog",
                "accept must not authorize work",
            ),
        }
        for label, (replacement, message) in cases.items():
            with self.subTest(label=label):
                text = ENTRY.replace("treatment: accept", replacement)
                self.assertNotEqual(text, ENTRY, "the fixture must actually change")

                with self.assertRaisesRegex(development_knowns.KnownError, message):
                    load_text(text)

    def test_every_enumeration_and_shape_rejects_a_bad_value(self) -> None:
        # A mutation sweep found each of these guards passing the suite when it was
        # neutered: the treatment-specific invariants were fenced, the vocabularies
        # and shapes they rest on were not.
        cases = {
            "schema value": ("schema: 1", "schema: 2", "schema must be 1"),
            "id shape": (
                "id: example-constraint",
                "id: Example_Constraint",
                "id must use lowercase hyphen-case",
            ),
            "kind vocabulary": ("kind: constraint", "kind: annoyance", "kind must be one of"),
            "treatment vocabulary": (
                "treatment: accept",
                "treatment: ignore",
                "treatment must be one of",
            ),
            "work vocabulary": (
                "treatment: accept",
                "treatment: remediate\n    repair: do the thing\n    work: someday",
                "work must be one of",
            ),
            "date shape": ("updated: 2026-08-18", "updated: 18-08-2026", "updated must use"),
            "missing required field": ("    kind: constraint\n", "", "missing kind"),
            "empty evidence": (
                "    evidence:\n      - python3.8 rejects list aliases in an assignment context.\n",
                "    evidence:\n",
                "evidence must contain at least one item",
            ),
        }
        for label, (old, new, message) in cases.items():
            with self.subTest(label=label):
                text = ENTRY.replace(old, new)
                self.assertNotEqual(text, ENTRY, "the fixture must actually change")

                with self.assertRaisesRegex(development_knowns.KnownError, message):
                    load_text(text)

    def test_a_duplicate_field_and_a_stray_list_item_are_refused(self) -> None:
        cases = {
            "duplicate field": (
                "    kind: constraint\n",
                "    kind: constraint\n    kind: constraint\n",
                "duplicate kind",
            ),
            "list item with no list field": (
                "    rationale: The supported runtime rejects the proposed replacement.\n",
                "    rationale: The supported runtime rejects the proposed replacement.\n"
                "      - stray\n",
                "list item has no list field",
            ),
        }
        for label, (old, new, message) in cases.items():
            with self.subTest(label=label):
                text = ENTRY.replace(old, new)
                self.assertNotEqual(text, ENTRY, "the fixture must actually change")

                with self.assertRaisesRegex(development_knowns.KnownError, message):
                    load_text(text)

    def test_remediate_requires_repair(self) -> None:
        text = ENTRY.replace("treatment: accept", "treatment: remediate")

        with self.assertRaisesRegex(development_knowns.KnownError, "requires repair"):
            load_text(text)

    def test_monitor_requires_reconsider_trigger(self) -> None:
        text = ENTRY.replace("treatment: accept", "treatment: monitor")

        with self.assertRaisesRegex(development_knowns.KnownError, "requires reconsider-when"):
            load_text(text)

    def test_resolved_requires_verification(self) -> None:
        text = ENTRY.replace("treatment: accept", "treatment: resolved")

        with self.assertRaisesRegex(development_knowns.KnownError, "requires verification"):
            load_text(text)

    def test_only_remediation_authorizes_open_work(self) -> None:
        text = ENTRY.replace("    updated:", "    work: backlog\n    updated:")

        with self.assertRaisesRegex(development_knowns.KnownError, "must not authorize work"):
            load_text(text)


class ViewTests(unittest.TestCase):
    def test_views_are_derived_and_stably_ordered(self) -> None:
        accepted = load_text(ENTRY)[0]
        backlog = load_text(
            ENTRY.replace("example-constraint", "z-remediation")
            .replace("treatment: accept", "treatment: remediate")
            .replace(
                "    updated:",
                "    repair: Change the implementation.\n    work: backlog\n    updated:",
            )
        )[0]

        backlog_ids = [
            known.scalar("id")
            for known in development_knowns.select((backlog, accepted), "backlog")
        ]
        accepted_ids = [
            known.scalar("id")
            for known in development_knowns.select((backlog, accepted), "accepted")
        ]
        self.assertEqual(
            backlog_ids,
            ["z-remediation"],
        )
        self.assertEqual(
            accepted_ids,
            ["example-constraint"],
        )

    def test_cli_list_does_not_rewrite_registry(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / development_knowns.REGISTRY
            path.write_text(ENTRY, encoding="utf-8")
            before = path.read_bytes()
            output = StringIO()

            with patch.object(development_knowns, "ROOT", root), redirect_stdout(output):
                code = development_knowns.main(["--list", "accepted"])

            self.assertEqual(code, 0)
            self.assertIn("example-constraint", output.getvalue())
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
