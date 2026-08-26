from __future__ import annotations

import json
import subprocess
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import fixtures
import skill_model
import distribution_manifest
import validate_skills

PUBLISHER = fixtures.PUBLISHER_ID
FOREIGN_PUBLISHER = "c52ebc66-c01e-49af-9ed6-818ee4bc49f1"
REVIEW_RECORD = f"{PUBLISHER}/review-record@1 text/markdown"

NAME = "example-skill"
MANIFEST = fixtures.manifest(NAME)
TRIGGER_BLOCK = f"triggers:\n  - user asks for {NAME}\n"
SKILL_MD = fixtures.skill_md(NAME)


def check(
    skill_dir: Path,
    allow_template_placeholders: bool = False,
    publisher_id: str | None = None,
) -> tuple[bool, str]:
    """Validate a skill, returning whether it *passed* and whatever it printed.

    The checks report whether they failed; this seam inverts once so the assertions
    below read as passed/failed without each restating the convention.
    """
    output = StringIO()

    with redirect_stdout(output):
        failed = validate_skills.validate_skill(
            skill_dir, allow_template_placeholders, publisher_id
        )

    return not failed, output.getvalue()


def check_skill(root: Path, **overrides: str) -> tuple[bool, str]:
    return check(fixtures.write_skill(root, NAME, **overrides))


def write_skill_with_sidecar(parent: Path, publisher: str) -> None:
    """A whole skill, declaring one produced record under the publisher it is given."""
    fixtures.write_skill(
        parent,
        NAME,
        interface_text=(
            f"publisher: {publisher}\n"
            "produces:\n"
            f"  - {publisher}/example-record@1 text/markdown\n"
        ),
    )


class SkillShapeTests(unittest.TestCase):
    """The rules a skill folder must satisfy before any of its content is judged.

    A mutation sweep found each guard below passing the suite when it was neutered:
    the checks that read a manifest's values were fenced, the ones that decide the
    folder is a skill at all were not.
    """

    def test_a_folder_name_that_is_not_hyphen_case_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            skill_dir = fixtures.write_skill(Path(tmp), NAME)
            renamed = skill_dir.parent / "Example_Skill"
            skill_dir.rename(renamed)

            passed, output = check(renamed)

        self.assertFalse(passed)
        self.assertIn("folder name must use lowercase letters, digits, and hyphens", output)

    def test_a_folder_missing_either_required_file_fails(self) -> None:
        cases = {"SKILL.md": "missing SKILL.md", "skill.yaml": "missing skill.yaml"}
        for relative, message in cases.items():
            with self.subTest(relative=relative), TemporaryDirectory() as tmp:
                skill_dir = fixtures.write_skill(Path(tmp), NAME)
                (skill_dir / relative).unlink()

                passed, output = check(skill_dir)

                self.assertFalse(passed)
                self.assertIn(message, output)

    def test_a_skill_document_without_frontmatter_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check_skill(Path(tmp), skill_md_text="# no frontmatter\n")

        self.assertFalse(passed)
        self.assertIn("SKILL.md must start with YAML frontmatter", output)

    def test_a_frontmatter_without_a_description_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            passed, output = check_skill(
                Path(tmp), skill_md_text=SKILL_MD.replace("description:", "summary:", 1)
            )

        self.assertFalse(passed)
        self.assertIn("frontmatter missing description", output)

    def test_a_name_that_disagrees_with_the_folder_or_its_sibling_fails(self) -> None:
        cases = {
            "manifest name": (
                {"manifest_text": MANIFEST.replace(f"name: {NAME}", "name: other-skill", 1)},
                "skill.yaml name 'other-skill' must match folder name",
            ),
            "frontmatter name": (
                {"skill_md_text": SKILL_MD.replace(f"name: {NAME}", "name: other-skill", 1)},
                "SKILL.md frontmatter name 'other-skill' must match folder name",
            ),
        }
        for label, (overrides, message) in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                passed, output = check_skill(Path(tmp), **overrides)

                self.assertFalse(passed)
                self.assertIn(message, output)

    def test_the_two_declared_names_must_agree_with_each_other(self) -> None:
        # Under placeholder mode neither name is held to the folder, so this is the
        # only rule left keeping the manifest and the document naming one skill.
        with TemporaryDirectory() as tmp:
            skill_dir = fixtures.write_skill(
                Path(tmp),
                NAME,
                manifest_text=MANIFEST.replace(f"name: {NAME}", "name: one-skill", 1),
                skill_md_text=SKILL_MD.replace(f"name: {NAME}", "name: other-skill", 1),
            )

            passed, output = check(skill_dir, allow_template_placeholders=True)

        self.assertFalse(passed)
        self.assertIn("skill.yaml name and SKILL.md frontmatter name must match", output)


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

    def test_a_key_with_no_value_is_missing_not_the_next_line(self) -> None:
        # Whitespace allowed to cross the newline made an empty key match the line
        # below it, so an empty entrypoint reported "not found: triggers:". The key
        # must sit above another line for this to reproduce.
        with TemporaryDirectory() as tmp:
            text = (
                f"name: {NAME}\n"
                "family: implementation\n"
                f"description: {fixtures.DESCRIPTION}\n"
                "entrypoint:\n"
                "triggers:\n"
                f"  - user asks for {NAME}\n"
            )
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("skill.yaml missing entrypoint", output)
        self.assertNotIn("triggers", output)

    def test_an_empty_frontmatter_name_is_missing(self) -> None:
        with TemporaryDirectory() as tmp:
            text = (
                "---\n"
                "name:\n"
                f"description: {fixtures.DESCRIPTION}\n"
                "---\n"
                f"\n# {NAME}\n"
                "\n**Input**: the thing this fixture consumes — if none is given, ask for it.\n"
            )
            skill_dir = fixtures.write_skill(Path(tmp), NAME, skill_md_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("frontmatter missing name", output)

    def test_an_entrypoint_naming_a_directory_fails(self) -> None:
        # Existence alone accepted it, so a manifest no host can load passed.
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace("entrypoint: SKILL.md", "entrypoint: references")
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)
            (skill_dir / "references").mkdir()

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("skill.yaml entrypoint must name a file: references", output)

    def test_a_resource_key_naming_a_file_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            text = MANIFEST + "resources:\n  scripts: SKILL.md\n"
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("resources.scripts must name a directory: SKILL.md", output)

    def test_a_resource_key_declared_without_a_path_fails(self) -> None:
        # Declared without a same-line path read as never declared, so the reader
        # returned an empty string and the caller's `if value` skipped it in silence.
        for label, block in {
            "nested block": "resources:\n  scripts:\n    path: helpers\n",
            "empty value": "resources:\n  scripts:\n",
        }.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                text = MANIFEST + block
                skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

                passed, output = check(skill_dir)

                self.assertFalse(passed)
                self.assertIn("resources.scripts must name a path", output)

    def test_a_manifest_path_naming_nothing_is_reported_for_either_field(self) -> None:
        # The absent branch of the shared check, which neither field covered before.
        cases = {
            "entrypoint": (
                MANIFEST.replace("entrypoint: SKILL.md", "entrypoint: gone.md"),
                "skill.yaml entrypoint not found: gone.md",
            ),
            "resource": (
                MANIFEST + "resources:\n  assets: gone\n",
                "resources.assets not found: gone",
            ),
        }
        for label, (text, expected) in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

                passed, output = check(skill_dir)

                self.assertFalse(passed)
                self.assertIn(expected, output)

    def test_a_crafted_manifest_cannot_forge_the_report(self) -> None:
        # An escape sequence in a value rewrote the line it sat in, so a skill folder
        # could bend its own FAIL toward looking like a pass.
        #
        # It no longer reaches a value at all: YAML forbids C0 control characters, so
        # the parser refuses the document and the manifest fails as unreadable. The
        # end-to-end guard on the sink is carried by the right-to-left override below,
        # which is a character YAML admits, and by test_diagnostic_text directly.
        forge = f"{chr(27)}[2Kquiet{chr(13)}OK   all good"
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace("entrypoint: SKILL.md", f"entrypoint: {forge}")
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertNotIn(chr(27), output)
        self.assertNotIn(chr(13), output)
        self.assertIn("special characters are not allowed", output)

    def test_a_crafted_manifest_cannot_reverse_the_report(self) -> None:
        # An escape sequence rewrites a line; a right-to-left override reverses how the
        # rest of it renders. Same class, different Unicode category, so it needs its
        # own end-to-end guard.
        forge = "SKILL.md" + chr(0x202E) + "dm.LLIKS ton"
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace("entrypoint: SKILL.md", f"entrypoint: {forge}")
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertNotIn(chr(0x202E), output)
        self.assertIn("SKILL.md\\u202edm.LLIKS ton", output)

    def test_triggers_must_be_a_non_empty_list_of_strings(self) -> None:
        # The required-field check proved only that the key existed, so every shape
        # below satisfied it while the schema calls triggers a list of strings. Each
        # of these is a document that parses and declares the wrong shape.
        for label, variant in {
            "empty block": "triggers:\n",
            "scalar": "triggers: not-a-list\n",
            "flow list": "triggers: []\n",
            "one empty item": "triggers:\n  - \n",
            # A nested mapping declares no list at the key's own level. The reader
            # used to attribute the nested item to the key, so this shape passed.
            "nested mapping": "triggers:\n  examples:\n    - user asks\n",
        }.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                text = MANIFEST.replace(TRIGGER_BLOCK, variant)
                self.assertNotEqual(text, MANIFEST, "the triggers block must be replaced")
                skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

                passed, output = check(skill_dir)

                self.assertFalse(passed)
                self.assertIn("skill.yaml triggers must be a non-empty list", output)

    def test_frontmatter_that_is_not_yaml_reports_the_parser_not_a_missing_field(self) -> None:
        # The manifest asked whether it parsed; the frontmatter did not, and every reader
        # answers about a document that did not parse as though the key were absent. So
        # an unterminated quote in the description made a `name` plainly present on the
        # line above report itself as missing.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill_dir = fixtures.write_skill(Path(tmp), NAME)
            document = skill_dir / "SKILL.md"
            document.write_text(
                f'---\nname: {NAME}\ndescription: "unterminated\n---\n\n**Input**: a thing\n',
                encoding="utf-8",
            )

            passed, output = check(skill_dir)

            self.assertFalse(passed)
            self.assertIn("SKILL.md frontmatter", output)
            self.assertIn("quoted scalar", output)
            self.assertNotIn("missing name", output)
            self.assertIn(str(root), str(skill_dir))

    def test_a_manifest_that_is_not_yaml_is_refused_whole(self) -> None:
        # Not one field at a time. Every value reader answers UNREAD for a document
        # that will not parse, so guarding each field with `if value` skipped its
        # checks one by one and reported nothing about why — which left an entrypoint
        # carrying an escape sequence validated by nothing at all.
        for label, variant in {
            "a list item where a mapping continues": (
                f"triggers:\n  - user asks for {NAME}\n  examples:\n    - user asks\n"
            ),
            "tab indentation": "triggers:\n\t- user asks\n",
        }.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                text = MANIFEST.replace(TRIGGER_BLOCK, variant)
                self.assertNotEqual(text, MANIFEST, "the triggers block must be replaced")
                skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

                passed, output = check(skill_dir)

                self.assertFalse(passed)
                self.assertIn("skill.yaml ", output)
                self.assertNotIn("missing", output)

    def test_a_continuation_line_is_read_the_way_yaml_reads_it(self) -> None:
        # A line indented past the items continues the plain scalar above it, so this
        # is one trigger and not two. The hand-written reader declined the shape, which
        # refused a manifest every parser in the ecosystem accepts — the one thing this
        # reader's contract says it must not do.
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace(
                TRIGGER_BLOCK, f"triggers:\n  - user asks for {NAME}\n    and then some\n"
            )
            self.assertNotEqual(text, MANIFEST, "the triggers block must be replaced")
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

            passed, output = check(skill_dir)

            self.assertTrue(passed, output)

    def test_a_windows_absolute_entrypoint_is_not_portable(self) -> None:
        # PosixPath does not read "C:/..." as absolute, so the running host's grammar
        # alone let this reach containment and fail as merely "not found".
        with TemporaryDirectory() as tmp:
            text = MANIFEST.replace("entrypoint: SKILL.md", "entrypoint: C:/docs/guide.md")
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("skill.yaml entrypoint must use a relative path", output)

    def test_a_backslash_traversal_is_rejected_even_though_posix_reads_a_filename(self) -> None:
        # The reachable case. A directory literally named "..\shared" is creatable on
        # POSIX, so without both grammars this manifest passed here in full and only
        # escaped the folder once installed on Windows.
        with TemporaryDirectory() as tmp:
            text = MANIFEST + "resources:\n  scripts: ..\\shared\n"
            skill_dir = fixtures.write_skill(Path(tmp), NAME, manifest_text=text)
            (skill_dir / "..\\shared").mkdir()

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn('resources.scripts must not use ".." segments', output)

    def test_a_windows_absolute_link_is_not_treated_as_external(self) -> None:
        with TemporaryDirectory() as tmp:
            text = SKILL_MD + "\n[Guide](C:/docs/guide.md)\n"
            skill_dir = fixtures.write_skill(Path(tmp), NAME, skill_md_text=text)

            passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("has absolute link: C:/docs/guide.md", output)

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

    def test_a_producer_declaring_no_record_of_that_type_fails(self) -> None:
        # The producer has a sidecar and it is valid; it just does not produce the
        # record the Input line names. Neither of the neighbouring branches covered it.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_skill(
                root,
                "static-review",
                interface_text=(
                    f"publisher: {PUBLISHER}\nproduces:\n"
                    f"  - {PUBLISHER}/disposition-record@1 text/markdown\n"
                ),
            )
            text = SKILL_MD.replace(
                "the thing this fixture consumes", "a `static-review` Review Record"
            )
            passed, output = check_skill(
                root,
                skill_md_text=text,
                interface_text=f"publisher: {PUBLISHER}\nconsumes:\n  - {REVIEW_RECORD}\n",
            )

        self.assertFalse(passed)
        self.assertIn("produces no review-record record", output)

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

    def test_every_canonical_field_rule_rejects_a_bad_value(self) -> None:
        # A mutation sweep found each of these guards passing the suite when it was
        # neutered: the rules that keep distribution.json well formed had no fixture.
        cases = {
            "schema": (lambda data: data.__setitem__("schema", 2), "schema must be 1"),
            "name": (
                lambda data: data.__setitem__("name", "Fixture Collection"),
                "name must use lowercase hyphen-case",
            ),
            "version": (
                lambda data: data.__setitem__("version", "1.2"),
                "version must use semantic version format",
            ),
            "publisher case": (
                lambda data: data.__setitem__(
                    "publisher_id", "9D0F3C1A-7B2E-4E61-8D45-2A6F90C3B817"
                ),
                "publisher_id must use canonical lowercase UUID form",
            ),
            "skills directory": (
                lambda data: data.__setitem__("skills_directory", "packs"),
                "skills_directory must be skills",
            ),
            # Belongs in this sweep now that the rule sits beside its siblings rather
            # than inside the function scoped to host projections.
            "description type": (
                lambda data: data.__setitem__("description", 42),
                "description must be a non-empty string",
            ),
            "description empty": (
                lambda data: data.__setitem__("description", ""),
                "description must be a non-empty string",
            ),
        }
        for label, (mutate, message) in cases.items():
            with self.subTest(label=label), TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixtures.write_distribution(root)
                self.edit(root / "distribution.json", mutate)

                passed, output = self.check_distribution(root)

                self.assertFalse(passed)
                self.assertIn(message, output)

    def test_a_host_projection_that_disagrees_on_name_or_version_fails(self) -> None:
        # The projections are what a host installs; agreement with the canonical
        # manifest is the release contract, and neither half was fenced.
        cases = {
            "name": ("name", "renamed", "name must match distribution.json"),
            "version": ("version", "9.9.9", "version must match distribution.json"),
        }
        for label, (field, value, message) in cases.items():
            for relative in distribution_manifest.HOST_VERSION_MANIFESTS:
                with self.subTest(label=label, relative=relative), TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    fixtures.write_distribution(root)
                    self.edit(root / relative, lambda data: data.__setitem__(field, value))

                    passed, output = self.check_distribution(root)

                    self.assertFalse(passed)
                    self.assertIn(relative, output)
                    self.assertIn(message, output)

    def test_a_documented_install_pin_that_disagrees_on_version_fails(self) -> None:
        # A release bumped every manifest and left a pin on the previous tag, and the
        # whole workspace stayed green: the commands a reader copies had no guard.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            relative = distribution_manifest.PINNED_INSTALL_DOCS[0]
            pin = root / relative
            pin.write_text(
                pin.read_text(encoding="utf-8").replace("@v1.2.3", "@v0.9.9"),
                encoding="utf-8",
            )

            passed, output = self.check_distribution(root)

            self.assertFalse(passed)
            self.assertIn(relative, output)
            self.assertIn("install ref v0.9.9 must be v1.2.3", output)

    def test_a_pin_in_an_unregistered_file_is_judged_too(self) -> None:
        # The point of deriving the file list: a pin nobody thought to register is
        # exactly the one a maintained list would have missed.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            nested = root / "docs" / "quickstart.md"
            nested.parent.mkdir(parents=True, exist_ok=True)
            nested.write_text(
                "pipx install git+https://example.invalid/fixture.git@v0.0.1\n",
                encoding="utf-8",
            )

            passed, output = self.check_distribution(root)

            self.assertFalse(passed)
            self.assertIn("docs/quickstart.md", output)
            self.assertIn("install ref v0.0.1 must be v1.2.3", output)

    def test_a_registered_doc_that_stops_carrying_a_pin_fails(self) -> None:
        # The direction derivation cannot see: an unpinned ref is a documented form,
        # so no rule over the text alone separates "deliberately unpinned" from
        # "lost its pin". Replacing the list with the scan traded this guarantee away.
        for relative in distribution_manifest.PINNED_INSTALL_DOCS:
            with self.subTest(relative=relative), TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixtures.write_distribution(root)
                path = root / relative
                path.write_text(
                    path.read_text(encoding="utf-8").replace("@v1.2.3", ""),
                    encoding="utf-8",
                )

                passed, output = self.check_distribution(root)

                self.assertFalse(passed)
                self.assertIn(f"{relative} - a registered install doc carrying no pin", output)

    def test_emptying_the_registry_does_not_buy_a_clean_answer(self) -> None:
        # With a populated registry the per-document rows say it better. This is the
        # case they cannot cover: the registry itself deleted, leaving nothing to miss.
        original = distribution_manifest.PINNED_INSTALL_DOCS
        distribution_manifest.PINNED_INSTALL_DOCS = ()
        try:
            with TemporaryDirectory() as tmp:
                root = Path(tmp)
                # The documents are written from the snapshot, so emptying the registry
                # cannot also empty the tree. Without that the scan finds nothing and the
                # assertion is satisfied by the branch this test exists to distinguish.
                fixtures.write_distribution(root, install_docs=original)

                passed, output = self.check_distribution(root)
                self.assertTrue(all((root / r).is_file() for r in original), "fixture empty")
        finally:
            distribution_manifest.PINNED_INSTALL_DOCS = original

        self.assertFalse(passed)
        self.assertIn("no documented install pin names the release tag", output)

    def test_a_longer_tag_does_not_pass_on_a_version_prefix(self) -> None:
        # Matching a prefix let @v0.4.1.999 and @v0.4.1rc1 capture 0.4.1 and compare
        # equal, so a pin resolving to another tag passed while validation stayed green.
        for suffix in (".999", "rc1", "-rc1", "+build.5", "_other", "/other"):
            with self.subTest(suffix=suffix), TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixtures.write_distribution(root)
                relative = distribution_manifest.PINNED_INSTALL_DOCS[0]
                path = root / relative
                path.write_text(
                    path.read_text(encoding="utf-8").replace("@v1.2.3", f"@v1.2.3{suffix}"),
                    encoding="utf-8",
                )

                passed, output = self.check_distribution(root)

                self.assertFalse(passed)
                self.assertIn(f"install ref v1.2.3{suffix} must be v1.2.3", output)

    def test_nothing_but_a_grammar_that_owns_the_question_ends_a_ref(self) -> None:
        # Form after form said where a ref ends by listing what may follow it. Then the
        # list moved rather than going away: whole() was handed a slice this function
        # had already cut at a set of shell operators, so it proved the slice complete
        # and said nothing about the token. Every character below is legal in a git ref
        # name, and each one shortened a ref into the shipped tag.
        for text, expected in (
            ('"REPO@v1.2.3"', ["v1.2.3"]),
            ('"REPO@v1.2.3#subdirectory=tools/cli"', ["v1.2.3"]),
            ('"fornax@REPO#v1.2.3"', ["v1.2.3"]),
            ("REPO@v1.2.3 \\", ["v1.2.3"]),
            # Near-miss on the accepted prefix: each of these used to answer v1.2.3.
            ("REPO@v1.2.3;old x", ["v1.2.3;old"]),
            ("REPO@v1.2.3(rc) x", ["v1.2.3(rc)"]),
            ("REPO@v1.2.3&next x", ["v1.2.3&next"]),
            ("REPO@v1.2.3>old x", ["v1.2.3>old"]),
            ("REPO@v1.2.3|tee x", ["v1.2.3|tee"]),
            # The same ref quoted and unquoted reads the same, which is the alternate
            # spelling control: nothing about the surroundings changes the token.
            ('"REPO@v1.2.3_rc/1"', ["v1.2.3_rc/1"]),
            ("REPO@v1.2.3_rc/1 x", ["v1.2.3_rc/1"]),
            # Not trimmed to the part that matches: reported, not silently shortened.
            ("see REPO@v1.2.3, then run", ["v1.2.3,"]),
            # No release named, so no claim about which one to install.
            ("REPO@main", []),
        ):
            with self.subTest(text=text):
                refs, unreadable = distribution_manifest.install_refs(
                    text.replace("REPO", "git+https://x.invalid/r.git"),
                    "https://x.invalid/r",
                )

                self.assertEqual(refs, expected)
                self.assertEqual(unreadable, [])

    def test_a_ref_git_forbids_is_reported_rather_than_shortened(self) -> None:
        # `whole()` is what stands between a token and a value here, and the alphabet
        # it checks is git's own: git-check-ref-format forbids these characters in a
        # ref name anywhere, so a token carrying one is not a ref this can read.
        for text in ('"REPO@v1.2.3^"', '"REPO@v1.2.3~1"', '"REPO@v1.2.3:x"'):
            with self.subTest(text=text):
                refs, unreadable = distribution_manifest.install_refs(
                    text.replace("REPO", "git+https://x.invalid/r.git"),
                    "https://x.invalid/r",
                )

                self.assertEqual(refs, [])
                self.assertEqual(len(unreadable), 1, unreadable)
                self.assertIn("is not a release ref", str(unreadable[0]))

    def test_a_quoted_ref_ends_at_its_quote_and_nowhere_else(self) -> None:
        # Whitespace sat in the quoted token's end set beside the closing quote, so
        # `"...@v1.2.3 old"` read as v1.2.3 and compared equal to the shipped tag. The
        # same truncation as the operator lists above, arriving through the delimiter
        # the docstring already claimed to be waiting for.
        for text, unread in (
            ('"REPO@v1.2.3 old"', "v1.2.3 old"),
            ("'REPO@v1.2.3 old'", "v1.2.3 old"),
            ('"REPO@v1.2.3\tnext"', "v1.2.3\tnext"),
            ('"REPO@v1.2.3\nnext"', "v1.2.3\nnext"),
        ):
            with self.subTest(text=text):
                refs, unreadable = distribution_manifest.install_refs(
                    text.replace("REPO", "git+https://x.invalid/r.git"),
                    "https://x.invalid/r",
                )

                self.assertEqual(refs, [])
                self.assertEqual([item.text for item in unreadable], [unread])

    def test_an_opening_quote_nothing_closes_leaves_the_ref_unread(self) -> None:
        # A token that ran to the end of the document is not a token read to its end,
        # whatever it happens to spell.
        for text in ('"REPO@v1.2.3', "'REPO@v1.2.3"):
            with self.subTest(text=text):
                refs, unreadable = distribution_manifest.install_refs(
                    text.replace("REPO", "git+https://x.invalid/r.git"),
                    "https://x.invalid/r",
                )

                self.assertEqual(refs, [])
                self.assertEqual(len(unreadable), 1, unreadable)
                self.assertIn("that nothing closes", str(unreadable[0]))

    def test_an_unpinned_install_ref_is_left_alone(self) -> None:
        # Tracking the default branch is a documented form, not a stale pin. Judging it
        # would force a version onto the one command that deliberately carries none.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            (root / "TRACK.md").write_text(
                "pipx install git+https://example.invalid/fixture.git\n",
                encoding="utf-8",
            )

            passed, output = self.check_distribution(root)

            self.assertTrue(passed, output)

    def test_a_non_worktree_reports_rather_than_raising(self) -> None:
        # The pin scan asks git what the workspace carries, and the lister raises on a
        # root that is not a worktree. The second caller did not turn that into a
        # diagnostic, so a valid distribution.json in an exported tree crashed.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            subprocess.run(["rm", "-rf", str(root / ".git")], check=True)

            passed, output = self.check_distribution(root)

            self.assertFalse(passed)
            self.assertIn("workspace could not be listed", output)

    def test_pins_cannot_be_checked_without_a_repository_url(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            self.edit(root / "distribution.json", lambda data: data.pop("repository"))

            passed, output = self.check_distribution(root)

            self.assertFalse(passed)
            self.assertIn("repository must be a non-empty string to check pins", output)

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


class DirectoryListingTests(unittest.TestCase):
    """A path that cannot be listed is a diagnostic, not a traceback.

    Both listings let the OSError escape, and this is the entry point CI, the
    pre-commit hook, and the deployment CLI's snapshot validation all invoke — so a
    malformed layout surfaced as a stack trace from inside a release run. Every
    sibling reader in this directory already reported it.
    """

    def test_a_skills_path_that_is_not_a_directory_is_reported(self) -> None:
        with TemporaryDirectory() as tmp:
            not_a_directory = Path(tmp) / "skills"
            not_a_directory.write_text("not a directory\n", encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                code = validate_skills.main(
                    ["--skills-path", str(not_a_directory)], root=Path(tmp)
                )

        self.assertEqual(code, 1)
        self.assertIn("Skills directory could not be read", error.getvalue())

    def test_an_unlistable_sibling_directory_is_reported_against_the_skill(self) -> None:
        with TemporaryDirectory() as tmp:
            skill_dir = fixtures.write_skill(Path(tmp) / "skills", NAME)
            with patch.object(
                validate_skills,
                "child_directories",
                return_value=([], OSError("Permission denied")),
            ):
                passed, output = check(skill_dir)

        self.assertFalse(passed)
        self.assertIn("sibling skills could not be listed", output)
        self.assertIn("Permission denied", output)

    def test_a_listing_returns_only_directories_in_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("gamma", "alpha", "beta"):
                (root / name).mkdir()
            (root / "loose-file.txt").write_text("x\n", encoding="utf-8")
            found, error = validate_skills.child_directories(root)

        self.assertIsNone(error)
        self.assertEqual([path.name for path in found], ["alpha", "beta", "gamma"])


class EntryPointTests(unittest.TestCase):
    """`main` validates the root it is given, not the one the process stands in.

    The argv seam alone left everything past the distribution check unreachable: it
    read Path.cwd(), so only the paths returning before it were testable, and one
    that got further validated whatever repository the process happened to stand in.
    """

    def run_main(self, root: Path) -> tuple[int, str]:
        output = StringIO()

        with redirect_stdout(output):
            code = validate_skills.main(["--skills-path", str(root / "skills")], root=root)

        return code, output.getvalue()

    def test_a_well_formed_workspace_passes_through_every_stage(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            # A matching sidecar, so the publisher stage compares one instead of
            # walking an empty glob. The mismatched case below is what observes it.
            write_skill_with_sidecar(root / "skills", PUBLISHER)
            code, output = self.run_main(root)

        self.assertEqual(code, 0, output)
        self.assertIn("Skill validation passed.", output)
        # Names the fixture collection, not this repository's. Asserting only the exit
        # code passed whether or not the root was honoured, because cwd during a suite
        # run is a valid repository too.
        self.assertIn("OK   distribution fixture 1.2.3", output)

    def test_a_mismatched_sidecar_publisher_fails_the_entry_point(self) -> None:
        """Observes the publisher stage through main, not just past it.

        The passing case above carries a matching sidecar so the stage does work, but
        a matching one cannot show whether the stage ran: removing main's call to it
        left the suite green. This case is what fails when the call goes.
        """
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root)
            write_skill_with_sidecar(root / "skills", FOREIGN_PUBLISHER)
            code, output = self.run_main(root)

        self.assertEqual(code, 1)
        self.assertIn("publisher must match distribution.json", output)
        # The run must not also say the skill is fine. One function owns the verdict,
        # so the OK line and the FAIL line cannot both be about this skill.
        self.assertNotIn(f"OK   {NAME}", output)

    def test_a_failure_is_reported_from_the_root_it_was_given(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root, version="not-a-version")
            fixtures.write_skill(root / "skills", NAME)
            code, output = self.run_main(root)

        self.assertEqual(code, 1)
        self.assertIn("version must use semantic version format", output)


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
    """The rule is that a sidecar matches *its own* collection's declared publisher.

    Every case below names a collection identity explicitly, and one of them names a
    collection that is not this one. Passing the production UUID as the argument under
    test could not distinguish this rule from a check hardcoded against that UUID: a
    mutation replacing the parameter with the literal passed the whole suite.
    """

    def check_publishers(self, parent: Path, publisher_id: str) -> tuple[bool, str]:
        """The publisher comparison as the skill's own verdict, which is where it runs."""
        return check(parent / NAME, publisher_id=publisher_id)

    def test_a_sidecar_from_another_publisher_fails_collection_validation(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill_with_sidecar(root, FOREIGN_PUBLISHER)
            passed, output = self.check_publishers(root, PUBLISHER)

        self.assertFalse(passed)
        self.assertIn("publisher must match distribution.json", output)

    def test_a_sidecar_matching_a_collection_that_is_not_this_one_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill_with_sidecar(root, FOREIGN_PUBLISHER)
            passed, output = self.check_publishers(root, FOREIGN_PUBLISHER)

        self.assertTrue(passed, output)

    def test_this_collections_publisher_fails_a_collection_that_is_not_this_one(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill_with_sidecar(root, PUBLISHER)
            passed, output = self.check_publishers(root, FOREIGN_PUBLISHER)

        self.assertFalse(passed)
        self.assertIn("publisher must match distribution.json", output)

    def test_the_declared_collection_identity_reaches_the_sidecar_check(self) -> None:
        """What main() wires: distribution.json's publisher_id, not a constant."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            fixtures.write_distribution(root, publisher_id=FOREIGN_PUBLISHER)
            write_skill_with_sidecar(root / "skills", FOREIGN_PUBLISHER)
            output = StringIO()
            with redirect_stdout(output):
                distribution = validate_skills.validate_distribution(root)
            passed, sidecar_output = self.check_publishers(
                root / "skills", distribution.publisher_id
            )

        self.assertTrue(distribution.passed, output.getvalue())
        self.assertEqual(distribution.publisher_id, FOREIGN_PUBLISHER)
        self.assertTrue(passed, sidecar_output)


if __name__ == "__main__":
    unittest.main()
