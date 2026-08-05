from __future__ import annotations

import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import skill_model
import validate_skills

DESCRIPTION = (
    "Use when an agent needs to do the one thing this fixture does; does the thing, "
    "rather than doing the other thing."
)

MANIFEST = f"""name: example-skill
family: implementation
status: draft
description: {DESCRIPTION}
triggers:
  - user asks for the example
entrypoint: SKILL.md
"""

SKILL_MD = f"""---
name: example-skill
description: {DESCRIPTION}
---

# Example skill

**Input**: the thing this fixture consumes — if none is given, ask for it.
"""


def build_skill(root: Path, name: str = "example-skill", **overrides: str) -> Path:
    """Write a skill that passes validation, then apply per-file overrides."""
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.yaml").write_text(overrides.get("manifest", MANIFEST), encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(overrides.get("skill_md", SKILL_MD), encoding="utf-8")
    return skill_dir


def check(skill_dir: Path, allow_template_placeholders: bool = False) -> tuple[bool, str]:
    """Validate a skill, returning its result and whatever it printed."""
    output = StringIO()

    with redirect_stdout(output):
        passed = validate_skills.validate_skill(skill_dir, allow_template_placeholders)

    return passed, output.getvalue()


class ValidateSkillTests(unittest.TestCase):
    def test_fixture_skill_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check(build_skill(Path(tmp)))

        self.assertTrue(passed, output)
        self.assertIn("OK   example-skill", output)

    def test_top_level_version_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            manifest = MANIFEST.replace("family:", "version: 9.9.9\nfamily:", 1)
            passed, output = check(build_skill(Path(tmp), manifest=manifest))

        self.assertFalse(passed)
        self.assertIn("must not set version", output)
        self.assertIn("distribution.json", output)

    def test_namespaced_nested_version_is_allowed(self) -> None:
        with TemporaryDirectory() as tmp:
            manifest = MANIFEST + "vendor_x:\n  version: 1.2.3\n"
            passed, output = check(build_skill(Path(tmp), manifest=manifest))

        self.assertTrue(passed, output)

    def test_missing_required_field_fails(self) -> None:
        for field in validate_skills.REQUIRED_MANIFEST_FIELDS:
            with self.subTest(field=field), TemporaryDirectory() as tmp:
                manifest = "\n".join(
                    line for line in MANIFEST.splitlines() if not line.startswith(f"{field}:")
                )
                passed, output = check(build_skill(Path(tmp), manifest=manifest + "\n"))

                self.assertFalse(passed)
                self.assertIn(f"missing {field}", output)

    def test_unknown_family_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            manifest = MANIFEST.replace("family: implementation", "family: invented")
            passed, output = check(build_skill(Path(tmp), manifest=manifest))

        self.assertFalse(passed)
        self.assertIn(skill_model.listed(skill_model.FAMILIES), output)

    def test_unknown_status_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            manifest = MANIFEST.replace("status: draft", "status: retired")
            passed, output = check(build_skill(Path(tmp), manifest=manifest))

        self.assertFalse(passed)
        self.assertIn(skill_model.listed(skill_model.STATUSES), output)

    def test_missing_input_contract_line_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            skill_md = SKILL_MD.replace("**Input**:", "Input:")
            passed, output = check(build_skill(Path(tmp), skill_md=skill_md))

        self.assertFalse(passed)
        self.assertIn("**Input**: contract line", output)

    def test_description_must_match_frontmatter(self) -> None:
        with TemporaryDirectory() as tmp:
            skill_md = SKILL_MD.replace(DESCRIPTION, "Use when an agent needs something else.")
            passed, output = check(build_skill(Path(tmp), skill_md=skill_md))

        self.assertFalse(passed)
        self.assertIn("description must match", output)

    def test_description_must_open_with_use_when(self) -> None:
        with TemporaryDirectory() as tmp:
            manifest = MANIFEST.replace(DESCRIPTION, "Does a thing.")
            skill_md = SKILL_MD.replace(DESCRIPTION, "Does a thing.")
            passed, output = check(build_skill(Path(tmp), manifest=manifest, skill_md=skill_md))

        self.assertFalse(passed)
        self.assertIn("must start with 'Use when '", output)

    def test_handoff_to_an_unknown_skill_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            skill_md = SKILL_MD + "\nIf it is structural, hand off to `no-such-skill`.\n"
            passed, output = check(build_skill(Path(tmp), skill_md=skill_md))

        self.assertFalse(passed)
        self.assertIn("handoff target not found: no-such-skill", output)

    def test_handoff_to_a_sibling_skill_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            build_skill(root, "other-skill")
            skill_md = SKILL_MD + "\nIf it is structural, hand off to `other-skill`.\n"
            passed, output = check(build_skill(root, manifest=MANIFEST, skill_md=skill_md))

        self.assertTrue(passed, output)

    def test_broken_relative_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            skill_md = SKILL_MD + "\nSee [the reference](references/missing.md).\n"
            passed, output = check(build_skill(Path(tmp), skill_md=skill_md))

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


if __name__ == "__main__":
    unittest.main()
