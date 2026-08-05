from __future__ import annotations

import os
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import skill_graph

DESCRIPTION = "Use when an agent needs the fixture; does the thing, rather than the other thing."

BEFORE = "# Fixture\n\nProse above the block.\n\n"
AFTER = "\nProse below the block.\n"


def manifest(name: str, family: str) -> str:
    return (
        f"name: {name}\n"
        f"family: {family}\n"
        "status: draft\n"
        f"description: {DESCRIPTION}\n"
        "triggers:\n  - user asks\n"
        "entrypoint: SKILL.md\n"
    )


def skill_md(name: str, handoff: str | None) -> str:
    body = f"---\nname: {name}\ndescription: {DESCRIPTION}\n---\n\n**Input**: a thing — ask.\n"

    if handoff:
        body += f"\nIf it is structural, hand off to `{handoff}`.\n"

    return body


def build_repo(root: Path, readme_body: str | None = None) -> None:
    """A miniature workspace: two skills in different families, one handoff, a README."""
    for name, family, handoff in (
        ("alpha-skill", "implementation", "beta-skill"),
        ("beta-skill", "knowledge", None),
    ):
        skill_dir = root / "skills" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "skill.yaml").write_text(manifest(name, family), encoding="utf-8")
        (skill_dir / "SKILL.md").write_text(skill_md(name, handoff), encoding="utf-8")

    if readme_body is None:
        readme_body = f"{BEFORE}{skill_graph.START}\nstale\n{skill_graph.END}{AFTER}"

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
        self.assertIn("skill maps are out of date", output)
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
