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
