"""Cover the evidence-currency registry: its grammar, its model, and drift itself."""

from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import evidence_currency


CURRENT = """schema: 1
evidence:
  - id: sample
    state: current
    tests: doc.md
    section: Gate 5: Responsibility
    fingerprint: {fingerprint}
    recorded: 2026-08-25
    record: scenarios/sample/README.md
"""

DOCUMENT = """# Title

## Gate 4: Control Flow

before

## Gate 5: Responsibility

measured body

## Gate 6: Logic

after
"""


def write(root: Path, registry: str, document: str = DOCUMENT) -> None:
    (root / "doc.md").write_text(document, encoding="utf-8")
    (root / "evidence.yaml").write_text(registry, encoding="utf-8")
    # Every `record:` an entry names must exist, unless a case is testing that it does not.
    for line in registry.splitlines():
        stripped = line.strip()
        if not stripped.startswith("record:") or "gone" in stripped:
            continue
        record = root / stripped.split(":", 1)[1].strip()
        record.parent.mkdir(parents=True, exist_ok=True)
        record.write_text("# record\n", encoding="utf-8")


def run_check(root: Path) -> tuple[bool, str]:
    output = StringIO()
    entries = evidence_currency.load(root / "evidence.yaml")
    evidence_currency.validate(entries)
    with redirect_stdout(output):
        failed = evidence_currency.check(root, entries)
    return failed, output.getvalue()


class SectionTests(unittest.TestCase):
    def test_a_section_stops_at_the_next_heading_of_its_own_level(self) -> None:
        found = evidence_currency.section_text(DOCUMENT, "Gate 5: Responsibility")

        self.assertIn("measured body", found)
        self.assertNotIn("before", found)
        self.assertNotIn("after", found)

    def test_a_deeper_heading_does_not_end_the_section(self) -> None:
        document = "## Gate 5\n\nbody\n\n### Detail\n\nmore\n\n## Gate 6\n\nafter\n"

        found = evidence_currency.section_text(document, "Gate 5")

        self.assertIn("more", found)
        self.assertNotIn("after", found)

    def test_whole_file_is_its_own_section(self) -> None:
        self.assertEqual(evidence_currency.section_text(DOCUMENT, "whole-file"), DOCUMENT)

    def test_an_absent_heading_is_none_rather_than_the_whole_file(self) -> None:
        # The distinction the check needs: a section that vanished is a failure, and
        # silently hashing the whole document instead would report a clean drift.
        self.assertIsNone(evidence_currency.section_text(DOCUMENT, "Gate 9"))

    def test_the_heading_is_matched_by_text_not_by_its_hashes(self) -> None:
        self.assertIsNone(evidence_currency.section_text(DOCUMENT, "## Gate 5: Responsibility"))


class DriftTests(unittest.TestCase):
    def test_matching_text_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, CURRENT.format(fingerprint="placeholder"))
            actual = evidence_currency.fingerprint(root, "doc.md", "Gate 5: Responsibility")
            write(root, CURRENT.format(fingerprint=actual))

            failed, output = run_check(root)

            self.assertFalse(failed, output)
            self.assertIn("OK   sample", output)

    def test_edited_text_drifts_and_names_the_repair(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, CURRENT.format(fingerprint="placeholder"))
            actual = evidence_currency.fingerprint(root, "doc.md", "Gate 5: Responsibility")
            write(root, CURRENT.format(fingerprint=actual), DOCUMENT.replace("measured", "edited"))

            failed, output = run_check(root)

            self.assertTrue(failed)
            self.assertIn("changed since the evidence recorded", output)
            self.assertIn("re-run it", output)

    def test_a_removed_section_fails_rather_than_passing_quietly(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, CURRENT.format(fingerprint="deadbeefdeadbeef"), "# Title\n\nnothing\n")

            failed, output = run_check(root)

            self.assertTrue(failed)
            self.assertIn("no longer carries", output)

    def test_superseded_is_reported_without_failing(self) -> None:
        # The third answer: evidence known not to describe current text is neither a
        # passing claim nor a build break, and must still say so out loud.
        registry = (
            "schema: 1\nevidence:\n  - id: old\n    state: superseded\n"
            "    tests: doc.md\n    section: whole-file\n    recorded: 2026-08-17\n"
            "    record: scenarios/old/README.md\n"
            "    superseded-reason: the runs predate the current wording\n"
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, registry)

            failed, output = run_check(root)

            self.assertFalse(failed, output)
            self.assertIn("SUPERSEDED old", output)
            self.assertIn("predate the current wording", output)

    def test_an_unregistered_scenario_fails(self) -> None:
        # The maintained-list hole this check was built to avoid: a scenario nobody
        # registered would otherwise be invisible rather than unverified.
        registry = (
            "schema: 1\nevidence:\n  - id: old\n    state: superseded\n"
            "    tests: doc.md\n    section: whole-file\n    recorded: 2026-08-17\n"
            "    record: scripts/tests/scenarios/known/README.md\n"
            "    superseded-reason: the runs predate the current wording\n"
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, registry)
            for name in ("known", "orphan"):
                scenario = root / "scripts" / "tests" / "scenarios" / name
                scenario.mkdir(parents=True, exist_ok=True)
                (scenario / "README.md").write_text("# scenario\n", encoding="utf-8")

            failed, output = run_check(root)

            self.assertTrue(failed)
            self.assertIn("scenarios/orphan", output)
            self.assertIn("no registry entry", output)
            self.assertNotIn("scenarios/known - a checked-in", output)

    def test_a_record_that_is_not_there_fails_the_standalone_check(self) -> None:
        # The unittest suite already asserted this; the documented command did not, so
        # `--check` passed on a claim pointing at a deleted result.
        registry = CURRENT.format(fingerprint="placeholder").replace(
            "record: scenarios/sample/README.md", "record: scenarios/gone/README.md"
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, registry)
            actual = evidence_currency.fingerprint(root, "doc.md", "Gate 5: Responsibility")
            write(root, registry.replace("placeholder", actual))

            failed, output = run_check(root)

            self.assertTrue(failed)
            self.assertIn("its record scenarios/gone/README.md is not there", output)

    def test_a_scenario_whose_record_is_not_a_readme_is_still_seen(self) -> None:
        # Deriving from the README filename would have left this invisible, which is
        # the maintained-list hole one filename further out.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, CURRENT.format(fingerprint="placeholder"))
            actual = evidence_currency.fingerprint(root, "doc.md", "Gate 5: Responsibility")
            write(root, CURRENT.format(fingerprint=actual))
            odd = root / "scripts" / "tests" / "scenarios" / "odd"
            odd.mkdir(parents=True, exist_ok=True)
            (odd / "notes.md").write_text("# notes\n", encoding="utf-8")

            failed, output = run_check(root)

            self.assertTrue(failed)
            self.assertIn("scenarios/odd", output)

    def test_material_inside_a_scenario_is_not_a_second_scenario(self) -> None:
        # Fixtures and per-round scores sit below a record; claiming each as its own
        # scenario would demand a registry entry for every subdirectory.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            scenario = root / "scripts" / "tests" / "scenarios" / "one"
            (scenario / "fixture" / "records").mkdir(parents=True, exist_ok=True)
            (scenario / "README.md").write_text("# one\n", encoding="utf-8")
            (scenario / "fixture" / "records" / "case.md").write_text("# case\n", encoding="utf-8")

            found = evidence_currency.scenario_directories(root)

            self.assertEqual(found, ["scripts/tests/scenarios/one"])

    def test_a_grouping_directory_is_not_itself_a_scenario(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "scripts" / "tests" / "scenarios" / "skill" / "case"
            nested.mkdir(parents=True, exist_ok=True)
            (nested / "README.md").write_text("# case\n", encoding="utf-8")

            found = evidence_currency.scenario_directories(root)

            self.assertEqual(found, ["scripts/tests/scenarios/skill/case"])

    def test_every_checked_in_scenario_is_registered(self) -> None:
        entries = evidence_currency.load(evidence_currency.ROOT / evidence_currency.REGISTRY)
        covered = {str(Path(entry.get("record")).parent) for entry in entries}

        found = evidence_currency.scenario_directories(evidence_currency.ROOT)

        self.assertTrue(found)
        self.assertEqual(sorted(set(found) - covered), [])


class ModelTests(unittest.TestCase):
    def parse(self, registry: str) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, registry)
            evidence_currency.validate(evidence_currency.load(root / "evidence.yaml"))

    def test_every_model_rule_rejects_its_own_shape(self) -> None:
        base = CURRENT.format(fingerprint="abc123")
        cases = {
            "empty registry": ("", "must declare schema: 1"),
            "no schema before entries": (base.replace("schema: 1\n", ""), "must precede"),
            "schema last": ("evidence:\n" + base.replace("evidence:\n", ""), "must precede"),
            "unknown field": (base + "    colour: red\n", "unknown field"),
            "duplicate field": (base + "    state: current\n", "appears twice"),
            "duplicate id": (base + base.split("evidence:\n")[1], "duplicate id"),
            "bad state": (base.replace("state: current", "state: maybe"), "state must be"),
            "current without fingerprint": (
                base.replace("    fingerprint: abc123\n", ""),
                "requires a fingerprint",
            ),
            "superseded without reason": (
                base.replace("state: current", "state: superseded"),
                "requires a reason",
            ),
            "missing required": (base.replace("    recorded: 2026-08-25\n", ""), "missing"),
        }
        for label, (registry, message) in cases.items():
            with self.subTest(label=label):
                with self.assertRaises(evidence_currency.EvidenceError) as caught:
                    self.parse(registry)
                self.assertIn(message, str(caught.exception))

    def test_yaml_features_outside_the_subset_fail(self) -> None:
        registry = CURRENT.format(fingerprint='"quoted"')

        with self.assertRaises(evidence_currency.EvidenceError):
            self.parse(registry)


class RegistryTests(unittest.TestCase):
    def test_the_checked_in_registry_loads_and_satisfies_the_model(self) -> None:
        entries = evidence_currency.load(evidence_currency.ROOT / evidence_currency.REGISTRY)

        evidence_currency.validate(entries)

        self.assertTrue(entries)

    def test_every_registered_record_and_source_exists(self) -> None:
        # A claim pointing at a path that is gone is the same defect one round later.
        for entry in evidence_currency.load(evidence_currency.ROOT / evidence_currency.REGISTRY):
            for field in ("tests", "record"):
                with self.subTest(id=entry.get("id"), field=field):
                    self.assertTrue((evidence_currency.ROOT / entry.get(field)).is_file())


if __name__ == "__main__":
    unittest.main()
