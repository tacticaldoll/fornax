from __future__ import annotations

import json
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

import fixtures
import skill_model
import validate_skills

PUBLISHER = "9d0f3c1a-7b2e-4e61-8d45-2a6f90c3b817"
FOREIGN_PUBLISHER = "c52ebc66-c01e-49af-9ed6-818ee4bc49f1"
REVIEW_RECORD = f"{PUBLISHER}/review-record@1 text/markdown"

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
    def test_invalid_utf8_inputs_fail_without_a_traceback(self) -> None:
        cases = ("skill.yaml", "SKILL.md", "references/guide.md")
        for relative in cases:
            with self.subTest(relative=relative), TemporaryDirectory() as tmp:
                skill_dir = fixtures.write_skill(Path(tmp), NAME)
                path = skill_dir / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"# invalid \xff\n")

                passed, output = check(skill_dir)

                self.assertFalse(passed)
                self.assertIn(relative, output)
                self.assertIn("must use UTF-8", output)

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

    def test_valid_relative_link_with_a_parenthesized_title_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = SKILL_MD + '\nSee [the reference](references/guide.md "short (local) guide").\n'
            skill_dir = fixtures.write_skill(root, NAME, skill_md_text=text)
            reference = skill_dir / "references" / "guide.md"
            reference.parent.mkdir()
            reference.write_text("# Guide\n", encoding="utf-8")

            passed, output = check(skill_dir)

        self.assertTrue(passed, output)

    def test_parent_link_that_remains_in_the_skill_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = fixtures.write_skill(root, NAME)
            guide = skill_dir / "references" / "guide.md"
            guide.parent.mkdir()
            guide.write_text("[self](../SKILL.md)\n", encoding="utf-8")

            passed, output = check(skill_dir)

        self.assertTrue(passed, output)

    def test_link_that_leaves_the_skill_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = SKILL_MD + "\n[Outside](../outside.md)\n"
            skill_dir = fixtures.write_skill(root, NAME, skill_md_text=text)
            (root / "outside.md").write_text("# Outside\n", encoding="utf-8")

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("link leaves skill directory", output)

    def test_link_cannot_escape_the_skill_through_a_symlink(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = SKILL_MD + "\n[Outside](references/outside.md)\n"
            skill_dir = fixtures.write_skill(root, NAME, skill_md_text=text)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            references = skill_dir / "references"
            references.mkdir()
            (references / "outside.md").symlink_to(outside)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("leaves skill directory", output)

    def test_symlink_loop_fails_without_a_traceback(self) -> None:
        with TemporaryDirectory() as tmp:
            skill_dir = fixtures.write_skill(Path(tmp), NAME)
            (skill_dir / "loop.md").symlink_to("loop.md")

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("loop.md could not be resolved", output)

    def test_an_absolute_entrypoint_that_exists_is_rejected(self) -> None:
        # Joining an absolute right operand discards the skill folder, so the old
        # existence check saw a path anywhere on the machine and passed it.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            text = MANIFEST.replace("entrypoint: SKILL.md", f"entrypoint: {outside}")
            skill_dir = fixtures.write_skill(root, NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("entrypoint must use a relative path", output)

    def test_a_parent_relative_entrypoint_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "outside.md").write_text("# Outside\n", encoding="utf-8")
            text = MANIFEST.replace("entrypoint: SKILL.md", "entrypoint: ../outside.md")
            skill_dir = fixtures.write_skill(root, NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn('entrypoint must not use ".." segments', output)

    def test_a_parent_relative_resource_path_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "shared").mkdir()
            text = MANIFEST + "resources:\n  scripts: ../shared\n"
            skill_dir = fixtures.write_skill(root, NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn('resources.scripts must not use ".." segments', output)

    def test_portability_is_judged_without_the_filesystem(self) -> None:
        # A path that does not exist anywhere: only a syntactic rule can produce
        # this message, so this is what separates it from containment.
        cases = {
            "absolute entrypoint": (
                MANIFEST.replace("entrypoint: SKILL.md", "entrypoint: /nowhere/absent.md"),
                "entrypoint must use a relative path",
            ),
            "parent-relative resource": (
                MANIFEST + "resources:\n  references: ../absent\n",
                'resources.references must not use ".." segments',
            ),
        }
        for label, (text, expected) in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

                passed, output = check(skill_dir)

                self.assertFalse(passed)
                self.assertIn(expected, output)

    def test_an_entrypoint_symlinked_outside_the_skill_fails(self) -> None:
        # Syntactically clean and still an escape, so this is containment's oracle
        # for entrypoint rather than the portability rule's.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            outside = root / "outside.md"
            outside.write_text("# Outside\n", encoding="utf-8")
            text = MANIFEST.replace("entrypoint: SKILL.md", "entrypoint: alias.md")
            skill_dir = fixtures.write_skill(root, NAME, manifest_text=text)
            (skill_dir / "alias.md").symlink_to(outside)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("entrypoint leaves the skill folder", output)

    def test_a_resource_directory_symlinked_outside_the_skill_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared = root / "shared"
            shared.mkdir()
            text = MANIFEST + "resources:\n  scripts: scripts\n"
            skill_dir = fixtures.write_skill(root, NAME, manifest_text=text)
            (skill_dir / "scripts").symlink_to(shared, target_is_directory=True)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("resources.scripts leaves the skill folder", output)

    def test_padded_broken_relative_link_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD + "\nSee [the reference]( references/missing.md ).\n"
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertFalse(passed)
        self.assertIn("link not found: references/missing.md", output)

    def test_local_query_and_network_links_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD + "\n[Self](SKILL.md?raw=1#input) [Web](//example.com/guide)\n"
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertTrue(passed, output)

    def test_code_spans_are_ignored_but_escaped_labels_are_checked(self) -> None:
        with TemporaryDirectory() as tmp:
            text = (
                SKILL_MD
                + "\n`[example](inside-code.md)` and "
                + r"[doc \] page](missing.md)"
                + "\n"
            )
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertFalse(passed)
        self.assertIn("link not found: missing.md", output)
        self.assertNotIn("inside-code.md", output)

    def test_code_spans_do_not_hide_links_in_later_paragraphs(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD + "\n` lone\n\nSee [missing](missing.md).\n\n` later\n"
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertFalse(passed)
        self.assertIn("link not found: missing.md", output)

    def test_code_spans_do_not_hide_links_across_heading_boundaries(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD + "\n# ` heading\nSee [missing](missing.md).\n` later\n"
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertFalse(passed)
        self.assertIn("link not found: missing.md", output)

    def test_valid_optional_interface_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = fixtures.write_skill(
                root,
                NAME,
                interface_text=(
                    f"publisher: {PUBLISHER}\n"
                    "produces:\n"
                    f"  - {PUBLISHER}/example-record@1 text/markdown\n"
                ),
            )

            passed, output = check(skill_dir)

        self.assertTrue(passed, output)

    def test_invalid_optional_interface_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = fixtures.write_skill(
                root,
                NAME,
                interface_text="publisher: not-a-uuid\nproduces:\n  - nonsense\n",
            )

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("skill-interface.yaml", output)

    def test_template_placeholder_mode_still_validates_an_interface(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = fixtures.write_skill(
                root,
                NAME,
                interface_text="publisher: invalid\nproduces:\n  - invalid\n",
            )

            passed, output = check(skill_dir, allow_template_placeholders=True)

        self.assertFalse(passed)
        self.assertIn("skill-interface.yaml", output)

    def test_explicit_record_input_requires_a_matching_consumer_sidecar(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(
                root,
                "static-review",
                interface_text=f"publisher: {PUBLISHER}\nproduces:\n  - {REVIEW_RECORD}\n",
            )
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `static-review` Review Record"
            )
            passed, output = check_skill(root, skill_md_text=text)

        self.assertFalse(passed)
        self.assertIn("consumer has no skill-interface.yaml", output)

    def test_explicit_record_input_distinguishes_an_incomplete_consumer_sidecar(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(
                root,
                "static-review",
                interface_text=f"publisher: {PUBLISHER}\nproduces:\n  - {REVIEW_RECORD}\n",
            )
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `static-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=(
                    f"publisher: {PUBLISHER}\nconsumes:\n"
                    f"  - {PUBLISHER}/other-record@1 text/markdown\n"
                ),
            )

        self.assertFalse(passed)
        self.assertIn("does not consume any exact identity", output)

    def test_explicit_record_input_accepts_a_matching_consumer_sidecar(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(
                root,
                "static-review",
                interface_text=f"publisher: {PUBLISHER}\nproduces:\n  - {REVIEW_RECORD}\n",
            )
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `static-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=f"publisher: {PUBLISHER}\nconsumes:\n  - {REVIEW_RECORD}\n",
            )

        self.assertTrue(passed, output)

    def test_explicit_record_input_accepts_one_of_multiple_producer_majors(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(
                root,
                "static-review",
                interface_text=(
                    f"publisher: {PUBLISHER}\nproduces:\n"
                    f"  - {PUBLISHER}/review-record@1 text/markdown\n"
                    f"  - {PUBLISHER}/review-record@2 text/markdown\n"
                ),
            )
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `static-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=(
                    f"publisher: {PUBLISHER}\nconsumes:\n"
                    f"  - {PUBLISHER}/review-record@1 text/markdown\n"
                ),
            )

        self.assertTrue(passed, output)

    def test_explicit_record_input_rejects_multiple_majors_without_overlap(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(
                root,
                "static-review",
                interface_text=(
                    f"publisher: {PUBLISHER}\nproduces:\n"
                    f"  - {PUBLISHER}/review-record@1 text/markdown\n"
                    f"  - {PUBLISHER}/review-record@2 text/markdown\n"
                ),
            )
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `static-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=(
                    f"publisher: {PUBLISHER}\nconsumes:\n"
                    f"  - {PUBLISHER}/review-record@3 text/markdown\n"
                ),
            )

        self.assertFalse(passed)
        self.assertIn("does not consume any exact identity", output)

    def test_explicit_record_input_accepts_a_declared_foreign_producer(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `foreign-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=(
                    f"publisher: {PUBLISHER}\nconsumes:\n"
                    f"  - {FOREIGN_PUBLISHER}/review-record@1 text/markdown\n"
                ),
            )

        self.assertTrue(passed, output)

    def test_local_producer_without_a_sidecar_cannot_use_the_foreign_concession(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(root, "local-review")
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `local-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=(
                    f"publisher: {PUBLISHER}\nconsumes:\n"
                    f"  - {FOREIGN_PUBLISHER}/review-record@1 text/markdown\n"
                ),
            )

        self.assertFalse(passed)
        self.assertIn("local producer `local-review`", output)
        self.assertIn("has no skill-interface.yaml", output)

    def test_absent_local_producer_rejects_a_local_identity(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `missing-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=(
                    f"publisher: {PUBLISHER}\nconsumes:\n"
                    f"  - {PUBLISHER}/review-record@1 text/markdown\n"
                ),
            )

        self.assertFalse(passed)
        self.assertIn("no local skill named `missing-review` exists", output)
        self.assertIn("declares no matching foreign identity", output)
        self.assertIn("correct the producer name or declare the external record identity", output)

    def test_generic_feedback_input_does_not_require_a_sidecar(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD.replace(
                "the thing this fixture consumes",
                "review feedback from another skill or a pasted findings list",
            )
            passed, output = check_skill(Path(tmp), skill_md_text=text)

        self.assertTrue(passed, output)


class ProjectedDescriptionTests(unittest.TestCase):
    def check_distribution(self, root: Path) -> tuple[bool, str]:
        output = StringIO()

        with redirect_stdout(output):
            result = validate_skills.validate_distribution(root)

        return result.passed, output.getvalue()

    def edit(self, path: Path, mutate) -> None:
        data = json.loads(path.read_text(encoding="utf-8"))
        mutate(data)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def test_invalid_utf8_distribution_inputs_fail_without_a_traceback(self) -> None:
        cases = (
            "distribution.json",
            ".codex-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
        )
        for relative in cases:
            with self.subTest(relative=relative), TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixtures.write_distribution(root)
                (root / relative).write_bytes(b'{"invalid": "\xff"}\n')

                passed, output = self.check_distribution(root)

                self.assertFalse(passed)
                self.assertIn(relative, output)
                self.assertIn("must use UTF-8", output)

    def test_non_object_distribution_inputs_fail_without_a_traceback(self) -> None:
        cases = (
            "distribution.json",
            ".codex-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
        )
        for relative in cases:
            with self.subTest(relative=relative), TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixtures.write_distribution(root)
                (root / relative).write_text("[]\n", encoding="utf-8")

                passed, output = self.check_distribution(root)

                self.assertFalse(passed)
                self.assertIn(relative, output)
                self.assertIn("must contain a JSON object", output)

    def test_non_list_marketplace_plugins_fail_without_a_traceback(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            self.edit(
                root / ".claude-plugin" / "marketplace.json",
                lambda data: data.__setitem__("plugins", None),
            )

            passed, output = self.check_distribution(root)

        self.assertFalse(passed)
        self.assertIn(".claude-plugin/marketplace.json - plugins must be a list", output)

    def test_matching_projections_pass(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            output = StringIO()
            with redirect_stdout(output):
                result = validate_skills.validate_distribution(root)

        self.assertTrue(result.passed, output.getvalue())
        self.assertEqual(result.publisher_id, PUBLISHER)

    def test_a_rewritten_description_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            self.edit(
                root / ".cursor-plugin" / "plugin.json",
                lambda d: d.__setitem__("description", "Something else entirely."),
            )
            passed, output = self.check_distribution(root)

        self.assertFalse(passed)
        self.assertIn(".cursor-plugin/plugin.json - description must open with", output)

    def test_an_appended_suffix_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            self.edit(
                root / ".cursor-plugin" / "plugin.json",
                lambda d: d.__setitem__("description", d["description"] + " Extra for this host."),
            )
            passed, output = self.check_distribution(root)

        self.assertTrue(passed, output)

    def test_a_rewritten_nested_plugin_description_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            self.edit(
                root / ".claude-plugin" / "marketplace.json",
                lambda d: d["plugins"][0].__setitem__("description", "A different sentence."),
            )
            passed, output = self.check_distribution(root)

        self.assertFalse(passed)
        self.assertIn("plugins[0].description must open with", output)

    def test_a_canonical_description_that_moved_fails_every_projection(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            self.edit(
                root / "distribution.json",
                lambda d: d.__setitem__("description", "A newly reworded canonical sentence."),
            )
            passed, output = self.check_distribution(root)

        self.assertFalse(passed)
        self.assertEqual(output.count("must open with"), 6)

    def test_a_missing_canonical_description_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            self.edit(root / "distribution.json", lambda d: d.pop("description"))
            passed, output = self.check_distribution(root)

        self.assertFalse(passed)
        self.assertIn("description must be a non-empty string", output)

    def test_an_invalid_publisher_id_fails(self) -> None:
        for invalid in ("bad", 123, []):
            with self.subTest(invalid=invalid), TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixtures.write_distribution(root)
                self.edit(
                    root / "distribution.json",
                    lambda data: data.__setitem__("publisher_id", invalid),
                )

                passed, output = self.check_distribution(root)

            self.assertFalse(passed)
            self.assertIn("publisher_id must be a UUID", output)


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


class InterfacePublisherTests(unittest.TestCase):
    def test_a_sidecar_from_another_publisher_fails_collection_validation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            foreign = "c52ebc66-c01e-49af-9ed6-818ee4bc49f1"
            fixtures.write_skill(
                root,
                NAME,
                interface_text=(
                    f"publisher: {foreign}\n"
                    "produces:\n"
                    f"  - {foreign}/example-record@1 text/markdown\n"
                ),
            )
            output = StringIO()
            with redirect_stdout(output):
                passed = validate_skills.validate_interface_publishers(root, PUBLISHER)

        self.assertFalse(passed)
        self.assertIn("publisher must match distribution.json", output.getvalue())


if __name__ == "__main__":
    unittest.main()
