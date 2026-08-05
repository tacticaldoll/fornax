from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import fixtures
import skill_model
import validate_skills

NAME = "example-skill"
MANIFEST = fixtures.manifest(NAME)
SKILL_MD = fixtures.skill_md(NAME)


def check(skill_dir: Path, allow_template_placeholders: bool = False) -> tuple[bool, str]:
    """Validate a skill, returning its result and whatever it printed."""
    output = StringIO()

    with redirect_stdout(output):
        passed = validate_skills.validate_skill(skill_dir, allow_template_placeholders)

    return passed, output.getvalue()


def check_skill(root: Path, **overrides: str) -> tuple[bool, str]:
    return check(fixtures.write_skill(root, NAME, **overrides))


class ValidateSkillTests(unittest.TestCase):
    def test_fixture_skill_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check_skill(Path(tmp))

        self.assertTrue(passed, output)
        self.assertIn(f"OK   {NAME}", output)

    def test_top_level_version_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace("family:", "version: 9.9.9\nfamily:", 1)
            passed, output = check_skill(Path(tmp), manifest_text=text)

        self.assertFalse(passed)
        self.assertIn("must not set version", output)
        self.assertIn("distribution.json", output)

    def test_namespaced_nested_version_is_allowed(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check_skill(
                Path(tmp), manifest_text=MANIFEST + "vendor_x:\n  version: 1.2.3\n"
            )

        self.assertTrue(passed, output)

    def test_missing_required_field_fails(self) -> None:
        for field in validate_skills.REQUIRED_MANIFEST_FIELDS:
            with self.subTest(field=field), TemporaryDirectory() as tmp:
                text = "\n".join(
                    line for line in MANIFEST.splitlines() if not line.startswith(f"{field}:")
                )
                passed, output = check_skill(Path(tmp), manifest_text=text + "\n")

                self.assertFalse(passed)
                self.assertIn(f"missing {field}", output)

    def test_unknown_family_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace("family: implementation", "family: invented")
            passed, output = check_skill(Path(tmp), manifest_text=text)

        self.assertFalse(passed)
        self.assertIn(skill_model.listed(skill_model.FAMILIES), output)

    def test_unknown_status_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace("status: draft", "status: retired")
            passed, output = check_skill(Path(tmp), manifest_text=text)

        self.assertFalse(passed)
        self.assertIn(skill_model.listed(skill_model.STATUSES), output)

    def test_missing_input_contract_line_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check_skill(
                Path(tmp), skill_md_text=SKILL_MD.replace("**Input**:", "Input:")
            )

        self.assertFalse(passed)
        self.assertIn("**Input**: contract line", output)

    def test_description_must_match_frontmatter(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD.replace(fixtures.DESCRIPTION, "Use when an agent needs something else.")
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertFalse(passed)
        self.assertIn("description must match", output)

    def test_description_must_open_with_use_when(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check_skill(
                Path(tmp),
                manifest_text=MANIFEST.replace(fixtures.DESCRIPTION, "Does a thing."),
                skill_md_text=SKILL_MD.replace(fixtures.DESCRIPTION, "Does a thing."),
            )

        self.assertFalse(passed)
        self.assertIn("must start with 'Use when '", output)

    def test_handoff_to_an_unknown_skill_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check_skill(
                Path(tmp), skill_md_text=fixtures.skill_md(NAME, handoff="no-such-skill")
            )

        self.assertFalse(passed)
        self.assertIn("handoff target not found: no-such-skill", output)

    def test_handoff_to_a_sibling_skill_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(root, "other-skill")
            passed, output = check_skill(
                root, skill_md_text=fixtures.skill_md(NAME, handoff="other-skill")
            )

        self.assertTrue(passed, output)

    def test_broken_relative_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD + "\nSee [the reference](references/missing.md).\n"
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertFalse(passed)
        self.assertIn("link not found", output)


class SkillModelTests(unittest.TestCase):
    def test_listed_reads_as_a_sentence(self) -> None:
        self.assertEqual(skill_model.listed(["a"]), "a")
        self.assertEqual(skill_model.listed(["a", "b"]), "a, or b")
        self.assertEqual(skill_model.listed(["a", "b", "c"]), "a, b, or c")

    def test_families_carry_a_title_each(self) -> None:
        self.assertTrue(all(title for title in skill_model.FAMILIES.values()))

    def test_handoff_pattern_accepts_every_documented_phrasing(self) -> None:
        for phrasing in ("hand off to", "handoff to", "point to", "route to"):
            with self.subTest(phrasing=phrasing):
                self.assertEqual(
                    skill_model.HANDOFF.findall(f"{phrasing} `map-codebase`"), ["map-codebase"]
                )

    def test_the_shared_fixture_satisfies_every_required_field(self) -> None:
        for field in validate_skills.REQUIRED_MANIFEST_FIELDS:
            with self.subTest(field=field):
                self.assertIn(f"{field}:", MANIFEST)


if __name__ == "__main__":
    unittest.main()
