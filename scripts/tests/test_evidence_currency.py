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
    section: "Gate 5: Responsibility"
    fingerprint: {fingerprint}
    recorded: 2026-08-25
    record: scripts/tests/scenarios/sample/README.md
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
    """Everything `main` runs, because a caller wants every fact from one pass.

    The three used to be one function under a docstring naming one of them. They are
    separate now, and this drives all of them so a case does not silently stop covering
    the phase it was written for.
    """
    output = StringIO()
    entries = evidence_currency.load(root / "evidence.yaml")
    evidence_currency.validate(entries)
    with redirect_stdout(output):
        failed = evidence_currency.report(root, entries)
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

    def test_a_hash_inside_a_fenced_block_does_not_end_the_section(self) -> None:
        # The defect the CommonMark parser closes: a shebang in a fenced block ended
        # the section, so the fingerprint covered part of the text it named. Any rule
        # that treats a `#`-prefixed line as a heading fails this.
        document = (
            "## Gate 5: Responsibility\n\nbefore\n\n```sh\n#!/usr/bin/env bash\n```\n\n"
            "after\n\n## Gate 6: Logic\n\nout\n"
        )

        found = evidence_currency.section_text(document, "Gate 5: Responsibility")

        self.assertIn("after", found)
        self.assertNotIn("Gate 6", found)

    def test_a_heading_inside_a_fenced_block_is_not_a_section(self) -> None:
        # An output template's headings belong to the template, not to the document
        # around it — which is where one registered fingerprint had been pinned.
        document = "## Real\n\n```markdown\n### Templated\n\nrow\n```\n"

        self.assertIsNone(evidence_currency.section_text(document, "Templated"))

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
            "    record: scripts/tests/scenarios/old/README.md\n"
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

    def test_every_root_shape_outside_a_scenario_is_refused(self) -> None:
        # The previous guard refused one shape — a parent equal to SCENARIOS — while
        # `.`, `scripts` and `scripts/tests` all passed it and all cover the whole tree,
        # and an absolute or parent-relative path passed too. Stated positively there is
        # no remainder to enumerate.
        outside = (
            "PROJECT.md",
            "scripts/x.md",
            "scripts/tests/x.md",
            "scripts/tests/scenarios/x.md",
            "/abs/path.md",
            "scripts/tests/scenarios/../../PROJECT.md",
        )
        for record in outside:
            with self.subTest(record=record):
                self.assertIsNone(evidence_currency.scenario_root(record))

    def test_a_record_inside_a_scenario_names_its_directory(self) -> None:
        for record, expected in (
            ("scripts/tests/scenarios/a/README.md", "scripts/tests/scenarios/a"),
            ("scripts/tests/scenarios/a/b/README.md", "scripts/tests/scenarios/a/b"),
        ):
            with self.subTest(record=record):
                found = evidence_currency.scenario_root(record)
                self.assertEqual(found.as_posix(), expected)

    def test_a_tests_path_cannot_leave_the_repository_by_spelling(self) -> None:
        # Only `record` was bounded when the root shape was stated positively, so the
        # fingerprint's own subject could name a file this repository does not ship.
        for candidate in ("/etc/hosts", "../../outside.md", "scripts/../PROJECT.md", ""):
            with self.subTest(candidate=candidate):
                self.assertFalse(evidence_currency.spelled_inside(candidate))

    def test_a_tests_path_spelled_inside_is_accepted(self) -> None:
        self.assertTrue(evidence_currency.spelled_inside("skills/static-review/SKILL.md"))

    def test_a_symlink_out_of_the_repository_is_not_fingerprinted(self) -> None:
        # Spelling is not enough where the next act is to read: a relative symlink with
        # no parent segment passed the lexical rule and its target was hashed.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = Path(tmp).parent / f"{root.name}-outside.md"
            outside.write_text("# outside\n", encoding="utf-8")
            try:
                (root / "escape.md").symlink_to(outside)

                self.assertFalse(evidence_currency.resolved_inside("escape.md", root))
                self.assertIsNone(evidence_currency.fingerprint(root, "escape.md", "whole-file"))
            finally:
                outside.unlink()

    def test_a_record_symlinked_out_of_the_tree_fails(self) -> None:
        # Repair 1b named both path fields; only `tests` reached the shared boundary, so
        # a record could be a lexically valid path resolving outside — `is_file()` says
        # yes about the target.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            scenario = root / "scripts" / "tests" / "scenarios" / "a"
            scenario.mkdir(parents=True)
            outside = Path(tmp).parent / f"{root.name}-record.md"
            outside.write_text("# outside\n", encoding="utf-8")
            try:
                (scenario / "README.md").symlink_to(outside)

                self.assertTrue((scenario / "README.md").is_file())
                registry = CURRENT.format(fingerprint="placeholder").replace(
                    "scenarios/sample/README.md", "scenarios/a/README.md"
                )
                write(root, registry)
                actual = evidence_currency.fingerprint(root, "doc.md", "Gate 5: Responsibility")
                write(root, registry.replace("placeholder", actual))
                (scenario / "README.md").unlink()
                (scenario / "README.md").symlink_to(outside)

                failed, output = run_check(root)

                self.assertTrue(failed)
                self.assertIn("is not a file inside", output)
            finally:
                outside.unlink()

    def test_a_symlink_inside_the_repository_is_fingerprinted(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "real.md").write_text("# real\n", encoding="utf-8")
            (root / "link.md").symlink_to(Path("real.md"))

            self.assertTrue(evidence_currency.resolved_inside("link.md", root))
            self.assertIsNotNone(evidence_currency.fingerprint(root, "link.md", "whole-file"))

    def test_a_tree_covering_record_cannot_silence_the_walk(self) -> None:
        # One entry whose record sits beside the registry would make SCENARIOS itself
        # the covering root, so every unaccounted file becomes accounted for. Refused at
        # validate rather than guarded at the walk, which cannot tell that answer from
        # a clean tree. The shape rule that refuses it is `scenario_root`, which the
        # walk uses too, so neither can admit a root the other rejects.
        registry = CURRENT.format(fingerprint="abc123").replace(
            "record: scripts/tests/scenarios/sample/README.md",
            "record: scripts/tests/scenarios/evidence.yaml",
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, registry)

            with self.assertRaises(evidence_currency.EvidenceError) as caught:
                evidence_currency.validate(evidence_currency.load(root / "evidence.yaml"))

            self.assertIn("must sit inside a scenario directory", str(caught.exception))

    def test_a_record_that_is_not_there_fails_the_standalone_check(self) -> None:
        # The unittest suite already asserted this; the documented command did not, so
        # `--check` passed on a claim pointing at a deleted result.
        registry = CURRENT.format(fingerprint="placeholder").replace(
            "scenarios/sample/README.md", "scenarios/gone/README.md"
        )
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, registry)
            actual = evidence_currency.fingerprint(root, "doc.md", "Gate 5: Responsibility")
            write(root, registry.replace("placeholder", actual))

            failed, output = run_check(root)

            self.assertTrue(failed)
            self.assertIn("scripts/tests/scenarios/gone/README.md is not a file inside", output)

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

    def test_material_inside_a_registered_scenario_is_not_reported(self) -> None:
        # Fixtures and per-round scores sit below a declared root; only the registry
        # knows a root from a grouping level, so it declares and this derives the rest.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            scenario = root / "scripts" / "tests" / "scenarios" / "one"
            (scenario / "fixture" / "records").mkdir(parents=True, exist_ok=True)
            (scenario / "README.md").write_text("# one\n", encoding="utf-8")
            (scenario / "fixture" / "records" / "case.md").write_text("# case\n", encoding="utf-8")

            found = evidence_currency.unaccounted_files(
                root, {"scripts/tests/scenarios/one/README.md"}
            )

            self.assertEqual(found, [])

    def test_a_stray_file_is_named_and_its_siblings_stay_accounted_for(self) -> None:
        # The distinguishing case. Any directory-naming rule reports the grouping level
        # and stops enumerating the registered scenario beneath it; naming the file
        # reports the stray and leaves the sibling covered. A rule that returns
        # directories cannot produce this answer at all.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            group = root / "scripts" / "tests" / "scenarios" / "skill"
            (group / "case").mkdir(parents=True, exist_ok=True)
            (group / "case" / "README.md").write_text("# case\n", encoding="utf-8")
            (group / "notes.md").write_text("# stray\n", encoding="utf-8")

            found = evidence_currency.unaccounted_files(
                root, {"scripts/tests/scenarios/skill/case/README.md"}
            )

            self.assertEqual(found, ["scripts/tests/scenarios/skill/notes.md"])

    def test_every_unaccounted_file_is_named_however_deep(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "scripts" / "tests" / "scenarios" / "skill" / "case"
            nested.mkdir(parents=True, exist_ok=True)
            (nested / "README.md").write_text("# case\n", encoding="utf-8")

            found = evidence_currency.unaccounted_files(root, set())

            self.assertEqual(found, ["scripts/tests/scenarios/skill/case/README.md"])

    def test_every_checked_in_scenario_is_registered(self) -> None:
        entries = evidence_currency.load(evidence_currency.ROOT / evidence_currency.REGISTRY)
        registered = {entry.get("record") for entry in entries}

        found = evidence_currency.unaccounted_files(evidence_currency.ROOT, registered)

        self.assertEqual(found, [])

    def test_the_walk_sees_the_real_tree_at_all(self) -> None:
        # The negative control the clean assertion above needs. Asserting an empty result
        # says nothing about whether anything was walked, and its previous anchor —
        # that the registry is non-empty — was about the YAML rather than the walk.
        found = evidence_currency.unaccounted_files(evidence_currency.ROOT, set())

        self.assertTrue(found, "the scenario tree carries files and none were seen")


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
            "record covering the whole tree": (
                base.replace(
                    "record: scripts/tests/scenarios/sample/README.md",
                    "record: scripts/tests/scenarios/evidence.yaml",
                ),
                "must sit inside a scenario directory",
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
        # Double quoting is inside the subset now, and had to be: a heading named
        # "Gate 5: Responsibility & Boundaries" cannot be a plain scalar, so refusing
        # every quote left this registry unable to hold its own values and no YAML
        # parser able to read the file. The rest stay out.
        for label, fingerprint in (
            ("single quoted", "'quoted'"),
            ("flow list", "[one, two]"),
            ("anchor", "&anchor"),
            ("literal block", "|"),
            ("trailing comment", "value  # note"),
            ("colon space", "Gate 5: Responsibility"),
        ):
            with self.subTest(label=label):
                with self.assertRaises(evidence_currency.EvidenceError):
                    self.parse(CURRENT.format(fingerprint=fingerprint))

    def test_a_double_quoted_scalar_holds_what_a_plain_one_cannot(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root, CURRENT.format(fingerprint='"Gate 5: Responsibility"'))

            entries = evidence_currency.load(root / "evidence.yaml")

            self.assertEqual(entries[0].get("fingerprint"), "Gate 5: Responsibility")


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


class SpelledInsideTests(unittest.TestCase):
    def test_both_host_grammars_are_asked(self) -> None:
        # Answered with Path alone, this gave the POSIX reading only, so a Windows
        # drive and a backslash parent segment were spelled inside on this host. The
        # question belongs to host_paths, which asks both.
        for candidate in ("C:/x", "C:x", "..\\x", "../x", "/abs", ""):
            with self.subTest(candidate=candidate):
                self.assertFalse(evidence_currency.spelled_inside(candidate))

    def test_a_relative_path_is_spelled_inside(self) -> None:
        self.assertTrue(evidence_currency.spelled_inside("scripts/tests/scenarios/x/README.md"))

    def test_the_record_field_asks_the_same_grammars_as_the_tests_field(self) -> None:
        # One entry model answered to two path grammars: `tests` was gated through both
        # host readings while `record` kept a local POSIX-only test 35 lines below, so
        # a backslash parent segment came back as an ownership root that escapes the
        # scenario tree on a Windows host.
        self.assertIsNone(evidence_currency.scenario_root("scripts/tests/scenarios/..\\esc/README.md"))
        self.assertIsNone(evidence_currency.scenario_root("C:/x/README.md"))
        self.assertEqual(
            evidence_currency.scenario_root("scripts/tests/scenarios/x/README.md"),
            Path("scripts/tests/scenarios/x"),
        )


if __name__ == "__main__":
    unittest.main()
