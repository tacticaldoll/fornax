from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import check_agent_skills
from agent_skill_builder.authoring import create_skill
from agent_skill_builder.profile import load_profile
from agent_skill_builder.validation import validate_skill


class AdapterTests(TestCase):
    def test_repository_profile_rejects_each_declared_constraint(self) -> None:
        profile = load_profile(check_agent_skills.ROOT / "profiles" / "fornax.yaml")
        cases = (
            (
                "missing-manifest",
                "Use when an agent needs to test a missing manifest.",
                "**Input**: A request — ask when ambiguous.\n",
                False,
                "profile-required-file-missing",
            ),
            (
                "wrong-description",
                "Test a description without the Fornax opening.",
                "**Input**: A request — ask when ambiguous.\n",
                True,
                "profile-description-prefix",
            ),
            (
                "missing-input",
                "Use when an agent needs to test a missing input contract.",
                "No input contract here.\n",
                True,
                "profile-markdown-label-missing",
            ),
        )
        for name, description, body, manifest, expected in cases:
            with self.subTest(expected=expected), TemporaryDirectory() as temporary:
                skill = Path(temporary) / name
                skill.mkdir()
                (skill / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: {description}\n---\n\n{body}",
                    encoding="utf-8",
                )
                if manifest:
                    (skill / "skill.yaml").write_text(f"name: {name}\n", encoding="utf-8")
                result = validate_skill(skill, profile)
                self.assertIn(expected, {finding.code for finding in result.findings})

    def test_collection_template_renders_through_declared_slots(self) -> None:
        with TemporaryDirectory() as temporary:
            target = create_skill(
                Path(temporary),
                "rendered-skill",
                "Use when an agent needs to test Fornax template rendering.",
                template=check_agent_skills.ROOT / "templates" / "skill",
            )
            profile = load_profile(check_agent_skills.ROOT / "profiles" / "fornax.yaml")
            result = validate_skill(target, profile)
            manifest = (target / "skill.yaml").read_text(encoding="utf-8")
        self.assertTrue(result.valid)
        self.assertIn("name: rendered-skill", manifest)
        self.assertNotIn("replace-me", manifest)

    def test_fornax_profile_accepts_a_conforming_skill(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "skills" / "example-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: example-skill\n"
                "description: Use when an agent needs to test the adapter.\n---\n\n"
                "**Input**: A request — ask the user when ambiguous.\n",
                encoding="utf-8",
            )
            (skill / "skill.yaml").write_text("name: example-skill\n", encoding="utf-8")
            (root / "profiles").mkdir()
            (root / "profiles" / "fornax.yaml").write_text(
                "schema: agent-skill-builder/profile/v1\nid: fornax\n"
                "description-prefix: 'Use when an agent needs to '\n"
                "required-files: [skill.yaml]\nrequired-markdown-labels: [Input]\n",
                encoding="utf-8",
            )
            (root / "agent-skill-builder.yaml").write_text(
                "schema: agent-skill-builder/workspace/v1\n"
                "skills: skills\nprofile: profiles/fornax.yaml\n",
                encoding="utf-8",
            )
            result = check_agent_skills.main(root)
        self.assertEqual(result, 0)

    def test_fornax_profile_rejects_a_missing_manifest(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            skill = root / "skills" / "example-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: example-skill\n"
                "description: Use when an agent needs to test the adapter.\n---\n\n"
                "**Input**: A request — ask the user when ambiguous.\n",
                encoding="utf-8",
            )
            (root / "profiles").mkdir()
            (root / "profiles" / "fornax.yaml").write_text(
                "schema: agent-skill-builder/profile/v1\nid: fornax\n"
                "required-files: [skill.yaml]\n",
                encoding="utf-8",
            )
            (root / "agent-skill-builder.yaml").write_text(
                "schema: agent-skill-builder/workspace/v1\n"
                "skills: skills\nprofile: profiles/fornax.yaml\n",
                encoding="utf-8",
            )
            result = check_agent_skills.main(root)
        self.assertEqual(result, 1)
