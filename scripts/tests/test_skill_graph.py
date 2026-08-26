from __future__ import annotations

import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fixtures
import skill_graph
import skill_model
from generated_block import BlockError

BEFORE = "# Fixture\n\nProse above the block.\n\n"
AFTER = "\nProse below the block.\n"


def build_repo(root: Path, readme_body: str | None = None) -> None:
    """A miniature workspace: skills in different families, a handoff, a README."""
    for name, family, handoff in (
        ("alpha-skill", "implementation", "beta-skill"),
        ("beta-skill", "knowledge", None),
    ):
        fixtures.write_skill(root / "skills", name, family=family, handoff=handoff)

    if readme_body is None:
        markers = skill_graph.MARKERS
        readme_body = f"{BEFORE}{markers.start}\nstale\n{markers.end}{AFTER}"

    (root / "README.md").write_text(readme_body, encoding="utf-8")


def run(root: Path, *argv: str) -> tuple[int, str]:
    output = StringIO()

    with patch.object(skill_graph, "ROOT", root), redirect_stdout(output):
        code = skill_graph.main(list(argv))

    return code, output.getvalue()


class RenderTests(unittest.TestCase):
    def test_only_populated_families_get_a_chart(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            code, block = run(root)

        self.assertEqual(code, 0)
        self.assertIn("### Implementation", block)
        self.assertIn("### Knowledge", block)
        self.assertNotIn("### Decisions & governance", block)
        self.assertIn("alpha-skill --> beta-skill", block)
        self.assertEqual(block.count("```mermaid"), 2)


class ReaderAgreementTests(unittest.TestCase):
    """One key, read the same way here and by the validator, and never guessed at.

    Each bad declaration below used to produce a chart rather than a diagnostic. The
    mismatched pair was trimmed to a valid family here while the validator refused
    the same manifest; the empty key read the description line beneath it. Both then
    left the skill out of every chart at exit 0.
    """

    def family_of(self, declaration: str) -> str:
        with TemporaryDirectory() as tmp:
            skills = Path(tmp) / "skills"
            fixtures.write_skill(
                skills,
                "quoted-skill",
                manifest_text=fixtures.manifest("quoted-skill").replace(
                    "family: implementation", declaration
                ),
            )
            _, family, _ = skill_graph.load(skills)

        return family["quoted-skill"]

    def test_a_mismatched_quote_pair_is_not_trimmed_into_a_valid_family(self) -> None:
        with self.assertRaisesRegex(BlockError, "quoted-skill"):
            self.family_of("family: \"meta'")

    def test_an_empty_family_is_reported_rather_than_read_from_the_next_line(self) -> None:
        with self.assertRaisesRegex(BlockError, "quoted-skill"):
            self.family_of("family:")

    def test_an_unplaceable_family_names_the_allowed_values(self) -> None:
        with self.assertRaisesRegex(BlockError, "family must be"):
            self.family_of("family: invented")

    def test_a_quoted_family_still_reads(self) -> None:
        self.assertEqual(self.family_of("family: 'meta'"), "meta")

    def test_every_declared_family_is_placeable(self) -> None:
        for declared in skill_model.FAMILIES:
            with self.subTest(family=declared):
                self.assertEqual(self.family_of(f"family: {declared}"), declared)


class WriteTests(unittest.TestCase):
    def test_write_replaces_only_the_marked_block(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            code, output = run(root, "--write")
            readme = (root / "README.md").read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertIn("rewrote the skill maps", output)
        self.assertTrue(readme.startswith(BEFORE))
        self.assertTrue(readme.endswith(AFTER))
        self.assertNotIn("stale", readme)
        self.assertIn("alpha-skill --> beta-skill", readme)

    def test_write_is_idempotent(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            run(root, "--write")
            first = (root / "README.md").read_text(encoding="utf-8")
            run(root, "--write")
            second = (root / "README.md").read_text(encoding="utf-8")

        self.assertEqual(first, second)


class CheckTests(unittest.TestCase):
    def test_check_passes_after_write(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            run(root, "--write")
            code, output = run(root, "--check")

        self.assertEqual(code, 0)
        self.assertIn("OK   README.md skill maps", output)

    def test_check_fails_on_a_stale_block(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            code, output = run(root, "--check")

        self.assertEqual(code, 1)
        self.assertIn("skill maps block is out of date", output)
        self.assertIn("--write", output)

    def test_check_fails_when_an_edge_is_removed_by_hand(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            run(root, "--write")
            readme = root / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8").replace("    alpha-skill --> beta-skill\n", ""),
                encoding="utf-8",
            )
            code, output = run(root, "--check")

        self.assertEqual(code, 1)
        self.assertIn("out of date", output)

    def test_missing_markers_are_reported_not_appended(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root, readme_body="# Fixture\n\nNo markers here.\n")
            code, output = run(root, "--check")

        self.assertEqual(code, 1)
        self.assertIn("SKILL-MAPS markers not found", output)


class IoFailureTests(unittest.TestCase):
    def test_missing_readme_reports_a_diagnostic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            (root / "README.md").unlink()
            code, output = run(root, "--check")

        self.assertEqual(code, 1)
        self.assertTrue(output.startswith("FAIL README.md - "), output)

    def test_missing_skills_directory_reports_a_diagnostic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)

            for path in sorted((root / "skills").rglob("*"), reverse=True):
                path.unlink() if path.is_file() else path.rmdir()

            (root / "skills").rmdir()
            code, output = run(root, "--check")

        self.assertEqual(code, 1)
        self.assertTrue(output.startswith("FAIL skills - "), output)

    @unittest.skipIf(os.geteuid() == 0, "root bypasses file permissions")
    def test_unreadable_manifest_reports_the_offending_skill(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            manifest_path = root / "skills" / "alpha-skill" / "skill.yaml"
            manifest_path.chmod(0o000)

            try:
                code, output = run(root, "--check")
            finally:
                manifest_path.chmod(0o644)

        self.assertEqual(code, 1)
        self.assertTrue(output.startswith("FAIL skills/alpha-skill/skill.yaml - "), output)

    @unittest.skipIf(os.geteuid() == 0, "root bypasses file permissions")
    def test_unwritable_readme_reports_a_diagnostic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_repo(root)
            readme = root / "README.md"
            readme.chmod(0o444)

            try:
                code, output = run(root, "--write")
            finally:
                readme.chmod(0o644)

        self.assertEqual(code, 1)
        self.assertTrue(output.startswith("FAIL README.md - "), output)


if __name__ == "__main__":
    unittest.main()
